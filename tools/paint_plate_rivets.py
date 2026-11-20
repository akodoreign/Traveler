"""Paint fitted hard-plate fasteners on the original UV islands."""
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from author_rivet_guides import BASE, ITEMS, barycentric, draw_texture, load_native_mesh, projection, project, tex_array


def pairs(level, span, radius):
    return [(-span, level, radius), (span, level, radius)]


# Coordinates are (lateral Z, Y height, physical radius). Each pair was placed
# over a visible rigid plate in the native textured front or back authoring views.
ANCHORS = {
    "A173": {
        1: (pairs(92.1, 12.4, .69) + pairs(88.0, 13.4, .69) +
            pairs(79.0, 3.9, .71) + pairs(75.1, 3.9, .71)),
        -1: pairs(90.0, 12.4, .69) + pairs(86.1, 13.3, .69),
    },
    "A110": {
        1: (pairs(125.1, 6.2, .57) + pairs(122.7, 8.5, .57) +
            pairs(110.1, 11.1, .60) + pairs(107.8, 12.5, .60)),
        -1: (pairs(125.1, 5.8, .57) + pairs(122.7, 8.4, .57) +
             pairs(110.2, 10.0, .60) + pairs(107.8, 11.2, .60)),
    },
    "A141": {
        1: (pairs(93.0, 11.4, .68) + pairs(87.9, 12.5, .68) +
            pairs(82.1, 4.9, .70) + pairs(75.0, 4.8, .70) +
            pairs(55.1, 9.4, .71) + pairs(48.6, 10.1, .71)),
        -1: (pairs(92.0, 11.4, .68) + pairs(86.3, 12.8, .68) +
             pairs(57.3, 4.6, .71) + pairs(50.9, 4.9, .71)),
    },
}


def ease(a, b, v):
    x = np.clip((v-a)/(b-a), 0, 1)
    return x*x*(3-2*x)


def bake_mask(verts, uv, faces, view, sides, width, height):
    left, top, scale, pw, ph = view
    # The overlays are authored in bind-space, so screen-sided hard plate polygons
    # must be visible through their original depth and their own UV triangle.
    projected = verts[faces][:, :, (2, 1)]
    mins, maxs = projected.min(axis=1), projected.max(axis=1)
    face_uv = uv[faces] * (width - 1, height - 1)
    contact = np.zeros((height, width), dtype=np.float32)
    cap = np.zeros_like(contact)
    light = np.zeros_like(contact)
    for side, depth, points in sides:
        for z, y, radius in points:
            outer = radius * 1.23
            selected = np.flatnonzero(np.all((mins <= (z+outer, y+outer)) &
                                            (maxs >= (z-outer, y-outer)), axis=1))
            for ti in selected:
                uv_tri = face_uv[ti]
                x0, y0 = np.maximum(0, np.floor(uv_tri.min(axis=0)).astype(int))
                x1, y1 = np.minimum((width-1, height-1), np.ceil(uv_tri.max(axis=0)).astype(int))
                yy, xx = np.mgrid[y0:y1+1, x0:x1+1].astype(np.float32)
                weights = barycentric(uv_tri, xx, yy)
                if weights is None:
                    continue
                a, b, c = weights
                inside = (a >= -.04) & (b >= -.04) & (c >= -.04)
                if not np.any(inside):
                    continue
                va, vb, vc = verts[faces[ti]]
                position = va[None, None, :]*a[..., None] + vb[None, None, :]*b[..., None] + vc[None, None, :]*c[..., None]
                u, v = (position[..., 2]-z) / radius, (y-position[..., 1]) / radius
                distance = np.sqrt(u*u + v*v)
                sx = np.clip(((position[..., 2]-left)*scale).astype(int), 0, pw-1)
                sy = np.clip(((top-position[..., 1])*scale).astype(int), 0, ph-1)
                visible = (position[..., 0]*side >= depth[sy, sx] - .37) & np.isfinite(depth[sy, sx])
                keep = inside & visible & (distance <= 1.23)
                rim = (1-ease(1.0, 1.23, distance)) * keep
                metal = (1-ease(.79, .99, distance)) * keep
                shade = np.clip(.52 - .29*u - .38*v, .16, .96)
                glint = .41*np.exp(-7.6*((u+.35)**2+(v+.44)**2))
                tile = (slice(y0, y1+1), slice(x0, x1+1))
                contact[tile] = np.maximum(contact[tile], rim)
                update = metal > cap[tile]
                cap[tile][update] = metal[update]
                light[tile][update] = (shade + glint)[update]
    return contact, cap, light


def paint(texture, masks, amber):
    contact, metal, light = [pixels[..., None] for pixels in masks]
    shadow = texture * (1 - .42*contact)
    dark, bright = ((28, 21, 13), (170, 134, 76)) if amber else ((16, 27, 45), (137, 150, 162))
    dark, bright = np.asarray(dark)/255., np.asarray(bright)/255.
    dome = dark + light*(bright-dark)
    return shadow*(1-metal) + dome*metal


def save_rgb(path, pixels):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.round(np.clip(pixels, 0, 1) * 255).astype(np.uint8)).save(path)


def render_comparison(rows, destination):
    panel_width, panel_height = 315, 295
    result = Image.new("RGB", (panel_width*3, panel_height*2+64), "#18202b")
    draw = ImageDraw.Draw(result)
    big = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 25)
    label = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)
    draw.text((15, 10), "Hard-plate rivets · fitted texture authoring", font=big, fill="#e8edf5")
    draw.text((15, 43), "Front bind-space views before and after", font=label, fill="#aebdce")
    for i, (title, before, after) in enumerate(rows):
        for j, (caption, view) in enumerate((("Original fasteners", before), ("Refined fasteners", after))):
            x, y = i*panel_width, j*panel_height+64
            view.thumbnail((panel_width-22, panel_height-30), Image.Resampling.LANCZOS)
            result.paste(view, (x+(panel_width-view.width)//2, y+24))
            draw.text((x+14, y+4), f"{title} · {caption}", font=label, fill="#e8edf5")
    result.save(destination)


def make(repo, work, out, preview):
    original = repo / BASE
    rows = []
    for key in ITEMS:
        verts, uv, faces = load_native_mesh(original / f"{key}.mdl")
        view = projection(verts)
        front, front_uv = project(verts, uv, faces, view, 1)
        rear, _ = project(verts, uv, faces, view, -1)
        if key == "A141":
            textures = sorted((original / "tex").glob(f"*/{key}.png"))
            textures.append(original / "tex" / f"{key}_color_srgb.png")
            sample = original / "tex" / "dragon" / f"{key}.png"
        else:
            sample = work / "true-red" / "tex/crab" / f"trav_natsuko_{key}.png"
            textures = [sample]
        h, w = tex_array(sample).shape[:2]
        masks = bake_mask(verts, uv, faces, view, ((1, front, ANCHORS[key][1]), (-1, rear, ANCHORS[key][-1])), w, h)
        save_rgb(out / "masks" / f"{key}-hard-plate-mask.png",
                 np.stack((masks[0], masks[1], masks[2]), axis=-1))
        for src in textures:
            relative = src.relative_to(original) if key == "A141" else Path("tex/crab") / src.name
            before = tex_array(src)
            after = paint(before, masks, amber=key == "A141")
            save_rgb(out / relative, after)
            if src == sample:
                rows.append((key, draw_texture(before, front, front_uv), draw_texture(after, front, front_uv)))
    render_comparison(rows, preview)


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("repository", type=Path)
    cli.add_argument("working", type=Path)
    cli.add_argument("out", type=Path)
    cli.add_argument("preview", type=Path)
    opts = cli.parse_args()
    make(opts.repository, opts.working, opts.out, opts.preview)

