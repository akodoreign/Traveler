"""Bake and install personal sash ornaments, ink and Mitsue's alternate mask."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zlib import crc32

from chara3d_native_all import build_registry
from chara3d_sheet import blender_exe
from blender.foe_batch import plan

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / "_tools/rpgcobo-tool/project/resource"


def design(key, spec):
    identity = spec.get("model_key") or key
    seed = crc32(identity.encode())
    style = ("inro", "tassel", "gourd", "coin")[seed % 4]
    if identity == "trav_rensei":
        style = "bells"
    motifs = ("tide", "peaks", "reed", "lozenge")
    parts = {"sash": style}
    if spec.get("name", "").split(" ")[0] == "Togashi" and spec.get("head_tattoo"):
        parts["ink"] = motifs[(seed >> 8) % len(motifs)]
    if identity == "trav_mitsue":
        parts["mask"] = "shinobi"
        for costume in ("shinobi", "maid", "fox", "soldier"):
            parts[costume] = costume
        for costume in ("maid", "fox", "soldier"):
            parts[f"{costume}_head"] = costume
    return {"parts": parts, "spec": spec}


def build_jobs():
    _, _, roster = build_registry()
    jobs = {key:design(key,spec) for key,spec,_,_ in roster}
    for ep, entry in plan().items():
        if entry["recipe"] == "human":
            jobs[ep] = design(entry["source"],entry["spec"])
    return jobs


def install(stage, jobs):
    out = RESOURCE / "native_ornament"
    out.mkdir(exist_ok=True)
    index = {key:list(job["parts"]) for key,job in jobs.items()}
    names = [f"{key}_{role}.{ext}" for key,roles in index.items() for role in roles for ext in ("mdl","pm")]
    textures = set()
    for name in names:
        file = stage/name
        if not file.is_file() or file.stat().st_size < 32:
            raise ValueError(f"Missing ornament {name}")
        if file.suffix == ".mdl" and file.read_bytes()[:4] != b"SMDL":
            raise ValueError(f"Invalid model {name}")
        if file.suffix == ".pm":
            textures.update(re.findall(r'texture[0-9]+ = "(tex/[^"]+)"', file.read_text("utf8")))
    if any(not (stage / path).stat().st_size for path in textures):
        raise ValueError("Missing costume material texture")
    for name in sorted(textures):
        (out / name).parent.mkdir(exist_ok=True, parents=True)
        os.replace(stage / name, out / name)
    for name in names:
        os.replace(stage/name,out/name)
    path=stage/"index.json"
    path.write_text(json.dumps(index,indent=1)+"\n",encoding="utf-8")
    os.replace(path,out/path.name)
    print(f"Installed {len(names)//2} pieces for {len(jobs)} characters")


if __name__ == "__main__":
    jobs=build_jobs()
    with tempfile.TemporaryDirectory(dir=RESOURCE,prefix="ornament-bake-") as tmp:
        stage=Path(tmp)
        (stage/"job.json").write_text(json.dumps(jobs),encoding="utf-8")
        subprocess.run([blender_exe(),"-b","--factory-startup","--threads","2","--python-exit-code","1",
                        "--python",str(ROOT/"tools/blender/cast_ornaments.py"),"--",str(stage)],check=True)
        install(stage,jobs)

