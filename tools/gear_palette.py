"""Colour roles shared by the Blender garment export and the wearer textures."""
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


def atlas(destination, clan, wearer):
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
