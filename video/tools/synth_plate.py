"""A synthetic test plate for track_markers.py: a marker screen moved like a hand-held phone over a real photo, with
motion blur (1/50 s at 30 fps), slight defocus, noise and a "thumb" that covers markers for part of the take.
    python3 video/tools/synth_plate.py <marker.png> <background.jpg> <out_dir> [--seconds 3] [--hevc]
Writes <out_dir>/synth.mp4 (or .mov in HEVC) and <out_dir>/truth.json with the screen's true corners per frame
(at the centre of each exposure). Then:
    python3 video/tools/track_markers.py <out_dir>/synth.mp4 <marker.png> <out_dir>/track.json
    python3 video/tools/synth_plate.py --score <out_dir>"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

W_OUT, H_OUT, FPS = 3840, 2160, 30
SUB = 8                     # subframes per exposure
EXPOSURE = (1 / 50) * FPS   # the shutter is open for 0,6 of a frame at 1/50 s


def corners_at(t: float, w: int, h: int):
    """The screen's corners at time t (s): a 600 px-wide portrait phone, swaying at 1-2 Hz, tilting, with a fast flick."""
    s = 620 / w
    cx = 1900 + 120 * np.sin(2 * np.pi * 1.1 * t) + 260 * np.clip((t - 1.6) / 0.3, 0, 1)  # a 0,3 s flick at 1,6 s
    cy = 1080 + 70 * np.sin(2 * np.pi * 1.7 * t + 0.6)
    rot = np.deg2rad(8 * np.sin(2 * np.pi * 0.8 * t) - 4)
    tilt = 0.10 * np.sin(2 * np.pi * 0.6 * t)    # perspective: the top edge narrower or wider
    hw, hh = w * s / 2, h * s / 2
    base = np.array([[-hw * (1 - tilt), -hh], [hw * (1 - tilt), -hh], [hw * (1 + tilt), hh], [-hw * (1 + tilt), hh]])
    R = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]])
    return base @ R.T + [cx, cy]


def render(a):
    mk = cv2.imread(a.marker)
    h, w = mk.shape[:2]
    bg = cv2.resize(cv2.imread(a.background), (W_OUT, H_OUT), interpolation=cv2.INTER_CUBIC)
    src = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    name = "synth.mov" if a.hevc else "synth.mp4"
    codec = ["-c:v", "libx265", "-crf", "20", "-tag:v", "hvc1"] if a.hevc else ["-c:v", "libx264", "-crf", "16"]
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W_OUT}x{H_OUT}",
                          "-r", str(FPS), "-i", "-", *codec, "-pix_fmt", "yuv420p", str(out / name)], stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    truth = []
    n = int(a.seconds * FPS)
    for f in range(n):
        acc = np.zeros((H_OUT, W_OUT, 3), np.float32)
        for k in range(SUB):
            t = (f + (k + 0.5) / SUB * EXPOSURE - EXPOSURE / 2) / FPS
            Q = corners_at(t, w, h).astype(np.float32)
            M = cv2.getPerspectiveTransform(src, Q)
            layer = cv2.warpPerspective(mk, M, (W_OUT, H_OUT), flags=cv2.INTER_LINEAR)
            mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), M, (W_OUT, H_OUT)) > 127
            img = bg.copy()
            img[mask] = layer[mask]
            acc += img
        img = (acc / SUB).astype(np.uint8)
        Qc = corners_at(f / FPS, w, h)
        # a thumb over the lower-right part of the screen from 0,8 s to 1,4 s
        if 0.8 <= f / FPS <= 1.4:
            c = Qc[2] * 0.62 + Qc[0] * 0.38
            cv2.ellipse(img, (int(c[0] + 40), int(c[1] + 160)), (150, 260), 25, 0, 360, (120, 150, 205), -1)
        img = cv2.GaussianBlur(img, (0, 0), 1.2)
        img = np.clip(img.astype(np.int16) + rng.normal(0, 3, img.shape).astype(np.int16), 0, 255).astype(np.uint8)
        p.stdin.write(img.tobytes())
        truth.append([f] + [round(float(v), 3) for v in Qc.reshape(-1)])
    p.stdin.close()
    p.wait()
    (out / "truth.json").write_text(json.dumps({"fps": FPS, "frames": truth}))
    print(out / name, n, "frames")


def score(out_dir: str):
    d = Path(out_dir)
    truth = {r[0]: np.array(r[1:]).reshape(4, 2) for r in json.loads((d / "truth.json").read_text())["frames"]}
    tr = json.loads((d / "track.json").read_text())
    errs, by_ok = [], {0: [], 1: [], 2: [], 3: []}
    for r in tr["frames"]:
        e = np.linalg.norm(np.array(r[3:]).reshape(4, 2) - truth[r[0]], axis=1)
        errs.append(np.sqrt(np.mean(e ** 2)))
        by_ok[r[1]].append(errs[-1])
    errs = np.array(errs)
    print(f"corner RMS error: median {np.median(errs):.3f} px, 95th {np.percentile(errs, 95):.3f} px, max {errs.max():.3f} px")
    for k, v in by_ok.items():
        if v:
            print(f"  ok={k}: {len(v)} frames, median {np.median(v):.3f} px, max {max(v):.3f} px")
    return errs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("marker", nargs="?")
    ap.add_argument("background", nargs="?")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--seconds", type=float, default=3)
    ap.add_argument("--hevc", action="store_true")
    ap.add_argument("--score", default=None)
    a = ap.parse_args()
    if a.score:
        score(a.score)
    else:
        render(a)
