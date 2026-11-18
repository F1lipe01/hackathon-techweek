// The real recognition numbers, read at render time from public/real/recognition.json (computed by
// video/tools/recognise.py with prototype/edge.py's OWLv2 + DINOv2). The fallback is only used if the file is missing,
// and repeats the values the file held on 18 Nov 2026.
import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

export type Box = [number, number, number, number];
export type Recognition = {
  photos_taken_s: number[];
  views: { file: string; t: number; owl_score: number; box_phone_px: Box }[];
  kit: {
    frame_s: number; size: [number, number]; book_box: Box; owl_score: number; score: number; threshold: number;
    recognised: boolean; per_view: number[];
  };
  controls: { label: string; box?: Box; owl_score: number; score: number }[];
};

const FALLBACK: Recognition = {
  photos_taken_s: [1.3, 7.83, 11.17, 16.2, 23.03, 27.27, 31.8, 36.1],
  views: [
    { file: "real/views/view-1.jpg", t: 1.3, owl_score: 0.366, box_phone_px: [95.9, 229.6, 325.2, 542.1] },
    { file: "real/views/view-2.jpg", t: 7.83, owl_score: 0.091, box_phone_px: [47.1, 178.3, 325.4, 561.4] },
    { file: "real/views/view-3.jpg", t: 11.17, owl_score: 0.164, box_phone_px: [34.6, 124.6, 357.7, 575.0] },
    { file: "real/views/view-4.jpg", t: 16.2, owl_score: 0.493, box_phone_px: [119.6, 125.8, 204.5, 583.7] },
    { file: "real/views/view-5.jpg", t: 23.03, owl_score: 0.394, box_phone_px: [-1.8, 228.5, 390.3, 442.0] },
    { file: "real/views/view-6.jpg", t: 27.27, owl_score: 0.459, box_phone_px: [1.7, 220.4, 372.4, 403.2] },
    { file: "real/views/view-7.jpg", t: 31.8, owl_score: 0.469, box_phone_px: [30.2, 248.2, 292.1, 486.7] },
    { file: "real/views/view-8.jpg", t: 36.1, owl_score: 0.484, box_phone_px: [39.5, 226.7, 291.4, 449.3] },
  ],
  kit: {
    frame_s: 10.0, size: [1920, 1080], book_box: [1208.0, 364.0, 1376.3, 486.4], owl_score: 0.234, score: 0.698,
    threshold: 0.62, recognised: true, per_view: [0.474, 0.339, 0.288, 0.386, 0.582, 0.565, 0.632, 0.698],
  },
  controls: [
    { label: "garrafa", box: [1074.5, 241.4, 1165.2, 473.8], owl_score: 0.23, score: 0.333 },
    { label: "teclado", box: [33.5, 323.7, 189.4, 412.2], owl_score: 0.576, score: 0.119 },
  ],
};

let cache: Recognition | null = null;
let pending: Promise<Recognition> | null = null;

export const useRecognition = (): Recognition => {
  const [data, setData] = useState<Recognition>(cache ?? FALLBACK);
  const [handle] = useState(() => (cache ? null : delayRender("Reading real/recognition.json")));
  useEffect(() => {
    if (handle === null) return;
    pending ??= fetch(staticFile("real/recognition.json"))
      .then((r) => (r.ok ? r.json() : FALLBACK))
      .catch(() => FALLBACK);
    pending.then((d: Recognition) => {
      cache = d;
      setData(d);
      continueRender(handle);
    });
  }, [handle]);
  return data;
};

/** 0.698 → "0,70" (PT-PT decimal comma). */
export const pt = (x: number, digits = 2) => x.toFixed(digits).replace(".", ",");
