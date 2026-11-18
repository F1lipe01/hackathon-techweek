// 9. End card: the mark, the name, the team and the challenge.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { Mark, WordReveal, clamp, ramp } from "../ui";

export const END_FRAMES = 165;

export const End: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const draw = ramp(frame, 4, 26, theme.ease.out);
  const dots = ramp(frame, 18, 40, theme.ease.out);
  const name = spring({ frame: frame - 22, fps, config: theme.spring.smooth });
  const breathe = 1 + Math.sin(frame / 26) * 0.008;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", transform: `scale(${breathe})` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 34 }}>
          <Mark size={150} draw={draw} dots={dots} />
          <div
            style={{
              fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 124, letterSpacing: "-0.035em", color: theme.colors.ink, lineHeight: 1,
              opacity: interpolate(name, [0, 0.6], [0, 1], clamp), transform: `translateX(${interpolate(name, [0, 1], [-30, 0])}px)`,
              filter: `blur(${interpolate(name, [0, 1], [8, 0], clamp)}px)`,
            }}
          >
            ThingTracker
          </div>
        </div>
        <div style={{ height: 56 }} />
        <WordReveal text="Equipa IT-Porto · Desafio Altice Labs #3" size={44} weight={500} delay={40} per={3} tracking="-0.02em" style={{ justifyContent: "center" }} />
        <div style={{ height: 18 }} />
        <WordReveal text="Connected Home, Reimagined: a IA ao serviço da casa" size={30} weight={400} color={theme.colors.inkDim} delay={52} per={2} tracking="-0.01em" style={{ justifyContent: "center" }} />
        <div style={{ height: 10 }} />
        <WordReveal text="Aveiro Tech City Hackathon 2026" size={30} weight={400} color={theme.colors.inkDim} delay={62} per={2} tracking="-0.01em" style={{ justifyContent: "center" }} />
      </div>
    </AbsoluteFill>
  );
};
