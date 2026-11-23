"""Real instrument recordings for the soundtrack (user 2026-11-22: "replace synthetics with real ... only if you can").
Cuts one-shot samples out of freely licensed Freesound recordings (previews kept in
_art/sources/real_instruments/freesound/, licences in its sources.json and CREDITS.md) and writes them, with an index,
to _art/sources/real_instruments/samples/. tools/gen_music.py plays these instead of its synthesized models where a
real one exists (real_shamisen, real_hit).
  shamisen   notes cut from a real player's improvisation (365262, CC0) and a second recording (721267, CC0): each
             clean, well-separated pluck, its pitch measured (YIN), the best one kept per semitone
  kotsuzumi  hits from a kotsuzumi roll (330563, CC0)
  tsuzumi    a tsuzumi hit (203346, CC-BY 3.0 klemmy) - the otsuzumi's "kan" is this, pitched up
  taiko      o-daiko / taiko hits (486140, 486141 CC0; 82712 CC-BY 4.0 sandyrb; 203344 CC-BY 3.0 klemmy)
  clap       wooden blocks clapped together (717371, CC0) - the ki and the tsuke's crack
  koto       notes from a real koto improvisation (365242, CC0) and a koto hit (175672, CC0)
  suzu       the kagura bell-tree / shrine bells, shaken (519190, 364846, 521822; CC0)
python -E tools/real_samples.py      (prints what it kept)
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", "_art", "sources", "real_instruments"))
SRC = os.path.join(ROOT, "freesound")
OUT = os.path.join(ROOT, "samples")
SR = 44100


def ffmpeg():
    import gen_music
    return gen_music.find_ffmpeg()


def load(name):
    raw = subprocess.run([ffmpeg(), "-loglevel", "error", "-i", os.path.join(SRC, name), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(float)


def save(x, name):
    os.makedirs(OUT, exist_ok=True)
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def envelope(x, hop=220):
    n = len(x) // hop
    return np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1)), hop


def onsets(x, rise=2.2, floor=0.04):
    e, hop = envelope(x)
    top = e.max()
    out = []
    for i in range(2, len(e)):
        if e[i] > rise * max(e[i - 2], 1e-5) and e[i] > floor * top and (not out or i - out[-1] > 8):
            out.append(i)
    return [i * hop for i in out], e, hop


def yin(seg, fmin=70, fmax=1400):
    """The fundamental of a short stretch (YIN difference function); 0 if unclear."""
    n = len(seg)
    tmax = int(SR / fmin)
    if n < 2 * tmax:
        return 0.0, 1.0
    d = np.array([np.sum((seg[:n - tmax] - seg[t:t + n - tmax]) ** 2) for t in range(tmax)])
    cmnd = d[1:] * np.arange(1, tmax) / (np.cumsum(d[1:]) + 1e-12)
    lo = int(SR / fmax)
    k = lo + int(np.argmin(cmnd[lo:]))
    for t in range(lo, tmax - 1):                            # the first dip under the threshold
        if cmnd[t] < 0.15:
            k = t
            while k + 1 < tmax - 1 and cmnd[k + 1] < cmnd[k]:
                k += 1
            break
    if 0 < k < len(cmnd) - 1:                                # (sub-sample: a parabola through the dip, so the pitch
        y0, y1, y2 = cmnd[k - 1], cmnd[k], cmnd[k + 1]      # is good to a few cents, not a third of a semitone)
        den = y0 - 2 * y1 + y2
        off = 0.5 * (y0 - y2) / den if abs(den) > 1e-12 else 0.0
        return SR / (k + 1 + off), float(y1)
    return SR / (k + 1), float(cmnd[k])


def hps(seg, fmin=70, fmax=1500):
    """The fundamental by harmonic product spectrum (the spectrum times itself squeezed by 2, 3 and 4)."""
    if len(seg) < 8192:
        seg = np.pad(seg, (0, 8192 - len(seg)))
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    h = S.copy()
    for k in (2, 3, 4):
        d = S[::k]
        h[:len(d)] *= d
    lo, hi = np.searchsorted(f, fmin), np.searchsorted(f, fmax)
    return float(f[lo + int(np.argmax(h[lo:hi]))]) if hi > lo else 0.0


def cut(x, at, length, fade=0.02):
    seg = x[at:at + int(length * SR)].copy()
    k = int(fade * SR)
    if len(seg) > k:
        seg[-k:] *= np.linspace(1, 0, k)
    return seg


def shamisen():
    return plucked(("fs_365262.mp3", "fs_721267.mp3"), "shamisen")


def koto():
    """The koto: notes cut from a real player's improvisation (365242, CC0), and a single koto hit (175672, CC0)."""
    return plucked(("fs_365242.mp3", "fs_175672.mp3"), "koto", max_len=2.2)


def plucked(names, prefix, max_len=1.6):
    """Clean plucks: an onset with at least 0.45 s before the next, a clear pitch 70 ms in, a strong attack."""
    kept = {}
    for name in names:
        x = load(name)
        ons, e, hop = onsets(x)
        for a, b in zip(ons, ons[1:] + [len(x)]):
            gap = (b - a) / SR
            if gap < 0.45:
                continue
            seg = x[a + int(0.05 * SR): a + int(0.05 * SR) + 2048]
            f0, clarity = yin(seg)
            fh = hps(x[a + int(0.03 * SR): a + int(0.03 * SR) + 8192])
            if not f0 or clarity > 0.2 or not fh:
                continue
            # (YIN alone landed an octave or two off on many plucks) keep a note only when the harmonic-product
            # spectrum agrees with YIN to within half a semitone, and label it by the HPS
            if abs(12 * np.log2(f0 / fh)) > 0.5:
                continue
            midi = 69 + 12 * np.log2(f0 / 440.0)                 # (YIN, refined: the precise one)
            m = int(round(midi))
            detune = midi - m
            peak = np.abs(x[a:a + int(0.05 * SR)]).max()
            score = peak * (1 - clarity) * (1 - abs(detune)) * min(gap, 1.5)
            if m not in kept or score > kept[m][0]:
                kept[m] = (score, name, a, min(gap, max_len), detune)
    index = {}
    for m, (score, name, a, ln, detune) in sorted(kept.items()):
        x = load(name)
        seg = cut(x, max(0, a - int(0.005 * SR)), ln)
        f = "%s_%d.wav" % (prefix, m)
        save(seg, f)
        index[str(m)] = {"file": f, "detune": round(float(detune), 3), "from": name}
    return index


def hits(name, n=None, length=1.0, prefix="hit"):
    x = load(name)
    ons, e, hop = onsets(x, rise=1.8, floor=0.15)
    ons = ons or [int(np.argmax(np.abs(x))) - int(0.01 * SR)]
    out = []
    for k, a in enumerate(ons[:n] if n else ons):
        seg = cut(x, max(0, a - int(0.004 * SR)), length)
        f = "%s_%d.wav" % (prefix, k)
        save(seg, f)
        out.append(f)
    return out


def main():
    index = {"shamisen": shamisen(),
             "kotsuzumi": hits("fs_330563.mp3", 7, 0.9, "kotsuzumi"),
             "tsuzumi": hits("fs_203346.mp3", 1, 0.3, "tsuzumi"),
             "taiko": hits("fs_486140.mp3", 1, 1.6, "taiko_a") + hits("fs_486141.mp3", 1, 1.7, "taiko_b"),
             "odaiko": hits("fs_82712.mp3", 1, 2.3, "odaiko"),
             "taiko_open": hits("fs_203344.mp3", 1, 0.8, "taiko_open"),
             "clap": hits("fs_717371.mp3", 4, 0.35, "clap"),
             "koto": koto(),
             # the suzu (the kagura bell-tree) and shrine bells: shakes cut from 519190 / 364846 / 521822 (CC0)
             "suzu": hits("fs_519190.mp3", 6, 0.9, "suzu") + hits("fs_364846.mp3", 4, 0.9, "shrinebell") +
             hits("fs_521822.mp3", 2, 0.9, "bells")}
    json.dump(index, open(os.path.join(OUT, "index.json"), "w"), indent=1)
    for k in ("shamisen", "koto"):
        sh = sorted(int(q) for q in index[k])
        print("%s: %d notes, MIDI %s" % (k, len(sh), sh))
    for k, v in index.items():
        if k not in ("shamisen", "koto"):
            print("%s: %d" % (k, len(v)))


if __name__ == "__main__":
    main()
