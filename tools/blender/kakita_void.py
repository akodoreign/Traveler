"""Build Kakita's native Void strike with equipped and hidden-headwear variants."""
from pathlib import Path
import math
import sys

import bpy
import numpy as np

# An out-of-tree staging copy can use the project's rig and exporter.
if "--source" in sys.argv:
    sys.path.insert(0, str(Path(sys.argv[sys.argv.index("--source") + 1]).resolve()))

import chara3d as c
from chara3d_victory import bank

FRAMES = 60


def ease(a, b, t):
    x = min(1., max(0., (t - a) / (b - a)))
    return x*x*(3.-2.*x)


def park_sword(form, t):
    joints, forward, up, _, gear = c.solve(form)
    pelvis = joints["pelvis"]
    pelvis_frame = c.frame(pelvis, pelvis + c.EY, c.EX + forward)
    sheath = c.unit(np.asarray(c.poses.SAYA_DIR, float))
    # The parked hilt is mounted at this bind-space socket by hunyuan_weapon.
    socket = c.P("pelvis") + c.SAYA_AT + sheath * .9
    parked = c.driven_frame(
        c.frame(socket, socket - sheath, c.EX), c.rest_frames()["pelvis"], pelvis_frame,
    )
    at, parked_x, parked_axis, _ = parked
    if gear:
        turn = ease(.375, .465, t)
        slide = 7 * (1 - ease(.445, .491, t))
        grip = gear["at"] * (1 - turn) + (at + parked_axis * slide) * turn
        blade_axis = c.unit(gear["dir"] * (1 - turn) + parked_axis * turn)
        _, cut_x, _, _ = c.frame(np.zeros(3), gear["dir"], c.EY + c.EX * .01)
        _, x, _, z = c.frame(np.zeros(3), blade_axis, c.EY + c.EX * .01)
        blade_x = cut_x * (1 - turn) + parked_x * turn
        roll = math.degrees(math.atan2(blade_x @ z, blade_x @ x))
        form["weapon"].update(dir=tuple(blade_axis), roll=roll)
    else:
        release = ease(.50, .61, t)
        grip = at * (1 - release) + joints["gripF"] * release
    face = joints["neck"] + up * 11
    torso = c.rz(-form["lean"]) @ c.ry(form["twist"]) @ c.rx(form["bend"])
    shoulder_to_grip = grip - joints["shF"]
    arm_reach = c.UPPER + c.FORE + c.HAND - .1
    collar_reach = max(0., float(np.linalg.norm(shoulder_to_grip)) - arm_reach)
    collar_offset = torso.T @ (c.unit(shoulder_to_grip) * collar_reach)
    form["collar"]["F"] = tuple(np.asarray(form["collar"]["F"]) + collar_offset)
    form["arms"]["F"] = {"face": tuple(torso.T @ (grip - face))}


def poses(hat):
    phases = c.poses
    for i in range(FRAMES + 1):
        t = i / FRAMES
        form = phases.controls("ready", 0, 1, "iai")
        dash = ease(.015, .07, t) * (1-ease(.33, .44, t))
        back = ease(.73, .79, t) * (1-ease(.94, 1., t))
        running = dash + back
        swing = math.tau * (t * 5.8)
        planted = ease(.19, .25, t) * (1-ease(.31, .38, t))
        form["lean"] = 6 + 22*dash + 12*back - 10*planted
        form["root"][1] = -.03 - .10*dash - .05*back - .18*planted
        form["head"] = -10*dash - 5*back + 3.5*running*math.sin(swing-.5)
        form["twist"] += 9.*running*math.sin(swing)
        form["bend"] += 7.*running*math.cos(swing)
        form["head_yaw"] = -5.*running*math.sin(swing)
        form["collar"] = {"N": (2.*running*math.sin(swing), running, 0.),
                          "F": (-2.*running*math.sin(swing), -.7*running, 0.)}
        for side, sign in c.SIDES:
            wave = sign * math.sin(swing)
            lift = max(0., sign * math.cos(swing)) ** 2
            step = (.30*wave, .13*lift, .04*sign, 9*sign, 24*lift)
            form["feet"] = dict(form["feet"], **{side: phases.lerp(phases.COMBAT[side], step, running*(1-planted))})
        cut = ease(.213, .315, t)
        if .212 < t < .50:
            form["iai"] = 1.
            turn_back = ease(.375, .465, t)
            form["twist"] = (-18 + 37*cut) * (1-turn_back) + form["twist"] * turn_back
            form["arms"]["F"] = phases.lerp((.32,-.44,-.62),(.83,-.14,.40),cut)
            form["weapon"] = dict(hand="F", shift=0, dir=(math.sin(cut*2.7), .035, -math.cos(cut*2.7)))
        if .375 < t < .61:
            park_sword(form, t)
        gesture = ease(.56,.63,t) * (1-ease(.675,.735,t))
        if hat and gesture:
            joints, forward, up, _, _ = c.solve(form)
            grip = joints["gripN"]
            brim = joints["neck"] + up*20.9 + forward*10.0 + c.EZ*7.4
            d = grip*(1-gesture) + brim*gesture - (joints["neck"] + up*11)
            torso = c.rz(-form["lean"]) @ c.ry(form["twist"]) @ c.rx(form["bend"])
            form["arms"]["N"] = {"face": tuple(torso.T @ d)}
        yield c.pose_frames(form)
    yield None


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--")+1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = c.make_armature(c.rest_frames())
    bank(rig, (frame for hat in (False, True) for frame in poses(hat)), out)
