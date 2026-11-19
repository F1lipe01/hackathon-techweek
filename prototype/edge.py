"""ThingTracker edge service: the part that runs in the home.

    prototype/.venv-vision/bin/python prototype/edge.py            # needs the server running (python prototype/server.py)

It reads the kit camera through the server, and stays idle while nothing changes: a cheap motion check on a
small grey picture runs twice a second. Only when something moves does it run the open-source detector (OWLv2)
on the things the home tracks, the places they live and people. It sends the server what it saw (thing, place,
time and a small crop of the thing; who is there, a person, a child, a dog or a cat, and where, without any picture of
them), never the full frame. The rules are evaluated by the server's rules engine.

Besides motion, the server can ask (GET /api/edge/task) for:
  refresh   an analysis now, without motion: the presence state rests on the cameras alone (someone sitting still)
  check     an active check of one thing over a few frames (left behind: is the book still on the desk?)
  photos    a fingerprint from the phone photos: OWLv2 finds the thing in each photo, DINOv2 makes the vectors
  snapshot  one picture of the room for an alert, sent only when no person is in view

Faces (opt-in, on this device only): when prototype/faces.py and its models are present, each person box is checked
for a face (YuNet) and the face compared with the family's templates (SFace) in this device's own database
(data/edge.db, never sent to the server). The server receives only the result: a registered person's id, "unknown"
(a face that matches nobody; with a crop of that person, which the server keeps only if a security rule fires) or
"not_visible". A thing whose box sits on a person's box is sent "in_hand", with who holds it when the face is known.
"""
import argparse
import base64
import io
import json
import time
from pathlib import Path
import urllib.request

import numpy as np
import torch
from PIL import Image, ImageFilter
from transformers import AutoImageProcessor, AutoModel, Owlv2ForObjectDetection, Owlv2Processor

PLACES = {"desk": "a desk", "table": "a table", "shelf": "a shelf", "sofa": "a sofa", "bench": "a workbench"}
PERSON = "a person"
PROFILE = {"child": "a child", "dog": "a dog", "cat": "a cat"}   # who lives here: the app suggests sensors for them
LOCAL_FP = Path(__file__).resolve().parent / "data" / "edge-fingerprints.json"   # the home device's own copy
EDGE_DB = Path(__file__).resolve().parent / "data" / "edge.db"   # the home device's face templates (faces.py)
ENROL_VIEWS = 8


def get(url, timeout=15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read() or b"{}")


class Motion:
    """Cheap change detector: 160 x 90 grey picture, the camera's clock overlay masked, against a slow background."""

    def __init__(self, pixel_delta=22, area=0.006):
        self.bg = None
        self.pixel_delta, self.area = pixel_delta, area

    def changed(self, img):
        g = np.asarray(img.convert("L").resize((160, 90)).filter(ImageFilter.BoxBlur(1)), dtype=np.float32)
        g[:12, :80] = 0                                   # the date/time overlay changes every second
        if self.bg is None:
            self.bg = g
            return False, 0.0
        diff = np.abs(g - self.bg) > self.pixel_delta
        frac = float(diff.mean())
        self.bg = 0.85 * self.bg + 0.15 * g               # adapts to slow light changes
        return frac > self.area, frac


class Detector:
    def __init__(self):
        self.dev = "mps" if torch.backends.mps.is_available() else "cpu"
        self.proc = Owlv2Processor.from_pretrained("google/owlv2-base-patch16-ensemble")
        self.model = Owlv2ForObjectDetection.from_pretrained("google/owlv2-base-patch16-ensemble").to(self.dev).eval()

    def __call__(self, img, queries, threshold=0.16):
        inputs = self.proc(text=[queries], images=img, return_tensors="pt").to(self.dev)
        with torch.no_grad():
            out = self.model(**inputs)
        res = self.proc.post_process_grounded_object_detection(
            outputs=out, threshold=threshold, target_sizes=torch.tensor([img.size[::-1]]).to(self.dev))[0]
        return [(queries[l], float(s), [float(v) for v in b]) for s, l, b in zip(res["scores"], res["labels"], res["boxes"])]


class Embedder:
    """DINOv2 small: one 384-number vector per crop. Close vectors mean the same object, seen again."""
    MODEL = "facebook/dinov2-small"

    def __init__(self, dev):
        self.dev = dev
        self.proc = AutoImageProcessor.from_pretrained(self.MODEL)
        self.model = AutoModel.from_pretrained(self.MODEL).to(dev).eval()

    def __call__(self, crops):
        inputs = self.proc(images=crops, return_tensors="pt").to(self.dev)
        with torch.no_grad():
            v = self.model(**inputs).pooler_output
        return torch.nn.functional.normalize(v, dim=-1).cpu().numpy()


def tight_crop(img, box, pad=0.08):
    w, h = box[2] - box[0], box[3] - box[1]
    return img.crop((max(0, box[0] - w * pad), max(0, box[1] - h * pad),
                     min(img.width, box[2] + w * pad), min(img.height, box[3] + h * pad)))


def norm_box(img, b):
    return [round(b[0] / img.width, 4), round(b[1] / img.height, 4), round(b[2] / img.width, 4), round(b[3] / img.height, 4)]


def query_for(t):
    return f"a photo of {(t.get('description') or t['name']).lower()}"


def load_fingerprints(server):
    """The device's own copy first; if it has none (new or reset device), restore it from the platform's copy."""
    try:
        fps = json.loads(LOCAL_FP.read_text())
    except Exception:
        fps = {}
    try:
        for tid, fp in json.loads(get(f"{server}/api/edge/fingerprints")).items():
            fps.setdefault(tid, fp)
    except Exception:
        pass
    return {tid: np.asarray(fp["vectors"], dtype=np.float32) for tid, fp in fps.items() if fp.get("vectors")}


def save_local(fps):
    LOCAL_FP.parent.mkdir(exist_ok=True)
    LOCAL_FP.write_text(json.dumps({tid: {"model": Embedder.MODEL, "vectors": v.round(5).tolist()} for tid, v in fps.items()}))


def place_of(box, places):
    """The place whose box holds the thing's bottom-centre point; the smallest such place wins."""
    cx, cy = (box[0] + box[2]) / 2, box[3]
    best = None
    for name, pb in places:
        if pb[0] <= cx <= pb[2] and pb[1] - 20 <= cy <= pb[3] + 20:
            area = (pb[2] - pb[0]) * (pb[3] - pb[1])
            if best is None or area < best[1]:
                best = (name, area)
    return best[0] if best else "room"


def overlaps(a, b, pad=0.15):
    """Do two boxes touch, the second grown by `pad` of its size on each side (a dog's head over its bowl)?"""
    w, h = (b[2] - b[0]) * pad, (b[3] - b[1]) * pad
    return a[0] < b[2] + w and a[2] > b[0] - w and a[1] < b[3] + h and a[3] > b[1] - h


def crop_b64(img, box, pad=0.25, size=200):
    w, h = box[2] - box[0], box[3] - box[1]
    x0, y0 = max(0, box[0] - w * pad), max(0, box[1] - h * pad)
    x1, y1 = min(img.width, box[2] + w * pad), min(img.height, box[3] + h * pad)
    c = img.crop((x0, y0, x1, y1))
    c.thumbnail((size, size))
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=82)
    return base64.b64encode(buf.getvalue()).decode()


def iou(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def in_hand(thing_box, person_box, min_iou=0.02):
    """Is the thing held: its centre inside the person's box, or the two boxes overlapping a little (a small IoU)?"""
    cx, cy = (thing_box[0] + thing_box[2]) / 2, (thing_box[1] + thing_box[3]) / 2
    inside = person_box[0] <= cx <= person_box[2] and person_box[1] <= cy <= person_box[3]
    return inside or iou(thing_box, person_box) >= min_iou


class FaceID:
    """The optional face step (prototype/faces.py: YuNet + SFace through OpenCV). Absent models or cv2: every person
    is "not_visible" and nothing else changes. Templates are re-read from the device's database every 10 s."""

    def __init__(self, db_path):
        self.ok, self.templates, self.read_at, self.db_path = False, {}, 0.0, db_path
        try:
            import faces as F                       # noqa: PLC0415  (optional: needs cv2 and the ONNX models)
            self.F, self.faces, self.store = F, F.Faces(), F.Templates(db_path)
            self.threshold = F.MATCH_THRESHOLD     # 0.30: measured on the lab take (faces.THRESHOLD_NOTE)
            self.ok = True
        except Exception as e:  # noqa: BLE001
            print("faces off:", e, flush=True)

    def look(self, img, box):
        if not self.ok:
            return {"identity": "not_visible", "score": None, "face_box": None}
        if time.time() - self.read_at > 10:
            self.templates, self.read_at = self.store.all(), time.time()
        bgr = np.asarray(img)[:, :, ::-1].copy()
        try:
            return self.faces.look(bgr, box, self.templates, self.threshold)
        except Exception as e:  # noqa: BLE001 - one bad crop must not stop the analysis
            print("face step failed:", e, flush=True)
            return {"identity": "not_visible", "score": None, "face_box": None}


def enrol_step(img, task, det, emb, enrol, args):
    """One registration step: find the named object (usually held close to the camera) and keep a new view of it."""
    tid = task["thing_id"]
    if enrol.get("tid") != tid:
        enrol.clear()
        enrol.update(tid=tid, vecs=[], crops=[])
    dets = det(img, [f"a photo of {task['query']}"], threshold=0.06)
    boxes = []
    if dets:
        q, s, b = max(dets, key=lambda d: d[1])
        big_enough = (b[2] - b[0]) * (b[3] - b[1]) > 0.002 * img.width * img.height
        if big_enough:
            v = emb([tight_crop(img, b)])[0]
            if all(float(v @ u) < 0.97 for u in enrol["vecs"]):      # a new angle, not the same view again
                enrol["vecs"].append(v)
                enrol["crops"].append(crop_b64(img, b, pad=0.15, size=240))
            boxes.append({"box": norm_box(img, b), "label": f"Registering {task['name']} · view {len(enrol['vecs'])} of {ENROL_VIEWS}",
                          "kind": "enrol", "score": round(s, 2)})
    done = len(enrol["vecs"]) >= ENROL_VIEWS
    payload = {"thing_id": tid, "got": len(enrol["vecs"]), "done": done}
    if done:
        payload.update(vectors=[v.round(5).tolist() for v in enrol["vecs"]], crops_b64=enrol["crops"], model=Embedder.MODEL)
    post(f"{args.server}/api/edge/enrol", payload)
    post(f"{args.server}/api/edge/observe", {"sightings": [], "boxes": boxes, "enrol": True})
    return np.asarray(enrol["vecs"], dtype=np.float32) if done else None


def analyse(img, things, fps, det, emb, args, faceid=None):
    """Find the tracked things, the places they rest on, people (and who each is, when the face is known), and who
    lives here. Returns the payload for the server."""
    tq = {query_for(t): t for t in things if t["id"] in fps}   # only what the user added and registered
    queries = list(tq) + list(PLACES.values()) + [PERSON] + list(PROFILE.values())
    dets = det(img, queries, threshold=0.1)
    places = [(k, b) for q, s, b in dets for k, v in PLACES.items() if q == v and s >= 0.18]
    people = [(s, b) for q, s, b in dets if q == PERSON and s >= 0.2]
    names = {t["id"]: t["name"] for t in things}
    persons, boxes = [], []
    for s, b in people[:6]:
        face = faceid.look(img, b) if faceid else {"identity": "not_visible", "score": None}
        who = face["identity"]
        p = {"box": norm_box(img, b), "identity": who, "score": face.get("score")}
        if who == "unknown":                              # only a face that matches nobody: kept if a rule fires
            p["crop_b64"] = crop_b64(img, b, pad=0.15, size=360)
        persons.append(p)
        label = (f"{names.get(who, who)} · face {face['score']:.2f}" if who not in ("unknown", "not_visible")
                 else f"Unknown face {face['score']:.2f}" if who == "unknown" else "Person")
        boxes.append({"box": norm_box(img, b), "label": label, "kind": "person", "score": round(s, 2)})
    profile = {k: max((s for q, s, b in dets if q == v), default=0.0) for k, v in PROFILE.items()}
    for k, v in PROFILE.items():
        for q, s, b in dets:
            if q == v and s >= 0.45:
                boxes.append({"box": norm_box(img, b), "label": k.capitalize(), "kind": "profile", "score": round(s, 2)})
    sightings = []
    for q, t in tq.items():
        cands = sorted([(s, b) for qq, s, b in dets if qq == q], key=lambda c: -c[0])[:4]
        if not cands:
            continue
        fp = fps[t["id"]]
        vecs = emb([tight_crop(img, b) for s, b in cands])
        sims = (vecs @ fp.T).max(axis=1)                  # closest registered view, for each candidate
        for (s, b), sim in zip(cands, sims):
            if sim >= args.match:
                sightings.append((t, s, b, f"recognised as yours ({sim:.2f})", float(sim)))
                break
            if s >= 0.25:                                 # clearly that kind of object, but not this one
                boxes.append({"box": norm_box(img, b), "label": f"A {t['name'].lower()}, not yours ({sim:.2f})",
                              "kind": "other", "score": round(float(sim), 2)})
    out = []
    for t, s, b, note, sim in sightings:
        place = place_of(b, places)
        holder = next((i for i, (ps, pb) in enumerate(people[:6]) if in_hand(b, pb)), None)
        label = f"{t['name']} · yours {sim:.2f}" + (" · in hand" if holder is not None else "")
        boxes.append({"box": norm_box(img, b), "label": label, "kind": "thing", "score": round(sim or s, 2)})
        o = {"thing_id": t["id"], "score": round(s, 2), "place": place, "crop_b64": crop_b64(img, b), "note": note}
        if holder is not None:
            who = persons[holder]["identity"]
            o.update(in_hand=True, by=who if who not in ("unknown", "not_visible") else None)
        out.append(o)
    # who is there, and where: at a registered thing it touches (the dog at its bowl), else on the surface under it.
    # No crop: the server keeps who, place and time only.
    seen_things = [(t["name"], b) for t, s, b, note, sim in sightings]
    where = lambda box: next((n for n, tb in seen_things if overlaps(box, tb)), None) or place_of(box, places)
    beings = [{"who": "person", "place": where(b)} for s, b in people[:6]]
    beings += [{"who": k, "place": where(b)} for k, v in PROFILE.items() for q, s, b in dets if q == v and s >= 0.45]
    return {"people": len(people), "persons": persons, "sightings": out, "boxes": boxes, "profile": profile,
            "beings": beings}


def best_match(img, thing, fp, det, emb, threshold):
    """The thing in this image: (similarity, box) of the best candidate that is the user's own, else (best, None)."""
    dets = det(img, [query_for(thing)], threshold=0.08)
    cands = sorted([(s, b) for q, s, b in dets], key=lambda c: -c[0])[:4]
    if not cands:
        return 0.0, None
    sims = (emb([tight_crop(img, b) for s, b in cands]) @ fp.T).max(axis=1)
    i = int(np.argmax(sims))
    return float(sims[i]), (cands[i][1] if sims[i] >= threshold else None)


def active_check(server, task, things, fps, det, emb, args, frames=3):
    """Is the thing still here? A few new frames, whatever the motion; the best sighting wins. Returns the answer
    for POST /api/edge/check, with a crop of the thing and its surroundings when it is seen."""
    t = next((x for x in things if x["id"] == task["thing_id"]), None)
    fp = fps.get(task["thing_id"])
    if not t or fp is None:
        return {"id": task["id"], "seen": False, "frames": 0, "note": "no fingerprint on this device"}
    best = (0.0, None, None)
    for i in range(int(task.get("frames") or frames)):
        img = Image.open(io.BytesIO(get(f"{server}/api/kit/frame.jpg"))).convert("RGB")
        sim, box = best_match(img, t, fp, det, emb, args.match)
        if box is not None and sim > best[0]:
            best = (sim, box, img)
        time.sleep(0.4)
    sim, box, img = best
    if box is None:
        return {"id": task["id"], "seen": False, "frames": frames, "score": round(sim, 2)}
    dets = det(img, list(PLACES.values()), threshold=0.18)
    places = [(k, b) for q, s, b in dets for k, v in PLACES.items() if q == v]
    return {"id": task["id"], "seen": True, "frames": frames, "score": round(sim, 2), "place": place_of(box, places),
            "crop_b64": crop_b64(img, box, pad=1.2, size=640)}


def photo_fingerprint(images, query, det, emb):
    """Phone photos of a thing -> (vectors, crops): OWLv2 finds it in each photo (its description is the query; the
    biggest confident box), DINOv2 makes a vector of each crop. A photo where it is not found is used whole (a close-up
    fills the frame). Returns also how many photos had a box."""
    vecs, crops, found = [], [], 0
    for img in images:
        img = img.convert("RGB")
        img.thumbnail((1280, 1280))
        dets = [d for d in det(img, [f"a photo of {query}"], threshold=0.08)]
        if dets:
            s, b = max(((s, b) for q, s, b in dets), key=lambda c: c[0] * ((c[1][2] - c[1][0]) * (c[1][3] - c[1][1])) ** 0.25)
            crop, found = tight_crop(img, b), found + 1
        else:
            crop = img
        vecs.append(emb([crop])[0])
        buf = io.BytesIO()
        c = crop.copy()
        c.thumbnail((240, 240))
        c.save(buf, "JPEG", quality=85)
        crops.append(base64.b64encode(buf.getvalue()).decode())
    return np.asarray(vecs, dtype=np.float32), crops, found


def run_photos(server, task, det, emb):
    imgs = [Image.open(io.BytesIO(get(f"{server}/crops/{urllib.request.quote(f)}"))) for f in task["files"]]
    vecs, crops, found = photo_fingerprint(imgs, task["query"], det, emb)
    post(f"{server}/api/edge/enrol", {"thing_id": task["thing_id"], "source": "photos", "done": True, "found": found,
                                      "vectors": [v.round(5).tolist() for v in vecs], "crops_b64": crops,
                                      "model": Embedder.MODEL})
    return vecs


def run_snapshot(server, task, img, det):
    """A picture of the room for an alert, only when the detector sees no person in it."""
    person = any(s >= 0.2 for q, s, b in det(img, [PERSON], threshold=0.15))
    payload = {"id": task["id"], "person": person}
    if not person:
        c = img.copy()
        c.thumbnail((960, 960))
        buf = io.BytesIO()
        c.save(buf, "JPEG", quality=80)
        payload["jpeg_b64"] = base64.b64encode(buf.getvalue()).decode()
    post(f"{server}/api/edge/snapshot", payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8765")
    ap.add_argument("--check-every", type=float, default=0.5, help="seconds between motion checks")
    ap.add_argument("--analyse-every", type=float, default=1.0, help="minimum seconds between two analyses")
    ap.add_argument("--active-for", type=float, default=6.0, help="seconds to keep analysing after the last motion")
    ap.add_argument("--match", type=float, default=0.62, help="cosine similarity to a registered view to count as yours")
    ap.add_argument("--no-faces", action="store_true", help="never look for faces (every person is 'not_visible')")
    args = ap.parse_args()

    print("loading OWLv2 and DINOv2…", flush=True)
    det = Detector()
    emb = Embedder(det.dev)
    fps = load_fingerprints(args.server)
    save_local(fps)
    faceid = FaceID(EDGE_DB) if not args.no_faces else None
    print(f"ready on {det.dev}; {len(fps)} registered things; faces {'on' if faceid and faceid.ok else 'off'}", flush=True)
    motion = Motion()
    checked = analysed = 0
    active_until = last_analysis = last_status = last_motion = 0.0
    things, things_at, enrol = [], 0.0, {}
    frac = 0.0

    while True:
        t0 = time.time()
        try:
            img = Image.open(io.BytesIO(get(f"{args.server}/api/kit/frame.jpg"))).convert("RGB")
            tasks = json.loads(get(f"{args.server}/api/edge/task"))
            task = tasks["enrol"]
        except Exception as e:  # camera or server not ready: keep trying, quietly
            print("no frame:", e, flush=True)
            time.sleep(2)
            continue
        checked += 1
        moved, frac = motion.changed(img)
        if moved:
            active_until, last_motion = t0 + args.active_for, t0
        forced = bool(tasks.get("refresh")) and not task
        state = "registering" if task else "active" if t0 < active_until or forced else "idle"

        try:
            if tasks.get("photos") and not task:
                p = tasks["photos"]
                fps[p["thing_id"]] = run_photos(args.server, p, det, emb)
                save_local(fps)
                print(f"fingerprint of {p['name']} from {len(p['files'])} photos", flush=True)
            if tasks.get("check") and not task:
                if t0 - things_at > 10:
                    things, things_at = json.loads(get(f"{args.server}/api/state"))["things"], t0
                res = active_check(args.server, tasks["check"], things, fps, det, emb, args)
                post(f"{args.server}/api/edge/check", res)
                print(f"active check of {tasks['check']['name']}: {'seen' if res['seen'] else 'not seen'}", flush=True)
            if tasks.get("snapshot") and not task:
                run_snapshot(args.server, tasks["snapshot"], img, det)
            if task:
                done = enrol_step(img, task, det, emb, enrol, args)
                analysed += 1
                if done is not None:
                    fps[task["thing_id"]] = done
                    save_local(fps)
                    print(f"registered {task['name']}: {len(done)} views", flush=True)
                    enrol.clear()
            elif state == "active" and t0 - last_analysis >= args.analyse_every:   # motion, or a refresh asked
                if t0 - things_at > 10:                   # the things to track can change from the app
                    things = json.loads(get(f"{args.server}/api/state"))["things"]
                    things_at = t0
                    fps = {tid: v for tid, v in fps.items() if any(t["id"] == tid for t in things)}
                    for t in things:                      # a fingerprint deleted in the app is deleted here too
                        if not t.get("fingerprint"):
                            fps.pop(t["id"], None)
                t1 = time.time()
                payload = analyse(img, things, fps, det, emb, args, faceid)
                ms = (time.time() - t1) * 1000
                payload["ms"], payload["forced"] = round(ms), forced and not moved
                analysed += 1
                last_analysis = t0
                post(f"{args.server}/api/edge/observe", payload)
                found = ", ".join(f"{s['thing_id']}@{s['place']}" for s in payload["sightings"]) or "no things"
                print(f"analysed in {ms:.0f} ms: {found}, {payload['people']} people", flush=True)
        except Exception as e:
            print("analysis failed:", e, flush=True)

        if t0 - last_status > 2:
            try:
                post(f"{args.server}/api/edge/status", {"state": state, "checked": checked, "analysed": analysed,
                                                        "last_motion": last_motion, "change": round(frac, 4)})
            except Exception:
                pass
            last_status = t0
        time.sleep(max(0.0, args.check_every - (time.time() - t0)))


if __name__ == "__main__":
    main()
