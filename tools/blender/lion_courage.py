"""Export Shizue's charging upswing for each compatible native weapon family."""
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


FRAMES = 60
FAMILIES = ("blade", "pole", "club", "short")


def ease(t, a, b):
    x = min(1., max(0., (t-a)/(b-a)))
    return x*x*(3.-2.*x)


def pulse(t, a, b, c_, d):
    return ease(t, a, b) * (1.0-ease(t,c_,d))


def frames(family):
    for i in range(FRAMES+1):
        t = i/FRAMES
        form = c.poses.controls("ready", 0, 1, family)
        hand = form["weapon"]["hand"]
        coil = pulse(t, .02, .19, .42, .52)
        rush = pulse(t, .07, .20, .32, .47)
        upswing = ease(t, .39, .56)
        finish = pulse(t, .41, .57, .70, .83)
        run_back = pulse(t, .72, .79, .91, .99)
        turning = math.sin((t-.14)*math.tau*6.2)
        stride = rush + run_back
        lead = pulse(t, .32,.43,.55,.70)
        form["root"][0] += .075*lead
        form["root"][1] -= .078*coil + .051*rush - .057*finish
        form["root"][2] += .025*stride*turning
        form["lean"] += 22*rush + 8*coil - 17*finish + 14*run_back
        form["twist"] += -27*coil + 34*finish
        form["bend"] -= 12*coil - 8*finish
        form["head"] -= 10*rush + 8*finish
        form["head_yaw"] = -9*coil + 10*finish
        form["collar"] = {"N": (2*coil, 2*finish, 0), "F": (4*finish, 2.8*finish, 0)}
        for side, sign in c.SIDES:
            leg = c.poses.COMBAT[side]
            swing = turning*sign
            lift = max(0., sign*math.cos((t-.14)*math.tau*6.2))
            run = (.28*swing, .108*lift, .045*sign, 8*sign, 18*lift)
            foot = c.poses.lerp(leg, run, stride)
            if side == "F":
                foot = c.poses.lerp(foot,(.48,0,-.07,15,0),lead)
            form["feet"] = dict(form["feet"], **{side: foot})
        ready_dir = form["weapon"]["dir"]
        # The hit uses the forward part of the arc. The motion keeps climbing
        # until the blade or pole is clearly above the shoulder.
        angle = math.radians(-80 + 153*upswing)
        arc = (math.cos(angle), math.sin(angle), -.35 + .66*upswing)
        weapon_active = pulse(t, .05,.26,.61,.82)
        form["weapon"]["dir"] = c.poses.lerp(ready_dir, arc, weapon_active)
        form["arms"][hand] = c.poses.lerp(form["arms"][hand],(.17,-.75,-.15),coil)
        form["arms"][hand] = c.poses.lerp(form["arms"][hand],(.69,.52,-.16),finish)
        writing = pulse(t,.50,.523,.622,.662)
        flutter = math.sin(math.tau*(t-.50)*22)
        knife = (0.58, 0.52 + .38 * flutter, .68 * flutter)
        form["weapon"]["dir"] = c.poses.lerp(form["weapon"]["dir"],knife,.82 * writing)
        form["arms"][hand] = c.poses.lerp(form["arms"][hand],(.76,.32+.17*flutter,-.10),writing)
        form["twist"] += 12 * flutter * writing
        yield c.pose_frames(form)
    yield None


if __name__ == "__main__":
    target = Path(sys.argv[sys.argv.index("--")+1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = c.make_armature(c.rest_frames())
    bank(rig, (pose for family in FAMILIES for pose in frames(family)), target)
