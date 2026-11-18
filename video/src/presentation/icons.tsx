// Clean line icons for the app screens and cards (no wand, no stars, no colour emoji). Each draws on with `draw`
// (0 → 1), so an icon can arrive as a stroke.
import React from "react";

export type IconName = "key" | "wallet" | "glasses" | "bell" | "door" | "paw" | "clock";

const PATHS: Record<IconName, string[]> = {
  key: ["M14.5 9.5a4.5 4.5 0 1 1-1.3-3.2 4.5 4.5 0 0 1 1.3 3.2Z", "M13.2 12.7 21 20.5", "M17.5 17l2-2", "M19.5 19l1.5-1.5"],
  wallet: ["M3.5 7.5h15a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2Z", "M3.5 7.5V6a2 2 0 0 1 2-2h10.5v3.5", "M16 13.5h4.5"],
  glasses: ["M3 12.5a3.5 3.5 0 1 0 7 0 3.5 3.5 0 1 0-7 0Z", "M14 12.5a3.5 3.5 0 1 0 7 0 3.5 3.5 0 1 0-7 0Z", "M10 12c1.2-.8 2.8-.8 4 0", "M3 12 4.5 6.5h2", "M21 12l-1.5-5.5h-2"],
  bell: ["M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15Z", "M10 20.5a2 2 0 0 0 4 0"],
  door: ["M6 20.5V4.5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v16", "M4 20.5h16", "M14.5 12.5v.01"],
  paw: ["M8 9.5a1.6 2 0 1 0 0 .01", "M16 9.5a1.6 2 0 1 0 0 .01", "M5 13.5a1.4 1.7 0 1 0 0 .01", "M19 13.5a1.4 1.7 0 1 0 0 .01", "M12 13c-3 0-5 3.5-4 5.5 1 1.8 3 .8 4 .8s3 1 4-.8c1-2-1-5.5-4-5.5Z"],
  clock: ["M12 3.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Z", "M12 7.5V12l3 2"],
};

export const LineIcon: React.FC<{ name: IconName; size: number; color: string; draw?: number; stroke?: number }> = ({ name, size, color, draw = 1, stroke = 1.8 }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} style={{ overflow: "visible", flex: "none" }}>
    {PATHS[name].map((d, i) => (
      <path key={i} d={d} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
    ))}
  </svg>
);
