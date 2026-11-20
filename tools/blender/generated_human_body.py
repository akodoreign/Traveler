"""Bind an upright Hunyuan body sculpt to Traveler's shared human skeleton."""
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c
from chara3d_native import saveModelData, savePolygonMesh
from blender_rpgcobo.pm_convert import PolygonMesh, buildPolygonMesh
from human_body_fit import Build, PREVIEWS, reshape


BODY_SKIN = (128, 112, 96)


def ease(value):
    value = np.clip(value, 0, 1)
    return value * value * (3 - 2 * value)


def fit_to_bind(points, profile):
    """Use the source joints to bring the shoulders, wrists and feet onto the bind rig."""
    depth, height, width = points.T
    signed = np.sign(width)
    side = np.abs(width)
    neck = profile["neck"]
    hip, shoulder = profile["hip"], profile["shoulder"]
    arm = np.asarray(profile["arm"])
    leg = np.asarray(profile["leg"])
    arm_center = np.interp(height, arm[:, 0], arm[:, 1])
    arm_radius = np.interp(height, arm[:, 0], arm[:, 2])
    torso_edge = np.interp(height, (0, hip, shoulder, neck), (.15, profile["hip_edge"], profile["torso_edge"], .04))
    # Blend the shoulder into the chest, keeping the lower arms independent.
    arm_border = np.maximum(torso_edge, arm_center - arm_radius * 1.15)
    if gaps := profile.get("arm_gaps"):
        heights, widths = np.asarray(gaps).T
        arm_border = np.interp(height, heights, widths)
    arm_region = ease((side - arm_border + .012) / .026)
    floor = profile.get("arm_floor", arm[0, 0])
    arm_region *= ease((height - floor + .014) / .027)
    arm_region *= ease((shoulder + .035 - height) / .056)
    leg_region = (1 - arm_region) * ease((hip + .037 - height) / .077)
    torso_region = 1 - arm_region - leg_region

    body_height = np.interp(height, (0, hip, shoulder, neck), (0, 58, 93, 101.2))
    limb_height = np.interp(height, arm[:, 0], profile.get("arm_heights", (54.8, 57.5, 61.5, 76.5, 93)))
    leg_height = np.interp(height, leg[:, 0], (0.2, 6, 31.5, 58))
    y = torso_region * body_height + arm_region * limb_height + leg_region * leg_height
    canonical_arm = np.interp(height, arm[:, 0], (13.4, 13.4, 13.2, 12.5, 11.5))
    canonical_leg = np.interp(height, leg[:, 0], (5.5, 5.5, 5.5, 5.2))
    leg_center = np.interp(height, leg[:, 0], leg[:, 1])
    limit = profile.get("limb_limit", 4.25)
    limb_width = np.clip((side - arm_center) * profile.get("limb_width", 87), -limit, limit)
    z = signed * (
        torso_region * side * profile["torso_width"] +
        arm_region * (canonical_arm + limb_width) +
        leg_region * (canonical_leg + (side - leg_center) * profile.get("leg_width", 82))
    )
    x = depth * profile["depth_scale"]
    return np.column_stack((x, y, z)), np.column_stack((torso_region, arm_region, leg_region))


def finger_weights(point, side, guides):
    """Attach fingers to their guide chains, blending into the shared palm."""
    segments = guides[side]
    names, starts, vectors, lengths, roots = segments
    relative = point - starts
    fraction = np.clip(np.sum(relative * vectors, axis=1) / lengths, 0, 1)
    distance = np.sum((relative - fraction[:, None] * vectors) ** 2, axis=1)
    first, second = np.argsort(distance)[:2]
    blend = float(ease((roots[first] + .32 - point[1]) / 1.8))
    if blend < .001:
        return {"hand" + side: 1.}
    certainty = float(ease((distance[second] - distance[first]) / 1.1))
    main = .5 + .5 * certainty
    return {"hand" + side: 1 - blend, names[first]: blend * main, names[second]: blend * (1 - main)}


def assign_weights(obj, points, regions, skirt=0, cuff=None, arm_heights=None, plate=None, bind_digits=False):
    groups = {}
    upper = c.blend((55, "pelvis"), (69, "pelvis"), (83, "spine"),
                    (91, "chest"), (96, "neck"), (100.2, "head"))
    arms = {side: c.arm_w(side) for side, _ in c.SIDES}
    legs = {side: c.leg_w(side) for side, _ in c.SIDES}
    digit_guides = {}
    if bind_digits:
        for side, sign in c.SIDES:
            bones = list(c.digit_bones(side, sign))
            starts = np.array([a for _, _, a, _ in bones])
            vectors = np.array([b-a for _, _, a, b in bones])
            roots = np.array([c.DIGIT_GUIDES[name[:-2]][0][1] for name, _, _, _ in bones])
            digit_guides[side] = ([name for name, _, _, _ in bones], starts, vectors,
                                  np.sum(vectors * vectors, axis=1), roots)
    for index, ((_, y, z), (torso, arm, leg)) in enumerate(zip(points, regions, strict=True)):
        side = "N" if z >= 0 else "F"
        blend = {}
        leg_near = np.clip(.5 + z / skirt, 0, 1) if skirt else int(side == "N")
        arm_height = y
        if arm_heights is not None:
            arm_height = arm_heights[index]
        elif cuff is not None:
            arm_height = max(y, cuff)
        arm_weights = arms[side](arm_height)
        palm = "hand" + side
        if bind_digits and arm > .6 and y < 59.82 and palm in arm_weights:
            palm_share = arm_weights.pop(palm)
            arm_weights.update((bone, weight * palm_share)
                               for bone, weight in finger_weights(points[index], side, digit_guides).items())
        for amount, definition in ((torso, upper(y)), (arm, arm_weights),
                                   (leg * leg_near, legs["N"](y)), (leg * (1-leg_near), legs["F"](y))):
            for name, value in definition.items():
                blend[name] = blend.get(name, 0) + amount * value
        if plate is not None and (stiffness := plate[index]) > 0:
            blend = {key: value * (1 - stiffness) for key, value in blend.items()}
            blend["spine"] = blend.get("spine", 0) + stiffness
        influences = sorted(blend.items(), key=lambda pair: -pair[1])[:4]
        total = sum(value for _, value in influences)
        for name, value in influences:
            if value > .00001:
                if name not in groups:
                    groups[name] = obj.vertex_groups.new(name=name)
                groups[name].add([index], value / total, "REPLACE")


def skin_and_wrap(obj, points, regions, female):
    """Separate the unadorned anatomy from the ivory base wraps."""
    mesh = obj.data
    material = mesh.materials[0]
    shader = material.node_tree.nodes.get("Principled BSDF")
    atlas = shader.inputs["Base Color"].links[0].from_node.image
    image = np.array(atlas.pixels[:], dtype=np.float32).reshape(atlas.size[1], atlas.size[0], 4)
    uvs = mesh.uv_layers.active.data
    mats = []
    for label, rgb in (("core", BODY_SKIN), ("hands", BODY_SKIN), ("neck", BODY_SKIN),
                       ("wrap", c.WHITE), ("throat", BODY_SKIN)):
        mat = bpy.data.materials.new("c%02x%02x%02x_" % rgb + label)
        mat.diffuse_color = ((rgb[0]/255)**2.2, (rgb[1]/255)**2.2, (rgb[2]/255)**2.2, 1)
        mat.use_nodes = True
        node = mat.node_tree.nodes.get("Principled BSDF")
        node.inputs["Base Color"].default_value = mat.diffuse_color
        node.inputs["Roughness"].default_value = .74
        mats.append(mat)
    mesh.materials.clear()
    for material in mats:
        mesh.materials.append(material)
    palette = []
    for face in mesh.polygons:
        vertices = list(face.vertices)
        y = points[vertices, 1].mean()
        arm = regions[vertices, 1].mean()
        upper = female and 80 < y < 93
        wrap = (51 < y < 70 or upper) and arm < .22
        if wrap:
            u, v = np.mean([uvs[key].uv for key in face.loop_indices], axis=0) % 1
            rgb = image[int(v * atlas.size[1]), int(u * atlas.size[0]), :3]
            wrap = rgb.mean() > .22 and rgb.max() - rgb.min() < .20
        x = sum(mesh.vertices[i].co.x for i in face.vertices) / len(face.vertices)
        z = abs(sum(mesh.vertices[i].co.y for i in face.vertices) / len(face.vertices))
        throat = 93.4 < y <= 97.25 and x > -.7 and z < 4.85
        collar_floor = 97.25 + 1.9 * ease((-x - .55) / 2.0)
        section = 3 if wrap else 2 if y > collar_floor else 4 if throat else 1 if arm > .55 and y < 62.4 else 0
        palette.append(section)
    mesh.polygons.foreach_set("material_index", palette)
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    if 3 not in palette:
        raise ValueError("The generated body has no identifiable plain base wrap")


def add_fit_controls(obj, points, regions, base):
    obj.shape_key_add(name="Basis")
    for name, build in PREVIEWS.items():
        extra = Build(base.muscle + build.muscle, base.weight + build.weight, base.chest + build.chest)
        deformed = reshape(points, regions, extra)
        positions = deformed[:, (0, 2, 1)] * (1, -1, 1)
        key = obj.shape_key_add(name=name)
        key.value = 0
        key.slider_min = -1
        key.data.foreach_set("co", positions.ravel())


def export(out, spec):
    out.mkdir(exist_ok=True, parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(spec["source"]))
    obj, = [item for item in scene.objects if item.type == "MESH"]
    obj.data.transform(Matrix.Rotation(math.pi / 2, 4, "Z") @ obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    raw = np.array([tuple(v.co) for v in obj.data.vertices])[:, (0, 2, 1)] * (1, 1, -1)
    lo, hi = raw.min(axis=0), raw.max(axis=0)
    reference = (lo + hi) / 2
    reference[1] = lo[1]
    neck = raw[:, 1] > hi[1] - .03 * (hi[1] - lo[1])
    reference[0] = np.median(raw[neck, 0])
    raw = (raw - reference) / (hi[1] - lo[1])
    points, regions = fit_to_bind(raw, spec)
    if palm := spec.get("palm_fit"):
        depth, scale = palm
        blend = regions[:, 1] * ease((61.5 - points[:, 1]) / 3.8)
        points[:, 0] += blend * (depth + (scale - 1) * points[:, 0])
    base = Build(**spec.get("build", {}))
    fitted = reshape(points, regions, base)
    vertices = fitted[:, (0, 2, 1)] * (1, -1, 1)
    obj.data.vertices.foreach_set("co", vertices.ravel())
    obj.data.update()
    skin_and_wrap(obj, points, regions, spec["female"])
    assign_weights(obj, points, regions, bind_digits=True)
    rig = c.make_armature(c.rest_frames())
    obj.name = spec["name"].replace("_", " ").title()
    obj.modifiers.new("Human bind rig", "ARMATURE").object = rig
    obj.parent = rig
    data = PolygonMesh()
    buildPolygonMesh(obj, obj.data, data, [group.name for group in obj.vertex_groups])
    data.aabb = [-125, -60, -125, 125, 165, 125]
    saveModelData(data, str(out / f'{spec["name"]}.mdl'))
    savePolygonMesh(data, str(out / f'{spec["name"]}.pm'), spec["name"], None, None)
    np.savez_compressed(out / f'{spec["name"]}_fit.npz', points=fitted, regions=regions)
    add_fit_controls(obj, points, regions, base)
    bpy.ops.export_scene.gltf(filepath=str(out / f'{spec["name"]}.glb'), export_morph=True)


if __name__ == "__main__":
    path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    job = json.loads(path.read_text("utf8"))
    for body in job["bodies"]:
        body["source"] = path.parent / body["source"]
        export(path.parent / job["out"], body)
