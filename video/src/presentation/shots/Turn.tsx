// Shot 8. The turn into the safety section: a white-out, then one line, word by word (the second and last word
// reveal), over the riser into the music's lift.
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { Title } from "../type";
import { Flash, Paper, ramp } from "../ui";
import { Sfx } from "../sound";
import { SHOT_FRAMES } from "../timeline";

export const TURN_FRAMES = SHOT_FRAMES.turn;

export const Turn: React.FC = () => (
  <AbsoluteFill>
    <Paper />
    <Sfx at={TURN_FRAMES - 84} role="riser" volume={0.32} lead={0} />
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", transform: `scale(${1 + 0.05 * ramp(useCurrentFrame(), 0, TURN_FRAMES, theme.ease.inOut)})` }}>
      <Title text="Ninguém configura nada. A app percebe a casa." size={70} max={1720} at={10} entrance="words" hero="percebe" align="center" />
    </AbsoluteFill>
    <Flash at={0} length={16} peak={1} />
  </AbsoluteFill>
);
