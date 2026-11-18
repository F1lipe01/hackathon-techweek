"""Record a take for the product video: the kit camera at full resolution, plus what the edge service saw.

    prototype/.venv/bin/python prototype/record.py --seconds 90 --name wallet-registration

Writes prototype/data/recordings/<time>-<name>/ (never committed):
  video.mp4    the camera's own H.265 stream, copied without re-encoding (2304 x 1296, 20 fps)
  boxes.jsonl  one line every 200 ms: wall-clock time, the edge's boxes (0-1 coordinates), state and registration
  take.json    when the recording started, to line the two up (the camera also burns its clock into the picture)

People in the lab appear in the video: use a take in the pitch only with their agreement, or blur them.
The address of the camera is read from the repo's .env and never printed.
"""
import argparse
import json
import os
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def camera_url():
    url = os.environ.get("CAMERA_RTSP_URL", "")
    env = HERE.parent / ".env"
    if not url and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("CAMERA_RTSP_URL="):
                url = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not url:
        raise SystemExit("CAMERA_RTSP_URL is not set")
    return url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--name", default="take")
    ap.add_argument("--server", default="http://127.0.0.1:8765")
    args = ap.parse_args()

    out = HERE / "data" / "recordings" / f"{time.strftime('%Y%m%d-%H%M%S')}-{args.name}"
    out.mkdir(parents=True)
    started = time.time()
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-rtsp_transport", "tcp", "-i", camera_url(),
                           "-t", str(args.seconds), "-c", "copy", "-tag:v", "hvc1", "-an", str(out / "video.mp4")],
                          stdin=subprocess.DEVNULL)
    stop = threading.Event()

    def boxes():
        with open(out / "boxes.jsonl", "w") as f:
            while not stop.is_set():
                try:
                    with urllib.request.urlopen(f"{args.server}/api/edge/boxes", timeout=2) as r:
                        b = json.loads(r.read())
                    f.write(json.dumps({"t": round(time.time(), 3), **b}) + "\n")
                    f.flush()
                except Exception:
                    pass
                time.sleep(0.2)

    th = threading.Thread(target=boxes, daemon=True)
    th.start()
    (out / "take.json").write_text(json.dumps({"started": started, "seconds": args.seconds, "name": args.name}))
    print(f"recording {args.seconds} s to {out}", flush=True)
    ff.wait()
    stop.set()
    th.join(timeout=2)
    size = (out / "video.mp4").stat().st_size if (out / "video.mp4").exists() else 0
    print(f"done: {size / 1e6:.1f} MB, ffmpeg exit {ff.returncode}", flush=True)


if __name__ == "__main__":
    main()
