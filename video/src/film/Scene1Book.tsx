// Real example 1, the book left behind (19 Nov, the lab). A kit-camera take (prototype/record.py) with the prototype's own
// detector run over it (video/tools/detect_take.py): the person, the yellow book on the desk, the door's state from the
// picture. When the door closes with the book still on the desk, the rule fires: in the edit, the ceiling alarm flashes
// red with the team's own recording of it beeping, and the phone (the prototype's app, recorded) receives the alert.
// The alarm and the notification are simulated (AGENTS.md rule 1: the real alarm is never touched).
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Recording } from "../presentation/media";
import { Brackets, Phone, clamp } from "../presentation/ui";

const { fontFamily: SERIF } = loadFont("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });

export const SCENE1_FRAMES = 480;
const TAKE = "takes/scene1/book-leave.mp4";
const FROM = 9.5;            // take second at frame 0
const CLOSE = 237;           // the door shuts (take 17,4 s, checked frame by frame): the rule fires
const BEEPS_AT = 243;        // the alarm starts
const SPLIT = 291;           // the layout opens: camera left, phone right
const BANNER = 303;          // the notification lands on the phone (alert-book.marks.json: 1,91 s)
// the door's state, checked frame by frame on the constant-rate take (the zone's change also caught him passing in front)
const DOOR_OPEN: [number, number][] = [[14.5, 17.35]];
const tTake = (f: number) => FROM + f / 30;

type Det = { size: [number, number]; frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[]; door: { zone: number[]; open: number[][] } };
const BOOK = [0.6348, 0.7445, 0.6874, 0.7791];   // the detector's median box for the yellow book (all 234 samples)
const ALARM = [0.881, 0.043, 0.916, 0.078];       // the ceiling alarm ("a ceiling sensor", 0,43)
// the beeps in the team's recording (s from its start), from silence detection
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
const beepAt = (s: number) => BEEPS.some(([a, b]) => s >= a && s <= b) ? 1 : 0;

/** A labelled box on the 1920 × 1080 camera picture (normalised coordinates). */
const Box: React.FC<{ b: number[]; label: string; color: string; pad?: number; opacity?: number; thick?: number }> = ({ b, label, color, pad = 0.006, opacity = 1, thick = 4 }) => {
  const x = (b[0] - pad) * 1920, y = (b[1] - pad) * 1080, w = (b[2] - b[0] + 2 * pad) * 1920, h = (b[3] - b[1] + 2 * pad) * 1080;
  return (
    <div style={{ position: "absolute", inset: 0, opacity }}>
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, border: `2px solid ${color}`, borderRadius: 6, opacity: 0.55 }} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <Brackets x={x} y={y} w={w} h={h} arm={Math.min(w, h) * 0.35} stroke={thick} radius={6} color={color} />
      </svg>
      <div style={{ position: "absolute", left: x, top: y - 40, padding: "4px 10px", borderRadius: 7, background: color, color: "#fff",
        fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 22, whiteSpace: "nowrap" }}>{label}</div>
    </div>
  );
};

/** The camera picture with the detector's boxes and the alarm, in its own 1920 × 1080 space. */
const Camera: React.FC = () => {
  const frame = useCurrentFrame();
  const det = useJson<Det>("takes/scene1/book-leave.boxes.json");
  const t = tTake(frame);
  const fired = frame >= CLOSE;
  const beep = frame >= BEEPS_AT ? beepAt((frame - BEEPS_AT) / 30) : 0;
  // the person: the detector's best box, between its samples
  let person: number[] | null = null;
  if (det && !fired) {
    const s = det.frames.map((f) => ({ t: f.t, b: f.boxes.filter((x) => x.label === "a person" && x.score >= 0.15).sort((p, q) => q.score - p.score)[0] })).filter((x) => x.b);
    const a = [...s].reverse().find((x) => x.t <= t), c = s.find((x) => x.t >= t);
    if (a && c && c.t - a.t < 1.2) {
      const u = c.t > a.t ? (t - a.t) / (c.t - a.t) : 0;
      person = a.b.box.map((v, i) => v + (c.b.box[i] - v) * u);
    }
  }
  const open = DOOR_OPEN.some(([a, b]) => t >= a && t < b);
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, overflow: "hidden", background: "#000" }}>
      <OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round(FROM * 30)} style={{ width: 1920, height: 1080, objectFit: "cover" }} />
      {/* the alarm: the room flushes red on every beep */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(230,30,30,0.10), rgba(200,0,0,0.42))", opacity: fired ? 0.25 + 0.75 * beep : 0 }} />
      {det ? <Box b={det.door.zone} label={open ? "porta aberta" : "porta fechada"} color={open ? "#E8710A" : "rgba(40,48,60,0.92)"} pad={0} thick={3} /> : null}
      {person ? <Box b={person} label="pessoa" color={theme.colors.labs} /> : null}
      <Box b={BOOK} label={fired ? "livro · ficou na mesa" : "livro"} color={fired ? "#D92D20" : theme.colors.labs} pad={0.01} />
      {fired ? <Box b={ALARM} label="alarme" color="#D92D20" pad={0.012} opacity={0.4 + 0.6 * beep} /> : null}
      {fired ? (
        <div style={{ position: "absolute", left: ALARM[0] * 1920 + 33, top: ALARM[1] * 1080 + 38, width: 120, height: 120, transform: "translate(-50%,-50%)",
          borderRadius: "50%", background: "radial-gradient(circle, rgba(255,60,50,0.95), rgba(255,40,40,0.0) 70%)", opacity: beep }} />
      ) : null}
      {/* the rule that is running, and the camera's name */}
      <div style={{ position: "absolute", left: 40, bottom: 36, display: "flex", gap: 12 }}>
        <span style={{ padding: "8px 14px", borderRadius: 10, background: "rgba(16,19,24,0.72)", color: "#fff", fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 24 }}>
          <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 5, background: "#ff3b30", marginRight: 10, verticalAlign: "middle" }} />Câmara · laboratório</span>
        <span style={{ padding: "8px 14px", borderRadius: 10, background: fired ? "#D92D20" : "rgba(16,19,24,0.72)", color: "#fff", fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 24 }}>
          {fired ? "Saiu sem o livro · alarme e aviso enviados" : "Regra ativa: avisar se sair sem o livro"}</span>
      </div>
    </AbsoluteFill>
  );
};

export const Scene1Book: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const split = interpolate(frame, [SPLIT, SPLIT + 20], [0, 1], { ...clamp, easing: theme.ease.inOut });
  // full frame → the prototype page's layout: the camera on the left (1260 px wide), the phone on the right
  const s = 1 - split * (1 - 1260 / 1920);
  const x = 40 * split, y = (1080 - 1080 * s) / 2;
  const phoneIn = interpolate(frame, [SPLIT + 4, SPLIT + 24], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <AbsoluteFill style={{ background: "#0E1116" }}>
      <div style={{ position: "absolute", left: x, top: y, width: 1920, height: 1080, transform: `scale(${s})`, transformOrigin: "0 0", borderRadius: 24 * split / s, overflow: "hidden" }}>
        <Camera />
      </div>
      {frame >= SPLIT ? (
        <div style={{ position: "absolute", right: 70, top: 75, opacity: phoneIn, transform: `translateX(${(1 - phoneIn) * 120}px)` }}>
          <Phone height={930}>
            <Sequence from={SPLIT} layout="none">
              <div style={{ width: 1206, height: 2622, transform: `scale(${(930 * 0.95) / 2622})`, transformOrigin: "0 0" }}>
                <Recording name="alert-book" segs={[[0, 1.5]]} radius={0} />
              </div>
            </Sequence>
          </Phone>
        </div>
      ) : null}
      {frame >= SPLIT + 30 ? (
        <div style={{ position: "absolute", left: 60, top: 970, fontFamily: SERIF, fontSize: 44, color: "#fff", opacity: interpolate(frame, [SPLIT + 30, SPLIT + 33], [0, 1], clamp) }}>
          Saiu sem o livro: o alarme tocou e o aviso chegou ao telemóvel.
        </div>
      ) : null}
      {/* sound: the room, the door shutting, the team's alarm recording, the phone */}
      <Audio src={staticFile("audio/sfx/v4/room-living.wav")} loop volume={0.05} />
      <Sequence from={CLOSE + 1 - Math.round(0.85 * fps)} layout="none"><Audio src={staticFile("audio/sfx/v4/door-1.wav")} volume={0.6} /></Sequence>
      <Sequence from={BEEPS_AT} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")} volume={0.75} /></Sequence>
      <Sequence from={BANNER + 1 - Math.round(0.298 * fps)} layout="none"><Audio src={staticFile("audio/sfx/v4/vib-2.wav")} volume={0.5} /></Sequence>
      <Sequence from={BANNER} layout="none"><Audio src={staticFile("audio/sfx/notify-safety.wav")} volume={0.35} /></Sequence>
    </AbsoluteFill>
  );
};
