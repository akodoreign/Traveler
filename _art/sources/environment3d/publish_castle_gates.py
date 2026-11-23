"""Fingerprint approved gate candidates and publish their exact tested files."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path, PurePosixPath
import re

from install_environment_rows import EXTRA_MODELS


CATALOG = Path("project/data/map.json")
INDEX = Path("project/resource/native_environment/index.json")
RUNTIME = Path("project/plugin/rokugan/RokuganEnvironmentKit.sk")
HERE = Path(__file__).resolve().parent
DESCRIPTOR_FILE = re.compile(r'^\s*(?:modeldata|texture[0-9]+)\s*=\s*"([^"]+)"', re.M)
PROTECTED_MAPS = {"M413", "M414", "M415", "M416", "M417", "M883"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def hash_data(content):
    return sha256(content).hexdigest()


def path_inside(root, relative):
    relative = PurePosixPath(relative)
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), f"Resource escapes its directory: {relative}")
    return path


def resource_files(resource_root, rows):
    names = set()
    files = set()
    for row in rows.values():
        names.update(name for name in (row.get("terrain"), row.get("water")) if name)
        for field in ("placements", "pondFish", "windStreaks", "leafDrift"):
            names.update(entry[0] for entry in row.get(field, ()))
        names.update(entry["model"] for entry in row.get("portcullises", ()))
        for field, dependencies in EXTRA_MODELS.items():
            if row.get(field):
                names.update(dependencies)
        for entry in row.get("doors", ()):
            names.update(entry.get("models", ("town_door_frame", "town_door_leaf")))
            if entry.get("stoop"):
                names.add(entry["stoop"])
        files.update(entry["motion"] + ".mot" for entry in row.get("seats", ()))
        if row.get("water"):
            prefix, count = {"lava": ("magma", 24), "storm": ("storm", 16)}.get(
                row.get("waterMode"), ("surf", 32)
            )
            if sequence := row.get("waterSequence"):
                prefix, count = sequence["prefix"], sequence["frames"]
            files.update(f"tex/{prefix}{i:02d}.png" for i in range(count))
    for name in names:
        descriptor = name + ".pm"
        files.add(descriptor)
        files.update(DESCRIPTOR_FILE.findall(path_inside(resource_root, descriptor).read_text("utf-8")))
    return {file: path_inside(resource_root, file).read_bytes() for file in sorted(files)}


def load_candidate(repo, profile, recipe, group):
    engine = repo / "_tools/rpgcobo-tool"
    require(profile != engine.resolve(), "The source must be a replayed, isolated profile")
    maps = tuple(recipe.GROUPS[group])
    require(maps and len(maps) == len(set(maps)), "The recipe must list unique map IDs")
    for mid in maps:
        require(re.fullmatch(r"M\d{3}", mid) and mid not in PROTECTED_MAPS, f"Out-of-scope map: {mid}")

    source, current, candidate, original, updated = recipe.variant(repo, group)
    require(source.resolve() == (repo / "tools/gen_maps.py").resolve(), "Unexpected map generator source")
    require(original != updated, "The gate generator contains no candidate change")
    for mid in maps:
        existing, existing_events = current.make(mid)
        world, events = candidate.make(mid)
        before_events = existing_events.ev if existing_events else None
        after_events = events.ev if events else None
        require(before_events == after_events, f"The candidate alters generated story events on {mid}")
        require((existing.w, existing.d) == (world.w, world.d), f"The candidate resizes {mid}")

    live_catalog = json.loads((engine / CATALOG).read_bytes())
    checked_catalog = json.loads((profile / CATALOG).read_bytes())
    for mid in maps:
        require(live_catalog[mid] == checked_catalog[mid], f"The profile catalog differs on {mid}")

    before_index = (engine / INDEX).read_bytes()
    live = json.loads(before_index)
    checked = json.loads((profile / INDEX).read_bytes())
    rows = {mid: checked[mid] for mid in maps}
    planned = json.loads((HERE / f"castle-gates-{group}-candidate/rows.json").read_bytes())
    require(rows == planned, "The profile rows differ from the reviewed art bundle")
    compiled = json.loads((HERE / f"castle-gates-{group}-worlds.json").read_bytes())
    before = {source: original, engine / INDEX: before_index}
    replace = {source: updated}
    for mid in maps:
        relative = Path(f"project/data/mapdata/{mid}.bw")
        before[engine / relative] = (engine / relative).read_bytes()
        replace[engine / relative] = (profile / relative).read_bytes()
        require(replace[engine / relative] != before[engine / relative], f"The profile still has the live world for {mid}")
        require(hash_data(replace[engine / relative]) == compiled[mid]["sha256"], f"Compiled world receipt differs for {mid}")
    before[engine / RUNTIME] = (engine / RUNTIME).read_bytes()
    replace[engine / RUNTIME] = (profile / RUNTIME).read_bytes()
    replace[engine / INDEX] = json.dumps({**live, **rows}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    resources = resource_files((profile / INDEX).parent, rows)
    add = {}
    for relative, content in resources.items():
        target = path_inside((engine / INDEX).parent, relative)
        if target.is_file():
            require(target.read_bytes() == content, f"The candidate would overwrite a shared asset: {relative}")
        else:
            require(target.parent.is_dir(), f"Missing native resource directory for {relative}")
            add[target] = content

    proof = {
        "recipe": recipe.__name__,
        "group": group,
        "maps": list(maps),
        "catalog": {mid: hash_data(json.dumps(checked_catalog[mid], sort_keys=True).encode()) for mid in maps},
        "baseline": {str(path.relative_to(repo)): hash_data(data) for path, data in before.items()},
        "candidate": {str(path.relative_to(repo)): hash_data(data) for path, data in replace.items()},
        "resources": {key: hash_data(value) for key, value in resources.items()},
    }
    return proof, before, replace, add


def publish(before, replace, add):
    changed = []
    created = []
    try:
        for path, content in add.items():
            with path.open("xb") as target:
                created.append(path)
                target.write(content)
        for path, content in replace.items():
            require(path.read_bytes() == before[path], f"The live file changed after review: {path}")
            if content != before[path]:
                changed.append(path)
                replace_file_contents(path, content)
        for path, content in {**add, **replace}.items():
            require(hash_data(path.read_bytes()) == hash_data(content), f"Install verification failed: {path}")
    except BaseException:
        for path in reversed(changed):
            replace_file_contents(path, before[path])
        for path in reversed(created):
            path.unlink()
        raise


def replace_file_contents(path, content):
    with path.open("r+b") as target:
        target.write(content)
        target.truncate()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "verify", "publish"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("recipe", help="Import name for the reviewed gate recipe")
    parser.add_argument("group", help="Map group from the gate recipe")
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    recipe = import_module(args.recipe)
    proof, before, replace, add = load_candidate(args.repo.resolve(), args.profile.resolve(), recipe, args.group)
    if args.action == "capture":
        with args.receipt.open("x", encoding="utf-8") as receipt:
            json.dump(proof, receipt, indent=2, ensure_ascii=False)
    else:
        stored = json.loads(args.receipt.read_text("utf-8"))
        require(proof == stored, "The approved profile or the live baseline changed")
        if args.action == "publish":
            publish(before, replace, add)
    print(f"{args.action}: {', '.join(proof['maps'])}; {len(add)} new resources")


if __name__ == "__main__":
    main()
