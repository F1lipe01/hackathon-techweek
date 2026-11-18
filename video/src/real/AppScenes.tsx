// 3 · Na app: our app (a copy of the Altice app, simulated data), recorded on screen. Three passages at real speed,
// cut together: the question and its answer, the sentence that creates the sensor, the door and the message.
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { IPHONE, IPhone, VideoAt } from "./devices";
import { Chip, Heading, Overline } from "./layers";
import { clamp, Cue, look } from "./look";

const { c, a } = look;

// footage/app-book.mp4 from 33 s, re-encoded with regular keyframes (the original's sparse full-range keyframes made
// Remotion show frames seconds off). Times below stay in the original recording's seconds.
const APP = "real/app-book-33s.mp4";
const APP_T0 = 33;
// app-book.marks.json, plus moments measured on the frames: the replies appear at 39.2 and 48.2, the sensor fires
// at 53.94 (mark "alert") and the notification banner slides in at 54.55.
const MARK = { sentQ: 37.73, answerQ: 39.2, sentS: 46.752, answerS: 48.2, door: 53.943, banner: 54.55 };

const SEGS = [
  { from: 36.55, to: 41.0 },
  { from: 45.7, to: 49.8 },
  { from: 53.4, to: 57.4 },
].map((s) => ({ ...s, len: Math.round((s.to - s.from) * theme.fps) }));
const LEAD = 6;
const SEG_START = SEGS.reduce<number[]>((acc, s, i) => [...acc, i === 0 ? LEAD : acc[i - 1] + SEGS[i - 1].len], []);
const at = (seg: number, t: number) => SEG_START[seg] + Math.round((t - SEGS[seg].from) * theme.fps);
export const APP_FRAMES = SEG_START[2] + SEGS[2].len;
export const APP_CUES: Cue[] = [
  { at: SEG_START[0], file: "typing", dur: at(0, MARK.sentQ) - SEG_START[0] - 2 },
  { at: at(0, MARK.sentQ), file: "tick" },
  { at: SEG_START[1], file: "typing", dur: at(1, MARK.sentS) - SEG_START[1] - 2 },
  { at: at(1, MARK.sentS), file: "tick" },
  { at: at(2, MARK.door), file: "door" },
  { at: at(2, MARK.banner) - 1, file: "notify" },
];

const PHONE_H = 960;
const PK = PHONE_H / IPHONE.h;
const PHONE_W = IPHONE.w * PK;
const PHONE_X = 1330 - PHONE_W / 2;
const PHONE_Y = (1080 - PHONE_H) / 2;

/** The phone, zoomed on a point of its screen (u, v in 0..1) placed at (tx, ty). */
const AppPhone: React.FC<{ second: number; zoom: number; u: number; v: number; tx: number; ty: number }> = ({ second, zoom, u, v, tx, ty }) => {
  const fx = (IPHONE.sx + u * IPHONE.sw) * PK;
  const fy = (IPHONE.sy + v * IPHONE.sh) * PK;
  const k = Math.min(1, (zoom - 1) / 0.6);
  return (
    <div style={{ position: "absolute", left: PHONE_X, top: PHONE_Y, transformOrigin: `${fx}px ${fy}px`,
      transform: `translate(${(tx - (PHONE_X + fx)) * k}px, ${(ty - (PHONE_Y + fy)) * k}px) scale(${zoom})` }}>
      <IPhone height={PHONE_H}>
        <VideoAt src={APP} second={second - APP_T0} />
      </IPhone>
    </div>
  );
};

const Caption: React.FC<{ from: number; to: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ from, to, children, style }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [from, from + 8, to - 1, to], [0, 1, 1, 0], { ...clamp, easing: theme.ease.out });
  if (o <= 0) return null;
  return <div style={{ opacity: o, transform: `translateY(${(1 - Math.min(1, (frame - from) / 8)) * 12}px)`, ...style }}>{children}</div>;
};

const Answer: React.FC<{ label: string; text: string; tone?: string }> = ({ label, text, tone = c.ink }) => (
  <div style={{ padding: "18px 22px", borderRadius: 16, background: c.white, border: look.cardBorder, boxShadow: `0 16px 36px -24px ${a(c.ink, 0.45)}`,
    maxWidth: 640 }}>
    <div style={{ fontFamily: theme.fonts.mono, fontSize: 17, color: c.inkDim, marginBottom: 6 }}>{label}</div>
    <div style={{ fontFamily: theme.fonts.display, fontSize: 31, fontWeight: 500, color: tone, lineHeight: 1.25 }}>{text}</div>
  </div>
);

/** The contact sensor's event over the app, which has no screen of its own for it. */
const DoorChip: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [from, from + 6, to, to + 8], [0, 1, 1, 0], { ...clamp, easing: theme.ease.out });
  if (o <= 0) return null;
  return (
    <div style={{ position: "absolute", left: 1330, top: 720, transform: `translate(-50%, -50%) translateY(${(1 - o) * 10}px)`, opacity: o,
      display: "flex", alignItems: "center", gap: 14, padding: "14px 24px 14px 16px", borderRadius: 999, background: c.white,
      boxShadow: `0 20px 44px -18px ${a(c.ink, 0.5)}`, border: look.cardBorder, whiteSpace: "nowrap" }}>
      <div style={{ width: 40, height: 40, borderRadius: 40, background: c.bgAlt, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 15, height: 22, border: `3px solid ${c.ink}`, borderRadius: 2, boxSizing: "border-box",
          transform: "perspective(60px) rotateY(-35deg)", transformOrigin: "left center" }} />
      </div>
      <div style={{ fontFamily: theme.fonts.display, fontSize: 27, fontWeight: 600, color: c.ink }}>Sensor de contacto · porta aberta</div>
    </div>
  );
};

export const App: React.FC = () => {
  const frame = useCurrentFrame();
  const seg = Math.max(0, SEG_START.filter((s) => frame >= s).length - 1);
  const local = Math.max(0, frame - SEG_START[seg]);
  const src = Math.min(SEGS[seg].to, SEGS[seg].from + local / theme.fps);
  const cutIn = seg > 0 ? interpolate(local, [0, 5], [1, 0], { ...clamp, easing: theme.ease.out }) : 0;

  // framing per passage: the answer, the reply, then the notification
  const io = { ...clamp, easing: theme.ease.inOut };
  let zoom = 1;
  let v = 0.5;
  let ty = 560;
  if (seg === 0) {
    zoom = interpolate(frame, [at(0, MARK.answerQ) - 4, at(0, MARK.answerQ) + 26], [1, 1.45], io);
    v = 0.55;
  } else if (seg === 1) {
    zoom = 1.3;
    v = 0.66;
    ty = 600;
  } else {
    const p = interpolate(frame, [at(2, MARK.banner) + 6, at(2, MARK.banner) + 40], [0, 1], io);
    zoom = 1 + 0.75 * p;
    v = interpolate(p, [0, 1], [0.5, 0.06]);
    ty = interpolate(p, [0, 1], [560, 330]);
  }

  const S0 = SEG_START[0], S1 = SEG_START[1], S2 = SEG_START[2], END = APP_FRAMES + 20;
  return (
    <AbsoluteFill>
      <AppPhone second={src} zoom={zoom} u={0.5} v={v} tx={1330} ty={ty} />
      <AbsoluteFill style={{ background: c.bg, opacity: cutIn * 0.9 }} />
      <DoorChip from={at(2, MARK.door)} to={at(2, MARK.banner) + 4} />

      <div style={{ position: "absolute", left: 140, top: 300, width: 720, display: "flex", flexDirection: "column", gap: 22 }}>
        <Caption from={0} to={END}><Overline>3 · Na app</Overline></Caption>
        <Caption from={S0} to={S1}><Heading size={60}>“Onde está o meu livro?”</Heading></Caption>
        <Caption from={at(0, MARK.answerQ) + 2} to={S1}><Answer label="resposta" text="Na secretária, na Work Room, às 16:30." /></Caption>
        <Caption from={S1} to={S2}><Heading size={56}>“Avisa-me se eu sair de casa sem o livro.”</Heading></Caption>
        <Caption from={at(1, MARK.answerS) + 2} to={S2}><Answer label="resposta" text="Sensor criado: sair de casa sem o livro." /></Caption>
        <Caption from={S2} to={END}><Heading size={56}>A porta abre; o livro fica na secretária.</Heading></Caption>
        <Caption from={at(2, MARK.banner) + 2} to={END}><Answer label="mensagem no telemóvel" text="Saíste sem o livro." tone={c.alert} /></Caption>
      </div>
      <div style={{ position: "absolute", left: 140, top: 880 }}>
        <Caption from={0} to={END}>
          <Chip mono bg={a(c.white, 0.8)} color={c.inkDim} style={{ fontSize: 17 }}>Interface: protótipo · dados simulados</Chip>
        </Caption>
      </div>
    </AbsoluteFill>
  );
};
