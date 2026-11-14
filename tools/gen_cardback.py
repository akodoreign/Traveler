"""The Memory game's card back (plugin RokuganMini.sk RTMemory; user 2026-11-14: "give the card back some rokugani
personality"): black lacquer edge, a crimson field with a seigaiha wave pattern, a gold double frame and a gold
mitsudomoe crest in a ring. Original art, drawn here.
Output: resource/efx/rt_memory_back.png (256 x 288; shown at 64 x 72). Run: python -E tools/gen_cardback.py"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "efx", "rt_memory_back.png")
W, H = 256, 288
LACQUER, CRIMSON, CRIMSON_D, GOLD, GOLD_D = (18, 12, 12), (150, 30, 28), (118, 20, 22), (214, 172, 84), (150, 112, 48)


def seigaiha(d, x0, y0, x1, y1, r=18):
    """Overlapping wave scales: rows of concentric half-rings, every other row offset."""
    row = 0
    y = y1 + r
    while y > y0 - r:
        off = (r if row % 2 else 0)
        x = x0 - r + off
        while x < x1 + r:
            for k, rr in enumerate((r, r * 0.72, r * 0.44)):
                col = CRIMSON if k % 2 == 0 else CRIMSON_D
                d.pieslice([x - rr, y - rr, x + rr, y + rr], 180, 360, fill=col)
            d.arc([x - r, y - r, x + r, y + r], 180, 360, fill=(96, 16, 18), width=2)
            x += 2 * r
        y -= r * 0.62
        row += 1


def tomoe(d, cx, cy, R, col):
    """Mitsudomoe: three comma heads round the centre, each with a tail sweeping round."""
    for i in range(3):
        a = math.radians(90 + i * 120)
        hx, hy = cx + math.cos(a) * R * 0.42, cy - math.sin(a) * R * 0.42
        r = R * 0.25
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=col)
        for t in range(0, 41):                                             # the tail: a thinning sweep outward
            u = t / 40.0
            ang = a + math.radians(10 + 115 * u)
            rad = R * (0.42 + 0.52 * u)
            w = r * (1.0 - u) ** 1.3 + 1.2
            x, y = cx + math.cos(ang) * rad, cy - math.sin(ang) * rad
            d.ellipse([x - w, y - w, x + w, y + w], fill=col)


def main():
    img = Image.new("RGBA", (W, H), LACQUER + (255,))
    d = ImageDraw.Draw(img)
    m = 14
    d.rounded_rectangle([0, 0, W - 1, H - 1], 18, fill=LACQUER + (255,))
    field = Image.new("RGBA", (W, H), CRIMSON_D + (255,))
    fd = ImageDraw.Draw(field)
    seigaiha(fd, m, m, W - m, H - m)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([m, m, W - 1 - m, H - 1 - m], 10, fill=255)
    img.paste(field, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([m, m, W - 1 - m, H - 1 - m], 10, outline=GOLD, width=5)            # the gold double frame
    d.rounded_rectangle([m + 10, m + 10, W - 1 - m - 10, H - 1 - m - 10], 6, outline=GOLD_D, width=2)
    for cx, cy in ((m + 10, m + 10), (W - 1 - m - 10, m + 10), (m + 10, H - 1 - m - 10), (W - 1 - m - 10, H - 1 - m - 10)):
        d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)                             # corner studs
    cx, cy, R = W / 2, H / 2, 62
    d.ellipse([cx - R - 10, cy - R - 10, cx + R + 10, cy + R + 10], fill=LACQUER + (255,))  # the crest in a ring
    d.ellipse([cx - R - 6, cy - R - 6, cx + R + 6, cy + R + 6], outline=GOLD, width=6)
    d.ellipse([cx - R + 4, cy - R + 4, cx + R - 4, cy + R - 4], outline=GOLD_D, width=2)
    tomoe(d, cx, cy, R * 0.86, GOLD)
    glow = img.filter(ImageFilter.GaussianBlur(0.6))                                         # soften the edges a touch
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    glow.save(OUT)
    glow.save(os.path.join(HERE, "..", "_art", "preview", "rt_memory_back.png"))
    print(OUT)


if __name__ == "__main__":
    main()
