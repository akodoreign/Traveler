"""Generate Haruki's staff-hand planted, free-hand Void Bolt release."""
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


FRAMES = 24


def ease(t, a, b):
    x = min(1.0, max(0.0, (t-a)/(b-a)))
    return x*x*(3.0-2.0*x)


def shape_fingers(pose, fold):
    rest = c.rest_frames()
    for name, parent, _, _ in c.digit_bones("F", -1.0):
        pos, x, y, z = c.driven_frame(rest[name], rest[parent], pose[parent])
        angle = math.radians(fold * (26.0 if name.startswith(("ring", "little")) else 6.0))
        sn, cos = math.sin(angle), math.cos(angle)
        pose[name] = pos, x, cos*y+sn*z, cos*z-sn*y
    return pose


def frames():
    for i in range(FRAMES+1):
        t = i / FRAMES
        form = c.poses.controls("cast", 0, 1, "pole")
        gather = ease(t, .015, .19) * (1.0 - ease(t, .235, .38))
        push = ease(t, .19, .34) * (1.0 - ease(t, .61, .985))
        focus = ease(t, .03, .22) * (1.0 - ease(t, .54, .975))
        form["feet"] = c.poses.COMBAT
        form["root"][0] += .044 * push
        form["root"][1] -= .043 * gather
        form["lean"] += 8.0 * push - 5.0 * gather
        form["twist"] += -7.0 * gather + 12.0 * push
        form["head"] += 10.0 * gather - 5.0 * push
        form["head_yaw"] = 12.0 * focus - 10.0 * push
        form["collar"] = {"F": (2.0*push, 4.0*gather, -2.0*push)}
        f = c.poses.lerp(form["arms"]["F"], (.31, .18, -.51), gather)
        form["arms"]["F"] = c.poses.lerp(f, (.91, .07, -.04), push)
        yield shape_fingers(c.pose_frames(form), .16 + .84 * gather)


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bank(c.make_armature(c.rest_frames()), frames(), out)
