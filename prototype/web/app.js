// ThingTracker prototype: camera, zones, observation loop, and the Things tab of the Altice app.
// Only zone crops leave the browser, and only when a zone changed (or every 45 s as a heartbeat).

const $ = (id) => document.getElementById(id);
const video = $('video'), kitimg = $('kitimg'), stage = $('stage'), zonesEl = $('zones'), drawEl = $('draw');
const OBSERVE_EVERY = 3000, HEARTBEAT = 45000, CHANGE_THRESHOLD = 10;

let state = { zones: [], things: [], rules: [], events: [], spend: { usd: 0, calls: 0 }, settings: {} };
let source = 'webcam', stream = null, kitTimer = null, watchTimer = null, busy = false;
let editing = false, pendingZone = null;
const lastSent = {};           // zone_id -> {sig, t}
const seenEvents = new Set();  // for alerts that slide in
let firstLoad = true;

// ------------------------------------------------------------------ helpers
const hm = (d) => d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
const when = (ts) => {
  const d = new Date(ts * 1000), now = new Date();
  return d.toDateString() === now.toDateString() ? hm(d) : `${d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}, ${hm(d)}`;
};
const usd = (v) => '$' + v.toFixed(4);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const mark = '<svg aria-hidden="true"><use href="#mark"/></svg>';
const ti = (name) => `<span class="ti" style="--i:url(/web/icons/tabler/${name}.svg)"></span>`;
const ICONS = { key: 'fluent/key', purse: 'fluent/purse', glasses: 'fluent/glasses', mobile_phone: 'fluent/mobile_phone',
  hot_beverage: 'fluent/hot_beverage', laptop: 'fluent/laptop', remote: 'remote' };
const thingIcon = (t) => {
  const crop = t.last_seen?.crop;
  if (crop) return `<img class="crop" src="/crops/${encodeURIComponent(crop)}" alt="">`;
  return ICONS[t.icon] ? `<img src="/web/icons/${ICONS[t.icon]}.svg" alt="">` : mark;
};

async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Error ${res.status}`);
  return body;
}
const setStatus = (text) => { $('status').textContent = text; };
const stageMsg = (text) => { $('stagemsg').textContent = text || ''; };

// ------------------------------------------------------------------ video sources
const media = () => (source === 'kit' ? kitimg : video);
const mediaSize = () => (source === 'kit' ? [kitimg.naturalWidth, kitimg.naturalHeight] : [video.videoWidth, video.videoHeight]);
// Where the picture actually is inside the stage (object-fit: contain leaves bars).
function contentRect() {
  const [mw, mh] = mediaSize();
  const sw = stage.clientWidth, sh = stage.clientHeight;
  if (!mw || !mh) return { x: 0, y: 0, w: sw, h: sh };
  const s = Math.min(sw / mw, sh / mh);
  return { x: (sw - mw * s) / 2, y: (sh - mh * s) / 2, w: mw * s, h: mh * s };
}

async function useSource(next) {
  source = next;
  if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
  clearInterval(kitTimer);
  video.hidden = next === 'kit'; kitimg.hidden = next !== 'kit';
  if (next === 'webcam') {
    stageMsg('Starting the webcam…');
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 } }, audio: false });
      video.srcObject = stream; await video.play(); stageMsg('');
    } catch { stageMsg('No access to the webcam. Allow the camera in the browser, or choose “Recorded video”.'); }
  } else if (next === 'file') {
    video.srcObject = null;
    stageMsg('Choose a clip recorded with the camera. It plays as if it were live.');
    $('file').click();
  } else {
    stageMsg('Asking the kit camera for a frame…');
    const pull = async () => {
      try {
        const r = await fetch('/api/kit/frame.jpg?t=' + Date.now());
        if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.status);
        const url = URL.createObjectURL(await r.blob());
        kitimg.onload = () => { URL.revokeObjectURL(url); stageMsg(''); renderZones(); };
        kitimg.src = url;
      } catch (e) { stageMsg('The kit camera is not answering: ' + e.message); }
    };
    pull(); kitTimer = setInterval(pull, 2000);
  }
  renderZones();
}
$('file').addEventListener('change', (e) => {
  const f = e.target.files[0];
  if (!f) return;
  video.src = URL.createObjectURL(f); video.play(); stageMsg('');
});
document.querySelectorAll('input[name="src"]').forEach((r) => r.addEventListener('change', () => useSource(r.value)));
video.addEventListener('loadedmetadata', () => renderZones());
new ResizeObserver(() => renderZones()).observe(stage);

// ------------------------------------------------------------------ zones
function renderZones(flash = []) {
  const c = contentRect();
  zonesEl.replaceChildren(...state.zones.map((z) => {
    const el = document.createElement('div');
    el.className = 'zone' + (flash.includes(z.id) ? ' pulse' : '');
    Object.assign(el.style, { left: c.x + z.x * c.w + 'px', top: c.y + z.y * c.h + 'px', width: z.w * c.w + 'px', height: z.h * c.h + 'px' });
    el.innerHTML = `<span>${esc(z.name)}</span>` + (editing ? `<button type="button" aria-label="Delete zone ${esc(z.name)}" data-del="${esc(z.id)}">${ti('x')}</button>` : '');
    return el;
  }));
}
zonesEl.addEventListener('click', async (e) => {
  const id = e.target.closest('[data-del]')?.dataset.del;
  if (id) await saveZones(state.zones.filter((z) => z.id !== id));
});
async function saveZones(zones) {
  const r = await api('/api/zones', { method: 'PUT', body: JSON.stringify(zones) });
  state.zones = r.zones; renderZones();
}
$('editzones').addEventListener('click', () => {
  editing = !editing;
  $('editzones').setAttribute('aria-pressed', String(editing));
  $('editzones').lastElementChild.textContent = editing ? 'Done' : 'Edit zones';
  drawEl.hidden = !editing; renderZones();
  stageMsg(editing ? 'Drag over the picture to draw a new zone (a table, the door, a shelf). Press × on a zone to delete it.' : '');
});
let drag = null;
drawEl.addEventListener('pointerdown', (e) => {
  const r = stage.getBoundingClientRect();
  drag = { x0: e.clientX - r.left, y0: e.clientY - r.top, box: document.createElement('div') };
  drag.box.className = 'zone'; drawEl.replaceChildren(drag.box); drawEl.setPointerCapture(e.pointerId);
});
drawEl.addEventListener('pointermove', (e) => {
  if (!drag) return;
  const r = stage.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
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
    const t = tiny.getContext('2d', { willReadFrequently: true });
    t.drawImage(full, sx, sy, sw, sh, 0, 0, 16, 12);
    const px = t.getImageData(0, 0, 16, 12).data, sig = [];
    for (let i = 0; i < px.length; i += 4) sig.push((px[i] + px[i + 1] + px[i + 2]) / 3);
    const prev = lastSent[z.id];
    const diff = prev ? sig.reduce((s, v, i) => s + Math.abs(v - prev.sig[i]), 0) / sig.length : 999;
    if (!force && prev && diff < CHANGE_THRESHOLD && Date.now() - prev.t < HEARTBEAT) continue;
    const scale = Math.min(1, 640 / Math.max(sw, sh));
    crop.width = Math.round(sw * scale); crop.height = Math.round(sh * scale);
    crop.getContext('2d').drawImage(full, sx, sy, sw, sh, 0, 0, crop.width, crop.height);
    out.push({ zone_id: z.id, jpeg_b64: crop.toDataURL('image/jpeg', 0.82).split(',')[1], sig });
  }
  return out;
}
async function observe(force = false) {
  if (busy) return;
  if (!state.zones.length) { setStatus('Draw at least one zone'); return; }
  const crops = grabCrops(force);
  if (!crops.length) { setStatus('No change in the zones'); return; }
  busy = true; setStatus(`Analysing ${crops.length} zone${crops.length > 1 ? 's' : ''}…`);
  const t0 = performance.now();
  try {
    await api('/api/observe', { method: 'POST', body: JSON.stringify({ crops: crops.map(({ zone_id, jpeg_b64 }) => ({ zone_id, jpeg_b64 })) }) });
    crops.forEach((c) => { lastSent[c.zone_id] = { sig: c.sig, t: Date.now() }; });
    renderZones(crops.map((c) => c.zone_id));
    setStatus(`Analysed at ${new Date().toLocaleTimeString('en-GB')} · ${((performance.now() - t0) / 1000).toFixed(1)} s`);
    await refresh();
  } catch (e) {
    setStatus(e.message);
    if (/Budget/.test(e.message)) stopWatching();
  } finally { busy = false; }
}
function stopWatching() {
  clearInterval(watchTimer); watchTimer = null;
  $('watch').setAttribute('aria-pressed', 'false');
  $('watch').innerHTML = `${ti('player-play')}<span>Start watching</span>`;
}
$('watch').addEventListener('click', () => {
  if (watchTimer) { stopWatching(); setStatus('Stopped'); return; }
  $('watch').setAttribute('aria-pressed', 'true');
  $('watch').innerHTML = `${ti('player-stop')}<span>Stop</span>`;
  observe(); watchTimer = setInterval(() => observe(), OBSERVE_EVERY);
});
$('once').addEventListener('click', () => observe(true));

// ------------------------------------------------------------------ Things tab
async function submitWith(form, fn) {
  const btn = form.querySelector('button[type="submit"]'); btn.disabled = true;
  try { await fn(); } finally { btn.disabled = false; }
}
$('askform').addEventListener('submit', (e) => {
  e.preventDefault();
  const q = $('ask').value.trim(); if (!q) return;
  submitWith(e.target, async () => {
    try {
      const r = await api('/api/ask', { method: 'POST', body: JSON.stringify({ question: q }) });
      $('answer').innerHTML = `<p>${esc(r.answer)}</p>` + (r.crop ? `<img src="/crops/${encodeURIComponent(r.crop)}" alt="Last picture of it">` : '');
    } catch (err) { $('answer').innerHTML = `<p>${esc(err.message)}</p>`; }
    $('answer').hidden = false; refresh();
  });
});
$('ruleform').addEventListener('submit', (e) => {
  e.preventDefault();
  const s = $('rule').value.trim(); if (!s) return;
  submitWith(e.target, async () => {
    try {
      const r = await api('/api/rules', { method: 'POST', body: JSON.stringify({ sentence: s }) });
      $('rule').value = ''; toast('New sensor', r.title); refresh();
    } catch (err) { toast('Could not create the sensor', err.message); }
  });
});
$('addthing').addEventListener('click', () => { $('thingform').hidden = !$('thingform').hidden; if (!$('thingform').hidden) $('thingname').focus(); });
$('thingform').addEventListener('submit', (e) => {
  e.preventDefault();
  const n = $('thingname').value.trim(); if (!n) return;
  submitWith(e.target, async () => {
    await api('/api/things', { method: 'POST', body: JSON.stringify({ name: n }) });
    $('thingname').value = ''; $('thingform').hidden = true; refresh();
  });
});
$('rules').addEventListener('change', async (e) => {
  const id = e.target.dataset?.rule; if (!id) return;
  await api(`/api/rules/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify({ active: e.target.checked }) });
  refresh();
});

let toastTimer;
function toast(title, text) {
  const t = $('toast');
  t.innerHTML = `${mark}<div><b>ThingTracker · ${esc(title)}</b>${esc(text)}</div>`;
  t.hidden = false; requestAnimationFrame(() => t.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.classList.remove('show'); setTimeout(() => { t.hidden = true; }, 260); }, 4500);
}

const ZONE = (id) => state.zones.find((z) => z.id === id)?.name || id;
const ACTION = { notify: 'Notify me', light_red: 'Light turns red', light_blue: 'Light turns blue', light_green: 'Light turns green',
  light_off: 'Light off', plug_off: 'Plug off', plug_on: 'Plug on' };

function render() {
  const s = state;
  $('things-title').textContent = `Your things (${s.things.length})`;
  $('things').innerHTML = s.things.map((t) => {
    const l = t.last_seen;
    const sub = l ? `<span class="sub">${esc(l.zone_name)} · ${when(l.ts)}${l.where ? ` · ${esc(l.where)}` : ''}</span>` : '<span class="sub none">Not seen yet</span>';
    return `<li class="card"><span class="ic">${thingIcon(t)}</span><span><b>${esc(t.name)}</b>${sub}</span><span></span></li>`;
  }).join('');

  $('sensors-title').textContent = `Sensors (${s.rules.length})`;
  $('rules').innerHTML = s.rules.map((r) => `
    <li class="card"><span class="ic">${mark}</span>
      <span><b>${esc(r.title)}</b><span class="q">${esc(ZONE(r.zone_id))} · ${esc(ACTION[r.action] || r.action)}${r.mode === 'not_by_deadline' ? ' · by ' + esc(r.deadline) : ''}</span></span>
      <label class="switch"><input type="checkbox" data-rule="${esc(r.id)}" ${r.active ? 'checked' : ''} aria-label="Turn on ${esc(r.title)}"><span></span></label>
    </li>`).join('') || '<li class="empty-note">No sensors yet. Describe one in a sentence above.</li>';

  const alerts = s.events.filter((e) => e.kind === 'alert').slice(0, 8);
  $('alerts').innerHTML = alerts.map((e) => `
    <li class="card"><span class="ic">${e.crop ? `<img class="crop" src="/crops/${encodeURIComponent(e.crop)}" alt="">` : mark}</span>
      <span><b>${esc(e.title || 'Alert')}</b><span class="sub red">${esc(e.text)} · ${when(e.ts)}</span></span><span></span></li>`).join('')
    || '<li class="empty-note">No alerts.</li>';

  $('log').innerHTML = s.events.map((e) => {
    const t = new Date(e.ts * 1000).toLocaleTimeString('en-GB');
    const act = e.action?.tool ? `<small>${e.action.live ? 'MCP' : 'MCP (simulated, not sent)'}: ${esc(e.action.tool)} ${esc(JSON.stringify(e.action.arguments))} → ${esc(e.action.result)}</small>` : '';
    const ev = e.evidence ? `<small>${esc(e.evidence)}</small>` : '';
    return `<li class="${e.kind === 'alert' ? 'alert' : ''} ${e.demo ? 'demo' : ''}"><time>${t}</time><span>${esc(e.text)}${ev}${act}</span></li>`;
  }).join('');

  const st = s.settings || {};
  $('spend').textContent = `AI spend ${usd(s.spend.usd)} of ${usd(st.budget_usd || 0)} · ${s.spend.calls} calls`;
  $('mode').textContent = st.ai ? 'AI on: real calls cost money' : 'AI off: simulated answers, $0';
  $('mode').classList.toggle('live', !!st.ai);
  renderZones();

  for (const e of s.events) {
    if (seenEvents.has(e.id)) continue;
    seenEvents.add(e.id);
    if (!firstLoad && e.kind === 'alert') toast(e.title || 'Alert', e.text);
  }
  firstLoad = false;
}
async function refresh() {
  try { state = await api('/api/state'); render(); } catch { setStatus('Server not reachable'); }
}

// ------------------------------------------------------------------ tabs and devices
document.querySelectorAll('.tabs button').forEach((b) => b.addEventListener('click', () => {
  document.querySelectorAll('.tabs button').forEach((x) => x.classList.toggle('on', x === b));
  const tab = b.dataset.tab;
  ['things', 'devices', 'menu', 'other'].forEach((t) => { $('tab-' + t).hidden = t !== tab; });
  if (tab === 'devices') loadDevices();
}));

const DEVICE_ICON = { contactSensor: 'contact-sensor', gateway: 'security-hub', smokeSensor: 'smoke-sensor',
  temperatureSensor: 'temperature-sensor', camera: 'camera', bulb: 'light', plug: 'plug' };
const ORDER = ['contactSensor', 'gateway', 'smokeSensor', 'temperatureSensor', 'camera', 'bulb', 'plug'];
async function loadDevices() {
  try {
    const r = await api('/api/devices');
    const list = [];
    (function walk(o) {
      if (Array.isArray(o)) o.forEach(walk);
      else if (o && typeof o === 'object') { if (o.capabilities && o.name) list.push(o); else Object.values(o).forEach(walk); }
    })(r.data);
    list.sort((a, b) => ORDER.indexOf(a.type) - ORDER.indexOf(b.type));
    const newest = Math.max(...list.map((d) => d.lastCommunicationTime || 0));
    $('devcount').textContent = list.length;
    $('devices').innerHTML = list.map((d) => {
      const cap = Object.fromEntries(d.capabilities.map((c) => [c.type, c.value]));
      const offline = newest - (d.lastCommunicationTime || 0) > 24 * 3600 * 1000;
      let status = 'On';
      if (d.type === 'contactSensor') status = cap.sensorState === 'alarm' ? 'Open' : 'Closed';
      if (d.type === 'temperatureSensor') status = `${cap.temperatureValue} °C | ${cap.humidityValue} %`;
      if (d.type === 'plug') status = `${cap.power === 'on' ? 'On' : 'Off'} · ${cap.instantPower ?? 0} W`;
      if (d.type === 'bulb') status = cap.power === 'on' ? 'On' : 'Off';
      const sub = offline ? '<span class="sub red">Disconnected</span>' : `<span class="sub">${esc(status)}</span>`;
      const icon = DEVICE_ICON[d.type] ? `<img src="/web/icons/app/${DEVICE_ICON[d.type]}.png" alt="">` : mark;
      return `<li class="card"><span class="ic">${icon}</span><span><b>${esc(d.name)}</b>${sub}</span><span></span></li>`;
    }).join('');
    $('devsrc').textContent = r.source === 'live' ? 'Live from the MCP.' : 'Not logged in to the MCP: showing the real readings from 16 Nov.';
  } catch (e) { $('devsrc').textContent = e.message; }
}

// live clock in the iPhone status bar
const tick = () => { $('iostime').textContent = new Date().toLocaleTimeString('en-GB', { hour: 'numeric', minute: '2-digit' }); };
tick(); setInterval(tick, 15000);

useSource('webcam');
refresh();
// open a tab from the address, e.g. http://127.0.0.1:8765/#devices
const startTab = document.querySelector(`.tabs button[data-tab="${location.hash.slice(1)}"]`);
if (startTab) startTab.click();
setInterval(refresh, 2500);
