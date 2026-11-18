"""The three Claude calls of Track Things, with a hard spending cap.

observe()  Haiku 5.5   zone crops -> which things are visible and where, and yes/no answers for each sensor
ask()      Sonnet 5.5  a question in Portuguese -> answer from the memory (text only, no images)
compile()  Sonnet 5.5  a sentence in Portuguese -> a virtual sensor (zone, yes/no question, action)

Every call goes through _call(), which refuses to run once the cap is reached
(TT_BUDGET_USD, default 3.00) and records the real token usage and cost.
"""
import json
import os
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
        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
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
        content = []
        for c in crops:
            content.append({"type": "text", "text": f"Zona {c['zone_id']} «{c['zone_name']}»:"})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": c["jpeg_b64"]}})
        content.append({"type": "text", "text": json.dumps({
            "coisas_a_procurar": [{"thing_id": t["id"], "nome": t["name"], "descricao": t.get("description", "")} for t in things],
            "sensores": [{"sensor_id": s["id"], "zone_id": s["zone_id"], "pergunta": s["question"]} for s in sensors],
        }, ensure_ascii=False)})
        system = (
            "You analyse crops of a home camera for the Track Things service. Each crop is one zone the user chose. "
            "For every zone: describe the scene in at most 12 Portuguese (PT-PT) words; for every thing to look for, "
            "say whether it is visible in that zone and, if so, where, in a few Portuguese words (e.g. 'à esquerda, junto ao portátil'); "
            "answer every sensor question that belongs to that zone with yes, no or unsure, plus brief evidence in Portuguese. "
            "Be literal and conservative: if you cannot see it clearly, it is not visible and the answer is unsure. "
            "Never identify people; you may say 'uma pessoa', 'uma criança' or 'um adulto'."
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
        system = (
            "You are the Track Things assistant inside the Altice home app. Answer in European Portuguese (PT-PT), "
            "in one or two natural sentences, using only the memory provided: where and when each thing was last seen, "
            "and recent events. Give times as 'às 8h42'. If the thing was never seen, say so plainly. Never invent. "
            "Set thing_id to the id of the thing the answer is about, or an empty string."
        )
        schema = {"type": "object", "properties": {"answer": {"type": "string"}, "thing_id": {"type": "string"}},
                  "required": ["answer", "thing_id"], "additionalProperties": False}
        content = [{"type": "text", "text": json.dumps({"pergunta": question, "memoria": memory}, ensure_ascii=False)}]
        return self._call("ask", REASON_MODEL, system, content, schema, max_tokens=600, thinking_off=False)

    # ------------------------------------------------------------------ compile a sentence into a sensor
    def compile(self, sentence, zones, things):
        system = (
            "You turn one sentence written by a user in Portuguese into a virtual sensor for a home camera. "
            "A sensor watches one zone and asks one yes/no question that can be answered from a single still image of that zone "
            "(for example 'Há uma caneca em cima da secretária?', 'Está uma criança a trepar a estante?'). "
            "Choose the zone that best matches; if none matches, use the first zone. "
            "Mode 'when_true' (deadline ''): the action fires when the answer equals trigger_when. "
            "Mode 'not_by_deadline', for sentences with a time limit such as 'se o gato não beber água até às 18h': "
            "ask about the expected event ('O gato está a beber água da taça?'), set trigger_when to the answer that means it happened ('yes') "
            "and deadline to 'HH:MM'; the action fires if that answer was never seen before the deadline. "
            "Pick the action from the list; use 'notify' when the sentence only asks to be told. "
            "If the sentence names an object that is not in the list of things, put its short Portuguese name in new_thing, else ''. "
            "title: at most 6 Portuguese words. message: the notification in natural PT-PT, one short sentence. "
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
            "frase": sentence,
            "zonas": [{"zone_id": z["id"], "nome": z["name"]} for z in zones],
            "coisas": [{"thing_id": t["id"], "nome": t["name"]} for t in things],
            "acoes_possiveis": ACTIONS,
        }, ensure_ascii=False)}]
        return self._call("compile", REASON_MODEL, system, content, schema, max_tokens=800, thinking_off=False)
