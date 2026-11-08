"""The world map (Octopath-style fast-travel screen), painted from the overworld sketch in
docs/story/storyboards/README.md section 4a. Every character cell of the sketch becomes terrain:
  ^ mountains   % forest   ~ sea   # the Kaiu Wall   = road   [XX] a node   CLAN NAMES tint their lands
Output: resource/enemy_pic/worldmap.png (1280x720, shown with cmd_showpic) + enemy_pic EP360, and
data/rt_worldmap.json (node -> pixel position, name) for the travel menu (tools/gen_maps.py).
Run: python -E tools/gen_worldmap.py
"""
import json
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
DATA = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data")
PREVIEW = os.path.join(HERE, "..", "_art", "preview")
README = os.path.join(HERE, "..", "docs", "story", "storyboards", "README.md")
W, H = 1280, 720
FONT = "C:/Windows/Fonts/georgia.ttf"
FONTB = "C:/Windows/Fonts/georgiab.ttf"
FONTI = "C:/Windows/Fonts/georgiai.ttf"

CLANS = {"CRAB": (92, 104, 122), "CRANE": (120, 160, 196), "LION": (202, 164, 72), "PHOENIX": (214, 112, 62),
         "DRAGON": (84, 140, 96), "SCORPION": (176, 62, 58), "UNICORN": (140, 96, 160), "MANTIS": (78, 150, 132)}
NODE_NAMES = {
    "HI": "Hoshi-no-Ichi", "KW": "Kaiu Wall", "KH": "Kyuden Hida", "TI": "Tortoise Isle", "IS": "Isle of Silk",
    "KG": "Kyuden Gusai", "YY": "Yasuki Yashiki", "GS": "Garden Under Shadow", "KU": "Kudo", "FF": "Floating Flowers",
    "RO": "Ryoko Owari", "KB": "Kyuden Bayushi", "SS": "Shiro no Soshi", "CM": "City of Masks", "KA": "Kakita Academy",
    "KD": "Kyuden Doji", "CP": "Crane port", "CK": "Cakon", "PT": "Plains of Thunder", "VP": "Beiden Pass",
    "OJ": "Ojatara", "KZ": "Kaze-no-Tani", "TR": "Toshi Ranbo", "MR": "Magonojo", "SP": "Sorrow's Path",
    "OU": "Otosan Uchi", "WL": "Wounded Lion", "SA": "Shiro Akodo", "BB": "Burned Bridge", "HC": "Hiruto's castle",
    "ZU": "Zumiki", "TC": "Treaty City", "SI": "Shiro Iuchi", "KM": "Shiro no Kamatori", "DM": "Dragon mtn town",
    "SK": "Shiro Kitsuki", "KI": "Kyuden Isawa", "IM": "Isawa Mori", "CT": "Coast temple", "KT": "Kyuden Togashi",
    "TF": "Tamori's Furnace", "OV": "Oracle's volcano", "RT": "Red torii cliff",
}


def sketch():
    txt = open(README, encoding="utf-8").read()
    a = txt.index("### 4a. Sketch")
    block = txt[txt.index("```", a) + 3:]
    block = block[block.index("\n") + 1:block.index("```")]
    lines = block.rstrip("\n").split("\n")
    cols = max(len(l) for l in lines)
    return [l.ljust(cols) for l in lines], cols, len(lines)


def main():
    lines, cols, rows = sketch()
    mx, my, cw, ch = 30, 46, (W - 60) / cols, (H - 80) / rows
    cell = lambda c, r: (mx + (c + 0.5) * cw, my + (r + 0.5) * ch)  # noqa: E731
    # ---- terrain fields from the sketch characters
    sea = np.zeros((rows, cols), float)
    mtn = np.zeros((rows, cols), float)
    forest = np.zeros((rows, cols), float)
    wall = np.zeros((rows, cols), float)
    road = []
    for r, l in enumerate(lines):
        for c, ch_ in enumerate(l):
            sea[r, c] = ch_ == "~"
            mtn[r, c] = ch_ == "^"
            forest[r, c] = ch_ == "%"
            wall[r, c] = ch_ == "#"
            if ch_ == "=":
                road.append((c, r))
    sea[-1:, :] = np.maximum(sea[-1:, :], 0)

    def field(a, blur):
        im = Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        return np.array(im.filter(ImageFilter.GaussianBlur(blur))).astype(float) / 255.0

    # the sea: everything east of the last land char on each row that has ~, plus the far south-east
    seaf = field(sea, 18)
    rng = np.random.default_rng(11)
    noise = np.array(Image.fromarray((rng.random((90, 160)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                     .filter(ImageFilter.GaussianBlur(6))).astype(float) / 255.0
    is_sea = (seaf + (noise - 0.5) * 0.35) > 0.32
    # ---- clan tint (nearest clan label)
    labels = []
    for r, l in enumerate(lines):
        for name in CLANS:
            for m in re.finditer(r"\b%s\b" % name, l):
                labels.append((name, cell(m.start() + len(name) / 2, r)))
    YY, XX = np.mgrid[0:H, 0:W]
    best = np.full((H, W), 1e9)
    clan = np.zeros((H, W, 3))
    for name, (lx, ly) in labels:
        d = np.hypot(XX - lx, (YY - ly) * 1.25)
        msk = d < best
        best[msk] = d[msk]
        clan[msk] = CLANS[name]
    clan = np.array(Image.fromarray(clan.astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))).astype(float)
    parchment = np.array([226, 210, 172], float)
    base = parchment * 0.62 + clan * 0.38
    base *= (0.94 + noise[..., None] * 0.12)
    # shadowlands: south-west beyond the Wall, dark and sick
    swall = [(c, r) for r, l in enumerate(lines) for c, ch_ in enumerate(l) if ch_ == "#"]
    wall_y = max(cell(c, r)[1] for c, r in swall) if swall else H
    sh = ((YY - (wall_y + 6)) / 30.0 + (W * 0.55 - XX) / 120.0 + (noise - 0.5) * 2.0)
    shadow = np.clip(np.minimum((YY - (wall_y + 4)) / 18.0, (W * 0.55 - XX) / 60.0) + (noise - 0.5) * 0.8, 0, 1)
    base = base * (1 - shadow[..., None] * 0.7) + np.array([70, 40, 52]) * (shadow[..., None] * 0.7)
    img = base.copy()
    sea_col = np.array([58, 96, 128], float) * (0.9 + noise[..., None] * 0.2)
    img[is_sea] = sea_col[is_sea]
    coast = is_sea & ~np.array(Image.fromarray(is_sea.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(9))) > 0
    img[coast] = img[coast] * 0.7 + np.array([150, 180, 196]) * 0.3
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(out, "RGBA")
    # ---- forests and mountains as painted marks
    for r, l in enumerate(lines):
        for c, ch_ in enumerate(l):
            x, y = cell(c, r)
            if is_sea[min(int(y), H - 1), min(int(x), W - 1)]:
                continue
            j = rng.uniform(-3, 3)
            if ch_ == "^":
                hgt = rng.uniform(10, 16)
                d.polygon([(x - 8 + j, y + 5), (x + j, y + 5 - hgt), (x + 8 + j, y + 5)], fill=(118, 104, 92, 255),
                          outline=(70, 58, 52, 255))
                d.polygon([(x + j, y + 5 - hgt), (x + 2.5 + j, y + 5 - hgt * 0.55), (x - 2 + j, y + 5 - hgt * 0.6)],
                          fill=(236, 232, 226, 255))
            elif ch_ == "%":
                for k in range(2):
                    fx, fy = x + rng.uniform(-6, 6), y + rng.uniform(-6, 4)
                    d.ellipse([fx - 6, fy - 6, fx + 6, fy + 5], fill=(54, 92, 58, 230), outline=(34, 60, 38, 255))
    # ---- the Kaiu Wall
    if swall:
        pts = sorted(cell(c, r) for c, r in swall)
        d.line([(pts[0][0] - 10, wall_y), (pts[-1][0] + 40, wall_y)], fill=(60, 64, 76, 255), width=7)
        for x in range(int(pts[0][0] - 10), int(pts[-1][0] + 40), 10):
            d.rectangle([x, wall_y - 7, x + 4, wall_y - 3], fill=(60, 64, 76, 255))
    # ---- nodes
    nodes = {}
    for r, l in enumerate(lines):
        for m in re.finditer(r"\[([A-Z]{2})\]", l):
            code = m.group(1)
            nodes[code] = cell(m.start() + 1.5, r)
    # roads: chain consecutive '=' cells into dotted lines
    for (c, r) in road:
        x, y = cell(c, r)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(120, 84, 52, 200))
    f_node = ImageFont.truetype(FONT, 15)
    f_clan = ImageFont.truetype(FONTB, 30)
    f_title = ImageFont.truetype(FONTI, 22)
    for name, (lx, ly) in labels:
        if lx < W - 40:
            col = tuple(int(v * 0.55) for v in CLANS[name]) + (150,)
            lx = min(max(lx, 140), W - 160)
            d.text((lx, ly), name.title() + " lands", font=f_clan, fill=col, anchor="mm")
    f_reg = ImageFont.truetype(FONTI, 20)
    d.text((170, wall_y + 34), "the Shadowlands", font=f_reg, fill=(214, 150, 160, 220), anchor="mm")
    d.text((120, 470), "Shinomen Mori", font=f_reg, fill=(34, 60, 38, 230), anchor="mm")
    meta = {}
    for code, (x, y) in nodes.items():
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(250, 240, 214, 255), outline=(60, 40, 30, 255), width=2)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(170, 40, 36, 255))
        nm = NODE_NAMES.get(code, code)
        d.text((x + 10, y - 9), nm, font=f_node, fill=(30, 20, 16, 255), stroke_width=2,
               stroke_fill=(240, 230, 204, 255))
        meta[code] = {"name": nm, "x": round(x), "y": round(y)}
    d.text((W - 20, 22), "Rokugan - the Emerald Empire, winter 1122", font=f_title, fill=(50, 34, 24, 255),
           anchor="rm")
    # frame + vignette
    v = np.array(out).astype(float)
    nx, ny = (XX + 0.5) / W * 2 - 1, (YY + 0.5) / H * 2 - 1
    vig = np.clip(1.15 - 0.35 * (nx ** 2 + ny ** 2), 0.6, 1.0)
    v = v * vig[..., None]
    out = Image.fromarray(np.clip(v, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(out)
    d.rectangle([4, 4, W - 5, H - 5], outline=(60, 40, 30), width=4)
    d.rectangle([12, 12, W - 13, H - 13], outline=(150, 120, 80), width=1)
    path = os.path.join(RES, "enemy_pic", "worldmap.png")
    out.save(path)
    out.save(os.path.join(PREVIEW, "worldmap.png"))
    # resource entry (shown with cmd_showpic)
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    e = json.loads(json.dumps(j["EP000"]))
    e.update({"name": {"en": "World map", "ja": "World map"}, "pic3d": "/resource/enemy_pic/worldmap.png",
              "aniuv": [1, 1], "memo": "world map (tools/gen_worldmap.py)", "gndpos": [0.5, 0.5], "scale": 1.0,
              "flipx": False, "animap": [{"id": "stand", "st": 0, "en": 1, "spd": 1.0, "loop": True,
                                          "replay": False}]})
    j["EP360"] = e
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    json.dump(meta, open(os.path.join(DATA, "rt_worldmap.json"), "w", encoding="utf-8"), indent=1)
    print(path, len(nodes), "nodes")


if __name__ == "__main__":
    main()
