// 0 · Opening: the bright home, defocused; what this is, where and when, and the book.
import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import { Body, Overline } from "./layers";
import { Cue, look } from "./look";
import { BlurIn } from "./stage";

const { c } = look;

export const OPENING_FRAMES = 90;
export const OPENING_CUES: Cue[] = [];

export const Opening: React.FC = () => (
  <AbsoluteFill>
    <AbsoluteFill style={{ padding: "0 170px", justifyContent: "center" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 26, maxWidth: 1400 }}>
        <BlurIn at={2}><Overline>Laboratório · 18 nov 2026</Overline></BlurIn>
        <BlurIn at={6} len={22}>
          <div style={{ fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 150, lineHeight: 1, letterSpacing: "-0.045em", color: c.ink }}>
            Exemplo real
          </div>
        </BlurIn>
        <BlurIn at={14}>
          <Body size={38} style={{ color: c.ink }}>
            <i>O ano da morte de Ricardo Reis</i>, de José Saramago: fotografado num telemóvel,
            <br />reconhecido pela câmara do kit.
          </Body>
        </BlurIn>
      </div>
    </AbsoluteFill>
  </AbsoluteFill>
);
