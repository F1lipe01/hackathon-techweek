// VIDEO 1, "the presentation": the ThingTracker product film, storyboard v5.1 (video/storyboard/index.html).
// 1920 × 1080, 30 fps, 90 s on the bed-fast music bed (120 BPM): every shot starts on a beat (timeline.ts).
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import "./fonts";
import { theme } from "../theme";
import { SoundTrack } from "./sound";
import { SHOT_FRAMES, SHOT_ORDER, SHOT_START, TOTAL_FRAMES } from "./timeline";
import { S01, S02, S03, S05, S06, S07 } from "./shots/Act1";
import { S08 } from "./shots/Drop";
import { S09, S10, S11, S12, S13 } from "./shots/Wallet";
import { S15 } from "./shots/How";
import { S16, S17, S19, S20, S21 } from "./shots/Cases";
import { S23 } from "./shots/End";

const SHOTS: Record<string, React.FC> = { s01: S01, s02: S02, s03: S03, s05: S05, s06: S06, s07: S07, s08: S08, s09: S09, s10: S10, s11: S11, s12: S12, s13: S13, s15: S15, s16: S16, s17: S17, s19: S19, s20: S20, s21: S21, s23: S23 };

export const DURATION = TOTAL_FRAMES;

export const Presentation: React.FC = () => (
  <AbsoluteFill style={{ background: theme.colors.bg }}>
    {SHOT_ORDER.map((id) => {
      const C = SHOTS[id];
      return (
        <Sequence key={id} name={id} from={SHOT_START[id]} durationInFrames={SHOT_FRAMES[id]}>
          <C />
        </Sequence>
      );
    })}
    <SoundTrack />
  </AbsoluteFill>
);
