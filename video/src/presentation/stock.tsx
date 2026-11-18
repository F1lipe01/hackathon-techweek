// Licensed stock clips (public/stock/) and their real OWLv2 boxes (public/stock/boxes/<clip>.json, sampled every
// 0,5 s, interpolated here between samples). Each shot names a slot; SLOTS maps it to a clip once they arrive.
import React from "react";
import { AbsoluteFill, Freeze, OffthreadVideo, Sequence, staticFile, useVideoConfig } from "remotion";
import { Placeholder, useJson } from "./assets";

/** Which delivered clip (public/stock/stock.json) plays in which slot of the film, from which second, at what speed. */
export const SLOTS: Record<string, { clip: string; start?: number; rate?: number } | undefined> = {
  // the montage (each shot plays from its own start, set in Montage.tsx)
  "m-keys": { clip: "leaving-home-keys-1", start: 0.3 },
  "m-dog": { clip: "dog-bowl-bright-1", start: 1.0 },
  "m-mother": { clip: "elderly-reading-1", start: 1.0 },
  "m-glasses": { clip: "montage-sunglasses", start: 2.0 },
  "m-plant": { clip: "montage-plant", start: 2.0 },
  "m-pills": { clip: "montage-pillbox", start: 2.0 },
  "m-cat": { clip: "montage-cats-sofa", start: 1.0 },
  "m-parcel": { clip: "montage-parcel", start: 2.0 },
  "m-kettle": { clip: "older-kitchen-1", start: 0.4 },
  "m-door": { clip: "leaving-home-keys-2", start: 2.0 },
  // the story
  "hall-keys": { clip: "leaving-home-keys-1", start: 0.0 }, // the keys on the hall table, before the hand comes in (held as a still)
  "keys-shown": { clip: "leaving-home-keys-1", start: 1.6 }, // a hand lifts the keys: shown to the camera
  "living-room": { clip: "establishing-1", start: 0.0 }, // a bright living room, as the phones' backdrop
  "hall": { clip: "leaving-home-1", start: 2.0 }, // the same hall, as a backdrop
  "leave-door": { clip: "leaving-home-1", start: 8.3 }, // from behind, out of the front door
  "phone-hands": { clip: "phone-alert-2", start: 3.0 }, // two hands hold a phone with a blank screen
  "phone-sofa": { clip: "phone-alert-1", start: 1.0 }, // over the shoulder, a phone with a blank screen
  "cat": { clip: "cat-counter-2", start: 0.5 }, // a black cat on a bright kitchen counter
  "dog-home": { clip: "dog-bowl-1", start: 0.0 },
  "elder-tea": { clip: "elderly-tea-1", start: 1.2 }, // an older woman drinks tea by a bright window
  "elder-reading": { clip: "elderly-reading-1", start: 4.0 }, // an older woman reads in an armchair by the window
  "kitchen-empty": { clip: "older-kitchen-1", start: 0.4 }, // before anyone comes in (held as a still)
  "garden-night": { clip: "garden-night-1", start: 3.0 }, // a silhouette, detected from 3 s (0,26–0,39)
};

type StockIndex = { clips?: { file: string; width: number; height: number }[] } | null;

export const useStockFile = (name: string) => {
  const index = useJson<StockIndex>("stock/stock.json");
  const slot = SLOTS[name];
  const clip = slot && index?.clips?.find((c) => c.file === `${slot.clip}.mp4`);
  return clip ? { file: `stock/${clip.file}`, start: slot!.start ?? 0, rate: slot!.rate ?? 1 } : null;
};

/** A stock clip, full frame, starting at `from` (scene frame); a placeholder until the clip exists. */
export const StockClip: React.FC<{ name: string; from?: number; note?: string; style?: React.CSSProperties }> = ({ name, from = 0, note, style }) => {
  const { fps } = useVideoConfig();
  const f = useStockFile(name);
  if (!f) return <Placeholder name={name} note={note} />;
  return (
    <AbsoluteFill style={style}>
      <Sequence from={from} layout="none">
        <OffthreadVideo src={staticFile(f.file)} muted playbackRate={f.rate} trimBefore={Math.round(f.start * fps)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />
      </Sequence>
    </AbsoluteFill>
  );
};

/** One frame of a stock clip, held: for calm shots, moved by a smooth push instead of slowed footage. */
export const StockStill: React.FC<{ name: string; frame?: number }> = ({ name, frame = 0 }) => (
  <Freeze frame={frame}>
    <StockClip name={name} />
  </Freeze>
);

/** A box from a stock clip (fractions of the clip's frame) in fractions of the 16:9 frame it fills (object-fit cover). */
export const cover = (b: [number, number, number, number], w: number, h: number): [number, number, number, number] => {
  const a = w / h;
  if (a > 16 / 9) {
    const k = a / (16 / 9);
    return [(b[0] - 0.5) * k + 0.5, b[1], (b[2] - 0.5) * k + 0.5, b[3]];
  }
  const k = 16 / 9 / a;
  return [b[0], (b[1] - 0.5) * k + 0.5, b[2], (b[3] - 0.5) * k + 0.5];
};
