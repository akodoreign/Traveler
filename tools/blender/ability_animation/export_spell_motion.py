"""Build uniquely timed spell motion banks on the shipped full humanoid rig."""
import argparse
from pathlib import Path
import json
import math
import sys

import bpy

from elemental_profiles import spell_profiles

BASE_FAMILIES = ("fist", "blade", "iai", "short", "club", "pole", "bow", "gun")
INTERVALS = 30
# Reach targets in production arm-control coordinates: set, gather, release, follow.
GESTURES = {
    "offer": ((.37,-.43,-.09),(.46,-.12,-.17),(.76,-.17,-.09),(.49,-.30,-.14)),
    "draw": ((.38,-.55,-.35),(.17,-.32,-.22),(.78,-.06,-.15),(.59,-.31,-.27)),
    "chop": ((.33,-.10,-.40),(.31,.34,-.26),(.67,-.26,-.05),(.52,-.53,-.19)),
    "fan": ((.48,-.39,-.45),(.49,.05,-.52),(.83,-.03,.23),(.51,-.33,.05)),
    "plant": ((.51,-.36,-.22),(.67,-.19,-.25),(.54,-.66,-.06),(.24,-.62,-.21)),
    "ward": ((.22,-.48,-.17),(.38,-.08,.36),(.69,.12,.05),(.54,-.25,-.27)),
    "brush": ((.31,-.24,-.29),(.53,.14,.26),(.66,-.17,-.49),(.51,-.40,-.17)),
    "swirl": ((.46,-.58,-.41),(.48,.22,-.39),(.88,.02,.23),(.69,-.32,-.22)),
    "hush": ((.36,-.55,-.25),(.42,.20,-.02),(.66,.06,-.16),(.36,-.17,-.30)),
    "pinch": ((.29,-.42,-.32),(.51,.14,-.20),(.84,-.09,-.04),(.38,-.38,-.36)),
    "seal": ((.32,-.52,-.28),(.40,.12,-.42),(.72,-.31,.10),(.42,-.23,.29)),
    "still": ((.22,-.56,-.12),(.36,-.31,.20),(.41,-.34,.07),(.32,-.49,-.09)),
    "raise": ((.46,-.57,-.22),(.56,-.13,-.42),(.38,.58,-.11),(.34,.22,-.23)),
    "tap": ((.36,-.22,-.18),(.49,.07,-.24),(.85,.12,-.12),(.41,-.39,-.16)),
    "heave": ((.37,-.49,-.27),(.17,-.64,-.31),(.71,.38,-.05),(.57,.21,.11)),
    "press": ((.40,-.22,-.22),(.48,-.02,.33),(.66,-.42,.07),(.35,-.52,-.11)),
    "brandish": ((.33,-.22,-.43),(.25,.18,-.57),(.45,.49,.26),(.38,.01,-.11)),
    "cup": ((.28,-.54,-.21),(.53,-.26,.27),(.62,.13,.12),(.48,-.20,-.09)),
    "coil": ((.29,-.33,-.35),(.53,-.20,.44),(.52,.17,-.09),(.36,-.37,-.40)),
    "bridge": ((.34,-.27,.38),(.46,.25,.35),(.61,.31,-.37),(.44,-.19,-.32)),
    "armsAcross": ((.39,-.36,-.22),(.52,.04,.54),(.45,.21,.38),(.33,-.38,.10)),
    "reachBelow": ((.32,-.57,-.21),(.50,-.70,-.07),(.76,-.34,.14),(.53,-.31,.17)),
    "pat": ((.51,-.29,-.13),(.69,.18,-.11),(.61,-.53,.13),(.38,-.43,-.18)),
    "unfurl": ((.27,-.37,.35),(.48,.18,.32),(.72,.42,-.39),(.52,-.10,-.55)),
    "step": ((.34,-.44,-.34),(.46,.02,-.24),(.55,-.50,-.26),(.49,-.29,-.14)),
    "claw": ((.38,-.22,-.41),(.28,.29,-.53),(.66,-.28,.32),(.43,-.43,.16)),
    "inspect": ((.39,-.44,-.17),(.28,.21,.21),(.58,.26,-.16),(.48,.06,-.35)),
    "tracer": ((.61,-.36,-.22),(.71,.30,-.23),(.69,.03,.39),(.49,-.37,.23)),
    "brace": ((.31,-.53,-.28),(.44,-.12,.39),(.48,-.04,.27),(.53,-.48,-.21)),
    "push": ((.40,-.16,.11),(.30,.02,.39),(.91,.08,-.02),(.70,-.16,-.07)),
}

def ramp(t, a, b):
    x = min(1, max(0, (t-a)/(b-a)))
    return x*x*(3-2*x)

def track(points, timing, t):
    for end in range(1,len(timing)):
        if t <= timing[end]:
            return tuple(a+(b-a)*ramp(t,timing[end-1],timing[end])
                         for a,b in zip(points[end-1],points[end]))
    return tuple(points[-1])

def pose(c, row, family, i, critical):
    t = i / INTERVALS
    form = c.poses.controls("ready", 0, 1, family)
    if i in (0, INTERVALS):
        return c.pose_frames(form)
    weapon = form["weapon"]
    free = "F" if weapon and weapon["hand"] == "N" else "N"
    joints, *_ = c.solve(form)
    rotation = c.rz(-form["lean"]) @ c.ry(form["twist"]) @ c.rx(form["bend"])
    direction = (rotation.T @ (joints["grip"+free] - joints["sh"+free])) / (c.UPPER+c.FORE+c.HAND)
    base = (direction[0], direction[1], direction[2] if free=="N" else -direction[2])
    if weapon:
        weapon["sep"] = None
    set_pos, gather, release, follow = GESTURES[row["gesture"]]
    reach, drop, bend, twist = row["body"]
    beats = list(row["beats"])
    strength = 1.0
    if critical:
        # The crit pulls back into a second gather, uses a lifted heel and opens through the hip.
        strength = 1.27
        beats[1] += .04
        beats[2] += .07
        gather = (gather[0]*.86, gather[1]+.13, gather[2]*1.19)
        release = (release[0]*1.04, release[1]+.12, release[2]*1.16)
    timing = [0,*beats,1]
    targets = [base, set_pos, gather, release, follow, base]
    form["arms"][free] = track(targets,timing,t)
    tilt = ramp(t,0,beats[1]) * (1-ramp(t,beats[1],beats[2]))
    hit = ramp(t,beats[1],beats[2]) * (1-ramp(t,beats[2],1))
    spill = ramp(t,beats[2],beats[3]) * (1-ramp(t,beats[3],1))
    form["root"][0] += strength * (.052*reach*hit-.024*tilt)
    form["root"][1] -= strength * drop * (.39*tilt+.28*hit)
    form["root"][2] += strength * (.031*tilt-.04*spill) * (1 if free=="N" else -1)
    form["lean"] += strength * (-bend*.48*tilt+bend*.8*hit)
    form["twist"] += strength * (twist*.67*tilt-twist*hit)
    form["head"] -= bend*.37*hit
    form["head_yaw"] = -form["twist"]*.72
    form["bend"] += strength*(6.4*tilt-5.5*spill)
    form["collar"] = {free: (2.4*hit,2.1*tilt,0.), "F" if free=="N" else "N": (-1.2*spill,.7*hit,0.)}
    gesture = row["gesture"]
    if critical or gesture in {"step", "brandish", "raise", "heave", "pat"}:
        x,lift,z,yaw,pitch = form["feet"][free]
        lead = .10 if gesture in {"step", "heave", "pat"} else .045
        heel = .085 if gesture in {"step", "brandish"} else .025
        form["feet"] = dict(form["feet"], **{free:(x+lead*hit,lift+heel*tilt,z,yaw+8*spill,pitch+13*hit)})
    if gesture in {"inspect", "reachBelow", "brace", "press"}:
        form["head"] += 11.0 * tilt - 4.0 * spill
    return c.pose_frames(form)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("repo",type=Path)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--families",nargs="+",choices=BASE_FAMILIES,default=list(BASE_FAMILIES))
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path[:0]=[str(args.repo/"tools/blender"),str(args.repo/"tools")]
    import chara3d as c
    from chara3d_victory import bank
    rows=json.loads((args.bundle/"spell_profiles.json").read_text(encoding="utf-8-sig"))
    rows.update(spell_profiles())
    out=args.bundle/"native_chara/ability"
    out.mkdir(parents=True,exist_ok=True)
    for row in rows.values():
        if len(row["beats"])!=4 or not 0<row["beats"][0]<row["beats"][1]<row["beats"][2]<row["beats"][3]<1:
            raise ValueError("Motion keyframes must advance from set through follow")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig=c.make_armature(c.rest_frames())
    index={}
    first=0
    for key,row in rows.items():
        index[key]={**row,"start":first,"finish":first+INTERVALS}
        first+=INTERVALS+1
        index[key]["void"]=[first,first+INTERVALS]
        first+=INTERVALS+1

    def frames(family):
        for row in rows.values():
            for critical in (False,True):
                yield None
                for i in range(INTERVALS+1):
                    yield pose(c,row,family,i,critical)
    for family in args.families:
        bank(rig,frames(family),out/("spells_"+family+".mot"))
        print(f"{family}: {len(rows)} element and support clips, {first} frames",flush=True)
    (out/"spell-index.json").write_text(json.dumps(index,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
