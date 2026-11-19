"""Rewrite the kit camera's burned-in clock in a clip so it continues another take (example 3: the AC clip, filmed at
17:50, is cut into the main take at 17:32; the empty lit room is extended with repeated pieces). The clock's digits are
swapped for the camera's own digits, cut from the same clip's seconds place, so the font, outline and greys match.

    python3 video/tools/fix_osd.py in.mp4 out.mp4 --start 17:49:38 --shift -1053

--start is the clock on the clip's first frame (read it from a frame). The tool finds the camera's tick rhythm (when
the seconds' ones digit changes) on steady frames, so the new clock ticks on the camera's own frames, and writes each
frame with the clock shifted by --shift seconds. A digit is rewritten when it should change, or when the digit the frame
shows (read by matching it against the camera's samples) is not the one it should show, so a clip made of repeated
pieces gets one continuous clock with --shift 0. The camera draws white digits with a thin black outline: on a dark or
grey background the white strokes are the digit; on a lit ceiling (nearly white) the digit is what the outline encloses.
Frames are read and written through ffmpeg (no audio; 20 fps clips).
"""
import argparse
import json
import subprocess

import cv2
import numpy as np

Y0, Y1, X0, PITCH, W0 = 51, 149, 92, 42, 24          # the clock band and its 42 px character grid (2304 x 1296)
CELLS = {"h1": 11, "h2": 12, "m1": 14, "m2": 15, "s1": 17, "s2": 18}   # character cells of HH:MM:SS (the space counts)
K = lambda n: np.ones((n, n), np.uint8)


def box(c):
    x = X0 + W0 + PITCH * c
    return (slice(Y0, Y1), slice(x - 6, x + 41))


def gray(p):
    return cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)


def bright(p):
    """A lit ceiling behind the digit: most of the cell is near white (a grey night-vision ceiling is not)."""
    return float((gray(p) > 200).mean()) > 0.4


def strokes(p, grow):
    w = (gray(p) > 200).astype(np.uint8) * 255
    return cv2.dilate(w, K(grow))


def outline_shape(p):
    """On a bright background: the digit's black outline and all it encloses, as the shape near the cell's middle
    (specks of the ceiling and a neighbour's edge are dropped)."""
    g = gray(p)
    dark = cv2.dilate((g < 150).astype(np.uint8), K(2))           # the outline, its faint compressed pixels and 1 px gaps closed
    free = np.pad(1 - dark, 1, constant_values=1)
    cv2.floodFill(free, np.zeros((free.shape[0] + 2, free.shape[1] + 2), np.uint8), (0, 0), 2)
    shape = (free[1:-1, 1:-1] != 2).astype(np.uint8)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(shape, connectivity=8)
    keep = np.zeros(shape.shape, bool)
    w = shape.shape[1]
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 120 and 0.2 * w < cent[i][0] < 0.8 * w:
            keep |= lab == i
    return keep


def ink(p):
    """What tells the digits apart: the black outline on a bright background, the white strokes otherwise."""
    if bright(p):
        return outline_shape(p) & (gray(p) < 150)
    return gray(p) > 200


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
    ap.add_argument("--sample-from", type=float, default=0, help="take the digits and the rhythm only from this second on")
    ap.add_argument("--sample-until", type=float, default=1e9, help="... and only up to this second (a clip of repeated pieces: its first piece)")
    a = ap.parse_args()
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                      "-of", "json", a.src], capture_output=True, text=True).stdout)["streams"][0]
    w, h = info["width"], info["height"]
    hh, mm, ss = (int(x) for x in a.start.split(":"))
    t0 = hh * 3600 + mm * 60 + ss

    # pass 1: the camera's tick rhythm and one clean sample of each digit 0-9, from steady frames in the sampling window
    # (a light switching floods or blacks out the clock band and would fake a tick); the camera ticks once a second, so
    # the rhythm found there gives every frame's clock, including the unsteady ones.
    samples, prev, ticks_t, n = [], None, [], 0
    for i, fr in enumerate(frames(a.src, w, h)):
        n = i + 1
        t = i / a.fps
        cellp = fr[box(CELLS["s2"])]
        m = ink(cellp)
        frac = (outline_shape(cellp).mean() if bright(cellp) else (gray(cellp) > 200).mean())
        steady = (0.08 < frac < 0.75 if bright(cellp) else 0.04 < frac < 0.45) and a.sample_from <= t <= a.sample_until
        if steady and prev is not None and (m ^ prev).sum() > 0.25 * max(1, m.sum()):
            ticks_t.append(t)
        prev = m if steady else None
        if steady:
            samples.append((t, cellp.copy()))
    if len(ticks_t) < 3:
        raise SystemExit("too few steady ticks to find the clock's rhythm")
    phase = float(np.median([t % 1.0 for t in ticks_t]))
    first = phase if phase > 0 else 1.0
    clock_at = lambda t: t0 + (0 if t < first - 1e-6 else int(np.floor(t - first + 1e-6)) + 1)
    times = [clock_at(j / a.fps) for j in range(n)]
    cands = {}
    for t, cellp in samples:                                         # samples well inside their second, not at a tick
        if (t - first) % 1.0 < 0.2 or (t - first) % 1.0 > 0.8:
            continue
        cands.setdefault(clock_at(t) % 10, []).append(cellp)

    def iou(p, q):
        m, n = cv2.dilate(ink(p).astype(np.uint8), K(3)) > 0, cv2.dilate(ink(q).astype(np.uint8), K(3)) > 0
        u = (m | n).sum()
        return (m & n).sum() / u if u else 0.0

    glyph = {}
    for d, cs in cands.items():                                      # the samples of one digit must agree with each other,
        pick = cs[len(cs) // 2]                                      # or the rhythm (and so the labels) is wrong
        if len(cs) >= 3 and min(iou(pick, cs[0]), iou(pick, cs[-1])) < 0.55:
            raise SystemExit(f"the samples labelled {d} disagree: the tick rhythm is off (phase {phase:.2f}); check --start and --sample-from")
        glyph[d] = pick
    print(f"{n} frames, {len(ticks_t)} steady ticks, tick phase {phase:.2f} s, clock {hms(t0)} -> {hms(times[-1])}, digits sampled: {sorted(glyph)}")
    missing = [d for d in range(10) if d not in glyph]
    if missing:
        raise SystemExit(f"digits never seen in the seconds place: {missing}; use a longer clip")

    gink = {d: cv2.dilate(ink(g).astype(np.uint8), K(3)) > 0 for d, g in glyph.items()}

    def read(cellp):
        m = cv2.dilate(ink(cellp).astype(np.uint8), K(3)) > 0
        best, score = None, 0.0
        for d, gm in gink.items():
            uni = (m | gm).sum()
            sc = (m & gm).sum() / uni if uni else 0.0
            if sc > score:
                best, score = d, sc
        return best if score >= 0.6 else None

    # pass 2: write every frame with the shifted clock
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(a.fps), "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    fixed = 0
    for j, fr in enumerate(frames(a.src, w, h)):
        old, new = hms(times[j]), hms(times[j] + a.shift)
        for (name, c), o, nw in zip(CELLS.items(), old, new):
            b = box(c); cur = fr[b].copy()
            if o == nw and read(cur) == int(nw):
                continue
            g = glyph[int(nw)]
            if bright(cur):
                hole = cv2.dilate(outline_shape(cur).astype(np.uint8) * 255, K(5))
                clean = cv2.inpaint(cur, hole, 5, cv2.INPAINT_TELEA)
                gm = (outline_shape(g) if bright(g) else strokes(g, 3) > 0).astype(np.uint8) * 255
                m = cv2.GaussianBlur(cv2.dilate(gm, K(2)), (3, 3), 0).astype(float)[..., None] / 255
            else:
                clean = cv2.inpaint(cur, strokes(cur, 9), 6, cv2.INPAINT_TELEA)
                m = cv2.GaussianBlur(strokes(g, 7), (5, 5), 0).astype(float)[..., None] / 255
            fr[b] = (g * m + clean * (1 - m)).astype(np.uint8)
            fixed += 1
        enc.stdin.write(fr.tobytes())
    enc.stdin.close(); enc.wait()
    # check: read the written clip's digits back (every 5th frame, away from ticks) against the clock it should show
    bad, seen = 0, 0
    for j, fr in enumerate(frames(a.out, w, h)):
        t = j / a.fps
        if j % 5 or (t - first) % 1.0 < 0.15 or (t - first) % 1.0 > 0.85:
            continue
        want = hms(times[j] + a.shift)
        got = [read(fr[box(c)]) for c in CELLS.values()]
        seen += 1
        if any(g is not None and g != int(x) for g, x in zip(got, want)):
            bad += 1
            if bad <= 3:
                print(f"  mismatch at {t:.2f} s: shows {''.join('?' if g is None else str(g) for g in got)}, should be {want}")
    print(f"written {a.out}: clock {hms(times[0] + a.shift)} -> {hms(times[-1] + a.shift)}, {fixed} digits rewritten; read back {seen} frames, {bad} wrong")
    if bad:
        raise SystemExit("the written clock does not read back right")


if __name__ == "__main__":
    main()
