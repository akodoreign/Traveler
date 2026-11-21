"""Flashing ally icons for companion Void criticals (user 2026-11-21: "use the icons there are a bunch of them now",
"re use some of the flashing icons we made"). Each is built like Ide's heart: an 8-frame billboard strip + a
one-particle .ptd: the battle UI's element / weapon icon (resource/efx/battleui/w_*.png) inside a ring in the
companion's colour, swelling and flashing twice a cycle.
    python -E tools/companion_void_fx.py [resource/efx/rt dir]
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from ide_performance_fx import FRAME_COUNT, SIZE, particle

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource" / "efx"

# ward name -> (icon, ring colour)
WARDS = {
    "hida_earth_ward": ("w_earth", (232, 186, 92)),       # Hida Sachiko: the Mountain
    "cv_ward_air_teal": ("w_air", (96, 214, 206)),        # Hiruma Ryoichi: razor's edge
    "cv_ward_katana_teal": ("w_katana", (96, 214, 206)),  # Hiruma Goro
    "cv_ward_tetsubo_teal": ("w_tetsubo", (96, 214, 206)),  # Hiruma Kage
    "cv_ward_katana_gold": ("w_katana", (240, 196, 72)),  # Akodo Gusai / Hiruto / Rin
    "cv_ward_unarmed_gold": ("w_unarmed", (240, 196, 72)),  # Akodo Kafu
    "cv_ward_yari_crimson": ("w_yari", (222, 74, 58)),    # the Lion rider (Matsu)
    "cv_ward_fire_crimson": ("w_fire", (222, 74, 58)),    # Matsu Hanae
    "cv_ward_fire_ember": ("w_fire", (250, 140, 52)),     # Shiba Ashimita
    "cv_ward_jade_ivory": ("w_jade", (238, 232, 210)),    # Seppun Ushimo
    "cv_ward_katana_white": ("w_katana", (250, 244, 228)),  # Doji Hayato
    "cv_ward_water_sea": ("w_water", (70, 150, 226)),     # Yoritomo Rui
    "cv_ward_air_pale": ("w_air", (214, 234, 246)),       # Shinjo Ryuko
    "cv_ward_fire_violet": ("w_fire", (168, 112, 232)),   # Isawa Michio
    "cv_ward_jade_amber": ("w_jade", (226, 170, 84)),     # Isawa Sanro
    "cv_ward_air_violet": ("w_air", (168, 112, 232)),     # Isawa Kasiko
    "cv_ward_fire_orange": ("w_fire", (246, 120, 40)),    # Tamori Haku
}


def frame(index, icon, rgb):
    t = index / FRAME_COUNT
    beat = max(0.0, math.cos(2 * math.pi * (t * 2 - .25))) ** 4          # two flashes per cycle
    img = Image.new("RGBA", (SIZE, SIZE))
    ring = Image.new("RGBA", (SIZE, SIZE))
    d = ImageDraw.Draw(ring)
    r = 30 + 8 * beat
    d.ellipse((SIZE / 2 - r, SIZE / 2 - r, SIZE / 2 + r, SIZE / 2 + r), outline=(*rgb, int(120 + 120 * beat)), width=5)
    ring = ring.filter(ImageFilter.GaussianBlur(2.2))
    img.alpha_composite(ring)
    s = int(56 + 10 * beat)
    ic = icon.resize((s, s), Image.Resampling.LANCZOS)
    if beat > .05:
        white = Image.new("RGBA", ic.size, (255, 248, 220, 0))
        white.putalpha(ic.getchannel("A").point(lambda a: int(a * .55 * beat)))
        ic = Image.alpha_composite(ic, white)
    img.alpha_composite(ic, ((SIZE - s) // 2, (SIZE - s) // 2))
    return img


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path, nargs="?", default=RES / "rt")
    a = p.parse_args()
    a.directory.mkdir(parents=True, exist_ok=True)
    for name, (icon_name, rgb) in WARDS.items():
        icon = Image.open(RES / "battleui" / f"{icon_name}.png").convert("RGBA")
        sheet = Image.new("RGBA", (SIZE * FRAME_COUNT, SIZE))
        for i in range(FRAME_COUNT):
            sheet.paste(frame(i, icon, rgb), (i * SIZE, 0))
        sheet.save(a.directory / f"{name}.png")
        particle(a.directory, name, 1200, 0.9)
    print("wrote", len(WARDS), "wards to", a.directory)


if __name__ == "__main__":
    main()
