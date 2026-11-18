// 5–6. Perguntar and Avisar, on one phone. The app recording (footage/app-book.mp4) in three segments, with slow
// push-ins on the answer, the sentence being typed, and the notification. On the left, the words; then the rule the
// sentence became, in plain words, and the front door opening.
import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha, app, layout, shadow } from "../tokens";
import { Entrance, Kicker, Sfx, Leave, Phone, SCREEN, SceneExit, WordReveal, clamp, mix, phoneWidth, ramp } from "../ui";

export const APP_FRAMES = 583;

const PHONE_H = 960;
const PW = phoneWidth(PHONE_H);
const PHONE = { x: 1300 - PW / 2, y: 60 };

// segments of the app recording: [scene frame, source second]
const SEG = [
  { from: 0, len: 232, src: 33.4 },   // the assistant: question and answer (answer at src 39.2)
  { from: 232, len: 168, src: 43.8 }, // the sentence, sent; "Done. I created a sensor" (src 48.2)
  { from: 400, len: 33, src: 51.25 }, // the sheet closes (src 52.0–52.3)
  { from: 433, len: 150, src: 53.4 }, // the notification (slides in at src 54.6, scene frame 469)
] as const;

// camera keys on the phone: frame, scale, focus (fraction of the screen), vertical shift
type Key = { at: number; s: number; fy: number; dy: number };
const KEYS: Key[] = [
  { at: 0, s: 1, fy: 0.5, dy: 0 },
  { at: 162, s: 1, fy: 0.5, dy: 0 },
  { at: 206, s: 1.55, fy: 0.72, dy: -170 },
  { at: 226, s: 1.55, fy: 0.72, dy: -170 },
  { at: 252, s: 1, fy: 0.72, dy: 0 },
  { at: 262, s: 1, fy: 0.93, dy: 0 },
  { at: 296, s: 1.42, fy: 0.93, dy: -300 },
  { at: 336, s: 1.42, fy: 0.93, dy: -300 },
  { at: 366, s: 1.32, fy: 0.74, dy: -150 },
  { at: 398, s: 1.32, fy: 0.74, dy: -150 },
  { at: 424, s: 1, fy: 0.5, dy: 0 },
  { at: 466, s: 1, fy: 0.09, dy: 0 },
  { at: 506, s: 1.6, fy: 0.09, dy: 250 },
  { at: APP_FRAMES, s: 1.66, fy: 0.09, dy: 250 },
];

const camAt = (frame: number) => {
  let i = 0;
  while (i < KEYS.length - 2 && frame >= KEYS[i + 1].at) i++;
  const a = KEYS[i];
  const b = KEYS[i + 1];
  const t = ramp(frame, a.at, b.at, theme.ease.inOut);
  return { s: mix(a.s, b.s, t), fy: mix(a.fy, b.fy, t), dy: mix(a.dy, b.dy, t) };
};

const RuleRow: React.FC<{ k: string; v: string; delay: number }> = ({ k, v, delay }) => (
  <Entrance delay={delay} rise={18}>
    <div style={{ display: "grid", gridTemplateColumns: "118px 1fr", alignItems: "baseline", padding: "13px 0", borderTop: `1px solid ${alpha(theme.colors.ink, 0.08)}` }}>
      <span style={{ fontFamily: theme.fonts.display, fontSize: 24, fontWeight: 500, color: theme.colors.inkDim }}>{k}</span>
      <span style={{ fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, color: theme.colors.ink, letterSpacing: "-0.015em", lineHeight: 1.2 }}>{v}</span>
    </div>
  </Entrance>
);

const Door: React.FC<{ delay: number; openAt: number }> = ({ delay, openAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const open = spring({ frame: frame - openAt, fps, config: theme.spring.snappy });
  return (
    <Entrance delay={delay} rise={18}>
      <div
        style={{
          display: "flex", alignItems: "center", gap: 22, padding: "20px 26px", borderRadius: 24, background: theme.colors.white,
          boxShadow: shadow.soft, width: 560, boxSizing: "border-box",
        }}
      >
        {/* a door, drawn: the frame and a leaf that swings open */}
        <svg viewBox="0 0 40 48" width={46} height={56}>
          <rect x="6" y="3" width="28" height="42" rx="2.5" fill="none" stroke={theme.colors.inkDim} strokeWidth="2.6" />
          <g style={{ transformOrigin: "8px 24px", transform: `perspective(80px) rotateY(${-58 * Math.min(1, open)}deg)` }}>
            <rect x="8" y="5" width="24" height="38" rx="1.5" fill={open > 0.05 ? alpha(theme.colors.labs, 0.18) : alpha(theme.colors.inkDim, 0.14)} stroke={theme.colors.ink} strokeWidth="2.4" />
            <circle cx="27" cy="25" r="1.8" fill={theme.colors.ink} />
          </g>
        </svg>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 28, fontWeight: 600, color: theme.colors.ink, letterSpacing: "-0.01em" }}>Porta da entrada</div>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 22, color: theme.colors.inkDim, marginTop: 2 }}>sensor de contacto do kit</div>
        </div>
        <div style={{ position: "relative", width: 128, height: 44 }}>
          {[
            { t: "fechada", o: 1 - open, bg: alpha(theme.colors.inkDim, 0.12), c: theme.colors.inkDim },
            { t: "aberta", o: open, bg: theme.colors.labs, c: theme.colors.white },
          ].map((st) => (
            <div
              key={st.t}
              style={{
                position: "absolute", inset: 0, display: "grid", placeItems: "center", borderRadius: 999, background: st.bg, color: st.c,
                fontFamily: theme.fonts.display, fontSize: 22, fontWeight: 600, opacity: interpolate(st.o, [0, 1], [0, 1], clamp),
                transform: `translateY(${(1 - st.o) * (st.t === "aberta" ? 10 : -10)}px)`,
              }}
            >
              {st.t}
            </div>
          ))}
        </div>
      </div>
    </Entrance>
  );
};

export const AppScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const phoneIn = spring({ frame, fps, config: theme.spring.smooth });
  const cam = camAt(frame);
  const focusY = PHONE_H * SCREEN.top + cam.fy * PHONE_H * SCREEN.height;

  return (
    <SceneExit duration={APP_FRAMES}>
      <AbsoluteFill>
        <Sfx at={0} name="whoosh" volume={0.14} />
        <Sfx at={18} name="tap" volume={0.2} />
        <Sfx at={452} name="tap" volume={0.25} />
        <Sfx at={469} name="chime" volume={0.32} />
        {/* phase A: Perguntar */}
        <Leave at={220} style={{ position: "absolute", left: layout.margin, top: 300, width: 640 }}>
          <Kicker n="03" label="Perguntar" delay={6} />
          <div style={{ height: 30 }} />
          <WordReveal text="Basta perguntar." size={96} delay={12} per={5} />
          <div style={{ height: 34 }} />
          <WordReveal text="“Onde está o meu livro?”" size={46} weight={500} delay={96} per={3} tracking="-0.02em" />
          <div style={{ height: 22 }} />
          <WordReveal text="A resposta traz o lugar, a hora e a fotografia." size={38} weight={500} color={theme.colors.inkDim} delay={176} per={2} lineHeight={1.25} tracking="-0.015em" />
        </Leave>

        {/* phase B: Avisar */}
        {frame >= 232 ? (
          <div style={{ position: "absolute", left: layout.margin, top: 150, width: 600 }}>
            <Kicker n="04" label="Avisar" delay={236} />
            <div style={{ height: 26 }} />
            <WordReveal text="Uma frase passa a ser um sensor." size={76} delay={240} per={4} />
            <div style={{ height: 36 }} />
            {frame >= 360 ? (
              <div style={{ width: 560 }}>
                <RuleRow k="Quando" v="a porta da entrada abrir" delay={368} />
                <RuleRow k="Se" v="o livro ainda estiver na secretária" delay={374} />
                <RuleRow k="Então" v="avisar no telemóvel" delay={380} />
              </div>
            ) : null}
            <div style={{ height: 28 }} />
            {frame >= 428 ? <Door delay={432} openAt={452} /> : null}
            <div style={{ height: 30 }} />
            <WordReveal text="A IA escreve a regra; a regra corre em casa." size={34} weight={500} color={theme.colors.inkDim} delay={500} per={2} tracking="-0.015em" style={{ width: 700 }} />
          </div>
        ) : null}

        {/* the phone */}
        <div
          style={{
            position: "absolute", left: PHONE.x, top: PHONE.y, width: PW, height: PHONE_H,
            opacity: interpolate(phoneIn, [0, 0.5], [0, 1], clamp),
            transformOrigin: `50% ${focusY}px`,
            transform: `translateY(${interpolate(phoneIn, [0, 1], [80, 0]) + cam.dy}px) scale(${cam.s * interpolate(phoneIn, [0, 1], [0.95, 1])})`,
          }}
        >
          <Phone height={PHONE_H}>
            <AbsoluteFill style={{ background: app.bg }}>
              {SEG.map((g, i) => (
                <Sequence key={i} from={g.from} durationInFrames={g.len} layout="none">
                  <OffthreadVideo src={staticFile("footage/app-book.mp4")} muted trimBefore={Math.round(g.src * fps)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
                </Sequence>
              ))}
            </AbsoluteFill>
          </Phone>
        </div>
      </AbsoluteFill>
    </SceneExit>
  );
};
