// ThingTracker prototype: camera, zones, observation loop, and the Things tab of the Altice app.
// Only zone crops leave the browser, and only when a zone changed (or every 45 s as a heartbeat).

const $ = (id) => document.getElementById(id);
const video = $('video'), kitimg = $('kitimg'), stage = $('stage'), zonesEl = $('zones'), drawEl = $('draw');
const OBSERVE_EVERY = 3000, HEARTBEAT = 45000, CHANGE_THRESHOLD = 10;

let state = { zones: [], things: [], rules: [], events: [], spend: { usd: 0, calls: 0 }, settings: {} };
let source = 'kit', stream = null, kitTimer = null, watchTimer = null, busy = false;
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
  const crop = t.last_seen?.crop || t.fingerprint?.crops?.[0];
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
  if (next !== 'kit') kitimg.removeAttribute('src');   // closes the live connection
  video.hidden = next === 'kit'; kitimg.hidden = next !== 'kit';
  // The computer's own camera is never used: the home's camera is the kit camera.
  if (next === 'file') {
    video.srcObject = null;
    stageMsg('Choose a clip recorded with the camera. It plays as if it were live.');
    $('file').click();
  } else {
    // Live view: the server keeps one RTSP connection open and streams each new frame (MJPEG), no plug-in needed.
    stageMsg('Connecting to the kit camera… (about 5 s, waiting for a keyframe)');
    kitimg.onload = () => { stageMsg(''); renderZones(); };
    kitimg.onerror = () => stageMsg('The kit camera is not answering. Is it powered and on the Wi-Fi?');
    kitimg.src = '/api/kit/stream.mjpg?t=' + Date.now();
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
  zonesEl.hidden = source === 'kit' && !editing;   // on the kit camera the edge service finds the places itself
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
  drawEl.hidden = !editing; if (!editing) cancelZone(); renderZones();
  stageMsg(editing ? 'Drag over the picture to draw a new zone (a table, the door, a shelf). Press × on a zone to delete it.' : '');
});
let drag = null;
drawEl.addEventListener('pointerdown', (e) => {
  if (pendingZone) cancelZone();
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
  placeNameBox(x1, y1, x2, y2);
});
// Put the name box right under the new rectangle, or above it, or inside it, whichever fits.
function placeNameBox(x1, y1, x2, y2) {
  const f = $('zoneform');
  f.hidden = false;
  const sw = stage.clientWidth, sh = stage.clientHeight, w = f.offsetWidth, h = f.offsetHeight;
  const left = Math.max(8, Math.min(x1, sw - w - 8));
  let top = y2 + 8;
  if (top + h > sh - 8) top = y1 - h - 8;
  if (top < 8) top = Math.min(Math.max(8, y1 + 8), sh - h - 8);
  Object.assign(f.style, { left: left + 'px', top: top + 'px' });
  $('zonename').focus();
}
function cancelZone() { pendingZone = null; $('zonename').value = ''; $('zoneform').hidden = true; drawEl.replaceChildren(); }
$('zonename').addEventListener('keydown', (e) => { if (e.key === 'Escape') cancelZone(); });
$('zoneform').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = $('zonename').value.trim();
  if (!name || !pendingZone) return;
  const id = 'z' + (Math.max(0, ...state.zones.map((z) => Number(z.id.slice(1)) || 0)) + 1);
  await saveZones([...state.zones, { id, name, ...pendingZone }]);
  pendingZone = null; $('zonename').value = ''; $('zoneform').hidden = true; drawEl.replaceChildren();
});
$('zonecancel').addEventListener('click', cancelZone);

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
    const r = await api('/api/observe', { method: 'POST', body: JSON.stringify({ crops: crops.map(({ zone_id, jpeg_b64 }) => ({ zone_id, jpeg_b64 })) }) });
    crops.forEach((c) => { lastSent[c.zone_id] = { sig: c.sig, t: Date.now() }; });
    if (r.ai === false) {
      setStatus('AI is off: the picture was not analysed ($0). Start the server with TT_AI=1 to analyse it.');
      return;
    }
    renderZones(crops.map((c) => c.zone_id));
    setStatus(`Analysed at ${new Date().toLocaleTimeString('en-GB')} · ${((performance.now() - t0) / 1000).toFixed(1)} s`);
    await refresh();
  } catch (e) {
    setStatus(/Too soon/.test(e.message) ? 'Waiting a moment between analyses…' : e.message);
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
$('things').addEventListener('click', async (e) => {
  const b = e.target.closest('[data-enrol]'); if (!b) return;
  try {
    await api(`/api/things/${encodeURIComponent(b.dataset.enrol)}/enrol`, { method: 'POST' });
    if (source !== 'kit') document.querySelector('input[name="src"][value="kit"]')?.click();
    refresh();
  } catch (err) { toast('Could not start the registration', err.message); }
});
$('suggestions').addEventListener('click', async (e) => {
  const b = e.target.closest('[data-suggest]'); if (!b) return;
  const ev = state.events.find((x) => x.id === b.dataset.suggest); if (!ev) return;
  try {
    const r = await api('/api/rules', { method: 'POST', body: JSON.stringify({ sentence: ev.sentence }) });
    toast('New sensor', r.title); refresh();
  } catch (err) { toast('Could not create the sensor', err.message); }
});

// What the edge service sees, drawn over the kit camera: one box per object, person or registration view.
const boxesEl = $('boxes');
async function drawBoxes() {
  if (source !== 'kit' || document.hidden) { boxesEl.replaceChildren(); return; }
  let b;
  try { b = await api('/api/edge/boxes'); } catch { return; }
  const r = contentRect();
  Object.assign(boxesEl.style, { left: r.x + 'px', top: r.y + 'px', width: r.w + 'px', height: r.h + 'px' });
  boxesEl.dataset.stale = b.age > 4 ? '1' : '';
  if (b.age > 20) { boxesEl.replaceChildren(); return; }
  boxesEl.innerHTML = b.boxes.map((x) => {
    const [x1, y1, x2, y2] = x.box;
    return `<div class="box ${esc(x.kind)}" style="left:${x1 * 100}%;top:${y1 * 100}%;width:${(x2 - x1) * 100}%;height:${(y2 - y1) * 100}%"><b>${esc(x.label)}</b></div>`;
  }).join('');
}
setInterval(drawBoxes, 700);

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
const THING = (id) => state.things.find((x) => x.id === id)?.name || id;
// A rule in words: local rules (compiled from a sentence, run by the rules engine) or the older zone rules.
function ruleText(r) {
  const act = ACTION[r.action] || r.action;
  if (r.engine === 'local') {
    const where = r.place ? ` on the ${r.place}` : '';
    const what = {
      left_for: `${THING(r.thing_id)}${where} for ${r.minutes} min`,
      nobody_for: `Nobody here for ${r.minutes} min`,
      someone_arrives: 'Someone arrives in an empty room',
      seen_in: `${THING(r.thing_id)} seen${where}`,
    }[r.kind] || r.kind;
    return `${what} · ${act}`;
  }
  return `${ZONE(r.zone_id)} · ${act}${r.mode === 'not_by_deadline' ? ' · by ' + r.deadline : ''}`;
}
// The edge service: idle until something moves, then it analyses (prototype/edge.py)
function renderEdge(e) {
  const pill = $('edge');
  if (!e || !e.online) { pill.hidden = true; return; }
  pill.hidden = false;
  pill.dataset.state = e.state;
  const n = (v) => Number(v || 0).toLocaleString('en');
  pill.textContent = e.state === 'registering' ? 'Camera: registering a thing'
    : e.state === 'active'
    ? `Camera: movement, analysing · ${n(e.analysed)} analyses`
    : `Camera idle, waiting for movement · ${n(e.checked)} checks, ${n(e.analysed)} analyses`;
}
const ACTION = { notify: 'Notify me', light_red: 'Light turns red', light_blue: 'Light turns blue', light_green: 'Light turns green',
  light_off: 'Light off', plug_off: 'Plug off', plug_on: 'Plug on' };

function render() {
  const s = state;
  renderEdge(s.edge);
  $('things-title').textContent = `Your things (${s.things.length})`;
  $('things').innerHTML = s.things.map((t) => {
    const l = t.last_seen;
    const sub = l ? `<span class="sub">${esc(l.zone_name)} · ${when(l.ts)}${l.where ? ` · ${esc(l.where)}` : ''}</span>` : '<span class="sub none">Not seen yet</span>';
    const en = s.enrol && s.enrol.thing_id === t.id ? s.enrol : null, fp = t.fingerprint;
    let side = '';
    if (en) side = `<span class="enrol-prog" role="progressbar" aria-valuemin="0" aria-valuemax="${en.target}" aria-valuenow="${en.got}" style="--p:${en.got / en.target}"><span>${en.got}/${en.target}</span></span>`;
    else if (!fp) side = `<button type="button" class="mini" data-enrol="${esc(t.id)}">${ti('focus-2')}Register</button>`;
    const views = fp ? `<span class="views" title="Visual fingerprint: ${fp.n} views">${fp.crops.slice(0, 5).map((c) => `<img src="/crops/${encodeURIComponent(c)}" alt="">`).join('')}<small>${fp.n} views</small></span>` : '';
    const sub2 = en ? '<span class="sub">Show it to the kit camera and turn it slowly</span>' : sub;
    return `<li class="card thing"><span class="ic">${thingIcon(t)}</span><span><b>${esc(t.name)}</b>${sub2}${views}</span>${side}</li>`;
  }).join('');

  $('sensors-title').textContent = `Sensors (${s.rules.length})`;
  $('rules').innerHTML = s.rules.map((r) => `
    <li class="card"><span class="ic">${mark}</span>
      <span><b>${esc(r.title)}</b><span class="q">${esc(ruleText(r))}</span></span>
      <label class="switch"><input type="checkbox" data-rule="${esc(r.id)}" ${r.active ? 'checked' : ''} aria-label="Turn on ${esc(r.title)}"><span></span></label>
    </li>`).join('') || '<li class="empty-note">No sensors yet. Describe one in a sentence above.</li>';

  const sugg = s.events.filter((e) => e.kind === 'suggest' && !s.rules.some((r) => r.sentence === e.sentence)).slice(0, 3);
  $('suggest').hidden = !sugg.length;
  $('suggestions').innerHTML = sugg.map((e) => `
    <li class="card"><span class="ic">${ti('sparkles')}</span>
      <span><b>${esc(e.title)}</b><span class="q">“${esc(e.sentence)}”</span></span>
      <button type="button" class="mini" data-suggest="${esc(e.id)}">${ti('circle-plus')}Add</button></li>`).join('');
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
  $('mode').textContent = st.ai ? 'AI on: real calls cost money' : 'AI off: nothing analysed, $0';
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

// Scale the 402 x 874 pt iPhone 18 Pro screen to the frame, so the app never reflows or overflows (see .device in app.css).
const screenWrap = $('screenwrap'), device = $('device');
function fitDevice() {
  if (matchMedia('(max-width: 520px)').matches) { device.style.zoom = ''; return; }
  device.style.zoom = screenWrap.clientWidth / 402;
}
new ResizeObserver(fitDevice).observe(screenWrap);
fitDevice();

// live clock in the iPhone status bar
const tick = () => { $('iostime').textContent = new Date().toLocaleTimeString('en-GB', { hour: 'numeric', minute: '2-digit' }); };
tick(); setInterval(tick, 15000);
// live: the edge keeps adding sightings and alerts, so keep the screen current while it is visible
setInterval(() => { if (!document.hidden) refresh(); }, 3000);

useSource('kit');
refresh();
// open a tab from the address, e.g. http://127.0.0.1:8765/#devices
const startTab = document.querySelector(`.tabs button[data-tab="${location.hash.slice(1)}"]`);
if (startTab) startTab.click();
setInterval(refresh, 2500);
