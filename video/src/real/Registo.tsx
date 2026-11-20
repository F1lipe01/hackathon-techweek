// 1 · Registo: the team's phone recording, three clean passages at real speed (no fingers on the lens), in a
// modern phone over the bright home. At each photo the phone holds the captured frame and that photo's crop glides,
// in one eased move, into its slot of the fingerprint (R.views3).
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { VideoAt } from "./devices";
import { Body, Heading, Overline } from "./layers";
import { clamp, Cue, look, mmss, warm } from "./look";
import { R } from "./recognition";
import { BlurIn, ContactShadow, Glass, ModernPhone } from "./stage";

const { c, a } = look;

// public/real/phone-3seg-2x.mp4 holds frames 12–68, 667–719 and 1059–1166 of footage/phone-photos.mp4, joined and
// upscaled 2x with lanczos and light sharpening by video/tools/prep-real.sh.
const CLIP = "real/phone-3seg-2x.mp4";
const CLIP_RANGES = [
  { from: 12, to: 69, at: 0 },
  { from: 667, to: 720, at: 57 },
  { from: 1059, to: 1167, at: 110 },
];
const clipFrameOf = (src: number) => {
  const r = CLIP_RANGES.find((x) => src >= x.from && src < x.to)!;
  return r.at + src - r.from;
};

// the three passages used (source frames, end excluded), each around one photo. The third stops at 37.0 s, before the
// photographer's fingers come over the lens. `blink` is where the camera app darkens its preview for 3 frames on capture.
const V3 = R.views3.views;
const PASSAGES = [
  { from: 12, to: 69, blink: 44 },
  { from: 667, to: 720, blink: 694 },
  { from: 1066, to: 1111, blink: 1087 },
].map((p, i) => ({ ...p, press: Math.round(V3[i].t * theme.fps) }));
const FLIGHT = 24;   // frames the phone holds the photo while its crop glides to the slot
const LEAD = 10;
const HOLD_END = 18;

// the source frame shown at each output frame
const TIMELINE: number[] = [];
const PRESS_F: number[] = [];
const PASSAGE_START: number[] = [];
for (let i = 0; i < LEAD; i++) TIMELINE.push(PASSAGES[0].from);
PASSAGES.forEach((p) => {
  PASSAGE_START.push(TIMELINE.length);
  for (let s = p.from; s < p.to; s++) {
    if (s === p.press) {
      PRESS_F.push(TIMELINE.length);
      for (let k = 0; k <= FLIGHT; k++) TIMELINE.push(s);
    } else if (s >= p.blink && s < p.blink + 3) {
      TIMELINE.push(p.blink - 1);                    // hold through the camera app's capture blink
    } else {
      TIMELINE.push(s);
    }
  }
});
for (let i = 0; i < HOLD_END; i++) TIMELINE.push(TIMELINE[TIMELINE.length - 1]);
export const REGISTO_FRAMES = TIMELINE.length;
export const REGISTO_CUES: Cue[] = [
  ...PRESS_F.flatMap((pf) => [{ at: pf, file: "shutter" }, { at: pf + 3, file: "slide" }]),
];

// the phone: screen 392 x 850 CSS px (the 2x clip at half size, sharp in 4K), a slight 3D tilt
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
  return { x: PHONE_C.x + (x2 * scale + tx) * s, y: PHONE_C.y + y1 * scale * s };
};

// the crop each view was made from (tight_crop: the box plus 8 % on each side), in px of the 392 x 850 recording
const cropBox = (b: readonly number[]) => {
  const w = b[2] - b[0];
  const h = b[3] - b[1];
  return [Math.max(0, b[0] - w * 0.08), Math.max(65, b[1] - h * 0.08), Math.min(SW, b[2] + w * 0.08), Math.min(589, b[3] + h * 0.08)];
};

export const Registo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = TIMELINE[Math.min(TIMELINE.length - 1, frame)];
  const landed = PRESS_F.filter((pf) => frame >= pf + FLIGHT).length;
  const sig = interpolate(frame, [PRESS_F[2] + FLIGHT + 4, PRESS_F[2] + FLIGHT + 24], [0, 1], { ...clamp, easing: theme.ease.out });

  // the phone arrives turning towards the camera, then rests at a slight angle
  const enter = spring({ frame, fps, config: { damping: 20, stiffness: 70, mass: 1.1 } });
  const rotY = 24 * (1 - enter) + 7 + Math.sin(frame / 60) * 0.8;
  const rotX = 3 + 5 * (1 - enter);
  const tx = -100 * (1 - enter);
  const scale = 0.94 + 0.06 * enter;
  const phoneTransform = `perspective(${PERSP}px) translateX(${tx}px) rotateY(${rotY}deg) rotateX(${rotX}deg) scale(${scale})`;

  const boxOnFrame = (b: readonly number[]): Rect => {
    const p0 = project(b[0] - SW / 2, b[1] - SH / 2, rotY, rotX, scale, tx);
    const p1 = project(b[2] - SW / 2, b[3] - SH / 2, rotY, rotX, scale, tx);
    return { x: p0.x, y: p0.y, w: p1.x - p0.x, h: p1.y - p0.y };
  };
  const card = spring({ frame: frame - 6, fps, config: { damping: 20, stiffness: 80, mass: 1 } });

  return (
    <AbsoluteFill>

      <ContactShadow x={PHONE_C.x + tx + 16} y={PHONE_C.y + SH / 2 + 46} w={460} opacity={0.4 * enter} />
      <div style={{ position: "absolute", left: PHONE_C.x - (SW + 2 * BEZEL) / 2, top: PHONE_C.y - (SH + 2 * BEZEL) / 2,
        transform: phoneTransform, opacity: interpolate(enter, [0, 0.25], [0, 1], clamp), filter: `drop-shadow(0 50px 50px ${a(warm.shadow, 0.35)})` }}>
        <ModernPhone w={SW} h={SH}>
          <VideoAt src={CLIP} second={clipFrameOf(src) / fps} />
          {/* while its crop glides out, the photo's place on the screen is veiled, so the book is never seen twice */}
          {PRESS_F.map((pf, i) => {
            const o = interpolate(frame, [pf, pf + 6, pf + FLIGHT - 2, pf + FLIGHT + 6], [0, 0.55, 0.55, 0], { ...clamp, easing: theme.ease.inOut });
            if (o <= 0) return null;
            const [x0, y0, x1, y1] = cropBox(R.views[V3[i].n - 1].box_phone_px);
            return <div key={i} style={{ position: "absolute", left: x0, top: y0, width: x1 - x0, height: y1 - y0, background: c.white, opacity: o, borderRadius: 4 }} />;
          })}
        </ModernPhone>
      </div>

      <div style={{ position: "absolute", left: PHONE_C.x - 170 + tx, top: 52, width: 340, display: "flex", justifyContent: "center", opacity: enter }}>
        <Glass strong style={{ borderRadius: 999, padding: "9px 18px", display: "flex", gap: 12, alignItems: "center",
          fontFamily: theme.fonts.mono, fontSize: 18, color: c.ink, fontVariantNumeric: "tabular-nums" }}>
          <span style={{ width: 9, height: 9, borderRadius: 9, background: c.alert }} />
          <span>telemóvel {mmss(src / fps)}</span>
          <span style={{ color: c.inkDim }}>tempo real</span>
        </Glass>
      </div>

      <div style={{ position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, opacity: card, transform: `translateX(${(1 - card) * 50}px)` }}>
        <Glass style={{ width: "100%", height: "100%" }} />
      </div>
      <div style={{ position: "absolute", left: CARD.x + 56, top: CARD.y + 52, width: CARD.w - 112, display: "flex", flexDirection: "column", gap: 16 }}>
        <BlurIn at={10}><Overline>1 · Registo</Overline></BlurIn>
        <BlurIn at={14}><Heading size={62}>Três fotografias do livro</Heading></BlurIn>
        <BlurIn at={18}><Body size={28}>Tiradas por um colega com o telemóvel. Cada fotografia dá uma vista do livro.</Body></BlurIn>
      </div>
      {V3.map((v, i) => {
        const s = slotRect(i);
        const filled = frame >= PRESS_F[i] + FLIGHT;
        const fillP = interpolate(frame, [PRESS_F[i] + FLIGHT - 4, PRESS_F[i] + FLIGHT + 8], [0, 1], { ...clamp, easing: theme.ease.out });
        return (
          <div key={i} style={{ position: "absolute", left: s.x, top: s.y, width: s.w,
            opacity: interpolate(frame, [16 + i * 4, 28 + i * 4], [0, 1], { ...clamp, easing: theme.ease.out }) }}>
            <div style={{ width: s.w, height: s.h, borderRadius: 18, boxSizing: "border-box",
              background: a(c.white, 0.45 + 0.55 * fillP), border: filled ? `1px solid ${a(c.ink, 0.06)}` : `2px dashed ${look.dimLine}`,
              boxShadow: `0 ${18 * fillP}px 30px -18px ${a(warm.shadow, 0.6 * fillP)}` }} />
            <div style={{ marginTop: 10, fontFamily: theme.fonts.mono, fontSize: 18, color: filled ? c.ink : c.inkDim, display: "flex", justifyContent: "space-between" }}>
              <span>vista {i + 1}</span><span style={{ color: c.inkDim }}>foto {mmss(v.t)}</span>
            </div>
          </div>
        );
      })}
      {V3.map((v, i) => {
        const pf = PRESS_F[i];
        if (frame < pf) return null;
        const p = interpolate(frame, [pf, pf + FLIGHT], [0, 1], { ...clamp, easing: theme.ease.inOut });
        const start = boxOnFrame(cropBox(R.views[v.n - 1].box_phone_px));
        const r = lerpRect(start, fitIn(slotRect(i), start.w / start.h), p);
        const arc = i === 0 ? 0 : -150 * Math.sin(Math.PI * p);       // pass over the slots already filled
        return (
          <Img key={i} src={staticFile(v.file)} style={{ position: "absolute", left: r.x, top: r.y + arc, width: r.w, height: r.h, objectFit: "fill",
            borderRadius: 4 + 4 * p, boxShadow: `0 ${16 * Math.sin(Math.PI * p) + 4}px ${24 * Math.sin(Math.PI * p) + 10}px -10px ${a(warm.shadow, 0.4)}` }} />
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
