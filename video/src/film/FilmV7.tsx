// Video 1, the cut from storyboard v7. Licensed stock (Pexels, public/stock/stock.json) and the real prototype's
// screens (video/tools/record_app.mjs): one real moment with the questions over it, text without sound effects (real
// sounds on real actions), the dog example, about 47 s, the privacy line kept. Pace and design rules: video/research/.
// 30 fps, 120 BPM (a beat is 15 frames).
import React from "react";
import { AbsoluteFill, Audio, Freeze, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/Newsreader";
import "../presentation/fonts";
import { theme } from "../theme";
import { useJson } from "../presentation/assets";
import { AppView, FrameBox, SoftGround, Tag, type BoxKey, type CamKey } from "../presentation/media";
import { TrackedScreen } from "../presentation/tracked";
import { ProofPicture } from "../proof/ProofCamera";
import { S23 } from "../presentation/shots/End";
import { clamp } from "../presentation/ui";

const { fontFamily: SERIF } = loadFont("normal", { weights: ["400", "500"], subsets: ["latin", "latin-ext"] });

/* ------------------------------------------------------------------ timeline (frames) */
const T = {
  opening: [0, 120], stop: [120, 150], answer: [150, 240], proof: [240, 390], ask: [390, 540], sensor: [540, 615],
  leaving: [615, 690], alert: [690, 780], cat: [780, 900], dog: [900, 1020], night: [1020, 1140], how: [1140, 1230], end: [1230, 1410],
} as const;
export const FILM_FRAMES = 1410;

/* ------------------------------------------------------------------ type: a serif for story lines, cut on */
const Line: React.FC<{ text: string; at: number; until?: number; x?: number; y?: number; size?: number; color?: string; shadow?: boolean; align?: "left" | "center" }> = ({
  text, at, until, x = 110, y = 860, size = 64, color = "#fff", shadow = true, align = "left",
}) => {
  const frame = useCurrentFrame();
  if (frame < at || (until !== undefined && frame >= until)) return null;
  const o = interpolate(frame, [at, at + 3], [0, 1], clamp); // a 3-frame fade: no slide, no bounce
  return (
    <div style={{ position: "absolute", left: align === "center" ? 0 : x, right: align === "center" ? 0 : undefined, top: y, textAlign: align, opacity: o,
      fontFamily: SERIF, fontWeight: 400, fontSize: size, lineHeight: 1.1, letterSpacing: "-0.015em", color, whiteSpace: "nowrap",
      textShadow: shadow ? "0 2px 22px rgb(0 0 0 / 0.38)" : undefined }}>
      {text}
    </div>
  );
};

/* ------------------------------------------------------------------ footage with the detector's boxes */
type Boxes = { frames: { t: number; boxes: { label: string; score: number; box: number[] }[] }[] };
const useBoxKeys = (clip: string, label: string, size: [number, number], from: number, to: number): BoxKey[] => {
  const b = useJson<Boxes>(`stock/boxes/${clip}.json`);
  if (!b) return [];
  return b.frames.filter((f) => f.t >= from - 1 && f.t <= to + 1).flatMap((f) => {
    const k = f.boxes.filter((x) => x.label === label).sort((p, q) => q.score - p.score)[0];
    return k ? [[f.t, k.box[0] * size[0], k.box[1] * size[1], k.box[2] * size[0], k.box[3] * size[1]] as BoxKey] : [];
  });
};

const Footage: React.FC<{ clip: string; from: number; push?: [number, number]; freeze?: number; grade?: string; children?: React.ReactNode }> = ({
  clip, from, push = [1, 1.04], freeze, grade = "brightness(1.03) saturate(1.03) contrast(0.99)", children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const s = interpolate(frame, [0, durationInFrames], push, clamp);
  const v = <OffthreadVideo src={staticFile(`stock/${clip}.mp4`)} muted trimBefore={Math.round(from * fps)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${s})`, filter: grade }}>
        {freeze !== undefined && frame >= freeze ? <Freeze frame={freeze}>{v}</Freeze> : v}
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Detected: React.FC<{ clip: string; from: number; labels: [string, string][]; size?: [number, number]; at?: number; push?: [number, number]; children?: React.ReactNode }> = ({
  clip, from, labels, size = [3840, 2160], at = 6, push, children,
}) => {
  const keys = labels.map(([q]) => useBoxKeys(clip, q, size, from, from + 6)); // eslint-disable-line react-hooks/rules-of-hooks
  return (
    <Footage clip={clip} from={from} push={push}>
      {labels.map(([, name], i) => keys[i].length ? <FrameBox key={name} clip={clip} keys={keys[i]} clipFrom={from} at={at + i * 6} label={name} /> : null)}
      {children}
    </Footage>
  );
};

/* ------------------------------------------------------------------ the shots */
const QUESTIONS = ["As chaves?", "Fechei a porta?", "O cão já comeu?", "A mãe já acordou?", "Desliguei o fogão?", "A encomenda chegou?"];

const Opening: React.FC = () => (
  <AbsoluteFill>
    <Footage clip="leaving-home-1" from={1.0} push={[1, 1.05]} />
    {QUESTIONS.map((q, i) => <Line key={q} text={q} at={6 + i * 15} until={i < QUESTIONS.length - 1 ? 6 + (i + 1) * 15 : undefined} size={84} y={820} />)}
  </AbsoluteFill>
);

const Stop: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <AbsoluteFill style={{ opacity: interpolate(frame, [0, 6], [0.55, 0.18], clamp) }}>
        <Footage clip="leaving-home-1" from={5.0} freeze={0} push={[1.05, 1.05]} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Answer: React.FC = () => (
  <AbsoluteFill>
    <Detected clip="leaving-home-keys-1" from={0.0} labels={[["keys", "chaves"]]} at={8} push={[1, 1.05]} />
    <Line text="A câmara da casa passa a saber onde estão as coisas." at={22} size={56} y={880} />
  </AbsoluteFill>
);

// the ask: the real app on a stock phone over a café table (phone-greenscreen-2), "Where are my keys?" and its answer
const ASK_KEYS: CamKey[] = [
  { at: 0, ppt: 0, fx: 201, fy: 600, upright: false }, { at: 52, ppt: 0, fx: 201, fy: 600, upright: false },
  { at: 74, ppt: 1.75, fx: 201, fy: 690, cx: 1280, cy: 560 },
];
const Ask: React.FC = () => (
  <AbsoluteFill>
    <TrackedScreen take="stock/phone-greenscreen-2.mp4" track="takes/proof/phone-gs-2.track.json" keyed="takes/proof/phone-gs-2.key.webm" from={0.5}
      rec="ask-keys" segs={[[0, 4.6]]} keys={ASK_KEYS} />
    <Line text="Basta perguntar." at={8} until={150} size={64} y={150} />
  </AbsoluteFill>
);

// the sentence that becomes a sensor: the same hands, a few seconds later
const SENSOR_KEYS: CamKey[] = [{ at: 0, ppt: 1.75, fx: 201, fy: 650, cx: 1280, cy: 560 }, { at: 74, ppt: 1.75, fx: 201, fy: 650, cx: 1280, cy: 560 }];
const Sensor: React.FC = () => (
  <AbsoluteFill>
    <TrackedScreen take="stock/phone-greenscreen-2.mp4" track="takes/proof/phone-gs-2.track.json" keyed="takes/proof/phone-gs-2.key.webm" from={5.5}
      rec="ask-keys" segs={[[0, 13.9], [30, 15.65]]} keys={SENSOR_KEYS} />
    <Line text="Uma frase torna-se um sensor." at={4} size={60} y={150} />
  </AbsoluteFill>
);

// leaving: the door shuts; an inset shows the keys left on the hall table, boxed
const KeysInset: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [10, 22], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", right: 64, bottom: 72, width: 520, height: 320, borderRadius: 18, overflow: "hidden", border: "4px solid #fff",
      boxShadow: "0 30px 60px -24px rgb(0 0 0 / 0.55)", opacity: p }}>
      <Img src={staticFile("v7/crop-keys.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      <div style={{ position: "absolute", left: 18, top: 16, padding: "4px 11px", borderRadius: 8, background: theme.colors.labs, color: "#fff",
        fontFamily: theme.fonts.display, fontSize: 24, fontWeight: 600 }}>chaves · ficaram na mesa</div>
    </div>
  );
};
const Leaving: React.FC = () => (
  <AbsoluteFill>
    <Footage clip="leaving-home-2" from={3.0} push={[1.02, 1.0]} />
    <KeysInset />
  </AbsoluteFill>
);

// the alert outside: a stock phone in a hand (phone-greenscreen-3), the real notification, a push to read it
const ALERT_KEYS: CamKey[] = [
  { at: 0, ppt: 0, fx: 201, fy: 120, upright: false }, { at: 28, ppt: 0, fx: 201, fy: 120, upright: false },
  { at: 50, ppt: 2.1, fx: 201, fy: 110, cx: 960, cy: 480 },
];
const Alert: React.FC = () => (
  <TrackedScreen take="stock/phone-greenscreen-3.mp4" track="takes/proof/phone-gs-3.track.json" keyed="takes/proof/phone-gs-3.key.webm" from={1.0}
    rec="alert-keys" segs={[[0, 1.2]]} keys={ALERT_KEYS} />
);

// a case: the thing itself with its box (2 s), then the real app's answer, large (2 s)
const Case: React.FC<{ clip: string; from: number; labels: [string, string][]; line: string; rec: string; recAt: number; fy: number; chip?: string }> = ({
  clip, from, labels, line, rec, recAt, fy, chip,
}) => (
  <AbsoluteFill>
    <Sequence durationInFrames={60} layout="none">
      <Detected clip={clip} from={from} labels={labels} at={4} push={[1, 1.04]}>
        {chip ? <div style={{ position: "absolute", left: 110, top: 96, fontFamily: theme.fonts.mono, fontSize: 30, color: "#fff", padding: "6px 12px",
          background: "rgb(0 0 0 / 0.45)", borderRadius: 8 }}>{chip}</div> : null}
      </Detected>
      <Line text={line} at={4} size={64} y={880} />
    </Sequence>
    <Sequence from={60} durationInFrames={60} layout="none">
      <AppView rec={rec} segs={[[0, recAt]]} keys={[{ at: 0, ppt: 1.9, fx: 201, fy, cx: 1250, cy: 540 }]} ground={<SoftGround clip={clip} at={from} />} />
      <Line text={line} at={0} size={56} y={480} color={theme.colors.ink} shadow={false} />
    </Sequence>
    <Tag text="conceito" dark />
  </AbsoluteFill>
);

// how it works: the kit's real devices, named and wired; only the keys' small crop travels to the app
const Node: React.FC<{ x: number; y: number; img?: string; label: string; at: number; contain?: boolean; children?: React.ReactNode }> = ({ x, y, img, label, at, contain, children }) => {
  const frame = useCurrentFrame();
  if (frame < at) return null;
  const o = interpolate(frame, [at, at + 3], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: "translate(-50%,-50%)", display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: o }}>
      {children ?? <Img src={staticFile(`v7/${img}`)} style={{ width: 190, height: 190, objectFit: contain ? "contain" : "cover", borderRadius: 22, background: "#fff",
        padding: contain ? 26 : 0, boxShadow: "0 18px 40px -24px rgb(0 0 0 / 0.55)" }} />}
      <div style={{ fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 30, color: "#16130E", background: "#fff", border: "2px solid rgb(0 0 0 / 0.12)",
        borderRadius: 999, padding: "8px 18px", whiteSpace: "nowrap" }}>{label}</div>
    </div>
  );
};
const How: React.FC = () => {
  const frame = useCurrentFrame();
  const draw = (at: number) => interpolate(frame, [at, at + 8], [0, 1], clamp);
  const travel = interpolate(frame, [48, 70], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const cx = 1130 + (1600 - 1130) * travel; // the crop moves from home to the app, along the wire
  return (
    <AbsoluteFill style={{ background: "#EFECE4", backgroundImage: "linear-gradient(rgba(60,50,30,.07) 2px,transparent 2px),linear-gradient(90deg,rgba(60,50,30,.07) 2px,transparent 2px)",
      backgroundSize: "44px 44px" }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <g fill="none" stroke="#16130E" strokeWidth={4} strokeLinecap="round">
          <path d="M 330 300 C 560 300, 560 470, 760 470" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw(12)} />
          <path d="M 330 700 C 560 700, 560 470, 760 470" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw(12)} />
          <path d="M 960 470 L 1170 470" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw(27)} />
          <path d="M 1370 470 L 1560 470" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw(39)} />
        </g>
        {frame >= 48 ? <path d={`M 960 470 L ${Math.min(1560, cx)} 470`} stroke="#F6E755" strokeWidth={14} strokeLinecap="round" opacity={0.85} fill="none" /> : null}
      </svg>
      <Node x={230} y={300} img="dev-camera.jpg" label="Câmara · entrada" at={0} />
      <Node x={230} y={700} img="dev-camera.jpg" label="Câmara · cozinha" at={6} />
      <Node x={860} y={470} img="dev-gateway.jpg" label="Em casa" at={15} />
      <Node x={1270} y={470} img="by-altice-labs-light.svg" label="Altice" at={27} contain />
      <Node x={1690} y={470} label="A app" at={39}>
        <div style={{ width: 130, height: 270, borderRadius: 30, background: "#16130E", padding: 9, display: "flex", alignItems: "center", boxShadow: "0 18px 40px -24px rgb(0 0 0 / 0.55)" }}>
          <div style={{ width: "100%", height: "62%", borderRadius: 20, background: `#fff url(${staticFile("v7/crop-keys.jpg")}) center/cover`, opacity: interpolate(frame, [70, 74], [0, 1], clamp) }} />
        </div>
      </Node>
      {frame >= 48 && travel < 1 ? (
        <div style={{ position: "absolute", left: cx, top: 470, width: 76, height: 76, transform: "translate(-50%,-50%)", borderRadius: 14,
          background: `url(${staticFile("v7/crop-keys.jpg")}) center/cover`, outline: "6px solid #F6E755" }} />
      ) : null}
      <Line text="Nenhum vídeo nem imagem completa sai de casa." at={60} align="center" y={900} size={58} color="#16130E" shadow={false} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ sound: the music marks sections; real sounds on real actions */
const MUSIC = "audio/music/bed-fast.wav";
// [film from, film to, file from] in seconds: the intro builds under the questions, silence on the stop, the drop on the
// answer, one jump at the cases so the bed's final hit (file 88 s) lands on the end card (film 41 s)
const SEGMENTS: [number, number, number][] = [[0, 4, 0], [5, 26, 8], [26, 47, 73]];
// [film frame of the action, file, volume, peak in the file (s)]: peaks one frame after the picture
const CUES: [number, string, number, number][] = [
  [T.answer[0] + 70, "sfx/v4/keys-1.wav", 0.42, 0.201],      // a hand reaches the keys
  [T.proof[0] + 2, "sfx/v4/keys-2.wav", 0.35, 0.098],        // keys in the hands, live view
  [T.proof[0] + 46, "sfx/v4/keys-1.wav", 0.4, 0.201],        // the keys move towards the camera
  [T.proof[0] + 47, "sfx/v3/click-1.wav", 0.22, 0.043],      // the brackets lock (the camera's own click)
  [T.ask[0] + 52, "sfx/v4/tap-1.wav", 0.42, 0.005],          // send
  [T.sensor[0] + 23, "sfx/v4/tap-2.wav", 0.4, 0.007],        // send
  [T.leaving[0] + 40, "sfx/v4/door-1.wav", 0.55, 0.85],      // the door shuts
  [T.leaving[0] + 70, "sfx/v4/vib-1.wav", 0.32, 0.223],      // the phone buzzes (J-cut into the alert)
  [T.alert[0] + 22, "sfx/v4/vib-2.wav", 0.36, 0.298],        // the notification lands
  [T.cat[0] + 4, "sfx/v3/click-1.wav", 0.2, 0.043],
  [T.dog[0] + 4, "sfx/v3/click-1.wav", 0.2, 0.043],
  [T.night[0] + 4, "sfx/v3/click-1.wav", 0.2, 0.043],
];
const Sound: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      {SEGMENTS.map(([a, b, f], i) => {
        const from = Math.round(a * fps), dur = Math.round((b - a) * fps);
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <Audio src={staticFile(MUSIC)} trimBefore={Math.round(f * fps)} volume={(fr) => {
              const t = a + fr / fps;
              const duck = 1 - 0.45 * interpolate(t * fps, [T.alert[0] + 18, T.alert[0] + 24, T.alert[0] + 60, T.alert[0] + 75], [0, 1, 1, 0], clamp);
              const tail = interpolate(t, [45.5, 47], [1, 0], clamp);
              return 0.62 * Math.min(1, fr / 2, (dur - fr) / 2) * duck * tail * interpolate(t, [0, 0.4], [0.5, 1], clamp);
            }} />
          </Sequence>
        );
      })}
      <Audio src={staticFile("audio/sfx/v4/room-living.wav")} loop volume={(f) => (f >= T.stop[0] && f < T.stop[1] ? 0.09 : 0.03)} />
      {CUES.map(([at, file, vol, peak], i) => (
        <Sequence key={i} from={Math.max(0, at + 1 - Math.round(peak * fps))} layout="none">
          <Audio src={staticFile(`audio/${file}`)} volume={vol} />
        </Sequence>
      ))}
    </>
  );
};

/* ------------------------------------------------------------------ the film */
const At: React.FC<{ span: readonly [number, number]; children: React.ReactNode }> = ({ span, children }) => (
  <Sequence from={span[0]} durationInFrames={span[1] - span[0]}>{children}</Sequence>
);

export const FilmV7: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <At span={T.opening}><Opening /></At>
    <At span={T.stop}><Stop /></At>
    <At span={T.answer}><Answer /></At>
    <At span={T.proof}><ProofPicture /></At>
    <At span={T.ask}><Ask /></At>
    <At span={T.sensor}><Sensor /></At>
    <At span={T.leaving}><Leaving /></At>
    <At span={T.alert}><Alert /></At>
    <At span={T.cat}><Case clip="cat-counter-2" from={2.0} labels={[["a cat", "gato"]]} line="O gato na bancada." rec="cat" recAt={7.6} fy={140} /></At>
    <At span={T.dog}><Case clip="dog-bowl-2" from={2.0} labels={[["a dog", "cão"], ["a pet bowl", "tigela"]]} line="O cão já comeu?" rec="dog" recAt={7.9} fy={560} /></At>
    <At span={T.night}><Case clip="garden-night-2" from={7.0} labels={[["a person", "pessoa"]]} line="O que aconteceu às 4h?" rec="night" recAt={8.0} fy={560} chip="04:02" /></At>
    <At span={T.how}><How /></At>
    <At span={T.end}><S23 /></At>
    <Sound />
  </AbsoluteFill>
);
