"""The kit camera, read directly: one persistent RTSP connection, the latest frame kept in memory.

The camera (H.265, 2304 x 1296, 20 fps) is reached through the organisers' go2rtc relay. Opening a new
connection costs about 5 s, because the decoder must wait for the next keyframe. So instead of one
connection per frame, a background ffmpeg keeps the stream open, downsamples it to FPS frames per second at
WIDTH pixels, and hands us JPEGs through a pipe. Nothing is written to disk.

The reader starts when someone asks for a frame and stops after IDLE_STOP seconds without requests, so the
relay is not used when nobody is looking.
"""
import os
import subprocess
import threading
import time

FPS = float(os.environ.get("TT_KIT_FPS", "5"))
WIDTH = int(os.environ.get("TT_KIT_WIDTH", "1280"))
IDLE_STOP = 60.0
SOI, EOI = b"\xff\xd8", b"\xff\xd9"


class KitCamera:
    def __init__(self, url):
        self.url = url
        self.frame = None          # latest JPEG bytes
        self.frame_at = 0.0        # when it arrived (time.time())
        self.frames = 0
        self.started_at = 0.0
        self.error = None
        self.last_request = 0.0
        self._proc = None
        self._thread = None
        self._lock = threading.Lock()
        self._new = threading.Condition()

    # -------------------------------------------------------------- lifecycle
    def _ensure_running(self):
        self.last_request = time.time()
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def _run(self):
        backoff = 1.0
        while time.time() - self.last_request < IDLE_STOP:
            self.started_at, self.error = time.time(), None
            cmd = ["ffmpeg", "-loglevel", "quiet", "-rtsp_transport", "tcp", "-timeout", "8000000",
                   "-i", self.url, "-an", "-vf", f"fps={FPS},scale={WIDTH}:-2",
                   "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "5", "pipe:1"]
            self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
            buf = b""
            try:
                while time.time() - self.last_request < IDLE_STOP:
                    chunk = self._proc.stdout.read(65536)
                    if not chunk:
                        break
                    buf += chunk
                    while True:
                        a = buf.find(SOI)
                        b = buf.find(EOI, a + 2) if a >= 0 else -1
                        if a < 0 or b < 0:
                            break
                        with self._new:
                            self.frame, self.frame_at = buf[a:b + 2], time.time()
                            self.frames += 1
                            self._new.notify_all()
                        buf = buf[b + 2:]
                        backoff = 1.0
                    if len(buf) > 8_000_000:   # never let a broken stream grow memory
                        buf = b""
            finally:
                self._proc.kill()
                self._proc.wait()
            if time.time() - self.last_request < IDLE_STOP:
                self.error = "stream ended; reconnecting"
                time.sleep(backoff)
                backoff = min(backoff * 2, 15)

    # -------------------------------------------------------------- reading
    def latest(self, wait=12.0, max_age=3.0):
        """The newest frame, waiting for the first one after a (re)connect."""
        self._ensure_running()
        deadline = time.time() + wait
        with self._new:
            while not self.frame or time.time() - self.frame_at > max_age:
                left = deadline - time.time()
                if left <= 0:
                    return None
                self._new.wait(left)
            return self.frame

    def frames_forever(self):
        """Yields each new frame as it arrives (for the live MJPEG view)."""
        seen = 0
        while True:
            self._ensure_running()
            with self._new:
                self._new.wait_for(lambda: self.frames != seen, timeout=12)
                if self.frames == seen:
                    return
                seen, frame = self.frames, self.frame
            yield frame

    def status(self):
        alive = bool(self._thread and self._thread.is_alive())
        age = time.time() - self.frame_at if self.frame_at else None
        return {"running": alive, "frames": self.frames, "fps_target": FPS, "width": WIDTH,
                "last_frame_age_s": round(age, 2) if age is not None else None, "error": self.error}
