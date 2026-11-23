"""Stage and publish the two fitted Dragon roadside shelters."""

import argparse
from copy import deepcopy
import json
from pathlib import Path

from install_environment_rows import STAGE
from publish_castle_gates import HERE, INDEX, hash_data, path_inside, publish, require, resource_files


MAPS = ("M379", "M382")
OLD = "dragon_slate_waystation"
NEW = "dragon_fitted_slate_waystation"
RECEIPT = HERE / "dragon-waystation-replacement.json"


def install(repo, profile, action):
    engine = repo / "_tools/rpgcobo-tool"
    expected_profiles = HERE.parent / "multi-window/profiles"
    require(profile.parent == expected_profiles.resolve(), "Choose an existing isolated test profile")
    receipt = json.loads(RECEIPT.read_bytes())
    require(set(receipt["before"]) == set(receipt["rows"]) == set(MAPS), "Unexpected maps in shelter receipt")
    for mid in MAPS:
        expected = deepcopy(receipt["before"][mid])
        entries = [entry for entry in expected["placements"] if entry[0] == OLD]
        require(len(entries) == 1, f"Unexpected shelter count on {mid}")
        entries[0][0] = NEW
        require(expected == receipt["rows"][mid], f"Receipt changes more than the shelter model on {mid}")
        world = Path(f"project/data/mapdata/{mid}.bw")
        require((profile / world).read_bytes() == (engine / world).read_bytes(), f"Profile geometry differs on {mid}")

    profile_art = (profile / INDEX).parent
    if action == "publish":
        checked = json.loads((profile / INDEX).read_bytes())
        require(all(checked[mid] == receipt["rows"][mid] for mid in MAPS), "The profile lacks the approved shelter rows")
    destination = profile if action == "stage" else engine
    sources = STAGE if action == "stage" else profile_art
    before = (destination / INDEX).read_bytes()
    manifest = json.loads(before)
    live = json.loads((engine / INDEX).read_bytes())
    for mid in MAPS:
        expected_rows = receipt["rows"] if action == "verify" else receipt["before"]
        require(live[mid] == expected_rows[mid], f"Live shelter row does not match the receipt on {mid}")

    assets = {}
    for relative, expected_hash in receipt["files"].items():
        resource = path_inside(sources, relative)
        asset = resource.read_bytes()
        require(hash_data(asset) == expected_hash, f"Unexpected shelter asset at {relative}")
        assets[relative] = asset
    if action == "stage":
        base_rows = deepcopy(receipt["rows"])
        for row in base_rows.values():
            row["placements"] = [entry for entry in row["placements"] if entry[0] != NEW]
        assets.update(resource_files((engine / INDEX).parent, base_rows))

    files = {}
    originals = {destination / INDEX: before}
    updates = {}
    owned_terrain = {receipt["rows"][mid]["terrain"] + ".pm" for mid in MAPS}
    for relative, asset in assets.items():
        target = path_inside((destination / INDEX).parent, relative)
        if target.exists():
            old = target.read_bytes()
            if old != asset:
                require(action == "stage" and relative in owned_terrain, f"Shelter install would overwrite {relative}")
                originals[target] = old
                updates[target] = asset
        else:
            require(action != "verify", f"Missing published shelter asset {relative}")
            files[target] = asset
    if action != "verify":
        updated = json.dumps({**manifest, **receipt["rows"]}, ensure_ascii=False, separators=(",", ":")).encode()
        updates[destination / INDEX] = updated
        publish(originals, updates, files)
    print(f"{action}: {', '.join(MAPS)}; {len(receipt['files'])} shelter files verified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("stage", "publish", "verify"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    install(args.repo.resolve(), args.profile.resolve(), args.action)
