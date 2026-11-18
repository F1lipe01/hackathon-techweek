// Video 2's local look: everything derives from the shared theme. No new hues, only alpha variants and helpers.
import { theme } from "../theme";

const c = theme.colors;
const a = (hex: string, alpha: number) => `${hex}${Math.round(alpha * 255).toString(16).padStart(2, "0")}`;

export const look = {
  c,
  a,
  shadow: `0 40px 80px -30px ${a(c.labsDeep, 0.35)}, 0 12px 28px -12px ${a(c.ink, 0.25)}`,
  cardBorder: `1px solid ${a(c.ink, 0.08)}`,
  phoneBody: c.ink,
  dimLine: a(c.inkDim, 0.35),
} as const;

// Portuguese number formatting: decimal comma.
export const pt = (v: number, d = 2) => v.toFixed(d).replace(".", ",");
export const mmss = (t: number) => `0:${String(Math.floor(t)).padStart(2, "0")}`;

/** A sound cue: `file` is a key of SFX in audio.ts; `dur` (frames) cuts it short with a quick fade. */
export type Cue = { at: number; file: string; volume?: number; dur?: number };

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
