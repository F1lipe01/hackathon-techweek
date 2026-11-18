// 4. Encontrar. The real kit camera; OWLv2 finds candidates by name, DINOv2 compares them with the book's fingerprint.
// Every number comes from public/real/recognition.json (frame at kit.frame_s).
import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { pt, useRecognition } from "../data";
import { alpha, shadow } from "../tokens";
import { Check, Kicker, Sfx, SceneExit, WordReveal, clamp, mix, ramp, useSec } from "../ui";

export const FIND_FRAMES = 352;

const M = 110;
const CARD = { x: M, y: 250, w: 1150, h: 647 } as const;
const PANEL = { x: M + 1150 + 40, y: 250, w: 1920 - 2 * M - 1150 - 40, h: 647 } as const;
const ANALYSE = 90; // the frame of the analysis = kit.frame_s in the footage

type Line = { at: number; text: React.ReactNode; color?: string; indent?: boolean; gap?: boolean };

const Typed: React.FC<{ line: Line }> = ({ line }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - line.at, fps, config: theme.spring.smooth });
  return (
    <div
      style={{
        marginTop: line.gap ? 22 : 0, paddingLeft: line.indent ? 118 : 0, color: line.color ?? theme.colors.codeInk,
        opacity: interpolate(p, [0, 0.5], [0, 1], clamp), transform: `translateX(${interpolate(p, [0, 1], [-14, 0])}px)`,
        whiteSpace: "nowrap", minHeight: 38,
      }}
    >
      {line.text}
    </div>
  );
};

const Bar: React.FC<{ at: number; label: string; score: number; threshold: number; win?: boolean }> = ({ at, label, score, threshold, win }) => {
  const frame = useCurrentFrame();
  const grow = ramp(frame, at, at + 22, theme.ease.out);
  const BAR = 130;
  const shown = score * grow;
  const passed = win && frame >= at + 22;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16, paddingLeft: 118, minHeight: 38, opacity: ramp(frame, at - 4, at + 6, theme.ease.out) }}>
      <span style={{ width: 96, color: passed ? theme.colors.codeOk : theme.colors.codeInk }}>{label}</span>
      <span style={{ width: 56, textAlign: "right", fontVariantNumeric: "tabular-nums", color: passed ? theme.colors.codeOk : theme.colors.codeInk }}>
        {pt(shown)}
      </span>
      <span style={{ position: "relative", width: BAR, height: 10, borderRadius: 5, background: alpha(theme.colors.codeInk, 0.1) }}>
        <span style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: BAR * shown, borderRadius: 5, background: passed ? theme.colors.codeOk : theme.colors.codeDim }} />
        <span style={{ position: "absolute", left: BAR * threshold - 1, top: -7, bottom: -7, width: 2, background: alpha(theme.colors.codeInk, 0.7) }} />
      </span>
    </div>
  );
};

export const Find: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const S = useSec();
  const rec = useRecognition();
  const kit = rec.kit;
  const [kw, kh] = kit.size;
  const [bx0, by0, bx1, by1] = kit.book_box;
  const f = { x: (bx0 + bx1) / 2 / kw, y: (by0 + by1) / 2 / kh };
  const controls = rec.controls.filter((c) => c.box && (c.label === "garrafa" || c.label === "teclado"));

  const cardIn = spring({ frame, fps, config: theme.spring.smooth });
  const panelIn = spring({ frame: frame - 6, fps, config: theme.spring.smooth });

  const push = ramp(frame, 118, 225);
  const s = mix(1, 2.15, push);
  const m = mix(0, 0.72, push);
  const cx = f.x + (0.5 - f.x) * m;
  const cy = f.y + (0.5 - f.y) * m;
  const tx = CARD.w * (cx - f.x * s);
  const ty = CARD.h * (cy - f.y * s);
  const toScreen = (b: [number, number, number, number]) => ({
    x: tx + (b[0] / kw) * CARD.w * s,
    y: ty + (b[1] / kh) * CARD.h * s,
    w: ((b[2] - b[0]) / kw) * CARD.w * s,
    h: ((b[3] - b[1]) / kh) * CARD.h * s,
  });
  const book = toScreen(kit.book_box);
  const outline = ramp(frame, 78, 100, theme.ease.out);
  const confirmed = ramp(frame, 200, 214, theme.ease.out);
  const best = Math.max(...kit.per_view);

  const lines: Line[] = [
    { at: 18, text: "câmara do kit · 16:30", color: theme.colors.codeDim },
    { at: 40, text: <><span style={{ color: theme.colors.codeOk }}>●</span> movimento → analisar</> },
    { at: 62, text: <><b style={{ fontWeight: 600 }}>OWLv2</b>{"    procura “book”"}</>, gap: true },
    { at: 84, text: `1 candidato (${pt(kit.owl_score)})`, indent: true, color: theme.colors.codeDim },
    { at: 116, text: <><b style={{ fontWeight: 600 }}>DINOv2</b>{"   compara com a assinatura"}</>, gap: true },
  ];

  return (
    <SceneExit duration={FIND_FRAMES}>
      <AbsoluteFill>
        <Sfx at={0} name="whoosh" volume={0.14} />
        <Sfx at={80} name="tap" volume={0.18} />
        <Sfx at={200} name="tap" volume={0.3} />
        <div style={{ position: "absolute", left: M, top: 92 }}>
          <Kicker n="02" label="Encontrar" delay={4} />
          <div style={{ height: 22 }} />
          <WordReveal text="Reconhece o seu livro, não um livro qualquer." size={66} delay={10} per={3} />
        </div>

        {/* the kit camera */}
        <div
          style={{
            position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 26, overflow: "hidden",
            boxShadow: shadow.card, background: theme.colors.ink,
            opacity: interpolate(cardIn, [0, 0.6], [0, 1], clamp),
            transform: `translateY(${interpolate(cardIn, [0, 1], [40, 0])}px) scale(${interpolate(cardIn, [0, 1], [0.96, 1])})`,
          }}
        >
          <div style={{ position: "absolute", left: 0, top: 0, width: CARD.w, height: CARD.h, transformOrigin: "0 0", transform: `translate(${tx}px, ${ty}px) scale(${s})` }}>
            <OffthreadVideo
              src={staticFile("footage/kit-desk.mp4")} muted trimBefore={Math.round((kit.frame_s * fps) - ANALYSE)}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
          {/* other objects the camera sees, compared with the same fingerprint */}
          {controls.map((c, i) => {
            const b = toScreen(c.box!);
            const p = ramp(frame, 86 + i * 6, 104 + i * 6, theme.ease.out);
            const fade = 1 - 0.55 * confirmed;
            return (
              <div key={c.label} style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, opacity: p * fade }}>
                <div style={{ position: "absolute", inset: 0, border: `2px solid ${alpha(theme.colors.white, 0.85)}`, borderRadius: 6 }} />
                <div style={{ position: "absolute", left: -1, top: -30, padding: "3px 9px", borderRadius: 6, background: alpha(theme.colors.ink, 0.7), color: theme.colors.white, fontFamily: theme.fonts.mono, fontSize: 16 }}>
                  {c.label}{frame >= 172 + i * 10 ? ` · ${pt(c.score)}` : ""}
                </div>
              </div>
            );
          })}
          {/* the book */}
          <svg style={{ position: "absolute", inset: 0, overflow: "visible" }} width={CARD.w} height={CARD.h}>
            <rect
              x={book.x} y={book.y} width={book.w} height={book.h} rx={8} fill={alpha(theme.colors.labs, 0.14 * confirmed)}
              stroke={theme.colors.labs} strokeWidth={mix(2.5, 4, confirmed)} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - outline}
            />
          </svg>
          <div
            style={{
              position: "absolute", left: book.x - 2, top: book.y - 50, display: "flex", alignItems: "center", gap: 10,
              padding: "7px 14px", borderRadius: 10, background: theme.colors.labs, color: theme.colors.white,
              fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 24, letterSpacing: "-0.01em",
              opacity: ramp(frame, 80, 92, theme.ease.out), transformOrigin: "0 100%",
              transform: `scale(${mix(0.9, 1, ramp(frame, 80, 96, theme.ease.out))})`,
            }}
          >
            {confirmed > 0.01 ? (
              <>
                <Check size={22} color={theme.colors.white} draw={confirmed} stroke={3.4} />
                <span>O seu livro · {pt(kit.score)}</span>
              </>
            ) : (
              <span style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 20 }}>book · {pt(kit.owl_score)}</span>
            )}
          </div>
        </div>

        {/* the thinking panel */}
        <div
          style={{
            position: "absolute", left: PANEL.x, top: PANEL.y, width: PANEL.w, height: PANEL.h, borderRadius: 26,
            background: theme.colors.code, boxShadow: shadow.card, padding: "34px 34px", boxSizing: "border-box",
            fontFamily: theme.fonts.mono, fontSize: 22, lineHeight: "38px", color: theme.colors.codeInk, overflow: "hidden",
            opacity: interpolate(panelIn, [0, 0.6], [0, 1], clamp),
            transform: `translateY(${interpolate(panelIn, [0, 1], [40, 0])}px) scale(${interpolate(panelIn, [0, 1], [0.96, 1])})`,
          }}
        >
          {lines.map((l, i) => <Typed key={i} line={l} />)}
          <Typed line={{ at: 124, text: "8 vistas do registo", indent: true, color: theme.colors.codeDim }} />
          <div style={{ height: 10 }} />
          <Bar at={140} label="livro" score={kit.score} threshold={kit.threshold} win />
          {controls.map((c, i) => <Bar key={c.label} at={150 + i * 10} label={c.label} score={c.score} threshold={kit.threshold} />)}
          <Typed line={{ at: 176, text: `limiar ${pt(kit.threshold)}`, indent: true, color: theme.colors.codeDim }} />
          <Typed line={{ at: 204, text: <span style={{ color: theme.colors.codeOk }}>{"→ é o seu livro"}</span>, gap: true }} />
          <Typed line={{ at: 214, text: "  secretária · 16:30", color: theme.colors.codeInk }} />
          <Typed line={{ at: 224, text: `  melhor vista: ${kit.per_view.indexOf(best) + 1} de ${kit.per_view.length}`, color: theme.colors.codeDim }} />
        </div>

        <div style={{ position: "absolute", left: M, top: CARD.y + CARD.h + 30 }}>
          <WordReveal
            text="O OWLv2 encontra pelo nome; o DINOv2 confirma pela assinatura." size={36} weight={500}
            color={theme.colors.inkDim} delay={S(7.8)} per={2} tracking="-0.015em"
          />
        </div>
      </AbsoluteFill>
    </SceneExit>
  );
};
