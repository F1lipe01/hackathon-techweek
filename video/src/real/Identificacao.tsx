// 2 · Identificação: the kit camera, the frame the edge service analysed, its real boxes and numbers.
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { VideoAt } from "./devices";
import { Heading, Overline, Rise, Typed } from "./layers";
import { clamp, Cue, look, pt } from "./look";
import { R } from "./recognition";

const { c, a } = look;
const K = R.kit;
const CTRL = R.control;
const MOTION = K.motion.samples.find((m) => m.moved)!;
const PER_VIEW: number[] = [...K.per_view];
const BEST = PER_VIEW.indexOf(Math.max(...PER_VIEW));

export const IDENT_FRAMES = 396;

// footage/kit-desk.mp4 from 6 s to 11.5 s, re-encoded with regular keyframes so the frozen frame is exactly the
// analysed one (K.frame_s); the original's sparse keyframes made Remotion show a different moment.
const KIT_CLIP = "real/kit-desk-6s.mp4";
const KIT_T0 = 6;

const CARD = { x: 80, y: 214, w: 1200, h: 675 };
const KS = CARD.w / 1920;
const PANEL = { x: 1316, y: CARD.y, w: 524, h: CARD.h };

// timeline (scene frames)
const SRC0 = MOTION.t - 2.5;                       // play the live feed up to the analysed frame
const FREEZE = Math.round((K.frame_s - SRC0) * theme.fps);
const T = {
  motion: Math.round((MOTION.t - SRC0) * theme.fps),
  owl: FREEZE + 8, cand: FREEZE + 20, place: FREEZE + 34,
  pushIn: FREEZE + 52, pushLen: 58,
  dino: FREEZE + 78, sims: FREEZE + 94, bars: FREEZE + 104,
  best: FREEZE + 150, yours: FREEZE + 166,
  ctrl: FREEZE + 214, ctrlRes: FREEZE + 228,
};

export const IDENT_SFX: Cue[] = [
  { at: T.motion, file: "tick.wav", volume: 0.4 },
  { at: FREEZE - 1, file: "shutter.wav", volume: 0.3 },
  { at: T.owl, file: "tick.wav", volume: 0.35 },
  { at: T.dino, file: "tick.wav", volume: 0.35 },
  { at: T.yours - 2, file: "confirm.wav", volume: 0.5 },
  { at: T.ctrl, file: "tick.wav", volume: 0.35 },
];

const center = (b: readonly number[]) => [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
const BOOK_C = center(K.book_box);

const CodeLine: React.FC<{ at: number; children?: React.ReactNode; text?: string; color?: string; indent?: number; bold?: boolean }> = ({
  at, text, children, color = c.codeInk, indent = 0, bold,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) return null;
  const p = interpolate(frame, [at, at + 8], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <div style={{ opacity: p, transform: `translateX(${(1 - p) * 10}px)`, paddingLeft: indent * 22, color, fontWeight: bold ? 700 : 400,
      whiteSpace: "pre" }}>
      {text !== undefined ? <Typed text={text} start={at} cps={2.4} /> : children}
    </div>
  );
};

export const Identificacao: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = Math.min(K.frame_s, SRC0 + frame / fps);
  const frozen = frame >= FREEZE;

  // camera move: a slow drift, then the push-in on the book
  const push = interpolate(frame, [T.pushIn, T.pushIn + T.pushLen], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const drift = interpolate(frame, [0, T.pushIn], [1.12, 1.16], { ...clamp, easing: theme.ease.inOut });
  const settle = interpolate(frame, [T.ctrl - 10, T.ctrl + 30], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const z = drift * interpolate(push, [0, 1], [1, 1.95]) * interpolate(settle, [0, 1], [1, 0.93]);
  const focus = [960 + (BOOK_C[0] - 120 * settle - 960) * push, 470 + (BOOK_C[1] - 30 * settle - 470) * push];
  const px = Math.min(1920 - 960 / z, Math.max(960 / z, focus[0]));
  const py = Math.min(1080 - 540 / z, Math.max(540 / z, focus[1]));
  const toS = (x: number, y: number) => [CARD.x + KS * ((x - px) * z + 960), CARD.y + KS * ((y - py) * z + 540)];
  const rectS = (b: readonly number[]) => {
    const [x0, y0] = toS(b[0], b[1]);
    const [x1, y1] = toS(b[2], b[3]);
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  };

  const cardIn = spring({ frame, fps, config: theme.spring.smooth });
  const panelIn = spring({ frame: frame - 6, fps, config: theme.spring.smooth });
  const flash = interpolate(frame, [FREEZE - 1, FREEZE, FREEZE + 10], [0, 0.55, 0], clamp);
  const fade = (at: number, len = 10) => interpolate(frame, [at, at + len], [0, 1], { ...clamp, easing: theme.ease.out });

  const book = rectS(K.book_box);
  const place = rectS(K.place_box!);
  const ctrl = rectS(CTRL.box!);
  const outline = interpolate(frame, [T.pushIn + T.pushLen - 14, T.pushIn + T.pushLen + 16], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const perim = 2 * (book.w + book.h) + 40;
  const yours = spring({ frame: frame - T.yours, fps, config: theme.spring.bouncy });
  const ctrlP = spring({ frame: frame - T.ctrl, fps, config: theme.spring.snappy });
  const candO = fade(T.cand) * (1 - outline);
  const placeO = fade(T.place) * interpolate(push, [0.2, 0.7], [1, 0], clamp);

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: CARD.x, top: 70, display: "flex", flexDirection: "column", gap: 12 }}>
        <Rise delay={2}><Overline>2 · Identificação</Overline></Rise>
        <Rise delay={6}><Heading size={54}>A câmara do kit reconhece o livro</Heading></Rise>
      </div>

      {/* the camera */}
      <div style={{ position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 24, overflow: "hidden",
        boxShadow: look.shadow, background: c.ink, opacity: cardIn, transform: `translateY(${interpolate(cardIn, [0, 1], [40, 0])}px)` }}>
        <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transformOrigin: "0 0",
          transform: `scale(${KS}) translate(${960 - px * z}px, ${540 - py * z}px) scale(${z})` }}>
          <VideoAt src={KIT_CLIP} second={src - KIT_T0} />
        </div>
        <AbsoluteFill style={{ background: c.white, opacity: flash }} />
        <div style={{ position: "absolute", left: 20, top: 18, display: "flex", gap: 10, alignItems: "center", padding: "8px 14px",
          borderRadius: 999, background: a(c.ink, 0.7), color: c.white, fontFamily: theme.fonts.mono, fontSize: 18 }}>
          <span style={{ width: 9, height: 9, borderRadius: 9, background: frozen ? c.labs : c.alert,
            opacity: frozen ? 1 : 0.55 + 0.45 * Math.sin(frame / 4) }} />
          {frozen ? "imagem analisada · 16:30" : "câmara do kit · 18 nov · 16:30"}
        </div>
      </div>

      {/* boxes, in screen space */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <clipPath id="card"><rect x={CARD.x} y={CARD.y} width={CARD.w} height={CARD.h} rx={24} /></clipPath>
        </defs>
        <g clipPath="url(#card)">
          {placeO > 0 ? (
            <g opacity={placeO}>
              <rect x={place.x} y={place.y} width={place.w} height={place.h} rx={6} fill="none" stroke={c.white} strokeWidth={2}
                strokeDasharray="10 8" opacity={0.85} />
              <rect x={place.x + 8} y={place.y + 8} width={190} height={28} rx={6} fill={a(c.ink, 0.72)} />
              <text x={place.x + 18} y={place.y + 28} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>
                secretária · {pt(K.place_score!)}
              </text>
            </g>
          ) : null}
          {candO > 0 ? (
            <g opacity={candO}>
              <rect x={book.x} y={book.y} width={book.w} height={book.h} rx={4} fill="none" stroke={c.labs} strokeWidth={3} />
              <rect x={book.x} y={book.y - 32} width={150} height={27} rx={6} fill={c.labs} />
              <text x={book.x + 10} y={book.y - 13} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>
                livro? · {pt(K.owl_score)}
              </text>
            </g>
          ) : null}
          {outline > 0 ? (
            <rect x={book.x - 6} y={book.y - 6} width={book.w + 12} height={book.h + 12} rx={10} fill="none" stroke={c.labs} strokeWidth={5}
              strokeDasharray={perim} strokeDashoffset={perim * (1 - outline)} style={{ filter: `drop-shadow(0 0 14px ${a(c.labs, 0.6)})` }} />
          ) : null}
          {ctrlP > 0.01 ? (
            <g opacity={Math.min(1, ctrlP)}>
              <rect x={ctrl.x} y={ctrl.y} width={ctrl.w} height={ctrl.h} rx={6} fill="none" stroke={c.alert} strokeWidth={3} strokeDasharray="9 6" />
            </g>
          ) : null}
        </g>
      </svg>

      {/* tags on the image */}
      {yours > 0.01 ? (
        <div style={{ position: "absolute", left: book.x + book.w / 2, top: book.y - 22, transform: `translate(-50%, -100%) scale(${yours})`,
          transformOrigin: "50% 100%", padding: "10px 18px", borderRadius: 14, background: c.labs, color: c.white,
          fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, whiteSpace: "nowrap", boxShadow: `0 10px 30px -8px ${a(c.labsDeep, 0.6)}` }}>
          Livro · é o teu <span style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 24, opacity: 0.9 }}>{pt(K.score)}</span>
        </div>
      ) : null}
      {ctrlP > 0.01 ? (
        <div style={{ position: "absolute", left: ctrl.x + ctrl.w / 2, top: ctrl.y - 14, transform: `translate(-50%, -100%) scale(${Math.min(1, ctrlP)})`,
          transformOrigin: "50% 100%", padding: "8px 14px", borderRadius: 12, background: c.white, color: c.alert,
          fontFamily: theme.fonts.mono, fontSize: 21, fontWeight: 500, whiteSpace: "nowrap", border: `2px solid ${c.alert}` }}>
          garrafa · {pt(CTRL.score!)} &lt; {pt(K.threshold)}
        </div>
      ) : null}

      {/* the edge service's log */}
      <div style={{ position: "absolute", left: PANEL.x, top: PANEL.y, width: PANEL.w, height: PANEL.h, borderRadius: 24, background: c.code,
        boxShadow: look.shadow, opacity: panelIn, transform: `translateY(${interpolate(panelIn, [0, 1], [40, 0])}px)`, overflow: "hidden",
        fontFamily: theme.fonts.mono, fontSize: 19, lineHeight: 1.55, color: c.codeInk, boxSizing: "border-box", padding: "20px 26px" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, color: c.codeDim, fontSize: 16 }}>
          {[0, 1, 2].map((i) => <span key={i} style={{ width: 10, height: 10, borderRadius: 10, background: a(c.codeInk, 0.22) }} />)}
          <span style={{ marginLeft: 8 }}>edge.py · análise desta imagem</span>
        </div>
        <CodeLine at={10} text="à espera de movimento…" color={c.codeDim} />
        <CodeLine at={T.motion} text={`movimento ${pt(MOTION.changed * 100)} % > 0,6 % → analisar`} />
        <CodeLine at={T.owl} text={`OWLv2   "${R.query}"`} color={c.codeInk} bold />
        <CodeLine at={T.cand} text={`1 candidato · confiança ${pt(K.owl_score)}`} indent={1} color={c.codeDim} />
        <CodeLine at={T.place} text={`lugar: secretária · ${pt(K.place_score!)}`} indent={1} color={c.codeDim} />
        <CodeLine at={T.dino} text="DINOv2  recorte → 384 números" bold />
        <CodeLine at={T.sims} text="semelhança com as 8 vistas" indent={1} color={c.codeDim} />
        <Bars />
        <CodeLine at={T.best} text={`máx. ${pt(K.score)} · vista ${BEST + 1}`} indent={1} />
        <CodeLine at={T.yours} text={`${pt(K.score)} ≥ ${pt(K.threshold)} → Livro · é o teu`} color={c.codeOk} bold />
        <CodeLine at={T.ctrl} text={`controlo "${CTRL.query}"`} color={c.codeDim} />
        <CodeLine at={T.ctrlRes} text={`garrafa ${pt(CTRL.score!)} < ${pt(K.threshold)} → não é`} indent={1} color={c.alert} />
        <Pair />
      </div>
    </AbsoluteFill>
  );
};

const Bars: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < T.bars - 2) return null;
  const H = 96;
  const BW = 40;
  const G = 14;
  const BASE = 40;
  const TOP = 0.8;                                 // bar scale: 0 to 0.8
  const th = interpolate(frame, [T.bars, T.bars + 16], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <div style={{ position: "relative", height: H + BASE + 6, marginLeft: 22, marginTop: 2 }}>
      {PER_VIEW.map((v, i) => {
        const p = spring({ frame: frame - T.bars - i * 4, fps, config: theme.spring.smooth });
        const ok = v >= K.threshold;
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: i * (BW + G), bottom: BASE, width: BW, height: (H * v * p) / TOP, borderRadius: 5,
              background: ok ? c.codeOk : a(c.codeInk, 0.28),
              boxShadow: i === BEST && frame >= T.best ? `0 0 0 2px ${c.code}, 0 0 0 4px ${c.codeOk}` : "none" }} />
            <div style={{ position: "absolute", left: i * (BW + G) - 6, bottom: 18, width: BW + 12, textAlign: "center", fontSize: 13,
              color: ok ? c.codeOk : c.codeInk, opacity: p }}>{pt(v)}</div>
            <div style={{ position: "absolute", left: i * (BW + G), bottom: 0, width: BW, textAlign: "center", fontSize: 12,
              color: c.codeDim }}>v{i + 1}</div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: -6, bottom: BASE + (H * K.threshold) / TOP, width: (8 * (BW + G) - G + 12) * th,
        borderTop: `2px dashed ${c.codeInk}`, opacity: 0.75 }} />
      <div style={{ position: "absolute", left: 8 * (BW + G) + 2, bottom: BASE + (H * K.threshold) / TOP - 9, fontSize: 14, color: c.codeInk, opacity: th }}>
        {pt(K.threshold)}
      </div>
    </div>
  );
};

/** The registered view that matched best, next to the crop from the kit camera. */
const Pair: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - T.best, fps, config: theme.spring.smooth });
  if (frame < T.best) return null;
  const tile = (src: string, label: string) => (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "flex-start" }}>
      <Img src={staticFile(src)} style={{ width: 128, height: 80, objectFit: "cover", borderRadius: 8, border: `1px solid ${a(c.codeInk, 0.2)}` }} />
      <div style={{ fontSize: 13, color: c.codeDim }}>{label}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 26, right: 26, bottom: 20, display: "flex", alignItems: "center", gap: 16, opacity: p,
      transform: `translateY(${(1 - p) * 16}px)` }}>
      {tile(BEST_VIEW, `vista ${BEST + 1} · telemóvel`)}
      <div style={{ fontSize: 22, color: c.codeOk, marginBottom: 22 }}>≈</div>
      {tile("real/kit-book-crop.jpg", "câmara do kit")}
      <div style={{ marginLeft: "auto", marginBottom: 22, fontSize: 30, fontWeight: 700, color: c.codeOk }}>{pt(K.score)}</div>
    </div>
  );
};

const BEST_VIEW = `real/views/view-${BEST + 1}.jpg`;
