"""Install the refreshed shared-rig Shosuro Renegade in a closed tool profile."""

import argparse
import hashlib
import json
from pathlib import Path
import re


STAGE = Path(__file__).resolve().parent
PROJECT = Path("project")
RESOURCE = PROJECT / "resource"
HUMAN = RESOURCE / "native_human"
TAILOR = RESOURCE / "native_tailoring"
FOE = RESOURCE / "native_foe"
WEAPONS = RESOURCE / "native_weapons"
ORNAMENT = RESOURCE / "native_ornament"
KEY = "EP427"
DONOR = "side_shiko"
FACE = DONOR + "_portrait_face"
MASK = "ep427_renegade_noh"
PALETTE = "A120_renegade_crimson"
ALIASES = {"E227", "E561", "E951"}


def read(target, rel):
    return (target / rel).read_bytes()


def load_json(target, rel):
    return json.loads(read(target, rel))


def descriptor(target, folder, stem):
    raw = read(target, folder / (stem + ".pm"))
    model = re.search(rb'modeldata\s*=\s*"([^"]+)"', raw)[1].decode()
    assert read(target, folder / model).startswith(b"SMDL"), stem
    for texture in re.findall(rb'texture[0-9]+\s*=\s*"([^"]+)"', raw):
        assert (target / folder / texture.decode()).is_file(), (stem, texture)
    return raw


def change_row(raw, previous, result):
    text = raw.decode()
    pattern = rf'(?m)^( +)"{KEY}": \{{\r?\n(?:(?!^\1\}})[\s\S])*^\1\}}(?=,|\r?$)'
    match = re.search(pattern, text)
    assert match and json.loads(match[0].split(":", 1)[1]) == previous
    indent = match[1]
    eol = "\r\n" if "\r\n" in match[0] else "\n"
    value = json.dumps(result, indent=min(len(indent), 2)).splitlines()
    line = indent + f'"{KEY}": ' + value[0] + eol
    line += eol.join(indent + line for line in value[1:])
    return (text[:match.start()] + line + text[match.end():]).encode()


def plan(target):
    human_file, tailoring_file = HUMAN / "index.json", TAILOR / "index.json"
    human = load_json(target, human_file)
    tailoring = load_json(target, tailoring_file)["defaults"]
    foes = load_json(target, FOE / "index.json")
    enemies = load_json(target, PROJECT / "data/enemy.json")
    ornaments = load_json(target, ORNAMENT / "index.json")
    weapon = load_json(target, WEAPONS / "weapons.json")["items"]["W124"]
    fit = load_json(STAGE, "fit-check.json")
    runtime = read(target, PROJECT / "plugin/rokugan/RokuganNativeChara.sk").split(
        b"class RokuganNativeFoe extends RokuganNativePicture", 1
    )[1]

    assert {key for key, enemy in enemies.items() if enemy.get("mdlid") == KEY} == ALIASES
    assert all(enemies[key]["name"] == "Shosuro Renegade" for key in ALIASES)
    assert foes[KEY]["human"] and (target / FOE / "EP427.mot").is_file()
    assert all(tag in runtime for tag in (b'person["mask"]', b'person["weaponItem"]', b'person["width"]'))
    assert human[KEY]["base"] == human[DONOR]["base"] == "shared_female"
    assert human[DONOR]["face"] == fit["head"] == FACE
    assert human[KEY]["face"] in ("EP427_face", FACE) and human[KEY]["mask"] in ("EP427_mask", MASK)
    assert b"tex/side_shiko_portrait_face_srgb.png" in descriptor(target, HUMAN, FACE)
    assert hashlib.sha256(read(target, HUMAN / (FACE + ".mdl"))).hexdigest() == fit["head_sha256"]
    assert fit["minimum_clearance"] > .12
    assert weapon["kind"] == "tanto" and b"tex/hunyuan_weapon_tanto_srgb.png" in descriptor(target, WEAPONS, "W124")
    assert ornaments[KEY] == ["sash"]
    descriptor(target, ORNAMENT, "EP427_sash")

    body = descriptor(target, HUMAN, DONOR)
    assert b'modeldata = "shared_female.mdl"' in body
    tones = dict(re.findall(rb'name\s*=\s*"c807060_(\w+)"[\s\S]*?basecol\s*=\s*(0x[0-9a-f]+)', body))
    assert set(tones) == {b"core", b"hands", b"neck", b"throat"} and set(tones.values()) == {b"0xe79474ff"}
    mesh = tailoring[KEY]
    assert mesh["mesh"] == "A120" and mesh["clan"] == "scorpion" and mesh["coverCore"]
    descriptor(target, TAILOR, mesh["mesh"])

    actor = dict(human[KEY], face=FACE, mask=MASK, weaponItem="W124", width=1.10, heightScale=1.0)
    dress = dict(mesh, palette=PALETTE)
    staged = STAGE / "assets"
    mask_path, dye_path = Path("native_human"), Path("native_tailoring/tex/scorpion")
    mask = descriptor(staged, mask_path, MASK)
    assert b'texture0 = "tex/ep427_renegade_noh_color_srgb.png"' in mask
    binary = read(staged, mask_path / (MASK + ".mdl"))
    assert binary.endswith(bytes.fromhex("00000000010004") + b"head" + bytes(9)), "Mask must be rigid on head"
    assets = [
        mask_path / (MASK + ".pm"),
        mask_path / (MASK + ".mdl"),
        mask_path / "tex" / (MASK + "_color_srgb.png"),
        dye_path / (PALETTE + ".png"),
    ]
    return {
        HUMAN / "EP427.pm": body,
        human_file: change_row(read(target, human_file), human[KEY], actor),
        tailoring_file: change_row(read(target, tailoring_file), mesh, dress),
        **{RESOURCE / rel: read(staged, rel) for rel in assets},
    }


def install(target, replacements):
    originals = {rel: (target / rel).read_bytes() if (target / rel).exists() else None for rel in replacements}
    changed = []
    try:
        for rel, content in replacements.items():
            file = target / rel
            if originals[rel] == content:
                continue
            if (file.read_bytes() if file.exists() else None) != originals[rel]:
                raise RuntimeError(f"Concurrent change to {file}")
            changed.append(rel)
            file.write_bytes(content)
            assert file.read_bytes() == content, rel
    except BaseException:
        for rel in reversed(changed):
            file = target / rel
            if originals[rel] is None:
                file.unlink(missing_ok=True)
            else:
                file.write_bytes(originals[rel])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Closed tool directory containing project/")
    parser.add_argument("--check", action="store_true", help="Validate inputs without writing")
    args = parser.parse_args()
    target = args.target.resolve(strict=True)
    changes = plan(target)
    if not args.check:
        install(target, changes)
    print(f"{'Checked' if args.check else 'Installed'} {len(changes)} resources for EP427. "
          "Aliases E227/E561/E951 use the shared female rig, textured Noh mask, crimson A120 and W124.")


if __name__ == "__main__":
    main()
