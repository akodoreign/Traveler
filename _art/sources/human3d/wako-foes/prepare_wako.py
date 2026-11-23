"""Stage five foe-specific body material, face, fit and equipment routes."""

import json
from pathlib import Path
import re
import shutil
import sys

from PIL import Image


STAGE = Path(__file__).resolve().parent
FILES = Path("project/resource")
FITS = {
    "EP417": ("side_sailor", 1.15, 1.018, "A127", "ronin", "wako_slate"),
    "EP404": ("side_h_sparrow", 1.03, .982, "A100", "ronin", None),
    "EP1300": ("side_lionsergeant", 1.09, 1.0, "A135", "lion", None),
    "EP1301": ("side_seppunguard", 1.17, 1.031, "A109", "lion", None),
    "EP1302": ("side_bayushiguard", 1.08, 1.0, "A120", "dragon", None),
}
EQUIPMENT = {
    "EP417": {"hat": "side_sailor_hachimaki", "weapon": "ep417_wako_nodachi"},
    "EP404": {"hatItem": "A102", "weaponItem": "W100"},
    "EP1300": {"hatItem": "A102", "weaponItem": "W101"},
    "EP1301": {"weaponItem": "W110"},
    "EP1302": {"mask": "side_bayushiguard_portrait_charcoal_cloth", "weaponItem": "W100"},
}


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf8")


def main(repo):
    source = repo / "_tools/rpgcobo-tool" / FILES
    output = STAGE / FILES
    human = read(source / "native_human/index.json")
    outfits = read(source / "native_tailoring/index.json")
    skin = read(repo / "_art/sources/human3d/skin_tones.json")
    foes = read(source / "native_foe/index.json")
    records = {}
    for key, (donor, width, scale, outfit, clan, palette) in FITS.items():
        assert human[key]["base"] == human[donor]["base"] == "shared_male"
        assert foes[key]["human"] and foes[key]["scale"] == .013
        face = human[donor]["face"]
        assert face.endswith("_portrait_face")
        assert (source / f"native_human/{face}.mdl").is_file()
        body = source / f"native_human/{donor}.pm"
        materials = re.findall(r"\bbasecol = (0x[0-9a-f]+)", body.read_text(encoding="utf8"))
        assert len(materials) == 5 and len({materials[i] for i in (0, 1, 2, 4)}) == 1
        body_out = output / f"native_human/{key}.pm"
        body_out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(body, body_out)
        fit = {
            **human[key], "face": face,
            "width": width, "heightScale": scale, **EQUIPMENT[key],
        }
        # Keep any old compatible accessory as a resource fallback for its loaded item.
        garment = dict(outfits["items"][outfit], clan=clan)
        if palette:
            garment["palette"] = palette
        if key in ("EP417", "EP1302"):
            garment.pop("decal", None)
        records[key] = {
            "donor": donor, "body_skin_srgb": skin[donor], "body_skin_basecol": materials[0],
            "human": fit, "tailoring": garment,
        }
    material = output / "native_tailoring/tex/ronin/wako_slate.png"
    material.parent.mkdir(parents=True, exist_ok=True)
    base = Image.open(source / "native_tailoring/tex/crab/A127.png").convert("RGBA")
    # Keep the generated cloth weave and alpha. Age the deep Crab-blue dye
    # into an unmarked coastal slate instead of using the clan's decal layer.
    red, green, blue, alpha = base.split()
    dyed = Image.merge("RGBA", (
        red.point(lambda v: min(255, int(v * .94 + 7))),
        green.point(lambda v: min(255, int(v * .94 + 7))),
        blue.point(lambda v: min(255, int(v * .87 + 5))),
        alpha,
    ))
    dyed.save(material)
    write(STAGE / "wako-fits.json", records)
    print(f"Prepared {len(records)} native human foe fits")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
