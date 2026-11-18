"""Export and enumerate the supported live-skinned roster (no PNG frames)."""
import argparse
import json
import subprocess

import chara3d_all as batch
from chara3d_sheet import extra_clips, family, look
from rig3d_poses import SPECIAL, VIEWS


def proportions(spec):
    """Relative depth, height and width in Blender's character-facing coordinates."""
    reach = spec.get("scale", 1.0)
    stature = 1.0 + 0.016 * spec.get("height", 0) - (0.055 if spec.get("age") == "old" else 0)
    breadth = {"heavy": 0.09, "round": 0.09, "strongman": 0.12}.get(spec.get("build"), 0)
    width = 1.0 + breadth + 0.035 * spec.get("wide", 0)
    if spec.get("female"):
        stature -= 0.025
        width -= 0.035
    return [round(max(0.78, min(1.40, x)), 4)
            for x in (width * reach ** 0.5, stature * reach, width * reach ** 0.5)]


def verify_assets(directory, roster):
    expected = {"roster.json"}
    for key, spec in roster.items():
        expected.add(f"motion_{spec['motion']}.mot")
        for part in ("body", "outfit", *(("weapon",) if spec["weapon"] != "none" else ())):
            expected.update(f"{key}_{part}.{ext}" for ext in ("pm", "mdl"))
    missing = [name for name in sorted(expected - {"roster.json"})
               if not (directory / name).is_file() or not (directory / name).stat().st_size]
    if missing:
        raise RuntimeError(f"Native roster is missing {len(missing)} assets: {', '.join(missing[:8])}")
    for key, spec in roster.items():
        body = (directory / f"{key}_body.pm").read_text(encoding="utf-8")
        if f'motiondata = "motion_{spec["motion"]}.mot"' not in body:
            raise RuntimeError(f"{key}: body does not reference its registered motion")
    return expected


def build_registry(group=None):
    models = json.loads((batch.RESOURCE / "enemy_pic.json").read_text(encoding="utf-8"))
    registered = {}
    for model in models.values():
        if isinstance(model, dict) and model.get("pic3d"):
            registered.setdefault(model["pic3d"].rsplit("/", 1)[-1][:-4], model)
    roster = {}
    frames, jobs = {}, []
    clips, _ = batch.sheet.plan()
    for key, category in batch.roster():
        if group and category != group:
            continue
        spec = look(key)
        weapon, kin = spec.get("weapon", "none"), family(spec)
        jobs.append((key, spec, kin, weapon))
        if kin not in frames:
            frames[kin] = []
            for name, kind, count, _ in clips:
                kind = VIEWS.get(kind, (kind,))[0]
                if name in ("critical", "void_critical"):
                    kind = SPECIAL[kin][name == "void_critical"]
                frames[kin].extend((kind, i, count) for i in range(count))
            frames[kin].append(frames[kin][-1])
        extra = extra_clips()
        animations = [a for a in registered[key]["animap"] if a["id"] not in extra] + list(extra.values())
        for anim in animations:
            if any(not (0 <= anim[field] < len(frames[kin])) for field in ("st", "en", "m1", "m2")
                   if field in anim):
                raise ValueError(f"{key}: {anim['id']} uses a frame outside the native motion")
        roster[key] = {"group": category, "weapon": weapon, "head": spec.get("head", ""),
                       "animap": animations, "motion": kin, "proportions": proportions(spec)}
    return roster, frames, jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("traveler", "companion", "hireling", "cast"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify the complete deployed index and assets")
    mode.add_argument("--index-only", action="store_true", help="refresh metadata without re-exporting meshes")
    args = parser.parse_args()
    outfits = batch.RESOURCE / "native_chara"
    outfits.mkdir(exist_ok=True)
    work = batch.SHEETS.parent
    work.mkdir(parents=True, exist_ok=True)
    index = outfits / "roster.json"
    roster, frames, jobs = build_registry(args.group)
    if args.check:
        recorded = json.loads(index.read_text(encoding="utf-8"))
        if recorded != roster:
            raise SystemExit("Native roster index is out of sync with game registrations")
        expected = verify_assets(outfits, roster)
        unexpected = {p.name for p in outfits.iterdir()} - expected
        if unexpected:
            raise SystemExit(f"Unindexed native assets: {', '.join(sorted(unexpected)[:8])}")
        print(f"Verified {len(roster)} native roster entries and {len(expected)} runtime files")
        return
    if args.group and index.exists():
        roster = json.loads(index.read_text(encoding="utf-8")) | roster
    if args.index_only:
        verify_assets(outfits, roster)
        index.write_text(json.dumps(roster, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"Indexed {len(roster)} models without re-exporting geometry")
        return
    job = work / "native_roster_job.json"
    job.write_text(json.dumps({"out": str(outfits), "models": jobs, "motions": frames}), encoding="utf-8")
    log = work / "native_roster.log"
    with log.open("w", encoding="utf-8") as output:
        proc = subprocess.run([batch.c3.blender_exe(), "-b", "--factory-startup", "--threads", "4",
                               "--python-exit-code", "1", "--python",
                               str(batch.TOOLS / "blender" / "chara3d_native.py"), "--", str(job)],
                              stdout=output, stderr=subprocess.STDOUT)
    if proc.returncode:
        raise SystemExit(f"Blender export failed; see {log}")
    verify_assets(outfits, roster)
    index.write_text(json.dumps(roster, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"Exported {len(jobs)} models; {len(roster)} in {index}")


if __name__ == "__main__":
    main()
