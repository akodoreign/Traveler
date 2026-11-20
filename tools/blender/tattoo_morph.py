"""Build the humanoid fold and release for Yosai's tattoo dragon transition."""
from pathlib import Path
import math
import sys

import bpy

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source") + 1]).resolve()
sys.path.insert(0, str(TOOLS / "blender"))

import chara3d as c
from chara3d_victory import bank


FRAMES = 30


def ease(t, start, end):
    u = min(1.0, max(0.0, (t - start) / (end - start)))
    return u*u*(3.0-2.0*u)


def fold_frame(t):
    form = c.poses.controls("ready", 0, 1, "fist")
    gather = ease(t, .05, .51)
    coil = ease(t, .23, .96)
    breath = math.sin(math.pi * gather)
    form["root"][0] -= .07 * coil
    form["root"][1] += .04 * breath - .18 * coil
    form["root"][2] += .04 * coil
    form["lean"] += -8.0 * breath + 27.0 * coil
    form["twist"] += 22.0 * gather + 13.0 * coil
    form["bend"] -= 15.0 * coil
    form["head"] += 24.0 * coil - 7.0 * breath
    form["head_yaw"] = -10.0 * gather
    form["collar"] = {"N": (5.0*coil, 3.0*gather, -2.0*coil),
                      "F": (4.0*coil, 3.7*gather, 2.0*coil)}
    form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.40, -.63, -.32), gather)
    form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.45, -.52, -.46), gather)
    form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.24, -.56, -.59), coil)
    form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.33, -.49, -.55), coil)
    return c.pose_frames(form)


def poses():
    for arm in (False, True):
        for i in range(FRAMES+1):
            t = i / FRAMES
            yield fold_frame(1.0 - t if arm else t)
        yield None


if __name__ == "__main__":
    output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = c.make_armature(c.rest_frames())
    bank(rig, poses(), output)
