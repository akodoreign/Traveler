"""Reader for the engine's .mot skeleton/motion files (written by blender_rpgcobo's saveMotionData).

Matrices are returned row-vector style (translation in row 3), the engine's own convention.
"""
import struct
import sys
from pathlib import Path

import numpy as np


class _In:
    def __init__(self, data):
        self.d, self.o = data, 0

    def take(self, fmt):
        v = struct.unpack_from(fmt, self.d, self.o)
        self.o += struct.calcsize(fmt)
        return v

    def b(self): return self.take(">B")[0]
    def s(self): return self.take(">H")[0]
    def i(self): return self.take(">i")[0]
    def f(self): return self.take(">f")[0]
    def h(self): return float(np.frombuffer(struct.pack("<H", self.s()), np.float16)[0])

    def t(self):
        n = self.s()
        v = self.d[self.o:self.o + n].decode("latin-1")
        self.o += n
        return v


def _timeline(r):
    start, end = r.s(), r.s()
    keys, prev = [], dict(p=(0., 0., 0.), s=(1., 1., 1.), q=(1., 0., 0., 0.))
    for _ in range(start, end + 1):
        flag = r.b()
        k = dict(prev)
        if not flag & 1: k["p"] = (r.h(), r.h(), r.h())
        if not flag & 2: k["s"] = (r.h(), r.h(), r.h())
        if not flag & 4: k["q"] = (r.h(), r.h(), r.h(), r.h())   # w, x, y, z
        keys.append(k)
        prev = k
    return start, end, keys


def load(path):
    r = _In(Path(path).read_bytes())
    assert r.d[:4] == b"SMOT", path
    r.o = 4
    r.b()
    parts = []
    for _ in range(r.b()):
        name, pid, parent = r.t(), r.b(), r.b() - 1
        pivot = (r.f(), r.f(), r.f()) if r.b() else None
        bind = np.array([r.f() for _ in range(16)]).reshape(4, 4)
        length = r.f()
        start, end, keys = _timeline(r)
        assert r.i() == 0, f"timeline misread at {name}"
        parts.append(dict(name=name, id=pid, parent=parent, pivot=pivot, bind=bind, length=length,
                          start=start, end=end, keys=keys))
    customs = {}
    for _ in range(r.b()):
        name = r.t()
        customs[name] = [r.f() for _ in range(r.s())]
    return dict(parts=parts, customs=customs)


if __name__ == "__main__":
    m = load(sys.argv[1])
    for p in m["parts"]:
        print(f'{p["id"]:2} {p["name"]:10} parent={p["parent"]:2} len={p["length"]:.3f} '
              f'head={np.round(p["bind"][3, :3], 3)} frames={p["start"]}-{p["end"]}')
    print("customs:", {k: len(v) for k, v in m["customs"].items()})
