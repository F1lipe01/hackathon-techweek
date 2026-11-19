// Real example 1, the book left behind (19 Nov, the lab), v4 after the team's notes on v3, edited in the manner of the
// two product films the team picked (research/claude-videos-study.md): a light page, a phone that glides while the
// lines stream in beside it, the camera always drifting and diving into the one thing that matters, real screens only.
//   1  the phone, centred, glides right; the Altice app opens with its real loading (screen recording of the team's
//      phone); Things › Add › Book › Take photos: the colleague's 8 shutter presses, each photo flying into a card; the
//      card flies back into the app; name; Save; a scenario in one sentence; Save; Done (record_app.mjs add-book)
//   2  "Vamos testar?", and the lab camera opens out of the page
//   3  one take, in one go (book-full, 19 Nov 15:59:53): he leaves without the book, the door shuts, the alarm sounds;
//      the phone glides in: the notification, the alert; it moves aside, the lab fills the page, "Turn off the alarm",
//      the alarm stops; a cut to his return: he takes the book and leaves; a green close.
// A camera readout in the corner gives the time since the take began and the clock time (the camera's own clock).
// The alarm and the notification are simulated (AGENTS.md rule 1).
import React from "react";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, interpolateColors, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import { loadFont as loadRoboto } from "@remotion/google-fonts/Roboto";
import { loadFont as loadMono } from "@remotion/google-fonts/RobotoMono";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Brackets, Phone, SCREEN, clamp, phoneWidth } from "../presentation/ui";

const { fontFamily: SERIF } = loadFont("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });
const { fontFamily: ROBOTO } = loadRoboto("normal", { weights: ["400", "500", "700"], subsets: ["latin"] });
const { fontFamily: MONO } = loadMono("normal", { weights: ["500"], subsets: ["latin"] });
const SANS = theme.fonts.display;
const PAPER = "#F3F0EA", INK = "#1E1D1A", ACCENT = "#1C9A7E";
const ez = (f: number, a: number, b: number, e = theme.ease.inOut) => interpolate(f, [a, b], [0, 1], { ...clamp, easing: e });
const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
type Rect = { x: number; y: number; w: number; h: number };
const lerpRect = (a: Rect, b: Rect, u: number): Rect => ({ x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u), w: lerp(a.w, b.w, u), h: lerp(a.h, b.h, u) });

/* ------------------------------------------------------------------ the timeline (30 fps) */
const T = {
  glide: 30, tapIcon: 80, grow: 82, s1: 118,      // the app opens; add-book from 1.38 s at 1.25×
  cam: 246,                                        // the colleague's viewfinder, 8 shutter presses
  s3: 380,                                         // add-book from 7.44 s at 1.4×: the photos, the name
  s4: 514,                                         // add-book from 13.70 s at 1.5×: added, the scenario, saved, Done
  test: 866, lab: 935,                             // "Vamos testar?"; the lab opens out of the page
  phoneIn: 1200, notice: 1236, tap: 1300, aside: 1320, cut: 1450,
  success: 1816, end: 1940,
};
export const SCENE1_FRAMES = T.end + 66;
const at = (s0: number, f0: number, rate: number, t: number) => f0 + ((t - s0) / rate) * 30;

/* ------------------------------------------------------------------ the take (book-full: one go) */
const TAKE = "takes/scene1/book-full.mp4";
const CLOCK0 = 15 * 3600 + 59 * 60 + 53.7;              // the camera's clock at the take's first frame
const A0 = 5.5, B0 = 27.8;                               // take seconds at T.lab and at T.cut
const takeT = (f: number) => (f < T.cut ? A0 + (f - T.lab) / 30 : B0 + (f - T.cut) / 30);
const DOOR_OPEN: [number, number][] = [[10.4, 11.9], [28.2, 31.3], [38.8, 39.9]];
const CLOSE = T.lab + Math.round((11.9 - A0) * 30);     // the door shuts behind him, the book on the desk
const ALARM_ON = CLOSE + 6;
const GRAB = 34.3;                                        // he lifts the book (take seconds)
const ALERT_OPEN = 3.24;                                  // alert-book-open: the alert page is up
const ALARM_OFF_T = 6.64;                                 // alert-book-open: "Turn off the alarm" pressed
const ALARM_OFF = T.tap + 2 + Math.round((ALARM_OFF_T - ALERT_OPEN) * 30);

/* ------------------------------------------------------------------ the page, the drifting camera, the phone */
const PH = 900, PW = phoneWidth(PH), KS = (PH * SCREEN.height) / 2622;
const phoneBox = (cx: number) => ({ x: cx - PW / 2, y: 540 - PH / 2 });
const scr = (cx: number, sx: number, sy: number) => ({ x: phoneBox(cx).x + SCREEN.left * PW + sx * KS, y: phoneBox(cx).y + SCREEN.top * PH + sy * KS });
const CX = { centre: 960, right: 1370, left: 560, cRight: 1300 };
type CK = { at: number; s: number; x: number; y: number };
const H0 = { s: 1, x: 960, y: 540 };
const BTN = scr(CX.right, 603, 1366), FIELDS = scr(CX.right, 603, 1560), TXT = scr(CX.right, 603, 1000), NOTE = scr(CX.cRight, 603, 210);
const CAM: CK[] = [
  { at: 0, ...H0 }, { at: 196, ...H0 }, { at: 222, s: 2.0, ...BTN }, { at: 244, s: 2.06, ...BTN }, { at: 272, ...H0 },
  { at: 414, ...H0 }, { at: 434, s: 1.9, ...FIELDS }, { at: 486, s: 1.95, ...FIELDS }, { at: 506, ...H0 },
  { at: 586, ...H0 }, { at: 608, s: 2.4, ...TXT }, { at: 718, s: 2.46, ...TXT }, { at: 740, ...H0 },
  { at: 1238, ...H0 }, { at: 1260, s: 1.7, ...NOTE }, { at: 1292, s: 1.74, ...NOTE }, { at: 1314, ...H0 },
];
/** The camera: eased moves between keys, and under them a slow drift so it never comes to rest. */
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1].at) i++;
  const a = CAM[i], b = CAM[i + 1], u = ez(f, a.at, b.at);
  const drift = 1 + 0.012 * Math.sin((2 * Math.PI * f) / 520);
  return { s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), u)) * drift, x: lerp(a.x, b.x, u) + 6 * Math.sin((2 * Math.PI * f) / 700), y: lerp(a.y, b.y, u) };
};
const camCss = (f: number) => { const c = camAt(f); return `translate(960px,540px) scale(${c.s}) translate(${-c.x}px,${-c.y}px)`; };
const Grain: React.FC = () => (
  <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
    <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter="url(#paper)" />
  </svg>
);
/** The phone at a centre x, its screen drawn in the app's pixels (1206 × 2622), floating a little. */
const PhoneAt: React.FC<{ cx: number; shadow?: number; children: React.ReactNode }> = ({ cx, shadow = 0, children }) => {
  const f = useCurrentFrame();
  const { x, y } = phoneBox(cx);
  return (
    <div style={{ position: "absolute", left: x, top: y + 5 * Math.sin((2 * Math.PI * f) / 260), filter: shadow ? `drop-shadow(0 ${40 * shadow}px ${70 * shadow}px rgba(0,0,0,${0.45 * shadow}))` : undefined }}>
      <Phone height={PH}><div style={{ position: "absolute", left: 0, top: 0, width: 1206, height: 2622, transform: `scale(${KS})`, transformOrigin: "0 0", overflow: "hidden" }}>{children}</div></Phone>
    </div>
  );
};
const Rec: React.FC<{ src: string; from: number; rate?: number; w?: number }> = ({ src, from, rate = 1, w = 1206 }) => (
  <OffthreadVideo src={staticFile(src)} muted trimBefore={Math.round(from * 30)} playbackRate={rate} style={{ position: "absolute", left: (1206 - w) / 2, top: 0, width: w, height: 2622 }} />
);
/** A serif line streamed word by word: each new word arrives in the accent and settles into ink. */
const Line: React.FC<{ text: string; from: number; to: number; top?: number; left?: number; size?: number; align?: "left" | "center"; width?: number; color?: string }> = ({ text, from, to, top = 420, left = 150, size = 62, align = "left", width = 760, color = INK }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const fade = interpolate(f, [to - 10, to], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left, top, width, opacity: fade, textAlign: align, fontFamily: SERIF, fontSize: size, lineHeight: 1.13, letterSpacing: "-0.015em" }}>
      {text.split(" ").map((w, k) => {
        const a = from + 4 + 3 * k;
        return <span key={k} style={{ opacity: interpolate(f, [a, a + 5], [0, 1], clamp), color: interpolateColors(f, [a, a + 16], [color === INK ? ACCENT : color, color]) }}>{w} </span>;
      })}
    </div>
  );
};

/* ------------------------------------------------------------------ the team's phone (720 × 1600 screenshots and its recording) */
const PK = 1206 / 720, POY = (1600 * PK - 2622) / 2;
const px = (x: number) => x * PK, py = (y: number) => y * PK - POY;
const PhoneImg: React.FC<{ src: string }> = ({ src }) => <Img src={staticFile(src)} style={{ position: "absolute", left: 0, top: -POY, width: 1206, height: 1600 * PK }} />;
const Clock: React.FC<{ time: string; bg: string; color: string }> = ({ time, bg, color }) => (
  <div style={{ position: "absolute", left: px(70), top: py(20), width: px(82), height: px(44), background: bg }}>
    <span style={{ position: "absolute", left: px(7), top: px(4.5), fontFamily: ROBOTO, fontWeight: 500, fontSize: px(31), lineHeight: 1, color, letterSpacing: "0.01em" }}>{time}</span>
  </div>
);
const Home: React.FC<{ time: string }> = ({ time }) => (<><PhoneImg src="phone/home.jpg" /><Clock time={time} bg="#010101" color="#E6E6E6" /></>);
/** A light touch: a small soft ring that presses in. */
const Touch: React.FC<{ x: number; y: number; at: number }> = ({ x, y, at: a }) => {
  const f = useCurrentFrame();
  if (f < a - 8 || f > a + 8) return null;
  const o = Math.min(ez(f, a - 8, a - 3), 1 - ez(f, a + 2, a + 8));
  return <div style={{ position: "absolute", left: x - 45, top: y - 45, width: 90, height: 90, borderRadius: 45, background: "rgba(255,255,255,0.22)",
    border: "3px solid rgba(255,255,255,0.8)", opacity: o, transform: `scale(${f >= a ? 0.86 : 1})` }} />;
};
/** The system's opening: the app's window grows out of what was tapped; inside, the Altice app's real loading, then the app. */
const Grow: React.FC<{ at: number; from: [number, number, number, number]; r0: number; splash?: boolean; appAt?: number; children?: React.ReactNode }> = ({ at: a, from, r0, splash = true, appAt = 34, children }) => {
  const f = useCurrentFrame();
  if (f < a) return null;
  const u = ez(f, a, a + 14);
  const [x, y, w, h] = from;
  const W = lerp(w, 1206, u), H = lerp(h, 2622, u);
  const app = splash ? ez(f, a + appAt, a + appAt + 10) : ez(f, a + 4, a + 12);
  return (
    <div style={{ position: "absolute", left: x * (1 - u), top: y * (1 - u), width: W, height: H, borderRadius: r0 * (1 - u), overflow: "hidden", boxShadow: "0 30px 90px rgb(0 0 0 / 0.35)" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1206, height: 2622, transform: `scale(${W / 1206}, ${H / 2622})`, transformOrigin: "0 0", background: "#27BE9F" }}>
        {splash ? <Sequence from={a} layout="none"><OffthreadVideo src={staticFile("phone/open-splash.mp4")} muted trimBefore={5}
          style={{ position: "absolute", left: 0, top: -POY, width: 1206, height: 1600 * PK }} /></Sequence> : null}
        {splash ? <Clock time="15:52" bg="#27BE9F" color="#1E1E1E" /> : null}
        <AbsoluteFill style={{ opacity: app }}>{children}</AbsoluteFill>
      </div>
    </div>
  );
};
const ICON: [number, number, number, number] = [px(390), py(708), px(108), px(108)];
const CARD: [number, number, number, number] = [px(29), py(70), px(662), px(146)];
/** The notification as the team's phone draws it (measured from a test notification on it). */
const Notice: React.FC<{ at: number }> = ({ at: a }) => {
  const f = useCurrentFrame();
  if (f < a) return null;
  const dy = interpolate(f, [a, a + 11], [-CARD[3] - 60, 0], { ...clamp, easing: theme.ease.out });
  const [x0, y0, w, h] = CARD;
  return (
    <div style={{ position: "absolute", left: x0, top: y0 + dy, width: w, height: h, borderRadius: px(40), background: "#F3F3F3", boxShadow: "0 18px 60px rgb(0 0 0 / 0.35)", fontFamily: ROBOTO }}>
      <div style={{ position: "absolute", left: px(22), top: px(27), width: px(46), height: px(46), borderRadius: "50%", overflow: "hidden", background: "#000" }}>
        <Img src={staticFile("phone/app-icon.png")} style={{ width: "100%", height: "100%" }} /></div>
      <div style={{ position: "absolute", left: px(86), right: px(100), top: px(30) }}>
        <div style={{ fontSize: px(23), fontWeight: 500, color: "#1F1F1F", whiteSpace: "nowrap" }}>Book left at home <span style={{ color: "#5F6368", fontWeight: 400 }}>• agora</span></div>
        <div style={{ fontSize: px(22), color: "#444746", marginTop: px(8), whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>The door closed and your book is still on the desk. The alarm is on.</div>
      </div>
      <div style={{ position: "absolute", right: px(20), top: px(27), width: px(46), height: px(46), borderRadius: "50%", background: "#D3E3D8", display: "grid", placeItems: "center" }}>
        <svg width={px(22)} height={px(22)} viewBox="0 0 24 24"><path d="m6 9 6 6 6-6" fill="none" stroke="#1F1F1F" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" /></svg></div>
    </div>
  );
};

/* ------------------------------------------------------------------ 1: the app, the photos */
const SHOT = [1.3, 7.83, 11.17, 16.2, 23.03, 27.27, 31.8, 36.1];   // the colleague's 8 shutter presses
const SEG = 16, BEFORE = 0.35, PRESS = Math.round(BEFORE * 30);
const S4_END = T.s4 + Math.floor(((31.5 - 13.7) / 1.5) * 30) - 2;   // add-book ends at 31.5 s
const ScreenA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {f < T.s1 + 12 ? <Home time="15:52" /> : null}
      <Touch x={ICON[0] + ICON[2] / 2} y={ICON[1] + ICON[3] / 2} at={T.tapIcon} />
      {f < T.cam + 2 ? <Grow at={T.grow} from={ICON} r0={40}><Sequence from={T.s1} layout="none"><Rec src="app/add-book.mp4" from={1.38} rate={1.25} /></Sequence></Grow> : null}
      {f >= T.cam && f < T.s3 ? SHOT.map((t, i) => (
        <Sequence key={i} from={T.cam + i * SEG} durationInFrames={i === SHOT.length - 1 ? T.s3 - T.cam - i * SEG : SEG} layout="none">
          <AbsoluteFill style={{ background: "#000" }}><Rec src="footage/phone-photos.mp4" from={t - BEFORE} w={1209} /></AbsoluteFill>
        </Sequence>)) : null}
      {f >= T.s3 && f < T.s4 ? <Sequence from={T.s3} layout="none"><Rec src="app/add-book.mp4" from={7.44} rate={1.4} /></Sequence> : null}
      {f >= T.s4 && f < S4_END ? <Sequence from={T.s4} layout="none"><Rec src="app/add-book.mp4" from={13.7} rate={1.5} /></Sequence> : null}
      {f >= S4_END ? <Img src={staticFile("phone/add-book-last.png")} style={{ position: "absolute", inset: 0, width: 1206, height: 2622 }} /> : null}
    </AbsoluteFill>
  );
};
const GRID: Rect = { x: 150, y: 420, w: 844, h: 472 };
const slot = (j: number): Rect => ({ x: GRID.x + 24 + (j % 4) * 202, y: GRID.y + 56 + Math.floor(j / 4) * 202, w: 190, h: 190 });
const r4 = (r: { x: number; y: number }, w: number, h: number): Rect => ({ x: r.x, y: r.y, w: w * KS, h: h * KS });
const VIEWFINDER = r4(scr(CX.right, 308, 386), 898, 1264);
const GRID_ON_SCREEN = r4(scr(CX.right, 72, 600), 1062, 510);
const PhotoCard: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.cam + 4 || f > T.s3 + 24) return null;
  const inU = ez(f, T.cam + 4, T.cam + 20, theme.ease.out);
  const back = ez(f, T.s3 + 2, T.s3 + 22);
  const r = lerpRect(GRID, GRID_ON_SCREEN, back);
  const sc = r.w / GRID.w;
  const shots = SHOT.map((_, i) => ({ src: `phone/photos/final-${i + 1}.jpg`, at: T.cam + i * SEG + PRESS + 1, j: i }));
  const landed = shots.filter((s) => f >= s.at + 14).length;
  return (
    <>
      <div style={{ position: "absolute", left: r.x, top: r.y, width: GRID.w, height: GRID.h, transform: `scale(${sc}) translateY(${(1 - inU) * 30}px)`, transformOrigin: "0 0",
        opacity: inU * (1 - ez(f, T.s3 + 14, T.s3 + 22)), borderRadius: 26, background: "#FFFFFF", boxShadow: "0 30px 70px -30px rgba(70,50,25,0.35), 0 0 0 1px rgba(30,25,15,0.05)" }}>
        <div style={{ position: "absolute", left: 24, top: 16, right: 24, display: "flex", justifyContent: "space-between", fontFamily: SANS, fontSize: 22 }}>
          <span style={{ color: INK, fontWeight: 600 }}>Book</span><span style={{ color: "#7A756C" }}>{landed} de 8 fotografias</span></div>
        {Array.from({ length: 8 }, (_, j) => <div key={j} style={{ position: "absolute", left: slot(j).x - GRID.x, top: slot(j).y - GRID.y, width: 190, height: 190, borderRadius: 14, background: "#EEEAE2" }} />)}
        {shots.map((p) => f >= p.at + 14 ? <Img key={p.j} src={staticFile(p.src)} style={{ position: "absolute", left: slot(p.j).x - GRID.x, top: slot(p.j).y - GRID.y, width: 190, height: 190, objectFit: "cover", borderRadius: 14 }} /> : null)}
      </div>
      {f < T.s3 ? shots.map((p) => {
        if (f < p.at || f >= p.at + 14) return null;
        const u = ez(f, p.at, p.at + 14, theme.ease.out);
        const q = lerpRect(VIEWFINDER, slot(p.j), u);
        return <Img key={`fly${p.j}`} src={staticFile(p.src)} style={{ position: "absolute", left: q.x, top: q.y, width: q.w, height: q.h, objectFit: "cover", borderRadius: lerp(24, 14, u), boxShadow: "0 24px 50px -18px rgba(40,30,15,0.5)" }} />;
      }) : null}
    </>
  );
};

/* ------------------------------------------------------------------ 3: the lab (one take) */
const BOOK = [0.628, 0.7238, 0.6727, 0.7438];            // the book on the desk: the take before and after he takes it, differenced
const AP = [0.66, 0.705, 0.693, 0.732];
const ALARM = [0.3135, 0.3023, 0.3243, 0.3115];
const DOOR: [number, number][] = [[0.339, 0.268], [0.435, 0.289], [0.414, 0.651], [0.321, 0.637]];
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
const BEEP_LEN = 6.67;
const beepAt = (s: number) => { const m = s % BEEP_LEN; return Math.max(0, ...BEEPS.map(([a, b]) => Math.min(interpolate(m, [a - 0.03, a + 0.12], [0, 1], clamp), interpolate(m, [b - 0.05, b + 0.3], [1, 0], clamp)))); };
const KIND = { thing: "#2ABE9E", person: "#FFFFFF", device: "#8B7CF6", alarm: "#E5322D", door: "#C9D1DB", open: "#E8710A", ok: "#1FA37F" };
type Det = { frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[] };
const Label: React.FC<{ x: number; y: number; kind: string; text?: string; color: string; dark?: boolean; below?: boolean }> = ({ x, y, kind, text, color, dark, below }) => (
  <div style={{ position: "absolute", left: x, top: y, transform: below ? undefined : "translateY(-100%)", marginTop: below ? 6 : -6, display: "flex", borderRadius: 7,
    overflow: "hidden", fontFamily: SANS, fontWeight: 600, fontSize: 21, whiteSpace: "nowrap", boxShadow: "0 4px 14px -6px rgb(0 0 0 / 0.5)" }}>
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
const hms = (s: number) => { const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = Math.floor(s % 60); return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}`; };
const ms = (s: number) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
/** The lab at frame f (absolute): the take, the detector's boxes, the alarm, the camera readout. */
const LabLayer: React.FC = () => {
  const f = useCurrentFrame();
  const det = useJson<Det>("takes/scene1/book-full.boxes.json");
  const t = takeT(f);
  const ringing = f >= ALARM_ON && f < ALARM_OFF;
  const beep = ringing ? beepAt((f - ALARM_ON) / 30) : 0;
  const left = t >= 11.9 && t < GRAB;                     // the book stays while he is out
  const taken = t >= GRAB;
  let person: number[] | null = null;
  if (det) {
    const s = det.frames.map((x) => ({ t: x.t, b: x.boxes.filter((y) => y.label === "a person" && y.score >= 0.15).sort((p, q) => q.score - p.score)[0] })).filter((x) => x.b);
    const a = [...s].reverse().find((x) => x.t <= t), c = s.find((x) => x.t >= t);
    if (a && c && c.t - a.t < 1.2) { const u = c.t > a.t ? (t - a.t) / (c.t - a.t) : 0; person = a.b.box.map((v, i) => v + (c.b.box[i] - v) * u); }
  }
  const open = DOOR_OPEN.some(([a, b]) => t >= a && t < b);
  const doorColor = open ? KIND.open : KIND.door;
  const ax = (ALARM[0] + ALARM[2]) / 2 * 1920, ay = (ALARM[1] + ALARM[3]) / 2 * 1080;
  const xfade = ez(f, T.cut - 3, T.cut + 5);              // the cut to his return, softened over 8 frames
  const chip = f >= ALARM_OFF && !taken ? ["Alarme desligado na app", "rgba(255,255,255,0.94)", INK] : taken ? ["Saiu com o livro", KIND.ok, "#fff"]
    : left && f >= CLOSE ? ["A porta fechou e o livro ficou · alarme e mensagem", KIND.alarm, "#fff"] : ["Cenário ativo · Book left at home", "rgba(255,255,255,0.94)", INK];
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, background: "#000" }}>
      {f < T.cut + 6 ? <Sequence from={T.lab} layout="none"><OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round(A0 * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} /></Sequence> : null}
      {f >= T.cut - 3 ? <AbsoluteFill style={{ opacity: xfade }}><Sequence from={T.cut - 3} layout="none"><OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round((B0 - 0.1) * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} /></Sequence></AbsoluteFill> : null}
      <AbsoluteFill style={{ background: "rgba(229,50,45,0.035)", opacity: beep }} />
      {ringing ? <div style={{ position: "absolute", left: ax, top: ay, width: 96, height: 96, transform: "translate(-50%,-50%)", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(255,90,80,0.7) 0%, rgba(255,60,50,0.25) 38%, rgba(255,40,40,0) 70%)", opacity: 0.15 + 0.5 * beep }} /> : null}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <polygon points={DOOR.map(([x, y]) => `${x * 1920},${y * 1080}`).join(" ")} fill={open ? "rgba(232,113,10,0.10)" : "none"} stroke={doorColor} strokeWidth={3} strokeLinejoin="round" opacity={0.9} />
      </svg>
      <Label x={DOOR[3][0] * 1920 + 8} y={DOOR[3][1] * 1080 - 14} kind="door" text={open ? "aberta" : "fechada"} color={doorColor} dark={!open} />
      {person ? <Box b={person} kind="person" text={taken ? "com o livro" : undefined} color={taken ? KIND.ok : KIND.person} dark={!taken} /> : null}
      {!taken ? <Box b={BOOK} kind="thing" text={left && f >= CLOSE ? "livro · ficou na mesa" : "livro"} color={left && f >= CLOSE && f < ALARM_OFF ? KIND.alarm : KIND.thing} pad={0.01} below /> : null}
      <Box b={AP} kind="device" text="ponto de acesso" color={KIND.device} brackets={false} />
      <Box b={ALARM} kind="device" text={ringing ? "alarme · a tocar" : "alarme"} color={ringing ? KIND.alarm : KIND.device} pad={0.008} brackets={false} />
      <div style={{ position: "absolute", left: 36, bottom: 32, padding: "10px 18px", borderRadius: 999, fontFamily: SANS, fontSize: 24, background: chip[1], color: chip[2], boxShadow: "0 10px 30px -10px rgb(0 0 0 / 0.4)" }}>{chip[0]}</div>
      {/* the camera readout: time since the take began, and the clock time */}
      <div style={{ position: "absolute", right: 36, top: 30, display: "flex", alignItems: "center", gap: 14, padding: "9px 16px", borderRadius: 10, background: "rgba(10,12,16,0.72)",
        fontFamily: MONO, fontWeight: 500, fontSize: 24, color: "#fff", letterSpacing: "0.02em" }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: "#ff3b30", opacity: Math.floor(f / 15) % 2 ? 1 : 0.35 }} />REC {ms(t)}
        <span style={{ opacity: 0.45 }}>|</span>{hms(CLOCK0 + t)}
      </div>
    </AbsoluteFill>
  );
};
/** The lab's frame on the page: it opens out of the "Vamos testar?" page, then fills it. */
const LabFrame: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.lab || f > T.success + 30) return null;
  const u = ez(f, T.lab, T.lab + 34);
  const small: Rect = { x: 960 - 320, y: 610, w: 640, h: 360 }, full: Rect = { x: 0, y: 0, w: 1920, h: 1080 };
  const r = lerpRect(small, full, u);
  const blur = ez(f, T.phoneIn, T.phoneIn + 20) * (1 - ez(f, T.aside, T.aside + 26));
  return (
    <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: 26 * (1 - u), overflow: "hidden", opacity: ez(f, T.lab, T.lab + 8),
      boxShadow: u < 1 ? "0 40px 90px -30px rgba(70,50,25,0.5)" : undefined }}>
      <div style={{ width: 1920, height: 1080, transform: `scale(${r.w / 1920})`, transformOrigin: "0 0", filter: blur > 0.01 ? `blur(${6 * blur}px) brightness(${1 - 0.25 * blur})` : undefined }}>
        <LabLayer />
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ 3: the phone over the lab */
const ALERT_END = T.tap + 2 + Math.floor((7.0 - ALERT_OPEN) * 30) - 2;
const AlertRec: React.FC = () => {
  const f = useCurrentFrame();
  return f < ALERT_END ? <Sequence from={T.tap + 2} layout="none"><Rec src="app/alert-book-open.mp4" from={ALERT_OPEN} /></Sequence>
    : <Img src={staticFile("phone/alert-last.png")} style={{ position: "absolute", inset: 0, width: 1206, height: 2622 }} />;
};
const ScreenC: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Home time="16:00" />
    <Notice at={T.notice} />
    <Touch x={CARD[0] + CARD[2] * 0.45} y={CARD[1] + CARD[3] / 2} at={T.tap - 2} />
    <Grow at={T.tap} from={CARD} r0={px(40)} splash={false}><AlertRec /></Grow>
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ the scene */
export const Scene1Book: React.FC = () => {
  const f = useCurrentFrame();
  // the phone: centred, glides right; leaves for the test; comes in over the lab; moves aside; goes
  const cxA = lerp(CX.centre, CX.right, ez(f, T.glide, T.glide + 36)) + 900 * ez(f, T.test, T.test + 26, theme.ease.in);
  const cxC = lerp(CX.cRight + 900, CX.cRight, ez(f, T.phoneIn, T.phoneIn + 26, theme.ease.out));
  const cxC2 = lerp(cxC, CX.left, ez(f, T.aside, T.aside + 30)) - 1300 * ez(f, T.cut - 10, T.cut + 18, theme.ease.in);
  const succ = ez(f, T.success, T.success + 26);
  const endIn = ez(f, T.end - 10, T.end + 6);
  const tap = (s0: number, f0: number, rate: number, t: number) => Math.round(at(s0, f0, rate, t) + 1.5);
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill style={{ transform: f < T.lab ? camCss(f) : camCss(f), transformOrigin: "0 0" }}>
        {f < T.test + 30 ? <PhoneAt cx={cxA}><ScreenA /></PhoneAt> : null}
        <Line text="Abre-se a app." from={44} to={150} />
        <Line text="Adiciona-se o livro." from={150} to={T.cam} />
        <Line text="Fotografa-se de vários lados." from={T.cam} to={T.s3 + 4} top={300} />
        <PhotoCard />
        <Line text="Dá-se-lhe um nome." from={T.s3 + 4} to={T.s4} />
        <Line text="E uma frase cria o cenário." from={T.s4 + 40} to={T.test + 6} />
        <Line text="Vamos testar?" from={T.test + 12} to={T.lab + 22} top={360} left={0} width={1920} align="center" size={104} />
      </AbsoluteFill>
      <LabFrame />
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f >= T.phoneIn && f < T.cut + 20 ? <PhoneAt cx={cxC2} shadow={1}><ScreenC /></PhoneAt> : null}
      </AbsoluteFill>
      {/* the close: a green wash, a check, the line */}
      {f >= T.success ? (
        <AbsoluteFill style={{ clipPath: `circle(${succ * 130}% at 38% 45%)`, background: "linear-gradient(135deg, #1C9A7E 0%, #2ABE9E 60%, #4FD1B0 100%)", opacity: 1 - endIn }}>
          <svg width={150} height={150} viewBox="0 0 150 150" style={{ position: "absolute", left: 885, top: 270 }}>
            <circle cx={75} cy={75} r={66} fill="none" stroke="rgba(255,255,255,0.95)" strokeWidth={6} strokeDasharray={415} strokeDashoffset={415 * (1 - ez(f, T.success + 18, T.success + 40))} transform="rotate(-90 75 75)" />
            <path d="M46 78 L66 98 L106 55" fill="none" stroke="#fff" strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={90} strokeDashoffset={90 * (1 - ez(f, T.success + 34, T.success + 50))} />
          </svg>
          <Line text="Desta vez, o livro saiu com ele." from={T.success + 30} to={T.end + 4} top={470} left={0} width={1920} align="center" size={80} color="#FFFFFF" />
        </AbsoluteFill>) : null}
      {f >= T.end - 10 ? (
        <AbsoluteFill style={{ opacity: endIn, alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
          <Img src={staticFile("phone/app-icon.png")} style={{ width: 104, height: 104, borderRadius: 24, marginBottom: 30, boxShadow: "0 18px 40px -16px rgba(70,50,25,0.45)" }} />
          <div style={{ fontFamily: SERIF, fontSize: 84, color: INK, letterSpacing: "-0.015em" }}>
            {"ThingTracker".split("").map((ch, i) => <span key={i} style={{ opacity: ez(f, T.end + 4 + 2 * i, T.end + 10 + 2 * i) }}>{ch}</span>)}</div>
        </AbsoluteFill>) : null}
      <Grain />
      {/* sound: a bed for the app and the close (none under the lab footage); a soft swish under each glide; light taps on
          the frame each button reacts; the shutters; the team's alarm recording until it is turned off; the buzz */}
      <Audio src={staticFile("audio/music/bed-real.wav")} volume={(v) => 0.12 * interpolate(v, [0, 20, T.lab - 30, T.lab, T.success - 6, T.success + 20, SCENE1_FRAMES - 30, SCENE1_FRAMES],
        [0, 1, 1, 0, 0, 1.2, 1.2, 0], clamp)} />
      {[T.glide, T.test, T.phoneIn, T.aside].map((a, i) => <Sequence key={`w${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/slide-card.wav")} volume={0.2} /></Sequence>)}
      {[T.tapIcon, tap(1.38, T.s1, 1.25, 2.411), tap(1.38, T.s1, 1.25, 4.389), tap(1.38, T.s1, 1.25, 6.563), tap(7.44, T.s3, 1.4, 9.625), tap(7.44, T.s3, 1.4, 11.207),
        tap(7.44, T.s3, 1.4, 13.413), tap(13.7, T.s4, 1.5, 16.09), tap(13.7, T.s4, 1.5, 17.959), tap(13.7, T.s4, 1.5, 24.868), tap(13.7, T.s4, 1.5, 31.131), T.tap, ALARM_OFF].map((a, i) => (
        <Sequence key={`t${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.15} /></Sequence>))}
      {SHOT.map((_, i) => <Sequence key={`s${i}`} from={T.cam + i * SEG + PRESS} layout="none"><Audio src={staticFile(`audio/sfx/v4/shutter-${i % 2 ? 3 : 2}.wav`)} volume={0.28} /></Sequence>)}
      <Sequence from={ALARM_ON} durationInFrames={ALARM_OFF - ALARM_ON + 4} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} loop
        volume={(v) => { const g = ALARM_ON + v; return (g < T.phoneIn ? 0.5 : g < T.aside ? 0.22 : 0.4) * (1 - ez(g, ALARM_OFF, ALARM_OFF + 4)); }} /></Sequence>
      <Sequence from={T.notice} layout="none"><Audio src={staticFile("audio/sfx/scene1/buzz.wav")} volume={0.5} /></Sequence>
      <Sequence from={T.success - 105} layout="none"><Audio src={staticFile("audio/sfx/v4/riser-air.wav")} volume={0.14} /></Sequence>
    </AbsoluteFill>
  );
};
