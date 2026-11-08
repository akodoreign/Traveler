"""Preview sheets for the cast: idle / wind-up / strike per character, 4 per row.
Run: python -E tools/preview_cast.py   -> _art/preview/travelers_final.png, sidecast_final.png"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sidecast as sc  # noqa: E402
import gen_sprites2d as g  # noqa: E402


def strip(Ts, names, path, per=4):
    cw, ch = g.FW * 3, g.FH + 4
    rows = (len(Ts) + per - 1) // per
    im = Image.new("RGBA", (cw * per, ch * rows), (64, 90, 58, 255))
    d = ImageDraw.Draw(im)
    for n, T in enumerate(Ts):
        r, c = n // per, n % per
        for k, (kind, i) in enumerate((("idle", 0), ("attack", 0), ("attack", 1))):
            f = Image.fromarray(g.frame(T, kind, i), "RGBA")
            im.paste(f, (c * cw + k * g.FW, r * ch - 6), f)
        d.text((c * cw + 4, r * ch + g.FH - 10), names[n], fill=(255, 255, 255, 255))
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(path)


if __name__ == "__main__":
    strip(g.TRAVELERS, [T["name"] for T in g.TRAVELERS], os.path.join(g.PREVIEW, "travelers_final.png"))
    strip([sc.config(c) for c in sc.CAST], [c["name"] for c in sc.CAST], os.path.join(g.PREVIEW, "sidecast_final.png"))
    print("ok")
