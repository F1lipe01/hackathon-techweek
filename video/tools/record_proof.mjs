// One proof run, recorded in one continuous take with no editing: the whole prototype page (the replayed camera with the
// edge's live boxes and the replay readout, the Altice app with the Things tab, the activity log with every event and
// its time), from the moment the replay starts until a few seconds after the take ends.
//   NODE_PATH=<playwright-core's folder> node video/tools/record_proof.mjs <server> <out.mp4> <seconds> <book|face|nobody>
// Started by video/tools/proof_run.py, which runs the server in replay mode and the real edge service. The only taps are
// the ones a person would make on the phone: open the notification; "Yes" on each device card and "Turn off the alarm"
// (the scenario "nobody"); "Turn off the alarm" (the scenario "book"). Every tap goes to the server's real endpoints.
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const [BASE, OUT, SECONDS, SCENARIO] = process.argv.slice(2);
const W = 1920, H = 1080;
const pause = (ms) => new Promise((r) => setTimeout(r, ms));

const frames = join(dirname(OUT), `.frames-${SCENARIO}`);
rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });
const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true,
  args: ['--hide-scrollbars', `--window-size=${W},${H}`] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('console', (m) => { if (m.type() === 'error') console.log('page:', m.text()); });
await page.goto(`${BASE}/#things`, { waitUntil: 'load' });
await pause(2500);
const cdp = await page.context().newCDPSession(page);
const shots = [];
cdp.on('Page.screencastFrame', async ({ data, metadata, sessionId }) => {
  const f = join(frames, `f${String(shots.length).padStart(5, '0')}.jpg`);
  writeFileSync(f, Buffer.from(data, 'base64'));
  shots.push({ f, t: metadata.timestamp });
  await cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
});
await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 85, maxWidth: W, maxHeight: H, everyNthFrame: 1 });
const keepAlive = setInterval(() => page.evaluate(() => {   // a frame every 100 ms even when nothing else is painted
  let k = document.getElementById('rec-tick');
  if (!k) { k = document.createElement('div'); k.id = 'rec-tick'; k.style.cssText = 'position:fixed;right:0;bottom:0;width:2px;height:2px;z-index:2147483647;pointer-events:none'; document.body.append(k); }
  k.style.background = k.style.background === 'rgba(0, 0, 0, 0.01)' ? 'rgba(0, 0, 0, 0.02)' : 'rgba(0, 0, 0, 0.01)';
}).catch(() => {}), 100);
await pause(1000);

const start = await (await fetch(`${BASE}/api/replay/start`, { method: 'POST' })).json();
console.log(`replay started: ${start.video} from ${start.from} s`);
const t0 = Date.now(), end = t0 + Number(SECONDS) * 1000;
const opened = new Set();
const click = async (sel) => { const el = await page.$(sel); if (el) { await el.click(); return true; } return false; };
while (Date.now() < end) {
  const toast = await page.evaluate(() => { const t = document.getElementById('toast'); return t && !t.hidden && t.classList.contains('show') ? t.textContent : null; });
  if (toast && !opened.has(toast)) {
    opened.add(toast);
    console.log(`notification at ${((Date.now() - t0) / 1000).toFixed(1)} s: ${toast}`);
    await pause(1500);
    await page.evaluate(() => document.getElementById('toast').click());
    await pause(3000);
    if (SCENARIO === 'nobody') {
      for (;;) {
        if (!(await click('section.page:last-of-type [data-act="alert-device"]:not([disabled])'))) break;
        await pause(2500);
      }
      await click('section.page:last-of-type [data-act="alarm-off"]');
    } else if (SCENARIO === 'book') {
      await pause(1500);
      await click('section.page:last-of-type [data-act="alarm-off"]');
    }
  }
  await pause(300);
}
clearInterval(keepAlive);
await pause(300);
const tEnd = Date.now() / 1000;
await cdp.send('Page.stopScreencast');
await browser.close();
const list = shots.map((s, i) => `file '${s.f.split('/').pop()}'\nduration ${Math.max(0.001, ((shots[i + 1]?.t ?? tEnd) - s.t)).toFixed(4)}`).join('\n');
writeFileSync(join(frames, 'list.txt'), list + `\nfile '${shots.at(-1).f.split('/').pop()}'\n`);
execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', join(frames, 'list.txt'),
  '-vf', 'fps=25,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-movflags', '+faststart', OUT], { stdio: 'inherit' });
rmSync(frames, { recursive: true, force: true });
console.log(`${SCENARIO}: ${shots.length} frames, ${(tEnd - shots[0].t).toFixed(1)} s -> ${OUT}`);
