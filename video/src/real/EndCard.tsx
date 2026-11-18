// 4 · End card: the name, and who it is by. Text only.
import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import { look } from "./look";
import { BlurIn, Plate } from "./stage";

const { c } = look;

export const END_FRAMES = 96;

export const EndCard: React.FC = () => (
  <AbsoluteFill>
    <Plate dur={END_FRAMES} offset={11} blur={22} zoom={[1.14, 1.2]} pan={[-10, 10]} wash={0.52} />
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 18 }}>
      <BlurIn at={4} len={24}>
        <div style={{ fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 172, lineHeight: 1, letterSpacing: "-0.05em", color: c.ink }}>
          ThingTracker
        </div>
      </BlurIn>
      <BlurIn at={16}>
        <div style={{ fontFamily: theme.fonts.display, fontWeight: 500, fontSize: 42, letterSpacing: "-0.01em", color: c.ink }}>by Altice Labs</div>
      </BlurIn>
    </AbsoluteFill>
  </AbsoluteFill>
);
