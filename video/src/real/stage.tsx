// The premium stage for video 2: a bright, warm, defocused home behind everything (public/real/bg-home.mp4, made from
// the stock clip establishing-1 by video/tools/prep-real.sh), glass cards, a modern phone with a 3D tilt and a contact
// shadow, a camera-view card with a HUD, lock-on brackets and the finishing layers.
import React from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { clamp, look, warm } from "./look";

const { c, a } = look;

/** The home behind every scene: the plate from `offset` seconds, defocused by `blur` px, with a slow camera drift. */
export const Plate: React.FC<{ offset?: number; blur?: number; zoom?: [number, number]; pan?: [number, number]; wash?: number; dur: number }> = ({
  offset = 0, blur = 12, zoom = [1.06, 1.12], pan = [0, -40], wash = 0.16, dur,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, dur], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const z = zoom[0] + (zoom[1] - zoom[0]) * p;
  const x = pan[0] + (pan[1] - pan[0]) * p;
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: c.bg }}>
      <AbsoluteFill style={{ transform: `translateX(${x}px) scale(${z})`, filter: `blur(${blur}px) brightness(1.06) saturate(1.04)` }}>
        <Sequence from={0} layout="none">
          <OffthreadVideo src={staticFile("real/bg-home.mp4")} muted trimBefore={Math.round(offset * theme.fps)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </Sequence>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: c.white, opacity: wash }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 70% 20%, ${a(warm.light, 0.35)}, transparent 60%)` }} />
    </AbsoluteFill>
  );
};

/** A translucent white card. */
export const Glass: React.FC<{ style?: React.CSSProperties; children?: React.ReactNode; strong?: boolean }> = ({ style, children, strong }) => (
  <div style={{ background: a(c.white, strong ? 0.9 : 0.78), border: `1px solid ${a(c.white, 0.9)}`, borderRadius: 28,
    boxShadow: `0 40px 80px -36px ${a(warm.shadow, 0.55)}, 0 10px 24px -14px ${a(c.ink, 0.18)}`, ...style }}>{children}</div>
);

/** A soft shadow on the floor under a floating object. */
export const ContactShadow: React.FC<{ x: number; y: number; w: number; opacity?: number }> = ({ x, y, w, opacity = 0.35 }) => (
  <div style={{ position: "absolute", left: x - w / 2, top: y - w * 0.06, width: w, height: w * 0.12, borderRadius: "50%",
    background: `radial-gradient(ellipse at center, ${a(warm.shadow, opacity)}, transparent 70%)`, filter: "blur(10px)" }} />
);

/** A modern Android phone: thin black bezels, a light metal rim, a punch-hole camera. Screen size in CSS px. */
export const ModernPhone: React.FC<{ w: number; h: number; children: React.ReactNode }> = ({ w, h, children }) => {
  const bezel = Math.round(w * 0.028);
  const r = Math.round(w * 0.12);
  return (
    <div style={{ position: "relative", width: w + 2 * bezel + 6, height: h + 2 * bezel + 6, borderRadius: r + bezel + 3, padding: 3, boxSizing: "border-box",
      background: `linear-gradient(135deg, ${c.white}, ${a(c.inkDim, 0.55)} 30%, ${a(c.white, 0.9)} 55%, ${a(c.inkDim, 0.6)} 85%)` }}>
      <div style={{ width: "100%", height: "100%", borderRadius: r + bezel, background: c.ink, padding: bezel, boxSizing: "border-box" }}>
        <div style={{ position: "relative", width: w, height: h, borderRadius: r, overflow: "hidden", background: c.ink }}>
          {children}
          <div style={{ position: "absolute", left: w / 2 - 7, top: 12, width: 14, height: 14, borderRadius: 14, background: c.ink,
            boxShadow: `0 0 0 2px ${a(c.white, 0.08)}` }} />
          {/* glass reflection */}
          <div style={{ position: "absolute", inset: 0, background: `linear-gradient(115deg, ${a(c.white, 0.10)}, transparent 32%, transparent 70%, ${a(c.white, 0.05)})` }} />
        </div>
      </div>
      <div style={{ position: "absolute", right: -3, top: h * 0.2, width: 4, height: h * 0.08, borderRadius: 2, background: a(c.inkDim, 0.8) }} />
      <div style={{ position: "absolute", right: -3, top: h * 0.32, width: 4, height: h * 0.13, borderRadius: 2, background: a(c.inkDim, 0.8) }} />
    </div>
  );
};

/** Corner brackets around a rectangle (viewfinder marks or a lock-on). */
export const Brackets: React.FC<{ x: number; y: number; w: number; h: number; len?: number; color?: string; width?: number; opacity?: number }> = ({
  x, y, w, h, len = 22, color = c.white, width = 3, opacity = 1,
}) => {
  const d = `M${x},${y + len} V${y} H${x + len} M${x + w - len},${y} H${x + w} V${y + len} M${x + w},${y + h - len} V${y + h} H${x + w - len} M${x + len},${y + h} H${x} V${y + h - len}`;
  return <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" opacity={opacity} />;
};

/** The finishing layers: a warm grade, light grain and a very soft warm vignette (never dark). */
export const Finish: React.FC = () => {
  const frame = useCurrentFrame();
  const NOISE = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: warm.light, mixBlendMode: "soft-light", opacity: 0.22 }} />
      <AbsoluteFill style={{ backgroundImage: NOISE, backgroundSize: "220px", backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
        opacity: 0.035, mixBlendMode: "overlay" }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, transparent 62%, ${a(warm.shadow, 0.10)} 100%)` }} />
    </AbsoluteFill>
  );
};

/** A blur-in title: opacity, rise and focus together. */
export const BlurIn: React.FC<{ at: number; children: React.ReactNode; len?: number; y?: number; style?: React.CSSProperties }> = ({
  at, children, len = 18, y = 18, style,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + len], [0, 1], { ...clamp, easing: theme.ease.out });
  return <div style={{ opacity: p, filter: p < 1 ? `blur(${(1 - p) * 14}px)` : undefined, transform: `translateY(${(1 - p) * y}px)`, ...style }}>{children}</div>;
};
