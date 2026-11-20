"""Export Haruki's combative inhale and rising focus."""
import math
from pathlib import Path
import sys

import bpy

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source") + 1]).resolve()
sys.path.insert(0, str(TOOLS / "blender"))

import chara3d as c
from chara3d_victory import bank


FRAMES = 28


def ease(t, a, b):
    p = min(1., max(0., (t-a)/(b-a)))
    return p*p*(3.0-2.0*p)


def frames():
    for i in range(FRAMES+1):
        t = i/FRAMES
        p = ease(t,.0,.30)*(1.0-ease(t,.67,.996))
        inhale = ease(t,.15,.41)*(1.0-ease(t,.48,.78))
        reach = ease(t,.38,.63)*(1.0-ease(t,.71,.991))
        form = c.poses.controls("cast",0,1,"pole")
        form["feet"] = c.poses.COMBAT
        form["root"][1] += .043*inhale-.040*p
        form["head"] += 11*p - 16*reach
        form["head_yaw"] = -11*p
        form["lean"] += 4*p - 9*inhale
        form["twist"] += -12*p + 9*reach
        form["collar"] = {"F":(0.,2.9*reach,0.)}
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"],(.27,-.27,-.57),p)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"],(.57,.53,-.08),reach)
        form["bend"] -= 5*inhale
        yield c.pose_frames(form)


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--")+1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bank(c.make_armature(c.rest_frames()), frames(), out)
