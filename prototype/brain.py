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
import unicodedata
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


def _plain(text):
    """Lower case, accents removed: 'Até às 20h' -> 'ate as 20h'."""
    return unicodedata.normalize("NFKD", str(text).lower()).encode("ascii", "ignore").decode()


# ---------------------------------------------------------------------- European Portuguese (PT-PT)
# The local model learnt more Brazilian than European Portuguese and slips into "você", "câmera", "celular" and the
# gerund. Every Portuguese answer goes through pt_pt(): the words become those of Portugal, "você" + verb becomes the
# verb in the "tu" form ("Você deixou" -> "Deixaste"), and "está procurando" becomes "está a procurar".
_PT_WORDS = {"câmera": "câmara", "câmeras": "câmaras", "caméra": "câmara", "caméras": "câmaras", "camêra": "câmara",
             "camera": "câmara", "cameras": "câmaras", "camara": "câmara", "camaras": "câmaras", "celular": "telemóvel", "celulares": "telemóveis", "tela": "ecrã",
             "usuário": "utilizador", "usuários": "utilizadores", "cachorro": "cão", "cachorros": "cães",
             "registrado": "registado", "registrada": "registada", "registrados": "registados",
             "registradas": "registadas", "registrar": "registar", "registrou": "registou", "cadastrado": "registado",
             "cadastrada": "registada", "cadastrar": "registar", "equipe": "equipa", "banheiro": "casa de banho",
             "geladeira": "frigorífico", "xícara": "chávena", "contato": "contacto", "arquivo": "ficheiro", "oi": "olá",
             "detectado": "detetado", "detectada": "detetada", "detectar": "detetar", "ônibus": "autocarro"}
_TU = {"está": "estás", "tem": "tens", "é": "és", "vai": "vais", "foi": "foste", "viu": "viste", "fez": "fizeste",
       "pôs": "puseste", "quer": "queres", "sabe": "sabes", "pode": "podes", "deve": "deves", "vê": "vês",
       "tinha": "tinhas", "estava": "estavas", "saiu": "saíste", "esteve": "estiveste", "teve": "tiveste",
       "disse": "disseste", "precisa": "precisas"}
_NOT_GERUND = {"quando", "mundo", "segundo", "fundo", "lindo", "redondo", "profundo"}


def _tu_verb(verb):
    """The 'tu' form of a verb a model wrote after 'você' (3rd person), or None when it does not look like a verb."""
    v = verb.lower()
    if v in _TU:
        return _TU[v]
    if len(v) < 3:
        return None
    for end, tu in (("ou", "aste"), ("eu", "este"), ("iu", "iste")):   # deixou, esqueceu, partiu
        if v.endswith(end):
            return v[:-2] + tu
    return v + "s" if v.endswith(("a", "e")) else None                    # procura, esquece


def _same_case(new, old):
    return new[:1].upper() + new[1:] if old[:1].isupper() else new


def pt_pt(text):
    """A Portuguese answer, as written in Portugal."""
    if not text:
        return text
    out = re.sub(r"\b(para|a|de|por|sem)\s+voc[êe]\b", lambda m: m.group(1) + " ti", text, flags=re.I)
    out = re.sub(r"\bcom\s+voc[êe]\b", lambda m: _same_case("contigo", m.group(0)), out, flags=re.I)
    out = re.sub(r"\b(\w+[aei]r)\s+voc[êe]\b", r"\1-te", out, flags=re.I)        # "ajudar você" -> "ajudar-te"
    used_voce = out != text

    def voce(m):
        adverbs, verb = m.group(2) or "", m.group(3)
        tu = _tu_verb(verb)
        new = (adverbs + tu) if tu else ("tu " + adverbs + verb)
        return _same_case(new, m.group(1))

    out2 = re.sub(r"\b(voc[êe])\s+((?:(?:não|nunca|já|ainda|também)\s+)*)(\w+)", voce, out, flags=re.I)
    out2 = re.sub(r"\bvoc[êe]\b", lambda m: _same_case("tu", m.group(0)), out2, flags=re.I)
    if out2 != out or used_voce:   # "tu" from here on: "o seu livro" becomes "o teu livro"
        for a, b in (("seus", "teus"), ("suas", "tuas"), ("seu", "teu"), ("sua", "tua")):
            out2 = re.sub(rf"\b{a}\b", lambda m, b=b: _same_case(b, m.group(0)), out2, flags=re.I)
    out = re.sub(r"\b(estou|estás|está|estamos|estão|estava|estavas|estavam|esteve|continua|continuas|continuam|fica|"
                 r"ficou|anda|andas)\s+(\w+?)ndo\b",
                 lambda m: m.group(0) if (m.group(2) + "ndo").lower() in _NOT_GERUND
                 else f"{m.group(1)} a {m.group(2)}r", out2, flags=re.I)
    out = re.sub(r"\b(\w+)\b", lambda m: _same_case(_PT_WORDS[m.group(1).lower()], m.group(1))
                 if m.group(1).lower() in _PT_WORDS else m.group(1), out)
    # the gender of the places ("no mesa" -> "na mesa"), "à 17:12" -> "às 17:12", "chegou em casa" -> "chegou a casa"
    out = re.sub(r"\b(?:no|em o)\s+(mesa|secretária|prateleira|estante|sala|cozinha|entrada|porta|varanda|divisão)\b",
                 r"na \1", out, flags=re.I)
    out = re.sub(r"\b(?:na|em a)\s+(sofá|banco|quarto|corredor|hall|átrio)\b", r"no \1", out, flags=re.I)
    out = re.sub(r"\bà\s+(?!0?1:)(\d{1,2}[:h]\d{2})", r"às \1", out)
    return re.sub(r"\b(cheg\w*)\s+em\s+casa\b", r"\1 a casa", out, flags=re.I)


_FOREIGN = re.compile(r"[\u0400-\u04ff\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")   # Cyrillic, CJK, Hangul


# ---------------------------------------------------------------------- places, who, times (the rule templates)
# Each camera stands for one place, named after its room ("Kitchen 1", "Kitchen 2"); a pet's bowl is either a
# registered thing or the place of the camera that watches it. These words give each kind of place one key, in English
# and Portuguese, so "cozinha" finds the camera "Kitchen 1".
PLACE_SYNONYMS = {
    "food bowl": ("food bowl", "bowl of food", "taca da comida", "tigela da comida", "comedouro", "food", "comida",
                  "comer", "comeu", "eat", "eaten", "eating"),
    "water bowl": ("water bowl", "bowl of water", "taca da agua", "tigela da agua", "bebedouro", "water", "agua",
                   "drink", "drunk", "drinking", "beber", "bebeu"),
    "kitchen": ("kitchen", "cozinha"),
    "living room": ("living room", "lounge", "sala de estar", "sala"),
    "entrance": ("entrance", "entry", "front door", "hallway", "hall", "door", "entrada", "porta", "atrio"),
    "bedroom": ("bedroom", "quarto"),
    "balcony": ("balcony", "varanda"),
    "bathroom": ("bathroom", "casa de banho"),
}


def place_key(name):
    """One key per kind of place: 'Cozinha 1' -> 'kitchen 1', 'the food bowl' -> 'food bowl', 'Work Room' -> 'work room'."""
    p = re.sub(r"^(the|a|an|o|os|as)\s+", "", _plain(name).strip())
    m = re.match(r"^(.*?)(\s+\d+)?$", p)
    base, num = m.group(1), m.group(2) or ""
    key = next((k for k, words in PLACE_SYNONYMS.items() if base == k or base in words), base)
    return key + num


def place_matches(rule_place, *names):
    """Does a sighting at one of `names` (the camera's place, the surface or thing it was on or near) count as being at
    the rule's place? An empty rule place means anywhere at home; 'kitchen' matches 'Kitchen 1' and 'Kitchen 2'."""
    if not rule_place:
        return True
    k = place_key(rule_place)
    return any(n and (place_key(n) == k or place_key(n).startswith(k + " ")) for n in names)


WHO_WORDS = {"dog": ("dog", "dogs", "cao", "caes", "cadela", "cachorro"),
             "cat": ("cat", "cats", "gato", "gata", "gatos"),
             "child": ("child", "children", "kid", "kids", "crianca", "criancas", "miudo", "miudos", "miuda",
                       "miudas", "filho", "filha", "filhos", "filhas"),
             "person": ("person", "someone", "somebody", "anyone", "anybody", "pessoa", "alguem")}
BEINGS = tuple(WHO_WORDS)
_TIME = r"(midday|noon|midnight|meio-dia|meio dia|meia-noite|meia noite|\d{1,2}(?:[:h.]\d{2})?(?::\d{2})?(?:\s*(?:am|pm)|h\b)?)"
_ART = r"(?:(?:as|a|ao|o|the)\s+)?"
_BY = re.compile(r"\b(?:by|before|until|till|ate|antes d[aoe]s?)\s+" + _ART + _TIME)
_FROM = re.compile(r"\b(?:from|after|since|desde|a partir d[aoe]s?|depois d[aoe]s?)\s+" + _ART + _TIME)
_BETWEEN = re.compile(r"\b(?:between|entre)\s+" + _ART + _TIME + r"\s+(?:and|e)\s+" + _ART + _TIME)
_WITHIN = re.compile(r"\b(?:in|for|within|em|durante|ha|nas ultimas|in the last|over the last)\s+(?:the\s+)?"
                     r"(\d+(?:[.,]\d+)?)\s*(h|hrs?|hours?|horas?|min|mins|minutes?|minutos?)\b")
_LEAVE = re.compile(r"\b(leave|leaving|go out|going out|get out|head out|step out|walk out)\b.*\bwithout\b|"
                    r"\bwithout\b.*\b(leave|leaving|go out|going out)\b|"
                    r"\b(sair|saio|sais|saires|sairmos|saimos)\b.*\bsem\b|\bsem\b.*\b(sair|saio)\b|"
                    r"\bforg[eo]t|\besquec")
_NOBODY = re.compile(r"\b(nobody|no one|no-one|ninguem)\b")
_NEG = re.compile(r"\b(not|never|nao|nunca)\b|n't\b")


def hhmm(token):
    """'20:00', '8 pm', '20h', 'meio-dia' -> 'HH:MM' (or 'HH:MM:SS' when seconds are given); '' if it is not a time."""
    t = _plain(token).strip()
    named = {"midday": "12:00", "noon": "12:00", "meio-dia": "12:00", "meio dia": "12:00", "midnight": "00:00",
             "meia-noite": "00:00", "meia noite": "00:00"}
    if t in named:
        return named[t]
    m = re.match(r"^(\d{1,2})(?:[:h.](\d{2}))?(?::(\d{2}))?\s*(am|pm|h)?$", t)
    if not m:
        return ""
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(4)
    h += 12 if ap == "pm" and h < 12 else 0
    h = 0 if ap == "am" and h == 12 else h
    if h > 23 or mi > 59:
        return ""
    return f"{h:02d}:{mi:02d}" + (f":{int(m.group(3)):02d}" if m.group(3) else "")


def _who(plain):
    return next((k for k, words in WHO_WORDS.items() if any(re.search(rf"\b{w}\b", plain) for w in words)), "")


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
            "(English, or European Portuguese as written in Portugal if the question is in Portuguese: impersonal or "
            "'tu', never 'você'; 'câmara', 'telemóvel'), in one or two natural sentences, using only "
            "the memory provided: where and when each thing was last seen, and recent events. Give times as '08:42'. "
            "If the thing was never seen, say so plainly. Never invent. "
            "Set thing_id to the id of the thing the answer is about, or an empty string."
        )
        schema = {"type": "object", "properties": {"answer": {"type": "string"}, "thing_id": {"type": "string"}},
                  "required": ["answer", "thing_id"], "additionalProperties": False}
        content = [{"type": "text", "text": json.dumps({"question": question, "memory": memory}, ensure_ascii=False)}]
        out = self._call("ask", REASON_MODEL, system, content, schema, max_tokens=600, thinking_off=False)
        if _lang(question) == "pt":
            out["answer"] = pt_pt(out["answer"])
        return out

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
    LOCAL_KINDS = ("left_for", "nobody_for", "someone_arrives", "seen_in", "leave_without", "not_by", "nobody_by")
    NEW_KINDS = ("leave_without", "not_by", "nobody_by")
    EXTRA_KEYS = ("who", "by", "from", "within_s", "grace_s", "min_s")

    def compile_local(self, sentence, things, places=()):
        """Compile a sentence once into a rule that the rules engine evaluates locally, at no cost per check.
        places: the places the home's cameras stand for ("Work Room", "Kitchen 1")."""
        mode = self.text_mode()
        if mode == "local":
            rule = (self._local_compile_local(sentence, things, places)
                    or self._sim_compile_local(sentence, things, places))
        elif mode == "templates":
            rule = self._sim_compile_local(sentence, things, places)
        else:
            rule = self._claude_compile_local(sentence, things, places)
        rule["lang"] = _lang(sentence)
        if rule["lang"] == "pt":
            rule["title"], rule["message"] = pt_pt(rule["title"]), pt_pt(rule["message"])
        return rule

    def _claude_compile_local(self, sentence, things, places):
        system = (
            "You turn one sentence from a home user into a rule for the ThingTracker rules engine. The camera detects the "
            "home's things, the places they are on (desk, table, shelf, sofa, bench), people, children, dogs and cats; "
            "each camera stands for one place of the home (its room). The front door has a contact sensor. Kinds: "
            "left_for (a thing stays on a place for N minutes), nobody_for (no movement or people for N minutes), "
            "someone_arrives (a person, or who, appears after none was seen for N minutes), seen_in (a thing, or who, is "
            "seen, optionally at a place), leave_without (the door opens while the thing is still at home: 'if I leave "
            "home without X'), not_by (who, or the thing id in who, has not been at a place by 'HH:MM' in by, or within "
            "within_s seconds), nobody_by (nobody was in a place between from and by, 'HH:MM'). who: dog, cat, child, "
            "person, a thing id or ''. For not_by and nobody_by, place is a camera place or a registered thing (a bowl); "
            "for the others one of the surfaces or ''. Unused fields: '' or 0. grace_s: 60 for leave_without. "
            "Actions: notify, plug_off, light_red, light_blue, light_green. Use the given thing ids. Title: short, in the "
            "language of the sentence (European Portuguese if Portuguese). Message: what the user is told when it fires."
        )
        schema = {"type": "object", "properties": {
            "title": {"type": "string"}, "kind": {"type": "string", "enum": list(self.LOCAL_KINDS)},
            "thing_id": {"type": "string"}, "place": {"type": "string"}, "minutes": {"type": "number"},
            "action": {"type": "string", "enum": ["notify", "plug_off", "light_red", "light_blue", "light_green"]},
            "message": {"type": "string"}, "cooldown_s": {"type": "integer"},
            "who": {"type": "string"}, "by": {"type": "string"}, "from": {"type": "string"},
            "within_s": {"type": "integer"}, "grace_s": {"type": "integer"}, "min_s": {"type": "integer"}},
            "required": ["title", "kind", "thing_id", "place", "minutes", "action", "message", "cooldown_s",
                         *self.EXTRA_KEYS],
            "additionalProperties": False}
        content = [{"type": "text", "text": json.dumps({"sentence": sentence, "camera_places": list(places), "things": [
            {"id": t["id"], "name": t["name"]} for t in things]}, ensure_ascii=False)}]
        rule = self._call("compile", REASON_MODEL, system, content, schema, max_tokens=800, thinking_off=False)
        hint = self._sim_compile_local(sentence, things, places)
        if rule["kind"] in self.NEW_KINDS and rule["kind"] == hint["kind"]:   # times and places as the sentence says
            rule.update({k: hint[k] for k in (*self.EXTRA_KEYS, "place") if k in hint})
        rule["grace_s"] = rule.get("grace_s") or 60
        return rule

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

    def _by_camera(self, e):
        """Did the camera record this event? Only its sightings: the door, alerts and sensor checks come from the
        rules engine, and earlier answers of the assistant ('"question": answer') are neither."""
        if "kind" in e:
            return e["kind"] == "seen"
        return not e["text"].startswith('"') and not self._APP_EVENT.search(e["text"])

    def _events(self, memory, names=None, camera=True):
        """Recent events as lines, oldest first: what the camera recorded (camera=True) or what was done in the app.
        Only those naming one of `names` when given."""
        return [f"- {self._day(e['when'])}: {e['text']}" for e in memory["recent_events"]
                if (self._by_camera(e) if camera else bool(self._APP_EVENT.search(e["text"])))
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

    # "Where is my book?" about a thing nobody registered: the answer says so and how to add it, from the code, so
    # a small model never invents a place for it ("O livro está a ser tratado pelo telemóvel").
    _ASK_THING = re.compile(
        r"^(?:onde (?:é que )?(?:está|estão|esta|estao|fica|ficam|anda|andam|deixei|pus|guardei)|quando (?:é que )?"
        r"(?:vi|viste)|viste|vês|ves|encontras|where (?:is|are|did i (?:leave|put))|have you seen|did you see|"
        r"when did i (?:last )?see)\s+(.+?)[\s?.!]*$", re.I)
    _NOT_A_THING = {"casa", "home", "câmara", "camara", "camera", "tudo", "everything", "alguém", "someone", "it", "isso"}
    _PT_ART = {"o": ("o", "lo", "o"), "a": ("a", "la", "a"), "os": ("os", "los", "os"), "as": ("as", "las", "as"),
               "meu": ("o teu", "lo", "o"), "minha": ("a tua", "la", "a"), "meus": ("os teus", "los", "os"),
               "minhas": ("as tuas", "las", "as")}

    def _unknown_thing(self, question, lang):
        """The answer for a question about one thing that is not registered, or None if it is not such a question."""
        m = self._ASK_THING.match(question.strip())
        if not m:
            return None
        words = m.group(1).strip().split()
        if len(words) > 2 and words[0].lower() in ("o", "a", "os", "as") and words[1].lower() in self._PT_ART:
            words = words[1:]                     # "as minhas chaves": the possessive decides ("as tuas chaves")
        first = words[0].lower() if words else ""
        noun = " ".join(words[1:] if first in (*self._PT_ART, "my", "the", "your") and len(words) > 1 else words)
        if not noun or noun.lower() in self._NOT_A_THING or len(noun.split()) > 4:
            return None
        if lang == "pt":
            art, inf, imp = self._PT_ART.get(first.lower(), ("", "lo", "o"))
            return (f"Ainda não conheço {art + ' ' if art else ''}{noun}. Podes adicioná-{inf} no separador Things: "
                    f"carrega em + e mostra-{imp} à câmara durante alguns segundos.")
        them = noun.lower().endswith("s")
        return (f"I don't know your {noun} yet. Add {'them' if them else 'it'} in the Things tab: press + and show "
                f"{'them' if them else 'it'} to the camera for a few seconds.")

    def _local_ask(self, question, memory):
        """The code decides which things the question is about (and so thing_id and candidates);
        the model writes the answer, in the user's language, from the facts it is given and nothing else."""
        lang = _lang(question)
        things = memory["things"]
        by_id = {t["thing_id"]: t for t in things}
        ids = self._match(question, things)
        unknown = None if ids else self._unknown_thing(question, lang)
        if unknown:
            return {"answer": unknown, "thing_id": ""}
        day = None
        now_ = f"Now: {self._day(memory['now'])}."
        system = (
            "You are the ThingTracker assistant in the Altice home app. A home camera recognises the things the family "
            "registered and records where and when it saw them. Use only the facts given; never invent a place, a time "
            "or a sighting. Reply in " +
            ("European Portuguese, as written in Portugal: write impersonally or address the user as 'tu', never "
             "'você'; say 'câmara', 'telemóvel', 'ecrã', 'está a procurar' (never 'câmera', 'celular', 'tela', "
             "'procurando')" if lang == "pt" else "English") +
            ", in one or two short, natural sentences, without lists. Write times as 08:42. "
            "Write the name of each thing exactly as it is given."
        )
        tail = "\n\nResponde em português de Portugal (nunca 'você', nunca 'câmera')." if lang == "pt" else ""
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
                          "example: " + ("\"Ainda não conheço as tuas chaves. Podes adicioná-las no separador Things.\" "
                                         if lang == "pt" else "\"I don't know your keys yet. You can add them in the Things tab.\" ") +
                          "If it is a general question about the home, answer from the events; if there are none, say so.")
        answer = (self._local(system, prompt + tail, 120, False) or "").strip().strip('"').strip()
        sentences = list(dict.fromkeys(re.split(r"(?<=[.!?])\s+", answer)))  # small models sometimes repeat themselves
        answer = " ".join(sentences[:3])
        if not answer:
            return None  # the service failed: the template answers instead
        q = question.strip().rstrip("?").lower()
        if len(q) > 8 and answer.lower().startswith(q):        # the model repeated the question first
            answer = answer[len(q):].lstrip(" ?:.,-").strip() or answer
        if lang == "pt":
            answer = pt_pt(answer)
        if _FOREIGN.search(answer):    # a small model sometimes slips into another script ("na 厨房"): use the facts
            print("local answer replaced (another script):", answer)
            if len(ids) == 1:
                return {"answer": self._fact_answer(by_id[ids[0]], lang), "thing_id": ids[0]}
            if len(ids) > 1:
                return {"answer": self._which_one([by_id[i]["name"] for i in ids], lang), "thing_id": "", "candidates": ids}
            return {"answer": self._camera_summary(self._camera_events(memory, day), day, lang), "thing_id": ""}
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
        return [e for e in memory["recent_events"] if self._by_camera(e)
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
            m = re.match(r"(.+) seen (?:on the (\w+)|in the room)(?: \((.+)\))?", e["text"])
            if m:
                place, cam = m.group(2) or "room", m.group(3)   # cam: the camera's place, when not the kit camera's
                if lang == "pt":
                    where = f"em {cam}" if cam and place == "room" else self.PLACE_PT.get(place, f"em {place}")
                else:
                    where = f"in the {cam}" if cam and place == "room" else "in the room" if place == "room" else f"on the {place}"
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
                "bench": "no banco", "room": "na divisão"}

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
        zone, room = last["zone"].lower(), last.get("room") or ""
        place = (f"em {room}" if zone == "room" and room else
                 self.PLACE_PT.get(zone, f"em {last['zone']}") + (f" ({room})" if room else ""))
        return f"A câmara viu {t['name']} pela última vez {place}, {day} às {hhmm}."

    def _local_compile_local(self, sentence, things, places=()):
        """The model chooses the kind and writes the title and the message; _literal_fixes() then sets what the
        sentence states literally (times, places, who, the thing), so a slip of the small model cannot break a rule."""
        system = (
            "You turn one sentence from a home user into a rule for the ThingTracker rules engine. The home camera "
            "recognises the registered things, the place each one is on (desk, table, shelf, sofa, bench), people, "
            "children, dogs and cats. The front door has a contact sensor.\n"
            "Kinds:\n"
            "- leave_without: the user leaves home (the door opens) while a thing is still at home ('if I leave home "
            "without X', 'if I forget X', 'se eu sair de casa sem X');\n"
            "- not_by: a dog, a cat, a person or a thing has not been at a place by a time ('if the dog has not been "
            "at the food bowl by 20:00');\n"
            "- nobody_by: nobody has been in a place by a time ('if nobody is in the kitchen by midday');\n"
            "- left_for: a thing stays on a place for N minutes ('if the book stays on the table for 30 minutes');\n"
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
            '{"title": "Keys left at home", "kind": "leave_without", "thing_id": "keys", "place": "", "minutes": 10, '
            '"action": "notify", "message": "You went out without your keys.", "cooldown_s": 300}'
        )
        listed = "\n".join(f'- id "{t["id"]}": {t["name"]}' for t in things) or "- none"
        pt = ("\n\nEscreve o title e a message em português de Portugal (tu ou impessoal, nunca 'você')."
              if _lang(sentence) == "pt" else "")
        raw = self._local(system, f"Registered things:\n{listed}\n\nSentence: {sentence}{pt}", 250, True)
        try:
            rule = self._valid_rule(self._flat_json(raw), things)
        except (TypeError, ValueError, KeyError):
            return None  # not valid JSON or not a valid rule: the template compiles it instead
        return self._literal_fixes(rule, sentence, things, places)

    # Words that name each place, in English and Portuguese.
    PLACE_WORDS = {"desk": ["desk", "secretária", "secretaria"], "table": ["table", "mesa"],
                   "shelf": ["shelf", "prateleira", "estante"], "sofa": ["sofa", "sofá"], "bench": ["bench", "banco"]}

    def _literal_fixes(self, rule, sentence, things, places=()):
        """What the sentence states literally wins over the model: a light or plug action, a number of minutes,
        a place, a thing named by its words, a kind word (nobody, arrives, without, stays), a time, a dog or a cat.
        The model writes the title and the message, and chooses the kind when no keyword says it."""
        low = sentence.lower()
        hint = self._sim_compile_local(sentence, things, places)
        if "_" in rule["title"] or rule["title"].lower() in self.LOCAL_KINDS:  # the kind echoed as a title
            rule["title"] = hint["title"]
        if hint["action"] != "notify":
            rule["action"] = hint["action"]
        if hint["kind"] != "seen_in":  # the templates found a kind word: nobody, someone arrives, stays, left...
            rule["kind"] = hint["kind"]
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
        if hint["kind"] in self.NEW_KINDS or hint.get("who"):
            # leave home without, not by, nobody by, a dog or a cat: the sentence's words decide, never the small model
            rule["kind"] = hint["kind"]
            rule.update({k: hint[k] for k in (*self.EXTRA_KEYS, "place", "thing_id") if k in hint})
            if hint["kind"] == "leave_without":
                rule["message"] = hint["message"]
        elif rule["kind"] in self.NEW_KINDS:  # the model chose a kind the sentence's words do not support
            rule["kind"] = hint["kind"]
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

    def _place_in(self, plain, things, places, skip=None):
        """The place a sentence names, for the kinds that watch a place: a camera place or a registered thing named
        in it, or a kind of place (kitchen, food bowl, entrance, in English or Portuguese), resolved to the camera place
        or thing of that kind when the home has one. '' when it names none (anywhere at home)."""
        named = list(places) + [t["name"] for t in things if t["id"] != skip]
        for name in named:
            if _plain(name).strip() and re.search(rf"\b{re.escape(_plain(name).strip())}\b", plain):
                return name
        for key, words in PLACE_SYNONYMS.items():
            if any(re.search(rf"\b{re.escape(w)}\b", plain) for w in (key, *words)):
                return next((n for n in named if place_matches(key, n)), key.capitalize())
        return ""

    def _sim_compile_local(self, sentence, things, places=()):
        """Keyword templates in English and Portuguese, so the demo runs with AI off (no cost)."""
        low = sentence.lower()
        plain = _plain(sentence)
        alias = {"keys": ["key", "chave"], "wallet": ["carteira"], "glasses": ["óculos", "oculos"], "phone": ["telemóvel", "telemovel", "telefone"],
                 "mug": ["caneca", "chávena", "cup"], "laptop": ["portátil", "portatil", "computador"], "remote": ["comando"],
                 "bottle": ["garrafa"], "waterbottle": ["garrafa", "bottle"], "backpack": ["mochila"]}
        ids = self._match(sentence, [{"thing_id": t["id"], "name": t["name"]} for t in things])
        thing = (next(t for t in things if t["id"] == ids[0]) if len(ids) == 1 else
                 next((t for t in things if t["name"].lower() in low or t["id"] in low
                       or any(a in low for a in alias.get(t["id"], []))), None))
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
        lang, who = _lang(sentence), _who(plain)
        between = _BETWEEN.search(plain)
        by = hhmm(between.group(2) if between else (_BY.search(plain) or [None, ""])[1])
        frm = hhmm(between.group(1) if between else (_FROM.search(plain) or [None, ""])[1])
        w = _WITHIN.search(plain)
        within = int(float(w.group(1).replace(",", ".")) * (3600 if w.group(2).startswith("h") else 60)) if w else 0
        title = sentence.strip().rstrip(".")
        title = (title[:38] + "…") if len(title) > 40 else title
        message, extra = sentence.strip(), {}
        if _LEAVE.search(plain):
            # "tell me if I leave home without my book", "avisa-me se eu sair de casa sem o livro"
            kind, extra = "leave_without", {"grace_s": 60}
            if thing:
                title = (f"Sair de casa sem: {thing['name']}" if lang == "pt"
                         else f"Leaving home without the {thing['name'].lower()}")
                message = (f"A porta abriu e “{thing['name']}” ainda está em casa." if lang == "pt"
                           else f"The door opened and the {thing['name'].lower()} is still at home.")
        elif _NOBODY.search(plain) and by:
            # "tell me if nobody has been in the kitchen by midday": from 06:00 when the sentence gives no start
            kind, place = "nobody_by", self._place_in(plain, things, places)
            extra = {"from": frm or "06:00", "by": by}
        elif (who or thing) and _NEG.search(plain) and (by or within):
            # "tell me if the dog has not been at the food bowl by 20:00", "... at the water bowl in 12 hours"
            kind = "not_by"
            subject = who or thing["id"]
            place = self._place_in(plain, things, places, skip=None if who else thing["id"])
            extra = {"who": subject, "by": "" if within else by, "within_s": within, "min_s": 0}
            thing = None if who else thing
        elif any(w in low for w in ("nobody", "no one", "ninguém", "ninguem", "empty", "vazi")):
            kind = "nobody_for"
        elif any(w in low for w in ("arrive", "comes in", "someone", "chega", "entra", "alguém", "alguem")):
            kind = "someone_arrives"
            if who in ("child", "dog", "cat"):   # "tell me when a child arrives home": no picture is ever sent
                extra = {"who": who}
                minutes = minutes if m else 30
        elif thing and any(w in low for w in ("left", "leave", "stays", "deixad", "esquec", "fica")):
            kind = "left_for"
        else:
            kind = "seen_in"
            if who and not thing:                # "tell me when the dog is on the sofa"
                extra = {"who": who}
                place = place or self._place_in(plain, things, places)
        return {"title": title, "kind": kind, "thing_id": thing["id"] if thing else "", "place": place,
                "minutes": minutes, "action": action, "message": message, "cooldown_s": 300, **extra}

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
        if _lang(question) == "pt":
            ids = [t["thing_id"] for t in found] or self._match(question, memory["things"])
            if ids:
                t = next(x for x in memory["things"] if x["thing_id"] == ids[0])
                return {"answer": self._fact_answer(t, "pt"), "thing_id": t["thing_id"]}
            return {"answer": self._unknown_thing(question, "pt") or "Não encontrei isso na memória da casa.",
                    "thing_id": ""}
        if found:
            t, last = found[0], found[0]["last_seen"]
            if not last:
                return {"answer": f"I haven't seen your {t['name'].lower()} yet.", "thing_id": t["thing_id"]}
            where = f", {last['where']}" if last.get("where") else ""
            room = f", {last['room']}" if last.get("room") else ""
            return {"answer": f"On the {last['zone'].lower()}{room}, at {last['when'].split(' ')[-1]}.",
                    "thing_id": t["thing_id"]}
        return {"answer": self._unknown_thing(question, "en") or "I couldn't find that in the home's memory.",
                "thing_id": ""}

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
