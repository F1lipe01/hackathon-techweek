// Act 3, s08 (8 s): the drop. The first boxes of the film lock on, one per beat (the wallet, then the pot), on the
// hall table; on the next downbeat the wallet's corners close into the ThingTracker mark while the picture softens
// behind it (blurred and lifted), the name is carried in, and the line holds over it, dead still. Fallback, when the take is missing: the wallet still.
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { Brackets, clamp, ramp } from "../ui";
import { Title } from "../type";
import { ToFilm } from "../media";
import { MarkParts, Wordmark, lockupGeom, markSquare } from "../brand";
import { lerp } from "../geom";
import { alpha } from "../tokens";

// the still (900 × 580) fills the frame by cover: 2,1333 px per pixel, 78,7 px cropped at the top
const K = 1920 / 900, OY = (1080 - 580 * K) / 2;
const px = (b: number[]) => ({ x: b[0] * K, y: b[1] * K + OY, w: (b[2] - b[0]) * K, h: (b[3] - b[1]) * K });
const WALLET = px([551, 303, 659, 359]); // hand-checked on the photo's edges, 3 px margin
const POT = px([298, 258, 419, 386]); // the yellow pot, rim to base
const ORIGIN = { x: 1190, y: 600 }; // the slow push centres near the wallet
const pushAt = (f: number) => interpolate(f, [0, 66], [1, 1.06], clamp);
const onScreen = (r: { x: number; y: number; w: number; h: number }, s: number) => ({ x: ORIGIN.x + (r.x - ORIGIN.x) * s, y: ORIGIN.y + (r.y - ORIGIN.y) * s, w: r.w * s, h: r.h * s });

const Lock: React.FC<{ r: ReturnType<typeof px>; at: number; label: string; out?: number }> = ({ r, at, label, out = 999 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < at) return null;
  const p = spring({ frame: frame - at, fps, config: { damping: 22, stiffness: 170, mass: 0.7 } });
  const g = 0.22 * (1 - p);
  const x = r.x - (r.w * g) / 2, y = r.y - (r.h * g) / 2, w = r.w * (1 + g), h = r.h * (1 + g);
  const o = interpolate(p, [0, 0.35], [0, 1], clamp) * (1 - ramp(frame, out, out + 5, theme.ease.in));
  const lab = ramp(frame - at, 5, 15, theme.ease.out);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: o }}>
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, border: `2px solid ${alpha(theme.colors.labs, 0.5)}`, borderRadius: 8 }} />
      <Brackets x={x} y={y} w={w} h={h} arm={Math.min(w, h) * 0.24} stroke={5} radius={8} color={theme.colors.labs} />
      <div style={{ position: "absolute", left: r.x, top: r.y - 44, padding: "5px 12px", borderRadius: 8, background: theme.colors.labs, color: theme.colors.white, fontFamily: theme.fonts.display, fontSize: 24, fontWeight: 600, clipPath: `inset(0 ${100 - 100 * lab}% 0 0)` }}>
        {label}
      </div>
    </div>
  );
};

export const S08: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const MORPH = 60; // the next downbeat (14,0 s)
  const s = pushAt(frame);
  const flood = ramp(frame, MORPH + 4, MORPH + 16, theme.ease.inOut);
  const g = lockupGeom(700, 960, 440);
  const sq = markSquare(g);
  // the wallet's corners travel to the mark's frame and become it
  const m = ramp(frame, MORPH, MORPH + 20, theme.ease.inOut);
  const from = onScreen(WALLET, pushAt(MORPH));
  const rx = lerp(from.x, sq.x, m), ry = lerp(from.y, sq.y, m), rw = lerp(from.w, sq.w, m), rh = lerp(from.h, sq.h, m);
  const markOn = frame >= MORPH + 20;
  const dotP = spring({ frame: frame - (MORPH + 14), fps, config: { damping: 14, stiffness: 160, mass: 0.7 } });
  const wipe = ramp(frame, MORPH + 20, MORPH + 40, theme.ease.out);
  return (
    <AbsoluteFill style={{ background: theme.colors.bg, overflow: "hidden" }}>
      {/* the hall table: a slow push, the boxes attached to it */}
      <AbsoluteFill style={{ filter: `blur(${(flood * 22).toFixed(2)}px)` }}>
        <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: `${ORIGIN.x}px ${ORIGIN.y}px` }}>
          <Img src={staticFile("stock/stills/wallet-hall-table.jpg")} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", filter: "brightness(1.04) saturate(1.04)" }} />
          <Lock r={POT} at={15} label="vaso" out={MORPH - 6} />
        </AbsoluteFill>
        {frame < MORPH ? (
          <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: `${ORIGIN.x}px ${ORIGIN.y}px` }}>
            <Lock r={WALLET} at={0} label="carteira" />
          </AbsoluteFill>
        ) : null}
      </AbsoluteFill>
      {/* the hall table softens and lifts behind the name: a soft blur of the picture, never an empty frame */}
      <AbsoluteFill style={{ background: alpha(theme.colors.white, 0.5 * flood) }} />
      <ToFilm />
      {/* the wallet's corners become the mark */}
      {frame >= MORPH && !markOn ? (
        <Brackets x={rx} y={ry} w={rw} h={rh} arm={lerp(Math.min(from.w, from.h) * 0.24, sq.w * 0.28, m)} stroke={lerp(5, 5 * g.unit, m)} radius={lerp(8, 5 * g.unit, m)} color={theme.colors.labs} />
      ) : null}
      {frame >= MORPH + 14 ? (
        <MarkParts x={g.mark(0, 0).x} y={g.mark(0, 0).y} unit={g.unit} showCorners={markOn} trail={ramp(frame, MORPH + 14, MORPH + 22, theme.ease.out)}
          dot={[-8 * (1 - dotP), 8 * (1 - dotP), interpolate(dotP, [0, 1], [0.6, 1]), interpolate(dotP, [0, 0.3], [0, 1], clamp)]} />
      ) : null}
      {frame >= MORPH + 20 ? <Wordmark g={g} wipe={wipe} dx={-14 * (1 - wipe)} /> : null}
      <div style={{ position: "absolute", left: 0, width: 1920, top: 590, display: "flex", justifyContent: "center" }}>
        <Title text="A câmara da casa passa a saber onde estão as coisas." size={56} max={1700} at={MORPH + 46} entrance="blur" weight={600} />
      </div>
    </AbsoluteFill>
  );
};
