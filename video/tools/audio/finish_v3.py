"""The third sound kit, smooth and quiet: video/public/audio/sfx/v3/, added to manifest.json with texture measures.

    video/tools/heavy.sh python3 -I video/tools/audio/finish_v3.py SOURCES_DIR

SOURCES_DIR (outside the repo) holds the raw library files as dl/<name>.wav. Each sound is cut to a window with soft
fades (transitions) or trimmed to its transient (clicks, slides, shutter), optionally low-passed, peak-normalised to
-3 dBFS and written as 48 kHz 16-bit stereo WAV. Every output is measured and must pass its texture limits:
  hf8 / hf4   share of the energy above 8 kHz / 4 kHz (bright noise reads as crinkle, plastic or hiss);
  tonal       how far the sharpest line of the averaged 80 Hz-12 kHz spectrum stands above the median of its
              third octave, in dB (noise and clicks average out below about 16; beeps and chimes measure 28 to 48);
  crinkle     roughness of the 2-12 kHz envelope, in dB (crackle, cloth, paper texture: above about 3).
The manifest also marks the earlier files left out after a listening check (`avoid`), with the measure that explains it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finish import OUT, RATE, fade, measure, write  # noqa: E402

# name -> (source, description, options). window: [start, end] s of the source; fades: (in, out) s;
# af: ffmpeg filters applied first; limits: the texture limits this sound must meet.
SMOOTH = {"hf8": 0.02, "hf4": 0.10, "tonal": 20.0, "crinkle": 3.0}
LOW_CUT = "highpass=f=90,highpass=f=90"     # the sources carry much of their energy below 60 Hz, unheard on laptops
SFX = {
    "trans-1": ("dl/trans-1.wav", "Short smooth low-mid air transition, about 0.3 s of body.",
                {"af": LOW_CUT, "window": (0.20, 0.62), "fades": (0.06, 0.16), "limits": SMOOTH}),
    "trans-2": ("dl/trans-2.wav", "Medium smooth soft-wind transition, about 0.6 s of body.",
                {"af": LOW_CUT, "window": (0.85, 1.70), "fades": (0.10, 0.22), "limits": SMOOTH}),
    "trans-3": ("dl/trans-3.wav", "Long smooth low-mid transition, about 1 s, with a soft fading tail.",
                {"af": LOW_CUT, "window": (0.30, 1.70), "fades": (0.08, 0.40), "limits": SMOOTH}),
    "trans-4": ("dl/trans-4.wav", "Rising air swell that stops dead: lay its end on the cut.",
                {"af": LOW_CUT, "window": (0.10, 1.22), "fades": (0.25, 0.02), "limits": SMOOTH}),
    "click-1": ("dl/click-1.wav", "Muted mechanical toggle click, for a box locking on.",
                {"limits": {"hf8": 0.05, "tonal": 20.0}}),
    "click-2": ("dl/click-2.wav", "Small dry mechanical click-on, precise and soft.",
                {"limits": {"hf8": 0.05, "tonal": 20.0}}),
    "click-3": ("dl/click-3.wav", "Dry mechanical button press (the press only), low-passed to soften it.",
                {"af": "lowpass=f=6000", "floor": -20, "keep": 0.15, "limits": {"hf8": 0.05, "tonal": 20.0}}),
    "slide-1": ("dl/slide-1.wav", "Soft slide: a book across a table, low-passed to a felt-like texture.",
                {"af": "highpass=f=120,lowpass=f=3500,lowpass=f=3500",
                 "limits": {"hf8": 0.03, "tonal": 20.0, "crinkle": 3.5}}),
    "slide-2": ("dl/slide-2.wav", "Soft slide: a large sheet moved on a table, low-passed to a felt-like texture.",
                {"af": "highpass=f=120,lowpass=f=3500,lowpass=f=3500",
                 "limits": {"hf8": 0.03, "tonal": 20.0, "crinkle": 3.5}}),
    "shutter-soft": ("dl/shutter-soft.wav", "Softer natural camera shutter: one clean click and release, gently "
                     "low-passed.", {"af": "lowpass=f=7000", "limits": {"hf8": 0.05, "tonal": 20.0}}),
}

# Earlier files left out after a listening check, with the measure that explains each.
AVOID = {
    "sfx_v2": {
        "lockon-1": "two tonal beeps (tonal 29 dB): reads as a quiz or game sound",
        "lockon-3": "a click with a sustained tone (tonal 44 dB, 70 % above 8 kHz)",
        "swipe-1": "rough noisy texture (crinkle 5.3 dB)",
        "swipe-2": "bright squeezy texture (31 % above 8 kHz, crinkle 5.6 dB)",
        "swipe-3": "UI swipe from the same set; replaced by slide-1 and slide-2",
        "whoosh-2": "bright noise (13 % above 8 kHz, centroid 4.4 kHz): the plastic-bag sound",
        "whoosh-4": "crackly texture (crinkle 3.8 dB)",
    },
    "sfx": {
        "lock-on": "a pure tonal beep (tonal 48 dB)",
        "swish-2": "bright (47 % above 4 kHz)",
        "swish-3": "bright (76 % above 4 kHz)",
    },
}


def decode(path, af=None):
    chain = ["-af", af] if af else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), *chain, "-ac", "2", "-ar", str(RATE),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def texture(x):
    """hf8, hf4, centroid (Hz), tonal (dB), crinkle (dB) of a sound; see the module docstring."""
    x = x.mean(1).astype(np.float64)
    n, hop = 2048, 512
    k = max(1, (len(x) - n) // hop)
    fr = np.stack([x[i * hop:i * hop + n] for i in range(k)]) * np.hanning(n)
    P = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / RATE)
    e = P.sum(1)
    act = e > e.max() * 1e-3
    S = P[act].sum(0)
    m = 16384                                         # averaged long-frame spectrum, 2.9 Hz bins, for the line test
    y = np.pad(x, (0, max(0, m - len(x))))
    L = sum(np.abs(np.fft.rfft(y[i:i + m] * np.hanning(m))) ** 2 for i in range(0, len(y) - m + 1, m // 4))
    fl = np.fft.rfftfreq(m, 1 / RATE)
    tonal = 0.0
    for i in np.where((fl > 80) & (fl < 12000))[0]:
        lo, hi = np.searchsorted(fl, fl[i] / 2 ** (1 / 6)), np.searchsorted(fl, fl[i] * 2 ** (1 / 6))
        tonal = max(tonal, 10 * np.log10(L[i] / (np.median(L[lo:hi]) + 1e-20)))
    F = np.fft.rfft(x)
    ff = np.fft.rfftfreq(len(x), 1 / RATE)
    F[(ff < 2000) | (ff > 12000)] = 0
    b = np.fft.irfft(F, len(x))
    h = RATE // 1000
    env = 20 * np.log10(np.abs(b[:len(b) // h * h]).reshape(-1, h).max(1) + 1e-9)
    live = env > env.max() - 30
    rough = env - np.convolve(env, np.ones(40) / 40, "same")
    return {"hf8": round(float(S[f > 8000].sum() / S.sum()), 4), "hf4": round(float(S[f > 4000].sum() / S.sum()), 4),
            "centroid_hz": round(float((S * f).sum() / S.sum())), "tonal_db": round(float(tonal), 1),
            "crinkle_db": round(float(np.std(rough[live])) if live.sum() > 10 else 0.0, 1)}


def shape(x, opts):
    if "window" in opts:
        a, b = opts["window"]
        x = x[int(a * RATE):int(b * RATE)].copy()
        fi, fo = (int(s * RATE) for s in opts["fades"])
        x[:fi] *= fade(fi)
        x[-fo:] *= fade(fo, False)
        return x
    mono = np.abs(x).max(1)
    peak = mono.max()
    start = max(0, int(np.argmax(mono > peak * 10 ** (opts.get("floor", -40) / 20))) - int(0.002 * RATE))
    x = x[start:]
    mono = np.abs(x).max(1)
    x = x[:len(x) - int(np.argmax(mono[::-1] > peak * 10 ** (-60 / 20)))].copy()
    if "keep" in opts:
        x = x[:int(opts["keep"] * RATE)].copy()
    f = min(int(0.03 * RATE), len(x) // 4)
    x[-f:] *= fade(f, False)
    g = int(0.002 * RATE)
    x[:g] *= fade(g)
    return x


def main():
    src_dir = Path(sys.argv[1]).resolve()
    check = src_dir / "check"
    check.mkdir(exist_ok=True)
    manifest = json.loads((OUT / "manifest.json").read_text())
    v3, failed = {}, []
    for name, (source, description, opts) in SFX.items():
        x = shape(decode(src_dir / source, opts.get("af")), opts)
        x = x * (10 ** (-3 / 20) / (np.abs(x).max() + 1e-12))
        target = OUT / "sfx" / "v3" / f"{name}.wav"
        write(target, x)
        entry = {"file": f"sfx/v3/{name}.wav", "description": description}
        entry.update(measure(target, check / f"{name}.png"))
        entry["texture"] = texture(x)
        t = entry["texture"]
        over = [k for k, lim in opts["limits"].items()
                if t[{"hf8": "hf8", "hf4": "hf4", "tonal": "tonal_db", "crinkle": "crinkle_db"}[k]] > lim]
        if over:
            failed.append(f"{name}: over {over} {t}")
        v3[name] = entry
    manifest["sfx_v3"] = v3
    for section, items in AVOID.items():
        for name, reason in items.items():
            if name in manifest.get(section, {}):
                manifest[section][name]["avoid"] = reason
    if "sfx_v3" not in manifest["about"]:
        manifest["about"] += (" sfx_v3 is the smooth kit (public/audio/sfx/v3/), each with texture measures; entries "
                              "marked `avoid` were left out after a listening check.")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for name, e in v3.items():
        t = e["texture"]
        print(f"{name:13} {e['duration_s']:6.3f} s  peak {e['peak_dbfs']:6.2f}  >8k {t['hf8']*100:4.1f}%  >4k "
              f"{t['hf4']*100:5.1f}%  centroid {t['centroid_hz']:5d} Hz  tonal {t['tonal_db']:4.1f}  crinkle {t['crinkle_db']}")
    print("\n".join(failed) or "all within limits")


if __name__ == "__main__":
    main()
