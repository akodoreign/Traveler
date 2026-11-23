"""Install selected staged native environment rows and their referenced files."""

import argparse
import json
from pathlib import Path
import re
import shutil


STAGE = Path(__file__).resolve().parent / "native_environment"
EXTRA_MODELS = {
    "watchfires": ("kaiu_brazier_flame",),
    "chests": ("hoshi_storehouse_lid",),
    "brushReveal": ("shadowlands_thorns",),
    "magmaSpatter": ("magma_spatter",),
}


def environment_versions(rows):
    for row in rows:
        yield row
        if row.get("siege"):
            yield row["siege"]


def install(engine, ids, *, preserve_existing=False, replace_existing=False):
    destination = engine / "project/resource/native_environment"
    manifest = destination / "index.json"
    raw = manifest.read_bytes()
    live = json.loads(raw)
    if preserve_existing and not replace_existing and set(ids).intersection(live):
        raise ValueError("A selected map already has an installed environment")
    staged = json.loads((STAGE / "index.json").read_bytes())
    names = set()
    extra = set()
    selected = {mid: staged[mid] for mid in ids}
    for row in environment_versions(selected.values()):
        names.update(name for name in (row.get("terrain"), row.get("water")) if name)
        names.update(entry[0] for entry in row["placements"])
        names.update(entry[0] for entry in row.get("pondFish", []))
        names.update(entry[0] for entry in row.get("windStreaks", []))
        names.update(entry[0] for entry in row.get("leafDrift", []))
        names.update(entry["model"] for entry in row.get("portcullises", []))
        for field, dependencies in EXTRA_MODELS.items():
            if row.get(field):
                names.update(dependencies)
        for entry in row.get("doors", []):
            names.update(entry.get("models", ("town_door_frame", "town_door_leaf")))
            if entry.get("stoop"):
                names.add(entry["stoop"])
        extra.update(entry["motion"] + ".mot" for entry in row.get("seats", []))
        if row.get("water"):
            prefix, count = {"lava": ("magma", 24), "storm": ("storm", 16)}.get(
                row.get("waterMode"), ("surf", 32))
            if "waterSequence" in row:
                sequence = row["waterSequence"]
                prefix, count = sequence["prefix"], sequence["frames"]
            extra.update(f"tex/{prefix}{i:02d}.png" for i in range(count))
    live.update(selected)

    for name in names:
        path = STAGE / (name + ".pm")
        descriptor = path if path.is_file() else destination / path.name
        pm = descriptor.read_text(encoding="utf8")
        extra.add(path.name)
        extra.update(re.findall(r'^\s*(?:modeldata|texture[0-9]+)\s*=\s*"([^"]+)"', pm, re.M))
    copies = []
    for relative in sorted(extra):
        path = STAGE / relative
        target = destination / relative
        if not path.is_file() and not target.is_file():
            raise FileNotFoundError(path)
        if path.is_file() and (not target.is_file() or path.read_bytes() != target.read_bytes()):
            if preserve_existing and target.is_file():
                raise ValueError(f"An existing shared asset would change: {target}")
            copies.append((path, target))
    for path, target in copies:
        shutil.copyfile(path, target)

    with manifest.open("r+b") as file:
        if file.read() != raw:
            raise RuntimeError("The environment index changed during installation")
        file.seek(0)
        file.write(json.dumps(live, separators=(",", ":")).encode())
        file.truncate()
    print(f"Installed {', '.join(ids)} with {len(names)} meshes. {len(live)} maps in the environment index.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("maps", nargs="+")
    parser.add_argument("--preserve-existing", action="store_true")
    args = parser.parse_args()
    install(args.engine, args.maps, preserve_existing=args.preserve_existing)
