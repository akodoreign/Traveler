"""Author Natsuko's Crab lacquer, woven cloth and painted mon on their existing charts."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter


ITEMS = ("A173", "A110")
WEARER = "trav_natsuko"
DYES = {
    "A173": (
        (0, 0, 0), (2, 5, 12), (4, 10, 22), (6, 15, 34),
        (8, 22, 49), (11, 31, 67), (14, 41, 86), (19, 53, 107), (26, 69, 133),
    ),
    "A110": (
        (0, 0, 0), (2, 4, 11), (3, 8, 21), (4, 12, 32),
        (6, 18, 46), (8, 25, 63), (11, 34, 81), (15, 45, 102), (21, 60, 126),
    ),
}
STOPS = (0, .045, .13, .23, .36, .51, .66, .83, 1)
RED = (
    (0, 0, 0), (20, 5, 8), (35, 9, 13), (59, 15, 19),
    (89, 25, 29), (124, 38, 41), (155, 50, 49), (180, 65, 58), (211, 87, 72),
)


def read(path, mode):
    with Image.open(path) as source:
        return np.array(source.convert(mode), dtype=np.float32) / 255.0


def save(path, pixels):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.rint(np.clip(pixels, 0, 1) * 255).astype("uint8")).save(path)


def smooth(low, high, values):
    t = np.clip((values - low) / (high - low), 0, 1)
    return t * t * (3 - 2 * t)


def tone(curve, light):
    anchors = np.asarray(curve, dtype=np.float32).T / 255.0
    return np.stack([np.interp(light, STOPS, channel) for channel in anchors], axis=-1)


def brush_finish(width, height, sequence):
    """Fine opposing cotton courses and irregular rubbed lacquer, aligned in atlas space."""
    rng = np.random.default_rng(sequence)
    y, x = np.mgrid[:height, :width]
    u, v = (.98 * x + .18 * y), (-.18 * x + .98 * y)
    warp = np.sin(np.pi * 2 * (u + .18 * np.sin(v / 7.8)) / 4.15)
    weft = np.sin(np.pi * 2 * (v - .23 * np.sin(u / 10.6)) / 4.65)
    flecks = rng.normal(0, 1, (height, width))
    chalk = gaussian_filter(flecks, 2.2) * .078
    weave = .018 * (warp * weft) + .009 * np.maximum(warp, weft) + chalk
    drag = gaussian_filter(flecks, (.45, 2.7))
    haze = gaussian_filter(flecks, 7.5) * .16
    lacquer = .011 * drag + .014 * np.maximum(drag - .7, 0) + haze
    return weave, lacquer


def dye(key, source, current):
    """Keep the mapped folds and focus crimson and iron-grey on existing small details."""
    original_value = source.max(axis=-1)
    old_value = current.max(axis=-1)
    saturation = (original_value - source.min(axis=-1)) / np.maximum(.03, original_value)
    sr, sg, sb = np.moveaxis(source, -1, 0)
    red = smooth(.08, .21, sr - sg) * smooth(.075, .17, sr - sb)
    red *= smooth(.44, .66, saturation) * smooth(.18, .32, original_value)
    if key == "A110":
        # Suppress the broad old crimson cast from warm browns under the Kabuto.
        red *= smooth(.66, .79, saturation)
    # Restrict steel-grey to small, bright neutral edges.
    bright_edge = original_value - gaussian_filter(original_value, 2.8)
    gray = smooth(.64, .80, original_value) * (1 - smooth(.08, .19, saturation))
    gray *= smooth(.034, .105, bright_edge)
    gray *= 1 - red

    value = .73 * old_value + .27 * original_value
    base = tone(DYES[key], value)
    accent = tone(RED, .3 * old_value + .7 * original_value)
    edge = np.stack((.62 * value + .14, .66 * value + .145, .69 * value + .159), axis=-1)
    color = base * (1 - red[..., None]) + accent * red[..., None]
    color = color * (1 - gray[..., None]) + edge * gray[..., None]
    h, w = value.shape
    weave, lacquer = brush_finish(w, h, 173 if key == "A173" else 110)
    gloss = np.maximum(gray, 1 - smooth(.17, .36, saturation)) if key == "A173" else .86
    finish = weave * (1 - gloss) + lacquer * gloss
    color *= 1 + finish[..., None]
    return np.where((original_value + old_value)[..., None] > .023, color, current)


def mon_atlas(current):
    """Retint painted mon while preserving both placement tiles and coverage byte-for-byte."""
    rgb = current[..., :3]
    r, g, b = np.moveaxis(rgb, -1, 0)
    light = np.clip(.34 * r + .56 * g + .10 * b, 0, 1)
    red = smooth(.26, .49, r - g) * smooth(.23, .45, r - b)
    steel = np.stack((.78 * light, .82 * light, .85 * light), axis=-1)
    cinnabar = np.stack((.83 * r, .86 * g, .82 * b), axis=-1)
    color = steel * (1 - red[..., None]) + cinnabar * red[..., None]
    result = current.copy()
    result[..., :3] = np.where(current[..., 3:4] > 0, color, rgb)
    return result


def contact_sheet(out, rows):
    palette = "#171f2c"
    panel_w, panel_h = 337, 291
    sheet = Image.new("RGB", (panel_w * 3, panel_h * len(rows) + 82), palette)
    draw = ImageDraw.Draw(sheet)
    header = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 24)
    label = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)
    draw.text((14, 11), "Hiruma Natsuko · Deep Crab navy material preview", font=header, fill="#e8edf5")
    draw.text((14, 46), "Runtime UV atlases and two-tile projected mon sheets", font=label, fill="#aebdce")
    for row, (title, before, after, mark_before, mark_after) in enumerate(rows):
        y = row * panel_h + 76
        for column, (caption, a) in enumerate((("Original dye", before), ("Deep Crab navy", after))):
            x = panel_w * column + 15
            draw.text((x, y + 3), f"{title} · {caption}", font=label, fill="#e8edf5")
            sheet.paste(Image.fromarray(np.rint(a * 255).astype("uint8")).resize((panel_w - 34, 243)),
                        (x, y + 29))
        x = panel_w * 2 + 15
        draw.text((x, y + 3), "Projected Crab mon", font=label, fill="#e8edf5")
        for mark_row, (caption, a) in enumerate((("Original paint", mark_before), ("Iron-grey and red", mark_after))):
            y_mark = y + 38 + mark_row * 119
            rgba = Image.fromarray(np.rint(a * 255).astype("uint8")).resize((182, 91))
            sheet.paste(rgba, (x + 3, y_mark), rgba)
            draw.text((x + 192, y_mark + 34), caption, font=label, fill="#c7d2e2")
    sheet.save(out)


def build(repo, out, preview):
    resource = repo / "_tools/rpgcobo-tool/project/resource"
    current = resource / "native_tailoring/tex"
    rows = []
    for key, title in zip(ITEMS, ("A173 Scout armor", "A110 Kabuto"), strict=True):
        source = read(current / f"{key}_color_srgb.png", "RGB")
        before = read(current / "crab" / f"{key}.png", "RGB")
        after = dye(key, source, before)
        original_mark = read(resource / "native_gear/decal/crab" / f"{key}.png", "RGBA")
        new_mark = mon_atlas(original_mark)
        stem = f"{WEARER}_{key}"
        save(out / "tex/crab" / f"{stem}.png", after)
        rows.append((title, before, after, original_mark, new_mark))
    contact_sheet(preview, rows)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("repository", type=Path)
    cli.add_argument("stage", type=Path)
    cli.add_argument("preview", type=Path)
    opt = cli.parse_args()
    build(opt.repository, opt.stage, opt.preview)

