// A separate entry point for video 2 alone, so it can be rendered on its own:
//   npx remotion render src/real/entry.tsx RealExample out/real-example.mp4
import React from "react";
import { Composition, registerRoot } from "remotion";
import { theme } from "../theme";
import { RealExample, DURATION } from "./RealExample";

const RealRoot: React.FC = () => (
  <Composition id="RealExample" component={RealExample} durationInFrames={DURATION} fps={theme.fps} width={theme.width} height={theme.height} />
);

registerRoot(RealRoot);
