"""Hida companion Void critical: a full-body tetsubo swing (school-choreography.md, Hida row:
"Load the rear foot, rotate hips then shoulders, follow through on a full-body tetsubo swing").

The clip is animated in place; RokuganCompanionVoid.sk carries the body to the target and back
(advance .12-.40, contact .48, return .72-.96). 60 frames at 30 fps.
Run: blender -b --factory-startup --python tools/blender/hida_void.py -- <out_dir>
"""
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


def ease(a, b, t):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3.0 - 2.0 * x)


def mix(a, b, w):
    return tuple(x * (1 - w) + y * w for x, y in zip(a, b))


READY_ARM, READY_DIR = (.55, -.45, -.25), (.3, .95, 0)        # club at the shoulder
COCK_ARM, COCK_DIR = (-.15, .55, -.05), (-.75, .62, 0)       # loaded high behind the head
HIT_ARM, HIT_DIR = (.85, -.15, -.32), (.97, -.2, 0)          # contact: arms long, club level
FOLLOW_ARM, FOLLOW_DIR = (.55, -.7, -.4), (.45, -.89, 0)     # follow-through, head of the club low


def frames():
    base = c.poses.COMBAT
    for i in range(FRAMES + 1):
        t = i / FRAMES
        form = c.poses.controls("ready", 0, 1, "club")
        coil = ease(0.0, .14, t) * (1 - ease(.40, .47, t))           # wound up through the advance
        swing = ease(.40, .48, t)                                     # hips, then shoulders, into contact
        follow = ease(.48, .60, t) * (1 - ease(.70, .90, t))
        settle = ease(.70, .90, t)
        advance = ease(.12, .20, t) * (1 - ease(.34, .40, t))         # heavy steps while carried in
        retreat = ease(.72, .78, t) * (1 - ease(.92, .98, t))
        stepping = advance + retreat
        # arm and club: ready -> cocked -> contact -> follow-through -> ready
        arm = mix(READY_ARM, COCK_ARM, coil)
        wdir = mix(READY_DIR, COCK_DIR, coil)
        arm = mix(arm, HIT_ARM, swing)
        wdir = mix(wdir, HIT_DIR, swing)
        arm = mix(arm, FOLLOW_ARM, follow * (1 - settle))
        wdir = mix(wdir, FOLLOW_DIR, follow * (1 - settle))
        arm = mix(arm, READY_ARM, settle)
        wdir = mix(wdir, READY_DIR, settle)
        form["arms"]["F"] = arm
        form["arms"]["N"] = mix((.4, -.3, .05), (.55, -.2, -.1), swing)   # the second hand rides the haft
        form["weapon"] = dict(hand="F", dir=wdir, shift=0, sep=-7.0)
        # hips lead the shoulders: twist winds back, then unwinds hard through contact
        form["twist"] = -28 * coil + 46 * swing * (1 - settle) + 8 * follow
        form["lean"] = -6 * coil + 20 * swing * (1 - settle) + 6 * follow
        form["bend"] = 6 * swing * (1 - settle)
        form["root"][1] = -.03 - .08 * coil - .16 * swing * (1 - settle) + .06 * follow * (1 - settle)
        form["root"][0] = -.04 * coil + .10 * swing * (1 - settle)
        form["head"] = -6 * coil + 8 * swing * (1 - settle)
        form["head_yaw"] = 6 * coil
        # feet: rear foot loaded back on the coil, front foot stamps at contact; a short heavy gait while carried
        rear = mix(base["N"], (-.40, 0, .14, 70, 0), coil)
        front = mix(base["F"], (.36, 0, -.06, 5, 0), swing * (1 - settle))
        if stepping > 0:
            gait = (t * 18.0) % 2.0
            lift = max(0.0, 1.0 - abs(gait - 1.0)) * stepping
            front = mix(front, (front[0] + .08, .10, front[2], front[3], 18), lift if gait < 1 else 0)
            rear = mix(rear, (rear[0] + .08, .10, rear[2], rear[3], 18), lift if gait >= 1 else 0)
        form["feet"] = {"N": rear, "F": front}
        form["collar"] = {"F": (3.0 * swing * (1 - settle), 1.2 * coil, 0.), "N": (-1.5 * coil, 0., 0.)}
        yield c.pose_frames(form)


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bank(c.make_armature(c.rest_frames()), frames(), out / "hida_void.mot")
    print("wrote", out / "hida_void.mot")
