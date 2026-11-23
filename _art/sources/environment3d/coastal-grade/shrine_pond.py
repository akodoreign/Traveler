"""Stage the Bayushi Shrine Court's garden colors and existing animated koi."""
import argparse
from copy import deepcopy
import io
import json
from math import floor, hypot, pi
from pathlib import Path
import struct

import numpy as np
from PIL import Image

from coastal_daylight import (
    ASSETS, CATALOG, FRAME, RENDER, apply, digest, js, read, resource_files, smooth, transfer,
)


MAP = "M586"
SKY = Path("project/resource/ibltex/traveler_clear_coast_ibl.ktx")
PRESET = "rt_coastal_brilliance_road_horizon"
ALIAS = "_shrine_court"
WATER_PREFIX = "m586_bayushi_jade_pond"
KOI = "bayushi_pond_koi"
PIGMENTS = {
    "cakon_silt": ((68, 111, 63), .86),
    "castle_bayushi_stone": ((132, 119, 104), .44),
    "castle_bayushi_gravel_daylight_palette": ((174, 123, 98), .58),
    "castle_bayushi_floor_daylight_palette": ((162, 93, 42), .64),
    "castle_bayushi_wood": ((84, 35, 32), .67),
    "castle_bayushi_paper": ((232, 191, 124), .42),
    "castle_bayushi_roof_daylight_palette": ((109, 37, 54), .72),
    "castle_bayushi_accent_daylight_palette": ((183, 32, 41), .46),
}


def native_positions(data):
    assert data[:10] == b"SMDL\x00\x01\x00\x00\x00\x03"
    assert data[14:18] == b"\x00\x01\x00\x03"
    count = struct.unpack_from(">I", data, 24)[0]
    return np.frombuffer(data, dtype=">f4", count=3 * count, offset=28).reshape(-1, 3)


def fit_koi(before, data, generated):
    points = native_positions(data[before["water"] + ".mdl"]).reshape(-1, 4, 3)
    half = .5
    height = float(points[0, 0, 1])
    assert np.allclose(points[:, :, 1], height)
    assert np.allclose(np.ptp(points[:, :, (0, 2)], axis=1), half)
    wet = {tuple(cell) for cell in np.rint(points[:, :, (0, 2)].min(axis=1) / half).astype(int)}
    left = {(x, z) for x in range(29, 34) for z in range(21, 29)}
    right = {(x, z) for x in range(37, 42) for z in range(21, 29)}
    assert wet == left | right
    cells = np.array(Image.open(generated).convert("RGB"))
    assert all(tuple(cells[z, x]) == (8, 0, 2) for x, z in wet)
    assert all(tuple(cells[z, x]) == (35, 3, 3) for x in range(34, 37) for z in range(21, 29))

    koi_points = native_positions(data[KOI + ".mdl"])
    radius = float(np.linalg.norm(koi_points[:, (0, 2)], axis=1).max())
    y = round(height - .012, 3)
    fish = [
        [KOI, 15.75, y, 12.5, 1.24, .69, 1.24, .46, .31],
        [KOI, 15.75, y, 12.5, 1.02, .69, 1.24, .46, round(.31 + pi, 5)],
        [KOI, 19.75, y, 12.5, 1.20, .71, 1.27, .41, 1.55],
        [KOI, 19.75, y, 12.5, 1.00, .71, 1.27, .41, round(1.55 + pi, 5)],
    ]
    bounds = []
    for _, x, _, z, scale, dx, dz, speed, _ in fish:
        r = radius * scale
        lo_x, hi_x, lo_z, hi_z = x - dx - r, x + dx + r, z - dz - r, z + dz + r
        swept_cells = {
            (i, j)
            for i in range(floor(lo_x / half), floor(hi_x / half) + 1)
            for j in range(floor(lo_z / half), floor(hi_z / half) + 1)
        }
        assert swept_cells <= wet, (lo_x, hi_x, lo_z, hi_z)
        bounds.append({"x": [lo_x, hi_x], "z": [lo_z, hi_z], "loopSeconds": 2 * pi / speed})
    return fish, {"wetCells": len(wet), "height": height, "koiRadius": radius, "sweptBounds": bounds}


def pine_palette(raw):
    source = Image.open(io.BytesIO(raw)).convert("RGBA")
    image = np.array(source)
    rgb = image[:, :, :3].astype(float)
    r, g, b = rgb.transpose(2, 0, 1)
    leaf = smooth(2, 16, g - r) * smooth(6, 22, g - b)
    image[:, :, :3] = np.rint(np.clip(rgb + leaf[..., None] * (-5, 26, -5), 0, 255))
    out = io.BytesIO()
    Image.fromarray(image).save(out, format="PNG")
    return out.getvalue()


def prepare(repo, bundle):
    engine = repo / "_tools/rpgcobo-tool"
    root = engine / ASSETS
    story = read(engine / CATALOG)[MAP]
    assert "Two Soshi courtiers by the koi pond" in str(story["event"])
    before = read(root / "index.json")[MAP]
    assert not before.get("pondFish")
    keys = ("bayushi_pond_koi.pm", "bayushi_pond_koi.mdl", "tex/bayushi_pond_koi.png")
    assets = resource_files(root, {MAP: before})
    fish_assets = {key: (root / key).read_bytes() for key in keys}
    assets.update(fish_assets)
    after = deepcopy(before)
    after["pondFish"], fit = fit_koi(before, assets, engine / "tmp/rt_mapgen/M586_cells.png")
    after["renderPreset"] = PRESET
    revised = fish_assets.copy()
    terrain_name = before["terrain"]
    pine_name = "castle_diorama_matsu"
    for name in (terrain_name, pine_name):
        desc = assets[name + ".pm"].decode("utf8")

        def pigment(match):
            filename = match[2]
            stem = Path(filename).stem
            if stem not in PIGMENTS and stem != pine_name:
                return match[0]
            raw = assets["tex/" + filename]
            new_name = stem + ALIAS + ".png"
            revised["tex/" + new_name] = (
                pine_palette(raw) if stem == pine_name else transfer(raw, stem, pigment=PIGMENTS[stem])
            )
            return match[1] + "tex/" + new_name + match[3]

        tinted = FRAME.sub(pigment, desc)
        assert tinted != desc
        revised[name + ALIAS + ".pm"] = tinted.encode("utf8")
    after["terrain"] = terrain_name + ALIAS
    for prop in after["placements"]:
        if prop[0] == pine_name:
            prop[0] += ALIAS

    seq = before["waterSequence"]
    prefix = seq["prefix"]
    assert seq["frames"] == 32 and seq["seconds"] == 17.8
    original = [assets[f"tex/{prefix}{i:02}.png"] for i in range(seq["frames"])]
    levels = []
    for raw in original:
        rgb = np.asarray(Image.open(io.BytesIO(raw)).convert("RGB"))
        levels.append(np.quantile(rgb @ (.213, .715, .072), [.07, .93]))
    contrast = tuple(np.mean(levels, axis=0))
    for i, raw in enumerate(original):
        revised[f"tex/{WATER_PREFIX}{i:02}.png"] = transfer(
            raw, prefix, water=((15, 68, 83), (54, 156, 137), .67), water_limits=contrast,
        )
    old_water = before["water"]
    water_descriptor = assets[old_water + ".pm"]
    assert water_descriptor.count((prefix + "00.png").encode()) == 1
    revised[old_water + ALIAS + ".pm"] = water_descriptor.replace(
        (prefix + "00.png").encode(), (WATER_PREFIX + "00.png").encode(),
    )
    after["water"] = old_water + ALIAS
    after["waterSequence"]["prefix"] = WATER_PREFIX

    sunlight = next(p for p in read(engine / RENDER)["rendersets"] if p["id"] == PRESET)
    sky = (engine / SKY).read_bytes()
    sky_proof = {SKY.as_posix(): digest(sky)}
    proof = {
        "maps": {
            MAP: {
                "before": before,
                "after": after,
                "story": digest(js(story)),
                "world": digest((engine / "project/data/mapdata/M586.bw").read_bytes()),
            },
        },
        "basePresets": {PRESET: sunlight},
        "presets": [sunlight],
        "source": {key: digest(data) for key, data in assets.items()},
        "files": {key: digest(data) for key, data in revised.items()},
        "projectSource": sky_proof,
        "projectFiles": sky_proof,
        "koiFit": fit,
    }
    for key, content in {**revised, SKY.as_posix(): sky}.items():
        target = bundle / "files" / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    (bundle / "coastal-proof.json").write_bytes(json.dumps(proof, indent=2).encode() + b"\n")
    print(f"Prepared {MAP}, {len(revised)} files, and {len(after['pondFish'])} koi in {fit['wetCells']} wet cells.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "stage", "publish"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    repo, bundle = args.repo.resolve(), args.bundle.resolve()
    if args.action == "prepare":
        prepare(repo, bundle)
    elif args.profile is None:
        parser.error("--profile is required to stage or publish.")
    else:
        apply(repo, args.profile.resolve(), bundle, args.action == "publish")


if __name__ == "__main__":
    main()
