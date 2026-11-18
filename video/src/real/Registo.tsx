// 1 · Registo: the colleague's phone recording, speed-ramped; each real photo becomes one of the 8 views.
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { ANDROID, AndroidPhone, VideoAt } from "./devices";
import { Body, Heading, Overline, Rise } from "./layers";
import { clamp, Cue, look, mmss } from "./look";
import { R } from "./recognition";
import { buildMap, frameOf, rampSpeed, srcAt } from "./timemap";

const { c, a } = look;

// footage/phone-photos.mp4 re-encoded with a keyframe every 15 frames and no B-frames (same timing): with the
// original's sparse keyframes Remotion showed frames that were off from the requested second.
const PHONE_CLIP = "real/phone-photos-kf.mp4";
const PRESSES = R.views.map((v) => v.t);
const SPEED = rampSpeed(PRESSES.map((p) => [p - 0.35, p + 0.25] as [number, number]), 8, 0.7);
const MAP = buildMap(0.5, 38.4, SPEED);
const PRESS_F = PRESSES.map((p) => frameOf(MAP, p));
const LEAD = 8;                                   // phone settles before the clip runs
const HOLD = 66;                                  // after the last photo: the fingerprint
export const REGISTO_FRAMES = LEAD + MAP.length + HOLD;
export const REGISTO_SFX: Cue[] = [
  ...PRESS_F.map((pf) => ({ at: LEAD + pf - 1, file: "shutter.wav", volume: 0.55 })),
  { at: LEAD + PRESS_F[7] + 22 + 6, file: "confirm.wav", volume: 0.35 },
];

// layout
const PHONE_SCALE = 0.98;
const PHONE_X = 200;
const PHONE_H = ANDROID.screenH * PHONE_SCALE + 2 * ANDROID.bezel;
const PHONE_Y = (1080 - PHONE_H) / 2 + 14;
const SCREEN_X = PHONE_X + ANDROID.bezel;
const SCREEN_Y = PHONE_Y + ANDROID.bezel;
const GRID_X = 780;
const GRID_Y = 420;
const SLOT = 196;
const GAP = 22;
const LAND = 22;                                  // frames from photo to landing

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

const slotRect = (i: number): Rect => ({ x: GRID_X + (i % 4) * (SLOT + GAP), y: GRID_Y + Math.floor(i / 4) * (SLOT + GAP + 34), w: SLOT, h: SLOT });

// the crop's own aspect, fitted inside a slot
const fitIn = (slot: Rect, aspect: number, inset = 12): Rect => {
  const w = slot.w - 2 * inset;
  const h = slot.h - 2 * inset;
  return aspect > w / h
    ? { x: slot.x + inset, y: slot.y + inset + (h - w / aspect) / 2, w, h: w / aspect }
    : { x: slot.x + inset + (w - h * aspect) / 2, y: slot.y + inset, w: h * aspect, h };
};

export const Registo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - LEAD;
  const src = srcAt(MAP, f);
  const speed = f >= MAP.length ? 0 : SPEED(src);
  const landed = PRESS_F.filter((pf) => f >= pf + LAND).length;
  const lastLand = PRESS_F[7] + LAND;
  const phoneIn = spring({ frame, fps, config: theme.spring.smooth });
  const sig = interpolate(f, [lastLand + 8, lastLand + 34], [0, 1], { ...clamp, easing: theme.ease.out });
  const bump = PRESS_F.reduce((m, pf) => {
    const d = f - (pf + LAND);
    return d >= 0 && d < 12 ? Math.max(m, 1 - d / 12) : m;
  }, 0);

  return (
    <AbsoluteFill>
      {/* the phone */}
      <div style={{ position: "absolute", left: PHONE_X, top: PHONE_Y, opacity: phoneIn,
        transform: `translateY(${interpolate(phoneIn, [0, 1], [50, 0]) + Math.sin(frame / 28) * 2}px)` }}>
        <AndroidPhone scale={PHONE_SCALE}>
          <VideoAt src={PHONE_CLIP} second={src} />
          {PRESS_F.map((pf, i) => {
            const o = interpolate(f, [pf - 1, pf, pf + 9], [0, 0.85, 0], { ...clamp, easing: theme.ease.out });
            return o > 0 ? <AbsoluteFill key={i} style={{ background: c.white, opacity: o }} /> : null;
          })}
        </AndroidPhone>
      </div>

      {/* speed and source time */}
      <div style={{ position: "absolute", left: PHONE_X, width: ANDROID.screenW * PHONE_SCALE + 2 * ANDROID.bezel, top: PHONE_Y - 58,
        display: "flex", justifyContent: "center", opacity: phoneIn }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center", padding: "8px 16px", borderRadius: 999, background: c.white,
          border: look.cardBorder, fontFamily: theme.fonts.mono, fontSize: 19, color: c.ink, fontVariantNumeric: "tabular-nums" }}>
          <span style={{ width: 9, height: 9, borderRadius: 9, background: speed === 0 || speed > 1.3 ? c.inkDim : c.alert }} />
          <span>{mmss(src)}</span>
          <span style={{ color: c.inkDim }}>{speed === 0 ? "fim da gravação" : speed > 1.3 ? `acelerado ×${Math.round(speed)}` : "tempo real"}</span>
        </div>
      </div>

      {/* OWLv2's box on each photo */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        {R.views.map((v, i) => {
          const pf = PRESS_F[i];
          const o = interpolate(f, [pf - 2, pf + 1, pf + 14, pf + 22], [0, 1, 1, 0], clamp);
          if (o <= 0) return null;
          const r = boxOnScreen(v.box_phone_px);
          return (
            <g key={i} opacity={o}>
              <rect x={r.x} y={r.y} width={r.w} height={r.h} rx={6} fill="none" stroke={c.labs} strokeWidth={3} />
              <rect x={r.x} y={r.y - 30} width={118} height={26} rx={5} fill={c.labs} />
              <text x={r.x + 9} y={r.y - 11} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>OWLv2 · livro</text>
            </g>
          );
        })}
      </svg>

      {/* text */}
      <div style={{ position: "absolute", left: GRID_X, top: 150, width: 4 * SLOT + 3 * GAP, display: "flex", flexDirection: "column", gap: 18 }}>
        <Rise delay={4}><Overline>1 · Registo</Overline></Rise>
        <Rise delay={8}><Heading size={62}>Oito fotografias, oito vistas</Heading></Rise>
        <Rise delay={12}>
          <Body size={27}>Um colega fotografa o livro com o telemóvel. Cada fotografia dá uma vista; uma vista quase igual a outra (≥ 0,97) não conta.</Body>
        </Rise>
      </div>

      {/* slots */}
      {R.views.map((v, i) => {
        const s = slotRect(i);
        const appear = spring({ frame: frame - 14 - i * 3, fps, config: theme.spring.smooth });
        const filled = f >= PRESS_F[i] + LAND;
        return (
          <div key={i} style={{ position: "absolute", left: s.x, top: s.y, width: s.w, opacity: appear,
            transform: `translateY(${interpolate(appear, [0, 1], [20, 0])}px)` }}>
            <div style={{ width: s.w, height: s.h, borderRadius: 18, background: filled ? c.white : a(c.white, 0.35),
              border: filled ? look.cardBorder : `2px dashed ${look.dimLine}`, boxShadow: filled ? `0 14px 30px -18px ${a(c.ink, 0.45)}` : "none",
              boxSizing: "border-box" }} />
            <div style={{ marginTop: 8, fontFamily: theme.fonts.mono, fontSize: 17, color: filled ? c.ink : c.inkDim, display: "flex",
              justifyContent: "space-between" }}>
              <span>vista {i + 1}</span><span style={{ color: c.inkDim }}>foto {mmss(v.t)}</span>
            </div>
          </div>
        );
      })}

      {/* the crops, flying out of the phone into their slots */}
      {R.views.map((v, i) => {
        const pf = PRESS_F[i];
        if (f < pf + 2) return null;
        const p = spring({ frame: f - pf - 2, fps, config: theme.spring.smooth, durationInFrames: LAND });
        const start = boxOnScreen(v.box_phone_px, 0.08);
        const end = fitIn(slotRect(i), start.w / start.h);
        const r = lerpRect(start, end, p);
        const arc = -70 * Math.sin(Math.PI * Math.min(1, p));
        const pop = 1 + 0.08 * Math.sin(Math.PI * Math.min(1, p));
        return (
          <Img key={i} src={staticFile(v.file)} style={{ position: "absolute", left: r.x, top: r.y + arc, width: r.w, height: r.h,
            objectFit: "fill", borderRadius: interpolate(p, [0, 1], [4, 8]), transform: `scale(${pop})`,
            boxShadow: `0 ${18 * Math.sin(Math.PI * Math.min(1, p))}px 30px -10px ${a(c.ink, 0.35)}` }} />
        );
      })}

      {/* counter and the fingerprint */}
      <div style={{ position: "absolute", left: GRID_X, top: GRID_Y + 2 * (SLOT + 34) + GAP + 28, width: 4 * SLOT + 3 * GAP,
        display: "flex", alignItems: "center", gap: 22 }}>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: 26, fontWeight: 500, color: c.ink, fontVariantNumeric: "tabular-nums",
          transform: `scale(${1 + bump * 0.08})`, transformOrigin: "left center", opacity: interpolate(frame, [16, 30], [0, 1], clamp) }}>
          {landed} / 8 vistas
        </div>
        <div style={{ height: 3, flex: `0 0 ${130 * sig}px`, background: c.labs, borderRadius: 2 }} />
        <div style={{ opacity: sig, transform: `translateX(${interpolate(sig, [0, 1], [-16, 0])}px)`, display: "flex", flexDirection: "column", gap: 4 }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 32, fontWeight: 600, color: c.ink }}>assinatura visual do livro</div>
          <div style={{ fontFamily: theme.fonts.mono, fontSize: 18, color: c.inkDim }}>DINOv2 · 384 números por vista</div>
        </div>
      </div>

      {/* the fingerprint frame around the grid */}
      {sig > 0 ? (
        <div style={{ position: "absolute", left: GRID_X - 14, top: GRID_Y - 14, width: 4 * SLOT + 3 * GAP + 28,
          height: 2 * SLOT + GAP + 34 + 28 + 34, borderRadius: 26, border: `3px solid ${c.labs}`, opacity: sig,
          transform: `scale(${interpolate(sig, [0, 1], [1.03, 1])})` }} />
      ) : null}
    </AbsoluteFill>
  );
};
