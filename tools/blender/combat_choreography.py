"""Native combat pose timing on the shared humanoid skeleton."""
import math

import rig3d_poses as poses


ATTACK_WEIGHT = {
    "atk_slash": (9., 12., .035),
    "atk_thrust": (4., 5., .048),
    "atk_overhead": (8., 9., .038),
    "atk_draw": (9., 15., .029),
}


def ease(t, start, end):
    u = min(1., max(0., (t - start) / (end - start)))
    return u * u * (3. - 2. * u)


def pulse(t, begin, peak, hold, end):
    return ease(t, begin, peak) * (1. - ease(t, hold, end))


def roll_contact(foot, pitch, shape):
    """Pitch the foot around its heel or toe on the plane under the sole."""
    x, lift, z, yaw, _ = foot
    leg_length, heel, toe, ankle = shape
    angle, direction = math.radians(pitch), math.radians(yaw)
    sin, cos = math.sin(angle), math.cos(angle)
    pivot = toe if pitch >= 0. else heel
    forward = (pivot * (1. - cos) + ankle * sin) / leg_length
    rise = (pivot * sin - ankle * (1. - cos)) / leg_length
    return x + forward * math.cos(direction), lift + rise, z + forward * math.sin(direction), yaw, pitch


def gait_foot(phase, sign, running, shape):
    # Constant backward stance speed follows the game's constant root speed.
    stance, stride, clearance = (.51, .34, .145) if running else (.61, .22, .086)
    heel = -9. if running else -8.
    toe = 21. if running else 16.
    if phase < stance:
        t = phase / stance
        x = stride * (1. - 2. * t)
        pitch = heel * (1. - ease(t, 0., .26)) + toe * ease(t, .67, 1.)
        lift = 0.
    else:
        t = (phase - stance) / (1. - stance)
        slope = 2. * stride * (1. - stance) / stance
        x = stride * (2. * ease(t, 0., 1.) - 1.) - slope * t * (1. - t) * (1. - 2. * t)
        pitch = toe * (1. - ease(t, 0., .36)) + heel * ease(t, .63, 1.)
        lift = clearance * math.sin(math.pi * t) ** 2
    return roll_contact((x, lift, .018 * sign, 7. * sign, 0.), pitch, shape)


def locomotion(form, family, index, count, running, shape):
    phase = index / count
    theta = math.tau * phase
    weight = math.sin(theta)
    stride = math.cos(theta)
    bounce = math.cos(2. * theta)
    form["feet"] = {
        "N": gait_foot(phase, 1, running, shape),
        "F": gait_foot((phase + .5) % 1., -1, running, shape),
    }
    form["root"][1] -= (.028 if running else .019) * (1. - bounce)
    form["root"][2] += (.041 if running else .035) * weight
    form["lean"] += 1.5 * bounce
    form["twist"] += (10. if running else 7.) * stride
    form["bend"] -= 3.1 * weight
    form["head_yaw"] = -.77 * form["twist"]
    form["head_bank"] = 2.4 * weight
    form["head"] -= 1.1 * bounce
    form["hair_follow"] = (.055 * math.sin(2. * theta - .45), -.12 * math.sin(theta - .5))
    form["collar"] = {"N": (-1.4 * stride, .58 * bounce, 0.), "F": (1.4 * stride, .58 * bounce, 0.)}
    amplitude = .38 if running else .23
    for side, sign in (("N", 1), ("F", -1)):
        swing = -sign * stride
        form["arms"][side] = (.12 + amplitude * swing, -.90 + .085 * abs(swing), .08)
    if form["weapon"]:
        hand = form["weapon"]["hand"]
        carried = {"pole": (.23, -.65, .11), "bow": (.14, -.77, .09),
                   "club": (.20, -.56, .12), "gun": (.20, -.61, .10)}
        if family in carried:
            x, y, z = carried[family]
            form["arms"][hand] = (x - .045 * stride, y + .031 * bounce, z)
        if family == "pole":
            # Bring the walking pole off the floor, inclined away from the face.
            form["weapon"]["dir"] = (.25 - .025 * bounce, .97, -.07)
        else:
            x, y, z = form["weapon"]["dir"]
            form["weapon"]["dir"] = (x + .05 * bounce, y, z + .032 * stride)


def bow_draw(form, kind, t, load, follow):
    # The form's head-relative goal is expressed in model units. The draw hand
    # travels towards the cheek, clears it on release, and drops to ready.
    reach = ease(t, .02, .52)
    release = ease(t, .53, .78)
    settle = ease(t, .77, 1.)
    loose = poses.lerp((16., -22., -1.), (6., -7., -7.), reach)
    loose = poses.lerp(loose, (-8., -5., -9.), release)
    form["arms"]["F"] = {"face": poses.lerp(loose, (16., -22., -1.), settle)}
    draw = reach * (1. - settle)
    form["arms"]["N"] = poses.lerp((.60, -.30, .05), (.92, -.035, .04), draw)
    high = -0.24 if kind == "atk_overhead" else 0.10
    form["weapon"]["dir"] = (poses.lerp((.12,), (high,), draw)[0] + .05 * follow, .99, -.065 * load)


def attack(form, kind, family, t, shape):
    yaw, sweep, push = ATTACK_WEIGHT[kind]
    load = pulse(t, .02, .25, .36, .58)
    contact = pulse(t, .31, .59, .64, .83)
    follow = pulse(t, .52, .76, .83, 1.)
    settle = pulse(t, .76, .90, .95, 1.)
    heavy = 1.22 if family == "club" else 1.
    if family in ("bow", "gun"):
        yaw *= .55
        sweep *= .45
        push *= .35
    form["root"][0] += heavy * (-.030 * load + push * contact + .014 * follow - .009 * settle)
    form["root"][1] -= heavy * (.026 * load + .035 * contact + .016 * follow)
    form["root"][2] += heavy * (.043 * load - .039 * contact - .022 * follow)
    form["lean"] += heavy * (-3.5 * load + 4.8 * contact + 2.1 * follow - 2.7 * settle)
    form["twist"] += heavy * (-yaw * load + .42 * sweep * contact + sweep * follow)
    form["bend"] += 4.1 * load - 4.6 * contact - 2.2 * follow
    form["head"] -= 3.2 * contact + 4.5 * follow
    form["head_yaw"] = -.66 * form["twist"]
    form["head_bank"] = -.67 * form["bend"]
    form["hair_follow"] = (-.16 * follow + .06 * settle, .16 * load - .24 * follow)
    form["collar"] = {"N": (-1.2 * load + 1.5 * contact, .6 * load, 0.),
                      "F": (-1.9 * load + 2.5 * contact + 1.3 * follow, 1.7 * load, 0.)}
    if family == "iai" and kind in ("atk_slash", "atk_draw"):
        # The normal draw stays low on its own stance. The dedicated Void
        # attack owns the traveling cut and its deeper silhouettes.
        form["feet"] = poses.COMBAT
        form["poles"] = {}
        form["root"][1] = -.03 - .095 * load - .13 * contact - .04 * follow
    form["feet"] = dict(form["feet"])
    heel = 0. if family in ("bow", "gun") else 12. * contact + 8. * follow
    form["feet"]["N"] = roll_contact(form["feet"]["N"], heel, shape)
    weapon = form["weapon"]
    if family == "bow":
        bow_draw(form, kind, t, load, follow)
    elif family == "gun":
        x, y, z = weapon["dir"]
        weapon["dir"] = (x, y + .19 * follow, z + .044 * follow)
        form["lean"] -= 6. * follow
        form["root"][0] -= .034 * follow
        form["collar"]["N"] = (-2.2 * follow, .9 * follow, 0.)
    elif weapon and family == "club":
        weapon["sep"] = -5.5 - 5.5 * load - 2.2 * contact
    elif weapon and family in ("blade", "short") and kind != "atk_thrust":
        weapon["roll"] = -7. * load + 15. * follow


def reaction(form, kind, t):
    if kind == "hurt":
        hit = poses.key(t, (.72, 1., .54, .22))
        form["root"][0] = -.08 * hit
        form["root"][1] -= .07 * hit
        form["root"][2] = -.053 * hit
        form["lean"], form["twist"], form["bend"] = -16. * hit, -8. * hit, 5. * hit
        form["head"] = -9. * hit + 4. * t
        form["head_yaw"] = 7. * hit
        form["hair_follow"] = (.15 * hit, -.12 * hit)
        form["collar"] = {"N": (-1.5 * hit, 2.2 * hit, 0.), "F": (-2.3 * hit, 1.2 * hit, 0.)}
    elif kind == "evade":
        shift = 1. - .56 * t
        form["root"][0], form["root"][2] = -.16 * shift, -.065 * shift
        form["root"][1] -= .055 * shift
        form["lean"], form["twist"], form["bend"] = -9. * shift, -10. * shift, 6. * shift
        form["head_yaw"] = 8. * shift
        form["head_bank"] = -3. * shift
        form["hair_follow"] = (.15 * shift, -.14 * shift)
    elif kind == "guard":
        brace = .70 + .30 * t
        form["root"][0], form["root"][2] = -.028 * brace, .022 * brace
        form["root"][1] -= .023 * brace
        form["lean"] += 6.5 * brace
        form["head"] = 5. * brace
        form["head_bank"] = -1.8 * brace
        form["collar"] = {"N": (1.1 * brace, 1.15 * brace, 0.), "F": (.8 * brace, 1.4 * brace, 0.)}


def controls(kind, index, count, family, foot_shape):
    t = index / max(1, count - 1)
    if kind.startswith("atk_"):
        if index in (0, count - 1):
            return poses.controls("ready", 0, 1, family)
        form = poses.controls(kind, index, count, family)
        attack(form, kind, family, t, foot_shape)
    else:
        form = poses.controls(kind, index, count, family)
        if kind in ("walk8", "run"):
            locomotion(form, family, index, count, kind == "run", foot_shape)
        elif kind in ("hurt", "guard", "evade"):
            reaction(form, kind, t)
    return form

