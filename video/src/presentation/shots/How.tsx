// Act 5, s15 (8 s): how it works, as one diagram that grows, one part per bar, each appearing as it is named, labels on
// the parts. The diagram always fills the width: one part sits in the centre, two share the frame, three spread across
// it; the parts glide to their new places on each bar as the next one arrives. The arrow out of the home carries a
// small crop, not a frame. The privacy line is the payoff.
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { clamp, ramp } from "../ui";
import { Title } from "../type";
import { lerp } from "../geom";
import { alpha } from "../tokens";

const INK = theme.colors.ink;
const ICON = 220;
const ICON_Y = 360;
const SW = 4.5;
const AT = [0, 60, 120]; // one part per bar (50, 52, 54 s)
const LAYOUT = [[960], [600, 1320], [330, 960, 1590]];

const Home: React.FC = () => (
  <svg viewBox="0 0 120 120" width={ICON} height={ICON} fill="none" stroke={INK} strokeWidth={SW} strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 56 60 18l46 38" />
    <path d="M26 48v54h68V48" />
    {/* the home's camera, in a corner of the room */}
    <rect x="66" y="58" width="20" height="14" rx="3" stroke={theme.colors.labs} />
    <path d="M76 72v8" stroke={theme.colors.labs} />
  </svg>
);
const Server: React.FC = () => (
  <svg viewBox="0 0 120 120" width={ICON} height={ICON} fill="none" stroke={INK} strokeWidth={SW} strokeLinecap="round" strokeLinejoin="round">
    <rect x="24" y="22" width="72" height="22" rx="5" />
    <rect x="24" y="50" width="72" height="22" rx="5" />
    <rect x="24" y="78" width="72" height="22" rx="5" />
    <path d="M36 33h10M36 61h10M36 89h10" />
  </svg>
);
const PhoneIcon: React.FC = () => (
  <svg viewBox="0 0 120 120" width={ICON} height={ICON} fill="none" stroke={INK} strokeWidth={SW} strokeLinecap="round" strokeLinejoin="round">
    <rect x="36" y="12" width="48" height="96" rx="10" />
    <path d="M54 22h12" />
    <rect x="43" y="38" width="34" height="14" rx="4" stroke={theme.colors.labs} />
  </svg>
);

/** Where part i sits at `frame`: it glides (one eased move, 0,5 s) to its place in each new layout. */
const xOf = (i: number, frame: number) => {
  let x = LAYOUT[0][0];
  for (let n = 0; n < 3; n++) {
    if (i > n) continue;
    const target = LAYOUT[n][i];
    const from = n === i ? target : x;
    x = lerp(from, target, ramp(frame, AT[n], AT[n] + 15, theme.ease.inOut));
  }
  return x;
};

const Part: React.FC<{ i: number; name: string; what: string; children: React.ReactNode }> = ({ i, name, what, children }) => {
  const frame = useCurrentFrame();
  const at = AT[i];
  if (frame < at) return null;
  const x = xOf(i, frame);
  const p = ramp(frame, at + 4, at + 18, theme.ease.out);
  const l = ramp(frame, at + 10, at + 24, theme.ease.out);
  return (
    <>
      <div style={{ position: "absolute", left: x - ICON / 2, top: ICON_Y - ICON / 2, width: ICON, height: ICON, opacity: p, transform: `scale(${0.92 + 0.08 * p})` }}>{children}</div>
      <div style={{ position: "absolute", left: x - 320, width: 640, top: ICON_Y + ICON / 2 + 26, textAlign: "center", opacity: l, transform: `translateY(${(1 - l) * 10}px)` }}>
        <div style={{ fontFamily: theme.fonts.display, fontSize: 64, fontWeight: 600, color: INK, letterSpacing: "-0.02em", lineHeight: 1.1 }}>{name}</div>
        <div style={{ fontFamily: theme.fonts.display, fontSize: 42, fontWeight: 500, color: theme.colors.inkDim, marginTop: 10 }}>{what}</div>
      </div>
    </>
  );
};

/** A straight arrow between two parts, drawn from the left one; it ends cleanly at its head. */
const Arrow: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const at = AT[i + 1];
  if (frame < at + 6) return null;
  const x0 = xOf(i, frame) + ICON / 2 + 20, x1 = xOf(i + 1, frame) - ICON / 2 - 20;
  const p = ramp(frame, at + 6, at + 20, theme.ease.inOut);
  const head = 20;
  const xe = lerp(x0, x1, p);
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <path d={`M ${x0} ${ICON_Y} H ${xe - head * 0.6}`} stroke={INK} strokeWidth={5} strokeLinecap="round" fill="none" />
      <path d={`M ${xe - head} ${ICON_Y - head * 0.7} L ${xe} ${ICON_Y} L ${xe - head} ${ICON_Y + head * 0.7}`} stroke={INK} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" fill="none" opacity={interpolate(p, [0.2, 0.4], [0, 1], clamp)} />
    </svg>
  );
};

export const S15: React.FC = () => {
  const frame = useCurrentFrame();
  // the crop travels out of the home along the first arrow, as part 2 is named
  const c = ramp(frame, 76, 104, theme.ease.inOut);
  const cropOn = frame >= 76 && frame < 118;
  const cropFade = 1 - ramp(frame, 106, 116, theme.ease.in);
  const a0 = xOf(0, frame) + ICON / 2 + 20, a1 = xOf(1, frame) - ICON / 2 - 20;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <Part i={0} name="Em casa" what="a câmara vê o que mudou"><Home /></Part>
      <Arrow i={0} />
      <Part i={1} name="Altice" what="reconhece as coisas"><Server /></Part>
      <Arrow i={1} />
      <Part i={2} name="Na app" what="respostas e avisos"><PhoneIcon /></Part>
      {cropOn ? (
        <div style={{ position: "absolute", left: lerp(a0, a1 - 60, c) - 50, top: ICON_Y - 120, width: 100, height: 72, borderRadius: 12, overflow: "hidden",
          border: `3px solid ${theme.colors.white}`, boxShadow: `0 10px 24px -10px ${alpha(INK, 0.5)}`, opacity: interpolate(frame, [76, 82], [0, 1], clamp) * cropFade }}>
          <Img src={staticFile("app-stills/view1.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 0, width: 1920, top: 840, display: "flex", justifyContent: "center" }}>
        <Title text="Nenhum vídeo nem imagem completa sai de casa." size={66} max={1760} at={150} entrance="blur" />
      </div>
    </AbsoluteFill>
  );
};
