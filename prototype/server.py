"""ThingTracker prototype server.

    prototype/.venv-llm/bin/python prototype/llm_local.py     # local text model on :8766 (Qwen3-1.7B, offline, 0 USD)
    prototype/.venv/bin/python prototype/server.py            # http://127.0.0.1:8765, no Claude: the assistant uses the
                                                               #   local model when it answers, else keyword templates
    TT_LLM=off ... server.py                                   # templates only, even when the local model is running
    TT_AI=1 ... server.py                                      # real Claude calls (costs money; capped by TT_BUDGET_USD)
    TT_AI=1 TT_LLM=local ... server.py                         # Claude for the camera, the local model for the assistant
    TT_LIVE_ACTIONS=1 ... server.py                            # really switch the Light and Plug through the MCP
    TT_BUDGET_USD=5 ...                                        # raise the spending cap (default 3.00 USD)

Reads ANTHROPIC_API_KEY and CAMERA_RTSP_URL from the repo's .env; neither is ever sent to the browser.
"""
import base64
import os
import subprocess
import threading
import time
from pathlib import Path

import anthropic
import uvicorn
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load_env(keys):
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            k = k.strip()
            if k in keys and not os.environ.get(k):
                os.environ[k] = v.strip().strip('"').strip("'")


load_env({"ANTHROPIC_API_KEY", "CAMERA_RTSP_URL"})

import actions  # noqa: E402  (after the environment is loaded)
from brain import Brain, BudgetExceeded  # noqa: E402
from kitcam import KitCamera  # noqa: E402
from store import CROPS, Store  # noqa: E402

store = Store()
brain = Brain(store)
app = FastAPI(title="ThingTracker prototype")


@app.middleware("http")
async def no_cache_for_the_page(request, call_next):
    """The page changes often while we build it: never let the browser keep an old copy."""
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/web/"):
        response.headers["Cache-Control"] = "no-store"
    return response
MIN_OBSERVE_GAP = 2.5  # seconds; protects the budget even if the page misbehaves
_last_observe = {"t": 0.0}
_obs_lock = threading.Lock()


def _llm(fn, *args):
    try:
        return fn(*args)
    except BudgetExceeded as e:
        raise HTTPException(402, str(e))
    except anthropic.APIStatusError as e:
        raise HTTPException(502, f"Claude API error {e.status_code}: {e.message}"[:300])
    except anthropic.APIConnectionError:
        raise HTTPException(502, "No connection to the Claude API")


def fire(rule, crop=None, evidence=""):
    result = actions.run(rule["action"])
    store.update_rule(rule["id"], last_fired=time.time(), fired_today=True)
    return store.add_event("alert", rule["message"], rule_id=rule["id"], title=rule["title"], action=result,
                           crop=crop, evidence=evidence)


def roll_day(rule):
    today = time.strftime("%Y-%m-%d")
    if rule.get("day") != today:
        store.update_rule(rule["id"], day=today, fired_today=False, seen_trigger_today=False)
        rule.update(day=today, fired_today=False, seen_trigger_today=False)


def deadline_passed(rule):
    try:
        hh, mm = (int(x) for x in rule.get("deadline", "").split(":"))
    except ValueError:
        return False
    t = time.localtime()
    return (t.tm_hour, t.tm_min) >= (hh, mm)


def deadline_ticker():
    """Fires 'not_by_deadline' sensors even when the camera sends nothing new."""
    while True:
        for r in store.active_rules():
            if r.get("mode") == "not_by_deadline":
                roll_day(r)
                if deadline_passed(r) and not r.get("seen_trigger_today") and not r.get("fired_today"):
                    fire(r, evidence=f"Nothing seen by {r['deadline']}.")
        time.sleep(30)


threading.Thread(target=deadline_ticker, daemon=True).start()



# ---------------------------------------------------------------------- edge service (prototype/edge.py)
EDGE = {"state": "offline", "checked": 0, "analysed": 0, "last_motion": 0.0, "last_person": 0.0, "updated": 0.0, "ms": None}
_last_crop = {}


def edge_online():
    return time.time() - EDGE["updated"] < 15


@app.post("/api/edge/status")
def edge_status(payload: dict = Body(...)):
    for k in ("state", "checked", "analysed", "last_motion", "change"):
        if k in payload:
            EDGE[k] = payload[k]
    EDGE["updated"] = time.time()
    return {"ok": True}


@app.post("/api/edge/observe")
def edge_observe(payload: dict = Body(...)):
    """What the edge saw: thing, place, a small crop of the thing, and how many people. Never the full frame."""
    now_ = time.time()
    EDGE["updated"], EDGE["ms"] = now_, payload.get("ms")
    if int(payload.get("people", 0)) > 0:
        EDGE["last_person"] = now_
    known = {t["id"]: t["name"] for t in store.things()}
    last = {t["id"]: t.get("last_seen") for t in store.snapshot()["things"]}
    for sgt in payload.get("sightings", [])[:12]:
        tid = sgt.get("thing_id")
        if tid not in known:
            continue
        place = "".join(ch for ch in str(sgt.get("place", "room")).lower() if ch.isalpha() or ch == " ")[:24] or "room"
        zone = {"id": "place-" + place, "name": place}
        prev = last.get(tid)
        moved = not prev or prev.get("zone_id") != zone["id"] or now_ - prev["ts"] > 600
        crop = None
        if sgt.get("crop_b64") and (moved or now_ - _last_crop.get(tid, 0) > 60):
            crop = f"{time.strftime('%Y%m%d-%H%M%S')}-{tid}.jpg"
            (CROPS / crop).write_bytes(base64.b64decode(sgt["crop_b64"]))
            _last_crop[tid] = now_
        elif prev:
            crop = prev.get("crop")
        store.add_observation(tid, zone, str(sgt.get("note", ""))[:60], crop)
        if moved:
            store.add_event("seen", f"{known[tid]} seen " + ("in the room." if place == "room" else f"on the {place}."), thing_id=tid, crop=crop)
    if "boxes" in payload:
        EDGE["boxes"], EDGE["boxes_at"] = payload["boxes"][:30], now_
    for kind, score in (payload.get("profile") or {}).items():
        suggest_for_profile(kind, score)
    return {"ok": True}


# ---------------------------------------------------------------------- visual registration (fingerprints)
# The edge keeps its own copy of each fingerprint; this file stands in for the copy in the Altice platform's
# database, associated with the customer, so a new or reset home device can get it back.
ENROL = {}
ENROL_VIEWS, ENROL_SECONDS = 8, 40


@app.post("/api/things/{tid}/enrol")
def start_enrol(tid: str):
    t = next((t for t in store.things() if t["id"] == tid), None)
    if not t:
        raise HTTPException(404, "unknown thing")
    if not edge_online():
        raise HTTPException(409, "The camera service is not running")
    ENROL.clear()
    ENROL.update(thing_id=tid, name=t["name"], query=(t.get("description") or t["name"]).lower(),
                 until=time.time() + ENROL_SECONDS, got=0, target=ENROL_VIEWS)
    store.add_event("thing", f"Registering {t['name']}: show it to the camera and turn it slowly.", thing_id=tid)
    return ENROL


@app.get("/api/edge/task")
def edge_task():
    if ENROL and time.time() > ENROL["until"]:
        store.add_event("thing", f"Registration of {ENROL['name']} stopped: the camera did not see it well enough.")
        ENROL.clear()
    return {"enrol": dict(ENROL) or None}


@app.post("/api/edge/enrol")
def edge_enrol(payload: dict = Body(...)):
    """Progress while the edge collects views, then the finished fingerprint (vectors and a few crops)."""
    tid = payload.get("thing_id")
    if not ENROL or ENROL.get("thing_id") != tid:
        return {"ok": False}
    ENROL["got"] = int(payload.get("got", ENROL["got"]))
    if not payload.get("done"):
        return {"ok": True}
    stamp = time.strftime("%Y%m%d-%H%M%S")
    names = []
    for i, b64 in enumerate(payload.get("crops_b64", [])[:ENROL_VIEWS]):
        names.append(f"{stamp}-{tid}-view{i}.jpg")
        (CROPS / names[-1]).write_bytes(base64.b64decode(b64))
    store.set_fingerprint(tid, {"n": len(payload.get("vectors", [])), "crops": names, "created": time.time(),
                                "model": payload.get("model", "")},
                          vectors=payload.get("vectors", []), model=payload.get("model", ""))
    store.add_event("thing", f"{ENROL['name']} registered: a visual fingerprint from {len(names)} views.",
                    thing_id=tid, crop=names[0] if names else None)
    ENROL.clear()
    return {"ok": True}


@app.get("/api/edge/fingerprints")
def edge_fingerprints():
    """Lets the home device restore its fingerprints from the platform copy."""
    return store.fingerprints()


@app.delete("/api/things/{tid}/fingerprint")
def delete_fingerprint(tid: str):
    store.set_fingerprint(tid, None)
    return {"ok": True}


@app.get("/api/edge/boxes")
def edge_boxes():
    return {"boxes": EDGE.get("boxes", []), "age": time.time() - EDGE.get("boxes_at", 0), "enrol": dict(ENROL) or None,
            "state": EDGE["state"], "online": edge_online()}


# ---------------------------------------------------------------------- suggestions from the home's profile
PROFILE_SUGGESTIONS = {
    "child": ("Children at home", "Tell me if the children are doing something wrong, something that could hurt them, or acting strangely."),
    "dog": ("A dog at home", "Tell me if the dog has not drunk water by 6 pm."),
    "cat": ("A cat at home", "Tell me if the cat has not drunk water by 6 pm."),
}


_profile_hits = {}


def suggest_for_profile(kind, score):
    """Suggest a sensor only after the camera has seen a child or a pet clearly, in 3 analyses within 10 minutes."""
    if kind not in PROFILE_SUGGESTIONS or float(score) < 0.45:
        return
    now_ = time.time()
    hits = [t for t in _profile_hits.get(kind, []) if now_ - t < 600] + [now_]
    _profile_hits[kind] = hits
    if kind in store.suggested() or len(hits) < 3:
        return
    store.mark_suggested(kind)
    title, sentence = PROFILE_SUGGESTIONS[kind]
    store.add_event("suggest", f"{title}. Suggested sensor: “{sentence}”", title=title, sentence=sentence)


def _stay_start(thing_id, place):
    """When the thing's current stay in this place began (sightings less than 5 min apart), or None."""
    start, prev_ts = None, None
    for o in reversed(store.observations(thing_id)):
        if o["thing_id"] != thing_id:
            continue
        if o["zone_name"] != place or (prev_ts and prev_ts - o["ts"] > 300):
            break
        start, prev_ts = o["ts"], o["ts"]
    return start


def rules_engine():
    """Evaluates the local rules every 2 s against the memory and the edge's presence signals."""
    while True:
        now_ = time.time()
        for r in store.active_rules():
            if r.get("engine") != "local" or now_ - r.get("last_fired", 0) < r.get("cooldown_s", 300):
                continue
            kind, mins = r.get("kind"), float(r.get("minutes") or 0)
            try:
                if kind == "left_for":
                    last = store.last_seen(r.get("thing_id"))
                    place = r.get("place") or (last or {}).get("zone_name")
                    if last and last["zone_name"] == place and now_ - last["ts"] < 120:
                        start = _stay_start(r["thing_id"], place)
                        if start and now_ - start >= mins * 60:
                            fire(r, crop=last.get("crop"), evidence=f"On the {place} for {int((now_ - start) // 60)} min.")
                elif kind == "nobody_for" and edge_online():
                    quiet = now_ - max(EDGE["last_motion"], EDGE["last_person"], r.get("armed_at", 0))
                    if quiet >= mins * 60:
                        fire(r, evidence=f"No movement for {int(quiet // 60)} min.")
                        store.update_rule(r["id"], armed_at=now_)
                elif kind == "someone_arrives" and edge_online():
                    lp = EDGE["last_person"]
                    if lp > r.get("seen_person", 0) and lp - r.get("seen_person", 0) > max(mins, 5) * 60:
                        if r.get("seen_person"):
                            fire(r, evidence="Someone arrived after the room was empty.")
                        store.update_rule(r["id"], seen_person=lp)
                    elif lp > r.get("seen_person", 0):
                        store.update_rule(r["id"], seen_person=lp)
                elif kind == "seen_in":
                    last = store.last_seen(r.get("thing_id"))
                    if last and now_ - last["ts"] < 10 and (not r.get("place") or last["zone_name"] == r["place"]):
                        fire(r, crop=last.get("crop"), evidence=f"Seen on the {last['zone_name']}.")
            except Exception as e:  # one bad rule must not stop the engine
                print("rule error", r.get("id"), e)
        time.sleep(2)


threading.Thread(target=rules_engine, daemon=True).start()

# ---------------------------------------------------------------------- API
@app.get("/api/state")
def state():
    s = store.snapshot()
    s["settings"] = {"live_actions": actions.LIVE, "ai": brain.enabled, "llm": brain.text_mode(), "budget_usd": brain.cap,
                     "kit_camera": bool(os.environ.get("CAMERA_RTSP_URL"))}
    s["edge"] = {k: v for k, v in EDGE.items() if k != "boxes"} | {"online": edge_online()}
    s["enrol"] = dict(ENROL) or None
    return s


@app.get("/api/devices")
def devices():
    """The home as the Altice app shows it, from the local database (a copy of the platform's home, rooms, devices)."""
    return store.home()


def _status(d):
    """A device's status line, written as the Altice app writes it."""
    caps = {c.get("name"): c.get("value") for c in d.get("capabilities", []) if isinstance(c, dict)}
    online = str(d.get("operStatus", "")).lower() not in ("offline", "disconnected")
    if not online:
        return "Disconnected"
    t = d.get("type")
    if t == "contactSensor":
        return "Open" if caps.get("sensorState") == "alarm" else "Closed"
    if t == "plug":
        return f"{float(caps.get('instantPower') or 0):.1f} W".replace(".", ",")
    if t == "temperatureSensor":
        return f"{caps.get('temperatureValue')} °C | {caps.get('humidityValue')} %"
    return "On"


def sync_from_platform():
    """When the MCP session is live, refresh the device statuses in the local database (read-only tool)."""
    res = actions.devices()
    if res.get("source") == "live":
        devs = res["data"].get("devices", [])
        store.sync_devices([{"id": d["id"], "status": _status(d)} for d in devs],
                           f"Synced from the Altice platform at {time.strftime('%H:%M')}")


threading.Thread(target=sync_from_platform, daemon=True).start()


@app.get("/api/things/{tid}/sightings")
def thing_sightings(tid: str):
    """The home's memory for one thing: where and when the camera saw it, oldest first."""
    return {"sightings": store.observations(tid, limit=50)}


@app.delete("/api/things/{tid}")
def delete_thing(tid: str):
    store.delete_thing(tid)
    return {"ok": True}


@app.put("/api/zones")
def put_zones(zones: list = Body(...)):
    clean = [{"id": str(z["id"]), "name": str(z["name"])[:40], **{k: max(0.0, min(1.0, float(z[k]))) for k in ("x", "y", "w", "h")}}
             for z in zones][:6]
    store.set_zones(clean)
    return {"zones": clean}


@app.post("/api/things")
def add_thing(payload: dict = Body(...)):
    name = str(payload.get("name", "")).strip()[:40]
    if not name:
        raise HTTPException(400, "name is required")
    tid = store.add_thing(name, str(payload.get("description", ""))[:120])
    store.add_event("thing", f"Now tracking: {name}.")
    return {"id": tid}


@app.post("/api/observe")
def observe(payload: dict = Body(...)):
    if not brain.enabled:  # AI off: nothing is analysed or stored, so no rate limit is needed
        return {"result": {"zones": [], "not_analysed": True}, "fired": [], "ai": False, "spend": store.snapshot()["spend"]}
    with _obs_lock:
        if time.time() - _last_observe["t"] < MIN_OBSERVE_GAP:
            raise HTTPException(429, "Too soon: one observation every 2.5 s at most")
        _last_observe["t"] = time.time()
    zones = {z["id"]: z for z in store.zones()}
    crops = [c for c in payload.get("crops", []) if c.get("zone_id") in zones][:4]
    if not crops:
        raise HTTPException(400, "no crops for known zones")
    for c in crops:
        c["zone_name"] = zones[c["zone_id"]]["name"]
    things = store.things()
    sensors = [r for r in store.active_rules() if r["zone_id"] in {c["zone_id"] for c in crops}]
    result = _llm(brain.observe, crops, things, [{"id": r["id"], "zone_id": r["zone_id"], "question": r["question"]} for r in sensors])
    if result.get("not_analysed"):
        return {"result": result, "fired": [], "ai": False, "spend": store.snapshot()["spend"]}

    # keep the crops (only the chosen zones ever reach the server)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    crop_names = {}
    for c in crops:
        name = f"{stamp}-{c['zone_id']}.jpg"
        (CROPS / name).write_bytes(base64.b64decode(c["jpeg_b64"]))
        crop_names[c["zone_id"]] = name

    by_name = {t["id"]: t["name"] for t in things}
    last = {t["id"]: t.get("last_seen") for t in store.snapshot()["things"]}
    fired = []
    for z in result.get("zones", []):
        zone = zones.get(z.get("zone_id"))
        if not zone:
            continue
        for t in z.get("things", []):
            if t.get("visible") and t.get("thing_id") in by_name:
                prev = last.get(t["thing_id"])
                store.add_observation(t["thing_id"], zone, t.get("where", ""), crop_names.get(zone["id"]))
                moved = not prev or prev.get("zone_id") != zone["id"] or time.time() - prev["ts"] > 600
                if moved:
                    where = t.get("where", "")
                    tail = f" {where}" if where.startswith("(") else (f", {where}" if where else "")
                    store.add_event("seen", f"{by_name[t['thing_id']]} seen on the {zone['name'].lower()}{tail}.",
                                    thing_id=t["thing_id"], crop=crop_names.get(zone["id"]))
        for s in z.get("sensors", []):
            rule = next((r for r in sensors if r["id"] == s.get("sensor_id")), None)
            if not rule:
                continue
            roll_day(rule)
            hit = s.get("answer") == rule["trigger_when"]
            if rule.get("mode") == "not_by_deadline":
                if hit and not rule.get("seen_trigger_today"):
                    store.update_rule(rule["id"], seen_trigger_today=True)
                    store.add_event("ok", f"{rule['title']}: confirmed.", rule_id=rule["id"], crop=crop_names.get(zone["id"]))
            elif hit and time.time() - rule.get("last_fired", 0) > rule.get("cooldown_s", 300):
                fired.append(fire(rule, crop=crop_names.get(zone["id"]), evidence=s.get("evidence", "")))
    return {"result": result, "fired": fired, "spend": store.snapshot()["spend"]}


@app.post("/api/ask")
def ask(payload: dict = Body(...)):
    q = str(payload.get("question", "")).strip()[:300]
    if not q:
        raise HTTPException(400, "question is required")
    out = _llm(brain.ask, q, store.memory_for_llm())
    things = {t["id"]: t for t in store.snapshot()["things"]}
    thing = things.get(out.get("thing_id"))
    crop = thing["last_seen"].get("crop") if thing and thing.get("last_seen") else None
    store.add_event("ask", f"\"{q}\": {out['answer']}", crop=crop)
    return {**out, "crop": crop, "thing": thing, "candidates": [things[c] for c in out.get("candidates", []) if c in things]}


RULE_WORDS = ("tell me", "notify", "alert me", "warn me", "let me know", "remind me", "turn ", "switch ", "when ",
              "avisa", "lembra", "notifica", "liga ", "desliga", "quando ")


@app.post("/api/assistant")
def assistant(payload: dict = Body(...)):
    """The app's assistant button: a question gets an answer from the home's memory; a sentence that asks to be
    told or to act becomes a sensor. Both go through the ThingTracker service, the only caller of the language model."""
    text = str(payload.get("text", "")).strip()[:300]
    if not text:
        raise HTTPException(400, "text is required")
    low = text.lower()
    if any(w in low for w in RULE_WORDS) and not low.rstrip().endswith("?"):
        return {"kind": "sensor", "sensor": add_rule({"sentence": text})}
    return {"kind": "answer", **ask({"question": text})}


@app.post("/api/rules")
def add_rule(payload: dict = Body(...)):
    """A sentence becomes a local rule: the language model (or, with AI off, a template) compiles it once;
    the rules engine then evaluates it on the camera's sightings, at no cost per check."""
    sentence = str(payload.get("sentence", "")).strip()[:300]
    if not sentence:
        raise HTTPException(400, "sentence is required")
    compiled = _llm(brain.compile_local, sentence, store.things())
    compiled.update(engine="local", zone_id="", cooldown_s=max(60, min(3600, int(compiled.get("cooldown_s", 300)))))
    rule = store.add_rule(sentence, compiled)
    store.add_event("sensor", f"New sensor: {rule['title']}.", rule_id=rule["id"])
    return rule


@app.patch("/api/rules/{rid}")
def patch_rule(rid: str, payload: dict = Body(...)):
    r = store.update_rule(rid, active=bool(payload.get("active")))
    if not r:
        raise HTTPException(404, "no such sensor")
    return r


@app.post("/api/reset")
def reset():
    store.reset()
    return {"ok": True}


kit = KitCamera(os.environ["CAMERA_RTSP_URL"]) if os.environ.get("CAMERA_RTSP_URL") else None


def _kit():
    if not kit:
        raise HTTPException(404, "CAMERA_RTSP_URL is not set in .env")
    return kit


@app.get("/api/kit/frame.jpg")
def kit_frame():
    """The newest frame from the persistent connection: instant once the stream is open."""
    frame = _kit().latest()
    if not frame:
        raise HTTPException(504, "The kit camera stream did not answer in 12 s")
    return Response(frame, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@app.get("/api/kit/stream.mjpg")
def kit_stream():
    """Live view for an <img>: every new frame, as multipart MJPEG. No plugin, no VLC."""
    cam = _kit()

    def parts():
        for frame in cam.frames_forever():
            yield b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(frame)).encode() + b"\r\n\r\n" + frame + b"\r\n"

    return StreamingResponse(parts(), media_type="multipart/x-mixed-replace; boundary=frame",
                             headers={"Cache-Control": "no-store"})


@app.get("/api/kit/status")
def kit_status():
    return _kit().status()


app.mount("/crops", StaticFiles(directory=CROPS), name="crops")
app.mount("/web", StaticFiles(directory=HERE / "web"), name="web")


@app.get("/")
def index():
    return FileResponse(HERE / "web" / "index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("TT_PORT", "8765")))
