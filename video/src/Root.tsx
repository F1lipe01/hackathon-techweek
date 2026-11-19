// Two videos, each in its own folder and owned by one editor: src/presentation (video 1, the product presentation)
// and src/real (video 2, the real example in the lab). Each module exports its component and its DURATION in frames.
import React from "react";
import { Composition } from "remotion";
import { theme } from "./theme";
import { Presentation, DURATION as PRESENTATION_FRAMES } from "./presentation/Presentation";
import { RealExample, DURATION as REAL_FRAMES } from "./real/RealExample";
import { TrackTest, TRACK_TEST_FRAMES } from "./proof/TrackTest";
import { ProofCamera, PROOF_FRAMES } from "./proof/ProofCamera";
import { FilmV7, FILM_FRAMES } from "./film/FilmV7";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Presentation" component={Presentation} durationInFrames={PRESENTATION_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="RealExample" component={RealExample} durationInFrames={REAL_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="TrackTest" component={TrackTest} durationInFrames={TRACK_TEST_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="ProofCamera" component={ProofCamera} durationInFrames={PROOF_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="FilmV7" component={FilmV7} durationInFrames={FILM_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
  </>
);
