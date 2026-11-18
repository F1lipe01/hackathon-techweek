// The film's timeline, in beats of the music bed (public/audio/manifest.json). Every shot lasts a whole number of
// beats, so every cut lands on a beat; the bed starts MUSIC_LEAD beats into its own track, so that the end of the
// white-out (shot "turn") falls exactly on the bed's lift and the end card holds its resolve.
export const FPS = 30;

// "bed-fast": 120 BPM (a beat is exactly 15 frames), downbeats every 2,0 s from 0; the beat drops at 8 s (beat 16),
// a breakdown at 40 s (beat 80), the lift at 56 s (beat 112), the final hit at 88 s (beat 176), silent from 92,5 s.
// (Fallback: "bed-presentation", 109 BPM, grid from 0,133 s, lift at beat 96.)
export const BED = { name: "bed-fast", bpm: 120, gridOffsetS: 0, liftBeat: 112 } as const;
export const BEAT_S = 60 / BED.bpm;
export const BEAT_F = BEAT_S * FPS;

// shots and their length in beats (≈ 0,55 s each)
const SHOTS: [string, number][] = [
  ["montage", 11], // one shot per beat over the rising intro, a boom on every cut
  ["stop", 1], // the stop hit and a beat of silence, just before the drop
  ["brand", 12], // on the drop
  ["register", 16],
  ["ask", 20],
  ["leave", 16],
  ["how", 20], // the breakdown
  ["turn", 12], // ends on the lift
  ["cat", 14],
  ["dog", 10],
  ["elder", 20],
  ["night", 20],
  ["end", 9], // on the final hit, until the bed falls silent
];

const startBeat: Record<string, number> = {};
const lenBeats: Record<string, number> = {};
SHOTS.reduce((b, [n, len]) => {
  startBeat[n] = b;
  lenBeats[n] = len;
  return b + len;
}, 0);
export const TOTAL_BEATS = SHOTS.reduce((s, [, l]) => s + l, 0);

/** Film beat n, in frames (film beats start at frame 0). */
export const beatFrame = (n: number) => Math.round(n * BEAT_F);
export const SHOT_START: Record<string, number> = Object.fromEntries(SHOTS.map(([n]) => [n, beatFrame(startBeat[n])]));
export const SHOT_FRAMES: Record<string, number> = Object.fromEntries(
  SHOTS.map(([n]) => [n, beatFrame(startBeat[n] + lenBeats[n]) - beatFrame(startBeat[n])]),
);
export const SHOT_ORDER = SHOTS.map(([n]) => n);
export const TOTAL_FRAMES = beatFrame(TOTAL_BEATS);

/** Frame, inside a shot, of its n-th beat. */
export const onBeat = (shot: string, n: number) => beatFrame(startBeat[shot] + n) - SHOT_START[shot];

/** Where the bed starts playing (seconds into its file): film beat (turn end) = the bed's lift. */
export const MUSIC_LEAD = BED.liftBeat - (startBeat.turn + lenBeats.turn);
export const MUSIC_START_S = BED.gridOffsetS + MUSIC_LEAD * BEAT_S;
/** The silent beat after the montage. */
export const STOP = { from: SHOT_START.stop, to: SHOT_START.brand };
