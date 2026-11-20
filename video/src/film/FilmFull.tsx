// The full film (20 Nov), about 90 s: the three examples' key moments, joined by fast cards, with ONE app that is built
// up from nothing as the film goes. The app is recorded for real against a private server that started empty, in story
// order (record_app.mjs full-1, full-2, ex3-scenarios -> public/app/full/): nobody and nothing is registered at the
// start; Mushahid (from one photo), the book (8 photos), its link to Mushahid and its scenario come in example 1;
// Filipe (a face video) and Home security in example 2; the two presence scenarios in example 3. Every later screen
// shows what came before. The lab parts are the three films' own (Scene1Book, Scene2Face, Scene3People), cut where the
// room is empty, with their own overlays (docs/24-what-is-real.md); their music is off and this film has one bed.
import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, interpolateColors, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { clamp } from "../presentation/ui";
import { S23 as EndCard } from "../presentation/shots/End";
import { ACCENT, CX, Cursor, Grain, INK, PAPER, PhoneAt, REC_Y, Rec, SANS, SERIF, Scene1Book, Way, ez, lerp, scr } from "./Scene1Book";
import { Scene2Face } from "./Scene2Face";
import { Scene3People } from "./Scene3People";

type Kind = "app" | "photos" | "selfie";
type Pc = { kind: Kind; from: number; to: number; rate: number };
type Laid = Pc & { start: number; end: number };
const lay = (at: number, pcs: Pc[]): Laid[] => {
  let s = at;
  return pcs.map((p) => { const len = Math.round(((p.to - p.from) / p.rate) * 30); const o = { ...p, start: s, end: s + len }; s += len; return o; });
};
/** The film frame of an app take's second t (the app pieces only); null if that moment is cut. */
const frOf = (ps: Laid[], t: number) => { const p = ps.find((x) => x.kind === "app" && t >= x.from && t <= x.to); return p ? Math.round(p.start + ((t - p.from) / p.rate) * 30) : null; };
type Tap = readonly [number, number, number];   // take second, x, y (app points, from the take's marks.json)
const waysOf = (ps: Laid[], taps: Tap[]): Way[] => taps.flatMap(([t, x, y]) => { const f = frOf(ps, t); return f === null ? [] : [{ f, x: x * 3, y: y * 3 + REC_Y, press: true }]; });

/* ------------------------------------------------------------------ the timeline (30 fps) */
const S1 = 0;
const P1 = lay(S1, [
  { kind: "app", from: 0.5, to: 2.25, rate: 1 },       // Things: nothing yet (the first card lifts off it)
  { kind: "app", from: 2.2, to: 13.95, rate: 3.5 },    // + › Person › Choose a photo › Mushahid › Save › "Mushahid added"
  { kind: "app", from: 13.95, to: 19.98, rate: 3 },    // Things (Mushahid) › + › Book › Take photos
  { kind: "photos", from: 0.9, to: 36.5, rate: 10 },   // the colleague's camera: the 8 photos, sped up, in one go
  { kind: "app", from: 20.68, to: 26.53, rate: 3 },    // the photos in the app, the name, Save
  { kind: "app", from: 26.53, to: 32.75, rate: 1.6 },  // "Link to Mushahid?" › Yes › "Belongs to Mushahid" › Create
  { kind: "app", from: 34.8, to: 40.63, rate: 3 },     // the sentence typed › Save
  { kind: "app", from: 43.2, to: 44.6, rate: 1.4 },    // "Scenario saved": Book left at home
]);
const TAPS1: Tap[] = [[2.397, 249, 90], [4.277, 201, 525.6], [6.251, 201, 565.7], [8.571, 201, 463.8], [10.487, 201, 664], [13.773, 201, 442.1],
  [15.951, 249, 90], [17.8, 201, 613.6], [19.788, 201, 455.3], [22.662, 201, 463.8], [24.255, 201, 573.5], [26.337, 201, 772.3], [29.224, 201, 587.6],
  [32.703, 116, 496.1], [40.435, 201, 436]];   // full-1.marks.json
const L1A = { at: P1[7].end, src0: 1160, len: 95 }, L1B = { at: P1[7].end + 95, src0: 1362, len: 278 };   // Scene1Book: he leaves, the door shuts; the alarm, the alert, turned off
const S2 = L1B.at + L1B.len;
const P2 = lay(S2, [
  { kind: "app", from: 1.0, to: 2.2, rate: 1 },        // Things: Mushahid, the book (his), Book left at home
  { kind: "app", from: 2.2, to: 10.25, rate: 3.2 },    // + › Person › Record a face video › Filipe › Record their face
  { kind: "selfie", from: 0.2, to: 8.4, rate: 2.6 },   // the face video, the one the app received
  { kind: "app", from: 11.45, to: 16.6, rate: 2.6 },   // saving › "Filipe added"
  { kind: "app", from: 16.6, to: 24.7, rate: 2.8 },    // Continue › Home security (Mushahid, Filipe) › Turn on › saved
  { kind: "app", from: 27.1, to: 29.9, rate: 1.4 },    // Done › Things: Family (2)
]);
const TAPS2: Tap[] = [[2.396, 249, 90], [4.272, 201, 525.6], [6.253, 201, 433.7], [8.133, 201, 306.8], [10.064, 201, 507], [18.903, 201, 520.1],
  [21.784, 116, 419.6], [27.17, 201, 607.7]];   // full-2.marks.json
const L2A = { at: P2[5].end, src0: 1075, len: 140 }, L2B = { at: P2[5].end + 140, src0: 1548, len: 402 };   // Scene2Face: Filipe recognised; the stranger, the book, the alarm, the alert
const S3 = L2B.at + L2B.len;
const P3 = lay(S3, [
  { kind: "app", from: 1.0, to: 2.2, rate: 1 },        // Things: Mushahid, Filipe, the book, two scenarios
  { kind: "app", from: 2.2, to: 8.2, rate: 3 },        // Menu › Scenarios › Add scenario
  { kind: "app", from: 8.2, to: 13.5, rate: 2.6 },     // "If nobody is home and something is on…" › Save
  { kind: "app", from: 13.5, to: 15.0, rate: 1.5 },    // saved: Power saving
  { kind: "app", from: 16.7, to: 21.0, rate: 3 },      // Done › Add scenario
  { kind: "app", from: 21.0, to: 27.2, rate: 2.8 },    // "If the door is left open when nobody is home…" › Save
  { kind: "app", from: 27.2, to: 28.6, rate: 1.5 },    // saved: Door left open
]);
const TAPS3: Tap[] = [[2.39, 357, 808.5], [4.253, 201, 212.3], [6.216, 201, 785], [8.062, 201, 228], [13.298, 201, 344], [16.766, 201, 586.7],
  [18.917, 201, 785], [20.782, 201, 228], [26.921, 201, 344]];   // full-3.marks.json (ex3-scenarios)
const L3A = { at: P3[6].end, src0: 1450, len: 90 }, L3B = { at: P3[6].end + 90, src0: 1900, len: 540 };   // Scene3People: the last ones leave; nobody home, the alarm, the alert, Yes, Yes
const END = L3B.at + L3B.len;
export const FULL_FRAMES = END + 120;

/* ------------------------------------------------------------------ the camera over the page (a dive in example 1) */
type CK = { at: number; s: number; x: number; y: number };
const H0 = { s: 1, x: 960, y: 540 };
const WHO = scr(CX.right, 603, 1000 + REC_Y);
const OWNED = frOf(P1, 29.42)!;
const CAM: CK[] = [{ at: 0, ...H0 }, { at: OWNED - 2, ...H0 }, { at: OWNED + 16, s: 1.9, ...WHO }, { at: P1[5].end - 14, s: 1.9, ...WHO }, { at: P1[5].end + 4, ...H0 }, { at: 99999, ...H0 }];
const camAt = (f: number) => {
  let i = 0;
  while (i < CAM.length - 2 && f >= CAM[i + 1].at) i++;
  const a = CAM[i], b = CAM[i + 1], u = ez(f, a.at, b.at);
  return { s: Math.exp(lerp(Math.log(a.s), Math.log(b.s), u)), x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u) };
};
const camCss = (f: number) => { const c = camAt(f); return `translate(960px,540px) scale(${c.s}) translate(${-c.x}px,${-c.y}px)`; };

/** A serif line streamed word by word, as in the three films; it steps aside while the camera dives. */
const Line: React.FC<{ text: string; from: number; to: number; top?: number; left?: number; size?: number; width?: number }> = ({ text, from, to, top = 400, left = 150, size = 80, width = 860 }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const dive = Math.max(0, Math.min(1, (camAt(f).s - 1.03) / 0.25));
  const fade = interpolate(f, [to - 8, to], [1, 0], clamp) * (1 - dive);
  return (
    <div style={{ position: "absolute", left, top, width, opacity: fade, fontFamily: SERIF, fontSize: size, lineHeight: 1.13, letterSpacing: "-0.015em" }}>
      {text.split(" ").map((w, k) => { const a = from + 3 + 2 * k;
        return <span key={k} style={{ opacity: interpolate(f, [a, a + 4], [0, 1], clamp), color: interpolateColors(f, [a, a + 14], [ACCENT, INK]) }}>{w} </span>; })}
    </div>
  );
};

/* ------------------------------------------------------------------ the phone's screen: the take's pieces in order */
const Screen: React.FC<{ src: string; ps: Laid[]; taps: Tap[] }> = ({ src, ps, taps }) => {
  const f = useCurrentFrame();
  const first = ps[0].start, last = ps[ps.length - 1].end;
  const inserts = ps.filter((p) => p.kind !== "app").map((p) => [p.start, p.end - 1] as [number, number]);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {ps.map((p, i) => (f >= p.start - 1 && f < p.end + 1 ? (
        <Sequence key={i} from={p.start} durationInFrames={p.end - p.start + (i === ps.length - 1 ? 200 : 1)} layout="none">
          {p.kind === "app" ? <AbsoluteFill style={{ background: "#EEF3FB" }}><Rec src={src} from={p.from} rate={p.rate} /></AbsoluteFill>
            : p.kind === "photos" ? <AbsoluteFill style={{ background: "#000" }}><Rec src="footage/phone-photos.mp4" from={p.from} rate={p.rate} w={1236} h={2680} top={0} /></AbsoluteFill>
            : <AbsoluteFill style={{ background: "#000", transform: "scaleX(-1)" }}><Rec src="phone/person/selfie-a.mp4" from={p.from} rate={p.rate} w={1508} h={2680} top={0} /></AbsoluteFill>}
        </Sequence>) : null))}
      <Cursor ways={waysOf(ps, taps)} show={[first + 4, last]} hide={inserts} />
    </AbsoluteFill>
  );
};
const AppPart: React.FC<{ src: string; ps: Laid[]; taps: Tap[]; time: string }> = ({ src, ps, taps, time }) => {
  const f = useCurrentFrame();
  const first = ps[0].start, last = ps[ps.length - 1].end;
  if (f < first || f >= last + 10) return null;
  const ins = ps.some((p) => p.kind !== "app" && f >= p.start && f < p.end);
  return <PhoneAt cx={CX.right} bars={{ mode: ins ? "none" : "app", time }}><Screen src={src} ps={ps} taps={taps} /></PhoneAt>;
};

/* ------------------------------------------------------------------ the lab: a film's own frames, from src0 */
const LabPart: React.FC<{ at: number; src0: number; len: number; scene: 1 | 2 | 3; fadeIn?: boolean }> = ({ at, src0, len, scene, fadeIn }) => {
  const f = useCurrentFrame();
  const C = scene === 1 ? Scene1Book : scene === 2 ? Scene2Face : Scene3People;
  return (
    <Sequence from={at} durationInFrames={len}>
      <AbsoluteFill style={{ opacity: fadeIn ? ez(f, at, at + 8) : 1 }}>
        <Sequence from={-src0}><C music={false} /></Sequence>
      </AbsoluteFill>
    </Sequence>
  );
};

/* ------------------------------------------------------------------ the cards between the examples (about 1 s) */
const TITLES = ["", "O livro do Mushahid", "Alguém que não é de casa", "Ninguém em casa"];
const Card: React.FC<{ at: number; n: number; first?: boolean; end?: boolean }> = ({ at, n, first, end }) => {
  const f = useCurrentFrame();
  if (f < at - 14 || f > at + 18) return null;
  const inX = first ? 0 : 1920 * (1 - ez(f, at - 14, at - 3, theme.ease.out));
  const outX = end ? 0 : -1920 * ez(f, at + 7, at + 18, theme.ease.in);
  const x = inX + outX;
  const txt = ez(f, at - 8, at + 2, theme.ease.out);
  return (
    <AbsoluteFill style={{ transform: `translateX(${x}px)`, background: PAPER, boxShadow: "0 0 80px rgba(40,30,15,0.35)" }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 14, background: ACCENT }} />
      {end ? null : <div style={{ position: "absolute", left: 0, width: 1920, top: 395, textAlign: "center", opacity: first ? 1 : txt, transform: `translateY(${(first ? 0 : 1 - txt) * 24}px)` }}>
        <div style={{ fontFamily: SANS, fontSize: 28, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: "#7A756C" }}>Exemplo {n} de 3</div>
        <div style={{ fontFamily: SERIF, fontSize: 112, color: INK, marginTop: 18, letterSpacing: "-0.015em" }}>{TITLES[n]}</div>
      </div>}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ sound */
const SHOT = [1.3, 7.83, 11.17, 16.2, 23.03, 27.27, 31.8, 36.1];   // the colleague's 8 shutter presses (phone-photos)
const typing = (ps: Laid[], a: number, b: number) => { const fa = frOf(ps, a), fb = frOf(ps, b); if (fa === null || fb === null) return []; const r: number[] = []; for (let x = fa; x < fb; x += 2) r.push(x); return r; };
const KEYS = [...typing(P1, 8.6, 9.3), ...typing(P1, 22.7, 23.2), ...typing(P1, 24.3, 25.3), ...typing(P1, 34.8, 39.25), ...typing(P2, 8.15, 8.75),
  ...typing(P3, 8.1, 11.9), ...typing(P3, 20.8, 25.5)];
const SUCCESS = [frOf(P1, 11.48), frOf(P1, 29.42), P1[7].start, frOf(P2, 16.42), frOf(P2, 24.28), P3[3].start, P3[6].start].filter((x): x is number => x !== null);
const LABS = [L1B, L2B, L3B];
const Sound: React.FC = () => {
  const taps = [...waysOf(P1, TAPS1), ...waysOf(P2, TAPS2), ...waysOf(P3, TAPS3)].map((w) => w.f);
  const shutters = SHOT.map((t) => Math.round(P1[3].start + ((t - P1[3].from) / P1[3].rate) * 30));
  const whoosh: [number, string, number][] = [[S2, "fast", 0.08], [S3, "fast", 0.08], [END, "fast", 0.08], [L1A.at, "riser-soft", 0.12], [L2A.at, "riser-soft", 0.12],
    [L3A.at, "riser-soft", 0.12], [OWNED + 7, "zoom-soft", 0.8], [END + 6, "riser-soft", 0.15], [END + 23, "slow-gentle", 0.28], [END + 68, "zoom-soft", 0.6]];
  const PEAK: Record<string, number> = { "slow-gentle": 0.28, "zoom-soft": 0.37, fast: 0.15, "riser-soft": 0.43 };
  const lab = (v: number) => (LABS.some((l) => v >= l.at + 30 && v < l.at + l.len - 10) ? 0.55 : 1);
  return (
    <>
      <Audio src={staticFile("audio/music/bed-real-long.wav")} volume={(v) => 0.45 * lab(v) * interpolate(v, [0, 15, FULL_FRAMES - 20, FULL_FRAMES], [0, 1, 1.3, 0], clamp)} />
      {whoosh.map(([peak, n, vol], i) => <Sequence key={`w${i}`} from={Math.max(0, Math.round(peak - PEAK[n] * 30))} layout="none"><Audio src={staticFile(`audio/sfx/whoosh/${n}.wav`)} volume={vol} /></Sequence>)}
      {taps.map((a, i) => <Sequence key={`t${i}`} from={a} layout="none"><Audio src={staticFile("audio/sfx/v4/tap-1.wav")} volume={0.13} /></Sequence>)}
      {shutters.map((a, i) => <Sequence key={`s${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/v4/shutter-${i % 2 ? 3 : 2}.wav`)} volume={0.2} /></Sequence>)}
      {KEYS.map((a, i) => <Sequence key={`k${i}`} from={a} layout="none"><Audio src={staticFile(`audio/sfx/ui/key-${((i * 5) % 12) + 1}.wav`)} volume={0.11} /></Sequence>)}
      {SUCCESS.map((a, i) => <Sequence key={`ok${i}`} from={Math.max(0, a - 9)} layout="none"><Audio src={staticFile("audio/sfx/ui/ui-success.wav")} volume={0.28} /></Sequence>)}
    </>
  );
};

/* ------------------------------------------------------------------ the film */
export const FilmFull: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill style={{ transform: camCss(f), transformOrigin: "0 0" }}>
        <AppPart src="app/full/full-1.mp4" ps={P1} taps={TAPS1} time="15:52" />
        <AppPart src="app/full/full-2.mp4" ps={P2} taps={TAPS2} time="16:21" />
        <AppPart src="app/full/full-3.mp4" ps={P3} taps={TAPS3} time="17:28" />
        <Line text="Junta-se o Mushahid, com uma foto." from={P1[0].start + 18} to={P1[2].start + 4} />
        <Line text="Fotografa-se o livro." from={P1[2].start + 6} to={P1[5].start} />
        <Line text="De quem é? Do Mushahid." from={P1[5].start + 2} to={P1[6].start} />
        <Line text="Uma frase cria o cenário." from={P1[6].start + 2} to={P1[7].end} />
        <Line text="O Filipe junta-se com um vídeo da cara." from={P2[0].start + 14} to={P2[4].start} />
        <Line text="A app sugere a segurança da casa." from={P2[4].start + 2} to={P2[5].end} />
        <Line text="Duas frases, dois cenários." from={P3[0].start + 14} to={P3[6].end} />
      </AbsoluteFill>
      <LabPart at={L1A.at} src0={L1A.src0} len={L1A.len} scene={1} fadeIn />
      <LabPart at={L1B.at} src0={L1B.src0} len={L1B.len} scene={1} />
      <LabPart at={L2A.at} src0={L2A.src0} len={L2A.len} scene={2} fadeIn />
      <LabPart at={L2B.at} src0={L2B.src0} len={L2B.len} scene={2} />
      <LabPart at={L3A.at} src0={L3A.src0} len={L3A.len} scene={3} fadeIn />
      <LabPart at={L3B.at} src0={L3B.src0} len={L3B.len} scene={3} />
      <Card at={14} n={1} first />
      <Card at={S2} n={2} />
      <Card at={S3} n={3} />
      {f >= END - 14 && f < END ? <Card at={END} n={0} end /> : null}
      {f >= END ? <Sequence from={END} layout="none"><EndCard bg={PAPER} /></Sequence> : null}
      <Grain />
      <Sound />
    </AbsoluteFill>
  );
};
