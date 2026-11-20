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
NATIVE_CLANS = {
    "crab": ((37, 67, 116), (19, 35, 62), (185, 43, 41), (75, 94, 113), (210, 55, 46)),
    "crane": ((36, 106, 166), (32, 61, 100), (244, 234, 212), (95, 133, 166), (237, 229, 210)),
    "dragon": ((27, 109, 68), (22, 64, 47), (211, 155, 48), (33, 92, 59), (237, 189, 74)),
    "lion": ((178, 110, 23), (106, 56, 28), (237, 178, 60), (146, 86, 28), (160, 46, 29)),
    "mantis": ((15, 119, 100), (17, 59, 55), (219, 166, 68), (34, 100, 84), (232, 189, 87)),
    "phoenix": ((219, 79, 19), (127, 30, 33), (196, 41, 29), (130, 45, 32), (249, 168, 51)),
    "scorpion": ((147, 21, 43), (50, 23, 38), (206, 152, 82), (91, 22, 38), (196, 38, 51)),
    "unicorn": ((108, 48, 151), (59, 33, 90), (212, 159, 77), (85, 54, 119), (234, 183, 89)),
    "imperial": ((26, 112, 70), (26, 66, 48), (225, 177, 62), (42, 91, 58), (241, 195, 88)),
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
