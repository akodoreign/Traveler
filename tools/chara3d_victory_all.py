"""Build and verify native inventory weapon models and victory clips."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

from chara3d_sheet import blender_exe
from rig3d import ROOT
from rig3d_poses import SPECIAL, VIEWS
from rig3d_sheet import plan
from victory_poses import FRAMES, SPEED
from weapon_catalog import COMBAT_BANKS, FAMILIES, inventory

PROJECT = ROOT / "_tools/rpgcobo-tool/project"
OUT = PROJECT / "resource/native_weapons"


def read(path):
    return json.loads(path.read_bytes())


def build():
    weapons = read(PROJECT / "data/weapon.json")
    roster = read(PROJECT / "resource/native_chara/roster.json")
    players = read(PROJECT / "data/player.json")
    pictures = read(PROJECT / "resource/enemy_pic.json")
    items = inventory(weapons)
    tracks = defaultdict(set)
    for key, spec in roster.items():
        tracks[spec["weapon"]].add(key)
    for spec in players.values():
        if not isinstance(spec, dict):
            continue
        pic = pictures.get(spec.get("mdlid"), {}).get("pic3d")
        if not pic:
            continue
        key = Path(pic).stem
        if key not in roster:
            continue
        tracks["none"].add(key)
        for item, kind in items.items():
            definition = weapons[item]
            allowed = spec.get("eqtypebits", 0) & (1 << definition["eqtype"])
            required = definition.get("rt_only_clan")
            if allowed and (not required or required == spec.get("rt_clan")):
                tracks[kind["kind"]].add(key)
    banks = {kind: {"family": FAMILIES[kind], "actors": sorted(actors)}
             for kind, actors in sorted(tracks.items())}
    victory = {kind: {key: i * (FRAMES + 1) for i, key in enumerate(info["actors"])}
               for kind, info in banks.items()}
    index = {"items": items, "victory": victory, "frames": FRAMES, "speed": SPEED,
             "combat": list(COMBAT_BANKS)}
    job_items = {item: look | {"name": weapons[item]["name"]} for item, look in items.items()}
    combat = {}
    for weapon in COMBAT_BANKS:
        family = FAMILIES[weapon]
        frames = []
        for name, kind, count, _ in plan()[0]:
            kind = VIEWS.get(kind, (kind,))[0]
            if name in ("critical", "void_critical"):
                kind = SPECIAL[family][name == "void_critical"]
            frames.extend((kind, i, count) for i in range(count))
        combat[weapon] = {"family": family, "frames": [*frames, frames[-1]]}
    return index, {"out": str(OUT), "weapons": job_items, "banks": banks, "combat": combat}


def verify(index):
    if read(OUT / "weapons.json") != index:
        raise ValueError("Weapon and victory registry is out of date")
    models = [item for item, look in index["items"].items() if look["kind"] != "none"]
    banks = [*(f"combat_{kind}.mot" for kind in index["combat"]),
             *(f"victory_{kind}.mot" for kind in index["victory"])]
    expected = {"weapons.json", *banks, *(item + ext for item in models for ext in (".mdl", ".pm"))}
    actual = {p.name for p in OUT.iterdir() if p.is_file()}
    if actual != expected:
        raise ValueError(f"Missing weapon assets {sorted(expected - actual)}; unexpected {sorted(actual - expected)}")
    for file in banks:
        with (OUT / file).open("rb") as stream:
            if stream.read(4) != b"SMOT":
                raise ValueError(f"Invalid motion file: {file}")
    meshes = set()
    for item in models:
        data = (OUT / f"{item}.mdl").read_bytes()
        if f'modeldata = "{item}.mdl"' not in (OUT / f"{item}.pm").read_text() or not data:
            raise ValueError(f"Invalid native model for {item}")
        digest = sha256(data).digest()
        if digest in meshes:
            raise ValueError(f"Duplicate inventory weapon mesh for {item}")
        meshes.add(digest)
    all_actors = {key for offsets in index["victory"].values() for key in offsets}
    print(f"Verified {len(models)} inventory weapon meshes and {sum(map(len, index['victory'].values()))} "
          f"character/weapon victory clips across {len(all_actors)} native actors")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    index, job = build()
    if not args.check:
        OUT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as temp:
            data = Path(temp) / "victory.json"
            data.write_text(json.dumps(job), encoding="utf-8")
            subprocess.run([blender_exe(), "-b", "--factory-startup", "--threads", "4",
                            "--python-exit-code", "1", "--python",
                            str(ROOT / "tools/blender/chara3d_victory.py"), "--", str(data)], check=True)
        (OUT / "weapons.json").write_text(json.dumps(index, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    verify(index)


if __name__ == "__main__":
    main()
