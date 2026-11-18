// Video 2, "the real example": the proof that it runs. The book photographed in the lab (3 photos), recognised on
// the kit camera with the numbers of edge.py's code (recognition.ts, from video/tools/recognise.py), then the
// question, the sensor and the message in the app prototype.
import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile } from "remotion";
import "./fonts";
import { App, APP_CUES, APP_FRAMES } from "./AppScenes";
import { BED, SFX } from "./audio";
import { EndCard, END_FRAMES } from "./EndCard";
import { IDENT_CUES, IDENT_FRAMES, Identificacao } from "./Identificacao";
import { BgMesh, Grade, Grain, SceneShell, Vignette } from "./layers";
import { Cue } from "./look";
import { Opening, OPENING_FRAMES } from "./Opening";
import { Registo, REGISTO_CUES, REGISTO_FRAMES } from "./Registo";

const OVERLAP = 8;
const SCENES: [React.FC, number, Cue[]][] = [
  [Opening, OPENING_FRAMES, []],
  [Registo, REGISTO_FRAMES, REGISTO_CUES],
  [Identificacao, IDENT_FRAMES, IDENT_CUES],
  [App, APP_FRAMES, APP_CUES],
  [EndCard, END_FRAMES, []],
];
const STARTS = SCENES.reduce<number[]>((acc, _, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1][1] - OVERLAP], []);

export const DURATION = STARTS[STARTS.length - 1] + SCENES[SCENES.length - 1][1];

const clampBoth = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const CUES: Cue[] = [
  ...SCENES.flatMap(([, , cues], i) => cues.map((q) => ({ ...q, at: STARTS[i] + q.at }))),
  { at: STARTS[SCENES.length - 1] + 2, file: "logo" },
];

export const RealExample: React.FC = () => (
  <AbsoluteFill>
    <BgMesh />
    {SCENES.map(([Scene, dur], i) => (
      <Sequence key={i} from={STARTS[i]} durationInFrames={dur} premountFor={30}>
        <SceneShell dur={dur} enter={i === 0 ? 1 : 10} exit={i === SCENES.length - 1 ? 1 : 8}>
          <Scene />
        </SceneShell>
      </Sequence>
    ))}
    <Grade />
    <Grain />
    <Vignette />
    <Audio src={staticFile(BED.file)} trimBefore={BED.from}
      volume={(f) => BED.volume * interpolate(f, [0, 24, DURATION - 24, DURATION], [0, 1, 1, 0], clampBoth)} />
    {CUES.filter((q) => SFX[q.file]).map((q, i) => (
      <Sequence key={`a${i}`} from={Math.max(0, q.at)} durationInFrames={q.dur ?? 120}>
        <Audio src={staticFile(SFX[q.file].file)}
          volume={(f) => (q.volume ?? 1) * SFX[q.file].volume * (q.dur ? interpolate(f, [q.dur - 5, q.dur], [1, 0], clampBoth) : 1)} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
