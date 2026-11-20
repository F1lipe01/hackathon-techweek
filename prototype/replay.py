"""Replay mode: a recorded lab take stands in for the kit camera, so the real pipeline (edge -> server -> presence ->
rules -> alerts) processes the same unedited footage the films used.

    TT_REPLAY=video/replays/book.json prototype/.venv/bin/python prototype/server.py
    POST /api/replay/start            starts the take at its first second (the proof recorder calls it)
    GET  /api/replay                  where the take is: t, duration, the events still to come

The replay file (JSON):
    {"video": "video/public/takes/scene1/book-full.mp4",        the take, read in real time, at full resolution
     "note": "...",                                              where each event's moment comes from
     "setup": {"phones": {"filipe": true}, "devices": {"ac": false}, "rules": {"leave_without": {"cooldown_s": 10}}},
     "events": [{"t": 10.4, "door": "open"}, {"t": 13.0, "phone": "filipe", "home": false},
                {"t": 50.6, "device": "ac", "on": true}, {"t": 2.0, "mark": {"thing": "book", "box": [x0, y0, x1, y1]}}]}

Only the inputs that no camera can see are replayed, each at the moment it happened in the take: the door's contact
sensor, the family's phones on the Wi-Fi, a device switched by hand, and the family marking their thing on the camera
picture. Each is written to the activity as "Replayed: ...". Everything else (motion, detection, recognition, faces,
presence, rules, alerts) is computed live by the same code as with the real camera.

The frames: ffmpeg -re decodes the take at its own frame rate (1 s of take = 1 s of wall time), full size, as JPEGs
through a pipe, nothing written to disk; the newest one is kept. The take's own clock (the camera's date overlay) is
in the picture itself; t, the take's second, is in GET /api/replay and drawn on the page.
"""
import json
import subprocess
import threading
import time
from pathlib import Path

SOI, EOI = b"\xff\xd8", b"\xff\xd9"
ROOT = Path(__file__).resolve().parents[1]


class ReplayCamera:
    """The KitCamera interface (latest, frames_forever, status), fed from a file."""

    def __init__(self, spec_path):
        self.spec_path = Path(spec_path)
        self.spec = json.loads(self.spec_path.read_text())
        v = Path(self.spec["video"])
        self.video = v if v.is_absolute() else ROOT / v
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(self.video)], capture_output=True, text=True)
        self.duration = float(probe.stdout.strip() or 0)
        self.offset = float(self.spec.get("from", 0))     # where the replay starts in the take (its reason is in "note")
        self.frame, self.frame_at, self.frames, self.started_at, self.ended = None, 0.0, 0, 0.0, False
        self.at, self.paused, self.paused_t = self.offset, False, self.offset   # the player (the pitch site)
        self._new = threading.Condition()
        self._proc = None
        self._first_frame()

    def _first_frame(self, at=None):
        """Before the start, the take's first frame (or the frame at a second), so the page shows what the camera sees."""
        at = self.offset if at is None else at
        out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{at:.3f}", "-i", str(self.video), "-frames:v", "1", "-f", "image2pipe",
                              "-vcodec", "mjpeg", "-q:v", "3", "-"], capture_output=True)
        if out.stdout:
            with self._new:
                self.frame, self.frame_at, self.frames = out.stdout, time.time(), self.frames + 1
                self._new.notify_all()

    def _kill(self):
        proc, self._proc = self._proc, None
        if proc:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pass

    def pause(self):
        """The player's pause: the picture stays on the current frame."""
        if not self.started_at or self.paused:
            return
        self.paused_t = self.t()
        self.paused = True
        self._kill()

    def seek(self, t):
        """The player's timeline: shows the frame at take second t, paused."""
        t = max(0.0, min(float(t), self.duration - 0.1))
        self._kill()
        self.paused, self.paused_t, self.ended = True, t, False
        if not self.started_at:
            self.started_at = time.time()
        self._first_frame(t)

    def stop(self):
        """Back to the take's first frame, not started (the demo site's reset and replay buttons)."""
        self._kill()
        self.started_at, self.ended, self.frames, self.paused = 0.0, False, 0, False
        self._first_frame()
        with self._new:
            self._new.notify_all()

    def start(self, at=None):
        """Plays the take in real time from its start (or from take second at, for the player)."""
        if self.started_at and not self.paused:
            return False
        self._kill()
        self.ended, self.paused = False, False
        self.at = self.offset if at is None else max(0.0, min(float(at), self.duration - 0.1))
        self.started_at = time.time()
        self._proc = subprocess.Popen(["ffmpeg", "-v", "error", "-re", "-ss", f"{self.at:.3f}", "-i", str(self.video), "-an", "-f", "image2pipe",
                                       "-vcodec", "mjpeg", "-q:v", "3", "-"], stdout=subprocess.PIPE)
        threading.Thread(target=self._read, daemon=True).start()
        return True

    def _read(self):
        buf, proc = b"", self._proc
        while True:
            chunk = proc.stdout.read(1 << 16)
            if not chunk:
                break
            buf += chunk
            while True:
                a = buf.find(SOI)
                b = buf.find(EOI, a + 2) if a >= 0 else -1
                if a < 0 or b < 0:
                    break
                jpg, buf = buf[a:b + 2], buf[b + 2:]
                if proc is not self._proc:          # stopped: a newer start owns the frames
                    return
                with self._new:
                    self.frame, self.frame_at, self.frames = jpg, time.time(), self.frames + 1
                    self._new.notify_all()
        if proc is self._proc:
            self.ended = True                      # the last frame stays: the camera keeps seeing the empty room

    def t(self):
        """The take's second now (0 before the start, the duration after the end)."""
        if not self.started_at:
            return self.offset
        if self.paused:
            return self.paused_t
        return min(self.duration, self.at + time.time() - self.started_at)

    def latest(self):
        return self.frame

    def frames_forever(self, max_fps=8):
        """The page's live view: at most max_fps frames a second (full-size JPEGs at the take's 20 fps would load the
        browser, and with it the machine the edge runs on). The edge reads frames on its own, through latest()."""
        last, sent = 0, 0.0
        while True:
            with self._new:
                self._new.wait(timeout=0.5)
                n, f = self.frames, self.frame
            if f and n != last and time.time() - sent >= 1 / max_fps:
                last, sent = n, time.time()
                yield f
            elif f and (self.ended or self.paused or not self.started_at):
                time.sleep(0.2)
                yield f

    def status(self):
        return {"replay": True, "video": self.video.name, "t": round(self.t(), 2), "duration": self.duration,
                "from": self.offset, "started": bool(self.started_at), "started_at": self.started_at, "ended": self.ended,
                "frames": self.frames, "paused": self.paused}


class WebcamCamera:
    """The MacBook's own camera (AVFoundation through ffmpeg), live, with the KitCamera interface. Frames are
    1280 x 720 JPEGs, 8 a second, through a pipe; nothing is written to disk."""

    def __init__(self, device="0", size="1280x720"):
        self.device, self.size = device, size
        self.video = Path("FaceTime HD Camera")
        self.frame, self.frame_at, self.frames, self.started_at, self.ended, self.paused = None, 0.0, 0, 0.0, False, False
        self.duration, self.offset = 0.0, 0.0
        self.spec = {}
        self._new = threading.Condition()
        self._proc = None

    def start(self, at=None):
        if self._proc and self._proc.poll() is None:
            return False
        self._proc = subprocess.Popen(["ffmpeg", "-v", "error", "-f", "avfoundation", "-pixel_format", "nv12", "-framerate", "30",
                                       "-video_size", self.size, "-i", f"{self.device}:none", "-vf", "fps=8", "-f", "image2pipe",
                                       "-vcodec", "mjpeg", "-q:v", "4", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.started_at = time.time()
        threading.Thread(target=self._read, args=(self._proc,), daemon=True).start()
        return True

    def _read(self, proc):
        buf = b""
        while True:
            chunk = proc.stdout.read(1 << 16)
            if not chunk:
                break
            buf += chunk
            while True:
                a = buf.find(SOI)
                b = buf.find(EOI, a + 2) if a >= 0 else -1
                if a < 0 or b < 0:
                    break
                jpg, buf = buf[a:b + 2], buf[b + 2:]
                if proc is not self._proc:
                    return
                with self._new:
                    self.frame, self.frame_at, self.frames = jpg, time.time(), self.frames + 1
                    self._new.notify_all()

    def stop(self):
        proc, self._proc = self._proc, None
        if proc:
            proc.kill()
        self.started_at, self.frame = 0.0, None

    pause = seek = lambda self, *a: None

    def t(self):
        return time.time() - self.started_at if self.started_at else 0.0

    def latest(self):
        return self.frame

    def frames_forever(self, max_fps=8):
        last = 0
        while True:
            with self._new:
                self._new.wait(timeout=0.5)
                n, f = self.frames, self.frame
            if f and n != last:
                last = n
                yield f

    def status(self):
        return {"replay": False, "webcam": True, "video": self.video.name, "t": round(self.t(), 1), "duration": 0,
                "started": bool(self.started_at), "frames": self.frames, "paused": False, "ended": False}


class Replayer:
    """Plays the replay file's events at their take seconds, through the server's own handlers."""

    def __init__(self, cam, handlers):
        self.cam, self.h = cam, handlers
        self.events = sorted(cam.spec.get("events", []), key=lambda e: e["t"])
        self.done = []

    def setup(self):
        self.h["setup"](self.cam.spec.get("setup", {}))

    def start(self):
        """The take's starting state is set at its first second, then the take and its events run."""
        if self.cam.started_at:
            return False
        self.setup()
        self.done = []
        self.active = True
        self.run_id = getattr(self, "run_id", 0) + 1
        if not self.cam.start():
            return False
        threading.Thread(target=self._run, args=(self.run_id,), daemon=True).start()
        return True

    def stop(self):
        """The take back to its first frame; the events still to come are dropped."""
        self.cancel()
        self.cam.stop()
        self.done = []

    def cancel(self):
        """The story's events still to come are dropped; the take keeps playing (the player's timeline was dragged)."""
        self.run_id = getattr(self, "run_id", 0) + 1
        self.active = False

    def _run(self, run_id):
        for e in self.events:
            while self.cam.t() < e["t"]:
                if run_id != self.run_id:
                    return
                time.sleep(0.05)
            if run_id != self.run_id:
                return
            try:
                self.h["event"](e)
            except Exception as ex:  # noqa: BLE001 - one bad event must not stop the replay
                print("replay event failed:", e, ex, flush=True)
            self.done.append(e)
        if run_id == self.run_id:
            self.active = False

    def status(self):
        return {**self.cam.status(), "note": self.cam.spec.get("note", ""), "file": self.cam.spec_path.name,
                "next": [e for e in self.events if e not in self.done][:3]}
