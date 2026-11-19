// A filmed take of a hand-held phone with the real app recording placed on its screen, tracked from the marker screen
// the phone showed (video/tools/track_markers.py) and with the thumb kept on top (video/tools/key_screen.py).
// Research: video/research/compositing-playbook.md §2 and §4. Layers, bottom to top, all inside the plate's grade:
//   1. the take;
//   2. the insert, drawn through the tracked homography, softened to the plate's focus, blacks lifted, with motion blur
//      made of sub-frame copies across the shutter (1/50 s at 30 fps = 0,6 of a frame);
//   3. the keyed take: the thumb, the bezel's real edge, the Dynamic Island and reflections;
//   4. the screen's light: a blurred copy of the insert in screen mode, which also falls on the thumb;
//   5. grain over everything.
// The camera keys (as in ScreenInsert) push into the screen; the plate is never blurred while the screen stays sharp.
import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { useJson } from "./assets";
import { APP, Recording, camAt, type CamKey, type RecSeg } from "./media";
import { camera, coverFit, homography, lerp, lerpPt, type Pt, type Quad } from "./geom";

type Track = { src: { w: number; h: number; fps: number }; screen: { w: number; h: number }; frames: number[][] };
type KeyMeta = { crop: [number, number, number, number]; first: number; fps: number };

/** The plate's grade, shared by every layer so the insert sits in the same light. */
const GRADE = "brightness(1.03) saturate(1.03) contrast(0.99)";

/** The look of the insert: defocus (frame px), lift of the blacks (0-1), glow opacity, grain opacity. */
export type ScreenLook = { defocus: number; lift: number; glow: number; grain: number };
const LOOK: ScreenLook = { defocus: 0.7, lift: 0.05, glow: 0.1, grain: 0.05 };

/** The screen's corners at a source frame (fractional), in frame px: rows interpolated, ends held. */
const quadAt = (tr: Track, f: number, map: (x: number, y: number) => Pt): Quad => {
  const fr = tr.frames;
  const i = Math.max(0, Math.min(fr.length - 1.001, f - fr[0][0]));
  const a = fr[Math.floor(i)], b = fr[Math.min(fr.length - 1, Math.floor(i) + 1)], u = i - Math.floor(i);
  const p = (k: number) => map(lerp(a[3 + 2 * k], b[3 + 2 * k], u), lerp(a[4 + 2 * k], b[4 + 2 * k], u));
  return [p(0), p(1), p(2), p(3)];
};

/** Grow a quad about its centre: with a keyed take the insert overscans the screen by a few px and the real bezel,
 *  kept by the key, draws the true edge on top, so no green fringe shows. */
const grow = (q: Quad, s: number): Quad => {
  const c = { x: (q[0].x + q[1].x + q[2].x + q[3].x) / 4, y: (q[0].y + q[1].y + q[2].y + q[3].y) / 4 };
  return q.map((p) => ({ x: c.x + (p.x - c.x) * (1 + s), y: c.y + (p.y - c.y) * (1 + s) })) as Quad;
};

const Grain: React.FC<{ opacity: number }> = ({ opacity }) => {
  const frame = useCurrentFrame();
  const id = `grain-${frame}`;
  return (
    <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, mixBlendMode: "overlay", opacity, pointerEvents: "none" }}>
      <filter id={id}>
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={Math.floor(random(`g${frame}`) * 1000)} />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter={`url(#${id})`} />
    </svg>
  );
};

export const TrackedScreen: React.FC<{
  /** The take and its data under public/: takes/<name>.mov, the track JSON and (green-screen takes) the keyed webm. */
  take: string; track: string; keyed?: string;
  /** Seconds into the take where this shot starts. */
  from: number;
  rec?: string; segs?: RecSeg[]; freezeRec?: number; screen?: React.ReactNode;
  /** Drawn over the recording in its own pixels (1206 x 2622), so it moves with the screen: e.g. a live view. */
  overlay?: React.ReactNode;
  keys: CamKey[]; look?: Partial<ScreenLook>; shutter?: number; screenRadius?: number;
  /** Layers to leave out, for checks: "blur" (one copy only), "key", "glow", "grain". */
  off?: string[];
  children?: (map: (ptx: number, pty: number) => Pt, lock: number) => React.ReactNode;
}> = ({ take, track, keyed, from, rec, segs, freezeRec, screen, overlay, keys, look: lookIn, shutter = 0.6, screenRadius: radiusIn, off = [], children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const look = { ...LOOK, ...lookIn };
  // with a key the real screen corners come from the plate, so the insert's own corners stay tighter than the glass's
  const screenRadius = radiusIn ?? (keyed ? 60 : 130);
  const tr = useJson<Track>(track);
  const km = useJson<KeyMeta>(keyed ? `${keyed}.json` : track);
  if (!tr) return null;
  const { k, ox, oy } = coverFit(tr.src.w, tr.src.h);
  const toF = (x: number, y: number): Pt => ({ x: ox + x * k, y: oy + y * k });
  const fSrc = (from + frame / fps) * tr.src.fps; // the source frame on screen now
  const SW = APP.w * APP.px, SH = APP.h * APP.px;
  const over = keyed ? 0.008 : 0; // overscan under the keyed bezel
  const Q = grow(quadAt(tr, fSrc, toF), over);
  const H = homography(SW, SH, Q);
  const toQ = (ptx: number, pty: number) => H.apply(ptx * APP.px, pty * APP.px);
  const widthPx = Math.hypot(Q[1].x - Q[0].x, Q[1].y - Q[0].y);
  const ppt0 = widthPx / APP.w;
  const theta = Math.atan2(Q[1].y - Q[0].y, Q[1].x - Q[0].x);

  // the camera (push-in), as in ScreenInsert
  const { a, b, u } = camAt(keys, frame);
  const state = (key: CamKey) => {
    const F = toQ(key.fx, key.fy);
    if (!key.ppt) return { F, T: F, logS: 0, rot: 0 };
    // a push that keeps the phone as filmed zooms about the phone itself unless told where to put it: it can't reveal an edge
    const T = key.cx !== undefined ? { x: key.cx, y: key.cy ?? 540 } : key.upright === false ? F : { x: 1300, y: 540 };
    return { F, T, logS: Math.log(key.ppt / ppt0), rot: key.upright === false ? 0 : -theta };
  };
  const A = state(a), B = state(b);
  const cam = camera(lerpPt(A.F, B.F, u), lerpPt(A.T, B.T, u), Math.exp(lerp(A.logS, B.logS, u)), lerp(A.rot, B.rot, u));
  const lock = lerp(a.ppt ? 1 : 0, b.ppt ? 1 : 0, u);
  const map = (ptx: number, pty: number) => cam.map(toQ(ptx, pty));

  // motion blur: sub-frame copies across the shutter, as many as the blur is long (render px at 4K = 2 × frame px)
  const Qa = quadAt(tr, fSrc - shutter / 2, toF), Qb = quadAt(tr, fSrc + shutter / 2, toF);
  const streak = Math.max(...Qa.map((p, i) => Math.hypot(p.x - Qb[i].x, p.y - Qb[i].y))) * 2;
  const n = off.includes("blur") ? 1 : Math.max(1, Math.min(6, Math.ceil(streak / 2)));
  const content = (
    <div style={{ position: "absolute", left: 0, top: 0, width: SW, height: SH, borderRadius: screenRadius, overflow: "hidden", background: "#000" }}>
      {screen ?? <Recording name={rec!} segs={segs!} freezeAt={freezeRec} radius={screenRadius} />}
      {overlay}
    </div>
  );
  const copies = Array.from({ length: n }, (_, j) => {
    const d = n === 1 ? 0 : (j / (n - 1) - 0.5) * shutter;
    const Hj = n === 1 ? H : homography(SW, SH, grow(quadAt(tr, fSrc + d, toF), over));
    return { css: Hj.css, opacity: 1 / (j + 1) }; // a running mean: each copy over the ones before
  });
  const insertFilter = `blur(${look.defocus}px) contrast(${1 - look.lift}) brightness(${1 + look.lift / 2})`;
  const keyTrim = km && keyed ? Math.round(((from * tr.src.fps - km.first) / tr.src.fps) * fps) : 0;

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: theme.colors.bg }}>
      <AbsoluteFill style={{ transform: cam.css, transformOrigin: "0 0" }}>
        <AbsoluteFill style={{ filter: GRADE }}>
          <OffthreadVideo src={staticFile(take)} muted trimBefore={Math.round(from * fps)}
            style={{ position: "absolute", left: ox, top: oy, width: tr.src.w * k, height: tr.src.h * k }} />
          {/* one filter in frame space over all the sub-frame copies (cheaper, and the blur is in true frame px) */}
          <AbsoluteFill style={{ filter: insertFilter }}>
            {copies.map((c, j) => (
              <div key={j} style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: c.css, opacity: c.opacity }}>{content}</div>
            ))}
          </AbsoluteFill>
          {keyed && km && !off.includes("key") ? (
            <Sequence from={0} layout="none">
              <OffthreadVideo src={staticFile(keyed)} transparent muted trimBefore={Math.max(0, keyTrim)}
                style={{ position: "absolute", left: ox + km.crop[0] * k, top: oy + km.crop[1] * k, width: km.crop[2] * k, height: km.crop[3] * k }} />
            </Sequence>
          ) : null}
          {off.includes("glow") ? null : <AbsoluteFill style={{ filter: "blur(14px) brightness(1.2)", mixBlendMode: "screen", opacity: look.glow,
            clipPath: `polygon(${grow(Q, 0.02).map((p) => `${p.x.toFixed(1)}px ${p.y.toFixed(1)}px`).join(",")})` }}>
            <div style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: H.css }}>{content}</div>
          </AbsoluteFill>}
        </AbsoluteFill>
      </AbsoluteFill>
      {off.includes("grain") ? null : <Grain opacity={look.grain} />}
      {children?.(map, lock)}
    </AbsoluteFill>
  );
};
