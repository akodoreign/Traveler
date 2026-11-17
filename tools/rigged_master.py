"""Rebuild one character's HD battle poses from a generated master drawing and the existing pose rig.

Run: py -3.12 -E tools/rigged_master.py trav_natsuko path\\to\\master.png
The default writes previews only; --install replaces that character's enemy_pic2x sheet.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_busts as busts
import gen_sprites2d as sprites
import rig_anim as rig
sys.argv = _argv

Z = 2
BG = (38, 36, 44)
OUT = os.path.join(HERE, "..", "_art", "preview", "rigged_masters")

# The generated master is upright with a vertical yari; align its arm and weapon joints to the drawing,
# then apply the rig's usual motion deltas around that pose.
MASTER_JOINTS = {
    "trav_natsuko": {
        "sh_b": (100, 70),
        "el_b": (97, 82),
        "ha_b": (98, 91),
        "sh_f": (106, 69),
        "el_f": (111, 71),
        "ha_f": (118, 75),
        "hip": (104, 94),
        "kn_b": (102, 111),
        "ft_b": (101, 127),
        "kn_f": (104, 111),
        "ft_f": (102, 127),
        "shm": (103, 70),
        "hipd": (104, 90),
        "neck": (103, 69),
        "head_top": (102, 46),
        "toe_b": (107, 127),
        "toe_f": (107, 127),
        "wtip": (118, 34),
    },
    "trav_rensei": {
        "sh_b": (70, 45),
        "el_b": (67, 56),
        "ha_b": (69, 66),
        "sh_f": (91, 45),
        "el_f": (94, 56),
        "ha_f": (91, 66),
        "hip": (80, 84),
        "kn_b": (70, 105),
        "ft_b": (67, 127),
        "toe_b": (73, 130),
        "kn_f": (90, 105),
        "ft_f": (89, 127),
        "toe_f": (95, 130),
        "shm": (80.5, 45),
        "hipd": (80, 80),
        "neck": (80, 43),
        "head_top": (80, 2),
        "waistline_b": (63, 83),
        "waistline_f": (98, 83),
        "wtip": (111, 63),
    }
}
MASTER_WEAPON_ROTATION = {"trav_natsuko": 0.6, "trav_rensei": 1.0}
MASTER_LEG_MOTION_SCALE = {"trav_natsuko": 0.7, "trav_rensei": 0.7}
MASTER_ARM_MOTION_SCALE = {"trav_natsuko": 0.7, "trav_rensei": 0.7}
MASTER_BODY_MOTION_SCALE = {"trav_rensei": 0.3}
MASTER_GESTURE_BODY_MOTION_SCALE = {"trav_rensei": 0.55}


def solid_box(alpha):
    ys, xs = np.nonzero(alpha >= 128)
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None


def make_master(key, source):
    if key == "trav_rensei":
        return make_rensei_parts_master()
    T = rig.traveler(key)
    if T is None:
        raise ValueError("No compatible rig for %s" % key)
    k0, i0 = sprites.FRAMES[0]
    reference = np.asarray(sprites.frame(T, k0, i0))
    rbox = solid_box(reference[..., 3])
    if not rbox:
        raise ValueError("The reference rig frame is empty")

    cut = busts.key_out(Image.open(source).convert("RGB"), tol=12, holes=True)
    pixels = np.asarray(cut).copy()
    pixels[..., 3] = np.where(pixels[..., 3] >= 128, 255, 0)
    box = solid_box(pixels[..., 3])
    if not box:
        raise ValueError("Background removal left no foreground pixels")
    x0, y0, x1, y1 = box
    piece = Image.fromarray(pixels[y0:y1 + 1, x0:x1 + 1], "RGBA")

    target_h = (rbox[3] - rbox[1] + 1) * Z
    target_w = max(1, int(round(piece.width * target_h / piece.height)))
    max_w = sprites.FW * Z - 4
    if target_w > max_w:
        target_h = max(1, int(round(target_h * max_w / target_w)))
        target_w = max_w
    piece = piece.resize((target_w, target_h), Image.Resampling.NEAREST)
    rgb = piece.convert("RGB").quantize(colors=128, method=Image.Quantize.FASTOCTREE,
                                        dither=Image.Dither.NONE).convert("RGB")
    piece = Image.merge("RGBA", (*rgb.split(), piece.getchannel("A")))

    canvas = Image.new("RGBA", (sprites.FW * Z, sprites.FH * Z), (0, 0, 0, 0))
    cx = (rbox[0] + rbox[2] + 1) * Z / 2.0
    foot = (rbox[3] + 1) * Z
    px, py = int(round(cx - piece.width / 2)), int(round(foot - piece.height))
    px = min(max(px, 0), canvas.width - piece.width)
    py = min(max(py, 0), canvas.height - piece.height)
    canvas.alpha_composite(piece, (px, py))
    return np.asarray(canvas)


def make_rensei_parts_master(return_masks=False):
    atlas_path = os.path.join(OUT, "trav_rensei_parts_atlas_v2.png")
    atlas = Image.open(atlas_path).convert("RGBA")

    def part(box):
        return atlas.crop(box)

    def fit(image, size):
        return image.resize(size, Image.Resampling.NEAREST)

    canvas = Image.new("RGBA", (sprites.FW * Z, sprites.FH * Z), (0, 0, 0, 0))
    masks = {name: np.zeros((canvas.height, canvas.width), dtype=bool)
             for name in ("body", "head", "waist", "foot_b", "foot_f")}

    def add(image, size, xy, part_name):
        image = fit(image, size)
        canvas.alpha_composite(image, xy)
        if part_name:
            alpha = np.asarray(image.getchannel("A")) >= 128
            x, y = xy
            visible = np.zeros_like(alpha)
            visible[:min(alpha.shape[0], canvas.height - y),
                    :min(alpha.shape[1], canvas.width - x)] = \
                alpha[:min(alpha.shape[0], canvas.height - y),
                      :min(alpha.shape[1], canvas.width - x)]
            region = masks[part_name][y:y + visible.shape[0], x:x + visible.shape[1]]
            for mask in masks.values():
                mask[y:y + visible.shape[0], x:x + visible.shape[1]][visible] = False
            region[visible] = True

    skirt = part((37, 622, 409, 1120))
    add(skirt, (50, 58), (55, 71), "waist")

    torso = part((466, 161, 747, 540))
    add(torso, (48, 58), (56, 35), "body")

    head = part((85, 161, 403, 526))
    add(head, (42, 48), (59, 0), "head")
    add(part((475, 985, 638, 1129)), (19, 16), (61, 119), "foot_b")
    add(part((661, 990, 829, 1129)), (21, 16), (79, 119), "foot_f")

    if return_masks:
        return np.asarray(canvas), masks
    return np.asarray(canvas)


def source_sheet(key):
    path = os.path.join(rig.RES, "enemy_pic2x", key + ".png")
    if os.path.exists(path):
        image = Image.open(path).convert("RGBA")
        if image.width % (sprites.FW * Z) == 0 and image.height % (sprites.FH * Z) == 0:
            return image
    path = os.path.join(rig.RES, "enemy_pic", key + ".png")
    image = Image.open(path).convert("RGBA")
    return image.resize((image.width * Z, image.height * Z), Image.Resampling.NEAREST)


def load_arm_pose_sets(key):
    if key != "trav_rensei":
        return None
    import cv2

    def load_side(name):
        poses = []
        for i in range(10):
            image = np.asarray(Image.open(os.path.join(OUT, "trav_rensei_armposes",
                                                      "arm_%s_%02d.png" % (name, i))).convert("RGBA"))
            rgb = image[..., :3].astype(int)
            visible = image[..., 3] >= 128
            skin = (visible & (rgb[..., 0] > 135) & (rgb[..., 0] > rgb[..., 1] + 18) &
                    (rgb[..., 1] > rgb[..., 2] + 8))
            blue = (visible & (rgb[..., 2] > rgb[..., 0] + 12) & (rgb[..., 2] > rgb[..., 1] + 4))
            n, labels, stats, _ = cv2.connectedComponentsWithStats(skin.astype(np.uint8), connectivity=8)
            if n > 1:
                skin = labels == (1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA])))
            sy, sx = np.nonzero(skin)
            by, bx = np.nonzero(blue)
            if not len(sx) or not len(bx):
                raise ValueError("Arm pose %s/%d has no detectable sleeve or hand" % (name, i))
            hand_center = np.array([sx.mean(), sy.mean()])
            sleeve_points = np.stack([bx, by], axis=1).astype(float)
            away = sleeve_points.mean(axis=0) - hand_center
            away /= max(1e-6, np.linalg.norm(away))
            projection = (sleeve_points - hand_center) @ away
            shoulder = sleeve_points[projection >= np.quantile(projection, 0.9)].mean(axis=0)
            hand_points = np.stack([sx, sy], axis=1).astype(float)
            tip = hand_points[np.argmax(np.linalg.norm(hand_points - shoulder, axis=1))]
            poses.append({"image": image, "anchor": shoulder, "tip": tip})
        return poses

    return {"b": load_side("back"), "f": load_side("front")}


def render_pose_sheet(key, arm_pose_sets, master, label_masks=None):
    ids = list(range(len(sprites.FRAMES)))
    frames, _ = rig.rig_frames(key, master, ids, z=Z,
                               master_joints=MASTER_JOINTS.get(key),
                               weapon_rotation=MASTER_WEAPON_ROTATION.get(key, rig.WEAPON_ROT),
                               leg_motion_scale=MASTER_LEG_MOTION_SCALE.get(key, 1.0),
                               arm_motion_scale=MASTER_ARM_MOTION_SCALE.get(key, 1.0),
                               body_motion_scale=MASTER_BODY_MOTION_SCALE.get(key, 1.0),
                               arm_pose_sets=arm_pose_sets, label_masks=label_masks)
    sheet = source_sheet(key)
    sheet = sheet.resize((sprites.FW * Z * sprites.COLS, sheet.height), Image.Resampling.NEAREST)
    expected_h = sprites.FH * Z * (sprites.ROWS + 1)
    if sheet.height < expected_h:
        sheet = Image.new("RGBA", (sprites.FW * Z * sprites.COLS, expected_h), (0, 0, 0, 0))
    for i, frame in frames.items():
        x, y = (i % sprites.COLS) * sprites.FW * Z, (i // sprites.COLS) * sprites.FH * Z
        sheet.paste((0, 0, 0, 0), (x, y, x + sprites.FW * Z, y + sprites.FH * Z))
        sheet.alpha_composite(Image.fromarray(frame), (x, y))
    return frames, sheet


def save_gif(key, aid, frames):
    if not frames:
        return
    images = []
    for frame in frames:
        bg = Image.new("RGBA", frame.size, BG + (255,))
        bg.alpha_composite(frame)
        images.append(bg.convert("RGB").resize((frame.width * 4, frame.height * 4), Image.Resampling.NEAREST))
    path = os.path.join(OUT, "%s_%s.gif" % (key, aid))
    images[0].save(path, save_all=True, append_images=images[1:], duration=120, loop=0, optimize=False)


def render(key, source, install=False):
    os.makedirs(OUT, exist_ok=True)
    if key == "trav_rensei":
        master, label_masks = make_rensei_parts_master(return_masks=True)
    else:
        master, label_masks = make_master(key, source), None
    master_joints = MASTER_JOINTS.get(key)
    arm_pose_sets = load_arm_pose_sets(key)
    if arm_pose_sets:
        rigged, sheet = render_pose_sheet(key, arm_pose_sets, master, label_masks)
    else:
        ids = list(range(len(sprites.FRAMES)))
        rigged, labels = rig.rig_frames(key, master, ids, z=Z, master_joints=master_joints,
                                       weapon_rotation=MASTER_WEAPON_ROTATION.get(key, rig.WEAPON_ROT),
                                       leg_motion_scale=MASTER_LEG_MOTION_SCALE.get(key, 1.0),
                                       arm_motion_scale=MASTER_ARM_MOTION_SCALE.get(key, 1.0),
                                       body_motion_scale=MASTER_BODY_MOTION_SCALE.get(key, 1.0),
                                       label_masks=label_masks)
        sheet = source_sheet(key)
        sheet = sheet.resize((sprites.FW * Z * sprites.COLS, sheet.height), Image.Resampling.NEAREST)
        expected_h = sprites.FH * Z * (sprites.ROWS + 1)
        if sheet.height < expected_h:
            sheet = Image.new("RGBA", (sprites.FW * Z * sprites.COLS, expected_h), (0, 0, 0, 0))
        for i, frame in rigged.items():
            x, y = (i % sprites.COLS) * sprites.FW * Z, (i // sprites.COLS) * sprites.FH * Z
            sheet.alpha_composite(Image.fromarray(frame), (x, y))

    gestures = rig.gesture_frames_hd(key, master, z=Z, master_joints=master_joints,
                                     arm_pose_sets=arm_pose_sets, label_masks=label_masks,
                                     body_motion_scale=MASTER_GESTURE_BODY_MOTION_SCALE.get(key, 1.0))
    if gestures:
        y = sprites.FH * Z * sprites.ROWS
        base_gesture_count = sum(count for _, count in rig.GESTURES)
        for i, frame in enumerate(gestures[:base_gesture_count]):
            x = i * sprites.FW * Z
            sheet.alpha_composite(Image.fromarray(frame), (x, y))
        offset = base_gesture_count
        for aid, count in rig.EXTENDED_GESTURES:
            save_gif(key, aid, [Image.fromarray(frame) for frame in gestures[offset:offset + count]])
            offset += count

    for aid in ("idle8", "walk8", "atk_thrust", "atk_draw"):
        frame_ids = [i for i, (kind, _pose) in enumerate(sprites.FRAMES) if kind == aid]
        save_gif(key, aid, [Image.fromarray(rigged[i]) for i in frame_ids if i in rigged])

    sheet_path = os.path.join(OUT, key + "_sheet.png")
    master_path = os.path.join(OUT, key + "_master.png")
    sheet.save(sheet_path)
    Image.fromarray(master).save(master_path)
    if install:
        dest = os.path.join(rig.RES, "enemy_pic2x", key + ".png")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        sheet.save(dest)
    print("%s: %d rigged poses, %d gesture poses; master %s; sheet %s%s" %
          (key, len(rigged), len(gestures or []), master_path, sheet_path, " [installed]" if install else ""))
    return sheet_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    parser.add_argument("image")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    render(args.key, args.image, args.install)


if __name__ == "__main__":
    main()
