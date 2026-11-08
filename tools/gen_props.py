"""Static pixel-art props used as map objects (picture models, enemy_pic EP350+).
EP350 supply cart (Crab Ch1 escort: rice sacks, a barrel of pickled radish). EP356 palanquin (Crane Ch1: Lady Sanae). EP352 egg heap, EP353 painted eggs, EP355 campfire (4 flicker frames). (Nezumi EP351/EP354: tools/gen_nezumi.py.)
Run after gen_sidecast.py:  python -E tools/gen_props.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402

W, H = 80, 68   # same canvas as gen_sprites2d (its shading helpers assume FW x FH)


def cart():
    cv = np.zeros((H, W, 4), np.uint8)

    class C:
        col = cv
    c = g.Canvas()
    c.col = cv
    YY, XX = np.mgrid[0:H, 0:W]
    wood, dark, straw = g.ramp((140, 94, 54)), g.ramp((70, 50, 36)), g.ramp((214, 184, 110))
    sack, rope, barrel = g.ramp((200, 186, 150)), g.ramp((150, 120, 80)), g.ramp((120, 80, 50))
    radish = g.ramp((236, 230, 200))
    gy = H - 4
    # bed
    bed = (XX >= 10) & (XX <= 62) & (YY >= gy - 20) & (YY <= gy - 15)
    t = np.full((H, W), 2)
    t[bed & (YY == gy - 20)] = 3
    t[bed & (XX % 8 == 0)] = 1
    c.paste(bed, g.finish_tones(bed, t, True), wood)
    # side rails
    for x in (12, 60):
        r = (XX >= x) & (XX <= x + 1) & (YY >= gy - 26) & (YY <= gy - 15)
        c.paste(r, g.shade_rows(r), dark)
    # load: sacks + barrel
    for cx, cy, rx, ry in ((22, gy - 26, 8, 6), (33, gy - 27, 8, 7), (28, gy - 34, 7, 5)):
        m = ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2 <= 1
        tt = g.shade_rows(m)
        tt[m & (YY == cy) & (abs(XX - cx) < rx - 1)] = 1
        c.paste(m, tt, sack)
        c.px(cx, cy - ry + 1, rope[1]), c.px(cx + 1, cy - ry + 1, rope[1])
    bar = (XX >= 44) & (XX <= 56) & (YY >= gy - 34) & (YY <= gy - 21)
    tt = g.shade_rows(bar)
    tt[bar & ((YY == gy - 31) | (YY == gy - 24))] = 0
    c.paste(bar, tt, barrel)
    top = ((XX - 50) / 6.5) ** 2 + ((YY - (gy - 34)) / 2.0) ** 2 <= 1
    c.paste(top, g.shade_rows(top), barrel)
    for k in range(3):                                   # radishes poking out
        x = 47 + k * 3
        rr = (XX >= x) & (XX <= x + 1) & (YY >= gy - 39) & (YY <= gy - 34)
        c.paste(rr, g.shade_rows(rr, outline=False), radish)
        c.px(x, gy - 40, (90, 150, 70)), c.px(x + 1, gy - 41, (70, 130, 60))
    # shafts
    for y in (gy - 17,):
        sh = (XX >= 62) & (XX <= 78) & (YY >= y) & (YY <= y + 1)
        c.paste(sh, g.shade_rows(sh, dither=False), wood)
    # wheels
    for cx in (22, 50):
        wheel = ((XX - cx) ** 2 + (YY - (gy - 7)) ** 2 <= 8.5 ** 2) & ((XX - cx) ** 2 + (YY - (gy - 7)) ** 2 >= 6 ** 2)
        c.paste(wheel, g.shade_rows(wheel, dither=False), dark)
        for a in range(0, 180, 45):
            import math
            dx, dy = math.cos(math.radians(a)) * 6, math.sin(math.radians(a)) * 6
            g.line(c, (cx - dx, gy - 7 - dy), (cx + dx, gy - 7 + dy), wood, 1)
        hub = (XX - cx) ** 2 + (YY - (gy - 7)) ** 2 <= 2.2 ** 2
        c.paste(hub, g.shade_rows(hub), straw)
    g.outline_outer(c)
    sh = ((XX - 40) / 30.0) ** 2 + ((YY - (gy + 1)) / 2.5) ** 2 <= 1
    cv[sh & (cv[..., 3] == 0)] = (0, 0, 0, 70)
    return Image.fromarray(cv, "RGBA")


def palanquin():
    """EP356: a plain norimono (Crane Ch1: Lady Doji Sanae's travelling box): black lacquer, gold trim, a sliding
    shoji window, a white Crane mon, and the carrying pole through the roof."""
    cv = np.zeros((H, W, 4), np.uint8)
    c = g.Canvas()
    c.col = cv
    YY, XX = np.mgrid[0:H, 0:W]
    lac, gold, paper = g.ramp((44, 38, 46)), g.ramp((214, 176, 70)), g.ramp((236, 230, 210))
    wood, white = g.ramp((140, 94, 54)), g.ramp((240, 240, 246))
    gy = H - 4
    box = (XX >= 20) & (XX <= 58) & (YY >= gy - 32) & (YY <= gy - 7)
    c.paste(box, g.shade_rows(box), lac)
    for y in (gy - 31, gy - 8):                                     # gold bands top and bottom
        band = box & (YY >= y) & (YY <= y + 1)
        c.paste(band, g.shade_rows(band, outline=False, dither=False), gold)
    win = (XX >= 31) & (XX <= 47) & (YY >= gy - 26) & (YY <= gy - 14)
    t = g.shade_rows(win, outline=False, dither=False)
    t[win & (((XX - 31) % 4 == 0) | ((YY - (gy - 26)) % 4 == 0))] = 0  # shoji lattice
    c.paste(win, t, paper)
    mon = ((XX - 53) ** 2 + (YY - (gy - 20)) ** 2 <= 2.6 ** 2)       # Crane mon (a white roundel)
    c.paste(mon, g.shade_rows(mon, outline=False, dither=False), white)
    roof = (YY >= gy - 38) & (YY <= gy - 33) & (XX >= 16 - (YY - (gy - 38))) & (XX <= 62 + (YY - (gy - 38)))
    c.paste(roof, g.shade_rows(roof), lac)
    edge = roof & (YY == gy - 33)
    c.paste(edge, g.shade_rows(edge, outline=False, dither=False), gold)
    pole = (XX >= 1) & (XX <= 78) & (YY >= gy - 41) & (YY <= gy - 40)
    c.paste(pole, g.shade_rows(pole, dither=False), wood)
    for x in (24, 54):                                               # pole brackets
        br = (XX >= x) & (XX <= x + 1) & (YY >= gy - 40) & (YY <= gy - 38)
        c.paste(br, g.shade_rows(br, outline=False, dither=False), gold)
    for x in (22, 54):                                               # little feet
        ft = (XX >= x) & (XX <= x + 2) & (YY >= gy - 7) & (YY <= gy - 4)
        c.paste(ft, g.shade_rows(ft, dither=False), lac)
    g.outline_outer(c)
    sh = ((XX - 40) / 30.0) ** 2 + ((YY - (gy + 1)) / 2.5) ** 2 <= 1
    cv[sh & (cv[..., 3] == 0)] = (0, 0, 0, 70)
    return Image.fromarray(cv, "RGBA")


def campfire(k):
    """A camp's cooking fire: ring of stones, crossed logs, a layered flame that flickers (k = 0..3), sparks."""
    cv = np.zeros((H, W, 4), np.uint8)
    c = g.Canvas()
    c.col = cv
    YY, XX = np.mgrid[0:H, 0:W]
    stone, log, ash = g.ramp((128, 124, 118)), g.ramp((96, 64, 40)), g.ramp((70, 60, 56))
    gy, cx = H - 4, 40
    bed = ((XX - cx) / 8.5) ** 2 + ((YY - (gy - 1)) / 2.6) ** 2 <= 1            # ash bed
    c.paste(bed, g.shade_rows(bed, dither=False), ash)
    for a in range(0, 360, 40):                                                # ring of stones (back half first)
        x = cx + 8.5 * np.cos(np.radians(a))
        y = gy - 1 + 2.6 * np.sin(np.radians(a))
        if np.sin(np.radians(a)) < 0:
            st = ((XX - x) / 2.0) ** 2 + ((YY - y) / 1.5) ** 2 <= 1
            c.paste(st, g.shade_rows(st), stone)
    for (x0, y0, x1, y1) in ((cx - 7, gy - 1, cx + 5, gy - 6), (cx + 7, gy - 1, cx - 5, gy - 6),
                             (cx - 2, gy, cx + 1, gy - 7)):                     # crossed logs
        g.line(c, (x0, y0), (x1, y1), log, 2)
    flick = [0.0, 1.0, -0.5, 0.6][k]
    sway = [0, 1, 0, -1][k]
    for col, rx, ry, top in (((214, 60, 30), 5.0, 9.5 + flick, 0.0), ((244, 130, 40), 3.7, 7.5 + flick, 0.6),
                             ((255, 206, 90), 2.3, 5.0 + flick * 0.6, 1.0), ((255, 250, 220), 1.0, 2.5, 1.4)):
        fy = gy - 3 - ry * 0.55
        flame = ((XX - (cx + sway * top)) / rx) ** 2 + ((YY - fy) / ry) ** 2 <= 1
        flame &= YY <= gy - 2
        tip = (YY < fy) & (np.abs(XX - (cx + sway * (top + 1))) <= rx * (YY - (fy - ry)) / ry)
        m = flame & ((YY >= fy) | tip)
        cv[m] = (*col, 255)
    for i, (sx, sy) in enumerate(((cx - 2, gy - 17), (cx + 3, gy - 20), (cx + 1, gy - 23))):   # sparks
        if (i + k) % 2 == 0:
            yy = int(sy - k)
            if 0 <= yy < H:
                cv[yy, int(sx + sway)] = (255, 220, 120, 255)
    for a in range(0, 360, 40):                                                # front stones over the logs
        x = cx + 8.5 * np.cos(np.radians(a))
        y = gy - 1 + 2.6 * np.sin(np.radians(a))
        if np.sin(np.radians(a)) >= 0:
            st = ((XX - x) / 2.0) ** 2 + ((YY - y) / 1.5) ** 2 <= 1
            c.paste(st, g.shade_rows(st), stone)
    return Image.fromarray(cv, "RGBA")


def floating_lantern(k):
    """EP358: a toro nagashi - a paper lantern on a little wooden float, drifting on the river (the lantern festival,
    E02). k = 0..3: it bobs a pixel and the light breathes. Its glow spills on the water as a broken reflection."""
    cv = np.zeros((H, W, 4), np.uint8)
    cx, gy = 40, H - 6
    bob = [0, 1, 1, 0][k]
    glow = [1.0, 0.9, 1.05, 0.95][k]
    for i, (dx, w, a) in enumerate(((0, 9, 150), (-2, 6, 110), (3, 4, 90), (-1, 3, 70))):   # the reflection
        y = gy + 2 + i + bob
        if 0 <= y < H:
            for x in range(cx + dx - w // 2 + (k + i) % 2, cx + dx + w // 2, 2):
                cv[y, x] = (255, 170 - i * 15, 60, a)
    base = (58, 40, 26, 255)
    for x in range(cx - 8, cx + 8):                                            # the float
        cv[gy + bob, x] = base
        cv[gy - 1 + bob, x] = (78, 56, 36, 255)
    top, bot, l, r = gy - 14 + bob, gy - 2 + bob, cx - 6, cx + 6                # the paper box
    for y in range(top, bot + 1):
        for x in range(l, r + 1):
            edge = y in (top, bot) or x in (l, r)
            if edge:
                cv[y, x] = (40, 28, 20, 255)                                   # wooden frame
            else:
                t = 1.0 - (abs(x - cx) / 6.0) ** 2 * 0.5 - abs(y - (top + bot) / 2) / 14.0
                t = max(0.0, min(1.0, t * glow))
                cv[y, x] = (255, int(150 + 95 * t), int(60 + 120 * t), 255)
    for x in range(l + 1, r):                                                  # a dark ink stroke (a name, a prayer)
        if x in (cx - 1, cx):
            for y in range(top + 3, bot - 3):
                cv[y, x] = (120, 50, 30, 255)
    for x in range(l - 1, r + 2):                                              # the little roof rim
        cv[top - 1, x] = (40, 28, 20, 255)
    return Image.fromarray(cv, "RGBA")


def star(k):
    """EP359: a four-pointed star that twinkles (k = 0..3): ink-world skies (Dragon Ch2's Outside time)."""
    cv = np.zeros((H, W, 4), np.uint8)
    cx, cy = 40, H // 2
    arm = [4, 6, 5, 3][k]
    for i in range(-arm, arm + 1):
        a = int(255 * (1 - abs(i) / (arm + 1)))
        cv[cy, cx + i] = (220, 235, 255, a)
        cv[cy + i, cx] = (220, 235, 255, a)
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        cv[cy + dy, cx + dx] = (190, 210, 255, 160)
    cv[cy, cx] = (255, 255, 255, 255)
    return Image.fromarray(cv, "RGBA")


def eggs(painted=False, basket=False):
    """A heap of eggs (Ryozo's altar) or a basket of painted ones (Egg Caves 2)."""
    cv = np.zeros((H, W, 4), np.uint8)
    c = g.Canvas()
    c.col = cv
    YY, XX = np.mgrid[0:H, 0:W]
    shell, ink = g.ramp((236, 226, 200)), g.ramp((150, 40, 40))
    reed = g.ramp((170, 130, 70))
    gy = H - 4
    rng = np.random.default_rng(7 if basket else 3)
    if basket:
        b = (((XX - 40) / 15.0) ** 2 + ((YY - (gy - 6)) / 7.0) ** 2 <= 1) & (YY >= gy - 9)
        c.paste(b, g.shade_rows(b), reed)
        weave = b & ((XX + YY) % 4 == 0)
        c.paste(weave, np.zeros((H, W), int) + 3, reed)
        spots = [(30 + 5 * i + (j % 2) * 2, gy - 12 - 4 * j) for j in range(2) for i in range(4 - j)]
    else:
        spots = []
        for row in range(5):                                             # a pyramid heap
            n = 7 - row
            for i in range(n):
                spots.append((40 - (n - 1) * 3 + 6 * i + int(rng.integers(-1, 2)), gy - 3 - 4 * row))
    for ex, ey in spots:
        e = ((XX - ex) / 3.0) ** 2 + ((YY - ey) / 3.8) ** 2 <= 1
        c.paste(e, g.shade_rows(e, dither=False), shell)
        if painted or basket:
            mark = e & (((XX - ex) * 2 + (YY - ey)) % 5 == 0)
            c.paste(mark, np.zeros((H, W), int) + 2, ink)
    g.outline_outer(c)
    return Image.fromarray(cv, "RGBA")


# ---- Room decorations (user: "go make the furniture and decorations"): our own pixel art in place of the engine's
# library pieces, drawn at the cast's scale (a person is ~60 px tall here, so 1 px is ~2.7 cm). Ground line at H-4.
DECOR = {}                                    # kind -> (EP id, name, draw function, frames)


def _px(cv, x, y, c):
    if 0 <= y < H and 0 <= x < W:
        cv[y, x] = c if len(c) == 4 else (*c, 255)


def _rect(cv, x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            _px(cv, x, y, c)


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def _block(cv, x0, y0, w, h, c, top=2, outline=True):
    """A box seen from the front and a little above: a lit top strip, the front face darkening downward."""
    for y in range(h):
        f = 1.25 if y < top else 1.0 - 0.25 * (y - top) / max(1, h - top)
        for x in range(w):
            side = 0.85 if x in (0, w - 1) else 1.0
            _px(cv, x0 + x, y0 + y, _shade(c, f * side))
    if outline:
        for x in range(w):
            _px(cv, x0 + x, y0 + h - 1, _shade(c, 0.45))
        for y in range(h):
            _px(cv, x0, y0 + y, _shade(c, 0.55))
            _px(cv, x0 + w - 1, y0 + y, _shade(c, 0.55))


def _oval(cv, cx, cy, rx, ry, c, light=True):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = ((x - cx) / max(0.5, rx)) ** 2 + ((y - cy) / max(0.5, ry)) ** 2
            if d <= 1:
                f = (1.2 - 0.5 * ((x - cx + rx * 0.4) / (2 * rx))) if light else 1.0
                _px(cv, x, y, _shade(c, f))


def _canvas():
    return np.zeros((H, W, 4), np.uint8)


def katana_rack(k=0):
    """A kake: a black lacquer stand holding a katana and a wakizashi, sheathed, edge up."""
    cv, gy, cx = _canvas(), H - 4, 40
    lac, gold = (36, 30, 34), (196, 160, 70)
    for x in (cx - 15, cx + 14):                                    # the two uprights
        _rect(cv, x, gy - 20, 2, 20, lac)
        _rect(cv, x - 2, gy - 1, 6, 2, _shade(lac, 1.3))
        for y in (gy - 18, gy - 11):                                # the cradles
            _rect(cv, x - 1, y, 4, 2, _shade(lac, 1.4))
    for y, ln, sc in ((gy - 19, 34, (60, 40, 46)), (gy - 12, 26, (90, 30, 30))):   # saya (scabbards)
        _rect(cv, cx - ln // 2, y, ln, 2, sc)
        _px(cv, cx - ln // 2, y, gold)
        tsuka = cx + ln // 2                                        # the hilt: ito wrap, a gold tsuba
        _rect(cv, tsuka - 9, y - 1, 1, 4, gold)
        for x in range(tsuka - 8, tsuka):
            _px(cv, x, y, (230, 225, 210) if x % 2 else (40, 34, 30))
            _px(cv, x, y + 1, (40, 34, 30) if x % 2 else (230, 225, 210))
    return Image.fromarray(cv, "RGBA")


def armour_stand(k=0):
    """A yoroi on its stand: kabuto, a lacquered do of laced plates, sode on the shoulders, the stand's cross-bar."""
    cv, gy, cx = _canvas(), H - 4, 40
    wood, lace, plate = (60, 44, 30), (150, 36, 36), (40, 40, 46)
    _rect(cv, cx - 1, gy - 34, 3, 34, wood)                         # the stand
    _rect(cv, cx - 8, gy - 1, 17, 2, _shade(wood, 1.2))
    for row in range(6):                                            # the do: laced plates
        y = gy - 26 + row * 3
        _rect(cv, cx - 7, y, 15, 2, _shade(plate, 1.2 - row * 0.05))
        for x in range(cx - 7, cx + 8, 2):
            _px(cv, x, y + 2, lace)
    for sx in (cx - 12, cx + 8):                                    # the sode (shoulder plates)
        for row in range(4):
            _rect(cv, sx, gy - 28 + row * 3, 5, 2, _shade(plate, 1.1))
            _px(cv, sx + 2, gy - 26 + row * 3, lace)
    _oval(cv, cx, gy - 33, 6, 4, plate)                             # the kabuto
    _rect(cv, cx - 8, gy - 30, 17, 2, _shade(plate, 0.9))           # its neck guard
    _rect(cv, cx - 1, gy - 39, 2, 3, (200, 170, 70))                # the maedate (gold crest)
    return Image.fromarray(cv, "RGBA")


def sake_barrel(k=0):
    """A taru: a cedar cask in a straw wrap, rope bands, a printed label, the lid on top."""
    cv, gy, cx = _canvas(), H - 4, 40
    straw, rope, cedar = (196, 170, 110), (120, 90, 56), (150, 104, 64)
    _block(cv, cx - 9, gy - 18, 18, 18, straw, top=0)
    for y in (gy - 15, gy - 4):
        _rect(cv, cx - 9, y, 18, 1, rope)
    _rect(cv, cx - 4, gy - 12, 8, 6, (230, 222, 200))               # the label, a red mark on it
    _rect(cv, cx - 1, gy - 11, 2, 4, (170, 40, 40))
    _oval(cv, cx, gy - 18, 9, 2, cedar)                              # the lid
    return Image.fromarray(cv, "RGBA")


def clay_pot(k=0):
    """A tsubo: a dark glazed storage jar with a wooden lid."""
    cv, gy, cx = _canvas(), H - 4, 40
    glaze = (86, 60, 44)
    _oval(cv, cx, gy - 7, 7, 7, glaze)
    _rect(cv, cx - 4, gy - 14, 8, 2, _shade(glaze, 0.8))
    _oval(cv, cx, gy - 15, 4, 1.4, (120, 90, 60))
    for x in range(cx - 4, cx + 2):                                  # a glaze run
        _px(cv, x, gy - 9, (130, 110, 80))
    return Image.fromarray(cv, "RGBA")


def bucket(k=0):
    """An oke: a wooden bucket in staves with two bamboo hoops and a rope handle."""
    cv, gy, cx = _canvas(), H - 4, 40
    wood = (164, 120, 76)
    _block(cv, cx - 6, gy - 10, 12, 10, wood, top=1)
    for x in range(cx - 5, cx + 6, 3):
        _rect(cv, x, gy - 9, 1, 9, _shade(wood, 0.8))
    for y in (gy - 8, gy - 3):
        _rect(cv, cx - 6, y, 12, 1, (110, 140, 70))
    for i in range(9):                                              # the handle
        _px(cv, cx - 4 + i, gy - 14 + abs(i - 4) // 2, (110, 84, 50))
    return Image.fromarray(cv, "RGBA")


def writing_set(k=0):
    """A writing box on the floor: an unrolled scroll, an inkstone, a brush on its rest."""
    cv, gy, cx = _canvas(), H - 4, 40
    _rect(cv, cx - 11, gy - 3, 15, 3, (236, 228, 206))              # the scroll
    for x in range(cx - 9, cx + 3, 2):                              # writing on it
        _rect(cv, x, gy - 3, 1, 2, (40, 36, 36))
    _rect(cv, cx - 12, gy - 4, 2, 4, (120, 80, 50))                  # its rollers
    _rect(cv, cx + 4, gy - 4, 2, 4, (120, 80, 50))
    _block(cv, cx + 7, gy - 4, 6, 4, (50, 50, 58), top=1)            # the inkstone
    _rect(cv, cx + 8, gy - 6, 6, 1, (170, 130, 80))                  # the brush
    _px(cv, cx + 14, gy - 6, (30, 30, 30))
    return Image.fromarray(cv, "RGBA")


def book_stack(k=0):
    """Bound books, stitched spines out, in a stack: indigo and rust covers."""
    cv, gy, cx = _canvas(), H - 4, 40
    for i, (c, w) in enumerate((((50, 60, 110), 13), ((150, 80, 50), 12), ((60, 90, 70), 13), ((50, 60, 110), 11))):
        y = gy - 3 * (i + 1)
        _block(cv, cx - w // 2 + (i % 2), y, w, 3, c, top=1)
        _rect(cv, cx - w // 2 + (i % 2) + 1, y + 1, w - 2, 1, (225, 215, 190))   # page edges
    return Image.fromarray(cv, "RGBA")


def meal_tray(k=0):
    """A lacquered zen tray: a rice bowl, a soup bowl, a little dish of pickles, chopsticks."""
    cv, gy, cx = _canvas(), H - 4, 40
    _block(cv, cx - 9, gy - 3, 18, 3, (130, 34, 30), top=1)
    _oval(cv, cx - 4, gy - 5, 3, 2, (230, 226, 216))                 # rice
    _oval(cv, cx + 3, gy - 5, 3, 2, (40, 30, 30))                    # miso, in black lacquer
    _rect(cv, cx + 1, gy - 6, 4, 1, (180, 120, 60))
    _rect(cv, cx - 8, gy - 4, 14, 1, (200, 170, 110))                # chopsticks
    return Image.fromarray(cv, "RGBA")


def sake_flask(k=0):
    """A tokkuri and its little cup."""
    cv, gy, cx = _canvas(), H - 4, 40
    _oval(cv, cx - 1, gy - 5, 4, 5, (220, 214, 200))
    _rect(cv, cx - 2, gy - 12, 3, 4, (220, 214, 200))
    _rect(cv, cx - 3, gy - 13, 5, 1, (90, 110, 150))                 # a blue band at the neck
    _oval(cv, cx + 6, gy - 2, 2, 1.5, (220, 214, 200))
    return Image.fromarray(cv, "RGBA")


def lacquer_box(k=0):
    """A black lacquer box with gold maki-e and a red cord."""
    cv, gy, cx = _canvas(), H - 4, 40
    _block(cv, cx - 7, gy - 7, 14, 7, (30, 26, 30), top=2)
    for x in range(cx - 5, cx + 5, 3):                              # gold maki-e
        _px(cv, x, gy - 4, (210, 170, 80))
        _px(cv, x + 1, gy - 5, (210, 170, 80))
    _rect(cv, cx, gy - 7, 1, 7, (180, 40, 40))                       # the cord
    return Image.fromarray(cv, "RGBA")


def andon(k=0):
    """An andon: a paper floor lamp in a dark wooden frame, glowing; the flame breathes (k = 0..3)."""
    cv, gy, cx = _canvas(), H - 4, 40
    frame = (54, 38, 26)
    glow = [1.0, 0.92, 1.06, 0.96][k]
    for x in (cx - 6, cx + 5):                                      # legs
        _rect(cv, x, gy - 4, 1, 4, frame)
    for y in range(gy - 24, gy - 4):                                # the paper, lit from inside
        for x in range(cx - 5, cx + 5):
            t = max(0.0, min(1.0, (1.0 - abs(x - cx + 0.5) / 7.0 - abs(y - (gy - 13)) / 18.0) * glow))
            _px(cv, x, y, (255, int(185 + 60 * t), int(110 + 110 * t)))
    for y in (gy - 25, gy - 14, gy - 4):                            # the frame bars
        _rect(cv, cx - 6, y, 12, 1, frame)
    for x in (cx - 6, cx + 5):
        _rect(cv, x, gy - 25, 1, 21, frame)
    _rect(cv, cx - 1, gy - 28, 2, 3, frame)                          # the handle
    return Image.fromarray(cv, "RGBA")


def crate_stack(k=0):
    """Road-closed barricade piece: wooden crates stacked two high, rope-tied, a paper notice pasted on the front."""
    cv, gy, cx = _canvas(), H - 4, 40
    wood = (150, 108, 66)
    _block(cv, cx - 11, gy - 10, 12, 10, wood, top=2)
    _block(cv, cx + 1, gy - 9, 10, 9, _shade(wood, 0.9), top=2)
    _block(cv, cx - 6, gy - 19, 11, 9, _shade(wood, 1.05), top=2)
    for x0, y0, w, h in ((cx - 11, gy - 10, 12, 10), (cx + 1, gy - 9, 10, 9), (cx - 6, gy - 19, 11, 9)):
        _rect(cv, x0 + w // 2, y0, 1, h, _shade(wood, 0.6))            # plank seams
    _rect(cv, cx - 11, gy - 6, 22, 1, (110, 84, 50))                    # the rope
    _rect(cv, cx - 3, gy - 17, 5, 6, (236, 228, 206))                   # the notice, two lines of ink
    _rect(cv, cx - 2, gy - 15, 3, 1, (40, 36, 36))
    _rect(cv, cx - 2, gy - 13, 3, 1, (40, 36, 36))
    return Image.fromarray(cv, "RGBA")


DECOR.update({"sword": ("EP210", "Katana rack", katana_rack, 1), "shield": ("EP211", "Armour stand", armour_stand, 1),
              "barrel": ("EP212", "Sake barrel", sake_barrel, 1), "pot": ("EP213", "Storage jar", clay_pot, 1),
              "bucket": ("EP214", "Bucket", bucket, 1), "doc": ("EP215", "Writing set", writing_set, 1),
              "book": ("EP216", "Books", book_stack, 1), "dish": ("EP217", "Meal tray", meal_tray, 1),
              "bottle": ("EP218", "Sake flask", sake_flask, 1), "jewel": ("EP219", "Lacquer box", lacquer_box, 1),
              "candle": ("EP220", "Andon", andon, 4), "crates": ("EP221", "Crates", crate_stack, 1)})


def main():
    jpath = os.path.join(g.RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    im = cart()
    im.save(os.path.join(g.PIC, "prop_cart.png"))
    e = json.loads(json.dumps(tmpl))
    e.update({"name": {"en": "Supply cart", "ja": "Supply cart"}, "pic3d": "/resource/enemy_pic/prop_cart.png",
              "aniuv": [1, 1], "memo": "prop (tools/gen_props.py)", "gndpos": [0.5, 3.0 / H], "scale": 1.45 * g.CAST_SCALE,
              "flipx": False, "animap": [{"id": "stand", "st": 0, "en": 1, "spd": 1.0, "loop": True, "replay": False}]})
    j["EP350"] = e
    fire = Image.new("RGBA", (W * 4, H))                                  # EP355 campfire: 4 flicker frames
    for k in range(4):
        fire.paste(campfire(k), (k * W, 0))
    fire.save(os.path.join(g.PIC, "prop_campfire.png"))
    p = json.loads(json.dumps(tmpl))
    p.update({"name": {"en": "Campfire", "ja": "Campfire"}, "pic3d": "/resource/enemy_pic/prop_campfire.png",
              "aniuv": [4, 1], "memo": "prop (tools/gen_props.py)", "gndpos": [0.5, 3.0 / H],
              "scale": 1.45 * g.CAST_SCALE, "flipx": False,
              "animap": [{"id": "stand", "st": 0, "en": 4, "spd": 7.0, "loop": True, "replay": False}]})
    j["EP355"] = p
    fire.resize((W * 16, H * 4), Image.NEAREST).save(os.path.join(g.PREVIEW, "campfire.png"))
    for pid, name, fn, spd in (("EP358", "Floating lantern", floating_lantern, 3.0), ("EP359", "Star", star, 4.0)):
        strip = Image.new("RGBA", (W * 4, H))                             # animated: 4 frames
        for k in range(4):
            strip.paste(fn(k), (k * W, 0))
        fname = "prop_" + name.lower().replace(" ", "_") + ".png"
        strip.save(os.path.join(g.PIC, fname))
        strip.resize((W * 16, H * 4), Image.NEAREST).save(os.path.join(g.PREVIEW, fname))
        p = json.loads(json.dumps(tmpl))
        p.update({"name": {"en": name, "ja": name}, "pic3d": "/resource/enemy_pic/" + fname, "aniuv": [4, 1],
                  "memo": "prop (tools/gen_props.py)", "gndpos": [0.5, 6.0 / H], "scale": 1.45 * g.CAST_SCALE,
                  "flipx": False, "animap": [{"id": "stand", "st": 0, "en": 4, "spd": spd, "loop": True,
                                              "replay": False}]})
        j[pid] = p
    for pid, name, img in (("EP352", "Egg heap", eggs(painted=True)), ("EP353", "Painted eggs", eggs(basket=True)),
                           ("EP356", "Palanquin", palanquin())):
        fname = "prop_" + name.lower().replace(" ", "_") + ".png"
        img.save(os.path.join(g.PIC, fname))
        p = json.loads(json.dumps(tmpl))
        p.update({"name": {"en": name, "ja": name}, "pic3d": "/resource/enemy_pic/" + fname, "aniuv": [1, 1],
                  "memo": "prop (tools/gen_props.py)", "gndpos": [0.5, 3.0 / H], "scale": 1.45 * g.CAST_SCALE,
                  "flipx": False, "animap": [{"id": "stand", "st": 0, "en": 1, "spd": 1.0, "loop": True,
                                              "replay": False}]})
        j[pid] = p
    sheet = Image.new("RGBA", (W * len(DECOR), H), (60, 54, 48, 255))       # the decorations (+ a preview sheet)
    for i, (kind, (pid, name, fn, frames)) in enumerate(DECOR.items()):
        strip = Image.new("RGBA", (W * frames, H))
        for k in range(frames):
            strip.paste(fn(k), (k * W, 0))
        fname = "decor_" + kind + ".png"
        strip.save(os.path.join(g.PIC, fname))
        sheet.alpha_composite(fn(0), (i * W, 0))
        p = json.loads(json.dumps(tmpl))
        p.update({"name": {"en": name, "ja": name}, "pic3d": "/resource/enemy_pic/" + fname, "aniuv": [frames, 1],
                  "memo": "decoration (tools/gen_props.py DECOR)", "gndpos": [0.5, 4.0 / H],
                  "scale": 1.45 * g.CAST_SCALE, "flipx": False,
                  "animap": [{"id": "stand", "st": 0, "en": frames, "spd": 3.0, "loop": True, "replay": False}]})
        j[pid] = p
    sheet.resize((sheet.width * 3, H * 3), Image.NEAREST).save(os.path.join(g.PREVIEW, "decor.png"))
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    im.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(g.PREVIEW, "prop_cart.png"))
    print("props written")


if __name__ == "__main__":
    main()
