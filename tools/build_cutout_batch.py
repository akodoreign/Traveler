"""Extract reusable roster parts from the drawn atlases and author each character's rig profile."""
import argparse
import copy
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

import rig3d as cutout
import gen_sprites2d as sprites

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "_art" / "sources" / "cutout"
BATCH = ("gendo", "shizue", "haruki", "mitsue", "tamotsu", "sayo", "yosai")
FOOT_ORDER = ("natsuko", "rensei", *BATCH)
# Output-pixel proportions that differ from the defaults: a bald head carries no hair volume, and bare arms
# need their shoulder inside the torso outline, not on its back edge.
BUILD = {"yosai": dict(head=27, torso=44, arm=36, leg=56, pin=.13, far=.88, drop=-.08, neck=.8)}
SOLO = {"yosai": "side_yosai_parts.png"}     # one character redrawn for the frame: rows are cores, limbs, feet


def atlas_parts(path, column_count=6, row_count=len(BATCH)):
    with Image.open(path) as source:
        pixels = np.array(source.convert("RGBA"))
    count, labels, stats, centers = cv2.connectedComponentsWithStats(
        (pixels[..., 3] >= 128).astype(np.uint8), 8)
    columns = [[] for _ in range(column_count)]
    for label in range(1, count):
        x, y, width, height, area = stats[label]
        if area < 700:
            continue
        column = int(centers[label][0] / (pixels.shape[1] / column_count))
        cropped = pixels[y:y + height, x:x + width].copy()
        selected = labels[y:y + height, x:x + width] == label
        cropped[~selected] = 0
        cropped[selected, 3] = 255
        columns[column].append((float(centers[label][1]), Image.fromarray(cropped)))
    if any(len(column) != row_count for column in columns):
        raise ValueError(f"{path.name}: expected {row_count} complete parts in each of {column_count} columns")
    return [[image for _, image in sorted(column, key=lambda item: item[0])] for column in columns]


def joint(image, fraction):
    alpha = np.asarray(image)[..., 3]
    y = min(image.height - 1, round((image.height - 1) * fraction))
    xs = np.flatnonzero(alpha[y] >= 128)
    if not len(xs):
        raise ValueError(f"Missing joint cross-section at {fraction}")
    return [float((xs[0] + xs[-1]) / 2), float(y)]


def draw_gear(spec, state):
    names = ("FW", "FH", "XX", "YY", "WEAPON_SCALE")
    original = {name: getattr(sprites, name) for name in names}
    try:
        sprites.FW = sprites.FH = 208
        sprites.YY, sprites.XX = np.mgrid[:208, :208]
        sprites.WEAPON_SCALE = 2.2 * original["WEAPON_SCALE"]
        canvas = sprites.Canvas()
        sprites.draw_weapon(canvas, spec, {"ha_f": (96, 96), "ha_b": (63, 96), "wang": 0, "bow": state},
                            sprites.palette(spec))
        return Image.fromarray(canvas.col)
    finally:
        for name, value in original.items():
            setattr(sprites, name, value)


def add_feet(profile, key, feet):
    row = FOOT_ORDER.index(key)
    directory = SOURCE / (("side_" if key == "yosai" else "trav_") + key)
    directory.mkdir(parents=True, exist_ok=True)
    for column, view in enumerate(("camera", "heel")):
        image = feet[column][row]
        path = directory / f"foot_{view}.png"
        image.save(path)
        anchor = joint(image, .36)
        for side in ("f", "b"):
            original = profile["parts"][f"foot_{side}"]
            with Image.open(ROOT / original["image"]) as source:
                source = source.convert("RGBA")
                if "box" in original:
                    source = source.crop(original["box"])
                ys = np.nonzero(np.asarray(source)[..., 3] >= 128)[0]
            floor = (int(ys.max()) - original["anchor"][1]) * original["scale"]
            profile["parts"][f"foot_{side}_{view}"] = {
                "image": path.relative_to(ROOT).as_posix(), "anchor": anchor,
                "scale": floor / (image.height - 1 - anchor[1]), "mirror_x": side == "f",
            }


def prepare(key, cores, limbs, feet):
    if key not in BATCH:
        basename = "trav_" + key
        path = cutout.PROFILES / f"{basename}.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        add_feet(profile, key, feet)
        path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        return basename
    row = BATCH.index(key)
    roster = {spec["key"]: spec for spec in sprites.TRAVELERS}
    spec = roster.get(key)
    if spec is None:
        from gen_sidecast import CAST
        spec = next(character for character in CAST if character["key"] == key)
    weapon = "none" if key == "yosai" else spec["weapon"]
    basename = ("side_" if key == "yosai" else "trav_") + key
    directory = SOURCE / basename
    directory.mkdir(parents=True, exist_ok=True)
    parts, nodes, views = {}, {}, {}

    def save(name, image, anchor, scale, sockets=None):
        path = directory / f"{name}.png"
        image.save(path)
        parts[name] = dict(image=path.relative_to(ROOT).as_posix(), anchor=anchor, scale=scale)
        if sockets:
            parts[name]["sockets"] = sockets

    for column, view in enumerate(("", "_front", "_back")):
        body = cores[column + 3][row]
        if not view and key not in SOLO:           # the shared atlas torsos face left; the sheets face right
            body = body.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        height = BUILD.get(key, {}).get("torso", 40 if key not in ("haruki", "sayo") else 38)
        scale = height / body.height
        width, depth = body.size
        hip = [width * .5, depth * .86]
        sockets = {
            "root": hip, "neck": joint(body, .04),
            "shoulder_f": [width * (BUILD.get(key, {}).get("pin", .13) if not view else .17),
                           depth * (.3 + BUILD.get(key, {}).get("drop", 0))],
            "shoulder_b": [width * (BUILD.get(key, {}).get("far", .84) if not view else .83),
                           depth * (.27 + BUILD.get(key, {}).get("drop", 0))],
            "hip_f": [width * .65, hip[1]], "hip_b": [width * .35, hip[1]],
            "saya": [width * .67, hip[1] - 4],
        }
        save("body" + view, body, hip, scale, sockets)
        head = cores[column][row]
        neck_y = .81 if key in ("mitsue", "sayo") else .90
        neck = joint(head, BUILD[key]["neck"]) if key in BUILD else [head.width * (.55 if not view else .5), head.height * neck_y]
        save("head" + view, head, neck,
             BUILD.get(key, {}).get("head", 31) / head.height, {"crown": [head.width * .5, head.height * .22]})
        waist = np.array(body)
        waist[:round(depth * .69)] = 0
        save("waist" + view, Image.fromarray(waist), hip, scale)
    for column, name in enumerate(("arm_front_left", "arm_front_right", "arm_back_left", "arm_back_right")):
        arm = limbs[column][row]
        shoulder, elbow, wrist, grip = (joint(arm, fraction) for fraction in (.09, .49, .81, .92))
        length = np.linalg.norm(np.array(elbow) - shoulder) + np.linalg.norm(np.array(wrist) - elbow)
        save(name, arm, shoulder, BUILD.get(key, {}).get("arm", 31) / length,
             {"elbow": elbow, "wrist": wrist, "grip": grip})
    for column, side in ((4, "b"), (5, "f")):
        leg = limbs[column][row]
        if side == "f":
            leg = leg.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        hip, knee, ankle = (joint(leg, fraction) for fraction in (.06, .46, .85))
        length = np.linalg.norm(np.array(knee) - hip) + np.linalg.norm(np.array(ankle) - knee)
        scale = BUILD.get(key, {}).get("leg", 50 if key == "gendo" else 48) / length
        pixels = np.array(leg)
        ys = np.arange(leg.height)[:, None]
        overlap = 2 / scale
        for segment, anchor, mask, sockets in (
            ("thigh", hip, ys <= knee[1] + overlap, {"knee": knee}),
            ("shin", knee, (ys >= knee[1] - overlap) & (ys <= ankle[1] + overlap), {"ankle": ankle}),
            ("foot", ankle, ys >= ankle[1] - overlap, None),
        ):
            piece = pixels.copy()
            piece[~np.broadcast_to(mask, piece.shape[:2])] = 0
            save(f"{segment}_{side}", Image.fromarray(piece), anchor, scale, sockets)
    parts["foot_b_outward"] = {"source_part": "foot_b", "mirror_x": True}
    nodes.update(
        hips=dict(part="body", visible=False),
        body=dict(part="body", parent="hips", socket="root", depth=30),
        waist=dict(part="waist", parent="hips", socket="root", depth=24),
        head=dict(part="head", parent="body", socket="neck", depth=35),
    )
    for side, arm, depth in (("b", "arm_front_right", 10), ("f", "arm_front_left", 20)):
        nodes[f"thigh_{side}"] = dict(part=f"thigh_{side}", parent="hips", socket=f"hip_{side}", depth=depth)
        nodes[f"shin_{side}"] = dict(part=f"shin_{side}", parent=f"thigh_{side}", socket="knee", depth=depth + 1)
        nodes[f"foot_{side}"] = dict(part=f"foot_{side}", parent=f"shin_{side}", socket="ankle", depth=depth - 1)
        nodes[f"arm_{side}"] = dict(part=arm, parent="body", socket=f"shoulder_{side}",
                                   depth=40 if side == "f" else 25)
    for view in ("front", "back"):
        views[view] = {
            "hips": {"part": "body_" + view}, "body": {"part": "body_" + view},
            "head": {"part": "head_" + view}, "weapon": {"visible": False},
            "arm_f": {"part": f"arm_{view}_left"},
            "arm_b": {"part": f"arm_{view}_right", "depth": 40},
        }
    if weapon == "katana":
        source = json.loads((cutout.PROFILES / "trav_rensei.json").read_text(encoding="utf-8"))
        for name in ("weapon", "weapon_hilt", "saya"):
            parts[name] = copy.deepcopy(source["parts"][name])
        nodes["saya"] = copy.deepcopy(source["nodes"]["saya"])
        nodes["hilt"] = copy.deepcopy(source["nodes"]["hilt"])
    else:
        gear = dict(spec, weapon="bo" if weapon == "none" else weapon, eye=spec.get("eye", (90, 70, 50)))
        for state in (("rest", "draw") if weapon == "yumi" else ("rest",)):
            anchor = [99, 96] if weapon == "yumi" else [96, 96]
            tip = [99, 76] if weapon == "yumi" else [96.6, 105] if weapon == "tanto" else [116, 96]
            save("weapon_draw" if state == "draw" else "weapon", draw_gear(gear, state),
                 anchor, 1, {"tip": tip, "string": [63, 96]})
    nodes["weapon"] = dict(part="weapon", parent="arm_f", socket="grip", depth=39, visible=weapon != "none")
    if key == "sayo":
        hat = Image.new("RGBA", (60, 30))
        draw = ImageDraw.Draw(hat)
        draw.polygon(((2, 24), (28, 2), (57, 24)), fill="#b89759", outline="#342b22")
        for x in range(7, 56, 5):
            draw.line(((28, 4), (x, 23)), fill="#80633e", width=1)
        draw.line(((3, 24), (56, 24)), fill="#e1c98b", width=2)
        save("hat", hat, [30, 22], .55)
        nodes["hat"] = dict(part="hat", parent="head", socket="crown", depth=36)
    motion = "atk_thrust" if weapon in ("bo", "shakujo") else "atk_slash"
    clips = {
        "critical": {"motion": motion, "count": 6, "speed": 12},
        "void_critical": {"motion": "atk_draw" if weapon == "none" else motion, "count": 8, "speed": 8},
    }
    profile = dict(size=[208, 208], origin=[96, 128], weapon=weapon, articulated_arms=True,
                   parts=parts, nodes=nodes, views=views, clips=clips)
    add_feet(profile, key, feet)
    (cutout.PROFILES / f"{basename}.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return basename


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="*", choices=FOOT_ORDER)
    args = parser.parse_args()
    cores = atlas_parts(SOURCE / "roster_cores.png")
    limbs = atlas_parts(SOURCE / "roster_limbs.png")
    feet = atlas_parts(SOURCE / "roster_feet.png", 2, len(FOOT_ORDER))
    for key in args.keys or BATCH:
        if key in SOLO:
            grid = atlas_parts(SOURCE / SOLO[key], 6, 3)
            pad, foot_pad = [None] * BATCH.index(key), [None] * FOOT_ORDER.index(key)
            parts = ([pad + [column[0]] for column in grid], [pad + [column[1]] for column in grid],
                     [foot_pad + [column[2]] for column in grid[:2]])
        else:
            parts = (cores, limbs, feet)
        print(f"{prepare(key, *parts)}: reusable parts and profile prepared")


if __name__ == "__main__":
    main()
