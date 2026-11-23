"""Deeper, richer clan dyes (user 2026-11-22: "continue fixing all npc clan colors, including kisada. with the deeper
richer colors"; for Hida Kisada: "dark blue, with darker blue tint, red studs"). Every samurai NPC in a tailored outfit
wears tex/<clan>/<mesh>.png, dyed from the outfit's base texture with the clan's five role colours (top, lower, accent,
armor, lace - gear_palette.NATIVE_CLANS). This re-dyes the deployed clan textures from the palette they were built
with (AS_BUILT) to the deeper one (gear_palette.NATIVE_CLANS, updated to match), the way blender/generated_wardrobe.dyes
does: each pixel split over the five role colours, the baked folds kept as shade. The textures as first deployed are
kept in tmp/clan_dye_src (not committed) and every run dyes from those, so running it again never dyes twice.
Commoners (peasant / eta / ronin) keep their own dyes (tools/gen_commoner_dyes.py).
python -E tools/gen_clan_dyes.py [clan ...]   -> resource/native_tailoring/tex/<clan>/*.png + _art/preview/clan_dyes.png"""
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gear_palette import NATIVE_CLANS  # noqa: E402
from gen_commoner_dyes import dye  # noqa: E402

PROJ = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project"))
TEX = os.path.join(PROJ, "resource", "native_tailoring", "tex")
SRC = os.path.normpath(os.path.join(PROJ, "..", "tmp", "clan_dye_src"))
PREVIEW = os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "clan_dyes.png"))

# the palettes the deployed clan textures were dyed with (gear_palette before 2026-11-22)
AS_BUILT = {
    "crab": ((37, 67, 116), (19, 35, 62), (185, 43, 41), (75, 94, 113), (210, 55, 46)),
    "crane": ((36, 106, 166), (32, 61, 100), (244, 234, 212), (95, 133, 166), (237, 229, 210)),
    "dragon": ((27, 109, 68), (22, 64, 47), (211, 155, 48), (33, 92, 59), (237, 189, 74)),
    "lion": ((178, 110, 23), (106, 56, 28), (237, 178, 60), (146, 86, 28), (160, 46, 29)),
    "mantis": ((15, 119, 100), (17, 59, 55), (219, 166, 68), (34, 100, 84), (232, 189, 87)),
    "phoenix": ((219, 79, 19), (127, 30, 33), (196, 41, 29), (130, 45, 32), (249, 168, 51)),
    "scorpion": ((147, 21, 43), (50, 23, 38), (206, 152, 82), (91, 22, 38), (196, 38, 51)),
    "unicorn": ((108, 48, 151), (59, 33, 90), (212, 159, 77), (85, 54, 119), (234, 183, 89)),
    "imperial": ((26, 112, 70), (26, 66, 48), (225, 177, 62), (42, 91, 58), (241, 195, 88)),
}
CLANS = tuple(AS_BUILT)


def textures(clan):
    """The clan's own outfit textures (not the commoner variants, which only peasant / eta / ronin have)."""
    d = os.path.join(TEX, clan)
    return sorted(f for f in os.listdir(d) if f.endswith(".png")) if os.path.isdir(d) else []


def keep_sources():
    for clan in CLANS:
        os.makedirs(os.path.join(SRC, clan), exist_ok=True)
        for f in textures(clan):
            src = os.path.join(SRC, clan, f)
            if not os.path.exists(src):
                shutil.copy2(os.path.join(TEX, clan, f), src)


def swatch_sheet():
    w, h = 64, 40
    im = Image.new("RGB", (w * 11, h * 2 * len(CLANS) + 10), (24, 22, 26))
    d = ImageDraw.Draw(im)
    for i, clan in enumerate(CLANS):
        y = i * 2 * h
        d.text((4, y + 4), clan, fill=(230, 220, 200))
        d.text((4, y + h + 4), "before / after", fill=(150, 140, 130))
        for k, (a, b) in enumerate(zip(AS_BUILT[clan], NATIVE_CLANS[clan])):
            d.rectangle((w * (k + 1), y, w * (k + 2) - 2, y + h - 2), fill=tuple(a))
            d.rectangle((w * (k + 1), y + h, w * (k + 2) - 2, y + 2 * h - 2), fill=tuple(b))
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    im.save(PREVIEW)


def main():
    keep_sources()
    n = 0
    only = set(a for a in sys.argv[1:] if not a.startswith("-"))
    for clan in CLANS:
        if (only and clan not in only) or tuple(map(tuple, NATIVE_CLANS[clan])) == AS_BUILT[clan]:
            continue
        for f in textures(clan):
            rgb = np.asarray(Image.open(os.path.join(SRC, clan, f)).convert("RGB"), float) / 255
            Image.fromarray(dye(rgb, AS_BUILT[clan], NATIVE_CLANS[clan])).save(os.path.join(TEX, clan, f),
                                                                              optimize=True)
            n += 1
        print("%-9s %d textures" % (clan, len(textures(clan))), flush=True)
    swatch_sheet()
    print("clan dyes: %d textures re-dyed; swatches %s" % (n, PREVIEW))


if __name__ == "__main__":
    main()
