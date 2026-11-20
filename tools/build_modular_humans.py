"""Prepare and stage the separate native human pieces without installing them."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

from blender.foe_batch import plan as plan_foes
from bust_skin import native_skin
from chara3d_all import RESOURCE
from chara3d_native_all import build_registry
from chara3d_sheet import blender_exe


def install_stage(stage, native):
    """Validate a complete set of references before publishing its registrations."""
    staged = json.loads((stage / "index.json").read_text(encoding="utf8"))
    names = set()
    for key, spec in staged.items():
        base = spec["base"]
        body = stage / f"{key}.pm"
        if base not in {"shared_male", "shared_female"} or f'modeldata = "{base}.mdl"' not in body.read_text("utf8"):
            raise ValueError(f"{key} does not use a shared body mesh")
        names.update((body.name, f"{base}.mdl"))
        for role, part in spec.items():
            if role == "base":
                continue
            descriptor = stage / f"{part}.pm"
            names.update((descriptor.name, f"{part}.mdl"))
            names.update(re.findall(r'texture[0-9]+ = "(tex/[^"]+)"', descriptor.read_text("utf8")))
    for name in sorted(names):
        if not (stage / name).stat().st_size:
            raise ValueError(f"Empty staged human asset: {name}")
    native.mkdir(exist_ok=True)
    index = native / "index.json"
    recorded = json.loads(index.read_text("utf8")) if index.exists() else {}
    for key, spec in staged.items():
        recent = recorded.get(key, {}).get("face", "")
        if recent.endswith("_portrait_face") and (native / f"{recent}.pm").is_file():
            spec["face"] = recent
    for name in sorted(names):
        target = native / name
        target.parent.mkdir(exist_ok=True, parents=True)
        shutil.copyfile(stage / name, target)
    merged = recorded | staged
    temporary = index.with_suffix(".tmp")
    temporary.write_text(json.dumps(merged, indent=1) + "\n", encoding="utf8")
    temporary.replace(index)
    print(f"Installed {len(staged)} modular humans. Total indexed: {len(merged)}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    parser.add_argument("actors", nargs="*")
    parser.add_argument("--foes", action="store_true", help="stage human battle opponents")
    parser.add_argument("--body-pack", type=Path, help="use the two generated body meshes and their descriptors")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--job-only", action="store_true")
    mode.add_argument("--install-stage", action="store_true")
    args = parser.parse_args()
    if args.install_stage:
        install_stage(args.out, RESOURCE / "native_human")
        return
    _, _, roster = build_registry()
    chosen = set(args.actors)
    foes = {}
    if args.foes:
        for key, entry in plan_foes().items():
            if entry["recipe"] != "human":
                continue
            spec = entry["spec"]
            actor = spec.get("model_key")
            if actor and (skin := native_skin(RESOURCE, actor, spec)) is not None:
                spec["skin"] = skin
            foes[key] = entry
    missing = chosen - {row[0] for row in roster}
    if args.foes:
        missing = chosen - foes.keys()
    if missing:
        parser.error(f"Unknown native actors: {', '.join(sorted(missing))}")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    job = out / "job.json"
    models = [] if args.foes else [row for row in roster if not chosen or row[0] in chosen]
    foes = {key: item for key, item in foes.items() if not chosen or key in chosen}
    job.write_text(json.dumps({"out": str(out), "models": models, "foes": foes,
                               "body_pack": str(args.body_pack.resolve()) if args.body_pack else None}), encoding="utf8")
    if not args.job_only:
        script = Path(__file__).parent / "blender/modular_humans.py"
        subprocess.run([blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1",
                        "--python", str(script), "--", str(job)], check=True)


if __name__ == "__main__":
    main()
