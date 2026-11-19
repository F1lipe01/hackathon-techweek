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
import json
import os
import re
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
from brain import BEINGS, Brain, BudgetExceeded, hhmm, place_matches  # noqa: E402
from kitcam import KitCamera  # noqa: E402
from presence import EMPTY, LEAVING, Presence, join  # noqa: E402
from store import CROPS, DATA, Store  # noqa: E402

store = Store()
brain = Brain(store)
presence = Presence(store)
T = presence.t                  # the named timings (presence.TIMINGS): demo seconds, or production minutes
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


# The devices the power-saving rule can turn off, as ThingTracker sees them (data/tt_devices.json, ThingTracker's own
# data, never written to the Altice platform):
# - the kit's real Plug, with what it powers: in the lab, the ceiling lights hang on it. The link is ThingTracker's.
#   Switching it goes through actions.run("plug_off"/"plug_on"): a dry run unless TT_LIVE_ACTIONS=1 (never set); the
#   state the app shows after a dry run is ThingTracker's own.
# - an Air conditioner connected to the app directly, as a third-party integration: not part of the Altice kit, and
#   simulated in this prototype (its state lives here; nothing is sent to it).
TT_FILE = Path(__file__).resolve().parent / "data" / "tt_devices.json"
TT_DEFAULT = {"powers": {"plug": "Ceiling lights"}, "state": {},
              "integrations": [{"id": "ac", "name": "Air conditioner", "type": "ac", "room": "Work Room", "on": True,
                                "via": "Third-party integration"}]}


def _tt():
    try:
        return json.loads(TT_FILE.read_text())
    except (OSError, ValueError):
        return json.loads(json.dumps(TT_DEFAULT))


def tt_devices():
    """The kit's plugs (with what each powers) and the app's integrations, with the on/off state the app shows."""
    d, out = _tt(), []
    rooms = {r["id"]: r["name"] for r in store.home().get("rooms", [])}
    for x in store.home().get("devices", []):
        if x["type"] != "plug":
            continue
        powers = d["powers"].get(x["id"]) or d["powers"].get("plug", "")
        on = d["state"].get(x["id"], str(x.get("status", "")).strip().lower() not in ("off", "disconnected"))
        out.append({"id": x["id"], "name": x["name"], "type": "plug", "room": rooms.get(x.get("room_id"), ""), "on": bool(on),
                    "powers": powers, "kit": True})
    for x in d["integrations"]:
        out.append({**x, "on": bool(d["state"].get(x["id"], x["on"])), "kit": False})
    return out


def tt_set(did, on):
    d = _tt()
    d["state"][did] = bool(on)
    TT_FILE.write_text(json.dumps(d))


# ---------------------------------------------------------------------- alerts and the (simulated) alarm
# An alert is an event of kind "alert" with a structured payload the app draws as its notification and alert screen:
#   title, text (the message), picture (a crop file: the thing, the unknown person, or the empty room), crop,
#   cards    [{"device", "name", "kind", "label", "state": "on"|"off"}]  devices the app offers to turn off ("Yes")
#   ask      [{"act": "alarm_on", "label", "state": "ask"|"done"}]       a question the app asks ("Sound the alarm?")
#   door     {"open": true, "text"}                                      the door banner
#   alarm    {"state": "on"|"off", "text", "since", "off_at"}            the simulated alarm, with "Turn off the alarm"
#   suggestion {"kind": "police", "title", "text", "number": "112"}      the app offers the call; it never dials
# Every answer goes through POST /api/alerts/{id}/act or /alarm-off -> actions.run (a dry run, or simulated for the
# alarm) -> the simulated device or alarm state -> an event. The Altice alarm is never called (AGENTS.md rule 1).
def alarm_state():
    return store.meta("alarm", {"on": False, "since": 0.0, "alert": None})


def sound_alarm(why):
    res = actions.run("alarm_on")
    store.set_meta("alarm", {"on": True, "since": time.time(), "alert": None, "why": why})
    return {"state": "on", "since": time.time(), "text": "Simulated: the alarm sounds in the app. The Altice alarm is never called.",
            "action": res}


def fire(rule, crop=None, evidence="", text=None, title=None, action=None, alarm=None, picture=None, **extra):
    """An alert for this rule: its device action (a dry run), the simulated alarm if the rule asks for it (alarm=None)
    or as given (True/False), and the structured payload."""
    result = actions.run(rule["action"] if action is None else action)
    if (rule.get("alarm") if alarm is None else alarm):
        extra["alarm"] = sound_alarm(rule["title"])
    store.update_rule(rule["id"], last_fired=time.time(), fired_today=True)
    e = store.add_event("alert", text or rule["message"], rule_id=rule["id"], title=title or rule["title"], action=result,
                        crop=crop, picture=picture or crop, evidence=evidence, **extra)
    if extra.get("alarm"):
        store.set_meta("alarm", {**alarm_state(), "alert": e["id"]})
    return e


def hm(ts):
    return time.strftime("%H:%M", time.localtime(ts))


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


def clock_today(text):
    """Today at 'HH:MM' (or 'HH:MM:SS'), as a timestamp; None if it is not a time."""
    try:
        h, m, sec = ([int(x) for x in str(text).split(":")] + [0, 0])[:3]
    except ValueError:
        return None
    t = time.localtime()
    return time.mktime((t.tm_year, t.tm_mon, t.tm_mday, h, m, sec, 0, 0, -1))


def visits(who, place, since, until=None):
    """When the camera saw `who` (person, child, dog, cat, or a thing id) at `place`, oldest first. A person
    includes children. Places match as place_matches() says: 'kitchen' is 'Kitchen 1' and 'Kitchen 2'."""
    if who in BEINGS:
        rows = store.presence(["person", "child"] if who == "person" else [who], since, until)
        return [r for r in rows if place_matches(place, r["room"], r["place"])]
    return [{"ts": o["ts"], "room": o["room"], "place": o["zone_name"]} for o in store.observations(who, limit=2000)
            if o["ts"] > since and (until is None or o["ts"] <= until) and place_matches(place, o["room"], o["zone_name"])]


def stayed(rows, min_s):
    """Did one stay (sightings less than 30 s apart) last at least min_s seconds? Any sighting counts when min_s is 0."""
    if not rows:
        return False
    start = prev = rows[0]["ts"]
    for r in rows:
        if r["ts"] - prev > 30:
            start = r["ts"]
        prev = r["ts"]
        if prev - start >= float(min_s or 0):
            return True
    return False


def camera_note():
    return "" if edge_online() else " The camera service was offline at the deadline, so nothing could be seen."


WHO_TEXT = {"dog": "The dog", "cat": "The cat", "child": "A child", "person": "Someone"}


def check_deadline(r):
    """not_by: who has not been at the place by 'by' today (or, with within_s, for that long); nobody_by: no person
    at the place between 'from' and 'by' today. One alert a day at most (roll_day resets it); a rule written after
    today's deadline starts tomorrow. Data: the presence table (people, pets) and the sightings (things)."""
    now_ = time.time()
    kind, place = r["kind"], r.get("place", "")
    who = "person" if kind == "nobody_by" else r.get("who", "")
    if not who:
        return
    names = {t["id"]: t["name"] for t in store.things()}
    subject = WHO_TEXT.get(who) or names.get(who, who)
    room = any(place_matches(place, n) for n in store.camera_places())
    at = (f" in the {place}" if room else f" at the {place.lower()}") if place else " at home"
    if kind == "not_by" and r.get("within_s"):            # a rolling window: "not at the water bowl for 12 hours"
        start = r.get("armed_at") or r.get("created_at") or now_
        seen = visits(who, place, since=start)
        if stayed(seen, r.get("min_s")):
            store.update_rule(r["id"], armed_at=seen[-1]["ts"])
        elif now_ - start >= float(r["within_s"]):
            hours = (now_ - start) / 3600
            fire(r, evidence=f"{subject} was not seen{at} for " + (f"{hours:.1f} h." if hours >= 1 else
                                                               f"{int(now_ - start)} s.") + camera_note())
            store.update_rule(r["id"], armed_at=now_)
        return
    roll_day(r)
    by_ts = clock_today(r.get("by"))
    if by_ts is None or r.get("fired_today") or r.get("seen_trigger_today") or by_ts <= r.get("created_at", 0):
        return
    from_ts = clock_today(r.get("from") or "00:00") if kind == "nobody_by" else clock_today("00:00")
    seen = visits(who, place, since=from_ts, until=min(now_, by_ts))
    if stayed(seen, r.get("min_s")):
        store.update_rule(r["id"], seen_trigger_today=True)
        store.add_event("ok", f"{r['title']}: {subject.lower()} was seen{at} at {hm(seen[-1]['ts'])}, so no alert today.",
                        rule_id=r["id"])
    elif now_ >= by_ts:
        span = f"between {r.get('from')} and {r['by']}" if kind == "nobody_by" else f"by {r['by']}"
        fire(r, evidence=(f"Nobody was seen{at} {span}." if kind == "nobody_by" else f"{subject} was not seen{at} {span}.")
             + camera_note())


def deadline_ticker():
    """Fires the deadline sensors even when the camera sends nothing new: the old 'not_by_deadline' ones (cloud
    vision) and the local not_by and nobody_by."""
    while True:
        for r in store.active_rules():
            try:
                if r.get("mode") == "not_by_deadline":
                    roll_day(r)
                    if deadline_passed(r) and not r.get("seen_trigger_today") and not r.get("fired_today"):
                        fire(r, evidence=f"Nothing seen by {r['deadline']}.")
                elif r.get("kind") in ("not_by", "nobody_by"):
                    check_deadline(r)
            except Exception as e:  # one bad rule must not stop the ticker
                print("deadline error", r.get("id"), e)
        time.sleep(3)


threading.Thread(target=deadline_ticker, daemon=True).start()



# ---------------------------------------------------------------------- edge service (prototype/edge.py)
# Who is home is the presence engine's (presence.py); the edge only reports what each analysis saw.
EDGE = {"state": "offline", "checked": 0, "analysed": 0, "last_motion": 0.0, "updated": 0.0, "ms": None}
_last_crop = {}
_unknown_crop = {}      # camera -> (ts, jpeg b64) of the latest unknown face's person crop; written only if a rule fires


def edge_online():
    return time.time() - EDGE["updated"] < 15


@app.post("/api/edge/status")
def edge_status(payload: dict = Body(...)):
    for k in ("state", "checked", "analysed", "last_motion", "change"):
        if k in payload:
            EDGE[k] = payload[k]
    EDGE["updated"] = time.time()
    return {"ok": True}


def clean_place(text, n=32):
    return " ".join("".join(ch for ch in str(text or "") if ch.isalnum() or ch in " -").split())[:n]


_last_presence = {}


def record_presence(payload, camera):
    """People and pets as sightings with a place, never a picture: the data of not_by, nobody_by and the arrival
    rules. The edge sends 'beings' (who, and the surface or registered thing each is at); an older edge only sends
    the number of people and its profile scores, recorded at the camera's place. At most one row every 5 s for the
    same who and place."""
    beings = payload.get("beings")
    if beings is None:
        beings = ([{"who": "person", "place": "room"}] if int(payload.get("people", 0)) > 0 else []) + \
                 [{"who": k, "place": "room"} for k, sc in (payload.get("profile") or {}).items()
                  if k in BEINGS and float(sc or 0) >= 0.45]
    now_ = time.time()
    for b in beings[:12]:
        who = b.get("who")
        if who not in BEINGS:
            continue
        place = clean_place(b.get("place"), 24) or "room"
        if now_ - _last_presence.get((who, camera, place), 0) < 5:
            continue
        _last_presence[(who, camera, place)] = now_
        store.add_presence(who, place, camera)


def persons_of(payload):
    """The persons of one analysis, each with an identity: a registered person's id (face recognised at the edge),
    "unknown" (a face is visible and matches nobody) or "not_visible" (no face seen). An edge without the face model
    sends only a count of people: each is "not_visible"."""
    if isinstance(payload.get("persons"), list):
        return [{"identity": str(p.get("identity") or "not_visible")[:40], "score": p.get("score")}
                for p in payload["persons"][:12] if isinstance(p, dict)]
    return [{"identity": "not_visible"} for _ in range(min(12, int(payload.get("people", 0) or 0)))]


def thing_place(sgt):
    return "".join(ch for ch in str(sgt.get("place", "room")).lower() if ch.isalpha() or ch == " ")[:24] or "room"


# ---------------------------------------------------------------------- picked up, taken, moved (edge: "in_hand")
# The edge marks a sighting "in_hand" when the thing's box sits on a person's box, with "by" the person's id when their
# face was recognised. Here: "picked up by" once; then, if the thing is missing from its place for taken_misses analyses
# of that camera, "taken by"; when it is seen again somewhere else, "moved to"; back where it was, "put back".
HELD = {}       # thing id -> {"by", "camera", "place", "ts", "misses", "taken"}


def track_handling(payload, camera, known, people):
    now_, seen = time.time(), {}
    for sgt in payload.get("sightings", [])[:12]:
        if sgt.get("thing_id") in known:
            seen[sgt["thing_id"]] = sgt
    for tid, sgt in seen.items():
        h = HELD.get(tid)
        if sgt.get("in_hand"):
            who = people.get(sgt.get("by") or "", "")
            if not h:
                last = store.last_seen(tid)
                HELD[tid] = {"by": who, "camera": camera, "place": last["zone_name"] if last else thing_place(sgt),
                             "room": last["room"] if last else camera, "ts": now_, "misses": 0, "taken": False}
                store.add_event("handled", f"{known[tid]} picked up" + (f" by {who}." if who else " by a person."),
                                thing_id=tid, by=who or None, camera=camera)
            elif who and not h["by"]:
                h["by"] = who
            if h:
                h["misses"] = 0
            continue
        if h:
            place = thing_place(sgt)
            if place != h["place"] or camera != h["room"]:
                where = "the room" if place == "room" else f"the {place}"
                store.add_event("handled", f"{known[tid]} moved to {where}" + ("" if camera == store.camera_room() else f" ({camera})")
                                + (f" by {h['by']}." if h["by"] else "."), thing_id=tid, place=place, room=camera)
            elif not h["taken"]:
                store.add_event("handled", f"{known[tid]} put back on the {place}.", thing_id=tid, place=place)
            HELD.pop(tid, None)
    for tid, h in list(HELD.items()):
        if tid in seen or h["camera"] != camera or h["taken"]:
            continue
        h["misses"] += 1
        if h["misses"] >= T["taken_misses"]:
            h["taken"] = True
            store.add_event("handled", f"{known.get(tid, tid)} taken by {h['by'] or 'a person'}: not on the {h['place']} "
                            f"for {h['misses']} analyses.", thing_id=tid, by=h["by"] or None, taken=True)


@app.post("/api/edge/observe")
def edge_observe(payload: dict = Body(...)):
    """What the edge saw: thing, place, a small crop of the thing, who is there (people, pets) and where, and who each
    person is when the face was recognised. Never the full frame; a person's crop only for a face that matches nobody
    (kept only if a security rule fires). 'camera' names the camera's place (default: the kit camera's room).
    A post with "persons" or "people" is one analysis and feeds the presence engine; one with only "boxes" does not."""
    now_ = time.time()
    EDGE["updated"], EDGE["ms"] = now_, payload.get("ms")
    camera = clean_place(payload.get("camera")) or store.camera_room()
    things = store.things()
    known = {t["id"]: t["name"] for t in things}
    people = {t["id"]: t["name"] for t in things if (t.get("description") or "").startswith("person")}
    last = {t["id"]: t.get("last_seen") for t in store.snapshot()["things"]}
    for sgt in payload.get("sightings", [])[:12]:
        tid = sgt.get("thing_id")
        if tid not in known or sgt.get("in_hand"):        # in someone's hand: the memory keeps where it rests
            continue
        place = thing_place(sgt)
        zone = {"id": "place-" + place, "name": place}
        prev = last.get(tid)
        moved = (not prev or prev.get("zone_id") != zone["id"] or prev.get("room") != camera
                 or now_ - prev["ts"] > 600)
        crop = None
        if sgt.get("crop_b64") and (moved or now_ - _last_crop.get(tid, 0) > 60):
            crop = f"{time.strftime('%Y%m%d-%H%M%S')}-{tid}.jpg"
            (CROPS / crop).write_bytes(base64.b64decode(sgt["crop_b64"]))
            _last_crop[tid] = now_
        elif prev:
            crop = prev.get("crop")
        store.add_observation(tid, zone, str(sgt.get("note", ""))[:60], crop, room=camera)
        if moved:
            cam = "" if camera == store.camera_room() else f" ({camera})"
            store.add_event("seen", f"{known[tid]} seen " + ("in the room" if place == "room" else f"on the {place}")
                            + f"{cam}.", thing_id=tid, crop=crop)
    record_presence(payload, camera)
    if ("persons" in payload or "people" in payload) and not payload.get("enrol"):
        persons = persons_of(payload)
        for p in payload.get("persons") or []:
            if isinstance(p, dict) and p.get("identity") == "unknown" and p.get("crop_b64"):
                _unknown_crop[camera] = (now_, p["crop_b64"])
        presence.analysis(camera, persons, forced=bool(payload.get("forced")))
        track_handling(payload, camera, known, people)
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


# What the server asks of the edge besides registering (GET /api/edge/task):
#   refresh   analyse now even without motion: the presence state rests on the cameras alone (a person sitting still)
#   check     an active check of one thing over a few frames, regardless of motion (left behind: "is it still there?")
#   photos    make a thing's fingerprint from the phone photos: OWLv2 crops it, DINOv2 makes the vectors
#   snapshot  one picture of the room for an alert, sent only if the edge sees no person in it
CHECKS = {}             # check id -> {"thing_id", "query", "name", "frames", "asked", "result"}
SNAPSHOTS = {}          # snapshot id -> {"alert_id", "asked"}


def photo_tasks():
    return store.meta("photo_tasks", {})


@app.get("/api/edge/task")
def edge_task(camera: str = ""):
    if ENROL and time.time() > ENROL["until"]:
        store.add_event("thing", f"Registration of {ENROL['name']} stopped: the camera did not see it well enough.")
        ENROL.clear()
    cam = clean_place(camera) or store.camera_room()
    check = next(({"id": k, **{x: v[x] for x in ("thing_id", "query", "name", "frames")}} for k, v in CHECKS.items()
                  if v.get("result") is None), None)
    photos = next(iter(photo_tasks().values()), None)
    snap = next(({"id": k, "alert_id": v["alert_id"]} for k, v in SNAPSHOTS.items() if not v.get("done")), None)
    learn = next(iter(LEARN.values()), None)
    return {"enrol": dict(ENROL) or None, "refresh": presence.wants_refresh(cam), "check": check, "photos": photos,
            "snapshot": snap, "learn": learn}


# "Mark it on the camera picture": the family taps their thing on the live view; the edge learns how it looks from
# where that camera stands (a few views of the detector's box that overlaps the mark) and adds them to the fingerprint.
# Phone photos of a cover do not look like a book lying flat across a room; these views do.
LEARN = {}


@app.post("/api/things/{tid}/learn")
def learn_from_camera(tid: str, payload: dict = Body(...)):
    """{"box": [x0, y0, x1, y1]} in 0-1 of the camera picture: where the family marked the thing."""
    t = next((x for x in store.things() if x["id"] == tid), None)
    box = payload.get("box")
    if not t or not (isinstance(box, list) and len(box) == 4):
        raise HTTPException(400, "a thing and its box are required")
    LEARN[tid] = {"thing_id": tid, "name": t["name"], "query": (t.get("description") or t["name"]).lower(),
                  "box": [max(0.0, min(1.0, float(v))) for v in box], "views": 3, "replayed": bool(payload.get("replayed"))}
    src = str(payload.get("from") or "")[:60]
    store.add_event("thing", ("Replayed: " if payload.get("replayed") else "") + f"{t['name']} marked on the "
                    f"{store.camera_room()} camera's picture" + (f" (in the family's clip {src})" if src else "")
                    + ": the camera learns how it looks from there.", thing_id=tid)
    return LEARN[tid]


@app.post("/api/edge/check")
def edge_check(payload: dict = Body(...)):
    """The edge's answer to an active check: {"id", "seen", "place", "score", "frames", "crop_b64"}."""
    c = CHECKS.get(payload.get("id"))
    if not c:
        return {"ok": False}
    crop = None
    if payload.get("seen") and payload.get("crop_b64"):
        crop = f"{time.strftime('%Y%m%d-%H%M%S')}-{c['thing_id']}-check.jpg"
        (CROPS / crop).write_bytes(base64.b64decode(payload["crop_b64"]))
    c["result"] = {"seen": bool(payload.get("seen")), "place": thing_place(payload) if payload.get("seen") else "",
                   "score": payload.get("score"), "frames": payload.get("frames"), "crop": crop, "at": time.time()}
    return {"ok": True}


@app.post("/api/edge/snapshot")
def edge_snapshot(payload: dict = Body(...)):
    """A picture of the room for an alert ({"id", "jpeg_b64"}), or {"id", "person": true} when someone is in view:
    then no picture is sent at all."""
    s = SNAPSHOTS.get(payload.get("id"))
    if not s:
        return {"ok": False}
    s["done"] = True
    if payload.get("jpeg_b64") and not payload.get("person"):
        name = f"{time.strftime('%Y%m%d-%H%M%S')}-room.jpg"
        (CROPS / name).write_bytes(base64.b64decode(payload["jpeg_b64"]))
        store.update_event(s["alert_id"], picture=name)
    return {"ok": True}


def ask_snapshot(alert):
    SNAPSHOTS[f"s{int(time.time() * 1000)}"] = {"alert_id": alert["id"], "asked": time.time()}


@app.post("/api/edge/enrol")
def edge_enrol(payload: dict = Body(...)):
    """Progress while the edge collects views, then the finished fingerprint (vectors and a few crops). With
    "source": "photos", the fingerprint the edge made from the phone photos of a queued photos task."""
    tid = payload.get("thing_id")
    if payload.get("source") == "camera":
        task = LEARN.pop(tid, None)
        t = next((x for x in store.things() if x["id"] == tid), None)
        if not task or not t or not payload.get("vectors"):
            return {"ok": False}
        old_vecs = store.fingerprints().get(tid, {}).get("vectors", [])
        stamp = time.strftime("%Y%m%d-%H%M%S")
        names = []
        for i, b64 in enumerate(payload.get("crops_b64", [])[:4]):
            names.append(f"{stamp}-{tid}-camera{i}.jpg")
            (CROPS / names[-1]).write_bytes(base64.b64decode(b64))
        info = {**(t.get("fingerprint") or {}), "camera_views": len(payload["vectors"]), "created": time.time()}
        info["crops"] = (info.get("crops") or []) + names
        info["n"] = len(old_vecs) + len(payload["vectors"])
        store.set_fingerprint(tid, info, vectors=old_vecs + payload["vectors"], model=payload.get("model", ""))
        store.add_event("thing", f"{t['name']}: {len(payload['vectors'])} views learnt from the {store.camera_room()} "
                        "camera, added to its fingerprint.", thing_id=tid, crop=names[0] if names else None)
        return {"ok": True}
    if payload.get("source") == "photos":
        tasks = photo_tasks()
        task = tasks.pop(tid, None)
        if not task or not payload.get("vectors"):
            return {"ok": False}
        store.set_meta("photo_tasks", tasks)
        t = next((x for x in store.things() if x["id"] == tid), None)
        if not t:
            return {"ok": False}
        found = int(payload.get("found", len(payload["vectors"])))
        info = {**(t.get("fingerprint") or {}), "n": len(payload["vectors"]), "model": payload.get("model", ""),
                "source": "photos", "found": found, "photos": len(task["files"]), "created": time.time()}
        store.set_fingerprint(tid, info, vectors=payload["vectors"], model=payload.get("model", ""))
        store.add_event("thing", f"{t['name']}: visual fingerprint made from {len(task['files'])} photos (found in "
                        f"{found} of them).", thing_id=tid, crop=(info.get("crops") or [None])[0])
        return {"ok": True}
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


@app.post("/api/things/{tid}/photos")
def thing_photos(tid: str, payload: dict = Body(...)):
    """Registration from photos taken with the phone (or frames picked from a phone video): the photos become the
    thing's views, and a photos task is queued for the edge service, which has the vision models: OWLv2 finds the thing
    in each photo (its description is the query), DINOv2 makes a vector of each crop, and the edge posts them to
    /api/edge/enrol. The task is kept in the database until the edge runs. People are not registered here: their face
    templates are made on the home device (face-video)."""
    t = next((t for t in store.things() if t["id"] == tid), None)
    if not t:
        raise HTTPException(404, "unknown thing")
    photos = [b for b in payload.get("photos_b64", []) if isinstance(b, str)][:ENROL_VIEWS]
    if not photos:
        raise HTTPException(400, "photos_b64 is required")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    names = []
    for i, b64 in enumerate(photos):
        names.append(f"{stamp}-{tid}-photo{i}.jpg")
        (CROPS / names[-1]).write_bytes(base64.b64decode(b64.split(",", 1)[-1]))
    store.set_fingerprint(tid, {"n": len(names), "crops": names, "created": time.time(), "source": "photos", "model": "",
                                "pending": True})
    queued = not (t.get("description") or "").startswith("person")
    if not queued:                    # a person: their face templates, made on the home device from the photos
        res = enrol_face(tid, ["enrol-image", "--image", *[str(CROPS / n) for n in names]], f"{stamp}-{tid}")
        store.set_fingerprint(tid, {"n": len(names), "crops": names, "created": time.time(), "source": "photos",
                                    "model": "YuNet + SFace (opencv_zoo)" if res.get("n") else "", "faces": res.get("n", 0)})
    if queued:
        store.set_meta("photo_tasks", {**photo_tasks(), tid: {"thing_id": tid, "name": t["name"], "files": names,
                                                               "query": (t.get("description") or t["name"]).lower()}})
    store.add_event("thing", f"{t['name']} registered from {len(names)} photos." + (
        " The camera service makes its visual fingerprint." if queued else ""), thing_id=tid, crop=names[0])
    return {"ok": True, "n": len(names), "queued": queued}


# ---------------------------------------------------------------------- faces: templates on the home device
# A person's face templates are made by faces.py (YuNet + SFace, OpenCV), the home device's code, and kept in the home
# device's own database (data/edge.db), never in this server's. In the prototype both run on one machine, so the server
# starts faces.py in the vision environment and waits (about 1-2 s); in production the app would hand the video to
# the home device. The server keeps only the aligned face crops the app shows as the person's views.
VISION_PY = Path(os.environ.get("TT_VISION_PY") or HERE / ".venv-vision" / "bin" / "python")
EDGE_DB = DATA / "edge.db"


def enrol_face(tid, source_args, prefix):
    """faces.py enrol-video / enrol-image for one person: {"n", "crops", ...} or {"n": 0, "error"}."""
    if not VISION_PY.exists():
        return {"n": 0, "error": "the vision environment (prototype/.venv-vision) is missing"}
    try:
        out = subprocess.run([str(VISION_PY), "-I", str(HERE / "faces.py"), *source_args, "--person", tid,
                              "--db", str(EDGE_DB), "--crops-out", str(CROPS), "--prefix", prefix],
                             capture_output=True, text=True, timeout=120, env={**os.environ, "TT_DATA": str(DATA)})
        lines = out.stdout.strip().splitlines()
        return json.loads(lines[-1]) if lines else {"n": 0, "error": out.stderr.strip()[-200:]}
    except (subprocess.TimeoutExpired, ValueError, OSError) as e:
        return {"n": 0, "error": str(e)[:200]}


def forget_face(tid):
    """The person was removed: their templates go from the home device's database too."""
    if EDGE_DB.exists():
        import sqlite3                                   # noqa: PLC0415
        with sqlite3.connect(EDGE_DB) as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name = 'face_templates'").fetchone():
                db.execute("DELETE FROM face_templates WHERE person_id = ?", (tid,))


@app.post("/api/things/{tid}/face-video")
def thing_face_video(tid: str, payload: dict = Body(...)):
    """A person registered from a short video of their face: the video is kept as it came; the home device's face
    step (faces.py) samples it, finds the face in each frame (YuNet), aligns it and keeps up to 8 diverse SFace
    templates in its own database. The aligned faces become the person's views in the app."""
    t = next((t for t in store.things() if t["id"] == tid), None)
    if not t:
        raise HTTPException(404, "unknown thing")
    data = str(payload.get("video_b64", ""))
    if not data:
        raise HTTPException(400, "video_b64 is required")
    faces = CROPS.parent / "faces"
    faces.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    video = faces / f"{stamp}-{tid}.mp4"
    video.write_bytes(base64.b64decode(data.split(",", 1)[-1]))
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    try:
        dur = float(probe.stdout.strip())
    except ValueError:
        raise HTTPException(400, "not a video")
    res = enrol_face(tid, ["enrol-video", "--video", str(video)], f"{stamp}-{tid}")
    if not res.get("n"):
        store.add_event("thing", f"{t['name']}: no clear face was found in the {dur:.0f} s video. Try again, in good light.",
                        thing_id=tid)
        raise HTTPException(422, "No clear face was found in the video: " + str(res.get("error", ""))[:120])
    names = res["crops"]
    store.set_fingerprint(tid, {"n": len(names), "crops": names, "created": time.time(), "source": "video", "video": video.name,
                                "duration": round(dur, 1), "model": "YuNet + SFace (opencv_zoo)", "faces": res["n"]})
    store.add_event("thing", f"{t['name']} added from a {dur:.0f} s video of their face: {res['n']} face templates, kept on "
                    "the home device.", thing_id=tid, crop=names[0])
    return {"ok": True, "n": len(names), "duration": round(dur, 1), "faces": res["n"]}


def power(did, on, **extra):
    """Turn a device off (or on). The kit's plug: actions.run through the Altice MCP (a dry run unless
    TT_LIVE_ACTIONS=1, which is never set). The integration: simulated, nothing is sent. Logs a device event."""
    d = next((x for x in tt_devices() if x["id"] == did), None)
    if not d:
        raise HTTPException(404, "unknown device")
    if d["kit"]:
        res = actions.run("plug_on" if on else "plug_off")
        sent = "sent to the platform" if res.get("live") else "not sent (dry run)"
        ev = store.add_event("device", f"{d['name']} (powers {d['powers']}) turned {'on' if on else 'off'} from the app: {sent}.",
                             action=res, **extra)
    else:
        ev = store.add_event("device", f"{d['name']} turned {'on' if on else 'off'} from the app ({d.get('via', 'integration').lower()}, simulated).",
                             **extra)
    tt_set(did, on)
    return ev


@app.post("/api/tt-devices/{did}/power")
def set_tt_device(did: str, payload: dict = Body(...)):
    """Turn a device off (or on) from the app's device screen."""
    power(did, bool(payload.get("on")))
    return {"ok": True, "devices": tt_devices()}


def _alert(eid):
    e = store.event(eid)
    if not e or e["kind"] != "alert":
        raise HTTPException(404, "no such alert")
    return e


@app.post("/api/alerts/{eid}/act")
def alert_act(eid: str, payload: dict = Body(...)):
    """The answer to one of an alert's questions: {"device": id, "on": false} for a card ("Turn off the lights?" Yes),
    or {"act": "alarm_on"} for an ask ("Sound the alarm?" Yes). The alert keeps what was done."""
    e = _alert(eid)
    if payload.get("device"):
        did, on = str(payload["device"]), bool(payload.get("on", False))
        ev = power(did, on, alert_id=eid)
        cards = [{**c, "state": "on" if on else "off", "at": time.time()} if c.get("device") == did else c
                 for c in (e.get("cards") or [])]
        return {"ok": True, "alert": store.update_event(eid, cards=cards), "event": ev}
    if payload.get("act") == "alarm_on":
        alarm = sound_alarm(e.get("title", "alert"))
        store.set_meta("alarm", {**alarm_state(), "alert": eid})
        asks = [{**a, "state": "done", "at": time.time()} if a.get("act") == "alarm_on" else a for a in (e.get("ask") or [])]
        ev = store.add_event("alarm", "Alarm turned on from the app (simulated: the Altice alarm is never called).",
                             alert_id=eid, action=alarm["action"])
        return {"ok": True, "alert": store.update_event(eid, alarm=alarm, ask=asks), "event": ev}
    raise HTTPException(400, "device or act is required")


@app.post("/api/alerts/{eid}/alarm-off")
def alert_alarm_off(eid: str):
    """"Turn off the alarm" on an alert: the simulated alarm goes off; the Altice alarm is never called."""
    e = _alert(eid)
    res = actions.run("alarm_off")
    store.set_meta("alarm", {"on": False, "since": 0.0, "alert": None, "off_at": time.time()})
    alarm = e.get("alarm") if isinstance(e.get("alarm"), dict) else {"text": e.get("alarm") or ""}
    ev = store.add_event("alarm", "Alarm turned off from the app (simulated: the Altice alarm is never called).",
                         alert_id=eid, action=res)
    return {"ok": True, "alert": store.update_event(eid, alarm={**alarm, "state": "off", "off_at": time.time()}), "event": ev}


@app.post("/api/sim/phone")
def sim_phone(payload: dict = Body(...)):
    """A Family member's phone joins or leaves the home Wi-Fi: {"member": "filipe", "home": false}. Simulated: the
    Altice router sees the phones, but no MCP tool exposes them yet (presence.py names the one we would propose)."""
    mid = str(payload.get("member", ""))
    if mid not in {m["id"] for m in presence.family()}:
        raise HTTPException(404, "not a Family member")
    presence.set_phone(mid, bool(payload.get("home")), source="sim")
    return presence.snapshot()


@app.get("/api/presence")
def get_presence():
    return presence.evaluate()


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
PROFILE_KINDS = ("child", "dog", "cat", "older_alone")


def profile_suggestions(kind):
    """The sensors to suggest for who lives here, as (title, sentence, rule). Each rule is ready-made and of a kind the
    rules engine evaluates locally on the camera's data, so it really fires. None sends a picture anywhere, and the
    child's rule carries no photo at all. A pet's bowl is a registered thing when the home has one, else the place of
    the camera (each camera is one place)."""
    cam, things = store.camera_room(), store.things()

    def spot(key):
        name = next((t["name"] for t in things if place_matches(key, t["name"])), None)
        return (name, f"the {name.lower()}") if name else (cam, f"the {key} ({cam} camera)")

    base = {"engine": "local", "action": "notify", "thing_id": "", "minutes": 0, "cooldown_s": 300, "lang": "en",
            "min_s": 0}
    if kind in ("dog", "cat"):
        (food, food_txt), (water, water_txt) = spot("food bowl"), spot("water bowl")
        return [(f"The {kind}'s food", f"Tell me if the {kind} has not been at {food_txt} by 20:00.",
                 {**base, "title": f"The {kind}'s food by 20:00", "kind": "not_by", "who": kind, "place": food,
                  "by": "20:00", "message": f"The {kind} has not been at {food_txt} today."}),
                (f"The {kind}'s water", f"Tell me if the {kind} has not been at {water_txt} for 12 hours.",
                 {**base, "title": f"The {kind}'s water, 12 h", "kind": "not_by", "who": kind, "place": water,
                  "within_s": 12 * 3600, "message": f"The {kind} has not been at {water_txt} for 12 hours."})]
    if kind == "older_alone":
        kitchen = next((p for p in store.camera_places() if place_matches("kitchen", p)), cam)
        return [("Someone living alone", f"Tell me if nobody has been in the {kitchen} between 06:00 and 12:00.",
                 {**base, "title": f"Nobody in the {kitchen} by 12:00", "kind": "nobody_by", "place": kitchen,
                  "from": "06:00", "by": "12:00", "message": f"Nobody has been in the {kitchen} this morning."})]
    if kind == "child":
        return [("Children at home", "Tell me when a child arrives home.",
                 {**base, "title": "A child arrives home", "kind": "someone_arrives", "who": "child", "minutes": 30,
                  "message": "A child arrived home."})]
    return []


_profile_hits = {}


def suggest_for_profile(kind, score, declared=False):
    """Suggest sensors after the camera has seen a child or a pet clearly, in 3 analyses within 10 minutes, or at once
    when the family declares who lives here. An older person living alone is only ever declared, never guessed."""
    if kind not in PROFILE_KINDS or (kind == "older_alone" and not declared):
        return []
    if not declared:
        if float(score or 0) < 0.45:
            return []
        now_ = time.time()
        _profile_hits[kind] = [t for t in _profile_hits.get(kind, []) if now_ - t < 600] + [now_]
        if len(_profile_hits[kind]) < 3:
            return []
    if kind in store.suggested():
        return []
    store.mark_suggested(kind)
    return [store.add_event("suggest", f"{title}. Suggested sensor: “{sentence}”", title=title, sentence=sentence,
                            rule=rule, profile=kind) for title, sentence, rule in profile_suggestions(kind)]


@app.post("/api/profile")
def declare_profile(payload: dict = Body(...)):
    """The family says who lives here ('older_alone', 'child', 'dog', 'cat'): the matching sensors are suggested."""
    kind = str(payload.get("kind", ""))
    if kind not in PROFILE_KINDS:
        raise HTTPException(400, f"kind is one of {', '.join(PROFILE_KINDS)}")
    return {"suggested": suggest_for_profile(kind, 1.0, declared=True)}


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


# ---------------------------------------------------------------------- the front door (the kit's Contact sensor)
# The door is the home's Contact sensor ('sensorState' 'alarm' means open). When the MCP session is live, the server
# polls it every 4 s with the read-only tool get_home_devices; when it is not, the page's "Simulate: door opens" button
# drives it (POST /api/sim/door). Both feed door_changed(), which starts the leave_without checks.
DOOR = {"open": None, "source": "", "changed": 0.0, "opened_at": 0.0, "live": False}
PENDING = {}                    # leave_without rule id -> the check started when the door closed (check_leave_without)
_door_lock = threading.Lock()
POLL_S = float(os.environ.get("TT_DOOR_POLL_S", "4"))


def door_changed(is_open, source, baseline=False):
    """baseline: the first live reading after the session comes up says where the door is, not that it moved.
    Every change goes to the presence engine (an opening then a closing is LEAVING). The leave_without rules start on
    the CLOSING after an opening: by then whoever went out is out."""
    now_ = time.time()
    with _door_lock:
        prev = DOOR["open"]
        if prev is is_open:
            return
        DOOR.update(open=is_open, source=source, changed=now_)
        if is_open:
            DOOR["opened_at"] = now_
    if baseline or (source == "live" and prev is None):
        return
    sim = source in ("sim", "replay")
    if sim:
        store.set_device_status("contactSensor", "Open" if is_open else "Closed")
    label = {"sim": "Simulated: the door ", "replay": "Replayed: the door "}.get(source, "The door ")
    store.add_event("door", label + ("opened" if is_open else "closed") + " (Contact sensor).", sim=sim,
                    replayed=source == "replay", open=is_open, device="Contact sensor")
    count_before = presence.s.get("count", 0)
    presence.door(is_open)
    if is_open or not prev:
        return
    opened = DOOR["opened_at"] or now_
    count_before = (presence.s.get("leaving") or {}).get("count_before", count_before)   # the count as the door opened
    for r in store.active_rules():          # open -> closed
        if (r.get("kind") == "leave_without" and r["id"] not in PENDING
                and now_ - r.get("last_fired", 0) >= r.get("cooldown_s", 300)):
            PENDING[r["id"]] = {"stage": "who", "opened": opened, "closed": now_, "count_before": count_before,
                                "decide_by": now_ + T["phone_lag_s"]}


@app.post("/api/sim/door")
def sim_door(payload: dict = Body(...)):
    """The simulated front door, for when the MCP session is not live: {"open": true} or {"open": false}."""
    door_changed(bool(payload.get("open")), "sim")
    return dict(DOOR)


def _caps(d):
    """A device's capabilities by type (the MCP sends them with an empty name and the type as the key)."""
    return {(c.get("type") or c.get("name")): c.get("value") for c in d.get("capabilities", []) if isinstance(c, dict)}


def device_poller():
    """When the MCP session is live: every POLL_S seconds, the device statuses through the READ-ONLY get_home_devices
    (into the local copy of the home), a device going on or off line, and the door's changes. When it is not live:
    try again every 15 s, quietly, so a `chmcp.py login` is picked up without restarting the server."""
    last_door = None
    while True:
        data = actions.poll_devices()
        DOOR["live"] = data is not None
        if data is None:
            last_door = None
            time.sleep(15)
            continue
        devs = [d for d in data.get("devices", []) if d.get("id")]
        before = {d["id"]: d["status"] for d in store.home()["devices"]}
        for d in devs:                       # "Light is online.", as the Altice app writes it
            old, new = before.get(d["id"]), _status(d)
            if old is not None and (old == "Disconnected") != (new == "Disconnected"):
                store.add_event("device", f"{d.get('name', 'A device')} is {'offline' if new == 'Disconnected' else 'online'}.",
                                device=d.get("name", ""))
        store.sync_devices([{"id": d["id"], "status": _status(d)} for d in devs],
                           f"Synced from the Altice platform at {time.strftime('%H:%M')}")
        door = next((d for d in devs if d.get("type") == "contactSensor"), None)
        if door and _status(door) != "Disconnected":
            is_open = _caps(door).get("sensorState") == "alarm"
            if is_open != last_door:         # only a change of the real sensor, never a re-read
                door_changed(is_open, "live", baseline=last_door is None)
                last_door = is_open
        time.sleep(POLL_S)


def is_exit(rule, o):
    """Was this sighting at the way out? A camera place (or surface) named entrance, hall, door, entrada, porta..."""
    return place_matches(rule.get("exit_place") or "entrance", o["room"], o["zone_name"])


def last_place_text(o, lang):
    day = time.strftime("%Y-%m-%d", time.localtime(o["ts"]))
    today, yday = time.strftime("%Y-%m-%d"), time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
    if lang == "pt":
        when = {today: "hoje", yday: "ontem"}.get(day, time.strftime("a %d/%m", time.localtime(o["ts"])))
        where = {**Brain.PLACE_PT, "room": "na divisão"}.get(o["zone_name"], f"em {o['zone_name']}")
        return f"Última deteção: {where} ({o['room']}), {when} às {hm(o['ts'])}."
    when = {today: "today", yday: "yesterday"}.get(day, time.strftime("on %d %b", time.localtime(o["ts"])))
    where = "in the room" if o["zone_name"] == "room" else f"on the {o['zone_name']}"
    return f"Last seen {where} ({o['room']}), {when} at {hm(o['ts'])}."


def check_leave_without(r, p, now_):
    """A leave_without check, started when the door CLOSED after an opening (door_changed). Returns True when done.
    1. who: did a Family member leave? A phone left the home Wi-Fi since the door opened, or the presence count dropped
       below the count as the door opened. A phone joining instead is an arrival: no check. Neither within phone_lag_s:
       nobody left, no check. A thing seen at an entrance camera as the door opened went out with them: no check.
    2. check: the edge looks for the thing now, over a few frames, whatever the motion (an active check). Seen at
       home: the alert, with that picture and the place. Not visible: "unsure" in the activity, no alert, no alarm.
       No answer within check_timeout_s (the camera service is off): "unsure" too."""
    tid = r.get("thing_id")
    thing = next((t for t in store.things() if t["id"] == tid), None)
    what = thing["name"] if thing else "the thing"
    if p["stage"] == "who":
        last = store.last_seen(tid) if thing else None
        if not last:
            store.add_event("info", f"{r['title']}: the door closed, but the camera has never seen {what.lower()}, so "
                            "there is no place to check.", rule_id=r["id"])
            return True
        grace = float(r.get("grace_s") or 60)
        if is_exit(r, last) and last["ts"] >= p["opened"] - grace:
            store.add_event("ok", f"{what} was seen at the {last['room']} as the door opened: it went out.",
                            rule_id=r["id"], thing_id=tid, crop=last.get("crop"))
            return True
        since = p["opened"] - 5
        left, came = presence.left_since(since), presence.arrived_since(since)
        dropped = presence.s["state"] != LEAVING and presence.s.get("count", 0) < p["count_before"]
        if came and not left:
            store.add_event("info", f"{r['title']}: the door opened and closed as {join(came)} arrived: no check.",
                            rule_id=r["id"])
            return True
        if left or dropped:
            who = (f"{join(left)} left (phone off the home Wi-Fi)" if left
                   else f"someone left (people at home: {p['count_before']} → {presence.s.get('count', 0)})")
            cid = f"c{int(now_ * 1000)}"
            CHECKS[cid] = {"thing_id": tid, "name": what, "query": (thing.get("description") or what).lower(),
                           "frames": 3, "asked": now_, "result": None}
            p.update(stage="check", check=cid, who=who, left=left, usual=last["zone_name"], room=last["room"],
                     due=now_ + T["check_timeout_s"])
            store.add_event("info", f"{r['title']}: {who}. Checking the {last['zone_name']} for the {what.lower()}.",
                            rule_id=r["id"], thing_id=tid)
            return False
        if now_ >= p["decide_by"]:
            store.add_event("info", f"{r['title']}: the door opened and closed, but nobody left (no phone left the "
                            "home Wi-Fi, the count did not drop): no check.", rule_id=r["id"])
            return True
        return False
    c = CHECKS.get(p.get("check"), {})
    res = c.get("result")
    if res is None and now_ < p["due"]:
        return False
    CHECKS.pop(p.get("check"), None)
    if res is None:
        store.add_event("unsure", f"{r['title']}: unsure. {p['who'][0].upper() + p['who'][1:]}, but the camera service did not "
                        f"answer the check of the {p['usual']}: no alert.", rule_id=r["id"], thing_id=tid)
        return True
    if not res["seen"]:
        store.add_event("unsure", f"{r['title']}: unsure. The {what.lower()} was not visible on the {p['usual']} after "
                        f"{p['who'].split(' (')[0]}: maybe it went with them. No alert.", rule_id=r["id"], thing_id=tid)
        return True
    place = res["place"] if res["place"] not in ("", "room") else p["usual"]
    where = f"in the {p['room']}" if place == "room" else f"on the {place}"
    text = f"The door closed and your {what.lower()} is still {where}." + (" The alarm is on." if r.get("alarm") else "")
    thing_crop = (store.last_seen(tid) or {}).get("crop")
    fire(r, crop=thing_crop or res["crop"], picture=res["crop"] or thing_crop, text=text, thing_id=tid, place=place, room=p["room"],
         evidence=f"Door opened at {hm(p['opened'])}, closed at {hm(p['closed'])}; {p['who']}; the camera saw the "
                  f"{what.lower()} {where} ({res.get('score')}, {res.get('frames')} frames).")
    return True


POLICE = {"kind": "police", "title": "Possible intrusion", "number": "112",
          "text": "Someone who isn't Family is at home while the family is away. We recommend calling the police."}


def person_picture(camera):
    """The unknown face's person crop the edge sent with its latest analysis of this camera, saved now that a rule
    fires; None if there is none from the last minute."""
    ts, b64 = _unknown_crop.get(camera, (0, None))
    if not b64 or time.time() - ts > 60:
        return None
    name = f"{time.strftime('%Y%m%d-%H%M%S')}-unknown-person.jpg"
    (CROPS / name).write_bytes(base64.b64decode(b64))
    return name


def check_security(r, now_):
    """'Sound the alarm when someone who isn't Family comes in' (a rule marked unknown). Per camera, from the edge's
    face recognition (presence runs):
    - a visible face that matches no registered person on unknown_runs consecutive analyses, with the Family away:
      the alarm (simulated) and the police suggestion; with a Family member at home (a guest, most likely): a message,
      no alarm. A Family member's face never counts: it is a known identity, not "unknown".
    - a person whose face is not seen, on unknown_runs consecutive analyses, with the Family away: an alert that asks
      ("Sound the alarm?"), never the alarm by itself."""
    need, fam_home = T["unknown_runs"], presence.family_home()
    names = presence.people()
    for cam in list(presence.s["cameras"]):
        n, since = presence.run(cam, "unknown")
        if n >= need and r.get("episode", 0) < since:
            store.update_rule(r["id"], episode=since)
            pic = person_picture(cam)
            if fam_home:
                fire(r, alarm=False, action="notify", picture=pic, unknown=True, camera=cam,
                     text=f"Someone who isn't Family is at home with {join(names.get(m, m) for m in fam_home)}.",
                     evidence=f"An unknown face on {n} analyses in a row ({cam}); Family at home, so no alarm.")
            else:
                took = [e for e in store.events(40) if e["kind"] == "handled" and e.get("taken") and e["ts"] >= since - 60]
                sugg = dict(POLICE)
                if took:
                    sugg["text"] = ("An unknown person came in and took something while the family is away. "
                                    "We recommend calling the police.")
                fire(r, picture=pic, unknown=True, camera=cam, suggestion=sugg,
                     text="Someone who isn't Family came in." + (" The alarm is on." if r.get("alarm") else ""),
                     evidence=f"An unknown face on {n} analyses in a row ({cam}); the family's phones are away and no "
                              "Family face was seen.")
            continue
        n2, since2 = presence.run(cam, "no_face")
        if n2 >= need and not fam_home and r.get("episode_noface", 0) < since2:
            store.update_rule(r["id"], episode_noface=since2)
            fire(r, alarm=False, action="notify", title="Someone is home", camera=cam,
                 text="Someone is at home, and the camera has not seen their face. The family is away.",
                 ask=[{"act": "alarm_on", "label": "Sound the alarm?", "state": "ask"}],
                 evidence=f"A person with no visible face on {n2} analyses in a row ({cam}); the family's phones are away.")


def check_empty_home(rules, now_):
    """nobody_devices_on and door_open_nobody, on the presence engine's EMPTY: one alert per incident. When devices are
    still on and the door is open, the alert waits for the longer grace and carries both: the devices to turn off and
    the door banner (with the simulated alarm if the door rule asks for it)."""
    if presence.s["state"] != EMPTY:
        return
    empty_since = presence.s["since"]
    dev_rules = [r for r in rules if r.get("kind") == "nobody_devices_on"]
    door_rules = [r for r in rules if r.get("kind") == "door_open_nobody"]
    grace = lambda r: float(r.get("grace_s") or float(r.get("minutes") or 0) * 60 or 10)
    on = [d for d in tt_devices() if d["on"]]
    door_open = DOOR["open"] is True
    dev_due = [r for r in dev_rules if on and r.get("asked_after", 0) < empty_since and now_ - empty_since >= grace(r)]
    dev_wait = [r for r in dev_rules if on and r.get("asked_after", 0) < empty_since and now_ - empty_since < grace(r)]
    door_due = [r for r in door_rules if door_open and r.get("door_seen", 0) < DOOR["changed"]
                and now_ - max(empty_since, DOOR["changed"]) >= grace(r)]
    if door_due and dev_wait:
        return                                   # one alert: wait for the devices' grace
    if not dev_due and not door_due:
        return
    door = {"open": True, "text": "The door is open and nobody is home."} if door_open and (door_due or door_rules) else None
    sound = any(r.get("alarm") for r in door_due)
    evidence = presence.s["reason"]
    if dev_due:
        r = dev_due[0]
        for x in dev_due:
            store.update_rule(x["id"], asked_after=empty_since)
        for x in door_due:
            store.update_rule(x["id"], door_seen=DOOR["changed"], last_fired=now_)
        cards = [{"device": d["id"], "name": d["name"], "kind": d["type"], "state": "on",
                  "label": "Turn off the AC?" if d["type"] == "ac" else "Turn off the lights?" if "light" in (d.get("powers") or "").lower()
                  else f"Turn off {d.get('powers') or d['name']}?"} for d in on]
        text = f"Everyone left, and {len(on)} thing{'s are' if len(on) > 1 else ' is'} still on." + (" The door is open." if door else "")
        e = fire(r, title="Nobody is home", text=text, alarm=sound, cards=cards, door=door, devices=[d["id"] for d in on],
                 camera=store.camera_room(),
                 rule_ids=[x["id"] for x in dev_due + door_due], evidence=evidence + " On: " + ", ".join(
                     d["name"] + (f" ({d['powers']})" if d.get("powers") else "") for d in on) + ".", ask_off=True)
    else:
        r = door_due[0]
        for x in door_due:
            store.update_rule(x["id"], door_seen=DOOR["changed"])
        e = fire(r, door={"open": True, "text": "The door is open and nobody is home."}, camera=store.camera_room(),
                 evidence=f"Door open since {hm(DOOR['changed'])}. {evidence}")
    ask_snapshot(e)


def rules_engine():
    """Evaluates the local rules every 2 s against the memory, the door and the presence engine."""
    while True:
        now_ = time.time()
        try:
            presence.evaluate()                         # time passes: LEAVING ends, faces and sightings grow old
            rules = [r for r in store.active_rules() if r.get("engine") == "local"]
            check_empty_home([r for r in rules if now_ - r.get("last_fired", 0) >= r.get("cooldown_s", 300)], now_)
        except Exception as e:
            print("presence error", e)
        for k, v in list(CHECKS.items()):               # a check nobody is waiting for any more
            if now_ - v["asked"] > 300:
                CHECKS.pop(k, None)
        for k, v in list(SNAPSHOTS.items()):
            if now_ - v["asked"] > 60:
                SNAPSHOTS.pop(k, None)
        for r in store.active_rules():
            if r.get("engine") != "local":
                continue
            if r.get("kind") == "leave_without":        # started by the door closing, not by the clock
                p = PENDING.get(r["id"])
                if p:
                    try:
                        if check_leave_without(r, p, now_):
                            PENDING.pop(r["id"], None)
                    except Exception as e:
                        PENDING.pop(r["id"], None)
                        print("rule error", r.get("id"), e)
                continue
            if now_ - r.get("last_fired", 0) < r.get("cooldown_s", 300) and not r.get("unknown"):
                continue                                # (the security rule counts its own episodes instead)
            kind, mins = r.get("kind"), float(r.get("minutes") or 0)
            try:
                if kind == "someone_arrives" and r.get("who") in ("child", "dog", "cat"):
                    # "a child arrives home": seen after none was seen for `minutes`. No photo, ever.
                    who, gap = r["who"], max(mins or 30, 5) * 60
                    rows = store.presence([who], since=r.get("seen_at") or r.get("created_at", 0))
                    if rows:
                        store.update_rule(r["id"], seen_at=rows[-1]["ts"])
                    for row in rows:
                        prev = store.last_presence([who], before=row["ts"])
                        if not prev or row["ts"] - prev["ts"] > gap:
                            fire(r, evidence=f"Seen at the {row['room']} at {hm(row['ts'])}; "
                                             f"none seen in the {int(gap // 60)} min before.")
                            break
                elif kind == "seen_in" and r.get("who"):
                    who = r["who"]
                    rows = [x for x in store.presence(["person", "child"] if who == "person" else [who],
                                                      since=max(now_ - 10, r.get("seen_at", 0)))
                            if place_matches(r.get("place"), x["room"], x["place"])]
                    if rows:
                        store.update_rule(r["id"], seen_at=rows[-1]["ts"])
                        fire(r, evidence=f"Seen at the {rows[-1]['room']} ({rows[-1]['place']}).")
                elif kind == "left_for":
                    last = store.last_seen(r.get("thing_id"))
                    place = r.get("place") or (last or {}).get("zone_name")
                    if last and last["zone_name"] == place and now_ - last["ts"] < 120:
                        start = _stay_start(r["thing_id"], place)
                        if start and now_ - start >= mins * 60:
                            fire(r, crop=last.get("crop"), evidence=f"On the {place} for {int((now_ - start) // 60)} min.")
                elif kind == "nobody_for" and edge_online():
                    quiet = now_ - max(EDGE["last_motion"], presence.s["last_person"], r.get("armed_at", 0))
                    if quiet >= mins * 60:
                        fire(r, evidence=f"No movement for {int(quiet // 60)} min.")
                        store.update_rule(r["id"], armed_at=now_)
                elif kind == "someone_arrives" and r.get("unknown"):
                    check_security(r, now_)
                elif kind == "someone_arrives":
                    # anyone arrives: the presence engine's last person seen, after none was seen for `minutes`
                    lp = presence.s["last_person"]
                    if lp > r.get("seen_person", 0) and lp - r.get("seen_person", 0) > max(mins, 5) * 60:
                        if r.get("seen_person"):
                            fire(r, evidence="Someone arrived after the room was empty. " + presence.s["reason"])
                        store.update_rule(r["id"], seen_person=lp)
                    elif lp > r.get("seen_person", 0):
                        store.update_rule(r["id"], seen_person=lp)
                elif kind in ("nobody_devices_on", "door_open_nobody"):
                    pass                                # check_empty_home, above: one alert per empty-home incident
                elif kind == "seen_in":
                    last = store.last_seen(r.get("thing_id"))
                    if last and now_ - last["ts"] < 10 and (not r.get("place") or last["zone_name"] == r["place"]):
                        fire(r, crop=last.get("crop"), evidence=f"Seen on the {last['zone_name']}.")
            except Exception as e:  # one bad rule must not stop the engine
                print("rule error", r.get("id"), e)
        time.sleep(2)


threading.Thread(target=rules_engine, daemon=True).start()
if not os.environ.get("TT_REPLAY"):     # in a replay the door is the take's, never the live sensor
    threading.Thread(target=device_poller, daemon=True).start()

# ---------------------------------------------------------------------- API
@app.get("/api/state")
def state():
    s = store.snapshot()
    s["settings"] = {"live_actions": actions.LIVE, "ai": brain.enabled, "llm": brain.text_mode(), "budget_usd": brain.cap,
                     "kit_camera": bool(os.environ.get("CAMERA_RTSP_URL"))}
    s["edge"] = {k: v for k, v in EDGE.items() if k != "boxes"} | {"online": edge_online()}
    s["enrol"] = dict(ENROL) or None
    s["tt_devices"] = tt_devices()
    s["door"] = dict(DOOR)
    s["presence"] = presence.snapshot()
    s["alarm"] = alarm_state()
    s["replay"] = replayer.status() if replayer else None
    return s


@app.get("/api/devices")
def devices():
    """The home as the Altice app shows it, from the local database (a copy of the platform's home, rooms, devices)."""
    return store.home()


def _status(d):
    """A device's status line, written as the Altice app writes it."""
    caps = _caps(d)
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


@app.get("/api/things/{tid}/sightings")
def thing_sightings(tid: str):
    """The home's memory for one thing: where and when the camera saw it, oldest first."""
    return {"sightings": store.observations(tid, limit=50)}


@app.delete("/api/things/{tid}")
def delete_thing(tid: str):
    store.delete_thing(tid)
    forget_face(tid)
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
    store.add_event("thing", f"Now tracking: {name}.", thing_id=tid)
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


# A sentence that asks to be told, or to act, becomes a sensor; anything else is a question. "When"/"quando" alone
# says nothing: "Quando vi o livro" is a question, "When the door opens, turn the light red" is a rule.
_REQUEST = re.compile(r"\b(tell me|notify|alert me|warn me|let me know|remind me|send me|avisa|avise|lembra|notifica|"
                      r"diz-me|diga-me|manda-me|alerta-me)")
_REQUEST_ASKS = re.compile(r"\b(tell me|let me know|diz-me|diga-me)\s+(where|what|which|who|how|onde|o que|qual|quais|"
                           r"quem|como)\b")
_ACTION = re.compile(r"\b(turn|switch|liga|desliga|acende|apaga)\b")
_ASKS = re.compile(r"^(where|what|which|who|whose|how|did|do|does|have|has|had|is|are|was|were|onde|qual|quais|quem|"
                   r"como|o que|que|viste|vi|viu|há|houve|esteve|estava|está|estão|já)\b")
_AUX = re.compile(r"^(when|quando)\s+(did|do|does|was|were|is|are|have|has|had|é que|foi|vi|viste|viu|esteve|estava|"
                  r"deixei|saí|tive)\b")


def is_rule(text):
    low = text.lower().strip()
    if low.endswith("?") or re.match(r"^(did|do|does|have|has|was|were)\b", low):
        return False
    if _REQUEST.search(low):
        return not _REQUEST_ASKS.search(low)
    if _ASKS.match(low) or _AUX.match(low):
        return False
    return bool(_ACTION.search(low))


@app.post("/api/assistant")
def assistant(payload: dict = Body(...)):
    """The app's assistant button: a question gets an answer from the home's memory; a sentence that asks to be
    told or to act becomes a sensor. Both go through the ThingTracker service, the only caller of the language model."""
    text = str(payload.get("text", "")).strip()[:300]
    if not text:
        raise HTTPException(400, "text is required")
    if is_rule(text):
        return {"kind": "sensor", "sensor": add_rule({"sentence": text})}
    return {"kind": "answer", **ask({"question": text})}


def rule_note(r):
    """Why a new sensor cannot fire yet, in one sentence for the activity, or ''."""
    kind, things = r.get("kind"), store.things()
    if kind in ("leave_without", "left_for") or (kind == "seen_in" and not r.get("who")):
        if not any(t["id"] == r.get("thing_id") for t in things):
            return "No registered thing matches it yet: add the thing in the Things tab."
    if kind in ("not_by", "nobody_by"):
        if kind == "not_by" and not r.get("by") and not r.get("within_s"):
            return "It gives no time: say “by 20:00” or “in 12 hours”."
        place = r.get("place")
        if place and not any(place_matches(place, n) for n in store.camera_places() + [t["name"] for t in things]):
            return f"No camera or registered thing is called “{place}” yet: register it as a thing, or name a camera after it."
    return ""


@app.post("/api/rules")
def add_rule(payload: dict = Body(...)):
    """A sentence becomes a local rule: the language model (or, with AI off, a template) compiles it once;
    the rules engine then evaluates it on the camera's sightings, at no cost per check."""
    sentence = str(payload.get("sentence", "")).strip()[:300]
    if not sentence:
        raise HTTPException(400, "sentence is required")
    suggestion = store.find_suggestion(sentence)    # a suggested sensor comes with its rule ready-made
    compiled = (dict(suggestion["rule"]) if suggestion and suggestion.get("rule")
                else _llm(brain.compile_local, sentence, store.things(), store.camera_places()))
    low = sentence.lower()
    if any(w in low for w in ("don't know", "do not know", "dont know", "stranger", "unknown", "não conheço", "nao conheco", "desconhecid",
                              "isn't family", "is not family", "not in family", "not family", "não é da família")):
        compiled["unknown"] = True      # someone who is not one of the people added in the app (the edge has no face model yet)
        compiled["thing_id"] = ""       # about anyone unknown, not about one registered person
        if not any(w in str(compiled.get("title", "")).lower() for w in ("unknown", "stranger")):
            compiled["title"] = "Unknown person at home"
    if str(payload.get("title", "")).strip():
        compiled["title"] = str(payload["title"]).strip()[:40]   # a suggestion the app makes comes with its own title
    if any(w in sentence.lower() for w in ("alarm", "siren", "alarme", "sirene")):
        compiled["alarm"] = True        # simulated: the alert says the alarm is on; the platform's alarm is never called
    compiled.update(engine="local", zone_id="", created_at=time.time(),
                    cooldown_s=max(60, min(3600, int(compiled.get("cooldown_s", 300)))))
    if compiled.get("kind") == "leave_without":
        compiled["grace_s"] = int(compiled.get("grace_s") or 60)
        if compiled.get("action", "notify") == "notify":   # the team's choice (18 Nov): the alert and a red light
            compiled["action"] = LEAVE_ACTION
    rule = store.add_rule(sentence, compiled)
    note = rule_note(rule)
    store.add_event("sensor", f"New sensor: {rule['title']}." + (f" {note}" if note else ""), rule_id=rule["id"])
    return {**rule, "note": note}


LEAVE_ACTION = os.environ.get("TT_LEAVE_ACTION", "light_red")
TUNABLE = {"grace_s": float, "min_s": float, "within_s": float, "minutes": float, "cooldown_s": int,
           "by": hhmm, "from": hhmm, "place": str, "exit_place": str}


@app.patch("/api/rules/{rid}")
def patch_rule(rid: str, payload: dict = Body(...)):
    """Pause or resume a sensor ({"active": false}), or tune it: grace_s, by, from, within_s, min_s, place..."""
    fields = {"active": bool(payload["active"])} if "active" in payload else {}
    for k, conv in TUNABLE.items():
        if k in payload:
            v = conv(str(payload[k]))[:40] if conv in (hhmm, str) else conv(payload[k])
            if conv is hhmm and not v:
                raise HTTPException(400, f"{k} must be a time, HH:MM")
            fields[k] = v
    if {"by", "from", "within_s"} & set(fields):     # a new deadline is checked afresh
        fields.update(fired_today=False, seen_trigger_today=False)
    r = store.update_rule(rid, **fields)
    if not r:
        raise HTTPException(404, "no such sensor")
    return r


@app.delete("/api/rules/{rid}")
def delete_rule(rid: str):
    store.delete_rule(rid)
    PENDING.pop(rid, None)
    return {"ok": True}


@app.post("/api/reset")
def reset():
    store.reset()
    presence.reset()
    HELD.clear()
    return {"ok": True}


kit = KitCamera(os.environ["CAMERA_RTSP_URL"]) if os.environ.get("CAMERA_RTSP_URL") else None
replayer = None


def replay_setup(setup):
    """The take's starting state, before its first second: the phones, the devices, a rule's tuning."""
    for mid, home in (setup.get("phones") or {}).items():
        presence.set_phone(mid, bool(home), source="replay")
    for did, on in (setup.get("devices") or {}).items():
        tt_set(did, bool(on))
    for kind, fields in (setup.get("rules") or {}).items():
        for r in store.active_rules():
            if r.get("kind") == kind:
                store.update_rule(r["id"], **fields)
    if setup.get("door") in ("open", "closed"):
        with _door_lock:
            DOOR.update(open=setup["door"] == "open", source="replay", changed=time.time())
        presence.s["door"]["open"] = setup["door"] == "open"


def replay_event(e):
    """One input no camera can see, at its moment in the take, labelled "Replayed" in the activity."""
    if "door" in e:
        door_changed(e["door"] == "open", "replay")
    elif "phone" in e:
        presence.set_phone(e["phone"], bool(e["home"]), source="replay")
    elif "device" in e:
        d = next((x for x in tt_devices() if x["id"] == e["device"]), None)
        tt_set(e["device"], bool(e["on"]))
        store.add_event("device", f"Replayed: {(d or {}).get('name', e['device'])} switched {'on' if e['on'] else 'off'} "
                        "by hand in the lab.", replayed=True)
    elif "mark" in e:
        learn_from_camera(e["mark"]["thing"], {"box": e["mark"]["box"], "replayed": True})


if os.environ.get("TT_REPLAY"):
    from replay import Replayer, ReplayCamera   # noqa: E402
    kit = ReplayCamera(os.environ["TT_REPLAY"])
    replayer = Replayer(kit, {"setup": replay_setup, "event": replay_event})
    replayer.setup()


@app.post("/api/replay/start")
def replay_start():
    if not replayer:
        raise HTTPException(404, "not in replay mode (TT_REPLAY)")
    started = replayer.start()
    if started:
        store.add_event("info", f"Replay started: {kit.video.name} ({kit.duration:.1f} s) stands in for the camera. "
                        "Only the door, the phones and hand-switched devices are replayed; the rest is computed live.")
    return replayer.status()


@app.get("/api/replay")
def replay_status():
    return replayer.status() if replayer else {"replay": False}


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
