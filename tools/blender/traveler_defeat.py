"""Bake native Traveler collapses, held KO poses, and recovery on the stock rig."""
from dataclasses import dataclass
from pathlib import Path
import json
import math
import sys

root, output = (Path(x).resolve() for x in sys.argv[sys.argv.index("--") + 1:])
sys.path[:0] = [str(root / "tools"), str(root / "tools" / "blender")]

import bpy
import numpy as np
from mathutils import Matrix

import chara3d as c
from chara3d_victory import bank
from combat_fidgets import touch
from rig3d_poses import lerp


FALL = 31
RISE = 45
FPS = 30
FAMILIES = ("blade", "bow", "club", "fist", "gun", "iai", "pole", "short")


@dataclass(frozen=True)
class Collapse:
    pitch: float
    roll: float
    recoil: float
    brace: float
    lead: str
    arm: tuple
    hold: tuple


CAST = {
    "trav_natsuko": Collapse(-79, 24, -.06, .90, "N", (.72, -.44, .25), (.39, -.83, .42)),
    "trav_rensei": Collapse(84, -12, -.13, .38, "F", (.23, -.62, .07), (.07, -.90, .18)),
    "trav_gendo": Collapse(76, 24, -.08, .78, "N", (.55, -.60, .33), (.22, -.70, .60)),
    "trav_shizue": Collapse(-84, -15, -.02, .91, "F", (.79, -.52, .23), (.35, -.81, .22)),
    "trav_haruki": Collapse(-73, 27, -.07, .73, "N", (.68, -.50, .17), (.30, -.77, .36)),
    "trav_mitsue": Collapse(74, -38, -.09, .48, "F", (.28, -.68, .37), (.12, -.84, .25)),
    "trav_tamotsu": Collapse(85, 19, -.15, .57, "N", (.28, -.57, .79), (.13, -.75, .67)),
    "trav_sayo": Collapse(-77, -24, -.04, .66, "F", (.72, -.58, .28), (.42, -.76, .40)),
}


def ramp(t, start, end):
    t = np.clip((t - start) / (end - start), 0.0, 1.0)
    return float(t * t * (3.0 - 2.0 * t))


def bump(t, start, peak, leave, end):
    return ramp(t, start, peak) * (1.0 - ramp(t, leave, end))


def tip_pose(profile, family, time):
    base = c.poses.controls("ready", 0, 1, family)
    shock = bump(time, .018, .12, .19, .31)
    slip = ramp(time, .14, .51)
    buckle = bump(time, .20, .39, .49, .69)
    fall = ramp(time, .38, .84)
    impact = bump(time, .77, .84, .86, .97)
    bracing = profile.brace * bump(time, .21, .40, .60, .84)
    other = "F" if profile.lead == "N" else "N"
    travel = profile.recoil * (.72 * slip + .28 * fall)
    lean = -math.copysign(1.0, profile.pitch)
    base["root"][0] += travel - .10 * shock
    base["root"][1] -= .23 * slip + .11 * buckle + .045 * impact
    base["root"][2] += math.copysign(1.0, profile.roll) * (.10 * slip + .05 * shock)
    base["lean"] += -11 * shock + lean * (17 * buckle + 19 * slip - 14 * fall)
    base["twist"] += math.copysign(1.0, profile.roll) * (12 * shock + 18 * slip)
    base["head"] -= lean * (11 * shock - 8 * slip + 8 * fall)
    base["head_bank"] = .24 * profile.roll * slip
    base["hair_follow"] = (.08 * shock - .08 * impact, .17 * fall * math.copysign(1, profile.roll))
    base["collar"] = {
        profile.lead: (2.4 * bracing, -3.0 * fall, -.3 * fall),
        other: (-1.3 * bracing, 0.9 * shock, .2 * fall),
    }
    for side, sign in c.SIDES:
        foot = base["feet"][side]
        tuck = .24 if side == profile.lead else -.21
        to = (tuck + travel, .10 if side == profile.lead else .025,
              .085 * sign, foot[3] + 15 * sign, 14 * sign)
        step = bump(time, .03, .14, .21, .37) if side == other else 0.
        staggered = (foot[0] - .17 * step, foot[1] + .058 * step,
                     foot[2] + .025 * sign * step, foot[3], foot[4] + 18. * step)
        base["feet"] = dict(base["feet"], **{side: lerp(staggered, to, slip)})
    touch(base, family, profile.lead, profile.arm, bracing)
    touch(base, family, profile.lead, profile.hold, fall)
    touch(base, family, other, (.16, -.86, .38), .82 * fall)
    frames = c.pose_frames(base)
    hip = frames["pelvis"][0]
    turn = c.rz(profile.pitch * (fall + .032 * impact)) @ c.rx(profile.roll * fall)
    lower = hip[1] - (hip[1] - 10.8) * fall
    origin = np.array((hip[0] + lean * 12.5 * fall, lower, hip[2] + .12 * profile.roll * fall))
    tilted = {
        name: (origin + turn @ (f[0] - hip), *(turn @ axis for axis in f[1:])) if f else None
        for name, f in frames.items()
    }
    # Protect contact points during the descent. The feet need clearance until
    # the body rolls and the bracing hand, hip, and head become the support.
    bounds = {"footN": 6 - 1.5 * fall, "footF": 6 - 1.5 * fall,
              "pelvis": 10.8 * fall, "head": 10.2 * fall,
              "handN": 3.2 * fall, "handF": 3.2 * fall}
    correction = max(0.0, *(level - tilted[name][0][1] for name, level in bounds.items()))
    rise = np.array((0., correction + 1.2 * impact, 0.))
    return {
        name: (f[0] + rise, *f[1:]) if f else None
        for name, f in tilted.items()
    }


@dataclass(frozen=True)
class Rise:
    plant: float
    knee: float
    front: str
    forearm: bool
    turn: float


RISES = {
    "trav_natsuko": Rise(.26, .62, "F", True, 10.),
    "trav_rensei": Rise(.29, .63, "F", False, -13.),
    "trav_gendo": Rise(.31, .68, "N", False, 15.),
    "trav_shizue": Rise(.25, .58, "F", False, -7.),
    "trav_haruki": Rise(.29, .65, "N", True, 9.),
    "trav_mitsue": Rise(.21, .56, "N", True, -19.),
    "trav_tamotsu": Rise(.30, .68, "F", False, 13.),
    "trav_sayo": Rise(.24, .59, "F", False, -8.),
}


def bone_frame(matrix):
    """Return the authoring-space frame expected by the shared exporter."""
    def coordinates(column):
        return np.array((column.x, column.z, -column.y), float)

    return (coordinates(matrix.translation), *(coordinates(matrix.col[i]) for i in range(3)))


def articulated_blend(a, b, amount):
    """Blend the roll in parent space so the arms and legs keep their lengths."""
    parents = c.humanoid_parents()
    angles_a = {name: c.matrix(f) for name, f in a.items() if f}
    angles_b = {name: c.matrix(f) for name, f in b.items() if f}
    out = {}
    transforms = {}

    def visit(name):
        if name in transforms:
            return transforms[name]
        if name not in angles_a or name not in angles_b:
            transforms[name] = angles_b.get(name) or angles_a.get(name)
            return transforms[name]
        mat_a, mat_b = angles_a[name], angles_b[name]
        parent = parents.get(name)
        if parent:
            mat_a = angles_a[parent].inverted() @ mat_a
            mat_b = angles_b[parent].inverted() @ mat_b
        rotation = mat_a.to_quaternion().slerp(mat_b.to_quaternion(), amount)
        offset = mat_a.translation.lerp(mat_b.translation, amount)
        frame = Matrix.Translation(offset) @ rotation.to_matrix().to_4x4()
        transforms[name] = visit(parent) @ frame if parent else frame
        return transforms[name]

    for name in a:
        matrix = visit(name)
        out[name] = bone_frame(matrix) if matrix is not None else None
    return out


def apply_hand(pose, side, wrist_goal, amount, forearm):
    if amount <= 0.:
        return
    upper, fore, hand = ("upper" + side, "fore" + side, "hand" + side)
    shoulder, old_elbow, old_wrist = (pose[name][0] for name in (upper, fore, hand))
    sign = 1. if side == "N" else -1.
    target = old_wrist * (1. - amount) + wrist_goal * amount
    support = np.array((-.30, -.81 if forearm else -.17, .71 * sign))
    pole = c.unit(old_elbow - shoulder) * (1. - amount) + support * amount
    elbow, wrist = c.ik(shoulder, target, c.UPPER, c.FORE, pole)
    direction = c.unit(pose[hand][2] * (1. - amount) + np.array((.96, 0., .27 * sign)) * amount)
    pose[upper] = c.frame(shoulder, elbow, wrist - elbow)
    pose[fore] = c.frame(elbow, wrist, shoulder - elbow)
    pose[hand] = c.frame(wrist, wrist + direction, c.EY)
    rest = c.rest_frames()
    for name, _, _, _ in c.digit_bones(side, sign):
        pose[name] = c.driven_frame(rest[name], rest[hand], pose[hand])


def apply_knee(pose, side, contact, amount):
    if amount <= 0.:
        return
    thigh, shin, foot = ("thigh" + side, "shin" + side, "foot" + side)
    hip, old_knee, ankle = (pose[name][0] for name in (thigh, shin, foot))
    pole = c.unit(old_knee - hip) * (1. - amount) + c.unit(contact - hip) * amount
    knee, ankle = c.ik(hip, ankle, c.THIGH, c.SHIN, pole)
    pose[thigh] = c.frame(hip, knee, c.EX)
    pose[shin] = c.frame(knee, ankle, c.EX)
    pose[foot] = (ankle, *pose[foot][1:])


def recovery_frame(profile, rise, family, down, time):
    """Solve fixed supports independently of the torso's rise."""
    form = c.poses.controls("ready", 0, 1, family)
    initial_hip = down["pelvis"][0]
    back = profile.pitch > 0
    side = 1. if profile.roll > 0 else -1.
    front = rise.front
    rear = "N" if front == "F" else "F"
    rear_sign = 1. if rear == "N" else -1.
    ready_x, ready_y, ready_z = list(form["root"])
    bulky = family in ("pole", "bow", "club", "gun")
    weapon = form["weapon"]
    weapon_hand = weapon["hand"] if weapon else None
    support = ("F" if weapon_hand == "N" else "N") if weapon_hand else profile.lead
    support_sign = 1. if support == "N" else -1.
    other = "F" if support == "N" else "N"

    push_time = rise.plant + (.215 if bulky else .185)
    push = ramp(time, rise.plant + .018, push_time)
    gather = ramp(time, push_time, rise.knee)
    stand = ramp(time, rise.knee + .040, .95)
    finish = ramp(time, .91, 1.0)
    settle = bump(time, .81, .91, .93, 1.0)

    toe_angle = math.radians(51.)
    toe_height = max(x * 1.12 * math.sin(toe_angle) - (low - 6.) * math.cos(toe_angle)
                     for x, low, *_ in c.FOOT)
    rear_ankle = np.array((-19.5, toe_height + .2, rear_sign * 9.))
    knee_z = rear_sign * 8.7
    knee_y = 4.6
    knee_dx = math.sqrt(c.SHIN ** 2 - (rear_ankle[1] - knee_y) ** 2 - (rear_ankle[2] - knee_z) ** 2)
    rear_contact = np.array((rear_ankle[0] + knee_dx, knee_y, knee_z))
    hip_x = -5.5 + .05 * rise.turn
    hip_z = -.9 * rear_sign
    knee_hip_y = knee_y + 2. + math.sqrt(c.THIGH ** 2 - (rear_contact[0] - hip_x) ** 2
                                         - (knee_z - hip_z - rear_sign * 5.5) ** 2)
    knee_hip = np.array((hip_x, knee_hip_y, hip_z))
    roll_hip = np.array((initial_hip[0] + (2.5 if not back else 1.0),
                         13.2 if back else 14.8, initial_hip[2] + 2.0 * side))
    push_hip = np.array((-9.4 if back else -7.2, 18.2, 3.5 * support_sign))
    ready_hip = c.P("pelvis") + np.array((ready_x, ready_y, ready_z)) * c.L
    hip = roll_hip * (1. - push) + push_hip * push
    hip = hip * (1. - gather) + knee_hip * gather
    hip = hip * (1. - stand) + ready_hip * stand
    hip[0] += (3.6 if bulky else 2.8) * math.sin(math.pi * stand)
    hip[1] -= 1.25 * settle
    form["root"] = (hip - c.P("pelvis")) / c.L

    rolled_lean = -31. if back else 65.
    torso = (rolled_lean * (1. - push) + 62. * push) * (1. - gather) + 34. * gather
    form["lean"] += torso * (1. - stand) + 3.0 * settle
    form["twist"] += rise.turn * (1. - gather) * (1. - finish)
    side_lean = 42. if back else 28.
    form["bend"] += support_sign * (side_lean * (1. - push) + 8. * push) * (1. - gather)
    form["head"] += (-9. + 23. * gather) * (1. - stand) - 6. * settle
    form["head_bank"] = -side * 8. * (1. - push)
    form["hair_follow"] = (-.09 * (1. - gather) + .05 * settle, side * .14 * (1. - push))

    for foot, sign in c.SIDES:
        current = np.array(form["feet"][foot], float)
        if foot == rear:
            start = np.array((rear_ankle[0] - 7., 8.2, rear_ankle[2] + 5. * sign))
            step = np.array((rear_ankle[0], rear_ankle[1], rear_ankle[2]))
            draw = ramp(time, rise.plant + .080, rise.knee - .012)
            point = start * (1. - draw) + step * draw
            point[1] += 4.2 * math.sin(math.pi * draw)
            foot_roll = 51. * draw
            switch = ramp(time, .74, .94)
        else:
            point = np.array((14.3, 6., sign * (9.0 if front == "N" else 8.2)))
            foot_roll = 0.
            switch = ramp(time, .80, .97) if front == "N" else finish
        placed = np.array((point[0] / c.L, (point[1] - 6.) / c.L,
                           (point[2] - 5.5 * sign) / c.L, 5. * sign, foot_roll))
        moved = (1. - switch) * placed + switch * current
        if front == "N" or foot == rear:
            moved[1] += 2.9 * math.sin(math.pi * switch) / c.L
        form["feet"] = dict(form["feet"], **{foot: tuple(moved)})

    if weapon:
        weapon["sep"] = None
        if bulky:
            direction = np.asarray(weapon["dir"], float)
            carrying = np.array((.87, .11, .48 if weapon_hand == "N" else -.48))
            weapon["dir"] = tuple(c.unit(carrying * (1. - stand) + direction * stand))
    replant = ramp(time, rise.plant + .044, push_time - .014) if back else 1.
    back_wrist = np.array((initial_hip[0] - 7., 3.8, 20. * support_sign))
    push_wrist = np.array((12.5 if back else 26., 3.8, 14.8 * support_sign))
    lead_wrist = back_wrist * (1. - replant) + push_wrist * replant
    lead_wrist[1] += 7.8 * math.sin(math.pi * replant)
    rest = c.pose_frames(form)
    ground_hold = 1. - ramp(time, push_time + .055, rise.knee - .046)
    apply_hand(rest, support, lead_wrist, ground_hold, rise.forearm)
    if not weapon:
        second = np.array((14.5, 3.8, -12.5 * support_sign))
        second_hold = ramp(time, rise.plant - .07, rise.plant + .10) * ground_hold * replant
        apply_hand(rest, other, second, second_hold, False)
    knee_hold = ramp(time, push_time + .04, rise.knee - .014) * (1. - ramp(time, rise.knee + .065, .81))
    apply_knee(rest, rear, rear_contact, knee_hold)
    return rest


def frames(family):
    for actor, profile in CAST.items():
        rise = RISES[actor]
        down = tip_pose(profile, family, 1.0)
        ready = tip_pose(profile, family, 0.0)
        first_contact = recovery_frame(profile, rise, family, down, rise.plant)
        for i in range(FALL + 1):
            yield down if i == FALL else tip_pose(profile, family, i / FALL)
        yield None
        for i in range(RISE + 1):
            time = i / RISE
            if i == 0:
                yield down
            elif i == RISE:
                yield ready
            elif time < rise.plant:
                yield articulated_blend(down, first_contact, ramp(time, .01, rise.plant))
            else:
                pose = recovery_frame(profile, rise, family, down, time)
                release = ramp(time, .92, 1.0)
                yield articulated_blend(pose, ready, release) if release else pose
        yield None


def main():
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig = c.make_armature(c.rest_frames())
    for family in FAMILIES:
        bank(rig, frames(family), output / f"{family}.mot")
    stride = FALL + 1 + RISE + 1
    actors = {
        actor: {"collapse": i * stride, "down": i * stride + FALL,
                "rise": i * stride + FALL + 1, "end": (i + 1) * stride - 1}
        for i, actor in enumerate(CAST)
    }
    (output / "index.json").write_text(json.dumps({"fps": FPS, "actors": actors}, indent=2) + "\n",
                                      encoding="utf-8")


if __name__ == "__main__":
    main()

