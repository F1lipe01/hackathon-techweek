// VIDEO 1, "the presentation": the ThingTracker product film, storyboard v4 (video/STORYBOARD.md).
// Composed at 1920 × 1080, 30 fps; the final is rendered at 4K with --scale=2. Every shot lasts whole beats of the
// music bed (timeline.ts), so every cut lands on a beat; transitions happen inside the shots.
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import "./fonts";
import { theme } from "../theme";
import { Finish } from "./ui";
import { MusicBed, RoomTone } from "./sound";
import { SHOT_FRAMES, SHOT_ORDER, SHOT_START, TOTAL_FRAMES } from "./timeline";
import { Montage, Stop } from "./shots/Montage";
import { Brand } from "./shots/Brand";
import { Register } from "./shots/Register";
import { Ask } from "./shots/Ask";
import { Leave } from "./shots/Leave";
import { Turn } from "./shots/Turn";
import { Cat, Dog, Elder, Night } from "./shots/Safety";
import { How } from "./shots/How";
import { End } from "./shots/End";

const COMPONENTS: Record<string, React.FC> = {
  montage: Montage, stop: Stop, brand: Brand, register: Register, ask: Ask, leave: Leave, turn: Turn,
  cat: Cat, dog: Dog, elder: Elder, night: Night, how: How, end: End,
};

export const DURATION = TOTAL_FRAMES;

export const Presentation: React.FC = () => (
  <AbsoluteFill style={{ background: theme.colors.bg }}>
    {SHOT_ORDER.map((name) => {
      const C = COMPONENTS[name];
      return (
        <Sequence key={name} name={name} from={SHOT_START[name]} durationInFrames={SHOT_FRAMES[name]}>
          <C />
        </Sequence>
      );
    })}
    <Finish />
    <MusicBed />
    <RoomTone />
  </AbsoluteFill>
);
