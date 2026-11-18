// ThingTracker prototype: the kit camera with the edge service's live boxes, and the Things tab of the Altice app.
// Everything is automatic: the edge service (edge.py) analyses the camera by itself whenever something moves.

const $ = (id) => document.getElementById(id);
const video = $('video'), kitimg = $('kitimg'), stage = $('stage');

let state = { zones: [], things: [], rules: [], events: [], spend: { usd: 0, calls: 0 }, settings: {} };
let source = 'kit', stream = null, kitTimer = null;
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
    kitimg.onload = () => stageMsg('');
    kitimg.onerror = () => stageMsg('The kit camera is not answering. Is it powered and on the Wi-Fi?');
    kitimg.src = '/api/kit/stream.mjpg?t=' + Date.now();
  }
}
$('file').addEventListener('change', (e) => {
  const f = e.target.files[0];
  if (!f) return;
  video.src = URL.createObjectURL(f); video.play(); stageMsg('');
});
document.querySelectorAll('input[name="src"]').forEach((r) => r.addEventListener('change', () => useSource(r.value)));

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
