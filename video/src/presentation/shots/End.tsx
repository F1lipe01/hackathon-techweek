// Act 7, s23 (6 s): the end card. On the downbeat the official mark lands centred (its corners close in, the dot
// settles with its trail), then it moves to its place as the name is carried out of it. One beat after the lockup
// settles it glides up a little, and "by" with the official Altice Labs logo, on one line, rises softly into place just
// under it, the pair optically centred. Then everything is dead still for 3,3 s; the music ends on the bar line.
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { ramp } from "../ui";
import { EndorsementLine, MarkParts, Wordmark, lockupGeom } from "../brand";
import { lerp } from "../geom";

const OUT = theme.ease.out;
const IN_OUT = theme.ease.inOut;
const W = 620; // the lockup: 32 % of the frame's width
const H = (127 * W) / 736.2; // its height
const EW = Math.round(W / 3); // "by" + the logo: a third of the lockup's width
const EH = ((EW * 0.75) * 893) / 2765; // the logo's height on that line
const GAP = Math.round(0.35 * H);

export const S23: React.FC = () => {
  const frame = useCurrentFrame();
  const groupTop = 540 - (H + GAP + EH) / 2;
  const settledY = groupTop + H / 2; // the lockup's centre once the endorsement is in
  const up = ramp(frame, 49, 67, IN_OUT); // 0,6 s, one beat after the lockup settles
  const g = lockupGeom(W, 960, lerp(540, settledY, up));
  const centred = 960 - g.mark(32, 0).x; // the mark alone, centred on the frame
  const dx = lerp(centred, 0, ramp(frame, 12, 32, IN_OUT));
  // the mark lands on the downbeat: corners close in from just outside, the dot settles with its trail
  const corners = [0, 1, 2, 3].map((i) => 0.45 + 0.55 * ramp(frame, i * 1.5, 10 + i * 1.5, OUT));
  const d = ramp(frame, 0, 12, OUT);
  const wipe = ramp(frame, 14, 34, OUT);
  const e = ramp(frame, 60, 80, OUT);
  const m = g.mark(0, 0);
  return (
    <AbsoluteFill style={{ background: theme.colors.white }}>
      <MarkParts x={m.x + dx} y={m.y} unit={g.unit} corners={corners} trail={0.5 + 0.5 * d} dot={[-6 * (1 - d), 6 * (1 - d), lerp(0.8, 1, d), 1]} />
      {frame >= 14 ? <Wordmark g={g} wipe={wipe} dx={dx - 10 * (1 - wipe)} /> : null}
      <EndorsementLine cx={960} top={groupTop + H + GAP + (1 - e) * 16} width={EW} style={{ opacity: e }} />
    </AbsoluteFill>
  );
};
