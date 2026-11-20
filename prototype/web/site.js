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
const TABS = ['demo', 'casos', 'como', 'docs', 'videos'];
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
  b.disabled = false; poll();
});

// ------------------------------------------------------------------ use cases (docs/pt/18-casos-de-uso.md)
const SHOWN = [
  ['livro.png', 'Sair sem o livro', 'A porta fecha, o livro ficou: aviso.', 'hoje', 'Ao vivo'],
  ['pessoa.png', 'Pessoa desconhecida', 'Família reconhecida; estranho: alarme.', 'rec', 'Em vídeo'],
  ['casa-vazia.png', 'Ninguém em casa', 'Ficou algo ligado? Desliga com um “Sim”.', 'hoje', 'Ao vivo'],
  ['crianca.jpg', 'Criança em perigo', 'Detergente na mão: alerta imediato.', 'ext', 'Proposta'],
];
$('#shown').innerHTML = SHOWN.map(([img, t, d, b, how]) => `<figure class="shot"><div class="ph"><img src="/media/img/${img}" alt="${esc(t)}" data-zoom loading="lazy"><span class="badge ${b}">${how}</span></div><figcaption><b>${esc(t)}</b><span>${esc(d)}</span></figcaption></figure>`).join('');

const CAT = [
  ['Segurança', [
    ['S1', 'Faca na bancada com um gato, um cão ou uma criança por perto', 'Cozinha', 'Kit', 'ext'],
    ['S2', 'Criança com uma faca, ou junto ao fogão ou ao forno', 'Cozinha', 'Kit; outro IoT opcional', 'ext'],
    ['S3', 'Fogão ou forno ligado sem ninguém na cozinha', 'Cozinha', 'Kit (tomada, fumo) ou outro IoT', 'ext'],
    ['S4', 'Fumo: quem está em casa e onde', 'Todos', 'Kit', 'ext'],
    ['S5', 'Medicamentos ou detergentes fora do sítio com uma criança em casa', 'Cozinha, sala', 'Kit', 'ext'],
    ['S6', 'Janela aberta com uma criança na divisão', 'Sala', 'Kit', 'ext'],
    ['S7', 'Pessoa desconhecida em casa', 'Entrada, sala', 'Kit e router da casa', 'parte'],
    ['S8', 'Porta ou janela aberta ao sair de casa ou à noite', 'Entrada', 'Kit', 'ext'],
    ['S9', 'Fuga de água', 'Cozinha', 'Outro IoT', 'fut'],
    ['S10', 'Fumo, chama ou água no chão vistos pela câmara', 'Cozinha', 'Kit; outro IoT opcional', 'fut'],
  ]],
  ['Cuidado', [
    ['C1', 'Animal que não vai à taça da comida nem à da água', 'Cozinha', 'Kit', 'hoje'],
    ['C2', 'Pessoa idosa: ninguém na cozinha até ao meio-dia', 'Cozinha', 'Kit', 'hoje'],
    ['C3', 'Caixa de medicamentos que não sai do lugar até à hora habitual', 'Cozinha, sala', 'Kit', 'ext'],
    ['C4', 'Casa fria com uma pessoa na sala', 'Sala', 'Kit', 'ext'],
    ['C5', 'Pessoa caída no chão', 'Cozinha, sala', 'Kit', 'fut'],
    ['C6', 'Uma criança chega a casa', 'Entrada', 'Kit', 'hoje'],
    ['C7', 'Animal que sai quando a porta abre', 'Entrada', 'Kit', 'ext'],
  ]],
  ['Conveniência', [
    ['V1', 'Sair de casa sem as chaves, a carteira ou o livro', 'Entrada', 'Kit', 'hoje'],
    ['V2', '“Onde está o livro?”', 'Todos', 'Kit', 'hoje'],
    ['V3', 'Aparelho ligado numa divisão vazia', 'Sala', 'Kit', 'hoje'],
    ['V4', 'Animal no sofá proibido', 'Sala', 'Kit', 'hoje'],
    ['V5', 'Presença e postura: luz e aquecimento', 'Sala', 'Kit; outro IoT (termóstato)', 'ext'],
    ['V6', 'Gestos: luz, televisão, máquina do café', 'Sala, cozinha', 'Kit', 'fut'],
  ]],
  ['Exterior', [
    ['E1', 'Intrusão: alguém força uma porta ou uma janela', 'Porta, traseiras', 'Câmara exterior; kit', 'ext'],
    ['E2', 'Pessoa no jardim ou no portão à noite', 'Jardim, portão', 'Outro IoT', 'ext'],
    ['E3', 'Portão aberto com o cão ou uma criança no jardim', 'Jardim, portão', 'Outro IoT', 'ext'],
    ['E4', 'Furto: a bicicleta ou a encomenda deixam de ser vistas', 'Jardim, porta', 'Outro IoT; kit', 'ext'],
    ['E5', 'Encomenda ou correio entregue', 'Porta', 'Outro IoT; lâmpada do kit', 'ext'],
    ['E6', 'O carro chega a casa', 'Garagem', 'Outro IoT', 'ext'],
    ['E7', 'Coisas deixadas lá fora: bicicleta, mangueira, caixote do lixo', 'Jardim', 'Outro IoT', 'ext'],
    ['E8', 'Animais no jardim: rega durante 5 s', 'Jardim', 'Outro IoT', 'ext'],
    ['E9', 'O cão à porta das traseiras: abrir a portinhola', 'Traseiras', 'Outro IoT', 'fut'],
  ]],
  ['Linha do tempo da casa', [
    ['T1', 'Chegar tarde demais: o que esteve perto da criança, e quando', 'Cozinha', 'Kit', 'ext'],
    ['T2', 'O que aconteceu às 4h?', 'Todos, exterior', 'Kit; câmara exterior opcional', 'ext'],
  ]],
];
const VIA = { hoje: 'hoje', parte: 'hoje', ext: 'ext', fut: 'fut' };
const all = CAT.flatMap(([, xs]) => xs);
$('#cat-count').textContent = `${all.length} casos`;
$('#catalog').innerHTML = CAT.map(([g, xs]) => `<div class="prow"><h3>${esc(g)}</h3><div>${xs.map(([c, t, place, dev, v]) =>
  `<span class="pill ${VIA[v]}" title="${esc(place)} · ${esc(dev)}"><b>${c}</b>${esc(t)}</span>`).join('')}</div></div>`).join('');

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
  ['Cortes do pitch', '', [
    ['pitch-livro.mp4', 'O livro', ''],
    ['pitch-pessoa.mp4', 'A pessoa desconhecida', ''],
    ['pitch-casa-vazia.mp4', 'Ninguém em casa', ''],
  ]],
  ['Execuções sem montagem', 'O sistema real a processar as gravações do laboratório, sem edição.', [
    ['proof-book.mp4', 'O livro', 'Aviso disparado pela regra: livro visto a 0,94.'],
    ['proof-face-blurred.mp4', 'O rosto (desfocado)', 'Filipe a 0,54 e 0,63; limiar 0,40.'],
    ['proof-nobody.mp4', 'Ninguém em casa', 'Aviso com os dois aparelhos ligados.'],
  ]],
  ['Filmes completos', '', [
    ['film-livro.mp4', 'Exemplo 1: o livro', ''],
    ['film-pessoa.mp4', 'Exemplo 2: a pessoa desconhecida', ''],
    ['film-pessoas.mp4', 'Exemplo 3: as pessoas', ''],
  ]],
];
$('#videos').innerHTML = VIDEOS.map(([g, d, xs]) => `<div class="vgroup"><h2 class="sec">${esc(g)}</h2>${d ? `<p>${esc(d)}</p>` : ''}<div class="vgrid">${xs.map(([f, t, p]) =>
  `<article class="vcard" data-f="${f}"><video src="/media/${f}" controls preload="metadata" playsinline></video><div class="t"><h3>${esc(t)}</h3>${p ? `<p>${esc(p)}</p>` : ''}</div></article>`).join('')}</div></div>`).join('');
document.querySelectorAll('#videos .vcard video').forEach((v) => v.addEventListener('error', () => v.closest('.vcard').remove()));
document.querySelectorAll('#videos video').forEach((v) => v.addEventListener('play', () => document.querySelectorAll('#videos video').forEach((o) => o !== v && o.pause())));

// ------------------------------------------------------------------ zoom on figures (drawn in the page)
const zoom = $('#zoom');
document.addEventListener('click', (e) => {
  const f = e.target.closest('[data-src], img[data-zoom]');
  if (f) { zoom.querySelector('img').src = f.dataset.src || f.src; zoom.hidden = false; return; }
  if (e.target.closest('#zoom')) zoom.hidden = true;
});
addEventListener('keydown', (e) => { if (e.key === 'Escape') zoom.hidden = true; });
