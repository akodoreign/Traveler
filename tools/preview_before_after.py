"""Before/after sheet comparison for the travelers: old v3 sheets (8x8, kept in _art/preview/agents/sprites/before)
against the current v4 sheets. Row per traveler: before (idle, walk, attack, cast, victory) | after (idle, walk, run,
main attack x2, rei, talk, victory). Run: python -E tools/preview_before_after.py
Writes _art/preview/agents/sprites/before_after.png
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402

DIR = os.path.join(g.PREVIEW, "agents", "sprites")
OLD = [0, 5, 11, 16, 24]                        # v3 layout (8 cols)


def cell(sheet, idx, cols):
    x, y = (idx % cols) * g.FW, (idx // cols) * g.FH
    return sheet.crop((x, y, x + g.FW, y + g.FH))


def main():
    Z = 3
    rows = []
    for T in g.TRAVELERS:
        old = Image.open(os.path.join(DIR, "before", "trav_%s.png" % T["key"])).convert("RGBA")
        new = Image.open(os.path.join(g.PIC, "trav_%s.png" % T["key"])).convert("RGBA")
        main_atk = g.primary_attack(T)
        nidx = [g.BLOCK_AT["idle8"][0], g.BLOCK_AT["walk8"][0] + 2, g.BLOCK_AT["run"][0] + 1,
                g.BLOCK_AT[main_atk][0] + 1, g.BLOCK_AT[main_atk][0] + 3, g.BLOCK_AT["rei"][0] + 2,
                g.BLOCK_AT["talk"][0] + 1, g.BLOCK_AT["victory2"][0] + 2]
        rows.append((T["name"], [cell(old, i, 8) for i in OLD], [cell(new, i, g.COLS) for i in nidx]))
    lw, gap = 120, 24
    W = lw + (len(OLD) + len(rows[0][2])) * g.FW * Z + gap
    H = 16 + len(rows) * g.FH * Z
    im = Image.new("RGBA", (W, H), (58, 74, 60, 255))
    d = ImageDraw.Draw(im)
    d.text((lw, 2), "BEFORE (v3)", fill=(255, 255, 255, 255))
    d.text((lw + len(OLD) * g.FW * Z + gap, 2), "AFTER (v4): idle, walk, run, attack x2, rei, talk, victory",
           fill=(255, 255, 255, 255))
    for r, (name, olds, news) in enumerate(rows):
        y = 16 + r * g.FH * Z
        d.text((4, y + 6), name, fill=(255, 255, 255, 255))
        x = lw
        for k, f in enumerate(olds + news):
            if k == len(olds):
                x += gap
            fz = f.resize((g.FW * Z, g.FH * Z), Image.NEAREST)
            im.paste(fz, (x, y), fz)
            x += g.FW * Z
    p = os.path.join(DIR, "before_after.png")
    im.save(p)
    print(p)


if __name__ == "__main__":
    main()
