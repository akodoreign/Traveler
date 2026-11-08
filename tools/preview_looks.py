"""Equipment-look grid: rows = weapon looks, columns = head looks, one battle-idle frame (or --frame block[:i]) per
cell, for each traveler. Run: python -E tools/preview_looks.py [key ...] [--frame atk_slash:3] [--zoom N]
Writes _art/preview/agents/sprites/looks_<key>.png
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402

OUT = os.path.join(g.PREVIEW, "agents", "sprites")


def grid(ti, T, block, k, zoom):
    combos = g.look_combos(ti, T)
    ws = [w for w in g.LOOK_WEAPONS if any(c[2] == w for c in combos)]
    lw, th = 70, 14
    cw, ch = g.FW * zoom, g.FH * zoom
    im = Image.new("RGBA", (lw + cw * len(g.LOOK_HATS), th + ch * len(ws)), (58, 74, 60, 255))
    d = ImageDraw.Draw(im)
    for c, h in enumerate(g.LOOK_HATS):
        d.text((lw + c * cw + 4, 2), h or "(own)", fill=(255, 255, 255, 255))
    for r, w in enumerate(ws):
        d.text((4, th + r * ch + 4), w, fill=(255, 255, 255, 255))
        for c, h in enumerate(g.LOOK_HATS):
            V = g.look_variant(T, w, h)
            s, _ = g.BLOCK_AT[block]
            f = Image.fromarray(g.frame(V, *g.FRAMES[s + k]), "RGBA").resize((cw, ch), Image.NEAREST)
            im.paste(f, (lw + c * cw, th + r * ch), f)
            ep = [x[1] for x in g.look_combos(ti, T) if x[2] == w and x[3] == h]
            d.text((lw + c * cw + 4, th + r * ch + ch - 12), ep[0] if ep else "", fill=(220, 230, 200, 255))
    return im


def main():
    args = sys.argv[1:]
    block, k, zoom, keys = "idle8", 0, 2, []
    i = 0
    while i < len(args):
        if args[i] == "--frame":
            block, _, kk = args[i + 1].partition(":")
            k = int(kk or 0); i += 2; continue
        if args[i] == "--zoom":
            zoom = int(args[i + 1]); i += 2; continue
        keys.append(args[i]); i += 1
    os.makedirs(OUT, exist_ok=True)
    for ti, T in enumerate(g.TRAVELERS):
        if keys and T["key"] not in keys:
            continue
        p = os.path.join(OUT, "looks_%s%s.png" % (T["key"], "" if block == "idle8" else "_" + block))
        grid(ti, T, block, k, zoom).save(p)
        print(p)


if __name__ == "__main__":
    main()
