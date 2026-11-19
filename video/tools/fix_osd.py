"""Rewrite the kit camera's burned-in clock in a clip so it continues another take (example 3: the AC clip, filmed at
17:50, is cut into the main take at 17:32). The clock's digits are swapped for the camera's own digits, cut from the
same clip's seconds place, so the font, outline and greys match exactly; only the digits that change are touched.

    python3 video/tools/fix_osd.py in.mp4 out.mp4 --start 17:49:38 --shift -1053

--start is the clock on the clip's first frame (read it from a frame). The tool follows the camera's own seconds ticks
(when the seconds' ones digit changes) so the new clock ticks on exactly the same frames, and writes each frame with
the clock shifted by --shift seconds. Frames are read and written through ffmpeg (no audio; 20 fps clips).
"""
import argparse
import json
import subprocess

import cv2
import numpy as np

Y0, Y1, X0, PITCH, W0 = 51, 149, 92, 42, 24          # the clock band and its 42 px character grid (2304 x 1296)
CELLS = {"h1": 11, "h2": 12, "m1": 14, "m2": 15, "s1": 17, "s2": 18}   # character cells of HH:MM:SS (the space counts)


def box(c):
    x = X0 + W0 + PITCH * c
    return (slice(Y0, Y1), slice(x - 6, x + 41))


def strokes(p, grow):
    w = (cv2.cvtColor(p, cv2.COLOR_BGR2GRAY) > 200).astype(np.uint8) * 255
    return cv2.dilate(w, np.ones((grow, grow), np.uint8))


def hms(s):
    s %= 86400
    return f"{s // 3600:02d}{(s % 3600) // 60:02d}{s % 60:02d}"


def frames(path, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3).copy()
    p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--start", required=True, help="the clock on the first frame, HH:MM:SS")
    ap.add_argument("--shift", type=int, required=True, help="seconds to add to the clock (negative: earlier)")
    ap.add_argument("--fps", type=float, default=20)
    ap.add_argument("--sample-from", type=float, default=0, help="take the digits only from this second on (match the lighting of the part used)")
    a = ap.parse_args()
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                      "-of", "json", a.src], capture_output=True, text=True).stdout)["streams"][0]
    w, h = info["width"], info["height"]
    hh, mm, ss = (int(x) for x in a.start.split(":"))
    t0 = hh * 3600 + mm * 60 + ss

    # pass 1: the camera's tick rhythm and one clean sample of each digit 0-9. Only steady frames from --sample-from on
    # count (a light switching on or off floods or blacks out the clock band and would fake a tick); the camera ticks
    # once a second, so the rhythm found there gives every frame's clock, including the unsteady ones.
    samples, prev, ticks_t, n = [], None, [], 0
    for i, fr in enumerate(frames(a.src, w, h)):
        n = i + 1
        cellp = fr[box(CELLS["s2"])]
        g = cv2.cvtColor(cellp, cv2.COLOR_BGR2GRAY)
        white = (g > 200).mean()
        steady = 0.04 < white < 0.45 and i / a.fps >= a.sample_from
        m = strokes(cellp, 1) > 0
        if steady and prev is not None and (m ^ prev).sum() > 0.25 * max(1, m.sum()):
            ticks_t.append(i / a.fps)
        prev = m if steady else None
        if steady:
            samples.append((i / a.fps, cellp.copy()))
    if len(ticks_t) < 3:
        raise SystemExit("too few steady ticks to find the clock's rhythm")
    phase = float(np.median([t % 1.0 for t in ticks_t]))          # where in each second the camera ticks
    first = phase if phase > 0 else 1.0                              # the first tick after the clip's first frame
    clock_at = lambda t: t0 + (0 if t < first - 1e-6 else int(np.floor(t - first + 1e-6)) + 1)
    times = [clock_at(j / a.fps) for j in range(n)]
    glyph = {}
    for t, cellp in samples:                                         # a sample well inside its second, not at a tick
        if (t - first) % 1.0 < 0.15 or (t - first) % 1.0 > 0.85:
            continue
        glyph.setdefault(clock_at(t) % 10, cellp)
    print(f"{n} frames, {len(ticks_t)} steady ticks, tick phase {phase:.2f} s, clock {hms(t0)} -> {hms(times[-1])}, digits sampled: {sorted(glyph)}")
    missing = [d for d in range(10) if d not in glyph]
    if missing:
        raise SystemExit(f"digits never seen in the seconds place: {missing}; use a longer clip")

    # pass 2: write every frame with the shifted clock, changing only the digits that differ
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(a.fps), "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    for j, fr in enumerate(frames(a.src, w, h)):
        old, new = hms(times[j]), hms(times[j] + a.shift)
        for (name, c), o, nw in zip(CELLS.items(), old, new):
            if o == nw:
                continue
            b = box(c); cur = fr[b].copy()
            clean = cv2.inpaint(cur, strokes(cur, 9), 6, cv2.INPAINT_TELEA)
            g = glyph[int(nw)]; m = cv2.GaussianBlur(strokes(g, 7), (5, 5), 0).astype(float)[..., None] / 255
            fr[b] = (g * m + clean * (1 - m)).astype(np.uint8)
        enc.stdin.write(fr.tobytes())
    enc.stdin.close(); enc.wait()
    print(f"written {a.out}: clock {hms(times[0] + a.shift)} -> {hms(times[-1] + a.shift)}")


if __name__ == "__main__":
    main()
