"""Author Gendo's deduction, notebook alignment, and ink brush."""
import math
from pathlib import Path
import sys

import bpy
import numpy as np

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source")+1]).resolve()
sys.path.insert(0,str(TOOLS/"blender"))

import chara3d as c
from chara3d_native import save_piece
from chara3d_victory import bank


FRAMES = 43


def ease(t,a,b):
    s=min(1.,max(0.,(t-a)/(b-a)))
    return s*s*(3.-2.*s)


def pulse(t,a,b,c_,d):
    return ease(t,a,b)*(1.0-ease(t,c_,d))


def frames():
    rest = c.rest_frames()
    page = c.P("grip",1) + np.array((2.,.57,3.4))
    page_frame = (page,*rest["handN"][1:])
    for i in range(FRAMES+1):
        t=i/FRAMES
        point=pulse(t,.02,.146,.29,.408)
        open_=pulse(t,.258,.435,.78,.943)
        edit=pulse(t,.395,.485,.72,.828)
        look=pulse(t,.706,.831,.875,.983)
        form=c.poses.controls("ready",0,1,"fist")
        form["feet"]=c.poses.COMBAT
        form["twist"] += 9*point - 16*open_ + 13*look
        form["lean"] += 5*point + 6*open_ - 3*look
        form["head"] += 17*open_ - 9*look
        form["head_yaw"] = -10*point + 12*look
        form["arms"]["N"]=c.poses.lerp(form["arms"]["N"],(.47,-.46,-.30),open_)
        form["arms"]["F"]=c.poses.lerp(form["arms"]["F"],(.97,-.02,-.35),point)
        if edit:
            first = c.pose_frames(form)
            notebook = c.driven_frame(page_frame, rest["handN"], first["handN"])
            pen = notebook[0] + notebook[1]*(2.7*math.sin((t-.47)*math.tau*13)) + notebook[2]*2.1
            pen += notebook[3]*(4.8 - 13.*(t-.46))
            joints,_,up,_,_=c.solve(form)
            torso = c.rz(-form["lean"]) @ c.ry(form["twist"]) @ c.rx(form["bend"])
            deliver = pen + c.EX*.2 + c.EY*4.4 - c.EZ*2.2
            grip = c.poses.lerp(joints["gripF"],deliver,edit)
            form["arms"]["F"]={"face":tuple(torso.T @ (grip - joints["neck"] - up*11))}
        yield c.pose_frames(form)


def brush(out, rig):
    skin = c.Skin()
    grip = c.P("grip",-1)
    shaft = c.unit(np.array((.37,-1.,.51)))
    points = [grip + amount*shaft for amount in (-3.8,3.2,5.0,6.1)]
    skin.add(c.tube([(points[0],.41,.41),(points[1],.42,.42)],10),(119,67,44),{"handF":1.})
    skin.add(c.tube([(points[1],.48,.48),(points[2],.39,.39)],10),(208,164,90),{"handF":1.})
    skin.add(c.tube([(points[2],.40,.40),(points[3],.10,.10)],9),(33,28,35),{"handF":1.})
    save_piece(bpy.context.scene,out,rig,"deduce_brush",skin)


if __name__ == "__main__":
    out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig=c.make_armature(c.rest_frames())
    bank(rig,frames(),out/"gendo_deduce.mot")
    brush(out,rig)
