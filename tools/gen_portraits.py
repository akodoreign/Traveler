"""Turn-order portraits: face crops from dialog busts, with sprite-sheet portraits as the fallback.
Party / guest portraits get a gold frame, enemies a red one.
Writes resource/efx/portrait/<sheet basename>.png (88x88: 44-px design, nearest-neighbour x2).
Run: python -E tools/gen_portraits.py
     python -E tools/gen_portraits.py --busts-only
"""
import argparse
import json
import os
import re

import numpy as np
from PIL import Image, ImageDraw
from atomic_io import save_png, copy_file  # noqa: E402  (atomic writes: the game may be running)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
OUT = os.path.join(RES, "efx", "portrait")
SIZE, INNER = 44, 40
ALLY = ((214, 184, 96), (120, 96, 44))
FOE = ((190, 64, 56), (96, 30, 30))


FACE_X = 40          # gen_sprites2d: face centre column in an 80-px frame (13 + CX + 15)


_SPECS = None


def our_spec(name):
    """The generator spec behind one of our sheets (trav_*, side_*, hum_*), or None."""
    global _SPECS
    import sys
    sys.path.insert(0, HERE)
    import gen_sprites2d as g
    if _SPECS is None:
        import gen_human_enemies as he
        import gen_sidecast as sc
        _SPECS = {"trav_" + t["key"]: t for t in g.TRAVELERS}
        _SPECS.update({"side_" + c["key"]: sc.config(c) for c in sc.CAST})
        _SPECS.update({"hum_" + c["key"]: he.config(c) for c in he.ENEMIES})
    base = os.path.splitext(name)[0]
    if base.endswith("_ss"):
        base = base[:-3]
    if base in _SPECS:
        return _SPECS[base]
    if "__" in base:                                     # traveler look: trav_<key>__<weapon>_<hat|own>
        key, look = base.split("__", 1)
        w, h = look.split("_", 1)
        if key in _SPECS:
            return g.look_variant(_SPECS[key], w, "" if h == "own" else h)
    return None


def render_portrait_frame(T):
    """Battle idle frame 0 drawn for the portrait: no back banner, the head at the pre-2026-11-07 scale (0.75) so
    the face reads in the small turn-order frame."""
    import sys
    sys.path.insert(0, HERE)
    import gen_sprites2d as g
    T = dict(T)
    T.pop("sashimono", None)
    keep = g.HEAD_SCALE
    g.HEAD_SCALE = 0.75
    try:
        return g.frame(T, *g.FRAMES[g.BLOCK_AT["idle8"][0]])
    finally:
        g.HEAD_SCALE = keep


def head_crop(sheet, cols, rows, ours=False, T=None):
    fw, fh = sheet.width // cols, sheet.height // rows
    f = np.array(sheet.crop((0, 0, fw, fh)).convert("RGBA"))
    if T is not None:
        f = render_portrait_frame(T)
    a = f[..., 3] > 40
    if ours:                                             # our pipeline: fixed face-centred window
        rws = a.sum(axis=1)
        y0 = int(np.nonzero(rws >= 5)[0].min())
        return Image.fromarray(f).crop((FACE_X - 18, y0, FACE_X + 18, y0 + 32))
    rows = a.sum(axis=1)
    body = np.nonzero(rows >= 5)[0]                     # ignore thin spear tips / crests above the head
    if not len(body):
        return None
    y0, y1 = body.min(), body.max()
    h = max(14, int((y1 - y0 + 1) * 0.46))
    top = a[y0:y0 + h]
    cols_ = top.sum(axis=0)
    xs = np.nonzero(cols_ >= max(3, int(h * 0.25)))[0]          # ignore thin weapon shafts / props
    if not len(xs):
        xs = np.nonzero(top.any(axis=0))[0]
    x0, x1 = xs.min(), xs.max()
    crop = Image.fromarray(f).crop((x0, y0, x1 + 1, y0 + h))
    k = min(1.0, INNER / crop.width, INNER / crop.height)
    if k < 1.0:
        crop = crop.resize((max(1, int(crop.width * k)), max(1, int(crop.height * k))), Image.NEAREST)
    return crop


def frame(crop, ally, scale=1):
    hi, lo = ALLY if ally else FOE
    size = SIZE * scale
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=6 * scale,
                        fill=(28, 24, 32, 235), outline=lo, width=3 * scale)
    border = [scale, scale, size - 2 * scale, size - 2 * scale]
    d.rounded_rectangle(border, radius=5 * scale, outline=hi, width=scale)
    ox, oy = (size - crop.width) // 2, size - 3 * scale - crop.height
    im.alpha_composite(crop, (ox, max(3 * scale, oy)))
    # re-draw the inner border on top so the head sits inside the frame
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(border, radius=5 * scale, outline=hi, width=scale)
    return im.resize((SIZE * 2, SIZE * 2), Image.NEAREST)


def bust_crop(image, face=None):
    """Keep the face, hair and upper shoulders using the dialog bust's face anchor."""
    image = image.convert("RGBA")
    if face is None:
        bounds = image.getchannel("A").getbbox()
        if bounds is None:
            raise ValueError("Bust image is fully transparent")
        x0, upper, x1, bottom = bounds
        size = min(x1 - x0, bottom - upper)
        left = (x0 + x1 - size) // 2
    else:
        cx, top, chin = face
        if not (0 <= cx <= 1 and 0 <= top < chin <= 1):
            raise ValueError("Invalid bust face anchor: %r" % (face,))
        height = (chin - top) * image.height
        size = max(1, round(min(image.width, image.height, height * 2.1)))
        left = round(max(0, min(image.width - size, cx * image.width - size / 2)))
        upper = round(max(0, min(image.height - size, top * image.height - height * 0.55)))
    return image.crop((left, upper, left + size, upper + size)).resize(
        (INNER * 2, INNER * 2), Image.Resampling.LANCZOS)


def generate_bust_portraits():
    project = os.path.dirname(RES)
    with open(os.path.join(project, "plugin", "rokugan", "RokuganBustData.sk"), encoding="utf-8") as stream:
        table = stream.read().split("};", 1)[0]
    names = {json.loads(name): json.loads(key) for name, key in re.findall(
        r'\[("(?:\\.|[^"\\])*")\]\s*=\s*("(?:\\.|[^"\\])*")', table)}
    done = set()
    for kind in ("player", "enemy"):
        with open(os.path.join(project, "data", kind + ".json"), encoding="utf-8") as stream:
            characters = json.load(stream)
        for character in characters.values():
            if not isinstance(character, dict):
                continue
            name = character.get("name", "").split(" (", 1)[0]
            key = names.get(name)
            if key is None or (key, kind) in done:
                continue
            folder = os.path.join(RES, "bust", key)
            with open(os.path.join(folder, "faces.json"), encoding="utf-8") as stream:
                faces = json.load(stream)
            variant = "travel" if "travel" in faces and os.path.exists(
                os.path.join(folder, "travel_neutral.png")) else "base"
            source = "neutral.png" if variant == "base" else "travel_neutral.png"
            anchor = faces.get(variant)
            if anchor is None:
                print("bust portrait %s: no face anchor; cropping the upper bust" % key)
            with Image.open(os.path.join(folder, source)) as image:
                crop = bust_crop(image, anchor)
            save_png(frame(crop, kind == "player", scale=2),
                     os.path.join(OUT, "_bust_%s_%s.png" % (key, kind)))
            done.add((key, kind))
    print("bust portraits:", len(done))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--busts-only", action="store_true", help="Leave legacy sprite portraits unchanged")
    args = parser.parse_args()
    os.makedirs(OUT, exist_ok=True)
    generate_bust_portraits()
    if args.busts_only:
        return
    j = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
    done = set()
    for k, e in j.items():
        if not isinstance(e, dict) or "pic3d" not in e:
            continue
        name = os.path.basename(e["pic3d"])
        if name in done:
            continue
        path = os.path.join(RES, "enemy_pic", name)
        if not os.path.exists(path):
            continue
        cols, rows = (e.get("aniuv") or [1, 1])[:2]
        if "/enemy_pic2x/" in e["pic3d"]:
            rows = 11                                      # (the entry describes the 14x12 HD sheet; this is the 1x)
        ours = name.startswith(("trav_", "side_", "hum_"))
        crop = head_crop(Image.open(path), max(1, cols), max(1, rows), ours=ours, T=our_spec(name) if ours else None)
        if crop is None:
            continue
        ally = name.startswith(("trav_", "side_"))
        save_png(frame(crop, ally), os.path.join(OUT, os.path.splitext(name)[0] + ".png"))
        done.add(name)
    for name, text in (("_now", "THIS TURN"), ("_next", "NEXT"), ("_rumble", "RUMBLE")):   # bar row tags
        w = 8 + 6 * len(text)
        tag = Image.new("RGBA", (w, 13), (0, 0, 0, 0))
        d = ImageDraw.Draw(tag)
        d.rounded_rectangle([0, 0, w - 1, 12], radius=3, fill=(28, 24, 32, 220), outline=ALLY[1])
        d.text((4, 1), text, fill=ALLY[0])
        save_png(tag.resize((w * 2, 26), Image.NEAREST), os.path.join(OUT, name + ".png"))
    bar = Image.new("RGBA", (64, 8), (0, 0, 0, 0))                       # Rumble meter (plugin stretches these)
    d = ImageDraw.Draw(bar)
    d.rounded_rectangle([0, 0, 63, 7], radius=2, fill=(28, 24, 32, 200), outline=(150, 120, 90, 255))
    save_png(bar.resize((128, 16), Image.NEAREST), os.path.join(OUT, "_rumble_bar.png"))
    fill = Image.new("RGBA", (64, 4), (0, 0, 0, 0))
    for x in range(64):
        t = x / 63.0
        col = (int(200 + 50 * t), int(170 - 120 * t), int(60 - 30 * t), 255)   # sand -> ember red
        for y in range(4):
            fill.putpixel((x, y), tuple(min(255, int(c * (1.0 if y else 1.15))) if i < 3 else c for i, c in enumerate(col)))
    save_png(fill, os.path.join(OUT, "_rumble_fill.png"))
    print("portraits:", len(done))


if __name__ == "__main__":
    main()
