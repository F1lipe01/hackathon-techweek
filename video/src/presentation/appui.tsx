// The Altice app copy's screens, drawn for the film at the phone's native width (402 pt) and scaled to the phone:
// "Add thing", "Show the keys to the camera", "Keys added", and the assistant sheet. Styles follow
// prototype/web/app.css (Montserrat, its palette, cards, buttons); the UI is in English, like the app.
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { alpha, app } from "./tokens";
import { Check, clamp, ramp } from "./ui";
import { IconName, LineIcon } from "./icons";

export const PT_W = 402;
export const PT_H = 874;

/** The app at native size inside a phone screen of width `screenW`. */
export const AppFrame: React.FC<{ screenW: number; time?: string; dark?: boolean; children: React.ReactNode }> = ({ screenW, time = "08:12", dark, children }) => {
  const k = screenW / PT_W;
  const ink = dark ? theme.colors.white : app.ink;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: PT_W, height: PT_H, transformOrigin: "0 0", transform: `scale(${k})`, background: app.bg, fontFamily: theme.fonts.app, color: app.ink, overflow: "hidden" }}>
      {children}
      {/* status bar and home indicator */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 50, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 30px 0 38px", boxSizing: "border-box", pointerEvents: "none" }}>
        <span style={{ fontSize: 15, fontWeight: 600, color: ink }}>{time}</span>
        <span style={{ display: "flex", gap: 5, alignItems: "flex-end" }}>
          {[5, 7, 9, 11].map((h) => <span key={h} style={{ width: 3, height: h, borderRadius: 1, background: ink }} />)}
          <span style={{ width: 22, height: 11, marginLeft: 6, borderRadius: 3, border: `1.5px solid ${ink}`, boxSizing: "border-box", padding: 1 }}>
            <span style={{ display: "block", width: "80%", height: "100%", borderRadius: 1, background: ink }} />
          </span>
        </span>
      </div>
      <div style={{ position: "absolute", left: "50%", top: 11, width: 122, height: 34, marginLeft: -61, borderRadius: 20, background: theme.colors.ink }} />
      <div style={{ position: "absolute", left: "50%", bottom: 8, width: 136, height: 5, marginLeft: -68, borderRadius: 3, background: ink, opacity: 0.85 }} />
    </div>
  );
};

/** A touch: a soft grey disc that swells and fades, like the app recordings. */
export const Touch: React.FC<{ at: number; x: number; y: number }> = ({ at, x, y }) => {
  const frame = useCurrentFrame();
  const t = frame - at;
  if (t < 0 || t > 14) return null;
  const p = interpolate(t, [0, 14], [0, 1], { ...clamp, easing: theme.ease.out });
  return <div style={{ position: "absolute", left: x - 22, top: y - 22, width: 44, height: 44, borderRadius: 22, background: alpha(app.ink, 0.22 * (1 - p)), transform: `scale(${0.6 + 0.8 * p})` }} />;
};

/* ------------------------------------------------------------------ Add thing */

export const AddThing: React.FC<{ tapAt: number }> = ({ tapAt }) => {
  const frame = useCurrentFrame();
  const rows: { name: string; icon: IconName }[] = [
    { name: "Keys", icon: "key" },
    { name: "Wallet", icon: "wallet" },
    { name: "Glasses", icon: "glasses" },
  ];
  const pressed = frame >= tapAt && frame < tapAt + 8;
  return (
    <AbsoluteFill style={{ background: app.bg }}>
      <div style={{ position: "absolute", left: 22, top: 66, fontSize: 26, color: app.ink }}>‹</div>
      <div style={{ position: "absolute", left: 24, top: 108, fontSize: 24, fontWeight: 700 }}>Add thing</div>
      <div style={{ position: "absolute", left: 24, top: 144, fontSize: 14, color: app.muted }}>Select the thing you want to track.</div>
      <div style={{ position: "absolute", left: 22, right: 22, top: 182, padding: "14px 16px", borderRadius: 18, background: app.list, fontSize: 13, color: app.muted, lineHeight: 1.45 }}>
        <span style={{ display: "inline-block", width: 9, height: 9, borderRadius: 9, background: app.teal, marginRight: 8 }} />
        <b style={{ color: app.ink }}>Looking through your cameras…</b>
        <div>When you choose a thing, hold it in front of a camera for a few seconds. ThingTracker learns what it looks like.</div>
      </div>
      <div style={{ position: "absolute", left: 24, top: 318, fontSize: 14, color: app.ink }}>Available things (9)</div>
      {rows.map((r, i) => (
        <div
          key={r.name}
          style={{
            position: "absolute", left: 22, right: 22, top: 348 + i * 70, height: 60, borderRadius: 18, background: i === 0 && pressed ? app.card : app.list,
            display: "flex", alignItems: "center", gap: 16, padding: "0 18px", fontSize: 15, fontWeight: 500, transform: i === 0 && pressed ? "scale(0.98)" : undefined,
          }}
        >
          <LineIcon name={r.icon} size={26} color={app.ink} draw={ramp(frame, 4 + i * 4, 20 + i * 4, theme.ease.out)} />
          {r.name}
        </div>
      ))}
      <Touch at={tapAt} x={120} y={378} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ Show the keys to the camera */

export const ShowToCamera: React.FC<{ from: number; views: number[]; camera: React.ReactNode }> = ({ from, views, camera }) => {
  const frame = useCurrentFrame();
  const n = views.filter((v) => frame >= v).length;
  const last = views.filter((v) => frame >= v).pop() ?? -100;
  const flash = interpolate(frame - last, [0, 8], [0.32, 0], { ...clamp, easing: theme.ease.out });
  return (
    <AbsoluteFill style={{ background: app.bg }}>
      <div style={{ position: "absolute", left: 24, top: 66, fontSize: 22, color: app.ink }}>✕</div>
      <div style={{ position: "absolute", left: 18, right: 18, top: 104, height: 240, borderRadius: 22, overflow: "hidden", background: theme.colors.ink }}>
        {camera}
        <AbsoluteFill style={{ background: theme.colors.white, opacity: flash }} />
        <div style={{ position: "absolute", left: 12, top: 12, padding: "4px 10px", borderRadius: 7, background: theme.colors.alert, color: theme.colors.white, fontSize: 12, fontWeight: 600, opacity: frame >= from + 6 ? 1 : 0 }}>
          Registering Keys · view {Math.max(1, n)} of 8
        </div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 372, textAlign: "center", fontSize: 19, fontWeight: 700 }}>Show the keys to the camera</div>
      <div style={{ position: "absolute", left: 40, right: 40, top: 406, textAlign: "center", fontSize: 13.5, color: app.muted, lineHeight: 1.5 }}>
        Hold them about 50 cm from the camera and turn them slowly, so it sees the front, the back and the sides.
      </div>
      <div style={{ position: "absolute", left: 22, right: 22, top: 490, height: 5, borderRadius: 3, background: alpha(app.ink, 0.1) }}>
        <div style={{ width: `${(n / 8) * 100}%`, height: "100%", borderRadius: 3, background: app.teal }} />
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 506, textAlign: "center", fontSize: 13.5, color: app.ink, fontVariantNumeric: "tabular-nums" }}>{n} of 8 views</div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ Keys added */

export const Added: React.FC<{ at: number; thumbs: React.ReactNode[] }> = ({ at, thumbs }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: app.bg }}>
      <div style={{ position: "absolute", left: 24, top: 66, fontSize: 22 }}>✕</div>
      <div style={{ position: "absolute", left: 18, right: 18, top: 110, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
        {thumbs.map((t, i) => {
          const p = spring({ frame: frame - at - i * 3, fps, config: theme.spring.snappy });
          return (
            <div key={i} style={{ height: 82, borderRadius: 12, overflow: "hidden", background: theme.colors.ink, transform: `scale(${0.8 + 0.2 * p})`, opacity: p }}>
              {t}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 226, textAlign: "center", fontSize: 20, fontWeight: 700 }}>Keys added</div>
      <div style={{ position: "absolute", left: 40, right: 40, top: 262, textAlign: "center", fontSize: 13.5, color: app.muted, lineHeight: 1.5 }}>
        ThingTracker learnt them from 8 views. From now on, the camera finds them whenever something moves, and you can ask “Where are my keys?”.
      </div>
      <div style={{ position: "absolute", left: 22, right: 22, top: 372, height: 50, borderRadius: 999, background: app.teal, display: "grid", placeItems: "center", fontSize: 15, fontWeight: 600 }}>Done</div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ the assistant sheet */

export type Msg =
  | { kind: "user"; text: string; typeAt: number; sendAt: number }
  | { kind: "bot"; text: string; at: number; card?: { title: string; status: string; thumb?: React.ReactNode; icon?: IconName } };

/** Text typed into the input between `at` and `at + text.length / cps`. */
const typed = (frame: number, at: number, text: string, cps = 1.4) => text.slice(0, Math.max(0, Math.min(text.length, Math.floor((frame - at) * cps))));

export const Assistant: React.FC<{ msgs: Msg[]; sheetAt?: number; scroll?: number }> = ({ msgs, sheetAt = 0, scroll = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sheet = spring({ frame: frame - sheetAt, fps, config: { damping: 20, stiffness: 120, mass: 0.9 } });
  // the input field shows the message being typed, until it is sent
  const typing = msgs.find((m): m is Extract<Msg, { kind: "user" }> => m.kind === "user" && frame >= m.typeAt && frame < m.sendAt);
  return (
    <AbsoluteFill style={{ background: app.bg }}>
      {/* the Things tab behind, dimmed */}
      <div style={{ position: "absolute", left: 24, top: 70, fontSize: 22, fontWeight: 700 }}>Hack 3</div>
      <div style={{ position: "absolute", left: 24, top: 124, fontSize: 15 }}>Hall (1)</div>
      <div style={{ position: "absolute", left: 22, right: 22, top: 152, height: 70, borderRadius: 20, background: app.card }} />
      <AbsoluteFill style={{ background: alpha(app.ink, 0.45 * sheet) }} />
      {/* the sheet */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 96, bottom: 0, borderRadius: "26px 26px 0 0", background: app.list, transform: `translateY(${(1 - sheet) * 780}px)`, overflow: "hidden" }}>
        <div style={{ position: "absolute", left: "50%", top: 8, width: 36, height: 4, marginLeft: -18, borderRadius: 2, background: alpha(app.ink, 0.8) }} />
        <div style={{ position: "absolute", left: 22, top: 26, fontSize: 18, fontWeight: 700 }}>Assistant</div>
        <div style={{ position: "absolute", right: 24, top: 22, fontSize: 20 }}>✕</div>
        <div style={{ position: "absolute", left: 16, right: 16, top: 66, bottom: 96, overflow: "hidden" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 12, transform: `translateY(${-scroll}px)` }}>
            <div style={{ alignSelf: "flex-start", maxWidth: "78%", padding: "12px 14px", borderRadius: 18, background: app.card, fontSize: 13.5, lineHeight: 1.45 }}>
              Hi! Ask me anything about your home, like where you left something, or describe a sensor in one sentence.
            </div>
            {msgs.map((m, i) => {
              if (m.kind === "user") {
                if (frame < m.sendAt) return null;
                const p = spring({ frame: frame - m.sendAt, fps, config: theme.spring.snappy });
                return (
                  <div key={i} style={{ alignSelf: "flex-end", maxWidth: "80%", padding: "11px 16px", borderRadius: 18, background: app.teal, fontSize: 14.5, transform: `translateY(${20 * (1 - p)}px)`, opacity: p }}>
                    {m.text}
                  </div>
                );
              }
              const prev = msgs[i - 1];
              const thinking = prev && prev.kind === "user" && frame >= prev.sendAt + 4 && frame < m.at;
              if (thinking) {
                return (
                  <div key={i} style={{ alignSelf: "flex-start", padding: "12px 16px", borderRadius: 16, background: app.card, display: "flex", gap: 5 }}>
                    {[0, 1, 2].map((d) => <span key={d} style={{ width: 7, height: 7, borderRadius: 7, background: app.muted, opacity: 0.4 + 0.6 * Math.abs(Math.sin((frame + d * 5) / 6)) }} />)}
                  </div>
                );
              }
              if (frame < m.at) return null;
              const p = spring({ frame: frame - m.at, fps, config: theme.spring.smooth });
              return (
                <div key={i} style={{ alignSelf: "flex-start", maxWidth: "84%", padding: "12px 14px", borderRadius: 18, background: app.card, fontSize: 14.5, lineHeight: 1.45, transform: `translateY(${18 * (1 - p)}px)`, opacity: p }}>
                  {m.text}
                  {m.card ? (
                    <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 12, padding: "10px 12px", borderRadius: 14, background: app.list }}>
                      <div style={{ width: 46, height: 46, borderRadius: 10, overflow: "hidden", background: app.card, display: "grid", placeItems: "center", flex: "none" }}>
                        {m.card.icon ? <LineIcon name={m.card.icon} size={26} color={app.ink} draw={ramp(frame, m.at + 2, m.at + 18, theme.ease.out)} /> : m.card.thumb}
                      </div>
                      <div>
                        <div style={{ fontSize: 14.5, fontWeight: 700 }}>{m.card.title}</div>
                        <div style={{ fontSize: 13, fontWeight: 500, color: app.blue, marginTop: 3, display: "flex", alignItems: "center", gap: 4 }}>
                          {m.card.icon ? <Check size={13} color={app.blue} draw={ramp(frame, m.at + 4, m.at + 14)} stroke={3} /> : null}
                          {m.card.status}
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
        {/* the input */}
        <div style={{ position: "absolute", left: 16, right: 16, bottom: 30, height: 50, display: "flex", gap: 10 }}>
          <div style={{ flex: 1, borderRadius: 14, background: app.card, display: "flex", alignItems: "center", padding: "0 16px", fontSize: 14.5, color: typing ? app.ink : app.muted, whiteSpace: "nowrap", overflow: "hidden" }}>
            {typing ? (
              <>
                {typed(frame, typing.typeAt, typing.text)}
                <span style={{ width: 1.5, height: 18, background: app.ink, marginLeft: 1, opacity: frame % 16 < 9 ? 1 : 0 }} />
              </>
            ) : (
              "Ask anything"
            )}
          </div>
          <div style={{ width: 50, height: 50, borderRadius: 25, background: app.teal, display: "grid", placeItems: "center", fontSize: 22, color: app.ink }}>→</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** How long `text` takes to type at the default speed, in frames. */
export const typeFrames = (text: string, cps = 1.4) => Math.ceil(text.length / cps);
