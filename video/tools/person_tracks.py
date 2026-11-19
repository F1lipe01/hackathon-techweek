"""People as tracks for the edit, from the detector's boxes on a take (example 3's main take).
    python3 video/tools/person_tracks.py stage1.boxes.json stage1.right.boxes.json stage1.persons.json
The whole-frame run and a full-resolution run on the right corner (where people sit at the frame's edge) are merged:
- boxes below each run's score threshold, and the fixed false finds (the jacket on the chair, a poster), are dropped;
- boxes that cover the same person are merged;
- boxes are linked into tracks frame to frame.
A track that loses its person keeps the last box while it may be hidden: up to 7,5 s for someone seated at the right
edge (behind the monitors), 1 s elsewhere, as a tracker keeps a still person. Tracks seen fewer than three times are
dropped. Output: {"tracks": [{"keys": [[t, x0, y0, x1, y1], ...]}]}; the film interpolates between keys."""
import json
import sys

full, right, out = sys.argv[1:4]
A = json.load(open(full)); B = json.load(open(right))


def cx(b): return (b[0] + b[2]) / 2


def iou(p, q):
    ix = max(0, min(p[2], q[2]) - max(p[0], q[0])); iy = max(0, min(p[3], q[3]) - max(p[1], q[1]))
    i = ix * iy; u = (p[2] - p[0]) * (p[3] - p[1]) + (q[2] - q[0]) * (q[3] - q[1]) - i
    return i / u if u else 0


def fixed_false(b):
    return cx(b) < 0.12 or (abs(cx(b) - 0.74) < 0.02 and abs((b[1] + b[3]) / 2 - 0.46) < 0.03)   # the jacket; a coat at the back


det = {}
for f in A["frames"]:
    det.setdefault(round(f["t"], 2), []).extend(b["box"] for b in f["boxes"] if b["label"] == "a person" and b["score"] >= 0.17 and not fixed_false(b["box"]))
for f in B["frames"]:
    det.setdefault(round(f["t"], 2), []).extend(b["box"] for b in f["boxes"] if b["label"] == "a person" and b["score"] >= 0.15 and cx(b["box"]) > 0.80 and not fixed_false(b["box"]))
tracks, active = [], []
for t in sorted(det):
    boxes = []
    for b in det[t]:                                          # one box per person
        if all(iou(b, k) < 0.45 for k in boxes):
            boxes.append(b)
    used = set()
    for tr in active:
        last = tr["keys"][-1]
        cands = [(iou(last[1:], b), i) for i, b in enumerate(boxes) if i not in used]
        cands += [(0.01, i) for i, b in enumerate(boxes) if i not in used and abs(cx(b) - cx(last[1:])) < 0.06 and iou(last[1:], b) == 0]
        if cands:
            sc, i = max(cands)
            if sc > 0:
                tr["keys"].append([t, *boxes[i]]); used.add(i)
    for i, b in enumerate(boxes):
        if i not in used:
            tr = {"keys": [[t, *b]]}; tracks.append(tr); active.append(tr)
    active = [tr for tr in active if t - tr["keys"][-1][0] <= (7.5 if cx(tr["keys"][-1][1:]) > 0.85 else 1.0)]
keep = [tr for tr in tracks if len(tr["keys"]) >= 3]
json.dump({"tracks": keep}, open(out, "w"))
print(f"{len(keep)} tracks (of {len(tracks)})")
for tr in keep:
    k = tr["keys"]; gaps = [round(k[i + 1][0] - k[i][0], 1) for i in range(len(k) - 1) if k[i + 1][0] - k[i][0] > 0.6]
    print(f"  {k[0][0]:.1f}-{k[-1][0]:.1f} s from x {cx(k[0][1:]):.2f} to {cx(k[-1][1:]):.2f}, {len(k)} keys, held gaps {gaps}")
