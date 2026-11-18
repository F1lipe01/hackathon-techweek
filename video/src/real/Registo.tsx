// 1 · Registo: three moments of the colleague's phone recording, at real speed, cut together. Each photo taken
// becomes one of the 3 views of the fingerprint (R.views3).
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { ANDROID, AndroidPhone, VideoAt } from "./devices";
import { Body, Heading, Overline, Rise } from "./layers";
import { clamp, Cue, look, mmss } from "./look";
import { R } from "./recognition";

const { c, a } = look;

// footage/phone-photos.mp4 re-encoded with a keyframe every 15 frames and no B-frames (same timing): with the
// original's sparse keyframes Remotion showed frames that were off from the requested second.
const PHONE_CLIP = "real/phone-photos-kf.mp4";
const V3 = R.views3.views;
const BOX = (n: number) => R.views[n - 1].box_phone_px;

// the three passages of the recording, each around one photo, played at real speed
const SEGS = [
  { from: 0.4, to: 2.3 },
  { from: 22.25, to: 24.0 },
  { from: 35.3, to: 38.9 },
].map((s) => ({ ...s, len: Math.round((s.to - s.from) * theme.fps) }));
const LEAD = 6;
const SEG_START = SEGS.reduce<number[]>((acc, s, i) => [...acc, i === 0 ? LEAD : acc[i - 1] + SEGS[i - 1].len], []);
const PRESS_F = V3.map((v, i) => SEG_START[i] + Math.round((v.t - SEGS[i].from) * theme.fps));
const HOLD = 12;
export const REGISTO_FRAMES = SEG_START[2] + SEGS[2].len + HOLD;
export const REGISTO_CUES: Cue[] = PRESS_F.map((pf) => ({ at: pf - 1, file: "shutter" }));

// layout
const PHONE_SCALE = 0.98;
const PHONE_X = 200;
const PHONE_H = ANDROID.screenH * PHONE_SCALE + 2 * ANDROID.bezel;
const PHONE_Y = (1080 - PHONE_H) / 2 + 14;
const SCREEN_X = PHONE_X + ANDROID.bezel;
const SCREEN_Y = PHONE_Y + ANDROID.bezel;
const GRID_X = 790;
const GRID_Y = 470;
const SLOT = 250;
const GAP = 26;
const LAND = 18;

type Rect = { x: number; y: number; w: number; h: number };
const lerpRect = (r0: Rect, r1: Rect, p: number): Rect => ({
  x: r0.x + (r1.x - r0.x) * p, y: r0.y + (r1.y - r0.y) * p, w: r0.w + (r1.w - r0.w) * p, h: r0.h + (r1.h - r0.h) * p,
});
const boxOnScreen = (b: readonly number[], pad = 0): Rect => {
  const w = b[2] - b[0];
  const h = b[3] - b[1];
  const x0 = Math.max(0, b[0] - w * pad);
  const y0 = Math.max(65, b[1] - h * pad);
  const x1 = Math.min(392, b[2] + w * pad);
  const y1 = Math.min(589, b[3] + h * pad);
  return { x: SCREEN_X + x0 * PHONE_SCALE, y: SCREEN_Y + y0 * PHONE_SCALE, w: (x1 - x0) * PHONE_SCALE, h: (y1 - y0) * PHONE_SCALE };
};
const slotRect = (i: number): Rect => ({ x: GRID_X + i * (SLOT + GAP), y: GRID_Y, w: SLOT, h: SLOT });
const fitIn = (slot: Rect, aspect: number, inset = 14): Rect => {
  const w = slot.w - 2 * inset;
  const h = slot.h - 2 * inset;
  return aspect > w / h
    ? { x: slot.x + inset, y: slot.y + inset + (h - w / aspect) / 2, w, h: w / aspect }
    : { x: slot.x + inset + (w - h * aspect) / 2, y: slot.y + inset, w: h * aspect, h };
};

export const Registo: React.FC = () => {
  const frame = useCurrentFrame();
  const seg = Math.max(0, SEG_START.filter((s) => frame >= s).length - 1);
  const local = Math.max(0, frame - SEG_START[seg]);
  const src = Math.min(SEGS[seg].to, SEGS[seg].from + local / theme.fps);
  const cutIn = seg > 0 ? interpolate(local, [0, 5], [0.85, 0], { ...clamp, easing: theme.ease.out }) : 0;
  const landed = PRESS_F.filter((pf) => frame >= pf + LAND).length;
  const sig = interpolate(frame, [PRESS_F[2] + LAND + 6, PRESS_F[2] + LAND + 26], [0, 1], { ...clamp, easing: theme.ease.out });

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: PHONE_X, top: PHONE_Y }}>
        <AndroidPhone scale={PHONE_SCALE}>
          <VideoAt src={PHONE_CLIP} second={src} />
          <AbsoluteFill style={{ background: c.ink, opacity: cutIn }} />
          {PRESS_F.map((pf, i) => {
            const o = interpolate(frame, [pf - 1, pf, pf + 7], [0, 0.7, 0], { ...clamp, easing: theme.ease.out });
            return o > 0 ? <AbsoluteFill key={i} style={{ background: c.white, opacity: o }} /> : null;
          })}
        </AndroidPhone>
      </div>

      {/* where in the recording we are */}
      <div style={{ position: "absolute", left: PHONE_X, width: ANDROID.screenW * PHONE_SCALE + 2 * ANDROID.bezel, top: PHONE_Y - 56,
        display: "flex", justifyContent: "center" }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center", padding: "8px 16px", borderRadius: 999, background: c.white,
          border: look.cardBorder, fontFamily: theme.fonts.mono, fontSize: 18, color: c.ink, fontVariantNumeric: "tabular-nums" }}>
          <span>telemóvel</span>
          <span style={{ color: c.inkDim }}>{mmss(src)} · tempo real</span>
        </div>
      </div>

      {/* OWLv2's box on each photo */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {V3.map((v, i) => {
          const pf = PRESS_F[i];
          const o = interpolate(frame, [pf - 2, pf + 1, pf + 10, pf + 16], [0, 1, 1, 0], clamp);
          if (o <= 0) return null;
          const r = boxOnScreen(BOX(v.n));
          return (
            <g key={i} opacity={o}>
              <rect x={r.x} y={r.y} width={r.w} height={r.h} rx={6} fill="none" stroke={c.labs} strokeWidth={3} />
              <rect x={r.x} y={r.y - 30} width={118} height={26} rx={5} fill={c.labs} />
              <text x={r.x + 9} y={r.y - 11} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>OWLv2 · livro</text>
            </g>
          );
        })}
      </svg>

      <div style={{ position: "absolute", left: GRID_X, top: 190, width: 3 * SLOT + 2 * GAP, display: "flex", flexDirection: "column", gap: 16 }}>
        <Rise delay={2} y={16}><Overline>1 · Registo</Overline></Rise>
        <Rise delay={5} y={16}><Heading size={60}>Três fotografias do livro</Heading></Rise>
        <Rise delay={8} y={16}>
          <Body size={27}>Tiradas por um colega com o telemóvel. Cada fotografia dá uma vista do livro.</Body>
        </Rise>
      </div>

      {V3.map((v, i) => {
        const s = slotRect(i);
        const filled = frame >= PRESS_F[i] + LAND;
        return (
          <div key={i} style={{ position: "absolute", left: s.x, top: s.y, width: s.w,
            opacity: interpolate(frame, [8 + i * 4, 20 + i * 4], [0, 1], { ...clamp, easing: theme.ease.out }) }}>
            <div style={{ width: s.w, height: s.h, borderRadius: 18, background: filled ? c.white : a(c.white, 0.35), boxSizing: "border-box",
              border: filled ? look.cardBorder : `2px dashed ${look.dimLine}` }} />
            <div style={{ marginTop: 10, fontFamily: theme.fonts.mono, fontSize: 18, color: filled ? c.ink : c.inkDim, display: "flex",
              justifyContent: "space-between" }}>
              <span>vista {i + 1}</span><span style={{ color: c.inkDim }}>foto {mmss(v.t)}</span>
            </div>
          </div>
        );
      })}

      {V3.map((v, i) => {
        const pf = PRESS_F[i];
        if (frame < pf + 2) return null;
        const p = interpolate(frame, [pf + 2, pf + LAND], [0, 1], { ...clamp, easing: theme.ease.inOut });
        const start = boxOnScreen(BOX(v.n), 0.08);
        const r = lerpRect(start, fitIn(slotRect(i), start.w / start.h), p);
        return (
          <Img key={i} src={staticFile(v.file)} style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, objectFit: "fill",
            borderRadius: 6, boxShadow: `0 ${10 * Math.sin(Math.PI * p)}px 24px -10px ${a(c.ink, 0.35)}` }} />
        );
      })}

      <div style={{ position: "absolute", left: GRID_X, top: GRID_Y + SLOT + 64, display: "flex", alignItems: "center", gap: 20 }}>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: 24, fontWeight: 500, color: c.ink, fontVariantNumeric: "tabular-nums",
          opacity: interpolate(frame, [14, 26], [0, 1], clamp) }}>
          {landed} / 3 vistas
        </div>
        <div style={{ height: 2, width: 110 * sig, background: c.labs }} />
        <div style={{ opacity: sig, display: "flex", flexDirection: "column", gap: 2 }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, color: c.ink }}>assinatura visual do livro</div>
          <div style={{ fontFamily: theme.fonts.mono, fontSize: 17, color: c.inkDim }}>DINOv2 · 384 números por vista</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
