// 7. A app percebe a casa e propõe, safety first (mentor feedback, 18 Nov). The client does not need to be clever or
// configure anything: the app notices what is in the home and proposes sensors, accepted with one tap.
//   1. Hero: a knife on the counter and the cat jumps up → the alert.
//   2. A child near the stove → the parents are alerted first; the siren only if they confirm (docs/pt/14-arquitetura.md §4.4).
//   3. More proposals: the pet, an older person living alone, a parcel at the door, a smart lock (beyond the kit).
// Proposals, drawn as flat graphics and app cards: a vision built on what the prototype does
// (prototype/server.py suggest_for_profile), never measured results. No footage of children, no faces.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../../theme";
import { alpha, app, shadow } from "../tokens";
import { Check, Entrance, Kicker, Leave, SceneExit, Sfx, Wand, WordReveal, clamp, ramp } from "../ui";
import { KnifeAndCat, Stove } from "./Kitchen";

export const SAFETY_FRAMES = 760;

// beats (scene frames)
const B1 = 92;     // kitchen: knife and cat
const TAP1 = 196;  // the proposal accepted
const JUMP = 236;  // the cat jumps
const ALERT = 272; // "Há uma faca na bancada e o gato está perto"
const B2 = 384;    // the child near the stove
const B3 = 572;    // more proposals
const GRID_TAPS = [628, 650, 672, 694];

const M = 110;
const CARD = { x: M, y: 250, w: 1040, h: 640 } as const;
const COL = { x: M + 1040 + 50, w: 1920 - 2 * M - 1040 - 50 } as const;

/* ------------------------------------------------------------------ app-style pieces */

const AcceptButton: React.FC<{ tapAt: number }> = ({ tapAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tap = frame - tapAt;
  const press = tap >= 0 && tap < 8 ? Math.sin((tap / 8) * Math.PI) : 0;
  const on = spring({ frame: frame - tapAt - 4, fps, config: theme.spring.snappy });
  const ripple = interpolate(tap, [0, 16], [0, 1], { ...clamp, easing: theme.ease.out });
  return (
    <div
      style={{
        position: "relative", height: 48, width: 150, flex: "none", borderRadius: 999, overflow: "hidden",
        background: alpha(app.teal, Math.max(0, 1 - on)), border: `2px solid ${alpha(app.teal, Math.min(1, on))}`, boxSizing: "border-box",
        transform: `scale(${1 - 0.05 * press})`, display: "grid", placeItems: "center",
        fontFamily: theme.fonts.app, fontSize: 20, fontWeight: 600, color: app.ink,
      }}
    >
      <span style={{ position: "absolute", opacity: interpolate(on, [0, 0.4], [1, 0], clamp) }}>Ativar</span>
      <span style={{ position: "absolute", display: "flex", alignItems: "center", gap: 8, opacity: interpolate(on, [0.3, 0.8], [0, 1], clamp) }}>
        <Check size={22} color={app.teal} draw={on} stroke={3.2} />
        Ativado
      </span>
      {tap >= 0 && tap < 16 ? (
        <span
          style={{
            position: "absolute", left: "50%", top: "50%", width: 150, height: 150, marginLeft: -75, marginTop: -75, borderRadius: "50%",
            background: alpha(app.ink, 0.16 * (1 - ripple)), transform: `scale(${ripple})`,
          }}
        />
      ) : null}
    </div>
  );
};

const Status: React.FC<{ tapAt: number }> = ({ tapAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const on = spring({ frame: frame - tapAt - 4, fps, config: theme.spring.snappy });
  return (
    <div style={{ position: "relative", height: 24 }}>
      <span style={{ position: "absolute", left: 0, top: 0, fontFamily: theme.fonts.app, fontSize: 18, fontWeight: 500, color: app.muted, opacity: interpolate(on, [0, 0.4], [1, 0], clamp) }}>
        Proposta da app
      </span>
      <span style={{ position: "absolute", left: 0, top: 0, fontFamily: theme.fonts.app, fontSize: 18, fontWeight: 500, color: app.blue, opacity: on, transform: `translateY(${(1 - on) * 8}px)` }}>
        Ativo
      </span>
    </div>
  );
};

/** A proposal card in the Altice app's style. */
const Proposal: React.FC<{ noticed: string; title: string; preview?: string; tapAt: number; delay: number; width: number; big?: boolean }> = ({
  noticed, title, preview, tapAt, delay, width, big,
}) => (
  <Entrance delay={delay} rise={28}>
    <div style={{ width, boxSizing: "border-box", borderRadius: 26, background: app.card, padding: big ? "30px 30px 28px" : "20px 22px", boxShadow: shadow.soft }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, fontFamily: theme.fonts.mono, fontSize: big ? 19 : 17, color: theme.colors.inkDim, marginBottom: big ? 16 : 12 }}>
        <span style={{ width: 8, height: 8, borderRadius: 8, background: theme.colors.inkDim, opacity: 0.6 }} />
        {noticed}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <Wand size={32} strokeColor={app.wandStroke} sparkColor={app.wandSpark} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontFamily: theme.fonts.app, fontSize: big ? 26 : 23, fontWeight: 600, color: app.ink2, lineHeight: 1.28 }}>{title}</div>
          {preview ? (
            <div style={{ fontFamily: theme.fonts.app, fontSize: big ? 21 : 18, fontWeight: 500, color: app.muted, lineHeight: 1.35, marginTop: 8 }}>“{preview}”</div>
          ) : null}
          <div style={{ marginTop: 6 }}>
            <Status tapAt={tapAt} />
          </div>
        </div>
        <AcceptButton tapAt={tapAt} />
      </div>
    </div>
  </Entrance>
);

/** A phone notification in the Altice app's style (prototype/web/app.css .toast). */
const Toast: React.FC<{ at: number; title: string; text: string; thumb: React.ReactNode; children?: React.ReactNode }> = ({ at, title, text, thumb, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: theme.spring.snappy });
  return (
    <div
      style={{
        width: COL.w, boxSizing: "border-box", borderRadius: 26, background: theme.colors.white, padding: "18px 20px",
        boxShadow: `0 24px 50px -18px ${alpha(theme.colors.ink, 0.35)}`,
        opacity: interpolate(p, [0, 0.5], [0, 1], clamp), transform: `translateY(${interpolate(p, [0, 1], [-60, 0])}px) scale(${interpolate(p, [0, 1], [0.96, 1])})`,
      }}
    >
      <div style={{ display: "grid", gridTemplateColumns: "84px 1fr", gap: 16, alignItems: "center" }}>
        <div style={{ width: 84, height: 84, borderRadius: 14, overflow: "hidden", background: theme.colors.bgAlt }}>{thumb}</div>
        <div>
          <div style={{ fontFamily: theme.fonts.app, fontSize: 19, fontWeight: 700, color: app.ink }}>{title}</div>
          <div style={{ fontFamily: theme.fonts.app, fontSize: 21, fontWeight: 500, color: app.ink, lineHeight: 1.3, marginTop: 4 }}>{text}</div>
        </div>
      </div>
      {children}
    </div>
  );
};

const Step: React.FC<{ n: number; text: string; delay: number; lit?: boolean }> = ({ n, text, delay, lit }) => (
  <Entrance delay={delay} rise={16}>
    <div style={{ display: "flex", alignItems: "center", gap: 18, padding: "12px 0" }}>
      <span
        style={{
          width: 40, height: 40, borderRadius: 20, display: "grid", placeItems: "center", flex: "none",
          background: lit ? theme.colors.ink : alpha(theme.colors.ink, 0.08), color: lit ? theme.colors.white : theme.colors.ink,
          fontFamily: theme.fonts.mono, fontSize: 18, fontWeight: 600,
        }}
      >
        {n}
      </span>
      <span style={{ fontFamily: theme.fonts.display, fontSize: 30, fontWeight: 600, color: theme.colors.ink, letterSpacing: "-0.015em" }}>{text}</span>
    </div>
  </Entrance>
);

/* ------------------------------------------------------------------ the scene */

export const Safety: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardIn = spring({ frame: frame - B1, fps, config: theme.spring.smooth });
  const boxes = ramp(frame, B1 + 26, B1 + 46, theme.ease.out);
  const jump = ramp(frame, JUMP, JUMP + 26, theme.ease.inOut);
  const alert = ramp(frame, ALERT - 6, ALERT, theme.ease.out);
  const toToast = spring({ frame: frame - ALERT, fps, config: theme.spring.smooth });
  const stoveIn = ramp(frame, B2, B2 + 12, theme.ease.out);
  const near = ramp(frame, B2 + 14, B2 + 60, theme.ease.inOut);
  const stoveBoxes = ramp(frame, B2 + 50, B2 + 66, theme.ease.out);
  const push = ramp(frame, B1, B2, theme.ease.inOut);
  const confirmTap = B2 + 128;
  const press = frame - confirmTap >= 0 && frame - confirmTap < 8 ? Math.sin(((frame - confirmTap) / 8) * Math.PI) : 0;

  return (
    <SceneExit duration={SAFETY_FRAMES}>
      <AbsoluteFill>
        <Sfx at={0} name="whoosh" volume={0.14} />
        <Sfx at={TAP1} name="tap" volume={0.32} />
        <Sfx at={JUMP + 4} name="whoosh" volume={0.18} />
        <Sfx at={ALERT} name="chime" volume={0.32} />
        <Sfx at={B2 + 66} name="chime" volume={0.26} />
        <Sfx at={confirmTap} name="tap" volume={0.3} />
        {GRID_TAPS.map((t) => <Sfx key={t} at={t} name="tap" volume={0.3} />)}

        {/* the statement */}
        <Leave at={B1 - 14} length={12} style={{ position: "absolute", left: 0, right: 0, top: 360, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <WordReveal text="Não é preciso configurar nada." size={112} delay={6} per={4} style={{ justifyContent: "center" }} />
          <div style={{ height: 24 }} />
          <WordReveal text="A app percebe a casa e propõe." size={72} weight={500} color={theme.colors.inkDim} delay={34} per={4} hero={["propõe."]} style={{ justifyContent: "center" }} />
        </Leave>

        {/* beats 1–2: the kitchen */}
        {frame >= B1 - 4 && frame < B3 + 14 ? (
          <Leave at={B3 - 6} length={12} style={{ position: "absolute", inset: 0 }}>
            <div style={{ position: "absolute", left: M, top: 92 }}>
              <Kicker n="05" label="A app propõe" delay={B1 + 2} />
              <div style={{ height: 22 }} />
              <div style={{ position: "relative", height: 80, width: 1700 }}>
                <Leave at={B2 - 10} style={{ position: "absolute", inset: 0 }}>
                  <WordReveal text="Uma faca na bancada. Um gato por perto." size={66} delay={B1 + 8} per={3} />
                </Leave>
                {frame >= B2 ? (
                  <div style={{ position: "absolute", inset: 0 }}>
                    <WordReveal text="Uma criança perto do fogão." size={66} delay={B2 + 2} per={3} />
                  </div>
                ) : null}
              </div>
            </div>

            <div
              style={{
                position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 26, overflow: "hidden",
                boxShadow: shadow.card, background: theme.colors.bgAlt,
                opacity: interpolate(cardIn, [0, 0.6], [0, 1], clamp),
                transform: `translateY(${interpolate(cardIn, [0, 1], [40, 0])}px) scale(${interpolate(cardIn, [0, 1], [0.96, 1])})`,
              }}
            >
              <div style={{ position: "absolute", inset: 0, transformOrigin: "50% 62%", transform: `scale(${1 + 0.05 * push})` }}>
                <KnifeAndCat boxes={boxes} jump={jump} alert={alert} />
                {stoveIn > 0 ? (
                  <div style={{ position: "absolute", inset: 0, opacity: stoveIn }}>
                    <Stove near={near} boxes={stoveBoxes} />
                  </div>
                ) : null}
              </div>
              <div
                style={{
                  position: "absolute", left: 24, top: 22, padding: "8px 16px", borderRadius: 999, background: alpha(theme.colors.ink, 0.6),
                  color: theme.colors.white, fontFamily: theme.fonts.mono, fontSize: 19,
                }}
              >
                câmara da cozinha · ilustração
              </div>
            </div>

            {/* right column, beat 1: the proposal, then the alert */}
            <Leave at={B2 - 10} style={{ position: "absolute", left: COL.x, top: CARD.y, width: COL.w }}>
              {frame >= ALERT ? (
                <div style={{ position: "absolute", left: 0, top: 0 }}>
                  <Toast at={ALERT} title="Altice Home · Segurança" text="Há uma faca na bancada e o gato está perto."
                    thumb={<KnifeAndCat boxes={0} jump={1} alert={0} viewBox="395 175 320 320" width={84} height={84} />} />
                </div>
              ) : null}
              <div style={{ transform: `translateY(${210 * toToast}px)` }}>
                <Entrance delay={B1 + 40} rise={14}>
                  <div style={{ fontFamily: theme.fonts.display, fontSize: 26, fontWeight: 500, color: theme.colors.inkDim, marginBottom: 14 }}>A app propõe:</div>
                </Entrance>
                <Proposal
                  noticed="a câmara viu um gato e uma faca" title="Avisar se o gato subir à bancada perto de uma faca"
                  tapAt={TAP1} delay={B1 + 46} width={COL.w}
                />
              </div>
            </Leave>

            {/* right column, beat 2: the parents first; the siren only if they confirm */}
            {frame >= B2 ? (
              <div style={{ position: "absolute", left: COL.x, top: CARD.y, width: COL.w }}>
                <Entrance delay={B2 + 8} rise={14}>
                  <div style={{ fontFamily: theme.fonts.display, fontSize: 24, fontWeight: 500, color: theme.colors.inkDim, lineHeight: 1.3, marginBottom: 16 }}>
                    Proposta ativa: avisar se uma criança se aproximar do fogão ou de uma faca.
                  </div>
                </Entrance>
                {frame >= B2 + 66 ? (
                  <Toast at={B2 + 66} title="Altice Home · Segurança" text="A criança está perto do fogão." thumb={<Stove near={1} boxes={0} />}>
                    <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
                      <div style={{ flex: 1, height: 50, borderRadius: 999, background: app.card, display: "grid", placeItems: "center", fontFamily: theme.fonts.app, fontSize: 19, fontWeight: 600, color: app.ink }}>
                        Está tudo bem
                      </div>
                      <div
                        style={{
                          flex: 1, height: 50, borderRadius: 999, background: app.teal, display: "grid", placeItems: "center", fontFamily: theme.fonts.app,
                          fontSize: 19, fontWeight: 600, color: app.ink, transform: `scale(${1 - 0.05 * press})`,
                        }}
                      >
                        Tocar a sirene
                      </div>
                    </div>
                  </Toast>
                ) : null}
                <div style={{ height: 18 }} />
                <Step n={1} text="Os pais recebem o aviso." delay={B2 + 84} lit={frame >= B2 + 66 && frame < confirmTap} />
                <Step n={2} text="Confirmam com um toque." delay={B2 + 96} lit={frame >= confirmTap && frame < confirmTap + 20} />
                <Step n={3} text="Só então a sirene toca." delay={B2 + 108} lit={frame >= confirmTap + 20} />
              </div>
            ) : null}
          </Leave>
        ) : null}

        {/* beat 3: more proposals, beyond the kit */}
        {frame >= B3 ? (
          <div style={{ position: "absolute", left: M, top: 110, width: 1920 - 2 * M }}>
            <Kicker n="05" label="A app propõe" delay={B3} />
            <div style={{ height: 22 }} />
            <WordReveal text="E propõe o que faz sentido em cada casa." size={66} delay={B3 + 4} per={3} />
            <div style={{ height: 64 }} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
              <Proposal noticed="a câmara viu um cão" title="Avisar se o cão não for à tigela" preview="O cão ainda não foi à tigela hoje." tapAt={GRID_TAPS[0]} delay={B3 + 18} width={834} big />
              <Proposal noticed="uma pessoa vive sozinha" title="Avisar um familiar se ninguém passar pela cozinha" preview="Ninguém passou pela cozinha até ao meio-dia." tapAt={GRID_TAPS[1]} delay={B3 + 24} width={834} big />
              <Proposal noticed="câmara da porta · fora do kit" title="Avisar quando deixarem uma encomenda à porta" preview="Deixaram uma encomenda à porta." tapAt={GRID_TAPS[2]} delay={B3 + 30} width={834} big />
              <Proposal noticed="fechadura inteligente · fora do kit" title="Trancar a porta quando a casa ficar vazia" preview="A porta foi trancada: não está ninguém em casa." tapAt={GRID_TAPS[3]} delay={B3 + 36} width={834} big />
            </div>
          </div>
        ) : null}
        {frame >= B3 ? (
          <div style={{ position: "absolute", left: 0, right: 0, top: 990, display: "flex", justifyContent: "center", opacity: ramp(frame, GRID_TAPS[3] + 10, GRID_TAPS[3] + 30, theme.ease.out) }}>
            <span style={{ fontFamily: theme.fonts.display, fontSize: 24, color: theme.colors.inkDim }}>
              Propostas ilustrativas, aceites com um toque. O protótipo já propõe sensores quando a câmara vê uma criança, um cão ou um gato.
            </span>
          </div>
        ) : null}
      </AbsoluteFill>
    </SceneExit>
  );
};

