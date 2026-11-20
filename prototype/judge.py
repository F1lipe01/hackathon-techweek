"""A local vision-language "judge" for the cases the detector leaves ambiguous. Opt-in, on this machine, offline.

    prototype/.venv-vlm/bin/python prototype/judge.py                 # 127.0.0.1:8767 (loads the model once)
    prototype/.venv-vlm/bin/python prototype/judge.py --ask "Is there a yellow book on the desk?" a.jpg b.jpg

Model: mlx-community/Qwen2-VL-2B-Instruct-4bit, a 4-bit MLX build of Qwen2-VL-2B-Instruct (Qwen team, Alibaba),
licence Apache-2.0 on both model cards (checked 19 Nov 2026; Qwen2.5-VL-3B was ruled out: its licence is the Qwen
Research licence, not open for commercial use). About 1.2 GB, in ~/.cache/huggingface; the revision is pinned below.
Its own environment (prototype/.venv-vlm, `pip install mlx-vlm`), so it can never change the text model's.

When it is called (prototype/edge.py): only when an active check of a thing ("is the book still on the desk?") finds
no match, on one tight crop of the place (320 x 240 around the thing's last box, enlarged to 640 x 480).
Measured on the M1 Pro (20 Nov 2026), on the book take's desk: on a 640 x 480 region it answered "no" with the book
there (the book is 116 x 40 px of it), about 3 s a call; on the tight crop "yes" with the book there and "no" after it
was taken, 1.5 s a call; loads in about 2 s; 1.6 GB resident, 3.8 GB peak. Its sentence is usually just the word. It answers yes, no or unsure, with one sentence. It never acts: the server turns
a "yes" or an "unsure" into a question to the family, and a "no" into a line in the activity.
API: POST /judge {"question", "images_b64": [...]} -> {"answer": "yes"|"no"|"unsure", "sentence", "ms"}; GET /health.
Memory: the machine has 16 GB shared with OWLv2, DINOv2 and Qwen3-1.7B; this model adds about 1.5 GB while loaded.
"""
import argparse
import base64
import json
import re
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

MODEL = "mlx-community/Qwen2-VL-2B-Instruct-4bit"
REVISION = "01af461cdb9574acc09084a0ef94e216e142b085"
PORT = 8767
PROMPT = ("These are {n} pictures of the same place in a home, taken about a second apart by the home's camera. "
          "Question: {q} Answer with one word first, yes, no or unsure, then one short sentence saying what you see.")

_model = {}
_lock = threading.Lock()


def load():
    if not _model:
        from huggingface_hub import snapshot_download
        from mlx_vlm import load as vlm_load
        from mlx_vlm.utils import load_config
        path = snapshot_download(MODEL, revision=REVISION)
        model, processor = vlm_load(path)
        _model.update(model=model, processor=processor, config=load_config(path))
    return _model


def judge(question, image_paths, max_tokens=60):
    from mlx_vlm import generate
    from mlx_vlm.prompt_utils import apply_chat_template
    m = load()
    prompt = apply_chat_template(m["processor"], m["config"], PROMPT.format(n=len(image_paths), q=question),
                                 num_images=len(image_paths))
    t0 = time.time()
    with _lock:
        out = generate(m["model"], m["processor"], prompt, image=[str(p) for p in image_paths], max_tokens=max_tokens,
                       verbose=False, temperature=0.0)
    text = (getattr(out, "text", out) or "").strip()
    first = re.match(r"\W*(yes|no|unsure)\b", text, re.I)
    answer = first.group(1).lower() if first else "unsure"
    sentence = re.sub(r"^\W*(yes|no|unsure)\W*", "", text, flags=re.I).strip() or text
    return {"answer": answer, "sentence": sentence[:200], "ms": round((time.time() - t0) * 1000)}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(200, {"ok": True, "model": MODEL, "loaded": bool(_model)}) if self.path == "/health" else self._send(404, {})

    def do_POST(self):
        if self.path != "/judge":
            return self._send(404, {})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            with tempfile.TemporaryDirectory() as d:
                paths = []
                for i, b64 in enumerate(body.get("images_b64", [])[:3]):
                    paths.append(Path(d) / f"{i}.jpg")
                    paths[-1].write_bytes(base64.b64decode(b64))
                self._send(200, judge(str(body.get("question", ""))[:200], paths))
        except Exception as e:  # noqa: BLE001
            self._send(500, {"error": str(e)[:200]})

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask")
    ap.add_argument("images", nargs="*")
    a = ap.parse_args()
    if a.ask:
        t0 = time.time()
        load()
        print(f"loaded in {time.time() - t0:.1f} s", flush=True)
        for _ in range(2):                     # the second call shows the warm time
            print(json.dumps(judge(a.ask, a.images)), flush=True)
        return
    load()
    print(f"judge ready on 127.0.0.1:{PORT} ({MODEL})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
