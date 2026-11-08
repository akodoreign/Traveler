"""Procedurally generate the eight travelers' character models for RPG-Cobo.

Approach: each traveler reuses a base voxel rig from the default asset pack and gets a clan colour scheme via the
chara_vox "pal" override list (no new .vox files needed; rigs and motions stay compatible).
- skin tones are kept;
- hair (non-skin colours in the head part) is remapped to the traveler's hair colour;
- clothing (non-skin colours in body/arms/legs) is remapped onto the clan ramp by lightness.
Outputs: entries CV100-CV107 merged into resource/chara_vox.json, and _art/preview/travelers.png.
Run: python -E tools/gen_travelers.py
"""
import colorsys
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import voxlib  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "_tools", "rpgcobo-tool", "project")
RES = os.path.join(ROOT, "resource")
OUT_PREVIEW = os.path.join(os.path.dirname(__file__), "..", "_art", "preview")

# id, name, base CV id, clan hue (deg), clan sat, accent hue, hair rgb
TRAVELERS = [
    ("CV100", "Hiruma Natsuko", "CV011", 214, 0.38, 0, (40, 32, 28)),     # Crab: slate blue-grey
    ("CV101", "Kakita Rensei", "CV003", 200, 0.42, 210, (236, 236, 240)),  # Crane: pale blue, white-dyed hair
    ("CV102", "Kitsuki Gendo", "CV026", 140, 0.50, 50, (30, 30, 34)),      # Dragon: green
    ("CV103", "Akodo Shizue", "CV001", 44, 0.78, 30, (70, 44, 26)),        # Lion: gold
    ("CV104", "Isawa Haruki", "CV020", 16, 0.80, 40, (34, 26, 24)),        # Phoenix: flame orange
    ("CV105", "Shosuro Mitsue", "CV007", 354, 0.78, 0, (22, 18, 20)),      # Scorpion: crimson and black
    ("CV106", "Ide Tamotsu", "CV027", 276, 0.50, 45, (78, 50, 32)),        # Unicorn: purple
    ("CV107", "Sayo", "CV004", 30, 0.38, 100, (58, 38, 26)),               # Ronin: earth brown
]


def hsv(rgb):
    r, g, b = [c / 255.0 for c in rgb[:3]]
    return colorsys.rgb_to_hsv(r, g, b)


def is_skin(rgb):
    h, s, v = hsv(rgb)
    return (0.02 <= h <= 0.12) and (0.15 <= s <= 0.62) and v >= 0.55


def to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0, min(1, s)), max(0, min(1, v)))
    return (round(r * 255), round(g * 255), round(b * 255))


def build(entry, chara_vox):
    cid, name, base, hue, sat, acc_hue, hair = entry
    d = chara_vox[base]
    vox = voxlib.read_vox(os.path.join(RES, d["vox"].replace("/resource/", "")))
    pal = voxlib.apply_pal(vox["palette"], d["pal"])
    head, face, body = set(), set(), set()
    counts = {}
    for mid, _ in vox["placed"]:
        n = vox["names"].get(mid, "")
        usage = voxlib.color_usage(vox["models"][mid])
        used = set(usage.keys())
        (head if n.startswith("head") else face if n.startswith("face") else body).update(used)
        if not (n.startswith("head") or n.startswith("face")):
            for k, c in usage.items():
                counts[k] = counts.get(k, 0) + c
    overrides = dict((d["pal"][i], d["pal"][i + 1]) for i in range(0, len(d["pal"]), 2))
    hair_h, hair_s, hair_v = hsv(hair)
    # hair: non-skin head colours, by lightness relative to the brightest
    hair_idx = [i for i in head - face - body if not is_skin(pal[i - 1])]
    if hair_idx:
        vmax = max(hsv(pal[i - 1])[2] for i in hair_idx) or 1
        for i in hair_idx:
            v = hsv(pal[i - 1])[2] / vmax
            overrides[i] = voxlib.encode_col(*to_rgb(hair_h, hair_s, hair_v * (0.65 + 0.35 * v) + 0.12 * v))
    # clothing: big colour areas take the clan colour; small areas (< 6% of body voxels) become accent trim
    skin = {i for i in head | face if is_skin(pal[i - 1])}   # real skin also shows on the head/face
    cloth = [i for i in body - face - set(hair_idx) if i not in skin]
    total = sum(counts.get(i, 0) for i in cloth) or 1
    for i in cloth:
        rgb = pal[i - 1]
        h0, s0, v0 = hsv(rgb)
        trim = counts.get(i, 0) / total < 0.06 and s0 > 0.25
        hh = (acc_hue if trim else hue) / 360.0
        if s0 < 0.12 and v0 < 0.35:          # near-blacks stay dark, faintly tinted
            new = to_rgb(hh, sat * 0.35, v0)
        elif s0 < 0.12:                      # whites / greys / metal: light clan tint
            new = to_rgb(hh, sat * 0.30, min(1.0, v0 * 0.95 + 0.05))
        else:
            new = to_rgb(hh, sat * (0.75 + 0.25 * s0), 0.30 + 0.70 * v0)
        overrides[i] = voxlib.encode_col(*new)
    newpal = []
    for k in sorted(overrides):
        newpal += [k, overrides[k]]
    out = dict(d)
    out["name"] = {"en": name, "ja": name}
    out["pal"] = newpal
    return out, vox


def main():
    path = os.path.join(RES, "chara_vox.json")
    cv = json.load(open(path, encoding="utf-8"))
    tiles = []
    for e in TRAVELERS:
        entry, vox = build(e, cv)
        cv[e[0]] = entry
        model = voxlib.merge_scene(vox, skip=lambda n: n.startswith("face") and n != "face0")
        img = voxlib.render_front(model, voxlib.apply_pal(vox["palette"], entry["pal"]), scale=6)
        lab = Image.new("RGBA", (img.width, img.height + 22), (40, 40, 48, 255))
        lab.paste(img, (0, 0), img)
        ImageDraw.Draw(lab).text((6, img.height + 4), e[1], fill=(230, 230, 230, 255))
        tiles.append(lab)
    json.dump(cv, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    os.makedirs(OUT_PREVIEW, exist_ok=True)
    W = sum(t.width for t in tiles) + 8 * len(tiles)
    sheet = Image.new("RGBA", (W, max(t.height for t in tiles)), (40, 40, 48, 255))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0), t)
        x += t.width + 8
    sheet.save(os.path.join(OUT_PREVIEW, "travelers.png"))
    print("wrote", [e[0] for e in TRAVELERS])


if __name__ == "__main__":
    main()
