// The Remotion compositions: src/presentation (video 1, the product presentation), src/real (video 2, the real example
// in the lab), src/proof (tracking and camera checks) and src/film (the three lab examples and the full film). Each
// module exports its component and its duration in frames.
import React from "react";
import { Composition } from "remotion";
import { theme } from "./theme";
import { Presentation, DURATION as PRESENTATION_FRAMES } from "./presentation/Presentation";
import { RealExample, DURATION as REAL_FRAMES } from "./real/RealExample";
import { TrackTest, TRACK_TEST_FRAMES } from "./proof/TrackTest";
import { ProofCamera, PROOF_FRAMES } from "./proof/ProofCamera";
import { FilmV7, FILM_FRAMES } from "./film/FilmV7";
import { Scene1Book, SCENE1_FRAMES } from "./film/Scene1Book";
import { Scene2Face, SCENE2_FRAMES } from "./film/Scene2Face";
import { Scene3People, SCENE3_FRAMES } from "./film/Scene3People";
import { FilmFull, FULL_FRAMES } from "./film/FilmFull";

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
    <Composition id="Scene1Book" component={Scene1Book} durationInFrames={SCENE1_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="Scene2Face" component={Scene2Face} durationInFrames={SCENE2_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="Scene3People" component={Scene3People} durationInFrames={SCENE3_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
    <Composition id="FilmFull" component={FilmFull} durationInFrames={FULL_FRAMES}
      fps={theme.fps} width={theme.width} height={theme.height} />
  </>
);
