"""Turns the downloaded and generated sources into the videos' audio: video/public/audio/{music,sfx}/ + manifest.json.

    video/tools/heavy.sh python3 -I video/tools/audio/finish.py SOURCES_DIR

SOURCES_DIR (outside the repo) holds the raw files named as in MUSIC and SFX below. Music is cut on the bar grid and
loudness-normalised to -18 LUFS integrated (ffmpeg loudnorm, two passes, linear gain). Effects are trimmed to start on
their transient with no silence before, trimmed after, and peak-normalised to -3 dBFS. Everything is 48 kHz, 16-bit
stereo WAV with no metadata. Each output is measured (ebur128 + astats) and gets a waveform PNG in SOURCES_DIR/check/.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

RATE = 48000
OUT = Path(__file__).resolve().parents[2] / "public" / "audio"


# ------------------------------------------------------------------ music
# Video 1 bed: the full track with 20 bars taken out of its main section (a jump between two matching phrases,
# waveform correlation 0.89 before and 0.93 after the cut), so the lift lands where the safety scenes start (53.3 s)
# and the track's own ending resolves under the end card.
BPM_A = 109.0
BAR_A = 240 / BPM_A
GRID_A = 0.138                      # first downbeat (s); bars fall on GRID_A + k * BAR_A
CUT_BAR, JUMP_BARS = 31, 20         # cut on the downbeat of bar 31, resume 20 bars later

MUSIC = {
    "bed-presentation": {
        "source": "presentation-full.wav", "bpm": BPM_A, "length": 94.0,
        "description": "Main bed for video 1: light ambient electronica, warm and hopeful, a gentle pulse that "
                       "builds from a sparse intro; full beat and bass from the lift; ends on its own final chord.",
        "sections": {"intro": 0.0, "build": round(GRID_A + 8 * BAR_A, 2), "lift": round(GRID_A + 24 * BAR_A, 2),
                     "inaudible_edit": round(GRID_A + CUT_BAR * BAR_A, 2), "resolve": 88.2, "silent_from": 93.0},
    },
    "bed-presentation-alt": {
        "source": "presentation-alt-edit.wav", "bpm": 98.0, "length": 93.0,
        "description": "Alternative bed for video 1: dreamy, hopeful ambient electronica, slower (98 BPM); a long soft "
                       "build, a clear lift with full beat and bass, a musical ending.",
        "sections": None,           # measured below
    },
    "bed-real": {
        "source": "real-edit.wav", "bpm": 100.0, "length": 52.0,
        "description": "Bed for video 2: understated, curious ambient with a soft steady pulse; no big lift, a gentle "
                       "swell in the middle and a musical ending.",
        "sections": None,
    },
}


# ------------------------------------------------------------------ effects
# name -> (source file, options). keep: max seconds kept; tail: take the last N seconds (risers end on their peak).
SFX = {
    "tap-1": ("tap-1.wav", "Soft glassy UI tap, like a phone button touch."),
    "tap-2": ("tap-2.wav", "Simple soft UI select tap, a second variation."),
    "notify-info": ("notify-info.wav", "Gentle tonal confirm chime for an information notification."),
    "notify-safety": ("notify-safety.wav", "UI alert notification, more insistent than the info chime; no siren."),
    "shutter": ("shutter.wav", "Smartphone camera shutter."),
    "lock-on": ("lock-on.wav", "Soft digital confirm, for a detection box locking on."),
    "swish-1": ("swish-1.wav", "Soft airy designed swish for a transition."),
    "swish-2": ("swish-2.wav", "UI motion swipe, short and light."),
    "swish-3": ("swish-3.wav", "UI motion swipe, a second variation, slightly longer."),
    "riser-short": ("riser-short.wav", "Short cinematic reverse-glass riser into a scene; peak at the end."),
    "door-open": ("door-open.wav", "Wooden front door opening, interior perspective."),
    "typing-soft": ("typing-soft.mp3", "Soft smartphone touchscreen typing, about 2 s."),
    "floodlight": ("floodlight.mp3", "Outdoor floodlight switching on: relay click and a faint electrical hum."),
    "room-tone": ("room-tone.wav", "Quiet house room tone, 10 s, loops seamlessly. Play very low."),
    "dog-steps": ("dog-steps.wav", "A dog's paws running across a wooden floor, indoors."),
    "cat-jump": ("cat-jump.mp3", "A house cat jumping down and landing softly on a wooden floor."),
    "hit-soft": ("hit-soft.wav", "Low designed hit with a soft boom, for the logo."),
}
OPTIONS = {"riser-short": {"tail": 2.0}, "room-tone": {"loop": 10.0, "skip": 5.0}, "notify-safety": {"keep": 2.0},
           "hit-soft": {"keep": 3.5}, "typing-soft": {"keep": 2.3}, "dog-steps": {"keep": 3.0}}


def decode(path, start=None, duration=None):
    span = (["-ss", f"{start}"] if start is not None else []) + (["-t", f"{duration}"] if duration else [])
    raw = subprocess.run(["ffmpeg", "-v", "error", *span, "-i", str(path), "-ac", "2", "-ar", str(RATE),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(RATE), "-ac", "2", "-i", "-",
                    "-map_metadata", "-1", "-c:a", "pcm_s16le", str(path)],
                   input=np.ascontiguousarray(x, np.float32).tobytes(), check=True)


def fade(n, rising=True):
    ramp = np.sin(np.linspace(0, np.pi / 2, n)) ** 2
    return (ramp if rising else ramp[::-1])[:, None]


def loudnorm(src, dst, target=-18.0):
    """Two-pass ffmpeg loudnorm with linear gain to `target` LUFS integrated, true peak <= -1 dBTP."""
    first = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                            f"loudnorm=I={target}:TP=-1:LRA=20:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    m = json.loads(first[first.rindex("{"):first.rindex("}") + 1])
    chain = (f"loudnorm=I={target}:TP=-1:LRA=20:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
             f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
             f"linear=true,aresample={RATE}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", chain, "-map_metadata", "-1",
                    "-ar", str(RATE), "-c:a", "pcm_s16le", str(dst)], check=True)


def lift_and_end(x, bpm):
    """Bar-level sections from the loudness curve: the biggest rise (lift) and where the final decay starts."""
    bar = 240 / bpm
    n = int(bar * RATE)
    mono = x.mean(1)
    k = len(mono) // n
    db = 20 * np.log10(np.sqrt((mono[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    rise = np.diff(db)
    lift = int(np.argmax(rise[2:k - 4])) + 3
    loud = np.percentile(db, 80)
    end = max(i for i in range(k) if db[i] > loud - 4) + 1
    return round(lift * bar, 2), round(end * bar, 2)


def build_music(src_dir, tmp):
    out = {}
    for name, spec in MUSIC.items():
        x = decode(src_dir / spec["source"])
        if name == "bed-presentation":
            a = int((GRID_A + CUT_BAR * BAR_A) * RATE)
            b = a + int(round(JUMP_BARS * BAR_A * RATE))
            f = int(0.05 * RATE)                       # 50 ms equal-power crossfade ending on the downbeat
            head, tail = x[:a - f].copy(), x[b:].copy()
            mix = x[a - f:a] * fade(f, False) + x[b - f:b] * fade(f, True)
            x = np.concatenate([head, mix, tail])
        x = x[:int(spec["length"] * RATE)]
        f = int(0.8 * RATE)
        x[-f:] *= fade(f, False)
        raw = tmp / f"{name}.wav"
        write(raw, x)
        target = OUT / "music" / f"{name}.wav"
        loudnorm(raw, target)
        sections = spec["sections"]
        if sections is None:
            lift, end = lift_and_end(x, spec["bpm"])
            sections = {"intro": 0.0, "lift": lift, "resolve": end}
        out[name] = {"file": f"music/{name}.wav", "bpm": spec["bpm"], "description": spec["description"],
                     "sections_s": sections}
    return out


def trim(x, opts):
    mono = np.abs(x).max(1)
    peak = mono.max()
    if "tail" in opts:                                 # keep the last seconds up to the loudest point + 0.15 s
        top = int(np.argmax(mono))
        end = min(len(x), top + int(0.15 * RATE))
        x = x[max(0, end - int(opts["tail"] * RATE)):end].copy()
        x[:int(0.25 * RATE)] *= fade(int(0.25 * RATE))
        return x
    start = int(np.argmax(mono > peak * 10 ** (-36 / 20)))  # first sample within 36 dB of the peak
    start = max(0, start - int(0.002 * RATE))
    x = x[start:]
    mono = np.abs(x).max(1)
    end = len(x) - int(np.argmax(mono[::-1] > peak * 10 ** (-60 / 20)))
    x = x[:end].copy()
    if "keep" in opts:
        x = x[:int(opts["keep"] * RATE)].copy()
    f = min(int(0.03 * RATE), len(x) // 4)
    x[-f:] *= fade(f, False)
    g = int(0.002 * RATE)
    x[:g] *= fade(g)
    return x


def loop(x, seconds, skip):
    """A `seconds` loop from the middle of a long ambience; its end crossfades into its start (1 s)."""
    s, n, f = int(skip * RATE), int(seconds * RATE), RATE
    seg = x[s:s + n + f].copy()
    head = seg[:f] * fade(f) + seg[n:n + f] * fade(f, False)
    return np.concatenate([head, seg[f:n]])


def build_sfx(src_dir):
    out = {}
    for name, (source, description) in SFX.items():
        opts = OPTIONS.get(name, {})
        x = decode(src_dir / source)
        x = loop(x, opts["loop"], opts["skip"]) if "loop" in opts else trim(x, opts)
        x = x * (10 ** (-3 / 20) / (np.abs(x).max() + 1e-12))
        write(OUT / "sfx" / f"{name}.wav", x)
        out[name] = {"file": f"sfx/{name}.wav", "description": description}
    return out


def measure(path, png):
    """Duration, integrated loudness, sample peak, clipped samples; and a waveform PNG for a visual check."""
    text = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                           "ebur128=peak=sample,astats=measure_overall=Peak_level+Number_of_samples:measure_perchannel=none",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", text)[-1].replace("-inf", "-200"))
    peak = float(re.findall(r"Peak level dB:\s+(-?[\d.]+|-inf)", text)[-1].replace("-inf", "-200"))
    x = decode(path)
    clipped = int((np.abs(x) >= 0.9999).sum())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-filter_complex",
                    "showwavespic=s=1200x240:split_channels=0:colors=0x2b6cb0", "-frames:v", "1", str(png)],
                   check=True)
    return {"duration_s": round(len(x) / RATE, 3), "lufs_i": lufs if len(x) >= 0.4 * RATE else None,  # 400 ms gate "peak_dbfs": round(peak, 2),
            "clipped_samples": clipped}


def key_root(path):
    """Rough tonal root from a chroma profile (root only; the mode is not estimated)."""
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    x = decode(path).mean(1)
    size, acc = 16384, np.zeros(12)
    f = np.fft.rfftfreq(size, 1 / RATE)
    keep = (f > 50) & (f < 2000)
    bins = np.round(12 * np.log2(f[keep] / 440)).astype(int) % 12
    for i in range(0, len(x) - size, size):
        sp = np.abs(np.fft.rfft(x[i:i + size] * np.hanning(size)))[keep] ** 2
        np.add.at(acc, bins, sp)
    return notes[int(np.argmax(acc))]


def main():
    src_dir = Path(sys.argv[1]).resolve()
    tmp, check = src_dir / "tmp", src_dir / "check"
    tmp.mkdir(exist_ok=True)
    check.mkdir(exist_ok=True)
    music, sfx = build_music(src_dir, tmp), build_sfx(src_dir)
    for kind, items in (("music", music), ("sfx", sfx)):
        for name, entry in items.items():
            stats = measure(OUT / entry["file"], check / f"{name}.png")
            entry.update(stats)
            if kind == "music":
                entry["key_root_estimate"] = key_root(OUT / entry["file"])
            if stats["peak_dbfs"] < -60 or stats["clipped_samples"]:
                print(f"CHECK {name}: {stats}")
    manifest = {
        "about": "Audio for the two videos. Music is -18 LUFS integrated; sfx are peak-normalised to -3 dBFS and "
                 "start on their transient (set their level in the edit). 48 kHz, 16-bit WAV. Section times are in "
                 "seconds from the start of each file.",
        "music": music, "sfx": sfx}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for kind, items in (("music", music), ("sfx", sfx)):
        for name, e in items.items():
            print(f"{kind:5} {name:22} {e['duration_s']:7.3f} s  {e['lufs_i'] or float('nan'):7.1f} LUFS  peak {e['peak_dbfs']:6.2f} dBFS"
                  f"  clipped {e['clipped_samples']}  {e.get('sections_s', '')}")


if __name__ == "__main__":
    main()
