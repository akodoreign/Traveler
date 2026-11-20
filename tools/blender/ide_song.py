"""Export Ide's virtuosic vocal performance in bow and free-hand variants."""
from pathlib import Path
import math
import sys

import bpy
import numpy as np

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source") + 1]).resolve()
sys.path.insert(0, str(TOOLS / "blender"))

import chara3d as c
from chara3d_victory import bank
from heart_listens import ease


FRAMES = 51


def pulse(t, a, b, c_, d):
    return ease(t, a, b) * (1.0 - ease(t, c_, d))


def frames(has_bow):
    family = "bow" if has_bow else "fist"
    for i in range(FRAMES + 1):
        t = i / FRAMES
        form = c.poses.controls("ready", 0, 1, family)
        breath = pulse(t, .035, .20, .31, .47)
        phrase = pulse(t, .22, .43, .57, .74)
        flourish = pulse(t, .57, .73, .77, .97)
        stow = pulse(t, .025, .21, .78, .997)
        meter = math.sin(math.tau * (t-.26) * 3)
        form["root"][0] += .036 * phrase - .055 * flourish
        form["root"][1] += .070 * breath + .014 * phrase
        form["root"][2] += .075 * phrase - .055 * flourish
        form["lean"] += -13.0 * breath - 7.0 * phrase + 15.0 * flourish
        form["twist"] += 15.0 * breath - 17.0 * phrase + 17.0 * flourish
        form["bend"] += -6.0 * phrase + 5.0 * flourish
        form["head"] += -12.0 * breath - 9.0 * phrase + 17.0 * flourish
        form["head_yaw"] = 14.0 * phrase + 4 * meter * phrase
        form["collar"] = {"F": (4 * phrase, 3.1 * phrase, -1),
                          "N": (2 * flourish, 2.7 * breath, 1.5 * phrase)}
        form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.53, -.24 + .045 * meter, -.49),
                                        max(breath, phrase))
        form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.29, -.55, .16), flourish)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.35, .38, .55), breath)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.38, .53 + .07 * meter, .58), phrase)
        form["arms"]["F"] = c.poses.lerp(form["arms"]["F"], (.52, .34, .76), flourish)
        foot = c.poses.COMBAT["F"]
        form["feet"] = dict(form["feet"], F=(foot[0] + .065 * phrase, foot[1],
                                            foot[2], foot[3] + 8.0 * phrase, foot[4]))
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
