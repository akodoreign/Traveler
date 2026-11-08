"""Review sheet of every bust wired into the game: one image per character (neutral, default look), on a dark
background with the dialog box's top edge marked (where the chin should sit above), labelled with the speaker name.
python -E tools/bust_review_sheet.py   ->  _art/preview/agents/busts/REVIEW_in_game.png (+ _2, _3 ... pages)"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_busts as g  # noqa: E402
sys.argv = _argv
from PIL import Image, ImageDraw  # noqa: E402

R = os.path.join(g.PROJ, "resource", "bust")
COLS, TW, TH = 8, 150, 220


def main():
    keys = [k for k in g.CHARS if os.path.exists(os.path.join(R, k, "neutral.png"))]
    pages = [keys[i:i + COLS * 5] for i in range(0, len(keys), COLS * 5)]
    f = g.label_font(14)
    for pn, ks in enumerate(pages):
        rows = (len(ks) + COLS - 1) // COLS
        sh = Image.new("RGB", (COLS * TW, rows * (TH + 34)), (30, 28, 34))
        d = ImageDraw.Draw(sh)
        for i, k in enumerate(ks):
            im = Image.open(os.path.join(R, k, "neutral.png"))
            bg = Image.new("RGBA", im.size, (52, 60, 52, 255))       # a map-ish backdrop shows keying faults
            bg.alpha_composite(im)
            t = bg.convert("RGB")
            t.thumbnail((TW, TH))
            x, y = (i % COLS) * TW, (i // COLS) * (TH + 34)
            sh.paste(t, (x + (TW - t.width) // 2, y))
            fc = json.load(open(os.path.join(R, k, "faces.json"))).get("base") if os.path.exists(
                os.path.join(R, k, "faces.json")) else None
            if fc:
                cy = y + int(fc[2] * t.height)
                d.line([(x + 4, cy), (x + TW - 4, cy)], fill=(255, 60, 60), width=1)
            nm = g.CHARS[k]["names"][0]
            tag = "" if g.CHARS[k].get("npc") else " (traveler)"
            d.text((x + 3, y + TH + 2), (nm + tag)[:22], fill=(240, 230, 200), font=f)
            d.text((x + 3, y + TH + 17), k[:24], fill=(150, 150, 160), font=f)
        out = os.path.join(g.PREVIEW, "REVIEW_in_game%s.png" % ("" if pn == 0 else "_%d" % (pn + 1)))
        sh.save(out)
        print(out)


if __name__ == "__main__":
    main()
