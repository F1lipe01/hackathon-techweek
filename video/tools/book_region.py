"""Book recognition on the region around the desk, at the camera's full resolution (the architecture's "only the region
that changed leaves the home", up to 640 x 480 here), with two fingerprints:
  phone : the book's fingerprint in the prototype's database (from the colleague's phone photos);
  camera: 8 views registered from another take of the same camera (book-grab.mp4), by edge.enrol_step's rule
          (OWLv2 at 0.06, a tight crop, DINOv2, a view kept only when its cosine to every kept view is below 0.97).
Recognition as edge.analyse(): OWLv2 "a photo of yellow book" (the thing's own query) at 0.1, the 4 best candidates,
the max cosine to the fingerprint, 0.62 or more is the book. Reported separately for frames with the book on the desk
and frames after it was taken, with the best candidate that is not the book as a control.

    prototype/.venv-vision/bin/python video/tools/book_region.py video/public/takes/scene1 out.json
"""
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "prototype"))
import edge  # noqa: E402

MATCH, QUERY = 0.62, "a photo of yellow book"
FW, FH = 2304, 1296
BOOK = [0.628, 0.7238, 0.6727, 0.7438]                      # where the book lies in book-full (to score, never to find it)
CX, CY = (BOOK[0] + BOOK[2]) / 2 * FW, (BOOK[1] + BOOK[3]) / 2 * FH
RX, RY, RW, RH = int(CX - 320), int(CY - 240), 640, 480     # the region around it, full resolution


def regions(path, every):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={1 / every},crop={RW}:{RH}:{RX}:{RY}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    i = 0
    while True:
        buf = p.stdout.read(RW * RH * 3)
        if len(buf) < RW * RH * 3:
            break
        yield round(i * every, 2), Image.fromarray(np.frombuffer(buf, np.uint8).reshape(RH, RW, 3))
        i += 1


def norm(v):
    v = np.asarray(v, dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def iou_book(b):
    bx = [(BOOK[0] * FW - RX) / RW, (BOOK[1] * FH - RY) / RH, (BOOK[2] * FW - RX) / RW, (BOOK[3] * FH - RY) / RH]
    ix = max(0, min(b[2], bx[2]) - max(b[0], bx[0])); iy = max(0, min(b[3], bx[3]) - max(b[1], bx[1]))
    i = ix * iy; u = (b[2] - b[0]) * (b[3] - b[1]) + (bx[2] - bx[0]) * (bx[3] - bx[1]) - i
    return i / u if u else 0


take_dir, out = Path(sys.argv[1]), sys.argv[2]
det = edge.Detector(); emb = edge.Embedder(det.dev)
db = sqlite3.connect(f"file:{ROOT / 'prototype/data/home.db'}?mode=ro", uri=True)
fps = {"phone": norm(json.loads(db.execute("select vectors from fingerprints where thing_id='book'").fetchone()[0]))}

# camera registration from book-grab, by enrol_step's rule
vecs = []
for t, img in regions(str(take_dir / "book-grab.mp4"), 0.5):
    if len(vecs) >= edge.ENROL_VIEWS:
        break
    d = sorted([(s, b) for l, s, b in det(img, [QUERY], threshold=0.06)], key=lambda x: -x[0])
    if not d:
        continue
    s, b = d[0]
    if (b[2] - b[0]) * (b[3] - b[1]) / (RW * RH) < 0.002:
        continue
    v = norm(emb([edge.tight_crop(img, b)]))[0]
    if all(float(v @ k) < 0.97 for k in vecs):
        vecs.append(v)
fps["camera"] = np.asarray(vecs)
print("camera views registered from book-grab:", len(vecs))

res = {"match": MATCH, "query": QUERY, "region": [RX, RY, RW, RH], "frames": []}
stats = {k: {"present": [], "absent": [], "control": []} for k in fps}
for t, img in regions(str(take_dir / "book-full.mp4"), 0.5):
    d = sorted([(s, b) for l, s, b in det(img, [QUERY] + [edge.PERSON], threshold=0.1) if l == QUERY], key=lambda x: -x[0])[:4]
    crops = [edge.tight_crop(img, b) for s, b in d]
    e = norm(emb(crops)) if crops else np.zeros((0, 384), np.float32)
    row = {"t": t, "cands": []}
    for (s, b), v in zip(d, e):
        nb = [round(b[0] / RW, 4), round(b[1] / RH, 4), round(b[2] / RW, 4), round(b[3] / RH, 4)]
        row["cands"].append({"box": nb, "owl": round(float(s), 3), "on_book": round(iou_book(nb), 2), **{k: round(float((v @ fp.T).max()), 3) for k, fp in fps.items()}})
    res["frames"].append(row)
    present = t < 34.0                                       # he lifts the book at 34,3 s and leaves with it
    for k in fps:
        on = [c[k] for c in row["cands"] if c["on_book"] > 0.2]
        off = [c[k] for c in row["cands"] if c["on_book"] <= 0.2]
        if present and on:
            stats[k]["present"].append(max(on))
        if not present:
            stats[k]["absent"].append(max([c[k] for c in row["cands"]], default=0))
        if off:
            stats[k]["control"].append(max(off))
Path(out).write_text(json.dumps(res))
n_present = sum(1 for f in res["frames"] if f["t"] < 34.0)
boxed = sum(1 for f in res["frames"] if f["t"] < 34.0 and any(c["on_book"] > 0.2 for c in f["cands"]))
print(f"OWLv2 boxed the book in {boxed} of {n_present} frames with it on the desk")
for k, s in stats.items():
    p = np.array(s["present"]); a = np.array(s["absent"]); c = np.array(s["control"])
    print(f"{k:6s} book on desk: median {np.median(p) if len(p) else 0:.2f}, {int((p >= MATCH).sum())} of {len(p)} at or over {MATCH} | "
          f"after it's taken, best anything: max {a.max() if len(a) else 0:.2f} | other objects: median {np.median(c) if len(c) else 0:.2f}, max {c.max() if len(c) else 0:.2f}")
