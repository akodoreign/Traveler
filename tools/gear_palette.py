"""Colour roles shared by the Blender garment export and the wearer textures."""
import colorsys
from functools import cache
import math

TILE = 32
SIZE = TILE * 8
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
# (user 2026-11-22: "fixing all npc clan colors ... with the deeper richer colors"; Hida Kisada "dark blue, with darker
# blue tint, red studs") Deeper, richer samurai dyes: each clan's hue kept, the main colours darker and more saturated,
# the armour lacquered in the clan colour rather than grey steel. tools/gen_clan_dyes.py re-dyed the deployed textures
# from the old values (its AS_BUILT) to these.
NATIVE_CLANS = {
    "crab": ((18, 34, 76), (8, 14, 34), (140, 14, 16), (18, 28, 64), (150, 12, 16)),   # (user: "make those pinks
#            red, and the blues darker")
    "crane": ((10, 60, 112), (10, 30, 63), (240, 232, 210), (41, 72, 105), (232, 224, 204)),
    "dragon": ((7, 64, 35), (6, 34, 23), (165, 108, 9), (11, 53, 29), (187, 134, 21)),
    "lion": ((125, 67, 0), (64, 25, 5), (189, 126, 10), (90, 44, 3), (121, 14, 3)),
    "mantis": ((0, 72, 59), (3, 33, 30), (172, 116, 21), (9, 60, 48), (185, 136, 35)),
    "phoenix": ((153, 41, 0), (78, 7, 10), (150, 9, 0), (78, 17, 9), (201, 117, 4)),
    "scorpion": ((92, 0, 16), (26, 7, 17), (160, 105, 36), (50, 5, 17), (150, 3, 18)),
    "unicorn": ((61, 15, 99), (29, 11, 53), (167, 111, 30), (44, 21, 74), (187, 132, 37)),
    "imperial": ((6, 69, 38), (9, 38, 24), (178, 127, 13), (18, 54, 29), (194, 146, 34)),
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


def deepen(rgb):
    """A washed-out pastel (light and greyish) as a deeper, richer dye of the same hue; whites and darks stay."""
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    if min(rgb) >= 205 or v < .62 or s < .08:
        return tuple(rgb)
    s, v = min(.78, s * 1.45 + .12), min(v, .62 - .1 * (s > .4))
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def clan_tones(clan, wearer):
    # (user 2026-11-21: "companions, npcs, guests all are still using the light (pastel) colors can we swap these to
    # the darker richer colors of their clan?") The side cast's own colours are the old 2-D sprite pastels: for them
    # the clan dye now dominates (a 6% hint of their own keeps people apart), and commoners' pastels are deepened.
    side = str(wearer.get("model_key", "")).startswith("side_")
    tones = {}
    for role, rgb in zip(CLAN_ROLES, NATIVE_CLANS[clan]):
        own = wearer.get(role)
        if side:
            weight = .62 if clan in COMMON else .06
        else:
            weight = .62 if clan in COMMON else .14 if clan in ("crab", "dragon", "phoenix") else .28
        if isinstance(own, (tuple, list)) and clan in COMMON and min(own) >= 205:
            tones[role] = tuple(own)
        elif isinstance(own, (tuple, list)) and side and clan in COMMON:
            tones[role] = mix(rgb, deepen(ground_dye(own)), weight)
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
    u = (index % 8 + .5 + .3125 * math.sin((x + z) * .12)) * TILE
    v = (index // 8 + .5 + .3125 * math.sin(y * .16)) * TILE
    return (u / SIZE, 1 - v / SIZE)


@cache
def finish(role, x, y):
    """Repeat a finish inside each palette swatch without bleeding into its neighbors."""
    u, v = (x + .5) / TILE, (y + .5) / TILE
    phase = math.tau
    grain = math.sin(phase * (11 * u + 9 * v)) * math.cos(phase * (9 * u - 13 * v))
    if role in {"armor", "trim", "jade"}:
        return .97 + .035 * math.cos(phase * (u + .42 * v)) + .025 * grain, 2
    if role in {"leather", "straw", "cedar"}:
        return .96 + .046 * math.sin(phase * (7 * u + v)) + .044 * grain, 1
    warp = math.sin(phase * 7 * u)
    weft = math.sin(phase * (7 * v + .13 * warp))
    sheen = math.cos(phase * (u - .17 * v))
    return .98 + .024 * warp * weft + .037 * sheen + .014 * grain, 0


def normal_atlas(destination):
    from PIL import Image

    image = Image.new("RGB", (SIZE, SIZE), (128, 128, 255))
    pixels = image.load()
    for role, _, _, index in SWATCHES.values():
        x0, y0 = index % 8 * TILE, index // 8 * TILE
        for y in range(TILE):
            for x in range(TILE):
                dx = finish(role, (x + 1) % TILE, y)[0] - finish(role, (x - 1) % TILE, y)[0]
                dy = finish(role, x, (y + 1) % TILE)[0] - finish(role, x, (y - 1) % TILE)[0]
                normal = (-2.5 * dx, 2.5 * dy, 1)
                length = math.sqrt(sum(value * value for value in normal))
                pixels[x0 + x, y0 + y] = tuple(round(127.5 + 127.5 * value / length) for value in normal)
    image.save(destination, optimize=True)


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
                scale, glint = finish(role, x, y)
                pixels[x0 + x, y0 + y] = shade(rgb, scale, glint)
    image.save(destination, optimize=True)
