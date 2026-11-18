// Real OWLv2 boxes for a stock clip (public/stock/boxes/<clip>.json: normalised [x1, y1, x2, y2] per sampled frame,
// rank 1 = the best box for a label), interpolated between samples and mapped to the 1920 × 1080 frame (the clip
// fills the frame, object-fit cover). A label missing in one sample keeps its neighbouring box.
import { useVideoConfig } from "remotion";
import { useJson } from "./assets";
import { Rect } from "./ui";
import { SLOTS } from "./stock";

type Det = { label: string; score: number; rank: number; box: [number, number, number, number] };
type BoxFile = { frame_size: [number, number]; frames: { t: number; boxes: Det[] }[] } | null;

const best = (f: { boxes: Det[] }, label: string) => f.boxes.find((b) => b.label === label && b.rank === 1);

/** The clip's boxes at `localFrame` (frames since the clip started in the shot), in frame pixels. */
export const useStockBoxes = (name: string, localFrame: number, minScore = 0.15): { label: string; rect: Rect; score: number }[] => {
  const { fps } = useVideoConfig();
  const slot = SLOTS[name];
  const data = useJson<BoxFile>(slot ? `stock/boxes/${slot.clip}.json` : "stock/boxes/none.json");
  if (!slot || !data?.frames?.length) return [];
  const t = (slot.start ?? 0) + (Math.max(0, localFrame) / fps) * (slot.rate ?? 1);
  const fr = data.frames;
  const [w, h] = data.frame_size;
  const k = Math.max(1920 / w, 1080 / h);
  const ox = (1920 - w * k) / 2;
  const oy = (1080 - h * k) / 2;
  const labels = Array.from(new Set(fr.flatMap((f) => f.boxes.filter((b) => b.rank === 1 && b.score >= minScore).map((b) => b.label))));
  const out: { label: string; rect: Rect; score: number }[] = [];
  for (const label of labels) {
    // the samples on either side of t that have this label
    const before = [...fr].reverse().find((f) => f.t <= t && best(f, label));
    const after = fr.find((f) => f.t >= t && best(f, label));
    const a = before ?? after;
    const b = after ?? before;
    if (!a || !b) continue;
    const da = best(a, label)!;
    const db = best(b, label)!;
    if (Math.max(da.score, db.score) < minScore) continue;
    const u = b.t > a.t ? (t - a.t) / (b.t - a.t) : 0;
    const q = da.box.map((v, j) => v + (db.box[j] - v) * u);
    out.push({ label, score: da.score, rect: { x: ox + q[0] * w * k, y: oy + q[1] * h * k, w: (q[2] - q[0]) * w * k, h: (q[3] - q[1]) * h * k } });
  }
  return out;
};
