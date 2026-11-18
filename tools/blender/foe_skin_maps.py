"""Bake a distinct surface-color tile for each installed native foe."""

from collections import Counter
from hashlib import sha256
import math
import re

import numpy as np
from PIL import Image


COLOR_TILE = re.compile(r'texture0 = "tex/foe_(\w+)_color\.png"')

# Larger markings stay readable at battle distance. Fine relief stays in
# the separately authored material normal map.
MARKINGS = {
    "skin": (.043, 3, (1., .47, .31)),
    "fur": (.085, 4, (1., .81, .62)),
    "feather": (.074, 5, (.82, .94, 1.)),
    "scale": (.085, 4, (.65, 1., .77)),
    "shell": (.085, 3, (.62, .81, 1.)),
    "bark": (.096, 4, (1., .86, .67)),
    "stone": (.086, 3, (.94, .89, .85)),
    "spirit": (.069, 2, (.63, .85, 1.)),
}


def paint_skin(base, item, key, kind):
    seed = int.from_bytes(sha256(f"{key}:{item['source']}".encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    phase = rng.uniform(0, math.tau, 5)
    height, width = base.shape[:2]
    x, y = np.meshgrid(np.arange(width) / width, np.arange(height) / height)
    strength, frequency, rgb = MARKINGS.get(kind, MARKINGS["skin"])
    mottle = np.sin(math.tau * (frequency*x + 2*y) + phase[0])
    mottle *= np.cos(math.tau * (x - frequency*y) + phase[1])
    veins = np.sin(math.tau * (2*x - y) + phase[2] + 1.25 * mottle)
    pigment = .65 * mottle + .35 * veins

    source = item["source"]
    if kind == "fur" and any(word in source for word in ("tiger", "bakeneko")):
        bars = np.sin(math.tau * (5*x + y) + phase[3] + .7 * veins)
        pigment -= 1.65 * np.maximum(0, bars) ** 4
    elif kind in ("skin", "scale", "shell"):
        speckles = np.sin(math.tau * (11*x + 7*y) + phase[3]) * np.sin(math.tau * (5*x - 13*y) + phase[4])
        pigment -= .36 * np.maximum(0, speckles) ** 7
    return np.clip(base + (strength * 255 * pigment[:, :, None]) * np.asarray(rgb), 0, 255).round().astype("uint8")


def install_skin_maps(out, jobs):
    tiles = {}
    for key, item in jobs.items():
        descriptor = out / f"{key}.pm"
        with descriptor.open(encoding="utf-8", newline="") as file:
            body = file.read()
        choices = Counter(kind for kind in COLOR_TILE.findall(body) if kind != "detail")
        if not choices:
            raise ValueError(f"{key} is missing a surface color texture")
        kind = "skin" if item["recipe"] == "human" and "skin" in choices else choices.most_common(1)[0][0]
        base = tiles.get(kind)
        if base is None:
            with Image.open(out / "tex" / f"foe_{kind}_color.png") as image:
                base = tiles[kind] = np.asarray(image.convert("RGB"), dtype=np.float32)
        name = f"{key.lower()}_skin.png"
        Image.fromarray(paint_skin(base, item, key, kind)).save(out / "tex" / name, optimize=True)
        body = body.replace(f'texture0 = "tex/foe_{kind}_color.png"', f'texture0 = "tex/{name}"')
        descriptor.write_text(body, encoding="utf-8", newline="")
