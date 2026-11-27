"""Export an overarm javelin throw for the shared native humanoid rig."""
from pathlib import Path
import sys

import bpy
import numpy as np

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source") + 1]).resolve()
sys.path.insert(0, str(TOOLS / "blender"))

import chara3d as c
from chara3d_native import convertToPM, saveModelData, savePolygonMesh
from chara3d_victory import bank
from hunyuan_weapon import FITS, assign, coordinates, fit_grip, read_mesh

FRAMES = 36


def ease(t, start, end):
    x = min(1.0, max(0.0, (t - start) / (end - start)))
    return x * x * (3.0 - 2.0 * x)


def frames():
    for i in range(FRAMES + 1):
        t = i / FRAMES
        wind = ease(t, .02, .30) * (1.0 - ease(t, .44, .60))
        release = ease(t, .43, .58) * (1.0 - ease(t, .76, .99))
        form = c.poses.controls("ready", 0, 1, "pole")
        form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (-.35, .68, .18), wind)
        form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.93, .26, .05), release)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.79, .12, -.16), wind)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.20, -.45, -.12), release)
        form["weapon"]["dir"] = c.poses.lerp(form["weapon"]["dir"], (.99, .10, -.04), wind)
        form["weapon"]["dir"] = c.poses.lerp(form["weapon"]["dir"], (1.0, .02, -.03), release)
        form["weapon"]["sep"] = None
        form["twist"] += -25 * wind + 30 * release
        form["lean"] += -10 * wind + 20 * release
        form["head_yaw"] = 8 * wind - 5 * release
        form["root"][0] += -.06 * wind + .13 * release
        form["root"][1] -= .035 * wind + .06 * release
        yield c.pose_frames(form)


def projectile(target):
    target.parent.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parents[2] / "_art" / "sources" / "human3d" / "weapons" / "yari_source.glb"
    obj = read_mesh(source)
    fit_grip(obj, *FITS["yari"])
    points = coordinates(obj)
    points = np.column_stack((points[:, 1], -points[:, 0], points[:, 2])) * .01125
    assign(obj, points)
    material, = obj.data.materials
    material.name = "hunyuan_weapon_yari"
    shader = next(n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Metallic"].default_value = .11
    shader.inputs["Roughness"].default_value = .66
    image = shader.inputs["Base Color"].links[0].from_node.image
    image.filepath = "hunyuan_weapon_yari.png"
    obj.name = "javelin_projectile"
    pm = convertToPM(bpy.context.scene, obj, {"export_anime": False, "export_mesh": True})
    pm.aabb = [*points.min(axis=0), *points.max(axis=0)]
    saveModelData(pm, str(target.with_suffix(".mdl")))
    savePolygonMesh(pm, str(target.with_suffix(".pm")), target.name, None, None)


if __name__ == "__main__":
    target = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    bank(c.make_armature(c.rest_frames()), frames(), target)
    projectile(target.parent.parent / "native_weapons" / "javelin_projectile")
