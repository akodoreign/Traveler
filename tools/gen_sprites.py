"""Procedural Octopath-style (HD-2D billboard) pixel sprites for the eight travelers.

Each traveler = a pose-driven skeleton drawn at 1x on a 48x56 frame (facing right; the engine flips to face left),
then an outline pass (darkened neighbour colour, like Octopath sprites) and a rim-light pass.
Sheet: 8 columns x 3 rows = 24 frames:
   0-3 idle · 4-7 walk · 8 ready · 9-12 attack (windup, strike, follow, recover) · 13 cast · 14-15 hurt ·
   16 guard · 17 KO · 18-19 victory
Writes resource/enemy_pic/trav_<name>.png + enemy_pic.json entries EP200-EP207 (picture models usable by players),
and points chara models for P100-P107 at them (via gen_data.py: PLAYER_MODEL).
Preview: _art/preview/sprites_travelers.png
Run: python -E tools/gen_sprites.py
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
PIC = os.path.join(RES, "enemy_pic")
PREVIEW = os.path.join(HERE, "..", "_art", "preview")
FW, FH = 48, 56
COLS, ROWS = 8, 4
GROUND = 53


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (255,)


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)


# --------------------------------------------------------------------------------------------- travelers
SKIN = (238, 196, 160)
SKIN_TAN = (214, 166, 128)
TRAVELERS = [
    dict(key="natsuko", name="Hiruma Natsuko", skin=SKIN_TAN, hair=(44, 36, 34), hairstyle="ponytail",
         top=(74, 92, 120), lower=(54, 62, 80), accent=(150, 160, 176), armor=(96, 108, 124), build="armored",
         weapon="yari", female=True),
    dict(key="rensei", name="Kakita Rensei", skin=SKIN, hair=(236, 238, 244), hairstyle="topknot_long",
         top=(176, 206, 232), lower=(232, 236, 244), accent=(90, 130, 190), build="normal", weapon="katana",
         female=False),
    dict(key="gendo", name="Kitsuki Gendo", skin=SKIN, hair=(30, 30, 36), hairstyle="short",
         top=(62, 128, 82), lower=(44, 70, 54), accent=(210, 190, 90), build="normal", weapon="bo",
         glasses=True, female=False),
    dict(key="shizue", name="Akodo Shizue", skin=SKIN, hair=(84, 52, 30), hairstyle="bob",
         top=(214, 168, 54), lower=(128, 86, 40), accent=(150, 40, 36), armor=(184, 140, 50), build="armored_light",
         weapon="yari", female=True),
    dict(key="haruki", name="Isawa Haruki", skin=SKIN, hair=(36, 28, 26), hairstyle="short",
         top=(222, 104, 40), lower=(170, 60, 34), accent=(246, 206, 90), build="robe", weapon="bo", female=False),
    dict(key="mitsue", name="Shosuro Mitsue", skin=SKIN, hair=(24, 20, 24), hairstyle="long",
         top=(168, 30, 44), lower=(36, 30, 36), accent=(210, 170, 70), build="normal", weapon="tanto",
         mask=True, female=True),
    dict(key="tamotsu", name="Ide Tamotsu", skin=SKIN, hair=(86, 56, 36), hairstyle="short_beard",
         top=(120, 72, 156), lower=(232, 226, 236), accent=(220, 180, 70), build="round", weapon="yumi",
         female=False),
    dict(key="sayo", name="Sayo", skin=SKIN_TAN, hair=(62, 40, 28), hairstyle="long",
         top=(150, 118, 82), lower=(100, 80, 60), accent=(70, 110, 70), build="normal", weapon="katana",
         hat="jingasa", female=True),
]

WEAPON = {   # length forward of grip, length behind grip, width, two-handed
    "yari": dict(fwd=24, back=10, w=1, two=True),
    "bo": dict(fwd=17, back=15, w=2, two=True),
    "katana": dict(fwd=16, back=4, w=1, two=True),
    "tanto": dict(fwd=7, back=2, w=1, two=False),
    "tetsubo": dict(fwd=16, back=4, w=3, two=True),
    "yumi": dict(fwd=0, back=0, w=1, two=False),
}


# --------------------------------------------------------------------------------------------- poses
def base_pose():
    return dict(hip=(23, 34), neck=(24, 22), head=(25, 14), sh_b=(22, 24), sh_f=(26, 24),
                el_b=(20, 29), el_f=(28, 29), ha_b=(22, 33), ha_f=(30, 32),
                kn_b=(21, 43), kn_f=(26, 43), ft_b=(20, 52), ft_f=(27, 52),
                wang=-60, smear=None, glow=None, lean=0)


def add(p, d):
    return (p[0] + d[0], p[1] + d[1])


def shift_upper(P, dx, dy):
    for k in ("hip", "neck", "head", "sh_b", "sh_f", "el_b", "el_f", "ha_b", "ha_f"):
        P[k] = add(P[k], (dx, dy))


def pose(kind, i):
    P = base_pose()
    if kind == "idle":
        b = [0, 0, 1, 1][i]
        shift_upper(P, 0, b)
        P["kn_b"] = add(P["kn_b"], (0, b // 1 * 0))
    elif kind == "walk":
        sw = [4, 0, -4, 0][i]
        bob = [0, -1, 0, -1][i]
        shift_upper(P, 0, bob)
        P["ft_f"] = add(P["ft_f"], (sw, -1 if sw < 0 else 0))
        P["ft_b"] = add(P["ft_b"], (-sw, -1 if sw > 0 else 0))
        P["kn_f"] = add(P["kn_f"], (sw // 2, -1 if i in (0, 2) else 0))
        P["kn_b"] = add(P["kn_b"], (-sw // 2, -1 if i in (0, 2) else 0))
        P["ha_b"] = add(P["ha_b"], (-sw // 2, 0))
        P["el_b"] = add(P["el_b"], (-sw // 3, 0))
    elif kind == "ready":
        shift_upper(P, 1, 1)
        P["ft_f"] = add(P["ft_f"], (4, 0))
        P["kn_f"] = add(P["kn_f"], (3, 0))
        P["ft_b"] = add(P["ft_b"], (-2, 0))
        P["ha_f"] = add(P["ha_f"], (2, 0))
        P["wang"] = -20
    elif kind == "attack":
        if i == 0:      # windup
            shift_upper(P, -2, 1)
            P["ha_f"], P["el_f"] = (26, 26), (27, 27)
            P["ha_b"] = (24, 27)
            P["wang"] = -150
        elif i == 1:    # strike
            shift_upper(P, 4, 1)
            P["ft_f"] = add(P["ft_f"], (7, 0))
            P["kn_f"] = add(P["kn_f"], (5, -1))
            P["ft_b"] = add(P["ft_b"], (-3, 0))
            P["ha_f"], P["el_f"] = (37, 30), (33, 28)
            P["ha_b"] = (34, 30)
            P["wang"] = 0
            P["smear"] = "strike"
        elif i == 2:    # follow-through
            shift_upper(P, 3, 2)
            P["ft_f"] = add(P["ft_f"], (6, 0))
            P["kn_f"] = add(P["kn_f"], (4, 0))
            P["ft_b"] = add(P["ft_b"], (-3, 0))
            P["ha_f"], P["el_f"] = (34, 35), (31, 31)
            P["ha_b"] = (31, 35)
            P["wang"] = 35
        else:           # recover
            shift_upper(P, 1, 1)
            P["ft_f"] = add(P["ft_f"], (3, 0))
            P["wang"] = -30
    elif kind == "cast":
        shift_upper(P, 0, 0)
        P["ha_f"], P["el_f"] = (31, 15), (30, 21)
        P["wang"] = -80
        P["glow"] = (32, 12)
    elif kind == "hurt":
        k = 2 if i == 0 else 1
        shift_upper(P, -k, 0)
        P["head"] = add(P["head"], (-1, 0))
        P["ha_f"] = add(P["ha_f"], (-3, -2))
        P["ha_b"] = add(P["ha_b"], (-3, -1))
        P["ft_f"] = add(P["ft_f"], (-1, 0))
        P["wang"] = -100
    elif kind == "guard":
        shift_upper(P, 0, 2)
        P["kn_f"] = add(P["kn_f"], (2, 1))
        P["kn_b"] = add(P["kn_b"], (-1, 1))
        P["ha_f"], P["el_f"] = (29, 26), (28, 29)
        P["ha_b"] = (27, 30)
        P["wang"] = -95
    elif kind == "ko":
        shift_upper(P, 4, 11)
        P["head"] = add(P["head"], (3, 2))
        P["kn_f"], P["ft_f"] = (30, 50), (22, 52)
        P["kn_b"], P["ft_b"] = (26, 51), (18, 52)
        P["ha_f"], P["el_f"] = (34, 48), (32, 42)
        P["ha_b"] = (30, 48)
        P["wang"] = 85
    elif kind == "victory":
        shift_upper(P, 0, -1 if i == 0 else 0)
        P["ha_f"], P["el_f"] = (30, 12), (29, 18)
        P["ha_b"] = (21, 32)
        P["wang"] = -95 if i == 0 else -100
    return P


FRAMES = [("idle", 0), ("idle", 1), ("idle", 2), ("idle", 3),          # 0-3
          ("walk", 0), ("walk", 1), ("walk", 2), ("walk", 3),          # 4-7
          ("ready", 0), ("ready", 0),                                  # 8-9   (9 = hold)
          ("attack", 0), ("attack", 1), ("attack", 2), ("attack", 3),  # 10-13
          ("attack", 3),                                               # 14    hold
          ("cast", 0), ("cast", 0),                                    # 15-16
          ("hurt", 0), ("hurt", 1), ("hurt", 1),                       # 17-19 (19 = hold)
          ("guard", 0), ("guard", 0),                                  # 20-21
          ("ko", 0), ("ko", 0),                                        # 22-23
          ("victory", 0), ("victory", 1), ("victory", 0)]              # 24-26

# engine animation id -> (start, end, speed, loop)
ANIMAP = {   # (start, end-exclusive, speed, loop); each non-loop sequence is followed by a hold frame
    "stand": (0, 4, 4.0, True), "sick": (0, 4, 2.5, True), "walk": (4, 8, 9.0, True), "run": (4, 8, 13.0, True),
    "dash": (4, 8, 13.0, True), "jump": (8, 9, 1.0, False), "aim": (8, 9, 1.0, True), "aimw": (8, 9, 1.0, True),
    "aimp": (8, 9, 1.0, True), "aimb": (8, 9, 1.0, True),
    "slash1": (10, 14, 12.0, False), "punch1": (10, 14, 12.0, False), "stick1": (10, 14, 12.0, False),
    "bow1": (10, 14, 10.0, False), "atk": (10, 14, 12.0, False),
    "spell": (15, 16, 1.0, False), "magic1": (15, 16, 1.0, False), "blast1": (15, 16, 1.0, False),
    "damage": (17, 19, 8.0, False), "avoid": (17, 19, 8.0, False), "shield": (20, 21, 1.0, False),
    "guard": (20, 21, 1.0, True), "die": (22, 23, 1.0, True), "fight": (24, 26, 3.0, True),
    "victory": (24, 26, 3.0, True),
}


# --------------------------------------------------------------------------------------------- drawing
class Painter:
    def __init__(self):
        self.img = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def limb(self, a, b, w, col):
        self.d.line([a, b], fill=col, width=w)
        r = w / 2.0
        for p in (a, b):
            self.d.ellipse([p[0] - r + 0.5, p[1] - r + 0.5, p[0] + r - 0.5, p[1] + r - 0.5], fill=col)

    def poly(self, pts, col):
        self.d.polygon([tuple(map(round, p)) for p in pts], fill=col)

    def ell(self, box, col):
        self.d.ellipse(box, fill=col)

    def px(self, p, col):
        x, y = int(round(p[0])), int(round(p[1]))
        if 0 <= x < FW and 0 <= y < FH:
            self.img.putpixel((x, y), col)


def weapon_line(P, spec):
    ang = math.radians(P["wang"])
    dx, dy = math.cos(ang), math.sin(ang)
    g = P["ha_f"]
    tip = (g[0] + dx * spec["fwd"], g[1] + dy * spec["fwd"])
    butt = (g[0] - dx * spec["back"], g[1] - dy * spec["back"])
    return butt, tip, (dx, dy)


def draw_weapon(pt, T, P):
    wkind = T["weapon"]
    spec = WEAPON[wkind]
    if wkind == "yumi":
        g = P["ha_f"]
        wood, string = (120, 74, 40, 255), (230, 230, 220, 255)
        top, bot = (g[0] + 1, g[1] - 13), (g[0] + 1, g[1] + 11)
        pt.d.arc([g[0] - 3, top[1], g[0] + 5, bot[1]], -80, 80, fill=wood, width=2)
        pt.d.line([top, bot], fill=string, width=1)
        return
    butt, tip, (dx, dy) = weapon_line(P, spec)
    if wkind == "katana":
        hilt = (P["ha_f"][0] + dx * 3, P["ha_f"][1] + dy * 3)
        pt.limb(butt, hilt, 2, (40, 30, 36, 255))
        pt.d.line([hilt, tip], fill=(214, 222, 232, 255), width=2)
        pt.d.line([hilt, tip], fill=(250, 252, 255, 255), width=1)
        pt.px(hilt, (210, 170, 60, 255))
    elif wkind == "tanto":
        pt.d.line([butt, tip], fill=(220, 226, 236, 255), width=2)
        pt.px(P["ha_f"], (60, 40, 40, 255))
    elif wkind == "yari":
        shaft_end = (tip[0] - dx * 5, tip[1] - dy * 5)
        pt.d.line([butt, shaft_end], fill=(140, 96, 56, 255), width=2)
        nx, ny = -dy, dx
        pt.poly([tip, (shaft_end[0] + nx * 2, shaft_end[1] + ny * 2), (shaft_end[0] - nx * 2, shaft_end[1] - ny * 2)],
                (220, 228, 238, 255))
        pt.px(shaft_end, (200, 40, 40, 255))
    elif wkind == "bo":
        pt.d.line([butt, tip], fill=(132, 90, 52, 255), width=2)
        pt.px(tip, (200, 170, 90, 255))
        pt.px(butt, (200, 170, 90, 255))
    elif wkind == "tetsubo":
        pt.d.line([butt, tip], fill=(70, 66, 72, 255), width=4)
        for k in range(4, spec["fwd"], 3):
            pt.px((P["ha_f"][0] + dx * k, P["ha_f"][1] + dy * k - 2), (190, 190, 200, 255))


def draw_hair(pt, T, P, back=False):
    h, hs = T["hair"] + (255,), shade(T["hair"] + (255,), 0.7)
    cx, cy = P["head"]
    style = T["hairstyle"]
    if back:
        if style in ("long",):
            pt.poly([(cx - 6, cy - 2), (cx - 1, cy - 4), (cx - 1, cy + 14), (cx - 7, cy + 12)], hs)
        if style == "ponytail":
            pt.limb((cx - 5, cy - 3), (cx - 10, cy + 6), 3, hs)
        if style == "topknot_long":
            pt.poly([(cx - 6, cy - 1), (cx - 2, cy - 3), (cx - 2, cy + 9), (cx - 7, cy + 7)], hs)
        return
    # cap
    pt.d.chord([cx - 7, cy - 8, cx + 6, cy + 4], 180, 360, fill=h)
    pt.poly([(cx - 7, cy - 2), (cx - 4, cy - 2), (cx - 4, cy + 4), (cx - 7, cy + 3)], h)   # back of head
    # bangs toward the face
    pt.poly([(cx - 2, cy - 6), (cx + 6, cy - 4), (cx + 6, cy - 1), (cx + 3, cy - 2), (cx + 1, cy + 0), (cx - 1, cy - 3)], h)
    pt.px((cx + 1, cy - 6), shade(h, 1.25))
    pt.px((cx + 2, cy - 6), shade(h, 1.25))
    if style in ("topknot_long",):
        pt.ell([cx - 4, cy - 11, cx, cy - 7], h)
    if style == "short_beard":
        pt.poly([(cx + 1, cy + 3), (cx + 6, cy + 3), (cx + 5, cy + 7), (cx + 2, cy + 7)], hs)
        pt.limb((cx + 2, cy + 2), (cx + 6, cy + 2), 1, h)
    if style == "bob":
        pt.poly([(cx - 7, cy - 1), (cx - 3, cy - 1), (cx - 3, cy + 6), (cx - 7, cy + 5)], h)


def draw_face(pt, T, P):
    cx, cy = P["head"]
    skin, skin_s = T["skin"] + (255,), shade(T["skin"] + (255,), 0.82)
    pt.ell([cx - 6, cy - 6, cx + 6, cy + 6], skin)
    pt.ell([cx - 6, cy - 6, cx - 1, cy + 6], skin_s)                        # far side in shadow
    pt.px((cx + 6, cy + 1), skin)                                            # nose
    eye = (cx + 3, cy)
    if T.get("female"):
        pt.d.rectangle([eye[0], eye[1] - 1, eye[0] + 1, eye[1] + 1], fill=(40, 30, 50, 255))
        pt.px((eye[0] + 1, eye[1] - 1), (250, 250, 255, 255))
        pt.px((eye[0] - 1, eye[1] - 2), (40, 30, 50, 255))                   # lash
    else:
        pt.d.rectangle([eye[0], eye[1] - 1, eye[0] + 1, eye[1]], fill=(36, 28, 40, 255))
        pt.px((eye[0], eye[1] - 2), shade(T["hair"] + (255,), 0.8))           # brow
    pt.px((cx - 1, cy), (36, 28, 40, 255))                                   # far eye (small)
    pt.px((cx + 4, cy + 4), (170, 90, 80, 255))                              # mouth
    if T.get("glasses"):
        pt.d.rectangle([eye[0] - 1, eye[1] - 2, eye[0] + 2, eye[1] + 1], outline=(200, 220, 240, 255))
        pt.px((cx - 1, cy - 1), (200, 220, 240, 255))
    if T.get("mask"):
        pt.poly([(cx, cy + 2), (cx + 7, cy + 1), (cx + 6, cy + 6), (cx + 1, cy + 6)], (30, 24, 30, 255))


def draw_hat(pt, T, P):
    if T.get("hat") != "jingasa":
        return
    cx, cy = P["head"]
    straw, straw_s = (214, 184, 110, 255), (170, 138, 74, 255)
    pt.poly([(cx - 12, cy - 4), (cx, cy - 12), (cx + 12, cy - 4)], straw)
    pt.d.line([(cx - 12, cy - 4), (cx + 12, cy - 4)], fill=straw_s)
    for k in (-6, 0, 6):
        pt.d.line([(cx, cy - 11), (cx + k, cy - 5)], fill=straw_s)


def draw_body(pt, T, P):
    top, top_s = T["top"] + (255,), shade(T["top"] + (255,), 0.72)
    low, low_s = T["lower"] + (255,), shade(T["lower"] + (255,), 0.72)
    acc = T["accent"] + (255,)
    skin, skin_s = T["skin"] + (255,), shade(T["skin"] + (255,), 0.8)
    build = T["build"]
    hip, neck = P["hip"], P["neck"]
    lean = hip[0] - 23
    wide = 2 if build == "round" else 0
    # back arm + back leg (in shadow)
    pt.limb(P["sh_b"], P["el_b"], 3, top_s)
    pt.limb(P["el_b"], P["ha_b"], 3, top_s)
    pt.px(P["ha_b"], skin_s)
    if build == "robe":
        pass
    else:
        pt.limb(hip, P["kn_b"], 4, low_s)
        pt.limb(P["kn_b"], P["ft_b"], 3, low_s)
        pt.limb((P["ft_b"][0], P["ft_b"][1]), (P["ft_b"][0] + 2, P["ft_b"][1]), 2, (60, 44, 34, 255))
    # front leg
    if build != "robe":
        pt.limb(hip, P["kn_f"], 4, low)
        pt.limb(P["kn_f"], P["ft_f"], 3, low)
        pt.limb((P["ft_f"][0], P["ft_f"][1]), (P["ft_f"][0] + 2, P["ft_f"][1]), 2, (70, 52, 40, 255))
        # hakama flare over the thighs
        pt.poly([(hip[0] - 4, hip[1] - 1), (hip[0] + 4, hip[1] - 1),
                 (max(P["kn_f"][0], P["kn_b"][0]) + 3, P["kn_f"][1] + 1),
                 (min(P["kn_f"][0], P["kn_b"][0]) - 3, P["kn_b"][1] + 1)], low)
        pt.d.line([(hip[0], hip[1]), (hip[0] + (P["kn_f"][0] - hip[0]) // 2, P["kn_f"][1])], fill=low_s)
    else:
        bottom = GROUND - 1
        pt.poly([(hip[0] - 5, hip[1] - 2), (hip[0] + 5, hip[1] - 2), (hip[0] + 7, bottom), (hip[0] - 7, bottom)], low)
        pt.poly([(hip[0] - 5, hip[1] - 2), (hip[0] - 1, hip[1] - 2), (hip[0] - 3, bottom), (hip[0] - 7, bottom)], low_s)
        pt.px((P["ft_f"][0] + 3, bottom), (60, 44, 34, 255))
    # torso
    tw = 5 + wide
    torso = [(neck[0] - tw + 1, neck[1] + 1), (neck[0] + tw - 1, neck[1] + 1), (hip[0] + tw, hip[1]), (hip[0] - tw, hip[1])]
    pt.poly(torso, top)
    pt.poly([(neck[0] - tw + 1, neck[1] + 1), (neck[0] - 1, neck[1] + 1), (hip[0] - 1, hip[1]), (hip[0] - tw, hip[1])], top_s)
    # kimono collar (V) and obi
    pt.d.line([(neck[0] - 1, neck[1] + 1), (neck[0] + 2, neck[1] + 6)], fill=(240, 236, 228, 255))
    pt.d.line([(neck[0] + 2, neck[1] + 1), (neck[0] + 2, neck[1] + 6)], fill=skin)
    pt.d.rectangle([hip[0] - tw, hip[1] - 3, hip[0] + tw, hip[1] - 2], fill=acc)
    if build == "round":
        pt.ell([hip[0] - tw, hip[1] - 9, hip[0] + tw + 1, hip[1] - 1], top)
        pt.d.rectangle([hip[0] - tw, hip[1] - 3, hip[0] + tw + 1, hip[1] - 2], fill=acc)
    if build in ("armored", "armored_light"):
        arm = T["armor"] + (255,)
        pt.poly([(neck[0] - 3, neck[1] + 2), (neck[0] + 4, neck[1] + 2), (hip[0] + 4, hip[1] - 4), (hip[0] - 3, hip[1] - 4)], arm)
        for yy in range(neck[1] + 4, hip[1] - 4, 2):
            pt.d.line([(neck[0] - 2 + (yy - neck[1]) * lean // 12, yy), (neck[0] + 3, yy)], fill=shade(arm, 0.75))
        if build == "armored":   # sode (shoulder plates)
            s = P["sh_f"]
            pt.poly([(s[0] - 2, s[1] - 1), (s[0] + 3, s[1] - 1), (s[0] + 4, s[1] + 4), (s[0] - 2, s[1] + 4)], arm)
            pt.d.line([(s[0] - 2, s[1] + 2), (s[0] + 4, s[1] + 2)], fill=shade(arm, 0.7))
    # neck
    pt.limb((neck[0], neck[1] - 1), neck, 3, skin_s)


def draw_front_arm(pt, T, P):
    top = T["top"] + (255,)
    skin = T["skin"] + (255,)
    pt.limb(P["sh_f"], P["el_f"], 3, top)
    pt.limb(P["el_f"], P["ha_f"], 3, top)
    pt.ell([P["ha_f"][0] - 1, P["ha_f"][1] - 1, P["ha_f"][0] + 1, P["ha_f"][1] + 1], skin)
    if T["build"] == "armored":
        s = P["sh_f"]
        arm = T["armor"] + (255,)
        pt.poly([(s[0] - 2, s[1] - 1), (s[0] + 3, s[1] - 1), (s[0] + 4, s[1] + 4), (s[0] - 2, s[1] + 4)], arm)


def draw_fx(pt, P, T):
    if P["smear"] == "strike":
        g = P["ha_f"]
        for r, a in ((15, 120), (13, 200), (11, 255)):
            pt.d.arc([g[0] - r, g[1] - r, g[0] + r, g[1] + r], -70, 40, fill=(255, 255, 255, a), width=1)
    if P["glow"]:
        x, y = P["glow"]
        for rr, a in ((4, 90), (2, 200)):
            pt.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(170, 220, 255, a))
        pt.px((x, y), (255, 255, 255, 255))


def frame(T, kind, i):
    P = pose(kind, i)
    pt = Painter()
    two = WEAPON[T["weapon"]]["two"]
    if two and T["weapon"] != "yumi":
        # back hand on the shaft, behind the front hand
        butt, tip, (dx, dy) = weapon_line(P, WEAPON[T["weapon"]])
        if kind not in ("hurt", "ko", "victory", "cast"):
            P["ha_b"] = (P["ha_f"][0] - dx * 4, P["ha_f"][1] - dy * 4)
            P["el_b"] = ((P["sh_b"][0] + P["ha_b"][0]) / 2 - 1, (P["sh_b"][1] + P["ha_b"][1]) / 2 + 2)
    # shadow on the ground
    pt.d.ellipse([12, GROUND - 1, 36, GROUND + 2], fill=(0, 0, 0, 70))
    draw_hair(pt, T, P, back=True)
    behind = P["wang"] < -110
    if behind:
        draw_weapon(pt, T, P)
    draw_body(pt, T, P)
    draw_face(pt, T, P)
    draw_hair(pt, T, P)
    draw_hat(pt, T, P)
    if not behind:
        draw_weapon(pt, T, P)
    draw_front_arm(pt, T, P)
    img = finish(pt.img)
    fx = Painter()
    fx.img = img
    fx.d = ImageDraw.Draw(img)
    draw_fx(fx, P, T)
    return img


def finish(img):
    """Octopath-ish polish: dark coloured outline from neighbours + rim light on the upper-left edges."""
    a = np.array(img).astype(np.int32)
    alpha = a[..., 3] > 100
    ground_shadow = (a[..., 3] > 0) & (a[..., 3] <= 100)
    out = a.copy()
    H, W = alpha.shape
    for y in range(H):
        for x in range(W):
            if alpha[y, x]:
                # rim light: transparent above-left -> lighten
                if (y > 0 and not alpha[y - 1, x]) or (x > 0 and not alpha[y, x - 1]):
                    out[y, x, :3] = np.minimum(255, a[y, x, :3] * 1.12 + 8)
                continue
            nb = [(y + dy, x + dx) for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)) if 0 <= y + dy < H and 0 <= x + dx < W]
            inner = [a[p][:3] for p in nb if alpha[p]]
            if inner:
                c = np.mean(inner, axis=0) * 0.32
                out[y, x] = (int(c[0]), int(c[1]), int(c[2]), 255)
    out[ground_shadow & ~(out[..., 3] == 255)] = a[ground_shadow & ~(out[..., 3] == 255)]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def sheet(T):
    sh = Image.new("RGBA", (FW * COLS, FH * ROWS), (0, 0, 0, 0))
    for n, (kind, i) in enumerate(FRAMES):
        sh.paste(frame(T, kind, i), ((n % COLS) * FW, (n // COLS) * FH))
    return sh


def main():
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    os.makedirs(PREVIEW, exist_ok=True)
    rows = []
    for idx, T in enumerate(TRAVELERS):
        sh = sheet(T)
        fname = "trav_%s" % T["key"]
        sh.save(os.path.join(PIC, fname + ".png"))
        e = json.loads(json.dumps(tmpl))
        e.update({"name": {"en": T["name"], "ja": T["name"]}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
                  "aniuv": [COLS, ROWS], "memo": "procedural traveler sprite (tools/gen_sprites.py)",
                  "gndpos": [0.5, 1.0 - GROUND / FH], "atkpos": [0.2, 0.55], "cntpos": [0.5, 0.6], "scale": 1.3,
                  "flipx": True})
        e["animap"] = [{"id": k, "st": v[0], "en": v[1], "spd": v[2], "loop": v[3], "replay": True}
                       for k, v in ANIMAP.items()]
        j["EP%03d" % (200 + idx)] = e
        rows.append(sh)
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    # preview: first row of each sheet (idle .. ready) and attack, at 4x
    prev = Image.new("RGBA", (FW * 13 * 3, FH * 3 * len(rows)), (54, 62, 58, 255))
    for r, sh in enumerate(rows):
        strip = Image.new("RGBA", (FW * 13, FH), (0, 0, 0, 0))
        for n, fi in enumerate([0, 4, 5, 6, 7, 8, 10, 11, 12, 15, 17, 20, 24]):
            strip.paste(sh.crop(((fi % COLS) * FW, (fi // COLS) * FH, (fi % COLS + 1) * FW, (fi // COLS + 1) * FH)),
                        (n * FW, 0))
        big = strip.resize((strip.width * 3, strip.height * 3), Image.NEAREST)
        prev.paste(big, (0, r * FH * 3), big)
    prev.save(os.path.join(PREVIEW, "sprites_travelers.png"))
    print("wrote", ["EP%03d" % (200 + i) for i in range(len(rows))])


if __name__ == "__main__":
    main()
