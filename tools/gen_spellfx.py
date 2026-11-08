"""Spell effects: one pixel-art effect per battle spell in docs/rules/haruki-spells.md (starting kit + §3 by element).

Each spell is classified from its description (element, target, verbs) into a cast pose (sprite animations cast_bolt /
cast_area / cast_heal / cast_ward / cast_summon / cast_void from gen_sprites2d.py) and a visual motif (flame, thunder,
orb, splash, healing ripple, wave, gust, cyclone, shards, spikes, shield, aura, curse, sleep, flash, mist, poison,
kami weapon, void, jade, summon pillar). The motif is drawn as an 8-frame pixel-art strip (64-px frames, x4 nearest)
and wrapped in a particle definition (.ptd: animated main sprite + elemental glow + motif particles). Variation per
spell is seeded from its name.
Writes resource/efx/rt/<id>.png + .ptd, efx.json FX400+, data/rt_spells.json (manifest used by gen_data.py for skills
S300+), preview _art/preview/spellfx.png.   Run: python -E tools/gen_spellfx.py
"""
import colorsys
import hashlib
import json
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROJ = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project")
RES = os.path.join(PROJ, "resource")
OUT = os.path.join(RES, "efx", "rt")
DOC = os.path.join(ROOT, "docs", "rules", "haruki-spells.md")
PREVIEW = os.path.join(ROOT, "_art", "preview")
N, PX, UP = 8, 64, 4                       # frames, frame px, upscale
FX0, SK0 = 400, 300

ELEM_PAL = {  # dark, mid, light, white-hot
    "Fire": ((150, 30, 20), (240, 110, 40), (255, 200, 80), (255, 250, 210)),
    "Water": ((20, 70, 170), (60, 150, 240), (150, 220, 255), (235, 250, 255)),
    "Air": ((90, 160, 150), (170, 225, 210), (225, 250, 240), (255, 255, 255)),
    "Earth": ((90, 60, 35), (160, 115, 65), (215, 180, 120), (250, 235, 190)),
    "Void": ((40, 10, 80), (130, 60, 220), (200, 150, 255), (245, 225, 255)),
    "Jade": ((15, 100, 55), (60, 200, 120), (160, 250, 190), (235, 255, 240)),
}

# ------------------------------------------------------------------------------------------- parsing


def parse_spells():
    lines = open(DOC, encoding="utf-8").read().splitlines()
    spells, elem, sec = [], None, None
    for ln in lines:
        if ln.startswith("## "):
            sec = ln
        m = re.match(r"### (Water|Fire|Air|Earth|Void)", ln)
        if m:
            elem = m.group(1)
        if ln.startswith("### ") and not m:
            elem = None if "Harmony" in ln or "Phoenix" in ln else elem
        if not ln.startswith("| ") or ln.startswith("| Spell") or ln.startswith("|---") or ln.startswith("| Pick"):
            continue
        if not sec or not (sec.startswith("## 2.") or sec.startswith("## 3.")):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("F:") or cells[0].startswith("F/") or cells[0].startswith("Pair"):
            continue
        name_cell, effect, target = cells[0], cells[1], cells[2] if len(cells) > 2 else ""
        if name_cell.startswith("Sense") or name_cell.startswith("*Void Fist"):
            if name_cell.startswith("*Void Fist"):
                name_cell = "Void Bolt (1)"
            else:
                continue
        el = elem
        if sec.startswith("## 2."):
            mm = re.search(r"\((Water|Fire|Air|Earth|Void) \d\)", name_cell)
            el = mm.group(1) if mm else "Void"
        if el is None:
            continue
        sep = " / " if " / " in name_cell else " · "
        names = [n.strip() for n in name_cell.split(sep)]
        effs = [e.strip() for e in effect.split(sep)] if len(names) > 1 else [effect]
        if len(effs) != len(names):
            effs = [effect] * len(names)
        tgts = [x.strip() for x in target.split(sep)] if len(names) > 1 else [target]
        if len(tgts) != len(names):
            tgts = [target] * len(names)
        for nm, ef, tg in zip(names, effs, tgts):
            ml = re.search(r"\((?:\w+ )?(\d)\)", nm)
            clean = re.sub(r"\*+", "", re.sub(r"\s*\((?:\w+ )?\d\)", "", nm)).strip()
            sp = re.search(r"\|\s*(\d+)", "|" + "|".join(cells[3:4]))
            spells.append({"name": clean, "elem": "Jade" if "Jade" in clean else el,
                           "ml": int(ml.group(1)) if ml else 1, "effect": re.sub(r"\*+", "", ef),
                           "target": tg, "sp": int(sp.group(1)) if sp else 6})
    seen, out = set(), []
    for s in spells:
        if s["name"] not in seen:
            seen.add(s["name"])
            out.append(s)
    return out


# ------------------------------------------------------------------------------------------- classification
OVERRIDES = {  # name -> (cast pose, motif, kind, target) where the description is too terse to classify
    "Tempest of Fire": ("area", "flame", "attack", 7),
    "The Wrath of Kaze-no-Kami": ("area", "cyclone", "attack", 7),
    "Hochiu's Call of Heaven": ("ward", "aura", "buff", 13),
    "Rise, Water": ("summon", "summon", "buff", 13),
    "Rise, Flame": ("summon", "summon", "buff", 13),
    "Rise, Air": ("summon", "summon", "buff", 13),
    "Rise, Earth": ("summon", "summon", "buff", 13),
    "Counterspell": ("ward", "shield", "buff", 13),
}


def classify(s):
    if s["name"] in OVERRIDES:
        return OVERRIDES[s["name"]]
    e, t, n = s["effect"].lower(), s["target"].lower(), s["name"].lower()
    en = e + " " + n
    dmg = bool(re.search(r"damage|bolt|blast|burst|orb|\bhit|breath|whip|knives|drown|destroyed|cyclone|strike", en))
    if t in ("", "—", "-"):
        t = "all enemies" if dmg else "self"
    enemy = "enemy" in t or "all enemies" in t or t == "all"
    many = "all" in t or "party" in t
    debuffy = re.search(r"−|debuff|loses its turn|skips|terror|rooted|seal|stagnation|curse|death of|burn the|\bdot\b|"
                        r"reveal|speed -|def -", en)
    if "summon" in e:
        cat, motif = "summon", "summon"
    elif "kami weapon" in e:
        cat, motif = "bolt", "weapon"
    elif s["elem"] == "Void":
        cat, motif = "void", "void"
    elif re.search(r"\bheal|cure|restore|full heal|regrow|\bhot\b", e) and not enemy:
        cat, motif = "heal", "heal"
    elif s["elem"] == "Jade":
        cat, motif = "bolt", "jade"
    elif enemy and re.search(r"thunder|osano", en):
        cat, motif = ("area" if many else "bolt"), "thunder"
    elif re.search(r"sleep|slumber", en):
        cat, motif = "area" if many else "bolt", "sleep"
    elif re.search(r"poison|spider", en):
        cat, motif = "area", "poison"
    elif enemy and re.search(r"blind|flash|sunlight|purge", en):
        cat, motif = "area", "flash"
    elif re.search(r"fog|mist|illusion|decoy|mirage|deception", en):
        cat, motif = "ward", "mist"
    elif enemy and re.search(r"cyclone|whirlwind|whirlpool|tempest|storm|gust|knives|wind", en):
        cat, motif = "area" if many else "bolt", "cyclone" if re.search("cyclone|whirl|tempest|storm", en) else "gust"
    elif enemy and debuffy and not re.search(r"damage", e):
        cat, motif = "bolt" if not many else "area", "curse"
    elif enemy and re.search(r"spike|quake|tremor", en):
        cat, motif = "area" if many else "bolt", "spikes"
    elif enemy and dmg:
        motif = {"Fire": "flame", "Water": "splash", "Air": "gust"}.get(s["elem"], "shards")
        cat = "area" if many else "bolt"
    elif enemy:
        cat, motif = "bolt", "curse"
    elif re.search(r"immune|ward|wall|armor|armour|resist|protection|sanctuary|reflect|endure|castle|untargetable",
                   en):
        cat, motif = "ward", "shield"
    else:
        cat, motif = ("ward" if "self" in t or "party" in t else "heal"), ("aura" if s["elem"] == "Fire" else "shield")
    if motif == "splash" and "wave" in en:
        motif = "wave"
    if motif == "heal":
        kind = "heal"
    elif enemy and (dmg or motif in ("weapon", "jade", "thunder", "flame", "splash", "shards", "spikes", "cyclone",
                                       "gust", "wave")):
        kind = "attack"
    else:
        kind = "debuff" if enemy else "buff"
    tgt = 7 if ("all enemies" in t or t == "all") else 1 if enemy else 11 if "party" in t or "all allies" in t         else 13 if "self" in t else 8
    return cat, motif, kind, tgt


# ------------------------------------------------------------------------------------------- drawing
def rng_for(name):
    return np.random.default_rng(int(hashlib.md5(name.encode()).hexdigest()[:8], 16))


def shift_pal(pal, rng):
    out = []
    dh = rng.uniform(-0.035, 0.035)
    for c in pal:
        h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in c])
        r, g, b = colorsys.hsv_to_rgb((h + dh) % 1, s, v)
        out.append((int(r * 255), int(g * 255), int(b * 255)))
    return out


class Frame:
    def __init__(self):
        self.im = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def disc(self, x, y, r, c, a=255):
        if r <= 0:
            return
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=c + (a,))

    def ring(self, x, y, r, c, w=2, a=255):
        if r <= 0:
            return
        self.d.ellipse([x - r, y - r, x + r, y + r], outline=c + (a,), width=w)

    def poly(self, pts, c, a=255):
        self.d.polygon([(float(x), float(y)) for x, y in pts], fill=c + (a,))

    def line(self, pts, c, w=2, a=255):
        self.d.line([(float(x), float(y)) for x, y in pts], fill=c + (a,), width=w)


C = PX / 2


def draw_frame(motif, k, pal, rng, seed):
    """k = 0..N-1. Returns a 64x64 RGBA frame."""
    f = Frame()
    t = k / (N - 1)
    dk, md, lt, wh = pal
    fade = int(255 * (1 - max(0, t - 0.6) / 0.4))
    r = np.random.default_rng(seed)                    # same random layout every frame
    if motif == "flame":
        for j in range(int(r.integers(5, 9))):
            a = r.uniform(0, 2 * math.pi)
            dist = (6 + 18 * t) * r.uniform(0.5, 1)
            x, y = C + math.cos(a) * dist, C + math.sin(a) * dist * 0.7 - 10 * t
            h = (10 + 8 * r.uniform()) * (1 - abs(t - 0.4))
            f.poly([(x - 4, y + 4), (x + 4, y + 4), (x + r.uniform(-2, 2), y - h)], md, fade)
            f.poly([(x - 2, y + 3), (x + 2, y + 3), (x, y - h * 0.6)], lt, fade)
        f.disc(C, C, 12 * (1 - t) + 2, wh, fade)
    elif motif == "thunder":
        f.disc(C, C, 22 * min(1, t * 3) * (1 - t * 0.5), lt, int(fade * 0.5))
        for j in range(3):
            x, y = C + r.uniform(-6, 6), 2
            pts = [(x, y)]
            while y < 60:
                y += r.uniform(6, 11)
                x += r.uniform(-8, 8)
                pts.append((x, y))
            if k % 2 == 0 or t < 0.5:
                f.line(pts, md, 4, fade)
                f.line(pts, wh, 2, fade)
    elif motif == "orb":
        f.disc(C, C, 6 + 6 * t, md, fade)
        f.disc(C - 2, C - 2, 3 + 3 * t, wh, fade)
        f.ring(C, C, 10 + 18 * t, lt, 2, fade)
    elif motif in ("splash", "wave"):
        if motif == "wave":
            for j in range(3):
                x0 = -20 + 70 * t + j * 6
                f.d.arc([x0 - 18, 14 + j * 4, x0 + 18, 58], 200, 340, fill=(md if j < 2 else lt) + (fade,), width=4)
        for j in range(int(r.integers(8, 14))):
            a = r.uniform(math.pi, 2 * math.pi)
            dist = 4 + 26 * t * r.uniform(0.6, 1)
            x = C + math.cos(a) * dist
            y = C + math.sin(a) * dist + 40 * t * t
            f.disc(x, y, 2.5 * (1 - t) + 1, lt if j % 2 else md, fade)
        f.ring(C, C + 14, 6 + 20 * t, md, 2, fade)
    elif motif == "heal":
        for j in range(3):
            rr = (t * 28 + j * 8) % 28
            f.ring(C, C + 10, rr, lt, 1, int(fade * (1 - rr / 28)))
        for j in range(int(r.integers(6, 10))):
            x = C + r.uniform(-18, 18)
            y = 54 - ((t * 50 + r.uniform(0, 40)) % 50)
            s = 1 + (j % 2)
            f.line([(x - s - 1, y), (x + s + 1, y)], wh, 1, fade)
            f.line([(x, y - s - 1), (x, y + s + 1)], wh, 1, fade)
        f.disc(C, C + 8, 8 * (1 - abs(t - 0.5) * 2) + 2, md, int(fade * 0.6))
    elif motif in ("gust", "cyclone"):
        turns = 2.5 if motif == "cyclone" else 1.4
        for j in range(4 if motif == "gust" else 6):
            pts = []
            for q in range(14):
                u = q / 13
                ang = (u * turns + t * 1.5 + j / 6) * 2 * math.pi
                rad = (4 + 22 * u) if motif == "gust" else (6 + 14 * (1 - u * 0.5))
                y = C + (math.sin(ang) * rad * 0.5 if motif == "gust" else 56 - u * 52)
                pts.append((C + math.cos(ang) * rad, y))
            f.line(pts, md if j % 2 else lt, 2, fade)
    elif motif in ("shards", "jade"):
        for j in range(int(r.integers(6, 10))):
            a = r.uniform(0, 2 * math.pi)
            dist = 4 + 26 * t * r.uniform(0.6, 1)
            x, y = C + math.cos(a) * dist, C + math.sin(a) * dist + (14 * t * t if motif == "shards" else 0)
            s = 4 + 3 * r.uniform()
            rot = a + t * 3
            pts = [(x + math.cos(rot + q * 2.1) * s, y + math.sin(rot + q * 2.1) * s) for q in range(3)]
            f.poly(pts, md if j % 2 else lt, fade)
            f.line([pts[0], pts[1]], wh if motif == "jade" else lt, 1, fade)
        f.disc(C, C, 10 * (1 - t), wh if motif == "jade" else lt, int(fade * 0.5))
    elif motif == "spikes":
        for j in range(5):
            x = 8 + j * 12 + r.uniform(-2, 2)
            h = 40 * min(1, t * 2.2) * (0.6 + 0.4 * r.uniform())
            f.poly([(x - 5, 60), (x + 5, 60), (x + r.uniform(-1, 1), 60 - h)], md, fade)
            f.poly([(x - 1, 60), (x + 4, 60), (x + 1, 60 - h * 0.9)], lt, fade)
        for j in range(6):
            f.disc(r.uniform(4, 60), 58 - 10 * t * r.uniform(), 2, dk, fade)
    elif motif == "shield":
        sides = int(r.integers(5, 9))
        rad = 14 + 10 * min(1, t * 2)
        rot = t * math.pi / 3
        pts = [(C + math.cos(rot + q * 2 * math.pi / sides) * rad, C + math.sin(rot + q * 2 * math.pi / sides) * rad)
               for q in range(sides)]
        f.line(pts + [pts[0]], lt, 3, fade)
        f.line(pts + [pts[0]], wh, 1, fade)
        for p in pts:
            f.disc(p[0], p[1], 2, wh, fade)
        f.disc(C, C, rad * 0.6, md, int(fade * 0.25))
    elif motif == "aura":
        for j in range(8):
            a = j / 8 * 2 * math.pi + t * 2
            x, y = C + math.cos(a) * 18, C + math.sin(a) * 10 + 8
            h = 8 + 6 * math.sin(t * 6 + j)
            f.poly([(x - 3, y), (x + 3, y), (x, y - h)], md, fade)
            f.poly([(x - 1, y), (x + 1, y), (x, y - h * 0.6)], lt, fade)
    elif motif == "curse":
        for j in range(3):
            pts = []
            for q in range(16):
                u = q / 15
                ang = (u * 2 + t + j / 3) * 2 * math.pi
                rad = 24 * (1 - u) * (1 - t * 0.3)
                pts.append((C + math.cos(ang) * rad, C + math.sin(ang) * rad * 0.6 + u * 6))
            f.line(pts, dk if j else md, 2, fade)
        for j in range(6):
            f.disc(C + r.uniform(-16, 16), 10 + ((t * 40 + r.uniform(0, 40)) % 48), 1.5, md, fade)
    elif motif == "sleep":
        for j in range(3):
            x = C - 12 + j * 9 + 4 * math.sin(t * 6 + j)
            y = 48 - ((t * 30 + j * 12) % 40)
            s = 3 + j
            f.line([(x - s, y - s), (x + s, y - s), (x - s, y + s), (x + s, y + s)], wh, 2, fade)
        f.disc(C, C + 14, 14, lt, int(fade * 0.25))
    elif motif == "flash":
        rad = 30 * min(1, t * 3)
        f.disc(C, C, rad, lt, int(fade * 0.5))
        f.disc(C, C, rad * 0.5, wh, fade)
        for j in range(8):
            a = j / 8 * 2 * math.pi
            f.line([(C, C), (C + math.cos(a) * rad * 1.1, C + math.sin(a) * rad * 1.1)], wh, 1, fade)
    elif motif == "mist":
        for j in range(7):
            x = C + r.uniform(-18, 18) + 8 * math.sin(t * 4 + j)
            y = C + r.uniform(-10, 14)
            f.disc(x, y, 6 + 6 * t, lt, int(fade * 0.45))
            f.disc(x - 2, y - 2, 3 + 3 * t, wh, int(fade * 0.35))
    elif motif == "poison":
        for j in range(int(r.integers(7, 12))):
            x = C + r.uniform(-20, 20)
            y = 56 - ((t * 44 + r.uniform(0, 44)) % 50)
            rr = 2 + 2 * r.uniform()
            f.ring(x, y, rr, md, 1, fade)
            f.disc(x - 1, y - 1, 1, wh, fade)
        f.disc(C, 52, 16, dk, int(fade * 0.4))
    elif motif == "weapon":
        a = -2.4 + 2.0 * t
        x0, y0 = C + math.cos(a) * 24, C + math.sin(a) * 24
        x1, y1 = C - math.cos(a) * 24, C - math.sin(a) * 24
        f.line([(x0, y0), (x1, y1)], md, 5, fade)
        f.line([(x0, y0), (x1, y1)], wh, 2, fade)
        for q in range(5):
            u = (q + 1) / 6
            f.d.arc([C - 26 * u - 2, C - 26 * u - 2, C + 26 * u + 2, C + 26 * u + 2],
                    math.degrees(a) - 60, math.degrees(a), fill=lt + (int(fade * (1 - u)),), width=1)
    elif motif == "void":
        f.disc(C, C, 10 * (1 - t) + 3, dk, fade)
        for j in range(10):
            a = j / 10 * 2 * math.pi + t * 3
            rad = 26 * (1 - t) + 2
            x, y = C + math.cos(a) * rad, C + math.sin(a) * rad
            f.line([(x - 2, y), (x + 2, y)], wh, 1, fade)
            f.line([(x, y - 2), (x, y + 2)], wh, 1, fade)
        f.ring(C, C, 6 + 20 * t, md, 2, fade)
    elif motif == "summon":
        w = 10 + 8 * math.sin(t * math.pi)
        f.d.rectangle([C - w / 2, 0, C + w / 2, 60], fill=lt + (int(fade * 0.55),))
        f.d.rectangle([C - w / 5, 0, C + w / 5, 60], fill=wh + (fade,))
        f.ring(C, 56, 10 + 18 * t, md, 2, fade)
        for q in range(6):
            a = q / 6 * 2 * math.pi + t * 2
            f.disc(C + math.cos(a) * (10 + 18 * t), 56 + math.sin(a) * 3, 2, wh, fade)
    else:
        f.disc(C, C, 10, md, fade)
    return f.im


SUBMOTIFS = [  # (motif it refines, regex on name+description, submotif)
    ("shield", r"armou?r|def\b|def or|plates", "plates"), ("shield", r"immune|immunity", "bubble"),
    ("shield", r"reflect", "mirror"), ("shield", r"endure|will\b|lethal", "heartflame"),
    ("shield", r"acts first|speed|haste", "speedlines"), ("shield", r"fortune|re-rolled|luck", "coins"),
    ("shield", r"sanctuary|shinsei|temple", "lotus"), ("shield", r"wall of|wall\b", "bars"),
    ("shield", r"bond|heart of mortality|shared", "links"), ("shield", r"contingency|silent waters|store", "hourglass"),
    ("shield", r"crow|taint", "feathers"), ("shield", r"debuff off|sympathetic|pass one", "swap"),
    ("shield", r"shaken|ice", "snowflake"), ("shield", r"untargetable|eye shall", "eye"),
    ("aura", r"steel|blade|weapon", "blade"), ("aura", r"sheath|purity", "flamesheath"),
    ("aura", r"acts first|speed", "speedlines"), ("aura", r"again|hurried", "footprints"),
    ("aura", r"whip|dragon", "whip"), ("aura", r"crit|hungry", "stars"), ("aura", r"extra fire hit|follow", "orbit"),
    ("curse", r"speed|stagnation|slow", "slowspiral"), ("curse", r"\bdef\b|e\.def|armou?r", "crack"),
    ("curse", r"\batk\b|weapon", "brokenblade"), ("curse", r"turn|skips|down", "hourglassx"),
    ("curse", r"seal|rooted|grasp|essence", "chains"), ("curse", r"burn|heat|dot|inferno", "embers"),
    ("curse", r"reveal|know the mind|next", "eye"),
    ("void", r"\+1 vp|drawing", "converge"), ("void", r"boosted|essence", "chains"),
    ("void", r"boost level|altering", "clock"), ("void", r"shared vp|kharmic", "links"),
    ("void", r"release|stat in place", "burstout"), ("void", r"steal vp|void strike", "siphon"),
    ("void", r"swap the target|suppression", "swap"), ("void", r"void damage|void bolt", "darkbolt"),
    ("void", r"counter|cancel", "mirror"),
]


def submotif(motif, s):
    en = (s["name"] + " " + s["effect"]).lower()
    for m, rx, sub in SUBMOTIFS:
        if m == motif and re.search(rx, en):
            return sub
    return None


RED = (230, 40, 40)


def draw_sub(f, sub, k, pal, r):
    t = k / (N - 1)
    dk, md, lt, wh = pal
    fade = int(255 * (1 - max(0, t - 0.6) / 0.4))
    grow = min(1, t * 2.2)
    if sub == "plates":
        for j in range(6):
            a = j / 6 * 2 * math.pi + t
            x, y = C + math.cos(a) * 16 * grow, C + math.sin(a) * 16 * grow
            f.poly([(x + math.cos(a + q * math.pi / 3) * 6, y + math.sin(a + q * math.pi / 3) * 6) for q in range(6)],
                   md, fade)
            f.ring(x, y, 5, wh, 1, fade)
    elif sub == "bubble":
        f.disc(C, C, 24 * grow, lt, int(fade * 0.3))
        f.ring(C, C, 24 * grow, wh, 2, fade)
        f.disc(C - 9 * grow, C - 9 * grow, 4 * grow, wh, fade)
    elif sub == "mirror":
        f.ring(C, C, 20 * grow, wh, 3, fade)
        for j in range(12):
            a = j / 12 * 2 * math.pi
            f.line([(C + math.cos(a) * 22 * grow, C + math.sin(a) * 22 * grow),
                    (C + math.cos(a) * 30 * grow, C + math.sin(a) * 30 * grow)], lt, 1, fade)
    elif sub == "heartflame":
        h = 22 * grow
        f.poly([(C - 10, C + 8), (C + 10, C + 8), (C, C - h)], md, fade)
        f.poly([(C - 5, C + 7), (C + 5, C + 7), (C, C - h * 0.6)], wh, fade)
    elif sub == "speedlines":
        for j in range(7):
            y = 8 + j * 8
            x = (t * 120 + j * 23) % 90 - 20
            f.line([(x, y), (x + 18, y)], lt if j % 2 else wh, 2, fade)
    elif sub == "coins":
        for j in range(7):
            a = j / 7 * 2 * math.pi + t * 4
            x, y = C + math.cos(a) * 18, C + math.sin(a) * 8 - 10 * t
            f.disc(x, y, 4, md, fade)
            f.disc(x - 1, y - 1, 2, wh, fade)
    elif sub == "lotus":
        for j in range(8):
            a = j / 8 * 2 * math.pi
            rr = 18 * grow
            f.poly([(C, C + 6), (C + math.cos(a - 0.3) * rr, C + 6 + math.sin(a - 0.3) * rr * 0.5),
                    (C + math.cos(a) * rr * 1.2, C + 6 + math.sin(a) * rr * 0.6),
                    (C + math.cos(a + 0.3) * rr, C + 6 + math.sin(a + 0.3) * rr * 0.5)], lt if j % 2 else md, fade)
        f.disc(C, C + 4, 5, wh, fade)
    elif sub == "bars":
        for j in range(6):
            x = 8 + j * 10
            h = 50 * grow
            f.d.rectangle([x, 60 - h, x + 5, 60], fill=md + (fade,))
            f.line([(x + 1, 60 - h), (x + 1, 60)], wh, 1, fade)
    elif sub == "links":
        f.ring(C - 9, C, 11, md, 3, fade)
        f.ring(C + 9, C, 11, lt, 3, fade)
        f.disc(C, C, 3 * grow, wh, fade)
    elif sub in ("hourglass", "hourglassx"):
        f.poly([(C - 12, 10), (C + 12, 10), (C, C)], md, fade)
        f.poly([(C - 12, 54), (C + 12, 54), (C, C)], lt, fade)
        f.line([(C - 12, 10), (C + 12, 10)], wh, 2, fade)
        f.line([(C - 12, 54), (C + 12, 54)], wh, 2, fade)
        if sub == "hourglassx" and t > 0.3:
            f.line([(C - 18, 14), (C + 18, 50)], RED, 3, fade)
            f.line([(C + 18, 14), (C - 18, 50)], RED, 3, fade)
    elif sub == "feathers":
        for j in range(5):
            x = C + r.uniform(-20, 20)
            y = 8 + ((t * 50 + j * 13) % 50)
            a = math.sin(t * 6 + j) * 0.6
            f.poly([(x, y - 6), (x + 4 * math.cos(a), y), (x, y + 6), (x - 4 * math.cos(a), y)], dk, fade)
            f.line([(x, y - 6), (x, y + 6)], md, 1, fade)
    elif sub == "swap":
        for sgn in (-1, 1):
            a0 = t * math.pi + (0 if sgn > 0 else math.pi)
            f.disc(C + math.cos(a0) * 16, C + math.sin(a0) * 10, 5, md if sgn > 0 else lt, fade)
        f.d.arc([C - 16, C - 10, C + 16, C + 10], 0, 360, fill=wh + (int(fade * 0.6),), width=1)
    elif sub == "snowflake":
        for j in range(6):
            a = j / 6 * 2 * math.pi + t
            x, y = C + math.cos(a) * 20 * grow, C + math.sin(a) * 20 * grow
            f.line([(C, C), (x, y)], wh, 2, fade)
            f.line([(x, y), (x + math.cos(a + 0.8) * 5, y + math.sin(a + 0.8) * 5)], lt, 1, fade)
    elif sub == "eye":
        f.d.ellipse([C - 20 * grow, C - 9 * grow, C + 20 * grow, C + 9 * grow], fill=lt + (fade,))
        f.disc(C, C, 6 * grow, dk, fade)
        f.disc(C + 1, C - 1, 2, wh, fade)
    elif sub in ("blade", "brokenblade"):
        f.poly([(C - 2, 56), (C + 2, 56), (C + 3, 12), (C, 6), (C - 3, 12)], wh, fade)
        f.line([(C - 8, 44), (C + 8, 44)], md, 3, fade)
        if sub == "brokenblade" and t > 0.35:
            f.d.rectangle([C - 5, 22, C + 5, 28], fill=(0, 0, 0, 0))
            f.line([(C - 6, 30), (C + 6, 20)], RED, 2, fade)
        else:
            f.line([(C + 4, 10 + 40 * t), (C + 10, 6 + 40 * t)], lt, 1, fade)
    elif sub == "flamesheath":
        for j in range(10):
            a = j / 10 * 2 * math.pi
            x, y = C + math.cos(a) * 14, C + math.sin(a) * 22
            h = 6 + 4 * math.sin(t * 8 + j)
            f.poly([(x - 2, y), (x + 2, y), (x, y - h)], md if j % 2 else lt, fade)
    elif sub == "footprints":
        for j in range(4):
            x, y = 10 + j * 13, 50 - j * 8
            if t * 4 > j:
                f.d.ellipse([x, y, x + 6, y + 9], fill=md + (fade,))
                f.poly([(x, y), (x + 6, y), (x + 3, y - 8)], lt, fade)
    elif sub == "whip":
        pts = [(8 + q * 3.6, C + math.sin(q * 0.5 + t * 8) * 14 * (q / 14)) for q in range(15)]
        f.line(pts, md, 4, fade)
        f.line(pts, wh, 1, fade)
    elif sub == "stars":
        for j in range(5):
            x, y = C + r.uniform(-20, 20), C + r.uniform(-20, 20)
            s_ = 5 * math.sin(math.pi * ((t * 2 + j * 0.2) % 1))
            f.line([(x - s_, y), (x + s_, y)], wh, 2, fade)
            f.line([(x, y - s_), (x, y + s_)], wh, 2, fade)
    elif sub == "orbit":
        for j in range(3):
            a = t * 6 + j * 2.1
            x, y = C + math.cos(a) * 20, C + math.sin(a) * 9
            f.poly([(x - 4, y + 3), (x + 4, y + 3), (x, y - 9)], md, fade)
            f.disc(x, y + 1, 2, wh, fade)
    elif sub == "slowspiral":
        pts = [(C + math.cos(q * 0.5 + t) * q * 1.6, C + math.sin(q * 0.5 + t) * q * 1.6) for q in range(18)]
        f.line(pts, md, 3, fade)
        f.line(pts[:8], wh, 1, fade)
    elif sub == "crack":
        f.poly([(C - 14, 12), (C + 14, 12), (C + 12, 40), (C, 54), (C - 12, 40)], md, fade)
        if t > 0.25:
            f.line([(C, 12), (C - 4, 26), (C + 3, 34), (C - 2, 54)], dk, 2, fade)
    elif sub == "chains":
        for j in range(6):
            a = j / 6 * 2 * math.pi + t
            x, y = C + math.cos(a) * 18, C + math.sin(a) * 12
            f.d.ellipse([x - 4, y - 3, x + 4, y + 3], outline=lt + (fade,), width=2)
    elif sub == "embers":
        for j in range(12):
            x = C + r.uniform(-20, 20)
            y = 6 + ((t * 40 + r.uniform(0, 50)) % 56)
            f.disc(x, y, 1.5, md if j % 2 else lt, fade)
    elif sub == "converge":
        for j in range(10):
            a = j / 10 * 2 * math.pi
            rad = 30 * (1 - t) + 2
            f.disc(C + math.cos(a) * rad, C + math.sin(a) * rad, 2, wh, fade)
        f.disc(C, C, 4 + 6 * t, md, fade)
    elif sub == "clock":
        f.ring(C, C, 20, lt, 2, fade)
        a = t * 2 * math.pi - math.pi / 2
        f.line([(C, C), (C + math.cos(a) * 16, C + math.sin(a) * 16)], wh, 2, fade)
        f.line([(C, C), (C + math.cos(a * 0.3) * 10, C + math.sin(a * 0.3) * 10)], md, 2, fade)
    elif sub == "burstout":
        for j in range(12):
            a = j / 12 * 2 * math.pi
            f.line([(C + math.cos(a) * 6, C + math.sin(a) * 6),
                    (C + math.cos(a) * (8 + 24 * t), C + math.sin(a) * (8 + 24 * t))], md if j % 2 else wh, 2, fade)
    elif sub == "siphon":
        pts = [(8 + q * 3.4, C + math.sin(q * 0.7 - t * 9) * 6) for q in range(15)]
        f.line(pts, md, 3, fade)
        f.disc(56 - 48 * t, C, 4, wh, fade)
    elif sub == "darkbolt":
        f.line([(6, C - 4), (C, C), (58, C + 4)], dk, 6, fade)
        f.line([(6, C - 4), (C, C), (58, C + 4)], md, 2, fade)
        f.disc(58 * t + 3, C - 4 + 8 * t, 5, wh, fade)


def sigil(f, k, pal, seed):
    """A unique little kanji-like glyph per spell, flashing at the centre mid-animation."""
    if not 2 <= k <= 5:
        return
    r = np.random.default_rng(seed ^ 0x5EED)
    a = 255 if k in (3, 4) else 150
    col = pal[3]
    x0, y0, sz = C - 6, C - 6, 12
    for q in range(int(r.integers(3, 6))):
        kind = int(r.integers(0, 4))
        u, v = r.integers(0, 4, 2) * sz / 3
        if kind == 0:
            f.line([(x0 + u, y0 + v), (x0 + u + sz / 2, y0 + v)], col, 1, a)
        elif kind == 1:
            f.line([(x0 + u, y0 + v), (x0 + u, y0 + v + sz / 2)], col, 1, a)
        elif kind == 2:
            f.line([(x0 + u, y0 + v), (x0 + u + sz / 3, y0 + v + sz / 3)], col, 1, a)
        else:
            f.disc(x0 + u, y0 + v, 0.8, col, a)


def strip(motif, pal, name, sub=None):
    seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    rng = rng_for(name)
    im = Image.new("RGBA", (PX * N, PX), (0, 0, 0, 0))
    for k in range(N):
        if sub:
            f = Frame()
            draw_sub(f, sub, k, pal, np.random.default_rng(seed))
        else:
            f = Frame()
            f.im = draw_frame(motif, k, pal, rng, seed)
            f.d = ImageDraw.Draw(f.im)
        sigil(f, k, pal, seed)
        im.paste(f.im, (k * PX, 0))
    return im


# ------------------------------------------------------------------------------------------- particle file
def s32(c):
    r, g, b, a = c
    v = (r << 24) | (g << 16) | (b << 8) | a
    return v - (1 << 32) if v & 0x80000000 else v


PARTS = {  # motif -> (count, velocity, accel_y, size, spread)
    "flame": (16, 1.2, 1.5, 0.12, 0.3), "thunder": (10, 4.0, 0.0, 0.08, 0.2), "splash": (18, 2.5, -4.0, 0.1, 0.2),
    "wave": (18, 2.5, -4.0, 0.1, 0.3), "heal": (14, 0.6, 1.2, 0.08, 0.5), "gust": (16, 2.0, 0.3, 0.07, 0.4),
    "cyclone": (24, 1.5, 1.0, 0.08, 0.4), "shards": (14, 3.0, -5.0, 0.12, 0.2), "jade": (14, 2.5, -2.0, 0.1, 0.2),
    "spikes": (12, 1.0, -3.0, 0.1, 0.5), "shield": (10, 0.4, 0.4, 0.08, 0.6), "aura": (14, 0.8, 1.6, 0.1, 0.5),
    "curse": (12, 0.6, -0.8, 0.09, 0.5), "sleep": (8, 0.4, 0.8, 0.08, 0.4), "flash": (20, 4.0, 0.0, 0.06, 0.1),
    "mist": (10, 0.3, 0.2, 0.25, 0.6), "poison": (14, 0.5, 1.0, 0.09, 0.5), "weapon": (12, 3.0, 0.0, 0.07, 0.2),
    "void": (16, -1.2, 0.0, 0.08, 0.6), "summon": (20, 1.0, 2.5, 0.09, 0.4), "orb": (12, 1.5, 0.0, 0.08, 0.3),
}


def group(name, num, life, tex, w, mods, aimtype=1, start_spr=0, posy=0.0, spread=0.0, dir_spr=0.0, local=True):
    return """	with ParticleGroupData(){
		name = "%s"
		enabled = true
		aimtype = %d
		localcoord = %s
		emitter = with ParticleEmitter(){
			num = %d
			start = 0, start_spr = %d
			life = %d, life_spr = %d
			posx = 0.0, posy = %.3f, posz = 0.0
			pos_sprx = %.3f, pos_spry = %.3f, pos_sprz = %.3f
			dirx = 0.0, diry = 0.0, dirz = 0.0
			dir_sprx = %.6f, dir_spry = %.6f, dir_sprz = 0.0
			linearbits = 0
		},
		shapetype = 0
		shapedata = {"axis":0,"r":0.0,"w":%.3f,"h":%.3f}
		texture = "%s"
		color = 0xffffffff
		blendmode = 5
		blend = 5
		Ka = 0x808080ff
		Ks = 0x00000000
		mod = [
%s
		]
	},
""" % (name, aimtype, "true" if local else "false", num, start_spr, life, life // 3, posy, spread, spread, spread,
       dir_spr, dir_spr, w, w, tex, "\n".join("\t\t" + json.dumps(m, separators=(",", ":")) + "," for m in mods))


def ptd(fxid, motif, pal, size):
    dk, md, lt, wh = pal
    n, vel, acc, psz, spread = PARTS.get(motif, PARTS["orb"])
    life = 900 if motif in ("summon", "cyclone", "heal", "shield", "aura", "mist") else 700
    main = group("main", 1, life, "/resource/efx/rt/%s.png" % fxid, size, [
        {"classid": "ptcmod_texanime", "frame": [0, N]},
        {"xyz": 7, "scale": [0.9, 1.0, 1.05, 1.1], "classid": "ptcmod_scale"},
        {"color": [s32(wh + (255,)), s32(wh + (255,)), s32(wh + (200,)), s32(wh + (0,))], "classid": "ptcmod_color"},
    ], posy=0.4)
    glow = group("glow", 2, life, "/resource/efx/tex/glow1.webp", size * 0.9, [
        {"xyz": 7, "scale": [0.6, 1.4, 1.8], "classid": "ptcmod_scale"},
        {"color": [s32(lt + (160,)), s32(md + (110,)), s32(dk + (0,))], "classid": "ptcmod_color"},
    ], start_spr=150, posy=0.4)
    sparks = group("sparks", n, int(life * 0.8), "/resource/efx/tex/square2.webp", psz, [
        {"vel": vel, "classid": "ptcmod_vel", "vel_spr": abs(vel) * 0.4},
        {"axisid": 1, "classid": "ptcmod_acc", "acc_spr": 0.2, "coord": 0, "acc": acc},
        {"color": [s32(wh + (255,)), s32(lt + (255,)), s32(md + (180,)), s32(dk + (0,))], "classid": "ptcmod_color"},
        {"xyz": 7, "scale": [1.0, 1.2, 0.5, 0.0], "classid": "ptcmod_scale"},
    ], aimtype=2 if motif in ("thunder", "flash", "weapon", "gust", "shards") else 1, start_spr=300, posy=0.4,
        spread=spread, dir_spr=3.141593)
    return """////////////////////////////////////////////////////////
//   ParticleData (Rokugan Traveler spell effect, tools/gen_spellfx.py)
////////////////////////////////////////////////////////
parentcoord <- false
currentgroup <- 0
prof <- {"showbnd":[0,0.5,0,1.5,1.5,1.5],"maxbnd":[0,0.5,0,2.0,2.0,2.0],"showtime":%d,"wholebnd":[0,0.5,0,2.0,2.0,2.0]}
groups <- [
%s%s%s]
actions <- [
	{"acttype":"emitall","time":0}
]
""" % (life, main, glow, sparks)


# ------------------------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    spells = parse_spells()
    epath = os.path.join(RES, "efx.json")
    efx = json.load(open(epath, encoding="utf-8"))
    efx = {k: v for k, v in efx.items() if not (k.startswith("FX") and k[2:].isdigit() and int(k[2:]) >= FX0)}
    efx["_meta"] = dict(efx.get("_meta", {}), caps=999)
    manifest = []
    prev = []
    for i, s in enumerate(spells):
        cat, motif, kind, tgt = classify(s)
        rng = rng_for(s["name"])
        pal = shift_pal(ELEM_PAL[s["elem"]], rng)
        fxid = "FX%03d" % (FX0 + i)
        sub = submotif(motif, s)
        im = strip(motif, pal, s["name"], sub)
        im.resize((im.width * UP, im.height * UP), Image.NEAREST).save(os.path.join(OUT, fxid + ".png"))
        size = 2.2 if cat in ("area", "summon") or tgt in (7, 11) else 1.5
        open(os.path.join(OUT, fxid + ".ptd"), "w", encoding="utf-8").write(ptd(fxid, motif, pal, size))
        efx[fxid] = {"billboard": False, "efx": "/resource/efx/rt/%s.ptd" % fxid, "eventuse": False,
                     "hpb": [0, 0, 0], "hsv": [0, 0, 0], "name": {"en": s["name"], "ja": s["name"]}, "ovfx": {},
                     "place": 0, "pos": [0, 0, 0], "scale": 1.0, "speed": 1.0, "waittime": 650}
        manifest.append(dict(s, cat=cat, motif=motif, sub=sub, kind=kind, tgt=tgt, fx=fxid,
                             skill="S%03d" % (SK0 + i)))
        prev.append(im.crop((PX * 3, 0, PX * 4, PX)))
    json.dump(efx, open(epath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    json.dump(manifest, open(os.path.join(PROJ, "data", "rt_spells.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    cols = 12
    sheet = Image.new("RGBA", (PX * cols, PX * ((len(prev) + cols - 1) // cols)), (24, 22, 30, 255))
    for i, im in enumerate(prev):
        sheet.alpha_composite(im, ((i % cols) * PX, (i // cols) * PX))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(PREVIEW, "spellfx.png"))
    from collections import Counter
    print("spells:", len(manifest), Counter(m["motif"] for m in manifest), Counter(m["cat"] for m in manifest))


if __name__ == "__main__":
    main()
