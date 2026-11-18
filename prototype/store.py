"""Track Things memory: one JSON file in prototype/data/ (gitignored).

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
        {"id": "z1", "name": "Secretária", "x": 0.05, "y": 0.45, "w": 0.55, "h": 0.5},
        {"id": "z2", "name": "Mesa da entrada", "x": 0.62, "y": 0.5, "w": 0.33, "h": 0.45},
    ]
    things = [
        {"id": "chaves", "name": "Chaves", "description": "porta-chaves com duas ou três chaves", "icon": "key"},
        {"id": "carteira", "name": "Carteira", "description": "carteira de pele", "icon": "wallet"},
        {"id": "oculos", "name": "Óculos", "description": "óculos de ver", "icon": "glasses"},
        {"id": "caneca", "name": "Caneca", "description": "caneca de café", "icon": "mug"},
        {"id": "telemovel", "name": "Telemóvel", "description": "smartphone", "icon": "phone"},
    ]
    seen = [
        ("chaves", "z2", "Mesa da entrada", "ao lado da taça", 8, 42),
        ("carteira", "z2", "Mesa da entrada", "à direita, junto às chaves", 8, 40),
        ("oculos", "z1", "Secretária", "em cima do caderno", 9, 15),
        ("caneca", "z1", "Secretária", "à esquerda do portátil", 9, 58),
    ]
    obs = [{"id": uuid.uuid4().hex[:10], "ts": _today_at(h, m), "thing_id": t, "zone_id": z, "zone_name": zn,
            "where": w, "crop": None, "demo": True} for t, z, zn, w, h, m in seen]
    rules = [{
        "id": "r-demo", "sentence": "Avisa-me se a caneca ficar na secretária quando eu sair.",
        "title": "Caneca esquecida", "zone_id": "z1", "question": "Há uma caneca em cima da secretária?",
        "trigger_when": "yes", "mode": "when_true", "deadline": "", "action": "notify",
        "message": "A caneca ficou na secretária.", "new_thing": "", "cooldown_s": 600,
        "active": False, "last_fired": 0, "demo": True,
    }]
    events = [{"id": uuid.uuid4().hex[:10], "ts": _today_at(8, 43), "kind": "seen",
               "text": "Chaves vistas na mesa da entrada.", "demo": True}]
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
        fmt = lambda ts: time.strftime("%d/%m %H:%M", time.localtime(ts))
        things = []
        for t in self.state["things"]:
            last = self._with_last_seen(t)["last_seen"]
            things.append({"thing_id": t["id"], "nome": t["name"],
                           "visto_pela_ultima_vez": None if not last else
                           {"quando": fmt(last["ts"]), "zona": last["zone_name"], "onde": last["where"]}})
        events = [{"quando": fmt(e["ts"]), "texto": e["text"]} for e in self.state["events"][-15:]]
        return {"agora": fmt(now()), "coisas": things, "eventos_recentes": events}

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
