"""Export the Coast Road kits in RPG-Cobo's native mesh format."""

import json
from pathlib import Path
import re
import struct
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
STAGE = HERE / "native_environment"
SRC = HERE / "voxel_sources"


class Geometry:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.uvs = []
        self.materials = []

    def quad(self, points, uv, material):
        begin = len(self.vertices)
        self.vertices.extend(points)
        self.faces.append(tuple(range(begin, begin + 4)))
        self.uvs.append(uv)
        self.materials.append(material)


def export(name, geom, maps):
    points = np.asarray(geom.vertices, dtype=np.float32)
    native = points[:, [0, 2, 1]]
    sculpt = points.reshape(-1, 4, 3)
    normals = np.cross(sculpt[:, 1] - sculpt[:, 0], sculpt[:, 2] - sculpt[:, 0])
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    normals = np.repeat(np.rint(normals[:, [0,2,1]] * 32767), 4, axis=0)
    uv = np.asarray(geom.uvs, dtype=np.float32).reshape(-1, 2)
    uv[:, 1] = 1. - uv[:, 1]
    mats = dict.fromkeys(geom.materials)
    # SMDL v1 vertex streams are planar on disk. Offsets and stride describe
    # the engine's interleaved position, packed normal and float UV buffers.
    stride = 32
    data = bytearray(b"SMDL\x00\x01\x00\x00\x00\x03")
    data += struct.pack(">I", len(points) * stride)
    for role, kind, normalize, width, offset, values, dtype in (
        (0, 1, 0, 3, 0, native, ">f4"), (1, 4, 1, 3, 12, normals, ">i2"),
        (4, 1, 0, 2, 24, uv, ">f4"),
    ):
        data += struct.pack(">6BII", role, kind, normalize, width, stride, 0, offset, len(points))
        data += values.astype(dtype).tobytes()
    data += bytes(4) + bytes([len(mats)])
    declarations = []
    for key in mats:
        # Swap winding with the Blender-to-native depth/up coordinate swap.
        first = 4 * np.flatnonzero(np.asarray(geom.materials) == key)
        ix = (first[:, None] + [0, 2, 1, 0, 3, 2]).reshape(-1)
        kind, dtype = (7, ">u4") if ix.max() > 65535 or len(ix) > 65535 else (3, ">u2")
        raw = ix.astype(dtype).tobytes()
        data += struct.pack(">4BII", 4, 0, 0, kind, len(raw), len(ix)) + raw + bytes(4)
        texture, roughness = maps[key]
        params = {"glow": "0xff160000", "lava": "0xff600000"}.get(key, "0xff000000")
        assert (STAGE / "tex" / texture).is_file()
        declarations.append(f"""  {{
    name = "{key}"
    tec = "pbr.basic"
    mtype = 0
    basecol = 0xffffffff
    rough = {roughness:.4f}
    metal = 0.0
    mparam = {params}
    texmap = 0
    texture0 = "tex/{texture}"
    texture1 = null
    texture2 = null
  }}""")
    data += bytes(14)
    (STAGE / f"{name}.mdl").write_bytes(data)
    lower, upper = native.min(axis=0), native.max(axis=0)
    bound = np.concatenate(((lower+upper)*.5, np.maximum((upper-lower)*.5, .015)))
    desc = "\n".join(declarations)
    (STAGE / f"{name}.pm").write_text(
        f'return {{\nmodeldata = "{name}.mdl"\nbnd = {bound.tolist()}\nmaterial = [\n{desc}\n]\n}}\n',
        encoding="utf-8", newline="\n")
    print(f"COAST {name}: {len(geom.faces)} quads, {list(mats)}")


def terrain(id_, data):
    floor, water = Geometry(), Geometry()
    repeats = {"sand": 4.8, "path": 5.3, "meadow": 3.2, "cliff": 4.9, "water": 8.}
    for tag, x, z, right, far, height in data["top"]:
        scale = repeats[tag]
        lift = {"water": .023, "meadow": .092}.get(tag,.019)
        points = [(a, b, height + lift) for a, b in ((x,z),(right,z),(right,far),(x,far))]
        uv = [(a/scale,b/scale) for a,b,_ in points]
        (water if tag == "water" else floor).quad(points, uv, tag)
    for x, z, low, high, dx, dz in data["cliff"]:
        epsilon = .009
        if dx < 0:
            a, b = (x-epsilon,z+.5), (x-epsilon,z)
        elif dx > 0:
            a, b = (x+.5+epsilon,z), (x+.5+epsilon,z+.5)
        elif dz < 0:
            a, b = (x,z-epsilon), (x+.5,z-epsilon)
        else:
            a, b = (x+.5,z+.5+epsilon), (x,z+.5+epsilon)
        box = [(a[0],a[1],low), (b[0],b[1],low), (b[0],b[1],high), (a[0],a[1],high)]
        uv = [((p[1] if dx else p[0])/4., p[2]/3.2) for p in box]
        floor.quad(box, uv, "cliff")
    name = id_.lower()
    export(name + "_surfaces", floor, {s: (f"{s}.png", .9) for s in ("sand","path","meadow","cliff")})
    export(name + "_water", water, {"water": ("surf00.png", .32)})


def voxel_asset(key, hot_material=False):
    data = np.load(SRC / f"{key}.npz")
    coordinates, colors, pitch = data["points"], data["colors"], data["pitch"]
    distinct, slots = np.unique(colors, axis=0, return_inverse=True)
    palette = np.zeros((128, 128, 3), np.uint8)
    for k, color in enumerate(distinct):
        x, y = (k % 8) * 16, (k // 8) * 16
        palette[y:y+16, x:x+16] = color
    file = f"{key}.png"
    Image.fromarray(palette[::-1]).save(STAGE / "tex" / file)
    occupied = set(map(tuple, coordinates))
    geometry = Geometry()
    center = np.append((coordinates.max(0)[:2] + 1) * .5, 0.)
    one = np.eye(3, dtype=int)
    for p, slot in zip(coordinates, slots, strict=True):
        u, v = ((slot % 8) * 16 + 8.) / 128, ((slot // 8) * 16 + 8.) / 128
        for axis, base in enumerate(one):
            k, l = one[(axis+1) % 3], one[(axis+2) % 3]
            for step in (-1, 1):
                if tuple(p + step * base) in occupied:
                    continue
                a = p + base if step > 0 else p
                loop = (a, a+k, a+k+l, a+l) if step > 0 else (a, a+l, a+k+l, a+k)
                vertices = [tuple((corner-center)*pitch) for corner in loop]
                color = distinct[slot].astype(int)
                material = "lava" if hot_material and color[0] > 145 and color[0] > color[2] * 2 else key
                geometry.quad(vertices, [(u, v)]*4, material)
    export(key, geometry, {key: (file, .84), "lava": (file, .55)})
    return geometry


if __name__ == "__main__":
    for mid, floor in json.loads((HERE / "coast-map-data.json").read_bytes()).items():
        terrain(mid, floor)
    for item in json.loads((SRC / "manifest.json").read_bytes()):
        voxel_asset(item["name"])
