// 2 · Identificação: the kit camera at real speed, then the frame the edge service analysed, with its real boxes and
// the numbers of edge.py's code against the 3-view fingerprint (R.views3).
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { VideoAt } from "./devices";
import { Heading, Overline, Rise, Typed } from "./layers";
import { clamp, Cue, look, mmss, pt } from "./look";
import { R } from "./recognition";

const { c, a } = look;
const K = R.kit;
const V3 = R.views3;
const CTRL = V3.control;
const MOTION = K.motion.samples.find((m) => m.moved)!;
const PER_VIEW: number[] = [...V3.kit.per_view];
const SCORE = V3.kit.score;
const BEST = PER_VIEW.indexOf(SCORE);
const BEST_VIEW = V3.views[BEST];

// footage/kit-desk.mp4 from 6 s to 11.5 s, re-encoded with regular keyframes so the frozen frame is exactly the
// analysed one (K.frame_s); the original's sparse keyframes made Remotion show a different moment.
const KIT_CLIP = "real/kit-desk-6s.mp4";
const KIT_T0 = 6;

const CARD = { x: 80, y: 214, w: 1200, h: 675 };
const KS = CARD.w / 1920;
const PANEL = { x: 1316, y: CARD.y, w: 524, h: CARD.h };

// timeline (scene frames): the live feed at real speed up to the analysed frame, then the analysis
const SRC0 = MOTION.t - 3.0;
const FREEZE = Math.round((K.frame_s - SRC0) * theme.fps);
const T = {
  motion: Math.round((MOTION.t - SRC0) * theme.fps),
  owl: FREEZE + 10, place: FREEZE + 26,
  pushIn: FREEZE + 40, pushLen: 60,
  dino: FREEZE + 70, bars: FREEZE + 86,
  best: FREEZE + 124, yours: FREEZE + 140,
  ctrl: FREEZE + 188, ctrlRes: FREEZE + 200,
};
export const IDENT_FRAMES = FREEZE + 262;
export const IDENT_CUES: Cue[] = [
  { at: FREEZE - 1, file: "capture" },
  { at: T.yours - 1, file: "confirm" },
  { at: T.ctrl, file: "tick" },
];

const center = (b: readonly number[]) => [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
const BOOK_C = center(K.book_box);

const CodeLine: React.FC<{ at: number; text: string; color?: string; indent?: number; bold?: boolean }> = ({
  at, text, color = c.codeInk, indent = 0, bold,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) return null;
  const p = interpolate(frame, [at, at + 6], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <div style={{ opacity: p, paddingLeft: indent * 22, color, fontWeight: bold ? 700 : 400, whiteSpace: "pre" }}>
      <Typed text={text} start={at} cps={3} />
    </div>
  );
};

export const Identificacao: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = Math.min(K.frame_s, SRC0 + frame / fps);
  const frozen = frame >= FREEZE;

  // camera: a still frame tightened to the desk, then a slow push-in on the book
  const push = interpolate(frame, [T.pushIn, T.pushIn + T.pushLen], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const z = 1.14 * interpolate(push, [0, 1], [1, 1.6]);
  const focus = [960 + (BOOK_C[0] - 80 - 960) * push, 470 + (BOOK_C[1] - 10 - 470) * push];
  const px = Math.min(1920 - 960 / z, Math.max(960 / z, focus[0]));
  const py = Math.min(1080 - 540 / z, Math.max(540 / z, focus[1]));
  const toS = (x: number, y: number) => [CARD.x + KS * ((x - px) * z + 960), CARD.y + KS * ((y - py) * z + 540)];
  const rectS = (b: readonly number[]) => {
    const [x0, y0] = toS(b[0], b[1]);
    const [x1, y1] = toS(b[2], b[3]);
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  };
  const fade = (at: number, len = 8) => interpolate(frame, [at, at + len], [0, 1], { ...clamp, easing: theme.ease.out });
  const flash = interpolate(frame, [FREEZE - 1, FREEZE, FREEZE + 8], [0, 0.4, 0], clamp);

  const book = rectS(K.book_box);
  const place = rectS(K.place_box!);
  const ctrl = rectS(CTRL.box!);
  const outline = interpolate(frame, [T.pushIn + T.pushLen - 16, T.pushIn + T.pushLen + 12], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const perim = 2 * (book.w + book.h) + 40;
  const candO = fade(T.owl) * (1 - outline);
  const placeO = fade(T.place) * interpolate(push, [0.2, 0.6], [1, 0], clamp);
  const yours = fade(T.yours, 10);
  const ctrlO = fade(T.ctrl, 10);

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: CARD.x, top: 74, display: "flex", flexDirection: "column", gap: 10 }}>
        <Rise delay={2} y={16}><Overline>2 · Identificação</Overline></Rise>
        <Rise delay={5} y={16}><Heading size={54}>A câmara do kit, no laboratório</Heading></Rise>
      </div>

      <div style={{ position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 20, overflow: "hidden",
        boxShadow: look.shadow, background: c.ink }}>
        <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transformOrigin: "0 0",
          transform: `scale(${KS}) translate(${960 - px * z}px, ${540 - py * z}px) scale(${z})` }}>
          <VideoAt src={KIT_CLIP} second={src - KIT_T0} />
        </div>
        <AbsoluteFill style={{ background: c.white, opacity: flash }} />
        <div style={{ position: "absolute", left: 18, top: 16, display: "flex", gap: 10, alignItems: "center", padding: "7px 13px",
          borderRadius: 999, background: a(c.ink, 0.7), color: c.white, fontFamily: theme.fonts.mono, fontSize: 18 }}>
          <span style={{ width: 9, height: 9, borderRadius: 9, background: frozen ? c.labs : c.alert }} />
          {frozen ? "imagem analisada · 16:30" : `câmara do kit · 18 nov · 16:30 · ${mmss(src)}`}
        </div>
      </div>

      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <clipPath id="card"><rect x={CARD.x} y={CARD.y} width={CARD.w} height={CARD.h} rx={20} /></clipPath>
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
              <text x={book.x + 10} y={book.y - 13} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>livro? · {pt(K.owl_score)}</text>
            </g>
          ) : null}
          {outline > 0 ? (
            <rect x={book.x - 6} y={book.y - 6} width={book.w + 12} height={book.h + 12} rx={10} fill="none" stroke={c.labs} strokeWidth={4}
              strokeDasharray={perim} strokeDashoffset={perim * (1 - outline)} />
          ) : null}
          {ctrlO > 0 ? (
            <rect x={ctrl.x} y={ctrl.y} width={ctrl.w} height={ctrl.h} rx={6} fill="none" stroke={c.alert} strokeWidth={3} strokeDasharray="9 6"
              opacity={ctrlO} />
          ) : null}
        </g>
      </svg>

      {yours > 0 ? (
        <div style={{ position: "absolute", left: book.x + book.w / 2, top: book.y - 20, transform: `translate(-50%, ${-100 + (1 - yours) * 10}%)`,
          opacity: yours, padding: "9px 16px", borderRadius: 12, background: c.labs, color: c.white, fontFamily: theme.fonts.display,
          fontSize: 28, fontWeight: 600, whiteSpace: "nowrap" }}>
          Livro · é o teu <span style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 23 }}>{pt(SCORE)}</span>
        </div>
      ) : null}
      {ctrlO > 0 ? (
        <div style={{ position: "absolute", left: ctrl.x + ctrl.w / 2, top: ctrl.y - 12, transform: "translate(-50%, -100%)", opacity: ctrlO,
          padding: "7px 13px", borderRadius: 10, background: c.white, color: c.alert, fontFamily: theme.fonts.mono, fontSize: 20,
          fontWeight: 500, whiteSpace: "nowrap", border: `2px solid ${c.alert}` }}>
          garrafa · {pt(CTRL.score!)} &lt; {pt(K.threshold)}
        </div>
      ) : null}

      <div style={{ position: "absolute", left: PANEL.x, top: PANEL.y, width: PANEL.w, height: PANEL.h, borderRadius: 20, background: c.code,
        boxShadow: look.shadow, overflow: "hidden", fontFamily: theme.fonts.mono, fontSize: 19, lineHeight: 1.6, color: c.codeInk,
        boxSizing: "border-box", padding: "20px 26px" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, color: c.codeDim, fontSize: 16 }}>
          {[0, 1, 2].map((i) => <span key={i} style={{ width: 10, height: 10, borderRadius: 10, background: a(c.codeInk, 0.22) }} />)}
          <span style={{ marginLeft: 8 }}>edge.py · análise desta imagem</span>
        </div>
        <CodeLine at={6} text="à espera de movimento…" color={c.codeDim} />
        <CodeLine at={T.motion} text={`movimento ${pt(MOTION.changed * 100)} % > 0,6 % → analisar`} />
        <CodeLine at={T.owl} text={`OWLv2   "${R.query}"`} bold />
        <CodeLine at={T.owl + 8} text={`1 candidato · confiança ${pt(K.owl_score)}`} indent={1} color={c.codeDim} />
        <CodeLine at={T.place} text={`lugar: secretária · ${pt(K.place_score!)}`} indent={1} color={c.codeDim} />
        <CodeLine at={T.dino} text="DINOv2  semelhança com as 3 vistas" bold />
        <Bars />
        <CodeLine at={T.best} text={`máx. ${pt(SCORE)} · vista ${BEST + 1}`} indent={1} />
        <CodeLine at={T.yours} text={`${pt(SCORE)} ≥ ${pt(K.threshold)} → Livro · é o teu`} color={c.codeOk} bold />
        <CodeLine at={T.ctrl} text={`controlo "${CTRL.query}"`} color={c.codeDim} />
        <CodeLine at={T.ctrlRes} text={`garrafa ${pt(CTRL.score!)} < ${pt(K.threshold)} → não é`} indent={1} color={c.alert} />
        <Pair />
      </div>
    </AbsoluteFill>
  );
};

const Bars: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.bars - 2) return null;
  const H = 110;
  const BW = 74;
  const G = 34;
  const BASE = 46;                                   // two label rows under the bars: the value, then the view
  const TOP = 0.8;                                   // bar scale: 0 to 0.8
  const th = interpolate(frame, [T.bars, T.bars + 14], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <div style={{ position: "relative", height: H + BASE + 4, marginLeft: 22, marginTop: 6, marginBottom: 6 }}>
      {PER_VIEW.map((v, i) => {
        const p = interpolate(frame, [T.bars + i * 5, T.bars + i * 5 + 16], [0, 1], { ...clamp, easing: theme.ease.out });
        const ok = v >= K.threshold;
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: i * (BW + G), bottom: BASE, width: BW, height: (H * v * p) / TOP, borderRadius: 5,
              background: ok ? c.codeOk : a(c.codeInk, 0.28) }} />
            <div style={{ position: "absolute", left: i * (BW + G), bottom: 20, width: BW, textAlign: "center", fontSize: 17, fontWeight: 700,
              color: ok ? c.codeOk : c.codeInk, opacity: p }}>{pt(v)}</div>
            <div style={{ position: "absolute", left: i * (BW + G), bottom: 0, width: BW, textAlign: "center", fontSize: 14, color: c.codeDim }}>
              vista {i + 1}
            </div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: -6, bottom: BASE + (H * K.threshold) / TOP, width: (3 * (BW + G) - G + 12) * th,
        borderTop: `2px dashed ${c.codeInk}`, opacity: 0.75 }} />
      <div style={{ position: "absolute", left: 3 * (BW + G) - G + 14, bottom: BASE + (H * K.threshold) / TOP - 9, fontSize: 14, color: c.codeInk,
        opacity: th }}>limiar {pt(K.threshold)}</div>
    </div>
  );
};

/** The registered view that matched best, next to the crop from the kit camera. */
const Pair: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.best) return null;
  const p = interpolate(frame, [T.best, T.best + 10], [0, 1], { ...clamp, easing: theme.ease.out });
  const tile = (src: string, label: string) => (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "flex-start" }}>
      <Img src={staticFile(src)} style={{ width: 128, height: 80, objectFit: "cover", borderRadius: 8, border: `1px solid ${a(c.codeInk, 0.2)}` }} />
      <div style={{ fontSize: 13, color: c.codeDim }}>{label}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 26, right: 26, bottom: 20, display: "flex", alignItems: "center", gap: 16, opacity: p }}>
      {tile(BEST_VIEW.file, `vista ${BEST + 1} · foto ${mmss(BEST_VIEW.t)}`)}
      <div style={{ fontSize: 22, color: c.codeOk, marginBottom: 22 }}>≈</div>
      {tile("real/kit-book-crop.jpg", "câmara do kit")}
      <div style={{ marginLeft: "auto", marginBottom: 22, fontSize: 30, fontWeight: 700, color: c.codeOk }}>{pt(SCORE)}</div>
    </div>
  );
};
