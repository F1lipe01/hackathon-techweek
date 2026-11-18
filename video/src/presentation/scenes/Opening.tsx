// 1–2. Hook and brand. A question in big type; the real kit camera on the desk, pushing in on the book; viewfinder
// corners close around the book and fly out of the footage to become the ThingTracker mark.
import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { useRecognition } from "../data";
import { alpha, shadow } from "../tokens";
import { Brackets, MarkDots, Sfx, WordReveal, clamp, mix, ramp, useSec } from "../ui";

export const OPENING_FRAMES = 330;

const CARD = { x: 280, y: 70, w: 1360, h: 765 } as const;
const MARK = { cx: 960, top: 236, size: 210 } as const;

export const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const S = useSec();
  const rec = useRecognition();
  const [kw, kh] = rec.kit.size;
  const [bx0, by0, bx1, by1] = rec.kit.book_box;
  const f = { x: (bx0 + bx1) / 2 / kw, y: (by0 + by1) / 2 / kh };

  // the question
  const qOut = ramp(frame, S(2.35), S(2.7), theme.ease.in);

  // the footage card and its slow push-in on the book
  const cardIn = spring({ frame: frame - S(2.45), fps, config: theme.spring.smooth });
  const push = ramp(frame, S(2.6), S(6.5));
  const s = mix(1, 1.9, push);
  const m = mix(0, 0.62, push);
  const cx = f.x + (0.5 - f.x) * m;
  const cy = f.y + (0.5 - f.y) * m;
  const tx = CARD.w * (cx - f.x * s);
  const ty = CARD.h * (cy - f.y * s);
  const cardOut = ramp(frame, S(6.45), S(7.0), theme.ease.in);

  // the book, in screen pixels (inside the card)
  const bookScreen = {
    x: CARD.x + tx + (bx0 / kw) * CARD.w * s,
    y: CARD.y + ty + (by0 / kh) * CARD.h * s,
    w: ((bx1 - bx0) / kw) * CARD.w * s,
    h: ((by1 - by0) / kh) * CARD.h * s,
  };
  const pad = 16;
  const r0 = { x: bookScreen.x - pad, y: bookScreen.y - pad, w: bookScreen.w + 2 * pad, h: bookScreen.h + 2 * pad };
  const u = MARK.size / 64;
  const r1 = { x: MARK.cx - MARK.size / 2 + 7 * u, y: MARK.top + 7 * u, w: 50 * u, h: 50 * u };
  const fly = ramp(frame, S(6.55), S(7.45));
  const draw = ramp(frame, S(5.5), S(6.2), theme.ease.out);
  const br = {
    x: mix(r0.x, r1.x, fly), y: mix(r0.y, r1.y, fly), w: mix(r0.w, r1.w, fly), h: mix(r0.h, r1.h, fly),
    arm: mix(Math.min(r0.w, r0.h) * 0.3, 14 * u, fly), radius: mix(8, 5 * u, fly), stroke: mix(5, 5 * u, fly),
  };
  const dots = ramp(frame, S(7.25), S(8.1), theme.ease.out);
  const breathe = 1 + Math.sin(frame / 24) * 0.01 * ramp(frame, S(8.2), S(9));

  // wordmark, letter by letter
  const word = "ThingTracker";

  return (
    <AbsoluteFill>
      <Sfx at={S(2.45)} name="whoosh" volume={0.22} />
      <Sfx at={S(6.55)} name="whoosh" volume={0.3} />
      <Sfx at={S(7.25) + 12} name="tap" volume={0.28} />
      {/* the question */}
      {qOut < 1 ? (
        <AbsoluteFill
          style={{
            justifyContent: "center", alignItems: "center",
            opacity: 1 - qOut, transform: `translateY(${-50 * qOut}px)`, filter: `blur(${6 * qOut}px)`,
          }}
        >
          <WordReveal text="Onde deixei o livro?" size={156} delay={S(0.25)} per={6} hero={["livro?"]} style={{ justifyContent: "center" }} />
        </AbsoluteFill>
      ) : null}

      {/* the kit camera */}
      {cardOut < 1 ? (
        <div
          style={{
            position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 30,
            overflow: "hidden", boxShadow: shadow.card, background: theme.colors.ink,
            opacity: interpolate(cardIn, [0, 0.6], [0, 1], clamp) * (1 - cardOut),
            transform: `translateY(${interpolate(cardIn, [0, 1], [40, 0])}px) scale(${interpolate(cardIn, [0, 1], [0.95, 1]) * (1 + 0.05 * cardOut)})`,
          }}
        >
          <div
            style={{
              position: "absolute", left: 0, top: 0, width: CARD.w, height: CARD.h, transformOrigin: "0 0",
              transform: `translate(${tx}px, ${ty}px) scale(${s})`,
            }}
          >
            <OffthreadVideo src={staticFile("footage/kit-desk.mp4")} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
          <div
            style={{
              position: "absolute", left: 28, top: 24, padding: "8px 16px", borderRadius: 999,
              background: alpha(theme.colors.ink, 0.55), color: theme.colors.white, fontFamily: theme.fonts.mono, fontSize: 20,
              opacity: interpolate(cardIn, [0.4, 1], [0, 1], clamp),
            }}
          >
            câmara do kit · 16:30
          </div>
        </div>
      ) : null}

      {/* captions under the card */}
      <div
        style={{
          position: "absolute", left: CARD.x, top: CARD.y + CARD.h + 34, width: CARD.w, display: "flex", gap: 18,
          opacity: 1 - ramp(frame, S(6.3), S(6.65), theme.ease.in),
        }}
      >
        <WordReveal text="A câmara já vê tudo." size={46} weight={500} delay={S(3.0)} per={3} />
        <WordReveal text="Só ainda não percebe o que vê." size={46} weight={500} delay={S(4.3)} per={3} color={theme.colors.inkDim} />
      </div>

      {/* the corners: around the book, then the mark */}
      {frame >= S(5.5) ? (
        <AbsoluteFill style={{ transformOrigin: `${MARK.cx}px ${MARK.top + MARK.size / 2}px`, transform: `scale(${breathe})` }}>
          <Brackets x={br.x} y={br.y} w={br.w} h={br.h} arm={br.arm} radius={br.radius} stroke={br.stroke} color={theme.colors.labs} draw={draw} />
          <div style={{ position: "absolute", left: MARK.cx - MARK.size / 2, top: MARK.top, width: MARK.size, height: MARK.size }}>
            <MarkDots size={MARK.size} dots={dots} />
          </div>
        </AbsoluteFill>
      ) : null}

      {/* wordmark and line */}
      <div
        style={{
          position: "absolute", left: 0, right: 0, top: MARK.top + MARK.size + 34, display: "flex", justifyContent: "center",
          fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 136, letterSpacing: "-0.035em", lineHeight: 1,
          color: theme.colors.ink,
        }}
      >
        {word.split("").map((ch, i) => {
          const p = spring({ frame: frame - S(7.55) - i * 1.6, fps, config: theme.spring.snappy });
          return (
            <span
              key={i}
              style={{
                display: "inline-block", opacity: interpolate(p, [0, 0.7], [0, 1], clamp),
                transform: `translateY(${interpolate(p, [0, 1], [46, 0])}px)`, filter: `blur(${interpolate(p, [0, 1], [8, 0], clamp)}px)`,
              }}
            >
              {ch}
            </span>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: MARK.top + MARK.size + 34 + 136 + 44, display: "flex", justifyContent: "center" }}>
        <WordReveal
          text="A câmara da casa passa a saber onde estão as coisas."
          size={48} weight={500} color={theme.colors.inkDim} delay={S(8.45)} per={3} tracking="-0.02em" style={{ justifyContent: "center" }}
        />
      </div>
    </AbsoluteFill>
  );
};
