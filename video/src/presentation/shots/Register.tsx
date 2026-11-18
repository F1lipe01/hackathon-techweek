// Shot 4. Register, with the keys: a phone floating over a bright, defocused living room tilts in; the app's
// "Add thing" → "Keys" → the keys shown to the camera, the views filling → "Keys added". The app's screens are drawn
// in its own style (appui.tsx); the flow is the prototype's, shown with the keys: "ilustração".
import React from "react";
import { AbsoluteFill, Freeze, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { Added, AddThing, AppFrame, ShowToCamera } from "../appui";
import { SmallPrint, Title } from "../type";
import { FloatPhone, HomeBackdrop, mix, ramp, screenSize } from "../ui";
import { StockClip } from "../stock";
import { Sfx } from "../sound";
import { SHOT_FRAMES, onBeat } from "../timeline";

export const REGISTER_FRAMES = SHOT_FRAMES.register;
const B = (n: number) => onBeat("register", n);

const PHONE_H = 900;
const SW = screenSize(PHONE_H).w;
const TAP = B(4);
const CAM = B(5);
const VIEWS = Array.from({ length: 8 }, (_, i) => CAM + 10 + i * 9);
const DONE = B(11);

/** The keys in the camera's view: the stock clip, framed on the keys (a hand lifts them). Sizes in app points. */
const KeysCam: React.FC<{ w: number; h: number; zoom?: number; freeze?: number; from?: number }> = ({ w, h, zoom = 1.35, freeze, from = 0 }) => {
  const W = w * zoom;
  const H = (W * 9) / 16;
  const c = { x: 0.4, y: 0.56 }; // the keys, in the clip
  const clip = (
    <div style={{ position: "absolute", left: w / 2 - c.x * W, top: Math.min(0, Math.max(h - H, h / 2 - c.y * H)), width: W, height: H }}>
      <StockClip name="keys-shown" from={from} />
    </div>
  );
  return <AbsoluteFill style={{ overflow: "hidden" }}>{freeze !== undefined ? <Freeze frame={freeze}>{clip}</Freeze> : clip}</AbsoluteFill>;
};

const Slide: React.FC<{ from: number; to?: number; children: React.ReactNode }> = ({ from, to, children }) => {
  const frame = useCurrentFrame();
  const inP = ramp(frame, from, from + 10, theme.ease.out);
  const outP = to !== undefined ? ramp(frame, to, to + 10, theme.ease.in) : 0;
  if (frame < from || (to !== undefined && frame > to + 10)) return null;
  return <AbsoluteFill style={{ transform: `translateX(${(1 - inP) * 402 - outP * 402}px)` }}>{children}</AbsoluteFill>;
};

export const Register: React.FC = () => {
  const frame = useCurrentFrame();
  // push in on the phone's top half (the camera view, then "Keys added") so the screen can be read
  const push = mix(1, 1.5, ramp(frame, CAM - 12, CAM + 14, theme.ease.inOut)) * mix(1, 1.04, ramp(frame, CAM + 14, REGISTER_FRAMES));
  return (
    <AbsoluteFill>
      <Sfx at={2} role="whoosh" volume={0.3} />
      <Sfx at={TAP} role="tap" volume={0.45} />
      <Sfx at={CAM - 10} role="swipe" volume={0.4} />
      <Sfx at={CAM - 10} role="whoosh-short" volume={0.15} />
      {VIEWS.map((v, i) => <Sfx key={i} at={v} role={i === 0 || i === 7 ? "shutter" : "tick"} volume={i === 0 || i === 7 ? 0.4 : 0.2} />)}
      <Sfx at={DONE - 10} role="swipe" variant={1} volume={0.4} />
      <Sfx at={DONE - 10} role="whoosh-short" volume={0.15} />
      <HomeBackdrop>
        <StockClip name="living-room" />
      </HomeBackdrop>
      <div style={{ position: "absolute", left: 110, top: 470 }}>
        <Title text="Mostra-se uma vez." size={88} max={800} at={8} entrance="rise" />
      </div>
      <FloatPhone height={PHONE_H} x={1300} y={540} at={0} push={push} origin="50% 250px">
        <AppFrame screenW={SW}>
          <Slide from={-10} to={CAM - 10}>
            <AddThing tapAt={TAP} />
          </Slide>
          <Slide from={CAM - 10} to={DONE - 10}>
            <ShowToCamera from={CAM} views={VIEWS} camera={<KeysCam w={366} h={240} zoom={1.25} from={CAM - 10} />} />
          </Slide>
          <Slide from={DONE - 10}>
            <Added at={DONE} thumbs={[0, 10, 22, 36].map((f) => <KeysCam key={f} w={86} h={82} zoom={2.6} freeze={f} />)} />
          </Slide>
        </AppFrame>
      </FloatPhone>
      <SmallPrint text="ilustração · imagens de arquivo" style={{ left: 110, bottom: 44 }} />
    </AbsoluteFill>
  );
};
