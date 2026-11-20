"""Publish reviewed generated wardrobe pieces and their runtime registrations."""
import argparse
import json
from pathlib import Path
import re
import shutil


def publish(stage, native, changes):
    files = set()
    for group in changes.values():
        for spec in group.values():
            key = spec["mesh"]
            meshes = [key]
            if spec.get("decal") or spec.get("sheet"):
                meshes.append(key + "_decal")
            for name in meshes:
                pm = stage / f"{name}.pm"
                mdl = stage / f"{name}.mdl"
                if mdl.read_bytes()[:4] != b"SMDL":
                    raise ValueError(f"Invalid rendered outfit: {mdl}")
                files.update((pm.name, mdl.name))
                files.update(re.findall(r'texture\d+ = "(tex/[^"]+)"', pm.read_text("utf8")))
            if spec.get("dyed"):
                fabrics = sorted((stage / "tex").glob(f"*/{key}.png"))
                if len(fabrics) != 12:
                    raise ValueError(f"{key}: expected 12 clan dye textures")
                files.update(path.relative_to(stage).as_posix() for path in fabrics)
            if sheet := spec.get("sheet"):
                files.add(sheet)
    for filename in files:
        if not (stage / filename).stat().st_size:
            raise ValueError(f"Missing wardrobe material {filename}")
    native.mkdir(parents=True, exist_ok=True)
    index = native / "index.json"
    previous = json.loads(index.read_text("utf8")) if index.exists() else {}
    for filename in sorted(files):
        destination = native / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stage / filename, destination)
    for category, maps in changes.items():
        previous.setdefault(category, {}).update(maps)
    temporary = index.with_suffix(".tmp")
    temporary.write_text(json.dumps(previous, indent=1) + "\n", encoding="utf8")
    temporary.replace(index)
    print("Installed", ", ".join(sorted({spec["mesh"] for group in changes.values() for spec in group.values()})))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", type=Path)
    parser.add_argument("native", type=Path)
    parser.add_argument("changes", type=Path)
    args = parser.parse_args()
    publish(args.stage, args.native, json.loads(args.changes.read_text("utf8")))
