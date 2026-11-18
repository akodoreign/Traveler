"""Character choreography layered over weapon-specific presentation poses."""
from hashlib import blake2s
import math

import rig3d_poses as p

FRAMES = 28
SPEED = 14

# Phase count, footwork, height, body turn, and free-hand finish.
TRAVELERS = {
    "trav_natsuko": (2, .13, .08, 14, "rally"),
    "trav_rensei": (1, .065, .027, 23, "bow"),
    "trav_gendo": (2, .12, .041, 9, "stomp"),
    "trav_shizue": (3, .15, .063, 28, "rally"),
    "trav_haruki": (3, .13, .16, 17, "wave"),
    "trav_mitsue": (2, .19, .055, 40, "turn"),
    "trav_tamotsu": (1, .21, .072, 31, "wave"),
    "trav_sayo": (3, .17, .16, 33, "turn"),
}
FINISHES = ("rally", "bow", "stomp", "wave", "turn")

# Grip hand, presentation target (forward/up/outward), and the direction of the weapon.
DISPLAY = {
    "katana": ("F", (.48, .59, .39), (.28, .92, -.14)),
    "kakita": ("F", (.36, .42, .55), (.14, .98, -.08)),
    "nodachi": ("F", (.65, .28, .31), (.61, .64, -.36)),
    "bokken": ("F", (.76, .39, .30), (.55, .61, -.49)),
    "tanto": ("F", (.60, .21, .52), (.62, .61, -.48)),
    "kama": ("F", (.54, .61, .39), (.43, .78, -.26)),
    "nunchaku": ("F", (.61, .51, .50), (.59, .45, -.56)),
    "fan": ("F", (.44, .71, .39), (.44, .81, -.30)),
    "yari": ("N", (.21, .17, .72), (.06, .98, .13)),
    "naginata": ("N", (.14, .27, .76), (.35, .91, .21)),
    "bo": ("N", (.49, .15, .61), (.08, .91, .39)),
    "shakujo": ("N", (.27, .23, .70), (.15, .97, .14)),
    "yumi": ("N", (.31, .49, .69), (.33, .88, .27)),
    "tetsubo": ("N", (.35, .31, .60), (.29, .83, .43)),
    "musket": ("N", (.38, -.08, .59), (.19, .95, .24)),
}


def controls(character, weapon, family, frame):
    """Loop through a step, weapon flourish, and character-specific finish."""
    seed = blake2s(character.encode(), digest_size=8).digest()
    beats, step, lift, turn, finish = TRAVELERS.get(character, (
        1 + seed[0] % 3, .078 + seed[1] / 2048, .036 + seed[2] / 2400,
        12 + seed[3] / 9, FINISHES[seed[4] % len(FINISHES)],
    ))
    u = frame / FRAMES
    pose = p.controls("idle8", 0, 1, family)
    angle = math.tau * u
    rhythm = math.tau * (beats * u + seed[5] / 1536)
    swing, down = math.sin(rhythm), math.cos(rhythm)
    envelope = math.sin(math.pi * u) ** 2
    lead = 1 if seed[6] & 1 else -1
    pivot = math.sin(angle + seed[7] / 190) * envelope
    pose["root"] = [step * .28 * swing * envelope, (-.02 - .061 * max(0, down)) * envelope,
                    step * .53 * pivot * lead]
    pose["twist"] = turn * pivot * lead
    pose["bend"] = 8 * swing * envelope * lead
    pose["lean"] = (-5 + 10 * max(0, down)) * envelope
    pose["head"] = -6 * swing * envelope
    for side, sign in (("N", 1), ("F", -1)):
        x, _, z, yaw, _ = p.STAND[side]
        stride = max(0., sign * swing * lead)
        pose["feet"] = pose["feet"] | {
            side: (x + sign * step * stride * envelope, lift * stride * envelope,
                   z + sign * step * .58 * stride * envelope,
                   yaw + sign * turn * .75 * pivot, -17 * stride * envelope)
        }

    # Both hands can join the rhythm when unarmed or wearing hand weapons.
    if weapon not in DISPLAY:
        pose["arms"] = dict(N=(.37, .28 + .48 * swing, .3),
                            F=(.43, .24 - .42 * swing, .38))
    else:
        hand, target, direction = DISPLAY[weapon]
        free = "F" if hand == "N" else "N"
        pole = weapon in ("yari", "naginata", "bo", "shakujo")
        base = (.25, -.26, .63) if pole else (.43, -.31, .34)
        salute = .55 + .45 * envelope
        pose["arms"][hand] = p.lerp(base, target, salute)
        pose["arms"][free] = (.38, .15 + .42 * swing, .36)
        x, y, z = direction
        direction = (x + (.13 if pole else .26) * pivot,
                     y + .15 * swing * envelope, z + .28 * swing * envelope)
        pose["weapon"] = dict(hand=hand, dir=direction, shift=0)
        if weapon == "tetsubo":
            pose["weapon"]["sep"] = -8.5
        if weapon == "musket":
            pose["weapon"]["sep"] = 7.5
        if weapon == "yumi":
            pose["weapon"]["roll"] = 69 + 16 * swing * envelope

    free = "N" if weapon not in DISPLAY or DISPLAY[weapon][0] == "F" else "F"
    if finish == "bow":
        pose["lean"] += 26 * max(0., -math.sin(angle)) ** 3
        pose["head"] += 10 * max(0., -math.sin(angle))
        pose["arms"][free] = (.27, -.63 + .34 * envelope, -.31)
    elif finish == "stomp":
        pose["lean"] += 7 * abs(swing) * envelope
        pose["root"][1] -= .05 * max(0., swing) ** 3 * envelope
        pose["arms"][free] = (.40, .20 + .24 * swing, .19)
    elif finish == "rally":
        pose["arms"][free] = (.21, .39 + .48 * envelope, .34 + .15 * swing)
    elif finish == "wave":
        pose["arms"][free] = (.43, .46 + .32 * swing, .37 + .22 * down)
    else:
        pose["twist"] += 17 * pivot
        pose["arms"][free] = (.53, .13 + .47 * envelope, .33 - .34 * swing)
    return pose
