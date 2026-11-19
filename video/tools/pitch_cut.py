"""A short cut of a finished film for the pitch: segments joined with short crossfades, a fade-out, and a static gain to
-15 LUFS (the films' mix) with the same limiter. No re-render: it cuts the finished file.

    python3 video/tools/pitch_cut.py in.mp4 out.mp4 9.0-12.0 23.7-27.2 36.5-44.0 ...   [--xfade 0.2] [--fade 0.5]
"""
import argparse
import re
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("segments", nargs="+")
ap.add_argument("--xfade", type=float, default=0.2, help="crossfade between segments, seconds (video and audio)")
ap.add_argument("--fade", type=float, default=0.5, help="fade-out at the end, seconds")
a = ap.parse_args()
segs = [tuple(float(x) for x in s.split("-")) for s in a.segments]
n, d = len(segs), a.xfade
parts = [f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n)) + ";", f"[0:a]asplit={n}" + "".join(f"[as{i}]" for i in range(n)) + ";"]
for i, (s, e) in enumerate(segs):
    parts.append(f"[vs{i}]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];[as{i}]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}];")
vcur, acur, length = "v0", "a0", segs[0][1] - segs[0][0]
for i in range(1, n):
    seg = segs[i][1] - segs[i][0]
    parts.append(f"[{vcur}][v{i}]xfade=transition=fade:duration={d}:offset={length - d:.3f}[vx{i}];[{acur}][a{i}]acrossfade=d={d}[ax{i}];")
    vcur, acur, length = f"vx{i}", f"ax{i}", length + seg - d
parts.append(f"[{vcur}]fade=t=out:st={length - a.fade:.3f}:d={a.fade}[vo];[{acur}]afade=t=out:st={length - a.fade:.3f}:d={a.fade}[ao]")
raw = a.out + ".raw.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-filter_complex", "".join(parts), "-map", "[vo]", "-map", "[ao]",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", raw], check=True)
meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meas)[-1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c:v", "copy", "-af", f"volume={-15 - I:.2f}dB,alimiter=limit=0.89:attack=5:release=60:level=disabled",
                "-c:a", "aac", "-b:a", "256k", a.out], check=True)
subprocess.run(["rm", "-f", raw])
print(f"written {a.out}: {length:.1f} s, {n} segments, gain {-15 - I:+.1f} dB")
