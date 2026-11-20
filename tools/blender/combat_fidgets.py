"""Author combat waiting gestures for every Traveler on the shared humanoid rig."""
from pathlib import Path
import json
import math
import sys

import bpy
import numpy as np
import chara3d as c
from chara3d_native import save_piece
from chara3d_victory import bank

FRAMES = 40
READY_FRAMES = 96
PROFILES = {
    "trav_natsuko": ("map", "satchel", "scout", "reset_feet", "shoulders"),
    "trav_rensei": ("check_hilt", "straighten_cuff", "chin", "reset_feet", "breath"),
    "trav_gendo": ("book", "glasses", "disbelief", "reset_feet", "shoulders"),
    "trav_shizue": ("brace", "stretch", "straighten_cuff", "reset_feet", "chin"),
    "trav_haruki": ("count", "focus", "breath", "reset_feet", "stretch"),
    "trav_mitsue": ("listen", "check_belt", "straighten_cuff", "reset_feet", "scout"),
    "trav_tamotsu": ("watch", "stretch", "brush_sleeve", "reset_feet", "breath"),
    "trav_sayo": ("hair", "check_belt", "listen", "reset_feet", "shoulders"),
    "human_foe": ("scout", "shoulders", "reset_feet", "brace", "breath"),
}
FAMILIES = ("blade", "bow", "club", "fist", "gun", "iai", "pole", "short")
PROPS = {
    "map": {"prop": "map", "show": [.26, .77], "satchel": True, "stow": [.13, .91]},
    "satchel": {"satchel": True, "stow": [.21, .76]},
    "book": {"prop": "book", "show": [.26, .77], "stow": [.16, .86]},
    "watch": {"prop": "watch", "show": [.26, .76], "stow": [.18, .87]},
    "stretch": {"stow": [.15, .87]},
}
HANDS = {
    "glasses": ({"face": (8., 2., 2.)}, None),
    "straighten_cuff": ({"face": (8., -22., -2.)}, None),
    "brush_sleeve": ({"face": (6., -15., -8.)}, None),
    "check_belt": ((.04, -.87, -.16), None),
    "satchel": ((-.16, -.94, .02), (.23, -.8, -.17)),
    "check_hilt": ((.26, -.83, -.30), None),
    "brace": ((.08, -.65, -.07), None),
    "stretch": ((.05, .93, .23), (.05, .93, .23)),
    "focus": ({"face": (12., -9., 3.)}, None),
    "hair": ({"face": (-1., 10., 8.)}, None),
    "count": ({"face": (21., -6., 6.)}, None),
}


def ease(x, start, end):
    u = min(1., max(0., (x - start) / (end - start)))
    return u*u*(3.-2.*u)


def pulse(x, a, b, c_, d):
    return ease(x, a, b) * (1. - ease(x, c_, d))


def touch(form, family, side, target, amount):
    if amount <= 0.:
        return
    joints, _, up, _, _ = c.solve(form)
    torso = c.rz(-form["lean"]) @ c.ry(form["twist"]) @ c.rx(form["bend"])
    origin = joints["neck"] + up * 11
    prior = joints["grip" + side]
    if isinstance(target, dict):
        goal = origin + torso @ np.asarray(target["face"], float)
    else:
        sign = 1 if side == "N" else -1
        shoulder = joints["sh" + side]
        goal = shoulder + torso @ (np.asarray(target, float) * (1, 1, sign)) * (c.UPPER+c.FORE+c.HAND)
    form["arms"][side] = {"face": tuple(torso.T @ (prior*(1-amount) + goal*amount - origin))}
    weapon = form["weapon"]
    if weapon and weapon["hand"] != side:
        weapon["sep"] = None
    if weapon and weapon["hand"] == side:
        active = np.asarray(weapon["dir"], float)
        lowered = np.array((.5, -.8, -.35))
        weapon["dir"] = tuple(c.unit(active*(1-amount) + lowered*amount))
    if family == "iai" and form["iai"]:
        form["iai"] *= 1. - amount


def counting(frame, phase, amount, side):
    """Open one finger at a time using the actual finger chain and fixed segment lengths."""
    rest = c.rest_frames()
    for i, digit in enumerate(("index", "middle", "ring", "little", "thumb")):
        curl = 41. * amount * (1. - ease(phase, .23 + .085*i, .30 + .085*i))
        parent = "hand" + side
        for n in range(1, 3 if digit == "thumb" else 4):
            name = f"{digit}{side}{n}"
            posed = c.driven_frame(rest[name], rest[parent], frame[parent])
            pivot, axis, bend, width = posed
            a = math.radians(curl)
            frame[name] = (pivot, math.cos(a)*axis + math.sin(a)*bend,
                           -math.sin(a)*axis + math.cos(a)*bend, width)
            parent = name


def pose(family, gesture, frame):
    t = frame / FRAMES
    form = c.poses.controls("ready", 0, 1, family)
    f = pulse(t, .03, .26, .66, .99)
    lean, twist, roll, head = {
        "scout": (1, 15, -3, -4), "chin": (-2, -8, 3, 13),
        "listen": (2, -14, 6, -4), "disbelief": (-5, 16, -5, 5),
        "breath": (-3, 2, 1, -3), "shoulders": (-4, -7, 5, -4),
        "stretch": (-9, 2, -3, -8), "brace": (8, 2, -3, -5),
        "focus": (1, 3, 1, 7), "count": (2, 4, 3, 12),
        "map": (8, 5, 2, 17), "book": (6, -3, -3, 16),
        "satchel": (11, -12, 5, 15), "watch": (2, -4, -4, 18),
        "hair": (-3, 5, -5, -6), "glasses": (2, -3, 1, 8),
    }.get(gesture, (2, 2, -3, 6))
    sway = math.sin(t * math.tau)
    follow = pulse(t, .11, .36, .69, 1.0)
    form["lean"] += f*lean + 2.4*f*sway
    form["twist"] += f*twist
    form["bend"] += f*roll
    form["head"] += follow*head - .2*f*lean
    form["head_yaw"] = follow*(6 if gesture in ("scout", "listen", "disbelief") else -3)
    form["head_bank"] = -.65*f*roll
    form["root"][1] -= f*(.055 if gesture == "brace" else .021)
    form["root"][2] += .065*f*(1. if roll >= 0 else -1.)
    form["collar"] = {"N": (1.1*f, 2.4*follow, .3*f), "F": (-1.2*f, 1.0*f, -.3*f)}
    if gesture == "reset_feet":
        foot = pulse(t, .12, .34, .61, .93)
        lift = pulse(t, .12, .2, .23, .33) + pulse(t, .65, .73, .77, .92)
        x, y, z, yaw, pitch = form["feet"]["N"]
        form["feet"] = dict(form["feet"], N=(x-.07*foot, y+.035*lift, z+.055*foot,
                                               yaw+8.*foot, pitch+7.*lift))
        form["root"][0] += .045*f*sway
    if gesture in HANDS:
        for side, goal in zip("NF", HANDS[gesture]):
            if goal is not None:
                # Do not drag a held long weapon through the actor to adjust a cuff.
                if gesture in ("glasses", "count", "hair", "focus") and form["weapon"] and form["weapon"]["hand"] == "N":
                    side = "F"
                    goal = {"face": (*goal["face"][:2], -goal["face"][2])}
                touch(form, family, side, goal, follow)
    if gesture in ("map", "book", "watch"):
        reach = pulse(t, .08, .22, .82, .96)
        read = pulse(t, .23, .39, .66, .79)
        target = {"map": (13., -18., 4.), "book": (16., -17., 4.), "watch": (15., -20., 6.)}[gesture]
        pocket = {"map": (0., -43., 9.), "book": (-5., -40., 11.), "watch": (1., -38., 8.)}[gesture]
        touch(form, family, "N", {"face": c.poses.lerp(pocket, target, read)}, reach)
        if gesture == "book":
            touch(form, family, "F", {"face": (9., 2., -1.)}, pulse(t, .42, .52, .57, .69))
            form["head"] -= 15.*pulse(t, .64, .72, .77, .90)
        elif gesture == "map":
            touch(form, family, "F", {"face": (16., -21., -7.)}, read)
    result = c.pose_frames(form)
    if gesture == "count":
        side = "F" if form["weapon"] and form["weapon"]["hand"] == "N" else "N"
        counting(result, t, f, side)
    return result


def ready(family, i):
    """A full breath and transfer of weight, with both feet fixed by the leg solver."""
    theta = math.tau * (i % READY_FRAMES) / READY_FRAMES
    sway = math.sin(theta)
    counter = math.sin(theta - .53) + math.sin(.53)
    rock = (1. - math.cos(theta)) * .5
    breath = math.sin(theta * 2.) * .5
    form = c.poses.controls("ready", 0, 1, family)
    form["root"][0] += .040*rock
    form["root"][1] -= .047*rock + .012*breath
    form["root"][2] += .060*sway
    form["lean"] += 4.2*rock - 2.1*breath
    form["twist"] += 4.4*sway
    form["bend"] -= 4.8*counter
    form["head"] -= 2.5*rock - 1.2*breath
    form["head_yaw"] = -3.9*counter
    form["head_bank"] = 3.3*sway
    form["collar"] = {"N": (1.25*rock, 1.65*breath + .85*sway, .2*sway),
                      "F": (-1.1*rock, 1.4*breath - .7*sway, -.2*sway)}
    return c.pose_frames(form)


def prop_models(scene, rig, out):
    paper, edge, leather = (229, 211, 162), (149, 115, 68), (91, 62, 42)
    for name in ("book", "map", "watch", "satchel"):
        skin = c.Skin()
        grip = c.P("grip", 1)
        hand = {"handN": 1.}
        if name == "book":
            for sign in (-1, 1):
                at = grip + (2., -1., 3.1*sign + 3.4)
                skin.add(c.box(at, (3.35, .56, 3.2)), (37, 43, 31), hand)
                skin.add(c.box(at + (0, .62, 0), (3.15, .52, 2.96)), paper, hand)
                for i in range(3):
                    skin.add(c.box(at + (-1.5 + 1.4*i, 1.16, 0), (.13, .035, 2.28)), edge, hand)
        elif name == "map":
            at = grip + (2.4, -.7, 4.2)
            skin.add(c.box(at, (4.5, .17, 7.5)), paper, hand)
            for x, z, size in ((-2, -2, 3.6), (0, 1, 4.7), (2, 3, 2.8)):
                skin.add(c.box(at + (x, .19, z), (.17, .035, size)), edge, hand)
        elif name == "watch":
            at = grip + (2., -.35, 2.2)
            skin.add(c.ellipsoid(at, (2.3, .62, 2.3), 20, 6), (182, 128, 58), hand)
            skin.add(c.ellipsoid(at + (0, .49, 0), (1.78, .24, 1.78), 18, 5), paper, hand)
            skin.add(c.box(at + (.28, .73, .32), (.15, .035, .87)), (44, 37, 30), hand)
            skin.add(c.box(at + (.49, .73, -.13), (.73, .035, .12)), (44, 37, 30), hand)
            for i in range(5):
                skin.add(c.ellipsoid(at + (-1.6-.45*i, -.55*i, -1.4), (.37, .27, .38), 7, 3), edge, hand)
        else:
            at, bind = np.array((-4., 59., 14.)), {"pelvis": 1.}
            skin.add(c.ellipsoid(at, (4.9, 7., 3.9), 12, 6), leather, bind)
            skin.add(c.box(at + (0, 3, 2.5), (4.4, 2.5, .63)), edge, bind)
            skin.add(c.box(at + (0, .9, 3.55), (.82, .73, .44)), (171, 135, 67), bind)
        save_piece(scene, out, rig, name, skin)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    rig = c.make_armature(c.rest_frames())
    gestures = tuple(dict.fromkeys(g for group in PROFILES.values() for g in group))
    for family in FAMILIES:
        def frames():
            for gesture in gestures:
                yield None
                for i in range(FRAMES + 1):
                    yield pose(family, gesture, i)
            yield None
            for i in range(READY_FRAMES + 1):
                yield ready(family, i)
        bank(rig, frames(), out / f"{family}.mot")
    prop_models(scene, rig, out)
    index = {
        "profiles": PROFILES,
        "ready": {"st": len(gestures)*(FRAMES+1), "en": len(gestures)*(FRAMES+1)+READY_FRAMES, "spd": 24},
        "clips": {g: dict(st=i*(FRAMES+1), en=i*(FRAMES+1)+FRAMES,
                          spd=12 if g == "book" else 17 if g in PROPS else 22,
                          **PROPS.get(g, {})) for i, g in enumerate(gestures)},
    }
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[sys.argv.index("--") + 1]).resolve())

