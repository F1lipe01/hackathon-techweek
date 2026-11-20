// The pitch site: tabs by hash, the demo's controls (prototype/server.py: /api/demo/*), and the content of the other
// tabs. Jury-facing text in European Portuguese. Never a browser dialog: everything is drawn in the page.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = (x, d = 1) => Number(x).toFixed(d).replace('.', ',');
async function api(path, body) {
  const r = await fetch(path, body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

// ------------------------------------------------------------------ tabs
const TABS = ['demo', 'videos', 'como', 'docs'];
function show() {
  const t = TABS.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'demo';
  TABS.forEach((x) => { $(`#t-${x}`).hidden = x !== t; });
  document.body.dataset.tab = t;
  document.querySelectorAll('.tabs a').forEach((a) => (a.dataset.tab === t ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
  if (t !== 'videos') document.querySelectorAll('#videos video').forEach((v) => v.pause());
  window.scrollTo(0, 0);
}
addEventListener('hashchange', show);
show();

// ------------------------------------------------------------------ demo controls
const app = $('#app');
let status = null, busy = false, llmFails = 0;
function render() {
  const s = status, sw = $('.switch'), lbl = $('#models-lbl');
  const set = (cls, html) => { sw.className = `switch ${cls}`; lbl.innerHTML = html; };
  if (!s) { set('red', '<i class="dot"></i>Servidor sem resposta'); return; }
  const r = s.replay;
  const m = s.models;
  if (!busy) $('#models').checked = m.on;
  if (m.on && m.loaded) set('ok', `<i class="dot"></i>Modelos ativos${m.edge_state === 'active' ? ' · a analisar' : ''}`);
  else if (m.on && m.waiting) set('warn busy', '<i class="dot"></i>À espera da máquina');
  else if (m.on && m.loading) set('warn busy', '<i class="dot"></i>A carregar (≈ 20 s)');
  else if (m.on) set('red', '<i class="dot"></i>Indisponíveis · <a href="#videos">gravação</a>');
  else set('', m.loaded ? 'Ativar modelos' : 'Ativar modelos');
  llmFails = s.llm ? 0 : llmFails + 1;            // a slow answer once is not "down"
  const llm = $('#c-llm');
  llm.hidden = llmFails < 3;
  llm.innerHTML = '<i class="dot"></i><span>Sem modelo de texto</span>';
}
async function poll() {
  try { status = await api('/api/demo/status'); } catch { status = null; }
  render();
}
poll(); setInterval(() => { if (!document.hidden) poll(); }, 1000);

$('#models').addEventListener('change', async (e) => {
  busy = true;
  try { status = await api('/api/demo/models', { on: e.target.checked }); } catch { /* shown by the next poll */ }
  busy = false; render();
});
$('#reset').addEventListener('click', async (e) => {
  const b = e.currentTarget; b.disabled = true;
  try { await api('/api/demo/reset', {}); } catch { /* the chip says it */ }
  try { ['tt-favs', 'tt-read'].forEach((k) => app.contentWindow.localStorage.removeItem(k)); } catch { /* storage blocked */ }
  app.src = '/?embed=1&r=' + Date.now();
  const lbl = b.querySelector('span'); lbl.textContent = 'Apagado ✓';
  setTimeout(() => { lbl.textContent = 'Apagar pessoas e objetos'; }, 2000);
  b.disabled = false; poll();
});

// ------------------------------------------------------------------ documents
const DOCS = [
  ['Sumário executivo', 'sumario-executivo.pdf', 2, 'O relatório entregue.'],
  ['Arquitetura', 'arquitetura.pdf', 24, 'O que corre em casa e o que corre na Altice.'],
  ['Especificação de integração', 'integracao.pdf', 7, 'O que se liga à plataforma Cognitive Home.'],
  ['Viabilidade do negócio', 'viabilidade.pdf', 9, '3,99 € por mês; cerca de 1,74 € de margem por casa (estimativa).'],
  ['Custos para o operador', 'custos-operador.pdf', 7, 'Cerca de 0,49 € por casa e por mês (estimativa).'],
  ['Casos de uso', 'casos-de-uso.pdf', 27, 'O catálogo completo.'],
  ['Produto', 'produto.pdf', 30, 'A especificação para um lançamento na MEO.'],
  ['Perguntas de engenharia', 'perguntas-engenharia.pdf', 11, 'Respostas curtas às perguntas difíceis.'],
];
$('#docs').innerHTML = DOCS.map(([t, f, n, d]) => `<article class="card"><div class="meta">PDF · ${n} ${n === 1 ? 'página' : 'páginas'}</div><h3>${esc(t)}</h3><p>${esc(d)}</p>
  <div class="acts"><a href="/media/${f}" target="_blank" rel="noopener">Abrir</a></div></article>`).join('')
;

const VIEWS = [
  ['c4-1-contexto', 'Contexto (C4, nível 1)', 'Quem usa o ThingTracker e com que sistemas fala.'],
  ['c4-2-contentores', 'Contentores (C4, nível 2)', 'As peças que correm: em casa, na Altice e no telemóvel.'],
  ['c4-3-componentes', 'Componentes (C4, nível 3)', 'O que há dentro do serviço ThingTracker.'],
  ['implantacao', 'Implantação', 'Em que máquina corre cada parte.'],
  ['presenca-estados', 'Estados de presença', 'Ocupada, a sair, vazia, incerta: como a casa sabe quem lá está.'],
  ['seq-livro-esquecido', 'Sequência: o livro esquecido', 'Da porta ao aviso, passo a passo.'],
  ['seq-pessoa-desconhecida', 'Sequência: a pessoa desconhecida', 'Do rosto ao alarme simulado.'],
  ['seq-casa-vazia', 'Sequência: ninguém em casa', 'Da última saída ao “desligar?”.'],
  ['sequencia-regra', 'Sequência: uma frase vira regra', 'Do texto escrito à regra validada.'],
  ['dfd-fronteiras', 'Fluxo de dados e fronteiras de confiança', 'O que sai de casa e o que nunca sai.'],
  ['er-casa', 'Dados no equipamento de casa', 'O que o equipamento de casa guarda.'],
  ['er-plataforma', 'Dados na plataforma', 'O que a plataforma guarda por cliente.'],
  ['fluxo-app', 'Fluxos da aplicação', 'Os ecrãs novos e por onde se chega a eles.'],
];
$('#views').innerHTML = VIEWS.map(([f, t]) => `<figure data-src="/media/views/${f}.png"><img src="/media/views/${f}.png" alt="${esc(t)}" loading="lazy"><figcaption><b>${esc(t)}</b></figcaption></figure>`).join('');

// ------------------------------------------------------------------ videos
const VIDEOS = [
  ['hero', '', [
    ['film-completo.mp4', 'O filme', 'As três histórias num só filme.'],
  ]],
  ['Os três exemplos', '', [
    ['film-livro.mp4', 'O livro', 'Sair de casa sem o livro: a porta, o telemóvel e a câmara decidem, e a aplicação avisa.'],
    ['film-pessoa.mp4', 'A pessoa desconhecida', 'A família é reconhecida; um rosto que não é da família, com a casa vazia, faz soar o alarme.'],
    ['film-pessoas.mp4', 'Ninguém em casa', 'Todos saem e ficam aparelhos ligados: a aplicação pergunta se os desliga.'],
  ]],
];
$('#videos').innerHTML = VIDEOS.map(([g, d, xs]) => `<div class="vgroup${g === 'hero' ? ' hero' : ''}">${g && g !== 'hero' ? `<h2 class="sec">${esc(g)}</h2>` : ''}${d ? `<p>${esc(d)}</p>` : ''}<div class="vgrid">${xs.map(([f, t, p]) =>
  `<article class="vcard" data-f="${f}"><video src="/media/${f}" controls preload="metadata" playsinline></video><div class="t"><h3>${esc(t)}</h3>${p ? `<p>${esc(p)}</p>` : ''}</div></article>`).join('')}</div></div>`).join('');
document.querySelectorAll('#videos .vcard video').forEach((v) => v.addEventListener('error', () => { const g = v.closest('.vgroup'); v.closest('.vcard').remove(); if (g && !g.querySelector('.vcard')) g.remove(); }));
document.querySelectorAll('#videos video').forEach((v) => v.addEventListener('play', () => document.querySelectorAll('#videos video').forEach((o) => o !== v && o.pause())));

// ------------------------------------------------------------------ zoom on figures (drawn in the page)
const zoom = $('#zoom');
document.addEventListener('click', (e) => {
  const f = e.target.closest('[data-src], img[data-zoom]');
  if (f) { zoom.querySelector('img').src = f.dataset.src || f.src; zoom.hidden = false; return; }
  if (e.target.closest('#zoom')) zoom.hidden = true;
});
addEventListener('keydown', (e) => { if (e.key === 'Escape') zoom.hidden = true; });
