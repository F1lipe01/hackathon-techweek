// The film's sound, from public/audio/ (manifest.json): the music bed and the sfx. Every move gets a sound: a boom on
// the montage cuts, a whoosh on camera moves, a swipe on UI slides, a lock-on on each box, a shutter on photos.
// Effects are named by role; each role takes the newest kit's file when the manifest has it (sfx/v2), else the first
// kit's. Effects land 2–3 frames ahead of the picture. The bed is -18 LUFS; the sfx are peak-normalised.
import React from "react";
import { Audio, Sequence, interpolate, staticFile } from "remotion";
import { useJson } from "./assets";
import { BED, FPS, MUSIC_START_S, STOP, TOTAL_FRAMES } from "./timeline";

type Entry = { file: string; duration_s?: number };
export type Manifest = { music?: Record<string, Entry & { bpm?: number; sections_s?: Record<string, number> }>; sfx?: Record<string, Entry>; sfx_v2?: Record<string, Entry>; sfx_v3?: Record<string, Entry> } | null;

export const useManifest = () => useJson<Manifest>("audio/manifest.json");

export type Role =
  | "boom" | "stop" | "swell" | "whoosh" | "whoosh-short" | "whoosh-long" | "whip" | "swipe" | "lockon" | "shutter" | "notify" | "alert"
  | "tap" | "riser" | "typing" | "door" | "tick";

// Candidates for each role, cleanest kit first: "v3:" keys are in the manifest's sfx_v3 (trans, click, slide,
// shutter-soft), "v2:" in sfx_v2, the others in sfx. Each group has a gain. Never used: lockon-1 and lockon-3 (beeps),
// the v2 swipes (squeezes), whoosh-2 (a plastic bag) and whoosh-4.
type Group = { keys: string[]; gain: number };
const ROLE: Record<Role, Group[]> = {
  boom: [{ keys: ["v2:boom-1", "v2:boom-2", "v2:boom-3", "v2:boom-4"], gain: 1 }],
  stop: [{ keys: ["v2:boom-stop"], gain: 1 }],
  swell: [{ keys: ["v3:trans-4"], gain: 1 }], // a rising swell that stops dead: its end is laid on the cut
  whoosh: [{ keys: ["v3:trans-2"], gain: 1 }, { keys: ["v2:whoosh-1"], gain: 0.45 }],
  "whoosh-short": [{ keys: ["v3:trans-1"], gain: 1 }, { keys: ["v2:whoosh-1"], gain: 0.35 }],
  "whoosh-long": [{ keys: ["v3:trans-3"], gain: 1 }, { keys: ["v2:whoosh-1"], gain: 0.35 }],
  whip: [{ keys: ["v3:trans-2"], gain: 1 }, { keys: ["v2:whoosh-1"], gain: 0.5 }],
  swipe: [{ keys: ["v3:slide-1", "v3:slide-2"], gain: 1 }],
  lockon: [{ keys: ["v3:click-1", "v3:click-2", "v3:click-3"], gain: 1 }, { keys: ["v2:tap-2"], gain: 0.7 }],
  shutter: [{ keys: ["v3:shutter-soft"], gain: 1 }, { keys: ["v2:shutter-1"], gain: 0.8 }],
  notify: [{ keys: ["v2:notify-1"], gain: 1 }],
  alert: [{ keys: ["v2:notify-2"], gain: 1 }],
  tap: [{ keys: ["v3:click-1"], gain: 1 }, { keys: ["v2:tap-1", "v2:tap-2"], gain: 1 }],
  riser: [{ keys: ["v2:riser-2"], gain: 0.8 }],
  typing: [{ keys: ["typing-soft"], gain: 1 }],
  door: [{ keys: ["door-open"], gain: 1 }],
  tick: [{ keys: ["v3:click-2"], gain: 1 }, { keys: ["v2:tap-2"], gain: 0.8 }],
};

const entry = (m: Manifest, key: string) => {
  if (key.startsWith("v3:")) return m?.sfx_v3?.[key.slice(3)] ?? null;
  if (key.startsWith("v2:")) return m?.sfx_v2?.[key.slice(3)] ?? null;
  return m?.sfx?.[key] ?? null;
};

const pick = (m: Manifest, role: Role, variant = 0): { e: Entry; gain: number } | null => {
  for (const g of ROLE[role]) {
    const e = entry(m, g.keys[variant % g.keys.length]) ?? g.keys.map((k) => entry(m, k)).find(Boolean);
    if (e) return { e, gain: g.gain };
  }
  return null;
};

export const MusicBed: React.FC = () => {
  const m = useManifest();
  const bed = m?.music?.[BED.name];
  if (!bed) return null;
  const s0 = STOP.from;
  const s1 = STOP.to;
  return (
    <Audio
      src={staticFile(`audio/${bed.file}`)}
      trimBefore={Math.round(MUSIC_START_S * FPS)}
      volume={(f) =>
        interpolate(f, [0, 4, s0 - 2, s0, s1 - 1, s1 + 3, TOTAL_FRAMES - 20, TOTAL_FRAMES], [0, 0.8, 0.8, 0, 0, 0.85, 0.85, 0.7], {
          extrapolateLeft: "clamp", extrapolateRight: "clamp",
        })
      }
    />
  );
};

/** The house's room tone (daytime, bright), looped very low under the whole film (about -30 dB), silent on the stop. */
export const RoomTone: React.FC = () => {
  const m = useManifest();
  const e = m?.sfx_v2?.["room-tone-bright"] ?? m?.sfx?.["room-tone"];
  if (!e) return null;
  return (
    <Audio
      src={staticFile(`audio/${e.file}`)}
      loop
      volume={(f) => (f >= STOP.from && f < STOP.to ? 0 : 0.032)}
    />
  );
};

/** One effect for a role, `lead` frames before the picture's hit at `at` (frames inside the current sequence). */
export const Sfx: React.FC<{ at: number; role: Role; volume?: number; lead?: number; variant?: number }> = ({ at, role, volume = 0.5, lead = 2, variant = 0 }) => {
  const m = useManifest();
  const hit = pick(m, role, variant);
  if (!hit) return null;
  const len = Math.ceil((hit.e.duration_s ?? 3) * FPS) + 4;
  return (
    <Sequence from={Math.max(0, at - lead)} durationInFrames={len} layout="none">
      <Audio src={staticFile(`audio/${hit.e.file}`)} volume={volume * hit.gain} />
    </Sequence>
  );
};
