"""Generate the goods shop's lacquered trade chest and woven salt sack."""

import json
import subprocess

from comfy_coast import THREED
from comfy_furnace import generate
from comfy_surface_pass import OUT

PROMPTS = {
    "hoshi_trade_chest": (
        "One plain Japanese provincial merchant chest from the late 1500s, low rectangular "
        "cedar box with subdued dark vermilion lacquer, black forged strap hinges, simple "
        "iron corner binding and one front pull. Rubbed edges from years of use. Complete "
        "freestanding closed box, three-quarter orthographic product view on pure white, "
        "no platform, ground shadow, letters, crest, people or other objects."
    ),
    "hoshi_salt_sack": (
        "One isolated small sack of coarse sea salt for a Japanese coastal merchant in the late "
        "1500s, tobacco-tan woven hemp, round soft-sided base and a simple gathered top tied "
        "with dark straw cord. An understated faded indigo horizontal stripe around the sack. "
        "Entire freestanding sack, detailed weave, three-quarter orthographic view on pure "
        "white, no stage, writing, ground shadow or other objects."
    ),
}


if __name__ == "__main__":
    generate(PROMPTS, "comfy-hoshi-goods-receipts.json", 94071)
    receipt = OUT.parent / "comfy-hoshi-goods-mesh.json"
    jobs = json.loads(receipt.read_bytes()) if receipt.exists() else {}
    for key, seed in zip(PROMPTS, (63, 64)):
        if key in jobs:
            continue
        run = subprocess.run(
            [str(THREED / "venv/Scripts/python.exe"), str(THREED / "queue.py"),
             str(OUT / f"{key}.png"), "--name", f"traveler_env_coast_{key}",
             "--seed", str(seed), "--no-wait"],
            capture_output=True, text=True, check=True,
        )
        jobs[key] = json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
        print(key, jobs[key], flush=True)
