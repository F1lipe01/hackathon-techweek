"""Real OWLv2 boxes for the stock clips in video/public/stock/, computed with the prototype's own detector.

    video/tools/heavy.sh prototype/.venv-vision/bin/python video/tools/stock_boxes.py <clip> [--preview DIR]

One clip per call (heavy.sh lets other jobs interleave). <clip> is the file stem in stock.json, e.g. cat-counter-1.
It imports prototype/edge.py's Detector (OWLv2 base patch16 ensemble; edge.py runs its loop only under __main__),
samples the clip once per second, asks for the scene's subjects at edge.analyse's detection threshold (0.1), and writes
  video/public/stock/boxes/<clip>.json   every box at or above the threshold: time, label, score, normalised box
                                         [x1, y1, x2, y2], and its rank among that label's boxes in the same frame;
  video/public/stock/stock.json          the clip's detection summary (labels found, top scores, when).
No box is moved, merged or invented. The edit chooses which to draw (e.g. rank 1 only, or the edge service's own display
thresholds: person 0.2, dog or cat 0.45, a place 0.18). Deterministic: the same clip gives the same numbers.
"""
import argparse
import json
import subprocess
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "prototype"))
import edge  # noqa: E402  (only the Detector class; main() is not called)

STOCK = ROOT / "video" / "public" / "stock"
THRESHOLD = 0.1          # edge.analyse: det(img, queries, threshold=0.1)
STEP_S = 1.0             # one frame per second
DETECT_WIDTH = 1920      # OWLv2 resizes to 960 x 960 anyway; boxes are stored normalised
DISPLAY = {"a person": 0.2, "a dog": 0.45, "a cat": 0.45, "a table": 0.18, "a sofa": 0.18}   # edge.analyse's own

QUERIES = {
    "cat-counter": ["a cat", "a knife", "a kitchen counter"],
    "dog-bowl": ["a dog", "a pet bowl"],
    "older-kitchen": ["a person", "a kettle"],
    "leaving-home": ["a person", "a door", "a bag"],
    "leaving-home-keys": ["a person", "a door", "a bag", "keys"],
    "phone-alert": ["a phone", "a hand"],
    "parcel-door": ["a parcel box", "a package", "a door"],   # "a package" also finds a soft mailer bag
    "garden-night": ["a person"],
    "child-kitchen": ["a hand", "a stove"],
    "establishing": ["a person", "a sofa", "a table"],
}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL).stdout
    return float(out.strip())


def frame_at(path, t):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-threads", "2", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                          "-vf", f"scale='min({DETECT_WIDTH},iw)':-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout
    return Image.open(BytesIO(raw)).convert("RGB")


def r(v, n=4):
    return round(float(v), n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--preview", help="folder for a JPEG of the best frame with its rank-1 boxes, to check by eye")
    args = ap.parse_args()

    manifest_path = STOCK / "stock.json"
    manifest = json.loads(manifest_path.read_text())
    entry = next(c for c in manifest["clips"] if Path(c["file"]).stem == args.clip)
    video = STOCK / entry["file"]
    queries = QUERIES[entry.get("queries_for", entry["scene"])]

    det = edge.Detector()
    total = duration(video)
    times = [i * STEP_S for i in range(int(total / STEP_S) + 1) if i * STEP_S < total - 0.05]
    frames, best = [], None
    for t in times:
        img = frame_at(video, t)
        dets = det(img, queries, threshold=THRESHOLD)
        boxes = []
        for q in queries:
            mine = sorted([(s, b) for qq, s, b in dets if qq == q], key=lambda x: -x[0])
            for rank, (s, b) in enumerate(mine, 1):
                boxes.append({"label": q, "score": r(s, 3), "rank": rank, "box": edge.norm_box(img, b)})
        frames.append({"t": r(t, 2), "boxes": boxes})
        top = max((b["score"] for b in boxes), default=0)
        if best is None or top > best[0]:
            best = (top, t, img, [b for b in boxes if b["rank"] == 1])
        print(f"{args.clip} {t:5.1f}s  " + ", ".join(f"{b['label']} {b['score']:.2f}" for b in boxes if b["rank"] == 1),
              flush=True)

    summary = {}
    for q in queries:
        hits = [(f["t"], b["score"]) for f in frames for b in f["boxes"] if b["label"] == q and b["rank"] == 1]
        disp = DISPLAY.get(q)
        summary[q] = {
            "frames_seen": len(hits), "frames_total": len(frames),
            "top_score": max((s for _, s in hits), default=None),
            "top_t": max(hits, key=lambda h: h[1])[0] if hits else None,
            "first_t": hits[0][0] if hits else None, "last_t": hits[-1][0] if hits else None,
            **({"edge_display_threshold": disp, "frames_at_display": sum(1 for _, s in hits if s >= disp)} if disp else {}),
        }

    out = {
        "clip": entry["file"], "scene": entry["scene"],
        "note": "OWLv2 (google/owlv2-base-patch16-ensemble) through prototype/edge.py's Detector, by "
                "video/tools/stock_boxes.py. Boxes are normalised [x1, y1, x2, y2] in the clip's frame; rank 1 is the "
                "best box for that label in that frame. All boxes at or above the threshold are kept, none altered.",
        "model": "google/owlv2-base-patch16-ensemble", "queries": queries, "threshold": THRESHOLD, "step_s": STEP_S,
        "frame_size": list(frame_at(video, 0).size), "duration_s": r(total, 3), "summary": summary, "frames": frames,
    }
    (STOCK / "boxes").mkdir(exist_ok=True)
    (STOCK / "boxes" / f"{args.clip}.json").write_text(json.dumps(out, indent=1))

    entry["detection"] = {"boxes": f"stock/boxes/{args.clip}.json", "queries": queries, "threshold": THRESHOLD,
                          "step_s": STEP_S,
                          "found": {q: {k: v for k, v in s.items() if k in ("top_score", "top_t", "frames_seen",
                                                                                "frames_total", "frames_at_display")}
                                    for q, s in summary.items() if s["frames_seen"]},
                          "not_found": [q for q, s in summary.items() if not s["frames_seen"]]}
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")

    if args.preview and best:
        _, t, img, boxes = best
        d = ImageDraw.Draw(img)
        for b in boxes:
            x1, y1, x2, y2 = (b["box"][0] * img.width, b["box"][1] * img.height,
                              b["box"][2] * img.width, b["box"][3] * img.height)
            d.rectangle((x1, y1, x2, y2), outline=(255, 220, 0), width=4)
            d.text((x1 + 6, y1 + 6), f"{b['label']} {b['score']:.2f}", fill=(255, 220, 0))
        Path(args.preview).mkdir(parents=True, exist_ok=True)
        img.thumbnail((960, 960))
        img.save(Path(args.preview) / f"{args.clip}@{t:.0f}s.jpg", quality=80)
    print("wrote", STOCK / "boxes" / f"{args.clip}.json", flush=True)


if __name__ == "__main__":
    main()
