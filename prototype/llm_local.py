"""ThingTracker's local text model: a small open-weight model served on this machine, offline, at no cost per call.

    prototype/.venv-llm/bin/python prototype/llm_local.py      # http://127.0.0.1:8766, loads the model once

    POST /generate {system, prompt, max_tokens, json: bool}  ->  {text, ms, tokens}
    GET  /health                                              ->  {ok, model}

Model: Qwen3-1.7B (Apache-2.0), 4-bit MLX build from mlx-community, about 1 GB, run with mlx-lm on Apple silicon.
The first run downloads it from Hugging Face into ~/.cache/huggingface; later runs load it from there, offline.
"Thinking" is switched off in the chat template, so the model answers directly.
With json=true the reply is primed with "{" and trimmed to the first complete JSON object.
"""
import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from huggingface_hub import snapshot_download
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler

MODEL = os.environ.get("TT_LLM_MODEL", "mlx-community/Qwen3-1.7B-4bit")
REVISION = os.environ.get("TT_LLM_REVISION", "3b1b1768f8f8cf8351c712464f906e86c2b8269e" if "TT_LLM_MODEL" not in os.environ else None)
PORT = int(os.environ.get("TT_LLM_PORT", "8766"))
MAX_TOKENS = 600


def model_path():
    """The cached copy when there is one (works offline), otherwise a download from Hugging Face."""
    try:
        return snapshot_download(MODEL, revision=REVISION, local_files_only=True)
    except Exception:
        return snapshot_download(MODEL, revision=REVISION)


t0 = time.time()
model, tokenizer = load(model_path())
LOAD_S = time.time() - t0
lock = threading.Lock()  # one generation at a time: the model and the GPU are shared


def first_json_object(text):
    """The first balanced {...} in the text, or the text unchanged."""
    start = text.find("{")
    if start < 0:
        return text
    depth, in_str, esc = 0, False, False
    for i, ch in enumerate(text[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]


def run(system, prompt, max_tokens=200, as_json=False):
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    chat = tokenizer.apply_chat_template(messages, add_generation_prompt=True, enable_thinking=False, tokenize=False)
    if as_json:
        chat += "{"
    with lock:
        t = time.time()
        out = generate(model, tokenizer, chat, max_tokens=max(1, min(int(max_tokens), MAX_TOKENS)),
                       sampler=make_sampler(temp=0.0))
        ms = int((time.time() - t) * 1000)
    out = re.sub(r"<think>.*?</think>", "", out, flags=re.S).strip()
    if as_json:
        out = first_json_object("{" + out)
    return {"text": out, "ms": ms, "tokens": len(tokenizer.encode(out))}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "model": MODEL, "load_s": round(LOAD_S, 1)})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/generate":
            return self._send(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            prompt = str(req.get("prompt", ""))
            if not prompt:
                return self._send(400, {"error": "prompt is required"})
            self._send(200, run(str(req.get("system", "")), prompt, req.get("max_tokens", 200), bool(req.get("json"))))
        except Exception as e:  # a bad request must not stop the service
            self._send(500, {"error": str(e)[:300]})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    run("", "Hi", max_tokens=1)  # warm-up, so the first real question is not slower than the rest
    print(f"{MODEL} loaded in {LOAD_S:.1f} s; listening on http://127.0.0.1:{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
