"""White left where it should be cut out (user, 2026-11-11: "clean up edges that are white when they should be cut out"):
ranks busts by (1) near-white pixels on the silhouette edge (a halo of the white background) and (2) opaque patches of
near-pure white enclosed by the figure (background kept between hair and face, as on npc_akodo_rin).
python -E tools/bustfringe.py [key ...] [--sheet] [--top N]
  -> _art/preview/busts_fringe.txt, --sheet: _art/preview/busts_fringe_KK.png (on magenta: white edges stand out)
     key names given: _art/preview/bustcheck_<key>.png, every file of those keys on magenta"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
BUST = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "bust")
OUT = os.path.join(HERE, "..", "_art", "preview")


def measure(path):
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.int16)
    a = im[..., 3]
    rgb = im[..., :3]
    solid = a > 128
    white = (rgb.min(axis=2) >= 232) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 14)
    out = cv2.dilate((a < 32).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    edge = solid & out
    fringe = edge & white
    # pure white patches inside the figure (not touching the edge band): kept background
    pure = solid & (rgb.min(axis=2) >= 248) & ~out
    n, lab, st, _ = cv2.connectedComponentsWithStats(pure.astype(np.uint8), 8)
    patch = np.zeros_like(pure)
    parea = 0
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 150:
            patch |= lab == i
            parea += int(st[i, cv2.CC_STAT_AREA])
    return int(fringe.sum()), int(edge.sum()), parea, fringe, patch


def paint(path, fr=None, pa=None, tw=220, th=250):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 0, 255, 255))
    bg.alpha_composite(im)
    if fr is not None:
        px = np.asarray(bg).copy()
        px[pa] = (0, 255, 255, 255)
        bg = Image.fromarray(px)
    bg.thumbnail((tw - 8, th - 24))
    return bg


def sheet(items, out, tw=220, th=250, cols=6):
    sh = Image.new("RGB", (tw * cols, th * ((len(items) + cols - 1) // cols)), (30, 30, 36))
    dr = ImageDraw.Draw(sh)
    for j, (im, lab) in enumerate(items):
        sh.paste(im, ((j % cols) * tw + 4, (j // cols) * th + 2))
        dr.text(((j % cols) * tw + 4, (j // cols) * th + th - 20), lab[:34], fill=(255, 255, 160))
    sh.save(out)


def main():
    keys = [x for x in sys.argv[1:] if not x.startswith("--") and not x.isdigit()]
    if keys:                                                    # every file of these keys on magenta
        for key in keys:
            d = os.path.join(BUST, key)
            fs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
            items = []
            for f in fs:
                p = os.path.join(d, f)
                fr, ed, pa, frm, pam = measure(p)
                items.append((paint(p, frm, pam, 300, 340), "%s fr%d pa%d" % (f[:-4], fr, pa)))
            sheet(items, os.path.join(OUT, "bustcheck_%s.png" % key), 300, 340, 6)
            print("bustcheck_%s.png" % key)
        return
    rows = []
    for key in sorted(os.listdir(BUST)):
        d = os.path.join(BUST, key)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".png"):
                fr, ed, pa, _f, _p = measure(os.path.join(d, f))
                rows.append((fr + pa, fr, ed, pa, key + "/" + f))
    rows.sort(reverse=True)
    open(os.path.join(OUT, "busts_fringe.txt"), "w").write(
        "".join("%6d  fringe %5d of %5d edge px  white patch %5d  %s\n" % r for r in rows))
    print("worst:", "\n".join("%6d fr%5d pa%5d %s" % (r[0], r[1], r[3], r[4]) for r in rows[:15]))
    if "--sheet" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 36
        sel = rows[:top]
        for k in range(0, len(sel), 18):
            items = []
            for r in sel[k:k + 18]:
                p = os.path.join(BUST, r[4])
                _a, _b, _c, frm, pam = measure(p)
                items.append((paint(p, frm, pam), "%s %d/%d" % (r[4], r[1], r[3])))
            sheet(items, os.path.join(OUT, "busts_fringe_%02d.png" % (k // 18)))


if __name__ == "__main__":
    main()
