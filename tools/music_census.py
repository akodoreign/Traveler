"""Note census for gen_music tracks: every pitched note each layer (stem tag) plays, checked against the track's own
scale (its "sc, root = ..." line), with the bars where out-of-scale notes fall, and each stem's share of the mix.
python -E tools/music_census.py [key ...]        (default: every track and cue body)"""
import inspect
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_music as g  # noqa: E402

NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
PENDING = []


def midi_of_hz(f):
    return int(round(69 + 12 * np.log2(float(f) / 440.0)))


def wrap(name, kind):
    f = getattr(g, name)

    def w(*a, **k):
        if kind == "m":                         # inst(m, dur, rng, ...)
            ch = k.get("chord", (0,)) if name == "guitar" else (0,)
            PENDING.extend((int(round(a[0])) + c, 0.0, float(a[1])) for c in ch)
        elif kind == "ms":                      # pad(ms, dur, ...), sho(ms, dur, ...)
            PENDING.extend((int(round(m)), 0.0, float(a[1])) for m in a[0])
        elif kind == "wind":                    # wind(kind, [(t, ln, midi, v, orn)], rng)
            PENDING.extend((int(round(n[2])), float(n[0]), float(n[1])) for n in a[1])
        elif kind == "hz":                      # bell(f0, ...), bonsho(f0, ...)
            PENDING.append((midi_of_hz(a[0]), 0.0, 1.5))
        return f(*a, **k)
    setattr(g, name, w)


for n in ("koto", "musicbox", "bass_koto", "shamisen", "biwa", "bass", "guitar", "lead"):
    wrap(n, "m")
for n in ("pad", "sho"):
    wrap(n, "ms")
wrap("wind", "wind")
for n in ("bell", "bonsho"):
    wrap(n, "hz")
for fn in (g.riff, g.arp):                      # default-argument instruments were bound at def time
    fn.__defaults__ = tuple(getattr(g, d.__name__) if callable(d) and hasattr(g, getattr(d, "__name__", "")) else d
                            for d in fn.__defaults__)

_add = g.Track.add


def add(self, sig, t, pan=0.0, gain=1.0, send=None, jit=0.0, tag="misc"):
    if PENDING:
        for m, off, dur in PENDING:
            t0 = t + off
            self._census[tag].append((m, int(t0 / (self.beats * self.spb)), t0, min(dur, 2.5)))
        del PENDING[:]
    return _add(self, sig, t, pan, gain, send, jit, tag)


g.Track.add = add
_init = g.Track.__init__


def init(self, *a, **k):
    _init(self, *a, **k)
    self._census = defaultdict(list)


g.Track.__init__ = init


def scale_of(fn):
    m = re.search(r"sc, root = (\w+), (\d+)", inspect.getsource(fn))
    if not m:
        return None, None
    return getattr(g, m.group(1)), int(m.group(2))


def census(key, fn, rng):
    sc, root = scale_of(fn)
    g._CACHE.clear()
    tr = fn(rng)
    print("== %s (%s)" % (key, "%s %s" % (NAMES[root % 12], [NAMES[(root + s) % 12] for s in sc]) if sc else
                         "no scale line"))
    tot = sum(tr.stems.values()) + 1e-12
    print("   stems: " + " ".join("%s %d%%" % (k, round(100 * v / tot)) for k, v in
                                  sorted(tr.stems.items(), key=lambda kv: -kv[1]) if v / tot >= 0.02))
    if not sc:
        clashes(tr, key)
        return
    pcs = {(root + s) % 12 for s in sc}
    clashes(tr, key, pcs if "--all" not in sys.argv else None)
    for tag, notes in sorted(tr._census.items()):
        bad = [(m, b) for m, b, _, _ in notes if m % 12 not in pcs]
        if bad:
            c = Counter(NAMES[m % 12] for m, _ in bad)
            bars = sorted(set(b for _, b in bad))
            print("   %-8s %4d/%4d out: %s  bars %s" % (tag, len(bad), len(notes), dict(c),
                                                       bars[:16] + (["..."] if len(bars) > 16 else [])))


def clashes(tr, key, pcs=None):
    """Seconds where two different layers sound a semitone (or minor 9th) apart, by the pair of layers."""
    step = tr.spb / 4
    n = int(tr.n / g.SR / step) + 2 if hasattr(tr, "n") else 4000
    grid = defaultdict(lambda: defaultdict(set))           # cell -> tag -> pitch classes
    for tag, notes in tr._census.items():
        if tag in ("drums", "taiko", "amb"):
            continue
        for m, b, t0, dur in notes:
            for c in range(int(t0 / step), int((t0 + max(dur, step)) / step)):
                grid[c][tag].add(m % 12)
    pair, where = Counter(), defaultdict(set)
    for c, tags in grid.items():
        ts = sorted(tags)
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                for a in tags[ts[i]]:
                    for b in tags[ts[j]]:
                        if (a - b) % 12 in (1, 11) and (pcs is None or a not in pcs or b not in pcs):
                            k = (ts[i], NAMES[a], ts[j], NAMES[b])
                            pair[k] += step
                            where[k].add(int(c * step / (tr.beats * tr.spb)))
    tot = sum(pair.values())
    print("   %s %.1f s total (track %.0f s)" % ("CLASH" if pcs is None else "FOREIGN", tot, tr.n / g.SR if hasattr(tr, "n") else 0))
    for k, v in pair.most_common(6):
        if v >= 0.5:
            bars = sorted(where[k])
            print("     %5.1f s  %s %s vs %s %s  bars %s" % ((v,) + k + (bars[:12] + (["..."] if len(bars) > 12 else []),)))


def main():
    want = set(a for a in sys.argv[1:] if not a.startswith("--"))
    for i, (key, (mid, title, fn, _, lufs)) in enumerate(g.TRACKS.items()):
        if not want or key in want:
            census(key, fn, np.random.default_rng(1000 + i))
    for i, (key, (mid, title, fa, fb, *_)) in enumerate(g.CUES.items()):
        if not want or key in want:
            census(key + "_intro", fa, np.random.default_rng(2000 + i))


if __name__ == "__main__":
    main()
