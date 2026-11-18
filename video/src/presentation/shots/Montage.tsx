// Shots 1–2. The opening: a rapid-fire montage of everyday questions, one shot per beat with a boom on every cut,
// each with a clean bracket box keyframed by hand against the footage (frame fractions, measured on the frames) and
// the object's name; then a hard stop, one beat of white and silence.
// The wallet has no clip: a still, small, in a card.
import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha, shadow } from "../tokens";
import { SmallPrint, Title } from "../type";
import { Daylight, LockBox, Paper, Track, mix, ramp, trackAt } from "../ui";
import { StockClip, cover } from "../stock";
import { Sfx } from "../sound";
import { SHOT_FRAMES, beatFrame } from "../timeline";

export const MONTAGE_FRAMES = SHOT_FRAMES.montage;
export const STOP_FRAMES = SHOT_FRAMES.stop;

type Shot = { slot: string; start: number; q: string; label: string; track: Track; lift?: number; zoom?: number };

const at = (t: number, b: [number, number, number, number]): Track[number] => [t, ...b];
const W = 1920 / 1013.3; // the 4096 × 2160 sources, scaled to 3840 × 2026 (aspect ≈ 1,895)

// boxes: measured by eye (keys, kettle, lock) or the detector's boxes checked by eye (stock.json subject_box)
export const SHOTS: Shot[] = [
  { slot: "m-keys", start: 0.3, q: "Onde estão as chaves?", label: "chaves", track: [[0.3, 0.255, 0.575, 0.54, 0.668], [0.9, 0.252, 0.575, 0.537, 0.668]] },
  { slot: "m-dog", start: 1.0, q: "O cão já comeu?", label: "cão", track: [at(1.0, [0.1411, 0.1685, 0.7464, 0.9117])] },
  { slot: "m-mother", start: 1.0, q: "A minha mãe já acordou?", label: "pessoa", track: [at(1.0, cover([0.086, 0.115, 0.691, 1.0], W, 1)), at(2.0, cover([0.086, 0.096, 0.685, 0.999], W, 1))] },
  { slot: "m-glasses", start: 2.0, q: "Onde deixei os óculos?", label: "óculos", track: [at(2.0, [0.5146, 0.4892, 0.6477, 0.6039])] },
  { slot: "m-plant", start: 2.0, q: "Reguei a planta?", label: "planta", track: [at(2.0, cover([0.2302, 0.0, 0.7153, 0.9944], W, 1))] },
  { slot: "m-pills", start: 2.0, q: "Tomei o comprimido?", label: "caixa dos comprimidos", track: [at(2.0, cover([0.2445, 0.486, 0.6786, 0.8468], 2732, 1440))], zoom: 1.12 },
  { slot: "m-cat", start: 1.0, q: "Onde está o gato?", label: "gato", track: [at(1.0, [0.3504, 0.0, 0.878, 0.9565])] },
  { slot: "m-parcel", start: 2.0, q: "A encomenda chegou?", label: "encomenda", track: [at(2.0, [0.1179, 0.5036, 0.4819, 0.9631])] },
  { slot: "m-kettle", start: 0.4, q: "Deixei a chaleira ligada?", label: "chaleira", track: [[0.4, 0.547, 0.426, 0.64, 0.648], [1.0, 0.53, 0.426, 0.627, 0.659]] },
  { slot: "m-door", start: 2.0, q: "Fechei a porta?", label: "fechadura", track: [[2.0, 0.328, 0.24, 0.495, 0.472], [2.6, 0.328, 0.24, 0.49, 0.47]] },
];

/** The last question: a still of a wallet on a hall table (900 × 580), small, in a card. */
const WALLET = { w: 900, h: 580, box: [551, 303, 659, 359] };
const WalletShot: React.FC<{ len: number }> = ({ len }) => {
  const frame = useCurrentFrame();
  const s = mix(1.04, 1.0, ramp(frame, 0, len, theme.ease.out));
  const left = (1920 - WALLET.w) / 2;
  const top = 150;
  const [x0, y0, x1, y1] = WALLET.box;
  return (
    <AbsoluteFill>
      <Paper />
      <div style={{ position: "absolute", left, top, width: WALLET.w, height: WALLET.h, transform: `scale(${s})`, borderRadius: 24, overflow: "hidden", boxShadow: shadow.card }}>
        <Img src={staticFile("stock/stills/wallet-hall-table.jpg")} style={{ width: "100%", height: "100%" }} />
        <LockBox r={{ x: x0, y: y0, w: x1 - x0, h: y1 - y0 }} at={0} label="carteira" size={24} fast />
      </div>
      <div style={{ position: "absolute", left: 110, bottom: 100 }}>
        <Title text="Onde está a carteira?" size={104} max={1700} at={0} entrance="cut" />
      </div>
      <SmallPrint text="imagem de arquivo" style={{ right: 60, bottom: 44 }} />
    </AbsoluteFill>
  );
};

const MontageShot: React.FC<{ shot: Shot; len: number }> = ({ shot, len }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = shot.start + frame / fps;
  const z = shot.zoom ?? 1;
  const s = mix(1.06, 1.0, ramp(frame, 0, len, theme.ease.out)) * z;
  const r = trackAt(shot.track, t);
  return (
    <AbsoluteFill style={{ background: theme.colors.ink }}>
      <AbsoluteFill style={{ transform: `scale(${s})` }}>
        <Daylight lift={shot.lift ?? 1.08}>
          <StockClip name={shot.slot} />
        </Daylight>
        <LockBox r={r} at={0} label={shot.label} size={26} fast />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 55%, ${alpha(theme.colors.ink, 0.5)} 100%)` }} />
      <div style={{ position: "absolute", left: 110, bottom: 100 }}>
        <Title text={shot.q} size={104} max={1700} at={0} entrance="cut" color={theme.colors.white} />
      </div>
    </AbsoluteFill>
  );
};

export const Montage: React.FC = () => (
  <AbsoluteFill style={{ background: theme.colors.ink }}>
    {[...SHOTS, null].map((shot, i) => {
      const from = beatFrame(i);
      const len = beatFrame(i + 1) - from;
      return (
        <React.Fragment key={shot?.slot ?? "wallet"}>
          <Sequence from={from} durationInFrames={len} layout="none">
            {shot ? <MontageShot shot={shot} len={len} /> : <WalletShot len={len} />}
            <Sfx at={2} role="lockon" volume={0.16} />
          </Sequence>
          <Sfx at={from} role="boom" variant={i} volume={0.34} lead={2} />
        </React.Fragment>
      );
    })}
    {/* a swell over the last shots that stops dead on the cut into the stop */}
    <Sfx at={MONTAGE_FRAMES - 34} role="swell" volume={0.4} lead={0} />
    <SmallPrint text="imagens de arquivo" dark style={{ right: 60, bottom: 44 }} />
  </AbsoluteFill>
);

/** The hard stop: a beat of white, in silence. */
export const Stop: React.FC = () => (
  <AbsoluteFill>
    <Paper />
    <Sfx at={0} role="stop" volume={0.6} lead={1} />
  </AbsoluteFill>
);
