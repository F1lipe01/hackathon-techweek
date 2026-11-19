"""Track the green screen of a hand-held phone in a stock clip (no markers), for screen replacement.
    python3 video/tools/track_green.py <clip> <out.json> [--from S] [--to S] [--check out.mp4] [--smooth]
Each frame, read in order:
  1. A hue key finds the screen's green; the largest green area near the last one is the screen.
  2. A straight line is fitted (Huber) to each of the four edges of that area, using only the middle of each edge and
     only boundary points close to where the edge was in the last frame. So the rounded glass corners, a notch and a
     thumb that bites into the screen are ignored. The four lines meet at the screen's "virtual sharp" corners.
  3. The edge with the notch (or Dynamic Island), the one where the green is pushed in at its middle, is the top, so
     the corners come out top-left, top-right, bottom-right, bottom-left of the screen held upright.
  4. A frame that can't be fitted (no green, a jump) is interpolated and flagged; --smooth runs a One Euro filter
     forwards and backwards (no lag).
Output: the same format as track_markers.py:
{"src":{"file","w","h","fps"}, "screen":{"w","h"}, "from":f0, "frames":[[f, ok, resid, x0,y0, x1,y1, x2,y2, x3,y3]]}
with ok 1 = fitted, 0 = interpolated, resid the RMS distance (px) of the edge points from their lines.
Tested on a synthetic plate: python3 video/tools/synth_plate.py <green.png> <bg.jpg> <dir> (see make_markers.py --green)."""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np


def green_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0].astype(np.int16) * 2, hsv[:, :, 1], hsv[:, :, 2]
    m = ((h >= 100) & (h <= 160) & (s > 70) & (v > 90)).astype(np.uint8) * 255  # screen green: bluer than leaves; pale when it catches the light
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))


def component(mask, near=None, min_area=2000):
    n, lab, stats, cents = cv2.connectedComponentsWithStats(mask)
    best, score = None, -1
    for i in range(1, n):
        a = stats[i, cv2.CC_STAT_AREA]
        if a < min_area:
            continue
        sc = a if near is None else a / (1 + np.hypot(*(cents[i] - near)) / 200)
        if sc > score:
            best, score = i, sc
    if best is None:
        return None
    cnts, _ = cv2.findContours((lab == best).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return max(cnts, key=cv2.contourArea).reshape(-1, 2).astype(np.float64)


def clockwise(q):
    c = q.mean(0)
    ang = np.arctan2(q[:, 1] - c[1], q[:, 0] - c[0])
    return q[np.argsort(ang)]  # image coordinates (y down): increasing angle is clockwise on screen


def initial_quad(cnt):
    hull = cv2.convexHull(cnt.astype(np.float32))
    peri = cv2.arcLength(hull, True)
    for eps in np.linspace(0.01, 0.1, 30):
        ap = cv2.approxPolyDP(hull, eps * peri, True).reshape(-1, 2)
        if len(ap) == 4:
            return clockwise(ap.astype(np.float64))
    rect = cv2.boxPoints(cv2.minAreaRect(hull))
    return clockwise(rect.astype(np.float64))


def intersect(l1, l2):
    (vx1, vy1, x1, y1), (vx2, vy2, x2, y2) = l1, l2
    A = np.array([[vx1, -vx2], [vy1, -vy2]])
    t = np.linalg.solve(A, [x2 - x1, y2 - y1])
    return np.array([x1 + vx1 * t[0], y1 + vy1 * t[0]])


def hull_points(cnt, step=2.0):
    """The convex hull of the green area, sampled every `step` px: it bridges straight across a notch or a thumb's bite,
    and those bridges lie on the screen's edges."""
    h = cv2.convexHull(cnt.astype(np.float32)).reshape(-1, 2).astype(np.float64)
    out = []
    for i in range(len(h)):
        a, b = h[i], h[(i + 1) % len(h)]
        n = max(1, int(np.hypot(*(b - a)) / step))
        out.append(a + (b - a) * (np.arange(n)[:, None] / n))
    return np.concatenate(out)


def refine(cnt, q):
    """Fit a line to each edge of the predicted quad q. Two passes on the hull (it bridges the notch and a thumb's bite,
    so a rough start converges), then a last, narrow pass on the true boundary, where only the straight visible parts
    of each edge are close enough to count (a sagging bridge over the notch would bias the top edge)."""
    hull = hull_points(cnt)
    for pts, band, lo in ((hull, 0.10, 0.15), (hull, 0.05, 0.15), (cnt, 0.012, 0.2)):
        q2, resid = fit_edges(pts, q, band, lo)
        if q2 is None:
            return None, -1.0
        q = q2
    return q, resid


def fit_edges(cnt, q, band_frac, lo=0.15):
    lines, res = [], []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        d = b - a
        L = np.hypot(*d)
        u = d / L
        nrm = np.array([-u[1], u[0]])
        rel = cnt - a
        t = rel @ u / L
        dist = np.abs(rel @ nrm)
        band = max(4.0, band_frac * L)
        sel = cnt[(t > lo) & (t < 1 - lo) & (dist < band)]
        if len(sel) < 20:
            return None, -1.0
        line = cv2.fitLine(sel.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        vx, vy, x0, y0 = line
        r = np.abs((sel[:, 0] - x0) * vy - (sel[:, 1] - y0) * vx)
        res.append(np.sqrt(np.mean(r ** 2)))
        lines.append(line)
    corners = np.array([intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)])
    return corners, float(np.sqrt(np.mean(np.square(res))))


def notch_edge(mask, q):
    """The short edge whose middle has the least green just inside it: the notch or the Dynamic Island."""
    lens = [np.hypot(*(q[(i + 1) % 4] - q[i])) for i in range(4)]
    short = sorted(range(4), key=lambda i: lens[i])[:2]
    c = q.mean(0)
    best, cover = None, 2.0
    for i in short:
        a, b = q[i], q[(i + 1) % 4]
        mid = (a + b) / 2
        inward = (c - mid) / np.hypot(*(c - mid))
        pts = [mid + (b - a) * s + inward * lens[(i + 1) % 4] * k for s in np.linspace(-0.12, 0.12, 9) for k in (0.015, 0.025)]
        vals = [mask[int(p[1]), int(p[0])] > 0 for p in pts if 0 <= int(p[1]) < mask.shape[0] and 0 <= int(p[0]) < mask.shape[1]]
        cov = np.mean(vals) if vals else 1.0
        if cov < cover:
            best, cover = i, cov
    return best


def one_euro(x, fps, mincutoff=2.0, beta=0.01, dcutoff=1.0):
    def alpha(cut):
        tau = 1.0 / (2 * np.pi * cut)
        return 1.0 / (1.0 + tau * fps)
    y = np.empty_like(x)
    y[0], dx_prev = x[0], 0.0
    for i in range(1, len(x)):
        dx = (x[i] - x[i - 1]) * fps
        dx_prev = dx_prev + alpha(dcutoff) * (dx - dx_prev)
        y[i] = y[i - 1] + alpha(mincutoff + beta * abs(dx_prev)) * (x[i] - y[i - 1])
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("out")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--check", default=None)
    ap.add_argument("--smooth", action="store_true")
    ap.add_argument("--screen", default="1206x2622", help="the inserted screen's size, written to the JSON")
    a = ap.parse_args()

    cap = cv2.VideoCapture(a.clip)
    fps = cap.get(cv2.CAP_PROP_FPS)
    sw, sh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    f0 = int(round(a.t0 * fps))
    f1 = int(round(a.t1 * fps)) if a.t1 is not None else None
    writer = None
    if a.check:
        writer = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{sw // 2}x{sh // 2}",
                                   "-r", f"{fps}", "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", a.check], stdin=subprocess.PIPE)
    rows, q, q_prev, last_good, misses = [], None, None, None, 0
    f = -1
    while True:
        ok_read, frame = cap.read()
        if not ok_read:
            break
        f += 1
        if f < f0:
            continue
        if f1 is not None and f > f1:
            break
        mask = green_mask(frame)
        if misses >= 2 and q is not None:
            last_good, q, q_prev = q, None, None  # re-acquire from the whole frame
        pred = None
        if q is not None:  # only near where the screen should be now, so green things nearby can't merge with it
            pred = q + (q - q_prev) if q_prev is not None else q
            c = pred.mean(0)
            roi = np.zeros_like(mask)
            cv2.fillConvexPoly(roi, np.round(c + (pred - c) * 1.3).astype(np.int32), 255)
            mask = cv2.bitwise_and(mask, roi)
        cnt = component(mask, None if pred is None else pred.mean(0))
        fitted, resid = None, -1.0
        if cnt is not None:
            start = pred if pred is not None else initial_quad(cnt)
            fitted, resid = refine(cnt, start)
            if fitted is not None and pred is not None and np.max(np.linalg.norm(fitted - pred, axis=1)) > 0.15 * np.hypot(*(q[2] - q[0])):
                fitted = None  # a jump: don't trust it
            if fitted is None and q is None:
                fitted, resid = initial_quad(cnt), -1.0
        if fitted is not None:
            if q is None:
                fitted = clockwise(fitted)
                if last_good is not None:  # keep the same corner order as before the loss
                    k = min(range(4), key=lambda r: np.linalg.norm(np.roll(fitted, -r, axis=0) - last_good))
                else:
                    k = notch_edge(mask, fitted) or 0  # the notch edge becomes top-left -> top-right
                fitted = np.roll(fitted, -k, axis=0)
            q_prev, q = q, fitted
            misses = 0
            rows.append([f, 1, round(resid, 3)] + [round(float(v), 3) for v in q.reshape(-1)])
        else:
            rows.append([f, 0, -1.0] + [np.nan] * 8)
            q_prev = None
            misses += 1
        if writer:
            out = frame.copy()
            if fitted is not None:
                cv2.polylines(out, [q.astype(np.int32)], True, (0, 255, 255), 3)
                cv2.circle(out, tuple(q[0].astype(int)), 14, (0, 0, 255), -1)  # top-left of the upright screen
            cv2.putText(out, f"f{f} resid{resid:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3)
            writer.stdin.write(cv2.resize(out, (sw // 2, sh // 2), interpolation=cv2.INTER_AREA).tobytes())
    if writer:
        writer.stdin.close()
        writer.wait()

    arr = np.array([r[3:] for r in rows], np.float64)
    good = ~np.isnan(arr[:, 0])
    if not good.any():
        raise SystemExit("no frame tracked")
    idx = np.arange(len(arr))
    for j in range(8):
        arr[:, j] = np.interp(idx, idx[good], arr[good, j])
    if a.smooth:
        for j in range(8):
            arr[:, j] = (one_euro(arr[:, j], fps) + one_euro(arr[::-1, j], fps)[::-1]) / 2
    w, h = (int(v) for v in a.screen.split("x"))
    res = {"src": {"file": Path(a.clip).name, "w": sw, "h": sh, "fps": fps}, "screen": {"w": w, "h": h}, "from": f0,
           "smoothed": a.smooth, "frames": [[r[0], r[1], r[2]] + [round(float(v), 3) for v in arr[i]] for i, r in enumerate(rows)]}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res))
    rs = [r[2] for r in rows if r[1] == 1 and r[2] >= 0]
    print(f"{a.out}: {len(rows)} frames · fitted {int(good.sum())} · gaps {int((~good).sum())} · edge resid median {np.median(rs) if rs else float('nan'):.2f} px")


if __name__ == "__main__":
    main()
