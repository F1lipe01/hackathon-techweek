"""Faces, on the home device and opt-in: detection with YuNet, recognition with SFace, both through OpenCV.

    prototype/.venv-vision/bin/python prototype/faces.py enrol-video --person filipe --video face.mp4 [--db edge.db]
    prototype/.venv-vision/bin/python prototype/faces.py enrol-image --person joao --image joao.jpg [--db edge.db]
    prototype/.venv-vision/bin/python prototype/faces.py look --video take.mp4 --t 19 --box 760 380 1060 1100 [--db edge.db]

The models (numpy and cv2 only, CPU, no torch). They are downloaded once into prototype/models/ (gitignored) and are
loaded only as weights through cv2.FaceDetectorYN / cv2.FaceRecognizerSF; nothing downloaded is ever executed.
  YuNet, face_detection_yunet_2023mar.onnx (Wu, Peng and Yu, 2023), licence MIT (Copyright (c) 2020 Shiqi Yu).
    https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet  (README "License" and LICENSE file)
    sha256 8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4
  SFace, face_recognition_sface_2021dec.onnx (Zhong et al., MobileFaceNet trained with the SFace loss), licence
    Apache-2.0.  https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface  (README and LICENSE)
    sha256 0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79
  Checked on 19 Nov 2026 with opencv-python-headless 5.1.0 in prototype/.venv-vision.

What it does. A face is looked for only inside a person box the detector (OWLv2) already found. The box is cropped
and enlarged so YuNet sees the face well (the kit camera's faces are about 70 px in a 2304 x 1296 frame), the face is
aligned on its 5 landmarks (alignCrop, 112 x 112) and SFace turns it into 128 numbers. Two faces are the same person
when the cosine of their vectors is high. Each person of the family keeps up to 8 vectors (templates) from a short
video of their face or from photos; a face is compared with every template and the best cosine counts.

The answer for one person box is one of three: the name of a known person, "unknown" (a face is clearly visible and
matches nobody), or "not_visible" (no face, or a face too small or too turned to judge). Only a clearly visible face
can be called unknown, so a family member seen from behind or in profile is never called a stranger.

Threshold. OpenCV recommends a cosine of 0.363 for SFace (same person at or above it), set on aligned, sharp,
close-up faces. This file uses 0.30 (MATCH_THRESHOLD), chosen from the scores measured on the lab take, together with
three gates on what counts as a visible face (score, size, turn): see THRESHOLD_NOTE for the numbers.
"""
import argparse
import json
import os
import sqlite3
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
DATA = Path(os.environ.get("TT_DATA") or HERE / "data")
YUNET = "face_detection_yunet_2023mar.onnx"
SFACE = "face_recognition_sface_2021dec.onnx"

DETECT_SCORE = 0.6          # YuNet's own confidence to report a face at all
VISIBLE_SCORE = 0.8         # ... and to judge it (known or unknown); between the two, the face is "not_visible"
MIN_FACE_PX = 40            # a face narrower than this in the original frame is too small to judge
MAX_TURN = 0.75             # nose offset from the eyes' midpoint, over the eye distance: beyond it, too turned to judge
MATCH_THRESHOLD = 0.40      # cosine to a template at or above which a face is that person (THRESHOLD_NOTE)
UNKNOWN_BELOW = 0.25        # ... below which (to every template) it is "unknown"; in between, not sure: "not_visible"
DIVERSE_COS = 0.92          # enrolment: a view this close to a kept one adds nothing
THRESHOLD_NOTE = """
Measured on 19 Nov 2026 on the lab take video/public/takes/scene2/face-take.mp4 (kit camera, 2304 x 1296), one frame
every 0.5 s, faces found by YuNet inside a box around each person, compared with Filipe's 8 templates (from his 7 s
face video) and one template each for Joao and Alice (one photo each). Faces judged: YuNet score >= 0.8, width >= 40 px,
turn <= 0.75 (the gates above).
  Filipe: 45 faces found, 21 judged (40-86 px), all named Filipe: cosine 0.323 to 0.639, median 0.489. The other 24
    were too small, unclear or turned ("not_visible"). Re-checked on the frames 0.05 s and 0.1 s around each judged
    one: 1 "unknown" (0.278) in about 100 looks.
  The other man in the take, not enrolled: 40 faces found, 10 judged, all "unknown": best cosine to anyone at most
    0.248 (0.271 on the neighbouring frames).
  A woman seated in the booth, not enrolled: her faces are 29-34 px and in profile, so none is judged; when they were
  (before the 40 px gate) they reached 0.38 against Filipe, which is why the size gate exists.
OpenCV's 0.363 is set for sharp, close-up faces (LFW). The kit camera's faces are 40-80 px and are enlarged about 2x
into SFace's 112 px input, which lowers the cosine between two pictures of the same person; other people stay low.
At 0.363, 2 of Filipe's 21 judged faces would be called unknown; at 0.30 none is, and the highest stranger score
(0.248) is still 0.05 below. This is one take with two people walking through: a check, not a measured accuracy. The
rule on the server adds its own safety: it alarms only after several consecutive "unknown" faces and never while a
family member is recognised.
Revised the same night, after replaying the whole take through the edge (video/tools/proof_run.py face): faces looked
for in looser person boxes are judged more often, and one of the other man's faces then scored 0.33 against Filipe,
while some of Filipe's own judged faces score 0.31-0.36. On this camera the two overlap between about 0.30 and 0.36.
So the answer has three zones: at or above 0.40 (MATCH_THRESHOLD) the person; below 0.25 (UNKNOWN_BELOW, every
template) "unknown"; in between, not sure, answered as "not_visible" (why: "not sure"), which can neither raise nor
silence an alarm. Filipe's median (0.489) stays known; every other-man face measured here (at most 0.248) stays unknown.
"""


def _unit(v):
    v = np.asarray(v, dtype=np.float32).reshape(-1)
    n = float(np.linalg.norm(v))
    return v / n if n else v


def turn_of(row):
    """How far the face is turned: the nose's horizontal offset from the eyes' midpoint, over the eye distance.
    0 is frontal; about 0.5 and more is a profile. YuNet's landmarks: right eye, left eye, nose, mouth corners."""
    rx, ry, lx, ly, nx = (float(v) for v in row[4:9])
    eye = float(np.hypot(lx - rx, ly - ry)) or 1.0
    return abs(nx - (rx + lx) / 2) / eye


class Faces:
    """YuNet and SFace, loaded once. Thread-safe: one call at a time (the detector's input size is state)."""

    def __init__(self, models_dir=MODELS):
        models_dir = Path(models_dir)
        for f in (YUNET, SFACE):
            if not (models_dir / f).exists():
                raise FileNotFoundError(f"{models_dir / f} is missing: download it from opencv_zoo (see faces.py)")
        self.det = cv2.FaceDetectorYN.create(str(models_dir / YUNET), "", (320, 320), DETECT_SCORE, 0.3, 50)
        self.rec = cv2.FaceRecognizerSF.create(str(models_dir / SFACE), "")
        self.lock = threading.Lock()

    # ------------------------------------------------------------------ detection
    def detect(self, bgr, min_score=DETECT_SCORE):
        """YuNet rows for the whole picture, in its pixels: x, y, w, h, 5 landmarks (10 numbers), score."""
        h, w = bgr.shape[:2]
        with self.lock:
            self.det.setScoreThreshold(float(min_score))
            self.det.setInputSize((w, h))
            _, rows = self.det.detect(bgr)
        return [] if rows is None else [r.astype(np.float32) for r in rows]

    def feature(self, bgr, row):
        """The 128-number SFace vector of one detected face, L2-normalised, and its aligned 112 x 112 crop."""
        with self.lock:
            aligned = self.rec.alignCrop(bgr, row)
            f = self.rec.feature(aligned)
        return _unit(f), aligned

    def in_box(self, bgr, box, pad=0.1, min_score=DETECT_SCORE, target=640):
        """The faces inside a person box [x0, y0, x1, y1] (pixels of bgr): the box, grown by `pad`, is cropped and
        enlarged so its longer side is about `target` px (never shrunk), YuNet runs on it, and each face is aligned
        and embedded on that enlarged crop. Returns [(row in full-frame pixels, feature, aligned crop)], best first."""
        H, W = bgr.shape[:2]
        x0, y0, x1, y1 = [float(v) for v in box]
        bw, bh = x1 - x0, y1 - y0
        x0, y0 = int(max(0, x0 - bw * pad)), int(max(0, y0 - bh * pad))
        x1, y1 = int(min(W, x1 + bw * pad)), int(min(H, y1 + bh * pad))
        if x1 - x0 < 8 or y1 - y0 < 8:
            return []
        crop = bgr[y0:y1, x0:x1]
        k = max(1.0, target / max(crop.shape[:2]))
        big = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC) if k > 1 else crop
        out = []
        for row in self.detect(big, min_score):
            f, aligned = self.feature(big, row)
            full = row.copy()
            full[:14] = full[:14] / k
            full[0] += x0                    # x, y of the box; [2], [3] are its width and height
            full[1] += y0
            full[4:14:2] += x0               # the 5 landmarks
            full[5:14:2] += y0
            out.append((full, f, aligned))
        out.sort(key=lambda r: -float(r[0][14]))
        return out

    # ------------------------------------------------------------------ recognition
    @staticmethod
    def identify(feature, templates, threshold=None):
        """(name or None, best cosine, cosine per name): the best-matching person, if at or above the threshold."""
        threshold = MATCH_THRESHOLD if threshold is None else threshold
        f = _unit(feature)
        scores = {name: float(np.max(np.asarray(t, dtype=np.float32) @ f)) for name, t in templates.items() if len(t)}
        if not scores:
            return None, None, {}
        name = max(scores, key=scores.get)
        return (name if scores[name] >= threshold else None), scores[name], scores

    def look(self, bgr, person_box, templates, threshold=None):
        """Who this person is, from their face: {"identity": name | "unknown" | "not_visible", "score", "face_box",
        "turn", "scores", "face_score", "why"}. A face is judged only when YuNet finds it in the box at VISIBLE_SCORE or
        more, at least MIN_FACE_PX wide in the frame and turned at most MAX_TURN; otherwise the answer is
        "not_visible" (with "why"), never "unknown"."""
        faces = self.in_box(bgr, person_box)
        if not faces:
            return {"identity": "not_visible", "score": None, "face_box": None, "turn": None, "scores": {},
                    "face_score": None, "why": "no face"}
        row, f, _ = faces[0]
        fb = [round(float(row[0]), 1), round(float(row[1]), 1), round(float(row[0] + row[2]), 1), round(float(row[1] + row[3]), 1)]
        turn = round(turn_of(row), 3)
        name, best, scores = self.identify(f, templates, threshold)
        out = {"face_box": fb, "turn": turn, "score": None if best is None else round(best, 3),
               "scores": {k: round(v, 3) for k, v in scores.items()}, "face_score": round(float(row[14]), 3), "why": ""}
        why = ("unclear" if row[14] < VISIBLE_SCORE else "too small" if row[2] < MIN_FACE_PX
               else "turned away" if turn > MAX_TURN else "")
        if why:
            return {**out, "identity": "not_visible", "why": why}
        if best is None:
            return {**out, "identity": "unknown", "why": "no templates"}
        if name:
            return {**out, "identity": name}
        if best >= UNKNOWN_BELOW:                        # between the zones: not sure, never a verdict
            return {**out, "identity": "not_visible", "why": "not sure"}
        return {**out, "identity": "unknown"}

    # ------------------------------------------------------------------ enrolment
    def _best_face(self, bgr, min_score=0.8):
        rows = self.detect(bgr, min_score)
        if not rows:
            return None
        return max(rows, key=lambda r: float(r[2] * r[3]))

    def enrol_frames(self, frames, n=8, min_px=60):
        """Up to n diverse face vectors from a list of BGR pictures: the largest clear face of each (YuNet 0.8 or more,
        at least min_px wide), then farthest-point selection: start with the most frontal view, then keep adding the
        view least like those kept, while it differs (cosine below DIVERSE_COS from every kept view).
        Returns (vectors, aligned crops as JPEG bytes)."""
        cands = []
        for bgr in frames:
            row = self._best_face(bgr)
            if row is None or row[2] < min_px:
                continue
            f, aligned = self.feature(bgr, row)
            cands.append((turn_of(row), f, aligned))
        if not cands:
            return [], []
        cands.sort(key=lambda c: c[0])
        kept = [cands[0]]
        rest = cands[1:]
        while rest and len(kept) < n:
            K = np.stack([k[1] for k in kept])
            sims = [float(np.max(K @ c[1])) for c in rest]
            i = int(np.argmin(sims))
            if sims[i] >= DIVERSE_COS:
                break
            kept.append(rest.pop(i))
        jpgs = [cv2.imencode(".jpg", k[2], [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tobytes() for k in kept]
        return [k[1] for k in kept], jpgs

    def enrol_video(self, path, n=8, every_s=0.1):
        """Up to n diverse face vectors from a short video of one face (frames sampled every `every_s` seconds)."""
        cap = cv2.VideoCapture(str(path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps * every_s)))
        frames, i = [], 0
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            if i % step == 0:
                frames.append(bgr)
            i += 1
        cap.release()
        return self.enrol_frames(frames, n)

    def enrol_image(self, path):
        """The face in one photo (the largest), as one vector."""
        bgr = cv2.imread(str(path))
        if bgr is None:
            raise ValueError(f"not an image: {path}")
        return self.enrol_frames([bgr], n=1, min_px=40)


# ---------------------------------------------------------------------- the home device's own store of templates
class Templates:
    """face_templates in the home device's own SQLite file (prototype/data/edge.db by default): the family's face
    vectors stay on the device. One row per vector."""

    SCHEMA = ("CREATE TABLE IF NOT EXISTS face_templates (person_id TEXT NOT NULL, idx INTEGER NOT NULL, "
              "vector TEXT NOT NULL, source TEXT, created REAL, PRIMARY KEY (person_id, idx))")

    def __init__(self, db_path=None):
        self.path = Path(db_path or DATA / "edge.db")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute(self.SCHEMA)
        self.db.commit()

    def set(self, person_id, vectors, source=""):
        with self.lock, self.db:
            self.db.execute("DELETE FROM face_templates WHERE person_id = ?", (person_id,))
            self.db.executemany("INSERT INTO face_templates VALUES (?, ?, ?, ?, ?)",
                                [(person_id, i, json.dumps([round(float(x), 6) for x in _unit(v)]), source, time.time())
                                 for i, v in enumerate(vectors)])

    def delete(self, person_id):
        with self.lock, self.db:
            self.db.execute("DELETE FROM face_templates WHERE person_id = ?", (person_id,))

    def all(self):
        with self.lock:
            rows = self.db.execute("SELECT person_id, vector FROM face_templates ORDER BY person_id, idx").fetchall()
        out = {}
        for pid, vec in rows:
            out.setdefault(pid, []).append(json.loads(vec))
        return {pid: np.asarray(v, dtype=np.float32) for pid, v in out.items()}

    def people(self):
        with self.lock:
            return {pid: n for pid, n in self.db.execute(
                "SELECT person_id, COUNT(*) FROM face_templates GROUP BY person_id").fetchall()}


def frame_at(video, t):
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, float(t) * 1000)
    ok, bgr = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f"no frame at {t} s in {video}")
    return bgr


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("enrol-video", "enrol-image"):
        p = sub.add_parser(name)
        p.add_argument("--person", required=True)
        p.add_argument("--video" if name == "enrol-video" else "--image", required=True, nargs="+" if name == "enrol-image" else None)
        p.add_argument("--db")
        p.add_argument("--crops-out", help="folder for the aligned face crops (JPEG)")
        p.add_argument("--prefix", help="crop file names: <prefix>-face<i>.jpg (default: the person's id)")
    p = sub.add_parser("look")
    p.add_argument("--video", required=True)
    p.add_argument("--t", type=float, required=True)
    p.add_argument("--box", type=float, nargs=4, required=True, metavar=("X0", "Y0", "X1", "Y1"))
    p.add_argument("--db")
    p.add_argument("--threshold", type=float)
    a = ap.parse_args(argv)

    faces, tpl = Faces(), Templates(a.db)
    if a.cmd == "look":
        res = faces.look(frame_at(a.video, a.t), a.box, tpl.all(), a.threshold)
        print(json.dumps(res))
        return
    if a.cmd == "enrol-video":
        vecs, jpgs = faces.enrol_video(a.video)
        source = f"video {Path(a.video).name}"
    else:
        vecs, jpgs = [], []
        for img in a.image:
            v, j = faces.enrol_image(img)
            vecs += v
            jpgs += j
        source = "photos " + ", ".join(Path(i).name for i in a.image)
    if not vecs:
        print(json.dumps({"person": a.person, "n": 0, "error": "no clear face found"}))
        sys.exit(1)
    tpl.set(a.person, vecs, source)
    if a.crops_out:
        out = Path(a.crops_out)
        out.mkdir(parents=True, exist_ok=True)
        names = [f"{a.prefix or a.person}-face{i}.jpg" for i in range(len(jpgs))]
        for name, j in zip(names, jpgs):
            (out / name).write_bytes(j)
    print(json.dumps({"person": a.person, "n": len(vecs), "source": source, "db": str(tpl.path),
                      "crops": names if a.crops_out else []}))


if __name__ == "__main__":
    main()
