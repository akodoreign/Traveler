"""The little ship the player sails the sea maps as (user 2026-11-14: "zoom out from the junk and get ocean maps ...
the little ship"). A junk: dark hull, a battened cream sail on one mast, a red pennant; two frames (it bobs). Drawn in
the travelers' 80 x 68 frame so it sits at their scale. Output resource/enemy_pic/sea_junk.png + enemy_pic EP2650
(every field animation id points at the two frames: standing, walking and running all bob).
Run: python -E tools/gen_ship_sprite.py"""
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
FW, FH = 80, 68
OUTLINE, HULL, HULL_L, DECK = (34, 22, 16, 255), (104, 64, 38, 255), (138, 90, 52, 255), (166, 120, 72, 255)
SAIL, SAIL_D, BATTEN, MAST, RED = (236, 222, 186, 255), (204, 186, 146, 255), (118, 86, 52, 255), (70, 46, 28, 255), \
    (196, 52, 40, 255)


def frame(dy):
    im = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base = 58 + dy
    hull = [(8, base - 12), (72, base - 12), (66, base - 2), (16, base - 2)]       # the hull, bow to the right
    d.polygon(hull, fill=HULL, outline=OUTLINE)
    d.line([(10, base - 9), (70, base - 9)], fill=HULL_L, width=2)
    d.polygon([(64, base - 12), (76, base - 18), (72, base - 12)], fill=HULL, outline=OUTLINE)   # the raised bow
    d.polygon([(8, base - 12), (6, base - 17), (16, base - 17), (18, base - 12)], fill=HULL, outline=OUTLINE)  # stern
    d.rectangle([12, base - 14, 66, base - 12], fill=DECK)
    d.rectangle([37, base - 52, 39, base - 13], fill=MAST)                         # the mast
    sail = [(22, base - 48), (54, base - 50), (58, base - 18), (18, base - 16)]    # the battened junk sail
    d.polygon(sail, fill=SAIL, outline=OUTLINE)
    d.polygon([(38, base - 49), (54, base - 50), (58, base - 18), (38, base - 17)], fill=SAIL_D)
    for k in range(1, 5):
        y = base - 48 + k * 6.5
        d.line([(21 - k * 0.3, y), (55 + k, y - 1)], fill=BATTEN, width=1)
    d.polygon([(39, base - 52), (50, base - 55 + (1 if dy else 0)), (39, base - 50)], fill=RED)   # the pennant
    return im


def main():
    sheet = Image.new("RGBA", (FW * 2, FH), (0, 0, 0, 0))
    sheet.alpha_composite(frame(0), (0, 0))
    sheet.alpha_composite(frame(1), (FW, 0))
    out = os.path.join(RES, "enemy_pic", "sea_junk.png")
    sheet.save(out)
    sheet.resize((FW * 6, FH * 3), Image.NEAREST).save(os.path.join(HERE, "..", "_art", "preview", "sea_junk.png"))
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    e = json.loads(json.dumps(j["EP200"]))                     # a traveler's entry: same scale and ground point
    ids = sorted({a["id"] for a in e["animap"]})
    e.update({"name": {"en": "Your ship", "ja": "Your ship"}, "pic3d": "/resource/enemy_pic/sea_junk.png",
              "aniuv": [2, 1], "memo": "the player's ship on the sea maps (tools/gen_ship_sprite.py)",
              "animap": [{"id": i, "st": 0, "en": 2, "spd": 1.2, "loop": True, "replay": False} for i in ids]})
    j["EP2650"] = e
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print(out, len(ids), "animation ids")


if __name__ == "__main__":
    main()
