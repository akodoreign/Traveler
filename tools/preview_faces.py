"""Head close-ups for the whole cast (side idle + front idle), no engine writes:
python -E tools/preview_faces.py [travelers|side|all] [out.png]  ->  _art/preview/faces.png"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sprites2d as g  # noqa: E402
import gen_sidecast as sc  # noqa: E402


def cast(which):
    out = []
    if which in ("travelers", "all"):
        out += [(t["name"], t) for t in g.TRAVELERS]
    if which in ("side", "all"):
        out += [(c["name"], sc.config(c)) for c in sc.CAST]
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "travelers"
    path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(g.PREVIEW, "faces.png")
    C = cast(which)
    Z, cw, ch = int(os.environ.get("FZ", 5)), 30, 26     # head crop size (frame px)
    cols = int(os.environ.get("FCOLS", 6))
    rows = (len(C) + cols - 1) // cols
    cell_w, cell_h = cw * Z * 2 + 8, ch * Z + 14
    img = Image.new("RGBA", (cell_w * cols, cell_h * rows), (70, 98, 62, 255))
    d = ImageDraw.Draw(img)
    for n, (name, T) in enumerate(C):
        r, c = n // cols, n % cols
        x0, y0 = c * cell_w, r * cell_h
        for k, (kind, cx) in enumerate((("idle", 44), ("fidle", 40))):
            f = Image.fromarray(g.frame(T, kind, 0), "RGBA")
            a = f.split()[3].getbbox()                       # top of the figure
            top = a[1] if a else 0
            crop = f.crop((cx - cw // 2, top - 1, cx + cw // 2, top - 1 + ch)).resize((cw * Z, ch * Z), Image.NEAREST)
            img.paste(crop, (x0 + k * cw * Z, y0), crop)
        d.text((x0 + 3, y0 + ch * Z), name, fill=(255, 255, 255, 255))
    img.save(path)
    print(path, len(C))


if __name__ == "__main__":
    main()
