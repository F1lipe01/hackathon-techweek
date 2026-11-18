// Act 6: the home understands (s16–s21). One line on a light frame, then three cases: safety (the cat), care (the
// mother's normal morning, then noon) and memory (the night). The app is the real prototype; its data in these cases is
// the case's own (record_app.mjs: concept takes), so each case carries the "conceito" tag.
import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { APP, AppView, Chip, Clip, FrameBox, Recording, ScreenInsert, SoftGround, Tag, type BoxKey, type CamKey } from "../media";
import { ramp } from "../ui";
import { Title } from "../type";
import { alpha } from "../tokens";

const Side: React.FC<{ text: string; at: number; exitAt?: number; entrance?: "blur" | "rise" | "wipe" | "track"; y?: number; color?: string }> = ({ text, at, exitAt, entrance = "rise", y = 500, color }) => (
  <div style={{ position: "absolute", left: 110, top: y }}>
    <Title text={text} size={54} max={720} at={at} exitAt={exitAt} entrance={entrance} color={color} />
  </div>
);

/* ------------------------------------------------------------------ s16 */

export const S16: React.FC = () => (
  <AbsoluteFill style={{ background: theme.colors.bg, alignItems: "center", justifyContent: "center" }}>
    <Title text="A app propõe o que vigiar." size={72} max={1600} at={0} entrance="cut" align="center" />
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ s17: the cat on the counter */

// the black cat (cat-counter-2, 3840 × 2160): its ears to its front paw, and the frame's right edge (its body runs on
// past the edge of the picture). Placed by hand every half second.
const CAT: BoxKey[] = [[0.5, 1920, 585, 3840, 1690], [1.0, 1920, 605, 3840, 1712], [1.5, 1965, 605, 3840, 1732], [2.0, 2008, 560, 3840, 1708], [2.5, 1990, 558, 3840, 1722]];

export const S17: React.FC = () => {
  // the phone part (from 62 s): the suggestion is tapped (62,9 s), the sensor card arrives (63,8 s), the sheet is closed
  // (65,2 s) and the alert lands (66,2 s). Two waits are skipped inside still screens (the card held, the tab held).
  const keys: CamKey[] = [
    { at: 60, ppt: 2.0, fx: 201, fy: 360, cx: 1250, cy: 540 },
    { at: 90, ppt: 2.0, fx: 201, fy: 360, cx: 1250, cy: 540 },
    { at: 108, ppt: 2.0, fx: 201, fy: 600, cx: 1250, cy: 540 },
    { at: 160, ppt: 2.0, fx: 201, fy: 600, cx: 1250, cy: 540 },
    { at: 176, ppt: 2.0, fx: 201, fy: 260, cx: 1250, cy: 540 },
  ];
  return (
    <AbsoluteFill>
      <Sequence durationInFrames={75} layout="none">
        <Clip clip="cat-counter-2" from={0.5} push={[1, 1.04]} origin="70% 50%">
          <FrameBox clip="cat-counter-2" keys={CAT} clipFrom={0.5} at={15} label="gato" />
        </Clip>
      </Sequence>
      <Sequence from={60} layout="none">
        <AppView rec="cat" segs={[[0, 1.4], [75, 5.1], [117, 7.1]]} keys={keys.map((k) => ({ ...k, at: k.at - 60 }))}
          ground={<SoftGround clip="cat-counter-2" at={2.5} />} reveal={{ at: 0, frames: 15, from: { x: 981, y: 272, w: 939, h: 599 } }} />
      </Sequence>
      <Sequence from={60} layout="none">
        <Side text="A cozinha, mais segura." at={14} entrance="blur" />
      </Sequence>
      <Tag text="conceito" corner="tr" />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ s19: "A minha mãe já acordou?" */

/** A region of a recording (pt) as a card, at `ppt` px per pt. */
const RecCard: React.FC<{ rec: string; segs: [number, number][]; y0: number; y1: number; ppt: number; style?: React.CSSProperties }> = ({ rec, segs, y0, y1, ppt, style }) => (
  <div style={{ position: "absolute", width: APP.w * ppt, height: (y1 - y0) * ppt, overflow: "hidden", borderRadius: 28, background: "#f7fafd", boxShadow: `0 30px 70px -26px ${alpha(theme.colors.ink, 0.55)}`, ...style }}>
    <div style={{ position: "absolute", left: 0, top: -y0 * ppt, transformOrigin: "0 0", transform: `scale(${ppt / APP.px})` }}>
      <Recording name={rec} segs={segs} radius={0} />
    </div>
  </div>
);

export const S19: React.FC = () => {
  const frame = useCurrentFrame();
  const p = ramp(frame, 34, 48, theme.ease.out);
  return (
    <AbsoluteFill>
      <Clip clip="elderly-reading-1" from={0.3} push={[1, 1.05]} origin="40% 40%" />
      <Chip at={6} text="08:12" x={110} y={86} size={30} />
      <div style={{ position: "absolute", left: 110, top: 160 }}>
        <Title text="“A minha mãe já acordou?”" size={60} max={900} at={8} entrance="rise" />
      </div>
      <RecCard rec="mum" segs={[[0, 7.0]]} y0={622} y1={770} ppt={2.0} style={{ left: 1040, top: 700 + (1 - p) * 40, opacity: p }} />
      <Tag text="conceito" corner="tr" />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ s20: noon, and nobody has been in the kitchen */

export const S20: React.FC = () => {
  const frame = useCurrentFrame();
  const noon = ramp(frame, 6, 36, theme.ease.inOut); // one dissolve for the hours passing
  const keys: CamKey[] = [
    { at: 45, ppt: 1.35, fx: 201, fy: 200, cx: 960, cy: 470 },
    { at: 52, ppt: 1.35, fx: 201, fy: 200, cx: 960, cy: 470 },
    { at: 74, ppt: 2.0, fx: 201, fy: 110, cx: 960, cy: 400 },
  ];
  return (
    <AbsoluteFill>
      {frame < 45 ? (
        <AbsoluteFill>
          <Clip clip="older-kitchen-1" from={0} push={[1.12, 1.13]} origin="0% 50%" grade="brightness(0.98) saturate(1.12) sepia(0.18)" />
          <AbsoluteFill style={{ opacity: noon }}>
            <Clip clip="older-kitchen-1" from={0} push={[1.12, 1.13]} origin="0% 50%" grade="brightness(1.1) saturate(0.95) contrast(1.02)" />
          </AbsoluteFill>
          <Chip at={0} text="08:12" x={110} y={86} size={30} turnAt={30} turnText="12:00" />
        </AbsoluteFill>
      ) : (
        <Sequence from={45} layout="none">
          <ScreenInsert clip="phone-alert-3" from={0} play={54} track="phone-alert-3_0-3" rec="noon" segs={[[0, 1.73]]} keys={keys.map((k) => ({ ...k, at: k.at - 45 }))} screenRadius={60} />
        </Sequence>
      )}
      <Tag text="conceito" corner="tr" />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ s21: what happened at 4 a.m.? */

// the person by the car (garden-night-2, 1920 × 1080): head to feet, the arm when it reaches out. From 7 s on the person
// is in front of the car, never hidden by it.
const PERSON: BoxKey[] = [[7.0, 352, 432, 540, 800], [7.6, 328, 428, 498, 800], [8.0, 312, 424, 472, 800], [8.5, 290, 415, 420, 800], [9.0, 262, 405, 385, 790]];

export const S21: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      {frame < 60 ? (
        <AbsoluteFill>
          <Clip clip="garden-night-2" from={7.0} push={[1, 1.05]} origin="25% 60%" grade="brightness(1.15) contrast(1.02)">
            <FrameBox clip="garden-night-2" keys={PERSON} clipFrom={7.0} at={15} label="pessoa · 04:02" />
          </Clip>
        </AbsoluteFill>
      ) : (
        <Sequence from={60} layout="none">
          <AppView rec="night" segs={[[0, 6.0]]} keys={[{ at: 0, ppt: 2.0, fx: 201, fy: 615, cx: 1250, cy: 540 }]} />
          <Side text="O que aconteceu às 4h?" at={4} entrance="wipe" />
        </Sequence>
      )}
      <Tag text="conceito" corner="tr" dark={frame < 60} />
    </AbsoluteFill>
  );
};

