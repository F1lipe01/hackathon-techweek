// Flat kitchen illustrations for the safety proposals (no footage, no people's faces): a knife on the counter and a
// cat that jumps up; a stove with a pan and a child's silhouette. Drawn in a 1040 × 640 viewBox.
import React from "react";
import { theme } from "../../theme";
import { alpha } from "../tokens";
import { mix } from "../ui";

export const KW = 1040;
export const KH = 640;
const COUNTER_Y = 360;
const FLOOR_Y = 580;

const Room: React.FC = () => (
  <g>
    <rect x={0} y={0} width={KW} height={KH} fill={theme.colors.bgAlt} />
    {/* upper cabinets */}
    {[0, 1, 2].map((i) => (
      <g key={i}>
        <rect x={110 + i * 275} y={48} width={255} height={150} rx={10} fill={theme.colors.white} stroke={alpha(theme.colors.ink, 0.08)} strokeWidth={2} />
        <rect x={110 + i * 275 + 112} y={170} width={32} height={6} rx={3} fill={alpha(theme.colors.ink, 0.25)} />
      </g>
    ))}
    {/* counter and the cabinets under it */}
    <rect x={40} y={COUNTER_Y + 22} width={KW - 80} height={FLOOR_Y - COUNTER_Y - 22} fill={alpha(theme.colors.white, 0.75)} />
    {[0, 1, 2, 3].map((i) => (
      <g key={i}>
        <rect x={52 + i * 237} y={COUNTER_Y + 36} width={225} height={FLOOR_Y - COUNTER_Y - 50} rx={8} fill="none" stroke={alpha(theme.colors.ink, 0.1)} strokeWidth={2} />
        <rect x={52 + i * 237 + 96} y={COUNTER_Y + 52} width={32} height={6} rx={3} fill={alpha(theme.colors.ink, 0.25)} />
      </g>
    ))}
    <rect x={28} y={COUNTER_Y} width={KW - 56} height={24} rx={4} fill={theme.colors.white} stroke={alpha(theme.colors.ink, 0.12)} strokeWidth={2} />
    {/* floor */}
    <rect x={0} y={FLOOR_Y} width={KW} height={KH - FLOOR_Y} fill={alpha(theme.colors.ink, 0.07)} />
  </g>
);

/** A cat, facing right, its feet at (0, 0). */
const Cat: React.FC<{ x: number; y: number; stretch: number; tilt: number }> = ({ x, y, stretch, tilt }) => (
  <g transform={`translate(${x} ${y}) rotate(${tilt}) scale(${1 + 0.12 * stretch} ${1 - 0.08 * stretch})`}>
    <path d="M -52 -42 Q -96 -60 -84 -112" fill="none" stroke={theme.colors.ink} strokeWidth={12} strokeLinecap="round" />
    <rect x={-40} y={-20} width={13} height={20 + 10 * stretch} rx={6} fill={theme.colors.ink} />
    <rect x={24} y={-20} width={13} height={20 + 10 * stretch} rx={6} fill={theme.colors.ink} />
    <ellipse cx={0} cy={-40} rx={56} ry={30} fill={theme.colors.ink} />
    <circle cx={52} cy={-74} r={25} fill={theme.colors.ink} />
    <path d="M 34 -90 L 40 -118 L 56 -96 Z" fill={theme.colors.ink} />
    <path d="M 56 -95 L 70 -116 L 74 -88 Z" fill={theme.colors.ink} />
  </g>
);

const Knife: React.FC = () => (
  <g>
    <rect x={560} y={COUNTER_Y - 14} width={52} height={13} rx={5} fill={theme.colors.ink} />
    <path d={`M 612 ${COUNTER_Y - 15} L 716 ${COUNTER_Y - 12} Q 730 ${COUNTER_Y - 7} 716 ${COUNTER_Y - 1} L 612 ${COUNTER_Y - 1} Z`} fill={theme.colors.white} stroke={theme.colors.inkDim} strokeWidth={2.5} />
  </g>
);

type Box = { x: number; y: number; w: number; h: number };

const DetBox: React.FC<{ b: Box; label: string; show: number; color: string; right?: boolean }> = ({ b, label, show, color, right }) => {
  const lw = label.length * 11 + 22;
  const lx = right ? b.x + b.w + 2 - lw : b.x - 2;
  return (
    <g opacity={show}>
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx={8} fill="none" stroke={color} strokeWidth={4}
        pathLength={1} strokeDasharray={1} strokeDashoffset={1 - show} />
      <rect x={lx} y={b.y - 34} width={lw} height={28} rx={7} fill={color} />
      <text x={lx + 11} y={b.y - 14} fill={theme.colors.white} fontFamily={theme.fonts.mono} fontSize={17} fontWeight={500}>{label}</text>
    </g>
  );
};

/** Knife on the counter; the cat jumps from the floor (jump 0) to the counter (jump 1). */
export const KnifeAndCat: React.FC<{ boxes: number; jump: number; alert: number; viewBox?: string; width?: number; height?: number }> = ({
  boxes, jump, alert, viewBox, width, height,
}) => {
  const x = mix(300, 470, jump);
  const arc = Math.sin(Math.PI * jump) * 170;
  const y = mix(FLOOR_Y, COUNTER_Y, jump) - arc;
  const flying = jump > 0.02 && jump < 0.98;
  const tilt = flying ? (jump < 0.5 ? -14 : 8) * Math.sin(Math.PI * jump) : 0;
  const color = alert > 0.5 ? theme.colors.alert : theme.colors.labs;
  const cat: Box = { x: x - 100, y: y - 124, w: 186, h: 132 };
  const knife: Box = { x: 548, y: COUNTER_Y - 30, w: 192, h: 40 };
  return (
    <svg viewBox={viewBox ?? `0 0 ${KW} ${KH}`} width={width ?? "100%"} height={height ?? "100%"} preserveAspectRatio="xMidYMid slice">
      <Room />
      <ellipse cx={270} cy={COUNTER_Y - 2} rx={62} ry={9} fill={alpha(theme.colors.ink, 0.08)} />
      <path d={`M 214 ${COUNTER_Y - 2} Q 270 ${COUNTER_Y + 40 - 70} 326 ${COUNTER_Y - 2} Z`} fill={theme.colors.white} stroke={alpha(theme.colors.ink, 0.18)} strokeWidth={2} />
      <Knife />
      <Cat x={x} y={y} stretch={flying ? Math.sin(Math.PI * jump) : 0} tilt={tilt} />
      {alert > 0 ? (
        <line x1={cat.x + cat.w} y1={cat.y + cat.h / 2 + 30} x2={knife.x} y2={knife.y + knife.h / 2} stroke={theme.colors.alert}
          strokeWidth={3} strokeDasharray="8 8" opacity={alert} />
      ) : null}
      <DetBox b={knife} label="faca" show={boxes} color={color} right />
      <DetBox b={cat} label={alert > 0.5 ? "gato · perto da faca" : "gato"} show={boxes} color={color} />
    </svg>
  );
};

/** A stove with a pan; a child's silhouette (no face) reaches towards the handle. */
export const Stove: React.FC<{ near: number; boxes: number }> = ({ near, boxes }) => {
  const cx = mix(980, 850, near);
  const reach = near;
  return (
    <svg viewBox={`0 0 ${KW} ${KH}`} width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <Room />
      {/* oven front and hob */}
      <rect x={520} y={COUNTER_Y + 30} width={280} height={FLOOR_Y - COUNTER_Y - 44} rx={10} fill={theme.colors.white} stroke={alpha(theme.colors.ink, 0.18)} strokeWidth={2} />
      <rect x={548} y={COUNTER_Y + 80} width={224} height={110} rx={8} fill={alpha(theme.colors.ink, 0.75)} />
      <rect x={520} y={COUNTER_Y - 6} width={280} height={8} rx={3} fill={alpha(theme.colors.ink, 0.8)} />
      {/* flames and pan */}
      {[0, 1, 2].map((i) => (
        <path key={i} d={`M ${616 + i * 22} ${COUNTER_Y - 6} q 6 -16 10 0 Z`} fill={theme.colors.alert} opacity={0.85} />
      ))}
      <rect x={584} y={COUNTER_Y - 60} width={128} height={50} rx={8} fill={theme.colors.inkDim} />
      <rect x={576} y={COUNTER_Y - 66} width={144} height={10} rx={5} fill={theme.colors.ink} />
      <rect x={712} y={COUNTER_Y - 50} width={92} height={10} rx={5} fill={theme.colors.ink} />
      {[0, 1, 2].map((i) => (
        <path key={i} d={`M ${616 + i * 28} ${COUNTER_Y - 80} q -10 -18 0 -36 q 10 -18 0 -36`} fill="none" stroke={alpha(theme.colors.inkDim, 0.45)} strokeWidth={4} strokeLinecap="round" />
      ))}
      {/* a child's silhouette: head, body, arm, legs; no face */}
      <g fill={alpha(theme.colors.ink, 0.55)}>
        <circle cx={cx} cy={FLOOR_Y - 236} r={28} />
        <rect x={cx - 34} y={FLOOR_Y - 200} width={68} height={120} rx={26} />
        <rect x={cx - 28} y={FLOOR_Y - 96} width={22} height={96} rx={10} />
        <rect x={cx + 6} y={FLOOR_Y - 96} width={22} height={96} rx={10} />
        <line x1={cx - 20} y1={FLOOR_Y - 186} x2={mix(cx - 40, 810, reach)} y2={mix(FLOOR_Y - 110, COUNTER_Y - 44, reach)}
          stroke={alpha(theme.colors.ink, 0.55)} strokeWidth={18} strokeLinecap="round" />
      </g>
      <DetBox b={{ x: cx - 80, y: FLOOR_Y - 290, w: 140, h: 296 }} label="criança · perto do fogão" show={boxes} color={theme.colors.alert} right />
    </svg>
  );
};
