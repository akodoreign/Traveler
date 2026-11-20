from pathlib import Path
import sys

from PIL import ImageEnhance

from author_rivet_guides import BASE, draw_texture, label_grid, load_native_mesh, project, projection, tex_array

repo, root = map(Path, sys.argv[1:3])
out = root / "edge-guides"
out.mkdir(exist_ok=True)
for key in sys.argv[3:] or ("A173", "A110", "A141", "A108", "A166"):
    verts, uv, faces = load_native_mesh(repo / BASE / f"{key}.mdl")
    view = projection(verts)
    left, top, scale, w, h = view
    view = (left, top, scale * 2, w * 2, h * 2)
    src = tex_array(repo / BASE / "tex" / f"{key}_color_srgb.png")
    for side, label in ((1, "front"), (-1, "rear")):
        depth, texcoord = project(verts, uv, faces, view, side)
        preview = ImageEnhance.Brightness(draw_texture(src, depth, texcoord)).enhance(1.16)
        label_grid(preview, view).save(out / f"{key}-{label}.png")

