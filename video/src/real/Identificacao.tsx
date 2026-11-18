// 2 · Identificação: the kit camera in a camera-view card over the bright home, at real speed, then the frame the edge
// service analysed, with its real boxes and the numbers of edge.py's code against the 3-view fingerprint (R.views3).
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { VideoAt } from "./devices";
import { Heading, Overline, Typed } from "./layers";
import { clamp, Cue, look, mmss, pt, warm } from "./look";
import { R } from "./recognition";
import { BlurIn, Brackets, Glass, Plate } from "./stage";

const { c, a } = look;
const K = R.kit;
const V3 = R.views3;
const CTRL = V3.control;
const MOTION = K.motion.samples.find((m) => m.moved)!;
const PER_VIEW: number[] = [...V3.kit.per_view];
const SCORE = V3.kit.score;
const BEST = PER_VIEW.indexOf(SCORE);
const BEST_VIEW = V3.views[BEST];

// public/real/kit-desk-6s-uhd.mp4: footage/kit-desk.mp4 from 6 s to 11.5 s, with regular keyframes (so the frozen frame
// is exactly the analysed one), upscaled to 3840 x 2160 with lanczos, light sharpening and the warm grade.
const KIT_CLIP = "real/kit-desk-6s-uhd.mp4";
const KIT_T0 = 6;

const FRAME = { x: 70, y: 218, w: 1200, h: 700 };          // the camera-view card
const PAD = 12;
const CARD = { x: FRAME.x + PAD, y: FRAME.y + PAD, w: FRAME.w - 2 * PAD, h: FRAME.h - 2 * PAD };
const KS = CARD.w / 1920;
const KH = CARD.h / KS;                                     // the footage area, in 1920-wide units (slightly taller than 16:9)
const PANEL = { x: 1300, y: FRAME.y, w: 550, h: FRAME.h };

// timeline (scene frames): the live feed at real speed up to the analysed frame, then the analysis
const SRC0 = MOTION.t - 3.0;
const FREEZE = Math.round((K.frame_s - SRC0) * theme.fps);
const T = {
  motion: Math.round((MOTION.t - SRC0) * theme.fps),
  owl: FREEZE + 10, place: FREEZE + 26,
  pushIn: FREEZE + 40, pushLen: 56,
  dino: FREEZE + 70, bars: FREEZE + 86,
  best: FREEZE + 124, yours: FREEZE + 140,
  ctrl: FREEZE + 188, ctrlRes: FREEZE + 200,
};
export const IDENT_FRAMES = FREEZE + 262;
export const IDENT_CUES: Cue[] = [
  { at: 0, file: "whooshBig" },
  { at: 8, file: "whoosh", volume: 0.7 },
  { at: T.motion, file: "tap", volume: 0.7 },
  { at: FREEZE - 1, file: "shutterCam" },
  { at: T.owl, file: "lockon" },
  { at: T.pushIn, file: "whoosh" },
  { at: T.pushIn + T.pushLen - 6, file: "lockonBig" },
  { at: T.bars, file: "tapAlt" },
  { at: T.yours - 1, file: "swipe", volume: 0.8 },
  { at: T.ctrl, file: "tap" },
];

const center = (b: readonly number[]) => [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2];
const BOOK_C = center(K.book_box);

const CodeLine: React.FC<{ at: number; text: string; color?: string; indent?: number; bold?: boolean }> = ({
  at, text, color = c.ink, indent = 0, bold,
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

  // the card arrives; the camera tightens on the desk, then pushes in slowly on the book
  const cardIn = spring({ frame: frame - 2, fps, config: { damping: 18, stiffness: 80, mass: 1 } });
  const push = interpolate(frame, [T.pushIn, T.pushIn + T.pushLen], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const z = 1.12 * interpolate(push, [0, 1], [1, 1.32]) + interpolate(frame, [0, T.pushIn], [0, 0.03], clamp);
  const focus = [960 + (BOOK_C[0] - 120 - 960) * push, 470 + (BOOK_C[1] - 30 - 470) * push];
  const hw = 960 / z;
  const hh = KH / 2 / z;
  const px = Math.min(1920 - hw, Math.max(hw, focus[0]));
  const py = Math.min(1080 - hh, Math.max(hh, focus[1]));
  const toS = (x: number, y: number) => [CARD.x + KS * ((x - px) * z + 960), CARD.y + KS * ((y - py) * z + KH / 2)];
  const rectS = (b: readonly number[]) => {
    const [x0, y0] = toS(b[0], b[1]);
    const [x1, y1] = toS(b[2], b[3]);
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  };
  const fade = (at: number, len = 8) => interpolate(frame, [at, at + len], [0, 1], { ...clamp, easing: theme.ease.out });
  const flash = interpolate(frame, [FREEZE - 1, FREEZE, FREEZE + 8], [0, 0.45, 0], clamp);

  const book = rectS(K.book_box);
  const place = rectS(K.place_box!);
  const ctrl = rectS(CTRL.box!);
  const lock = spring({ frame: frame - (T.pushIn + T.pushLen - 6), fps, config: theme.spring.snappy });
  const candO = fade(T.owl) * (1 - Math.min(1, lock * 1.5));
  const placeO = fade(T.place) * interpolate(push, [0.2, 0.6], [1, 0], clamp);
  const yours = spring({ frame: frame - T.yours, fps, config: theme.spring.smooth });
  const ctrlO = fade(T.ctrl, 10);
  const lockPad = 26 * (1 - lock) + 8;

  return (
    <AbsoluteFill>
      <Plate dur={IDENT_FRAMES} offset={1} blur={16} zoom={[1.1, 1.16]} pan={[-30, 30]} />

      <div style={{ position: "absolute", left: FRAME.x, top: 70, display: "flex", flexDirection: "column", gap: 10 }}>
        <BlurIn at={4}><Overline>2 · Identificação</Overline></BlurIn>
        <BlurIn at={8}><Heading size={56}>A câmara do kit, no laboratório</Heading></BlurIn>
      </div>

      {/* the camera-view card */}
      <div style={{ position: "absolute", left: FRAME.x, top: FRAME.y, width: FRAME.w, height: FRAME.h, opacity: cardIn,
        transform: `perspective(2400px) translateY(${(1 - cardIn) * 50}px) rotateX(${(1 - cardIn) * 8}deg) scale(${0.96 + 0.04 * cardIn})` }}>
        <Glass strong style={{ position: "absolute", inset: 0, borderRadius: 30 }} />
        <div style={{ position: "absolute", left: PAD, top: PAD, width: CARD.w, height: CARD.h, borderRadius: 20, overflow: "hidden", background: c.bgAlt }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: KH, transformOrigin: "0 0",
            transform: `scale(${KS}) translate(${960 - px * z}px, ${KH / 2 - py * z}px) scale(${z})` }}>
            <div style={{ width: 1920, height: 1080 }}>
              <VideoAt src={KIT_CLIP} second={src - KIT_T0} />
            </div>
          </div>
          <AbsoluteFill style={{ background: c.white, opacity: flash }} />
          {/* HUD */}
          <svg width={CARD.w} height={CARD.h} style={{ position: "absolute", inset: 0 }}>
            <Brackets x={22} y={22} w={CARD.w - 44} h={CARD.h - 44} len={34} width={3} opacity={0.85} />
          </svg>
          <div style={{ position: "absolute", left: 44, top: 40, display: "flex", gap: 10, alignItems: "center", padding: "8px 14px", borderRadius: 999,
            background: a(c.ink, 0.42), color: c.white, fontFamily: theme.fonts.mono, fontSize: 17 }}>
            <span style={{ width: 10, height: 10, borderRadius: 10, background: frozen ? c.labs : c.alert,
              opacity: frozen ? 1 : 0.6 + 0.4 * Math.cos(frame / 5) }} />
            {frozen ? "imagem analisada" : "REC"} · Câmara do kit · Laboratório
          </div>
          <div style={{ position: "absolute", right: 44, top: 40, padding: "8px 14px", borderRadius: 999, background: a(c.ink, 0.42), color: c.white,
            fontFamily: theme.fonts.mono, fontSize: 17, fontVariantNumeric: "tabular-nums" }}>
            18 nov 2026 · 16:30{frozen ? "" : ` · ${mmss(src)}`}
          </div>
        </div>
      </div>

      {/* boxes, in screen space, clipped to the footage */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: cardIn }}>
        <defs>
          <clipPath id="kitcard"><rect x={CARD.x} y={CARD.y} width={CARD.w} height={CARD.h} rx={20} /></clipPath>
        </defs>
        <g clipPath="url(#kitcard)">
          {placeO > 0 ? (
            <g opacity={placeO}>
              <rect x={place.x} y={place.y} width={place.w} height={place.h} rx={6} fill="none" stroke={c.white} strokeWidth={2} strokeDasharray="10 8" />
              <rect x={place.x + 8} y={place.y + 8} width={190} height={28} rx={8} fill={a(c.ink, 0.55)} />
              <text x={place.x + 18} y={place.y + 28} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>secretária · {pt(K.place_score!)}</text>
            </g>
          ) : null}
          {candO > 0 ? (
            <g opacity={candO}>
              <rect x={book.x} y={book.y} width={book.w} height={book.h} rx={4} fill="none" stroke={c.labs} strokeWidth={3} />
              <rect x={book.x} y={book.y - 32} width={150} height={27} rx={8} fill={c.labs} />
              <text x={book.x + 10} y={book.y - 13} fill={c.white} fontFamily={theme.fonts.mono} fontSize={16}>livro? · {pt(K.owl_score)}</text>
            </g>
          ) : null}
          {lock > 0.01 ? (
            <g opacity={Math.min(1, lock * 1.4)}>
              <rect x={book.x - lockPad} y={book.y - lockPad} width={book.w + 2 * lockPad} height={book.h + 2 * lockPad} rx={12}
                fill={a(c.labs, 0.08)} stroke="none" />
              <Brackets x={book.x - lockPad} y={book.y - lockPad} w={book.w + 2 * lockPad} h={book.h + 2 * lockPad} len={26} color={c.labs} width={5} />
            </g>
          ) : null}
          {ctrlO > 0 ? (
            <rect x={ctrl.x} y={ctrl.y} width={ctrl.w} height={ctrl.h} rx={6} fill="none" stroke={c.alert} strokeWidth={3} strokeDasharray="9 6" opacity={ctrlO} />
          ) : null}
        </g>
      </svg>
      {yours > 0.01 ? (
        <div style={{ position: "absolute", left: book.x + book.w / 2, top: book.y - lockPad - 14, opacity: Math.min(1, yours * 1.3),
          transform: `translate(-50%, -100%) translateY(${(1 - yours) * 14}px) scale(${0.9 + 0.1 * yours})`, transformOrigin: "50% 100%",
          padding: "10px 18px", borderRadius: 14, background: c.labs, color: c.white, fontFamily: theme.fonts.display, fontSize: 28, fontWeight: 600,
          whiteSpace: "nowrap", boxShadow: `0 14px 30px -12px ${a(c.labsDeep, 0.55)}` }}>
          Livro · é o teu <span style={{ fontFamily: theme.fonts.mono, fontWeight: 500, fontSize: 23 }}>{pt(SCORE)}</span>
        </div>
      ) : null}
      {ctrlO > 0 ? (
        <div style={{ position: "absolute", left: ctrl.x + ctrl.w / 2, top: ctrl.y - 12, transform: `translate(-50%, -100%) translateY(${(1 - ctrlO) * 10}px)`,
          opacity: ctrlO, padding: "7px 13px", borderRadius: 10, background: c.white, color: c.alert, fontFamily: theme.fonts.mono, fontSize: 20,
          fontWeight: 500, whiteSpace: "nowrap", border: `2px solid ${c.alert}` }}>
          garrafa · {pt(CTRL.score!)} &lt; {pt(K.threshold)}
        </div>
      ) : null}

      {/* the edge service's analysis, on a light panel */}
      {(() => {
        const p = spring({ frame: frame - 8, fps, config: { damping: 18, stiffness: 80, mass: 1 } });
        return (
          <div style={{ position: "absolute", left: PANEL.x, top: PANEL.y, width: PANEL.w, height: PANEL.h, opacity: p,
            transform: `translateX(${(1 - p) * 60}px)` }}>
            <Glass strong style={{ position: "absolute", inset: 0, borderRadius: 30 }} />
            <div style={{ position: "absolute", inset: 0, padding: "26px 30px", boxSizing: "border-box", fontFamily: theme.fonts.mono, fontSize: 19,
              lineHeight: 1.6, color: c.ink }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, color: c.inkDim, fontSize: 16 }}>
                {[0, 1, 2].map((i) => <span key={i} style={{ width: 10, height: 10, borderRadius: 10, background: a(c.ink, 0.14) }} />)}
                <span style={{ marginLeft: 8 }}>edge.py · análise desta imagem</span>
              </div>
              <CodeLine at={8} text="à espera de movimento…" color={c.inkDim} />
              <CodeLine at={T.motion} text={`movimento ${pt(MOTION.changed * 100)} % > 0,6 % → analisar`} />
              <CodeLine at={T.owl} text={`OWLv2   "${R.query}"`} bold />
              <CodeLine at={T.owl + 8} text={`1 candidato · confiança ${pt(K.owl_score)}`} indent={1} color={c.inkDim} />
              <CodeLine at={T.place} text={`lugar: secretária · ${pt(K.place_score!)}`} indent={1} color={c.inkDim} />
              <CodeLine at={T.dino} text="DINOv2  semelhança com as 3 vistas" bold />
              <Bars />
              <CodeLine at={T.best} text={`máx. ${pt(SCORE)} · vista ${BEST + 1}`} indent={1} />
              <CodeLine at={T.yours} text={`${pt(SCORE)} ≥ ${pt(K.threshold)} → Livro · é o teu`} color={c.labs} bold />
              <CodeLine at={T.ctrl} text={`controlo "${CTRL.query}"`} color={c.inkDim} />
              <CodeLine at={T.ctrlRes} text={`garrafa ${pt(CTRL.score!)} < ${pt(K.threshold)} → não é`} indent={1} color={c.alert} />
              <Pair />
            </div>
          </div>
        );
      })()}
    </AbsoluteFill>
  );
};

const Bars: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.bars - 2) return null;
  const H = 104;
  const BW = 78;
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
            <div style={{ position: "absolute", left: i * (BW + G), bottom: BASE, width: BW, height: (H * v * p) / TOP, borderRadius: 6,
              background: ok ? c.labs : a(c.inkDim, 0.28) }} />
            <div style={{ position: "absolute", left: i * (BW + G), bottom: 20, width: BW, textAlign: "center", fontSize: 17, fontWeight: 700,
              color: ok ? c.labs : c.ink, opacity: p }}>{pt(v)}</div>
            <div style={{ position: "absolute", left: i * (BW + G), bottom: 0, width: BW, textAlign: "center", fontSize: 14, color: c.inkDim }}>vista {i + 1}</div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: -6, bottom: BASE + (H * K.threshold) / TOP, width: (3 * (BW + G) - G + 12) * th,
        borderTop: `2px dashed ${a(c.ink, 0.55)}` }} />
      <div style={{ position: "absolute", left: 3 * (BW + G) - G + 14, bottom: BASE + (H * K.threshold) / TOP - 9, fontSize: 14, color: c.ink, opacity: th }}>
        limiar {pt(K.threshold)}
      </div>
    </div>
  );
};

/** The registered view that matched best, next to the crop from the kit camera. */
const Pair: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.best) return null;
  const p = interpolate(frame, [T.best, T.best + 12], [0, 1], { ...clamp, easing: theme.ease.out });
  const tile = (src: string, label: string) => (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "flex-start" }}>
      <Img src={staticFile(src)} style={{ width: 132, height: 82, objectFit: "cover", borderRadius: 10,
        boxShadow: `0 10px 20px -12px ${a(warm.shadow, 0.6)}` }} />
      <div style={{ fontSize: 13, color: c.inkDim }}>{label}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 30, right: 30, bottom: 24, display: "flex", alignItems: "center", gap: 16, opacity: p,
      transform: `translateY(${(1 - p) * 12}px)` }}>
      {tile(BEST_VIEW.file, `vista ${BEST + 1} · foto ${mmss(BEST_VIEW.t)}`)}
      <div style={{ fontSize: 22, color: c.labs, marginBottom: 22 }}>≈</div>
      {tile("real/kit-book-crop.jpg", "câmara do kit")}
      <div style={{ marginLeft: "auto", marginBottom: 22, fontSize: 32, fontWeight: 700, color: c.labs }}>{pt(SCORE)}</div>
    </div>
  );
};
