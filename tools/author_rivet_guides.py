"""Author armor fasteners from installed RPG-Cobo bind-space geometry and its original UVs."""
import argparse
from pathlib import Path
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates


BASE = Path("_tools/rpgcobo-tool/project/resource/native_tailoring")
ITEMS = ("A173", "A110", "A141")


def load_native_mesh(path):
    data = path.read_bytes()
    if not data.startswith(b"SMDL\0\1"):
        raise ValueError(f"Unexpected model format in {path.name}")
    at = 14
    datatypes = {1: ">f4", 2: ">f2", 3: ">u2", 4: ">i2", 5: "u1", 6: "i1", 7: ">u4", 8: ">i4"}
    attrs = {}
    for _ in range(data[9]):
        role, kind, normalized, dimensions, _, _, _, count = struct.unpack_from(">6BII", data, at)
        at += 14
        dtype = np.dtype(datatypes[kind])
        if role in (0, 4):
            entry = np.frombuffer(data, dtype=dtype, count=count * dimensions, offset=at)
            entry = entry.reshape(count, dimensions).astype(np.float32)
            attrs[role] = entry / np.iinfo(dtype).max if normalized else entry
        at += dtype.itemsize * count * dimensions
    material_count = data[at + 4]
    at += 5
    faces = []
    for _ in range(material_count):
        mode, _, _, kind, length, count = struct.unpack_from(">4BII", data, at)
        at += 12
        if mode != 4:
            raise ValueError(f"Expected triangles in {path.name}")
        faces.append(np.frombuffer(data, dtype=datatypes[kind], count=count, offset=at).reshape(-1, 3))
        at += length + 4
    return attrs[0], attrs[4][:, :2], np.concatenate(faces).astype(np.int32)


def tex_array(path):
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.


def barycentric(xy, px, py):
    (x0, y0), (x1, y1), (x2, y2) = xy
    determinant = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(determinant) < 1.e-6:
        return None
    a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / determinant
    b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / determinant
    return a, b, 1. - a - b


def projection(verts):
    left = float(np.floor(min(verts[:, 2])) - 3)
    right = float(np.ceil(max(verts[:, 2])) + 3)
    top = float(np.ceil(max(verts[:, 1])) + 3)
    floor = float(np.floor(min(verts[:, 1])) - 3)
    unit = 9 if top - floor < 50 else 5
    return left, top, unit, int((right-left) * unit), int((top-floor) * unit)


def project(verts, uv, faces, view, side):
    left, top, scale, w, h = view
    points = np.stack(((verts[:, 2] - left) * scale, (top - verts[:, 1]) * scale), axis=-1)
    depth = np.full((h, w), -np.inf, dtype=np.float32)
    mapped = np.zeros((h, w, 2), dtype=np.float32)
    for tri, xy in zip(faces, points[faces], strict=True):
        x0, y0 = np.maximum(0, np.floor(xy.min(axis=0)).astype(int))
        x1, y1 = np.minimum((w - 1, h - 1), np.ceil(xy.max(axis=0)).astype(int))
        if x0 >= x1 or y0 >= y1:
            continue
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1].astype(np.float32)
        weights = barycentric(xy, xx + .5, yy + .5)
        if weights is None:
            continue
        a, b, c = weights
        x = verts[tri, 0] * side
        z = a * x[0] + b * x[1] + c * x[2]
        dst = depth[y0:y1 + 1, x0:x1 + 1]
        active = (a >= -.00001) & (b >= -.00001) & (c >= -.00001) & (z > dst)
        if np.any(active):
            chart = uv[tri]
            dst[active] = z[active]
            target = mapped[y0:y1 + 1, x0:x1 + 1]
            target[active] = a[active, None] * chart[0] + b[active, None] * chart[1] + c[active, None] * chart[2]
    return depth, mapped


def draw_texture(texture, depth, uv):
    h, w = texture.shape[:2]
    foreground = np.stack([map_coordinates(ch, (uv[..., 1] * (h-1), uv[..., 0] * (w-1)),
                                          order=1) for ch in np.moveaxis(texture, -1, 0)], axis=-1)
    image = np.where(np.isfinite(depth)[..., None], foreground, [.108, .142, .188])
    return Image.fromarray(np.round(np.clip(image, 0, 1) * 255).astype(np.uint8))


def label_grid(im, view):
    left, top, scale, w, h = view
    layer = Image.new("RGBA", im.size)
    grid = ImageDraw.Draw(layer)
    font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 12)
    for z in range(-60, 61, 5):
        p = int((z - left) * scale)
        if 0 <= p < w:
            grid.line((p, 0, p, h), fill=(255, 255, 255, 45))
            grid.text((p + 2, 3), str(z), font=font, fill=(255, 230, 188, 240))
    for y in range(0, 145, 5):
        p = int((top - y) * scale)
        if 0 <= p < h:
            grid.line((0, p, w, p), fill=(255, 255, 255, 45))
            grid.text((3, p + 3), str(y), font=font, fill=(255, 230, 188, 240))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def texture_source(repo, stage, key):
    if key == "A141":
        return repo / BASE / "tex/dragon/A141.png"
    return stage / "true-red" / "tex/crab" / f"trav_natsuko_{key}.png"


def make_guides(repo, stage):
    out = stage / "rivet-guides"
    out.mkdir(parents=True, exist_ok=True)
    for key in ITEMS:
        verts, uv, faces = load_native_mesh(repo / BASE / f"{key}.mdl")
        view = projection(verts)
        texture = tex_array(texture_source(repo, stage, key))
        for side, label in ((1, "front"), (-1, "rear")):
            depth, mapped = project(verts, uv, faces, view, side)
            image = draw_texture(texture, depth, mapped)
            label_grid(image, view).save(out / f"{key}-{label}.png")
            np.savez_compressed(out / f"{key}-{label}.npz", depth=depth, uv=mapped, view=view)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("repository", type=Path)
    cli.add_argument("stage", type=Path)
    opts = cli.parse_args()
    make_guides(opts.repository, opts.stage)

