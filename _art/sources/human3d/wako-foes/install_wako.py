"""Install the staged foe fits into one closed RPG-Cobo tool or test profile."""

import argparse
import json
from pathlib import Path
import re


STAGE = Path(__file__).resolve().parent
PARENT = Path("project/resource")
NATIVE = Path("project/plugin/rokugan/RokuganNativeChara.sk")

HAT_OLD = '''		if( person["hat"] && ClientConfig.showHeadwear()) nativeHead = addNativePart( HUMAN .. person.hat);'''
HAT_NEW = '''		if( ClientConfig.showHeadwear()){
				local fittedHat = tailored( "items", person["hatItem"]);
				if( fittedHat) nativeHead = addTailoredPart( fittedHat, costume ? costume["clan"] || "ronin" : "ronin");
				else if( person["hat"]) nativeHead = addNativePart( HUMAN .. person.hat);
			}'''
WEAPON_OLD = '''			if( person["weapon"]) nativeWeapon = addNativePart( HUMAN .. person.weapon);'''
WEAPON_NEW = '''			local fittedWeapon = person["weaponItem"];
			if( fittedWeapon && ::getResource( ARMS .. fittedWeapon .. ".pm") && ::getResource( ARMS .. fittedWeapon .. ".mdl"))
				nativeWeapon = addNativePart( ARMS .. fittedWeapon);
			else if( person["weapon"]) nativeWeapon = addNativePart( HUMAN .. person.weapon);'''
SCALE_OLD = '''		local size = spec.scale;
		nativeBody.scale << Vector3D( size, size, size);'''
SCALE_NEW = '''		local size = spec.scale * (person ? person["heightScale"] || 1.0 : 1.0);
		nativeBody.scale << Vector3D( size, size, size);
		if( person && person["width"]) setTravelerWidth( person.width);'''


def patched_script(raw):
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf8").replace("\r\n", "\n")
    assert text.count("class RokuganNativeFoe extends RokuganNativePicture") == 1
    pos = text.index("class RokuganNativeFoe extends RokuganNativePicture")
    before, foe = text[:pos], text[pos:]
    for original, updated in ((HAT_OLD, HAT_NEW), (WEAPON_OLD, WEAPON_NEW), (SCALE_OLD, SCALE_NEW)):
        if updated in foe:
            continue
        if foe.count(original) != 1:
            raise RuntimeError(f"Expected one foe runtime anchor: {original.strip()}")
        foe = foe.replace(original, updated)
    return (before + foe).replace("\n", eol).encode("utf8")


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf8")


def inputs(target):
    fits = json.loads((STAGE / "wako-fits.json").read_bytes())
    hfile = PARENT / "native_human/index.json"
    tfile = PARENT / "native_tailoring/index.json"
    human = json.loads((target / hfile).read_bytes())
    tailoring = json.loads((target / tfile).read_bytes())
    assert json.loads((target / "project/data/enemy.json").read_bytes())["E539"]["mdlid"] == "EP417"
    for key, fit in fits.items():
        assert human[fit["donor"]]["base"] == human[key]["base"] == fit["human"]["base"]
        assert human[fit["donor"]]["face"] == fit["human"]["face"]
        # Keep any metadata added independently after this fit was prepared.
        human[key].update(fit["human"])
        tailoring["defaults"][key] = fit["tailoring"]
    replacements = {hfile: json_bytes(human), tfile: json_bytes(tailoring)}
    replacements[NATIVE] = patched_script((target / NATIVE).read_bytes())
    for file in (STAGE / PARENT).rglob("*"):
        if file.is_file() and file.suffix in (".pm", ".mdl", ".png"):
            replacements[file.relative_to(STAGE)] = file.read_bytes()
    required = {PARENT / f"native_human/{key}.pm" for key in fits}
    required.update(PARENT / f"native_human/ep417_wako_nodachi.{ext}" for ext in ("pm", "mdl"))
    required.add(PARENT / "native_tailoring/tex/ronin/wako_slate.png")
    if not required.issubset(replacements):
        raise RuntimeError(f"Incomplete staged files: {sorted(str(p) for p in required - replacements.keys())}")
    bladekey = PARENT / "native_human/ep417_wako_nodachi"
    assert replacements[bladekey.with_suffix(".mdl")][:4] == b"SMDL"
    assert replacements[bladekey.with_suffix(".pm")].decode().count("texture0 = \"tex/") >= 2
    for match in re.findall(r'texture0 = "(tex/[^"]+)"', replacements[bladekey.with_suffix(".pm")].decode()):
        assert (bladekey.parent / match) in replacements, match
    for fit in fits.values():
        variant = fit["human"]
        for field in ("face", "hat", "mask", "weapon"):
            if variant.get(field):
                for ext in ("pm", "mdl"):
                    file = PARENT / f"native_human/{variant[field]}.{ext}"
                    assert file in replacements or (target / file).is_file(), file
        if variant.get("weaponItem"):
            for ext in ("pm", "mdl"):
                assert (target / PARENT / f"native_weapons/{variant['weaponItem']}.{ext}").is_file()
        garment = fit["tailoring"]
        assert (target / PARENT / f"native_tailoring/{garment['mesh']}.mdl").is_file()
        dye = PARENT / f"native_tailoring/tex/{garment['clan']}/{garment.get('palette', garment['mesh'])}.png"
        assert dye in replacements or (target / dye).is_file(), dye
    return replacements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="The tool directory containing project/ and rpgcobo.exe")
    parser.add_argument("--check", action="store_true", help="Verify the plan without writing the target")
    args = parser.parse_args()
    target = args.target.resolve(strict=True)
    assert (target / "rpgcobo.exe").is_file()
    replacements = inputs(target)
    if not args.check:
        prior = {rel: (target / rel).read_bytes() for rel in replacements if (target / rel).is_file()}
        changed = []
        try:
            for rel, content in replacements.items():
                path = target / rel
                if prior.get(rel) == content:
                    continue
                if path.is_file() and path.read_bytes() != prior.get(rel):
                    raise RuntimeError(f"Concurrent change to {path}")
                path.parent.mkdir(exist_ok=True, parents=True)
                changed.append(rel)
                path.write_bytes(content)
                assert path.read_bytes() == content
        except BaseException:
            for rel in reversed(changed):
                if rel in prior:
                    (target / rel).write_bytes(prior[rel])
                else:
                    (target / rel).unlink(missing_ok=True)
            raise
    print(f"{'Checked' if args.check else 'Installed'} {len(replacements)} files for five shared-rig human foes.")


if __name__ == "__main__":
    main()
