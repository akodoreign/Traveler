"""MagicaVoxel .vox reader/writer that round-trips every chunk.

The RPG-Cobo voxel characters (resource/vox/chara/*.vox) keep extra data that
plain voxel tools drop: a META chunk (`_anim_range`), the nTRN/nGRP/nSHP scene
graph whose `_name` attributes are the part names the engine binds to bones
(head0, face0..3, body0, arm_L0..2, ...), and LAYR names such as
`mot=leg2_woman`.  This module keeps all chunks in order and only rewrites the
ones you change, so a template character can be re-skinned without touching
its rig layout.

    vf = VoxFile.load(path)
    m = vf.model("head0")            # Model(size=(x, y, z), vox=np.uint8[x,y,z])
    m.vox[...] = 0; vf.palette[5] = (r, g, b, 255)
    vf.save(out)

Voxel value 0 is empty; values 1..255 index palette entry value-1 in RGBA
(the file convention).  `vf.palette` is indexed by voxel value, with
`vf.palette[0]` unused.
"""
import struct
import numpy as np


def _rdict(b, o):
    n, = struct.unpack_from("<i", b, o)
    o += 4
    r = {}
    for _ in range(n):
        ln, = struct.unpack_from("<i", b, o)
        k = b[o + 4:o + 4 + ln].decode("latin1")
        o += 4 + ln
        ln, = struct.unpack_from("<i", b, o)
        v = b[o + 4:o + 4 + ln].decode("latin1")
        o += 4 + ln
        r[k] = v
    return r, o


def _wdict(d):
    out = [struct.pack("<i", len(d))]
    for k, v in d.items():
        kb, vb = k.encode("latin1"), str(v).encode("latin1")
        out += [struct.pack("<i", len(kb)), kb, struct.pack("<i", len(vb)), vb]
    return b"".join(out)


class Model:
    def __init__(self, size, vox):
        self.size = tuple(size)
        self.vox = vox

    def xyzi(self):
        xs, ys, zs = np.nonzero(self.vox)
        idx = self.vox[xs, ys, zs]
        arr = np.stack([xs, ys, zs, idx], 1).astype(np.uint8)
        return struct.pack("<i", len(arr)) + arr.tobytes()


class VoxFile:
    def __init__(self):
        self.version = 150
        self.chunks = []        # [(id, content)] children of MAIN, in order
        self.models = []        # Model per SIZE/XYZI pair, in file order
        self.palette = np.zeros((256, 4), np.uint8)
        self.names = {}         # part name -> model index (via nTRN -> nSHP)
        self.trans = {}         # part name -> (x, y, z) from nTRN `_t`

    @classmethod
    def load(cls, path):
        d = open(path, "rb").read()
        if d[:4] != b"VOX ":
            raise ValueError("not a .vox file: %s" % path)
        vf = cls()
        vf.version, = struct.unpack_from("<i", d, 4)
        o = 8 + 12              # skip the MAIN header
        size = None
        nodes = {}
        while o < len(d):
            cid = d[o:o + 4].decode("latin1")
            n, m = struct.unpack_from("<ii", d, o + 4)
            c = d[o + 12:o + 12 + n]
            o += 12 + n + m
            if cid == "SIZE":
                size = struct.unpack("<iii", c)
                vf.chunks.append(("SIZE", len(vf.models)))
                continue
            if cid == "XYZI":
                k, = struct.unpack_from("<i", c, 0)
                a = np.frombuffer(c, np.uint8, k * 4, 4).reshape(-1, 4)
                vox = np.zeros(size, np.uint8)
                vox[a[:, 0], a[:, 1], a[:, 2]] = a[:, 3]
                vf.chunks.append(("XYZI", len(vf.models)))
                vf.models.append(Model(size, vox))
                continue
            if cid == "RGBA":
                vf.palette[1:] = np.frombuffer(c, np.uint8, 255 * 4).reshape(-1, 4)
                vf.chunks.append(("RGBA", c[255 * 4:256 * 4]))
                continue
            if cid in ("nTRN", "nGRP", "nSHP"):
                nid, = struct.unpack_from("<i", c, 0)
                attr, p = _rdict(c, 4)
                if cid == "nTRN":
                    child, = struct.unpack_from("<i", c, p)
                    frame, _ = _rdict(c, p + 16)
                    nodes[nid] = ("T", attr, child, frame)
                elif cid == "nSHP":
                    mid, = struct.unpack_from("<i", c, p + 4)
                    nodes[nid] = ("S", mid)
            vf.chunks.append((cid, c))
        for nid, nd in nodes.items():
            if nd[0] == "T" and "_name" in nd[1]:
                sh = nodes.get(nd[2])
                if sh and sh[0] == "S":
                    vf.names[nd[1]["_name"]] = sh[1]
                    t = nd[3].get("_t", "0 0 0").split()
                    vf.trans[nd[1]["_name"]] = tuple(int(v) for v in t)
        return vf

    def model(self, name):
        return self.models[self.names[name]]

    def set_translation(self, name, t):
        """Rewrite the `_t` of the nTRN node that carries part `name`."""
        for i, (cid, c) in enumerate(self.chunks):
            if cid != "nTRN":
                continue
            nid, = struct.unpack_from("<i", c, 0)
            attr, p = _rdict(c, 4)
            if attr.get("_name") != name:
                continue
            child, res, layer, nf = struct.unpack_from("<iiii", c, p)
            frame, _ = _rdict(c, p + 16)
            frame["_t"] = "%d %d %d" % tuple(t)
            self.chunks[i] = ("nTRN", struct.pack("<i", nid) + _wdict(attr)
                              + struct.pack("<iiii", child, res, layer, nf) + _wdict(frame))
            self.trans[name] = tuple(t)
            return
        raise KeyError(name)

    def save(self, path):
        body = []
        for cid, c in self.chunks:
            if cid == "SIZE":
                c = struct.pack("<iii", *self.models[c].size)
            elif cid == "XYZI":
                c = self.models[c].xyzi()
            elif cid == "RGBA":
                c = self.palette[1:].tobytes() + c
            body.append(cid.encode("latin1") + struct.pack("<ii", len(c), 0) + c)
        body = b"".join(body)
        with open(path, "wb") as f:
            f.write(b"VOX " + struct.pack("<i", self.version))
            f.write(b"MAIN" + struct.pack("<ii", 0, len(body)) + body)
