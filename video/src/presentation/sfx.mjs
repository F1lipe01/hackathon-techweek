// Synthesizes the presentation film's small SFX kit as 16-bit mono WAVs in public/presentation/sfx/.
// Deterministic (seeded noise), no downloads.  Run: node src/presentation/sfx.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RATE = 48000;
const out = path.join(path.dirname(fileURLToPath(import.meta.url)), "../../public/presentation/sfx");
fs.mkdirSync(out, { recursive: true });

let seed = 7;
const noise = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 2 ** 31 - 1;
};

const write = (name, samples) => {
  const n = samples.length;
  const buf = Buffer.alloc(44 + n * 2);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(RATE, 24); buf.writeUInt32LE(RATE * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(n * 2, 40);
  const peak = Math.max(1e-9, ...samples.map(Math.abs));
  samples.forEach((v, i) => buf.writeInt16LE(Math.round((v / peak) * 0.9 * 32767), 44 + i * 2));
  fs.writeFileSync(path.join(out, name), buf);
};

const len = (s) => Math.round(s * RATE);

// whoosh: band-passed noise sweeping up then down, soft attack, longer tail
{
  const n = len(0.7); const a = new Array(n).fill(0);
  let lp = 0, lp2 = 0;
  for (let i = 0; i < n; i++) {
    const t = i / n;
    const cut = 0.02 + 0.18 * Math.sin(Math.PI * Math.min(1, t * 1.3));
    lp += cut * (noise() - lp); lp2 += cut * (lp - lp2);
    const env = Math.sin(Math.PI * Math.pow(t, 0.7)) ** 2;
    a[i] = (lp - lp2) * env;
  }
  write("whoosh.wav", a);
}

// shutter: two short filtered clicks, 45 ms apart
{
  const n = len(0.16); const a = new Array(n).fill(0);
  for (const at of [0, 0.045]) {
    let lp = 0;
    const s0 = len(at);
    for (let i = 0; i < len(0.03); i++) {
      lp += 0.5 * (noise() - lp);
      a[s0 + i] += (noise() - lp) * Math.exp(-i / len(0.006)) * (at === 0 ? 1 : 0.7);
    }
  }
  write("shutter.wav", a);
}

// tap: a soft, short pitched pop (sine with a fast pitch drop)
{
  const n = len(0.12); const a = new Array(n);
  let ph = 0;
  for (let i = 0; i < n; i++) {
    const t = i / RATE;
    const f = 520 * Math.exp(-t * 28) + 260;
    ph += (2 * Math.PI * f) / RATE;
    a[i] = Math.sin(ph) * Math.exp(-t * 38);
  }
  write("tap.wav", a);
}

// chime: two soft sine notes (a notification)
{
  const n = len(0.9); const a = new Array(n).fill(0);
  for (const [at, f] of [[0, 880], [0.11, 1318.5]]) {
    const s0 = len(at);
    for (let i = 0; s0 + i < n; i++) {
      const t = i / RATE;
      const env = Math.min(1, t / 0.006) * Math.exp(-t * 5.5);
      a[s0 + i] += (Math.sin(2 * Math.PI * f * t) + 0.18 * Math.sin(2 * Math.PI * f * 2 * t)) * env;
    }
  }
  write("chime.wav", a);
}

console.log("wrote", fs.readdirSync(out).join(", "), "in", out);
