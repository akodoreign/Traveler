"""Author the teahouse's woven surfaces, paper art, and original teaware."""

from comfy_furnace import generate
from comfy_surface_pass import OUT
from comfy_coast import THREED
import json
import subprocess

PROMPTS={
    "hoshi_tatami": (
        "Edge-to-edge realistic square diffuse texture scan of Japanese tatami igusa woven rush fiber; close flat "
        "orthographic top-down view, fine tightly aligned straw reeds and subtle irregular woven crossing, "
        "olive straw gold with slightly green dried rush, natural soft even light, no border, no object or text."
    ),
    "hoshi_tea_scroll": (
        "An original vertical-format monochrome ink wash hanging scroll painting on antique warm ivory mulberry "
        "paper. Spare brushwork depicts one rocky headland, two pine silhouettes and mist over a quiet cove, "
        "large empty pale space above, softly aged Japanese painted paper. No mount, no frame, no writing, no seal."
    ),
    "hoshi_tea_bowl": (
        "One Japanese stoneware tea bowl with black-brown irregular old ash glaze giving way to muted ochre "
        "earthen body at the bottom, set on a short rounded foot, softly uneven open rim. An utterly empty bowl "
        "showing its interior shape. Isolated full object on pure white, no floor plane, orthographic three quarter view."
    ),
    "hoshi_tea_kettle": (
        "One squat unadorned old Japanese round cast iron tea kettle with a simple low rounded lid and curved "
        "overhead iron handle, subtle spout, no bright ornament, soot-dark rough patina. Complete isolated "
        "prop on matte pure white, no floor plane, no chimney or stand, three-quarter orthographic asset view."
    ),
}

if __name__=="__main__":
    generate(PROMPTS,"comfy-hoshi-tea-receipts.json",124006)
    receipt=OUT.parent/"comfy-hoshi-tea-meshes.json"
    jobs=json.loads(receipt.read_bytes()) if receipt.is_file() else {}
    for name in ("hoshi_tea_bowl","hoshi_tea_kettle"):
        if name in jobs:
            continue
        run=subprocess.run([str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
                            str(OUT/f"{name}.png"),"--name",f"traveler_env_coast_{name}",
                            "--seed","43","--no-wait"],capture_output=True,text=True,check=True)
        jobs[name]=json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs,indent=2),encoding="utf-8")
        print(name,jobs[name],flush=True)
