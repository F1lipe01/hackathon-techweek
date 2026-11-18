// The official ThingTracker lockup (public/brand/thingtracker-light.svg: the mark and the wordmark, Switzer outlines)
// and the "by Altice Labs" endorsement (public/brand/by-altice-labs-light.svg). The mark is drawn here from the same
// geometry as the official file (64-unit grid, corners stroke 5 in #0084D6, the trail and the dot) so its parts can move;
// the wordmark is the official file itself, clipped so only its letters show. Nothing is redrawn, stretched or recoloured.
import React from "react";
import { Img, staticFile } from "remotion";

export const LOCKUP = { vbX: -6, vbY: -6, vbW: 736.2, vbH: 127, markScale: 1.79687, wordFrom: 0.185 } as const;
export const BLUE = "#0084D6";

/** Where the lockup's parts sit when it is `width` px wide and centred on (cx, cy). */
export const lockupGeom = (width: number, cx: number, cy: number) => {
  const k = width / LOCKUP.vbW;
  const h = LOCKUP.vbH * k;
  const left = cx - width / 2, top = cy - h / 2;
  const unit = LOCKUP.markScale * k; // px per mark unit
  const mark = (u: number, v: number) => ({ x: left + (u * LOCKUP.markScale - LOCKUP.vbX) * k, y: top + (v * LOCKUP.markScale - LOCKUP.vbY) * k });
  return { k, h, left, top, unit, mark, width };
};

/** The mark's frame square (corner to corner, 7..57 units) in px, for a lockup geometry. */
export const markSquare = (g: ReturnType<typeof lockupGeom>) => {
  const a = g.mark(7, 7);
  return { x: a.x, y: a.y, w: 50 * g.unit, h: 50 * g.unit };
};

const CORNERS = ["M7 21 V12 Q7 7 12 7 H21", "M43 7 H52 Q57 7 57 12 V21", "M57 43 V52 Q57 57 52 57 H43", "M7 43 V52 Q7 57 12 57 H21"];
const FROM = [[-7, -7], [7, -7], [7, 7], [-7, 7]];

/**
 * The mark at a position (its 64-unit box at x, y, `unit` px per unit). `corners` 0→1 each locks one corner on (from
 * 7 units out, faded); `trail` 0→1 shows the two trail dots; `dot` is the dot's [dx, dy, scale, opacity] in units.
 */
export const MarkParts: React.FC<{ x: number; y: number; unit: number; corners?: number[]; trail?: number; dot?: [number, number, number, number]; showCorners?: boolean }> = ({
  x, y, unit, corners = [1, 1, 1, 1], trail = 1, dot = [0, 0, 1, 1], showCorners = true,
}) => (
  <svg viewBox="0 0 64 64" width={64 * unit} height={64 * unit} style={{ position: "absolute", left: x, top: y, overflow: "visible" }}>
    {showCorners
      ? CORNERS.map((d, i) => {
          const p = corners[i];
          const [fx, fy] = FROM[i];
          return (
            <path key={i} d={d} fill="none" stroke={BLUE} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" opacity={Math.min(1, p * 1.6)}
              transform={`translate(${fx * (1 - p)} ${fy * (1 - p)})`} />
          );
        })
      : null}
    <circle cx={19} cy={45} r={2.4} fill={BLUE} fillOpacity={0.35 * trail} />
    <circle cx={25.5} cy={38.5} r={3} fill={BLUE} fillOpacity={0.6 * trail} />
    <circle cx={35 + dot[0]} cy={29 + dot[1]} r={8 * dot[2]} fill="#000000" opacity={dot[3]} />
  </svg>
);

/** The official wordmark (the lockup file with its mark clipped away), revealed left to right by `wipe` 0→1. */
export const Wordmark: React.FC<{ g: ReturnType<typeof lockupGeom>; wipe?: number; dx?: number }> = ({ g, wipe = 1, dx = 0 }) => {
  const from = LOCKUP.wordFrom * 100;
  const right = 100 - (from + (100 - from) * wipe);
  return (
    <Img
      src={staticFile("brand/thingtracker-light.svg")}
      style={{ position: "absolute", left: g.left + dx, top: g.top, width: g.width, height: g.h, clipPath: `inset(-10% ${right}% -10% ${from}%)` }}
    />
  );
};

/**
 * "by" and the official Altice Labs logo (public/brand/altice-labs-logo-black.png, 2765 × 893) on one line, `width` px
 * wide in all. "by" is set at the logo's x-height (Inter 500, the endorsement grey #555555) and sits on the baseline of
 * the logo's "altice", so it is centred on the wordmark. Measured on the logo: "altice" runs from 13,7 % (x-height top)
 * to 49,3 % (baseline) of its height.
 */
export const EndorsementLine: React.FC<{ cx: number; top: number; width: number; style?: React.CSSProperties }> = ({ cx, top, width, style }) => {
  const LOGO = { w: 2765, h: 893, xTop: 0.137, base: 0.493 };
  const byShare = 0.25; // "by" and its space, as a share of the line
  const lw = width * (1 - byShare);
  const lh = (lw * LOGO.h) / LOGO.w;
  const fs = ((LOGO.base - LOGO.xTop) * lh) / 0.546; // Inter's x-height is 0,546 em
  const baseline = top + LOGO.base * lh;
  const left = cx - width / 2;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, ...style }}>
      <span style={{ position: "absolute", left, top: baseline - 0.863 * fs, fontFamily: "Inter, sans-serif", fontWeight: 500, fontSize: fs, lineHeight: 1, color: "#555555", whiteSpace: "nowrap" }}>by</span>
      <Img src={staticFile("brand/altice-labs-logo-black.png")} style={{ position: "absolute", left: left + width - lw, top, width: lw, height: lh }} />
    </div>
  );
};
