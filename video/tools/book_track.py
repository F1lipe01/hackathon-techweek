"""The book's recognition over film 1's take, with the prototype's own models and matching rule (real model output for the
film's "livro" box, and an honest measure of how often the book is recognised on the ceiling camera).

    prototype/.venv-vision/bin/python video/tools/book_track.py video/public/takes/scene1/book-full.mp4 out.json [--every 0.5]

For each sampled frame, as edge.analyse() does it: the frame at 1280 px; OWLv2 with the edge's query list at threshold 0.1;
the 4 best "a photo of book" candidates; each tight-cropped, embedded by DINOv2 and compared with the book's fingerprint
stored in the prototype's SQLite database (the max cosine over its views); the first at or above 0.62 is the book.
Writes {"match": 0.62, "frames": [{"t", "cands": [{"box", "owl", "sim"}], "book": {"box", "sim"} | null}]}.
"""
import argparse
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

MATCH = 0.62
QUERY = "a photo of book"          # edge.query_for({"name": "Book"})
W, H = 1280, 720

ap = argparse.ArgumentParser()
ap.add_argument("take"); ap.add_argument("out")
ap.add_argument("--every", type=float, default=0.5)
a = ap.parse_args()

db = sqlite3.connect(f"file:{ROOT / 'prototype/data/home.db'}?mode=ro", uri=True)
row = db.execute("select vectors from fingerprints where thing_id = 'book'").fetchone()
assert row, "the book has no fingerprint in the database"
fp = np.asarray(json.loads(row[0]), dtype=np.float32)
fp /= np.linalg.norm(fp, axis=1, keepdims=True)
print(f"fingerprint: {fp.shape[0]} views of {fp.shape[1]} numbers")

det = edge.Detector()
emb = edge.Embedder(det.dev)
queries = [QUERY] + list(edge.PLACES.values()) + [edge.PERSON] + list(edge.PROFILE.values())
pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.take, "-vf", f"fps={1 / a.every},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                        stdout=subprocess.PIPE)
frames, i = [], 0
while True:
    buf = pipe.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = round(i * a.every, 2); i += 1
    img = Image.fromarray(np.frombuffer(buf, np.uint8).reshape(H, W, 3))
    dets = det(img, queries, threshold=0.1)
    cands = sorted([(s, b) for l, s, b in dets if l == QUERY], key=lambda x: -x[0])[:4]
    sims = (emb([edge.tight_crop(img, b) for s, b in cands]) @ fp.T).max(axis=1) if cands else []
    cs = [{"box": [round(b[0] / W, 4), round(b[1] / H, 4), round(b[2] / W, 4), round(b[3] / H, 4)], "owl": round(float(s), 3), "sim": round(float(m), 3)}
          for (s, b), m in zip(cands, sims)]
    book = next((c for c in cs if c["sim"] >= MATCH), None)
    frames.append({"t": t, "cands": cs, "book": book})
    print(f"{t:6.1f}  best sim {max([c['sim'] for c in cs], default=0):.2f}  {'BOOK' if book else '-'}", flush=True)
Path(a.out).write_text(json.dumps({"match": MATCH, "query": QUERY, "frames": frames}))
print("written", a.out)
