"""The three Claude calls of ThingTracker, with a hard spending cap.

observe()  Haiku 5.5   zone crops -> which things are visible and where, and yes/no answers for each sensor
ask()      Sonnet 5.5  a question (English or Portuguese) -> answer from the memory (text only, no images)
compile()  Sonnet 5.5  a sentence (English or Portuguese) -> a virtual sensor (zone, yes/no question, action)

Every call goes through _call(), which refuses to run once the cap is reached
(TT_BUDGET_USD, default 3.00) and records the real token usage and cost.

AI IS OFF BY DEFAULT. Without TT_AI=1 nothing is sent to Claude, at zero cost:
- observe() analyses nothing and never invents sightings or alerts;
- ask() and compile_local() use the LOCAL TEXT MODEL (llm_local.py, Qwen3-1.7B on this machine, offline, free)
  when its service answers on 127.0.0.1:8766, and keyword templates otherwise.

Which engine answers ask() and compile_local() (TT_LLM):
- unset   Claude if TT_AI=1; else the local model if it answers; else the templates;
- local   the local model even when TT_AI=1 (observe() still uses Claude then); the templates if it is down;
- off     Claude if TT_AI=1; else the templates.
"""
import json
import os
import re
import threading
import time
import urllib.request

import anthropic

OBSERVE_MODEL = "claude-haiku-5-5"
REASON_MODEL = "claude-sonnet-5-5"
# USD per million tokens (input, output), prompts under 100K tokens.
PRICES = {OBSERVE_MODEL: (0.10, 0.50), REASON_MODEL: (2.00, 10.00)}

ACTIONS = ["notify", "light_red", "light_blue", "light_green", "light_off", "plug_off", "plug_on"]
LOCAL_ACTIONS = ["notify", "plug_off", "light_red", "light_blue", "light_green"]
PLACES = ["desk", "table", "shelf", "sofa", "bench"]
LOCAL_LLM_URL = os.environ.get("TT_LLM_URL", "http://127.0.0.1:8766")

# Words that mark a question as Portuguese, so the local model is told which language to answer in.
_PT = re.compile(r"\b(onde|está|estão|minha|minhas|meu|meus|quando|qual|quais|que|viu|vi|câmara|hoje|ontem|"
                 r"deixei|tenho|há|não|avisa|diz|lembra|se|sem|sair|casa)\b|[ãõçáéíóúâêô]")


def _lang(text):
    return "pt" if _PT.search(text.lower()) else "en"


# Portuguese words for common things and colours, so "carteira preta" finds "Black wallet", and back.
_PT_EN = {"carteira": "wallet", "chave": "key", "chaves": "key", "keys": "key", "livro": "book", "óculos": "glasses",
          "oculos": "glasses", "telemóvel": "phone", "telemovel": "phone", "telefone": "phone", "caneca": "mug",
          "chávena": "mug", "cup": "mug", "mochila": "backpack", "comando": "remote", "garrafa": "bottle",
          "portátil": "laptop", "portatil": "laptop", "computador": "laptop", "relógio": "watch", "mala": "bag",
          "saco": "bag", "casaco": "coat", "chapéu": "hat", "preta": "black", "preto": "black", "castanha": "brown",
          "castanho": "brown", "amarela": "yellow", "amarelo": "yellow", "azul": "blue", "vermelha": "red",
          "vermelho": "red", "verde": "green", "branca": "white", "branco": "white", "cinzenta": "grey",
          "cinzento": "grey", "gray": "grey"}
_STOP = {"my", "the", "where", "are", "is", "a", "an", "of", "do", "you", "see", "saw", "seen", "have", "did", "what",
         "when", "was", "last", "i", "it", "camera", "today", "onde", "está", "estão", "o", "os", "as", "meu", "minha",
         "meus", "minhas", "de", "do", "da", "que", "é", "viste", "foi", "vista", "visto", "câmara", "hoje", "viu"}


def _words(text):
    """The meaningful words of a name or a question, in one vocabulary (Portuguese mapped to English, no plurals)."""
    out = set()
    for w in re.findall(r"[a-zà-ú]+", text.lower()):
        if w in _STOP:
            continue
        w = _PT_EN.get(w, w)
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.add(w)
    return out


class BudgetExceeded(Exception):
    pass


class Brain:
    def __init__(self, store):
        self.store = store
        self.cap = float(os.environ.get("TT_BUDGET_USD", "3.00"))
        self.enabled = os.environ.get("TT_AI") == "1"
        self.client = anthropic.Anthropic() if self.enabled else None  # reads ANTHROPIC_API_KEY from the environment
        self.lock = threading.Lock()
        self.llm = os.environ.get("TT_LLM", "").lower()   # "", "local" or "off"
        self._local_seen = (0.0, False)                   # (when checked, did it answer)

    # ------------------------------------------------------------------ which engine answers questions and sentences
    def _local_up(self):
        """Does the local model service answer? Checked at most every 5 s."""
        t, ok = self._local_seen
        if time.time() - t > 5:
            try:
                with urllib.request.urlopen(LOCAL_LLM_URL + "/health", timeout=1) as r:
                    ok = json.loads(r.read()).get("ok") is True
            except Exception:
                ok = False
            self._local_seen = (time.time(), ok)
        return ok

    def text_mode(self):
        """'claude', 'local' or 'templates': who answers ask() and compile_local() right now."""
        if self.enabled and self.llm != "local":
            return "claude"
        if self.llm != "off" and self._local_up():
            return "local"
        return "templates"

    def _local(self, system, prompt, max_tokens, as_json):
        """One call to llm_local.py; None if the service is down or fails, so the caller falls back to the templates."""
        body = json.dumps({"system": system, "prompt": prompt, "max_tokens": max_tokens, "json": as_json}).encode()
        req = urllib.request.Request(LOCAL_LLM_URL + "/generate", body, {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())["text"]
        except Exception as e:
            print("local model unavailable:", e)
            self._local_seen = (time.time(), False)
            return None

    # ------------------------------------------------------------------ plumbing
    def _call(self, kind, model, system, content, schema, max_tokens, thinking_off):
        spent = self.store.spend()["usd"]
        if spent >= self.cap:
            raise BudgetExceeded(f"Budget cap reached: {spent:.4f} of {self.cap:.2f} USD")
        kwargs = dict(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": content}],
            output_config={"format": {"type": "json_schema", "schema": schema}, "effort": "low"},
        )
        if thinking_off:
            kwargs["thinking"] = {"type": "disabled"}
        resp = self.client.messages.create(**kwargs)
        pin, pout = PRICES[model]
        u = resp.usage
        cost = (u.input_tokens * pin + u.output_tokens * pout) / 1_000_000
        self.store.add_spend(kind, model, u.input_tokens, u.output_tokens, cost)
        if resp.stop_reason == "refusal":
            raise RuntimeError("The model declined this request")
        text = next(b.text for b in resp.content if b.type == "text")
        return json.loads(text)

    # ------------------------------------------------------------------ observe
    def observe(self, crops, things, sensors):
        """crops: [{zone_id, zone_name, jpeg_b64}]; things: [{id, name, description}];
        sensors: [{id, zone_id, question}] -> {zones: [...]}"""
        if not self.enabled:
            return {"zones": [], "not_analysed": True}  # AI off: never invent sightings or alerts
        content = []
        for c in crops:
            content.append({"type": "text", "text": f"Zone {c['zone_id']} \"{c['zone_name']}\":"})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": c["jpeg_b64"]}})
        content.append({"type": "text", "text": json.dumps({
            "things_to_look_for": [{"thing_id": t["id"], "name": t["name"], "description": t.get("description", "")} for t in things],
            "sensors": [{"sensor_id": s["id"], "zone_id": s["zone_id"], "question": s["question"]} for s in sensors],
        }, ensure_ascii=False)})
        system = (
            "You analyse crops of a home camera for the ThingTracker service. Each crop is one zone the user chose. "
            "For every zone: describe the scene in at most 12 English words; for every thing to look for, "
            "say whether it is visible in that zone and, if so, where, in a few English words (e.g. 'left of the laptop'); "
            "answer every sensor question that belongs to that zone with yes, no or unsure, plus brief evidence in English. "
            "Be literal and conservative: if you cannot see it clearly, it is not visible and the answer is unsure. "
            "Never identify people; you may say 'a person', 'a child' or 'an adult'."
        )
        schema = {
            "type": "object",
            "properties": {"zones": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "zone_id": {"type": "string"},
                    "scene": {"type": "string"},
                    "things": {"type": "array", "items": {"type": "object", "properties": {
                        "thing_id": {"type": "string"}, "visible": {"type": "boolean"}, "where": {"type": "string"}},
                        "required": ["thing_id", "visible", "where"], "additionalProperties": False}},
                    "sensors": {"type": "array", "items": {"type": "object", "properties": {
                        "sensor_id": {"type": "string"}, "answer": {"type": "string", "enum": ["yes", "no", "unsure"]},
                        "evidence": {"type": "string"}},
                        "required": ["sensor_id", "answer", "evidence"], "additionalProperties": False}},
                },
                "required": ["zone_id", "scene", "things", "sensors"], "additionalProperties": False}}},
            "required": ["zones"], "additionalProperties": False,
        }
        return self._call("observe", OBSERVE_MODEL, system, content, schema, max_tokens=900, thinking_off=True)

    # ------------------------------------------------------------------ ask
    def ask(self, question, memory):
        mode = self.text_mode()
        if mode == "local":
            return self._local_ask(question, memory) or self._sim_ask(question, memory)
        if mode == "templates":
            return self._sim_ask(question, memory)
        system = (
            "You are the ThingTracker assistant inside the Altice home app. Answer in the language of the question "
            "(English, or European Portuguese if the question is in Portuguese), in one or two natural sentences, using only "
            "the memory provided: where and when each thing was last seen, and recent events. Give times as '08:42'. "
            "If the thing was never seen, say so plainly. Never invent. "
            "Set thing_id to the id of the thing the answer is about, or an empty string."
        )
        schema = {"type": "object", "properties": {"answer": {"type": "string"}, "thing_id": {"type": "string"}},
                  "required": ["answer", "thing_id"], "additionalProperties": False}
        content = [{"type": "text", "text": json.dumps({"question": question, "memory": memory}, ensure_ascii=False)}]
        return self._call("ask", REASON_MODEL, system, content, schema, max_tokens=600, thinking_off=False)

    # ------------------------------------------------------------------ compile a sentence into a sensor
    def compile(self, sentence, zones, things):
        if not self.enabled:
            return self._sim_compile(sentence, zones, things)
        system = (
            "You turn one sentence written by a user (English or Portuguese) into a virtual sensor for a home camera. "
            "A sensor watches one zone and asks one yes/no question that can be answered from a single still image of that zone "
            "(for example 'Is there a mug on the desk?', 'Is a child climbing the bookshelf?'). Write the question, title and message in the language of the sentence. "
            "Choose the zone that best matches; if none matches, use the first zone. "
            "Mode 'when_true' (deadline ''): the action fires when the answer equals trigger_when. "
            "Mode 'not_by_deadline', for sentences with a time limit such as 'if the cat hasn't drunk water by 6 pm': "
            "ask about the expected event ('Is the cat drinking from the bowl?'), set trigger_when to the answer that means it happened ('yes') "
            "and deadline to 'HH:MM'; the action fires if that answer was never seen before the deadline. "
            "Pick the action from the list; use 'notify' when the sentence only asks to be told. "
            "If the sentence names an object that is not in the list of things, put its short name in new_thing, else ''. "
            "title: at most 6 words. message: the notification, one short natural sentence. "
            "cooldown_s: seconds before the sensor may fire again (60 to 3600)."
        )
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "zone_id": {"type": "string"},
                "question": {"type": "string"},
                "trigger_when": {"type": "string", "enum": ["yes", "no"]},
                "mode": {"type": "string", "enum": ["when_true", "not_by_deadline"]},
                "deadline": {"type": "string"},
                "action": {"type": "string", "enum": ACTIONS},
                "message": {"type": "string"},
                "new_thing": {"type": "string"},
                "cooldown_s": {"type": "integer"},
            },
            "required": ["title", "zone_id", "question", "trigger_when", "mode", "deadline", "action", "message", "new_thing", "cooldown_s"],
            "additionalProperties": False,
        }
        content = [{"type": "text", "text": json.dumps({
            "sentence": sentence,
            "zones": [{"zone_id": z["id"], "name": z["name"]} for z in zones],
            "things": [{"thing_id": t["id"], "name": t["name"]} for t in things],
            "possible_actions": ACTIONS,
        }, ensure_ascii=False)}]
        return self._call("compile", REASON_MODEL, system, content, schema, max_tokens=800, thinking_off=False)


    # ------------------------------------------------------------------ a sentence -> a local rule (the camera era)
    LOCAL_KINDS = ("left_for", "nobody_for", "someone_arrives", "seen_in")

    def compile_local(self, sentence, things):
        """Compile a sentence once into a rule that the rules engine evaluates locally, at no cost per check."""
        mode = self.text_mode()
        if mode == "local":
            return self._local_compile_local(sentence, things) or self._sim_compile_local(sentence, things)
        if mode == "templates":
            return self._sim_compile_local(sentence, things)
        system = (
            "You turn one sentence from a home user into a rule for the ThingTracker rules engine. The camera detects the "
            "home's things, the places they are on (desk, table, shelf, sofa, bench) and people. Kinds: "
            "left_for (a thing stays on a place for N minutes), nobody_for (no movement or people for N minutes), "
            "someone_arrives (a person appears after the room was empty), seen_in (a thing is seen, optionally on a place). "
            "Actions: notify, plug_off, light_red, light_blue, light_green. Use the given thing ids; place is one of the "
            "places or empty. Title: short, in the language of the sentence. Message: what the user is told when it fires."
        )
        schema = {"type": "object", "properties": {
            "title": {"type": "string"}, "kind": {"type": "string", "enum": list(self.LOCAL_KINDS)},
            "thing_id": {"type": "string"}, "place": {"type": "string"}, "minutes": {"type": "number"},
            "action": {"type": "string", "enum": ["notify", "plug_off", "light_red", "light_blue", "light_green"]},
            "message": {"type": "string"}, "cooldown_s": {"type": "integer"}},
            "required": ["title", "kind", "thing_id", "place", "minutes", "action", "message", "cooldown_s"],
            "additionalProperties": False}
        content = [{"type": "text", "text": json.dumps({"sentence": sentence, "things": [
            {"id": t["id"], "name": t["name"]} for t in things]}, ensure_ascii=False)}]
        return self._call("compile", REASON_MODEL, system, content, schema, max_tokens=800, thinking_off=False)

    # ------------------------------------------------------------------ the local text model (llm_local.py)
    @staticmethod
    def _day(when):
        """'18 Nov 08:42' -> 'today at 08:42', 'yesterday at 08:42' or '16 Nov at 08:42' (easier for a small model)."""
        day, _, hhmm = when.rpartition(" ")
        if day == time.strftime("%d %b"):
            return f"today at {hhmm}"
        if day == time.strftime("%d %b", time.localtime(time.time() - 86400)):
            return f"yesterday at {hhmm}"
        return f"{day} at {hhmm}"

    @classmethod
    def _seen(cls, t):
        last = t["last_seen"]
        if not last:
            return f"{t['name']}: never seen by the camera."
        room = f" ({last['room']})" if last.get("room") else ""
        note = f", {last['where']}" if last.get("where") else ""
        return f"{t['name']}: last seen by the camera {cls._day(last['when'])}, on the {last['zone']}{room}{note}."

    # Events the server writes when the user acts in the app (server.py), as opposed to what the camera recorded.
    _APP_EVENT = re.compile(r"^(Now tracking:|New sensor:|Registering |Registration of )|"
                            r" registered: a visual fingerprint|Suggested sensor:")

    def _events(self, memory, names=None, camera=True):
        """Recent events as lines, oldest first: what the camera recorded (camera=True) or what was done in the app.
        Only those naming one of `names` when given. Earlier answers of the assistant are logged as events
        ('"question": answer'); they are neither."""
        return [f"- {self._day(e['when'])}: {e['text']}" for e in memory["recent_events"] if not e["text"].startswith('"')
                and bool(self._APP_EVENT.search(e["text"])) != camera
                and (names is None or any(n.lower() in e["text"].lower() for n in names))]

    @staticmethod
    def _match(question, things):
        """The ids of the registered things a question is about, by their words in English or Portuguese.
        'brown wallet' or 'carteira castanha' -> the brown one; 'wallet' with two wallets -> both."""
        q = _words(question)
        low = question.lower()
        exact = [t for t in things if t["name"].lower() in low]
        if exact:
            longest = max(len(t["name"]) for t in exact)
            return [t["thing_id"] for t in exact if len(t["name"]) == longest]
        score = {}
        for t in things:
            name = _words(t["name"])
            if name & q:
                score[t["thing_id"]] = (len(name & q), name <= q)  # shared words, then "every word of the name"
        best = max(score.values(), default=None)
        return [tid for tid, s in score.items() if s == best]

    @staticmethod
    def _which_one(names, lang):
        opts = ", ".join(names[:-1]) + (" ou " if lang == "pt" else " or ") + names[-1]
        return (f"Encontrei {len(names)} que correspondem: {opts}. De qual se trata?" if lang == "pt"
                else f"You have {len(names)} of those: {opts}. Which one?")

    def _local_ask(self, question, memory):
        """The code decides which things the question is about (and so thing_id and candidates);
        the model writes the answer, in the user's language, from the facts it is given and nothing else."""
        lang = _lang(question)
        things = memory["things"]
        by_id = {t["thing_id"]: t for t in things}
        ids = self._match(question, things)
        day = None
        now_ = f"Now: {self._day(memory['now'])}."
        system = (
            "You are the ThingTracker assistant in the Altice home app. A home camera recognises the things the family "
            "registered and records where and when it saw them. Use only the facts given; never invent a place, a time "
            "or a sighting. Reply in " +
            ("European Portuguese, as spoken in Portugal (say 'a sua', 'câmara', 'telemóvel')" if lang == "pt" else "English") +
            ", in one or two short, natural sentences, without lists. Write times as 08:42. "
            "Write the name of each thing exactly as it is given."
        )
        tail = "\n\nResponde em português de Portugal." if lang == "pt" else ""
        if len(ids) > 1:
            facts = "\n".join("- " + self._seen(by_id[i]) for i in ids)
            prompt = (f"{now_}\n\nSeveral registered things fit the question:\n{facts}\n\nQuestion: {question}\n\n"
                      "The question does not say which one. Do not answer it: ask the user which one they mean, "
                      "naming each one, in one short sentence that ends with a question mark.")
        elif ids:
            t = by_id[ids[0]]
            events = self._events(memory, [t["name"]])
            prompt = (f"{now_}\n\nThe question is about this registered thing:\n- {self._seen(t)}\n" +
                      ("Events about it, oldest first:\n" + "\n".join(events) + "\n" if events else "") +
                      f"\nQuestion: {question}\n\nAnswer from its last sighting: where and when. "
                      "If it was never seen, say the camera has not seen it yet.")
        else:
            low = question.lower()
            day = next((d for d, w in (("today", ("today", "this morning", "tonight", "hoje", "esta manhã")),
                                       ("yesterday", ("yesterday", "ontem"))) if any(x in low for x in w)), None)
            if day:  # a question about one day gets that day's events only, so nothing older is reported as new
                cam = "\n".join(e for e in self._events(memory) if e.startswith(f"- {day} ")) or "- nothing"
                app = "\n".join(e for e in self._events(memory, camera=False) if e.startswith(f"- {day} ")) or "- nothing"
                prompt = (f"{now_}\n\nRecorded by the camera {day}, oldest first:\n{cam}\n\n"
                          f"Done by the user in the app {day} (the camera did not see these):\n{app}\n\n"
                          f"Question: {question}\n\nAnswer from these lists only. Never describe something done in "
                          f"the app as seen by the camera. If the camera recorded nothing {day}, say so.")
            else:
                facts = "\n".join("- " + self._seen(t) for t in things) or "- none"
                cam = "\n".join(self._events(memory)) or "- nothing"
                app = "\n".join(self._events(memory, camera=False)) or "- nothing"
                prompt = (f"{now_}\n\nRegistered things:\n{facts}\n\nRecently recorded by the camera, oldest first:\n"
                          f"{cam}\n\nRecently done by the user in the app (the camera did not see these):\n{app}\n\n"
                          f"Question: {question}\n\n"
                          "If the question asks about a thing that is not among the registered things, say so, for "
                          "example: " + ("\"Ainda não conheço as suas chaves. Pode adicioná-las no separador Things.\" "
                                         if lang == "pt" else "\"I don't know your keys yet. You can add them in the Things tab.\" ") +
                          "If it is a general question about the home, answer from the events; if there are none, say so.")
        answer = (self._local(system, prompt + tail, 120, False) or "").strip().strip('"').strip()
        sentences = list(dict.fromkeys(re.split(r"(?<=[.!?])\s+", answer)))  # small models sometimes repeat themselves
        answer = " ".join(sentences[:3])
        if not answer:
            return None  # the service failed: the template answers instead
        if len(ids) > 1:
            names = [_words(by_id[i]["name"]) for i in ids]
            own = [n - set().union(*(m for m in names if m is not n)) for n in names]  # what tells each one apart
            if not answer.endswith("?") or not all(o & _words(answer) for o in own if o):
                print("local answer replaced (does not ask which one):", answer)
                answer = self._which_one([by_id[i]["name"] for i in ids], lang)
            return {"answer": answer, "thing_id": "", "candidates": ids}
        asked = bool(ids)
        if not ids and re.search(r"camera|câmara|camara|\b(see|saw|seen|viu|visto|vista)\b", question.lower()):
            answer = self._check_camera_answer(answer, memory, day, lang)
        if not ids:  # a general answer may still be about one thing, named in it
            named = [t["thing_id"] for t in things if t["name"].lower() in answer.lower()]
            ids = named if len(named) == 1 else []
        thing_id = ids[0] if ids else ""
        if asked:  # an answer about the thing asked for must agree with the memory: seen or never seen
            t = by_id[thing_id]
            says_not = re.search(r"\b(not|never|yet|não|nunca|ainda)\b|n't\b", answer.lower())
            if bool(t["last_seen"]) == bool(says_not) or (not t["last_seen"] and re.search(r"\d{1,2}[:h]\d{2}", answer)):
                print("local answer replaced (disagrees with the memory):", answer)
                answer = self._fact_answer(t, lang)
        return {"answer": answer, "thing_id": thing_id}

    _NEGATION = re.compile(r"\b(not|never|nothing|no|none|yet|não|nunca|nada|nenhum|nenhuma|ainda)\b|n't\b")

    def _camera_events(self, memory, day=None):
        return [e for e in memory["recent_events"] if not e["text"].startswith('"') and not self._APP_EVENT.search(e["text"])
                and (not day or self._day(e["when"]).startswith(day + " "))]

    def _check_camera_answer(self, answer, memory, day, lang):
        """An answer about what the camera saw may only use what the camera recorded: its times, the things it names,
        and 'nothing' when there is nothing. Otherwise a plain summary of the camera's events replaces it."""
        events = self._camera_events(memory, day)
        seen = " ".join(f"{e['text']} {e['when']}" for e in events).lower()
        named = [t["name"].lower() for t in memory["things"] if t["name"].lower() in answer.lower()]
        on_camera = [t["name"].lower() for t in memory["things"] if t["name"].lower() in seen]
        times = re.findall(r"\b\d{1,2}:\d{2}\b", answer)
        ok = (all(x in seen for x in times) and all(n in seen for n in named) and (named or not on_camera)
              and (events or self._NEGATION.search(answer.lower())))
        if not ok:
            print("local answer replaced (not what the camera recorded):", answer)
        return answer if ok else self._camera_summary(events, day, lang)

    def _camera_summary(self, events, day, lang):
        """'Today the camera saw: Brown wallet on the table (08:42).' straight from the events."""
        items = []
        for e in events:
            hhmm = e["when"].rpartition(" ")[2]
            m = re.match(r"(.+) seen (?:on the (\w+)|in the room)", e["text"])
            if m:
                place = m.group(2) or "room"
                where = (self.PLACE_PT.get(place, f"em {place}") if lang == "pt"
                         else "in the room" if place == "room" else f"on the {place}")
                items.append(f"{m.group(1)} {where} ({hhmm})")
            else:
                items.append(f"{e['text'].rstrip('.')} ({hhmm})")
        when = {"today": ("today", "hoje"), "yesterday": ("yesterday", "ontem")}.get(day, ("recently", "recentemente"))
        if lang == "pt":
            return (f"{when[1].capitalize()}, a câmara viu: " + "; ".join(items) + "." if items
                    else f"A câmara não registou nada {when[1]}.")
        return (f"{when[0].capitalize()} the camera saw: " + "; ".join(items) + "." if items
                else f"The camera recorded nothing {when[0]}.")

    PLACE_PT = {"table": "na mesa", "desk": "na secretária", "shelf": "na prateleira", "sofa": "no sofá",
                "bench": "no banco", "room": "na sala"}

    def _fact_answer(self, t, lang):
        """A plain sentence straight from the memory, used when the model's answer disagrees with it."""
        last = t["last_seen"]
        if lang != "pt":
            if not last:
                return f"I haven't seen your {t['name'].lower()} yet."
            return self._sim_ask(t["name"], {"things": [t]})["answer"]
        if not last:
            return f"A câmara ainda não viu: {t['name']}."
        day, _, hhmm = self._day(last["when"]).partition(" at ")
        day = {"today": "hoje", "yesterday": "ontem"}.get(day, f"a {day}")
        place = self.PLACE_PT.get(last["zone"].lower(), f"em {last['zone']}")
        return f"A câmara viu {t['name']} pela última vez {place}, {day} às {hhmm}."

    def _local_compile_local(self, sentence, things):
        system = (
            "You turn one sentence from a home user into a rule for the ThingTracker rules engine. The home camera "
            "recognises the registered things, the place each one is on (desk, table, shelf, sofa, bench) and people.\n"
            "Kinds:\n"
            "- left_for: a thing stays on a place for N minutes (also 'if I leave home without X', 'if I forget X');\n"
            "- nobody_for: no movement and no people for N minutes;\n"
            "- someone_arrives: a person appears after the room was empty;\n"
            "- seen_in: a thing is seen, optionally on a given place.\n"
            "Actions: notify (only tell the user), plug_off, light_red, light_blue, light_green.\n"
            "thing_id: the id of the thing the sentence names, from the list, or \"\" if none matches. "
            "place: desk, table, shelf, sofa, bench or \"\". minutes: a number, 10 if the sentence gives none. "
            "title: at most 6 words; message: what the user is told when the rule fires, one short sentence; "
            "both in the language of the sentence" + (" (European Portuguese)" if _lang(sentence) == "pt" else "") + ". "
            "cooldown_s: seconds before it may fire again, 60 to 3600, usually 300.\n"
            'Reply with JSON only, with exactly these keys: {"title": "", "kind": "", "thing_id": "", "place": "", '
            '"minutes": 10, "action": "notify", "message": "", "cooldown_s": 300}\n'
            "Examples:\n"
            'Things: id "keys": Keys. Sentence: Tell me if I go out without my keys\n'
            '{"title": "Keys left at home", "kind": "left_for", "thing_id": "keys", "place": "", "minutes": 10, '
            '"action": "notify", "message": "You went out without your keys.", "cooldown_s": 300}'
        )
        listed = "\n".join(f'- id "{t["id"]}": {t["name"]}' for t in things) or "- none"
        pt = "\n\nEscreve o title e a message em português de Portugal." if _lang(sentence) == "pt" else ""
        raw = self._local(system, f"Registered things:\n{listed}\n\nSentence: {sentence}{pt}", 250, True)
        try:
            rule = self._valid_rule(self._flat_json(raw), things)
        except (TypeError, ValueError, KeyError):
            return None  # not valid JSON or not a valid rule: the template compiles it instead
        return self._literal_fixes(rule, sentence, things)

    # Words that name each place, in English and Portuguese.
    PLACE_WORDS = {"desk": ["desk", "secretária", "secretaria"], "table": ["table", "mesa"],
                   "shelf": ["shelf", "prateleira", "estante"], "sofa": ["sofa", "sofá"], "bench": ["bench", "banco"]}

    def _literal_fixes(self, rule, sentence, things):
        """What the sentence states literally wins over the model: a light or plug action, a number of minutes,
        a place, a thing named by its words, a kind word (nobody, arrives, without, stays). The model writes the
        title and the message, and chooses the kind when no keyword says it."""
        low = sentence.lower()
        hint = self._sim_compile_local(sentence, things)
        if "_" in rule["title"] or rule["title"].lower() in self.LOCAL_KINDS:  # the kind echoed as a title
            rule["title"] = hint["title"]
        if hint["action"] != "notify":
            rule["action"] = hint["action"]
        if hint["kind"] != "seen_in":  # the templates found a kind word: nobody, someone arrives, stays, left...
            rule["kind"] = hint["kind"]
        if re.search(r"\bwithout\b|\bforg[eo]t|esquec|\bsem\b", low):  # "leave home without X", "sair sem X"
            rule["kind"] = "left_for"
        if re.search(r"\d+\s*(min|minut|hora|hour|h\b)", low):
            rule["minutes"] = hint["minutes"]
        said = [p for p, words in self.PLACE_WORDS.items() if any(re.search(rf"\b{w}\b", low) for w in words)]
        if rule["place"] not in said:
            rule["place"] = said[0] if said else ""
        ids = self._match(sentence, [{"thing_id": t["id"], "name": t["name"]} for t in things])
        if len(ids) == 1:
            rule["thing_id"] = ids[0]
        elif ids and rule["thing_id"] not in ids:
            rule["thing_id"] = ""
        if rule["thing_id"] and re.search(r"\bfica|\bstay|\bleft on\b|deixad|mais de \d|more than \d", low):
            rule["kind"] = "left_for"  # "if the book stays on the table for more than 30 minutes"
        return rule

    RULE_KEYS = ("title", "kind", "thing_id", "place", "minutes", "action", "message", "cooldown_s")

    def _flat_json(self, raw):
        """The rule's flat JSON object. A small model sometimes slips ('300"', '2*60'): then each known key is read
        on its own, strings and plain numbers only, and _valid_rule() still checks every value."""
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            if not isinstance(raw, str):
                raise
        d = {}
        for k in self.RULE_KEYS:
            m = re.search(rf'"{k}"\s*:\s*(?:"((?:[^"\\]|\\.)*)"|(\d+(?:\.\d+)?)(?:\s*\*\s*(\d+))?)', raw)
            if m:
                d[k] = (m.group(1) if m.group(1) is not None
                        else float(m.group(2)) * (int(m.group(3)) if m.group(3) else 1))
        return d

    def _valid_rule(self, d, things):
        """The rule in the exact schema of compile_local(), or ValueError."""
        if not isinstance(d, dict) or d.get("kind") not in self.LOCAL_KINDS or d.get("action") not in LOCAL_ACTIONS:
            raise ValueError("kind or action")
        title, message = str(d.get("title", "")).strip(), str(d.get("message", "")).strip()
        if not title or not message:
            raise ValueError("title or message")
        ids = {t["id"] for t in things}
        names = {t["name"].lower(): t["id"] for t in things}
        tid = str(d.get("thing_id") or "").strip()
        tid = tid if tid in ids else names.get(tid.lower(), "")
        place = str(d.get("place") or "").strip().lower()
        minutes = float(d.get("minutes") if d.get("minutes") not in (None, "") else 10)
        if not 0 < minutes <= 24 * 60:
            raise ValueError("minutes")
        return {"title": title[:60], "kind": d["kind"], "thing_id": tid, "place": place if place in PLACES else "",
                "minutes": int(minutes) if minutes == int(minutes) else minutes, "action": d["action"], "message": message[:200],
                "cooldown_s": max(60, min(3600, int(float(d.get("cooldown_s") or 300))))}

    def _sim_compile_local(self, sentence, things):
        """Keyword templates in English and Portuguese, so the demo runs with AI off (no cost)."""
        low = sentence.lower()
        alias = {"keys": ["key", "chave"], "wallet": ["carteira"], "glasses": ["óculos", "oculos"], "phone": ["telemóvel", "telemovel", "telefone"],
                 "mug": ["caneca", "chávena", "cup"], "laptop": ["portátil", "portatil", "computador"], "remote": ["comando"],
                 "bottle": ["garrafa"], "waterbottle": ["garrafa", "bottle"], "backpack": ["mochila"]}
        thing = next((t for t in things if t["name"].lower() in low or t["id"] in low
                      or any(a in low for a in alias.get(t["id"], []))), None)
        place = next((en for en, words in {"desk": ["desk", "secretária", "secretaria"], "table": ["table", "mesa"],
                                            "shelf": ["shelf", "prateleira", "estante"], "sofa": ["sofa", "sofá"]}.items()
                      if any(w in low for w in words)), "")
        m = re.search(r"(\d+)\s*(min|minut|hora|hour|h\b)", low)
        minutes = (int(m.group(1)) * (60 if m.group(2).startswith(("hora", "hour", "h")) else 1)) if m else 10
        action = "notify"
        if any(w in low for w in ("light", "luz", "lâmpada", "lampada")):
            action = "light_red" if ("red" in low or "vermelh" in low) else "light_green" if ("green" in low or "verde" in low) else "light_blue"
        if ("plug" in low or "tomada" in low) and ("off" in low or "deslig" in low):
            action = "plug_off"
        if any(w in low for w in ("nobody", "no one", "ninguém", "ninguem", "empty", "vazi")):
            kind = "nobody_for"
        elif any(w in low for w in ("arrive", "comes in", "someone", "chega", "entra", "alguém", "alguem")):
            kind = "someone_arrives"
        elif thing and any(w in low for w in ("left", "leave", "stays", "deixad", "esquec", "fica")):
            kind = "left_for"
        else:
            kind = "seen_in"
        title = sentence.strip().rstrip(".")
        return {"title": (title[:38] + "…") if len(title) > 40 else title, "kind": kind,
                "thing_id": thing["id"] if thing else "", "place": place, "minutes": minutes, "action": action,
                "message": sentence.strip(), "cooldown_s": 300}

    # ------------------------------------------------------------------ simulation (TT_AI unset): no API calls, no cost
    def _sim_ask(self, question, memory):
        q = question.lower()
        words = set(re.findall(r"[a-zà-ú]+", q))
        stop = {"my", "the", "where", "are", "is", "a", "an", "of", "do", "you", "see", "have"}
        exact = [t for t in memory["things"] if t["name"].lower() in q]
        loose = [t for t in memory["things"]
                 if (set(re.findall(r"[a-zà-ú]+", t["name"].lower())) - stop) & words]
        if not exact and len(loose) > 1:              # several things fit: ask which one, as a person would
            opts = []
            for t in loose[:4]:
                last = t["last_seen"]
                opts.append(f"{t['name']}" + (f" (on the {last['zone'].lower()} at {last['when'].split(' ')[-1]})" if last else " (not seen yet)"))
            return {"answer": f"You have {len(loose)} of those. Which one?", "thing_id": "",
                    "candidates": [t["thing_id"] for t in loose[:4]]}
        found = exact or loose or [t for t in memory["things"] if t["thing_id"] in q]
        if found:
            t, last = found[0], found[0]["last_seen"]
            if not last:
                return {"answer": f"I haven't seen your {t['name'].lower()} yet.", "thing_id": t["thing_id"]}
            where = f", {last['where']}" if last.get("where") else ""
            room = f", {last['room']}" if last.get("room") else ""
            return {"answer": f"On the {last['zone'].lower()}{room}, at {last['when'].split(' ')[-1]}.",
                    "thing_id": t["thing_id"]}
        return {"answer": "I couldn't find that in the home's memory.", "thing_id": ""}

    def _sim_compile(self, sentence, zones, things):
        low = sentence.lower()
        zone = next((z for z in zones if z["name"].lower() in low), zones[0])
        action = "notify"
        if any(w in low for w in ("light", "luz", "lâmpada")):
            action = "light_red" if ("red" in low or "vermelh" in low) else "light_green" if ("green" in low or "verde" in low) else "light_blue"
        if ("plug" in low or "tomada" in low) and ("off" in low or "deslig" in low):
            action = "plug_off"
        m = re.search(r"(?:by|até às)\s*(\d{1,2})(?:[:h](\d{2}))?\s*(pm|h)?", low)
        hh = None
        if m:
            hh = int(m.group(1)) + (12 if m.group(3) == "pm" and int(m.group(1)) < 12 else 0)
        title = sentence.strip().rstrip(".")
        return {
            "title": (title[:38] + "…") if len(title) > 40 else title,
            "zone_id": zone["id"], "question": f"(simulated) {sentence.strip()}",
            "trigger_when": "yes", "mode": "not_by_deadline" if m else "when_true",
            "deadline": f"{hh:02d}:{m.group(2) or '00'}" if m else "",
            "action": action, "message": f"(simulated) {sentence.strip()}", "new_thing": "", "cooldown_s": 60,
        }
