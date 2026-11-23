"""Court reactions for the dance contest (plugin RokuganDance.sk; user 2026-11-22: "with failure only having her be
laughed at"). Synthesized in numpy like the soundtrack (tools/gen_music.py), written as Ogg with its ffmpeg:
  SE300 rt_applause.ogg  - a hall of courtiers applauding: twenty-odd pairs of hands, a swell, a polite tail
  SE301 rt_fans.ogg      - the court laughing behind its fans: fans flicked open all round the hall, a couple of
                           sharp fan snaps, and the tittering breath behind them (short airy "ho-ho"s)
and registers them in resource/snd.json (in its own layout).
python -E tools/gen_court_sfx.py
"""
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_music import SR, bandpass, find_ffmpeg, lowpass, noise, norm, write_wav  # noqa: E402

RES = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_tools", "rpgcobo-tool",
                                    "project", "resource"))
PREVIEW = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_art", "preview", "music"))


def clap(rng):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    lo, hi = rng.uniform(700, 1300), rng.uniform(2200, 4200)
    x = norm(bandpass(noise(n, rng), lo, hi)) * np.exp(-t / rng.uniform(0.008, 0.016))
    return x


def applause(rng, dur=4.2):
    out = np.zeros((2, int(dur * SR)))
    for _ in range(24):                                          # each courtier claps at their own pace
        rate = rng.uniform(3.6, 5.2)
        start = rng.uniform(0.0, 0.45)
        stop = dur - rng.uniform(0.6, 1.8)
        pan = rng.uniform(-0.8, 0.8)
        g = rng.uniform(0.4, 1.0)
        t = start
        while t < stop:
            i = int(t * SR)
            c = clap(rng) * g * min(1.0, (t - start) / 0.25 + 0.3) * min(1.0, (stop - t) / 0.6 + 0.2)
            j = min(len(c), out.shape[1] - i)
            out[0, i:i + j] += c[:j] * np.cos((pan + 1) * np.pi / 4)
            out[1, i:i + j] += c[:j] * np.sin((pan + 1) * np.pi / 4)
            t += 1.0 / rate * rng.uniform(0.85, 1.15)
    return out


def fan_open(rng):
    """A folding fan flicked open: a quick rising swish of paper and ribs, a soft clack as it stops."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    sweep = np.zeros(n)
    nz = noise(n, rng)
    for k in range(8):                                           # the sweep, in band slices
        lo = 600 + 400 * k
        seg = bandpass(nz, lo, lo + 500)
        w = np.exp(-((t - 0.015 * k - 0.02) / 0.025) ** 2)
        sweep += seg * w
    clack = norm(bandpass(noise(n, rng), 2500, 7000)) * np.exp(-np.maximum(0, t - 0.13) / 0.004) * (t >= 0.13)
    return norm(sweep) * 0.7 + clack * 0.35


def fan_snap(rng):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return norm(bandpass(noise(n, rng), 1800, 8000)) * np.exp(-t / 0.005)


def titter(rng):
    """A courtier's laugh behind a fan: three or four airy "ho"s, breath through a vowel formant, falling a little."""
    out = []
    f0 = rng.uniform(300, 520)
    for k in range(int(rng.integers(3, 5))):
        n = int(rng.uniform(0.07, 0.1) * SR)
        t = np.arange(n) / SR
        breath = noise(n, rng)
        f = f0 * (1 - 0.04 * k)
        voiced = np.sign(np.sin(2 * np.pi * f * t)) * 0.3                  # a little voice under the breath
        x = bandpass(breath * 0.8 + voiced * 0.4, 400, 1200) + 0.4 * bandpass(breath, 2400, 3200)
        x = norm(x) * np.clip(np.sin(np.pi * t / t[-1]), 0, 1) ** 1.5 * (1 - 0.15 * k)
        out.append(x)
        out.append(np.zeros(int(rng.uniform(0.05, 0.08) * SR)))
    return lowpass(np.concatenate(out), 3500) * 0.5


def fans(rng, dur=3.0):
    out = np.zeros((2, int(dur * SR)))

    def put(sig, at, pan, g):
        i = int(at * SR)
        j = min(len(sig), out.shape[1] - i)
        out[0, i:i + j] += g * sig[:j] * np.cos((pan + 1) * np.pi / 4)
        out[1, i:i + j] += g * sig[:j] * np.sin((pan + 1) * np.pi / 4)
    for _ in range(14):
        put(fan_open(rng), rng.uniform(0.0, 0.9), rng.uniform(-0.9, 0.9), rng.uniform(0.3, 0.8))
    for _ in range(7):
        put(titter(rng), rng.uniform(0.2, 1.6), rng.uniform(-0.8, 0.8), rng.uniform(0.25, 0.5))
    for at in (rng.uniform(1.6, 2.0), rng.uniform(2.1, 2.5)):
        put(fan_snap(rng), at, rng.uniform(-0.6, 0.6), 0.6)
    return out


def write(x, name, peak=0.6):
    x = x / (np.abs(x).max() + 1e-9) * peak
    k = int(0.3 * SR)
    x[:, -k:] *= np.linspace(1, 0, k)
    os.makedirs(PREVIEW, exist_ok=True)
    wav = os.path.join(PREVIEW, name + ".wav")
    write_wav(x, wav)
    ogg = os.path.join(RES, "snd", name + ".ogg")
    subprocess.run([find_ffmpeg(), "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "5", ogg],
                   check=True)
    return x.shape[1]


def register(entries):
    """Add / replace SE entries in snd.json, keeping its hand layout (tabs, CRLF, compact info)."""
    path = os.path.join(RES, "snd.json")
    raw = open(path, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    for sid, (wav, n, en, gain) in entries.items():
        block = (nl.join(['\t"%s":{' % sid, '\t\t"detune":0.0,', '\t\t"gain":%.2f,' % gain,
                          '\t\t"info":{"ch":2,"format":"ogg","freq":44100,"length":%d},' % n, '\t\t"memcache":2,',
                          '\t\t"muteg":0,', '\t\t"name":{"en":"%s","ja":"%s"},' % (en, en), '\t\t"src3d":"3D_OFF",',
                          '\t\t"tags":1,', '\t\t"wav":"/resource/snd/%s.ogg"' % wav, '\t},']))
        pat = re.compile(r'\t"%s":\{.*?\n\t\},\r?\n' % sid, re.S)
        if pat.search(raw):
            raw = pat.sub(lambda _: block + nl, raw, count=1)
        else:
            i = raw.index('\t"_env"')
            raw = raw[:i] + block + nl + raw[i:]
    open(path, "wb").write(raw.encode("utf-8"))


def main():
    rng = np.random.default_rng(300)
    n1 = write(applause(rng), "rt_applause", 0.55)
    n2 = write(fans(rng), "rt_fans", 0.6)
    register({"SE300": ("rt_applause", n1, "Court applause", 0.8), "SE301": ("rt_fans", n2, "Court laughs behind fans",
                                                                            0.9)})
    print("SE300 rt_applause %.1f s, SE301 rt_fans %.1f s" % (n1 / SR, n2 / SR))


if __name__ == "__main__":
    main()
