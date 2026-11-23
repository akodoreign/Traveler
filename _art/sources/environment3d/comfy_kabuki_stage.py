"""Generate original theatrical flats and a bronze mirror for the Crane play."""

import json
import subprocess

from comfy_coast import THREED
from comfy_furnace import generate
from comfy_surface_pass import OUT

PROMPTS = {
    "kabuki_komatsu_paint": (
        "Square face-on painted scenic flat for a Japanese historical fantasy stage, "
        "the lost Court of Komatsu. A warm gold background with a hand-painted dark "
        "pine bough, restrained persimmon cloud bands and aged gold-leaf underpaint. "
        "Large readable simple forms, brush grain, matte pigments, no people, objects "
        "in front, titles, calligraphy, borders or angle distortion."
    ),
    "kabuki_mirror_paint": (
        "Square full-bleed painting on a Japanese theatre flat for a private imperial "
        "chamber. Muted malachite and sea green fog behind delicate branches and "
        "pale gold running water, broad curves, washed ink on handmade textile. "
        "Front-on flat image, quiet atmosphere, no people, mirror, calligraphy, "
        "writing, borders or frame."
    ),
    "kabuki_blade_paint": (
        "An orthographic square painted backdrop for a historical fantasy theatre in "
        "Japan. Cold midnight blue and violet palace garden, a low pale moon, reeds "
        "and fine bare pine silhouettes, layered mist. Broad flat hand-painted stage "
        "design that reads at a distance, no people, weapon, writing or borders."
    ),
    "kabuki_title_paint": (
        "A full-bleed square painted scenic flat for the final act of a Japanese "
        "fantasy historical play. Muted vermilion clouds over pale antique gold, "
        "with rivulets of smoke and delicate ash-gray branches along the lower "
        "margin. Bright subdued gilded center where actors can silhouette. "
        "Flat scenic illustration, no text, characters, panels or framing."
    ),
    "kabuki_bronze_mirror": (
        "One freestanding banquet-sized round Japanese bronze vanity mirror on a carved "
        "dark red lacquer wood stand. Opaque sea-gray burnished polished bronze, subtle "
        "tonal glint, engraved fine rim, rear wooden easel support, theatrical fantasy "
        "prop. Complete isolated model, pure white background, no shadow, floor, "
        "writing, humans or secondary objects, front three-quarter orthographic."
    ),
}


if __name__ == "__main__":
    generate(PROMPTS, "comfy-kabuki-stage-receipts.json", 94201)
    receipt = OUT.parent/"comfy-kabuki-mirror-mesh.json"
    if not receipt.exists():
        run = subprocess.run(
            [str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
             str(OUT/"kabuki_bronze_mirror.png"),"--name","traveler_env_coast_kabuki_bronze_mirror",
             "--seed","78","--no-wait"],capture_output=True,text=True,check=True,
        )
        result = json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(result,indent=2),encoding="utf8")
        print(result,flush=True)
