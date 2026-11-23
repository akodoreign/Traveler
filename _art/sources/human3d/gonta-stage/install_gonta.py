"""Bind the original Gonta bouts to his approved shared-rig actor and profile."""

import argparse
import json
from pathlib import Path
import re


PROJECT = Path("project")
RESOURCE = PROJECT / "resource"
HUMAN = RESOURCE / "native_human"
FOE = RESOURCE / "native_foe"
ORNAMENTS = RESOURCE / "native_ornament"
TAILOR = RESOURCE / "native_tailoring"
CAST = "side_gonta"
FOE_KEY = "EP742"


def data(target, relative):
    return (target / relative).read_bytes()


def table(target, relative):
    return json.loads(data(target, relative))


def native_part(target, folder, name):
    text = data(target, folder / f"{name}.pm")
    refs = re.findall(rb'(?:modeldata|texture[0-9]+)\s*=\s*"([^"]+)"', text)
    assert refs and data(target, folder / refs[0].decode()).startswith(b"SMDL"), name
    assert all((target / folder / ref.decode()).is_file() for ref in refs[1:]), name
    return text


def add_cast_route(raw, key, before):
    """Add one name selector to the foe registration, retaining its existing animation bank."""
    text = raw.decode()
    eol = "\r\n" if "\r\n" in text else "\n"
    key_line = re.search(rf'(?m)^( +)"{key}": \{{\r?$', text)
    assert key_line
    if "castForName" in before:
        assert before["castForName"] == {"Gonta": CAST}
        return raw
    start = key_line.end()
    if text[start - 1] == "\r":
        start -= 1
    indent = key_line[1]
    line = eol + indent * 2 + '"castForName": {' + eol
    line += indent * 3 + f'"Gonta": "{CAST}"' + eol + indent * 2 + "},"
    changed = (text[:start] + line + text[start:]).encode()
    result = json.loads(changed)
    assert result[key] == dict(before, castForName={"Gonta": CAST})
    return changed


def patch_runtime(raw):
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode().replace("\r\n", "\n")
    if 'local castKey = spec["castForName"]' in text:
        return raw
    edits = (
        ('local HUMAN = "/resource/native_human/";',
         'local HUMAN = "/resource/native_human/";\nlocal humanScale = .015 * .75;'),
        ("local baseScale = 0.015 * 0.75 * fieldNpcScale;",
         "local baseScale = humanScale * fieldNpcScale;"),
        ("function setFoe( pc, key, spec, path){", "function setFoe( pc, key, spec, path, castKey=null){"),
        ("""		local person = spec["human"] ? modularPerson( key) : null;
		nativeBody = celNative( SK3DObject( person ? HUMAN .. key .. ".pm" : path));""",
         """		local person = spec["human"] ? modularPerson( key) : null;
		local cast = person && castKey && roster[castKey] ? modularPerson( castKey) : null;
		if( cast && cast.base != person.base) cast = null;
		local bodyKey = cast ? castKey : key;
		nativeBody = celNative( SK3DObject( person ? HUMAN .. bodyKey .. ".pm" : path));"""),
        ("""			local face = HUMAN .. person.face;
			if( nativeHead && person["hatFace"]){""",
         """			local face = HUMAN .. (cast ? cast.face : person.face);
			if( nativeHead && person["hatFace"]){"""),
        ("""		local size = spec.scale * (person ? person["heightScale"] || 1.0 : 1.0);
		nativeBody.scale << Vector3D( size, size, size);""",
         """		local size = spec.scale * (person ? person["heightScale"] || 1.0 : 1.0);
		local proportions = cast ? roster[castKey]["proportions"] : null;
		if( proportions) nativeBody.scale << Vector3D( proportions[0], proportions[1], proportions[2]).scale( humanScale);
		else nativeBody.scale << Vector3D( size, size, size);"""),
        ("""	local model = nativeFoe();
	model.setFoe( pic, key, spec, path .. ".pm");""",
         """	// A shared opponent can keep its own model unless the encounter names the cast member.
	local castKey = spec["castForName"] && data["name"] ? spec.castForName[data.name] : null;
	local model = nativeFoe();
	model.setFoe( pic, key, spec, path .. ".pm", castKey);"""),
    )
    for before, after in edits:
        if text.count(before) != 1:
            raise RuntimeError(f"Expected one runtime anchor: {before.strip()}")
        text = text.replace(before, after, 1)
    return text.replace("\n", eol).encode()


def plan(target):
    humans = table(target, HUMAN / "index.json")
    tailoring = table(target, TAILOR / "index.json")["defaults"]
    roster = table(target, RESOURCE / "native_chara/roster.json")
    pictures = table(target, RESOURCE / "enemy_pic.json")
    players = table(target, PROJECT / "data/player.json")
    enemies = table(target, PROJECT / "data/enemy.json")
    maps = table(target, PROJECT / "data/map.json")
    ornaments = table(target, ORNAMENTS / "index.json")
    file = FOE / "index.json"
    foes = table(target, file)
    row = foes[FOE_KEY]
    assert not any("castForName" in value for key, value in foes.items() if key != FOE_KEY)

    assert players["P125"]["name"] == "Gonta" and players["P125"]["mdlid"] == "EP342"
    assert players["P125"]["equips"] == ["W113", None, None, "A100"]
    assert all(Path(pictures[key]["pic3d"]).stem == CAST for key in ("EP342", FOE_KEY))
    assert {key for key, enemy in enemies.items() if enemy.get("mdlid") == FOE_KEY} == {"E120", "E121"}
    assert enemies["E120"]["name"] == "Gonta" and enemies["E121"]["name"] == "Wrestler"
    assert all(maps["M104"]["event"][key]["mdlid"] == "EP342" for key in ("#4#", "#15#"))
    assert maps["M104"]["event"]["#7#"]["mdlid"] == "EP345"
    assert maps["M170"]["event"]["#6#"]["mdlid"] == "EP342"
    bout = next(x for x in maps["M001"]["encount"] if x["gid"] == 6)
    assert bout["mapid"] == "M812" and [entry["id"] for entry in bout["enemies"]] == ["E120"]
    field = data(target, PROJECT / "plugin/rokugan/RokuganField.sk")
    assert b'["EP342"] = "EP742"' in field

    assert row["human"] and (target / FOE / "EP742.mot").is_file()
    person, cast = humans[FOE_KEY], humans[CAST]
    assert person["base"] == cast["base"] == "shared_male"
    assert cast["face"] == "side_gonta_portrait_face"
    assert not any(person.get(key) for key in ("hat", "hatItem", "hatFace", "mask", "weapon", "weaponItem"))
    assert b"tex/side_gonta_portrait_face_srgb.png" in native_part(target, HUMAN, cast["face"])
    assert "side_gontaboy" in humans and humans["side_gontaboy"]["face"] != cast["face"]
    skin_pm = native_part(target, HUMAN, CAST)
    assert b'modeldata = "shared_male.mdl"' in skin_pm
    colors = dict(re.findall(rb'name\s*=\s*"c807060_(\w+)"[\s\S]*?basecol\s*=\s*(0x[0-9a-f]+)', skin_pm))
    assert set(colors) == {b"core", b"neck", b"throat", b"hands"} and set(colors.values()) == {b"0xd95b24ff"}
    assert tailoring[FOE_KEY] == tailoring[CAST] and tailoring[CAST]["mesh"] == "A108"
    native_part(target, TAILOR, "A108")
    native_part(target, TAILOR, "A108_decal")
    assert (target / TAILOR / "tex/ronin/A108.png").is_file()
    assert (target / RESOURCE / "native_gear/decal/ronin/A108.png").is_file()
    assert ornaments[FOE_KEY] == ornaments[CAST] == ["sash"]
    native_part(target, ORNAMENTS, FOE_KEY + "_sash")

    assert roster[CAST]["proportions"] == [1.355, 1.09, 1.37] and roster[CAST]["weapon"] == "none"
    gonta, yosai, hiruma = (roster[a]["proportions"] for a in (CAST, "side_yosai", "trav_natsuko"))
    assert yosai[1] > hiruma[1] > gonta[1]
    assert all(gonta[axis] > yosai[axis] > hiruma[axis] for axis in (0, 2))

    runtime = PROJECT / "plugin/rokugan/RokuganNativeChara.sk"
    return {file: add_cast_route(data(target, file), FOE_KEY, row),
            runtime: patch_runtime(data(target, runtime))}


def install(target, changes):
    originals = {rel: data(target, rel) for rel in changes}
    changed = []
    try:
        for rel, new in changes.items():
            if originals[rel] == new:
                continue
            if data(target, rel) != originals[rel]:
                raise RuntimeError(f"Concurrent change to {target / rel}")
            changed.append(rel)
            (target / rel).write_bytes(new)
            assert data(target, rel) == new, rel
    except BaseException:
        for rel in reversed(changed):
            (target / rel).write_bytes(originals[rel])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Closed tool directory containing project/")
    parser.add_argument("--check", action="store_true", help="Verify references without writing")
    args = parser.parse_args()
    target = args.target.resolve(strict=True)
    changes = plan(target)
    if not args.check:
        install(target, changes)
    print(f"{'Checked' if args.check else 'Installed'} two resources for adult Gonta. "
          "EP742 uses side_gonta when the opponent is Gonta.")


if __name__ == "__main__":
    main()
