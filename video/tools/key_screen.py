"""Cut the thumb (and the screen's real edge and reflections) out of a take filmed with the green marker screen, so they
can sit on top of the inserted app.
    python3 video/tools/key_screen.py <take> <track.json> <out.webm> [--margin 0.03]
<track.json> comes from track_markers.py. For each tracked frame, inside the screen's quad grown by --margin:
  - a soft hue key removes the screen's greens (100-170 deg hue, saturation over about 0,35, not near-black); skin, the
    bezel, the Dynamic Island and reflections that wash the green out stay;
  - the matte is choked by 1 px and softened by 1 px;
  - green spill on what stays is removed (G = min(G, max(R, B))).
Everything outside the quad is transparent (the plate underneath shows it anyway).
Writes <out.webm> (VP9 with alpha, cropped to the area the screen ever covers) and <out.webm>.json:
{"crop":[x, y, w, h], "first": source frame of the webm's first frame, "fps", "src":[w, h]}."""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def grown(q, margin):
    c = q.mean(0)
    return c + (q - c) * (1 + margin)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("take")
    ap.add_argument("track")
    ap.add_argument("out")
    ap.add_argument("--margin", type=float, default=0.03)
    a = ap.parse_args()

    tr = json.loads(Path(a.track).read_text())
    rows = {r[0]: np.array(r[3:], np.float64).reshape(4, 2) for r in tr["frames"]}
    first, last = min(rows), max(rows)
    sw, sh = tr["src"]["w"], tr["src"]["h"]
    allq = np.concatenate([grown(q, a.margin) for q in rows.values()])
    x0, y0 = np.floor(allq.min(0)).astype(int)
    x1, y1 = np.ceil(allq.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(sw, x1), min(sh, y1)
    w, h = (x1 - x0) // 2 * 2, (y1 - y0) // 2 * 2

    cap = cv2.VideoCapture(a.take)
    fps = cap.get(cv2.CAP_PROP_FPS)
    enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", f"{fps}",
                            "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "22", "-row-mt", "1",
                            "-deadline", "good", "-cpu-used", "4", "-auto-alt-ref", "0", a.out], stdin=subprocess.PIPE)
    k3 = np.ones((3, 3), np.uint8)
    f = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        f += 1
        if f < first:
            continue
        if f > last:
            break
        crop = frame[y0:y0 + h, x0:x0 + w]
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV).astype(np.float32)
        hue, sat, val = hsv[:, :, 0] * 2, hsv[:, :, 1] / 255, hsv[:, :, 2] / 255  # hue in degrees
        green = smoothstep(92, 104, hue) * (1 - smoothstep(166, 178, hue)) * smoothstep(0.25, 0.45, sat) * smoothstep(0.05, 0.12, val)
        keep = 1 - green
        inside = np.zeros((h, w), np.uint8)
        cv2.fillConvexPoly(inside, np.round(grown(rows[f], a.margin) - [x0, y0]).astype(np.int32), 255)
        alpha = (keep * 255).astype(np.uint8)
        alpha = cv2.erode(alpha, k3)                      # choke 1 px
        alpha = cv2.GaussianBlur(alpha, (0, 0), 0.8)     # soften 1 px
        alpha = np.minimum(alpha, inside)
        b, g, r = cv2.split(crop)
        g = np.minimum(g, np.maximum(r, b))              # despill
        rgba = cv2.merge([r, g, b, alpha])
        enc.stdin.write(rgba.tobytes())
    enc.stdin.close()
    enc.wait()
    Path(a.out + ".json").write_text(json.dumps({"crop": [int(x0), int(y0), int(w), int(h)], "first": int(first), "fps": fps, "src": [sw, sh]}))
    print(a.out, f"{w}x{h} at ({x0},{y0}), source frames {first}-{last}")


if __name__ == "__main__":
    main()
