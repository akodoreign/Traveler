"""Octopath-style "pixel texture" for the voxel map tiles (idempotent; originals backed up to _tools/data_orig/).

RPG-Cobo maps are assembled from tile models (resource/vox/map/*.vox) recoloured per tile type by the palette
overrides in resource/map_vox.json. Stock grass tiles are one flat colour per 8x8 cell, which reads as smooth plastic.
This script:
  - floor1.vox grass1/2/3 + def: paints a seamless 4-tone leafy pattern into the top two layers, using spare palette
    indices TEX (dark2, dark1, light1, light2); map_vox.json floor entries get a hue-shifted ramp for those indices,
    derived from each entry's own grass colour.
  - terrain1.vox cliff walls (mid*/btm*/midc): horizontal tan/brown strata with jitter, using the 3 indices each
    wall already has (dark/main/light).
Only colour-index bytes and palette entries are rewritten in place (file structure untouched).
Run: python -E tools/gen_terrain_tex.py
"""
import colorsys
import json
import os
import shutil
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import voxlib  # noqa: E402

RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
BACKUP = os.path.join(HERE, "..", "_tools", "data_orig", "vox_map")
FLOOR = os.path.join(RES, "vox", "map", "floor", "floor1.vox")
TERRAIN = os.path.join(RES, "vox", "map", "terrain", "terrain1.vox")
MAPVOX = os.path.join(RES, "map_vox.json")
TEX = (131, 132, 133, 134)          # free in floor1.vox: darker2, darker1, lighter1, lighter2
GRASS_MODELS = {"grass1": 83, "grass2": 84, "grass3": 93, "def": 102}   # model -> its top colour index
rng = np.random.default_rng(7)


def backup(path):
    os.makedirs(BACKUP, exist_ok=True)
    b = os.path.join(BACKUP, os.path.basename(path))
    if not os.path.exists(b):
        shutil.copy(path, b)
    shutil.copy(b, path)               # always start from the original -> idempotent


def xyzi_offsets(data):
    """Byte offset of each XYZI chunk's voxel array, in model order."""
    offs, o = [], 8
    cid, n, m = data[o:o + 4], *struct.unpack_from("<ii", data, o + 4)
    o += 12                            # into MAIN's children
    while o < len(data):
        cid = data[o:o + 4]
        n, m = struct.unpack_from("<ii", data, o + 4)
        if cid == b"XYZI":
            offs.append(o + 12 + 4)
        if cid == b"RGBA":
            offs.append(("RGBA", o + 12))
        o += 12 + n + m
    return offs


def leafy_pattern(n=8):
    """Seamless n x n leafy clump pattern -> values 0..4 (0 darkest, 2 main, 4 brightest)."""
    v = np.zeros((n, n))
    for _ in range(9):                 # soft clumps, wrapped
        cx, cy, r, a = rng.uniform(0, n), rng.uniform(0, n), rng.uniform(1.2, 2.6), rng.choice([-1, 1])
        for y in range(n):
            for x in range(n):
                dx = min(abs(x - cx), n - abs(x - cx))
                dy = min(abs(y - cy), n - abs(y - cy))
                v[y, x] += a * max(0, 1 - (dx * dx + dy * dy) ** 0.5 / r)
    v += rng.normal(0, 0.35, (n, n))   # per-texel grain
    q = np.quantile(v, [0.05, 0.28, 0.74, 0.95])
    out = np.digitize(v, q)
    # blade strokes: short diagonal light/dark pairs
    for _ in range(3):
        x, y = rng.integers(0, n, 2)
        out[y, x] = 4
        out[(y + 1) % n, (x + 1) % n] = 0
    return out


def ramp(rgb):
    h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in rgb])
    res = []
    for dv, dh, ds in ((-0.17, +0.02, +0.08), (-0.08, +0.01, +0.04), (+0.06, -0.015, -0.03), (+0.12, -0.03, -0.08)):
        r, g, b = colorsys.hsv_to_rgb((h + dh) % 1, min(1, max(0, s + ds)), min(1, max(0, v + dv)))
        res.append((int(r * 255), int(g * 255), int(b * 255)))
    return res


def texture_floor():
    backup(FLOOR)
    vox = voxlib.read_vox(FLOOR)
    data = bytearray(open(FLOOR, "rb").read())
    offs = [o for o in xyzi_offsets(data) if not isinstance(o, tuple)]
    pal_off = [o for o in xyzi_offsets(data) if isinstance(o, tuple)][0][1]
    for mid, ((sx, sy, sz), arr) in enumerate(vox["models"]):
        name = vox["names"].get(mid)
        if name not in GRASS_MODELS:
            continue
        main = GRASS_MODELS[name]
        pat = leafy_pattern(sx)
        idx_of = {0: TEX[0], 1: TEX[1], 2: main, 3: TEX[2], 4: TEX[3]}
        o = offs[mid]
        for i, (x, y, z, c) in enumerate(arr):
            if z >= sz - 2:
                lvl = pat[y, x] if z == sz - 1 else max(0, pat[y, x] - 1)
                data[o + i * 4 + 3] = idx_of[int(lvl)]
        # default palette for the TEX indices (used when a map_vox entry has no override)
        base = vox["palette"][main - 1][:3]
        for k, col in zip(TEX, ramp(base)):
            struct.pack_into("<4B", data, pal_off + (k - 1) * 4, *col, 255)
    open(FLOOR, "wb").write(data)
    print("floor1.vox: grass tiles textured")


def texture_mapvox():
    backup(MAPVOX)
    mv = json.load(open(MAPVOX, encoding="utf-8"))
    n = 0
    for grp in mv.values():
        for e in grp.values():
            for vk, pk in (("vp0", "pal0"), ("vp1", "pal1")):
                vp = e.get(vk)
                if not vp or vp[0] != "floor1" or vp[1] not in GRASS_MODELS:
                    continue
                pal = e.get(pk) or []
                pairs = dict(zip(pal[0::2], pal[1::2]))
                main = GRASS_MODELS[vp[1]]
                if main not in pairs:
                    continue
                v = pairs[main]
                hi = v & ~0xFFFFFF
                for k, (r, g, b) in zip(TEX, ramp(voxlib.decode_col(v))):
                    pairs[k] = hi | (b << 16) | (g << 8) | r
                e[pk] = [x for k in sorted(pairs) for x in (k, pairs[k])]
                n += 1
    json.dump(mv, open(MAPVOX, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print("map_vox.json: %d grass entries got texture ramps" % n)


def texture_terrain():
    backup(TERRAIN)
    vox = voxlib.read_vox(TERRAIN)
    data = bytearray(open(TERRAIN, "rb").read())
    offs = [o for o in xyzi_offsets(data) if not isinstance(o, tuple)]
    jit = rng.integers(0, 2, (64, 64))
    for mid, ((sx, sy, sz), arr) in enumerate(vox["models"]):
        name = vox["names"].get(mid, "")
        if not name.startswith(("mid", "btm")):
            continue
        cols = sorted(set(int(c) for c in arr[:, 3]) - {255})
        if len(cols) != 3:
            continue
        dark, main, light = cols
        o = offs[mid]
        for i, (x, y, z, c) in enumerate(arr):
            if c == 255:
                continue
            band = (int(z) + jit[x % 64, y % 64] + (int(x) + int(y)) // 5) % 7
            nc = light if band in (0, 1) else dark if band == 4 else main
            if rng.random() < 0.08:
                nc = dark
            data[o + i * 4 + 3] = nc
    open(TERRAIN, "wb").write(data)
    print("terrain1.vox: cliff strata painted")


if __name__ == "__main__":
    texture_floor()
    texture_mapvox()
    texture_terrain()
