"""Track the screen of a hand-held phone showing a marker screen (video/shoot/markers), for screen replacement.
    python3 video/tools/track_markers.py <take> <reference.png> <out.json> [--from S] [--to S] [--check out.mp4] [--smooth]
<reference.png> is a screenshot taken on the phone while it shows the marker screen (best: it gives the markers' exact
place on that screen), or the marker PNG itself.

Each frame, read in order (never by seeking):
  1. ArUco finds the markers (sub-pixel corners) on the green channel, which carries them in both variants; a RANSAC
     homography maps the reference screen onto the frame. On its own this is biased by motion blur (several px).
  2. ECC (an intensity-based planar fit, as planar trackers do) refines the homography on the marker tiles, ignoring
     skin (a thumb) through a mask. It starts from the previous frames' motion and, when they disagree, from the
     markers' homography, and keeps the start that fits best, so a blurred frame with one marker doesn't throw it off.
     In fast moves the template gets the same motion streak as the frame (--shutter: exposure / frame time).
  3. The screen's corners (0,0) (W,0) (W,H) (0,H) go through it: the "virtual sharp" corners of a rounded screen.
  4. Frames that can't be fitted are interpolated and flagged.
  5. --smooth: a One Euro filter run forwards and backwards and averaged (no lag). Off by default: smooth only if the
     check video shows jitter, because real hand motion must stay.
Output: {"src":{"file","w","h","fps"}, "screen":{"w","h"}, "from":S, "frames":[[f, ok, score, x0,y0, x1,y1, x2,y2, x3,y3]]}
with f the source frame number; ok 1 = markers seen and refined, 3 = no marker, refined from the previous motion,
2 = markers only (refinement failed; kept only when 3+ markers agree within 1,5 px), 0 = interpolated; score the ECC correlation (0-1, -1 when not refined); corners
top-left, top-right, bottom-right, bottom-left in source pixels.
--check writes a half-size video: the reference warped onto the frame in difference mode inside the screen (dark and
still where the track is right), the screen outline (yellow: refined, red: not) and ok/score.
Tested on a synthetic plate (video/tools/synth_plate.py): see its docstring."""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
ECC_PARAMS = cv2.ECCParameters()  # a 3-level pyramid widens the capture range for fast moves
ECC_PARAMS.motionType = cv2.MOTION_HOMOGRAPHY
ECC_PARAMS.nlevels = 3
ECC_PARAMS.criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 80, 1e-5)
ECC_PARAMS.gaussFiltSize = 5
MIN_SCORE = 0.6  # below this ECC correlation a fit is not trusted


def detector():
    p = cv2.aruco.DetectorParameters()
    p.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    p.cornerRefinementWinSize = 9
    p.cornerRefinementMaxIterations = 60
    p.cornerRefinementMinAccuracy = 0.01
    p.adaptiveThreshWinSizeMax = 63
    return cv2.aruco.ArucoDetector(DICT, p)


def detect(det, bgr):
    found, ids, _ = det.detectMarkers(bgr[:, :, 1])
    if ids is None:
        return {}
    return {int(i): c.reshape(4, 2).astype(np.float64) for i, c in zip(ids.ravel(), found)}


def reference(path: Path):
    img = cv2.imread(str(path))
    if img is None:
        raise SystemExit(f"cannot read {path}")
    h, w = img.shape[:2]
    ref = detect(detector(), img)
    if len(ref) < 4:
        raise SystemExit(f"only {len(ref)} markers found in the reference {path}")
    return img, w, h, ref


def tile_mask(w, h, ref):
    """The marker tiles plus one module around them: the only part of the screen with texture to fit."""
    m = np.zeros((h, w), np.uint8)
    for c in ref.values():
        x0, y0 = c.min(0)
        x1, y1 = c.max(0)
        pad = (x1 - x0) / 6 * 2
        m[max(0, int(y0 - pad)):int(y1 + pad), max(0, int(x0 - pad)):int(x1 + pad)] = 255
    return m


class Refiner:
    def __init__(self, ref_img, ref):
        self.H, self.W = ref_img.shape[:2]
        self.gray = ref_img[:, :, 1]
        self.mask = tile_mask(self.W, self.H, ref)
        b, g, r = (int(v) for v in np.median(ref_img.reshape(-1, 3), axis=0))
        self.green = g > r + 30  # the dark-green variant: keep only green pixels; else drop skin-like pixels
        self.corners = np.array([[0, 0], [self.W, 0], [self.W, self.H], [0, self.H]], np.float64)
        self.cache = {}

    def template(self, s):
        k = round(s, 2)
        if k not in self.cache:
            T = cv2.resize(self.gray, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            M = cv2.resize(self.mask, (T.shape[1], T.shape[0]), interpolation=cv2.INTER_NEAREST)
            self.cache[k] = (T, M, k)
        return self.cache[k]

    def input_mask(self, crop_bgr):
        hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        if self.green:
            m = (h >= 35) & (h <= 95) & (s > 60)
        else:
            m = ~(((h <= 25) | (h >= 165)) & (s > 40) & (v > 60))
        return cv2.dilate(m.astype(np.uint8) * 255, np.ones((5, 5), np.uint8))

    def refine(self, frame, Hm, blur=(0.0, 0.0)):
        """ECC from the homography Hm (reference screen px -> frame px). `blur` is the screen's motion during the
        exposure (frame px); the template gets the same streak so a smeared frame still fits. Returns (H, score)."""
        fh, fw = frame.shape[:2]
        q = cv2.perspectiveTransform(self.corners.reshape(-1, 1, 2), Hm).reshape(-1, 2)
        if not np.all(np.isfinite(q)):
            return None, -1.0
        x0, y0 = np.floor(q.min(0) - 60).astype(int)
        x1, y1 = np.ceil(q.max(0) + 60).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, fw), min(y1, fh)
        if x1 - x0 < 40 or y1 - y0 < 40:
            return None, -1.0
        crop = frame[y0:y1, x0:x1]
        s = float(np.clip(np.linalg.norm(q[1] - q[0]) / self.W, 0.2, 1.0))
        T, TM, s = self.template(s)
        S = np.diag([s, s, 1.0])
        Tc = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1.0]])
        Hc = Tc @ Hm @ np.linalg.inv(S)
        Hc /= Hc[2, 2]
        if np.hypot(*blur) > 3:
            T = streak(T, Hc, np.array(blur))
        try:
            score, Hc2 = cv2.findTransformECCMultiScale(T, crop[:, :, 1], Hc.astype(np.float32), ECC_PARAMS, TM,
                                                        self.input_mask(crop))
        except cv2.error:
            return None, -1.0
        Hn = np.linalg.inv(Tc) @ Hc2.astype(np.float64) @ S
        return Hn / Hn[2, 2], float(score)

    def from_corners(self, q):
        return cv2.getPerspectiveTransform(self.corners.astype(np.float32), q.astype(np.float32)).astype(np.float64)


def streak(T, Hc, v_img):
    """Blur the template T with a line along the motion v_img (frame px), mapped into template px through the local
    Jacobian of Hc (template -> crop) at the template's centre."""
    c = np.array([T.shape[1] / 2, T.shape[0] / 2])
    def m(p):
        x = Hc @ np.array([p[0], p[1], 1.0])
        return x[:2] / x[2]
    J = np.column_stack([m(c + [1, 0]) - m(c), m(c + [0, 1]) - m(c)])
    v = np.linalg.solve(J, v_img)
    n = int(np.ceil(np.hypot(*v))) | 1
    k = np.zeros((n, n), np.float32)
    a, b = (n // 2) - v / 2, (n // 2) + v / 2
    cv2.line(k, tuple(np.round(a * 16).astype(int)), tuple(np.round(b * 16).astype(int)), 1.0, 1, cv2.LINE_AA, shift=4)
    if k.sum() == 0:
        return T
    return cv2.filter2D(T, -1, k / k.sum(), borderType=cv2.BORDER_REPLICATE)


def one_euro(x, fps, mincutoff=2.0, beta=0.01, dcutoff=1.0):
    """Casiez's One Euro filter over a 1-D series."""
    def alpha(cut):
        tau = 1.0 / (2 * np.pi * cut)
        return 1.0 / (1.0 + tau * fps)
    y = np.empty_like(x)
    y[0], dx_prev = x[0], 0.0
    for i in range(1, len(x)):
        dx = (x[i] - x[i - 1]) * fps
        dx_prev = dx_prev + alpha(dcutoff) * (dx - dx_prev)
        a = alpha(mincutoff + beta * abs(dx_prev))
        y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("take")
    ap.add_argument("ref")
    ap.add_argument("out")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--check", default=None)
    ap.add_argument("--smooth", action="store_true")
    ap.add_argument("--shutter", type=float, default=0.6, help="exposure as a share of the frame (1/50 s at 30 fps = 0.6)")
    a = ap.parse_args()

    ref_img, W, H, ref = reference(Path(a.ref))
    rf = Refiner(ref_img, ref)
    cap = cv2.VideoCapture(a.take)
    if not cap.isOpened():
        raise SystemExit(f"cannot open {a.take}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    sw, sh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    f0 = int(round(a.t0 * fps))
    f1 = int(round(a.t1 * fps)) if a.t1 is not None else None
    det = detector()

    writer = None
    if a.check:
        writer = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{sw // 2}x{sh // 2}",
                                   "-r", f"{fps}", "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", a.check],
                                  stdin=subprocess.PIPE)

    rows, hist = [], []  # hist: the last two trusted corner sets, for the motion prediction
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
        found = detect(det, frame)
        common = [k for k in found if k in ref]
        H_aruco, aruco_rms = None, np.inf
        if common:
            sp = np.concatenate([ref[k] for k in common])
            ip = np.concatenate([found[k] for k in common])
            H_aruco, _ = cv2.findHomography(sp, ip, cv2.RANSAC if len(common) > 1 else 0, 3.0)
            if H_aruco is not None:
                pr = cv2.perspectiveTransform(sp.reshape(-1, 1, 2), H_aruco).reshape(-1, 2)
                aruco_rms = float(np.sqrt(np.mean(np.sum((pr - ip) ** 2, axis=1))))
        # starts for ECC: the motion prediction first, then the markers' fit if it disagrees with it
        starts, blur = [], (0.0, 0.0)
        if hist:
            vel = hist[-1] - hist[-2] if len(hist) == 2 else np.zeros((4, 2))
            pred = hist[-1] + vel
            blur = tuple(vel.mean(0) * a.shutter)
            starts.append(rf.from_corners(pred))
        if H_aruco is not None:
            qa = cv2.perspectiveTransform(rf.corners.reshape(-1, 1, 2), H_aruco).reshape(-1, 2)
            if not hist or np.sqrt(np.mean(np.sum((qa - pred) ** 2, axis=1))) > 3:
                starts.append(H_aruco)
        best, best_score = None, -1.0
        for Hs in starts:
            for bl in ((blur, (0.0, 0.0)) if np.hypot(*blur) > 3 else ((0.0, 0.0),)):
                Hn, score = rf.refine(frame, Hs, bl)
                if Hn is not None and score > best_score:
                    best, best_score = Hn, score
                if best_score >= 0.9:
                    break
            if best_score >= 0.9:
                break
        if best is not None and best_score >= MIN_SCORE:
            Hm, ok = best, (1 if common else 3)
        elif H_aruco is not None and len(common) >= 3 and aruco_rms < 1.5:
            Hm, ok, best_score = H_aruco, 2, -1.0  # the markers alone, only when they agree well
        else:
            Hm, ok, best_score = None, 0, -1.0
        if Hm is not None:
            q = cv2.perspectiveTransform(rf.corners.reshape(-1, 1, 2), Hm).reshape(-1, 2)
            rows.append([f, ok, round(best_score, 4)] + [round(float(v), 3) for v in q.reshape(-1)])
            if ok in (1, 3):
                hist = (hist + [q])[-2:]
        else:
            rows.append([f, 0, -1.0] + [np.nan] * 8)

        if writer:
            out = frame.copy()
            if Hm is not None:
                warped = cv2.warpPerspective(ref_img, Hm, (sw, sh))
                m = cv2.warpPerspective(np.full((H, W), 255, np.uint8), Hm, (sw, sh))
                diff = cv2.absdiff(frame, warped)
                out[m > 0] = diff[m > 0]
                cv2.polylines(out, [q.astype(np.int32)], True, (0, 255, 255) if ok in (1, 3) else (0, 0, 255), 3)
            cv2.putText(out, f"f{f} ok{ok} ecc{best_score:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3)
            writer.stdin.write(cv2.resize(out, (sw // 2, sh // 2), interpolation=cv2.INTER_AREA).tobytes())

    if writer:
        writer.stdin.close()
        writer.wait()

    arr = np.array([r[3:] for r in rows], np.float64)
    good = ~np.isnan(arr[:, 0])
    if good.sum() == 0:
        raise SystemExit("no frame tracked")
    idx = np.arange(len(arr))
    for j in range(8):  # fill the gaps (flagged ok 0)
        arr[:, j] = np.interp(idx, idx[good], arr[good, j])
    if a.smooth:
        for j in range(8):
            fwd = one_euro(arr[:, j], fps)
            bwd = one_euro(arr[::-1, j], fps)[::-1]
            arr[:, j] = (fwd + bwd) / 2
    frames = [[r[0], r[1], r[2]] + [round(float(v), 3) for v in arr[i]] for i, r in enumerate(rows)]
    res = {"src": {"file": Path(a.take).name, "w": sw, "h": sh, "fps": fps}, "screen": {"w": W, "h": H}, "from": f0,
           "smoothed": a.smooth, "frames": frames}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res))
    oks = [r[1] for r in rows]
    sc = [r[2] for r in rows if r[1] in (1, 3)]
    print(f"{a.out}: {len(rows)} frames · refined with markers {oks.count(1)} · refined from motion {oks.count(3)} · "
          f"markers only {oks.count(2)} · gaps {oks.count(0)} · ECC score min {min(sc) if sc else float('nan'):.3f}")


if __name__ == "__main__":
    main()
