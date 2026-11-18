// Shot 13. The end card, text only: "ThingTracker" and "by Altice Labs".
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { Title } from "../type";
import { Paper, clamp, ramp } from "../ui";
import { SHOT_FRAMES, onBeat } from "../timeline";

export const END_FRAMES = SHOT_FRAMES.end;

export const End: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const B = (n: number) => onBeat("end", n);
  return (
    <AbsoluteFill>
      <Paper />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", transform: `scale(${1 + 0.04 * ramp(frame, 0, END_FRAMES, theme.ease.inOut)})` }}>
        <div style={{ display: "flex", fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 150, letterSpacing: "-0.04em", lineHeight: 1, color: theme.colors.ink }}>
          {"ThingTracker".split("").map((ch, i) => {
            const p = spring({ frame: frame - 2 - i * 1.6, fps, config: theme.spring.snappy });
            return (
              <span key={i} style={{ display: "inline-block", opacity: interpolate(p, [0, 0.6], [0, 1], clamp), transform: `translateY(${28 * (1 - p)}px)`, filter: `blur(${8 * (1 - p)}px)` }}>
                {ch}
              </span>
            );
          })}
        </div>
        <div style={{ height: 30 }} />
        <Title text="by Altice Labs" size={44} max={1200} weight={500} at={B(3)} entrance="track" color={theme.colors.inkDim} tracking={-0.01} align="center" />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
