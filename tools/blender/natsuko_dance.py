"""Hiruma Natsuko's Winter Court dance (user 2026-11-22: "dance minigame, build a stage for it ... a Dance dance type hit
the keys ... make sure to use her model for it ... shes 3d so you can rig animations"). One motion bank for the dance
mini-game (plugin RokuganDance.sk): a kagura-flavoured base stance (the yari put away), an idle sway on the beat, the
four step moves the arrows call for, a stumble for a miss, the finale flourish, the closing bow, and the mortified
slump when the court laughs; and the Champion's seated pose on his throne (court_throne). Every clip starts and ends on the same base pose, so they chain without a pop.
30 fps. The clip table (CLIPS: name -> first frame, frame count, loop) is printed and mirrored in RokuganDance.sk.
Run: blender -b --factory-startup --python tools/blender/natsuko_dance.py -- <out_dir>
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
    """Up over a..b, held, down over d..e."""
    return ease(t, a, b) * (1.0 - ease(t, d, e))


def mix(a, b, w):
    return tuple(x * (1 - w) + y * w for x, y in zip(a, b))


ARM_BASE = (.16, -.82, .30)                  # relaxed, a little forward and out: the miko-mai's open sleeves
FOOT_BASE = {"N": (0., 0., .07, 14, 0), "F": (0., 0., -.07, -14, 0)}


def base():
    form = c.poses.controls("idle8", 0, 1, "fist")
    form["weapon"] = None                    # the yari is put away for the dance (None hides the weapon bone)
    form["feet"] = dict(FOOT_BASE)
    form["poles"] = {"N": (1, .1, .12), "F": (1, .1, -.12)}
    form["arms"] = {"N": ARM_BASE, "F": ARM_BASE}
    form["root"] = [0., -.02, 0.]
    form["lean"], form["head"], form["twist"] = 2., -2., 0.
    return form


def idle(t):
    """Two beats: a soft dip on each beat, the sleeves floating."""
    f = base()
    beat = math.sin(2 * math.pi * 2 * t)
    dip = .5 - .5 * math.cos(2 * math.pi * 2 * t)
    f["root"][1] -= .025 * dip
    f["twist"] = 4. * math.sin(2 * math.pi * t)
    f["head"] += 3. * beat
    f["arms"]["N"] = mix(ARM_BASE, (.22, -.70, .42), .5 + .5 * math.sin(2 * math.pi * t))
    f["arms"]["F"] = mix(ARM_BASE, (.22, -.70, .42), .5 - .5 * math.sin(2 * math.pi * t))
    return f


def step(t, side):
    """A side step toward `side` ("N" or "F"): that foot reaches out, the weight follows, the lead arm sweeps out at
    shoulder height and the other folds across the chest; the head turns to look along the sleeve."""
    f = base()
    sg = 1. if side == "N" else -1.
    other = "F" if side == "N" else "N"
    w = pulse(t, .0, .35, .62, 1.0)
    foot = FOOT_BASE[side]
    f["feet"] = dict(f["feet"], **{side: (foot[0], .05 * pulse(t, 0, .15, .2, .35), foot[2] + sg * .20 * w,
                                          foot[3] + 20 * w, 0)})
    f["root"][2] += sg * .09 * w
    f["root"][1] -= .03 * w
    f["arms"][side] = mix(ARM_BASE, (.25, .05, .97), w)
    f["arms"][other] = mix(ARM_BASE, (.55, -.12, -.45), w)
    f["twist"] = sg * 14. * w
    f["head_yaw"] = sg * 22. * w
    f["lean"] += -4. * w
    return f


def rise(t):
    """Up: onto the toes in a small hop, both sleeves thrown up to the heavens."""
    f = base()
    w = pulse(t, .0, .35, .65, 1.0)
    hop = pulse(t, .12, .32, .38, .6)
    for s in ("N", "F"):
        x, y, z, yaw, pitch = FOOT_BASE[s]
        f["feet"][s] = (x, y + .07 * hop, z, yaw, 18 * w)
    f["root"][1] += .05 * w + .07 * hop
    f["arms"]["N"] = mix(ARM_BASE, (.10, .95, .32), w)
    f["arms"]["F"] = mix(ARM_BASE, (.10, .95, .32), w)
    f["lean"] += -8. * w
    f["head"] += -16. * w
    return f


def sink(t):
    """Down: a deep bend of the knees, sleeves swept low and wide, the head bowed."""
    f = base()
    w = pulse(t, .0, .35, .62, 1.0)
    f["root"][1] -= .17 * w
    f["lean"] += 14. * w
    f["head"] += 12. * w
    f["arms"]["N"] = mix(ARM_BASE, (.45, -.55, .70), w)
    f["arms"]["F"] = mix(ARM_BASE, (.45, -.55, .70), w)
    return f


def stumble(t):
    """A miss: a foot catches, she pitches, arms windmill, and she catches herself."""
    f = base()
    w = pulse(t, .0, .2, .6, 1.0)
    wob = math.sin(t * 2 * math.pi * 2.5) * w
    f["lean"] += 16. * w + 6. * wob
    f["twist"] = 12. * wob
    f["root"][0] += .05 * w
    f["root"][1] -= .05 * w
    f["arms"]["N"] = mix(ARM_BASE, (.1, .55, .8), w)
    f["arms"]["F"] = mix(ARM_BASE, (.6, -.1, .7), w)
    f["head"] += 10. * w
    f["head_yaw"] = -14. * wob
    return f


def finale(t):
    """The last beat: one sleeve high, one wide, chin up, held."""
    f = base()
    w = pulse(t, .0, .3, .8, 1.0)
    f["arms"]["N"] = mix(ARM_BASE, (.05, .97, .2), w)
    f["arms"]["F"] = mix(ARM_BASE, (.2, -.05, .97), w)
    f["lean"] += -10. * w
    f["head"] += -12. * w
    f["twist"] = 10. * w
    f["root"][1] += .02 * w
    return f


def bow(t):
    """The formal bow to the judges: hands slide to the thighs, a deep bend from the hips, held, and up."""
    f = base()
    w = pulse(t, .05, .35, .7, .97)
    f["lean"] += 34. * w
    f["head"] += 10. * w
    f["arms"]["N"] = mix(ARM_BASE, (.42, -.86, .06), w)
    f["arms"]["F"] = mix(ARM_BASE, (.42, -.86, .06), w)
    f["feet"] = {s: mix(FOOT_BASE[s], (0., 0., .03 if s == "N" else -.03, 4 if s == "N" else -4, 0), w)
                 for s in ("N", "F")}
    return f


def shame(t):
    """Laughed at: the shoulders drop, the head goes down, one hand rubs the back of her neck."""
    f = base()
    w = pulse(t, .0, .3, .82, 1.0)
    f["lean"] += 9. * w
    f["head"] += 24. * w
    f["head_yaw"] = -10. * w
    f["root"][1] -= .03 * w
    f["arms"]["N"] = mix(ARM_BASE, (.04, -.97, .12), w)
    rub = math.sin(t * 2 * math.pi * 3) * pulse(t, .3, .4, .7, .8)
    f["arms"]["F"] = mix(ARM_BASE, (-.06 + .03 * rub, .42, .26), w)   # the hand up behind her neck, rubbing
    f["collar"] = {"F": (0., 1.5 * w, 0.), "N": (0., -1. * w, 0.)}
    return f


def throne(t):
    """(user 2026-11-22: "make a throne and have him sit down weapon put away") Hida Kisada on his seat by the stage:
    seated square, hands on his knees, chin up, breathing. Any native human can play it (the rig is shared)."""
    f = base()
    breath = math.sin(2 * math.pi * t)
    f["feet"] = {"N": (.46, 0., .12, 6, 0), "F": (.46, 0., -.12, -6, 0)}
    f["poles"] = {"N": (1, .3, .1), "F": (1, .3, -.1)}
    f["root"] = [0., -.40 + .004 * breath, 0.]
    f["lean"], f["head"], f["twist"] = -3., -4. + 1.5 * breath, 0.
    f["arms"] = {"N": (.62, -.62, .12), "F": (.62, -.62, .12)}
    f["collar"] = {"F": (0., .4 * breath, 0.), "N": (0., .4 * breath, 0.)}
    return f


# name, frame count, loop, pose fn
CLIPS = (("idle", 30, True, idle),
         ("left", 14, False, lambda t: step(t, "N")),
         ("right", 14, False, lambda t: step(t, "F")),
         ("up", 14, False, rise),
         ("down", 14, False, sink),
         ("stumble", 20, False, stumble),
         ("finale", 30, False, finale),
         ("bow", 40, False, bow),
         ("shame", 48, False, shame),
         ("throne", 60, True, throne))


def frames(table):
    at = 0
    for name, count, loop, fn in CLIPS:
        n = count if loop else count + 1             # a loop's last frame wraps to its first
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
    bank(c.make_armature(c.rest_frames()), frames(table), out / "natsuko_dance.mot")
    print("wrote", out / "natsuko_dance.mot")
    for name, at, n, loop in table:
        print("CLIP %s %d %d %s" % (name, at, n, "loop" if loop else "once"))
