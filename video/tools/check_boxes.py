"""Draw hand-placed box keys over a clip's frames, tiled at full width, to check them by eye.
    python3 video/tools/check_boxes.py <clip> <t0> <t1> <step> '<json keys: [[t,x1,y1,x2,y2],...]>' <out.jpg> [cols]
Keys are in the clip's source pixels; between keys the box eases (smoothstep), as in the film."""
import json, sys
from pathlib import Path
import cv2
import numpy as np
clip, t0, t1, step, keys, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), json.loads(sys.argv[5]), sys.argv[6]
cols = int(sys.argv[7]) if len(sys.argv) > 7 else 3
cap = cv2.VideoCapture(str(Path(__file__).resolve().parents[1] / "public" / "stock" / f"{clip}.mp4"))
fps = cap.get(cv2.CAP_PROP_FPS)
def box_at(t):
    i = 0
    while i < len(keys) - 2 and keys[i + 1][0] <= t: i += 1
    a, b = keys[i], keys[min(i + 1, len(keys) - 1)]
    u = min(1, max(0, (t - a[0]) / (b[0] - a[0]))) if b[0] > a[0] else 0
    u = u * u * (3 - 2 * u)
    return [a[j] + (b[j] - a[j]) * u for j in range(1, 5)]
tiles = []
t = t0
while t <= t1 + 1e-6:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps)))
    ok, img = cap.read()
    x1, y1, x2, y2 = [int(v) for v in box_at(t)]
    th = max(2, img.shape[1] // 800)
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 120, 0), th)
    cv2.putText(img, f"{t:.2f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.4, (0, 0, 255), 5)
    w = 960 if cols <= 2 else 640
    tiles.append(cv2.resize(img, (w, int(w * img.shape[0] / img.shape[1]))))
    t += step
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
