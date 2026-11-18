// Local additions to src/theme.ts for the presentation film, kept in one place.
// `app` is the Altice app copy's palette, sampled in prototype/web/app.css (tokens at the top of that file).
import { theme } from "../theme";

export const app = {
  bg: "#EEF3FB",      // page
  card: "#E4EAF6",    // tinted card
  list: "#F7FAFD",    // white lists, sheets
  ink: "#1A2233",
  ink2: "#111320",
  muted: "#73727C",
  blue: "#175BCC",    // status lines, "Active"
  teal: theme.colors.teal,
  wandStroke: "#3AA58B",
  wandSpark: "#C837B5",
} as const;

/** "#RRGGBB" + alpha → "rgba(r,g,b,a)". */
export const alpha = (hex: string, a: number): string => {
  const h = hex.replace("#", "");
  const n = parseInt(h, 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

/** The daylight grade: a warm white lifted into footage. */
export const grade = { warm: "#FFE7C6" } as const;

export const shadow = {
  card: `0 30px 60px -24px ${alpha(theme.colors.ink, 0.28)}, 0 2px 6px ${alpha(theme.colors.ink, 0.06)}`,
  soft: `0 18px 40px -20px ${alpha(theme.colors.ink, 0.22)}`,
  phone: `0 60px 90px -30px ${alpha(theme.colors.ink, 0.45)}`,
} as const;

/** Layout constants shared by the scenes (px, 1920 × 1080). */
export const layout = {
  margin: 140,
  colW: 640,
} as const;
