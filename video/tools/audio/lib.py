"""Search and download from the music and sfx library, and generate the few sfx it lacks.

Environment: LIB_URL and LIB_KEY_FILE for the library; GEN_URL, GEN_KEY_FILE and GEN_KEY_HEADER for the generator
(see client.py). Run one command at a time: no parallel downloads.

    LIB_URL=... python3 -I video/tools/audio/lib.py tools
    LIB_URL=... python3 -I video/tools/audio/lib.py music "felt piano hopeful" [--first 12]
    LIB_URL=... python3 -I video/tools/audio/lib.py sfx "ui tap soft" [--first 12]
    LIB_URL=... python3 -I video/tools/audio/lib.py track ID OUT.wav
    LIB_URL=... python3 -I video/tools/audio/lib.py effect ID OUT.wav
    LIB_URL=... python3 -I video/tools/audio/lib.py edit ID SECONDS OUT.wav
    GEN_URL=... python3 -I video/tools/audio/lib.py gen "prompt" SECONDS OUT.mp3

Downloads go to a folder outside the repo (argument OUT); finish.py turns them into public/audio/.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import Library, download, find, generate  # noqa: E402


def _nodes(found):
    out = []
    for node in find(found, "nodes") or find(found, "edges") or []:
        if isinstance(node, dict):
            node = node.get("node", node)
            node = node.get("recording", node.get("soundEffect", node))
        if isinstance(node, dict) and node.get("id"):
            out.append(node)
    return out


def _row(node):
    ms = (node.get("audioFile") or {}).get("durationInMilliseconds") or 0
    tags = {}
    for t in node.get("tags") or []:
        dim = (t.get("dimension") or {}).get("name", "tag")
        tags.setdefault(dim, []).append(t.get("displayName", ""))
    genres = ",".join(tags.get("genre", [])[:3])
    moods = ",".join(tags.get("mood", [])[:4])
    vocals = ",".join(tags.get("vocal type", [])) or "-"
    return (f"{node['id']}  {ms / 1000:6.1f}s  bpm {node.get('bpm', '?')!s:>4}  voc {vocals[:12]:12} "
            f"{str(node.get('title'))[:44]:44}  {genres[:34]:34} {moods[:44]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd")
    p.add_argument("args", nargs="*")
    p.add_argument("--first", type=int, default=12)
    p.add_argument("--raw", action="store_true")
    a = p.parse_args()
    if a.cmd == "gen":
        text, seconds, out = a.args
        print(generate(text, float(seconds), out))
        return
    lib = Library()
    if a.cmd == "tools":
        for t in lib.call("tools/list").get("tools", []):
            props = ",".join((t.get("inputSchema") or {}).get("properties", {}).keys())
            print(f"{t['name']}({props})")
        return
    if a.cmd in ("music", "sfx", "similar"):
        if a.cmd == "music":
            found = lib.tool("SearchRecordings", {"query": {"term": a.args[0]}, "first": a.first})
        elif a.cmd == "similar":
            found = lib.tool("SearchSimilarToRecording", {"id": a.args[0], "first": a.first})
        else:
            found = lib.tool("SearchSoundEffects", {"query": {"term": a.args[0]}, "first": a.first})
        if a.raw:
            print(json.dumps(found, indent=1)[:4000])
            return
        for node in _nodes(found):
            print(_row(node))
        return
    if a.cmd == "track":
        rid, out = a.args
        url = find(lib.tool("DownloadRecording", {"id": rid, "options": {"fileType": "WAV", "stemType": "FULL"}}),
                   "assetUrl")
        print(download(url, out))
        return
    if a.cmd == "effect":
        eid, out = a.args
        url = find(lib.tool("DownloadSoundEffect", {"id": eid, "options": {"fileType": "WAV"}}), "assetUrl")
        print(download(url, out))
        return
    if a.cmd == "edit":
        rid, seconds, out = a.args
        job = lib.tool("EditRecording", {"id": rid, "input": {
            "targetDurationMs": int(float(seconds) * 1000), "downloadAudioFormat": "WAV", "skipStems": True,
            "maxResults": 1, "forceDuration": True}})
        job_id, state, status = find(job, "id"), None, None
        for _ in range(60):
            status = lib.tool("PollEditRecordingJob", {"id": job_id})
            state = find(status, "status")
            if state in ("COMPLETED", "FAILED"):
                break
            time.sleep(5)
        if state != "COMPLETED":
            raise SystemExit(f"edit {rid}: {state}")
        edit = find(status, "edit") or {}
        url = find(lib.tool("DownloadRecordingEdit", {"input": {"jobId": job_id, "editId": edit.get("id")}}),
                   "assetUrl")
        print(download(url, out))
        return
    raise SystemExit(f"unknown command {a.cmd}")


if __name__ == "__main__":
    main()
