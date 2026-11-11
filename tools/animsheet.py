"""One row per animation of a sprite (user, 2026-11-11: "bad animation frames ... like the togashi's head"): the frames
each animation actually plays, in order, labelled, so a frame that breaks the loop (a back-of-head frame in an idle,
a frame facing the other way) stands out.
python -E tools/animsheet.py EP309 [EP200 ...]      -> _art/preview/anim/EPxxx.png"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
OUT = os.path.join(HERE, "..", "_art", "preview", "anim")


def sheet(epid):
    pics = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
    e = pics[epid]
    src = e["pic3d"]
    im = Image.open(os.path.join(RES, "enemy_pic", os.path.basename(src))).convert("RGBA")
    cols, rows = e.get("aniuv") or (14, 11)
    fw, fh = im.size[0] // cols, im.size[1] // rows
    frames = [im.crop(((i % cols) * fw, (i // cols) * fh, (i % cols + 1) * fw, (i // cols + 1) * fh))
              for i in range(cols * rows)]
    anims = [a for a in e.get("animap", []) if isinstance(a, dict) and "st" in a]
    width = max(a["en"] - a["st"] for a in anims) if anims else cols
    s = 2
    out = Image.new("RGB", (90 + width * fw * s, len(anims) * fh * s), (90, 140, 90))
    d = ImageDraw.Draw(out)
    for r, a in enumerate(anims):
        d.text((4, r * fh * s + 4), "%s\n%d-%d" % (a["id"], a["st"], a["en"]), fill=(255, 255, 255))
        for k, i in enumerate(range(a["st"], a["en"])):
            if i < len(frames):
                f = frames[i].resize((fw * s, fh * s), Image.NEAREST)
                out.paste(f, (90 + k * fw * s, r * fh * s), f)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, epid + ".png")
    out.save(p)
    return p, src, (cols, rows, fw, fh)


if __name__ == "__main__":
    for ep in sys.argv[1:]:
        print(*sheet(ep))
