"""ThingTracker prototype server.

    prototype/.venv/bin/python prototype/server.py            # http://127.0.0.1:8765, AI OFF: simulated answers, 0 USD
    TT_AI=1 ... server.py                                      # real Claude calls (costs money; capped by TT_BUDGET_USD)
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
from fastapi.responses import FileResponse, Response
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
from store import CROPS, Store  # noqa: E402

store = Store()
brain = Brain(store)
app = FastAPI(title="ThingTracker prototype")
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


# ---------------------------------------------------------------------- API
@app.get("/api/state")
def state():
    s = store.snapshot()
    s["settings"] = {"live_actions": actions.LIVE, "ai": brain.enabled, "budget_usd": brain.cap, "kit_camera": bool(os.environ.get("CAMERA_RTSP_URL"))}
    return s


@app.get("/api/devices")
def devices():
    return actions.devices()


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
                    store.add_event("seen", f"{by_name[t['thing_id']]} seen on the {zone['name'].lower()}, {t.get('where', '')}.",
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
    thing = next((t for t in store.snapshot()["things"] if t["id"] == out.get("thing_id")), None)
    crop = thing["last_seen"].get("crop") if thing and thing.get("last_seen") else None
    store.add_event("ask", f"\"{q}\": {out['answer']}", crop=crop)
    return {**out, "crop": crop}


@app.post("/api/rules")
def add_rule(payload: dict = Body(...)):
    sentence = str(payload.get("sentence", "")).strip()[:300]
    if not sentence:
        raise HTTPException(400, "sentence is required")
    zones = store.zones()
    compiled = _llm(brain.compile, sentence, zones, store.things())
    if compiled["zone_id"] not in {z["id"] for z in zones}:
        compiled["zone_id"] = zones[0]["id"]
    if compiled.get("new_thing"):
        store.add_thing(compiled["new_thing"])
    compiled["cooldown_s"] = max(60, min(3600, int(compiled.get("cooldown_s", 300))))
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


@app.get("/api/kit/frame.jpg")
def kit_frame():
    url = os.environ.get("CAMERA_RTSP_URL")
    if not url:
        raise HTTPException(404, "CAMERA_RTSP_URL is not set in .env")
    try:
        p = subprocess.run(["ffmpeg", "-loglevel", "error", "-rtsp_transport", "tcp", "-i", url, "-frames:v", "1",
                            "-vf", "scale=1280:-2", "-f", "image2", "-vcodec", "mjpeg", "pipe:1"],
                           capture_output=True, timeout=12)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "The kit camera stream did not answer in 12 s")
    if p.returncode != 0 or not p.stdout:
        raise HTTPException(502, "The kit camera stream returned no frame")
    return Response(p.stdout, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


app.mount("/crops", StaticFiles(directory=CROPS), name="crops")
app.mount("/web", StaticFiles(directory=HERE / "web"), name="web")


@app.get("/")
def index():
    return FileResponse(HERE / "web" / "index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("TT_PORT", "8765")))
