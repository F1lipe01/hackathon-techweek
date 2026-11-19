"""The presence engine: is anybody home, who, how many, and how sure. The server's rules read it instead of guessing
from the last person a camera happened to see.

It fuses three signals:
  1. The family's phones on the home Wi-Fi. The Altice router sees them, but no MCP tool exposes its Wi-Fi clients today,
     so the prototype simulates them in ThingTracker's own data (table `phones`, one home/away flag per Family member,
     toggled from the page's simulate panel: POST /api/sim/phone). The tool we would propose to Altice is a read-only
     `get_home_wifi_clients` (each client's MAC, name, band and "connected since"), from which the family pairs each
     phone with a person once, in the app.
  2. The door's contact sensor: real through the read-only MCP tool get_home_devices when the session is live, else the
     page's simulated door. An opening followed by a closing starts LEAVING.
  3. People seen by each camera at its last analysis, with an identity when the edge recognised the face (a Family
     member's id), "unknown" (a face is visible and matches nobody registered) or "not_visible" (a person, no face seen).

States:
  OCCUPIED  someone is home, and the signals agree.
  LEAVING   the door opened then closed; for `leaving_check_s` the engine checks who left (phones going away, the count
            dropping, the cameras' refresh analyses).
  EMPTY     no family phone on the Wi-Fi, no Family face seen recently, nobody seen by any camera now.
  UNSURE    the signals disagree: the phones are away but a camera sees a person whose face is not Family (or not
            visible); or a phone is home but nobody has been seen and the door has not been used for `stale_s`.

Count = known people at home (phone on the Wi-Fi, or face seen recently after the phone last left) + registered guests
seen now + unknown faces seen now + people seen now with no face visible who cannot be one of the family already
counted. Rooms without a camera are invisible: a person there counts only through their phone.

The whole state lives in SQLite (tables `phones` and `presence_state`, in the same file as the rest of ThingTracker's
data), so it survives a restart. Every change of state is written to the activity as a "presence" event.

Timings: TIMINGS["demo"] (seconds, so a scenario plays out on stage) and TIMINGS["prod"] (minutes, as a home would
need); TT_TIMINGS=prod selects the second.
"""
import json
import os
import time

OCCUPIED, LEAVING, EMPTY, UNSURE = "OCCUPIED", "LEAVING", "EMPTY", "UNSURE"

# seen_now_s       a camera's last analysis counts as "now" for this long
# face_recent_s    a Family face seen keeps that person "home" for this long (unless their phone leaves later)
# leaving_check_s  how long LEAVING lasts after the door closes
# phone_lag_s      a phone may leave the Wi-Fi this long after its owner went through the door
# stale_s          a phone at home with nobody seen and the door unused for this long is UNSURE (a phone left at home)
# refresh_s        while the state rests on the cameras alone, ask the edge for an analysis this often, even without motion
# check_timeout_s  how long to wait for the edge's active check of a thing before calling it unsure
# unknown_runs     consecutive analyses with an unknown face (or a person with no face) before a security rule acts
# taken_misses     analyses in which a thing is missing from its place, after a person was near it, before "taken"
TIMINGS = {
    "demo": {"seen_now_s": 15, "face_recent_s": 120, "leaving_check_s": 10, "phone_lag_s": 30, "stale_s": 900,
             "refresh_s": 30, "check_timeout_s": 15, "unknown_runs": 3, "taken_misses": 3},
    "prod": {"seen_now_s": 120, "face_recent_s": 30 * 60, "leaving_check_s": 5 * 60, "phone_lag_s": 5 * 60,
             "stale_s": 4 * 3600, "refresh_s": 30, "check_timeout_s": 60, "unknown_runs": 3, "taken_misses": 3},
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS phones (
  member_id TEXT PRIMARY KEY, home INTEGER NOT NULL, changed REAL NOT NULL, source TEXT NOT NULL DEFAULT 'sim');
CREATE TABLE IF NOT EXISTS presence_state (id INTEGER PRIMARY KEY CHECK (id = 1), data TEXT NOT NULL, updated REAL NOT NULL);
"""


def hm(ts):
    return time.strftime("%H:%M", time.localtime(ts))


def span(seconds):
    s = int(max(0, seconds))
    return f"{s} s" if s < 120 else f"{s // 60} min" if s < 7200 else f"{s / 3600:.1f} h"


def join(names):
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1] if names else ""


def is_family(thing):
    d = (thing.get("description") or "").lower()
    return d.startswith("person") and d.split("·")[-1].strip() == "family"


def is_person(thing):
    return (thing.get("description") or "").lower().startswith("person")


class Presence:
    def __init__(self, store, timings=None, clock=time.time):
        self.store, self.clock = store, clock
        self.mode = os.environ.get("TT_TIMINGS", "demo") if timings is None else "custom"
        self.t = dict(TIMINGS.get(self.mode, TIMINGS["demo"]) if timings is None else timings)
        for k in self.t:                    # TT_TIMING_PHONE_LAG_S=4 and the like: the tests shorten single waits
            if os.environ.get(f"TT_TIMING_{k.upper()}") and timings is None:
                self.t[k] = float(os.environ[f"TT_TIMING_{k.upper()}"])
        with store.lock, store.db:
            store.db.executescript(SCHEMA)
        row = self._q("SELECT data FROM presence_state WHERE id = 1")
        self.s = {"state": None, "since": 0.0, "reason": "", "count": 0, "home": [], "door": {}, "leaving": None,
                  "cameras": {}, "faces": {}, "last_person": 0.0, "runs": {}, "started": self.clock()}
        if row:
            self.s.update(json.loads(row[0]["data"]))
        self._saved = None

    # ------------------------------------------------------------------ storage
    def _q(self, sql, args=()):
        with self.store.lock:
            return [dict(r) for r in self.store.db.execute(sql, args).fetchall()]

    def _save(self):
        data = json.dumps(self.s, sort_keys=True)
        if data != self._saved:
            with self.store.lock, self.store.db:
                self.store.db.execute("INSERT OR REPLACE INTO presence_state VALUES (1, ?, ?)", (data, self.clock()))
            self._saved = data

    # ------------------------------------------------------------------ the family and their phones
    def family(self):
        return [{"id": t["id"], "name": t["name"]} for t in self.store.things() if is_family(t)]

    def people(self):
        """Everyone registered as a person (Family and Guests), by id."""
        return {t["id"]: t["name"] for t in self.store.things() if is_person(t)}

    def phones(self):
        return {r["member_id"]: {"home": bool(r["home"]), "changed": r["changed"], "source": r["source"]}
                for r in self._q("SELECT * FROM phones")}

    def _seed_phones(self, fam):
        """A Family member just added has a phone on the home Wi-Fi (simulated, until the toggle says otherwise)."""
        have = self.phones()
        new = [m["id"] for m in fam if m["id"] not in have]
        if new:
            with self.store.lock, self.store.db:
                self.store.db.executemany("INSERT OR IGNORE INTO phones VALUES (?, 1, ?, 'sim-default')",
                                          [(m, self.clock()) for m in new])

    def reset(self):
        with self.store.lock, self.store.db:
            self.store.db.execute("DELETE FROM phones")
            self.store.db.execute("DELETE FROM presence_state")
        self.s.update(state=None, since=0.0, reason="", count=0, home=[], door={}, leaving=None, cameras={}, faces={},
                      last_person=0.0, runs={})
        self._saved = None

    def set_phone(self, member_id, home, source="sim"):
        """A Family member's phone joins (home=True) or leaves the home Wi-Fi. Returns True when it changed."""
        old = self.phones().get(member_id)
        if old and old["home"] == bool(home):
            return False
        with self.store.lock, self.store.db:
            self.store.db.execute("INSERT OR REPLACE INTO phones VALUES (?, ?, ?, ?)",
                                  (member_id, int(bool(home)), self.clock(), source))
        name = self.people().get(member_id, member_id)
        self.store.add_event("phone", ("Simulated: " if source == "sim" else "") + f"{name}'s phone "
                             + ("joined" if home else "left") + " the home Wi-Fi.", member=member_id, home=bool(home),
                             sim=source == "sim")
        self.evaluate()
        return True

    # ------------------------------------------------------------------ inputs
    def door(self, is_open):
        now, d = self.clock(), self.s["door"]
        was_open = d.get("open")
        d["open"] = bool(is_open)
        if is_open:
            d["opened"] = now
            d["count_at_open"], d["home_at_open"] = self.s.get("count", 0), list(self.s.get("home_ids", []))
        else:
            d["closed"] = now
            if was_open:
                self.s["leaving"] = {"opened": d.get("opened", now), "closed": now, "until": now + self.t["leaving_check_s"],
                                     "count_before": d.get("count_at_open", self.s.get("count", 0)),
                                     "home_before": d.get("home_at_open", [])}
        self.evaluate()

    def analysis(self, camera, persons, forced=False):
        """One analysis of one camera: persons is a list of {"identity": a person's id | "unknown" | "not_visible"}.
        An empty list means the camera looked and saw nobody."""
        now, ppl = self.clock(), self.people()
        known = sorted({p["identity"] for p in persons if p.get("identity") in ppl})
        unknown = sum(1 for p in persons if p.get("identity") == "unknown")
        no_face = sum(1 for p in persons if p.get("identity") not in ppl and p.get("identity") != "unknown")
        self.s["cameras"][camera] = {"ts": now, "known": known, "unknown": unknown, "no_face": no_face, "forced": bool(forced)}
        for pid in known:
            self.s["faces"][pid] = now
        if persons:
            self.s["last_person"] = now
        runs = self.s["runs"].setdefault(camera, {"unknown": 0, "unknown_since": 0.0, "no_face": 0, "no_face_since": 0.0})
        fam = {m["id"] for m in self.family()}
        fam_home = (set(known) | set(self.s.get("home_ids", []))) & fam    # a faceless person may be one of them
        for key, hit in (("unknown", unknown > 0), ("no_face", no_face > 0 and not unknown and not fam_home)):
            if hit:
                if not runs[key]:
                    runs[key + "_since"] = now
                runs[key] += 1
            else:
                runs[key], runs[key + "_since"] = 0, 0.0
        self.evaluate()

    # ------------------------------------------------------------------ the state
    def evaluate(self):
        now, t, s = self.clock(), self.t, self.s
        fam = self.family()
        self._seed_phones(fam)
        phones = self.phones()
        names = {m["id"]: m["name"] for m in fam}
        ppl = self.people()
        home, why, by_phone_only = [], [], []
        for m in fam:
            ph, face = phones.get(m["id"]), s["faces"].get(m["id"], 0.0)
            phone_home = bool(ph and ph["home"])
            away_since = ph["changed"] if ph and not ph["home"] else 0.0
            face_home = face >= now - t["face_recent_s"] and face > away_since
            if phone_home or face_home:
                home.append(m["id"])
                how = " and ".join(x for x, on in (("phone on the Wi-Fi", phone_home),
                                                   (f"seen {span(now - face)} ago", face_home)) if on)
                why.append(f"{m['name']} ({how})")
                if not face_home:
                    by_phone_only.append(m["id"])
        seen_known, unknown, no_face, cams_now = set(), 0, 0, []
        for cam, c in s["cameras"].items():
            if c["ts"] >= now - t["seen_now_s"]:
                seen_known |= set(c["known"])
                unknown += c["unknown"]
                no_face += c["no_face"]
                if c["known"] or c["unknown"] or c["no_face"]:
                    cams_now.append(cam)
        guests = sorted(g for g in seen_known if g not in names)
        unattributed = max(0, no_face - len(set(home) - seen_known))
        count = len(home) + len(guests) + unknown + unattributed
        people_now = len(seen_known) + unknown + no_face
        extra = [f"{ppl.get(g, g)} (guest, seen now)" for g in guests]
        if unknown:
            extra.append(f"{unknown} unknown face{'s' if unknown > 1 else ''} seen now")
        if unattributed:
            extra.append(f"{unattributed} person{'s' if unattributed > 1 else ''} seen now, face not visible")
        door = s["door"]
        last_door = max(door.get("opened", 0.0), door.get("closed", 0.0))
        lv = s.get("leaving")
        if lv and now >= lv["until"]:
            s["leaving"] = lv = None
        where = join(f"the {c} camera" for c in cams_now) or "a camera"
        if lv:
            state = LEAVING
            reason = f"The door opened and closed at {hm(lv['closed'])}: checking who left."
        elif not home and not people_now:
            state = EMPTY
            last = s["last_person"]
            reason = ("No family phone on the home Wi-Fi, no Family face seen recently, and nobody seen by the cameras"
                      + (f" since {hm(last)}." if last else "."))
        elif not home:
            state = UNSURE
            reason = (f"The family's phones are away, but {where} sees a person whose face "
                      + ("is not Family." if unknown else "is not visible."))
        elif by_phone_only and len(by_phone_only) == len(home) and not people_now and \
                now - max(s["last_person"], last_door, min(phones[m]["changed"] for m in by_phone_only)) >= t["stale_s"]:
            state = UNSURE
            quiet = now - max(s["last_person"], last_door, min(phones[m]["changed"] for m in by_phone_only))
            reason = (f"{join(names[m] for m in by_phone_only)}'s phone{'s are' if len(by_phone_only) > 1 else ' is'} "
                      f"home, but nobody has been seen and the door not used for {span(quiet)}.")
        else:
            state = OCCUPIED
            reason = "At home: " + "; ".join(why + extra) + "."
        s.update(count=count, home=[names[m] for m in home] + [ppl.get(g, g) for g in guests],
                 home_ids=home + guests, unknown=unknown + unattributed, reason=reason, updated=now)
        if state != s["state"]:
            old = s["state"]
            s["state"], s["since"] = state, now
            self.store.add_event("presence", f"Home: {old or 'started'} → {state}. {reason}", state=state, prev=old,
                                 count=count, who=s["home"])
        self._save()
        return self.snapshot()

    # ------------------------------------------------------------------ what the rules and the app read
    def snapshot(self):
        s, phones, ppl = self.s, self.phones(), self.people()
        return {"state": s["state"], "since": s["since"], "reason": s["reason"], "count": s["count"], "home": s["home"],
                "home_ids": s.get("home_ids", []), "unknown": s.get("unknown", 0), "updated": s.get("updated", 0.0),
                "last_person": s["last_person"], "door": dict(s["door"]), "leaving": s.get("leaving"),
                "cameras": s["cameras"], "mode": self.mode, "timings": self.t,
                "phones": [{"id": m["id"], "name": m["name"], **phones.get(m["id"], {"home": None, "changed": 0.0})}
                           for m in self.family()],
                "relies_on_camera": self.relies_on_camera(), "people": ppl}

    def family_home(self):
        """The ids of the Family members counted at home now."""
        fam = {m["id"] for m in self.family()}
        return [p for p in self.s.get("home_ids", []) if p in fam]

    def relies_on_camera(self):
        """No family phone is on the Wi-Fi, and yet the state says someone may be home (or is being checked): only the
        cameras can tell, and a person sitting still never wakes the motion check."""
        phones_home = any(p["home"] for p in self.phones().values())
        return self.s["state"] == LEAVING or (not phones_home and (self.s["count"] > 0 or self.s["state"] == UNSURE))

    def wants_refresh(self, camera):
        """Should this camera analyse now, even without motion? Every refresh_s while the state rests on the cameras."""
        if not self.relies_on_camera():
            return False
        last = self.s["cameras"].get(camera, {}).get("ts", 0.0)
        return self.clock() - last >= self.t["refresh_s"] or (self.s["state"] == LEAVING and self.clock() - last >= 3)

    def left_since(self, ts):
        """Family members whose phone left the Wi-Fi at or after ts."""
        names = {m["id"]: m["name"] for m in self.family()}
        return [names[m] for m, p in self.phones().items() if m in names and not p["home"] and p["changed"] >= ts]

    def arrived_since(self, ts):
        """Family members whose phone joined the Wi-Fi at or after ts (a member just added is not an arrival)."""
        names = {m["id"]: m["name"] for m in self.family()}
        return [names[m] for m, p in self.phones().items()
                if m in names and p["home"] and p["changed"] >= ts and p["source"] != "sim-default"]

    def run(self, camera, key):
        """(consecutive analyses, since when) of an unknown face ('unknown') or of a person with no face ('no_face')."""
        r = self.s["runs"].get(camera, {})
        return r.get(key, 0), r.get(key + "_since", 0.0)
