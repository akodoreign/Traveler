"""Fit textured Hunyuan weapon sculpts to Traveler's existing hand and saya bones."""
import json
from pathlib import Path
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix

import chara3d as c
from chara3d_native import clearCaches, saveModelData, savePolygonMesh
from blender_rpgcobo.pm_convert import PolygonMesh, buildPolygonMesh

# Length and grip fraction in model space. The source stores some swords tip-down.
FITS = {
    "katana": (44., .163, True), "kakita": (45., .161, True),
    "tanto": (20.5, .233, False), "nodachi": (57., .136, False),
    "bokken": (35., .127, False), "bo": (107., .523, False),
    "yari": (118., .475, False), "naginata": (120., .467, False),
    "shakujo": (115., .461, False), "yumi": (52., .43, False),
    "tetsubo": (116., .151, False), "musket": (61., .32, False),
    "kama": (21., .237, False), "fan": (15., .12, False),
    "nunchaku": (22., .20, False), "claws": (11., .27, True),
}
SWORDS = {"katana", "kakita", "tanto", "nodachi"}
SAYA_LENGTHS = {"katana": 34., "kakita": 35., "tanto": 12.7, "nodachi": 48.}


def read_mesh(path):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    mesh, = [o for o in bpy.context.scene.objects if o not in before and o.type == "MESH"]
    mesh.data.transform(mesh.matrix_world)
    mesh.parent = None
    mesh.matrix_world = Matrix.Identity(4)
    return mesh


def coordinates(obj):
    positions = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", positions)
    return positions.reshape(-1, 3)[:, (0, 2, 1)] * (1, 1, -1)


def assign(obj, points):
    obj.data.vertices.foreach_set("co", (points[:, (0, 2, 1)] * (1, -1, 1)).ravel())
    obj.data.update()


def fit_grip(obj, length, fraction, inverted):
    points = coordinates(obj)
    if inverted:
        points[:, :2] *= -1
    low, high = map(float, np.quantile(points[:, 1], [0, 1]))
    span = high - low
    level = low + span * fraction
    section = points[abs(points[:, 1] - level) < span * .018]
    if len(section) < 15:
        raise ValueError(f"No grip section on {obj.name}")
    grip = np.median(section, axis=0)
    grip[1] = level
    assign(obj, (points-grip) * length / span)


def bind(obj, bone):
    obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))), 1., "REPLACE")


def clone(obj):
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.context.scene.collection.objects.link(copy)
    return copy


def mount(obj, place, direction, sideways=c.EX):
    x, y, z = c.frame(np.zeros(3), direction, sideways)[1:]
    points = coordinates(obj)
    assign(obj, points @ np.column_stack((x, y, z)).T + place)


def only_hilt(obj, position):
    edit = bmesh.new()
    edit.from_mesh(obj.data)
    bmesh.ops.bisect_plane(edit, geom=[*edit.verts, *edit.edges, *edit.faces], dist=.0001,
                          plane_co=(0, 0, position), plane_no=(0, 0, 1), clear_outer=True)
    if len(edit.faces) < 30:
        raise ValueError("Weapon hilt crop removed surface geometry")
    edit.to_mesh(obj.data)
    edit.free()


def textured_material(obj, key, out):
    material, = obj.data.materials
    shader = next(n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Metallic"].default_value = .11
    shader.inputs["Roughness"].default_value = .66
    image = shader.inputs["Base Color"].links[0].from_node.image
    image_path = out / "tex" / (key + ".png")
    image.filepath_raw = str(image_path)
    image.file_format = "PNG"
    stamp = image_path.with_stem(image_path.stem + "_srgb")
    if not stamp.exists():
        if not image_path.exists():
            image.save()
        image_path.replace(stamp)
    image.filepath = str(image_path)
    material.name = key
    return image, stamp


def export_weapon(out, key, kind, source, scabbard, label, preview=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    clearCaches()
    blade = read_mesh(source)
    length, grip, inverted = FITS[kind]
    if key.startswith("W") and key[1:].isdigit():
        length *= 1. + (int(key[1:]) - 100) * .00037
    fit_grip(blade, length, grip, inverted)
    textures = [textured_material(blade, "hunyuan_weapon_" + kind, out)]
    pieces = [blade]
    if kind in SWORDS:
        mouth = c.P("pelvis") + c.SAYA_AT
        direction = c.unit(np.asarray(c.poses.SAYA_DIR, dtype=float))
        hilt = clone(blade)
        only_hilt(hilt, 3.3 if kind != "tanto" else 2.1)
        mount(hilt, mouth + direction*.9, -direction)
        bind(hilt, "sheathed")
        shape = read_mesh(scabbard)
        fit_grip(shape, SAYA_LENGTHS[kind], 0., True)
        mount(shape, mouth, direction)
        textures.append(textured_material(shape, "hunyuan_weapon_saya", out))
        bind(shape, "pelvis")
        pieces += [hilt, shape]
        bind(blade, "weapon")
    elif kind == "claws":
        other = clone(blade)
        for obj, (side, sign) in zip((blade, other), c.SIDES):
            coords = coordinates(obj)
            coords[:, 2] *= sign
            assign(obj, coords + c.P("grip", sign) + (-.9, 2.1, .55 * sign))
            if sign < 0:
                obj.data.flip_normals()
            bind(obj, "hand" + side)
        pieces.append(other)
    else:
        bind(blade, "weapon")

    bpy.ops.object.select_all(action="DESELECT")
    for mesh in pieces:
        mesh.select_set(True)
        mesh.data.polygons.foreach_set("use_smooth", [True]*len(mesh.data.polygons))
    bpy.context.view_layer.objects.active = blade
    if len(pieces) > 1:
        bpy.ops.object.join()
    blade.name = key
    data = PolygonMesh()
    buildPolygonMesh(blade, blade.data, data, [group.name for group in blade.vertex_groups])
    if not data.wmapname or not data.face:
        raise ValueError(f"No exported weights or faces for {key}")
    finish = label.casefold()
    tint = 0x91f1bbff if "jade" in finish else 0xc3a999ff if "ironwood" in finish else None
    if tint:
        for face in data.face:
            if face.mate.name != "hunyuan_weapon_saya":
                face.mate.basecol = tint
    data.aabb = [-125, -60, -125, 125, 165, 125]
    saveModelData(data, str(out / f"{key}.mdl"))
    savePolygonMesh(data, str(out / f"{key}.pm"), key, None, None)
    for image, path in textures:
        image.filepath = str(path)
    if preview:
        bpy.ops.export_scene.gltf(filepath=str(out / f"{key}.glb"), use_selection=True)
    print("GENERATED WEAPON", key, kind, flush=True)


def main(plan):
    out = Path(plan["out"])
    (out / "tex").mkdir(exist_ok=True, parents=True)
    for key, spec in plan["items"].items():
        kind = spec["kind"]
        source = Path(plan["sources"][kind])
        scabbard = Path(plan["sources"]["saya"]) if kind in SWORDS else None
        export_weapon(out, key, kind, source, scabbard, spec["name"], spec.get("preview", False))


if __name__ == "__main__":
    job = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    plan = json.loads(job.read_bytes())
    plan["out"] = job.parent / plan["out"]
    plan["sources"] = {kind: job.parent / source for kind, source in plan["sources"].items()}
    main(plan)

