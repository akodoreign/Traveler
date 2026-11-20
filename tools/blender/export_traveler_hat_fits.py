"""Stage head-bone hat fits from fresh source geometry and existing generated materials."""
import argparse
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

import chara3d as c
from chara3d_decals import project
from chara3d_native import save_piece
from hunyuan_weapon import (
    PolygonMesh, assign, bind, buildPolygonMesh, clearCaches, coordinates, read_mesh, saveModelData,
)


# The first profile moves the broad rim down to the scalp and keeps room above
# Rensei's topknot. Sayo's cap sits flatter and further forward on her head.
FITS = {
    "trav_rensei": {
        "item": "A170", "dims": (43., 15., 43.), "base": 121.,
        "source_height": (121., 125., 127., 131., 136.),
        "fit_height": (112.3, 116.5, 120.3, 128.3, 136.4),
        "x_shift": -.7, "z_shift": -.4, "width": .99, "tilt": -.025,
    },
    "trav_sayo": {
        "item": "A102", "dims": (36., 14., 36.), "base": 121.,
        "source_height": (121., 135.), "fit_height": (114.2, 128.2),
        "x_shift": -.7, "z_shift": -.45, "width": 1.02, "tilt": -.015,
    },
}


def build(actor, spec, source, templates, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    clearCaches()
    id_ = spec["item"]
    key = f"{actor}_{id_}"
    prop = read_mesh(source / f"traveler_accessory_{id_}_00001_.glb")
    prop.data.transform(Matrix.Rotation(np.pi / 2., 4, "Z"))
    points = coordinates(prop)
    low, high = points.min(axis=0), points.max(axis=0)
    anchor = low + np.array((.5, 0., .5)) * (high - low)
    points = (points - anchor) * (np.array(spec["dims"]) / (high - low))
    points += (0., spec["base"], 0.)
    bind(prop, "head")

    proxy = c.Skin()
    proxy.verts = points
    proxy.faces = [tuple(face.vertices) for face in prop.data.polygons]
    proxy.weights = [{"head": 1.}] * len(points)
    decal, uv = project(id_, "head", proxy)

    source_height = spec["source_height"]
    fit_height = spec["fit_height"]
    x_shift, z_shift, tilt, width = (spec[k] for k in ("x_shift", "z_shift", "tilt", "width"))

    def fit(verts):
        p = np.array(verts, dtype=float, copy=True)
        p[:, 1] = np.interp(p[:, 1], source_height, fit_height) + tilt * p[:, 0]
        p[:, 0] += x_shift
        p[:, 2] = p[:, 2] * width + z_shift
        return p

    def decal_uv(color, position):
        x, minus_z, y = position
        x -= x_shift
        z = (-minus_z - z_shift) / width
        y = np.interp(y - tilt * x, fit_height, source_height)
        return uv(color, (x, -z, y))

    assign(prop, fit(points))
    prop.data.polygons.foreach_set("use_smooth", np.ones(len(prop.data.polygons), dtype=bool))
    prop.name = key
    mesh = PolygonMesh()
    buildPolygonMesh(prop, prop.data, mesh, ["head"])
    mesh.aabb = [-125, -60, -125, 125, 165, 125]
    saveModelData(mesh, str(out / f"{key}.mdl"))
    template = (templates / f"{id_}.pm").read_text(encoding="utf-8")
    (out / f"{key}.pm").write_text(template.replace(f'"{id_}.mdl"', f'"{key}.mdl"'), encoding="utf-8")

    decal.verts = [tuple(v) for v in fit(decal.verts)]
    rig = c.make_armature(c.rest_frames())
    save_piece(bpy.context.scene, out, rig, key + "_decal", decal, texture_uv=decal_uv, alpha_test=True)
    return {"mesh": key, "dyed": True, "palette": id_, "decal": id_}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("templates", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    routes = {f'{actor}:{spec["item"]}': build(actor, spec, args.source, args.templates, args.out)
              for actor, spec in FITS.items()}
    (args.out / "head-fit-additions.json").write_text(json.dumps(routes, indent=2) + "\n", encoding="utf-8")
