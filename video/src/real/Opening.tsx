// 0 · Opening card: what this is, where and when, and the book.
import React from "react";
import { AbsoluteFill } from "remotion";
import { Body, Heading, Overline, Rise } from "./layers";
import { look } from "./look";

const { c } = look;

export const OPENING_FRAMES = 84;

export const Opening: React.FC = () => (
  <AbsoluteFill style={{ padding: "0 170px", justifyContent: "center" }}>
    <div style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 1300 }}>
      <Rise delay={0} y={14}><Overline>Laboratório · 18 nov 2026</Overline></Rise>
      <Rise delay={3} y={14}><Heading size={130} style={{ letterSpacing: "-0.04em" }}>Exemplo real</Heading></Rise>
      <Rise delay={7} y={14}>
        <Body size={36} style={{ color: c.ink }}>
          <i>O ano da morte de Ricardo Reis</i>, de José Saramago: fotografado num telemóvel,
          <br />reconhecido pela câmara do kit.
        </Body>
      </Rise>
    </div>
  </AbsoluteFill>
);
