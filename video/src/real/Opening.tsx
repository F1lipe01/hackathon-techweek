// 0 · Opening card: what this is, where and when, and the book.
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { Body, Heading, Overline, Rise } from "./layers";
import { clamp, look } from "./look";

const { c, a } = look;

export const OPENING_FRAMES = 112;

export const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const card = spring({ frame: frame - 10, fps, config: theme.spring.smooth });
  const kb = interpolate(frame, [0, OPENING_FRAMES], [1.04, 1.12], { ...clamp, easing: theme.ease.inOut });
  const pan = interpolate(frame, [0, OPENING_FRAMES], [8, -10], { ...clamp, easing: theme.ease.inOut });
  const breathe = Math.sin(frame / 24) * 4;
  const rule = interpolate(frame, [16, 46], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <AbsoluteFill style={{ padding: "0 170px", flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 26, maxWidth: 980 }}>
        <Rise delay={2}><Overline>Laboratório · 18 nov 2026</Overline></Rise>
        <Rise delay={7}><Heading size={150} style={{ letterSpacing: "-0.04em" }}>Exemplo real</Heading></Rise>
        <div style={{ height: 3, width: 520 * rule, background: c.labs, borderRadius: 2 }} />
        <Rise delay={14}>
          <Body size={36} style={{ color: c.ink }}>
            Um livro: <i>O ano da morte de Ricardo Reis</i>,<br />de José Saramago.
          </Body>
        </Rise>
        <Rise delay={19}>
          <Body size={28}>Fotografado num telemóvel, reconhecido pela câmara do kit.</Body>
        </Rise>
      </div>
      <div style={{ position: "relative", width: 400, height: 540, borderRadius: 28, overflow: "hidden", boxShadow: look.shadow, border: look.cardBorder,
        background: c.white, opacity: card,
        transform: `translateY(${interpolate(card, [0, 1], [60, 0]) + breathe}px) rotate(${interpolate(card, [0, 1], [6, 2.5])}deg) scale(${interpolate(card, [0, 1], [0.92, 1])})` }}>
        <Img src={staticFile("real/views/view-1.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${kb}) translateX(${pan}px)` }} />
        <div style={{ position: "absolute", left: 18, bottom: 18, padding: "7px 13px", borderRadius: 999, background: a(c.ink, 0.72),
          color: c.white, fontFamily: theme.fonts.mono, fontSize: 17 }}>foto 1 · telemóvel</div>
      </div>
    </AbsoluteFill>
  );
};
