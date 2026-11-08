"""Close-up preview of arms and weapons across poses (no engine writes):
python -E tools/preview_arms.py [traveler keys...]  ->  _art/preview/arms.png"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402

KINDS = [("idle", 0), ("walk", 0), ("ready", 0), ("attack", 0), ("attack", 1), ("attack", 2), ("cast", 1),
         ("guard", 0), ("hurt", 0), ("victory", 0), ("fidle", 0), ("bidle", 0)]


def main():
    keys = sys.argv[1:] or [t["key"] for t in g.TRAVELERS]
    rows = [t for t in g.TRAVELERS if t["key"] in keys]
    W, H, Z = g.FW, g.FH, 3
    out = Image.new("RGBA", (W * len(KINDS) * Z, H * len(rows) * Z), (70, 98, 62, 255))
    for r, T in enumerate(rows):
        for c, (kind, i) in enumerate(KINDS):
            im = Image.fromarray(g.frame(T, kind, i), "RGBA").resize((W * Z, H * Z), Image.NEAREST)
            out.paste(im, (c * W * Z, r * H * Z), im)
    path = os.path.join(g.PREVIEW, "arms.png")
    out.save(path)
    print(path)


if __name__ == "__main__":
    main()
