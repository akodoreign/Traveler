"""Fit an independent Noh mask to the regenerated Shiko head and dye the silk armor."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, maximum_filter
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals

STAGE = Path(__file__).resolve().parent
WORK = STAGE.parents[1]
sys.path[:0] = [str(WORK / "gendo-geometry"), str(WORK / "batch20-masks")]
from build_porcelain import component, extrude, facial_surface, front_panels
from render_fit import draw, load_native_mesh, native_layout


MASK = "ep427_renegade_noh"
HEAD = "side_shiko_portrait_face"
PALETTE = "A120_renegade_crimson"
BODY_TONE = (244, 199, 178)


def silhouette(across, down):
    edge = np.abs(across)
    lateral = across * (3.71 + .58 * np.sin(np.pi * down) - 2.58 * down**3.05)
    brow = 111.40 - 1.17 * edge**2.7
    chin = 102.83 + 1.31 * edge**1.7
    return lateral, brow + down * (chin - brow)


def eye_openings(lateral, height):
    horizontal = np.abs(lateral) - 2.205
    vertical = height - 108.07 - .105 * horizontal
    return np.hypot(horizontal / 1.44, vertical / .765)


def mask_fit(head, faces):
    columns, rows = 111, 93
    across, down = np.meshgrid(np.linspace(-1, 1, columns), np.linspace(0, 1, rows))
    lateral, height = silhouette(across, down)
    eye = eye_openings(lateral, height)
    points = np.column_stack((lateral.ravel(), height.ravel()))
    triangles = head[faces][:, :, [0, 2, 1]]
    area = (triangles[:, :, 0].max(1) > 0) & (triangles[:, :, 2].max(1) > 102.7)
    area &= triangles[:, :, 2].min(1) < 111.45
    exact = facial_surface(points, triangles[area]).reshape(height.shape)
    assert np.isfinite(exact).all(), "The mask outline ran beyond the fitted head"
    # Seat the porcelain against the complete fitted head, including the bangs.
    outward = maximum_filter(exact, size=(5, 5), mode="nearest")
    bowl = gaussian_filter(outward, sigma=(2.2, 3.0), mode="nearest")
    inner = np.maximum(outward + .135, bowl + .165)
    edge = np.minimum.reduce((1 - np.abs(across), down, 1 - down))
    cheek = .08 * np.cos(np.pi * across) * np.sin(np.pi * down)
    lip = .07 * np.exp(-((edge - .035) / .026)**2)
    outer = inner + .218 + cheek + lip
    uv = np.column_stack((.055 + .89 * (across.ravel() + 1) / 2, .055 + .89 * (1 - down.ravel())))
    shell, atlas_uv = extrude(
        front_panels(rows, columns, eye),
        np.column_stack((outer.ravel(), height.ravel(), lateral.ravel())),
        np.column_stack((inner.ravel(), height.ravel(), lateral.ravel())),
        uv,
    )
    seat = face_clearance(shell.vertices, triangles[area])
    assert seat.min() > .12, f"Minimum head clearance {seat.min():.3f}"
    return shell, atlas_uv, seat


def face_clearance(vertices, head_triangles):
    front = facial_surface(vertices[:, [2, 1]], head_triangles)
    assert np.isfinite(front).all()
    return vertices[:, 0] - front


def glaze():
    row, col = np.indices((512, 512), dtype=np.float32)
    across = np.clip((col / 511 - .055) / .89, 0, 1) * 2 - 1
    down = np.clip((row / 511 - .055) / .89, 0, 1)
    lateral, height = silhouette(across, down)
    aperture = eye_openings(lateral, height)
    edge = np.minimum.reduce((1 - np.abs(across), down, 1 - down))
    reflect = .85 * np.exp(-((across + .28 + .24 * down) / .47)**2)
    micro = gaussian_filter(np.random.default_rng(427).normal(size=down.shape), 2.65)
    grain = micro * (1.15 / micro.std())
    tone = np.broadcast_to(np.array([231., 221., 201.]), (*down.shape, 3)).copy()
    tone += reflect[:, :, None] * [15, 16, 18] + grain[:, :, None]
    tone -= (np.exp(-((edge - .023) / .021)**2) + .37 * (down**3))[:, :, None] * [25, 25, 24]

    def paint(color, amount):
        tone[:] = tone * (1 - amount[:, :, None]) + np.asarray(color) * amount[:, :, None]

    # The dark upper brows and small painted lips are cues from the original sprite.
    brow_side = (np.abs(lateral) - 2.04) / 1.18
    brow_y = 109.53 + .34 * (1 - brow_side**2) + .025 * brow_side
    brow = np.exp(-((height - brow_y) / .140)**2) * np.clip(3.5 * (1 - brow_side**2), 0, 1)
    paint((52, 26, 29), .91 * brow)
    eye_rim = np.exp(-((aperture - 1.057) / .058)**2)
    paint((123, 62, 57), .60 * eye_rim)
    lip = np.exp(-((lateral / .78)**4 + ((height - 104.43) / .186)**2))
    lip_line = np.exp(-((lateral / .70)**4 + ((height - 104.49) / .071)**2))
    paint((135, 32, 46), .93 * lip)
    paint((79, 16, 30), .80 * lip_line)
    return Image.fromarray(np.uint8(np.clip(tone, 0, 255)))


def scorpion_silk(source):
    """Retain the original folds and trim while restoring woven crimson diamonds."""
    rgba = np.array(Image.open(source).convert("RGBA"))
    color = rgba[:, :, :3].astype(np.float32)
    red, green, blue = color.transpose(2, 0, 1)
    cloth = np.clip((red - 18) / 62, 0, 1) * np.clip((blue - green + 6) / 15, 0, 1)
    row, col = np.indices(cloth.shape, dtype=np.float32)
    weft = .5 + .5 * np.sin(row * np.pi / 1.90) * np.cos(col * np.pi / 2.1)
    lattice = np.abs(((col + row * .625) / 31.0 + .5) % 1 - .5)
    cross = np.abs(((col - row * .625) / 31.0 + .5) % 1 - .5)
    line = np.exp(-(np.minimum(lattice, cross) / .043)**2)
    accent = cloth * (.32 + .105 * weft - .52 * line)
    new = color + accent[:, :, None] * np.array([24, 10, 19])
    rgba[:, :, :3] = np.uint8(np.clip(new, 0, 255))
    return Image.fromarray(rgba)


def atlas(path):
    return np.asarray(Image.open(path).convert("RGB"))


def preview(head, helmet, dressed, base, colors, output):
    width, height, scale = 244, 330, 7.6
    front_height = 122.5
    panel = Image.new("RGB", (4 * width, 2 * (height + 24)), "#181f2b")
    labels = ImageDraw.Draw(panel)
    bp, buv, bf = base
    for row, mask_on in enumerate((False, True)):
        for index, yaw in enumerate((0, 42, 90, -90)):
            angle = np.deg2rad(yaw)
            forward = np.array([np.cos(angle), 0, np.sin(angle)])
            lateral = np.array([-np.sin(angle), 0, np.cos(angle)])
            parts = [((bp, buv, bf), np.array([[BODY_TONE]], np.uint8)), (dressed, colors[1]), (head, colors[0])]
            if mask_on:
                parts.append((helmet, colors[2]))
            depth = np.full((height, width), -np.inf, np.float32)
            canvas = np.full((height, width, 3), (33, 40, 52), np.uint8)
            owners = np.zeros((height, width), np.uint8)
            for index_part, ((p, uv, faces), skin) in enumerate(parts, 1):
                projection = np.column_stack(((p @ lateral) * scale + width / 2,
                                              (front_height - p[:, 1]) * scale, p @ forward))
                draw(projection, uv, faces, skin, depth, canvas, owners, index_part)
            if mask_on and yaw == 0:
                visible = np.count_nonzero(owners == 4)
                assert visible > 1750, f"Only {visible} visible facial mask pixels"
                for eye in [-2.205, 2.205]:
                    x = round(width / 2 + eye * scale)
                    y = round((front_height - 108.07) * scale)
                    assert np.count_nonzero(owners[y-2:y+3, x-2:x+3] == 3) > 18, "The eye opening is obscured"
            x, y = width * index, row * (height + 24)
            labels.text((x + 9, y + 5), f"Mask {'fitted' if mask_on else 'removed'}   {'Front' if not yaw else str(yaw) + '°'}",
                        fill="white")
            panel.paste(Image.fromarray(canvas), (x, y + 24))
    panel.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Tool directory containing project/")
    args = parser.parse_args()
    source = args.target / "project/resource"
    human, tailor = source / "native_human", source / "native_tailoring"
    target = STAGE / "assets"
    mask_path = target / "native_human"
    mask_path.joinpath("tex").mkdir(parents=True, exist_ok=True)
    dye_path = target / "native_tailoring/tex/scorpion"
    dye_path.mkdir(parents=True, exist_ok=True)

    head_path = human / (HEAD + ".mdl")
    head = load_native_mesh(head_path)
    sculpt, uv, clearance = mask_fit(head[0], head[2])
    mask_image = glaze()
    texture_name = MASK + "_color_srgb.png"
    mask_image.save(mask_path / "tex" / texture_name)
    component.NAME = component.native.NAME = MASK
    component.native.PALETTE = {"noh_porcelain": ((255, 255, 255), .38, .015)}
    component.native.export_native({"noh_porcelain": sculpt}, source / "native_ornament/side_hagi_sash.mdl", mask_path)
    component.weave_uv = lambda verts: np.column_stack((uv[:, 0], 1 - uv[:, 1]))
    component.attach_texture(mask_path, {"noh_porcelain": sculpt}, texture_name)
    sculpt.visual = TextureVisuals(uv=uv, material=PBRMaterial(name="Noh porcelain", baseColorTexture=mask_image,
                                    roughnessFactor=.38, metallicFactor=.015))
    sculpt.apply_transform(component.REFLECTION)
    sculpt.export(STAGE / (MASK + ".glb"))
    (mask_path / (MASK + ".glb")).unlink()

    dye = scorpion_silk(tailor / "tex/scorpion/A120.png")
    dye.save(dye_path / (PALETTE + ".png"))
    body = load_native_mesh(human / "shared_female.mdl")
    _, body_groups = native_layout((human / "shared_female.mdl").read_bytes())
    body = (*body[:2], np.concatenate(body_groups[1:]))
    preview(head, load_native_mesh(mask_path / (MASK + ".mdl")), load_native_mesh(tailor / "A120.mdl"), body,
            [atlas(human / "tex" / (HEAD + "_srgb.png")), np.asarray(dye.convert("RGB")), np.asarray(mask_image)],
            STAGE / "renegade-bind-review.png")
    report = {
        "head": HEAD, "head_sha256": hashlib.sha256(head_path.read_bytes()).hexdigest(),
        "mask_vertices": len(sculpt.vertices), "mask_triangles": len(sculpt.faces),
        "minimum_clearance": float(clearance.min()), "median_clearance": float(np.median(clearance)),
        "eye_centers_native_y_z": [[108.07, -2.205], [108.07, 2.205]],
        "asset_recipe": "Noh shell fitted to the regenerated Shiko surface, using the project's porcelain shell exporter"
    }
    (STAGE / "fit-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
