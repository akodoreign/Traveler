"""Build the native open-armed Heart Listens gesture in bow and free-hand variants."""
from pathlib import Path
import sys

import bpy
import numpy as np

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source") + 1]).resolve()
sys.path.insert(0, str(TOOLS / "blender"))

import chara3d as c
from chara3d_victory import bank


FRAMES = 42


def ease(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3.0 - 2.0 * x)


def frames(has_bow):
    family = "bow" if has_bow else "fist"
    for i in range(FRAMES + 1):
        t = i / FRAMES
        form = c.poses.controls("ready", 0, 1, family)
        opening = ease(t, .12, .36) * (1.0 - ease(t, .67, .96))
        far = ease(t, .15, .385) * (1.0 - ease(t, .68, .97))
        stow = ease(t, .03, .24) * (1.0 - ease(t, .73, .99))
        greeting = ease(t, .04, .22) * (1.0 - ease(t, .24, .38))
        settle = ease(t, .64, .78) * (1.0 - ease(t, .78, .99))

        form["lean"] += 5.0 * greeting - 7.0 * opening + 4.0 * settle
        form["twist"] += 9.0 * greeting - 10.0 * opening
        form["bend"] += 3.0 * opening
        form["head"] += 7.0 * greeting - 8.0 * opening + 5.0 * settle
        form["head_yaw"] = 12.0 * opening
        form["root"][1] += .035 * opening - .025 * greeting
        form["root"][2] -= .027 * opening
        form["collar"] = {"N": (3.0 * opening, 3.3 * opening, 1.8 * opening),
                          "F": (2.0 * far, 3.1 * far, -1.8 * far)}
        near = c.poses.lerp(form["arms"]["N"], (-.28, -.63, -.26), greeting) if has_bow else form["arms"]["N"]
        form["arms"]["N"] = c.poses.lerp(near, (.21, .05, .89), opening)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.40, .20, .78), far)
        pose = c.pose_frames(form)
        if has_bow:
            grip, _, axis, _ = pose["weapon"]
            shoulder_sling = pose["pelvis"][0] + np.array((-13.0, 34.0, -12.0))
            stowed_axis = np.array((-.31, .93, .18))
            origin = grip * (1.0 - stow) + shoulder_sling * stow
            direction = c.unit(axis * (1.0 - stow) + stowed_axis * stow)
            pose["weapon"] = c.frame(origin, origin + direction, c.EY + .01 * c.EX)
        yield pose
    yield None


if __name__ == "__main__":
    output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = c.make_armature(c.rest_frames())
    bank(rig, (frame for bow in (True, False) for frame in frames(bow)), output)
