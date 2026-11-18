// Shared building blocks for video 2: the five-layer stack, entrances, scene shell, type.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { clamp, look } from "./look";

const { c, a } = look;

export const BgMesh: React.FC = () => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 60) * 50;
  const d2 = Math.cos(frame / 75) * 40;
  return (
    <AbsoluteFill style={{ background: c.bg }}>
      <div style={{ position: "absolute", width: 1300, height: 1300, borderRadius: "50%", top: -560, left: -380 + d1,
        filter: "blur(60px)", background: `radial-gradient(circle, ${a(c.labs, 0.14)}, transparent 62%)` }} />
      <div style={{ position: "absolute", width: 1000, height: 1000, borderRadius: "50%", bottom: -480, right: -300 - d2,
        filter: "blur(70px)", background: `radial-gradient(circle, ${a(c.teal, 0.12)}, transparent 65%)` }} />
    </AbsoluteFill>
  );
};

export const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ backgroundColor: c.labsDeep, mixBlendMode: "soft-light", opacity: 0.06 }} />
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${a(c.ink, 0.04)}, transparent 25%, transparent 75%, ${a(c.ink, 0.08)})` }} />
  </AbsoluteFill>
);

const NOISE = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;

export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", backgroundImage: NOISE, backgroundSize: "220px",
      backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`, opacity: 0.045, mixBlendMode: "multiply" }} />
  );
};

export const Vignette: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none",
    background: `radial-gradient(ellipse at center, transparent 58%, ${a(c.ink, 0.13)} 100%)` }} />
);

/** Entrance: opacity + rise + scale, on a spring. */
export const Rise: React.FC<{ delay?: number; y?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  delay = 0, y = 34, children, style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  return (
    <div style={{ opacity: p, transform: `translateY(${interpolate(p, [0, 1], [y, 0])}px) scale(${interpolate(p, [0, 1], [0.96, 1])})`,
      ...style }}>{children}</div>
  );
};

/** A scene's wrapper: a short scale-through entrance and a faster exit. */
export const SceneShell: React.FC<{ dur: number; children: React.ReactNode; enter?: number; exit?: number; delay?: number }> = ({
  dur, children, enter = 10, exit = 8, delay = 3,
}) => {
  const frame = useCurrentFrame();
  const pin = enter <= 1 ? 1 : interpolate(frame, [delay, delay + enter], [0, 1], { ...clamp, easing: theme.ease.out });
  const pout = interpolate(frame, [dur - exit, dur], [0, 1], { ...clamp, easing: theme.ease.in });
  const scale = interpolate(pin, [0, 1], [0.99, 1]);
  return (
    <AbsoluteFill style={{ opacity: pin * (1 - pout), transform: `scale(${scale})` }}>
      {children}
    </AbsoluteFill>
  );
};

export const Overline: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = c.labsDeep }) => (
  <div style={{ fontFamily: theme.fonts.mono, fontSize: 22, fontWeight: 500, letterSpacing: "0.08em",
    textTransform: "uppercase", color }}>{children}</div>
);

export const Heading: React.FC<{ children: React.ReactNode; size?: number; style?: React.CSSProperties }> = ({
  children, size = 64, style,
}) => (
  <div style={{ fontFamily: theme.fonts.display, fontWeight: 600, fontSize: size, lineHeight: 1.06,
    letterSpacing: "-0.025em", color: c.ink, ...style }}>{children}</div>
);

export const Body: React.FC<{ children: React.ReactNode; size?: number; style?: React.CSSProperties }> = ({
  children, size = 28, style,
}) => (
  <div style={{ fontFamily: theme.fonts.display, fontWeight: 400, fontSize: size, lineHeight: 1.35, color: c.inkDim, ...style }}>
    {children}
  </div>
);

/** Small rounded label. */
export const Chip: React.FC<{ children: React.ReactNode; bg?: string; color?: string; style?: React.CSSProperties; mono?: boolean }> = ({
  children, bg = c.white, color = c.ink, style, mono,
}) => (
  <div style={{ display: "inline-flex", alignItems: "center", gap: 10, padding: "9px 16px", borderRadius: 999, background: bg,
    color, fontFamily: mono ? theme.fonts.mono : theme.fonts.display, fontSize: 20, fontWeight: 500,
    boxShadow: `0 6px 18px -8px ${a(c.ink, 0.3)}`, border: look.cardBorder, whiteSpace: "nowrap", ...style }}>{children}</div>
);

/** Text typed in: characters revealed over `per` frames each, from `start`. */
export const Typed: React.FC<{ text: string; start: number; cps?: number; style?: React.CSSProperties; caret?: boolean }> = ({
  text, start, cps = 1.6, style, caret,
}) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor((frame - start) * cps)));
  if (frame < start) return null;
  const typing = n < text.length;
  return (
    <span style={style}>
      {text.slice(0, n)}
      {caret && typing ? <span style={{ opacity: 0.7 }}>▌</span> : null}
    </span>
  );
};
