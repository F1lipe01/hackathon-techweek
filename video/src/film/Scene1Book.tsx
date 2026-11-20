// Real example 1, the book left behind (the lab, 19 Nov). The style (video/research/): a light page, a phone that glides
// while the lines stream in beside it, the camera always drifting and diving into the one thing that matters, real
// screens only.
//   1  the phone, centred, glides right; the Altice app opens with its real loading (screen recording of the team's
//      phone); Things › Add › Book › Take photos: 8 shutter presses, each photo flying into a card; the
//      card flies back into the app; name; Save; a scenario in one sentence; Save; Done (record_app.mjs add-book)
//   2  "Vamos testar?", and the lab camera opens out of the page
//   3  one take, in one go (book-full, 19 Nov 15:59:53): he leaves without the book, the door shuts, the alarm sounds;
//      the phone glides in: the notification, the alert; it moves aside, the lab fills the page, "Turn off the alarm",
//      the alarm stops; a cut to his return: he takes the book and leaves; a green close.
// A camera readout in the corner gives the time since the take began and the clock time (the camera's own clock).
// The alarm and the notification are simulated (AGENTS.md rule 1).
// After Save the app asks who the book belongs to (link-person, recorded with record_app.mjs: the same book,
// the same 8 photos): "Link to Mushahid?", Yes, "Belongs to Mushahid"; then a page cut to the scenario. In the lab the
// book is "o livro do Mushahid" (the thing's owner, as the app holds it); the man in the take is never named.
import React from "react";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, interpolateColors, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import { loadFont as loadRoboto } from "@remotion/google-fonts/Roboto";
import { loadFont as loadMono } from "@remotion/google-fonts/RobotoMono";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Brackets, Phone, SCREEN, clamp, phoneWidth } from "../presentation/ui";
import { S23 as EndCard } from "../presentation/shots/End";

export const { fontFamily: SERIF } = loadFont("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });
export const { fontFamily: ROBOTO } = loadRoboto("normal", { weights: ["400", "500", "700"], subsets: ["latin"] });
export const { fontFamily: MONO } = loadMono("normal", { weights: ["500"], subsets: ["latin"] });
export const SANS = theme.fonts.display;
export const PAPER = "#F3F0EA", INK = "#1E1D1A", ACCENT = "#1C9A7E";
export const ez = (f: number, a: number, b: number, e = theme.ease.inOut) => interpolate(f, [a, b], [0, 1], { ...clamp, easing: e });
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
type Rect = { x: number; y: number; w: number; h: number };
const lerpRect = (a: Rect, b: Rect, u: number): Rect => ({ x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u), w: lerp(a.w, b.w, u), h: lerp(a.h, b.h, u) });

/* ------------------------------------------------------------------ the timeline (30 fps) */
const LINK = 130;                                  // link-person on screen from T.s4: added, who it belongs to, linked
const D = LINK - 58;                               // everything after it comes this much later than in v12
const T = {
  glide: 30, tapIcon: 80, grow: 82, s1: 118,      // the app opens; add-book from 1.38 s at 1.25×
  cam: 246,                                        // the colleague's viewfinder, 8 shutter presses
  s3: 380,                                         // add-book from 7.44 s at 1.4×: the photos, the name
  s4: 514,                                         // link-person (from its Save, 27.43 s, at 1.4×): added, "Link to Mushahid?", Yes, "Belongs to Mushahid"
  s5: 514 + LINK,                                  // add-book from 16.6 s at 1.5×: the scenario, saved, Done
  test: 866 + D, lab: 956 + D,                     // "Vamos testar?" (held 3 s); the lab opens out of the page
  phoneIn: 1342 + D, notice: 1370 + D, tap: 1434 + D, aside: 1454 + D, cut: 1580 + D,
  success: 1946 + D, end: 2070 + D,
};
const S5 = T.s4 + D;                               // add-book's clock for its part after the link: frame = at(13.7, S5, 1.5, t)
export const SCENE1_FRAMES = T.end + 120;   // the end card: the mark lands, the name is carried out of it, then "by Altice Labs"
const at = (s0: number, f0: number, rate: number, t: number) => f0 + ((t - s0) / rate) * 30;

/* ------------------------------------------------------------------ the take (book-full: one go) */
const TAKE = "takes/scene1/book-full.mp4";
const CLOCK0 = 15 * 3600 + 59 * 60 + 53.7;              // the camera's clock at the take's first frame
const A0 = 5.5, B0 = 27.8;                               // take seconds at T.lab and at T.cut
const takeT = (f: number) => (f < T.cut ? A0 + (f - T.lab) / 30 : B0 + (f - T.cut) / 30);
const DOOR_OPEN: [number, number][] = [[10.4, 11.9], [28.2, 31.3], [38.8, 39.9]];
const CLOSE = T.lab + Math.round((11.9 - A0) * 30);     // the door shuts behind him, the book on the desk
const ALARM_ON = CLOSE + 150;                            // the rule waits 5 s after the door shuts
const GRAB = 34.3;                                        // he lifts the book (take seconds)
const ALERT_OPEN = 3.23;                                  // alert-book-open: the alert page is up
const ALARM_OFF_T = 6.54;                                 // alert-book-open: "Turn off the alarm" pressed
const ALARM_OFF = T.tap + 2 + Math.round((ALARM_OFF_T - ALERT_OPEN) * 30);

/* ------------------------------------------------------------------ the page, the camera, the phone */
// The team's phone (an Android phone, screen 720 × 1600 = 9:20), drawn here: a thin even bezel, a punch-hole camera,
// and its real status and navigation bars (cut from its screenshot) fixed above whatever the screen shows. The screen
// is drawn in content px: 1206 × 2680 (the screenshots × 1206/720). The app recordings (1206 × 2622, their iPhone status
// row and home bar hidden by record_app.mjs) sit REC_Y higher, so the app starts right under the real status bar.
export const SCR_W = 1206, SCR_H = 2680, PK = SCR_W / 720;
export const px = (x: number) => x * PK, py = (y: number) => y * PK;
export const SB_H = py(84), NAV_Y = py(1504);                  // the status bar's height and the navigation bar's top, measured on the screenshot
export const REC_Y = -21;
export const PH = 900, BEZ = 9, SHC = PH - 2 * BEZ, KS = SHC / SCR_H, SWC = SCR_W * KS, PW = SWC + 2 * BEZ;
export const phoneBox = (cx: number) => ({ x: cx - PW / 2, y: 540 - PH / 2 });
export const OVER = 1.01;   // the screen's content is drawn 1 % larger, centred, so no edge shows while the phone moves
export const scr = (cx: number, sx: number, sy: number) => ({ x: phoneBox(cx).x + BEZ + KS * (OVER * sx - ((OVER - 1) / 2) * SCR_W),
  y: phoneBox(cx).y + BEZ + KS * (OVER * sy - ((OVER - 1) / 2) * SCR_H) });
export const CX = { centre: 960, right: 1370, left: 560, cRight: 1300 };
type CK = { at: number; s: number; x: number; y: number };
const H0 = { s: 1, x: 960, y: 540 };
const WHO = scr(CX.right, 603, 1000 + REC_Y);   // link-person: "Belongs to Mushahid", the book and his face, the suggestion
const BTN = scr(CX.right, 603, 1366 + REC_Y), FIELDS = scr(CX.right, 603, 1560 + REC_Y), TXT = scr(CX.right, 603, 1000 + REC_Y), NOTE = scr(CX.cRight, 603, SB_H + 14 + px(273) / 2);
const CAM: CK[] = [
  { at: 0, ...H0 }, { at: 196, ...H0 }, { at: 222, s: 2.0, ...BTN }, { at: 246, s: 2.0, ...BTN }, { at: 270, ...H0 },
  { at: 414, ...H0 }, { at: 434, s: 1.9, ...FIELDS }, { at: 484, s: 1.9, ...FIELDS }, { at: 502, ...H0 },
  { at: T.s4 + 62, ...H0 }, { at: T.s4 + 80, s: 1.9, ...WHO }, { at: T.s5 - 14, s: 1.9, ...WHO }, { at: T.s5 + 4, ...H0 },
  { at: 586 + D, ...H0 }, { at: 606 + D, s: 2.4, ...TXT }, { at: 712 + D, s: 2.4, ...TXT }, { at: 730 + D, ...H0 },
  { at: 1372 + D, ...H0 }, { at: 1394 + D, s: 1.7, ...NOTE }, { at: 1424 + D, s: 1.7, ...NOTE }, { at: 1446 + D, ...H0 },
];
/** The camera: eased moves between keys that come to rest (the phone and the text stay still between moves). */
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1].at) i++;
  const a = CAM[i], b = CAM[i + 1], u = ez(f, a.at, b.at);
  return { s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), u)), x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) };
};
const camCss = (f: number) => { const c = camAt(f); return `translate(960px,540px) scale(${c.s}) translate(${-c.x}px,${-c.y}px)`; };
export const Grain: React.FC = () => (
  <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 0.05, mixBlendMode: "multiply", pointerEvents: "none" }}>
    <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter="url(#paper)" />
  </svg>
);
export type BarMode = "home" | "splash" | "app" | "none";
const ClockText: React.FC<{ time: string; color: string }> = ({ time, color }) => (
  <span style={{ position: "absolute", left: px(77), top: px(24.5), fontFamily: ROBOTO, fontWeight: 500, fontSize: px(31), lineHeight: 1, color, letterSpacing: "0.01em" }}>{time}</span>
);
/** The phone's own bars, above everything on its screen: on the home screen the screenshot's (only the clock changes);
 *  over the app (or its loading) the real glyphs in dark, the way Android draws them on a light app. */
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
/** The phone at a centre x: a dark body with a thin even bezel, side buttons, the screen and its punch-hole camera. */
export const PhoneAt: React.FC<{ cx: number; shadow?: number; bars: { mode: BarMode; time: string }; children: React.ReactNode }> = ({ cx, shadow = 0, bars, children }) => {
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
export const Rec: React.FC<{ src: string; from: number; rate?: number; w?: number; h?: number; top?: number }> = ({ src, from, rate = 1, w = SCR_W, h = 2622, top = REC_Y }) => (
  <OffthreadVideo src={staticFile(src)} muted trimBefore={Math.round(from * 30)} playbackRate={rate} style={{ position: "absolute", left: (SCR_W - w) / 2, top, width: w, height: h }} />
);
/** A serif line streamed word by word: each new word arrives in the accent and settles into ink. */
const Line: React.FC<{ text: string; from: number; to: number; top?: number; left?: number; size?: number; align?: "left" | "center"; width?: number; color?: string }> = ({ text, from, to, top = 400, left = 150, size = 84, align = "left", width = 900, color = INK }) => {   // the team: bigger headlines (84 px, was 62)
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const dive = Math.max(0, Math.min(1, (camAt(f).s - 1.03) / 0.25));   // a line steps aside while the camera dives into the phone
  const fade = interpolate(f, [to - 10, to], [1, 0], clamp) * (1 - dive);
  return (
    <div style={{ position: "absolute", left, top, width, opacity: fade, textAlign: align, fontFamily: SERIF, fontSize: size, lineHeight: 1.13, letterSpacing: "-0.015em" }}>
      {text.split(" ").map((w, k) => {
        const a = from + 4 + 3 * k;
        return <span key={k} style={{ opacity: interpolate(f, [a, a + 5], [0, 1], clamp), color: interpolateColors(f, [a, a + 16], [color === INK ? ACCENT : color, color]) }}>{w} </span>;
      })}
    </div>
  );
};

/* ------------------------------------------------------------------ the team's phone: its screenshots and recordings */
const PhoneImg: React.FC<{ src: string }> = ({ src }) => <Img src={staticFile(src)} style={{ position: "absolute", left: 0, top: 0, width: SCR_W, height: SCR_H }} />;
export const Home: React.FC = () => <PhoneImg src="phone/home.jpg" />;
/** One touch mark that glides between the taps like a pointer: it eases into each tap (slowing almost to a stop),
 *  presses, and moves on; between moves it keeps a slight drift so it never quite stops. `hide` lists frame ranges. */
export type Way = { f: number; x: number; y: number; press?: boolean };
export const Cursor: React.FC<{ ways: Way[]; hide?: [number, number][]; show?: [number, number] }> = ({ ways, hide = [], show }) => {
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
const ADD_TAPS = { add: [2.405, 201, 440], pick: [4.405, 201, 525.6], photos: [6.585, 201, 455.3], name: [9.646, 201, 463.8], what: [11.208, 201, 573.5],
  save: [13.459, 201, 772.3], scen: [16.155, 201, 515.7], text: [18.032, 201, 320], saveScen: [24.922, 201, 436], done: [31.205, 201, 607.7] } as const;   // add-book.marks.json
const ALERT_TAP_OFF = [6.54, 201, 596] as const;   // app points; screen y = 3 × y + REC_Y
/** The system's opening: the app's window grows out of what was tapped, under the phone's bars; inside, the Altice
 *  app's real loading (a screen recording of the team's phone), then the app. */
export const Grow: React.FC<{ at: number; from: [number, number, number, number]; r0: number; splash?: boolean; appAt?: number; children?: React.ReactNode }> = ({ at: a, from, r0, splash = true, appAt = 34, children }) => {
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
export const ICON: [number, number, number, number] = [px(390), py(708), px(108), px(108)];   // SmartHome Beta on the home screen
export const CARD: [number, number, number, number] = [px(28), SB_H + 14, px(664), px(273)];   // under the status bar; size measured on the team's phone
/** The notification as the team's phone draws it, measured on a real one with a picture (19 Nov, 720 px wide): a light
 *  card (#F3F3F3, radius 44); the app's round icon (48) at left; "app • time" in grey; the picture (96, radius 10) at
 *  the top right beside the round expand button (48, #CBD6C6); the title (medium) and the whole message below. */
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
      <Img src={staticFile("phone/photos/final-1.jpg")} style={{ position: "absolute", left: px(456), top: px(32), width: px(96), height: px(96), borderRadius: px(10), objectFit: "cover" }} />
      <div style={{ position: "absolute", left: px(584), top: px(32), width: px(48), height: px(48), borderRadius: "50%", background: "#CBD6C6", display: "grid", placeItems: "center" }}>
        <svg width={px(24)} height={px(24)} viewBox="0 0 24 24"><path d="m6 15 6-6 6 6" fill="none" stroke="#1F1F1F" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" /></svg></div>
      <div style={{ position: "absolute", left: px(105), top: px(102), fontSize: px(31), fontWeight: 500, color: "#1F1F1F", whiteSpace: "nowrap" }}>Book left at home</div>
      <div style={{ position: "absolute", left: px(105), top: px(156), width: px(505), fontSize: px(26), lineHeight: `${px(40)}px`, color: "#444746" }}>
        The door closed and your book is still on the desk. The alarm is on.</div>
    </div>
  );
};

/* ------------------------------------------------------------------ 1: the app, the photos */
const SHOT = [1.3, 7.83, 11.17, 16.2, 23.03, 27.27, 31.8, 36.1];   // the colleague's 8 shutter presses
const SEG = 16, BEFORE = 0.35, PRESS = Math.round(BEFORE * 30);
const S4_END = S5 + Math.floor(((36.26 - 13.7) / 1.5) * 30) - 2;   // add-book ends at 36.27 s
const SAVE_F = Math.round(at(7.44, T.s3, 1.4, 13.459));             // Save pressed: link-person takes over from its own Save (27.425 s)
const LINK_SRC = 27.425, LINK_RATE = 1.4;
const LINK_YES = { f: Math.round(at(LINK_SRC, SAVE_F, LINK_RATE, 30.504)), x: 201 * 3, y: 587.6 * 3 + REC_Y, press: true };   // link-person.marks.json
const OWNED = Math.round(at(LINK_SRC, SAVE_F, LINK_RATE, 30.703));   // "Belongs to Mushahid"
const tapF = (s0: number, f0: number, rate: number, t: readonly [number, number, number]) => ({ f: Math.round(at(s0, f0, rate, t[0])), x: t[1] * 3, y: t[2] * 3 + REC_Y, press: true });
const A1 = (t: readonly [number, number, number]) => tapF(1.38, T.s1, 1.25, t), A3 = (t: readonly [number, number, number]) => tapF(7.44, T.s3, 1.4, t), A4 = (t: readonly [number, number, number]) => tapF(13.7, S5, 1.5, t);
const rest = (w: Way, df: number, dx: number, dy: number): Way => ({ f: w.f + df, x: w.x + dx, y: w.y + dy });   // aside, off the text being typed
const WAYS_A: Way[] = (() => {
  const name = A3(ADD_TAPS.name), what = A3(ADD_TAPS.what), text = A4(ADD_TAPS.text);
  return [{ f: 54, x: 860, y: 2050 }, { f: T.tapIcon, x: ICON[0] + ICON[2] / 2, y: ICON[1] + ICON[3] / 2, press: true }, { f: T.s1 + 10, x: 700, y: 1700 },
    A1(ADD_TAPS.add), A1(ADD_TAPS.pick), A1(ADD_TAPS.photos), { f: T.s3 + 16, x: 760, y: 2000 },
    name, rest(name, 16, 170, 300), what, rest(what, 16, 170, 300), A3(ADD_TAPS.save),
    LINK_YES, rest(LINK_YES, 18, 170, 300), text, rest(text, 20, 220, 520), A4(ADD_TAPS.saveScen), A4(ADD_TAPS.done), { f: T.test + 20, x: 760, y: 2100 }];
})();
const ScreenA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {f < T.s1 + 12 ? <Home /> : null}
      {f < T.cam + 2 ? <Grow at={T.grow} from={ICON} r0={40}><Sequence from={T.s1} layout="none"><Rec src="app/add-book.mp4" from={1.38} rate={1.25} /></Sequence></Grow> : null}
      {f >= T.cam && f < T.s3 ? SHOT.map((t, i) => (
        <Sequence key={i} from={T.cam + i * SEG} durationInFrames={i === SHOT.length - 1 ? T.s3 - T.cam - i * SEG : SEG} layout="none">
          <AbsoluteFill style={{ background: "#000" }}><Rec src="footage/phone-photos.mp4" from={t - BEFORE} w={CAM_W} h={SCR_H} top={0} /></AbsoluteFill>
        </Sequence>)) : null}
      {f >= T.s3 && f < SAVE_F + 1 ? <Sequence from={T.s3} layout="none"><Rec src="app/add-book.mp4" from={7.44} rate={1.4} /></Sequence> : null}
      <EmptySlots />
      {f >= SAVE_F && f < T.s5 + 4 ? <Sequence from={SAVE_F} layout="none"><Rec src="app/link-person.mp4" from={LINK_SRC} rate={LINK_RATE} /></Sequence> : null}
      {/* a page cut to the scenario, softened like the app's own page change */}
      {f >= T.s5 - 3 && f < S4_END ? <AbsoluteFill style={{ opacity: ez(f, T.s5 - 3, T.s5 + 3) }}><Sequence from={T.s5 - 3} layout="none">
        <Rec src="app/add-book.mp4" from={16.6 - (3 / 30) * 1.5} rate={1.5} /></Sequence></AbsoluteFill> : null}
      {f >= S4_END ? <Img src={staticFile("phone/add-book-last.png")} style={{ position: "absolute", left: 0, top: REC_Y, width: SCR_W, height: 2622 }} /> : null}
      <Cursor ways={WAYS_A} show={[54, T.test + 4]} hide={[[T.grow - 2, T.s1 + 10], [T.cam - 1, T.s3 + 16]]} />
    </AbsoluteFill>
  );
};
const GRID: Rect = { x: 150, y: 420, w: 844, h: 472 };
const slot = (j: number): Rect => ({ x: GRID.x + 24 + (j % 4) * 202, y: GRID.y + 56 + Math.floor(j / 4) * 202, w: 190, h: 190 });
const r4 = (r: { x: number; y: number }, w: number, h: number): Rect => ({ x: r.x, y: r.y, w: w * KS * OVER, h: h * KS * OVER });
const CAM_W = Math.round((392 * SCR_H) / 850);   // the colleague's camera recording (392 × 850), to cover the screen
const CAM_K = CAM_W / 392, CAM_X = (SCR_W - CAM_W) / 2;
const VIEWFINDER = r4(scr(CX.right, CAM_X + 100 * CAM_K, 125 * CAM_K), 292 * CAM_K, 410 * CAM_K);   // where the photos were cut from its preview
const APP_SLOTS: [number, number, number, number][] = [[114, 618, 231, 232], [362, 618, 232, 232], [612, 618, 231, 232], [861, 618, 231, 232],
  [114, 867, 232, 231], [362, 867, 232, 231], [612, 867, 231, 231], [860, 867, 232, 231]];
const BACK = (j: number) => T.s3 + 2 + 2 * j;            // photo j leaves the card for its slot in the app
const BACK_LEN = 16;
const PhotoCard: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.cam + 4 || f > BACK(7) + BACK_LEN + 2) return null;
  const inU = ez(f, T.cam + 4, T.cam + 20, theme.ease.out);
  const frameOut = ez(f, BACK(5), BACK(7) + 10);          // the card's frame goes once its last photos have lifted off
  const shots = SHOT.map((_, i) => ({ src: `phone/photos/final-${i + 1}.jpg`, at: T.cam + i * SEG + PRESS + 1, j: i }));
  const landed = shots.filter((s) => f >= s.at + 14).length;
  return (
    <>
      <div style={{ position: "absolute", left: GRID.x, top: GRID.y, width: GRID.w, height: GRID.h, transform: `translateY(${(1 - inU) * 30}px) scale(${1 - 0.04 * frameOut})`,
        transformOrigin: "50% 50%", opacity: inU * (1 - frameOut), borderRadius: 26, background: "#FFFFFF", boxShadow: "0 30px 70px -30px rgba(70,50,25,0.35), 0 0 0 1px rgba(30,25,15,0.05)" }}>
        <div style={{ position: "absolute", left: 24, top: 16, right: 24, display: "flex", justifyContent: "space-between", fontFamily: SANS, fontSize: 22 }}>
          <span style={{ color: INK, fontWeight: 600 }}>Book</span><span style={{ color: "#7A756C" }}>{landed} de 8 fotografias</span></div>
        {Array.from({ length: 8 }, (_, j) => <div key={j} style={{ position: "absolute", left: slot(j).x - GRID.x, top: slot(j).y - GRID.y, width: 190, height: 190, borderRadius: 14, background: "#EEEAE2" }} />)}
      </div>
      {shots.map((p) => {
        if (f < p.at) return null;
        const back = BACK(p.j);
        if (f >= back + BACK_LEN) return null;                 // landed: the app's own thumbnail is now showing
        const app = APP_SLOTS[p.j], to = r4(scr(CX.right, app[0], app[1] + REC_Y), app[2], app[3]);
        const q = f < p.at + 14 ? lerpRect(VIEWFINDER, slot(p.j), ez(f, p.at, p.at + 14, theme.ease.out)) : f < back ? slot(p.j) : lerpRect(slot(p.j), to, ez(f, back, back + BACK_LEN));
        const flying = f < p.at + 14 || f >= back;
        return <Img key={p.j} src={staticFile(p.src)} style={{ position: "absolute", left: q.x, top: q.y, width: q.w, height: q.h, objectFit: "cover",
          borderRadius: f >= back ? lerp(14, 8, ez(f, back, back + BACK_LEN)) : f < p.at + 14 ? lerp(24, 14, ez(f, p.at, p.at + 14)) : 14,
          boxShadow: flying ? "0 24px 50px -18px rgba(40,30,15,0.5)" : undefined }} />;
      })}
    </>
  );
};
/** On the app's page, the slots stay empty until each photo lands in its own (the real thumbnails sit underneath). */
const EmptySlots: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.s3 || f >= BACK(7) + BACK_LEN) return null;
  return <>{APP_SLOTS.map(([x, y, w, h], j) => f < BACK(j) + BACK_LEN ? <div key={j} style={{ position: "absolute", left: x, top: y + REC_Y, width: w, height: h, borderRadius: 24, background: "#D9E1EE" }} /> : null)}</>;
};

/* ------------------------------------------------------------------ 3: the lab (one take) */
const AP = [0.66, 0.705, 0.693, 0.732];
const ALARM = [0.3135, 0.3023, 0.3243, 0.3115];
const DOOR: [number, number][] = [[0.339, 0.268], [0.435, 0.289], [0.414, 0.651], [0.321, 0.637]];
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
const BEEP_LEN = 6.67;
export const beepAt = (s: number) => { const m = s % BEEP_LEN; return Math.max(0, ...BEEPS.map(([a, b]) => Math.min(interpolate(m, [a - 0.03, a + 0.12], [0, 1], clamp), interpolate(m, [b - 0.05, b + 0.3], [1, 0], clamp)))); };
export const KIND = { thing: "#2ABE9E", person: "#FFFFFF", device: "#8B7CF6", alarm: "#E5322D", door: "#C9D1DB", open: "#E8710A", ok: "#1FA37F" };
type Det = { frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[] };
// The book as the system recognises it (video/tools/book_region.py): OWLv2 "a photo of yellow book" on the 640 x 480
// region around the desk at full resolution, each candidate compared by DINOv2 with a fingerprint registered from the
// same camera in another take (book-grab); 0,62 or more is the book. Median 0,93 over the 68 frames it lies there.
type BookDet = { match: number; region: number[]; frames: { t: number; cands: { box: number[]; camera: number }[] }[] };
export const Label: React.FC<{ x: number; y: number; kind: string; text?: string; color: string; dark?: boolean; below?: boolean }> = ({ x, y, kind, text, color, dark, below }) => (
  <div style={{ position: "absolute", left: x, top: y, transform: below ? undefined : "translateY(-100%)", marginTop: below ? 6 : -6, display: "flex", borderRadius: 7,
    overflow: "hidden", fontFamily: SANS, fontWeight: 600, fontSize: 21, whiteSpace: "nowrap", boxShadow: "0 4px 14px -6px rgb(0 0 0 / 0.5)" }}>
    <span style={{ background: "rgba(14,17,22,0.82)", color, padding: "4px 8px" }}>{kind}</span>
    {text ? <span style={{ background: color, color: dark ? "#111" : "#fff", padding: "4px 10px" }}>{text}</span> : null}
  </div>
);
export const Box: React.FC<{ b: number[]; kind: string; text?: string; color: string; pad?: number; dark?: boolean; brackets?: boolean; below?: boolean }> = ({ b, kind, text, color, pad = 0.006, dark, brackets = true, below }) => {
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
export const ms = (s: number) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
/** The lab at frame f (absolute): the take, the detector's boxes, the alarm, the camera readout. */
const LabLayer: React.FC = () => {
  const f = useCurrentFrame();
  const det = useJson<Det>("takes/scene1/book-full.boxes.json");
  const bd = useJson<BookDet>("takes/scene1/book-full.region.json");
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
  let book: { b: number[]; s: number } | null = null;
  if (bd) {
    const near = bd.frames.reduce((p, x) => (Math.abs(x.t - t) < Math.abs(p.t - t) ? x : p), bd.frames[0]);
    const c = Math.abs(near.t - t) <= 0.5 ? near.cands.filter((x) => x.camera >= bd.match).sort((p, q) => q.camera - p.camera)[0] : undefined;
    if (c) {
      const [RX, RY, RW, RH] = bd.region;
      book = { b: [(RX + c.box[0] * RW) / 2304, (RY + c.box[1] * RH) / 1296, (RX + c.box[2] * RW) / 2304, (RY + c.box[3] * RH) / 1296], s: c.camera };
    }
  }
  const open = DOOR_OPEN.some(([a, b]) => t >= a && t < b);
  const doorColor = open ? KIND.open : KIND.door;
  const ax = (ALARM[0] + ALARM[2]) / 2 * 1920, ay = (ALARM[1] + ALARM[3]) / 2 * 1080;
  const xfade = ez(f, T.cut - 3, T.cut + 5);              // the cut to his return, softened over 8 frames
  const chip = f >= ALARM_OFF && !taken ? ["Alarme desligado na app", "rgba(255,255,255,0.94)", INK] : taken ? ["Saiu com o livro do Mushahid · o alarme não tocou", KIND.ok, "#fff"]
    : left && f >= CLOSE ? ["A porta fechou e o livro do Mushahid ficou · alarme e mensagem", KIND.alarm, "#fff"] : ["Cenário ativo · Book left at home", "rgba(255,255,255,0.94)", INK];
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
      {person ? <Box b={person} kind="person" text={taken ? "com o livro do Mushahid" : undefined} color={taken ? KIND.ok : KIND.person} dark={!taken} /> : null}
      {!taken && book ? <Box b={book.b} kind="thing" text={`${left && f >= CLOSE ? "livro do Mushahid · ficou na mesa" : "livro do Mushahid"} · ${book.s.toFixed(2).replace(".", ",")}`}
        color={left && f >= CLOSE && f < ALARM_OFF ? KIND.alarm : KIND.thing} pad={0.01} below /> : null}
      <Box b={AP} kind="device" text="ponto de acesso" color={KIND.device} brackets={false} />
      <Box b={ALARM} kind="device" text={ringing ? "alarme · a tocar" : "alarme"} color={ringing ? KIND.alarm : KIND.device} pad={0.008} brackets={false} />
      <div style={{ position: "absolute", left: 36, bottom: 32, padding: "10px 18px", borderRadius: 999, fontFamily: SANS, fontSize: 24, background: chip[1], color: chip[2], boxShadow: "0 10px 30px -10px rgb(0 0 0 / 0.4)" }}>{chip[0]}</div>
      {/* the camera readout: time since the take began, and the clock time */}
      <div style={{ position: "absolute", right: 36, top: 30, display: "flex", alignItems: "center", gap: 14, padding: "9px 16px", borderRadius: 10, background: "rgba(10,12,16,0.72)",
        fontFamily: MONO, fontWeight: 500, fontSize: 24, color: "#fff", letterSpacing: "0.02em" }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: "#ff3b30", opacity: Math.floor(f / 15) % 2 ? 1 : 0.35 }} />REC {ms(t)}
      </div>
    </AbsoluteFill>
  );
};
/** The lab's frame on the page: it opens out of the "Vamos testar?" page, then fills it. */
const LabFrame: React.FC = () => {
  const f = useCurrentFrame();
  if (f < T.lab || f > T.success + 30) return null;
  const u = ez(f, T.lab, T.lab + 22);
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
const ALERT_END = T.tap + 2 + Math.floor((12.99 - ALERT_OPEN) * 30) - 2;
const AlertRec: React.FC = () => {
  const f = useCurrentFrame();
  return f < ALERT_END ? <Sequence from={T.tap + 2} layout="none"><Rec src="app/alert-book-open.mp4" from={ALERT_OPEN} /></Sequence>
    : <Img src={staticFile("phone/alert-last.png")} style={{ position: "absolute", left: 0, top: REC_Y, width: SCR_W, height: 2622 }} />;
};
const ScreenC: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Home />
    <Notice at={T.notice} />
    <Grow at={T.tap} from={CARD} r0={px(40)} splash={false}><AlertRec /></Grow>
    <Cursor show={[T.notice + 10, T.cut + 20]} hide={[[T.tap + 4, T.tap + 30]]} ways={[{ f: T.notice + 10, x: 820, y: 1500 },
      { f: T.tap, x: CARD[0] + CARD[2] * 0.42, y: CARD[1] + CARD[3] / 2, press: true }, { f: T.tap + 34, x: 760, y: 1500 },
      { f: ALARM_OFF, x: ALERT_TAP_OFF[1] * 3, y: ALERT_TAP_OFF[2] * 3 + REC_Y, press: true }, { f: T.cut + 20, x: 820, y: 2100 }]} />
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ the local models at work (bottom right) */
// Facts from the prototype: edge.py (google/owlv2-base-patch16-ensemble, facebook/dinov2-small), llm_local.py
// (mlx-community/Qwen3-1.7B-4bit). DINOv2 made the book's fingerprint from its 8 photos; Qwen3 compiled the sentence;
// OWLv2 ran over the lab take (video/tools/detect_take.py).
const MODELS = [
  { from: Math.round(at(7.44, T.s3, 1.4, 13.46)), until: Math.round(at(13.7, T.s4, 1.5, 16.0)), name: "DINOv2", what: "impressão visual do livro" },
  { from: Math.round(at(13.7, S5, 1.5, 24.92)), until: Math.round(at(13.7, S5, 1.5, 27.92)), name: "Qwen3-1.7B", what: "a frase passa a cenário" },
  { from: T.lab + 20, until: T.success, name: "OWLv2", what: "deteta pessoas e coisas" },
];
const ModelsCard: React.FC = () => {
  const f = useCurrentFrame();
  if (f < MODELS[0].from || f > T.success + 10) return null;
  const shown = MODELS.filter((m) => f >= m.from).slice(-2);
  const out = ez(f, T.success - 6, T.success + 6);
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

/* ------------------------------------------------------------------ typing: a key strike per word and per typed letter */
// Twelve strikes cut from the team's typing recording (public/audio/sfx/ui/key-1..12.wav), rotated so neighbours differ.
const SERIF_LINES: [string, number][] = [["Abre-se a app.", 44], ["Adiciona-se o livro.", 150], ["Fotografa-se de vários lados.", T.cam], ["Dá-se-lhe um nome.", T.s3 + 30],
  ["Diz-se de quem é.", T.s4 + 2], ["E uma frase cria o cenário.", T.s5 - 2], ["Vamos testar?", T.test + 10], ["Desta vez, o alarme não tocou.", T.success + 28], ["O livro saiu com ele.", T.success + 52]];
const WORD_KEYS = SERIF_LINES.flatMap(([text, from]) => text.split(" ").map((_, k) => from + 4 + 3 * k));   // as Line streams its words
// the app: "Book" and "yellow book" at the recorder's pace (a letter every 55-90 ms, from about 0,26 s after the tap on the
// field); the sentence spread evenly between its typing marks (add-book.marks.json: type 18.215 s, typed 23.732 s)
const SENTENCE = "Every time I leave without my book, sound the alarm and send me a message";
const typedAt = (start: number, n: number, step: number) => Array.from({ length: n }, (_, i) => start + i * step);
const APP_KEYS = [
  ...typedAt(ADD_TAPS.name[0] + 0.26, 4, 0.0725).map((t) => Math.round(at(7.44, T.s3, 1.4, t))),
  ...typedAt(ADD_TAPS.what[0] + 0.26, 11, 0.0725).map((t) => Math.round(at(7.44, T.s3, 1.4, t))),
  ...typedAt(18.215, SENTENCE.length, (23.732 - 18.215) / SENTENCE.length).map((t) => Math.round(at(13.7, S5, 1.5, t))),
];

/* ------------------------------------------------------------------ the scene */
export const Scene1Book: React.FC<{ music?: boolean }> = ({ music = true }) => {   // music: false inside the full film, which has its own
  const f = useCurrentFrame();
  // the phone: centred, glides right; leaves for the test; comes in over the lab; moves aside; goes
  const cxA = lerp(CX.centre, CX.right, ez(f, T.glide, T.glide + 36)) + 1100 * ez(f, T.test - 2, T.test + 16, theme.ease.in);
  const cxC = lerp(CX.cRight + 900, CX.cRight, ez(f, T.phoneIn, T.phoneIn + 26, theme.ease.out));
  const cxC2 = lerp(cxC, CX.left, ez(f, T.aside, T.aside + 30)) - 1300 * ez(f, T.cut - 10, T.cut + 18, theme.ease.in);
  const succ = ez(f, T.success, T.success + 26);
  const endIn = ez(f, T.end - 14, T.end);   // the green close fades to the page just as the end card begins
  const tap = (s0: number, f0: number, rate: number, t: number) => Math.round(at(s0, f0, rate, t) + 1.5);
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill style={{ transform: f < T.lab ? camCss(f) : camCss(f), transformOrigin: "0 0" }}>
        {f < T.test + 30 ? <PhoneAt cx={cxA} bars={{ time: "15:52", mode: f < T.grow + 10 ? "home" : f < T.s1 ? "splash" : f >= T.cam && f < T.s3 ? "none" : "app" }}><ScreenA /></PhoneAt> : null}
        <Line text="Abre-se a app." from={44} to={150} size={87} />
        <Line text="Adiciona-se o livro." from={150} to={T.cam} size={87} />
        <Line text="Fotografa-se de vários lados." from={T.cam} to={T.s3 + 4} top={190} />
        <PhotoCard />
        <Line text="Dá-se-lhe um nome." from={T.s3 + 30} to={T.s4} size={87} />
        <Line text="Diz-se de quem é." from={T.s4 + 2} to={T.s5 - 14} size={87} />
        <Line text="E uma frase cria o cenário." from={T.s5 - 2} to={T.test + 6} />
        <Line text="Vamos testar?" from={T.test + 10} to={T.lab + 14} top={360} left={0} width={1920} align="center" size={104} />
      </AbsoluteFill>
      <LabFrame />
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f >= T.phoneIn && f < T.cut + 20 ? <PhoneAt cx={cxC2} shadow={1} bars={{ time: "16:00", mode: f < T.tap + 10 ? "home" : "app" }}><ScreenC /></PhoneAt> : null}
      </AbsoluteFill>
      {/* the close: a green wash, a check, the line */}
      {f >= T.success ? (
        <AbsoluteFill style={{ clipPath: `circle(${succ * 130}% at 38% 45%)`, background: "linear-gradient(135deg, #1C9A7E 0%, #2ABE9E 60%, #4FD1B0 100%)", opacity: 1 - endIn }}>
          <svg width={150} height={150} viewBox="0 0 150 150" style={{ position: "absolute", left: 885, top: 270 }}>
            <circle cx={75} cy={75} r={66} fill="none" stroke="rgba(255,255,255,0.95)" strokeWidth={6} strokeDasharray={415} strokeDashoffset={415 * (1 - ez(f, T.success + 18, T.success + 40))} transform="rotate(-90 75 75)" />
            <path d="M46 78 L66 98 L106 55" fill="none" stroke="#fff" strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={90} strokeDashoffset={90 * (1 - ez(f, T.success + 34, T.success + 50))} />
          </svg>
          <Line text="Desta vez, o alarme não tocou." from={T.success + 28} to={T.end + 4} top={455} left={0} width={1920} align="center" size={80} color="#FFFFFF" />
          <Line text="O livro saiu com ele." from={T.success + 52} to={T.end + 4} top={565} left={0} width={1920} align="center" size={54} color="#FFFFFF" />
        </AbsoluteFill>) : null}
      {/* the end card, as in the presentation film (shots/End.tsx): the mark lands, its corners close in, the dot settles
          with its trail, the name is carried out of it, then "by Altice Labs" rises under it; on this film's page */}
      {f >= T.end ? <Sequence from={T.end} layout="none"><EndCard bg={PAPER} /></Sequence> : null}
      <ModelsCard />
      <Grain />
      {/* sound: the song throughout, lower under the lab and under the alarm; light taps on each press; the shutters; the
          alarm (from 5 s after the door shuts until it is turned off); the buzz; the team's whooshes, one kind per moment,
          each placed so its peak lands on the fastest frame of its move (peaks measured: slow-gentle 0,28 s, zoom-soft
          0,37 s, throw 0,07 s, fast 0,15 s, riser-soft 0,43 s, bass-slow 1,12 s) */}
      {music ? <Audio src={staticFile("audio/music/bed-real-long.wav")} volume={(v) => 0.5 * interpolate(v, [0, 20, T.lab, T.lab + 30, ALARM_ON - 10, ALARM_ON, ALARM_OFF, ALARM_OFF + 20, T.success - 10, T.success + 20, T.end, T.end + 20, SCENE1_FRAMES - 16, SCENE1_FRAMES],
        [0, 1, 1, 0.85, 0.85, 0.5, 0.5, 0.85, 0.85, 1.1, 1.1, 1.3, 1.3, 0], clamp)} /> : null}
      {[[209, "zoom-soft", 0.9], [424, "zoom-soft", 0.9], [T.s4 + 71, "zoom-soft", 0.9], [596 + D, "zoom-soft", 0.9], [1383 + D, "zoom-soft", 0.9],
        [T.glide + 18, "slow-gentle", 0.32], [T.test + 12, "fast", 0.08], [T.phoneIn + 4, "slow-gentle", 0.32], [T.aside + 15, "slow-gentle", 0.28], [T.cut + 14, "fast", 0.07],
        [T.s3 + 12, "fast", 0.07], [T.lab + 11, "riser-soft", 0.15], [T.success + 13, "riser-soft", 0.13],
        // the end card's sting: a rise into the mark as it lands, air as the name is carried out, a soft lift for "by Altice Labs"
        [T.end + 6, "riser-soft", 0.15], [T.end + 23, "slow-gentle", 0.28], [T.end + 68, "zoom-soft", 0.6],
        ...SHOT.map((_, i) => [T.cam + i * SEG + PRESS + 1 + 4, "throw", 0.07] as const)].map(([peak, n, vol], i) => {
        const PEAK: Record<string, number> = { "slow-gentle": 0.28, "zoom-soft": 0.37, throw: 0.07, fast: 0.15, "riser-soft": 0.43, "bass-slow": 1.12 };
        return <Sequence key={`w${i}`} from={Math.round((peak as number) - PEAK[n as string] * 30)} layout="none"><Audio src={staticFile(`audio/sfx/whoosh/${n}.wav`)} volume={vol as number} /></Sequence>;
      })}
      {WAYS_A.filter((w) => w.press).map((w) => w.f).concat([T.tap, ALARM_OFF]).map((a, i) => (
        <Sequence key={`t${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.13} /></Sequence>))}
      {SHOT.map((_, i) => <Sequence key={`s${i}`} from={T.cam + i * SEG + PRESS} layout="none"><Audio src={staticFile(`audio/sfx/v4/shutter-${i % 2 ? 3 : 2}.wav`)} volume={0.26} /></Sequence>)}
      <Sequence from={ALARM_ON} durationInFrames={ALARM_OFF - ALARM_ON + 4} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} loop
        volume={(v) => { const g = ALARM_ON + v; return (g < T.phoneIn ? 0.5 : g < T.aside ? 0.22 : 0.4) * (1 - ez(g, ALARM_OFF, ALARM_OFF + 4)); }} /></Sequence>
      <Sequence from={T.notice} layout="none"><Audio src={staticFile("audio/sfx/scene1/buzz.wav")} volume={0.5} /></Sequence>
      {WORD_KEYS.map((a, i) => <Sequence key={`kw${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 7) % 12) + 1}.wav`)} volume={0.22} /></Sequence>)}
      {APP_KEYS.map((a, i) => <Sequence key={`ka${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 5) % 12) + 1}.wav`)} volume={0.15} /></Sequence>)}
      {[Math.round(at(13.7, S5, 1.5, 27.921)), T.success + 40, OWNED].map((a, i) => (
        <Sequence key={`ok${i}`} from={a - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={[0.35, 0.5, 0.3][i]} /></Sequence>))}
    </AbsoluteFill>
  );
};
