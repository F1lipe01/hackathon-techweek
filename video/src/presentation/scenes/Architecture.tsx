// 8. Arquitetura, as in docs/pt/14-arquitetura.md: câmara → modelos em casa → memória da casa → assistente →
// MCP da Altice → app e dispositivos. Straight arrows, plain words; the home's boundary between memory and assistant.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha, shadow } from "../tokens";
import { Kicker, SceneExit, Sfx, WordReveal, clamp, ramp } from "../ui";

export const ARCH_FRAMES = 270;

const NODES = [
  { title: "Câmara", sub: "a câmara do kit, na rede da casa" },
  { title: "Modelos em casa", sub: "OWLv2 e DINOv2, só quando há movimento" },
  { title: "Memória da casa", sub: "recortes pequenos e lugares" },
  { title: "Assistente", sub: "modelo de linguagem" },
  { title: "MCP da Altice", sub: "as ferramentas da plataforma" },
  { title: "App e dispositivos", sub: "respostas, avisos e ações" },
];

const X0 = 110;
const NODE_W = 236;
const GAP = 58;
const NODE_H = 280;
const ROW_Y = 450;
const nodeX = (i: number) => X0 + i * (NODE_W + GAP);
const STEP = 16; // frames between nodes

const Arrow: React.FC<{ x: number; y: number; len: number; draw: number }> = ({ x, y, len, draw }) => {
  const head = 11;
  const shaft = Math.max(0, (len - head) * draw);
  return (
    <svg style={{ position: "absolute", left: x, top: y - 12, overflow: "visible" }} width={len} height={24}>
      <line x1={0} y1={12} x2={shaft} y2={12} stroke={theme.colors.inkDim} strokeWidth={3} strokeLinecap="butt" />
      {draw > 0.98 ? <path d={`M ${len - head} 5 L ${len} 12 L ${len - head} 19 Z`} fill={theme.colors.inkDim} /> : null}
    </svg>
  );
};

export const Architecture: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = 30;
  const pulse = ramp(frame, start + 6 * STEP + 6, start + 6 * STEP + 70, theme.ease.inOut);
  const pulseX = nodeX(0) + NODE_W / 2 + pulse * (nodeX(5) - nodeX(0));
  const boundaryX = nodeX(3) - GAP / 2;
  const groupIn = ramp(frame, start + 3 * STEP, start + 3 * STEP + 20, theme.ease.out);

  return (
    <SceneExit duration={ARCH_FRAMES}>
      <AbsoluteFill>
        <Sfx at={0} name="whoosh" volume={0.14} />
        <div style={{ position: "absolute", left: X0, top: 120 }}>
          <Kicker n="06" label="Como funciona" delay={4} />
          <div style={{ height: 24 }} />
          <WordReveal text="Ver em casa, raciocinar sob contrato." size={76} delay={10} per={4} />
        </div>

        {/* the two sides */}
        <div style={{ position: "absolute", left: X0, top: ROW_Y - 66, width: boundaryX - X0 - 24, display: "flex", justifyContent: "space-between", opacity: groupIn }}>
          <span style={{ fontFamily: theme.fonts.display, fontSize: 26, fontWeight: 600, color: theme.colors.ink }}>Em casa</span>
        </div>
        <div style={{ position: "absolute", left: boundaryX + 24, top: ROW_Y - 66, opacity: groupIn }}>
          <span style={{ fontFamily: theme.fonts.display, fontSize: 26, fontWeight: 600, color: theme.colors.ink }}>Na plataforma Altice</span>
        </div>
        <svg style={{ position: "absolute", left: boundaryX - 2, top: ROW_Y - 74 }} width={4} height={NODE_H + 150}>
          <line x1={2} y1={0} x2={2} y2={(NODE_H + 150) * groupIn} stroke={alpha(theme.colors.inkDim, 0.6)} strokeWidth={2.5} strokeDasharray="8 8" />
        </svg>

        {NODES.map((n, i) => {
          const p = spring({ frame: frame - start - i * STEP, fps, config: theme.spring.smooth });
          const lit = Math.abs(pulseX - (nodeX(i) + NODE_W / 2)) < NODE_W / 2 && pulse > 0 && pulse < 1;
          return (
            <div
              key={n.title}
              style={{
                position: "absolute", left: nodeX(i), top: ROW_Y, width: NODE_W, height: NODE_H, boxSizing: "border-box",
                borderRadius: 26, background: theme.colors.white, padding: "26px 22px", boxShadow: shadow.soft,
                border: `2px solid ${lit ? alpha(theme.colors.labs, 0.9) : alpha(theme.colors.ink, 0.06)}`,
                opacity: interpolate(p, [0, 0.6], [0, 1], clamp),
                transform: `translateY(${interpolate(p, [0, 1], [36, 0])}px) scale(${interpolate(p, [0, 1], [0.94, 1])})`,
              }}
            >
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 18, color: theme.colors.inkDim }}>{String(i + 1).padStart(2, "0")}</div>
              <div style={{ fontFamily: theme.fonts.display, fontSize: 34, fontWeight: 600, color: theme.colors.ink, letterSpacing: "-0.02em", lineHeight: 1.08, marginTop: 12 }}>
                {n.title}
              </div>
              <div style={{ fontFamily: theme.fonts.display, fontSize: 23, color: theme.colors.inkDim, lineHeight: 1.3, marginTop: 12 }}>{n.sub}</div>
            </div>
          );
        })}

        {NODES.slice(0, -1).map((_, i) => (
          <Arrow key={i} x={nodeX(i) + NODE_W + 8} y={ROW_Y + NODE_H / 2} len={GAP - 16} draw={ramp(frame, start + i * STEP + 10, start + i * STEP + 22, theme.ease.out)} />
        ))}

        {/* a small signal travels the chain */}
        {pulse > 0 && pulse < 1 ? (
          <div
            style={{
              position: "absolute", left: pulseX - 9, top: ROW_Y + NODE_H + 30, width: 18, height: 18, borderRadius: 9,
              background: theme.colors.labs, boxShadow: `0 0 24px ${alpha(theme.colors.labs, 0.6)}`,
            }}
          />
        ) : null}

        <div style={{ position: "absolute", left: X0, top: ROW_Y + NODE_H + 70, width: 560 }}>
          <WordReveal text="Nenhum vídeo nem imagem completa sai de casa para análise." size={30} weight={500} color={theme.colors.inkDim} delay={start + 3 * STEP + 16} per={2} lineHeight={1.3} tracking="-0.01em" />
        </div>
        <div style={{ position: "absolute", left: boundaryX + 24, top: ROW_Y + NODE_H + 70, width: 440 }}>
          <WordReveal text="As ações seguem pelo MCP, como os comandos de hoje." size={30} weight={500} color={theme.colors.inkDim} delay={start + 6 * STEP + 10} per={2} lineHeight={1.3} tracking="-0.01em" />
        </div>
      </AbsoluteFill>
    </SceneExit>
  );
};
