"""Queue original assets for the Shinomen gate, its smith, and the Shadowlands arenas."""

import json
import subprocess

from comfy_coast import THREED
from comfy_furnace import generate
from comfy_surface_pass import HERE, OUT


PROMPTS = {
    "shinomen_watch_drum": (
        "One outdoor Japanese Sengoku military signal drum on a short heavy timber trestle. "
        "Round pale weathered hide faces, cylindrical dark lacquered cedar body, braided "
        "dark navy lacing, handmade iron tacks and scuffed posts. Single isolated complete "
        "object, orthographic three-quarter view on pure white, no ground, figures, text or shadow."
    ),
    "shinomen_smith_anvil": (
        "One compact Japanese sixteenth-century smithing block: broad charcoal gray squared "
        "iron anvil set into the head of a deeply split heavy hardwood stump with two iron "
        "bands. Scale and burn stains, stable flat foot, fully visible isolated on pure white, "
        "game asset, orthographic three-quarter view, no other objects, ground, text or shadow."
    ),
    "shinomen_covered_supplies": (
        "Single waist-high set of stacked rectangular cedar supply crates, bound with rice-straw "
        "rope and half-covered with a rough dark indigo canvas tied down at the corners. Bit of "
        "exposed aged end grain, complete isolated Japanese military outpost game prop, orthographic "
        "three-quarter view on white, no ground plane, shadow, signs, figures or scenery."
    ),
    "shadowlands_oni_bones": (
        "One wide low scatter of weathered large fantasy demon bones, three arched rib fragments and "
        "a large broken horn embedded together in clumped ash. Matte aged gray ivory and dark etched "
        "weathering, no flesh or gore. Freestanding prop orthographic three-quarter view on a pure white "
        "background, full compact object visible, no scene, text, people or shadow."
    ),
    "shadowlands_burnt_stump": (
        "One blackened massive old Japanese cypress stump splintered by a lightning strike, "
        "charcoal cracked dry bark with a few twisted roots, split tall uneven silhouette, "
        "subtle rusty mineral grit. Complete freestanding waste prop on white, slightly elevated "
        "orthographic three-quarter view, no plants, lighting effects, text, ground plane or shadow."
    ),
    "shadowlands_blackpitch": (
        "Square strictly overhead flat diffuse game material, still pitch-black tar crust broken "
        "into subtly warped scabs with thin charcoal silver vein cracks and matte oily brown around "
        "the edges, even light, no strong highlights, no scenery, no props or perspective. Edge to edge."
    ),
}
MODELS = tuple(PROMPTS)[:-1]


def queue_meshes(prompts, models, project, image_seed, mesh_seed):
    generate(prompts, f"comfy-{project}-images.json", image_seed)
    receipt = HERE / f"comfy-{project}-meshes.json"
    jobs = json.loads(receipt.read_bytes()) if receipt.is_file() else {}
    for seed, name in enumerate(models, mesh_seed):
        if name in jobs:
            continue
        result = subprocess.run([
            str(THREED / "venv/Scripts/python.exe"), str(THREED / "queue.py"),
            str(OUT / f"{name}.png"), "--name", f"traveler_env_coast_{name}",
            "--seed", str(seed), "--no-wait",
        ], capture_output=True, text=True, check=True)
        jobs[name] = json.loads(result.stdout.strip().splitlines()[-1])
        receipt.write_text(json.dumps(jobs, indent=2), encoding="utf8")
        print(f"{name} {jobs[name]['prompt_id']}", flush=True)


if __name__ == "__main__":
    queue_meshes(PROMPTS, MODELS, "shinomen-gate", 113729, 421)
