// Shot 13. How it works, as one line drawn in a single stroke: at home (camera → motion detection) | at Altice (vision
// models on the changed zone only → the home's memory → the assistant → MCP) → app and devices. Straight arrows.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha } from "../tokens";
import { Title, useOneLine } from "../type";
import { Paper, clamp, ramp } from "../ui";
import { Sfx } from "../sound";
import { SHOT_FRAMES } from "../timeline";

export const HOW_FRAMES = SHOT_FRAMES.how;

const Y = 560;
const NODES = [
  { x: 190, title: "câmara", sub: "do kit" },
  { x: 450, title: "movimento", sub: "deteção em casa" },
  { x: 770, title: "modelos de visão", sub: "só a zona que mudou" },
  { x: 1040, title: "memória da casa", sub: "objeto, lugar e hora" },
  { x: 1290, title: "assistente", sub: "modelo de linguagem" },
  { x: 1510, title: "MCP", sub: "da Altice" },
  { x: 1740, title: "app e dispositivos", sub: "avisos e ações" },
];
const BOUNDARY = 610;
const START = 18;
const END = 190;

const NodeLabel: React.FC<{ n: (typeof NODES)[number]; at: number }> = ({ n, at }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  useOneLine(n.title, 30, 600, -0.02, 250);
  useOneLine(n.sub, 21, 400, 0, 250);
  const p = spring({ frame: frame - at, fps, config: theme.spring.snappy });
  return (
    <>
      <div style={{ position: "absolute", left: n.x - 11, top: Y - 11, width: 22, height: 22, borderRadius: 11, background: theme.colors.white, border: `4px solid ${theme.colors.ink}`, boxSizing: "border-box", transform: `scale(${p})` }} />
      <div style={{ position: "absolute", left: n.x - 150, width: 300, top: Y - 64, textAlign: "center", fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, letterSpacing: "-0.02em", color: theme.colors.ink, whiteSpace: "nowrap", opacity: interpolate(p, [0, 0.6], [0, 1], clamp), transform: `translateY(${12 * (1 - p)}px)` }}>
        {n.title}
      </div>
      <div style={{ position: "absolute", left: n.x - 150, width: 300, top: Y + 30, textAlign: "center", fontFamily: theme.fonts.display, fontSize: 21, color: theme.colors.inkDim, whiteSpace: "nowrap", opacity: ramp(frame, at + 4, at + 14, theme.ease.out) }}>
        {n.sub}
      </div>
    </>
  );
};

export const How: React.FC = () => {
  const frame = useCurrentFrame();
  const x0 = NODES[0].x;
  const x1 = NODES[NODES.length - 1].x;
  const draw = ramp(frame, START, END, theme.ease.inOut);
  const head = x0 + (x1 - x0) * draw;
  const reach = (x: number) => START + ((x - x0) / (x1 - x0)) * (END - START);
  const sides = ramp(frame, START + 10, START + 26, theme.ease.out);
  return (
    <AbsoluteFill>
      <Paper />
      <Sfx at={START} role="whoosh" volume={0.3} />
      <div style={{ position: "absolute", left: 110, top: 150 }}>
        <Title text="Nenhum vídeo nem imagem completa sai de casa." size={64} max={1700} at={8} entrance="rise" />
      </div>
      {/* the two sides */}
      <div style={{ position: "absolute", left: 110, top: Y - 190, fontFamily: theme.fonts.mono, fontSize: 21, color: theme.colors.inkDim, opacity: sides }}>em casa</div>
      <div style={{ position: "absolute", left: BOUNDARY + 30, top: Y - 190, fontFamily: theme.fonts.mono, fontSize: 21, color: theme.colors.inkDim, opacity: sides }}>Altice</div>
      <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1920} height={1080}>
        <line x1={BOUNDARY} y1={Y - 200} x2={BOUNDARY} y2={Y - 200 + 330 * sides} stroke={alpha(theme.colors.inkDim, 0.6)} strokeWidth={2} strokeDasharray="7 9" />
        {/* the single stroke */}
        <line x1={x0} y1={Y} x2={head} y2={Y} stroke={theme.colors.ink} strokeWidth={3.5} />
        {/* arrowheads, each drawn as the stroke passes it, ending cleanly before the next node */}
        {NODES.slice(1).map((n, i) => {
          const tipX = n.x - 18;
          if (head < tipX) return null;
          return <path key={i} d={`M ${tipX - 12} ${Y - 8} L ${tipX} ${Y} L ${tipX - 12} ${Y + 8}`} fill="none" stroke={theme.colors.ink} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round" />;
        })}
        {/* a small signal travelling the line once it is drawn */}
        {frame > END ? <circle cx={x0 + (x1 - x0) * ramp(frame, END, END + 70, theme.ease.inOut)} cy={Y} r={9} fill={theme.colors.labs} /> : null}
      </svg>
      {NODES.map((n) => <NodeLabel key={n.title} n={n} at={Math.round(reach(n.x)) - 4} />)}
    </AbsoluteFill>
  );
};
