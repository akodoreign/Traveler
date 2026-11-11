"""Find see-through busts (user, 2026-11-11: "see through eyes, and hair ... the mirumoto's neck was all fucked up for
bath busts"): background removal also cut away white/pale parts INSIDE the figure (eye whites, pale hair, a neck).
A hole = transparent pixels the outside background can't reach (they're enclosed by the figure), or a big
transparent bite cut into the body from the side (open to the outside through a narrow gap).
python -E tools/busthole.py [--min 40] [--sheet]   -> _art/preview/busts_holes.txt (+ _art/preview/busts_holes_K.png)"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
BUST = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "bust")
OUT = os.path.join(HERE, "..", "_art", "preview")


def holes(path):
    a = np.asarray(Image.open(path).convert("RGBA"))[..., 3]
    solid = a > 128

    def fill(m):                                               # everything the border's background can't reach
        h, w = m.shape
        pad = np.zeros((h + 2, w + 2), np.uint8)
        pad[1:-1, 1:-1] = m
        ff = pad.copy()
        cv2.floodFill(ff, np.zeros((h + 4, w + 4), np.uint8), (0, 0), 2)
        return (ff[1:-1, 1:-1] != 2)

    filled = fill(solid.astype(np.uint8))
    enclosed = filled & ~solid                                  # fully enclosed holes
    k = np.ones((9, 9), np.uint8)
    closed = cv2.morphologyEx(solid.astype(np.uint8), cv2.MORPH_CLOSE, k, iterations=2)   # bites, narrow mouths
    bites = fill(closed) & ~solid & ~enclosed
    n, lab, stats, _c = cv2.connectedComponentsWithStats((enclosed | bites).astype(np.uint8), 8)
    big = [int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 12]
    return sum(big), len(big), enclosed | bites


def main():
    mn = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 40
    rows = []
    for key in sorted(os.listdir(BUST)):
        d = os.path.join(BUST, key)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".png"):
                area, n, mask = holes(os.path.join(d, f))
                if area >= mn:
                    rows.append((area, n, key + "/" + f))
    rows.sort(reverse=True)
    txt = os.path.join(OUT, "busts_holes.txt")
    open(txt, "w").write("".join("%6d px in %2d holes  %s\n" % r for r in rows))
    print("%d busts with see-through holes >= %d px -> %s" % (len(rows), mn, txt))
    if "--sheet" in sys.argv:                                   # holes painted magenta, 18 a sheet
        tw, th = 220, 250
        for k in range(0, len(rows), 18):
            chunk = rows[k:k + 18]
            sh = Image.new("RGB", (tw * 6, th * ((len(chunk) + 5) // 6)), (30, 30, 36))
            dr = ImageDraw.Draw(sh)
            for j, (area, n, f) in enumerate(chunk):
                im = Image.open(os.path.join(BUST, f)).convert("RGBA")
                _a, _n, mask = holes(os.path.join(BUST, f))
                bg = Image.new("RGBA", im.size, (40, 40, 48, 255))
                bg.alpha_composite(im)
                px = np.asarray(bg).copy()
                px[mask] = (255, 0, 255, 255)
                im2 = Image.fromarray(px)
                im2.thumbnail((tw - 8, th - 24))
                sh.paste(im2, ((j % 6) * tw + 4, (j // 6) * th + 2))
                dr.text(((j % 6) * tw + 4, (j // 6) * th + th - 20), "%s %d" % (f[:28], area), fill=(255, 255, 160))
            sh.save(os.path.join(OUT, "busts_holes_%02d.png" % (k // 18)))


if __name__ == "__main__":
    main()
