"""Animation-strip previews for the v4 sprite sheets (gen_sprites2d BLOCKS): one labelled row per block.
Run: python -E tools/preview_anims.py [key ...] [--zoom N] [--blocks a,b,c] [--out DIR] [--weapon W] [--hat H]
Writes <out>/anim_<key>.png (default out: _art/preview/agents/sprites).
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402

OUT = os.path.join(g.PREVIEW, "agents", "sprites")
BG = (58, 74, 60, 255)


def strip_rows(T, blocks, zoom):
    rows = []
    for name in blocks:
        s, n = g.BLOCK_AT[name]
        frames = [g.frame(T, *g.FRAMES[s + k]) for k in range(n)]
        rows.append((name, frames))
    maxn = max(len(f) for _, f in rows)
    lw = 96
    W, H = lw + maxn * g.FW * zoom, len(rows) * g.FH * zoom
    im = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(im)
    for r, (name, frames) in enumerate(rows):
        y = r * g.FH * zoom
        if r % 2:
            d.rectangle((0, y, W, y + g.FH * zoom - 1), fill=(64, 82, 66, 255))
        d.text((4, y + 4), name, fill=(255, 255, 255, 255))
        for k, f in enumerate(frames):
            fi = Image.fromarray(f, "RGBA").resize((g.FW * zoom, g.FH * zoom), Image.NEAREST)
            im.paste(fi, (lw + k * g.FW * zoom, y), fi)
    return im


def main():
    args = sys.argv[1:]
    zoom, blocks, out, weapon, hat = 3, [b for b, _ in g.BLOCKS], OUT, None, None
    keys = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--zoom":
            zoom = int(args[i + 1]); i += 2; continue
        if a == "--blocks":
            blocks = args[i + 1].split(","); i += 2; continue
        if a == "--out":
            out = args[i + 1]; i += 2; continue
        if a == "--weapon":
            weapon = args[i + 1]; i += 2; continue
        if a == "--hat":
            hat = args[i + 1]; i += 2; continue
        keys.append(a)
        i += 1
    os.makedirs(out, exist_ok=True)
    trav = {t["key"]: t for t in g.TRAVELERS}
    for key in keys or list(trav):
        T = trav[key]
        if weapon or hat is not None:
            T = g.look_variant(T, weapon or g.base_look(T)[0], hat if hat is not None else "")
        im = strip_rows(T, blocks, zoom)
        suffix = ("_" + weapon if weapon else "") + ("_" + hat if hat else "")
        p = os.path.join(out, "anim_%s%s.png" % (key, suffix))
        im.save(p)
        print(p)


if __name__ == "__main__":
    main()
