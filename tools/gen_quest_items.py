"""Generate key-item quest stars and register their inventory entries.

Run: py -3.12 -E tools/gen_quest_items.py
"""
import copy
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import gen_maps as gm  # noqa: E402

RES = ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"
S = 64


def star(draw, cx, cy, radius, color, rotation=0.0):
    points = []
    for i in range(8):
        angle = rotation + i * math.pi / 4
        r = radius if i % 2 == 0 else radius * 0.25
        points.append((cx + math.sin(angle) * r, cy - math.cos(angle) * r))
    draw.polygon(points, fill=color)


def frame(rgb, pulse, cross=False, pickup=False):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    radius = 9 + round(10 * pulse)
    alpha = 30 + round(180 * pulse)
    gd.ellipse([S / 2 - radius, S / 2 - radius, S / 2 + radius, S / 2 + radius],
               fill=(*rgb, alpha))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6 + pulse * 3)))
    draw = ImageDraw.Draw(img)
    cx = cy = S / 2
    if pickup:
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=(*rgb, 25 + round(150 * pulse)), width=2)
    if cross:
        cross_color = (*rgb, 35 + round(185 * pulse))
        draw.rectangle([cx - 1, 7, cx + 1, 57], fill=cross_color)
        draw.rectangle([7, cy - 1, 57, cy + 1], fill=cross_color)
    star(draw, cx, cy, 11 + round(9 * pulse), (*rgb, 150 + round(105 * pulse)))
    star(draw, cx, cy, 7 + round(5 * pulse), (255, 255, 255, 165 + round(90 * pulse)),
         rotation=math.pi / 4)
    return img


def register_models():
    path = RES / "enemy_pic.json"
    models = json.loads(path.read_text(encoding="utf-8"))
    template = models["EP361"]
    entries = [
        (gm.QUEST_MARKER_YELLOW_MODEL, "Yellow quest marker", "quest_marker_yellow.png",
         (255, 207, 72), True, False, 0.08),
        (gm.QUEST_MARKER_BLUE_MODEL, "Blue quest marker", "quest_marker_blue.png",
         (92, 176, 255), True, False, 0.08),
        (gm.QUEST_ITEM_MODEL, "Quest item star", "quest_item_star.png",
         (255, 198, 58), False, True, 0.18),
    ]
    memo = "quest marker/pickup (tools/gen_quest_items.py)"
    for mid in ("EP362", "EP363", "EP364", "EP20000", "EP20001", "EP20002"):
        if mid in models:
            if models[mid].get("memo") != memo:
                raise RuntimeError("%s is already assigned to %s" % (mid, models[mid].get("name")))
            del models[mid]
    for mid, name, filename, color, cross, pickup, scale in entries:
        if mid in models and models[mid].get("memo") != memo:
            raise RuntimeError("%s is already assigned to %s" % (mid, models[mid].get("name")))
        image = frame(color, 0.72, cross=cross, pickup=pickup)
        image = image.resize((S * 2, S * 2), Image.Resampling.NEAREST)
        image.save(RES / "enemy_pic" / filename)
        model = copy.deepcopy(template)
        model.update({
            "name": {"en": name, "ja": name},
            "pic3d": "/resource/enemy_pic/" + filename,
            "aniuv": [1, 1],
            "memo": memo,
            "gndpos": [0.5, 0.5],
            "scale": scale,
            "flipx": False,
            "animap": [{"id": "stand", "st": 0, "en": 1, "spd": 1.0, "loop": True, "replay": False}],
        })
        models[mid] = model
    path.write_text(json.dumps(models, ensure_ascii=False, indent="\t"), encoding="utf-8")

    preview = Image.new("RGBA", (S * 2, S * 6), (30, 30, 38, 255))
    for row, (_, _, filename, *_rest) in enumerate(entries):
        preview.alpha_composite(Image.open(RES / "enemy_pic" / filename), (0, row * S * 2))
    out = ROOT / "_art" / "preview" / "quest_items.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    preview.resize((S * 8, S * 24), Image.Resampling.NEAREST).save(out)


def main():
    register_models()
    gm.register_quest_items()
    print("quest item assets and %d inventory items registered" % len(gm.FQ_ITEM_IDS))


if __name__ == "__main__":
    main()
