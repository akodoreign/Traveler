"""Minimal MagicaVoxel .vox reader/writer and preview renderer for Rokugan Traveler asset work.

- read_vox(path) -> {"models": [(size, voxels[N,4] x,y,z,colorindex)], "palette": [(r,g,b,a)]*256, "names": {...}}
- render_front(model, palette, scale) -> PIL.Image (orthographic, looking along -y, z up, simple depth shading)
- apply_pal(palette, pal_pairs) -> palette with RPG-Cobo "pal" overrides applied (index -> 0x1RRGGBB)
"""
import struct
import numpy as np
from PIL import Image

DEFAULT_PALETTE = None  # MagicaVoxel default palette is only needed when a file has no RGBA chunk.


def _chunks(data, off, end):
    while off < end:
        cid = data[off:off + 4].decode("ascii", "replace")
        n, m = struct.unpack_from("<ii", data, off + 4)
        content = data[off + 12: off + 12 + n]
        children = (off + 12 + n, off + 12 + n + m)
        yield cid, content, children
        off += 12 + n + m


def _read_string(b, o):
    n = struct.unpack_from("<i", b, o)[0]
    return b[o + 4:o + 4 + n].decode("utf-8", "replace"), o + 4 + n


def _read_dict(b, o):
    cnt = struct.unpack_from("<i", b, o)[0]
    o += 4
    d = {}
    for _ in range(cnt):
        k, o = _read_string(b, o)
        v, o = _read_string(b, o)
        d[k] = v
    return d, o


def read_vox(path):
    data = open(path, "rb").read()
    assert data[:4] == b"VOX ", path
    models, palette, sizes = [], None, []
    shapes, transforms, groups = {}, {}, {}
    # MAIN chunk at 8
    for cid, content, (cs, ce) in _chunks(data, 8, len(data)):
        if cid != "MAIN":
            continue
        for c2, cont2, _ in _chunks(data, cs, ce):
            if c2 == "SIZE":
                sizes.append(struct.unpack("<iii", cont2[:12]))
            elif c2 == "XYZI":
                n = struct.unpack_from("<i", cont2, 0)[0]
                arr = np.frombuffer(cont2, dtype=np.uint8, count=n * 4, offset=4).reshape(n, 4).copy()
                models.append((sizes[len(models)], arr))
            elif c2 == "RGBA":
                raw = np.frombuffer(cont2, dtype=np.uint8, count=1024).reshape(256, 4)
                palette = [tuple(int(x) for x in raw[i]) for i in range(256)]
            elif c2 == "nSHP":
                nid = struct.unpack_from("<i", cont2, 0)[0]
                attr, o = _read_dict(cont2, 4)
                cnt = struct.unpack_from("<i", cont2, o)[0]
                mids = [struct.unpack_from("<i", cont2, o + 4 + i * 8)[0] for i in range(cnt)]
                shapes[nid] = mids
            elif c2 == "nTRN":
                nid = struct.unpack_from("<i", cont2, 0)[0]
                attr, o = _read_dict(cont2, 4)
                child, _res, _layer, nfr = struct.unpack_from("<iiii", cont2, o)
                o += 16
                t = (0, 0, 0)
                if nfr > 0:
                    fr, o = _read_dict(cont2, o)
                    if "_t" in fr:
                        t = tuple(int(x) for x in fr["_t"].split())
                transforms[nid] = (attr.get("_name"), child, t)
            elif c2 == "nGRP":
                nid = struct.unpack_from("<i", cont2, 0)[0]
                attr, o = _read_dict(cont2, 4)
                cnt = struct.unpack_from("<i", cont2, o)[0]
                groups[nid] = [struct.unpack_from("<i", cont2, o + 4 + i * 4)[0] for i in range(cnt)]
    names, placed = {}, []
    for nid, (name, child, t) in transforms.items():
        if name and child in shapes:
            for mid in shapes[child]:
                names[mid] = name

    def walk(nid, off):
        if nid in transforms:
            name, child, t = transforms[nid]
            walk(child, (off[0] + t[0], off[1] + t[1], off[2] + t[2]))
        elif nid in groups:
            for c in groups[nid]:
                walk(c, off)
        elif nid in shapes:
            for mid in shapes[nid]:
                placed.append((mid, off))

    if transforms:
        walk(0, (0, 0, 0))
    if palette is None:
        palette = [(i, i, i, 255) for i in range(256)]
    return {"models": models, "palette": palette, "names": names, "placed": placed}


def merge_scene(vox, skip=lambda name: False):
    """Combine all placed models (MagicaVoxel centres each model on its translation) into one voxel list."""
    pts = []
    for mid, (tx, ty, tz) in vox["placed"]:
        name = vox["names"].get(mid, "")
        if skip(name):
            continue
        (sx, sy, sz), arr = vox["models"][mid]
        a = arr.astype(np.int32).copy()
        a[:, 0] += tx - sx // 2
        a[:, 1] += ty - sy // 2
        a[:, 2] += tz - sz // 2
        pts.append(a)
    allp = np.concatenate(pts)
    mn = allp[:, :3].min(axis=0)
    allp[:, :3] -= mn
    size = tuple(int(x) for x in allp[:, :3].max(axis=0) + 1)
    return (size, allp)


def apply_pal(palette, pal_pairs):
    """RPG-Cobo chara_vox 'pal': [index, 0x1RRGGBB, ...]. Index is the voxel colour index (1-based)."""
    pal = list(palette)
    for i in range(0, len(pal_pairs), 2):
        idx, col = pal_pairs[i], pal_pairs[i + 1]
        pal[idx - 1] = decode_col(col) + (255,)
    return pal


def encode_col(r, g, b):
    """RPG-Cobo palette value: 0x1BBGGRR (verified against chara_vox.json defaults)."""
    return 0x1000000 | (int(b) << 16) | (int(g) << 8) | int(r)


def decode_col(v):
    return (v & 255, (v >> 8) & 255, (v >> 16) & 255)


def render_front(model, palette, scale=8, view="front"):
    """Orthographic render. MagicaVoxel is z-up; 'front' looks from -y toward +y."""
    (sx, sy, sz), vox = model
    img = np.zeros((sz, sx, 4), dtype=np.float32)
    depth = np.full((sz, sx), 1e9)
    for x, y, z, c in vox:
        if view == "front":
            u, v, d = x, sz - 1 - z, y
        elif view == "side":
            u, v, d = y, sz - 1 - z, sx - x
        else:
            u, v, d = x, sz - 1 - z, -y
        if d < depth[v, u]:
            depth[v, u] = d
            r, g, b, a = palette[c - 1]
            img[v, u] = (r, g, b, 255)
    # depth shading
    mask = img[..., 3] > 0
    if mask.any():
        dmin, dmax = depth[mask].min(), depth[mask].max()
        shade = 1.0 - 0.35 * (depth - dmin) / max(1.0, dmax - dmin)
        img[..., :3] *= np.where(mask, shade, 1.0)[..., None]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")
    return out.resize((sx * scale, sz * scale), Image.NEAREST)


def color_usage(model):
    _, vox = model
    idx, cnt = np.unique(vox[:, 3], return_counts=True)
    return dict(zip(idx.tolist(), cnt.tolist()))
