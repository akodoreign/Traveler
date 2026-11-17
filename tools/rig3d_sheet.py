"""Bake the 3-D mannequin's poses into the game's sprite sheets, or capture a few poses for review.

py -3.12 -E tools\\rig3d_sheet.py trav_natsuko trav_rensei --review
py -3.12 -E tools\\rig3d_sheet.py trav_natsuko --install
"""
import argparse
import json
import math

from PIL import Image, ImageDraw

import rig3d
import rig3d_poses as poses

GESTURES = (("facepalm", 4), ("shrug", 3), ("crossarms", 2), ("scratch", 3), ("point", 2))
EXTRA = (("squat", 5, 8, False), ("celebration", 10, 8, True), ("critical", 6, 12, False),
         ("void_critical", 8, 8, False))
REVIEW = "idle8:0,fidle:0,bidle:0,walk8:2,fwalk8:2,ready:0,atk_slash:1,atk_slash:3,atk_thrust:3,atk_overhead:2,atk_draw:3"


def plan():
    import gen_sprites2d as sprites
    clips = [(kind, kind, count, None) for kind, count in sprites.BLOCKS]
    clips += [(kind + ("_f" if view else ""), kind, count, view) for view in (None, "front")
              for kind, count in GESTURES]
    if sum(clip[2] for clip in clips) != 182:
        raise ValueError("The legacy battle and conversation ranges must occupy exactly 182 frames")
    return clips + [(name, name, count, None) for name, count, _, _ in EXTRA], sprites.COLS


def frame(m, kind, index, count, view=None):
    kind, view = poses.VIEWS.get(kind, (kind, view))
    if kind in ("critical", "void_critical"):
        kind = poses.SPECIAL[m.family][kind == "void_critical"]
    try:
        return m.render(poses.controls(kind, index, count, m.family), view)
    except ValueError as exc:
        raise ValueError(f"{m.key} {kind} frame {index}: {exc}") from exc


def build_sheet(m):
    clips, cols = plan()
    frames = [frame(m, kind, index, count, view) for _, kind, count, view in clips for index in range(count)]
    extra, start = {}, 182
    for name, count, speed, loop in EXTRA:
        extra[name] = {"id": name, "st": start, "en": start + count, "spd": speed, "loop": loop, "replay": True}
        start += count
    grid = (cols, math.ceil(len(frames) / cols))
    sheet = Image.new("RGBA", (m.size[0] * grid[0], m.size[1] * grid[1]))
    for i, image in enumerate(frames):
        sheet.alpha_composite(image, ((i % cols) * m.size[0], (i // cols) * m.size[1]))
    return sheet, extra, grid


def install_sheet(m, sheet, extra, grid):
    resource = rig3d.ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"
    sheet.save(resource / "enemy_pic2x" / f"{m.key}.png", optimize=True)
    register([m.key], extra, grid, m.size, m.ground_y)


def register(names, extra, grid, size, ground_y):
    """Point every registered picture with one of these basenames at its freshly baked sheet."""
    path = rig3d.ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource" / "enemy_pic.json"
    models = json.loads(path.read_text(encoding="utf-8"))
    missing = set(names)
    for entry in models.values():
        name = entry.get("pic3d", "").rsplit("/", 1)[-1][:-4] if isinstance(entry, dict) else None
        if name not in names:
            continue
        missing.discard(name)
        if "/enemy_pic2x/" not in entry["pic3d"]:
            entry["scale1x"] = entry["scale"]
            entry["scale"] /= 2
        entry["pic3d"] = f"/resource/enemy_pic2x/{name}.png"
        entry["aniuv"] = list(grid)
        entry["gndpos"] = [.5, (size[1] - ground_y - 1) / size[1]]
        entry["animap"] = [clip for clip in entry["animap"] if clip["id"] not in extra] + list(extra.values())
    if missing:
        raise ValueError(f"No registered game picture for {sorted(missing)}")
    path.write_text(json.dumps(models, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def review(keys, selections, out, zoom=1):
    """One row per character, one column per requested pose, cropped to the figure."""
    counts = {name: (kind, count, view) for name, kind, count, view in plan()[0]}
    box = (30, 14, 204, 184)
    width, height = box[2] - box[0], box[3] - box[1]
    page = Image.new("RGB", (len(selections) * width, len(keys) * height + 12), (37, 39, 48))
    draw = ImageDraw.Draw(page)
    for column, selection in enumerate(selections):
        draw.text((column * width + 4, 0), selection, fill=(240, 225, 177))
    for row, key in enumerate(keys):
        m = rig3d.Mannequin(key)
        for column, selection in enumerate(selections):
            name, index = selection.rsplit(":", 1)
            kind, count, view = counts[name]
            image = frame(m, kind, int(index), count, view).crop(box)
            page.paste(image, (column * width, row * height + 12), image)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.resize((page.width * zoom, page.height * zoom), Image.Resampling.NEAREST).save(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keys", nargs="+")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--review", nargs="?", const=REVIEW, help="comma-separated ANIMATION:FRAME poses")
    parser.add_argument("--zoom", type=int, default=1)
    args = parser.parse_args()
    out = rig3d.ROOT / "_art" / "preview" / "rig3d"
    if args.review:
        review(args.keys, args.review.split(","), out / "review.png", args.zoom)
        print(f"review: {out / 'review.png'}")
        return
    for key in args.keys:
        m = rig3d.Mannequin(key)
        sheet, extra, grid = build_sheet(m)
        out.mkdir(parents=True, exist_ok=True)
        sheet.save(out / f"{key}.png")
        if args.install:
            install_sheet(m, sheet, extra, grid)
        print(f"{key}: {grid[0]}x{grid[1]} cells, {'installed' if args.install else 'baked'}")


if __name__ == "__main__":
    main()
