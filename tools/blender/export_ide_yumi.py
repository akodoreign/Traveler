"""Stage a tall, hand-centered native yumi for each bow Ide Tamotsu can equip."""
import argparse
import json
from pathlib import Path

import bpy
import numpy as np

from hunyuan_weapon import (
    FITS, PolygonMesh, assign, bind, buildPolygonMesh, clearCaches, coordinates,
    fit_grip, read_mesh, saveModelData, savePolygonMesh, textured_material,
)


def export(source, game, out):
    weapons = json.loads((game / "resource/native_weapons/weapons.json").read_text(encoding="utf-8"))
    data = json.loads((game / "data/weapon.json").read_text(encoding="utf-8"))
    bow_ids = [item for item, spec in weapons["items"].items() if spec["kind"] == "yumi"]
    (out / "tex").mkdir(parents=True, exist_ok=True)
    length, fraction, inverted = FITS["yumi"]
    for item in bow_ids:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        clearCaches()
        bow = read_mesh(source)
        # Match the installed exporter’s per-item dimensions before lengthening.
        item_length = length * (1. + (int(item[1:]) - 100) * .00037)
        fit_grip(bow, item_length, fraction, inverted)
        points = coordinates(bow)
        points[:, 1] *= 104. / item_length if item == "W104" else 2.
        assign(bow, points)
        textured_material(bow, "hunyuan_weapon_yumi", out)
        bow.data.polygons.foreach_set("use_smooth", np.ones(len(bow.data.polygons), dtype=bool))
        bind(bow, "weapon")
        bow.name = item
        mesh = PolygonMesh()
        buildPolygonMesh(bow, bow.data, mesh, [group.name for group in bow.vertex_groups])
        if "jade" in data[item]["name"].casefold():
            for face in mesh.face:
                face.mate.basecol = 0x91f1bbff
        mesh.aabb = [-125, -60, -125, 125, 165, 125]
        saveModelData(mesh, str(out / (item + ".mdl")))
        savePolygonMesh(mesh, str(out / (item + ".pm")), item, None, None)
        print(f"{item} {data[item]['name']}: {points[:, 1].min():.2f} to {points[:, 1].max():.2f} about the original grip", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("game", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    export(args.source, args.game, args.out)
