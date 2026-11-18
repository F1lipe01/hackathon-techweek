"""Real recognition numbers for video 2, computed with the prototype's own models and logic.

    prototype/.venv-vision/bin/python video/tools/recognise.py

It imports the edge service's classes (prototype/edge.py runs its loop only under __main__) and replays:
  1. registration (edge.enrol_step) on the photos the colleague took in the phone recording (each shutter press is
     found from the camera app's own shutter animation): OWLv2 "a photo of book" at threshold 0.06, the best box,
     the size check, a tight crop, DINOv2, and a view kept only when its cosine to every kept view is below 0.97,
     until 8 views. For comparison it also replays the same rule on every frame at 2 per second (the edge loop's
     pace), which fills the 8 views in the first seconds with the front cover only;
  2. recognition (edge.analyse) on the kit camera frame: OWLv2 with the edge service's full query list at threshold
     0.1, the 4 best "book" candidates, each embedded and compared with the fingerprint (max cosine over the 8 views),
     the first at or above 0.62 counts as the book; the place comes from edge.place_of with the places OWLv2 found,
     and edge.Motion is run over the kit footage to show when the service would wake up;
  3. negative controls: the best box for other objects on the desk (and the wallet in the phone recording),
     compared with the same fingerprint;
  4. the same recognition and controls with a 3-view fingerprint (views 1, 5 and 8), written as "views3".
Writes video/public/real/recognition.json (plus src/real/recognition.ts, the same data for the edit), the 8 view
crops in public/real/views/, the kit crop and the control crops. Deterministic: the same footage gives the same numbers.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "prototype"))
import edge  # noqa: E402  (only classes and helpers; main() is not called)

VIDEO = ROOT / "video"
FOOT = VIDEO / "public" / "footage"
OUT = VIDEO / "public" / "real"
PHONE = FOOT / "phone-photos.mp4"
KIT = FOOT / "kit-desk.mp4"
PREVIEW = (0, 65, 392, 589)        # the phone camera's preview inside the 392x850 screen recording
SAMPLE_FPS = 2                      # the edge loop checks twice a second
MATCH = 0.62                        # edge.py --match default
VIEWS3 = (1, 5, 8)                  # the 3 photos the video shows: front cover, an angle, flat on the desk
QUERY = "a photo of book"           # edge.query_for({"name": "Book"}) and enrol_step's f"a photo of {query}"


def frame_at(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGB")


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def shutter_presses(path, w=392, h=850):
    """Seconds at which the camera app's shutter button animates: the moments a photo was taken."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    d = np.abs(np.diff(a[:, 670:740, 160:232], axis=0)).mean(axis=(1, 2))
    out, last = [], -9.0
    for i, v in enumerate(d):
        t = (i + 1) / 30
        if v > 6 and t - last > 2:
            out.append(round(t, 2))
            last = t
        elif v > 6:
            last = t
    return out


def enrol(det, emb, times, save):
    """edge.enrol_step's rule over a list of moments; returns kept views, their vectors and a log."""
    views, vecs, log = [], [], []
    for t in times:
        if len(vecs) >= edge.ENROL_VIEWS:
            break
        img = frame_at(PHONE, t).crop(PREVIEW)
        dets = det(img, [QUERY], threshold=0.06)
        if not dets:
            log.append({"t": r(t, 2), "owl": None, "kept": False})
            continue
        q, s, b = max(dets, key=lambda d: d[1])
        if (b[2] - b[0]) * (b[3] - b[1]) <= 0.002 * img.width * img.height:
            log.append({"t": r(t, 2), "owl": r(s, 3), "kept": False, "why": "too small"})
            continue
        crop = edge.tight_crop(img, b)
        v = emb([crop])[0]
        cos = [float(v @ u) for u in vecs]
        kept = all(c < 0.97 for c in cos)
        log.append({"t": r(t, 2), "owl": r(s, 3), "max_cos_to_kept": r(max(cos), 3) if cos else None, "kept": kept})
        if kept:
            vecs.append(v)
            n = len(vecs)
            box_full = [b[0] + PREVIEW[0], b[1] + PREVIEW[1], b[2] + PREVIEW[0], b[3] + PREVIEW[1]]
            view = {"t": r(t, 2), "owl_score": r(s, 3), "box_phone_px": [r(x, 1) for x in box_full],
                    "max_cos_to_previous": r(max(cos), 3) if cos else None}
            if save:
                crop.save(OUT / "views" / f"view-{n}.jpg", quality=92)
                view = {"file": f"real/views/view-{n}.jpg", **view}
            views.append(view)
            print(f"view {n} at {t:.2f}s  owl {s:.2f}  max cos {max(cos) if cos else 0:.3f}", flush=True)
    return views, np.asarray(vecs, dtype=np.float32), log


def r(v, n=4):
    return round(float(v), n)


def main():
    det = edge.Detector()
    emb = edge.Embedder(det.dev)
    print("models on", det.dev, flush=True)

    # 1. Registration, as enrol_step does it, on the photos the colleague took
    presses = shutter_presses(PHONE)
    print("shutter presses at", presses, flush=True)
    views, fp, log = enrol(det, emb, presses, save=True)
    assert len(fp) == edge.ENROL_VIEWS, f"only {len(fp)} views"
    # the same rule on every frame at the edge loop's pace, for comparison
    every = [i / SAMPLE_FPS for i in range(int(duration(PHONE) * SAMPLE_FPS))]
    views_2fps, fp_2fps, _ = enrol(det, emb, every, save=False)

    # 2. Recognition on the kit camera, as analyse() does it
    frame_s = 10.0
    kit = frame_at(KIT, frame_s)
    queries = [QUERY] + list(edge.PLACES.values()) + [edge.PERSON] + list(edge.PROFILE.values())
    dets = det(kit, queries, threshold=0.1)
    cands = sorted([(s, b) for q, s, b in dets if q == QUERY], key=lambda c: -c[0])[:4]
    sims = (emb([edge.tight_crop(kit, b) for s, b in cands]) @ fp.T).max(axis=1) if cands else []
    candidates, book = [], None
    for (s, b), sim in zip(cands, sims):
        candidates.append({"box": [r(x, 1) for x in b], "owl_score": r(s, 3), "similarity": r(sim, 3)})
        if book is None and sim >= MATCH:
            book = (s, b, float(sim))
    others = [{"label": q, "box": [r(x, 1) for x in b], "owl_score": r(s, 3)} for q, s, b in dets if q != QUERY]
    if book is None:
        print("WARNING: no candidate reached the threshold", flush=True)
        s, b = cands[0]
        book = (s, b, float(sims[0]))
    print(f"kit book box {[round(x) for x in book[1]]}  owl {book[0]:.3f}  similarity {book[2]:.3f}", flush=True)
    book_vec = emb([edge.tight_crop(kit, book[1])])[0]
    per_view = [r(x, 3) for x in (fp @ book_vec)]
    sim_2fps = float((fp_2fps @ book_vec).max())
    print("per view", per_view, " | 2 fps replay fingerprint:", round(sim_2fps, 3), flush=True)
    edge.tight_crop(kit, book[1]).save(OUT / "kit-book-crop.jpg", quality=92)

    # the place: edge.place_of with the places OWLv2 found (score >= 0.18), as analyse() does
    places = [(k, b) for q, s_, b in dets for k, v in edge.PLACES.items() if q == v and s_ >= 0.18]
    place = edge.place_of(book[1], places)
    place_box = None
    cx, cy = (book[1][0] + book[1][2]) / 2, book[1][3]
    best = None
    for k, pb in places:
        if k == place and pb[0] <= cx <= pb[2] and pb[1] - 20 <= cy <= pb[3] + 20:
            area = (pb[2] - pb[0]) * (pb[3] - pb[1])
            if best is None or area < best[0]:
                best = (area, pb)
    if best:
        place_box = [r(x, 1) for x in best[1]]
    place_score = next((r(s_, 3) for q, s_, b in dets if place_box and [r(x, 1) for x in b] == place_box), None)
    people = [(s_, b) for q, s_, b in dets if q == edge.PERSON and s_ >= 0.2]
    print(f"place {place} {place_box} ({place_score}); people {len(people)}", flush=True)

    # the edge service's cheap motion check on the kit footage, twice a second
    motion, mlog = edge.Motion(), []
    for i in range(int(duration(KIT) * 2)):
        moved, frac = motion.changed(frame_at(KIT, i / 2))
        mlog.append({"t": i / 2, "changed": r(frac, 4), "moved": bool(moved)})
    print("motion at", [m["t"] for m in mlog if m["moved"]], flush=True)

    # 3. Negative controls: other objects on the same desk, against the book's fingerprint
    controls, ctrl_vecs = [], {}
    for label, q in [("garrafa", "a photo of bottle"), ("carteira", "a photo of wallet"),
                     ("auscultadores", "a photo of earbuds case"), ("teclado", "a photo of keyboard")]:
        d = det(kit, [q], threshold=0.05)
        if not d:
            controls.append({"label": label, "query": q, "box": None, "score": None})
            continue
        _, s, b = max(d, key=lambda x: x[1])
        cv = emb([edge.tight_crop(kit, b)])[0]
        ctrl_vecs[label] = cv
        sim = float((fp @ cv).max())
        edge.tight_crop(kit, b).save(OUT / f"control-{label}.jpg", quality=92)
        controls.append({"label": label, "query": q, "box": [r(x, 1) for x in b], "owl_score": r(s, 3), "score": r(sim, 3)})
        print(f"control {label}: box {[round(x) for x in b]} owl {s:.2f} similarity {sim:.3f}", flush=True)

    # the wallet the colleague left next to the book at the end of the phone recording (a different camera)
    wal = None
    for tw in (38.0, 38.5, 39.0, 39.5):
        img = frame_at(PHONE, tw).crop(PREVIEW)
        d = det(img, ["a photo of wallet"], threshold=0.05)
        if d:
            _, s, b = max(d, key=lambda x: x[1])
            wv = emb([edge.tight_crop(img, b)])[0]
            sim = float((fp @ wv).max())
            if wal is None or s > wal["owl_score"]:
                ctrl_vecs["carteira (telemóvel)"] = wv
                edge.tight_crop(img, b).save(OUT / "control-carteira-telemovel.jpg", quality=92)
                wal = {"label": "carteira (telemóvel)", "t": tw, "box_preview_px": [r(x, 1) for x in b],
                       "owl_score": r(s, 3), "score": r(sim, 3)}
    if wal:
        print(f"phone wallet at {wal['t']}s: owl {wal['owl_score']} similarity {wal['score']}", flush=True)

    primary = next((c for c in controls if c["label"] == "garrafa" and c["score"] is not None), controls[0])

    # 4. The same recognition with only 3 of the 8 views as the fingerprint (the 3 photos the video shows)
    idx = [n - 1 for n in VIEWS3]
    fp3 = fp[idx]
    pair = [float(fp3[i] @ fp3[j]) for i in range(len(idx)) for j in range(i + 1, len(idx))]
    per3 = [r(x, 3) for x in (fp3 @ book_vec)]
    score3 = max(per3)
    ctrl3 = {k: r(float((fp3 @ v).max()), 3) for k, v in ctrl_vecs.items()}
    views3 = {
        "note": "Fingerprint made of 3 of the 8 kept views (front cover, an angle, flat on the desk); the same max over "
                "views and the same 0.62 threshold. The 3 views are distinct under edge.enrol_step's rule (cos < 0.97).",
        "views": [{"n": n, "file": views[n - 1]["file"], "t": views[n - 1]["t"]} for n in VIEWS3],
        "max_cos_between_views": r(max(pair), 3),
        "kit": {"frame_s": frame_s, "book_box": [r(x, 1) for x in book[1]], "per_view": per3, "score": score3,
                "best_view": VIEWS3[per3.index(score3)], "threshold": MATCH, "recognised": bool(score3 >= MATCH)},
        "control": {"label": primary["label"], "query": primary["query"], "box": primary["box"],
                    "score": ctrl3.get(primary["label"])},
        "controls": [{"label": k, "score": v} for k, v in ctrl3.items()],
    }
    print(f"3 views {VIEWS3}: per view {per3}, score {score3}, control {ctrl3}", flush=True)
    result = {
        "note": "Computed by video/tools/recognise.py with prototype/edge.py's Detector (OWLv2 base patch16 ensemble), "
                "Embedder (DINOv2 small) and its registration and recognition logic.",
        "query": QUERY,
        "photos_taken_s": presses,
        "views": views,
        "registration_log": log,
        "replay_every_frame_2fps": {"views_t": [v["t"] for v in views_2fps],
                                    "kit_score": r(sim_2fps, 3),
                                    "note": "edge.enrol_step's rule on every frame at 2 per second: the 8 views all "
                                            "come from the front cover in the first seconds, and the book on the "
                                            "kit camera does not reach 0.62 against that fingerprint."},
        "kit": {"video": "footage/kit-desk.mp4", "frame_s": frame_s, "size": [kit.width, kit.height],
                "book_box": [r(x, 1) for x in book[1]], "owl_score": r(book[0], 3), "score": r(book[2], 3),
                "threshold": MATCH, "recognised": bool(book[2] >= MATCH),
                "place": place, "place_box": place_box, "place_score": place_score,
                "people": [{"box": [r(x, 1) for x in b], "owl_score": r(s_, 3)} for s_, b in people],
                "motion": {"rule": "edge.Motion: 160x90 grey, pixel change > 22, area > 0.6 %", "samples": mlog}, "per_view": per_view, "candidates": candidates, "other_detections": others},
        "control": {"label": primary["label"], "query": primary["query"], "box": primary["box"],
                    "owl_score": primary.get("owl_score"), "score": primary["score"]},
        "controls": controls + ([wal] if wal else []),
        "views3": views3,
    }
    text = json.dumps(result, indent=1, ensure_ascii=False)
    (OUT / "recognition.json").write_text(text)
    (VIDEO / "src" / "real" / "recognition.ts").write_text(
        "// Generated by video/tools/recognise.py from the prototype's own models. Do not edit by hand.\n"
        f"export const R = {text} as const;\n")
    print("wrote", OUT / "recognition.json", flush=True)


if __name__ == "__main__":
    main()
