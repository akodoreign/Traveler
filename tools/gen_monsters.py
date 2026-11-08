"""Monsters drawn from scratch in the cast's pixel style (gen_sprites2d helpers), enemies facing east (toward the
party on the right). Idle frames -> gen_enemy_art.animate (idle / attack / hurt rows).

  EP110 Goblin Warmonger   the template goblin, bigger, iron jingasa, red war paint, a rusty jagged blade
  EP111 Cave Bat Swarm     three bats on a flap cycle
  EP112 Yurei              a drowned-pale ghost: white burial kimono, hair over the face, no feet, blue wisps
  EP114, EP115   hsv-tinted copies: Goblin Experiment (of EP110), Drunken Samurai II (of EP408)
  EP113 Troll              a hunched mossy giant, long arms, tusks, filed shackles on the wrists (Crab Ch2 donjon)

  EP160-163  Gaki, Tsuchigumo, Mieko's Shadow (moved off the boss banners EP450-452), Blood Leech;
  EP164-165  Paddy Python, Giant Hornet
  EP166-170  Snow Bear, Tengu Crow-Warrior, Fire Elemental, Ash Ghoul, Wolf-Spirit (a tinted Grey Wolf)
  EP171-174  Pigeon Swarm (a tinted crow), Persimmon the pony, a woodchuck, a powder keg

Run after gen_enemy_art.py:  python -E tools/gen_monsters.py   (then gen_portraits.py)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402
import gen_enemy_art as ea  # noqa: E402

FW, FH = g.FW, g.FH
XX, YY = g.XX, g.YY
GROUND = g.GROUND


def canvas():
    c = g.Canvas()
    return c


def finish(c, shadow=(40, 9)):
    g.outline_outer(c)
    if shadow:
        sh = g.m_ellipse(shadow[0], GROUND + 0.5, shadow[1], 1.8)
        c.col[sh & (c.col[..., 3] == 0)] = (0, 0, 0, 70)
    return Image.fromarray(c.col, "RGBA")


# ------------------------------------------------------------------------------------------- goblin warmonger
def warmonger():
    out = []
    for i, f in enumerate(ea.frames(ea.load("goblin"), 4)):
        f = f.resize((int(f.width * 1.25), int(f.height * 1.25)), Image.NEAREST)
        f = ea.recolor(f, hue_to=0.22, sat_mul=0.45, val_mul=0.72, keep=lambda h, s, v: v > 0.85)
        d = ImageDraw.Draw(f)
        ty = ea.top_row(f, 14, 38)
        cx, base = 26, ty + 6
        d.polygon([(cx - 12, base), (cx, ty - 4), (cx + 12, base)], fill=(92, 96, 104, 255), outline=ea.OUTLINE)
        d.line([(cx - 12, base), (cx + 12, base)], fill=ea.OUTLINE)
        d.line([(cx - 9, base - 2), (cx + 9, base - 2)], fill=(150, 156, 166, 255))      # rivet band
        for k in (-6, 0, 6):
            d.point((cx + k, base - 2), fill=(214, 220, 228, 255))
        d.line([(cx + 1, base + 4), (cx + 6, base + 4)], fill=(190, 40, 34, 255), width=2)  # war paint
        sw = (i % 2)
        d.polygon([(40, 8 + sw), (44, 6 + sw), (46, 10 + sw), (44, 30 + sw), (41, 30 + sw), (42, 14 + sw),
                   (39, 12 + sw)], fill=(150, 90, 60, 255), outline=ea.OUTLINE)                # rusty jagged blade
        d.line([(41, 31 + sw), (44, 36 + sw)], fill=(80, 54, 40, 255), width=2)
        out.append(f)
    return out


# ------------------------------------------------------------------------------------------- bats
def bats(k):
    c = canvas()
    body, wing = g.ramp((70, 56, 70)), g.ramp((96, 70, 90))
    for n, (bx, by) in enumerate(((30, 28), (44, 20), (40, 38))):
        ph = (k + n) % 4
        up = [-5, -1, 4, -1][ph]
        bx += [0, 1, 0, -1][(k + n * 2) % 4]
        by += [0, -1, 0, 1][(k + n) % 4]
        for sgn in (-1, 1):
            w = g.m_poly([(bx, by), (bx + sgn * 7, by + up - 2), (bx + sgn * 10, by + up + 1),
                          (bx + sgn * 7, by + up + 1), (bx + sgn * 5, by + up + 3), (bx + sgn * 3, by + 2)])
            c.paste(w, g.shade_rows(w), wing)
        b = g.m_ellipse(bx + 0.5, by + 1, 2.0, 2.6)
        c.paste(b, g.shade_rows(b), body)
        for sgn in (-1, 1):
            c.px(bx + sgn * 1, by - 2, body[3])                    # ears
        c.px(bx + 1, by, (255, 80, 70))                             # eye
    return finish(c, shadow=None)


# ------------------------------------------------------------------------------------------- yurei
def yurei(k):
    c = canvas()
    robe, hair, skin = g.ramp((232, 236, 240)), g.ramp((26, 24, 32)), g.ramp((214, 222, 226))
    fl = [0, -1, -2, -1][k]
    cx, top = 40, 18 + fl
    # the robe tapers into a trailing wisp instead of feet
    r = g.m_poly([(cx - 6, top + 10), (cx + 6, top + 10), (cx + 9, top + 30), (cx + 4, top + 38), (cx - 2, top + 44 - k),
                  (cx - 7, top + 34), (cx - 9, top + 28)])
    t = g.shade_rows(r)
    fade = r & (YY > top + 34)
    c.paste(r, t, robe)
    c.col[fade, 3] = (150 - (YY[fade] - top - 34) * 12).clip(30, 150).astype(np.uint8)
    lap = g.m_capsule((cx - 4, top + 11), (cx + 3, top + 22), 0.6)[0] & r            # left over right: burial fold
    c.paste(lap, np.zeros((FH, FW), int) + 1, robe)
    # hanging arms, limp wrists, forward
    for dx in (-1, 3):
        a = g.m_capsule((cx + dx, top + 14), (cx + dx + 8, top + 19), 1.6)[0]
        c.paste(a, g.shade_rows(a), robe)
        h = g.m_capsule((cx + dx + 8, top + 19), (cx + dx + 9, top + 23), 0.9)[0]
        c.paste(h, g.shade_rows(h), skin)
    # head, face hidden by long wet hair
    hd = g.m_ellipse(cx + 1.5, top + 5, 4.6, 5.0)
    c.paste(hd, g.shade_rows(hd), skin)
    hr = g.m_poly([(cx - 5, top - 1), (cx + 4, top - 2), (cx + 6, top + 1), (cx + 4, top + 2), (cx + 2, top + 1),
                   (cx + 1, top + 5), (cx + 3, top + 14), (cx + 1, top + 20), (cx - 2, top + 26), (cx - 5, top + 18),
                   (cx - 8, top + 24), (cx - 7, top + 6)])                         # one long sheet down the back
    th = g.shade_rows(hr)
    th[hr & (XX % 2 == 0) & (th >= 2)] = 1
    c.paste(hr, th, hair)
    for n in range(6):                                             # a wet strand across the face
        c.px(cx + 3 - (n > 3), top + 2 + n, hair[1])
    c.px(cx + 4, top + 4, (20, 30, 40)), c.px(cx + 5, top + 4, (200, 230, 255))   # one staring eye
    c.px(cx + 4, top + 8, (90, 100, 120))                          # a grey mouth
    out = finish(c, shadow=None)
    d = ImageDraw.Draw(out)
    for n, (wx, wy) in enumerate(((cx - 12, top + 4), (cx + 13, top + 10), (cx - 10, top + 26))):  # hitodama wisps
        wy += [0, -1, -2, -1][(k + n) % 4]
        d.ellipse([wx - 2, wy - 2, wx + 2, wy + 2], fill=(120, 190, 255, 200))
        d.point((wx, wy + 3), fill=(120, 190, 255, 120))
    return out


# ------------------------------------------------------------------------------------------- troll
def troll(k):
    """A hunched mossy giant drawn at half scale (the sprite is shown at 2x)."""
    c = canvas()
    skin, moss, tusk = g.ramp((118, 128, 100)), g.ramp((70, 96, 58)), g.ramp((232, 222, 190))
    iron, hair = g.ramp((92, 92, 100)), g.ramp((54, 60, 44))
    br = [0, 1, 1, 0][k]
    cx, gy = 38, GROUND
    hip, sh = (cx - 3, gy - 22 + br), (cx + 1, gy - 38 + br)
    for (x, dark) in ((cx - 6, True), (cx + 2, False)):           # stumpy bowed legs
        l = g.m_capsule((x, hip[1] + 2), (x + 2, gy - 3), 4.2, 3.6)[0]
        t = g.shade_rows(l)
        if dark:
            t[l & (t >= 2)] -= 1
        c.paste(l, t, skin)
        ft = g.m_ellipse(x + 4, gy - 1.5, 5.0, 2.2)
        c.paste(ft, g.shade_rows(ft), skin)
    far = g.m_capsule((sh[0] - 4, sh[1] + 3), (cx - 10, gy - 12 + br), 4.0, 3.6)[0]  # far arm to the ground
    t = g.shade_rows(far)
    t[far & (t >= 2)] -= 1
    c.paste(far, t, skin)
    body = g.m_capsule(hip, sh, 10.5, 12.0)[0]
    c.paste(body, g.shade_rows(body), skin)
    bel = g.m_ellipse(cx + 4, gy - 26 + br, 6.5, 7.0) & body
    c.paste(bel, g.shade_rows(bel, outline=False), g.ramp((150, 156, 120)))
    mo = body & (YY < sh[1] + 2) & ((XX * 3 + YY * 5) % 7 < 3)       # moss on the shoulders and back
    c.paste(mo, g.shade_rows(mo, outline=False), moss)
    hd = g.m_ellipse(sh[0] + 9, sh[1] + 1, 6.5, 5.5)                 # head thrust forward, low
    c.paste(hd, g.shade_rows(hd), skin)
    mane = g.m_poly([(sh[0] - 2, sh[1] - 6), (sh[0] + 9, sh[1] - 5), (sh[0] + 5, sh[1] + 2), (sh[0] - 4, sh[1] + 6)])
    c.paste(mane, g.shade_rows(mane), hair)
    c.px(sh[0] + 12, sh[1] - 1, (250, 200, 60)), c.px(sh[0] + 13, sh[1] - 1, (30, 20, 10))       # eye
    for tx in (11, 14):                                            # tusks from the underbite
        tk = g.m_poly([(sh[0] + tx, sh[1] + 4), (sh[0] + tx + 1.5, sh[1] + 4), (sh[0] + tx + 1, sh[1] + 1)])
        c.paste(tk, g.shade_rows(tk), tusk)
    near = g.m_capsule((sh[0] + 2, sh[1] + 4), (cx + 14, gy - 10 + br), 4.6, 4.2)[0]  # near arm, knuckles down
    c.paste(near, g.shade_rows(near), skin)
    fist = g.m_ellipse(cx + 15, gy - 7 + br, 4.4, 3.6)
    c.paste(fist, g.shade_rows(fist), skin)
    for (wx, wy) in ((cx + 12, gy - 13 + br), (cx - 9, gy - 15 + br)):   # shackles, the chain filed through
        sk = g.m_ellipse(wx, wy, 4.2, 2.2) & ~g.m_ellipse(wx, wy, 2.6, 1.0)
        c.paste(sk, g.shade_rows(sk), iron)
        for n in range(3):
            c.px(wx - 3 + n * 2, wy + 3 + n, iron[2] if n % 2 else iron[3])
    return finish(c, shadow=(38, 16))


# ------------------------------------------------------------------------------------------- onikage
def onikage(k):
    """A demon horse (Crab Ch3): black hide over bone, a smoke mane, a red eye, ember hooves. Drawn at half scale."""
    c = canvas()
    hide, bone, smoke = g.ramp((44, 36, 52)), g.ramp((168, 156, 140)), g.ramp((84, 52, 96))
    gy = GROUND
    br = [0, -1, 0, 1][k]
    gait = [(0, 2), (2, 0), (0, -2), (-2, 0)][k]
    body = g.m_ellipse(34, gy - 24 + br, 14.0, 8.2)
    for n, (x, fwd) in enumerate(((26, False), (29, True), (41, False), (44, True))):   # far legs darker
        dx = gait[0] if n % 2 else gait[1]
        lg = g.m_capsule((x, gy - 21 + br), (x + dx, gy - 2), 2.9, 1.9)[0]
        t = g.shade_rows(lg)
        if not fwd:
            t[lg & (t >= 2)] -= 1
        c.paste(lg, t, hide)
        c.px(x + dx, gy - 1, (255, 130, 50)), c.px(x + dx + 1, gy - 1, (255, 190, 90))   # ember hooves
    c.paste(body, g.shade_rows(body), hide)
    for rx in range(28, 42, 3):                                     # ribs showing through
        rib = body & (np.abs(XX - rx) < 0.8) & (YY > gy - 27 + br)
        c.paste(rib, g.shade_rows(rib, outline=False), bone)
    nk = g.m_capsule((44, gy - 27 + br), (51, gy - 39 + br), 4.4, 3.0)[0]
    c.paste(nk, g.shade_rows(nk), hide)
    hd = g.m_capsule((51, gy - 40 + br), (60, gy - 34 + br), 3.4, 2.2)[0]
    c.paste(hd, g.shade_rows(hd), bone)                             # a bare skull for a face
    c.px(54, gy - 39 + br, (255, 60, 40)), c.px(55, gy - 39 + br, (255, 150, 90))       # the red eye
    c.px(59, gy - 33 + br, (40, 20, 20))
    for n in range(7):                                              # smoke mane along the neck, streaming back
        mx, my = 49 - n * 1.5, gy - 41 + n * 2 + br
        w = g.m_ellipse(mx + [0, -1, 0, 1][(k + n) % 4], my, 2.6, 1.8)
        c.paste(w, g.shade_rows(w, outline=False), smoke)
    for n in range(5):                                              # smoke tail
        w = g.m_ellipse(20 - n * 2, gy - 26 + n * 2 + [0, 1, 0, -1][(k + n) % 4], 2.8 - n * 0.3, 2.0)
        c.paste(w, g.shade_rows(w, outline=False), smoke)
    return finish(c, shadow=(36, 15))


# ------------------------------------------------------------------------------------------- toothed poppy
def poppy(k):
    """A Shadowlands poppy: a red flower head with a toothed mouth, turning to follow you."""
    c = canvas()
    stem, petal, gum = g.ramp((70, 110, 56)), g.ramp((206, 40, 44)), g.ramp((60, 16, 24))
    gy = GROUND
    sw = [0, 1, 0, -1][k]
    st = g.m_capsule((40, gy - 1), (42 + sw, gy - 26), 1.6, 1.2)[0]
    c.paste(st, g.shade_rows(st), stem)
    for (lx, ly, d) in ((40, gy - 8, -1), (41, gy - 15, 1)):        # two saw-edged leaves
        lf = g.m_poly([(lx, ly), (lx + d * 9, ly - 4), (lx + d * 7, ly - 1), (lx + d * 8, ly + 1), (lx + d * 2, ly + 2)])
        c.paste(lf, g.shade_rows(lf), stem)
    cx, cy = 44 + sw, gy - 32
    hd = g.m_ellipse(cx, cy, 10.0, 8.0)
    c.paste(hd, g.shade_rows(hd), petal)
    for a in range(0, 360, 60):                                     # petal folds
        x2, y2 = cx + 9 * math.cos(math.radians(a)), cy + 7 * math.sin(math.radians(a))
        fold = g.m_capsule((cx, cy), (x2, y2), 0.5)[0] & hd
        c.paste(fold, np.zeros((FH, FW), int) + 1, petal)
    mo = g.m_ellipse(cx + 2, cy + 1, 5.0, 3.6 + (k % 2))            # the mouth, opening and closing
    c.paste(mo, np.zeros((FH, FW), int) + 0, gum)
    for n in range(5):                                              # teeth round the rim
        tx = cx - 2 + n * 2
        c.px(tx, cy - 2 - (k % 2), (240, 236, 220)), c.px(tx, cy + 4 + (k % 2), (240, 236, 220))
    return finish(c, shadow=(42, 8))


# ------------------------------------------------------------------------------------------- Crab coast beasts
def crow(k):
    """Carrion Crow (bestiary B4 I): a big black crow hopping on the sand, wings half open, blue-black sheen."""
    c = canvas()
    ink, beak = g.ramp((38, 40, 58)), g.ramp((70, 66, 72))
    gy = GROUND
    hop = [0, -2, -3, -1][k]
    cx, cy = 38, gy - 9 + hop
    flap = [2, -3, -5, -1][k]
    for sgn, dark in ((-1, True), (1, False)):                      # far wing darker, near wing in front
        w = g.m_poly([(cx - 2, cy - 2), (cx - 9, cy - 7 + flap * sgn * 0.5), (cx - 12, cy - 3 + flap),
                      (cx - 6, cy + 1), (cx + 2, cy + 1)])
        t = g.shade_rows(w)
        if dark:
            t[w & (t >= 2)] -= 1
        c.paste(w, t, ink)
    b = g.m_ellipse(cx + 1, cy, 6.0, 4.0)
    c.paste(b, g.shade_rows(b), ink)
    tl = g.m_poly([(cx - 5, cy - 1), (cx - 12, cy + 2), (cx - 11, cy + 4), (cx - 4, cy + 2)])   # tail
    c.paste(tl, g.shade_rows(tl), ink)
    hd = g.m_ellipse(cx + 7, cy - 4, 3.0, 2.8)
    c.paste(hd, g.shade_rows(hd), ink)
    bk = g.m_poly([(cx + 9, cy - 5), (cx + 14, cy - 3), (cx + 9, cy - 2)])
    c.paste(bk, g.shade_rows(bk, outline=False), beak)
    c.px(cx + 8, cy - 5, (230, 210, 120))                           # a yellow eye
    for lx in (cx - 1, cx + 2):                                     # legs
        for yy in range(cy + 4, gy):
            c.px(lx, yy, (60, 56, 50))
    for n in range(3):                                              # blue sheen on the back
        c.px_on(cx - 2 + n * 2, cy - 3, (90, 104, 150))
    return finish(c, shadow=(38, 6))


def wisp(k):
    """Will-o'-wisp (hitodama, bestiary D I): a pale blue soul-flame with a trailing tail, two dark eyes."""
    c = canvas()
    gy = GROUND
    bob = [0, -1, -2, -1][k]
    cx, cy = 40, gy - 22 + bob
    core, flame = g.ramp((200, 236, 255)), g.ramp((90, 150, 230))
    tail = g.m_poly([(cx - 4, cy - 2), (cx - 14, cy - 8 + [0, 2, 0, -2][k]), (cx - 11, cy - 1),
                     (cx - 16, cy + 3 + [0, -1, 0, 1][k]), (cx - 4, cy + 4)])
    c.paste(tail, g.shade_rows(tail, outline=False), flame)
    b = g.m_ellipse(cx, cy, 6.5, 6.0 + (k % 2) * 0.5)
    c.paste(b, g.shade_rows(b, outline=False), flame)
    inner = g.m_ellipse(cx + 1, cy - 1, 4.0, 3.6)
    c.paste(inner, g.shade_rows(inner, outline=False), core)
    c.px(cx + 2, cy - 1, (30, 50, 90)), c.px(cx + 4, cy - 1, (30, 50, 90))           # eyes
    img = finish(c, shadow=None)
    a = np.array(img)
    m = a[..., 3] > 0
    a[m, 3] = 210                                                   # a little see-through
    return Image.fromarray(a, "RGBA")


def boar(k):
    """Wild Boar (bestiary B3 I): a bristly dark-brown boar, head low, white tusks, trotting at the party."""
    c = canvas()
    hide, bristle, tusk = g.ramp((96, 70, 52)), g.ramp((60, 44, 34)), g.ramp((236, 228, 206))
    gy = GROUND
    br = [0, -1, 0, 1][k]
    gait = [(0, 2), (2, 0), (0, -2), (-2, 0)][k]
    for n, (x, near) in enumerate(((28, False), (31, True), (43, False), (46, True))):
        dx = gait[0] if n % 2 else gait[1]
        lg = g.m_capsule((x, gy - 10 + br), (x + dx, gy - 1), 2.4, 1.6)[0]
        t = g.shade_rows(lg)
        if not near:
            t[lg & (t >= 2)] -= 1
        c.paste(lg, t, hide)
        c.px(x + dx, gy - 1, (40, 30, 26))
    body = g.m_ellipse(37, gy - 14 + br, 13.0, 7.5)
    c.paste(body, g.shade_rows(body), hide)
    mane = body & (YY < gy - 18 + br)                               # a bristle ridge along the back
    t = g.shade_rows(mane, outline=False)
    t[mane & (XX % 2 == 0)] = 0
    c.paste(mane, t, bristle)
    hd = g.m_poly([(46, gy - 19 + br), (55, gy - 14 + br), (57, gy - 9 + br), (50, gy - 7 + br), (45, gy - 10 + br)])
    c.paste(hd, g.shade_rows(hd), hide)
    sn = g.m_ellipse(56.5, gy - 9.5 + br, 1.6, 1.8)
    c.paste(sn, g.shade_rows(sn), g.ramp((150, 110, 100)))          # snout
    c.px(52, gy - 15 + br, (20, 14, 12))                            # eye
    for p in ((54, gy - 8 + br), (55, gy - 9 + br), (55, gy - 10 + br)):           # tusk curling up
        c.px(*p, tusk[3])
    ear = g.m_poly([(47, gy - 19 + br), (49, gy - 22 + br), (50, gy - 18 + br)])
    c.paste(ear, g.shade_rows(ear), bristle)
    tl = g.m_capsule((24, gy - 16 + br), (21, gy - 12 + br + (k % 2)), 0.8)[0]
    c.paste(tl, g.shade_rows(tl), bristle)
    return finish(c, shadow=(38, 13))


# ------------------------------------------------------------------------------------------- the other face
def other_face(k):
    """The face on the back of the Kommei's head (a separate target): a grinning oni mask that floats."""
    c = canvas()
    skin, horn, wisp = g.ramp((214, 90, 70)), g.ramp((236, 222, 190)), g.ramp((110, 60, 130))
    bob = [0, -1, -2, -1][k]
    cx, cy = 40, GROUND - 30 + bob
    for d in (-1, 1):                                               # horns
        hn = g.m_poly([(cx + d * 3, cy - 6), (cx + d * 7, cy - 13), (cx + d * 6, cy - 5)])
        c.paste(hn, g.shade_rows(hn), horn)
    fc = g.m_ellipse(cx, cy, 7.5, 8.5)
    c.paste(fc, g.shade_rows(fc), skin)
    for d in (-1, 1):                                               # glaring eyes
        c.px(cx + d * 3, cy - 2, (255, 220, 60)), c.px(cx + d * 3 + (1 if d > 0 else -1), cy - 2, (255, 220, 60))
        c.px(cx + d * 3, cy - 1, (30, 10, 10))
        c.px(cx + d * 2, cy - 4, skin[0]), c.px(cx + d * 4, cy - 5, skin[0])               # brows
    mo = g.m_ellipse(cx, cy + 4, 5.0, 1.8 + (k % 2) * 0.6)
    c.paste(mo, np.zeros((FH, FW), int), g.ramp((50, 10, 16)))
    for n in range(-4, 5, 2):
        c.px(cx + n, cy + 3, (246, 240, 226))                       # fangs
    for n in range(4):                                              # it trails a purple wisp, no body
        w = g.m_ellipse(cx - 1 + [0, 1, 0, -1][(k + n) % 4], cy + 10 + n * 3, 3.6 - n * 0.7, 1.8)
        c.paste(w, g.shade_rows(w, outline=False), wisp)
    return finish(c, shadow=None)


# ------------------------------------------------------------------------------------------- sea serpent eel
def sea_eel(k):
    """Sea Serpent Eel (bestiary F "Crane sea & isles"): a long grey-green eel rearing out of a splash, jaw open,
    a dorsal fin along its back."""
    c = canvas()
    skin, belly, fin = g.ramp((80, 104, 92)), g.ramp((170, 176, 140)), g.ramp((60, 80, 96))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    pts = [(22, gy - 4), (26, gy - 14), (34, gy - 22), (42, gy - 26 + sway), (50, gy - 30 + sway), (55, gy - 36 + sway)]
    for i in range(len(pts) - 1):                                       # the body: a thick curve of capsules
        seg = g.m_capsule(pts[i], pts[i + 1], 4.6 - i * 0.35, 4.6 - (i + 1) * 0.35)[0]
        c.paste(seg, g.shade_rows(seg), skin)
        bl = seg & (YY > (pts[i][1] + pts[i + 1][1]) / 2 + 1)
        c.paste(bl, g.shade_rows(bl, outline=False), belly)
    for i in range(1, 5):                                               # the dorsal fin
        x, y = pts[i]
        fn = g.m_poly([(x - 2, y - 3), (x, y - 7 - (i % 2)), (x + 2, y - 3)])
        c.paste(fn, g.shade_rows(fn), fin)
    hd = g.m_capsule((55, gy - 36 + sway), (62, gy - 34 + sway), 3.4, 2.4)[0]
    c.paste(hd, g.shade_rows(hd), skin)
    c.px(57, gy - 38 + sway, (230, 220, 90))                            # eye
    for n in range(3):                                                  # needle teeth in the open jaw
        c.px(59 + n, gy - 33 + sway, (240, 236, 220))
    spl = g.m_ellipse(24, gy - 1, 9.0, 2.6)                              # the splash it rises from
    c.paste(spl, g.shade_rows(spl, outline=False), g.ramp((150, 190, 214)))
    return finish(c, shadow=(30, 12))


# ------------------------------------------------------------------------------------------- umibozu shade
def umibozu(k):
    """Umibozu Shade (rare, in storms): a vast dark bald head and shoulders rising out of black water, two pale
    eyes, sea mist curling round it."""
    c = canvas()
    body, mist = g.ramp((36, 40, 58)), g.ramp((120, 136, 160))
    gy = GROUND
    bob = [0, -1, -2, -1][k]
    sh = g.m_ellipse(40, gy - 10 + bob, 20.0, 12.0)
    c.paste(sh, g.shade_rows(sh), body)
    hd = g.m_ellipse(40, gy - 30 + bob, 13.0, 15.0)
    c.paste(hd, g.shade_rows(hd), body)
    for d in (-1, 1):
        c.px(40 + d * 5, gy - 32 + bob, (220, 236, 255)), c.px(40 + d * 5 + d, gy - 32 + bob, (220, 236, 255))
    for n in range(5):                                                  # mist at the waterline
        m = g.m_ellipse(18 + n * 11 + [0, 1, 0, -1][(k + n) % 4], gy - 1, 6.0, 2.0)
        c.paste(m, g.shade_rows(m, outline=False), mist)
    return finish(c, shadow=None)


# ------------------------------------------------------------------------------------------- paper-spirit
def paper_spirit(k):
    """Paper-spirit (tsukumogami, the Kyuden Doji archives; bestiary D): a torn sheet of writing paper standing up
    on its own, flapping, two ink-blot eyes and a slit of a mouth, brush strokes of old text across it."""
    c = canvas()
    paper, ink = g.ramp((232, 226, 204)), g.ramp((40, 36, 44))
    gy = GROUND
    fl = [0, 2, 0, -2][k]
    pts = [(30, gy - 8), (50, gy - 6 + fl // 2), (52 + fl, gy - 40), (44, gy - 44 - fl // 2), (34, gy - 42),
           (28 - fl // 2, gy - 36), (31, gy - 22)]
    sh = g.m_poly(pts)
    c.paste(sh, g.shade_rows(sh), paper)
    for i in range(4):                                                  # columns of old text
        for y in range(gy - 36, gy - 12, 3):
            c.px(46 - i * 4, y + (i % 2), ink[2])
    for x in (36, 43):                                                  # ink-blot eyes
        e = g.m_ellipse(x, gy - 32, 1.8, 2.2)
        c.paste(e, g.shade_rows(e, outline=False), ink)
    for x in range(37, 43):
        c.px(x, gy - 25 + (x % 2), ink[1])
    return finish(c, shadow=(18, 8))


# ------------------------------------------------------------------------------------------- ink-pot spirit
def inkpot(k):
    """Ink-pot Spirit (tsukumogami): a squat glazed ink pot on stubby legs, one big eye in the ink, two ink arms."""
    c = canvas()
    glaze, ink = g.ramp((70, 92, 120)), g.ramp((22, 20, 30))
    gy = GROUND
    bob = [0, -1, -2, -1][k]
    for d in (-1, 1):                                                   # stubby legs
        leg = g.m_capsule((40 + d * 6, gy - 6 + bob), (40 + d * 7, gy - 1), 2.0, 1.6)[0]
        c.paste(leg, g.shade_rows(leg), glaze)
    pot = g.m_ellipse(40, gy - 14 + bob, 12.0, 10.0)
    c.paste(pot, g.shade_rows(pot), glaze)
    lip = g.m_ellipse(40, gy - 23 + bob, 8.0, 2.6)
    c.paste(lip, g.shade_rows(lip, outline=False), ink)
    eye = g.m_ellipse(40, gy - 14 + bob, 4.2, 4.2)
    c.paste(eye, g.shade_rows(eye, outline=False), g.ramp((236, 232, 210)))
    c.px(40 + [0, 1, 0, -1][k], gy - 14 + bob, (20, 16, 24)), c.px(41 + [0, 1, 0, -1][k], gy - 14 + bob, (20, 16, 24))
    for d in (-1, 1):                                                   # ink arms, dripping
        arm = g.m_capsule((40 + d * 8, gy - 22 + bob), (40 + d * 16, gy - 30 - [0, 2, 0, -2][k] * d), 1.8, 1.2)[0]
        c.paste(arm, g.shade_rows(arm), ink)
    return finish(c, shadow=(22, 8))


# ------------------------------------------------------------------------------------------- lantern spirit
def lantern(k):
    """Lantern Spirit (chochin-obake): a paper lantern split into a grin, one huge eye, a long red tongue."""
    c = canvas()
    paper, rib, tongue = g.ramp((238, 214, 150)), g.ramp((120, 70, 40)), g.ramp((210, 60, 70))
    gy = GROUND
    bob = [0, -2, -3, -2][k]
    body = g.m_ellipse(40, gy - 22 + bob, 10.0, 14.0)
    c.paste(body, g.shade_rows(body), paper)
    for y in range(gy - 34 + bob, gy - 8 + bob, 4):                     # bamboo ribs
        for x in range(31, 50):
            if body[y, x] if 0 <= y < body.shape[0] else False:
                c.px(x, y, rib[2])
    for y0 in (gy - 37 + bob, gy - 9 + bob):                            # top and bottom caps
        cap = g.m_ellipse(40, y0, 6.0, 1.8)
        c.paste(cap, g.shade_rows(cap), rib)
    eye = g.m_ellipse(37, gy - 26 + bob, 3.6, 4.0)
    c.paste(eye, g.shade_rows(eye, outline=False), g.ramp((250, 250, 240)))
    c.px(37, gy - 26 + bob, (20, 16, 20))
    mouth = g.m_poly([(32, gy - 18 + bob), (48, gy - 19 + bob), (44, gy - 14 + bob), (35, gy - 14 + bob)])
    c.paste(mouth, g.shade_rows(mouth, outline=False), g.ramp((60, 20, 24)))
    tg = g.m_capsule((42, gy - 15 + bob), (50 + [0, 2, 3, 2][k], gy - 8 + bob), 2.2, 1.4)[0]
    c.paste(tg, g.shade_rows(tg), tongue)
    glow = g.m_ellipse(40, gy - 22 + bob, 4.0, 6.0) & ~eye & ~mouth
    c.paste(glow, g.shade_rows(glow, outline=False), g.ramp((255, 236, 170)))
    return finish(c, shadow=(18, 6))


# ------------------------------------------------------------------------------------------- fear shade
def fear_shade(k):
    """Fear Shade (Ianwa's spawn): a hunched smoke-black shape with long arms, two pale eyes, fraying at the edges."""
    c = canvas()
    body, edge = g.ramp((26, 24, 34)), g.ramp((70, 64, 86))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    sh = g.m_ellipse(40 + sway, gy - 18, 9.0, 15.0)
    c.paste(sh, g.shade_rows(sh), body)
    hd = g.m_ellipse(41 + sway, gy - 35, 6.0, 6.0)
    c.paste(hd, g.shade_rows(hd), body)
    for d in (-1, 1):                                                   # long reaching arms
        arm = g.m_capsule((40 + d * 7 + sway, gy - 26), (40 + d * 14 + sway, gy - 10 - [0, 2, 0, -2][k] * d),
                          2.2, 1.2)[0]
        c.paste(arm, g.shade_rows(arm), body)
    for n in range(6):                                                  # fraying smoke at the hem
        w = g.m_ellipse(31 + n * 4 + (k + n) % 2, gy - 3 - (n * 3 + k) % 4, 2.2, 3.0)
        c.paste(w, g.shade_rows(w, outline=False), edge)
    for d in (-1, 1):
        c.px(41 + d * 2 + sway, gy - 36, (230, 236, 250))
    return finish(c, shadow=(16, 6))


# ------------------------------------------------------------------------------------------- burning bridge
def burning_bridge(k):
    """The Burning Bridge (Lion Ch4 wave 4): a broken span of planks on two piles, flames licking up through it."""
    c = canvas()
    wood, char = g.ramp((120, 84, 50)), g.ramp((46, 34, 30))
    flame, core = g.ramp((236, 110, 40)), g.ramp((255, 220, 120))
    gy = GROUND
    for x in (26, 54):                                                  # the piles
        pile = g.m_capsule((x, gy - 1), (x, gy - 16), 2.4, 2.4)[0]
        c.paste(pile, g.shade_rows(pile), char)
    deck = g.m_poly([(16, gy - 18), (64, gy - 22), (64, gy - 16), (16, gy - 12)])
    c.paste(deck, g.shade_rows(deck), wood)
    for x in range(20, 62, 6):                                          # plank seams, charred
        c.px(x, gy - 15 - (x - 16) // 12, char[1]), c.px(x, gy - 14 - (x - 16) // 12, char[1])
    for n in range(5):                                                  # the flames, flickering
        fx = 22 + n * 9
        h = 9 + (n * 5 + k * 3) % 7
        fl = g.m_poly([(fx - 4, gy - 16 - (fx - 16) // 12), (fx + 4, gy - 17 - (fx - 16) // 12),
                       (fx + [1, -1, 2, 0][(n + k) % 4], gy - 17 - h - (fx - 16) // 12)])
        c.paste(fl, g.shade_rows(fl, outline=False), flame)
        cr = g.m_ellipse(fx, gy - 19 - (fx - 16) // 12, 1.6, 2.6)
        c.paste(cr, g.shade_rows(cr, outline=False), core)
    return finish(c, shadow=(30, 6))


# ------------------------------------------------------------------------------------------- guardian stone
def guardian_stone(k):
    """Guardian-stone shard (Phoenix Ch1 b_shrine_guardian_shards): a broken komainu's head and chest, grey stone
    with moss in the cracks, one carved eye still glowing, lurching on a stump of a plinth."""
    c = canvas()
    stone, moss = g.ramp((150, 150, 142)), g.ramp((96, 120, 70))
    gy = GROUND
    lean = [0, 1, 0, -1][k]
    base = g.m_poly([(30, gy), (50, gy), (48, gy - 7), (32, gy - 7)])
    c.paste(base, g.shade_rows(base), stone)
    body = g.m_poly([(31 + lean, gy - 7), (49 + lean, gy - 7), (47 + lean, gy - 22), (35 + lean, gy - 25)])
    c.paste(body, g.shade_rows(body), stone)
    head = g.m_ellipse(42 + lean, gy - 28, 8.0, 6.5)
    c.paste(head, g.shade_rows(head), stone)
    mane = g.m_ellipse(37 + lean, gy - 30, 4.0, 5.5)
    c.paste(mane, g.shade_rows(mane), g.ramp((128, 128, 120)))
    for x, y in ((36, gy - 14), (44, gy - 19), (40, gy - 10)):           # cracks with moss
        c.px(x + lean, y, moss[2]), c.px(x + 1 + lean, y + 1, moss[1]), c.px(x + 2 + lean, y + 1, moss[2])
    c.px(46 + lean, gy - 29, (240, 230, 160)), c.px(47 + lean, gy - 29, (255, 250, 200))   # the carved eye, lit
    for n in range(3):                                                  # a chip falling off
        c.px(51 + lean, gy - 12 + n * 3 + k, stone[1])
    return finish(c, shadow=(20, 6))


# ------------------------------------------------------------------------------------------- the Darkfever
def fever_spirit(k):
    """Fever Spirit (Phoenix Ch3): bruised smoke with a hot core and dark veins, drifting."""
    c = canvas()
    smoke, vein, core = g.ramp((96, 70, 104)), g.ramp((40, 24, 48)), g.ramp((236, 160, 120))
    gy = GROUND
    bob = [0, -2, -3, -1][k]
    for n in range(5):
        p = g.m_ellipse(34 + n * 3 + (k + n) % 2, gy - 14 - n * 3 + bob, 7.0 - n * 0.6, 6.0 - n * 0.4)
        c.paste(p, g.shade_rows(p, outline=n == 0), smoke)
    cr = g.m_ellipse(41, gy - 20 + bob, 3.2, 3.2)
    c.paste(cr, g.shade_rows(cr, outline=False), core)
    for x, y in ((36, -16), (44, -24), (39, -28), (46, -14)):
        c.px(x, gy + y + bob, vein[1]), c.px(x + 1, gy + y + 1 + bob, vein[2])
    return finish(c, shadow=(16, 5))


def gaki(k):
    """Gaki (hungry ghost): a starved grey figure with a swollen belly, needle-thin neck, a huge empty mouth."""
    c = canvas()
    skin, dark = g.ramp((150, 156, 150)), g.ramp((40, 30, 36))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    for d in (-1, 1):
        leg = g.m_capsule((40 + d * 3, gy - 12), (40 + d * 4, gy - 1), 1.4, 1.2)[0]
        c.paste(leg, g.shade_rows(leg), skin)
    belly = g.m_ellipse(40 + sway, gy - 16, 7.0, 6.0)
    c.paste(belly, g.shade_rows(belly), skin)
    neck = g.m_capsule((40 + sway, gy - 22), (41 + sway, gy - 30), 1.0, 1.0)[0]
    c.paste(neck, g.shade_rows(neck), skin)
    head = g.m_ellipse(41 + sway, gy - 34, 5.0, 4.6)
    c.paste(head, g.shade_rows(head), skin)
    mouth = g.m_ellipse(43 + sway, gy - 32, 2.6, 2.2)
    c.paste(mouth, g.shade_rows(mouth, outline=False), dark)
    for d in (-1, 1):
        arm = g.m_capsule((40 + d * 5 + sway, gy - 20), (40 + d * 10 + sway, gy - 10 - [0, 1, 0, -1][k]), 1.0, 0.8)[0]
        c.paste(arm, g.shade_rows(arm), skin)
    c.px(42 + sway, gy - 36, (240, 230, 160))
    return finish(c, shadow=(14, 5))


def tsuchigumo(k):
    """Tsuchigumo (earth spider): a big dark spider with a demon's face on its back and eight jointed legs."""
    c = canvas()
    body, face = g.ramp((70, 56, 50)), g.ramp((170, 70, 60))
    gy = GROUND
    lift = [0, -1, 0, 1][k]
    for n in range(4):
        for d in (-1, 1):
            kx = 40 + d * (8 + n * 3)
            leg = g.m_capsule((40 + d * 4, gy - 12 + lift), (kx, gy - 18 + n + lift), 1.2, 1.0)[0]
            c.paste(leg, g.shade_rows(leg), body)
            foot = g.m_capsule((kx, gy - 18 + n + lift), (kx + d * 3, gy - 1), 1.0, 0.8)[0]
            c.paste(foot, g.shade_rows(foot), body)
    ab = g.m_ellipse(40, gy - 13 + lift, 10.0, 7.0)
    c.paste(ab, g.shade_rows(ab), body)
    fc = g.m_ellipse(40, gy - 14 + lift, 4.5, 3.6)
    c.paste(fc, g.shade_rows(fc, outline=False), face)
    for d in (-1, 1):
        c.px(40 + d * 2, gy - 15 + lift, (250, 230, 120))
    return finish(c, shadow=(26, 6))


def kappa(k):
    """Kappa (river imp): a green, turtle-backed child-sized imp with a beak and a water-filled dish on its head."""
    c = canvas()
    skin, shell, dish = g.ramp((90, 150, 80)), g.ramp((110, 90, 50)), g.ramp((200, 210, 200))
    gy = GROUND
    bob = [0, -1, 0, 1][k]
    for d in (-1, 1):
        leg = g.m_capsule((40 + d * 3, gy - 9 + bob), (40 + d * 4, gy - 1), 1.6, 1.4)[0]
        c.paste(leg, g.shade_rows(leg), skin)
    back = g.m_ellipse(37, gy - 14 + bob, 7.0, 7.5)
    c.paste(back, g.shade_rows(back), shell)
    body = g.m_ellipse(41, gy - 14 + bob, 5.5, 6.5)
    c.paste(body, g.shade_rows(body), skin)
    head = g.m_ellipse(42, gy - 24 + bob, 5.0, 4.4)
    c.paste(head, g.shade_rows(head), skin)
    beak = g.m_ellipse(47, gy - 23 + bob, 2.4, 1.4)
    c.paste(beak, g.shade_rows(beak, outline=False), g.ramp((220, 190, 80)))
    top = g.m_ellipse(42, gy - 28 + bob, 3.6, 1.2)
    c.paste(top, g.shade_rows(top, outline=False), dish)
    c.px(42, gy - 28 + bob, (120, 170, 230))
    c.px(43, gy - 28 + bob, (120, 170, 230))
    for d in (-1, 1):
        arm = g.m_capsule((41 + d * 4, gy - 17 + bob), (44 + d * 5, gy - 10 - [0, 1, 0, -1][k]), 1.1, 0.9)[0]
        c.paste(arm, g.shade_rows(arm), skin)
    c.px(44, gy - 25 + bob, (250, 230, 120))
    return finish(c, shadow=(16, 5))


def blood_leech(k):
    """Blood Leech (Scorpion Ch1, the River of Gold marsh; bestiary I): a swollen, segmented dark-red leech as long as
    a dog, its front end reared up to strike with a round sucker ringed with teeth. It glistens."""
    c = canvas()
    skin, belly = g.ramp((120, 30, 40)), g.ramp((170, 70, 70))
    gy = GROUND
    rear = [0, -1, -2, -1][k]
    pts = [(24, gy - 4), (30, gy - 5), (36, gy - 6), (41, gy - 10 + rear), (44, gy - 16 + rear),
           (46, gy - 21 + rear)]
    for n, (x, y) in enumerate(pts):                                       # body segments, fatter in the middle
        r = (3.2, 4.2, 4.8, 4.4, 3.8, 3.4)[n]
        seg = g.m_ellipse(x, y, r + 0.6, r)
        c.paste(seg, g.shade_rows(seg), skin)
        lo = seg & (YY > y + 1)
        c.paste(lo, g.shade_rows(lo, outline=False), belly)
    mouth = g.m_ellipse(48, gy - 23 + rear, 2.6, 2.6)                      # the sucker
    c.paste(mouth, g.shade_rows(mouth, outline=False), g.ramp((60, 14, 22)))
    for a in range(0, 360, 60):                                            # teeth round the rim
        c.px(48 + int(round(2.4 * math.cos(math.radians(a)))), gy - 23 + rear + int(round(2.4 * math.sin(
            math.radians(a)))), (236, 220, 200))
    for x, y in ((30, -8), (36, -10), (42, -14 + rear)):                  # wet highlights
        c.px(x, gy + y, (236, 160, 160))
    return finish(c, shadow=(18, 4))


def paddy_python(k):
    """Paddy Python (Scorpion Ch2, the plains north of Shiro no Soshi; bestiary II): a thick olive snake in coils,
    blotched brown, its head raised over the loops, tongue out."""
    c = canvas()
    skin, blot = g.ramp((110, 120, 60)), g.ramp((80, 62, 40))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    for n, (x, y, rx, ry) in enumerate(((28, -4, 9, 4.2), (36, -6, 7, 4.6), (31, -11, 7.5, 4.2), (37, -15, 5, 3.6))):
        coil = g.m_ellipse(x, gy + y, rx, ry)                               # the stacked coils
        c.paste(coil, g.shade_rows(coil), skin)
        for d in (-4, 1):
            c.px(x + d, gy + y - 1, blot[1]), c.px(x + d + 1, gy + y, blot[1])
    neck = g.m_capsule((40, gy - 15), (44 + sway, gy - 24), 2.4, 2.0)[0]
    c.paste(neck, g.shade_rows(neck), skin)
    head = g.m_ellipse(46 + sway, gy - 25, 3.6, 2.4)
    c.paste(head, g.shade_rows(head), skin)
    c.px(47 + sway, gy - 26, (240, 210, 90))
    c.px(50 + sway, gy - 24, (200, 40, 50)), c.px(51 + sway, gy - 23, (200, 40, 50))   # the tongue
    return finish(c, shadow=(18, 4))


def giant_hornet(k):
    """Giant Hornet (Scorpion Ch2 plains; bestiary II): a hornet the size of a cat, yellow and black, wings a blur."""
    c = canvas()
    yel, blk = g.ramp((230, 180, 50)), g.ramp((40, 34, 30))
    gy = GROUND - 14 + [0, -2, 0, 2][k]
    ab = g.m_ellipse(34, gy, 6.5, 4.0)                                      # the abdomen, striped
    c.paste(ab, g.shade_rows(ab), yel)
    for x in (31, 34, 37):
        st = ab & (g.XX >= x) & (g.XX < x + 1)
        c.paste(st, g.shade_rows(st, outline=False), blk)
    c.px(27, gy + 1, blk[0]), c.px(26, gy + 2, blk[0])                     # the sting
    th = g.m_ellipse(42, gy - 2, 3.6, 3.2)
    c.paste(th, g.shade_rows(th), blk)
    hd = g.m_ellipse(47, gy - 2, 2.8, 2.6)
    c.paste(hd, g.shade_rows(hd), yel)
    c.px(48, gy - 3, (30, 20, 20))
    wing = g.m_ellipse(40, gy - 8 - [0, 2, 0, 2][k], 5.0, 2.4)            # a blur of wing
    c.col[wing & (c.col[..., 3] == 0)] = (230, 236, 246, 150)
    for d in (-2, 1, 4):
        leg = g.m_capsule((41 + d, gy + 2), (40 + d, gy + 6), 0.6, 0.5)[0]
        c.paste(leg, g.shade_rows(leg, outline=False), blk)
    return finish(c, shadow=(10, 3))


# ------------------------------------------------------------------------------------------- Mieko's shadow
def mieko_shadow(k):
    """Mieko's shadow (Phoenix Ch4): a girl's silhouette in black glass, long hair streaming, two pale glints for
    eyes, cracks of violet light running through her."""
    c = canvas()
    body, crack = g.ramp((30, 24, 44)), g.ramp((150, 110, 210))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    robe = g.m_poly([(34 + sway, gy - 24), (46 + sway, gy - 24), (50, gy), (30, gy)])
    c.paste(robe, g.shade_rows(robe), body)
    head = g.m_ellipse(40 + sway, gy - 29, 4.5, 5.0)
    c.paste(head, g.shade_rows(head), body)
    hair = g.m_poly([(36 + sway, gy - 31), (44 + sway, gy - 31), (47 + sway * 2, gy - 12), (35 + sway * 2, gy - 12)])
    c.paste(hair, g.shade_rows(hair, outline=False), body)
    for x, y in ((38, -20), (42, -14), (40, -8), (44, -22)):           # violet cracks
        c.px(x + sway, gy + y, crack[2]), c.px(x + 1 + sway, gy + y + 1, crack[1])
    for d in (-1, 1):
        c.px(40 + d * 2 + sway, gy - 30, (236, 240, 255))
    return finish(c, shadow=(14, 5))


# ------------------------------------------------------------------------------------------- grey wolf
def grey_wolf(k):
    """Grey Wolf (bestiary F "Crane coast & Beiden forest"): the wolf-rider's wolf without the goblin, leaner and
    lighter grey, head lowered to stalk."""
    c = canvas()
    fur, belly = g.ramp((128, 126, 130)), g.ramp((184, 180, 172))
    gy = GROUND
    br = [0, -1, 0, 1][k]
    gait = [(0, 2), (2, 0), (0, -2), (-2, 0)][k]
    for n, (x, near) in enumerate(((25, False), (29, True), (41, False), (45, True))):
        dx = gait[0] if n % 2 else gait[1]
        lg = g.m_capsule((x, gy - 14 + br), (x + dx, gy - 2), 2.2, 1.4)[0]
        t = g.shade_rows(lg)
        if not near:
            t[lg & (t >= 2)] -= 1
        c.paste(lg, t, fur)
        c.px(x + dx, gy - 1, (50, 46, 50))
    tail = g.m_capsule((21, gy - 19 + br), (12, gy - 15 + br + [0, 1, 0, -1][k]), 2.2, 1.1)[0]   # tail held low
    c.paste(tail, g.shade_rows(tail), fur)
    body = g.m_ellipse(35, gy - 18 + br, 12.5, 6.0)
    c.paste(body, g.shade_rows(body), fur)
    bl = body & (YY > gy - 16 + br)
    c.paste(bl, g.shade_rows(bl, outline=False), belly)
    nk = g.m_capsule((45, gy - 19 + br), (50, gy - 21 + br), 4.0, 3.2)[0]
    c.paste(nk, g.shade_rows(nk), fur)
    hd = g.m_capsule((50, gy - 21 + br), (59, gy - 18 + br), 3.6, 2.0)[0]      # head down, snout forward
    c.paste(hd, g.shade_rows(hd), fur)
    for ex in (49, 52):
        er = g.m_poly([(ex, gy - 23 + br), (ex + 2, gy - 29 + br), (ex + 3, gy - 23 + br)])
        c.paste(er, g.shade_rows(er), fur)
    c.px(54, gy - 22 + br, (240, 200, 90)), c.px(58, gy - 16 + br, (250, 240, 230))   # eye, a fang
    c.px(59, gy - 19 + br, (30, 24, 24))
    return finish(c, shadow=(36, 14))


# ------------------------------------------------------------------------------------------- bakemono wolf-rider
def wolfrider(k):
    """A goblin riding a big grey Shadowlands wolf (bestiary IV, two-part target). Drawn at half scale."""
    c = canvas()
    fur, belly, gob = g.ramp((98, 96, 104)), g.ramp((150, 146, 140)), g.ramp((112, 140, 78))
    leather, iron = g.ramp((96, 64, 42)), g.ramp((120, 120, 128))
    gy = GROUND
    br = [0, -1, 0, 1][k]
    gait = [(0, 2), (2, 0), (0, -2), (-2, 0)][k]
    for n, (x, near) in enumerate(((24, False), (28, True), (42, False), (46, True))):
        dx = gait[0] if n % 2 else gait[1]
        lg = g.m_capsule((x, gy - 17 + br), (x + dx, gy - 2), 2.6, 1.6)[0]
        t = g.shade_rows(lg)
        if not near:
            t[lg & (t >= 2)] -= 1
        c.paste(lg, t, fur)
        c.px(x + dx, gy - 1, (40, 36, 40)), c.px(x + dx + 1, gy - 1, (40, 36, 40))
    tail = g.m_capsule((20, gy - 24 + br), (10, gy - 30 + br + [0, 1, 0, -1][k]), 2.4, 1.2)[0]
    c.paste(tail, g.shade_rows(tail), fur)
    body = g.m_ellipse(35, gy - 21 + br, 14.0, 7.0)
    c.paste(body, g.shade_rows(body), fur)
    bl = body & (YY > gy - 19 + br)
    c.paste(bl, g.shade_rows(bl, outline=False), belly)
    nk = g.m_capsule((46, gy - 23 + br), (52, gy - 30 + br), 4.6, 3.6)[0]
    c.paste(nk, g.shade_rows(nk), fur)
    hd = g.m_capsule((51, gy - 31 + br), (61, gy - 28 + br), 4.0, 2.2)[0]            # long wolf snout
    c.paste(hd, g.shade_rows(hd), fur)
    for ex in (49, 52):                                                         # ears
        er = g.m_poly([(ex, gy - 33 + br), (ex + 2, gy - 39 + br), (ex + 3, gy - 33 + br)])
        c.paste(er, g.shade_rows(er), fur)
    c.px(55, gy - 32 + br, (255, 200, 60)), c.px(60, gy - 27 + br, (250, 240, 230))   # eye, a fang
    c.px(61, gy - 29 + br, (30, 24, 24))
    sad = g.m_ellipse(34, gy - 28 + br, 6.0, 2.0)                                # saddle
    c.paste(sad, g.shade_rows(sad), leather)
    rb = [0, 0, -1, 0][k]                                                       # the rider bobs a beat behind
    leg = g.m_capsule((34, gy - 29 + br), (38, gy - 23 + br), 1.6, 1.4)[0]
    c.paste(leg, g.shade_rows(leg), gob)
    tor = g.m_capsule((33, gy - 30 + br + rb), (35, gy - 38 + br + rb), 3.4, 3.0)[0]
    c.paste(tor, g.shade_rows(tor), gob)
    vest = tor & (YY > gy - 36 + br + rb)
    c.paste(vest, g.shade_rows(vest, outline=False), leather)
    gh = g.m_ellipse(36, gy - 42 + br + rb, 3.6, 3.2)
    c.paste(gh, g.shade_rows(gh), gob)
    for d in (-1, 1):                                                           # long goblin ears
        ge = g.m_poly([(36 + d * 2, gy - 43 + br + rb), (36 + d * 6, gy - 46 + br + rb), (36 + d * 3, gy - 41 + br + rb)])
        c.paste(ge, g.shade_rows(ge), gob)
    c.px(38, gy - 43 + br + rb, (255, 60, 40))                                  # red eye
    sp = g.m_capsule((30, gy - 30 + br + rb), (54, gy - 47 + br + rb), 0.7)[0]   # a crude spear
    c.paste(sp, g.shade_rows(sp, outline=False), leather)
    tip = g.m_poly([(54, gy - 47 + br + rb), (58, gy - 51 + br + rb), (55, gy - 45 + br + rb)])
    c.paste(tip, g.shade_rows(tip), iron)
    return finish(c, shadow=(36, 15))


# ------------------------------------------------------------------------------------------- Scorpion Ch4
def snow_bear(k):
    """Snow Bear (bestiary III; the Dragon mountains): a big white bear on all fours, black muzzle and claws, head low
    and swinging."""
    c = canvas()
    fur, shade, dark = g.ramp((226, 230, 236)), g.ramp((184, 192, 206)), g.ramp((40, 38, 44))
    gy = GROUND
    br = [0, -1, 0, 1][k]
    gait = [(0, 1), (1, 0), (0, -1), (-1, 0)][k]
    for n, (x, near) in enumerate(((23, False), (28, True), (42, False), (47, True))):
        dx = gait[0] if n % 2 else gait[1]
        lg = g.m_capsule((x, gy - 14 + br), (x + dx, gy - 2), 3.4, 2.6)[0]
        t = g.shade_rows(lg)
        if not near:
            t[lg & (t >= 2)] -= 1
        c.paste(lg, t, fur if near else shade)
        for cl in range(3):
            c.px(x + dx - 1 + cl, gy - 1, dark[1])
    body = g.m_ellipse(35, gy - 18 + br, 15.0, 9.0)
    c.paste(body, g.shade_rows(body), fur)
    hump = g.m_ellipse(30, gy - 24 + br, 7.0, 4.0)
    c.paste(hump, g.shade_rows(hump), fur)
    hd = g.m_ellipse(52, gy - 18 + br + gait[0], 6.0, 5.0)
    c.paste(hd, g.shade_rows(hd), fur)
    mz = g.m_ellipse(57, gy - 16 + br + gait[0], 3.0, 2.4)
    c.paste(mz, g.shade_rows(mz, outline=False), shade)
    c.px(59, gy - 17 + br + gait[0], dark[0])                          # nose
    for ex in (48, 52):
        er = g.m_ellipse(ex, gy - 23 + br + gait[0], 1.6, 1.4)
        c.paste(er, g.shade_rows(er), fur)
    c.px(54, gy - 20 + br + gait[0], dark[0])                          # a small black eye
    return finish(c, shadow=(40, 14))


def tengu(k):
    """Tengu Crow-Warrior (bestiary III): a crow-headed swordsman in a dark kimono, black wings half open, a katana
    held low."""
    c = canvas()
    ink, robe, belt = g.ramp((36, 38, 56)), g.ramp((70, 60, 92)), g.ramp((170, 60, 50))
    beak, steel = g.ramp((210, 180, 70)), g.ramp((200, 206, 216))
    gy = GROUND
    bob = [0, -1, 0, 1][k]
    flap = [0, -2, -3, -1][k]
    for sgn, dark in ((-1, True), (1, False)):                         # wings behind
        w = g.m_poly([(38, gy - 30 + bob), (38 - 14 + sgn, gy - 38 + flap), (38 - 16, gy - 24 + flap),
                      (38 - 10, gy - 16), (40, gy - 20 + bob)])
        t = g.shade_rows(w)
        if dark:
            t[w & (t >= 2)] -= 1
        c.paste(w, t, ink)
    for d in (-1, 1):
        lg = g.m_capsule((40 + d * 3, gy - 12 + bob), (40 + d * 4, gy - 1), 1.6, 1.2)[0]
        c.paste(lg, g.shade_rows(lg), robe)
    body = g.m_poly([(34, gy - 30 + bob), (46, gy - 30 + bob), (48, gy - 10 + bob), (32, gy - 10 + bob)])
    c.paste(body, g.shade_rows(body), robe)
    bl = body & (YY >= gy - 20 + bob) & (YY <= gy - 18 + bob)
    c.paste(bl, g.shade_rows(bl, outline=False), belt)
    hd = g.m_ellipse(41, gy - 35 + bob, 5.0, 4.6)
    c.paste(hd, g.shade_rows(hd), ink)
    bk = g.m_poly([(44, gy - 37 + bob), (52, gy - 33 + bob), (44, gy - 32 + bob)])
    c.paste(bk, g.shade_rows(bk, outline=False), beak)
    c.px(43, gy - 37 + bob, (250, 90, 60))                             # a red eye
    arm = g.m_capsule((44, gy - 26 + bob), (50, gy - 18 + bob), 1.6, 1.4)[0]
    c.paste(arm, g.shade_rows(arm), robe)
    sw = g.m_capsule((50, gy - 18 + bob), (60, gy - 6 + bob + [0, 1, 2, 1][k]), 0.8, 0.6)[0]
    c.paste(sw, g.shade_rows(sw, outline=False), steel)
    return finish(c, shadow=(18, 5))


def fire_elemental(k):
    """Fire Elemental (bestiary D IV; Tamori's Furnace): a walking column of flame, a coal for a heart, two white-hot
    eyes, sparks rising."""
    c = canvas()
    outer, inner, core = g.ramp((220, 70, 30)), g.ramp((250, 170, 50)), g.ramp((255, 240, 190))
    gy = GROUND
    fl = [0, -2, -1, 1][k]
    shape = g.m_poly([(30, gy), (50, gy), (48, gy - 14), (52, gy - 26 + fl), (46, gy - 22), (44, gy - 38 + fl),
                      (40, gy - 30), (36, gy - 42 - fl), (34, gy - 26), (28, gy - 30 + fl), (31, gy - 14)])
    c.paste(shape, g.shade_rows(shape), outer)
    mid = g.m_poly([(34, gy - 2), (46, gy - 2), (44, gy - 16), (41, gy - 28 + fl), (37, gy - 22), (35, gy - 14)])
    c.paste(mid, g.shade_rows(mid, outline=False), inner)
    hc = g.m_ellipse(40, gy - 12, 3.0, 3.0)
    c.paste(hc, g.shade_rows(hc, outline=False), core)
    c.px(38, gy - 24 + fl, (255, 255, 240)), c.px(42, gy - 24 + fl, (255, 255, 240))   # eyes
    out = finish(c, shadow=(18, 5))
    d = ImageDraw.Draw(out)
    for n, (sx, sy) in enumerate(((30, gy - 40), (48, gy - 44), (38, gy - 50))):       # sparks rising
        sy -= (k * 3 + n * 4) % 10
        d.point((sx, sy), fill=(255, 210, 90, 255))
    return out


def ash_ghoul(k):
    """Ash Ghoul (Tamori's Furnace): a hunched pilgrim made of grey ash, the shape of a straw hat still on its head,
    embers glowing in its cracks, ash falling off its arms."""
    c = canvas()
    ash, dark, ember = g.ramp((150, 146, 140)), g.ramp((70, 66, 64)), g.ramp((240, 120, 50))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    for d in (-1, 1):
        lg = g.m_capsule((40 + d * 3, gy - 12), (40 + d * 4, gy - 1), 1.8, 1.4)[0]
        c.paste(lg, g.shade_rows(lg), ash)
    body = g.m_ellipse(40 + sway, gy - 18, 7.0, 8.0)
    c.paste(body, g.shade_rows(body), ash)
    hd = g.m_ellipse(44 + sway, gy - 28, 4.4, 4.0)
    c.paste(hd, g.shade_rows(hd), ash)
    hat = g.m_poly([(37 + sway, gy - 30), (44 + sway, gy - 36), (52 + sway, gy - 30)])
    c.paste(hat, g.shade_rows(hat), dark)
    for d in (-1, 1):
        arm = g.m_capsule((40 + d * 5 + sway, gy - 22), (46 + d * 2 + sway, gy - 12 - [0, 1, 0, -1][k]), 1.4, 1.0)[0]
        c.paste(arm, g.shade_rows(arm), ash)
    for x, y in ((38, -20), (42, -14), (36, -12), (45, -27)):           # embers in the cracks
        c.px(x + sway, gy + y, ember[2]), c.px(x + 1 + sway, gy + y + 1, ember[1])
    c.px(46 + sway, gy - 29, (255, 160, 60))                           # an ember eye
    out = finish(c, shadow=(16, 5))
    d = ImageDraw.Draw(out)
    for n in range(3):                                                 # ash falling
        d.point((34 + n * 7, gy - 10 + (k * 2 + n * 3) % 8), fill=(170, 166, 160, 200))
    return out


# ------------------------------------------------------------------------------------------- Unicorn Ch1
def pony(k):
    """Persimmon (Unicorn Ch1): Tamotsu's small chestnut pony with a shaggy dark mane, ears back, glaring."""
    c = canvas()
    coat, mane, hoof = g.ramp((150, 80, 44)), g.ramp((54, 36, 30)), g.ramp((40, 34, 30))
    gy = GROUND
    br = [0, -1, 0, 1][k]
    for n, (x, near) in enumerate(((27, False), (31, True), (41, False), (45, True))):
        lg = g.m_capsule((x, gy - 13 + br), (x, gy - 2), 1.9, 1.5)[0]
        t = g.shade_rows(lg)
        if not near:
            t[lg & (t >= 2)] -= 1
        c.paste(lg, t, coat)
        c.px(x, gy - 1, hoof[0]), c.px(x + 1, gy - 1, hoof[0])
    tail = g.m_capsule((23, gy - 18 + br), (19, gy - 9 + br), 2.0, 1.2)[0]
    c.paste(tail, g.shade_rows(tail), mane)
    body = g.m_ellipse(36, gy - 17 + br, 11.0, 6.0)
    c.paste(body, g.shade_rows(body), coat)
    nk = g.m_capsule((44, gy - 19 + br), (48, gy - 26 + br), 3.6, 2.8)[0]
    c.paste(nk, g.shade_rows(nk), coat)
    hd = g.m_capsule((48, gy - 27 + br), (55, gy - 23 + br), 3.0, 2.0)[0]
    c.paste(hd, g.shade_rows(hd), coat)
    mn = g.m_capsule((43, gy - 22 + br), (47, gy - 30 + br), 1.6, 1.4)[0]            # the shaggy mane
    c.paste(mn, g.shade_rows(mn), mane)
    for ex in (47, 49):                                                         # ears laid back: she's cross
        c.px(ex - 1, gy - 30 + br, coat[2]), c.px(ex - 2, gy - 31 + br, coat[1])
    c.px(51, gy - 27 + br, (20, 14, 12)), c.px(52, gy - 28 + br, (20, 14, 12))     # a glare
    return finish(c, shadow=(30, 10))


def woodchuck(k):
    """Iuchi Daiyu's woodchuck (Unicorn Ch1): a plump brown woodchuck sitting up on its haunches, paws together."""
    c = canvas()
    fur, belly = g.ramp((120, 90, 60)), g.ramp((170, 140, 100))
    gy = GROUND
    bob = [0, 0, -1, 0][k]
    body = g.m_ellipse(40, gy - 6 + bob, 5.0, 6.0)
    c.paste(body, g.shade_rows(body), fur)
    bl = g.m_ellipse(41, gy - 5 + bob, 2.6, 4.0)
    c.paste(bl, g.shade_rows(bl, outline=False), belly)
    hd = g.m_ellipse(41, gy - 13 + bob, 3.4, 3.0)
    c.paste(hd, g.shade_rows(hd), fur)
    c.px(42, gy - 14 + bob, (20, 16, 12)), c.px(44, gy - 12 + bob, (40, 30, 26))   # eye, nose
    c.px(42, gy - 8 + bob, belly[3]), c.px(43, gy - 8 + bob, belly[3])            # paws together
    return finish(c, shadow=(8, 3))


def powder_keg(k):
    """Powder Keg (Unicorn Ch1 boss): a squat iron-hooped barrel of gaijin pepper, a fuse curling from the lid."""
    c = canvas()
    wood, hoop = g.ramp((130, 90, 52)), g.ramp((70, 70, 76))
    gy = GROUND
    b = g.m_ellipse(40, gy - 8, 7.0, 8.0) & (YY > gy - 15) & (YY < gy)
    c.paste(b, g.shade_rows(b), wood)
    for y in (gy - 12, gy - 4):
        h = b & (YY >= y) & (YY < y + 1)
        c.paste(h, g.shade_rows(h, outline=False), hoop)
    out = finish(c, shadow=(14, 4))
    d = ImageDraw.Draw(out)
    fx = [0, 1, 0, -1][k]
    d.line([(41, gy - 15), (43 + fx, gy - 19), (42, gy - 21)], fill=(60, 50, 40, 255))   # the fuse
    if k % 2 == 0:
        d.point((42, gy - 22), fill=(255, 210, 90, 255))                                  # a spark
    return out


def bloodstone_basin(k):
    """The Bloodstone Basin (Ronin Ch3 boss; Past Heroes: "a large stone bird bath on a pedestal filled with little black
    pebbles" - bloodstones, made when pure blood touches impure stone): a grey stone basin on a pedestal, heaped with
    red stones that pulse."""
    c = canvas()
    stone = g.ramp((120, 118, 124))
    gy = GROUND
    ped = (XX >= 36) & (XX <= 44) & (YY > gy - 12) & (YY < gy)
    c.paste(ped, g.shade_rows(ped), stone)
    foot = (XX >= 32) & (XX <= 48) & (YY >= gy - 3) & (YY < gy)
    c.paste(foot, g.shade_rows(foot), stone)
    bowl = g.m_ellipse(40, gy - 15, 12.0, 5.0) & (YY > gy - 17)
    c.paste(bowl, g.shade_rows(bowl), stone)
    out = finish(c, shadow=(18, 4))
    d = ImageDraw.Draw(out)
    glow = [(200, 40, 40, 255), (230, 70, 60, 255), (170, 20, 30, 255), (240, 110, 90, 255)]
    for i, (x, y) in enumerate(((32, gy - 18), (35, gy - 19), (38, gy - 18), (41, gy - 19), (44, gy - 18),
                                (47, gy - 18), (36, gy - 17), (40, gy - 17), (43, gy - 17))):
        d.rectangle([x, y, x + 1, y + 1], fill=glow[(i + k) % 4])                      # the bloodstones, pulsing
    return out


def naga_scout(k):
    """Naga Scout (the finale's Shinomen; bestiary B2 V): a pearl-and-bronze serpent warrior, the long body coiled on
    the moss, a green-bronze torso rising from it under a ribbed hood, a spear tipped with a pearl."""
    c = canvas()
    scale, band = g.ramp((214, 208, 186)), g.ramp((168, 120, 60))
    skin, hood = g.ramp((96, 132, 108)), g.ramp((150, 110, 58))
    gy = GROUND
    sway = [0, 1, 0, -1][k]
    for n, (x, y, rx, ry) in enumerate(((10, -3, 5, 2.6), (17, -5, 6, 3.2), (25, -4, 9, 4.2), (36, -4, 9, 4.2),
                                        (31, -9, 8.5, 4.0), (35, -12, 6, 3.4))):
        coil = g.m_ellipse(x, gy + y, rx, ry)                               # the long body, coiled on the moss
        t = g.shade_rows(coil)
        t[coil & ((XX % 4) == 0) & (t >= 2)] = 1                            # scale rows
        c.paste(coil, t, scale)
        bb = coil & (np.abs(XX + 0.5 - (x + 3)) < 0.8)
        c.paste(bb, g.shade_rows(bb, outline=False), band)                  # bronze bands
    tip = g.m_capsule((6, gy - 3), (1, gy - 8 + sway), 1.8, 0.5)[0]
    c.paste(tip, g.shade_rows(tip), scale)
    torso = g.m_capsule((36, gy - 11), (38 + sway * 0.5, gy - 27), 4.6, 3.8)[0]
    c.paste(torso, g.shade_rows(torso), skin)
    plate = torso & (YY > gy - 26) & (YY < gy - 17)
    pt = g.shade_rows(plate, outline=False)
    pt[plate & ((YY % 3) == 0) & (pt >= 2)] = 1
    c.paste(plate, pt, band)                                                # a bronze cuirass
    hd = g.m_ellipse(38 + sway * 0.5, gy - 35, 7.0, 6.5) & (XX < 40 + sway)
    ht = g.shade_rows(hd)
    ht[hd & ((XX % 2) == 0) & (ht >= 2)] -= 1                               # the ribbed hood behind the head
    c.paste(hd, ht, hood)
    head = g.m_ellipse(40 + sway * 0.5, gy - 33, 3.4, 3.8)
    c.paste(head, g.shade_rows(head), skin)
    c.px(42 + sway * 0.5, gy - 34, (250, 220, 90))                           # a slit-pupil eye
    g.draw_limb(c, (39, gy - 25), (46, gy - 20), 1.6, 1.3, skin)            # the spear arm
    g.line(c, (47, gy - 1), (49, gy - 46), g.ramp((120, 86, 50)), 1)
    pearl = g.m_ellipse(49, gy - 47, 1.8, 1.8)
    c.paste(pearl, g.shade_rows(pearl, dither=False), g.ramp((236, 238, 246)))
    c.keep |= pearl
    hand = g.m_ellipse(47, gy - 20, 1.4, 1.2)
    c.paste(hand, g.shade_rows(hand), skin)
    return finish(c, shadow=(28, 12))


def lava_dryad(k):
    """Lava Tree Dryad (bestiary D V; the Shadowlands' roots-up Lava Trees, and now the Shinomen's edge): a woman of
    charred bark with fire in the cracks, roots for hair reaching up, branch arms dripping embers."""
    c = canvas()
    bark, ember = g.ramp((70, 48, 40)), g.ramp((250, 130, 40))
    gy = GROUND
    fl = [0, -1, 0, 1][k]
    for d in (-1, 1):                                                       # the roots she stands on
        for n in range(3):
            r = g.m_capsule((40, gy - 6), (40 + d * (6 + n * 4), gy - (n % 2)), 1.6, 0.6)[0]
            c.paste(r, g.shade_rows(r), bark)
    body = g.m_poly([(35, gy - 2), (45, gy - 2), (44, gy - 16), (46, gy - 28), (34, gy - 28), (36, gy - 16)])
    c.paste(body, g.shade_rows(body), bark)
    for d in (-1, 1):                                                       # branch arms, raised a little
        g.draw_limb(c, (40 + d * 5, gy - 26), (40 + d * 11, gy - 20 + fl), 1.8, 1.2, bark)
        g.draw_limb(c, (40 + d * 11, gy - 20 + fl), (40 + d * 15, gy - 24 + fl), 1.2, 0.7, bark)
    head = g.m_ellipse(40, gy - 32, 3.8, 4.2)
    c.paste(head, g.shade_rows(head), bark)
    for n, (dx, h) in enumerate(((-5, 9), (-2, 12), (1, 13), (4, 10), (6, 7))):   # roots-up hair
        g.line(c, (40 + dx * 0.4, gy - 35), (40 + dx, gy - 35 - h + (fl if n % 2 else 0)), bark, 1)
    cracks = (body | head) & (((XX * 3 + YY * 2) % 11) == 0) & ~g.edges(body | head)
    c.paste(cracks, np.zeros((FH, FW), int) + 4, ember)                     # fire in the cracks
    c.keep |= cracks
    for d in (-1, 1):
        c.px(40 + d * 1.5, gy - 33, (255, 230, 120))                         # eyes like coals
    out = finish(c, shadow=(22, 7))
    dr = ImageDraw.Draw(out)
    for n, sx in enumerate((26, 54, 30, 50)):                               # embers dripping from the branches
        dr.point((sx, gy - 18 + (k * 3 + n * 5) % 12), fill=(255, 160, 60, 255))
    return out


def kumo_brood(k):
    """Kumo Brood (the finale's Shinomen; bestiary B3 IV): a pale violet spider the size of a dog, long jointed legs
    raised high, a striped abdomen and a cluster of red eyes."""
    c = canvas()
    body, stripe, eye = g.ramp((150, 120, 170)), g.ramp((90, 60, 110)), (230, 40, 50)
    gy = GROUND
    lift = [0, -1, 0, 1][k]
    for n in range(4):
        for d in (-1, 1):
            kx = 40 + d * (10 + n * 4)
            knee = (kx, gy - 24 + n * 2 + lift)
            leg = g.m_capsule((40 + d * 4, gy - 14 + lift), knee, 1.4, 1.1)[0]
            c.paste(leg, g.shade_rows(leg), body)
            foot = g.m_capsule(knee, (kx + d * 4, gy - 1), 1.1, 0.7)[0]
            c.paste(foot, g.shade_rows(foot), body)
    ab = g.m_ellipse(34, gy - 15 + lift, 11.0, 8.0)
    t = g.shade_rows(ab)
    c.paste(ab, t, body)
    st = ab & (((YY + XX // 3) % 5) == 0) & ~g.edges(ab)
    c.paste(st, np.zeros((FH, FW), int) + 1, stripe)
    hd = g.m_ellipse(46, gy - 15 + lift, 5.0, 4.4)
    c.paste(hd, g.shade_rows(hd), body)
    for ex, ey in ((48, -17), (50, -16), (48, -15), (46, -17)):
        c.px(ex, gy + ey + lift, eye)
    c.keep |= g.m_ellipse(48, gy - 16 + lift, 3.0, 2.0)
    for d in (-1, 1):                                                       # fangs
        c.px(51, gy - 13 + d + lift, (240, 230, 210))
    return finish(c, shadow=(36, 12))


def oni_spawn(k):
    """Oni Spawn (bestiary D V, "lesser oni"): a squat young oni, red-skinned and pot-bellied, two short horns, a wide
    tusked mouth, an iron club over its shoulder; not big yet, but it wants a name."""
    c = canvas()
    skin, horn, iron = g.ramp((190, 60, 50)), g.ramp((232, 222, 196)), g.ramp((90, 90, 96))
    loin = g.ramp((70, 60, 50))
    gy = GROUND
    b = [0, 1, 1, 0][k]
    for d in (-1, 1):                                                       # stubby legs
        lg = g.m_capsule((40 + d * 5, gy - 12 + b), (40 + d * 6, gy - 2), 3.4, 3.0)[0]
        c.paste(lg, g.shade_rows(lg), skin)
    belly = g.m_ellipse(40, gy - 19 + b, 10.0, 9.0)
    c.paste(belly, g.shade_rows(belly), skin)
    lo = belly & (YY > gy - 14 + b)
    c.paste(lo, g.shade_rows(lo), loin)
    head = g.m_ellipse(42, gy - 31 + b, 6.5, 6.0)
    c.paste(head, g.shade_rows(head), skin)
    for d in (-1, 1):                                                       # horns
        hn = g.m_capsule((42 + d * 3, gy - 36 + b), (42 + d * 5, gy - 42 + b), 1.4, 0.5)[0]
        c.paste(hn, g.shade_rows(hn), horn)
    c.px(44, gy - 32 + b, (255, 230, 90)), c.px(46, gy - 32 + b, (255, 230, 90))   # eyes
    for x in range(43, 48):
        c.px(x, gy - 28 + b, (40, 10, 10))                                  # the wide mouth
    c.px(43, gy - 29 + b, horn[4]), c.px(47, gy - 29 + b, horn[4])         # tusks
    g.draw_limb(c, (34, gy - 24 + b), (30, gy - 16 + b), 2.6, 2.2, skin)   # the far arm
    g.draw_limb(c, (48, gy - 24 + b), (51, gy - 30 + b), 2.6, 2.2, skin)   # the club arm, raised
    club = g.m_capsule((51, gy - 30 + b), (44, gy - 46 + b), 1.6, 3.0)[0]
    c.paste(club, g.shade_rows(club), iron)
    return finish(c, shadow=(30, 11))


def write(j, tmpl, epid, fname, label, idle, scale):
    sheet, (cols, rows), animap = ea.animate(idle)
    sheet.save(os.path.join(g.PIC, fname + ".png"))
    e = json.loads(json.dumps(tmpl))
    e.update({"name": {"en": label, "ja": label}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
              "aniuv": [cols, rows], "animap": animap, "memo": "monster (tools/gen_monsters.py)",
              "gndpos": [0.5, (FH - GROUND - 1) / FH], "scale": scale, "flipx": False})
    j[epid] = e
    return idle[0]


def main():
    jpath = os.path.join(g.RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    s = 1.05 * g.CAST_SCALE
    prev = []
    wm = warmonger()
    sheet, (cols, rows), animap = ea.animate(wm)
    sheet.save(os.path.join(g.PIC, "goblin_warmonger.png"))
    e = json.loads(json.dumps(j["EP106"]))
    e.update({"name": {"en": "Goblin Warmonger", "ja": "Goblin Warmonger"}, "pic3d": "/resource/enemy_pic/goblin_warmonger.png",
              "aniuv": [cols, rows], "animap": animap, "memo": "monster (tools/gen_monsters.py)"})
    j["EP110"] = e
    prev.append(wm[0])
    prev.append(write(j, tmpl, "EP111", "cave_bats", "Cave Bat Swarm", [bats(k) for k in range(4)], s))
    prev.append(write(j, tmpl, "EP112", "yurei", "Yurei", [yurei(k) for k in range(4)], s))
    prev.append(write(j, tmpl, "EP113", "troll", "Troll", [troll(k) for k in range(4)], s * 2.2))
    prev.append(write(j, tmpl, "EP116", "onikage", "Onikage", [onikage(k) for k in range(4)], s * 1.9))
    prev.append(write(j, tmpl, "EP117", "toothed_poppy", "Toothed Poppy", [poppy(k) for k in range(4)], s * 1.2))
    prev.append(write(j, tmpl, "EP119", "other_face", "The Other Face", [other_face(k) for k in range(4)], s * 1.1))
    prev.append(write(j, tmpl, "EP436", "wolfrider", "Bakemono Wolf-rider", [wolfrider(k) for k in range(4)], s * 1.8))
    # the Crab coast table (bestiary F "Kaiu Wall & Crab coast"; storyboard crab-ch1 R1 Hunting side path)
    prev.append(write(j, tmpl, "EP437", "carrion_crow", "Carrion Crow", [crow(k) for k in range(4)], s))
    prev.append(write(j, tmpl, "EP438", "will_o_wisp", "Will-o'-wisp", [wisp(k) for k in range(4)], s))
    prev.append(write(j, tmpl, "EP439", "wild_boar", "Wild Boar", [boar(k) for k in range(4)], s * 1.3))
    prev.append(write(j, tmpl, "EP440", "grey_wolf", "Grey Wolf", [grey_wolf(k) for k in range(4)], s * 1.3))
    prev.append(write(j, tmpl, "EP441", "sea_eel", "Sea Serpent Eel", [sea_eel(k) for k in range(4)], s * 1.4))
    prev.append(write(j, tmpl, "EP442", "umibozu", "Umibozu Shade", [umibozu(k) for k in range(4)], s * 1.8))
    prev.append(write(j, tmpl, "EP443", "paper_spirit", "Paper-spirit", [paper_spirit(k) for k in range(4)], s * 1.1))
    prev.append(write(j, tmpl, "EP444", "inkpot", "Ink-pot Spirit", [inkpot(k) for k in range(4)], s * 1.1))
    prev.append(write(j, tmpl, "EP445", "lantern", "Lantern Spirit", [lantern(k) for k in range(4)], s * 1.2))
    prev.append(write(j, tmpl, "EP446", "fear_shade", "Fear Shade", [fear_shade(k) for k in range(4)], s * 1.2))
    prev.append(write(j, tmpl, "EP447", "burning_bridge", "Burning Bridge", [burning_bridge(k) for k in range(4)],
                      s * 1.4))
    prev.append(write(j, tmpl, "EP448", "guardian_stone", "Guardian-stone", [guardian_stone(k) for k in range(4)],
                      s * 1.2))
    prev.append(write(j, tmpl, "EP449", "fever_spirit", "Fever Spirit", [fever_spirit(k) for k in range(4)], s * 2.0))
    prev.append(write(j, tmpl, "EP160", "gaki", "Gaki", [gaki(k) for k in range(4)], s * 1.2))
    prev.append(write(j, tmpl, "EP161", "tsuchigumo", "Tsuchigumo", [tsuchigumo(k) for k in range(4)], s * 1.3))
    prev.append(write(j, tmpl, "EP162", "mieko_shadow", "Mieko's Shadow", [mieko_shadow(k) for k in range(4)], s * 1.6))
    prev.append(write(j, tmpl, "EP459", "kappa", "Kappa", [kappa(k) for k in range(4)], s * 1.2))      # Dragon Ch2
    prev.append(write(j, tmpl, "EP163", "blood_leech", "Blood Leech", [blood_leech(k) for k in range(4)], s * 1.2))
    prev.append(write(j, tmpl, "EP164", "paddy_python", "Paddy Python", [paddy_python(k) for k in range(4)], s * 1.3))
    prev.append(write(j, tmpl, "EP165", "giant_hornet", "Giant Hornet", [giant_hornet(k) for k in range(4)], s * 1.0))
    # Scorpion Ch4 "The Eve" (bestiary F "Dragon mountains", "Tamori's Furnace")
    prev.append(write(j, tmpl, "EP166", "snow_bear", "Snow Bear", [snow_bear(k) for k in range(4)], s * 1.6))
    prev.append(write(j, tmpl, "EP167", "tengu", "Tengu Crow-Warrior", [tengu(k) for k in range(4)], s * 1.3))
    prev.append(write(j, tmpl, "EP168", "fire_elemental", "Fire Elemental", [fire_elemental(k) for k in range(4)],
                      s * 1.5))
    prev.append(write(j, tmpl, "EP169", "ash_ghoul", "Ash Ghoul", [ash_ghoul(k) for k in range(4)], s * 1.3))
    # Unicorn Ch1 "Fault Lines": Persimmon the pony, Daiyu's woodchuck, the boss arena's powder kegs
    prev.append(write(j, tmpl, "EP172", "pony", "Persimmon", [pony(k) for k in range(4)], s * 1.3))
    prev.append(write(j, tmpl, "EP173", "woodchuck", "Woodchuck", [woodchuck(k) for k in range(4)], s * 0.9))
    prev.append(write(j, tmpl, "EP174", "powder_keg", "Powder Keg", [powder_keg(k) for k in range(4)], s * 1.1))
    prev.append(write(j, tmpl, "EP181", "bloodstone_basin", "Bloodstone Basin", [bloodstone_basin(k) for k in range(4)],
                      s * 3.2))                                                       # Ronin Ch3 boss
    prev.append(write(j, tmpl, "EP107", "naga_scout", "Naga Scout", [naga_scout(k) for k in range(4)], s * 1.5))
    prev.append(write(j, tmpl, "EP108", "lava_dryad", "Lava Tree Dryad", [lava_dryad(k) for k in range(4)], s * 1.4))
    prev.append(write(j, tmpl, "EP109", "kumo_brood", "Kumo Brood", [kumo_brood(k) for k in range(4)], s * 1.6))
    prev.append(write(j, tmpl, "EP208", "oni_spawn", "Oni Spawn", [oni_spawn(k) for k in range(4)], s * 1.7))
    for epid, src, name, hsv in (("EP114", "EP110", "Goblin Experiment", [150, -10, 6]),     # tinted copies
                                 ("EP115", "EP408", "Drunken Samurai II", [-25, 15, -12]),
                                 ("EP118", "EP113", "Ogre", [200, -20, -10]),
                                 ("EP170", "EP440", "Wolf-Spirit", [110, -40, 40]),   # Scorpion Ch4: pale blue
                                 ("EP171", "EP437", "Pigeon Swarm", [0, -85, 70]),     # Unicorn Ch1: grey doves
                                 ("EP175", "EP164", "Shadow-Snake", [190, -80, -62])):  # Ronin Ch2: the den's shadows
        if src in j:
            x = json.loads(json.dumps(j[src]))
            x.update({"name": {"en": name, "ja": name}, "hsv": hsv})
            j[epid] = x
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    strip = Image.new("RGBA", (FW * len(prev), FH), (70, 98, 62, 255))
    x = 0
    for im in prev:
        strip.paste(im, (x, 0), im)
        x += FW
    out = os.path.join(g.PREVIEW, "monsters.png")
    strip.resize((strip.width * 4, strip.height * 4), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    main()
