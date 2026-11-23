"""Queue separately generated art for Kiyo's open noodle stall."""

from pathlib import Path
import json
import subprocess
import sys
import time
from uuid import uuid4

from comfy_coast import HTTP, THREED, download, response, workflow

HERE = Path(__file__).resolve().parent
JOBS = {
    "noodle_counter": "one isolated heavy rough plank counter, late Sengoku Japanese market stall, "
                      "simple rectangle, three dark cedar front boards, low sturdy square wooden trestle legs, "
                      "a thick scrubbed pale top, full object, handmade dark stained cedar",
    "iron_pot": "one isolated round dark cast-iron Japanese cauldron cooking pot with two small loop handles "
                "and an open mouth, rustic Edo precursor Sengoku cookware, charcoal black weathered iron, "
                "classic wide-bellied iron kama with flat stable foot, no liquid spilling, complete silhouette",
    "soup_bowl": "one isolated simple rustic Japanese pottery serving bowl on white, glazed warm gray "
                 "earthenware, pale tan soup inside, deep footed bowl, unadorned, 16th century, one bowl only",
    "cedar_well": "one isolated traditional rural Japanese shibori water well, Sengoku style, roughly laid "
                  "stone low circular well rim with dark old cedar cap ring, two upright timber posts with "
                  "thin overhead timber cross beam and simple straw rope, plain clay background removed",
}

REPLACEMENTS = {
    "coast_pine": "a single windswept Japanese black pine tree with a twisting salt-weathered trunk, "
                  "broad flat-tiered dark olive needle canopy, roots visible at base, late-period Japan, "
                  "isolated without ground tile, handcrafted blocky voxel 3D game plant",
    "stone_lantern": "a single squat weathered Japanese roadside stone lantern, low cut sandstone base, "
                     "open square lamp chamber and pitched cap, late Sengoku road, simple stone tan, "
                     "no surrounding scene or foundation tile",
    "road_milestone": "one rough upright pale gray roughly carved Japanese roadside milestone slab with "
                      "weathered chisel face, low moss and stones integrated at base, late Sengoku coast, "
                      "small restrained realistic voxel sculpture; no legible text",
    "castle_stone_bay": "one modular tapering stone foundation wall bay from a late 1500s Japanese "
                        "castle, uneven interlocking gray boulders, low-worked rounded natural stone, "
                        "slight battered profile, freestanding single voxel wall segment",
    "castle_roof_eave": "one modular 16th century Japanese castle roof corner piece, clean dark blue gray "
                        "rounded kawara tiles, wooden curved eave and woven wave of overlapping tiles, "
                        "complete individual architectural piece orthographic isolated",
}


def main():
    replacements = len(sys.argv)>1 and sys.argv[1]=="replacements"
    jobs = REPLACEMENTS if replacements else JOBS
    batch = "coast-replacements" if replacements else "town"
    note = HERE / f"comfy-{batch}-receipts.json"
    stage = HERE / ("replacement_concepts" if replacements else "town_concepts")
    stage.mkdir(exist_ok=True)
    identity = json.loads(note.read_bytes()) if note.is_file() else {}
    for index, (key, prompt) in enumerate(jobs.items()):
        if key in identity:
            continue
        task = workflow(key,prompt,(1671050 if replacements else 1671030)+index)
        task["7"]["inputs"]["filename_prefix"] = f"traveler_{batch}/{key}"
        ans = json.loads(response(HTTP,"/prompt",{"prompt":task,"client_id":str(uuid4())}))
        identity[key] = {"image": ans["prompt_id"]}
        note.write_text(json.dumps(identity,indent=2),encoding="utf-8")
        print(key,ans["prompt_id"],flush=True)
    while not all((stage/f"{k}.png").exists() for k in identity):
        for name, record in identity.items():
            file=stage/f"{name}.png"
            if not file.exists():
                data=download(record["image"])
                if data is not None:
                    file.write_bytes(data)
                    print("downloaded",name,flush=True)
        time.sleep(4)
    queue=json.loads(response(HTTP,"/queue"))
    if not queue["queue_running"] and not queue["queue_pending"]:
        response(HTTP,"/free",{"unload_models":True,"free_memory":True})
    meshes = tuple(jobs) if replacements else ("noodle_counter","iron_pot","soup_bowl")
    for name in meshes:
        if identity[name].get("model"):
            continue
        run=subprocess.run([str(THREED/"venv/Scripts/python.exe"),str(THREED/"queue.py"),str(stage/f"{name}.png"),
                            "--name",f"traveler_env_coast_{name}","--seed","47","--no-wait"],
                           capture_output=True,text=True,check=True)
        identity[name]["model"]=json.loads(run.stdout.strip().splitlines()[-1])
        note.write_text(json.dumps(identity,indent=2),encoding="utf-8")
        print(name,identity[name]["model"],flush=True)


if __name__=="__main__":
    main()
