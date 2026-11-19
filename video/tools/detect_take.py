"""The prototype's own detector (OWLv2, as edge.py) run offline over a recorded kit-camera take, for the edit.
    prototype/.venv-vision/bin/python video/tools/detect_take.py <take.mp4> <out.json> --every 0.25 --queries "a person" "a yellow book"
      [--door x0 y0 x1 y1]
Writes {"size":[w,h],"fps","frames":[{"t","boxes":[{"label","score","box":[x0,y0,x1,y1] normalised}]}],
        "door":{"zone":[...], "open":[[t0,t1],...], "diff":[[t,d],...]}}.
The door's state comes from the picture itself: the mean change inside its zone against the first frame, open above 10."""
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "prototype"))
import edge  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("take"); ap.add_argument("out")
ap.add_argument("--every", type=float, default=0.25)
ap.add_argument("--queries", nargs="+", default=["a person"])
ap.add_argument("--door", nargs=4, type=float, default=None)
ap.add_argument("--threshold", type=float, default=0.12)
a = ap.parse_args()
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                                   "-of", "json", a.take], capture_output=True, check=True).stdout)["streams"][0]
w, h = probe["width"], probe["height"]
num, den = (int(x) for x in probe["r_frame_rate"].split("/")); fps = num / den
W, H = 1152, 648  # frames are read at this size, in order, through ffmpeg
pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.take, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
det = edge.Detector()
step = max(1, round(a.every * fps))
frames, diffs, ref = [], [], None
i = -1
while True:
    buf = pipe.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    i += 1
    im = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    t = i / fps
    if a.door:
        x0, y0, x1, y1 = a.door
        z = im[int(y0*H):int(y1*H), int(x0*W):int(x1*W)].mean(axis=2)
        if ref is None: ref = z
        diffs.append([round(t, 3), round(float(np.abs(z - ref).mean()), 2)])
    if i % step: continue
    out = det(Image.fromarray(im), list(a.queries), threshold=a.threshold)
    frames.append({"t": round(t, 3), "boxes": [{"label": l, "score": round(sc, 3), "box": [round(b[0]/W, 4), round(b[1]/H, 4), round(b[2]/W, 4), round(b[3]/H, 4)]} for l, sc, b in out]})
res = {"take": Path(a.take).name, "size": [w, h], "fps": fps, "queries": a.queries, "frames": frames}
if a.door:
    opened, start = [], None
    for t, d in diffs:
        if d > 10 and start is None: start = t
        if d <= 10 and start is not None:
            if t - start > 0.3: opened.append([start, t])
            start = None
    if start is not None: opened.append([start, diffs[-1][0]])
    res["door"] = {"zone": a.door, "open": opened, "diff": diffs[::2]}
Path(a.out).write_text(json.dumps(res)); print(a.out, len(frames), "frames detected;", "door open:", res.get("door", {}).get("open"))
