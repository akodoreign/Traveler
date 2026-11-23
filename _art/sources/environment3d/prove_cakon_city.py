"""Check the Cakon city publisher's map, resource, and runtime fingerprints."""

import argparse
import json
from pathlib import Path

from cakon_worlds import GROUPS
from install_environment_rows import STAGE
from publish_castle_gates import CATALOG, INDEX, RUNTIME, hash_data, require, resource_files


HERE = Path(__file__).resolve().parent


def portals(map_data):
    return {key: event for key, event in map_data.get("event", {}).items() if event.get("role") == "portal"}


def fingerprint(repo, profile, *, published=False):
    engine = repo / "_tools/rpgcobo-tool"
    maps = GROUPS["city"]
    compiled = json.loads((HERE / "cakon-city-worlds.json").read_bytes())
    prepared = json.loads((STAGE / "index.json").read_bytes())
    checked = json.loads((profile / INDEX).read_bytes())
    live = json.loads((engine / INDEX).read_bytes())
    catalog = json.loads((engine / CATALOG).read_bytes())
    tested_catalog = json.loads((profile / CATALOG).read_bytes())
    runtime = (profile / RUNTIME).read_bytes()
    require(runtime == (HERE / RUNTIME.name).read_bytes(), "Runtime candidate differs from the tested profile")
    if published:
        require((engine / RUNTIME).read_bytes() == runtime, "Published runtime differs from the tested profile")

    scoped = {}
    for mid in maps:
        world = Path(f"project/data/mapdata/{mid}.bw")
        world_hash = hash_data((profile / world).read_bytes())
        require(world_hash == compiled[mid]["sha256"], f"Compiled candidate differs for {mid}")
        row = checked[mid]
        require(row == prepared[mid], f"Prepared art differs from the tested profile for {mid}")
        require(portals(catalog[mid]) == portals(tested_catalog[mid]), f"Portal catalog differs for {mid}")
        if published:
            require(hash_data((engine / world).read_bytes()) == world_hash, f"Published world differs for {mid}")
            require(live[mid] == row, f"Published art differs for {mid}")
        else:
            require(mid not in live, f"Cakon publisher expects {mid} to be unpublished")
        scoped[mid] = {"world_sha256": world_hash,
                       "row_sha256": hash_data(json.dumps(row, sort_keys=True).encode()),
                       "catalog_sha256": hash_data(json.dumps(catalog[mid], sort_keys=True).encode())}

    portal = catalog["M417"]["event"]["#113#"]
    require(portal["reqs0"] == [{"lvar": "G1043", "op": "==", "rvar": True}], "Cakon gate story unlock changed")
    require(portal["dest"]["mapid"] == "M418", "Cakon gate destination changed")
    rows = {mid: checked[mid] for mid in maps}
    resources = resource_files((profile / INDEX).parent, rows)
    live_resources = resource_files((engine / INDEX).parent, rows) if published else None
    if published:
        require(resources == live_resources, "A published Cakon resource differs from the test profile")
    else:
        for name, data in resources.items():
            live_path = (engine / INDEX).parent / name
            if live_path.is_file():
                require(live_path.read_bytes() == data, f"Candidate would replace shared resource {name}")
    return {"state": "published" if published else "candidate", "maps": scoped,
            "runtime_sha256": hash_data(runtime), "resource_count": len(resources),
            "resource_package_sha256": hash_data(json.dumps({k: hash_data(v) for k, v in resources.items()},
                                                              sort_keys=True).encode())}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--published", action="store_true")
    args = parser.parse_args()
    print(json.dumps(fingerprint(args.repo, args.profile, published=args.published), indent=2))
