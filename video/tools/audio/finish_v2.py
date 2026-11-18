"""The second sound kit: video/public/audio/sfx/v2/ and the faster music bed, added to manifest.json.

    video/tools/heavy.sh python3 -I video/tools/audio/finish_v2.py SOURCES_DIR

SOURCES_DIR (outside the repo) holds the raw library and generated files under the names in SFX below, and the full
track as bed-fast-full.wav. Same rules as finish.py: 48 kHz 16-bit stereo WAV with no metadata; effects start on their
transient (or, for swells, on the first audible sample) and peak at -3 dBFS; music is -18 LUFS integrated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finish import OUT, RATE, decode, fade, key_root, loudnorm, loop, measure, write  # noqa: E402

# ------------------------------------------------------------------ music: the faster cut
# A 120 BPM soft-house track on a 2 s bar grid starting at 0. The bed starts on bar 8 (16 s), so the beat drops 8 s in,
# right after the montage; it keeps the breakdown and the lift, and takes 8 bars out of the last section (cut at
# 92 s -> 108 s, waveform correlation 0.93 before and 0.92 after), so the final hit lands at 88 s.
FAST = {"source": "bed-fast-full.wav", "bpm": 120.0, "start": 16.0, "cut": 92.0, "resume": 108.0, "length": 94.0}
FAST_SECTIONS = {"montage": 0.0, "drop": 8.0, "breakdown": 40.0, "lift": 56.0, "inaudible_edit": 76.0,
                 "final_hit": 88.0, "silent_from": 92.5}
FAST_DESCRIPTION = ("Faster bed for video 1: modern, warm, upbeat soft house at 120 BPM. Eight seconds of rising intro "
                    "for the montage, the beat drops at 8 s, a breakdown at 40 s, the full beat returns at 56 s, and "
                    "a final hit at 88 s.")

# ------------------------------------------------------------------ effects
# name -> (source, description, options). floor: dB below the peak where the sound is taken to start (lower for swells);
# keep: max seconds; tail: keep the last N seconds up to the peak (risers); loop/skip: a seamless ambience loop.
SFX = {
    "shutter-1": ("dl/shutter-1.wav", "Phone camera shutter, the familiar smartphone sound.", {"keep": 0.6}),
    "shutter-2": ("dl/shutter-2.wav", "Real camera shutter click only, crisp and short.", {"floor": -18}),
    "shutter-3": ("dl/shutter-3.wav", "Mirrorless camera shutter, mechanical open and close.", {}),
    "whoosh-1": ("dl/whoosh-1.wav", "Short air whoosh, about 0.4 s, for a quick camera move.", {"floor": -50, "keep": 0.5}),
    "whoosh-2": ("dl/whoosh-2.wav", "Medium wide whoosh, about 0.8 s, for a camera move.", {"floor": -50, "keep": 0.95}),
    "whoosh-3": ("dl/whoosh-3.wav", "Long fast pass-by whoosh with a reverberant tail, about 1.2 s plus tail.",
                 {"floor": -50, "keep": 1.9}),
    "whoosh-4": ("gen/whoosh-4.mp3", "Whip-pan whoosh: a fast rush of air past the camera.", {"floor": -50}),
    "swipe-1": ("dl/swipe-1.wav", "UI slide, a phone screen or card sliding in.", {"floor": -50}),
    "swipe-2": ("dl/swipe-2.wav", "UI slide, a second variation, a little longer.", {"floor": -50}),
    "swipe-3": ("dl/swipe-3.wav", "UI slide, short, like a panel opening.", {"floor": -50}),
    "lockon-1": ("dl/lockon-1.wav", "Real mirrorless camera focus-confirm beep, for a box locking on.", {}),
    "lockon-2": ("dl/lockon-2.wav", "Real camera autofocus lock, the loudest moment of a focus sequence.",
                 {"start": 0.56, "keep": 0.35}),
    "lockon-3": ("gen/lockon-3b.mp3", "One crisp tiny click followed by a short clean high tone, like a focus lock.",
                 {}),
    "boom-1": ("dl/boom-1.wav", "Sub drum kick one-shot: a tight thump for a montage cut on the beat.", {}),
    "boom-2": ("dl/boom-2.wav", "Short clean trailer sub drop with a soft attack, for a cut on the beat.", {}),
    "boom-3": ("gen/boom-3.mp3", "Punchy hit: bright transient over a clean sub thump, short decay.", {}),
    "boom-4": ("gen/boom-4.mp3", "Deep sub thump with a crisp woody click, very short.", {}),
    "boom-stop": ("dl/boom-stop.wav", "Final stop hit with a long reverb tail, for the last cut or the logo.", {}),
    "riser-1": ("dl/riser-1.wav", "Short reverse metal build into a hit point, about 1.6 s; peak at the end.",
                {"tail": 1.6}),
    "riser-2": ("dl/riser-2.wav", "Riser with a whoosh, about 3 s; peak at the end.", {"tail": 3.0}),
    "reverse-swell": ("dl/reverse-swell.wav", "Reverse cymbal swell, about 2.5 s; peak at the end.", {"tail": 2.5}),
    "notify-1": ("dl/notify-1.wav", "Warm two-note marimba notification, the notes 0.3 s apart.", {"keep": 1.6}),
    "notify-2": ("dl/notify-2.wav", "Phone notification tone, two quick soft notes.", {}),
    "tap-1": ("dl/tap-1.wav", "Soft dull UI tap.", {}),
    "tap-2": ("dl/tap-2.wav", "Soft dull UI tap, a second variation.", {}),
    "room-tone-bright": ("dl/room-tone-bright.wav", "Daytime living room: air, birds and life outside a closed "
                         "window. 15 s, loops seamlessly. Play very low.", {"loop": 15.0}),
    "page-flip": ("dl/page-flip.wav", "A book page turning.", {}),
    "paper-photo": ("dl/paper-photo.wav", "A printed photograph being handled.", {}),
    "ceramic-tap": ("dl/ceramic-tap.wav", "A coffee mug set down on a table.", {}),
}


def calm_skip(x, seconds):
    """Where to take an ambience loop so that neither its start nor the second after its end holds a sudden event
    (a bird call or a knock there would repeat on every pass of the loop)."""
    env = np.abs(x).max(1)
    hop = RATE // 20
    env = env[:len(env) // hop * hop].reshape(-1, hop).max(1)          # 50 ms peaks
    n, w = int(seconds * 20), 20
    best = min(range(40, len(env) - n - w - 40, 5),
               key=lambda s: env[s:s + w].max() + env[s + n:s + n + w].max())
    return best / 20


def trim(x, opts):
    if "start" in opts:
        x = x[int(opts["start"] * RATE):]
    mono = np.abs(x).max(1)
    peak = mono.max()
    if "tail" in opts:                                 # the last seconds up to the loudest point + 0.15 s
        top = int(np.argmax(mono))
        end = min(len(x), top + int(0.15 * RATE))
        x = x[max(0, end - int(opts["tail"] * RATE)):end].copy()
        f = int(0.2 * RATE)
        x[:f] *= fade(f)
        return x
    start = int(np.argmax(mono > peak * 10 ** (opts.get("floor", -36) / 20)))
    x = x[max(0, start - int(0.002 * RATE)):]
    mono = np.abs(x).max(1)
    x = x[:len(x) - int(np.argmax(mono[::-1] > peak * 10 ** (-60 / 20)))].copy()
    if "keep" in opts and len(x) > opts["keep"] * RATE:
        x = x[:int(opts["keep"] * RATE)].copy()
        f = int(0.15 * RATE)                           # a cut sound fades out over its last 150 ms
    else:
        f = min(int(0.03 * RATE), len(x) // 4)
    x[-f:] *= fade(f, False)
    g = int(0.002 * RATE)
    x[:g] *= fade(g)
    return x


def build_fast(src_dir, tmp):
    x = decode(src_dir / FAST["source"])
    a, c, r = (int(FAST[k] * RATE) for k in ("start", "cut", "resume"))
    f = int(0.05 * RATE)                               # 50 ms equal-power crossfade ending on the downbeat
    head = x[a:c - f].copy()
    head[:int(0.02 * RATE)] *= fade(int(0.02 * RATE))
    mix = x[c - f:c] * fade(f, False) + x[r - f:r] * fade(f, True)
    y = np.concatenate([head, mix, x[r:]])[:int(FAST["length"] * RATE)]
    y[-int(0.8 * RATE):] *= fade(int(0.8 * RATE), False)
    raw = tmp / "bed-fast.wav"
    write(raw, y)
    loudnorm(raw, OUT / "music" / "bed-fast.wav")
    return {"file": "music/bed-fast.wav", "bpm": FAST["bpm"], "description": FAST_DESCRIPTION,
            "sections_s": FAST_SECTIONS,
            "note": "Bar grid: downbeats every 2.0 s from 0. The montage runs over the last 4 bars of the intro."}


def main():
    src_dir = Path(sys.argv[1]).resolve()
    tmp, check = src_dir / "tmp", src_dir / "check"
    tmp.mkdir(exist_ok=True)
    check.mkdir(exist_ok=True)
    manifest = json.loads((OUT / "manifest.json").read_text())
    fast = build_fast(src_dir, tmp)
    fast.update(measure(OUT / fast["file"], check / "bed-fast.png"))
    fast["key_root_estimate"] = key_root(OUT / fast["file"])
    manifest["music"]["bed-fast"] = fast
    v2 = {}
    for name, (source, description, opts) in SFX.items():
        x = decode(src_dir / source)
        x = loop(x, opts["loop"], calm_skip(x, opts["loop"])) if "loop" in opts else trim(x, opts)
        x = x * (10 ** (-3 / 20) / (np.abs(x).max() + 1e-12))
        target = OUT / "sfx" / "v2" / f"{name}.wav"
        write(target, x)
        entry = {"file": f"sfx/v2/{name}.wav", "description": description}
        entry.update(measure(target, check / f"{name}.png"))
        if name.startswith("room-tone"):
            entry["note"] = "Peak-normalised like the other sfx, so it is loud as delivered: play at about -30 dB."
        v2[name] = entry
    manifest["sfx_v2"] = v2
    if "sfx_v2" not in manifest["about"]:
        manifest["about"] += " sfx_v2 is the second, stronger kit (public/audio/sfx/v2/)."
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for name, e in [("bed-fast", fast)] + list(v2.items()):
        print(f"{name:18} {e['duration_s']:7.3f} s  LUFS {e['lufs_i']}  peak {e['peak_dbfs']:6.2f}  "
              f"clipped {e['clipped_samples']}")


if __name__ == "__main__":
    main()
