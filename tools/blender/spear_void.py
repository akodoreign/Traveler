"""Export the shared native yari leap on Traveler's humanoid armature."""
from pathlib import Path
import math
import sys

import bpy

TOOLS = Path(__file__).resolve().parents[1]
if "--source" in sys.argv:
    TOOLS = Path(sys.argv[sys.argv.index("--source") + 1]).resolve()
sys.path.insert(0, str(TOOLS / "blender"))

import chara3d as c
from chara3d_victory import bank


FRAMES = 60


def ease(start, end, time):
    x = min(1.0, max(0.0, (time - start) / (end - start)))
    return x * x * (3.0 - 2.0 * x)


def frames():
    baseline = c.poses.COMBAT
    for i in range(FRAMES + 1):
        time = i / FRAMES
        form = c.poses.controls("ready", 0, 1, "pole")
        coil = ease(.00, .16, time) * (1.0 - ease(.19, .27, time))
        flight = ease(.19, .31, time) * (1.0 - ease(.46, .57, time))
        drive = ease(.466, .56, time) * (1.0 - ease(.63, .72, time))
        land = ease(.51, .59, time) * (1.0 - ease(.61, .72, time))
        retreat = ease(.70, .765, time) * (1.0 - ease(.92, 1.0, time))
        swing = math.tau * (time - .70) * 7
        form["root"][1] += -.14 * coil + .15 * flight - .14 * land
        form["root"][0] += -.05 * coil + .17 * drive
        form["root"][2] += .024 * retreat * math.sin(swing)
        form["lean"] += 15 * coil + 12 * flight + 21 * drive + 12 * retreat
        form["twist"] += -15 * coil + 14 * drive + 8 * retreat * math.sin(swing)
        form["bend"] += -7 * flight - 8 * drive
        form["head"] += -8 * coil - 9 * flight - 8 * drive
        form["head_yaw"] = -5 * coil + 5 * flight
        form["collar"] = {"N": (5 * drive, flight, 0), "F": (2 * flight, -drive, 0)}
        for side, sign in c.SIDES:
            # Tuck the trailing foot on the way up, and land over the leading one.
            tuck = (.12, .18, -.02, 15, 17) if side == "F" else (-.12, .24, .06, 37, 40)
            recover = (.18 * sign * math.sin(swing), .07 * max(0.0, sign * math.cos(swing)),
                       .03 * sign, 12 * sign, 15 * max(0.0, sign * math.cos(swing)))
            foot = c.poses.lerp(baseline[side], tuck, flight)
            foot = c.poses.lerp(foot, recover, retreat)
            form["feet"] = dict(form["feet"], **{side: foot})
        # Spin the shaft through two complete turns. Keep the circular motion
        # in the authored direction and regrip only once the tip faces forward.
        wind = ease(.17, .20, time) * (1.0 - ease(.448, .477, time))
        spin = min(1.0, max(0.0, (time - .201) / (.453 - .201)))
        phase = (spin + ease(0.0, 1.0, spin)) * .5
        angle = math.atan2(-.12, .94) + 2.0 * math.tau * phase
        pitch = .30 + .55 * wind + .14 * wind * math.sin(angle)
        orbit = (.948 * math.cos(angle), pitch, .948 * math.sin(angle))
        aim = ease(.453, .483, time) * (1.0 - ease(.65, .76, time))
        form["weapon"]["dir"] = c.poses.lerp(orbit, (1.0, .02, -.026), aim)
        form["weapon"]["sep"] = None
        form["arms"]["F"] = (.20, -.10, .36)
        form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.34, .05, .14), flight)
        form["arms"]["N"] = c.poses.lerp(form["arms"]["N"], (.70, -.23, .03), drive)
        joints, _, up, _, gear = c.solve(form)
        held = joints["gripN"] + gear["dir"] * (17 - 8 * drive)
        guide = wind * (1.0 - drive)
        target = held * (1.0 - guide) + joints["gripF"] * guide
        torso = c.rz(-form["lean"]) @ c.ry(form["twist"]) @ c.rx(form["bend"])
        form["arms"]["F"] = {"face": tuple(torso.T @ (target - joints["neck"] - up * 11))}
        yield c.pose_frames(form)


if __name__ == "__main__":
    target = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    rig = c.make_armature(c.rest_frames())
    bank(rig, frames(), target)
