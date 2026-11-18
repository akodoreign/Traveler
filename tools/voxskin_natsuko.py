"""Hiruma Natsuko's voxel skin for the engine's chibi 3D character rig.

Base model: resource/vox/chara/woman_soldier.vox (the stock armoured woman that
CV100 "Hiruma Natsuko" pointed at with only a palette swap).  The engine binds
every part by name to a bone of /resource/mot/leg2_woman/woman_2.mot and pivots
each variant (arm_L1, face2, ...) with its "...0" sibling's translation, so this
script keeps every part, its box size and its nTRN `_t` (except head0, which is
grown at the back with `_t` shifted so existing voxels keep their world
position).  Inside those boxes the skin is redesigned from the character art in
_art/sources/cutout/trav_natsuko*.png:

  head0   dark-brown hair, red hachimaki with a knot and tails, high ponytail,
          longer side locks
  face0-3 tan skin, brown eyes (same expressions as the base)
  body0   navy kimono collar with a white V, navy lamellar do with red lacing
          and gold edges, red obi with a knot, laced kusazuri
  arm_*   sode shoulder plate, navy sleeve, laced kote, red cord, bare hand
  leg_*   navy hakama, laced suneate, navy tabi, straw waraji

    python -E tools/voxskin_natsuko.py [--preview out.png]

writes _tools/rpgcobo-tool/project/resource/vox/chara/trav_natsuko.vox.
"""
import os
import sys
from collections import deque

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voxfile import VoxFile  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARA = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource", "vox", "chara")
BASE = os.path.join(CHARA, "woman_soldier.vox")
OUT = os.path.join(CHARA, "trav_natsuko.vox")

# Palette sampled (k-means) from the Natsuko art, one base/shade/light per material.
NEW = {
    "navy0": (18, 20, 34), "navy1": (30, 34, 55), "navy2": (44, 49, 74),
    "plate1": (49, 68, 98), "plate2": (73, 92, 119),
    "red0": (146, 4, 7), "red1": (190, 6, 11), "red2": (228, 18, 22),
    "gold0": (155, 100, 45), "gold1": (210, 156, 80),
    "white": (222, 216, 202), "straw": (150, 108, 62),
    "hair0": (34, 13, 8), "hair1": (56, 24, 15), "hair2": (80, 38, 24),
    "hair3": (108, 55, 34), "hair4": (136, 74, 46),
}
SLOT0 = 20                      # unused by the base palette

# Base palette indices recoloured in place (face blocks keep their drawing).
RECOLOR = {
    185: (166, 96, 60), 186: (182, 108, 68), 187: (190, 115, 73),
    188: (202, 127, 83), 189: (216, 145, 99),                      # skin
    121: (92, 44, 24), 122: (128, 70, 40),                         # iris
    8: (30, 14, 10), 194: (52, 24, 15), 195: (72, 36, 22),
    196: (98, 52, 32), 197: (124, 70, 44), 206: (150, 88, 58),     # lashes, brows
    174: (168, 52, 42),                                            # open mouth
}
HAIR = {201: "hair0", 202: "hair1", 203: "hair2", 204: "hair3", 205: "hair4"}
SKIN = {185, 186, 187, 188, 189}


class Skin:
    def __init__(self):
        self.vf = VoxFile.load(BASE)
        self.idx = {}
        for i, (k, rgb) in enumerate(NEW.items()):
            self.vf.palette[SLOT0 + i] = (*rgb, 255)
            self.idx[k] = SLOT0 + i
        for i, rgb in RECOLOR.items():
            self.vf.palette[i] = (*rgb, 255)
        self.base = {n: self.vf.model(n).vox.copy() for n in self.vf.names}

    def c(self, name):
        return self.idx[name]

    # world <-> local for a part (MagicaVoxel: _t is the model centre, size//2)
    def offset(self, part):
        p0 = part[:-1] + "0"
        m = self.vf.model(part)
        return np.array(self.vf.trans[p0]) - np.array(m.size) // 2

    # ---------------------------------------------------------------- head
    def head(self):
        vf = self.vf
        old = vf.model("head0")
        grow = 8                               # extra depth behind the head
        sx, sy, sz = old.size
        vox = np.zeros((sx, sy + grow, sz), np.uint8)
        vox[:, :sy] = old.vox
        old.size, old.vox = (sx, sy + grow, sz), vox
        t = vf.trans["head0"]
        vf.set_translation("head0", (t[0], t[1] + grow // 2, t[2]))
        o = self.offset("head0")

        def put(x, y, z, col, over=True):
            lx, ly, lz = x - o[0], y - o[1], z - o[2]
            if 0 <= lx < vox.shape[0] and 0 <= ly < vox.shape[1] and 0 <= lz < vox.shape[2]:
                if over or vox[lx, ly, lz] == 0:
                    vox[lx, ly, lz] = col

        def get(x, y, z):
            lx, ly, lz = x - o[0], y - o[1], z - o[2]
            if 0 <= lx < vox.shape[0] and 0 <= ly < vox.shape[1] and 0 <= lz < vox.shape[2]:
                return vox[lx, ly, lz]
            return 0

        # strip the soldier's helmet band and visor, recolour the hair
        for v in (13, 16, 162, 163, 164):
            vox[vox == v] = 0
        for v, k in HAIR.items():
            vox[vox == v] = self.c(k)
        # fill crown gaps the visor left (front of the scalp, z 18..23)
        for z in range(18, 24):
            for x in range(-7, 7):
                ys = [y for y in range(-6, 9) if get(x, y, z)]
                if ys and min(ys) > -5:
                    put(x, -5, z, self.c("hair2"), over=False)

        # hachimaki: a 2-voxel red ring over the hair at forehead height
        band = (21, 22)
        for z in band:
            for x in range(-10, 10):
                for y in range(-8, 12):
                    if not get(x, y, z):
                        continue
                    if any(not get(x + dx, y + dy, z) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        put(x, y, z, self.c("red1" if z == band[1] else "red0"))
            for x in range(-6, 6):                      # across the forehead
                put(x, -6, z, self.c("red2" if z == band[1] else "red1"))
        # knot at the back and two tails that hang beside the ponytail
        yb = max(y for y in range(-8, 14) if get(0, y, band[0]))
        for x in (-1, 0):
            for z in band:
                put(x, yb + 1, z, self.c("red2"))
        for side, x0 in ((-1, -2), (1, 1)):
            for i, z in enumerate(range(band[0] - 1, 15, -1)):
                x = x0 + side * (i // 4)
                put(x, yb + 1 + (i > 2), z, self.c("red1" if i % 3 else "red0"))

        # high ponytail: tied at the back of the crown, arcs up and falls down the back
        path = [(-0.5, 5.0, 25.5, 2.6), (-0.5, 8.0, 27.5, 2.4), (-0.5, 11.5, 25.5, 2.3),
                (-0.5, 13.0, 21.0, 2.1), (-0.5, 13.0, 16.0, 1.8), (-0.5, 12.0, 11.5, 1.2)]
        pts = []
        for a, b in zip(path, path[1:]):
            for s in np.linspace(0, 1, 12, endpoint=False):
                pts.append(tuple(a[k] + (b[k] - a[k]) * s for k in range(4)))
        pts.append(path[-1])
        for i, (cx, cy, cz, r) in enumerate(pts):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                for y in range(int(cy - r - 1), int(cy + r + 2)):
                    for z in range(int(cz - r - 1), int(cz + r + 2)):
                        d = ((x + .5 - cx - .5) ** 2 + (y - cy) ** 2 + (z - cz) ** 2) ** .5
                        if d > r:
                            continue
                        strand = (x * 3 + z) % 4
                        col = ("hair3", "hair2", "hair2", "hair1")[strand]
                        if d > r - 0.8 and y > cy:
                            col = "hair1"
                        if i < 4 and z > cz + r - 1.2:
                            col = "hair4"
                        put(x, y, z, self.c(col), over=False)
        # red tie around the root of the tail
        cx, cy, cz, r = pts[3]
        for x in range(-4, 4):
            for y in range(int(cy) - 4, int(cy) + 5):
                for z in range(int(cz) - 4, int(cz) + 5):
                    d = ((x + .5 - cx - .5) ** 2 + (y - cy) ** 2 + (z - cz) ** 2) ** .5
                    if r < d <= r + 0.8 and abs(y - cy) < 0.6:
                        put(x, y, z, self.c("red1"), over=False)

        # side locks framing the face, down to the jaw
        for x, col in ((-8, "hair2"), (-7, "hair3"), (6, "hair3"), (7, "hair2")):
            for z in range(12, 17):
                put(x, -4, z, self.c(col if z > 12 else "hair1"), over=False)
                put(x, -3, z, self.c("hair1"), over=False)

    # ---------------------------------------------------------------- face
    def faces(self):
        pass                    # base expressions, recoloured through RECOLOR

    # ---------------------------------------------------------------- body
    def body(self):
        m = self.vf.model("body0")
        o = self.offset("body0")
        base = self.base["body0"]
        vox = np.zeros_like(base)
        occ = base > 0
        c = self.c

        def surface(lx, ly, lz):
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                p = (lx + dx, ly + dy, lz + dz)
                if not (0 <= p[0] < occ.shape[0] and 0 <= p[1] < occ.shape[1] and 0 <= p[2] < occ.shape[2]) or not occ[p]:
                    return True
            return False

        for lx, ly, lz in np.argwhere(occ):
            x, y, z = lx + o[0], ly + o[1], lz + o[2]
            if not surface(lx, ly, lz):
                vox[lx, ly, lz] = c("navy0")
                continue
            ys = [yy + o[1] for yy in np.nonzero(occ[lx, :, lz])[0]]
            front, back = y == min(ys), y == max(ys)
            edge = x in (-4, 3)
            if z >= 11:                                   # kimono collar with white V
                if front and x in (-1, 0):
                    col = "plate2" if False else None
                    col = None
                    vox[lx, ly, lz] = 188                 # skin at the V
                    continue
                col = "white" if front and x in (-2, 1) else ("navy1" if edge else "navy2")
            elif z >= 8:                                  # lamellar do
                if y <= -3:
                    col = "red1" if x in (-3, 2) else ("gold0" if z == 9 else "plate2")
                elif (front or back) and x in (-3, 2):
                    col = "red1"
                elif (front or back) and edge:
                    col = "gold0"
                elif edge and not (front or back):
                    col = "navy1"                         # kimono under the arm
                else:
                    col = "plate1" if z % 2 == 0 else "plate2"
            elif z == 7:                                  # obi
                col = "red2" if front and x in (-1, 0) else "red1"
            else:                                         # kusazuri
                if z == 5:
                    col = "gold0" if (front or back) else "plate1"
                else:
                    col = "red1" if (front or back) and x in (-3, -1, 0, 2) else "plate1"
            vox[lx, ly, lz] = c(col)

        def put(x, y, z, col):
            vox[x - o[0], y - o[1], z - o[2]] = c(col)
        # obi knot and tails on the front
        ymin7 = min(yy + o[1] for yy in np.nonzero(occ[:, :, 7 - o[2]].any(0))[0])
        for x in (-1, 0):
            put(x, ymin7 - 1, 7, "red2")
        put(0, ymin7 - 1, 6, "red1")
        put(0, ymin7 - 1, 5, "red0")
        put(-1, ymin7 - 1, 6, "red0")
        m.vox = vox

    # ---------------------------------------------------------------- arms
    def arm(self, part):
        m = self.vf.model(part)
        base = self.base[part]
        occ = base > 0
        pts = [tuple(p) for p in np.argwhere(occ)]
        top = max(p[2] for p in pts)
        start = [p for p in pts if p[2] == top]
        dist = {p: 0 for p in start}
        q = deque(start)
        while q:
            p = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        n = (p[0] + dx, p[1] + dy, p[2] + dz)
                        if n in dist or not (0 <= n[0] < occ.shape[0] and 0 <= n[1] < occ.shape[1] and 0 <= n[2] < occ.shape[2]):
                            continue
                        if occ[n]:
                            dist[n] = dist[p] + 1
                            q.append(n)
        far = max(dist.values()) or 1
        vox = np.zeros_like(base)
        out = 1 if "_L" in part else -1
        for p, d in dist.items():
            t = d / far
            if t <= 0.3:
                col = "red1" if d % 2 else "plate1"
            elif t <= 0.45:
                col = "navy2"
            elif t <= 0.55:
                col = "red1"
            elif t <= 0.78:
                col = "plate1" if d % 2 else "plate2"
            elif t <= 0.84:
                col = "gold1"
            else:
                vox[p] = 188 if base[p] not in SKIN else base[p]
                continue
            vox[p] = self.c(col)
        # sode: a plate hanging off the outside of the shoulder
        for p, d in dist.items():
            if d / far <= 0.3:
                n = (p[0] + out, p[1], p[2])
                if 0 <= n[0] < vox.shape[0] and not vox[n]:
                    vox[n] = self.c("gold0" if d == 0 else ("plate2" if d % 2 else "red1"))
        m.vox = vox

    # ---------------------------------------------------------------- legs
    def leg(self, part):
        m = self.vf.model(part)
        base = self.base[part]
        o = self.offset(part)
        vox = np.zeros_like(base)
        for lx, ly, lz in np.argwhere(base > 0):
            z = lz + o[2]
            col = base[lx, ly, lz]
            ys = np.nonzero(base[lx, :, lz])[0]
            front = ly == ys.min()
            if z >= 5:
                col = "navy2" if not front else "navy1"
            elif z >= 2:
                col = ("gold1" if z == 4 else "red1" if z == 3 else "plate2") if front else "plate1"
            elif z == 1:
                col = "gold0" if front else "navy1"
            else:
                col = "straw"
            vox[lx, ly, lz] = self.c(col)
        m.vox = vox

    def build(self):
        self.head()
        self.faces()
        self.body()
        for side in ("L", "R"):
            for i in range(3):
                self.arm("arm_%s%d" % (side, i))
            for i in range(2):
                self.leg("leg_%s%d" % (side, i))
        return self.vf


def main():
    vf = Skin().build()
    vf.save(OUT)
    print("wrote", OUT)
    for n in sorted(vf.names):
        mdl = vf.model(n)
        print("  %-7s size %-14s t %-14s voxels %d" % (n, mdl.size, vf.trans[n], int((mdl.vox > 0).sum())))


if __name__ == "__main__":
    main()
