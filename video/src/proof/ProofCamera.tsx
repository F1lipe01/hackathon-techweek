// Proof A, 5 s: the keys are shown to the home camera and the app learns them. The film's new standard, on one shot,
// before the film is rebuilt (video/research/compositing-playbook.md). All footage is licensed stock (Pexels, listed in
// public/stock/stock.json); the app is a recording of the real prototype (video/tools/record_app.mjs register-keys).
//   0-44   a hand holds an iPhone; the app, tracked onto its green screen, shows the camera's live view of the keys
//          with the registration box; a line pops in
//   45-89  the home camera's own view: the brackets lock onto the keys, the views count up to 8
//   90-149 back to the phone; the camera pushes into "Keys added"
// 30 fps, cuts on the beat (120 BPM: 15 frames). Every visual event has its sound.
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { APP, Chip, FrameBox, Tag, type BoxKey, type CamKey } from "../presentation/media";
import { TrackedScreen } from "../presentation/tracked";
import { Title } from "../presentation/type";
import { clamp } from "../presentation/ui";

export const PROOF_FRAMES = 150;
const PHONE = "stock/phone-greenscreen-1.mp4";
const TRACK = "takes/proof/phone-gs-1.track.json";
const KEYED = "takes/proof/phone-gs-1.key.webm";
const KEYS = "keys-shown-1"; // 3840 x 2160, 30 fps
const P = APP.px; // recording px per pt

// the register-keys recording: when each view is counted (s), from its marks
const VIEW_AT = [5.655, 6.093, 6.522, 6.952, 7.385, 7.818, 8.251, 8.682]; // register-keys.marks.json (re-recorded 19 Nov)
const viewsAt = (t: number) => VIEW_AT.filter((v) => t >= v).length;

type Boxes = { frames: { t: number; boxes: { label: string; score: number; box: [number, number, number, number] }[] }[] };
/** The detector's keys box (normalised), one sample a second, eased between samples. */
const useKeysBox = () => {
  const b = useJson<Boxes>(`stock/boxes/${KEYS}.json`);
  return (t: number): [number, number, number, number] | null => {
    if (!b) return null;
    const s = b.frames.map((f) => ({ t: f.t, k: f.boxes.filter((x) => x.label === "keys").sort((p, q) => q.score - p.score)[0] })).filter((f) => f.k);
    let i = 0;
    while (i < s.length - 2 && s[i + 1].t <= t) i++;
    const a = s[i], c = s[Math.min(i + 1, s.length - 1)];
    const u0 = c.t > a.t ? Math.min(1, Math.max(0, (t - a.t) / (c.t - a.t))) : 0;
    const u = u0 * u0 * (3 - 2 * u0);
    return [0, 1, 2, 3].map((j) => a.k.box[j] + (c.k.box[j] - a.k.box[j]) * u) as [number, number, number, number];
  };
};

/** The recording's Dynamic Island, covered: this phone has a notch, and the real notch stays on top (the key). */
const IslandCover: React.FC = () => (
  <div style={{ position: "absolute", left: 132 * P, top: 6 * P, width: 138 * P, height: 46 * P, background: "#eef3fb" }} />
);

/** The app's live view, drawn over the recording's own live box: the camera's view of the keys and the app's
 *  registration box (styles from prototype/web/app.css: .livebox, .box.enrol), in recording px. */
const LiveView: React.FC<{ keysFrom: number; recFrom: number }> = ({ keysFrom, recFrom }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const box = useKeysBox();
  const L = { x: 22 * P, y: 120 * P, w: 358 * P, h: (358 / 1.6) * P }; // .livebox: full width less 22 pt margins, 16:10
  const k = Math.max(L.w / 3840, L.h / 2160);
  const dw = 3840 * k, ox = (L.w - dw) / 2;
  const t = keysFrom + frame / fps;
  const b = box(t);
  const n = viewsAt(recFrom + frame / fps);
  return (
    <>
      <IslandCover />
      <div style={{ position: "absolute", left: L.x, top: L.y, width: L.w, height: L.h, borderRadius: 18 * P, overflow: "hidden", background: "#000" }}>
        <OffthreadVideo src={staticFile(`stock/${KEYS}.mp4`)} muted trimBefore={Math.round(keysFrom * fps)}
          style={{ position: "absolute", left: ox, top: 0, width: dw, height: L.h }} />
        {b ? (
          <div style={{ position: "absolute", left: ox + b[0] * dw, top: b[1] * L.h, width: (b[2] - b[0]) * dw, height: (b[3] - b[1]) * L.h,
            border: `${2 * P}px dashed #E8710A`, borderRadius: 6 * P, boxShadow: `0 0 0 ${P}px rgb(0 0 0 / 0.35)` }}>
            <b style={{ position: "absolute", left: -2 * P, bottom: `calc(100% + ${4 * P}px)`, whiteSpace: "nowrap", font: `600 ${12 * P}px/1 ${theme.fonts.display}`,
              color: "#fff", background: "#E8710A", padding: `${5 * P}px ${7 * P}px`, borderRadius: 5 * P }}>
              {`Registering Keys · view ${Math.max(1, n)} of 8`}
            </b>
          </div>
        ) : null}
      </div>
    </>
  );
};

/** The home camera's view: the keys, the brackets locking on, the views counting to 8. */
const CameraView: React.FC = () => {
  const frame = useCurrentFrame();
  const box = useKeysBox();
  const FROM = 6.0; // clip second at the cut: the keys come towards the camera
  const keys: BoxKey[] = [];
  for (let t = FROM; t <= FROM + 1.6; t += 0.1) {
    const b = box(t);
    if (b) keys.push([t, b[0] * 3840, b[1] * 2160, b[2] * 3840, b[3] * 2160]);
  }
  const n = Math.min(8, 4 + Math.max(0, Math.floor((frame - 5) / 6))); // 4 of 8 at the cut, one more every 6 frames
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: theme.colors.bg }}>
      <AbsoluteFill style={{ transform: `scale(${interpolate(frame, [0, 45], [1.0, 1.035], clamp)})` }}>
        <OffthreadVideo src={staticFile(`stock/${KEYS}.mp4`)} muted trimBefore={Math.round(FROM * 30)} style={{ width: "100%", height: "100%", objectFit: "cover",
          filter: "brightness(1.03) saturate(1.03) contrast(0.99)" }} />
        {keys.length ? <FrameBox clip={KEYS} keys={keys} clipFrom={FROM} at={2} label="chaves" color={theme.colors.labs} /> : null}
      </AbsoluteFill>
      <Chip at={4} text={`vista ${n} de 8`} x={1500} y={930} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ sound */
// [frame of the picture event, file, volume, peak in the file (s)]: the peak lands one frame after the picture
const CUES: [number, string, number, number][] = [
  [6, "sfx/v3/click-1.wav", 0.32, 0.043],      // the line pops in
  [2, "sfx/v4/keys-2.wav", 0.35, 0.098],       // keys in the hand, live view
  [47, "sfx/v3/click-1.wav", 0.34, 0.043],     // the brackets lock on
  [46, "sfx/v4/keys-1.wav", 0.42, 0.201],      // the keys move towards the camera
  ...[0, 1, 2, 3, 4].map((i) => [45 + 5 + i * 6, "sfx/v3/click-3.wav", 0.16 + i * 0.02, 0.004] as [number, string, number, number]), // a view counted
  [101, "sfx/v3/trans-2.wav", 0.24, 0.375],    // the push into the screen, peaking at its fastest
  [114, "sfx/v3/click-1.wav", 0.24, 0.043],    // "Keys added" settles
];
const Sound: React.FC = () => (
  <>
    <Audio src={staticFile("audio/music/bed-fast.wav")} trimBefore={24 * 30}
      volume={(f) => 0.62 * interpolate(f, [0, 3, PROOF_FRAMES - 12, PROOF_FRAMES], [0, 1, 1, 0], clamp)} />
    <Audio src={staticFile("audio/sfx/v4/room-living.wav")} volume={0.035} loop />
    {CUES.map(([at, file, vol, peak], i) => (
      <Sequence key={i} from={Math.max(0, at + 1 - Math.round(peak * 30))} layout="none">
        <Audio src={staticFile(`audio/${file}`)} volume={vol} />
      </Sequence>
    ))}
  </>
);

/* ------------------------------------------------------------------ the shot */
/** Proof A's picture only, for the film, which carries its own continuous sound. */
export const ProofPicture: React.FC = () => {
  // shot 1: a slow push towards the live view (from the footage as filmed to about 1,2x), so the keys can be seen
  const still: CamKey[] = [{ at: 0, ppt: 0, fx: 201, fy: 230 }, { at: 1, ppt: 0, fx: 201, fy: 230 }, { at: 44, ppt: 0.95, fx: 201, fy: 230, upright: false }];
  const push: CamKey[] = [{ at: 0, ppt: 0, fx: 201, fy: 300 }, { at: 3, ppt: 0, fx: 201, fy: 300 }, { at: 24, ppt: 1.9, fx: 201, fy: 300, cx: 960, cy: 560 }];
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <Sequence from={0} durationInFrames={45}>
        <TrackedScreen take={PHONE} track={TRACK} keyed={KEYED} from={3.0} rec="register-keys" segs={[[0, 5.0]]} keys={still}
          overlay={<LiveView keysFrom={2.0} recFrom={5.0} />} />
      </Sequence>
      <Sequence from={45} durationInFrames={45}>
        <CameraView />
      </Sequence>
      <Sequence from={90} durationInFrames={60}>
        <TrackedScreen take={PHONE} track={TRACK} keyed={KEYED} from={6.2} rec="register-keys" segs={[[0, 9.15]]} keys={push} overlay={<IslandCover />} />
      </Sequence>
      <Sequence from={0} durationInFrames={90} layout="none">
        <div style={{ position: "absolute", left: 110, top: 96 }}>
          <Title text="Mostra-se uma vez." size={64} max={900} at={6} entrance="rise" color={theme.colors.white}
            style={{ textShadow: "0 2px 18px rgb(0 0 0 / 0.35)" }} />
        </div>
      </Sequence>
      <Tag text="imagens de arquivo" dark />
    </AbsoluteFill>
  );
};

export const ProofCamera: React.FC = () => (
  <AbsoluteFill>
    <ProofPicture />
    <Sound />
  </AbsoluteFill>
);
