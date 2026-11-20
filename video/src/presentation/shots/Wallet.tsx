// Act 4: the wallet, from the photos to the alert (s09–s13). The app is always the real prototype, recorded
// (public/app/*.mp4) and placed into the filmed phone's screen, then pushed in until it can be read (2 px per pt keeps the
// app's 13 pt text at 26 px). Fallbacks for takes not yet filmed are tagged "a filmar".
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../../theme";
import { AppView, Chip, Clip, ScreenInsert, SoftGround, ToFilm, type CamKey } from "../media";
import { Brackets, clamp, ramp } from "../ui";
import { Title } from "../type";
import { lerp, type Pt } from "../geom";
import { alpha } from "../tokens";

const STILL = "stock/stills/wallet-hall-table.jpg";
/** A title on the left column, beside the phone. */
const Side: React.FC<{ text: string; at: number; exitAt?: number; entrance?: "blur" | "rise" | "wipe" | "track"; y?: number }> = ({ text, at, exitAt, entrance = "rise", y = 500 }) => (
  <div style={{ position: "absolute", left: 110, top: y }}>
    <Title text={text} size={54} max={720} at={at} exitAt={exitAt} entrance={entrance} />
  </div>
);

/* ------------------------------------------------------------------ s09: three photos, then "Wallet added" */

// the phone's camera preview while the wallet is photographed: the still, framed three ways (the same framings as the
// three photos the app shows: front, at an angle, closer)
const FRAMINGS = [
  { w: 240, rot: 0, c: [605, 330] }, // view1.jpg: 120 px square around the wallet
  { w: 260, rot: 6, c: [605, 337] }, // view2.jpg: 150 px, turned 6°
  { w: 200, rot: -5, c: [605, 331] }, // view3.jpg: 98 px, turned −5°
];
const VIEWS = ["view1", "view2", "view3"];
const CROP = [120 / 240, 150 / 260, 98 / 200]; // each photo's square, as a share of the preview's width
const SHUTTER = [60, 90, 120]; // shot frames (22, 23, 24 s)
const SLOTS = [{ x: 1250, y: 170 }, { x: 1250, y: 425 }, { x: 1250, y: 680 }];
const SLOT = 230;
const GRID = [[21, 122], [112, 122], [203, 122]]; // the three photos in the app's "Wallet added" (pt, 85 pt squares)

const Preview: React.FC<{ i: number; drift: number }> = ({ i, drift }) => {
  const f = FRAMINGS[i];
  const k = (1206 / f.w) * (1 + 0.04 * drift); // screen px per still px
  return (
    <div style={{ position: "absolute", left: 603, top: 1311, width: 0, height: 0, transform: `rotate(${f.rot}deg)` }}>
      <Img src={staticFile(STILL)} style={{ position: "absolute", left: -f.c[0] * k, top: -f.c[1] * k, width: 900 * k, height: 580 * k, maxWidth: "none", filter: "brightness(1.04)" }} />
    </div>
  );
};

export const S09: React.FC = () => {
  const frame = useCurrentFrame();
  const shot = frame < SHUTTER[1] - 8 ? 0 : frame < SHUTTER[2] - 8 ? 1 : 2;
  const drift = ramp(frame, shot === 0 ? 0 : SHUTTER[shot - 1] - 8, SHUTTER[shot] + 10, theme.ease.inOut);
  const APP_AT = 135; // 24,5 s: the app's result
  const keys: CamKey[] = [
    { at: 0, ppt: 0.95, fx: 201, fy: 437, cx: 880, cy: 540 },
    { at: 140, ppt: 0.95, fx: 201, fy: 437, cx: 880, cy: 540 },
    { at: 168, ppt: 2.0, fx: 155, fy: 245, cx: 1250, cy: 520 },
  ];
  return (
    <AbsoluteFill>
      <ScreenInsert clip="phone-alert-2" from={1.0} play={150} track="phone-alert-2_1-6" rec="register" segs={[[APP_AT, 9.05]]} keys={keys}
        screen={frame < APP_AT ? <Preview i={shot} drift={drift} /> : undefined}>
        {(map) => (
          <>
            {SHUTTER.map((s, i) => {
              if (frame < s) return null;
              // the photo leaves the screen (its square in the middle of the preview) and lands in its slot...
              const c = map(201, 437);
              const sw = Math.hypot(map(402, 437).x - map(0, 437).x, map(402, 437).y - map(0, 437).y) * CROP[i];
              const p = ramp(frame, s, s + 12, theme.ease.out);
              let x = lerp(c.x - sw / 2, SLOTS[i].x, p), y = lerp(c.y - sw / 2, SLOTS[i].y, p), w = lerp(sw, SLOT, p);
              let r = 18;
              // ...then flies into the app's grid as the camera pushes in
              const q = ramp(frame, 140, 168, theme.ease.inOut);
              if (q > 0) {
                const a = map(GRID[i][0], GRID[i][1]), b = map(GRID[i][0] + 85, GRID[i][1] + 85);
                x = lerp(SLOTS[i].x, a.x, q); y = lerp(SLOTS[i].y, a.y, q); w = lerp(SLOT, b.x - a.x, q); r = lerp(18, 8 * 2, q);
              }
              const o = 1 - ramp(frame, 170, 176, theme.ease.out);
              return (
                <div key={i} style={{ position: "absolute", left: x, top: y, width: w, height: w, borderRadius: r, overflow: "hidden", opacity: o, boxShadow: `0 18px 40px -18px ${alpha(theme.colors.ink, 0.5)}` }}>
                  <Img src={staticFile(`app-stills/${VIEWS[i]}.jpg`)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                </div>
              );
            })}
          </>
        )}
      </ScreenInsert>
      <Side text="Três fotografias." at={18} exitAt={126} y={170} />
      <Side text="A casa fica a conhecê-la." at={172} entrance="blur" y={170} />
      <ToFilm />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ s10: "Where is my wallet?" */

// the answer card's photo in the recording (pt), at the moment it grows into the hall table
const CARD_PHOTO = { x: 51, y: 689, w: 40, h: 40 };
// the photo the card shows: the region 505..705 × 260..400 of the still, cover-fitted in its square
const SEEN = { cx: 605, cy: 330, h: 140 };
const HALL = { cx: 1200, cy: 560, k: (1920 / 900) * 1.25 }; // the hall table later in the day: framing and scale

export const S10: React.FC = () => {
  const frame = useCurrentFrame();
  const keys: CamKey[] = [
    { at: 0, ppt: 0, fx: 201, fy: 655 },
    { at: 24, ppt: 0, fx: 201, fy: 655 },
    { at: 50, ppt: 2.0, fx: 201, fy: 655, cx: 1250, cy: 520 },
  ];
  const G0 = 150, G1 = 172; // the photo grows into the scene (5,0–5,73 s)
  const u = ramp(frame, G0, G1, theme.ease.inOut);
  const warm = ramp(frame, G1, G1 + 24, theme.ease.inOut);
  const settle = interpolate(frame, [G1, 240], [1, 1.035], clamp);
  return (
    <AbsoluteFill>
      <ScreenInsert clip="phone-alert-1" from={1.0} play={150} track="phone-alert-1_0-6" rec="ask" segs={[[0, 5.67]]} keys={keys} multiply>
        {(map) => {
          if (frame < G0) return null;
          // the card's photo (on screen now) → the whole hall table
          const a = map(CARD_PHOTO.x, CARD_PHOTO.y), b = map(CARD_PHOTO.x + CARD_PHOTO.w, CARD_PHOTO.y + CARD_PHOTO.h);
          const r0 = { x: a.x, y: a.y, w: b.x - a.x, h: b.y - a.y };
          const rect = { x: lerp(r0.x, 0, u), y: lerp(r0.y, 0, u), w: lerp(r0.w, 1920, u), h: lerp(r0.h, 1080, u) };
          const k0 = r0.h / SEEN.h; // px per still px inside the thumbnail
          const k = Math.exp(lerp(Math.log(k0), Math.log(HALL.k), u)) * settle;
          const c: Pt = { x: lerp(r0.x + r0.w / 2, HALL.cx, u), y: lerp(r0.y + r0.h / 2, HALL.cy, u) };
          return (
            <div style={{ position: "absolute", left: rect.x, top: rect.y, width: rect.w, height: rect.h, borderRadius: lerp(18, 0, u), overflow: "hidden", background: theme.colors.bg }}>
              <Img src={staticFile(STILL)} style={{
                position: "absolute", left: c.x - rect.x - SEEN.cx * k, top: c.y - rect.y - SEEN.cy * k, width: 900 * k, height: 580 * k, maxWidth: "none",
                filter: `brightness(${1.04 - 0.04 * warm}) saturate(${1 + 0.12 * warm}) sepia(${0.16 * warm})`,
              }} />
            </div>
          );
        }}
      </ScreenInsert>
      <Side text="Basta perguntar." at={66} exitAt={146} />
      <ToFilm />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ s11: a sentence becomes a sensor */

export const S11: React.FC = () => (
  <AbsoluteFill>
    <AppView rec="ask" segs={[[0, 13.4], [60, 17.0]]} keys={[{ at: 0, ppt: 2.0, fx: 201, fy: 600, cx: 1250, cy: 540 }]} ground={<SoftGround still={STILL} />} />
    <Side text="Uma frase torna-se um sensor." at={8} entrance="wipe" />
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ s12: leaving without it */

// the wallet left on the hall table, as the camera's close-up crop (from the still), with its box
const Inset: React.FC = () => {
  const frame = useCurrentFrame();
  const p = ramp(frame, 12, 26, theme.ease.out);
  const W = 560, H = 340;
  const k = 3.1; // inset px per still px, centred on the wallet
  const wx = W / 2 - 605 * k, wy = H / 2 - 331 * k;
  const box = { x: wx + 551 * k, y: wy + 303 * k, w: 108 * k, h: 56 * k };
  return (
    <div style={{ position: "absolute", right: 56, bottom: 64, width: W, height: H, borderRadius: 18, overflow: "hidden", border: `4px solid ${theme.colors.white}`,
      boxShadow: `0 30px 60px -24px ${alpha(theme.colors.ink, 0.5)}`, opacity: p, transform: `translateX(${(1 - p) * 60}px)` }}>
      <Img src={staticFile(STILL)} style={{ position: "absolute", left: wx, top: wy, width: 900 * k, height: 580 * k, maxWidth: "none" }} />
      <div style={{ position: "absolute", left: box.x, top: box.y, width: box.w, height: box.h, border: `2px solid ${alpha(theme.colors.labs, 0.5)}`, borderRadius: 8 }} />
      <Brackets x={box.x} y={box.y} w={box.w} h={box.h} arm={box.h * 0.32} stroke={5} radius={8} color={theme.colors.labs} />
      <div style={{ position: "absolute", left: box.x, top: box.y - 42, padding: "4px 11px", borderRadius: 8, background: theme.colors.labs, color: theme.colors.white, fontFamily: theme.fonts.display, fontSize: 24, fontWeight: 600 }}>carteira</div>
    </div>
  );
};

export const S12: React.FC = () => {
  const frame = useCurrentFrame();
  // "porta aberta" beside the door while it is open (until it shuts, about 2,6 s in); it follows the camera's drift
  const x = interpolate(frame, [0, 60, 78], [1030, 1045, 1060], clamp);
  return (
    <AbsoluteFill>
      <Clip clip="leaving-home-1" from={8.0} push={[1, 1]} />
      {frame < 76 ? <Chip at={6} text="porta aberta" x={x} y={150} /> : null}
      <Inset />
      <ToFilm />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ s13: the alert, outside */

export const S13: React.FC = () => {
  const keys: CamKey[] = [
    { at: 0, ppt: 0.82, fx: 201, fy: 437, cx: 960, cy: 540 },
    { at: 18, ppt: 0.82, fx: 201, fy: 437, cx: 960, cy: 540 },
    { at: 42, ppt: 2.1, fx: 201, fy: 100, cx: 960, cy: 360 },
  ];
  return (
    <AbsoluteFill>
      <ScreenInsert clip="phone-alert-2" from={6.0} track="phone-alert-2_6-12" rec="alert" segs={[[0, 4.0]]} freezeRec={144} keys={keys} />
      <ToFilm />
    </AbsoluteFill>
  );
};
