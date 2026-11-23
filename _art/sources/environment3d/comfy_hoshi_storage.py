"""Generate Hoshi's rebuilt storehouse props and lantern paper."""

from comfy_furnace import generate
from comfy_surface_pass import OUT
from comfy_coast import THREED
import json
import subprocess

PROMPTS = {
    "hoshi_rice_bale": ("One traditional tied rice straw bale, squat barrel-shaped tawara lying horizontally, "
                        "tan golden tightly bundled straw with two distinct dark braided straw ropes and round fibrous "
                        "ends. Handcrafted small late medieval Japanese storehouse prop. Centered full isolated object "
                        "on perfectly blank white, three-quarter orthographic lighting and realistic weave, no shadow."),
    "hoshi_storage_jar": ("One traditional round Japanese stoneware storage jar, old irregular brown-green "
                          "ash glaze and a small nearly black clay lid, narrow neck, broad spherical shoulders, "
                          "flat ring foot, ink-dark weathering. Complete isolated centered object on white, "
                          "slightly elevated orthographic, subtle realistic natural surface, no lettering."),
    "hoshi_paper_lantern": ("Warm ivory handmade Japanese kozo paper, flat orthographic seamless diffuse "
                           "material scan for an andon lantern, visible subtle natural long fibres, parchment "
                           "and antique creamy off-white. Square fills the image, evenly backlit, no object, "
                           "no writing, no shadows, no frame, no perspective."),
}

if __name__ == "__main__":
    generate(PROMPTS, "comfy-hoshi-storage-receipts.json", 171841)
    receipt = OUT.parent / "comfy-hoshi-storage-meshes.json"
    jobs = json.loads(receipt.read_bytes()) if receipt.is_file() else {}
    for item in ("hoshi_rice_bale","hoshi_storage_jar"):
        if item in jobs:
            continue
        run = subprocess.run([str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
                              str(OUT/f"{item}.png"),"--name",f"traveler_env_coast_{item}",
                              "--seed","143","--no-wait"],capture_output=True,text=True,check=True)
        jobs[item]=json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs,indent=2),encoding="utf-8")
        print(item,jobs[item],flush=True)
