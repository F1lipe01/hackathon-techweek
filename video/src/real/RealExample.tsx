// Video 2, "the real example": the proof that it runs. The book photographed in the lab (3 photos), recognised on
// the kit camera with the numbers of edge.py's code (recognition.ts, from video/tools/recognise.py), then the
// question, the sensor and the message in the app prototype.
import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import "./fonts";
import { App, APP_CUES, APP_FRAMES } from "./AppScenes";
import { BED, LEAD_FRAMES, ROOM, SFX, TRANS_IN_FRAMES } from "./audio";
import { EndCard, END_FRAMES } from "./EndCard";
import { IDENT_CUES, IDENT_FRAMES, Identificacao } from "./Identificacao";
import { SceneShell } from "./layers";
import { Finish, RoomPlate } from "./stage";
import { Cue } from "./look";
import { Opening, OPENING_CUES, OPENING_FRAMES } from "./Opening";
import { Registo, REGISTO_CUES, REGISTO_FRAMES } from "./Registo";

const OVERLAP = 8;
const SCENES: [React.FC, number, Cue[]][] = [
  [Opening, OPENING_FRAMES, OPENING_CUES],
  [Registo, REGISTO_FRAMES, REGISTO_CUES],
  [Identificacao, IDENT_FRAMES, IDENT_CUES],
  [App, APP_FRAMES, APP_CUES],
  [EndCard, END_FRAMES, []],
];
const STARTS = SCENES.reduce<number[]>((acc, _, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1][1] - OVERLAP], []);

export const DURATION = STARTS[STARTS.length - 1] + SCENES[SCENES.length - 1][1];

const clampBoth = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const CUES: Cue[] = [
  ...SCENES.flatMap(([, , cues], i) => cues.map((q) => ({ ...q, at: STARTS[i] + q.at - LEAD_FRAMES }))),
  // scene transitions: a smooth air move into each scene, a longer one into the app, a swell that stops on the end card
  { at: STARTS[1] + 2, file: "trans" },
  { at: STARTS[2] + 2, file: "trans" },
  { at: STARTS[3] + 2, file: "transLong" },
  { at: STARTS[4] + 8 - TRANS_IN_FRAMES, file: "transIn" },
  { at: STARTS[SCENES.length - 1] + 6, file: "logo" },
];

// the room behind everything: one continuous plate whose focus and wash ease from scene to scene
const SCENE_LOOK = [
  { blur: 3, wash: 0.32 },    // opening
  { blur: 0, wash: 0.16 },    // registo
  { blur: 1, wash: 0.16 },    // identificação
  { blur: 0, wash: 0.14 },    // na app
  { blur: 6, wash: 0.5 },     // end card
];
const PLATE_SECONDS = 15.8;   // length of public/real/bg-home.mp4
const Room: React.FC = () => {
  const frame = useCurrentFrame();
  const keys = STARTS.flatMap((s, i) => (i === 0 ? [0] : [s - 6, s + OVERLAP + 6]));
  const pick = (k: "blur" | "wash") => STARTS.flatMap((_, i) => (i === 0 ? [SCENE_LOOK[0][k]] : [SCENE_LOOK[i - 1][k], SCENE_LOOK[i][k]]));
  const ease = { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: theme.ease.inOut } as const;
  const t = frame / DURATION;
  return (
    <RoomPlate rate={PLATE_SECONDS / (DURATION / theme.fps)} blur={interpolate(frame, keys, pick("blur"), ease)} wash={interpolate(frame, keys, pick("wash"), ease)}
      zoom={1.08 + 0.08 * t} x={30 - 60 * t} />
  );
};

export const RealExample: React.FC = () => (
  <AbsoluteFill>
    <Room />
    {SCENES.map(([Scene, dur], i) => (
      <Sequence key={i} from={STARTS[i]} durationInFrames={dur} premountFor={30}>
        <SceneShell dur={dur} enter={i === 0 ? 1 : 12} exit={i === SCENES.length - 1 ? 1 : 10}>
          <Scene />
        </SceneShell>
      </Sequence>
    ))}
    <Finish />
    <Audio src={staticFile(ROOM.file)} loop
      volume={(f) => ROOM.volume * interpolate(f, [0, 30, DURATION - 30, DURATION], [0, 1, 1, 0], clampBoth)} />
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
