"""Export and enumerate the supported live-skinned roster (no PNG frames)."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from zlib import crc32

import chara3d_all as batch
from bust_skin import native_skin
from chara3d_sheet import extra_clips, family, look
from native_eye_materials import two_sided_eyes
from rig3d_poses import SPECIAL, VIEWS
from weapon_catalog import FAMILIES


# Depth, stature and breadth of the shared skinned body and its fitted parts.
PLAYABLE_PROPORTIONS = {
    "trav_natsuko": (0.99, 1.145, 1.025),
    "trav_rensei": (0.97, 1.022, 0.99),
    "trav_gendo": (0.945, 1.044, 0.95),
    "trav_shizue": (1.005, 0.933, 1.035),
    "trav_haruki": (0.955, 0.978, 0.955),
    "trav_mitsue": (0.965, 0.969, 0.965),
    "trav_tamotsu": (1.14, 1.08, 1.075),
    "trav_sayo": (1.0, 0.953, 1.015),
    "side_sachiko": (1.15, 1.0618, 1.16),
    "side_ryoichi": (0.985, 1.0, 1.0),
    "side_goro": (1.04, 1.044, 1.06),
    "side_michio": (0.965, 0.982, 0.98),
    "side_gonta": (1.355, 1.09, 1.37),
    "side_kage": (0.975, 1.022, 0.99),
    "side_gusai": (1.045, 1.036, 1.065),
    "side_lionrider": (0.975, 0.988, 1.005),
    "side_kafu": (1.065, 1.0, 1.085),
    "side_hiruto": (0.965, 0.962, 0.975),
    "side_ashimita": (1.035, 1.036, 1.055),
    "side_yosai": (1.08, 1.205, 1.11),
    "side_hayato": (1.01, 0.964, 1.02),
    "side_ushimo": (1.06, 0.97, 1.08),
    "side_sanro": (1.025, 0.912, 1.01),
    "side_rui": (1.005, 0.957, 1.025),
    "side_kasiko": (0.985, 0.931, 0.985),
    "side_akodorin": (0.94, 0.981, 0.955),
    "side_haku": (1.045, 0.978, 1.055),
    "side_ryuko": (1.01, 0.969, 1.035),
    "side_hanae": (1.045, 0.999, 1.07),
}
SAME_PERSON = {"side_kage_ch3": "side_kage", "side_kafu_nosword": "side_kafu"}


def proportions(key):
    """Relative depth, height and width, with neutral variation where looks omit size."""
    key = SAME_PERSON.get(key, key)
    if key in PLAYABLE_PROPORTIONS:
        return list(PLAYABLE_PROPORTIONS[key])
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
    if (directory / "defeat/index.json").is_file():
        expected.add("defeat/index.json")
        expected.update(f"defeat/{family}.mot" for family in set(FAMILIES.values()) | {"iai"})
    fidget_index = directory / "fidget/index.json"
    if fidget_index.is_file():
        fidgets = json.loads(fidget_index.read_text(encoding="utf-8"))
        expected.add("fidget/index.json")
        expected.update(f"fidget/{family}.mot" for family in set(FAMILIES.values()) | {"iai"})
        props = {clip["prop"] for clip in fidgets["clips"].values() if "prop" in clip}
        if any(clip.get("satchel") for clip in fidgets["clips"].values()):
            props.add("satchel")
        expected.update(f"fidget/{prop}.{ext}" for prop in props for ext in ("pm", "mdl"))
    if (directory / "kakita_void.mot").is_file():
        expected.add("kakita_void.mot")
    if (directory / "spear_void.mot").is_file():
        expected.add("spear_void.mot")
    if (directory / "heart_listens.mot").is_file():
        expected.add("heart_listens.mot")
    if (directory / "ide_song.mot").is_file():
        expected.add("ide_song.mot")
    if (directory / "tattoo_morph.mot").is_file():
        expected.add("tattoo_morph.mot")
    if (directory / "void_bolt_release.mot").is_file():
        expected.add("void_bolt_release.mot")
    if (directory / "lion_courage.mot").is_file():
        expected.add("lion_courage.mot")
    if (directory / "shosuro_throw.mot").is_file():
        expected.add("shosuro_throw.mot")
    if (directory / "sayo_remedy.mot").is_file():
        expected.add("sayo_remedy.mot")
        expected.update({"sayo_mortar.pm", "sayo_mortar.mdl", "sayo_pestle.pm", "sayo_pestle.mdl"})
    if (directory / "gendo_deduce.mot").is_file():
        expected.add("gendo_deduce.mot")
        expected.update({"deduce_brush.pm", "deduce_brush.mdl"})
    if (directory / "isawa_rising.mot").is_file():
        expected.add("isawa_rising.mot")
    ability = directory / "ability"
    for index_name, bank in (("spell-index.json", "spells"), ("school-index.json", "school"),
                             ("support-index.json", "support")):
        if (ability / index_name).is_file():
            expected.add(f"ability/{index_name}")
            expected.update(f"ability/{bank}_{family}.mot" for family in set(FAMILIES.values()) | {"iai"})
    if (directory / "shosuro_star.pm").is_file():
        expected.update({"shosuro_star.pm", "shosuro_star.mdl"})
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
    from human_anatomy import anatomy_group

    jobs.sort(key=lambda job: (*anatomy_group(job[1]), job[0]))
    return roster, frames, jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("traveler", "companion", "hireling", "cast"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify the complete deployed index and assets")
    mode.add_argument("--index-only", action="store_true", help="refresh metadata without re-exporting meshes")
    mode.add_argument("--eye-materials", action="store_true", help="repair eye culling without re-exporting meshes")
    mode.add_argument("--bust-skin", action="store_true", help="re-export only bodies with sampled bust colors")
    mode.add_argument("--outfit-clans", nargs="+", help="refresh default outfits for the named clans")
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
    if args.eye_materials:
        repairs = {}
        for key, spec, _, _ in jobs:
            path = outfits / f"{key}_body.pm"
            original = path.read_bytes()
            updated = two_sided_eyes(original.decode("utf-8"), spec).encode("utf-8")
            if updated != original:
                repairs[path] = updated
        for path, updated in repairs.items():
            path.write_bytes(updated)
        print(f"Checked eye materials for {len(jobs)} bodies; updated {len(repairs)} descriptors")
        return
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
    outfits_only = bool(args.outfit_clans or args.outfits_only)
    stem = "native_outfit" if outfits_only else "native_roster"
    job = work / f"{stem}_job.json"
    if args.bust_skin:
        jobs = [job for job in jobs if native_skin(batch.RESOURCE, job[0], look(job[0])) is not None]
    if args.outfit_clans:
        clans = {spec.get("clan", spec.get("mon")) for _, spec, _, _ in jobs}
        unknown = set(args.outfit_clans) - clans
        if unknown:
            parser.error(f"No actors in clans: {', '.join(sorted(unknown))}")
        jobs = [job for job in jobs if job[1].get("clan", job[1].get("mon")) in args.outfit_clans]
    def export(destination, job, log):
        job.write_text(json.dumps({"out": str(destination), "models": jobs, "motions": frames,
                                   "body_only": args.bust_skin, "accessories": args.accessories,
                                   "head_surfaces": args.head_surfaces, "outfits_only": outfits_only}),
                       encoding="utf-8")
        command = [batch.c3.blender_exe(), "-b", "--factory-startup", "--threads", "4",
                   "--python-exit-code", "1", "--python",
                   str(batch.TOOLS / "blender" / "chara3d_native.py"), "--", str(job)]
        print(f"Exporting {len(jobs)} entries; full log: {log}", flush=True)
        with log.open("w", encoding="utf-8") as output, subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace") as proc:
            for line in proc.stdout:
                output.write(line)
                if line.startswith("OUTFIT "):
                    output.flush()
                    print(line.rstrip(), flush=True)
            if proc.wait():
                raise SystemExit(f"Blender export failed; see {log}")

    if outfits_only:
        with tempfile.TemporaryDirectory(prefix="outfit-", dir=work) as temporary:
            stage = Path(temporary)
            export(stage, stage / "job.json", work / f"{stage.name}.log")
            files = [stage / f"{key}_outfit.{ext}" for key, *_ in jobs for ext in ("pm", "mdl")]
            if not all(path.is_file() and path.stat().st_size for path in files):
                raise SystemExit("Incomplete staged outfit export; runtime outfits were not changed")
            for path in files:
                path.replace(outfits / path.name)
            for path in (stage / "tex").iterdir():
                path.replace(outfits / "tex" / path.name)
    else:
        export(outfits, job, work / f"{stem}.log")
    verify_assets(outfits, roster)
    index.write_text(json.dumps(roster, indent=1) + "\n", encoding="utf-8", newline="\n")
    part = "outfits" if outfits_only else "bodies" if args.bust_skin else "models"
    print(f"Exported {len(jobs)} {part}; {len(roster)} in {index}")


if __name__ == "__main__":
    main()
