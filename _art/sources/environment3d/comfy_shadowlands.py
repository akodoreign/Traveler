"""Generate the Hiruma road's ground, shattered basalt, and dying thorn brush."""

import json
import subprocess

from comfy_coast import THREED
from comfy_furnace import generate
from comfy_surface_pass import OUT

PROMPTS = {
    "shadowlands_earth": (
        "Edge-to-edge flat square top-down material scan of desolate dark plum-gray volcanic "
        "earth, fine volcanic dust caught in cracked clay, occasional muted rusty-red mineral "
        "stains. Subdued color, consistent scale, matte natural grain, no paths, lighting "
        "direction, props, plants, horizon, or text."
    ),
    "shadowlands_thorns": (
        "Single low wind-torn fantasy bramble thicket for a dark volcanic wasteland. Dense "
        "interlocking charcoal stems, wiry blackberry branches, a few dark muted red dried "
        "leaves and clumps of black brittle grass low around a strong roots base. Totally "
        "isolated on plain white, fully visible from roots to tips, no ground plane, shadow, "
        "person, objects or text, high detail three-quarter orthographic game asset."
    ),
    "shadowlands_shards": (
        "Single cluster of fractured upright basalt slabs from a ruined dark fantasy road. "
        "Blue-charcoal slate, layered crust, jagged asymmetrical low and high tips and fine "
        "oxide patches. Freestanding terrain obstruction, wide base, entirely visible on pure "
        "white, three-quarter orthographic, no shadow or ground plane, no scenery or writing."
    ),
    "shadowlands_waymarker": (
        "One complete ancient low waystone from a ruined Japanese mountain road, dark irregular "
        "stone with a rounded shoulder and a notched weathered head. A tiny worn crab crest carved "
        "shallowly in the upper face and muted pale green jade grit caught in several cracks. "
        "Sparse moss near the foot. Three-quarter orthographic single object on pure white, "
        "no platform, ground plane, text, person or background."
    ),
    "shadowlands_broken_cart": (
        "One collapsed small two-wheel wooden scout cart from a fantasy late sixteenth century "
        "Japanese mountain road, dark splintered cedar frame with one broken wheel still attached, "
        "twisted lashing and a short strip of faded red cloth. Low and irregular, all pieces close "
        "to the cart. One isolated prop on pure white, orthographic three-quarter, no ground plane, "
        "shadow, scenery, extra props or figures."
    ),
    "shadowlands_dead_cedar": (
        "One twisted short dead Japanese cedar with silver charcoal split bark, torn "
        "asymmetrical angular limbs, exposed thick roots and a little red-brown fungus. "
        "A dark fantasy wasteland landmark. Complete isolated three-quarter orthographic "
        "game prop on plain white, no ground plane, shadow, foliage, building or figure."
    ),
    "shadowlands_ruined_shrine": (
        "Single broken waist-high Japanese stone roadside shrine with fractured tiered "
        "stone roof, sunken foot and a dark carved empty niche. Ash and bluish purple "
        "stone with subdued yellow lichens. Freestanding fantasy world prop, complete "
        "three-quarter orthographic view on white, no text, platform or ground shadow."
    ),
    "hiruma_gate_ruin": (
        "One ruined Japanese Sengoku-period fortified gateway, fully open central passage beneath "
        "thick charred cypress framing, broken adjoining battered stone bases, and a shallow black "
        "kawara roof with several missing tiles. Weathered wood and one small strip of deep navy "
        "cloth with a faded red edge. Isolated on pure white, complete three-quarter orthographic "
        "fantasy game prop without ground plane, people, text, extra walls, glowing effects or shadow."
    ),
    "hiruma_ancestor_tablets": (
        "One complete small charred cedar household altar furniture piece from historical Japan. "
        "Low lacquered bench and wood cabinet with aligned rows of slender upright dark wooden memorial "
        "tablets in an open recess, restrained dull bronze trim, and ash. Isolated on pure white, "
        "complete three-quarter orthographic, physical fantasy game prop without text, floor or shadow."
    ),
    "hiruma_fallen_standard": (
        "Single fallen Japanese Sengoku field standard, broken upright cedar mounting in dark "
        "irregular stones, tattered deep indigo woven banner with bookmatched crimson edging and "
        "faded pale crab crest. Entire isolated object on pure white, clear silhouette three-quarter "
        "orthographic fantasy game prop, no text, scene, shadow, person or ground plane."
    ),
}


if __name__ == "__main__":
    generate(PROMPTS, "comfy-shadowlands-receipts.json", 94173)
    receipt = OUT.parent/"comfy-shadowlands-mesh.json"
    jobs = json.loads(receipt.read_bytes()) if receipt.exists() else {}
    for key,seed in (
        ("shadowlands_thorns",72),("shadowlands_shards",73),
        ("shadowlands_waymarker",74),("shadowlands_broken_cart",75),
        ("shadowlands_dead_cedar",76),("shadowlands_ruined_shrine",77),
        ("hiruma_gate_ruin",78),("hiruma_ancestor_tablets",79),("hiruma_fallen_standard",80),
    ):
        if key in jobs:
            continue
        run = subprocess.run(
            [str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
             str(OUT/f"{key}.png"),"--name",f"traveler_env_coast_{key}",
             "--seed",str(seed),"--no-wait"],capture_output=True,text=True,check=True,
        )
        jobs[key] = json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs,indent=2),encoding="utf-8")
        print(key,jobs[key],flush=True)
