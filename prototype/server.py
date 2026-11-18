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


def fire(rule, crop=None, evidence="", text=None, **extra):
    result = actions.run(rule["action"])
    store.update_rule(rule["id"], last_fired=time.time(), fired_today=True)
    return store.add_event("alert", text or rule["message"], rule_id=rule["id"], title=rule["title"], action=result,
                           crop=crop, evidence=evidence, **extra)


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
        if who in ("person", "child"):
            EDGE["last_person"] = now_


@app.post("/api/edge/observe")
def edge_observe(payload: dict = Body(...)):
    """What the edge saw: thing, place, a small crop of the thing, who is there (people, pets) and where. Never the
    full frame, never a picture of a person. 'camera' names the camera's place (default: the kit camera's room)."""
    now_ = time.time()
    EDGE["updated"], EDGE["ms"] = now_, payload.get("ms")
    if int(payload.get("people", 0)) > 0:
        EDGE["last_person"] = now_
    camera = clean_place(payload.get("camera")) or store.camera_room()
    known = {t["id"]: t["name"] for t in store.things()}
    last = {t["id"]: t.get("last_seen") for t in store.snapshot()["things"]}
    for sgt in payload.get("sightings", [])[:12]:
        tid = sgt.get("thing_id")
        if tid not in known:
            continue
        place = "".join(ch for ch in str(sgt.get("place", "room")).lower() if ch.isalpha() or ch == " ")[:24] or "room"
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
DOOR = {"open": None, "source": "", "changed": 0.0, "live": False}
PENDING = {}                    # leave_without rule id -> {"opened": ts, "due": ts}
_door_lock = threading.Lock()
POLL_S = float(os.environ.get("TT_DOOR_POLL_S", "4"))


NO_EXIT_GRACE = 5   # seconds: with no camera at the entrance there is nothing to wait for


def door_changed(is_open, source, baseline=False):
    """baseline: the first live reading after the session comes up says where the door is, not that it moved."""
    now_ = time.time()
    with _door_lock:
        prev = DOOR["open"]
        if prev is is_open:
            return
        DOOR.update(open=is_open, source=source, changed=now_)
    if baseline or (source == "live" and prev is None):
        return
    sim = source == "sim"
    if sim:
        store.set_device_status("contactSensor", "Open" if is_open else "Closed")
    store.add_event("door", ("Simulated: the door " if sim else "The door ") + ("opened" if is_open else "closed")
                    + " (Contact sensor).", sim=sim, open=is_open, device="Contact sensor")
    if not is_open:
        return
    # grace_s is the time to see the thing go out at an entrance camera; with none, only a few seconds
    entrance = any(place_matches("entrance", p) for p in store.camera_places())
    for r in store.active_rules():          # closed (or unknown, for the simulation) -> open
        if (r.get("kind") == "leave_without" and r["id"] not in PENDING
                and now_ - r.get("last_fired", 0) >= r.get("cooldown_s", 300)):
            grace = float(r.get("grace_s") or 60)
            if not (entrance or r.get("exit_place")):
                grace = min(grace, NO_EXIT_GRACE)
            PENDING[r["id"]] = {"opened": now_, "due": now_ + grace}


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


def check_leave_without(r, p):
    """The door opened grace_s ago: alert if the thing is still at home, with its photo and its last place.
    "At home" means its newest sighting is anywhere but the way out; it need not be recent, because the last known
    place stays home until a camera sees the thing going out. "Going out" means seen at an entrance camera (a place
    named entrance, hall, door, entrada...) from grace_s before the door opened until now.
    Limits of this simple version, on purpose:
    - the contact sensor says the door opened, not who opened it nor which way: someone arriving also counts;
    - without a camera at the entrance nothing is ever seen going out, so every opening while the thing is at home
      alerts, also when the user did take it;
    - a thing taken out unseen still counts as at home until a camera sees it again;
    - a thing the camera has never seen gives no alert (a line in the activity instead): there is no last place."""
    tid = r.get("thing_id")
    thing = next((t for t in store.things() if t["id"] == tid), None)
    last = store.last_seen(tid) if thing else None
    if not last:
        what = thing["name"] if thing else "the thing"
        store.add_event("info", f"{r['title']}: the door opened, but the camera has never seen {what}, so there is no "
                        "last place to check.", rule_id=r["id"])
        return
    grace = float(r.get("grace_s") or 60)
    if is_exit(r, last) and last["ts"] >= p["opened"] - grace:
        store.add_event("ok", f"{thing['name']} was seen at the {last['room']} as the door opened: it went out.",
                        rule_id=r["id"], thing_id=tid, crop=last.get("crop"))
        return
    fire(r, crop=last.get("crop"), text=f"{r['message']} {last_place_text(last, r.get('lang'))}",
         evidence=f"Door opened at {hm(p['opened'])}; not seen going out.", thing_id=tid,
         place=last["zone_name"], room=last["room"], seen_at=last["ts"])


def rules_engine():
    """Evaluates the local rules every 2 s against the memory, the door and the edge's presence signals."""
    while True:
        now_ = time.time()
        for r in store.active_rules():
            if r.get("engine") != "local":
                continue
            if r.get("kind") == "leave_without":        # started by the door, not by the clock
                p = PENDING.get(r["id"])
                if p and now_ >= p["due"]:
                    PENDING.pop(r["id"], None)
                    try:
                        check_leave_without(r, p)
                    except Exception as e:
                        print("rule error", r.get("id"), e)
                continue
            if now_ - r.get("last_fired", 0) < r.get("cooldown_s", 300):
                continue
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
threading.Thread(target=device_poller, daemon=True).start()

# ---------------------------------------------------------------------- API
@app.get("/api/state")
def state():
    s = store.snapshot()
    s["settings"] = {"live_actions": actions.LIVE, "ai": brain.enabled, "llm": brain.text_mode(), "budget_usd": brain.cap,
                     "kit_camera": bool(os.environ.get("CAMERA_RTSP_URL"))}
    s["edge"] = {k: v for k, v in EDGE.items() if k != "boxes"} | {"online": edge_online()}
    s["enrol"] = dict(ENROL) or None
    s["door"] = dict(DOOR)
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
