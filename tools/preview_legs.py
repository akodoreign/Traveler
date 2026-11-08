"""Close-up preview of legs across builds and poses (no engine writes):
python -E tools/preview_legs.py [out.png]  ->  _art/preview/legs.png (travelers + side-cast build samples)"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402
import gen_sidecast as sc  # noqa: E402

KINDS = [("idle", 0), ("walk", 0), ("walk", 1), ("walk", 2), ("walk", 3), ("ready", 0), ("attack", 1),
         ("hurt", 0), ("guard", 0), ("ko", 0)]
SIDE = ["kisada", "yosai", "kiyo", "gonta", "satomi"]          # heavy, monk, peasant (f), peasant big, robe


def rows():
    out = [(t["name"], t) for t in g.TRAVELERS]
    for k in SIDE:
        c = next(c for c in sc.CAST if c["key"] == k)
        out.append((c["name"], sc.config(c)))
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(g.PREVIEW, "legs.png")
    x0, y0, x1, y1 = 22, 44, 66, 68                           # hips to ground
    Z = 4
    w, h = (x1 - x0) * Z, (y1 - y0) * Z
    R = rows()
    img = Image.new("RGBA", (w * len(KINDS), h * len(R)), (70, 98, 62, 255))
    for r, (_, T) in enumerate(R):
        for c, (kind, i) in enumerate(KINDS):
            f = Image.fromarray(g.frame(T, kind, i), "RGBA").crop((x0, y0, x1, y1)).resize((w, h), Image.NEAREST)
            img.paste(f, (c * w, r * h), f)
    img.save(path)
    print(path)


if __name__ == "__main__":
    main()
