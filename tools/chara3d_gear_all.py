"""Generate or check native gear geometry and wearer texture atlases."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from PIL import Image

from chara3d_sheet import blender_exe, look
from gen_sidecast import CLAN
import gear_catalog as catalog
from gear_palette import NATIVE_CLANS, SIZE, atlas, normal_atlas
from gear_decals import SIZE as DECAL_SIZE, sheet
from rig3d import ROOT

PROJECT = ROOT / "_tools" / "rpgcobo-tool" / "project"
OUT = PROJECT / "resource" / "native_gear"


def read(path):
    return json.loads(path.read_bytes())


def build_index():
    roster = read(PROJECT / "resource/native_chara/roster.json")
    armor = read(PROJECT / "data/armor.json")
    enemies = read(PROJECT / "resource/enemy_pic.json")
    players = read(PROJECT / "data/player.json")
    items = catalog.registry()
    visible = {item for item, spec in armor.items() if isinstance(spec, dict)
               and spec.get("eqtype") in (10, 11, 13, 14, 15) and spec.get("name") and not (spec.get("rt_costume") or spec.get("rt_costume_head"))
               and not spec["name"].startswith("(unused")}
    if visible - items.keys() or items.keys() - armor.keys():
        raise ValueError(f"Missing armor designs {sorted(visible - items.keys())}; "
                         f"unknown IDs {sorted(items.keys() - armor.keys())}")
    player_clans = {}
    for spec in players.values():
        if isinstance(spec, dict) and spec.get("rt_clan") in CLAN:
            pic = enemies.get(spec.get("mdlid"), {}).get("pic3d")
            if pic:
                player_clans[Path(pic).stem] = spec["rt_clan"]
    looks = {key: look(key) for key in roster}
    palettes = {key: player_clans.get(key, spec.get("clan", spec.get("mon", "ronin")))
                for key, spec in looks.items()}
    palettes = {key: clan if clan in CLAN else "ronin" for key, clan in palettes.items()}
    return {"items": items, "weapons": catalog.WEAPONS, "palettes": palettes,
            "clans": sorted(CLAN), "decals": True}, looks


def verify(index, out=OUT):
    if index != read(out / "gear.json"):
        raise ValueError("The native gear catalog is out of date")
    decal_meshes = [item + "_decal" for item in index["items"]]
    meshes = [*index["items"], *decal_meshes, *("weapon_" + k for k in index["weapons"]), "natsuko_uncovered"]
    meshes += [f"{item}_yosai{suffix}" for item in catalog.HEAD for suffix in ("", "_decal")]
    decal_meshes += [f"{item}_yosai_decal" for item in catalog.HEAD]
    decals = [f"decal/{clan}/{item}.png" for clan in index["clans"] for item in index["items"]]
    expected = {"gear.json", "tex/wardrobe_normal.png", *(name + ext for name in meshes for ext in (".pm", ".mdl"))}
    textures = [*index["palettes"], *("clan_" + name for name in index["clans"])]
    expected.update(f"palette/{name}.png" for name in textures)
    expected.update(decals)
    for item in catalog.HEAD:
        descriptor = (out / f"{item}.pm").read_text(encoding="utf-8")
        for line in descriptor.splitlines():
            if 'texture1 = "tex/head_' in line:
                expected.add(line.split('"')[1])
    actual = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    if expected != actual:
        raise ValueError(f"Missing gear assets {sorted(expected - actual)}; unexpected {sorted(actual - expected)}")
    for name in meshes:
        pm, mdl = out / (name + ".pm"), out / (name + ".mdl")
        if not mdl.stat().st_size or f'modeldata = "{name}.mdl"' not in pm.read_text(encoding="utf-8"):
            raise ValueError(f"Invalid native gear mesh {name}")
    for name in decal_meshes:
        if "alphatest = 1" not in (out / (name + ".pm")).read_text(encoding="utf-8"):
            raise ValueError(f"Missing alpha cutoff on {name}")
    for file in decals:
        with Image.open(out / file) as image:
            if image.size != DECAL_SIZE or image.mode != "RGBA" or image.getchannel("A").getextrema() != (0, 255):
                raise ValueError(f"Invalid decal sheet {file}")
    for name in textures:
        with Image.open(out / "palette" / f"{name}.png") as image:
            if image.size != (SIZE, SIZE) or image.mode != "RGB":
                raise ValueError(f"Invalid wearer texture {name}")
            image.verify()
    print(f"Verified {len(index['items'])} wearable designs, {len(index['weapons'])} weapon looks, "
          f"{len(index['palettes'])} wearer textures, {len(index['clans'])} clan palettes, and {len(decals)} decal sheets")


def export(job):
    subprocess.run([blender_exe(), "-b", "--factory-startup", "--threads", "4",
                    "--python-exit-code", "1", "--python", str(ROOT / "tools/blender/chara3d_gear.py"),
                    "--", str(job)], check=True)


def textures(out, index, looks):
    palette = out / "palette"
    palette.mkdir(parents=True, exist_ok=True)
    (out / "tex").mkdir(exist_ok=True)
    normal_atlas(out / "tex" / "wardrobe_normal.png")
    for name, colours in CLAN.items():
        atlas(palette / f"clan_{name}.png", colours, {}, name)
        decal_dir = out / "decal" / name
        decal_dir.mkdir(parents=True, exist_ok=True)
        for item, slot in index["items"].items():
            style = catalog.BODY[item][0] if slot == "body" else (
                catalog.HEAD.get(item) or catalog.ACCESSORY.get(item) or "cape")
            sheet(decal_dir / f"{item}.png", name, NATIVE_CLANS.get(name, colours), item, slot, style)
    for key, clan in index["palettes"].items():
        atlas(palette / f"{key}.png", CLAN[clan], looks[key], clan)
    (out / "gear.json").write_text(json.dumps(index, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT, help="build or verify an alternate pack directory")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--head-only", action="store_true", help="refresh equipped headwear detail without rebuilding palettes or decals")
    mode.add_argument("--garments-only", action="store_true", help="refresh body garments and their decal geometry")
    mode.add_argument("--textures-only", action="store_true", help="stage palettes and decals for a separate Blender export")
    args = parser.parse_args()
    out = args.output.resolve()
    index, looks = build_index()
    if args.textures_only:
        textures(out, index, looks)
        return
    if args.head_only or args.garments_only:
        with tempfile.TemporaryDirectory() as temp:
            job = Path(temp) / "headwear.json"
            job.write_text(json.dumps({"out": str(out), "head_only": args.head_only,
                                       "garments_only": args.garments_only,
                                       "natsuko": looks["trav_natsuko"]}), encoding="utf-8")
            export(job)
    elif not args.check:
        textures(out, index, looks)
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "job.json"
            config.write_text(json.dumps({"out": str(out), "natsuko": looks["trav_natsuko"]}), encoding="utf-8")
            export(config)
    verify(index, out)


if __name__ == "__main__":
    main()
