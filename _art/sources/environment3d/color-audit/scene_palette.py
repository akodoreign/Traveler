"""Prepare and install a map-local native material color pass."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from publish_castle_gates import resource_files


@dataclass(frozen=True)
class Tone:
    color: tuple[int, int, int]
    mix: float
    contrast: float = 1.0
    mask: str = ""
    mottle: float = 0.0


# A consistent hue hierarchy within each environment gives the strong notes room.
# Shadowlands rock is cool slate, its routes ochre, and the taint is dried wine.
WASTE_TONES = {
    "waste_earth": Tone((41, 24, 42), 0.94, 1.19, mottle=9.0),
    "waste_taint": Tone((62, 13, 16), 0.97, 1.30, mottle=13.0),
    "waste_ash": Tone((69, 79, 108), 0.78, 1.08),
    "waste_trail": Tone((134, 101, 64), 0.76, 1.05),
    "waste_shale": Tone((44, 54, 84), 0.78, 1.14),
    "shadowlands_ochre_ash": Tone((133, 99, 68), 0.74, 1.09),
    "shadowlands_blackpitch": Tone((30, 26, 53), 0.72, 1.14),
    "shadowlands_obsidian_tree": Tone((23, 30, 51), 0.45, 1.02),
    "shadowlands_shards": Tone((48, 78, 118), 0.66, 1.13),
    "hiruma_ash": Tone((77, 55, 88), 0.67, 1.10),
    "hiruma_courtyard": Tone((113, 84, 64), 0.60, 1.02),
    "hiruma_ishi": Tone((79, 85, 111), 0.65, 1.11),
    "hiruma_scorched_cedar": Tone((65, 34, 42), 0.67, 1.14),
}
# Deep indigo fabric gives these rooms an accent distinct from their amber wood.
IUCHI_TONES = {
    "iuchi_beam": Tone((63, 38, 50), 0.52, 1.13),
    "iuchi_board_a": Tone((121, 77, 49), 0.73, 1.10),
    "iuchi_board_b": Tone((143, 94, 61), 0.70, 1.09),
    "iuchi_indigo": Tone((56, 48, 140), 0.83, 1.10),
    "iuchi_bronze": Tone((156, 113, 54), 0.72, 1.10),
    "iuchi_siege_canvas": Tone((66, 45, 123), 0.93, 1.12),
    "iuchi_gale_scoured": Tone((174, 143, 108), 0.65, 1.09),
    "iuchi_gale_slate": Tone((32, 55, 92), 0.79, 1.10),
    "iuchi_gale_ridge": Tone((56, 73, 115), 0.80, 1.07),
    "iuchi_gale_shale": Tone((24, 34, 65), 0.75, 1.07),
    "iuchi_siege_earth": Tone((125, 77, 55), 0.57, 1.06),
    "iuchi_storm_mineral": Tone((55, 67, 114), 0.81, 1.08),
    "iuchi_storm_cloth": Tone((52, 35, 108), 0.88, 1.12),
    "iuchi_tower_screen": Tone((53, 66, 133), 0.65, 1.09, "blue"),
    "iuchi_canvas": Tone((38, 92, 58), 0.65, 1.11),
    "iuchi_jade": Tone((34, 133, 86), 0.80, 1.11),
    "iuchi_jade_seam": Tone((49, 156, 95), 0.68, 1.08, "green"),
}
AUTUMN_TONES = {
    "autumn_brocade": Tone((148, 22, 48), 0.82, 1.10),
    "autumn_soshi_lacquer": Tone((86, 25, 43), 0.83, 1.12),
    "dragon_inn_heartwood": Tone((110, 55, 43), 0.61, 1.05),
    "dragon_inn_floor": Tone((109, 66, 47), 0.50, 1.08),
    "dragon_inn_floor_medium": Tone((120, 73, 51), 0.50, 1.08),
    "dragon_inn_floor_light": Tone((143, 94, 64), 0.57, 1.06),
    "autumn_timber": Tone((96, 52, 38), 0.68, 1.08),
    "autumn_roof": Tone((66, 48, 99), 0.84, 1.10),
    "autumn_road": Tone((133, 83, 52), 0.66, 1.06),
    "autumn_leaf_bed": Tone((120, 73, 45), 0.57, 1.05),
    "ojatara_canvas_indigo": Tone((35, 58, 134), 0.74, 1.11),
    "ojatara_canvas_oxide": Tone((149, 50, 41), 0.71, 1.11),
}

WASTE = ("M171", "M172", "M173", "M174", "M175", "M176", "M177", "M458", "M459",
         "M460", "M461", "M462", "M463", "M465", "M466", "M467", "M468", "M469",
         "M808", "M817", "M818")
IUCHI = ("M400", "M401", "M402", "M404", "M405", "M406", "M407", "M408", "M409",
         "M410", "M411", "M412", "M878", "M879", "M880", "M881", "M882")
AUTUMN = ("M369", "M371", "M387", "M394", "M396")
SETS = {
    "shadowlands": (WASTE, WASTE_TONES, {"shadowlands_obsidian_tree", "shadowlands_shards",
                                       "hiruma_hall_screen"}),
    "iuchi": (IUCHI, IUCHI_TONES, {"iuchi_tower_screen", "iuchi_fitted_andon", "iuchi_notes_table",
                                  "iuchi_siege_pavilion", "iuchi_dragon_shelter",
                                  "iuchi_dragon_command", "iuchi_dragon_standard",
                                  "iuchi_storm_hanging", "iuchi_deep_stone_shrine", "iuchi_jade_seam"}),
    "autumn": (AUTUMN, AUTUMN_TONES, {"autumn_soshi_partition", "autumn_soshi_writing_desk",
                                      "ojatara_refugee_shelter_indigo",
                                      "ojatara_refugee_shelter_oxide", "ojatara_command_shelter"}),
}
BASE = Path("project/resource/native_environment")
CATALOG = Path("project/data/map.json")
MODEL = re.compile(r'^modeldata = "([^"]+)"', re.M)
TEX = re.compile(r'(?m)^([ \t]*texture0 = ")tex/([^"]+)(")')
LUMA = np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
SUFFIX = "_story_palette"
DRIED_SUFFIX = "_story_palette_dried"


def digest(data):
    return sha256(data).hexdigest()


def json_bytes(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf8")


def read_json(path):
    return json.loads(path.read_bytes())


def periodic_mottle(shape):
    """Interpolate odd-frequency noise on a wrapped texture grid."""
    rng = np.random.default_rng(2929)
    result = np.zeros(shape, dtype=np.float32)
    for count, weight in ((5, .50), (11, .32), (29, .18)):
        field = rng.uniform(-1., 1., (count, count)).astype(np.float32)
        row, col = (np.arange(size, dtype=np.float32) * (count / size) for size in shape)
        y, x = np.floor(row).astype(int), np.floor(col).astype(int)
        fy, fx = row-y, col-x
        fy = (fy**2*(3-2*fy))[:, None]
        fx = (fx**2*(3-2*fx))[None, :]
        low = field[y[:, None], x[None, :]]*(1-fx) + field[y[:, None], (x+1)[None, :] % count]*fx
        high = field[(y+1)[:, None] % count, x[None, :]]*(1-fx) + field[(y+1)[:, None] % count, (x+1)[None, :] % count]*fx
        result += weight * (low*(1-fy) + high*fy)
    return np.clip((result - np.median(result)) / .48, -1.35, 1.35)


def palette_texture(source, tone):
    image = Image.open(io.BytesIO(source))
    rgba = np.asarray(image.convert("RGBA"), dtype=np.float32)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    luma = rgb @ LUMA
    target = np.asarray(tone.color, dtype=np.float32)
    opaque = alpha > 112
    if tone.mask == "green":
        strength = np.clip((rgb[:, :, 1] - rgb[:, :, 0] - 4) / 38, 0, 1)
        chosen = opaque & (strength > .6)
    elif tone.mask == "blue":
        strength = np.clip((rgb[:, :, 2] - rgb[:, :, 0] - 6) / 42, 0, 1)
        chosen = opaque & (strength > .6)
    else:
        strength = np.ones_like(alpha)
        chosen = opaque
    center = float(np.median(luma[chosen if np.any(chosen) else opaque]))
    lowlight = np.clip((luma + .4 * center) / max(center, 15), .0, 1.)
    highlights = np.clip((253 - luma) / 85, .0, 1.)
    mix = tone.mix * strength * lowlight * highlights
    wash = target + ((luma - center) * tone.contrast)[:, :, None]
    # Keep paint/grain variation around the color anchor and leave very bright edges alone.
    original_chroma = rgb - luma[:, :, None]
    center_chroma = np.median(original_chroma[chosen if np.any(chosen) else opaque], axis=0)
    wash += .24 * (original_chroma - center_chroma)
    if tone.mottle:
        mottle = periodic_mottle(luma.shape)
        wash += (tone.mottle * mottle)[:, :, None] * np.array((1.26, .78, .62), np.float32)
    revised = np.clip(np.round(rgb + mix[:, :, None] * (wash - rgb)), 0, 255).astype(np.uint8)
    altered = Image.fromarray(revised, "RGB")
    if "A" in image.getbands() or "transparency" in image.info:
        altered.putalpha(Image.fromarray(alpha.astype(np.uint8), "L"))
    if altered.size != image.size:
        raise ValueError("A texture changed dimensions")
    buf = io.BytesIO()
    altered.save(buf, format="PNG", compress_level=6)
    final_med = np.median(revised[chosen if np.any(chosen) else opaque], axis=0)
    old_med = np.median(rgb[chosen if np.any(chosen) else opaque], axis=0)
    return buf.getvalue(), {
        "size": list(image.size), "before_rgb": old_med.round().astype(int).tolist(),
        "after_rgb": final_med.round().astype(int).tolist(), "alpha": altered.mode in ("RGBA", "LA")
    }


def prepare(repo, bundle, groups):
    live = repo / "_tools/rpgcobo-tool"
    root = live / BASE
    rows = read_json(root / "index.json")
    map_catalog = read_json(live / CATALOG)
    result = {}
    originals = {}
    outputs = {}
    materials = {}
    substitutions = {}
    memo = {}

    def baseline(path):
        data = (root / path).read_bytes()
        originals[path] = digest(data)
        return data

    def variant(name, tones):
        if name in memo:
            return memo[name]
        desc = baseline(name + ".pm").decode("utf-8")
        dried = any((grade := tones.get(Path(tex).stem)) and grade.mottle for _,tex,_ in TEX.findall(desc))

        def change_texture(match):
            path = match[2]
            tone = tones.get(Path(path).stem)
            if tone is None:
                return match[0]
            new_path = Path(path).stem + (DRIED_SUFFIX if tone.mottle else SUFFIX) + ".png"
            if "tex/" + new_path not in outputs:
                revised, sample = palette_texture(baseline("tex/" + path), tone)
                outputs["tex/" + new_path] = revised
                materials[path] = sample
            return match[1] + 'tex/' + new_path + match[3]

        revised = TEX.sub(change_texture, desc)
        if revised == desc:
            memo[name] = name
            return name
        clone = name + (DRIED_SUFFIX if dried else SUFFIX)
        model = MODEL.search(desc)[1]
        originals[model] = digest((root / model).read_bytes())
        # Point at the identical mesh to keep vertex, lighting and collision coordinates fixed.
        outputs[clone + ".pm"] = revised.encode("utf-8")
        substitutions[name] = clone
        memo[name] = clone
        return clone

    for group in groups:
        maps, tones, allowed_props = SETS[group]
        for mid in maps:
            row = rows[mid]
            revised = dict(row)
            revised["terrain"] = variant(row["terrain"], tones)
            revised["placements"] = [
                [variant(p[0], tones), *p[1:]] if p[0] in allowed_props else p
                for p in row["placements"]
            ]
            if revised == row:
                continue
            assert {k: v for k, v in row.items() if k not in ("terrain", "placements")} == {
                k: v for k, v in revised.items() if k not in ("terrain", "placements")
            }
            assert len(row["placements"]) == len(revised["placements"])
            assert all(after[1:] == before[1:] for before, after in zip(row["placements"], revised["placements"]))
            world = live / "project/data/mapdata" / f"{mid}.bw"
            result[mid] = {
                "name": map_catalog[mid].get("name", mid),
                "before": row, "after": revised, "world": digest(world.read_bytes()),
                "story": digest(json_bytes(map_catalog[mid]))
            }
    if not result:
        raise ValueError("No map material changes")
    bundle.mkdir(parents=True, exist_ok=True)
    for path, data in outputs.items():
        dest = bundle / "files" / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    info = {
        "groups": list(groups), "maps": result, "source": originals,
        "files": {path: digest(data) for path, data in outputs.items()},
        "materials": materials, "aliases": substitutions
    }
    (bundle / "palette-proof.json").write_text(json.dumps(info, indent=2) + "\n", "utf-8")
    print(f"Prepared {len(result)} maps, {len(materials)} textures and {len(substitutions)} descriptor aliases")


def replace_existing(path, data):
    with NamedTemporaryFile(dir=path.parent, prefix=".palette-", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(data)
        except BaseException:
            handle.close()
            temporary.unlink()
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_once(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Conflicting shared asset {path}")
        return False
    with path.open("xb") as stream:
        stream.write(data)
    return True


def apply(repo, profile, bundle, publish=False):
    live = repo / "_tools/rpgcobo-tool"
    live_root = live / BASE
    profile_root = profile / BASE
    if live == profile:
        raise ValueError("Choose an isolated game profile")
    info = read_json(bundle / "palette-proof.json")
    maps = info["maps"]
    live_index = read_json(live_root / "index.json")
    live_story = read_json(live / CATALOG)
    for name, expected in info["source"].items():
        if digest((live_root / name).read_bytes()) != expected:
            raise ValueError(f"Shared source asset differs from the review {name}")
    after = {mid: row["after"] for mid, row in maps.items()}
    payload = {name: (bundle / "files" / name).read_bytes() for name in info["files"]}
    for name, data in payload.items():
        if digest(data) != info["files"][name]:
            raise ValueError(f"Prepared color asset differs from its receipt {name}")
    for mid, row in maps.items():
        if live_index[mid] not in (row["before"], row["after"]):
            raise ValueError(f"Live environment row was edited since review {mid}")
        if digest(json_bytes(live_story[mid])) != row["story"]:
            raise ValueError(f"Live story differs from the reviewed map {mid}")
        live_world = live / "project/data/mapdata" / f"{mid}.bw"
        if digest(live_world.read_bytes()) != row["world"]:
            raise ValueError(f"Live world differs from the reviewed terrain {mid}")

    index_path = (live_root if publish else profile_root) / "index.json"
    prior = index_path.read_bytes()
    scoped = json.loads(prior)
    scoped.update(after)
    updated = json_bytes(scoped)
    created = []
    changed = []
    try:
        if publish:
            stage = read_json(profile_root / "index.json")
            if any(stage.get(mid) != after[mid] for mid in maps):
                raise ValueError("The approved palette rows are missing from the review profile")
            stage_story = read_json(profile / CATALOG)
            for mid, row in maps.items():
                world = profile / "project/data/mapdata" / f"{mid}.bw"
                if digest(world.read_bytes()) != row["world"] or digest(json_bytes(stage_story[mid])) != row["story"]:
                    raise ValueError(f"Review profile world/story differs from the live baseline {mid}")
            for name, data in payload.items():
                if (profile_root / name).read_bytes() != data:
                    raise ValueError(f"Unreviewed palette resource differs {name}")
                target = live_root / name
                if write_once(target, data):
                    created.append(target)
        else:
            # Stage only from the current baseline and the checked palette bundle.
            for name, data in payload.items():
                target = profile_root / name
                if write_once(target, data):
                    created.append(target)
            for name, data in profile_dependencies(live_root, profile_root, maps, payload).items():
                target = profile_root / name
                stage_content(target, data, created, changed)
            profile_story = read_json(profile / CATALOG)
            for mid in maps:
                relative = Path("project/data/mapdata") / f"{mid}.bw"
                stage_content(profile / relative, (live / relative).read_bytes(), created, changed)
                profile_story[mid] = live_story[mid]
            stage_content(profile / CATALOG, json_bytes(profile_story), created, changed)
        if index_path.read_bytes() != prior:
            raise ValueError("The environment index changed during installation")
        if updated != prior:
            changed.append((index_path, prior))
            replace_existing(index_path, updated)
        installed = read_json(index_path)
        for mid, row in maps.items():
            if installed[mid] != row["after"]:
                raise ValueError(f"Installed palette row verification failed {mid}")
    except BaseException:
        for target, before in reversed(changed):
            replace_existing(target, before)
        for target in reversed(created):
            target.unlink()
        raise

    print(f"{'Published' if publish else 'Staged'} {len(maps)} map-local palette rows")


def stage_content(path, data, created, changed):
    if path.exists():
        before = path.read_bytes()
        if data != before:
            changed.append((path, before))
            replace_existing(path, data)
    elif write_once(path, data):
        created.append(path)


def profile_dependencies(live, profile, maps, payload):
    # The original assets remain immutable and are enough to resolve every
    # texture and mesh reference that is shared with an out-of-scope map.
    base_rows = {mid: row["before"] for mid,row in maps.items()}
    aliases = {}
    for key in payload:
        if not key.endswith(".pm"):
            continue
        raw = (profile / key).read_bytes().decode("utf-8")
        model = MODEL.search(raw)[1]
        aliases[model] = (live / model).read_bytes()
    return {**resource_files(live, base_rows), **aliases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "stage", "publish"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--groups", nargs="+", choices=SETS, default=tuple(SETS))
    args = parser.parse_args()
    repo = args.repo.resolve()
    bundle = args.bundle.resolve()
    if args.action == "prepare":
        prepare(repo, bundle, args.groups)
    elif not args.profile:
        parser.error("--profile is required for stage and publish")
    else:
        apply(repo, args.profile.resolve(), bundle, publish=args.action == "publish")


if __name__ == "__main__":
    main()

