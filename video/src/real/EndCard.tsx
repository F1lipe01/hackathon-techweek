// 4 · End card.
import React from "react";
import { AbsoluteFill } from "remotion";
import { Body, Heading, Overline, Rise } from "./layers";
import { look } from "./look";

const { c } = look;

export const END_FRAMES = 84;

export const EndCard: React.FC = () => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 24 }}>
    <Rise delay={0} y={14}><Overline>Exemplo real · Laboratório · 18 nov 2026</Overline></Rise>
    <Rise delay={3} y={14}><Heading size={150} style={{ letterSpacing: "-0.045em" }}>ThingTracker</Heading></Rise>
    <Rise delay={7} y={14}><Body size={36} style={{ color: c.ink }}>Equipa IT-Porto · Desafio Altice Labs #3</Body></Rise>
  </AbsoluteFill>
);
