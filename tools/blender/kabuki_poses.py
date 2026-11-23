"""Kabuki for the rehearsal mini-game (user 2026-11-22: "a minigame modeled on the hiruma dance minigame but with
kabuki"; plugin RokuganKabuki.sk, Crane Ch4 S03 - Kakita Rensei on the old stage in Kyuden Doji's north garden). The
shared rig, so any native human can play it: a low, wide aragoto stance (the sword stays sheathed at the hip), the idle
breath, the four moves the arrows call for - the sleeve-sweep turn, the roppo stamp, the mie (the frozen glare) and the
hand to the hilt - a falter for a miss, the grand mie at the end, and the bow. Clips start and end on the stance.
Run: blender -b --factory-startup --python tools/blender/kabuki_poses.py -- <out_dir>
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


def ease(t, a, b):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3.0 - 2.0 * x)


def pulse(t, a, b, d, e):
    return ease(t, a, b) * (1.0 - ease(t, d, e))


def mix(a, b, w):
    return tuple(x * (1 - w) + y * w for x, y in zip(a, b))


FIST_HIP = (.18, -.62, .22)                     # a fist on the hip, elbow out
SLEEVE = (.38, -.45, .36)                       # the forearm held across, the sleeve hanging
FEET = {"N": (-.02, 0., .17, 30, 0), "F": (.02, 0., -.17, -30, 0)}


def stance():
    f = c.poses.controls("idle8", 0, 1, "fist")
    f["weapon"] = None                                              # sheathed at the hip (the saya shows)
    f["feet"] = dict(FEET)
    f["poles"] = {"N": (1, .1, .35), "F": (1, .1, -.35)}
    f["root"] = [0., -.08, 0.]
    f["lean"], f["head"], f["twist"] = 4., -3., 0.
    f["arms"] = {"N": SLEEVE, "F": FIST_HIP}
    return f


def idle(t):
    f = stance()
    breath = math.sin(2 * math.pi * t)
    f["root"][1] += .012 * breath
    f["head"] += 1.5 * breath
    f["collar"] = {"N": (0., .5 * breath, 0.), "F": (0., .5 * breath, 0.)}
    return f


def turn(t):
    """Left: the sleeve swept out and round, the body turning after it, the head snapping last."""
    f = stance()
    w = pulse(t, 0, .35, .65, 1)
    f["arms"]["N"] = mix(SLEEVE, (.15, .25, .95), w)
    f["twist"] = 22. * w
    f["head_yaw"] = 30. * ease(t, .15, .4) * (1 - ease(t, .65, 1))
    f["lean"] += -5. * w
    return f


def stamp(t):
    """Down: the roppo stamp - the far foot lifted high, then driven into the boards; arms flung wide."""
    f = stance()
    lift = pulse(t, 0, .3, .35, .55)
    land = pulse(t, .5, .58, .7, 1)
    x, y, z, yaw, pitch = FEET["F"]
    f["feet"] = dict(f["feet"], F=(x + .08 * lift, y + .22 * lift, z - .05 * lift, yaw, 20 * lift))
    f["root"][1] -= .06 * land + .02 * lift
    w = pulse(t, 0, .3, .7, 1)
    f["arms"]["N"] = mix(SLEEVE, (.1, .05, .99), w)
    f["arms"]["F"] = mix(FIST_HIP, (.1, .05, .99), w)
    f["lean"] += 10. * land
    return f


def mie(t):
    """Up: the mie - one arm thrust out, the fist on the hip, the head snapped round and down into the glare, held."""
    f = stance()
    w = pulse(t, 0, .25, .8, 1)
    hold = ease(t, .25, .3) * (1 - ease(t, .8, .85))
    f["arms"]["N"] = mix(SLEEVE, (.55, .25, .75), w)
    f["arms"]["F"] = FIST_HIP
    f["head_yaw"] = 28. * w
    f["head"] += 10. * w
    f["head_bank"] = 6. * hold * math.sin(t * 2 * math.pi * 6)      # the tremor of the held glare
    f["lean"] += -6. * w
    f["root"][1] -= .03 * w
    return f


def draw(t):
    """Right: the far hand crosses to the hilt at the near hip, the body coiling forward over it."""
    f = stance()
    w = pulse(t, 0, .35, .7, 1)
    f["arms"]["F"] = mix(FIST_HIP, (.42, -.62, -.62), w)
    f["arms"]["N"] = mix(SLEEVE, (.62, -.1, .3), w)
    f["lean"] += 12. * w
    f["twist"] = -16. * w
    f["head"] += 6. * w
    return f


def falter(t):
    f = stance()
    w = pulse(t, 0, .2, .6, 1)
    wob = math.sin(t * 2 * math.pi * 2) * w
    f["lean"] += 12. * w + 5. * wob
    f["twist"] = 10. * wob
    f["arms"]["N"] = mix(SLEEVE, (.2, .4, .9), w)
    f["head"] += 12. * w
    return f


def grand_mie(t):
    """The end: the grand mie - both arms out, one high, the stance at its widest, the glare held."""
    f = stance()
    w = pulse(t, 0, .2, .85, 1)
    f["arms"]["N"] = mix(SLEEVE, (.2, .85, .5), w)
    f["arms"]["F"] = mix(FIST_HIP, (.35, -.05, .94), w)
    f["head_yaw"] = 24. * w
    f["head"] += 8. * w
    f["root"][1] -= .05 * w
    f["lean"] += -8. * w
    f["head_bank"] = 5. * w * math.sin(t * 2 * math.pi * 7)
    return f


def bow(t):
    f = stance()
    w = pulse(t, .05, .35, .7, .97)
    f["lean"] += 30. * w
    f["head"] += 10. * w
    f["arms"]["N"] = mix(SLEEVE, (.42, -.86, .1), w)
    f["arms"]["F"] = mix(FIST_HIP, (.42, -.86, .1), w)
    return f


CLIPS = (("idle", 40, True, idle), ("turn", 14, False, turn), ("stamp", 16, False, stamp),
         ("mie", 20, False, mie), ("draw", 14, False, draw), ("falter", 18, False, falter),
         ("grand_mie", 40, False, grand_mie), ("bow", 40, False, bow))


def frames(table):
    at = 0
    for name, count, loop, fn in CLIPS:
        n = count if loop else count + 1
        table.append((name, at, n, loop))
        yield None
        for i in range(n):
            yield c.pose_frames(fn(i / count))
        at += n


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    table = []
    bank(c.make_armature(c.rest_frames()), frames(table), out / "kabuki.mot")
    print("wrote", out / "kabuki.mot")
    for name, at, n, loop in table:
        print("CLIP %s %d %d %s" % (name, at, n, "loop" if loop else "once"))
