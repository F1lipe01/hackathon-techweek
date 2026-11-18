// Shot 6. A sentence becomes a sensor: in the same assistant, "Tell me if I leave home without my keys" is typed and
// the sensor is created; a whip-pan to the same hall (stock), where someone leaves by the front door, from behind, and
// the door sensor's chip; a hard cut to a hand-held phone, whose screen wakes with the notification.
import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha } from "../tokens";
import { AppFrame, Assistant, Msg, typeFrames } from "../appui";
import { SmallPrint, Title } from "../type";
import { Daylight, FloatPhone, HomeBackdrop, Notice, mix, ramp, screenSize, useWhip } from "../ui";
import { StockClip } from "../stock";
import { Sfx } from "../sound";
import { SHOT_FRAMES, onBeat } from "../timeline";
import { askMsgs } from "./Ask";

export const LEAVE_FRAMES = SHOT_FRAMES.leave;
const B = (n: number) => onBeat("leave", n);

const PHONE_H = 940;
const SW = screenSize(PHONE_H).w;
const S = "Tell me if I leave home without my keys";
const TYPE_AT = 10;
const SEND = TYPE_AT + typeFrames(S) + 6;
const REPLY = SEND + 28;
const WHIP = B(7);
const DOOR = B(8);
const HANDS = B(10);
const NOTE = B(11);

// the phone's screen in the stock clip (phone-alert-2, 3–6 s), in frame pixels: it wakes with the notification
const SCREEN_RECT = { x: 855, y: 422, w: 169, h: 353 };

const WakingScreen: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const on = ramp(frame, at, at + 6, theme.ease.out);
  const r = SCREEN_RECT;
  if (on <= 0) return null;
  return (
    <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: 20, overflow: "hidden", opacity: on, background: `linear-gradient(170deg, ${theme.colors.labs}, ${theme.colors.labsDeep} 80%)` }}>
      <div style={{ position: "absolute", top: 4, left: "50%", width: 64, height: 13, marginLeft: -32, borderRadius: 8, background: theme.colors.ink }} />
      <div style={{ position: "absolute", top: 38, left: 0, right: 0, textAlign: "center", fontFamily: theme.fonts.display, fontSize: 34, fontWeight: 500, color: alpha(theme.colors.white, 0.95), letterSpacing: "-0.02em" }}>08:14</div>
      <div style={{ position: "absolute", top: 100, left: 8, right: 8, padding: "7px 8px", borderRadius: 10, background: alpha(theme.colors.white, 0.95), fontFamily: theme.fonts.app, fontSize: 9.5, fontWeight: 600, color: theme.colors.ink, lineHeight: 1.25 }}>
        <div style={{ fontWeight: 700, fontSize: 8 }}>Altice Home</div>
        Saíste sem as chaves.
      </div>
    </div>
  );
};

const DoorChip: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.bouncy });
  if (frame < at) return null;
  return (
    <div
      style={{
        display: "flex", alignItems: "center", gap: 14, padding: "14px 24px 14px 18px", borderRadius: 999, background: alpha(theme.colors.white, 0.95),
        boxShadow: `0 20px 40px -16px ${alpha(theme.colors.ink, 0.5)}`, transform: `scale(${0.6 + 0.4 * p})`, opacity: Math.min(1, p * 1.6),
        fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, color: theme.colors.ink, transformOrigin: "0 50%", whiteSpace: "nowrap",
      }}
    >
      <span style={{ width: 16, height: 16, borderRadius: 16, background: theme.colors.labs, boxShadow: `0 0 0 6px ${alpha(theme.colors.labs, 0.2)}` }} />
      porta aberta
      <span style={{ fontFamily: theme.fonts.mono, fontSize: 18, fontWeight: 400, color: theme.colors.inkDim }}>sensor de contacto do kit</span>
    </div>
  );
};

const WhipIn: React.FC<{ from: number; children: React.ReactNode }> = ({ from, children }) => {
  const frame = useCurrentFrame();
  const p = ramp(frame, from, from + 8, theme.ease.out);
  return <AbsoluteFill style={{ transform: `translateX(${(1 - p) * 1400}px)`, filter: p < 0.98 ? `blur(${(1 - p) * 40}px)` : undefined }}>{children}</AbsoluteFill>;
};

export const Leave: React.FC = () => {
  const frame = useCurrentFrame();
  const whipOut = useWhip(WHIP + 8, { outFrames: 8 });
  const push = ramp(frame, HANDS, LEAVE_FRAMES, theme.ease.inOut);
  // the earlier question and answer are already there; then the sentence
  const msgs: Msg[] = [
    ...askMsgs(-400),
    { kind: "user", text: S, typeAt: TYPE_AT, sendAt: SEND },
    { kind: "bot", text: "Done. I created a sensor; it is also in Menu > Scenarios.", at: REPLY, card: { title: "Left home without the keys", status: "Active", icon: "key" } },
  ];
  const scroll = mix(0, 120, ramp(frame, SEND, REPLY + 10, theme.ease.inOut));
  return (
    <AbsoluteFill style={{ background: theme.colors.ink }}>
      <Sfx at={TYPE_AT} role="typing" volume={0.22} lead={0} />
      <Sfx at={SEND} role="tap" volume={0.35} />
      <Sfx at={REPLY} role="notify" volume={0.28} />
      <Sfx at={WHIP} role="whip" volume={0.45} />
      <Sfx at={DOOR} role="door" volume={0.55} />
      <Sfx at={HANDS} role="whoosh-short" volume={0.25} />
      <Sfx at={NOTE} role="alert" volume={0.45} />

      {frame < WHIP + 8 ? (
        <AbsoluteFill style={whipOut}>
          <HomeBackdrop>
            <StockClip name="hall" />
          </HomeBackdrop>
          <div style={{ position: "absolute", left: 110, top: 470 }}>
            <Title text="Uma frase torna-se um sensor." size={64} max={1000} at={6} entrance="rise" />
          </div>
          <FloatPhone height={PHONE_H} x={1420} y={540} at={-60} push={mix(1, 1.6, ramp(frame, REPLY - 2, REPLY + 18, theme.ease.inOut))} origin="50% 72%">
            <AppFrame screenW={SW}>
              <Assistant msgs={msgs} sheetAt={-60} scroll={scroll} />
            </AppFrame>
          </FloatPhone>
        </AbsoluteFill>
      ) : null}

      {frame >= WHIP + 8 && frame < HANDS ? (
        <WhipIn from={WHIP + 8}>
          <AbsoluteFill style={{ transform: `scale(${mix(1.0, 1.06, ramp(frame, WHIP, HANDS))})` }}>
            <Daylight>
              <StockClip name="leave-door" from={WHIP + 8} />
            </Daylight>
          </AbsoluteFill>
          <div style={{ position: "absolute", left: 110, top: 110 }}>
            <DoorChip at={DOOR} />
          </div>
          <SmallPrint text="imagens de arquivo" dark style={{ right: 60, bottom: 44 }} />
        </WhipIn>
      ) : null}

      {frame >= HANDS ? (
        <AbsoluteFill>
          <AbsoluteFill style={{ transformOrigin: `${SCREEN_RECT.x + SCREEN_RECT.w / 2}px ${SCREEN_RECT.y + SCREEN_RECT.h / 2}px`, transform: `scale(${1 + 0.32 * push})` }}>
            <Daylight>
              <StockClip name="phone-hands" from={HANDS} />
            </Daylight>
            <WakingScreen at={NOTE - 6} />
          </AbsoluteFill>
          <div style={{ position: "absolute", left: 960 - 340, top: 96 }}>
            <Notice at={NOTE} title="Altice Home" text="Saíste sem as chaves. Estão na mesa da entrada." tone="safety" width={680} tag="08:14" />
          </div>
          <SmallPrint text="imagens de arquivo" dark style={{ right: 60, bottom: 44 }} />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
