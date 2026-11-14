"""The floating quest marker (plugin RokuganMarker.sk; user 2026-11-14: "a white/silver sparkly cross mixed with a
star"): a four-point silver star over a thin cross, a soft glow and two small sparkles. Original art, drawn here.
Output: resource/enemy_pic/questmarker.png + enemy_pic EP361 (a picture model, faces the camera).
Run: python -E tools/gen_questmarker.py"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
S = 128


def star(d, cx, cy, r_long, r_short, col, rot=0.0):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4
        r = r_long if i % 2 == 0 else r_short
        pts.append((cx + math.sin(a) * r, cy - math.cos(a) * r))
    d.polygon(pts, fill=col)


def main():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([S * 0.18, S * 0.18, S * 0.82, S * 0.82], fill=(200, 220, 255, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    c = S / 2
    d.rectangle([c - 2, S * 0.06, c + 2, S * 0.94], fill=(235, 240, 250, 230))             # the cross, thin
    d.rectangle([S * 0.06, c - 2, S * 0.94, c + 2], fill=(235, 240, 250, 230))
    star(d, c, c, S * 0.40, S * 0.10, (220, 228, 240, 255))                                # the silver star
    star(d, c, c, S * 0.26, S * 0.07, (255, 255, 255, 255), rot=math.pi / 4)               # a white one inside
    d.ellipse([c - 7, c - 7, c + 7, c + 7], fill=(255, 255, 255, 255))
    for (x, y, r) in ((S * 0.80, S * 0.22, 9), (S * 0.22, S * 0.78, 7)):                   # two small sparkles
        star(d, x, y, r, r * 0.25, (255, 255, 255, 240))
    a = np.array(img)
    out = os.path.join(RES, "enemy_pic", "questmarker.png")
    Image.fromarray(a).save(out)
    Image.fromarray(a).save(os.path.join(HERE, "..", "_art", "preview", "questmarker.png"))
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    e = json.loads(json.dumps(j["EP360"] if "EP360" in j else j["EP000"]))
    e.update({"name": {"en": "Quest marker", "ja": "Quest marker"}, "pic3d": "/resource/enemy_pic/questmarker.png",
              "aniuv": [1, 1], "memo": "quest marker (tools/gen_questmarker.py)", "gndpos": [0.5, 0.5], "scale": 0.0875,   # (user: "about 1/4 the size")
              "flipx": False, "animap": [{"id": "stand", "st": 0, "en": 1, "spd": 1.0, "loop": True, "replay": False}]})
    j["EP361"] = e
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print(out)


if __name__ == "__main__":
    main()
