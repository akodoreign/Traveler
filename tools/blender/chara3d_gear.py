"""Export shared, UV-mapped garments and alternate weapons for RPG-Cobo."""
import json
import math
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d_native as native

import gear_catalog as catalog
from gear_palette import SPEC, SWATCHES, uv
from chara3d_decals import project

c = native.c


def mantle(skin, bottom, wide):
    """A shoulder cape with an open front and longer back."""
    verts, faces = [], []
    count = 24
    for y, depth, width in ((bottom, 15, wide), ((bottom + 87) / 2, 13, wide - 1),
                            (87, 12.5, wide - .5), (94, 9, 15.4), (97, 5.8, 6.5)):
        for k in range(count + 1):
            a = .83 + (math.tau - 1.66) * k / count
            pleat = 1 + .07 * math.cos(8 * a)
            lift = max(0, 85 - y) * .37 * max(0, math.cos(a))
            verts.append((depth * math.cos(a) * pleat, y + lift, width * math.sin(a) * pleat))
    for i in range(4):
        for k in range(count):
            t = i * (count + 1) + k
            faces.append((t, t + count + 1, t + count + 2, t + 1))
    colours = [SPEC["lining"] if k in (0, count - 1) or i == 0 and k % 3 == 0
               else SPEC["top"] for i in range(4) for k in range(count)]
    skin.add((verts, faces), SPEC["top"], [c.torso_w()(p[1]) for p in verts], colours=colours)


def plates(skin, detail):
    """Solid lacquered plates, worn over the normal lacing and cloth."""
    w = c.torso_w()
    low = 73 if detail == "heavy" else 75
    skin.loft(c.cover("torso", low, 90.5, 3.1), SPEC["armor"], w, n=32,
              band=(2.9, (SPEC["armor"], SPEC["armor"], c.shade(SPEC["armor"], .6))))
    skin.loft(c.cover("torso", 88.9, 91., 3.31), SPEC["trim"], w, n=32)
    if detail in ("heavy", "champion"):
        for side, sign in c.SIDES:
            w_arm = {"upper" + side: 1.}
            for j in range(3):
                skin.add(c.box((0, 92 - 3 * j, (18.7 + .8 * j) * sign), (7.4, 1.35, 1.35)),
                         SPEC["armor"], w_arm, smooth=False)
                skin.add(c.box((3, 91 - 3 * j, (20.1 + .8 * j) * sign), (.72, .64, .33)),
                         SPEC["lace"], w_arm, smooth=False)


def garment(skin, design):
    style, hem, pattern, detail = design
    spec = SPEC | {"coat_bottom": hem, "pattern": pattern, "hakama_hem": hem}
    hard = style in ("lamellar", "plate")
    c.kimono(skin, spec, wide=style in ("robe", "silk"))
    c.hakama(skin, spec, short=hard or style == "riding")
    if style in ("robe", "silk"):
        c.coat(skin, spec)
    if style == "travel":
        # Tied travel cloak cropped high enough for walking and fighting.
        mantle(skin, 63, 16.4)
    elif detail == "mantle":
        mantle(skin, 78, 16.7)
    if hard:
        c.armour(skin, spec)
    if style == "plate":
        plates(skin, detail)
    if style == "silk":
        for side, sign in c.SIDES:
            w = c.arm_w(side)
            for y in (67.5, 71.8) if detail else (69.4,):
                skin.loft(c.cover("arm", y, y + 1.45, 4.45, sign), SPEC["armor"], w, n=16,
                          band=(.8, (SPEC["armor"], SPEC["lace"])))
    if detail in ("scales", "riding"):
        for side, sign in c.SIDES:
            bone = {"thigh" + side: .6, "pelvis": .4}
            for i in range(3):
                center = (-1.35 if detail == "riding" else 1.85, 60 - i * 3.65, (15.7 + i * .48) * sign)
                skin.add(c.box(center, (5.5 - .5 * i, 1.52, .73), yaw=-sign * 11),
                         SPEC["armor"], bone, smooth=False)
                skin.add(c.box((center[0], center[1] - 1.31, center[2] + .52 * sign),
                               (4.25 - .4 * i, .34, .4), yaw=-sign * 11),
                         SPEC["lace"], bone, smooth=False)
    if style == "riding":
        skin.loft(c.cover("torso", 72, 90, 2.2), SPEC["leather"], c.torso_w(), n=16,
                  band=(2., (SPEC["leather"], SPEC["leather"], c.shade(SPEC["leather"], .72))))
    c.obi(skin, spec)
    c.footwear(skin, spec, c.INK if hard or style == "riding" else c.WHITE)
    if detail in ("ofuda", "ward", "crest", "champion", "rivet", "storm", "lacquer"):
        motif(skin, detail)


def motif(skin, detail):
    """Small ornaments in material roles shared with the garment's textile."""
    if detail in ("ofuda", "ward"):
        for y, z in ((83, 4.2), (79, -4.1), (75, 4.2)):
            x = c.profile(c.BODY["torso"], y)[0] * c.GIRTH["torso"] + 1.07
            skin.add(c.box((x, y, z), (.43, 2.55, .95), yaw=21 if z > 0 else -21),
                     SPEC["collar"], c.torso_w()(y), smooth=False)
    else:
        for z in (-4.25, 0, 4.25):
            y = 85 if z else 87
            x = c.profile(c.BODY["torso"], y)[0] * c.GIRTH["torso"] + 3.12 - abs(z) * .103
            skin.add(c.ellipsoid((x, y, z), (.77, 1.1 if z else 1.48, .91 if z else 1.56), 8, 5),
                     SPEC["trim" if detail in ("crest", "champion", "rivet") else "lace"],
                     c.torso_w()(y), smooth=False)


def hat(skin, style):
    if style in ("band", "champion_band"):
        c.headband(skin, SPEC | {"band": SPEC["lace" if style == "band" else "accent"]}, growth=.62)
        return
    skin.zoom = c.HEAD
    w = {"head": 1.}
    if style in ("jingasa", "guard", "scout", "straw"):
        wide = 17.9 if style == "straw" else 15.6 if style == "guard" else 14.7
        profile = [(118, wide, wide), (119.3, wide, wide), (122.4, 11.5, 10.75),
                   (126.2, 7.55, 6.9), (128.8, 1.25, 1.25)]
        cloth = SPEC["straw" if style == "straw" else "armor"]
        skin.loft(profile, cloth, lambda y: w, n=32, band=(1.1, lambda i, k:
                  SPEC["lining"] if i == 0 else SPEC["trim"] if style == "guard" and i == 1 else cloth))
        if style == "scout":
            skin.add(c.ellipsoid((10.2, 122, 0), (1, 1.35, 1.35), 8, 6), SPEC["jade"], w)
    elif style == "eboshi":
        skin.loft([(117, 12.6, 11.8, -2, 0), (124, 11.7, 10.4, -2, 0), (131, 8., 6.2, -3, 0),
                   (137, 3.2, 2.7, -4.8, 0)], SPEC["ink"], lambda y: w, n=24, x=-2)
        skin.loft([(116.6, 12.9, 12), (117.8, 12.9, 12)], SPEC["lace"], lambda y: w, n=24, x=-2)
    else:
        skin.loft([(113.6, 13.2, 12.1), (120, 12.55, 11.55), (125.7, 10.1, 9.95),
                   (129.4, 6.1, 5.8), (131.2, 1.6, 1.45)], SPEC["armor"], lambda y: w, n=32,
                  band=(1.8, lambda i, k: SPEC["lace"] if i == 0
                        else c.shade(SPEC["armor"], 1.14, 8) if k % 6 == 0 else SPEC["armor"]))
        for side, sg in c.SIDES:
            for i in range(3):
                skin.add(c.box((-3.6, 112 - i * 2.5, (10.95 + .67 * i) * sg),
                               (7.9, 1.28, 1.37)), SPEC["armor"], w, smooth=False)
                skin.add(c.box((.6, 111.32 - i * 2.5, (12.38 + .67 * i) * sg),
                               (1.45, .55, .4)), SPEC["lace"], w, smooth=False)
            if style == "legion":
                c.strand(skin, SPEC["trim"], [(11, 118, 1.2 * sg), (11, 123, 3.4 * sg),
                                               (10.3, 128, 6.35 * sg)], 1.35)
    skin.zoom = None


def mask(skin, style):
    intrinsic = {"oni": "accent", "iron": "armor", "cedar": "cedar", "ink": "ink",
                 "silk": "top", "jade": "jade", "giseiki": "lower", "abbot": "cedar", "cloth": "top"}
    colour = SPEC[intrinsic[style]]
    skin.zoom = c.HEAD
    points = [(-6, 105), (-3.5, 104.1), (0, 104.35), (3.5, 104.1), (6, 105),
              (4.3, 100.3), (2.2, 98.9), (-2.2, 98.9), (-4.3, 100.3)]
    verts = [(c.face_x(y, z) + .94, y, z) for z, y in [(0, 102), *points]]
    # The central ridge keeps the inner curve above the nose and chin.
    verts[0] = (c.face_x(102, 0) + 1.51, 102, 0)
    n = len(points)
    skin.add((verts, [(0, (i + 1) % n + 1, i + 1) for i in range(n)]), colour, {"head": 1.},
             colours=[SPEC["lining"] if i in (0, 3, 5, 7) else colour for i in range(n)])
    if style in ("oni", "giseiki"):
        for _, sign in c.SIDES:
            c.strand(skin, SPEC["trim"], [(8, 102.4, 3.5 * sign), (9.6, 104.6, 4.1 * sign),
                                          (9, 106.7, 4.6 * sign)], 1.03)
    skin.zoom = None


def export(job):
    out = Path(job["out"])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    native.clearCaches()
    scene = bpy.context.scene
    rig = c.make_armature(c.rest_frames())
    from head_surfaces import HAT_SURFACE, HeadSurface, make_textures

    detail = make_textures(out / "tex", set(HAT_SURFACE.values()), color_maps=False)
    for item, slot in catalog.registry().items():
        if job.get("head_only") and slot != "head":
            continue
        skin = c.Skin()
        if slot == "body":
            garment(skin, catalog.BODY[item])
        elif slot == "head":
            hat(skin, catalog.HEAD[item])
        elif slot == "mask":
            mask(skin, catalog.ACCESSORY[item])
        else:
            mantle(skin, 57, 20.5)
        missing = set(skin.colour) - SWATCHES.keys()
        if missing:
            raise ValueError(f"{item} uses unmapped colours {missing}")
        surface = HeadSurface(detail, catalog.HEAD[item]) if slot == "head" else None
        native.save_piece(scene, out, rig, item, skin, texture_uv=uv, surface=surface)
        if job.get("head_only"):
            continue
        decal, decal_uv = project(item, slot, skin)
        native.save_piece(scene, out, rig, item + "_decal", decal, texture_uv=decal_uv, alpha_test=True)
    if job.get("head_only"):
        return
    for weapon in catalog.WEAPONS:
        skin = c.Skin()
        if weapon == "musket":
            w = {"weapon": 1.}
            skin.add(c.tube([((0, -20, 0), 1.7, 1.7), ((0, 12, 0), 1.45, 1.35),
                             ((0, 31, 0), .87, .86)], 8), c.WOOD, w)
            skin.add(c.tube([((1.1, -2, 0), .81, .81), ((1.1, 42, 0), .81, .81)], 8), c.STEEL, w)
            skin.add(c.box((.7, 1.2, 0), (.9, 1.3, 1.05)), c.INK, w)
        else:
            spec = {"accent": (192, 182, 161), "trim": (214, 188, 88)} if weapon == "kakita" else {
                "accent": (91, 64, 53), "trim": (162, 135, 88)}
            c.weapon(skin, spec, "katana" if weapon == "kakita" else weapon)
        native.save_piece(scene, out, rig, "weapon_" + weapon, skin)
    spec = job["natsuko"] | {"iron_cap": False}
    native.save_piece(scene, out, rig, "natsuko_uncovered", native.outfit(spec, "armored"))


if __name__ == "__main__":
    with open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8") as file:
        export(json.load(file))
