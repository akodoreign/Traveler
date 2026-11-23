"""Submit Coast Road art through the existing local ComfyUI installations."""

import json
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

HERE = Path(__file__).resolve().parent
CONCEPTS = HERE / "concepts"
CONCEPTS.mkdir(exist_ok=True)
HTTP = "http://127.0.0.1:8188"
THREED = Path("C:/AI/comfy-3d")
ART = {
    "cedar_bench": ("one freestanding low rustic Japanese cedar bench, rectangular uneven thick plank seat, "
                   "two chunky timber trestle legs, oak pegs, late Sengoku rural coast roadside rest stop, "
                   "weathered warm gray brown wood, visible horizontal plank seams, simple clearly readable geometry"),
    "salt_crate": ("one low rectangular fifteenth to sixteenth century rural Japanese cedar packing chest, "
                   "three dark horizontal split wood planks, pegged narrow vertical battens, stained straw rope handles, "
                   "old gray-brown worn cedar, small practical salt merchant's supply box, complete visible corners"),
    "shore_boulder": ("one low irregular wide layered coastal slate boulder, stepped sandy gray strata "
                      "and patches of cool moss, four chunky horizontal ledges, sun-worn sandstone colors"),
    "wind_grass": ("one isolated tuft of Japanese coastal dune grass, several tall narrow olive and jade "
                   "grass blades, some golden slender tips, rooted in a small tight cluster, "
                   "blocky small voxel diorama, clean individual blade silhouettes"),
    "coast_flowers": ("one small low wild flowering clump for Japan's coast, low muted rosy pink five-petal "
                       "coastal flowers, small ochre centers, waxy jade green leaves, several upright thin "
                       "green stalks, flowers at three heights, pixel-shaped petals"),
    "sand_grain": ("seamless tiling game texture, strictly straight-down orthographic flat material scan "
                   "of pale muted golden wind-raked slightly damp coastal sand, small scattered warm ivory "
                   "and dark gray pebbles, fine irregular granular detail, soft horizontal ripples, "
                   "no objects no perspective no borders no horizon, balanced even light"),
    "meadow_grain": ("seamless tiling game texture, strictly straight-down orthographic flat material scan "
                     "of fine olive and jade grass on nutrient-rich muted mossy brown coastal soil, "
                     "overlapping subtle small irregular patches of grass with warm straw dead blades, "
                     "no objects no perspective no borders no horizon, balanced even light"),
    "cliff_grain": ("seamless tiling game texture, flat straight-on photo atlas of weathered warm grey "
                    "Japanese coastline sandstone cliff rock, horizontal tight bedding planes with irregular "
                    "hairline fractures, pale sand highlights, dark weathered gray seams, finely detailed  "
                    "natural stone, no scenery no perspective no borders no horizon, balanced even light"),
    "water_grain": ("seamless tiling game texture, strictly overhead clear shallow coastal sea water, "
                    "deep turquoise jade teal waves with soft pale seafoam caustic curved threads, "
                    "fine natural ripples with no objects or shoreline, no perspective no borders no horizon"),
}
SHAPE_INPUTS = ("cedar_bench", "salt_crate", "shore_boulder")


def response(base, path, payload=None):
    req = Request(base + path, data=None if payload is None else json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=45) as result:
        return result.read()


def workflow(key, positive, seed):
    material = key.endswith("_grain")
    if not material:
        positive += (", one isolated game asset only, full object orthographic isometric three-quarter view "
                     "from slightly elevated camera, centered with generous blank white margin, pure white "
                     "background, no floor line, hand-crafted high-detail voxel diorama forms, "
                     "muted harmonious natural tones, daylight physically based material shading")
    negative = ("text, signature, border, people, complex background, scene, multiple objects, clutter, "
                "cropped, floating pieces, cast shadow, harsh lighting, glossy plastic, modern industrial hardware")
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "novaAnimeXL_ilV190.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": positive}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": negative}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
              "latent_image": ["4", 0], "seed": seed, "steps": 23, "cfg": 5.1, "sampler_name": "dpmpp_2m",
              "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": f"traveler_coast/{key}"}},
    }


def download(prompt):
    result = json.loads(response(HTTP, f"/history/{prompt}")).get(prompt)
    if not result:
        return None
    if result["status"]["status_str"] != "success":
        raise RuntimeError(result["status"])
    image, = result["outputs"]["7"]["images"]
    return response(HTTP, "/view?" + urlencode(image))


def main():
    receipts = HERE / "comfy-receipts.json"
    saved = json.loads(receipts.read_bytes()) if receipts.is_file() else {"images": {}, "meshes": {}}
    for index, (key, text) in enumerate(ART.items()):
        if key not in saved["images"]:
            data = workflow(key, text, 1851500 + index)
            result = json.loads(response(HTTP, "/prompt", {"prompt": data, "client_id": str(uuid4())}))
            saved["images"][key] = result["prompt_id"]
            receipts.write_text(json.dumps(saved, indent=2), encoding="utf-8")
            print(f"Queued Comfy image {key}: {result['prompt_id']}", flush=True)
    pending = dict(saved["images"])
    stop = time.monotonic() + 900
    while pending:
        for key, prompt in tuple(pending.items()):
            concept = CONCEPTS / f"{key}.png"
            if not concept.is_file():
                png = download(prompt)
                if png is None:
                    continue
                if not png.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise RuntimeError(f"Invalid Comfy output for {key}")
                concept.write_bytes(png)
                print(f"Downloaded {key}", flush=True)
            del pending[key]
        if pending:
            if time.monotonic() >= stop:
                raise TimeoutError(pending)
            time.sleep(4)
    # Run the two installations in sequence so the GPU can unload the image model.
    response(HTTP, "/free", {"unload_models": True, "free_memory": True})
    for key in SHAPE_INPUTS:
        if key in saved["meshes"]:
            continue
        result = subprocess.run([str(THREED / "venv/Scripts/python.exe"), str(THREED / "queue.py"),
                                 str(CONCEPTS / f"{key}.png"), "--name", f"traveler_env_coast_{key}",
                                 "--seed", "47", "--no-wait"], capture_output=True, text=True, check=True)
        print(result.stdout.strip(), flush=True)
        saved["meshes"][key] = json.loads(result.stdout.strip().splitlines()[-1])
        receipts.write_text(json.dumps(saved, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
