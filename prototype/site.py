"""The pitch site: one local page with the live demo, the use cases, the documents and the videos.

    prototype/.venv/bin/python prototype/site.py              # http://127.0.0.1:8780/site
    prototype/.venv/bin/python prototype/site.py --fresh      # rebuild the demo home from scratch first

What it starts, all on this Mac and offline:
  1. the local text model (prototype/llm_local.py, port 8766), unless it already answers;
  2. a server of its own (prototype/server.py, port 8780) in replay mode: the lab take of the book
     (prototype/replays/book.json) stands in for the kit camera, and the home is the demo home below, in
     prototype/data/demo/ (never the prototype's own prototype/data/home.db).
The edge service (OWLv2 + DINOv2) is started from the page ("Ativar modelos"), through video/tools/heavy.sh.

The demo home: the kit's real devices (a frozen copy, nothing is read from or sent to the platform), plus devices
simulated by ThingTracker in five rooms, and the family's things with where they were last seen (simulated memory,
except the book, whose fingerprint was learnt by the real models from the lab take: video/out/proof/book-data).
Everything a button changes is simulated; the page's reset puts the home back as it was built (pristine.db).
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEMO = HERE / "data" / "demo"
SOURCE = ROOT / "video" / "out" / "proof" / "book-data"     # the book's camera views, learnt by the real edge
PORT = 8780

ROOMS = [("living-room", "Living room"), ("kitchen", "Kitchen"), ("bedroom", "Bedroom"), ("entrance", "Entrance"),
         ("work-room", "Work Room")]

# The kit's devices, placed in rooms (their ids are the platform's).
KIT_ROOMS = {
    "0c7856ad-89b1-468d-9d6a-10253b2f3c20": ("work-room", "On"),                 # Camera
    "7aafb6f4-74ec-4771-84f6-bbc7df420631": ("entrance", "Closed"),              # Contact sensor (front door)
    "00e038d4-0da7-45c2-b61f-f38c9ff9df82": ("living-room", "On"),               # Light
    "bc891629-98bc-44f7-99a8-1aa61428a9bf": ("work-room", "12,4 W"),             # Plug (powers the ceiling lights)
    "5d5f8fff-cd69-4f33-a331-04bd731de043": ("entrance", "On"),                  # Security hub
    "d091c05f-e72c-45be-a16f-0ab2e93297a3": ("kitchen", "On"),                   # Smoke sensor
    "2c76ef67-f807-426a-9237-9e67df475202": ("living-room", "21,4 °C | 52 %"),   # Temperature sensor
}

# Simulated devices: (id, name, type, room, on, watch). "watch": counted by "nobody home and something is on".
SIM = [
    ("sim-tv", "TV", "tv", "living-room", True, True),
    ("sim-lamp", "Floor lamp", "bulb", "living-room", True, True),
    ("sim-speaker", "Speaker", "speaker", "living-room", False, True),
    ("sim-blinds", "Blinds", "blind", "living-room", True, False),
    ("sim-vacuum", "Robot vacuum", "vacuum", "living-room", False, False),
    ("sim-motion-lr", "Motion sensor", "motionSensor", "living-room", None, False),
    ("sim-coffee", "Coffee machine", "coffee", "kitchen", True, True),
    ("sim-oven", "Oven", "oven", "kitchen", False, True),
    ("sim-kitchen-light", "Kitchen lights", "bulb", "kitchen", True, True),
    ("sim-leak", "Leak sensor", "leakSensor", "kitchen", None, False),
    ("sim-window-k", "Kitchen window", "contactSensor", "kitchen", None, False),
    ("sim-washer", "Washing machine", "washer", "kitchen", False, False),
    ("sim-bedside", "Bedside lamp", "bulb", "bedroom", False, True),
    ("sim-heater", "Heater", "heater", "bedroom", True, True),
    ("sim-thermostat", "Thermostat", "thermostat", "bedroom", None, False),
    ("sim-window-b", "Bedroom window", "contactSensor", "bedroom", None, False),
    ("sim-lock", "Smart lock", "lock", "entrance", True, False),
    ("sim-hall-light", "Hall light", "bulb", "entrance", False, True),
    ("sim-siren", "Indoor siren", "siren", "entrance", None, False),
    ("sim-desk-lamp", "Desk lamp", "bulb", "work-room", True, True),
]
SENSOR_STATUS = {"sim-motion-lr": "No motion", "sim-leak": "Dry", "sim-window-k": "Closed", "sim-window-b": "Open",
                 "sim-thermostat": "20,5 °C · Heating", "sim-siren": "Ready"}

# The family's things, with where each was last seen (simulated memory: no camera saw these; minutes ago).
THINGS = [
    ("keys", "Keys", "keys", "hall table", "Entrance", 35),
    ("wallet", "Wallet", "wallet", "sofa", "Living room", 80),
    ("glasses", "Glasses", "glasses", "bedside table", "Bedroom", 140),
    ("remote", "TV remote", "tv remote control", "sofa", "Living room", 20),
    ("pills", "Medication box", "medication box", "kitchen counter", "Kitchen", 300),
    ("passport", "Passport", "passport", "drawer", "Bedroom", 4300),
    ("backpack", "School backpack", "backpack", "hall bench", "Entrance", 55),
    ("laptop", "Laptop", "laptop", "desk", "Work Room", 10),
]


def build(fresh=False):
    """The demo home in prototype/data/demo, and its pristine copy for the page's reset."""
    if DEMO.exists() and not fresh and (DEMO / "pristine.db").exists():
        return
    shutil.rmtree(DEMO, ignore_errors=True)
    DEMO.mkdir(parents=True)
    src = sqlite3.connect(SOURCE / "home.db")
    db = sqlite3.connect(DEMO / "home.db")
    src.backup(db)
    src.close()
    for table in ("events", "sightings", "presence", "phones", "presence_state", "spend"):
        try:
            db.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            pass
    db.execute("DELETE FROM meta WHERE key IN ('alarm', 'photo_tasks', 'suggested')")
    db.execute("UPDATE home SET name = 'Hack 3'")
    db.executemany("INSERT OR REPLACE INTO rooms VALUES (?, ?)", ROOMS)
    for did, (room, status) in KIT_ROOMS.items():
        db.execute("UPDATE devices SET room_id = ?, status = ? WHERE id = ?", (room, status, did))
    now = time.time()
    for did, name, typ, room, on, _ in SIM:
        status = SENSOR_STATUS.get(did) or ("On" if on else "Off")
        db.execute("INSERT OR REPLACE INTO devices VALUES (?, ?, ?, ?, ?, 0, ?)", (did, name, typ, room, status, now))
    db.execute("INSERT OR REPLACE INTO meta VALUES ('devices_source', ?)",
               (json.dumps("Demo home: the kit's devices (a copy) and simulated devices"),))
    for tid, name, query, place, room, mins in THINGS:
        db.execute("INSERT OR REPLACE INTO things (id, name, query, created, fingerprint) VALUES (?, ?, ?, ?, NULL)",
                   (tid, name, query, now - 86400 * 3))
        db.execute("INSERT INTO sightings VALUES (?, ?, ?, ?, ?, ?, NULL)",
                   (f"sim-{tid}", now - mins * 60, tid, place, room, "simulated memory"))
    db.commit()
    db.close()
    shutil.copytree(SOURCE / "crops", DEMO / "crops")
    for f in ("edge.db", "edge-fingerprints.json", "edge-places.json"):
        if (SOURCE / f).exists():
            shutil.copy2(SOURCE / f, DEMO / f)
    tt = {"powers": {"plug": "Ceiling lights"},
          "state": {"bc891629-98bc-44f7-99a8-1aa61428a9bf": True, "ac": True},
          "integrations": [{"id": "ac", "name": "Air conditioner", "type": "ac", "room": "Living room", "on": True,
                            "via": "Third-party integration"}],
          "sim": {did: {"on": bool(on), "watch": watch} for did, _, _, _, on, watch in SIM if on is not None}}
    (DEMO / "tt_devices.json").write_text(json.dumps(tt))
    (DEMO / "tt_devices.pristine.json").write_text(json.dumps(tt))
    shutil.copy2(DEMO / "home.db", DEMO / "pristine.db")
    print(f"demo home built in {DEMO}")


def up(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true", help="rebuild the demo home first")
    ap.add_argument("--port", type=int, default=PORT)
    a = ap.parse_args()
    build(a.fresh)
    if not up("http://127.0.0.1:8766/health"):
        print("starting the local text model (llm_local.py)…")
        subprocess.Popen([str(HERE / ".venv-llm" / "bin" / "python"), str(HERE / "llm_local.py")],
                         stdout=open(DEMO / "llm.out", "a"), stderr=subprocess.STDOUT, start_new_session=True)
    env = {**os.environ, "TT_DATA": str(DEMO), "TT_PORT": str(a.port), "TT_DEMO": "1", "TT_TIMINGS": "demo",
           "TT_REPLAY": str(HERE / "replays" / "book.json"), "TT_DEVICES_FILE": str(DEMO / "tt_devices.json")}
    for k in ("TT_LIVE_ACTIONS", "TT_AI"):
        env.pop(k, None)
    print(f"ThingTracker site on http://127.0.0.1:{a.port}/site")
    os.execve(str(HERE / ".venv" / "bin" / "python"), [str(HERE / ".venv" / "bin" / "python"), str(HERE / "server.py")], env)


if __name__ == "__main__":
    sys.exit(main())
