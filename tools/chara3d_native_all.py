"""Export and enumerate the supported live-skinned roster (no PNG frames)."""
import argparse
import json
import subprocess
from zlib import crc32

import chara3d_all as batch
from bust_skin import native_skin
from chara3d_sheet import extra_clips, family, look
from rig3d_poses import SPECIAL, VIEWS


TRAVELER_STATURE = {"side_yosai": 1.16, "trav_natsuko": 1.12, "trav_tamotsu": 1.08}
SAME_PERSON = {"side_kage_ch3": "side_kage", "side_kafu_nosword": "side_kafu"}


def proportions(key):
    """Relative depth, height and width, with neutral variation where looks omit size."""
    key = SAME_PERSON.get(key, key)
    spec = look(key)
    seed = crc32(key.encode("ascii"))
    height = 0.022 * spec["height"] if "height" in spec else (seed % 15 - 7) * 0.006
    wide = 0.040 * spec["wide"] if "wide" in spec else (seed // 15 % 11 - 5) * 0.009
    size = spec.get("scale", 1.0) - 1.0
    stature = 1.0 + height + 0.26 * size
    if spec.get("age") == "old":
        stature -= 0.06
    if spec.get("female"):
        stature -= 0.025
    stature = TRAVELER_STATURE.get(key, stature)
    if key == "side_kisada":
        stature = 1.27  # The Great Bear's authored look is the tallest.
    breadth, thickness = {"heavy": (0.09, 0.08), "round": (0.08, 0.15),
                          "strongman": (0.13, 0.10)}.get(spec.get("build"), (0.0, 0.0))
    frame = 1.0 + wide + 0.22 * size + 0.16 * (spec.get("mass", 1.0) - 1.0)
    if spec.get("female"):
        frame -= 0.03
    return [round(max(0.78, min(1.40, x)), 4)
            for x in (frame + thickness, stature, frame + breadth)]


def verify_assets(directory, roster):
    expected = {"roster.json"}
    for key, spec in roster.items():
        expected.add(f"motion_{spec['motion']}.mot")
        parts = ["body", "outfit"]
        if spec["weapon"] != "none":
            parts.append("weapon")
        if spec.get("mask"):
            parts.append("mask")
        for part in parts:
            expected.update(f"{key}_{part}.{ext}" for ext in ("pm", "mdl"))
    missing = [name for name in sorted(expected - {"roster.json"})
               if not (directory / name).is_file() or not (directory / name).stat().st_size]
    if missing:
        raise RuntimeError(f"Native roster is missing {len(missing)} assets: {', '.join(missing[:8])}")
    for key, spec in roster.items():
        body = (directory / f"{key}_body.pm").read_text(encoding="utf-8")
        if f'motiondata = "motion_{spec["motion"]}.mot"' not in body:
            raise RuntimeError(f"{key}: body does not reference its registered motion")
    for part in list(expected):
        if part.endswith(".pm"):
            descriptor = (directory / part).read_text(encoding="utf-8")
            for line in descriptor.splitlines():
                if ' = "tex/head_' in line:
                    texture = line.split('"')[1]
                    if not (directory / texture).is_file():
                        raise RuntimeError(f"{part}: missing head texture {texture}")
                    expected.add(texture)
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
        tone = native_skin(batch.RESOURCE, key, spec)
        if tone is not None:
            spec["skin"] = tone
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
        # Sprite ranges end at the next block; native interpolation can blend into it.
        motion = frames[kin]
        animations = [
            dict(anim, en=anim["en"] - 1)
            if anim.get("loop") and motion[anim["st"]][0] == "idle8"
            and motion[anim["en"]][0] == "walk8" else anim
            for anim in animations
        ]
        roster[key] = {"group": category, "weapon": weapon, "head": spec.get("head", ""),
                       "animap": animations, "motion": kin, "proportions": proportions(key)}
        if spec.get("mask"):
            roster[key]["mask"] = spec["mask"]
    return roster, frames, jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("traveler", "companion", "hireling", "cast"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify the complete deployed index and assets")
    mode.add_argument("--index-only", action="store_true", help="refresh metadata without re-exporting meshes")
    mode.add_argument("--bust-skin", action="store_true", help="re-export only bodies with sampled bust colors")
    mode.add_argument("--accessories", action="store_true", help="refresh costume pieces, body ornaments and outfit fit")
    mode.add_argument("--head-surfaces", action="store_true", help="refresh hair, headbands and authored helmet meshes")
    mode.add_argument("--outfits-only", action="store_true", help="refresh outfit meshes without regenerating bodies or motion")
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
        unexpected = {p.relative_to(outfits).as_posix() for p in outfits.rglob("*") if p.is_file()} - expected
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
    if args.bust_skin:
        jobs = [job for job in jobs if native_skin(batch.RESOURCE, job[0], look(job[0])) is not None]
    job.write_text(json.dumps({"out": str(outfits), "models": jobs, "motions": frames,
                               "body_only": args.bust_skin, "accessories": args.accessories,
                               "head_surfaces": args.head_surfaces,
                               "outfits_only": args.outfits_only}), encoding="utf-8")
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
    print(f"Exported {len(jobs)} {'bodies' if args.bust_skin else 'models'}; {len(roster)} in {index}")


if __name__ == "__main__":
    main()
