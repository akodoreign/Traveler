"""Procedural enemy sprite sheets for Rokugan Traveler (Crab Ch1 set) + enemy_pic.json entries EP100-EP105.

- EP100 Goblin in a Hat : goblin.png + a drawn straw jingasa on every frame
- EP101 Nezumi Warrior  : rat.png recoloured brown + red headband + bamboo spear
- EP102 Cave Beetle     : drawn from scratch (4-frame leg cycle)
- EP103 Mamushi Viper   : snake.png recoloured olive-brown with dark bands
- EP104 Tide Crab       : crab.png recoloured slate-blue
- EP105 Nezumi Shaman   : rat.png recoloured grey-violet + bone headdress + shaman staff
Run: python -E tools/gen_enemy_art.py
"""
import colorsys
import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
PIC = os.path.join(RES, "enemy_pic")
PREVIEW = os.path.join(HERE, "..", "_art", "preview")
OUTLINE = (24, 16, 12, 255)


def load(name):
    return Image.open(os.path.join(PIC, name + ".png")).convert("RGBA")


def frames(img, n):
    w = img.width // n
    return [img.crop((i * w, 0, (i + 1) * w, img.height)) for i in range(n)]


def join(fr):
    out = Image.new("RGBA", (sum(f.width for f in fr), fr[0].height), (0, 0, 0, 0))
    for i, f in enumerate(fr):
        out.paste(f, (i * f.width, 0), f)
    return out


def recolor(img, hue_to=None, sat_mul=1.0, val_mul=1.0, keep=lambda h, s, v: False):
    a = np.array(img).astype(np.float32) / 255.0
    out = a.copy()
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            r, g, b, al = a[y, x]
            if al == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            if keep(h, s, v):
                continue
            if hue_to is not None and s > 0.08:
                h = hue_to
            out[y, x, :3] = colorsys.hsv_to_rgb(h, min(1, s * sat_mul), min(1, v * val_mul))
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")


def top_row(fr, x0, x1):
    a = np.array(fr)[:, x0:x1, 3]
    rows = np.where(a.max(axis=1) > 0)[0]
    return int(rows[0]) if len(rows) else 0


def goblin_hat():
    fr = frames(load("goblin"), 4)
    out = []
    for f in fr:
        f = f.copy()
        d = ImageDraw.Draw(f)
        ty = top_row(f, 12, 30)
        cx, base = 21, ty + 6
        # straw jingasa: flat wide cone, outlined, with weave lines
        cone = [(cx - 13, base), (cx, ty - 3), (cx + 13, base)]
        d.polygon(cone, fill=(214, 182, 96, 255), outline=OUTLINE)
        d.line([(cx - 13, base), (cx + 13, base)], fill=OUTLINE)
        for k in (-8, -3, 2, 7):
            d.line([(cx, ty - 1), (cx + k, base - 1)], fill=(170, 136, 60, 255))
        d.line([(cx - 10, base - 2), (cx + 10, base - 2)], fill=(240, 214, 140, 255))
        d.point((cx, ty - 3), fill=(120, 40, 30, 255))    # red tie knot
        out.append(f)
    return join(out)


def nezumi_warrior():
    fr = frames(load("rat"), 6)
    out = []
    for i, f in enumerate(fr):
        f = recolor(f, hue_to=0.07, sat_mul=1.4, val_mul=1.25, keep=lambda h, s, v: v > 0.8 or (h < 0.05 and s > 0.5))
        d = ImageDraw.Draw(f)
        ty = top_row(f, 36, 44)
        d.line([(34, ty + 3), (43, ty + 3)], fill=(200, 40, 36, 255), width=2)    # red headband
        sway = (i % 3) - 1
        d.line([(10 + sway, 4), (20 + sway, 36)], fill=OUTLINE, width=3)           # spear shaft (outline)
        d.line([(10 + sway, 4), (20 + sway, 36)], fill=(176, 150, 80, 255), width=1)
        d.polygon([(8 + sway, 0), (12 + sway, 1), (11 + sway, 7)], fill=(210, 214, 220, 255), outline=OUTLINE)
        out.append(f)
    return join(out)


def nezumi_shaman():
    fr = frames(load("rat"), 6)
    out = []
    for i, f in enumerate(fr):
        f = recolor(f, hue_to=0.76, sat_mul=0.6, val_mul=1.35, keep=lambda h, s, v: v > 0.8 or (h < 0.05 and s > 0.5))
        d = ImageDraw.Draw(f)
        ty = top_row(f, 36, 44) + 1
        for k, x in enumerate((35, 37, 39, 41)):                                 # bone headdress
            h = 5 if k % 2 else 7
            d.line([(x, ty + 2), (x, ty + 2 - h)], fill=OUTLINE, width=3)
            d.line([(x, ty + 2), (x, ty + 2 - h)], fill=(236, 228, 204, 255), width=1)
        glow = 120 + 40 * (i % 3)
        d.line([(6, 2), (12, 38)], fill=OUTLINE, width=3)                        # staff
        d.line([(6, 2), (12, 38)], fill=(110, 80, 50, 255), width=1)
        d.ellipse([(2, 0), (10, 7)], fill=(232, 224, 200, 255), outline=OUTLINE)  # skull knob
        d.point([(5, 3), (7, 3)], fill=(glow, 40, glow + 60, 255))
        out.append(f)
    return join(out)


def cave_beetle():
    W, H = 48, 40
    out = []
    for i in range(4):
        f = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(f)
        # legs (3 pairs, alternating phase)
        for k, lx in enumerate((14, 23, 32)):
            ph = (i + k) % 2
            d.line([(lx, 26), (lx - 6, 36 - 2 * ph)], fill=OUTLINE, width=3)
            d.line([(lx, 26), (lx - 6, 36 - 2 * ph)], fill=(52, 44, 60, 255), width=1)
            d.line([(lx + 2, 26), (lx + 7, 36 - 2 * (1 - ph))], fill=OUTLINE, width=3)
            d.line([(lx + 2, 26), (lx + 7, 36 - 2 * (1 - ph))], fill=(52, 44, 60, 255), width=1)
        bob = 1 if i % 2 else 0
        d.ellipse([(6, 8 + bob), (38, 32 + bob)], fill=(38, 46, 74, 255), outline=OUTLINE)       # carapace
        d.line([(22, 9 + bob), (22, 31 + bob)], fill=(20, 24, 40, 255))                            # wing seam
        d.arc([(10, 11 + bob), (30, 25 + bob)], 200, 300, fill=(120, 150, 210, 255), width=2)      # sheen
        d.ellipse([(34, 14 + bob), (45, 26 + bob)], fill=(30, 34, 52, 255), outline=OUTLINE)       # head
        d.line([(43, 16 + bob), (47, 11 + bob)], fill=OUTLINE, width=2)                            # mandibles
        d.line([(43, 24 + bob), (47, 28 + bob)], fill=OUTLINE, width=2)
        d.point([(40, 18 + bob)], fill=(220, 120, 60, 255))                                        # eye
        out.append(f)
    return join(out)


def viper():
    img = recolor(load("snake"), hue_to=0.10, sat_mul=0.55, val_mul=0.85)
    return img


def tide_crab():
    return recolor(load("crab"), hue_to=0.58, sat_mul=0.45, val_mul=1.0)


ATTACK_IDS = ["punch1", "slash1", "stick1", "bow1", "atk", "magic1", "spell", "blast1"]


def animate(idle_frames):
    """Idle row + attack row (windup, lunge+smear, follow, recover, hold) + hurt row (knockback flash, recoil, hold).
    Enemies face right (toward the party). Canvas widened by PAD on both sides for the lunge."""
    PAD = 8
    w, h = idle_frames[0].size
    W = w + PAD * 2
    cols = max(len(idle_frames), 5)
    sheet = Image.new("RGBA", (W * cols, h * 3), (0, 0, 0, 0))

    def put(img, col, row, dx=0, tint=None, smear=False):
        f = Image.new("RGBA", (W, h), (0, 0, 0, 0))
        src = img
        if tint is not None:
            a = np.array(img).astype(np.float32)
            a[..., :3] = a[..., :3] * (1 - tint[3]) + np.array(tint[:3]) * tint[3]
            src = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
        f.paste(src, (PAD + dx, 0), src)
        if smear:
            d = ImageDraw.Draw(f)
            cx, cy, r = PAD + dx + w - 6, h // 2, h // 3
            for k, al in ((0, 255), (2, 170), (4, 90)):
                d.arc([cx - r - k, cy - r - k, cx + r + k, cy + r + k], -75, 55, fill=(255, 255, 255, al), width=1)
        sheet.paste(f, (col * W, row * h), f)

    for i, fr in enumerate(idle_frames):
        put(fr, i, 0)
    base = idle_frames[0]
    put(base, 0, 1, dx=-3)                                   # windup
    put(base, 1, 1, dx=7, smear=True)                         # lunge + smear
    put(base, 2, 1, dx=5)                                     # follow-through
    put(base, 3, 1, dx=2)                                     # recover
    put(base, 4, 1, dx=0)                                     # hold
    put(base, 0, 2, dx=-4, tint=(255, 90, 80, 0.55))          # hit flash
    put(base, 1, 2, dx=-2)                                    # recoil
    put(base, 2, 2, dx=-1)                                    # hold
    animap = [{"id": "stand", "st": 0, "en": len(idle_frames), "spd": 5.0, "loop": True, "replay": False}]
    for aid in ATTACK_IDS:
        animap.append({"id": aid, "st": cols, "en": cols + 4, "spd": 12.0, "loop": False, "replay": True})
    for aid in ("damage", "avoid"):
        animap.append({"id": aid, "st": cols * 2, "en": cols * 2 + 2, "spd": 8.0, "loop": False, "replay": True})
    animap.append({"id": "die", "st": cols * 2, "en": cols * 2 + 1, "spd": 1.0, "loop": True, "replay": False})
    return sheet, (cols, 3), animap


def goblin_plain():
    return load("goblin")


def main():
    made = {
        "EP106": ("goblin_anim", goblin_plain(), 4, "Goblin"),
        "EP100": ("goblin_hat", goblin_hat(), 4, "Goblin in a Hat"),
        "EP101": ("nezumi_warrior", nezumi_warrior(), 6, "Nezumi Warrior"),
        "EP102": ("cave_beetle", cave_beetle(), 4, "Cave Beetle"),
        "EP103": ("mamushi", viper(), 6, "Mamushi Viper"),
        "EP104": ("tide_crab", tide_crab(), 4, "Tide Crab"),
        "EP105": ("nezumi_shaman", nezumi_shaman(), 6, "Nezumi Shaman"),
    }
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    tmpl = j["EP000"]
    os.makedirs(PREVIEW, exist_ok=True)
    rows = []
    for epid, (fname, img, n, label) in made.items():
        sheet, (cols, nrows), animap = animate(frames(img, n))
        sheet.save(os.path.join(PIC, fname + ".png"))
        e = json.loads(json.dumps(tmpl))
        e["name"] = {"en": label, "ja": label}
        e["pic3d"] = "/resource/enemy_pic/%s.png" % fname
        e["aniuv"] = [cols, nrows]
        e["animap"] = animap
        e["memo"] = "procedural (tools/gen_enemy_art.py): idle / attack / hurt rows"
        e["scale"] = (e.get("scale") or 1.0) * 0.5          # = gen_sprites2d.CAST_SCALE
        j[epid] = e
        rows.append(sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST))
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (60, 60, 70, 255))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y), r)
        y += r.height + 8
    sheet.save(os.path.join(PREVIEW, "enemies_crab_ch1.png"))
    print("wrote", list(made))


if __name__ == "__main__":
    main()
