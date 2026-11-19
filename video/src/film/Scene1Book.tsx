// Real example 1, the book left behind (19 Nov, the lab), v3 after the team's notes on v2.
//   A  the phone: the team's own home screen, the Altice app's real opening (its splash), then the prototype app recorded
//      on its real state (video/tools/record_app.mjs add-book): Things › Add › Book › Take photos (the colleague's own
//      camera recording, cut at four shutter presses) › the 8 photos › name it › Save › a scenario in one sentence › Save
//   B  the lab's kit camera from the start, the colleague on the right, with the prototype's detector run over the take;
//      boxes by kind (thing, person, device, door); the door shuts with the book on the desk and the alarm glows, eased,
//      in time with the team's recording of it
//   C  outside: the home screen, the notification drawn as the team's phone draws it, a tap, the app opens on the alert
// The alarm and the notification are simulated (AGENTS.md rule 1).
import React from "react";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import { loadFont as loadRoboto } from "@remotion/google-fonts/Roboto";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Brackets, Phone, clamp } from "../presentation/ui";

const { fontFamily: SERIF } = loadFont("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });
const { fontFamily: ROBOTO } = loadRoboto("normal", { weights: ["400", "500", "700"], subsets: ["latin"] });

const X = 12;                                   // frames of each cross-zoom between the phone and the lab
const A = { open: 0, add: 52, cam: 186, name: 298, scen: 441, end: 747 };
const B0 = A.end - X, B1 = 1155;                // the lab
const C0 = B1 - X;                              // outside
export const SCENE1_FRAMES = C0 + 240;
const LAB_FROM = 7.0;                           // take second at the lab's first frame: the colleague still on the right
const CLOSE = B0 + Math.round((17.4 - LAB_FROM) * 30);   // the door shuts (17,4 s, checked frame by frame)
const BEEPS_AT = CLOSE + 6;

/* ------------------------------------------------------------------ shared */
const ease = theme.ease.inOut;
const CrossZoom: React.FC<{ len: number; inn?: boolean; out?: boolean; children: React.ReactNode }> = ({ len, inn = true, out = true, children }) => {
  const f = useCurrentFrame();
  const i = inn ? interpolate(f, [0, X], [0, 1], { ...clamp, easing: theme.ease.out }) : 1;
  const o = out ? interpolate(f, [len - X, len], [1, 0], { ...clamp, easing: theme.ease.in }) : 1;
  return <AbsoluteFill style={{ opacity: Math.min(i, o), transform: `scale(${1.04 - 0.04 * i - 0.03 * (1 - o)})` }}>{children}</AbsoluteFill>;
};
/** A serif line streamed word by word, and gone at its end. */
const Line: React.FC<{ text: string; from: number; to: number; sub?: string }> = ({ text, from, to, sub }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const out = interpolate(f, [to - 8, to], [1, 0], clamp);
  const words = text.split(" ");
  return (
    <div style={{ position: "absolute", left: 150, top: 400, width: 760, opacity: out }}>
      <div style={{ fontFamily: SERIF, fontSize: 66, lineHeight: 1.12, letterSpacing: "-0.015em", color: "#fff" }}>
        {words.map((w, k) => <span key={k} style={{ opacity: interpolate(f, [from + 6 + 3 * k, from + 11 + 3 * k], [0, 1], clamp) }}>{w} </span>)}
      </div>
      {sub ? <div style={{ fontFamily: theme.fonts.display, fontSize: 26, color: "#9AA3AE", marginTop: 18,
        opacity: interpolate(f, [from + 10 + 3 * words.length, from + 18 + 3 * words.length], [0, 1], clamp) }}>{sub}</div> : null}
    </div>
  );
};
/** The phone in the right column; its screen is drawn in the app's own pixels (1206 × 2622). */
const H = 940;
const PhoneAt: React.FC<{ push?: number; children: React.ReactNode }> = ({ push = 1, children }) => (
  <div style={{ position: "absolute", right: 250, top: (1080 - H) / 2, transform: `scale(${push})`, transformOrigin: "50% 50%" }}>
    <Phone height={H}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1206, height: 2622, transform: `scale(${(H * 0.95) / 2622})`, transformOrigin: "0 0", overflow: "hidden" }}>{children}</div>
    </Phone>
  </div>
);
const Rec: React.FC<{ src: string; from: number; rate?: number; w?: number; h?: number }> = ({ src, from, rate = 1, w = 1206, h = 2622 }) => (
  <OffthreadVideo src={staticFile(src)} muted trimBefore={Math.round(from * 30)} playbackRate={rate}
    style={{ position: "absolute", left: (1206 - w) / 2, top: (2622 - h) / 2, width: w, height: h }} />
);

/* ------------------------------------------------------------------ the team's phone (720 × 1600 screenshots) */
const K = 1206 / 720, OY = (1600 * K - 2622) / 2;          // the phone's pictures, fitted to the screen (cover)
const px = (x: number) => x * K, py = (y: number) => y * K - OY;
const PhoneImg: React.FC<{ src: string }> = ({ src }) => (
  <Img src={staticFile(src)} style={{ position: "absolute", left: 0, top: -OY, width: 1206, height: 1600 * K }} />
);
/** The status bar's clock, set to the story's time (the screenshots were taken at 15:16). */
const Clock: React.FC<{ time: string; bg: string; color: string }> = ({ time, bg, color }) => (
  <div style={{ position: "absolute", left: px(70), top: py(20), width: px(82), height: px(44), background: bg }}>
    <span style={{ position: "absolute", left: px(9), top: px(4.5), fontFamily: ROBOTO, fontWeight: 500, fontSize: px(31), lineHeight: 1, color, letterSpacing: "0.01em" }}>{time}</span>
  </div>
);
const Home: React.FC<{ time: string }> = ({ time }) => (<><PhoneImg src="phone/home.jpg" /><Clock time={time} bg="#010101" color="#E6E6E6" /></>);
const Splash: React.FC<{ time: string }> = ({ time }) => (<><PhoneImg src="phone/splash.jpg" /><Clock time={time} bg="#36D09E" color="#1E1E1E" /></>);
const Finger: React.FC<{ x: number; y: number; at: number }> = ({ x, y, at }) => {
  const f = useCurrentFrame();
  if (f < at - 12 || f > at + 8) return null;
  const o = Math.min(interpolate(f, [at - 12, at - 6], [0, 1], clamp), interpolate(f, [at + 2, at + 8], [1, 0], clamp));
  return <div style={{ position: "absolute", left: x - 70, top: y - 70, width: 140, height: 140, borderRadius: 70, background: "rgba(255,255,255,0.32)",
    border: "5px solid rgba(255,255,255,0.92)", boxShadow: "0 6px 24px rgb(0 0 0 / 0.25)", opacity: o, transform: `scale(${f >= at ? 0.82 : 1})` }} />;
};
/** The system's opening: the app's window grows out of what was tapped (an icon, a notification), showing its splash. */
const Grow: React.FC<{ at: number; from: [number, number, number, number]; r0: number; time: string; children?: React.ReactNode }> = ({ at, from, r0, time, children }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const u = interpolate(f, [at, at + 14], [0, 1], { ...clamp, easing: ease });
  const [x, y, w, h] = from;
  const L = x * (1 - u), T = y * (1 - u), W = w + (1206 - w) * u, Hh = h + (2622 - h) * u;
  const app = interpolate(f, [at + 24, at + 34], [0, 1], { ...clamp, easing: ease });
  return (
    <div style={{ position: "absolute", left: L, top: T, width: W, height: Hh, borderRadius: r0 * (1 - u), overflow: "hidden", boxShadow: "0 30px 90px rgb(0 0 0 / 0.35)" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1206, height: 2622, transform: `scale(${W / 1206}, ${Hh / 2622})`, transformOrigin: "0 0" }}>
        <Splash time={time} />
        <AbsoluteFill style={{ opacity: app }}>{children}</AbsoluteFill>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ A: the book and its scenario, on the phone */
const SHUTTERS = [1.3, 11.17, 23.03, 31.8];   // the colleague's shutter presses kept (front, back, on the desk, at an angle)
const SEG = 28, BEFORE = 0.65;                // frames per photo, seconds before each press
const ICON = [px(390), py(708), px(108), px(108)] as [number, number, number, number];
const PhoneA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {f < A.add + 40 ? <Home time="14:01" /> : null}
      <Finger x={ICON[0] + ICON[2] / 2} y={ICON[1] + ICON[3] / 2} at={24} />
      <Grow at={26} from={ICON} r0={40} time="14:01">
        <Sequence from={A.add - 26} layout="none"><Rec src="app/add-book.mp4" from={1.38} rate={1.2} /></Sequence>
      </Grow>
      {f >= A.cam && f < A.name ? SHUTTERS.map((t, i) => (
        <Sequence key={i} from={A.cam + i * SEG} durationInFrames={SEG} layout="none">
          <AbsoluteFill style={{ background: "#000" }}><Rec src="footage/phone-photos.mp4" from={t - BEFORE} w={Math.round((392 * 2622) / 850)} h={2622} /></AbsoluteFill>
        </Sequence>)) : null}
      {f >= A.name && f < A.scen ? <Sequence from={A.name} layout="none"><Rec src="app/add-book.mp4" from={7.44} rate={1.3} /></Sequence> : null}
      {f >= A.scen ? <Sequence from={A.scen} layout="none"><Rec src="app/add-book.mp4" from={13.62} rate={1.5} /></Sequence> : null}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ B: the lab */
const BOOK = [0.6348, 0.7445, 0.6874, 0.7791];          // "a yellow book": its median box over all 234 samples
const AP = [0.66, 0.705, 0.693, 0.732];                  // the access point beside it ("a small white box", 0,24)
const ALARM = [0.3135, 0.3023, 0.3243, 0.3115];          // the alarm on the shelf (from the team's screenshot, 0,82 match)
const DOOR: [number, number][] = [[0.339, 0.268], [0.435, 0.289], [0.414, 0.651], [0.321, 0.637]]; // the door leaf's corners
const DOOR_OPEN: [number, number][] = [[14.5, 17.35]];
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
/** The beeps, eased: a soft rise and a slower fall. */
const beepAt = (s: number) => Math.max(0, ...BEEPS.map(([a, b]) => Math.min(interpolate(s, [a - 0.03, a + 0.12], [0, 1], clamp), interpolate(s, [b - 0.05, b + 0.3], [1, 0], clamp))));
const KIND = { thing: "#2ABE9E", person: "#FFFFFF", device: "#8B7CF6", alarm: "#E5322D", door: "#C9D1DB", open: "#E8710A" };
type Det = { frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[] };

const Label: React.FC<{ x: number; y: number; kind: string; text?: string; color: string; dark?: boolean; below?: boolean }> = ({ x, y, kind, text, color, dark, below }) => (
  <div style={{ position: "absolute", left: x, top: y, transform: below ? undefined : "translateY(-100%)", marginTop: below ? 6 : -6, display: "flex", borderRadius: 7,
    overflow: "hidden", fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 21, whiteSpace: "nowrap", boxShadow: "0 4px 14px -6px rgb(0 0 0 / 0.5)" }}>
    <span style={{ background: "rgba(14,17,22,0.82)", color, padding: "4px 8px" }}>{kind}</span>
    {text ? <span style={{ background: color, color: dark ? "#111" : "#fff", padding: "4px 10px" }}>{text}</span> : null}
  </div>
);
const Box: React.FC<{ b: number[]; kind: string; text?: string; color: string; pad?: number; dark?: boolean; brackets?: boolean; below?: boolean }> = ({ b, kind, text, color, pad = 0.006, dark, brackets = true, below }) => {
  const x = (b[0] - pad) * 1920, y = (b[1] - pad) * 1080, w = (b[2] - b[0] + 2 * pad) * 1920, h = (b[3] - b[1] + 2 * pad) * 1080;
  return (
    <>
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, border: `2px solid ${color}`, borderRadius: 6, opacity: brackets ? 0.5 : 1 }} />
      {brackets ? <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <Brackets x={x} y={y} w={w} h={h} arm={Math.min(w, h) * 0.35} stroke={4} radius={6} color={color} /></svg> : null}
      <Label x={x} y={below ? y + h : y} kind={kind} text={text} color={color} dark={dark} below={below} />
    </>
  );
};
const Lab: React.FC = () => {
  const frame = useCurrentFrame() + B0;
  const det = useJson<Det>("takes/scene1/book-leave.boxes.json");
  const t = LAB_FROM + (frame - B0) / 30;
  const fired = frame >= CLOSE;
  const beep = frame >= BEEPS_AT ? beepAt((frame - BEEPS_AT) / 30) : 0;
  let person: number[] | null = null;
  if (det && !fired) {
    const s = det.frames.map((f) => ({ t: f.t, b: f.boxes.filter((x) => x.label === "a person" && x.score >= 0.15).sort((p, q) => q.score - p.score)[0] })).filter((x) => x.b);
    const a = [...s].reverse().find((x) => x.t <= t), c = s.find((x) => x.t >= t);
    if (a && c && c.t - a.t < 1.2) { const u = c.t > a.t ? (t - a.t) / (c.t - a.t) : 0; person = a.b.box.map((v, i) => v + (c.b.box[i] - v) * u); }
  }
  const open = DOOR_OPEN.some(([a, b]) => t >= a && t < b);
  const doorColor = open ? KIND.open : KIND.door;
  const ax = (ALARM[0] + ALARM[2]) / 2 * 1920, ay = (ALARM[1] + ALARM[3]) / 2 * 1080;
  const push = interpolate(frame, [B0, B1], [1, 1.05], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${push})`, transformOrigin: "55% 55%" }}>
        <OffthreadVideo src={staticFile("takes/scene1/book-leave.mp4")} muted trimBefore={Math.round(LAB_FROM * 30)} style={{ width: 1920, height: 1080, objectFit: "cover" }} />
        <AbsoluteFill style={{ background: "rgba(229,50,45,0.035)", opacity: fired ? beep : 0 }} />
        {fired ? <div style={{ position: "absolute", left: ax, top: ay, width: 96, height: 96, transform: "translate(-50%,-50%)", borderRadius: "50%",
          background: "radial-gradient(circle, rgba(255,90,80,0.7) 0%, rgba(255,60,50,0.25) 38%, rgba(255,40,40,0) 70%)", opacity: 0.15 + 0.5 * beep }} /> : null}
        <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
          <polygon points={DOOR.map(([x, y]) => `${x * 1920},${y * 1080}`).join(" ")} fill={open ? "rgba(232,113,10,0.10)" : "none"} stroke={doorColor} strokeWidth={3} strokeLinejoin="round" opacity={0.9} />
        </svg>
        <Label x={DOOR[3][0] * 1920 + 8} y={DOOR[3][1] * 1080 - 14} kind="door" text={open ? "aberta" : "fechada"} color={doorColor} dark={!open} />
        {person ? <Box b={person} kind="person" color={KIND.person} dark /> : null}
        <Box b={BOOK} kind="thing" text={fired ? "livro · ficou na mesa" : "livro"} color={fired ? KIND.alarm : KIND.thing} pad={0.01} below />
        <Box b={AP} kind="device" text="ponto de acesso" color={KIND.device} pad={0.006} brackets={false} />
        <Box b={ALARM} kind="device" text={fired ? "alarme · a tocar" : "alarme"} color={fired ? KIND.alarm : KIND.device} pad={0.008} brackets={false} />
      </AbsoluteFill>
      <div style={{ position: "absolute", left: 36, bottom: 32, display: "flex", gap: 12, fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 23 }}>
        <span style={{ padding: "8px 14px", borderRadius: 10, background: "rgba(14,17,22,0.78)", color: "#fff" }}>
          <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 5, background: "#ff3b30", marginRight: 10, verticalAlign: "middle" }} />Câmara · laboratório</span>
        <span style={{ padding: "8px 14px", borderRadius: 10, background: fired ? KIND.alarm : "rgba(14,17,22,0.78)", color: "#fff" }}>
          {fired ? "Saiu sem o livro · alarme e mensagem" : "Cenário ativo · Book left at home"}</span>
      </div>
      <div style={{ position: "absolute", right: 36, bottom: 32, display: "flex", gap: 18, padding: "8px 14px", borderRadius: 10, background: "rgba(14,17,22,0.78)",
        fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 21, color: "#fff" }}>
        {([["thing", KIND.thing], ["person", KIND.person], ["device", KIND.device]] as const).map(([k, c]) => (
          <span key={k}><span style={{ display: "inline-block", width: 12, height: 12, borderRadius: 3, background: c, marginRight: 8, verticalAlign: "middle" }} />{k}</span>))}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ C: outside, the alert */
const BANNER = 18, TAP = 80;                    // frames into part C
const CARD = [px(29), py(70), px(662), px(146)] as [number, number, number, number];   // the heads-up card, measured on the team's phone
/** The notification as the team's phone draws it (measured from a test notification on it): a light card, the app's
 *  round icon, the title with its age, one line of text cut with "…", the expand button. */
const Notice: React.FC = () => {
  const f = useCurrentFrame();
  if (f < BANNER) return null;
  const y = interpolate(f, [BANNER, BANNER + 11], [-CARD[3] - 60, 0], { ...clamp, easing: theme.ease.out });
  const [x0, y0, w, h] = CARD;
  return (
    <div style={{ position: "absolute", left: x0, top: y0 + y, width: w, height: h, borderRadius: px(40), background: "#F3F3F3",
      boxShadow: "0 18px 60px rgb(0 0 0 / 0.35)", fontFamily: ROBOTO, display: "flex", alignItems: "center" }}>
      <div style={{ position: "absolute", left: px(22), top: px(50) - px(23), width: px(46), height: px(46), borderRadius: "50%", overflow: "hidden", background: "#000" }}>
        <Img src={staticFile("phone/app-icon.png")} style={{ width: "100%", height: "100%" }} />
      </div>
      <div style={{ position: "absolute", left: px(86), right: px(100), top: px(30) }}>
        <div style={{ fontSize: px(23), fontWeight: 500, color: "#1F1F1F", whiteSpace: "nowrap" }}>Book left at home <span style={{ color: "#5F6368", fontWeight: 400 }}>• agora</span></div>
        <div style={{ fontSize: px(22), color: "#444746", marginTop: px(8), whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          The door closed and your book is still on the desk. The alarm is on.</div>
      </div>
      <div style={{ position: "absolute", right: px(20), top: px(50) - px(23), width: px(46), height: px(46), borderRadius: "50%", background: "#D3E3D8", display: "grid", placeItems: "center" }}>
        <svg width={px(22)} height={px(22)} viewBox="0 0 24 24"><path d="m6 9 6 6 6-6" fill="none" stroke="#1F1F1F" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" /></svg>
      </div>
    </div>
  );
};
const PhoneC: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Home time="14:11" />
    <Notice />
    <Finger x={CARD[0] + CARD[2] * 0.45} y={CARD[1] + CARD[3] / 2} at={TAP - 2} />
    <Grow at={TAP} from={CARD} r0={px(40)} time="14:11"><Img src={staticFile("phone/alert-page.png")} style={{ width: 1206, height: 2622 }} /></Grow>
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ the scene */
const appTap = (s0: number, f0: number, rate: number, t: number) => f0 + Math.round(((t - s0) / rate) * 30) + 1;
export const Scene1Book: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#0E1116" }}>
      <Sequence from={0} durationInFrames={A.end}>
        <CrossZoom len={A.end} inn={false}>
          <PhoneAt push={interpolate(f, [0, A.end], [1, 1.035], clamp)}><PhoneA /></PhoneAt>
          <Line text="Abre-se a app." from={0} to={A.add + 8} />
          <Line text="Adiciona-se o livro." from={A.add + 8} to={A.cam} />
          <Line text="Fotografa-se de vários lados." from={A.cam} to={A.name} sub="As fotografias do colega, com o telemóvel" />
          <Line text="Dá-se-lhe um nome." from={A.name} to={A.scen} />
          <Line text="E uma frase cria o cenário." from={A.scen + 40} to={A.end} sub="Alarme e mensagem, se sair sem o livro" />
        </CrossZoom>
      </Sequence>
      <Sequence from={B0} durationInFrames={B1 - B0}><CrossZoom len={B1 - B0}><Lab /></CrossZoom></Sequence>
      <Sequence from={C0}>
        <CrossZoom len={SCENE1_FRAMES - C0} out={false}>
          <PhoneAt push={interpolate(f, [C0, SCENE1_FRAMES], [1, 1.035], clamp)}><PhoneC /></PhoneAt>
          <Line text="Lá fora, o telemóvel avisa." from={4} to={TAP + 18} />
          <Line text="Toca-se, e vê-se o que a câmara viu." from={TAP + 18} to={SCENE1_FRAMES - C0 + 10} />
        </CrossZoom>
      </Sequence>
      {/* sound: a quiet bed; the app's taps; the shutters; the team's alarm recording; the phone's buzz; the tap that opens the alert */}
      <Audio src={staticFile("audio/music/bed-real.wav")} volume={(v) => 0.13 * interpolate(v, [0, 20, CLOSE - 10, CLOSE, C0 + 40, C0 + 70, SCENE1_FRAMES - 30, SCENE1_FRAMES],
        [0, 1, 1, 0.2, 0.2, 0.8, 0.8, 0], clamp)} />
      {[25, appTap(1.38, A.add, 1.2, 2.411), appTap(1.38, A.add, 1.2, 4.389), appTap(1.38, A.add, 1.2, 6.563), appTap(7.44, A.name, 1.3, 9.625), appTap(7.44, A.name, 1.3, 11.207),
        appTap(7.44, A.name, 1.3, 13.413), appTap(13.62, A.scen, 1.5, 16.09), appTap(13.62, A.scen, 1.5, 17.959), appTap(13.62, A.scen, 1.5, 24.899)].map((at, i) => (
        <Sequence key={`t${i}`} from={at} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.32} /></Sequence>))}
      {SHUTTERS.map((_, i) => (
        <Sequence key={`s${i}`} from={A.cam + i * SEG + Math.round(BEFORE * 30)} layout="none"><Audio src={staticFile(`audio/sfx/v4/shutter-${i % 2 ? 3 : 2}.wav`)} volume={0.4} /></Sequence>))}
      <Sequence from={BEEPS_AT} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} volume={(v) => 0.6 * (BEEPS_AT + v < C0 ? 1 : 0.2)} /></Sequence>
      <Sequence from={C0 + BANNER} layout="none"><Audio src={staticFile("audio/sfx/scene1/buzz.wav")} volume={0.55} /></Sequence>
      <Sequence from={C0 + TAP} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-2.wav")} volume={0.38} /></Sequence>
    </AbsoluteFill>
  );
};
