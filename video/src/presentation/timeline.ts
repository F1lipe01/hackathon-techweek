// The film's timeline, storyboard v5.1 (video/storyboard/index.html). 30 fps on the "bed-fast" music bed: 120 BPM, a beat
// is 15 frames, a bar (4 beats) is 2 s. Every shot starts on a beat and almost every one on a bar line.
export const FPS = 30;
export const BEAT = 15; // frames
export const BAR = 60; // frames
export const sec = (s: number) => Math.round(s * FPS);

/** Each shot: its id in the storyboard and its length in seconds. s14 (the red light) and s22 (the child) are out. */
const SHOTS: [string, number][] = [
  ["s01", 2], ["s02", 2], ["s03", 2], ["s05", 2], // act 1: four steady moments, one bar each
  ["s06", 3.5], ["s07", 0.5], // act 2: the questions stack up, then a silent stop
  ["s08", 8], // act 3: the drop
  ["s09", 8], ["s10", 8], ["s11", 4], ["s12", 4], ["s13", 6], // act 4: the wallet
  ["s15", 8], // act 5: how it works
  ["s16", 2], ["s17", 8], ["s19", 4], ["s20", 4], ["s21", 8], // act 6: the home understands
  ["s23", 6], // act 7: the end card (three bars: 1 s carried in, the move up and the endorsement, 3,5 s still)
];

export const SHOT_START: Record<string, number> = {};
export const SHOT_FRAMES: Record<string, number> = {};
let t = 0;
for (const [id, s] of SHOTS) {
  SHOT_START[id] = sec(t);
  SHOT_FRAMES[id] = sec(t + s) - sec(t);
  t += s;
}
export const SHOT_ORDER = SHOTS.map(([id]) => id);
export const TOTAL_FRAMES = sec(t);

/**
 * The music: bed-fast's drop (8,0 s into its file) lands on act 3 (film 12,0 s), so the file runs 4 s behind the film.
 * The first two bars of its intro are played twice (film 0–4 s and 4–8 s; the intro is level and repeats by bar), it is
 * cut for the half-second stop, and one phrase (file 76–84 s, an inaudible edit) is skipped so that the bed's final hit
 * (file 88 s) lands on the end card (film 84 s).
 */
export const MUSIC = {
  file: "audio/music/bed-fast.wav",
  segments: [
    // [film from (s), film to (s), file from (s)]
    [0, 4, 0],
    [4, 11.5, 0],
    [12, 80, 8],
    [80, 90, 84],
  ] as [number, number, number][],
};
