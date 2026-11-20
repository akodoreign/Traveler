"""Export the text-free ink and crest treatments for the combat boss titles."""
from argparse import ArgumentParser
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw

W, H = 960, 190
THEMES = {
    "ink": ((27, 21, 26), (185, 143, 84)),
    "nezumi": ((43, 34, 28), (227, 182, 104)),
    "orochi": ((25, 35, 44), (121, 193, 204)),
    "okura": ((54, 23, 28), (234, 130, 83)),
    "kommei": ((44, 24, 42), (221, 142, 153)),
    "tsukakoro": ((30, 40, 37), (187, 203, 155)),
    "yasurugi": ((29, 42, 57), (164, 209, 220)),
    "nashiko": ((52, 31, 42), (232, 165, 167)),
    "empress": ((44, 28, 36), (237, 192, 110)),
}


def crest(draw, theme, center, accent):
    cx, cy = center
    faint = (*accent, 102)
    solid = (*accent, 204)

    def line(*points, color=solid, width=2):
        draw.line([(cx + x, cy + y) for x, y in points], fill=color, width=width, joint="curve")

    def oval(box, start=0, end=360, color=solid, width=2):
        x0, y0, x1, y1 = box
        draw.arc((cx+x0, cy+y0, cx+x1, cy+y1), start=start, end=end, fill=color, width=width)

    oval((-28, -28, 28, 28), color=faint)
    if theme == "nezumi":
        line((-13, 18), (-13, -16), (-7, -23), (0, -19), (2, -10), (-7, -6))
        line((4, 19), (4, -12), (10, -19), (17, -13), (17, -7), (9, -2))
        line((-17, 5), (20, 5), color=faint)
    elif theme == "orochi":
        oval((-19, -17, 14, 3), 5, 297, width=3)
        oval((-7, -3, 19, 17), 155, 440, width=3)
        line((-11, 3), (-17, 10), (-21, 9))
    elif theme == "okura":
        line((-21, -18), (-14, -5), (-7, 0), (0, -3), (7, 0), (14, -5), (21, -18), width=3)
        line((-16, -1), (-15, 10), (-9, 17), (0, 21), (9, 17), (15, 10), (16, -1))
        line((-10, 4), (-4, 7))
        line((10, 4), (4, 7))
    elif theme == "kommei":
        line((-20, -13), (-13, -18), (-3, -15), (0, -7), (-3, 10), (-11, 19), (-18, 9), (-20, -13))
        line((0, -7), (6, -15), (15, -17), (21, -12), (18, 8), (11, 19), (3, 11), (0, -7))
        line((-15, -6), (-9, -4), color=faint)
        line((9, -4), (15, -6), color=faint)
    elif theme == "tsukakoro":
        for y, eye in ((-16, -14), (0, -17), (16, -14)):
            line((eye, y), (0, y + 6), (-eye, y))
        line((0, -22), (0, 22), color=faint)
    elif theme == "yasurugi":
        line((-14, 16), (13, -14), (17, -19), (18, -10), (-9, 19), width=3)
        line((-18, 8), (-7, 18))
        line((-21, 19), (-16, 24), color=faint)
    elif theme == "nashiko":
        oval((-17, -16, 17, 16), 180, 360)
        line((-22, 0), (22, 0))
        line((-19, 12), (-12, 8), (-5, 14), (5, 5), (12, 9), (20, 4))
    elif theme == "empress":
        oval((-17, -17, 17, 17), 9, 331, width=3)
        oval((-12, -17, 17, 12), 100, 275, color=faint)
        line((-22, 22), (0, 16), (22, 22))
        line((0, -25), (0, -19), color=faint)


def backdrop(theme, pigment, accent):
    rng = Random(theme)
    buf = Image.new("RGBA", (W, H))
    pixels = []
    for y in range(H):
        depth = abs(y - 95.0) / 57.0
        for x in range(W):
            edge = min(x, W-1-x)
            fade = min(1., max(0., (edge - 14. - 116.*depth**1.9) / 94.))
            rim = min(1., max(0., (1. - depth)*7.))
            alpha = int(245 * fade * rim)
            grain = rng.randrange(-5, 6)
            pixels.append(tuple(max(0, c+grain) for c in pigment) + (alpha,))
    buf.putdata(pixels)

    ink = Image.new("RGBA", buf.size)
    draw = ImageDraw.Draw(ink)
    for _ in range(530):
        x = rng.randrange(46, 914)
        y = rng.randrange(46, 144)
        if not pixels[y*W+x][3]:
            continue
        length = rng.randrange(3, 52)
        a = rng.randrange(5, 34)
        draw.line((x, y, min(924, x+length), y), fill=(*accent, a))
    draw.line((168, 49, 792, 49), fill=(*accent, 99), width=1)
    draw.line((205, 137, 755, 137), fill=(*accent, 132), width=1)
    draw.line((281, 141, 679, 141), fill=(*accent, 55), width=1)
    if theme != "ink":
        crest(draw, theme, (122, 94), accent)
        crest(draw, theme, (838, 94), accent)
        draw.polygon(((170, 94), (177, 87), (184, 94), (177, 101)), fill=(*accent, 145))
        draw.polygon(((776, 94), (783, 87), (790, 94), (783, 101)), fill=(*accent, 145))
    return Image.alpha_composite(buf, ink)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for theme, (pigment, accent) in THEMES.items():
        backdrop(theme, pigment, accent).save(args.output / (theme + ".png"))
