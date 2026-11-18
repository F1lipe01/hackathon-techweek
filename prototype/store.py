"""ThingTracker memory: one JSON file in prototype/data/ (gitignored).

Seeded with demo data so the app looks lived-in; every seeded item carries "demo": true.
"""
import json
import threading
import time
import unicodedata
import uuid
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
STATE = DATA / "state.json"
CROPS = DATA / "crops"


def now():
    return time.time()


def _today_at(hh, mm):
    t = time.localtime()
    return time.mktime((t.tm_year, t.tm_mon, t.tm_mday, hh, mm, 0, 0, 0, -1))


def seed():
    zones = [
        {"id": "z1", "name": "Desk", "x": 0.05, "y": 0.45, "w": 0.5, "h": 0.5},
        {"id": "z2", "name": "Hall table", "x": 0.6, "y": 0.5, "w": 0.35, "h": 0.45},
    ]
    things = [
        {"id": "keys", "name": "Keys", "description": "a key ring with two or three keys", "icon": "key"},
        {"id": "wallet", "name": "Wallet", "description": "a leather wallet", "icon": "purse"},
        {"id": "glasses", "name": "Glasses", "description": "reading glasses", "icon": "glasses"},
        {"id": "phone", "name": "Phone", "description": "a smartphone", "icon": "mobile_phone"},
        {"id": "mug", "name": "Mug", "description": "a coffee mug", "icon": "hot_beverage"},
        {"id": "laptop", "name": "Laptop", "description": "a laptop computer", "icon": "laptop"},
        {"id": "remote", "name": "TV remote", "description": "a black TV remote control", "icon": "remote"},
    ]
    seen = [
        ("keys", "z2", "Hall table", "next to the bowl", 8, 42),
        ("wallet", "z2", "Hall table", "on the right, by the keys", 8, 40),
        ("glasses", "z1", "Desk", "on the notebook", 9, 15),
        ("laptop", "z1", "Desk", "in the middle", 9, 50),
        ("mug", "z1", "Desk", "left of the laptop", 9, 58),
    ]
    obs = [{"id": uuid.uuid4().hex[:10], "ts": _today_at(h, m), "thing_id": t, "zone_id": z, "zone_name": zn,
            "where": w, "crop": None, "demo": True} for t, z, zn, w, h, m in seen]
    rules = [{
        "id": "r-demo", "sentence": "Tell me if the mug is left on the desk.",
        "title": "Mug left on the desk", "zone_id": "z1", "question": "Is there a mug on the desk?",
        "trigger_when": "yes", "mode": "when_true", "deadline": "", "action": "notify",
        "message": "The mug was left on the desk.", "new_thing": "", "cooldown_s": 600,
        "active": False, "last_fired": 0, "demo": True,
    }]
    events = [{"id": uuid.uuid4().hex[:10], "ts": _today_at(8, 43), "kind": "seen",
               "text": "Keys seen on the hall table.", "demo": True}]
    return {"zones": zones, "things": things, "observations": obs, "rules": rules, "events": events,
            "spend": {"usd": 0.0, "calls": []}}


class Store:
    def __init__(self):
        DATA.mkdir(exist_ok=True)
        CROPS.mkdir(exist_ok=True)
        self.lock = threading.RLock()
        self.state = json.loads(STATE.read_text()) if STATE.exists() else seed()
        self._save()

    def _save(self):
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=1))
        tmp.replace(STATE)

    # ------------------------------------------------------------------ reads
    def snapshot(self):
        with self.lock:
            s = self.state
            return {
                "zones": s["zones"], "things": [self._with_last_seen(t) for t in s["things"]],
                "rules": s["rules"], "events": s["events"][-60:][::-1],
                "spend": {"usd": round(s["spend"]["usd"], 4), "calls": len(s["spend"]["calls"])},
            }

    def _with_last_seen(self, t):
        last = None
        for o in reversed(self.state["observations"]):
            if o["thing_id"] == t["id"]:
                last = o
                break
        return {**t, "last_seen": last}

    def zones(self):
        return list(self.state["zones"])

    def things(self):
        return list(self.state["things"])

    def active_rules(self):
        return [r for r in self.state["rules"] if r.get("active")]

    def memory_for_llm(self):
        """Compact memory for ask(): last sighting per thing and the latest events, local time."""
        fmt = lambda ts: time.strftime("%d %b %H:%M", time.localtime(ts))
        things = []
        for t in self.state["things"]:
            last = self._with_last_seen(t)["last_seen"]
            things.append({"thing_id": t["id"], "name": t["name"],
                           "last_seen": None if not last else
                           {"when": fmt(last["ts"]), "zone": last["zone_name"], "where": last["where"]}})
        events = [{"when": fmt(e["ts"]), "text": e["text"]} for e in self.state["events"][-15:]]
        return {"now": fmt(now()), "things": things, "recent_events": events}

    def spend(self):
        return self.state["spend"]

    # ------------------------------------------------------------------ writes
    def add_spend(self, kind, model, tin, tout, usd):
        with self.lock:
            self.state["spend"]["usd"] += usd
            self.state["spend"]["calls"].append({"ts": now(), "kind": kind, "model": model, "in": tin, "out": tout, "usd": usd})
            self._save()

    def set_zones(self, zones):
        with self.lock:
            self.state["zones"] = zones
            self._save()

    def add_thing(self, name, description=""):
        with self.lock:
            ascii_name = unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode()
            tid = "".join(ch for ch in ascii_name if ch.isalnum())[:20] or uuid.uuid4().hex[:6]
            if any(t["id"] == tid for t in self.state["things"]):
                return tid
            self.state["things"].append({"id": tid, "name": name, "description": description, "icon": "dot"})
            self._save()
            return tid

    def add_observation(self, thing_id, zone, where, crop_name):
        with self.lock:
            self.state["observations"].append({"id": uuid.uuid4().hex[:10], "ts": now(), "thing_id": thing_id,
                                               "zone_id": zone["id"], "zone_name": zone["name"], "where": where, "crop": crop_name})
            self.state["observations"] = self.state["observations"][-800:]
            self._save()

    def add_event(self, kind, text, **extra):
        with self.lock:
            e = {"id": uuid.uuid4().hex[:10], "ts": now(), "kind": kind, "text": text, **extra}
            self.state["events"].append(e)
            self.state["events"] = self.state["events"][-300:]
            self._save()
            return e

    def add_rule(self, sentence, compiled):
        with self.lock:
            r = {"id": "r-" + uuid.uuid4().hex[:6], "sentence": sentence, **compiled, "active": True, "last_fired": 0,
                 "fired_today": False, "seen_trigger_today": False, "day": time.strftime("%Y-%m-%d")}
            self.state["rules"].insert(0, r)
            self._save()
            return r

    def update_rule(self, rid, **fields):
        with self.lock:
            for r in self.state["rules"]:
                if r["id"] == rid:
                    r.update(fields)
                    self._save()
                    return r
        return None

    def reset(self):
        """Back to the demo data. Spending is kept, so a reset never lifts the budget cap."""
        with self.lock:
            spend = self.state["spend"]
            self.state = seed()
            self.state["spend"] = spend
            self._save()
