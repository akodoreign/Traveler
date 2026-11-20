"""Bake the strike, stance, and social choreographies on the same 50-joint rig."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy

from export_spell_motion import BASE_FAMILIES, INTERVALS, pose as gesture_pose, ramp
from school_profiles import school_profiles, ALIASES as SCHOOL_ALIASES
from support_profiles import support_profiles, ALIASES as SUPPORT_ALIASES

# base cut, step lead, sink, lean, yaw, lateral sway, high finish
STYLES = {
    "cleave": ("atk_overhead",.14,.14,15,-16,.04,.45),
    "quickdraw": ("atk_draw",.16,.13,11,20,.04,-.08),
    "lunge": ("atk_thrust",.22,.08,16,-11,.02,.08),
    "feint": ("atk_slash",.12,.10,14,16,.11,.15),
    "wheel": ("atk_slash",.14,.12,12,-25,.11,.36),
    "volley": ("atk_thrust",.11,.08,14,-17,.05,.39),
    "drill": ("atk_thrust",.17,.11,12,22,.04,.22),
    "taunt": ("atk_slash",.08,.06,16,-16,.07,.38),
    "focus": ("atk_draw",.08,.19,6,7,.01,.10),
    "command": ("atk_thrust",.06,.08,8,-10,.03,.30),
    "attune": ("atk_slash",.08,.09,-5,15,.04,.34),
    "snatch": ("atk_draw",.13,.16,21,-18,.05,-.24),
    "hail": ("atk_thrust",.10,.07,11,-8,.02,.35),
    "deflect": ("atk_slash",.12,.09,11,25,.07,.16),
    "crush": ("atk_overhead",.13,.25,24,-18,.09,-.19),
    "hammer": ("atk_overhead",.16,.20,25,14,.09,-.24),
    "mountain": ("atk_thrust",.14,.18,10,7,.07,-.08),
    "watch": ("atk_draw",.11,.12,-8,-17,.04,.19),
    "accuse": ("atk_thrust",.12,.10,14,-9,.03,.17),
    "crosscut": ("atk_slash",.13,.12,17,24,.07,.20),
    "bind": ("atk_slash",.10,.11,12,-17,.04,-.19),
    "bow": ("atk_draw",.03,.12,26,2,.04,-.30),
    "copy": ("atk_thrust",.07,.11,6,15,.04,.25),
    "cover": ("atk_thrust",.15,.19,9,18,.08,.09),
    "serve": ("atk_thrust",.04,.13,16,-8,.02,-.06),
    "sweep": ("atk_slash",.12,.18,17,-28,.08,-.29),
    "veil": ("atk_draw",.06,.17,12,12,.09,.06),
    "dress": ("atk_thrust",.05,.16,19,8,.02,-.17),
    "pounce": ("atk_slash",.20,.15,16,-21,.11,.29),
    "rush": ("atk_thrust",.22,.14,20,16,.08,.29),
    "underhand": ("atk_slash",.10,.16,17,-19,.04,.26),
    "stop": ("atk_thrust",.11,.07,13,11,.02,.09),
    "examine": ("atk_thrust",.04,.10,23,5,.02,-.14),
    "brace": ("atk_thrust",.10,.23,17,-9,.12,-.10),
    "balance": ("atk_draw",.17,.09,8,17,.14,.20),
    "close": ("atk_draw",.07,.12,8,10,.03,-.09),
    "raise": ("atk_overhead",.13,.08,7,-15,.03,.59),
    "crouch": ("atk_slash",.15,.22,29,22,.09,-.29),
    "snare": ("atk_thrust",.08,.13,17,14,.06,-.08),
    "draw": ("atk_thrust",.09,.11,10,-8,.05,.05),
    "bridge": ("atk_thrust",.06,.11,11,9,.06,.12),
    "jab": ("atk_thrust",.13,.09,13,14,.03,.13),
    "hook": ("atk_slash",.14,.11,15,-21,.09,.13),
    "wing": ("atk_slash",.19,.11,16,-25,.13,.49),
}


def stance_pose(c, row, family, frame, critical):
    _,step,sink,lean,yaw,side,_ = STYLES[row["style"]]
    gesture = {
        **row, "gesture":row["lead"] or "unfurl",
        "body": [max(.45,4.2*step)*row["effort"],sink,lean,yaw],
    }
    if row["style"] == "focus":
        # The scabbard hand stays at the hip while the torso settles into focus.
        return focus(c, gesture, family, frame, critical)
    return gesture_pose(c, gesture, family, frame, critical)


def focus(c, row, family, frame, critical):
    t = frame / INTERVALS
    settle = ramp(t,0,row["beats"][1])*(1-ramp(t,row["beats"][2],1))
    exhales = math.sin(math.pi*t*2)*settle
    form = c.poses.controls("ready",0,1,family)
    form["root"][1] -= (.15 if critical else .092)*settle
    form["root"][2] += .031*settle
    form["lean"] += 8.0*settle
    form["twist"] += 4.0*settle
    form["bend"] -= 6.0*settle
    form["head"] += 10*settle+2.5*exhales
    form["saya_pull"] += 3.3*settle
    if family != "iai":
        form["collar"] = {"N":(-1.8*settle,-1.3*settle,0), "F":(2.2*settle,-1.9*settle,0)}
    return c.pose_frames(form)


def strike_pose(c, row, family, frame, critical):
    t = frame / INTERVALS
    style = row["style"]
    cut,step,sink,lean,yaw,side,high = STYLES[style]
    if family == "iai":
        cut = "atk_draw"
    elif family in {"fist","club"} and style in {"brace","bind","cover","mountain","crouch"}:
        cut = "atk_thrust"
    elif family == "fist" and style == "balance":
        cut = "atk_draw"
    gather, release, settle = row["beats"][1:]
    effort = row["effort"]
    if critical:
        release += .07
        effort *= 1.18
    base_time = (.60*t/release if t <= release else .60 + .40*(t-release)/(1-release))
    phase = int(round(base_time*800))
    form = c.combat_controls(cut,phase,801,family)
    if frame in (0,INTERVALS):
        return c.pose_frames(form)
    wind = ramp(t,.03,gather)*(1-ramp(t,gather,release))
    commit = ramp(t,gather,release)*(1-ramp(t,release,settle))
    follow = ramp(t,release,settle)*(1-ramp(t,settle,1))
    grounded = family not in {"bow","gun"}
    load = .74 if grounded else .36
    amplitude = load*effort

    form["root"][0] += amplitude*step*(.79*commit-.31*wind)
    form["root"][1] -= amplitude*sink*(.73*wind+.58*commit)
    form["root"][2] += amplitude*side*(.47*wind-.66*commit+.21*follow)
    form["lean"] += amplitude*lean*(.72*commit-.46*wind)
    form["twist"] += amplitude*yaw*(.86*wind-1.05*commit+.45*follow)
    form["bend"] += amplitude*yaw*(-.13*wind+.20*follow)
    form["head_yaw"] = -.79*form["twist"]
    form["head"] -= .24*lean*commit
    if style in {"watch","balance","raise","wing"}:
        form["head"] -= (8.5+4.2*effort)*wind+(3.1+high*5)*commit
    if style in {"snare","close","cover","freeze","crouch"}:
        form["head"] += (6+9*sink)*wind
    if style in {"feint","deflect","crosscut","wheel","drill","bind"}:
        turn = math.sin(t*math.pi*4)*(wind+follow)
        form["torso_turn"] = turn
        form["twist"] += 10.0*turn
        form["root"][2] += .037*turn
    if grounded:
        side_id = "F" if style in {"crosscut","deflect","bind","crouch","wheel"} else "N"
        x,y,z,yaw_at,pitch = form["feet"][side_id]
        lift = .19 if style in {"pounce","balance","wing","rush"} else .082
        form["feet"] = dict(form["feet"],**{side_id:(x+step*.42*commit,y+lift*wind,
                              z+side*.25*commit,yaw_at+12*follow,pitch+15*commit)})
        if style in {"pounce","wing"} and .18<t<.78:
            form["root"][1] += .15*commit
        weapon = form["weapon"]
        if weapon and family != "iai":
            dx,dy,dz = weapon["dir"]
            weapon["dir"] = (dx+.17*commit,dy+high*(commit+.27*wind),
                             dz+.019*yaw*(commit+.33*follow))
            weapon["roll"] = weapon.get("roll",0) + .61*yaw*wind -1.05*yaw*follow
    return c.pose_frames(form)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("repo",type=Path)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--bank",choices=("school","support"),default="school")
    parser.add_argument("--families",nargs="+",choices=BASE_FAMILIES,default=list(BASE_FAMILIES))
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    sys.path[:0]=[str(args.repo/"tools/blender"),str(args.repo/"tools")]
    import chara3d as c
    from chara3d_victory import bank
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig=c.make_armature(c.rest_frames())
    rows=school_profiles() if args.bank=="school" else support_profiles()
    aliases=SCHOOL_ALIASES if args.bank=="school" else SUPPORT_ALIASES
    index={}
    first=0
    for sid,row in rows.items():
        index[sid]={**row,"start":first,"finish":first+INTERVALS,
                    "void":[first+INTERVALS+1,first+2*INTERVALS+1]}
        first+=2*(INTERVALS+1)
    for sid,src in aliases.items():
        index[sid]={**index[src],"asset":src}
    out=args.bundle/"native_chara/ability"

    def frames(family):
        for sid,row in rows.items():
            form = strike_pose if row["movement"]=="strike" else stance_pose
            for critical in (False,True):
                yield None
                for i in range(INTERVALS+1):
                    try:
                        yield form(c,row,family,i,critical)
                    except Exception as ex:
                        raise ValueError(f"{sid}, {family}, frame {i}, void={critical}") from ex

    for family in args.families:
        bank(rig,frames(family),out/(args.bank+"_"+family+".mot"))
        print(f"{family}: {len(rows)} skills, {first} frames",flush=True)
    (out/(args.bank+"-index.json")).write_text(json.dumps(index,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()

