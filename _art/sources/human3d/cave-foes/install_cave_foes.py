"""Install regenerated visual fits for the cave-route human foes."""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re


RESOURCE = Path("project/resource")
HUMAN = RESOURCE / "native_human"
TAILOR = RESOURCE / "native_tailoring"
WEAPONS = RESOURCE / "native_weapons"
CREATURE = RESOURCE / "native_foe"


@dataclass(frozen=True)
class Fit:
    donor: str
    outfit: str
    clan: str
    weapon: str
    kind: str
    width: float
    height: float
    hat_item: str = ""
    helmet_face: bool = False
    mask: str = ""


FITS = {
    # Visually reported or recorded in the cave-route previews.
    "EP413": Fit("side_seppunguard", "A116", "ronin", "W104", "yumi", 1.07, 1.00, hat_item="A102"),
    "EP414": Fit("side_h_yari", "A141", "ronin", "W101", "yari", 1.09, 1.04, helmet_face=True),
    "EP411": Fit("side_lionsergeant", "A109", "scorpion", "W110", "katana", 1.14, 1.07, helmet_face=True),
    "EP405": Fit("side_h_yojimbo", "A111", "ronin", "W100", "katana", 1.05, 1.02),
    "EP426": Fit("side_bayushiguard", "A127", "ronin", "W102", "tanto", 1.02, 1.00,
                 mask="side_bayushiguard_portrait_charcoal_cloth"),
    "EP415": Fit("side_sergeant", "A112", "crab", "W103", "tetsubo", 1.20, 1.11, helmet_face=True),
    # Nearby maps in the same route branch.
    "EP400": Fit("side_ff_boatman", "A100", "ronin", "W100", "katana", 1.04, 0.98),
    "EP401": Fit("side_ferryman", "A127", "peasant", "W114", "yumi", 1.09, 1.01),
    "EP402": Fit("side_yosuke", "A101", "ronin", "W161", "naginata", 1.13, 1.06),
    "EP409": Fit("side_soshiofficer", "A109", "scorpion", "W100", "katana", 1.10, 1.05),
    "EP416": Fit("side_drunksailor", "A127", "ronin", "W146", "kama", 1.11, 1.02),
    "EP425": Fit("side_bayushiguard", "A127", "scorpion", "W124", "tanto", 1.03, 0.98,
                 mask="side_bayushiguard_portrait_charcoal_cloth"),
    "EP427": Fit("side_shiko", "A120", "scorpion", "W124", "tanto", 1.04, 1.00),
    "EP115": Fit("side_drunksailor", "A111", "peasant", "W121", "katana", 1.13, 1.00),
    "EP2603": Fit("side_h_fisherman", "A100", "peasant", "W101", "yari", 1.01, 0.97),
    "EP2611": Fit("side_yosuke", "A141", "ronin", "ep417_wako_nodachi", "nodachi", 1.19, 1.10),
    "EP2613": Fit("side_uyojimbo", "A101", "ronin", "W139", "katana", 1.08, 1.03),
    "EP2623": Fit("side_bayushiguard", "A127", "scorpion", "W139", "katana", 1.07, 1.03,
                  mask="side_bayushiguard_portrait_charcoal_cloth"),
}
PRIORITY = tuple(FITS)[:6]
BODY_SKIN = {"core", "hands", "neck", "throat"}
REFERENCES = re.compile(r'(?:modeldata|texture[0-9]+)\s*=\s*"([^"]+)"')


def read(target, rel):
    return (target / rel).read_bytes()


def load_json(target, rel):
    return json.loads(read(target, rel))


def json_bytes(data, original):
    indent_line = re.search(rb"\n( +)\S", original)
    indent = len(indent_line[1]) if indent_line else 2
    line_ending = "\r\n" if b"\r\n" in original else "\n"
    return (json.dumps(data, ensure_ascii=False, indent=indent) + "\n").replace("\n", line_ending).encode()


def descriptor(target, folder, name):
    raw = read(target, folder / f"{name}.pm").decode()
    references = REFERENCES.findall(raw)
    assert references and references[0].endswith(".mdl"), name
    assert read(target, folder / references[0]).startswith(b"SMDL"), name
    for texture in references[1:]:
        assert (target / folder / texture).is_file(), (name, texture)
    return raw


def expect_skin(body, face):
    tones = dict(re.findall(r'name\s*=\s*"c807060_(\w+)"[\s\S]*?basecol\s*=\s*(0x[0-9a-f]+)', body))
    assert set(tones) == BODY_SKIN and len(set(tones.values())) == 1, (face, tones)
    return tones["neck"]


def plan(target, fits):
    runtime = read(target, Path("project/plugin/rokugan/RokuganNativeChara.sk")).decode().split(
        "class RokuganNativeFoe extends RokuganNativePicture", 1
    )[1]
    assert all(f'person["{slot}"]' in runtime for slot in ("hatItem", "hatFace", "weaponItem", "heightScale", "width"))
    human_file = HUMAN / "index.json"
    clothes_file = TAILOR / "index.json"
    human = load_json(target, human_file)
    tailoring = load_json(target, clothes_file)
    native_foes = load_json(target, CREATURE / "index.json")
    enemies = load_json(target, Path("project/data/enemy.json"))
    weapons = load_json(target, WEAPONS / "weapons.json")["items"]
    for eid, ep in {"E651": "EP413", "E738": "EP411", "E741": "EP414",
                    "E728": "EP405", "E949": "EP426", "E737": "EP415"}.items():
        assert enemies[eid]["mdlid"] == ep, eid
    for eid in ("E035", "E926"):
        ep = enemies[eid]["mdlid"]
        assert not native_foes[ep].get("human"), (eid, ep)
        descriptor(target, CREATURE, ep)
        assert (target / CREATURE / f"{ep}.mot").is_file(), ep

    replacements = {}
    for key, fit in fits.items():
        person, donor = human[key], human[fit.donor]
        assert native_foes[key]["human"] and (target / CREATURE / f"{key}.mot").is_file(), key
        face = donor["face"]
        assert person["base"] == donor["base"] and person["face"] in (f"{key}_face", face), (key, person)
        assert re.search(r'texture0\s*=\s*"tex/[^"]+_srgb.png"', descriptor(target, HUMAN, face)), face
        body = descriptor(target, HUMAN, fit.donor)
        assert f'modeldata = "{person["base"]}.mdl"' in body, key
        skin = expect_skin(body, face)
        replacements[HUMAN / f"{key}.pm"] = read(target, HUMAN / f"{fit.donor}.pm")
        person.update(face=face, width=fit.width, heightScale=fit.height)
        if fit.weapon in weapons:
            assert weapons[fit.weapon]["kind"] == fit.kind, (key, fit.weapon, weapons[fit.weapon])
            person["weaponItem"] = fit.weapon
            weapon_folder = WEAPONS
        else:
            assert fit.weapon == "ep417_wako_nodachi" and fit.kind == "nodachi", key
            person.pop("weaponItem", None)
            person["weapon"] = fit.weapon
            weapon_folder = HUMAN
        weapon_pm = descriptor(target, weapon_folder, fit.weapon)
        # Current tetsubos are the fitted native material variants.
        assert fit.kind == "tetsubo" or re.search(r'texture0\s*=\s*"tex/', weapon_pm), fit.weapon

        if fit.hat_item:
            hat = tailoring["items"][fit.hat_item]
            descriptor(target, TAILOR, hat["mesh"])
            assert (target / TAILOR / f'tex/{fit.clan}/{hat["mesh"]}.png').is_file(), hat
            person["hatItem"] = fit.hat_item
        elif person.get("hat"):
            descriptor(target, HUMAN, person["hat"])
        if fit.helmet_face:
            # The regenerated heads fit the established shells. Drop the old
            # flat-color helmet-only head so the same fitted portrait shows.
            assert person["hat"].endswith("_hunyuan_kabuto_cords"), key
            person.pop("hatFace", None)
        else:
            assert "hatFace" not in person, key
        if fit.mask:
            person["mask"] = fit.mask
        if person.get("mask"):
            descriptor(target, HUMAN, person["mask"])

        outfit = tailoring["items"][fit.outfit].copy()
        outfit.pop("decal", None)
        outfit["clan"] = fit.clan
        descriptor(target, TAILOR, outfit["mesh"])
        assert (target / TAILOR / f'tex/{fit.clan}/{outfit["mesh"]}.png').is_file(), (key, outfit)
        tailoring["defaults"][key] = outfit
        print(f"{key} {face} {skin} {fit.outfit}/{fit.clan} {fit.weapon} width {fit.width:.2f}")

    replacements[human_file] = json_bytes(human, read(target, human_file))
    replacements[clothes_file] = json_bytes(tailoring, read(target, clothes_file))
    return replacements


def install(target, replacements):
    previous = {rel: read(target, rel) if (target / rel).exists() else None for rel in replacements}
    changed = []
    try:
        for rel, content in replacements.items():
            path = target / rel
            if previous[rel] == content:
                continue
            if (path.read_bytes() if path.exists() else None) != previous[rel]:
                raise RuntimeError(f"Concurrent change to {path}")
            changed.append(rel)
            path.write_bytes(content)
            assert path.read_bytes() == content, path
    except BaseException:
        for rel in reversed(changed):
            path = target / rel
            if previous[rel] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(previous[rel])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Directory containing project/")
    parser.add_argument("--check", action="store_true", help="Verify all inputs without writing")
    parser.add_argument("--priority", action="store_true", help="Select the six previewed families")
    args = parser.parse_args()
    fits = {key: FITS[key] for key in PRIORITY} if args.priority else FITS
    replacements = plan(args.target.resolve(strict=True), fits)
    if not args.check:
        install(args.target, replacements)
    print(f"{'Checked' if args.check else 'Installed'} {len(fits)} humanoid fits across {len(replacements)} resources.")


if __name__ == "__main__":
    main()
