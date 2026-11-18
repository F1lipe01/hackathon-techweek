// Shared building blocks of the presentation film: the five-layer stack, text reveals, entrances and exits,
// the phone frame, the ThingTracker mark and the viewfinder brackets.
import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import { alpha, shadow } from "./tokens";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Seconds → frames, from the composition's fps. */
export const useSec = () => {
  const { fps } = useVideoConfig();
  return (s: number) => Math.round(s * fps);
};

/** Eased 0→1 progress between two frames. */
export const useProgress = (from: number, to: number, ease = theme.ease.inOut) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [from, to], [0, 1], { ...clamp, easing: ease });
};

export const ramp = (frame: number, from: number, to: number, ease = theme.ease.inOut) =>
  interpolate(frame, [from, to], [0, 1], { ...clamp, easing: ease });

export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

/* ------------------------------------------------------------------ the five layers */

export const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 90) * 60;
  const d2 = Math.cos(frame / 120) * 50;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <div
        style={{
          position: "absolute", width: 1500, height: 1500, borderRadius: "50%", top: -760, left: -420 + d1,
          filter: "blur(60px)",
          background: `radial-gradient(circle, ${alpha(theme.colors.labs, 0.07)}, transparent 62%)`,
        }}
      />
      <div
        style={{
          position: "absolute", width: 1200, height: 1200, borderRadius: "50%", bottom: -640, right: -300 - d2,
          filter: "blur(70px)",
          background: `radial-gradient(circle, ${alpha(theme.colors.white, 0.9)}, transparent 65%)`,
        }}
      />
    </AbsoluteFill>
  );
};

const NOISE = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;

export const Finish: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* grade: a faint cool cast and a soft top/bottom falloff */}
      <AbsoluteFill style={{ backgroundColor: theme.colors.labs, mixBlendMode: "soft-light", opacity: 0.06 }} />
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${alpha(theme.colors.ink, 0.035)}, transparent 22%, transparent 80%, ${alpha(theme.colors.ink, 0.05)})`,
        }}
      />
      {/* grain */}
      <AbsoluteFill
        style={{
          backgroundImage: NOISE, backgroundSize: "220px",
          backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
          opacity: 0.045, mixBlendMode: "multiply",
        }}
      />
      {/* vignette */}
      <AbsoluteFill
        style={{ background: `radial-gradient(ellipse at center, transparent 58%, ${alpha(theme.colors.ink, 0.1)} 100%)` }}
      />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ entrances and exits */

export const Entrance: React.FC<{
  delay?: number; rise?: number; children: React.ReactNode; style?: React.CSSProperties;
}> = ({ delay = 0, rise = 36, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  return (
    <div
      style={{
        opacity: interpolate(p, [0, 0.6], [0, 1], clamp),
        transform: `translateY(${interpolate(p, [0, 1], [rise, 0])}px) scale(${interpolate(p, [0, 1], [0.96, 1])})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Exit of a whole scene in its last frames: faster than the entrances, eased in. */
export const SceneExit: React.FC<{ duration: number; length?: number; children: React.ReactNode }> = ({
  duration, length = 12, children,
}) => {
  const frame = useCurrentFrame();
  const t = ramp(frame, duration - length, duration - 1, theme.ease.in);
  return (
    <AbsoluteFill style={{ opacity: 1 - t, transform: `translateY(${-28 * t}px) scale(${1 - 0.015 * t})` }}>
      {children}
    </AbsoluteFill>
  );
};

/** A block that leaves early, before the scene ends (text swaps inside one scene). */
export const Leave: React.FC<{ at: number; length?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({
  at, length = 10, children, style,
}) => {
  const frame = useCurrentFrame();
  const t = ramp(frame, at, at + length, theme.ease.in);
  if (t >= 1) return null;
  return <div style={{ opacity: 1 - t, transform: `translateY(${-22 * t}px)`, ...style }}>{children}</div>;
};

/* ------------------------------------------------------------------ type */

export const WordReveal: React.FC<{
  text: string; delay?: number; per?: number; size: number; weight?: number; color?: string;
  hero?: string[]; lineHeight?: number; style?: React.CSSProperties; font?: string; tracking?: string;
}> = ({ text, delay = 0, per = 4, size, weight = 600, color = theme.colors.ink, hero = [], lineHeight = 1.08, style, font, tracking = "-0.03em" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        display: "flex", flexWrap: "wrap", columnGap: Math.round(size * 0.24), rowGap: 0,
        fontFamily: font ?? theme.fonts.display, fontSize: size, fontWeight: weight, letterSpacing: tracking,
        lineHeight, color, ...style,
      }}
    >
      {text.split(" ").map((word, i) => {
        const p = spring({ frame: frame - delay - i * per, fps, config: theme.spring.snappy });
        const isHero = hero.includes(word);
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: interpolate(p, [0, 0.7], [0, 1], clamp),
              transform: `translateY(${interpolate(p, [0, 1], [size * 0.32, 0])}px)`,
              color: isHero ? theme.colors.labs : undefined,
              filter: `blur(${interpolate(p, [0, 1], [6, 0], clamp)}px)`,
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

/** Chapter label: a short rule and a word, set small above the headline. */
export const Kicker: React.FC<{ n: string; label: string; delay?: number }> = ({ n, label, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  return (
    <div
      style={{
        display: "flex", alignItems: "center", gap: 16, fontFamily: theme.fonts.display, fontSize: 26,
        fontWeight: 500, color: theme.colors.inkDim, letterSpacing: "0.01em",
        opacity: interpolate(p, [0, 0.6], [0, 1], clamp), transform: `translateX(${interpolate(p, [0, 1], [-24, 0])}px)`,
      }}
    >
      <span style={{ fontFamily: theme.fonts.mono, fontSize: 20, color: theme.colors.inkDim }}>{n}</span>
      <span style={{ width: 44 * p, height: 2, background: theme.colors.inkDim, opacity: 0.5 }} />
      <span>{label}</span>
    </div>
  );
};

/* ------------------------------------------------------------------ phone */

const FRAME_W = 1350;
const FRAME_H = 2760;
/** The screen inside img/iphone-frame.svg, as fractions of the frame. */
export const SCREEN = { left: 0.053333, top: 0.025, width: 0.893333, height: 0.95 } as const;

export const phoneWidth = (height: number) => (height * FRAME_W) / FRAME_H;
export const screenSize = (height: number) => ({
  w: phoneWidth(height) * SCREEN.width,
  h: height * SCREEN.height,
});

export const Phone: React.FC<{ height: number; children: React.ReactNode; overlay?: React.ReactNode }> = ({
  height, children, overlay,
}) => {
  const width = phoneWidth(height);
  return (
    <div style={{ position: "relative", width, height }}>
      <div
        style={{
          position: "absolute", inset: "1.2% 1.5%", borderRadius: "17% / 8.4%", boxShadow: shadow.phone,
        }}
      />
      <div
        style={{
          position: "absolute", left: `${SCREEN.left * 100}%`, top: `${SCREEN.top * 100}%`,
          width: `${SCREEN.width * 100}%`, height: `${SCREEN.height * 100}%`,
          borderRadius: "15.837% / 7.284%", overflow: "hidden", background: theme.colors.white,
        }}
      >
        {children}
      </div>
      <Img src={staticFile("img/iphone-frame.svg")} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
      {overlay ? (
        <div
          style={{
            position: "absolute", left: `${SCREEN.left * 100}%`, top: `${SCREEN.top * 100}%`,
            width: `${SCREEN.width * 100}%`, height: `${SCREEN.height * 100}%`,
          }}
        >
          {overlay}
        </div>
      ) : null}
    </div>
  );
};

/* ------------------------------------------------------------------ the mark and the brackets */

/** Four viewfinder corners around a rectangle, drawn in screen pixels. `draw` 0→1 grows the arms. */
export const Brackets: React.FC<{
  x: number; y: number; w: number; h: number; arm: number; stroke: number; color: string; draw?: number; radius?: number;
}> = ({ x, y, w, h, arm, stroke, color, draw = 1, radius }) => {
  const a = Math.max(0.001, arm * draw);
  const r = Math.min(radius ?? arm * 0.36, a);
  const paths = [
    `M ${x} ${y + a} V ${y + r} Q ${x} ${y} ${x + r} ${y} H ${x + a}`,
    `M ${x + w - a} ${y} H ${x + w - r} Q ${x + w} ${y} ${x + w} ${y + r} V ${y + a}`,
    `M ${x} ${y + h - a} V ${y + h - r} Q ${x} ${y + h} ${x + r} ${y + h} H ${x + a}`,
    `M ${x + w} ${y + h - a} V ${y + h - r} Q ${x + w} ${y + h} ${x + w - r} ${y + h} H ${x + w - a}`,
  ];
  return (
    <svg style={{ position: "absolute", inset: 0, overflow: "visible", pointerEvents: "none" }} width="100%" height="100%">
      {paths.map((d, i) => (
        <path key={i} d={d} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" />
      ))}
    </svg>
  );
};

/** The ThingTracker mark (prototype/web/index.html, symbol #mark), with its dot trail animated by `dots` 0→1. */
export const MarkDots: React.FC<{ size: number; dots: number }> = ({ size, dots }) => {
  const d = (i: number) => interpolate(dots, [i * 0.22, i * 0.22 + 0.5], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <circle cx="19" cy="45" r={2.4 * d(0)} fill={theme.colors.labs} opacity={0.35} />
      <circle cx="25.5" cy="38.5" r={3 * d(1)} fill={theme.colors.labs} opacity={0.6} />
      <circle cx="35" cy="29" r={8 * d(2)} fill={theme.colors.ink} />
    </svg>
  );
};

/** The full mark: brackets plus dots, at `size` px. */
export const Mark: React.FC<{ size: number; draw: number; dots: number }> = ({ size, draw, dots }) => {
  const u = size / 64;
  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <Brackets x={7 * u} y={7 * u} w={50 * u} h={50 * u} arm={14 * u} radius={5 * u} stroke={5 * u} color={theme.colors.labs} draw={draw} />
      <MarkDots size={size} dots={dots} />
    </div>
  );
};

/** The wand icon of the Altice app copy's scenario cards (prototype/web/app.js, I.wandC). */
export const Wand: React.FC<{ size: number; strokeColor: string; sparkColor: string }> = ({ size, strokeColor, sparkColor }) => (
  <svg viewBox="0 0 24 24" width={size} height={size}>
    <path d="M3.5 20.5 14 10" stroke={strokeColor} strokeWidth={2.4} strokeLinecap="round" />
    <path d="m16 3 1 2.6 2.6 1-2.6 1-1 2.6-1-2.6-2.6-1 2.6-1Z" fill={sparkColor} />
    <circle cx="20.5" cy="12.5" r="1.2" fill={sparkColor} />
    <circle cx="11" cy="4" r="1" fill={sparkColor} />
  </svg>
);

/** A check mark drawn as a stroke. */
export const Check: React.FC<{ size: number; color: string; draw?: number; stroke?: number }> = ({ size, color, draw = 1, stroke = 3 }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} style={{ overflow: "visible" }}>
    <path
      d="M5 12.5 10 17.5 19 7.5" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round"
      pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw}
    />
  </svg>
);

/** Idle micro-motion for anything on screen for more than two seconds. */
export const useBreath = (period = 30, amp = 3) => {
  const frame = useCurrentFrame();
  return Math.sin(frame / period) * amp;
};

/** A short synthesized sound (public/presentation/sfx), starting 2 frames before the visual hit at `at`. */
export const Sfx: React.FC<{ at: number; name: "whoosh" | "shutter" | "tap" | "chime"; volume?: number }> = ({ at, name, volume = 0.3 }) => (
  <Sequence from={Math.max(0, at - 2)} durationInFrames={30} layout="none">
    <Audio src={staticFile(`presentation/sfx/${name}.wav`)} volume={volume} />
  </Sequence>
);
