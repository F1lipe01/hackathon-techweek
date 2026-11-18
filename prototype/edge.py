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
import urllib.request

import numpy as np
import torch
from PIL import Image, ImageFilter
from transformers import Owlv2ForObjectDetection, Owlv2Processor

PLACES = {"desk": "a desk", "table": "a table", "shelf": "a shelf", "sofa": "a sofa", "bench": "a workbench"}
PERSON = "a person"


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://127.0.0.1:8765")
    ap.add_argument("--check-every", type=float, default=0.5, help="seconds between motion checks")
    ap.add_argument("--analyse-every", type=float, default=1.0, help="minimum seconds between two analyses")
    ap.add_argument("--active-for", type=float, default=6.0, help="seconds to keep analysing after the last motion")
    args = ap.parse_args()

    print("loading OWLv2…", flush=True)
    det = Detector()
    print(f"ready on {det.dev}", flush=True)
    motion = Motion()
    checked = analysed = 0
    active_until = last_analysis = last_status = last_motion = 0.0
    things = []
    things_at = 0.0

    while True:
        t0 = time.time()
        try:
            img = Image.open(io.BytesIO(get(f"{args.server}/api/kit/frame.jpg"))).convert("RGB")
        except Exception as e:  # camera or server not ready: keep trying, quietly
            print("no frame:", e, flush=True)
            time.sleep(2)
            continue
        checked += 1
        moved, frac = motion.changed(img)
        if moved:
            active_until, last_motion = t0 + args.active_for, t0
        state = "active" if t0 < active_until else "idle"

        if state == "active" and t0 - last_analysis >= args.analyse_every:
            if t0 - things_at > 10:                       # the things to track can change from the app
                things = json.loads(get(f"{args.server}/api/state"))["things"]
                things_at = t0
            tq = {f"a photo of {t.get('description') or t['name']}": t["id"] for t in things}
            queries = list(tq) + list(PLACES.values()) + [PERSON]
            t1 = time.time()
            dets = det(img, queries)
            ms = (time.time() - t1) * 1000
            analysed += 1
            last_analysis = t0
            places = [(k, b) for q, s, b in dets for k, v in PLACES.items() if q == v and s >= 0.18]
            people = sum(1 for q, s, b in dets if q == PERSON and s >= 0.18)
            best = {}
            for q, s, b in dets:
                if q in tq and s >= 0.25 and (tq[q] not in best or s > best[tq[q]][0]):
                    best[tq[q]] = (s, b)
            sightings = [{"thing_id": tid, "score": round(s, 2), "place": place_of(b, places), "crop_b64": crop_b64(img, b)}
                         for tid, (s, b) in best.items()]
            try:
                post(f"{args.server}/api/edge/observe", {"people": people, "sightings": sightings, "ms": round(ms)})
            except Exception as e:
                print("post failed:", e, flush=True)
            print(f"analysed in {ms:.0f} ms: {len(sightings)} things, {people} people, places {[p for p, _ in places]}", flush=True)

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
