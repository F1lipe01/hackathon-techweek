"""The prototype's local database: one SQLite file, prototype/data/home.db.

Two kinds of tables live in it.

1. A copy of what the Altice platform already holds, in the platform's own model: the home, its rooms and its
   devices. The real app reads these from the platform; the prototype reads them from here. On start the server
   refreshes them through the MCP (read-only tools get_home_devices / get_home_rooms) when it is logged in; otherwise
   it keeps the last copy. The first copy matches the "Hack 3" home as the app showed it on 18 Nov 2026, 15:27.

2. What ThingTracker adds on top, which in production would live in the platform's database, per customer:
   things          the objects the user registered (name, the English word the detector searches for)
   fingerprints    each thing's visual fingerprint (8 DINOv2 vectors); the home device keeps its own copy too
   sightings       the home's memory: where and when each thing was seen, with a small crop of it
   presence        where and when the camera saw a person, a child, a dog or a cat; never a picture of them
   sensors         the rules written as sentences, compiled to structured rules
   events          what the app shows as activity and alerts
   spend           what each language-model call cost

Values that are lists or nested objects are kept as JSON text in a column. The class keeps the interface the server
already uses (snapshot, things, add_observation, ...), so the server never writes SQL itself.
"""
import json
import os
import sqlite3
import threading
import time
import unicodedata
import uuid
from pathlib import Path

# TT_DATA points a second server at its own data folder (prototype/test_scenarios.py uses one), so tests never
# write into the demo's database.
DATA = Path(os.environ.get("TT_DATA") or Path(__file__).resolve().parent / "data")
DB = DATA / "home.db"
CROPS = DATA / "crops"

SCHEMA = """
CREATE TABLE IF NOT EXISTS home (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rooms (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL, room_id TEXT REFERENCES rooms(id),
  status TEXT NOT NULL, raised INTEGER NOT NULL DEFAULT 0, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS things (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, query TEXT NOT NULL, created REAL NOT NULL, fingerprint TEXT);
CREATE TABLE IF NOT EXISTS fingerprints (
  thing_id TEXT PRIMARY KEY REFERENCES things(id) ON DELETE CASCADE, model TEXT, vectors TEXT NOT NULL, created REAL);
CREATE TABLE IF NOT EXISTS sightings (
  id TEXT PRIMARY KEY, ts REAL NOT NULL, thing_id TEXT NOT NULL REFERENCES things(id) ON DELETE CASCADE,
  place TEXT NOT NULL, room TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', crop TEXT);
CREATE INDEX IF NOT EXISTS sightings_by_thing ON sightings(thing_id, ts);
CREATE TABLE IF NOT EXISTS presence (
  id TEXT PRIMARY KEY, ts REAL NOT NULL, who TEXT NOT NULL, place TEXT NOT NULL, room TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS presence_by_who ON presence(who, ts);
CREATE TABLE IF NOT EXISTS sensors (id TEXT PRIMARY KEY, created REAL NOT NULL, active INTEGER NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, ts REAL NOT NULL, kind TEXT NOT NULL, text TEXT NOT NULL, data TEXT);
CREATE TABLE IF NOT EXISTS spend (ts REAL, kind TEXT, model TEXT, tokens_in INTEGER, tokens_out INTEGER, usd REAL);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""

# The "Hack 3" home as the Altice app showed it on 18 Nov 2026 at 15:27 (ids from the MCP's get_home_devices).
# "raised" marks the cards the app draws white and raised (Contact sensor, Plug); the others are tinted.
SEED_ROOMS = [("work-room", "Work Room")]
SEED_DEVICES = [
    ("0c7856ad-89b1-468d-9d6a-10253b2f3c20", "Camera", "camera", "work-room", "On", 0),
    ("7aafb6f4-74ec-4771-84f6-bbc7df420631", "Contact sensor", "contactSensor", None, "Open", 1),
    ("00e038d4-0da7-45c2-b61f-f38c9ff9df82", "Light", "bulb", None, "Disconnected", 0),
    ("bc891629-98bc-44f7-99a8-1aa61428a9bf", "Plug", "plug", None, "0,0 W", 1),
    ("5d5f8fff-cd69-4f33-a331-04bd731de043", "Security hub", "gateway", None, "On", 0),
    ("d091c05f-e72c-45be-a16f-0ab2e93297a3", "Smoke sensor", "smokeSensor", None, "On", 0),
    ("2c76ef67-f807-426a-9237-9e67df475202", "Temperature sensor", "temperatureSensor", None, "23.5 °C | 65.5 %", 0),
]


def now():
    return time.time()


def _id():
    return uuid.uuid4().hex[:10]


class Store:
    def __init__(self, path=DB):
        DATA.mkdir(exist_ok=True)
        CROPS.mkdir(exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SCHEMA)
        if not self.db.execute("SELECT 1 FROM home").fetchone():
            self._seed()

    def _seed(self):
        with self.lock, self.db:
            self.db.execute("INSERT INTO home VALUES ('hack3', 'Hack 3')")
            self.db.executemany("INSERT INTO rooms VALUES (?, ?)", SEED_ROOMS)
            self.db.executemany("INSERT INTO devices VALUES (?, ?, ?, ?, ?, ?, ?)",
                                [(*d, now()) for d in SEED_DEVICES])
            self._set_meta("devices_source", "Copy of the app on 18 Nov 2026, 15:27")

    def _q(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def _set_meta(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (key, json.dumps(value)))

    def meta(self, key, default=None):
        row = self._q("SELECT value FROM meta WHERE key = ?", (key,))
        return json.loads(row[0]["value"]) if row else default

    # ------------------------------------------------------------------ the platform's model: home, rooms, devices
    def home(self):
        h = self._q("SELECT name FROM home")[0]["name"]
        rooms = self._q("SELECT id, name FROM rooms ORDER BY name")
        devices = self._q("SELECT id, name, type, room_id, status, raised FROM devices ORDER BY name")
        return {"name": h, "rooms": rooms, "devices": devices, "source": self.meta("devices_source", "")}

    def camera_room(self):
        row = self._q("SELECT r.name FROM devices d JOIN rooms r ON r.id = d.room_id WHERE d.type = 'camera' LIMIT 1")
        return row[0]["name"] if row else "Without room"

    def camera_places(self):
        """The places the cameras stand for: each camera is one place ("Kitchen 1", "Kitchen 2"), named by its room,
        plus any place a camera has reported sightings from."""
        names = [self.camera_room()] + [r["room"] for r in self._q(
            "SELECT DISTINCT room FROM sightings UNION SELECT DISTINCT room FROM presence")]
        return list(dict.fromkeys(n for n in names if n and n != "Without room"))

    def set_device_status(self, device_type, status):
        """The status line of every device of one type (the simulated door changes the Contact sensor's card)."""
        with self.lock, self.db:
            self.db.execute("UPDATE devices SET status = ?, updated = ? WHERE type = ?", (status, now(), device_type))

    def sync_devices(self, devices, source):
        """Refresh device statuses from the platform (get_home_devices); keeps rooms and the card style."""
        with self.lock, self.db:
            for d in devices:
                self.db.execute("UPDATE devices SET status = ?, updated = ? WHERE id = ?", (d["status"], now(), d["id"]))
            self._set_meta("devices_source", source)

    # ------------------------------------------------------------------ reads used by the server
    def things(self):
        out = []
        for t in self._q("SELECT * FROM things ORDER BY created"):
            t["description"] = t.pop("query")
            t["fingerprint"] = json.loads(t["fingerprint"]) if t["fingerprint"] else None
            out.append(t)
        return out

    def observations(self, thing_id=None, limit=800):
        sql = "SELECT * FROM sightings" + (" WHERE thing_id = ?" if thing_id else "") + " ORDER BY ts DESC LIMIT ?"
        rows = self._q(sql, ((thing_id, limit) if thing_id else (limit,)))
        # the shape the rules engine and the language model already expect, oldest first
        return [{"id": r["id"], "ts": r["ts"], "thing_id": r["thing_id"], "zone_id": "place-" + r["place"],
                 "zone_name": r["place"], "room": r["room"], "where": r["note"], "crop": r["crop"]} for r in reversed(rows)]

    def last_seen(self, thing_id):
        obs = self.observations(thing_id, limit=1)
        return obs[-1] if obs else None

    def presence(self, who, since=0.0, until=None):
        """Sightings of people and pets (who: a list of 'person', 'child', 'dog', 'cat'), oldest first."""
        marks = ",".join("?" * len(who))
        return self._q(f"SELECT ts, who, place, room FROM presence WHERE who IN ({marks}) AND ts > ? AND ts <= ? "
                       "ORDER BY ts", (*who, since, until if until is not None else now() + 1))

    def last_presence(self, who, before):
        marks = ",".join("?" * len(who))
        rows = self._q(f"SELECT ts, who, place, room FROM presence WHERE who IN ({marks}) AND ts < ? "
                       "ORDER BY ts DESC LIMIT 1", (*who, before))
        return rows[0] if rows else None

    def rules(self):
        return [{**json.loads(r["data"]), "id": r["id"], "active": bool(r["active"])}
                for r in self._q("SELECT * FROM sensors ORDER BY created DESC")]

    def active_rules(self):
        return [r for r in self.rules() if r["active"]]

    def events(self, limit=60):
        return [{**(json.loads(e["data"]) if e["data"] else {}), "id": e["id"], "ts": e["ts"], "kind": e["kind"], "text": e["text"]}
                for e in self._q("SELECT * FROM events ORDER BY ts DESC LIMIT ?", (limit,))]

    def spend(self):
        rows = self._q("SELECT COALESCE(SUM(usd), 0) AS usd, COUNT(*) AS calls FROM spend")[0]
        return {"usd": rows["usd"], "calls": rows["calls"]}

    def snapshot(self):
        things = [{**t, "last_seen": self.last_seen(t["id"])} for t in self.things()]
        sp = self.spend()
        return {"zones": [], "things": things, "rules": self.rules(), "events": self.events(),
                "spend": {"usd": round(sp["usd"], 4), "calls": sp["calls"]}, "home": self.home()}

    def memory_for_llm(self):
        """Compact memory for answering a question: the last sighting of each thing and the latest events, local time."""
        fmt = lambda ts: time.strftime("%d %b %H:%M", time.localtime(ts))
        things = []
        for t in self.things():
            last = self.last_seen(t["id"])
            things.append({"thing_id": t["id"], "name": t["name"],
                           "last_seen": None if not last else
                           {"when": fmt(last["ts"]), "zone": last["zone_name"], "room": last["room"], "where": last["where"]}})
        # the camera's latest 15 sightings and the latest 15 other events, so a busy door or sensor log never
        # pushes what the camera saw out of the memory
        recent = self.events(200)
        recent = sorted([e for e in recent if e["kind"] == "seen"][:15] + [e for e in recent if e["kind"] != "seen"][:15],
                        key=lambda e: -e["ts"])
        events = [{"when": fmt(e["ts"]), "kind": e["kind"], "text": e["text"]} for e in recent]
        return {"now": fmt(now()), "things": things, "recent_events": events[::-1]}

    def find_suggestion(self, sentence):
        """The suggestion event that proposed this exact sentence, with its ready-made rule, or None."""
        rows = self._q("SELECT data FROM events WHERE kind = 'suggest' AND json_extract(data, '$.sentence') = ? "
                       "ORDER BY ts DESC LIMIT 1", (sentence,))
        return json.loads(rows[0]["data"]) if rows else None

    def zones(self):
        return []                       # one camera = one place; zones inside a camera are left to Altice

    def suggested(self):
        return self.meta("suggested", [])

    def fingerprints(self):
        return {r["thing_id"]: {"model": r["model"], "vectors": json.loads(r["vectors"]), "created": r["created"]}
                for r in self._q("SELECT * FROM fingerprints")}

    # ------------------------------------------------------------------ writes
    def add_spend(self, kind, model, tin, tout, usd):
        with self.lock, self.db:
            self.db.execute("INSERT INTO spend VALUES (?, ?, ?, ?, ?, ?)", (now(), kind, model, tin, tout, usd))

    def set_zones(self, zones):
        pass

    def mark_suggested(self, kind):
        with self.lock, self.db:
            self._set_meta("suggested", sorted(set(self.suggested()) | {kind}))

    def add_thing(self, name, description=""):
        ascii_name = unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode()
        tid = "".join(ch for ch in ascii_name if ch.isalnum())[:20] or _id()
        with self.lock, self.db:
            if not self.db.execute("SELECT 1 FROM things WHERE id = ?", (tid,)).fetchone():
                self.db.execute("INSERT INTO things VALUES (?, ?, ?, ?, NULL)", (tid, name, description or name.lower(), now()))
        return tid

    def delete_thing(self, tid):
        with self.lock, self.db:
            self.db.execute("DELETE FROM things WHERE id = ?", (tid,))

    def set_fingerprint(self, thing_id, info, vectors=None, model=""):
        """Visual registration: how many views, a few crops and when; the vectors go in the fingerprints table."""
        with self.lock, self.db:
            self.db.execute("UPDATE things SET fingerprint = ? WHERE id = ?", (json.dumps(info) if info else None, thing_id))
            if info and vectors is not None:
                self.db.execute("INSERT OR REPLACE INTO fingerprints VALUES (?, ?, ?, ?)",
                                (thing_id, model, json.dumps(vectors), now()))
            if not info:
                self.db.execute("DELETE FROM fingerprints WHERE thing_id = ?", (thing_id,))

    def add_observation(self, thing_id, zone, where, crop_name, room=None):
        """room: the place of the camera that saw it (each camera is one place); the kit camera's room by default."""
        with self.lock, self.db:
            self.db.execute("INSERT INTO sightings VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (_id(), now(), thing_id, zone["name"], room or self.camera_room(), where or "", crop_name))

    def add_presence(self, who, place, room):
        with self.lock, self.db:
            self.db.execute("INSERT INTO presence VALUES (?, ?, ?, ?, ?)", (_id(), now(), who, place, room))

    def add_event(self, kind, text, **extra):
        e = {"id": _id(), "ts": now(), "kind": kind, "text": text, **extra}
        with self.lock, self.db:
            self.db.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)", (e["id"], e["ts"], kind, text, json.dumps(extra)))
        return e

    def add_rule(self, sentence, compiled):
        r = {"id": "r-" + uuid.uuid4().hex[:6], "sentence": sentence, **compiled, "active": True, "last_fired": 0,
             "fired_today": False, "seen_trigger_today": False, "day": time.strftime("%Y-%m-%d")}
        with self.lock, self.db:
            self.db.execute("INSERT INTO sensors VALUES (?, ?, 1, ?)", (r["id"], now(), json.dumps(r)))
        return r

    def update_rule(self, rid, **fields):
        with self.lock, self.db:
            row = self.db.execute("SELECT data, active FROM sensors WHERE id = ?", (rid,)).fetchone()
            if not row:
                return None
            r = {**json.loads(row["data"]), **fields}
            active = fields.get("active", bool(row["active"]))
            self.db.execute("UPDATE sensors SET data = ?, active = ? WHERE id = ?", (json.dumps(r), int(bool(active)), rid))
            return {**r, "id": rid, "active": bool(active)}

    def delete_rule(self, rid):
        """A sensor and the activity it wrote."""
        with self.lock, self.db:
            self.db.execute("DELETE FROM sensors WHERE id = ?", (rid,))
            self.db.execute("DELETE FROM events WHERE json_extract(data, '$.rule_id') = ?", (rid,))

    def reset(self):
        """Start again with no things, sightings, sensors or events. The home's devices and the spending stay."""
        with self.lock, self.db:
            for table in ("sightings", "presence", "fingerprints", "things", "sensors", "events"):
                self.db.execute(f"DELETE FROM {table}")
            self.db.execute("DELETE FROM meta WHERE key = 'suggested'")
