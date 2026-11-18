"""Track the blank white screen of a hand-held phone in a stock clip, for the screen inserts of video 1.
    python3 video/tools/track_screen.py <clip> <t0> <t1> <seed_x> <seed_y> [thresh]
Writes video/public/stock/screens/<clip>_<t0>-<t1>.json: {fps, frames: [[t, x0,y0, x1,y1, x2,y2, x3,y3], ...]} with the
screen's corners (top-left, top-right, bottom-right, bottom-left) in pixels of the clip, sampled every 1/30 s and smoothed.
The seed is a point inside the screen at t0 (pixels); each frame keeps the bright region nearest the last centre."""
import json, sys
from pathlib import Path
import cv2
import numpy as np

clip, t0, t1, sx, sy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
thresh = int(sys.argv[6]) if len(sys.argv) > 6 else 215
root = Path(__file__).resolve().parents[1] / "public" / "stock"
cap = cv2.VideoCapture(str(root / f"{clip}.mp4"))
fps = cap.get(cv2.CAP_PROP_FPS)
W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


def order(pts):
    pts = np.array(pts, dtype=float)
    c = pts.mean(0)
    ang = np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0])
    pts = pts[np.argsort(ang)]          # clockwise from the left in image coordinates
    i = np.argmin(pts.sum(1))           # top-left first
    return np.roll(pts, -i, axis=0)


out, centre, prev_area = [], np.array([sx, sy]), None
for k in range(int(round((t1 - t0) * 30)) + 1):
    t = t0 + k / 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps)))
    ok, img = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    m = (g > thresh).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, cents = cv2.connectedComponentsWithStats(m)
    best, bd = None, 1e9
    for i in range(1, n):
        a = stats[i, cv2.CC_STAT_AREA]
        if a < 0.002 * W * H:
            continue
        if prev_area and not (0.6 * prev_area < a < 1.6 * prev_area):
            continue
        d = np.hypot(*(cents[i] - centre))
        if d < bd:
            best, bd = i, d
    if best is None:
        out.append(None)
        continue
    cnt, _ = cv2.findContours((lab == best).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = cv2.convexHull(max(cnt, key=cv2.contourArea))
    box = cv2.boxPoints(cv2.minAreaRect(hull))
    q = order(box)
    out.append([round(t, 4)] + [round(float(v), 2) for v in q.reshape(-1)])
    centre, prev_area = cents[best], stats[best, cv2.CC_STAT_AREA]

# fill gaps and smooth each coordinate (a centred moving average over 7 samples, about 0,23 s)
arr = np.array([o[1:] if o else [np.nan] * 8 for o in out])
for j in range(8):
    col = arr[:, j]
    idx = np.arange(len(col))
    good = ~np.isnan(col)
    arr[:, j] = np.interp(idx, idx[good], col[good])
    pad = np.pad(arr[:, j], 3, mode="edge")
    arr[:, j] = np.convolve(pad, np.ones(7) / 7, mode="valid")
res = {"clip": clip, "size": [W, H], "t0": t0, "t1": t1, "missing": int(sum(o is None for o in out)),
       "frames": [[round(t0 + k / 30, 4)] + [round(float(v), 2) for v in arr[k]] for k in range(len(arr))]}
dst = root / "screens" / f"{clip}_{t0:g}-{t1:g}.json"
dst.write_text(json.dumps(res))
print(dst, len(res["frames"]), "frames, missing", res["missing"], "first", res["frames"][0][1:], "last", res["frames"][-1][1:])
