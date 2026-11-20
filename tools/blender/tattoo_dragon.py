"""Fit and animate the generated Eastern dragon used by Yosai's tattoo summon."""
import argparse
import json
import math
import shutil
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

import chara3d as c
from chara3d_native import clearCaches, convertToPM, saveModelData, saveMotionData, savePolygonMesh

CLIPS = {
    "summon": (0, 35, False),
    "hover": (36, 60, True),
    "breath": (61, 96, False),
    "vanish": (97, 128, False),
}
RATE = 24
KEY = "tattoo_dragon"

# Measured through the source's front orthographic preview. Depth is in
# projected pixel units, halfway between the front and back surfaces.
TORSO = (
    (311, 464, -24), (281, 469, -30), (251, 470, -37), (225, 455, -41),
    (209, 426, -29), (219, 405, -35), (244, 392, -37), (275, 381, -38),
    (309, 376, -30), (346, 376, -31), (371, 355, -42), (378, 325, -41),
    (359, 299, -48), (331, 286, -51), (298, 294, -50), (267, 307, -50),
    (230, 322, -46), (188, 322, -42), (158, 306, -36), (149, 277, -42),
    (173, 258, -35), (211, 246, -41), (240, 228, -50), (242, 201, -50),
    (211, 185, -41),
)
TAIL = ((311, 464, -24), (340, 457, -14), (367, 455, 23), (389, 454, 63), (407, 471, 66))
LIMBS = {
    "fore_far": (20, ((134, 254, -62), (105, 268, -68), (75, 289, -74))),
    "fore_near": (19, ((168, 262, 0), (151, 280, -9), (133, 311, -3))),
    "hind_far": (7, ((284, 386, -24), (307, 408, -13), (333, 431, -11))),
    "hind_near": (5, ((225, 396, -18), (217, 421, -13), (207, 441, -6))),
}
SKULL = ((211, 185, -41), (113, 192, -16))
JAW = ((163, 193, -28), (124, 214, -17))
SOCKET = ((120, 201, -13), (103, 199, -13))
UNIT = 160. / (480*.78)


def joint(point):
    x, y, depth = point
    return np.array((240 - x, 485 - y, -depth - 34.)) * UNIT


def projection(mesh):
    raw = np.array([list(v.co) for v in mesh.data.vertices])
    low, high = raw.min(axis=0), raw.max(axis=0)
    scaled = (raw - (high+low)*.5) * (480*.78/(high-low).max())
    x, y, z = scaled.T
    py = 298-(z+.015*y)/math.sqrt(1+.015**2)
    return np.column_stack((240+x, py, -y))


def make_skeleton():
    guides = {}
    parents = {}
    radius = {}

    def add(name, pivot, tip, parent=None, width=None):
        guides[name] = joint(pivot), joint(tip)
        if parent:
            parents[name] = parent
        if width:
            radius[name] = width * UNIT

    add("root", (240, 485, -34), (240, 465, -34))
    for i, (a, b) in enumerate(zip(TORSO, TORSO[1:])):
        add(f"spine_{i:02}", a, b, f"spine_{i-1:02}" if i else "root", 24)
    for i, (a, b) in enumerate(zip(TAIL, TAIL[1:])):
        add(f"tail_{i:02}", a, b, f"tail_{i-1:02}" if i else "spine_00", 16 if i<2 else 12)
    add("head", *SKULL, f"spine_{len(TORSO)-2:02}", 34)
    add("jaw", *JAW, "head", 13)
    add("mouth", *SOCKET, "head")
    add("mouth_aim", SOCKET[1], (95, 198, -13), "mouth")
    for prefix, (spine, points) in LIMBS.items():
        add(prefix, points[0], points[1], f"spine_{spine:02}", 13)
        add(prefix+"_paw", points[1], points[2], prefix, 13)

    frames = {name: c.frame(a,b,c.EZ) for name, (a,b) in guides.items()}
    armature = c.make_armature(frames)
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (a,b) in guides.items():
        edit = armature.data.edit_bones[name]
        edit.length = float(np.linalg.norm(b-a))
        if name in parents:
            edit.parent = armature.data.edit_bones[parents[name]]
    bpy.ops.object.mode_set(mode="OBJECT")
    armature.name = KEY
    return armature, guides, parents, radius


def bind_skin(mesh, points, pixels, guides, parents, radius):
    names = list(radius)
    indices = {name: i for i,name in enumerate(names)}
    scores = np.empty((len(points), len(names)))
    for i, name in enumerate(names):
        a, b = guides[name]
        line = b - a
        offsets = points - a
        t = np.clip(offsets @ line / (line@line), 0, 1)
        scores[:,i] = np.linalg.norm(offsets - t[:,None]*line, axis=1) / radius[name]
    x,y,depth = pixels.T
    head, jaw = indices["head"], indices["jaw"]
    # Horns and muzzle stay with the skull. Only the lower lip and chin
    # use the jaw hinge, regardless of nearby whisker and neck surfaces.
    above_brow = (x < 236) & (y < 185)
    scores[above_brow,:] = 40.
    scores[above_brow,head] = 0.
    mouth_floor = 201.0 - .10*(x-133)
    lower_lip = (x < 154) & (x > 106) & (y > mouth_floor) & (y < 232) & (abs(depth+19) < 32.)
    scores[~lower_lip,jaw] += 5.
    scores[lower_lip,jaw] *= .67
    strongest = scores.argmin(axis=1)
    groups = [mesh.vertex_groups.new(name=name) for name in names]
    for i, best in enumerate(strongest):
        name = names[best]
        allowed = [best]
        parent = indices.get(parents[name])
        if parent is not None:
            allowed.append(parent)
        allowed.extend(indices[child] for child,owner in parents.items() if owner==name and child in indices)
        ranked = sorted(allowed, key=lambda k: scores[i,k])[:4]
        delta = scores[i, ranked]**2 - scores[i,best]**2
        w = np.exp(-5. * delta)
        active = w > .055
        for k, share in zip(np.array(ranked)[active], w[active]/w[active].sum()):
            groups[k].add([i], float(share), "REPLACE")


def smooth(t, a, b):
    x = min(1.,max(0.,(t-a)/(b-a)))
    return x*x*(3.-2.*x)


def stroke(t, a, b, c_, d):
    return smooth(t,a,b)*(1.-smooth(t,c_,d))


def animate(scene, rig):
    scene.render.fps = RATE
    scene.frame_start, scene.frame_end = 0, 128
    previous={}
    for bone in rig.pose.bones:
        bone.rotation_mode = "QUATERNION"
    for clip, (first,last,_) in CLIPS.items():
        for frame in range(first,last+1):
            t = (frame-first)/(last-first)
            rootlift=roll=spin=jaw=surge=0.
            gust=math.sin(math.tau*t)
            if clip=="summon":
                ready=smooth(t,0.,.92)
                rootlift=-46.*(1.-ready)+4.*math.sin(math.pi*t)
                spin=-42.*(1.-ready)
                roll=9.*math.sin(math.pi*t)
                surge=stroke(t,0.,.46,.57,1.)
            elif clip=="hover":
                rootlift=3.*gust
                roll=1.8*gust
            elif clip=="breath":
                surge=stroke(t,.02,.23,.76,.98)
                rootlift=2.5*surge
                roll=-3.5*surge
                jaw=18.*surge
            else:
                farewell=smooth(t,.05,1.)
                rootlift=-41.*farewell
                spin=35.*farewell
                roll=8.*farewell
                surge=stroke(t,.05,.45,.60,1.)
            for bone in rig.pose.bones:
                name=bone.name
                bone.location=(0.,0.,0.)
                basis=bone.bone.matrix_local.to_quaternion().inverted()
                bend=yaw=twist=0.
                if name=="root":
                    bone.location=basis @ Vector(c.blender((0.,rootlift,0.)))
                    bend, yaw=roll, spin
                elif name.startswith(("spine_","tail_")):
                    i=int(name.rsplit("_",1)[1])
                    w=math.sin(math.tau*t-i*.37)-math.sin(-i*.37)*(1.-smooth(t,0.,.24))
                    # A traveling ripple closes naturally at neutral clip endpoints.
                    envelope=stroke(t,0.,.24,.72,1.)
                    direction=-1 if name.startswith("tail") else 1
                    bend=direction*(1.24*w*envelope+1.25*surge*math.sin(i*.41))
                    yaw=.8*gust*envelope*math.cos(i*.37)
                elif name=="head":
                    bend=-7.*surge if clip=="breath" else -3.*surge
                    yaw=3.5*gust*stroke(t,0.,.18,.72,1.)
                elif name=="jaw":
                    bend=-jaw
                elif name.startswith(("fore_","hind_")):
                    side=1 if "_near" in name else -1
                    bend=side*(5.*surge+3.*gust*stroke(t,0.,.3,.7,1.))*(-.52 if name.endswith("_paw") else 1.)
                    twist=side*2.*surge
                q=Quaternion(basis @ Vector((0,0,1)), math.radians(yaw))
                q=q @ Quaternion(basis @ Vector((0,-1,0)), math.radians(bend))
                q=q @ Quaternion((0,1,0), math.radians(twist))
                if name in previous:
                    q.make_compatible(previous[name])
                previous[name]=q.copy()
                bone.rotation_quaternion=q
                for field in ("location","rotation_quaternion"):
                    bone.keyframe_insert(field, frame=frame, group=name)
    scene.frame_set(0)


def finish_texture(out, mesh, atlas):
    tex=out/"tex"
    tex.mkdir(exist_ok=True,parents=True)
    material,=mesh.data.materials
    material.name="lacquered dragon scales"
    shader=material.node_tree.nodes.get("Principled BSDF")
    base=shader.inputs["Base Color"].links[0].from_node
    final=tex/(KEY+"_color.png")
    shutil.copyfile(atlas, final)
    repaired=bpy.data.images.load(str(final),check_existing=False)
    repaired.pack()
    base.image=repaired
    shader.inputs["Metallic"].default_value=.06
    shader.inputs["Roughness"].default_value=.67
    return repaired, final


def export(source, atlas, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(source))
    mesh,=[o for o in scene.objects if o.type=="MESH"]
    mesh.data.transform(mesh.matrix_world)
    mesh.parent=None
    mesh.matrix_world=Matrix.Identity(4)
    pixels=projection(mesh)
    points=(pixels-(240,485,-34))*(-UNIT)
    mesh.data.vertices.foreach_set("co",(points[:,(0,2,1)]*(1,-1,1)).ravel())
    mesh.data.polygons.foreach_set("use_smooth",[True]*len(mesh.data.polygons))
    mesh.data.update()
    rig, guides, parents, radius=make_skeleton()
    bind_skin(mesh, points, pixels, guides, parents, radius)
    mesh.name="Tattoo dragon"
    mesh.parent=rig
    mesh.modifiers.new("Dragon skin","ARMATURE").object=rig
    repaired, final=finish_texture(out,mesh,atlas)

    animate(scene,rig)
    clearCaches()
    packed=convertToPM(scene,mesh,{"export_mesh":True,"export_anime":True})
    space=points*(1,1,-1)
    padding=(35,55,35)
    packed.aabb=[*(space.min(axis=0)-padding),*(space.max(axis=0)+padding)]
    saveModelData(packed,str(out/(KEY+".mdl")))
    saveMotionData(packed.mot,str(out/(KEY+".mot")))
    savePolygonMesh(packed,str(out/(KEY+".pm")),KEY,KEY,None)
    stamp=final.with_stem(final.stem+"_srgb")
    if stamp.name in (out/(KEY+".pm")).read_text("utf8"):
        final.replace(stamp)
        repaired.filepath=str(stamp)

    action=rig.animation_data.action
    for name,(first,last,_) in CLIPS.items():
        track=rig.animation_data.nla_tracks.new()
        track.name=name
        strip=track.strips.new(name,0,action)
        strip.action_frame_start=first
        strip.action_frame_end=last
        strip.frame_start=0
        strip.frame_end=last-first
    rig.animation_data.action=None
    bpy.ops.export_scene.gltf(filepath=str(out/(KEY+"_rigged.glb")),export_animation_mode="NLA_TRACKS")
    data={
        "scale": .019, "facing": "+X", "mouth": "mouth", "aim": "mouth_aim",
        "breathLeadMs": 330,
        "clips": {name: {"st":st,"en":en,"spd":RATE,"loop":loop} for name,(st,en,loop) in CLIPS.items()},
        "rig": {name:{"base":[round(float(x),3) for x in base],"tip":[round(float(x),3) for x in tip],"parent":parents.get(name)} for name,(base,tip) in guides.items()},
    }
    (out/(KEY+".json")).write_text(json.dumps(data, indent=2)+"\n","utf8")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("atlas", type=Path)
    parser.add_argument("out", type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    export(args.source.resolve(),args.atlas.resolve(),args.out.resolve())

