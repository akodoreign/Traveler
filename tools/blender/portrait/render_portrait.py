"""Render Natsuko turning her head beneath a stationary area light in Eevee."""

import sys
from math import radians
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

folder = Path(__file__).resolve().parent
tools = folder.parents[1]
sys.path[:0] = [str(tools / "blender"), str(tools)]
import chara3d

spec = {
    "model_key": "trav_natsuko", "face": "sharp", "female": True,
    "skin": (203, 155, 134), "hair": (53, 41, 48), "eye": (138, 65, 38),
    "hairstyle": "ponytail", "bangs": "side", "face_albedo": True,
    "ear_ornament": ("hoop", (181, 189, 196)),
    "top": (50, 60, 75), "lower": (41, 43, 65), "accent": (120, 69, 76),
    "collar": (213, 194, 184), "weapon": "none",
}

def uv_for_face(mesh):
    layer = mesh.uv_layers.new(name="Portrait albedo")
    pivot, scale = chara3d.HEAD
    for face in mesh.polygons:
        if "_face" not in mesh.materials[face.material_index].name:
            continue
        for index in face.loop_indices:
            p = mesh.vertices[mesh.loops[index].vertex_index].co
            height = pivot[1] + (p.z-pivot[1])/scale
            u = (.5-p.y/(18.*scale), (height-97.)/22.)
            layer.data[index].uv = u if p.x > 0 else (0.,0.)
    return layer.name

def skin_shader(material, painted, uv_name):
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    base = nodes.new("ShaderNodeRGB")
    base.outputs[0].default_value = (*material.diffuse_color[:3],1.)
    color = base.outputs[0]
    if "_face" in material.name:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = painted
        texture.extension = "CLIP"
        coords = nodes.new("ShaderNodeUVMap")
        coords.uv_map = uv_name
        links.new(coords.outputs["UV"], texture.inputs[0])
        mix = nodes.new("ShaderNodeMixRGB")
        links.new(texture.outputs["Alpha"],mix.inputs[0])
        links.new(color,mix.inputs[1])
        links.new(texture.outputs["Color"],mix.inputs[2])
        color = mix.outputs[0]
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.inputs["Color"].default_value = (1., 1., 1., 1.)
    rgb = nodes.new("ShaderNodeShaderToRGB")
    ramp = nodes.new("ShaderNodeValToRGB")
    # Cast shadow stays deepest under the chin. Broad form shading rolls across the cheeks.
    ramp.color_ramp.interpolation = "EASE"
    ramp.color_ramp.elements[0].color = (.62, .52, .53, 1.)
    ramp.color_ramp.elements[1].position = .72
    ramp.color_ramp.elements[1].color = (1., .985, .965, 1.)
    for level, tint in ((.22, (.83, .76, .75, 1.)), (.48, (.94, .90, .88, 1.))):
        ramp.color_ramp.elements.new(level).color = tint
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 1.
    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    for a,b in ((diffuse.outputs[0],rgb.inputs[0]),(rgb.outputs[0],ramp.inputs[0]),
                (color,multiply.inputs[1]),(ramp.outputs[0],multiply.inputs[2]),
                (multiply.outputs[0],emission.inputs[0]),(emission.outputs[0],output.inputs[0])):
        links.new(a,b)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
rig = chara3d.make_armature(chara3d.rest_frames())
mesh = chara3d.build_character(spec,"robe","none").build(rig, surface_materials=True).data
uv_name = uv_for_face(mesh)
painted = bpy.data.images.load(str(folder / "painted-makeup.png"))
painted.alpha_mode = "STRAIGHT"
assert any("_face" in m.name for m in mesh.materials)
for mat in mesh.materials:
    skin_shader(mat, painted, uv_name)

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = 580, 610
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Standard"
key = bpy.data.lights.new("Window above the face", "AREA")
key.energy = 125000.
key.shape, key.size = "DISK", 30.
key.use_shadow = True
light = bpy.data.objects.new(key.name, key)
scene.collection.objects.link(light)
light.location = (52., -25., 170.)
light.rotation_euler = (Vector((0.,0.,104.)) - light.location).to_track_quat("-Z","Y").to_euler()
camera = bpy.data.objects.new("Portrait camera", bpy.data.cameras.new("Portrait camera"))
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.type, camera.data.ortho_scale, camera.data.clip_end = "ORTHO", 38., 1100.
target = Vector((0.,0.,104.3))
camera.location = target + 320.*Vector((1.,-.20,.045)).normalized()
camera.rotation_euler = (target-camera.location).to_track_quat("-Z","Y").to_euler()
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else tools.parent / "_art" / "preview" / "portrait")
output.mkdir(parents=True, exist_ok=True)
head = rig.pose.bones["head"]
rest = head.bone.matrix_local.copy()
scene.frame_end = 25
for frame, degrees in ((1, -32), (13, 0), (25, 32)):
    # Rotate around the vertical in rig space, through the head bone's rest origin.
    pivot = Matrix.Translation(rest.translation)
    head.matrix = pivot @ Matrix.Rotation(radians(degrees), 4, "Z") @ pivot.inverted() @ rest
    head.keyframe_insert(data_path="rotation_quaternion", frame=frame)
for frame, label in ((1, "left"), (13, "front"), (25, "right")):
    scene.frame_set(frame)
    scene.render.filepath = str(output / f"natsuko-neck-light-{label}.png")
    bpy.ops.render.render(write_still=True)
    print(scene.render.filepath, flush=True)
