"""Generate a new straw target for the Kaiu training yard."""

from comfy_furnace import generate
from comfy_surface_pass import OUT
from comfy_coast import THREED
import json
import subprocess

NAME = "kaiu_straw_target"
PROMPTS = {
    NAME: (
        "One freestanding sixteenth century Japanese practice target, one cylindrical bundle of neatly woven "
        "pale golden straw lashed horizontally at chest height to two squared weathered cedar stakes with a "
        "short cross brace and rope lashing; a simple low charcoal pebbled footing. Recognizable training yard "
        "prop, not a person or a weapon. Single isolated full object, slightly raised three-quarter orthographic "
        "view, flat white background, generous white margins, realistic weave and dark primitive timber."
    )
}

if __name__ == "__main__":
    generate(PROMPTS, "comfy-kaiu-details-receipts.json", 510309)
    receipt = OUT.parent / "comfy-kaiu-target-mesh.json"
    if not receipt.is_file():
        run = subprocess.run([str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
                              str(OUT/f"{NAME}.png"),"--name",f"traveler_env_coast_{NAME}",
                              "--seed","143","--no-wait"],capture_output=True,text=True,check=True)
        job = json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(job,indent=2),encoding="utf-8")
        print(job,flush=True)
