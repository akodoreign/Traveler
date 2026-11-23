"""Generate the Old Quarry's stone, rough tent canvas and spoil-pile reference."""

from comfy_furnace import generate
from comfy_surface_pass import OUT
from comfy_coast import THREED
import json
import subprocess

PROMPTS={
    "quarry_face": (
        "Photoreal flat orthographic game wall material scan of a weathered old limestone quarry face. "
        "Many small shallow parallel hand-cut chisel marks along irregular dull bluish gray beds, fractures "
        "with dull iron ore and green lichen. Edge to edge seamless texture, no ground, scenery or objects."
    ),
    "quarry_canvas": (
        "Seamless edge-to-edge square texture scan of coarse woven hemp sailcloth, faded light oatmeal "
        "and desaturated warm brown, a few faint darned patches and frayed dark threads, flat orthographic "
        "diffuse albedo, no pattern or writing, no objects, no floor or horizon."
    ),
    "quarry_cut_rock": (
        "One small loose spoil pile of sharply broken limestone chunks from a medieval hand-cut quarry, a handful "
        "of stacked flat rough blocks, powder and modest irregular pebble shapes underneath. Dull slate bluish "
        "gray with pale freshly broken edges. Full isolated 3D environment prop on white, three-quarter "
        "orthographic, no floor plane, no drop shadow, no lettering."
    ),
}

if __name__=="__main__":
    generate(PROMPTS,"comfy-quarry-receipts.json",317190)
    receipt=OUT.parent/"comfy-quarry-mesh.json"
    if not receipt.is_file():
        run=subprocess.run([str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),
                            str(OUT/"quarry_cut_rock.png"),"--name","traveler_env_coast_quarry_cut_rock",
                            "--seed","206","--no-wait"],capture_output=True,text=True,check=True)
        result=json.loads(run.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(result,flush=True)
