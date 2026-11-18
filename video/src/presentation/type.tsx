// Titles for the presentation film. Every title is one line: it is measured (canvas, after the fonts load) and the
// render fails if it does not fit its width, so a phrase can never wrap. Each title picks one entrance from a
// varied palette; no two consecutive shots use the same one, and the word-by-word reveal is used at most twice.
import React, { useEffect, useState } from "react";
import { continueRender, delayRender, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { alpha } from "./tokens";
import { clamp, ramp } from "./ui";

export type Entrance = "track" | "wipe" | "rise" | "cut" | "blur" | "words";
export type Exit = "fade" | "cut" | "up";

const widthCache = new Map<string, number>();

/** Width in px of one line of text, measured after the font has loaded. Fails the render if it is wider than `max`. */
export const useOneLine = (text: string, size: number, weight: number, trackingEm: number, max: number, family = "Switzer") => {
  const key = `${family}|${weight}|${size}|${trackingEm}|${text}`;
  const [width, setWidth] = useState<number | null>(widthCache.get(key) ?? null);
  const [handle] = useState(() => (widthCache.has(key) ? null : delayRender(`measure "${text}"`)));
  useEffect(() => {
    if (handle === null) return;
    const font = `${weight} ${size}px ${family}`;
    document.fonts.load(font, text).then(() => {
      const ctx = document.createElement("canvas").getContext("2d")!;
      ctx.font = font;
      (ctx as unknown as { letterSpacing: string }).letterSpacing = `${trackingEm * size}px`;
      const w = ctx.measureText(text).width;
      widthCache.set(key, w);
      setWidth(w);
      continueRender(handle);
    });
  }, [handle, key, text, size, weight, trackingEm, family]);
  if (width !== null && width > max) {
    throw new Error(`Title does not fit on one line: "${text}" needs ${Math.ceil(width)} px at ${size} px, has ${max} px. Cut words.`);
  }
  return width;
};

export const Title: React.FC<{
  text: string;
  size: number;
  max: number;
  at: number;
  entrance: Entrance;
  exitAt?: number;
  exit?: Exit;
  weight?: number;
  color?: string;
  tracking?: number;
  hero?: string;
  align?: "left" | "center";
  style?: React.CSSProperties;
}> = ({ text, size, max, at, entrance, exitAt, exit = "fade", weight = 600, color = theme.colors.ink, tracking = -0.035, hero, align = "left", style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  useOneLine(text, size, weight, tracking, max);
  const t = frame - at;
  if (t < 0) return null;
  if (exitAt !== undefined && exit === "cut" && frame >= exitAt) return null;

  // exit
  const out = exitAt === undefined ? 0 : ramp(frame, exitAt, exitAt + (exit === "up" ? 12 : 9), theme.ease.in);
  if (out >= 1) return null;

  const base: React.CSSProperties = {
    fontFamily: theme.fonts.display, fontSize: size, fontWeight: weight, lineHeight: 1.12, color,
    letterSpacing: `${tracking}em`, whiteSpace: "nowrap", textAlign: align, ...style,
  };
  const heroSplit = (s: string) => {
    if (!hero || !s.includes(hero)) return s;
    const i = s.indexOf(hero);
    return (
      <>
        {s.slice(0, i)}
        <span style={{ color: theme.colors.labs }}>{hero}</span>
        {s.slice(i + hero.length)}
      </>
    );
  };

  let inner: React.ReactNode = heroSplit(text);
  let wrap: React.CSSProperties = {};
  let innerStyle: React.CSSProperties = {};

  if (entrance === "track") {
    const p = ramp(t, 0, 30, theme.ease.out);
    wrap = { opacity: ramp(t, 0, 14, theme.ease.out) };
    innerStyle = { letterSpacing: `${tracking + 0.16 * (1 - p)}em`, filter: `blur(${10 * (1 - p)}px)` };
  } else if (entrance === "wipe") {
    const p = ramp(t, 0, 20, theme.ease.inOut);
    wrap = { clipPath: `inset(-20% ${100 - 100 * p}% -20% 0)` };
    innerStyle = { transform: `translateX(${-24 * (1 - p)}px)` };
  } else if (entrance === "rise") {
    const p = spring({ frame: t, fps, config: theme.spring.smooth });
    wrap = { overflow: "hidden", paddingBottom: size * 0.12, marginBottom: -size * 0.12 };
    innerStyle = { transform: `translateY(${110 * (1 - p)}%)`, display: "inline-block" };
  } else if (entrance === "blur") {
    const p = ramp(t, 0, 28, theme.ease.out);
    wrap = { opacity: ramp(t, 0, 12, theme.ease.out) };
    innerStyle = { filter: `blur(${22 * (1 - p)}px)`, transform: `scale(${1.06 - 0.06 * p})`, display: "inline-block", transformOrigin: align === "center" ? "50% 60%" : "0 60%" };
  } else if (entrance === "words") {
    inner = (
      <span style={{ display: "inline-flex", gap: size * 0.24, justifyContent: align === "center" ? "center" : "flex-start" }}>
        {text.split(" ").map((w, i) => {
          const p = spring({ frame: t - i * 4, fps, config: theme.spring.snappy });
          return (
            <span
              key={i}
              style={{
                display: "inline-block", opacity: interpolate(p, [0, 0.7], [0, 1], clamp),
                transform: `translateY(${size * 0.3 * (1 - p)}px)`, filter: `blur(${6 * (1 - p)}px)`,
                color: hero && w.includes(hero) ? theme.colors.labs : undefined,
              }}
            >
              {w}
            </span>
          );
        })}
      </span>
    );
  }

  const exitStyle: React.CSSProperties =
    exit === "up" ? { clipPath: `inset(-20% 0 ${100 * out}% 0)`, transform: `translateY(${-size * 0.4 * out}px)` } : { opacity: 1 - out, transform: `translateY(${-14 * out}px)` };

  return (
    <div style={{ ...base, ...exitStyle }}>
      <div style={wrap}>
        <span style={innerStyle}>{inner}</span>
      </div>
    </div>
  );
};

/** Small print on a frame: "imagens de arquivo", "proposta", "ilustração". */
export const SmallPrint: React.FC<{ text: string; dark?: boolean; at?: number; style?: React.CSSProperties }> = ({ text, dark, at = 0, style }) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute", display: "flex", alignItems: "center", gap: 10, fontFamily: theme.fonts.mono, fontSize: 18,
        letterSpacing: "0.02em", color: dark ? alpha(theme.colors.white, 0.78) : theme.colors.inkDim,
        opacity: ramp(frame, at, at + 10, theme.ease.out), ...style,
      }}
    >
      <span style={{ width: 7, height: 7, borderRadius: 7, background: dark ? alpha(theme.colors.white, 0.7) : theme.colors.inkDim }} />
      {text}
    </div>
  );
};
