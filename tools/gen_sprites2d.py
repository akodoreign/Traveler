"""Traveler sprites v3: hand-pixel-rule 2D sprite art (Octopath II party look), no 3D rendering.

Everything is drawn directly on the pixel grid: flat material regions shaded by pixel-art rules (light from the
upper front, banded tones, inside-edge selective outlines, dither at tone borders), spiky anime hair clumps with a
shine band, big eyes (lash line, iris, highlight), flared kimono sleeves, pleated hakama, and a distinct weapon/prop
silhouette per traveler.

Frame 80x68 (48-px design grid + reach margin), facing right (flipx in the sheet entry makes the party face the enemies).
Sheet layout v4 (2026-11-07): 14 x 11 cells, 154 frames, blocks listed in BLOCKS (8-frame breathing idle, 8-frame walk,
run, ready, four typed attacks per weapon family, cast + chant + cast_*, item, hurt, evade, guard, KO, collapse,
victory, talk, nod, rei (bow), seiza, seated bow, think, surprise, laugh, front/back field views). animap_for(T) maps
the engine's animation ids (old and new) onto the blocks.
Equipment looks: look_variant(T, weapon, hat) redraws a traveler with another weapon type / head item; main() writes
every combination as EP2000+ and the plugin table plugin/rokugan/RokuganLookData.sk (picked by RokuganLook.sk).
Writes resource/enemy_pic/trav_<key>.png (EP200-EP207), trav_<key>__<weapon>_<hat>.png (EP2000+), preview
_art/preview/sprites2d.png
Run: python -E tools/gen_sprites2d.py [key ...] [--base-only]
"""
import colorsys
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
PIC = os.path.join(RES, "enemy_pic")
PREVIEW = os.path.join(HERE, "..", "_art", "preview")
FW, FH = 80, 68
CY = 8                      # y headroom for tall characters / helmets
CX = 12                     # x offset of the 48-px design grid inside the wider frame (attack reach)
COLS, ROWS = 8, 8
CAST_SCALE = 0.5          # whole-cast size multiplier (user: half size -> real human height vs. 2 m walls)
HUMAN_SCALE = 0.92        # human sprites only: the 2026-11-07 adult proportions drew them ~8% taller in the frame;
                          # this keeps their in-engine height (gen_sprites2d / gen_sidecast / gen_human_enemies)
GROUND = 65

# ------------------------------------------------------------------------------------------- colour ramps


def ramp(rgb):
    """5 tones: 0 outline, 1 shadow, 2 base, 3 light, 4 highlight. Shadows drift to purple, lights to warm."""
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    out = []
    for dv, ds, tgt, amt in ((-0.52, +0.18, 0.75, 0.22), (-0.24, +0.10, 0.75, 0.12), (0, 0, 0, 0),
                             (+0.14, -0.10, 0.13, 0.08), (+0.26, -0.22, 0.13, 0.14)):
        hh = h
        if s > 0.06 and amt:
            diff = ((tgt - h + 0.5) % 1.0) - 0.5
            hh = (h + diff * amt) % 1.0
        vv = v + dv * (0.85 if dv < 0 else 1.0)
        ss = s + ds
        if s < 0.14 and v > 0.72 and dv < 0:              # pale hair / white cloth: deeper, cool lavender shadows
            hh, ss, vv = 0.68, s + (0.16 if dv < -0.3 else 0.09), v + dv * 1.05
        rr, gg, bb = colorsys.hsv_to_rgb(hh, min(1, max(0, ss)), min(1, max(0.03, vv)))
        out.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return out


FIXED = {"eyek": (30, 22, 36), "white": (252, 252, 255), "mouth": (170, 84, 80), "blush": (240, 150, 140),
         "glass": (58, 54, 66), "glint": (255, 255, 255), "fx": (255, 255, 255), "glow": (190, 230, 255), "glowred": (255, 70, 50), "scar": (190, 120, 110)}

# ------------------------------------------------------------------------------------------- travelers
SKIN = (246, 206, 170)
SKIN_TAN = (226, 176, 136)
TRAVELERS = [
    dict(key="natsuko", kit=dict(eye="sharp", brow="angled", mouth="smirk", marks=["scar_nose", "bags"]), idle_spd=6.0, lining=(170, 60, 48), cord=(210, 200, 170), mon="crab", face="sharp", name="Hiruma Natsuko", skin=SKIN_TAN, hair=(56, 46, 50), eye=(120, 84, 56),
         hairstyle="ponytail", bangs="side", head="hachimaki", band=(176, 46, 40), top=(66, 84, 116),
         lower=(48, 54, 72), accent=(164, 54, 44), armor=(96, 108, 128), lace=(170, 60, 48), build="armored",
         weapon="yari", props=["mapcase", "inro"], scar=True, brow="thick", female=True),
    dict(key="rensei", kit=dict(eye="half", brow="straight", mouth="set", marks=["mole_eye"]), idle_spd=3.5, lining=(210, 228, 248), cord=(60, 96, 170), height=1, mon="crane", face="sharp", name="Kakita Rensei", skin=SKIN, hair=(226, 232, 244), eye=(78, 120, 196),
         hairstyle="long_topknot", bangs="parted", top=(236, 238, 246), haori=(150, 190, 230), pattern="dots",
         pcol=(200, 222, 246), lower=(214, 220, 236), accent=(60, 96, 170), build="normal", weapon="katana",
         props=["daisho"], idle="iai", female=False),
    dict(key="gendo", kit=dict(eye="half", brow="skeptical", mouth="set", marks=["bags"]), idle_spd=4.0, lining=(214, 188, 88), cord=(236, 228, 200), height=2, wide=-1, mon="dragon", face="long", name="Kitsuki Gendo", skin=SKIN, hair=(36, 36, 44), eye=(64, 124, 84),
         hairstyle="short", bangs="short", ahoge=True, top=(176, 196, 160), haori=(48, 100, 64), lower=(44, 66, 52),
         pattern="stripes", pattern_on=("lower",), pcol=(70, 96, 76), accent=(214, 188, 88), build="normal",
         weapon="bo", props=["jitte", "inro"], glasses=True, brow="stern", female=False),
    dict(key="shizue", kit=dict(eye="round", brow="straight", mouth="smile", marks=["blush"]), idle_spd=5.0, lining=(158, 42, 36), cord=(240, 210, 120), mon="lion", face="round", name="Akodo Shizue", skin=SKIN, hair=(104, 62, 36), eye=(150, 98, 40),
         hairstyle="bob", bangs="heavy", head="hachimaki", band=(196, 52, 40), top=(214, 166, 56), lower=(128, 86, 44),
         accent=(158, 42, 36), armor=(188, 144, 58), lace=(150, 40, 34), build="armored_light", weapon="katana",
         props=["gunbai", "saya"], female=True),
    dict(key="haruki", kit=dict(eye="gentle", brow="worried", mouth="pout", marks=[]), idle_spd=6.5, lining=(246, 206, 92), cord=(90, 140, 210), height=-1, mon="phoenix", glow=(150, 205, 255), face="round", name="Isawa Haruki", skin=SKIN, hair=(44, 32, 30), eye=(176, 92, 40),
         hairstyle="spiky", bangs="messy", top=(222, 104, 40), lower=(172, 58, 34), accent=(246, 206, 92),
         pattern="waves", pattern_on=("top", "lower"), pcol=(236, 132, 66), build="robe", weapon="shakujo",
         props=["scroll", "ofuda"], female=False),
    dict(key="mitsue", kit=dict(eye="sharp", brow="arched", mouth="smirk", marks=["paint_red"]), idle_spd=5.0, lining=(40, 30, 40), cord=(212, 170, 70), mon="scorpion", face="sharp", name="Shosuro Mitsue", skin=SKIN, hair=(34, 26, 38), eye=(160, 44, 56),
         hairstyle="long", bangs="swept", top=(168, 30, 46), lower=(42, 34, 44), accent=(212, 170, 70),
         pattern="diamonds", pcol=(120, 20, 34), build="normal", weapon="tanto", mask="cloth", mask_col=(118, 30, 42),
         female=True),
    dict(key="tamotsu", kit=dict(eye="smile", brow="arched", mouth="grin", nose="strong", marks=["laugh"]), idle_spd=3.5, lining=(224, 184, 72), cord=(170, 40, 50), mon="unicorn", face="round", name="Ide Tamotsu", skin=SKIN, hair=(94, 60, 38), eye=(96, 62, 44),
         hairstyle="chonmage", facial="beard", top=(236, 228, 214), haori=(118, 72, 158), trim="fur",
         lower=(204, 198, 214), accent=(224, 184, 72), build="round", weapon="yumi", props=["quiver", "gourd"],
         mouth="grin", female=False),
    dict(key="sayo", kit=dict(eye="wide", brow="arched", mouth="smile", marks=["freckles"]), idle_spd=4.5, lining=(120, 150, 110), cord=(196, 70, 60), height=-1, mon="ronin", face="round", name="Sayo", skin=SKIN_TAN, hair=(70, 44, 32), eye=(108, 74, 50),
         hairstyle="long", bangs="normal", top=(150, 120, 84), lower=(98, 80, 62), accent=(70, 112, 72),
         pattern="waves", pcol=(128, 100, 70), build="normal", weapon="katana", props=["basket", "saya"],
         hat="jingasa", female=True),
]
# v4 personality: victory poses and main attacks (animap_for / victory_pose)
_V4 = {"rensei": dict(primary="atk_draw"), "gendo": dict(victory="glasses"), "shizue": dict(victory="gunbai"),
       "haruki": dict(victory="count"), "mitsue": dict(victory="curtain"), "tamotsu": dict(victory="laugh"),
       "sayo": dict(victory="hat_tip")}
for _t in TRAVELERS:
    _t.update(_V4.get(_t["key"], {}))
COLLAR = (238, 234, 224)
WOOD = (140, 94, 54)
METAL = (200, 210, 224)
DARK = (44, 36, 44)
TABI = (236, 234, 228)
SANDAL = (96, 66, 44)
STRAW = (214, 184, 110)

# ------------------------------------------------------------------------------------------- canvas


class Canvas:
    def __init__(self):
        self.col = np.zeros((FH, FW, 4), dtype=np.uint8)
        self.keep = np.zeros((FH, FW), dtype=bool)

    def paste(self, mask, tones, pal):
        """Write a shaded part. tones: int array (same shape), pal: 5-tone ramp."""
        ys, xs = np.nonzero(mask)
        for y, x in zip(ys, xs):
            self.col[y, x, :3] = pal[int(tones[y, x])]
            self.col[y, x, 3] = 255

    def px(self, x, y, rgb):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < FW and 0 <= y < FH:
            self.col[y, x, :3] = rgb
            self.col[y, x, 3] = 255

    def px_on(self, x, y, rgb):
        """Only over already-drawn pixels."""
        x, y = int(round(x)), int(round(y))
        if 0 <= x < FW and 0 <= y < FH and self.col[y, x, 3]:
            self.col[y, x, :3] = rgb


YY, XX = np.mgrid[0:FH, 0:FW]


def m_capsule(a, b, r1, r2=None):
    r2 = r1 if r2 is None else r2
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = max(dx * dx + dy * dy, 1e-6)
    t = np.clip(((XX - ax) * dx + (YY - ay) * dy) / L2, 0, 1)
    px, py = ax + dx * t, ay + dy * t
    d = np.hypot(XX - px, YY - py)
    return d <= (r1 + (r2 - r1) * t), t, ((XX - px) * -dy + (YY - py) * dx) / math.sqrt(L2)


def m_poly(pts):
    from PIL import ImageDraw
    im = Image.new("L", (FW, FH), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.array(im) > 0


def m_ellipse(cx, cy, rx, ry):
    return ((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2 <= 1.0


def edges(mask):
    """Inside-edge pixels of a mask (4-neighbourhood)."""
    p = np.pad(mask, 1)
    inner = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return mask & ~inner


def edge_dir(mask):
    p = np.pad(mask, 1)
    up, dn, lf, rt = ~p[:-2, 1:-1] & mask, ~p[2:, 1:-1] & mask, ~p[1:-1, :-2] & mask, ~p[1:-1, 2:] & mask
    return up, dn, lf, rt


def shade_rows(mask, lit=0.70, shd=0.34, dither=True, outline=True):
    """Pixel-art cylinder banding per row run: light on the right (front), shadow on the left (back)."""
    tones = np.full((FH, FW), 2, dtype=np.int32)
    for y in range(FH):
        row = mask[y]
        if not row.any():
            continue
        xs = np.nonzero(row)[0]
        runs = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
        for run in runs:
            a, b = run[0], run[-1]
            w = max(1, b - a)
            for x in run:
                rel = (x - a) / w
                if rel >= lit:
                    tones[y, x] = 3
                elif rel <= shd:
                    tones[y, x] = 1
                elif dither and rel <= shd + 0.12 and (x + y) % 2 == 0:
                    tones[y, x] = 1
    return finish_tones(mask, tones, outline)


def shade_axis(mask, side, r, outline=True):
    """For capsules: side = signed distance across the limb; positive side is lit when the limb points down."""
    tones = np.full((FH, FW), 2, dtype=np.int32)
    tones[mask & (side > r * 0.35)] = 3
    tones[mask & (side < -r * 0.25)] = 1
    return finish_tones(mask, tones, outline)


def finish_tones(mask, tones, outline=True):
    up, dn, lf, rt = edge_dir(mask)
    if outline:
        tones[(lf | dn) & mask] = 0
        tones[(up | rt) & mask & (tones >= 2)] = np.maximum(tones[(up | rt) & mask & (tones >= 2)], 3)
        tones[(rt & dn) & mask] = 0
        # keep the silhouette readable: outline the upper/right edges too, but with the shadow tone
        tones[(up | rt) & mask & (tones < 3)] = 0
    tones[~mask] = 0
    return tones


# ------------------------------------------------------------------------------------------- sculpted shading
# Bare skin (wrestlers, monks) is modelled as a union of soft solids: each primitive is a height field (an ellipsoid,
# or a capsule along a bone); the body surface is their maximum. Its normals are lit from the upper front (the same
# light as the banded parts) and quantised to the ramp, so pecs, belly, deltoids and thighs get real form shading,
# and a crease (shadow tone) is drawn where two primitives meet: the line under the pecs, the belly fold, the knee.
LIGHT3 = np.array([0.50, -0.62, 0.60])
LIGHT3 = LIGHT3 / np.linalg.norm(LIGHT3)


def hf_ellipse(cx, cy, rx, ry, k=1.0):
    q = 1.0 - ((XX + 0.5 - cx) / rx) ** 2 - ((YY + 0.5 - cy) / ry) ** 2
    return np.where(q > 0, np.sqrt(np.clip(q, 0, 1)) * min(rx, ry) * k, -1.0)


def hf_capsule(a, b, r1, r2=None, k=1.0):
    m, t, side = m_capsule(a, b, r1, r2)
    r = r1 + ((r2 if r2 is not None else r1) - r1) * t
    ax, ay = a
    px, py = ax + (b[0] - ax) * t, ay + (b[1] - ay) * t
    d = np.hypot(XX + 0.5 - px - 0.5, YY + 0.5 - py - 0.5)
    q = 1.0 - (d / np.maximum(r, 0.3)) ** 2
    return np.where(q > 0, np.sqrt(np.clip(q, 0, 1)) * r * k, -1.0)


def sculpt(prims, crease=True, light=None, lo=0.30, mid=0.62, hi=0.88, outline=True, groups=None):
    """prims: list of height fields (hf_*). groups: one label per primitive; primitives with the same label blend
    smoothly (no crease between them). Returns (mask, tones)."""
    H = np.stack(prims)
    top = H.max(0)
    mask = top > 0
    if not mask.any():
        return mask, np.zeros((FH, FW), np.int32)
    h = np.where(mask, top, 0.0)
    gy, gx = np.gradient(h)
    n = np.stack([-gx, -gy, np.ones_like(h)])
    n = n / np.linalg.norm(n, axis=0)
    L = LIGHT3 if light is None else light
    lam = n[0] * L[0] + n[1] * L[1] + n[2] * L[2]
    tones = np.full((FH, FW), 2, dtype=np.int32)
    tones[lam < lo] = 1
    tones[lam >= mid] = 3
    tones[lam >= hi] = 4
    if crease and len(prims) > 1:
        gl = np.array(groups if groups is not None else range(len(prims)))
        lab = np.where(mask, gl[H.argmax(0)], -1)
        sec = np.sort(H, axis=0)[-2]
        p = np.pad(lab, 1, constant_values=-1)
        # one pixel wide: the lower-right side of each region boundary (a valley seen from the upper-right light)
        bd = ((p[1:-1, :-2] != lab) & (p[1:-1, :-2] >= 0)) | ((p[:-2, 1:-1] != lab) & (p[:-2, 1:-1] >= 0))
        cr = mask & bd & (sec > 0.6) & ~edges(mask)
        tones[cr] = np.minimum(tones[cr], 1)
    if outline:
        up, dn, lf, rt = edge_dir(mask)
        tones[(lf | dn) & mask] = 0
        tones[(up | rt) & mask & (tones <= 1)] = 0
    tones[~mask] = 0
    return mask, tones


def outline_outer(cv):
    """Darken the outermost ring of the whole figure where it touches background (selective outline)."""
    a = cv.col[..., 3] > 0
    e = edges(a) & ~getattr(cv, "keep", np.zeros_like(a))
    ys, xs = np.nonzero(e)
    for y, x in zip(ys, xs):
        c = cv.col[y, x, :3].astype(int)
        lum = c.mean()
        if lum > 60:
            cv.col[y, x, :3] = (c * 0.45).astype(np.uint8)


# ------------------------------------------------------------------------------------------- poses
def base_pose():
    return dict(
        dx=0, dy=0, head=(0, 0), lean=0,
        sh_b=(25, 34), el_b=(23, 37), ha_b=(24, 40),
        sh_f=(33, 34), el_f=(35, 37), ha_f=(36, 40),
        hip=(28, 41), kn_b=(25, 49), ft_b=(24, 56), kn_f=(32, 49), ft_f=(33, 56),
        wang=-80.0, wlen=1.0, smear=False, glow=None, sway=0, bow=None, smear_dir="h", sheathed=False, expr=None, glow_small=False)


def shift(P, keys, d):
    for k in keys:
        P[k] = (P[k][0] + d[0], P[k][1] + d[1])


UPPER = ("sh_b", "el_b", "ha_b", "sh_f", "el_f", "ha_f", "hip")


STYLE = {"yari": "thrust", "bo": "thrust", "shakujo": "thrust", "tanto": "thrust", "katana": "slash", "bokken": "slash",
         "nodachi": "slash", "naginata": "slash", "kama": "slash", "fan": "slash", "none": "slash", "tetsubo": "smash",
         "yumi": "shoot", "nunchaku": "slash", "musket": "thrust"}


def lunge(P, dx, dy, foot=7):
    shift(P, UPPER, (dx, dy))
    P["head"] = (dx, dy)
    P["ft_f"] = (P["ft_f"][0] + foot, P["ft_f"][1])
    P["kn_f"] = (P["kn_f"][0] + foot - 1, P["kn_f"][1] - 1)
    P["ft_b"] = (P["ft_b"][0] - 3, P["ft_b"][1])


def pose(kind, i, style="thrust", spear=False):
    P = base_pose()
    if kind == "attack" and style in ("slash", "smash"):
        hi = style == "smash"
        if i == 0:                                         # raise overhead
            shift(P, UPPER, (-2, 1))
            P["head"] = (-2, 1)
            P["el_f"], P["ha_f"] = (31, 25 if hi else 27), (29, 18 if hi else 22)
            P["el_b"], P["ha_b"] = (27, 27), (28, 20 if hi else 23)
            P["wang"] = -100.0 if hi else -125.0
            P["sway"] = 1
            P["grip2"] = True
        elif i == 1:                                       # cut down-forward
            lunge(P, 5, 2 if not hi else 3)
            P["el_f"], P["ha_f"] = (40, 32), (44, 36)
            P["el_b"], P["ha_b"] = (37, 34), (41, 37)
            P["wang"] = 40.0 if not hi else 62.0
            P["smear"], P["smear_dir"] = True, "v"
            P["sway"] = -1
            P["grip2"] = True
        elif i == 2:
            lunge(P, 4, 3 if not hi else 4)
            P["grip2"] = True
            P["el_f"], P["ha_f"] = (40, 40), (41, 45)
            P["el_b"], P["ha_b"] = (36, 40), (39, 44)
            P["wang"] = 78.0
            P["sway"] = -1
        else:
            shift(P, UPPER, (1, 1))
            P["head"] = (1, 1)
            P["ft_f"] = (P["ft_f"][0] + 2, P["ft_f"][1])
            P["el_f"], P["ha_f"] = (36, 35), (39, 37)
            P["wang"] = -30.0
            P["grip2"] = True
        return _finish(P)
    if kind == "attack" and style == "shoot":
        P["ft_f"] = (P["ft_f"][0] + 3, P["ft_f"][1])
        P["ft_b"] = (P["ft_b"][0] - 2, P["ft_b"][1])
        P["el_f"], P["ha_f"] = (37, 31), (41, 31)           # bow arm straight out
        if i == 0:
            P["el_b"], P["ha_b"], P["bow"] = (33, 33), (37, 31), "nock"
        elif i == 1:
            P["el_b"], P["ha_b"], P["bow"] = (22, 31), (27, 28), "draw"
        elif i == 2:
            P["el_b"], P["ha_b"], P["bow"] = (21, 30), (24, 26), "release"
        else:
            P["el_f"], P["ha_f"] = (36, 35), (39, 38)
        return _finish(P)
    if kind == "idle":                         # battle-ready breathing: 1px dip on 1-2, hair sway
        d = [0, 1, 1, 0][i]
        if style == "slash":                   # chudan: two hands on the hilt, blade forward-up
            P["grip2"] = True
            P["el_f"], P["ha_f"] = (34, 34), (37, 37)
            P["el_b"], P["ha_b"] = (30, 35), (34, 38)
            P["wang"] = -42.0
            P["ft_f"] = (P["ft_f"][0] + 2, P["ft_f"][1])
        elif style == "smash":                 # club resting on the shoulder, rising behind the head
            P["el_f"], P["ha_f"] = (32, 37), (29, 33)
            P["wang"] = -118.0
        elif style == "iai":                   # iaijutsu: hand on the sheathed hilt, weight forward
            P["el_f"], P["ha_f"] = (34, 37), (35, 40)
            P["el_b"], P["ha_b"] = (25, 37), (29, 41)
            P["sheathed"] = True
            P["ft_f"] = (P["ft_f"][0] + 2, P["ft_f"][1])
        elif style == "thrust" and spear:      # spear angled forward
            P["grip2"] = True
            P["el_f"], P["ha_f"] = (35, 35), (38, 37)
            P["el_b"], P["ha_b"] = (28, 36), (31, 39)
            P["wang"] = -32.0
            P["ft_f"] = (P["ft_f"][0] + 2, P["ft_f"][1])
        shift(P, UPPER, (0, d))
        P["head"] = (0, d)
        P["sway"] = [0, 1, 1, 0][i]
        P["ha_f"] = (P["ha_f"][0], P["ha_f"][1] + [0, 0, 1, 0][i])
    elif kind == "walk":
        # contact (near leg forward) - passing (near leg supports, far leg swings through, lifted) - contact (far leg
        # forward) - passing (far leg supports, near leg swings). Body is lowest on contact, highest on passing.
        s = [4, 0, -4, 0][i]
        hx = P["hip"][0]
        if i == 0:
            P["ft_f"], P["ft_b"] = (hx + 6, 56), (hx - 5, 56)
            P["pitch_f"], P["pitch_b"] = -12.0, 28.0          # front heel strike, back toe push-off
        elif i == 2:
            P["ft_b"], P["ft_f"] = (hx + 6, 56), (hx - 5, 56)
            P["pitch_b"], P["pitch_f"] = -12.0, 28.0
        elif i == 1:
            P["ft_f"], P["ft_b"] = (hx + 1, 56), (hx - 1, 53)
            P["pitch_b"] = 30.0                               # swing foot: toe down
        else:
            P["ft_b"], P["ft_f"] = (hx + 1, 56), (hx - 1, 53)
            P["pitch_f"] = 30.0
        b = [0, 1, 0, 1][i]
        shift(P, UPPER, (0, -b))
        P["head"] = (0, -b)
        if style == "slash" and not spear:                    # drawn sword carried low, tip forward-down (pole arms upright)
            P["wang"] = 32.0
        elif style == "smash":                                # club rides on the shoulder
            P["wang"] = -118.0
        P["wang"] += [-6.0, 0.0, 6.0, 0.0][i]                 # the carried weapon rocks with the stride
        P["wfront"] = style != "smash"                        # in the near hand, in front, every frame
        P["ha_b"] = (P["ha_b"][0] + s, P["ha_b"][1] - abs(s) // 3)          # back arm swings with the far leg
        P["el_b"] = (P["el_b"][0] + s // 2, P["el_b"][1])
        P["ha_f"] = (P["ha_f"][0] - s * 0.6, P["ha_f"][1] - (1 if s < 0 else 0))  # weapon arm counter-swings
        P["head"] = (P["head"][0] + 1, P["head"][1])                          # slight forward lean
        P["sway"] = [1, 0, -1, 0][i]
    elif kind == "ready":
        P["grip2"] = True
        shift(P, UPPER, (1, 1))
        P["head"] = (1, 1)
        P["ft_f"] = (P["ft_f"][0] + 3, P["ft_f"][1])
        P["kn_f"] = (P["kn_f"][0] + 2, P["kn_f"][1])
        P["ft_b"] = (P["ft_b"][0] - 2, P["ft_b"][1])
        P["el_f"], P["ha_f"] = (36, 34), (39, 35)
        P["wang"] = -35.0
    elif kind == "attack":
        P["grip2"] = True                                     # two-handed weapons (TWO_HAND) thrust with both hands
        if i == 0:                             # wind-up
            shift(P, UPPER, (-2, 1))
            P["head"] = (-2, 1)
            P["el_f"], P["ha_f"] = (28, 35), (23, 36)
            P["el_b"], P["ha_b"] = (22, 35), (21, 38)
            P["wang"] = -165.0
            P["sway"] = 1
        elif i == 1:                           # strike (lunge)
            shift(P, UPPER, (5, 2))
            P["head"] = (5, 2)
            P["ft_f"] = (P["ft_f"][0] + 7, P["ft_f"][1])
            P["kn_f"] = (P["kn_f"][0] + 6, P["kn_f"][1] - 1)
            P["ft_b"] = (P["ft_b"][0] - 3, P["ft_b"][1])
            P["el_f"], P["ha_f"] = (42, 34), (46, 34)
            P["el_b"], P["ha_b"] = (36, 36), (42, 35)
            P["wang"] = 0.0
            P["smear"] = True
            P["sway"] = -1
        elif i == 2:                           # follow-through
            shift(P, UPPER, (4, 3))
            P["head"] = (4, 3)
            P["ft_f"] = (P["ft_f"][0] + 6, P["ft_f"][1])
            P["kn_f"] = (P["kn_f"][0] + 5, P["kn_f"][1] - 1)
            P["ft_b"] = (P["ft_b"][0] - 3, P["ft_b"][1])
            P["el_f"], P["ha_f"] = (40, 41), (42, 45)
            P["el_b"], P["ha_b"] = (34, 40), (38, 44)
            P["wang"] = 40.0
            P["sway"] = -1
        else:                                  # recover
            shift(P, UPPER, (1, 1))
            P["head"] = (1, 1)
            P["ft_f"] = (P["ft_f"][0] + 2, P["ft_f"][1])
            P["el_f"], P["ha_f"] = (36, 35), (39, 37)
            P["wang"] = -30.0
    elif kind == "cast" and i == 0:            # gather: hands together at the chest, small glow
        P["expr"] = "focus"
        P["el_f"], P["ha_f"] = (34, 35), (32, 34)
        P["el_b"], P["ha_b"] = (26, 35), (30, 34)
        P["glow"] = (31, 33)
        P["wang"] = -55.0
        P["glow_small"] = True
    elif kind == "cast":
        P["expr"] = "focus"
        P["el_f"], P["ha_f"] = (36, 28), (38, 23)
        P["el_b"], P["ha_b"] = (22, 33), (25, 29)
        P["glow"] = (39, 20)
        P["wang"] = -95.0
    elif kind == "hurt":
        P["expr"] = "pain"
        k = 5 if i == 0 else 3                             # thrown back by the blow, the front foot skids
        shift(P, UPPER, (-k, 2))
        P["head"] = (-k - 2, 3)
        P["ft_f"] = (P["ft_f"][0] - 2, P["ft_f"][1])
        P["ft_b"] = (P["ft_b"][0] - 3, P["ft_b"][1])
        P["el_f"], P["ha_f"] = (31, 36), (29, 40)
        P["ha_b"] = (P["ha_b"][0] - 3, P["ha_b"][1] - 3)  # the free arm flung back for balance
        P["wang"] = -120.0
        P["sway"] = 2
    elif kind == "evade":                      # quick side-step back, guard kept up, no wince
        k = 4 if i == 0 else 2
        shift(P, UPPER, (-k, 0))
        P["head"] = (-k - 1, 0)
        P["ft_f"] = (P["ft_f"][0] - k, P["ft_f"][1])
        P["ft_b"] = (P["ft_b"][0] - k - 2, P["ft_b"][1] - 1)
        P["kn_f"] = (P["kn_f"][0] - k, P["kn_f"][1])
        P["kn_b"] = (P["kn_b"][0] - k - 1, P["kn_b"][1])
        P["sway"] = 2
    elif kind.startswith("cast_"):             # spell-category casting poses (2 frames: gather, release)
        P["expr"] = "focus" if i == 0 else None
        P["glow_small"] = i == 0
        c = kind[5:]
        if c == "bolt":
            if i == 0:
                P["el_f"], P["ha_f"] = (32, 35), (30, 33)
                P["glow"] = (30, 31)
            else:
                shift(P, UPPER, (2, 0))
                P["head"] = (2, 0)
                P["el_f"], P["ha_f"] = (40, 32), (45, 32)
                P["ft_f"] = (P["ft_f"][0] + 3, P["ft_f"][1])
                P["glow"] = (48, 31)
            P["wang"] = -100.0
        elif c == "area":
            P["el_f"], P["ha_f"] = (36, 26), (37, 18)
            P["el_b"], P["ha_b"] = (24, 26), (23, 18) if i else (27, 20)
            P["glow"] = (31, 10 if i else 15)
            P["wang"] = -90.0
        elif c == "heal":
            if i == 0:
                P["el_f"], P["ha_f"] = (34, 35), (32, 34)
                P["el_b"], P["ha_b"] = (26, 35), (30, 34)
                P["glow"] = (31, 33)
            else:
                P["el_f"], P["ha_f"] = (37, 32), (41, 30)
                P["el_b"], P["ha_b"] = (31, 33), (37, 31)
                P["glow"] = (42, 27)
            P["wang"] = -60.0
        elif c == "ward":
            if i == 0:
                P["el_f"], P["ha_f"] = (32, 35), (27, 33)
                P["el_b"], P["ha_b"] = (28, 35), (33, 33)
            else:
                P["el_f"], P["ha_f"] = (40, 34), (45, 35)
                P["el_b"], P["ha_b"] = (21, 34), (17, 35)
                P["glow"] = (45, 33)
            P["wang"] = -80.0
        elif c == "summon":
            if i == 0:
                shift(P, UPPER, (0, 3))
                P["head"] = (0, 3)
                P["kn_f"] = (P["kn_f"][0] + 2, P["kn_f"][1] + 2)
                P["el_f"], P["ha_f"] = (36, 37), (38, 41)
            else:
                P["el_f"], P["ha_f"] = (36, 24), (36, 15)
                P["el_b"], P["ha_b"] = (25, 24), (25, 15)
                P["glow"] = (31, 5)
            P["wang"] = -90.0
        elif c == "void":
            P["expr"] = "focus"
            P["el_f"], P["ha_f"] = (33, 38), (31, 43)
            P["el_b"], P["ha_b"] = (27, 38), (29, 43)
            P["glow"] = (30, 41) if i else None
            P["wang"] = -150.0
    elif kind == "ko":                         # collapsed to the knees, head bowed, weapon dropped
        P["expr"] = "pain"
        P["dropped"] = True
        P["kneel"] = True
        P["pitch_f"] = P["pitch_b"] = 80.0
        shift(P, UPPER, (3, 8))
        P["head"] = (5, 10)
        P["hip"] = (28, 47)
        P["kn_f"], P["ft_f"] = (34, 54), (25, 56)
        P["kn_b"], P["ft_b"] = (29, 54), (20, 56)
        P["el_f"], P["ha_f"] = (37, 47), (39, 54)
        P["el_b"], P["ha_b"] = (31, 47), (33, 54)
        P["wang"] = 2.0
        P["sway"] = 2
    elif kind == "guard":
        P["grip2"] = True
        shift(P, UPPER, (0, 3))
        P["head"] = (0, 3)
        P["kn_f"] = (P["kn_f"][0] + 2, P["kn_f"][1] + 1)
        P["kn_b"] = (P["kn_b"][0] - 1, P["kn_b"][1] + 1)
        P["el_f"], P["ha_f"] = (37, 34), (36, 29)
        P["el_b"], P["ha_b"] = (28, 37), (33, 33)
        P["wang"] = -100.0
    elif kind == "victory":
        P["expr"] = "grin"
        up = 1 if i == 1 else 0
        shift(P, UPPER, (0, -up))
        P["head"] = (0, -up)
        if style in ("slash", "iai"):           # noto: blade returned to the saya, hand resting on the hilt
            P["el_f"], P["ha_f"] = (34, 37), (35, 40)
            P["el_b"], P["ha_b"] = (25, 37), (29, 41)
            P["sheathed"] = True
        elif style == "thrust" and spear:      # spear planted upright beside
            P["el_f"], P["ha_f"] = (36, 31), (38, 30)
            P["wang"] = -90.0
        elif style == "shoot":                 # bow lowered, other hand raised
            P["el_f"], P["ha_f"] = (35, 36), (37, 40)
            P["el_b"], P["ha_b"] = (22, 27), (21, 21)
        elif style == "smash":                 # club on the shoulder, fist up
            P["el_f"], P["ha_f"] = (35, 37), (34, 32)
            P["el_b"], P["ha_b"] = (23, 27), (22, 20)
            P["wang"] = -140.0
        else:
            P["el_f"], P["ha_f"] = (36, 25), (37, 18)
            P["wang"] = -90.0
    return _finish(P)


def _finish(P):
    P.setdefault("grip2", False)
    P.setdefault("pitch_f", 0.0)
    P.setdefault("pitch_b", 0.0)
    for k, v in list(P.items()):
        if isinstance(v, tuple) and k != "head":
            P[k] = (v[0] + CX, v[1] + CY)
    return P


FRAMES_V3 = [("idle", 0), ("idle", 1), ("idle", 2), ("idle", 3),
          ("walk", 0), ("walk", 1), ("walk", 2), ("walk", 3),
          ("ready", 0), ("ready", 0),
          ("attack", 0), ("attack", 1), ("attack", 2), ("attack", 3), ("attack", 3),
          ("cast", 0), ("cast", 1),
          ("hurt", 0), ("hurt", 1), ("hurt", 1),
          ("guard", 0), ("guard", 0),
          ("ko", 0), ("ko", 0),
          ("victory", 0), ("victory", 1), ("victory", 0),
          ("evade", 0), ("evade", 1),
          ("fidle", 0), ("fidle", 1), ("fidle", 2), ("fidle", 3), ("fwalk", 0), ("fwalk", 1), ("fwalk", 2), ("fwalk", 3),
          ("bidle", 0), ("bidle", 1), ("bidle", 2), ("bidle", 3), ("bwalk", 0), ("bwalk", 1), ("bwalk", 2), ("bwalk", 3)] +     [("cast_" + c, i) for c in ("bolt", "area", "heal", "ward", "summon", "void") for i in (0, 1)]
CAST_KINDS = ("bolt", "area", "heal", "ward", "summon", "void")

ANIMAP_V3 = {
    "stand": (0, 4, 5.0, True), "fight": (0, 4, 5.0, True), "sick": (0, 4, 3.0, True),
    "walk": (4, 8, 8.0, True), "run": (4, 8, 12.0, True), "dash": (4, 8, 12.0, True),
    "jump": (8, 9, 1.0, False), "aim": (8, 9, 1.0, True), "aimw": (8, 9, 1.0, True), "aimp": (8, 9, 1.0, True),
    "aimb": (8, 9, 1.0, True),
    "slash1": (10, 14, 12.0, False), "punch1": (10, 14, 12.0, False), "stick1": (10, 14, 12.0, False),
    "bow1": (10, 14, 10.0, False), "atk": (10, 14, 12.0, False),
    "spell": (15, 17, 5.0, False), "magic1": (15, 17, 5.0, False), "blast1": (15, 17, 5.0, False),
    "damage": (17, 19, 8.0, False), "avoid": (27, 29, 8.0, False),
    "shield": (20, 21, 1.0, False), "guard": (20, 21, 1.0, True), "die": (22, 23, 1.0, True),
    "victory": (24, 26, 3.0, True),
    "stand_f": (29, 33, 5.0, True), "walk_f": (33, 37, 8.0, True), "run_f": (33, 37, 12.0, True),
    "dash_f": (33, 37, 12.0, True), "stand_b": (37, 41, 5.0, True), "walk_b": (41, 45, 8.0, True),
    "run_b": (41, 45, 12.0, True), "dash_b": (41, 45, 12.0, True),
    **{"cast_" + c: (45 + 2 * k, 47 + 2 * k, 4.0, False) for k, c in enumerate(("bolt", "area", "heal", "ward", "summon", "void"))},
}


# ------------------------------------------------------------------------------------------- animation set v4
# Sheet layout v4 (2026-11-07): 14 x 11 cells, 154 frames. Blocks in order (name, frames). Side-view blocks are
# drawn by pose_v4 / the legacy pose(); f*/b* blocks are the front / back field views (compose_fb).
BLOCKS = [
    ("idle8", 8), ("walk8", 8), ("run", 6), ("ready", 2),
    ("atk_slash", 6), ("atk_thrust", 6), ("atk_overhead", 6), ("atk_draw", 6),
    ("cast", 2), ("chant", 4)] + [("cast_" + c, 2) for c in CAST_KINDS] + [
    ("item", 4), ("hurt", 3), ("evade", 2), ("guard", 2), ("ko", 2), ("collapse", 4), ("victory2", 4),
    ("talk", 4), ("nod", 4), ("rei", 6), ("seiza", 2), ("seiza_rei", 3), ("think", 2), ("surprise", 2),
    ("laugh", 2),
    ("fidle", 4), ("fwalk8", 8), ("bidle", 4), ("bwalk8", 8),
    ("ftalk", 4), ("fnod", 4), ("frei", 3), ("bnod", 4), ("brei", 3)]
COLS, ROWS = 14, 11
LEGACY_IDX = {"ready": [0, 0], "cast": [0, 1], "hurt": [0, 1, 1], "evade": [0, 1], "guard": [0, 0], "ko": [0, 0],
              "fidle": [0, 1, 2, 3], "bidle": [0, 1, 2, 3]}
FRAMES, BLOCK_AT = [], {}
for _name, _n in BLOCKS:
    BLOCK_AT[_name] = (len(FRAMES), _n)
    for _i in range(_n):
        if _name in LEGACY_IDX:
            FRAMES.append((_name, LEGACY_IDX[_name][_i]))
        elif _name.startswith("cast_"):
            FRAMES.append((_name, _i))
        else:
            FRAMES.append((_name, _i))
assert len(FRAMES) <= COLS * ROWS, len(FRAMES)
ATTACKS = ("atk_slash", "atk_thrust", "atk_overhead", "atk_draw")


def _blk(name, a=0, b=None):
    s, n = BLOCK_AT[name]
    return s + a, s + (n if b is None else b)


def wfamily(w):
    if w in ("katana", "bokken", "nodachi"):
        return "blade"
    if w in ("yari", "naginata", "bo", "shakujo"):
        return "pole"
    if w == "tetsubo":
        return "club"
    if w == "yumi":
        return "bow"
    if w == "musket":
        return "gun"
    if w == "none":
        return "fist"
    return "short"                                       # tanto, kama, fan, nunchaku: one hand


PRIMARY = {"blade": "atk_slash", "pole": "atk_thrust", "club": "atk_overhead", "bow": "atk_slash",
           "gun": "atk_thrust", "fist": "atk_thrust", "short": "atk_thrust"}


def primary_attack(T):
    if T.get("primary"):
        return T["primary"]
    if T.get("weapon") in ("naginata", "kama", "fan", "nunchaku"):
        return "atk_slash"
    return PRIMARY[wfamily(T.get("weapon", "none"))]


def animap_for(T=None):
    """Animation id -> (first frame, end frame, fps, loop) for a v4 sheet. Old engine ids keep their meaning:
    stand/fight (battle idle), walk/run/dash, aim*, slash1/punch1/stick1/bow1/atk (this sheet's main attack),
    spell/magic1/blast1, damage, avoid, shield/guard, die, victory, *_f/*_b field facings, cast_*. New ids:
    atk_slash, atk_thrust, atk_overhead, atk_draw, atk_main, chant, item, collapse, victory_in, talk, nod, rei,
    rei_full, seiza, sit, seiza_rei, think, surprise, laugh, talk_f, nod_f, rei_f, talk_b, nod_b, rei_b."""
    T = T or {}
    idle = T.get("idle_spd", 5.0) * 1.6                    # 8 frames where the old idle had 4
    main = primary_attack(T)
    A = {
        "stand": _blk("idle8") + (idle, True), "fight": _blk("idle8") + (idle, True),
        "sick": _blk("idle8") + (idle * 0.6, True), "idle": _blk("idle8") + (idle, True),
        "walk": _blk("walk8") + (13.0, True), "run": _blk("run") + (13.0, True), "dash": _blk("run") + (15.0, True),
        "jump": _blk("ready", 0, 1) + (1.0, False),
        "aim": _blk("ready", 0, 1) + (1.0, True), "aimw": _blk("ready", 0, 1) + (1.0, True),
        "aimp": _blk("ready", 0, 1) + (1.0, True), "aimb": _blk("ready", 0, 1) + (1.0, True),
        "spell": _blk("cast") + (5.0, False), "magic1": _blk("cast") + (5.0, False),
        "blast1": _blk("cast") + (5.0, False), "chant": _blk("chant") + (6.0, True),
        "damage": _blk("hurt", 0, 2) + (8.0, False), "avoid": _blk("evade") + (8.0, False),
        "shield": _blk("guard", 0, 1) + (1.0, False), "guard": _blk("guard", 0, 1) + (1.0, True),
        "die": _blk("ko", 0, 1) + (1.0, True), "collapse": _blk("collapse") + (7.0, False),
        "victory": _blk("victory2", 2, 4) + (2.5, True), "victory_in": _blk("victory2") + (6.0, False),
        "item": _blk("item") + (6.0, False),
        "talk": _blk("talk") + (5.0, True), "nod": _blk("nod") + (8.0, False),
        "rei": _blk("rei", 0, 3) + (5.0, False), "rei_full": _blk("rei") + (5.0, False),
        "seiza": _blk("seiza") + (1.5, True), "sit": _blk("seiza") + (1.5, True),
        "seiza_rei": _blk("seiza_rei") + (4.0, False), "think": _blk("think") + (1.5, True),
        "surprise": _blk("surprise") + (8.0, False), "laugh": _blk("laugh") + (6.0, True),
        "stand_f": _blk("fidle") + (5.0, True), "walk_f": _blk("fwalk8") + (13.0, True),
        "run_f": _blk("fwalk8") + (18.0, True), "dash_f": _blk("fwalk8") + (18.0, True),
        "stand_b": _blk("bidle") + (5.0, True), "walk_b": _blk("bwalk8") + (13.0, True),
        "run_b": _blk("bwalk8") + (18.0, True), "dash_b": _blk("bwalk8") + (18.0, True),
        "talk_f": _blk("ftalk") + (5.0, True), "nod_f": _blk("fnod") + (8.0, False),
        "rei_f": _blk("frei") + (5.0, False), "talk_b": _blk("bidle") + (5.0, True),
        "nod_b": _blk("bnod") + (8.0, False), "rei_b": _blk("brei") + (5.0, False),
    }
    for a in ATTACKS:
        A[a] = _blk(a) + (14.0, False)
    for k in ("slash1", "punch1", "stick1", "bow1", "atk", "atk_main"):
        A[k] = _blk(main) + (14.0 if k != "bow1" else 12.0, False)
    for c in CAST_KINDS:
        A["cast_" + c] = _blk("cast_" + c) + (4.0, False)
    return A


ANIMAP = animap_for()


def _key(P, d):
    """Apply one keyframe: b body shift, hd extra head shift, ff/fb front/back foot x, hf/hb hand targets (design
    grid), w weapon angle, plus any flag (sm smear dir, ex expression, g2 two-handed grip, sh sheathed)."""
    b = d.get("b", (0, 0))
    if b != (0, 0):
        shift(P, UPPER, b)
    hd = d.get("hd", (0, 0))
    P["head"] = (P["head"][0] + b[0] + hd[0], P["head"][1] + b[1] + hd[1])
    if d.get("ff"):
        P["ft_f"] = (P["ft_f"][0] + d["ff"], P["ft_f"][1])
    if d.get("fb"):
        P["ft_b"] = (P["ft_b"][0] + d["fb"], P["ft_b"][1])
    if "hf" in d:
        P["ha_f"] = d["hf"]
    if "hb" in d:
        P["ha_b"] = d["hb"]
    if "w" in d:
        P["wang"] = d["w"]
    if "sm" in d:
        P["smear"], P["smear_dir"] = True, d["sm"]
    if "ex" in d:
        P["expr"] = d["ex"]
    if "g2" in d:
        P["grip2"] = d["g2"]
    if "sh" in d:
        P["sheathed"] = d["sh"]
    for k in ("sway", "bow", "bow_tilt", "dust", "muzzle", "smear_r", "whand", "hand_prop", "fingers", "fist",
              "open_hand", "glow", "glow_small", "kneel", "pitch_f", "pitch_b", "hip", "kn_f", "kn_b", "ft_f",
              "ft_b", "wlay", "dropped"):
        if k in d:
            P[k] = d[k]
    return P


# Attack keyframes per weapon family (design grid; the body stands at hip (28,41), near shoulder (33,34)).
CHUDAN = dict(hf=(37, 37), w=-42.0, g2=True)
ATK = {
    ("blade", "atk_slash"): [                               # kesa-giri: from hasso down across the body
        dict(b=(-1, 0), hf=(33, 31), w=-118.0, g2=True, sway=1),
        dict(b=(-2, 1), hf=(31, 26), w=-140.0, g2=True, sway=1),
        dict(b=(3, 1), ff=4, hf=(40, 29), w=-55.0, g2=True, sm="v", smear_r=0.95),
        dict(b=(5, 2), ff=7, fb=-3, hf=(45, 35), w=28.0, g2=True, sm="v", sway=-1),
        dict(b=(5, 3), ff=7, fb=-3, hf=(43, 42), w=72.0, g2=True, sway=-1),
        dict(b=(2, 1), ff=3, hf=(38, 37), w=-28.0, g2=True)],
    ("blade", "atk_thrust"): [                              # tsuki
        dict(b=(-1, 1), hf=(34, 37), w=-18.0, g2=True),
        dict(b=(-3, 2), fb=-1, hf=(30, 37), w=-8.0, g2=True, sway=1),
        dict(b=(4, 2), ff=6, fb=-3, hf=(43, 36), w=-5.0, g2=True, sm="t"),
        dict(b=(7, 2), ff=8, fb=-4, hf=(48, 35), w=-3.0, g2=True, sm="t", sway=-1),
        dict(b=(6, 2), ff=8, fb=-4, hf=(46, 36), w=-6.0, g2=True, sway=-1),
        dict(b=(2, 1), ff=3, hf=(38, 37), w=-25.0, g2=True)],
    ("blade", "atk_overhead"): [                            # jodan: up over the head, straight down
        dict(b=(0, 1), hf=(34, 30), w=-96.0, g2=True),
        dict(b=(-2, 0), hd=(0, -1), hf=(31, 21), w=-102.0, g2=True, sway=1),
        dict(b=(-2, -1), hf=(30, 19), w=-84.0, g2=True, sway=1),
        dict(b=(5, 3), ff=7, fb=-3, hf=(43, 32), w=30.0, g2=True, sm="v", sway=-1),
        dict(b=(5, 4), ff=7, fb=-3, hf=(43, 40), w=72.0, g2=True, dust=True, sway=-1),
        dict(b=(2, 2), ff=3, hf=(38, 38), w=-20.0, g2=True)],
    ("blade", "atk_draw"): [                                # iaijutsu: crouch on the sheathed blade, one cut, noto
        dict(b=(1, 2), ff=3, hf=(35, 40), hb=(29, 41), sh=True, g2=False),
        dict(b=(2, 3), ff=5, hf=(35, 41), hb=(29, 42), sh=True, g2=False, ex="focus"),
        dict(b=(6, 2), ff=8, fb=-3, hf=(46, 34), hb=(23, 39), w=-6.0, g2=False, sm="w", sway=-1),
        dict(b=(7, 2), ff=8, fb=-3, hf=(48, 31), hb=(22, 38), w=-24.0, g2=False, sm="w", sway=-1),
        dict(b=(6, 2), ff=8, fb=-3, hf=(46, 29), hb=(23, 38), w=-36.0, g2=False),
        dict(b=(3, 1), ff=4, hf=(35, 40), hb=(29, 41), sh=True, g2=False, ex="calm")],
    ("pole", "atk_thrust"): [
        dict(b=(-1, 1), hf=(35, 36), w=-12.0, g2=True),
        dict(b=(-3, 2), fb=-1, hf=(29, 37), w=-7.0, g2=True, sway=1),
        dict(b=(4, 2), ff=6, fb=-3, hf=(42, 35), w=-4.0, g2=True, sm="t"),
        dict(b=(7, 2), ff=8, fb=-4, hf=(47, 34), w=-2.0, g2=True, sm="t", sway=-1),
        dict(b=(6, 2), ff=8, fb=-4, hf=(45, 35), w=-4.0, g2=True, sway=-1),
        dict(b=(2, 1), ff=3, hf=(38, 36), w=-25.0, g2=True)],
    ("pole", "atk_slash"): [                                # a sweeping cut with the long blade / the staff's end
        dict(b=(-1, 0), hf=(32, 32), w=-150.0, g2=True, sway=1),
        dict(b=(-2, 1), hf=(30, 30), w=-168.0, g2=True, sway=1),
        dict(b=(3, 1), ff=4, hf=(40, 31), w=-62.0, g2=True, sm="v", smear_r=1.15),
        dict(b=(5, 2), ff=7, fb=-3, hf=(44, 36), w=14.0, g2=True, sm="v", smear_r=1.15, sway=-1),
        dict(b=(5, 3), ff=7, fb=-3, hf=(42, 40), w=40.0, g2=True, sway=-1),
        dict(b=(2, 1), ff=3, hf=(38, 36), w=-25.0, g2=True)],
    ("pole", "atk_overhead"): [
        dict(b=(0, 1), hf=(34, 31), w=-110.0, g2=True),
        dict(b=(-2, 0), hd=(0, -1), hf=(31, 22), w=-118.0, g2=True, sway=1),
        dict(b=(-2, -1), hf=(30, 20), w=-96.0, g2=True, sway=1),
        dict(b=(5, 3), ff=7, fb=-3, hf=(43, 32), w=22.0, g2=True, sm="v", smear_r=1.15, sway=-1),
        dict(b=(5, 4), ff=7, fb=-3, hf=(43, 39), w=48.0, g2=True, dust=True, sway=-1),
        dict(b=(2, 2), ff=3, hf=(38, 37), w=-25.0, g2=True)],
    ("pole", "atk_draw"): [                                 # kiriage: low and behind, rising through the target
        dict(b=(0, 2), hf=(32, 41), w=150.0, g2=True),
        dict(b=(-1, 3), fb=-1, hf=(30, 42), w=162.0, g2=True, sway=1),
        dict(b=(4, 2), ff=6, fb=-3, hf=(41, 38), w=40.0, g2=True, sm="u"),
        dict(b=(6, 1), ff=8, fb=-3, hf=(45, 31), w=-38.0, g2=True, sm="u", sway=-1),
        dict(b=(6, 1), ff=8, fb=-3, hf=(44, 27), w=-70.0, g2=True, sway=-1),
        dict(b=(2, 1), ff=3, hf=(38, 36), w=-30.0, g2=True)],
    ("fist", "atk_thrust"): [                               # straight punch
        dict(b=(0, 1), hf=(37, 34), hb=(34, 35), fist=True),
        dict(b=(-2, 2), fb=-1, hf=(33, 35), hb=(35, 33), fist=True, sway=1),
        dict(b=(4, 2), ff=6, fb=-3, hf=(44, 33), hb=(31, 37), fist=True, sm="t"),
        dict(b=(6, 2), ff=7, fb=-4, hf=(47, 33), hb=(30, 37), fist=True, sm="t", sway=-1),
        dict(b=(5, 2), ff=7, fb=-4, hf=(45, 34), hb=(31, 36), fist=True, sway=-1),
        dict(b=(1, 1), ff=2, hf=(37, 34), hb=(34, 35), fist=True)],
    ("fist", "atk_slash"): [                                # open-palm strike from the hip
        dict(b=(-1, 1), hf=(33, 40), hb=(35, 33)),
        dict(b=(-2, 2), hf=(30, 41), hb=(36, 33), sway=1),
        dict(b=(4, 2), ff=6, fb=-3, hf=(44, 35), hb=(31, 37), sm="t"),
        dict(b=(6, 2), ff=7, fb=-4, hf=(47, 34), hb=(30, 38), sway=-1),
        dict(b=(5, 2), ff=7, fb=-4, hf=(45, 35), hb=(31, 37), sway=-1),
        dict(b=(1, 1), ff=2, hf=(37, 34), hb=(34, 35), fist=True)],
    ("fist", "atk_overhead"): [                             # leaping hammer-fist
        dict(b=(0, 2), hf=(36, 36), hb=(34, 37), fist=True),
        dict(b=(1, -2), ff=2, hf=(36, 22), hb=(32, 23), fist=True, sway=1),
        dict(b=(2, -3), ff=3, hf=(37, 20), hb=(33, 21), fist=True, sway=1),
        dict(b=(5, 3), ff=7, fb=-3, hf=(44, 34), hb=(42, 35), fist=True, sm="v", smear_r=0.6, sway=-1),
        dict(b=(5, 4), ff=7, fb=-3, hf=(44, 41), hb=(42, 41), fist=True, dust=True, sway=-1),
        dict(b=(1, 1), ff=2, hf=(37, 34), hb=(34, 35), fist=True)],
    ("fist", "atk_draw"): [                                 # front kick
        dict(b=(0, 1), hf=(37, 34), hb=(34, 35), fist=True),
        dict(b=(-1, 0), hf=(35, 33), hb=(31, 36), fist=True, ft_f=(36, 48), pitch_f=40.0),
        dict(b=(-2, 0), hf=(34, 33), hb=(29, 36), fist=True, ft_f=(46, 44), pitch_f=-30.0, sm="t"),
        dict(b=(-2, 0), hf=(34, 33), hb=(29, 36), fist=True, ft_f=(47, 43), pitch_f=-35.0),
        dict(b=(-1, 0), hf=(35, 33), hb=(31, 36), fist=True, ft_f=(37, 49), pitch_f=40.0),
        dict(b=(1, 1), ff=2, hf=(37, 34), hb=(34, 35), fist=True)],
    ("gun", "atk_thrust"): [                                # matchlock: raise, sight, fire, recoil
        dict(b=(0, 1), hf=(34, 37), w=-40.0, g2=True),
        dict(b=(1, 1), hd=(1, 0), ff=2, hf=(37, 34), w=-3.0, g2=True, ex="focus"),
        dict(b=(1, 1), hd=(1, 0), ff=2, hf=(37, 34), w=-3.0, g2=True, muzzle=True),
        dict(b=(-2, 1), hd=(0, 0), ff=2, hf=(35, 33), w=-14.0, g2=True, muzzle=True, sway=1),
        dict(b=(-1, 1), ff=2, hf=(36, 34), w=-8.0, g2=True),
        dict(b=(0, 1), hf=(34, 37), w=-40.0, g2=True)],
}
# the same moves for the other families
for _a in ATTACKS:
    ATK[("club", _a)] = ATK[("pole", _a)] if _a != "atk_slash" else ATK[("blade", "atk_slash")]
    ATK[("short", _a)] = [dict(d, g2=False, hb=d.get("hb", (24, 39))) for d in ATK[("blade", _a)]]
    ATK.setdefault(("gun", _a), ATK[("gun", "atk_thrust")])
ATK[("club", "atk_overhead")] = ATK[("blade", "atk_overhead")]
ATK[("blade", "atk_slash_spear")] = ATK[("pole", "atk_slash")]
# the bow: a standard shot, a snap shot, an arcing volley, a kneeling shot (string hand = the far hand)
_ST = dict(ff=3, fb=-2)
_KNEEL = dict(kneel=True, b=(0, 5), hip=(28, 46), kn_b=(25, 54), ft_b=(19, 56), kn_f=(34, 47), ft_f=(34, 56),
              pitch_b=70.0)
ATK.update({
    ("bow", "atk_slash"): [
        dict(_ST, hf=(37, 33), hb=(35, 33), bow="nock"),
        dict(_ST, hf=(40, 31), hb=(28, 30), bow="draw"),
        dict(_ST, hf=(41, 31), hb=(25, 29), bow="draw", ex="focus"),
        dict(_ST, hf=(41, 31), hb=(22, 28), bow="release", sway=-1),
        dict(_ST, hf=(41, 32), hb=(23, 30), bow=None),
        dict(_ST, hf=(37, 36), hb=(25, 38), bow=None)],
    ("bow", "atk_thrust"): [
        dict(_ST, hf=(39, 32), hb=(33, 32), bow="nock"),
        dict(_ST, hf=(41, 31), hb=(27, 30), bow="draw"),
        dict(_ST, hf=(41, 31), hb=(23, 29), bow="release", sway=-1),
        dict(_ST, hf=(41, 31), hb=(22, 29), bow="release"),
        dict(_ST, hf=(40, 33), hb=(24, 33), bow=None),
        dict(_ST, hf=(37, 36), hb=(25, 38), bow=None)],
    ("bow", "atk_overhead"): [
        dict(_ST, hf=(38, 30), hb=(35, 32), bow="nock", bow_tilt=-20.0),
        dict(_ST, hf=(39, 26), hb=(29, 32), bow="draw", bow_tilt=-35.0),
        dict(_ST, hf=(39, 25), hb=(27, 32), bow="draw", bow_tilt=-38.0, ex="focus"),
        dict(_ST, hf=(39, 25), hb=(25, 31), bow="release", bow_tilt=-38.0, sway=-1),
        dict(_ST, hf=(39, 27), hb=(26, 32), bow=None, bow_tilt=-30.0),
        dict(_ST, hf=(37, 36), hb=(25, 38), bow=None)],
    ("bow", "atk_draw"): [
        dict(_KNEEL, hf=(38, 37), hb=(36, 37), bow="nock"),
        dict(_KNEEL, hf=(41, 36), hb=(29, 35), bow="draw"),
        dict(_KNEEL, hf=(42, 36), hb=(26, 34), bow="draw", ex="focus"),
        dict(_KNEEL, hf=(42, 36), hb=(23, 33), bow="release", sway=-1),
        dict(_KNEEL, hf=(42, 37), hb=(24, 35), bow=None),
        dict(_ST, hf=(37, 36), hb=(25, 38), bow=None)],
})


def _social(T, P, open_hand=True):
    """Weapon handling outside a fight: blades go back in the scabbard, long weapons and bows rest upright in the far
    hand, so the near hand is free to gesture."""
    fam = wfamily(T["weapon"])
    if fam in ("blade", "short"):
        P["sheathed"] = True
    elif fam in ("pole", "club", "bow", "gun"):
        P["whand"] = "b"
        P["ha_b"] = (19, 39)                               # held out behind, so the staff shows past the back
        P["wang"] = -93.0 if fam != "club" else -100.0
    P["open_hand"] = open_hand
    P["grip2"] = False
    return P


def pose_v4(T, kind, i):
    """New v4 blocks (side view). Returns a finished pose (frame coords)."""
    w = T["weapon"]
    fam = wfamily(w)
    style = STYLE.get(w, "thrust")
    spear = w in ("yari", "naginata")
    if kind == "idle8":                                    # breathing: chest and head rise, hands lag a frame
        st = T.get("idle") if T.get("idle") and (w in ("katana", "bokken", "nodachi")) else style
        P = pose("idle", 0, st, spear=spear)
        P = {k: ((v[0] - CX, v[1] - CY) if isinstance(v, tuple) and k != "head" else v) for k, v in P.items()}
        up = [0, 0, 1, 1, 1, 1, 0, 0][i]
        hand = [0, 0, 0, 1, 1, 1, 1, 0][i]
        shift(P, ("sh_b", "el_b", "sh_f", "el_f"), (0, -up))
        P["head"] = (P["head"][0], P["head"][1] - up)
        P["ha_f"] = (P["ha_f"][0], P["ha_f"][1] - hand)
        P["ha_b"] = (P["ha_b"][0], P["ha_b"][1] - hand)
        P["wang"] += [0.0, 0.8, 1.6, 2.0, 1.6, 0.8, 0.0, -0.6][i]
        P["sway"] = [0, 0, 1, 1, 1, 1, 0, 0][i]
        if T.get("build") == "strongman":                  # a wrestler's ready stance: feet wide, fists ready
            P["ft_f"] = (P["ft_f"][0] + 3, P["ft_f"][1])
            P["ft_b"] = (P["ft_b"][0] - 4, P["ft_b"][1])
            P["ha_f"] = (41, 40 - hand)                  # both fists up in front, elbows bent, clear of the chest
            P["ha_b"] = (45, 36 - hand)
            P["grip2"], P["fist"] = False, True
        if T.get("build") == "sumai":                      # a wrestler's ready stance: feet wide, fists low
            P["ft_f"] = (P["ft_f"][0] + 3, P["ft_f"][1])
            P["ft_b"] = (P["ft_b"][0] - 4, P["ft_b"][1])
            P["ha_f"] = (30, 46 - hand)                  # the near arm hangs down the side, the belly in front
            P["ha_b"] = (43, 38 - hand)                  # the far fist pushed forward past it
            P["grip2"], P["fist"] = False, True
        return _finish(P)
    if kind == "walk8":
        return _finish(walk_cycle(T, i, 8, style, spear))
    if kind == "run":
        return _finish(run_cycle(T, i, style, spear))
    if kind in ATTACKS:
        P = base_pose()
        fam2 = fam
        seq = ATK.get((fam2, kind)) or ATK[("blade", kind)]
        if fam == "blade" and kind == "atk_draw" and w == "nodachi":
            seq = ATK[("pole", "atk_draw")]
        if fam == "short" and kind == "atk_draw":            # quick one-handed draw-and-stab
            seq = ATK[("short", "atk_thrust")]
        d = seq[i]
        if fam in ("bow",):
            P["ft_f"] = (P["ft_f"][0], P["ft_f"][1])
        _key(P, d)
        if fam == "short":                                  # the free hand balances out behind
            P["grip2"] = False
        if fam == "fist" and "sm" in d:
            P["smear_r"] = 0.35
        return _finish(P)
    P = base_pose()
    if kind == "chant":                                     # hands pressed together (gassho), the light pulsing
        b = [0, 0, 1, 0][i]
        _key(P, dict(b=(0, -b), hf=(34, 34), hb=(32, 34), ex="focus", sway=[0, 1, 1, 0][i],
                     glow=(32, 31 - b), glow_small=i % 2 == 0))
        _social(T, P, open_hand=True)
        if fam in ("pole", "club", "bow", "gun"):          # the staff tucked into the crook of the arm
            P["whand"] = "b"
            P["ha_b"] = (31, 34)
        return _finish(P)
    if kind == "item":
        _social(T, P, open_hand=False)
        seq = [dict(hf=(35, 40), hd=(1, 1), fist=True),
               dict(hf=(37, 34), hand_prop="item"),
               dict(hf=(38, 28), hd=(0, -1), hand_prop="item"),
               dict(hf=(38, 27), hd=(0, -1), hand_prop="item", glow=(39, 21), glow_small=True)]
        _key(P, seq[i])
        if i == 0:
            P["open_hand"] = False
        return _finish(P)
    if kind == "collapse":
        seq = [dict(b=(-4, 1), hd=(-1, 1), hf=(31, 37), w=-120.0, ex="pain", sway=2),
               dict(b=(-2, 4), hd=(0, 1), ff=1, fb=-1, hf=(33, 43), w=30.0, ex="pain", sway=2),
               None, None]
        if seq[i] is not None:
            _key(P, seq[i])
            return _finish(P)
        Q = pose("ko", 0, style, spear)
        if i == 2:                                           # half down: upright on the knees, head bowed
            Q = {k: ((v[0] - CX, v[1] - CY) if isinstance(v, tuple) and k != "head" else v) for k, v in Q.items()}
            shift(Q, UPPER, (-2, -3))
            Q["head"] = (Q["head"][0] - 3, Q["head"][1] - 4)
            return _finish(Q)
        return Q
    if kind == "victory2":
        return _finish(victory_pose(T, i, fam, style, spear))
    if kind == "talk":
        _social(T, P)
        hands = [(37, 37), (40, 33), (39, 35), (41, 34)]
        _key(P, dict(hf=hands[i], ex="talk" if i in (1, 3) else None, hd=(0, 1 if i == 3 else 0)))
        return _finish(P)
    if kind == "nod":
        _social(T, P)
        P["open_hand"] = False
        d = [(0, 0), (1, 1), (1, 2), (0, 0)][i]
        _key(P, dict(hd=d, hf=(36, 40), ex="calm" if i == 2 else None))
        return _finish(P)
    if kind == "rei":
        _social(T, P)
        deg = [0, 1, 2, 2, 1, 0][i]
        lean = [(0, 0), (2, 1), (4, 3)][deg]
        head = [(0, 0), (4, 3), (7, 6)][deg]
        shift(P, ("sh_b", "el_b", "sh_f", "el_f"), lean)
        P["head"] = head
        hip = P["hip"]
        P["ha_f"] = (hip[0] + 4 + deg, hip[1] + 4 + deg)       # the hands slide down the front of the thighs
        P["expr"] = "calm" if deg == 2 else None
        if P.get("whand") == "b":
            P["ha_b"] = (19 + lean[0] // 2, 39 + lean[1] // 2)
        P["open_hand"] = True
        return _finish(P)
    if kind in ("seiza", "seiza_rei"):
        k = 0 if kind == "seiza" else i
        _social(T, P)
        P.pop("whand", None)
        P["kneel"] = True
        drop = 8
        shift(P, UPPER, (0, drop))
        P["head"] = (0, drop)
        P["hip"] = (27, 41 + drop)
        P["kn_f"], P["ft_f"] = (36, 54), (25, 56)
        P["kn_b"], P["ft_b"] = (35, 55), (24, 56)
        P["pitch_f"] = P["pitch_b"] = 80.0
        P["ha_f"], P["ha_b"] = (34, 48), (32, 49)
        if fam in ("pole", "club", "bow", "gun"):               # laid on the floor beside
            P["wlay"] = (8, 55)
            P["wang"] = 0.0 if fam != "bow" else 0.0
        if kind == "seiza" and i == 1:
            shift(P, ("sh_b", "el_b", "sh_f", "el_f"), (0, -1))
            P["head"] = (0, drop - 1)
        if kind == "seiza_rei":
            lean = [(0, 0), (3, 3), (6, 6)][k]
            shift(P, ("sh_b", "el_b", "sh_f", "el_f"), lean)
            P["head"] = (lean[0] + [0, 2, 5][k], drop + lean[1] + [0, 1, 3][k])
            if k:
                P["ha_f"], P["ha_b"] = (38 + 2 * k, 52 + 2 * k), (36 + 2 * k, 52 + 2 * k)
            P["expr"] = "calm" if k else None
        P["open_hand"] = True
        return _finish(P)
    if kind == "think":
        _social(T, P)
        _key(P, dict(hf=(37, 28), hb=P["ha_b"] if P.get("whand") == "b" else (31, 37), ex="think",
                     hd=(0, -1 if i else 0), fist=True))
        P["open_hand"] = False
        return _finish(P)
    if kind == "surprise":
        _social(T, P)
        if i == 0:
            _key(P, dict(b=(-3, -2), hd=(-1, 0), ff=-4, fb=-5, hf=(39, 27), ex="surprise", sway=2))
            P["ft_f"] = (P["ft_f"][0], 54)
            P["ft_b"] = (P["ft_b"][0], 53)
        else:
            _key(P, dict(b=(-4, 1), hd=(-1, 0), ff=-3, fb=-6, hf=(38, 31), ex="surprise", sway=1))
        return _finish(P)
    if kind == "laugh":
        _social(T, P)
        _key(P, dict(b=(-1, 0), hd=(-1, -1 if i == 0 else 0), hf=(34, 40), ex="laugh2" if i == 0 else "laugh",
                     sway=i))
        P["open_hand"] = True
        return _finish(P)
    raise KeyError(kind)


def walk_cycle(T, i, n, style, spear, stride=5.5, lift=3.0):
    """A parametric walk (n frames per cycle): stance foot slides back on the ground, swing foot arcs forward; the
    body dips after each contact and rises before the next; arms swing against the legs."""
    P = base_pose()
    hx = P["hip"][0]
    ph = i / n

    def foot(p):
        if p < 0.5:                                         # stance: front -> back, flat on the ground
            x = hx + stride - 2 * stride * (p / 0.5)
            return (x, 56.0), (-12.0 if p < 0.06 else (24.0 if p > 0.4 else 0.0))
        q = (p - 0.5) / 0.5                                 # swing: back -> front, lifted
        x = hx - stride + 2 * stride * q
        return (x, 56.0 - lift * math.sin(math.pi * q)), (30.0 * math.sin(math.pi * q) if q < 0.8 else -8.0)
    P["ft_f"], P["pitch_f"] = foot(ph)
    P["ft_b"], P["pitch_b"] = foot((ph + 0.5) % 1.0)
    bob = [0, 1, 0, -1, 0, 1, 0, -1][i * 8 // n]
    shift(P, UPPER, (0, bob))
    P["head"] = (1, bob)
    s = 4.0 * math.cos(2 * math.pi * ph)                    # >0: the far arm swings forward (near leg is ahead)
    if style == "slash" and not spear:
        P["wang"] = 32.0
    elif style == "smash":
        P["wang"] = -118.0
    P["wang"] += -6.0 * math.cos(2 * math.pi * ph)
    P["wfront"] = style != "smash"
    P["ha_b"] = (P["ha_b"][0] + s, P["ha_b"][1] - abs(s) / 3)
    P["el_b"] = (P["el_b"][0] + s / 2, P["el_b"][1])
    P["ha_f"] = (P["ha_f"][0] - s * 0.6, P["ha_f"][1] - (1 if s < 0 else 0))
    P["sway"] = int(round(math.cos(2 * math.pi * ph)))
    if T.get("weapon") == "yumi":
        P["ha_f"] = (P["ha_f"][0], P["ha_f"][1])
    return P


def run_cycle(T, i, style, spear, n=6):
    """Run: forward lean, long stride with a flight phase, arms pumping high."""
    P = base_pose()
    hx = P["hip"][0] + 2
    ph = i / n
    S = 7.0

    def foot(p):
        if p < 0.38:
            x = hx + S - 2 * S * (p / 0.38)
            return (x, 56.0), (-10.0 if p < 0.06 else 30.0 if p > 0.3 else 0.0)
        q = (p - 0.38) / 0.62
        x = hx - S + 2 * S * q
        return (x, 56.0 - 5.0 * math.sin(math.pi * q) ** 0.8), 40.0 * math.sin(math.pi * q)
    P["ft_f"], P["pitch_f"] = foot(ph)
    P["ft_b"], P["pitch_b"] = foot((ph + 0.5) % 1.0)
    bob = [1, 0, -1, 1, 0, -1][i]
    shift(P, UPPER, (2, bob))
    P["head"] = (3, bob)
    s = 4.5 * math.cos(2 * math.pi * ph)
    P["ha_b"] = (P["ha_b"][0] + 2 + s, P["ha_b"][1] - 3 - abs(s) / 2)
    P["ha_f"] = (P["ha_f"][0] + 1 - s * 0.7, P["ha_f"][1] - 2)
    if style == "slash" and not spear:
        P["wang"] = 150.0                                   # the blade trails low behind (wakigamae run)
    elif style == "smash":
        P["wang"] = -125.0
    else:
        P["wang"] = -20.0 if spear or T.get("weapon") in ("bo", "shakujo") else P["wang"]
    P["wfront"] = style != "smash"
    P["sway"] = 2 if i % 3 == 0 else 1
    return P


def victory_pose(T, i, fam, style, spear):
    """Victory: two flourish frames, then a held pose that breathes (frames 2-3 loop as 'victory')."""
    P = base_pose()
    v = T.get("victory")
    w = T["weapon"]
    br = 1 if i == 3 else 0
    if v == "count" or v == "glasses" or v == "laugh" or v == "gunbai" or v == "hat_tip" or v == "curtain":
        _social(T, P, open_hand=False)
    if v == "count":                                        # Haruki counts on his fingers (one, two, three!)
        _key(P, dict(hf=(38, 32 - (1 if i >= 2 else 0)), fingers=min(i + 1, 3), hd=(0, -br),
                     ex="grin" if i >= 2 else "think"))
        P["fist"] = True
        return P
    if v == "glasses":                                      # Gendo pushes his spectacles up his nose
        seq = [dict(hf=(36, 33)), dict(hf=(35, 29), ex="calm"), dict(hf=(36, 39), ex="smug"),
               dict(hf=(36, 39), ex="smug", hd=(0, -1))]
        _key(P, seq[i])
        P["fist"] = True
        return P
    if v == "laugh":                                        # Tamotsu: a belly laugh, hand on the belly
        _key(P, dict(b=(-1, 0), hd=(-1, -1 if i % 2 == 0 else 0), hf=(34, 40), ex="laugh2" if i % 2 == 0 else "laugh"))
        P["open_hand"] = True
        return P
    if v == "gunbai":                                       # Shizue raises the war fan: the field is won
        seq = [dict(hf=(36, 34)), dict(hf=(37, 25), hd=(0, -1)), dict(hf=(42, 30), ex="grin"),
               dict(hf=(42, 30), ex="grin", hd=(0, -1))]
        _key(P, seq[i])
        P["hand_prop"] = "gunbai"
        return P
    if v == "hat_tip":                                      # Sayo touches the brim of her hat and smiles
        seq = [dict(hf=(37, 33)), dict(hf=(36, 26), ex="calm"), dict(hf=(36, 26), ex="grin"),
               dict(hf=(36, 27), ex="grin", hd=(0, -1))]
        _key(P, seq[i])
        P["fist"] = True
        return P
    if v == "curtain":                                      # Mitsue the actress: a curtain-call bow
        if i == 0:
            _key(P, dict(hf=(43, 32), ex="smug"))
        elif i == 1:
            shift(P, ("sh_b", "el_b", "sh_f", "el_f"), (2, 1))
            P["head"] = (4, 3)
            _key(P, dict(hf=(34, 36), ex="calm"))
        else:
            _key(P, dict(hf=(35, 40), ex="smug", hd=(0, -br)))
            P["open_hand"] = True
        return P
    # by weapon
    if fam == "blade":                                      # chiburi (flick the blade clean), then noto
        if i == 0:
            _key(P, dict(b=(1, 0), ff=2, hf=(42, 39), w=52.0, sm="h", smear_r=0.7))
        elif i == 1:
            _key(P, dict(hf=(36, 37), hb=(29, 41), w=-170.0))
        else:
            _key(P, dict(hf=(34, 40), hb=(29, 41), sh=True, ex="calm" if i == 2 else "grin", hd=(0, -br)))
        return P
    if fam == "pole" or fam == "club":                      # a twirl, then planted upright
        if i == 0:
            _key(P, dict(hf=(36, 32), w=-150.0 if fam == "pole" else -130.0, g2=False))
        elif i == 1:
            _key(P, dict(hf=(38, 33), w=-30.0, g2=False, sm="v", smear_r=1.1))
        else:
            if fam == "club":
                _key(P, dict(hf=(34, 32), hb=(22, 22), w=-140.0, ex="grin", hd=(0, -br)))
            else:
                _key(P, dict(hf=(37, 31), w=-90.0, ex="grin", hd=(0, -br)))
        return P
    if fam == "bow":
        _key(P, dict(hf=(36, 36) if i else (39, 32), hb=(22, 26 - br) if i >= 2 else (25, 36),
                     ex="grin" if i >= 2 else None))
        return P
    if fam == "short":                                      # a flip of the knife, then hand on hip
        if i == 0:
            _key(P, dict(hf=(38, 28), ex="smug"))
        else:
            _key(P, dict(hf=(36, 37), hb=(26, 41), ex="smug", hd=(0, -br)))
        return P
    if fam == "gun":
        _key(P, dict(hf=(35, 33), w=-95.0, ex="smug", hd=(0, -br)))
        return P
    # unarmed: fist pump
    _key(P, dict(hf=(37, 20 if i else 26), hd=(0, -br), ex="grin", fist=True))
    return P


# ------------------------------------------------------------------------------------------- body parts
# ------------------------------------------------------------------------------------------- per-character body
def build_pose(T, P):
    """Per-character body on top of the shared pose: height (px), width (px), age posture."""
    P = dict(P)
    h = T.get("height", 0) - (2 if T.get("age") == "old" else 0)
    w = T.get("wide", 0) + (2 if T["build"] in ("round", "strongman") else 3 if T["build"] == "sumai" else 0)
    if T.get("female") and T["build"] not in ("heavy", "armored"):
        w -= 1                                                    # narrower shoulders / waist
    for k in ("sh_b", "el_b", "ha_b", "sh_f", "el_f", "ha_f", "hip"):
        P[k] = (P[k][0], P[k][1] - h)
    for k in ("kn_b", "kn_f"):
        P[k] = (P[k][0], P[k][1] - h // 2)
    P["head"] = (P["head"][0] + (1 if T.get("age") == "old" else 0), P["head"][1] - h)
    if P["glow"] is not None:
        P["glow"] = (P["glow"][0], P["glow"][1] - h)
    for k, s in (("sh_b", -1), ("el_b", -1), ("sh_f", 1), ("el_f", 1)):
        P[k] = (P[k][0] + s * w * 0.6, P[k][1])
    if T["build"] == "sumai":                              # profile: the shoulder sits mid-depth, the chest and
        P["sh_f"] = (P["sh_f"][0] - 4.0, P["sh_f"][1])     # belly bulge out in front of the arm
    P["wide"] = w
    return P


# Stature (2026-11-07, user's reference roster: "these are how i was hoping my units would turn out"): adult, not chibi
# proportions. Every body joint is stretched upward about the soles (STATURE) and outward about the body's centre line
# (BREADTH, which also widens stances and lunges); limbs and weapons get longer to match, and the head is drawn
# smaller (HEAD_SCALE). Applied once per frame after build_pose, so every pose, build and view gets it.
STATURE = 1.26
BREADTH = 1.08
WEAPON_SCALE = 1.12
SOLE_Y = 56 + CY                                   # the feet's ground line (frame coords)
BODY_X = 28 + CX                                   # the body's centre line (frame coords)
STAT_KEYS = ("sh_b", "el_b", "ha_b", "sh_f", "el_f", "ha_f", "hip", "kn_b", "kn_f", "ft_b", "ft_f", "glow")


BUILD_STAT = {"strongman": (1.15, 1.12), "sumai": (1.10, 1.22), "heavy": (1.20, 1.12), "round": (1.18, 1.10)}


def stat_of(T):
    """(stature, breadth) for this character: the build's default, or the spec's own."""
    S, B = BUILD_STAT.get(T.get("build"), (STATURE, BREADTH))
    return T.get("stature", S), T.get("breadth", B)


def stat_pt(p, S=STATURE, B=BREADTH):
    return (BODY_X + (p[0] - BODY_X) * B, SOLE_Y - (SOLE_Y - p[1]) * S)


def stature(T, P):
    P = dict(P)
    if P.get("_stat"):
        return P
    S, B = stat_of(T)
    nb = ((P["sh_b"][0] + P["sh_f"][0]) / 2, (P["sh_b"][1] + P["sh_f"][1]) / 2)
    for k in STAT_KEYS:
        if P.get(k) is not None:
            P[k] = stat_pt(P[k], S, B)
    P["hip"] = (int(round(P["hip"][0])), int(round(P["hip"][1])))   # parts index pixel rows off the hip
    na =((P["sh_b"][0] + P["sh_f"][0]) / 2, (P["sh_b"][1] + P["sh_f"][1]) / 2)
    P["head"] = (P["head"][0] + int(round(na[0] - nb[0])), P["head"][1] + int(round(na[1] - nb[1])))
    if P.get("glow") is not None:
        P["glow"] = (P["glow"][0], max(4.0, P["glow"][1]))
    P["_stat"] = True
    return P


def pattern_mask(kind):
    if kind == "waves":       # seigaiha-like arcs
        ph = (XX + 3 * ((YY // 4) % 2)) % 6
        return ((YY % 4 == 0) & (ph >= 1) & (ph <= 3)) | ((YY % 4 == 1) & ((ph == 0) | (ph == 4)))
    if kind == "diamonds":
        return ((XX + YY) % 6 == 0) | ((XX - YY) % 6 == 0)
    if kind == "stripes":
        return XX % 4 == 0
    if kind == "dots":
        return (XX % 4 == 1) & (YY % 4 == 1)
    if kind == "checks":
        return ((XX // 3 + YY // 3) % 2 == 0)
    if kind == "flames":
        return ((XX * 2 + YY) % 7 == 0) & (YY % 2 == 0)
    return np.zeros((FH, FW), bool)


def paste_cloth(cv, m, tones, pal, T, R, key):
    cv.paste(m, tones, pal)
    pat = T.get("pattern")
    if pat and key in T.get("pattern_on", ("haori",) if T.get("haori") else ("top",)):
        pm = m & pattern_mask(pat) & ~edges(m) & (tones >= 1)
        ys, xs = np.nonzero(pm)
        PP = R["pattern"]
        for y, x in zip(ys, xs):
            cv.col[y, x, :3] = PP[min(int(tones[y, x]) + 1, 4)]


def lames(m, tones, step=2):
    """Armour plates: horizontal lame lines + laced columns. Returns (tones, lace_mask)."""
    inner = m & ~edges(m)
    tones[inner & (YY % step == 0) & (tones >= 1)] = 1
    return tones, inner & (YY % step == 1) & (XX % 3 == 0)


def paste_armor(cv, m, R, T, lit=0.68, shd=0.32):
    t = shade_rows(m, lit=lit, shd=shd)
    t, lm = lames(m, t)
    cv.paste(m, t, R["armor"])
    ys, xs = np.nonzero(lm)
    for y, x in zip(ys, xs):
        cv.col[y, x, :3] = R["lace"][2 if t[y, x] >= 2 else 1]


def draw_limb(cv, a, b, r1, r2, pal, outline=True):
    m, t, side = m_capsule(a, b, r1, r2)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (-dy, dx)
    L = math.hypot(*n) or 1
    facing = (n[0] * 0.8 - n[1] * 0.6) / L       # >0 -> positive side faces the light
    sgn = 1 if facing >= 0 else -1
    tones = shade_axis(m, side * sgn, max(r1, r2), outline)
    cv.paste(m, tones, pal)
    return m, tones


def tattoo(cv, m, R):
    tm = m & ~edges(m) & ((((XX * 3 + YY * 2) % 7) < 2) | ((XX + YY * 3) % 9 == 0))
    ys, xs = np.nonzero(tm)
    for y, x in zip(ys, xs):
        cv.col[y, x, :3] = R["tattoo"][1]


def draw_arm(cv, T, P, R, which, hand=True):
    sh, el, ha = P["sh_" + which], P["el_" + which], P["ha_" + which]
    build = T["build"]
    mid = ((el[0] + ha[0]) / 2, (el[1] + ha[1]) / 2)
    if build == "strongman":                               # bare muscular arms: deltoid, biceps, forearm
        strong_arm(cv, T, sh, el, ha, R, back=which == "b")
    elif build == "sumai":                                 # a wrestler's bare arms: deltoid, biceps, thick forearm
        sumai_arm(cv, T, sh, el, ha, R, back=which == "b", side=True)
    elif build == "monk":                                  # bare tattooed arms
        for a, b, r1, r2 in ((sh, el, 2.0, 1.8), (el, ha, 1.7, 1.4)):
            m, _ = draw_limb(cv, a, b, r1, r2, R["skin"])
            if T.get("tattoo"):
                tattoo(cv, m, R)
    elif build == "heavy":                                 # kote (armoured sleeves)
        draw_limb(cv, sh, el, 2.4, 2.4, R["dark"])
        draw_limb(cv, el, ha, 2.2, 1.8, R["dark"])
        m = m_capsule(mid, ha, 1.6)[0]
        cv.paste(m, shade_rows(m), R["armor"])
    else:
        sleeve = R["haori"] if T.get("haori") else R["top"]
        key = "haori" if T.get("haori") else "top"
        m, t = draw_limb(cv, sh, el, 2.6, 3.2, sleeve)
        paste_cloth(cv, m, t, sleeve, T, R, key)
        if which == "b":
            bag = m_poly([(sh[0] - 2, sh[1] + 1), (el[0] - 2, el[1] - 1), (mid[0] - 1, mid[1] + 3),
                          (el[0] - 3, el[1] + 4), (sh[0] - 3, sh[1] + 4)])
            if bag.any():
                paste_cloth(cv, bag, shade_rows(bag), sleeve, T, R, key)
        m, t = draw_limb(cv, el, mid, 3.0, 2.6, sleeve)
        paste_cloth(cv, m, t, sleeve, T, R, key)
        if T.get("trim") == "fur":
            cuff = m_capsule(mid, (mid[0] + (ha[0] - el[0]) * 0.12, mid[1] + (ha[1] - el[1]) * 0.12), 2.8)[0]
            cv.paste(cuff, shade_rows(cuff, dither=False), R["fur"])
        else:
            cuff = m_capsule(mid, (mid[0] + (ha[0] - el[0]) * 0.08, mid[1] + (ha[1] - el[1]) * 0.08), 2.3)[0]
            cv.paste(cuff, shade_rows(cuff, outline=False), R["lining"])                # sleeve lining
        draw_limb(cv, mid, ha, 1.3, 1.3, R["skin"])
    if hand:
        hm = m_ellipse(ha[0] + 0.5, ha[1] + 0.5, 1.9, 1.9)
        cv.paste(hm, shade_rows(hm), R["dark"] if build == "heavy" else R["skin"])
    if build == "heavy" or (build == "armored" and which == "f"):
        # sode: big laced shoulder plate hanging over the upper arm
        w = 3.8 if build == "heavy" else 3.0
        hgt = 8 if build == "heavy" else 6
        sd = m_poly([(sh[0] - w, sh[1] - 2), (sh[0] + w, sh[1] - 2), (sh[0] + w + 1, sh[1] + hgt),
                     (sh[0] - w + 1, sh[1] + hgt)])
        paste_armor(cv, sd, R, T)


# ------------------------------------------------------------------------------------------- leg rig (side views)
# East/west frames: thigh + shin of fixed length (longer for tall characters) solved by IK from the hip joint to the
# ankle; knees fold forward. If a stance puts a foot out of reach, the whole body crouches (hips drop) instead of the
# foot leaving the ground. Feet are shaped (heel, instep, toe) and pitched per pose (heel strike, toe push-off,
# toe-down swing).
LEG_BASE = 13.6                                   # thigh + shin at height 0 (hip joint -> ankle)
ANKLE_UP = 2.4                                    # ankle above the sole


def leg_lengths(T):
    tot = LEG_BASE + T.get("height", 0) - (2 if T.get("age") == "old" else 0)
    S = stat_of(T)[0]
    tot = tot * S + (ANKLE_UP + 1) * (S - 1)                 # the stretched hip-to-ankle span (see stature)
    return tot * 0.5, tot * 0.5


def hip_joint(P, back, wide):
    hx, hy = P["hip"]
    return (hx + (-1.6 - wide * 0.4 if back else 1.6 + wide * 0.4), hy + 1)


def leg_ik(hip, ankle, lt, ls):
    """Knee by two-bone IK; knees fold forward (hip->ankle direction turned 90 deg counter-clockwise, east-facing)."""
    dx, dy = ankle[0] - hip[0], ankle[1] - hip[1]
    d = math.hypot(dx, dy) or 1e-6
    dd = min(max(d, abs(lt - ls) + 1.0), lt + ls - 0.02)
    ux, uy = dx / d, dy / d
    a = (lt * lt - ls * ls + dd * dd) / (2 * dd)
    h = math.sqrt(max(lt * lt - a * a, 0.0))
    mx, my = hip[0] + ux * a, hip[1] + uy * a
    return (mx + uy * h, my - ux * h)


def rig_legs(T, P):
    """Crouch so both feet reach the ground, then solve the knees."""
    P = dict(P)
    if P.get("kneel"):
        return P
    lt, ls = leg_lengths(T)
    reach = lt + ls - 0.3
    wide = P.get("wide", 0)
    drop = 0.0
    for ft, back in (("ft_b", True), ("ft_f", False)):
        hp = hip_joint(P, back, wide)
        ax, ay = P[ft][0], P[ft][1] - ANKLE_UP
        dx = ax - hp[0]
        if abs(dx) > reach - 1.0:                          # too far even crouched: pull the foot in
            ax = hp[0] + math.copysign(reach - 1.0, dx)
            P[ft] = (ax, P[ft][1])
            dx = ax - hp[0]
        need = ay - math.sqrt(max(reach * reach - dx * dx, 0.0))
        drop = max(drop, need - hp[1])
    drop = int(math.ceil(drop - 0.25))                     # whole pixels: the head is placed on the pixel grid
    if drop > 0:
        shift(P, UPPER, (0, drop))
        P["head"] = (P["head"][0], P["head"][1] + drop)
        if P["glow"] is not None:
            P["glow"] = (P["glow"][0], P["glow"][1] + drop)
    for ft, kn, back in (("ft_b", "kn_b", True), ("ft_f", "kn_f", False)):
        hp = hip_joint(P, back, wide)
        P[kn] = leg_ik(hp, (P[ft][0], P[ft][1] - ANKLE_UP), lt, ls)
    return P


def rot(pt, c, ang):
    a = math.radians(ang)
    x, y = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def draw_foot_side(cv, f, R, pitch=0.0, kind="tabi", dark=False):
    """East-facing foot: heel, sole, toe, instep. pitch > 0 tips the toe down (swing / push-off), < 0 lifts it
    (heel strike). kind: tabi (split-toe sock on a waraji sandal), bare (peasant: skin on a straw sandal), boot."""
    x, y = f[0], f[1] + 0.5
    ank = (x, y - ANKLE_UP)
    shape = [(x - 1.5, y - 1.1), (x - 1.3, y), (x + 2.9, y), (x + 3.5, y - 0.8), (x + 2.7, y - 1.6),
             (x + 0.9, y - 2.2), (x - 0.4, y - 2.9), (x - 1.4, y - 2.2)]
    shape = [rot(pt, ank, pitch) for pt in shape]
    m = m_poly(shape)
    pal = R["skin"] if kind == "bare" else R["dark"] if kind == "boot" else R["tabi"]
    t = shade_rows(m)
    t[m & (t >= 3) & (YY + 0.5 > y - 1.0)] = 2             # the sole side is in shadow
    if dark:
        t[m & (t >= 2)] -= 1
    cv.paste(m, t, pal)
    if kind == "tabi":                                     # the split between big toe and the rest
        tx, ty = rot((x + 2.4, y - 1.3), ank, pitch)
        cv.px_on(tx, ty, pal[1])
    sole = m_capsule(rot((x - 1.4, y + 0.2), ank, pitch), rot((x + 3.3, y + 0.2), ank, pitch), 0.6)[0] & ~m
    sp = R["straw"] if kind == "bare" else R["sandal"]
    if kind != "boot":
        cv.paste(sole, np.zeros((FH, FW), int) + 1, sp)
        for k in (0.3, 1.8):                               # straw thongs over the instep
            sx, sy = rot((x + k, y - 1.6 + k * 0.2), ank, pitch)
            cv.px_on(sx, sy, sp[0])


def leg_poly(top, knee, ankle, w0, w1, w2):
    """A trouser/hakama leg through the knee: half-widths at hip, knee and hem (normals mitred at the knee)."""
    def nrm(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        return -dy / L, dx / L
    n1, n2 = nrm(top, knee), nrm(knee, ankle)
    nk = ((n1[0] + n2[0]) * 0.5, (n1[1] + n2[1]) * 0.5)
    L = math.hypot(*nk) or 1
    nk = (nk[0] / L, nk[1] / L)
    pts = [(top[0] + n1[0] * w0, top[1] + n1[1] * w0), (knee[0] + nk[0] * w1, knee[1] + nk[1] * w1),
           (ankle[0] + n2[0] * w2, ankle[1] + n2[1] * w2), (ankle[0] - n2[0] * w2, ankle[1] - n2[1] * w2),
           (knee[0] - nk[0] * w1, knee[1] - nk[1] * w1), (top[0] - n1[0] * w0, top[1] - n1[1] * w0)]
    return m_poly(pts), n2


def leg_layer(T, P, R, base, back):
    """One side-view leg on its own layer (so the near leg can be outlined where it crosses the far one)."""
    lay = Canvas()
    build, wide = T["build"], P.get("wide", 0)
    kn, ft = ("kn_b", "ft_b") if back else ("kn_f", "ft_f")
    top = hip_joint(P, back, wide)
    k, f = P[kn], P[ft]
    pitch = P["pitch_b" if back else "pitch_f"]
    ank = (f[0], f[1] - ANKLE_UP)
    if build == "strongman":                               # muscular bare legs
        strong_leg(lay, T, top, k, ank, R, back)
        draw_foot_side(lay, f, R, pitch, "bare", dark=back)
    elif build == "sumai":                                 # massive thighs, heavy calves, bare to the foot
        sumai_leg(lay, top, k, ank, R, back)
        draw_foot_side(lay, f, R, pitch, "bare", dark=back)
    elif build == "peasant":                               # bare legs, shin wraps, straw sandals
        draw_limb(lay, top, k, 2.3, 2.0, R["skin"])
        draw_limb(lay, k, ank, 1.9, 1.6, R["skin"])
        wr = m_capsule((k[0] + (ank[0] - k[0]) * 0.3, k[1] + (ank[1] - k[1]) * 0.3), ank, 2.1)[0]
        t = shade_rows(wr)
        t[wr & ((XX + YY) % 3 == 0) & (t >= 2)] = 1        # diagonal wrapping
        lay.paste(wr, t, R["lower"])
        draw_foot_side(lay, f, R, pitch, "bare", dark=back)
    else:
        w0, w1, w2 = 3.0 + wide * 0.4, 3.3 + wide * 0.4, 4.2 + wide * 0.4
        hem = (ank[0] + (ank[0] - k[0]) * 0.02, ank[1] + 0.6)
        leg, n2 = leg_poly(top, k, hem, w0, w1, w2)
        tones = shade_rows(leg)
        if back:
            tones[(tones >= 2) & leg] -= 1
        for off in (-1.6, 1.2):                            # pleats follow the shin, opening toward the hem
            a = (k[0] + n2[0] * off * 0.6, k[1] + n2[1] * off * 0.6)
            b = (hem[0] + n2[0] * off * 1.3, hem[1] + n2[1] * off * 1.3 - 0.8)
            pl = m_capsule(a, b, 0.45)[0] & leg & ~edges(leg)
            tones[pl & (tones >= 2)] = 1
        hb = leg & (np.hypot(XX + 0.5 - hem[0], YY + 0.5 - hem[1]) < w2 + 0.5) & (YY + 0.5 >= hem[1] - 0.6)
        tones[hb & (tones >= 1)] = np.maximum(tones[hb & (tones >= 1)] - 1, 0)   # the hem's lower fold
        paste_cloth(lay, leg, tones, R["lower"], T, R, "lower")
        if build in ("heavy", "armored", "armored_light"):  # suneate along the shin, laced plates
            sg = m_capsule((k[0] + (ank[0] - k[0]) * 0.25, k[1] + (ank[1] - k[1]) * 0.25),
                           (ank[0] - n2[0] * 0.3, ank[1] - n2[1] * 0.3 - 0.4), 1.9)[0]
            t = shade_rows(sg)
            t[sg & ((YY % 2) == 0) & ~edges(sg) & (t >= 2)] = 1
            lay.paste(sg, t, R["armor"] if build != "armored_light" else R["dark"])
            kp = m_ellipse(k[0] + 0.5, k[1] + 0.5, 1.6, 1.4)      # knee cop
            lay.paste(kp, shade_rows(kp), R["armor"] if build == "heavy" else R["dark"])
        draw_foot_side(lay, f, R, pitch, "boot" if build in ("heavy", "armored", "armored_light") else "tabi",
                       dark=back)                          # armour: dark kogake foot covers over the tabi
    a = lay.col[..., 3] > 0
    if not back:                                           # contact line where the near leg crosses the far one
        touch = edges(a) & (base[..., 3] > 0) & ~edge_dir(a)[0]
        lay.col[touch, :3] = (lay.col[touch, :3].astype(int) * 0.55).astype(np.uint8)
    return lay.col


def draw_legs(cv, T, P, R):
    hip = P["hip"]
    build = T["build"]
    if build in ("robe", "monk"):
        x0, y0 = hip
        fb, ff = P["ft_b"], P["ft_f"]
        kf = P["kn_f"]
        for f, back in ((fb, True), (ff, False)):          # feet first: the robe falls over the ankles
            draw_foot_side(cv, f, R, P["pitch_b" if back else "pitch_f"], "tabi", dark=back)
        front = max(ff[0], x0 + 3) + 5
        robe = m_poly([(x0 - 6, y0 - 1), (x0 + 6, y0 - 1), (max(kf[0] + 3.5, x0 + 6.5), kf[1]),
                       (front, GROUND - 3), (min(fb[0], x0 - 3) - 5, GROUND - 3)])
        t = shade_rows(robe)
        for px in range(int(x0 - 8), int(x0 + 9), 4):          # long folds
            t[robe & (XX == px) & (YY > y0 + 4) & (t >= 2)] = 1
        kfold = m_capsule((kf[0] + 1.5, kf[1] + 1), (front - 2, GROUND - 4), 0.5)[0] & robe & ~edges(robe)
        t[kfold & (t >= 2)] = 1                                # the stride pulls a fold from the knee
        paste_cloth(cv, robe, t, R["lower"], T, R, "lower")
        hem = robe & (YY >= GROUND - 6)
        cv.paste(hem, shade_rows(hem), R["accent"])
        hem_line = robe & (YY == GROUND - 7)
        cv.paste(hem_line, np.zeros((FH, FW), int) + 1, R["accent"])
        return
    over(cv.col, leg_layer(T, P, R, cv.col, True))
    over(cv.col, leg_layer(T, P, R, cv.col, False))


def draw_foot_fb(cv, x, y, R, kind="tabi", lifted=False, back=False):
    """Front/back-view foot. Front: a rounded toe cap (tabi split line) on a sandal sole. Back: the heel; a lifted
    foot seen from behind shows its sandal sole."""
    x, y = float(x), float(y)
    pal = R["skin"] if kind == "bare" else R["dark"] if kind == "boot" else R["tabi"]
    sp = R["straw"] if kind == "bare" else R["sandal"]
    if back and lifted and kind != "boot":
        sole = m_ellipse(x + 0.5, y - 1.0, 1.9, 1.6)
        t = shade_rows(sole)
        cv.paste(sole, t, sp)
        return
    cap = m_ellipse(x + 0.5, y - 1.0, 2.0 - (0.2 if lifted else 0), 1.5)
    t = shade_rows(cap)
    cv.paste(cap, t, pal)
    if kind == "tabi" and not back:
        cv.px_on(x + 0.5, y - 1.4, pal[1])                   # the big-toe split
    sole = (np.abs(XX + 0.5 - (x + 0.5)) <= 2.4) & (YY == int(round(y))) & ~cap
    if kind != "boot" and not lifted:
        cv.paste(sole, np.zeros((FH, FW), int) + 1, sp)
    if kind != "boot" and not back:
        cv.px_on(x + 0.5, y - 2.2, sp[0])                    # thong


def draw_foot(cv, f, R, bare=False):
    x, y = int(round(f[0])), int(round(f[1]))
    m = (XX >= x - 1) & (XX <= x + 2) & (YY >= y - 2) & (YY <= y - 1)
    cv.paste(m, shade_rows(m), R["skin"] if bare else R["tabi"])
    s = (XX >= x - 2) & (XX <= x + 3) & (YY == y)
    cv.paste(s, np.zeros((FH, FW), int) + 1, R["straw"] if bare else R["sandal"])
    cv.px(x + 1, y - 2, R["sandal"][0])                 # thong strap


MON = {  # tiny clan mon shapes (pixel offsets)
    "crab": ((-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)),
    "crane": ((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 0)),
    "dragon": ((-1, -1), (0, -1), (0, 0), (0, 1), (1, 1)),
    "lion": ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)),
    "phoenix": ((0, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (1, 1)),
    "scorpion": ((-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1)),
    "unicorn": ((-1, 1), (0, 0), (1, -1), (1, 1)),
    "imperial": ((0, -1), (-1, 0), (1, 0), (0, 1), (0, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)),
    "mantis": ((0, -1), (0, 0), (-1, 1), (1, 1)),
}


def draw_mon(cv, x, y, R, T=None):
    """Clan mon in a colour that contrasts with the garment under it."""
    clan = (T or {}).get("mon", (T or {}).get("clan"))
    if clan in ("ronin", "eta", "peasant", "none"):
        return
    shape = MON.get(clan, ((0, -1), (1, 0), (0, 1), (-1, 0)))
    under = cv.col[int(y), int(x), :3].astype(int).mean() if 0 <= y < FH and 0 <= x < FW else 100
    col = R["accent"][1] if under > 170 else R["collar"][3]
    for dx, dy in shape:
        cv.px_on(x + dx, y + dy, col)


def draw_mawashi(cv, body, hip, wide, R, side=True, back=False):
    """The sumai wrestler's belt: a thick band at the hips (lower colour), the knot at the back, sagari cords
    hanging at the front."""
    hx, hy = hip
    band = body & (YY >= hy - 1) & (YY <= hy + 3)                                 # wraps the body, under the belly
    if not side:                                           # the front / back panel between the legs
        band |= m_poly([(hx - 3.5, hy + 2), (hx + 4.5, hy + 2), (hx + 2.5, hy + 7), (hx - 1.5, hy + 7)])
    t = shade_rows(band)
    t[band & (YY == hy) & ~edges(band) & (t >= 2)] = 1                            # the folded edge
    cv.paste(band, t, R["lower"])
    if band.any() and (back or side):                      # the knot over the spine
        xs = np.nonzero(band.any(0))[0]
        kx = xs.min() + 1 if side else hx
        kn = m_ellipse(kx + 0.5, hy + 0.5, 1.6, 2.0)
        cv.paste(kn, shade_rows(kn), R["lower"])
    if not back:                                           # sagari: stiff cords hanging over the front
        x0 = hx + (5 + wide if side else -3)
        for i in range(4 if side else 6):
            x = x0 + i * (1 if side else 1.2)
            for y in range(hy + 3, hy + 9):
                cv.px(x, y, R["lower"][1 if (y + i) % 2 else 2])


def sumai_arm(cv, T, sh, el, ha, R, back=False, side=False):
    """A wrestler's arm, sculpted: a round deltoid, a thick upper arm, a forearm almost as thick, and (optional) a
    cord tied round the upper arm (T["armband"]). Side view: a little slimmer, and fully outlined so the arm reads
    in front of the belly instead of merging with it."""
    k = 0.85 if side else 1.0
    m, t = sculpt([hf_ellipse(sh[0] + 0.5, sh[1] + 1.0, 4.0 * k, 4.2 * k, 1.1),
                   hf_capsule(sh, el, 3.6 * k, 3.2 * k),
                   hf_ellipse((sh[0] + el[0]) / 2 + 0.5, (sh[1] + el[1]) / 2 + 0.5, 3.6 * k, 3.4 * k, 1.0),
                   hf_capsule(el, ha, 3.3 * k, 2.5 * k)], groups=[0, 1, 1, 2])
    if side:
        t[edges(m)] = 0
    if back:
        t[m & (t >= 2)] -= 1
    cv.paste(m, t, R["skin"])
    if T.get("armband"):
        bx, by = sh[0] + (el[0] - sh[0]) * 0.55, sh[1] + (el[1] - sh[1]) * 0.55
        dx, dy = el[0] - sh[0], el[1] - sh[1]
        L = math.hypot(dx, dy) or 1
        along = ((XX + 0.5 - bx) * dx + (YY + 0.5 - by) * dy) / L
        near = m_capsule(sh, el, 4.2)[0]
        bm = m & near & (np.abs(along) < 1.1) & ~edges(m)
        for y, x in zip(*np.nonzero(bm)):
            cv.col[y, x, :3] = R["band"][max(1, min(3, int(t[y, x])))]


def sumai_leg(cv, top, k, ank, R, back):
    """A wrestler's side-view leg: a massive thigh with the quadriceps bulging forward, a heavy calf behind the shin."""
    qx, qy = top[0] + (k[0] - top[0]) * 0.5 + 1.2, top[1] + (k[1] - top[1]) * 0.5
    cx_, cy_ = k[0] + (ank[0] - k[0]) * 0.3 - 1.0, k[1] + (ank[1] - k[1]) * 0.3
    m, t = sculpt([hf_capsule(top, k, 5.6, 4.0),
                   hf_ellipse(qx + 0.5, qy + 0.5, 4.6, 4.4, 1.05),
                   hf_capsule(k, ank, 3.7, 2.6),
                   hf_ellipse(cx_ + 0.5, cy_ + 0.5, 3.2, 3.6, 1.0)], groups=[0, 0, 1, 1])
    if back:
        t[m & (t >= 3)] -= 1
    cv.paste(m, t, R["skin"])


def sumai_torso_side(cv, T, P, R, top_y, sh_y, front_x, wide):
    """Profile of a sumai wrestler: a broad back, a deep chest with the pectoral overhang, a great round belly pushed
    forward over the mawashi, a heavy seat behind; then the mawashi with its knot and the hanging sagari apron."""
    hx, hy = P["hip"]
    sb, sf = P["sh_b"], P["sh_f"]
    belly = hf_ellipse(hx + 6.5 + wide * 0.4, hy - 4.0, 9.6 + wide * 0.3, 8.2, 1.3)
    prims = [hf_ellipse(sb[0] + 0.5, sh_y + 4.5, 5.6, 7.0, 0.95),                  # upper back
             hf_ellipse(front_x - 0.5, top_y + 2.5, 5.0, 3.4, 0.9),               # trapezius / neck base
             hf_ellipse(sf[0] + 5.5, sh_y + 3.5, 5.6, 4.4, 1.1),                  # pectoral
             belly,
             hf_ellipse(hx - 4.0 - wide * 0.3, hy - 1.0, 5.6, 5.8, 0.95)]          # seat
    poly = m_poly([(sb[0], top_y + 1), (sf[0] + 4, top_y + 1), (sf[0] + 6, sh_y), (hx + 6 + wide, hy + 1),
                   (hx - 6 - wide, hy + 1), (sb[0] - 2, sh_y)])
    prims.append(np.where(poly, 1.2, -1.0))                                       # fills the gaps between them
    m, t = sculpt(prims, groups=[0, 0, 1, 2, 3, 0])
    cv.paste(m, t, R["skin"])
    nav = (int(hx + 13 + wide * 0.6), int(hy - 4))                                # navel on the belly's front
    if 0 <= nav[0] < FW and m[nav[1], nav[0]]:
        cv.px(nav[0], nav[1], R["skin"][1])
    for k in range(3):                                                            # the pec's lower edge
        cv.px_on(sf[0] + 7 + k * 0.5, sh_y + 6, R["skin"][1])
    draw_mawashi_side(cv, T, P, R, belly > 0, wide, m)


def mawashi_pal(T, R):
    return ramp(T.get("mawashi", T["lower"]))


def sagari(cv, x0, x1, y0, y1, pal, fringe=3):
    """The hanging apron of stiffened cords: a panel from y0 to y1 with a cord fringe below."""
    pan = m_poly([(x0, y0), (x1, y0), (x1 - 0.5, y1), (x0 + 0.5, y1)])
    t = shade_rows(pan)
    t[pan & (XX % 2 == 0) & ~edges(pan) & (t >= 2) & (YY > y0 + 1)] -= 1          # the cords' ribbing
    cv.paste(pan, t, pal)
    for x in range(int(round(x0 + 1)), int(round(x1))):
        for y in range(int(y1) + 1, int(y1) + 1 + fringe - (x % 2)):
            cv.px(x, y, pal[1 if (x + y) % 2 else 2])


def draw_mawashi_side(cv, T, P, R, belly, wide, torso):
    hx, hy = P["hip"]
    pal = mawashi_pal(T, R)
    body = torso | ((cv.col[..., 3] > 0) & (YY >= hy + 1) & (XX + 0.5 > hx - 7 - wide) & (XX + 0.5 < hx + 10 + wide))
    tx = np.nonzero(torso[max(0, hy - 1):hy + 2].any(0))[0]
    back_x = tx.min() if tx.size else hx - 8
    band = body & (YY >= hy - 1) & (YY <= hy + 4) & (XX >= back_x)                # wraps the hips, nothing behind
    band |= m_poly([(hx - 6 - wide, hy + 2), (hx + 3, hy + 3), (hx + 3, hy + 8), (hx - 1, hy + 8)]) & body
    band &= ~(belly & (YY < hy + 1))                                             # the belly hangs over the belt
    t = shade_rows(band)
    t[band & (YY == hy + 1) & ~edges(band) & (t >= 2)] = 1                        # the folded edge
    cv.paste(band, t, pal)
    kn = m_ellipse(back_x + 1.5, hy + 0.5, 1.6, 2.4)                             # the knot over the spine
    cv.paste(kn, shade_rows(kn), pal)
    bx = np.nonzero((belly & (YY >= hy) & (YY <= hy + 3)).any(0))[0]
    if bx.size:                                                                   # sagari: stiff strips hanging
        f0 = bx.max() - 6                                                         # at the front, under the belly
        for i in range(6):
            x = f0 + i
            if i % 2:
                continue
            for y in range(hy + 3, hy + 9 + (i // 2) % 2):
                cv.px(x, y, pal[0] if y == hy + 8 + (i // 2) % 2 else pal[3 if i < 3 else 2])
                cv.px(x + 1, y, pal[1])


def sumai_torso_fb(cv, T, R, cx, ct, sy, hy, hw, wide, back):
    """Front / back of a sumai wrestler: shoulders, two pecs over a great belly (front) or the broad back, then the
    mawashi: the belt, the sagari apron to the knees (front) or the knot and the strip between the legs (back)."""
    belly = hf_ellipse(cx + 0.5, hy - 4.5, 8.6 + wide * 0.6, 7.8, 1.2)
    prims = [hf_ellipse(cx + 0.5, ct + 2.5, 6.0, 3.2, 0.9),                         # trapezius
             hf_ellipse(cx + 0.5, sy + 6, hw + 1.5, 7.0, 0.95)]                     # ribcage / flanks
    if not back:
        prims += [hf_ellipse(cx - 3.0, sy + 3.8, 4.4, 3.8, 1.1), hf_ellipse(cx + 4.0, sy + 3.8, 4.4, 3.8, 1.1),
                  belly]
    else:
        prims += [hf_ellipse(cx - 3.5, sy + 4.5, 4.8, 6.0, 1.0), hf_ellipse(cx + 4.5, sy + 4.5, 4.8, 6.0, 1.0),
                  hf_ellipse(cx + 0.5, hy - 3, 8.2 + wide * 0.6, 6.5, 1.0)]
    m, t = sculpt(prims, groups=[0, 0, 1, 2, 3])
    if back:                                                                      # the spine's groove
        t[m & (XX == int(cx)) & (YY > sy + 2) & (YY < hy - 2) & (t >= 2)] = 1
    cv.paste(m, t, R["skin"])
    if not back:
        cv.px(cx, hy - 5, R["skin"][1])                                           # navel
    pal = mawashi_pal(T, R)
    body = cv.col[..., 3] > 0
    band = body & (YY >= hy - 1) & (YY <= hy + 3) & (np.abs(XX + 0.5 - cx) < hw + 4)
    if not back:
        band &= ~((belly > 0) & (YY < hy + 1))
    t = shade_rows(band)
    t[band & (YY == hy + 1) & ~edges(band) & (t >= 2)] = 1
    cv.paste(band, t, pal)
    knee_y = hy + (GROUND - hy) * 0.55
    if not back:
        sagari(cv, cx - 4, cx + 5, hy + 3, knee_y, pal)
    else:
        st = m_poly([(cx - 2, hy + 3), (cx + 3, hy + 3), (cx + 1.5, hy + 8), (cx - 0.5, hy + 8)])
        cv.paste(st, shade_rows(st), pal)
        kn = m_ellipse(cx + 0.5, hy + 0.5, 2.6, 2.2)
        cv.paste(kn, shade_rows(kn), pal)


# ------------------------------------------------------------------------------------------- strongman build
# Gonta v3 (2026-11-07, user: "scrap the sumo... big muscular works too, like the example"): a broad, muscular
# wrestler built from the normal rig: a V torso (broad chest and lats, a solid waist), a thick neck, bare arms and legs
# drawn as separate outlined muscle masses (deltoid, upper arm with the biceps, forearm; thigh with the quadriceps,
# calf), banded like the rest of the cast (light from the front), a white mawashi with the sagari strips at the front.
# T["mass"] scales the limb thickness (variants: 0.9 leaner .. 1.15 heavier).
def strong_limb(cv, a, b, r1, r2, pal, bulge=None, dark=False):
    """A bare muscular limb segment: a capsule plus an optional muscle belly (frac along, offset across, radius),
    banded across the limb, with its own outline."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    m, _, side = m_capsule(a, b, r1, r2)
    if bulge:
        f, off, rr = bulge
        nx, ny = -dy / L, dx / L
        m = m | m_ellipse(a[0] + dx * f + nx * off + 0.5, a[1] + dy * f + ny * off + 0.5, rr, rr)
    facing = (-dy * 0.8 - dx * 0.6) / L
    sgn = 1 if facing >= 0 else -1
    tones = shade_axis(m, side * sgn, max(r1, r2))
    if dark:
        tones[m & (tones >= 2)] -= 1
    cv.paste(m, tones, pal)
    return m


def smooth_limb(cv, pts, radii, pal, bulges=(), dark=False):
    """One whole limb as a single tapered shape: capsules along the bones (pts, radii at each joint) plus muscle bellies
    (seg, frac along, offset across, radius), merged into one mask with one outline; each pixel is banded across the
    bone nearest to it, so there are no seams at the joints."""
    best = np.full((FH, FW), np.inf)
    side = np.zeros((FH, FW))
    rad = np.ones((FH, FW))
    mask = np.zeros((FH, FW), bool)
    segs = []
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = max(dx * dx + dy * dy, 1e-6)
        L = math.sqrt(L2)
        t = np.clip(((XX + 0.5 - ax) * dx + (YY + 0.5 - ay) * dy) / L2, 0, 1)
        px, py = ax + dx * t, ay + dy * t
        d = np.hypot(XX + 0.5 - px, YY + 0.5 - py)
        r = radii[i] + (radii[i + 1] - radii[i]) * t
        mask |= d <= r
        facing = (-dy * 0.8 - dx * 0.6) / L
        sg = 1 if facing >= 0 else -1
        across = ((XX + 0.5 - px) * -dy + (YY + 0.5 - py) * dx) / L * sg
        nd = d / np.maximum(r, 0.3)
        sel = nd < best
        best[sel], side[sel], rad[sel] = nd[sel], across[sel], r[sel]
        segs.append((ax, ay, dx, dy, L))
    cores = np.zeros((FH, FW), bool)
    for seg, f, off, rr in bulges:
        ax, ay, dx, dy, L = segs[seg]
        nx, ny = -dy / L, dx / L
        bx_, by_ = ax + dx * f + nx * off + 0.5, ay + dy * f + ny * off + 0.5
        mask |= m_ellipse(bx_, by_, rr, rr)
        cores |= m_ellipse(bx_, by_, rr * 0.62, rr * 0.62)
    tones = np.full((FH, FW), 2, dtype=np.int32)
    tones[mask & (side > rad * 0.30)] = 3
    tones[mask & (side < -rad * 0.25)] = 1
    tones[mask & cores & (side > rad * 0.05)] = 3                          # each muscle belly catches the light
    tones[mask & cores & (side > rad * 0.45)] = 4
    for (jx, jy) in pts[1:-1]:                                             # the elbow / knee crease
        cr = mask & (np.hypot(XX + 0.5 - jx, YY + 0.5 - jy) < 1.6) & (side < 0)
        tones[cr] = 1
    if dark:
        tones[mask & (tones >= 2)] -= 1
    tones = finish_tones(mask, tones, True)
    cv.paste(mask, tones, pal)
    return mask


def strong_arm(cv, T, sh, el, ha, R, back=False):
    k = T.get("mass", 1.0)
    smooth_limb(cv, [sh, el, ha], [3.3 * k, 2.6 * k, 1.9 * k], R["skin"], dark=back,
                bulges=[(0, 0.08, 0.0, 3.4 * k),                 # the deltoid cap
                        (0, 0.5, -1.0 * k, 2.7 * k),             # biceps
                        (1, 0.28, 0.5 * k, 2.6 * k)])            # forearm


def strong_leg(cv, T, top, k, ank, R, back):
    s_ = T.get("mass", 1.0)
    smooth_limb(cv, [top, k, ank], [4.3 * s_, 3.2 * s_, 2.0 * s_], R["skin"], dark=back,
                bulges=[(0, 0.42, -1.2 * s_, 3.6 * s_),          # quadriceps
                        (1, 0.30, 1.1 * s_, 2.8 * s_)])          # calf


def strong_arm_old(cv, T, sh, el, ha, R, back=False):
    k = T.get("mass", 1.0)
    pal = R["skin"]
    strong_limb(cv, el, ha, 2.6 * k, 1.9 * k, pal, bulge=(0.25, 0.0, 2.7 * k), dark=back)            # forearm
    strong_limb(cv, sh, el, 2.9 * k, 2.4 * k, pal, bulge=(0.5, -1.0 * k, 2.6 * k), dark=back)        # upper arm, biceps
    d = m_ellipse(sh[0] + 0.5, sh[1] + 1.2, 3.1 * k, 3.0 * k)                                         # deltoid
    t = shade_rows(d, dither=False)
    if back:
        t[d & (t >= 2)] -= 1
    cv.paste(d, t, pal)


def strong_leg_old(cv, T, top, k, ank, R, back):
    s = T.get("mass", 1.0)
    pal = R["skin"]
    strong_limb(cv, k, ank, 3.1 * s, 2.0 * s, pal, bulge=(0.3, 1.0 * s, 2.6 * s), dark=back)        # calf behind
    strong_limb(cv, top, k, 4.2 * s, 3.2 * s, pal, bulge=(0.45, -1.1 * s, 3.4 * s), dark=back)       # thigh, quads


def mawashi_band(cv, R, T, body, y0, y1):
    pal = mawashi_pal(T, R)
    band = body & (YY >= y0) & (YY <= y1)
    t = shade_rows(band)
    t[band & (YY == y0 + 1) & ~edges(band) & (t >= 2)] = 1                       # the folded top edge
    cv.paste(band, t, pal)
    return band, pal


def sagari_strips(cv, x0, n, y0, length, pal):
    """Stiff cord strips hanging from the belt: 1-px strips with 1-px gaps, a dark tip."""
    for i in range(n):
        x = x0 + i * 2
        ln = length - (i % 2)
        for y in range(int(y0), int(y0) + ln):
            cv.px(x, y, pal[1] if y == int(y0) + ln - 1 else pal[3 if i % 2 == 0 else 2])


def strong_torso_side(cv, T, P, R, top_y, sh_y, wide):
    hx, hy = P["hip"]
    sb, sf = P["sh_b"], P["sh_f"]
    pal = R["skin"]
    w2 = wide * 0.5
    poly = [(sb[0] + 1, top_y + 1), (sf[0] + 1, top_y + 1), (sf[0] + 3, sh_y + 1), (sf[0] + 3.5, sh_y + 5),
            (hx + 5 + w2, hy - 2), (hx + 5 + w2, hy + 1), (hx - 5 - w2, hy + 1), (hx - 6 - w2, hy - 3),
            (sb[0] - 2.5, sh_y + 6), (sb[0] - 2, sh_y + 1)]
    m = m_poly(poly)
    pec = m_ellipse(sf[0] + 2.8, sh_y + 3.6, 4.9, 3.7)                            # the chest pushes forward
    m |= pec
    m |= m_ellipse(sb[0] - 0.5, sh_y + 5.0, 4.4, 5.6)                              # the broad back (lats)
    m |= m_poly([(sb[0] + 1, top_y), (sf[0] + 1, top_y), (sf[0] + 2, sh_y + 1), (sb[0] - 1, sh_y + 1)])   # traps
    t = shade_rows(m, lit=0.62, shd=0.22, dither=False)
    pec_low = pec & ~np.roll(pec, -1, 0) & ~edges(m)                              # the shelf under the pec
    t[pec_low | (np.roll(pec_low, 1, 0) & m & ~edges(m) & (XX > sf[0] - 1))] = 1
    fx = int(round(hx + 3 + w2))
    for yy in (int(sh_y + 9), int(sh_y + 12)):                                   # two ab lines
        t[m & (YY == yy) & (XX >= fx - 1) & (XX <= fx + 1) & ~edges(m)] = 1
    lat = m & (np.abs(XX + 0.5 - (sb[0] + 1.5 + (YY - sh_y) * 0.35)) < 0.6) & (YY > sh_y + 3) & (YY < hy - 3)
    t[lat & ~edges(m)] = 1                                                        # the lat's edge on the back
    cv.paste(m, t, pal)
    # mawashi: a belt round the hips, the knot at the back, the strip between the legs, sagari at the front
    xs = np.nonzero(m[hy - 1:hy + 1].any(0))[0]
    x0, x1 = (xs.min(), xs.max()) if xs.size else (hx - 6, hx + 6)
    body = (cv.col[..., 3] > 0) & (XX >= x0) & (XX <= x1)
    band, mp = mawashi_band(cv, R, T, body, hy - 1, hy + 3)
    kn = m_ellipse(x0 + 1.0, hy + 0.5, 1.6, 2.3)
    cv.paste(kn, shade_rows(kn), mp)
    ap = m_poly([(x1 - 2.5, hy + 3), (x1 + 0.5, hy + 3), (x1 + 0.5, hy + 8), (x1 - 1.5, hy + 8)])   # apron profile
    t = shade_rows(ap, dither=False)
    cv.paste(ap, t, mp)
    for x in range(int(x1 - 1), int(x1 + 1)):
        cv.px(x, hy + 9, mp[1])


def strong_torso_fb(cv, T, R, cx, ct, sy, hy, hw, wide, back):
    pal = R["skin"]
    w2 = wide * 0.5
    tor = m_poly([(cx - 3, ct - 1), (cx + 4, ct - 1), (cx + hw + 1.5, sy + 0.5), (cx + hw + 1, sy + 6),
                  (cx + 5 + w2, hy), (cx - 4 - w2, hy), (cx - hw, sy + 6), (cx - hw - 0.5, sy + 0.5)])   # traps rise to the neck
    t = shade_rows(tor, lit=0.62, shd=0.22, dither=False)
    inner = tor & ~edges(tor)
    if not back:
        for sx_ in (-1, 1):                                                       # pecs: the line under each
            pc = m_ellipse(cx + 0.5 + sx_ * 3.2, sy + 3.8, 3.9, 3.0)
            low = pc & ~np.roll(pc, -1, 0) & inner
            t[low | (np.roll(low, 1, 0) & inner)] = 1                            # the pec shelf (2 px)
        t[inner & (XX == int(cx)) & (YY >= sy + 2) & (YY <= hy - 2)] = 1         # sternum / linea alba
        for yy in (int(sy + 9), int(sy + 12)):                                   # ab rows
            t[inner & (YY == yy) & (np.abs(XX + 0.5 - (cx + 0.5)) <= 3) & (np.abs(XX + 0.5 - (cx + 0.5)) >= 1)] = 1
    else:
        t[inner & (XX == int(cx)) & (YY >= sy + 1) & (YY <= hy - 2)] = 1         # spine
        for sx_ in (-1, 1):                                                       # shoulder blades
            for k_ in range(4):
                x = int(round(cx + sx_ * (2 + k_ * 0.5)))
                y = int(round(sy + 3 + k_))
                if inner[y, x]:
                    t[y, x] = 1
    cv.paste(tor, t, pal)
    body = ((cv.col[..., 3] > 0) | (np.abs(XX + 0.5 - (cx + 0.5)) < hw - 1)) & (np.abs(XX + 0.5 - (cx + 0.5)) < hw + 1)
    band, mp = mawashi_band(cv, R, T, body, hy - 1, hy + 3)
    if not back:
        sagari(cv, cx - 3, cx + 4, hy + 3, hy + 8, mp, fringe=2)                # the sagari apron
    else:
        st = m_poly([(cx - 1.5, hy + 3), (cx + 2.5, hy + 3), (cx + 1.5, hy + 7), (cx - 0.5, hy + 7)])
        cv.paste(st, shade_rows(st), mp)
        kn = m_ellipse(cx + 0.5, hy + 0.5, 2.2, 2.0)
        cv.paste(kn, shade_rows(kn), mp)


def draw_torso(cv, T, P, R):
    hip = P["hip"]
    sb, sf = P["sh_b"], P["sh_f"]
    build = T["build"]
    wide = P.get("wide", 0)
    sh_y = min(sb[1], sf[1])
    top_y = neck_top(P) + 2                                # the collar sits on the neck's base; shoulders slope below
    bottom = hip[1] + (7 if build == "peasant" else 1)
    poly = [(sb[0] + 1, top_y + 1), (sf[0] - 1, top_y + 1), (sf[0] + 1, sh_y), (hip[0] + 6 + wide, bottom),
            (hip[0] - 6 - wide, bottom), (sb[0] - 1, sh_y)]  # sloping shoulders, not a shrug
    m = m_poly(poly)
    if build == "round":
        m |= m_ellipse(hip[0] + 2, hip[1] - 4, 8, 6)
    front_x = (sb[0] + sf[0]) / 2 + 1
    if build == "strongman":                               # bare V torso, the mawashi
        strong_torso_side(cv, T, P, R, top_y, sh_y, wide)
        return
    if build == "sumai":                                   # bare chest and a great belly over the mawashi
        sumai_torso_side(cv, T, P, R, top_y, sh_y, front_x, wide)
        return
    if build == "heavy":                                   # do (cuirass) over everything + long kusazuri
        paste_armor(cv, m, R, T)
        draw_mon(cv, int(front_x + 3), top_y + 5, R, T)
        ob = m & (YY >= hip[1] - 3) & (YY <= hip[1] - 2)
        cv.paste(ob, shade_rows(ob), R["accent"])
        ks = m_poly([(hip[0] - 8 - wide, hip[1]), (hip[0] + 8 + wide, hip[1]), (hip[0] + 10 + wide, hip[1] + 10),
                     (hip[0] - 10 - wide, hip[1] + 10)])
        t = shade_rows(ks)
        t, lm = lames(ks, t)
        for xx in range(hip[0] - 9 - wide, hip[0] + 11 + wide, 5):     # panel gaps
            t[ks & (XX == xx)] = 0
        cv.paste(ks, t, R["armor"])
        ys, xs = np.nonzero(lm)
        for y, x in zip(ys, xs):
            cv.col[y, x, :3] = R["lace"][2]
        return
    t = shade_rows(m)
    paste_cloth(cv, m, t, R["top"], T, R, "top")
    nx, ny = front_x, top_y                                # crossed collar (white under-kimono V)
    for k in range(0, 9):
        cv.px(nx - 2 + k * 0.55, ny + k, R["collar"][2])
        cv.px(nx - 1 + k * 0.55, ny + k, R["collar"][3])
        cv.px(nx + 3 - k * 0.2, ny + k * 0.9, R["collar"][1] if k > 1 else R["collar"][2])
    if build == "peasant":                                 # rope belt
        ob = m & (YY == hip[1] - 1)
        cv.paste(ob, np.zeros((FH, FW), int) + 2, R["straw"])
        cv.px(hip[0] - 6 - wide, hip[1], R["straw"][1])
        cv.px(hip[0] - 7 - wide, hip[1] + 1, R["straw"][1])
    else:                                                  # obi with weave + knot at the back
        ob = m & (YY >= hip[1] - 3) & (YY <= hip[1] - 1)
        t = shade_rows(ob)
        t[ob & (YY == hip[1] - 2) & (XX % 3 == 0) & (t >= 2)] = 3
        cv.paste(ob, t, R["accent"])
        cord = ob & (YY == hip[1] - 2) & ~edges(ob)                                    # obijime cord
        for y, x in zip(*np.nonzero(cord)):
            cv.col[y, x, :3] = R["cord"][2 if x % 2 else 3]
        knot = m_ellipse(hip[0] - 6.5 - wide, hip[1] - 1.5, 1.8, 2.2)
        cv.paste(knot, shade_rows(knot), R["accent"])
    if build == "monk":                                    # kesa sash across the chest
        sash = m & (np.abs((XX - sb[0]) - (YY - top_y) * 0.9) < 1.6)
        cv.paste(sash, shade_rows(sash), R["accent"])
    if T.get("haori"):
        hp = [(sb[0], top_y + 1), (sf[0], top_y + 1), (sf[0] + 2, sh_y), (hip[0] + 8 + wide, hip[1] + 6),
              (hip[0] - 8 - wide, hip[1] + 6), (sb[0] - 2, sh_y)]
        opening = np.abs(XX - (front_x + 1 + (YY - top_y) * 0.25))
        hm = m_poly(hp) & ~((opening < 1.6) & (YY > top_y + 1))
        t = shade_rows(hm)
        t[hm & (YY > hip[1] + 1) & (XX % 4 == 2) & (t >= 2)] = 1                 # hem folds
        paste_cloth(cv, hm, t, R["haori"], T, R, "haori")
        lap = m_poly(hp) & (opening >= 1.6) & (opening < 2.6) & (YY > top_y + 1)
        if T.get("trim") == "fur":
            lap |= m_poly(hp) & (YY >= hip[1] + 5)
            cv.paste(lap, shade_rows(lap, dither=False), R["fur"])
        else:
            cv.paste(lap, np.zeros((FH, FW), int) + 1, R["haori"])
        cv.px(front_x + 1, top_y + 7, R["collar"][3])      # himo cords
        cv.px(front_x + 3, top_y + 7, R["collar"][3])
        draw_mon(cv, int(front_x - 3), top_y + 4, R, T)
    elif build not in ("peasant", "monk"):
        draw_mon(cv, int(front_x + 3), top_y + 4, R, T)
    if build in ("armored", "armored_light"):
        ch = m & (YY >= top_y + 2) & (YY <= hip[1] - 5) & (XX >= sb[0] - 1)
        paste_armor(cv, ch, R, T)
        ks = m_poly([(hip[0] - 7, hip[1]), (hip[0] + 7, hip[1]), (hip[0] + 8, hip[1] + 6), (hip[0] - 8, hip[1] + 6)])
        t = shade_rows(ks)
        t, lm = lames(ks, t)
        for xx in range(hip[0] - 6, hip[0] + 8, 4):
            t[ks & (XX == xx)] = 0
        cv.paste(ks, t, R["armor"])
        ys, xs = np.nonzero(lm)
        for y, x in zip(ys, xs):
            cv.col[y, x, :3] = R["lace"][2]
    if T.get("cloak"):                                     # travelling mantle over the shoulders
        cp = m_poly([(sb[0] - 4, top_y), (sf[0] + 3, top_y), (sf[0] + 5, hip[1] - 2), (hip[0] + 1, hip[1] + 1),
                     (sb[0] - 6, hip[1] - 1)])
        t = shade_rows(cp)
        t[cp & (XX % 3 == 0) & (YY > top_y + 3) & (t >= 2)] = 1
        cv.paste(cp, t, R["cloak"])


# ------------------------------------------------------------------------------------------- head
def head_origin(P):
    # face/hair canvas top-left (24x30 design grid) relative to the neck
    return 13 + CX + P["head"][0], 8 + CY + P["head"][1]


FACE_ROWS = {8: (8, 18), 9: (7, 20), 10: (7, 21), 11: (7, 22), 12: (7, 22), 13: (7, 22), 14: (7, 23),
             15: (7, 22), 16: (8, 21), 17: (9, 20), 18: (10, 19), 19: (12, 17)}


def _shape(**over):
    d = dict(FACE_ROWS)
    for k, v in over.items():
        r = int(k[1:])
        if v is None:
            d.pop(r, None)
        else:
            d[r] = v
    return d


FACE_SHAPES = {
    "normal": FACE_ROWS,
    "round": _shape(r16=(8, 22), r17=(8, 21), r18=(9, 20), r19=(11, 18)),
    "square": _shape(r16=(8, 22), r17=(8, 21), r18=(9, 21), r19=(10, 20), r20=(12, 19)),
    "long": _shape(r17=(9, 20), r18=(10, 19), r19=(11, 18), r20=(13, 17)),
    "sharp": _shape(r16=(8, 21), r17=(10, 20), r18=(12, 19), r19=(14, 17)),
}


def face_mask(ox, oy, rows=FACE_ROWS):
    m = np.zeros((FH, FW), bool)
    for r, (a, b) in rows.items():
        y = oy + r
        if 0 <= y < FH:
            m[y, max(0, ox + a):min(FW, ox + b + 1)] = True
    return m


def draw_face(cv, T, P, R):
    ox, oy = head_origin(P)
    mo = ox + (2 if PROFILE else 0)                           # mouths sit nearer the face's front edge in profile
    rows = FACE_SHAPES[T.get("face", "normal")]
    m = face_mask(ox, oy, rows)
    tones = np.full((FH, FW), 2, int)
    for r, (a, b) in rows.items():
        y = oy + r
        if not (0 <= y < FH):
            continue
        for c in range(a, b + 1):
            x = ox + c
            if (c <= a + 1 and r >= 12) or r >= max(rows) - 1:
                tones[y, x] = 1
            elif c >= b - 1 and r <= 13:
                tones[y, x] = 3
    tones = finish_tones(m, tones, True)
    mask = T.get("mask")
    skin = R["skin"]
    if mask in ("porcelain", "death", "reed", "noh", "stitched"):   # painted / worn full-face masks
        skin = R["mask_" + mask]
    cv.paste(m, tones, skin)
    if mask == "reed":                                    # eye holes + woven texture
        holes = ((16, 12), (17, 12), (18, 12), (16, 13), (17, 13), (18, 13)) if PROFILE else \
            ((12, 12), (13, 12), (14, 12), (12, 13), (13, 13), (14, 13), (19, 12), (20, 12), (19, 13))
        for p in [(ox + a, oy + b) for a, b in holes]:
            cv.px(*p, R["dark"][0])
        wv = m & ~edges(m) & (((XX + YY) % 3 == 0) | ((XX - YY) % 4 == 0))
        for y, x in zip(*np.nonzero(wv)):
            cv.col[y, x, :3] = skin[1]
    if mask == "stitched":                                # crude stitches across the face
        for xs_ in (13, 17, 21):
            for yy in range(oy + 9, oy + 19, 1):
                if (yy + xs_) % 2 == 0:
                    cv.px_on(ox + xs_, yy, R["dark"][0])
        for xx in range(ox + 9, ox + 23):
            if xx % 2 == 0:
                cv.px_on(xx, oy + 15, R["dark"][1])
    if not kit_ok(T, P):
        cv.px(ox + 23, oy + 15, skin[1])                      # nose shadow
        K, W = FIXED["eyek"], FIXED["white"]
        er = R["eye"]
        ex, ey = ox + 12, oy + 12
        fx, fy = ox + 19, oy + 12
        if PROFILE:                                           # side view (user): one eye forward, the far one hidden
            ex, fx, fy = ox + 16, -99, -99                    # (pixels off the canvas are clipped)
        eyes = T.get("eyes", "normal")
        expr = P.get("expr")
        if expr == "pain" and eyes != "glow" and mask != "porcelain":
            eyes = "pain"
        elif expr == "focus" and eyes not in ("glow",) and mask != "porcelain":
            eyes = "shut"
        if mask == "death":                                   # dark painted sockets
            for dx in range(-1, 5):
                for dy in range(-1, 4):
                    cv.px_on(ex + dx, ey + dy, R["dark"][1])
            for dx in range(-1, 3):
                for dy in range(-1, 3):
                    cv.px_on(fx + dx, fy + dy, R["dark"][1])
        if (mask == "porcelain" and not T.get("mask_plain")) or eyes == "glow":   # glowing red eyes in the mask
            G = FIXED["glowred"]
            for p in ((ex + 1, ey + 1), (ex + 2, ey + 1), (ex + 2, ey + 2), (fx, fy + 1), (fx + 1, fy + 1)):
                cv.px(*p, G)
            cv.px(ex + 1, ey + 2, (255, 210, 180))
            for c in range(4):
                cv.px(ex + c, ey, R["dark"][0])
        elif eyes == "pain":                                  # squeezed shut  > <
            for p in ((ex, ey), (ex + 1, ey + 1), (ex + 2, ey + 1), (ex + 3, ey + 2), (ex, ey + 2),
                      (fx + 1, fy), (fx, fy + 1), (fx + 1, fy + 2)):
                cv.px(*p, K)
        elif eyes == "shut":                                  # calm closed lids (casting)
            for c in range(4):
                cv.px(ex + c, ey + 2, K)
            cv.px(ex + 4, ey + 1, K), cv.px(fx, fy + 2, K), cv.px(fx + 1, fy + 2, K)
        elif eyes == "closed":                                # cheerful ^ ^
            for p in ((ex, ey + 2), (ex + 1, ey + 1), (ex + 2, ey + 1), (ex + 3, ey + 2), (fx, fy + 1), (fx + 1, fy + 2)):
                cv.px(*p, K)
        elif eyes in ("narrow", "old"):
            for c in range(-1, 4):
                cv.px(ex + c, ey + 1, K)
            cv.px(ex + 1, ey + 2, er[1]), cv.px(ex + 2, ey + 2, er[2]), cv.px(ex + 3, ey + 2, W)
            cv.px(fx, fy + 1, K), cv.px(fx + 1, fy + 1, K), cv.px(fx, fy + 2, er[2])
            if eyes == "old":
                cv.px_on(ex + 4, ey + 3, skin[1]), cv.px_on(ex + 3, ey + 4, skin[1])
                cv.px_on(ox + 17, oy + 16, skin[1]), cv.px_on(ox + 16, oy + 15, skin[1])
                cv.px_on(ox + 10, oy + 11, skin[1])
        elif mask == "reed":                                  # eyes hidden behind the reed mask
            pass
        else:                                                 # big Octopath eyes
            for c in range(4):
                cv.px(ex + c, ey, K)
            cv.px(ex, ey + 1, K)
            cv.px(ex + 1, ey + 1, er[1]), cv.px(ex + 2, ey + 1, er[1]), cv.px(ex + 3, ey + 1, W)
            cv.px(ex + 1, ey + 2, er[2]), cv.px(ex + 2, ey + 2, er[3]), cv.px(ex + 3, ey + 2, er[2])
            cv.px(ex + 2, ey + 3, er[4])
            if T.get("female"):
                cv.px(ex - 1, ey, K), cv.px(ex + 4, ey - 1, K)
            cv.px(fx, fy, K), cv.px(fx + 1, fy, K)
            cv.px(fx, fy + 1, er[1]), cv.px(fx + 1, fy + 1, W)
            cv.px(fx, fy + 2, er[3])
        if mask not in ("porcelain", "reed", "noh"):          # brows
            bc = R["hair"][1]
            brow = T.get("brow", "normal")
            for c in range(-1, 3):
                dy = -2 if brow != "stern" else (-1 if c >= 1 else -2)
                cv.px(ex + c + 1, ey + dy, bc)
            cv.px(fx, fy - 2, bc), cv.px(fx + 1, fy - 2 if brow != "stern" else fy - 1, bc)
            if brow == "thick":
                for c in range(0, 4):
                    cv.px(ex + c, ey - 3, bc)
        if T.get("scar"):
            for k in range(4):
                cv.px_on(ox + 15 + k, oy + 10 + k, FIXED["scar"])
        if T.get("female") and not mask:
            cv.px(ox + 13, oy + 16, FIXED["blush"]), cv.px(ox + 14, oy + 16, FIXED["blush"])
        if T.get("blushm"):                                   # drunk flush across nose and cheeks
            for p in ((13, 15), (14, 15), (13, 16), (14, 16), (21, 15), (22, 15), (22, 14)):
                cv.px_on(ox + p[0], oy + p[1], (230, 110, 100))
        if not mask or mask in ("death",):
            mouth = T.get("mouth", "normal")
            if expr == "pain":
                mouth = "open"
            elif expr == "grin" and mouth == "normal":
                mouth = "grin"
            if mouth == "open":
                cv.px(mo + 18, oy + 17, FIXED["eyek"]), cv.px(mo + 19, oy + 17, FIXED["eyek"])
                cv.px(mo + 18, oy + 18, FIXED["mouth"]), cv.px(mo + 19, oy + 18, FIXED["mouth"])
                mouth = "done"
            if mouth == "toothless":
                cv.px(mo + 18, oy + 17, FIXED["eyek"]), cv.px(mo + 19, oy + 17, FIXED["eyek"])
                cv.px(mo + 20, oy + 17, FIXED["mouth"])
            elif mouth == "grin":
                cv.px(mo + 17, oy + 17, FIXED["mouth"]), cv.px(mo + 18, oy + 17, W), cv.px(mo + 19, oy + 17, W)
                cv.px(mo + 20, oy + 17, FIXED["mouth"])
            elif mouth == "done":
                pass
            elif mouth == "frown":
                cv.px(mo + 18, oy + 18, FIXED["mouth"]), cv.px(mo + 19, oy + 17, FIXED["mouth"])
                cv.px(mo + 20, oy + 18, FIXED["mouth"])
            else:
                cv.px(mo + 19, oy + 17, FIXED["mouth"])
                if not T.get("female"):
                    cv.px(mo + 18, oy + 17, skin[1])
        if mask == "porcelain":                               # hairline crack + mouth slit
            cv.px_on(ox + 17, oy + 9, skin[1]), cv.px_on(ox + 16, oy + 10, skin[1]), cv.px_on(ox + 16, oy + 11, skin[1])
            cv.px_on(mo + 18, oy + 17, skin[0]), cv.px_on(mo + 19, oy + 17, skin[0]), cv.px_on(mo + 20, oy + 17, skin[0])
        if mask == "noh":                                     # high painted brows + tiny red lips
            for bx in ((16, 17) if PROFILE else (13, 14, 20)):
                cv.px(ox + bx, oy + 9, R["dark"][1])
            cv.px(mo + 19, oy + 17, (200, 40, 50)), cv.px(mo + 18, oy + 17, (150, 30, 40))
        if T.get("glasses"):
            g = FIXED["glass"]
            for c in range(-1, 5):
                cv.px_on(ex + c, ey - 1, g), cv.px_on(ex + c, ey + 4, g)
            for c in (1, 2, 3):
                cv.px_on(ex - 1, ey + c, g), cv.px_on(ex + 4, ey + c, g)
            for c in range(5, 8):
                cv.px_on(ex + c, ey, g)
            cv.px_on(fx - 1, fy - 1, g), cv.px_on(fx - 1, fy + 2, g), cv.px_on(fx + 2, fy + 2, g)
            cv.px_on(ex + 3, ey + 1, FIXED["glint"]), cv.px_on(ex + 2, ey + 2, FIXED["glint"])
    if mask in (True, "cloth"):
        mk = m & (YY >= oy + 16) & (XX >= ox + 11)
        t = shade_rows(mk)
        t[mk & (YY == oy + 16) & ~edges(mk)] = 3                                 # folded top edge
        cv.paste(mk, t, R["mask"])
    elif mask == "mempo":                                 # iron face guard under the eyes
        mk = m & (YY >= oy + 14)
        t = shade_rows(mk)
        t[mk & (YY == oy + 17) & (XX >= ox + 15)] = 0     # mouth grille
        t[mk & (YY == oy + 18) & (XX % 2 == 0) & (XX >= ox + 15)] = 3
        cv.paste(mk, t, R["mempo"])
    facial = T.get("facial")
    hc = R["facial"]
    if facial in ("beard", "longbeard"):
        bd = np.zeros((FH, FW), bool)
        for r, (a, b) in rows.items():
            if r >= 16:
                y = oy + r + 1
                if 0 <= y < FH:
                    bd[y, ox + a:ox + b + 1] = True
        drop = 23 if facial == "beard" else 28
        bd |= m_poly([(ox + 12, oy + 17), (ox + 22, oy + 17), (ox + 19, oy + drop), (ox + 14, oy + drop - 1)])
        bd &= ~((XX >= ox + 18) & (XX <= ox + 20) & (YY == oy + 18))
        t = shade_rows(bd)
        t[bd & ((XX + YY) % 3 == 0) & (t >= 2)] = 1                       # beard strands
        cv.paste(bd, t, hc)
        cv.px(ox + 19, oy + 18, FIXED["mouth"])
    if facial in ("mustache", "beard", "longbeard", "goatee_mustache"):
        for c in range(16, 22):
            cv.px(ox + c, oy + 16, hc[2])
        cv.px(ox + 16, oy + 17, hc[1]), cv.px(ox + 21, oy + 17, hc[1])
        cv.px(ox + 15, oy + 18, hc[1])
    if facial in ("goatee", "goatee_mustache"):
        for c in range(17, 20):
            cv.px(ox + c, oy + 19, hc[2]), cv.px(ox + c, oy + 20, hc[1])
    if facial == "stubble":
        for p in ((15, 17), (17, 18), (19, 19), (21, 17), (14, 16), (16, 19)):
            cv.px_on(ox + p[0], oy + p[1], skin[1])


BANGS = {
    "normal": [(11, 13), (14.5, 12), (18, 13), (21, 12.5), (23, 14)],
    "side": [(10, 12), (13, 12.5), (16, 13), (19, 14), (22, 15)],
    "center": [(12, 12), (15, 13.5), (17.5, 14), (20, 13.5), (23, 12)],
    "short": [(12, 11), (15.5, 11), (19, 11.5), (22, 11)],
    "swept": [(9.5, 11), (12.5, 12), (15.5, 13), (18.5, 14), (21.5, 15), (24, 15.5)],
    "parted": [(11, 13.5), (13.5, 12.5), (19.5, 12.5), (22, 13.5), (24, 14.5)],
    "heavy": [(10.5, 14), (13.5, 14.5), (16.5, 14), (19.5, 14.5), (22.5, 14)],
    "messy": [(10, 12.5), (13, 14), (15.5, 11.5), (18.5, 14.5), (21, 12), (23.5, 15)],
    "none": [],
}
GAPS = {"parted": (16.5,), "heavy": (15, 18), "messy": (14.3, 20)}
TUFTS = {"short": 4, "ponytail": 3, "long": 2, "long_topknot": 2, "bob": 3, "spiky": 0, "mane": 0, "bun": 1,
         "chonmage": 0, "bald": 0, "beard": 4, "sumotop": 2}


def add_tufts(mask, cx, cy, n, size=1.7, a0=165, a1=300, seed=0):
    """Small pointed clumps breaking the smooth outline across the back and top of the head."""
    if n <= 0:
        return mask
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5 + 0.25 * math.sin(seed + k * 2.3)) / n)
        bx, by = cx + 11.0 * math.cos(a), cy - 1 + 10.0 * math.sin(a)
        tx, ty = bx + size * 1.7 * math.cos(a - 0.35), by + size * 1.7 * math.sin(a - 0.35)
        nx, ny = -math.sin(a), math.cos(a)
        mask = mask | m_poly([(bx - nx * size, by - ny * size), (bx + nx * size, by + ny * size), (tx, ty)])
    return mask


def zigzag_hem(mask, every=3, depth=2):
    """Split the bottom of hanging hair into pointed tips."""
    out = mask.copy()
    for x in range(FW):
        ys = np.nonzero(mask[:, x])[0]
        if len(ys) < 6 or x % every == 0:
            continue
        bottom = ys.max()
        out[bottom - depth + 1:bottom + 1, x] = False
    return out


def hair_masks(T, P):
    """Returns (back_mask, front_mask, scalp_mask) in frame coords."""
    ox, oy = head_origin(P)
    sw = P["sway"]
    hs = T["hairstyle"]
    cx, cy = ox + 13.0, oy + 10.5
    cap = m_ellipse(cx - 0.5, cy - 1.0, 11.5, 10.5)
    face_zone = np.zeros((FH, FW), bool)
    for r, (a, b) in FACE_ROWS.items():
        y = oy + r
        if 0 <= y < FH:
            face_zone[y, max(0, ox + a + 3):min(FW, ox + b + 1)] = True
    scalp = np.zeros((FH, FW), bool)
    back = np.zeros((FH, FW), bool)
    if hs == "bald":
        scalp = cap & ~(face_zone & (YY >= oy + 9))
        scalp |= m_poly([(ox + 2, oy + 8), (ox + 10, oy + 8), (ox + 10.5, oy + 15), (ox + 8, oy + 19), (ox + 3.5, oy + 18)])
        return back, np.zeros((FH, FW), bool), scalp
    front = cap & ~(face_zone & (YY >= oy + 11))
    front = add_tufts(front, cx, cy, T.get("tufts", TUFTS.get(hs, 2)), seed=len(T["name"]))
    bangs = "none" if hs == "chonmage" else T.get("bangs", "normal")
    if bangs != "none":
        for tx, ty in BANGS[bangs]:
            tx, ty = ox + tx, oy + ty
            front |= m_poly([(tx - 2.6, oy + 9), (tx + 2.0, oy + 9), (tx + 0.7, ty + 1)])
        for gx in GAPS.get(bangs, (13, 16.5, 20)):
            gx += ox
            front &= ~m_poly([(gx - 0.8, oy + 13.5), (gx + 1.2, oy + 13.5), (gx + 0.2, oy + 10.5)])
    else:
        front &= ~(face_zone & (YY >= oy + 9))
    front |= m_poly([(ox + 2, oy + 8), (ox + 10, oy + 8), (ox + 10.5, oy + 15), (ox + 8, oy + 19), (ox + 3.5, oy + 18)])
    if T.get("sidelock") or (T.get("female") and hs in ("ponytail", "short", "bun")):
        front |= m_poly([(ox + 8.5, oy + 10), (ox + 11, oy + 10), (ox + 10.6 + sw * 0.4, oy + 19),
                         (ox + 9.4 + sw * 0.4, oy + 21)])
    if T.get("ahoge"):                                    # cowlick strand on the crown
        front |= m_capsule((cx - 1, cy - 9.5), (cx + 1.5, cy - 13.5), 0.8, 0.6)[0]
        front |= m_capsule((cx + 1.5, cy - 13.5), (cx + 4 + sw * 0.5, cy - 12.5), 0.6, 0.4)[0]
    if hs == "chonmage":                                  # shaved pate (sakayaki) + folded topknot
        inner = m_ellipse(cx - 0.5, cy - 1.0, 10.6, 9.6)
        scalp = inner & (XX >= ox + 11) & (YY < oy + 10) & ~(face_zone & (YY >= oy + 9))
        scalp |= cap & (XX >= ox + 13) & (YY < oy + 9) & ~(face_zone & (YY >= oy + 9))
        front &= ~scalp
        front |= m_capsule((ox + 9, oy + 1.5), (ox + 16, oy - 0.2), 1.3, 1.0)[0]
        front |= m_ellipse(ox + 8.5, oy + 2.0, 1.9, 1.7)
    elif hs == "ponytail":
        back |= m_capsule((ox + 3, oy + 5), (ox - 2 + sw, oy + 24), 3.6, 1.6)[0]
        back |= m_capsule((ox - 2 + sw, oy + 24), (ox + sw, oy + 29), 1.6, 0.6)[0]
        back |= m_capsule((ox + 2, oy + 7), (ox - 4 + sw, oy + 19), 1.4, 0.5)[0]       # loose strand
    elif hs in ("long", "long_topknot"):
        back |= m_poly([(ox + 2, oy + 8), (ox + 12, oy + 10), (ox + 12 + sw, oy + 31), (ox + 6 + sw, oy + 33),
                        (ox + sw, oy + 30)])
        back = zigzag_hem(back)
        front |= m_poly([(ox + 8, oy + 11), (ox + 11, oy + 11), (ox + 11 + sw * 0.5, oy + 23), (ox + 9 + sw * 0.5, oy + 25)])
        if hs == "long_topknot":
            front |= m_ellipse(ox + 9, oy + 0.5, 3.5, 2.6)
    elif hs == "mane":
        back |= m_poly([(ox - 1, oy + 4), (ox + 13, oy + 8), (ox + 14 + sw, oy + 34), (ox + 9 + sw, oy + 31),
                        (ox + 5 + sw, oy + 36), (ox + 2 + sw, oy + 30), (ox - 3 + sw, oy + 33), (ox - 2, oy + 18)])
        back = zigzag_hem(back, every=2, depth=2)
        for k in range(5):
            a = math.radians(200 + k * 28)
            bx, by = cx + 10 * math.cos(a), cy - 1 + 9.5 * math.sin(a)
            front |= m_poly([(bx - 2, by + 1), (bx + 2, by + 1), (bx + 4.5 * math.cos(a), by + 4.5 * math.sin(a))])
        front |= m_poly([(ox + 8, oy + 11), (ox + 11, oy + 11), (ox + 11 + sw * 0.5, oy + 24), (ox + 8 + sw * 0.5, oy + 26)])
    elif hs == "bun":
        front |= m_ellipse(ox + 4.5, oy + 2.5, 3.8, 3.4)
    elif hs == "sumotop":                                 # a wrestler's full hair, pulled up into a tall top-knot bun
        front |= m_capsule((ox + 10, oy + 3.5), (ox + 10.5, oy - 1.0), 1.8, 1.5)[0]
        front |= m_ellipse(ox + 10.5, oy - 4.5, 4.2, 3.6)
    elif hs == "spiky":
        for k in range(6):
            a = math.radians(195 + k * 23)
            bx, by = cx + 9.5 * math.cos(a), cy - 1 + 9 * math.sin(a)
            ln = 5.2 if k % 2 else 4.2
            front |= m_poly([(bx - 2.2, by + 1.5), (bx + 2.2, by + 1.5),
                             (bx + ln * math.cos(a - 0.3), by + ln * math.sin(a - 0.3))])
    elif hs == "bob":
        bob = m_poly([(ox + 2, oy + 9), (ox + 10, oy + 10), (ox + 11, oy + 21), (ox + 3, oy + 21)])
        front |= zigzag_hem(bob, every=2, depth=1)
        front |= m_poly([(ox + 21.5, oy + 10), (ox + 24.5, oy + 10), (ox + 24, oy + 19), (ox + 22.5, oy + 20)])
    return back, front, scalp


def shade_hair(mask, P, cx, cy, hanging=False):
    """Anime clump shading: strands radiate from the crown, each clump lit on one edge and creased on the other;
    a broken shine band follows the skull; hanging hair falls in slanted vertical strands."""
    tones = np.full((FH, FW), 2, dtype=np.int32)
    tones[mask & (YY < cy - 5)] = 3
    tones[mask & (YY > cy + 3)] = 1
    tones[mask & (XX > cx + 5) & (YY < cy + 2)] += 1                        # light from the upper front
    crx, cry = cx - 1.5, cy - 10.5
    ang = np.degrees(np.arctan2(YY + 0.5 - cry, XX + 0.5 - crx))
    w = 27.0
    phase = ((ang + 7.0) % w) / w
    hang = mask & (YY > cy + 6) & (XX < cx - 3) if not hanging else mask & (YY > cy + 2)
    sp = ((XX + 0.5 + (YY - cy) * 0.14 - P["sway"] * 0.5) % 3.5) / 3.5
    phase = np.where(hang, sp, phase)
    dc = np.hypot(XX + 0.5 - crx, (YY + 0.5 - cry) * 1.1)
    clumpy = mask & ((dc > 7.0) | hang)                                       # smooth crown, clumps toward the ends
    tones[clumpy & (phase < 0.2)] += 1                                        # lit clump edge
    tones[clumpy & (phase > 0.78)] -= 1                                       # shadowed side
    tones[clumpy & (phase > 0.94) & (dc > 9.0)] -= 1                          # crease between clumps
    d = np.hypot(XX + 0.5 - (cx + 1), (YY + 0.5 - (cy + 0.5)) * 1.12)
    band = mask & (d > 6.4) & (d < 8.2) & (YY < cy - 1) & (XX > cx - 9) & ~hang
    tones[band & (phase > 0.05) & (phase < 0.72)] = 4                         # broken shine band
    tones[band & ((phase <= 0.05) | (phase >= 0.72))] = 3
    halo = mask & ((np.abs(d - 5.9) < 0.5) | (np.abs(d - 8.7) < 0.5)) & (YY < cy - 1) & (XX > cx - 7) & ~hang
    tones[halo & (tones < 3)] = 3
    np.clip(tones, 0, 4, out=tones)
    return finish_tones(mask, tones, True)


def draw_hair_back(cv, T, P, R):
    back, _, _ = hair_masks(T, P)
    if back.any():
        ox, oy = head_origin(P)
        t = shade_hair(back, P, ox + 13, oy + 10, hanging=True)
        t[back & (t >= 2)] -= 1                                               # behind the body: a step darker
        cv.paste(back, t, R["hair"])
        if T["hairstyle"] == "ponytail":
            tie = m_ellipse(ox + 3.5, oy + 6.5, 1.8, 1.6)
            cv.paste(tie, shade_rows(tie), R["accent"])
    head = T.get("head")
    if head == "hachimaki":
        ox, oy = head_origin(P)
        sw = P["sway"]
        for end in ((ox - 5 + sw, oy + 11), (ox - 4 + sw, oy + 14)):
            m = m_capsule((ox + 2, oy + 8), end, 1.1, 0.7)[0]
            cv.paste(m, shade_rows(m), R["band"])


def draw_kabuto(cv, T, P, R, ox, oy):
    """Kabuto: riveted ridged bowl with a top ring, projecting visor, laced shikoro lames, turned-back fukigaeshi
    with the mon, crest on a base plate."""
    dome = m_ellipse(ox + 12.5, oy + 8.5, 12.5, 11) & (YY <= oy + 8)
    t = shade_rows(dome, lit=0.62, shd=0.3)
    tx, ty = ox + 11.5, oy - 1.5
    ang = np.degrees(np.arctan2(YY + 0.5 - ty, XX + 0.5 - tx))
    ridge = dome & ~edges(dome) & ((ang % 14.0) < 1.6) & (YY > oy - 1)
    t[ridge & (t >= 1)] = 1
    t[dome & ~edges(dome) & (((ang + 2.2) % 14.0) < 1.0) & (t >= 2) & (YY > oy - 1)] = 3
    cv.paste(dome, t, R["helm"])
    for y, x in zip(*np.nonzero(ridge & ((YY - oy) % 3 == 0))):                 # rivets along the ridges
        cv.col[y, x, :3] = R["metal"][3]
    tehen = m_ellipse(tx + 0.5, ty + 1.5, 1.8, 1.2)
    cv.paste(tehen, shade_rows(tehen), R["crest"])
    shik = m_poly([(ox + 1, oy + 5), (ox + 12, oy + 8), (ox + 13, oy + 14), (ox - 5, oy + 17), (ox - 6, oy + 11)])
    paste_armor(cv, shik, R, T)
    visor = m_poly([(ox + 13, oy + 7.5), (ox + 26, oy + 7.5), (ox + 28, oy + 10), (ox + 14, oy + 10)])
    t = shade_rows(visor, dither=False)
    t[visor & (YY == oy + 7)] = 3
    cv.paste(visor, t, R["helm"])
    fk = m_poly([(ox + 17, oy + 4), (ox + 21.5, oy + 4), (ox + 22, oy + 9), (ox + 18, oy + 10)])
    cv.paste(fk, shade_rows(fk), R["armor"])
    draw_mon(cv, ox + 19, oy + 6, R, T)
    crest = T.get("crest", "horns")
    if crest != "none":
        base = (XX >= ox + 17) & (XX <= ox + 21) & (YY >= oy + 2) & (YY <= oy + 4)
        cv.paste(base, shade_rows(base, dither=False), R["crest"])
    if crest == "horns":                                                      # kuwagata
        for a, b in (((ox + 18, oy + 3), (ox + 13, oy - 6)), ((ox + 21, oy + 3), (ox + 26, oy - 5))):
            line(cv, a, b, R["crest"], 2)
        cv.px(ox + 13, oy - 6, R["crest"][4]), cv.px(ox + 26, oy - 5, R["crest"][4])
    elif crest == "moon":
        mm = m_ellipse(ox + 19.5, oy + 0, 5.0, 3.8) & ~m_ellipse(ox + 19.5, oy - 1.6, 4.2, 3.2)
        cv.paste(mm, shade_rows(mm), R["crest"])
    elif crest == "disc":
        dd = m_ellipse(ox + 19.5, oy + 0.5, 2.8, 2.8)
        t = shade_rows(dd)
        cv.paste(dd, t, R["crest"])
        cv.px(ox + 19, oy + 0, R["accent"][1])


def draw_hair_front(cv, T, P, R):
    _, front, scalp = hair_masks(T, P)
    ox, oy = head_origin(P)
    head = T.get("head")
    helm = head in ("kabuto", "kabuto_full")
    if scalp.any():
        t = shade_rows(scalp, lit=0.62, shd=0.30, dither=False)
        d = np.hypot(XX + 0.5 - (ox + 14), (YY + 0.5 - (oy + 4)))
        t[scalp & (d < 2.2) & (t >= 2)] = 4
        cv.paste(scalp, t, R["skin"])
        cv.px(ox + 9, oy + 13, R["skin"][1]), cv.px(ox + 9, oy + 14, R["skin"][1])
        if T.get("head_tattoo"):
            d1 = np.hypot(XX + 0.5 - (ox + 9), YY + 0.5 - (oy + 6))
            d2 = np.hypot(XX + 0.5 - (ox + 16), YY + 0.5 - (oy + 1))
            tm = scalp & ~edges(scalp) & ((np.abs(d1 - 4.5) < 0.6) | (np.abs(d1 - 7.5) < 0.6) |
                                          (np.abs(d2 - 3.0) < 0.55) | ((XX - ox) + (YY - oy) == 10))
            for y, x in zip(*np.nonzero(tm)):
                cv.col[y, x, :3] = R["tattoo"][1]
    if not helm and front.any():
        cv.paste(front, shade_hair(front, P, ox + 13, oy + 10), R["hair"])
        # bangs cast a soft shadow on the forehead / cheeks just below them
        below = np.zeros((FH, FW), bool)
        below[1:, :] = front[:-1, :]
        sh = below & ~front & face_zone(ox, oy) & (cv.col[..., 3] > 0)
        cv.col[sh, :3] = (cv.col[sh, :3] * 0.8).astype(np.uint8)
        if T["hairstyle"] == "bun":
            line(cv, (ox + 1, oy + 5), (ox + 8, oy), R["accent"], 1)
            cv.px(ox + 1, oy + 5, R["accent"][4])
        if T["hairstyle"] == "sumotop":                   # the red cord round the base of the bun
            for x in range(ox + 8, ox + 13):
                cv.px(x, oy + 0, R["band"][3 if x % 2 else 2])
                cv.px(x, oy + 1, R["band"][1])
    if head == "hachimaki":
        band = (m_ellipse(ox + 12.5, oy + 9.5, 12, 11) & (YY >= oy + 7) & (YY <= oy + 8) & (XX <= ox + 23))
        t = shade_rows(band, dither=False)
        cv.paste(band, t, R["band"])
        cv.px(ox + 19, oy + 7, R["band"][4])
    elif head == "headcloth":
        hcm = m_ellipse(ox + 12.5, oy + 9.0, 12.0, 10.8) & (YY <= oy + 7)
        t = shade_rows(hcm)
        t[hcm & (YY == oy + 7)] = 0
        cv.paste(hcm, t, R["cloth"])
        if T.get("cloth_dots", True):
            for y, x in zip(*np.nonzero(hcm & ~edges(hcm) & ((XX + 2 * (YY % 2)) % 4 == 0) & (YY % 2 == 0))):
                cv.col[y, x, :3] = R["collar"][3]
        sw = P["sway"]
        for end in ((ox - 4 + sw, oy + 7), (ox - 3 + sw, oy + 10)):
            m = m_capsule((ox + 1, oy + 5), end, 1.2, 0.8)[0]
            cv.paste(m, shade_rows(m), R["cloth"])
    elif helm:
        draw_kabuto(cv, T, P, R, ox, oy)
    if T.get("hat") == "jingasa":
        hat = m_poly([(ox - 4, oy + 7), (ox + 30, oy + 7), (ox + 26, oy + 4), (ox + 14, oy - 3), (ox + 2, oy + 4)])
        t = shade_rows(hat, lit=0.62, shd=0.28)
        for xx in range(ox - 2, ox + 30, 3):
            t[hat & (XX == xx) & (t >= 2) & (YY < oy + 6)] = 1
        t[hat & (YY == oy + 7)] = 0
        cv.paste(hat, t, R["hat"])
        cv.px(ox + 14, oy - 3, R["accent"][2])
        if T.get("hat_lacquer"):                          # lacquered jingasa: a gold mon on the crown, a shine line
            draw_mon(cv, ox + 17, oy + 2, R, T)
            for xx in range(ox + 9, ox + 20):
                cv.px_on(xx, oy + 4 - (xx - ox - 9) * 0.25, R["hat"][3])
        line(cv, (ox + 8, oy + 8), (ox + 9, oy + 17), R["straw"], 1, tone=1, hi=False)
    elif T.get("hat") == "kasa":                         # sandogasa: a wide, shallow woven-straw dome
        hat = m_poly([(ox - 8, oy + 8), (ox + 33, oy + 8), (ox + 31, oy + 5), (ox + 24, oy + 0), (ox + 13, oy - 2),
                      (ox + 2, oy + 0), (ox - 5, oy + 5)])
        t = shade_rows(hat, lit=0.60, shd=0.26)
        d = np.hypot(XX + 0.5 - (ox + 12.5), (YY + 0.5 - (oy + 13)) * 1.6)
        weave = hat & ~edges(hat) & ((d.astype(int) % 3) == 0) & (t >= 2)
        t[weave] = 1                                       # concentric weave rings
        t[hat & ~edges(hat) & ((XX + YY) % 5 == 0) & (t >= 2) & (YY < oy + 7)] = 3
        t[hat & (YY == oy + 8)] = 0
        cv.paste(hat, t, R["hat"])
        line(cv, (ox + 9, oy + 9), (ox + 11, oy + 18), R["dark"], 1, tone=1, hi=False)     # chin cord
    elif T.get("hat") == "eboshi":                       # court cap: tall black lacquered gauze, leaning back
        eb = m_poly([(ox + 4, oy + 5), (ox + 19, oy + 5), (ox + 18, oy - 4), (ox + 13, oy - 11), (ox + 7, oy - 12),
                     (ox + 3, oy - 8)])
        t = shade_rows(eb, lit=0.66, shd=0.30)
        t[eb & ~edges(eb) & (np.abs((XX - ox) - 0.55 * (YY - oy) - 13) < 0.7) & (t >= 1)] = 1   # the fold
        t[eb & ~edges(eb) & (YY == oy + 3)] = 3                                                 # the brim band
        cv.paste(eb, t, R["dark"])
        line(cv, (ox + 9, oy + 6), (ox + 11, oy + 18), R["collar"], 1, tone=2, hi=False)   # white chin cord


def face_zone(ox, oy):
    fz = np.zeros((FH, FW), bool)
    for r, (a, b) in FACE_ROWS.items():
        y = oy + r
        if 0 <= y < FH:
            fz[y, max(0, ox + a + 3):min(FW, ox + b + 1)] = True
    return fz


# ------------------------------------------------------------------------------------------- weapons & props
def wdir(P):
    a = math.radians(P["wang"])
    return math.cos(a), math.sin(a)


def line(cv, a, b, pal, width=1, tone=2, hi=True):
    m, t, side = m_capsule(a, b, width * 0.5 + 0.15)
    tones = np.where(side > 0, 3 if hi else tone, tone)
    tones = finish_tones(m, tones, width > 1)
    cv.paste(m, tones, pal)
    return m


def curved_blade(cv, at, dx, dy, k0, k1, pal, width=2, bend=0.25):
    pts = [at(k0 + k) for k in range(0, int(k1 - k0) + 1, 3)]
    for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        c0, c1 = i * bend, (i + 1) * bend
        line(cv, (a[0] + dy * c0, a[1] - dx * c0), (b[0] + dy * c1, b[1] - dx * c1), pal, width)


def forge_blade(cv, at, dx, dy, k0, k1, pal, width=2.2, sori=0.10, tip=2.5):
    """A forged blade from k0 to k1 along the weapon axis: sori (curve toward the back), tapering to a kissaki;
    bright cutting edge, polished face, darker back. Kept out of the silhouette outline pass.
    n = the mune (back) side: (dy, -dx) puts the edge toward the opponent / down and the spine toward the wielder
    in east-facing frames (2026-11-07 user: the blades read as held upside down with (-dy, dx))."""
    nx, ny = dy, -dx
    L = float(k1 - k0)
    top, bot = [], []
    for t in np.linspace(0.0, 1.0, 14):
        k = k0 + L * t
        c = sori * L * t * t
        w = width * (1.0 - 0.3 * t)
        cx, cy = at(k)
        cx, cy = cx + nx * c, cy + ny * c
        top.append((cx + nx * w * 0.5, cy + ny * w * 0.5))
        bot.append((cx - nx * w * 0.5, cy - ny * w * 0.5))
    ex, ey = at(k1 + tip)
    c = sori * L
    point = (ex + nx * (c + width * 0.25), ey + ny * (c + width * 0.25))
    m = m_poly(top + [point] + bot[::-1])
    if not m.any():
        return m
    sx, sy = int(round(nx)), int(round(ny))
    back = m & ~np.roll(np.roll(m, -sy, 0), -sx, 1)                     # the mune (back)
    edge = m & ~np.roll(np.roll(m, sy, 0), sx, 1)                       # the ha (cutting edge)
    tones = np.full((FH, FW), 3, dtype=np.int32)
    tones[back] = 0                                                       # dark mune: reads over pale cloth/hair
    tones[edge] = 4
    tones[~m] = 0
    cv.paste(m, tones, pal)
    cv.keep |= m
    return m


def draw_weapon(cv, T, P, R):
    w = T["weapon"]
    g = P.get("wgrip") or P["ha_f"]                 # wgrip: the weapon rests in the far hand / lies on the floor
    dx, dy = wdir(P)
    at = lambda k: (g[0] + dx * k * WEAPON_SCALE, g[1] + dy * k * WEAPON_SCALE)  # noqa: E731
    if w == "yari":
        line(cv, at(-14), at(21), R["wood"], 2)
        blade = m_poly([at(21), (at(23.5)[0] - dy * 2.2, at(23.5)[1] + dx * 2.2), at(28),
                        (at(23.5)[0] + dy * 2.2, at(23.5)[1] - dx * 2.2)])
        t = shade_rows(blade)
        cv.paste(blade, t, R["metal"])
        cv.keep |= blade
        line(cv, at(22), at(27), R["metal"], 1, tone=4, hi=False)                # ridge
        tas = m_ellipse(at(20)[0] + 0.5, at(20)[1] + 1.5, 1.6, 2.2)
        cv.paste(tas, shade_rows(tas), R["accent"])
        cv.px(*at(-14), R["metal"][1])                                           # ishizuki butt cap
    elif w == "naginata":
        line(cv, at(-16), at(19), R["wood"], 2)
        for k in (-10, -4, 2, 8):                                                # grip wraps
            cv.px(*at(k), R["dark"][1])
        ts = m_ellipse(at(19.5)[0] + 0.5, at(19.5)[1] + 0.5, 1.6, 1.6)
        cv.paste(ts, shade_rows(ts), R["accent"])
        forge_blade(cv, at, dx, dy, 20, 30, R["metal"], width=3.0, sori=0.22, tip=2.0)
    elif w == "tetsubo":                                                         # studded iron-shod club
        line(cv, at(-8), at(4), R["wood"], 2)
        head = m_capsule(at(4), at(20), 2.2, 3.4)[0]
        t = shade_rows(head)
        cv.paste(head, t, R["iron"])
        for k in range(5, 20, 3):                                                # studs + bands
            for s in (-1, 1):
                p = at(k)
                cv.px(p[0] - dy * 2.8 * s, p[1] + dx * 2.8 * s, R["metal"][3])
            cv.px(*at(k + 1), R["metal"][2])
        cv.px(*at(20.5), R["metal"][4])
    elif w == "bokken":                                                          # wooden practice sword
        line(cv, at(-4), at(2), R["dark"], 2, hi=False)
        tsuba = m_ellipse(at(2.4)[0] + 0.5, at(2.4)[1] + 0.5, 1.5, 1.5)
        cv.paste(tsuba, shade_rows(tsuba), R["dark"])
        forge_blade(cv, at, dx, dy, 3, 19, R["wood"], width=2.3, sori=0.07)
    elif w in ("katana", "nodachi"):
        rust = w == "nodachi" and T.get("rusty")
        hl = 6 if w == "nodachi" else 4
        line(cv, at(-hl), at(2), R["dark"], 2, hi=False)
        for k in range(-hl + 1, 2, 2):                                           # tsuka-ito wrap diamonds
            cv.px(*at(k), R["collar"][2])
        tsuba = m_ellipse(at(2.4)[0] + 0.5, at(2.4)[1] + 0.5, 1.7, 1.7)
        cv.paste(tsuba, shade_rows(tsuba), R["accent"])
        forge_blade(cv, at, dx, dy, 3, 28 if w == "nodachi" else 19, R["rust"] if rust else R["metal"],
              width=2.4 if w == "nodachi" else 2.1, sori=0.07)
        hb = m_capsule(at(2.6), at(3.6), 1.2)[0]                                 # habaki (blade collar)
        cv.paste(hb, shade_rows(hb, outline=False), R["accent"])
    elif w == "musket":                                                          # gaijin matchlock (Dragon Ch3)
        line(cv, at(-9), at(3), R["wood"], 3)                                    # the stock
        line(cv, at(3), at(21), R["iron"], 1)                                    # the barrel
        cv.px(*at(21), R["metal"][4])
        cv.px(*at(2), R["accent"][2])                                            # the match cord
    elif w == "bo":
        line(cv, at(-16), at(19), R["wood"], 2)
        for k in (-16, 19):
            c = m_ellipse(at(k)[0] + 0.5, at(k)[1] + 0.5, 1.4, 1.4)
            cv.paste(c, shade_rows(c), R["accent"])
        for k in (-3, 3):
            cv.px(*at(k), R["dark"][1])
    elif w == "shakujo":
        line(cv, at(-15), at(19), R["wood"], 2)
        hx, hy = at(23)
        ring = m_ellipse(hx + 0.5, hy + 0.5, 3.6, 3.6) & ~m_ellipse(hx + 0.5, hy + 0.5, 2.0, 2.0)
        cv.paste(ring, shade_rows(ring), R["metal"])
        for k in (-1, 1):
            r2 = m_ellipse(hx + 0.5 + 3.5 * k, hy + 3.5, 1.2, 1.2) & ~m_ellipse(hx + 0.5 + 3.5 * k, hy + 3.5, 0.5, 0.5)
            cv.paste(r2, shade_rows(r2), R["metal"])
        if T.get("ofuda_staff", True):
            for k in (8, 11):
                px, py = at(k)
                st = (XX >= px + 1) & (XX <= px + 2) & (YY >= py) & (YY <= py + 4)
                cv.paste(st, shade_rows(st, outline=False), R["collar"])
                cv.px(px + 1, py + 2, R["accent"][0])
    elif w == "tanto":                                                           # reverse grip
        line(cv, (g[0], g[1] - 2), (g[0], g[1] + 1), R["dark"], 2, hi=False)
        bl = m_poly([(g[0] - 1, g[1] + 2), (g[0] + 1.6, g[1] + 2), (g[0] + 0.6, g[1] + 9)])
        cv.paste(bl, shade_rows(bl), R["metal"])
        cv.keep |= bl
    elif w == "kama":                                                            # peasant sickle
        line(cv, at(-4), at(8), R["wood"], 2)
        tip = at(8)
        bl = m_capsule(tip, (tip[0] + dy * -5 + dx * 1.5, tip[1] - dx * -5 + dy * 1.5), 1.2, 0.5)[0]
        cv.paste(bl, shade_rows(bl), R["metal"])
    elif w == "nunchaku":                                                        # two sticks on a short chain
        line(cv, at(-1), at(6), R["wood"], 2)
        p = at(6)
        q = (p[0] + dx * 2 - dy * 2.5, p[1] + dy * 2 + dx * 2.5)                  # the chain kinks the second stick
        line(cv, p, q, R["metal"], 1, hi=False)
        line(cv, q, (q[0] + dx * 6.5 - dy * 1.5, q[1] + dy * 6.5 + dx * 1.5), R["wood"], 2)
    elif w == "fan":                                                             # closed folding fan
        line(cv, at(-2), at(6), R["dark"], 2)
        cv.px(*at(6), R["accent"][3]), cv.px(*at(-2), R["accent"][2])
    elif w == "yumi":
        top, bot = (g[0] + 1, g[1] - 19 * WEAPON_SCALE), (g[0] + 1, g[1] + 12 * WEAPON_SCALE)
        pts = []
        tilt = P.get("bow_tilt", 0.0)                  # < 0: the bow leans back (an arcing volley)
        if P.get("wlay") is not None:
            tilt = 90.0                                # laid on the floor
        bend = 4.5 + (1.5 if P["bow"] == "draw" else 0.0)
        for k in range(0, 13):
            t = k / 12
            y = top[1] + (bot[1] - top[1]) * t
            x = g[0] + bend * math.sin(math.pi * (0.08 + 0.84 * t)) - 1
            pts.append(rot((x, y), g, tilt) if tilt else (x, y))
        for a, b in zip(pts[:-1], pts[1:]):
            line(cv, a, b, R["wood"], 2)
        for k in (3, 9):                                                         # rattan bindings
            cv.px(pts[k][0], pts[k][1], R["dark"][1])
        hb = P["ha_b"]
        if P["bow"] in ("draw", "nock"):
            line(cv, pts[0], hb, R["collar"], 1, hi=False)
            line(cv, hb, pts[-1], R["collar"], 1, hi=False)
            ax_, ay_ = g[0] - hb[0], g[1] - hb[1]
            al = math.hypot(ax_, ay_) or 1.0
            ux_, uy_ = ax_ / al, ay_ / al
            tip = (g[0] + ux_ * 7, g[1] + uy_ * 7)
            line(cv, (hb[0] - ux_, hb[1] - uy_), tip, R["wood"], 1, tone=3, hi=False)        # arrow
            cv.px(tip[0] + ux_, tip[1] + uy_, R["metal"][4])
            cv.px(hb[0] - ux_ - uy_, hb[1] - uy_ + ux_, R["collar"][4])                     # fletching
            cv.px(hb[0] - ux_ + uy_, hb[1] - uy_ - ux_, R["collar"][4])
        else:
            line(cv, pts[0], pts[-1], R["collar"], 1, hi=False)
        if P["bow"] == "release":                          # arrow streak leaving the bow
            a = math.radians(P.get("bow_tilt", 0.0))
            ux_, uy_ = math.cos(a), math.sin(a)
            for k in range(6, 80):
                x, yy = int(round(g[0] + ux_ * k)), int(round(g[1] + uy_ * k))
                if 0 <= yy < FH and 0 <= x < FW:
                    cv.col[yy, x] = (255, 252, 230, 255 if k > 20 else 150)
        if P.get("wlay") is None:
            gp = rot((g[0] + 3, g[1]), g, P.get("bow_tilt", 0.0))
            grip = (np.abs(XX - gp[0]) <= 1) & (np.abs(YY - gp[1]) <= 1)
            cv.paste(grip, shade_rows(grip), R["accent"])


# ------------------------------------------------------------------------------------------- arm rig (side views)
# East/west frames: every arm is a 2-bone chain of fixed length, solved by IK toward the pose's hand target (the
# pose's elbow is only a hint for which way the elbow bends). The weapon hangs off the near fist; two-handed weapons
# pull the far fist onto the grip, so the weapon always moves with the arms. Both fists are drawn wrapped around the
# haft, and the near arm gets a contact outline where it crosses the body.
ARM_UP, ARM_FORE = 5.8, 5.6
_ARM_S = STATURE                                   # arm length scale of the character being rigged (rig_arms)
TWO_HAND = {"katana": -3.6, "bokken": -3.6, "nodachi": -5.0, "yari": -9.0, "naginata": -9.0, "bo": -9.0, "tetsubo": -5.5,
            "shakujo": -9.0, "musket": 7.0}


def ik(sh, target, hint, lu=None, lf=None):
    """Two-bone IK: returns (elbow, hand). The hand is clamped to the arm's reach. (hint: kept for callers.)"""
    lu = ARM_UP * _ARM_S if lu is None else lu
    lf = ARM_FORE * _ARM_S if lf is None else lf
    sx, sy = sh
    dx, dy = target[0] - sx, target[1] - sy
    d = math.hypot(dx, dy) or 1e-6
    dd = min(max(d, abs(lu - lf) + 1.5), lu + lf - 0.05)
    ux, uy = dx / d, dy / d
    hand = (sx + ux * dd, sy + uy * dd)
    a = (lu * lu - lf * lf + dd * dd) / (2 * dd)
    h = math.sqrt(max(lu * lu - a * a, 0.0))
    mx, my = sx + ux * a, sy + uy * a
    # anatomical fold (east-facing): the elbow sits on the shoulder->hand direction turned 90 deg clockwise, so a
    # forward reach bends down, a hanging arm bends back, a raised arm bends forward. The pose's elbow is ignored.
    el = (mx - uy * h, my + ux * h)
    return el, hand


def rig_arms(T, P):
    """Solve both arms; for two-handed weapons bring the far hand onto the grip (sliding the weapon back toward the
    body when the far shoulder can't reach)."""
    P = dict(P)
    global _ARM_S
    _ARM_S = stat_of(T)[0]
    want = P["ha_f"]
    P["el_f"], P["ha_f"] = ik(P["sh_f"], want, P["el_f"])
    P["grip_b"] = False
    k = TWO_HAND.get(T["weapon"])
    if k is not None and P.get("grip2") and not P["sheathed"]:
        dx, dy = wdir(P)
        for _ in range(4):
            tgt = (P["ha_f"][0] + dx * k, P["ha_f"][1] + dy * k)
            el, ha = ik(P["sh_b"], tgt, P["el_b"])
            miss = math.hypot(ha[0] - tgt[0], ha[1] - tgt[1])
            if miss <= 0.8:
                P["el_b"], P["ha_b"], P["grip_b"] = el, ha, True
                return P
            sb = P["sh_b"]                                 # slide the near fist (and the weapon) toward the far shoulder
            L = math.hypot(tgt[0] - sb[0], tgt[1] - sb[1]) or 1.0
            want = (P["ha_f"][0] - (tgt[0] - sb[0]) / L * (miss + 0.3),
                    P["ha_f"][1] - (tgt[1] - sb[1]) / L * (miss + 0.3))
            P["el_f"], P["ha_f"] = ik(P["sh_f"], want, P["el_f"])
    P["el_b"], P["ha_b"] = ik(P["sh_b"], P["ha_b"], P["el_b"])
    return P


def grip_axis(T, P):
    if T["weapon"] == "yumi":
        return 0.0, -1.0                                   # the bow stands upright in the fist
    return wdir(P)


def draw_fist(cv, T, P, R, which):
    """A closed fist wrapped around the haft: fingers across the weapon axis, knuckles catching the light."""
    hx, hy = P["ha_" + which]
    dx, dy = grip_axis(T, P)
    nx, ny = -dy, dx
    pal = R["dark"] if T["build"] == "heavy" else R["skin"]
    fist = m_capsule((hx - nx * 1.1, hy - ny * 1.1), (hx + nx * 1.1, hy + ny * 1.1), 1.55)[0]
    cv.paste(fist, shade_rows(fist), pal)
    kx, ky = hx + nx * 0.6 + dx * 0.9, hy + ny * 0.6 + dy * 0.9          # knuckle ridge on the blade side
    cv.px_on(kx, ky, pal[4])
    cv.px_on(hx - nx * 1.2 - dx * 0.6, hy - ny * 1.2 - dy * 0.6, pal[1])   # thumb shadow under the grip


def arm_layer(T, P, R, base, which="f", fist=True, forearm_only=False):
    """Draw an arm on its own layer, outline it where it crosses the body, return the layer. The near arm is lit a
    little (it is closest to the light); the far forearm, reaching across the chest to a two-handed grip, is drawn
    without its upper arm (hidden by the torso) and a little darker so it sits behind the near one."""
    lay = Canvas()
    draw_arm(lay, T, P, R, which, hand=not fist)
    if fist:
        draw_fist(lay, T, P, R, which)
    a = lay.col[..., 3] > 0
    if forearm_only:
        sx, sy = P["sh_" + which]
        ex, ey = P["el_" + which]
        cut = np.hypot(XX + 0.5 - sx, YY + 0.5 - sy) < math.hypot(ex - sx, ey - sy) * 0.8
        lay.col[cut] = 0
        a = lay.col[..., 3] > 0
    body = a & (base[..., 3] > 0)
    c = lay.col[..., :3].astype(int)
    if which == "f":
        c[a] += 10                                         # additive lift: works on dark lacquer and pale silk alike
        up, dn, lf, rt = edge_dir(a)
        rim = (up | rt) & ~(dn | lf)                       # light from the upper right: a rim along the lit edges
        c[rim] += 34
    else:
        c[a] = (c[a] * 0.82).astype(int)
    touch = edges(a) & body & ~(edge_dir(a)[0] | edge_dir(a)[3] if which == "f" else np.zeros_like(a))
    c[touch] = (c[touch] * 0.5).astype(int)
    lay.col[..., :3] = np.clip(c, 0, 255).astype(np.uint8)
    if which == "f" and T["build"] in ("sumai", "strongman"):           # bare arm on bare belly: cast a 1-px shadow round it
        p = np.pad(a, 1)
        grow = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
        ring = grow & ~a & (base[..., 3] > 0)
        lay.col[ring, :3] = (base[ring, :3].astype(int) * 0.62).astype(np.uint8)
        lay.col[ring, 3] = 255
    return lay.col


def props(T):
    p = T.get("props") or ([T["prop"]] if T.get("prop") else [])
    return p


def draw_sashimono(cv, T, P, R, view="side"):
    """The soldier's back banner (T["sashimono"] = flag colour, or True for the clan / top colour): a pole up the
    spine, a crossbar, and a tall flag above the head with the mon. view: side | front | back."""
    col = T["sashimono"] if isinstance(T.get("sashimono"), (tuple, list)) else T.get("banner_col", T["top"])
    if sum(col) / 3 < 110:                                 # dark clan colours: lift them so the flag reads as cloth
        col = tuple(int(c + (255 - c) * 0.3) for c in col)
    fp = ramp(tuple(col))
    ax, ay = head_anchor(P)
    top = max(1, int(round(ay - 23)))                      # the flag's top edge, well above the head
    fh = 13
    sw = P.get("sway", 0)
    if view == "side":
        hip, sb = P["hip"], P["sh_b"]
        px_ = sb[0] - 3.5
        line(cv, (px_, hip[1] - 1), (px_ - 0.5, top - 1), R["dark"], 1, hi=False)
        x1, x0 = px_ - 1, px_ - 8
        flag = m_poly([(x0 - sw * 0.5, top), (x1, top), (x1, top + fh), (x0 - sw, top + fh - 1)])
    else:                                                  # front / back: the pole up one shoulder blade, the flag
        cx = P["hip"][0]                                   # beside the head with a gap above it (not a tall hat)
        side_ = 1 if view == "front" else -1
        pole = cx + side_ * 4.5
        top = max(1, top - 3)
        fh = 11
        line(cv, (pole, P["hip"][1] - 2), (pole, top), R["dark"], 1, hi=False)
        x0, x1 = (pole + 0.5, pole + 7.5) if side_ > 0 else (pole - 7.5, pole - 0.5)
        flag = m_poly([(x0, top), (x1, top), (x1 + sw * 0.5, top + fh), (x0 + sw * 0.5, top + fh)])
    t = shade_rows(flag, dither=False)
    t[flag & (YY == top + fh - 1) & (t >= 2)] -= 1                     # the hem
    cv.paste(flag, t, fp)
    if view == "side":
        line(cv, (x0 - 0.5, top - 0.5), (px_ + 0.5, top - 0.5), R["dark"], 1, hi=False)   # the crossbar
    ys, xs = np.nonzero(flag)
    if xs.size:
        mx, my = int(round(xs.mean())), int(round(top + fh * 0.42))
        clan = T.get("mon", T.get("clan"))
        shape = MON.get(clan, ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)))
        lum = sum(col) / 3
        mc = (36, 30, 36) if lum > 150 else (240, 236, 222)
        ring = m_ellipse(mx + 0.5, my + 0.5, 2.9, 2.9) & ~m_ellipse(mx + 0.5, my + 0.5, 2.0, 2.0) & flag
        for y, x in zip(*np.nonzero(ring)):
            cv.col[y, x, :3] = mc
        for dx, dy in shape:
            cv.px_on(mx + dx, my + dy, mc)
    cv.keep |= flag


def draw_prop_back(cv, T, P, R):
    hip, sb = P["hip"], P["sh_b"]
    for p in props(T):
        if p == "mapcase":
            line(cv, (sb[0] - 5, sb[1] - 4), (hip[0] + 4, hip[1] + 2), R["wood"], 4)
            cap = m_ellipse(sb[0] - 4.5, sb[1] - 3.5, 2.2, 2.2)
            cv.paste(cap, shade_rows(cap), R["accent"])
            for k in (0.35, 0.7):
                x = sb[0] - 5 + (hip[0] + 9 - sb[0]) * k
                y = sb[1] - 4 + (hip[1] + 6 - sb[1]) * k
                cv.px(x, y, R["dark"][1])
        elif p == "quiver":
            line(cv, (sb[0] - 4, sb[1] - 3), (hip[0] - 5, hip[1] + 3), R["wood"], 4)
            for k in range(3):
                cv.px(sb[0] - 5 + k, sb[1] - 6 - k % 2, R["collar"][3])
                cv.px(sb[0] - 5 + k, sb[1] - 5, R["accent"][2])
        elif p == "basket":
            b = m_poly([(sb[0] - 9, sb[1] - 1), (sb[0] - 1, sb[1] - 1), (sb[0] - 2, hip[1] - 1), (sb[0] - 8, hip[1] - 1)])
            t = shade_rows(b)
            for yy in range(int(sb[1]), int(hip[1]), 2):
                t[b & (YY == yy) & (t >= 2)] = 1
            t[b & (XX % 3 == 0) & (t >= 2)] = 3
            cv.paste(b, t, R["straw"])
            for k in range(3):
                cv.px(sb[0] - 7 + k * 2, sb[1] - 2, R["accent"][2 + k % 2])
                cv.px(sb[0] - 6 + k * 2, sb[1] - 3, (196, 70, 60))
        elif p == "swordsback":                           # two hilts over the shoulder, under the cloak
            for off in (0, 3):
                line(cv, (sb[0] - 2 + off, sb[1] - 9), (sb[0] + 1 + off, sb[1] + 2), R["dark"], 2, hi=False)
                cv.px(sb[0] - 1 + off, sb[1] - 4, R["accent"][3])
        elif p == "nodachi_back":
            line(cv, (sb[0] - 6, sb[1] - 8), (hip[0] + 8, hip[1] + 6), R["dark"], 2, hi=True)


def draw_prop_front(cv, T, P, R):
    hip = P["hip"]
    for p in props(T):
        if p in ("saya", "daisho"):
            line(cv, (hip[0] + 6, hip[1] - 3), (hip[0] - 10, hip[1] + 5), R["dark"], 2, hi=True)
            cv.px(hip[0] + 6, hip[1] - 3, R["accent"][3])
            cv.px(hip[0] - 10, hip[1] + 5, R["accent"][2])                   # kojiri
            if p == "daisho":                                                    # wakizashi above it
                line(cv, (hip[0] + 5, hip[1] - 5), (hip[0] - 6, hip[1] + 0), R["dark"], 2, hi=True)
                cv.px(hip[0] + 5, hip[1] - 5, R["accent"][3])
        elif p == "jitte":
            line(cv, (hip[0] + 3, hip[1] - 4), (hip[0] + 1, hip[1] + 4), R["metal"], 1)
            cv.px(hip[0] + 4, hip[1] - 1, R["metal"][1])
            cv.px(hip[0] + 3, hip[1] - 5, (190, 50, 40))                        # red tassel
        elif p == "gunbai":
            f = m_ellipse(hip[0] - 4.5, hip[1] + 1, 2.8, 3.2)
            cv.paste(f, shade_rows(f), R["dark"])
            cv.px(hip[0] - 4, hip[1] + 1, R["accent"][2])
            cv.px(hip[0] - 4, hip[1] + 4, R["accent"][3])
        elif p == "ofuda":
            for k in range(2):
                m = (XX >= hip[0] + 4 + k * 2) & (XX <= hip[0] + 5 + k * 2) & (YY >= hip[1]) & (YY <= hip[1] + 4)
                cv.paste(m, shade_rows(m, outline=False), R["collar"])
                cv.px(hip[0] + 4 + k * 2, hip[1] + 2, (190, 50, 40))
        elif p == "scroll":                               # scroll case at the obi
            line(cv, (hip[0] + 5, hip[1] - 4), (hip[0] + 8, hip[1] + 3), R["accent"], 3)
            cv.px(hip[0] + 5, hip[1] - 4, R["dark"][1])
        elif p == "gourd":                                # sake / water gourd (hyotan)
            for cy_, r in ((hip[1] + 1, 1.6), (hip[1] + 4, 2.3)):
                gm = m_ellipse(hip[0] + 6.5, cy_ + 0.5, r, r)
                cv.paste(gm, shade_rows(gm), R["straw"])
        elif p == "inro":
            im = (XX >= hip[0] + 4) & (XX <= hip[0] + 6) & (YY >= hip[1] + 1) & (YY <= hip[1] + 4)
            cv.paste(im, shade_rows(im), R["dark"])
            cv.px(hip[0] + 5, hip[1] + 2, R["accent"][3])
        elif p == "lantern":
            lm = m_ellipse(hip[0] + 9, hip[1] + 6, 2.2, 3)
            cv.paste(lm, shade_rows(lm), ramp((250, 220, 150)))


# ------------------------------------------------------------------------------------------- frame assembly
def palette(T):
    acc = T["accent"]
    R = {"skin": ramp(T["skin"]), "hair": ramp(T["hair"]), "top": ramp(T["top"]), "lower": ramp(T["lower"]),
            "accent": ramp(acc), "collar": ramp(COLLAR), "armor": ramp(T.get("armor", (120, 120, 130))),
            "wood": ramp(WOOD), "metal": ramp(METAL), "dark": ramp(DARK), "tabi": ramp(TABI),
            "sandal": ramp(SANDAL), "straw": ramp(STRAW), "eye": ramp(T["eye"]), "mask": ramp(T.get("mask_col", (74, 58, 72))),
            "haori": ramp(T.get("haori") or T["top"]), "pattern": ramp(T.get("pcol", acc)),
            "lace": ramp(T.get("lace", acc)), "helm": ramp(T.get("helm", T.get("armor", (90, 90, 100)))),
            "crest": ramp(T.get("crest_col", (226, 190, 80))), "band": ramp(T.get("band", acc)),
            "cloth": ramp(T.get("cloth", (200, 196, 180))), "cloak": ramp(T.get("cloak", (90, 80, 70))),
            "facial": ramp(T.get("facial_col", T["hair"])), "tattoo": ramp(T.get("tattoo", (40, 70, 120))),
            "fur": ramp((222, 206, 176)), "iron": ramp((112, 116, 126)), "rust": ramp((150, 96, 66)), "mempo": ramp(T.get("mempo", (110, 40, 36))),
            "mask_porcelain": ramp((240, 238, 232)), "mask_death": ramp((236, 232, 226)),
            "lining": ramp(T.get("lining", COLLAR)), "cord": ramp(T.get("cord", (236, 228, 200))),
            "mask_reed": ramp((222, 204, 150)),          # pale straw: reads as a face against brown hair
            "mask_noh": ramp((246, 240, 226)), "mask_stitched": ramp((214, 204, 196)),
            "hat": ramp(T.get("hat_col", STRAW))}
    if T.get("mask_tone") and T.get("mask") in ("porcelain", "death", "reed", "noh", "stitched"):
        R["mask_" + T["mask"]] = ramp(T["mask_tone"])          # City of Masks: iron, cedar, clay, shell, jade...
    return R


HEAD_SCALE = 0.64       # head size vs. the design grid (user: heads -25% -> 0.75; 2026-11-07 adult proportions)
NECK_UP = -1            # head drop (negative = lower); set per view: side -2, front/back -3 (user: "most of the neck")
NECK_SIDE, NECK_FB = -2, -3


def head_anchor(P):
    ox, oy = head_origin(P)
    return ox + 14.5, oy + 19.5                              # chin / neck joint


def neck_top(P):
    ax, ay = head_anchor(P)
    return int(ay - NECK_UP - 2)


def draw_neck(cv, T, P, R, front=False):
    """Neck: width by build and sex, the jaw's shadow across the top, a lit front edge, an Adam's apple on grown men,
    a throat guard (nodowa) on heavy armour."""
    ax, ay = head_anchor(P)
    top = neck_top(P)
    fem, heavy = T.get("female"), T["build"] == "heavy"
    w = 3 if fem else 4 + (2 if T["build"] in ("sumai", "strongman") else 1 if T["build"] in ("round", "heavy") or
                            P.get("wide", 0) >= 2 else 0)
    x0 = int(ax) - (w // 2 if front else 2)
    nk = (XX >= x0) & (XX <= x0 + w - 1) & (YY >= top) & (YY <= top + 2)   # a short stub: the head sits on the collar
    t = np.where(nk, 2, 0)
    t[nk & (YY <= top + 1)] = 0                             # the jaw's shadow
    t[nk & (YY == top + 2)] = 1
    if front:
        t[nk & (XX == x0) & (YY > top + 1)] = 1
        t[nk & (XX == x0 + w - 1) & (YY > top + 1)] = 3
    else:
        t[nk & (XX == x0 + w - 1) & (YY > top + 1)] = 3     # the lit front of the throat
        t[nk & (XX == x0) & (YY > top + 1)] = 1             # nape in shadow
    pal = R["dark"] if heavy else R["skin"]
    cv.paste(nk, t, pal)
    if not fem and not heavy and T.get("age") != "child" and T.get("height", 0) > -6:
        if front:
            cv.px_on(x0 + w // 2, top + 2, pal[3])
        else:
            cv.px_on(x0 + w - 1, top + 2, pal[4])         # Adam's apple
    if heavy:                                              # nodowa: laced throat guard
        for xx in range(x0, x0 + w):
            cv.px_on(xx, top + 2, R["lace"][2] if xx % 2 else R["armor"][2])


def scaled_head(layer, P):
    """Shrink a head layer about the chin and lift it by NECK_UP. Box-average, then snap each pixel back to the
    layer's own colours so the result stays crisp pixel art."""
    a = layer[..., 3] > 0
    if not a.any():
        return layer
    ys, xs = np.nonzero(a)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    ax, ay = head_anchor(P)
    crop = Image.fromarray(layer[y0:y1, x0:x1], "RGBA").convert("RGBa")
    nw, nh = max(1, round((x1 - x0) * HEAD_SCALE)), max(1, round((y1 - y0) * HEAD_SCALE))
    sm = np.array(crop.resize((nw, nh), Image.BOX).convert("RGBA")).astype(int)
    src = layer[y0:y1, x0:x1].reshape(-1, 4)
    pal = np.unique(src[src[:, 3] > 0][:, :3], axis=0).astype(int)
    out = np.zeros_like(layer)
    nx0 = int(round(ax + (x0 - ax) * HEAD_SCALE))
    ny0 = int(round(ay + (y0 - ay) * HEAD_SCALE)) - NECK_UP
    for yy in range(nh):
        for xx in range(nw):
            px = sm[yy, xx]
            if px[3] < 110:
                continue
            c = pal[np.argmin(((pal - px[:3]) ** 2).sum(axis=1))]
            ty, tx = ny0 + yy, nx0 + xx
            if 0 <= ty < FH and 0 <= tx < FW:
                out[ty, tx, :3] = c
                out[ty, tx, 3] = 255
    return out


def restamp_eyes(cv, T, P, R):
    """Crisp compact eyes on the scaled head (the box downscale muddies the 4x4 design eyes)."""
    if T.get("eyes", "normal") != "normal" or T.get("mask") in ("porcelain", "reed", "noh") or             P.get("expr") in ("pain", "focus"):
        return
    ox, oy = head_origin(P)
    ax, ay = head_anchor(P)
    sc = lambda x, y: (int(round(ax + (x - ax) * HEAD_SCALE)), int(round(ay + (y - ay) * HEAD_SCALE)) - NECK_UP)  # noqa
    K, W, er = FIXED["eyek"], FIXED["white"], R["eye"]
    ex, ey = sc(ox + 12.5, oy + 12)
    for c in range(3):
        cv.px(ex + c, ey, K)                                       # lash line
    cv.px(ex, ey + 1, er[1]), cv.px(ex + 1, ey + 1, er[2]), cv.px(ex + 2, ey + 1, W)
    cv.px(ex + 1, ey + 2, er[3]), cv.px(ex, ey + 2, er[1])
    if T.get("female"):
        cv.px(ex - 1, ey, K)
    fx, fy = sc(ox + 19.5, oy + 12)
    cv.px(fx, fy, K), cv.px(fx + 1, fy, K)
    cv.px(fx, fy + 1, er[2]), cv.px(fx + 1, fy + 1, W)


# ------------------------------------------------------------------------------------------- face kit
# The head is drawn on a 4x design grid and box-scaled to HEAD_SCALE, which blurs one-pixel features. Faces are
# therefore stamped crisply at sprite resolution after scaling, from a per-character kit:
#   eye   round | sharp | gentle | half | wide | smile (closed ^) | tired
#   brow  straight | angled | worried | arched | thick | skeptical | none
#   mouth neutral | set | smile | smirk | frown | grin | open | pout | toothless
#   nose  dot | strong | none
#   marks scar_cheek, scar_nose, scar_brow, freckles, mole_eye, mole_chin, bags, laugh, wrinkles, blush, paint_red,
#         paint_white, beauty
# Travelers set "kit" explicitly; everyone else gets one derived from their spec plus a little seeded variety.
def kit_ok(T, P=None):
    return not (T.get("mask") in ("porcelain", "reed", "noh", "death", "stitched") or T.get("eyes") == "glow")


def face_kit(T):
    k = dict(T.get("kit") or {})
    seed = sum(ord(c) * (i + 3) for i, c in enumerate(T.get("key", T.get("name", "x"))))
    old = T.get("age") == "old"
    fem = T.get("female")
    eyes = T.get("eyes", "normal")
    k.setdefault("eye", {"narrow": "half", "old": "half", "closed": "smile"}.get(
        eyes, ("round", "sharp", "gentle", "wide")[seed % 4] if fem else ("round", "sharp", "half", "gentle")[seed % 4]))
    k.setdefault("brow", {"thick": "thick", "stern": "angled"}.get(T.get("brow", "normal"),
                 "arched" if fem else ("straight", "angled", "straight", "skeptical")[seed // 4 % 4]))
    m = T.get("mouth", "normal")
    k.setdefault("mouth", {"normal": ("neutral", "smile", "set", "neutral")[seed // 16 % 4]}.get(m, m))
    k.setdefault("nose", "strong" if (old or T.get("build") in ("heavy", "round", "sumai", "strongman")) and not fem else "dot")
    marks = list(k.get("marks", []))
    if "kit" not in T:
        if T.get("scar"):
            marks.append("scar_cheek")
        if old:
            marks += ["wrinkles", "bags"]
        if fem and T.get("clan") in ("peasant", "eta"):
            marks.append("freckles")
        elif fem:
            marks.append("blush")
        if T.get("blushm"):
            marks.append("drunk")
        if seed % 7 == 0 and not old:
            marks.append(("mole_eye", "mole_chin")[seed % 2])
    k["marks"] = marks
    return k


PROFILE = True              # side views: the head turns where the feet point (user), one eye, nose past the edge
GAZE_DOWN = False           # (tried: irises low under the lid; user wanted heads turned to the feet instead)
LOOK_DOWN = 0               # feature drop (0 = off)
SCAR, MOLE, FRECK, RED = (232, 180, 168), (70, 44, 40), (196, 126, 96), (190, 52, 60)


def _eye(cv, x, y, style, er, K, W, mirror, wide=3, lash=False):
    """One eye, outer corner on the left (or the right when mirror). x, y = top-left of the lash line."""
    def p(dx, dy, c):
        cv.px(x + (wide - 1 - dx if mirror else dx), y + dy, c)
    if style == "smile":                                   # closed, curved up: ^
        p(0, 1, K), p(1, 0, K), p(min(2, wide - 1), 1 if wide > 2 else 0, K)
        return
    if style == "half":                                    # heavy upper lid: calm, sleepy or wary
        for c in range(wide):
            p(c, 0, K)
            p(c, 1, er[1] if c < wide - 1 else W)
        p(0, 1, K)
        return
    if style == "sharp":                                   # narrow, upswept outer corner
        p(-1, -1, K) if wide > 2 else None
        for c in range(wide):
            p(c, 0, K)
        p(0, 1, er[2]), p(1, 1, er[3] if wide > 2 else W)
        if wide > 2:
            p(2, 1, W)
        return
    if style == "gentle":                                  # outer corner droops
        p(0, 1, K)
        for c in range(1, wide):
            p(c, 0, K)
        p(1, 1, er[2]), p(1, 2, er[3]) if wide > 2 else None
        if wide > 2:
            p(2, 1, W)
        return
    # round / wide / tired: the big Octopath eye, gaze lowered toward the feet (the lid shades the top row)
    for c in range(wide):
        p(c, 0, K)
    if wide > 2 and GAZE_DOWN:
        p(0, 1, er[1]), p(1, 1, er[1]), p(2, 1, er[1] if style != "wide" else W)
        p(0, 2, er[2]), p(1, 2, er[3]), p(2, 2, W)
        return
    p(0, 1, er[1]), p(1, 1, er[2] if wide > 2 else W)
    if wide > 2:
        p(2, 1, W)
        p(0, 2, er[2]), p(1, 2, er[3]), p(2, 2, er[2] if style != "wide" else W)
    if style == "wide":
        p(0, 1, W) if wide > 2 else None
    if lash:
        p(-1, 0, K)


def _brow(cv, x, y, style, c, mirror, wide=3):
    def p(dx, dy):
        cv.px(x + (wide - 1 - dx if mirror else dx), y + dy, c)
    if style == "none":
        return
    rows = {"straight": [0] * wide, "angled": [0] * (wide - 1) + [1], "worried": [1] * (wide - 1) + [-1],
            "arched": [0, -1, 0][:wide], "thick": [0] * wide, "skeptical": [-1, -1, 0][:wide]}.get(style, [0] * wide)
    for dx, dy in enumerate(rows):
        p(dx, dy)
    if style == "thick":
        for dx in range(wide):
            p(dx, -1)


def _mouth(cv, x, y, style, K, W, M, skin, front):
    if style == "set":
        cv.px(x - 1, y, skin[0]), cv.px(x, y, skin[0])
    elif style == "smile":
        cv.px(x, y, M), cv.px(x - 1, y - 1, M)
        if front:
            cv.px(x + 1, y - 1, M)
    elif style == "smirk":
        cv.px(x, y, M), cv.px(x + 1, y - 1, M)
    elif style == "frown":
        cv.px(x - 1, y + 1, M), cv.px(x, y, M), cv.px(x + 1, y + 1, M)
    elif style == "grin":
        cv.px(x - 1, y, M), cv.px(x, y, W), cv.px(x + 1, y, M if front else W)
    elif style == "open":
        cv.px(x, y, K), cv.px(x + 1, y, K), cv.px(x, y + 1, M)
    elif style == "pout":
        cv.px(x, y, M), cv.px(x, y + 1, skin[1])
    elif style == "toothless":
        cv.px(x - 1, y, K), cv.px(x, y, K), cv.px(x + 1, y, M)
    else:
        cv.px(x, y, M)


def stamp_face(cv, T, P, R, front=False):
    """Crisp eyes, brows, nose, mouth and marks on the scaled head (side 3/4 view, or front)."""
    if not kit_ok(T, P):
        return
    kit = face_kit(T)
    ox, oy = head_origin(P)
    ax, ay = head_anchor(P)
    sc = lambda x, y: (int(round(ax + (x - ax) * HEAD_SCALE)), int(round(ay + (y - ay) * HEAD_SCALE)) - NECK_UP)  # noqa
    K, W, M, er = FIXED["eyek"], FIXED["white"], FIXED["mouth"], R["eye"]
    skin = R["mask_" + T["mask"]] if T.get("mask") in ("porcelain",) else R["skin"]
    brc = R["hair"][1] if T.get("hair") else R["dark"][1]
    eye, brow = kit["eye"], kit["brow"]
    expr = P.get("expr")
    if expr == "pain":
        eye, brow = "pain", "worried"
    elif expr in ("focus", "calm"):
        eye = "shut"
    elif expr == "grin" and eye not in ("smile",):
        eye = "smile" if eye in ("gentle", "round") else eye
    elif expr in ("laugh", "laugh2"):
        eye = "smile"
    elif expr == "surprise":
        eye, brow = "wide", ("arched" if brow != "none" else brow)
    elif expr in ("think", "smug"):
        eye = "half"
    mouth = kit["mouth"]
    if expr == "pain":
        mouth = "open"
    elif expr == "grin" and mouth in ("neutral", "set", "smile"):
        mouth = "grin"
    elif expr in ("talk", "laugh2", "surprise"):
        mouth = "open"
    elif expr == "laugh":
        mouth = "grin"
    elif expr == "smug":
        mouth = "smirk"
    elif expr == "think":
        mouth = "set"
    covered = T.get("mask") in (True, "cloth", "mempo")
    fem = T.get("female")
    LD = LOOK_DOWN
    if front:
        cx = ox + 15
        eyes_at = [((sc(cx - 4.5, oy + 12)[0], sc(cx - 4.5, oy + 12)[1] + LD), False),
                   ((sc(cx + 2.5, oy + 12)[0], sc(cx + 2.5, oy + 12)[1] + LD), True)]
        mx, my = sc(cx, oy + 17)
        nx, ny = sc(cx, oy + 15)
        ny += LD
    elif PROFILE:
        e0 = sc(ox + 17.5, oy + 12)
        eyes_at = [((e0[0], e0[1] + LD), False)]
        fx, fy = None, None
        mx, my = sc(ox + 21.2, oy + 17)
        nx, ny = sc(ox + 22.8, oy + 15)
        ny += LD
    else:
        e0 = sc(ox + 12.5, oy + 12)
        eyes_at = [((e0[0], e0[1] + LD), False)]
        fx, fy = sc(ox + 19.5, oy + 12)
        fy += LD
        mx, my = sc(ox + 19, oy + 17)
        nx, ny = sc(ox + 22.8, oy + 15)
        ny += LD
    # eyes + brows
    for (ex, ey), mir in eyes_at:
        if eye == "pain":
            for d in ((0, 0), (1, 1), (2, 0) if False else (0, 2)):
                cv.px(ex + (2 - d[0] if mir else d[0]), ey + d[1], K)
            cv.px(ex + (0 if mir else 2), ey + 1, K)
        elif eye == "shut":
            for c in range(3):
                cv.px(ex + c, ey + 1, K)
        else:
            _eye(cv, ex, ey, eye if eye != "tired" else "round", er, K, W, mir, 3, lash=fem)
        if brow != "none" and not T.get("hide_brows"):
            _brow(cv, ex, ey - 2, brow, brc, mir, 3)
    if not front and fx is not None:                       # the far eye, foreshortened (3/4 view only)
        if eye == "pain":
            cv.px(fx + 1, fy, K), cv.px(fx, fy + 1, K)
        elif eye == "shut":
            cv.px(fx, fy + 1, K), cv.px(fx + 1, fy + 1, K)
        else:
            _eye(cv, fx, fy, eye if eye != "tired" else "round", er, K, W, False, 2)
        if brow != "none" and not T.get("hide_brows"):
            _brow(cv, fx, fy - 2, "skeptical" if brow == "skeptical" else brow, brc, False, 2)
    if T.get("glasses"):                                   # round rims over the eyes
        gl = FIXED["glass"]
        for (ex, ey), mir in eyes_at + ([] if front or fx is None else [((fx, fy), False)]):
            w = 3 if (front or (ex, ey) != (fx if not front else -9, fy if not front else -9)) else 2
            for c in range(-1, w + 1):
                cv.px_on(ex + c, ey - 1, gl), cv.px_on(ex + c, ey + 3, gl)
            cv.px_on(ex - 1, ey + 1, gl), cv.px_on(ex + w, ey + 1, gl)
            cv.px_on(ex + w - 1, ey + 1, FIXED["glint"])
    # nose (in profile it juts past the face's edge) + the ear at the back of the cheek
    if not front and PROFILE:
        if not covered:
            ry = ny
            edge = nx
            while edge + 1 < FW and cv.col[ry, edge + 1, 3] > 0:
                edge += 1
            cv.px(edge + 1, ry, skin[2]), cv.px_on(edge, ry + 1, skin[1])
            if kit["nose"] == "strong":
                cv.px(edge + 1, ry - 1, skin[3])
            nx, ny = edge, ry
        if not T.get("hide_ear"):
            ex0, ey0 = sc(ox + 11.5, oy + 14)
            if cv.col[ey0, ex0, 3] > 0 and tuple(cv.col[ey0, ex0, :3]) in [tuple(c) for c in skin]:
                cv.px_on(ex0, ey0, skin[1]), cv.px_on(ex0 + 1, ey0, skin[3]), cv.px_on(ex0, ey0 + 1, skin[1])
    elif kit["nose"] != "none" and not covered:
        cv.px_on(nx, ny, skin[1])
        if kit["nose"] == "strong":
            cv.px_on(nx, ny - 1, skin[3]), cv.px_on(nx - (0 if front else 1), ny + (1 if front else 0), skin[1])
    # marks
    (ex, ey), _ = eyes_at[0]
    for mk in kit["marks"]:
        if mk == "scar_cheek":
            for d in range(3):
                cv.px_on(ex + 2 + d, ey + 2 + d, SCAR)
        elif mk == "scar_nose":
            for d in range(4 if not front else 5):
                cv.px_on(ex + 2 + d, ey + 2, SCAR)
        elif mk == "scar_brow":
            cv.px_on(ex + 1, ey - 3, SCAR), cv.px_on(ex + 1, ey - 2, SCAR), cv.px_on(ex + 2, ey - 1, SCAR)
        elif mk == "freckles" and not covered:
            for d in ((0, 3), (2, 4), (4, 3)) + (((7, 3), (9, 4)) if front else ()):
                cv.px_on(ex + d[0], ey + d[1], FRECK)
        elif mk == "mole_eye":
            cv.px_on(ex + (3 if not front else -1), ey + 3, MOLE)
        elif mk == "mole_chin" and not covered:
            cv.px_on(mx + 1, my + 2, MOLE)
        elif mk == "beauty" and not covered:
            cv.px_on(mx + 2, my - 1, MOLE)
        elif mk == "bags":
            cv.px_on(ex, ey + 3, skin[1]), cv.px_on(ex + 1, ey + 3, skin[1])
            if front:
                cv.px_on(ex + 6, ey + 3, skin[1]), cv.px_on(ex + 7, ey + 3, skin[1])
        elif mk == "laugh" and not covered:
            cv.px_on(mx - 2, my - 1, skin[1])
            if front:
                cv.px_on(mx + 2, my - 1, skin[1])
        elif mk == "wrinkles":
            for c in range(3):
                cv.px_on(ex + 1 + c, ey - 4, skin[1])
            cv.px_on(ex - 1, ey + 1, skin[1])
        elif mk in ("blush", "drunk") and not covered:
            col = FIXED["blush"] if mk == "blush" else (230, 110, 100)
            cv.px_on(ex, ey + 3, col), cv.px_on(ex + 1, ey + 3, col)
            if front:
                cv.px_on(ex + 6, ey + 3, col), cv.px_on(ex + 7, ey + 3, col)
            if mk == "drunk":
                cv.px_on(nx, ny, col)
        elif mk == "paint_red":                            # Scorpion-style red lid paint, winged
            for c in range(3):
                cv.px_on(ex + c, ey - 1, RED)
            cv.px_on(ex - 1, ey, RED)
            if front:
                for c in range(3):
                    cv.px_on(ex + 7 + c, ey - 1, RED)
                cv.px_on(ex + 10, ey, RED)
        elif mk == "paint_white":
            cv.px_on(ex + 1, ey - 3, (250, 250, 250)), cv.px_on(ex + 2, ey - 3, (250, 250, 250))
    # mouth
    if not covered:
        _mouth(cv, mx, my, mouth, K, W, M, skin, front)


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]


def draw_hand_prop(cv, T, P, R):
    """A small object in the near fist: item (a medicine gourd), gunbai (the war fan), ofuda (a prayer strip)."""
    hx, hy = P["ha_f"]
    kind = P["hand_prop"]
    if kind == "item":
        body = m_ellipse(hx + 0.5, hy - 2.5, 1.9, 2.1) | m_ellipse(hx + 0.5, hy - 5.0, 1.2, 1.2)
        cv.paste(body, shade_rows(body), ramp((206, 120, 70)))
        cv.px(hx, hy - 6.5, R["wood"][1])                      # the cork
        cv.px_on(hx + 1, hy - 3, (255, 236, 210))
        cv.keep |= body
    elif kind == "gunbai":
        line(cv, (hx, hy), (hx + 1, hy - 4), R["dark"], 1, hi=False)
        fan = m_ellipse(hx + 1.5, hy - 7.5, 3.2, 3.8)
        t = shade_rows(fan)
        cv.paste(fan, t, R["dark"])
        cv.px_on(hx + 1, hy - 8, R["accent"][3]), cv.px_on(hx + 2, hy - 8, R["accent"][3])
        cv.px_on(hx + 1, hy - 7, R["accent"][2])
        cv.keep |= fan
    elif kind == "ofuda":
        st = (XX >= hx) & (XX <= hx + 1) & (YY >= hy - 7) & (YY <= hy - 2)
        cv.paste(st, shade_rows(st, outline=False), R["collar"])
        cv.px(hx, hy - 5, (190, 50, 40)), cv.px(hx + 1, hy - 4, (190, 50, 40))


def draw_fingers(cv, T, P, R, n):
    """Raised fingers over the near hand (Haruki counts on his fingers)."""
    hx, hy = P["ha_f"]
    sk = R["skin"]
    for k in range(int(n)):
        x = int(round(hx - 1 + k))
        for dy in (2, 3):
            cv.px(x, int(round(hy)) - dy, sk[3] if k % 2 == 0 else sk[2])
        cv.px(x, int(round(hy)) - 4, sk[0])


def draw_dust(cv, P):
    """An impact puff where a heavy blow meets the ground."""
    dx, dy = wdir(P)
    g = P["ha_f"]
    k = (GROUND - 1 - g[1]) / dy if dy > 0.2 else 18
    x0 = g[0] + dx * min(k, 24)
    for ox_, oy_, r, a in ((-4, -1, 1.8, 160), (3, -2, 2.2, 190), (0, -3, 1.6, 150), (6, -1, 1.3, 120),
                           (-7, -1, 1.1, 110)):
        m = m_ellipse(x0 + ox_, GROUND - 1 + oy_, r, r * 0.8) & (cv.col[..., 3] < a)
        cv.col[m] = (226, 214, 190, a)


def draw_muzzle(cv, T, P):
    """Matchlock flash and smoke at the muzzle."""
    dx, dy = wdir(P)
    g = P["ha_f"]
    mx, my = g[0] + dx * 22, g[1] + dy * 22
    for r, col in ((3.2, (255, 190, 80, 200)), (1.8, (255, 250, 200, 255))):
        m = m_ellipse(mx + 1.5, my + 0.5, r * 1.4, r) & (cv.col[..., 3] < col[3])
        cv.col[m] = col
    for ox_, oy_, r in ((-1, -3, 1.6), (2, -4, 1.8), (5, -2, 1.4)):
        m = m_ellipse(mx + ox_, my + oy_, r, r) & (cv.col[..., 3] == 0)
        cv.col[m] = (210, 210, 214, 150)


# Upright standing poses (user, 2026-11-08: "everyone leans, head behind the hips"). OFF by default so the game's sheets
# stay as they are; RT_UPRIGHT=1 turns it on (the AI sprite guides, tools/gen_upright_guides.py). In the standing blocks
# the shoulders (with elbows and hands, so grips and weapons move as one) and the feet (with the knees) are moved to
# stack over the hip, and the head one pixel forward: the skull ends half a pixel ahead of the hip (it can only sit on
# half pixels). Walk and run keep their forward lean; attacks, hurt, evade, KO and bows are untouched.
UPRIGHT_ON = os.environ.get("RT_UPRIGHT") == "1"
UPRIGHT_KINDS = {"idle8", "ready", "cast", "chant", "item", "guard", "talk", "nod", "think", "victory2"} | \
    {"cast_" + c for c in CAST_KINDS}


def upright(P):
    P = dict(P)
    hx = P["hip"][0]
    d = hx - (P["sh_b"][0] + P["sh_f"][0]) / 2
    if P.get("_build") == "sumai":                         # the shoulder sits mid-depth by design, the belly in front
        d = 0.0
    shift(P, ("sh_b", "sh_f", "el_b", "el_f", "ha_b", "ha_f"), (d, 0))
    f = hx - (P["ft_b"][0] + P["ft_f"][0]) / 2
    shift(P, ("ft_b", "ft_f", "kn_b", "kn_f"), (f, 0))
    if not P.get("_old"):                                  # the old already stoop one pixel forward (build_pose)
        P["head"] = (P["head"][0] + 1, P["head"][1])
    return P


def mark_upright(T, P, kind):
    if UPRIGHT_ON and kind in UPRIGHT_KINDS:
        P["_upright"], P["_build"], P["_old"] = True, T.get("build"), T.get("age") == "old"
    return P


def compose(T, P):
    global NECK_UP
    NECK_UP = NECK_SIDE
    whand_b = P.get("whand") == "b"
    if whand_b or P.get("wlay") is not None:
        P["grip2"] = False                                 # the near hand is free (gesture, item, bow)
    P = stature(T, build_pose(T, P))
    if P.get("_upright"):
        P = upright(P)
    P = rig_arms(T, rig_legs(T, P))
    if whand_b:
        P["wgrip"] = P["ha_b"]                             # the weapon rests upright in the far hand
    elif P.get("wlay") is not None:
        P["wgrip"] = (P["wlay"][0] + CX, P["wlay"][1] + CY)   # laid on the floor
    R = palette(T)
    cv = Canvas()
    long_w = T["weapon"] in ("yari", "bo", "shakujo")
    weapon_back = (P["wang"] < -100 or (P["smear"] is False and P["wang"] < -60 and long_w)) and not P.get("wfront")
    if T["weapon"] == "tetsubo" and not P["smear"]:
        weapon_back = False                                # club rests on the near shoulder, in front of the bulk
    if whand_b or P.get("wlay") is not None:
        weapon_back = True
    if P.get("wlay") is not None and not P["sheathed"] and T["weapon"] != "none":
        draw_weapon(cv, T, P, R)                           # on the floor, behind everything
    hb = Canvas()
    draw_hair_back(hb, T, P, R)
    over(cv.col, scaled_head(hb.col, P))
    if T.get("sashimono"):
        draw_sashimono(cv, T, P, R, "side")
    draw_prop_back(cv, T, P, R)
    draw_arm(cv, T, P, R, "b", hand=not P["grip_b"])
    if weapon_back and not P["sheathed"] and P.get("wlay") is None:
        draw_weapon(cv, T, P, R)
        if P["grip_b"] or (whand_b and T["weapon"] != "none"):
            draw_fist(cv, T, P, R, "b")
    draw_legs(cv, T, P, R)
    draw_torso(cv, T, P, R)
    draw_prop_front(cv, T, P, R)
    draw_neck(cv, T, P, R)
    hf = Canvas()
    draw_face(hf, T, P, R)
    draw_hair_front(hf, T, P, R)
    over(cv.col, scaled_head(hf.col, P))
    if kit_ok(T, P):
        stamp_face(cv, T, P, R)
    else:
        restamp_eyes(cv, T, P, R)
    if not weapon_back and not P["sheathed"]:
        if P["grip_b"]:
            over(cv.col, arm_layer(T, P, R, cv.col, "b", fist=False, forearm_only=True))
        draw_weapon(cv, T, P, R)
        if P["grip_b"]:
            draw_fist(cv, T, P, R, "b")
    holds = (T["weapon"] != "none" and not P["sheathed"] and not P.get("dropped") and not whand_b
             and P.get("wlay") is None) or P.get("fist", False) or bool(P.get("hand_prop"))
    if P.get("open_hand"):
        holds = False
    over(cv.col, arm_layer(T, P, R, cv.col, "f", fist=holds))
    if P.get("hand_prop"):
        draw_hand_prop(cv, T, P, R)
    if P.get("fingers"):
        draw_fingers(cv, T, P, R, P["fingers"])
    outline_outer(cv)
    if P.get("dust"):
        draw_dust(cv, P)
    if P.get("muzzle"):
        draw_muzzle(cv, T, P)
    if P["smear"]:
        g = P["ha_f"]
        sd = P["smear_dir"]
        if sd == "t":                                      # thrust: speed lines along the weapon, behind the point
            dx, dy = wdir(P)
            nx, ny = -dy, dx
            reach = {"yari": 26, "naginata": 28, "bo": 19, "shakujo": 22, "tetsubo": 20, "nodachi": 26,
                     "none": 3, "tanto": 6}.get(T["weapon"], 18)
            for off, k0, k1, alpha in ((-2.0, 4, reach - 6, 150), (0.0, -2, reach - 3, 230), (2.0, 6, reach - 8, 120)):
                for k in np.arange(k0 - 8, k1, 0.5):
                    x, y = int(round(g[0] + dx * k + nx * off)), int(round(g[1] + dy * k + ny * off))
                    if 0 <= x < FW and 0 <= y < FH and cv.col[y, x, 3] < alpha and k < k1:
                        cv.col[y, x] = (255, 255, 250, alpha)
        else:
            if sd == "v":                                  # overhead cut: arc from above the head down to the front
                cx_, cy_ = g[0] - 10, g[1] - 2
                lo, hi_ = -100, 60
            elif sd == "u":                                # rising cut: arc from below up to the front-high
                cx_, cy_ = g[0] - 8, g[1] + 1
                lo, hi_ = -70, 95
            elif sd == "w":                                # draw-cut: a long flat arc at chest height
                cx_, cy_ = g[0] - 12, g[1] + 3
                lo, hi_ = -40, 35
            else:
                cx_, cy_ = g[0] - 6, g[1] + 2
                lo, hi_ = -85, 50
            d = np.hypot(XX + 0.5 - cx_, (YY + 0.5 - cy_) * (1.6 if sd == "w" else 1.0))
            ang = np.degrees(np.arctan2(YY + 0.5 - cy_, XX + 0.5 - cx_))
            arc = (ang > lo) & (ang < hi_)
            rr = P.get("smear_r", 1.0)
            for r0, r1, alpha in ((17.5, 19.5, 120), (15.5, 17.5, 230), (14.5, 15.5, 140)):
                m = arc & (d >= r0 * rr) & (d < r1 * rr) & (cv.col[..., 3] < alpha)
                cv.col[m] = (255, 255, 250, alpha)
    if P["glow"] is not None:
        gx, gy = P["glow"]
        rings = ((2.6, 110), (1.4, 230)) if P.get("glow_small") else ((4.5, 90), (3.0, 170), (1.6, 255))
        gc = np.array(T.get("glow", FIXED["glow"]), float)
        for rr, alpha in rings:
            m = m_ellipse(gx, gy, rr, rr)
            if P.get("glow_small"):                        # cupped in the hands: blend over the body
                cv.col[m, :3] = (cv.col[m, :3] * (1 - alpha / 255) + gc * (alpha / 255)).astype(np.uint8)
                cv.col[m, 3] = np.maximum(cv.col[m, 3], alpha)
            else:
                cv.col[m & (cv.col[..., 3] < alpha)] = (*gc.astype(int), alpha)
        if not P.get("glow_small"):                        # released: a white-hot core, a soft halo, sparks
            halo = m_ellipse(gx, gy, 7.0, 7.0) & ~m_ellipse(gx, gy, 4.5, 4.5) & (cv.col[..., 3] == 0)
            cv.col[halo] = (*gc.astype(int), 55)
            core = m_ellipse(gx, gy, 1.0, 1.0)
            cv.col[core, :3] = np.clip(gc * 0.3 + 255 * 0.7, 0, 255).astype(np.uint8)
            cv.col[core, 3] = 255
            hot = np.clip(gc * 0.5 + 255 * 0.5, 0, 255).astype(int)
            seed = int(gx * 7 + gy * 13)
            for k in range(7):
                a = seed * 0.37 + k * 2.39996                # golden-angle spread
                r = 6.0 + (seed + k * 5) % 5
                sx, sy = int(round(gx + math.cos(a) * r)), int(round(gy + math.sin(a) * r))
                for ddx, ddy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)) if k % 3 == 0 else ((0, 0),):
                    x, y = sx + ddx, sy + ddy
                    if 0 <= x < FW and 0 <= y < FH and cv.col[y, x, 3] < 200:
                        cv.col[y, x] = (*(hot if (ddx, ddy) == (0, 0) else gc.astype(int)), 230)
            if T.get("glow"):                              # a caster's rim light: the spell lights the figure
                body = cv.col[..., 3] == 255
                rim = edges(body) & ~cv.keep
                d = np.hypot(XX + 0.5 - gx, YY + 0.5 - gy)
                rim &= d < 22
                k_ = np.clip(0.55 - d / 50.0, 0.15, 0.55)[rim][:, None]
                cv.col[rim, :3] = (cv.col[rim, :3] * (1 - k_) + gc * k_).astype(np.uint8)
    return cv.col


# ------------------------------------------------------------------------------------------- front / back views
# Field sprites face the way they walk: side (east; west = mirrored), front (toward the camera) and back.
FRONT_FACE = {8: 5, 9: 6, 10: 7, 11: 7, 12: 7, 13: 7, 14: 7, 15: 7, 16: 6, 17: 5, 18: 4, 19: 2}
FRONT_SHAPES = {
    "normal": FRONT_FACE,
    "round": {**FRONT_FACE, 16: 7, 17: 6, 18: 5, 19: 3},
    "square": {**FRONT_FACE, 16: 7, 17: 7, 18: 6, 19: 5, 20: 3},
    "long": {**FRONT_FACE, 17: 5, 18: 4, 19: 3, 20: 1},
    "sharp": {**FRONT_FACE, 16: 6, 17: 4, 18: 3, 19: 1},
}
LONG_W = ("yari", "bo", "shakujo", "naginata", "tetsubo", "nodachi", "yumi")


def fb_pose(kind, i):
    """Front/back body numbers (frame coords). kind: idle | walk | walk8 | talk | nod | rei."""
    if kind == "walk8":                                   # 8-phase: lift rises and falls, body dips after contact
        ph = i / 8.0
        la = max(0.0, 3.2 * math.sin(2 * math.pi * ph))
        lb = max(0.0, -3.2 * math.sin(2 * math.pi * ph))
        bob = [0, 1, 0, -1, 0, 1, 0, -1][i]
        return dict(bob=bob, lift=(int(round(la)), int(round(lb))), swing=math.cos(2 * math.pi * ph) * 1.2)
    if kind == "talk":
        return dict(bob=0, lift=(0, 0), swing=0, gest=[(0, 0), (-1, -7), (0, -5), (-2, -7)][i],
                    expr="talk" if i in (1, 3) else None, hdy=1 if i == 3 else 0)
    if kind == "nod":
        return dict(bob=0, lift=(0, 0), swing=0, hdy=[0, 1, 2, 0][i], expr="calm" if i == 2 else None)
    if kind == "rei":
        return dict(bob=0, lift=(0, 0), swing=0, hdy=[0, 2, 4][i], dip=[0, 1, 2][i], fold=[0, 2, 3][i],
                    expr="calm" if i else None)
    bob = [0, 1, 1, 0][i] if kind == "idle" else [0, -1, 0, -1][i]
    lift = (0, 0) if kind == "idle" else [(3, 0), (0, 0), (0, 3), (0, 0)][i]
    swing = 0 if kind == "idle" else [1, 0, -1, 0][i]
    return dict(bob=bob, lift=lift, swing=swing)


def fb_face_mask(cx, oy, rows):
    m = np.zeros((FH, FW), bool)
    for r, hw in rows.items():
        y = oy + r
        if 0 <= y < FH:
            m[y, max(0, int(cx - hw)):min(FW, int(cx + hw + 1))] = True
    return m


def draw_front_head(cv, T, P, R, back=False):
    """Head on the design grid (scaled later by scaled_head). cx = face centre."""
    ox, oy = head_origin(P)
    cx = ox + 15
    rows = FRONT_SHAPES[T.get("face", "normal")]
    mask = T.get("mask")
    hs = T["hairstyle"]
    sw = P.get("sway", 0)
    face = fb_face_mask(cx, oy, rows)
    cap = m_ellipse(cx + 0.5, oy + 9.5, 12.0, 10.5)
    # hanging hair behind the head (front view: at the sides; back view: drawn over the back later)
    if not back:
        side = np.zeros((FH, FW), bool)
        if hs in ("long", "long_topknot", "mane"):
            for sgn in (-1, 1):
                side |= m_poly([(cx + sgn * 6, oy + 9), (cx + sgn * 12.5, oy + 10), (cx + sgn * 13 + sw, oy + 30),
                                (cx + sgn * 8 + sw, oy + 31), (cx + sgn * 7, oy + 18)])
        elif hs == "bob":
            for sgn in (-1, 1):
                side |= m_poly([(cx + sgn * 6, oy + 9), (cx + sgn * 12, oy + 10), (cx + sgn * 11.5, oy + 21),
                                (cx + sgn * 7, oy + 21)])
        if side.any():
            t = shade_hair(side, P, cx, oy + 10)
            t[side & (t >= 2)] -= 1
            cv.paste(side, t, R["hair"])
    if back:                                                  # seen from behind: all hair (or scalp / helmet)
        if hs == "bald":
            sc = cap & (YY < oy + 21)
            cv.paste(sc, shade_rows(sc, dither=False), R["skin"])
            cv.px(cx - 11, oy + 13, R["skin"][1]), cv.px(cx + 12, oy + 13, R["skin"][1])
            if T.get("head_tattoo"):
                d1 = np.hypot(XX + 0.5 - cx, YY + 0.5 - (oy + 6))
                tm = sc & ~edges(sc) & ((np.abs(d1 - 4.5) < 0.6) | (np.abs(d1 - 7.5) < 0.6))
                for y, x in zip(*np.nonzero(tm)):
                    cv.col[y, x, :3] = R["tattoo"][1]
        else:
            hb = cap & (YY < oy + 21)
            hb |= m_poly([(cx - 9, oy + 14), (cx + 10, oy + 14), (cx + 8, oy + 21), (cx - 7, oy + 21)])
            if hs == "chonmage":
                pate = m_ellipse(cx + 0.5, oy + 5, 6, 4) & hb
                cv.paste(hb, shade_hair(hb, P, cx, oy + 10), R["hair"])
                cv.paste(pate, shade_rows(pate, dither=False), R["skin"])
            else:
                cv.paste(hb, shade_hair(hb, P, cx, oy + 10), R["hair"])
        draw_fb_hairtop(cv, T, P, R, cx, oy)
        draw_fb_headwear(cv, T, P, R, cx, oy, back=True)
        return
    # ---- front: face
    tones = np.full((FH, FW), 2, int)
    for r, hw in rows.items():
        y = oy + r
        if 0 <= y < FH:
            for x in range(int(cx - hw), int(cx + hw + 1)):
                if x <= cx - hw + 1 or r >= max(rows) - 1:
                    tones[y, x] = 1
                elif x >= cx + hw - 1 and r <= 13:
                    tones[y, x] = 3
    tones = finish_tones(face, tones, True)
    skin = R["skin"]
    if mask in ("porcelain", "death", "reed", "noh", "stitched"):
        skin = R["mask_" + mask]
    cv.paste(face, tones, skin)
    for sgn in (-1, 1):                                       # ears
        cv.px(cx + sgn * 8, oy + 13, skin[1]), cv.px(cx + sgn * 8, oy + 14, skin[1])
    if not kit_ok(T, P):
        cv.px(cx, oy + 15, skin[1])                               # nose
        K, W = FIXED["eyek"], FIXED["white"]
        er = R["eye"]
        eyes = T.get("eyes", "normal")
        for sgn in (-1, 1):
            ex = cx + sgn * 3 - (1 if sgn < 0 else 0) - 1
            ey = oy + 12
            if mask == "porcelain" or eyes == "glow":
                cv.px(ex + 1, ey + 1, FIXED["glowred"]), cv.px(ex + 2, ey + 1, FIXED["glowred"])
            elif eyes == "closed":
                cv.px(ex, ey + 2, K), cv.px(ex + 1, ey + 1, K), cv.px(ex + 2, ey + 1, K), cv.px(ex + 3, ey + 2, K)
            elif eyes in ("narrow", "old"):
                for c in range(4):
                    cv.px(ex + c, ey + 1, K)
                cv.px(ex + 1, ey + 2, er[2]), cv.px(ex + 2, ey + 2, er[2])
            elif mask != "reed":
                for c in range(4):
                    cv.px(ex + c, ey, K)
                cv.px(ex + 1, ey + 1, er[1]), cv.px(ex + 2, ey + 1, er[1])
                cv.px(ex + (2 if sgn < 0 else 1), ey + 1, W)
                cv.px(ex + 1, ey + 2, er[3]), cv.px(ex + 2, ey + 2, er[2])
            if mask not in ("porcelain", "reed", "noh"):
                for c in range(4):
                    cv.px(ex + c, ey - 2 - (1 if T.get("brow") == "stern" and (c == 0 if sgn > 0 else c == 3) else 0),
                          R["hair"][1])
        if T.get("glasses"):
            g = FIXED["glass"]
            for sgn in (-1, 1):
                ex = cx + sgn * 3 - (1 if sgn < 0 else 0) - 1
                for c in range(-1, 5):
                    cv.px_on(ex + c, oy + 11, g), cv.px_on(ex + c, oy + 16, g)
                for r_ in (12, 13, 14, 15):
                    cv.px_on(ex - 1, oy + r_, g), cv.px_on(ex + 4, oy + r_, g)
            cv.px_on(cx, oy + 13, g)
        if T.get("female") and not mask:
            for sgn in (-1, 1):
                cv.px(cx + sgn * 5, oy + 16, FIXED["blush"])
        if T.get("blushm"):
            for x in range(cx - 6, cx + 7):
                if abs(x - cx) > 2:
                    cv.px_on(x, oy + 15, (230, 110, 100))
        if not mask or mask == "death":
            mouth = T.get("mouth", "normal")
            if P.get("expr") == "grin" and mouth == "normal":
                mouth = "grin"
            if mouth == "grin":
                cv.px(cx - 1, oy + 17, FIXED["mouth"]), cv.px(cx, oy + 17, W), cv.px(cx + 1, oy + 17, FIXED["mouth"])
            elif mouth == "frown":
                cv.px(cx - 1, oy + 18, FIXED["mouth"]), cv.px(cx, oy + 17, FIXED["mouth"]), cv.px(cx + 1, oy + 18, FIXED["mouth"])
            elif mouth == "toothless":
                cv.px(cx - 1, oy + 17, K), cv.px(cx, oy + 17, K), cv.px(cx + 1, oy + 17, FIXED["mouth"])
            else:
                cv.px(cx, oy + 17, FIXED["mouth"])
    if mask in (True, "cloth"):
        mk = face & (YY >= oy + 16)
        cv.paste(mk, shade_rows(mk), R["mask"])
    elif mask == "mempo":
        mk = face & (YY >= oy + 14)
        t = shade_rows(mk)
        t[mk & (YY == oy + 17)] = 0
        cv.paste(mk, t, R["mempo"])
    if T.get("scar") and not kit_ok(T, P):
        for k in range(4):
            cv.px_on(cx + 3 + k, oy + 10 + k, FIXED["scar"])
    facial = T.get("facial")
    hc = R["facial"]
    if facial in ("beard", "longbeard"):
        bd = fb_face_mask(cx, oy + 1, {r: hw for r, hw in rows.items() if r >= 15})
        drop = 23 if facial == "beard" else 28
        bd |= m_poly([(cx - 5, oy + 17), (cx + 6, oy + 17), (cx + 3, oy + drop), (cx - 2, oy + drop)])
        bd &= ~((abs(XX - cx) <= 1) & (YY == oy + 18))
        t = shade_rows(bd)
        t[bd & ((XX + YY) % 3 == 0) & (t >= 2)] = 1
        cv.paste(bd, t, hc)
    if facial in ("mustache", "beard", "longbeard", "goatee_mustache"):
        for x in range(cx - 3, cx + 4):
            cv.px(x, oy + 16, hc[2])
        cv.px(cx - 4, oy + 17, hc[1]), cv.px(cx + 4, oy + 17, hc[1])
    if facial in ("goatee", "goatee_mustache"):
        for x in range(cx - 1, cx + 2):
            cv.px(x, oy + 19, hc[2]), cv.px(x, oy + 20, hc[1])
    if facial == "stubble":
        for x, y in ((cx - 3, 17), (cx + 3, 17), (cx - 1, 19), (cx + 1, 19)):
            cv.px_on(x, oy + y, skin[1])
    # ---- front: hair cap and bangs
    if hs == "bald":
        sc = cap & (YY < oy + 10) | (cap & ~face & (YY < oy + 14))
        cv.paste(sc, shade_rows(sc, dither=False), R["skin"])
        if T.get("head_tattoo"):
            d1 = np.hypot(XX + 0.5 - cx, YY + 0.5 - (oy + 6))
            tm = sc & ~edges(sc) & ((np.abs(d1 - 4.5) < 0.6) | (np.abs(d1 - 7.5) < 0.6))
            for y, x in zip(*np.nonzero(tm)):
                cv.col[y, x, :3] = R["tattoo"][1]
    else:
        front = cap & ~(face & (YY >= oy + 10))
        front &= (YY < oy + 16) | ~face
        front &= ~((YY >= oy + 13) & (np.abs(XX + 0.5 - cx) < 8))
        if hs == "chonmage":
            pate = m_ellipse(cx + 0.5, oy + 4.5, 6.5, 4) & front
        else:
            pate = None
            bangs = T.get("bangs", "normal")
            n = {"short": 4, "heavy": 5, "messy": 6, "swept": 5, "parted": 4, "center": 5, "side": 5,
                 "none": 0}.get(bangs, 5)                  # none: hair pulled back off the forehead
            for k in range(n):
                tx = cx - 7 + k * 14.0 / (n - 1)
                if bangs == "parted" and abs(tx - cx) < 1.5:
                    continue
                ty = oy + (13 if bangs in ("heavy", "center") else 12) + (k % 2)
                if bangs == "swept":
                    tx += 1.5
                front |= m_poly([(tx - 2.4, oy + 9), (tx + 2.4, oy + 9), (tx + (0.8 if bangs == "swept" else 0), ty)])
            front |= m_poly([(cx - 12, oy + 9), (cx - 7, oy + 9), (cx - 7.5, oy + 17), (cx - 10, oy + 18)])   # sidelocks
            front |= m_poly([(cx + 8, oy + 9), (cx + 13, oy + 9), (cx + 11, oy + 18), (cx + 8.5, oy + 17)])
        cv.paste(front, shade_hair(front, P, cx, oy + 10), R["hair"])
        if pate is not None:
            cv.paste(pate, shade_rows(pate, dither=False), R["skin"])
        below = np.zeros((FH, FW), bool)
        below[1:, :] = front[:-1, :]
        shm = below & ~front & face & (cv.col[..., 3] > 0)
        cv.col[shm, :3] = (cv.col[shm, :3] * 0.8).astype(np.uint8)
    draw_fb_hairtop(cv, T, P, R, cx, oy)
    draw_fb_headwear(cv, T, P, R, cx, oy, back=False)


def draw_fb_hairtop(cv, T, P, R, cx, oy):
    hs = T["hairstyle"]
    if hs in ("long_topknot", "bun"):
        b = m_ellipse(cx + 0.5, oy - 0.5, 3.6, 3.0)
        cv.paste(b, shade_hair(b, P, cx, oy), R["hair"])
    elif hs == "sumotop":
        b = m_capsule((cx + 0.5, oy + 3), (cx + 0.5, oy - 1), 2.6, 2.2)[0] | m_ellipse(cx + 0.5, oy - 3.5, 4.6, 4.0)
        cv.paste(b, shade_hair(b, P, cx, oy), R["hair"])
        for x in range(cx - 2, cx + 4):
            cv.px(x, oy + 0.5, R["band"][3 if x % 2 else 2])
            cv.px(x, oy + 1.5, R["band"][1])
    elif hs == "chonmage":
        b = m_capsule((cx, oy + 1.5), (cx + 0.5, oy - 3), 1.4, 1.1)[0]
        cv.paste(b, shade_hair(b, P, cx, oy), R["hair"])
    elif hs in ("spiky", "mane"):
        sp = np.zeros((FH, FW), bool)
        for k in range(7):
            a = math.radians(200 + k * 23)
            bx, by = cx + 10.5 * math.cos(a), oy + 9 + 9.5 * math.sin(a)
            sp |= m_poly([(bx - 2, by + 1.5), (bx + 2, by + 1.5), (bx + 4.5 * math.cos(a), by + 4.5 * math.sin(a))])
        cv.paste(sp, shade_hair(sp, P, cx, oy + 10), R["hair"])


def draw_fb_headwear(cv, T, P, R, cx, oy, back):
    head = T.get("head")
    if head == "hachimaki":
        band = m_ellipse(cx + 0.5, oy + 9.5, 12.2, 11) & (YY >= oy + 7) & (YY <= oy + 8)
        cv.paste(band, shade_rows(band, dither=False), R["band"])
        if back:
            for end in ((cx - 3 + P.get("sway", 0), oy + 16), (cx + 2 + P.get("sway", 0), oy + 15)):
                m = m_capsule((cx, oy + 8), end, 1.1, 0.7)[0]
                cv.paste(m, shade_rows(m), R["band"])
    elif head == "headcloth":
        hc = m_ellipse(cx + 0.5, oy + 9, 12.2, 10.8) & (YY <= oy + 7)
        t = shade_rows(hc)
        t[hc & (YY == oy + 7)] = 0
        cv.paste(hc, t, R["cloth"])
        if back:
            kn = m_poly([(cx - 2, oy + 6), (cx + 3, oy + 6), (cx + 1, oy + 11)])
            cv.paste(kn, shade_rows(kn), R["cloth"])
    elif head in ("kabuto", "kabuto_full"):
        dome = m_ellipse(cx + 0.5, oy + 8.5, 12.5, 11) & (YY <= oy + 8)
        t = shade_rows(dome, lit=0.62, shd=0.3)
        ang = np.degrees(np.arctan2(YY + 0.5 - (oy - 1.5), XX + 0.5 - cx))
        t[dome & ~edges(dome) & ((ang % 14.0) < 1.6) & (YY > oy - 1) & (t >= 1)] = 1
        cv.paste(dome, t, R["helm"])
        shik = m_poly([(cx - 13, oy + 7), (cx + 14, oy + 7), (cx + 16, oy + (17 if back else 13)),
                       (cx - 15, oy + (17 if back else 13))])
        if not back:
            shik &= ~fb_face_mask(cx, oy, FRONT_FACE)
        paste_armor(cv, shik, R, T)
        if not back:
            for sgn in (-1, 1):                               # fukigaeshi
                fk = m_poly([(cx + sgn * 10, oy + 5), (cx + sgn * 14, oy + 5), (cx + sgn * 14, oy + 10),
                             (cx + sgn * 11, oy + 10)])
                cv.paste(fk, shade_rows(fk), R["armor"])
            crest = T.get("crest", "horns")
            if crest == "horns":
                for sgn in (-1, 1):
                    line(cv, (cx + sgn * 2, oy + 2), (cx + sgn * 7, oy - 7), R["crest"], 2)
            elif crest == "moon":
                mm = m_ellipse(cx + 0.5, oy - 1, 6, 3.8) & ~m_ellipse(cx + 0.5, oy - 2.6, 5, 3.2)
                cv.paste(mm, shade_rows(mm), R["crest"])
            elif crest == "disc":
                dd = m_ellipse(cx + 0.5, oy + 0.5, 2.8, 2.8)
                cv.paste(dd, shade_rows(dd), R["crest"])
    if T.get("hat") == "jingasa":
        hat = m_poly([(cx - 17, oy + 7), (cx + 18, oy + 7), (cx + 12, oy + 3), (cx + 0.5, oy - 3), (cx - 11, oy + 3)])
        t = shade_rows(hat, lit=0.62, shd=0.28)
        for xx in range(cx - 16, cx + 18, 3):
            t[hat & (XX == xx) & (t >= 2) & (YY < oy + 6)] = 1
        t[hat & (YY == oy + 7)] = 0
        cv.paste(hat, t, R["hat"])
        if T.get("hat_lacquer") and not back:
            draw_mon(cv, cx, oy + 2, R, T)
    elif T.get("hat") == "kasa":
        hat = m_poly([(cx - 20, oy + 8), (cx + 21, oy + 8), (cx + 16, oy + 3), (cx + 0.5, oy - 2), (cx - 15, oy + 3)])
        t = shade_rows(hat, lit=0.62, shd=0.28)
        d = np.hypot(XX + 0.5 - (cx + 0.5), (YY + 0.5 - (oy + 12)) * 1.7)
        t[hat & ~edges(hat) & ((d.astype(int) % 3) == 0) & (t >= 2)] = 1
        t[hat & (YY == oy + 8)] = 0
        cv.paste(hat, t, R["hat"])
    elif T.get("hat") == "eboshi":
        eb = m_poly([(cx - 6, oy + 5), (cx + 7, oy + 5), (cx + 6, oy - 5), (cx + 2, oy - 12), (cx - 3, oy - 12),
                     (cx - 6, oy - 5)])
        t = shade_rows(eb, lit=0.66, shd=0.30)
        t[eb & ~edges(eb) & (YY == oy + 3)] = 3
        cv.paste(eb, t, R["dark"])


def draw_fb_body(cv, T, P, R, F, back=False):
    """Legs, torso, arms for the front/back views (symmetric about the hip centre)."""
    cx = P["hip"][0]
    hy = P["hip"][1] + F["bob"]
    sy = int(round(P["sh_b"][1])) + F["bob"] + F.get("dip", 0)
    wide = P.get("wide", 0)
    build = T["build"]
    hw = 7 + wide                                             # shoulder half-width
    # ---- legs / robe: the lifted leg's knee comes toward the camera (raised hem, narrower shin, knee light)
    boot = build in ("heavy", "armored", "armored_light")
    if build in ("robe", "monk"):
        for sgn, lf in ((-1, F["lift"][0]), (1, F["lift"][1])):
            draw_foot_fb(cv, cx + sgn * 4, GROUND - lf, R, "tabi", lifted=lf > 0, back=back)
        sw = F["swing"] * (1 if not back else -1)
        robe = m_poly([(cx - 6 - wide, hy - 1), (cx + 6 + wide, hy - 1), (cx + 9 + wide + sw, GROUND - 3),
                       (cx - 9 - wide + sw, GROUND - 3)])
        t = shade_rows(robe)
        t[robe & (XX == cx + (1 if sw > 0 else 0)) & (YY > hy + 2)] = 1
        paste_cloth(cv, robe, t, R["lower"], T, R, "lower")
        hem = robe & (YY >= GROUND - 6)
        cv.paste(hem, shade_rows(hem), R["accent"])
    else:
        for sgn, lf in ((-1, F["lift"][0]), (1, F["lift"][1])):
            lx = cx + sgn * (4 - (0.6 if lf else 0))           # the swinging leg tucks in a little
            foot_y = GROUND - lf
            ky = hy + (GROUND - hy) * 0.5 - lf * 0.7           # knee height (rises with the step)
            if build == "strongman":                           # wide-set muscular legs
                ms = T.get("mass", 1.0)
                lx = cx + sgn * (4.8 + wide * 0.4 - (0.6 if lf else 0))
                smooth_limb(cv, [(lx - sgn * 0.8, hy + 1), (lx + sgn * 0.3, ky), (lx, foot_y - 2)],
                            [4.4 * ms, 3.3 * ms - 0.15 * lf, 2.0 * ms], R["skin"],
                            bulges=[(0, 0.42, -0.9 * sgn * ms, 3.6 * ms), (1, 0.3, 0.9 * sgn * ms, 2.7 * ms)])
                draw_foot_fb(cv, lx, foot_y, R, "bare", lifted=lf > 0, back=back)
                continue
            if build == "sumai":                               # wide-set legs, knees bowed out (shiko stance)
                lx = cx + sgn * (6.5 + wide * 0.5 - (0.8 if lf else 0))
                kx = lx + sgn * 1.5
                m, t = sculpt([hf_capsule((lx - sgn * 1.0, hy + 1), (kx, ky), 5.4, 4.2),
                               hf_ellipse(kx - sgn * 0.5, ky - 4, 4.6, 4.4, 1.05),
                               hf_capsule((kx, ky), (lx, foot_y - 2), 3.9 - 0.15 * lf, 2.8),
                               hf_ellipse(kx - sgn * 0.2, ky + 4, 3.6, 3.4)], groups=[0, 0, 1, 1])
                cv.paste(m, t, R["skin"])
                draw_foot_fb(cv, lx + sgn * 0.5, foot_y, R, "bare", lifted=lf > 0, back=back)
                continue
            if build == "peasant":
                leg = m_capsule((lx, hy + 2), (lx, ky), 2.1, 2.0)[0] | m_capsule((lx, ky), (lx, foot_y - 2),
                                                                             2.0 - 0.15 * lf, 1.7)[0]
                cv.paste(leg, shade_rows(leg), R["skin"])
                wr = (np.abs(XX + 0.5 - lx) <= 2.2 - 0.15 * lf) & (YY >= ky + 2) & (YY <= foot_y - 3)
                t = shade_rows(wr)
                t[wr & ((XX + YY) % 3 == 0) & (t >= 2)] = 1
                cv.paste(wr, t, R["lower"])
                if lf:
                    cv.px_on(lx, ky, R["skin"][4])
                draw_foot_fb(cv, lx, foot_y, R, "bare", lifted=lf > 0, back=back)
                continue
            w_top, w_hem = 3.5 + wide * 0.3, 4.5 + wide * 0.3 - 0.4 * lf
            leg = m_poly([(lx - w_top, hy + 1), (lx + w_top, hy + 1), (lx + w_hem, foot_y - 2),
                          (lx - w_hem, foot_y - 2)])
            t = shade_rows(leg)
            for px in (lx - 2, lx + 1):
                t[leg & (XX == int(px)) & (YY > hy + 4) & (t >= 2)] = 1
            if lf and not back:                                # the knee pushing the cloth forward
                kn = leg & (np.hypot(XX + 0.5 - lx, (YY + 0.5 - ky) * 1.4) < 2.2)
                t[kn & (t >= 1)] = np.minimum(t[kn & (t >= 1)] + 1, 4)
            hemrow = leg & (YY >= foot_y - 3)
            t[hemrow & (t >= 2)] -= 1
            paste_cloth(cv, leg, t, R["lower"], T, R, "lower")
            if boot:
                sg = (np.abs(XX + 0.5 - lx) <= 2.5 - 0.2 * lf) & (YY >= ky + 1) & (YY <= foot_y - 3)
                tt = shade_rows(sg)
                tt[sg & (YY % 2 == 0) & ~edges(sg) & (tt >= 2)] = 1
                cv.paste(sg, tt, R["armor"] if build != "armored_light" else R["dark"])
            draw_foot_fb(cv, lx, foot_y, R, "boot" if boot else "tabi", lifted=lf > 0, back=back)
    # ---- torso
    bottom = hy + (7 if build == "peasant" else 1)
    ct = neck_top(P) + 3                                  # collar row, on the neck's base
    sy2 = sy                                              # the (lowered) shoulder line; the torso slopes up to the collar
    tor = m_poly([(cx - 3, ct), (cx + 3, ct), (cx + hw, sy2), (cx + 6 + wide, bottom),
                  (cx - 6 - wide, bottom), (cx - hw, sy2)])
    if build == "round":
        tor |= m_ellipse(cx + 0.5, hy - 4, 8 + wide, 6)
    if build == "strongman":
        strong_torso_fb(cv, T, R, cx, ct, sy, hy, hw, wide, back)
    elif build == "sumai":
        sumai_torso_fb(cv, T, R, cx, ct, sy, hy, hw, wide, back)
    elif build == "heavy":
        paste_armor(cv, tor, R, T)
        ks = m_poly([(cx - 8 - wide, hy), (cx + 8 + wide, hy), (cx + 10 + wide, hy + 10), (cx - 10 - wide, hy + 10)])
        t = shade_rows(ks)
        t, lm = lames(ks, t)
        for xx in range(cx - 9 - wide, cx + 11 + wide, 5):
            t[ks & (XX == xx)] = 0
        cv.paste(ks, t, R["armor"])
        if not back:
            draw_mon(cv, cx, sy + 5, R, T)
    else:
        paste_cloth(cv, tor, shade_rows(tor), R["top"], T, R, "top")
        if not back:                                          # crossed collar V
            for k in range(0, 9):
                cv.px(cx - 3 + k * 0.4, ct + k, R["collar"][2])
                cv.px(cx + 3 - k * 0.4, ct + k, R["collar"][3])
        ob = tor & (YY >= hy - 3) & (YY <= hy - 1)
        if build == "peasant":
            ob = tor & (YY == hy - 1)
            cv.paste(ob, np.zeros((FH, FW), int) + 2, R["straw"])
        else:
            t = shade_rows(ob)
            t[ob & (YY == hy - 2) & ~edges(ob)] = 3
            cv.paste(ob, t, R["accent"])
            if back:                                          # obi knot at the back
                kn = m_poly([(cx - 4, hy - 4), (cx + 4, hy - 4), (cx + 3, hy + 1), (cx - 3, hy + 1)])
                cv.paste(kn, shade_rows(kn), R["accent"])
        if build in ("armored", "armored_light"):
            ch = tor & (YY >= sy + 2) & (YY <= hy - 5)
            paste_armor(cv, ch, R, T)
            ks = m_poly([(cx - 7, hy), (cx + 7, hy), (cx + 8, hy + 6), (cx - 8, hy + 6)])
            t = shade_rows(ks)
            t, lm = lames(ks, t)
            cv.paste(ks, t, R["armor"])
        if T.get("haori"):
            hm = m_poly([(cx - 3, ct), (cx + 3, ct), (cx + hw + 1, sy2), (cx + 8 + wide, hy + 6),
                         (cx - 8 - wide, hy + 6), (cx - hw - 1, sy2)])
            if not back:
                hm &= ~((np.abs(XX + 0.5 - cx) < 2.2) & (YY > ct + 1))
            paste_cloth(cv, hm, shade_rows(hm), R["haori"], T, R, "haori")
            if T.get("trim") == "fur":
                fur = hm & ((YY >= hy + 5) | ((np.abs(XX + 0.5 - cx) < 3.4) & ~back))
                cv.paste(fur, shade_rows(fur, dither=False), R["fur"])
            if back:
                draw_mon(cv, cx, sy + 5, R, T)
        elif back and build not in ("peasant", "monk"):
            draw_mon(cv, cx, sy + 5, R, T)
        if build == "monk" and not back:
            sash = tor & (np.abs((XX - (cx - hw)) - (YY - sy) * 1.1) < 1.6)
            cv.paste(sash, shade_rows(sash), R["accent"])
    if T.get("cloak"):
        cp = m_poly([(cx - 4, ct), (cx + 4, ct), (cx + hw + 2, sy2), (cx + hw + 3, hy - 1),
                     (cx - hw - 3, hy - 1), (cx - hw - 2, sy2)])
        if not back:
            cp &= ~((np.abs(XX + 0.5 - cx) < 4) & (YY > sy + 1))
        cv.paste(cp, shade_rows(cp), R["cloak"])
    if back:
        draw_fb_backprops(cv, T, P, R, cx, sy, hy)
    # ---- arms hanging at the sides (sleeve + hand), from the sloped shoulder line
    sy = sy2
    for sgn in (-1, 1):
        sx = cx + sgn * hw
        hx, hyy = cx + sgn * (hw + 2), hy + 3 + (F["swing"] * sgn if F["swing"] else 0)
        whand = sgn == (1 if back else -1) and T["weapon"] in LONG_W
        if F.get("fold") and not whand:                   # bowing: the hands slide to the front of the thighs
            hx, hyy = cx + sgn * (hw + 2 - 2 * F["fold"]), hy + 3 + F["fold"]
        gest = F.get("gest")
        if gest and sgn == (1 if not back else -1) and gest != (0, 0):   # the free (left) hand gestures
            hx, hyy = cx + sgn * (hw - 1) + gest[0], hy + 3 + gest[1]
        if build == "strongman":                           # arms hanging clear of the body
            ms = T.get("mass", 1.0)
            ax, ay = cx + sgn * (hw + 3.5), hyy
            el_ = (sx + sgn * 1.8, (sy + ay) / 2 + 0.5)
            smooth_limb(cv, [(sx, sy + 1), el_, (ax, ay)], [3.2 * ms, 2.5 * ms, 1.9 * ms], R["skin"],
                        bulges=[(0, 0.05, 0.0, 3.4 * ms), (0, 0.5, 0.9 * sgn * ms, 2.6 * ms),
                                (1, 0.28, -0.4 * sgn * ms, 2.5 * ms)])
            hm = m_ellipse(ax + 0.5, ay + 1.5, 2.1, 2.1)
            cv.paste(hm, shade_rows(hm), R["skin"])
            continue
        if build == "sumai":                               # thick arms held out from the belly
            ax, ay = cx + sgn * (hw + 4.5), hyy - 1
            sumai_arm(cv, T, (sx, sy + 1), (sx + sgn * 3.2, (sy + ay) / 2 + 1), (ax, ay), R, back=False)
            hm = m_ellipse(ax + 0.5, ay + 1.5, 2.4, 2.4)
            cv.paste(hm, shade_rows(hm), R["skin"])
            continue
        elif build == "monk":
            arm = m_capsule((sx, sy + 1), (hx, hyy), 2.0, 1.6)[0]
            cv.paste(arm, shade_rows(arm), R["skin"])
            if T.get("tattoo"):
                tattoo(cv, arm, R)
        elif build == "heavy":
            arm = m_capsule((sx, sy + 1), (hx, hyy), 2.6, 2.2)[0]
            cv.paste(arm, shade_rows(arm), R["dark"])
            sd = m_poly([(sx - 4, sy - 2), (sx + 4, sy - 2), (sx + 4 + sgn, sy + 7), (sx - 4 + sgn, sy + 7)])
            paste_armor(cv, sd, R, T)
        else:
            sl = R["haori"] if T.get("haori") else R["top"]
            key = "haori" if T.get("haori") else "top"
            arm = m_poly([(sx - 2.5, sy), (sx + 2.5, sy), (hx + 3, hyy - 2), (hx - 3, hyy - 2)])
            paste_cloth(cv, arm, shade_rows(arm), sl, T, R, key)
            if build == "armored" and sgn > 0 and not back:
                sd = m_poly([(sx - 3, sy - 2), (sx + 3, sy - 2), (sx + 4, sy + 5), (sx - 2, sy + 5)])
                paste_armor(cv, sd, R, T)
        hand = m_ellipse(hx + 0.5, hyy + 0.5, 1.9, 1.9)
        cv.paste(hand, shade_rows(hand), R["dark"] if build == "heavy" else R["skin"])


def draw_fb_backprops(cv, T, P, R, cx, sy, hy):
    for p in props(T):
        if p == "mapcase":
            line(cv, (cx - 8, sy - 2), (cx + 7, hy + 2), R["wood"], 4)
            cap = m_ellipse(cx - 7.5, sy - 1.5, 2.2, 2.2)
            cv.paste(cap, shade_rows(cap), R["accent"])
        elif p == "quiver":
            line(cv, (cx + 6, sy - 4), (cx - 3, hy + 1), R["wood"], 4)
            for k in range(3):
                cv.px(cx + 5 + k, sy - 6, R["collar"][3])
        elif p == "basket":
            b = m_poly([(cx - 6, sy), (cx + 6, sy), (cx + 5, hy - 1), (cx - 5, hy - 1)])
            t = shade_rows(b)
            for yy in range(sy, hy, 2):
                t[b & (YY == yy) & (t >= 2)] = 1
            cv.paste(b, t, R["straw"])
        elif p in ("swordsback", "nodachi_back"):
            line(cv, (cx + 5, sy - 8), (cx - 6, hy + 4), R["dark"], 2)


def draw_fb_weapon(cv, T, P, R, F, back=False):
    w = T["weapon"]
    cx = P["hip"][0]
    hw = 7 + P.get("wide", 0)
    hx = cx + (hw + 2) * (1 if back else -1)                  # the right hand: viewer's left from the front
    hy = P["hip"][1] + F["bob"] + 3
    if w in LONG_W:
        top, bot = hy - 22, min(GROUND - 1, hy + 13)
        if w == "yumi":
            pts = [(hx + 4 * math.sin(math.pi * k / 10) * (-1 if back else 1), top + 3 + (bot - top - 3) * k / 10)
                   for k in range(11)]
            for a, b in zip(pts[:-1], pts[1:]):
                line(cv, a, b, R["wood"], 2)
            line(cv, pts[0], pts[-1], R["collar"], 1, hi=False)
            return
        pal = R["iron"] if w == "tetsubo" else R["wood"]
        line(cv, (hx, top), (hx, bot), R["wood"], 2)
        if w == "yari":
            bl = m_poly([(hx - 1.5, top), (hx + 2.5, top), (hx + 0.5, top - 6)])
            cv.paste(bl, shade_rows(bl), R["metal"])
            tas = m_ellipse(hx + 0.5, top + 2, 1.6, 2.0)
            cv.paste(tas, shade_rows(tas), R["accent"])
        elif w == "naginata":
            bl = m_poly([(hx - 1, top), (hx + 2, top), (hx + 3, top - 7), (hx + 1, top - 9)])
            cv.paste(bl, shade_rows(bl), R["metal"])
        elif w == "shakujo":
            ring = m_ellipse(hx + 0.5, top - 3, 3.4, 3.4) & ~m_ellipse(hx + 0.5, top - 3, 1.9, 1.9)
            cv.paste(ring, shade_rows(ring), R["metal"])
        elif w == "tetsubo":
            hd = m_capsule((hx, top - 2), (hx, top + 12), 3.0, 2.3)[0]
            cv.paste(hd, shade_rows(hd), pal)
            for yy in range(top, top + 12, 3):
                cv.px(hx - 3, yy, R["metal"][3]), cv.px(hx + 3, yy, R["metal"][3])
        elif w == "nodachi":
            line(cv, (hx, top), (hx, top + 8), R["dark"], 2)
            line(cv, (hx, top - 18), (hx, top), R["rust"] if T.get("rusty") else R["metal"], 2)
        elif w == "bo":
            for yy in (top, bot):
                c = m_ellipse(hx + 0.5, yy + 0.5, 1.4, 1.4)
                cv.paste(c, shade_rows(c), R["accent"])
    else:
        hip = P["hip"]
        if w in ("katana",) or "daisho" in props(T) or "saya" in props(T):
            sx = cx + (-6 if not back else 6)
            if not back:                                          # hilts at the left hip (viewer's right)
                line(cv, (cx + 5, hip[1] - 3), (cx + 9, hip[1] - 7), R["dark"], 2, hi=False)
                cv.px(cx + 5, hip[1] - 3, R["accent"][3])
            else:
                line(cv, (cx + 4, hip[1]), (cx + 11, hip[1] + 6), R["dark"], 2, hi=False)
        if w == "tanto":
            line(cv, (hx, hy), (hx, hy + 6), R["metal"], 1)
        elif w == "fan":
            line(cv, (hx, hy - 1), (hx, hy + 5), R["dark"], 2)
        elif w == "nunchaku":                                     # one stick in the hand, one hanging on its chain
            line(cv, (hx, hy - 1), (hx, hy + 4), R["wood"], 2)
            cv.px(hx, hy + 5, R["metal"][2])
            line(cv, (hx, hy + 6), (hx + (1 if back else -1), hy + 11), R["wood"], 2)
        elif w == "kama":
            line(cv, (hx, hy - 2), (hx, hy + 6), R["wood"], 2)
            line(cv, (hx, hy - 2), (hx + (3 if back else -3), hy - 3), R["metal"], 1)


def compose_fb(T, kind, i, back=False):
    global NECK_UP
    NECK_UP = NECK_FB
    P = stature(T, build_pose(T, pose("idle", 0, "thrust")))
    F = fb_pose(kind, i)
    P["head"] = (0, P["head"][1] + F["bob"] + F.get("hdy", 0))
    P["sway"] = int(round(F["swing"]))
    P["expr"] = F.get("expr")
    R = palette(T)
    cv = Canvas()
    hb = Canvas()
    if not back:
        if T.get("sashimono"):
            draw_sashimono(cv, T, P, R, "front")
        draw_fb_body(cv, T, P, R, F, back=False)
        draw_neck(cv, T, P, R, front=True)
        draw_front_head(hb, T, P, R, back=False)
        over(cv.col, scaled_head(hb.col, P))
        if kit_ok(T, P):
            stamp_face(cv, T, P, R, front=True)
        else:
            restamp_front_eyes(cv, T, P, R)
        draw_fb_weapon(cv, T, P, R, F, back=False)
    else:
        draw_fb_body(cv, T, P, R, F, back=True)
        draw_neck(cv, T, P, R, front=True)
        draw_front_head(hb, T, P, R, back=True)
        over(cv.col, scaled_head(hb.col, P))
        hang = Canvas()                                           # hanging hair over the back
        ox, oy = head_origin(P)
        c = ox + 15
        hs = T["hairstyle"]
        m = np.zeros((FH, FW), bool)
        if hs == "ponytail":
            m |= m_capsule((c, oy + 6), (c + F["swing"], oy + 26), 3.4, 1.6)[0]
        elif hs in ("long", "long_topknot", "mane"):
            m |= m_poly([(c - 9, oy + 14), (c + 10, oy + 14), (c + 9 + F["swing"], oy + 32), (c - 8 + F["swing"], oy + 32)])
            m = zigzag_hem(m)
        if m.any():
            t = shade_hair(m, P, c, oy + 10, hanging=True)
            hang.paste(m, t, R["hair"])
            over(cv.col, scaled_head(hang.col, P))
        if T.get("sashimono"):
            draw_sashimono(cv, T, P, R, "back")
        draw_fb_weapon(cv, T, P, R, F, back=True)
    outline_outer(cv)
    return cv.col


def restamp_front_eyes(cv, T, P, R):
    if T.get("eyes", "normal") != "normal" or T.get("mask") in ("porcelain", "reed", "noh"):
        return
    ox, oy = head_origin(P)
    ax, ay = head_anchor(P)
    cx = ox + 15
    sc = lambda x, y: (int(round(ax + (x - ax) * HEAD_SCALE)), int(round(ay + (y - ay) * HEAD_SCALE)) - NECK_UP)  # noqa
    K, W, er = FIXED["eyek"], FIXED["white"], R["eye"]
    for sgn in (-1, 1):
        ex, ey = sc(cx + sgn * 3.5 - 1, oy + 12)
        cv.px(ex, ey, K), cv.px(ex + 1, ey, K), cv.px(ex + 2, ey, K)
        cv.px(ex, ey + 1, er[1]), cv.px(ex + 1, ey + 1, er[2]), cv.px(ex + 2, ey + 1, er[1])
        cv.px(ex + (2 if sgn < 0 else 0), ey + 1, W)
        cv.px(ex + 1, ey + 2, er[3])


def ground_shadow(img, x0=28 + CX):  # body centre = FW / 2
    out = img.copy()
    sh = m_ellipse(x0, GROUND + 0.5, 11, 2.0)
    blank = out[..., 3] == 0
    out[sh & blank] = (0, 0, 0, 70)
    return out


FB_KINDS = ("fidle", "fwalk", "bidle", "bwalk", "fwalk8", "bwalk8", "ftalk", "fnod", "frei", "bnod", "brei")
V4_KINDS = ("idle8", "walk8", "run", "chant", "item", "collapse", "victory2", "talk", "nod", "rei", "seiza",
            "seiza_rei", "think", "surprise", "laugh") + ATTACKS


LYING_KO = True             # 2026-11-07 (user's reference DEAD row): KO lies flat on the ground, not kneeling


def lying(T):
    """KO: the staggering collapse pose turned a quarter backward (a lossless 90-degree turn of the pixels), laid on
    the ground: head toward the back (west), feet toward the front."""
    T2 = dict(T)
    T2.pop("sashimono", None)                              # the banner has fallen away
    P = base_pose()                                        # laid out straight: feet together, arms along the sides
    hx, hy = P["hip"]
    P["ft_f"], P["ft_b"] = (hx + 1.5, 56), (hx - 1.0, 56)
    P["ha_f"], P["el_f"] = (P["sh_f"][0] + 0.5, hy + 6), (P["sh_f"][0] + 0.5, hy)   # straight down the sides
    P["ha_b"], P["el_b"] = (P["sh_b"][0] - 0.5, hy + 6), (P["sh_b"][0] - 0.5, hy)
    P["sheathed"] = True                                   # (the weapon is drawn on the ground below)
    P["expr"] = "pain"
    P["grip2"], P["open_hand"] = False, True
    P["kneel"] = True                                      # (skips the crouch solver: the knees stay straight)
    for kn, ft in (("kn_f", "ft_f"), ("kn_b", "ft_b")):
        P[kn] = ((hx + P[ft][0]) / 2 + 0.3, (hy + 1 + 56 - ANKLE_UP) / 2)
    P = _finish(P)
    img = compose(T2, P)
    a = img[..., 3] > 0
    ys, xs = np.nonzero(a)
    crop = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rot = np.rot90(crop, 1)                                # counter-clockwise: the head falls back to the left
    h, w = rot.shape[:2]
    out = np.zeros((FH, FW, 4), np.uint8)
    x0 = int(round(BODY_X - w / 2)) - 2
    y0 = GROUND - h
    x0 = max(0, min(FW - w, x0))
    y0 = max(0, y0)
    w_ = T["weapon"]
    if w_ != "none" and wfamily(w_) not in ("fist",):     # the weapon lies flat on the ground beside the body
        Pw = rig_arms(T2, rig_legs(T2, stature(T2, build_pose(T2, _finish(base_pose())))))
        Pw.update(wgrip=(BODY_X + 2, GROUND - 1.5), wang=0.0, wlay=(0, 0), sheathed=False, smear=False, bow=None)
        wc = Canvas()
        draw_weapon(wc, T2, Pw, palette(T2))
        out = wc.col.copy()
    sub = rot[:FH - y0, :FW - x0]
    m = sub[..., 3] > 0
    out[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]][m] = sub[m]
    return out


def frame(T, kind, i):
    if LYING_KO and (kind == "ko" or (kind == "collapse" and i == 3)):
        return ground_shadow(lying(T))
    if kind in FB_KINDS:
        return ground_shadow(compose_fb(T, kind[1:], i, back=kind[0] == "b"))
    if kind in V4_KINDS:
        return ground_shadow(compose(T, mark_upright(T, pose_v4(T, kind, i), kind)))
    style = STYLE.get(T["weapon"], "thrust")
    if kind in ("idle", "victory") and T.get("idle"):
        style = T["idle"]
    return ground_shadow(compose(T, mark_upright(T, pose(kind, i, style, spear=T["weapon"] in ("yari", "naginata")), kind)))


def sheet(T):
    sh = np.zeros((FH * ROWS, FW * COLS, 4), dtype=np.uint8)
    for n, (kind, i) in enumerate(FRAMES):
        r, c = n // COLS, n % COLS
        sh[r * FH:(r + 1) * FH, c * FW:(c + 1) * FW] = frame(T, kind, i)
    return Image.fromarray(sh, "RGBA")


# ------------------------------------------------------------------------------------------- equipment looks
# Look keys: weapon by the item's eqtype (type.json: 0 Unarmed 1 Tanto 2 Katana 3 Yari 5 Bo 6 Yumi 7 Tetsubo; a
# weapon's "rt_look" overrides, e.g. W142 the gaijin musket), head item by the armour's "rt_look" ("" = nothing on the
# head: the traveler's own headwear). Ids are fixed: EP(2000 + traveler*64 + weapon*8 + hat), never reused.
LOOK_WEAPONS = ["none", "tanto", "katana", "yari", "bo", "yumi", "tetsubo", "musket"]
LOOK_HATS = ["", "jingasa", "kasa", "kabuto", "eboshi", "hachimaki"]
LOOK_EXTRA = {"gendo": ["musket"]}                 # weapon looks only one traveler can come by
LOOK_BASE_EP = 2000
EQTYPE_LOOK = {0: "none", 1: "tanto", 2: "katana", 3: "yari", 4: "none", 5: "bo", 6: "yumi", 7: "tetsubo"}
PLUGIN_DIR = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "plugin", "rokugan")
PIDS = ["P100", "P101", "P102", "P103", "P104", "P105", "P106", "P107"]


def base_look(T):
    return {"shakujo": "bo"}.get(T["weapon"], T["weapon"]), ""


def look_variant(T, wkey, hat):
    """The traveler redrawn holding another weapon type and / or wearing a head item."""
    V = json.loads(json.dumps(T))
    for k, v in T.items():                                 # (tuples come back from json as lists)
        if isinstance(v, tuple):
            V[k] = v
    w = wkey
    if wkey == "bo" and T["weapon"] == "shakujo":
        w = "shakujo"                                      # Haruki's staff is his ringed shakujo
    V["weapon"] = w
    if wfamily(w) != "blade":
        V.pop("idle", None)
        if V.get("primary") == "atk_draw":
            V.pop("primary")
    elif w == "katana" and not set(V.get("props") or []) & {"saya", "daisho"}:
        V["props"] = list(V.get("props") or []) + ["saya"]   # somewhere to put the blade away
    if hat:
        V.pop("hat", None)
        V.pop("hat_col", None)
        if V.get("head") == "hachimaki":
            V.pop("head")
        if hat == "jingasa":
            V.update(hat="jingasa", hat_col=(150, 46, 40), hat_lacquer=True)
        elif hat == "kasa":
            V.update(hat="kasa", hat_col=(208, 178, 110))
        elif hat == "kabuto":
            V.update(head="kabuto", crest="disc", helm=tuple(T.get("armor", (84, 86, 98))),
                     crest_col=(226, 190, 80))
        elif hat == "eboshi":
            V.update(hat="eboshi")
        elif hat == "hachimaki":
            V.update(head="hachimaki", band=(238, 234, 226))
    return V


def look_combos(ti, T):
    """(look key, ep id, weapon, hat) for every combination; the traveler's own look keeps EP200+."""
    out = []
    bw, _ = base_look(T)
    for wi, w in enumerate(LOOK_WEAPONS):
        if w == "musket" and w not in LOOK_EXTRA.get(T["key"], []):
            continue
        for hi, h in enumerate(LOOK_HATS):
            ep = "EP%03d" % (200 + ti) if (w, h) == (bw, "") else "EP%d" % (LOOK_BASE_EP + ti * 64 + wi * 8 + hi)
            out.append(("%s|%s" % (w, h), ep, w, h))
    return out


def sheet_entry(tmpl, T, name, fname, memo):
    e = json.loads(json.dumps(tmpl))
    e.update({"name": {"en": name, "ja": name}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
              "aniuv": [COLS, ROWS], "memo": memo,
              "gndpos": [0.5, (FH - GROUND - 1) / FH], "atkpos": [0.25, 0.55], "cntpos": [0.5, 0.6],
              "scale": 1.45 * CAST_SCALE * HUMAN_SCALE, "flipx": True})
    e["animap"] = [{"id": k, "st": v[0], "en": v[1], "spd": v[2], "loop": v[3], "replay": not v[3]}
                   for k, v in animap_for(T).items()]   # loops must not restart on repeat requests
    return e


def write_look_table(tables):
    lines = ["//\tGENERATED by tools/gen_sprites2d.py (write_look_table): do not edit by hand.",
             "//\tTraveler look table: player id -> { \"<weapon look>|<head look>\" : enemy_pic id }.",
             "//\tWeapon look = the weapon's eqtype (or its rt_look); head look = the head item's rt_look (\"\" = none).",
             "::Rokugan.LOOK_EQTYPE <- { %s };" % ", ".join("[%d] = \"%s\"" % kv for kv in sorted(EQTYPE_LOOK.items())),
             "::Rokugan.LOOKS <- {"]
    for pid, rows in tables:
        body = ", ".join("[\"%s\"] = \"%s\"" % (k, ep) for k, ep in rows)
        lines.append("\t%s = { %s }," % (pid, body))
    lines.append("};")
    path = os.path.join(PLUGIN_DIR, "RokuganLookData.sk")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", path)


def main():
    args = sys.argv[1:]
    base_only = "--base-only" in args
    only = set(a for a in args if not a.startswith("--"))
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    os.makedirs(PREVIEW, exist_ok=True)
    strips, tables = [], []
    show = [BLOCK_AT["idle8"][0], BLOCK_AT["walk8"][0] + 2, BLOCK_AT["run"][0] + 1, BLOCK_AT["ready"][0]] + \
        [BLOCK_AT[a][0] + 3 for a in ATTACKS] + [BLOCK_AT["rei"][0] + 2, BLOCK_AT["victory2"][0] + 2]
    for idx, T in enumerate(TRAVELERS):
        combos = look_combos(idx, T)
        tables.append((PIDS[idx], [(k, ep) for k, ep, _, _ in combos]))
        if only and T["key"] not in only:
            continue
        sh = sheet(T)
        fname = "trav_%s" % T["key"]
        sh.save(os.path.join(PIC, fname + ".png"), optimize=True)
        j["EP%03d" % (200 + idx)] = sheet_entry(tmpl, T, T["name"], fname,
                                                "traveler sprite v4 (tools/gen_sprites2d.py)")
        strip = Image.new("RGBA", (FW * len(show), FH), (0, 0, 0, 0))
        for n, fi in enumerate(show):
            strip.paste(sh.crop(((fi % COLS) * FW, (fi // COLS) * FH, (fi % COLS + 1) * FW, (fi // COLS + 1) * FH)),
                        (n * FW, 0))
        strips.append(strip)
        print("done", T["key"])
        if base_only:
            continue
        bw, _ = base_look(T)
        for key, ep, w, h in combos:
            if (w, h) == (bw, ""):
                continue
            V = look_variant(T, w, h)
            vname = "trav_%s__%s_%s" % (T["key"], w, h or "own")
            sheet(V).save(os.path.join(PIC, vname + ".png"), optimize=True)
            j[ep] = sheet_entry(tmpl, V, T["name"], vname,
                                "traveler look %s (tools/gen_sprites2d.py look_variant)" % key)
        print("  looks", T["key"], len(combos) - 1)
    write_look_table(tables)
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    if strips:
        prev = Image.new("RGBA", (strips[0].width * 4, FH * 4 * len(strips)), (70, 98, 62, 255))
        for r, s in enumerate(strips):
            big = s.resize((s.width * 4, s.height * 4), Image.NEAREST)
            prev.paste(big, (0, r * FH * 4), big)
        prev.save(os.path.join(PREVIEW, "sprites2d.png"))


if __name__ == "__main__":
    main()
