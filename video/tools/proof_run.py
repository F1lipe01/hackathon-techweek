"""One proof run: a lab take replayed through the real pipeline, recorded in one continuous take, with its log.

    video/tools/heavy.sh prototype/.venv/bin/python video/tools/proof_run.py book      # or face, nobody
    ... proof_run.py book --no-video                                                    # the run and its log only

What runs, all on this machine; only the inputs no camera can see are replayed:
  1. a private server (port 8790) in replay mode (prototype/replays/<name>.json): the take is its camera, read in real
     time at full resolution; the door, the phones and hand-switched devices are replayed at their moments in the take,
     each written "Replayed: ..." in the activity;
  2. the real edge service (prototype/edge.py: motion, OWLv2, DINOv2, YuNet + SFace), reading that camera;
  3. the recorder (video/tools/record_proof.mjs): the whole page, from the replay's start to a few seconds after its
     end, as video/out/proof/<name>.mp4.
Its data is a copy of the home's (things, fingerprints, rules, face templates) in video/out/proof/<name>-data, with
the activity, sightings and presence emptied, so the run starts clean and the home's own database is never touched.
The log of everything that happened (video/out/proof/<name>.log.txt and .json) is written from that copy at the end.
Device actions stay dry runs (TT_LIVE_ACTIONS is removed from the environment); the alarm is simulated.
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "prototype"
OUT = ROOT / "video" / "out" / "proof"
PORT = 8790
# The recorder needs playwright-core: NODE_PATH, or the first of these folders that holds it.
NODE_PATH = os.environ.get("NODE_PATH") or next(
    (str(d) for d in (ROOT / "video" / "node_modules", ROOT / "node_modules",
                      Path.home() / ".hermes" / "hermes-agent" / "node_modules") if (d / "playwright-core").is_dir()), "")


def get(path, timeout=5):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=timeout) as r:
        return json.loads(r.read())


def fresh_data(name):
    """A copy of the home's data, with the activity, the sightings and presence emptied."""
    data = OUT / f"{name}-data"
    shutil.rmtree(data, ignore_errors=True)
    data.mkdir(parents=True)
    src = sqlite3.connect(PROTO / "data" / "home.db")
    dst = sqlite3.connect(data / "home.db")
    src.backup(dst)
    src.close()
    for table in ("events", "sightings", "presence", "phones", "presence_state"):
        try:
            dst.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            pass
    dst.execute("DELETE FROM meta WHERE key IN ('alarm', 'photo_tasks')")
    dst.commit()
    dst.close()
    shutil.copytree(PROTO / "data" / "crops", data / "crops")
    for f in ("edge.db", "tt_devices.json"):
        if (PROTO / "data" / f).exists():
            shutil.copy2(PROTO / "data" / f, data / f)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=["book", "face", "nobody"])
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--tail", type=float, default=20.0, help="seconds to keep recording after the take ends")
    ap.add_argument("--judge", action="store_true", help="also run the local vision-language judge (prototype/judge.py)")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    spec_path = PROTO / "replays" / f"{a.name}.json"
    spec = json.loads(spec_path.read_text())
    data = fresh_data(a.name)
    env = {**os.environ, "TT_DATA": str(data), "TT_PORT": str(PORT), "TT_REPLAY": str(spec_path), "TT_TIMINGS": "demo"}
    env.pop("TT_LIVE_ACTIONS", None)
    env.pop("TT_DEVICES_FILE", None)
    logs = {k: open(OUT / f"{a.name}.{k}.out", "w") for k in ("server", "edge")}
    server = subprocess.Popen([str(PROTO / ".venv" / "bin" / "python"), str(PROTO / "server.py")], env=env,
                              stdout=logs["server"], stderr=subprocess.STDOUT)
    edge = judge = None
    if a.judge:
        judge = subprocess.Popen([str(PROTO / ".venv-vlm" / "bin" / "python"), str(PROTO / "judge.py")],
                                 stdout=open(OUT / f"{a.name}.judge.out", "w"), stderr=subprocess.STDOUT)
    try:
        for _ in range(60):
            try:
                st = get("/api/state")
                break
            except Exception:
                time.sleep(0.5)
        else:
            raise SystemExit("the server did not start")
        if st["settings"]["live_actions"]:
            raise SystemExit("live actions are on: refusing")
        duration = st["replay"]["duration"] - st["replay"]["from"]
        if spec.get("learn"):                     # camera views of the thing from another take, before the replay
            L = spec["learn"]
            subprocess.run([str(PROTO / ".venv-vision" / "bin" / "python"), str(PROTO / "edge.py"), "--server",
                            f"http://127.0.0.1:{PORT}", "--learn-video", str(ROOT / L["video"]), "--thing", L["thing"],
                            "--box", *[str(v) for v in L["box"]], "--every", str(L.get("every", 0.5))], env=env,
                           stdout=logs["edge"], stderr=subprocess.STDOUT, check=True)
        edge = subprocess.Popen([str(PROTO / ".venv-vision" / "bin" / "python"), str(PROTO / "edge.py"), "--server",
                                 f"http://127.0.0.1:{PORT}"], env=env, stdout=logs["edge"], stderr=subprocess.STDOUT)
        for _ in range(240):                     # the models load in 10-30 s
            if (OUT / f"{a.name}.edge.out").read_text().count("ready on"):
                break
            time.sleep(0.5)
        else:
            raise SystemExit("the edge service did not get ready")
        time.sleep(2)
        seconds = duration + a.tail
        if a.no_video:
            urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}/api/replay/start", method="POST"), timeout=5)
            time.sleep(seconds)
        else:
            subprocess.run(["node", str(ROOT / "video" / "tools" / "record_proof.mjs"), f"http://127.0.0.1:{PORT}",
                            str(OUT / f"{a.name}.mp4"), f"{seconds:.1f}", a.name], env={**env, "NODE_PATH": NODE_PATH},
                           check=True)
        rep = get("/api/replay")
    finally:
        for p in (edge, server, judge):
            if p:
                p.terminate()
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
    write_log(a.name, data, spec, rep)


def write_log(name, data, spec, rep):
    db = sqlite3.connect(data / "home.db")
    rows = db.execute("SELECT ts, kind, text, data FROM events ORDER BY ts").fetchall()
    t0 = rep.get("started_at") or (rows[0][0] if rows else 0)
    off = spec.get("from", 0)
    out, lines = [], [f"Proof run '{name}': {spec['video']} replayed from {off} s through the real pipeline.",
                      f"Note: {spec.get('note', '')}", "", "time      take t   kind      what happened"]
    for ts, kind, text, extra in rows:
        e = json.loads(extra or "{}")
        t = ts - t0 + off if t0 else None
        out.append({"time": time.strftime("%H:%M:%S", time.localtime(ts)), "take_t": round(t, 1) if t is not None else None,
                    "kind": kind, "text": text, **{k: e[k] for k in ("evidence", "rule_id", "title") if k in e}})
        lines.append(f"{out[-1]['time']}  {('%6.1f' % t) if t is not None else '     -'} s  {kind:9s} {text}"
                     + (f"\n{'':29s}evidence: {e['evidence']}" if e.get("evidence") and kind in ("alert", "unsure") else ""))
    (OUT / f"{name}.log.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (OUT / f"{name}.log.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(l for l in lines if any(k in l for k in ("alert", "unsure", "handled", "Replayed", "Home:", "learnt", "info"))))


if __name__ == "__main__":
    sys.exit(main())
