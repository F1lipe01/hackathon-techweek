// Shot 5. Ask (the part the team liked in v3), now with the keys: the phone tilts in over the bright hall; "Where are
// my keys?" is typed; the answer arrives with the photo, which grows into the frame: a match cut into the hall table,
// where the keys lie, boxed.
import React from "react";
import { AbsoluteFill, Freeze, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { AppFrame, Assistant, Msg, PT_W, typeFrames } from "../appui";
import { SmallPrint, Title } from "../type";
import { Daylight, FloatPhone, HomeBackdrop, LockBox, SCREEN, Track, mix, phoneWidth, ramp, screenSize, trackAt } from "../ui";
import { StockClip, StockStill } from "../stock";
import { Sfx } from "../sound";
import { SHOT_FRAMES, onBeat } from "../timeline";

export const ASK_FRAMES = SHOT_FRAMES.ask;
const B = (n: number) => onBeat("ask", n);

const PHONE_H = 940;
const PW = phoneWidth(PHONE_H);
const SW = screenSize(PHONE_H).w;
const K = SW / PT_W;
const PHONE = { x: 1300, y: 540 };
const Q = "Where are my keys?";
const TYPE_AT = 22;
const SEND = TYPE_AT + typeFrames(Q) + 6;
const ANSWER = SEND + 28;
const MATCH = B(11);
const MATCH_LEN = 26;
// the answer card's photo, in app points (measured on a still)
const THUMB = { x: 40, y: 356, w: 46, h: 46 };
// the keys on the hall table (leaving-home-keys-1, frame fractions)
const KEYS: Track = [[0, 0.256, 0.575, 0.541, 0.668], [1.6, 0.25, 0.575, 0.535, 0.668]];

/** A still of the keys on the table, cropped to the keys, for the answer card. */
export const KeysThumb: React.FC<{ size: number }> = ({ size }) => {
  const W = size * 3.2;
  const H = (W * 9) / 16;
  return (
    <div style={{ position: "relative", width: size, height: size, overflow: "hidden" }}>
      <Freeze frame={0}>
        <div style={{ position: "absolute", left: size / 2 - 0.398 * W, top: size / 2 - 0.62 * H, width: W, height: H }}>
          <StockClip name="hall-keys" />
        </div>
      </Freeze>
    </div>
  );
};

export const askMsgs = (sheetAt = 6): Msg[] => [
  { kind: "user", text: Q, typeAt: TYPE_AT - (6 - sheetAt), sendAt: SEND - (6 - sheetAt) },
  { kind: "bot", text: "On the hall table, in the Hall, at 08:12.", at: ANSWER - (6 - sheetAt), card: { title: "Keys", status: "On the hall table · 08:12", thumb: <KeysThumb size={46} /> } },
];

export const Ask: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // where the answer's photo sits on screen (the phone is nearly flat by then)
  const sx = PHONE.x - PW / 2 + PW * SCREEN.left;
  const sy = PHONE.y - PHONE_H / 2 + PHONE_H * SCREEN.top;
  const thumb = { x: sx + THUMB.x * K, y: sy + THUMB.y * K, w: THUMB.w * K, h: THUMB.h * K };
  const tc = { x: thumb.x + thumb.w / 2, y: thumb.y + thumb.h / 2 };
  const push = mix(1, 1.75, ramp(frame, ANSWER + 4, MATCH - 4, theme.ease.inOut));

  // the match cut: the photo's rectangle grows to the whole frame, the keys inside it
  const p = ramp(frame, MATCH, MATCH + MATCH_LEN, theme.ease.inOut);
  const start = { x: tc.x - (thumb.w * push) / 2, y: tc.y - (thumb.h * push) / 2, w: thumb.w * push, h: thumb.h * push };
  const rect = { x: mix(start.x, 0, p), y: mix(start.y, 0, p), w: mix(start.w, 1920, p), h: mix(start.h, 1080, p) };
  const keys = trackAt(KEYS, 0);
  const keysW = mix(start.w * 1.15, keys.w * 1.9, p);
  const sc = keysW / keys.w;
  const kc = { x: mix(tc.x, 960, p), y: mix(tc.y, 560, p) };
  const fx = kc.x - (keys.x + keys.w / 2) * sc;
  const fy = kc.y - (keys.y + keys.h / 2) * sc;
  const keysRect = { x: kc.x - (keys.w * sc) / 2, y: kc.y - (keys.h * sc) / 2, w: keys.w * sc, h: keys.h * sc };

  return (
    <AbsoluteFill>
      <Sfx at={2} role="whoosh" volume={0.3} />
      <Sfx at={6} role="swipe" variant={2} volume={0.35} />
      <Sfx at={TYPE_AT} role="typing" volume={0.22} lead={0} />
      <Sfx at={SEND} role="tap" volume={0.35} />
      <Sfx at={ANSWER} role="notify" volume={0.3} />
      <Sfx at={MATCH} role="whoosh" volume={0.38} />
      <Sfx at={MATCH + MATCH_LEN + 2} role="lockon" volume={0.4} />
      <HomeBackdrop>
        <StockClip name="hall" />
      </HomeBackdrop>
      <div style={{ position: "absolute", left: 110, top: 470, opacity: 1 - ramp(frame, MATCH, MATCH + 10, theme.ease.in) }}>
        <Title text="Basta perguntar." size={104} max={860} at={10} entrance="blur" />
      </div>
      <FloatPhone height={PHONE_H} x={PHONE.x} y={PHONE.y} at={2} push={push} origin={`${tc.x - (PHONE.x - PW / 2)}px ${tc.y - (PHONE.y - PHONE_H / 2)}px`}>
        <AppFrame screenW={SW}>
          <Assistant msgs={askMsgs()} sheetAt={6} />
        </AppFrame>
      </FloatPhone>
      {frame >= MATCH ? (
        <div style={{ position: "absolute", left: rect.x, top: rect.y, width: rect.w, height: rect.h, overflow: "hidden", borderRadius: mix(10, 0, p) }}>
          <div style={{ position: "absolute", left: -rect.x, top: -rect.y, width: 1920, height: 1080 }}>
            <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transformOrigin: "0 0", transform: `translate(${fx}px, ${fy}px) scale(${sc})` }}>
              <Daylight lift={1.1}>
                <StockStill name="hall-keys" />
              </Daylight>
            </div>
          </div>
        </div>
      ) : null}
      {frame >= MATCH + MATCH_LEN ? (
        <>
          <LockBox r={keysRect} at={MATCH + MATCH_LEN + 2} label="Mesa da entrada · 08:12" size={26} />
          <SmallPrint text="imagens de arquivo" dark style={{ right: 60, bottom: 44 }} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};
