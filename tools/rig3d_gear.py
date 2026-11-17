"""Swappable gear for the 3-D mannequin: procedurally drawn weapons and head items, as rig parts."""
import json

import numpy as np
from PIL import Image, ImageDraw

import rig3d

HATS = ("jingasa", "kasa", "kabuto", "eboshi", "hachimaki")


def draw_weapon(spec, state="rest"):
    """One weapon from the legacy sprite generator, redrawn on a canvas large enough for the new scale."""
    import gen_sprites2d as sprites
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


def weapon_parts(spec, weapon):
    """Rig parts for a weapon type held by this character; a katana comes with its scabbard."""
    if weapon == "katana":
        source = json.loads((rig3d.PROFILES / "trav_rensei.json").read_text(encoding="utf-8"))
        return rig3d.load_parts({"parts": {name: source["parts"][name] for name in ("weapon", "saya")}})
    gear = dict(spec, weapon=weapon)
    anchor = (99., 96.) if weapon == "yumi" else (96., 96.)
    tip = (99., 76.) if weapon == "yumi" else (96.6, 105.) if weapon == "tanto" else (116., 96.)
    parts = {}
    for name, state in (("weapon", "rest"), ("weapon_draw", "draw")) if weapon == "yumi" else (("weapon", "rest"),):
        parts[name] = rig3d.Part(np.array(draw_weapon(gear, state)), np.array(anchor),
                                 {"tip": np.array(tip), "string": np.array((63., 96.))}, 1.)
    return parts


def hat_part(name, armor=(84, 86, 98)):
    """A head item drawn at twice its size; its anchor sits on the head's crown."""
    image = Image.new("RGBA", (64, 44))
    draw = ImageDraw.Draw(image)
    ink = (38, 32, 36)
    if name in ("jingasa", "kasa"):
        wide, tall, fill, rim = (46, 18, (150, 46, 40), (226, 190, 80)) if name == "jingasa" else \
            (62, 26, (198, 168, 104), (232, 208, 150))
        left = 32 - wide // 2
        draw.polygon(((left, tall), (32, 2), (left + wide, tall)), fill=fill, outline=ink)
        if name == "kasa":
            for x in range(left + 6, left + wide - 2, 6):
                draw.line(((32, 4), (x, tall - 1)), fill=(150, 122, 70))
        draw.line(((left + 1, tall), (left + wide - 1, tall)), fill=rim, width=2)
        anchor = (32, tall - 3)
    elif name == "kabuto":
        draw.pieslice((12, 4, 52, 44), 180, 360, fill=armor, outline=ink)
        draw.polygon(((10, 24), (16, 24), (14, 38), (6, 36)), fill=tuple(c * 3 // 4 for c in armor), outline=ink)
        draw.polygon(((48, 24), (54, 24), (58, 36), (50, 38)), fill=tuple(c * 3 // 4 for c in armor), outline=ink)
        draw.line(((13, 24), (51, 24)), fill=(226, 190, 80), width=2)
        draw.ellipse((27, 0, 37, 10), fill=(226, 190, 80), outline=ink)
        anchor = (32, 20)
    elif name == "eboshi":
        draw.polygon(((22, 40), (42, 40), (40, 14), (30, 2), (20, 6)), fill=(44, 40, 48), outline=ink)
        draw.line(((30, 4), (36, 38)), fill=(78, 72, 84))
        draw.line(((22, 38), (42, 38)), fill=(110, 104, 118), width=2)
        anchor = (32, 36)
    else:                                           # hachimaki: a white band across the brow, knot tails behind
        draw.rectangle((14, 20, 50, 26), fill=(238, 234, 226), outline=ink)
        draw.polygon(((14, 21), (4, 26), (6, 32), (15, 26)), fill=(238, 234, 226), outline=ink)
        anchor = (32, 12)
    return rig3d.Part(np.array(image), np.array(anchor, float), {}, .5)
