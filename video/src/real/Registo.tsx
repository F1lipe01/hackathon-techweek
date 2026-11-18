// 1 · Registo: the colleague's phone recording, three passages at real speed, in a modern phone tilted over the bright
// home. Each photo taken becomes one of the 3 views of the fingerprint (R.views3) and flies into the glass card.
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { VideoAt } from "./devices";
import { Body, Heading, Overline } from "./layers";
import { clamp, Cue, look, mmss, warm } from "./look";
import { R } from "./recognition";
import { BlurIn, ContactShadow, Glass, ModernPhone, Plate } from "./stage";

const { c, a } = look;

// public/real/phone-3seg-2x.mp4: the three passages of footage/phone-photos.mp4 (frames 12–69, 667–720, 1059–1167),
// joined and upscaled 2x with lanczos and light sharpening by video/tools/prep-real.sh.
const CLIP = "real/phone-3seg-2x.mp4";
const SEGS = [
  { f0: 12, f1: 69 },
  { f0: 667, f1: 720 },
  { f0: 1059, f1: 1167 },
].map((s) => ({ ...s, len: s.f1 - s.f0 }));
const CLIP_AT = SEGS.reduce<number[]>((acc, s, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SEGS[i - 1].len], []);
const V3 = R.views3.views;
const BOX = (n: number) => R.views[n - 1].box_phone_px;

const LEAD = 10;
const SEG_START = SEGS.reduce<number[]>((acc, s, i) => [...acc, i === 0 ? LEAD : acc[i - 1] + SEGS[i - 1].len], []);
const PRESS_F = V3.map((v, i) => SEG_START[i] + Math.round(v.t * theme.fps) - SEGS[i].f0);
const LAND = 20;
const HOLD = 14;
export const REGISTO_FRAMES = SEG_START[2] + SEGS[2].len + HOLD;
export const REGISTO_CUES: Cue[] = [
  { at: 0, file: "whooshBig" },
  { at: 6, file: "whoosh", volume: 0.7 },
  ...PRESS_F.flatMap((pf, i) => [
    { at: pf - 1, file: "shutter" },
    { at: pf + 3, file: i % 2 ? "swipeAlt" : "swipe" },
    { at: pf + LAND - 2, file: "paper" },
  ]),
  { at: PRESS_F[2] + LAND + 6, file: "lockonSoft" },
];

// the phone: screen 392 x 850 CSS px (the 2x clip is shown at half size, sharp in 4K), tilted in 3D
const SW = 392;
const SH = 850;
const PHONE_C = { x: 430, y: 560 };
const PERSP = 2200;
const BEZEL = Math.round(SW * 0.028) + 3;

// glass card and its slots
const CARD = { x: 790, y: 150, w: 1000, h: 790 };
const SLOT = 268;
const GAP = 28;
const SLOTS_X = CARD.x + 56;
const SLOTS_Y = CARD.y + 330;

type Rect = { x: number; y: number; w: number; h: number };
const lerp = (p: number, a0: number, a1: number) => a0 + (a1 - a0) * p;
const lerpRect = (r0: Rect, r1: Rect, p: number): Rect => ({ x: lerp(p, r0.x, r1.x), y: lerp(p, r0.y, r1.y), w: lerp(p, r0.w, r1.w), h: lerp(p, r0.h, r1.h) });
const slotRect = (i: number): Rect => ({ x: SLOTS_X + i * (SLOT + GAP), y: SLOTS_Y, w: SLOT, h: SLOT });
const fitIn = (slot: Rect, aspect: number, inset = 14): Rect => {
  const w = slot.w - 2 * inset;
  const h = slot.h - 2 * inset;
  return aspect > w / h
    ? { x: slot.x + inset, y: slot.y + inset + (h - w / aspect) / 2, w, h: w / aspect }
    : { x: slot.x + inset + (w - h * aspect) / 2, y: slot.y + inset, w: h * aspect, h };
};

/** Where a point of the flat screen (px from the screen's centre) lands on the frame, after the phone's 3D tilt. */
const project = (dx: number, dy: number, rotY: number, rotX: number, scale: number, tx: number) => {
  const ry = (rotY * Math.PI) / 180;
  const rx = (rotX * Math.PI) / 180;
  const y1 = dy * Math.cos(rx);
  const z1 = dy * Math.sin(rx);
  const x2 = dx * Math.cos(ry) + z1 * Math.sin(ry);
  const z2 = -dx * Math.sin(ry) + z1 * Math.cos(ry);
  const s = PERSP / (PERSP - z2 * scale);
  return { x: PHONE_C.x + tx + x2 * scale * s, y: PHONE_C.y + y1 * scale * s };
};

export const Registo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const seg = Math.max(0, SEG_START.filter((s) => frame >= s).length - 1);
  const local = Math.max(0, Math.min(SEGS[seg].len - 1, frame - SEG_START[seg]));
  const clipFrame = CLIP_AT[seg] + local;
  const srcSecond = (SEGS[seg].f0 + local) / fps;
  const cutIn = seg > 0 ? interpolate(frame - SEG_START[seg], [0, 6], [1, 0], { ...clamp, easing: theme.ease.out }) : 0;
  const landed = PRESS_F.filter((pf) => frame >= pf + LAND).length;
  const sig = interpolate(frame, [PRESS_F[2] + LAND + 6, PRESS_F[2] + LAND + 26], [0, 1], { ...clamp, easing: theme.ease.out });

  // the phone arrives turning towards the camera, then breathes
  const enter = spring({ frame, fps, config: { damping: 18, stiffness: 70, mass: 1.1 } });
  const rotY = 30 * (1 - enter) + 11 + Math.sin(frame / 46) * 1.2;
  const rotX = 4 + 6 * (1 - enter);
  const tx = -120 * (1 - enter);
  const scale = 0.92 + 0.08 * enter;
  const phoneTransform = `perspective(${PERSP}px) translateX(${tx}px) rotateY(${rotY}deg) rotateX(${rotX}deg) scale(${scale})`;

  // a box on the phone's screen (px of the 392 x 850 recording) as a rectangle on the frame
  const boxOnFrame = (b: readonly number[], pad = 0): Rect => {
    const w = b[2] - b[0];
    const h = b[3] - b[1];
    const x0 = Math.max(0, b[0] - w * pad), y0 = Math.max(65, b[1] - h * pad);
    const x1 = Math.min(SW, b[2] + w * pad), y1 = Math.min(589, b[3] + h * pad);
    const p0 = project(x0 - SW / 2, y0 - SH / 2, rotY, rotX, scale, tx);
    const p1 = project(x1 - SW / 2, y1 - SH / 2, rotY, rotX, scale, tx);
    return { x: p0.x, y: p0.y, w: p1.x - p0.x, h: p1.y - p0.y };
  };

  return (
    <AbsoluteFill>
      <Plate dur={REGISTO_FRAMES} offset={3} blur={14} zoom={[1.08, 1.14]} pan={[30, -30]} />

      <ContactShadow x={PHONE_C.x + tx + 20} y={PHONE_C.y + SH / 2 + 46} w={460} opacity={0.4 * enter} />
      <div style={{ position: "absolute", left: PHONE_C.x - (SW + 2 * BEZEL) / 2, top: PHONE_C.y - (SH + 2 * BEZEL) / 2,
        transform: phoneTransform, opacity: interpolate(enter, [0, 0.25], [0, 1], clamp),
        filter: `drop-shadow(0 50px 50px ${a(warm.shadow, 0.35)})` }}>
        <ModernPhone w={SW} h={SH}>
          <VideoAt src={CLIP} second={clipFrame / fps} />
          <AbsoluteFill style={{ background: c.ink, opacity: cutIn }} />
          {PRESS_F.map((pf, i) => {
            const o = interpolate(frame, [pf - 1, pf, pf + 8], [0, 0.75, 0], { ...clamp, easing: theme.ease.out });
            return o > 0 ? <AbsoluteFill key={i} style={{ background: c.white, opacity: o }} /> : null;
          })}
        </ModernPhone>
      </div>

      {/* where in the colleague's recording we are */}
      <div style={{ position: "absolute", left: PHONE_C.x - 170 + tx, top: 52, width: 340, display: "flex", justifyContent: "center",
        opacity: enter }}>
        <Glass strong style={{ borderRadius: 999, padding: "9px 18px", display: "flex", gap: 12, alignItems: "center",
          fontFamily: theme.fonts.mono, fontSize: 18, color: c.ink, fontVariantNumeric: "tabular-nums" }}>
          <span style={{ width: 9, height: 9, borderRadius: 9, background: c.alert }} />
          <span>telemóvel {mmss(srcSecond)}</span>
          <span style={{ color: c.inkDim }}>tempo real</span>
        </Glass>
      </div>

      {/* OWLv2's box on each photo */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {V3.map((v, i) => {
          const pf = PRESS_F[i];
          const o = interpolate(frame, [pf - 2, pf + 1, pf + 10, pf + 16], [0, 1, 1, 0], clamp);
          if (o <= 0) return null;
          const r = boxOnFrame(BOX(v.n));
          return (
            <g key={i} opacity={o}>
              <rect x={r.x} y={r.y} width={r.w} height={r.h} rx={6} fill="none" stroke={c.labs} strokeWidth={3} />
              <rect x={r.x} y={r.y - 30} width={118} height={26} rx={6} fill={c.labs} />
              <text x={r.x + 9} y={r.y - 11} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>OWLv2 · livro</text>
            </g>
          );
        })}
      </svg>

      {/* the glass card: what happens, the 3 views, the fingerprint */}
      {(() => {
        const p = spring({ frame: frame - 6, fps, config: theme.spring.smooth });
        return (
          <div style={{ position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, opacity: p,
            transform: `translateX(${(1 - p) * 60}px)` }}>
            <Glass style={{ width: "100%", height: "100%" }} />
          </div>
        );
      })()}
      <div style={{ position: "absolute", left: CARD.x + 56, top: CARD.y + 52, width: CARD.w - 112, display: "flex", flexDirection: "column", gap: 16 }}>
        <BlurIn at={10}><Overline>1 · Registo</Overline></BlurIn>
        <BlurIn at={14}><Heading size={62}>Três fotografias do livro</Heading></BlurIn>
        <BlurIn at={18}><Body size={28}>Tiradas por um colega com o telemóvel. Cada fotografia dá uma vista do livro.</Body></BlurIn>
      </div>
      {V3.map((v, i) => {
        const s = slotRect(i);
        const filled = frame >= PRESS_F[i] + LAND;
        const fillP = interpolate(frame, [PRESS_F[i] + LAND - 2, PRESS_F[i] + LAND + 8], [0, 1], { ...clamp, easing: theme.ease.out });
        return (
          <div key={i} style={{ position: "absolute", left: s.x, top: s.y, width: s.w,
            opacity: interpolate(frame, [16 + i * 4, 28 + i * 4], [0, 1], { ...clamp, easing: theme.ease.out }) }}>
            <div style={{ width: s.w, height: s.h, borderRadius: 18, boxSizing: "border-box",
              background: filled ? c.white : a(c.white, 0.45), border: filled ? `1px solid ${a(c.ink, 0.06)}` : `2px dashed ${look.dimLine}`,
              boxShadow: filled ? `0 ${18 * fillP}px 30px -18px ${a(warm.shadow, 0.6)}` : "none" }} />
            <div style={{ marginTop: 10, fontFamily: theme.fonts.mono, fontSize: 18, color: filled ? c.ink : c.inkDim, display: "flex", justifyContent: "space-between" }}>
              <span>vista {i + 1}</span><span style={{ color: c.inkDim }}>foto {mmss(v.t)}</span>
            </div>
          </div>
        );
      })}
      {V3.map((v, i) => {
        const pf = PRESS_F[i];
        if (frame < pf + 2) return null;
        const p = interpolate(frame, [pf + 2, pf + LAND], [0, 1], { ...clamp, easing: theme.ease.inOut });
        const start = boxOnFrame(BOX(v.n), 0.08);
        const r = lerpRect(start, fitIn(slotRect(i), start.w / start.h), p);
        const lift = Math.sin(Math.PI * p);
        return (
          <Img key={i} src={staticFile(v.file)} style={{ position: "absolute", left: r.x, top: r.y - 40 * lift, width: r.w, height: r.h, objectFit: "fill",
            borderRadius: 8, transform: `scale(${1 + 0.06 * lift})`, boxShadow: `0 ${24 * lift + 6}px ${30 * lift + 12}px -10px ${a(warm.shadow, 0.45)}` }} />
        );
      })}
      <div style={{ position: "absolute", left: SLOTS_X, top: SLOTS_Y + SLOT + 70, display: "flex", alignItems: "center", gap: 20 }}>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: 24, fontWeight: 500, color: c.ink, fontVariantNumeric: "tabular-nums",
          opacity: interpolate(frame, [22, 34], [0, 1], clamp) }}>{landed} / 3 vistas</div>
        <div style={{ height: 2, width: 110 * sig, background: c.labs }} />
        <div style={{ opacity: sig, transform: `translateX(${(1 - sig) * -12}px)`, display: "flex", flexDirection: "column", gap: 2 }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, color: c.ink }}>assinatura visual do livro</div>
          <div style={{ fontFamily: theme.fonts.mono, fontSize: 17, color: c.inkDim }}>DINOv2 · 384 números por vista</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
