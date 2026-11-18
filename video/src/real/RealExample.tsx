// Video 2, "the real example": the book photographed in the lab, registered, recognised on the kit camera,
// then asked about and watched by a sensor. Recognition numbers come from video/tools/recognise.py (recognition.ts).
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import "./fonts";
import { Pergunta, PERGUNTA_FRAMES, PERGUNTA_SFX, Sensor, SENSOR_FRAMES, SENSOR_SFX } from "./AppScenes";
import { EndCard, END_FRAMES } from "./EndCard";
import { Identificacao, IDENT_FRAMES, IDENT_SFX } from "./Identificacao";
import { BgMesh, Grade, Grain, SceneShell, Vignette } from "./layers";
import { Cue } from "./look";
import { Opening, OPENING_FRAMES } from "./Opening";
import { Registo, REGISTO_FRAMES, REGISTO_SFX } from "./Registo";

const OVERLAP = 10;
const SCENES: [React.FC, number, Cue[]][] = [
  [Opening, OPENING_FRAMES, []],
  [Registo, REGISTO_FRAMES, REGISTO_SFX],
  [Identificacao, IDENT_FRAMES, IDENT_SFX],
  [Pergunta, PERGUNTA_FRAMES, PERGUNTA_SFX],
  [Sensor, SENSOR_FRAMES, SENSOR_SFX],
  [EndCard, END_FRAMES, []],
];
const STARTS = SCENES.reduce<number[]>((acc, _, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1][1] - OVERLAP], []);

export const DURATION = STARTS[STARTS.length - 1] + SCENES[SCENES.length - 1][1];

// every cue on the video's clock: a soft whoosh into each scene, then the scene's own cues
const CUES: Cue[] = SCENES.flatMap(([, , cues], i) => [
  ...(i > 0 ? [{ at: STARTS[i] - 6, file: "whoosh.wav", volume: 0.18 }] : []),
  ...cues.map((q) => ({ ...q, at: STARTS[i] + q.at })),
]);

export const RealExample: React.FC = () => (
  <AbsoluteFill>
    <BgMesh />
    {SCENES.map(([Scene, dur], i) => (
      <Sequence key={i} from={STARTS[i]} durationInFrames={dur} premountFor={30}>
        <SceneShell dur={dur} enter={i === 0 ? 1 : 14}>
          <Scene />
        </SceneShell>
      </Sequence>
    ))}
    <Grade />
    <Grain />
    <Vignette />
    {CUES.map((q, i) => (
      <Sequence key={`a${i}`} from={Math.max(0, q.at)} durationInFrames={45}>
        <Audio src={staticFile(`real/sfx/${q.file}`)} volume={q.volume ?? 0.5} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
