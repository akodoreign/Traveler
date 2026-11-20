"""Build the Mitsue jump-release and an original four-point throwing star."""
import math
from pathlib import Path
import sys

import bpy
import numpy as np

TOOLS=Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS=Path(sys.argv[sys.argv.index("--source")+1]).resolve()
sys.path.insert(0,str(TOOLS/"blender"))

import chara3d as c
from chara3d_native import convertToPM, saveModelData, savePolygonMesh
from chara3d_victory import bank


FRAMES=25


def ease(t,a,b):
    p=min(1.,max(0.,(t-a)/(b-a)))
    return p*p*(3.0-2.0*p)


def pulse(t,a,b,c_,d):
    return ease(t,a,b)*(1.0-ease(t,c_,d))


def frames():
    for i in range(FRAMES+1):
        t=i/FRAMES
        form=c.poses.controls("ready",0,1,"fist")
        coil=pulse(t,.0,.17,.26,.41)
        air=pulse(t,.21,.37,.68,.875)
        throw=pulse(t,.29,.425,.58,.79)
        land=pulse(t,.74,.87,.91,.999)
        form["root"][1] -= .115*coil+.135*land-.081*air
        form["root"][0] += .08*throw
        form["lean"] += 17*coil+17*land+15*air
        form["twist"] += -24*coil+44*throw
        form["bend"] += -16*air+11*land
        form["head"] += 8*land-11*throw
        form["head_yaw"] = -14*throw
        form["feet"]={
            "N":c.poses.lerp(c.poses.COMBAT["N"],(-.21,.21,.07,17,34),air),
            "F":c.poses.lerp(c.poses.COMBAT["F"],(.36,.09,-.08,8,14),air),
        }
        form["arms"]["F"]=c.poses.lerp(form["arms"]["F"],(-.07,.48,.49),coil)
        form["arms"]["F"]=c.poses.lerp(form["arms"]["F"],(.93,.12,-.20),throw)
        form["arms"]["N"]=c.poses.lerp(form["arms"]["N"],(.28,.11,.81),air)
        form["collar"]={"F":(4.0*throw,1.6*throw,0.),"N":(-2.*air,2.*air,0.)}
        yield c.pose_frames(form)


def mesh(out):
    shape=[]
    for i in range(4):
        phi=i*math.pi/2
        sn,cs=math.sin(phi),math.cos(phi)
        for x,y in ((25.,0.),(11.,1.4),(5.5,5.1)):
            shape.append(np.array((x*cs-y*sn,x*sn+y*cs,0.)))
    n=len(shape)
    points=[]
    for z,ratio in ((0.,1.),(-1.8,.67),(1.8,.67)):
        for p in shape:
            points.append((p[0]*ratio,p[1]*ratio,z))
    points.extend(((0,0,-2.2),(0,0,2.2)))
    idx=[]
    colors=[]
    for i in range(n):
        j=(i+1)%n
        idx.extend(((i,j,n+j,n+i),(j,i,n*2+i,n*2+j),
                    (n+i,n+j,n*3),(n*2+j,n*2+i,n*3+1)))
        colors.extend((1,1,0 if i%3 else 2,0 if i%3 else 2))
    data=bpy.data.meshes.new("shuriken")
    data.from_pydata([c.blender(p) for p in points],[],[tuple(reversed(face)) for face in idx])
    data.update()
    uv = data.uv_layers.new(name="UVMap")
    for corner in data.loops:
        x,y,_ = points[corner.vertex_index]
        uv.data[corner.index].uv = (x/52+.5,y/52+.5)
    obj=bpy.data.objects.new("Shosuro throwing star",data)
    bpy.context.scene.collection.objects.link(obj)
    for name,rgb,metal,roughness in (("forged blue steel",(.15,.19,.26),.42,.43),
                                      ("honed facets",(.65,.74,.85),.58,.27),
                                      ("violet steel centre",(.27,.14,.35),.33,.42)):
        m=bpy.data.materials.new(name)
        m.diffuse_color=(*rgb,1)
        m.use_nodes=True
        bsdf=m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value=m.diffuse_color
        bsdf.inputs["Metallic"].default_value=metal
        bsdf.inputs["Roughness"].default_value=roughness
        data.materials.append(m)
    data.polygons.foreach_set("material_index",colors)
    pm=convertToPM(bpy.context.scene,obj,{"export_anime":False,"export_mesh":True})
    pm.aabb=[-26,-26,-4,26,26,4]
    saveModelData(pm,str(out/"shosuro_star.mdl"))
    savePolygonMesh(pm,str(out/"shosuro_star.pm"),"shosuro_star",None,None)


if __name__=="__main__":
    out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bank(c.make_armature(c.rest_frames()),frames(),out/"shosuro_throw.mot")
    mesh(out)
