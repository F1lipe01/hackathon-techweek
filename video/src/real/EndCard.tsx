// 5 · End card.
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { Body, Heading, Overline, Rise } from "./layers";
import { clamp, look } from "./look";

const { c } = look;

export const END_FRAMES = 110;

export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const rule = interpolate(frame, [12, 42], [0, 1], { ...clamp, easing: theme.ease.out });
  const breathe = 1 + Math.sin(frame / 26) * 0.006;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 26 }}>
      <Rise delay={2}><Overline>Exemplo real · Laboratório · 18 nov 2026</Overline></Rise>
      <Rise delay={6}>
        <Heading size={160} style={{ letterSpacing: "-0.045em", transform: `scale(${breathe})` }}>ThingTracker</Heading>
      </Rise>
      <div style={{ height: 3, width: 420 * rule, background: c.labs, borderRadius: 2 }} />
      <Rise delay={14}><Body size={36} style={{ color: c.ink }}>Equipa IT-Porto · Desafio Altice Labs #3</Body></Rise>
    </AbsoluteFill>
  );
};
