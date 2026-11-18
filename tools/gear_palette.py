"""Colour roles shared by the Blender garment export and the wearer textures."""
import colorsys
import math

TILE = 16
SIZE = 128
ROLES = dict(
    top=((193, 72, 37), ((.76, 0), (.82, 0), (.86, 0), (.62, 0))),
    lower=((68, 80, 179), ((.58, 0), (.67, 0), (.8, 0))),
    accent=((58, 159, 64), ()),
    armor=((126, 139, 152), ((.6, 0), (1.14, 8), (.59, 0), (1.08, 13))),
    lace=((155, 46, 170), ()),
    lining=((54, 155, 165), ((.72, 0),)),
    pcol=((239, 161, 80), ()),
    cord=((198, 172, 224), ()),
    trim=((216, 193, 58), ()),
    collar=((241, 233, 216), ()),
    leather=((124, 70, 46), ((.72, 0),)),
    cedar=((162, 108, 61), ()),
    jade=((70, 162, 116), ()),
    ink=((44, 36, 44), ()),
    straw=((196, 168, 108), ()),
    white=((236, 232, 222), ()),
)


def shade(rgb, factor, lift=0):
    return tuple(max(0, min(255, int(c * factor + lift))) for c in rgb)


def mix(a, b, amount):
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


CLAN_ROLES = ("top", "lower", "accent", "armor", "lace")
NATIVE_CLANS = {
    "crab": ((28, 48, 81), (25, 39, 65), (218, 48, 40), (115, 124, 134), (224, 52, 45)),
    "crane": ((52, 127, 188), (46, 84, 130), (243, 244, 238), (76, 120, 157), (239, 243, 239)),
    "dragon": ((23, 91, 50), (29, 70, 45), (231, 176, 49), (42, 87, 53), (237, 181, 48)),
    "lion": ((191, 131, 30), (126, 78, 38), (236, 177, 52), (162, 108, 39), (177, 57, 34)),
    "mantis": ((22, 132, 103), (30, 86, 79), (219, 174, 53), (35, 107, 89), (226, 179, 54)),
    "phoenix": ((255, 100, 14), (183, 39, 31), (248, 58, 31), (186, 44, 29), (255, 145, 22)),
    "scorpion": ((169, 30, 53), (89, 39, 59), (223, 157, 50), (132, 32, 54), (185, 48, 62)),
    "unicorn": ((121, 61, 163), (82, 49, 117), (222, 170, 61), (99, 65, 138), (229, 175, 62)),
    "imperial": ((46, 122, 76), (36, 82, 54), (228, 172, 47), (61, 101, 67), (227, 181, 55)),
    "peasant": ((89, 109, 102), (119, 90, 59), (153, 113, 66), (112, 95, 72), (151, 110, 67)),
    "eta": ((113, 93, 73), (90, 72, 55), (145, 104, 71), (110, 88, 66), (149, 107, 63)),
    "ronin": ((133, 94, 58), (93, 71, 52), (95, 130, 77), (108, 92, 75), (119, 141, 81)),
}
COMMON = {"peasant", "eta", "ronin"}


def ground_dye(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    if v > .58 and .10 < s < .57:
        s = min(.67, s * 1.27 + .06)
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def clan_tones(clan, wearer):
    tones = {}
    for role, rgb in zip(CLAN_ROLES, NATIVE_CLANS[clan]):
        own = wearer.get(role)
        weight = .62 if clan in COMMON else .14 if clan in ("crab", "dragon", "phoenix") else .28
        if isinstance(own, (tuple, list)) and clan in COMMON and min(own) >= 205:
            tones[role] = tuple(own)
        else:
            tones[role] = mix(rgb, ground_dye(own), weight) if isinstance(own, (tuple, list)) else rgb
    tones.update(lining=mix(tones["accent"], tones["top"], .24),
                 pcol=tones["lace"], cord=tones["lace"], trim=tones["lace"])
    return tones


def costume_tones(clan, wearer):
    tones = clan_tones(clan, wearer) if clan in NATIVE_CLANS else {}
    for role in (*CLAN_ROLES, "lining", "pcol", "cord", "trim"):
        if role not in tones and isinstance(wearer.get(role), (tuple, list)):
            tones[role] = ground_dye(wearer[role])
    return tones


SPEC = {role: rgb for role, (rgb, _) in ROLES.items()}
SWATCHES = {}
for role, (rgb, tones) in ROLES.items():
    for factor, lift in ((1, 0), *tones):
        key = shade(rgb, factor, lift)
        if key in SWATCHES:
            raise ValueError(f"Duplicate garment colour {key}")
        SWATCHES[key] = (role, factor, lift, len(SWATCHES))

# The wraps on a belt may themselves need a narrow highlight.
belt = shade(SPEC["lower"], .58)
SWATCHES[shade(belt, 1.13, 6)] = ("belt_highlight", 1, 0, len(SWATCHES))


def uv(colour, position):
    index = SWATCHES[colour][3]
    # Small continuous variation across the rest mesh samples the interior of the tile.
    x, z, y = position
    u = (index % 8) * TILE + 7.5 + 5 * math.sin((x + z) * .12)
    v = (index // 8) * TILE + 7.5 + 5 * math.sin(y * .16)
    return ((u + .5) / SIZE, 1 - (v + .5) / SIZE)


def atlas(destination, clan, wearer, name=None):
    from PIL import Image

    # Keep the clan dominant while preserving differences between wearers of the same clan.
    tones = dict(SPEC)
    for role, rgb in zip(("top", "lower", "accent", "armor", "lace"), clan):
        own = wearer.get(role, rgb)
        if not isinstance(own, (list, tuple)):
            own = rgb
        tones[role] = mix(rgb, own, .32)
    tones.update(lining=mix(tones["accent"], tones["top"], .24),
                 pcol=mix(tones["top"], (255, 234, 184), .55),
                 cord=mix(tones["lace"], (232, 221, 205), .3),
                 trim=mix(tones["accent"], (223, 190, 123), .48),
                 collar=mix((241, 233, 216), tones["top"], .12),
                 belt_highlight=shade(shade(tones["lower"], .58), 1.13, 6))
    if name in NATIVE_CLANS:
        tones.update(clan_tones(name, wearer))
        tones["collar"] = mix((241, 233, 216), tones["top"], .12)
        tones["belt_highlight"] = shade(shade(tones["lower"], .58), 1.13, 6)
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = image.load()
    for role, factor, lift, index in SWATCHES.values():
        rgb = shade(tones[role], factor, lift)
        x0, y0 = index % 8 * TILE, index // 8 * TILE
        for y in range(TILE):
            for x in range(TILE):
                weave = (x % 4 == 0) * -3 + (y % 4 == 0) * 3
                pixels[x0 + x, y0 + y] = shade(rgb, 1, weave)
    image.save(destination, optimize=True)
