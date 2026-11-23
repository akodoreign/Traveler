"""Generate administrative room props through the local image and mesh queues."""

import json
import subprocess

from comfy_coast import THREED
from comfy_furnace import generate
from comfy_surface_pass import OUT

PROMPTS = {
    "hoshi_case_bundle": (
        "One small tied bundle of old Japanese handmade mulberry-paper folios, papers folded "
        "and stacked irregularly, wrapped by a narrow faded persimmon-dyed paper band and light "
        "tan hemp cord. Modest late sixteenth century Japanese magistrate's filing bundle. One "
        "intact isolated volume, white background, no writing, other objects, ground, or shadow."
    ),
    "hoshi_inkstone": (
        "One small plain charcoal-grey Japanese suzuri inkstone block, softly worn rectangular "
        "rims, shallow grinding slope and ink recess, a simple indigo-brown fitted lacquer tray "
        "beneath it. Modest Sengoku-era court clerk tool. Single complete isolated prop in "
        "orthographic three-quarter view on white, no letters, ground shadow or other objects."
    ),
}


if __name__ == "__main__":
    generate(PROMPTS, "comfy-hoshi-magistrate-receipts.json", 94110)
    receipt = OUT.parent/"comfy-hoshi-magistrate-mesh.json"
    jobs = json.loads(receipt.read_bytes()) if receipt.exists() else {}
    for key, seed in zip(PROMPTS,(69,70)):
        if key in jobs:
            continue
        run = subprocess.run(
            [str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
             str(OUT/f"{key}.png"),"--name",f"traveler_env_coast_{key}",
             "--seed",str(seed),"--no-wait"],
            capture_output=True,text=True,check=True,
        )
        jobs[key] = json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs,indent=2),encoding="utf-8")
        print(key,jobs[key],flush=True)
