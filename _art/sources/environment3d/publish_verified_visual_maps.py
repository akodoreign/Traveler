"""Install an exact native-reviewed environment bundle without changing map data."""
import argparse
import json
from pathlib import Path

from publish_castle_gates import CATALOG, INDEX, hash_data, path_inside, publish, require, resource_files


def plan(repo, profile, receipt_path, render_settings=None):
    engine = repo / "_tools/rpgcobo-tool"
    require(profile != engine.resolve(), "Use a separate profile for native review")
    receipt = json.loads(receipt_path.read_bytes())
    candidate = receipt_path.parent / "native_environment"
    rows = json.loads((candidate / "index.json").read_bytes())
    review = receipt.get("maps")
    if review is None:
        require(len(rows) == 1, "Single-map receipts must have exactly one environment row")
        review = {next(iter(rows)): receipt}
    require(rows.keys() == review.keys(), "Receipt and bundle list different maps")
    checked_index = json.loads((profile / INDEX).read_bytes())
    catalog_data = (engine / CATALOG).read_bytes()
    live_catalog = json.loads(catalog_data)
    checked_catalog = json.loads((profile / CATALOG).read_bytes())
    for key, baseline in review.items():
        require(rows[key] == checked_index[key], f"Reviewed profile has different art for {key}")
        original = live_catalog[key]
        expected = original
        if render_settings and key in render_settings:
            prior, selected = render_settings[key]
            require(original["rsetid"] in (prior, selected), f"Live render preset changed for {key}")
            expected = {**original, "rsetid": selected}
            original = {**original, "rsetid": prior}
            live_catalog[key] = expected
        require(expected == checked_catalog[key], f"Gameplay catalog differs for {key}")
        catalog_hash = hash_data(json.dumps(original, sort_keys=True).encode())
        require(catalog_hash == baseline["catalog_hash"], f"Outdated catalog receipt for {key}")
        world = Path(f"project/data/mapdata/{key}.bw")
        world_hash = baseline["world_hash"]
        for root in (profile, engine):
            require(hash_data((root / world).read_bytes()) == world_hash, f"Different collision on {key} in {root}")

    assets = resource_files(candidate, rows)
    require({key: hash_data(data) for key, data in assets.items()} == receipt["files"], "Asset receipt differs")
    additions = {}
    for key, data in assets.items():
        require(path_inside((profile / INDEX).parent, key).read_bytes() == data, f"Reviewed asset differs: {key}")
        installed = path_inside((engine / INDEX).parent, key)
        if installed.exists():
            require(installed.read_bytes() == data, f"Shared live asset differs: {key}")
        else:
            require(installed.parent.is_dir(), f"Native resource directory missing for {key}")
            additions[installed] = data
    index = engine / INDEX
    prior = index.read_bytes()
    live = json.loads(prior)
    updated = json.dumps({**live, **rows}, ensure_ascii=False, separators=(",", ":")).encode()
    before, replace = {index: prior}, {index: updated}
    if render_settings:
        before[engine / CATALOG] = catalog_data
        replace[engine / CATALOG] = json.dumps(live_catalog, ensure_ascii=False, separators=(",", ":")).encode()
    return rows, before, replace, additions


def install(repo, profile, receipt_path):
    rows, before, replace, additions = plan(repo, profile, receipt_path)
    publish(before, replace, additions)
    print(f"Published {', '.join(rows)} with {len(additions)} new assets.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "profile", "receipt_path"):
        parser.add_argument(name, type=lambda value: Path(value).resolve())
    install(**vars(parser.parse_args()))
