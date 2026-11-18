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


LIGHT = "00e038d4-0da7-45c2-b61f-f38c9ff9df82"
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
           "TT_DOOR_POLL_S": "1"}
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
    args = ap.parse_args()
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


def run(private, db):
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
            observe(sightings=[{"thing_id": book, "place": "table", "crop_b64": JPEG, "note": "test"}])
            set_contact("alarm")
            a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r["id"], timeout=15)
            door_ev = next((e for e in events() if e["kind"] == "door" and e.get("open") and not e.get("sim")), None)
            check("the real sensor opens -> a door event (not simulated)", door_ev, door_ev and door_ev["text"])
            check("… and the alert, with the book's photo", a and a.get("crop"), a and a["text"])
            calls = (a or {}).get("action", {}).get("calls", [])
            want = [{"type": "power", "value": "on"}, {"type": "color_rgb", "redValue": 255, "greenValue": 0, "blueValue": 0}]
            check("… and the red light: the exact MCP calls, dry run", [c["arguments"].get("body") for c in calls] == want
                  and all(c["tool"] == "update_device_capabilities" and c["arguments"].get("deviceId") == LIGHT for c in calls)
                  and not a["action"]["live"] and a["action"]["result"] == "dry run: not sent",
                  "; ".join(f"{c['tool']} {json.dumps(c['arguments'])}" for c in calls))
            set_contact("normal")
            closed = wait_for(lambda e: e["kind"] == "door" and e.get("open") is False and not e.get("sim"), timeout=8)
            check("the real sensor closes -> a door event", closed, closed and closed["text"])
            call("DELETE", f"/api/rules/{r['id']}")

    # ------------------------------------------------------------------ A. leave home without
    print("\nA. “Tell me if I leave home without my book”: fires when the door opens and the book is still at home")
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

    if r_en:
        observe(sightings=[{"thing_id": book, "place": "table", "crop_b64": JPEG, "note": "test"}])
        if db:   # the camera saw it an hour ago and the room has been quiet since: it must still count as at home
            with sqlite3.connect(db) as c:
                c.execute("UPDATE sightings SET ts = ts - 3600 WHERE thing_id = ?", (book,))
        call("PATCH", f"/api/rules/{r_en['id']}", {"grace_s": 2})
        door()
        a = wait_for(lambda e: e["kind"] == "alert" and e.get("rule_id") == r_en["id"], timeout=12)
        check("door opens, book last seen on the table " + ("an hour ago" if db else "just now") + " -> alert",
              a, a and a["text"])
        check("the alert carries the book's photo and its last place", a and a.get("crop") and a.get("place") == "table",
              a and f"crop {a.get('crop')}, place {a.get('place')}, room {a.get('room')}")
        check("the door opening is in the activity", any(e["kind"] == "door" and e.get("open") for e in events()))
        call("DELETE", f"/api/rules/{r_en['id']}")

    r_k = sensor("Tell me if I leave home without my keys")
    if r_k:
        call("PATCH", f"/api/rules/{r_k['id']}", {"grace_s": 2})
        observe(camera="Entrance", sightings=[{"thing_id": keys, "place": "room", "crop_b64": JPEG, "note": "test"}])
        door()
        ok = wait_for(lambda e: e["kind"] == "ok" and e.get("rule_id") == r_k["id"], timeout=12)
        check("keys seen at the entrance as the door opens -> no alert (they went out)", ok and not alert_for(r_k["id"]),
              ok and ok["text"])
        call("DELETE", f"/api/rules/{r_k['id']}")

    r_w = sensor("Tell me if I leave home without my wallet")
    if r_w:
        call("PATCH", f"/api/rules/{r_w['id']}", {"grace_s": 2})
        door()
        info = wait_for(lambda e: e["kind"] == "info" and e.get("rule_id") == r_w["id"], timeout=12)
        check("wallet never seen -> no alert, a line in the activity", info and not alert_for(r_w["id"]), info and info["text"])
        call("DELETE", f"/api/rules/{r_w['id']}")

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
