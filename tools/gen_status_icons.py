"""Status-effect icons (user 2026-11-21: "start working on better status effect icons. fists and shields for everything
doesn't explain visually whats going on").

Every condition used to show the stock fist (U+F2C1) or shield (U+F2C2). This draws one 32 px tile per effect into
the engine's user icon atlas, resource/icon/usericon.json + .bin (RPGSystem.sk registerIcon: registerEmoji(.., 2)),
at codepoints U+E400.. (stock atlas: F23F-F83A, vk: EC08-EF1C), and points cond.json "icon" at them. The engine
writes condition icons as text (getConditionString, the battle row "conds" label, popups), so they show everywhere.

The language of a tile:
  pictogram = what it does: blade ATK, shield DEF, flame spell power, ofuda ward spell defence, chevrons Speed,
              afterimage evasion, target accuracy, starburst criticals, curved arrows counter, mountain damage taken
              ... and story effects get their own (net, letter, blood, roots, tattoos ...)
  badge     = green up (helps) / red down (hurts), bottom right
  frame     = gold: a kata / kiho stance (rt_kata); violet: a Void-critical gift; none: everything else
  tile      = the effect's colour; debuffs are a dark tile
Drawn at 8x and downsampled like gen_battleui_art.py.

    python -E tools/gen_status_icons.py            (writes the atlas, patches cond.json icons, preview sheet)
    python -E tools/gen_status_icons.py --check    (preview only)
"""
import io
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project"))
ICONDIR = os.path.join(PROJ, "resource", "icon")
CONDS = os.path.join(PROJ, "data", "cond.json")
PREVIEW = os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "status_icons.png"))
CP0 = 0xE400
OUT_PX, SS = 32, 8
W = OUT_PX * SS
WHITE = (255, 255, 255, 255)
INK = (20, 22, 30, 255)

# ---------------------------------------------------------------- drawing helpers (unit coords: -1..1, y down)


def U(x, y):
    return (W / 2 + x * W * 0.5, W / 2 + y * W * 0.5)


def P(*xy):
    return [U(x, y) for x, y in xy]


def px(v):
    return max(1, int(v * W * 0.5))


def line(d, pts, w, col=WHITE):
    d.line(P(*pts), fill=col, width=px(w), joint="curve")
    for q in (pts[0], pts[-1]):             # round caps
        r = w / 2
        d.ellipse([*U(q[0] - r, q[1] - r), *U(q[0] + r, q[1] + r)], fill=col)


def circ(d, x, y, r, fill=None, outline=None, w=0.0):
    d.ellipse([*U(x - r, y - r), *U(x + r, y + r)], fill=fill, outline=outline, width=px(w) if w else 0)


def arc(cx, cy, r, a0, a1, n=32):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def poly(d, pts, col=WHITE):
    d.polygon(P(*pts), fill=col)


# ---------------------------------------------------------------- pictograms (white on the tile; ~ -0.62..0.62)


def p_blade(d, c=WHITE):                   # a katana: a gently curved edge, a tsuba, a grip
    (x0, y0), (x1, y1) = (-0.26, 0.26), (0.64, -0.64)
    nx, ny = -0.7071, -0.7071                  # the curve bows up-left, the edge faces down-right
    side_a, side_b = [], []
    for i in range(21):
        t = i / 20.0
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        sag = 0.10 * math.sin(math.pi * t * 0.9)
        w = 0.115 * (1 - t ** 3)
        side_a.append((bx + nx * (sag + w), by + ny * (sag + w)))
        side_b.append((bx + nx * (sag - w * 0.7), by + ny * (sag - w * 0.7)))
    poly(d, side_a + side_b[::-1], c)
    line(d, [(-0.40, 0.12), (-0.12, 0.40)], 0.12, c)                                   # tsuba
    line(d, [(-0.30, 0.30), (-0.60, 0.60)], 0.15, c)                                   # grip


def p_shield(d, c=WHITE):
    poly(d, [(0, -0.64), (0.54, -0.44), (0.50, 0.12), (0, 0.66), (-0.50, 0.12), (-0.54, -0.44)], c)


def p_flame(d, c=WHITE):
    poly(d, [(0.02, -0.68), (0.22, -0.34), (0.48, -0.10), (0.48, 0.28), (0.26, 0.58), (-0.26, 0.58), (-0.48, 0.28),
             (-0.44, -0.08), (-0.24, 0.06), (-0.18, -0.36)], c)


def p_ward(d, c=WHITE, bg=None):           # an ofuda: a paper slip with a seal and brush lines
    poly(d, [(-0.32, -0.66), (0.32, -0.66), (0.32, 0.66), (-0.32, 0.66)], c)
    k = bg or INK
    circ(d, 0, -0.30, 0.15, outline=k, w=0.07)
    for y in (0.05, 0.25, 0.45):
        line(d, [(-0.14, y), (0.14, y)], 0.07, k)


def p_speed(d, c=WHITE):
    for x in (-0.42, 0.04):
        line(d, [(x, -0.52), (x + 0.36, 0), (x, 0.52)], 0.16, c)


def p_evade(d, c=WHITE):                   # a figure and two afterimages
    for k, (dx, a) in enumerate(((-0.40, 70), (-0.20, 140), (0.06, 255))):
        col = c[:3] + (a,)
        circ(d, dx + 0.10, -0.40, 0.15, fill=col)
        poly(d, [(dx - 0.06, -0.20), (dx + 0.26, -0.20), (dx + 0.34, 0.24), (dx + 0.18, 0.62), (dx + 0.04, 0.62),
                 (dx + 0.10, 0.26), (dx - 0.12, 0.62), (dx - 0.28, 0.62), (dx - 0.10, 0.18)], col)


def p_target(d, c=WHITE):
    circ(d, 0, 0, 0.56, outline=c, w=0.10)
    circ(d, 0, 0, 0.30, outline=c, w=0.09)
    circ(d, 0, 0, 0.09, fill=c)


def p_star(d, c=WHITE):                    # a critical: an 8-point burst
    pts = []
    for i in range(16):
        r = 0.66 if i % 2 == 0 else 0.26
        a = math.radians(i * 22.5 - 90)
        pts.append((r * math.cos(a), r * math.sin(a)))
    poly(d, pts, c)


def p_counter(d, c=WHITE):                 # two curved arrows chasing each other
    for a0 in (200, 20):
        pts = arc(0, 0, 0.46, a0, a0 + 130)
        line(d, pts, 0.13, c)
        ex, ey = pts[-1]
        a = math.radians(a0 + 130)
        tx, ty = -math.sin(a), math.cos(a)
        nx, ny = math.cos(a), math.sin(a)
        poly(d, [(ex + tx * 0.26, ey + ty * 0.26), (ex + nx * 0.18 - tx * 0.04, ey + ny * 0.18 - ty * 0.04),
                 (ex - nx * 0.18 - tx * 0.04, ey - ny * 0.18 - ty * 0.04)], c)


def p_mountain(d, c=WHITE, bg=None):
    poly(d, [(-0.70, 0.52), (-0.16, -0.50), (0.08, -0.06), (0.26, -0.30), (0.70, 0.52)], c)
    poly(d, [(-0.16, -0.50), (-0.32, -0.20), (-0.16, -0.26), (-0.02, -0.20)], bg or INK)


def p_heart(d, c=WHITE):
    circ(d, -0.24, -0.16, 0.28, fill=c)
    circ(d, 0.24, -0.16, 0.28, fill=c)
    poly(d, [(-0.50, -0.04), (0.50, -0.04), (0, 0.58)], c)


def p_lotus(d, c=WHITE, bg=None):          # calm, no fear: a lotus on still water
    def petal(ang, ln, wd):
        r = math.radians(ang)
        pts = []
        for i in range(25):
            t = i / 24.0
            w = wd * math.sin(math.pi * t) ** 0.8
            pts.append((w, -ln * t))
        pts += [(-x, y) for x, y in reversed(pts[1:-1])]
        return [(0.0 + x * math.cos(r) - y * math.sin(r), 0.30 + x * math.sin(r) + y * math.cos(r)) for x, y in pts]
    k = bg or INK
    for ang, ln, wd in ((-62, 0.62, 0.20), (62, 0.62, 0.20), (-30, 0.80, 0.24), (30, 0.80, 0.24), (0, 0.92, 0.26)):
        poly(d, petal(ang, ln, wd), c)
        d.line(P(*petal(ang, ln, wd)), fill=k, width=px(0.035))
    line(d, [(-0.60, 0.50), (0.60, 0.50)], 0.08, c)
    line(d, [(-0.36, 0.66), (0.36, 0.66)], 0.06, c[:3] + (170,))


def p_eye(d, c=WHITE, bg=None):
    pts = arc(0, 0.62, 0.92, -130, -50) + arc(0, -0.62, 0.92, 50, 130)
    poly(d, pts, c)
    circ(d, 0, 0, 0.20, fill=bg or INK)
    circ(d, 0.06, -0.06, 0.06, fill=c)


def p_falcon_eye(d, c=WHITE, bg=None):
    p_eye(d, c, bg)
    line(d, [(-0.62, -0.42), (-0.10, -0.30), (0.40, -0.46)], 0.09, c)


def p_net(d, c=WHITE):
    for i in range(-2, 3):
        line(d, [(i * 0.26 - 0.30, -0.58), (i * 0.26 + 0.30, 0.58)], 0.06, c)
        line(d, [(i * 0.26 + 0.30, -0.58), (i * 0.26 - 0.30, 0.58)], 0.06, c)
    circ(d, 0, 0, 0.66, outline=c, w=0.08)


def p_letter(d, c=WHITE, bg=None):         # a scandalous letter
    poly(d, [(-0.58, -0.40), (0.58, -0.40), (0.58, 0.44), (-0.58, 0.44)], c)
    line(d, [(-0.54, -0.36), (0, 0.06), (0.54, -0.36)], 0.07, bg or INK)
    poly(d, [(0.20, -0.70), (0.42, -0.70), (0.36, -0.10), (0.26, -0.10)], (255, 214, 64, 255))
    circ(d, 0.31, 0.06, 0.07, fill=(255, 214, 64, 255))


def p_prone(d, c=WHITE):                   # a figure flat on the ground
    circ(d, -0.46, 0.10, 0.15, fill=c)
    poly(d, [(-0.28, 0.02), (0.56, 0.06), (0.58, 0.28), (-0.28, 0.26)], c)
    line(d, [(-0.66, 0.50), (0.66, 0.50)], 0.08, c)
    line(d, [(0.10, -0.60), (0.10, -0.16)], 0.10, c)
    poly(d, [(-0.06, -0.24), (0.26, -0.24), (0.10, -0.06)], c)


def p_broken(d, c=WHITE, bg=None):         # a broken guard (Suki)
    p_shield(d, c)
    line(d, [(0.04, -0.70), (-0.12, -0.20), (0.14, 0.06), (-0.04, 0.70)], 0.12, bg or INK)


def p_taint(d, c=(30, 10, 36, 255)):
    poly(d, [(0, -0.66), *arc(0, 0.18, 0.44, -25, 205)], c)
    circ(d, 0.40, 0.48, 0.10, fill=c)
    circ(d, -0.12, 0.06, 0.10, fill=(190, 120, 255, 255))


def p_blood(d, c=(255, 255, 255, 255)):
    for x, y, s in ((-0.24, -0.16, 1.0), (0.30, 0.10, 0.75)):
        poly(d, [(x, y - 0.50 * s), *arc(x, y + 0.10 * s, 0.30 * s, -25, 205)], c)


def p_hourglass(d, c=WHITE):
    line(d, [(-0.44, -0.62), (0.44, -0.62)], 0.10, c)
    line(d, [(-0.44, 0.62), (0.44, 0.62)], 0.10, c)
    poly(d, [(-0.36, -0.54), (0.36, -0.54), (0.06, 0), (0.36, 0.54), (-0.36, 0.54), (-0.06, 0)], c)


def p_bolt(d, c=WHITE):
    poly(d, [(0.16, -0.70), (-0.38, 0.06), (-0.04, 0.06), (-0.18, 0.70), (0.40, -0.12), (0.06, -0.12), (0.26, -0.70)], c)


def p_spiral(d, c=WHITE):
    pts = [(0.06 * t * math.cos(t), 0.06 * t * math.sin(t)) for t in [i * 0.2 for i in range(4, 52)]]
    line(d, pts, 0.10, c)


def p_mask(d, c=WHITE, bg=None):           # a death-mask
    poly(d, [(-0.46, -0.56), (0.46, -0.56), (0.50, 0.04), (0.20, 0.62), (-0.20, 0.62), (-0.50, 0.04)], c)
    k = bg or INK
    poly(d, [(-0.36, -0.20), (-0.08, -0.12), (-0.36, -0.04)], k)
    poly(d, [(0.36, -0.20), (0.08, -0.12), (0.36, -0.04)], k)
    line(d, [(-0.16, 0.34), (0.16, 0.34)], 0.07, k)


def p_fireward(d, c=WHITE, bg=None):
    p_shield(d, c)
    k = bg or INK
    poly(d, [(0.02, -0.36), (0.14, -0.16), (0.28, -0.02), (0.26, 0.20), (0.12, 0.36), (-0.14, 0.36), (-0.26, 0.18),
             (-0.24, -0.02), (-0.12, 0.06), (-0.08, -0.18)], k)


def p_veil(d, c=WHITE):                    # a veil falling over the ear
    poly(d, [(-0.56, -0.60), (0.56, -0.60), (0.48, 0.20), (0.30, 0.62), (0.12, 0.30), (-0.06, 0.62), (-0.24, 0.30),
             (-0.42, 0.62), (-0.54, 0.20)], c[:3] + (210,))
    line(d, [(-0.56, -0.60), (0.56, -0.60)], 0.10, c)


def p_wind(d, c=WHITE):
    line(d, [(-0.66, -0.30), (0.24, -0.30)] + arc(0.24, -0.50, 0.20, 90, -150), 0.10, c)
    line(d, [(-0.66, 0.02), (0.44, 0.02)] + arc(0.44, -0.18, 0.20, 90, -120), 0.10, c)
    line(d, [(-0.44, 0.34), (0.18, 0.34)] + arc(0.18, 0.54, 0.18, -90, 130), 0.10, c)


def p_twoshields(d, c=WHITE, bg=None):
    s = 0.72
    for dx, col in ((-0.20, c[:3] + (150,)), (0.18, c)):
        poly(d, [(dx, -0.60 * s - 0.05), (dx + 0.50 * s, -0.40 * s), (dx + 0.46 * s, 0.10 * s), (dx, 0.62 * s + 0.08),
                 (dx - 0.46 * s, 0.10 * s), (dx - 0.50 * s, -0.40 * s)], col)


def p_wave(d, c=WHITE):
    for y in (-0.26, 0.20):
        pts = [(x / 20.0 * 1.3 - 0.65, y + 0.14 * math.sin(x / 20.0 * 2 * math.pi * 1.5)) for x in range(21)]
        line(d, pts, 0.12, c)


def p_drowning(d, c=WHITE):                # a head under the waves
    circ(d, 0, -0.30, 0.22, fill=c)
    p_wave(d, c)


def p_wall(d, c=WHITE, bg=None):
    poly(d, [(-0.62, -0.50), (0.62, -0.50), (0.62, 0.56), (-0.62, 0.56)], c)
    k = bg or INK
    for y in (-0.14, 0.20):
        line(d, [(-0.62, y), (0.62, y)], 0.06, k)
    for row, y0, y1 in ((0, -0.50, -0.14), (1, -0.14, 0.20), (0, 0.20, 0.56)):
        for x in ((-0.20, 0.30) if row == 0 else (-0.42, 0.06, 0.48)):
            line(d, [(x, y0), (x, y1)], 0.06, k)


def p_unseen(d, c=WHITE, bg=None):         # One Truth: hardly targeted
    p_eye(d, c, bg)
    line(d, [(-0.60, 0.50), (0.60, -0.50)], 0.12, bg or INK)
    line(d, [(-0.60, 0.40), (0.60, -0.60)], 0.08, c)


def p_nocrit(d, c=WHITE, bg=None):         # Blackened Sight: no criticals land on her
    p_shield(d, c)
    k = bg or INK
    pts = []
    for i in range(16):
        r = 0.34 if i % 2 == 0 else 0.13
        a = math.radians(i * 22.5 - 90)
        pts.append((r * math.cos(a), r * math.sin(a) - 0.02))
    poly(d, pts, k)


def p_revive(d, c=WHITE, bg=None):         # Auto-revive / Force of Will: a heart that gets back up
    p_heart(d, c)
    k = bg or INK
    line(d, [(0, 0.22), (0, -0.20)], 0.09, k)
    poly(d, [(-0.16, -0.10), (0.16, -0.10), (0, -0.32)], k)


def p_jizo(d, c=WHITE, bg=None):           # Blessings of Jizo: a mirror that turns spells back
    circ(d, 0, -0.10, 0.48, fill=c)
    circ(d, 0, -0.10, 0.34, fill=bg or INK)
    line(d, [(-0.18, -0.22), (0.06, -0.36)], 0.07, c)
    poly(d, [(-0.14, 0.36), (0.14, 0.36), (0.22, 0.66), (-0.22, 0.66)], c)


def p_biting(d, c=WHITE):                  # a blade with teeth
    p_blade(d, c)
    for t in (0.15, 0.35, 0.55):
        x, y = -0.21 + (0.63 + 0.21) * t, 0.21 - (0.63 + 0.21) * t
        poly(d, [(x + 0.05, y + 0.05), (x + 0.20, y + 0.16), (x + 0.14, y - 0.02)], c)


def p_helm(d, c=WHITE, bg=None):           # Armor of the Emperor: a kabuto with kuwagata horns
    k = bg or INK
    poly(d, arc(0, 0.16, 0.44, 180, 360), c)                                           # bowl
    poly(d, [(-0.44, 0.14), (0.44, 0.14), (0.70, 0.50), (0.38, 0.42), (0, 0.50), (-0.38, 0.42), (-0.70, 0.50)], c)
    line(d, [(0, -0.12), (-0.20, -0.40), (-0.42, -0.70)], 0.11, c)                     # horns
    line(d, [(0, -0.12), (0.20, -0.40), (0.42, -0.70)], 0.11, c)
    circ(d, 0, -0.02, 0.10, fill=k)                                                    # mon
    line(d, [(-0.40, 0.14), (0.40, 0.14)], 0.05, k)


def p_roots(d, c=WHITE):
    line(d, [(0, -0.66), (0, 0.10)], 0.12, c)
    for pts in ([(0, 0.0), (-0.30, 0.24), (-0.56, 0.62)], [(0, 0.0), (0.30, 0.24), (0.56, 0.62)],
                [(0, 0.08), (-0.08, 0.38), (-0.04, 0.66)], [(-0.30, 0.24), (-0.10, 0.60)], [(0.30, 0.24), (0.14, 0.64)]):
        line(d, pts, 0.08, c)
    line(d, [(-0.66, -0.04), (0.66, -0.04)], 0.07, c[:3] + (160,))


def p_clay(d, c=WHITE, bg=None):           # Earth's Stagnation: a snail's pace
    k = bg or INK
    poly(d, [(-0.66, 0.40), (0.50, 0.40), (0.62, 0.24), (0.56, 0.12), (-0.40, 0.14)], c)       # foot
    line(d, [(0.50, 0.18), (0.62, -0.20)], 0.07, c)                                          # horns
    line(d, [(0.42, 0.18), (0.44, -0.14)], 0.06, c)
    circ(d, -0.08, -0.12, 0.42, fill=c)                                                     # shell
    pts = [(-0.08 + 0.024 * t * math.cos(t), -0.12 + 0.024 * t * math.sin(t)) for t in [i * 0.25 for i in range(6, 60)]]
    d.line(P(*pts), fill=k, width=px(0.06), joint="curve")
    line(d, [(-0.70, 0.56), (0.70, 0.56)], 0.06, c[:3] + (150,))


def p_hungry(d, c=WHITE):                  # Hungry Blade: a blade and a critical star
    p_blade(d, c)
    pts = []
    for i in range(10):
        r = 0.26 if i % 2 == 0 else 0.10
        a = math.radians(i * 36 - 90)
        pts.append((-0.40 + r * math.cos(a), -0.40 + r * math.sin(a)))
    poly(d, pts, (255, 228, 120, 255))


def p_thunder_mute(d, c=WHITE, bg=None):   # Thunderstruck: a bolt over a sealed mouth
    p_bolt(d, c)
    line(d, [(-0.56, 0.48), (0.56, 0.48)], 0.12, (255, 120, 120, 255))


def p_gust_eye(d, c=WHITE, bg=None):       # Buffeted: wind in the eyes
    p_eye(d, c, bg)
    line(d, [(-0.66, -0.56), (0.30, -0.56)] + arc(0.30, -0.72, 0.16, 90, -120), 0.08, c)


def p_dazzle(d, c=WHITE, bg=None):         # Dazzled: a flash in the eye
    p_eye(d, c, bg)
    for a in range(-150, -20, 32):
        r = math.radians(a)
        line(d, [(0.62 * math.cos(r), -0.06 + 0.62 * math.sin(r)), (0.80 * math.cos(r), -0.06 + 0.80 * math.sin(r))],
             0.07, (255, 230, 120, 255))


def p_rage(d, c=WHITE, bg=None):           # Everburning Rage: a figure in flames
    p_flame(d, c)
    k = bg or INK
    circ(d, 0, 0.0, 0.11, fill=k)
    poly(d, [(-0.14, 0.12), (0.14, 0.12), (0.18, 0.50), (-0.18, 0.50)], k)


def p_claws(d, c=WHITE):                   # Tiger Tattoo
    for x in (-0.30, 0.0, 0.30):
        line(d, [(x + 0.18, -0.60), (x - 0.04, 0.0), (x - 0.18, 0.60)], 0.11, c)


def p_feather(d, c=WHITE, bg=None):        # Raven Tattoo
    poly(d, [(0.50, -0.64), (0.10, -0.30), (-0.30, 0.20), (-0.44, 0.52), (-0.10, 0.36), (0.30, -0.06)], c)
    line(d, [(0.46, -0.60), (-0.50, 0.62)], 0.05, bg or INK)


def p_centipede(d, c=WHITE):               # Centipede Tattoo: an ink centipede, head up
    pts = [(0.30 * math.sin(i * 0.9), 0.54 - i * 0.22) for i in range(6)]
    for i, (x, y) in enumerate(pts):
        for s in (-1, 1):
            line(d, [(x, y), (x + s * 0.34, y + 0.10)], 0.06, c)
        circ(d, x, y, 0.13 if i < 5 else 0.15, fill=c)
    hx, hy = pts[-1]
    line(d, [(hx, hy), (hx - 0.18, hy - 0.20)], 0.05, c)
    line(d, [(hx, hy), (hx + 0.18, hy - 0.20)], 0.05, c)


def p_phoenix(d, c=WHITE):                 # Phoenix Tattoo: a rising flame-wing
    poly(d, [(0, 0.62), (-0.18, 0.10), (-0.62, -0.20), (-0.30, -0.18), (-0.50, -0.56), (-0.10, -0.24), (0, -0.66),
             (0.10, -0.24), (0.50, -0.56), (0.30, -0.18), (0.62, -0.20), (0.18, 0.10)], c)


def p_charm(d, c=WHITE, bg=None):          # a false White Squid charm
    circ(d, 0, -0.04, 0.42, fill=c)
    circ(d, 0, -0.04, 0.20, fill=bg or INK)
    for x in (-0.24, 0, 0.24):
        line(d, [(x, 0.34), (x * 1.3, 0.66)], 0.07, c)
    line(d, [(0, -0.46), (0, -0.66)], 0.07, c)


def p_charm_broken(d, c=WHITE, bg=None):
    p_charm(d, c, bg)
    line(d, [(-0.10, -0.66), (0.10, -0.20), (-0.06, 0.10), (0.12, 0.66)], 0.11, bg or INK)


def p_waves_strike(d, c=WHITE):            # Stand Against the Waves: a wave and extra cuts
    p_wave(d, c)
    for x in (-0.30, 0.0, 0.30):
        line(d, [(x + 0.12, -0.66), (x - 0.12, -0.44)], 0.07, c)


def p_tongue(d, c=WHITE):                  # Dazed (licked): stars round the head
    p_spiral(d, c)


# ---------------------------------------------------------------- tiles

PALETTE = {                                # tile top / bottom colours
    "atk": ((226, 92, 52), (150, 36, 24)), "def": ((70, 140, 226), (30, 72, 150)),
    "matk": ((222, 86, 186), (128, 30, 120)), "mdef": ((150, 110, 230), (76, 48, 150)),
    "agi": ((54, 196, 180), (16, 116, 112)), "eva": ((128, 196, 236), (52, 110, 170)),
    "hit": ((240, 196, 60), (176, 120, 20)), "cri": ((250, 170, 40), (196, 92, 16)),
    "counter": ((90, 180, 110), (30, 110, 60)), "earth": ((184, 140, 84), (110, 78, 40)),
    "hp": ((236, 96, 120), (160, 36, 64)), "calm": ((120, 200, 230), (60, 120, 170)),
    "fire": ((240, 120, 40), (170, 50, 20)), "water": ((60, 150, 220), (20, 76, 150)),
    "story": ((196, 170, 120), (120, 96, 60)), "taint": ((150, 90, 190), (60, 26, 90)),
    "blood": ((206, 40, 52), (120, 14, 26)), "dark": ((86, 88, 104), (34, 36, 46)),
    "void": ((120, 70, 200), (50, 20, 110)),
}
DEBUFF_TILE = ((88, 70, 92), (36, 26, 40))


def tile(kind, debuff=False):
    top, bot = DEBUFF_TILE if debuff else PALETTE[kind]
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    grad = Image.new("RGBA", (W, W))
    gd = ImageDraw.Draw(grad)
    for y in range(W):
        t = y / (W - 1)
        gd.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))
    mask = Image.new("L", (W, W), 0)
    m = int(W * 0.035)
    ImageDraw.Draw(mask).rounded_rectangle([m, m, W - m, W - m], radius=int(W * 0.20), fill=255)
    im.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([m, m, W - m, W - m], radius=int(W * 0.20), outline=(0, 0, 0, 120), width=int(W * 0.03))
    return im


def frame(im, kind):
    d = ImageDraw.Draw(im)
    m = int(W * 0.035)
    col = {"kata": (250, 214, 110, 255), "void": (214, 150, 255, 255)}[kind]
    d.rounded_rectangle([m, m, W - m, W - m], radius=int(W * 0.20), outline=col, width=int(W * 0.075))
    if kind == "void":                     # a small void ring top-left
        circ(d, -0.70, -0.70, 0.17, outline=col, w=0.07)


def badge(im, up):
    d = ImageDraw.Draw(im)
    cx, cy, r = 0.64, 0.64, 0.33
    circ(d, cx, cy, r + 0.05, fill=(0, 0, 0, 200))
    circ(d, cx, cy, r, fill=(70, 200, 90, 255) if up else (226, 56, 56, 255))
    if up:
        poly(d, [(cx, cy - 0.22), (cx + 0.20, cy + 0.10), (cx - 0.20, cy + 0.10)], WHITE)
    else:
        poly(d, [(cx, cy + 0.22), (cx + 0.20, cy - 0.10), (cx - 0.20, cy - 0.10)], WHITE)


def shadowed(fn, bgcol):
    """The pictogram, with a soft dark drop shadow so it reads on any tile."""
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    try:
        fn(ld, WHITE, bgcol)
    except TypeError:
        fn(ld, WHITE)
    a = lay.split()[3]
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(W * 0.02)).point(lambda v: int(v * 0.55)))
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.alpha_composite(sh, (int(W * 0.015), int(W * 0.025)))
    out.alpha_composite(lay)
    return out


def make(spec):
    """spec: (pictogram, tile kind, direction 'up'/'down'/None, frame None/'kata'/'void')"""
    fn, kind, dirn, fr = spec
    deb = dirn == "down"
    im = tile(kind, deb)
    bgc = tuple(DEBUFF_TILE[1] if deb else PALETTE[kind][1]) + (255,)
    # pictogram slightly up-left so the badge has room
    pic = shadowed(fn, bgc)
    if dirn:
        pic = pic.resize((int(W * 0.86), int(W * 0.86)), Image.LANCZOS)
        im.alpha_composite(pic, (int(W * 0.03), int(W * 0.03)))
    else:
        im.alpha_composite(pic)
    if fr:
        frame(im, fr)
    if dirn:
        badge(im, dirn == "up")
    return im.resize((OUT_PX, OUT_PX), Image.LANCZOS)


# ---------------------------------------------------------------- which icon each condition gets

STAT = {"PATK": (p_blade, "atk"), "PDEF": (p_shield, "def"), "MATK": (p_flame, "matk"), "MDEF": (p_ward, "mdef"),
        "AGI": (p_speed, "agi"), "PEVA": (p_evade, "eva"), "PHIT": (p_target, "hit"), "CRI": (p_star, "cri"),
        "CEVA": (p_nocrit, "def"), "MAXHP": (p_heart, "hp")}
# weight to compare points (PHIT, PEVA, CRI) with percents
WEIGHT = {"PHIT": 1.2, "PEVA": 1.2, "CRI": 1.4, "CEVA": 0.4, "TGR": 0.0}

SPECIAL = {   # cond -> (pictogram, tile, direction, frame-override or None)
    "K020": (p_blade, "atk", "up"), "K021": (p_blade, "atk", "down"), "K022": (p_shield, "def", "up"),
    "K023": (p_shield, "def", "down"), "K024": (p_ward, "mdef", "up"),
    "K025": (p_letter, "story", None), "K026": (p_taint, "taint", None), "K027": (p_mountain, "earth", "up"),
    "K028": (p_net, "story", None), "K029": (p_prone, "earth", "down"), "K030": (p_broken, "dark", None),
    "K044": (p_charm, "taint", None), "K045": (p_charm, "taint", None), "K046": (p_charm, "taint", None),
    "K047": (p_charm, "taint", None), "K048": (p_charm, "taint", None), "K049": (p_charm, "taint", None),
    "K050": (p_charm_broken, "taint", None), "K051": (p_hourglass, "agi", "down"), "K052": (p_bolt, "water", None),
    "K053": (p_falcon_eye, "hit", "up"), "K054": (p_tongue, "story", None), "K055": (p_blood, "blood", None),
    "K056": (p_mask, "dark", None), "K057": (p_fireward, "fire", "up"), "K058": (p_veil, "calm", None),
    "K059": (p_wind, "agi", "up"), "K060": (p_twoshields, "def", "up"), "K061": (p_drowning, "water", None),
    "K062": (p_speed, "agi", "up"),
    "K073": (p_wall, "earth", None), "K082": (p_unseen, "dark", None), "K092": (p_lotus, "atk", None),
    "K100": (p_nocrit, "def", "up"), "K112": (p_revive, "earth", None),
    "K121": (p_claws, "atk", None), "K122": (p_feather, "eva", None), "K123": (p_centipede, "agi", None),
    "K124": (p_phoenix, "fire", None),
    "K126": (p_mountain, "earth", "up"), "K136": (p_waves_strike, "water", None),
    "K146": (p_mountain, "earth", "up"), "K147": (p_mountain, "earth", "up"), "K152": (p_ward, "mdef", "up"),
    "K155": (p_lotus, "calm", None), "K156": (p_lotus, "calm", None), "K157": (p_lotus, "void", None),
    "K158": (p_revive, "hp", None), "K159": (p_jizo, "eva", None), "K160": (p_biting, "atk", "up"),
    "K161": (p_helm, "def", "up"), "K162": (p_roots, "earth", "down"), "K163": (p_clay, "earth", "down"),
    "K164": (p_hungry, "cri", "up"), "K165": (p_thunder_mute, "dark", None), "K166": (p_gust_eye, "hit", "down"),
    "K167": (p_dazzle, "hit", "down"), "K168": (p_rage, "fire", None),
}
VOID_GIFTS = {"K%03d" % i for i in list(range(125, 132)) + list(range(137, 155))}
KEEP_STOCK = {"K000", "K001", "K002", "K003", "K004", "K005", "K006", "K007", "K008", "K009", "K010", "K011",
              "K012", "K040", "K041", "K042", "K043"}


def spec_for(cid, c):
    fr = "kata" if c.get("rt_kata") else ("void" if cid in VOID_GIFTS else None)
    if cid in SPECIAL:
        s = SPECIAL[cid]
        return (s[0], s[1], s[2], fr)
    opts = [o for o in c.get("option", []) if o.get("opttype") == "opt_status" and o.get("propid") in STAT]
    if any(o.get("opttype") == "opt_counter" for o in c.get("option", [])):
        return (p_counter, "counter", None, fr)
    if any(o.get("opttype") == "opt_conddef" for o in c.get("option", [])):
        return (p_lotus, "calm", None, fr)
    if c.get("rt_dmgtaken"):
        return (p_mountain, "earth", "up", fr)
    if not opts:
        return None
    lv1 = [o for o in opts if o.get("LV", 1) == 1] or opts
    score = lambda o: o["val"] * WEIGHT.get(o["propid"], 1.0)  # noqa: E731
    best_up = max(lv1, key=score)
    if score(best_up) > 0:
        pic, kind = STAT[best_up["propid"]]
        return (pic, kind, "up", fr)
    worst = min(lv1, key=score)
    pic, kind = STAT[worst["propid"]]
    return (pic, kind, "down", fr)


def build():
    conds = json.load(open(CONDS, encoding="utf-8"))
    specs, assign = {}, {}
    for cid in sorted(k for k in conds if k.startswith("K")):
        c = conds[cid]
        if not isinstance(c, dict) or cid in KEEP_STOCK:
            continue
        sp = spec_for(cid, c)
        if not sp:
            continue
        key = (sp[0].__name__, sp[1], sp[2], sp[3])
        specs.setdefault(key, sp)
        assign[cid] = key
    keys = sorted(specs, key=lambda k: min(c for c, kk in assign.items() if kk == k))
    images = {k: make(specs[k]) for k in keys}
    return conds, assign, keys, images


def preview(conds, assign, keys, images):
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    rows = sorted(assign)
    cols = 4
    cw, ch = 330, 40
    sheet = Image.new("RGBA", (cols * cw, ((len(rows) + cols - 1) // cols) * ch + 8), (28, 30, 38, 255))
    d = ImageDraw.Draw(sheet)
    for i, cid in enumerate(rows):
        x, y = (i % cols) * cw + 6, (i // cols) * ch + 6
        sheet.alpha_composite(images[assign[cid]], (x, y))
        small = images[assign[cid]].resize((20, 20), Image.LANCZOS)
        sheet.alpha_composite(small, (x + 36, y + 6))
        d.text((x + 62, y + 4), "%s %s" % (cid, conds[cid]["name"][:30]), fill=(235, 235, 235, 255), font=font)
        d.text((x + 62, y + 20), assign[cid][0][2:] + (" " + assign[cid][3] if assign[cid][3] else ""),
               fill=(150, 150, 160, 255), font=font)
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    sheet.save(PREVIEW)
    cols = 12                                  # and every distinct icon at 3x, with a row at the real ~20 px size
    zs = Image.new("RGBA", (cols * 104, ((len(keys) + cols - 1) // cols) * 104 + 34), (40, 42, 52, 255))
    for i, k in enumerate(keys):
        zs.alpha_composite(images[k].resize((96, 96), Image.NEAREST), ((i % cols) * 104 + 4, (i // cols) * 104 + 4))
        if i * 18 + 24 < zs.width:
            zs.alpha_composite(images[k].resize((20, 20), Image.LANCZOS), (4 + i * 18, zs.height - 28))
    zs.save(PREVIEW.replace(".png", "_zoom.png"))
    print("preview", PREVIEW, len(rows), "conditions,", len(keys), "icons")


def write(conds, assign, keys, images):
    entries, blob = [], bytearray()
    cp_of = {}
    for i, k in enumerate(keys):
        cp = CP0 + i
        buf = io.BytesIO()
        images[k].save(buf, "PNG", optimize=True)
        data = buf.getvalue()
        entries.append({"cp": cp, "h": OUT_PX, "offs": len(blob), "size": len(data), "w": OUT_PX})
        blob += data
        cp_of[k] = cp
    open(os.path.join(ICONDIR, "usericon.bin"), "wb").write(bytes(blob))
    json.dump(entries, open(os.path.join(ICONDIR, "usericon.json"), "w"), separators=(",", ":"))
    for cid, k in assign.items():
        conds[cid]["icon"] = chr(cp_of[k])
    raw = open(CONDS, encoding="utf-8").read()
    indent = "\t" if raw[:40].count("\t") else None
    json.dump(conds, open(CONDS, "w", encoding="utf-8"), ensure_ascii=False, indent=indent)
    print("wrote usericon.bin/json:", len(entries), "icons; cond.json icons:", len(assign))


def main(check=False):
    """gen_data.py calls this right after it saves cond.json, so regenerated conditions keep their icons."""
    conds, assign, keys, images = build()
    preview(conds, assign, keys, images)
    if not check:
        write(conds, assign, keys, images)


if __name__ == "__main__":
    main("--check" in sys.argv)
