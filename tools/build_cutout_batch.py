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
# Later batches: seven cast keys per pair of atlases (<name>_cores.png, <name>_limbs.png), in atlas row order.
BATCH_FILE = ROOT / "tools" / "cutout_batches.json"
BATCHES = json.loads(BATCH_FILE.read_text(encoding="utf-8"))
PLACE = {}                                   # key -> atlas row, borrowed foot row and sheet basename


def footwear(spec):
    """Row of roster_feet.png whose camera-facing feet suit this character."""
    if spec.get("build") == "monk":
        return 8
    if spec.get("clan") in ("peasant", "eta", "ronin", "mantis") or spec.get("build") == "peasant":
        return 7
    return 5 if spec.get("clan") == "scorpion" else 2


def atlas_parts(path, column_count=6, row_count=len(BATCH)):
    with Image.open(path) as source:
        pixels = np.array(source.convert("RGBA"))
    if (pixels[..., 3] < 128).mean() < .2:     # no real transparency: key out the flat painted backdrop
        rgb = pixels[..., :3].astype(int)
        edge = np.concatenate((rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]))
        backdrop = np.median(edge, axis=0)
        off = np.abs(rgb - backdrop).max(axis=-1)
        if backdrop.max() - backdrop.min() > 100:   # a saturated key colour is never part of the art: enclosed gaps too
            pixels[off <= 60] = 0
        _, labels = cv2.connectedComponents((off <= 30).astype(np.uint8), connectivity=4)
        border = np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1])))
        pixels[np.isin(labels, border[border > 0])] = 0
        for _ in range(2):                      # the blended fringe between backdrop and outline
            ragged = cv2.dilate((pixels[..., 3] == 0).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            pixels[ragged & (off <= 90)] = 0
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
    import rig3d_gear
    return rig3d_gear.draw_weapon(spec, state)


def add_feet(profile, key, feet):
    row = PLACE[key]["foot"] if key in PLACE else FOOT_ORDER.index(key)
    directory = SOURCE / (PLACE[key]["basename"] if key in PLACE else ("side_" if key == "yosai" else "trav_") + key)
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


def stubs(body):
    """Centres of the mannequin's bare arm sockets (drawn in the neck stub's colour) on each side of a torso."""
    pixels = np.asarray(body).astype(int)
    opaque = pixels[..., 3] >= 128
    top = pixels[:max(2, body.height // 20)][opaque[:max(2, body.height // 20)]][:, :3]
    like = opaque & (np.abs(pixels[..., :3] - np.median(top, axis=0)).sum(axis=-1) < 60)
    like[:body.height // 10] = like[body.height * 6 // 10:] = False
    found = []
    for columns in (slice(0, body.width * 3 // 10), slice(body.width * 7 // 10, None)):
        ys, xs = np.nonzero(like[:, columns])
        found.append([float(xs.mean() + (columns.start or 0)), float(ys.mean())] if len(xs) >= 20 else None)
    return found


def prepare(key, cores, limbs, feet):
    if key not in BATCH and key not in PLACE:
        basename = "trav_" + key
        path = cutout.PROFILES / f"{basename}.json"
        profile = json.loads(path.read_text(encoding="utf-8"))
        add_feet(profile, key, feet)
        path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
        return basename
    row = PLACE[key]["row"] if key in PLACE else BATCH.index(key)
    roster = {spec["key"]: spec for spec in sprites.TRAVELERS}
    spec = roster.get(key)
    if spec is None:
        from gen_sidecast import CAST, CLAN
        spec = next(character for character in CAST if character["key"] == key)
        spec = dict(zip(("top", "lower", "accent", "armor", "lace"), CLAN[spec["clan"]])) | spec
    weapon = "none" if key == "yosai" else spec["weapon"]
    basename = PLACE[key]["basename"] if key in PLACE else ("side_" if key == "yosai" else "trav_") + key
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
        left, right = stubs(body) if key in PLACE else (None, None)
        if not view and ((right is not None and left is None) if key in PLACE else key not in SOLO):
            body = body.transpose(Image.Transpose.FLIP_LEFT_RIGHT)   # the visible arm socket is the near shoulder
            left, right = ([body.width - 1 - right[0], right[1]] if right else None), None
        height = BUILD.get(key, {}).get("torso", 40 if key not in ("haruki", "sayo") else 38)
        scale = height / body.height
        width, depth = body.size
        hip = [width * .5, depth * .86]
        sockets = {
            "root": hip, "neck": joint(body, .04),
            "shoulder_f": left or [width * (BUILD.get(key, {}).get("pin", .13) if not view else .17),
                                   depth * (.3 + BUILD.get(key, {}).get("drop", 0))],
            "shoulder_b": right or [width * (BUILD.get(key, {}).get("far", .84) if not view else .83),
                                    depth * (.27 + BUILD.get(key, {}).get("drop", 0))],
            "hip_f": [width * .65, hip[1]], "hip_b": [width * .35, hip[1]],
            "saya": [width * .67, hip[1] - 4],
        }
        save("body" + view, body, hip, scale, sockets)
        head = cores[column][row]
        neck_y = .81 if key in ("mitsue", "sayo") or spec.get("hairstyle") == "long" else .90
        neck = joint(head, BUILD[key]["neck"]) if key in BUILD else [head.width * (.55 if not view else .5), head.height * neck_y]
        tall = BUILD.get(key, {}).get("head", 31)
        if key in PLACE:                            # less hair or hat above the skull means a smaller drawing
            tall = 34 if spec.get("hat") or spec.get("head") else 30 if spec.get("hairstyle") in ("mane", "long") else 28
        save("head" + view, head, neck,
             tall / head.height, {"crown": [head.width * .5, head.height * .22]})
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
        if key in PLACE:                            # every leg must point its toes right, however it was drawn
            alpha = np.asarray(leg)[..., 3] >= 128
            toes = np.nonzero(alpha[leg.height * 9 // 10:])[1].mean()
            shin = np.nonzero(alpha[leg.height * 6 // 10:leg.height * 8 // 10])[1].mean()
            if toes < shin:
                leg = leg.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif side == "f":
            leg = leg.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        hip, knee, ankle = (joint(leg, fraction) for fraction in (.06, .46, .85))
        length = np.linalg.norm(np.array(knee) - hip) + np.linalg.norm(np.array(ankle) - knee)
        scale = BUILD.get(key, {}).get("leg", 50 if key == "gendo" else 48 + (spec.get("height", 0) if key in PLACE else 0)) / length
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


def prepare_batch(name, feet=None):
    from gen_sidecast import CAST
    cast = {character["key"]: character for character in CAST}
    feet = feet or atlas_parts(SOURCE / "roster_feet.png", 2, len(FOOT_ORDER))
    cores = atlas_parts(SOURCE / f"{name}_cores.png")
    limbs = atlas_parts(SOURCE / f"{name}_limbs.png")
    done = []
    for row, key in enumerate(BATCHES[name]):
        PLACE[key] = dict(row=row, foot=footwear(cast[key]), basename="side_" + key)
        done.append(prepare(key, cores, limbs, feet))
    return done


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="*", choices=FOOT_ORDER)
    parser.add_argument("--batch", choices=BATCHES)
    args = parser.parse_args()
    cores = atlas_parts(SOURCE / "roster_cores.png")
    limbs = atlas_parts(SOURCE / "roster_limbs.png")
    feet = atlas_parts(SOURCE / "roster_feet.png", 2, len(FOOT_ORDER))
    if args.batch:
        for basename in prepare_batch(args.batch, feet):
            print(f"{basename}: reusable parts and profile prepared")
        return
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
