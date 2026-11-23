"""Prepare steady bounced daylight for the Doji beach encounter."""
import argparse
from copy import deepcopy
from pathlib import Path

from coastal_daylight import ASSETS, CATALOG, RENDER, apply, digest, js, read, resource_files, s32


MAP = "M828"
CURRENT = "rt_coastal_brilliance_arena_horizon"
REVISED = "rt_coastal_brilliance_arena_open_fill"
SKY = Path("project/resource/ibltex/traveler_clear_coast_ibl.ktx")


def fill(position, power):
    return {
        "type": 2,
        "pos": list(position),
        "k1": 9.5,
        "color": s32(0xE3EFF8FF),
        "power": power,
        "shadow": {},
    }


def prepare(repo, bundle):
    live = repo / "_tools/rpgcobo-tool"
    assets = live / ASSETS
    row = read(assets / "index.json")[MAP]
    assert row["renderPreset"] == CURRENT, "M828 requires the installed coast horizon."
    current = next(preset for preset in read(live / RENDER)["rendersets"] if preset["id"] == CURRENT)
    revised = deepcopy(current)
    revised["id"] = REVISED
    revised["envlights"][0].update(head=156, pitch=67)
    # Keep the shadow-producing sun first. These steady, shadowless points
    # model cove bounce in front of the foe and traveler lines separately.
    revised["envlights"].extend((fill((27.8, 3.2, 31.3), 1230), fill((35.5, 3.4, 29.9), 1290)))
    after = {**row, "renderPreset": REVISED}
    world = live / "project/data/mapdata" / f"{MAP}.bw"
    sky = (live / SKY).read_bytes()
    sky_digest = {SKY.as_posix(): digest(sky)}
    proof = {
        "maps": {
            MAP: {
                "before": row,
                "after": after,
                "story": digest(js(read(live / CATALOG)[MAP])),
                "world": digest(world.read_bytes()),
            }
        },
        "basePresets": {CURRENT: current},
        "presets": [revised],
        "source": {key: digest(content) for key, content in resource_files(assets, {MAP: row}).items()},
        "projectSource": sky_digest,
        "projectFiles": sky_digest,
        "files": {},
    }
    sky_file = bundle / "files" / SKY
    sky_file.parent.mkdir(parents=True, exist_ok=True)
    sky_file.write_bytes(sky)
    (bundle / "coastal-proof.json").write_bytes(js(proof) + b"\n")


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
        parser.error("--profile is required for stage or publish")
    else:
        apply(repo, args.profile.resolve(), bundle, args.action == "publish")


if __name__ == "__main__":
    main()
