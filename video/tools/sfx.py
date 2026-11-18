"""Synthesises the few sound effects of video 2 into video/public/real/sfx/ (16-bit mono WAV, deterministic).

    python3 video/tools/sfx.py
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
OUT = Path(__file__).resolve().parents[1] / "public" / "real" / "sfx"
rng = np.random.default_rng(7)


def t(sec):
    return np.arange(int(SR * sec)) / SR


def env(n, attack, decay):
    x = np.arange(n) / SR
    return np.minimum(1, x / max(attack, 1e-4)) * np.exp(-x / decay)


def lowpass(x, a):
    y = np.zeros_like(x)
    for i in range(1, len(x)):
        y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y


def save(name, x, gain=0.8):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def shutter():
    n = int(SR * 0.12)
    x = np.zeros(n)
    for start, dur, amp in ((0.0, 0.012, 1.0), (0.045, 0.02, 0.7)):
        s = int(start * SR)
        m = int(dur * SR)
        burst = rng.standard_normal(m) * env(m, 0.0005, dur / 4)
        x[s:s + m] += amp * (burst - lowpass(burst, 0.08))      # high-passed click
    return x


def tick():
    x = t(0.04)
    return np.sin(2 * np.pi * 2100 * x) * env(len(x), 0.0005, 0.008)


def whoosh():
    x = t(0.45)
    noise = rng.standard_normal(len(x))
    shape = np.sin(np.pi * x / x[-1]) ** 2
    return lowpass(noise, 0.06) * shape


def ping():
    x = t(0.9)
    a = np.sin(2 * np.pi * 988 * x) * env(len(x), 0.002, 0.25)
    b = np.zeros_like(x)
    d = int(0.11 * SR)
    b[d:] = np.sin(2 * np.pi * 1318 * x[:-d]) * env(len(x) - d, 0.002, 0.35)
    return a + 0.9 * b


def confirm():
    x = t(0.6)
    low = np.sin(2 * np.pi * 110 * x) * env(len(x), 0.004, 0.12)
    tone = (np.sin(2 * np.pi * 660 * x) + 0.6 * np.sin(2 * np.pi * 990 * x)) * env(len(x), 0.003, 0.16)
    return 0.8 * low + 0.5 * tone


if __name__ == "__main__":
    save("shutter.wav", shutter(), 0.7)
    save("tick.wav", tick(), 0.5)
    save("whoosh.wav", whoosh(), 0.6)
    save("ping.wav", ping(), 0.7)
    save("confirm.wav", confirm(), 0.7)
    print("wrote", sorted(p.name for p in OUT.iterdir()))
