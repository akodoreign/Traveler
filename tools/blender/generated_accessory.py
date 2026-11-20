"""Place freshly generated apparel and props on the shared attachment bones."""
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c
from chara3d_native import clearCaches
from generated_wardrobe import cape_or_body_decal, save_textured_native


def sculpt(out, entry):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    clearCaches()
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(entry["source"]))
    prop, = [item for item in scene.objects if item.type == "MESH"]
    yaw = math.radians(entry.get("yaw", 90))
    pitch = math.radians(entry.get("pitch", 0))
    rotation = Matrix.Rotation(pitch, 4, "Y") @ Matrix.Rotation(yaw, 4, "Z")
    prop.data.transform(rotation @ prop.matrix_world)
    prop.matrix_world = Matrix.Identity(4)
    verts = np.array([tuple(v.co) for v in prop.data.vertices])[:, (0, 2, 1)] * (1, 1, -1)
    minimum, maximum = verts.min(axis=0), verts.max(axis=0)
    span = maximum - minimum
    x, y, z = entry["dimensions"]
    primary = next(i for i, size in enumerate((x, y, z)) if size)
    common = entry["dimensions"][primary] / span[primary]
    scale = [target / span[i] if target else common for i, target in enumerate((x, y, z))]
    anchor = minimum + np.asarray(entry.get("anchor", [.5, .5, .5])) * span
    points = (verts - anchor) * scale + np.asarray(entry["position"])
    if curve := entry.get("wrap_front"):
        points[:, 0] += curve * (1 - (2 * (verts[:, 2] - minimum[2]) / span[2] - 1) ** 2)
    prop.data.vertices.foreach_set("co", (points[:, (0, 2, 1)] * (1, -1, 1)).ravel())
    prop.data.polygons.foreach_set("use_smooth", [True] * len(prop.data.polygons))
    prop.data.update()
    rig = c.make_armature(c.rest_frames())
    bone = entry.get("bone", "head")
    if bone == "cape":
        torso = c.torso_w()
        group = {}
        for i, (forward, height, width) in enumerate(points):
            share = .25 * max(0, 1 - abs(91-height)/7) * min(1, max(0, (abs(width) - 8)/8))
            weights = {key: value * (1 - share) for key, value in torso(height).items()}
            if share:
                weights["upperN" if width > 0 else "upperF"] = share
            for key, weight in weights.items():
                if key not in group:
                    group[key] = prop.vertex_groups.new(name=key)
                group[key].add([i], weight, "REPLACE")
    else:
        prop.vertex_groups.new(name=bone).add(list(range(len(points))), 1, "REPLACE")
    prop.name = entry["key"]
    prop.parent = rig
    prop.modifiers.new("Attachment rig", "ARMATURE").object = rig
    save_textured_native(out, entry, prop)
    if entry.get("decal"):
        cape_or_body_decal(out, entry, prop, points, rig)
    bpy.ops.export_scene.gltf(filepath=str(out / f'{entry["key"]}.glb'))
    print("GENERATED ATTACHMENT", entry["key"], flush=True)


if __name__ == "__main__":
    plan = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    job = json.loads(plan.read_text("utf8"))
    for entry in job["parts"]:
        entry["source"] = plan.parent / entry["source"]
        sculpt(plan.parent / job["out"], entry)
