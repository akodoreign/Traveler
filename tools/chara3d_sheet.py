"""Pixel-art sprite sheets rendered from real 3-D characters (tools/blender/chara3d.py).

py -3.12 -E tools\\chara3d_sheet.py trav_natsuko --review                    # a page of poses, nothing installed
py -3.12 -E tools\\chara3d_sheet.py trav_natsuko --review --outfit bare --weapon katana
py -3.12 -E tools\\chara3d_sheet.py trav_natsuko side_goro --install         # bake all 211 frames and install

Blender poses and renders each frame three ways (lit, flat colour, part id) at sprite resolution; this
script turns them into pixel art: a three-tone ramp per material, chosen by how lit the pixel is, with a
dark outline around the figure and between its parts.
"""
import argparse
import colorsys
import glob
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import rig3d
import rig3d_poses as poses
import rig3d_sheet as sheet

SCALE = 1.4                                     # sprite pixels per model unit
SIZE, ORIGIN = (292, 256), (146, 240)
REVIEW = "idle8:0,fidle:0,bidle:0,walk8:1,walk8:3,ready:0,atk_thrust:1,atk_thrust:3,atk_overhead:2,talk:1,rei:2,seiza:0"
DEEP, SHADOW, LIGHT = .30, .51, .605            # lit / flat colour ratios where the tone changes


def blender_exe():
    found = [os.environ.get("BLENDER", "")] + sorted(glob.glob(os.path.expandvars(
        r"%LOCALAPPDATA%\Programs\Blender\*\blender.exe")), reverse=True)
    for path in found:
        if path and os.path.isfile(path):
            return path
    raise FileNotFoundError("Blender not found; see docs/CHARACTERS_3D.md")


# Colours that read better on a lit 3-D figure than the flat 2-D values did.
LOOK3D = {
    "side_yosai": dict(body_ink="ise_zumi", short_sleeves=True),
    "trav_natsuko": dict(top=(43, 54, 85), lower=(33, 36, 50), armor=(111, 118, 131),
                         lace=(177, 39, 54), accent=(175, 38, 52), iron_cap=True),
    "trav_haruki": dict(top=(196, 69, 29), lower=(73, 54, 47), accent=(175, 41, 36),
                        pcol=(250, 187, 108), lining=(233, 158, 81), long_robe=True),
    "trav_mitsue": dict(top=(153, 29, 54), lower=(43, 33, 50), accent=(178, 32, 56),
                        pcol=(222, 145, 111), lining=(124, 35, 48), long_robe=True),
}

# Small pieces that remain on the body when clothing is swapped.
EAR_ORNAMENTS = {
    "trav_natsuko": ["stud", [184, 177, 155]], "trav_shizue": ["drop", [218, 174, 80]],
    "trav_mitsue": ["stud", [204, 155, 77]], "trav_haruki": ["stud", [193, 141, 68]],
    "side_norie": ["stud", [230, 167, 92]], "side_sanae": ["drop", [165, 208, 227]],
    "side_yachiko": ["drop", [113, 185, 145]], "side_sachiko": ["stud", [171, 123, 74]],
}

def look(key):
    """The character's look spec, shared with the 2-D generators."""
    kind, name = key.split("_", 1)
    if kind == "trav":
        import gen_sprites2d as sprites
        spec = next(t for t in sprites.TRAVELERS if t["key"] == name)
    else:
        import gen_sidecast as cast
        spec = next(c for c in cast.CAST if c["key"] == name)
        spec = dict(zip(("top", "lower", "accent", "armor", "lace"), cast.CLAN[spec["clan"]])) | spec
    spec = dict(spec) | LOOK3D.get(key, {})
    if key in EAR_ORNAMENTS:
        spec["ear_ornament"] = EAR_ORNAMENTS[key]
    return {k: list(v) if isinstance(v, tuple) else v for k, v in spec.items()}


def family(spec, weapon=None):
    weapon = weapon or spec.get("weapon", "none")
    return "iai" if spec.get("idle") == "iai" and weapon == "katana" else rig3d.FAMILY.get(weapon, "fist")


def render(key, frames, outfit=None, weapon=None):
    """Run Blender for these (kind, index, count, view) frames; returns the folder of raw passes."""
    spec = look(key)
    out = rig3d.ROOT / "_art" / "preview" / "chara3d" / "raw" / "_".join(filter(None, (key, outfit, weapon)))
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    kin = family(spec, weapon)
    resolved = []
    for kind, index, count, view in frames:
        kind, view = poses.VIEWS.get(kind, (kind, view))
        if kind in ("critical", "void_critical"):
            kind = poses.SPECIAL[kin][kind == "void_critical"]
        resolved.append([kind, index, count, view])
    job = out / "job.json"
    job.write_text(json.dumps(dict(spec=spec, family=kin, outfit=outfit, weapon=weapon, out=str(out), size=SIZE, scale=SCALE,
                                   origin=ORIGIN, frames=resolved)), encoding="utf-8")
    script = rig3d.ROOT / "tools" / "blender" / "chara3d.py"
    done = subprocess.run([blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python",
                           str(script), "--", str(job)], capture_output=True, text=True)
    if done.returncode or not (out / "meta.json").is_file():
        raise RuntimeError(f"{key}: Blender failed\n{(done.stdout + done.stderr)[-1500:]}")
    return out


def ramp(rgb):
    """Shadow, base and light tones: shadows cool and deepen, lights warm and fade."""
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))

    def tone(value, saturation, toward, amount):
        hue = h + ((toward - h + .5) % 1 - .5) * amount
        return [round(c * 255) for c in colorsys.hsv_to_rgb(hue % 1, min(1., saturation), min(1., value))]

    dark = .66 + .12 * (v < .4)                  # already-dark cloth keeps its shadows readable
    return [tone(v * dark * .72, s * 1.2 + .05 * (s > .05), .70, .16), tone(v * dark, s * 1.15 + .04 * (s > .05), .70, .10),
            list(rgb), tone(v * 1.17 + .05, s * .8, .12, .08)]


def pixelize(folder, number, palette):
    lit, flat, part = (np.asarray(Image.open(folder / f"{number:04d}_{m}.png").convert("RGBA")).astype(int)
                       for m in "sai")
    mask = flat[..., 3] > 127
    colours = np.array(palette)
    index = np.abs(flat[..., None, :3] - colours[None, None]).sum(-1).argmin(-1)
    weight = np.array((.3, .59, .11))
    base = colours[index] @ weight
    ratio = (lit[..., :3] @ weight) / np.maximum(base, 14)
    tones = np.array([ramp(c) for c in palette])
    out = tones[index, 2 + (ratio > LIGHT) - (ratio < SHADOW) - (ratio < DEEP)]
    line = np.zeros_like(mask)
    for axis in (0, 1):                         # a line between two parts goes on the darker one
        a, b = (slice(None, -1), slice(1, None))
        first = (a, slice(None)) if axis == 0 else (slice(None), a)
        second = (b, slice(None)) if axis == 0 else (slice(None), b)
        differ = mask[first] & mask[second] & (np.abs(part[first][..., :3] - part[second][..., :3]).sum(-1) > 12)
        darker = base[first] <= base[second]
        line[first] |= differ & darker
        line[second] |= differ & ~darker
    inside = np.pad(mask, 1)
    edge = mask & ~(inside[:-2, 1:-1] & inside[2:, 1:-1] & inside[1:-1, :-2] & inside[1:-1, 2:])
    out[line] = tones[index, 0][line] * .8
    out[edge] = tones[index, 0][edge] * .55
    return Image.fromarray(np.dstack((out * mask[..., None], mask * 255)).astype(np.uint8), "RGBA")


def frames_for(selections):
    counts = {name: (kind, count, view) for name, kind, count, view in sheet.plan()[0]}
    return [(counts[name][0], int(index), counts[name][1], counts[name][2])
            for name, index in (s.rsplit(":", 1) for s in selections)]


def review(keys, selections, out, zoom, outfit, weapon):
    box = (40, 20, 288, 256)
    width, height = box[2] - box[0], box[3] - box[1]
    page = Image.new("RGB", (len(selections) * width, len(keys) * height + 12), (204, 196, 176))
    draw = ImageDraw.Draw(page)
    for column, selection in enumerate(selections):
        draw.text((column * width + 4, 0), selection, fill=(60, 50, 40))
    for row, key in enumerate(keys):
        folder = render(key, frames_for(selections), outfit, weapon)
        palette = json.loads((folder / "meta.json").read_text())["palette"]
        for column in range(len(selections)):
            image = pixelize(folder, column, palette).crop(box)
            page.paste(image, (column * width, row * height + 12), image)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.resize((page.width * zoom, page.height * zoom), Image.Resampling.NEAREST).save(out)


def bake(key):
    """All 211 frames of one character as a sprite sheet in the game's layout."""
    clips, cols = sheet.plan()
    folder = render(key, [(kind, index, count, view) for _, kind, count, view in clips for index in range(count)])
    palette = json.loads((folder / "meta.json").read_text())["palette"]
    total = sum(count for _, _, count, _ in clips)
    grid = (cols, -(-total // cols))
    image = Image.new("RGBA", (SIZE[0] * grid[0], SIZE[1] * grid[1]))
    for i in range(total):
        image.alpha_composite(pixelize(folder, i, palette), ((i % cols) * SIZE[0], (i // cols) * SIZE[1]))
    resource = rig3d.ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"
    image.save(resource / "enemy_pic2x" / f"{key}.png", optimize=True)
    return key, grid


def extra_clips():
    extra, start = {}, 182
    for name, count, speed, loop in sheet.EXTRA:
        extra[name] = {"id": name, "st": start, "en": start + count, "spd": speed, "loop": loop, "replay": True}
        start += count
    return extra


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="+")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--review", nargs="?", const=REVIEW)
    parser.add_argument("--outfit")
    parser.add_argument("--weapon")
    parser.add_argument("--zoom", type=int, default=3)
    parser.add_argument("--out", default="review")
    args = parser.parse_args()
    if args.review:
        out = rig3d.ROOT / "_art" / "preview" / "chara3d" / f"{args.out}.png"
        review(args.keys, args.review.split(","), out, args.zoom, args.outfit, args.weapon)
        print(f"review: {out}")
    elif args.install:
        for key in args.keys:
            name, grid = bake(key)
            sheet.register([name], extra_clips(), grid, SIZE, ORIGIN[1])
            print(f"{name}: installed")


if __name__ == "__main__":
    main()
