"""Install idle-motion banks and shared human fidget routing for native foes.

Run python tools/foe_fidgets.py after replacing or adding native foe assets.
Each bank keeps the installed combat skeleton. The five fidgets use 31 frames
at 20 fps, followed by a 97-frame continuous ready loop at 24 fps.
"""
import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import struct
from zlib import crc32

from blender.foe_batch import FAMILIES, plan, write
from motfile import load


RESOURCE = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool" / "project" / "resource"
FRAMES = 31
SOURCE_FAMILY = {name: family for family, entries in FAMILIES.items() for name in entries.split()}
HOVERING = {"boss_tsukakoro", "fire_elemental", "foe_nukekubi", "will_o_wisp"}
HALF_FIELDS = {"p": ">3e", "s": ">3e", "q": ">4e"}


@dataclass(frozen=True)
class Cue:
    pitch: float = 0
    yaw: float = 0
    roll: float = 0
    rise: float = 0
    mirror: bool = False
    one_side: bool = False


# Pitch is about engine Z, yaw about Y and roll about X. Distances are native
# model units. Cue keys identify the bones used to convey the gesture.
GESTURES = {
    "upright": (
        {"head": Cue(yaw=24, roll=8), "upper": Cue(yaw=4)},
        {"head": Cue(pitch=15, yaw=7), "arm": Cue(pitch=22, roll=10, one_side=True)},
        {"head": Cue(pitch=-9), "upper": Cue(pitch=-3, rise=1), "arm": Cue(roll=8, mirror=True)},
        {"head": Cue(yaw=13, roll=-12), "arm": Cue(pitch=-17, roll=18, one_side=True),
         "tail": Cue(yaw=12, mirror=True)},
        {"head": Cue(pitch=-18, roll=5), "upper": Cue(pitch=5),
         "arm": Cue(pitch=9, yaw=7, mirror=True), "tail": Cue(roll=7)},
    ),
    "beast": (
        {"head": Cue(yaw=22, roll=7), "tail": Cue(yaw=-12)},
        {"head": Cue(pitch=-16, yaw=6), "foreleg": Cue(pitch=8, rise=1.4, one_side=True)},
        {"head": Cue(pitch=12, roll=9), "upper": Cue(pitch=3, rise=1.2), "tail": Cue(roll=11)},
        {"head": Cue(roll=-12), "tail": Cue(yaw=24, roll=8),
         "foreleg": Cue(roll=5, rise=0.7, one_side=True)},
        {"head": Cue(pitch=20, yaw=-9), "upper": Cue(pitch=-4), "tail": Cue(yaw=-10, roll=-9)},
    ),
    "crawler": (
        {"head": Cue(yaw=19), "arm": Cue(yaw=-13, pitch=9, one_side=True),
         "upper": Cue(yaw=6)},
        {"arm": Cue(roll=17, pitch=11, mirror=True), "foreleg": Cue(roll=8, rise=1.1, one_side=True)},
        {"upper": Cue(pitch=-5, rise=0.8), "head": Cue(pitch=13),
         "foreleg": Cue(pitch=9, rise=0.7, one_side=True)},
        {"foreleg": Cue(roll=-9, yaw=8, rise=1.8, one_side=True),
         "rearleg": Cue(roll=4, yaw=-4, mirror=True), "tail": Cue(yaw=14)},
        {"upper": Cue(roll=6, rise=0.6), "head": Cue(roll=-9),
         "arm": Cue(pitch=-13, yaw=8, mirror=True), "foreleg": Cue(pitch=-7, one_side=True)},
    ),
    "water": (
        {"head": Cue(yaw=17), "upper": Cue(yaw=4), "tail": Cue(yaw=-17)},
        {"head": Cue(pitch=9), "arm": Cue(roll=14, pitch=10, mirror=True),
         "tail": Cue(pitch=10)},
        {"air": Cue(rise=1.7, pitch=-5), "head": Cue(pitch=-12), "tail": Cue(pitch=-12)},
        {"head": Cue(roll=10), "arm": Cue(pitch=-16, roll=-10, one_side=True),
         "tail": Cue(yaw=24, roll=6)},
        {"head": Cue(pitch=14, yaw=-12), "upper": Cue(yaw=-6), "tail": Cue(yaw=-14, pitch=9)},
    ),
    "winged": (
        {"head": Cue(yaw=22, roll=9), "wing": Cue(roll=12, mirror=True)},
        {"wing": Cue(roll=18, yaw=8, mirror=True), "tail": Cue(pitch=-11),
         "head": Cue(pitch=-8)},
        {"air": Cue(rise=2.7, pitch=6), "head": Cue(pitch=12), "wing": Cue(roll=-17, mirror=True)},
        {"air": Cue(roll=7), "head": Cue(roll=-12), "wing": Cue(roll=16, yaw=8, one_side=True)},
        {"wing": Cue(roll=14, pitch=-7, mirror=True), "head": Cue(yaw=-16, pitch=-13),
         "tail": Cue(yaw=-13), "air": Cue(rise=1.5, pitch=-4)},
    ),
    "plant": (
        {"head": Cue(yaw=24, roll=10), "upper": Cue(roll=4), "arm": Cue(roll=-7, mirror=True)},
        {"arm": Cue(roll=18, pitch=-8, mirror=True), "head": Cue(pitch=10)},
        {"upper": Cue(rise=1.2, pitch=-8), "head": Cue(pitch=-15), "tail": Cue(roll=12, mirror=True)},
        {"arm": Cue(yaw=18, roll=21, one_side=True), "head": Cue(roll=-14), "upper": Cue(roll=7)},
        {"head": Cue(pitch=18, yaw=9), "arm": Cue(roll=-14, pitch=11, mirror=True),
         "tail": Cue(yaw=-15, mirror=True)},
    ),
    "spectral": (
        {"head": Cue(yaw=24, roll=12), "air": Cue(yaw=5), "tail": Cue(yaw=-12)},
        {"head": Cue(pitch=-15), "arm": Cue(roll=16, pitch=10, mirror=True),
         "tail": Cue(pitch=14)},
        {"air": Cue(rise=2.3, pitch=6), "head": Cue(pitch=16), "tail": Cue(roll=11)},
        {"head": Cue(roll=-17), "air": Cue(roll=6), "arm": Cue(roll=-18, yaw=14, one_side=True),
         "tail": Cue(yaw=19, roll=7)},
        {"air": Cue(rise=1.1, yaw=-6), "head": Cue(pitch=17, yaw=-12),
         "tail": Cue(roll=-10, pitch=-15), "arm": Cue(pitch=-10, roll=-9, mirror=True)},
    ),
    "object": (
        {"object": Cue(yaw=4), "head": Cue(yaw=12)},
        {"object": Cue(roll=3), "head": Cue(roll=10)},
        {"object": Cue(pitch=-3, rise=0.6), "head": Cue(pitch=-9, rise=0.8)},
        {"object": Cue(yaw=-6, roll=-1), "head": Cue(yaw=-14, roll=-6)},
        {"object": Cue(pitch=4, roll=2, rise=0.4), "head": Cue(pitch=12, roll=4)},
    ),
}
FAMILY_GESTURES = {
    "crab": "crawler", "crawler": "crawler", "flier": "winged", "naga": "water",
    "plant": "plant", "serpent": "water", "spirit": "spectral", "swimmer": "water",
    "relic": "object",
}


def roles_for(name):
    if name == "root":
        return ("upper", "air", "object")
    if name in {"head", "light", "rider_head", "curl"} or name.startswith("neck"):
        return ("upper", "head") if name == "head" else ("head", "tail")
    if name.startswith(("leg", "front_leg", "rear_leg")):
        if name.startswith("rear") or ("_" in name and name.rsplit("_", 1)[-1] in {"2", "3", "4"}):
            return ("rearleg",)
        return ("foreleg",)
    if name.startswith("wing"):
        return ("upper", "wing")
    if name.startswith(("arm", "claw", "branch", "fin", "leaf", "lower_arm", "vine", "sleeve", "fold")):
        return ("upper", "arm")
    if name == "rider":
        return ("upper",)
    return ("tail",)


def group_for(source, names):
    family = SOURCE_FAMILY.get(source)
    if family is None:
        raise ValueError(f"Missing anatomy classification for {source}")
    if any(name.startswith("front_leg") for name in names):
        return "beast"
    if any(name.startswith("wing") for name in names):
        return "winged"
    if family == "crawler" and not any(name.startswith("leg") for name in names):
        return "water"
    if source == "boss_tsukakoro":
        return "object"
    return FAMILY_GESTURES.get(family, "upright")


def pulse(t, variation, delay=0):
    t = max(0, (t - delay) / (1 - delay))
    envelope = math.sin(math.pi * t) ** 2
    # Hold, quick double motion, rising stretch, shake, and slow release.
    return envelope * (
        1,
        0.64 + 0.36 * math.cos(math.tau * (2 * t - 0.17)),
        0.25 + t,
        math.sin(math.tau * (t + 0.14)),
        1.37 - 0.7 * t,
    )[variation]


def product(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
    )


def rotation(pitch, yaw, roll):
    p, y, r = (math.radians(v) / 2 for v in (pitch, yaw, roll))
    return product(
        (math.cos(y), 0, math.sin(y), 0),
        product((math.cos(p), 0, 0, math.sin(p)), (math.cos(r), math.sin(r), 0, 0)),
    )


def rotate(q, point):
    return product(product(q, (0, *point)), (q[0], -q[1], -q[2], -q[3]))[1:]


def side_and_delay(name):
    side_match = re.search(r"(-?1)(?:_\d+)?$", name)
    side = int(side_match[1]) if side_match else 0
    # Trailing numbers on a single tail describe segments, not mirrored sides.
    if re.fullmatch(r"(?:tail|tongue)\d+", name):
        return 0, min(0.16, int(name[-1]) * 0.035)
    if "_" in name and name.rsplit("_", 1)[-1].isdigit():
        return side, min(0.14, int(name.rsplit("_", 1)[-1]) * 0.035)
    return side, 0


def pose_track(part, base, root, group, source, intensity, preferred_side):
    name = part["name"]
    roles = roles_for(name)
    side, delay = side_and_delay(name)
    fly = source in HOVERING or group == "spectral" or SOURCE_FAMILY[source] in {"flier", "swimmer"}
    for variation, gesture in enumerate(GESTURES[group]):
        for frame in range(FRAMES):
            if frame in (0, FRAMES - 1):
                yield base
                continue
            t = frame / (FRAMES - 1)
            local = [0., 0., 0., 0.]
            body = [0., 0., 0., 0.]
            for role in roles:
                if role == "air" and not fly:
                    continue
                cue = gesture.get(role)
                if not cue or cue.one_side and side != preferred_side:
                    continue
                # The upper body moves around its origin while ground contact
                # bones keep their source pose. Hovering rigs move together.
                total = body if role in {"upper", "air", "object"} else local
                scale = intensity * pulse(t, variation, delay if role == "tail" else 0)
                sign = side if cue.mirror and side else preferred_side
                for i, value in enumerate((cue.pitch, cue.yaw * sign, cue.roll * sign, cue.rise)):
                    total[i] += value * scale
            if fly and name != "root":
                cue = gesture.get("air")
                if cue:
                    scale = intensity * pulse(t, variation)
                    for i, value in enumerate((cue.pitch, cue.yaw * preferred_side,
                                               cue.roll * preferred_side, cue.rise)):
                        body[i] += value * scale
            if not any((*local, *body)):
                yield base
                continue
            pivot = root
            if group == "object":
                # Grounded props rock around their base. The floating cage
                # keeps its original centre of rotation.
                if fly:
                    body[3] += abs(body[0] + body[1] + body[2]) * 0.28
                else:
                    pivot = (root[0], 0, root[2])
            orbit = rotation(*body[:3])
            relative = tuple(value - origin for value, origin in zip(base["p"], pivot))
            position = tuple(value + origin for value, origin in zip(rotate(orbit, relative), pivot))
            move = product(orbit, rotation(*local[:3]))
            yield {
                "p": (position[0], position[1] + local[3] + body[3], position[2]),
                "s": base["s"],
                "q": product(move, base["q"]),
            }


def ready_track(part, base, root, group, source, intensity):
    """A continuous low-amplitude movement with ground contacts held in place."""
    roles = roles_for(part["name"])
    airborne = source in HOVERING or group in {"spectral", "water"} or SOURCE_FAMILY[source] == "flier"
    for i in range(97):
        theta = math.tau * (i % 96) / 96.
        sway = math.sin(theta) * intensity
        breath = (1. - math.cos(theta * 2.)) * .5 * intensity
        if airborne:
            angles = (.8*breath, 1.7*sway, 1.2*sway)
            rise = 1.35*sway
        elif any(role in roles for role in ("upper", "head", "tail", "object")):
            multiplier = 1.4 if "head" in roles or "tail" in roles else 1.
            angles = (1.5*breath, 1.9*sway*multiplier, 1.25*sway)
            rise = .68*breath
        else:
            yield base
            continue
        q = rotation(*angles)
        pivot = (root[0], 0, root[2]) if group == "object" and not airborne else root
        relative = tuple(value - origin for value, origin in zip(base["p"], pivot))
        x, y, z = (value + origin for value, origin in zip(rotate(q, relative), pivot))
        yield {"p": (x, y + rise, z), "s": base["s"], "q": product(q, base["q"])}


def motion_bytes(parts, tracks):
    """Write the engine's SMOT v0 layout with the original bind metadata."""
    data = bytearray(b"SMOT" + struct.pack(">BB", 0, len(parts)))
    for part, track in zip(parts, tracks, strict=True):
        name = part["name"].encode("latin-1")
        pivot = part["pivot"]
        data.extend(struct.pack(">H", len(name)) + name)
        data.extend(struct.pack(">BBB", part["id"], part["parent"] + 1, pivot is not None))
        if pivot is not None:
            data.extend(struct.pack(">3f", *pivot))
        data.extend(struct.pack(">17f", *part["bind"].flat, part["length"]))
        data.extend(struct.pack(">HH", 0, len(track) - 1))
        prev = {}
        for key in track:
            fields = {field: struct.pack(fmt, *key[field]) for field, fmt in HALF_FIELDS.items()}
            flag = sum(1 << i for i, field in enumerate(fields) if fields[field] == prev.get(field))
            data.append(flag)
            for field, value in fields.items():
                if prev.get(field) != value:
                    data.extend(value)
            prev = fields
        data.extend(b"\0" * 4)
    return data + b"\0\0"


def build(resource, output):
    installed = resource / "native_foe"
    index = json.loads((installed / "index.json").read_text(encoding="utf-8-sig"))
    pictures = json.loads((resource / "enemy_pic.json").read_text(encoding="utf-8-sig"))
    output.mkdir(parents=True, exist_ok=True)
    counts = defaultdict(int)
    jobs = plan()
    humans = {}
    for key, spec in index.items():
        if spec.get("human"):
            if jobs[key]["recipe"] != "human":
                raise ValueError(f"{key} has conflicting human/creature classifications")
            humans[key] = jobs[key]["family"]
            continue
        motion = load(installed / f"{key}.mot")
        parts = motion["parts"]
        if motion["customs"] or any(part["parent"] >= 0 for part in parts):
            raise ValueError(f"{key} needs a fidget exporter for a hierarchical or custom rig")
        stand = next(clip["st"] for clip in spec["animap"] if clip["id"] == "stand")
        fight = next(clip["st"] for clip in spec["animap"] if clip["id"] == "fight")
        base = {part["name"]: part["keys"][stand - part["start"]] for part in parts}
        if any(base[part["name"]] != part["keys"][fight - part["start"]] for part in parts):
            raise ValueError(f"{key} needs different endpoints for its stand and fight fidgets")
        root = base["root"]["p"]
        source = Path(pictures[key]["pic3d"]).stem
        group = group_for(source, base.keys())
        seed = crc32(source.encode("ascii"))
        intensity = 0.9 + (seed % 21) / 100
        preferred_side = 1 if seed & 1 else -1
        tracks = [
            [*pose_track(part, base[part["name"]], root, group, source, intensity, preferred_side),
             *ready_track(part, base[part["name"]], root, group, source, intensity)]
            for part in parts
        ]
        destination = output / f"{key}.mot"
        temporary = destination.with_suffix(".tmp")
        temporary.write_bytes(motion_bytes(parts, tracks))
        temporary.replace(destination)
        counts[group] += 1
    fidgets = resource / "native_chara" / "fidget"
    if any(not (fidgets / f"{family}.mot").is_file() for family in set(humans.values())):
        raise ValueError("Build humanoid banks with tools/blender/combat_fidgets.py first")
    write(output / "index.json", humans)
    print(f"Generated {sum(counts.values())} foe motion banks with five gestures and a ready loop ({dict(counts)})")
    print(f"Routed {len(humans)} native human foes to shared weapon-family fidgets")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", type=Path, default=RESOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build(args.resource, args.output or args.resource / "native_foe" / "fidget")

