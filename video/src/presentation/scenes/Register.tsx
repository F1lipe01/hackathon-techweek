// 3. Registar. The colleague's phone photographs the book; at each real shutter (recognition.json photos_taken_s) the
// OWLv2 box appears on the phone, and the real crop flies into the grid of 8 views; DINOv2 turns them into one
// visual fingerprint; the app says "Book added".
import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { useRecognition } from "../data";
import { alpha, layout, shadow } from "../tokens";
import { Entrance, Kicker, Sfx, Leave, Phone, SCREEN, SceneExit, WordReveal, clamp, mix, phoneWidth, ramp, screenSize, useSec } from "../ui";

export const REGISTER_FRAMES = 375;

const PHONE_H = 880;
const PHONE_CX = 930;
const PHONE = { x: PHONE_CX - phoneWidth(PHONE_H) / 2, y: (1080 - PHONE_H) / 2 };
const SCR = {
  x: PHONE.x + phoneWidth(PHONE_H) * SCREEN.left,
  y: PHONE.y + PHONE_H * SCREEN.top,
  ...screenSize(PHONE_H),
};
const SRC = { w: 392, h: 850 }; // phone-photos.mp4
const K = Math.max(SCR.w / SRC.w, SCR.h / SRC.h);
const OFF = { x: (SCR.w - SRC.w * K) / 2, y: (SCR.h - SRC.h * K) / 2 };

const GRID = { x: 1232, y: 368, tile: 126, gap: 16, cols: 4 } as const;
const gridW = GRID.cols * GRID.tile + (GRID.cols - 1) * GRID.gap;
const slot = (k: number) => ({
  x: GRID.x + (k % GRID.cols) * (GRID.tile + GRID.gap),
  y: GRID.y + Math.floor(k / GRID.cols) * (GRID.tile + GRID.gap),
});

const CLIP = 26;        // frames per photo in the montage
const SHUTTER = 18;     // the shutter, inside each clip
const START = 15;       // first clip
const APP_AT = 285;     // the app's "Book added"

/** Deterministic pseudo-random 0..1 for the fingerprint bars. */
const rnd = (i: number) => {
  const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};

export const Register: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const S = useSec();
  const rec = useRecognition();
  const views = rec.views.slice(0, 8);
  const shutterAt = (k: number) => START + k * CLIP + SHUTTER;
  const taken = views.filter((_, k) => frame >= shutterAt(k)).length;

  const phoneIn = spring({ frame, fps, config: theme.spring.smooth });
  const appIn = ramp(frame, APP_AT, APP_AT + 10, theme.ease.out);
  const appPush = ramp(frame, APP_AT, REGISTER_FRAMES, theme.ease.inOut);
  const printAt = START + 8 * CLIP + 10;
  const print = ramp(frame, printAt, printAt + S(1.0), theme.ease.out);

  return (
    <SceneExit duration={REGISTER_FRAMES}>
      <AbsoluteFill>
        <Sfx at={0} name="whoosh" volume={0.14} />
        {views.map((_, k) => <Sfx key={k} at={shutterAt(k)} name="shutter" volume={0.45} />)}
        <Sfx at={APP_AT} name="tap" volume={0.2} />
        {/* text column */}
        <div style={{ position: "absolute", left: layout.margin, top: 300, width: 560 }}>
          <Kicker n="01" label="Registar" delay={4} />
          <div style={{ height: 30 }} />
          <WordReveal text="Fotografa-se o livro, de vários lados." size={74} delay={10} per={4} />
          <div style={{ height: 40 }} />
          <div style={{ position: "relative", height: 140 }}>
            <Leave at={APP_AT} style={{ position: "absolute", inset: 0 }}>
              <WordReveal text="As fotografias formam a assinatura visual do livro." size={36} weight={500} color={theme.colors.inkDim} delay={printAt} per={2} tracking="-0.015em" lineHeight={1.25} />
            </Leave>
            <div style={{ position: "absolute", inset: 0 }}>
              <WordReveal text="Fica registado. A câmara passa a reconhecê-lo." size={36} weight={500} color={theme.colors.inkDim} delay={APP_AT + 12} per={2} tracking="-0.015em" lineHeight={1.25} />
            </div>
          </div>
        </div>

        {/* the phone */}
        <div
          style={{
            position: "absolute", left: PHONE.x, top: PHONE.y, transformOrigin: "50% 50%",
            opacity: interpolate(phoneIn, [0, 0.5], [0, 1], clamp),
            transform: `translateY(${interpolate(phoneIn, [0, 1], [70, 0])}px) scale(${interpolate(phoneIn, [0, 1], [0.95, 1]) * mix(1, 1.07, appPush)})`,
          }}
        >
          <Phone height={PHONE_H}>
            <AbsoluteFill style={{ background: theme.colors.ink }}>
              {views.map((v, k) => {
                const from = START + k * CLIP;
                const len = k === views.length - 1 ? APP_AT + 12 - from : CLIP;
                const trim = Math.max(0, Math.round((v.t - SHUTTER / fps) * fps));
                return (
                  <Sequence key={k} from={k === 0 ? 0 : from} durationInFrames={k === 0 ? from + len : len} layout="none">
                    <OffthreadVideo
                      src={staticFile("footage/phone-photos.mp4")} muted trimBefore={k === 0 ? Math.max(0, trim - START) : trim}
                      style={{ position: "absolute", left: OFF.x, top: OFF.y, width: SRC.w * K, height: SRC.h * K }}
                    />
                  </Sequence>
                );
              })}
              {/* shutter flash */}
              {views.map((_, k) => {
                const t = frame - shutterAt(k);
                if (t < 0 || t > 7) return null;
                return <AbsoluteFill key={k} style={{ background: theme.colors.white, opacity: interpolate(t, [0, 7], [0.75, 0], { ...clamp, easing: theme.ease.out }) }} />;
              })}
              {/* the OWLv2 box on the photo being taken */}
              {views.map((v, k) => {
                const t = frame - shutterAt(k);
                if (t < -7 || t > CLIP - SHUTTER - 1) return null;
                const [x0, y0, x1, y1] = v.box_phone_px;
                const p = interpolate(t, [-7, 0], [0, 1], { ...clamp, easing: theme.ease.out });
                const bx = OFF.x + Math.max(2, x0) * K;
                const by = OFF.y + y0 * K;
                const bw = (Math.min(SRC.w - 2, x1) - Math.max(2, x0)) * K;
                const bh = (y1 - y0) * K;
                return (
                  <div key={k} style={{ position: "absolute", left: bx, top: by, width: bw, height: bh, opacity: p, transform: `scale(${mix(1.06, 1, p)})` }}>
                    <div style={{ position: "absolute", inset: 0, border: `3px solid ${theme.colors.labs}`, borderRadius: 8 }} />
                    <div
                      style={{
                        position: "absolute", left: -1, top: -30, padding: "3px 9px", borderRadius: 6, background: theme.colors.labs,
                        color: theme.colors.white, fontFamily: theme.fonts.mono, fontSize: 15, fontWeight: 500,
                      }}
                    >
                      book
                    </div>
                  </div>
                );
              })}
              {/* the app: Book added */}
              {frame >= APP_AT ? (
                <AbsoluteFill style={{ opacity: appIn }}>
                  <OffthreadVideo src={staticFile("footage/app-book.mp4")} muted trimBefore={Math.round(20.85 * fps) - APP_AT} style={{ width: "100%", height: "100%" }} />
                </AbsoluteFill>
              ) : null}
            </AbsoluteFill>
          </Phone>
        </div>

        {/* the grid of views */}
        <div style={{ position: "absolute", left: GRID.x, top: GRID.y - 58, width: gridW, display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <Entrance delay={20} rise={16}>
            <span style={{ fontFamily: theme.fonts.display, fontSize: 28, fontWeight: 600, color: theme.colors.ink, letterSpacing: "-0.01em" }}>Vistas</span>
          </Entrance>
          <Entrance delay={24} rise={16}>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 22, color: theme.colors.inkDim, fontVariantNumeric: "tabular-nums" }}>{taken} de 8</span>
          </Entrance>
        </div>
        {views.map((_, k) => {
          const p = spring({ frame: frame - 24 - k * 3, fps, config: theme.spring.smooth });
          const { x, y } = slot(k);
          return (
            <div
              key={k}
              style={{
                position: "absolute", left: x, top: y, width: GRID.tile, height: GRID.tile, borderRadius: 18,
                border: `2px dashed ${alpha(theme.colors.inkDim, 0.28)}`, opacity: interpolate(p, [0, 0.6], [0, 1], clamp) * (1 - ramp(frame, shutterAt(k) + 14, shutterAt(k) + 20)),
                transform: `scale(${interpolate(p, [0, 1], [0.85, 1])})`,
              }}
            />
          );
        })}
        {views.map((v, k) => {
          const t0 = shutterAt(k) + 2;
          if (frame < t0) return null;
          const p = spring({ frame: frame - t0, fps, config: theme.spring.smooth });
          const [x0, y0, x1, y1] = v.box_phone_px;
          const sc = mix(1, 1.07, appPush);
          const from = {
            x: PHONE_CX + (SCR.x + OFF.x + Math.max(0, x0) * K - PHONE_CX) * sc,
            y: 540 + (SCR.y + OFF.y + y0 * K - 540) * sc,
            w: (Math.min(SRC.w, x1) - Math.max(0, x0)) * K,
            h: (y1 - y0) * K,
          };
          const to = slot(k);
          const glow = interpolate(print, [0, 0.4, 1], [0, 1, 0.35], clamp);
          return (
            <div
              key={k}
              style={{
                position: "absolute", left: mix(from.x, to.x, p), top: mix(from.y, to.y, p),
                width: mix(from.w, GRID.tile, p), height: mix(from.h, GRID.tile, p),
                borderRadius: mix(8, 18, p), overflow: "hidden", boxShadow: shadow.soft,
                outline: `3px solid ${alpha(theme.colors.labs, glow * 0.9)}`, outlineOffset: 3,
              }}
            >
              <Img src={staticFile(v.file)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            </div>
          );
        })}

        {/* DINOv2: one visual fingerprint */}
        <div style={{ position: "absolute", left: GRID.x, top: GRID.y + 2 * GRID.tile + GRID.gap + 44, width: gridW }}>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 76 }}>
            {Array.from({ length: 56 }).map((_, i) => {
              const p = ramp(frame, printAt + i * 0.6, printAt + i * 0.6 + 12, theme.ease.out);
              const h = 12 + 64 * rnd(i);
              return <div key={i} style={{ flex: 1, height: h * p, borderRadius: 2, background: theme.colors.labs, opacity: 0.35 + 0.65 * rnd(i + 99) }} />;
            })}
          </div>
          <div
            style={{
              marginTop: 16, display: "flex", justifyContent: "space-between", fontFamily: theme.fonts.mono, fontSize: 20,
              color: theme.colors.inkDim, opacity: print, transform: `translateY(${10 * (1 - print)}px)`,
            }}
          >
            <span>DINOv2</span>
            <span>assinatura visual · 8 vistas</span>
          </div>
        </div>
      </AbsoluteFill>
    </SceneExit>
  );
};
