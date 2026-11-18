"""Find one-frame glitches in a rendered film: a frame unlike both of its neighbours while they agree with each other
(a flash, a frame of footage drawn wrong). Prints their frame numbers, one per line; nothing when the film is clean.
    python3 video/tools/glitch_check.py <video.mp4>
On 18 Nov 2026 a 1080p render had three such frames (stock footage drawn as a 3 × 3 grid of small copies); a still of
the same frame rendered correctly, so they are re-rendered as stills and patched in with tools/patch_frames.sh."""
import subprocess
import sys

import numpy as np

W, H = 192, 108
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)
d = np.abs(np.diff(a, axis=0)).mean((1, 2))  # d[i]: frame i → i+1
for i in range(1, len(a) - 1):
    before, after = d[i - 1], d[i]
    around = np.abs(a[i - 1] - a[i + 1]).mean()
    if before > 4 and after > 4 and around < 0.35 * min(before, after):
        print(i)
