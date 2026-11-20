// Phones and the frozen-frame video player used for speed ramps.
import React from "react";
import { Freeze, Img, OffthreadVideo, staticFile } from "remotion";
import { theme } from "../theme";
import { look } from "./look";

const { c, a } = look;

/** A video shown at a given source second (any speed curve: the caller decides the second for each frame). */
export const VideoAt: React.FC<{ src: string; second: number; style?: React.CSSProperties }> = ({ src, second, style }) => (
  <Freeze frame={Math.round(second * theme.fps)}>
    <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%", display: "block", ...style }} />
  </Freeze>
);

/** The team's Android phone: a plain dark body drawn in CSS around a 392 x 850 screen recording. */
export const ANDROID = { screenW: 392, screenH: 850, bezel: 13, radius: 50 } as const;

export const AndroidPhone: React.FC<{ scale: number; children: React.ReactNode }> = ({ scale, children }) => {
  const w = ANDROID.screenW * scale;
  const h = ANDROID.screenH * scale;
  const b = ANDROID.bezel;
  return (
    <div style={{ position: "relative", width: w + 2 * b, height: h + 2 * b, borderRadius: ANDROID.radius, background: look.phoneBody,
      boxShadow: `${look.shadow}, inset 0 0 0 2px ${a(c.white, 0.08)}` }}>
      <div style={{ position: "absolute", left: b, top: b, width: w, height: h, borderRadius: ANDROID.radius - b,
        overflow: "hidden", background: c.ink }}>
        {children}
      </div>
      {/* side buttons */}
      <div style={{ position: "absolute", right: -4, top: 170, width: 4, height: 70, borderRadius: 2, background: a(c.ink, 0.85) }} />
      <div style={{ position: "absolute", right: -4, top: 270, width: 4, height: 110, borderRadius: 2, background: a(c.ink, 0.85) }} />
    </div>
  );
};

/** The iPhone frame (img/iphone-frame.svg, 1350 x 2760) with the app recording (1206 x 2622) behind its screen. */
export const IPHONE = { w: 1350, h: 2760, sx: 72, sy: 69, sw: 1206, sh: 2622, r: 191 } as const;

export const IPhone: React.FC<{ height: number; children: React.ReactNode }> = ({ height, children }) => {
  const k = height / IPHONE.h;
  return (
    <div style={{ position: "relative", width: IPHONE.w * k, height, filter: `drop-shadow(0 40px 50px ${a(c.labsDeep, 0.28)})` }}>
      <div style={{ position: "absolute", left: IPHONE.sx * k, top: IPHONE.sy * k, width: IPHONE.sw * k, height: IPHONE.sh * k,
        borderRadius: IPHONE.r * k, overflow: "hidden", background: c.white }}>
        {children}
      </div>
      <Img src={staticFile("img/iphone-frame.svg")} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
    </div>
  );
};
