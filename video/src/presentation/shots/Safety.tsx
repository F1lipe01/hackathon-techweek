// The knife lives only in the proposal's text: no stock clip shows a real knife (OWLv2's "a knife" boxes there are a
// pestle and a cat's ear), so no "faca" box is ever drawn. The floodlight is an overlay effect, marked "ilustração".
// Shots 9–12. The safety section (docs/pt/18-casos-de-uso.md, "Os 8 casos para a apresentação"): each use case is a
// scene of stock footage with real OWLv2 boxes locking on, then the alert on a phone. The hooks are the titles; the
// alerts are the doc's. Cases the prototype does not do today are labelled "conceito"; stock "imagens de arquivo".
import React from "react";
import { AbsoluteFill, Freeze, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha, app, shadow } from "../tokens";
import { SmallPrint, Title } from "../type";
import { Check, Daylight, HomeBackdrop, LockBox, Notice, Phone, Rect, Track, clamp, mix, ramp, trackAt } from "../ui";
import { LineIcon } from "../icons";
import { StockClip, StockStill, cover } from "../stock";
import { useStockBoxes } from "../boxes";
import { Sfx } from "../sound";
import { SHOT_FRAMES, onBeat } from "../timeline";

export const CAT_FRAMES = SHOT_FRAMES.cat;
export const DOG_FRAMES = SHOT_FRAMES.dog;
export const ELDER_FRAMES = SHOT_FRAMES.elder;
export const NIGHT_FRAMES = SHOT_FRAMES.night;

/* ------------------------------------------------------------------ pieces */

/** The app's proposal, in its card style, accepted with one tap. */
const ProposalCard: React.FC<{ at: number; tapAt: number; text: string }> = ({ at, tapAt, text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.smooth });
  const on = spring({ frame: frame - tapAt - 3, fps, config: theme.spring.snappy });
  const tap = frame - tapAt;
  const press = tap >= 0 && tap < 8 ? Math.sin((tap / 8) * Math.PI) : 0;
  const ripple = interpolate(tap, [0, 16], [0, 1], { ...clamp, easing: theme.ease.out });
  if (frame < at) return null;
  return (
    <div
      style={{
        width: 660, boxSizing: "border-box", borderRadius: 28, background: alpha(app.bg, 0.97), padding: "22px 24px", boxShadow: shadow.card,
        opacity: interpolate(p, [0, 0.5], [0, 1], clamp), transform: `translateY(${50 * (1 - p)}px)`,
      }}
    >
      <div style={{ fontFamily: theme.fonts.app, fontSize: 17, fontWeight: 600, color: app.muted, marginBottom: 10 }}>A app propõe</div>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <LineIcon name="bell" size={34} color={app.ink} draw={ramp(frame, at + 4, at + 20, theme.ease.out)} />
        <div style={{ flex: 1, fontFamily: theme.fonts.app, fontSize: 24, fontWeight: 600, color: app.ink2, lineHeight: 1.28 }}>{text}</div>
        <div
          style={{
            position: "relative", flex: "none", width: 150, height: 50, borderRadius: 999, overflow: "hidden", display: "grid", placeItems: "center",
            background: alpha(app.teal, 1 - on), border: `2px solid ${alpha(app.teal, Math.min(1, on))}`, boxSizing: "border-box",
            fontFamily: theme.fonts.app, fontSize: 20, fontWeight: 600, color: app.ink, transform: `scale(${1 - 0.06 * press})`,
          }}
        >
          <span style={{ position: "absolute", opacity: interpolate(on, [0, 0.4], [1, 0], clamp) }}>Ativar</span>
          <span style={{ position: "absolute", display: "flex", gap: 8, alignItems: "center", opacity: interpolate(on, [0.3, 0.8], [0, 1], clamp) }}>
            <Check size={22} color={app.teal} draw={on} stroke={3.2} />
            Ativo
          </span>
          {tap >= 0 && tap < 16 ? (
            <span style={{ position: "absolute", left: "50%", top: "50%", width: 160, height: 160, marginLeft: -80, marginTop: -80, borderRadius: "50%", background: alpha(app.ink, 0.18 * (1 - ripple)), transform: `scale(${ripple})` }} />
          ) : null}
        </div>
      </div>
    </div>
  );
};

/** A phone on its lock screen, rising in with a slight tilt, where a notification arrives. */
const LockPhone: React.FC<{ at: number; height?: number; time: string; caption?: string; children: React.ReactNode }> = ({ at, height = 700, time, caption, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: { damping: 17, stiffness: 90, mass: 1 } });
  if (frame < at) return null;
  return (
    <div style={{ transform: `perspective(1800px) translateY(${300 * (1 - p)}px) rotateX(${18 * (1 - p)}deg) rotateZ(${-6 * (1 - p)}deg)`, opacity: interpolate(p, [0, 0.3], [0, 1], clamp) }}>
      {caption ? <div style={{ fontFamily: theme.fonts.mono, fontSize: 19, color: alpha(theme.colors.white, 0.85), textAlign: "center", marginBottom: 14 }}>{caption}</div> : null}
      <div style={{ position: "relative" }}>
        <Phone height={height}>
          <AbsoluteFill style={{ background: `linear-gradient(170deg, ${theme.colors.labsDeep}, ${theme.colors.ink} 70%)` }}>
            <div style={{ position: "absolute", top: "11%", left: 0, right: 0, textAlign: "center", fontFamily: theme.fonts.display, fontWeight: 500, fontSize: height * 0.11, color: alpha(theme.colors.white, 0.92), letterSpacing: "-0.02em" }}>
              {time}
            </div>
          </AbsoluteFill>
        </Phone>
        {/* the notification pops out of the phone at a readable size */}
        <div style={{ position: "absolute", top: height * 0.34, left: "50%", transform: "translateX(-50%)" }}>{children}</div>
      </div>
    </div>
  );
};

/** A device in the home reacting: a lamp chip that changes colour. */
const LampChip: React.FC<{ at: number; label: string; color: string; state: string }> = ({ at, label, color, state }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.bouncy });
  if (frame < at) return null;
  return (
    <div
      style={{
        display: "inline-flex", alignItems: "center", gap: 14, padding: "12px 22px 12px 14px", borderRadius: 999, background: alpha(theme.colors.white, 0.95),
        boxShadow: `0 18px 36px -16px ${alpha(theme.colors.ink, 0.5)}`, transform: `scale(${0.6 + 0.4 * p})`, opacity: Math.min(1, p * 1.6), transformOrigin: "0 50%",
        fontFamily: theme.fonts.display, fontSize: 26, fontWeight: 600, color: theme.colors.ink, whiteSpace: "nowrap",
      }}
    >
      <span style={{ width: 22, height: 22, borderRadius: 22, background: color, boxShadow: `0 0 18px 4px ${alpha(color, 0.6)}` }} />
      {label}
      <span style={{ fontFamily: theme.fonts.mono, fontSize: 18, fontWeight: 400, color: theme.colors.inkDim }}>{state}</span>
    </div>
  );
};

/** Boxes from public/stock/boxes for this clip, at this frame, as lock-ons; none until the file exists. */
const ClipBoxes: React.FC<{ name: string; from?: number; labels: Record<string, string>; at: number; alertAt?: number; fadeAt?: number; minScore?: number; strong?: boolean }> = ({ name, from = 0, labels, at, alertAt, fadeAt, minScore, strong }) => {
  const frame = useCurrentFrame();
  const boxes = useStockBoxes(name, frame - from, minScore);
  return (
    <>
      {boxes
        .filter((b) => labels[b.label])
        .map((b, i) => (
          <LockBox key={b.label + i} r={b.rect as Rect} at={at + i * 6} label={labels[b.label]} alertAt={alertAt} fadeAt={fadeAt} size={strong ? 26 : 22} strong={strong} />
        ))}
    </>
  );
};

const Scrims: React.FC = () => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, ${alpha(theme.colors.ink, 0.6)}, transparent 30%, transparent 68%, ${alpha(theme.colors.ink, 0.5)})` }} />
);

/* ------------------------------------------------------------------ shot 9: a knife on the counter; the cat jumps (S1) */

export const Cat: React.FC = () => {
  const frame = useCurrentFrame();
  const B = (n: number) => onBeat("cat", n);
  const s = mix(1.0, 1.1, ramp(frame, 0, CAT_FRAMES, theme.ease.inOut));
  return (
    <AbsoluteFill style={{ background: theme.colors.ink }}>
      <Sfx at={B(1)} role="lockon" volume={0.35} />
      <Sfx at={B(4)} role="tap" volume={0.4} />
      <Sfx at={B(7)} role="alert" volume={0.45} />
      <AbsoluteFill style={{ transform: `scale(${s})` }}>
        <Daylight lift={1.06}>
          <StockClip name="cat" note="um gato na bancada da cozinha" />
        </Daylight>
        {/* only the cat: no stock clip shows a real knife (OWLv2's "a knife" boxes there are a pestle and an ear) */}
        <ClipBoxes name="cat" labels={{ "a cat": "gato" }} at={B(1)} alertAt={B(6)} />
      </AbsoluteFill>
      <Scrims />
      <div style={{ position: "absolute", left: 110, bottom: 100 }}>
        <Title text="A cozinha, mais segura." size={72} max={1150} at={4} entrance="wipe" color={theme.colors.white} />
      </div>
      <div style={{ position: "absolute", left: 110, top: 80, opacity: 1 - ramp(frame, B(6) - 6, B(6) + 4, theme.ease.in) }}>
        <ProposalCard at={B(1) + 4} tapAt={B(4)} text="Avisar se o gato subir à bancada perto de uma faca" />
      </div>
      <div style={{ position: "absolute", left: 110, top: 90 }}>
        <LampChip at={B(6) + 4} label="lâmpada da cozinha" color={theme.colors.alert} state="vermelha" />
      </div>
      <div style={{ position: "absolute", right: 240, top: 190 }}>
        <LockPhone at={B(6)} time="16:42">
          <Notice at={B(7)} title="Altice Home" text="O gato subiu à bancada." tone="safety" width={560} actions={["Tocar a sirene", "Ignorar"]} />
        </LockPhone>
      </div>
      <SmallPrint text="imagens de arquivo · conceito" dark style={{ right: 60, bottom: 44 }} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ shot 10: the dog and its bowl */

const DayLine: React.FC<{ at: number; to: number; from?: [number, number]; end?: [number, number]; label: React.ReactNode; redAt?: number; width?: number }> = ({ at, to, from = [7, 0], end = [18, 0], label, redAt, width = 1100 }) => {
  const frame = useCurrentFrame();
  const p = ramp(frame, at, at + 14, theme.ease.out);
  const run = ramp(frame, at + 8, to, theme.ease.inOut);
  const m0 = from[0] * 60 + from[1];
  const m1 = end[0] * 60 + end[1];
  const minutes = Math.round(mix(m0, m1, run));
  const clock = `${String(Math.floor(minutes / 60)).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
  const red = redAt !== undefined && frame >= redAt;
  const hhmm = (m: number) => `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
  return (
    <div style={{ width, boxSizing: "border-box", padding: "24px 30px", borderRadius: 24, background: alpha(theme.colors.ink, 0.72), opacity: p, transform: `translateY(${40 * (1 - p)}px)` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", fontFamily: theme.fonts.mono, color: theme.colors.white }}>
        <span style={{ fontSize: 26 }}>{label}</span>
        <span style={{ fontSize: 38, fontVariantNumeric: "tabular-nums", fontWeight: 500, color: red ? theme.colors.alert : theme.colors.white }}>{clock}</span>
      </div>
      <div style={{ position: "relative", height: 10, marginTop: 18, borderRadius: 5, background: alpha(theme.colors.white, 0.18) }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${run * 100}%`, borderRadius: 5, background: red ? theme.colors.alert : alpha(theme.colors.white, 0.75) }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, fontFamily: theme.fonts.mono, fontSize: 17, color: alpha(theme.colors.white, 0.6) }}>
        <span>{hhmm(m0)}</span>
        <span>{hhmm(m1)}</span>
      </div>
    </div>
  );
};

export const Dog: React.FC = () => {
  const frame = useCurrentFrame();
  const B = (n: number) => onBeat("dog", n);
  const s = mix(1.12, 1.0, ramp(frame, 0, DOG_FRAMES, theme.ease.out));
  return (
    <AbsoluteFill style={{ background: theme.colors.ink }}>
      <Sfx at={4} role="lockon" volume={0.3} />
      <Sfx at={B(5)} role="notify" volume={0.35} />
      <AbsoluteFill style={{ transform: `scale(${s})` }}>
        <Daylight>
          <StockClip name="dog-home" note="um cão em casa" />
        </Daylight>
        <ClipBoxes name="dog-home" labels={{ "a dog": "cão", "a pet bowl": "tigela" }} at={4} />
      </AbsoluteFill>
      <Scrims />
      <div style={{ position: "absolute", left: 1190, bottom: 100 }}>
        <DayLine at={B(1)} to={B(5)} width={630} label={<>tigela · <b style={{ fontWeight: 600 }}>0</b> visitas hoje</>} />
      </div>
      <div style={{ position: "absolute", left: 110, top: 100 }}>
        <Notice at={B(5)} title="Altice Home" text="O cão ainda não comeu hoje." width={580} tag="18:00" />
      </div>
      <SmallPrint text="imagens de arquivo · conceito" dark style={{ right: 60, bottom: 44 }} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ shot 10: noon, and grandma has not come to the kitchen (C2) */
// Her normal mornings first (a real older woman: tea by the window, then reading; her box and the time), then today:
// the kitchen empty until noon, the clock turning red, and the alert on her daughter's hand-held phone.
const TEA: Track = [[1.2, 0.274, 0.0, 0.907, 0.995], [3.2, 0.269, 0.0, 0.909, 0.996]];
const READING: Track = [[4.0, ...cover([0.146, 0.06, 0.714, 1.0], 1920 / 1013.3, 1)] as [number, number, number, number, number], [6.0, ...cover([0.097, 0.076, 0.816, 0.998], 1920 / 1013.3, 1)] as [number, number, number, number, number]];

const DayChip: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", right: 110, top: 96, padding: "12px 26px", borderRadius: 999, background: alpha(theme.colors.white, 0.94), fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 32, color: theme.colors.ink }}>
    {text}
  </div>
);

export const Elder: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const B = (n: number) => onBeat("elder", n);
  const READ = B(4);
  const TODAY = B(8);
  const PHONE = B(13);
  return (
    <AbsoluteFill style={{ background: theme.colors.ink }}>
      <Sfx at={4} role="lockon" volume={0.35} />
      <Sfx at={READ} role="whoosh-short" volume={0.25} />
      <Sfx at={READ + 4} role="lockon" volume={0.3} />
      <Sfx at={TODAY} role="whoosh" volume={0.3} />
      <Sfx at={B(12)} role="tick" volume={0.35} />
      <Sfx at={PHONE} role="whoosh-short" volume={0.25} />
      <Sfx at={B(14)} role="notify" volume={0.38} />
      {frame < READ ? (
        <AbsoluteFill style={{ transform: `scale(${mix(1.0, 1.05, ramp(frame, 0, READ))})` }}>
          <Daylight>
            <StockClip name="elder-tea" />
          </Daylight>
          <LockBox r={trackAt(TEA, 1.2 + frame / fps)} at={4} label="pessoa · 07:42" size={26} labelInside />
          <DayChip text="Segunda-feira" />
        </AbsoluteFill>
      ) : frame < TODAY ? (
        <AbsoluteFill style={{ transform: `scale(${mix(1.04, 1.0, ramp(frame, READ, TODAY))})` }}>
          <Daylight>
            <StockClip name="elder-reading" from={READ} />
          </Daylight>
          <LockBox r={trackAt(READING, 4.0 + (frame - READ) / fps)} at={READ + 4} label="pessoa · 08:05" size={26} labelInside />
          <DayChip text="Terça-feira" />
        </AbsoluteFill>
      ) : frame < PHONE ? (
        <AbsoluteFill>
          <AbsoluteFill style={{ transformOrigin: "28% 50%", transform: `scale(${1.36 * mix(1, 1.06, ramp(frame, TODAY, PHONE))})` }}>
            <Daylight lift={1.18}>
              <StockStill name="kitchen-empty" />
            </Daylight>
          </AbsoluteFill>
          <DayChip text="Hoje" />
          <div style={{ position: "absolute", left: 110, bottom: 220 }}>
            <DayLine at={TODAY + 4} to={B(12)} end={[12, 0]} redAt={B(12)} label={<>cozinha · <b style={{ fontWeight: 600 }}>ninguém</b> desde as 07:00</>} />
          </div>
        </AbsoluteFill>
      ) : (
        <AbsoluteFill>
          <AbsoluteFill style={{ transform: `scale(${mix(1.0, 1.08, ramp(frame, PHONE, ELDER_FRAMES))})` }}>
            <Daylight>
              <StockClip name="phone-sofa" from={PHONE} />
            </Daylight>
          </AbsoluteFill>
          <div style={{ position: "absolute", left: 1150, top: 120 }}>
            <div style={{ display: "inline-block", padding: "8px 16px", borderRadius: 999, background: alpha(theme.colors.ink, 0.72), fontFamily: theme.fonts.mono, fontSize: 20, color: theme.colors.white, marginBottom: 18 }}>
              telemóvel da filha
            </div>
            <Notice at={B(14)} title="Altice Home" text="Ninguém passou na cozinha desde as 7h." width={640} tag="12:00" />
          </div>
        </AbsoluteFill>
      )}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 60%, ${alpha(theme.colors.ink, 0.45)} 100%)` }} />
      {frame >= TODAY ? (
        <div style={{ position: "absolute", left: 110, bottom: 100 }}>
          <Title text="Meio-dia, e a avó não veio à cozinha." size={68} max={1300} at={TODAY + 2} entrance="track" color={theme.colors.white} />
        </div>
      ) : null}
      <SmallPrint text="imagens de arquivo" dark style={{ right: 60, bottom: 44 }} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ shot 11: what happened at 4 a.m.? (T2) */
// Not an alarm: the night, briefly (the clip lifted bright), then the next morning in a bright home, where the home's
// memory answers with the night's unusual events, each with an image. The bark is only a label: "conceito".

const PinIcon: React.FC<{ on: number }> = ({ on }) => (
  <svg viewBox="0 0 24 24" width={28} height={28}>
    <path d="M9 3h6l-1 6 3 3H7l3-3-1-6Z" fill={on > 0.5 ? app.teal : "none"} stroke={on > 0.5 ? app.teal : app.muted} strokeWidth={1.8} strokeLinejoin="round" />
    <path d="M12 12v8" stroke={on > 0.5 ? app.teal : app.muted} strokeWidth={1.8} strokeLinecap="round" />
  </svg>
);

/** A still crop of the night clip around the person, lifted bright. */
const NightCrop: React.FC<{ size: number }> = ({ size }) => {
  const box = { cx: 0.536, cy: 0.6, h: 0.36 };
  const k = (size * 0.92) / (box.h * 1080);
  const w = 1920 * k;
  const h = 1080 * k;
  return (
    <div style={{ position: "relative", width: size, height: size, borderRadius: 14, overflow: "hidden", background: theme.colors.ink }}>
      <Freeze frame={30}>
        <div style={{ position: "absolute", left: size / 2 - box.cx * w, top: size / 2 - box.cy * h, width: w, height: h, filter: "grayscale(1) brightness(3.2) contrast(1.1)" }}>
          <StockClip name="garden-night" />
        </div>
      </Freeze>
    </div>
  );
};

const Event: React.FC<{ at: number; time: string; place: string; what: string; tag?: string; thumb?: React.ReactNode; pinAt?: number }> = ({ at, time, place, what, tag, thumb, pinAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.smooth });
  const pin = pinAt !== undefined ? spring({ frame: frame - pinAt, fps, config: theme.spring.snappy }) : 0;
  const tap = pinAt !== undefined ? frame - pinAt : -1;
  const press = tap >= 0 && tap < 8 ? Math.sin((tap / 8) * Math.PI) : 0;
  if (frame < at) return null;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "104px 1fr 40px", gap: 20, alignItems: "center", padding: "16px 18px", borderRadius: 22, background: app.card, opacity: interpolate(p, [0, 0.5], [0, 1], clamp), transform: `translateY(${30 * (1 - p)}px)` }}>
      <div style={{ width: 104, height: 104, borderRadius: 14, background: alpha(app.ink, 0.08), display: "grid", placeItems: "center", overflow: "hidden" }}>
        {thumb ?? <span style={{ fontFamily: theme.fonts.mono, fontSize: 16, color: app.muted }}>sound</span>}
      </div>
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontFamily: theme.fonts.mono, fontSize: 24, fontWeight: 600, color: app.ink }}>{time}</span>
          <span style={{ fontFamily: theme.fonts.app, fontSize: 21, fontWeight: 600, color: app.blue }}>{place}</span>
          {tag ? <span style={{ fontFamily: theme.fonts.mono, fontSize: 15, color: app.muted, border: `1px solid ${alpha(app.muted, 0.6)}`, borderRadius: 999, padding: "1px 10px" }}>{tag}</span> : null}
        </div>
        <div style={{ fontFamily: theme.fonts.app, fontSize: 25, fontWeight: 600, color: app.ink2, marginTop: 4 }}>{what}</div>
      </div>
      <div style={{ transform: `scale(${1 - 0.1 * press})` }}>
        <PinIcon on={pin} />
      </div>
    </div>
  );
};

export const Night: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const B = (n: number) => onBeat("night", n);
  const MORNING = B(5);
  const panel = spring({ frame: frame - MORNING - 6, fps, config: { damping: 20, stiffness: 80, mass: 1 } });
  const bubble = spring({ frame: frame - MORNING - 14, fps, config: theme.spring.smooth });
  return (
    <AbsoluteFill style={{ background: theme.colors.ink }}>
      <Sfx at={B(1)} role="lockon" volume={0.35} />
      <Sfx at={MORNING} role="whip" volume={0.42} />
      <Sfx at={MORNING + 14} role="swipe" volume={0.3} />
      <Sfx at={B(10)} role="notify" volume={0.32} />
      <Sfx at={B(14)} role="tap" volume={0.45} />
      {frame < MORNING ? (
        <AbsoluteFill>
          {/* the night, lifted bright and cool: no moody scene */}
          <AbsoluteFill style={{ filter: "grayscale(1) brightness(3.3) contrast(1.05)", transform: `scale(${mix(1.0, 1.06, ramp(frame, 0, MORNING))})` }}>
            <StockClip name="garden-night" note="jardim à noite, uma silhueta" />
          </AbsoluteFill>
          <AbsoluteFill style={{ background: alpha(theme.colors.labs, 0.16), mixBlendMode: "color" }} />
          <ClipBoxes name="garden-night" labels={{ "a person": "pessoa" }} at={B(1)} strong />
          <div style={{ position: "absolute", left: 110, top: 96, fontFamily: theme.fonts.mono, fontSize: 26, color: theme.colors.white, display: "flex", gap: 14, alignItems: "baseline", textShadow: `0 1px 8px ${alpha(theme.colors.ink, 0.5)}` }}>
            <span>câmara exterior · jardim</span>
            <span style={{ fontSize: 40, fontWeight: 500 }}>04:02</span>
          </div>
          <AbsoluteFill style={{ background: `linear-gradient(180deg, transparent 60%, ${alpha(theme.colors.ink, 0.45)} 100%)` }} />
          <div style={{ position: "absolute", left: 110, bottom: 100 }}>
            <Title text="O que aconteceu às 4h?" size={88} max={1200} at={0} entrance="cut" color={theme.colors.white} />
          </div>
        </AbsoluteFill>
      ) : (
        <AbsoluteFill>
          <HomeBackdrop>
            <StockClip name="living-room" from={MORNING} />
          </HomeBackdrop>
          <div style={{ position: "absolute", left: 110, top: 420 }}>
            <Title text="Na manhã seguinte, pergunta-se." size={56} max={840} at={MORNING + 4} entrance="blur" />
            <div style={{ fontFamily: theme.fonts.display, fontSize: 30, color: theme.colors.inkDim, marginTop: 20, maxWidth: 640, lineHeight: 1.3, opacity: ramp(frame, MORNING + 20, MORNING + 34, theme.ease.out) }}>
              A memória da casa mostra só o que foi invulgar.
            </div>
          </div>
          <div
            style={{
              position: "absolute", right: 120, top: 140, width: 820, boxSizing: "border-box", padding: "28px 28px 24px", borderRadius: 36, background: alpha(app.bg, 0.97),
              boxShadow: `0 50px 100px -30px ${alpha(theme.colors.ink, 0.45)}`, opacity: interpolate(panel, [0, 0.4], [0, 1], clamp),
              transform: `perspective(2000px) translateY(${60 * (1 - panel)}px) rotateY(${-12 * (1 - panel) - 3}deg)`,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", fontFamily: theme.fonts.app, fontSize: 19, fontWeight: 600, color: app.muted }}>
              <span>Assistant</span>
              <span>08:10</span>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16, opacity: interpolate(bubble, [0, 0.5], [0, 1], clamp), transform: `translateY(${16 * (1 - bubble)}px)` }}>
              <div style={{ padding: "13px 22px", borderRadius: 18, background: app.teal, fontFamily: theme.fonts.app, fontSize: 24, fontWeight: 500, color: app.ink }}>What happened last night?</div>
            </div>
            <div style={{ fontFamily: theme.fonts.app, fontSize: 20, color: app.muted, margin: "18px 4px 14px", opacity: ramp(frame, B(10) - 6, B(10) + 4, theme.ease.out) }}>
              Between 3:00 and 5:00, only what is unusual in this home:
            </div>
            <div style={{ display: "grid", gap: 14 }}>
              <Event at={B(10)} time="04:01" place="Living room" what="The dog barked." tag="conceito" />
              <Event at={B(11)} time="04:02" place="Garden" what="Unusual movement: a person." thumb={<NightCrop size={104} />} pinAt={B(14)} />
            </div>
          </div>
        </AbsoluteFill>
      )}
      <SmallPrint text={frame < MORNING ? "imagens de arquivo · conceito · câmara exterior, fora do kit" : "imagens de arquivo · conceito"} dark={frame < MORNING} style={{ right: 60, bottom: 44 }} />
    </AbsoluteFill>
  );
};
