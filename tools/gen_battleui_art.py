"""Art for the battle screen (RokuganBattleUI.sk): weakness symbols, unknown dot, shield, panel, bars, gems ->
resource/efx/battleui/, and the battle-only button/row clips in the shared UI atlas (presetui/uiimg.ss.webp + .ssg;
the originals are kept in _tools/data_orig/ui). Colours: ink #0e1116, hairline gold #c9a86a, selection lacquer #8c2f28.
Run: python -E tools/gen_battleui_art.py, then tools/patch_ui.py"""
import io
import json
import math
import os
import re
import shutil
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project"))
OUT = os.path.join(PROJ, "resource", "efx", "battleui")
BK = os.path.join(HERE, "..", "_tools", "data_orig", "ui")
os.makedirs(OUT, exist_ok=True)
os.makedirs(BK, exist_ok=True)
INK, GOLD, RED = (14, 17, 22), (201, 168, 106), (140, 47, 40)
S, ICON = 8, 64
W, c = ICON * S, ICON * S / 2
STEEL, WHITE, DK = (222, 228, 236, 255), (250, 250, 246, 255), (40, 44, 54, 255)
WOOD, GILT, WRAP = (196, 150, 96, 255), (210, 180, 110, 255), (190, 70, 60, 255)
WPN = ((54, 60, 72, 255), (176, 184, 198, 255))


def disc(fill, rim):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = W * 0.46
    d.ellipse([c - r, c - r, c + r, c + r], fill=rim)
    r = W * 0.405
    d.ellipse([c - r, c - r, c + r, c + r], fill=fill)
    return im, d


def P(*xy):
    return [(c + x * W * 0.40, c + y * W * 0.40) for x, y in xy]


def L(d, pts, w, col):
    d.line(P(*pts), fill=col, width=int(w * W), joint="curve")


def arc(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def katana(d):
    L(d, arc(-1.5, 1.5, 2.25, -66, -24), 0.075, STEEL)
    L(d, [(-0.62, 0.40), (-0.30, 0.72)], 0.08, GILT)
    L(d, [(-0.46, 0.56), (-0.76, 0.86)], 0.085, WRAP)


def yari(d):
    L(d, [(-0.78, 0.78), (0.32, -0.32)], 0.05, WOOD)
    d.polygon(P((0.82, -0.82), (0.16, -0.46), (0.46, -0.16)), fill=STEEL)


def tanto(d):
    d.polygon(P((0.66, -0.66), (0.22, -0.40), (-0.14, -0.04), (0.04, 0.14), (0.40, -0.22)), fill=STEEL)
    L(d, [(-0.24, -0.08), (0.08, 0.24)], 0.06, GILT)
    L(d, [(-0.06, 0.08), (-0.52, 0.54)], 0.09, WRAP)


def tetsubo(d):
    L(d, [(-0.76, 0.76), (-0.20, 0.20)], 0.07, WOOD)
    L(d, [(-0.20, 0.20), (0.56, -0.56)], 0.20, STEEL)
    for t in (-0.05, 0.16, 0.37):
        for s in (-1, 1):
            x, y, r = t + s * 0.16, -t + s * 0.16, 0.055
            d.ellipse(P((x - r, y - r), (x + r, y + r)), fill=DK)


def yumi(d):
    a = arc(-0.55, 0, 1.08, -62, 62)
    L(d, a, 0.07, WOOD)
    L(d, [a[0], a[-1]], 0.022, WHITE)


def bo(d):
    L(d, [(-0.72, 0.72), (0.72, -0.72)], 0.085, WOOD)
    for s in (-1, 1):
        L(d, [(s * 0.72, -s * 0.72), (s * 0.52, -s * 0.52)], 0.10, STEEL)


def fire(d):
    d.polygon(P((0.02, -0.82), (0.26, -0.40), (0.58, -0.14), (0.60, 0.30), (0.34, 0.66), (-0.30, 0.66), (-0.60, 0.30),
                (-0.54, -0.10), (-0.30, 0.06), (-0.22, -0.42)), fill=(255, 196, 92, 255))
    d.polygon(P((0.02, -0.14), (0.28, 0.20), (0.20, 0.58), (-0.20, 0.58), (-0.30, 0.24)), fill=(255, 246, 214, 255))


def water(d):
    d.polygon(P((0, -0.80), *arc(0, 0.22, 0.48, -20, 200)), fill=(206, 236, 255, 255))


def air(d):
    L(d, [(-0.70, -0.30), (0.26, -0.30)] + arc(0.26, -0.52, 0.22, 90, -150), 0.075, WHITE)
    L(d, [(-0.70, 0.02), (0.46, 0.02)] + arc(0.46, -0.20, 0.22, 90, -120), 0.075, WHITE)
    L(d, [(-0.46, 0.34), (0.20, 0.34)] + arc(0.20, 0.54, 0.20, -90, 130), 0.075, WHITE)


def earth(d):
    d.polygon(P((-0.82, 0.58), (-0.22, -0.44), (0.06, 0.04), (0.28, -0.20), (0.82, 0.58)), fill=(236, 214, 170, 255))
    d.polygon(P((-0.22, -0.44), (-0.40, -0.14), (-0.22, -0.20), (-0.06, -0.14)), fill=WHITE)


def void(d):
    L(d, arc(0, 0, 0.56, -60, 250), 0.13, (232, 214, 255, 255))


def jade(d):
    d.polygon(P((0, -0.74), (0.64, -0.37), (0.64, 0.37), (0, 0.74), (-0.64, 0.37), (-0.64, -0.37)), fill=(150, 236, 180, 255))
    d.polygon(P((0, -0.74), (0.64, -0.37), (0, 0), (-0.64, -0.37)), fill=(214, 255, 226, 255))


def unarmed(d):
    d.rounded_rectangle(P((-0.56, -0.36), (0.56, 0.62)), radius=int(W * 0.08), fill=(244, 206, 164, 255))
    for x in (-0.28, 0.0, 0.28):
        L(d, [(x, -0.40), (x, -0.02)], 0.03, (120, 72, 44, 255))
    d.rounded_rectangle(P((-0.58, 0.02), (0.20, 0.30)), radius=int(W * 0.05), fill=(226, 180, 136, 255))


def crystal(d):
    d.polygon(P((0, -0.82), (0.50, -0.20), (0, 0.82), (-0.50, -0.20)), fill=(214, 232, 255, 255))
    d.polygon(P((0, -0.82), (0.50, -0.20), (0, -0.04), (-0.50, -0.20)), fill=WHITE)


ICONS = [("katana", katana, WPN), ("yari", yari, WPN), ("tanto", tanto, WPN), ("tetsubo", tetsubo, WPN),
         ("yumi", yumi, WPN), ("bo", bo, WPN),
         ("fire", fire, ((168, 46, 30, 255), (240, 150, 70, 255))),
         ("water", water, ((28, 84, 150, 255), (120, 190, 240, 255))),
         ("air", air, ((64, 130, 120, 255), (170, 230, 214, 255))),
         ("earth", earth, ((98, 72, 40, 255), (206, 172, 112, 255))),
         ("void", void, ((46, 28, 78, 255), (178, 140, 232, 255))),
         ("jade", jade, ((22, 96, 66, 255), (120, 220, 160, 255))),
         ("unarmed", unarmed, ((120, 72, 44, 255), (232, 180, 130, 255))),
         ("crystal", crystal, ((66, 90, 160, 255), (190, 214, 255, 255)))]


def save_icon(im, name, size=ICON):
    im.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name + ".png"))


for name, fn, (f, r) in ICONS:
    im, d = disc(f, r)
    fn(d)
    save_icon(im, "w_" + name)
im, d = disc((6, 6, 8, 255), (112, 116, 124, 255))
save_icon(im, "w_unknown")
im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.polygon(P((0, -0.9), (0.76, -0.62), (0.70, 0.22), (0, 0.92), (-0.70, 0.22), (-0.76, -0.62)), fill=GOLD + (255,))
d.polygon(P((0, -0.70), (0.58, -0.48), (0.52, 0.14), (0, 0.68), (-0.52, 0.14), (-0.58, -0.48)), fill=(38, 44, 58, 255))
save_icon(im, "shield")
for name, f, r in (("gem_on", (116, 196, 255, 255), (232, 246, 255, 255)), ("gem_off", (30, 34, 44, 255), (92, 98, 110, 255))):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(P((0, -1), (0.76, 0), (0, 1), (-0.76, 0)), fill=r)
    d.polygon(P((0, -0.68), (0.5, 0), (0, 0.68), (-0.5, 0)), fill=f)
    save_icon(im, name, 32)
Image.new("RGBA", (8, 8), (255, 255, 255, 255)).save(os.path.join(OUT, "white.png"))


def panel(w, h, boxes):
    k = 4
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in boxes:
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=14 * k, fill=INK + (214,), outline=GOLD + (150,),
                            width=k + k // 2)
    return im.resize((w, h), Image.LANCZOS)


panel(1008, 220, [(8, 8, 288, 212), (298, 8, 1000, 212)]).save(os.path.join(OUT, "panel.png"))
panel(412, 173, [(2, 2, 410, 171)]).save(os.path.join(OUT, "enemybox.png"))
panel(976, 96, [(2, 2, 974, 94)]).save(os.path.join(OUT, "popover.png"))
band = np.zeros((8, 256, 4), np.uint8)
band[..., :3] = 255
band[..., 3] = np.linspace(112, 34, 256).astype(np.uint8)[None, :]
Image.fromarray(band, "RGBA").save(os.path.join(OUT, "band.png"))
panel(1008, 220, [(8, 8, 1000, 212)]).save(os.path.join(OUT, "panel_wide.png"))

def msgbox(w, h, radius=22):
    k, m = 4, 7
    base = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    s = Image.new("L", base.size, 0)
    ImageDraw.Draw(s).rounded_rectangle([m * k, (m + 2) * k, (w - m) * k, (h - m + 2) * k], radius=radius * k, fill=150)
    base.putalpha(s.filter(ImageFilter.GaussianBlur(4 * k)))
    base = Image.composite(base, Image.new("RGBA", base.size, (0, 0, 0, 0)), base.getchannel("A"))
    g = np.zeros((h * k, w * k, 4), np.uint8)
    t_ = np.linspace(0, 1, h * k)[:, None]
    g[..., 0] = (24 - 10 * t_).astype(np.uint8)
    g[..., 1] = (28 - 11 * t_).astype(np.uint8)
    g[..., 2] = (38 - 16 * t_).astype(np.uint8)
    g[..., 3] = 240
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([m * k, m * k, (w - m) * k, (h - m) * k], radius=radius * k, fill=255)
    base.paste(Image.fromarray(g, "RGBA"), (0, 0), mask)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([m * k, m * k, (w - m) * k, (h - m) * k], radius=radius * k, outline=GOLD + (235,), width=k + k // 2)
    d.rounded_rectangle([(m + 4) * k, (m + 4) * k, (w - m - 4) * k, (h - m - 4) * k], radius=(radius - 4) * k, outline=GOLD + (46,), width=k)
    return base.resize((w, h), Image.LANCZOS)


msgbox(920, 160).save(os.path.join(OUT, "msgbox.png"))
msgbox(920, 232).save(os.path.join(OUT, "msgbox_tall.png"))
k_ = 4
pill = Image.new("RGBA", (292 * k_, 44 * k_), (0, 0, 0, 0))
ImageDraw.Draw(pill).rounded_rectangle([3 * k_, 3 * k_, 289 * k_, 41 * k_], radius=19 * k_, fill=(20, 23, 32, 250), outline=GOLD + (235,), width=k_ + k_ // 2)
pill.resize((292, 44), Image.LANCZOS).save(os.path.join(OUT, "namepill.png"))

panel(1008, 220, [(298, 8, 1000, 212)]).save(os.path.join(OUT, "panel_party.png"))


def pma(im):
    a = np.asarray(im.convert("RGBA")).astype(float)
    a[..., :3] *= a[..., 3:] / 255.0
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def clip(fill, line=None, size=42):
    k = 4
    s = size * k
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([3 * k, 3 * k, s - 3 * k, s - 3 * k], radius=5 * k, fill=fill, outline=line, width=2 * k if line else 0)
    return im.resize((size, size), Image.LANCZOS)


wp, sg = os.path.join(PROJ, "presetui", "uiimg.ss.webp"), os.path.join(PROJ, "presetui", "uiimg.ssg")
for f in (wp, sg):
    if not os.path.exists(os.path.join(BK, os.path.basename(f))):
        shutil.copy(f, BK)
A = Image.open(os.path.join(BK, "uiimg.ss.webp")).convert("RGBA")
txt = open(os.path.join(BK, "uiimg.ssg"), encoding="utf-8", newline="").read()


def put(xy, im):
    A.paste(Image.new("RGBA", im.size, (0, 0, 0, 0)), xy)
    A.paste(im, xy)


def box(cid):
    m = re.search(r'"clipid":"%s","subbnd":\[(\d+),(\d+),(\d+),(\d+)' % re.escape(cid), txt)
    return tuple(int(v) for v in m.groups())


put((0, 760), clip((255, 255, 255, 12)))                    # bctl_n: a resting command
put((44, 760), clip(RED + (240,), GOLD + (235,)))           # bctl_g: the focused command
i = txt.index('{"resorate"', txt.index("cliplist"))
txt = txt[:i] + ('{"resorate":150,"stretch":[14.0,14.0,14.0,14.0,0],"clipid":"bctl_n.png","subbnd":[0,760,42,42,0]},'
                 '{"resorate":150,"stretch":[16.0,16.0,16.0,16.0,0],"clipid":"bctl_g.png","subbnd":[44,760,42,42,0]},') + txt[i:]
for cid, im in (("item_gb.png", clip(RED + (240,), GOLD + (235,))), ("member.png", Image.new("RGBA", (60, 60), (0, 0, 0, 0))),
                ("member_b.png", clip(GOLD + (46,), GOLD + (230,), size=60))):
    x, y, w_, h_ = box(cid)
    put((x, y), im.resize((w_, h_)))
def rect(w, h, fill, line=None, inset=10, radius=8):
    k = 4
    im = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([inset * k, inset * k, (w - inset) * k, (h - inset) * k], radius=radius * k, fill=fill, outline=line,
                                         width=k + k // 2 if line else 0)
    return im.resize((w, h), Image.LANCZOS)


EXTRA = [("msgwin.png", [100, 760, 104, 104], [36.0, 36.0, 36.0, 36.0, 0], rect(104, 104, INK + (250,), GOLD + (255,), radius=24)),   # the dialog box
         ("mfram.png", [210, 760, 38, 38], [16.0, 16.0, 16.0, 16.0, 0], Image.new("RGBA", (38, 38), (0, 0, 0, 0))),        # no heavy frame
         ("msgplate1.png", [254, 760, 104, 72], [36.0, 30.0, 36.0, 30.0, 0], rect(104, 72, INK + (240,), GOLD + (200,), inset=14, radius=6))]  # name plate
for cid, b, st, im in EXTRA:
    put((b[0], b[1]), im)
    i = txt.index('{"resorate"', txt.index("cliplist"))
    txt = txt[:i] + json.dumps({"resorate": 150, "stretch": st, "clipid": cid, "subbnd": b + [0]}, separators=(",", ":")) + "," + txt[i:]
buf = io.BytesIO()
A.save(buf, "WEBP", lossless=True, exact=True)                  # the engine reads the clip list from a custom skmt chunk
vp8l = buf.getvalue()[12:]                                       # (and premultiplies on load: pma 1)
if vp8l[:4] != b"VP8L":
    raise SystemExit("expected a lossless webp")
orig = open(os.path.join(BK, "uiimg.ss.webp"), "rb").read()
j = orig.index(b"skmt")
meta = json.loads(orig[j + 8:j + 8 + struct.unpack("<I", orig[j + 4:j + 8])[0]].decode("utf-8"))
meta["cliplist"] = [dict(resorate=150, stretch=[14.0, 14.0, 14.0, 14.0, 0], clipid="bctl_n.png", subbnd=[0, 760, 42, 42, 0]),
                    dict(resorate=150, stretch=[16.0, 16.0, 16.0, 16.0, 0], clipid="bctl_g.png", subbnd=[44, 760, 42, 42, 0])] + meta["cliplist"]
meta["cliplist"] = [dict(resorate=150, stretch=st, clipid=cid, subbnd=b + [0]) for cid, b, st, im in EXTRA] + meta["cliplist"]
mb = json.dumps(meta, separators=(",", ":")).encode("utf-8")
def chunk(tag, d):
    return tag + struct.pack("<I", len(d)) + d + (bytes(1) if len(d) & 1 else b"")
body = chunk(b"VP8X", bytes([0x10, 0, 0, 0]) + (A.width - 1).to_bytes(3, "little") + (A.height - 1).to_bytes(3, "little")) + vp8l + chunk(b"skmt", mb)
open(wp, "wb").write(b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body)
open(sg, "w", encoding="utf-8", newline="").write(txt)
names = ["w_" + n[0] for n in ICONS] + ["w_unknown", "shield"]
sheet = Image.new("RGB", (len(names) * 72, 130), (60, 66, 60))
for n, k in enumerate(names):
    f = Image.open(os.path.join(OUT, k + ".png")).convert("RGBA")
    sheet.paste(f, (n * 72 + 4, 4), f)
    s = f.resize((24, 24), Image.LANCZOS)
    sheet.paste(s, (n * 72 + 24, 90), s)
sheet.save(os.path.join(HERE, "..", "_art", "preview", "battleui_icons.png"))
print("ok", len(ICONS))
