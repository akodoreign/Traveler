"""Prepare tileable materials and native placement data for the Coast Road kit."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
STAGE = HERE / "native_environment"
MATERIALS = STAGE / "tex"
CONCEPTS = HERE / "concepts"


def periodic(image, size=512):
    source = np.array(image.resize((size, size), Image.Resampling.LANCZOS), dtype=float)
    x = np.linspace(0, np.pi, size)
    bank = (1 - np.cos(x)) / 2
    for axis in (0, 1):
        source = source.swapaxes(0, axis)
        jump = source[-1] - source[0]
        source -= (bank[:, None, None] - .5) * jump
        source = source.swapaxes(0, axis)
    return np.clip(source, 0, 255)


def colorize(key, bounds, color, variation):
    scan = HERE / "surface_sources" / f"{key}_scan.png"
    if scan.is_file():
        image = Image.open(scan).convert("RGB")
        image = image.crop((12, 12, image.width - 12, image.height - 12))
        data = periodic(image, size=1024)
    else:
        image = Image.open(CONCEPTS / f"{key}_grain.png").convert("RGB").crop(bounds)
        data = periodic(image)
    luminosity = data @ [0.24, .65, .11]
    low, high = np.percentile(luminosity, [4, 96])
    detail = np.clip((luminosity - (low + high) / 2) / max(high - low, 1), -.51, .51)
    if key != "water":
        gray = Image.fromarray(np.uint8(np.clip(luminosity, 0, 255)))
        macro = np.array(gray.filter(ImageFilter.GaussianBlur(11.)), dtype=float)
        micro = (luminosity - macro) / max(np.std(luminosity - macro), 1.)
        micro = np.clip(micro, -2.4, 2.4)
        roughness = {"sand": .17, "cliff": .36, "meadow": .28}[key]
        detail = roughness * detail + (.23 if scan.is_file() else .18) * micro
    result = np.asarray(color) * (1 + variation * detail[..., None])
    chroma = data - luminosity[..., None]
    return np.clip(result + .105 * chroma, 0, 255).astype(np.uint8)


def textures():
    MATERIALS.mkdir(exist_ok=True, parents=True)
    for name, source, crop, tint, variation in (
        ("sand", "sand", (23, 270, 251, 555), (183, 153, 111), .19),
        ("path", "sand", (23, 265, 251, 590), (149, 122, 85), .32),
        ("meadow", "meadow", (495, 6, 754, 183), (102, 123, 69), .45),
        ("cliff", "cliff", (8, 22, 179, 527), (109, 105, 93), .54),
    ):
        Image.fromarray(colorize(source, crop, tint, variation)).save(MATERIALS / f"{name}.png")
    # Preserve the generated water's irregular caustic detail. Scroll and
    # refract it over a closed cycle for both open water and small tide pools.
    water = colorize("water", (25, 180, 755, 451), (55, 127, 130), .64)
    height, width = water.shape[:2]
    y, x = np.indices((height, width))
    for style, frames, amplitude in (("calm",32,8.),("storm",16,18.)):
        for i in range(frames):
            phase = i * 2 * np.pi / frames
            dx = np.rint(amplitude*.45 * np.sin(y * np.pi / 82 + phase))
            dy = np.rint(amplitude * np.sin(phase + x*np.pi/132) + amplitude*.21*np.sin(phase*2-y*np.pi/75))
            if style == "storm":
                dy += i * height // frames
            u = (x + dx.astype(int)) % width
            v = (y + dy.astype(int)) % height
            shifted = Image.fromarray(water[v, u]).filter(ImageFilter.GaussianBlur(.45))
            stem = "surf" if style=="calm" else "storm"
            shifted.save(MATERIALS / f"{stem}{i:02}.png")


def collect(gm, mid):
    m, events = gm.make(mid)
    terrain = {"top": [], "cliff": []}
    tiles = m.blk
    height = m.hgt
    depth, width = tiles.shape
    shelf = 12 if mid == "M811" else 8
    rng = np.random.default_rng(1851 if mid == "M811" else 1571)
    heights = (height.astype(float) + 1) * .5
    road = tiles == gm.ROAD
    wet = tiles == gm.WATER
    grass = tiles == gm.GRASS
    active = (tiles & 31) == 2
    exposed = grass | wet | active
    tags = np.full(tiles.shape, "cliff", "U6")
    tags[(tiles == gm.SAND) | (tiles == gm.SAND2)] = "sand"
    tags[grass] = "meadow"
    tags[tiles == gm.T(2,0)] = "meadow"
    tags[road] = "path"
    tags[wet] = "water"
    tags[~exposed] = ""
    # Build merged stripe faces with continuous UVs across every painted tile.
    for row in range(depth):
        start = 0
        while start < width:
            end = start + 1
            tag, yy = str(tags[row, start]), float(heights[row, start])
            while end < width and tags[row, end] == tag and heights[row, end] == yy:
                end += 1
            if tag:
                terrain["top"].append([tag, start * .5, row * .5, end * .5, (row + 1) * .5, yy])
            start = end
    for row in range(depth):
        for col in range(width):
            for dx, dz in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                px, pz = col + dx, row + dz
                if not (0 <= px < width and 0 <= pz < depth):
                    continue
                high, low = float(heights[row, col]), float(heights[pz, px])
                if exposed[row, col] and high > low:
                    terrain["cliff"].append([col * .5, row * .5, low, high, dx, dz])
    terrain["water_cells"] = int(wet.sum())
    field = mid != "M811"
    vegetation, props = [], []
    old_rows = getattr(m, "environment_replaced", [])
    danger = [(obj["x"], obj["z"]) for obj in m.objs + old_rows if obj["t"] == "fb"]
    if events:
        danger += [row["pos"][:3:2] for row in events.ev.values()
                   if isinstance(row.get("pos"), (list, tuple)) and len(row["pos"]) >= 3]
    for row, col in zip(*np.nonzero(grass), strict=True):
        if not (shelf <= col < width - shelf and shelf <= row < depth - shelf):
            continue
        if rng.random() > (.22 if field else .11):
            continue
        if any(abs(col - x) < 2 and abs(row - z) < 2 for x, z in danger):
            continue
        # Repeated seed changes appearance by region without moving plants
        # into playable tiles or covering a trigger.
        key = "coast_flowers" if rng.random() < .29 else "wind_grass"
        vegetation.append([key, (col + rng.uniform(.18, .82)) * .5, float(heights[row, col]),
                           (row + rng.uniform(.18, .82)) * .5, float(rng.uniform(.72, 1.22)),
                           float(rng.uniform(0, np.pi * 2))])
    if mid == "M103":
        candidates = []
    elif field:
        candidates = [(45, 24), (79, 25), (102, 29), (146, 26), (157, 27), (56, 19), (101, 17), (138, 18)]
        # Coast Road is padded 26 blocks to the west and 4 to the south.
        # Roadside rest points sit on grass just north of the carriage lane.
        for x in (50, 81, 119, 150):
            row = 25
            if grass[row, x] and not any(abs(x - dx) < 4 and abs(row - dz) < 3 for dx, dz in danger):
                for key, offset in (("cedar_bench", 0), ("salt_crate", 1)):
                    props.append([key, (x + offset * 2) * .5, float(heights[row, x]), row * .5 + .22, 1., .17])
    else:
        candidates = [(27, 52), (48, 52), (80, 50), (99, 60), (92, 78), (40, 84), (58, 81), (112, 82)]
        for x, row in ((34, 82), (92, 84)):
            props.append(["cedar_bench", x * .5, float(heights[row, x]), row * .5, 1., .23])
            props.append(["salt_crate", x * .5 + 1.05, float(heights[row, x]), row * .5 + .2, 1.1, -.31])
    for x, row in candidates:
        if mid == "M811" and 42 < x < 87 and 47 < row < 75:
            continue
        if not wet[row, x]:
            props.append(["shore_boulder", x * .5, float(heights[row, x]), row * .5, .92, 0.56])
    terrain["placements"] = props + vegetation
    terrain["shape"] = [width, depth]
    return terrain


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo / "tools"))
    import gen_maps as gm
    textures()
    all_data = {mid: collect(gm, mid) for mid in ("M102", "M103", "M105", "M811")}
    (HERE / "coast-map-data.json").write_text(json.dumps(all_data), encoding="utf-8")
    scenes = {
        mid: {"terrain": mid.lower() + "_surfaces", "water": mid.lower() + "_water",
              "placements": data["placements"]} for mid, data in all_data.items()
    }
    (STAGE / "index.json").write_text(json.dumps(scenes, separators=(",", ":")), encoding="utf-8")
    print({mid: (len(data["placements"]), len(data["top"]), len(data["cliff"]))
           for mid, data in all_data.items()})


if __name__ == "__main__":
    main()
