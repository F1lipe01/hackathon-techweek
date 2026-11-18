// 3 · Pergunta and 4 · Sensor: our app (a copy of the Altice app, simulated data), recorded on screen.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { IPHONE, IPhone, VideoAt } from "./devices";
import { Body, Chip, Heading, Overline, Rise } from "./layers";
import { clamp, Cue, look } from "./look";
import { buildMap, frameOf, srcAt } from "./timemap";

const { c, a } = look;
// footage/app-book.mp4 from 33 s, re-encoded with regular keyframes (the original's sparse full-range keyframes made
// Remotion show frames seconds off). Times below stay in the original recording's seconds.
const APP = "real/app-book-33s.mp4";
const APP_T0 = 33;
// app-book.marks.json, plus the moments measured on the frames: the replies appear at 39.2 and 48.2,
// the sensor fires at 53.94 (mark "alert") and the notification banner slides in at 54.55.
const MARK = { typeQ: 35.117, sentQ: 37.73, answerQ: 39.2, typeS: 42.816, sentS: 46.752, answerS: 48.2, door: 53.943, alert: 54.55 };

/** Speed by source second: [until, speed] segments, blended over `ramp` seconds at each boundary. */
const piecewise = (segs: [number, number][], ramp = 0.35) => (s: number) => {
  let i = segs.findIndex(([until]) => s < until);
  if (i < 0) i = segs.length - 1;
  const [until, v] = segs[i];
  const next = segs[i + 1];
  if (next && s > until - ramp) {
    const t = (s - (until - ramp)) / ramp;
    return v + (next[1] - v) * t * t * (3 - 2 * t);
  }
  return v;
};

const PHONE_H = 960;
const PK = PHONE_H / IPHONE.h;
const PHONE_W = IPHONE.w * PK;
const PHONE_X = 1300 - PHONE_W / 2;
const PHONE_Y = (1080 - PHONE_H) / 2;

/** The phone with the app, zoomed on a point of its screen (u, v in 0..1) and moved to (tx, ty) on screen. */
const AppPhone: React.FC<{ second: number; zoom: number; u: number; v: number; tx: number; ty: number; enter: number }> = ({
  second, zoom, u, v, tx, ty, enter,
}) => {
  const fx = (IPHONE.sx + u * IPHONE.sw) * PK;
  const fy = (IPHONE.sy + v * IPHONE.sh) * PK;
  const dx = (tx - (PHONE_X + fx)) * (zoom - 1) / Math.max(0.001, zoom - 1);
  const dy = (ty - (PHONE_Y + fy)) * (zoom - 1) / Math.max(0.001, zoom - 1);
  const k = Math.min(1, (zoom - 1) / 0.8);
  return (
    <div style={{ position: "absolute", left: PHONE_X, top: PHONE_Y, transformOrigin: `${fx}px ${fy}px`, opacity: enter,
      transform: `translate(${dx * k}px, ${dy * k + interpolate(enter, [0, 1], [60, 0])}px) scale(${zoom})` }}>
      <IPhone height={PHONE_H}>
        <VideoAt src={APP} second={second - APP_T0} />
      </IPhone>
    </div>
  );
};

const LeftColumn: React.FC<{ children: React.ReactNode; width?: number }> = ({ children, width = 760 }) => (
  <div style={{ position: "absolute", left: 140, top: 0, bottom: 0, width, display: "flex", flexDirection: "column", justifyContent: "center", gap: 22 }}>
    {children}
  </div>
);

const Prototype: React.FC<{ delay: number }> = ({ delay }) => (
  <Rise delay={delay}>
    <Chip mono bg={a(c.white, 0.8)} color={c.inkDim} style={{ fontSize: 17 }}>Interface: protótipo · dados simulados</Chip>
  </Rise>
);

// ---------------------------------------------------------------- 3 · Pergunta
const QMAP = buildMap(33.75, 41.0, piecewise([[35.05, 1], [37.65, 2.2], [99, 1]]));
const Q_HOLD = 56;
export const PERGUNTA_FRAMES = 6 + QMAP.length + Q_HOLD;
export const PERGUNTA_SFX: Cue[] = [{ at: 6 + frameOf(QMAP, MARK.answerQ), file: "tick.wav", volume: 0.4 }];

export const Pergunta: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - 6;
  const src = srcAt(QMAP, f);
  const enter = spring({ frame, fps, config: theme.spring.smooth });
  const ansF = frameOf(QMAP, MARK.answerQ);
  const z = interpolate(f, [frameOf(QMAP, MARK.sentQ) + 4, ansF + 22], [1, 1.7], { ...clamp, easing: theme.ease.inOut });
  const ans = spring({ frame: f - ansF - 6, fps, config: theme.spring.smooth });
  return (
    <AbsoluteFill>
      <AppPhone second={src} zoom={z} u={0.42} v={0.5} tx={1290} ty={560} enter={enter} />
      <LeftColumn>
        <Rise delay={4}><Overline>3 · Pergunta</Overline></Rise>
        <Rise delay={8}><Heading size={64}>“Onde está o meu livro?”</Heading></Rise>
        <Rise delay={12}><Body size={28}>Uma pergunta ao assistente da app. A resposta traz o lugar, a hora e a fotografia.</Body></Rise>
        <div style={{ opacity: ans, transform: `translateY(${interpolate(ans, [0, 1], [24, 0])}px)`, marginTop: 8, padding: "20px 24px",
          borderRadius: 18, background: c.white, border: look.cardBorder, boxShadow: `0 18px 40px -24px ${a(c.ink, 0.45)}`, maxWidth: 620 }}>
          <div style={{ fontFamily: theme.fonts.mono, fontSize: 17, color: c.inkDim, marginBottom: 6 }}>resposta</div>
          <div style={{ fontFamily: theme.fonts.display, fontSize: 32, fontWeight: 500, color: c.ink, lineHeight: 1.25 }}>
            Na secretária, na Work Room, às 16:30.
          </div>
        </div>
        <Prototype delay={18} />
      </LeftColumn>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 4 · Sensor
const SMAP = buildMap(42.55, 57.0, piecewise([[46.45, 2.6], [48.9, 1], [53.5, 7], [53.85, 1], [54.5, 0.45], [99, 1]], 0.25));
const S_HOLD = 46;
export const SENSOR_FRAMES = 6 + SMAP.length + S_HOLD;
export const SENSOR_SFX: Cue[] = [
  { at: 6 + frameOf(SMAP, MARK.answerS), file: "confirm.wav", volume: 0.35 },
  { at: 6 + frameOf(SMAP, MARK.door), file: "tick.wav", volume: 0.45 },
  { at: 6 + frameOf(SMAP, MARK.alert) - 2, file: "ping.wav", volume: 0.55 },
];

const Step: React.FC<{ at: number; title: string; detail: string; tone: string; last?: boolean }> = ({ at, title, detail, tone, last }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.snappy });
  const on = frame >= at;
  const ring = on ? interpolate(frame - at, [0, 24], [0, 1], { ...clamp, easing: theme.ease.out }) : 0;
  return (
    <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
      <div style={{ position: "relative", width: 30, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ width: 26, height: 26, borderRadius: 26, marginTop: 6, background: on ? tone : c.bg, border: `3px solid ${on ? tone : look.dimLine}`,
          boxSizing: "border-box", transform: `scale(${on ? 0.8 + 0.2 * p : 1})` }} />
        {on && ring < 1 ? (
          <div style={{ position: "absolute", top: 6, width: 26, height: 26, borderRadius: 26, border: `2px solid ${tone}`,
            transform: `scale(${1 + ring * 1.4})`, opacity: 1 - ring }} />
        ) : null}
        {!last ? <div style={{ width: 2, height: 60, background: look.dimLine, marginTop: 6 }} /> : null}
      </div>
      <div style={{ opacity: on ? 0.35 + 0.65 * p : 0.35, transform: `translateX(${on ? (1 - p) * 10 : 0}px)` }}>
        <div style={{ fontFamily: theme.fonts.display, fontSize: 32, fontWeight: 600, color: c.ink }}>{title}</div>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: 19, color: c.inkDim, marginTop: 4 }}>{detail}</div>
      </div>
    </div>
  );
};

/** The contact sensor's event, shown over the app while it happens (the app itself has no screen for it). */
const DoorChip: React.FC<{ at: number; until: number }> = ({ at, until }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < at || frame > until + 12) return null;
  const pin = spring({ frame: frame - at, fps, config: theme.spring.bouncy });
  const pout = interpolate(frame, [until, until + 10], [0, 1], { ...clamp, easing: theme.ease.in });
  const pulse = interpolate((frame - at) % 30, [0, 30], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 1300, top: 700, transform: `translate(-50%, -50%) scale(${pin * (1 - 0.15 * pout)})`,
      opacity: 1 - pout, display: "flex", alignItems: "center", gap: 16, padding: "16px 26px 16px 18px", borderRadius: 999,
      background: c.white, boxShadow: `0 24px 50px -18px ${a(c.ink, 0.5)}`, border: look.cardBorder, whiteSpace: "nowrap" }}>
      <div style={{ position: "relative", width: 44, height: 44, borderRadius: 44, background: c.bgAlt, display: "flex",
        alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "absolute", inset: 0, borderRadius: 44, border: `2px solid ${c.ink}`, transform: `scale(${1 + pulse * 0.6})`,
          opacity: 1 - pulse }} />
        {/* a door, ajar */}
        <div style={{ width: 16, height: 24, border: `3px solid ${c.ink}`, borderRadius: 2, boxSizing: "border-box",
          transform: "perspective(60px) rotateY(-35deg)", transformOrigin: "left center" }} />
      </div>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <div style={{ fontFamily: theme.fonts.display, fontSize: 28, fontWeight: 600, color: c.ink }}>Sensor de contacto · porta aberta</div>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: 17, color: c.inkDim }}>porta da rua · o livro ficou na secretária</div>
      </div>
    </div>
  );
};

export const Sensor: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - 6;
  const src = srcAt(SMAP, f);
  const enter = spring({ frame, fps, config: theme.spring.smooth });
  const alertF = frameOf(SMAP, MARK.alert);
  const zIn = interpolate(f, [frameOf(SMAP, MARK.sentS) - 6, frameOf(SMAP, MARK.answerS) + 10], [1, 1.45], { ...clamp, easing: theme.ease.inOut });
  const zOut = interpolate(f, [frameOf(SMAP, 50), frameOf(SMAP, 52.5)], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const zNote = interpolate(f, [alertF + 4, alertF + 34], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const z = interpolate(zOut, [0, 1], [zIn, 1]) + zNote * 1.0;
  const v = interpolate(zNote, [0, 1], [0.6, 0.06]);
  const ty = interpolate(zNote, [0, 1], [600, 330]);
  return (
    <AbsoluteFill>
      <AppPhone second={src} zoom={z} u={0.5} v={v} tx={1330} ty={ty} enter={enter} />
      <DoorChip at={6 + frameOf(SMAP, MARK.door)} until={6 + alertF + 6} />
      <LeftColumn width={660}>
        <Rise delay={4}><Overline>4 · Sensor</Overline></Rise>
        <Rise delay={8}><Heading size={58}>“Avisa-me se eu sair de casa sem o livro.”</Heading></Rise>
        <Rise delay={12}><Body size={28}>Uma frase cria o sensor. Quando a porta abre e o livro fica, chega a mensagem.</Body></Rise>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>
          <Step at={6 + frameOf(SMAP, MARK.answerS)} title="Regra criada" detail="sair de casa sem o livro" tone={c.teal} />
          <Step at={6 + frameOf(SMAP, MARK.door)} title="Porta aberta" detail="sensor de contacto da porta da rua" tone={c.ink} />
          <Step at={6 + alertF} title="Mensagem no telemóvel" detail="notificação: saíste sem o livro" tone={c.alert} last />
        </div>
        <Prototype delay={18} />
      </LeftColumn>
    </AbsoluteFill>
  );
};
