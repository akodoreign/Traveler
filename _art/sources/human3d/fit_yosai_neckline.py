"""Open the Yosai robe collar and smooth the actor's bare neck lighting."""
import argparse
from pathlib import Path
import struct

import numpy as np


FORMATS = {1: ">f4", 2: ">f2", 3: ">u2", 4: ">i2", 5: "u1", 6: "i1", 7: ">u4", 8: ">i4"}


def attributes(data):
    if not data.startswith(b"SMDL\0\1"):
        raise ValueError("Unexpected model format")
    offset = 14
    result = {}
    for _ in range(data[9]):
        role, fmt, _, dimension, _, _, _, count = struct.unpack_from(">6BII", data, offset)
        offset += 14
        dtype = np.dtype(FORMATS[fmt])
        result[role] = np.frombuffer(data, dtype, count * dimension, offset).reshape(count, dimension)
        offset += count * dimension * dtype.itemsize
    return result, offset


def smooth(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)


def normalized(vectors):
    return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-9)


def open_collar(points):
    front, height, side = points.T
    width = abs(side)
    neck = 1-smooth((width-4.7)/3.5)
    upper = smooth((height-90.0)/8.0)
    opening = neck*upper
    facing = smooth((front+1.0)/4.0)
    midline = (1-smooth((width-.6)/2.6))*smooth((height-88.5)/4.0)
    result = points.copy()
    result[:, 0] -= 2.5*midline*facing
    result[:, 1] -= opening*(2.8+1.1*(1-facing))
    result[:, 2] += 1.19*opening*facing*np.tanh(side/1.4)
    return result


def fit_robes(source, target):
    data = bytearray(source.read_bytes())
    mesh, _ = attributes(data)
    rest = mesh[0].astype(float)
    moved = open_collar(rest)
    select = np.max(abs(moved-rest), axis=1) > 1e-6
    if not 10 < select.sum() < len(rest)*.15:
        raise ValueError(f"Unexpected collar area in {source.name}")
    pts = rest[select]
    axes = np.eye(3)*.001
    gradient = np.stack([(open_collar(pts+axis)-open_collar(pts-axis))/.002 for axis in axes], -1)
    inverse = np.swapaxes(np.linalg.inv(gradient), 1, 2)
    normal = normalized(np.einsum("nij,nj->ni", inverse, mesh[1][select]/32767.0))
    mesh[0][select] = moved[select]
    mesh[1][select] = np.rint(normal*32767.0)
    if 8 in mesh:
        tangent = normalized(np.einsum("nij,nj->ni", gradient, mesh[8][select, :3]/32767.0))
        mesh[8][select, :3] = np.rint(tangent*32767.0)
    target.write_bytes(data)
    return int(select.sum())


def smooth_throat(source, target):
    data = bytearray(source.read_bytes())
    mesh, offset = attributes(data)
    assert data[offset+4] == 5
    # The upper chest, neck and throat have separate material groups. Give the
    # visible front join the same rounded normal field across those boundaries.
    fore, height, side = mesh[0].astype(float).T
    fade = smooth((height-93.0)/4.0)*(1-smooth((abs(side)-4.5)/2.0))
    fade *= smooth((fore+.8)/2.3)*(1-smooth((height-99.8)/1.4))*.72
    select = fade > 0
    if not 40 < select.sum() < 1000:
        raise ValueError("The shared male neck layout differs from this fit")
    original = mesh[1][select]/32767.0
    field = normalized(np.column_stack((np.maximum(.3, fore[select]-.55),
                                      1.25*(1-smooth((height[select]-95.5)/4)),
                                      side[select])))
    blend = fade[select, None]
    mesh[1][select] = np.rint(normalized(original*(1-blend)+field*blend)*32767.0)
    target.write_bytes(data)
    return int(select.sum())


def main(resources, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("side_yosai_signature.mdl", "side_yosai_signature_decal.mdl"):
        print(name, fit_robes(resources/"native_tailoring"/name, destination/name))
    print("Yosai throat normals", smooth_throat(resources/"native_human/shared_male.mdl",
                                               destination/"side_yosai_skin.mdl"))


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("resources", type=Path)
    cli.add_argument("destination", type=Path)
    main(**vars(cli.parse_args()))
