"""Install the regenerated servant fit for the field and battle Maho Puppet."""

import argparse
import json
from pathlib import Path
import re


PROJECT = Path("project")
RESOURCE = PROJECT / "resource"
HUMAN = RESOURCE / "native_human"
TAILOR = RESOURCE / "native_tailoring"
FOES = RESOURCE / "native_foe"
ORNAMENTS = RESOURCE / "native_ornament"
KEY = "EP429"
DONOR = "side_servant"
FACE = "ep429_puppet_portrait_face"
CAP = "side_servant_headcloth"
DYE = "A100_crab_3"
SOURCE_SKIN = (242, 197, 164)
PUPPET_SKIN = (216, 193, 162)
SKIN_MATERIAL = rb'(name\s*=\s*"c807060_(core|hands|neck|throat)"[\s\S]*?basecol\s*=\s*)0x([a-f0-9]{8})'


def read(target, relative):
    return (target / relative).read_bytes()


def load_json(target, path):
    return json.loads(read(target, path))


def descriptor(target, folder, name):
    text = read(target, folder / (name + ".pm"))
    resources = re.findall(rb'(?:modeldata|texture[0-9]+)\s*=\s*"([^"]+)"', text)
    assert resources and read(target, folder / resources[0].decode()).startswith(b"SMDL"), name
    for path in resources[1:]:
        assert (target / folder / path.decode()).is_file(), (name, path)
    return text


def replace_row(raw, before, after):
    text = raw.decode()
    pattern = rf'(?m)^( +)"{KEY}": \{{\r?\n(?:(?!^\1\}})[\s\S])*^\1\}}(?=,|\r?$)'
    match = re.search(pattern, text)
    assert match and json.loads(match[0].split(":", 1)[1]) == before
    indent = match[1]
    eol = "\r\n" if "\r\n" in match[0] else "\n"
    rows = json.dumps(after, indent=min(len(indent), 2)).splitlines()
    replacement = indent + f'"{KEY}": ' + rows[0] + eol
    replacement += eol.join(indent + row for row in rows[1:])
    return (text[:match.start()] + replacement + text[match.end():]).encode()


def skin_fit(target, human):
    face = human[DONOR]["face"]
    assert face == DONOR + "_portrait_face"
    portrait = descriptor(target, HUMAN, face)
    assert f"tex/{face}_srgb.png".encode() in portrait
    tint = tuple(round(255 * (goal / old)**2.2) for old, goal in zip(SOURCE_SKIN, PUPPET_SKIN))
    source_body = descriptor(target, HUMAN, DONOR)
    assert b'modeldata = "shared_male.mdl"' in source_body
    tones = dict(re.findall(rb'name\s*=\s*"c807060_(\w+)"[\s\S]*?basecol\s*=\s*(0x[0-9a-f]+)', source_body))
    assert set(tones) == {b"core", b"hands", b"neck", b"throat"} and set(tones.values()) == {b"0xe39161ff"}
    body_color = tuple(round(donor * shade / 255) for donor, shade in zip((0xE3, 0x91, 0x61), tint))
    body_hex = (bytes(body_color).hex() + "ff").encode()
    body, groups = re.subn(SKIN_MATERIAL, lambda m: m[1] + b"0x" + body_hex, source_body)
    assert groups == 4 and b"basecol = 0xd7cfbbff" in body
    assert portrait.count(b"basecol = 0xffffffff") == 1
    portrait = portrait.replace(b"basecol = 0xffffffff", b"basecol = 0x" + (bytes(tint).hex() + "ff").encode())
    model_key = f'"{face}.mdl"'.encode()
    assert portrait.count(model_key) == 1
    print(f"Diffuse sample {SOURCE_SKIN}, pallor target {PUPPET_SKIN}, face tint 0x{bytes(tint).hex()}ff, body 0x{body_hex.decode()}.")
    return {HUMAN / (KEY + ".pm"): body,
            HUMAN / (FACE + ".pm"): portrait.replace(model_key, f'"{FACE}.mdl"'.encode()),
            HUMAN / (FACE + ".mdl"): read(target, HUMAN / (face + ".mdl"))}


def plan(target):
    human_file, tailor_file = HUMAN / "index.json", TAILOR / "index.json"
    human = load_json(target, human_file)
    tailor = load_json(target, tailor_file)["defaults"]
    enemies = load_json(target, PROJECT / "data/enemy.json")
    maps = load_json(target, PROJECT / "data/map.json")
    foes = load_json(target, FOES / "index.json")
    ornaments = load_json(target, ORNAMENTS / "index.json")
    actor = human[KEY]
    assert {key for key, foe in enemies.items() if foe.get("mdlid") == KEY} == {"E235"}
    assert enemies["E235"]["name"] == "Maho Puppet" and enemies["E234"]["mdlid"] == "EP121"
    assert enemies["E234"]["name"] == "Troll" and not foes["EP121"].get("human")
    assert b"ep121_hunyuan_color_srgb.png" in descriptor(target, FOES, "EP121")
    assert maps["M150"]["event"]["#3#"]["mdlid"] == KEY
    duel = next(group for group in maps["M001"]["encount"] if group["gid"] == 14)
    assert duel["mapid"] == "M815" and [row["id"] for row in duel["enemies"]] == ["E235", "E234"]
    look = read(target, PROJECT / "plugin/rokugan/RokuganLook.sk")
    assert b"::Rokugan.createFieldHumanoidFoe( data)" in look
    assert foes[KEY]["human"] and (target / FOES / (KEY + ".mot")).is_file()
    assert {"stand", "walk", "fight", "spell", "punch1"}.issubset({row["id"] for row in foes[KEY]["animap"]})

    donor = human[DONOR]
    assert actor["base"] == donor["base"] == "shared_male"
    assert actor["face"] in ("EP429_face", FACE) and actor["hat"] in ("EP429_hat", CAP)
    assert CAP in {value["mesh"] for value in donor["portraitAccessories"] if value.get("headwear")}
    assert b"side_servant_headcloth_weave.png" in descriptor(target, HUMAN, CAP)
    assert not any(actor.get(key) for key in ("weapon", "weaponItem", "hatItem", "hatFace", "mask"))
    assert ornaments[KEY] == ["sash"]
    descriptor(target, ORNAMENTS, KEY + "_sash")
    costume = tailor[KEY]
    assert costume["mesh"] == "A100" and costume["coverCore"]
    descriptor(target, TAILOR, "A100")
    assert (target / TAILOR / f"tex/peasant/{DYE}.png").is_file()
    fitted = dict(actor, face=FACE, hat=CAP, width=1.035)
    wardrobe = dict(costume, clan="peasant", palette=DYE)
    wardrobe.pop("decal", None)
    return {**skin_fit(target, human),
            human_file: replace_row(read(target, human_file), actor, fitted),
            tailor_file: replace_row(read(target, tailor_file), costume, wardrobe)}


def install(target, changes):
    original = {rel: (target / rel).read_bytes() if (target / rel).exists() else None for rel in changes}
    written = []
    try:
        for rel, content in changes.items():
            file = target / rel
            if original[rel] == content:
                continue
            if (file.read_bytes() if file.exists() else None) != original[rel]:
                raise RuntimeError(f"Concurrent change to {file}")
            written.append(rel)
            file.write_bytes(content)
            assert file.read_bytes() == content, rel
    except BaseException:
        for rel in reversed(written):
            file = target / rel
            if original[rel] is None:
                file.unlink(missing_ok=True)
            else:
                file.write_bytes(original[rel])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Closed RPG-Cobo profile containing project/")
    parser.add_argument("--check", action="store_true", help="Verify without changing the target")
    args = parser.parse_args()
    target = args.target.resolve(strict=True)
    changes = plan(target)
    if not args.check:
        install(target, changes)
    print(f"{'Checked' if args.check else 'Installed'} {len(changes)} resources for Maho Puppet E235/EP429.")


if __name__ == "__main__":
    main()
