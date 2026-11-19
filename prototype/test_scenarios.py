"""The headline scenarios, end to end, against a running server, with simulated data. Prints PASS or FAIL for each.

    prototype/.venv/bin/python prototype/test_scenarios.py
        starts a private server on :8775 with its own, empty data folder (the same code, the same local text model on
        :8766 if it runs), so the test never writes sensors, alerts or suggestions into the demo's database; stops it
        at the end.
    prototype/.venv/bin/python prototype/test_scenarios.py --server http://127.0.0.1:8765
        uses a server that is already running. It WRITES test things, sensors, sightings and suggestions into that
        server's database: use it only on a throwaway one.

The private server also reads the devices from a file in the shape of get_home_devices (TT_DEVICES_FILE) instead
of the MCP, so the live door path (the device poll, the Contact sensor going from closed to open) runs without a
session; the test flips the sensor in that file.

What it does: it plays the edge service (POST /api/edge/observe: a thing on the table, a cat at the food bowl, a
person in the kitchen, a child in the hall), opens the simulated door (POST /api/sim/door), writes sentences to the
assistant (POST /api/assistant), and shortens deadlines and grace periods (PATCH /api/rules) so each case takes
seconds. Nothing reaches the Altice platform: actions stay dry runs, and the door is the simulated one.
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
JPEG = ("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABQODxIPDRQSEBIXFRQYHjIhHhwcHj0sLiQySUBMS0dARkVQWnNiUFVtVkVGZIhlbXd7gYKBTmCNl4x9"
        "lnN+gXz/2wBDARUXFx4aHjshITt8U0ZTfHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHz/wAARCAAQABAD"
        "ASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKB"
        "kaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZ"
        "mqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQF"
        "BgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5"
        "OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX"
        "2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDZooor5o7T/9k=")
# Brazilian Portuguese that must never reach a European Portuguese user.
BRAZILIAN = re.compile(r"\bvoc[êe]\b|\bc[âa]m[eê]ra\b|\bcamara\b|\bcaméra\b|\bcelular\b|\bcachorro\b|\busuário\b|"
                       r"\b(est[áa]|estou|estava)\s+\w+ndo\b|\bno mesa\b|\bà \d\d:|\bchegou em casa\b|"
                       r"[\u0400-\u04ff\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]", re.I)

results = []
SERVER = ""


def call(method, path, body=None, timeout=90):
    req = urllib.request.Request(SERVER + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> {e.code}: {e.read()[:200]!r}")


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""), flush=True)
    return ok


def events():
    return call("GET", "/api/state")["events"]


def wait_for(pred, timeout=15.0, step=0.5):
    """The first event that satisfies pred, waiting up to `timeout` seconds; None if none came."""
    end = time.time() + timeout
    while time.time() < end:
        hit = next((e for e in events() if pred(e)), None)
        if hit:
            return hit
        time.sleep(step)
    return None


def alert_for(rid):
    return next((e for e in events() if e["kind"] == "alert" and e.get("rule_id") == rid), None)


def sensor(text):
    out = call("POST", "/api/assistant", {"text": text})
    return out.get("sensor") if out.get("kind") == "sensor" else None


def soon(seconds=4):
    return time.strftime("%H:%M:%S", time.localtime(time.time() + seconds))


def observe(**payload):
    return call("POST", "/api/edge/observe", {"people": 0, "sightings": [], **payload})


def door():
    """Someone opens the door and closes it again."""
    call("POST", "/api/sim/door", {"open": True})
    time.sleep(0.5)
    call("POST", "/api/sim/door", {"open": False})


def phone(member, home):
    """A Family member's phone joins or leaves the home Wi-Fi (simulated)."""
    return call("POST", "/api/sim/phone", {"member": member, "home": home})


def edge_task(key, timeout=12.0):
    """Play the edge: wait until the server asks for a task of this kind (check, snapshot, photos, refresh)."""
    end = time.time() + timeout
    while time.time() < end:
        t = call("GET", "/api/edge/task")
        if t.get(key):
            return t[key]
        time.sleep(0.4)
    return None


def latest(kind, rid=None, since=0.0):
    return next((e for e in events() if e["kind"] == kind and e["ts"] >= since and (rid is None or e.get("rule_id") == rid)), None)


LIGHT = "00e038d4-0da7-45c2-b61f-f38c9ff9df82"
PLUG = "bc891629-98bc-44f7-99a8-1aa61428a9bf"
DEVICES = None


def set_contact(state):
    """The Contact sensor in the devices file: 'normal' (closed) or 'alarm' (open)."""
    d = json.loads((HERE.parent / "mcp" / "samples" / "get_home_devices.json").read_text())
    for dev in d["devices"]:
        if dev["type"] == "contactSensor":
            for c in dev["capabilities"]:
                if c.get("type") == "sensorState":
                    c["value"] = state
    DEVICES.write_text(json.dumps(d))


def start_private_server(port):
    global DEVICES
    data = Path(tempfile.mkdtemp(prefix="tt-test-"))
    DEVICES = data / "devices.json"
    set_contact("normal")
    env = {**os.environ, "TT_PORT": str(port), "TT_DATA": str(data), "TT_DEVICES_FILE": str(DEVICES),
           "TT_DOOR_POLL_S": "1", "TT_TIMINGS": "demo",
           # shorter single waits than the demo's, so the whole run takes a few minutes (presence.TIMINGS)
           "TT_TIMING_PHONE_LAG_S": "4", "TT_TIMING_LEAVING_CHECK_S": "3", "TT_TIMING_CHECK_TIMEOUT_S": "5",
           "TT_TIMING_REFRESH_S": "3"}
    env.pop("TT_AI", None)
    env.pop("TT_LIVE_ACTIONS", None)          # never: device actions stay dry runs
    proc = subprocess.Popen([sys.executable, str(HERE / "server.py")], env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state", timeout=2)
            return proc, data
        except Exception:
            time.sleep(0.5)
    proc.kill()
    raise SystemExit("the private server did not start")


def main():
    global SERVER
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", help="use this running server instead of a private one (writes into its database)")
    ap.add_argument("--port", type=int, default=8775)
    ap.add_argument("--unit", action="store_true", help="only the presence engine's unit tests (no server)")
    args = ap.parse_args()
    if args.unit:
        presence_unit()
        failed = [n for n, ok in results if not ok]
        print(f"\n{len(results) - len(failed)} of {len(results)} passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
        sys.exit(1 if failed else 0)
    proc, data = None, None
    if args.server:
        SERVER = args.server.rstrip("/")
        print(f"Using {SERVER}: test data is written into its database.")
    else:
        proc, data = start_private_server(args.port)
        SERVER = f"http://127.0.0.1:{args.port}"
        print(f"Private server on {SERVER}, data in {data}")
    try:
        run(private=proc is not None, db=(data / "home.db") if data else None)
    finally:
        if proc:
            proc.terminate()
            proc.wait(timeout=10)
    failed = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(failed)} of {len(results)} passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    sys.exit(1 if failed else 0)


def presence_unit():
    """The presence engine alone (presence.py), on a fake clock and a throwaway database: no server, no camera."""
    print("\nP. Presence engine: phones + door + cameras (fake clock, own database)")
    sys.path.insert(0, str(HERE))
    import presence as P
    from store import Store
    st = Store(Path(tempfile.mkdtemp(prefix="tt-presence-")) / "home.db")
    clock = [1_000_000.0]
    t = P.TIMINGS["demo"]
    pr = P.Presence(st, timings=t, clock=lambda: clock[0])
    st.add_thing("Filipe", "person · family")
    st.add_thing("Ana", "person · family")
    st.add_thing("Rui", "person · guest")
    later = lambda s: clock.__setitem__(0, clock[0] + s)
    cam = "Work Room"

    s = pr.evaluate()
    check("P1 new Family members' phones start home -> OCCUPIED, 2 at home", s["state"] == P.OCCUPIED and s["count"] == 2
          and s["home"] == ["Filipe", "Ana"], s["reason"])
    pr.set_phone("filipe", False)
    pr.set_phone("ana", False)
    s = pr.evaluate()
    check("P2 both phones leave the Wi-Fi, nobody seen -> EMPTY, 0", s["state"] == P.EMPTY and s["count"] == 0, s["reason"])
    for _ in range(t["unknown_runs"]):
        later(1)
        pr.analysis(cam, [{"identity": "unknown"}])
    s = pr.evaluate()
    check("P3 phones away, a face that matches nobody -> UNSURE, 1 at home", s["state"] == P.UNSURE and s["count"] == 1
          and s["unknown"] == 1, s["reason"])
    check("P4 ... and the security run counts consecutive analyses", pr.run(cam, "unknown")[0] == t["unknown_runs"],
          str(pr.run(cam, "unknown")))
    check("P5 ... and the state rests on the camera: a refresh is wanted after refresh_s", s["relies_on_camera"]
          and not pr.wants_refresh(cam) and (later(t["refresh_s"]) or pr.wants_refresh(cam)))
    pr.analysis(cam, [])
    check("P6 the camera looks again and sees nobody -> EMPTY, and the run resets",
          pr.evaluate()["state"] == P.EMPTY and pr.run(cam, "unknown")[0] == 0)
    pr.analysis(cam, [{"identity": "filipe"}])
    s = pr.evaluate()
    check("P7 Filipe's face, his phone away -> OCCUPIED: Filipe (the face is direct evidence)", s["state"] == P.OCCUPIED
          and s["home"] == ["Filipe"], s["reason"])
    later(2)
    pr.analysis(cam, [{"identity": "not_visible"}])
    s = pr.evaluate()
    check("P8 then a person with no face visible -> still 1: it can be Filipe", s["count"] == 1, s["reason"])
    check("P9 a family face never starts a security run", pr.run(cam, "no_face")[0] == 0 and pr.run(cam, "unknown")[0] == 0)
    later(t["face_recent_s"] + 1)
    s = pr.evaluate()
    check("P10 Filipe still and unseen for face_recent_s, phone away -> EMPTY (hence the refresh analyses)",
          s["state"] == P.EMPTY, s["reason"])
    pr.set_phone("ana", True)
    pr.analysis(cam, [{"identity": "rui"}, {"identity": "not_visible"}])
    s = pr.evaluate()
    check("P11 Ana's phone home, Rui (guest) seen, one person face not visible -> 2 (the faceless one may be Ana)",
          s["count"] == 2 and set(s["home"]) == {"Ana", "Rui"}, s["reason"])
    pr.door(True)
    later(2)
    pr.door(False)
    s = pr.evaluate()
    check("P12 the door opens then closes -> LEAVING", s["state"] == P.LEAVING, s["reason"])
    opened = clock[0] - 2
    later(3)
    pr.set_phone("ana", False)
    check("P13 Ana's phone leaves after the door -> left_since says Ana; nobody arrived",
          pr.left_since(opened - 5) == ["Ana"] and pr.arrived_since(opened - 5) == [])
    check("P13b while LEAVING the engine asks the camera for refresh analyses", pr.wants_refresh(cam))
    pr.analysis(cam, [], forced=True)                    # the refresh: the camera sees nobody
    later(t["leaving_check_s"])
    s = pr.evaluate()
    check("P14 LEAVING ends after leaving_check_s -> EMPTY", s["state"] == P.EMPTY, s["reason"])
    t0 = clock[0]
    pr.set_phone("filipe", True)
    check("P15 Filipe's phone joins -> an arrival", pr.arrived_since(t0) == ["Filipe"] and pr.evaluate()["state"] == P.OCCUPIED)
    later(t["stale_s"] + 1)
    s = pr.evaluate()
    check("P16 a phone home, nobody seen and the door unused for stale_s -> UNSURE (a phone left at home?)",
          s["state"] == P.UNSURE and s["count"] == 1, s["reason"])
    again = P.Presence(st, timings=t, clock=lambda: clock[0])
    check("P17 a new engine on the same database (a restart) keeps the state and the count",
          again.s["state"] == P.UNSURE and again.s["count"] == 1 and again.phones()["ana"]["home"] is False)
    moves = [e["text"].split(".")[0] for e in st.events(100) if e["kind"] == "presence"][::-1]
    check("P18 every change of state is an event", len(moves) >= 8 and moves[0].startswith("Home: started → OCCUPIED"),
          " | ".join(moves))
    check("P19 production timings are minutes, demo timings seconds", P.TIMINGS["prod"]["leaving_check_s"] >= 60
          and P.TIMINGS["prod"]["face_recent_s"] >= 600 and P.TIMINGS["demo"]["leaving_check_s"] <= 30)


def run(private, db):
    presence_unit()
    st = call("GET", "/api/state")
    engine = st["settings"]["llm"]
    print(f"Assistant engine: {engine}; device actions live: {st['settings']['live_actions']}\n")
    if st["settings"]["live_actions"]:
        raise SystemExit("This server has TT_LIVE_ACTIONS=1: refusing to fire test alerts that would act on the home.")
    check("state carries the door", "door" in st, json.dumps(st.get("door")))
    for q, want in [("Onde está o livro?", "Ainda não conheço o livro"), ("Where is my book?", "don't know your book")]:
        out = call("POST", "/api/assistant", {"text": q})
        check(f"“{q}” with no book registered -> says so and how to add it", want in out.get("answer", "")
              and "Things" in out.get("answer", ""), out.get("answer", ""))
    book = call("POST", "/api/things", {"name": "Book", "description": "yellow book"})["id"]
    keys = call("POST", "/api/things", {"name": "Keys", "description": "keys"})["id"]
    wallet = call("POST", "/api/things", {"name": "Wallet", "description": "wallet"})["id"]

    # ------------------------------------------------------------------ C. routing
    print("\nC. Routing: a question is answered, a request becomes a sensor")
    for text, want in [("Quando vi o livro", "answer"), ("When did I last see the book", "answer"),
                       ("Where is my book", "answer"), ("Onde está o livro", "answer"),
                       ("Tell me where my keys are", "answer"),
                       ("When the door opens, turn the light red", "sensor")]:
        out = call("POST", "/api/assistant", {"text": text})
        check(f"“{text}” -> {want}", out["kind"] == want, out["kind"] + (": " + out.get("answer", "")[:70] if out["kind"] == "answer" else ""))
        if out["kind"] == "sensor":
            call("DELETE", f"/api/rules/{out['sensor']['id']}")

    filipe = call("POST", "/api/things", {"name": "Filipe", "description": "person · family"})["id"]
    pres = call("GET", "/api/presence")
    check("a new Family member's phone starts on the home Wi-Fi -> OCCUPIED", pres["state"] == "OCCUPIED"
          and pres["home"] == ["Filipe"] and "presence" in call("GET", "/api/state"), pres["reason"])

    # ------------------------------------------------------------------ A0. the live door, read through the device poll
    if private:
        print("\nA0. The real door: the Contact sensor read every second through the device poll (a file, not the MCP)")
        end = time.time() + 10
        while time.time() < end and not call("GET", "/api/state")["door"].get("live"):
            time.sleep(0.5)
        d = call("GET", "/api/state")["door"]
        check("device poll is live and the door reads closed", d.get("live") and d.get("open") is False, json.dumps(d))
        r = sensor("Avisa-me se eu sair de casa sem o livro")
        check("the sentence of the lab test -> leave_without, light red", r and r["kind"] == "leave_without"
              and r["action"] == "light_red", r and f"{r['kind']}, action {r['action']}")
        if r:
            observe(people=1, persons=[{"identity": filipe}],
                    sightings=[{"thing_id": book, "place": "table", "crop_b64": JPEG, "note": "test"}])
            set_contact("alarm")
            door_ev = wait_for(lambda e: e["kind"] == "door" and e.get("open") and not e.get("sim"), timeout=8)
            check("the real sensor opens -> a door event (not simulated)", door_ev, door_ev and door_ev["text"])
            check("… and no alert while the door is open: the check starts when it closes", not alert_for(r["id"]))
            set_contact("normal")
            closed = wait_for(lambda e: e["kind"] == "door" and e.get("open") is False and not e.get("sim"), timeout=8)
            check("the real sensor closes -> a door event, and presence says LEAVING", closed
                  and call("GET", "/api/presence")["state"] == "LEAVING", closed and closed["text"])
            phone(filipe, False)
            chk = edge_task("check")
            check("Filipe's phone leaves -> the server asks the edge for an active check of the book",
                  chk and chk["thing_id"] == book and chk["frames"] >= 3, json.dumps(chk))
            if chk:
                call("POST", "/api/edge/check", {"id": chk["id"], "seen": True, "place": "table", "score": 0.71, "frames": 3,
                                                 "crop_b64": JPEG})
            a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r["id"], timeout=10)
            check("… seen on the table -> the alert, with the book's photo and the check's picture",
                  a and a.get("crop") and a.get("picture") and a.get("place") == "table", a and a["text"])
            calls = (a or {}).get("action", {}).get("calls", [])
            want = [{"type": "power", "value": "on"}, {"type": "color_rgb", "redValue": 255, "greenValue": 0, "blueValue": 0}]
            check("… and the red light: the exact MCP calls, dry run", [c["arguments"].get("body") for c in calls] == want
                  and all(c["tool"] == "update_device_capabilities" and c["arguments"].get("deviceId") == LIGHT for c in calls)
                  and not a["action"]["live"] and a["action"]["result"] == "dry run: not sent",
                  "; ".join(f"{c['tool']} {json.dumps(c['arguments'])}" for c in calls))
            phone(filipe, True)
            call("DELETE", f"/api/rules/{r['id']}")

    # ------------------------------------------------------------------ A. leave home without
    print("\nA. “Tell me if I leave home without my book”: on the door closing, if someone left, an active check")
    r_en = sensor("Tell me if I leave home without my book")
    check("EN sentence -> leave_without on the book", r_en and r_en["kind"] == "leave_without" and r_en["thing_id"] == book
          and r_en.get("grace_s") == 60, r_en and f"{r_en['kind']}, thing {r_en['thing_id']!r}, grace {r_en.get('grace_s')}")
    r_pt = sensor("Avisa-me se eu sair de casa sem o livro")
    check("PT sentence -> leave_without on the book", r_pt and r_pt["kind"] == "leave_without" and r_pt["thing_id"] == book,
          r_pt and f"{r_pt['kind']}, thing {r_pt['thing_id']!r}, title “{r_pt['title']}”")
    if r_pt:
        call("DELETE", f"/api/rules/{r_pt['id']}")
    r_ko = sensor("Tell me if I forget my keys")
    check("“forget my keys” -> leave_without on the keys", r_ko and r_ko["kind"] == "leave_without" and r_ko["thing_id"] == keys)
    if r_ko:
        call("DELETE", f"/api/rules/{r_ko['id']}")

    def leave_case(phone_after=None, answer=None):
        """A fresh book rule; the book on the table (an hour ago, when the test owns the database); the door opens
        and closes; then the phone change and the edge's answer to the check. Returns (rule, check task)."""
        r = sensor("Tell me if I leave home without my book")
        observe(sightings=[{"thing_id": book, "place": "table", "crop_b64": JPEG, "note": "test"}])
        if db:
            with sqlite3.connect(db) as c:
                c.execute("UPDATE sightings SET ts = ts - 3600 WHERE thing_id = ?", (book,))
        door()
        if phone_after is not None:
            phone(filipe, phone_after)
        chk = edge_task("check", timeout=6) if answer is not None or phone_after is False else None
        if chk and answer:
            call("POST", "/api/edge/check", {"id": chk["id"], **answer})
        return r, chk

    if r_en:
        call("DELETE", f"/api/rules/{r_en['id']}")
    r, chk = leave_case(phone_after=False, answer={"seen": True, "place": "table", "score": 0.7, "frames": 3, "crop_b64": JPEG})
    a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r["id"], timeout=10)
    check("Filipe leaves, the book is still on the table " + ("(last seen an hour ago)" if db else "") + " -> alert",
          a and "still on the table" in a["text"] and "Filipe left" in a.get("evidence", ""), a and f"{a['text']} | {a.get('evidence')}")
    check("the door's closing and opening are in the activity", any(e["kind"] == "door" and e.get("open") for e in events())
          and any(e["kind"] == "door" and e.get("open") is False for e in events()))
    call("DELETE", f"/api/rules/{r['id']}")
    phone(filipe, True)

    r, chk = leave_case(phone_after=False, answer={"seen": False, "frames": 3, "score": 0.31})
    u = wait_for(lambda e: e["kind"] == "unsure" and e.get("rule_id") == r["id"], timeout=10)
    check("Filipe leaves, the book is not visible -> “unsure” in the activity, no alert, no alarm",
          u and not alert_for(r["id"]) and not call("GET", "/api/state")["alarm"].get("on"), u and u["text"])
    call("DELETE", f"/api/rules/{r['id']}")
    phone(filipe, True)

    r, chk = leave_case(phone_after=False)
    u = wait_for(lambda e: e["kind"] == "unsure" and e.get("rule_id") == r["id"], timeout=12)
    check("Filipe leaves, the camera service never answers the check -> “unsure”, no alert", chk and u
          and not alert_for(r["id"]), u and u["text"])
    call("DELETE", f"/api/rules/{r['id']}")

    r, chk = leave_case(phone_after=True)
    i = wait_for(lambda e: e["kind"] == "info" and e.get("rule_id") == r["id"] and "arrived" in e["text"], timeout=8)
    check("Filipe's phone joins as the door closes (an arrival) -> no check, no alert", i and not alert_for(r["id"]),
          i and i["text"])
    call("DELETE", f"/api/rules/{r['id']}")

    time.sleep(6)                     # the arrival above is more than 5 s before the next opening
    r, chk = leave_case()
    i = wait_for(lambda e: e["kind"] == "info" and e.get("rule_id") == r["id"] and "nobody left" in e["text"], timeout=10)
    check("the door opens and closes, no phone leaves -> “nobody left”, no check, no alert", i and not alert_for(r["id"])
          and not call("GET", "/api/edge/task").get("check"), i and i["text"])
    call("DELETE", f"/api/rules/{r['id']}")

    r_k = sensor("Tell me if I leave home without my keys")
    if r_k:
        observe(camera="Entrance", sightings=[{"thing_id": keys, "place": "room", "crop_b64": JPEG, "note": "test"}])
        door()
        ok = wait_for(lambda e: e["kind"] == "ok" and e.get("rule_id") == r_k["id"], timeout=12)
        check("keys seen at the entrance as the door opens -> no alert (they went out)", ok and not alert_for(r_k["id"]),
              ok and ok["text"])
        call("DELETE", f"/api/rules/{r_k['id']}")

    r_w = sensor("Tell me if I leave home without my wallet")
    if r_w:
        door()
        info = wait_for(lambda e: e["kind"] == "info" and e.get("rule_id") == r_w["id"], timeout=12)
        check("wallet never seen -> no alert, a line in the activity", info and not alert_for(r_w["id"]), info and info["text"])
        call("DELETE", f"/api/rules/{r_w['id']}")

    # ------------------------------------------------------------------ S. someone who isn't Family
    print("\nS. “Sound the alarm when someone who isn't Family comes in”: face identities from the edge")
    sec = call("POST", "/api/rules", {"sentence": "Sound the alarm when someone who isn't Family comes in", "title": "Home Security"})
    check("the app's suggestion -> someone_arrives, unknown, alarm", sec["kind"] == "someone_arrives" and sec.get("unknown")
          and sec.get("alarm"), f"{sec['kind']} unknown={sec.get('unknown')} alarm={sec.get('alarm')}")
    call("PATCH", f"/api/rules/{sec['id']}", {"cooldown_s": 0})
    phone(filipe, False)
    observe(people=0, persons=[])
    for i in range(3):
        observe(people=1, persons=[{"identity": "unknown", "score": 0.14, "crop_b64": JPEG}])
        time.sleep(0.4)
        if i == 1:
            time.sleep(2.5)
            check("an unknown face on 2 analyses -> no alert yet", not alert_for(sec["id"]))
    a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == sec["id"], timeout=8)
    check("an unknown face on 3 analyses, the family away -> alert, alarm on, police suggested, the person's picture",
          a and (a.get("alarm") or {}).get("state") == "on" and (a.get("suggestion") or {}).get("number") == "112"
          and a.get("picture") and call("GET", "/api/state")["alarm"].get("on"), a and f"{a['text']} | {a.get('evidence')}")
    if a:
        out = call("POST", f"/api/alerts/{a['id']}/alarm-off")
        st = call("GET", "/api/state")
        check("“Turn off the alarm” -> the alert's alarm is off, the simulated alarm is off, an event, no MCP call",
              out["alert"]["alarm"]["state"] == "off" and not st["alarm"].get("on") and out["event"]["kind"] == "alarm"
              and not out["event"]["action"]["calls"] and "never called" in out["event"]["action"]["result"],
              out["event"]["text"])
    observe(people=0, persons=[])
    for _ in range(3):
        observe(people=1, persons=[{"identity": "not_visible"}])
        time.sleep(0.4)
    a2 = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == sec["id"] and e.get("ask"), timeout=8)
    check("a person whose face is not seen, the family away -> “Someone is home”, it asks, no alarm",
          a2 and not a2.get("alarm") and a2["ask"][0]["act"] == "alarm_on" and not a2.get("suggestion"), a2 and a2["text"])
    if a2:
        out = call("POST", f"/api/alerts/{a2['id']}/act", {"act": "alarm_on"})
        check("… “Sound the alarm?” Yes -> the simulated alarm sounds, the question is answered",
              out["alert"]["alarm"]["state"] == "on" and out["alert"]["ask"][0]["state"] == "done"
              and call("GET", "/api/state")["alarm"].get("on"), out["event"]["text"])
        call("POST", f"/api/alerts/{a2['id']}/alarm-off")
    observe(people=0, persons=[])
    n_before = len([e for e in events() if e["kind"] == "alert" and e.get("rule_id") == sec["id"]])
    for _ in range(3):
        observe(people=1, persons=[{"identity": filipe, "score": 0.52}])
        time.sleep(0.4)
    time.sleep(3)
    check("Filipe's face on 3 analyses, his phone away -> no alert (a Family member never counts), Filipe home",
          len([e for e in events() if e["kind"] == "alert" and e.get("rule_id") == sec["id"]]) == n_before
          and call("GET", "/api/presence")["home"] == ["Filipe"])
    phone(filipe, True)
    for _ in range(3):
        observe(people=1, persons=[{"identity": "unknown", "score": 0.2, "crop_b64": JPEG}])
        time.sleep(0.4)
    a3 = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == sec["id"] and "at home with" in e["text"], timeout=8)
    check("an unknown face while Filipe is home -> a message, no alarm, no police", a3 and not a3.get("alarm")
          and not a3.get("suggestion") and len([e for e in events() if e["kind"] == "alert" and e.get("rule_id") == sec["id"]]) == n_before + 1,
          a3 and a3["text"])
    observe(people=0, persons=[])
    call("DELETE", f"/api/rules/{sec['id']}")

    # ------------------------------------------------------------------ R. the refresh for someone sitting still
    print("\nR. The state rests on the camera alone: the edge is asked to look again without motion")
    phone(filipe, False)
    observe(people=1, persons=[{"identity": filipe}])
    p = call("GET", "/api/presence")
    check("phone away, Filipe's face seen -> OCCUPIED by the camera alone", p["state"] == "OCCUPIED" and p["relies_on_camera"],
          p["reason"])
    check("… no refresh right after an analysis", not call("GET", "/api/edge/task")["refresh"])
    time.sleep(3.5)
    check("… a refresh is asked after refresh_s", call("GET", "/api/edge/task")["refresh"])
    observe(people=1, persons=[{"identity": filipe}], forced=True)
    check("… and the forced analysis answers it", not call("GET", "/api/edge/task")["refresh"])
    phone(filipe, True)
    observe(people=0, persons=[])

    # ------------------------------------------------------------------ E. nobody home: devices on, the door open
    print("\nE. Nobody home: one alert with the devices to turn off and the door banner")
    r1 = sensor("If nobody is home and something is on, ask me to turn it off")
    r2 = sensor("If the door is left open when nobody is home, sound the alarm and tell me")
    check("the two sentences -> nobody_devices_on and door_open_nobody (alarm)", r1 and r2 and r1["kind"] == "nobody_devices_on"
          and r2["kind"] == "door_open_nobody" and r2.get("alarm"), f"{r1 and r1['kind']}, {r2 and r2['kind']}")
    if r1 and r2:
        call("PATCH", f"/api/rules/{r1['id']}", {"grace_s": 3})
        call("PATCH", f"/api/rules/{r2['id']}", {"grace_s": 1})
        devs = call("GET", "/api/state")["tt_devices"]
        for d in devs:
            call("POST", f"/api/tt-devices/{d['id']}/power", {"on": True})
        if private:
            set_contact("alarm")
            wait_for(lambda e: e["kind"] == "door" and e.get("open") and not e.get("sim"), timeout=8)
        else:
            call("POST", "/api/sim/door", {"open": True})
        t0 = time.time()
        time.sleep(1.5)
        check("the door open, Filipe's phone home -> no alert", not alert_for(r1["id"]) and not alert_for(r2["id"]))
        phone(filipe, False)
        observe(people=0, persons=[])
        check("Filipe's phone leaves, the camera sees nobody -> EMPTY", call("GET", "/api/presence")["state"] == "EMPTY")
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r1["id"], timeout=10)
        time.sleep(2.5)
        own = [e for e in events() if e["kind"] == "alert" and e["ts"] >= t0 and e.get("rule_id") in (r1["id"], r2["id"])]
        check("one alert: the devices to turn off, the door banner, the alarm on", a and len(own) == 1
              and len(a.get("cards", [])) == len(devs) and (a.get("door") or {}).get("open")
              and (a.get("alarm") or {}).get("state") == "on" and r2["id"] in a.get("rule_ids", []),
              a and f"{a['title']}: {a['text']} | {len(own)} alert(s)")
        snap = edge_task("snapshot", timeout=5)
        if snap:
            call("POST", "/api/edge/snapshot", {"id": snap["id"], "jpeg_b64": JPEG})
        check("the server asks the edge for a picture of the empty room, and the alert gets it",
              snap and (call("GET", "/api/state")["events"] and next(e for e in events() if a and e["id"] == a["id"]).get("picture")))
        if a:
            out = call("POST", f"/api/alerts/{a['id']}/act", {"device": PLUG, "on": False})
            plug = next(d for d in call("GET", "/api/state")["tt_devices"] if d["id"] == PLUG)
            calls = out["event"].get("action", {}).get("calls", [])
            check("“Turn off the lights?” Yes -> plug_off through actions.run (dry run), the card and the plug off",
                  not plug["on"] and next(c for c in out["alert"]["cards"] if c["device"] == PLUG)["state"] == "off"
                  and calls and calls[0]["arguments"] == {"deviceId": PLUG, "body": {"type": "power", "value": "off"}}
                  and calls[0]["result"] == "dry run: not sent", out["event"]["text"])
            out = call("POST", f"/api/alerts/{a['id']}/act", {"device": "ac", "on": False})
            check("“Turn off the AC?” Yes -> the integration off (simulated), both cards off",
                  all(c["state"] == "off" for c in out["alert"]["cards"]) and not next(
                      d for d in call("GET", "/api/state")["tt_devices"] if d["id"] == "ac")["on"], out["event"]["text"])
            out = call("POST", f"/api/alerts/{a['id']}/alarm-off")
            check("“Turn off the alarm” on the door banner -> off", out["alert"]["alarm"]["state"] == "off")
        if private:
            set_contact("normal")
        else:
            call("POST", "/api/sim/door", {"open": False})
        phone(filipe, True)
        call("DELETE", f"/api/rules/{r1['id']}")
        call("DELETE", f"/api/rules/{r2['id']}")

    # ------------------------------------------------------------------ H. picked up, taken, moved
    print("\nH. Picked up, taken, moved: the edge's “in hand” sightings")
    observe(people=0, persons=[], sightings=[{"thing_id": book, "place": "desk", "crop_b64": JPEG, "note": "test"}])
    t0 = time.time()
    observe(people=1, persons=[{"identity": filipe}],
            sightings=[{"thing_id": book, "place": "desk", "in_hand": True, "by": filipe, "note": "test"}])
    h = latest("handled", since=t0)
    check("the book's box on Filipe's box -> “Book picked up by Filipe”", h and h["text"] == "Book picked up by Filipe.",
          h and h["text"])
    for i in range(3):
        observe(people=1 if i == 0 else 0, persons=[{"identity": filipe}] if i == 0 else [])
    h = latest("handled", since=t0)
    check("then missing from the desk for 3 analyses -> “Book taken by Filipe”", h and h["text"].startswith("Book taken by Filipe"),
          h and h["text"])
    observe(people=0, persons=[], sightings=[{"thing_id": book, "place": "shelf", "crop_b64": JPEG, "note": "test"}])
    h = latest("handled", since=t0)
    check("then seen on the shelf -> “Book moved to the shelf”", h and h["text"].startswith("Book moved to the shelf"),
          h and h["text"])
    t1 = time.time()
    observe(people=1, persons=[{"identity": "not_visible"}],
            sightings=[{"thing_id": book, "place": "shelf", "in_hand": True, "note": "test"}])
    observe(people=0, persons=[], sightings=[{"thing_id": book, "place": "shelf", "crop_b64": JPEG, "note": "test"}])
    check("picked up by someone whose face is not seen, then put back -> “by a person”, “put back”",
          [e["text"] for e in events() if e["kind"] == "handled" and e["ts"] >= t1][::-1]
          == ["Book picked up by a person.", "Book put back on the shelf."])

    # ------------------------------------------------------------------ PH. photos -> fingerprint (the edge's task)
    print("\nPH. Phone photos: the server queues a fingerprint task for the edge")
    glasses = call("POST", "/api/things", {"name": "Glasses", "description": "black glasses"})["id"]
    out = call("POST", f"/api/things/{glasses}/photos", {"photos_b64": [JPEG, JPEG, JPEG]})
    task = edge_task("photos", timeout=3)
    check("3 photos -> a photos task with the files and the description as the query", out.get("queued") and task
          and task["thing_id"] == glasses and len(task["files"]) == 3 and task["query"] == "black glasses", json.dumps(task)[:160])
    if task:
        vec = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
        call("POST", "/api/edge/enrol", {"thing_id": glasses, "source": "photos", "done": True, "found": 3, "vectors": vec,
                                         "model": "facebook/dinov2-small"})
        fp = call("GET", "/api/edge/fingerprints").get(glasses)
        t = next(x for x in call("GET", "/api/state")["things"] if x["id"] == glasses)
        check("the edge's vectors -> the fingerprint (3 vectors, DINOv2), the task done", fp and len(fp["vectors"]) == 3
              and t["fingerprint"]["model"] == "facebook/dinov2-small" and not call("GET", "/api/edge/task")["photos"],
              json.dumps(t["fingerprint"])[:160])
    face_photo = HERE.parent / "video" / "public" / "phone" / "person" / "joao.jpg"
    if face_photo.exists() and (HERE / "models" / "face_detection_yunet_2023mar.onnx").exists():
        ana = call("POST", "/api/things", {"name": "Ana", "description": "person · family"})["id"]
        b64 = __import__("base64").b64encode(face_photo.read_bytes()).decode()
        call("POST", f"/api/things/{ana}/photos", {"photos_b64": [b64]})
        t = next(x for x in call("GET", "/api/state")["things"] if x["id"] == ana)
        check("a person's photo -> face templates on the home device, no fingerprint task", t["fingerprint"].get("faces") == 1
              and not call("GET", "/api/edge/task")["photos"], json.dumps(t["fingerprint"])[:160])
    else:
        print("SKIP  a person's photo -> face templates (no photo or no face models here)")

    # ------------------------------------------------------------------ B. deadlines
    print("\nB. Deadlines: not_by and nobody_by")
    r = sensor("Tell me if the dog has not been at the food bowl by 20:00")
    check("“dog … food bowl by 20:00” -> not_by", r and r["kind"] == "not_by" and r.get("who") == "dog"
          and r.get("by") == "20:00" and "bowl" in r.get("place", "").lower(), r and f"{r['kind']} {r.get('who')} {r.get('place')!r} {r.get('by')}")
    if r:
        call("PATCH", f"/api/rules/{r['id']}", {"by": soon()})
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r["id"], timeout=15)
        check("no dog at the food bowl by the deadline -> alert", a, a and a.get("evidence"))
        call("DELETE", f"/api/rules/{r['id']}")

    r = sensor("Tell me if the cat has not been at the food bowl by 20:00")
    if r:
        observe(camera="Kitchen", beings=[{"who": "cat", "place": "Food bowl"}])
        call("PATCH", f"/api/rules/{r['id']}", {"by": soon()})
        ok = wait_for(lambda e: e["kind"] == "ok" and e.get("rule_id") == r["id"], timeout=15)
        time.sleep(5)
        check("cat seen at the food bowl before the deadline -> no alert", ok and not alert_for(r["id"]), ok and ok["text"])
        call("DELETE", f"/api/rules/{r['id']}")

    r = sensor("Tell me if the cat has not been at the water bowl in 12 hours")
    check("“cat … water bowl in 12 hours” -> not_by, 12 h window", r and r["kind"] == "not_by" and r.get("who") == "cat"
          and r.get("within_s") == 43200, r and f"{r['kind']} {r.get('who')} {r.get('place')!r} within {r.get('within_s')}")
    if r:
        call("PATCH", f"/api/rules/{r['id']}", {"within_s": 3})
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r["id"], timeout=15)
        check("cat not at the water bowl for the window -> alert", a, a and a.get("evidence"))
        call("DELETE", f"/api/rules/{r['id']}")

    for text in ("Tell me if nobody has been in the kitchen by midday", "Avisa-me se ninguém estiver na cozinha até ao meio-dia"):
        r = sensor(text)
        check(f"“{text}” -> nobody_by", r and r["kind"] == "nobody_by" and r.get("by") == "12:00"
              and r.get("from") == "06:00" and "kitchen" in r.get("place", "").lower(),
              r and f"{r['kind']} {r.get('place')!r} {r.get('from')}-{r.get('by')}")
        if r:
            call("DELETE", f"/api/rules/{r['id']}")

    r = sensor("Tell me if nobody has been in the kitchen by midday")
    if r:
        call("PATCH", f"/api/rules/{r['id']}", {"from": "00:00", "by": soon()})
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r["id"], timeout=15)
        check("nobody in the kitchen (only the cat) by the deadline -> alert", a, a and a.get("evidence"))
        call("DELETE", f"/api/rules/{r['id']}")
    r = sensor("Tell me if nobody has been in the kitchen by midday")
    if r:
        observe(camera="Kitchen", people=1, beings=[{"who": "person", "place": "room"}])
        call("PATCH", f"/api/rules/{r['id']}", {"from": "00:00", "by": soon()})
        ok = wait_for(lambda e: e["kind"] == "ok" and e.get("rule_id") == r["id"], timeout=15)
        time.sleep(5)
        check("a person in the kitchen before the deadline -> no alert", ok and not alert_for(r["id"]), ok and ok["text"])
        call("DELETE", f"/api/rules/{r['id']}")

    # ------------------------------------------------------------------ B. suggestions that really fire
    print("\nB. Suggestions for who lives here compile to rules that fire")
    for _ in range(3):   # the camera sees a dog clearly in 3 analyses
        observe(profile={"dog": 0.9, "cat": 0.0, "child": 0.0}, beings=[])
    call("POST", "/api/profile", {"kind": "older_alone"})
    for _ in range(3):
        observe(profile={"dog": 0.0, "cat": 0.0, "child": 0.8}, beings=[])
    sugg = [e for e in events() if e["kind"] == "suggest"]
    by_profile = {}
    for e in sugg:
        by_profile.setdefault(e.get("profile"), []).append(e)
    check("dog seen -> 2 suggestions", len(by_profile.get("dog", [])) == 2, "; ".join(e["sentence"] for e in by_profile.get("dog", [])))
    check("older person living alone (declared) -> 1 suggestion", len(by_profile.get("older_alone", [])) == 1,
          "; ".join(e["sentence"] for e in by_profile.get("older_alone", [])))
    check("child seen -> 1 suggestion", len(by_profile.get("child", [])) == 1,
          "; ".join(e["sentence"] for e in by_profile.get("child", [])))
    rules = {}
    for e in sugg:
        s = sensor(e["sentence"])     # as the app does when the user taps a suggestion
        rules[e["sentence"]] = s
        want = e["rule"]["kind"]
        fields = {k: s.get(k) for k in ("who", "place", "by", "from", "within_s") if s and s.get(k)}
        check(f"suggestion “{e['sentence']}” -> {want}", s and s["kind"] == want and s["kind"] != "seen_in", json.dumps(fields))
    food = next((s for t, s in rules.items() if "dog" in t and "by 20:00" in t), None)
    if food:
        call("PATCH", f"/api/rules/{food['id']}", {"by": soon()})
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == food["id"], timeout=15)
        check("suggested dog-food sensor fires at its deadline", a, a and a.get("evidence"))
    child = next((s for t, s in rules.items() if "child" in t), None)
    if child:
        observe(camera="Hall", beings=[{"who": "child", "place": "room"}])
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == child["id"], timeout=10)
        check("suggested child sensor fires when a child arrives, with no photo", a and not a.get("crop"), a and a.get("evidence"))
    older = next((s for t, s in rules.items() if "nobody" in t.lower()), None)
    if older:   # a person was in the kitchen earlier in this test: the window starts now
        call("PATCH", f"/api/rules/{older['id']}", {"from": soon(0), "by": soon(4)})
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == older["id"], timeout=15)
        check("suggested living-alone sensor fires when nobody was seen", a, a and a.get("evidence"))

    # ------------------------------------------------------------------ C. European Portuguese
    print("\nC. Answers in European Portuguese")
    sys.path.insert(0, str(HERE))
    from brain import pt_pt
    for br, want in [("Você deixou o livro na mesa, a câmera viu.", "Deixaste o livro na mesa, a câmara viu."),
                     ("Hoje, à 17:14, alguém chegou em casa e o livro está no mesa.",
                      "Hoje, às 17:14, alguém chegou a casa e o livro está na mesa."),
                     ("Estou procurando o seu livro no celular.", "Estou a procurar o seu livro no telemóvel."),
                     ("Você não tem o seu livro?", "Não tens o teu livro?")]:
        got = pt_pt(br)
        check(f"pt_pt(“{br}”)", got == want, got)
    if engine != "local":
        print("SKIP  answers of the local model: it is not running (the assistant uses " + engine + ")")
        return
    for q in ("Onde está o livro?", "Quando vi o livro", "Onde estão as chaves?", "O que viu a câmara hoje?",
              "Onde está a carteira?", "Viste o meu telemóvel?"):
        out = call("POST", "/api/assistant", {"text": q})
        ans = out.get("answer", "")
        bad = BRAZILIAN.search(ans)
        check(f"“{q}” answered in PT-PT", out["kind"] == "answer" and ans and not bad,
              ans[:110] + (f"  [Brazilian: {bad.group(0)}]" if bad else ""))


if __name__ == "__main__":
    main()
