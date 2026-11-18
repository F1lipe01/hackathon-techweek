"""The three Claude calls of ThingTracker, with a hard spending cap.

observe()  Haiku 5.5   zone crops -> which things are visible and where, and yes/no answers for each sensor
ask()      Sonnet 5.5  a question (English or Portuguese) -> answer from the memory (text only, no images)
compile()  Sonnet 5.5  a sentence (English or Portuguese) -> a virtual sensor (zone, yes/no question, action)

Every call goes through _call(), which refuses to run once the cap is reached
(TT_BUDGET_USD, default 3.00) and records the real token usage and cost.

AI IS OFF BY DEFAULT. Without TT_AI=1 nothing is sent to Claude, at zero cost:
- observe() analyses nothing and never invents sightings or alerts;
- ask() and compile() return simulated answers built only from the memory and the sentence, marked "(simulated)".
"""
import json
import os
import re
import threading

import anthropic

OBSERVE_MODEL = "claude-haiku-5-5"
REASON_MODEL = "claude-sonnet-5-5"
# USD per million tokens (input, output), prompts under 100K tokens.
PRICES = {OBSERVE_MODEL: (0.10, 0.50), REASON_MODEL: (2.00, 10.00)}

ACTIONS = ["notify", "light_red", "light_blue", "light_green", "light_off", "plug_off", "plug_on"]


class BudgetExceeded(Exception):
    pass


class Brain:
    def __init__(self, store):
        self.store = store
        self.cap = float(os.environ.get("TT_BUDGET_USD", "3.00"))
        self.enabled = os.environ.get("TT_AI") == "1"
        self.client = anthropic.Anthropic() if self.enabled else None  # reads ANTHROPIC_API_KEY from the environment
        self.lock = threading.Lock()

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
        if not self.enabled:
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


    # ------------------------------------------------------------------ simulation (TT_AI unset): no API calls, no cost
    def _sim_ask(self, question, memory):
        q = question.lower()
        for t in memory["things"]:
            if t["name"].lower() in q or t["thing_id"] in q:
                last = t["last_seen"]
                if not last:
                    return {"answer": f"I haven't seen your {t['name'].lower()} yet. (simulated answer)", "thing_id": t["thing_id"]}
                where = f", {last['where']}" if last.get("where") else ""
                return {"answer": f"Your {t['name'].lower()}: last seen at {last['when'].split(' ')[-1]}, on the {last['zone'].lower()}{where}. (simulated answer)",
                        "thing_id": t["thing_id"]}
        return {"answer": "I couldn't find that in my memory. (simulated answer)", "thing_id": ""}

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
