"""HD-2D traveler sprites, v2: sculpted SDF figures raymarched onto the pixel grid (3/4 view), cel-shaded with
hue-shifted 4-tone ramps, outlined, with pixel-placed faces. Replaces gen_sprites.py output (same layout/ids).

Frame 64x80, facing right (the sheet entry sets flipx so the party faces the enemies). 8x4 grid, 27 frames:
   0-3 idle · 4-7 walk · 8-9 ready(+hold) · 10-13 attack · 14 hold · 15-16 cast · 17-19 hurt(+hold) ·
   20-21 guard · 22-23 KO · 24-26 victory
Writes resource/enemy_pic/trav_<key>.png, enemy_pic.json EP200-EP207, preview _art/preview/sprites3d.png
Run: python -E tools/gen_sprites3d.py [key ...]
"""
import colorsys
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
PIC = os.path.join(RES, "enemy_pic")
PREVIEW = os.path.join(HERE, "..", "_art", "preview")
FW, FH = 64, 80
COLS, ROWS = 8, 4
GROUND_PY = FH - 4          # pixel row of y=0
HEAD_S = 1.2               # head geometry scale (chibi Octopath head ~1/3 of height)
BODY_SQ = 0.8              # body height squash
YAW = math.radians(-62)     # character turned toward the camera (char +x/front -> world +z)
LIGHT = np.array([0.30, 0.78, 0.66])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# ------------------------------------------------------------------------------------------- materials / ramps


def ramp(rgb, sat=1.0):
    """4 tones + highlight with hue-shifted shadows (cool) and lights (warm)."""
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    tones = []
    for dv, dh, ds in ((-0.42, +0.045, +0.10), (-0.22, +0.02, +0.05), (0.0, 0.0, 0.0), (+0.13, -0.02, -0.08),
                       (+0.24, -0.03, -0.16)):
        hh = h
        if s > 0.08:
            # shadows drift toward purple (the short way round the hue wheel); lights toward warm yellow
            target, amt = (0.78, -dv * 0.35) if dv < 0 else (0.13, dv * 0.25)
            diff = ((target - h + 0.5) % 1.0) - 0.5
            hh = (h + diff * amt) % 1.0
        rr, gg, bb = colorsys.hsv_to_rgb(hh, max(0, min(1, s * sat + ds)), max(0, min(1, v + dv * (0.9 if v > 0.5 else 0.7))))
        tones.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return tones


def mats(T):
    m = {
        "skin": T["skin"], "hair": T["hair"], "top": T["top"], "lower": T["lower"], "accent": T["accent"],
        "collar": (236, 232, 222), "armor": T.get("armor", (120, 120, 130)), "wood": (138, 92, 54),
        "metal": (196, 206, 220), "sandal": (78, 56, 42), "hat": (212, 182, 108), "mask": (34, 28, 34),
        "string": (232, 228, 214), "trim": T.get("trim", T["accent"]),
    }
    return {k: ramp(v) for k, v in m.items()}


# ------------------------------------------------------------------------------------------- SDF primitives
def sd_sphere(p, c, r):
    return np.linalg.norm(p - c, axis=-1) - r


def sd_ellipsoid(p, c, rad):
    q = (p - c) / rad
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm(q / rad, axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def sd_roundcone(p, a, b, r1, r2):
    """Capsule with radius r1 at a and r2 at b (approximation, good for limbs)."""
    pa, ba = p - a, b - a
    h = np.clip(np.sum(pa * ba, axis=-1) / max(np.dot(ba, ba), 1e-6), 0, 1)
    r = r1 + (r2 - r1) * h
    return np.linalg.norm(pa - ba * h[..., None], axis=-1) - r


def sd_box(p, c, half, rnd=0.6):
    q = np.abs(p - c) - half
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.max(q, axis=-1), 0) - rnd


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


V = lambda *a: np.array(a, dtype=np.float64)  # noqa: E731

# ------------------------------------------------------------------------------------------- travelers
SKIN = (240, 200, 166)
SKIN_TAN = (220, 172, 134)
TRAVELERS = [
    dict(key="natsuko", name="Hiruma Natsuko", skin=SKIN_TAN, hair=(48, 40, 40), hairstyle="ponytail",
         top=(70, 88, 118), lower=(50, 58, 76), accent=(148, 160, 178), armor=(92, 104, 124), build="armored",
         weapon="yari", female=True),
    dict(key="rensei", eye=(84, 128, 196), name="Kakita Rensei", skin=SKIN, hair=(232, 236, 244), hairstyle="topknot",
         top=(170, 204, 234), lower=(206, 212, 228), accent=(80, 122, 186), build="normal", weapon="katana",
         female=False),
    dict(key="gendo", eye=(62, 120, 84), name="Kitsuki Gendo", skin=SKIN, hair=(34, 34, 40), hairstyle="short",
         top=(58, 126, 80), lower=(40, 66, 50), accent=(214, 190, 92), build="normal", weapon="bo",
         glasses=True, female=False),
    dict(key="shizue", name="Akodo Shizue", skin=SKIN, hair=(92, 56, 32), hairstyle="bob",
         top=(222, 172, 56), lower=(132, 88, 42), accent=(160, 44, 38), armor=(190, 146, 56), build="armored_light",
         weapon="yari", female=True),
    dict(key="haruki", eye=(176, 92, 40), name="Isawa Haruki", skin=SKIN, hair=(40, 30, 28), hairstyle="short",
         top=(226, 108, 42), lower=(176, 62, 36), accent=(248, 210, 96), build="robe", weapon="bo", female=False),
    dict(key="mitsue", eye=(150, 40, 52), name="Shosuro Mitsue", skin=SKIN, hair=(28, 22, 30), hairstyle="long",
         top=(172, 32, 48), lower=(40, 32, 40), accent=(214, 172, 72), build="normal", weapon="tanto",
         mask=True, female=True),
    dict(key="tamotsu", name="Ide Tamotsu", skin=SKIN, hair=(90, 58, 36), hairstyle="beard",
         top=(122, 74, 160), lower=(206, 200, 216), accent=(224, 184, 72), build="round", weapon="yumi",
         female=False),
    dict(key="sayo", name="Sayo", skin=SKIN_TAN, hair=(66, 42, 30), hairstyle="long",
         top=(152, 122, 86), lower=(102, 82, 62), accent=(74, 116, 74), build="normal", weapon="katana",
         hat="jingasa", female=True),
]


# ------------------------------------------------------------------------------------------- poses (char space)
def base_pose():
    return dict(hip=V(0, 21, 0), chest=V(0.5, 35, 0), neck=V(1, 43, 0), head=V(1.5, 51.0, 0),
                sh_n=V(0.3, 40, 6.2), sh_f=V(0.3, 40, -6.2),
                el_n=V(2.0, 32, 8.4), ha_n=V(4.5, 27, 9.6), el_f=V(-1, 32.5, -7.0), ha_f=V(3, 27.5, -3.5),
                kn_n=V(1.5, 11, 4.0), ft_n=V(2.5, 1.6, 4.8), kn_f=V(-1.2, 11, -4.0), ft_f=V(-1.8, 1.6, -4.8),
                wang=-78.0, smear=False, glow=None, headtilt=0.0)


def up(P, d):
    for k in ("hip", "chest", "neck", "head", "sh_n", "sh_f", "el_n", "el_f", "ha_n", "ha_f"):
        P[k] = P[k] + d


def pose(kind, i):
    P = base_pose()
    if kind == "idle":
        up(P, V(0, [0, -0.4, -0.8, -0.4][i], 0))
        P["ha_f"] = P["ha_f"] + V(0, [0, -0.3, -0.6, -0.3][i], 0)
    elif kind == "walk":
        s = [5, 0, -5, 0][i]
        up(P, V(0.5, [0, 1, 0, 1][i], 0))
        P["ft_n"] = P["ft_n"] + V(s, 1.2 if s < 0 else 0, 0)
        P["ft_f"] = P["ft_f"] + V(-s, 1.2 if s > 0 else 0, 0)
        P["kn_n"] = P["kn_n"] + V(s * 0.55, 1.0 if i % 2 == 0 else 0.4, 0)
        P["kn_f"] = P["kn_f"] + V(-s * 0.55, 1.0 if i % 2 == 0 else 0.4, 0)
        P["el_f"] = P["el_f"] + V(-s * 0.3, 0, 0)
    elif kind == "ready":
        up(P, V(1.5, -1.5, 0))
        P["ft_n"] = P["ft_n"] + V(5, 0, 0)
        P["kn_n"] = P["kn_n"] + V(4, -1, 0)
        P["ft_f"] = P["ft_f"] + V(-3, 0, 0)
        P["ha_n"] = P["ha_n"] + V(2.5, 1, 0)
        P["wang"] = -22.0
    elif kind == "attack":
        if i == 0:
            up(P, V(-2.5, -1, 0))
            P["ha_n"], P["el_n"] = V(-1, 43, 3.5), V(1, 38, 5.5)
            P["ha_f"], P["el_f"] = V(0, 41, -2), V(-1.5, 36, -5)
            P["wang"] = -125.0
        elif i == 1:
            up(P, V(6, -2.5, 0))
            P["ft_n"] = P["ft_n"] + V(10, 0, 0)
            P["kn_n"] = P["kn_n"] + V(8, -2.5, 0)
            P["ft_f"] = P["ft_f"] + V(-4, 0, 0)
            P["ha_n"], P["el_n"] = V(19, 32, 4), V(13, 33, 5)
            P["ha_f"], P["el_f"] = V(15, 32, -2), V(9, 33, -4.5)
            P["wang"] = -2.0
            P["smear"] = True
        elif i == 2:
            up(P, V(5, -3, 0))
            P["ft_n"] = P["ft_n"] + V(9, 0, 0)
            P["kn_n"] = P["kn_n"] + V(7, -2, 0)
            P["ft_f"] = P["ft_f"] + V(-4, 0, 0)
            P["ha_n"], P["el_n"] = V(15, 23, 4), V(11, 28, 5)
            P["ha_f"], P["el_f"] = V(11, 24, -2), V(7, 29, -4.5)
            P["wang"] = 38.0
        else:
            up(P, V(1.5, -1, 0))
            P["ft_n"] = P["ft_n"] + V(4, 0, 0)
            P["wang"] = -30.0
    elif kind == "cast":
        P["ha_n"], P["el_n"] = V(8, 50, 4), V(6, 43, 5.5)
        P["glow"] = V(9, 56, 4)
        P["wang"] = -80.0
    elif kind == "hurt":
        k = 3.0 if i == 0 else 1.5
        up(P, V(-k, 0, 0))
        P["head"] = P["head"] + V(-1.5, -0.5, 0)
        P["ha_n"] = P["ha_n"] + V(-5, 2, 0)
        P["ha_f"] = P["ha_f"] + V(-5, 2, 0)
        P["wang"] = -110.0
    elif kind == "guard":
        up(P, V(0, -2.5, 0))
        P["kn_n"] = P["kn_n"] + V(2.5, -1, 0)
        P["kn_f"] = P["kn_f"] + V(-1.5, -1, 0)
        P["ha_n"], P["el_n"] = V(6, 36, 4.5), V(4, 31, 5.5)
        P["ha_f"], P["el_f"] = V(4, 33, -2.5), V(1, 30, -5)
        P["wang"] = -98.0
    elif kind == "ko":
        up(P, V(6, -13, 0))
        P["head"] = P["head"] + V(4, -2, 0)
        P["kn_n"], P["ft_n"] = V(7, 2.5, 2.6), V(-3, 1.6, 2.6)
        P["kn_f"], P["ft_f"] = V(5, 2.5, -2.6), V(-5, 1.6, -2.6)
        P["ha_n"], P["el_n"] = V(14, 3, 4), V(11, 10, 5)
        P["ha_f"], P["el_f"] = V(11, 3, -3), V(8, 10, -5)
        P["wang"] = 4.0
    elif kind == "victory":
        up(P, V(0, -0.5 if i == 1 else 0, 0))
        P["ha_n"], P["el_n"] = V(5, 56, 4), V(4, 48, 5.5)
        P["wang"] = -96.0
    # Octopath proportions: squash everything below the head, then sit the (scaled-up) head on the neck
    hoff = P["head"] - P["neck"]
    for k in ("hip", "chest", "neck", "sh_n", "sh_f", "el_n", "el_f", "ha_n", "ha_f", "kn_n", "ft_n", "kn_f", "ft_f"):
        P[k] = V(P[k][0], P[k][1] * BODY_SQ, P[k][2])
    if P["glow"] is not None:
        P["glow"] = V(P["glow"][0], P["glow"][1] * BODY_SQ, P["glow"][2])
    P["head"] = P["neck"] + hoff * HEAD_S + V(0, 0.8, 0)
    return P


FRAMES = [("idle", 0), ("idle", 1), ("idle", 2), ("idle", 3),
          ("walk", 0), ("walk", 1), ("walk", 2), ("walk", 3),
          ("ready", 0), ("ready", 0),
          ("attack", 0), ("attack", 1), ("attack", 2), ("attack", 3), ("attack", 3),
          ("cast", 0), ("cast", 0),
          ("hurt", 0), ("hurt", 1), ("hurt", 1),
          ("guard", 0), ("guard", 0),
          ("ko", 0), ("ko", 0),
          ("victory", 0), ("victory", 1), ("victory", 0)]

ANIMAP = {
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

WEAPON = {"yari": (30, 9, True), "bo": (20, 17, True), "katana": (18, 4, True), "tanto": (8, 2, False),
          "yumi": (0, 0, False)}


# ------------------------------------------------------------------------------------------- the figure
def build_parts(T, P):
    """Returns list of (material, sdf_fn, smooth_k) in character space."""
    parts = []
    add = lambda m, f, k=0.0: parts.append((m, f, k))  # noqa: E731
    head, neck, chest, hip = P["head"], P["neck"], P["chest"], P["hip"]
    build = T["build"]
    wide = 2.4 if build == "round" else 0.0
    # --- head & neck
    add("skin", lambda p: sd_ellipsoid(p, head, V(8.6, 8.8, 8.2)))
    add("skin", lambda p: sd_sphere(p, head + V(4.2, -3.6, 0), 3.4), 2.0)          # jaw/cheek mass
    add("skin", lambda p: sd_roundcone(p, neck + V(0, -1, 0), head + V(-0.5, -5, 0), 2.3, 2.6), 1.2)
    # --- hair
    hs = T["hairstyle"]
    hc = head + V(-1.0, 1.0, 0)

    def hair_cap(p):
        d = sd_ellipsoid(p, hc, V(9.5, 9.6, 9.1))
        # cut away the face: keep top and back
        q = p - head
        cut = -(q[..., 1] * 0.95 - q[..., 0] * 1.05 + 1.6)
        return np.maximum(d, cut)
    add("hair", hair_cap)
    for bx, by, bz, r in ((5.6, 5.0, 2.5, 2.4), (6.0, 4.0, -1.0, 2.3), (4.4, 6.4, 4.6, 2.2), (6.4, 3.0, 0.8, 1.7)):
        c = head + V(bx, by, bz)
        add("hair", lambda p, c=c, r=r: sd_sphere(p, c, r), 1.0)                     # bangs
    for side in (1, -1):                                                              # sidelocks
        add("hair", lambda p, side=side: sd_roundcone(p, head + V(3.0, 4.0, 7.6 * side), head + V(4.2, -5.0, 7.4 * side), 2.0, 1.2), 1.0)
    if hs == "ponytail":
        add("hair", lambda p: sd_roundcone(p, head + V(-6, 4, 0), head + V(-12, -9, 0), 3.0, 1.6), 1.5)
        add("accent", lambda p: sd_sphere(p, head + V(-6.8, 3.5, 0), 1.8))
    elif hs == "topknot":
        add("hair", lambda p: sd_ellipsoid(p, head + V(-2, 9.5, 0), V(3.4, 2.6, 2.6)), 1.5)
        add("hair", lambda p: sd_roundcone(p, head + V(-6, 3, 0), head + V(-8, -10, 0), 3.2, 2.0), 1.5)
    elif hs == "long":
        add("hair", lambda p: sd_roundcone(p, head + V(-4, 2, 0), head + V(-6.5, -17, 0), 7.0, 4.0), 2.0)
    elif hs == "bob":
        add("hair", lambda p: sd_roundcone(p, head + V(-2.5, 1, 0), head + V(-2.0, -6, 0), 8.2, 7.0), 1.5)
    elif hs == "beard":
        add("hair", lambda p: sd_ellipsoid(p, head + V(4.6, -5.0, 0), V(3.6, 3.4, 4.6)), 1.0)
    if T.get("hat") == "jingasa":
        add("hat", lambda p: np.maximum(sd_roundcone(p, head + V(-0.5, 6.5, 0), head + V(-0.5, 11.5, 0), 13.5, 0.8),
                                         head[1] + 5.5 - p[..., 1]))
    # scale every head part (incl. hair/hat) about the head centre
    for n in range(len(parts)):
        m, f, k = parts[n]
        parts[n] = (m, (lambda p, f=f: HEAD_S * f(head + (p - head) / HEAD_S)), k * HEAD_S)
    # --- torso (kimono) + obi
    add("top", lambda p: sd_ellipsoid(p, (chest + hip) * 0.5 + V(0, 3.5, 0), V(6.4 + wide, 10.5, 8.0 + wide)), 2.0)
    if build == "round":
        add("top", lambda p: sd_sphere(p, hip + V(2.5, 8, 0), 7.6), 2.5)
    add("collar", lambda p: sd_roundcone(p, neck + V(1.2, -1.2, 3.2), chest + V(5.4 + wide, -3, 0.8), 1.0, 0.9))
    add("collar", lambda p: sd_roundcone(p, neck + V(1.2, -1.2, -3.2), chest + V(5.4 + wide, -3, -0.8), 1.0, 0.9))
    add("accent", lambda p: sd_ellipsoid(p, hip + V(0, 4.3, 0), V(6.9 + wide * 1.4, 1.6, 8.5 + wide * 1.4)))
    add("wood", lambda p: sd_box(p, hip + V(2.5, 1.4, 7.2 + wide), V(1.4, 1.8, 0.7), 0.5))       # inro
    add("string", lambda p: sd_roundcone(p, hip + V(2.5, 3.4, 7.0 + wide), hip + V(2.5, 4.6, 6.6 + wide), 0.35, 0.35))
    # --- armour
    if build in ("armored", "armored_light"):
        add("armor", lambda p: sd_box(p, chest + V(1.5 + wide, -1.5, 0), V(4.6, 4.8, 5.6), 1.2))
        for yy in (-3.5, -0.5, 2.5):
            add("trim", lambda p, yy=yy: sd_box(p, chest + V(6.2, yy - 1.5, 0), V(0.25, 0.35, 5.0), 0.25))
        if build == "armored":
            for side in (1, -1):
                s = P["sh_n"] if side > 0 else P["sh_f"]
                add("armor", lambda p, s=s, side=side: sd_box(p, s + V(-0.5, -2.5, 1.4 * side), V(3.6, 3.2, 1.0), 0.9))
        add("armor", lambda p: sd_box(p, hip + V(1.5, 1.0, 0), V(5.0, 2.4, 6.4), 0.8))     # tassets
    # --- legs (hakama) or robe
    if build == "robe":
        add("lower", lambda p: sd_roundcone(p, hip + V(0, 4, 0), V(1, 2.5, 0), 6.4, 9.5), 2.0)
        add("trim", lambda p: sd_roundcone(p, V(1, 4.2, 0), V(1, 2.2, 0), 9.4, 9.8))
    else:
        for kn, ft in (("kn_n", "ft_n"), ("kn_f", "ft_f")):
            a, b, c = hip + V(0, 1, 0), P[kn], P[ft]
            add("lower", lambda p, a=a, b=b: sd_roundcone(p, a, b, 5.0, 4.8), 0.0)
            add("lower", lambda p, b=b, c=c: sd_roundcone(p, b, c + V(0, 2.4, 0), 4.8, 6.0), 1.2)
            add("sandal", lambda p, c=c: sd_ellipsoid(p, c + V(1.5, -0.4, 0), V(3.6, 1.6, 2.2)))
    # --- arms (wide kimono sleeves)
    for sh, el, ha, near in (("sh_n", "el_n", "ha_n", True), ("sh_f", "el_f", "ha_f", False)):
        a, b, c = P[sh], P[el], P[ha]
        mat_sleeve = "top"
        add(mat_sleeve, lambda p, a=a, b=b: sd_roundcone(p, a, b, 3.4, 4.4), 1.6)
        add(mat_sleeve, lambda p, b=b, c=c: sd_roundcone(p, b, b + (c - b) * 0.55, 4.4, 3.4), 1.0)
        add("skin", lambda p, b=b, c=c: sd_roundcone(p, b + (c - b) * 0.5, c, 1.7, 1.6), 0.8)
        add("skin", lambda p, c=c: sd_sphere(p, c, 2.0), 0.8)
    # --- weapon
    wk = T["weapon"]
    fwd, back, two = WEAPON[wk]
    ang = math.radians(P["wang"])
    d = V(math.cos(ang), -math.sin(ang), 0)            # wang: degrees below horizontal (screen-space convention)
    d = V(math.cos(ang), math.sin(-ang), 0)
    g = P["ha_n"]
    if wk == "yumi":
        top, bot = g + V(1.5, 15, 0.8), g + V(1.5, -13, 0.8)
        pts = [g + V(1.5 + 4.5 * math.cos(t), 14 * math.sin(t), 0.8) for t in np.linspace(-1.35, 1.35, 9)]
        for a, b in zip(pts[:-1], pts[1:]):
            add("wood", lambda p, a=a, b=b: sd_roundcone(p, a, b, 0.9, 0.9))
        add("string", lambda p: sd_roundcone(p, top, bot, 0.35, 0.35))
    else:
        tip, butt = g + d * fwd, g - d * back
        if wk == "katana":
            hilt = g + d * 3.5
            add("mask", lambda p: sd_roundcone(p, butt, hilt, 1.0, 1.0))
            add("accent", lambda p: sd_roundcone(p, hilt, hilt + d * 0.7, 1.8, 1.8))
            add("metal", lambda p: sd_roundcone(p, hilt, tip, 0.9, 0.45))
        elif wk == "tanto":
            add("mask", lambda p: sd_roundcone(p, butt, g + d * 1.5, 0.9, 0.9))
            add("metal", lambda p: sd_roundcone(p, g + d * 1.5, tip, 0.9, 0.35))
        elif wk == "yari":
            neck_ = tip - d * 6
            add("wood", lambda p: sd_roundcone(p, butt, neck_, 0.85, 0.85))
            add("accent", lambda p: sd_sphere(p, neck_, 1.3))
            add("metal", lambda p: sd_roundcone(p, neck_, tip, 1.5, 0.2))
        elif wk == "bo":
            add("wood", lambda p: sd_roundcone(p, butt, tip, 1.0, 1.0))
            add("accent", lambda p: sd_sphere(p, tip, 1.2))
            add("accent", lambda p: sd_sphere(p, butt, 1.2))
    return parts


def to_char(pw):
    """world (screen-aligned) -> character space (undo yaw)."""
    c, s = math.cos(YAW), math.sin(YAW)
    x, y, z = pw[..., 0], pw[..., 1], pw[..., 2]
    return np.stack([x * c - z * s, y, x * s + z * c], axis=-1)


def to_world(pc):
    c, s = math.cos(-YAW), math.sin(-YAW)
    x, y, z = pc[0], pc[1], pc[2]
    return V(x * c - z * s, y, x * s + z * c)


def scene(parts, pw):
    pc = to_char(pw)
    names = sorted({m for m, _, _ in parts})
    best_d = np.full(pc.shape[:-1], 1e9)
    best_m = np.zeros(pc.shape[:-1], dtype=np.int32)
    for mi, name in enumerate(names):
        dm = None
        for m, f, k in parts:
            if m != name:
                continue
            dd = f(pc)
            dm = dd if dm is None else (smin(dm, dd, k) if k > 0 else np.minimum(dm, dd))
        sel = dm < best_d
        best_d = np.where(sel, dm, best_d)
        best_m = np.where(sel, mi, best_m)
    return best_d, best_m, names


def render(T, P):
    parts = build_parts(T, P)
    ys, xs = np.mgrid[0:FH, 0:FW]
    wx = xs - FW / 2 + 0.5
    wy = (GROUND_PY - ys) + 0.0
    N = FH * FW
    ro = np.stack([wx.ravel(), wy.ravel(), np.full(N, 40.0)], axis=-1)
    t = np.zeros(N)
    hit = np.zeros(N, dtype=bool)
    alive = np.ones(N, dtype=bool)
    for _ in range(70):
        idx = np.where(alive)[0]
        if len(idx) == 0:
            break
        p = ro[idx].copy()
        p[:, 2] -= t[idx]
        d, _, _ = scene(parts, p)
        h = d < 0.15
        hit[idx[h]] = True
        alive[idx[h]] = False
        t[idx] += np.maximum(d, 0.05) * 0.9
        alive[idx[t[idx] > 80]] = False
    img = np.zeros((N, 4), dtype=np.uint8)
    depth = np.full(N, 1e9)
    matid = np.full(N, -1)
    hi = np.where(hit)[0]
    if len(hi):
        p = ro[hi].copy()
        p[:, 2] -= t[hi]
        d, m, names = scene(parts, p)
        e = 0.35
        nx = scene(parts, p + V(e, 0, 0))[0] - scene(parts, p - V(e, 0, 0))[0]
        ny = scene(parts, p + V(0, e, 0))[0] - scene(parts, p - V(0, e, 0))[0]
        nz = scene(parts, p + V(0, 0, e))[0] - scene(parts, p - V(0, 0, e))[0]
        n = np.stack([nx, ny, nz], axis=-1)
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        lam = np.clip(n @ LIGHT, 0, 1)
        rim = np.clip(n[:, 2] * 0.0 + (1 - np.abs(n[:, 2])) * (n[:, 0] < -0.3), 0, 1) * 0.12
        val = 0.10 + 0.90 * lam + rim
        R = mats(T)
        band = np.digitize(val, [0.30, 0.52, 0.78, 0.95])          # 0..4
        pc = to_char(p)
        rel = pc - P["head"]
        az = np.arctan2(rel[:, 2], rel[:, 0])
        if "hair" in names:                                         # strand clumps + shine ring
            hm = m == names.index("hair")
            sw = np.sin(az * 9 + rel[:, 1] * 0.22)
            band = np.where(hm & (sw > 0.55), np.maximum(band - 1, 0), band)
            ring = hm & (np.abs(rel[:, 1] - 5.5) < 1.1) & (band >= 2) & (sw < 0.3)
            band = np.where(ring, 4, band)
        if "lower" in names:                                        # hakama pleats
            lm = m == names.index("lower")
            rh = pc - P["hip"]
            pl = np.sin(np.arctan2(rh[:, 2], rh[:, 0] + 0.01) * 8 + rh[:, 0] * 0.4)
            band = np.where(lm & (pl > 0.75), np.maximum(band - 1, 0), band)
        if "top" in names:                                          # sleeve/robe folds
            tm = m == names.index("top")
            fl = np.sin(pc[:, 1] * 0.9 + pc[:, 0] * 0.5)
            band = np.where(tm & (fl > 0.86) & (band >= 2), band - 1, band)
        for k, name in enumerate(names):
            sel = m == k
            rp = np.array(R[name])
            img[hi[sel], :3] = rp[band[sel]]
        img[hi, 3] = 255
        depth[hi] = t[hi]
        matid[hi] = m
    img = img.reshape(FH, FW, 4)
    depth = depth.reshape(FH, FW)
    return img, depth, parts


def finish(img, depth):
    out = img.copy()
    a = img[..., 3] > 0
    H, W = a.shape
    for y in range(H):
        for x in range(W):
            if a[y, x]:
                # inner line: a neighbour noticeably nearer the camera -> darken this pixel
                for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and a[yy, xx] and depth[yy, xx] < depth[y, x] - 2.4:
                        out[y, x, :3] = (img[y, x, :3] * 0.55).astype(np.uint8)
                        break
                continue
            nb = [(y + dy, x + dx) for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))
                  if 0 <= y + dy < H and 0 <= x + dx < W and a[y + dy, x + dx]]
            if nb:
                c = np.mean([img[p][:3] for p in nb], axis=0) * 0.28
                out[y, x] = (int(c[0]), int(c[1]), int(c[2] + 6), 255)
    return out


def screen(pc):
    w = to_world(pc)
    return int(round(w[0] + FW / 2 - 0.5)), int(round(GROUND_PY - w[1]))


def face(img, T, P):
    """Pixel-placed Octopath face: big eyes (lash line, iris, highlight), brows, mouth, glasses/mask."""
    head = P["head"]
    hp = lambda x, y, z: screen(head + V(x, y, z) * HEAD_S)  # noqa: E731
    ex, ey = hp(7.0, 0.4, 3.0)          # near eye (top-left of the 3x4 block)
    fx, fy = hp(7.2, 0.4, -2.6)         # far eye
    lash = np.array([30, 22, 34, 255], dtype=np.uint8)
    white = np.array([255, 255, 255, 255], dtype=np.uint8)
    er = ramp(T.get("eye", (96, 62, 44)))
    iris, iris2 = np.array(list(er[1]) + [255], dtype=np.uint8), np.array(list(er[3]) + [255], dtype=np.uint8)
    brow = np.array(list(ramp(T["hair"])[0]) + [255], dtype=np.uint8)
    skin_d = np.array(list(ramp(T["skin"])[1]) + [255], dtype=np.uint8)

    def put(x, y, c):
        if 0 <= x < FW and 0 <= y < FH and img[y, x, 3] > 0:
            img[y, x] = c
    if T.get("mask"):
        m = np.array([40, 32, 40, 255], dtype=np.uint8)
        for yy in range(ey + 3, ey + 12):
            for xx in range(ex - 10, ex + 6):
                if 0 <= yy < FH and 0 <= xx < FW and img[yy, xx, 3] > 0 and (img[yy, xx, 0] > 150):
                    img[yy, xx] = m
    x0, y0 = ex - 1, ey - 2
    for dx in range(3):
        put(x0 + dx, y0, lash)
    put(x0, y0 + 1, lash), put(x0 + 1, y0 + 1, iris), put(x0 + 2, y0 + 1, white)
    put(x0, y0 + 2, lash), put(x0 + 1, y0 + 2, iris), put(x0 + 2, y0 + 2, iris)
    put(x0 + 1, y0 + 3, iris2), put(x0 + 2, y0 + 3, iris2)
    if T.get("female"):
        put(x0 + 3, y0, lash)
    put(fx, fy - 2, lash), put(fx + 1, fy - 2, lash)
    put(fx, fy - 1, lash), put(fx + 1, fy - 1, iris)
    put(fx + 1, fy, iris2)
    for dx in range(-1, 3):                                       # brows
        put(x0 + dx, y0 - 2, brow)
    put(fx, fy - 4, brow)
    if not T.get("mask"):
        put(x0 + 2, ey + 4, skin_d)
        put(x0 + 3, ey + 4, np.array([176, 92, 82, 255], dtype=np.uint8))
    if T.get("glasses"):
        g = np.array([206, 226, 244, 255], dtype=np.uint8)
        for xx in range(x0 - 1, x0 + 4):
            put(xx, y0 - 1, g)
            put(xx, y0 + 4, g)
        put(x0 - 1, y0 + 1, g), put(x0 - 1, y0 + 2, g), put(x0 + 3, y0 + 1, g), put(x0 + 3, y0 + 2, g)
        put(fx - 1, fy - 1, g)


def fx_layer(img, P, T):
    im = Image.fromarray(img, "RGBA")
    d = ImageDraw.Draw(im)
    if P["smear"]:
        g = screen(P["ha_n"])
        for r, a in ((18, 90), (16, 170), (14, 255)):
            d.arc([g[0] - r, g[1] - r, g[0] + r, g[1] + r], -80, 45, fill=(255, 255, 255, a), width=2)
    if P["glow"] is not None:
        x, y = screen(P["glow"])
        for rr, a in ((6, 80), (4, 150), (2, 230)):
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(176, 224, 255, a))
    return np.array(im)


def frame(T, kind, i):
    P = pose(kind, i)
    img, depth, _ = render(T, P)
    out = finish(img, depth)
    face(out, T, P)
    # ground shadow under the figure (drawn behind)
    sh = np.zeros_like(out)
    shimg = Image.fromarray(sh, "RGBA")
    ImageDraw.Draw(shimg).ellipse([FW / 2 - 13, GROUND_PY - 2, FW / 2 + 13, GROUND_PY + 2], fill=(0, 0, 0, 80))
    base = np.array(shimg)
    m = out[..., 3] > 0
    base[m] = out[m]
    return fx_layer(base, P, T)


def sheet(T):
    sh = np.zeros((FH * ROWS, FW * COLS, 4), dtype=np.uint8)
    for n, (kind, i) in enumerate(FRAMES):
        f = frame(T, kind, i)
        r, c = n // COLS, n % COLS
        sh[r * FH:(r + 1) * FH, c * FW:(c + 1) * FW] = f
    return Image.fromarray(sh, "RGBA")


def main():
    only = set(sys.argv[1:])
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    os.makedirs(PREVIEW, exist_ok=True)
    strips = []
    for idx, T in enumerate(TRAVELERS):
        if only and T["key"] not in only:
            continue
        sh = sheet(T)
        fname = "trav_%s" % T["key"]
        sh.save(os.path.join(PIC, fname + ".png"))
        e = json.loads(json.dumps(tmpl))
        e.update({"name": {"en": T["name"], "ja": T["name"]}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
                  "aniuv": [COLS, ROWS], "memo": "procedural traveler sprite v2 (tools/gen_sprites3d.py)",
                  "gndpos": [0.5, 4.0 / FH], "atkpos": [0.2, 0.55], "cntpos": [0.5, 0.6], "scale": 1.1,
                  "flipx": True})
        e["animap"] = [{"id": k, "st": v[0], "en": v[1], "spd": v[2], "loop": v[3], "replay": True}
                       for k, v in ANIMAP.items()]
        j["EP%03d" % (200 + idx)] = e
        strip = Image.new("RGBA", (FW * 9, FH), (0, 0, 0, 0))
        for n, fi in enumerate([0, 5, 7, 8, 10, 11, 12, 17, 24]):
            strip.paste(sh.crop(((fi % COLS) * FW, (fi // COLS) * FH, (fi % COLS + 1) * FW, (fi // COLS + 1) * FH)),
                        (n * FW, 0))
        strips.append(strip)
        print("done", T["key"])
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    prev = Image.new("RGBA", (FW * 9 * 3, FH * 3 * len(strips)), (78, 112, 72, 255))
    for r, s in enumerate(strips):
        big = s.resize((s.width * 3, s.height * 3), Image.NEAREST)
        prev.paste(big, (0, r * FH * 3), big)
    prev.save(os.path.join(PREVIEW, "sprites3d.png"))


if __name__ == "__main__":
    main()
