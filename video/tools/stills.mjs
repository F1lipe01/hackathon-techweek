// Render chosen frames of a composition as PNG stills, bundling once (for review sheets: every cut at −0,2 s and
// +0,2 s, the middle of each shot). Run it through tools/heavy.sh.
//   node tools/stills.mjs <composition> <out dir> <frame> [<frame> ...]     (frames may be "s:12.3" for seconds)
import { bundle } from '@remotion/bundler';
import { openBrowser, renderStill, selectComposition } from '@remotion/renderer';
import { mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const [id, out, ...list] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: resolve('src/index.ts') });
// the system Chrome (the downloaded headless shell is not reliable on this machine)
const browser = { browserExecutable: process.env.REMOTION_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', chromeMode: 'chrome-for-testing' };
const puppeteerInstance = await openBrowser('chrome', { browserExecutable: browser.browserExecutable, chromeMode: browser.chromeMode });
const composition = await selectComposition({ serveUrl, id, ...browser, puppeteerInstance });
for (const f of list) {
  const frame = f.startsWith('s:') ? Math.round(parseFloat(f.slice(2)) * composition.fps) : parseInt(f, 10);
  const output = join(out, `${id}-${String(frame).padStart(5, '0')}.png`);
  try {
    await renderStill({ serveUrl, composition, frame, output, imageFormat: 'png', ...browser, puppeteerInstance });
    console.log(output);
  } catch (e) {
    console.log(`frame ${frame}: ${String(e.message).split('\n')[0]}`);
  }
}
await puppeteerInstance.close({ silent: true });
