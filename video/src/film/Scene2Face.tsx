// Real example 2, the unknown person (19 Nov, the lab), v3 (the team's notes on v2), built on example 1 v9's grammar: the team's own Android
// phone on a light page, a touch that glides between the real taps, the camera diving into what matters, typing sounds.
//   1  the phone glides right; the app opens (its real loading); Things › + › Person › "Record their face": the team
//      member's own selfie video, each of 8 views flying into a card, then into its slot in the app; the name; Save;
//      a scenario in one sentence (compiled by the local model); Save; Done (record_app.mjs add-person)
//   2  "Vamos testar?", and the lab opens out of the page
//   3  one take (face-take, 19 Nov 16:25:27): Filipe comes in: the frame is caught, the camera dives into his face, the
//      face is set beside his registered one and they match; he takes the book and leaves. A cut to a stranger: caught,
//      compared, no match; he takes the book; the alarm sounds; the phone gets the notification and opens the alert.
//   4  a calm close and the end card.
// Honest limits: the prototype has no face model. The face comparison is the film's illustration (marked on screen);
// DINOv2 was tried on these faces (it scored the stranger 0,57 and Filipe 0,48 against Filipe's views, so it cannot
// tell them apart) and is not shown. The person boxes come from OWLv2 over the take (detect_take.py); the scenario was
// compiled by Qwen3-1.7B; the alarm and the notification are simulated (AGENTS.md rule 1). The person seated in the
// glass cabin is blurred (rule 6). v2: the face scan screen centres the tracked face in a fixed oval and fills a ring of
// segments right then left as the head really turns (measured, OWLv2 face and nose boxes, selfie A mirrored); João and
// Alice are registered beforehand and the lab compares each face with all three; the alarm waits until the stranger
// holds the book; the alert recommends calling the police ("Sugestão da app"). v3: the app's own person flow, recorded
// for real: the name, the face recorded, the clip uploaded (the server cuts 8 views), "Filipe added", and the app's
// Home security suggestion turned on (a real rule), no typed sentence; the Things list groups the Family.
import React from "react";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, interpolateColors, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import { loadFont as loadRoboto } from "@remotion/google-fonts/Roboto";
import { loadFont as loadMono } from "@remotion/google-fonts/RobotoMono";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Brackets, clamp } from "../presentation/ui";
import { S23 as EndCard } from "../presentation/shots/End";

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
// add-person.marks.json (v3, the app's own flow): things 1.702, + 2.413, Person 4.417, the name 6.404 (typed to 7.042),
// Record their face 8.428, the clip uploaded 10.141, "Filipe added" 13.089, Turn on 16.166, saved 19.186 (the local
// model compiles the suggestion), Done 22.483
const T = {
  glide: 30, tapIcon: 80, grow: 82, s1: 118,      // the app opens; add-person from 1.38 s at 1.25x: Person, the name, Record
  face: 292,                                       // the face scan (drawn: the phone's camera screen)
  s3: 456,                                         // add-person from 10.77 s (the saving page's first frame) at 1.25x: saving, added, Continue, the suggestion, Turn on
  s4: 683, s4b: 710,                               // the rule is compiled ("Turning on…", still: 20.23-25.44 s at 5.8x), then saved, Done (1.25x)
  test: 820, lab: 910,                             // "Vamos testar?" (held 3 s); the lab opens out of the page
  f1: 1090, f1end: 1210,                           // Filipe's face: caught, compared, matched (4 s)
  cut: 1426,                                       // a cut to the stranger
  f2: 1552, f2end: 1672,                           // the stranger's face: caught, compared, no match
  alarm: 1755,                                     // take 64,75 s: the stranger holds the book, 0,25 s before his head comes up
  phoneIn: 1800, notice: 1828, tap: 1892, aside: 1912,
  close: 2090, end: 2210,
};
export const SCENE2_FRAMES = T.end + 120;
const at = (s0: number, f0: number, rate: number, t: number) => f0 + ((t - s0) / rate) * 30;
/** add-person's second at frame f, for the part after T.s4 (three speeds). */
const S3_SRC = 10.77, S4_SRC = S3_SRC + ((T.s4 - T.s3) / 30) * 1.25, S4B_SRC = 25.44;   // add-person.marks.json (v5): saving page, compile, saved page (25.467)
const S4_RATE = ((S4B_SRC - S4_SRC) * 30) / (T.s4b - T.s4);
const appSrc = (t: number) => (t < S4_SRC ? at(S3_SRC, T.s3, 1.25, t) : t < S4B_SRC ? at(S4_SRC, T.s4, S4_RATE, t) : at(S4B_SRC, T.s4b, 1.25, t));   // add-person after the scan

/* ------------------------------------------------------------------ the take (face-take: one go) */
const TAKE = "takes/scene2/face-take.mp4";
const CLOCK0 = 16 * 3600 + 25 * 60 + 27.2;             // the camera's clock at the take's first frame (read off the frames)
const A0 = 13.0, B0 = 57.8;                             // take seconds at T.lab and at T.cut
const FREEZE = T.f1end - T.f1;                          // the frames each face is held for
const F1_T = 19.0, F2_T = 62.0;                         // the frames caught: Filipe, then the stranger, facing the camera
/** The take's second on screen at frame f (frozen while a face is compared). */
const takeT = (f: number) => {
  if (f < T.cut) return f < T.f1 ? A0 + (f - T.lab) / 30 : f < T.f1end ? F1_T : F1_T + (f - T.f1end) / 30;
  return f < T.f2 ? B0 + (f - T.cut) / 30 : f < T.f2end ? F2_T : F2_T + (f - T.f2end) / 30;
};
const ALARM_ON = T.alarm;                               // measured: he lifts the book at 64,7 s, his head comes up from 65,0 s
const ALARM_FILE0 = ALARM_ON - 3;                       // the recording's first beep is 0,09 s in
const LAB_OUT = T.close;

/* ------------------------------------------------------------------ the page, the camera, the phone (as example 1) */
const SCR_W = 1206, SCR_H = 2680, PK = SCR_W / 720;
const px = (x: number) => x * PK, py = (y: number) => y * PK;
const SB_H = py(84), NAV_Y = py(1504);
const REC_Y = -21;
const PH = 900, BEZ = 9, SHC = PH - 2 * BEZ, KS = SHC / SCR_H, SWC = SCR_W * KS, PW = SWC + 2 * BEZ;
const phoneBox = (cx: number) => ({ x: cx - PW / 2, y: 540 - PH / 2 });
const OVER = 1.01;
const scr = (cx: number, sx: number, sy: number) => ({ x: phoneBox(cx).x + BEZ + KS * (OVER * sx - ((OVER - 1) / 2) * SCR_W),
  y: phoneBox(cx).y + BEZ + KS * (OVER * sy - ((OVER - 1) / 2) * SCR_H) });
const CX = { centre: 960, right: 1370, left: 560, cRight: 1300 };
type CK = { at: number; s: number; x: number; y: number };
const H0 = { s: 1, x: 960, y: 540 };
const FIELD = scr(CX.right, 603, 306.8 * 3 + REC_Y), BTN = scr(CX.right, 603, 507 * 3 + REC_Y), RECO = scr(CX.right, 603, 1000 + REC_Y), NOTE = scr(CX.cRight, 603, SB_H + 14 + px(273) / 2);
const CAM: CK[] = [
  { at: 0, ...H0 }, { at: 212, ...H0 }, { at: 232, s: 1.9, ...FIELD }, { at: 258, s: 1.9, ...FIELD }, { at: 278, s: 2.0, ...BTN }, { at: 292, s: 2.0, ...BTN }, { at: 316, ...H0 },
  { at: 611, ...H0 }, { at: 631, s: 1.7, ...RECO }, { at: 659, s: 1.7, ...RECO }, { at: 676, ...H0 },   // the Suggested scenario page (up at 605)
  { at: T.notice + 2, ...H0 }, { at: T.notice + 24, s: 1.7, ...NOTE }, { at: T.tap - 10, s: 1.7, ...NOTE }, { at: T.tap + 12, ...H0 },
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1].at) i++;
  const a = CAM[i], b = CAM[i + 1], u = ez(f, a.at, b.at);
  return { s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), u)), x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) };
};
const camCss = (f: number) => { const c = camAt(f); return `translate(960px,540px) scale(${c.s}) translate(${-c.x}px,${-c.y}px)`; };
const Grain: React.FC = () => (
  <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
    <filter id="paper2"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter="url(#paper2)" />
  </svg>
);
type BarMode = "home" | "splash" | "app" | "dark" | "none";
const ClockText: React.FC<{ time: string; color: string }> = ({ time, color }) => (
  <span style={{ position: "absolute", left: px(77), top: px(24.5), fontFamily: ROBOTO, fontWeight: 500, fontSize: px(31), lineHeight: 1, color, letterSpacing: "0.01em" }}>{time}</span>
);
const Bars: React.FC<{ mode: BarMode; time: string }> = ({ mode, time }) => {
  if (mode === "none") return null;
  if (mode === "home") return (<><div style={{ position: "absolute", left: px(64), top: 0, width: px(92), height: px(80), background: "#010101" }} /><ClockText time={time} color="#EDEDED" /></>);
  if (mode === "dark") return (
    <>
      <Img src={staticFile("phone/status-light.png")} style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SB_H }} />
      <div style={{ position: "absolute", left: px(64), top: 0, width: px(92), height: px(80), background: SCAN_BG }} />
      <ClockText time={time} color="#EDEDED" />
      <Img src={staticFile("phone/nav-light.png")} style={{ position: "absolute", left: 0, top: NAV_Y, width: SCR_W, height: SCR_H - NAV_Y }} />
    </>
  );
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SB_H, background: mode === "splash" ? "#36D09E" : "transparent" }} />
      <Img src={staticFile("phone/status-dark.png")} style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SB_H }} />
      <div style={{ position: "absolute", left: px(64), top: 0, width: px(92), height: px(80), background: mode === "splash" ? "#36D09E" : "transparent" }} />
      <ClockText time={time} color="#1C1C1C" />
      <div style={{ position: "absolute", left: 0, top: NAV_Y, width: SCR_W, height: SCR_H - NAV_Y, background: mode === "splash" ? "#D6F6EB" : "#EEF3FB" }} />
      <Img src={staticFile("phone/nav-dark.png")} style={{ position: "absolute", left: 0, top: NAV_Y, width: SCR_W, height: SCR_H - NAV_Y }} />
    </>
  );
};
const PhoneAt: React.FC<{ cx: number; shadow?: number; bars: { mode: BarMode; time: string }; children: React.ReactNode }> = ({ cx, shadow = 0, bars, children }) => {
  const { x, y } = phoneBox(cx);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: PW, height: PH, filter: shadow ? `drop-shadow(0 ${40 * shadow}px ${70 * shadow}px rgba(0,0,0,${0.45 * shadow}))` : undefined }}>
      <div style={{ position: "absolute", right: -2.5, top: PH * 0.2, width: 4, height: PH * 0.115, borderRadius: 2, background: "#2B2C30" }} />
      <div style={{ position: "absolute", right: -2.5, top: PH * 0.36, width: 4, height: PH * 0.065, borderRadius: 2, background: "#2B2C30" }} />
      <div style={{ position: "absolute", inset: 0, borderRadius: 54, background: "linear-gradient(150deg, #44464C 0%, #1B1C20 28%, #0E0F11 100%)",
        boxShadow: "inset 0 0 0 1.5px rgba(255,255,255,0.09), inset 0 0 0 3px rgba(0,0,0,0.6), 0 40px 70px -36px rgba(50,35,15,0.5), 0 12px 26px -14px rgba(50,35,15,0.35)" }} />
      <div style={{ position: "absolute", left: BEZ, top: BEZ, width: SWC, height: SHC, borderRadius: 46, overflow: "hidden", background: "#000" }}>
        <div style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SCR_H, transform: `translate(${-((OVER - 1) / 2) * SCR_W * KS}px, ${-((OVER - 1) / 2) * SCR_H * KS}px) scale(${KS * OVER})`,
          transformOrigin: "0 0", overflow: "hidden" }}>
          {children}
          <Bars {...bars} />
        </div>
        <div style={{ position: "absolute", left: SWC / 2 - 7, top: 10, width: 14, height: 14, borderRadius: 7, background: "#050506",
          boxShadow: "inset 0 0 0 1.5px #1C1D21, inset 2px 2px 3px rgba(90,100,130,0.35)" }} />
      </div>
    </div>
  );
};
const Rec: React.FC<{ src: string; from: number; rate?: number; w?: number; h?: number; top?: number; left?: number }> = ({ src, from, rate = 1, w = SCR_W, h = 2622, top = REC_Y, left }) => (
  <OffthreadVideo src={staticFile(src)} muted trimBefore={Math.round(from * 30)} playbackRate={rate} style={{ position: "absolute", left: left ?? (SCR_W - w) / 2, top, width: w, height: h }} />
);
const Line: React.FC<{ text: string; from: number; to: number; top?: number; left?: number; size?: number; align?: "left" | "center"; width?: number; color?: string }> = ({ text, from, to, top = 400, left = 150, size = 84, align = "left", width = 900, color = INK }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const dive = 1 - Math.min(1, Math.max(0, (camAt(f).s - 1.03) / 0.25));   // gone while the camera is inside the phone: no cut-off fragment at the frame's edge
  const fade = interpolate(f, [to - 10, to], [1, 0], clamp) * dive;
  return (
    <div style={{ position: "absolute", left, top, width, opacity: fade, textAlign: align, fontFamily: SERIF, fontSize: size, lineHeight: 1.13, letterSpacing: "-0.015em" }}>
      {text.split(" ").map((w, k) => {
        const a = from + 4 + 3 * k;
        return <span key={k} style={{ opacity: interpolate(f, [a, a + 5], [0, 1], clamp), color: interpolateColors(f, [a, a + 16], [color === INK ? ACCENT : color, color]) }}>{w} </span>;
      })}
    </div>
  );
};
const PhoneImg: React.FC<{ src: string }> = ({ src }) => <Img src={staticFile(src)} style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SCR_H }} />;
const Home: React.FC = () => <PhoneImg src="phone/home.jpg" />;
type Way = { f: number; x: number; y: number; press?: boolean };
const Cursor: React.FC<{ ways: Way[]; hide?: [number, number][]; show?: [number, number] }> = ({ ways, hide = [], show }) => {
  const f = useCurrentFrame();
  if (show && (f < show[0] || f > show[1])) return null;
  const fade = Math.min(1, ...hide.map(([a, b]) => (f < a - 6 || f > b + 6 ? 1 : f < a ? (a - f) / 6 : f > b ? (f - b) / 6 : 0)),
    show ? Math.min(ez(f, show[0], show[0] + 8), 1 - ez(f, show[1] - 8, show[1])) : 1);
  if (fade <= 0) return null;
  let i = 0;
  while (i < ways.length - 2 && f >= ways[i + 1].f) i++;
  const a = ways[i], b = ways[Math.min(i + 1, ways.length - 1)];
  const u = b.f > a.f ? ez(f, a.f + 3, b.f) : 1;
  const x = lerp(a.x, b.x, u) + 7 * Math.sin(f / 19), y = lerp(a.y, b.y, u) + 5 * Math.cos(f / 23);
  const pressAt = ways.filter((w) => w.press).map((w) => w.f).find((p) => Math.abs(f - p) <= 5);
  const press = pressAt === undefined ? 0 : 1 - Math.abs(f - pressAt) / 5;
  return <div style={{ position: "absolute", left: x - 34, top: y - 34, width: 68, height: 68, borderRadius: 34, background: `rgba(20,24,30,${0.16 + 0.12 * press})`,
    border: "3px solid rgba(255,255,255,0.88)", boxShadow: "0 4px 14px rgb(0 0 0 / 0.18)", opacity: fade, transform: `scale(${1 - 0.18 * press})` }} />;
};
const Grow: React.FC<{ at: number; from: [number, number, number, number]; r0: number; splash?: boolean; appAt?: number; children?: React.ReactNode }> = ({ at: a, from, r0, splash = true, appAt = 34, children }) => {
  const f = useCurrentFrame();
  if (f < a) return null;
  const u = ez(f, a, a + 14);
  const [x, y, w, h] = from;
  const W = lerp(w, SCR_W, u), H = lerp(h, SCR_H, u);
  // after the splash, the app's first screen comes in on a cut (the splash ends on its own still screen): never two screens at once
  const app = splash ? (f >= a + appAt + 5 ? 1 : 0) : ez(f, a + 4, a + 12);
  return (
    <div style={{ position: "absolute", left: x * (1 - u), top: y * (1 - u), width: W, height: H, borderRadius: r0 * (1 - u), overflow: "hidden", boxShadow: "0 30px 90px rgb(0 0 0 / 0.35)" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SCR_H, transform: `scale(${W / SCR_W}, ${H / SCR_H})`, transformOrigin: "0 0", background: splash ? "#36D09E" : "#EEF3FB" }}>
        {splash ? <Sequence from={a} layout="none"><OffthreadVideo src={staticFile("phone/open-splash.mp4")} muted trimBefore={12}
          style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SCR_H }} /></Sequence> : null}
        <AbsoluteFill style={{ opacity: app }}>{children}</AbsoluteFill>
      </div>
    </div>
  );
};
const ICON: [number, number, number, number] = [px(390), py(708), px(108), px(108)];
const CARD: [number, number, number, number] = [px(28), SB_H + 14, px(664), px(273)];
/** The notification as the team's phone draws it (measured on a real one with a picture). */
const Notice: React.FC<{ at: number }> = ({ at: a }) => {
  const f = useCurrentFrame();
  if (f < a) return null;
  const dy = interpolate(f, [a, a + 12], [-CARD[3] - 80, 0], { ...clamp, easing: theme.ease.out });
  const [x0, y0, w, h] = CARD;
  return (
    <div style={{ position: "absolute", left: x0, top: y0 + dy, width: w, height: h, borderRadius: px(44), background: "#F3F3F3", boxShadow: "0 18px 60px rgb(0 0 0 / 0.35)", fontFamily: ROBOTO }}>
      <div style={{ position: "absolute", left: px(32), top: px(32), width: px(48), height: px(48), borderRadius: "50%", overflow: "hidden", background: "#000" }}>
        <Img src={staticFile("phone/app-icon.png")} style={{ width: "100%", height: "100%" }} /></div>
      <div style={{ position: "absolute", left: px(105), top: px(42), fontSize: px(24), color: "#444746", whiteSpace: "nowrap" }}>SmartHome Beta • agora</div>
      <Img src={staticFile("phone/person/cam-face-stranger.jpg")} style={{ position: "absolute", left: px(456), top: px(32), width: px(96), height: px(96), borderRadius: px(10), objectFit: "cover" }} />
      <div style={{ position: "absolute", left: px(584), top: px(32), width: px(48), height: px(48), borderRadius: "50%", background: "#CBD6C6", display: "grid", placeItems: "center" }}>
        <svg width={px(24)} height={px(24)} viewBox="0 0 24 24"><path d="m6 15 6-6 6 6" fill="none" stroke="#1F1F1F" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" /></svg></div>
      <div style={{ position: "absolute", left: px(105), top: px(102), width: px(440 - 105), fontSize: px(31), fontWeight: 500, color: "#1F1F1F", whiteSpace: "nowrap",
        overflow: "hidden", textOverflow: "ellipsis" }}>Home Security</div>
      <div style={{ position: "absolute", left: px(105), top: px(156), width: px(505), fontSize: px(26), lineHeight: `${px(40)}px`, color: "#444746" }}>
        Someone who isn't Family came in. The alarm is on.</div>
    </div>
  );
};

/* ------------------------------------------------------------------ 1: the app, the face */
const PERSON_TAPS = { add: [2.393, 249, 90], pick: [4.369, 201, 525.6], name: [6.374, 201, 306.8], face: [8.386, 201, 507], next: [16.91, 201, 520.1],
  on: [20.085, 116, 419.6], done: [28.876, 201, 607.7] } as const;   // add-person.marks.json (v5)
// The face scan (v2): selfie A, mirrored as enrolment previews are, from 0,5 s at 1,3x. Its face is tracked (OWLv2 face
// and nose boxes, every other frame: public/phone/person/track.json) and the clip is moved under a fixed oval so the face
// stays centred and fills 86 % of the oval's height; the clip always covers the oval. Measured turns of the mirrored
// clip: straight to 1,9 s; to screen right 2,0-3,6 s (peak 0,39 at 2,8-3,4); straight by 4,2 s; to screen left
// 4,4-5,9 s (peak 0,42 at 5,0-5,6); straight from 6,4 s. No up or down movement (pitch within 0,07).
const SEL_T0 = 0.5, SEL_RATE = 1.3;
const selT = (f: number) => SEL_T0 + ((f - T.face) / 30) * SEL_RATE;
const selF = (t: number) => Math.round(T.face + ((t - SEL_T0) / SEL_RATE) * 30);
const OX = 603, OY = 1000, RX = 360, RY = 500, S_FACE = (0.86 * 2 * RY) / 324, SEL_W = 576, SEL_H = 1024;
const SCAN_BG = "#0F1013";
const STEP = { right: selF(1.85), left: selF(4.25), done: selF(6.45) };
type Track = { [k: string]: { fps: number; frames: { t: number; face: number[] | null; nose: number[] | null }[] } };
const gauss = (a: number[], k = 3) => a.map((_, i) => { let s = 0, w = 0; for (let j = -k; j <= k; j++) { const v = a[i + j]; if (v === undefined) continue; const g = Math.exp(-0.5 * (j / (k / 2)) ** 2); s += g * v; w += g; } return s / w; });
const fill = (a: (number | null)[]) => { const out = [...a] as number[]; let last = a.find((x) => x !== null) ?? 0; for (let i = 0; i < out.length; i++) { if (a[i] === null) out[i] = last as number; else last = a[i] as number; } return out; };
const useSelfie = () => {
  const d = useJson<Track>("phone/person/track.json");
  if (!d) return null;
  const fr = d["selfie-a"].frames;
  const cx = gauss(fill(fr.map((x) => (x.face ? (x.face[0] + x.face[2]) / 2 : null))));
  const cy = gauss(fill(fr.map((x) => (x.face ? (x.face[1] + x.face[3]) / 2 : null))));
  const yaw = gauss(fill(fr.map((x) => (x.face && x.nose ? -(((x.nose[0] + x.nose[2]) / 2 - (x.face[0] + x.face[2]) / 2) / (x.face[2] - x.face[0])) : null))));   // mirrored: + is screen right
  const at = (a: number[], t: number) => { const i = t * 15, i0 = Math.max(0, Math.min(a.length - 1, Math.floor(i))), i1 = Math.min(a.length - 1, i0 + 1); return a[i0] + (a[i1] - a[i0]) * (i - i0); };
  const maxSince = (sign: number, from: number, t: number) => { let m = 0; for (let s = from; s <= t; s += 1 / 15) m = Math.max(m, sign * at(yaw, s)); return m; };
  return { cx: (t: number) => at(cx, t), cy: (t: number) => at(cy, t), maxSince };
};
const FaceScan: React.FC = () => {
  const f = useCurrentFrame();
  const sel = useSelfie();
  if (!sel) return null;
  const t = Math.min(selT(f), 8.3);
  const W = SEL_W * S_FACE, H = SEL_H * S_FACE;
  const L = Math.min(OX - RX, Math.max(OX + RX - W, OX - (SEL_W - sel.cx(t)) * S_FACE));
  const Tp = Math.min(OY - RY, Math.max(OY + RY - H, OY - sel.cy(t) * S_FACE));
  const pr = t < 2.0 ? 0 : Math.min(1, sel.maxSince(1, 2.0, t) / 0.34);
  const pl = t < 4.3 ? 0 : Math.min(1, sel.maxSince(-1, 4.3, t) / 0.34);
  const done = ez(f, STEP.done, STEP.done + 10);
  const N = 96;
  const ticks = Array.from({ length: N }, (_, k) => {
    const th = (2 * Math.PI * k) / N, c = Math.cos(th), sn = Math.sin(th);
    const a = Math.abs(Math.atan2(sn, c));                       // 0 at screen right, pi at screen left
    const g = Math.max(c > 0.02 ? Math.min(1, Math.max(0, (pr - a / (Math.PI / 2)) / 0.06)) : 0, c < -0.02 ? Math.min(1, Math.max(0, (pl - (Math.PI - a) / (Math.PI / 2)) / 0.06)) : 0, done);
    const nx = c / RX, ny = sn / RY, nl = Math.hypot(nx, ny), ux = nx / nl, uy = ny / nl;
    const x = OX + RX * c, y = OY + RY * sn;
    return <line key={k} x1={x + ux * 24} y1={y + uy * 24} x2={x + ux * 66} y2={y + uy * 66} strokeWidth={10} strokeLinecap="round"
      stroke={interpolateColors(g, [0, 1], ["rgba(255,255,255,0.88)", "#2ABE9E"])} />;
  });
  const step = f < STEP.right ? 0 : f < STEP.left ? 1 : f < STEP.done ? 2 : 3;
  const LINES = ["Look straight at the camera", "Turn your head slowly to the right", "Now to the left", "Done"];
  const starts = [T.face, STEP.right, STEP.left, STEP.done];
  const ends = [STEP.right, STEP.left, STEP.done, T.s3 + 10];
  return (
    <AbsoluteFill style={{ background: SCAN_BG }}>
      <Sequence from={T.face} layout="none"><OffthreadVideo src={staticFile("phone/person/selfie-a.mp4")} muted trimBefore={Math.round(SEL_T0 * 30)} playbackRate={SEL_RATE}
        style={{ position: "absolute", left: L, top: Tp, width: W, height: H, transform: "scaleX(-1)" }} /></Sequence>
      <svg width={SCR_W} height={SCR_H} style={{ position: "absolute", inset: 0 }}>
        <defs><mask id="scanoval"><rect width={SCR_W} height={SCR_H} fill="white" /><ellipse cx={OX} cy={OY} rx={RX} ry={RY} fill="black" /></mask></defs>
        <rect width={SCR_W} height={SCR_H} fill={SCAN_BG} mask="url(#scanoval)" />
        {ticks}
      </svg>
      <div style={{ position: "absolute", left: 0, width: SCR_W, top: 250, textAlign: "center", fontFamily: ROBOTO, fontWeight: 500, fontSize: 52, color: "#fff" }}>Face scan</div>
      {LINES.map((txt, i) => {
        const a = starts[i], b = ends[i];
        if (f < a - 1 || f > b + 8) return null;
        const o = Math.min(ez(f, a, a + 8, theme.ease.out), 1 - ez(f, b, b + 8));
        return (
          <div key={i} style={{ position: "absolute", left: 0, width: SCR_W, top: OY + RY + 120, textAlign: "center", opacity: o, transform: `translateY(${10 * (1 - ez(f, a, a + 10, theme.ease.out))}px)`,
            fontFamily: ROBOTO, fontWeight: 500, fontSize: 58, color: "#fff", display: "flex", justifyContent: "center", alignItems: "center", gap: 22 }}>
            {i === 3 ? <span style={{ width: 70, height: 70, borderRadius: 35, background: "#2ABE9E", display: "grid", placeItems: "center", transform: `scale(${0.6 + 0.4 * ez(f, a, a + 8, theme.ease.out)})` }}>
              <svg width={40} height={40} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="m5.5 12.5 4.2 4.2 8.8-9.4" /></svg></span> : null}
            {txt}
          </div>);
      })}

    </AbsoluteFill>
  );
};
const APP_END = Math.round(appSrc(31.85)) - 2;   // add-person ends at 31.93 s
const tapF = (f: number, t: readonly [number, number, number]) => ({ f, x: t[1] * 3, y: t[2] * 3 + REC_Y, press: true });
const WAYS_A: Way[] = (() => {
  const s1 = (t: readonly [number, number, number]) => tapF(Math.round(at(1.38, T.s1, 1.25, t[0])), t);
  const sA = (t: readonly [number, number, number]) => tapF(Math.round(appSrc(t[0])), t);
  const name = s1(PERSON_TAPS.name);
  return [{ f: 54, x: 860, y: 2050 }, { f: T.tapIcon, x: ICON[0] + ICON[2] / 2, y: ICON[1] + ICON[3] / 2, press: true }, { f: T.s1 + 10, x: 700, y: 1700 },
    s1(PERSON_TAPS.add), s1(PERSON_TAPS.pick), name, { f: name.f + 18, x: name.x + 200, y: name.y + 380 }, s1(PERSON_TAPS.face), { f: T.s3 + 30, x: 760, y: 2000 },
    sA(PERSON_TAPS.next), sA(PERSON_TAPS.on), sA(PERSON_TAPS.done), { f: T.test + 20, x: 760, y: 2100 }];
})();
const ScreenA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {f < T.s1 + 12 ? <Home /> : null}
      {f < T.face + 2 ? <Grow at={T.grow} from={ICON} r0={40}><Sequence from={T.s1} layout="none"><Rec src="app/add-person.mp4" from={1.38} rate={1.25} /></Sequence></Grow> : null}
      {f >= T.face && f < T.s3 ? <FaceScan /> : null}
      {f >= T.s3 && f < T.s4 ? <Sequence from={T.s3} layout="none"><Rec src="app/add-person.mp4" from={S3_SRC} rate={1.25} /></Sequence> : null}
      {f >= T.s4 && f < T.s4b ? <Sequence from={T.s4} layout="none"><Rec src="app/add-person.mp4" from={S4_SRC} rate={S4_RATE} /></Sequence> : null}
      {f >= T.s4b && f < APP_END ? <Sequence from={T.s4b} layout="none"><Rec src="app/add-person.mp4" from={S4B_SRC} rate={1.25} /></Sequence> : null}
      <Cursor ways={WAYS_A} show={[54, T.test + 4]} hide={[[T.grow - 2, T.s1 + 10], [T.face - 1, T.s3 + 24]]} />
    </AbsoluteFill>
  );
};
/* ------------------------------------------------------------------ 3: the lab */
const AP = [0.66, 0.705, 0.693, 0.732];
const ALARM = [0.3135, 0.3023, 0.3243, 0.3115];
const CABIN = [0.645, 0.41, 0.745, 0.69];               // the glass cabin: the detector's boxes of the person seated there
// Her face only is blurred (the team's choice, 19 Nov): a soft oval on her head, followed frame by frame by template
// matching (cabin-face.json, from a box set by hand); she keeps a detector box like anyone else ("person")
type Head = { fps: number; frames: { t: number; head: number[] }[] };
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
const BEEP_LEN = 6.67;
const beepAt = (s: number) => { const m = s % BEEP_LEN; return Math.max(0, ...BEEPS.map(([a, b]) => Math.min(interpolate(m, [a - 0.03, a + 0.12], [0, 1], clamp), interpolate(m, [b - 0.05, b + 0.3], [1, 0], clamp)))); };
const KIND = { thing: "#2ABE9E", person: "#FFFFFF", device: "#8B7CF6", alarm: "#E5322D", ok: "#1FA37F" };
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
const ms = (s: number) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
// the faces caught (take px 2304 x 1296 -> 1920 x 1080), and the two people's moments
const FACE1 = { x: (926.7 / 2304) * 1920, y: (440.8 / 1296) * 1080 }, FACE2 = { x: (990.7 / 2304) * 1920, y: (473.6 / 1296) * 1080 };
const GRAB1 = 22.0, GRAB2 = 64.6, PUTBACK2 = 68.3;       // each takes the book; the stranger puts it back at 68,2 s and leaves
/** One copy of the lab picture: the take (or a caught frame while a face is compared). */
const Picture: React.FC<{ f: number }> = ({ f }) => (
  <>
    {f < T.cut + 6 ? <Sequence from={T.lab} durationInFrames={T.f1 - T.lab + 1} layout="none"><OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round(A0 * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} /></Sequence> : null}
    {f >= T.f1 && f < T.f1end ? <Img src={staticFile("phone/person/cam-filipe.jpg")} style={{ position: "absolute", width: 1920, height: 1080 }} /> : null}
    {f >= T.f1end && f < T.cut + 6 ? <Sequence from={T.f1end} layout="none"><OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round(F1_T * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} /></Sequence> : null}
    {f >= T.cut - 3 && f < T.f2 + 1 ? <AbsoluteFill style={{ opacity: ez(f, T.cut - 3, T.cut + 5) }}><Sequence from={T.cut - 3} layout="none"><OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round((B0 - 0.1) * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} /></Sequence></AbsoluteFill> : null}
    {f >= T.f2 && f < T.f2end ? <Img src={staticFile("phone/person/cam-stranger.jpg")} style={{ position: "absolute", width: 1920, height: 1080 }} /> : null}
    {f >= T.f2end ? <Sequence from={T.f2end} layout="none"><OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round(F2_T * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} /></Sequence> : null}
  </>
);
/** The lab: the picture, the cabin blurred, the detector's boxes, the faces' verdicts, the alarm, the readout. */
const LabLayer: React.FC<{ ov?: number }> = ({ ov = 1 }) => {
  const f = useCurrentFrame();
  const det = useJson<Det>("takes/scene2/face-take.boxes.json");
  const heads = useJson<Head>("takes/scene2/cabin-face.json");
  const t = takeT(f);
  const ringing = f >= ALARM_ON;
  const beep = ringing ? beepAt((f - ALARM_FILE0) / 30) : 0;
  let person: number[] | null = null, seated: number[] | null = null;
  if (det) {
    const cab = (b: number[]) => (b[0] + b[2]) / 2 > CABIN[0] && (b[0] + b[2]) / 2 < CABIN[2] && (b[1] + b[3]) / 2 > CABIN[1] && (b[1] + b[3]) / 2 < CABIN[3];
    const track = (inCab: boolean) => {
      const s = det.frames.map((x) => ({ t: x.t, b: x.boxes.filter((y) => y.label === "a person" && (inCab ? cab(y.box) : y.score >= 0.15 && !cab(y.box))).sort((p, q) => q.score - p.score)[0] })).filter((x) => x.b);
      const a = [...s].reverse().find((x) => x.t <= t), c = s.find((x) => x.t >= t);
      if (!a || !c || c.t - a.t >= 1.2) return null;
      const u = c.t > a.t ? (t - a.t) / (c.t - a.t) : 0;
      return a.b.box.map((v, i) => v + (c.b.box[i] - v) * u);
    };
    person = track(false); seated = track(true);
  }
  const hb = heads ? heads.frames.reduce((p, q) => (Math.abs(q.t - t) < Math.abs(p.t - t) ? q : p)).head : null;
  const second = f >= T.cut;
  const known = !second && f >= T.f1 + 66, stranger = second && f >= T.f2 + 66;
  const pLabel = known ? (t >= GRAB1 ? "Filipe · com o livro" : "Filipe · reconhecido") : stranger ? (t >= GRAB2 && t < PUTBACK2 ? "desconhecido · com o livro" : "desconhecido") : undefined;
  const pColor = known ? KIND.ok : stranger ? KIND.alarm : KIND.person;
  const ax = (ALARM[0] + ALARM[2]) / 2 * 1920, ay = (ALARM[1] + ALARM[3]) / 2 * 1080;
  const chip = ringing ? ["Um desconhecido pegou no livro · alarme e mensagem", KIND.alarm, "#fff"] : known ? ["Filipe é de casa · nada toca", KIND.ok, "#fff"]
    : stranger ? ["Não é ninguém de casa", "rgba(255,255,255,0.94)", "#B42318"] : ["Cenário ativo · Home Security", "rgba(255,255,255,0.94)", INK];
  // her whole head (hair, ears, jaw) and a margin: the tracked box is face and hair, about 52 x 68 px here
  const ov2 = hb ? (() => { const ax = ((hb[2] - hb[0]) / 2) * 1920 * 1.75, ay = ((hb[3] - hb[1]) / 2) * 1080 * 1.6;
    const cx = ((hb[0] + hb[2]) / 2) * 1920, cy = ((hb[1] + hb[3]) / 2) * 1080; return { x: cx - ax * 1.15, y: cy - ay * 1.15, w: ax * 2.3, h: ay * 2.3, ax, ay }; })() : null;
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, background: "#000" }}>
      <Picture f={f} />
      {/* the face of the person in the glass cabin, hidden (AGENTS.md rule 6): a soft-edged oval that follows her head,
          pixelated (9 px blocks), then blurred */}
      <svg width={0} height={0} style={{ position: "absolute" }}><defs><filter id="cabin-pix" x="0" y="0" width="1" height="1">
        <feFlood x={4} y={4} width={1} height={1} /><feComposite width={9} height={9} /><feTile result="t" />
        <feComposite in="SourceGraphic" in2="t" operator="in" /><feMorphology operator="dilate" radius={4.5} /></filter></defs></svg>
      {ov2 ? <div style={{ position: "absolute", left: ov2.x, top: ov2.y, width: ov2.w, height: ov2.h,
        WebkitMaskImage: `radial-gradient(ellipse ${ov2.ax}px ${ov2.ay}px at 50% 50%, #000 76%, transparent 100%)`, maskImage: `radial-gradient(ellipse ${ov2.ax}px ${ov2.ay}px at 50% 50%, #000 76%, transparent 100%)` }}>
        <div style={{ position: "absolute", inset: 0, overflow: "hidden", filter: "url(#cabin-pix) blur(6px)" }}>
          <div style={{ position: "absolute", left: -ov2.x, top: -ov2.y, width: 1920, height: 1080 }}><Picture f={f} /></div>
        </div>
      </div> : null}
      <AbsoluteFill style={{ background: "rgba(229,50,45,0.035)", opacity: beep }} />
      <AbsoluteFill style={{ opacity: ov }}>
      {ringing ? <div style={{ position: "absolute", left: ax, top: ay, width: 96, height: 96, transform: "translate(-50%,-50%)", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(255,90,80,0.7) 0%, rgba(255,60,50,0.25) 38%, rgba(255,40,40,0) 70%)", opacity: 0.15 + 0.5 * beep }} /> : null}
      {seated ? <Box b={seated} kind="person" color={KIND.person} dark /> : null}
      {person ? <Box b={person} kind="person" text={pLabel} color={pColor} dark={!pLabel} /> : null}
      <Box b={AP} kind="device" text="ponto de acesso" color={KIND.device} brackets={false} below />
      <Box b={ALARM} kind="device" text={ringing ? "alarme · a tocar" : "alarme"} color={ringing ? KIND.alarm : KIND.device} pad={0.008} brackets={false} />
      <div style={{ position: "absolute", left: 36, bottom: 32, padding: "10px 18px", borderRadius: 999, fontFamily: SANS, fontSize: 24, background: chip[1], color: chip[2], boxShadow: "0 10px 30px -10px rgb(0 0 0 / 0.4)" }}>{chip[0]}</div>
      <div style={{ position: "absolute", right: 36, top: 30, display: "flex", alignItems: "center", gap: 14, padding: "9px 16px", borderRadius: 10, background: "rgba(10,12,16,0.72)",
        fontFamily: MONO, fontWeight: 500, fontSize: 24, color: "#fff", letterSpacing: "0.02em" }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: "#ff3b30", opacity: Math.floor(f / 15) % 2 ? 1 : 0.35 }} />REC {ms(t)}
      </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
/** A caught face: the frame flashes, the camera dives onto the face, the face is set beside the registered one; a
 *  scan passes over both; then the verdict (a match for Filipe, none for the stranger); the camera pulls back. */
const DIVE = 3.0;
const faceZoom = (f: number) => {
  for (const [a, face] of [[T.f1, FACE1], [T.f2, FACE2]] as const) {
    if (f >= a && f < a + FREEZE) {
      const u = ez(f, a + 4, a + 24) * (1 - ez(f, a + 92, a + 116));
      return { s: lerp(1, DIVE, u), fx: face.x, fy: face.y, u };
    }
  }
  return { s: 1, fx: 960, fy: 540, u: 0 };
};
// The people the app knows: João and Alice were registered before (free portraits, public/stock/portraits.json); Filipe in
// this film. The camera face is checked against each in turn; Filipe matches his own, the stranger matches none.
const REGISTERED = [{ name: "Filipe", src: "phone/person/face-view-1.jpg" }, { name: "João", src: "phone/person/joao.jpg" }, { name: "Alice", src: "phone/person/alice.jpg" }];
const Compare: React.FC<{ a: number; match: number | null }> = ({ a, match }) => {
  const f = useCurrentFrame();
  if (f < a + 16 || f > a + 100) return null;
  const inU = ez(f, a + 16, a + 30, theme.ease.out), outU = ez(f, a + 88, a + 100, theme.ease.in);
  const verdictAt = a + 30 + 10 * REGISTERED.length + 2;
  const verdict = ez(f, verdictAt, verdictAt + 10, theme.ease.out);
  const ok = match !== null, col = ok ? KIND.ok : KIND.alarm;
  const camSrc = ok ? "phone/person/cam-face-filipe.jpg" : "phone/person/cam-face-stranger.jpg";
  return (
    <div style={{ position: "absolute", left: 1010, top: 250, width: 820, height: 560, opacity: inU * (1 - outU), transform: `translateX(${(1 - inU) * 40}px)` }}>
      <div style={{ position: "absolute", left: 0, top: 40, width: 300 }}>
        <div style={{ width: 300, height: 300, borderRadius: 26, overflow: "hidden", boxShadow: `0 0 0 ${4 * verdict}px ${col}, 0 30px 70px -26px rgba(0,0,0,0.6)` }}>
          <Img src={staticFile(camSrc)} style={{ width: 300, height: 300, objectFit: "cover" }} /></div>
        <div style={{ marginTop: 14, fontFamily: SANS, fontSize: 22, fontWeight: 600, color: "#fff", textAlign: "center", textShadow: "0 2px 10px rgba(0,0,0,0.6)" }}>Câmara, agora</div>
      </div>
      {REGISTERED.map((p, k) => {
        const s0 = a + 30 + 10 * k, scan = interpolate(f, [s0, s0 + 10], [0, 1], clamp);
        const mine = ok && match === k, dim = ok && !mine ? verdict : 0;
        const ring = mine ? `0 0 0 ${4 * verdict}px ${KIND.ok}` : f >= s0 && f < s0 + 11 ? "0 0 0 3px #7CF5D8" : "0 0 0 1.5px rgba(255,255,255,0.35)";
        const cross = !ok ? ez(f, verdictAt + 3 * k, verdictAt + 3 * k + 8, theme.ease.out) : 0;
        return (
          <div key={p.name} style={{ position: "absolute", left: 380, top: k * 168, width: 420, height: 150, display: "flex", alignItems: "center", gap: 22, opacity: 1 - 0.65 * dim }}>
            <div style={{ position: "relative", width: 150, height: 150, borderRadius: 20, overflow: "hidden", boxShadow: `${ring}, 0 20px 40px -20px rgba(0,0,0,0.6)` }}>
              <Img src={staticFile(p.src)} style={{ width: 150, height: 150, objectFit: "cover" }} />
              {scan > 0 && scan < 1 ? <div style={{ position: "absolute", left: 0, right: 0, top: `${scan * 100}%`, height: 3, background: "#7CF5D8", boxShadow: "0 0 14px 5px rgba(124,245,216,0.55)" }} /> : null}
            </div>
            <div style={{ fontFamily: SANS, fontSize: 26, fontWeight: 600, color: "#fff", textShadow: "0 2px 10px rgba(0,0,0,0.6)" }}>{p.name}<div style={{ fontSize: 17, fontWeight: 500, opacity: 0.75 }}>registado</div></div>
            {mine || cross > 0 ? <div style={{ position: "absolute", left: 122, top: -6, width: 40, height: 40, borderRadius: 20, background: mine ? KIND.ok : KIND.alarm, display: "grid", placeItems: "center",
              opacity: mine ? verdict : cross, transform: `scale(${0.6 + 0.4 * (mine ? verdict : cross)})`, boxShadow: "0 6px 18px -6px rgba(0,0,0,0.6)" }}>
              <svg width={22} height={22} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round">{mine ? <path d="m5.5 12.5 4.2 4.2 8.8-9.4" /> : <path d="M6 6l12 12M18 6 6 18" />}</svg>
            </div> : null}
          </div>);
      })}
      <div style={{ position: "absolute", left: 0, width: 300, top: 420, textAlign: "center", opacity: verdict }}>
        <span style={{ display: "inline-block", padding: "10px 20px", borderRadius: 999, background: col, color: "#fff", fontFamily: SANS, fontSize: 24, fontWeight: 600, whiteSpace: "nowrap" }}>
          {ok ? "É o Filipe · é de casa" : "Não é ninguém de casa"}</span>
      </div>
      <div style={{ position: "absolute", left: 0, width: 300, top: 478, textAlign: "center", fontFamily: SANS, fontSize: 17, color: "rgba(255,255,255,0.75)" }}>comparação ilustrativa</div>
    </div>
  );
};
const LabFrame: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.lab || f > LAB_OUT + 16) return null;
  const u = ez(f, T.lab, T.lab + 22);
  const small: Rect = { x: 960 - 320, y: 610, w: 640, h: 360 }, full: Rect = { x: 0, y: 0, w: 1920, h: 1080 };
  const r = lerpRect(small, full, u);
  const blur = ez(f, T.phoneIn, T.phoneIn + 20) * (1 - ez(f, T.aside, T.aside + 26));
  const z = faceZoom(f);
  const flash = Math.max(0, 1 - Math.abs(f - T.f1) / 4, 1 - Math.abs(f - T.f2) / 4);
  return (
    <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: 26 * (1 - u), overflow: "hidden", opacity: ez(f, T.lab, T.lab + 8) * (1 - ez(f, LAB_OUT, LAB_OUT + 16)),
      boxShadow: u < 1 ? "0 40px 90px -30px rgba(70,50,25,0.5)" : undefined }}>
      <div style={{ width: 1920, height: 1080, transform: `scale(${r.w / 1920})`, transformOrigin: "0 0", filter: blur > 0.01 ? `blur(${6 * blur}px) brightness(${1 - 0.25 * blur})` : undefined }}>
        <div style={{ width: 1920, height: 1080, transform: `translate(${lerp(960, 600, z.u)}px, ${540}px) scale(${z.s}) translate(${-lerp(960, z.fx, z.u)}px, ${-lerp(540, z.fy, z.u)}px)`, transformOrigin: "0 0" }}>
          <LabLayer ov={(1 - z.u) * (1 - 0.65 * ez(f, T.aside + 30, T.aside + 44) * (1 - ez(f, T.close - 6, T.close + 6)))} />   {/* the labels step back while the camera is on a face, and under the app's suggestion */}
        </div>
        <AbsoluteFill style={{ background: "rgba(0,0,0,0.35)", opacity: z.u }} />
        <Compare a={T.f1} match={0} />
        <Compare a={T.f2} match={null} />
        <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.7 }} />
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ 3: the phone over the lab */
const ALERT_OPEN = 3.218;   // alert-person-open.marks.json (v4): the tap
/** The alert opening (its recording stops 0,3 s after the page is up), then its last frame held. */
const AlertRec: React.FC = () => {
  const f = useCurrentFrame();
  return f < T.tap + 18 ? <Sequence from={T.tap + 2} layout="none"><Rec src="app/alert-person-open.mp4" from={ALERT_OPEN} /></Sequence>
    : <Img src={staticFile("phone/person/alert-last.png")} style={{ position: "absolute", left: 0, top: REC_Y, width: SCR_W, height: 2622 }} />;
};
const ScreenC: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Home />
    <Notice at={T.notice} />
    <Grow at={T.tap} from={CARD} r0={px(40)} splash={false}><AlertRec /></Grow>
    <Cursor show={[T.notice + 10, T.close]} hide={[[T.tap + 4, T.close]]} ways={[{ f: T.notice + 10, x: 820, y: 1500 },
      { f: T.tap, x: CARD[0] + CARD[2] * 0.42, y: CARD[1] + CARD[3] / 2, press: true }, { f: T.tap + 34, x: 760, y: 1500 }]} />
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ the app's suggestion, traced on the phone */
// alert-person-open's last frame (1206 x 2622): the camera picture spans y 548-1172, the "Possible intrusion" card
// x 48-1158, y 1614-1916. A thin line leaves the picture, runs down outside the phone and points at the card.
const Suggestion: React.FC<{ cx: number }> = ({ cx }) => {
  const f = useCurrentFrame();
  const a = T.aside + 36;
  if (f < a || f > T.close + 8) return null;
  const pic = scr(cx, 1158, 860 + REC_Y), card = scr(cx, 1158, 1765 + REC_Y);
  const bx = phoneBox(cx).x + PW + 46;
  const len = (bx - pic.x) * 2 + (card.y - pic.y);
  const draw = ez(f, a, a + 22, theme.ease.inOut), lab = ez(f, a + 16, a + 30, theme.ease.out), out = 1 - ez(f, T.close - 4, T.close + 8);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: out }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <path d={`M ${pic.x} ${pic.y} H ${bx} V ${card.y} H ${card.x + 10}`} fill="none" stroke="#fff" strokeWidth={2.5} strokeLinejoin="round"
          strokeDasharray={len} strokeDashoffset={len * (1 - draw)} style={{ filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.5))" }} />
        <circle cx={pic.x} cy={pic.y} r={5} fill="#fff" opacity={draw > 0 ? 1 : 0} />
        <path d={`M ${card.x + 22} ${card.y - 9} L ${card.x + 8} ${card.y} L ${card.x + 22} ${card.y + 9}`} fill="none" stroke="#fff" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" opacity={ez(f, a + 18, a + 22)} />
      </svg>
      <div style={{ position: "absolute", left: bx + 24, top: (pic.y + card.y) / 2 - 70, width: 470, padding: "16px 20px", borderRadius: 16, background: "rgba(255,255,255,0.95)",
        boxShadow: "0 18px 40px -18px rgba(0,0,0,0.6)", opacity: lab, transform: `translateX(${(1 - lab) * 16}px)`, fontFamily: SANS }}>
        <div style={{ fontSize: 16, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: "#6E695F" }}>Sugestão da app</div>
        <div style={{ fontSize: 23, color: INK, marginTop: 6, lineHeight: 1.35 }}>Pessoa desconhecida + alarme a tocar + objeto levado: ligar à polícia (112).</div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ the local models at work (bottom right) */
// What really ran: Qwen3-1.7B compiled the sentence (/api/rules); OWLv2 found the people in the take (detect_take.py).
const MODELS = [
  { from: Math.round(appSrc(20.09)), until: Math.round(appSrc(25.47)), name: "Qwen3-1.7B", what: "a sugestão passa a regra" },
  { from: T.lab + 20, until: LAB_OUT, name: "OWLv2", what: "deteta pessoas e coisas" },
];
const ModelsCard: React.FC = () => {
  const f = useCurrentFrame();
  if (f < MODELS[0].from || f > LAB_OUT + 10) return null;
  const shown = MODELS.filter((m) => f >= m.from).slice(-2);
  const out = ez(f, LAB_OUT - 6, LAB_OUT + 6);
  return (
    <div style={{ position: "absolute", right: 36, bottom: 30, width: 392, padding: "12px 16px 10px", borderRadius: 14, background: "rgba(255,255,255,0.93)",
      boxShadow: "0 14px 34px -14px rgba(40,30,15,0.4), 0 0 0 1px rgba(30,25,15,0.06)", fontFamily: SANS, opacity: ez(f, MODELS[0].from, MODELS[0].from + 10) * (1 - out) }}>
      <div style={{ fontSize: 15, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: "#7A756C", marginBottom: 6 }}>Modelos locais</div>
      {shown.map((m) => {
        const busy = f < m.until;
        return (
          <div key={m.name} style={{ display: "flex", alignItems: "center", gap: 10, padding: "4px 0", opacity: ez(f, m.from, m.from + 10), transform: `translateY(${8 * (1 - ez(f, m.from, m.from + 12, theme.ease.out))}px)` }}>
            <span style={{ width: 9, height: 9, borderRadius: 5, background: busy ? ACCENT : "#C9C3B8", opacity: busy ? 0.55 + 0.45 * Math.abs(Math.sin(f / 8)) : 1 }} />
            <span style={{ fontSize: 20, fontStyle: "italic", fontWeight: 600, color: INK, whiteSpace: "nowrap" }}>{m.name}</span>
            <span style={{ fontSize: 18, color: "#6E695F", whiteSpace: "nowrap" }}>{m.what}</span>
          </div>);
      })}
    </div>
  );
};

/* ------------------------------------------------------------------ typing */
const SERIF_LINES: [string, number][] = [["Abre-se a app.", 44], ["Adiciona-se uma pessoa.", 150], ["Grava-se a cara, a rodar.", T.face], ["A app guarda o vídeo.", T.s3 + 4],
  ["E sugere a segurança da casa.", T.s3 + 149], ["Vamos testar?", T.test + 10], ["O Filipe entrou, e o alarme não tocou.", T.close + 16], ["Um desconhecido entra, e o alarme é ativado.", T.close + 44]];
const WORD_KEYS = SERIF_LINES.flatMap(([text, from]) => text.split(" ").map((_, k) => from + 4 + 3 * k));
const typedAt = (start: number, n: number, step: number) => Array.from({ length: n }, (_, i) => start + i * step);
const APP_KEYS = typedAt(6.573, 6, 0.0725).map((t) => Math.round(at(1.38, T.s1, 1.25, t)));   // "Filipe", typed until 7.008 s (named)

/* ------------------------------------------------------------------ the scene */
export const Scene2Face: React.FC = () => {
  const f = useCurrentFrame();
  const cxA = lerp(CX.centre, CX.right, ez(f, T.glide, T.glide + 36)) + 1100 * ez(f, T.test - 2, T.test + 16, theme.ease.in);
  const cxC = lerp(CX.cRight + 900, CX.cRight, ez(f, T.phoneIn, T.phoneIn + 26, theme.ease.out));
  const cxC2 = lerp(cxC, CX.left, ez(f, T.aside, T.aside + 30)) - 1300 * ez(f, LAB_OUT - 10, LAB_OUT + 18, theme.ease.in);
  const closeIn = ez(f, T.close, T.close + 16);
  const endIn = ez(f, T.end - 14, T.end);
  const tap1 = (w: Way) => w.f;
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f < T.test + 30 ? <PhoneAt cx={cxA} bars={{ time: "16:21", mode: f < T.grow + 10 ? "home" : f < T.s1 ? "splash" : f >= T.face && f < T.s3 ? "dark" : "app" }}><ScreenA /></PhoneAt> : null}
        <Line text="Abre-se a app." from={44} to={150} size={87} />
        <Line text="Adiciona-se uma pessoa." from={150} to={T.face} />
        <Line text="Grava-se a cara, a rodar." from={T.face} to={T.s3 + 4} />
        <Line text="A app guarda o vídeo." from={T.s3 + 4} to={T.s3 + 145} size={87} />
        <Line text="E sugere a segurança da casa." from={T.s3 + 149} to={T.test + 6} size={80} width={960} />
        <Line text="Vamos testar?" from={T.test + 10} to={T.lab + 14} top={360} left={0} width={1920} align="center" size={104} />
      </AbsoluteFill>
      <LabFrame />
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f >= T.phoneIn && f < LAB_OUT + 20 ? <PhoneAt cx={cxC2} shadow={1} bars={{ time: "16:26", mode: f < T.tap + 10 ? "home" : "app" }}><ScreenC /></PhoneAt> : null}
        <Suggestion cx={cxC2} />
      </AbsoluteFill>
      {/* the close: calm, on the page */}
      {f >= T.close && f < T.end + 2 ? (
        <AbsoluteFill style={{ background: PAPER, opacity: closeIn * (1 - endIn) }}>
          <Line text="O Filipe entrou, e o alarme não tocou." from={T.close + 16} to={T.end + 2} top={400} left={0} width={1920} align="center" size={72} />
          <Line text="Um desconhecido entra, e o alarme é ativado." from={T.close + 44} to={T.end + 2} top={500} left={0} width={1920} align="center" size={72} />
        </AbsoluteFill>) : null}
      {f >= T.end ? <Sequence from={T.end} layout="none"><EndCard bg={PAPER} /></Sequence> : null}
      <ModelsCard />
      <Grain />
      {/* sound: as example 1 (the song; the team's whooshes as they are; taps; typing), plus the face scenes' shutter, scan,
          match and mismatch; the alarm a beat after the stranger's face fails to match; the buzz */}
      <Audio src={staticFile("audio/music/bed-real-long.wav")} volume={(v) => 0.5 * interpolate(v, [0, 20, T.lab, T.lab + 30, ALARM_ON - 10, ALARM_ON, T.close, T.close + 20, T.end, T.end + 20, SCENE2_FRAMES - 16, SCENE2_FRAMES],
        [0, 1, 1, 0.85, 0.85, 0.5, 0.5, 1.1, 1.1, 1.3, 1.3, 0], clamp)} />
      {[[222, "zoom-soft", 0.9], [621, "zoom-soft", 0.9], [T.notice + 13, "zoom-soft", 0.9], [T.f1 + 14, "zoom-soft", 0.9], [T.f2 + 14, "zoom-soft", 0.9],
        [T.glide + 18, "slow-gentle", 0.32], [T.test + 12, "fast", 0.08], [T.phoneIn + 4, "slow-gentle", 0.32], [T.aside + 15, "slow-gentle", 0.28], [LAB_OUT + 4, "fast", 0.07],
        [T.lab + 11, "riser-soft", 0.15], [T.close + 8, "riser-soft", 0.12],
        [T.end + 6, "riser-soft", 0.15], [T.end + 23, "slow-gentle", 0.28], [T.end + 68, "zoom-soft", 0.6],
        ].map(([peak, n, vol], i) => {
        const PEAK: Record<string, number> = { "slow-gentle": 0.28, "zoom-soft": 0.37, throw: 0.07, fast: 0.15, "riser-soft": 0.43 };
        return <Sequence key={`w${i}`} from={Math.round((peak as number) - PEAK[n as string] * 30)} layout="none"><Audio src={staticFile(`audio/sfx/whoosh/${n}.wav`)} volume={vol as number} /></Sequence>;
      })}
      {WAYS_A.filter((w) => w.press).map(tap1).concat([T.tap]).map((a, i) => (
        <Sequence key={`t${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.13} /></Sequence>))}
      {/* the face scan: a soft scan under the capture, the success sound on "Done" */}
      <Sequence from={T.face + 20} durationInFrames={STEP.done - T.face - 14} layout="none"><Audio src={staticFile("audio/sfx/ui/scan.wav")} loop
        volume={(v) => 0.3 * Math.min(ez(v, 0, 10), 1 - ez(v, STEP.done - T.face - 28, STEP.done - T.face - 14))} /></Sequence>
      <Sequence from={STEP.done - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.3} /></Sequence>
      {[T.f1, T.f2].map((a, i) => <Sequence key={`c${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/shutter-2.wav")} volume={0.32} /></Sequence>)}
      {[T.f1, T.f2].map((a, i) => <Sequence key={`sc${i}`} from={a + 30} layout="none"><Audio src={staticFile("audio/sfx/ui/scan.wav")} volume={0.5} /></Sequence>)}
      <Sequence from={T.f1 + 62 - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.42} /></Sequence>
      <Sequence from={T.f2 + 62 - 2} layout="none"><Audio src={staticFile("audio/sfx/ui/wrong.wav")} volume={0.9} /></Sequence>
      <Sequence from={Math.round(appSrc(13.533)) - 6} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.22} /></Sequence>
      <Sequence from={Math.round(appSrc(25.55)) - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.35} /></Sequence>
      <Sequence from={ALARM_FILE0} durationInFrames={LAB_OUT + 16 - ALARM_FILE0} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} loop
        volume={(v) => { const g = ALARM_FILE0 + v; return (g < T.phoneIn ? 0.5 : g < T.aside ? 0.22 : 0.36) * (1 - ez(g, LAB_OUT - 4, LAB_OUT + 16)); }} /></Sequence>
      <Sequence from={T.notice} layout="none"><Audio src={staticFile("audio/sfx/scene1/buzz.wav")} volume={0.5} /></Sequence>
      {WORD_KEYS.map((a, i) => <Sequence key={`kw${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 7) % 12) + 1}.wav`)} volume={0.22} /></Sequence>)}
      {APP_KEYS.map((a, i) => <Sequence key={`ka${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 5) % 12) + 1}.wav`)} volume={0.15} /></Sequence>)}
    </AbsoluteFill>
  );
};
