"""Generate material references for the Tamori's Furnace environment."""

import json
from urllib.parse import urlencode
from uuid import uuid4
import time

from comfy_surface_pass import graph, HTTP, response, OUT, HERE

PROMPTS = {
    "furnace_basalt": ("Ultra detailed flat front-on orthographic game albedo texture scan of jointed "
        "charcoal basalt inside a lava tube. Dark blue slate and purplish gray stone, sharp chunky polygonal "
        "breaks, horizontal shear and a few deep cracks. Gentle even neutral illumination. Tileable edge "
        "to edge square, only the mineral, no lava, no props, no perspective, no writing."),
    "furnace_ash": ("Strict straight-down square material scan of dark gray dry volcanic cinders, scoria and "
        "fine ash. Fine particulate texture, occasional broken small angular black porous pebbles, neutral "
        "cool grays with a muted hint of ochre. Consistent scale, flat physically based albedo, edge to edge, "
        "no scenery, no shadows, no symbols, no frame."),
    "furnace_flow": ("Strict straight-down orthographic square seamless top-down material map of slowly "
        "moving basaltic lava. Black purple charcoal islands of thick cracked lava crust surrounded by a "
        "connected network of molten red orange channels with narrow golden hot interiors. Organic lava "
        "rope textures, broken darker plates, no water, no explosions, no horizon, no terrain framing, "
        "the magma texture fills the square, high detail."),
    "furnace_columns": ("Isolated low-resolution voxel game diorama asset, one asymmetrical cluster of "
        "thick fractured charcoal-purple basalt columns after their lava solidified. Seven close-packed "
        "vertical jointed geological rock stacks, partly broken at different heights, stair-step edges and "
        "vertical cracks, fine gray grain and terracotta staining. Complete freestanding three-quarter "
        "orthographic view on plain white, no ground plane, no architecture, no words."),
}


def generate(prompts, receipt, seed):
    OUT.mkdir(exist_ok=True)
    path = HERE / receipt
    jobs = json.loads(path.read_bytes()) if path.is_file() else {}
    for index, (key, prompt) in enumerate(prompts.items()):
        if key in jobs:
            continue
        packet = {"prompt": graph(key, prompt, seed + index), "client_id": str(uuid4())}
        jobs[key] = json.loads(response(HTTP, "/prompt", packet))["prompt_id"]
        path.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
        print(key, jobs[key], flush=True)
    deadline = time.monotonic() + 780
    pending = {key: job for key, job in jobs.items() if not (OUT / f"{key}.png").is_file()}
    while pending:
        for key, job in list(pending.items()):
            history = json.loads(response(HTTP, f"/history/{job}")).get(job)
            if not history:
                continue
            if history["status"]["status_str"] != "success":
                raise RuntimeError(history["status"])
            image, = history["outputs"]["10"]["images"]
            (OUT / f"{key}.png").write_bytes(response(HTTP, "/view?" + urlencode(image)))
            del pending[key]
            print("downloaded", key, flush=True)
        if pending:
            if time.monotonic() >= deadline:
                raise TimeoutError(pending)
            time.sleep(3)


if __name__ == "__main__":
    generate(PROMPTS, "comfy-furnace-receipts.json", 67035)
