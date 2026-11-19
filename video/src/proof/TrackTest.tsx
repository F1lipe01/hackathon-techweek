// A test of the screen-replacement pipeline on the synthetic plate (video/tools/synth_plate.py): the tracker, the keyer
// and TrackedScreen together, before any real take exists. Files in public/takes/synth/ (never committed).
import React from "react";
import { AbsoluteFill, getInputProps } from "remotion";
import { TrackedScreen } from "../presentation/tracked";

export const TRACK_TEST_FRAMES = 90;

export const TrackTest: React.FC = () => (
  <AbsoluteFill>
    <TrackedScreen take="takes/synth/synth.mov" track="takes/synth/track.json" keyed="takes/synth/key.webm" from={0}
      rec="register" segs={[[0, 6.0]]} off={(getInputProps() as { off?: string[] }).off ?? []}
      keys={[{ at: 0, ppt: 0, fx: 201, fy: 437 }, { at: 62, ppt: 0, fx: 201, fy: 437 }, { at: 88, ppt: 1.6, fx: 201, fy: 300, cx: 960, cy: 540 }]} />
  </AbsoluteFill>
);
