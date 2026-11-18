// Shot 3. After the stop, the first calm shot: the keys on the hall table (stock, slowed). The brackets lock on the
// keys, the camera pushes in, then the corners leave the footage and close into the ThingTracker mark.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { SmallPrint, Title, useOneLine } from "../type";
import { Brackets, Daylight, LockBox, MarkDots, Paper, Track, clamp, mix, ramp, trackAt } from "../ui";
import { StockStill } from "../stock";
import { Sfx } from "../sound";
import { SHOT_FRAMES, onBeat } from "../timeline";

export const BRAND_FRAMES = SHOT_FRAMES.brand;
const B = (n: number) => onBeat("brand", n);

const MARK = 150;
const GAP = 34;
const WORD = 124;
const LOCK_Y = 380;
// the keys on the hall table (leaving-home-keys-1, frame fractions), before the hand comes in at 1,8 s
const KEYS: Track = [[0, 0.256, 0.575, 0.541, 0.668], [1.6, 0.25, 0.575, 0.535, 0.668]];

/** The ThingTracker lockup: mark + wordmark, centred. */
export const useLockup = () => {
  const w = useOneLine("ThingTracker", WORD, 600, -0.035, 1500) ?? 720;
  const left = (1920 - (MARK + GAP + w)) / 2;
  return { left, top: LOCK_Y, wordLeft: left + MARK + GAP, wordWidth: w };
};

export const Wordmark: React.FC<{ at: number; left: number; top: number }> = ({ at, left, top }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ position: "absolute", left, top: top + (MARK - WORD) / 2 - 4, display: "flex", fontFamily: theme.fonts.display, fontWeight: 600, fontSize: WORD, letterSpacing: "-0.035em", lineHeight: 1, color: theme.colors.ink, whiteSpace: "nowrap" }}>
      {"ThingTracker".split("").map((ch, i) => {
        const p = spring({ frame: frame - at - i * 1.4, fps, config: theme.spring.snappy });
        return (
          <span key={i} style={{ display: "inline-block", opacity: interpolate(p, [0, 0.6], [0, 1], clamp), transform: `translateX(${-18 * (1 - p)}px)`, filter: `blur(${6 * (1 - p)}px)` }}>
            {ch}
          </span>
        );
      })}
    </div>
  );
};

export const Brand: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lock = useLockup();
  const keys = trackAt(KEYS, 0);
  const f = { x: (keys.x + keys.w / 2) / 1920, y: (keys.y + keys.h / 2) / 1080 };

  const push = ramp(frame, B(1), B(5), theme.ease.inOut);
  const s = mix(1, 1.85, push);
  const m = mix(0, 0.75, push);
  const cx = f.x + (0.5 - f.x) * m;
  const cy = f.y + (0.5 - f.y) * m;
  const tx = 1920 * (cx - f.x * s);
  const ty = 1080 * (cy - f.y * s);
  const kr = { x: tx + keys.x * s, y: ty + keys.y * s, w: keys.w * s, h: keys.h * s };

  const toPaper = ramp(frame, B(5) - 2, B(6), theme.ease.inOut);
  const fly = ramp(frame, B(5), B(6) + 8, theme.ease.inOut);
  const u = MARK / 64;
  const pad = 10;
  const r0 = { x: kr.x - pad, y: kr.y - pad, w: kr.w + 2 * pad, h: kr.h + 2 * pad };
  const r1 = { x: lock.left + 7 * u, y: lock.top + 7 * u, w: 50 * u, h: 50 * u };

  return (
    <AbsoluteFill>
      <Sfx at={B(1)} role="lockon" volume={0.45} />
      <Sfx at={B(1) + 4} role="whoosh-long" volume={0.2} lead={0} />
      <Sfx at={B(5)} role="whoosh" volume={0.32} />
      <Sfx at={B(7)} role="boom" variant={1} volume={0.45} lead={3} />
      <AbsoluteFill style={{ opacity: 1 - toPaper }}>
        <AbsoluteFill style={{ transformOrigin: "0 0", transform: `translate(${tx}px, ${ty}px) scale(${s})` }}>
          <Daylight lift={1.1}>
            <StockStill name="hall-keys" />
          </Daylight>
        </AbsoluteFill>
        {frame < B(5) ? <LockBox r={kr} at={B(1)} label="chaves" size={26} fadeAt={B(5) - 6} /> : null}
        <SmallPrint text="imagens de arquivo" dark style={{ right: 60, bottom: 44 }} />
      </AbsoluteFill>
      {toPaper > 0 ? (
        <AbsoluteFill style={{ opacity: toPaper }}>
          <Paper />
        </AbsoluteFill>
      ) : null}
      {frame >= B(5) - 6 ? (
        <>
          <Brackets
            x={mix(r0.x, r1.x, fly)} y={mix(r0.y, r1.y, fly)} w={mix(r0.w, r1.w, fly)} h={mix(r0.h, r1.h, fly)}
            arm={mix(Math.min(r0.w, r0.h) * 0.28, 14 * u, fly)} radius={mix(6, 5 * u, fly)} stroke={mix(4.5, 5 * u, fly)} color={theme.colors.labs}
          />
          <div style={{ position: "absolute", left: lock.left, top: lock.top, width: MARK, height: MARK }}>
            <MarkDots size={MARK} dots={ramp(frame, B(6), B(7), theme.ease.out)} />
          </div>
          <Wordmark at={B(6) + 4} left={lock.wordLeft} top={lock.top} />
          <div style={{ position: "absolute", left: 0, right: 0, top: lock.top + MARK + 70, display: "flex", justifyContent: "center" }}>
            <Title text="A câmara da casa passa a saber onde estão as coisas." size={46} max={1600} weight={500} at={B(6) + 12} entrance="words" color={theme.colors.inkDim} tracking={-0.02} align="center" />
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};
