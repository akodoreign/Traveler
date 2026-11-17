"""Pose library for the 3-D mannequin: every clip is a set of 3-D controls, never a drawing.

Feet are (forward, lift, sideways, toe yaw, toe pitch) in leg lengths from the spot beneath each hip.
Hands are (forward, up, outward) in arm reaches from their own shoulder, in the torso's frame.
N is the camera-side half of the body and F the far half; the N leg is the rear leg of every stance.
"""
import math

import numpy as np

from rig3d import SAYA_DIR, unit

REST, GUARD = (.06, -.97, .05), (.4, -.15, -.2)
STAND = {"N": (-.10, 0, .04, 45, 0), "F": (.05, 0, 0, 0, 0)}
COMBAT = {"N": (-.30, 0, .12, 70, 0), "F": (.27, 0, -.05, 5, 0)}
KNEEL = {"N": (-.52, .03, .10, 0, 75), "F": (.45, 0, -.05, 0, 0)}
SEIZA = {"N": (0, 0, .02, 0, 80), "F": (0, 0, -.02, 0, 80)}
PLANTED = (.27, -.94, -.05)                    # the lead foot of COMBAT, measured from its hip
POLE = dict(
    hand="N", shift=-14,
    ready=dict(arm=[(-.05, -.55, .05)], dir=[(.94, .30, -.12)], sep=[17]),
    guard=dict(arm=[(.15, -.5, 0)], dir=[(.35, .93, 0)], sep=[18]),
    atk_thrust=dict(
        arm=[(-.05, -.55, .05), (-.3, -.5, .05), (-.25, -.48, .05), (.45, -.35, 0), (.4, -.38, 0), (-.05, -.55, .05)],
        dir=[(.94, .3, -.12), (.97, .2, -.1), (.99, .08, -.08), (1, 0, -.05), (1, 0, -.05), (.94, .3, -.12)],
        sep=[17, 20, 20, 9, 10, 17], lean=[0, -6, -4, 16, 12, 2], x=[0, -.05, -.04, .1, .08, 0]),
    atk_slash=dict(
        arm=[(-.05, -.55, .05), (0, -.2, .1), (.1, -.15, .05), (.25, -.5, 0), (.2, -.55, 0), (-.05, -.55, .05)],
        dir=[(.94, .3, -.12), (-.2, .95, .1), (.5, .85, 0), (.95, -.2, -.15), (.9, -.4, -.1), (.94, .3, -.12)],
        sep=[17], lean=[0, -5, 0, 14, 12, 2], x=[0, -.03, 0, .07, .06, 0]),
    atk_overhead=dict(
        arm=[(-.05, -.55, .05), (.1, .22, .05), (.08, .28, .05), (.35, -.1, 0), (.35, -.3, 0), (-.05, -.55, .05)],
        dir=[(.94, .3, -.12), (-.35, .93, 0), (-.5, .86, 0), (.96, .25, 0), (.98, -.2, 0), (.94, .3, -.12)],
        sep=[17, 9, 6, 14, 17, 17], lean=[0, -8, -10, 15, 16, 3], x=[0, -.03, -.04, .08, .08, 0]),
    atk_draw=dict(
        arm=[(-.05, -.55, .05), (-.1, -.6, .05), (-.1, -.6, .05), (.2, -.2, 0), (.15, 0, 0), (-.05, -.55, .05)],
        dir=[(.94, .3, -.12), (.88, -.47, .1), (.84, -.54, .1), (.8, .6, 0), (.6, .8, 0), (.94, .3, -.12)],
        sep=[17, 12, 12, 17, 17, 17], lean=[0, 8, 10, -2, -6, 0], x=[0, 0, .02, .07, .06, 0]))
BLADE = dict(
    hand="F", shift=0,
    ready=dict(arm=[(.55, -.45, -.25)], dir=[(.8, .6, 0)], sep=[-5.5]),
    atk_slash=dict(
        arm=[(.55, -.45, -.25), (.15, .25, -.1), (.1, .4, -.1), (.6, -.2, -.3), (.5, -.6, -.3), (.55, -.45, -.25)],
        dir=[(.8, .6, 0), (-.3, .95, 0), (-.45, .89, 0), (.95, .3, 0), (.75, -.66, 0), (.8, .6, 0)],
        sep=[-5.5], lean=[0, -4, -6, 12, 14, 2], x=[0, -.02, -.02, .07, .07, 0]),
    atk_thrust=dict(
        arm=[(.55, -.45, -.25), (.3, -.4, -.25),                 (.25, -.38, -.25), (.72, -.2, -.42), (.7, -.2, -.42), (.55, -.45, -.25)],
        dir=[(.8, .6, 0), (.97, .25, 0), (1, .1, 0), (1, .02, 0), (1, .02, 0), (.8, .6, 0)],
                sep=[-5.5], twist=[0, 0, 0, -10, -8, 0], lean=[0, -3, -3, 14, 12, 2], x=[0, -.03, -.03, .1, .09, 0]),
    atk_overhead=dict(
        arm=[(.55, -.45, -.25), (0, .55, -.1), (-.1, .6, -.1), (.75, .1, -.3), (.6, -.45, -.3), (.55, -.45, -.25)],
        dir=[(.8, .6, 0), (-.5, .87, 0), (-.75, .66, 0), (.9, .45, 0), (.85, -.5, 0), (.8, .6, 0)],
        sep=[-5.5], lean=[0, -6, -8, 12, 16, 2], x=[0, -.02, -.03, .07, .08, 0]),
    atk_draw=dict(
        arm=[(.55, -.45, -.25), (.1, -.3, .2), (.3, -.3, .3), (.7, -.3, -.2), (.5, -.35, -.5), (.55, -.45, -.25)],
        dir=[(.8, .6, 0), (-.6, .1, -.8), (.3, 0, -.95), (.98, 0, .2), (.8, -.1, .6), (.8, .6, 0)],
        lean=[0, -2, 2, 10, 10, 2], x=[0, -.02, 0, .06, .06, 0]))
SHORT = dict(
    hand="F", shift=0,
    ready=dict(arm=[(.5, -.3, -.2)], dir=[(.75, .66, 0)], other=[(.4, -.2, -.25)]),
    atk_slash=dict(
        arm=[(.5, -.3, -.2), (.1, .1, -.2), (.05, .15, -.2), (.85, -.1, -.3), (.6, -.4, -.4), (.5, -.3, -.2)],
        dir=[(.75, .66, 0), (-.2, .98, 0), (-.3, .95, 0), (.95, .3, 0), (.8, -.6, 0), (.75, .66, 0)],
        lean=[0, -3, -4, 12, 12, 2], x=[0, -.02, -.02, .08, .07, 0]),
    atk_thrust=dict(
        arm=[(.5, -.3, -.2), (.1, -.4, -.1), (.05, -.4, -.1), (.95, -.15, -.2), (.9, -.15, -.2), (.5, -.3, -.2)],
        dir=[(.75, .66, 0), (.95, .3, 0), (1, .1, 0), (1, .05, 0), (1, .05, 0), (.75, .66, 0)],
        lean=[0, -3, -3, 14, 12, 2], x=[0, -.03, -.03, .11, .1, 0]),
    atk_overhead=dict(
        arm=[(.5, -.3, -.2), (.1, .5, -.1), (.05, .55, -.1), (.7, .1, -.2), (.65, -.3, -.2), (.5, -.3, -.2)],
        dir=[(.75, .66, 0), (.3, .95, 0), (.5, .87, 0), (.7, -.7, 0), (.6, -.8, 0), (.75, .66, 0)],
        lean=[0, -5, -6, 12, 14, 2], x=[0, -.02, -.02, .08, .08, 0]),
    atk_draw=dict(
        arm=[(.5, -.3, -.2), (.2, -.5, .1), (.3, -.5, 0), (.9, -.35, -.3), (.8, -.2, -.4), (.5, -.3, -.2)],
        dir=[(.75, .66, 0), (.9, -.4, 0), (.95, -.3, 0), (.9, .4, 0), (.6, .8, 0), (.75, .66, 0)],
        lean=[0, 6, 8, 12, 6, 2], x=[0, 0, .02, .1, .08, 0]))
FIST = dict(
    hand="F",
    ready=dict(arm=[(.62, .12, -.2)], other=[(.38, .02, -.25)]),
    atk_slash=dict(                            # the lead hand snaps out
        arm=[(.62, .12, -.2), (.5, .1, -.2), (.98, .08, -.3), (.98, .08, -.3), (.7, .1, -.25), (.62, .12, -.2)],
        lean=[0, -2, 8, 10, 4, 0], x=[0, -.01, .05, .06, .03, 0]),
    atk_thrust=dict(                           # reverse punch off the rear hip
        arm=[(.62, .12, -.2), (.4, 0, -.1), (.2, -.35, 0), (.1, -.45, 0), (.3, -.2, -.1), (.62, .12, -.2)],
        other=[(.38, .02, -.25), (.2, -.15, -.1), (.15, -.2, -.1), (1, .05, -.35), (.95, .05, -.35), (.38, .02, -.25)],
        twist=[0, -8, -10, 18, 16, 0], lean=[0, -3, -3, 10, 9, 0], x=[0, -.02, -.02, .08, .07, 0]),
    atk_overhead=dict(                         # knife-hand chop
        arm=[(.62, .12, -.2), (.2, .75, -.1), (.1, .85, -.1), (.85, .25, -.3), (.8, -.15, -.3), (.62, .12, -.2)],
        lean=[0, -4, -6, 10, 14, 2], x=[0, -.02, -.02, .06, .07, 0]),
    atk_draw=dict(                             # front kick with the lead leg
        arm=[(.62, .12, -.2), (.5, .15, -.1), (.45, .1, 0), (.4, 0, .1), (.5, .1, -.1), (.62, .12, -.2)],
        kick=[PLANTED, (.3, -.5, -.02), (.45, -.3, 0), (.93, -.1, 0), (.5, -.4, 0), PLANTED],
        toes=[0, -30, -40, -50, -30, 0], lean=[0, -4, -8, -14, -8, 0], x=[0, -.02, -.03, -.03, -.02, 0]))
TABLES = {"pole": POLE, "blade": BLADE, "iai": BLADE, "short": SHORT, "fist": FIST}
SPECIAL = {"pole": ("atk_thrust", "atk_overhead"), "blade": ("atk_slash", "atk_overhead"),
           "iai": ("atk_draw", "atk_draw"), "short": ("atk_thrust", "atk_slash"),
           "bow": ("atk_slash", "atk_overhead"), "fist": ("atk_thrust", "atk_draw")}
VIEWS = {"fidle": ("idle8", "front"), "fwalk8": ("walk8", "front"), "bidle": ("idle8", "back"),
         "bwalk8": ("walk8", "back"), "ftalk": ("talk", "front"), "fnod": ("nod", "front"),
         "frei": ("rei", "front"), "bnod": ("nod", "back"), "brei": ("rei", "back")}


def key(t, seq):
    """Interpolate evenly spaced keys; one key is a constant."""
    values = np.asarray(seq, float)
    x = np.linspace(0, 1, len(values))
    if values.ndim == 1:
        return float(np.interp(t, x, values))
    return np.array([np.interp(t, x, values[:, i]) for i in range(values.shape[1])])


def lerp(a, b, w):
    return tuple(np.asarray(a, float) * (1 - w) + np.asarray(b, float) * w)
def iai(c, t, attacking):
    """Hand on the sheathed hilt; the draw-cut starts at the hip and slashes outward over a dropped knee."""
    sheath = unit(SAYA_DIR)
    c["arms"].update(F="hilt", N="saya")
    c["lean"] = 6
    if not attacking:
        return
    low = key(t, [0, .7, 1, 1, .8, 0])
    c["feet"] = {side: lerp(COMBAT[side], KNEEL[side], low) for side in "NF"}
    c["poles"] = {"N": lerp((.34, .1, .94), (.35, -1, .1), low), "F": lerp((1, .1, .09), (.4, 1, 0), low)}
    c["root"] = [key(t, [0, .02, .08, .1, .08, 0]), -.03 - .55 * low, 0]
    c["lean"] = key(t, [6, 10, 12, 14, 12, 6])
    c["saya_pull"] = key(t, [0, 4, 6, 6, 4, 0])
    c["iai"] = key(t, [0, .45, 1, 1, 1, 0])
    if c["iai"] >= .999:                        # clear of the scabbard: one horizontal cut, near side to far
        c["arms"]["F"] = key(t, [(.5, -.4, -.6)] * 3 + [(.95, -.12, .1), (.93, -.14, .14), (.5, -.4, -.6)])
        c["weapon"] = dict(hand="F", shift=0, dir=key(
            t, [sheath, sheath, (-.25, .05, .95), (.95, .04, -.3), (.9, 0, -.42), sheath]))


def shoot(c, kind, t):
    attacking = kind.startswith("atk_")
    drawn = attacking and .3 < t < .7
    c["arms"]["N"] = key(t, [(.6, -.3, .05), (.8, -.1, .02), (.92, -.02, 0), (.92, -.02, 0), (.9, -.05, 0),
                             (.6, -.3, .05)]) if attacking else (.6, -.3, .05)
    c["arms"]["F"] = "string" if drawn else key(
        t, [(.45, -.25, -.3), (.6, -.1, -.3), (.6, -.1, -.3), (.6, -.1, -.3), (-.25, -.02, .1),
            (.45, -.25, -.3)]) if attacking else (.45, -.25, -.3)
    aim = (-.3, .95, 0) if kind == "atk_overhead" and .1 < t < .9 else (.12, .99, 0)
    c["weapon"] = dict(hand="N", shift=0, dir=aim, part="weapon_draw" if drawn else "weapon")


def controls(kind, frame, count, family):
    t, loop = frame / max(1, count - 1), frame / count
    swing = math.sin(2 * math.pi * loop)
    c = dict(root=[0., 0., 0.], lean=0., twist=0., bend=0., head=0., tip=0., feet=STAND, poles={}, kick={},
             elbows={}, arms={"N": REST, "F": REST}, weapon=None, carry=True, iai=0., saya_pull=0.)
    arms = c["arms"]
    free = "F" if family in ("pole", "bow") else "N"       # the hand that is not carrying anything
    if kind == "idle8":
        c["root"][1], c["lean"] = -.008 * (.5 + .5 * swing), .6 * swing
    elif kind in ("walk8", "run"):
        stride, lift = (.36, .16) if kind == "run" else (.22, .07)
        angle = 2 * math.pi * loop
        for side, sign in (("N", 1), ("F", -1)):
            up = max(0., sign * math.cos(angle))
            c["feet"] = c["feet"] | {side: (sign * stride * math.sin(angle), lift * up, .02 * sign,
                                            8 if side == "N" else 0, 25 * up)}
            arms[side] = (REST[0] - sign * stride * 1.6 * math.sin(angle), REST[1] + .06, REST[2])
        c["lean"] = 9 if kind == "run" else 2
    elif kind in ("ready", "guard", "hurt", "evade") or kind.startswith("atk_"):
        c["feet"], c["root"][1] = COMBAT, -.03
        swordless = family == "iai" and kind in ("atk_thrust", "atk_overhead") and frame in (0, count - 1)
        if family == "iai" and (kind in ("ready", "guard", "hurt", "evade", "atk_slash", "atk_draw") or swordless):
            iai(c, t, kind in ("atk_slash", "atk_draw"))
        elif family == "bow":
            shoot(c, kind, t)
        else:
            table = TABLES[family]
            a = table.get(kind, table["ready"])
            hand = table["hand"]
            other = "N" if hand == "F" else "F"
            arms[hand] = key(t, a["arm"])
            arms[other] = key(t, a.get("other", table["ready"].get("other", [GUARD])))
            if "dir" in a:
                c["weapon"] = dict(hand=hand, dir=key(t, a["dir"]), shift=table.get("shift", 0),
                                   sep=key(t, a["sep"]) if "sep" in a else None)
            c["lean"], c["twist"] = key(t, a.get("lean", [0])), key(t, a.get("twist", [0]))
            c["root"][0] = key(t, a.get("x", [0]))
            if "kick" in a and 0 < t < 1:
                c["kick"]["F"] = key(t, a["kick"])
                c["feet"] = c["feet"] | {"F": (*COMBAT["F"][:4], key(t, a["toes"]))}
        if kind == "guard":
            c["lean"] -= 4
            c["root"][1] -= .03
        elif kind == "hurt":
            c["lean"] += key(t, [-6, -16, -8])
            c["root"][0] += key(t, [-.03, -.08, -.04])
            c["head"] = -10
        elif kind == "evade":
            c["root"][0] -= .16
            c["root"][1] -= .06
            c["lean"] -= 8
    elif kind in ("ko", "collapse"):
        c["tip"] = 86 if kind == "ko" else key(t, [15, 40, 68, 86])
        c["carry"], c["head"] = False, -8
        arms["N"], arms["F"] = (-.3, -.85, .35), (-.2, -.9, .3)
    elif kind in ("cast", "chant") or kind.startswith("cast_"):
        arms[free] = (.55, .45 + .05 * swing, -.1)
        c["head"] = -4
    elif kind == "item":
        arms[free] = (.7, -.1, -.1) if frame % 2 == 0 else (.6, -.2, -.1)
    elif kind == "talk":
        arms[free] = key(t, [(.4, -.35, .1), (.5, -.2, .15), (.42, -.3, .1), (.35, -.4, .05)])
        c["head"] = key(t, [0, 3, 0, -3])
    elif kind == "nod":
        c["head"] = key(t, [0, 10, 16, 5])
    elif kind == "rei":
        c["lean"] = key(t * .5 if count == 3 else t, [0, 14, 28, 30, 16, 0])
        c["head"] = c["lean"] * .25
        arms["N"] = arms["F"] = (.12, -.95, .02)
    elif kind in ("seiza", "seiza_rei"):
        c["feet"], c["root"][1] = SEIZA, -.86
        c["saya"] = (-.97, -.2, .1)             # the scabbard lies flatter beside a kneeling thigh
        c["poles"] = {"N": (1, 0, 0), "F": (1, 0, 0)}
        c["lean"] = key(t, [10, 30, 45]) if kind == "seiza_rei" else 4
        arms["N"] = arms["F"] = (.55, -.6, 0) if kind == "seiza_rei" else (.3, -.62, -.05)
        c["carry"] = family not in ("pole", "bow")
    elif kind == "think":
        arms[free], c["head"] = {"face": (5, -9, 0)}, 4
    elif kind == "surprise":
        arms["N"] = arms["F"] = (.3, .15, .5)
        c["lean"], c["head"] = -6, -8
    elif kind == "laugh":
        arms["N"] = arms["F"] = (.1, -.5, .35)
        c["lean"], c["head"] = (-8, -3)[frame % 2], -10
    elif kind == "facepalm":
        arms[free] = (.35, -.1, -.1) if frame == 0 else {"face": (6, -2, 0)}
        c["head"] = key(t, [4, 10, 12, 10])
    elif kind == "scratch":
        arms[free], c["head"] = {"face": (-4 + 2 * (frame % 2), 6, 0)}, 7
    elif kind == "shrug":
        arms["N"] = arms["F"] = (.2, -.4, .7)
        c["head"] = key(t, [-3, -6, -3])
    elif kind == "crossarms":
        arms["N"], arms["F"] = (.42, -.42, -.62), (.38, -.5, -.6)
    elif kind == "point":
        arms[free] = (.97, .05, -.05)
    elif kind == "squat":
        c["root"][1], c["lean"] = key(t, [0, -.2, -.42, -.42, -.2]), 10
    elif kind in ("celebration", "victory2"):
        arms[free] = (.25, .8 + .1 * swing, .25)
        c["root"][1], c["head"] = -.03 * (.5 - .5 * swing), -4
    else:
        raise ValueError(f"No pose for {kind}")
    if c["weapon"] is None and c["carry"]:     # how each weapon is carried out of combat
        if family == "pole":
            arms["N"] = {"plant": (.42, .08)}
            c["weapon"] = dict(hand="N", dir=(.02, 1, 0), shift=0)
        elif family == "bow":
            c["weapon"] = dict(hand="N", dir=(.25, .97, 0), shift=0)
    return c