"""Export and exercise the opt-in Natsuko mesh in RPG-Cobo, without installing art."""
import argparse
import json
import shutil
import subprocess

from PIL import Image, ImageChops

import chara3d_sheet as sheets
import playbot
from rig3d import ROOT


def roster_test():
    name, mid = "native_roster", "M202"
    steps = ["wait 750", "shot native_roster_field", r"evalf ..\..\tools\test_native_roster.sk",
             "wait 250", "shot native_roster_action"]
    logs, timed_out = playbot.launch(name, mid, *playbot.block(mid, 49, 15), steps, lead="P100", secs=45)
    log = ROOT / "_art" / "preview" / "bot" / name / "log.txt"
    if timed_out or not any("10 sampled actors" in ln for ln in log.read_text(errors="replace").splitlines()
                            if ln.startswith("[NATIVE ROSTER]")) or any("Exception in thread" in ln for ln in logs):
        raise RuntimeError(f"Native roster test failed; see {log}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", action="store_true", help="check the installed native roster in game")
    if parser.parse_args().roster:
        return roster_test()
    out = ROOT / "_art" / "preview" / "chara3d" / "native"
    out.mkdir(parents=True, exist_ok=True)
    spec = sheets.look("trav_natsuko")
    job = out / "job.json"
    job.write_text(json.dumps({
        "spec": spec, "family": sheets.family(spec), "out": str(out),
        "frames": [["atk_thrust", i, 6] for i in range(6)],
    }), encoding="utf-8")
    subprocess.run([sheets.blender_exe(), "-b", "--factory-startup", "--threads", "2",
                    "--python-exit-code", "1", "--python",
                    str(ROOT / "tools" / "blender" / "chara3d_native.py"), "--", str(job)], check=True)

    assets = ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource" / "rt_native_probe"
    assets.mkdir()
    try:
        for name in ("body.pm", "body.mdl", "armor.pm", "armor.mdl", "robe.pm", "robe.mdl",
                     "spear.pm", "spear.mdl", "rig.mot"):
            shutil.copyfile(out / name, assets / name)
        name, map_id = "native", "M202"
        step = r"evalf ..\..\tools\test_chara3d_native.sk"
        states = ("armor", "thrust", "robe")
        lines = ["wait 1000"]
        for state in states:
            lines.extend((step, "wait 700", f"shot {name}_{state}"))
        _, timed_out = playbot.launch(name, map_id, *playbot.block(map_id, 49, 15), lines, secs=60)
    finally:
        shutil.rmtree(assets)

    shots = ROOT / "_art" / "preview" / "bot" / name
    log = (shots / "log.txt").read_text(encoding="utf-8", errors="replace")
    expected = ["[NATIVE] loaded", "[NATIVE] thrust", "[NATIVE] robe and empty hands"]
    if timed_out or [line for line in log.splitlines() if line.startswith("[NATIVE]")] != expected:
        raise RuntimeError(f"Native mesh fixture did not finish: {shots / 'log.txt'}")

    # Compare only the actor's region; ambient scene or UI animation is not evidence.
    crops = []
    for state in states:
        with Image.open(shots / f"{name}_{state}.png") as image:
            crops.append(image.crop((675, 255, 835, 405)))
    for before, after in zip(crops, crops[1:]):
        changed = ImageChops.difference(before, after).convert("L").histogram()
        if sum(changed[12:]) < 200:
            raise RuntimeError("The native actor did not visibly change pose or equipment")
    page = Image.new("RGB", (480, 150))
    for i, crop in enumerate(crops):
        page.paste(crop, (160 * i, 0))
    page.resize((1440, 450), Image.Resampling.NEAREST).save(shots / "native_mesh_comparison.png")


if __name__ == "__main__":
    main()
