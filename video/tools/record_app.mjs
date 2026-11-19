// Records the REAL prototype app (prototype/server.py on :8765, local text model on :8766) as raw phone-screen footage
// for video 1 (storyboard v5.1, F3): 402 x 874 pt at 3x, one MP4 per take in video/public/app/, with the time of each
// action next to it (<take>.marks.json, seconds from the first frame).
//   NODE_PATH=<playwright-core's folder> node video/tools/record_app.mjs <take> [<take> ...]
// Takes: register (Things tab, add the wallet), register-keys (the same with the keys, eight views), ask (Where is my wallet? + the sentence that becomes a sensor),
// alert (the door opens, the notification).
// The server, the database and the language model are the real ones. Only two things stand in for the camera service
// (edge.py), which stays off: its status and registration progress are posted to the server's own edge API, and the
// live view inside the registration screen shows a still of the wallet instead of the lab's camera stream.
// Back up prototype/data/home.db before running and restore it after (the caller does this). Never sets
// TT_LIVE_ACTIONS: the server keeps every device action a dry run.
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync, rmSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8765';
const OUT = resolve('video/public/app');
const IMG = process.env.REC_IMG; // folder with live.jpg, view1-3.jpg, seen.jpg
const W = 402, H = 874, DSF = 3;
const pause = (ms) => new Promise((r) => setTimeout(r, ms));
const b64 = (f) => readFileSync(join(IMG, f)).toString('base64');

async function api(path, body, method = 'POST') {
  const r = await fetch(BASE + path, { method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) throw new Error(`${method} ${path}: ${r.status} ${await r.text()}`);
  return r.json();
}

// the stand-in camera service: online while recording
let edgeTimer = null;
const edgeOn = (state = 'idle') => { clearInterval(edgeTimer); const f = () => api('/api/edge/status', { state, checked: 0, analysed: 0 }).catch(() => {}); f(); edgeTimer = setInterval(f, 3000); };
const edgeOff = () => clearInterval(edgeTimer);

// raw phone screen: only the device, at 402 x 874, no frame; a visible finger for taps
const RAW_CSS = `
  html, body { width: ${W}px !important; height: ${H}px !important; overflow: hidden !important; margin: 0 !important; background: #eef3fb !important; }
  #screenwrap { position: fixed !important; left: 0 !important; top: 0 !important; width: ${W}px !important; height: ${H}px !important; border-radius: 0 !important; z-index: 9998 !important; }
  .phone .frame, .activity, .main { visibility: hidden !important; }
  #screenwrap, #screenwrap * { visibility: visible; }
  .rec-finger { position: absolute; z-index: 9999; left: 0; top: 0; width: 40px; height: 40px; margin: -20px 0 0 -20px; border-radius: 50%;
    background: rgb(26 34 51 / 0.22); border: 2px solid rgb(255 255 255 / 0.9); box-shadow: 0 4px 14px rgb(0 0 0 / 0.18); opacity: 0; pointer-events: none;
    transition: left 480ms cubic-bezier(0.65, 0, 0.35, 1), top 480ms cubic-bezier(0.65, 0, 0.35, 1), opacity 200ms ease-out, transform 120ms ease-out; }
  .rec-finger.show { opacity: 1; } .rec-finger.press { transform: scale(0.8); background: rgb(42 190 158 / 0.45); }
`;

// Concept takes (act 6, marked "conceito" in the film): the same real app, but /api/state and /api/assistant are
// answered here with the case's data, as prototype/web/demo.js does. Nothing reaches the server's database.
const C = { on: false, events: [], rules: [], reply: null };
const today = (h, m) => { const d = new Date(); d.setHours(h, m, 0, 0); return d.getTime() / 1000; };
let cid = 0;
const conceptEvent = (e) => C.events.unshift({ id: 'concept-' + (++cid), ts: Date.now() / 1000, text: '', ...e });

async function take(name, clock, script) {
  const frames = join(OUT, `.frames-${name}`);
  rmSync(frames, { recursive: true, force: true });
  mkdirSync(frames, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true,
    args: ['--hide-scrollbars', `--force-device-scale-factor=${DSF}`, `--window-size=${W},${H}`] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: DSF });
  page.on('console', (m) => { if (m.type() === 'error') console.log('page:', m.text()); });
  // the lab's camera stream never appears: the registration live view shows the wallet
  await page.route('**/api/kit/**', (route) => route.fulfill({ status: 200, contentType: 'image/jpeg', body: readFileSync(join(IMG, 'live.jpg')) }));
  await page.route('**/crops/concept-*', (route) => route.fulfill({ status: 200, contentType: 'image/jpeg', body: readFileSync(join(IMG, decodeURIComponent(route.request().url().split('/').pop()))) }));
  if (C.on) {
    await page.route('**/api/state', async (route) => {
      const s = await (await fetch(BASE + '/api/state')).json();
      s.events = [...C.events, ...s.events];
      s.rules = [...C.rules, ...s.rules];
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(s) });
    });
    await page.route('**/api/assistant', async (route) => {
      const text = JSON.parse(route.request().postData()).text;
      await pause(C.delay ?? 900);
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(C.reply(text)) });
    });
  }
  // the phone's clock in the status bar reads the story's time
  await page.addInitScript((t) => { setInterval(() => { const e = document.getElementById('iostime'); if (e && e.textContent !== t) e.textContent = t; }, 50); }, clock);
  await page.goto(`${BASE}/#things`, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: RAW_CSS });
  await page.evaluate(() => { const f = document.createElement('div'); f.className = 'rec-finger'; f.id = 'recfinger'; document.getElementById('device').appendChild(f); });
  await pause(1500);
  const cdp = await page.context().newCDPSession(page);
  const shots = [];
  cdp.on('Page.screencastFrame', async ({ data, metadata, sessionId }) => {
    const f = join(frames, `f${String(shots.length).padStart(5, '0')}.jpg`);
    writeFileSync(f, Buffer.from(data, 'base64'));
    shots.push({ f, t: metadata.timestamp });
    await cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  const marks = [];
  const mark = (n) => marks.push({ name: n, t: Date.now() / 1000 });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 94, maxWidth: W * DSF, maxHeight: H * DSF, everyNthFrame: 1 });
  // keep frames coming while nothing changes, so the timing stays exact
  const keepAlive = setInterval(() => page.evaluate(() => { document.body.style.outlineColor = document.body.style.outlineColor === 'red' ? 'blue' : 'red'; }).catch(() => {}), 100);
  await pause(400);
  mark('start');

  const tap = async (sel) => {
    const el = await page.waitForSelector(sel, { timeout: 8000, state: 'visible' });
    const xy = await page.evaluate((s) => {
      const r = document.querySelector(s).getBoundingClientRect(), d = document.getElementById('device').getBoundingClientRect();
      return [r.left + r.width / 2 - d.left, r.top + r.height / 2 - d.top];
    }, sel);
    await page.evaluate(([x, y]) => {
      const f = document.getElementById('recfinger');
      if (!f.classList.contains('show')) { f.style.transition = 'none'; f.style.left = x + 'px'; f.style.top = y + 'px'; void f.offsetWidth; f.style.transition = ''; }
      f.style.left = x + 'px'; f.style.top = y + 'px'; f.classList.add('show');
    }, xy);
    await pause(560);
    await page.evaluate(() => document.getElementById('recfinger').classList.add('press'));
    await pause(110);
    mark('tap ' + sel);
    await el.click();
    await pause(150);
    await page.evaluate(() => document.getElementById('recfinger').classList.remove('press'));
  };
  const hideFinger = () => page.evaluate(() => document.getElementById('recfinger').classList.remove('show'));
  const type = async (text) => {
    for (const ch of text) { await page.evaluate((c) => { const f = document.getElementById('askfield'); f.value += c; f.scrollLeft = f.scrollWidth; }, ch); await pause(55 + Math.random() * 35); }
  };
  const refresh = () => page.evaluate(() => window.__ttRefresh?.());

  await script({ page, tap, hideFinger, type, refresh, mark });

  clearInterval(keepAlive);
  await pause(300);
  const tEnd = Date.now() / 1000;
  await cdp.send('Page.stopScreencast');
  await browser.close();
  const t0 = shots[0].t;
  const list = shots.map((s, i) => `file '${s.f.split('/').pop()}'\nduration ${Math.max(0.001, ((shots[i + 1]?.t ?? tEnd) - s.t)).toFixed(4)}`).join('\n');
  writeFileSync(join(frames, 'list.txt'), list + `\nfile '${shots.at(-1).f.split('/').pop()}'\n`);
  const out = join(OUT, `${name}.mp4`);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', join(frames, 'list.txt'),
    '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-g', '15', '-movflags', '+faststart', out], { stdio: 'inherit' });
  writeFileSync(join(OUT, `${name}.marks.json`), JSON.stringify(marks.map((m) => ({ name: m.name, s: +(m.t - t0).toFixed(3) })), null, 1));
  rmSync(frames, { recursive: true, force: true });
  console.log(`${name}: ${shots.length} frames, ${(shots.at(-1).t - t0).toFixed(1)} s → ${out}`);
}

const TAKES = {
  // Things tab → Add things → Wallet → three views → "Wallet added" → Done
  register: () => take('register', '8:05', async ({ page, tap, hideFinger, refresh, mark }) => {
    edgeOn('idle');
    await pause(1200);
    await tap('[data-act="add-thing"].btn-p');
    await pause(1300);
    await tap('[data-act="pick-thing"][data-name="Wallet"]');
    edgeOn('registering');
    await page.waitForSelector('.livebox', { timeout: 8000 });
    mark('register');
    await hideFinger();
    const tid = (await api('/api/state', null, 'GET')).enrol?.thing_id;
    await pause(1100);
    const crops = ['view1.jpg', 'view2.jpg', 'view3.jpg'].map(b64);
    for (let i = 1; i <= 3; i++) {
      await api('/api/edge/observe', { boxes: [{ box: [0.29, 0.38, 0.71, 0.74], label: `Registering Wallet · view ${i} of 8`, kind: 'enrol' }] });
      await api('/api/edge/enrol', { thing_id: tid, got: i });
      await refresh();
      mark('view-' + i);
      await pause(1000);
    }
    const vec = () => Array.from({ length: 8 }, () => +Math.random().toFixed(4));
    await api('/api/edge/enrol', { thing_id: tid, got: 3, done: true, crops_b64: crops, vectors: [vec(), vec(), vec()], model: 'stand-in for edge.py (video recording)' });
    await api('/api/edge/observe', { boxes: [] });
    await refresh();
    mark('added');
    await pause(3200);
    await tap('.bottom-bar [data-act="finish"]');
    mark('done');
    await hideFinger();
    await pause(2200);
    edgeOff();
  }),
  // Things tab → Add things → Keys → eight views, quickly → "Keys added" → Done. No boxes from the stand-in edge: the
  // film draws the live view (the stock clip of keys shown to the camera) and its box over the recording's live box.
  'register-keys': () => take('register-keys', '8:05', async ({ page, tap, hideFinger, refresh, mark }) => {
    edgeOn('idle');
    await pause(1200);
    await tap('[data-act="add-thing"].btn-p');
    await pause(1300);
    await tap('[data-act="pick-thing"][data-name="Keys"]');
    edgeOn('registering');
    await page.waitForSelector('.livebox', { timeout: 8000 });
    mark('register');
    await hideFinger();
    const tid = (await api('/api/state', null, 'GET')).enrol?.thing_id;
    await api('/api/edge/observe', { boxes: [] });
    await pause(900);
    for (let i = 1; i <= 8; i++) {
      await api('/api/edge/enrol', { thing_id: tid, got: i });
      await refresh();
      mark('view-' + i);
      await pause(420);
    }
    const crops = Array.from({ length: 8 }, (_, i) => b64(`view${i + 1}.jpg`));
    const vec = () => Array.from({ length: 8 }, () => +Math.random().toFixed(4));
    await api('/api/edge/enrol', { thing_id: tid, got: 8, done: true, crops_b64: crops, vectors: crops.map(vec), model: 'stand-in for edge.py (video recording)' });
    await refresh();
    mark('added');
    await pause(3200);
    await tap('.bottom-bar [data-act="finish"]');
    mark('done');
    await hideFinger();
    await pause(1500);
    edgeOff();
  }),
  // the assistant: "Where is my wallet?", then "Tell me if I leave home without my wallet"
  ask: () => take('ask', '8:40', async ({ tap, hideFinger, type, mark }) => {
    await pause(900);
    await tap('#fab');
    mark('assistant');
    await pause(900);
    await tap('#askfield');
    await hideFinger();
    mark('type-question');
    await type('Where is my wallet?');
    await pause(350);
    await tap('[data-act="send"]');
    mark('sent-question');
    await hideFinger();
    await pause(4200);
    mark('type-sensor');
    await type('Tell me if I leave home without my wallet');
    await pause(350);
    await tap('[data-act="send"]');
    mark('sent-sensor');
    await hideFinger();
    await pause(5200);
  }),
  // the front door opens (the prototype's simulated Contact sensor) and the wallet is still on the hall table
  alert: () => take('alert', '8:52', async ({ refresh, mark }) => {
    await pause(1500);
    mark('door');
    await api('/api/sim/door', { open: true });
    const t0 = Date.now();
    let seen = false;
    while (Date.now() - t0 < 15000) {
      await refresh();
      const s = await api('/api/state', null, 'GET');
      if (!seen && s.events.some((e) => e.kind === 'alert')) { seen = true; await refresh(); mark('alert'); break; }
      await pause(150);
    }
    await api('/api/sim/door', { open: false });
    await pause(5000);
  }),
  // act 6, the cat: the app proposes a sensor, one tap adds it, later the alert with the cat's photo
  cat: () => { Object.assign(C, { on: true, events: [], rules: [], delay: 800,
    reply: () => { const r = { id: 'concept-r1', title: 'Cat on the kitchen counter', sentence: 'Tell me if the cat jumps on the kitchen counter', active: true };
      C.rules = [r]; return { kind: 'sensor', sensor: r }; } });
    conceptEvent({ kind: 'suggest', title: 'The cat on the counter', sentence: 'Tell me if the cat jumps on the kitchen counter' });
    return take('cat', '14:20', async ({ tap, hideFinger, refresh, mark }) => {
      await pause(1200);
      await tap('[data-act="suggest"]');
      mark('suggest');
      await hideFinger();
      await pause(2600);
      await tap('[data-act="close-sheet"]');
      await hideFinger();
      await pause(1400);
      conceptEvent({ kind: 'alert', title: 'Cat on the kitchen counter', text: 'The cat is on the kitchen counter.', crop: 'concept-cat.jpg' });
      await refresh();
      mark('alert');
      await pause(4000);
    }); },
  // act 6, the mother: "Is Mum up yet?" answered from presence in the living room, no face recognition
  mum: () => { Object.assign(C, { on: true, events: [], rules: [], delay: 900,
    reply: () => ({ kind: 'answer', answer: 'Yes. Someone has been in the living room since 08:12.', candidates: [], thing: null }) });
    return take('mum', '8:15', async ({ tap, hideFinger, type, mark }) => {
      await pause(800);
      await tap('#fab');
      await pause(800);
      await tap('#askfield');
      await hideFinger();
      mark('type');
      await type('Is Mum up yet?');
      await pause(300);
      await tap('[data-act="send"]');
      mark('sent');
      await hideFinger();
      await pause(3600);
    }); },
  // act 6, noon: the "someone living alone" sensor the server really proposes (server.py: profile_suggestions)
  noon: () => { Object.assign(C, { on: true, events: [], rules: [], reply: null });
    return take('noon', '12:00', async ({ refresh, mark }) => {
      await pause(1500);
      conceptEvent({ kind: 'alert', title: 'Nobody in the kitchen by 12:00', text: 'Nobody has been in the kitchen this morning.' });
      await refresh();
      mark('alert');
      await pause(4500);
    }); },
  // act 6, the night: "What happened last night?", two events, each with its picture
  night: () => { Object.assign(C, { on: true, events: [], rules: [], delay: 1000,
    reply: () => ({ kind: 'answer', answer: 'Two things last night: the dog barked at 04:01, and a person was by the car at 04:02.', thing: null,
      candidates: [{ id: 'concept-dog', name: 'Dog barking', last_seen: { ts: today(4, 1), zone_name: 'porch', crop: 'concept-porch.jpg' } },
        { id: 'concept-person', name: 'Person', last_seen: { ts: today(4, 2), zone_name: 'driveway', crop: 'concept-person.jpg' } }] }) });
    return take('night', '7:30', async ({ tap, hideFinger, type, mark }) => {
      await pause(800);
      await tap('#fab');
      await pause(800);
      await tap('#askfield');
      await hideFinger();
      mark('type');
      await type('What happened last night?');
      await pause(300);
      await tap('[data-act="send"]');
      mark('sent');
      await hideFinger();
      await pause(4000);
    }); },
};

for (const name of process.argv.slice(2)) await TAKES[name]();
edgeOff();
