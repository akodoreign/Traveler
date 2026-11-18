"""Fit-check a chibi .vox skin on the stock leg2 skeleton in Blender.

    blender -b _tools/rpgcobo-tool/work/mot/leg2_woman/woman_2.blend --factory-startup \
        --python tools/blender/vox_fit_render.py -- <skin.vox> <out_dir> [frame ...]

Every template part mesh (head0_a.001, arm_L1_a.001, ...) is replaced by the
matching voxel part of <skin.vox>, placed the way the engine places it (blend
units = voxel/16, variants share their "...0" sibling's pivot, missing variants
fall back to "...0"), and skinned by copying the nearest template vertex's
weights.  The motion's visibility drivers pick the variant per frame exactly
like RPG3DVoxChara.updatePartsVisibles.  Renders front, front 3/4 and back 3/4
PNGs per frame into <out_dir>.
"""
import math
import os
import sys

import bpy
import mathutils
from mathutils.kdtree import KDTree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from voxfile import VoxFile  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
VOX, OUT = argv[0], argv[1]
FRAMES = [int(f) for f in argv[2:]] or [0, 60, 140, 220, 300, 380, 460, 540]
S = 1.0 / 16
os.makedirs(OUT, exist_ok=True)

vf = VoxFile.load(VOX)
pal = vf.palette
arm = bpy.data.objects["motion"]
FACES = [((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
         ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
         ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
         ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
         ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
         ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)])]


def srgb_to_linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def part_mesh(name, tmpl):
    base = name[:-1] + "0"
    src = name if name in vf.names else base
    m = vf.model(src)
    off = [vf.trans[base][i] - m.size[i] // 2 for i in range(3)]
    occ = m.vox
    # nearest template vertex (rest pose, world) -> weights
    tmesh = tmpl.data
    kd = KDTree(len(tmesh.vertices))
    for v in tmesh.vertices:
        kd.insert(tmpl.matrix_world @ v.co, v.index)
    kd.balance()
    gname = {g.index: g.name for g in tmpl.vertex_groups}
    verts, faces, cols, vweights = [], [], [], []
    sx, sy, sz = occ.shape
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                c = occ[x, y, z]
                if not c:
                    continue
                w = (x + off[0], y + off[1], z + off[2])
                _, vi, _ = kd.find(mathutils.Vector(((w[0] + .5) * S, (w[1] + .5) * S, (w[2] + .5) * S)))
                wt = [(gname[g.group], g.weight) for g in tmesh.vertices[vi].groups if g.weight > 0]
                rgb = tuple(srgb_to_linear(float(pal[c][i])) for i in range(3)) + (1.0,)
                for n, quad in FACES:
                    nx, ny, nz = x + n[0], y + n[1], z + n[2]
                    if 0 <= nx < sx and 0 <= ny < sy and 0 <= nz < sz and occ[nx, ny, nz]:
                        continue
                    i0 = len(verts)
                    for q in quad:
                        verts.append(((w[0] + q[0]) * S, (w[1] + q[1]) * S, (w[2] + q[2]) * S))
                        vweights.append(wt)
                    faces.append((i0, i0 + 1, i0 + 2, i0 + 3))
                    cols.append(rgb)
    me = bpy.data.meshes.new(name + "_vox")
    me.from_pydata(verts, [], faces)
    attr = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    for poly, rgb in zip(me.polygons, cols):
        for li in poly.loop_indices:
            attr.data[li].color = rgb
    ob = bpy.data.objects.new(name + "_vox", me)
    bpy.context.scene.collection.objects.link(ob)
    groups = {}
    for i, wt in enumerate(vweights):
        for g, val in wt:
            if g not in groups:
                groups[g] = ob.vertex_groups.new(name=g)
            groups[g].add([i], val, "REPLACE")
    mod = ob.modifiers.new("arm", "ARMATURE")
    mod.object = arm
    return ob


pairs = []
for ob in list(bpy.data.objects):
    if ob.type != "MESH":
        continue
    if ob.name.endswith("_a.001"):
        new = part_mesh(ob.name[:-6], ob)
        pairs.append((ob, new))
    ob.hide_render = True                       # template meshes, sample weapons

scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
sh = scn.display.shading
sh.light = "STUDIO"
sh.color_type = "VERTEX"
sh.show_cavity = True
sh.cavity_type = "WORLD"
scn.display_settings.display_device = "sRGB"
scn.view_settings.view_transform = "Standard"
scn.view_settings.exposure = 0.6
scn.render.film_transparent = False
sh.background_type = "VIEWPORT"
sh.background_color = (0.06, 0.06, 0.07)
scn.render.resolution_x = 360
scn.render.resolution_y = 480
cam = scn.camera
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.6
target = mathutils.Vector((0, 0.15, 0.9))
VIEWS = {"front": 0, "q": -35, "back": 150}

for f in FRAMES:
    scn.frame_set(f)
    for tmpl, new in pairs:
        new.hide_render = tmpl.hide_viewport
    for vname, yaw in VIEWS.items():
        a = math.radians(yaw)
        d = mathutils.Vector((math.sin(a), -math.cos(a), 0.18)).normalized()
        cam.location = target + d * 6
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        scn.render.filepath = os.path.join(OUT, "f%03d_%s.png" % (f, vname))
        bpy.ops.render.render(write_still=True)
print("FIT_DONE", len(pairs), "parts", FRAMES)
