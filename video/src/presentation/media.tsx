// Footage, stills, real app recordings and hand-placed boxes for video 1 (storyboard v5.1).
// - Clip: a stock clip filling the frame from a given second, optionally frozen after n frames, with a slow push.
// - ScreenInsert: a stock clip of a hand-held phone with a real recording of the prototype mapped onto its tracked screen
//   (public/stock/screens/*.json), and a camera that can push in until the app is readable, locking onto the screen.
// - AppView: a real recording shown flat and large, the camera on the element the beat is about.
// - FrameBox: a box placed by hand on the object's real edges, keyframed, with its name on it.
import React from "react";
import { AbsoluteFill, Freeze, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { useJson } from "./assets";
import { Brackets, clamp, ramp } from "./ui";
import { alpha } from "./tokens";
import { camera, coverFit, homography, lerp, lerpPt, type Pt, type Quad } from "./geom";

export const STOCK: Record<string, { w: number; h: number }> = {
  "leaving-home-keys-1": { w: 3840, h: 2160 }, "dog-bowl-2": { w: 3840, h: 2160 }, "elderly-tea-2": { w: 3840, h: 2026 },
  "parcel-door-1": { w: 3840, h: 2160 }, "phone-alert-1": { w: 1920, h: 1080 }, "phone-alert-2": { w: 2560, h: 1440 },
  "phone-alert-3": { w: 1920, h: 1080 }, "leaving-home-1": { w: 2560, h: 1440 }, "cat-counter-2": { w: 3840, h: 2160 },
  "elderly-reading-1": { w: 3840, h: 2026 }, "older-kitchen-1": { w: 3840, h: 2026 }, "garden-night-2": { w: 1920, h: 1080 },
};

/** Source pixels of a clip → frame pixels (object-fit: cover). */
export const toFrame = (clip: string) => {
  const s = STOCK[clip];
  const { k, ox, oy } = coverFit(s.w, s.h);
  return (x: number, y: number): Pt => ({ x: ox + x * k, y: oy + y * k });
};

/** The daylight grade on footage: lifted a little, never moody. */
const GRADE = "brightness(1.05) saturate(1.04) contrast(0.98)";

const VideoLayer: React.FC<{ src: string; from: number; play?: number; style?: React.CSSProperties; muted?: boolean }> = ({ src, from, play, style }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const v = (
    <OffthreadVideo src={staticFile(src)} muted trimBefore={Math.round(from * fps)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", ...style }} />
  );
  if (play !== undefined && frame >= play) return <Freeze frame={play}>{v}</Freeze>;
  return v;
};

/** A stock clip filling the frame from `from` seconds; it freezes after `play` frames if given. `push` is the slow push. */
export const Clip: React.FC<{ clip: string; from: number; play?: number; push?: [number, number]; origin?: string; grade?: string; children?: React.ReactNode }> = ({
  clip, from, play, push = [1, 1.03], origin = "50% 50%", grade = GRADE, children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const s = interpolate(frame, [0, durationInFrames], push, clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: theme.colors.bg }}>
      <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: origin }}>
        <AbsoluteFill style={{ filter: grade }}>
          <VideoLayer src={`stock/${clip}.mp4`} from={from} play={play} />
        </AbsoluteFill>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ boxes placed by hand */

/** A box keyframed by hand on the object's edges: [clip second, x1, y1, x2, y2] in the clip's source pixels. */
export type BoxKey = [number, number, number, number, number];

const smooth = (u: number) => u * u * (3 - 2 * u); // eased between keys, so a box never jerks at a key

export const boxAt = (keys: BoxKey[], t: number) => {
  let i = 0;
  while (i < keys.length - 2 && keys[i + 1][0] <= t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const u = b[0] > a[0] ? smooth(Math.min(1, Math.max(0, (t - a[0]) / (b[0] - a[0])))) : 0;
  return [1, 2, 3, 4].map((j) => lerp(a[j], b[j], u)) as [number, number, number, number];
};

/**
 * A detection box: corners close in from a wider frame onto the object (a spring, no overshoot past the edges), then the
 * label wipes out of the top-left corner. Drawn in frame pixels; place it inside the same transform as the footage.
 */
export const FrameBox: React.FC<{ clip: string; keys: BoxKey[]; clipFrom: number; at: number; label: string; outAt?: number; color?: string; labelSize?: number }> = ({
  clip, keys, clipFrom, at, label, outAt, color = theme.colors.labs, labelSize = 24,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < at) return null;
  const [x1, y1, x2, y2] = boxAt(keys, clipFrom + frame / fps);
  const f = toFrame(clip);
  const A = f(x1, y1), B = f(x2, y2);
  const p = spring({ frame: frame - at, fps, config: { damping: 22, stiffness: 170, mass: 0.7 } });
  const grow = 0.22 * (1 - p);
  const w = B.x - A.x, h = B.y - A.y;
  const x = A.x - (w * grow) / 2, y = A.y - (h * grow) / 2, W = w * (1 + grow), H = h * (1 + grow);
  const lab = ramp(frame - at, 5, 15, theme.ease.out);
  const out = outAt !== undefined ? ramp(frame, outAt, outAt + 6, theme.ease.in) : 0;
  const arm = Math.min(W, H) * 0.24;
  const inside = A.y - labelSize * 1.9 < 6;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: interpolate(p, [0, 0.35], [0, 1], clamp) * (1 - out) }}>
      <div style={{ position: "absolute", left: x, top: y, width: W, height: H, border: `2px solid ${alpha(color, 0.5)}`, borderRadius: 8 }} />
      <Brackets x={x} y={y} w={W} h={H} arm={arm} stroke={5} radius={8} color={color} />
      <div
        style={{
          position: "absolute", left: A.x, top: inside ? A.y + 12 : A.y - labelSize * 1.75, padding: `${labelSize * 0.22}px ${labelSize * 0.5}px`,
          borderRadius: 8, background: color, color: theme.colors.white, fontFamily: theme.fonts.display, fontSize: labelSize, fontWeight: 600,
          whiteSpace: "nowrap", clipPath: `inset(0 ${100 - 100 * lab}% 0 0)`, marginLeft: inside ? 12 : 0,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};

/** A small chip on footage (a time, "porta aberta"): fades in, sits still. */
export const Chip: React.FC<{ at: number; text: string; x: number; y: number; color?: string; turnAt?: number; turnText?: string; size?: number }> = ({
  at, text, x, y, color = theme.colors.ink, turnAt, turnText, size = 28,
}) => {
  const frame = useCurrentFrame();
  if (frame < at) return null;
  const turned = turnAt !== undefined && frame >= turnAt;
  const k = turnAt !== undefined ? ramp(frame, turnAt, turnAt + 8, theme.ease.out) : 0;
  return (
    <div
      style={{
        position: "absolute", left: x, top: y, padding: `${size * 0.28}px ${size * 0.6}px`, borderRadius: 10,
        background: turned ? theme.colors.alert : alpha(theme.colors.white, 0.94), color: turned ? theme.colors.white : color,
        fontFamily: theme.fonts.display, fontSize: size, fontWeight: 600, letterSpacing: "0.01em", fontVariantNumeric: "tabular-nums",
        boxShadow: `0 8px 24px -10px ${alpha(theme.colors.ink, 0.35)}`, opacity: ramp(frame, at, at + 6, theme.ease.out),
        transform: `scale(${1 + 0.06 * Math.sin(Math.PI * k)})`,
      }}
    >
      {turned ? turnText ?? text : text}
    </div>
  );
};

/** A small honesty tag in a corner: "a filmar" (preview only: footage we film on Thursday), "conceito". */
export const Tag: React.FC<{ text: string; dark?: boolean; corner?: "br" | "tr" }> = ({ text, dark, corner = "br" }) => (
  <div
    style={{
      position: "absolute", right: 28, ...(corner === "br" ? { bottom: 24 } : { top: 24 }), padding: "6px 12px", borderRadius: 8, fontFamily: theme.fonts.mono, fontSize: 18,
      color: dark ? theme.colors.white : theme.colors.ink, background: dark ? alpha(theme.colors.ink, 0.55) : alpha(theme.colors.white, 0.82), letterSpacing: "0.03em",
    }}
  >
    {text}
  </div>
);
export const ToFilm: React.FC<{ dark?: boolean }> = ({ dark }) => <Tag text="a filmar" dark={dark} />;

/* ------------------------------------------------------------------ real app recordings */

/** Recordings of the prototype: 402 × 874 pt at 3x (video/tools/record_app.mjs). */
export const APP = { w: 402, h: 874, px: 3 } as const;

/**
 * Which part of a recording plays when: [shot frame from, recording second at that frame]. A later segment starts a jump
 * in the recording (used only to skip the language model's wait). `freezeAt` (shot frame) holds the frame from then on.
 */
export type RecSeg = [number, number];

const recTime = (segs: RecSeg[], frame: number, fps: number) => {
  let s = segs[0];
  for (const x of segs) if (frame >= x[0]) s = x;
  return { seg: s, t: s[1] + (frame - s[0]) / fps };
};

/** The recording, as a 1206 × 2622 element (its native pixels); place it with a transform. */
export const Recording: React.FC<{ name: string; segs: RecSeg[]; freezeAt?: number; radius?: number }> = ({ name, segs, freezeAt, radius = 150 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = freezeAt !== undefined ? Math.min(frame, freezeAt) : frame;
  const { seg } = recTime(segs, f, fps);
  const startFrame = Math.round(seg[1] * fps);
  const local = f - seg[0];
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: APP.w * APP.px, height: APP.h * APP.px, borderRadius: radius, overflow: "hidden", background: "#eef3fb" }}>
      {/* the video's own frame is `local`: the Sequence starts `local` frames ago, also while frozen */}
      <Sequence from={frame - local} layout="none">
        <OffthreadVideo src={staticFile(`app/${name}.mp4`)} muted trimBefore={startFrame} style={{ position: "absolute", left: 0, top: 0, width: APP.w * APP.px, height: APP.h * APP.px }} />
      </Sequence>
    </div>
  );
};

/** A camera state on an app screen: px per pt (0 = the footage as filmed), the app point looked at, where it sits. */
export type CamKey = { at: number; ppt: number; fx: number; fy: number; cx?: number; cy?: number };

const camAt = (keys: CamKey[], frame: number) => {
  let i = 0;
  while (i < keys.length - 2 && frame >= keys[i + 1].at) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const u = b.at > a.at ? ramp(frame, a.at, b.at, theme.ease.inOut) : 0;
  return { a, b, u };
};

type Screens = { size: [number, number]; frames: number[][] } | null;

/**
 * A stock clip of a hand-held phone, the real recording on its screen, and a camera. Keys with ppt 0 are the footage as
 * filmed; keys with ppt > 0 lock the camera onto the screen: the app point (fx, fy) at (cx, cy), at ppt px per pt, the
 * phone turned upright. Between keys the camera eases both ways. The footage softens as the camera locks on.
 */
export const ScreenInsert: React.FC<{
  clip: string; from: number; play?: number; track: string; rec: string; segs: RecSeg[]; freezeRec?: number; keys: CamKey[];
  multiply?: boolean; screenRadius?: number; screen?: React.ReactNode; children?: (map: (ptx: number, pty: number) => Pt, lock: number) => React.ReactNode;
}> = ({ clip, from, play, track, rec, segs, freezeRec, keys, multiply, screenRadius = 130, screen, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const data = useJson<Screens>(`stock/screens/${track}.json`);
  if (!data) return null;
  const tClip = from + Math.min(frame, play ?? Infinity) / fps;
  const fr = data.frames;
  const i = Math.max(0, Math.min(fr.length - 1, Math.round((tClip - fr[0][0]) * 30)));
  const q = fr[i];
  const tf = toFrame(clip);
  const Q = [tf(q[1], q[2]), tf(q[3], q[4]), tf(q[5], q[6]), tf(q[7], q[8])] as Quad;
  const H = homography(APP.w * APP.px, APP.h * APP.px, Q);
  const toQ = (ptx: number, pty: number) => H.apply(ptx * APP.px, pty * APP.px);
  const widthPx = Math.hypot(Q[1].x - Q[0].x, Q[1].y - Q[0].y);
  const ppt0 = widthPx / APP.w;
  const theta = Math.atan2(Q[1].y - Q[0].y, Q[1].x - Q[0].x);

  const { a, b, u } = camAt(keys, frame);
  const state = (k: CamKey) => {
    const F = toQ(k.fx, k.fy);
    if (!k.ppt) return { F, T: F, logS: 0, rot: 0 };
    return { F, T: { x: k.cx ?? 1300, y: k.cy ?? 540 }, logS: Math.log(k.ppt / ppt0), rot: -theta };
  };
  const A = state(a), B = state(b);
  const F = lerpPt(A.F, B.F, u);
  const T = lerpPt(A.T, B.T, u);
  const logS = lerp(A.logS, B.logS, u);
  const cam = camera(F, T, Math.exp(logS), lerp(A.rot, B.rot, u));
  const lockA = a.ppt ? 1 : 0, lockB = b.ppt ? 1 : 0;
  const lock = lerp(lockA, lockB, u);
  const map = (ptx: number, pty: number) => cam.map(toQ(ptx, pty));
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: theme.colors.bg }}>
      <AbsoluteFill style={{ transform: cam.css, transformOrigin: "0 0" }}>
        <AbsoluteFill style={{ filter: `${GRADE} blur(${(lock * 3).toFixed(2)}px)` }}>
          <VideoLayer src={`stock/${clip}.mp4`} from={from} play={play} />
        </AbsoluteFill>
        <div style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: H.css, mixBlendMode: multiply ? "multiply" : undefined }}>
          {screen ? (
            <div style={{ position: "absolute", left: 0, top: 0, width: APP.w * APP.px, height: APP.h * APP.px, borderRadius: screenRadius, overflow: "hidden", background: "#000" }}>{screen}</div>
          ) : (
            <Recording name={rec} segs={segs} freezeAt={freezeRec} radius={screenRadius} />
          )}
        </div>
      </AbsoluteFill>
      {children?.(map, lock)}
    </AbsoluteFill>
  );
};

/**
 * A real recording shown flat and large over a soft, light ground (the scene behind, out of focus). The camera keys
 * say which app point sits where, at how many px per pt (2 px per pt keeps 13 pt text at 26 px).
 */
export const AppView: React.FC<{ rec: string; segs: RecSeg[]; freezeRec?: number; keys: CamKey[]; ground?: React.ReactNode; reveal?: { at: number; from: { x: number; y: number; w: number; h: number }; frames: number } }> = ({
  rec, segs, freezeRec, keys, ground, reveal,
}) => {
  const frame = useCurrentFrame();
  const { a, b, u } = camAt(keys, frame);
  const ppt = Math.exp(lerp(Math.log(a.ppt), Math.log(b.ppt), u));
  const fx = lerp(a.fx, b.fx, u), fy = lerp(a.fy, b.fy, u);
  const cx = lerp(a.cx ?? 1300, b.cx ?? 1300, u), cy = lerp(a.cy ?? 540, b.cy ?? 540, u);
  const s = ppt / APP.px;
  const left = cx - fx * ppt, top = cy - fy * ppt;
  let clip: string | undefined;
  if (reveal) {
    const r = ramp(frame, reveal.at, reveal.at + reveal.frames, theme.ease.inOut);
    const x = lerp(reveal.from.x, 0, r), y = lerp(reveal.from.y, 0, r);
    const w = lerp(reveal.from.w, 1920, r), h = lerp(reveal.from.h, 1080, r);
    clip = `inset(${y}px ${1920 - x - w}px ${1080 - y - h}px ${x}px round ${lerp(8, 0, r)}px)`;
  }
  return (
    <AbsoluteFill style={{ overflow: "hidden", clipPath: clip }}>
      <AbsoluteFill style={{ background: "#eef3fb" }}>{ground}</AbsoluteFill>
      <div style={{ position: "absolute", left, top, width: APP.w * ppt, height: APP.h * ppt, borderRadius: 46 * ppt, boxShadow: `0 40px 90px -30px ${alpha(theme.colors.ink, 0.45)}, 0 0 0 ${3 * ppt}px ${alpha(theme.colors.ink, 0.9)}` }} />
      <div style={{ position: "absolute", left, top, transformOrigin: "0 0", transform: `scale(${s})` }}>
        <Recording name={rec} segs={segs} freezeAt={freezeRec} radius={46 * APP.px} />
      </div>
    </AbsoluteFill>
  );
};

/** A still image filling the frame (cover), with a slow push. */
export const Still: React.FC<{ src: string; push?: [number, number]; origin?: string; filter?: string; children?: React.ReactNode }> = ({ src, push = [1, 1.04], origin = "50% 50%", filter, children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const s = interpolate(frame, [0, durationInFrames], push, clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: theme.colors.bg }}>
      <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: origin }}>
        <Img src={staticFile(src)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", filter }} />
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** A soft, light ground made from a frame of footage: out of focus and lifted, so ink type reads over it. */
export const SoftGround: React.FC<{ clip?: string; still?: string; at?: number }> = ({ clip, still, at = 0 }) => (
  <AbsoluteFill style={{ background: "#eef3fb" }}>
    <AbsoluteFill style={{ transform: "scale(1.15)", filter: "blur(28px) brightness(1.08) saturate(0.9)" }}>
      {clip ? (
        <Freeze frame={0}>
          <OffthreadVideo src={staticFile(`stock/${clip}.mp4`)} muted trimBefore={Math.round(at * 30)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />
        </Freeze>
      ) : null}
      {still ? <Img src={staticFile(still)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} /> : null}
    </AbsoluteFill>
    <AbsoluteFill style={{ background: alpha(theme.colors.white, 0.62) }} />
  </AbsoluteFill>
);
