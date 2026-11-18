// Geometry for screen inserts and hand-placed boxes: cover-fit of a clip into the 1920 × 1080 frame, the projective map
// of a rectangle onto a tracked quad (as a CSS matrix3d), and 2D camera transforms.
export type Pt = { x: number; y: number };
export type Quad = [Pt, Pt, Pt, Pt]; // top-left, top-right, bottom-right, bottom-left

/** Where a clip of w × h source pixels sits in the 1920 × 1080 frame with object-fit: cover. */
export const coverFit = (w: number, h: number) => {
  const k = Math.max(1920 / w, 1080 / h);
  return { k, ox: (1920 - w * k) / 2, oy: (1080 - h * k) / 2 };
};

/** The 3 × 3 projective matrix (row-major, h33 = 1) that maps the unit square's corners to q. */
const squareToQuad = (q: Quad): number[] => {
  const [p0, p1, p2, p3] = q;
  const dx1 = p1.x - p2.x, dx2 = p3.x - p2.x, dx3 = p0.x - p1.x + p2.x - p3.x;
  const dy1 = p1.y - p2.y, dy2 = p3.y - p2.y, dy3 = p0.y - p1.y + p2.y - p3.y;
  let g = 0, h = 0;
  if (Math.abs(dx3) > 1e-9 || Math.abs(dy3) > 1e-9) {
    const den = dx1 * dy2 - dx2 * dy1;
    g = (dx3 * dy2 - dx2 * dy3) / den;
    h = (dx1 * dy3 - dx3 * dy1) / den;
  }
  const a = p1.x - p0.x + g * p1.x, b = p3.x - p0.x + h * p3.x, c = p0.x;
  const d = p1.y - p0.y + g * p1.y, e = p3.y - p0.y + h * p3.y, f = p0.y;
  return [a, b, c, d, e, f, g, h, 1];
};

/** A projective map from the rectangle 0..w × 0..h onto q. */
export const homography = (w: number, h: number, q: Quad) => {
  const m = squareToQuad(q);
  const H = [m[0] / w, m[1] / h, m[2], m[3] / w, m[4] / h, m[5], m[6] / w, m[7] / h, m[8]];
  const apply = (x: number, y: number): Pt => {
    const z = H[6] * x + H[7] * y + H[8];
    return { x: (H[0] * x + H[1] * y + H[2]) / z, y: (H[3] * x + H[4] * y + H[5]) / z };
  };
  // CSS matrix3d is column-major 4 × 4: x' = (a x + b y + c) / (g x + h y + 1)
  const css = `matrix3d(${H[0]},${H[3]},0,${H[6]},${H[1]},${H[4]},0,${H[7]},0,0,1,0,${H[2]},${H[5]},0,${H[8]})`;
  return { apply, css };
};

/** A 2D camera: p' = T + R(rot) · s · (p − F). Returns the CSS matrix() and the point map. */
export const camera = (F: Pt, T: Pt, s: number, rot: number) => {
  const c = Math.cos(rot) * s, n = Math.sin(rot) * s;
  const e = T.x - (c * F.x - n * F.y);
  const f = T.y - (n * F.x + c * F.y);
  return {
    css: `matrix(${c},${n},${-n},${c},${e},${f})`,
    map: (p: Pt): Pt => ({ x: c * p.x - n * p.y + e, y: n * p.x + c * p.y + f }),
  };
};

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const lerpPt = (a: Pt, b: Pt, t: number): Pt => ({ x: lerp(a.x, b.x, t), y: lerp(a.y, b.y, t) });
