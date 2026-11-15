"""Placeholder sprites for the new foes (tools/new_foes.py; user 2026-11-14: "feel free to use a pixel script then tell
the agent handling the art they are place holders needing art"). Each is the nearest existing sheet, hue / saturation /
value shifted so the new foe reads as different at a glance, saved as resource/enemy_pic/ph_<key>.png and registered
as its EP id (a copy of the base EP entry: same frame grid and animations). The memo says PLACEHOLDER: the art agent
replaces the PNG with a drawn sheet of the same layout.
Run: python -E tools/gen_placeholder_foes.py"""
import colorsys
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import new_foes  # noqa: E402

RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")


def shift(img, hue_deg, sat_x, val_x):
    a = np.array(img.convert("RGBA")).astype(np.float32) / 255.0
    rgb, al = a[..., :3], a[..., 3:]
    mx, mn = rgb.max(-1), rgb.min(-1)
    v = mx
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.maximum(d, 1e-6), 0)
    gc = np.where(m, (mx - g) / np.maximum(d, 1e-6), 0)
    bc = np.where(m, (mx - b) / np.maximum(d, 1e-6), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = (h + hue_deg / 360.0) % 1.0
    s = np.clip(s * sat_x, 0, 1)
    v = np.clip(v * val_x, 0, 1)
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros_like(rgb)
    for k, (cr, cg, cb) in enumerate(((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))):
        sel = i == k
        out[..., 0] = np.where(sel, cr, out[..., 0])
        out[..., 1] = np.where(sel, cg, out[..., 1])
        out[..., 2] = np.where(sel, cb, out[..., 2])
    return Image.fromarray((np.concatenate([out, al], -1) * 255).round().astype(np.uint8), "RGBA")


def main():
    jpath = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jpath, encoding="utf-8"))
    n = 0
    for (eid, ep, key, name, base, hue, sat, val, *_rest) in new_foes.NEW_FOES:
        b = j.get(base)
        if not b:
            print("no base sprite", base, "for", name)
            continue
        src = os.path.join(RES, b["pic3d"].lstrip("/").replace("resource/", "", 1))
        out = os.path.join(RES, "enemy_pic", "ph_%s.png" % key)
        if os.path.exists(out) and "PLACEHOLDER" not in str((j.get(ep) or {}).get("memo", "PLACEHOLDER")):
            continue                                          # drawn art already installed: leave it
        shift(Image.open(src), hue, sat, val).save(out)
        x = json.loads(json.dumps(b))
        x.update({"name": {"en": name, "ja": name}, "pic3d": "/resource/enemy_pic/ph_%s.png" % key,
                  "memo": "PLACEHOLDER (tools/gen_placeholder_foes.py, from %s): needs drawn art" % base})
        j[ep] = x
        n += 1
    json.dump(j, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print("placeholder sprites:", n)


if __name__ == "__main__":
    main()
