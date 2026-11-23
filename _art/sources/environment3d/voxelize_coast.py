"""Turn the accepted generated Coast Road props into colored voxel grid modules."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
import trimesh

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / "native_environment"
OUT = HERE / "voxel_sources"
MODELS = Path("C:/AI/comfy-3d/app/output/nonhumans")
OUT.mkdir(exist_ok=True)


def mesh_source(key):
    candidates = sorted(MODELS.glob(f"traveler_env_coast_{key}_*.glb"))
    if not candidates:
        raise FileNotFoundError(key)
    source = candidates[0]
    meshes = trimesh.load_scene(source, process=False).dump()
    if len(meshes) != 1:
        raise ValueError(f"Expected one isolated prop in {source}")
    return source, meshes[0]


def plank_bench():
    key, points, colors, _, source = convert_prop("cedar_bench", (1.42,.48,.45), 31, lower=.70)
    valid = (colors.max(1) > 48) & (colors[:,0] >= colors[:,2]+10)
    palette = colors[valid]
    if not len(palette):
        raise ValueError("Generated cedar bench has no usable wood color")
    rng = np.random.default_rng(57)
    voxels, tint = [], []
    for x in range(39):
        for z in range(13):
            for h in range(13):
                seat = h>=10 and (z not in (4,8) or h<12)
                leg = x in (4,5,6,32,33,34) and 1<z<11 and h<10
                brace = (x in (4,5,6,32,33,34) and z not in (0,12) and h in (8,9))
                if seat or leg or brace:
                    rgb = np.median(palette, axis=0).astype(float)
                    patch = .18 * np.sin(z*2.4 + h*.72) + .045*np.cos(x*.34 + z*.16)
                    rgb *= (1+patch + rng.normal(0,.025)) * (.80 if leg else 1.)
                    voxels.append((x,z,h))
                    tint.append(np.rint(rgb))
    return key, np.array(voxels), np.array(tint), np.asarray([1.42/39,.43/13,.46/13]), source


def convert_prop(key, world, samples, lower=0., upper=1.):
    source, mesh = mesh_source(key)
    original = mesh.vertices.copy()
    height = (original[:, 1] - original[:, 1].min()) / np.ptp(original[:, 1])
    rgb = mesh.visual.to_color().vertex_colors[:, :3]
    tree = cKDTree(original)
    voxels = mesh.voxelized(float(np.max(mesh.extents) / samples))
    centers = voxels.points
    y = (centers[:, 1] - original[:, 1].min()) / np.ptp(original[:, 1])
    keep = (y >= lower) & (y <= upper)
    indices = voxels.sparse_indices[keep][:, [0, 2, 1]]
    centers = centers[keep]
    colors = rgb[tree.query(centers)[1]]
    coordinates = indices - indices.min(0)
    dims = coordinates.max(0) + 1
    return key, coordinates, colors, np.asarray(world) / dims, str(source)


def palette_from(image, hue):
    path = HERE / "concepts" / f"{image}.png"
    hsv = np.asarray(Image.open(path).convert("HSV"))
    rgb = np.asarray(Image.open(path).convert("RGB"))
    use = ((hsv[..., 0] >= hue[0]) & (hsv[..., 0] <= hue[1]) &
           (hsv[..., 1] > 90) & (hsv[..., 2] > 60))
    if use.sum() < 25:
        raise ValueError(f"Insufficient palette pixels for {image}")
    return np.percentile(rgb[use], [20, 59, 87], axis=0).astype(int)


def plants(key, rng):
    flower = key == "coast_flowers"
    greens = palette_from(key, (44, 100))
    colors = {}
    for stem in range(6 if flower else 12):
        x, y = rng.integers(6, 15, 2)
        h = int(rng.integers(8, 18) if flower else rng.integers(7, 25))
        dx, dy = rng.integers(-7, 8, 2)
        end = (0, 0, 0)
        for z in range(h):
            t = (z / h) ** 1.55
            px, py = round(x + dx * t), round(y + dy * t)
            end = (px, py, z)
            colors[end] = greens[0 if z < 3 else 1 if z < h - 4 else 2]
            if not flower and z < h - 2:
                colors[px+1, py, z] = greens[1]
            if flower and 3 < z < h - 3 and z % 3 == 0:
                for off in (1, 2):
                    colors[px + (off if stem % 2 else -off), py, z + off // 2] = greens[1]
        if flower:
            px, py, pz = end
            petal = [(229, 166, 158), (241, 195, 180), (233, 206, 153)][stem % 3]
            for a, b in ((1,0),(-1,0),(0,1),(0,-1),(1,1)):
                colors[px+a, py+b, pz+1] = petal
                colors[px+a*2, py+b, pz+1] = petal
            colors[px, py, pz+1] = [211, 159, 61]
    vox = np.array(list(colors), dtype=int)
    vox -= vox.min(0)
    size = (.44,.41,.36) if flower else (.46,.40,.57)
    return key, vox, np.array(list(colors.values())), np.asarray(size)/(vox.max(0)+1), str(HERE / "concepts" / f"{key}.png")


def save(key, points, rgb, pitch, source, voxfile):
    assert points.min() >= 0 and points.max() < 255
    assert len(np.unique(points, axis=0)) == len(points)
    # Map the baked generated texture to an indexed voxel palette for the
    # source asset. The native mesh uses the same quantized RGB values.
    img = Image.fromarray(np.uint8(rgb)[None, ...]).quantize(colors=64)
    pal = np.asarray(img.getpalette()[:192], dtype=np.uint8).reshape(-1, 3)
    index = np.asarray(img).ravel() + 1
    dims = tuple(map(int, points.max(0) + 1))
    vf = voxfile.VoxFile()
    arr = np.zeros(dims, dtype=np.uint8)
    arr[tuple(points.T)] = index
    vf.models = [voxfile.Model(dims, arr)]
    vf.chunks = [("SIZE", 0), ("XYZI", 0), ("RGBA", bytes(4))]
    vf.palette[1:1+len(pal), :3] = pal
    vf.palette[1:1+len(pal), 3] = 255
    vf.save(OUT / f"{key}.vox")
    np.savez_compressed(OUT / f"{key}.npz", points=points, colors=pal[index - 1], pitch=pitch)
    return {"name": key, "source": source, "grid": list(dims), "occupied": len(points),
            "world_size": (np.asarray(dims) * pitch).tolist()}


def main():
    repo = Path(sys.argv[1])
    sys.path.insert(0, str(repo / "tools"))
    import voxfile
    rng = np.random.default_rng(1805)
    spec = [
        plank_bench(),
        convert_prop("salt_crate", (.49,.45,.40), 24, upper=.55),
        convert_prop("shore_boulder", (.96,.79,.51), 26),
        plants("wind_grass", rng), plants("coast_flowers", rng),
    ]
    (OUT / "manifest.json").write_text(json.dumps([save(*item, voxfile) for item in spec], indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
