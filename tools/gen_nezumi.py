"""Nezumi (ratfolk) sprites, drawn from scratch at the cast's pixel density (gen_sprites2d helpers).
Upright ratlings in the Master Splinter mould: long tapered snout, small rounded ears set back on the skull, beady
eyes, whiskers, digitigrade feet, clawed pink hands, a long bare tail; clothes by role.

  EP351 Squeak            young nezumi in scrappy rags (field NPC + battle guest: full party animation set)
  EP354 Young nezumi      the tribe's young ones (field NPC)
  EP101 Nezumi Warrior    hide armour, red headband, bamboo spear (enemy: idle / attack / hurt rows)
  EP105 Nezumi Shaman     old and grey: robe, bone charms, bone headdress, skull staff (enemy)
  EP357 Stich'Kik         the finale's guide: thin, scarred, one-handed (a bandaged stump), a rope halter (field NPC)

Run after gen_props.py and gen_enemy_art.py:  python -E tools/gen_nezumi.py   (then gen_portraits.py)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402
import gen_enemy_art as ea  # noqa: E402

FW, FH, GROUND = g.FW, g.FH, g.GROUND
XX, YY = g.XX, g.YY
CX0 = 38                                    # body centre x on the canvas (east-facing: snout to the right)

SPECS = {
    "squeak": dict(size=0.78, fur=(150, 126, 106), belly=(206, 186, 160), clothes="rags", cloth=(118, 70, 56),
                   accent=(170, 140, 90), prop=None, age="young"),
    "stichkik": dict(size=0.86, fur=(112, 98, 90), belly=(170, 156, 140), clothes="rags", cloth=(80, 70, 62),
                     accent=(150, 120, 80), prop=None, age="adult", stump=True, scars=True),
    "young": dict(size=0.7, fur=(136, 116, 100), belly=(196, 178, 152), clothes="loin", cloth=(120, 98, 72),
                  accent=(150, 120, 80), prop=None, age="young"),
    "warrior": dict(size=0.96, fur=(118, 92, 72), belly=(186, 160, 130), clothes="hide", cloth=(96, 72, 52),
                    accent=(196, 46, 40), prop="spear", age="adult"),
    "shaman": dict(size=0.92, fur=(150, 146, 150), belly=(214, 210, 206), clothes="robe", cloth=(96, 70, 104),
                   accent=(228, 220, 196), prop="staff", age="old"),
}
PINK = (214, 150, 146)
CLAW = (238, 230, 214)
EYE = (20, 14, 16)


class Pose:
    def __init__(self, **kw):
        self.bob, self.lean, self.step, self.arm, self.tail, self.eyes, self.hand_fwd = 0, 0.0, 0, "rest", 0, "open", 0
        self.__dict__.update(kw)


def frame(spec, P):
    """One east-facing frame. Coordinates are designed at size 1 around the feet (y up = negative) and scaled."""
    S = spec["size"]
    cv = g.Canvas()
    R = {k: g.ramp(v) for k, v in (("fur", spec["fur"]), ("belly", spec["belly"]), ("cloth", spec["cloth"]),
                                   ("accent", spec["accent"]), ("pink", PINK), ("claw", CLAW), ("eye", EYE),
                                   ("wood", (140, 100, 60)), ("bone", (232, 224, 204)), ("metal", g.METAL))}
    old = spec["age"] == "old"
    hunch = 3.0 if old else 1.2

    def at(x, y):
        return (CX0 + x * S, GROUND + (y + P.bob) * S)

    lean = P.lean + hunch
    # --- skeleton (size-1 units)
    hip = (-1.0, -15.5)
    chest = (2.0 + lean * 0.6, -24.0)
    neck = (4.0 + lean, -28.5)
    head = (6.0 + lean * 1.1, -32.5)
    sx = P.step                                            # walk: +near leg forward / -far leg forward
    legs = {"far": (-sx, -2), "near": (sx, 0)}

    # tail: long, thin, bare; sweeps behind and along the ground
    tail = np.zeros((FH, FW), bool)
    for t in np.linspace(0, 1, 40):
        x = hip[0] - 3 - 17 * t
        y = hip[1] + 3 + 13.5 * t - 4.0 * math.sin(t * math.pi) + P.tail * math.sin(t * 6.0) * t
        r = (1.4 - 0.9 * t) * S
        tail |= g.m_ellipse(*at(x, y), max(r, 0.45), max(r, 0.45))
    tt = g.shade_rows(tail, dither=False)
    tt[tail & (((XX + YY) % 3) == 0) & (tt >= 2)] = 1      # ringed scales
    cv.paste(tail, tt, R["pink"])
    cv.keep |= tail                                        # thin: the silhouette pass would blacken it

    def leg(side, dark):
        dx, dz = legs[side]
        hp = (hip[0] + dz * 0.4, hip[1] + 1)
        knee = (hp[0] + 3.5 + dx * 0.5, hp[1] + 6.5)
        hock = (knee[0] - 3.0 + dx * 0.6, knee[1] + 5.0 - (2.0 if dx < 0 and P.step else 0))
        toe = (hock[0] + 5.5 + dx * 0.3, -0.5 - (1.5 if dx < 0 and P.step else 0))
        g.draw_limb(cv, at(*hp), at(*knee), 2.6 * S, 2.1 * S, R["fur"])
        g.draw_limb(cv, at(*knee), at(*hock), 1.8 * S, 1.3 * S, R["fur"])
        ft = g.m_capsule(at(*hock), at(*toe), 1.2 * S, 0.9 * S)[0]
        t = g.shade_rows(ft)
        if dark:
            t[ft & (t >= 2)] -= 1
        cv.paste(ft, t, R["pink"])
        cv.px(*at(toe[0] + 0.8, toe[1]), R["claw"][3])

    leg("far", True)

    def arm(side):
        far = side == "far"
        sh = (chest[0] + (-1.5 if far else 1.0), chest[1] - 2.5)
        if P.arm == "rest":                                # hands folded before the chest (Splinter's stance)
            el, ha = (sh[0] + 1.0, sh[1] + 5.0), (sh[0] + 4.5 + P.hand_fwd, sh[1] + 4.5)
        elif P.arm == "hold":                              # gripping a staff / spear upright in front
            el, ha = (sh[0] + 2.0, sh[1] + 5.0), (sh[0] + 6.5, sh[1] + 2.0 - (1.5 if far else 0))
        elif P.arm == "throw":                             # flung forward (Pocket Sand)
            el, ha = (sh[0] + 4.0, sh[1] + 1.0), (sh[0] + 9.0, sh[1] - 1.0)
        elif P.arm == "windup":
            el, ha = (sh[0] - 3.0, sh[1] + 2.0), (sh[0] - 5.5, sh[1] - 1.0)
        elif P.arm == "up":                                # victory / cheer
            el, ha = (sh[0] + 1.5, sh[1] - 4.0), (sh[0] + 2.5, sh[1] - 8.5)
        else:                                              # "hurt": flung back
            el, ha = (sh[0] - 2.0, sh[1] + 3.0), (sh[0] - 4.0, sh[1] + 5.0)
        sleeve = R["cloth"] if spec["clothes"] == "robe" else R["fur"]
        g.draw_limb(cv, at(*sh), at(*el), 1.8 * S, 1.6 * S, sleeve)
        if not far and spec.get("stump"):                  # Stich'Kik: the hand is gone; a dirty bandage
            ha = (el[0] + (ha[0] - el[0]) * 0.6, el[1] + (ha[1] - el[1]) * 0.6)
            g.draw_limb(cv, at(*el), at(*ha), 1.5 * S, 1.3 * S, R["fur"])
            wrap = g.m_ellipse(*at(*ha), 1.3 * S, 1.2 * S)
            cv.paste(wrap, g.shade_rows(wrap), R["bone"])
            return ha
        g.draw_limb(cv, at(*el), at(*ha), 1.5 * S, 1.2 * S, R["fur"])
        hand = g.m_ellipse(*at(ha[0] + 0.4, ha[1]), 1.3 * S, 1.1 * S)
        t = g.shade_rows(hand)
        if far:
            t[hand & (t >= 2)] -= 1
        cv.paste(hand, t, R["pink"])
        cv.px_on(*at(ha[0] + 1.4, ha[1] + 0.6), R["claw"][3])
        return ha

    far_hand = arm("far")
    # --- torso (fur) + belly
    body = g.m_capsule(at(*hip), at(*chest), 5.2 * S, 4.6 * S)[0] | g.m_ellipse(*at(*chest), 4.6 * S, 4.2 * S)
    cv.paste(body, g.shade_rows(body), R["fur"])
    bel = g.m_capsule(at(hip[0] + 2.5, hip[1] - 1), at(chest[0] + 2.0, chest[1] + 1.5), 2.6 * S, 2.2 * S)[0] & body
    cv.paste(bel, g.shade_rows(bel, outline=False), R["belly"])
    # --- clothes by role
    c = spec["clothes"]
    if c == "robe":                                        # Splinter's robe: crossed collar, sash, long hem
        robe = g.m_poly([at(chest[0] - 4.5, chest[1] - 2.5), at(chest[0] + 4.0, chest[1] - 2.0),
                         at(hip[0] + 7.0, -5.0), at(hip[0] - 6.5, -5.5)])
        t = g.shade_rows(robe)
        for kx in (-3, 0, 3):
            t[robe & (np.abs(XX + 0.5 - at(hip[0] + kx, 0)[0]) < 0.6) & (YY > at(0, hip[1])[1]) & (t >= 2)] = 1
        cv.paste(robe, t, R["cloth"])
        col = g.m_capsule(at(chest[0] - 1.5, chest[1] - 2.5), at(chest[0] + 2.5, chest[1] + 3.0), 0.8 * S)[0] & robe
        cv.paste(col, np.zeros((FH, FW), int) + 3, R["cloth"])
        sash = robe & (np.abs(YY + 0.5 - at(0, hip[1] - 2.5)[1]) < 1.0 * S)
        cv.paste(sash, g.shade_rows(sash, outline=False), R["accent"])
        for k in range(4):                                 # bone charms on a cord
            bx, by = at(chest[0] - 1.0 + k * 1.3, chest[1] + 0.8 + (k % 2) * 0.6)
            cv.px(bx, by, R["bone"][4 if k % 2 else 3])
    elif c == "rags":                                      # scrappy vest, ragged edge
        v = body & (YY < at(0, hip[1] + 2)[1]) & ((XX + 0.5) < at(chest[0] + 1.5, 0)[0])
        v &= ~(((XX * 3 + YY) % 7 == 0) & g.edges(v))
        cv.paste(v, g.shade_rows(v), R["cloth"])
        rope = body & (np.abs(YY + 0.5 - at(0, hip[1] - 1.5)[1]) < 0.6)
        cv.paste(rope, np.zeros((FH, FW), int) + 2, R["accent"])
    elif c == "loin":
        lo = body & (YY > at(0, hip[1] - 2.5)[1])
        cv.paste(lo, g.shade_rows(lo), R["cloth"])
    elif c == "hide":                                      # hide cuirass with lacing, loincloth
        cu = body & (YY < at(0, hip[1] - 1)[1])
        t = g.shade_rows(cu)
        t[cu & ((YY % 2) == 0) & ~g.edges(cu) & (t >= 2)] = 1
        cv.paste(cu, t, R["cloth"])
        lo = body & (YY >= at(0, hip[1] - 1)[1])
        cv.paste(lo, g.shade_rows(lo), R["cloth"])
    if spec.get("scars"):                                  # old whip scars across the back and flank
        for k in range(3):
            for t in range(4):
                cv.px_on(*at(hip[0] - 2.5 + k * 2.2 + t * 0.8, hip[1] - 7.5 + k * 1.5 - t * 0.9), R["pink"][4])
    leg("near", False)

    # --- neck, then the head (chibi scale like the human cast): cranium + long tapered snout
    nk = g.m_capsule(at(*chest), at(*head), 2.9 * S, 2.6 * S)[0]
    cv.paste(nk, g.shade_rows(nk), R["fur"])
    HS = 1.35
    hx, hy = head
    _at = at

    S0 = S

    def at(x, y):                                          # head-local scaling about the head centre
        return (CX0 + (hx + (x - hx) * HS) * S0, GROUND + (hy + (y - hy) * HS + P.bob) * S0)

    S = S0 * HS
    cran = g.m_ellipse(*at(hx, hy), 4.9 * S, 4.4 * S)
    snout = g.m_poly([at(hx + 1.0, hy - 3.6), at(hx + 9.6, hy + 0.9), at(hx + 10.2, hy + 1.8), at(hx + 8.6, hy + 2.8),
                      at(hx + 1.5, hy + 3.9)])
    jaw = g.m_poly([at(hx + 1.0, hy + 2.4), at(hx + 7.4, hy + 2.6), at(hx + 6.6, hy + 3.7), at(hx + 1.6, hy + 4.2)])
    headm = cran | snout
    t = g.shade_rows(headm)
    cv.paste(headm, t, R["fur"])
    cv.paste(jaw & ~headm, g.shade_rows(jaw & ~headm), R["belly"])
    muzzle = g.m_poly([at(hx + 4.0, hy + 1.2), at(hx + 9.6, hy + 1.2), at(hx + 8.6, hy + 2.8), at(hx + 4.0, hy + 3.4)])
    mt = g.shade_rows(muzzle & headm, outline=False)
    cv.paste(muzzle & headm, mt, R["belly"] if not old else R["belly"])
    nose = g.m_ellipse(*at(hx + 10.0, hy + 1.4), 1.2 * S, 1.0 * S)
    cv.paste(nose, g.shade_rows(nose, dither=False), R["pink"])
    for k, (ex, ey) in enumerate(((hx - 1.6, hy - 4.0), (hx + 0.4, hy - 4.6))):   # small rounded ears, set back
        er = (2.3 if k else 2.0) * S * (1.4 if spec["age"] == "young" else 1.0)   # the young: big ears
        ear = g.m_ellipse(*at(ex, ey), er, er * 1.15)
        et = g.shade_rows(ear)
        if k == 0:
            et[ear & (et >= 2)] -= 1
        cv.paste(ear, et, R["fur"])
        inner = g.m_ellipse(*at(ex + 0.3, ey + 0.2), er * 0.55, er * 0.7)
        cv.paste(inner & ear, g.shade_rows(inner & ear, outline=False), R["pink"])
        if old and k:
            cv.px_on(*at(ex + 1.5, ey - 1.3), (0, 0, 0))     # a notch: an old fighter's ear
    ex, ey = at(hx + 3.6, hy - 0.9)                         # beady eye with a glint
    if P.eyes == "shut":
        cv.px(ex, ey, R["eye"][2])
        cv.px(ex + 1, ey, R["eye"][2])
    else:
        cv.px(ex, ey, EYE)
        cv.px(ex, ey + 1, EYE)
        cv.px(ex + 1, ey, EYE)
        cv.px_on(ex, ey, (240, 240, 240))
    if old:                                                 # grey brow tufts + long whiskers/beard wisps
        for k in range(3):
            cv.px_on(*at(hx + 2.6 + k * 0.9, hy - 2.2 - k * 0.2), R["belly"][4])
        for k in range(3):
            cv.px(*at(hx + 3.0 - k * 0.6, hy + 4.8 + k * 1.1), R["belly"][3])
    wl = 5.0 if old else 3.6                                # whiskers: two fine light strokes fanning out
    wc = R["belly"][4] if not old else (236, 232, 226)
    for ang in (-28.0, 14.0):
        a = at(hx + 8.2, hy + 1.8)
        b = (a[0] + math.cos(math.radians(ang)) * wl * S, a[1] + math.sin(math.radians(ang)) * wl * S)
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for k in range(1, n + 1):
            x = a[0] + (b[0] - a[0]) * k / n
            y = a[1] + (b[1] - a[1]) * k / n
            yi, xi = int(round(y)), int(round(x))
            if 0 <= yi < FH and 0 <= xi < FW and not cv.col[yi, xi, 3]:
                cv.px(x, y, wc)
                cv.keep[yi, xi] = True
    if spec["prop"] == "spear" or spec["accent"] == (196, 46, 40):
        band = headm & (np.abs(YY + 0.5 - at(0, hy - 2.2)[1]) < 0.55 * S) & ((XX + 0.5) < at(hx + 3.0, 0)[0])
        cv.paste(band, g.shade_rows(band, outline=False), R["accent"])
    if old:                                                 # bone headdress
        for k, bx in enumerate((hx - 2.5, hx - 1.0, hx + 0.5)):
            h = 3.2 if k % 2 else 4.6
            g.line(cv, at(bx, hy - 3.6), at(bx - 0.6, hy - 3.6 - h), R["bone"], 1)

    at, S = _at, S0                                        # back to body space
    # --- near arm + weapon
    if spec["prop"]:
        hx2, hy2 = arm_target = (chest[0] + 7.5, chest[1] - 0.5)
        top = (hx2 + 2.0, hy2 - (22 if spec["prop"] == "spear" else 15))
        bot = (hx2 - 1.0, -1.0)
        if P.arm in ("throw",):
            top, bot = (hx2 + 15, hy2 - 1), (hx2 - 8, hy2 + 2)
        g.line(cv, at(*bot), at(*top), R["wood"], 2)
        if spec["prop"] == "spear":
            tip = g.m_poly([at(top[0] - 1.0, top[1] + 0.8), at(top[0] + 1.0, top[1] + 0.3),
                            at(top[0] + 0.9 + (top[0] - bot[0]) * 0.12, top[1] - 3.2)])
            cv.paste(tip, g.shade_rows(tip), R["metal"])
            cv.keep |= tip
        else:
            sk = g.m_ellipse(*at(top[0], top[1] - 1.2), 2.0 * S, 1.8 * S)  # skull knob
            cv.paste(sk, g.shade_rows(sk), R["bone"])
            cv.px(*at(top[0] + 0.6, top[1] - 1.2), (150, 40, 190))
    arm("near")
    g.outline_outer(cv)
    sh = g.m_ellipse(CX0 + 2, GROUND + 0.5, 9 * S, 1.8)
    cv.col[sh & (cv.col[..., 3] == 0)] = (0, 0, 0, 70)
    return cv.col


def poses(kind, i):
    if kind == "idle":
        return Pose(bob=[0, 0, 1, 1][i], tail=[0, 1, 0, -1][i], hand_fwd=[0, 0, 0.5, 0.5][i])
    if kind == "walk":
        return Pose(step=[3, 0, -3, 0][i], bob=[0, -1, 0, -1][i], tail=[1, 0, -1, 0][i], lean=1.0)
    if kind == "attack":
        return [Pose(arm="windup", lean=-1.5), Pose(arm="throw", lean=2.5, step=2), Pose(arm="throw", lean=2.0, step=2),
                Pose(arm="rest", lean=0.5)][i]
    if kind == "hurt":
        return Pose(arm="hurt", lean=-3.0, eyes="shut", bob=[0, 1][i])
    if kind == "ko":
        return Pose(arm="hurt", lean=-1.0, eyes="shut", bob=4)
    if kind == "victory":
        return Pose(arm="up", bob=[0, -1][i], tail=[1, -1][i])
    return Pose()


def pick(spec):
    """Weapon-holders hold their weapon in every idle frame."""
    def f(kind, i):
        P = poses(kind, i)
        if spec["prop"] and kind in ("idle", "walk"):
            P.arm = "hold"
        return frame(spec, P)
    return f


V4_ALIAS = {"idle8": ("idle", None), "walk8": ("walk", None), "run": ("walk", None), "atk_slash": ("attack", None),
            "atk_thrust": ("attack", None), "atk_overhead": ("attack", None), "atk_draw": ("attack", None),
            "chant": ("attack", 0), "item": ("idle", 0), "collapse": ("hurt", 1), "victory2": ("victory", 0),
            "talk": ("idle", None), "nod": ("idle", 0), "rei": ("idle", 0), "seiza": ("idle", 0),
            "seiza_rei": ("idle", 0), "think": ("idle", 0), "surprise": ("hurt", 0), "laugh": ("victory", 0),
            "fwalk8": ("walk", None), "bwalk8": ("walk", None), "ftalk": ("idle", None), "fnod": ("idle", 0),
            "frei": ("idle", 0), "bnod": ("idle", 0), "brei": ("idle", 0)}


def party_sheet(spec):
    """Squeak's full sheet in the travelers' layout (gen_sprites2d.FRAMES / ANIMAP), from the frames we draw."""
    draw = pick(spec)
    cache = {}

    def fr(kind, i):
        key = (kind, i)
        if key not in cache:
            cache[key] = draw(kind, i)
        return cache[key]
    alias = {"ready": ("idle", 0), "cast": ("attack", 0), "guard": ("hurt", 1), "evade": ("hurt", 1),
             "fidle": ("idle", None), "fwalk": ("walk", None), "bidle": ("idle", None), "bwalk": ("walk", None)}
    sh = np.zeros((FH * g.ROWS, FW * g.COLS, 4), dtype=np.uint8)
    for n, (kind, i) in enumerate(g.FRAMES):
        k2, i2 = kind, i
        if kind in alias:
            k2, j = alias[kind]
            i2 = i if j is None else j
        elif kind.startswith("cast_"):
            k2, i2 = "attack", i
        elif kind in V4_ALIAS:                                 # gen_sprites2d v4 blocks: nearest drawn pose
            k2, j = V4_ALIAS[kind]
            i2 = (i % 4) if j is None else j
        if k2 == "hurt":
            i2 = min(i2, 1)
        if k2 == "victory":
            i2 = min(i2, 1)
        if k2 == "ko":
            i2 = 0
        r, c = n // g.COLS, n % g.COLS
        sh[r * FH:(r + 1) * FH, c * FW:(c + 1) * FW] = fr(k2, i2)
    return Image.fromarray(sh, "RGBA")


def main():
    jpath = os.path.join(g.RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    gnd = [0.5, (FH - GROUND - 1) / FH]
    scale = 1.45 * g.CAST_SCALE
    previews = []
    # Squeak: travelers' layout, so he can stand in the party (Pocket Sand) and walk the field 4 ways
    sq = party_sheet(SPECS["squeak"])
    sq.save(os.path.join(g.PIC, "npc_squeak.png"))
    e = json.loads(json.dumps(tmpl))
    e.update({"name": {"en": "Squeak", "ja": "Squeak"}, "pic3d": "/resource/enemy_pic/npc_squeak.png",
              "aniuv": [g.COLS, g.ROWS], "memo": "nezumi (tools/gen_nezumi.py)", "gndpos": gnd, "scale": scale,
              "flipx": True, "atkpos": [0.25, 0.55], "cntpos": [0.5, 0.6]})
    e["animap"] = [{"id": k, "st": v[0], "en": v[1], "spd": v[2], "loop": v[3], "replay": not v[3]}
                   for k, v in g.ANIMAP.items()]
    j["EP351"] = e
    young = party_sheet(SPECS["young"])
    young.save(os.path.join(g.PIC, "npc_young_nezumi.png"))
    y = json.loads(json.dumps(e))
    y.update({"name": {"en": "Young nezumi", "ja": "Young nezumi"}, "pic3d": "/resource/enemy_pic/npc_young_nezumi.png"})
    j["EP354"] = y
    sk = party_sheet(SPECS["stichkik"])                     # the finale's guide (field NPC, walks 4 ways)
    sk.save(os.path.join(g.PIC, "npc_stichkik.png"))
    z = json.loads(json.dumps(e))
    z.update({"name": {"en": "Stich'Kik", "ja": "Stich'Kik"}, "pic3d": "/resource/enemy_pic/npc_stichkik.png"})
    j["EP357"] = z
    # enemies: idle frames -> gen_enemy_art.animate (idle / attack / hurt rows), east-facing like every enemy
    for epid, key, fname, label in (("EP101", "warrior", "nezumi_warrior", "Nezumi Warrior"),
                                    ("EP105", "shaman", "nezumi_shaman", "Nezumi Shaman")):
        draw = pick(SPECS[key])
        idle = [Image.fromarray(draw("idle", i), "RGBA") for i in range(4)]
        sheet, (cols, rows), animap = ea.animate(idle)
        sheet.save(os.path.join(g.PIC, fname + ".png"))
        x = json.loads(json.dumps(tmpl))
        x.update({"name": {"en": label, "ja": label}, "pic3d": "/resource/enemy_pic/%s.png" % fname,
                  "aniuv": [cols, rows], "animap": animap, "memo": "nezumi (tools/gen_nezumi.py)",
                  "gndpos": gnd, "scale": scale, "flipx": False})
        j[epid] = x
        previews.append(idle[0])
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    strip = Image.new("RGBA", (FW * 8, FH), (70, 98, 62, 255))
    for n, (spec, kind, i) in enumerate((("squeak", "idle", 0), ("squeak", "walk", 0), ("squeak", "walk", 1),
                                         ("squeak", "attack", 1), ("young", "idle", 0), ("warrior", "idle", 0),
                                         ("shaman", "idle", 0), ("stichkik", "idle", 0))):
        im = Image.fromarray(pick(SPECS[spec])(kind, i), "RGBA")
        strip.paste(im, (n * FW, 0), im)
    out = os.path.join(g.PREVIEW, "nezumi.png")
    strip.resize((strip.width * 4, strip.height * 4), Image.NEAREST).save(out)
    print(out)


if __name__ == "__main__":
    main()
