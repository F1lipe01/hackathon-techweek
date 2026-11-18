// Track Things prototype: camera, zones, observation loop, and the "Coisas" tab of the Altice app.
// Only zone crops leave the browser, and only when a zone changed (or every 45 s as a heartbeat).

const $ = (id) => document.getElementById(id);
const video = $('video'), kitimg = $('kitimg'), stage = $('stage'), zonesEl = $('zones'), drawEl = $('draw');
const OBSERVE_EVERY = 3000, HEARTBEAT = 45000, CHANGE_THRESHOLD = 10;

let state = { zones: [], things: [], rules: [], events: [], spend: { usd: 0, calls: 0 }, settings: {} };
let source = 'webcam', stream = null, kitTimer = null, watchTimer = null, busy = false;
let editing = false, pendingZone = null;
const lastSent = {};            // zone_id -> {sig, t}
const seenEvents = new Set();   // for toasts
let firstLoad = true;

// ------------------------------------------------------------------ helpers
const fmtTime = (ts) => {
  const d = new Date(ts * 1000), now = new Date();
  const hm = d.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
  return d.toDateString() === now.toDateString() ? `às ${hm}` : `a ${d.toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' })} às ${hm}`;
};
const usd = (v) => v.toLocaleString('pt-PT', { minimumFractionDigits: 4, maximumFractionDigits: 4 }) + ' USD';
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const trail = '<svg aria-hidden="true"><use href="#trail"/></svg>';

async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Erro ${res.status}`);
  return body;
}
function setStatus(text) { $('status').textContent = text; }
function stageMsg(text) { $('stagemsg').textContent = text || ''; }

// ------------------------------------------------------------------ media sources
function media() { return source === 'kit' ? kitimg : video; }
function mediaSize() {
  const m = media();
  return source === 'kit' ? [m.naturalWidth, m.naturalHeight] : [m.videoWidth, m.videoHeight];
}
// Where the picture actually is inside the stage (object-fit: contain leaves bars).
function contentRect() {
  const [mw, mh] = mediaSize();
  const sw = stage.clientWidth, sh = stage.clientHeight;
  if (!mw || !mh) return { x: 0, y: 0, w: sw, h: sh };
  const s = Math.min(sw / mw, sh / mh);
  const w = mw * s, h = mh * s;
  return { x: (sw - w) / 2, y: (sh - h) / 2, w, h };
}

async function useSource(next) {
  source = next;
  stopWebcam(); clearInterval(kitTimer);
  video.hidden = next === 'kit'; kitimg.hidden = next !== 'kit';
  if (next === 'webcam') {
    stageMsg('A ligar a webcam…');
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 } }, audio: false });
      video.srcObject = stream; await video.play(); stageMsg('');
    } catch (e) { stageMsg('Sem acesso à webcam. Autorize a câmara no navegador ou escolha «Vídeo gravado».'); }
  } else if (next === 'file') {
    video.srcObject = null;
    stageMsg('Escolha um vídeo gravado com a câmara (é reproduzido como se fosse em direto).');
    $('file').click();
  } else {
    stageMsg('A pedir imagem à câmara do kit…');
    const pull = async () => {
      try {
        const r = await fetch('/api/kit/frame.jpg?t=' + Date.now());
        if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.status);
        const url = URL.createObjectURL(await r.blob());
        kitimg.onload = () => { URL.revokeObjectURL(url); stageMsg(''); renderZones(); };
        kitimg.src = url;
      } catch (e) { stageMsg('Câmara do kit sem resposta: ' + e.message); }
    };
    pull(); kitTimer = setInterval(pull, 2000);
  }
  renderZones();
}
function stopWebcam() { if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; } }

$('file').addEventListener('change', (e) => {
  const f = e.target.files[0];
  if (!f) return;
  video.src = URL.createObjectURL(f); video.play(); stageMsg('');
});
document.querySelectorAll('input[name="src"]').forEach((r) => r.addEventListener('change', () => useSource(r.value)));
video.addEventListener('loadedmetadata', renderZones);
new ResizeObserver(renderZones).observe(stage);

// ------------------------------------------------------------------ zones
function renderZones(flash = []) {
  const c = contentRect();
  zonesEl.replaceChildren(...state.zones.map((z) => {
    const el = document.createElement('div');
    el.className = 'zone' + (flash.includes(z.id) ? ' pulse' : '');
    Object.assign(el.style, { left: c.x + z.x * c.w + 'px', top: c.y + z.y * c.h + 'px', width: z.w * c.w + 'px', height: z.h * c.h + 'px' });
    el.innerHTML = `<span>${esc(z.name)}</span>` + (editing ? `<button type="button" aria-label="Apagar zona ${esc(z.name)}" data-del="${esc(z.id)}">×</button>` : '');
    return el;
  }));
}
zonesEl.addEventListener('click', async (e) => {
  const id = e.target.dataset?.del;
  if (!id) return;
  await saveZones(state.zones.filter((z) => z.id !== id));
});
async function saveZones(zones) {
  const r = await api('/api/zones', { method: 'PUT', body: JSON.stringify(zones) });
  state.zones = r.zones; renderZones();
}

$('editzones').addEventListener('click', () => {
  editing = !editing;
  $('editzones').setAttribute('aria-pressed', String(editing));
  $('editzones').textContent = editing ? 'Terminar zonas' : 'Desenhar zonas';
  drawEl.hidden = !editing; renderZones();
  if (editing) stageMsg('Arraste sobre a imagem para desenhar uma zona (uma mesa, a porta, a taça do gato).'); else stageMsg('');
});

let drag = null;
drawEl.addEventListener('pointerdown', (e) => {
  const r = stage.getBoundingClientRect();
  drag = { x0: e.clientX - r.left, y0: e.clientY - r.top, box: document.createElement('div') };
  drag.box.className = 'zone'; drawEl.replaceChildren(drag.box); drawEl.setPointerCapture(e.pointerId);
});
drawEl.addEventListener('pointermove', (e) => {
  if (!drag) return;
  const r = stage.getBoundingClientRect();
  const x = e.clientX - r.left, y = e.clientY - r.top;
  Object.assign(drag.box.style, { left: Math.min(x, drag.x0) + 'px', top: Math.min(y, drag.y0) + 'px', width: Math.abs(x - drag.x0) + 'px', height: Math.abs(y - drag.y0) + 'px' });
});
drawEl.addEventListener('pointerup', (e) => {
  if (!drag) return;
  const r = stage.getBoundingClientRect(), c = contentRect();
  const x1 = Math.min(e.clientX - r.left, drag.x0), y1 = Math.min(e.clientY - r.top, drag.y0);
  const x2 = Math.max(e.clientX - r.left, drag.x0), y2 = Math.max(e.clientY - r.top, drag.y0);
  drag = null;
  if (x2 - x1 < 20 || y2 - y1 < 20) { drawEl.replaceChildren(); return; }
  const clamp = (v) => Math.max(0, Math.min(1, v));
  pendingZone = { x: clamp((x1 - c.x) / c.w), y: clamp((y1 - c.y) / c.h), w: clamp((x2 - x1) / c.w), h: clamp((y2 - y1) / c.h) };
  $('zoneform').hidden = false; $('zonename').focus();
});
$('zoneform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = $('zonename').value.trim();
  if (!name || !pendingZone) return;
  const id = 'z' + (Math.max(0, ...state.zones.map((z) => Number(z.id.slice(1)) || 0)) + 1);
  await saveZones([...state.zones, { id, name, ...pendingZone }]);
  pendingZone = null; $('zonename').value = ''; $('zoneform').hidden = true; drawEl.replaceChildren();
});
$('zonecancel').addEventListener('click', () => { pendingZone = null; $('zoneform').hidden = true; drawEl.replaceChildren(); });

// ------------------------------------------------------------------ observation loop
const full = document.createElement('canvas'), crop = document.createElement('canvas'), tiny = document.createElement('canvas');
tiny.width = 16; tiny.height = 12;

function grabCrops(force) {
  const [mw, mh] = mediaSize();
  if (!mw || !mh) return [];
  full.width = mw; full.height = mh;
  full.getContext('2d').drawImage(media(), 0, 0, mw, mh);
  const out = [];
  for (const z of state.zones) {
    const sx = z.x * mw, sy = z.y * mh, sw = Math.max(8, z.w * mw), sh = Math.max(8, z.h * mh);
    // change signature: 16x12 grey thumbnail
    const t = tiny.getContext('2d', { willReadFrequently: true });
    t.drawImage(full, sx, sy, sw, sh, 0, 0, 16, 12);
    const px = t.getImageData(0, 0, 16, 12).data, sig = [];
    for (let i = 0; i < px.length; i += 4) sig.push((px[i] + px[i + 1] + px[i + 2]) / 3);
    const prev = lastSent[z.id];
    const diff = prev ? sig.reduce((s, v, i) => s + Math.abs(v - prev.sig[i]), 0) / sig.length : 999;
    const stale = !prev || Date.now() - prev.t > HEARTBEAT;
    if (!force && diff < CHANGE_THRESHOLD && !stale) continue;
    const scale = Math.min(1, 640 / Math.max(sw, sh));
    crop.width = Math.round(sw * scale); crop.height = Math.round(sh * scale);
    crop.getContext('2d').drawImage(full, sx, sy, sw, sh, 0, 0, crop.width, crop.height);
    out.push({ zone_id: z.id, jpeg_b64: crop.toDataURL('image/jpeg', 0.82).split(',')[1], sig });
  }
  return out;
}

async function observe(force = false) {
  if (busy) return;
  if (!state.zones.length) { setStatus('Desenhe pelo menos uma zona'); return; }
  const crops = grabCrops(force);
  if (!crops.length) { setStatus('Sem alterações nas zonas'); return; }
  busy = true; setStatus(`A analisar ${crops.length} zona(s)…`);
  const t0 = performance.now();
  try {
    const r = await api('/api/observe', { method: 'POST', body: JSON.stringify({ crops: crops.map(({ zone_id, jpeg_b64 }) => ({ zone_id, jpeg_b64 })) }) });
    crops.forEach((c) => { lastSent[c.zone_id] = { sig: c.sig, t: Date.now() }; });
    renderZones(crops.map((c) => c.zone_id));
    setStatus(`Analisado ${new Date().toLocaleTimeString('pt-PT')} · ${((performance.now() - t0) / 1000).toFixed(1)} s`);
    await refresh();
  } catch (e) {
    setStatus(e.message);
    if (/Budget/.test(e.message)) stopWatching();
  } finally { busy = false; }
}
function stopWatching() {
  clearInterval(watchTimer); watchTimer = null;
  $('watch').setAttribute('aria-pressed', 'false'); $('watch').textContent = 'Começar a observar';
}
$('watch').addEventListener('click', () => {
  if (watchTimer) { stopWatching(); setStatus('Parado'); return; }
  $('watch').setAttribute('aria-pressed', 'true'); $('watch').textContent = 'Parar';
  observe(); watchTimer = setInterval(() => observe(), OBSERVE_EVERY);
});
$('once').addEventListener('click', () => observe(true));

// ------------------------------------------------------------------ app (Coisas tab)
$('askform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = $('ask').value.trim(); if (!q) return;
  const btn = e.submitter; btn.disabled = true;
  try {
    const r = await api('/api/ask', { method: 'POST', body: JSON.stringify({ question: q }) });
    $('answer').innerHTML = `<p>${esc(r.answer)}</p>` + (r.crop ? `<img src="/crops/${encodeURIComponent(r.crop)}" alt="Última imagem da coisa">` : '');
    $('answer').hidden = false;
    refresh();
  } catch (err) { $('answer').innerHTML = `<p>${esc(err.message)}</p>`; $('answer').hidden = false; }
  finally { btn.disabled = false; }
});
$('ruleform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const s = $('rule').value.trim(); if (!s) return;
  const btn = e.submitter; btn.disabled = true; btn.textContent = 'A criar…';
  try {
    const r = await api('/api/rules', { method: 'POST', body: JSON.stringify({ sentence: s }) });
    $('rule').value = ''; toast('Novo sensor', r.title); refresh();
  } catch (err) { toast('Não foi possível criar o sensor', err.message); }
  finally { btn.disabled = false; btn.textContent = 'Criar'; }
});
$('thingform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const n = $('thingname').value.trim(); if (!n) return;
  await api('/api/things', { method: 'POST', body: JSON.stringify({ name: n }) });
  $('thingname').value = ''; refresh();
});
$('rules').addEventListener('change', async (e) => {
  const id = e.target.dataset?.rule; if (!id) return;
  await api(`/api/rules/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify({ active: e.target.checked }) });
  refresh();
});

let toastTimer;
function toast(title, text) {
  const t = $('toast');
  t.innerHTML = `${trail}<div><b>Track Things · ${esc(title)}</b>${esc(text)}</div>`;
  t.hidden = false; requestAnimationFrame(() => t.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.classList.remove('show'); setTimeout(() => { t.hidden = true; }, 260); }, 4500);
}

const ZONE_NAME = (id) => state.zones.find((z) => z.id === id)?.name || id;
const ACTION = { notify: 'Aviso no telemóvel', light_red: 'Luz vermelha', light_blue: 'Luz azul', light_green: 'Luz verde', light_off: 'Desligar a luz', plug_off: 'Desligar a tomada', plug_on: 'Ligar a tomada' };

function render() {
  const s = state;
  $('things').innerHTML = s.things.map((t) => {
    const l = t.last_seen;
    const thumb = l?.crop ? `<img src="/crops/${encodeURIComponent(l.crop)}" alt="">` : trail;
    const sub = l ? `<span class="sub">Visto ${fmtTime(l.ts)} · ${esc(l.zone_name)}${l.where ? ', ' + esc(l.where) : ''}</span>` : '<span class="sub none">Ainda não visto</span>';
    return `<li class="card"><span class="thumb">${thumb}</span><span><b>${esc(t.name)}</b>${sub}</span><span></span></li>`;
  }).join('');

  $('rules').innerHTML = s.rules.map((r) => `
    <li class="card"><span class="thumb">${trail}</span>
      <span><b>${esc(r.title)}</b><span class="q">${esc(ZONE_NAME(r.zone_id))} · «${esc(r.question)}» → ${esc(ACTION[r.action] || r.action)}${r.mode === 'not_by_deadline' ? ' · até às ' + esc(r.deadline) : ''}</span></span>
      <label class="switch"><input type="checkbox" data-rule="${esc(r.id)}" ${r.active ? 'checked' : ''} aria-label="Ativar ${esc(r.title)}"><span></span></label>
    </li>`).join('') || '<li class="q">Ainda não há sensores. Escreva uma frase acima.</li>';

  const alerts = s.events.filter((e) => e.kind === 'alert').slice(0, 8);
  $('alerts').innerHTML = alerts.map((e) => `
    <li class="card alert"><span class="thumb">${e.crop ? `<img src="/crops/${encodeURIComponent(e.crop)}" alt="">` : trail}</span>
      <span><b>${esc(e.title || 'Aviso')}</b><span class="sub">${esc(e.text)} · ${fmtTime(e.ts)}</span></span><span></span></li>`).join('')
    || '<li class="q">Sem avisos.</li>';

  $('log').innerHTML = s.events.map((e) => {
    const t = new Date(e.ts * 1000).toLocaleTimeString('pt-PT');
    const act = e.action?.tool ? `<small>${e.action.live ? 'MCP' : 'MCP (simulação)'}: ${esc(e.action.tool)} ${esc(JSON.stringify(e.action.arguments))} → ${esc(e.action.result)}</small>` : '';
    const ev = e.evidence ? `<small>${esc(e.evidence)}</small>` : '';
    return `<li class="${e.kind === 'alert' ? 'alert' : ''} ${e.demo ? 'demo' : ''}"><time>${t}</time><span>${esc(e.text)}${ev}${act}</span></li>`;
  }).join('');

  const st = s.settings || {};
  $('spend').textContent = `${usd(s.spend.usd)} de ${usd(st.budget_usd || 0)} · ${s.spend.calls} pedidos`;
  $('meta').textContent = `Protótipo · ações ${st.live_actions ? 'reais no kit' : 'em simulação'}`;
  renderZones();

  for (const e of s.events) {
    if (seenEvents.has(e.id)) continue;
    seenEvents.add(e.id);
    if (!firstLoad && e.kind === 'alert') toast(e.title || 'Aviso', e.text);
  }
  firstLoad = false;
}

async function refresh() {
  try { state = await api('/api/state'); render(); } catch (e) { setStatus('Servidor indisponível'); }
}

// tabs
document.querySelectorAll('.tabs button').forEach((b) => b.addEventListener('click', async () => {
  document.querySelectorAll('.tabs button').forEach((x) => x.classList.toggle('on', x === b));
  const tab = b.dataset.tab;
  ['coisas', 'dispositivos', 'outros'].forEach((t) => { $('tab-' + t).hidden = t !== tab; });
  $('apptitle').textContent = tab === 'coisas' ? 'Coisas' : 'Hack 3';
  if (tab === 'dispositivos') loadDevices();
}));

async function loadDevices() {
  try {
    const r = await api('/api/devices');
    const list = [];
    (function walk(o) {
      if (Array.isArray(o)) o.forEach(walk);
      else if (o && typeof o === 'object') { if (o.capabilities && o.name) list.push(o); else Object.values(o).forEach(walk); }
    })(r.data);
    $('devsrc').textContent = r.source === 'live' ? 'Estado em direto, através do MCP.' : 'Sem sessão no MCP: dados reais de 16 de novembro.';
    $('devices').innerHTML = list.map((d) => {
      const online = d.connectivity?.online ?? d.online ?? d.status;
      const st = online === false || online === 'offline' ? '<span class="sub" style="color:var(--app-red)">Desligado</span>' : '<span class="sub">Ligado</span>';
      return `<li class="card"><span class="thumb">${trail}</span><span><b>${esc(d.name)}</b>${st}</span><span></span></li>`;
    }).join('');
  } catch (e) { $('devsrc').textContent = e.message; }
}

$('apptitle').textContent = 'Coisas';
useSource('webcam');
refresh();
setInterval(refresh, 2500);
