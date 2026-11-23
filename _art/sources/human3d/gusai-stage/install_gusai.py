"""Use Akodo Gusai's approved regenerated face and Lion fit in both duels."""

import argparse
import json
from pathlib import Path
import re


PROJECT = Path("project")
RESOURCE = PROJECT / "resource"
HUMAN = RESOURCE / "native_human"
TAILOR = RESOURCE / "native_tailoring"
FOE = RESOURCE / "native_foe"
ARMS = RESOURCE / "native_weapons"
ORNAMENTS = RESOURCE / "native_ornament"
FIELD = "side_gusai"
DUEL = "EP834"
FACE = "side_gusai_portrait_face"


def read(target, rel):
    return (target / rel).read_bytes()


def pm(target, folder, key):
    raw = read(target, folder / (key + ".pm"))
    model = re.search(rb'modeldata\s*=\s*"([^"]+)"', raw)[1].decode()
    assert model.endswith(".mdl") and read(target, folder / model).startswith(b"SMDL"), key
    for texture in re.findall(rb'texture[0-9]+\s*=\s*"([^"]+)"', raw):
        assert (target / folder / texture.decode()).is_file(), (key, texture)
    return raw


def change_row(raw, row, before, after):
    """Replace one indented manifest row and preserve the rest of the file."""
    text = raw.decode("utf-8")
    match = re.search(
        rf'(?m)^( +)"{row}": \{{\r?\n(?:(?!^\1\}})[\s\S])*^\1\}}(?=,|\r?$)',
        text,
    )
    assert match and json.loads(match[0].split(":", 1)[1]) == before, row
    prefix = match[1]
    indent = min(len(prefix), 2)
    eol = "\r\n" if "\r\n" in match[0] else "\n"
    value = json.dumps(after, ensure_ascii=False, indent=indent).splitlines()
    replacement = prefix + f'"{row}": ' + value[0] + eol
    replacement += eol.join(prefix + line for line in value[1:])
    return (text[:match.start()] + replacement + text[match.end():]).encode("utf-8")


def build(target):
    human_file = HUMAN / "index.json"
    clothes_file = TAILOR / "index.json"
    raw_humans = read(target, human_file)
    raw_clothes = read(target, clothes_file)
    humans = json.loads(raw_humans)
    clothes = json.loads(raw_clothes)["defaults"]
    players = json.loads(read(target, PROJECT / "data/player.json"))
    enemies = json.loads(read(target, PROJECT / "data/enemy.json"))
    foe_bank = json.loads(read(target, FOE / "index.json"))
    roster = json.loads(read(target, RESOURCE / "native_chara/roster.json"))
    pic = json.loads(read(target, RESOURCE / "enemy_pic.json"))
    ornaments = json.loads(read(target, ORNAMENTS / "index.json"))
    runtime = read(target, PROJECT / "plugin/rokugan/RokuganNativeChara.sk")
    foe_runtime = runtime.split(b"class RokuganNativeFoe extends RokuganNativePicture", 1)[1]

    assert players["P127"]["mdlid"] == "EP554" and players["P127"]["equips"][0] == "W100"
    assert Path(pic["EP554"]["pic3d"]).stem == FIELD
    assert all(enemies[key]["mdlid"] == DUEL for key in ("E351", "E389"))
    assert foe_bank[DUEL]["human"] and (target / FOE / "EP834.mot").is_file()
    assert all(piece in foe_runtime for piece in (b'person["weaponItem"]', b'person["heightScale"]', b'person["width"]'))
    assert humans[FIELD]["base"] == humans[DUEL]["base"] == "shared_male"
    assert humans[FIELD]["face"] == FACE and humans[DUEL]["face"] in ("EP834_face", FACE)
    assert not any(humans[DUEL].get(key) for key in ("hat", "hatItem", "hatFace", "mask"))
    assert b"tex/side_gusai_portrait_face_srgb.png" in pm(target, HUMAN, FACE)
    assert ornaments[DUEL] == ["sash"] and ornaments[FIELD] == ["sash"]
    pm(target, ORNAMENTS, "EP834_sash")

    body = pm(target, HUMAN, FIELD)
    assert b'modeldata = "shared_male.mdl"' in body
    skin = dict(re.findall(
        rb'name\s*=\s*"c807060_(\w+)"[\s\S]*?basecol\s*=\s*(0x[0-9a-f]+)', body
    ))
    assert set(skin) == {b"core", b"neck", b"throat", b"hands"}
    assert set(skin.values()) == {b"0x8f4727ff"}
    assert b"tex/hunyuan_weapon_katana_srgb.png" in pm(target, ARMS, "W100")

    fit = clothes[FIELD]
    assert fit["mesh"] == "A135_lion_takeo" and fit["clan"] == "lion"
    assert fit["palette"] == "A135" and fit["decal"] == "A135" and fit["coverCore"]
    pm(target, TAILOR, fit["mesh"])
    pm(target, TAILOR, fit["mesh"] + "_decal")
    assert (target / TAILOR / "tex/lion/A135.png").is_file()
    assert (target / RESOURCE / "native_gear/decal/lion/A135.png").is_file()

    x, height, z = roster[FIELD]["proportions"]
    updated = dict(humans[DUEL], face=FACE, weaponItem="W100",
                   width=round((x * z) ** 0.5, 3), heightScale=height)
    return {
        HUMAN / "EP834.pm": body,
        human_file: change_row(raw_humans, DUEL, humans[DUEL], updated),
        clothes_file: change_row(raw_clothes, DUEL, clothes[DUEL], fit),
    }


def install(target, replacements):
    previous = {rel: read(target, rel) for rel in replacements}
    changed = []
    try:
        for rel, content in replacements.items():
            if content == previous[rel]:
                continue
            if read(target, rel) != previous[rel]:
                raise RuntimeError(f"Concurrent change to {target / rel}")
            changed.append(rel)
            (target / rel).write_bytes(content)
            assert read(target, rel) == content, rel
    except BaseException:
        for rel in reversed(changed):
            (target / rel).write_bytes(previous[rel])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Closed tool profile containing project/")
    parser.add_argument("--check", action="store_true", help="Validate without changing the target")
    args = parser.parse_args()
    target = args.target.resolve(strict=True)
    replacements = build(target)
    if not args.check:
        install(target, replacements)
    print(f"{'Checked' if args.check else 'Installed'} EP834 in {len(replacements)} resources. "
          "E351 and E389 use side_gusai_portrait_face, A135_lion_takeo and W100.")


if __name__ == "__main__":
    main()
