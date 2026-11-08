"""The soundtrack (user: "music should be more medieval Japanese :) but i appreciate sound"; v2 2026-11-07: "go
through the music to clean it up and add different boss battle scores"). Every track is synthesized here in numpy
and composed from Japanese scales:

  instruments  koto, jushichigen (bass koto), shamisen, biwa (plucked strings with sawari buzz, oshi-de bends),
               shakuhachi, shinobue, hichiriki and horagai (whole legato lines: breath, meri scoops, enbai slides,
               late vibrato), sho (aitake clusters), o-daiko, shime-daiko, kakko, hyoshigi, atarigane, kane, rin,
               bonsho; a choir and strings for the climaxes; ambience: waves, drips, wind, insects, thunder.
               Battles and bosses (user: "light rock with biwa mixed in"): a rock kit, bass and a lightly driven
               guitar under the biwa, with taiko fills
  scales       yo (D E G A B), in / miyako-bushi (D Eb G A Bb), ryo, hirajoshi, min'yo (= rock's minor pentatonic)

Melodies are written out by hand (M() strings: scale degrees and beats) with antecedent / consequent phrases,
sections (intro, A, A', B, breakdowns) and variation on repeats; timing and velocity are humanised.
Two leitmotifs: the travelers' theme (TRAV_A/TRAV_B, D ryo: the title, the join-up, the ending and the last
battle) and Doji Nashiko's motif (NASHIKO, D in: all three phases of the final battle).

Each looping track is rendered circularly (notes and reverb tails that run past the end wrap round to the loop
start), so it loops without a seam. Tracks with an intro set the engine's looppoint: the intro plays once, then
the body loops. Short cues (victory, inn, fall) play an intro and loop a quiet tail. Mastering: a K-weighted loudness
target per track (calm places quieter than fights), a look-ahead peak limiter at -1 dBFS.
Writes resource/bgm/rt_<key>.ogg (ffmpeg, libvorbis) and registers MU101+ in resource/bgm.json; the engine's victory,
inn and game-over entries (MU021, MU022, MU017) are re-pointed to the Japanese cues. gen_maps assigns map tracks
(MUSIC ids); gen_data assigns battle tracks with battle_music(group name) (BATTLE_MUSIC below).
python -E tools/gen_music.py [key ...]      (preview WAVs and a level report in _art/preview/music/)
python -E tools/gen_music.py --clips [key ...]   (also 45 s MP3 previews in _art/preview/agents/music/)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource"))
PREVIEW = os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "music"))
CLIPS = os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "agents", "music"))
SR = 44100

YO, IN, RYO, HIRA = [0, 2, 5, 7, 9], [0, 1, 5, 7, 8], [0, 2, 4, 7, 9], [0, 2, 3, 7, 8]
MINYO = [0, 3, 5, 7, 10]          # min'yo (folk) scale: also rock's minor pentatonic, so the battle band agrees


def hz(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69) / 12.0)


def deg(scale, root, d):
    """Scale degree d (any integer; 5 = an octave up in a pentatonic scale) -> MIDI note."""
    o, i = divmod(d, len(scale))
    return root + 12 * o + scale[i]


def in_key(tr, m):
    return tr is None or tr.sc is None or (m - tr.root) % 12 in tr.sc


def keyed(tr, ms):
    """A cluster / chord with every note in the track's key (duplicates dropped)."""
    return sorted(set(snap(tr, m) for m in ms))


def snap(tr, m):
    """m, or the nearest note of the track's key (a step down first). Keeps accompaniment from sounding a semitone
    against the melody (user, the Orochi fix: "the two layers of music do not match")."""
    if in_key(tr, m):
        return m
    for d in (-1, 1, -2, 2):
        if in_key(tr, m + d):
            return m + d
    return m


def fifth(tr, r):
    """The power-chord interval over r: a fifth if it is in the key, else a fourth."""
    return 7 if in_key(tr, r + 7) or not in_key(tr, r + 5) else 5


def key_step(tr, r, semi):
    """A riff note given as semitones over the tonic, moved by scale steps onto the chord root r (parallel in the
    key, not chromatic), then snapped into the key."""
    if tr is None or tr.sc is None or not in_key(tr, r):
        return snap(tr, r + semi)
    sc = tr.sc
    pc = (r - tr.root) % 12
    o, rem = divmod(semi, 12)
    d = max(i for i, v in enumerate(sc) if v <= rem)
    return snap(tr, deg(sc, r - pc, sc.index(pc) + d + len(sc) * o) + rem - sc[d])


# ------------------------------------------------------------------------------------------- signal helpers
def tvec(dur):
    return np.arange(max(1, int(dur * SR))) / SR


def env(n, a, r, sustain=1.0):
    """Linear attack a s, exponential-ish release r s at the end."""
    e = np.full(n, sustain)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    na = min(na, n)
    e[:na] = np.linspace(0, sustain, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def _freqs(n):
    return np.fft.rfftfreq(n, 1.0 / SR)


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = _freqs(len(x))
    w = np.exp(-0.5 * ((np.log(np.maximum(f, 1.0)) - np.log(np.sqrt(lo * hi))) / (0.5 * np.log(hi / lo))) ** 2)
    return np.fft.irfft(X * w, len(x))


def lowpass(x, fc):
    X = np.fft.rfft(x)
    f = _freqs(len(x))
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))


def highpass(x, fc):
    X = np.fft.rfft(x)
    r = (_freqs(len(x)) / fc) ** 2
    return np.fft.irfft(X * r / np.sqrt(1 + r * r), len(x))


def phase(fcurve):
    return 2 * np.pi * np.cumsum(fcurve) / SR


def noise(n, rng):
    return rng.standard_normal(n)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


# ---- a render cache: patterns repeat the same notes hundreds of times, so keep a few takes of each and pick one
_CACHE = {}


def cached(key, rng, make, takes=3):
    lst = _CACHE.setdefault(key, [])
    if len(lst) < takes:
        lst.append(make())
        return lst[-1]
    return lst[int(rng.integers(len(lst)))]


def _q(d, step=0.05):
    return round(max(step, d) / step) * step


def _vq(v):
    return round(min(1.3, max(0.3, v)) * 4) / 4


# ------------------------------------------------------------------------------------------- instruments
def pluck(f0, dur, rng, decay=1.2, bright=0.6, pos=0.2, buzz=0.0, inharm=0.00025, bend=0.0, bend_at=0.18,
          partials=18, glide=0.12, vib=0.0):
    """Koto / shamisen / biwa: additive partials, faster decay up the series, pluck-position comb, attack click;
    sawari buzz = a band of upper partials that rings on; bend = an oshi-de press after bend_at s (semitones);
    glide = the string's pitch settling after the pluck (semitones); vib = late vibrato depth."""
    t = tvec(dur)
    n = len(t)
    fc = np.full(n, f0) * 2 ** (glide * np.exp(-t / 0.035) / 12.0)
    if bend:
        k0 = int(bend_at * SR)
        if k0 < n:
            ramp = np.clip((np.arange(n - k0)) / (0.09 * SR), 0, 1)
            fc[k0:] *= 2 ** (bend * (3 * ramp ** 2 - 2 * ramp ** 3) / 12.0)
    if vib:
        fc *= 1 + vib * smooth((t - 0.25) / 0.4) * np.sin(2 * np.pi * 5.4 * t + rng.uniform(0, 6))
    ph = phase(fc)
    out = np.zeros(n)
    for k in range(1, partials + 1):
        if k * f0 > SR / 2.4:
            break
        a = abs(np.sin(np.pi * k * pos)) / k ** (1.35 - 0.7 * bright)
        d = decay * (1 + 0.45 * (k - 1))
        if buzz and k >= 6:
            a *= 1 + 1.4 * buzz
            d = decay * (1.6 + 0.12 * k)
        out += a * np.exp(-d * t) * np.sin(k * ph * np.sqrt(1 + inharm * k * k) + rng.uniform(0, 6.28))
    click = rng.standard_normal(n) * np.exp(-t / 0.004) * 0.25 * (0.4 + bright)
    out = out * (1 - np.exp(-t / 0.0015)) + bandpass(click, 1500, 7000)
    return out * env(n, 0.0, min(0.08, dur * 0.3))


def koto(m, dur, rng, vel=1.0, decay=1.1, bend=0.0, bend_at=0.12, **kw):
    dur, b = _q(dur), _vq(vel)
    return cached(("koto", m, dur, b, decay, bend, bend_at), rng, lambda: pluck(
        hz(m), dur, rng, decay=decay, bright=0.4 + 0.15 * b, pos=0.22, bend=bend, bend_at=bend_at, glide=0.12) * 0.55)


def musicbox(m, dur, rng, vel=1.0, **kw):
    """A high koto with a glassy, fast-fading top: the lullaby colour of the Bride."""
    dur = _q(min(dur, 2.5))
    return cached(("mbox", m, dur), rng, lambda: (pluck(hz(m), dur, rng, decay=2.2, bright=0.95, pos=0.08,
                                                       partials=8, glide=0.0)
                                                 + 0.25 * bell(hz(m) * 2, dur, rng, ratios=(1.0, 2.76), beat=0.0)) * 0.4)


def bass_koto(m, dur, rng, vel=1.0, **kw):
    """Jushichigen, the 17-string bass koto: round, a little woody, warm under the field tracks."""
    dur = _q(dur)

    def make():
        t = tvec(dur)
        x = pluck(hz(m), dur, rng, decay=1.3, bright=0.35, pos=0.3, partials=10, glide=0.08)
        sub = np.sin(phase(np.full(len(t), hz(m)))) * np.exp(-t * 1.6) * (1 - np.exp(-t / 0.004))
        return lowpass(x + 0.3 * sub, 1600) * 0.45
    return cached(("bkoto", m, dur), rng, make)


def shamisen(m, dur, rng, vel=1.0, bend=0.0, bend_at=0.12, **kw):
    dur, b = _q(dur), _vq(vel)
    return cached(("sham", m, dur, b, bend, bend_at), rng, lambda: pluck(
        hz(m), dur, rng, decay=3.0, bright=0.75 + 0.15 * b, pos=0.1, buzz=0.35, bend=bend, bend_at=bend_at,
        glide=0.2) * 0.5)


def biwa(m, dur, rng, vel=1.0, bend=0.0, bend_at=0.18, decay=0.9, **kw):
    dur, b = _q(dur), _vq(vel)
    return cached(("biwa", m, dur, b, bend, bend_at, decay), rng, lambda: pluck(
        hz(m), dur, rng, decay=decay, bright=0.65 + 0.12 * b, pos=0.15, buzz=0.6, bend=bend, bend_at=bend_at,
        glide=0.25) * 0.6)


def bass(m, dur, rng, vel=1.0, **kw):
    """The battle band's bass: a plucked tone with a sine sub, cut above 1.6 kHz."""
    dur = _q(dur, 0.025)

    def make():
        t = tvec(dur)
        x = pluck(hz(m), dur, rng, decay=2.0, bright=0.45, pos=0.25, partials=10, glide=0.05)
        sub = np.sin(phase(np.full(len(t), hz(m)))) * np.exp(-t * 1.5) * (1 - np.exp(-t / 0.003))
        x = highpass(lowpass(x + 0.6 * sub, 1600), 38)
        return x * env(len(t), 0.002, min(0.05, dur * 0.3)) * 0.6
    return cached(("bass", m, dur), rng, make)


def guitar(m, dur, rng, drive=3.0, chord=(0, 7, 12), mute=False, vel=1.0, **kw):
    """A power chord (root, fifth, octave) through a soft clipper and a speaker-cabinet filter: light rock, not
    metal. mute = palm-muted (short, dark)."""
    dur = _q(dur, 0.025)

    def make():
        x = sum(pluck(hz(m + c), dur, rng, decay=9.0 if mute else 1.4, bright=0.85, pos=0.12, partials=14,
                      inharm=0.0001, glide=0.06) for c in chord)
        x = np.tanh(drive * x) / np.tanh(drive)
        x = highpass(lowpass(x, 1700 if mute else 3800), 110 if mute else 130)
        return x * env(len(x), 0.001, min(0.04, dur * 0.3)) * 0.5
    return cached(("gtr", m, dur, drive, chord, mute), rng, make)


def lead(m, dur, rng, vel=1.0, bend=0.0, bend_at=0.15, **kw):
    """A singing overdriven lead guitar (single notes, vibrato, bends) for the big fights."""
    dur, b = _q(dur), _vq(vel)

    def make():
        x = pluck(hz(m), dur, rng, decay=0.35, bright=0.95, pos=0.13, partials=20, bend=bend, bend_at=bend_at,
                  glide=0.05, vib=0.006)
        x = np.tanh(5.0 * x) / np.tanh(5.0)
        return highpass(lowpass(x, 3600), 220) * env(len(x), 0.004, min(0.1, dur * 0.3)) * 0.34
    return cached(("lead", m, dur, b, bend, bend_at), rng, make)


# ---- winds: a whole legato phrase is one breath, so the pitch glides between notes instead of restarting
WINDS = {
    "shakuhachi": dict(h=(1, .28, .12, .05, .02), breath=.10, nb=(1.0, 3.5), scoop=-.7, enbai=0.0, vib=.010,
                       vrate=5.0, att=.09, glide=.05, gain=.42),
    "shinobue": dict(h=(1, .45, .25, .12, .06, .03), breath=.05, nb=(1.5, 5.0), scoop=-.35, enbai=0.0, vib=.007,
                     vrate=5.6, att=.05, glide=.03, gain=.34),
    "hichiriki": dict(saw=True, form=((620, 1.0), (1400, .7), (2700, .35)), breath=.03, nb=(1.0, 3.0), scoop=-1.0,
                      enbai=-1.5, vib=.006, vrate=4.2, att=.05, glide=.08, gain=.30),
    "horagai": dict(saw=True, form=((380, 1.0), (950, .6), (1900, .25)), breath=.09, nb=(1.0, 4.0), scoop=-3.0,
                    enbai=0.0, vib=.004, vrate=3.0, att=.25, glide=.15, gain=.40, fall=-4.0),
}

_TAB = {}


def osc_saw(f, rng):
    """A band-limited sawtooth read from a wavetable (fast enough for choirs and string sections)."""
    nh = int(max(1, min(48, SR / 2.3 / max(float(np.max(f)), 20.0))))
    if nh not in _TAB:
        ph = np.arange(2048) / 2048 * 2 * np.pi
        _TAB[nh] = sum(np.sin(k * ph) / k for k in range(1, nh + 1)) * 0.6
    tab = _TAB[nh]
    p = (rng.uniform() + np.cumsum(f) / SR) % 1.0 * 2048
    i = p.astype(int)
    fr = p - i
    return tab[i] * (1 - fr) + tab[(i + 1) % 2048] * fr


def formant(x, forms):
    return sum(g * bandpass(x, F / 1.25, F * 1.25) for F, g in forms)


def wind(kind, notes, rng):
    """notes: [(start s, length s, midi, vel, ornaments)] of one breath, starts relative to the first. A pitch curve
    that glides note to note (meri scoop at the start and on '~', the hichiriki's enbai slide on every note), finger
    'cuts' between notes, a breath burst (muraiki) on each attack, vibrato that grows late in long notes."""
    c = WINDS[kind]
    T = notes[-1][0] + notes[-1][1] + 0.25
    n = int(T * SR)
    t = np.arange(n) / SR
    mid = np.zeros(n)
    amp = np.ones(n)
    benv = np.full(n, 0.6)
    for i, (s, d, m, v, orn) in enumerate(notes):
        a = int(s * SR)
        mid[a:] = m
        tt = t[a:] - s
        if i:
            prev = notes[i - 1][2]
            g = min(int(c["glide"] * SR), n - a)
            mid[a:a + g] = prev + (m - prev) * smooth(np.arange(g) / max(1, g))
            amp[a:] *= 1 - 0.4 * np.exp(-(tt / 0.025) ** 2)
        if i == 0 or "~" in orn:
            mid[a:] += c["scoop"] * (2.0 if "~" in orn and kind != "horagai" else 1.0) * np.exp(-tt / 0.07)
        if c["enbai"]:
            mid[a:] += c["enbai"] * np.exp(-tt / 0.1)
        if d > 0.7:                                                             # late vibrato on held notes
            depth = c["vib"] * smooth((tt - 0.4 * d) / (0.5 * d + 1e-6)) * (tt < d + 0.1)
            mid[a:] += 12 * np.log2(1 + depth * np.sin(2 * np.pi * c["vrate"] * tt + rng.uniform(0, 6)))
        seg = slice(a, min(n, int((s + d) * SR) + 1))
        amp[seg] *= v
        if d > 1.0:                                                             # a long note swells a little
            amp[seg] *= 0.86 + 0.14 * smooth((t[seg] - s) / (0.6 * d))
        benv[a:] += (2.4 if ">" in orn else 1.2) * np.exp(-tt / 0.06)
    if c.get("fall"):
        k = max(0, n - int(0.45 * SR))
        mid[k:] += c["fall"] * smooth(np.arange(n - k) / max(1, n - k - int(0.25 * SR)))
    amp = lowpass(amp, 60)
    f = hz(mid)
    if c.get("saw"):
        raw = osc_saw(f, rng)
        tone = formant(raw, c["form"]) + 0.15 * raw
    else:
        ph = phase(f)
        tone = sum(h * np.sin((k + 1) * ph) for k, h in enumerate(c["h"]))
    f0 = float(np.median(f))
    nz = norm(bandpass(noise(n, rng), f0 * c["nb"][0], f0 * c["nb"][1]))
    sig = tone * amp + c["breath"] * nz * benv * np.sqrt(np.maximum(amp, 0))
    return sig * env(n, c["att"], 0.2) * c["gain"]


def flute(m, dur, rng, kind="shakuhachi", **kw):
    return wind(kind, [(0.0, dur, m, 1.0, "")], rng)


def hichiriki(m, dur, rng, **kw):
    return wind("hichiriki", [(0.0, dur, m, 1.0, "")], rng)


VOWELS = {"a": ((800, 1.0), (1150, .5), (2900, .22)), "o": ((450, 1.0), (800, .45), (2830, .1)),
          "u": ((325, 1.0), (700, .3), (2530, .06))}


def pad(ms, dur, rng, kind="strings", vowel="a", att=0.35, rel=0.8, voices=3, vib=0.004):
    """A string section or a choir: detuned sawtooth ensembles with vibrato; the choir is formant-filtered."""
    t = tvec(dur)
    n = len(t)
    out = np.zeros(n)
    for m in ms:
        for v in range(voices):
            f = float(hz(m)) * 2 ** (rng.uniform(-9, 9) / 1200)
            fc = f * (1 + vib * np.sin(2 * np.pi * rng.uniform(4.2, 5.6) * t + rng.uniform(0, 6)))
            out += osc_saw(fc, rng)
    out /= max(1, len(ms) * voices) ** 0.5
    if kind == "choir":
        out = formant(out, VOWELS[vowel]) + 0.04 * bandpass(noise(n, rng), 2000, 7000) * (np.abs(out).mean() + 0.1)
        out = highpass(out, 120) * 1.4
    else:
        out = highpass(lowpass(out, 2600), 110)
    return out * env(n, min(att, dur * 0.4), min(rel, dur * 0.4)) * 0.3


def sho(ms, dur, rng):
    """Aitake: a cluster of soft reed tones, a long swell in and out."""
    t = tvec(dur)
    n = len(t)
    out = np.zeros(n)
    for m in ms:
        f = float(hz(m)) * (1 + rng.uniform(-0.0012, 0.0012))
        ph = 2 * np.pi * f * t + rng.uniform(0, 6)
        out += np.sin(ph) + 0.33 * np.sin(3 * ph) + 0.15 * np.sin(5 * ph) + 0.08 * np.sin(2 * ph)
    return out / len(ms) * env(n, min(1.2, dur * 0.35), min(1.2, dur * 0.35)) * 0.3


def bell(f0, dur, rng, ratios=(1.0, 2.41, 3.92, 5.33, 6.8), beat=1.2):
    """Kane / rin: inharmonic partials, the low ones ring long, a slow beat from a doubled fundamental."""
    t = tvec(dur)
    out = np.zeros(len(t))
    for i, r in enumerate(ratios):
        if f0 * r < SR / 2.3:
            out += np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * np.exp(-t * (0.7 + 1.6 * i)) / (1 + i)
    out += 0.5 * np.sin(2 * np.pi * (f0 + beat) * t) * np.exp(-0.7 * t)
    return out * (1 - np.exp(-t / 0.002)) * 0.35


def bonsho(f0, rng, dur=9.0):
    """The great temple bell (joya no kane): a hum tone under the strike, long beating partials."""
    t = tvec(dur)
    out = np.zeros(len(t))
    for r, a, d in ((0.5, .8, .25), (1.0, 1.0, .35), (1.19, .5, .6), (2.0, .45, .8), (2.52, .3, 1.2),
                    (3.0, .2, 1.6), (4.1, .12, 2.4)):
        out += a * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * np.exp(-t * d) \
            * (1 + 0.25 * np.sin(2 * np.pi * (0.6 + r * 0.2) * t))
    hit = lowpass(noise(len(t), rng), 900) * np.exp(-t / 0.03)
    return (out + 0.4 * norm(hit)) * (1 - np.exp(-t / 0.004)) * 0.3


def drum(kind, rng):
    def make():
        if kind == "hyoshigi":                                                  # kabuki wooden clappers
            t = tvec(0.18)
            body = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in
                       ((2150, 1.0, 55), (3240, .6, 70), (5100, .3, 90)))
            clk = bandpass(noise(len(t), rng), 2000, 9000) * np.exp(-t / 0.002)
            return (body + 0.8 * norm(clk)) * 0.32
        if kind == "atarigane":                                                 # the festival hand gong
            t = tvec(0.5)
            body = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * d) for f, a, d in
                       ((1820, 1.0, 9), (2950, .7, 12), (4410, .5, 16), (6100, .3, 20)))
            return (body + 0.4 * norm(bandpass(noise(len(t), rng), 3000, 9000)) * np.exp(-t / 0.01)) * 0.16
        if kind == "chappa":                                                    # small hand cymbals
            t = tvec(0.9)
            x = norm(bandpass(noise(len(t), rng), 3500, 11000)) * np.exp(-t * 5)
            return (x + 0.3 * np.sin(2 * np.pi * 3900 * t) * np.exp(-t * 4)) * 0.16
        if kind == "odaiko":
            dur, f1, f2, dec, nlp, ng = 1.6, 88, 46, 2.6, 380, 0.45
        elif kind == "odaiko_rim":
            dur, f1, f2, dec, nlp, ng = 0.25, 600, 500, 25, 5000, 0.6
        elif kind == "shime":
            dur, f1, f2, dec, nlp, ng = 0.3, 340, 260, 14, 4500, 0.4
        else:                                                                   # kakko: a dry, high tap
            dur, f1, f2, dec, nlp, ng = 0.12, 900, 700, 40, 9000, 0.7
        t = tvec(dur)
        n = len(t)
        fc = f2 + (f1 - f2) * np.exp(-t / 0.05)
        body = np.sin(phase(fc)) * np.exp(-dec * t)
        if kind == "odaiko":
            body += 0.35 * np.sin(phase(fc * 1.52)) * np.exp(-dec * 2.0 * t)
            body += 0.2 * np.sin(phase(fc * 2.3)) * np.exp(-dec * 3.0 * t)
        hit = norm(lowpass(noise(n, rng), nlp)) * np.exp(-t / 0.02)
        return (body + ng * hit) * {"odaiko": 0.9, "odaiko_rim": 0.35, "shime": 0.45, "kakko": 0.3}[kind]
    return cached(("drum", kind), rng, make, takes=4)


# ---- the battle band (user: "for battle music how about something light rock with biwa mixed in")
def kit(kind, rng):
    def make():
        if kind == "kick":
            t = tvec(0.4)
            body = np.sin(phase(48 + 110 * np.exp(-t / 0.03))) * np.exp(-t * 9)
            click = norm(bandpass(noise(len(t), rng), 1500, 6000)) * np.exp(-t / 0.003)
            return (0.75 * body + 0.25 * click) * 0.85
        if kind == "snare":
            t = tvec(0.3)
            n = len(t)
            tone = (np.sin(phase(np.full(n, 185.0))) + 0.5 * np.sin(phase(np.full(n, 330.0)))) * np.exp(-t * 26)
            rattle = norm(bandpass(noise(n, rng), 1500, 8000))
            return (0.45 * tone + 0.8 * rattle * np.exp(-t * 15)) * 0.55
        if kind in ("hat", "ohat"):
            t = tvec(0.06 if kind == "hat" else 0.35)
            x = highpass(noise(len(t), rng), 7000)
            return norm(x) * np.exp(-t / (0.012 if kind == "hat" else 0.09)) * 0.2
        if kind == "rim":
            t = tvec(0.07)
            x = norm(bandpass(noise(len(t), rng), 1500, 4500)) * np.exp(-t / 0.005)
            return (x + 0.6 * np.sin(2 * np.pi * 620 * t) * np.exp(-t * 60)) * 0.3
        if kind == "ride":
            t = tvec(1.4)
            x = norm(bandpass(noise(len(t), rng), 4000, 10000)) * np.exp(-t * 5)
            pings = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (2930, 4310, 5170)) * np.exp(-t * 3)
            return (x + 0.25 * pings) * 0.13
        t = tvec(2.4)                                                           # crash
        x = norm(bandpass(noise(len(t), rng), 3000, 12000))
        return x * np.exp(-t * 1.7) * (1 - np.exp(-t / 0.003)) * 0.3
    return cached(("kit", kind), rng, make, takes=4)


def drip(rng):
    t = tvec(0.12)
    f = rng.uniform(1300, 2400) * (1 + 0.8 * np.exp(-t / 0.01))
    return np.sin(phase(f)) * np.exp(-t / 0.025) * 0.18


def waves(n, rng, gain=1.0, period=7.3):
    x = lowpass(rng.standard_normal(n), 600) + 0.15 * bandpass(rng.standard_normal(n), 1500, 5000)
    t = np.arange(n) / SR
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / period) ** 2
    x = norm(x) * swell
    return x * gain, np.roll(x, int(0.13 * SR)) * gain


def windnoise(n, rng, lo=250, hi=1800, period=11.0):
    t = np.arange(n) / SR
    x = norm(bandpass(rng.standard_normal(n), lo, hi))
    gust = 0.35 + 0.65 * smooth(0.5 + 0.5 * np.sin(2 * np.pi * t / period + rng.uniform(0, 6)))
    return x * gust


def insects(n, rng, rate=0.7):
    """Suzumushi: bell-crickets, short high trills scattered through the night."""
    out = np.zeros(n)
    for _ in range(int(n / SR * rate)):
        i = int(rng.uniform(0, n))
        t = tvec(rng.uniform(0.3, 0.9))
        f = rng.uniform(4200, 5200)
        x = np.sin(2 * np.pi * f * t) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * rng.uniform(28, 40) * t)))
        x *= env(len(t), 0.02, 0.1) * rng.uniform(0.3, 1.0)
        j = min(n, i + len(x))
        out[i:j] += x[:j - i]
    return out * 0.05


def thunder(rng, dur=5.0):
    t = tvec(dur)
    n = len(t)
    crack = norm(bandpass(noise(n, rng), 300, 4000)) * np.exp(-t / 0.08)
    rum = norm(lowpass(noise(n, rng), 160))
    bursts = sum(np.exp(-((t - rng.uniform(0.2, dur * 0.7)) / rng.uniform(0.2, 0.6)) ** 2) for _ in range(4))
    return (0.5 * crack + rum * (0.4 + bursts) * np.exp(-t * 0.6)) * env(n, 0.005, 1.0) * 0.5


def swell(dur, rng, lo=400, hi=6000):
    """A reversed-cymbal rise that lands on the next downbeat."""
    t = tvec(dur)
    x = norm(bandpass(noise(len(t), rng), lo, hi))
    return x * (t / dur) ** 3 * 0.25


# ------------------------------------------------------------------------------------------- the score
class Track:
    def __init__(self, bars, bpm, beats=4, rng=None, send=0.2, intro=0, loop=True):
        self.spb = 60.0 / bpm
        self.beats = beats
        self.bars = bars
        self.n = int(round(bars * beats * self.spb * SR))
        self.i0 = int(round(intro * beats * self.spb * SR))                    # the engine's looppoint
        self.loop = loop
        self.L, self.R = np.zeros(self.n), np.zeros(self.n)
        self.SL, self.SR_ = np.zeros(self.n), np.zeros(self.n)                 # the reverb send bus
        self.send = send
        self.rng = rng if rng is not None else np.random.default_rng(0)
        self.stems = {}
        self.sc, self.root = None, None             # the key (set by each track): the helpers keep notes inside it

    def at(self, bar, beat=0.0):
        return (bar * self.beats + beat) * self.spb

    def add(self, sig, t, pan=0.0, gain=1.0, send=None, jit=0.0, tag="misc"):
        """Mix sig in at t s. A loop wraps what runs past the end to the loop start (seamless); jit = timing
        humanisation (s, gaussian)."""
        nominal = int(round(t * SR))
        if jit:
            t += self.rng.normal(0, jit)
        i = int(round(t * SR))
        if self.loop and self.i0 and nominal >= self.i0 and i < self.i0:       # pushed early across the loop
            i = self.i0 + (i - self.i0) % (self.n - self.i0)                    # point: it belongs to the body
        if i < 0:
            i = 0 if (self.i0 or not self.loop) else i % self.n
        if i >= self.n:
            if not self.loop:
                return
            i = self.i0 + (i - self.n) % (self.n - self.i0)
        s = self.send if send is None else send
        lg, rg = gain * np.cos((pan + 1) * np.pi / 4), gain * np.sin((pan + 1) * np.pi / 4)
        self.stems[tag] = self.stems.get(tag, 0.0) + float(np.sum(sig ** 2)) * gain * gain
        pos = 0
        while pos < len(sig):
            take = min(len(sig) - pos, self.n - i)
            chunk = sig[pos:pos + take]
            self.L[i:i + take] += lg * chunk
            self.R[i:i + take] += rg * chunk
            if s:
                self.SL[i:i + take] += s * lg * chunk
                self.SR_[i:i + take] += s * rg * chunk
            pos += take
            if not self.loop:
                break
            i = self.i0

    def ambience(self, sig_l, sig_r, gain, send=0.0):
        self.L += gain * sig_l[:self.n]
        self.R += gain * sig_r[:self.n]
        self.stems["amb"] = self.stems.get("amb", 0.0) + float(np.sum(sig_l[:self.n] ** 2)) * gain * gain * 2
        if send:
            self.SL += send * gain * sig_l[:self.n]
            self.SR_ += send * gain * sig_r[:self.n]

    def fold(self, y):
        """A signal longer than the track: what runs past the end lands in the loop region."""
        out = y[:self.n].copy()
        over = y[self.n:]
        if not self.loop or not len(over):
            return out
        p = self.n - self.i0
        for k in range(0, len(over), p):
            seg = over[k:k + p]
            out[self.i0:self.i0 + len(seg)] += seg
        return out


def reverb(tr, rt60=2.0, wet=1.0, bright=4000, lowcut=180, seed=7):
    """The send bus through a decaying-noise hall (early taps + tail), high-passed first so the bass and the
    kick stay dry and the low end clean. Linear FFT convolution, folded into the loop so the tail wraps."""
    rng = np.random.default_rng(seed)
    ln = int(rt60 * 1.3 * SR)
    t = np.arange(ln) / SR
    for ch in (0, 1):
        bus = highpass(tr.SL if ch == 0 else tr.SR_, lowcut)
        ir = lowpass(rng.standard_normal(ln), bright) * np.exp(-6.9 * t / rt60)
        pre = int(0.02 * SR)
        ir = np.concatenate([np.zeros(pre), ir[:ln - pre]])
        for _ in range(6):
            k = int(rng.uniform(0.007, 0.045) * SR)
            ir[k] += rng.uniform(0.2, 0.5) * rng.choice([-1, 1]) * np.sqrt(np.sum(ir ** 2) / ln) * 40
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        nfft = 1 << int(np.ceil(np.log2(tr.n + ln)))
        y = np.fft.irfft(np.fft.rfft(bus, nfft) * np.fft.rfft(ir, nfft), nfft)[:tr.n + ln]
        y = tr.fold(y)
        if ch == 0:
            tr.L = tr.L + wet * 2.0 * y
        else:
            tr.R = tr.R + wet * 2.0 * y


# ---- mastering: a K-weighted loudness target, a look-ahead peak limiter
def kweight(x):
    X = np.fft.rfft(x)
    f = _freqs(len(x))
    hp = (f / 38.0) ** 2 / (1 + (f / 38.0) ** 2)
    shelf = 1 + 0.58 * (f ** 2 / (f ** 2 + 1500.0 ** 2))
    return np.fft.irfft(X * hp * shelf, len(x))


def loudness(x):
    """Integrated loudness (BS.1770-style gating on 400 ms blocks), in LUFS (approximate K-weighting)."""
    k = np.stack([kweight(c) for c in x])
    p = np.sum(k ** 2, axis=0)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    c = np.concatenate([[0], np.cumsum(p)])
    idx = np.arange(0, max(1, len(p) - blk), hop)
    ms = (c[np.minimum(idx + blk, len(p))] - c[idx]) / blk
    lv = -0.691 + 10 * np.log10(ms + 1e-12)
    g = ms[lv > -70]
    if not len(g):
        return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = ms[(lv > -70) & (lv > rel)]
    return float(-0.691 + 10 * np.log10(g2.mean() + 1e-12))


def limit(x, ceil=0.89, rel=0.08, blk=64, loop=True):
    """A look-ahead brickwall: block peaks, instant attack one block early, exponential release. For a loop the
    gain is computed with the end prepended, so the limiter state is the same on both sides of the seam."""
    pre = int(SR * 0.5) if loop else 0
    xx = np.concatenate([x[:, -pre:], x], axis=1) if pre else x
    a = np.abs(xx).max(axis=0)
    nb = (len(a) + blk - 1) // blk
    pad_ = np.zeros(nb * blk)
    pad_[:len(a)] = a
    pk = pad_.reshape(nb, blk).max(axis=1)
    pk = np.maximum(pk, np.concatenate([pk[1:], [0]]))
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    k = 1 - np.exp(-blk / (rel * SR))
    gs = np.empty(nb)
    cur = 1.0
    for i in range(nb):
        cur = min(g[i], cur + (1 - cur) * k)
        gs[i] = cur
    gi = np.interp(np.arange(len(a)), np.arange(nb) * blk + blk / 2, gs)
    y = (xx * gi)[:, pre:]
    return np.clip(y, -0.995, 0.995)


def master(tr, target=-14.0):
    """tr: a Track (or a (2, n) array). DC and sub-28 Hz out, gain to the loudness target, the limiter; twice, so
    the limiting's loudness loss is made up."""
    x = tr if isinstance(tr, np.ndarray) else np.stack([tr.L, tr.R])
    loop = True if isinstance(tr, np.ndarray) else tr.loop
    i0 = 0 if isinstance(tr, np.ndarray) else tr.i0
    x = x - x.mean(axis=1, keepdims=True)
    x = np.stack([highpass(c, 28) for c in x])
    g = 10 ** ((target - loudness(x)) / 20)
    for _ in range(3):
        if i0:                                  # the intro limited as it plays, the body as the loop it is
            y = np.concatenate([limit(x * g, loop=False)[:, :i0], limit(x[:, i0:] * g, loop=True)], axis=1)
        else:
            y = limit(x * g, loop=loop)
        err = target - loudness(y)
        if abs(err) < 0.15:
            break
        g *= 10 ** (err / 20)
    return y


# ------------------------------------------------------------------------------------------- composition helpers
def M(s, bars=None, beats=4):
    """A melody string: 'degree:beats' tokens ('3:1.5'; no ':' = 1 beat), 'r:2' a rest (ma), '|' bar lines (for
    reading only). Suffixes: '#'/'b' chromatic, '~' slide/press into the note, '^' grace from above, '>' accent,
    'z' tremolo (plucked). Returns [(beat, length, degree, accidental, ornaments)]."""
    out, t = [], 0.0
    for tok in s.replace("|", " ").split():
        d, _, ln = tok.partition(":")
        ln = float(ln) if ln else 1.0
        orn = ""
        while d and d[-1] in "~^>z":
            orn += d[-1]
            d = d[:-1]
        acc = 0
        while d and d[-1] in "#b" and d not in ("b",):
            acc += 1 if d[-1] == "#" else -1
            d = d[:-1]
        if d == "r":
            t += ln
            continue
        out.append((t, ln, int(d), acc, orn))
        t += ln
    if bars is not None and abs(t - bars * beats) > 1e-6:
        raise ValueError("melody is %.2f beats, expected %d: %s" % (t, bars * beats, s[:40]))
    return out


def shift(mel, k):
    return [(t, ln, d + k, a, o) for t, ln, d, a, o in mel]


def cut(mel, b0, b1, beats=4):
    """The notes from bar b0 to b1, moved to start at 0."""
    return [(t - b0 * beats, ln, d, a, o) for t, ln, d, a, o in mel if b0 * beats - 1e-6 <= t < b1 * beats - 1e-6]


def RING(inst):
    return {koto: 1.6, musicbox: 1.2, bass_koto: 1.0, shamisen: 0.7, biwa: 1.3, bass: 0.05, lead: 0.5}.get(inst, 0.3)


def play(tr, mel, inst, bar0, sc, root, pan=0.0, gain=1.0, send=None, legato=1.0, ring=None, jit=0.006, vel=0.9,
         tag="lead", **kw):
    """Plucked notes, humanised: downbeats a little louder, off-beats softer, a random spread; '~' plucks the
    scale step below and presses up into the note, '^' adds a grace note from above, 'z' a tremolo."""
    rng = tr.rng
    for t, ln, d, acc, orn in mel:
        m = deg(sc, root, d) + acc
        bp = t % tr.beats
        v = vel * (1.1 if bp < 1e-6 else 1.0 if abs(t - round(t)) < 1e-6 else 0.9)
        v *= (1.2 if ">" in orn else 1.0) * float(np.exp(rng.normal(0, 0.06)))
        dur = ln * tr.spb * legato + (RING(inst) if ring is None else ring)
        start = tr.at(bar0) + t * tr.spb
        if "^" in orn:
            mg = deg(sc, root, d + 1) + acc
            tr.add(inst(mg, 0.35, rng, vel=v * 0.8, **kw), start - 0.07, pan, gain * v * 0.55, send, jit, tag)
        if "z" in orn:
            step = tr.spb / 4 if tr.spb > 0.3 else tr.spb / 2
            k = max(1, int(round(ln * tr.spb / step)))
            for j in range(k):
                vv = v * (0.75 + 0.25 * (j % 2 == 0)) * (1 + 0.25 * j / k)
                tr.add(inst(m, step * 1.5, rng, vel=vv, **kw), start + j * step, pan, gain * vv * 0.8, send, 0.003,
                       tag)
            continue
        if "~" in orn and inst in (koto, shamisen, biwa, lead):
            ml = deg(sc, root, d - 1) + acc
            sig = inst(ml, dur, rng, vel=v, bend=m - ml, bend_at=min(0.12, ln * tr.spb * 0.4), **kw)
        else:
            sig = inst(m, dur, rng, vel=v, **kw)
        tr.add(sig, start, pan, gain * v, send, jit, tag)


def blow(tr, mel, kind, bar0, sc, root, pan=0.0, gain=1.0, send=None, vel=0.9, gap=0.05, jit=0.01, tag="lead",
         semis=0):
    """A wind line: notes closer than gap beats share one breath (legato); a rest starts a new breath."""
    groups, cur = [], []
    for nt in mel:
        if cur and nt[0] - (cur[-1][0] + cur[-1][1]) > gap:
            groups.append(cur)
            cur = []
        cur.append(nt)
    if cur:
        groups.append(cur)
    for g in groups:
        t0 = g[0][0]
        notes = []
        for t, ln, d, acc, orn in g:
            bp = t % tr.beats
            v = vel * (1.06 if bp < 1e-6 else 1.0) * (1.15 if ">" in orn else 1.0) \
                * float(np.exp(tr.rng.normal(0, 0.05)))
            notes.append(((t - t0) * tr.spb, ln * tr.spb, deg(sc, root, d) + acc + semis, min(1.2, v), orn))
        tr.add(wind(kind, notes, tr.rng), tr.at(bar0) + t0 * tr.spb, pan, gain, send, jit, tag)


def stack(sc, root, d, steps=(0, 2, 3, 5)):
    """A quartal / sus chord built from scale steps above degree d (stays inside the pentatonic scale)."""
    return [deg(sc, root, d + s) for s in steps]


def chord_pad(tr, b, ms, bars=1, kind="strings", vowel="a", pan=0.0, gain=1.0, send=0.35, att=0.35, tag="pad"):
    ms = sorted(set(snap(tr, m) for m in ms))
    tr.add(pad(ms, bars * tr.beats * tr.spb + 0.6, tr.rng, kind=kind, vowel=vowel, att=att), tr.at(b), pan, gain,
           send, 0.0, tag)


def kit_bar(tr, b, style="drive", gain=1.0, fill=None, crash=False):
    """One bar of the rock kit. Styles: drive (kick 1, 2&, 3, 4&; snare 2, 4), half (snare on 3), double (kick 8ths
    + ride), gallop, shuffle (triplet hats), light (rim + quarter hats), waltz (3/4). Fills on the last two beats:
    taiko (shime, rim, o-daiko), snare (a 16th roll), roll (a whole-bar snare crescendo)."""
    rng, B = tr.rng, tr.beats

    def hit(kind, beat, g, pan=0.0, drumkind=False):
        sig = drum(kind, rng) if drumkind else kit(kind, rng)
        tr.add(sig, tr.at(b, beat), pan, gain * g * float(np.exp(rng.normal(0, 0.06))), 0.06, 0.003, "drums")
    fz = B - 2 if fill in ("taiko", "snare") else (0 if fill == "roll" else B)
    if crash:
        hit("crash", 0, 0.9, 0.35)
    if style in ("drive", "half", "light", "double", "gallop"):
        if style == "double":
            for i in range(B):
                hit("ride", i, 0.8, 0.3)
        elif style == "light":
            for i in range(B):
                hit("hat", i, 0.8, 0.3)
        else:
            for i in range(B * 2):
                hit("hat", i * 0.5, 0.9 if i % 2 == 0 else 0.55, 0.3)
        kicks = {"drive": (0, 1.5, 2, 3.5), "half": (0, 2.5), "light": (0, 2.5), "double": [i * 0.5 for i in
                 range(B * 2)], "gallop": [k + o for k in range(B) for o in (0, 0.5, 0.75)]}[style]
        snares = {"half": (2,), "light": ()}.get(style, (1, 3))
        for k in kicks:
            if k < fz:
                hit("kick", k, 1.0 if k == 0 else 0.85)
        for s in snares:
            if s < fz:
                hit("snare", s, 1.0, -0.05)
        if style == "light":
            for s in (1, 3):
                if s < fz:
                    hit("rim", s, 0.9, -0.1)
    elif style == "shuffle":
        for i in range(B * 3):
            hit("hat", i / 3, 0.9 if i % 3 == 0 else 0.45 if i % 3 == 1 else 0.65, 0.3)
        for k in (0, 2, 2 + 2 / 3):
            if k < fz:
                hit("kick", k, 1.0)
        for s in (1, 3):
            if s < fz:
                hit("snare", s, 1.0, -0.05)
    elif style == "blast":
        for i in range(B * 2):
            if i * 0.5 < fz:
                hit("kick", i * 0.5, 0.8)
                if i % 2:
                    hit("snare", i * 0.5, 0.7, -0.05)
        for i in range(B):
            hit("ride", i, 0.8, 0.3)
    elif style == "waltz":
        hit("kick", 0, 1.0)
        for s in range(1, B):
            hit("rim", s, 0.8, -0.1)
            hit("hat", s, 0.6, 0.3)
    if fill == "taiko":
        for i, kind in enumerate(("shime", "shime", "odaiko_rim", "odaiko")):
            hit(kind, B - 2 + i * 0.5, 0.95, -0.3 + 0.2 * i, True)
    elif fill == "snare":
        for i in range(8):
            hit("snare", B - 2 + i * 0.25, 0.45 + 0.07 * i, -0.05)
    elif fill == "roll":
        for i in range(B * 4):
            hit("snare", i * 0.25, 0.25 + 0.75 * i / (B * 4), -0.05)


def taiko_bar(tr, b, pattern, gain=1.0, pan_spread=0.25):
    """pattern: [(beat, kind, gain)]: the taiko ensemble (o-daiko, shime, kakko, rim, hyoshigi, atarigane)."""
    for beat, kind, g in pattern:
        tr.add(drum(kind, tr.rng), tr.at(b, beat), tr.rng.uniform(-pan_spread, pan_spread),
               gain * g * float(np.exp(tr.rng.normal(0, 0.07))), 0.15 if kind == "odaiko" else 0.1, 0.004, "taiko")


def bass_bar(tr, b, r, style="8ths", gain=0.75, nxt=None, fifth=None):
    rng = tr.rng
    B = tr.beats

    f5 = fifth if fifth is not None else globals()["fifth"](tr, r)

    def note(m, beat, ln, g=1.0):
        m = snap(tr, m)
        tr.add(bass(m, ln * tr.spb, rng), tr.at(b, beat), 0.0, gain * g * float(np.exp(rng.normal(0, 0.05))), 0.0,
               0.003, "bass")
    if style == "8ths":
        for i in range(B * 2):
            m = r
            if nxt is not None and i == B * 2 - 1 and nxt != r:
                m = r + (2 if nxt > r else -2) if abs(nxt - r) > 2 else r
            note(m, i * 0.5, 0.45, 1.0 if i % 2 == 0 else 0.85)
    elif style == "push":
        for beat in (0, 1.5, 2, 3.5):
            note(r, beat, 0.9 if beat in (0, 2) else 0.45)
    elif style == "gallop":
        for k in range(B):
            for o, ln in ((0, 0.45), (0.5, 0.22), (0.75, 0.22)):
                note(r, k + o, ln, 1.0 if o == 0 else 0.8)
    elif style == "whole":
        note(r, 0, B * 0.98)
    elif style == "half":
        note(r, 0, B / 2 - 0.05)
        note(r, B / 2, B / 2 - 0.05, 0.9)
    elif style == "waltz":
        note(r, 0, 1.4)
        note(r + f5, 2, 0.9, 0.8)
    elif style == "7/8":
        for beat, ln in ((0, 1.8), (2, 1.8), (4, 0.9), (5, 0.9), (6, 0.9)):
            note(r, beat, ln, 1.0 if beat in (0, 2, 4) else 0.8)
    elif style == "shuffle":
        for k in range(B):
            note(r, k, 0.6)
            note(r + (12 if k % 2 else f5), k + 2 / 3, 0.3, 0.75)


def gtr_bar(tr, b, r, style="chug", gain=0.5, drive=2.5, chord=(0, 7, 12), beats=None):
    """Two takes of the rhythm guitar, hard left and right. Styles: chug (8ths, palm-muted, open on 1, 2&, 4),
    open (one ringing chord), half (two), stab (the given beats), gallop (muted 16th gallop), 7/8."""
    rng = tr.rng
    B = tr.beats
    r = snap(tr, r)
    if tuple(chord) == (0, 7, 12):
        chord = (0, fifth(tr, r), 12)
    for pan in (-0.65, 0.65):
        def g(beat, ln, mute, gg=1.0):
            tr.add(guitar(r, ln * tr.spb, rng, drive=drive, mute=mute, chord=chord), tr.at(b, beat), pan,
                   gain * gg * float(np.exp(rng.normal(0, 0.05))), 0.05, 0.005, "gtr")
        if style == "chug":
            for i in range(B * 2):
                accent = i in (0, 3, 6)
                g(i * 0.5, 1.4 if accent else 0.3, not accent, 1.1 if accent else 0.75)
        elif style == "open":
            g(0, B, False)
        elif style == "half":
            g(0, B / 2, False)
            g(B / 2, B / 2, False, 0.9)
        elif style == "stab":
            for beat in beats:
                g(beat, 0.6, False)
        elif style == "gallop":
            for k in range(B):
                for o in (0, 0.5, 0.75):
                    g(k + o, 0.25, True, 1.0 if o == 0 else 0.8)
        elif style == "7/8":
            for beat in (0, 2, 4):
                g(beat, 1.6, False)
            for beat in (1, 3, 5, 6):
                g(beat, 0.5, True, 0.7)
        elif style == "shuffle":
            for k in range(B):
                g(k, 0.6, True, 1.0)
                g(k + 2 / 3, 0.3, True, 0.7)


def riff(tr, b, r, shape, inst=biwa, pan=-0.15, gain=1.0, octave=12, tag="riff"):
    """A one-bar riff as [(beat, semitones above the chord root, bend)] (parallel over the chord changes)."""
    for beat, semi, bnd in shape:
        m = key_step(tr, r + octave, semi)
        tr.add(inst(m - bnd, 0.9 if inst is biwa else 0.6, tr.rng, vel=1.0, bend=bnd, bend_at=0.08) if bnd else
               inst(m, 0.9, tr.rng, vel=1.0), tr.at(b, beat), pan, gain * float(np.exp(tr.rng.normal(0, 0.06))),
               None, 0.004, tag)


def arp(tr, b, ms, pattern, inst=koto, step=0.5, pan=-0.3, gain=0.35, ring=1.2, beat0=0.0, tag="arp"):
    """A broken chord: pattern indexes ms, one note per step beats."""
    ms = [snap(tr, m) for m in ms]
    for i, k in enumerate(pattern):
        if k is None:
            continue
        v = 1.0 if i % 2 == 0 else 0.85
        tr.add(inst(ms[k % len(ms)] + 12 * (k // len(ms)), step * tr.spb + ring, tr.rng, vel=v),
               tr.at(b, beat0 + i * step), pan, gain * v * float(np.exp(tr.rng.normal(0, 0.06))), None, 0.006, tag)


# ------------------------------------------------------------------------------------------- the leitmotifs
# The travelers' theme (D ryo, D E F# A B): 8 bars, antecedent (ends open, on E) and consequent (ends home, high D).
TRAV_A = "0:1 3:1 4:1.5 3:.5 | 5:2 4:1 3:1 | 2:1 3:.5 4:.5 3:1 2:1 | 1:3 r:1 | " \
         "0:1 3:1 4:1.5 3:.5 | 5:2 6:1 7:1 | 6:1 5:.5 4:.5 3:1 4:1 | 5:3 r:1"
TRAV_H = [0, 3, 2, 1, 0, 2, 3, 0]          # its harmony, as ryo degrees of the chord roots: D G Bm A | D Bm G D
TRAV_HR = [62, 67, 59, 69, 62, 59, 67, 62]  # the chord roots (MIDI), with the triads below
TRIADS = {62: (62, 66, 69), 67: (67, 71, 74), 59: (59, 62, 66), 69: (69, 73, 76), 64: (64, 67, 71),
          66: (66, 69, 73)}
TRAV_B = "4:2 3:1 2:1 | 3:1.5 2:.5 1:2 | 2:1 3:1 4:1 5:1 | 4:4 | 4:2 5:1 6:1 | 7:1.5 6:.5 5:2 | " \
         "6:1 5:1 4:1 3:1 | 3:2 r:2"
TRAV_BR = [67, 62, 67, 64, 67, 62, 64, 69]  # G D G Em | G D Em A
# Doji Nashiko (D in, D Eb G A Bb): the Bride's sigh, Eb falling to D, at both ends of the phrase.
NASHIKO = "5:1.5 6:.5 5:1 4:1 | 3:3 r:1 | 4:1 3:.5 2:.5 1:1 0:1 | 1:2 0:2"
NASHIKO2 = "5:1.5 6:.5 7:1 8:1 | 9:3 r:1 | 8:1 7:.5 6:.5 5:1 4:1 | 3:4"


# ------------------------------------------------------------------------------------------- the tracks
def t_town(rng):
    """Towns and villages (D yo, 100 BPM, 32 bars): A (koto) - A' (shinobue, koto counter) - B (shamisen, the
    festival bell) - A'' (all, drums). Jushichigen bass, koto broken chords, shime and kakko."""
    tr = Track(32, 100, rng=rng, send=0.16)
    sc, root = YO, 62
    tr.sc, tr.root = sc, root
    A = M("3:1 4:.5 3:.5 2:1 3:1 | 5:1.5 4:.5 3:2 | 2:1 3:.5 2:.5 1:1 0:1 | 1:3 r:1 | "
          "3:1 4:.5 3:.5 2:1 3:1 | 5:1.5 6:.5 5:2 | 4:1 3:.5 2:.5 1:1 2:.5 1:.5 | 0:3 r:1", 8)
    A2 = M("3:1 4^:.5 3:.5 2:1 3~:1 | 5:1.5 4:.5 3:1 2:.5 3:.5 | 2:1 3:.5 2:.5 1:1 0:1 | 1:2 2:1 1:1 | "
           "3:1 4^:.5 3:.5 2:1 3~:1 | 5:1.5 6:.5 5:1 7:1 | 6:.5 5:.5 4:1 3:.5 2:.5 1:.5 2:.5 | 0:3 r:1", 8)
    Bm = M("5:1.5 6:.5 7:1 6:1 | 5:1 4:1 3:2 | 4:1.5 5:.5 4:1 3:1 | 2:2 1:2 | "
           "5:1.5 6:.5 7:1 6:1 | 5:1 6:.5 5:.5 4:1 3:1 | 2:1 3:1 1:1 2:1 | 3:3 r:1", 8)
    CTR = M("0:4 | 2:2 1:2 | 0:2 -1:2 | 1:4 | 0:4 | 2:2 3:2 | 1:2 2:2 | 0:4", 8)          # long-note counterline
    HA, HB = [0, 2, 3, 1, 0, 4, 2, 0], [2, 3, 4, 1, 2, 0, 1, 3]
    plan = [(0, A, HA, 0), (8, A2, HA, 1), (16, Bm, HB, 2), (24, A, HA, 3)]
    for bar0, mel, H, sec in plan:
        if sec == 0:
            play(tr, mel, koto, bar0, sc, root + 12, pan=-0.15, gain=1.0)
        elif sec == 1:
            blow(tr, mel, "shinobue", bar0, sc, root + 12, pan=0.2, gain=0.85)
            play(tr, CTR, koto, bar0, sc, root + 12, pan=-0.3, gain=0.55, tag="ctr")
        elif sec == 2:
            play(tr, mel, shamisen, bar0, sc, root + 12, pan=0.25, gain=1.05)
            play(tr, shift(mel, -2), koto, bar0, sc, root + 12, pan=-0.35, gain=0.4, vel=0.8, tag="ctr")
        else:
            play(tr, A2, koto, bar0, sc, root + 12, pan=-0.2, gain=0.85)
            blow(tr, mel, "shinobue", bar0, sc, root + 12, pan=0.25, gain=0.6)
        for k in range(8):
            b = bar0 + k
            d = H[k]
            tr.add(bass_koto(deg(sc, root - 24, d), 2.2, rng), tr.at(b), 0.0, 0.8, 0.1, 0.004, "bass")
            if sec >= 2:
                tr.add(bass_koto(deg(sc, root - 24, d + 3), 1.0, rng), tr.at(b, 2.5), 0.0, 0.5, 0.1, 0.004, "bass")
            ch = stack(sc, root, d)
            if sec == 0:
                arp(tr, b, ch, [0, 2, 1, 3], step=1.0, pan=0.3, gain=0.32)
            else:
                arp(tr, b, ch, [0, 2, 1, 3, 2, 1, 3, 2], pan=0.3, gain=0.3)
            pat = [(0, "shime", 0.7), (3.5, "kakko", 0.4)]
            if sec >= 1:
                pat += [(2.5, "shime", 0.45), (3, "shime", 0.55)]
            if sec >= 2:
                pat += [(1, "atarigane", 0.7), (3, "atarigane", 0.7), (2, "atarigane", 0.35)]
                if k % 4 == 0:
                    pat.append((0, "odaiko", 0.55))
            if sec == 3 and k == 7:
                pat += [(2, "shime", 0.6), (2.5, "shime", 0.7), (3.25, "shime", 0.6), (3.5, "shime", 0.8)]
            taiko_bar(tr, b, pat, gain=0.6)
    reverb(tr, rt60=1.8, wet=0.9)
    return tr


def t_road(rng):
    """Roads and fields (E yo, 84 BPM, 4 + 32 bars): a koto-and-sho opening, A on the shakuhachi, A' koto lead
    with a shakuhachi counterline, B on the shinobue up high with the taiko, A'' shakuhachi and shinobue together."""
    tr = Track(36, 84, rng=rng, send=0.22)
    sc, root = YO, 64
    tr.sc, tr.root = sc, root
    A = M("0:1 1:1 2:2 | 3:1.5 2:.5 3:1 4:1 | 3:3 2:1 | 1:4 | 0:1 1:1 2:2 | 3:1.5 4:.5 5:1 4:1 | "
          "3:1 2:1 1:1 2:1 | 0:4", 8)
    A2 = M("0:1 1:.5 2:.5 2:2 | 3:1.5 2:.5 3:.5 4:.5 5:1 | 4:1 3:2 2:1 | 1:3 r:1 | 0:1 1:.5 2:.5 2:2 | "
           "3:1.5 4:.5 5:1 6:1 | 5:.5 4:.5 3:1 2:.5 1:.5 2:1 | 0:3 r:1", 8)
    Bm = M("5:2 4:1 5:1 | 6:2 5:1 4:1 | 3:1.5 4:.5 3:1 2:1 | 3:4 | 5:2 4:1 5:1 | 7:2 6:1 5:1 | "
           "4:1 3:1 2:1 1:1 | 2:2 1:2", 8)
    CTR = M("r:2 2:2 | 3:4 | 1:4 | -1:4 | r:2 2:2 | 3:2 2:2 | 1:4 | -2:4", 8)
    HA, HB = [0, 2, 1, 4, 0, 2, 1, 0], [3, 2, 1, 3, 3, 4, 2, 4]
    for b in range(4):                                                         # the opening: koto and sho only
        arp(tr, b, stack(sc, root - 12, [0, 0, 2, 4][b]), [0, 1, 2, 3, 2, 1, 2, 1], pan=-0.3, gain=0.4)
        tr.add(bass_koto(deg(sc, root - 24, [0, 0, 2, 4][b]), 3.0, rng), tr.at(b), 0.0, 0.7, 0.15, 0.0, "bass")
    tr.add(sho(stack(sc, root, 0, (0, 2, 3, 6)), 4 * 4 * tr.spb, rng), tr.at(0), 0.0, 0.5, 0.4, 0.0, "pad")
    plan = [(4, A, HA, 0), (12, A2, HA, 1), (20, Bm, HB, 2), (28, A, HA, 3)]
    for bar0, mel, H, sec in plan:
        if sec == 0:
            blow(tr, mel, "shakuhachi", bar0, sc, root, pan=0.1, gain=1.0)
        elif sec == 1:
            play(tr, mel, koto, bar0, sc, root + 12, pan=-0.1, gain=0.95)
            blow(tr, CTR, "shakuhachi", bar0, sc, root, pan=0.3, gain=0.55, tag="ctr")
        elif sec == 2:
            blow(tr, mel, "shinobue", bar0, sc, root + 12, pan=0.15, gain=0.8)
            play(tr, shift(mel, -2), koto, bar0, sc, root, pan=-0.35, gain=0.4, tag="ctr")
        else:
            blow(tr, mel, "shakuhachi", bar0, sc, root, pan=-0.1, gain=0.9)
            blow(tr, shift(mel, 5), "shinobue", bar0, sc, root, pan=0.3, gain=0.45, tag="ctr")
        for k in range(8):
            b = bar0 + k
            d = H[k]
            arp(tr, b, stack(sc, root - 12, d), [0, 1, 2, 3, 2, 1, 2, 1], pan=-0.3, gain=0.36)
            tr.add(bass_koto(deg(sc, root - 24, d), 2.6, rng), tr.at(b), 0.0, 0.75, 0.12, 0.004, "bass")
            if k % 2 == 0:
                tr.add(sho(stack(sc, root, d, (0, 2, 3, 6)), 2 * 4 * tr.spb, rng), tr.at(b), 0.0,
                       0.25 if sec != 2 else 0.4, 0.4, 0.0, "pad")
            pat = [(0, "odaiko", 0.5)] if k % 2 == 0 else []
            if sec >= 2:
                pat += [(1, "shime", 0.35), (2, "shime", 0.5), (3, "shime", 0.35), (3.5, "shime", 0.3)]
            if sec == 2 and k == 7:
                pat += [(2, "odaiko", 0.6), (3, "odaiko", 0.7)]
            taiko_bar(tr, b, pat, gain=0.6)
    tr.ambience(*[0.5 * w for w in (windnoise(tr.n, rng, 300, 1500), windnoise(tr.n, rng, 300, 1500))], 0.035)
    reverb(tr, rt60=2.6, wet=1.0)
    return tr


def t_cave(rng):
    """Caves, cellars, ruins (D in, 60 BPM, 24 bars): low biwa strokes and a jushichigen drone, a heartbeat o-daiko,
    drips, and a far shakuhachi that states a falling motif twice (the second time an answer)."""
    tr = Track(24, 60, rng=rng, send=0.42)
    sc, root = IN, 50
    tr.sc, tr.root = sc, root
    roots = [0, 0, 1, 0, 3, 1, 0, -1, 0, 0, 1, 0, 4, 3, 1, 0, 0, 1, 3, 1, 0, -1, 0, 0]
    for b in range(24):
        if b % 2 == 0:
            tr.add(biwa(deg(sc, root - 12, roots[b]), 4.0, rng, decay=0.7), tr.at(b), -0.3, 0.55, 0.4, 0.01, "biwa")
        tr.add(bass_koto(deg(sc, root - 12, roots[b]), 4.0, rng), tr.at(b), 0.1, 0.45, 0.2, 0.0, "bass")
        if b % 4 == 2:
            tr.add(biwa(deg(sc, root, [2, 1, 4, 1][b // 4 % 4]) - 1, 3.0, rng, bend=1.0, bend_at=0.6), tr.at(b, 2.5),
                   0.35, 0.3, 0.5, 0.01, "biwa")
        taiko_bar(tr, b, [(0, "odaiko", 0.4), (0.6, "odaiko", 0.22)], gain=0.65)
    q = M("3:3 4:1 | 3:2 2:1 1:1 | 0:4 | r:4 | 2:2 3:1 4:1 | 5:3 4:1 | 3:2 1:2 | 0:4", 8)
    blow(tr, q, "shakuhachi", 4, sc, root + 12, pan=0.4, gain=0.6, send=0.6)
    blow(tr, shift(cut(q, 4, 8), 2), "shakuhachi", 14, sc, root + 12, pan=-0.3, gain=0.5, send=0.7)
    blow(tr, cut(q, 0, 3), "shakuhachi", 19, sc, root + 12, pan=0.4, gain=0.45, send=0.7)
    for _ in range(30):
        tr.add(drip(rng), rng.uniform(0, tr.n / SR), rng.uniform(-0.8, 0.8), 0.7, 0.6, 0.0, "amb")
    w = windnoise(tr.n, rng, 120, 700, 17.0)
    tr.ambience(w, np.roll(w, 9000), 0.05)
    reverb(tr, rt60=4.2, wet=1.0, bright=2600, lowcut=220)
    return tr


def t_battle(rng):
    """Random battles (user: light rock with biwa, "more upbeat tempo"): A min'yo (A C D E G, a Japanese folk scale
    that is also rock's minor pentatonic), 176 BPM. Intro riff (once), A biwa melody, A' shinobue, B (F G Em Am, the
    biwa up high), a taiko breakdown, A'' biwa and shinobue in harmony with the lead guitar, a riff turnaround."""
    tr = Track(48, 176, rng=rng, send=0.1, intro=4)
    sc, root = MINYO, 57
    tr.sc, tr.root = sc, root
    A, F, G, Em, C = 45, 41, 43, 40, 48
    RIFF = [(0, 0, 0), (0.5, 0, 0), (1, 3, 0), (1.5, 0, 0), (2, 5, 0), (2.5, 0, 0), (3, 7, 2), (3.5, 5, 0)]
    RIFF2 = [(0, 12, 0), (0.5, 10, 0), (1, 7, 0), (1.5, 10, 2), (2, 7, 0), (2.5, 5, 0), (3, 3, 0), (3.5, 5, 0)]
    MA = M("5:1 4:.5 3:.5 4:1 5:1 | 3:2 2:1 1:1 | 2:1 3:.5 2:.5 1:1 0:.5 1:.5 | 2:3 r:1 | "
           "5:1 4:.5 3:.5 4:1 5:1 | 7~:2 6:1 5:1 | 6:1 5:.5 4:.5 5:1 6:1 | 7:3 r:1", 8)
    MB = M("3:2 4:1 5:1 | 6:3 5:1 | 4:1.5 3:.5 2:2 | 4:4 | 3:2 4:1 5:1 | 7:3 8:1 | 6:1 5:1 4:1 2:1 | 4:4", 8)
    MC = M("6:1.5 5:.5 6:1 7:1 | 8:2 7:2 | 8:1.5 7:.5 6:1 8:1 | 5:4 | 6:1.5 7:.5 8:1 9:1 | 10~:2 9:1 8:1 | "
           "7:1 6:1 5:1 6:1 | 8:4", 8)
    # F is not in A min'yo (its F sat a semitone over the melody's E): C, the relative major, instead
    progA, progB = [A, A, C, G, A, A, C, G], [C, G, Em, A, C, G, A, Em]
    # intro (bars 0-3, plays once): riff in unison, the band joins on bar 2
    for b in range(4):
        r = [A, A, C, G][b]
        riff(tr, b, r, RIFF, gain=1.0)
        riff(tr, b, r, RIFF, inst=lambda m, d, rg, **k: guitar(m, d, rg, drive=3.0, chord=(0, 12), mute=False),
             pan=0.0, gain=0.35, octave=0, tag="gtr")
        if b >= 2:
            kit_bar(tr, b, "drive" if b == 2 else "half", 0.6, fill="taiko" if b == 3 else None, crash=b == 2)
            bass_bar(tr, b, r - 12, "8ths", 0.75)
        else:
            taiko_bar(tr, b, [(0, "odaiko", 0.9), (2, "odaiko", 0.6), (3, "odaiko_rim", 0.6)], 0.7)
    sections = [(4, "A"), (12, "A2"), (20, "B"), (28, "BRK"), (32, "A3"), (40, "OUT")]
    for bar0, sec in sections:
        nb = 4 if sec == "BRK" else 8
        for k in range(nb):
            b = bar0 + k
            r = (progB if sec == "B" else progA)[k % 8]
            nxt = (progB if sec == "B" else progA)[(k + 1) % 8]
            last = k == nb - 1
            if sec == "BRK":
                taiko_bar(tr, b, [(0, "odaiko", 1.0), (1, "shime", 0.6), (1.5, "shime", 0.5), (2, "odaiko", 0.8),
                                  (2.5, "odaiko_rim", 0.5), (3, "shime", 0.7), (3.5, "shime", 0.8)], 0.7)
                bass_bar(tr, b, A - 12, "push", 0.8)
                riff(tr, b, A, RIFF if k % 2 == 0 else RIFF2, gain=0.85)
                if last:
                    kit_bar(tr, b, "light", 0.5, fill="roll")
                continue
            style = "half" if sec == "B" and k < 4 else "drive"
            kit_bar(tr, b, style, 0.6, fill=("taiko" if k % 4 == 3 else None) if not last else "snare",
                    crash=(k % 4 == 0))
            bass_bar(tr, b, r - 12, "8ths", 0.75, nxt=nxt - 12)
            gtr_bar(tr, b, r, "open" if sec == "B" and k < 4 else "chug", 0.42, drive=2.2)
            if sec == "OUT":
                riff(tr, b, r, RIFF if k < 4 else RIFF2, gain=0.95)
        if sec == "A":
            play(tr, MA, biwa, bar0, sc, root + 12, pan=-0.15, gain=1.1, vel=1.0)
        elif sec == "A2":
            blow(tr, MB, "shinobue", bar0, sc, root + 12, pan=0.25, gain=1.0)
            for k in (3, 7):
                riff(tr, bar0 + k, progA[k], RIFF2, gain=0.6, pan=-0.3)
        elif sec == "B":
            play(tr, MC, biwa, bar0, sc, root, pan=-0.1, gain=1.1, vel=1.0)
            play(tr, shift(MC, -2), lead, bar0, sc, root, pan=0.3, gain=0.5, tag="lead2")
        elif sec == "A3":
            play(tr, MA, biwa, bar0, sc, root + 12, pan=-0.2, gain=1.0, vel=1.0)
            blow(tr, MA, "shinobue", bar0, sc, root + 12, pan=0.3, gain=0.55, tag="lead2")
            play(tr, shift(MA, -2), lead, bar0, sc, root + 12, pan=0.15, gain=0.45, tag="lead2")
        elif sec == "OUT":
            blow(tr, cut(MB, 0, 4), "shinobue", bar0 + 4, sc, root + 12, pan=0.25, gain=0.8)
    reverb(tr, rt60=1.2, wet=0.9)
    return tr


def t_boss(rng):
    """The standard boss (E min'yo: E G A B D, 152 BPM, intro 4 + 44 bars): an o-daiko and kane opening, a gallop
    riff under a crying hichiriki (A), the biwa answers it (A'), a half-time B with the lead guitar, a taiko
    breakdown, a double-time C in harmony, and a riff turnaround."""
    tr = Track(48, 152, rng=rng, send=0.12, intro=4)
    sc, root = MINYO, 52
    tr.sc, tr.root = sc, root
    E, C, D, B_, A_, G_ = 40, 48, 50, 47, 45, 43
    MH = M("3:2 4:1 3:1 | 2:1.5 1:.5 0:2 | 1:1 2:1 3:1 4:1 | 3:3 r:1 | 3:2 4:1 5:1 | 6:1.5 5:.5 4:2 | "
           "3:1 4:.5 3:.5 2:1 1:1 | 3:4", 8)
    MH2 = M("3~:2 4:.5 3:.5 2:.5 3:.5 | 2:1.5 1:.5 0:2 | 1:.5 2:.5 2:1 3:1 4:1 | 3~:3 r:1 | 3:1.5 4:.5 5:1 6:1 | "
            "7:1.5 6:.5 5:2 | 3:1 4:.5 3:.5 2:1 1:1 | 3~:4", 8)
    MG = M("5:2 6:1 5:1 | 4:2 3:2 | 3:1 4:1 5:1 6:1 | 5:4 | 5:2 6:1 7:1 | 8:2 7:1 6:1 | 5:1 4:1 3:1 4:1 | 3:4", 8)
    RIFF = [(0, 0, 0), (0.75, 0, 0), (1, 3, 0), (1.5, 5, 0), (2, 0, 0), (2.75, 0, 0), (3, 7, 2), (3.5, 5, 0)]
    # C is not in E min'yo (it rubbed on the melody's B): G, the relative major, instead
    progA, progB = [E, E, G_, D, E, E, D, B_], [G_, D, E, E, G_, D, B_, B_]
    # intro: a ringing chord, the o-daiko, the kane, a hichiriki held high and swelling; the kit builds on bar 3
    for pan in (-0.65, 0.65):
        tr.add(guitar(E, 8 * tr.spb, rng, drive=3.0), tr.at(0), pan, 0.5, 0.2, 0.0, "gtr")
        tr.add(guitar(D, 4 * tr.spb, rng, drive=3.0), tr.at(2), pan, 0.45, 0.2, 0.0, "gtr")
    for b in range(4):
        taiko_bar(tr, b, [(0, "odaiko", 1.0), (1.5, "odaiko", 0.6), (3, "odaiko", 0.75)], 0.75)
    KANE = float(hz(74))                          # the kane on D (it was 560 Hz, a C# under the melody's D)
    tr.add(bell(KANE, 4.0, rng), tr.at(0), 0.5, 0.45, 0.4, 0.0, "bell")
    tr.add(bell(KANE, 4.0, rng), tr.at(2), -0.5, 0.4, 0.4, 0.0, "bell")
    blow(tr, M("3:6 4:2 | 5:8"), "hichiriki", 0, sc, root + 12, pan=0.2, gain=0.9)
    kit_bar(tr, 3, "half", 0.6, fill="roll")
    bass_bar(tr, 2, E - 12, "whole", 0.7)
    bass_bar(tr, 3, D - 12, "whole", 0.7)
    sections = [(4, "A"), (12, "A2"), (20, "B"), (28, "BRK"), (32, "C"), (40, "OUT")]
    for bar0, sec in sections:
        nb = 4 if sec == "BRK" else 8
        for k in range(nb):
            b = bar0 + k
            prog = progB if sec == "B" else progA
            r = prog[k % 8]
            last = k == nb - 1
            if sec == "BRK":
                taiko_bar(tr, b, [(0, "odaiko", 1.0), (0.5, "shime", 0.5), (1, "shime", 0.7), (1.5, "odaiko", 0.7),
                                  (2, "shime", 0.6), (2.5, "shime", 0.6), (3, "odaiko", 0.9), (3.5, "kakko", 0.6)], 0.75)
                bass_bar(tr, b, E - 12, "half", 0.8)
                if k % 2 == 0:
                    tr.add(bell(KANE, 3.0, rng), tr.at(b), 0.5, 0.4, 0.4, 0.0, "bell")
                if last:
                    kit_bar(tr, b, "light", 0.5, fill="snare")
                continue
            style = {"A": "gallop", "A2": "drive", "B": "half", "C": "double", "OUT": "gallop"}[sec]
            kit_bar(tr, b, style, 0.6, fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None),
                    crash=k % 4 == 0)
            if sec in ("A", "OUT", "C"):
                taiko_bar(tr, b, [(0, "odaiko", 0.6), (2.5, "odaiko", 0.4)], 0.6)
            bass_bar(tr, b, r - 12, {"A": "gallop", "OUT": "gallop", "B": "half"}.get(sec, "8ths"), 0.75)
            gtr_bar(tr, b, r, {"A": "gallop", "OUT": "gallop", "B": "half"}.get(sec, "chug"), 0.45, drive=3.0)
            if sec in ("A", "A2", "OUT") and k % 2 == 1:
                riff(tr, b, r, RIFF, gain=0.55, pan=-0.35)
            if k % 4 == 0:
                tr.add(bell(KANE, 3.0, rng), tr.at(b), 0.5, 0.35, 0.4, 0.0, "bell")
        if sec == "A":
            blow(tr, MH, "hichiriki", bar0, sc, root + 12, pan=0.2, gain=1.0)
        elif sec == "A2":
            play(tr, MH2, biwa, bar0, sc, root + 12, pan=-0.15, gain=1.1, vel=1.0)
            blow(tr, M("r:4 | 0:4 | 1:4 | 0:4 | r:4 | 3:4 | 1:4 | 0:4"), "hichiriki", bar0, sc, root + 12, pan=0.3,
                 gain=0.5, tag="ctr")
        elif sec == "B":
            play(tr, MG, lead, bar0, sc, root + 12, pan=0.15, gain=0.9)
            play(tr, MG, biwa, bar0, sc, root, pan=-0.25, gain=0.7, tag="lead2")
            for k in range(0, 8, 2):
                chord_pad(tr, bar0 + k, [progB[k] + 12, progB[k] + 19, progB[k] + 24], 2, "strings", gain=0.35)
        elif sec == "C":
            blow(tr, MH, "hichiriki", bar0, sc, root + 12, pan=0.25, gain=0.95)
            play(tr, shift(MH, -2), biwa, bar0, sc, root + 12, pan=-0.25, gain=0.8, tag="lead2")
        elif sec == "OUT":
            play(tr, cut(MG, 4, 8), lead, bar0 + 4, sc, root + 12, pan=0.15, gain=0.8)
    reverb(tr, rt60=1.8, wet=0.9)
    return tr


def t_court(rng):
    """Castles, palaces, mansions (D ryo, 56 BPM, 16 bars): gagaku colour. A stately hichiriki line through all 16
    bars with a shinobue shadowing it in heterophony, sho clusters, gakuso koto two-note figures, rolled biwa chords,
    kakko rolls and the taiko on the cycle."""
    tr = Track(16, 56, rng=rng, send=0.3)
    sc, root = RYO, 62
    tr.sc, tr.root = sc, root
    clusters = [[62, 66, 69, 71, 74], [64, 67, 69, 71, 76], [62, 64, 67, 69, 74], [59, 62, 66, 69, 71]]
    for b in range(0, 16, 2):
        tr.add(sho(keyed(tr, clusters[b // 2 % 4]), 2 * 4 * tr.spb + 1.2, rng), tr.at(b), 0.0, 0.7, 0.4, 0.0, "pad")
    mel = M("2:4 | 3:2 4:2 | 3:3 2:1 | 1:4 | 2:2 3:2 | 5:3 4:1 | 3:2 2:2 | 3:4 | 4:4 | 5:2 4:2 | 3:3 4:1 | "
            "3:2 2:2 | 1:2 2:2 | 3:2 1:2 | 0:4 | r:4", 16)
    blow(tr, mel, "hichiriki", 0, sc, root, pan=-0.15, gain=0.8)
    het = [(t + 0.25, max(0.5, ln - 0.25), d + 5, a, o) for t, ln, d, a, o in mel if ln >= 2]
    blow(tr, het, "shinobue", 0, sc, root, pan=0.3, gain=0.32, tag="ctr")
    for b in range(16):
        d = [0, 3, 0, 4, 2, 3, 1, 0][b % 8]
        for i, s in enumerate((0, 2, 3)):                                      # a rolled biwa chord
            tr.add(biwa(deg(sc, root - 24, d + s), 3.0, rng, decay=0.8), tr.at(b) + 0.05 * i, 0.35, 0.28, None,
                   0.004, "biwa")
        for beat, dd in ((1, 5), (1.5, 3), (2.5, 5), (3, 4)):                  # gakuso: the koto's pair figures
            tr.add(koto(deg(sc, root, d + dd), 1.8, rng, decay=0.8), tr.at(b, beat), -0.35, 0.28, None, 0.006, "arp")
        taiko_bar(tr, b, [(3, "kakko", 0.5)] + ([(3.5 + k * 0.08, "kakko", 0.25 + 0.05 * k) for k in range(5)]
                                                if b % 2 else []), 0.8)
        if b % 4 == 3:
            taiko_bar(tr, b, [(0, "odaiko", 0.45), (2, "shime", 0.35)], 0.8)
    reverb(tr, rt60=3.2, wet=1.0)
    return tr


def t_shrine(rng):
    """Shrines and temples (D yo, 60 BPM, 16 bars): rin bowls, a slow shakuhachi through 16 bars, koto harmonics,
    a low jushichigen and sho, a little wind."""
    tr = Track(16, 60, rng=rng, send=0.4)
    sc, root = YO, 62
    tr.sc, tr.root = sc, root
    for b in range(0, 16, 2):
        tr.add(bell(float(hz(deg(sc, root + 12, [0, 3, 2, 4][b // 2 % 4]))), 6.0, rng, ratios=(1.0, 2.71, 5.15),
                    beat=0.8), tr.at(b), rng.uniform(-0.5, 0.5), 0.75, 0.5, 0.0, "bell")
    mel = M("4:4 | 3:2 2:1 3:1 | 2:4 | r:2 1:2 | 2:3 3:1 | 4:2 3:2 | 2:2 1:2 | 0:4 | 5:3 4:1 | 3:2 4:2 | "
            "5:4 | r:2 4:2 | 3:2 2:2 | 1:2 2:1 1:1 | 0:4 | r:4", 16)
    blow(tr, mel, "shakuhachi", 0, sc, root, pan=0.15, gain=0.85)
    for b in range(16):
        tr.add(koto(deg(sc, root + 12, [0, 3, 4, 2][b % 4]), 2.5, rng, decay=0.7), tr.at(b, 1.5), -0.4, 0.3, None,
               0.01, "arp")
        if b % 4 == 0:
            tr.add(bass_koto(deg(sc, root - 24, [0, 2, 3, 0][b // 4]), 5.0, rng), tr.at(b), 0.0, 0.5, 0.2, 0.0,
                   "bass")
            tr.add(sho(stack(sc, root, [0, 2, 3, 0][b // 4], (0, 2, 3, 6)), 4 * 4 * tr.spb, rng), tr.at(b), 0.0,
                   0.22, 0.4, 0.0, "pad")
    wl, wr = windnoise(tr.n, rng, 300, 2000), windnoise(tr.n, rng, 300, 2000)
    tr.ambience(wl, wr, 0.04)
    reverb(tr, rt60=4.0, wet=1.0)
    return tr


def t_sea(rng):
    """Coasts, ports, ships, islands (E yo, 92 BPM, 32 bars): waves under a bright koto, the shinobue answering
    each phrase (call and response), jushichigen, a rolling shime; B rises, the last A in octaves."""
    tr = Track(32, 92, rng=rng, send=0.22)
    sc, root = YO, 64
    tr.sc, tr.root = sc, root
    a = M("2:1.5 3:.5 4:2 | 3:1 2:1 1:2 | 2:1.5 3:.5 2:1 1:1 | 0:4", 4)
    a2 = M("2:1.5 3:.5 4:2 | 5:1 4:1 3:2 | 4:1.5 3:.5 2:1 1:1 | 2:4", 4)
    ans = M("r:2 4:1 5:1 | 6:4 | r:2 5:1 4:1 | 3:4", 4)
    b = M("5:1.5 6:.5 7:2 | 6:1 5:1 4:2 | 5:1 4:1 3:1 2:1 | 3:4", 4)
    b2 = M("5:1.5 6:.5 7:2 | 8:1 7:1 6:2 | 5:1 4:1 3:1 4:1 | 5:4", 4)
    plan = [(0, a, "k"), (4, a2, "k"), (8, a, "k"), (12, ans, "f"), (16, b, "k"), (20, b2, "f"), (24, a, "kf"),
            (28, a2, "kf")]
    for bar0, mel, who in plan:
        if "k" in who:
            play(tr, mel, koto, bar0, sc, root + 12, pan=-0.2, gain=0.95)
            if bar0 < 12:
                blow(tr, shift(ans, 0), "shinobue", bar0, sc, root + 12, pan=0.35, gain=0.45, tag="ctr")
        if "f" in who:
            blow(tr, mel if who == "f" else shift(mel, 5), "shinobue", bar0, sc, root + 12 if who == "f" else root,
                 pan=0.3, gain=0.7 if who == "f" else 0.5)
            if who == "f":
                play(tr, shift(mel, -2), koto, bar0, sc, root + 12, pan=-0.3, gain=0.5, tag="ctr")
    H = [0, 3, 2, 0, 0, 3, 4, 1] * 2 + [3, 4, 2, 1, 3, 4, 2, 3] + [0, 3, 2, 0, 0, 3, 4, 1]
    for k in range(32):
        d = H[k]
        tr.add(bass_koto(deg(sc, root - 24, d), 2.4, rng), tr.at(k), 0.0, 0.7, 0.1, 0.004, "bass")
        tr.add(bass_koto(deg(sc, root - 24, d + 3), 1.2, rng), tr.at(k, 2.5), 0.0, 0.45, 0.1, 0.004, "bass")
        arp(tr, k, stack(sc, root, d), [0, None, 2, 1, None, 3, 2, None], pan=0.25, gain=0.3)
        if k >= 8:
            taiko_bar(tr, k, [(0, "shime", 0.5), (1.5, "shime", 0.35), (2, "shime", 0.45), (3.5, "kakko", 0.35)],
                      0.55)
    wl, wr = waves(tr.n, rng, 0.22)
    tr.ambience(wl, wr, 1.0)
    reverb(tr, rt60=2.2, wet=1.0)
    return tr


def t_night(rng):
    """Night, sorrow, the dead (D in, 58 BPM, 16 bars): a solo shakuhachi in honkyoku style, long tones and ma,
    a soft koto underneath, a rin now and then, bell-crickets."""
    tr = Track(16, 58, rng=rng, send=0.36)
    sc, root = IN, 62
    tr.sc, tr.root = sc, root
    mel = M("3~:4 | 4:1 3:1 2:2 | 1:3 r:1 | 0:4 | 2:2 3:2 | 4~:3 5:1 | 4:2 3:2 | 3:4 | "
            "5:3 4:1 | 3:2 4:1 3:1 | 2:4 | r:2 2:1 3:1 | 1:3 2:1 | 1:2 0:2 | 0:4 | r:4", 16)
    blow(tr, mel, "shakuhachi", 0, sc, root, pan=0.1, gain=0.9)
    for b in range(16):
        d = [0, 3, 1, 3, 0, 2, 1, 4][b % 8]
        tr.add(koto(deg(sc, root - 12, d), 3.5, rng, decay=0.6), tr.at(b), -0.3, 0.45, None, 0.01, "arp")
        tr.add(koto(deg(sc, root - 12, d + 5), 2.0, rng, decay=0.9), tr.at(b, 2), -0.3, 0.18, None, 0.01, "arp")
        if b % 4 == 0:
            tr.add(bass_koto(deg(sc, root - 24, d), 5.0, rng), tr.at(b), 0.0, 0.4, 0.2, 0.0, "bass")
        if b % 8 == 6:
            tr.add(bell(float(hz(deg(sc, root + 12, 0))), 6.0, rng, ratios=(1.0, 2.71, 5.15), beat=0.6),
                   tr.at(b, 1), 0.4, 0.3, 0.5, 0.0, "bell")
    il, ir = insects(tr.n, rng), insects(tr.n, rng)
    tr.ambience(il, ir, 1.0, send=0.3)
    reverb(tr, rt60=3.6, wet=1.0)
    return tr


def t_past(rng):
    """The year 400 and the ink (F# in, 66 BPM, 16 bars): high koto bells drowning in reverb, a sho that never
    resolves, a shakuhachi remembering."""
    tr = Track(16, 66, rng=rng, send=0.5)
    sc, root = IN, 66
    tr.sc, tr.root = sc, root
    for b in range(0, 16, 4):
        tr.add(sho(keyed(tr, [61, 66, 68, 73]), 4 * 4 * tr.spb + 1.0, rng), tr.at(b), 0.0, 0.4, 0.5, 0.0, "pad")
        tr.add(bass_koto(deg(sc, root - 24, [0, 1, 0, -1][b // 4]), 6.0, rng), tr.at(b), 0.0, 0.35, 0.3, 0.0, "bass")
    for b in range(16):
        for i, d in enumerate((0, 2, 4, 6, 4, 2)):
            if rng.random() < 0.8:
                tr.add(koto(deg(sc, root, d + [0, 1, 0, -1][b % 4]), 2.2, rng, decay=0.5), tr.at(b, i * 0.66),
                       rng.uniform(-0.6, 0.6), 0.28, None, 0.0, "arp")
    mel = M("5:6 4:2 | 3:4 r:4 | 4:4 5:2 6:2 | 5:8 | r:4 4:2 3:2 | 2:8", 12)
    blow(tr, mel, "shakuhachi", 4, sc, root - 12, pan=0.2, gain=0.6)
    reverb(tr, rt60=5.5, wet=1.0)
    return tr


def t_shadow(rng):
    """The Shadowlands and maho (A hirajoshi: A B C E F, 64 BPM, 24 bars): a drone that grinds, a heartbeat that
    quickens, the biwa bending down, minor-second sho clusters, a horagai calling from far off, reversed swells,
    a hichiriki fragment with a tritone in it, and the wind."""
    tr = Track(24, 64, rng=rng, send=0.4)
    sc, root = HIRA, 45
    tr.sc, tr.root = sc, root
    for b in range(24):
        tr.add(biwa(root - 12 + [0, 1, 0, 6][b % 4], 4.0, rng, bend=-1.0, bend_at=1.0), tr.at(b), -0.3, 0.55, 0.3,
               0.01, "biwa")
        beats = [(0, "odaiko", 0.55), (0.4, "odaiko", 0.3)] if b < 16 else \
                [(0, "odaiko", 0.6), (0.35, "odaiko", 0.35), (2, "odaiko", 0.45), (2.35, "odaiko", 0.28)]
        taiko_bar(tr, b, beats, 0.7, pan_spread=0.1)
        if b % 4 == 0:
            tr.add(bass_koto(root - 12, 8.0, rng), tr.at(b), 0.0, 0.35, 0.1, 0.0, "bass")
            tr.add(sho([root + 12, root + 13, root + 19, root + 20], 4 * 4 * tr.spb, rng), tr.at(b), 0.0, 0.35,
                   0.5, 0.0, "pad")
        if b % 8 == 7:
            tr.add(swell(4 * tr.spb, rng, 300, 4000), tr.at(b), 0.0, 0.8, 0.3, 0.0, "fx")
    blow(tr, M("0:3 -1:1 | 0:4"), "horagai", 2, sc, root + 12, pan=-0.6, gain=0.35, send=0.8)
    blow(tr, M("0:2 1:2 | 0:4"), "horagai", 14, sc, root + 12, pan=0.6, gain=0.3, send=0.8)
    mel = M("3:4 | 4:2 3:2 | 2:3 3:1 | 1:4 | 3:3 1b:1 | 3:4 | 2:2 1:1 0:1 | 0:4", 8)
    blow(tr, mel, "hichiriki", 8, sc, root + 24, pan=0.3, gain=0.65)
    blow(tr, shift(cut(mel, 4, 8), -1), "shakuhachi", 18, sc, root + 12, pan=-0.3, gain=0.55)
    for b in range(0, 24, 4):
        tr.add(bell(float(hz(64)), 5.0, rng, beat=2.5), tr.at(b, 1), 0.5, 0.4, 0.5, 0.0, "bell")
    w = windnoise(tr.n, rng, 200, 1200, 9.0)
    tr.ambience(w, np.roll(w, 13000), 0.07, send=0.2)
    reverb(tr, rt60=4.5, wet=1.0, bright=2200)
    return tr


# ---- boss themes (new in v2)
def t_boss_oni(rng):
    """Oni, maho and the Taint (D in: D Eb G A Bb, 138 BPM, intro 4 + 40 bars): a horagai call and a tremolo chord,
    then a semitone gallop riff (D-Eb) under a screaming hichiriki; a half-time doom section with a low choir;
    a blast section with the shamisen tremolo; a breakdown of heartbeats and sho clusters; the riff again."""
    tr = Track(44, 138, rng=rng, send=0.14, intro=4)
    sc, root = IN, 50
    tr.sc, tr.root = sc, root
    D, Eb, Bb, A_, G_ = 38, 39, 46, 45, 43
    MO = M("5:2 6:1 5:1 | 4:1.5 3:.5 4:2 | 3:1 2:1 1:2 | 0:4 | 5:2 6:1 7:1 | 8~:2 7:1 6:1 | "
           "5:1 4:1 3:1 1:1 | 0:4", 8)
    MZ = M("5z:2 6z:2 | 4z:2 3z:2 | 2z:2 3z:1 4z:1 | 5z:4 | 7z:2 8z:2 | 9z:2 8z:2 | 7z:1 6z:1 5z:1 4z:1 | 5z:4", 8)
    RIFF = [(0, 0, 0), (0.5, 0, 0), (0.75, 0, 0), (1, 1, 0), (1.5, 0, 0), (2, 0, 0), (2.5, 6, 0), (3, 5, 0),
            (3.5, 1, 0)]
    progA = [D, D, Bb, A_, D, Eb, Bb, D]
    progB = [Bb, A_, G_, Eb, Bb, A_, Eb, D]
    blow(tr, M("0:3 -1:1 | 0:2 -2:2"), "horagai", 0, sc, root, pan=-0.3, gain=0.55, send=0.6)
    for b in range(4):
        taiko_bar(tr, b, [(0, "odaiko", 1.0), (2, "odaiko", 0.7)], 0.8)
        for pan in (-0.65, 0.65):
            for i in range(16):                                                 # a tremolo-picked chord swelling
                tr.add(guitar(D, 0.2, rng, drive=3.5, mute=True), tr.at(b, i * 0.25), pan,
                       0.12 + 0.3 * (b * 16 + i) / 64, 0.1, 0.002, "gtr")
    tr.add(sho([62, 63, 69, 70], 4 * 4 * tr.spb, rng), tr.at(0), 0.0, 0.6, 0.5, 0.0, "pad")
    kit_bar(tr, 3, "half", 0.6, fill="roll")
    sections = [(4, "A"), (12, "B"), (20, "C"), (28, "BRK"), (32, "A2"), (40, "OUT")]
    for bar0, sec in sections:
        nb = 4 if sec in ("BRK", "OUT") else 8
        for k in range(nb):
            b = bar0 + k
            r = (progB if sec == "B" else progA)[k % 8]
            last = k == nb - 1
            if sec == "BRK":
                taiko_bar(tr, b, [(0, "odaiko", 0.9), (0.4, "odaiko", 0.55), (2, "odaiko", 0.7),
                                  (2.4, "odaiko", 0.45)], 0.8)
                if k == 0:
                    tr.add(bass_koto(D, 8 * tr.spb, rng), tr.at(b), 0.0, 0.6, 0.1, 0.0, "bass")
                    tr.add(sho([50, 51, 57, 58], 4 * 4 * tr.spb, rng), tr.at(b), 0.0, 0.6, 0.6, 0.0, "pad")
                    tr.add(biwa(D + 12, 6.0, rng, bend=-1.0, bend_at=1.5), tr.at(b, 1), -0.3, 0.6, 0.4, 0.0, "biwa")
                if k == 2:
                    tr.add(swell(8 * tr.spb, rng), tr.at(b), 0.0, 0.9, 0.3, 0.0, "fx")
                if last:
                    kit_bar(tr, b, "light", 0.55, fill="roll")
                continue
            style = {"A": "gallop", "B": "half", "C": "blast", "A2": "gallop", "OUT": "drive"}[sec]
            kit_bar(tr, b, style, 0.62, fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None),
                    crash=k % 4 == 0)
            taiko_bar(tr, b, [(0, "odaiko", 0.7)] + ([(2, "odaiko", 0.5)] if sec != "C" else []), 0.65)
            bass_bar(tr, b, r - 12 if r > 40 else r, {"B": "whole", "C": "8ths"}.get(sec, "gallop"), 0.8)
            if sec == "B":
                gtr_bar(tr, b, r, "open", 0.45, drive=3.5)
                if k % 2 == 0:
                    chord_pad(tr, b, [r + 12, r + 19, r + 24], 2, "choir", vowel="o", gain=0.55)
            else:
                gtr_bar(tr, b, r, "gallop" if sec in ("A", "A2") else "chug", 0.45, drive=3.5)
                if sec in ("A", "A2", "OUT"):
                    riff(tr, b, r, RIFF, gain=0.5 if sec != "OUT" else 0.85, pan=-0.3)
        if sec == "A":
            blow(tr, MO, "hichiriki", bar0, sc, root + 12, pan=0.2, gain=1.0)
        elif sec == "B":
            play(tr, M("5~:3 4:1 | 3:4 | 2~:2 1:2 | 0:4 | 5~:3 6:1 | 5:2 4:2 | 3:2 1:2 | 0:4", 8), biwa, bar0, sc,
                 root, pan=-0.15, gain=1.1, vel=1.0)
            blow(tr, M("r:4 | 0:4 | r:4 | -1:4 | r:4 | 1:4 | r:4 | 0:4", 8), "horagai", bar0, sc, root, pan=0.4,
                 gain=0.35, send=0.6, tag="ctr")
        elif sec == "C":
            play(tr, MZ, shamisen, bar0, sc, root, pan=0.25, gain=0.85)
            play(tr, shift(MO, 0), biwa, bar0, sc, root, pan=-0.25, gain=0.8, tag="lead2")
        elif sec == "A2":
            blow(tr, MO, "hichiriki", bar0, sc, root + 12, pan=0.2, gain=0.95)
            for k in range(0, 8, 2):
                chord_pad(tr, bar0 + k, [progA[k] + 24, progA[k] + 31, progA[k] + 36], 2, "choir", vowel="a",
                          gain=0.4)
        elif sec == "OUT":
            blow(tr, M("0:3 1:1 | 0:4 | 0:2 -1:2 | 0:4"), "horagai", bar0, sc, root, pan=-0.4, gain=0.4, send=0.5)
    reverb(tr, rt60=2.2, wet=0.9, bright=3200)
    return tr


def t_duel(rng):
    """Duels and rivals (A in: A Bb D E F, 168 BPM, intro 4 + 40 bars). Kabuki clappers and a held shakuhachi, ma,
    the clappers speeding up (kizami); then two duelists: the shamisen (left) and the biwa (right) trade phrases
    over drums and bass; the guitars come in; B in unison (the clash); a stillness before the cut; the shakuhachi
    over everything."""
    tr = Track(44, 168, rng=rng, send=0.12, intro=4)
    sc, root = IN, 57
    tr.sc, tr.root = sc, root
    A_, Bb, F_, E_, D_ = 45, 46, 41, 40, 50
    L1, R1 = M("5:.5 5:.5 3:.5 4:.5 5:1 7:.5 6:.5 | 5:1 4:.5 3:.5 2:2", 2), M("2:.5 2:.5 3:.5 4:.5 5:1 4:.5 3:.5 | "
                                                                             "1:1 2:.5 1:.5 0:2", 2)
    L2, R2 = M("5:.5 5:.5 6:.5 7:.5 8:1 7:.5 6:.5 | 7:1 6:.5 5:.5 6:2", 2), M("6:.5 5:.5 4:.5 3:.5 4:1 3:.5 2:.5 | "
                                                                             "1:1.5 2:.5 0:2", 2)
    MD = M("4:2 3:2 | 4:1 5:1 6:2 | 4:2 3:2 | 1:1 2:1 3:2 | 2:2 3:2 | 4:1 5:1 6:2 | 7:1.5 6:.5 5:1 4:1 | 3:4", 8)
    MS = M("3:3 4:1 | 3:2 2:2 | 1:3 2:1 | 3:4 | 5:3 6:1 | 7:2 6:1 5:1 | 4:2 3:2 | 3:4", 8)
    progA = [A_, A_, Bb, A_, A_, A_, F_, E_]
    progB = [F_, E_, F_, E_, D_, E_, Bb, E_]
    # intro: two clacks, a held shakuhachi, ma; then the kizami (the clappers accelerating) into the downbeat
    taiko_bar(tr, 0, [(0, "hyoshigi", 1.0), (1, "hyoshigi", 1.0)], 0.9, 0.05)
    blow(tr, M("3:4 | 3:2 4:2"), "shakuhachi", 0, sc, root + 12, pan=0.1, gain=0.8, send=0.5)
    ts = np.cumsum(0.42 * 0.86 ** np.arange(22))
    ts = ts[ts < 8 * tr.spb - 0.05]
    for i, t in enumerate(ts):
        tr.add(drum("hyoshigi", rng), tr.at(2) + t, rng.uniform(-0.05, 0.05), 0.5 + 0.4 * i / len(ts), 0.15, 0.0,
               "taiko")
    tr.add(drum("odaiko", rng), tr.at(3, 3.5), 0.0, 0.7, 0.2, 0.0, "taiko")
    sections = [(4, "A"), (12, "A2"), (20, "B"), (28, "BRK"), (32, "C"), (40, "OUT")]
    for bar0, sec in sections:
        nb = 4 if sec in ("BRK", "OUT") else 8
        for k in range(nb):
            b = bar0 + k
            r = (progB if sec == "B" else progA)[k % 8]
            last = k == nb - 1
            if sec == "BRK":
                if k < 2:
                    if k == 0:
                        blow(tr, M("5:8"), "shakuhachi", b, sc, root, pan=0.0, gain=0.8, send=0.6)
                        tr.add(drum("hyoshigi", rng), tr.at(b), 0.0, 0.9, 0.2, 0.0, "taiko")
                    continue
                taiko_bar(tr, b, [(i * 0.25, "shime", 0.3 + 0.6 * (i + (k - 2) * 16) / 32) for i in range(16)], 0.7)
                if last:
                    taiko_bar(tr, b, [(3, "odaiko", 0.8), (3.5, "odaiko", 1.0)], 0.8)
                continue
            style = "drive" if sec != "C" else "double"
            kit_bar(tr, b, style, 0.58, fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None),
                    crash=k % 4 == 0)
            bass_bar(tr, b, r - 12 if r >= 40 else r, "push" if sec == "A" else "8ths", 0.78)
            if sec != "A":
                gtr_bar(tr, b, r, "chug" if sec != "B" else "half", 0.42, drive=2.6)
            else:
                taiko_bar(tr, b, [(0, "odaiko", 0.6), (1.5, "shime", 0.4), (2.5, "shime", 0.4), (3, "shime", 0.5)],
                          0.6)
        if sec in ("A", "A2", "C"):                                            # the two duelists trading phrases
            g = 0.55 if sec == "C" else 1.0
            for k, (l, r_) in enumerate(((L1, R1), (L2, R2))):
                play(tr, l, shamisen, bar0 + 4 * k, sc, root, pan=-0.55, gain=1.6 * g, vel=1.0, tag="duelL")
                play(tr, r_, biwa, bar0 + 4 * k + 2, sc, root, pan=0.55, gain=1.0 * g, vel=1.0, tag="duelR")
        if sec == "A2":
            blow(tr, M("3:8 | 4:4 3:4 | 5:8 | 6:4 5:4", 8), "shakuhachi", bar0, sc, root + 12, pan=0.0, gain=0.5,
                 tag="ctr")
        elif sec == "B":
            play(tr, MD, shamisen, bar0, sc, root, pan=-0.4, gain=1.35, vel=1.0, tag="duelL")
            play(tr, MD, biwa, bar0, sc, root - 12, pan=0.4, gain=0.9, vel=1.0, tag="duelR")
            blow(tr, MD, "shinobue", bar0, sc, root + 12, pan=0.0, gain=0.45, tag="lead2")
        elif sec == "C":
            blow(tr, MS, "shakuhachi", bar0, sc, root + 12, pan=0.0, gain=1.0)
        elif sec == "OUT":
            play(tr, L2 + [(t + 8, ln, d, a, o) for t, ln, d, a, o in R2], shamisen, bar0, sc, root, pan=-0.3,
                 gain=1.0, vel=1.0)
    reverb(tr, rt60=1.6, wet=0.9)
    return tr


def t_intrigue(rng):
    """Court villains, assassins, the Order (G in: G Ab C D Eb, a 3/4 court dance at 138 BPM, intro 4 + 60 bars).
    A staccato koto waltz and a plucked bass, kakko and hyoshigi, a slinky shamisen melody with grace notes (A),
    a sinuous hichiriki over sho swells (B), a low biwa creeping (C), the biwa and shinobue together (A')."""
    tr = Track(64, 138, beats=3, rng=rng, send=0.16, intro=4)
    sc, root = IN, 55
    tr.sc, tr.root = sc, root
    G_, Ab, Eb, D_ = 43, 44, 39, 38
    VO = {G_: (55, 60, 62), Ab: (56, 60, 63), Eb: (55, 58 + 2, 63), D_: (56, 62, 67)}   # in-scale court chords
    VO[Eb] = (55, 60, 63)
    prog = [G_, G_, Ab, Ab, Eb, D_, G_, D_]
    P1 = M("3:1 4^:.5 3:.5 1:1 | 0:3 | 2:1 3:.5 2:.5 1:1 | 0:2 -1:1", 4, 3)
    P2 = M("3:1 4:.5 5:.5 6:1 | 5:2 4:1 | 3:1 4:.5 3:.5 1:1 | 3:3", 4, 3)
    P1z = M("3:1 4^:.5 3:.5 1:1 | 0z:3 | 2:1 3:.5 2:.5 1:1 | 0:2 -1:1", 4, 3)
    P3 = M("5:3 | 6:2 5:1 | 4:3 | 3:2 1:1 | 2:3 | 3:2 4:1 | 3:2 1:1 | 0:3", 8, 3)
    CR = M("0:1 -1:1 0:1 | 1:3 | 0:1 -1:1 -2:1 | -1:3", 4, 3)
    for b in range(64):
        r = prog[b % 8]
        sec = "I" if b < 4 else "A" if b < 20 else "B" if b < 36 else "C" if b < 44 else "A2" if b < 60 else "T"
        bass_bar(tr, b, r, "waltz", 0.7)
        if sec != "C":
            for beat in (1, 2):
                for m in VO[r]:
                    tr.add(koto(m, 0.5, rng, decay=4.0, vel=0.9), tr.at(b, beat), 0.3, 0.2, None, 0.006, "arp")
            if sec in ("A2", "B"):
                for pan in (-0.6, 0.6):
                    tr.add(guitar(r + 12, 0.25, rng, drive=2.0, mute=True), tr.at(b, 1), pan, 0.18, 0.05, 0.004, "gtr")
                    tr.add(guitar(r + 12, 0.25, rng, drive=2.0, mute=True), tr.at(b, 2), pan, 0.15, 0.05, 0.004, "gtr")
        if sec in ("A", "B", "A2"):
            kit_bar(tr, b, "waltz", 0.5, crash=(b % 16 == 4))
        taiko_bar(tr, b, [(0, "kakko", 0.5), (2.5, "kakko", 0.35)] +
                  ([(0, "hyoshigi", 0.8)] if b % 4 == 0 else []), 0.6, 0.15)
        if b % 8 == 7 and sec != "I":
            taiko_bar(tr, b, [(2 + k * 0.17, "kakko", 0.3 + 0.08 * k) for k in range(6)], 0.6)
        if sec == "B" and b % 4 == 0:
            tr.add(sho([55, 56, 62, 63, 67], 4 * 3 * tr.spb + 0.5, rng), tr.at(b), 0.0, 0.4, 0.4, 0.0, "pad")
        if sec == "C":
            taiko_bar(tr, b, [(0, "odaiko", 0.4)] if b % 2 == 0 else [], 0.6)
    for bar0, mel in ((4, P1), (8, P2), (12, P1z), (16, P2)):
        play(tr, mel, shamisen, bar0, sc, root + 12, pan=-0.2, gain=1.0, vel=1.0)
    blow(tr, P3, "hichiriki", 20, sc, root + 12, pan=0.15, gain=0.85)
    blow(tr, shift(P3, 1), "hichiriki", 28, sc, root + 12, pan=0.15, gain=0.85)
    play(tr, shift(P3, -5), koto, 28, sc, root + 12, pan=-0.35, gain=0.45, tag="ctr")
    for bar0 in (36, 40):
        play(tr, CR, biwa, bar0, sc, root, pan=-0.2, gain=1.0, vel=1.0)
    for bar0, mel in ((44, P1), (48, P2), (52, P1z), (56, P2)):
        play(tr, mel, biwa, bar0, sc, root + 12, pan=-0.2, gain=0.95, vel=1.0)
    blow(tr, shift(P3, 5), "shinobue", 44, sc, root, pan=0.3, gain=0.45, tag="ctr")
    blow(tr, P3, "shinobue", 52, sc, root + 12, pan=0.3, gain=0.4, tag="ctr")
    play(tr, M("0:1 1:1 0:1 | -1:3 | 0:1 1:1 3:1 | 0:3", 4, 3), shamisen, 60, sc, root + 12, pan=-0.2, gain=0.9)
    reverb(tr, rt60=1.9, wet=0.9)
    return tr


def t_miniboss(rng):
    """Mini-bosses (D min'yo: D F G A C, 184 BPM, intro 2 + 32 bars): punchier and shorter than the boss theme. A
    biwa melody over a driving band, the shinobue over double-time kicks, a taiko break, the lead guitar and biwa in
    harmony."""
    tr = Track(34, 184, rng=rng, send=0.1, intro=2)
    sc, root = MINYO, 50
    tr.sc, tr.root = sc, root
    D_, Bb, C_, A_ = 38, 46, 48, 45
    MM = M("5:.5 5:.5 4:.5 5:.5 6:1 5:1 | 4:1 3:.5 2:.5 3:2 | 2:1 3:.5 4:.5 3:1 2:.5 1:.5 | 0:3 r:1 | "
           "5:.5 5:.5 4:.5 5:.5 6:1 7:1 | 8~:2 7:1 6:1 | 7:1 6:.5 5:.5 4:1 5:1 | 3:4", 8)
    MN = M("3:2 4:1 5:1 | 6:3 5:1 | 4:2 5:1 6:1 | 5:4 | 4:2 5:1 6:1 | 7:3 6:1 | 5:1 4:1 3:1 2:1 | 3:4", 8)
    RIFF = [(0, 0, 0), (0.5, 12, 0), (1, 10, 0), (1.5, 7, 0), (2, 0, 0), (2.5, 5, 0), (3, 7, 2), (3.5, 3, 0)]
    # Bb is not in D min'yo (it rubbed on the melody's A): G instead (i - IV - bVII)
    G_ = 43
    progA, progB = [D_, D_, G_, C_, D_, D_, G_, A_], [G_, C_, D_, D_, G_, C_, A_, A_]
    for b in range(2):
        riff(tr, b, [D_, C_][b], RIFF, gain=1.0)
        gtr_bar(tr, b, [D_, C_][b], "stab", 0.45, drive=2.8, beats=(0, 1.5, 3))
        taiko_bar(tr, b, [(0, "odaiko", 0.9), (1.5, "odaiko", 0.6), (3, "odaiko", 0.8), (3.5, "odaiko", 0.8)], 0.7)
    for bar0, sec in ((2, "A"), (10, "B"), (18, "BRK"), (22, "A2"), (30, "OUT")):
        nb = 4 if sec in ("BRK", "OUT") else 8
        for k in range(nb):
            b = bar0 + k
            r = (progB if sec == "B" else progA)[k % 8]
            last = k == nb - 1
            if sec == "BRK":
                taiko_bar(tr, b, [(0, "odaiko", 1.0), (0.75, "odaiko", 0.6), (1.5, "shime", 0.7), (2, "odaiko", 0.9),
                                  (2.75, "shime", 0.6), (3, "shime", 0.7), (3.5, "odaiko_rim", 0.7)], 0.7)
                bass_bar(tr, b, D_, "push", 0.8)
                riff(tr, b, D_, RIFF, gain=0.8)
                if last:
                    kit_bar(tr, b, "light", 0.5, fill="snare")
                continue
            kit_bar(tr, b, "double" if sec == "B" else "drive", 0.6,
                    fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None), crash=k % 4 == 0)
            bass_bar(tr, b, r - 12 if r > 40 else r, "8ths", 0.78, nxt=(progB if sec == "B" else progA)[(k + 1) % 8])
            gtr_bar(tr, b, r, "chug", 0.44, drive=2.8)
            if sec == "OUT":
                riff(tr, b, r, RIFF, gain=0.9)
        if sec == "A":
            play(tr, MM, biwa, bar0, sc, root + 12, pan=-0.15, gain=1.1, vel=1.0)
        elif sec == "B":
            blow(tr, MN, "shinobue", bar0, sc, root + 12, pan=0.2, gain=1.0)
            play(tr, shift(MN, -2), biwa, bar0, sc, root, pan=-0.3, gain=0.6, tag="lead2")
        elif sec == "A2":
            play(tr, MM, lead, bar0, sc, root + 12, pan=0.2, gain=0.85)
            play(tr, shift(MM, -2), biwa, bar0, sc, root + 12, pan=-0.25, gain=0.85, tag="lead2")
    reverb(tr, rt60=1.3, wet=0.9)
    return tr


def t_final1(rng):
    """The finale, phase 1: Doji Nashiko, the Bride in White (D in, 144 BPM, intro 8 + 48 bars). A music-box koto
    lullaby states her motif over a sho and rin; the band crashes in half-time under a choir, the hichiriki sings the
    motif; full time with the lullaby still ringing above; a breakdown where only the lullaby is left; the motif on
    the lead guitar with the choir; a new 'veil' melody; the riff."""
    tr = Track(56, 144, rng=rng, send=0.16, intro=8)
    sc, root = IN, 62
    tr.sc, tr.root = sc, root
    D_, Bb, G_, A_, Eb = 38, 46, 43, 45, 39
    N1, N2 = M(NASHIKO, 4), M(NASHIKO2, 4)
    N = N1 + [(t + 16, ln, d, a, o) for t, ln, d, a, o in N2]
    MV = M("7:2 6:1 5:1 | 4:2 3:2 | 2:1 3:1 4:1 5:1 | 3:4 | 7:2 8:1 9:1 | 10~:2 9:1 8:1 | 7:1 6:1 5:1 4:1 | 5:4", 8)
    prog = [D_, Bb, G_, A_, D_, Eb, Bb, A_]
    progV = [Bb, A_, G_, A_, Bb, A_, Eb, D_]
    RIFF = [(0, 0, 0), (0.5, 0, 0), (1, 1, 0), (1.5, 0, 0), (2, 7, 0), (2.5, 5, 0), (3, 1, 0), (3.5, 0, 0)]
    # the lullaby (bars 0-7): music box, sho, rin; the drums gather on bars 6-7
    play(tr, N, musicbox, 0, sc, root + 12, pan=0.2, gain=0.9, tag="lead")
    play(tr, shift(N, -5), koto, 0, sc, root + 12, pan=-0.3, gain=0.3, vel=0.7, tag="ctr")
    for b in range(0, 8, 2):
        tr.add(sho([62, 69, 75, 81], 2 * 4 * tr.spb + 0.5, rng), tr.at(b), 0.0, 0.4, 0.4, 0.0, "pad")
        tr.add(bell(float(hz(86)), 5.0, rng, ratios=(1.0, 2.71, 5.15), beat=0.7), tr.at(b), 0.5, 0.3, 0.5, 0.0, "bell")
    chord_pad(tr, 6, [50, 57, 62], 2, "choir", vowel="a", gain=0.5, att=2.0)
    taiko_bar(tr, 6, [(0, "odaiko", 0.7), (2, "odaiko", 0.8), (3, "odaiko", 0.9)], 0.7)
    kit_bar(tr, 7, "light", 0.6, fill="roll")
    tr.add(swell(4 * tr.spb, rng), tr.at(7), 0.0, 0.9, 0.3, 0.0, "fx")
    sections = [(8, "A"), (16, "B"), (24, "C"), (32, "A2"), (40, "V"), (48, "OUT")]
    for bar0, sec in sections:
        for k in range(8):
            b = bar0 + k
            r = (progV if sec == "V" else prog)[k]
            last = k == 7
            if sec == "C":
                if k < 4:
                    if k == 0:
                        play(tr, N1, musicbox, b, sc, root + 12, pan=0.0, gain=1.0)
                        chord_pad(tr, b, [50, 57, 62, 63], 4, "choir", vowel="o", gain=0.45, att=1.5)
                    continue
                taiko_bar(tr, b, [(0, "odaiko", 0.8), (2, "odaiko", 0.7)] +
                          [(i * 0.5, "shime", 0.3 + 0.08 * (k - 4) + 0.03 * i) for i in range(8)], 0.75)
                play(tr, M("5z:4"), shamisen, b, sc, root - 12 + (k - 4) * 0, pan=0.3, gain=0.4 + 0.1 * (k - 4))
                bass_bar(tr, b, D_, "whole", 0.6)
                if last:
                    kit_bar(tr, b, "light", 0.55, fill="roll")
                continue
            style = {"A": "half", "B": "drive", "A2": "gallop", "V": "drive", "OUT": "double"}[sec]
            kit_bar(tr, b, style, 0.62, fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None),
                    crash=k % 4 == 0)
            taiko_bar(tr, b, [(0, "odaiko", 0.6)], 0.6)
            bass_bar(tr, b, r if r < 40 else r - 12, {"A": "half", "A2": "gallop"}.get(sec, "8ths"), 0.8)
            gtr_bar(tr, b, r, {"A": "open", "A2": "gallop"}.get(sec, "chug"), 0.45, drive=3.2)
            if k % 2 == 0 and sec in ("A", "A2", "V"):
                chord_pad(tr, b, [r + 12, r + 19, r + 24], 2, "choir", vowel="a" if sec != "V" else "o",
                          gain=0.5 if sec == "A" else 0.4)
            if sec == "OUT":
                riff(tr, b, r, RIFF, gain=0.85)
        if sec == "A":
            blow(tr, N, "hichiriki", bar0, sc, root, pan=0.15, gain=1.0)
        elif sec == "B":
            play(tr, N, musicbox, bar0, sc, root + 12, pan=0.35, gain=0.55, tag="ctr")
            play(tr, M("0:1 1:1 0:1 -1:1 | 0:2 2:2 | 3:1 2:1 1:1 0:1 | 1:4 | 0:1 1:1 0:1 -1:1 | 0:2 3:2 | "
                       "4:1 3:1 2:1 1:1 | 0:4", 8), biwa, bar0, sc, root, pan=-0.2, gain=1.1, vel=1.0)
            for k in range(0, 8, 2):
                chord_pad(tr, bar0 + k, [prog[k] + 24, prog[k] + 31], 2, "strings", gain=0.35)
        elif sec == "A2":
            play(tr, N, lead, bar0, sc, root, pan=0.15, gain=0.9)
            blow(tr, N, "hichiriki", bar0, sc, root, pan=-0.2, gain=0.5, tag="lead2")
        elif sec == "V":
            blow(tr, MV, "shinobue", bar0, sc, root, pan=0.2, gain=0.95)
            play(tr, shift(MV, -5), biwa, bar0, sc, root, pan=-0.25, gain=0.85, tag="lead2")
        elif sec == "OUT":
            blow(tr, shift(N1, 0), "hichiriki", bar0 + 4, sc, root, pan=0.2, gain=0.8)
    reverb(tr, rt60=2.4, wet=0.9)
    return tr


def t_final2(rng):
    """The finale, phase 2: the Body of Damned Time (D in, 7/8 in 2+2+3, eighth = 300 BPM, intro 4 + 56 bars). A
    clock of hyoshigi and kakko on every eighth, the band in 2+2+3, the koto running like clockwork, the choir
    singing Nashiko's motif slowed to one note a bar, the temple bell, the biwa with the motif in 7/8; a stretch
    where the clock slows and stops, then starts again."""
    tr = Track(60, 300, beats=7, rng=rng, send=0.15, intro=4)
    sc, root = IN, 62
    tr.sc, tr.root = sc, root
    D_, Eb, Bb, A_, G_ = 38, 39, 46, 45, 43
    prog = [D_, D_, Eb, D_, Bb, A_, G_, A_]
    SLOW = [(5, None), (6, 5), (4, None), (3, None), (4, None), (3, 2), (1, None), (0, None)]
    B7 = M("5:2 6:2 5:3 | 4:2 3:2 4:3 | 3:1 4:1 3:1 2:1 1:3 | 0:7 | 5:2 6:2 7:3 | 8:2 7:2 6:3 | "
           "5:1 6:1 5:1 4:1 3:3 | 3:7", 8, 7)

    def clock(b, g=1.0):
        for i in range(7):
            tr.add(drum("hyoshigi" if i in (0, 2, 4) else "kakko", rng), tr.at(b, i), 0.25 if i % 2 else -0.25,
                   g * (0.55 if i in (0, 2, 4) else 0.35), 0.1, 0.002, "clock")
    for b in range(4):                                                          # the clock alone, the bell
        clock(b, 0.8 + 0.1 * b)
    tr.add(bonsho(73.4, rng), tr.at(0), 0.0, 0.8, 0.5, 0.0, "bell")
    tr.add(swell(7 * tr.spb * 2, rng), tr.at(2), 0.0, 0.8, 0.3, 0.0, "fx")
    for b in range(4, 60):
        k = (b - 4) % 8
        r = prog[k]
        sec = "A" if b < 20 else "B" if b < 36 else "BRK" if b < 44 else "C"
        if sec == "BRK":
            j = b - 36
            if j == 0:
                tr.add(bonsho(73.4, rng, 12.0), tr.at(b), 0.0, 0.9, 0.5, 0.0, "bell")
                tr.add(sho([62, 63, 69, 70, 74], 8 * 7 * tr.spb, rng), tr.at(b), 0.0, 0.5, 0.5, 0.0, "pad")
                chord_pad(tr, b, [50, 57, 62], 6, "choir", vowel="u", gain=0.5, att=2.0)
                t, gap = tr.at(b), 0.2                                          # the clock slows, stops
                while gap < 1.6:
                    tr.add(drum("hyoshigi", rng), t, 0.0, 0.5, 0.2, 0.0, "clock")
                    t += gap
                    gap *= 1.18
            if j >= 6:
                clock(b, 0.4 + 0.3 * (j - 6))
                if j == 7:
                    tr.add(swell(7 * tr.spb, rng), tr.at(b), 0.0, 0.9, 0.3, 0.0, "fx")
            continue
        clock(b)
        for beat, g in ((0, 1.0), (2, 0.8), (4, 0.9)):
            tr.add(kit("kick", rng), tr.at(b, beat), 0.0, 0.6 * g, 0.0, 0.002, "drums")
        tr.add(kit("snare", rng), tr.at(b, 4), -0.05, 0.6, 0.06, 0.002, "drums")
        if sec == "C":
            tr.add(kit("snare", rng), tr.at(b, 6), -0.05, 0.45, 0.06, 0.002, "drums")
        if k == 0:
            tr.add(kit("crash", rng), tr.at(b), 0.35, 0.5, 0.06, 0.0, "drums")
        bass_bar(tr, b, r if r < 40 else r - 12, "7/8", 0.8)
        gtr_bar(tr, b, r, "7/8", 0.42 if sec != "A" else 0.3, drive=3.0)
        ch = [deg(sc, root, d) for d in (0, 2, 3, 5)] if r in (D_, A_) else [r + 24, r + 31, r + 36, r + 31 + 12]
        arp(tr, b, ch, [0, 1, 2, 3, 2, 1, 2], step=1.0, pan=0.35, gain=0.28, ring=0.6)
        if k % 2 == 0:
            chord_pad(tr, b, [r + 12, r + 19, r + 24], 2, "strings", gain=0.3)
        d, d2 = SLOW[k]
        if sec in ("A", "C"):                                                   # the motif, one note a bar
            mel = M("%d:7" % d) if d2 is None else M("%d:4 %d:3" % (d, d2))
            choir_note = [(t, ln, dd, a, o) for t, ln, dd, a, o in mel]
            for t, ln, dd, a, o in choir_note:
                m = deg(sc, root, dd)
                tr.add(pad([m, m - 12], ln * tr.spb + 0.4, rng, kind="choir", vowel="a", att=0.15), tr.at(b, t),
                       0.0, 0.7, 0.35, 0.0, "lead")
        if k == 0 and sec != "B":
            tr.add(bonsho(73.4, rng, 6.0), tr.at(b), 0.0, 0.45, 0.4, 0.0, "bell")
    play(tr, B7, biwa, 20, sc, root, pan=-0.15, gain=1.1, vel=1.0)
    play(tr, B7, biwa, 28, sc, root, pan=-0.15, gain=1.1, vel=1.0)
    blow(tr, shift(B7, 5), "shinobue", 28, sc, root - 12, pan=0.25, gain=0.5, tag="lead2")
    play(tr, B7, lead, 52, sc, root, pan=0.15, gain=0.8, tag="lead2")
    reverb(tr, rt60=2.4, wet=0.9)
    return tr


def _trav_band(tr, b0, rng, bars=8, style="drive", gain=1.0, strings=True, prog=None, arps=True, kick=True):
    """The travelers' theme accompaniment in D (ryo): triads on strings, koto broken chords, bass, kit."""
    prog = prog or TRAV_HR
    for k in range(bars):
        b = b0 + k
        r = prog[k % len(prog)]
        tri = TRIADS[r]
        if strings:
            chord_pad(tr, b, list(tri) + [tri[0] + 12], 1, "strings", gain=0.3 * gain)
        if arps:
            arp(tr, b, [tri[0], tri[1], tri[2], tri[0] + 12], [0, 1, 2, 3, 2, 1, 2, 1], pan=-0.35, gain=0.28 * gain)
        if kick:
            bass_bar(tr, b, r - 24, "8ths" if style != "light" else "half", 0.65 * gain)
            kit_bar(tr, b, style, 0.5 * gain, fill="taiko" if k % 4 == 3 else None, crash=k % 4 == 0)


def t_final3(rng):
    """The finale, phase 3: the Empress of Nothing (D in against D ryo, 160 BPM, intro 8 + 88 bars: the biggest track
    in the game). A choir alone with her motif and a horagai; the full band, strings and hichiriki; the biwa and the
    shamisen tremolo; a half-time B with the motif in augmentation; then the travelers' theme breaks through in D
    major (shakuhachi, then biwa and shinobue in harmony); her motif and their theme answer each other; everything
    falls away to the music box and a heartbeat; the taiko ensemble rebuilds it; the climax with choir, strings and
    lead guitar, the travelers' theme triumphant; the riff to the loop."""
    tr = Track(96, 160, rng=rng, send=0.16, intro=8)
    sc, root = IN, 62
    tr.sc, tr.root = sc, root
    D_, Eb, Bb, A_, G_ = 38, 39, 46, 45, 43
    N1, N2 = M(NASHIKO, 4), M(NASHIKO2, 4)
    N = N1 + [(t + 16, ln, d, a, o) for t, ln, d, a, o in N2]
    Nslow = [(t * 2, ln * 2, d, a, o) for t, ln, d, a, o in N1]               # augmented: 8 bars
    T = M(TRAV_A, 8)
    TB = M(TRAV_B, 8)
    prog = [D_, D_, Bb, A_, D_, Eb, Bb, A_]
    progB = [Bb, A_, G_, Eb, Bb, A_, Eb, A_]
    RIFF = [(0, 0, 0), (0.5, 0, 0), (0.75, 0, 0), (1, 1, 0), (1.5, 0, 0), (2, 7, 0), (2.5, 5, 0), (3, 8, 1),
            (3.5, 7, 0)]
    # intro: the choir alone with her motif (augmented), o-daiko on the bars, horagai; a roll into the band
    for t, ln, d, a, o in Nslow:
        m = deg(sc, root, d)
        tr.add(pad([m, m - 12, m + 12], ln * tr.spb + 0.5, rng, kind="choir", vowel="a", att=0.3), tr.at(0) + t * tr.spb,
               0.0, 0.8, 0.45, 0.0, "lead")
    chord_pad(tr, 0, [38, 45, 50], 8, "choir", vowel="o", gain=0.5, att=2.0)
    blow(tr, M("0:3 -1:1 | 0:4"), "horagai", 0, sc, root - 12, pan=-0.4, gain=0.5, send=0.6)
    blow(tr, M("0:3 1:1 | 0:4"), "horagai", 4, sc, root - 12, pan=0.4, gain=0.5, send=0.6)
    for b in range(8):
        taiko_bar(tr, b, [(0, "odaiko", 0.9)] + ([(2, "odaiko", 0.6)] if b >= 4 else []), 0.5)
    taiko_bar(tr, 6, [(i * 0.5, "shime", 0.3 + 0.05 * i) for i in range(8)], 0.7)
    kit_bar(tr, 7, "light", 0.6, fill="roll")
    tr.add(swell(4 * tr.spb, rng), tr.at(7), 0.0, 1.0, 0.3, 0.0, "fx")

    def dark_bar(b, r, style, k, nb, gstyle="chug", riff_g=0.0):
        last = k == nb - 1
        kit_bar(tr, b, style, 0.62, fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None),
                crash=k % 4 == 0)
        taiko_bar(tr, b, [(0, "odaiko", 0.65)] + ([(2, "odaiko", 0.45)] if style in ("gallop", "half") else []),
                  0.65)
        bass_bar(tr, b, r if r < 40 else r - 12, {"half": "whole", "gallop": "gallop"}.get(style, "8ths"), 0.8)
        gtr_bar(tr, b, r, gstyle, 0.45, drive=3.4)
        if riff_g:
            riff(tr, b, r, RIFF, gain=riff_g, pan=-0.3)

    # 8-15 A: the band, strings, the hichiriki with the motif
    for k in range(8):
        dark_bar(8 + k, prog[k], "gallop", k, 8, "gallop")
        if k % 2 == 0:
            chord_pad(tr, 8 + k, [prog[k] + 24, prog[k] + 31, prog[k] + 36], 2, "strings", gain=0.4)
    blow(tr, N, "hichiriki", 8, sc, root, pan=0.15, gain=1.0)
    # 16-23 A2: biwa lead (the motif with bends), shamisen tremolo, choir pads
    for k in range(8):
        dark_bar(16 + k, prog[k], "drive", k, 8, "chug", 0.0)
        if k % 2 == 0:
            chord_pad(tr, 16 + k, [prog[k] + 12, prog[k] + 19, prog[k] + 24], 2, "choir", vowel="a", gain=0.45)
    play(tr, M("5~:1.5 6:.5 5:1 4:1 | 3~:3 r:1 | 4:1 3:.5 2:.5 1:1 0:1 | 1~:2 0:2 | 5:1.5 6:.5 7:1 8:1 | "
               "9~:3 r:1 | 8:1 7:.5 6:.5 5:1 4:1 | 3~:4", 8), biwa, 16, sc, root, pan=-0.15, gain=1.1, vel=1.0)
    play(tr, M("5z:4 | 4z:4 | 3z:4 | 1z:2 0z:2 | 5z:4 | 7z:4 | 6z:4 | 5z:4", 8), shamisen, 16, sc, root - 12,
         pan=0.35, gain=0.5, tag="ctr")
    # 24-31 B: half time; the choir sings the motif augmented; the lead guitar carries the 'veil' line
    for k in range(8):
        dark_bar(24 + k, progB[k], "half", k, 8, "open")
    for t, ln, d, a, o in Nslow:
        m = deg(sc, root, d)
        tr.add(pad([m, m + 12], ln * tr.spb + 0.4, rng, kind="choir", vowel="o", att=0.25), tr.at(24) + t * tr.spb,
               0.0, 0.75, 0.4, 0.0, "lead")
    play(tr, M("7:2 6:1 5:1 | 4:2 3:2 | 2:1 3:1 4:1 5:1 | 3:4 | 7:2 8:1 9:1 | 10~:2 9:1 8:1 | 7:1 6:1 5:1 4:1 | "
               "5:4", 8), lead, 24, sc, root - 12, pan=0.2, gain=0.75, tag="lead2")
    # 32-47 C: the travelers' theme breaks through (D ryo): the shakuhachi, then biwa and shinobue in harmony
    tr.add(kit("crash", rng), tr.at(32), 0.0, 0.5, 0.1, 0.0, "drums")
    tr.sc, tr.root = RYO, 62                      # their key while their theme plays (the helpers follow it)
    _trav_band(tr, 32, rng, 8, "drive", 1.0)
    _trav_band(tr, 40, rng, 8, "drive", 1.1)
    for k in range(16):
        r = TRAV_HR[k % 8]
        gtr_bar(tr, 32 + k, r - 24 if r - 24 >= 38 else r - 12, "chug" if k >= 8 else "half", 0.36, drive=2.4)
        taiko_bar(tr, 32 + k, [(0, "odaiko", 0.5)], 0.6)
    blow(tr, T, "shakuhachi", 32, RYO, 62, pan=0.1, gain=1.05)
    play(tr, T, biwa, 40, RYO, 62, pan=-0.2, gain=1.0, vel=1.0)
    blow(tr, T, "shinobue", 40, RYO, 74, pan=0.25, gain=0.75, tag="lead2")
    blow(tr, shift(T, -2), "shakuhachi", 40, RYO, 74, pan=0.0, gain=0.4, tag="ctr")
    # 48-55 D: her motif and their theme answer each other, two bars each
    for j in range(4):
        b = 48 + 2 * j
        tr.sc, tr.root = (sc, root) if j % 2 == 0 else (RYO, 62)
        if j % 2 == 0:
            for k in range(2):
                dark_bar(b + k, [D_, Eb][k], "gallop", k + 2 * j, 8, "gallop")
            chord_pad(tr, b, [50, 57, 62, 63], 2, "choir", vowel="a", gain=0.55)
            play(tr, cut(N1, 0, 2) if j == 0 else cut(N2, 0, 2), lead, b, sc, root, pan=0.15, gain=0.9)
        else:
            _trav_band(tr, b, rng, 2, "drive", 1.0, prog=[62, 67] if j == 1 else [59, 69])
            for k in range(2):
                gtr_bar(tr, b + k, 38 if k == 0 else 43, "chug", 0.36, drive=2.4)
            blow(tr, cut(T, 0, 2) if j == 1 else cut(T, 4, 6), "shinobue", b, RYO, 74, pan=0.2, gain=0.95)
            play(tr, cut(T, 0, 2) if j == 1 else cut(T, 4, 6), biwa, b, RYO, 62, pan=-0.2, gain=0.8, tag="lead2")
    tr.sc, tr.root = sc, root
    # 56-63: everything falls away: the music box and a heartbeat; then the taiko ensemble rebuilds it
    play(tr, N1, musicbox, 56, sc, root + 12, pan=0.0, gain=1.0)
    for b in range(56, 60):
        taiko_bar(tr, b, [(0, "odaiko", 0.6), (0.4, "odaiko", 0.35)], 0.7)
    tr.add(sho([62, 63, 69, 70], 4 * 4 * tr.spb, rng), tr.at(56), 0.0, 0.45, 0.5, 0.0, "pad")
    for b in range(60, 64):
        j = b - 60
        taiko_bar(tr, b, [(0, "odaiko", 0.9), (1.5, "odaiko", 0.6), (2, "odaiko", 0.8), (3, "odaiko_rim", 0.6)] +
                  [(i * 0.5, "shime", 0.35 + 0.1 * j) for i in range(8)] +
                  ([(i * 0.25, "kakko", 0.25 + 0.1 * j) for i in range(16)] if j >= 2 else []), 0.75)
        tr.add(bass(D_, 4 * tr.spb, rng), tr.at(b), 0.0, 0.5 + 0.1 * j, 0.0, 0.0, "bass")
    chord_pad(tr, 60, [50, 57, 62, 69], 4, "choir", vowel="a", gain=0.5, att=3.0)
    tr.add(swell(4 * tr.spb, rng), tr.at(63), 0.0, 1.0, 0.3, 0.0, "fx")
    # 64-71 E: the climax, double time: the motif harmonised (choir, strings, lead guitar, hichiriki)
    for k in range(8):
        dark_bar(64 + k, prog[k], "double", k, 8, "chug", 0.5)
        chord_pad(tr, 64 + k, [prog[k] + 24, prog[k] + 31, prog[k] + 36], 1, "strings", gain=0.4)
        chord_pad(tr, 64 + k, [prog[k] + 12, prog[k] + 19, prog[k] + 24], 1, "choir", vowel="a", gain=0.4)
    play(tr, N, lead, 64, sc, root, pan=0.2, gain=0.9)
    blow(tr, N, "hichiriki", 64, sc, root, pan=-0.15, gain=0.7, tag="lead2")
    play(tr, shift(N, -2), biwa, 64, sc, root, pan=-0.35, gain=0.6, tag="ctr")
    # 72-79: the travelers' theme triumphant, the whole ensemble with the choir
    tr.add(kit("crash", rng), tr.at(72), -0.3, 0.6, 0.1, 0.0, "drums")
    tr.sc, tr.root = RYO, 62
    _trav_band(tr, 72, rng, 8, "double", 1.15)
    for k in range(8):
        r = TRAV_HR[k]
        gtr_bar(tr, 72 + k, r - 24 if r - 24 >= 38 else r - 12, "chug", 0.4, drive=2.6)
        tri = TRIADS[r]
        chord_pad(tr, 72 + k, [tri[0] - 12, tri[1] - 12, tri[2] - 12], 1, "choir", vowel="a", gain=0.45)
        taiko_bar(tr, 72 + k, [(0, "odaiko", 0.7), (2, "odaiko", 0.5)], 0.65)
    blow(tr, T, "shinobue", 72, RYO, 74, pan=0.2, gain=0.9)
    play(tr, T, lead, 72, RYO, 62, pan=-0.15, gain=0.75, tag="lead2")
    play(tr, T, biwa, 72, RYO, 62, pan=-0.35, gain=0.75, tag="lead2")
    blow(tr, shift(T, -2), "shakuhachi", 72, RYO, 74, pan=0.35, gain=0.45, tag="ctr")
    tr.sc, tr.root = sc, root
    # 80-95 F: her answer, darker (the B line on the lead), then the riff into the loop
    for k in range(16):
        r = (progB if k < 8 else prog)[k % 8]
        dark_bar(80 + k, r, "drive" if k < 8 else "gallop", k % 8, 8, "chug" if k < 8 else "gallop",
                 0.0 if k < 8 else 0.85)
        if k % 2 == 0 and k < 8:
            chord_pad(tr, 80 + k, [r + 12, r + 19, r + 24], 2, "choir", vowel="o", gain=0.45)
    play(tr, M("4:2 3:1 2:1 | 3:1.5 2:.5 1:2 | 2:1 3:1 4:1 5:1 | 4:4 | 7:2 6:1 5:1 | 4:1.5 3:.5 2:2 | "
               "1:1 2:1 1:1 0:1 | 0:4", 8), biwa, 80, sc, root, pan=-0.15, gain=1.05, vel=1.0)
    blow(tr, M("5:4 | 4:4 | 3:4 | 4:4 | 5:4 | 6:4 | 5:2 4:2 | 3:4", 8), "hichiriki", 80, sc, root, pan=0.25,
         gain=0.55, tag="ctr")
    blow(tr, N1, "hichiriki", 88, sc, root, pan=0.2, gain=0.8)
    reverb(tr, rt60=2.4, wet=0.9)
    return tr


def t_orochi(rng):
    """The post-game superboss: the Orochi, a sea serpent (E hirajoshi: E F# G B C, 12/8 at 126, intro 4 + 40
    bars). A storm (waves, thunder, a horagai); an eight-note 'heads' figure on biwa and guitar running against the
    12/8 bar (it lines up again every two bars); a swelling hichiriki; a choir and strings in the half-time B; a
    thunder break; the shinobue high over everything."""
    tr = Track(44, 126, rng=rng, send=0.16, intro=4)
    sc, root = HIRA, 52
    E_, C_, G_, B_, Fs = 40, 48, 43, 47, 42
    prog = [E_, E_, C_, B_, E_, E_, C_, Fs]
    progB = [C_, B_, C_, E_, C_, B_, G_, B_]
    # The heads figure in scale steps over the chord root (over E: E B G C B G F# E). It was semitones, which put
    # Eb / Ab / D / C# against the hirajoshi lead over the C, B, F# and G chords (user: "the two layers... sound bad").
    HEADS = [0, 3, 2, 4, 3, 2, 1, 0]

    def in_sc(m):
        return (m - root) % 12 in sc

    def hnote(r, j):
        pc = (r - root) % 12
        return deg(sc, r - pc, sc.index(pc) + HEADS[j]) + 12

    def power(r):                                   # root + fifth only where the fifth is in the scale (F#, G: 4th)
        return (0, 7, 12) if in_sc(r + 7) else (0, 5, 12)
    MO8 = M("3:3 4:1 | 3:1.5 2:.5 1:2 | 2:2 3:2 | 0:4 | 3:3 4:1 | 5:1.5 6:.5 7:2 | 6:1 5:1 4:1 3:1 | 3:4", 8)
    MW = M("5:3 6:1 | 7:2 6:2 | 5:2 4:1 3:1 | 4:4 | 5:3 6:1 | 7:2 8:2 | 7:1 6:1 5:1 4:1 | 5:4", 8)

    def heads(b, r, g=1.0, inst=biwa, pan=-0.2):
        for i in range(12):                                                     # 8 against 12: two bars per cycle
            j = (b * 12 + i) % 8
            tr.add(inst(hnote(r, j), 0.5, rng, vel=1.0), tr.at(b, i / 3), pan,
                   0.7 * g * (1.1 if j == 0 else 0.85) * float(np.exp(rng.normal(0, 0.05))), None, 0.003, "riff")

    def shuffle_bar(b, r, k, nb, half=False):
        last = k == nb - 1
        kit_bar(tr, b, "shuffle" if not half else "half", 0.6,
                fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None), crash=k % 4 == 0)
        bass_bar(tr, b, r if r < 40 else r - 12, "shuffle" if not half else "whole", 0.8, fifth=power(r)[1])
        gtr_bar(tr, b, r, "shuffle" if not half else "open", 0.42, drive=3.0, chord=power(r))
        taiko_bar(tr, b, [(0, "odaiko", 0.7), (2, "odaiko", 0.5)], 0.6)
    wl, wr = waves(tr.n, rng, 0.2, period=5.1)
    tr.ambience(wl, wr, 1.0)
    for t in (0.2, 3.1):
        tr.add(thunder(rng), tr.at(0) + t, rng.uniform(-0.5, 0.5), 0.8, 0.3, 0.0, "amb")
    blow(tr, M("0:3 -1:1 | 0:4"), "horagai", 1, sc, root, pan=0.3, gain=0.5, send=0.6)
    for b in range(4):
        taiko_bar(tr, b, [(0, "odaiko", 0.8)] + ([(i / 3, "shime", 0.25 + 0.06 * i) for i in range(12)]
                                                  if b == 3 else []), 0.75)
    for b in (2, 3):
        heads(b, E_, 0.6 + 0.2 * (b - 2))
    for bar0, sec in ((4, "A"), (12, "B"), (20, "BRK"), (24, "C"), (36, "A2")):
        nb = {"BRK": 4, "C": 12}.get(sec, 8)
        for k in range(nb):
            b = bar0 + k
            r = (progB if sec == "B" else prog)[k % 8]
            if sec == "BRK":
                taiko_bar(tr, b, [(0, "odaiko", 1.0), (1, "odaiko", 0.6), (2, "odaiko", 0.9), (2 + 2 / 3, "odaiko",
                                  0.6), (3, "odaiko", 0.8)], 0.75)
                if k in (0, 2):
                    tr.add(thunder(rng), tr.at(b, 0.5), rng.uniform(-0.5, 0.5), 0.9, 0.3, 0.0, "amb")
                heads(b, E_ - 12 + 12, 0.7, pan=0.2)
                if k == nb - 1:
                    kit_bar(tr, b, "light", 0.5, fill="roll")
                continue
            shuffle_bar(b, r, k % 8, nb, half=sec == "B")
            if sec in ("A", "A2", "C"):
                heads(b, r, 0.55 if sec != "A2" else 0.8)
            if sec == "B" and k % 2 == 0:
                f5 = power(r)[1]
                chord_pad(tr, b, [r + 12, r + 12 + f5, r + 24], 2, "choir", vowel="o", gain=0.5)
                chord_pad(tr, b, [r + 24, r + 24 + f5], 2, "strings", gain=0.35)
            if sec == "C" and k % 4 == 0:
                tr.add(thunder(rng), tr.at(b, 1), rng.uniform(-0.5, 0.5), 0.5, 0.3, 0.0, "amb")
        if sec == "A":
            blow(tr, MO8, "hichiriki", bar0, sc, root + 12, pan=0.2, gain=1.0)
        elif sec == "B":
            play(tr, MW, biwa, bar0, sc, root + 12, pan=-0.15, gain=1.05, vel=1.0)
            blow(tr, shift(MW, -2), "shakuhachi", bar0, sc, root + 12, pan=0.3, gain=0.5, tag="ctr")
        elif sec == "C":
            blow(tr, MW, "shinobue", bar0, sc, root + 12, pan=0.2, gain=0.95)
            play(tr, MO8, lead, bar0 + 4, sc, root + 12, pan=-0.2, gain=0.7, tag="lead2")
            blow(tr, M("0:3 1:1 | 0:4"), "horagai", bar0 + 10, sc, root, pan=-0.4, gain=0.45, send=0.5)
            for k in range(0, 12, 2):
                chord_pad(tr, bar0 + k, [prog[k % 8] + 12, prog[k % 8] + 19, prog[k % 8] + 24], 2, "choir",
                          vowel="a", gain=0.4)
        elif sec == "A2":
            blow(tr, MO8, "hichiriki", bar0, sc, root + 12, pan=0.2, gain=0.9)
            play(tr, shift(MO8, -2), biwa, bar0, sc, root + 12, pan=-0.25, gain=0.75, tag="lead2")
    reverb(tr, rt60=2.6, wet=0.9)
    return tr


def t_okura(rng):
    """The post-game superboss at Shiro Hiruma: Oni no Okura, Akuma's daughter (C in: C Db F G Ab, 104 BPM, intro 4
    + 44 bars). Doom: horagai and a low choir drone, a massive o-daiko ensemble, low guitars in half time (C, Db);
    the gallop; a choir chanting on the beat; a taiko solo; everything at once."""
    tr = Track(48, 104, rng=rng, send=0.15, intro=4)
    sc, root = IN, 48
    tr.sc, tr.root = sc, root
    C_, Db, Ab, G_, F_ = 36, 37, 44, 43, 41
    prog = [C_, C_, Db, C_, Ab, G_, Db, C_]
    MK = M("5:2 6:2 | 5:1 4:1 3:2 | 4:2 3:1 1:1 | 0:4 | 5:2 6:1 7:1 | 8~:3 7:1 | 6:1 5:1 4:1 3:1 | 5:4", 8)
    RIFF = [(0, 0, 0), (0.5, 0, 0), (0.75, 1, 0), (1, 0, 0), (2, 0, 0), (2.5, 7, 0), (3, 6, 0), (3.5, 1, 0)]
    blow(tr, M("0:4 | -1:2 0:2"), "horagai", 0, sc, root - 12 + 12, pan=-0.35, gain=0.6, send=0.6)
    blow(tr, M("0:4 | 1:2 0:2"), "horagai", 2, sc, root + 7 - 12 + 12, pan=0.35, gain=0.5, send=0.6)
    chord_pad(tr, 0, [36, 43, 48], 4, "choir", vowel="u", gain=0.6, att=2.5)
    for b in range(4):
        taiko_bar(tr, b, [(0, "odaiko", 1.0), (2, "odaiko", 0.8), (3, "odaiko", 0.6), (3.5, "odaiko", 0.8)], 0.8)
    tr.add(bell(196, 6.0, rng, beat=1.8), tr.at(0), 0.4, 0.5, 0.4, 0.0, "bell")
    kit_bar(tr, 3, "light", 0.55, fill="roll")
    for bar0, sec in ((4, "A"), (12, "B"), (20, "C"), (28, "BRK"), (32, "D"), (40, "OUT")):
        nb = 4 if sec == "BRK" else 8
        for k in range(nb):
            b = bar0 + k
            r = prog[k % 8]
            last = k == nb - 1
            if sec == "BRK":
                taiko_bar(tr, b, [(0, "odaiko", 1.0), (0.5, "shime", 0.6), (0.75, "shime", 0.5), (1, "odaiko", 0.7),
                                  (1.5, "shime", 0.6), (2, "odaiko", 0.9), (2.5, "odaiko", 0.6),
                                  (3, "shime", 0.7), (3.25, "shime", 0.7), (3.5, "odaiko", 0.9),
                                  (3.75, "odaiko_rim", 0.6)], 0.8)
                if k == 0:
                    tr.add(bell(196, 6.0, rng, beat=1.8), tr.at(b), 0.4, 0.5, 0.4, 0.0, "bell")
                if last:
                    kit_bar(tr, b, "light", 0.55, fill="roll")
                continue
            style = {"A": "half", "B": "gallop", "C": "drive", "D": "gallop", "OUT": "double"}[sec]
            kit_bar(tr, b, style, 0.62, fill="taiko" if k % 4 == 3 and not last else ("snare" if last else None),
                    crash=k % 4 == 0)
            taiko_bar(tr, b, [(0, "odaiko", 0.8), (2, "odaiko", 0.6)] + ([(1, "odaiko", 0.5), (3, "odaiko", 0.5)]
                                                                         if sec in ("C", "D") else []), 0.7)
            bass_bar(tr, b, r if r < 40 else r - 12, {"A": "whole", "B": "gallop", "D": "gallop"}.get(sec, "8ths"),
                     0.8)
            gtr_bar(tr, b, r + 12 if r < 40 else r, {"A": "open", "B": "gallop", "D": "gallop"}.get(sec, "chug"),
                    0.46, drive=3.6)
            if sec in ("B", "OUT"):
                riff(tr, b, r + 12 if r < 40 else r, RIFF, gain=0.6 if sec == "B" else 0.85, pan=-0.3)
            if sec == "C":                                                       # the chant: choir hits on the beat
                for beat in (0, 1, 2, 3):
                    tr.add(pad([r + 12, r + 12 + fifth(tr, r)], 0.45 * tr.spb + 0.1, rng, kind="choir", vowel="o", att=0.02,
                               rel=0.1), tr.at(b, beat), 0.0, 0.8 if beat == 0 else 0.6, 0.3, 0.003, "pad")
            if sec == "A" and k % 4 == 0:
                chord_pad(tr, b, [r + 12, r + 19], 4, "choir", vowel="u", gain=0.55)
        if sec == "A":
            play(tr, MK, biwa, bar0, sc, root + 12, pan=-0.15, gain=1.1, vel=1.0)
            blow(tr, shift(MK, 0), "hichiriki", bar0 + 4, sc, root + 12, pan=0.25, gain=0.5, tag="lead2")
        elif sec == "B":
            play(tr, M("5z:4 | 6z:2 5z:2 | 4z:4 | 3z:4 | 5z:4 | 7z:2 8z:2 | 7z:2 6z:2 | 5z:4", 8), shamisen, bar0,
                 sc, root + 12, pan=0.3, gain=0.6)
            blow(tr, MK, "hichiriki", bar0, sc, root + 12, pan=-0.1, gain=0.9)
        elif sec == "C":
            play(tr, MK, lead, bar0, sc, root + 12, pan=0.2, gain=0.85)
        elif sec == "D":
            play(tr, MK, lead, bar0, sc, root + 12, pan=0.2, gain=0.8)
            play(tr, shift(MK, -2), biwa, bar0, sc, root + 12, pan=-0.25, gain=0.8, tag="lead2")
            for k in range(0, 8, 2):
                chord_pad(tr, bar0 + k, [prog[k] + 24, prog[k] + 31, prog[k] + 36], 2, "strings", gain=0.4)
        elif sec == "OUT":
            blow(tr, M("0:4 | -1:2 0:2"), "horagai", bar0 + 4, sc, root, pan=-0.3, gain=0.5, send=0.5)
    reverb(tr, rt60=2.8, wet=0.9, bright=3200)
    return tr


def t_travelers(rng):
    """The travelers' theme, "Eight Roads, One Dawn" (D ryo, 112 BPM, intro 4 + 36 bars): the title screen, the
    join-up on the Plains of Thunder and Sayo's long table. A koto-and-sho opening with a shakuhachi call; A on the
    shakuhachi; A' koto and shinobue with the strings and a light kit; B (the bridge) on the biwa; A'' everything,
    the shinobue and biwa in harmony with the choir; a cadence."""
    tr = Track(40, 112, rng=rng, send=0.22, intro=4)
    T, TB = M(TRAV_A, 8), M(TRAV_B, 8)
    sc, root = RYO, 62
    tr.sc, tr.root = sc, root
    for b in range(4):
        r = [62, 67, 59, 69][b]
        tri = TRIADS[r]
        arp(tr, b, [tri[0] - 12, tri[1] - 12, tri[2] - 12, tri[0]], [0, 1, 2, 3, 2, 1, 2, 1], pan=-0.3, gain=0.35)
        tr.add(bass_koto(snap(tr, r - 24), 2.5, rng), tr.at(b), 0.0, 0.7, 0.1, 0.0, "bass")
        taiko_bar(tr, b, [(0, "odaiko", 0.35 + 0.15 * b)], 0.7)
    tr.add(sho([62, 66, 69, 71, 76], 4 * 4 * tr.spb, rng), tr.at(0), 0.0, 0.5, 0.4, 0.0, "pad")
    blow(tr, M("0:2 3:2 | 5:8 | r:4"), "shakuhachi", 0, sc, root, pan=0.15, gain=0.7, send=0.5)
    # 4-11 A: the shakuhachi with the theme, koto and jushichigen
    for k in range(8):
        r = TRAV_HR[k]
        tri = TRIADS[r]
        arp(tr, 4 + k, [tri[0] - 12, tri[1] - 12, tri[2] - 12, tri[0]], [0, 1, 2, 3, 2, 1, 2, 1], pan=-0.3, gain=0.33)
        tr.add(bass_koto(snap(tr, r - 24), 2.4, rng), tr.at(4 + k), 0.0, 0.7, 0.1, 0.004, "bass")
        tr.add(bass_koto(snap(tr, r - 17), 1.0, rng), tr.at(4 + k, 2.5), 0.0, 0.45, 0.1, 0.004, "bass")
        taiko_bar(tr, 4 + k, [(0, "odaiko", 0.45)] + ([(2, "shime", 0.35), (3, "shime", 0.3)] if k >= 4 else []), 0.7)
    blow(tr, T, "shakuhachi", 4, sc, root, pan=0.1, gain=1.0)
    # 12-19 A': koto melody, shinobue counter, strings, a light kit
    _trav_band(tr, 12, rng, 8, "light", 0.9)
    play(tr, T, koto, 12, sc, root + 12, pan=-0.15, gain=1.0)
    blow(tr, M("r:4 | 3:4 | 4:2 3:2 | 1:4 | r:4 | 2:2 3:2 | 4:2 3:2 | 5:4", 8), "shinobue", 12, sc, root + 12,
         pan=0.3, gain=0.5, tag="ctr")
    # 20-27 B: the bridge on the biwa, strings, the kit drives
    _trav_band(tr, 20, rng, 8, "drive", 0.9, prog=TRAV_BR)
    play(tr, TB, biwa, 20, sc, root, pan=-0.15, gain=1.05, vel=1.0)
    blow(tr, shift(TB, -2), "shakuhachi", 20, sc, root + 12, pan=0.3, gain=0.45, tag="ctr")
    # 28-35 A'': all together
    tr.add(kit("crash", rng), tr.at(28), 0.3, 0.5, 0.1, 0.0, "drums")
    _trav_band(tr, 28, rng, 8, "drive", 1.05)
    for k in range(8):
        tri = TRIADS[TRAV_HR[k]]
        if k % 2 == 0:
            chord_pad(tr, 28 + k, [tri[0] - 12, tri[1] - 12, tri[2] - 12], 2, "choir", vowel="a", gain=0.4)
        taiko_bar(tr, 28 + k, [(0, "odaiko", 0.55), (2, "odaiko", 0.35)], 0.6)
    blow(tr, T, "shinobue", 28, sc, root + 12, pan=0.2, gain=0.9)
    play(tr, T, biwa, 28, sc, root, pan=-0.2, gain=0.85, vel=1.0, tag="lead2")
    blow(tr, shift(T, -2), "shakuhachi", 28, sc, root + 12, pan=0.0, gain=0.4, tag="ctr")
    # 36-39: the cadence (D - G - A - D), a ritardando feel from long notes, then back to A
    for k, r in enumerate((62, 67, 69, 62)):
        tri = TRIADS[r]
        chord_pad(tr, 36 + k, list(tri) + [tri[0] + 12], 1, "strings", gain=0.35)
        tr.add(bass_koto(snap(tr, r - 24), 2.4, rng), tr.at(36 + k), 0.0, 0.7, 0.1, 0.0, "bass")
        kit_bar(tr, 36 + k, "light", 0.45, crash=k == 0, fill="taiko" if k == 3 else None)
        arp(tr, 36 + k, [tri[0] - 12, tri[1] - 12, tri[2] - 12, tri[0]], [0, 1, 2, 3, 2, 1, 2, 1], pan=-0.3, gain=0.3)
    blow(tr, M("5:2 4:1 3:1 | 4:2 5:2 | 6:2 7:2 | 5:4", 4), "shinobue", 36, sc, root + 12, pan=0.2, gain=0.8)
    play(tr, M("3:2 2:1 1:1 | 2:2 3:2 | 4:2 4:2 | 3:4", 4), koto, 36, sc, root + 12, pan=-0.2, gain=0.6, tag="ctr")
    reverb(tr, rt60=2.2, wet=1.0)
    return tr


def t_ending(rng):
    """The ending, "Lanterns on the River" (D ryo, 72 BPM, 40 bars): the capital's river at night in 1123, THE END.
    A koto alone with the travelers' theme; the shakuhachi takes it with the koto under it; her motif, softened into
    the yo scale on a sho and a shinobue (a requiem, not a threat); the bridge; the theme once more with strings and a
    soft choir; rin bells and the koto's last notes."""
    tr = Track(40, 72, rng=rng, send=0.32)
    T, TB = M(TRAV_A, 8), M(TRAV_B, 8)
    sc, root = RYO, 62
    tr.sc, tr.root = sc, root
    for b in range(4):
        r = [62, 67, 59, 62][b]
        tri = TRIADS[r]
        arp(tr, b, [tri[0] - 12, tri[1] - 12, tri[2] - 12, tri[0]], [0, 2, 1, 3, 2, 1, 2, None], pan=-0.25, gain=0.38)
        tr.add(bass_koto(snap(tr, r - 24), 3.0, rng), tr.at(b), 0.0, 0.55, 0.15, 0.0, "bass")
    tr.add(bell(float(hz(86)), 6.0, rng, ratios=(1.0, 2.71, 5.15), beat=0.6), tr.at(0), 0.4, 0.4, 0.5, 0.0, "bell")
    play(tr, T, koto, 4, sc, root + 12, pan=0.0, gain=1.0, vel=0.85)
    for k in range(8):
        r = TRAV_HR[k]
        tr.add(bass_koto(snap(tr, r - 24), 3.0, rng), tr.at(4 + k), 0.0, 0.55, 0.15, 0.0, "bass")
        tr.add(koto(r - 12, 2.0, rng, vel=0.7), tr.at(4 + k, 2), -0.35, 0.25, None, 0.008, "arp")
    blow(tr, T, "shakuhachi", 12, sc, root, pan=0.1, gain=0.95)
    for k in range(8):
        r = TRAV_HR[k]
        tri = TRIADS[r]
        arp(tr, 12 + k, [tri[0] - 12, tri[1] - 12, tri[2] - 12, tri[0]], [0, 2, 1, 3, 2, 1, 2, 1], pan=-0.3, gain=0.3)
        tr.add(bass_koto(snap(tr, r - 24), 3.0, rng), tr.at(12 + k), 0.0, 0.6, 0.15, 0.0, "bass")
        if k % 2 == 0:
            tr.add(sho(keyed(tr, list(tri) + [tri[0] + 12]), 2 * 4 * tr.spb, rng), tr.at(12 + k), 0.0, 0.2, 0.4, 0.0, "pad")
    # 20-23: Nashiko's motif in the yo scale (her sigh without its sting), shinobue over a sho
    blow(tr, M(NASHIKO, 4), "shinobue", 20, YO, 62, pan=0.2, gain=0.6)
    for b, cl in ((20, [62, 67, 69, 74]), (22, [59, 64, 67, 71])):
        tr.add(sho(keyed(tr, cl), 2 * 4 * tr.spb + 0.5, rng), tr.at(b), 0.0, 0.45, 0.4, 0.0, "pad")
        tr.add(bass_koto(cl[0] - 12, 5.0, rng), tr.at(b), 0.0, 0.5, 0.2, 0.0, "bass")
    tr.add(bell(float(hz(81)), 6.0, rng, ratios=(1.0, 2.71, 5.15), beat=0.6), tr.at(22), -0.4, 0.35, 0.5, 0.0, "bell")
    # 24-31: the bridge (first half) on the koto with strings; 28-31 the shakuhachi
    for k in range(8):
        r = TRAV_BR[k]
        tri = TRIADS[r]
        chord_pad(tr, 24 + k, list(tri), 1, "strings", gain=0.25, att=0.8)
        tr.add(bass_koto(snap(tr, r - 24), 3.0, rng), tr.at(24 + k), 0.0, 0.55, 0.15, 0.0, "bass")
    play(tr, cut(TB, 0, 4), koto, 24, sc, root + 12, pan=-0.1, gain=0.95)
    blow(tr, cut(TB, 4, 8), "shakuhachi", 28, sc, root, pan=0.1, gain=0.9)
    # 32-39: the theme's consequent once more, strings and a soft choir; the koto's last notes; rin
    for k in range(8):
        r = TRAV_HR[4 + k % 4] if k < 4 else [62, 67, 69, 62][k - 4]
        tri = TRIADS[r]
        chord_pad(tr, 32 + k, list(tri), 1, "strings", gain=0.28, att=0.8)
        if k % 2 == 0:
            chord_pad(tr, 32 + k, [tri[0] - 12, tri[2] - 12], 2, "choir", vowel="u", gain=0.3, att=1.0)
        tr.add(bass_koto(snap(tr, r - 24), 3.0, rng), tr.at(32 + k), 0.0, 0.55, 0.15, 0.0, "bass")
    blow(tr, cut(T, 4, 8), "shinobue", 32, sc, root + 12, pan=0.15, gain=0.75)
    play(tr, cut(T, 4, 8), koto, 32, sc, root, pan=-0.2, gain=0.55, tag="ctr")
    play(tr, M("5:2 3:2 | 4:2 2:2 | 3:1 2:1 1:1 0:1 | 0:4", 4), koto, 36, sc, root + 12, pan=0.0, gain=0.85)
    for b in (36, 38):
        tr.add(bell(float(hz(deg(sc, root + 24, 0 if b == 36 else 3))), 6.0, rng, ratios=(1.0, 2.71, 5.15),
                    beat=0.6), tr.at(b, 2), rng.uniform(-0.5, 0.5), 0.35, 0.5, 0.0, "bell")
    il, ir = insects(tr.n, rng, 0.4), insects(tr.n, rng, 0.4)
    wl, wr = waves(tr.n, rng, 1.0, period=9.0)
    tr.ambience(il + 0.03 * lowpass(wl, 400), ir + 0.03 * lowpass(wr, 400), 0.8, send=0.2)
    reverb(tr, rt60=3.2, wet=1.0)
    return tr


# ---- cues: an intro, then a quiet loop body (looppoint = the intro's length)
def cue(intro_fn, body_fn, rng, lufs_intro, lufs_body):
    a = intro_fn(rng)
    b = body_fn(rng)
    xa, xb = master(a, lufs_intro), master(b, lufs_body)
    return np.concatenate([xa, xb], axis=1), xa.shape[1]


def c_victory_intro(rng):
    """A fanfare (D ryo, 132 BPM): a taiko pickup, the band's hit, biwa, shinobue and koto up the scale, a held
    chord with a koto glissando and the kane."""
    tr = Track(3, 132, rng=rng, send=0.15, loop=False)
    tr.n += int(2.0 * SR)
    tr.L, tr.R, tr.SL, tr.SR_ = (np.zeros(tr.n) for _ in range(4))
    sc, root = RYO, 62
    tr.sc, tr.root = sc, root
    F = M("2:.25 3:.25 5:.5 r:.5 5:.5 4:.5 5:.5 7:1 | 6:.5 5:.5 3:.5 4:.5 5:2 | 7:4", 3)
    play(tr, F, biwa, 0, sc, root, pan=-0.2, gain=1.0, vel=1.0)
    blow(tr, F, "shinobue", 0, sc, root + 12, pan=0.25, gain=0.75)
    play(tr, shift(F, -2), koto, 0, sc, root + 12, pan=-0.35, gain=0.5, tag="ctr")
    for b, r in ((0, 38), (1, 43), (2, 38)):
        for pan in (-0.6, 0.6):
            tr.add(guitar(snap(tr, r), (4 if b == 2 else 1.6) * tr.spb, rng, drive=2.4, chord=(0, fifth(tr, snap(tr, r)), 12)), tr.at(b), pan, 0.4, 0.1, 0.0, "gtr")
        tr.add(bass(snap(tr, r), (4 if b == 2 else 1.8) * tr.spb, rng), tr.at(b), 0.0, 0.7, 0.0, 0.0, "bass")
    for b in (0, 2):
        tr.add(kit("crash", rng), tr.at(b), 0.3, 0.8, 0.1, 0.0, "drums")
        tr.add(kit("kick", rng), tr.at(b), 0.0, 0.8, 0.0, 0.0, "drums")
        tr.add(drum("odaiko", rng), tr.at(b), 0.0, 0.8, 0.2, 0.0, "taiko")
    for beat in (1, 2, 3):
        tr.add(kit("snare", rng), tr.at(1, beat), 0.0, 0.4 + 0.1 * beat, 0.05, 0.0, "drums")
    for i, d in enumerate(range(0, 11)):                                       # the koto glissando on the last chord
        tr.add(koto(deg(sc, root, d), 2.4, rng), tr.at(2) + i * 0.035, -0.3 + 0.06 * i, 0.45, None, 0.0, "arp")
    chord_pad(tr, 2, [62, 66, 69, 74], 1, "strings", gain=0.45, att=0.05)
    tr.add(bell(880, 3.0, rng), tr.at(2), 0.4, 0.3, 0.4, 0.0, "bell")
    reverb(tr, rt60=1.8, wet=0.9)
    return tr


def c_victory_body(rng):
    """The results screen: a relaxed koto tune (D ryo, 104 BPM, 8 bars) with jushichigen and a soft shime."""
    tr = Track(8, 104, rng=rng, send=0.2)
    sc, root = RYO, 62
    tr.sc, tr.root = sc, root
    mel = M("3:1 5:1 4:.5 3:.5 2:1 | 3:3 r:1 | 2:1 3:1 2:.5 1:.5 0:1 | 1:3 r:1 | 3:1 5:1 4:.5 3:.5 2:1 | "
            "3:2 5:2 | 4:1 3:.5 2:.5 1:1 2:1 | 0:3 r:1", 8)
    play(tr, mel, koto, 0, sc, root + 12, pan=-0.1, gain=0.9)
    H = [62, 67, 59, 69, 62, 67, 69, 62]
    for k, r in enumerate(H):
        tri = TRIADS[r]
        arp(tr, k, [tri[0] - 12, tri[1] - 12, tri[2] - 12, tri[0]], [0, 2, 1, 3], step=1.0, pan=0.3, gain=0.3)
        tr.add(bass_koto(snap(tr, r - 24), 2.2, rng), tr.at(k), 0.0, 0.6, 0.1, 0.0, "bass")
        taiko_bar(tr, k, [(0, "shime", 0.4), (2, "shime", 0.3), (3.5, "kakko", 0.3)], 0.6)
    reverb(tr, rt60=2.0, wet=1.0)
    return tr


def c_inn_intro(rng):
    tr = Track(4, 70, rng=rng, send=0.3, loop=False)
    sc, root = YO, 67
    tr.sc, tr.root = sc, root
    for i, d in enumerate((4, 3, 2, 0, 2, 0, -1, 0)):
        tr.add(koto(deg(sc, root, d), 3.0, rng, decay=0.7, vel=0.85), i * 0.55, -0.2, 0.6, None, 0.01, "lead")
    tr.add(bass_koto(deg(sc, root - 24, 0), 4.0, rng), 0.0, 0.0, 0.5, 0.2, 0.0, "bass")
    tr.add(bass_koto(deg(sc, root - 24, 0), 4.0, rng), 3.3, 0.0, 0.4, 0.2, 0.0, "bass")
    tr.add(sho(keyed(tr, [67, 71, 74, 76]), 5.0, rng), 0.0, 0.0, 0.25, 0.4, 0.0, "pad")
    tr.add(bell(float(hz(deg(sc, root + 12, 0))), 4.0, rng, ratios=(1.0, 2.71, 5.15)), 4.6, 0.3, 0.4, 0.4, 0.0, "bell")
    reverb(tr, rt60=2.6, wet=1.0)
    return tr


def c_quiet_body(rng):
    tr = Track(2, 60, rng=rng, send=0.0)
    wl, wr = waves(tr.n, rng, 0.004)
    tr.ambience(wl, wr, 1.0)
    return tr


def c_fall_intro(rng):
    """Game over: a shakuhachi falling through the in scale over a low o-daiko and a kane, the koto falling too."""
    tr = Track(4, 54, rng=rng, send=0.4, loop=False)
    sc, root = IN, 62
    tr.sc, tr.root = sc, root
    blow(tr, M("4:3 3:1 | 1:4 | 0:2 -1:2 | -2:4", 4), "shakuhachi", 0, sc, root, pan=0.0, gain=0.9)
    for i, d in enumerate((5, 4, 3, 2, 1, 0, -1, -2)):
        tr.add(koto(deg(sc, root, d), 2.5, rng, decay=0.8, vel=0.8), tr.at(0, 1 + i * 0.75), -0.3, 0.35, None, 0.01,
               "arp")
    tr.add(drum("odaiko", rng), tr.at(0), 0.0, 0.6, 0.3, 0.0, "taiko")
    tr.add(drum("odaiko", rng), tr.at(2), 0.0, 0.5, 0.3, 0.0, "taiko")
    tr.add(bell(float(hz(58)), 6.0, rng, beat=1.5), tr.at(2, 0), 0, 0.5, 0.4, 0.0, "bell")
    tr.add(bass_koto(deg(sc, root - 24, 0), 8.0, rng), tr.at(0), 0.0, 0.5, 0.2, 0.0, "bass")
    reverb(tr, rt60=4.0, wet=1.0)
    return tr


# key -> (MU id, title, builder, kind, loudness target LUFS). Fights are loudest; calm places sit 3-6 dB under.
TRACKS = {
    "town": ("MU101", "Village Lanterns", t_town, "loop", -15.0),
    "road": ("MU102", "The Long Road", t_road, "loop", -15.0),
    "cave": ("MU103", "Beneath the Stone", t_cave, "loop", -17.5),
    "battle": ("MU104", "Steel Drawn", t_battle, "loop", -12.0),
    "boss": ("MU105", "The Fortunes Turn Away", t_boss, "loop", -11.5),
    "court": ("MU106", "Halls of the Gozoku", t_court, "loop", -16.0),
    "shrine": ("MU107", "Incense and Bells", t_shrine, "loop", -17.0),
    "sea": ("MU108", "Salt Wind", t_sea, "loop", -15.0),
    "night": ("MU109", "Moon Over the Paddies", t_night, "loop", -17.0),
    "past": ("MU110", "Ink Between the Years", t_past, "loop", -17.0),
    "shadow": ("MU111", "Where the Kami Do Not Go", t_shadow, "loop", -16.0),
    "boss_oni": ("MU115", "Teeth of the Shadowlands", t_boss_oni, "loop", -11.5),
    "duel": ("MU116", "Two Breaths, One Cut", t_duel, "loop", -12.0),
    "intrigue": ("MU117", "Smiles Behind the Fan", t_intrigue, "loop", -12.5),
    "miniboss": ("MU118", "Blades in the Way", t_miniboss, "loop", -12.0),
    "final1": ("MU119", "The Bride in White", t_final1, "loop", -11.5),
    "final2": ("MU120", "Body of Damned Time", t_final2, "loop", -11.5),
    "final3": ("MU121", "The Empress of Nothing", t_final3, "loop", -11.0),
    "orochi": ("MU122", "Eight Heads Beneath the Waves", t_orochi, "loop", -11.0),
    "okura": ("MU123", "Akuma's Daughter", t_okura, "loop", -11.0),
    "travelers": ("MU124", "Eight Roads, One Dawn", t_travelers, "loop", -14.0),
    "ending": ("MU125", "Lanterns on the River", t_ending, "loop", -16.0),
}
CUES = {
    "victory": ("MU112", "Victory", c_victory_intro, c_victory_body, "MU021", -12.5, -19.0),
    "inn": ("MU113", "A Night's Rest", c_inn_intro, c_quiet_body, "MU022", -16.0, -40.0),
    "fall": ("MU114", "The Fall", c_fall_intro, c_quiet_body, "MU017", -16.0, -40.0),
}
MUSIC = {k: v[0] for k, v in TRACKS.items()}                                   # gen_maps / gen_data: key -> MU id

# Battle themes by the group's tag ("Scripted (b_boss_kommei)" -> b_boss_kommei). Anything not listed: groups named
# boss / duel get the boss theme, everything else the battle theme (battle_music below).
BATTLE_MUSIC = {
    # the standard boss (MU105)
    "b_boss_grasping_paw": "boss", "b_boss_grasping_paw_ryozo": "boss", "b_boss_katsuo": "boss",
    "b_boss_katsuo_ryohei": "boss", "b_boss_tide": "boss", "b_boss_parley": "boss", "b_boss_naohida": "boss",
    "b_boss_tomie_old": "boss", "b_boss_tomie_cho": "boss",
    # oni, maho, the Taint, the restless dead (MU115)
    "b_boss_puppet_troll": "boss_oni", "b_boss_kommei": "boss_oni", "b_boss_tsukakoro": "boss_oni",
    "b_boss_otamai": "boss_oni", "b_boss_otamai_yard": "boss_oni", "b_boss_otamai_nohost": "boss_oni",
    "b_boss_otamai_yard_nohost": "boss_oni", "b_boss_ianwa": "boss_oni", "b_boss_rokuro_demon": "boss_oni",
    "b_boss_hioninmaru": "boss_oni", "b_boss_oni_no_kuzushi": "boss_oni", "b_boss_mieko_dark": "boss_oni",
    "b_boss_kansen_hana": "boss_oni", "b_boss_stolen_face": "boss_oni", "b_boss_mine_guardian": "boss_oni",
    "b_boss_kurosho_regret": "boss_oni", "b_boss_ghost_guard_basin": "boss_oni",
    # duels and rivals (MU116)
    "b_duel_noboru": "duel", "b_boss_yasurugi": "duel", "b_boss_yasurugi_cells": "duel", "b_boss_masanori": "duel",
    "b_duel_ozaki": "duel", "b_duel_gusai": "duel", "b_duel_ashimita": "duel", "b_duel_shiba_guard": "duel",
    "b_gusai_duel": "duel", "b_berserker_duel": "duel", "b_boss_ushimo": "duel", "b_front_mantis": "duel",
    "b_boss_naga_champion": "duel", "b_bracket_1": "duel", "b_bracket_2": "duel", "b_bracket_3": "duel",
    "b_shogen_test": "duel",
    # court villains, assassins, conspiracies (MU117)
    "b_boss_iron_cranes": "intrigue", "b_boss_miya_killers": "intrigue", "b_boss_kumpei_flagship": "intrigue",
    "b_boss_iuchi_hit_squad": "intrigue", "b_boss_snake_enforcers": "intrigue", "b_boss_munashii": "intrigue",
    # mini-bosses: a named foe with boss art inside a chapter (MU118)
    "b_midboss_chihaya": "miniboss", "b_storm_yosuke": "miniboss", "b_sea_umibozu": "miniboss",
    "b_archive_guardian": "miniboss", "b_nagai_possessed": "miniboss", "b_bridge_bandit": "miniboss",
    "b_ashimoshi": "miniboss", "b_pass_cultists": "miniboss", "b_mieko_dark_mid": "miniboss", "b_siko": "miniboss",
    "b_alley_ambush": "miniboss", "b_tengu_bridge": "miniboss", "b_shrine_wave_4_ryozo": "miniboss",
    "b_shrine_wave_6": "miniboss", "b_shrine_wave_6_kage": "miniboss", "b_shrine_wave_7": "miniboss",
    "b_sl_akutsukai": "miniboss", "b_siege_breach_b": "miniboss", "b_ss_goro_troll": "miniboss",
    "b_kommei_brood": "miniboss", "b_ss_benjiro_father": "miniboss",
    # the finale and the post-game
    "b_boss_final_nashiko_p1": "final1", "b_boss_final_nashiko_p2": "final2", "b_boss_final_nashiko_p3": "final3",
    "b_superboss_orochi": "orochi", "b_boss_okura": "okura",
}


def battle_music(name):
    """A battle group's name -> its MU id (gen_data)."""
    nm = (name or "").lower()
    m = re.search(r"\((b_[a-z0-9_]+)", nm)
    key = BATTLE_MUSIC.get(m.group(1)) if m else None
    if key is None:
        key = "boss" if any(k in nm for k in ("boss", "duel")) else "battle"
    return MUSIC[key]


# ------------------------------------------------------------------------------------------- output
def find_ffmpeg():
    for c in (os.environ.get("RT_FFMPEG"), shutil.which("ffmpeg"),
              os.path.expanduser(r"~\Desktop\chatGPT-discord-bot\.venv\Lib\site-packages\imageio_ffmpeg\binaries"
                                 r"\ffmpeg-win-x86_64-v9.0.2.exe"),
              r"D:\chatGPT-discord-bot\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"):
        if c and os.path.exists(c):
            return c
    sys.exit("gen_music: ffmpeg not found (set RT_FFMPEG to an ffmpeg.exe with libvorbis)")


def write_wav(x, path):
    pcm = (np.clip(x, -1, 1).T * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def write_ogg(x, key):
    os.makedirs(PREVIEW, exist_ok=True)
    wav = os.path.join(PREVIEW, "rt_%s.wav" % key)
    write_wav(x, wav)
    ogg = os.path.join(RES, "bgm", "rt_%s.ogg" % key)
    subprocess.run([find_ffmpeg(), "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "5", ogg],
                   check=True)
    return "/resource/bgm/rt_%s.ogg" % key


def write_clip(x, key, loop=0, secs=45.0):
    """A preview for the user: the intro and the start of the body, the loop seam included when the track is
    short enough (the body is repeated once so the seam can be heard), faded out at the end."""
    os.makedirs(CLIPS, exist_ok=True)
    body = x[:, loop:]
    y = np.concatenate([x, body, body], axis=1)[:, :int(secs * SR)]
    k = int(2.0 * SR)
    y[:, -k:] *= np.linspace(1, 0, k)
    wav = os.path.join(CLIPS, "_tmp_%s.wav" % key)
    write_wav(y, wav)
    mp3 = os.path.join(CLIPS, "rt_%s.mp3" % key)
    subprocess.run([find_ffmpeg(), "-y", "-loglevel", "error", "-i", wav, "-c:a", "libmp3lame", "-q:a", "3", mp3],
                   check=True)
    os.remove(wav)


def bands(x):
    m = x.mean(0)
    X = np.abs(np.fft.rfft(m)) ** 2
    f = _freqs(len(m))
    e = [X[(f >= a) & (f < b)].sum() for a, b in ((20, 120), (120, 500), (500, 2000), (2000, 6000), (6000, 20000))]
    s = sum(e) + 1e-12
    return "/".join("%d" % round(100 * v / s) for v in e)


def stem_report(tr):
    tot = sum(tr.stems.values()) + 1e-12
    return " ".join("%s %d%%" % (k, round(100 * v / tot)) for k, v in sorted(tr.stems.items(), key=lambda kv: -kv[1])
                    if v / tot >= 0.02)


def main():
    args = sys.argv[1:]
    clips = "--clips" in args
    want = set(a for a in args if not a.startswith("--"))
    jpath = os.path.join(RES, "bgm.json")
    j = json.load(open(jpath, encoding="utf-8"))
    report = []
    for i, (key, (mid, title, fn, _, lufs)) in enumerate(TRACKS.items()):
        if want and key not in want:
            continue
        _CACHE.clear()
        rng = np.random.default_rng(1000 + i)
        tr = fn(rng)
        x = master(tr, lufs)
        j[mid] = entry(write_ogg(x, key), x.shape[1], title, tr.i0)
        if clips:
            write_clip(x, key, tr.i0)
        report.append("%s %-9s %-30s %5.1f s%s  %5.1f LUFS  peak %5.1f dBFS  bands %s\n      stems: %s" % (
            mid, key, title, x.shape[1] / SR, " (intro %.1f s)" % (tr.i0 / SR) if tr.i0 else "", loudness(x),
            20 * np.log10(np.abs(x).max()), bands(x), stem_report(tr)))
        print(report[-1], flush=True)
    for i, (key, (mid, title, fa, fb, repoint, la, lb)) in enumerate(CUES.items()):
        if want and key not in want:
            continue
        _CACHE.clear()
        rng = np.random.default_rng(2000 + i)
        x, loop = cue(fa, fb, rng, la, lb)
        e = entry(write_ogg(x, key), x.shape[1], title, loop)
        j[mid] = e
        j[repoint] = dict(e, memo="tools/gen_music.py (the engine's cue, re-pointed)")
        if clips:
            write_clip(x, key, loop, secs=min(45.0, x.shape[1] / SR + 4))
        report.append("%s %-9s %-30s %5.1f s  loop at %.1f s  (also %s)  intro %5.1f LUFS  peak %5.1f dBFS" % (
            mid, key, title, x.shape[1] / SR, loop / SR, repoint, loudness(x[:, :loop]),
            20 * np.log10(np.abs(x).max())))
        print(report[-1], flush=True)
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")


def entry(path, n, title, loop=0):
    return {"endpoint": -1, "gain": 1.0, "info": {"ch": 2, "format": "ogg", "freq": SR, "length": int(n)},
            "looppoint": int(loop), "name": {"en": title, "ja": title}, "startpoint": 0, "wav": path,
            "memo": "tools/gen_music.py"}


if __name__ == "__main__":
    main()
