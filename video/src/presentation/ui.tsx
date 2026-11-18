// Shared building blocks of the presentation film: the finishing layers, the phone frame, the ThingTracker mark and
// brackets, lock-on boxes, the notification card, light leaks and whip-pans.
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { alpha, app, grade, shadow } from "./tokens";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Seconds → frames, from the composition's fps. */
export const useSec = () => {
  const { fps } = useVideoConfig();
  return (s: number) => Math.round(s * fps);
};

export const ramp = (frame: number, from: number, to: number, ease = theme.ease.inOut) =>
  interpolate(frame, [from, to], [0, 1], { ...clamp, easing: ease });

export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

/* ------------------------------------------------------------------ finishing layers */

export const Paper: React.FC<{ tone?: "light" | "dark" }> = ({ tone = "light" }) => {
  const frame = useCurrentFrame();
  const d = Math.sin(frame / 120) * 50;
  const light = tone === "light";
  return (
    <AbsoluteFill style={{ background: light ? theme.colors.bg : theme.colors.ink }}>
      <div
        style={{
          position: "absolute", width: 1600, height: 1600, borderRadius: "50%", top: -820, left: -380 + d, filter: "blur(80px)",
          background: `radial-gradient(circle, ${alpha(light ? theme.colors.labs : theme.colors.labsDeep, light ? 0.06 : 0.25)}, transparent 62%)`,
        }}
      />
    </AbsoluteFill>
  );
};

const NOISE = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;

/** Grain and a soft vignette, above everything. */
export const Finish: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill
        style={{
          backgroundImage: NOISE, backgroundSize: "220px", backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
          opacity: 0.04, mixBlendMode: "overlay",
        }}
      />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, transparent 66%, ${alpha(theme.colors.ink, 0.06)} 100%)` }} />
    </AbsoluteFill>
  );
};

/** A dark gradient at the bottom of footage, for white type. */
export const Scrim: React.FC<{ strength?: number }> = ({ strength = 0.55 }) => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 52%, ${alpha(theme.colors.ink, strength)} 100%)` }} />
);

/** A warm light leak / flash, peaking at `at`. */
export const Flash: React.FC<{ at: number; length?: number; peak?: number; warm?: boolean }> = ({ at, length = 10, peak = 0.85, warm }) => {
  const frame = useCurrentFrame();
  const t = frame - at;
  if (t < -3 || t > length) return null;
  const o = t < 0 ? interpolate(t, [-3, 0], [0, peak], clamp) : interpolate(t, [0, length], [peak, 0], { ...clamp, easing: theme.ease.out });
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none", opacity: o, mixBlendMode: "screen",
        background: warm
          ? `radial-gradient(ellipse at 70% 30%, ${theme.colors.white}, ${alpha(theme.colors.white, 0.6)} 40%, transparent 80%)`
          : theme.colors.white,
      }}
    />
  );
};

/** Whip-pan: the content leaves (or arrives) sideways with motion blur over a few frames around a cut. */
export const useWhip = (duration: number, { inFrames = 0, outFrames = 0, dir = 1 }: { inFrames?: number; outFrames?: number; dir?: number }) => {
  const frame = useCurrentFrame();
  let x = 0;
  let blur = 0;
  if (inFrames > 0 && frame < inFrames) {
    const p = ramp(frame, 0, inFrames, theme.ease.out);
    x = (1 - p) * 1400 * dir;
    blur = (1 - p) * 40;
  }
  if (outFrames > 0 && frame > duration - outFrames) {
    const p = ramp(frame, duration - outFrames, duration, theme.ease.in);
    x = -p * 1400 * dir;
    blur = p * 40;
  }
  return { transform: `translateX(${x}px)`, filter: blur > 0.5 ? `blur(${blur}px)` : undefined } as React.CSSProperties;
};

/* ------------------------------------------------------------------ phone */

const FRAME_W = 1350;
const FRAME_H = 2760;
/** The screen inside img/iphone-frame.svg, as fractions of the frame. */
export const SCREEN = { left: 0.053333, top: 0.025, width: 0.893333, height: 0.95 } as const;
export const phoneWidth = (height: number) => (height * FRAME_W) / FRAME_H;
export const screenSize = (height: number) => ({ w: phoneWidth(height) * SCREEN.width, h: height * SCREEN.height });

export const Phone: React.FC<{ height: number; children: React.ReactNode }> = ({ height, children }) => {
  const width = phoneWidth(height);
  return (
    <div style={{ position: "relative", width, height }}>
      <div style={{ position: "absolute", inset: "1.2% 1.5%", borderRadius: "17% / 8.4%", boxShadow: shadow.phone }} />
      <div
        style={{
          position: "absolute", left: `${SCREEN.left * 100}%`, top: `${SCREEN.top * 100}%`, width: `${SCREEN.width * 100}%`,
          height: `${SCREEN.height * 100}%`, borderRadius: "15.837% / 7.284%", overflow: "hidden", background: theme.colors.white,
        }}
      >
        {children}
      </div>
      <Img src={staticFile("img/iphone-frame.svg")} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
    </div>
  );
};

/* ------------------------------------------------------------------ the mark, brackets and lock-on boxes */

/** Four viewfinder corners around a rectangle, in px. `draw` 0→1 grows the arms. */
export const Brackets: React.FC<{
  x: number; y: number; w: number; h: number; arm: number; stroke: number; color: string; draw?: number; radius?: number; opacity?: number;
}> = ({ x, y, w, h, arm, stroke, color, draw = 1, radius, opacity = 1 }) => {
  const a = Math.max(0.001, arm * draw);
  const r = Math.min(radius ?? arm * 0.36, a);
  const d = [
    `M ${x} ${y + a} V ${y + r} Q ${x} ${y} ${x + r} ${y} H ${x + a}`,
    `M ${x + w - a} ${y} H ${x + w - r} Q ${x + w} ${y} ${x + w} ${y + r} V ${y + a}`,
    `M ${x} ${y + h - a} V ${y + h - r} Q ${x} ${y + h} ${x + r} ${y + h} H ${x + a}`,
    `M ${x + w} ${y + h - a} V ${y + h - r} Q ${x + w} ${y + h} ${x + w - r} ${y + h} H ${x + w - a}`,
  ].join(" ");
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", pointerEvents: "none", opacity }} width={1} height={1}>
      <path d={d} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

export const MarkDots: React.FC<{ size: number; dots: number; ink?: string }> = ({ size, dots, ink = theme.colors.ink }) => {
  const d = (i: number) => interpolate(dots, [i * 0.22, i * 0.22 + 0.5], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <svg viewBox="0 0 64 64" width={size} height={size} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
      <circle cx="19" cy="45" r={2.4 * d(0)} fill={theme.colors.labs} opacity={0.35} />
      <circle cx="25.5" cy="38.5" r={3 * d(1)} fill={theme.colors.labs} opacity={0.6} />
      <circle cx="35" cy="29" r={8 * d(2)} fill={ink} />
    </svg>
  );
};

export const Mark: React.FC<{ size: number; draw: number; dots: number }> = ({ size, draw, dots }) => {
  const u = size / 64;
  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <Brackets x={7 * u} y={7 * u} w={50 * u} h={50 * u} arm={14 * u} radius={5 * u} stroke={5 * u} color={theme.colors.labs} draw={draw} />
      <MarkDots size={size} dots={dots} />
    </div>
  );
};

export type Rect = { x: number; y: number; w: number; h: number };

/** A detection locking on: corners snap in from a wider frame, a brief flash, then the label slides out. */
export const LockBox: React.FC<{ r: Rect; at: number; label: string; color?: string; alertAt?: number; fadeAt?: number; labelBelow?: boolean; labelInside?: boolean; size?: number; strong?: boolean; fast?: boolean }> = ({
  r, at, label, color = theme.colors.labs, alertAt, fadeAt, labelBelow, labelInside, size = 20, strong, fast,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame - at) * (fast ? 2.2 : 1);
  if (t < 0) return null;
  const p = spring({ frame: t, fps, config: theme.spring.snappy });
  const grow = 0.45 * (1 - p);
  const x = r.x - (r.w * grow) / 2;
  const y = r.y - (r.h * grow) / 2;
  const w = r.w * (1 + grow);
  const h = r.h * (1 + grow);
  const alert = alertAt !== undefined ? ramp(frame, alertAt, alertAt + 6, theme.ease.out) : 0;
  const c = alert > 0.5 ? theme.colors.alert : color;
  const fade = fadeAt !== undefined ? 1 - ramp(frame, fadeAt, fadeAt + 10, theme.ease.in) : 1;
  const flash = interpolate(t, [4, 14], [0.32, 0], clamp);
  const lab = ramp(t, 6, 18, theme.ease.out);
  const arm = Math.min(w, h) * 0.28;
  // with no room above the box (it touches the top of the frame), the label sits inside its top-left corner
  const inside = labelInside || (!labelBelow && r.y - size * 1.9 < 8);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: interpolate(p, [0, 0.4], [0, 1], clamp) * fade, pointerEvents: "none", filter: strong ? `drop-shadow(0 0 6px ${alpha(theme.colors.ink, 0.9)})` : undefined }}>
      <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, background: alpha(theme.colors.white, flash), borderRadius: 6 }} />
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, border: `${strong ? 3 : 1.5}px solid ${alpha(c, strong ? 0.9 : 0.55)}`, borderRadius: 6 }} />
      <Brackets x={x} y={y} w={w} h={h} arm={arm} stroke={strong ? 7 : 4.5} radius={6} color={c} />
      <div
        style={{
          position: "absolute", left: inside ? Math.max(r.x, 0) + 14 : r.x - 1, top: inside ? Math.max(r.y, 0) + 14 : labelBelow ? r.y + r.h + 10 : r.y - size * 1.9, padding: `${size * 0.25}px ${size * 0.55}px`,
          borderRadius: 7, background: c, color: theme.colors.white, fontFamily: theme.fonts.mono, fontSize: size, fontWeight: 500, whiteSpace: "nowrap",
          clipPath: `inset(0 ${100 - 100 * lab}% 0 0)`,
        }}
      >
        {label}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ the notification */

/** A phone notification, drawn in the Altice app's style (prototype/web/app.css .toast). */
export const Notice: React.FC<{ at: number; title: string; text: string; thumb?: React.ReactNode; width?: number; tone?: "info" | "safety"; tag?: string; actions?: string[] }> = ({
  at, title, text, thumb, width = 620, tone = "info", tag, actions,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - at;
  if (t < 0) return null;
  const p = spring({ frame: t, fps, config: { damping: 15, stiffness: 150, mass: 0.8 } });
  return (
    <div
      style={{
        width, boxSizing: "border-box", borderRadius: 30, padding: "20px 22px", background: alpha(theme.colors.white, 0.97),
        boxShadow: `0 30px 60px -20px ${alpha(theme.colors.ink, 0.45)}`, display: "grid", gridTemplateColumns: thumb ? "64px 1fr" : "1fr", gap: 16, alignItems: "center",
        opacity: interpolate(p, [0, 0.4], [0, 1], clamp), transform: `translateY(${-70 * (1 - p)}px) scale(${0.94 + 0.06 * p})`,
      }}
    >
      {thumb ? <div style={{ width: 64, height: 64, borderRadius: 14, overflow: "hidden", background: theme.colors.bgAlt }}>{thumb}</div> : null}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
          <span style={{ fontFamily: theme.fonts.app, fontSize: 18, fontWeight: 700, color: app.ink, display: "flex", alignItems: "center", gap: 8 }}>
            {tone === "safety" ? <span style={{ width: 9, height: 9, borderRadius: 9, background: theme.colors.alert }} /> : null}
            {title}
          </span>
          <span style={{ fontFamily: theme.fonts.app, fontSize: 16, fontWeight: 500, color: app.muted }}>{tag ?? "agora"}</span>
        </div>
        <div style={{ fontFamily: theme.fonts.app, fontSize: 23, fontWeight: 600, color: app.ink, lineHeight: 1.25, marginTop: 4 }}>{text}</div>
      </div>
      {actions ? (
        <div style={{ gridColumn: "1 / -1", display: "flex", gap: 10, marginTop: 4, opacity: ramp(t, 8, 18, theme.ease.out) }}>
          {actions.map((a, i) => (
            <div key={a} style={{ flex: 1, height: 46, borderRadius: 999, display: "grid", placeItems: "center", fontFamily: theme.fonts.app, fontSize: 17, fontWeight: 600, color: app.ink, background: i === 0 ? app.teal : app.card, whiteSpace: "nowrap" }}>
              {a}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
};

export const Check: React.FC<{ size: number; color: string; draw?: number; stroke?: number }> = ({ size, color, draw = 1, stroke = 3 }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} style={{ overflow: "visible" }}>
    <path d="M5 12.5 10 17.5 19 7.5" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
  </svg>
);

/* ------------------------------------------------------------------ daylight, homes and phones */

/** Wraps footage in the daylight grade: lifted, a touch warm, never moody. */
export const Daylight: React.FC<{ lift?: number; children: React.ReactNode }> = ({ lift = 1.08, children }) => (
  <AbsoluteFill>
    <AbsoluteFill style={{ filter: `brightness(${lift}) saturate(1.04) contrast(0.97)` }}>{children}</AbsoluteFill>
    <AbsoluteFill style={{ background: alpha(grade.warm, 0.14), mixBlendMode: "soft-light", pointerEvents: "none" }} />
  </AbsoluteFill>
);

/** A bright real home, out of focus, drifting slowly: the stage for the phones. */
export const HomeBackdrop: React.FC<{ children: React.ReactNode; blur?: number }> = ({ children, blur = 22 }) => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 18;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg, overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(1.12) translateX(${drift}px)`, filter: `blur(${blur}px) brightness(1.12) saturate(0.95)` }}>{children}</AbsoluteFill>
      <AbsoluteFill style={{ background: alpha(theme.colors.white, 0.18) }} />
    </AbsoluteFill>
  );
};

/** A phone floating in the room: a slight 3D tilt that settles, a soft contact shadow, and the camera's move. */
export const FloatPhone: React.FC<{
  height: number; x: number; y: number; at?: number; tiltFrom?: { y: number; x: number }; push?: number; origin?: string; children: React.ReactNode;
}> = ({ height, x, y, at = 0, tiltFrom = { y: -26, x: 10 }, push = 1, origin = "50% 50%", children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: { damping: 18, stiffness: 70, mass: 1.1 } });
  const idleY = Math.sin(frame / 46) * 1.6 * p;
  const idleX = Math.cos(frame / 60) * 1.0 * p;
  const w = phoneWidth(height);
  return (
    <div
      style={{
        position: "absolute", left: x - w / 2, top: y - height / 2, width: w, height, transformOrigin: origin,
        transform: `perspective(2400px) translateY(${120 * (1 - p)}px) rotateY(${tiltFrom.y * (1 - p) + idleY - 4}deg) rotateX(${tiltFrom.x * (1 - p) + idleX + 2}deg) scale(${(0.9 + 0.1 * p) * push})`,
        opacity: interpolate(p, [0, 0.25], [0, 1], clamp),
      }}
    >
      <div style={{ position: "absolute", left: "8%", right: "8%", bottom: -height * 0.05, height: height * 0.08, borderRadius: "50%", background: alpha(theme.colors.ink, 0.28), filter: "blur(28px)" }} />
      <Phone height={height}>{children}</Phone>
    </div>
  );
};

/** A box keyframed by hand against the footage: [t (clip seconds), x0, y0, x1, y1] in frame fractions. */
export type Track = [number, number, number, number, number][];
export const trackAt = (track: Track, t: number): Rect => {
  let i = 0;
  while (i < track.length - 2 && track[i + 1][0] <= t) i++;
  const a = track[i];
  const b = track[Math.min(i + 1, track.length - 1)];
  const u = b[0] > a[0] ? Math.min(1, Math.max(0, (t - a[0]) / (b[0] - a[0]))) : 0;
  const q = [1, 2, 3, 4].map((j) => a[j] + (b[j] - a[j]) * u);
  return { x: q[0] * 1920, y: q[1] * 1080, w: (q[2] - q[0]) * 1920, h: (q[3] - q[1]) * 1080 };
};
