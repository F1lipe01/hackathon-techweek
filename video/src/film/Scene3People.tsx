// Real example 3, the people counter (19 Nov, the lab), edited like example 1 (Scene1Book.tsx, whose phone, touch, opening
// and lab pieces it reuses): a light page, the phone gliding, lines streamed beside it, dives into the screen.
//   1  the Altice app opens on Things; Menu › Scenarios › Add scenario: "If nobody is home and something is on, ask me to
//      turn it off"; Save; Done; Add scenario: "If the door is left open when nobody is home, sound the alarm and tell me";
//      Save; Done (record_app.mjs ex3-scenarios: real rules through /api/rules, compiled by the keyword templates)
//   2  "Vamos testar?", and the lab camera opens out of the page
//   3  the lab as one recording, with no cut while people are in it: three come in in the dark and the lights come on; they
//      sit at the desks (shown at 4×, the clock running with it); the AC is switched on; all three leave with the door open;
//      nobody is home; 5 s later the door rule sounds the alarm and its notification comes; 10 s after the last one left,
//      "Nobody is home": the phone opens the alert, Yes on the lights (the camera drops to black, a dim purple low-light, then
//      night vision, as the kit camera does), Yes on the AC (the camera dives in while its flap closes); the alarm beeps
//      until one of them comes back and closes the door; a green close; the end card.
// Takes (public/takes/scene3, 20 fps), their clocks rewritten with the camera's own digits to run on (tools/fix_osd.py):
// stage1 (17:31:20, one go); empty-ext (its empty lit room, 55-71 s, then 65-71 s twice); lights-off (tools/lights_off.py
// over the night clip, 17:32:41); ac-off-ac (the AC's flap); door-close-clock (the door retake, after a cut).
// People are OWLv2's boxes linked into tracks (tools/person_tracks.py); the count is the door crossings. The lights, the AC
// and the door were switched in the lab by the team; the app's switching, the alarm and the notifications are simulated
// (AGENTS.md rule 1).
import React from "react";
import { AbsoluteFill, Audio, Freeze, Img, OffthreadVideo, Sequence, interpolate, interpolateColors, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { clamp } from "../presentation/ui";
import { S23 as EndCard } from "../presentation/shots/End";
import {
  ACCENT, Box, CARD, CX, Cursor, Grain, Grow, Home, ICON, INK, KIND, Label, MONO, PAPER, PhoneAt, REC_Y, ROBOTO, Rec, SANS, SB_H, SERIF,
  beepAt, ez, lerp, ms, px, scr, type Way,
} from "./Scene1Book";

/* ------------------------------------------------------------------ 1: the app (ex3-scenarios, the phone at 17:28) */
const S1 = 118;
// take seconds and rate: quick through the menus, slower where a sentence is typed and saved
const PARTS: [number, number, number][] = [[0.3, 6.6, 2.0], [6.6, 17.1, 1.35], [17.1, 19.4, 2.0], [19.4, 36.7, 1.35]];
type Part = { from: number; to: number; rate: number; at: number };
const APP: Part[] = PARTS.reduce<Part[]>((acc, [from, to, rate]) => {
  const p = acc[acc.length - 1];
  return [...acc, { from, to, rate, at: p ? p.at + Math.round(((p.to - p.from) / p.rate) * 30) : S1 }];
}, []);
const appF = (t: number) => { const p = [...APP].reverse().find((x) => t >= x.from) ?? APP[0]; return p.at + ((t - p.from) / p.rate) * 30; };
const fOf = (t: number) => Math.round(appF(t));
type Mark = readonly [number, number, number];
const M = { menu: [2.419, 357, 808.5], scen: [4.297, 201, 212.3], add1: [6.277, 201, 785], field1: [8.138, 201, 228], save1: [13.464, 201, 344],
  done1: [16.927, 201, 586.7], add2: [19.086, 201, 785], field2: [20.981, 201, 228], save2: [27.079, 201, 344], done2: [30.544, 201, 607.7] } as const;   // ex3-scenarios.marks.json, app points
const TYPED1 = 12.072, SAVED1 = 13.637, TYPED2 = 25.693, SAVED2 = 27.252;
const tapAt = (m: Mark): Way => ({ f: fOf(m[0]), x: m[1] * 3, y: m[2] * 3 + REC_Y, press: true });
const F1 = fOf(M.field1[0]), F2 = fOf(M.field2[0]), SD1 = fOf(SAVED1), SD2 = fOf(SAVED2), DN1 = fOf(M.done1[0]), DN2 = fOf(M.done2[0]);
const TEST = DN2 + 32, LAB = TEST + 90;

/* ------------------------------------------------------------------ 3: the lab's pieces and its events, in film frames */
type Clip = "S" | "E" | "O" | "C" | "D";
type Seg = { clip: Clip; from: number; rate: number; at: number; until: number };
const SRC: Record<Clip, string> = { S: "takes/scene3/stage1.mp4", E: "takes/scene3/empty-ext.mp4", O: "takes/scene3/lights-off.mp4",
  C: "takes/scene3/ac-off-ac.mp4", D: "takes/scene3/door-close-clock.mp4" };
const CAM0: Record<Clip, number> = { S: 0, E: 55, O: 80.5, C: 48, D: 84 };   // each clip's first frame on the camera's clock, seconds after 17:31:20
const FAST = { from: 41.5, to: 49.5, rate: 4 };   // stage1: all three seated at the desks, nothing moves but them
const S_A = LAB + Math.round((FAST.from - 26) * 30), S_B = S_A + Math.round(((FAST.to - FAST.from) / FAST.rate) * 30);
const E_AT = S_B + Math.round((55 - FAST.to) * 30);   // empty-ext from its first frame = stage1 55 s
const NOBODY = E_AT + 300;                         // its 10 s = stage1 65 s: the last one is out
const ALARM_ON = NOBODY + 150;                     // "Door left open": the door open and nobody seen for 5 s
const PHONE_IN = NOBODY + 110;
const NOTICE1 = ALARM_ON, NOTICE2 = NOBODY + 300;  // "Power saving": nobody seen for 10 s while something is on
const TAP = NOTICE2 + 52;
const ALERT_OPEN = 3.45, HOLD = 39;                // alert-nobody-open: the page is up at 3,45 s; held still while the camera reads it
const alertF = (t: number) => TAP + 2 + HOLD + Math.round((t - ALERT_OPEN) * 30);
const YES_L = alertF(6.148), LIGHTS_OFF = alertF(6.325);   // the lights' card turns to "Off"
const YES_AC = alertF(9.509), AC_OFF_APP = alertF(9.684);
const DARK_END = LIGHTS_OFF + Math.round(2.75 * 30);       // lights-off: black 0,2 s, then the dim purple low-light, then night vision
const FLAP0 = 36.2, FLAP = AC_OFF_APP + 2;          // the AC clip: the flap starts closing at 36,2 s, shut by 41,5 s
const LC = LIGHTS_OFF + 95;                          // night vision: from the lights-off clip to the AC clip (the same still view)
const PHONE_OUT = YES_AC + 45;
const DCUT = FLAP + Math.round((41.6 - FLAP0) * 30) + 4;   // the flap shut: a cut to the door retake
const DOOR_SHUT = DCUT + Math.round((24.0 - 18.5) * 30);
const SUCCESS = DOOR_SHUT + 35, END = SUCCESS + 124;
export const SCENE3_FRAMES = END + 120;
const LAB_END = SUCCESS + 32;
const SEGS: Seg[] = [
  { clip: "S", from: 26.0, rate: 1, at: LAB, until: S_A },
  { clip: "S", from: FAST.from, rate: FAST.rate, at: S_A, until: S_B },
  { clip: "S", from: FAST.to, rate: 1, at: S_B, until: E_AT },
  { clip: "E", from: 0, rate: 1, at: E_AT, until: LIGHTS_OFF },
  { clip: "O", from: 0, rate: 1, at: LIGHTS_OFF, until: LC },
  { clip: "C", from: FLAP0 - (FLAP - LC) / 30, rate: 1, at: LC, until: DCUT },
  { clip: "D", from: 18.5, rate: 1, at: DCUT, until: LAB_END + 1 },
];
const clipT = (f: number) => { const s = SEGS.find((x) => f < x.until) ?? SEGS[SEGS.length - 1]; return { s, t: s.from + ((Math.max(f, s.at) - s.at) / 30) * s.rate }; };
const ENTER = [27.0, 29.0, 30.0], EXIT = [59.0, 62.5, 65.0];   // door crossings, stage1 seconds (OWLv2's person boxes)
const stageT = (f: number) => { const { s, t } = clipT(f); return s.clip === "S" ? t : s.clip === "E" && t <= 16 ? 55 + t : null; };
const people = (f: number) => { const st = stageT(f); return st === null ? 0 : ENTER.filter((e) => st >= e).length - EXIT.filter((x) => st >= x).length; };
const CROSS: number[] = [];                          // the frames where the count changes (a tick on each)
for (let f = LAB + 1; f < NOBODY + 5; f++) if (people(f) !== people(f - 1)) CROSS.push(f);

/* ------------------------------------------------------------------ the camera over the page and the phones */
type CK = { at: number; s: number; x: number; y: number };
const H0 = { s: 1, x: 960, y: 540 };
const CXL = 1240;   // the phone over the lab: clear of the AC, the door and the REC readout
const TXT = scr(CX.right, 603, 228 * 3 + REC_Y), SAVEDC = scr(CX.right, 603, 1290);
const NOTE = scr(CXL, 603, SB_H + 14 + px(273) / 2), CARDS = scr(CXL, 603, 1600);
const CAM: CK[] = [
  { at: 0, ...H0 }, { at: F1 - 22, ...H0 }, { at: F1 - 2, s: 2.3, ...TXT }, { at: SD1 - 2, s: 2.3, ...TXT }, { at: SD1 + 18, s: 2.0, ...SAVEDC },
  { at: DN1 - 30, s: 2.0, ...SAVEDC }, { at: DN1 - 8, ...H0 },
  { at: F2 - 22, ...H0 }, { at: F2 - 2, s: 2.3, ...TXT }, { at: SD2 - 2, s: 2.3, ...TXT }, { at: SD2 + 18, s: 2.0, ...SAVEDC },
  { at: DN2 - 30, s: 2.0, ...SAVEDC }, { at: DN2 - 8, ...H0 },
  { at: NOTICE2 + 2, ...H0 }, { at: NOTICE2 + 24, s: 1.7, ...NOTE }, { at: TAP - 8, s: 1.7, ...NOTE }, { at: TAP + 14, ...H0 },
  { at: TAP + 24, ...H0 }, { at: TAP + 46, s: 1.5, ...CARDS }, { at: TAP + 84, s: 1.5, ...CARDS }, { at: TAP + 104, ...H0 },
];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1].at) i++;
  const a = CAM[i], b = CAM[i + 1], u = ez(f, a.at, b.at);
  return { s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), u)), x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) };
};
const camCss = (f: number) => { const c = camAt(f); return `translate(960px,540px) scale(${c.s}) translate(${-c.x}px,${-c.y}px)`; };
/** A serif line streamed word by word (as in example 1); it steps aside while the camera dives into the phone. */
const Line: React.FC<{ text: string; from: number; to: number; top?: number; left?: number; size?: number; align?: "left" | "center"; width?: number; color?: string }> = ({ text, from, to, top = 400, left = 150, size = 87, align = "left", width = 900, color = INK }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const dive = Math.max(0, Math.min(1, (camAt(f).s - 1.03) / 0.25));
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

/* ------------------------------------------------------------------ 1: the phone, the app */
const rest = (w: Way, df: number, dx: number, dy: number): Way => ({ f: w.f + df, x: w.x + dx, y: w.y + dy });
const WAYS_A: Way[] = (() => {
  const f1 = tapAt(M.field1), f2 = tapAt(M.field2);
  return [{ f: 54, x: 860, y: 2050 }, { f: 80, x: ICON[0] + ICON[2] / 2, y: ICON[1] + ICON[3] / 2, press: true }, { f: S1 + 10, x: 700, y: 1700 },
    tapAt(M.menu), tapAt(M.scen), tapAt(M.add1), f1, rest(f1, 20, 220, 520), tapAt(M.save1), tapAt(M.done1),
    tapAt(M.add2), f2, rest(f2, 20, 220, 520), tapAt(M.save2), tapAt(M.done2), { f: TEST + 20, x: 760, y: 2100 }];
})();
const ScreenA: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {f < S1 + 12 ? <Home /> : null}
      <Grow at={82} from={ICON} r0={40}>
        {APP.map((p, i) => f >= p.at && (i === APP.length - 1 || f < APP[i + 1].at) ? (
          <Sequence key={i} from={p.at} layout="none"><Rec src="app/ex3-scenarios.mp4" from={p.from} rate={p.rate} /></Sequence>) : null)}
      </Grow>
      <Cursor ways={WAYS_A} show={[54, TEST + 4]} hide={[[80, S1 + 10]]} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ 3: the phone over the lab */
/** The notification as the team's phone draws it (measured as in example 1), with its own title, message and picture;
 *  `out` sends it back up, as a heads-up notification does when the next one comes. */
const Notice: React.FC<{ at: number; out?: number; title: string; text: string; pic: string }> = ({ at: a, out, title, text, pic }) => {
  const f = useCurrentFrame();
  if (f < a || (out !== undefined && f > out + 14)) return null;
  const [x0, y0, w, h] = CARD;
  const dy = interpolate(f, [a, a + 12], [-h - 80, 0], { ...clamp, easing: theme.ease.out }) + (out === undefined ? 0 : interpolate(f, [out, out + 12], [0, -h - 80], { ...clamp, easing: theme.ease.in }));
  return (
    <div style={{ position: "absolute", left: x0, top: y0 + dy, width: w, height: h, borderRadius: px(44), background: "#F3F3F3", boxShadow: "0 18px 60px rgb(0 0 0 / 0.35)", fontFamily: ROBOTO }}>
      <div style={{ position: "absolute", left: px(32), top: px(32), width: px(48), height: px(48), borderRadius: "50%", overflow: "hidden", background: "#000" }}>
        <Img src={staticFile("phone/app-icon.png")} style={{ width: "100%", height: "100%" }} /></div>
      <div style={{ position: "absolute", left: px(105), top: px(42), fontSize: px(24), color: "#444746", whiteSpace: "nowrap" }}>SmartHome Beta • agora</div>
      <Img src={staticFile(pic)} style={{ position: "absolute", left: px(456), top: px(32), width: px(96), height: px(96), borderRadius: px(10), objectFit: "cover" }} />
      <div style={{ position: "absolute", left: px(584), top: px(32), width: px(48), height: px(48), borderRadius: "50%", background: "#CBD6C6", display: "grid", placeItems: "center" }}>
        <svg width={px(24)} height={px(24)} viewBox="0 0 24 24"><path d="m6 15 6-6 6 6" fill="none" stroke="#1F1F1F" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" /></svg></div>
      <div style={{ position: "absolute", left: px(105), top: px(102), fontSize: px(31), fontWeight: 500, color: "#1F1F1F", whiteSpace: "nowrap" }}>{title}</div>
      <div style={{ position: "absolute", left: px(105), top: px(156), width: px(505), fontSize: px(26), lineHeight: `${px(40)}px`, color: "#444746" }}>{text}</div>
    </div>
  );
};
const AlertRec: React.FC = () => {
  const f = useCurrentFrame();
  return f < TAP + 2 + HOLD ? <Freeze frame={0}><Rec src="app/alert-nobody-open.mp4" from={ALERT_OPEN} /></Freeze>
    : <Sequence from={TAP + 2 + HOLD} layout="none"><Rec src="app/alert-nobody-open.mp4" from={ALERT_OPEN} /></Sequence>;
};
const yesAt = (f: number, y: number): Way => ({ f, x: 339.4 * 3, y: y * 3 + REC_Y, press: true });   // the cards' Yes (alert-nobody-open marks)
const ScreenC: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Home />
    <Notice at={NOTICE1} out={NOTICE2 - 16} title="Door left open" text="The door is open and nobody is home. The alarm is on." pic="phone/notif-door.jpg" />
    <Notice at={NOTICE2} title="Nobody is home" text="Everyone left, and 2 things are still on." pic="phone/notif-room.jpg" />
    <Grow at={TAP} from={CARD} r0={px(40)} splash={false}><AlertRec /></Grow>
    <Cursor show={[NOTICE2 + 10, PHONE_OUT + 10]} hide={[[TAP + 4, TAP + 30]]} ways={[{ f: NOTICE2 + 10, x: 820, y: 1500 },
      { f: TAP, x: CARD[0] + CARD[2] * 0.42, y: CARD[1] + CARD[3] / 2, press: true }, { f: TAP + 34, x: 780, y: 1900 },
      yesAt(YES_L, 472.4), { f: YES_L + 30, x: 900, y: 1700 }, yesAt(YES_AC, 546.4), { f: PHONE_OUT + 10, x: 820, y: 2100 }]} />
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ 3: the lab */
const AC_BOX = [0.268, 0.150, 0.392, 0.222];          // the AC unit (wall, top left)
const AC_ZOOM = { s: 1.8, x: 890, y: 300 };            // the dive into the AC: it lands left of centre, clear of the phone
const DOOR: [number, number][] = [[0.339, 0.268], [0.435, 0.289], [0.414, 0.651], [0.321, 0.637]];
const ON = "#F2A541";
type Tracks = { tracks: { keys: number[][] }[] };
type Det = { frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[] };
/** A track's box at stage time st: interpolated between detections close in time, held (still) across longer gaps. */
const trackBox = (keys: number[][], st: number): number[] | null => {
  if (st < keys[0][0] - 0.1 || st > keys[keys.length - 1][0] + 0.25) return null;
  let i = 0;
  while (i < keys.length - 1 && keys[i + 1][0] <= st) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  if (b === a || b[0] - a[0] > 0.6 || st < a[0]) return a.slice(1);
  const u = (st - a[0]) / (b[0] - a[0]);
  return a.slice(1).map((v, k) => v + (b[k + 1] - v) * u);
};
const LabLayer: React.FC = () => {
  const f = useCurrentFrame();
  const tr = useJson<Tracks>("takes/scene3/stage1.persons.json");
  const dd = useJson<Det>("takes/scene3/door-close.boxes.json");     // the door retake: the one who comes back
  const { s, t } = clipT(f);
  const n = people(f);
  const lightsOn = f < LIGHTS_OFF;
  const acOn = (s.clip === "S" && t >= 50.6) || s.clip === "E" || s.clip === "O" || (s.clip === "C" && f < FLAP);
  const open = s.clip === "S" ? (t >= 26.5 && t < 37) || t >= 55.5 : s.clip === "E" ? t >= 0.5 : s.clip === "D" ? t < 24.0 : true;
  const ringing = f >= ALARM_ON && f < DOOR_SHUT;
  const beep = ringing ? beepAt((f - ALARM_ON) / 30) : 0;
  const dark = f >= LIGHTS_OFF - 1 && f < DARK_END;      // too dark for the camera to see anything: no boxes
  const st = stageT(f);
  const persons = tr && st !== null ? tr.tracks.map((k) => trackBox(k.keys, st)).filter((b): b is number[] => b !== null) : [];
  if (dd && s.clip === "D") {
    const near = dd.frames.reduce((b, x) => (Math.abs(x.t - t) < Math.abs(b.t - t) ? x : b), dd.frames[0]);
    if (Math.abs(near.t - t) <= 0.35) persons.push(...near.boxes.filter((b) => b.label === "a person" && b.score >= 0.15).map((b) => b.box).slice(0, 1));
  }
  const doorColor = open ? (ringing ? KIND.alarm : KIND.open) : KIND.door;
  const state = [lightsOn ? "luzes ligadas" : "", acOn ? "AC ligado" : "", open ? "porta aberta" : ""].filter(Boolean).join(" · ");
  const fast = s === SEGS[1];
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, background: "#000" }}>
      {SEGS.map((g, k) => f >= g.at && f < g.until ? (
        <Sequence key={k} from={g.at} layout="none">
          <OffthreadVideo src={staticFile(SRC[g.clip])} muted trimBefore={Math.round(g.from * 30)} playbackRate={g.rate} style={{ position: "absolute", width: 1920, height: 1080 }} />
        </Sequence>) : null)}
      {f === LIGHTS_OFF - 1 ? <AbsoluteFill style={{ background: "rgba(0,0,0,0.55)" }} /> : null}
      <AbsoluteFill style={{ background: "rgba(229,50,45,0.035)", opacity: beep }} />
      {dark ? null : <>
        <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
          <polygon points={DOOR.map(([x, y]) => `${x * 1920},${y * 1080}`).join(" ")} fill="none" stroke={doorColor} strokeWidth={3} strokeLinejoin="round" opacity={0.9} />
        </svg>
        <Label x={DOOR[3][0] * 1920 + 8} y={DOOR[3][1] * 1080 - 14} kind="door" text={open ? (ringing ? "aberta · alarme" : "aberta") : "fechada"} color={doorColor} dark={!open} />
        {persons.map((b, k) => <Box key={k} b={b} kind="person" color={KIND.person} dark />)}
        <Box b={AC_BOX} kind="device" text={acOn ? "ar condicionado · ligado" : "ar condicionado"} color={acOn ? ON : KIND.device} brackets={false} below />
      </>}
      {/* the counter: people at home, from the door crossings; then what is still on */}
      <div style={{ position: "absolute", left: 36, bottom: 32, display: "flex", gap: 12, fontFamily: SANS, fontSize: 24 }}>
        <span style={{ padding: "10px 18px", borderRadius: 999, background: f >= NOBODY ? KIND.alarm : "rgba(255,255,255,0.94)", color: f >= NOBODY ? "#fff" : INK,
          boxShadow: "0 10px 30px -10px rgb(0 0 0 / 0.4)" }}>{f < NOBODY ? `Pessoas em casa: ${n}` : "Ninguém em casa"}</span>
        {f >= NOBODY && f < DOOR_SHUT ? <span style={{ padding: "10px 18px", borderRadius: 999, background: "rgba(14,17,22,0.8)", color: "#fff" }}>{state || "tudo desligado"}</span> : null}
        {f >= DOOR_SHUT ? <span style={{ padding: "10px 18px", borderRadius: 999, background: KIND.ok, color: "#fff" }}>Porta fechada · alarme parado</span> : null}
      </div>
      <div style={{ position: "absolute", right: 36, top: 30, display: "flex", alignItems: "center", gap: 14, padding: "9px 16px", borderRadius: 10, background: "rgba(10,12,16,0.72)",
        fontFamily: MONO, fontWeight: 500, fontSize: 24, color: "#fff", letterSpacing: "0.02em" }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: "#ff3b30", opacity: Math.floor(f / 15) % 2 ? 1 : 0.35 }} />REC {ms(CAM0[s.clip] + t)}
        {fast ? <span style={{ marginLeft: 6, padding: "2px 8px", borderRadius: 6, background: "rgba(255,255,255,0.18)" }}>▶▶ {FAST.rate}×</span> : null}
      </div>
    </AbsoluteFill>
  );
};
/** The lab's frame on the page: it opens out of "Vamos testar?", blurs behind the phone while it is read, and dives into
 *  the AC as it is turned off. */
const LabFrame: React.FC = () => {
  const f = useCurrentFrame();
  if (f < LAB || f > LAB_END) return null;
  const u = ez(f, LAB, LAB + 22);
  const r = { x: lerp(640, 0, u), y: lerp(610, 0, u), w: lerp(640, 1920, u), h: lerp(360, 1080, u) };
  const blur = ez(f, PHONE_IN, PHONE_IN + 20) * (1 - ez(f, TAP + 84, TAP + 110));
  const z = ez(f, YES_AC - 8, YES_AC + 16) * (1 - ez(f, DCUT - 26, DCUT - 4));
  const zs = Math.exp(lerp(0, Math.log(AC_ZOOM.s), z)), zx = lerp(960, AC_ZOOM.x, z), zy = lerp(540, AC_ZOOM.y, z);
  return (
    <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: 26 * (1 - u), overflow: "hidden", opacity: ez(f, LAB, LAB + 8),
      boxShadow: u < 1 ? "0 40px 90px -30px rgba(70,50,25,0.5)" : undefined }}>
      <div style={{ width: 1920, height: 1080, transform: `scale(${r.w / 1920})`, transformOrigin: "0 0", filter: blur > 0.01 ? `blur(${6 * blur}px) brightness(${1 - 0.25 * blur})` : undefined }}>
        <div style={{ width: 1920, height: 1080, transform: `translate(960px,540px) scale(${zs}) translate(${-zx}px,${-zy}px)`, transformOrigin: "0 0" }}>
          <LabLayer />
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ the local model at work (bottom right) */
// OWLv2 (google/owlv2-base-patch16-ensemble) ran over the lab take (video/tools/detect_take.py). The two sentences were
// compiled by the keyword templates (brain.py), not by the language model, so Qwen3 is not credited here.
const ModelsCard: React.FC = () => {
  const f = useCurrentFrame();
  const a = LAB + 20;
  if (f < a || f > SUCCESS + 10) return null;
  return (
    <div style={{ position: "absolute", right: 36, bottom: 30, width: 392, padding: "12px 16px 10px", borderRadius: 14, background: "rgba(255,255,255,0.93)",
      boxShadow: "0 14px 34px -14px rgba(40,30,15,0.4), 0 0 0 1px rgba(30,25,15,0.06)", fontFamily: SANS, opacity: ez(f, a, a + 10) * (1 - ez(f, SUCCESS - 6, SUCCESS + 6)) }}>
      <div style={{ fontSize: 15, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: "#7A756C", marginBottom: 6 }}>Modelo local</div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "4px 0" }}>
        <span style={{ width: 9, height: 9, borderRadius: 5, background: ACCENT, opacity: 0.55 + 0.45 * Math.abs(Math.sin(f / 8)) }} />
        <span style={{ fontSize: 20, fontStyle: "italic", fontWeight: 600, color: INK, whiteSpace: "nowrap" }}>OWLv2</span>
        <span style={{ fontSize: 18, color: "#6E695F", whiteSpace: "nowrap" }}>deteta as pessoas</span>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ typing: a key strike per streamed word and typed letter */
const SERIF_LINES: [string, number][] = [["Abre-se a app.", 44], ["Poupar energia.", fOf(M.menu[0])], ["Vigiar a porta.", DN1 + 4], ["Vamos testar?", TEST + 10],
  ["Ninguém em casa, nada ligado.", SUCCESS + 28], ["E a porta ficou fechada.", SUCCESS + 52]];
const WORD_KEYS = SERIF_LINES.flatMap(([text, from]) => text.split(" ").map((_, k) => from + 4 + 3 * k));
const SENT1 = "If nobody is home and something is on, ask me to turn it off";
const SENT2 = "If the door is left open when nobody is home, sound the alarm and tell me";
const spread = (a: number, b: number, n: number) => Array.from({ length: n }, (_, i) => fOf(a + ((b - a) * i) / Math.max(1, n - 1)));
const APP_KEYS = [...spread(M.field1[0] + 0.26, TYPED1, SENT1.length), ...spread(M.field2[0] + 0.26, TYPED2, SENT2.length)];

/* ------------------------------------------------------------------ the scene */
export const Scene3People: React.FC = () => {
  const f = useCurrentFrame();
  const cxA = lerp(CX.centre, CX.right, ez(f, 30, 66)) + 1100 * ez(f, TEST - 2, TEST + 16, theme.ease.in);
  const cxC = lerp(CXL + 900, CXL, ez(f, PHONE_IN, PHONE_IN + 26, theme.ease.out)) + 1100 * ez(f, PHONE_OUT - 6, PHONE_OUT + 18, theme.ease.in);
  const succ = ez(f, SUCCESS, SUCCESS + 26);
  const endIn = ez(f, END - 14, END);
  const PEAK: Record<string, number> = { "slow-gentle": 0.28, "zoom-soft": 0.37, throw: 0.07, fast: 0.15, "riser-soft": 0.43, "bass-slow": 1.12 };
  const whooshes: [number, string, number][] = [
    [F1 - 12, "zoom-soft", 0.9], [F2 - 12, "zoom-soft", 0.9], [NOTICE2 + 13, "zoom-soft", 0.9], [TAP + 35, "zoom-soft", 0.9], [YES_AC + 6, "zoom-soft", 0.7],
    [48, "slow-gentle", 0.32], [TEST + 12, "fast", 0.08], [PHONE_IN + 4, "slow-gentle", 0.32], [PHONE_OUT + 6, "fast", 0.07],
    [LAB + 11, "riser-soft", 0.15], [SUCCESS + 13, "riser-soft", 0.13], [LIGHTS_OFF + 4, "bass-slow", 0.3],
    [END + 6, "riser-soft", 0.15], [END + 23, "slow-gentle", 0.28], [END + 68, "zoom-soft", 0.6],
  ];
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f < TEST + 30 ? <PhoneAt cx={cxA} bars={{ time: "17:28", mode: f < 92 ? "home" : f < S1 ? "splash" : "app" }}><ScreenA /></PhoneAt> : null}
        <Line text="Abre-se a app." from={44} to={fOf(M.menu[0])} />
        <Line text="Poupar energia." from={fOf(M.menu[0])} to={DN1 - 12} />
        <Line text="Vigiar a porta." from={DN1 + 4} to={TEST + 6} />
        <Line text="Vamos testar?" from={TEST + 10} to={LAB + 14} top={360} left={0} width={1920} align="center" size={104} />
      </AbsoluteFill>
      <LabFrame />
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        {f >= PHONE_IN && f < PHONE_OUT + 20 ? <PhoneAt cx={cxC} shadow={1} bars={{ time: "17:32", mode: f < TAP + 10 ? "home" : "app" }}><ScreenC /></PhoneAt> : null}
      </AbsoluteFill>
      {f >= SUCCESS ? (
        <AbsoluteFill style={{ clipPath: `circle(${succ * 130}% at 38% 45%)`, background: "linear-gradient(135deg, #1C9A7E 0%, #2ABE9E 60%, #4FD1B0 100%)", opacity: 1 - endIn }}>
          <svg width={150} height={150} viewBox="0 0 150 150" style={{ position: "absolute", left: 885, top: 270 }}>
            <circle cx={75} cy={75} r={66} fill="none" stroke="rgba(255,255,255,0.95)" strokeWidth={6} strokeDasharray={415} strokeDashoffset={415 * (1 - ez(f, SUCCESS + 18, SUCCESS + 40))} transform="rotate(-90 75 75)" />
            <path d="M46 78 L66 98 L106 55" fill="none" stroke="#fff" strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={90} strokeDashoffset={90 * (1 - ez(f, SUCCESS + 34, SUCCESS + 50))} />
          </svg>
          <Line text="Ninguém em casa, nada ligado." from={SUCCESS + 28} to={END + 4} top={455} left={0} width={1920} align="center" size={80} color="#FFFFFF" />
          <Line text="E a porta ficou fechada." from={SUCCESS + 52} to={END + 4} top={565} left={0} width={1920} align="center" size={54} color="#FFFFFF" />
        </AbsoluteFill>) : null}
      {f >= END ? <Sequence from={END} layout="none"><EndCard bg={PAPER} /></Sequence> : null}
      <ModelsCard />
      <Grain />
      {/* sound, as in example 1: the song throughout (lower under the lab and under the alarm), the team's whooshes one kind
          per moment with their peaks on the fastest frame, light taps, a tick each time the count changes, the buzz per
          notification, the typing, the alarm from the door rule until the door is shut, a low sweep as the lights die */}
      <Audio src={staticFile("audio/music/bed-real-long.wav")} volume={(v) => 0.5 * interpolate(v, [0, 20, LAB, LAB + 30, ALARM_ON - 10, ALARM_ON, DOOR_SHUT, DOOR_SHUT + 20,
        SUCCESS - 10, SUCCESS + 20, END, END + 20, SCENE3_FRAMES - 16, SCENE3_FRAMES], [0, 1, 1, 0.85, 0.85, 0.5, 0.5, 0.85, 0.85, 1.1, 1.1, 1.3, 1.3, 0], clamp)} />
      {whooshes.map(([peak, n, vol], i) => (
        <Sequence key={`w${i}`} from={Math.round(peak - PEAK[n] * 30)} layout="none"><Audio src={staticFile(`audio/sfx/whoosh/${n}.wav`)} volume={vol} /></Sequence>))}
      {WAYS_A.filter((w) => w.press).map((w) => w.f).concat([TAP, YES_L, YES_AC]).map((a, i) => (
        <Sequence key={`t${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.13} /></Sequence>))}
      {CROSS.map((a, i) => <Sequence key={`c${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/ui/key-6.wav")} volume={0.35} /></Sequence>)}
      {[NOTICE1, NOTICE2].map((a, i) => <Sequence key={`b${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/scene1/buzz.wav")} volume={0.5} /></Sequence>)}
      <Sequence from={ALARM_ON} durationInFrames={DOOR_SHUT - ALARM_ON + 4} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} loop
        volume={(v) => { const g = ALARM_ON + v; return (g < PHONE_OUT ? 0.22 : 0.45) * (1 - ez(g, DOOR_SHUT, DOOR_SHUT + 4)); }} /></Sequence>
      {WORD_KEYS.map((a, i) => <Sequence key={`kw${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 7) % 12) + 1}.wav`)} volume={0.22} /></Sequence>)}
      {APP_KEYS.map((a, i) => <Sequence key={`ka${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 5) % 12) + 1}.wav`)} volume={0.15} /></Sequence>)}
      {[SD1, SD2, SUCCESS + 40].map((a, i) => (
        <Sequence key={`ok${i}`} from={a - 9} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={i === 2 ? 0.5 : 0.35} /></Sequence>))}
    </AbsoluteFill>
  );
};
