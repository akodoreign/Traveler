"""Fit Hiruma's generated W101 with a compact shaft ornament."""
import argparse
from pathlib import Path

import bpy
import numpy as np

from hunyuan_weapon import (
    FITS, PolygonMesh, assign, bind, buildPolygonMesh, clearCaches, coordinates,
    fit_grip, read_mesh, saveModelData, savePolygonMesh, textured_material,
)


def smooth_range(y, start, end):
    q = np.clip((y - start) / (end - start), 0., 1.)
    return q * q * (3. - 2. * q)


def sculpt(source, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    clearCaches()
    (out / "tex").mkdir(parents=True, exist_ok=True)

    spear = read_mesh(source)
    length, fraction, inverted = FITS["yari"]
    fit_grip(spear, length * 1.00037, fraction, inverted)
    points = coordinates(spear)

    # The sculpt's protruding shaft band sits above the grip and below the head.
    # Keep the hand at y=0 and leave the blade and butt fully unchanged.
    height = points[:, 1].copy()
    ornament = smooth_range(height, 4., 9.) * (1. - smooth_range(height, 31., 39.))
    shrink = 1. - .51 * ornament
    points[:, 0] *= shrink
    points[:, 2] = .62 + (points[:, 2] - .62) * shrink
    points[:, 1] = np.interp(height, (-100., 4., 8., 33., 39., 100.), (-100., 4., 12., 30., 39., 100.))

    assign(spear, points)
    textured_material(spear, "hunyuan_weapon_yari", out)
    spear.data.polygons.foreach_set("use_smooth", np.ones(len(spear.data.polygons), dtype=bool))
    bind(spear, "weapon")
    spear.name = "W101"
    mesh = PolygonMesh()
    buildPolygonMesh(spear, spear.data, mesh, ["weapon"])
    mesh.aabb = [-125, -60, -125, 125, 165, 125]
    saveModelData(mesh, str(out / "W101.mdl"))
    savePolygonMesh(mesh, str(out / "W101.pm"), "W101", None, None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    sculpt(args.source, args.out)
