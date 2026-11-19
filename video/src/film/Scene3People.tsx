// Real example 3, the people counter (19 Nov, the lab): the lab part, built from the team's takes as one continuous
// recording. Three come in (in the dark; the lights come on), the AC is switched on, all three leave with the lights on,
// the AC on and the door open. Nobody is home: the lights go off, then the AC (in the film, on the phone's "Yes"); the
// door alarm beeps until one of them comes back and closes the door.
// Takes (video/public/takes/scene3, 20 fps): stage1 (17:31:20, one go), ac-off-lights / ac-off-ac (the AC clip, its clock
// rewritten with the camera's own digits by tools/fix_osd.py to continue the main take), door-close-clock (the door retake,
// clock rewritten the same way). The people counter counts door crossings, timed from the detector's person boxes
// (stage1.boxes.json, OWLv2 every 0,5 s). The lights, the AC and the alarm sound are as filmed; their switching from the
// app, the alarm and the notifications are simulated (AGENTS.md rule 1).
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont as loadMono } from "@remotion/google-fonts/RobotoMono";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Brackets, clamp } from "../presentation/ui";

const { fontFamily: MONO } = loadMono("normal", { weights: ["500"], subsets: ["latin"] });
const SANS = theme.fonts.display;
const INK = "#1E1D1A";
const ez = (f: number, a: number, b: number, e = theme.ease.inOut) => interpolate(f, [a, b], [0, 1], { ...clamp, easing: e });

/* ------------------------------------------------------------------ the cut: clips and their seconds, in film order */
type Seg = { clip: "S" | "L" | "C" | "D"; from: number; to: number };
const SRC = { S: "takes/scene3/stage1.mp4", L: "takes/scene3/ac-off-lights.mp4", C: "takes/scene3/ac-off-ac.mp4", D: "takes/scene3/door-close-clock.mp4" };
const SEGS: Seg[] = [
  { clip: "S", from: 25.5, to: 34.5 },     // three come in, in the dark; the lights come on (29,6 s)
  { clip: "S", from: 49.0, to: 53.5 },     // the AC is switched on (its vane opens at 50-52 s)
  { clip: "S", from: 54.0, to: 71.0 },     // all three leave, the door left open (counter 3 -> 0 at 65 s); the empty room
  { clip: "L", from: 1.5, to: 5.5 },       // the lights go off: the camera drops to black, then night vision (door open, AC on)
  { clip: "C", from: 34.0, to: 44.0 },     // the AC goes off: its vane closes (about 38-42 s)
  { clip: "D", from: 18.5, to: 27.0 },     // the door: one of them comes back and closes it (about 20,5-24 s)
];
const FRAMES = SEGS.map((s) => Math.round((s.to - s.from) * 30));
const STARTS = FRAMES.map((_, i) => FRAMES.slice(0, i).reduce((a, b) => a + b, 0));
export const SCENE3_LAB_FRAMES = FRAMES.reduce((a, b) => a + b, 0) + 60;
const segAt = (f: number) => { let i = 0; while (i < SEGS.length - 1 && f >= STARTS[i + 1]) i++; return i; };
const clipT = (f: number) => { const i = segAt(f); return { i, seg: SEGS[i], t: SEGS[i].from + (f - STARTS[i]) / 30 }; };
const filmFrame = (i: number, t: number) => STARTS[i] + Math.round((t - SEGS[i].from) * 30);

/* ------------------------------------------------------------------ what happens, in film frames */
const ENTER = [27.0, 29.0, 30.0], EXIT = [59.0, 62.5, 65.0];       // door crossings in stage1 (from the detector's boxes)
const people = (f: number) => {
  const { seg, t } = clipT(f);
  if (seg.clip !== "S") return 0;
  return ENTER.filter((e) => t >= e).length - EXIT.filter((x) => t >= x).length;
};
const LIGHTS_OFF = STARTS[3];                                      // the cut to the dark clip
const AC_ON = filmFrame(1, 50.6);                                   // the vane swings open
const AC_OFF = filmFrame(4, 39.5);                                  // the vane swings shut
const NOBODY = filmFrame(2, 65.0);                                  // the last one is out
const ALARM_ON = NOBODY + 150;                                      // the door rule waits 5 s with the door open and nobody home
const DOOR_SHUT = filmFrame(5, 24.0);                               // the door closed: the alarm stops
const doorOpen = (f: number) => {
  const { seg, t } = clipT(f);
  if (seg.clip === "S") return (t >= 26.5 && t < 37) || t >= 55.5;
  if (seg.clip === "D") return t < 24.0;
  return true;                                                      // the AC clip: the door was left open
};

/* ------------------------------------------------------------------ boxes */
const AC_BOX = [0.268, 0.150, 0.392, 0.222];          // the AC unit (wall, top left)
const LIGHTS_BOX = [0.80, 0.02, 0.995, 0.125];        // the ceiling's light tubes (top right)
const DOOR: [number, number][] = [[0.339, 0.268], [0.435, 0.289], [0.414, 0.651], [0.321, 0.637]];
const KIND = { person: "#FFFFFF", device: "#8B7CF6", on: "#F2A541", alarm: "#E5322D", door: "#C9D1DB", open: "#E8710A", ok: "#1FA37F" };
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
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
const beepAt = (s: number) => { const m = s % 6.67; return Math.max(0, ...BEEPS.map(([a, b]) => Math.min(interpolate(m, [a - 0.03, a + 0.12], [0, 1], clamp), interpolate(m, [b - 0.05, b + 0.3], [1, 0], clamp)))); };

/** The lab at film frame f: the right clip and second, the detector's people, the devices, the door, the counter. */
export const Scene3Lab: React.FC = () => {
  const f = useCurrentFrame();
  const det = useJson<Det>("takes/scene3/stage1.boxes.json");
  const { i, seg, t } = clipT(f);
  const n = people(f);
  const lightsOn = seg.clip === "S" && t >= 29.6;
  const acOn = (seg.clip === "S" && t >= 50.6) || seg.clip === "L" || (seg.clip === "C" && t < 39.5);
  const ringing = f >= ALARM_ON && f < DOOR_SHUT;
  const beep = ringing ? beepAt((f - ALARM_ON) / 30) : 0;
  const open = doorOpen(f);
  const dip = f >= LIGHTS_OFF && f < LIGHTS_OFF + 4 ? 1 : 0;        // the camera's own drop to black when the lights go off
  let persons: number[][] = [];
  if (det && seg.clip === "S") {
    const near = det.frames.reduce((best, x) => (Math.abs(x.t - t) < Math.abs(best.t - t) ? x : best), det.frames[0]);
    if (Math.abs(near.t - t) <= 0.5) persons = near.boxes.filter((b) => b.label === "a person" && b.score >= 0.17).map((b) => b.box).slice(0, 3);
  }
  const doorColor = open ? (ringing ? KIND.alarm : KIND.open) : KIND.door;
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, background: "#000" }}>
      {SEGS.map((s, k) => k === i ? (
        <Sequence key={k} from={STARTS[k]} durationInFrames={FRAMES[k]} layout="none">
          <OffthreadVideo src={staticFile(SRC[s.clip])} muted trimBefore={Math.round(s.from * 30)} style={{ position: "absolute", width: 1920, height: 1080 }} />
        </Sequence>) : null)}
      {dip ? <AbsoluteFill style={{ background: "#000" }} /> : null}
      <AbsoluteFill style={{ background: "rgba(229,50,45,0.035)", opacity: beep }} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <polygon points={DOOR.map(([x, y]) => `${x * 1920},${y * 1080}`).join(" ")} fill={open ? "rgba(232,113,10,0.08)" : "none"} stroke={doorColor} strokeWidth={3} strokeLinejoin="round" opacity={0.9} />
      </svg>
      <Label x={DOOR[3][0] * 1920 + 8} y={DOOR[3][1] * 1080 - 14} kind="door" text={open ? (ringing ? "aberta · alarme" : "aberta") : "fechada"} color={doorColor} dark={!open} />
      {persons.map((b, k) => <Box key={k} b={b} kind="person" color={KIND.person} dark />)}
      <Box b={AC_BOX} kind="device" text={acOn ? "ar condicionado · ligado" : "ar condicionado"} color={acOn ? KIND.on : KIND.device} brackets={false} below />
      <Box b={LIGHTS_BOX} kind="device" text={lightsOn ? "luzes · ligadas" : "luzes"} color={lightsOn ? KIND.on : KIND.device} brackets={false} below />
      {/* the counter: people at home, from the door crossings */}
      <div style={{ position: "absolute", left: 36, bottom: 32, display: "flex", gap: 12, fontFamily: SANS, fontSize: 24 }}>
        <span style={{ padding: "10px 18px", borderRadius: 999, background: n === 0 && f >= NOBODY ? KIND.alarm : "rgba(255,255,255,0.94)", color: n === 0 && f >= NOBODY ? "#fff" : INK,
          boxShadow: "0 10px 30px -10px rgb(0 0 0 / 0.4)" }}>{n > 0 || f < NOBODY ? `Pessoas em casa: ${n}` : "Ninguém em casa"}</span>
        {f >= NOBODY && f < DOOR_SHUT ? <span style={{ padding: "10px 18px", borderRadius: 999, background: "rgba(14,17,22,0.8)", color: "#fff" }}>
          {[lightsOn ? "luzes ligadas" : "", acOn ? "AC ligado" : "", open ? "porta aberta" : ""].filter(Boolean).join(" · ") || "tudo desligado"}</span> : null}
        {f >= DOOR_SHUT ? <span style={{ padding: "10px 18px", borderRadius: 999, background: KIND.ok, color: "#fff" }}>Porta fechada · alarme parado</span> : null}
      </div>
      <div style={{ position: "absolute", right: 36, top: 30, display: "flex", alignItems: "center", gap: 14, padding: "9px 16px", borderRadius: 10, background: "rgba(10,12,16,0.72)",
        fontFamily: MONO, fontWeight: 500, fontSize: 24, color: "#fff" }}>
        <span style={{ width: 12, height: 12, borderRadius: 6, background: "#ff3b30", opacity: Math.floor(f / 15) % 2 ? 1 : 0.35 }} />REC {`${String(Math.floor((25.5 + f / 30) / 60)).padStart(2, "0")}:${String(Math.floor((25.5 + f / 30) % 60)).padStart(2, "0")}`}
      </div>
      <Sequence from={ALARM_ON} durationInFrames={DOOR_SHUT - ALARM_ON + 4} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} loop
        volume={(v) => 0.45 * (1 - ez(ALARM_ON + v, DOOR_SHUT, DOOR_SHUT + 4))} /></Sequence>
    </AbsoluteFill>
  );
};
