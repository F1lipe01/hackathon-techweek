// Acts 1 and 2: four steady real moments (one bar each, no text, no boxes), then the questions stack up, text only,
// and a half-second silent stop on the empty light frame.
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { Clip } from "../media";
import { clamp } from "../ui";

export const S01: React.FC = () => <Clip clip="leaving-home-keys-1" from={1.2} origin="40% 55%" />;
export const S02: React.FC = () => <Clip clip="dog-bowl-2" from={4.0} origin="35% 60%" />;
export const S03: React.FC = () => <Clip clip="elderly-tea-2" from={2.0} origin="50% 45%" />;
export const S05: React.FC = () => <Clip clip="parcel-door-1" from={6.0} origin="45% 60%" />;

const QUESTIONS = [
  "Onde estão as chaves?", "O cão já comeu?", "A minha mãe já acordou?", "Onde deixei a carteira?", "Fechei a porta?",
  "A criança está bem?", "Deixei o fogão ligado?", "A encomenda chegou?", "O gato subiu à bancada?", "O que aconteceu esta noite?",
];
// one per beat for the first four, then two per beat (frames)
const AT = QUESTIONS.map((_, i) => (i < 4 ? i * 15 : 60 + Math.round((i - 4) * 7.5)));

const SIZE = 76;
const LH = Math.round(SIZE * 1.12); // ten lines take 79 % of the frame's height
const MOVE = 6; // frames: the column re-centres as each line arrives

export const S06: React.FC = () => {
  const frame = useCurrentFrame();
  // the column is always centred on the lines it holds: each new line moves it up by half a line
  const top = 540 - LH / 2 - QUESTIONS.reduce((y, _, i) => y + (i === 0 ? 0 : (LH / 2) * interpolate(frame, [AT[i], AT[i] + MOVE], [0, 1], { ...clamp, easing: theme.ease.inOut })), 0);
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      {QUESTIONS.map((q, i) => (
        <div
          key={q}
          style={{
            position: "absolute", left: 110, top: top + i * LH, height: LH, display: "flex", alignItems: "center",
            fontFamily: theme.fonts.display, fontSize: SIZE, fontWeight: 600, letterSpacing: "-0.03em", color: theme.colors.ink,
            opacity: interpolate(frame, [AT[i], AT[i] + 4], [0, 1], { ...clamp, easing: theme.ease.out }), whiteSpace: "nowrap",
          }}
        >
          {q}
        </div>
      ))}
    </AbsoluteFill>
  );
};

/** The stop: the questions vanish on the beat; the empty light frame, room tone only. */
export const S07: React.FC = () => <AbsoluteFill style={{ background: theme.colors.bg }} />;
