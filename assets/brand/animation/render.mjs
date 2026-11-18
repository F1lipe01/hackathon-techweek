// Render logo-reveal.html to MP4, frame by frame, at an exact frame rate.
// Needs Node 22+ (global WebSocket), Google Chrome and ffmpeg. No npm packages.
//   node render.mjs                       -> default variants below
//   node render.mjs expand:meo-blue ...   -> chosen variants (mode:theme)
import { spawn, execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const W = 1920, H = 1080, FPS = Number(process.env.FPS || 60), PORT = 9339;
const variants = process.argv.slice(2).length ? process.argv.slice(2)
  : ['expand:labs', 'expand:labs-deep', 'collapse:labs'];

const profile = mkdtempSync(join(tmpdir(), 'tt-chrome-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
  '--hide-scrollbars', '--disable-gpu', `--window-size=${W},${H}`, 'about:blank'], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 50; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find((t) => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(200);
  }
  throw new Error('Chrome did not start');
}

const ws = new WebSocket(await target());
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let seq = 0;
const pending = new Map();
const waiters = [];
ws.addEventListener('message', (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  if (msg.method) waiters.filter((w) => w.method === msg.method).forEach((w) => w.resolve(msg));
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++seq;
  pending.set(id, (m) => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
  ws.send(JSON.stringify({ id, method, params }));
});
const once = (method) => new Promise((resolve) => waiters.push({ method, resolve }));
const evaluate = async (expression) =>
  (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result.value;

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });

const outDir = join(HERE, 'out');
mkdirSync(outDir, { recursive: true });

try {
  for (const v of variants) {
    const [mode, theme] = v.split(':');
    const url = `${pathToFileURL(join(HERE, 'logo-reveal.html')).href}?export=1&mode=${mode}&theme=${theme}`;
    const loaded = once('Page.loadEventFired');
    await send('Page.navigate', { url });
    await loaded;
    for (let i = 0; i < 100 && !(await evaluate('window.READY === true')); i++) await sleep(100);
    const duration = await evaluate('window.DURATION');
    const frames = Math.round((duration / 1000) * FPS);
    const dir = mkdtempSync(join(tmpdir(), `tt-frames-${mode}-${theme}-`));
    for (let f = 0; f <= frames; f++) {
      await evaluate(`renderAt(${(f * 1000) / FPS})`);
      const { data } = await send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(join(dir, `f${String(f).padStart(4, '0')}.png`), Buffer.from(data, 'base64'));
    }
    const out = join(outDir, `track-things-${mode}-${theme}.mp4`);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(dir, 'f%04d.png'),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-movflags', '+faststart', out]);
    // a still of the last frame, for slides that cannot play video
    execFileSync('cp', [join(dir, `f${String(frames).padStart(4, '0')}.png`), out.replace(/\.mp4$/, '-end.png')]);
    rmSync(dir, { recursive: true, force: true });
    console.log(`built ${out}  (${frames + 1} frames, ${duration} ms)`);
  }
} finally {
  ws.close();
  chrome.kill();
  await sleep(300);
  rmSync(profile, { recursive: true, force: true });
}
