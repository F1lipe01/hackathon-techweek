// Real example 2, the unknown person (19 Nov, the lab), v1, built on example 1 v9's grammar: the team's own Android
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
// glass cabin is blurred (rule 6).
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
// add-person.marks.json: things 1.702, + 2.398, Person 4.367, Record their face 6.531, faces 7.438, name 9.623,
// Save 11.517, added 11.817, Create a scenario 14.336, the field 16.205, typing 16.40-20.173, Save 21.357,
// saved 27.376 (the local model takes ~6 s: shown 4x faster), Done 30.661
const T = {
  glide: 30, tapIcon: 80, grow: 82, s1: 118,      // the app opens; add-person from 1.38 s at 1.25x
  face: 246,                                       // the selfie video: 8 views of the face
  s3: 410,                                         // add-person from 7.44 s at 1.4x: the views, the name, Save
  s4: 504,                                         // add-person from 11.80 s at 1.5x: added, the scenario, typing
  s4b: 700, s4c: 742,                              // the save waits (21.6-27.2 s at 4x), then saved, Done (27.2 s on, 1.5x)
  test: 820, lab: 910,                             // "Vamos testar?" (held 3 s); the lab opens out of the page
  f1: 1090, f1end: 1210,                           // Filipe's face: caught, compared, matched (4 s)
  cut: 1426,                                       // a cut to the stranger
  f2: 1552, f2end: 1672,                           // the stranger's face: caught, compared, no match
  phoneIn: 1730, notice: 1758, tap: 1822, aside: 1842,
  close: 1992, end: 2112,
};
export const SCENE2_FRAMES = T.end + 120;
const at = (s0: number, f0: number, rate: number, t: number) => f0 + ((t - s0) / rate) * 30;
/** add-person's second at frame f, for the part after T.s4 (three speeds). */
const s4Src = (t: number) => (t < 21.6 ? at(11.8, T.s4, 1.5, t) : t < 27.2 ? at(21.6, T.s4b, 4, t) : at(27.2, T.s4c, 1.5, t));

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
const ALARM_ON = T.f2end + 24;                          // a beat after the failed match
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
const BTN = scr(CX.right, 603, 1366 + REC_Y), FIELD = scr(CX.right, 603, 1391 + REC_Y), TXT = scr(CX.right, 603, 1000 + REC_Y), NOTE = scr(CX.cRight, 603, SB_H + 14 + px(273) / 2);
const CAM: CK[] = [
  { at: 0, ...H0 }, { at: 196, ...H0 }, { at: 222, s: 2.0, ...BTN }, { at: 246, s: 2.0, ...BTN }, { at: 270, ...H0 },
  { at: 436, ...H0 }, { at: 452, s: 1.9, ...FIELD }, { at: 484, s: 1.9, ...FIELD }, { at: 500, ...H0 },
  { at: 576, ...H0 }, { at: 596, s: 2.4, ...TXT }, { at: 680, s: 2.4, ...TXT }, { at: 698, ...H0 },
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
type BarMode = "home" | "splash" | "app" | "none";
const ClockText: React.FC<{ time: string; color: string }> = ({ time, color }) => (
  <span style={{ position: "absolute", left: px(77), top: px(24.5), fontFamily: ROBOTO, fontWeight: 500, fontSize: px(31), lineHeight: 1, color, letterSpacing: "0.01em" }}>{time}</span>
);
const Bars: React.FC<{ mode: BarMode; time: string }> = ({ mode, time }) => {
  if (mode === "none") return null;
  if (mode === "home") return (<><div style={{ position: "absolute", left: px(64), top: 0, width: px(92), height: px(80), background: "#010101" }} /><ClockText time={time} color="#EDEDED" /></>);
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
  const app = splash ? ez(f, a + appAt, a + appAt + 10) : ez(f, a + 4, a + 12);
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
      <div style={{ position: "absolute", left: px(105), top: px(102), fontSize: px(31), fontWeight: 500, color: "#1F1F1F", whiteSpace: "nowrap" }}>Unknown person at home</div>
      <div style={{ position: "absolute", left: px(105), top: px(156), width: px(505), fontSize: px(26), lineHeight: `${px(40)}px`, color: "#444746" }}>
        Someone the camera does not know came in. The alarm is on.</div>
    </div>
  );
};

/* ------------------------------------------------------------------ 1: the app, the face */
const PERSON_TAPS = { add: [2.398, 249, 90], pick: [4.367, 201, 525.6], face: [6.531, 201, 455.3], name: [9.623, 201, 463.8], save: [11.517, 201, 662.5],
  scen: [14.336, 201, 537.3], text: [16.205, 201, 320], saveScen: [21.357, 201, 436], done: [30.661, 201, 607.7] } as const;   // add-person.marks.json
// the selfie videos (576 x 1024) cover the screen; the 8 views were cut at these seconds (video/public/phone/person/faces.json)
const SEL_K = SCR_H / 1024, SEL_W = 576 * SEL_K, SEL_X = (SCR_W - SEL_W) / 2;
const SEL_A = 96, SEL_RATE = 2.5;                       // selfie A 0-8 s, then selfie B 1-6 s, both at 2.5x
const VIEW_AT = [0.2, 2.5, 4.5, 5.0, 7.5].map((t) => T.face + Math.round((t / SEL_RATE) * 30))
  .concat([1.5, 3.0, 5.5].map((t) => T.face + SEL_A + Math.round(((t - 1.0) / SEL_RATE) * 30)));
const FACE_ON_SCREEN = { x: SEL_X + 150 * SEL_K, y: 190 * SEL_K, s: 290 * SEL_K };   // where the face sits in the selfie frame
const S4_END = Math.round(s4Src(35.8)) - 2;
const tapF = (f: number, t: readonly [number, number, number]) => ({ f, x: t[1] * 3, y: t[2] * 3 + REC_Y, press: true });
const rest = (w: Way, df: number, dx: number, dy: number): Way => ({ f: w.f + df, x: w.x + dx, y: w.y + dy });
const WAYS_A: Way[] = (() => {
  const s1 = (t: readonly [number, number, number]) => tapF(Math.round(at(1.38, T.s1, 1.25, t[0])), t);
  const s3 = (t: readonly [number, number, number]) => tapF(Math.round(at(7.44, T.s3, 1.4, t[0])), t);
  const s4 = (t: readonly [number, number, number]) => tapF(Math.round(s4Src(t[0])), t);
  const name = s3(PERSON_TAPS.name), text = s4(PERSON_TAPS.text);
  return [{ f: 54, x: 860, y: 2050 }, { f: T.tapIcon, x: ICON[0] + ICON[2] / 2, y: ICON[1] + ICON[3] / 2, press: true }, { f: T.s1 + 10, x: 700, y: 1700 },
    s1(PERSON_TAPS.add), s1(PERSON_TAPS.pick), s1(PERSON_TAPS.face), { f: T.s3 + 18, x: 760, y: 2000 },
    name, rest(name, 16, 170, 300), s3(PERSON_TAPS.save),
    s4(PERSON_TAPS.scen), text, rest(text, 20, 220, 520), s4(PERSON_TAPS.saveScen), s4(PERSON_TAPS.done), { f: T.test + 20, x: 760, y: 2100 }];
})();
/** The capture screen drawn over the selfie: an oval guide that fills as the 8 views are taken. */
const FaceGuide: React.FC = () => {
  const f = useCurrentFrame();
  const n = VIEW_AT.filter((a) => f >= a).length;
  const flash = Math.max(0, ...VIEW_AT.map((a) => 1 - Math.abs(f - a) / 3));
  const cx = SCR_W / 2, cy = 880, rx = 390, ry = 500, L = Math.PI * (3 * (rx + ry) - Math.sqrt((3 * rx + ry) * (rx + 3 * ry)));
  return (
    <>
      <svg width={SCR_W} height={SCR_H} style={{ position: "absolute", inset: 0 }}>
        <defs><mask id="oval"><rect width={SCR_W} height={SCR_H} fill="white" /><ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="black" /></mask></defs>
        <rect width={SCR_W} height={SCR_H} fill="rgba(0,0,0,0.38)" mask="url(#oval)" />
        <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth={8} />
        <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="none" stroke="#2ABE9E" strokeWidth={14} strokeLinecap="round" strokeDasharray={L} strokeDashoffset={L * (1 - n / 8)}
          transform={`rotate(-90 ${cx} ${cy})`} />
      </svg>
      <div style={{ position: "absolute", left: 0, width: SCR_W, top: 1470, textAlign: "center", fontFamily: ROBOTO, color: "#fff" }}>
        <div style={{ fontSize: 64, fontWeight: 500 }}>{n} of 8</div>
        <div style={{ fontSize: 46, opacity: 0.85, marginTop: 14 }}>Turn your head slowly</div>
      </div>
      <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.35 }} />
    </>
  );
};
const ScreenA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {f < T.s1 + 12 ? <Home /> : null}
      {f < T.face + 2 ? <Grow at={T.grow} from={ICON} r0={40}><Sequence from={T.s1} layout="none"><Rec src="app/add-person.mp4" from={1.38} rate={1.25} /></Sequence></Grow> : null}
      {f >= T.face && f < T.s3 ? (
        <>
          <Sequence from={T.face} durationInFrames={SEL_A} layout="none"><Rec src="phone/person/selfie-a.mp4" from={0} rate={SEL_RATE} w={SEL_W} h={SCR_H} top={0} left={SEL_X} /></Sequence>
          <Sequence from={T.face + SEL_A} durationInFrames={T.s3 - T.face - SEL_A} layout="none"><Rec src="phone/person/selfie-b.mp4" from={1.0} rate={SEL_RATE} w={SEL_W} h={SCR_H} top={0} left={SEL_X} /></Sequence>
          <FaceGuide />
        </>) : null}
      {f >= T.s3 && f < T.s4 ? <Sequence from={T.s3} layout="none"><Rec src="app/add-person.mp4" from={7.44} rate={1.4} /></Sequence> : null}
      <EmptySlots />
      {f >= T.s4 && f < T.s4b ? <Sequence from={T.s4} layout="none"><Rec src="app/add-person.mp4" from={11.8} rate={1.5} /></Sequence> : null}
      {f >= T.s4b && f < T.s4c ? <Sequence from={T.s4b} layout="none"><Rec src="app/add-person.mp4" from={21.6} rate={4} /></Sequence> : null}
      {f >= T.s4c && f < S4_END ? <Sequence from={T.s4c} layout="none"><Rec src="app/add-person.mp4" from={27.2} rate={1.5} /></Sequence> : null}
      <Cursor ways={WAYS_A} show={[54, T.test + 4]} hide={[[T.grow - 2, T.s1 + 10], [T.face - 1, T.s3 + 18]]} />
    </AbsoluteFill>
  );
};
const GRID: Rect = { x: 150, y: 420, w: 844, h: 472 };
const slot = (j: number): Rect => ({ x: GRID.x + 24 + (j % 4) * 202, y: GRID.y + 56 + Math.floor(j / 4) * 202, w: 190, h: 190 });
const r4 = (r: { x: number; y: number }, w: number, h: number): Rect => ({ x: r.x, y: r.y, w: w * KS * OVER, h: h * KS * OVER });
const FACE_SRC = r4(scr(CX.right, FACE_ON_SCREEN.x, FACE_ON_SCREEN.y), FACE_ON_SCREEN.s, FACE_ON_SCREEN.s);
const APP_SLOTS: [number, number, number, number][] = [[116, 618, 228, 231], [364, 618, 230, 231], [612, 618, 230, 231], [861, 618, 231, 231],
  [114, 867, 230, 231], [364, 867, 230, 231], [613, 867, 229, 231], [862, 867, 230, 231]];   // measured on add-person at 8.3 s
const BACK = (j: number) => T.s3 + 2 + 2 * j;
const BACK_LEN = 16;
const FaceCard: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.face + 4 || f > BACK(7) + BACK_LEN + 2) return null;
  const inU = ez(f, T.face + 4, T.face + 20, theme.ease.out);
  const frameOut = ez(f, BACK(5), BACK(7) + 10);
  const views = VIEW_AT.map((a, i) => ({ src: `phone/person/face-view-${i + 1}.jpg`, at: a + 1, j: i }));
  const landed = views.filter((v) => f >= v.at + 14).length;
  return (
    <>
      <div style={{ position: "absolute", left: GRID.x, top: GRID.y, width: GRID.w, height: GRID.h, transform: `translateY(${(1 - inU) * 30}px) scale(${1 - 0.04 * frameOut})`,
        transformOrigin: "50% 50%", opacity: inU * (1 - frameOut), borderRadius: 26, background: "#FFFFFF", boxShadow: "0 30px 70px -30px rgba(70,50,25,0.35), 0 0 0 1px rgba(30,25,15,0.05)" }}>
        <div style={{ position: "absolute", left: 24, top: 16, right: 24, display: "flex", justifyContent: "space-between", fontFamily: SANS, fontSize: 22 }}>
          <span style={{ color: INK, fontWeight: 600 }}>Pessoa</span><span style={{ color: "#7A756C" }}>{landed} de 8 vistas da cara</span></div>
        {Array.from({ length: 8 }, (_, j) => <div key={j} style={{ position: "absolute", left: slot(j).x - GRID.x, top: slot(j).y - GRID.y, width: 190, height: 190, borderRadius: 95, background: "#EEEAE2" }} />)}
      </div>
      {views.map((p) => {
        if (f < p.at) return null;
        const back = BACK(p.j);
        if (f >= back + BACK_LEN) return null;
        const app = APP_SLOTS[p.j], to = r4(scr(CX.right, app[0], app[1] + REC_Y), app[2], app[3]);
        const q = f < p.at + 14 ? lerpRect(FACE_SRC, slot(p.j), ez(f, p.at, p.at + 14, theme.ease.out)) : f < back ? slot(p.j) : lerpRect(slot(p.j), to, ez(f, back, back + BACK_LEN));
        const flying = f < p.at + 14 || f >= back;
        return <Img key={p.j} src={staticFile(p.src)} style={{ position: "absolute", left: q.x, top: q.y, width: q.w, height: q.h, objectFit: "cover", borderRadius: "50%",
          boxShadow: flying ? "0 24px 50px -18px rgba(40,30,15,0.5)" : undefined }} />;
      })}
    </>
  );
};
const EmptySlots: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.s3 || f >= BACK(7) + BACK_LEN) return null;
  return <>{APP_SLOTS.map(([x, y, w, h], j) => f < BACK(j) + BACK_LEN ? <div key={j} style={{ position: "absolute", left: x, top: y + REC_Y, width: w, height: h, borderRadius: "50%", background: "#D9E1EE" }} /> : null)}</>;
};

/* ------------------------------------------------------------------ 3: the lab */
const AP = [0.66, 0.705, 0.693, 0.732];
const ALARM = [0.3135, 0.3023, 0.3243, 0.3115];
const CABIN = [0.645, 0.41, 0.745, 0.69];               // the person seated in the glass cabin (OWLv2 at 5 s, padded): blurred
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
const GRAB1 = 22.0, GRAB2 = 64.6;                        // each takes the book (take seconds; the book is put back in between)
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
  const t = takeT(f);
  const ringing = f >= ALARM_ON;
  const beep = ringing ? beepAt((f - ALARM_ON) / 30) : 0;
  let person: number[] | null = null;
  if (det) {
    const cab = (b: number[]) => (b[0] + b[2]) / 2 > CABIN[0] && (b[0] + b[2]) / 2 < CABIN[2] && (b[1] + b[3]) / 2 > CABIN[1] && (b[1] + b[3]) / 2 < CABIN[3];
    const s = det.frames.map((x) => ({ t: x.t, b: x.boxes.filter((y) => y.label === "a person" && y.score >= 0.15 && !cab(y.box)).sort((p, q) => q.score - p.score)[0] })).filter((x) => x.b);
    const a = [...s].reverse().find((x) => x.t <= t), c = s.find((x) => x.t >= t);
    if (a && c && c.t - a.t < 1.2) { const u = c.t > a.t ? (t - a.t) / (c.t - a.t) : 0; person = a.b.box.map((v, i) => v + (c.b.box[i] - v) * u); }
  }
  const second = f >= T.cut;
  const known = !second && f >= T.f1 + 66, stranger = second && f >= T.f2 + 66;
  const pLabel = known ? (t >= GRAB1 ? "Filipe · com o livro" : "Filipe · reconhecido") : stranger ? (t >= GRAB2 ? "desconhecido · com o livro" : "desconhecido") : undefined;
  const pColor = known ? KIND.ok : stranger ? KIND.alarm : KIND.person;
  const ax = (ALARM[0] + ALARM[2]) / 2 * 1920, ay = (ALARM[1] + ALARM[3]) / 2 * 1080;
  const chip = ringing ? ["Uma pessoa desconhecida entrou · alarme e mensagem", KIND.alarm, "#fff"] : known ? ["Filipe é de casa · nada toca", KIND.ok, "#fff"]
    : ["Cenário ativo · Unknown person at home", "rgba(255,255,255,0.94)", INK];
  const cb = { x: CABIN[0] * 1920, y: CABIN[1] * 1080, w: (CABIN[2] - CABIN[0]) * 1920, h: (CABIN[3] - CABIN[1]) * 1080 };
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, background: "#000" }}>
      <Picture f={f} />
      {/* the person in the glass cabin, blurred (AGENTS.md rule 6) */}
      <div style={{ position: "absolute", left: cb.x, top: cb.y, width: cb.w, height: cb.h, overflow: "hidden", borderRadius: 18 }}>
        <div style={{ position: "absolute", left: -cb.x, top: -cb.y, width: 1920, height: 1080, filter: "blur(16px)" }}><Picture f={f} /></div>
      </div>
      <AbsoluteFill style={{ background: "rgba(229,50,45,0.035)", opacity: beep }} />
      <AbsoluteFill style={{ opacity: ov }}>
      {ringing ? <div style={{ position: "absolute", left: ax, top: ay, width: 96, height: 96, transform: "translate(-50%,-50%)", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(255,90,80,0.7) 0%, rgba(255,60,50,0.25) 38%, rgba(255,40,40,0) 70%)", opacity: 0.15 + 0.5 * beep }} /> : null}
      {person ? <Box b={person} kind="person" text={pLabel} color={pColor} dark={!pLabel} /> : null}
      <Box b={AP} kind="device" text="ponto de acesso" color={KIND.device} brackets={false} />
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
const Compare: React.FC<{ a: number; match: boolean }> = ({ a, match }) => {
  const f = useCurrentFrame();
  if (f < a + 16 || f > a + 100) return null;
  const inU = ez(f, a + 16, a + 30, theme.ease.out), outU = ez(f, a + 88, a + 100, theme.ease.in);
  const scan = interpolate(f, [a + 30, a + 58], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const verdict = ez(f, a + 62, a + 72, theme.ease.out);
  const col = match ? KIND.ok : KIND.alarm;
  const Tile: React.FC<{ src: string; label: string; x: number }> = ({ src, label, x }) => (
    <div style={{ position: "absolute", left: x, top: 0, width: 300 }}>
      <div style={{ position: "relative", width: 300, height: 300, borderRadius: 26, overflow: "hidden", boxShadow: `0 0 0 ${4 * verdict}px ${col}, 0 30px 70px -26px rgba(0,0,0,0.6)` }}>
        <Img src={staticFile(src)} style={{ width: 300, height: 300, objectFit: "cover" }} />
        {scan > 0 && scan < 1 ? <div style={{ position: "absolute", left: 0, right: 0, top: `${scan * 100}%`, height: 3, background: "#7CF5D8", boxShadow: "0 0 18px 6px rgba(124,245,216,0.55)" }} /> : null}
      </div>
      <div style={{ marginTop: 14, fontFamily: SANS, fontSize: 22, fontWeight: 600, color: "#fff", textAlign: "center", textShadow: "0 2px 10px rgba(0,0,0,0.6)" }}>{label}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 1090, top: 300, width: 680, height: 470, opacity: inU * (1 - outU), transform: `translateX(${(1 - inU) * 40}px)` }}>
      <Tile src={match ? "phone/person/cam-face-filipe.jpg" : "phone/person/cam-face-stranger.jpg"} label="Câmara, agora" x={0} />
      <Tile src="phone/person/face-view-1.jpg" label="Filipe, registado" x={360} />
      <div style={{ position: "absolute", left: 300, top: 120, width: 60, height: 60, display: "grid", placeItems: "center", opacity: verdict, transform: `scale(${0.6 + 0.4 * verdict})` }}>
        <div style={{ width: 56, height: 56, borderRadius: 28, background: col, display: "grid", placeItems: "center", boxShadow: "0 8px 24px -8px rgba(0,0,0,0.6)" }}>
          <svg width={30} height={30} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round">
            {match ? <path d="m5.5 12.5 4.2 4.2 8.8-9.4" /> : <path d="M6 6l12 12M18 6 6 18" />}</svg></div>
      </div>
      <div style={{ position: "absolute", left: 0, width: 660, top: 372, textAlign: "center", opacity: verdict }}>
        <span style={{ display: "inline-block", padding: "10px 20px", borderRadius: 999, background: col, color: "#fff", fontFamily: SANS, fontSize: 26, fontWeight: 600 }}>
          {match ? "É o Filipe · é de casa" : "Não é ninguém de casa"}</span>
      </div>
      <div style={{ position: "absolute", left: 0, width: 660, top: 432, textAlign: "center", fontFamily: SANS, fontSize: 17, color: "rgba(255,255,255,0.75)" }}>comparação ilustrativa</div>
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
          <LabLayer ov={1 - z.u} />   {/* the detector's labels step back while the camera is on a face */}
        </div>
        <AbsoluteFill style={{ background: "rgba(0,0,0,0.35)", opacity: z.u }} />
        <Compare a={T.f1} match />
        <Compare a={T.f2} match={false} />
        <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.7 }} />
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ 3: the phone over the lab */
const ALERT_OPEN = 3.23;
/** The alert opening (its recording stops 0,3 s after the page is up), then its last frame held. */
const AlertRec: React.FC = () => {
  const f = useCurrentFrame();
  return f < T.tap + 10 ? <Sequence from={T.tap + 2} layout="none"><Rec src="app/alert-person-open.mp4" from={ALERT_OPEN} /></Sequence>
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

/* ------------------------------------------------------------------ the local models at work (bottom right) */
// What really ran: Qwen3-1.7B compiled the sentence (/api/rules); OWLv2 found the people in the take (detect_take.py).
const MODELS = [
  { from: Math.round(s4Src(21.36)), until: Math.round(s4Src(27.38)), name: "Qwen3-1.7B", what: "a frase passa a cenário" },
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
const SERIF_LINES: [string, number][] = [["Abre-se a app.", 44], ["Adiciona-se uma pessoa.", 150], ["Grava-se a cara, a rodar.", T.face], ["Dá-se-lhe um nome.", T.s3 + 30],
  ["E uma frase cria o cenário.", T.s4 + 40], ["Vamos testar?", T.test + 10], ["O Filipe entrou, e nada tocou.", T.close + 16], ["Um desconhecido entrou, e o alarme tocou.", T.close + 44]];
const WORD_KEYS = SERIF_LINES.flatMap(([text, from]) => text.split(" ").map((_, k) => from + 4 + 3 * k));
const SENTENCE = "Sound the alarm if someone I don't know comes in";
const typedAt = (start: number, n: number, step: number) => Array.from({ length: n }, (_, i) => start + i * step);
const APP_KEYS = [
  ...typedAt(PERSON_TAPS.name[0] + 0.26, 6, 0.0725).map((t) => Math.round(at(7.44, T.s3, 1.4, t))),
  ...typedAt(16.4, SENTENCE.length, (20.173 - 16.4) / SENTENCE.length).map((t) => Math.round(s4Src(t))),
];

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
        {f < T.test + 30 ? <PhoneAt cx={cxA} bars={{ time: "16:21", mode: f < T.grow + 10 ? "home" : f < T.s1 ? "splash" : f >= T.face && f < T.s3 ? "none" : "app" }}><ScreenA /></PhoneAt> : null}
        <Line text="Abre-se a app." from={44} to={150} />
        <Line text="Adiciona-se uma pessoa." from={150} to={T.face} />
        <Line text="Grava-se a cara, a rodar." from={T.face} to={T.s3 + 4} top={300} />
        <FaceCard />
        <Line text="Dá-se-lhe um nome." from={T.s3 + 30} to={T.s4} />
        <Line text="E uma frase cria o cenário." from={T.s4 + 40} to={T.test + 6} />
        <Line text="Vamos testar?" from={T.test + 10} to={T.lab + 14} top={360} left={0} width={1920} align="center" size={104} />
      </AbsoluteFill>
      <LabFrame />
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f >= T.phoneIn && f < LAB_OUT + 20 ? <PhoneAt cx={cxC2} shadow={1} bars={{ time: "16:26", mode: f < T.tap + 10 ? "home" : "app" }}><ScreenC /></PhoneAt> : null}
      </AbsoluteFill>
      {/* the close: calm, on the page */}
      {f >= T.close && f < T.end + 2 ? (
        <AbsoluteFill style={{ background: PAPER, opacity: closeIn * (1 - endIn) }}>
          <Line text="O Filipe entrou, e nada tocou." from={T.close + 16} to={T.end + 2} top={400} left={0} width={1920} align="center" size={72} />
          <Line text="Um desconhecido entrou, e o alarme tocou." from={T.close + 44} to={T.end + 2} top={500} left={0} width={1920} align="center" size={72} />
        </AbsoluteFill>) : null}
      {f >= T.end ? <Sequence from={T.end} layout="none"><EndCard bg={PAPER} /></Sequence> : null}
      <ModelsCard />
      <Grain />
      {/* sound: as example 1 (the song; the team's whooshes as they are; taps; typing), plus the face scenes' shutter, scan,
          match and mismatch; the alarm a beat after the stranger's face fails to match; the buzz */}
      <Audio src={staticFile("audio/music/bed-real-long.wav")} volume={(v) => 0.5 * interpolate(v, [0, 20, T.lab, T.lab + 30, ALARM_ON - 10, ALARM_ON, T.close, T.close + 20, T.end, T.end + 20, SCENE2_FRAMES - 16, SCENE2_FRAMES],
        [0, 1, 1, 0.85, 0.85, 0.5, 0.5, 1.1, 1.1, 1.3, 1.3, 0], clamp)} />
      {[[209, "zoom-soft", 0.9], [443, "zoom-soft", 0.9], [586, "zoom-soft", 0.9], [T.notice + 13, "zoom-soft", 0.9], [T.f1 + 14, "zoom-soft", 0.9], [T.f2 + 14, "zoom-soft", 0.9],
        [T.glide + 18, "slow-gentle", 0.32], [T.test + 12, "fast", 0.08], [T.phoneIn + 4, "slow-gentle", 0.32], [T.aside + 15, "slow-gentle", 0.28], [LAB_OUT + 4, "fast", 0.07],
        [T.s3 + 12, "fast", 0.07], [T.lab + 11, "riser-soft", 0.15], [T.close + 8, "riser-soft", 0.12],
        [T.end + 6, "riser-soft", 0.15], [T.end + 23, "slow-gentle", 0.28], [T.end + 68, "zoom-soft", 0.6],
        ...VIEW_AT.map((a) => [a + 5, "throw", 0.07] as const)].map(([peak, n, vol], i) => {
        const PEAK: Record<string, number> = { "slow-gentle": 0.28, "zoom-soft": 0.37, throw: 0.07, fast: 0.15, "riser-soft": 0.43 };
        return <Sequence key={`w${i}`} from={Math.round((peak as number) - PEAK[n as string] * 30)} layout="none"><Audio src={staticFile(`audio/sfx/whoosh/${n}.wav`)} volume={vol as number} /></Sequence>;
      })}
      {WAYS_A.filter((w) => w.press).map(tap1).concat([T.tap]).map((a, i) => (
        <Sequence key={`t${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.13} /></Sequence>))}
      {VIEW_AT.map((a, i) => <Sequence key={`v${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/v4/shutter-${i % 2 ? 3 : 2}.wav`)} volume={0.2} /></Sequence>)}
      {[T.f1, T.f2].map((a, i) => <Sequence key={`c${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/shutter-2.wav")} volume={0.32} /></Sequence>)}
      {[T.f1, T.f2].map((a, i) => <Sequence key={`sc${i}`} from={a + 30} layout="none"><Audio src={staticFile("audio/sfx/ui/scan.wav")} volume={0.5} /></Sequence>)}
      <Sequence from={T.f1 + 62 - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.42} /></Sequence>
      <Sequence from={T.f2 + 62 - 2} layout="none"><Audio src={staticFile("audio/sfx/ui/wrong.wav")} volume={0.9} /></Sequence>
      <Sequence from={Math.round(s4Src(27.376)) - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.35} /></Sequence>
      <Sequence from={ALARM_ON} durationInFrames={LAB_OUT + 16 - ALARM_ON} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} loop
        volume={(v) => { const g = ALARM_ON + v; return (g < T.phoneIn ? 0.5 : g < T.aside ? 0.22 : 0.36) * (1 - ez(g, LAB_OUT - 4, LAB_OUT + 16)); }} /></Sequence>
      <Sequence from={T.notice} layout="none"><Audio src={staticFile("audio/sfx/scene1/buzz.wav")} volume={0.5} /></Sequence>
      {WORD_KEYS.map((a, i) => <Sequence key={`kw${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 7) % 12) + 1}.wav`)} volume={0.22} /></Sequence>)}
      {APP_KEYS.map((a, i) => <Sequence key={`ka${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 5) % 12) + 1}.wav`)} volume={0.15} /></Sequence>)}
    </AbsoluteFill>
  );
};
