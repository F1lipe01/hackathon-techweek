// Real example 1, the book left behind (19 Nov, the lab), v2 after the team's notes.
//   A (0–8 s)    on the phone: the book is registered (the real registration of 18 Nov, video 2's recording) and one
//                sentence sets the rule: the alarm and a message
//   B (8–17,5 s) the lab's kit camera (prototype/record.py) with the prototype's own detector run over it
//                (video/tools/detect_take.py). Boxes by kind: a thing (the book), a person, devices (the alarm, the access
//                point) and the door, drawn along its real edges. When the door shuts with the book on the desk, the
//                alarm device glows red in time with the team's own recording of it beeping.
//   C (17,5–24,5 s) outside: a phone's home screen; the alert drops in, a tap opens it: the camera's picture, large.
// The alarm and the notification are simulated (AGENTS.md rule 1: the real alarm is never touched).
import React from "react";
import { AbsoluteFill, Audio, Freeze, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { Brackets, Phone, clamp } from "../presentation/ui";

const { fontFamily: SERIF } = loadFont("normal", { weights: ["400"], subsets: ["latin", "latin-ext"] });

export const SCENE1_FRAMES = 735;
const A_END = 240, B_END = 525;
const TAKE = "takes/scene1/book-leave.mp4";
const B_FROM = 12.0;                          // take second at the start of part B
const tTake = (f: number) => B_FROM + (f - A_END) / 30;
const CLOSE = A_END + Math.round((17.4 - B_FROM) * 30);   // the door shuts (17,4 s, checked frame by frame)
const BEEPS_AT = CLOSE + 6;
const BANNER = B_END + 15, TAP = B_END + 60;

// what the detector and the frame checks found in this take (normalised to the camera picture)
const BOOK = [0.6348, 0.7445, 0.6874, 0.7791];          // "a yellow book": its median box over all 234 samples
const AP = [0.66, 0.705, 0.693, 0.732];                  // the access point beside it ("a small white box", 0,24)
const ALARM = [0.3135, 0.3023, 0.3243, 0.3115];          // the alarm on the shelf (from the team's screenshot, 0,82 match)
const DOOR: [number, number][] = [[0.339, 0.268], [0.435, 0.289], [0.414, 0.651], [0.321, 0.637]]; // the door leaf's corners
const DOOR_OPEN: [number, number][] = [[14.5, 17.35]];
const BEEPS: [number, number][] = [[0.09, 0.73], [1.08, 1.81], [2.42, 2.69], [3.48, 4.5], [4.79, 6.2]];
const beepAt = (s: number) => BEEPS.some(([a, b]) => s >= a && s <= b) ? 1 : 0;

// one colour per kind, so a thing, a person and a device never look alike
const KIND = { thing: "#2ABE9E", person: "#FFFFFF", device: "#8B7CF6", alarm: "#E5322D", door: "#C9D1DB", open: "#E8710A" };

type Det = { frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[] };

const Label: React.FC<{ x: number; y: number; kind: string; text: string; color: string; dark?: boolean }> = ({ x, y, kind, text, color, dark }) => (
  <div style={{ position: "absolute", left: x, top: y, transform: "translateY(-100%)", marginTop: -6, display: "flex", borderRadius: 7, overflow: "hidden",
    fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 21, whiteSpace: "nowrap", boxShadow: "0 4px 14px -6px rgb(0 0 0 / 0.5)" }}>
    <span style={{ background: "rgba(14,17,22,0.82)", color, padding: "4px 8px" }}>{kind}</span>
    <span style={{ background: color, color: dark ? "#111" : "#fff", padding: "4px 10px" }}>{text}</span>
  </div>
);

const Box: React.FC<{ b: number[]; kind: string; text: string; color: string; pad?: number; dark?: boolean; brackets?: boolean }> = ({ b, kind, text, color, pad = 0.006, dark, brackets = true }) => {
  const x = (b[0] - pad) * 1920, y = (b[1] - pad) * 1080, w = (b[2] - b[0] + 2 * pad) * 1920, h = (b[3] - b[1] + 2 * pad) * 1080;
  return (
    <>
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, border: `2px solid ${color}`, borderRadius: 6, opacity: brackets ? 0.5 : 1 }} />
      {brackets ? <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        <Brackets x={x} y={y} w={w} h={h} arm={Math.min(w, h) * 0.35} stroke={4} radius={6} color={color} /></svg> : null}
      <Label x={x} y={y} kind={kind} text={text} color={color} dark={dark} />
    </>
  );
};

/** Part B: the camera, its boxes by kind, the alarm. */
const Camera: React.FC = () => {
  const frame = useCurrentFrame() + A_END; // the film's frame: this part sits in a Sequence that starts at A_END
  const det = useJson<Det>("takes/scene1/book-leave.boxes.json");
  const t = tTake(frame);
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
  const pts = DOOR.map(([x, y]) => `${x * 1920},${y * 1080}`).join(" ");
  const ax = (ALARM[0] + ALARM[2]) / 2 * 1920, ay = (ALARM[1] + ALARM[3]) / 2 * 1080;
  return (
    <AbsoluteFill style={{ width: 1920, height: 1080, overflow: "hidden", background: "#000" }}>
      <OffthreadVideo src={staticFile(TAKE)} muted trimBefore={Math.round(B_FROM * 30)} style={{ width: 1920, height: 1080, objectFit: "cover" }} />
      {/* a faint red on the room while the alarm sounds, the glow on the alarm itself */}
      <AbsoluteFill style={{ boxShadow: "inset 0 0 0 6px rgba(229,50,45,0.9)", background: "rgba(229,50,45,0.06)", opacity: fired ? 0.35 + 0.65 * beep : 0 }} />
      {fired ? <div style={{ position: "absolute", left: ax, top: ay, width: 150, height: 150, transform: "translate(-50%,-50%)", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(255,70,60,0.95) 0%, rgba(255,50,45,0.45) 30%, rgba(255,40,40,0) 70%)", opacity: beep }} /> : null}
      {/* the door, along its real edges */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <polygon points={pts} fill={open ? "rgba(232,113,10,0.10)" : "none"} stroke={doorColor} strokeWidth={3} strokeLinejoin="round" opacity={0.9} />
      </svg>
      <Label x={DOOR[3][0] * 1920 + 8} y={DOOR[3][1] * 1080 - 14} kind="porta" text={open ? "aberta" : "fechada"} color={doorColor} dark={!open} />
      {person ? <Box b={person} kind="pessoa" text="1" color={KIND.person} dark /> : null}
      <Box b={BOOK} kind="coisa" text={fired ? "livro · ficou na mesa" : "livro"} color={fired ? KIND.alarm : KIND.thing} pad={0.01} />
      <Box b={AP} kind="dispositivo" text="ponto de acesso" color={KIND.device} pad={0.006} brackets={false} />
      <Box b={ALARM} kind="dispositivo" text={fired ? "alarme · a tocar" : "alarme"} color={fired ? KIND.alarm : KIND.device} pad={0.008} brackets={false} />
      {/* the rule, the camera, the legend */}
      <div style={{ position: "absolute", left: 36, bottom: 32, display: "flex", gap: 12, fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 23 }}>
        <span style={{ padding: "8px 14px", borderRadius: 10, background: "rgba(14,17,22,0.78)", color: "#fff" }}>
          <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 5, background: "#ff3b30", marginRight: 10, verticalAlign: "middle" }} />Câmara · laboratório</span>
        <span style={{ padding: "8px 14px", borderRadius: 10, background: fired ? KIND.alarm : "rgba(14,17,22,0.78)", color: "#fff" }}>
          {fired ? "Saiu sem o livro: alarme e mensagem" : "Regra: sair sem o livro → alarme e mensagem"}</span>
      </div>
      <div style={{ position: "absolute", right: 36, bottom: 32, display: "flex", gap: 18, padding: "8px 14px", borderRadius: 10, background: "rgba(14,17,22,0.78)",
        fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 21, color: "#fff" }}>
        {([["coisa", KIND.thing], ["pessoa", KIND.person], ["dispositivo", KIND.device]] as const).map(([k, c]) => (
          <span key={k}><span style={{ display: "inline-block", width: 12, height: 12, borderRadius: 3, background: c, marginRight: 8, verticalAlign: "middle" }} />{k}</span>))}
      </div>
    </AbsoluteFill>
  );
};

/** A phone in the right column, its screen given in the app's own pixels (1206 × 2622). */
const PhoneAt: React.FC<{ children: React.ReactNode; height?: number }> = ({ children, height = 940 }) => (
  <div style={{ position: "absolute", right: 210, top: (1080 - height) / 2 }}>
    <Phone height={height}>
      <div style={{ width: 1206, height: 2622, transform: `scale(${(height * 0.95) / 2622})`, transformOrigin: "0 0" }}>{children}</div>
    </Phone>
  </div>
);
const Rec: React.FC<{ src: string; from: number; rate?: number; freeze?: number }> = ({ src, from, rate = 1, freeze }) => {
  const frame = useCurrentFrame();
  const v = <OffthreadVideo src={staticFile(src)} muted trimBefore={Math.round(from * 30)} playbackRate={rate} style={{ width: 1206, height: 2622 }} />;
  return freeze !== undefined && frame >= freeze ? <Freeze frame={freeze}>{v}</Freeze> : v;
};
const Title: React.FC<{ text: string; sub?: string; at?: number }> = ({ text, sub, at = 4 }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [at, at + 3], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 140, top: 420, width: 760, opacity: o }}>
      <div style={{ fontFamily: SERIF, fontSize: 64, lineHeight: 1.1, color: "#fff", letterSpacing: "-0.015em" }}>{text}</div>
      {sub ? <div style={{ fontFamily: theme.fonts.display, fontSize: 26, color: "#9AA3AE", marginTop: 18 }}>{sub}</div> : null}
    </div>
  );
};

/** Part C: an ordinary phone home screen (drawn, no real apps), the alert dropping in, the tap that opens it. */
const HomeScreen: React.FC = () => {
  const frame = useCurrentFrame();
  const drop = interpolate(frame, [BANNER - B_END, BANNER - B_END + 10], [-260, 0], { ...clamp, easing: theme.ease.out });
  const icons = ["#5B8DEF", "#F2A541", "#4CC38A", "#E5646E", "#8E7CF6", "#3BB3C3", "#F07F3C", "#6C7A89", "#D4A017", "#5AA469", "#C25B9A", "#4A6FA5", "#E08E45", "#7FB069", "#B56576", "#3D8BFD"];
  return (
    <div style={{ position: "absolute", inset: 0, background: "linear-gradient(160deg, #2B4C7E 0%, #1E2A44 55%, #10151F 100%)" }}>
      <div style={{ position: "absolute", left: 110, top: 70, fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 52, color: "#fff" }}>14:10</div>
      <div style={{ position: "absolute", left: 90, right: 90, top: 330, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", rowGap: 110, justifyItems: "center" }}>
        {icons.map((c, i) => <div key={i} style={{ width: 190, height: 190, borderRadius: 46, background: c, opacity: 0.92 }} />)}
      </div>
      <div style={{ position: "absolute", left: 60, right: 60, bottom: 70, height: 250, borderRadius: 70, background: "rgba(255,255,255,0.16)", display: "flex",
        justifyContent: "space-around", alignItems: "center" }}>
        {["#4CC38A", "#5B8DEF", "#F2A541", "#E5646E"].map((c, i) => <div key={i} style={{ width: 190, height: 190, borderRadius: 46, background: c }} />)}
      </div>
      {frame >= BANNER - B_END - 1 ? (
        <div style={{ position: "absolute", left: 40, right: 40, top: 150, transform: `translateY(${drop}px)`, borderRadius: 60, background: "rgba(246,247,249,0.97)",
          padding: "44px 46px", display: "grid", gridTemplateColumns: "150px 1fr", columnGap: 36, alignItems: "center", boxShadow: "0 30px 80px -30px rgb(0 0 0 / 0.6)" }}>
          <img src={staticFile("v7/notify-book.jpg")} style={{ width: 150, height: 150, borderRadius: 30, objectFit: "cover" }} />
          <div style={{ fontFamily: theme.fonts.display, color: "#1a2233" }}>
            <div style={{ fontWeight: 700, fontSize: 46 }}>Altice Home · Left without the book</div>
            <div style={{ fontSize: 42, marginTop: 10, color: "#3a4352" }}>The door closed and your book is still on the desk. The alarm is on.</div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export const Scene1Book: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const open = interpolate(frame, [TAP, TAP + 10], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const finger = frame >= TAP - 12 && frame < TAP + 8;
  return (
    <AbsoluteFill style={{ background: "#0E1116" }}>
      {/* A: the book registered, then the rule */}
      <Sequence from={0} durationInFrames={90}>
        <PhoneAt><Rec src="footage/app-book.mp4" from={12.4} rate={3} /></PhoneAt>
        <Title text="Mostra-se o livro à câmara." sub="O registo real, no protótipo" />
      </Sequence>
      <Sequence from={90} durationInFrames={102}>
        <PhoneAt><Rec src="app/rule-book.mp4" from={4.4} rate={2} /></PhoneAt>
        <Title text="Uma frase cria a regra." sub="Sair sem o livro → alarme e mensagem" />
      </Sequence>
      <Sequence from={192} durationInFrames={48}>
        <PhoneAt><Rec src="app/rule-book.mp4" from={11.2} /></PhoneAt>
        <Title text="Uma frase cria a regra." sub="Sair sem o livro → alarme e mensagem" at={-10} />
      </Sequence>
      {/* B: the lab */}
      <Sequence from={A_END} durationInFrames={B_END - A_END}><Camera /></Sequence>
      {/* C: outside, the phone */}
      <Sequence from={B_END}>
        <PhoneAt>
          <HomeScreen />
          {frame >= TAP ? (
            <div style={{ position: "absolute", inset: 0, opacity: open, transform: `scale(${0.6 + 0.4 * open})`, transformOrigin: "50% 12%", borderRadius: 120 * (1 - open), overflow: "hidden" }}>
              <Sequence from={TAP - B_END} layout="none"><Rec src="app/alert-book-open.mp4" from={4.15} freeze={0} /></Sequence>
            </div>
          ) : null}
          {finger ? <div style={{ position: "absolute", left: 560, top: 300, width: 120, height: 120, borderRadius: 60, background: "rgba(26,34,51,0.28)",
            border: "5px solid rgba(255,255,255,0.9)", transform: `scale(${frame >= TAP ? 0.8 : 1})` }} /> : null}
        </PhoneAt>
        <Title text="Lá fora, o telemóvel avisa." sub="Toca-se no aviso e vê-se o que a câmara viu" />
      </Sequence>
      {/* sound: the send tap, the team's alarm recording (fainter outside), the phone's buzz, the tap that opens the alert */}
      <Sequence from={188} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.4} /></Sequence>
      <Sequence from={BEEPS_AT} layout="none"><Audio src={staticFile("audio/sfx/scene1/alarm-beep.wav")}
        volume={(f) => 0.7 * (BEEPS_AT + f < B_END ? 1 : 0.25)} /></Sequence>
      <Sequence from={BANNER + 1 - Math.round(0.298 * fps)} layout="none"><Audio src={staticFile("audio/sfx/v4/vib-2.wav")} volume={0.55} /></Sequence>
      <Sequence from={TAP} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-2.wav")} volume={0.45} /></Sequence>
    </AbsoluteFill>
  );
};
