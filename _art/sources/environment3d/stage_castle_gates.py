"""Load an audited gate candidate into an isolated game profile for native testing."""

import argparse
import json
from pathlib import Path

import castle_gate_candidates as recipe
from kensu_worlds import stage_worlds
from publish_castle_gates import CATALOG, HERE, INDEX, RUNTIME, path_inside, require, replace_file_contents, resource_files


def stage(repo, profile, group):
    expected_profiles = HERE.parent / "multi-window/profiles"
    require(profile.parent == expected_profiles.resolve(), "Choose an existing isolated test profile")
    bundle = HERE / f"castle-gates-{group}-candidate"
    rows = json.loads((bundle / "rows.json").read_bytes())
    maps = tuple(recipe.GROUPS[group])
    require(set(rows) == set(maps), f"Wrong scope for art bundle {bundle.name}")

    art = (profile / INDEX).parent
    engine = repo / "_tools/rpgcobo-tool"
    originals = json.loads((engine / INDEX).read_bytes())
    baseline = (profile / INDEX).read_bytes()
    changed = {**json.loads(baseline), **rows}
    catalog_before = (profile / CATALOG).read_bytes()
    source_catalog = json.loads((engine / CATALOG).read_bytes())
    catalog = json.loads(catalog_before)
    for mid in maps:
        catalog[mid] = source_catalog[mid]
    native = (HERE / RUNTIME.name).read_bytes()
    assets = resource_files((engine / INDEX).parent, {mid: originals[mid] for mid in maps})
    for asset in bundle.rglob("*"):
        if not asset.is_file() or asset.name == "rows.json":
            continue
        relative = asset.relative_to(bundle).as_posix()
        source = asset.read_bytes()
        require(assets.get(relative, source) == source, f"Candidate alters existing art at {relative}")
        assets[relative] = source
    for relative, source in assets.items():
        dest = path_inside(art, relative)
        if dest.exists():
            if dest.read_bytes() != source:
                live = path_inside((engine / INDEX).parent, relative)
                require(live.is_file() and live.read_bytes() == source,
                        f"Staging would overwrite unrelated profile art: {relative}")
                replace_file_contents(dest, source)
        else:
            with dest.open("xb") as output:
                output.write(source)

    stage_worlds(repo, profile, False, maps, f"castle-gates-{group}", recipe.variant(repo, group), maps)
    require((profile / INDEX).read_bytes() == baseline, "Profile index changed during compilation")
    require((profile / CATALOG).read_bytes() == catalog_before, "Profile catalog changed during compilation")
    replace_file_contents(profile / INDEX, json.dumps(changed, separators=(",", ":")).encode())
    if catalog != json.loads(catalog_before):
        replace_file_contents(profile / CATALOG, json.dumps(catalog, ensure_ascii=False, separators=(",", ":")).encode())
    replace_file_contents(profile / RUNTIME, native)
    print(f"Staged {', '.join(maps)} in {profile.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("group", choices=recipe.GROUPS)
    args = parser.parse_args()
    stage(args.repo.resolve(), args.profile.resolve(), args.group)
