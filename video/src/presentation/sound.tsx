// The film's sound (storyboard v5.1): the music bed, room tone, and real-object sounds only on visible changes.
// Every cue is placed so that the file's peak lands one frame after its picture (peak times measured from the files).
// Repeated sounds rotate takes and step their level down. No beeps, chimes or synthesised tones; one riser, under the
// questions, into the stop. Levels are set for a −16 to −14 LUFS mix (measured on the render).
import React from "react";
import { Audio, Sequence, interpolate, staticFile } from "remotion";
import { FPS, MUSIC, SHOT_START, TOTAL_FRAMES, sec } from "./timeline";

/** Each sound: its file and the time of its peak (s), measured from the file. */
const FX = {
  riser: { file: "sfx/v4/riser-air.wav", peak: 3.36, len: 3.5 },
  click1: { file: "sfx/v3/click-1.wav", peak: 0.043, len: 0.15 },
  click2: { file: "sfx/v3/click-2.wav", peak: 0.041, len: 0.1 },
  click3: { file: "sfx/v3/click-3.wav", peak: 0.004, len: 0.15 },
  shutter2: { file: "sfx/v4/shutter-2.wav", peak: 0.045, len: 0.38 },
  shutter3: { file: "sfx/v4/shutter-3.wav", peak: 0.083, len: 0.33 },
  shutterSoft: { file: "sfx/v3/shutter-soft.wav", peak: 0.062, len: 0.54 },
  tap1: { file: "sfx/v4/tap-1.wav", peak: 0.005, len: 0.08 },
  tap2: { file: "sfx/v4/tap-2.wav", peak: 0.007, len: 0.1 },
  typing: { file: "sfx/typing-soft.wav", peak: 0, len: 2.03 },
  air: { file: "sfx/v3/trans-2.wav", peak: 0.375, len: 0.85 },
  door: { file: "sfx/v4/door-1.wav", peak: 0.85, len: 2.66 }, // its peak here is the soft close
  vib1: { file: "sfx/v4/vib-1.wav", peak: 0.223, len: 0.39 },
  vib2: { file: "sfx/v4/vib-2.wav", peak: 0.298, len: 0.72 },
  slide: { file: "sfx/v4/slide-card.wav", peak: 0.286, len: 0.45 },
} as const;
type Fx = keyof typeof FX;

/** [film second of the picture, sound, volume, longest it plays (s)] */
const at = (shot: string, s: number) => SHOT_START[shot] / FPS + s;
const CUES: [number, Fx, number, number?][] = [
  // act 2: the burst's one riser, peaking on the stop
  [at("s07", -0.14), "riser", 0.55],
  // act 3: a soft click on each lock (two takes, the second a step lower)
  [at("s08", 0), "click1", 0.32],
  [at("s08", 0.5), "click3", 0.26],
  // act 4, s09: three shutters (three takes, stepping down), a soft click on "Wallet added"
  [at("s09", 2.0), "shutter2", 0.36],
  [at("s09", 3.0), "shutter3", 0.3],
  [at("s09", 4.0), "shutterSoft", 0.25],
  [at("s09", 4.5), "click2", 0.2],
  // s10: soft typing, the tap on send; the answer arrives silently; an air move as the photo grows
  [at("s10", 0.0), "typing", 0.22, 0.55], // the last letters of the question
  [at("s10", 0.82), "tap1", 0.4],
  [at("s10", 5.35), "air", 0.22],
  // s11: the last letters, the tap on send
  [at("s11", 0.0), "typing", 0.2, 1.2],
  [at("s11", 1.6), "tap2", 0.35],
  // s12: the front door shutting (2,2 s in); the alert's vibration starts on its last beat (a J-cut)
  [at("s12", 2.2), "door", 0.55],
  [at("s12", 3.5), "vib1", 0.3],
  // s13: the vibration as the notification lands
  [at("s13", 0.4), "vib2", 0.32],
  // s17: the lock on the cat, the tap that adds the sensor, the alert's vibration
  [at("s17", 0.5), "click2", 0.2],
  [at("s17", 2.9), "tap1", 0.32],
  [at("s17", 5.2), "tap2", 0.24],
  [at("s17", 6.23), "vib1", 0.26],
  // s20: the noon alert
  [at("s20", 1.7), "vib2", 0.26],
  // s21: the lock on the person, then the phone in the morning
  [at("s21", 0.5), "click1", 0.2],
  [at("s21", 2.62), "tap2", 0.3],
];

const Cue: React.FC<{ t: number; fx: Fx; volume: number; max?: number }> = ({ t, fx, volume, max }) => {
  const f = FX[fx];
  const start = Math.max(0, Math.round((t - f.peak) * FPS) + 1);
  const len = Math.ceil(Math.min(f.len, max ?? Infinity) * FPS) + (max ? 0 : 2);
  return (
    <Sequence from={start} durationInFrames={len} layout="none" name={`sfx ${fx}`}>
      <Audio src={staticFile(`audio/${f.file}`)} volume={(i) => volume * (max ? Math.min(1, (len - i) / 3) : 1)} />
    </Sequence>
  );
};

/** The music bed, cut as timeline.ts says: thin under the opening, building under the questions, silent on the stop. */
const MusicBed: React.FC = () => (
  <>
    {MUSIC.segments.map(([a, b, fileFrom], i) => {
      const from = sec(a), dur = sec(b) - sec(a);
      return (
        <Sequence key={i} from={from} durationInFrames={dur} layout="none" name={`music ${a}–${b} s`}>
          <Audio
            src={staticFile(MUSIC.file)}
            trimBefore={sec(fileFrom)}
            volume={(f) => {
              const t = a + f / FPS;
              const v = interpolate(t, [0, 0.3, 7.6, 8, 11.4, 11.5, 12, 84, 89, 90], [0, 0.8, 0.8, 0.85, 1.05, 0, 1.38, 1.38, 1.38, 0], {
                extrapolateLeft: "clamp", extrapolateRight: "clamp",
              });
              // a 2-frame fade at each edit, so no segment starts or stops with a click
              const edge = Math.min(1, f / 2, (dur - f) / 2);
              return v * Math.max(0, edge);
            }}
          />
        </Sequence>
      );
    })}
  </>
);

/** Room tone: a quiet living room, a kitchen hum on the kitchen shots; also under the half-second stop. */
const RoomTone: React.FC = () => {
  const kitchen = (f: number) => {
    const t = f / FPS;
    const inK = (a: number, b: number) => interpolate(t, [a - 0.1, a, b, b + 0.1], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return Math.max(inK(at("s17", 0), at("s17", 2)), inK(at("s20", 0), at("s20", 1.5)));
  };
  return (
    <>
      <Audio src={staticFile("audio/sfx/v4/room-living.wav")} loop volume={(f) => 0.032 * (1 - kitchen(f)) * (f < TOTAL_FRAMES - 15 ? 1 : (TOTAL_FRAMES - f) / 15)} />
      <Audio src={staticFile("audio/sfx/v4/room-kitchen.wav")} loop volume={(f) => 0.028 * kitchen(f)} />
    </>
  );
};

export const SoundTrack: React.FC = () => (
  <>
    <MusicBed />
    <RoomTone />
    {CUES.map(([t, fx, v, max], i) => (
      <Cue key={i} t={t} fx={fx} volume={v} max={max} />
    ))}
  </>
);
