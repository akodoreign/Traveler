"""Create the inn's woven bedding scan and a new travel-bundle mesh."""

from comfy_furnace import generate
from comfy_surface_pass import OUT
from comfy_coast import THREED
import json
import subprocess

PROMPTS={
    "hoshi_inn_bedding": (
        "Edge-to-edge orthographic diffusion material scan of homespun cream cotton bedding, handwoven "
        "moderately coarse fabric with subtle linen fibers and a pale beige hue. One flat matte textile "
        "with a few faint changes of weave, no border, no perspective, no folds, no objects."
    ),
    "hoshi_travel_bundle": (
        "One modest traveller's wrapped cloth pack, low bundled travel luggage in worn indigo cotton, a "
        "plain cloth knot, faded rice-straw braided cord, and a rolled small brown reed mat lashed around "
        "the bundle. Single full isolated Japanese period inn prop. White background with no surface "
        "plane or shadow, detailed cloth folds and tiny weave, three-quarter orthographic."
    ),
}

if __name__=="__main__":
    generate(PROMPTS,"comfy-hoshi-inn-receipts.json",94021)
    receipt=OUT.parent/"comfy-hoshi-inn-mesh.json"
    if not receipt.is_file():
        run=subprocess.run([str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
                            str(OUT/"hoshi_travel_bundle.png"),"--name","traveler_env_coast_hoshi_travel_bundle",
                            "--seed","59","--no-wait"],capture_output=True,text=True,check=True)
        result=json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(result,flush=True)
