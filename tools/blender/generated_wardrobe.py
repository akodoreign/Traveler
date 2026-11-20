"""Fit a newly generated garment and project its decals onto the fitted cloth."""
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c
from chara3d_decals import project
from chara3d_native import clearCaches, saveModelData, savePolygonMesh, save_piece
from blender_rpgcobo.pm_convert import PolygonMesh, buildPolygonMesh
from generated_human_body import add_fit_controls, assign_weights, ease, fit_to_bind
from gear_palette import CLAN_ROLES, NATIVE_CLANS
from human_body_fit import Build, garment_regions, reshape


def save_pixels(path, values, linear=False):
    height, width = values.shape[:2]
    image = bpy.data.images.new(path.stem, width=width, height=height, alpha=False)
    rgba = np.ones((height, width, 4), dtype=np.float32)
    rgba[:, :, :3] = values
    if linear:
        image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(rgba.reshape(-1))
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    return image


def surface_normal(path, rgb):
    value = rgb @ np.array((.24, .67, .09))
    dx = .8 * (np.roll(value, -1, axis=1) - np.roll(value, 1, axis=1))
    dy = .8 * (np.roll(value, -1, axis=0) - np.roll(value, 1, axis=0))
    normals = np.stack((-dx, -dy, np.ones_like(dx)), axis=2)
    normals /= np.linalg.norm(normals, axis=2, keepdims=True)
    return save_pixels(path, normals * .5 + .5, True)


def dyes(out, key, rgb, source_roles):
    """Change the dye colors while preserving the baked folds and fiber contrast."""
    anchors = np.asarray([source_roles[role] for role in CLAN_ROLES], dtype=float) / 255
    normalized = rgb / np.maximum(.05, rgb.max(axis=2, keepdims=True))
    comparison = anchors / np.maximum(.05, anchors.max(axis=1, keepdims=True))
    hue = ((normalized[:, :, None] - comparison[None, None]) ** 2).sum(axis=3)
    power = ((rgb.max(axis=2)[:, :, None] - anchors.max(axis=1)) ** 2)
    distribution = np.exp(-12 * hue - 4 * power)
    distribution /= np.maximum(1e-6, distribution.sum(axis=2, keepdims=True))
    original = distribution @ anchors
    shade = np.clip(rgb.max(axis=2) / np.maximum(.055, original.max(axis=2)), .22, 1.49)
    for clan, palette in NATIVE_CLANS.items():
        directory = out / "tex" / clan
        directory.mkdir(exist_ok=True, parents=True)
        tint = distribution @ (np.asarray(palette) / 255)
        color = np.clip(tint * shade[:, :, None], 0, 1)
        image = save_pixels(directory / f"{key}.png", color)
        bpy.data.images.remove(image)


def cape_or_body_decal(out, item, obj, points, rig):
    proxy = c.Skin()
    proxy.verts = points
    proxy.faces = [tuple(face.vertices) for face in obj.data.polygons]
    names = [group.name for group in obj.vertex_groups]
    proxy.weights = [{names[group.group]: group.weight for group in v.groups} for v in obj.data.vertices]
    decal, uv = project(item["decal"], item.get("slot", "body"), proxy)
    save_piece(bpy.context.scene, out, rig, item["key"] + "_decal", decal, texture_uv=uv, alpha_test=True)


def shape_clearance(points, regions, base, clearance, fit_parts):
    """Center garment cross-sections around the fitted sculpt and allow for its volume."""
    body, body_regions = base["points"], base["regions"]
    height = points[:, 1]
    body_height = body[:, 1]
    envelope = points.copy()
    for part, (lower, upper) in enumerate(((71, 96), (60, 94), (4, 55))):
        if part not in fit_parts:
            continue
        sides = (0,) if part == 0 else (-1, 1)
        for side in sides:
            active = (regions[:, part] > .52) & (height >= lower) & (height <= upper)
            reference = body_regions[:, part] > .68
            if side:
                active &= points[:, 2] * side > 0
                reference &= body[:, 2] * side > 0
            rows = []
            for y in np.arange(lower, upper + 1, 2):
                cloth = points[active & (np.abs(height - y) < 2.75)][:, (0, 2)]
                skin = body[reference & (np.abs(body_height - y) < 2.75)][:, (0, 2)]
                if min(len(cloth), len(skin)) < 12:
                    continue
                cloth_ends = np.quantile(cloth, (.08, .92), axis=0)
                skin_ends = np.quantile(skin, (.06, .94), axis=0)
                center = cloth_ends.mean(axis=0)
                shift = skin_ends.mean(axis=0) - center
                radius = np.maximum(.5, np.ptp(cloth_ends, axis=0) / 2)
                target = np.ptp(skin_ends, axis=0) / 2 + clearance
                rows.append([y, *center, *shift, *np.clip(target / radius - 1, 0, 1.)])
            if len(rows) < 3:
                continue
            control = np.asarray(rows)
            indices = np.flatnonzero(active)
            reach = ease((height[indices] - lower) / 4) * ease((upper - height[indices]) / 4)
            reach *= ease((regions[indices, part] - .5) / .42)
            for axis, point_axis in enumerate((0, 2)):
                value = points[indices, point_axis]
                center = np.interp(height[indices], control[:, 0], control[:, 1 + axis])
                shift = np.interp(height[indices], control[:, 0], control[:, 3 + axis])
                scale = np.interp(height[indices], control[:, 0], control[:, 5 + axis])
                envelope[indices, point_axis] += reach * (.86 * shift + (value - center) * scale)
    return envelope


def save_textured_native(out, item, obj):
    """Write the generated mesh and its native surface atlases."""
    key = item["key"]
    tex = out / "tex"
    tex.mkdir(exist_ok=True, parents=True)
    mat, = obj.data.materials
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value = .06 if item.get("armor") else 0
    shader.inputs["Roughness"].default_value = .65 if item.get("armor") else .78
    base = shader.inputs["Base Color"].links[0].from_node.image
    base_path = tex / f"{key}_color.png"
    base.filepath_raw = str(base_path)
    base.file_format = "PNG"
    base.save()
    base.filepath = str(base_path)
    rgb = np.asarray(base.pixels[:], dtype=np.float32).reshape(base.size[1], base.size[0], 4)[:, :, :3]
    relief = nodes.new("ShaderNodeTexImage")
    relief.image = surface_normal(tex / f"{key}_normal.png", rgb)
    bump = nodes.new("ShaderNodeNormalMap")
    links.new(relief.outputs["Color"], bump.inputs["Color"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    data = PolygonMesh()
    buildPolygonMesh(obj, obj.data, data, [group.name for group in obj.vertex_groups])
    data.aabb = [-125, -60, -125, 125, 165, 125]
    saveModelData(data, str(out / f"{key}.mdl"))
    descriptor = out / f"{key}.pm"
    savePolygonMesh(data, str(descriptor), key, None, None)
    embossed = tex / f"{key}_color_srgb.png"
    if embossed.name in descriptor.read_text("utf8"):
        base_path.replace(embossed)
        base.filepath = str(embossed)
    if item.get("source_roles"):
        dyes(out, key, rgb, item["source_roles"])


def open_neckline(obj, opening):
    """Remove the generated facing that closes a V-neck garment."""
    edit = bmesh.new()
    edit.from_mesh(obj.data)
    tip, slope, offset, depth = opening
    planes = [((depth, 0, 0), (1, 0, 0)),
              ((0, offset, tip), (0, 1, slope)),
              ((0, offset, tip), (0, -1, slope))]
    for position, normal in planes:
        bmesh.ops.bisect_plane(edit, geom=[*edit.verts, *edit.edges, *edit.faces],
                              plane_co=position, plane_no=Vector(normal).normalized(), dist=.00005)
    facing = []
    for face in edit.faces:
        x, z, y = face.calc_center_median()
        if x > depth and abs(z - offset) < slope * (y - tip):
            facing.append(face)
    if not facing:
        raise ValueError(f"No neckline facing found in {obj.name}")
    bmesh.ops.delete(edit, geom=facing, context="FACES")
    bmesh.ops.triangulate(edit, faces=[face for face in edit.faces if len(face.verts) > 4])
    edit.to_mesh(obj.data)
    edit.free()
    obj.data.update()


def fitted_arm_heights(points, regions, body):
    """Match sleeve weights to the underlying arm, keeping the rim on the forearm."""
    skin = body["points"]
    forearm = (body["regions"][:, 1] > .64) & (skin[:, 1] >= 63.5) & (skin[:, 1] <= 94)
    heights = np.maximum(points[:, 1], 63.5)
    for sign in (-1, 1):
        surface = skin[forearm & (skin[:, 2] * sign > 0)]
        tree = KDTree(len(surface))
        for i, point in enumerate(surface):
            tree.insert(point, i)
        tree.balance()
        active = np.flatnonzero((regions[:, 1] > .12) & (points[:, 2] * sign > 0))
        for i in active:
            x, y, z = points[i]
            closest = tree.find_n((x, max(y, 63.5), z), 4)
            distance = np.array([item[2] for item in closest])
            height = np.array([item[0].y for item in closest])
            heights[i] = np.average(height, weights=1 / (1 + distance) ** 2)
    return heights


def plate_stiffness(points, regions):
    """Keep the breastplate on the spine, blending through its edges and straps."""
    _, height, lateral = points.T
    edge = ease((height - 72) / 4) * ease((94 - height) / 3)
    centered = ease((11.5 - abs(lateral)) / 2.6)
    return edge * centered * ease((regions[:, 0] - .52) / .35)


def fitted_garment(out, item, profile, body_points):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    clearCaches()
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(item["source"]))
    obj, = [entry for entry in scene.objects if entry.type == "MESH"]
    yaw = math.radians(item.get("yaw", 90))
    obj.data.transform(Matrix.Rotation(yaw, 4, "Z") @ obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    original = np.array([tuple(v.co) for v in obj.data.vertices])[:, (0, 2, 1)] * (1, 1, -1)
    lo, hi = original.min(axis=0), original.max(axis=0)
    center = (lo + hi) / 2
    center[1] = lo[1]
    center[0] += item.get("depth_offset", 0) * (hi[1] - lo[1])
    normalized = (original - center) / (hi[1] - lo[1])
    settings = profile | item.get("fit_overrides", {})
    points, regions = fit_to_bind(normalized, settings)
    points = shape_clearance(points, regions, body_points, item.get("clearance", .82), item.get("fit_parts", (0, 1)))
    controls = Build(**item.get("build", {}))
    fitted = reshape(points, regions, controls)
    if seat := item.get("back_collar"):
        x, y, lateral = fitted.T
        behind = ease((1.2 - x) / 3.5)
        collar = np.exp(-((y - 97.1) / 2.4) ** 2) * ease((10 - abs(lateral)) / 5)
        fitted[:, 0] -= seat * behind * collar
    fitted[:, 1] += item.get("lift", 0)
    positions = fitted[:, (0, 2, 1)] * (1, -1, 1)
    obj.data.vertices.foreach_set("co", positions.ravel())
    obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    obj.data.update()
    weights = regions.copy()
    x, y, z = fitted.T
    hang = np.zeros(len(fitted))
    if drape := item.get("drape"):
        hem, top, side, depth, strength = drape
        band = ease((y - hem) / 10) * ease((top - y) / 12)
        outer = np.maximum(ease((abs(z) - side) / 6), ease((x - depth) / 4))
        hang = strength * band * outer
    if ties := item.get("obi_ties"):
        front, hem, width, center = ties
        hold = ease((x - front) / 2.0) * ease((y - hem) / 8)
        hold *= ease((69 - y) / 4) * ease((width - abs(z - center)) / 2.8)
        hang = np.maximum(hang, hold)
    weights *= 1 - hang[:, None]
    weights[:, 0] += hang
    arm_heights = fitted_arm_heights(fitted, weights, body_points) if item.get("follow_arm_surface") else None
    plate = plate_stiffness(fitted, weights) if item.get("rigid_plates") else None
    assign_weights(obj, fitted, weights, item.get("skirt", 0), cuff=65, arm_heights=arm_heights, plate=plate)
    rig = c.make_armature(c.rest_frames())
    obj.parent = rig
    obj.modifiers.new("Outfit rig", "ARMATURE").object = rig

    key = item["key"]
    opening = item.get("neck_opening")
    if opening:
        open_neckline(obj, opening)
        fitted = np.array([tuple(v.co) for v in obj.data.vertices])[:, (0, 2, 1)] * (1, 1, -1)
        names = [group.name for group in obj.vertex_groups]
        regions = garment_regions([{names[g.group]: g.weight for g in v.groups} for v in obj.data.vertices])
        points = fitted.copy()
        points[:, 1] -= item.get("lift", 0)
        for _ in range(3):
            points += fitted - reshape(points, regions, controls) - np.array((0, item.get("lift", 0), 0))
    save_textured_native(out, item, obj)
    if item.get("decal"):
        cape_or_body_decal(out, item, obj, fitted, rig)
    add_fit_controls(obj, points, regions, controls)
    bpy.ops.export_scene.gltf(filepath=str(out / f"{key}.glb"), export_morph=True)
    print(f"GENERATED WARDROBE {key}", flush=True)


if __name__ == "__main__":
    plan = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    job = json.loads(plan.read_text("utf8"))
    profiles = json.loads((plan.parent / job["body_fit"]).read_text("utf8"))["bodies"]
    body = {profile["name"].removeprefix("shared_"): profile for profile in profiles}
    body_pack = plan.parent / job.get("body_pack", "generated-bodies")
    for garment in job["outfits"]:
        garment["source"] = plan.parent / garment["source"]
        with np.load(body_pack / f"shared_{garment['fit']}_fit.npz") as points:
            fitted_garment(plan.parent / job["out"], garment, body[garment["fit"]], points)
