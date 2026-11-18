"""Draw tracked screen quads (or hand-set boxes) over frames of a clip, tiled, to check them by eye.
    python3 video/tools/check_quads.py <screens json> <out.jpg> [every_n]"""
import json, sys
from pathlib import Path
import cv2
import numpy as np
d = json.loads(Path(sys.argv[1]).read_text())
every = int(sys.argv[3]) if len(sys.argv) > 3 else 15
root = Path(__file__).resolve().parents[1] / "public" / "stock"
cap = cv2.VideoCapture(str(root / f"{d['clip']}.mp4"))
fps = cap.get(cv2.CAP_PROP_FPS)
tiles = []
for f in d["frames"][::every]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(f[0] * fps)))
    ok, img = cap.read()
    q = np.array(f[1:], dtype=np.int32).reshape(-1, 2)
    cv2.polylines(img, [q], True, (0, 0, 255), max(2, img.shape[1] // 640))
    cv2.putText(img, f"{f[0]:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    tiles.append(cv2.resize(img, (640, int(640 * img.shape[0] / img.shape[1]))))
while len(tiles) % 4:
    tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
cv2.imwrite(sys.argv[2], np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
