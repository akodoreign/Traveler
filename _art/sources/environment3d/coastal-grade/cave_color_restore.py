"""Restore the earlier coastal cave pigments while keeping pools distinct."""
import argparse
from copy import deepcopy
import io
from pathlib import Path

import numpy as np
from PIL import Image

from coastal_daylight import ASSETS, CATALOG, LUMA, RENDER, apply, digest, js, read, resource_files, smooth, transfer


GROUPS = {"doji": ("M486",), "yasuki": ("M480", "M481", "M829")}
DOJI_ATLAS = "doji_tidal_footpath_atlas"
DOJI_INSTALLED = DOJI_ATLAS + "_coastal_daylight_dry_floor"
RESTORE = "_cave_color_restore"
YASUKI_WATER = "yasuki_tidal_pool"
YASUKI_RESTORED = "yasuki_tidal_pool_clear_aqua"


def rgb(data):
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGB"), dtype=np.float32)


def png(color):
    result = io.BytesIO()
    Image.fromarray(np.rint(np.clip(color, 0, 255)).astype(np.uint8)).save(result, format="PNG")
    return result.getvalue()


def restore_banks(installed, earlier):
    live, natural = rgb(installed), rgb(earlier)
    assert live.shape == natural.shape
    r, g, b = natural.transpose(2, 0, 1)
    stone = smooth(7, 28, b - r) * smooth(3, 24, g - r)
    # Recover the original jade-blue floor without touching the ochre path or
    # flooding bank and pool into one color at the edge.
    result = live + (.69 * stone)[..., None] * (natural - live)
    assert np.array_equal(result[stone == 0], live[stone == 0])
    return png(result)


def tag_descriptor(assets, payloads, model, texture, new_texture):
    descriptor = assets[model + ".pm"]
    old_name, new_name = f'tex/{texture}.png'.encode(), f'tex/{new_texture}.png'.encode()
    assert descriptor.count(old_name) == 1
    alias = model + RESTORE
    payloads[alias + ".pm"] = descriptor.replace(old_name, new_name)
    return alias


def restore_water(assets, frame_count, payloads):
    frames = [assets[f"tex/{YASUKI_WATER}{i:02}.png"] for i in range(frame_count)]
    levels = np.array([np.quantile(rgb(data) @ LUMA, [.08, .94]) for data in frames])
    colors = ((5, 67, 103), (41, 151, 172), .51)
    for i, frame in enumerate(frames):
        payloads[f"tex/{YASUKI_RESTORED}{i:02}.png"] = transfer(
            frame, YASUKI_WATER, water=colors, water_limits=tuple(levels.mean(axis=0)),
        )


def prepare(repo, bundle, group):
    engine = repo / "_tools/rpgcobo-tool"
    root = engine / ASSETS
    index = read(root / "index.json")
    story = read(engine / CATALOG)
    stock = {row["id"]: row for row in read(engine / RENDER)["rendersets"]}
    before = {mid: index[mid] for mid in GROUPS[group]}
    provenance = resource_files(root, before)
    result = deepcopy(before)
    payloads = {}
    if group == "doji":
        source_png = f"tex/{DOJI_ATLAS}.png"
        provenance[source_png] = (root / source_png).read_bytes()
        bank_name = DOJI_ATLAS + "_restored_banks"
        payloads[f"tex/{bank_name}.png"] = restore_banks(
            provenance[f"tex/{DOJI_INSTALLED}.png"], provenance[source_png],
        )
        row = result["M486"]
        assert row["renderPreset"] == "rt_coastal_brilliance_cave"
        assert row["waterSequence"] == {"prefix": "doji_tide_clear_water", "frames": 40, "seconds": 22.6}
        row["terrain"] = tag_descriptor(provenance, payloads, row["terrain"], DOJI_INSTALLED, bank_name)
    else:
        restore_water(provenance, 32, payloads)
        for row in result.values():
            assert row["renderPreset"] == "rt_hd2d_snake_den"
            assert row["waterSequence"] == {"prefix": YASUKI_WATER, "frames": 32, "seconds": 24.0}
            row["water"] = tag_descriptor(
                provenance, payloads, row["water"], YASUKI_WATER + "00", YASUKI_RESTORED + "00",
            )
            row["waterSequence"]["prefix"] = YASUKI_RESTORED

    maps = {}
    for mid, row in result.items():
        # Let existing lamps carry a little more amber through the original
        # cave palette using the same locations, range and authored hue.
        for lamp in row["poolLights"]:
            lamp[4] = round(lamp[4] * (1.095 if group == "doji" else 1.08), 3)
        maps[mid] = {
            "before": before[mid],
            "after": row,
            "story": digest(js(story[mid])),
            "world": digest((engine / "project/data/mapdata" / f"{mid}.bw").read_bytes()),
        }
    proof = {
        "maps": maps,
        "basePresets": {row["renderPreset"]: stock[row["renderPreset"]] for row in before.values()},
        "presets": [],
        "source": {key: digest(data) for key, data in provenance.items()},
        "files": {key: digest(data) for key, data in payloads.items()},
    }
    for key, content in payloads.items():
        path = bundle / "files" / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    (bundle / "coastal-proof.json").write_bytes(js(proof) + b"\n")
    print(f"Prepared {len(maps)} {group} cave maps with {len(payloads)} palette files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "stage", "publish"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--group", choices=GROUPS)
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    repo, bundle = args.repo.resolve(), args.bundle.resolve()
    if args.action == "prepare":
        if args.group is None:
            parser.error("--group is required to prepare.")
        prepare(repo, bundle, args.group)
    elif args.profile is None:
        parser.error("--profile is required to stage or publish.")
    else:
        apply(repo, args.profile.resolve(), bundle, args.action == "publish")


if __name__ == "__main__":
    main()
