"""ThingTracker edge service: the part that runs in the home.

    prototype/.venv-vision/bin/python prototype/edge.py            # needs the server running (python prototype/server.py)

It reads the kit camera through the server, and stays idle while nothing changes: a cheap motion check on a
small grey picture runs twice a second. Only when something moves does it run the open-source detector (OWLv2)
on the things the home tracks, the places they live and people. It sends the server what it saw (thing, place,
time and a small crop of the thing), never the full frame. The rules are evaluated by the server's rules engine.
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


def crop_b64(img, box, pad=0.25, size=200):
    w, h = box[2] - box[0], box[3] - box[1]
    x0, y0 = max(0, box[0] - w * pad), max(0, box[1] - h * pad)
    x1, y1 = min(img.width, box[2] + w * pad), min(img.height, box[3] + h * pad)
    c = img.crop((x0, y0, x1, y1))
    c.thumbnail((size, size))
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=82)
    return base64.b64encode(buf.getvalue()).decode()


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
    post(f"{args.server}/api/edge/observe", {"people": 0, "sightings": [], "boxes": boxes})
    return np.asarray(enrol["vecs"], dtype=np.float32) if done else None


def analyse(img, things, fps, det, emb, args):
    """Find the tracked things, the places they rest on, people, and who lives here. Returns the payload for the server."""
    tq = {query_for(t): t for t in things if t["id"] in fps}   # only what the user added and registered
    queries = list(tq) + list(PLACES.values()) + [PERSON] + list(PROFILE.values())
    dets = det(img, queries, threshold=0.1)
    places = [(k, b) for q, s, b in dets for k, v in PLACES.items() if q == v and s >= 0.18]
    people = [(s, b) for q, s, b in dets if q == PERSON and s >= 0.2]
    boxes = [{"box": norm_box(img, b), "label": "Person", "kind": "person", "score": round(s, 2)} for s, b in people[:6]]
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
        label = f"{t['name']} · yours {sim:.2f}"
        boxes.append({"box": norm_box(img, b), "label": label, "kind": "thing", "score": round(sim or s, 2)})
        out.append({"thing_id": t["id"], "score": round(s, 2), "place": place, "crop_b64": crop_b64(img, b), "note": note})
    return {"people": len(people), "sightings": out, "boxes": boxes, "profile": profile}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8765")
    ap.add_argument("--check-every", type=float, default=0.5, help="seconds between motion checks")
    ap.add_argument("--analyse-every", type=float, default=1.0, help="minimum seconds between two analyses")
    ap.add_argument("--active-for", type=float, default=6.0, help="seconds to keep analysing after the last motion")
    ap.add_argument("--match", type=float, default=0.62, help="cosine similarity to a registered view to count as yours")
    args = ap.parse_args()

    print("loading OWLv2 and DINOv2…", flush=True)
    det = Detector()
    emb = Embedder(det.dev)
    fps = load_fingerprints(args.server)
    save_local(fps)
    print(f"ready on {det.dev}; {len(fps)} registered things", flush=True)
    motion = Motion()
    checked = analysed = 0
    active_until = last_analysis = last_status = last_motion = 0.0
    things, things_at, enrol = [], 0.0, {}
    frac = 0.0

    while True:
        t0 = time.time()
        try:
            img = Image.open(io.BytesIO(get(f"{args.server}/api/kit/frame.jpg"))).convert("RGB")
            task = json.loads(get(f"{args.server}/api/edge/task"))["enrol"]
        except Exception as e:  # camera or server not ready: keep trying, quietly
            print("no frame:", e, flush=True)
            time.sleep(2)
            continue
        checked += 1
        moved, frac = motion.changed(img)
        if moved:
            active_until, last_motion = t0 + args.active_for, t0
        state = "registering" if task else "active" if t0 < active_until else "idle"

        try:
            if task:
                done = enrol_step(img, task, det, emb, enrol, args)
                analysed += 1
                if done is not None:
                    fps[task["thing_id"]] = done
                    save_local(fps)
                    print(f"registered {task['name']}: {len(done)} views", flush=True)
                    enrol.clear()
            elif state == "active" and t0 - last_analysis >= args.analyse_every:
                if t0 - things_at > 10:                   # the things to track can change from the app
                    things = json.loads(get(f"{args.server}/api/state"))["things"]
                    things_at = t0
                    fps = {tid: v for tid, v in fps.items() if any(t["id"] == tid for t in things)}
                    for t in things:                      # a fingerprint deleted in the app is deleted here too
                        if not t.get("fingerprint"):
                            fps.pop(t["id"], None)
                t1 = time.time()
                payload = analyse(img, things, fps, det, emb, args)
                ms = (time.time() - t1) * 1000
                payload["ms"] = round(ms)
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
