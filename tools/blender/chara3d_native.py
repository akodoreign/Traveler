"""Export an opt-in Natsuko test actor as native weighted RPG-Cobo meshes."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_tools" / "rpgcobo-tool" / "work"))
from blender_rpgcobo import clearCaches, convertToPM, saveModelData, saveMotionData, savePolygonMesh


def animate(scene, name, frames, family):
    rig = c.make_armature(c.rest_frames())
    rig.name = name
    scene.frame_start, scene.frame_end = 0, len(frames) - 1
    previous = {}
    for i, (kind, index, count) in enumerate(frames):
        pose = c.pose_frames(c.poses.controls(kind, index, count, family))
        for bone in rig.pose.bones:
            target = pose[bone.name]
            transform = bone.bone.matrix_local.inverted() @ c.matrix(target) if target else Matrix.Identity(4)
            bone.matrix_basis = transform
            if target is None:
                bone.scale = (0., 0., 0.)
            elif bone.name in previous:
                q = bone.rotation_quaternion.copy()
                q.make_compatible(previous[bone.name])
                bone.rotation_quaternion = q
            previous[bone.name] = bone.rotation_quaternion.copy()
            for path in ("location", "rotation_quaternion", "scale"):
                bone.keyframe_insert(path, frame=i, group=bone.name)
    scene.frame_set(0)
    return rig


def save_piece(scene, out, rig, name, skin, motion=None, write_motion=False, texture_uv=None,
               alpha_test=False, surface=None):
    obj = skin.build(rig)
    mesh = obj.data
    if surface:
        import bmesh

        edit = bmesh.new()
        edit.from_mesh(mesh)
        bmesh.ops.triangulate(edit, faces=[face for face in edit.faces if len(face.verts) > 4])
        edit.to_mesh(mesh)
        edit.free()
        mesh.update()
    materials = list(mesh.materials)
    mesh.color_attributes.remove(mesh.color_attributes["part"])
    uvs = mesh.uv_layers.new(name="UVMap")
    if texture_uv:
        palette = sorted(set(skin.colour))
        for face in mesh.polygons:
            rgb = palette[face.material_index]
            for i in face.loop_indices:
                uvs.data[i].uv = texture_uv(rgb, mesh.vertices[mesh.loops[i].vertex_index].co)
        white = bpy.data.materials.new("gear")
        white.diffuse_color = (1, 1, 1, 1)
        mesh.materials.clear()
        mesh.materials.append(white)
        mesh.polygons.foreach_set("material_index", [0] * len(mesh.polygons))
        for mat in materials:
            bpy.data.materials.remove(mat)
        materials = [white]
    for mat in materials:
        if mat.node_tree is None:
            mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = mat.diffuse_color
    if surface:
        surface.apply(mesh, uvs, materials)
    # Subsequent geometry uses the same bind pose, not a resampling of every animation.
    if write_motion:
        data = convertToPM(scene, obj, {"export_mesh": True, "export_anime": True})
        saveMotionData(data.mot, str(out / f"{motion}.mot"))
    else:
        from blender_rpgcobo.pm_convert import PolygonMesh, buildPolygonMesh
        data = PolygonMesh()
        buildPolygonMesh(obj, mesh, data, [g.name for g in obj.vertex_groups])
    if not data.wmapname:
        raise RuntimeError(f"No weights exported for {name}")
    if surface:
        surface.restore_tints(data, materials)
    if alpha_test:
        for face in data.face:
            face.mate.alphatest = 1
            face.mate.alpharef = 1.0
    data.aabb = [-125, -60, -125, 125, 165, 125]
    saveModelData(data, str(out / f"{name}.mdl"))
    savePolygonMesh(data, str(out / f"{name}.pm"), name, motion, None)
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(mesh)
    for mat in materials:
        bpy.data.materials.remove(mat)


def outfit(spec, name):
    skin = c.Skin()
    for layer in c.OUTFITS[name]:
        layer(skin, spec)
    return skin


def export(job):
    out = Path(job["out"])
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    clearCaches()
    if "models" not in job:
        spec = job["spec"]
        rig = animate(scene, "rig", job["frames"], job["family"])
        spear = c.Skin()
        c.weapon(spear, spec, "yari")
        for name, skin in (("body", c.build_character(spec, "bare", "none")),
                           ("armor", outfit(spec, "armored")), ("robe", outfit(spec, "robe")), ("spear", spear)):
            save_piece(scene, out, rig, name, skin, "rig", write_motion=name == "body")
        return

    if job.get("body_only"):
        rig = c.make_armature(c.rest_frames())
        for key, spec, family, _ in job["models"]:
            save_piece(scene, out, rig, key + "_body", c.build_character(spec, "bare", "none"), f"motion_{family}")
        return

    def save_mask(key, spec, rig):
        if spec.get("mask"):
            mask = c.Skin()
            c.signature_mask(mask, spec)
            save_piece(scene, out, rig, f"{key}_mask", mask)

    if job.get("accessories"):
        rig = c.make_armature(c.rest_frames())
        for key, spec, family, _ in job["models"]:
            if spec.get("ear_ornament") or spec.get("head_tattoo") or spec.get("glasses"):
                save_piece(scene, out, rig, key + "_body", c.build_character(spec, "bare", "none"), f"motion_{family}")
            save_mask(key, spec, rig)
            default = spec.get("build", "normal")
            dressed = "armored" if default.startswith("armored") or default == "heavy" else "robe"
            save_piece(scene, out, rig, key + "_outfit", outfit(spec, dressed))
        return

    rigs = {}
    for key, spec, family, weapon in job["models"]:
        print(f"NATIVE {key}", flush=True)
        default = spec.get("build", "normal")
        dressed = "armored" if default.startswith("armored") or default == "heavy" else "robe"
        motion = f"motion_{family}"
        fresh = family not in rigs
        if fresh:
            rigs[family] = animate(scene, motion, job["motions"][family], family)
        rig = rigs[family]
        save_piece(scene, out, rig, key + "_body", c.build_character(spec, "bare", "none"), motion, fresh)
        save_piece(scene, out, rig, key + "_outfit", outfit(spec, dressed))
        save_mask(key, spec, rig)
        if weapon != "none":
            gear = c.Skin()
            c.weapon(gear, spec, weapon)
            save_piece(scene, out, rig, key + "_weapon", gear)


if __name__ == "__main__":
    with open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8") as file:
        export(json.load(file))
