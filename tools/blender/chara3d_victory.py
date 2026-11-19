"""Export native weapon meshes and character-specific victory motion banks."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d_native as native

from blender_rpgcobo.pm_convert import BoneParts, MotionData, Transform, mtx_xm90
import victory_poses

c = native.c


def weapon_mesh(item, kind, label):
    skin = c.Skin()
    name = label.lower()
    number = int(item[1:])
    jade = "jade" in name
    wood = (105, 80, 52) if "bamboo" in name or "rattan" in name else (99, 66, 47)
    if "ironwood" in name:
        wood = (66, 49, 43)
    accent = (68, 141, 104) if jade else (130, 61, 45) if number < 120 else (90, 85, 121)
    trim = (205, 180, 112) if "fine" in name or "kakita" in name or "master" in name else (155, 143, 120)
    steel = (168, 202, 178) if jade else (221, 226, 236)
    if kind == "musket":
        w = {"weapon": 1.}
        skin.add(c.tube([((0, -20, 0), 1.7, 1.7), ((0, 12, 0), 1.45, 1.35),
                         ((0, 31, 0), .87, .86)], 8), c.WOOD, w)
        skin.add(c.tube([((1.1, -2, 0), .81, .81), ((1.1, 42, 0), .81, .81)], 8), c.STEEL, w)
        skin.add(c.box((.7, 1.2, 0), (.9, 1.3, 1.05)), c.INK, w)
    elif kind == "claws":
        for side, sign in c.SIDES:
            hand = {"hand" + side: 1.}
            skin.add(c.box((-1.5, 58.5, 13.4 * sign), (.8, 1.45, 2.3)), accent, hand, smooth=False)
            for span in (-1.22, 0, 1.22):
                z = 13.4 * sign + span
                skin.add(c.tube([((-1.6, 58.6, z), .34, .28), ((-2.4, 55.5, z), .33, .22),
                                 ((-1.4, 53.2 if number == 160 else 54.1, z), .08, .08)], 5),
                         c.STEEL, hand)
    else:
        spec = {"accent": accent, "trim": trim}
        if kind == "tetsubo" and jade:
            spec["stud"] = (68, 141, 104)
        c.weapon(skin, spec, "katana" if kind == "kakita" else kind)
        if kind in ("katana", "kakita", "tanto", "bokken", "bo", "yari", "shakujo"):
            grips = 2 + number % 4
            for i in range(grips):
                at = -1.6 - i * 1.05
                skin.add(c.tube([((0, at, 0), 1.17, 1.06), ((0, at + .49, 0), 1.17, 1.06)], 8),
                         accent if i % 2 == 0 else trim, {"weapon": 1.})
        if kind in ("tetsubo", "yumi", "kama"):
            skin.add(c.ellipsoid((0, -1.65, 0), (1.29, 1.04, 1.29), 8, 5), accent, {"weapon": 1.})
        # Differently sized fittings distinguish individual entries with the same silhouette.
        size = .92 + (number - 100) * .011
        at = -6.8 if kind in ("katana", "kakita") else -3.8 if kind == "tanto" else -2.6
        skin.add(c.tube([((0, at - .31, 0), size, size * .88),
                         ((0, at + .31, 0), size, size * .88)], 8), trim, {"weapon": 1.})
    colours = {c.WOOD: wood, c.STEEL: steel}
    skin.colour = [colours.get(colour, colour) for colour in skin.colour]
    return skin


def bank(rig, frames, destination):
    """Use the RPG-Cobo writer directly, with the same bind transforms as the body exporter."""
    motion = MotionData()
    for index, bone in enumerate(rig.data.bones):
        part = BoneParts()
        part.id, part.name = index, bone.name
        part.bindpose = mtx_xm90 @ bone.matrix_local
        part.length = bone.length
        motion.parts.append(part)
    previous = {}
    for frame in frames:
        if frame is None:
            previous.clear()
            continue
        for part in motion.parts:
            target = frame[part.name]
            matrix = mtx_xm90 @ c.matrix(target) if target else part.bindpose @ Matrix.Scale(0., 4)
            location, rotation, scale = matrix.decompose()
            if part.name in previous and target:
                rotation.make_compatible(previous[part.name])
            previous[part.name] = rotation
            transform = Transform()
            transform.set(location, scale, rotation)
            part.timeline.append(transform)
    for part in motion.parts:
        part.timeline.end = len(part.timeline.list) - 1
        if part.timeline.end >= 32767:
            raise ValueError(f"Motion bank too long: {destination}")
    native.saveMotionData(motion, str(destination))


def victory_frames(kind, family, actors):
    for key in actors:
        yield None
        for frame in range(victory_poses.FRAMES + 1):
            yield c.pose_frames(victory_poses.controls(key, kind, family, frame))


def combat_frames(weapon, info):
    for clip, index, count in info["frames"]:
        controls = c.poses.controls(clip, index, count, info["family"])
        if controls["weapon"] is None and controls["carry"]:
            controls["weapon"] = {"hand": "F", "dir": (.32, -.61, -.47), "shift": 0}
        yield c.pose_frames(controls)


def main(job):
    out = Path(job["out"])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    native.clearCaches()
    scene = bpy.context.scene
    rig = c.make_armature(c.rest_frames())
    for item, details in job["weapons"].items():
        if details["kind"] != "none":
            native.save_piece(scene, out, rig, item, weapon_mesh(item, details["kind"], details["name"]))
    for key, spec in job.get("authored_weapons", {}).items():
        skin = c.Skin()
        c.weapon(skin, spec, spec["weapon"])
        native.save_piece(scene, Path(job["authored_out"]), rig, key + "_weapon", skin)
    for kind in job.get("shared_weapons", []):
        skin = c.Skin()
        c.weapon(skin, {"accent": (91, 64, 53), "trim": (162, 135, 88)}, kind)
        native.save_piece(scene, Path(job["shared_out"]), rig, "weapon_" + kind, skin)
    for kind, info in job["banks"].items():
        print(f"VICTORY {kind}: {len(info['actors'])}", flush=True)
        bank(rig, victory_frames(kind, info["family"], info["actors"]), out / f"victory_{kind}.mot")
    for weapon, info in job["combat"].items():
        bank(rig, combat_frames(weapon, info), out / f"combat_{weapon}.mot")


if __name__ == "__main__":
    main(json.loads(Path(sys.argv[-1]).read_text(encoding="utf-8")))
