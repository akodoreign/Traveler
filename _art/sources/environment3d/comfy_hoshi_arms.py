"""Generate decorative stock for Hoshi's equipment shop display racks."""

import json
import subprocess

from comfy_coast import THREED
from comfy_furnace import generate
from comfy_surface_pass import OUT

PROMPTS = {
    "hoshi_arms_bundle": (
        "Museum diorama prop showing a single late-sixteenth century Japanese sheathed sword "
        "wrapped for display, simple dark indigo cloth cover tied with two faded ochre cords, "
        "muted copper end caps and a gently curved elongated silhouette. Fully enclosed and "
        "resting horizontally, centered full-length on pure white. Orthographic product "
        "view, no fixture, ground shadow, face, blade, text or other object."
    ),
    "hoshi_arms_armor_sample": (
        "One old suit of late sixteenth century Japanese display armor on a low "
        "plain wood shop stand, blue-black layered lacquered iron cuirass, small reddish silk "
        "laces, simple dark hemispherical helmet and draped off-white lining. Arms absent or "
        "stowed to sides. Empty historical museum artifact. Full compact object on pure white, "
        "three-quarter orthographic view, no people, large horns, crests, scenery or ground shadow."
    ),
}


if __name__ == "__main__":
    generate(PROMPTS, "comfy-hoshi-arms-receipts.json", 94089)
    receipt=OUT.parent/"comfy-hoshi-arms-mesh.json"
    jobs=json.loads(receipt.read_bytes()) if receipt.exists() else {}
    for key, seed in zip(PROMPTS,(66,67)):
        if key in jobs:
            continue
        run=subprocess.run(
            [str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
             str(OUT/f"{key}.png"),"--name",f"traveler_env_coast_{key}",
             "--seed",str(seed),"--no-wait"],
            capture_output=True,text=True,check=True,
        )
        jobs[key]=json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs,indent=2),encoding="utf-8")
        print(key,jobs[key],flush=True)
