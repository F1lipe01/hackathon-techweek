"""The kit camera's own reaction when the room's lights go off, rebuilt on a night-vision clip of the same view (example 3).
Seen in the team's door retake (19 Nov, 18:09:34): about 0,2 s of near-black with the clock still drawn, then a dim, noisy,
purple-tinted low-light picture in which only lit things show (the corridor's light through the door, the PC's LEDs),
brightening for a few seconds, then the switch to grey night vision. The input is already night vision (its clock
rewritten by fix_osd.py); the first frames are darkened and tinted into that sequence, the clock's white digits kept.

    python3 video/tools/lights_off.py ac-off-lights.mp4 lights-off.mp4 --from 1.5 --to 5.0 --black 0.2 --dim 2.55
"""
import argparse
import subprocess

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--from", dest="t0", type=float, required=True)
ap.add_argument("--to", dest="t1", type=float, required=True)
ap.add_argument("--black", type=float, default=0.2, help="seconds of near-black")
ap.add_argument("--dim", type=float, default=2.55, help="seconds of purple low-light before night vision")
ap.add_argument("--fps", type=float, default=20)
a = ap.parse_args()
W, H = 2304, 1296
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a.t0), "-t", str(a.t1 - a.t0), "-i", a.src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                     capture_output=True, check=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
band = (slice(45, 155), slice(80, 900))                     # the clock, kept as the camera draws it
rng = np.random.default_rng(11)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(a.fps), "-i", "-",
                        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
for i, fr in enumerate(frames):
    t = i / a.fps
    src = fr.astype(np.float32)
    g = src.mean(axis=2)
    if t < a.black:
        out = src * 0.045 + rng.normal(0, 2.2, src.shape) + np.array([3, 1, 2])
    elif t < a.black + a.dim:
        u = (t - a.black) / a.dim
        k = 0.08 + 0.22 * (1 - (1 - u) ** 2)                 # the exposure opens up
        tint = np.array([1.25, 0.78, 1.05], np.float32)      # B, G, R: the low-light purple
        dark = g[..., None] * k * tint
        hi = np.clip((g - 185) / 55, 0, 1)[..., None]        # lit things (the corridor's light, the LEDs) stay bright
        out = hi * src * np.array([1.0, 0.96, 1.0]) + (1 - hi) * dark
        noise = rng.normal(0, 7 + 5 * u, (H // 2, W // 2, 3)).astype(np.float32)   # coarse chroma noise, as a sensor at high gain
        out = cv2.GaussianBlur(out, (3, 3), 0) + cv2.resize(noise, (W, H), interpolation=cv2.INTER_LINEAR)
    else:
        out = src
    if t < a.black + a.dim:
        gb = g[band]
        al = np.clip((gb - 150) / 70, 0, 1)[..., None]
        out[band] = src[band] * al + out[band] * (1 - al)
    enc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
print(f"written {a.out}: {len(frames)} frames")
