// ThingTracker prototype.
// Left: the kit camera, with the boxes the edge service (edge.py) draws when something moves.
// Right: a copy of the Altice app (beta, captured from a phone over adb on 18 Nov 2026): same screens, sizes, colours
// and transitions (tabs switch instantly; screens cross-fade in 280-300 ms; sheets slide up), plus the Things tab and
// the assistant button. Its data comes from the prototype's local SQLite database (server.py, store.py).

const $ = (id) => document.getElementById(id);
const EMBED = new URLSearchParams(location.search).has('embed');
if (EMBED) document.body.classList.add('embed');
// on a real phone (/phone): the app alone, full screen; the phone's own status bar replaces the drawn one
const PHONE = new URLSearchParams(location.search).has('phone');
if (PHONE) document.body.classList.add('phone-page');
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const hm = (ts) => new Date(ts * 1000).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
const ago = (ts) => {
  const m = Math.max(0, Math.round((Date.now() / 1000 - ts) / 60));
  return m < 1 ? 'just now' : m < 60 ? `${m}min ago` : `${Math.floor(m / 60)}h ${m % 60}min ago`;
};
async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Error ${res.status}`);
  return body;
}
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private window: keep it in memory only */ } },
};

// ------------------------------------------------------------------ icons (drawn to match the app's outline set)
const S = (d, extra = '') => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" ${extra}>${d}</svg>`;
const I = {
  plus: S('<circle cx="12" cy="12" r="9.2"/><path d="M12 8v8M8 12h8"/>'),
  more: S('<circle cx="12" cy="12" r="9.2"/><circle cx="8" cy="12" r=".6" fill="currentColor"/><circle cx="12" cy="12" r=".6" fill="currentColor"/><circle cx="16" cy="12" r=".6" fill="currentColor"/>'),
  filter: S('<path d="M3 7h9M17 7h4M3 17h4M12 17h9"/><circle cx="14.5" cy="7" r="2.5"/><circle cx="9.5" cy="17" r="2.5"/>'),
  search: S('<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/>'),
  chevUp: S('<path d="m5 15 7-7 7 7"/>', 'class="chev"'),
  chevR: S('<path d="m9 5 7 7-7 7"/>', 'class="chev-r"'),
  back: S('<path d="m15 4-8 8 8 8"/>'),
  x: S('<path d="M5 5l14 14M19 5 5 19"/>'),
  star: S('<path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9Z"/>'),
  starOn: S('<path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9Z" fill="currentColor"/>'),
  sort: S('<path d="M8 4v16M4 8l4-4 4 4M16 20V4M12 16l4 4 4-4"/>'),
  home: S('<path d="M4 10.5 12 4l8 6.5V20H4Z"/><path d="M10 20v-6h4v6"/>'),
  door: S('<path d="M6 21V3.5h12V21M3.5 21h17"/><circle cx="14.6" cy="12.5" r=".7" fill="currentColor"/>'),
  user: S('<circle cx="12" cy="12" r="9.2"/><circle cx="12" cy="10" r="3.2"/><path d="M6.2 18.4a7 7 0 0 1 11.6 0"/>'),
  bell: S('<path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15Z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>'),
  gear: S('<circle cx="12" cy="12" r="3"/><path d="M12 2.8v2.4M12 18.8v2.4M4.2 7.5l2.1 1.2M17.7 15.3l2.1 1.2M4.2 16.5l2.1-1.2M17.7 8.7l2.1-1.2"/><circle cx="12" cy="12" r="6.5"/>'),
  help: S('<circle cx="12" cy="12" r="9.2"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.3 2.4c-.5.2-.8.7-.8 1.2V14"/><circle cx="12" cy="17" r=".6" fill="currentColor"/>'),
  logout: S('<path d="M10 4H5v16h5M15 8l4 4-4 4M19 12H9"/>'),
  wandC: '<svg viewBox="0 0 24 24"><path d="M3.5 20.5 14 10" stroke="#3aa58b" stroke-width="2.4" stroke-linecap="round"/><path d="m16 3 1 2.6 2.6 1-2.6 1-1 2.6-1-2.6-2.6-1 2.6-1Z" fill="#c837b5"/><circle cx="20.5" cy="12.5" r="1.2" fill="#c837b5"/><circle cx="11" cy="4" r="1" fill="#c837b5"/></svg>',
  wand: S('<path d="M4 20 15 9M15 4v2M19 8h2M18 5l1-1M12 5l-1-1"/><path d="m14 7 3 3"/>'),
  eventsC: '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="12" height="17" rx="2" fill="#f08a24"/><circle cx="16.5" cy="16.5" r="5" fill="#2f7be8"/><path d="M16.5 14.2v2.6l1.6 1" stroke="#fff" stroke-width="1.4" stroke-linecap="round" fill="none"/></svg>',
  // ThingTracker's sensors: a line bell in the app's teal (the wand stays only on the Altice app's own Scenarios)
  sensor: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2abe9e" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15Z"/><path d="M10 20.5a2 2 0 0 0 4 0"/></svg>',
  bellC: '<svg viewBox="0 0 24 24"><path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.6 2.1H4.4Z" fill="#6c3fd1"/><circle cx="12" cy="20.6" r="2" fill="#6c3fd1"/></svg>',
  infoC: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#22a99a"/><path d="M12 11v6" stroke="#fff" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="7.6" r="1.3" fill="#fff"/></svg>',
  gearC: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="#f08a24"/><circle cx="12" cy="12" r="3.4" fill="#fff"/></svg>',
  recC: '<svg viewBox="0 0 24 24"><rect x="2" y="7" width="15" height="10" rx="3" fill="#36b08f"/><path d="m17 10.5 5-2.5v8l-5-2.5Z" fill="#2a8d72"/></svg>',
  play: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l12-7.5Z" fill="#1a2233"/></svg>',
  send: S('<path d="M5 12h13M13 6l6 6-6 6"/>', 'stroke-width="2.2"'),
  robot: '<svg viewBox="0 0 32 32" fill="none" stroke="#1a2233" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4.5v4"/><circle cx="16" cy="3.6" r="1.6" fill="#1a2233"/><rect x="6.5" y="8.5" width="19" height="15" rx="5.5"/><circle cx="12.3" cy="15.6" r="1.9" fill="#1a2233" stroke="none"/><circle cx="19.7" cy="15.6" r="1.9" fill="#1a2233" stroke="none"/><path d="M12.5 20h7"/><path d="M6.5 14.5H4.2M25.5 14.5h2.3"/><path d="M11 23.5v3h10v-3"/></svg>',
  medal: '<svg viewBox="0 0 48 48"><path d="m24 2 5.4 3.7 6.5-.5 2.2 6.1 5.5 3.6-1.6 6.3 2.5 6-4.8 4.4-.7 6.5-6.4 1.3L24 44l-4.6-4.6-6.4-1.3-.7-6.5-4.8-4.4 2.5-6-1.6-6.3 5.5-3.6 2.2-6.1 6.5.5Z" fill="#f0a531"/><circle cx="24" cy="24" r="12.5" fill="#c97a1c"/><path d="m24 15.5 2.5 5.1 5.6.8-4 3.9.9 5.6-5-2.6-5 2.6.9-5.6-4-3.9 5.6-.8Z" fill="#f7cf6b"/></svg>',
  shield: '<svg viewBox="0 0 72 80"><path d="M36 2 66 12v26c0 18-13 32-30 40C19 70 6 56 6 38V12Z" fill="#f05aa0"/><path d="M36 2 66 12v26c0 18-13 32-30 40Z" fill="#c8135f"/><path d="M6 38h60c-1 6-3 11-6.5 16H36V2v52H12.5C9 49 7 44 6 38Z" fill="#f78cbd" opacity=".55"/></svg>',
  bolt: '<svg viewBox="0 0 72 80"><path d="M42 2 10 46h22l-6 32 36-46H40Z" fill="#f5b52e"/><path d="M42 2 26 46h6l-6 32 36-46H40Z" fill="#e0901a"/></svg>',
  matter: '<svg viewBox="0 0 24 24" fill="none" stroke="#1a2233" stroke-width="1.8" stroke-linecap="round"><path d="M12 3v7M12 10 5.5 13.8M12 10l6.5 3.8M8 6.5l4 3.5 4-3.5M5 18l4-4.5M19 18l-4-4.5M9 20.5l3-6.5 3 6.5"/></svg>',
  thermo: '<svg viewBox="0 0 30 30"><rect x="11.5" y="3" width="7" height="17" rx="3.5" fill="#f08a24"/><circle cx="15" cy="22" r="5.5" fill="#f08a24"/><rect x="13.5" y="9" width="3" height="13" rx="1.5" fill="#e0452f"/></svg>',
  drop: '<svg viewBox="0 0 30 30"><path d="M15 3c4.5 6.4 8 10.8 8 15.4A8 8 0 0 1 7 18.4C7 13.8 10.5 9.4 15 3Z" fill="#28b6c9"/></svg>',
  book: '<svg viewBox="0 0 34 34"><rect x="7" y="4" width="20" height="26" rx="2.5" fill="#f6d31a"/><rect x="7" y="4" width="4" height="26" rx="2" fill="#d9b308"/><path d="M14 11h9M14 15h7" stroke="#6b5a12" stroke-width="1.6" stroke-linecap="round"/></svg>',
};
const TAB_ICON = {
  favorites: [I.star, I.starOn],
  areas: [S('<path d="m12 3 9 4.6-9 4.6-9-4.6Z"/><path d="m3 12.3 9 4.6 9-4.6M3 16.8l9 4.6 9-4.6"/>'),
          S('<path d="m12 3 9 4.6-9 4.6-9-4.6Z" fill="currentColor"/><path d="m3 12.3 9 4.6 9-4.6M3 16.8l9 4.6 9-4.6"/>', 'stroke-width="2.1"')],
  devices: [S('<rect x="4" y="4" width="7" height="7" rx="1.8"/><rect x="13" y="4" width="7" height="7" rx="1.8"/><rect x="4" y="13" width="7" height="7" rx="1.8"/><rect x="13" y="13" width="7" height="7" rx="1.8"/>'),
            '<svg viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="7.6" height="7.6" rx="2" fill="currentColor"/><rect x="12.9" y="3.5" width="7.6" height="7.6" rx="2" fill="currentColor"/><rect x="3.5" y="12.9" width="7.6" height="7.6" rx="2" fill="currentColor"/><rect x="12.9" y="12.9" width="7.6" height="7.6" rx="2" fill="currentColor"/></svg>'],
  things: [S('<path d="M4 9V6.5A2.5 2.5 0 0 1 6.5 4H9M15 4h2.5A2.5 2.5 0 0 1 20 6.5V9M4 15v2.5A2.5 2.5 0 0 0 6.5 20H9M20 15v2.5a2.5 2.5 0 0 1-2.5 2.5H15"/><circle cx="12" cy="12" r="2.6"/>'),
           S('<path d="M4 9V6.5A2.5 2.5 0 0 1 6.5 4H9M15 4h2.5A2.5 2.5 0 0 1 20 6.5V9M4 15v2.5A2.5 2.5 0 0 0 6.5 20H9M20 15v2.5a2.5 2.5 0 0 1-2.5 2.5H15"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/>', 'stroke-width="2.3"')],
  menu: [S('<path d="M4 6h16M4 12h16M4 18h16"/>'), S('<path d="M4 6h16M4 12h16M4 18h16"/>', 'stroke-width="2.6"')],
};
const DEVICE_PNG = { camera: 'camera', contactSensor: 'contact-sensor', bulb: 'light', plug: 'plug', gateway: 'security-hub',
  smokeSensor: 'smoke-sensor', temperatureSensor: 'temperature-sensor' };
// the demo home's simulated devices (prototype/site.py): drawn for ThingTracker in the app's flat style
const SIM_SVG = ['tv', 'speaker', 'blind', 'vacuum', 'coffee', 'oven', 'leakSensor', 'washer', 'heater', 'thermostat', 'lock', 'siren', 'motionSensor', 'ac'];
const devImg = (type) => (SIM_SVG.includes(type) ? `/web/icons/sim/${type}.svg` : `/web/icons/app/${DEVICE_PNG[type] || 'camera'}.png`);
// a thing's icon when it has no photo yet, from the word the detector searches for
const THING_ICON = { keys: '/web/icons/fluent/key.svg', wallet: '/web/icons/fluent/purse.svg', glasses: '/web/icons/fluent/glasses.svg',
  'tv remote control': '/web/icons/remote.svg', laptop: '/web/icons/fluent/laptop.svg', smartphone: '/web/icons/fluent/mobile_phone.svg',
  'coffee mug': '/web/icons/fluent/hot_beverage.svg', 'medication box': '/web/icons/sim/pills.svg', passport: '/web/icons/sim/passport.svg',
  backpack: '/web/icons/sim/backpack.svg' };
const thingIcon = (t) => (THING_ICON[t?.query] ? `<img src="${THING_ICON[t.query]}" alt="">` : null);
// on/off words of a simulated device
const SIM_WORDS = { lock: ['Locked', 'Unlocked', 'Lock', 'Unlock'], blind: ['Open', 'Closed', 'Open', 'Close'] };
const simWord = (d, on) => (SIM_WORDS[d.type] || ['On', 'Off', 'Turn on', 'Turn off'])[on ? 0 : 1];
const crop = (name) => `/crops/${encodeURIComponent(name)}`;

// ------------------------------------------------------------------ state
let state = { things: [], rules: [], events: [], edge: {}, enrol: null, settings: {}, spend: { usd: 0, calls: 0 }, home: null };
let firstLoad = true, lastSig = '';
const seen = new Set();
const ui = { tab: 'devices', search: { devices: false, things: false }, q: { devices: '', things: '' }, closed: new Set(),
  sort: 'az', types: new Set(), area: 'security', favs: new Set(store.get('tt-favs', [])), read: new Set(store.get('tt-read', [])) };
const chat = [];
const device = $('device'), views = $('views');
$('fab').innerHTML = I.robot;

// ------------------------------------------------------------------ the camera (left)
const video = $('video'), kitimg = $('kitimg'), stage = $('stage');
let source = 'kit';
const stageMsg = (t) => { $('stagemsg').textContent = t || ''; };
function useSource(next) {
  source = next;
  video.hidden = next === 'kit'; kitimg.hidden = next !== 'kit';
  stageMsg('Connecting to the kit camera… (about 5 s, waiting for a keyframe)');
  kitimg.onload = () => stageMsg('');
  kitimg.onerror = () => stageMsg('The kit camera is not answering. Is it powered and on the Wi-Fi?');
  if (PHONE) return;                  // the phone shows the app only; the camera is on the Mac
  if (EMBED) { pollFrames(); return; }
  kitimg.src = '/api/kit/stream.mjpg?t=' + Date.now();
}
// Inside the site, the camera is read frame by frame (GET /api/kit/frame.jpg, about 6 a second) instead of one long
// MJPEG stream: a browser keeps at most 6 connections to a host, and long streams from other tabs or the phone's camera
// screen can take them all, which left the picture black. Each frame is decoded before it is shown, so it never flickers.
let framesOn = false;
async function pollFrames() {
  if (framesOn) return;
  framesOn = true;
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  while (true) {
    if (document.hidden) { await wait(500); continue; }
    const t0 = performance.now();
    try {
      const r = await fetch('/api/kit/frame.jpg', { cache: 'no-store' });
      if (r.ok) {
        const url = URL.createObjectURL(await r.blob());
        const im = new Image(); im.src = url;
        await im.decode().catch(() => {});
        const old = kitimg.src;
        kitimg.src = url;
        document.querySelectorAll('img.live-cam').forEach((x) => { x.src = url; });
        if (old.startsWith('blob:')) setTimeout(() => URL.revokeObjectURL(old), 1000);
        stageMsg('');
        if (!kitimg.dataset.sized) { kitimg.dataset.sized = '1'; kitimg.addEventListener('load', fitStage, { once: true }); }
      } else stageMsg('The camera is not answering.');
    } catch { stageMsg('The camera is not answering.'); }
    await wait(Math.max(40, 160 - (performance.now() - t0)));
  }
}
// Where the picture sits inside the stage. "cover" fills the stage and crops the edges; "contain" letterboxes it.
function contentRect(el, w, h) {
  const sw = el.clientWidth, sh = el.clientHeight;
  if (!w || !h) return { x: 0, y: 0, w: sw, h: sh };
  const s = (el.dataset.fit === 'cover' ? Math.max : Math.min)(sw / w, sh / h);
  return { x: (sw - w * s) / 2, y: (sh - h * s) / 2, w: w * s, h: h * s };
}
// The stage takes whatever shape the grid gives it. Fill it when that crops less than about a quarter of the picture;
// otherwise show the whole picture with bars, so nothing the camera sees is hidden.
function fitStage() {
  const w = kitimg.naturalWidth || 16, h = kitimg.naturalHeight || 9;
  const r = (stage.clientWidth / stage.clientHeight) / (w / h);
  stage.dataset.fit = r > 0.8 && r < 1.35 ? 'cover' : 'contain';
}
new ResizeObserver(fitStage).observe(stage);
kitimg.addEventListener('load', fitStage, { once: true });
const boxHtml = (bs) => bs.map((x) => {
  const [x1, y1, x2, y2] = x.box;
  return `<div class="box ${esc(x.kind)}" style="left:${x1 * 100}%;top:${y1 * 100}%;width:${(x2 - x1) * 100}%;height:${(y2 - y1) * 100}%"><b>${esc(x.label)}</b></div>`;
}).join('');
let lastBoxes = { boxes: [], age: 99 };
async function drawBoxes() {
  if (document.hidden) return;
  try { lastBoxes = await api('/api/edge/boxes'); } catch { return; }
  const el = $('boxes');
  if (source !== 'kit') { el.replaceChildren(); return; }
  fitStage();    // the stream's size is only known after its first frame
  const r = contentRect(stage, kitimg.naturalWidth, kitimg.naturalHeight);
  Object.assign(el.style, { left: r.x + 'px', top: r.y + 'px', width: r.w + 'px', height: r.h + 'px' });
  el.dataset.stale = lastBoxes.age > 4 ? '1' : '';
  el.innerHTML = lastBoxes.age > 20 && !PLAYER.paused ? '' : boxHtml(lastBoxes.boxes);
  const live = document.querySelector('.page .lbox');   // the same boxes inside the app's registration screen
  if (live) live.innerHTML = lastBoxes.age > 20 ? '' : boxHtml(lastBoxes.boxes);
}
setInterval(drawBoxes, 700);
function renderEdge(e) {
  const pill = $('edge');
  if (!e || !e.online) { pill.hidden = true; return; }
  pill.hidden = false; pill.dataset.state = e.state;
  $('flow').dataset.state = e.state;     // the flow strip under the camera lights the stages in use
  const n = (v) => Number(v || 0).toLocaleString('en');
  // the state first; the detail is dropped on phones (app.css: .edge-pill .more)
  const [head, more] = e.state === 'registering' ? ['Camera registering', ': a thing is being shown']
    : e.state === 'active' ? ['Camera analysing', ` · movement · ${n(e.analysed)} analyses`]
    : ['Camera idle', ` · waiting for movement · ${n(e.checked)} checks, ${n(e.analysed)} analyses`];
  pill.innerHTML = `${esc(head)}<span class="more">${esc(more)}</span>`;
}
const devName = (id) => (state.home?.devices || []).find((d) => d.id === id)?.name;
function renderLog() {
  $('log').innerHTML = state.events.map((e) => {
    const t = new Date(e.ts * 1000).toLocaleTimeString('en-GB');
    // the device action: the exact MCP calls, sent (live) or only written down (dry run, the default)
    const calls = e.action?.calls || (e.action?.tool ? [{ tool: e.action.tool, arguments: e.action.arguments }] : []);
    const act = calls.length ? `<small title="${esc(calls.map((c) => `${c.tool} ${JSON.stringify(c.arguments)}`).join('\n'))}">${e.action.live ? 'MCP, sent' : 'MCP dry run, not sent'}: ${calls.map((c) => `${esc(c.tool)} ${esc(devName(c.arguments.deviceId) || c.arguments.deviceName || '')} ${esc(JSON.stringify(c.arguments.body ?? c.arguments))}`).join(', then ')}${e.action.live ? ` → ${esc(e.action.result)}` : ''}</small>` : '';
    const ev = e.evidence ? `<small>${esc(e.evidence)}</small>` : '';
    return `<li class="${e.kind === 'alert' ? 'alert' : ''}">${e.crop ? `<img src="${crop(e.crop)}" alt="">` : `<time>${t.slice(0, 5)}</time>`}<span>${e.crop ? `<time>${t.slice(0, 5)}</time> · ` : ''}${esc(e.text)}${ev}${act}</span></li>`;
  }).join('');
  const st = state.settings || {};
  $('spend').textContent = `AI spend $${(state.spend.usd || 0).toFixed(4)} of $${(st.budget_usd || 0).toFixed(2)} · ${state.spend.calls} calls`;
  // what is real right now: who answers, where the device states come from, whether actions reach the home
  const who = st.ai ? 'Claude answers (costs money)' : st.llm === 'local' ? 'Local text model, $0' : 'Templates, $0';
  const devs = state.door?.live ? 'devices live from the MCP' : 'devices: copy of 18 Nov';
  $('mode').textContent = `${who} · ${devs} · ${st.live_actions ? 'actions LIVE' : 'actions dry run'}`;
  $('mode').classList.toggle('live', !!(st.ai || st.live_actions));
}

// ------------------------------------------------------------------ the app (right): building blocks
const ahead = (title, icons) => `<header class="ahead"><h2>${esc(title)}</h2><div class="icons">${icons.map(([ic, act, label]) =>
  `<button type="button" class="ibtn" data-act="${act}" aria-label="${label}">${ic}</button>`).join('')}</div></header>`;
const phead = (title, sub, right = '') => `<header class="phead"><button type="button" class="ibtn" data-act="back" aria-label="Back">${I.back}</button>
  <div class="t"><b>${esc(title)}</b>${sub ? `<small>${esc(sub)}</small>` : ''}</div><div class="icons">${right}</div></header>`;
const sec = (key, title, count) => `<h3 class="sec ${ui.closed.has(key) ? 'closed' : ''}" data-act="sec" data-key="${esc(key)}">${esc(title)} (${count})${I.chevUp}</h3>`;
const row = (icon, label, act = '', extra = '') => `<button type="button" class="row ${extra}" ${act ? `data-act="${act}" data-title="${esc(label)}"` : ''}>${icon}<span>${esc(label)}</span>${extra.includes('danger') ? '<span></span>' : I.chevR}</button>`;
const statusCls = (s) => (s === 'Disconnected' ? 'red' : '');
const ttOf = (id) => (state.tt_devices || []).find((x) => x.id === id);
const ttStatus = (d) => { const t = ttOf(d.id); return t?.sim ? simWord(t, t.on) : t?.powers ? `${t.on ? 'On' : 'Off'} · powers ${t.powers}` : d.status; };
function deviceCard(d) {
  const round = d.type === 'plug' ? 'round' : '';
  const glow = d.type === 'bulb' ? (/^White/.test(d.status) ? 'white' : /^Orange/.test(d.status) ? 'orange' : '') : '';
  return `<li><button type="button" class="card ${d.raised ? 'raised' : ''}" data-act="device" data-id="${esc(d.id)}">
    <span class="ic ${round}${glow ? ` glow ${glow}` : ''}"><img src="${devImg(d.type)}" alt=""></span>
    <span><span class="nm">${esc(d.name)}</span><span class="st ${ttOf(d.id)?.sim && !ttOf(d.id).on ? 'grey' : statusCls(d.status)}">${esc(ttStatus(d))}</span></span><span></span></button></li>`;
}
function thingPhoto(t) { return t.last_seen?.crop || t.fingerprint?.crops?.[0] || null; }
function thingStatus(t) {
  if (state.enrol && state.enrol.thing_id === t.id) return [`Registering · ${state.enrol.got} of ${state.enrol.target}`, ''];
  const l = t.last_seen;
  if (l) return [`On the ${l.zone_name} · ${hm(l.ts)}`, ''];
  if (!t.fingerprint) return ['Not registered yet', 'grey'];
  return ['Not seen yet', 'grey'];
}
function thingCard(t, act = 'thing') {
  const p = thingPhoto(t), [st, cls] = thingStatus(t);
  const ic = p ? `<span class="ic photo"><img src="${crop(p)}" alt=""></span>` : `<span class="ic">${thingIcon(t) || I.book}</span>`;
  return `<li><button type="button" class="card" data-act="${act}" data-id="${esc(t.id)}">${ic}
    <span><span class="nm">${esc(t.name)}</span><span class="st ${cls}">${esc(st)}</span></span><span></span></button></li>`;
}
// People are things whose description starts with "person" ("person · family" when the app saved who they are).
const isPerson = (t) => /^person\b/.test(t?.description || '');
/** The person a thing belongs to (things.owner), when the family linked it to one. */
const ownerOf = (t) => (t?.owner ? state.things.find((x) => x.id === t.owner && isPerson(x)) : null);
const relationOf = (t) => { const r = (t?.description || '').split('·')[1]?.trim(); return r ? r[0].toUpperCase() + r.slice(1) : ''; };
/** The scenarios that use a thing or a person: by thing_id, and for people every rule about someone unknown (it
 *  depends on who the camera knows). Counted from the real rules only. */
const rulesFor = (t) => state.rules.filter((r) => (r.unknown ? isPerson(t) : r.thing_id === t.id));
const addedOn = (ts) => {
  if (!ts) return '';
  const d = new Date(ts * 1000), now = new Date();
  return d.toDateString() === now.toDateString() ? 'Added today' : `since ${d.getDate()} ${d.toLocaleString('en-GB', { month: 'short' })}`;
};
function itemCard(t) {
  const p = thingPhoto(t), person = isPerson(t), n = rulesFor(t).length;
  const kind = person ? 'Person' : 'Thing';   // the group above says who they are (Family, Guests)
  const meta = [ownerOf(t) ? `Belongs to ${ownerOf(t).name}` : kind, addedOn(t.created), n ? `${n} scenario${n === 1 ? '' : 's'}` : 'No scenarios'].join(' · ');
  const l = t.last_seen;
  const ic = p ? `<span class="ic photo${person ? ' round' : ''}"><img src="${crop(p)}" alt=""></span>` : `<span class="ic">${person ? I.user : thingIcon(t) || I.book}</span>`;
  return `<li><button type="button" class="card" data-act="thing" data-id="${esc(t.id)}">${ic}
    <span><span class="nm">${esc(t.name)}</span><span class="st meta">${esc(meta)}</span>${l ? `<span class="st seen">On the ${esc(l.zone_name)} · ${hm(l.ts)}</span>` : ''}</span><span></span></button></li>`;
}
const watches = (r) => (r.kind === 'nobody_devices_on' ? `the empty home, ${(state.tt_devices || []).map((d) => d.name).join(', ')}` : r.kind === 'door_open_nobody' ? 'the door, the empty home' : r.unknown ? 'anyone not in Family' : state.things.find((t) => t.id === r.thing_id)?.name || (r.who ? r.who : 'the home'));
const homeName = () => state.home?.name || 'Hack 3';

// ------------------------------------------------------------------ tabs
function renderTabs() {
  document.querySelectorAll('#tabs button').forEach((b) => {
    const on = b.dataset.tab === ui.tab;
    b.classList.toggle('on', on);
    b.querySelector('.tab-ic').innerHTML = TAB_ICON[b.dataset.tab][on ? 1 : 0];
  });
  const dot = document.querySelector('#tabs .tab-dot');      // the Menu tab's dot: only when something is unread
  if (dot) dot.hidden = !unreadCount();
}
function setTab(t) {
  ui.tab = t;
  ['favorites', 'areas', 'devices', 'things', 'menu'].forEach((x) => { $('v-' + x).hidden = x !== t; });
  renderTabs(); renderTab(t);
}
function searchBox(key) {
  return ui.search[key] ? `<label class="search">${I.search}<input data-search="${key}" placeholder="Search" value="${esc(ui.q[key])}" autocomplete="off"></label>` : '';
}
// each tab has a fixed top (header + search) and a body that re-renders as data changes
function shell(id, top) {
  const el = $('v-' + id);
  if (el.dataset.top !== top) { el.innerHTML = `${top}<div class="tb"></div>`; el.dataset.top = top; }
  return el.querySelector('.tb');
}
function renderTab(t) {
  if (t === 'devices') renderDevices();
  else if (t === 'things') renderThings();
  else if (t === 'favorites') renderFavorites();
  else if (t === 'areas') renderAreas();
  else if (t === 'menu') renderMenu();
}
function devicesSorted() {
  let list = [...(state.home?.devices || [])];
  const q = ui.q.devices.trim().toLowerCase();
  if (q) list = list.filter((d) => d.name.toLowerCase().includes(q));
  if (ui.types.size) list = list.filter((d) => ui.types.has(d.type));
  list.sort((a, b) => a.name.localeCompare(b.name));
  if (ui.sort === 'za') list.reverse();
  return list;
}
function renderDevices() {
  const tb = shell('devices', ahead(homeName(), [[I.plus, 'add-device', 'Add device'], [I.filter, 'filter', 'Sort and filter'], [I.search, 'search-devices', 'Search']]) + searchBox('devices'));
  const list = devicesSorted(), rooms = state.home?.rooms || [];
  let html = '';
  const camRoom = (EMBED || PHONE) ? (state.home?.devices || []).find((d) => d.type === 'camera')?.room_id : null;
  for (const r of camRoom ? [...rooms].sort((a, b) => (b.id === camRoom) - (a.id === camRoom)) : rooms) {
    const ds = list.filter((d) => d.room_id === r.id);
    if (ds.length) html += sec('room-' + r.id, r.name, ds.length) + `<ul class="cards">${ds.map(deviceCard).join('')}</ul>`;
  }
  // devices connected to the app directly (third-party integrations, not part of the Altice kit; simulated here)
  const apps = (state.tt_devices || []).filter((d) => !d.kit && !d.sim);
  if (apps.length) html += sec('room-apps', 'Connected to the app', apps.length) + `<ul class="cards">${apps.map((d) => `<li><button type="button" class="card" data-act="tt-device" data-id="${esc(d.id)}">
    <span class="ic">${ttIcon(d)}</span><span><span class="nm">${esc(d.name)}</span><span class="st ${d.on ? '' : 'grey'}">${d.on ? 'On' : 'Off'} · ${esc(d.room)}</span></span><span></span></button></li>`).join('')}</ul>`;
  const none = list.filter((d) => !d.room_id);
  if (none.length) html += sec('room-none', 'Without room', none.length) + `<ul class="cards">${none.map(deviceCard).join('')}</ul>`;
  tb.innerHTML = html || '<div class="empty"><p>No devices match.</p></div>';
}
function renderThings() {
  const tb = shell('things', ahead(homeName(), [[I.plus, 'add-thing', 'Add thing'], [I.filter, 'filter', 'Sort and filter'], [I.search, 'search-things', 'Search']]) + searchBox('things'));
  const q = ui.q.things.trim().toLowerCase();
  const things = state.things.filter((t) => !q || t.name.toLowerCase().includes(q));
  if (!state.things.length) {
    tb.innerHTML = `<div class="empty"><svg class="art" style="--a:#2abe9e;--i:#1a2233"><use href="#mark"/></svg><h3>No things yet</h3>
      <p>Add the things you want to find later, like your keys or a book. The camera learns each one in a few seconds.</p>
      <button type="button" class="btn-p" data-act="add-thing">Add things</button></div>`;
    return;
  }
  const people = things.filter(isPerson), objects = things.filter((t) => !isPerson(t));
  let html = '';
  for (const [rel, label] of [['Family', 'Family'], ['Guest', 'Guests'], ['', 'People']]) {
    const g = people.filter((t) => relationOf(t) === rel);
    if (g.length) html += sec('th-' + (rel || 'people'), label, g.length) + `<ul class="cards">${g.map(itemCard).join('')}</ul>`;
  }
  if (objects.length) html += sec('th-things', 'Things', objects.length) + `<ul class="cards">${objects.map(itemCard).join('')}</ul>`;
  const sugg = state.events.filter((e) => e.kind === 'suggest' && !state.rules.some((r) => r.sentence === e.sentence)).slice(0, 3);
  if (sugg.length) html += sec('sugg', 'Suggested for your home', sugg.length) + `<ul class="cards">${sugg.map((e) => `<li><button type="button" class="card" data-act="suggest" data-id="${esc(e.id)}">
    <span class="ic">${I.sensor}</span><span><span class="nm">${esc(e.title)}</span><span class="st">Add: “${esc(e.sentence)}”</span></span><span></span></button></li>`).join('')}</ul>`;
  html += sec('sensors', 'Scenarios', state.rules.length) + `<ul class="cards">${state.rules.map((r) => `<li><button type="button" class="card" data-act="sensor" data-id="${esc(r.id)}">
    <span class="ic">${I.sensor}</span><span><span class="nm">${esc(r.title)}</span><span class="st meta"><b class="${r.active ? 'on' : 'off'}">${r.active ? 'Active' : 'Paused'}</b> · Watches: ${esc(watches(r))}</span></span><span></span></button></li>`).join('')}
    <li><button type="button" class="card new-scen" data-act="new-scenario"><span class="ic">${I.plus}</span><span><span class="nm">New scenario</span><span class="st meta">One sentence: when, and what to do</span></span><span></span></button></li></ul>`;
  tb.innerHTML = html;
}
function renderFavorites() {
  const tb = shell('favorites', ahead(homeName(), [[I.plus, 'add-device', 'Add device'], [I.more, 'fav-pick', 'Edit favorites']]));
  const favs = (state.home?.devices || []).filter((d) => ui.favs.has(d.id));
  tb.innerHTML = favs.length ? `<div style="height:20px"></div><ul class="cards">${favs.map(deviceCard).join('')}</ul>`
    : `<div class="empty">${I.medal.replace('<svg', '<svg class="art"')}<h3>No favorites yet</h3><p>Choose what you use most, for quick access from here.</p>
       <button type="button" class="btn-p" data-act="fav-pick">Add favorites</button></div>`;
}
function renderAreas() {
  const tb = shell('areas', ahead(homeName(), [[I.plus, 'add-device', 'Add device']]));
  const sec2 = ui.area === 'security';
  tb.innerHTML = `<div class="segc"><button type="button" class="${sec2 ? 'on' : ''}" data-act="area" data-id="security">Security</button><button type="button" class="${sec2 ? '' : 'on'}" data-act="area" data-id="energy">Energy</button></div>
    <div class="empty areas-empty">${(sec2 ? I.shield : I.bolt).replace('<svg', '<svg class="art"')}<h3>Welcome to ${sec2 ? 'security' : 'energy'}!</h3><p>See the amazing features that we have for you!</p>
    <button type="button" class="btn-p" data-act="stub" data-title="${sec2 ? 'Security' : 'Energy'}" style="height:46px;padding:0 44px">Let's try</button></div>`;
}
// Notifications: ThingTracker's alerts, the door and devices going on or off line (server.py), never made-up rows.
const NOTE_KINDS = ['alert', 'door', 'device', 'alarm'];
const notes = () => state.events.filter((e) => NOTE_KINDS.includes(e.kind));
function unreadCount() { return notes().filter((e) => !ui.read.has(e.id)).length; }
function renderMenu() {
  const tb = shell('menu', ahead(homeName(), [[I.plus, 'add-device', 'Add device']]));
  tb.innerHTML = `<h3 class="gtitle">Home</h3><div class="group">${row(I.wand, 'Scenarios', 'scenarios')}${row(I.door, 'Rooms', 'rooms')}${row(I.home, 'Houses management', 'stub')}</div>
    <h3 class="gtitle">Account</h3><div class="group">${row(I.user, 'Profile', 'stub')}
      <button type="button" class="row" data-act="notifications">${I.bell}<span>Notifications</span>${unreadCount() ? `<span class="badge">${unreadCount()}</span>` : I.chevR}</button>${row(I.gear, 'App settings', 'settings')}</div>
    <h3 class="gtitle">Support</h3><div class="group">${row(I.help, 'Help', 'stub')}<button type="button" class="row danger" data-act="stub" data-title="Log out">${I.logout}<span>Log out</span><span></span></button></div>
    <p class="powered">Powered by Altice Labs</p>`;
}

// ------------------------------------------------------------------ pushed screens (cross-fade, as in the app)
const stack = [];
function push(render, opts = {}) {
  const el = document.createElement('section');
  el.className = 'view page enter';
  el._render = render; el._live = !!opts.live;
  el.innerHTML = render();
  views.append(el); stack.push(el);
  device.classList.add('pushed');
  el.addEventListener('animationend', () => el.classList.remove('enter'), { once: true });
  opts.mount?.(el);
  return el;
}
// One screen at a time, never two superimposed: a pushed page is opaque at once and only its content fades in; a pop
// removes the pages at once and fades in the content of the screen it reveals.
function reveal(el) {
  if (!el) return;
  el.classList.remove('enter'); void el.offsetWidth; el.classList.add('enter');
  el.addEventListener('animationend', () => el.classList.remove('enter'), { once: true });
}
function pop(n = 1) {
  for (let i = 0; i < n && stack.length; i++) stack.pop().remove();
  document.body.classList.remove('alert-open');
  if (!stack.length) { device.classList.remove('pushed'); renderTab(ui.tab); }
  reveal(stack[stack.length - 1] || $('v-' + ui.tab));
}
function refreshPage() {
  const el = stack[stack.length - 1];
  if (!el || !el._live || el.contains(document.activeElement)) return;
  const top = el.scrollTop;
  el.innerHTML = el._render(); el.scrollTop = top;
}
const stub = (title) => push(() => `${phead(title, '')}<div class="empty"><p>This screen of the Altice app is not reproduced in the prototype.</p></div>`);

function devicePage(id) {
  const d = () => (state.home?.devices || []).find((x) => x.id === id) || {};
  const room = (x) => (state.home?.rooms || []).find((r) => r.id === x.room_id)?.name || 'Without room';
  push(() => {
    const x = d(), fav = ui.favs.has(id);
    const right = `<button type="button" class="ibtn" data-act="fav" data-id="${esc(id)}" aria-label="Favorite">${fav ? I.starOn : I.star}</button><button type="button" class="ibtn" data-act="stub" data-title="More" aria-label="More">${I.more}</button>`;
    const rows = `<div class="group">${row(I.wandC, 'Scenarios', 'scenarios')}${row(I.eventsC, 'Events', 'stub')}${row(I.bellC, 'Notifications', 'notifications')}${row(I.infoC, 'About', 'stub')}</div>`;
    if (x.type === 'camera') {
      return `${phead(x.name, room(x), right)}<div class="live">${EMBED ? `<img class="live-cam" src="${kitimg.src}" alt="Live view">` : '<img src="/api/kit/stream.mjpg?t=cam" alt="Live view">'}</div>
        <div class="single">${row(I.recC, 'Video Recordings', 'stub')}</div><div style="height:18px"></div>
        <div class="group">${row(I.gearC, 'Camera settings', 'stub')}${row(I.wandC, 'Scenarios', 'scenarios')}${row(I.eventsC, 'Events', 'stub')}${row(I.bellC, 'Notifications', 'notifications')}${row(I.infoC, 'About', 'stub')}</div>`;
    }
    if (x.type === 'temperatureSensor') {
      const [t, h] = String(x.status || '').split('|').map((v) => v.trim());
      return `${phead(x.name, room(x), right)}<p class="battery">Battery<span>Good</span></p>
        <div class="tiles"><div class="tile">${I.thermo}<small>Temperature</small><b>${esc(t || '')}</b></div><div class="tile">${I.drop}<small>Humidity</small><b>${esc(h || '')}</b></div></div>${rows}`;
    }
    const tt = ttOf(x.id);
    if (tt?.sim) {
      return `${phead(x.name, room(x), right)}<div class="hero"><img class="dev" src="${devImg(x.type)}" alt=""><span class="st ${tt.on ? '' : 'grey'}">${esc(simWord(tt, tt.on))}</span></div>
        <div class="single"><button type="button" class="btn-p sim-toggle" data-act="tt-toggle" data-id="${esc(x.id)}">${esc((SIM_WORDS[x.type] || ['On', 'Off', 'Turn on', 'Turn off'])[tt.on ? 3 : 2])}</button></div>
        <p class="sim-note">Simulated in this demo home: ThingTracker keeps its state and sends nothing to a real device.</p><div style="height:14px"></div>${rows}`;
    }
    if (!tt && x.id.startsWith('sim-')) {
      return `${phead(x.name, room(x), right)}<div class="hero"><img class="dev" src="${devImg(x.type)}" alt=""><span class="st">${esc(x.status)}</span></div>
        <p class="sim-note">Simulated sensor in this demo home.</p><div style="height:14px"></div>${rows}`;
    }
    const powers = tt?.powers ? `<div class="group powers"><div class="row">${ICON_LIGHT}<span>Powers</span><span class="val">${esc(tt.powers)}</span></div></div>
      <p class="sim-note">What this plug powers is set in ThingTracker and kept with your things, not in the Altice platform.</p>` : '';
    return `${phead(x.name, room(x), right)}<div class="hero"><img class="dev" src="${devImg(x.type)}" alt=""><span class="st ${statusCls(x.status)}">${esc(tt ? (tt.on ? 'On' : 'Off') : x.status)}</span></div>${powers}${rows}`;
  }, { live: true });
}
function thingPage(id) {
  const el = push(() => {
    const t = state.things.find((x) => x.id === id);
    if (!t) return `${phead('Thing', '')}<div class="empty"><p>This thing was removed.</p></div>`;
    const p = thingPhoto(t), [st, cls] = thingStatus(t), l = t.last_seen, fp = t.fingerprint;
    return `${phead(t.name, l ? l.room || '' : st, `<button type="button" class="ibtn" data-act="stub" data-title="More" aria-label="More">${I.more}</button>`)}
      <div class="hero">${p ? `<img class="photo" src="${crop(p)}" alt="">` : thingIcon(t)?.replace('<img', '<img class="dev"') || I.book.replace('<svg', '<svg width="60" height="60"')}<span class="st ${cls}">${esc(st)}</span></div>
      ${ownerOf(t) ? `<div class="owner-line"><img src="${crop(ownerOf(t).fingerprint?.crops?.[0] || '')}" alt=""><span>Belongs to <b>${esc(ownerOf(t).name)}</b></span></div>` : ''}
      ${fp ? `<div class="single" style="padding-top:12px"><div style="font-size:14.5px;font-weight:600;padding:2px 0 10px">Visual fingerprint · ${fp.n} views</div>
        <div class="views-grid">${fp.crops.map((c) => `<img src="${crop(c)}" alt="">`).join('')}</div></div><div style="height:18px"></div>` : ''}
      <div class="group">${row(I.eventsC, 'Sightings', 'sightings')}${row(I.sensor, 'Sensors', 'scenarios')}${row(I.bellC, 'Notifications', 'notifications')}</div>
      <div style="height:18px"></div><div class="group">${fp ? '' : row(I.recC, 'Register with the camera', 'reregister')}<button type="button" class="row danger" data-act="remove-thing">${I.x}<span>Remove thing</span><span></span></button></div>`;
  }, { live: true });
  el.dataset.id = id;
}
async function sightingsPage(id) {
  const t = state.things.find((x) => x.id === id);
  let list = [];
  try { list = (await api(`/api/things/${encodeURIComponent(id)}/sightings`)).sightings; } catch { /* shown as empty */ }
  push(() => `${phead('Sightings', t?.name || '')}
    ${list.length ? list.slice().reverse().map((o) => `<div class="nrow read"><span>${I.eventsC}</span><span><b>On the ${esc(o.zone_name)}${o.room ? ` · ${esc(o.room)}` : ''}</b><small>${hm(o.ts)} · ${ago(o.ts)}${o.where ? ` · ${esc(o.where)}` : ''}</small>${o.crop ? `<img class="crop" src="${crop(o.crop)}" alt="">` : ''}</span><span></span></div>`).join('')
      : '<div class="empty"><p>Not seen yet. The camera looks for it whenever something moves.</p></div>'}`);
}
const COMMON = [['Person', 'person', I.user], ['Book', 'book', I.book], ['Keys', 'keys', '<img src="/web/icons/fluent/key.svg" alt="">'], ['Wallet', 'wallet', '<img src="/web/icons/fluent/purse.svg" alt="">'],
  ['Glasses', 'glasses', '<img src="/web/icons/fluent/glasses.svg" alt="">'], ['Phone', 'smartphone', '<img src="/web/icons/fluent/mobile_phone.svg" alt="">'],
  ['Mug', 'coffee mug', '<img src="/web/icons/fluent/hot_beverage.svg" alt="">'], ['Laptop', 'laptop', '<img src="/web/icons/fluent/laptop.svg" alt="">'],
  ['TV remote', 'tv remote control', '<img src="/web/icons/remote.svg" alt="">']];
function addThingPage() {
  push(() => `${phead('', '')}<div class="ptitle">Add thing</div><p class="psub">Select the thing you want to track.</p>
    <div class="looking"><b><span class="pulse"></span>Looking through your cameras…</b><p>Choose a thing, then take a few photos of it with your phone, or show it to a camera. ThingTracker learns what it looks like.</p></div>
    <p class="lbl">Works with:</p><span class="chip"><img src="/web/icons/app/camera.png" alt="" style="width:20px">Work Room camera</span>
    <p class="lbl">Available things (${COMMON.length + 1})</p>
    <ul class="alist">${COMMON.map(([n, q, ic]) => `<li><button type="button" class="aitem" data-act="pick-thing" data-name="${esc(n)}" data-q="${esc(q)}">${ic}<span>${esc(n)}</span><span></span></button></li>`).join('')}
      <li><button type="button" class="aitem" data-act="other-thing">${I.plus}<span>Other…</span><span></span></button></li></ul>`);
}
function otherThingPage() {
  push(() => `<div class="step"><button type="button" class="ibtn x" data-act="back" aria-label="Close">${I.x}</button>
      <svg class="art" style="--a:#2abe9e;--i:#1a2233"><use href="#mark"/></svg><h3>Name your thing</h3>
      <p>Write its name in English, as the camera will search for it, for example “yellow book” or “car keys”.</p>
      <input class="field" id="othername" placeholder="Insert the name" maxlength="40" autocomplete="off"></div>
      <div class="bottom-bar"><button type="button" class="btn-p" data-act="other-next" disabled>Next</button></div>`,
  { mount: (el) => { const i = el.querySelector('#othername'); i.addEventListener('input', () => { el.querySelector('[data-act="other-next"]').disabled = !i.value.trim(); }); i.focus(); } });
}
// ------------------------------------------------------------------ adding a thing from photos taken with the phone
// Things › Add › a thing › Take photos (the phone's camera, or photos and video frames from the gallery) › name it ›
// Save › Create a scenario › Save. The photos become the thing's views; the edge service makes the fingerprint.
const pending = { name: '', q: '', photos: [] };
const ICON_CAMERA = '<svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="#1a2233" stroke-width="1.6" stroke-linejoin="round"><path d="M3 8.5A2.5 2.5 0 0 1 5.5 6h2l1.5-2h6l1.5 2h2A2.5 2.5 0 0 1 21 8.5v9a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5Z"/><circle cx="12" cy="12.5" r="3.6" stroke="#2abe9e" stroke-width="1.8"/></svg>';
const ICON_CHECK = '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5.5 12.5 4.2 4.2 8.8-9.4"/></svg>';
function methodPage(name, q) {
  Object.assign(pending, { name, q, photos: [], kind: 'thing' });
  push(() => `<div class="step"><button type="button" class="ibtn x" data-act="back" aria-label="Close">${I.x}</button>
      <div class="method-art">${ICON_CAMERA}</div><h3>Add the ${esc(name.toLowerCase())}</h3>
      <p>Take 6 to 8 photos of it with your phone, from the front, the back and the sides. A short video works too.</p></div>
    <input type="file" id="photoin" accept="image/*,video/*" multiple hidden>
    <div class="bottom-bar col"><button type="button" class="btn-p" data-act="take-photos">Take photos</button>
      <button type="button" class="btn-s" data-act="pick-camera">Show it to a home camera</button></div>`,
  { mount: (el) => el.querySelector('#photoin').addEventListener('change', (e) => loadPhotos(e.target.files)) });
}
/** Eight frames spread through a short video (a face turning, a thing turned round), as photos. */
async function framesFromVideo(file, n = 8) {
  const v = Object.assign(document.createElement('video'), { muted: true, playsInline: true, src: URL.createObjectURL(file) });
  await new Promise((ok, no) => { v.onloadedmetadata = ok; v.onerror = no; });
  const out = [];
  for (let i = 0; i < n; i++) {
    v.currentTime = (v.duration * (i + 0.5)) / n;
    await new Promise((ok) => { v.onseeked = ok; });
    const k = Math.min(1, 720 / Math.max(v.videoWidth, v.videoHeight));
    const c = Object.assign(document.createElement('canvas'), { width: Math.round(v.videoWidth * k), height: Math.round(v.videoHeight * k) });
    c.getContext('2d').drawImage(v, 0, 0, c.width, c.height);
    out.push(c.toDataURL('image/jpeg', 0.9));
  }
  URL.revokeObjectURL(v.src);
  return out;
}
async function loadPhotos(files) {
  const out = [];
  const video = [...files].find((x) => x.type.startsWith('video/'));
  if (video) out.push(...await framesFromVideo(video));
  for (const f of [...files].filter((x) => x.type.startsWith('image/')).slice(0, 8 - out.length)) {
    const bmp = await createImageBitmap(f), k = Math.min(1, 720 / Math.max(bmp.width, bmp.height));
    const c = Object.assign(document.createElement('canvas'), { width: Math.round(bmp.width * k), height: Math.round(bmp.height * k) });
    c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
    out.push(c.toDataURL('image/jpeg', 0.9));
  }
  if (!out.length) return;
  pending.photos = out;
  photosPage();
}
function photosPage() {
  push(() => `${phead('', '')}<div class="ptitle">New thing</div><p class="psub">${pending.photos.length} photos · from different sides</p>
    <div class="single"><div class="views-grid">${pending.photos.map((u) => `<img src="${u}" alt="">`).join('')}</div></div>
    <p class="lbl">Name</p><div class="fwrap"><input class="field" id="tname" placeholder="For example: Book" maxlength="40" autocomplete="off"></div>
    <p class="lbl">What is it?</p><div class="fwrap"><input class="field" id="tdesc" placeholder="A few words, for example: yellow book" maxlength="60" autocomplete="off"></div>
    <p class="lbl">Room</p><span class="chip"><img src="/web/icons/app/camera.png" alt="" style="width:20px">Work Room</span>
    <div class="bottom-bar"><button type="button" class="btn-p" data-act="save-thing" disabled>Save</button></div>`,
  { mount: (el) => { const n = el.querySelector('#tname'); n.addEventListener('input', () => { el.querySelector('[data-act="save-thing"]').disabled = !n.value.trim(); }); } });
}
async function saveThing(btn) {
  const name = $('tname').value.trim(), q = ($('tdesc').value.trim() || name).toLowerCase();
  if (!name) return;
  btn.disabled = true; btn.textContent = 'Saving…';
  try {
    const { id } = await api('/api/things', { method: 'POST', body: JSON.stringify({ name, description: q }) });
    await api(`/api/things/${encodeURIComponent(id)}/photos`, { method: 'POST', body: JSON.stringify({ photos_b64: pending.photos }) });
    await refresh();
    addedPage(id);
  } catch (e) { btn.disabled = false; btn.textContent = 'Save'; dialog('Could not save', e.message, [['OK', 'btn-p', null]]); }
}
/** The people a thing can belong to, the one added last first (the app proposes them). */
const ownersFor = () => state.things.filter(isPerson).sort((a, b) => b.created - a.created);
function addedPage(id) {
  if (ownersFor().length) { linkPage(id); return; }
  push(() => {
    const t = state.things.find((x) => x.id === id), fp = t?.fingerprint;
    return `<div class="step"><button type="button" class="ibtn x" data-act="finish" aria-label="Close">${I.x}</button>
      <div class="views-grid" style="width:100%;margin-bottom:22px">${(fp?.crops || []).slice(0, 8).map((c) => `<img src="${crop(c)}" alt="">`).join('')}</div>
      <h3>${esc(t?.name || 'Thing')} added</h3><p>The camera looks for it whenever something moves. Now tell the app what to do with it.</p></div>
    <div class="bottom-bar col"><button type="button" class="btn-p" data-act="new-scenario" data-id="${esc(id)}">Create a scenario</button>
      <button type="button" class="btn-s" data-act="finish">Not now</button></div>`;
  });
}
/** "Book added" with the question "Who does it belong to?": the family's faces, the person added last proposed. */
function linkPage(id) {
  const people = ownersFor(), pick = { id: people[0]?.id };
  const page = push(() => {
    const t = state.things.find((x) => x.id === id), fp = t?.fingerprint, sel = people.find((q) => q.id === pick.id) || people[0];
    return `<div class="step link-step"><button type="button" class="ibtn x" data-act="finish" aria-label="Close">${I.x}</button>
      <div class="views-grid" style="width:100%;margin-bottom:10px">${(fp?.crops || []).slice(0, 4).map((c) => `<img src="${crop(c)}" alt="">`).join('')}</div>
      <h3>${esc(t?.name || 'Thing')} added</h3><p>The camera looks for it whenever something moves.</p></div>
    <div class="reco-card link-card"><div class="reco-head">${ICON_LINK.replace('#fff', '#1d8f74')}<b>Who does it belong to?</b></div>
      <p>Link to ${esc(sel.name)}?</p>
      <div class="fam-row">${people.map((q) => `<button type="button" class="fam${q.id === sel.id ? ' on' : ''}" data-act="pick-owner" data-id="${esc(q.id)}"><img src="${crop(q.fingerprint?.crops?.[0] || '')}" alt=""><small>${esc(q.name)}</small></button>`).join('')}</div></div>
    <div class="bottom-bar col"><button type="button" class="btn-p" data-act="link-owner" data-id="${esc(id)}">Yes, link to ${esc(sel.name)}</button>
      <button type="button" class="btn-s" data-act="new-scenario" data-id="${esc(id)}">Not now</button></div>`;
  });
  page._pick = pick;
}
async function linkOwner(btn) {
  const tid = btn.dataset.id, owner = stack[stack.length - 1]?._pick?.id;
  btn.disabled = true;
  try {
    await api(`/api/things/${encodeURIComponent(tid)}/owner`, { method: 'POST', body: JSON.stringify({ owner }) });
    await refresh();
    ownedPage(tid);
  } catch (e) { btn.disabled = false; dialog('Could not link it', e.message, [['OK', 'btn-p', null]]); }
}
/** Linked: the thing and its person side by side, and a scenario about that person, ready to save. */
function ownedPage(id) {
  push(() => {
    const t = state.things.find((x) => x.id === id), o = ownerOf(t), name = (t?.name || 'thing').toLowerCase();
    const sentence = `Tell me if ${o?.name || 'they'} leaves home without the ${name}`;
    return `<div class="step"><button type="button" class="ibtn x" data-act="finish" aria-label="Close">${I.x}</button>
      <div class="owner-pair"><img src="${crop(thingPhoto(t) || '')}" alt=""><span class="owner-link">${ICON_LINK}</span><img class="round" src="${crop(o?.fingerprint?.crops?.[0] || '')}" alt=""></div>
      <h3>Belongs to ${esc(o?.name || '')}</h3><p>The ${esc(name)} is linked to ${esc(o?.name || '')}. Scenarios can now be about ${esc(o?.name || 'them')}.</p></div>
    <div class="reco-card sugg"><div class="reco-head">${I.sensor}<b>Suggested scenario</b></div>
      <p>${esc(sentence)}</p>
      <div class="reco-acts"><button type="button" class="btn-p" data-act="owned-scenario" data-id="${esc(id)}" data-text="${esc(sentence)}">Create</button><button type="button" class="btn-s" data-act="finish">Not now</button></div></div>`;
  });
}
const ICON_LINK = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>';
// ------------------------------------------------------------------ adding a person: a face video, or one photo of the face
/** Add › Person: how to show the app their face. A face video gives 8 views; one clear photo gives one. */
function personPickPage() {
  push(() => `<div class="step"><button type="button" class="ibtn x" data-act="back" aria-label="Close">${I.x}</button>
      <div class="method-art">${ICON_FACE}</div><h3>Add a person</h3>
      <p>Record a short video of their face, or use one clear photo of it, looking at the camera.</p></div>
    <input type="file" id="pphotoin" accept="image/*" hidden>
    <div class="bottom-bar col"><button type="button" class="btn-p" data-act="person-video">Record a face video</button>
      <button type="button" class="btn-s" data-act="person-photo" data-capture="user">Take a photo</button>
      <button type="button" class="btn-s" data-act="person-photo">Choose a photo</button></div>`,
  { mount: (el) => el.querySelector('#pphotoin').addEventListener('change', (e) => { if (e.target.files[0]) personPhotoPage(e.target.files[0]); }) });
}
// "Choose a photo" opens the phone's own photo picker; the app draws it as Android does (Photos / Albums, a grid of the
// recent pictures, a check on the one chosen, Add), over the pictures the server offers from data/picker (out of git).
// With none there, the browser's own file dialog opens instead.
async function photoPicker() {
  let photos = [];
  try { photos = (await (await fetch('/api/picker')).json()).photos || []; } catch { photos = []; }
  if (!photos.length) { const i = $('pphotoin'); i.removeAttribute('capture'); i.value = ''; i.click(); return; }
  const src = (p) => `/picker/${encodeURIComponent(p)}`;
  push(() => `<div class="pk"><div class="pk-top"><button type="button" class="pk-x" data-act="back" aria-label="Close">${I.x}</button>
      <div class="pk-tabs"><span class="on">Photos</span><span>Albums</span></div></div>
    <p class="pk-lbl">Recent</p>
    <div class="pk-grid">${photos.map((p) => `<button type="button" class="pk-ph" data-act="pick-photo" data-src="${src(p)}"><img src="${src(p)}" alt=""><i></i></button>`).join('')}</div>
    <div class="pk-bar"><span class="pk-n"></span><button type="button" class="pk-add" data-act="picker-add" disabled>Add</button></div></div>`);
}
async function personPhotoPage(file) {
  const bmp = await createImageBitmap(file), k = Math.min(1, 900 / Math.max(bmp.width, bmp.height));
  const c = Object.assign(document.createElement('canvas'), { width: Math.round(bmp.width * k), height: Math.round(bmp.height * k) });
  c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
  const url = c.toDataURL('image/jpeg', 0.92);
  push(() => `${phead('', '')}<div class="ptitle">New person</div><p class="psub">One photo of their face, looking at the camera.</p>
    <div class="person-shot"><img src="${url}" alt=""></div>
    <p class="lbl">Name</p><div class="fwrap"><input class="field" id="pname" placeholder="For example: Ana" maxlength="40" autocomplete="off" spellcheck="false"></div>
    <p class="lbl">Who is it?</p><div class="chips-row"><button type="button" class="chip on" data-act="rel" data-rel="family">Family</button><button type="button" class="chip" data-act="rel" data-rel="guest">Guest</button></div>
    <div class="bottom-bar"><button type="button" class="btn-p" data-act="save-person-photo" disabled>Save</button></div>`,
  { mount: (el) => { el._photo = url; const n = el.querySelector('#pname'); n.addEventListener('input', () => { el.querySelector('[data-act="save-person-photo"]').disabled = !n.value.trim(); }); } });
}
/** The photo goes to the server as a person's views; the home device's face step (faces.py) makes their template. */
async function savePersonPhoto(btn) {
  const pg = stack[stack.length - 1], name = $('pname').value.trim(), rel = pg.querySelector('.chip.on[data-rel]')?.dataset.rel || 'family';
  if (!name) return;
  btn.disabled = true; btn.textContent = 'Saving…';
  try {
    const { id } = await api('/api/things', { method: 'POST', body: JSON.stringify({ name, description: `person · ${rel}` }) });
    await api(`/api/things/${encodeURIComponent(id)}/photos`, { method: 'POST', body: JSON.stringify({ photos_b64: [pg._photo] }) });
    await refresh();
    push(() => {
      const t = state.things.find((x) => x.id === id), fp = t?.fingerprint;
      return `<div class="step"><button type="button" class="ibtn x" data-act="finish" aria-label="Close">${I.x}</button>
        <div class="person-added"><img src="${crop(fp?.crops?.[0] || '')}" alt=""><span class="ok">${ICON_CHECK}</span></div>
        <h3>${esc(t?.name || name)} added</h3><p>${esc(relationOf(t) || 'Person')} · ${fp?.faces ? 'face learnt from 1 photo' : 'no face found in the photo: it is kept as their picture only'}</p></div>
      <div class="bottom-bar"><button type="button" class="btn-p" data-act="finish">Done</button></div>`;
    });
  } catch (e) { btn.disabled = false; btn.textContent = 'Save'; dialog('Could not save', e.message, [['OK', 'btn-p', null]]); }
}
// ------------------------------------------------------------------ adding a person: views of the face from a short video
const ICON_FACE = '<svg viewBox="0 0 24 24" width="46" height="46" fill="none" stroke="#1a2233" stroke-width="1.6" stroke-linecap="round"><path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="10.2" r="3" stroke="#2abe9e" stroke-width="1.8"/><path d="M7.6 17.2a5.2 5.2 0 0 1 8.8 0" stroke="#2abe9e" stroke-width="1.8"/></svg>';
function personMethodPage() {
  Object.assign(pending, { name: '', q: 'person', photos: [], kind: 'person' });
  push(() => `${phead('', '')}<div class="ptitle">New person</div><p class="psub">Record a short video of their face, turning slowly from one side to the other.</p>
    <p class="lbl">Name</p><div class="fwrap"><input class="field" id="pname" placeholder="For example: Ana" maxlength="40" autocomplete="off"></div>
    <p class="lbl">Who is it?</p><div class="chips-row"><button type="button" class="chip on" data-act="rel" data-rel="family">Family</button><button type="button" class="chip" data-act="rel" data-rel="guest">Guest</button></div>
    <input type="file" id="facein" accept="video/*" hidden>
    <div class="bottom-bar"><button type="button" class="btn-p" data-act="record-face" disabled>Record their face</button></div>`,
  { mount: (el) => {
    const n = el.querySelector('#pname');
    n.addEventListener('input', () => { el.querySelector('[data-act="record-face"]').disabled = !n.value.trim(); });
    el.querySelector('#facein').addEventListener('change', (e) => { if (e.target.files[0]) savePersonVideo(e.target.files[0]); });
  } });
}
/** The face video goes to the server as it came; the screen follows the real upload and the server's work. */
async function savePersonVideo(file) {
  const name = $('pname').value.trim(), rel = document.querySelector('section.page:last-of-type .chip.on[data-rel]')?.dataset.rel || 'family';
  if (!name) return;
  const thumb = (await framesFromVideo(file, 1).catch(() => []))[0] || '';
  const prog = { p: 0, target: 0, step: 'Uploading the video' };
  const el = push(() => `<div class="step saving"><div class="ring-wrap"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="54" class="track"/><circle cx="60" cy="60" r="54" class="bar" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg>
      ${thumb ? `<img src="${thumb}" alt="">` : ''}<span class="ok">${ICON_CHECK}</span></div><h3>Saving ${esc(name)}'s face…</h3><p class="saving-step">Uploading the video</p></div>`);
  const bar = el.querySelector('.bar'), stepEl = el.querySelector('.saving-step'), t0 = performance.now();
  let raf;
  const tick = () => { prog.p += (prog.target - prog.p) * 0.12; bar.style.strokeDashoffset = String(100 - prog.p * 100); stepEl.textContent = prog.step; raf = requestAnimationFrame(tick); };
  tick();
  try {
    const { id } = await api('/api/things', { method: 'POST', body: JSON.stringify({ name, description: `person · ${rel}` }) });
    const b64 = await new Promise((ok) => { const r = new FileReader(); r.onload = () => ok(r.result); r.readAsDataURL(file); });
    const res = await new Promise((ok, no) => {
      const x = new XMLHttpRequest();
      x.open('POST', `/api/things/${encodeURIComponent(id)}/face-video`); x.setRequestHeader('Content-Type', 'application/json');
      x.upload.onprogress = (e) => { if (e.lengthComputable) prog.target = 0.6 * (e.loaded / e.total); };
      x.upload.onload = () => { prog.target = 0.65; prog.step = 'Finding the face in 8 views'; };
      x.onload = () => (x.status < 300 ? ok(JSON.parse(x.responseText)) : no(new Error(`Error ${x.status}`)));
      x.onerror = () => no(new Error('Network error'));
      x.send(JSON.stringify({ video_b64: b64 }));
    });
    prog.target = 1; prog.step = `${res.n} views from a ${Math.round(res.duration)} s video`;
    await new Promise((ok) => setTimeout(ok, Math.max(700, 2600 - (performance.now() - t0))));   // long enough to read; the work itself is real
    await new Promise((ok) => { const w = () => (prog.p > 0.996 ? ok() : requestAnimationFrame(w)); w(); });   // the ring closes
    cancelAnimationFrame(raf); bar.style.strokeDashoffset = '0';
    await refresh();
    personAdded(el, id, res);
  } catch (e) { cancelAnimationFrame(raf); pop(); dialog('Could not save', e.message, [['OK', 'btn-p', null]]); }
}
const ICON_SHIELD = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1d8f74" stroke-width="2" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.3 7.5 9.5 4.3-1.2 7.5-4.9 7.5-9.5V6Z"/><path d="m8.8 12.2 2.3 2.3 4.3-4.6" stroke-linecap="round"/></svg>';
const familyOf = () => state.things.filter((t) => isPerson(t) && relationOf(t) === 'Family');
/** The saving screen becomes the "added" screen in place: the closed ring stays as the face's border, the check badge
 * pops in, and each line of text fades out before its new words fade in (never two texts at once). */
function personAdded(el, id, res) {
  const t = state.things.find((x) => x.id === id), fp = t?.fingerprint;
  const step = el.querySelector('.step.saving'), h3 = step.querySelector('h3'), p = step.querySelector('.saving-step');
  const hasSecurity = state.rules.some((r) => r.unknown);
  const swap = (node, text) => { node.style.opacity = '0'; setTimeout(() => { node.textContent = text; node.style.opacity = '1'; }, 170); };
  step.classList.add('done');
  setTimeout(() => {
    swap(h3, `${t?.name || 'Person'} added`);
    swap(p, `${relationOf(t) || 'Person'} · ${fp?.n || res?.n || 0} views from a ${Math.round(fp?.duration || res?.duration || 0)} s video`);
  }, 140);
  setTimeout(() => {
    step.classList.add('added-person');
    el.insertAdjacentHTML('beforeend', `<div class="bottom-bar fade-in">${hasSecurity ? '<button type="button" class="btn-p" data-act="finish">Done</button>'
      : '<button type="button" class="btn-p" data-act="person-next">Continue</button>'}</div>`);
  }, 560);
}
/** The app's suggestion after a person is added, on its own page (as New scenario): the family's faces and one rule. */
function suggestionPage() {
  const fam = familyOf();
  push(() => `${phead('', '')}<div class="ptitle">Suggested scenario</div><p class="psub">Based on the people you added.</p>
    <div class="reco-card sugg"><div class="reco-head">${ICON_SHIELD}<b>Home security</b></div>
      <p>Sound the alarm when someone who isn't Family comes in?</p>
      <div class="fam-row">${fam.map((q) => `<span class="fam"><img src="${crop(q.fingerprint?.crops?.[0] || '')}" alt=""><small>${esc(q.name)}</small></span>`).join('')}</div>
      <div class="reco-acts"><button type="button" class="btn-p" data-act="security-on">Turn on</button><button type="button" class="btn-s" data-act="finish">Not now</button></div></div>`);
}
/** The app's own suggestion: one sentence, compiled as any other into a rule, with its own title. */
async function securityOn(btn) {
  btn.disabled = true; btn.textContent = 'Turning on…';
  ui.scenBack = 0;   // Done goes back to Things
  try {
    const r = await api('/api/rules', { method: 'POST', body: JSON.stringify({ sentence: "Sound the alarm when someone who isn't Family comes in", title: 'Home Security' }) });
    await refresh();
    savedPage(r);
  } catch (e) { btn.disabled = false; btn.textContent = 'Turn on'; dialog('Could not turn it on', e.message, [['OK', 'btn-p', null]]); }
}
function scenarioPage(id, text = '') {
  const t = state.things.find((x) => x.id === id), photo = t?.fingerprint?.crops?.[0];
  const back = t ? 0 : stack.length;   // a scenario without a thing (Menu › Scenarios): Done returns to that list
  const page = push(() => `${phead('', '')}<div class="ptitle">New scenario</div><p class="psub">Say what should happen, in one sentence.</p>
    ${t ? `<div class="scen-thing">${photo ? `<img src="${crop(photo)}" alt="">` : ''}<span><b>${esc(t.name)}</b><small>${isPerson(t) ? relationOf(t) || 'Person' : 'Work Room'}</small></span></div>` : ''}
    <div class="fwrap"><textarea class="field" id="scentext" rows="1" placeholder="${t ? 'For example: tell me if I leave without it' : 'For example: if nobody is home, tell me'}" maxlength="300">${esc(text)}</textarea></div>
    <div class="bottom-bar"><button type="button" class="btn-p" data-act="save-scenario" disabled>Save</button></div>`,
  { mount: (el) => {
    const f = el.querySelector('#scentext'), b = el.querySelector('[data-act="save-scenario"]');
    const grow = () => { f.style.height = 'auto'; f.style.height = `${Math.min(f.scrollHeight, 170)}px`; b.disabled = !f.value.trim(); };
    f.addEventListener('input', grow); grow();
  } });
  page._back = back;
}
async function saveScenario(btn) {
  const text = $('scentext').value.trim();
  if (!text) return;
  btn.disabled = true; btn.textContent = 'Saving…';
  try {
    const r = await api('/api/rules', { method: 'POST', body: JSON.stringify({ sentence: text }) });
    ui.scenBack = stack[stack.length - 1]?._back || 0;
    await refresh();
    savedPage(r);
  } catch (e) { btn.disabled = false; btn.textContent = 'Save'; dialog('Could not save', e.message, [['OK', 'btn-p', null]]); }
}
function savedPage(r) {
  const t = state.things.find((x) => x.id === r.thing_id);
  const then = r.kind === 'nobody_devices_on' ? ['Ask you to turn them off'] : r.unknown || r.kind === 'door_open_nobody' ? [r.alarm ? 'Sound the alarm' : '', 'Send you a message'].filter(Boolean) : ['Send you a message', r.alarm ? 'Sound the alarm' : '', /^light_/.test(r.action || '') ? `Turn the light ${r.action.slice(6)}` : '',
    r.action === 'plug_off' ? 'Switch the plug off' : ''].filter(Boolean);
  const when = r.kind === 'nobody_devices_on' ? 'Nobody is home and something is still on' : r.kind === 'door_open_nobody' ? 'The door is left open and nobody is home' : r.unknown ? 'Someone not in Family is seen at home' : r.kind === 'leave_without' ? `You leave home and the ${(t?.name || 'thing').toLowerCase()} stays` : r.sentence;
  push(() => `<div class="step"><button type="button" class="ibtn x" data-act="finish" aria-label="Close">${I.x}</button>
      <div class="saved-ok">${ICON_CHECK}</div><h3>Scenario saved</h3><p>It is on from now. You can change it in Menu&nbsp;›&nbsp;Scenarios.</p></div>
    <div class="scen-card"><div class="scen-title">${I.sensor}<b>${esc(r.title)}</b><span class="on">Active</span></div>
      <div class="scen-row"><small>When</small><span>${esc(when)}</span></div>
      <div class="scen-row"><small>Then</small><span>${then.map(esc).join('<br>')}</span></div></div>
    <div class="bottom-bar"><button type="button" class="btn-p" data-act="finish">Done</button></div>`);
}
async function startRegister(name, q) {
  try {
    const { id } = await api('/api/things', { method: 'POST', body: JSON.stringify({ name, description: q }) });
    await api(`/api/things/${encodeURIComponent(id)}/enrol`, { method: 'POST' });
    await refresh();
    registerPage(id);
  } catch (e) {
    dialog('The camera is not ready', /not running/.test(e.message) ? 'The camera service is not running. Start it and try again.' : e.message, [['OK', 'btn-p', null]]);
  }
}
/** "Where is my wallet?", "Where are my keys?": plural names (keys, glasses) take "are". */
const whereIs = (n) => `Where ${/s$/.test(n) ? "are" : "is"} my ${n}?`;
function registerPage(id) {
  const el = push(() => {
    const t = state.things.find((x) => x.id === id);
    const name = t?.name || 'thing', en = state.enrol && state.enrol.thing_id === id ? state.enrol : null;
    if (t?.fingerprint) {
      return `<div class="step"><button type="button" class="ibtn x" data-act="finish" aria-label="Close">${I.x}</button>
        <div class="views-grid" style="width:100%;margin-bottom:22px">${t.fingerprint.crops.slice(0, 8).map((c) => `<img src="${crop(c)}" alt="">`).join('')}</div>
        <h3>${esc(name)} added</h3><p>ThingTracker learnt it from ${t.fingerprint.n} views. From now on, the camera finds it whenever something moves, and you can ask “${esc(whereIs(name.toLowerCase()))}”.</p></div>
        <div class="bottom-bar"><button type="button" class="btn-p" data-act="finish">Done</button></div>`;
    }
    const got = en?.got || 0, target = en?.target || 8, failed = !en;
    return `<div class="step"><button type="button" class="ibtn x" data-act="cancel-register" aria-label="Close">${I.x}</button>
      <div class="livebox"><img src="/api/kit/stream.mjpg?t=reg" alt="Live view from the camera"><div class="boxes lbox" style="position:absolute;inset:0"></div></div>
      <h3>Show the ${esc(name.toLowerCase())} to the camera</h3>
      <p>${failed ? 'The camera did not see it well enough. Hold it closer, in good light, and try again.' : 'Hold it about 50 cm from the camera and turn it slowly, so it sees the front, the back and the sides.'}</p>
      <div class="progress"><i style="width:${(got / target) * 100}%"></i></div><p class="count">${got} of ${target} views</p></div>
      <div class="bottom-bar">${failed ? '<button type="button" class="btn-p" data-act="retry-register">Try again</button>' : '<button type="button" class="btn-p" disabled>Next</button>'}</div>`;
  }, { live: true });
  el.dataset.id = id;
}
const ADD_ONLY = ['light', 'motion-sensor', 'outdoor-siren', 'power-strip', 'remote-controller', 'smart-fibergateway', 'indoor-siren'];
const addIcon = (n) => `/web/icons/app/${ADD_ONLY.includes(n) ? 'add-' + n : n}.png`;
function addDevicePage() {
  const L = [['Camera', 'camera'], ['Contact Sensor', 'contact-sensor'], ['Indoor Siren', 'indoor-siren'], ['Light', 'light'], ['Motion Sensor', 'motion-sensor'],
    ['Outdoor Siren', 'outdoor-siren'], ['Plug', 'plug'], ['Power Strip', 'power-strip'], ['Remote Controller', 'remote-controller'], ['Security Hub', 'security-hub'],
    ['Smart Fibergateway', 'smart-fibergateway'], ['Smoke Sensor', 'smoke-sensor'], ['Temperature Sensor', 'temperature-sensor']];
  const M = [['Temperature Sensor', 'temperature-sensor'], ['Plug', 'plug'], ['Motion Sensor', 'motion-sensor'], ['Light', 'light'], ['Temperature Sensor', 'temperature-sensor'],
    ['Plug', 'plug'], ['Contact Sensor', 'contact-sensor']];
  push(() => `${phead('', '')}<div class="ptitle">Add device</div><p class="psub">Select the device you want to install.</p>
    <div class="looking"><b><span class="pulse"></span>Looking for nearby Matter devices...</b><p>Make sure your device is in pairing mode. Devices will appear here automatically when detected.</p></div>
    <p class="lbl">Works with:</p><span class="chip">${I.matter}Matter</span><p class="lbl">Available devices (20)</p>
    <ul class="alist">${L.map(([n, ic]) => `<li><button type="button" class="aitem" data-act="${n === 'Camera' ? 'install-camera' : 'stub'}" data-title="${esc(n)}"><img src="${addIcon(ic)}" alt=""><span>${esc(n)}</span><span></span></button></li>`).join('')}
      ${M.map(([n, ic]) => `<li><button type="button" class="aitem" data-act="stub" data-title="${esc(n)}"><img src="${addIcon(ic)}" alt=""><span>${esc(n)}</span><small>${I.matter.replace('<svg', '<svg width="14" height="14"')}matter</small></button></li>`).join('')}</ul>`);
}
function installCameraPage() {
  push(() => `<div class="step"><button type="button" class="ibtn x" data-act="cancel-install" aria-label="Close">${I.x}</button>
    <img class="art" src="/web/icons/app/camera.png" alt=""><h3>Install your camera</h3>
    <p>Insert the serial number of your Camera manually or by scanning the label on the device.</p>
    <input class="field" placeholder="Insert the serial number" autocomplete="off"><div class="or">or</div>
    <button type="button" class="btn-s" style="width:100%;height:52px" data-act="stub" data-title="Scan label">Scan label</button></div>
    <div class="bottom-bar"><button type="button" class="btn-p" disabled>Next</button></div>`);
}
const REAL_SCENARIOS = ['Test Motion', 'Turn Off Camera', 'Detect-motion', 'test_alarm', 'Work'];
function scenariosPage() {
  push(() => `${phead('', '', `<button type="button" class="ibtn" data-act="stub" data-title="Filter" aria-label="Filter">${I.filter}</button><button type="button" class="ibtn" data-act="stub" data-title="Search" aria-label="Search">${I.search}</button>`)}
    <div class="ptitle">Scenarios</div>
    ${state.rules.map((r) => `<div class="scard">${I.sensor}<span><div class="nm">${esc(r.title)}</div><div class="st ${r.active ? '' : 'grey'}">${r.active ? 'Active' : 'Paused'} · ThingTracker</div></span><span class="play">${I.play}</span></div>`).join('')}
    ${REAL_SCENARIOS.map((n) => `<div class="scard">${I.wandC}<span><div class="nm">${esc(n)}</div><div class="st">Active</div></span><span class="play">${I.play}</span></div>`).join('')}
    <div class="bottom-bar"><button type="button" class="btn-p" data-act="new-scenario">Add scenario</button></div>`, { live: true });
}
function roomsPage() {
  push(() => `${phead('', '', `<button type="button" class="ibtn" data-act="stub" data-title="Sort" aria-label="Sort">${I.sort}</button><button type="button" class="ibtn" data-act="stub" data-title="Search" aria-label="Search">${I.search}</button>`)}
    <div class="ptitle">Rooms</div>${(state.home?.rooms || []).map((r) => `<div class="scard" style="height:64px"><img src="/web/icons/app/camera.png" alt="" style="width:26px"><span><div class="nm">${esc(r.name)}</div>
    <div class="st grey">${(state.home?.devices || []).filter((d) => d.room_id === r.id).length} device</div></span><span></span></div>`).join('')}
    <div class="bottom-bar" style="margin-top:420px"><button type="button" class="btn-p" data-act="stub" data-title="Add room">Add room</button></div>`);
}
function notificationsPage() {
  push(() => {
    const list = notes();
    return `${phead('', '', `<button type="button" class="ibtn" data-act="stub" data-title="Filter" aria-label="Filter">${I.filter}</button>`)}<div class="ptitle">Notifications</div>
      <div class="unread-h"><b>Unread (${unreadCount()})</b><span data-act="mark-read" role="button" style="cursor:pointer">Mark all as read</span></div>
      ${list.length ? '' : '<div class="empty"><p>No notifications yet.</p></div>'}
      ${list.map((e) => { const thing = e.kind === 'alert'; return `<div class="nrow ${ui.read.has(e.id) ? 'read' : ''}" ${thing ? `data-act="open-alert" data-id="${esc(e.id)}" role="button" style="cursor:pointer"` : ''}><span>${I.bellC}</span><span><b>${esc(thing ? e.title || 'ThingTracker' : e.device || 'Device')}</b><small>${esc(e.text)} · ${ago(e.ts)}</small>
        ${e.crop || e.picture ? `<img class="crop" src="${crop(e.crop || e.picture)}" alt="">` : ''}<span class="tag">${thing ? 'Things' : 'Device'}</span></span>${I.chevR}</div>`; }).join('')}`;
  }, { live: true });
}
/** An alert, opened from its notification: the camera's picture, large, what happened and when, and the alarm's state. */
/** A small beacon (blue and red halves on a dark base, light rays): an original drawing, no force's badge or logo. */
const ICON_BEACON = '<svg viewBox="0 0 40 40" width="40" height="40"><path d="M11 28V19a9 9 0 0 1 18 0v9Z" fill="#2563EB"/><path d="M20 10a9 9 0 0 1 9 9v9h-9Z" fill="#DC2626"/><rect x="8" y="28" width="24" height="5" rx="2" fill="#1a2233"/><path d="M20 3.5v3M7.5 8.5l2 2M32.5 8.5l-2 2M3.5 19h3M33.5 19h3" stroke="#1a2233" stroke-width="2.2" stroke-linecap="round"/></svg>';
const ICON_LIGHT = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#b7791f" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.4 1.1 2.2h5c0-.8.4-1.6 1.1-2.2A6 6 0 0 0 12 3Z" fill="#fde68a"/></svg>';
const ICON_AC = '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="8" rx="2" fill="#dbeafe"/><path d="M7 10h10M8 16l-1 3M12 16v3M16 16l1 3"/></svg>';
// the same icon wherever a device appears: the Altice app's own plug image for the kit's plug, the AC's for the integration
function ttIcon(d) { return d.type === 'plug' || d.sim ? `<img src="${devImg(d.type)}" alt="">` : ICON_AC; }
const askFor = (d) => (d.type === 'ac' ? 'Turn off the AC?' : /light/i.test(d.powers || '') ? 'Turn off the lights?' : `Turn off ${d.powers || d.name}?`);
/** The alert as the server keeps it now: its cards and alarm change when the user answers (server.py: /api/alerts). */
const alertNow = (e) => (state.events || []).find((x) => x.id === e.id) || e;
/** An alarm in the alert: {state, text, off_at} from the server, or the older plain text. */
const alarmOf = (e) => (!e.alarm ? null : typeof e.alarm === 'string' ? { state: e.alarmOff ? 'off' : 'on', text: e.alarm, off_at: e.alarmOff } : e.alarm);
function cardRows(e) {
  const cards = e.cards || (e.devices || []).map((id) => ({ device: id, state: ttOf(id)?.on === false ? 'off' : 'on' }));
  const rows = cards.map((c) => {
    const d = ttOf(c.device) || { id: c.device, name: c.name || c.device, type: c.kind };
    const off = c.state === 'off';
    return `<div class="dev-ask${off ? ' done' : ''}"><span class="dic">${ttIcon(d)}</span><span><b>${esc(c.label || askFor(d))}</b><small>${esc(d.name)} · ${off ? 'Off' : 'On'}</small></span>
      ${off ? '<span class="dev-off">Off ✓</span>' : `<button type="button" class="btn-p" data-act="alert-device" data-id="${esc(c.device)}">Yes</button>`}</div>`;
  });
  for (const a of e.ask || []) {
    const done = a.state === 'done';
    rows.push(`<div class="dev-ask${done ? ' done' : ''}"><span class="dic">${ICON_BEACON.replace('width="40" height="40"', 'width="30" height="30"')}</span><span><b>${esc(a.label)}</b><small>${done ? 'Alarm on (simulated)' : 'The alarm stays off until you say yes'}</small></span>
      ${done ? '<span class="dev-off">Done ✓</span>' : `<button type="button" class="btn-p" data-act="alert-ask" data-id="${esc(a.act)}">Yes</button>`}</div>`);
  }
  return rows.length ? `<div class="dev-asks">${rows.join('')}</div>` : '';
}
/** An alert, opened from its notification: the camera's picture, what happened and when, then what the app can do:
 * turn devices off, sound or stop the (simulated) alarm, the door's state, and the police suggestion (never dials). */
function alertPage(e0) {
  document.body.classList.add('alert-open');
  const page = push(() => {
    const e = alertNow(e0), alarm = alarmOf(e), door = e.door || (e.doorAlarm ? { open: true, text: 'The door is open and nobody is home.' } : null);
    const sugg = e.suggestion || (e.unknown && !e.cards ? { kind: 'police', title: 'Possible intrusion', text: 'An unknown person came in and took something. We recommend calling the police.', number: '112' } : null);
    const pic = e.picture || e.snapshot || e.crop, cam = e.room || e.camera, where = cam ? `${cam} camera` : e.place || 'Camera';
    const alarmOn = alarm && alarm.state !== 'off';
    const offBtn = alarmOn ? `<button type="button" class="btn-s small" data-act="alarm-off">Turn off the alarm</button>` : '';
    const banner = door
      ? (alarm ? (alarmOn ? `<div class="alert-alarm door"><span class="dot"></span><b>Door open · Alarm on</b><small>${esc(door.text)}</small>${offBtn}</div>`
        : `<div class="alert-alarm door off"><span class="dot"></span><b>Door open · Alarm off</b><small>Turned off from the app at ${hm(alarm.off_at || Date.now() / 1000)}.</small></div>`)
        : `<div class="alert-alarm door"><span class="dot"></span><b>Door open</b><small>${esc(door.text)}</small></div>`)
      : alarm ? (alarmOn ? `<div class="alert-alarm"><span class="dot"></span><b>Alarm on</b><small>${esc(alarm.text)}</small></div>`
        : `<div class="alert-alarm off"><span class="dot"></span><b>Alarm off</b><small>Turned off from the app at ${hm(alarm.off_at || Date.now() / 1000)}.</small></div>`) : '';
    const reco = sugg ? `<div class="alert-reco"><span class="beacon">${ICON_BEACON}</span><span><b>${esc(sugg.title)}</b><small>${esc(sugg.text)}</small></span></div>` : '';
    const acts = [sugg ? `<button type="button" class="btn-p police" data-act="call-police">Call the police (${esc(sugg.number || '112')})</button>` : '',
      alarmOn && !door ? `<button type="button" class="${sugg ? 'btn-s' : 'btn-p danger'}" data-act="alarm-off">Turn off the alarm</button>` : '',
      '<button type="button" class="btn-s" data-act="stub" data-title="Open the camera">Open the camera</button>'].filter(Boolean);
    return `${phead('', '')}<div class="ptitle">${esc(e.title || 'Alert')}</div>
    <div class="alert-shot">${pic ? `<img src="${crop(pic)}" alt="What the camera saw">` : ''}<span class="when">${hm(e.ts)} · ${esc(where)}</span></div>
    <p class="alert-text">${esc(e.text || '')}</p>
    ${cardRows(e)}${banner}${reco}
    <div class="bottom-bar alert-actions${acts.length === 3 ? ' three' : ''}">${acts.join('')}</div>`;
  }, { live: true });
  page._alert = e0;
}
function integrationPage(id) {
  push(() => {
    const d = ttOf(id) || {};
    return `${phead(d.name || 'Device', d.room || '')}<div class="hero sim"><span class="sim-ic">${ttIcon(d)}</span><span class="st ${d.on ? '' : 'grey'}">${d.on ? 'On' : 'Off'}</span></div>
      <p class="sim-note">Connected to the app directly, as a third-party integration. It is not part of the Altice kit. In this prototype it is simulated: the app keeps its state and sends nothing to the device.</p>
      <div class="bottom-bar"><button type="button" class="btn-p" data-act="tt-toggle" data-id="${esc(d.id)}">${d.on ? 'Turn off' : 'Turn on'}</button></div>`;
  }, { live: true });
}
function settingsPage() {
  push(() => `${phead('', '')}<div class="ptitle">Settings</div><h3 class="gtitle">Notifications</h3><div class="group">${row(I.bell, 'Type of notifications', 'stub')}</div>
    <h3 class="gtitle">App</h3><div class="group"><div class="row">${I.user}<span>App authentication</span><span class="toggle"></span></div>${row('<span></span>', 'Access code', 'stub')}
      <div class="row"><span></span><span>Biometrics</span><span class="toggle"></span></div></div>
    <h3 class="gtitle">General options</h3><div class="group">${row(I.home, 'Language', 'stub')}${row(I.sort, 'Units', 'stub')}</div>`);
}
function favPickerPage() {
  push(() => `${phead('Favorites', '')}<p class="psub" style="margin-top:6px">Tap the star of what you use most.</p>
    <ul class="cards">${(state.home?.devices || []).map((d) => `<li><button type="button" class="card" data-act="fav" data-id="${esc(d.id)}"><span class="ic"><img src="${devImg(d.type)}" alt=""></span>
      <span><span class="nm">${esc(d.name)}</span><span class="st ${statusCls(d.status)}">${esc(d.status)}</span></span><span style="width:22px">${ui.favs.has(d.id) ? I.starOn : I.star}</span></button></li>`).join('')}</ul>`, { live: true });
}

// ------------------------------------------------------------------ sheets and dialogs
function openSheet(html, mount) {
  const sh = $('sheet');
  $('dim').hidden = false; sh.hidden = false; sh.classList.remove('closing');
  sh.innerHTML = `<div><div class="handle"></div>${html.head}</div><div class="sbody">${html.body}</div>${html.foot ? `<div class="sfoot">${html.foot}</div>` : '<div></div>'}`;
  mount?.(sh);
}
function closeSheet() {
  const sh = $('sheet');
  if (sh.hidden) return;
  sh.classList.add('closing');
  setTimeout(() => { sh.hidden = true; $('dim').hidden = true; sh.classList.remove('closing'); }, 220);
}
function filterSheet() {
  const draft = { sort: ui.sort, types: new Set(ui.types) };
  const T = [['camera', 'Camera'], ['contactSensor', 'Contact Sensor'], ['plug', 'Energy Meter'], ['bulb', 'Light'], ['gateway', 'Security Hub'], ['smokeSensor', 'Smoke Sensor'], ['temperatureSensor', 'Temperature Sensor'],
    ['tv', 'TV'], ['heater', 'Heater'], ['lock', 'Lock'], ['leakSensor', 'Leak Sensor'], ['motionSensor', 'Motion Sensor']].filter(([k]) => (state.home?.devices || []).some((d) => d.type === k));
  const body = () => `<p class="sh">Sort by</p>${[['az', 'A - Z (default)'], ['za', 'Z - A']].map(([k, l]) => `<div class="opt" data-sort="${k}"><span class="radio ${draft.sort === k ? 'on' : ''}"></span>${l}</div>`).join('')}
    <div class="sline"></div><p class="sh">Filter by</p><p class="sh" style="font-size:14px">Device</p>
    ${T.map(([k, l]) => `<div class="opt" data-type="${k}"><span class="check ${draft.types.has(k) ? 'on' : ''}"></span>${l}</div>`).join('')}`;
  openSheet({ head: `<div class="shead"><b>Sort &amp; Filter</b><button type="button" class="ibtn" data-act="close-sheet" aria-label="Close">${I.x}</button></div>`, body: body(),
    foot: '<button type="button" class="btn-s" style="flex:1;height:50px" data-act="filter-clear">Clear</button><button type="button" class="btn-p" style="flex:1;height:50px" data-act="filter-apply">Apply</button>' },
  (sh) => {
    sh._draft = draft;
    sh.querySelector('.sbody').addEventListener('click', (e) => {
      const s = e.target.closest('[data-sort]'), t = e.target.closest('[data-type]');
      if (s) draft.sort = s.dataset.sort;
      if (t) { if (draft.types.has(t.dataset.type)) draft.types.delete(t.dataset.type); else draft.types.add(t.dataset.type); }
      if (s || t) sh.querySelector('.sbody').innerHTML = body();
    });
  });
}
function chatHtml() {
  return `<div class="msgs">${chat.map((m) => {
    if (m.typing) return '<div class="msg bot"><span class="typing"><i></i><i></i><i></i></span></div>';
    if (m.me) return `<div class="msg me">${esc(m.text)}</div>`;
    return `<div class="msg bot">${esc(m.text)}${m.html || ''}</div>`;
  }).join('')}</div>`;
}
function openAssistant(prefill = '') {
  if (!chat.length) {
    const n = (state.things[0]?.name || 'keys').toLowerCase();     // the examples use a thing the home really has
    chat.push({ text: 'Hi! Ask me anything about your home, like where you left something, or describe a sensor in one sentence.',
      html: `<div class="suggest">${[whereIs(n), `Tell me if I leave home without my ${n}`, 'What did the camera see today?'].map((s) => `<button type="button" data-ask="${esc(s)}">${esc(s)}</button>`).join('')}</div>` });
  }
  openSheet({ head: `<div class="shead"><b>Assistant</b><button type="button" class="ibtn" data-act="close-sheet" aria-label="Close">${I.x}</button></div>`, body: chatHtml(),
    foot: `<textarea class="field" id="askfield" rows="1" placeholder="Ask anything" maxlength="300" autocomplete="off">${esc(prefill)}</textarea><button type="button" class="send" data-act="send" aria-label="Send">${I.send}</button>` },
  (sh) => {
    const f = sh.querySelector('#askfield');
    const grow = () => { f.style.height = 'auto'; f.style.height = `${Math.min(f.scrollHeight, 124)}px`; };
    f.addEventListener('input', grow); grow();
    f.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(f.value); } });
    sh.querySelector('.sbody').addEventListener('click', (e) => { const b = e.target.closest('[data-ask]'); if (b) ask(b.dataset.ask); });
    scrollChat(); setTimeout(() => f.focus(), 340);
  });
}
function scrollChat() { const b = document.querySelector('#sheet .sbody'); if (b) { b.innerHTML = chatHtml(); b.scrollTop = b.scrollHeight; } }
async function ask(text) {
  text = String(text || '').trim();
  const f = $('askfield'); if (f) { f.value = ''; f.dispatchEvent(new Event('input')); }
  if (!text) return;
  chat.push({ me: true, text }); chat.push({ typing: true }); scrollChat();
  let reply;
  try {
    const r = await api('/api/assistant', { method: 'POST', body: JSON.stringify({ text }) });
    if (r.kind === 'sensor') {
      reply = { text: 'Done. I created a sensor; it is also in Menu > Scenarios.',
        html: `<ul class="cards" style="padding:0"><li><div class="card"><span class="ic">${I.sensor}</span><span><span class="nm">${esc(r.sensor.title)}</span><span class="st">Active</span></span><span></span></div></li></ul>` };
    } else {
      const cards = r.candidates?.length ? r.candidates.map((t) => thingCard(t, 'ask-about')).join('') : r.thing ? thingCard(r.thing) : '';
      reply = { text: r.answer, html: cards ? `<ul class="cards" style="padding:0">${cards}</ul>` : '' };
    }
  } catch (e) { reply = { text: e.message }; }
  chat.pop(); chat.push(reply); scrollChat(); refresh();
}
function dialog(title, text, actions) {
  const d = $('dialog');
  d.innerHTML = `<h3>${esc(title)}</h3><p>${esc(text)}</p><div class="acts">${actions.map(([l, cls], i) => `<button type="button" class="${cls}" data-i="${i}">${esc(l)}</button>`).join('')}</div>`;
  d.hidden = false; $('dim').hidden = false;
  d.onclick = (e) => {
    const b = e.target.closest('[data-i]'); if (!b) return;
    d.hidden = true; if ($('sheet').hidden) $('dim').hidden = true;
    actions[+b.dataset.i][2]?.();
  };
}
let toastTimer;
function toast(title, text, img, ev) {
  const t = $('toast');
  t._event = ev || null;
  t.onclick = () => { if (t._event) { t.classList.remove('show'); t.hidden = true; alertPage(t._event); } };
  t.style.cursor = ev ? 'pointer' : '';
  t.innerHTML = `${img ? `<img src="${crop(img)}" alt="">` : '<svg style="--a:#2abe9e;--i:#1a2233"><use href="#mark"/></svg>'}<div><b>Altice Home · ${esc(title)}</b>${esc(text)}</div>`;
  t.hidden = false; requestAnimationFrame(() => t.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.classList.remove('show'); setTimeout(() => { t.hidden = true; }, 320); }, 4500);
}

// ------------------------------------------------------------------ every tap in the app goes through here
device.addEventListener('click', async (e) => {
  const tabBtn = e.target.closest('#tabs button');
  if (tabBtn) { while (stack.length) pop(); setTab(tabBtn.dataset.tab); return; }
  if (e.target.closest('#fab')) { openAssistant(); return; }
  if (e.target.id === 'dim') { if ($('dialog').hidden) closeSheet(); return; }
  const el = e.target.closest('[data-act]'); if (!el) return;
  const act = el.dataset.act, id = el.dataset.id;
  const topId = () => stack[stack.length - 1]?.dataset.id;
  switch (act) {
    case 'back': pop(); break;
    case 'sec': if (ui.closed.has(el.dataset.key)) ui.closed.delete(el.dataset.key); else ui.closed.add(el.dataset.key); el.classList.toggle('closed'); break;
    case 'search-devices': case 'search-things': {
      const k = act.split('-')[1]; ui.search[k] = !ui.search[k]; if (!ui.search[k]) ui.q[k] = '';
      renderTab(ui.tab); if (ui.search[k]) $('v-' + ui.tab).querySelector('[data-search]')?.focus(); break;
    }
    case 'filter': filterSheet(); break;
    case 'filter-apply': { const d = $('sheet')._draft; ui.sort = d.sort; ui.types = d.types; closeSheet(); renderTab(ui.tab); break; }
    case 'filter-clear': ui.sort = 'az'; ui.types = new Set(); closeSheet(); renderTab(ui.tab); break;
    case 'close-sheet': closeSheet(); break;
    case 'device': devicePage(id); break;
    case 'fav': if (ui.favs.has(id)) ui.favs.delete(id); else ui.favs.add(id); store.set('tt-favs', [...ui.favs]); refreshPage(); break;
    case 'fav-pick': favPickerPage(); break;
    case 'area': ui.area = id; renderAreas(); break;
    case 'add-device': addDevicePage(); break;
    case 'install-camera': installCameraPage(); break;
    case 'cancel-install': dialog('Cancel installation', 'Do you want to cancel the installation?', [['No, continue', 'btn-s', null], ['Yes, cancel', 'btn-p', () => pop()]]); break;
    case 'scenarios': scenariosPage(); break;
    case 'rooms': roomsPage(); break;
    case 'notifications': notificationsPage(); break;
    case 'open-alert': { const ev = (state.events || []).find((x) => String(x.id) === el.dataset.id); if (ev) alertPage(ev); break; }
    case 'settings': settingsPage(); break;
    case 'mark-read': notes().forEach((x) => ui.read.add(x.id)); store.set('tt-read', [...ui.read]); refreshPage(); renderTabs(); break;
    case 'stub': stub(el.dataset.title || el.textContent.trim()); break;
    case 'assistant': openAssistant(); break;
    case 'send': ask($('askfield')?.value); break;
    case 'thing': closeSheet(); thingPage(id); break;
    case 'ask-about': { const t = state.things.find((x) => x.id === id); ask(whereIs(t ? t.name.toLowerCase() : 'thing')); break; }
    case 'sightings': sightingsPage(topId()); break;
    case 'add-thing': addThingPage(); break;
    case 'pick-thing': if (el.dataset.q === 'person') personPickPage(); else methodPage(el.dataset.name, el.dataset.q); break;
    case 'person-video': pop(); personMethodPage(); break;
    case 'person-photo': { const i = $('pphotoin'); if (el.dataset.capture) { i.setAttribute('capture', el.dataset.capture); i.value = ''; i.click(); } else photoPicker(); break; }
    case 'pick-photo': { const g = el.closest('.pk'); g.querySelectorAll('.pk-ph.sel').forEach((x) => x !== el && x.classList.remove('sel')); el.classList.toggle('sel');
      const n = g.querySelectorAll('.pk-ph.sel').length; g.querySelector('.pk-add').disabled = !n; g.querySelector('.pk-n').textContent = n ? '1 selected' : ''; break; }
    case 'picker-add': { const s = el.closest('.pk').querySelector('.pk-ph.sel'); if (!s) break; el.disabled = true;
      const b = await (await fetch(s.dataset.src)).blob(); pop(); personPhotoPage(new File([b], 'photo.jpg', { type: b.type })); break; }
    case 'save-person-photo': savePersonPhoto(el); break;
    case 'pick-owner': { const pg = el.closest('section.page'); if (pg?._pick) { pg._pick.id = el.dataset.id; pg.innerHTML = pg._render(); } break; }
    case 'link-owner': linkOwner(el); break;
    case 'owned-scenario': scenarioPage(el.dataset.id, el.dataset.text); break;
    case 'person-next': suggestionPage(); break;
    case 'security-on': securityOn(el); break;
    case 'record-face': $('facein')?.click(); break;
    case 'rel': el.parentElement.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === el)); break;
    // the prototype never dials: it only asks, as a real phone would before a call
    case 'call-police': dialog('Call 112?', 'The phone would call the emergency number. The prototype does not dial.', [['Cancel', 'btn-s', null], ['Call', 'btn-p police', null]]); break;
    case 'take-photos': $('photoin')?.click(); break;
    case 'pick-camera': pop(); startRegister(pending.name, pending.q); break;
    case 'save-thing': saveThing(el); break;
    case 'new-scenario': scenarioPage(el.dataset.id); break;
    case 'save-scenario': saveScenario(el); break;
    // the kit's plug goes through the Altice MCP (a dry run unless TT_LIVE_ACTIONS=1); the integration is simulated (server.py, tt_devices)
    case 'tt-off': el.blur(); api(`/api/tt-devices/${encodeURIComponent(el.dataset.id)}/power`, { method: 'POST', body: JSON.stringify({ on: false }) }).then(refresh).then(refreshPage); break;
    // an alert's answers go to the server, which runs the action (a dry run; the alarm is simulated) and keeps the answer
    case 'alert-device': case 'alert-ask': {
      el.blur(); el.disabled = true;
      const pg = el.closest('section.page'), body = act === 'alert-device' ? { device: el.dataset.id, on: false } : { act: el.dataset.id };
      if (pg?._alert) api(`/api/alerts/${encodeURIComponent(pg._alert.id)}/act`, { method: 'POST', body: JSON.stringify(body) }).then(refresh).then(refreshPage).catch((err) => dialog('Could not do it', err.message, [['OK', 'btn-p', null]]));
      break;
    }
    case 'tt-device': integrationPage(el.dataset.id); break;
    case 'tt-toggle': { el.blur(); const d = ttOf(el.dataset.id); if (d) api(`/api/tt-devices/${encodeURIComponent(d.id)}/power`, { method: 'POST', body: JSON.stringify({ on: !d.on }) }).then(refresh).then(refreshPage); break; }
    // simulated: the alert shows the alarm turned off; the platform's alarm is never called (AGENTS.md rule 1)
    case 'alarm-off': { el.blur(); el.disabled = true; const pg = el.closest('section.page'); if (pg?._alert) api(`/api/alerts/${encodeURIComponent(pg._alert.id)}/alarm-off`, { method: 'POST' }).then(refresh).then(refreshPage).catch((err) => dialog('Could not do it', err.message, [['OK', 'btn-p', null]])); break; }
    case 'other-thing': otherThingPage(); break;
    case 'other-next': { const n = $('othername').value.trim(); if (n) { pop(); methodPage(n.charAt(0).toUpperCase() + n.slice(1), n.toLowerCase()); } break; }
    case 'reregister': case 'retry-register': {
      const tid = topId();
      try { await api(`/api/things/${encodeURIComponent(tid)}/enrol`, { method: 'POST' }); await refresh(); if (act === 'reregister') registerPage(tid); else refreshPage(); }
      catch (err) { dialog('The camera is not ready', err.message, [['OK', 'btn-p', null]]); }
      break;
    }
    case 'cancel-register': {
      const tid = topId();
      dialog('Cancel adding this thing?', 'The thing will not be added.', [['No, continue', 'btn-s', null],
        ['Yes, cancel', 'btn-p', async () => { await api(`/api/things/${encodeURIComponent(tid)}`, { method: 'DELETE' }).catch(() => {}); pop(2); refresh(); }]]);
      break;
    }
    case 'finish': if (ui.scenBack) { pop(stack.length - ui.scenBack); ui.scenBack = 0; refreshPage(); } else { pop(stack.length); setTab('things'); } break;
    case 'remove-thing': {
      const tid = topId();
      dialog('Remove this thing?', 'Its visual fingerprint and sightings are deleted, at home and in the Altice database.', [['Cancel', 'btn-s', null],
        ['Remove', 'btn-p', async () => { await api(`/api/things/${encodeURIComponent(tid)}`, { method: 'DELETE' }).catch(() => {}); pop(); refresh(); }]]);
      break;
    }
    case 'suggest': { const ev = state.events.find((x) => x.id === id); if (ev) { openAssistant(); ask(ev.sentence); } break; }
    case 'sensor': {
      const r = state.rules.find((x) => x.id === id);
      if (r) { await api(`/api/rules/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify({ active: !r.active }) }); toast('Sensor', `${r.title}: ${r.active ? 'paused' : 'active'}.`); refresh(); }
      break;
    }
    default: break;
  }
});
device.addEventListener('input', (e) => {
  const k = e.target.dataset?.search; if (!k) return;
  ui.q[k] = e.target.value;
  if (k === 'devices') renderDevices(); else renderThings();
});

// ------------------------------------------------------------------ data
async function refresh() {
  try { state = await api('/api/state'); } catch { $('status').textContent = 'Server not reachable'; return; }
  $('status').textContent = '';
  renderEdge(state.edge); renderLog(); renderDoor(state.door); renderSim(state.presence); renderReplay(state.replay);
  // re-render the app only when its data changed, so a tap is never lost to a redraw
  const sig = JSON.stringify([state.home, state.things, state.rules, state.enrol, state.events.length, state.events[0]?.id]);
  if (sig !== lastSig) { lastSig = sig; renderTabs(); if (!stack.length) renderTab(ui.tab); else refreshPage(); }
  for (const e of state.events) {
    if (seen.has(e.id)) continue;
    seen.add(e.id);
    if (!firstLoad && e.kind === 'alert') toast(e.title || 'Alert', e.text, e.crop || e.picture, e);
    else if (!firstLoad && e.light) toast('Light', e.text);
  }
  firstLoad = false;
}

// The front door: "Simulate: door opens" opens the simulated Contact sensor and closes it 3 s later, as someone
// going out would. The server checks the "leave home without" sensors when it opens (server.py: /api/sim/door).
const simDoor = $('simdoor');
simDoor.addEventListener('click', async () => {
  simDoor.disabled = true; simDoor.textContent = 'Door open…';
  try {
    await api('/api/sim/door', { method: 'POST', body: JSON.stringify({ open: true }) });
    refresh();
    await new Promise((r) => setTimeout(r, 3000));
    await api('/api/sim/door', { method: 'POST', body: JSON.stringify({ open: false }) });
  } catch (e) { $('status').textContent = e.message; }
  simDoor.disabled = false; simDoor.textContent = 'Simulate: door opens';
  refresh();
});
function renderDoor(d) {
  simDoor.hidden = !!d?.live;    // the real Contact sensor drives the door while the MCP session is live
  simDoor.title = 'The MCP session is not live: this simulates the Contact sensor on the front door.';
  simHold.hidden = !!d?.live;
  simHold.textContent = EMBED ? (d?.open && d?.source === 'sim' ? 'Fechar a porta' : 'Deixar a porta aberta')
    : d?.open && d?.source === 'sim' ? 'Simulate: close the door' : 'Simulate: leave the door open';
  if (EMBED) simDoor.textContent = 'Porta abre e fecha';
}
// "Leave the door open" opens the simulated Contact sensor and keeps it open (the door left open when everyone left);
// the same button then closes it.
const simHold = $('simhold');
simHold.addEventListener('click', async () => {
  simHold.disabled = true;
  try { await api('/api/sim/door', { method: 'POST', body: JSON.stringify({ open: !(state.door?.open) }) }); } catch (e) { $('status').textContent = e.message; }
  simHold.disabled = false;
  refresh();
});
// Replay mode (server.py: TT_REPLAY): a recorded lab take stands in for the camera. The pill says which take, its second
// and the real clock; only the door, the phones and hand-switched devices are replayed, the rest is computed live.
let replayAt = null;
function renderReplay(r) {
  const el = $('replay');
  if (!r || !r.replay || EMBED) { el.hidden = true; replayAt = null; return; }
  replayAt = { t: r.t, at: performance.now(), on: r.started && !r.ended, d: r.duration, v: r.video };
  el.hidden = false;
  $('place').textContent = 'Work Room · Kit camera · replayed take';
  tickReplay();
}
function tickReplay() {
  if (!replayAt) return;
  const t = Math.min(replayAt.d, replayAt.t + (replayAt.on ? (performance.now() - replayAt.at) / 1000 : 0));
  const clock = new Date().toLocaleTimeString('en-GB');
  $('replay').innerHTML = `<b>REPLAY</b><span>${esc(replayAt.v)} · t ${t.toFixed(1)} / ${replayAt.d.toFixed(1)} s</span><span>now ${clock}</span>`;
}
setInterval(tickReplay, 100);
// The presence engine's state, and one toggle per Family member: their phone on the home Wi-Fi or not (simulated:
// the Altice router sees the phones, but no MCP tool exposes them yet).
function renderSim(p) {
  if (!p) return;
  const who = p.home?.length ? ` · ${p.home.join(', ')}` : '';
  const extra = p.unknown ? ` + ${p.unknown} not known` : '';
  if (EMBED) {
    const ST = { OCCUPIED: 'ocupada', LEAVING: 'a sair', EMPTY: 'vazia', UNSURE: 'incerta' };
    $('pres').innerHTML = `Casa <b data-state="${esc(p.state)}">${esc(ST[p.state] || '…')}</b> · ${p.count} em casa`;
    $('pres').title = p.reason || '';
  } else $('pres').innerHTML = `Home: <b data-state="${esc(p.state)}">${esc(p.state || '…')}</b> · ${p.count} at home${esc(who)}${esc(extra)}<br>${esc(p.reason || '')}`;
  const sig = JSON.stringify(p.phones);
  if ($('simphones').dataset.sig === sig) return;
  $('simphones').dataset.sig = sig;
  $('simphones').innerHTML = (p.phones || []).map((m) => `<button type="button" class="sim-phone" data-member="${esc(m.id)}" aria-pressed="${m.home ? 'true' : 'false'}"
    title="Simulated: ${esc(m.name)}'s phone on the home Wi-Fi">${EMBED ? `📱 ${esc(m.name)} · ${m.home ? 'em casa' : 'fora'}` : `${esc(m.name)}'s phone · ${m.home ? 'home' : 'away'}`}</button>`).join('');
}
$('simphones').addEventListener('click', async (e) => {
  const b = e.target.closest('[data-member]'); if (!b) return;
  b.disabled = true;
  try { await api('/api/sim/phone', { method: 'POST', body: JSON.stringify({ member: b.dataset.member, home: b.getAttribute('aria-pressed') !== 'true' }) }); } catch (err) { $('status').textContent = err.message; }
  refresh();
});

// Scale the 402 x 874 pt screen to the frame, so the app never reflows: the whole screen scales, as on a real device.
const screenWrap = $('screenwrap');
function fitDevice() {
  const z = screenWrap.clientWidth / 402;
  device.style.zoom = z;
  if (PHONE) device.style.height = `${Math.round(screenWrap.clientHeight / z)}px`;   // the app fills the phone's screen
}
new ResizeObserver(fitDevice).observe(screenWrap);
fitDevice();
const tick = () => { $('iostime').textContent = new Date().toLocaleTimeString('en-GB', { hour: 'numeric', minute: '2-digit' }); };
tick(); setInterval(tick, 15000);


// ------------------------------------------------------------------ the pitch site (embed): one scaled canvas, and the player
// The canvas is laid out at 1920 x 1016 and scaled as a whole to the frame, keeping its proportions (no reflow).
const PLAYER = { paused: false };
if (EMBED) {
  const split = document.querySelector('.split');
  const fitCanvas = () => {
    const sc = Math.min(innerWidth / 1920, innerHeight / 1016);
    split.style.setProperty('--s', sc);
    split.style.setProperty('--ox', `${Math.max(0, (innerWidth - 1920 * sc) / 2)}px`);
    split.style.setProperty('--oy', `${Math.max(0, (innerHeight - 1016 * sc) / 2)}px`);
  };
  addEventListener('resize', fitCanvas); fitCanvas();
  $('simbar').append($('simdoor'), $('simhold'));     // the door's two buttons sit with the phones

  const pl = $('player');
  const P = { s: null, at: 0, dragging: false };
  const fmt = (x) => x.toFixed(1).replace('.', ',');
  const ICON = { play: '<svg viewBox="0 0 24 24"><path d="M8 5.5v13l10.5-6.5z"/></svg>', pause: '<svg viewBox="0 0 24 24"><path d="M7 5h3.6v14H7zM13.4 5H17v14h-3.6z"/></svg>' };
  const post = (path, body) => fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then((r) => r.json()).catch(() => null);
  function draw(force) {
    const st = P.s; if (!st?.source) return;
    const src = st.source, take = src.kind === 'take';
    const playing = take && src.started && !src.paused && !src.ended;
    PLAYER.paused = take && (src.paused || src.ended || !src.started);
    $('place').textContent = take ? `Work Room · câmara do kit · gravação de 19 nov` : 'MacBook · webcam ao vivo';
    const sig = JSON.stringify([src.id, take, playing, src.story, st.sources.map((x) => x.id)]);
    if (force || pl.dataset.sig !== sig) {
      pl.dataset.sig = sig;
      const seg = st.sources.length < 2 ? '' : `<div class="seg" role="group" aria-label="Fonte da câmara">${st.sources.map((x) => `<button type="button" data-src="${x.id}" aria-pressed="${x.id === src.id}">${x.kind === 'live' ? '<i class="live"></i>' : ''}${esc(x.name)}</button>`).join('')}</div>`;
      pl.innerHTML = seg + (take
        ? `<button type="button" class="pb" data-act-p="${playing ? 'pause' : 'play'}" aria-label="${playing ? 'Pausa' : 'Reproduzir'}">${playing ? ICON.pause : ICON.play}</button>
           <button type="button" class="story" data-act-p="story" aria-pressed="${src.story}" title="Do início, com a porta e o telemóvel nos seus momentos">${src.story ? '● História a decorrer' : '↺ História do início'}</button>
           <div class="tl"><div class="marks">${src.marks.map((m) => `<i class="${m.what}" style="left:${((m.t - src.from) / (src.duration - src.from)) * 100}%"></i>`).join('')}</div>
             <input type="range" id="tl" min="${src.from}" max="${src.duration}" step="0.1" value="${src.t}" aria-label="Linha do tempo"></div>
           <span class="time" id="tltime"></span>`
        : `<div class="livebadge"><b>● AO VIVO</b> Câmara do MacBook · nada é gravado${st.phone_url ? `<span class="purl">Aplicação no telemóvel: <code>${esc(st.phone_url)}</code></span>` : ''}</div>`);
    }
    if (take) {
      const t = playing ? Math.min(src.duration, src.t + (performance.now() - P.at) / 1000) : src.t;
      const tl = $('tl');
      if (tl && !P.dragging) tl.value = t;
      if ($('tltime')) $('tltime').textContent = `${fmt(P.dragging ? +tl.value : t)} / ${fmt(src.duration)} s`;
    }
  }
  async function poll() {
    try { P.s = await fetch('/api/demo/status').then((r) => r.json()); P.at = performance.now(); } catch { return; }
    draw();
  }
  pl.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-src], [data-act-p]'); if (!b) return;
    b.disabled = true;
    const r = b.dataset.src ? await post('/api/demo/source', { id: b.dataset.src }) : await post('/api/demo/player', { action: b.dataset.actP });
    if (r?.source) { P.s = r; P.at = performance.now(); }
    if (b.dataset.src) { $('boxes').replaceChildren(); refresh(); }
    draw(true);
    if (b.dataset.actP === 'story') refresh();
  });
  pl.addEventListener('input', (e) => { if (e.target.id === 'tl') { P.dragging = true; draw(); } });
  pl.addEventListener('change', async (e) => {
    if (e.target.id !== 'tl') return;
    $('boxes').replaceChildren();
    const r = await post('/api/demo/player', { action: 'seek', t: +e.target.value });
    P.dragging = false;
    if (r?.source) { P.s = r; P.at = performance.now(); }
    draw(true);
  });
  poll(); setInterval(() => { if (!document.hidden) poll(); }, 700);
  setInterval(() => { if (!document.hidden && !P.dragging) draw(); }, 100);
}

window.__ttRefresh = refresh;     // lets web/demo.html (the scripted product video) redraw on cue
useSource('kit');
renderTabs();
await refresh();
const start = location.hash.slice(1);
setTab(['favorites', 'areas', 'devices', 'things', 'menu'].includes(start) ? start : 'devices');
setInterval(() => { if (!document.hidden) refresh(); }, 2000);
