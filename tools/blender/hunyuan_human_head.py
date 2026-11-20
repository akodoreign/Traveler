"""Fit a textured Hunyuan head to Traveler's native human neck and head bone."""
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c
from chara3d_native import saveModelData, savePolygonMesh
from blender_rpgcobo.pm_convert import PolygonMesh, buildPolygonMesh


def facial_shapes(face, raw_bounds, fit_matrix, features):
    """Add independent blink, brow and mouth controls in the cropped bust's view."""
    basis = face.shape_key_add(name="Basis")
    count = len(basis.data)
    neutral = np.empty(count * 3, np.float32)
    basis.data.foreach_get("co", neutral)
    neutral = neutral.reshape(count, 3)
    inv = np.asarray(fit_matrix.inverted())
    original = neutral @ inv[:3, :3].T + inv[:3, 3]
    origin = raw_bounds.mean(axis=0)
    span = np.ptp(raw_bounds, axis=0)
    factor = 480 * .78 / span.max()
    x = (original[:, 1] - origin[1]) * factor + 240
    y = 240 - ((original[:, 2] - origin[2]) - .015 * (original[:, 0] - origin[0])) * factor
    front = np.clip((original[:, 0] - origin[0]) / (span[0] * .24), 0, 1)

    def area(mark, width, height):
        hx, hy = x - mark[0], y - mark[1]
        radius = np.sqrt((hx / width) ** 2 + (hy / height) ** 2)
        w = np.clip((1 - radius) * 2.1, 0, 1)
        return hx, hy, front * w * w * (3 - 2 * w)

    def add(name, dx, dy):
        local = np.column_stack((np.zeros(count), np.broadcast_to(dx, count), -np.broadcast_to(dy, count))) / factor
        moved = neutral + local @ np.asarray(fit_matrix.to_3x3()).T
        if np.max(np.abs(moved - neutral)) < .01:
            raise ValueError(f"{name} has no visible effect on {face.name}")
        channel = face.shape_key_add(name=name)
        channel.value = 0
        channel.data.foreach_set("co", moved.ravel())

    for side, mark in zip(("right", "left"), features["eyes"]):
        dx, dy, weight = area(mark, 33, 23)
        target = -dy + dx * mark[2] + 1.0
        add("blink_" + side, 0, target * weight * .96)
    brows = [area(mark, 31, 20) for mark in features["brows"]]
    add("brows_up", 0, sum(-11 * weight for _, _, weight in brows))
    add("brows_knit", sum(-dx * weight * .18 for dx, _, weight in brows),
        sum(8 * weight for _, _, weight in brows))
    dx, dy, weight = area(features["mouth"], 47, 27)
    add("smile", dx * weight * .27, (1.5 - .54 * np.abs(dx)) * weight)
    add("frown", -dx * weight * .07, (-1.5 + .44 * np.abs(dx)) * weight)
    add("mouth_open", -dx * weight * .22, (np.tanh(dy / 2.8) * 7 + 5) * weight)


def fit(entry, scene, rig, out):
    source = Path(entry["source"])
    key = entry["key"]
    bpy.ops.import_scene.gltf(filepath=str(source))
    face, = [item for item in scene.objects if item.type == "MESH"]
    face.data.transform(Matrix.Rotation(math.pi / 2, 4, "Z") @ face.matrix_world)
    face.matrix_world = Matrix.Identity(4)
    bounds = np.array(list(face.bound_box))
    raw_bounds = np.array([bounds.min(axis=0), bounds.max(axis=0)])
    ref = Vector(entry["anchor"])
    eyes = entry.get("features", {}).get("eyes")
    roll = math.atan2(eyes[1][1] - eyes[0][1], eyes[1][0] - eyes[0][0]) if eyes else 0
    yaw = math.radians(entry.get("yaw", 0))
    rotation = Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(roll, 4, "X")
    scale = Matrix.Scale(entry["scale"], 4)
    target = Vector(entry["target"])
    matrix = Matrix.Translation(target) @ scale @ rotation @ Matrix.Translation(-ref)
    face.data.transform(matrix)
    # Remove the part of the bust below the neck. The body supplies the lower neck.
    edit = bmesh.new()
    edit.from_mesh(face.data)
    hair = entry.get("long_hair")
    floor = hair[0] if hair else entry["trim"]
    bmesh.ops.bisect_plane(edit, geom=[*edit.verts, *edit.edges, *edit.faces], dist=.0001,
                          plane_co=(0, 0, floor), plane_no=(0, 0, 1), clear_inner=True)
    if hair:
        _, side, rear = hair
        bmesh.ops.delete(edit, geom=[v for v in edit.verts
                                    if v.co.z < entry["trim"] and abs(v.co.y) < side and v.co.x > rear],
                         context="VERTS")
    if clearance := entry.get("neck_clearance"):
        height, width, *depth = clearance
        front = depth[0] if depth else math.inf
        bmesh.ops.delete(edit, geom=[v for v in edit.verts
                                    if v.co.z < height and abs(v.co.y) > width and v.co.x < front],
                         context="VERTS")
    if len(edit.faces) < 400:
        raise ValueError("Portrait crop discarded too much geometry")
    edit.to_mesh(face.data)
    edit.free()
    offset = entry.get("head_offset")
    if pins := entry.get("neck_pins"):
        source_pins, body_pins = np.asarray(pins, dtype=float)
        offset = (body_pins - source_pins).mean(axis=0)
    if offset is not None:
        translation = Matrix.Translation(offset)
        face.data.transform(translation)
        matrix = translation @ matrix
    face.data.polygons.foreach_set("use_smooth", [True] * len(face.data.polygons))
    shades = face.data.materials[0].node_tree
    shader = next(n for n in shades.nodes if n.type == "BSDF_PRINCIPLED")
    base = shader.inputs["Base Color"].links[0].from_node.image
    tex = out / "tex"
    tex.mkdir(exist_ok=True, parents=True)
    base_path = tex / f"{key}.png"
    base.filepath_raw = str(base_path)
    base.file_format = "PNG"
    base.save()
    base.filepath = str(base_path)
    shader.inputs["Metallic"].default_value = 0
    shader.inputs["Roughness"].default_value = .76
    normal_image = bpy.data.images.new("Portrait normal", 4, 4, alpha=False)
    normal_image.colorspace_settings.name = "Non-Color"
    normal_image.pixels[:] = [.5, .5, 1., 1.] * 16
    normal_image.filepath_raw = str(tex / "portrait_flat_normal.png")
    normal_image.save()
    normal = shades.nodes.new("ShaderNodeNormalMap")
    normal_tex = shades.nodes.new("ShaderNodeTexImage")
    normal_tex.image = normal_image
    shades.links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    shades.links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    bones = face.vertex_groups.new(name="head")
    bones.add(list(range(len(face.data.vertices))), 1.0, "REPLACE")
    face.modifiers.new("Armature", "ARMATURE").object = rig
    face.parent = rig
    data = PolygonMesh()
    buildPolygonMesh(face, face.data, data, ["head"])
    data.aabb = [-15, 90, -20, 22, 145, 20]
    saveModelData(data, str(out / f"{key}.mdl"))
    savePolygonMesh(data, str(out / f"{key}.pm"), key, None, None)
    pm_text = (out / f"{key}.pm").read_text(encoding="utf8")
    stamped = tex / f"{key}_srgb.png"
    if stamped.name in pm_text:
        base_path.replace(stamped)
        base.filepath = str(stamped)
    for line in pm_text.splitlines():
        if 'texture' in line and '"' in line:
            assert (out / line.split('"')[1]).is_file(), line
    if "features" in entry:
        facial_shapes(face, raw_bounds, matrix, entry["features"])
    bpy.ops.object.select_all(action="DESELECT")
    face.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = face
    bpy.ops.export_scene.gltf(filepath=str(out / f"{key}.glb"), use_selection=True)
    bpy.data.objects.remove(face, do_unlink=True)


def main(job):
    output = Path(job["out"])
    output.mkdir(exist_ok=True, parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    rig = c.make_armature(c.rest_frames())
    for entry in job["heads"]:
        fit(entry, scene, rig, output)


if __name__ == "__main__":
    job = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    data = json.loads(job.read_text("utf8"))
    data["out"] = str(job.parent / data["out"])
    for head in data["heads"]:
        head["source"] = str(job.parent / head["source"])
    main(data)
