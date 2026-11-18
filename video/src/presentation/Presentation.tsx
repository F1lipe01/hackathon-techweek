// VIDEO 1, "the presentation": the ThingTracker product film (≈ 92 s, 1920 × 1080, 30 fps).
// Scenes overlap by a few frames: each one exits faster than the next one enters.
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import "./fonts";
import { Backdrop, Finish } from "./ui";
import { Opening, OPENING_FRAMES } from "./scenes/Opening";
import { Register, REGISTER_FRAMES } from "./scenes/Register";
import { Find, FIND_FRAMES } from "./scenes/Find";
import { AppScene, APP_FRAMES } from "./scenes/AppScene";
import { Safety, SAFETY_FRAMES } from "./scenes/Safety";
import { Architecture, ARCH_FRAMES } from "./scenes/Architecture";
import { End, END_FRAMES } from "./scenes/End";

const OVERLAP = 10;

const SCENES: { name: string; frames: number; C: React.FC }[] = [
  { name: "Gancho e marca", frames: OPENING_FRAMES, C: Opening },
  { name: "Registar", frames: REGISTER_FRAMES, C: Register },
  { name: "Encontrar", frames: FIND_FRAMES, C: Find },
  { name: "Perguntar e avisar", frames: APP_FRAMES, C: AppScene },
  { name: "A app propõe (segurança)", frames: SAFETY_FRAMES, C: Safety },
  { name: "Arquitetura", frames: ARCH_FRAMES, C: Architecture },
  { name: "Fim", frames: END_FRAMES, C: End },
];

const starts = SCENES.reduce<number[]>((acc, s, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].frames - OVERLAP], []);

/** Where each scene starts, in frames (also used for the report). */
export const SCENE_STARTS = SCENES.map((s, i) => ({ name: s.name, from: starts[i], frames: s.frames }));

export const DURATION = starts[starts.length - 1] + SCENES[SCENES.length - 1].frames;

export const Presentation: React.FC = () => (
  <AbsoluteFill>
    <Backdrop />
    {SCENES.map(({ name, frames, C }, i) => (
      <Sequence key={name} name={name} from={starts[i]} durationInFrames={frames}>
        <C />
      </Sequence>
    ))}
    <Finish />
  </AbsoluteFill>
);
