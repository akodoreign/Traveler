"""Hida Sachiko's Void critical prelude (user 2026-11-21: "have her raise her arms then use the already pre rendered
earth icon and give everyone the damage reduction for 2 turns"): plant, then both arms up with the tetsubo raised
overhead in a war cry, a held shudder, and back to ready. In place; 42 frames at 30 fps.
Run: blender -b --factory-startup --python tools/blender/hida_rally.py -- <out_dir>
"""
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

FRAMES = 42


def ease(a, b, t):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3.0 - 2.0 * x)


def mix(a, b, w):
    return tuple(x * (1 - w) + y * w for x, y in zip(a, b))


def frames():
    base = c.poses.COMBAT
    for i in range(FRAMES + 1):
        t = i / FRAMES
        form = c.poses.controls("ready", 0, 1, "club")
        up = ease(.06, .30, t) * (1 - ease(.80, .98, t))
        shake = math.sin(t * 70.0) * ease(.30, .38, t) * (1 - ease(.72, .80, t))
        # both arms high: the club hand overhead, the free hand thrown up beside it
        form["arms"]["F"] = mix((.55, -.45, -.25), (.12, .92, -.12), up)
        form["arms"]["N"] = mix((.4, -.3, .05), (-.08, .90, .18), up)
        form["weapon"] = dict(hand="F", dir=mix((.3, .95, 0), (.15, .99, 0), up), shift=0)
        form["lean"] = -9 * up + 1.2 * shake
        form["head"] = -14 * up
        form["twist"] = 4 * shake
        form["root"][1] = -.03 - .06 * up
        # a wide, planted stance: the mountain does not move
        form["feet"] = {"N": mix(base["N"], (-.36, 0, .16, 70, 0), up),
                        "F": mix(base["F"], (.33, 0, -.09, 5, 0), up)}
        form["collar"] = {"F": (0., 2.2 * up, 0.), "N": (0., 2.2 * up, 0.)}
        yield c.pose_frames(form)


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bank(c.make_armature(c.rest_frames()), frames(), out / "hida_rally.mot")
    print("wrote", out / "hida_rally.mot")
