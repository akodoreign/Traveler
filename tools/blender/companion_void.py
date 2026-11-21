"""Companion Void critical preludes (user 2026-11-21: "start giving the other companions (not travelers) their own
animation if they have a void crit"; "everyone should be somewhat unique"; "use the current framework").

One in-place clip per companion, authored as timed key poses on the shared pose controls (rig3d_poses.controls) and
smoothly interpolated. RokuganCompanionVoid.sk plays the clip after the school title and lights the school's icon over
the allies. Each clip starts and ends in the family's ready pose so it blends into the attack that follows.

Keys: (time 0..1, {field: value}). Fields: F / N (hand targets in arm reaches from their shoulder), wdir (weapon
direction), lean / twist / bend / head / head_yaw (degrees), x / y (root offsets), stance (feet: "combat", "wide",
"low", "kneel", "tall"), shake (amplitude of a held tremble), collar (F / N lift).
Run: blender -b --factory-startup --python tools/blender/companion_void.py -- <out_dir> [clip ...]
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

P = c.poses
STANCES = {
    "combat": P.COMBAT,
    "wide": {"N": (-.38, 0, .16, 70, 0), "F": (.34, 0, -.09, 5, 0)},
    "low": {"N": (-.40, 0, .14, 70, 30), "F": (.36, 0, -.07, 8, 0)},
    "kneel": P.KNEEL,
    "tall": {"N": (-.12, 0, .06, 40, 0), "F": (.10, 0, -.02, 0, 0)},
}
STANCE_Y = {"combat": -.03, "wide": -.08, "low": -.20, "kneel": -.52, "tall": 0.0}

# clip -> (weapon family, frames, keys)
CLIPS = {
    # Hiruma Ryoichi, kama: drop into a scout's crouch, twirl the kama twice at the hip, rise light on the feet
    "cv_ryoichi": ("short", 40, [
        (0.00, {}),
        (0.18, dict(stance="low", lean=16, head=-6, F=(.35, -.55, -.2), wdir=(.2, -.9, .2))),
        (0.30, dict(F=(.55, -.35, -.35), wdir=(.95, .1, -.3), twist=-12)),
        (0.42, dict(F=(.35, -.55, .05), wdir=(-.6, -.6, .5), twist=8)),
        (0.54, dict(F=(.55, -.35, -.35), wdir=(.95, .1, -.3), twist=-12)),
        (0.66, dict(F=(.35, -.55, .05), wdir=(-.6, -.6, .5), twist=8)),
        (0.80, dict(stance="combat", lean=4, F=(.5, -.3, -.2), wdir=(.75, .66, 0))),
        (1.00, {}),
    ]),
    # Hiruma Goro, katana: head scans left then right (scouting the field), blade flicks up into guard
    "cv_goro": ("blade", 40, [
        (0.00, {}),
        (0.18, dict(head_yaw=-24, head=-4, lean=6, stance="low")),
        (0.40, dict(head_yaw=24, head=-4)),
        (0.58, dict(head_yaw=0, F=(.2, .1, -.3), wdir=(-.2, .98, 0), twist=-10)),
        (0.70, dict(F=(.62, -.1, -.3), wdir=(.95, .3, 0), twist=6, lean=10)),
        (1.00, {}),
    ]),
    # Hiruma Kage, tetsubo: spins the club once overhead one-handed, then drops it onto the shoulder and grins
    "cv_kage": ("club", 44, [
        (0.00, {}),
        (0.16, dict(F=(.2, .8, -.1), wdir=(.95, .2, 0), head=-8)),
        (0.28, dict(F=(.1, .9, -.1), wdir=(0, .2, .98))),
        (0.40, dict(F=(.1, .9, -.1), wdir=(-.95, .2, 0))),
        (0.52, dict(F=(.2, .8, -.1), wdir=(0, .2, -.98))),
        (0.66, dict(F=(.25, .35, -.05), wdir=(-.4, .9, 0), head=-10, lean=-6, stance="wide")),
        (0.84, dict(head=-4, lean=-2)),
        (1.00, {}),
    ]),
    # Akodo Gusai: blade lifted high, then levelled to point the line forward - the general's order
    "cv_gusai": ("blade", 44, [
        (0.00, {}),
        (0.22, dict(F=(.2, .92, -.1), wdir=(.1, .99, 0), head=-10, lean=-4, stance="tall")),
        (0.40, dict(F=(.2, .92, -.1), wdir=(.1, .99, 0), shake=.6)),
        (0.58, dict(F=(.95, .15, -.2), wdir=(.99, .1, 0), lean=12, stance="wide", head=2)),
        (0.80, dict(F=(.95, .15, -.2), wdir=(.99, .1, 0))),
        (1.00, {}),
    ]),
    # Akodo Kafu, bare-handed: fists thrown up, chest out, a roar
    "cv_kafu": ("fist", 40, [
        (0.00, {}),
        (0.16, dict(F=(.3, -.5, -.3), N=(.3, -.5, .3), lean=12, head=6, stance="low")),
        (0.34, dict(F=(.25, .95, -.25), N=(.2, .95, .25), lean=-12, head=-18, stance="wide", collar=2.4)),
        (0.70, dict(F=(.25, .95, -.25), N=(.2, .95, .25), lean=-12, head=-18, shake=1.0)),
        (1.00, {}),
    ]),
    # Akodo Hiruto: the lord, unhurried: blade lowered, the open hand sweeps across the line, a nod
    "cv_hiruto": ("blade", 46, [
        (0.00, {}),
        (0.18, dict(F=(.4, -.75, -.15), wdir=(.6, -.8, 0), stance="tall", head=-3)),
        (0.36, dict(N=(.75, .1, .55), head_yaw=14)),
        (0.62, dict(N=(.75, .1, -.45), head_yaw=-14, twist=-10)),
        (0.78, dict(N=(.4, -.3, .05), head=8, head_yaw=0, twist=0)),
        (1.00, {}),
    ]),
    # Akodo Rin: a crisp blade salute - hilt to the brow, blade upright - then snapped down to ready
    "cv_rin": ("blade", 38, [
        (0.00, {}),
        (0.24, dict(F=(.38, .4, -.05), wdir=(.02, .99, 0), N=(.3, .2, .1), stance="tall", head=-4)),
        (0.56, dict(F=(.38, .4, -.05), wdir=(.02, .99, 0), N=(.3, .2, .1))),
        (0.72, dict(F=(.6, -.55, -.25), wdir=(.55, -.83, 0), lean=6)),
        (1.00, {}),
    ]),
    # The Lion rider (Matsu), yari: the spear raised two-handed over the head and shaken - a war cry
    "cv_lionrider": ("pole", 44, [
        (0.00, {}),
        (0.22, dict(N=(.2, .95, .1), wdir=(.15, .99, 0), head=-14, lean=-8, stance="wide", collar=2.0)),
        (0.70, dict(N=(.2, .95, .1), wdir=(.15, .99, 0), head=-14, lean=-8, shake=1.4)),
        (1.00, {}),
    ]),
    # Matsu Hanae: katana raised over the head in both hands, drops into a deep forward stance, roaring
    "cv_hanae": ("blade", 42, [
        (0.00, {}),
        (0.22, dict(F=(.05, .9, -.1), wdir=(-.6, .8, 0), head=-12, lean=-6)),
        (0.44, dict(F=(.05, .9, -.1), wdir=(-.6, .8, 0), stance="low", lean=14, head=-16, shake=1.1)),
        (0.74, dict(F=(.05, .9, -.1), wdir=(-.6, .8, 0), stance="low", lean=14, head=-16, shake=1.1)),
        (1.00, {}),
    ]),
    # Shiba Ashimita, naginata: the shaft planted upright at her side, the free arm crossed - a cross-guard ward
    "cv_ashimita": ("pole", 46, [
        (0.00, {}),
        (0.24, dict(N=(.35, -.05, .3), wdir=(.02, .99, 0), F=(.55, .15, .25), stance="wide", head=-4)),
        (0.70, dict(N=(.35, -.05, .3), wdir=(.02, .99, 0), F=(.55, .15, .25), shake=.4)),
        (1.00, {}),
    ]),
    # Seppun Ushimo: stands tall, blade upright before the face, a heel-led quarter turn to cover the party
    "cv_ushimo": ("blade", 44, [
        (0.00, {}),
        (0.24, dict(F=(.42, .25, -.1), wdir=(.02, .99, 0), stance="tall", head=-6)),
        (0.48, dict(twist=-28, head_yaw=-12)),
        (0.74, dict(twist=0, head_yaw=0, F=(.42, .25, -.1), wdir=(.02, .99, 0))),
        (1.00, {}),
    ]),
    # Doji Hayato: the blade tip writes the strokes of a character in the air - down, across, a sweep - then a bow
    "cv_hayato": ("blade", 52, [
        (0.00, {}),
        (0.14, dict(F=(.7, .5, -.2), wdir=(.9, .4, 0), stance="tall")),
        (0.28, dict(F=(.7, .05, -.2), wdir=(.9, -.1, 0))),                     # stroke 1: down
        (0.40, dict(F=(.75, .3, .15), wdir=(.85, .2, .45))),
        (0.52, dict(F=(.75, .3, -.45), wdir=(.85, .2, -.5))),                  # stroke 2: across
        (0.66, dict(F=(.7, .55, .05), wdir=(.9, .4, .1))),
        (0.78, dict(F=(.65, -.25, -.45), wdir=(.8, -.5, -.3), twist=-8)),      # stroke 3: the sweep
        (0.90, dict(lean=14, head=10, F=(.55, -.45, -.25), wdir=(.8, -.6, 0))),  # a small bow
        (1.00, {}),
    ]),
    # Yoritomo Rui, kama: a low shoulder-led sweep, turning off the back foot - the rolling wave
    "cv_rui": ("short", 40, [
        (0.00, {}),
        (0.20, dict(stance="low", twist=-30, F=(.2, -.5, .4), wdir=(-.3, -.5, .8), lean=12)),
        (0.44, dict(stance="low", twist=34, F=(.9, -.35, -.45), wdir=(.85, -.2, -.5), lean=16)),
        (0.62, dict(twist=40, F=(.6, -.5, -.6), wdir=(.5, -.4, -.75))),
        (1.00, {}),
    ]),
    # Shinjo Ryuko: a quick draw flourish, then the arm points down the lane - ride on
    "cv_ryuko": ("blade", 40, [
        (0.00, {}),
        (0.16, dict(F=(.2, -.35, .25), wdir=(-.5, .2, .85), twist=-14)),
        (0.34, dict(F=(.85, .05, -.35), wdir=(.95, .15, -.3), twist=16, lean=8)),
        (0.54, dict(N=(.95, .12, .1), head_yaw=-6, F=(.55, -.45, -.25), wdir=(.8, -.6, 0))),
        (0.80, dict(N=(.95, .12, .1))),
        (1.00, {}),
    ]),
    # Isawa Michio, shakujo: the ringed staff lifted high and shaken three times
    "cv_michio": ("pole", 44, [
        (0.00, {}),
        (0.22, dict(N=(.3, .85, .1), wdir=(.05, .99, 0), head=-8, stance="tall")),
        (0.36, dict(N=(.3, .95, .1))),
        (0.46, dict(N=(.3, .8, .1))),
        (0.56, dict(N=(.3, .95, .1))),
        (0.66, dict(N=(.3, .8, .1))),
        (0.76, dict(N=(.3, .95, .1))),
        (1.00, {}),
    ]),
    # Isawa Sanro: counts on the free hand, then both palms draw together and press down - a ward set in earth
    "cv_sanro": ("fist", 46, [
        (0.00, {}),
        (0.18, dict(F=(.6, .25, -.2), head=6)),
        (0.30, dict(F=(.6, .3, -.2), head=8)),
        (0.42, dict(F=(.6, .25, -.2), head=6)),
        (0.60, dict(F=(.55, .1, -.02), N=(.55, .1, .02), head=0, stance="wide")),
        (0.78, dict(F=(.6, -.45, -.05), N=(.6, -.45, .05), lean=12, stance="wide")),
        (1.00, {}),
    ]),
    # Isawa Kasiko: palms open low, then sweep up and outward - the wind lifts
    "cv_kasiko": ("fist", 42, [
        (0.00, {}),
        (0.20, dict(F=(.5, -.6, -.3), N=(.5, -.6, .3), lean=6)),
        (0.52, dict(F=(.35, .9, -.45), N=(.35, .9, .45), lean=-8, head=-14)),
        (0.72, dict(F=(.35, .9, -.45), N=(.35, .9, .45), lean=-8, head=-14, shake=.5)),
        (1.00, {}),
    ]),
    # Tamori Haku: drops to one knee, palm to the ground, then the palm rises with the heat
    "cv_haku": ("fist", 48, [
        (0.00, {}),
        (0.24, dict(stance="kneel", F=(.7, -.85, -.1), lean=24, head=6)),
        (0.44, dict(stance="kneel", F=(.7, -.85, -.1), lean=24)),
        (0.70, dict(stance="kneel", F=(.55, .55, -.1), lean=0, head=-10)),
        (1.00, {}),
    ]),
}
# (Togashi Yosai has no prelude here: user 2026-11-21 "just all the companions, except togashi")


def smooth(x):
    return x * x * (3.0 - 2.0 * x)


def lerp(a, b, w):
    if isinstance(a, (int, float)):
        return a + (b - a) * w
    return tuple(x + (y - x) * w for x, y in zip(a, b))


def resolved(keys, ready):
    """Fill every key with every field: a field a key omits keeps the previous key's value (the first: ready)."""
    out, cur = [], dict(ready)
    for t, k in keys:
        cur = dict(cur)
        if t in (0.0, 1.0) and not k:
            cur = dict(ready)
        cur.update(k)
        if "stance" in k and k["stance"] != cur.get("_stance"):
            cur["_stance"] = k["stance"]
        out.append((t, cur))
    return out


def sample(keys, t):
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            w = smooth((t - t0) / max(1e-6, t1 - t0))
            v = {}
            for f in a:
                if f == "_stance":
                    continue
                if f == "stance":
                    v["feet_a"], v["feet_b"], v["feet_w"] = a["stance"], b["stance"], w
                    continue
                v[f] = lerp(a[f], b[f], w)
            return v
    return dict(keys[-1][1])


def frames(name):
    family, count, keys = CLIPS[name]
    base = P.controls("ready", 0, 1, family)
    ready = dict(F=tuple(base["arms"]["F"]) if not isinstance(base["arms"]["F"], dict) else (.5, -.3, -.2),
                 N=tuple(base["arms"]["N"]) if not isinstance(base["arms"]["N"], dict) else (.4, -.3, .05),
                 wdir=tuple(base["weapon"]["dir"]) if base["weapon"] else (1, 0, 0),
                 lean=float(base["lean"]), twist=float(base["twist"]), bend=0.0, head=0.0, head_yaw=0.0,
                 x=0.0, y=0.0, stance="combat", shake=0.0, collar=0.0)
    keys = resolved(keys, ready)
    for i in range(count + 1):
        t = i / count
        v = sample(keys, t)
        form = P.controls("ready", 0, 1, family)
        tremble = v["shake"] * math.sin(t * 90.0)
        form["arms"]["F"], form["arms"]["N"] = v["F"], v["N"]
        if form["weapon"]:
            form["weapon"] = dict(form["weapon"], dir=v["wdir"])
        form["lean"] = v["lean"] + 1.5 * tremble
        form["twist"] = v["twist"] + 2.0 * tremble
        form["bend"] = v["bend"]
        form["head"] = v["head"] - 1.0 * tremble
        form["head_yaw"] = v["head_yaw"]
        sa, sb, sw = v.get("feet_a", "combat"), v.get("feet_b", "combat"), v.get("feet_w", 0.0)
        form["feet"] = {s: lerp(STANCES[sa][s], STANCES[sb][s], sw) for s in "NF"}
        form["root"][0] += v["x"]
        form["root"][1] = lerp(STANCE_Y[sa], STANCE_Y[sb], sw) + v["y"]
        form["collar"] = {"F": (0., v["collar"], 0.), "N": (0., v["collar"], 0.)}
        yield c.pose_frames(form)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = Path(argv[0]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    names = argv[1:] or list(CLIPS)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = c.make_armature(c.rest_frames())
    for name in names:
        bank(rig, frames(name), out / f"{name}.mot")
        print("wrote", out / f"{name}.mot", CLIPS[name][1], "frames")
