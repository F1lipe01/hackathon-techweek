"""The fourth kit, real-object sounds only: video/public/audio/sfx/v4/, added to manifest.json with texture measures.

    video/tools/heavy.sh python3 -I video/tools/audio/finish_v4.py SOURCES_DIR

No synthesised tones, chimes or beeps: every sound is a recording of a visible action, with 2-3 takes of anything that
repeats (a third vibration take measured a tonal line of 20.4 dB and was left out). Same processing and measures as finish_v3.py (hf8, hf4, tonal, crinkle); ambiences loop seamlessly from a
calm stretch of the recording (finish_v2.calm_skip).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finish import OUT, RATE, fade, loop, measure, write  # noqa: E402
from finish_v2 import calm_skip  # noqa: E402
from finish_v3 import decode, shape, texture  # noqa: E402

REAL = {"hf8": 0.05, "tonal": 20.0}
QUIET = {"hf8": 0.02, "tonal": 20.0, "crinkle": 3.0}
SOFT_SHUTTER = "lowpass=f=7000"
SFX = {
    "vib-1": ("dl/vib-1.wav", "Phone vibrating on a table, one short buzz.", {"limits": REAL}),
    "vib-2": ("dl/vib-3.wav", "Phone vibrating, one buzz of about 0.7 s (a second take).",
              {"window": (0.28, 1.00), "fades": (0.01, 0.08), "limits": REAL}),
    "tap-1": ("dl/tap-1.wav", "A finger tapping a phone touchscreen.", {"limits": REAL}),
    "tap-2": ("dl/tap-2.wav", "A finger tapping a phone touchscreen, second take.", {"limits": REAL}),
    "keys-1": ("dl/keys-1.wav", "Keys on a plastic ring picked up from a wooden surface.",
               {"limits": {"hf8": 0.30, "tonal": 20.0}}),
    "keys-2": ("dl/keys-2.wav", "Car keys picked up from a table.", {"limits": {"hf8": 0.30, "tonal": 20.0}}),
    "door-1": ("dl/door-1.wav", "Wooden entrance door opening and closing softly, heard from inside.",
               {"limits": REAL}),
    "door-2": ("dl/door-2.wav", "Interior room door opening and closing.", {"limits": REAL}),
    "room-living": ("dl/room-living.wav", "Quiet living room by day, faint distant traffic. 9 s, loops seamlessly. "
                    "Play very low.", {"loop": 9.0, "limits": QUIET}),
    "room-kitchen": ("dl/room-kitchen.wav", "Quiet kitchen: a soft appliance hum. 9 s, loops seamlessly. Play very low.",
                     {"af": "lowpass=f=6000", "loop": 9.0, "limits": QUIET}),
    "shutter-2": ("dl/shutter-2.wav", "Gentle real camera shutter, gently low-passed; rotate with v3 shutter-soft.",
                  {"af": "lowpass=f=6000", "floor": -20, "limits": REAL}),
    "shutter-3": ("dl/shutter-3.wav", "Gentle real film-camera shutter release, low-passed; third take.",
                  {"af": "lowpass=f=6000,lowpass=f=6000", "limits": REAL}),
    "riser-air": ("dl/riser-air.wav", "Soft wide air riser, 3.5 s, peaking at its end: for the questions burst.",
                  {"tail": 3.5, "limits": {"hf8": 0.02, "tonal": 20.0, "crinkle": 3.0}}),
    "slide-card": ("dl/slide-card.wav", "A light playing card slid across a table, softened.",
                   {"af": "lowpass=f=5000,lowpass=f=5000", "limits": {"hf8": 0.03, "tonal": 20.0, "crinkle": 3.5}}),
}
KEYS = {"hf8": "hf8", "hf4": "hf4", "tonal": "tonal_db", "crinkle": "crinkle_db"}


def riser_tail(x, seconds):
    """The last `seconds` of a riser, ending just after its loudest point, with a soft start."""
    top = int(np.argmax(np.abs(x).max(1)))
    end = min(len(x), top + int(0.05 * RATE))
    x = x[max(0, end - int(seconds * RATE)):end].copy()
    f = int(0.3 * RATE)
    x[:f] *= fade(f)
    return x


def main():
    src_dir = Path(sys.argv[1]).resolve()
    check = src_dir / "check"
    check.mkdir(exist_ok=True)
    manifest = json.loads((OUT / "manifest.json").read_text())
    v4, failed = {}, []
    for name, (source, description, opts) in SFX.items():
        x = decode(src_dir / source, opts.get("af"))
        if "loop" in opts:
            x = loop(x, opts["loop"], calm_skip(x, opts["loop"]))
        elif "tail" in opts:
            x = riser_tail(x, opts["tail"])
        else:
            x = shape(x, opts)
        x = x * (10 ** (-3 / 20) / (np.abs(x).max() + 1e-12))
        target = OUT / "sfx" / "v4" / f"{name}.wav"
        write(target, x)
        entry = {"file": f"sfx/v4/{name}.wav", "description": description}
        entry.update(measure(target, check / f"{name}.png"))
        entry["texture"] = t = texture(x)
        if name.startswith("room-"):
            entry["note"] = "Peak-normalised like the other sfx, so it is loud as delivered: play at about -30 dB."
        over = [k for k, lim in opts["limits"].items() if t[KEYS[k]] > lim]
        if over:
            failed.append(f"{name}: over {over} {t}")
        v4[name] = entry
    manifest["sfx_v4"] = v4
    if "sfx_v4" not in manifest["about"]:
        manifest["about"] += (" sfx_v4 holds real-object sounds only (public/audio/sfx/v4/); rotate the takes of "
                              "any sound that repeats.")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for name, e in v4.items():
        t = e["texture"]
        print(f"{name:13} {e['duration_s']:6.3f} s  >8k {t['hf8']*100:4.1f}%  centroid {t['centroid_hz']:5d} Hz  "
              f"tonal {t['tonal_db']:4.1f}  crinkle {t['crinkle_db']}")
    print("\n".join(failed) or "all within limits")


if __name__ == "__main__":
    main()
