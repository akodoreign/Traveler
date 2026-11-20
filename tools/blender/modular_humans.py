"""Stage separate bodies and portrait-informed heads for the native human rig.

Run in Blender with --python modular_humans.py -- JOB.json.
"""
import json
from pathlib import Path
import re
import shutil
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c
from chara3d_native import save_piece
from foe_batch import costume
from head_surfaces import CLOTH_PATTERNS, HeadSurface, make_textures


BODY_SKIN = (128, 112, 96)
SKIN_MATERIAL = "c%02x%02x%02x" % BODY_SKIN
SKIN_TONE_FILE = Path(__file__).resolve().parents[2] / "_art/sources/human3d/skin_tones.json"
PORTRAIT_SKIN_TONES = json.loads(SKIN_TONE_FILE.read_text("utf8")) if SKIN_TONE_FILE.is_file() else {}


def tint_body(template, color):
    """Apply one portrait-matched skin tone to all the shared body's skin sections."""
    linear = [round((value / 255) ** 2.2 * 255) for value in color]
    tinted = "0x%02x%02x%02xff" % tuple(linear)
    marker = rf'(?m)(^\t\tname = "{SKIN_MATERIAL}(?:_(?:core|hands|neck|throat))?"\n(?:[^\n]*\n)*?^\t\tbasecol = )0x[0-9a-f]+'
    result, count = re.subn(marker, lambda match: match[1] + tinted, template)
    if count not in (1, 3, 4):
        raise ValueError("Shared body has missing skin materials")
    return result


def save_actor_head(out, scene, rig, spec, name, detail):
    geometry = c.Skin(spec)
    c.face(geometry, spec)
    c.hair(geometry, spec)
    save_piece(scene, out, rig, name, geometry,
               surface=detail if any(geometry.surfaces) else None, eye_spec=spec)


def save_foe(out, scene, rig, key, entry, person, detail):
    spec = entry["spec"]
    if spec.get("head") in ("kabuto", "kabuto_full"):
        spec["iron_cap"] = True
        spec.setdefault("armor", spec.get("helm", (75, 74, 80)))
    if spec.get("head") == "headcloth":
        spec.update(head="hachimaki", band=spec.get("cloth", spec["accent"]))

    face = key + "_face"
    save_actor_head(out, scene, rig, spec, face, detail)
    person["face"] = face

    def save_part(role, geometry):
        if geometry.faces:
            name = f"{key}_{role}"
            save_piece(scene, out, rig, name, geometry, surface=detail if any(geometry.surfaces) else None)
            person[role] = name

    armor = c.Skin(spec)
    build = spec.get("build", "normal")
    style = "armored" if build.startswith("armored") or build == "heavy" else "robe"
    for layer in c.OUTFITS[style]:
        if layer is not c.helmet:
            layer(armor, spec)
    costume(c, armor, spec | {"hat": None})
    save_part("outfit", armor)

    hat = c.Skin(spec)
    if style == "armored":
        c.helmet(hat, spec)
    if spec.get("head") == "hachimaki":
        c.headband(hat, spec)
    costume(c, hat, spec | {"sashimono": None})
    save_part("hat", hat)
    if spec.get("mask"):
        mask = c.Skin(spec)
        c.signature_mask(mask, spec)
        save_part("mask", mask)
    weapon = c.Skin(spec)
    c.weapon(weapon, spec, spec.get("weapon", "none"))
    save_part("weapon", weapon)


def export(out, roster, foes, body_pack):
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    rig = c.make_armature(c.rest_frames())
    roles = {"hair", "linen"}
    if foes:
        roles.update(("iron", "cloth"))
        roles.update(i["spec"].get("pattern") for i in foes.values() if i["spec"].get("pattern") in CLOTH_PATTERNS)
    detail = HeadSurface(make_textures(out / "tex", roles))
    templates = {}
    for female in (False, True):
        name = "shared_female" if female else "shared_male"
        if body_pack:
            source = Path(body_pack)
            shutil.copyfile(source / f"{name}.mdl", out / f"{name}.mdl")
            template = (source / f"{name}.pm").read_text(encoding="utf8")
        else:
            spec = {"female": female, "skin": BODY_SKIN, "build": "normal"}
            geometry = c.Skin(spec)
            c.body(geometry, spec, include_face=False, include_ink=False)
            save_piece(scene, out, rig, name, geometry)
            descriptor = out / f"{name}.pm"
            template = descriptor.read_text(encoding="utf8")
            descriptor.unlink()
        templates[female] = (name, template)

    index = {}
    for key, spec, family, _ in roster:
        head = key + "_face"
        save_actor_head(out, scene, rig, spec, head, detail)
        base, template = templates[bool(spec.get("female"))]
        (out / f"{key}.pm").write_text(tint_body(template, PORTRAIT_SKIN_TONES.get(key, spec["skin"])), encoding="utf8", newline="\n")
        index[key] = {"base": base, "face": head}
        if spec.get("head") == "hachimaki":
            band = c.Skin(spec)
            c.headband(band, spec)
            name = key + "_headband"
            save_piece(scene, out, rig, name, band, surface=detail if any(band.surfaces) else None)
            index[key]["headband"] = name
        print(f"MODULAR {key} {base} {family}", flush=True)
    for key, entry in foes.items():
        spec = entry["spec"]
        base, template = templates[bool(spec.get("female"))]
        (out / f"{key}.pm").write_text(tint_body(template, PORTRAIT_SKIN_TONES.get(spec.get("model_key"), spec["skin"])), encoding="utf8", newline="\n")
        index[key] = {"base": base}
        save_foe(out, scene, rig, key, entry, index[key], detail)
        print(f"MODULAR FOE {key} {base} {entry['family']}", flush=True)
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf8")


if __name__ == "__main__":
    path = Path(sys.argv[sys.argv.index("--") + 1])
    data = json.loads(path.read_text(encoding="utf8"))
    export(Path(data["out"]), data["models"], data.get("foes", {}), data.get("body_pack"))
