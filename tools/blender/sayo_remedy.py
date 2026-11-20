"""Author Sayo's herb mixing, ceramic mortar and wood pestle."""
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
from chara3d_native import save_piece
from chara3d_victory import bank


FRAMES=42


def ease(t,a,b):
    q=min(1.,max(0.,(t-a)/(b-a)))
    return q*q*(3.-2.*q)


def frames():
    rest=c.rest_frames()
    bowl=c.P("grip",1)+np.array((4.,2.,3.))
    top=(bowl,*rest["handN"][1:])
    for i in range(FRAMES+1):
        t=i/FRAMES
        gather=ease(t,.00,.30)*(1.0-ease(t,.77,.985))
        grind=ease(t,.26,.37)*(1.0-ease(t,.70,.84))
        display=ease(t,.65,.79)*(1.0-ease(t,.83,.995))
        form=c.poses.controls("ready",0,1,"fist")
        form["feet"]=c.poses.COMBAT
        form["head"] += 23*gather-13*display
        form["head_yaw"] = -12*gather+11*display
        form["lean"] += 8*gather-8*display
        form["root"][1] -= .04*gather
        form["twist"] -= 11*gather
        form["arms"]["N"]=c.poses.lerp(form["arms"]["N"],(.55,-.52,-.36),gather)
        form["arms"]["N"]=c.poses.lerp(form["arms"]["N"],(.65,-.24,-.30),display)
        if grind:
            initial=c.pose_frames(form)
            surface=c.driven_frame(top,rest["handN"],initial["handN"])
            phase=(t-.34)*5.3*math.tau
            goal=surface[0]+c.EY*(5.1+1.3*math.cos(phase))
            goal += surface[1]*math.cos(phase)*2.15 + surface[3]*math.sin(phase)*2.15
            joints,_,up,_,_=c.solve(form)
            torso=c.rz(-form["lean"])@c.ry(form["twist"])@c.rx(form["bend"])
            hand=c.poses.lerp(joints["gripF"],goal,grind)
            form["arms"]["F"]={"face":tuple(torso.T @ (hand-joints["neck"]-11*up))}
        yield c.pose_frames(form)


def props(out,rig):
    mortar = c.Skin()
    centre=c.P("grip",1)+np.array((4.,.7,3.))
    def rings(heights):
        return [(centre+c.EY*y,r,r) for y,r in heights]
    h={"handN":1.0}
    mortar.add(c.tube(rings([(-3.2,2.3),(-2.7,3.2),(-.65,5.5),(.90,6.2)]),16,caps=False),(98,63,44),h)
    mortar.add(c.tube(rings([(.90,6.2),(1.8,6.05),(1.45,5.40),(.35,4.9),(-1.7,2.25)]),16),(147,104,65),h)
    mortar.add(c.ellipsoid(centre + c.EY*.25,(3.2,.9,3.15),12,7),(95,134,55),h)
    for offset in (np.array((2.,1.,.8)),np.array((-1.4,.6,-1.2)),np.array((.25,.8,1.8))):
        mortar.add(c.ellipsoid(centre+offset,(1.15,.25,.52),8,5),(132,184,77),h)
    pestle=c.Skin()
    grip=c.P("grip",-1)
    shaft=c.unit(np.array((.30,-1.,.44)))
    h={"handF":1.0}
    pestle.add(c.tube([(grip-5*shaft,.67,.67),(grip+4.3*shaft,.86,.86),(grip+6.1*shaft,.73,.73)],10),(132,86,52),h)
    pestle.add(c.ellipsoid(grip+6.2*shaft,(.78,.94,.77),8,6),(191,155,104),h)
    for name, part in (("sayo_mortar",mortar),("sayo_pestle",pestle)):
        save_piece(bpy.context.scene,out,rig,name,part)


if __name__=="__main__":
    out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig=c.make_armature(c.rest_frames())
    bank(rig,frames(),out/"sayo_remedy.mot")
    props(out,rig)
