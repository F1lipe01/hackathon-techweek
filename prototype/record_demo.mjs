// Record the scripted product video (web/demo.html) at 1920 x 1080 with headless Chrome.
//   NODE_PATH=<playwright-core's folder> node prototype/record_demo.mjs [out.mp4]
// Chrome sends a frame each time the page repaints (DevTools screencast); each frame is kept as long as it was on
// screen, then ffmpeg encodes a constant 30 fps H.264 file.
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const out = process.argv[2] || 'prototype/data/recordings/thingtracker-demo.mp4';
const frames = join('prototype/data/recordings', 'demo-frames');
rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });

const browser = await chromium.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: true, args: ['--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1920,1080'],   // the capture is the window: keep it 1080 tall
});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('console', (m) => { if (m.type() === 'warning' || m.type() === 'error') console.log('page:', m.text()); });
const cdp = await page.context().newCDPSession(page);
const shots = [];
cdp.on('Page.screencastFrame', async ({ data, metadata, sessionId }) => {
  const f = join(frames, `f${String(shots.length).padStart(5, '0')}.jpg`);
  writeFileSync(f, Buffer.from(data, 'base64'));
  shots.push({ f, t: metadata.timestamp });
  await cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
});
await page.goto('http://127.0.0.1:8765/web/demo.html', { waitUntil: 'networkidle' });
await page.waitForTimeout(800);
await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
await page.waitForFunction(() => window.DEMO_DONE === true, null, { timeout: 180000, polling: 250 });
await page.waitForTimeout(600);
await cdp.send('Page.stopScreencast');
await browser.close();

// each frame lasts until the next one arrived
const list = shots.map((s, i) => `file '${s.f.split('/').pop()}'\nduration ${Math.max(0.001, ((shots[i + 1]?.t ?? s.t + 0.5) - s.t)).toFixed(4)}`).join('\n');
writeFileSync(join(frames, 'list.txt'), list + `\nfile '${shots.at(-1).f.split('/').pop()}'\n`);
execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', join(frames, 'list.txt'),
  '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-movflags', '+faststart', out], { stdio: 'inherit' });
console.log(`${shots.length} frames, ${(shots.at(-1).t - shots[0].t).toFixed(1)} s → ${out}`);
