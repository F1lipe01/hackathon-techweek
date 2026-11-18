// 3 · Na app: our app (a copy of the Altice app, simulated data), recorded on screen, in a phone floating over the
// bright home. Three passages at real speed: the question and its answer, the sentence that creates the sensor, the
// door and the message. Each answer and the notification lift out of the screen as cards (the recording's own pixels).
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { IPHONE, IPhone, VideoAt } from "./devices";
import { Body, Chip, Heading, Overline } from "./layers";
import { clamp, Cue, look, warm } from "./look";
import { BlurIn, ContactShadow, Glass, Plate } from "./stage";

const { c, a } = look;

// footage/app-book.mp4 from 33 s, re-encoded with regular keyframes (the original's sparse full-range keyframes made
// Remotion show frames seconds off). Times below stay in the original recording's seconds.
const APP = "real/app-book-33s.mp4";
const APP_T0 = 33;
// app-book.marks.json, plus moments measured on the frames: the replies appear at 39.2 and 48.2, the sensor fires
// at 53.94 (mark "alert") and the notification banner slides in at 54.55.
const MARK = { sentQ: 37.73, answerQ: 39.2, sentS: 46.752, answerS: 48.2, door: 53.943, banner: 54.55 };
// regions of the recording (px of 1206 x 2622): the reply bubble (stable once shown) and the notification banner
const BUBBLE = { x: 66, y: 1827, w: 924, h: 441 };
const BANNER = { x: 30, y: 156, w: 1146, h: 246 };

const SEGS = [
  { from: 36.55, to: 41.3 },
  { from: 45.7, to: 50.0 },
  { from: 53.4, to: 57.6 },
].map((s) => ({ ...s, len: Math.round((s.to - s.from) * theme.fps) }));
const LEAD = 10;
const SEG_START = SEGS.reduce<number[]>((acc, s, i) => [...acc, i === 0 ? LEAD : acc[i - 1] + SEGS[i - 1].len], []);
const at = (seg: number, t: number) => SEG_START[seg] + Math.round((t - SEGS[seg].from) * theme.fps);
export const APP_FRAMES = SEG_START[2] + SEGS[2].len;
const POP_Q = at(0, MARK.answerQ) + 8;
const POP_S = at(1, MARK.answerS) + 10;
const POP_N = at(2, MARK.banner) + 8;
export const APP_CUES: Cue[] = [
  { at: 0, file: "whooshBig" },
  { at: SEG_START[0], file: "typing", dur: at(0, MARK.sentQ) - SEG_START[0] - 2 },
  { at: at(0, MARK.sentQ), file: "tap" },
  { at: POP_Q, file: "swipe" },
  { at: SEG_START[1] - 3, file: "whip" },
  { at: SEG_START[1], file: "typing", dur: at(1, MARK.sentS) - SEG_START[1] - 2 },
  { at: at(1, MARK.sentS), file: "tap" },
  { at: POP_S, file: "swipeAlt" },
  { at: SEG_START[2] - 3, file: "whip" },
  { at: at(2, MARK.door), file: "door" },
  { at: at(2, MARK.door) + 1, file: "whoosh", volume: 0.6 },
  { at: at(2, MARK.banner) - 1, file: "notify" },
  { at: POP_N, file: "swipe" },
];

// the phone
const PH = 900;
const PK = PH / IPHONE.h;
const PW = IPHONE.w * PK;
const PHONE_C = { x: 1330, y: 548 };
const SCR = { x: PHONE_C.x - PW / 2 + IPHONE.sx * PK, y: PHONE_C.y - PH / 2 + IPHONE.sy * PK, k: PK };   // the screen's top-left and px scale

type Rect = { x: number; y: number; w: number; h: number };
const regionOnScreen = (r: typeof BUBBLE): Rect => ({ x: SCR.x + r.x * SCR.k, y: SCR.y + r.y * SCR.k, w: r.w * SCR.k, h: r.h * SCR.k });
const lerp = (p: number, x0: number, x1: number) => x0 + (x1 - x0) * p;

/** A region of the app recording, lifted out of the phone into a floating card. */
const PopOut: React.FC<{ second: number; region: typeof BUBBLE; from: Rect; to: Rect; at: number; until: number }> = ({ second, region, from, to, at: t0, until }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < t0 || frame > until) return null;
  const p = spring({ frame: frame - t0, fps, config: { damping: 17, stiffness: 90, mass: 0.9 } });
  const out = interpolate(frame, [until - 6, until], [1, 0], clamp);
  const r = { x: lerp(p, from.x, to.x), y: lerp(p, from.y, to.y), w: lerp(p, from.w, to.w), h: lerp(p, from.h, to.h) };
  const k = r.w / region.w;
  return (
    <div style={{ position: "absolute", left: r.x, top: r.y, width: r.w, height: r.h, overflow: "hidden", borderRadius: 26 * (r.w / to.w),
      opacity: Math.min(1, p * 3) * out, boxShadow: `0 ${40 * p}px ${70 * p}px -30px ${a(warm.shadow, 0.55)}, 0 8px 20px -12px ${a(c.ink, 0.25)}`,
      transform: `perspective(1600px) rotateY(${(1 - p) * -14}deg)` }}>
      <div style={{ position: "absolute", left: -region.x * k, top: -region.y * k, width: 1206 * k, height: 2622 * k }}>
        <VideoAt src={APP} second={second - APP_T0} />
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const seg = Math.max(0, SEG_START.filter((s) => frame >= s).length - 1);
  const local = Math.max(0, frame - SEG_START[seg]);
  const src = Math.min(SEGS[seg].to, SEGS[seg].from + local / fps);
  const cutIn = seg > 0 ? interpolate(local, [0, 6], [1, 0], { ...clamp, easing: theme.ease.out }) : 0;

  // the phone turns in; a slow dolly all along; a push towards the notification at the end
  const enter = spring({ frame: frame - 2, fps, config: { damping: 18, stiffness: 70, mass: 1.1 } });
  const idle = Math.sin(frame / 44) * 1.3 * enter;
  const notePush = interpolate(frame, [POP_N - 10, POP_N + 30], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const dolly = 1 + 0.035 * interpolate(frame, [0, APP_FRAMES], [0, 1], clamp) + 0.04 * notePush;
  const rotY = -28 * (1 - enter) - 9 + idle;
  const phoneTransform = `perspective(2200px) translateX(${220 * (1 - enter)}px) rotateY(${rotY}deg) rotateX(${8 * (1 - enter) + 2}deg) scale(${(0.88 + 0.12 * enter) * dolly})`;
  // depth of field: the room starts almost in focus and falls out of focus as the phone arrives
  const blur = interpolate(enter, [0, 1], [3, 15]);

  const doorP = interpolate(frame, [at(2, MARK.door), at(2, MARK.door) + 8, at(2, MARK.banner) + 6, at(2, MARK.banner) + 14], [0, 1, 1, 0], { ...clamp, easing: theme.ease.out });
  const S0 = SEG_START[0], S1 = SEG_START[1], S2 = SEG_START[2], END = APP_FRAMES + 20;
  const card = (w: number, region: typeof BUBBLE): Rect => ({ x: 140, y: 480, w, h: (w * region.h) / region.w });

  return (
    <AbsoluteFill>
      <Plate dur={APP_FRAMES} offset={5} blur={blur} zoom={[1.06, 1.12 + 0.03 * notePush]} pan={[-20, 30]} />
      <ContactShadow x={PHONE_C.x + 30} y={PHONE_C.y + PH / 2 + 34} w={520} opacity={0.38 * enter} />

      <div style={{ position: "absolute", left: PHONE_C.x - PW / 2, top: PHONE_C.y - PH / 2, transform: phoneTransform,
        opacity: interpolate(enter, [0, 0.25], [0, 1], clamp) }}>
        <IPhone height={PH}>
          <VideoAt src={APP} second={src - APP_T0} />
          <AbsoluteFill style={{ background: c.white, opacity: cutIn * 0.9 }} />
        </IPhone>
      </div>

      {/* the contact sensor's event: the app has no screen of its own for it */}
      {doorP > 0 ? (
        <div style={{ position: "absolute", left: PHONE_C.x, top: 760, transform: `translate(-50%, -50%) translateY(${(1 - doorP) * 16}px) scale(${0.94 + 0.06 * doorP})`, opacity: doorP }}>
          <Glass strong style={{ borderRadius: 999, display: "flex", alignItems: "center", gap: 14, padding: "14px 26px 14px 16px", whiteSpace: "nowrap" }}>
            <div style={{ width: 42, height: 42, borderRadius: 42, background: a(c.labs, 0.12), display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 15, height: 22, border: `3px solid ${c.labs}`, borderRadius: 2, boxSizing: "border-box",
                transform: "perspective(60px) rotateY(-35deg)", transformOrigin: "left center" }} />
            </div>
            <div style={{ fontFamily: theme.fonts.display, fontSize: 27, fontWeight: 600, color: c.ink }}>Sensor de contacto · porta aberta</div>
          </Glass>
        </div>
      ) : null}

      <PopOut second={src} region={BUBBLE} from={regionOnScreen(BUBBLE)} to={card(620, BUBBLE)} at={POP_Q} until={S1} />
      <PopOut second={src} region={BUBBLE} from={regionOnScreen(BUBBLE)} to={card(620, BUBBLE)} at={POP_S} until={S2} />
      <PopOut second={src} region={BANNER} from={regionOnScreen(BANNER)} to={card(720, BANNER)} at={POP_N} until={END} />

      <div style={{ position: "absolute", left: 140, top: 250, width: 760 }}>
        <BlurIn at={6}><Overline>3 · Na app</Overline></BlurIn>
      </div>
      <Passage from={S0} to={S1} heading="“Onde está o meu livro?”" note="Na secretária, na Work Room, às 16:30." noteAt={POP_Q + 14} noteY={card(620, BUBBLE).y + card(620, BUBBLE).h + 24} />
      <Passage from={S1} to={S2} heading="“Avisa-me se eu sair de casa sem o livro.”" note="Sensor criado: sair de casa sem o livro." noteAt={POP_S + 14} noteY={card(620, BUBBLE).y + card(620, BUBBLE).h + 24} />
      <Passage from={S2} to={END} heading="A porta abre; o livro fica na secretária." note="Mensagem no telemóvel: saíste sem o livro." noteAt={POP_N + 14} noteY={card(720, BANNER).y + card(720, BANNER).h + 24} alert />

      <div style={{ position: "absolute", left: 140, top: 930 }}>
        <BlurIn at={12}>
          <Chip mono bg={a(c.white, 0.85)} color={c.inkDim} style={{ fontSize: 17 }}>Interface: protótipo · dados simulados</Chip>
        </BlurIn>
      </div>
    </AbsoluteFill>
  );
};

/** One passage's caption: the sentence (in Portuguese) above the lifted card, and its translation under it. */
const Passage: React.FC<{ from: number; to: number; heading: string; note: string; noteAt: number; noteY: number; alert?: boolean }> = ({
  from, to, heading, note, noteAt, noteY, alert,
}) => {
  const frame = useCurrentFrame();
  if (frame < from || frame > to) return null;
  const out = interpolate(frame, [to - 4, to], [1, 0], clamp);
  return (
    <div style={{ opacity: out }}>
      <div style={{ position: "absolute", left: 140, top: 300, width: 760 }}>
        <BlurIn at={from + 2}><Heading size={54}>{heading}</Heading></BlurIn>
      </div>
      <div style={{ position: "absolute", left: 140, top: noteY, width: 720 }}>
        <BlurIn at={noteAt}><Body size={28} style={{ color: alert ? c.alert : c.ink }}>{note}</Body></BlurIn>
      </div>
    </div>
  );
};
