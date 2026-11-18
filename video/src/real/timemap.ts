// Speed ramps: the source second shown at each output frame, integrated from a smooth speed profile.
import { theme } from "../theme";

const smooth = (x: number) => x * x * (3 - 2 * x);

/** 1 inside each window, `fast` far from them, a smooth ramp of `ramp` source seconds in between. */
export const rampSpeed = (windows: [number, number][], fast: number, ramp: number) => (s: number) => {
  let w = 0;
  for (const [from, to] of windows) {
    const d = s < from ? from - s : s > to ? s - to : 0;
    w = Math.max(w, d >= ramp ? 0 : smooth(1 - d / ramp));
  }
  return 1 + (fast - 1) * (1 - w);
};

/** Source seconds per output frame, from `start` until `end`. */
export const buildMap = (start: number, end: number, speed: (s: number) => number, fps: number = theme.fps): number[] => {
  const out: number[] = [];
  let s = start;
  while (s < end) {
    out.push(s);
    s += speed(s) / fps;
  }
  return out;
};

/** First output frame at which the source reaches second `t`. */
export const frameOf = (map: number[], t: number) => {
  const i = map.findIndex((s) => s >= t);
  return i < 0 ? map.length - 1 : i;
};

export const srcAt = (map: number[], f: number) => map[Math.max(0, Math.min(map.length - 1, Math.round(f)))];
