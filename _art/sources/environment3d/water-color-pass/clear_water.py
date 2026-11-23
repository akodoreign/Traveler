"""Generate and stage clear water on scoped winter and mountain maps."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from publish_castle_gates import publish as write_transaction, resource_files


ROOT = Path("project/resource/native_environment")
CATALOG = Path("project/data/map.json")
TAU = np.float32(2. * np.pi)
SIDE = 256
DESCRIPTOR_SUFFIX = "_clear_flow"


@dataclass(frozen=True)
class Water:
    maps: tuple[str, ...]
    original: str
    prefix: str
    seconds: float
    frames: int
    colors: tuple[tuple[int, int, int], ...]
    kind: str


FAMILIES = (
    Water(("M422", "M423", "M424", "M888"), "winter_river_water",
          "winter_sapphire_flow", 17.8, 64, ((8,36,127), (14,82,187), (34,149,226)),
          "river"),
    Water(("M889",), "winter_jetty_storm_water", "winter_sapphire_storm", 9.6, 64,
          ((11,30,84), (24,67,135), (53,128,192)), "storm"),
    Water(("M403",), "iuchi_brook", "iuchi_clear_brook", 13., 32,
          ((10,65,101), (16,114,157), (44,170,195)), "brook"),
)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def data_json(path: Path):
    return json.loads(path.read_bytes())


def json_bytes(data) -> bytes:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf8")


def smooth(low, high, sample):
    value = np.clip((sample-low)/(high-low), 0., 1.)
    return value*value*(3.-2.*value)


def sinusoid(turns):
    return np.sin(TAU * turns)


def moving_blue(style: Water, time: float) -> np.ndarray:
    axis = np.arange(SIDE, dtype=np.float32) / SIDE
    v, u = np.meshgrid(axis, axis, indexing="ij")
    # Advect one complete UV tile along the shore each authored cycle.
    # The slight cross-stream bend exposes broken rather than parallel crests.
    flow, back = u - time, u - .17*sinusoid(time)/TAU
    curl = .19*sinusoid(flow+v) + .11*sinusoid(2*flow-3*v)
    pool = .50*sinusoid(flow+v) + .31*sinusoid(2*flow-3*v) + .19*sinusoid(3*flow+5*v)
    long_roll = .54*sinusoid(2*flow+5*v+curl) + .28*sinusoid(flow-3*v-.65*curl)
    long_roll += .18*sinusoid(3*flow+4*v+.16*sinusoid(2*back+v-time))
    split = smooth(.46,.92, sinusoid(2*flow-2*v)+.33*sinusoid(3*flow+v))
    pal = np.array(style.colors, dtype=np.float32)
    if style.kind == "storm":
        chop = .57*sinusoid(3*flow+8*v+curl) + .29*sinusoid(5*flow-6*v-curl)
        chop += .14*sinusoid(7*flow+9*v+time)
        field = .46+.20*pool+.16*long_roll+.15*chop
        crests = smooth(.22,.92, chop)*smooth(.27,.74,long_roll+.25*pool)*.34
    elif style.kind == "brook":
        threading = sinusoid(2*flow+9*v+curl)*.55 + sinusoid(5*flow-5*v-curl)*.45
        field = .51+.23*pool+.14*long_roll+.06*threading
        crests = smooth(.24,.93,threading)*split*.21
    else:
        distant = .62*sinusoid(3*flow+8*v+curl) + .38*sinusoid(4*flow-6*v-.33*curl)
        field = .46+.22*pool+.19*long_roll+.04*distant
        crests = smooth(.26,.89,long_roll+.27*pool)*split*.30

    water = pal[0]+(pal[1]-pal[0])*smooth(.04,.78,field)[:, :, None]
    water += (pal[2]-pal[1])*(smooth(.47,.95,field)*.49+crests)[:, :, None]
    return np.round(np.clip(water,0,255)).astype(np.uint8)


def encode_frame(style: Water, index: int, total: int) -> bytes:
    buffer = io.BytesIO()
    Image.fromarray(moving_blue(style, index/total)).save(buffer, format="PNG", compress_level=6)
    return buffer.getvalue()


def water_path(profile: Path, mid: str) -> Path:
    return profile / "project/data/mapdata" / f"{mid}.bw"


def prepare(repo: Path, bundle: Path) -> None:
    engine = repo / "_tools/rpgcobo-tool"
    assets = engine / ROOT
    current = data_json(assets / "index.json")
    story = data_json(engine / CATALOG)
    files = {}
    source = {}
    maps = {}
    recipes = {}
    for style in FAMILIES:
        expected = {"prefix":style.original, "frames":32, "seconds":style.seconds}
        allowed = {
            mid for mid,row in current.items()
            if (row.get("waterSequence") or {}).get("prefix") == style.original
        }
        assert allowed == set(style.maps),(style.original, sorted(allowed))
        for index in range(expected["frames"]):
            rel = f"tex/{style.original}{index:02d}.png"
            source[rel] = digest((assets/rel).read_bytes())
        for index in range(style.frames):
            files[f"tex/{style.prefix}{index:02d}.png"] = encode_frame(style,index,style.frames)
        for mid in style.maps:
            row = current[mid]
            assert row.get("waterSequence") == expected and row.get("waterMode") != "lava",mid
            key = row["water"]
            raw = (assets/(key+".pm")).read_bytes()
            model = re.search(rb'^modeldata = "([^"]+)"', raw, re.M).group(1).decode()
            old = f'texture0 = "tex/{style.original}00.png"'.encode()
            new = f'texture0 = "tex/{style.prefix}00.png"'.encode()
            assert raw.count(old) == 1,mid
            variant = key+DESCRIPTOR_SUFFIX
            files[variant+".pm"] = raw.replace(old, new)
            source[key+".pm"] = digest(raw)
            source[model] = digest((assets/model).read_bytes())
            revised = {**row,"water":variant,"waterSequence":{**expected,"prefix":style.prefix,"frames":style.frames}}
            maps[mid] = {
                "name":story[mid].get("name",mid),"before":row,"after":revised,
                "world":digest(water_path(engine,mid).read_bytes()),
                "story":digest(json_bytes(story[mid])),"model":model,
            }
        recipes[style.prefix] = {"old_prefix":style.original,
                                 "map_ids":list(style.maps),"seconds":style.seconds,
                                 "frames":style.frames,"colors":style.colors}

    bundle.mkdir(parents=True,exist_ok=True)
    for filename,data in files.items():
        path = bundle/"files"/filename
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    receipt = {"maps":maps,"source":source,"files":{f:digest(data) for f,data in files.items()},
               "sequences":recipes}
    (bundle/"water-proof.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n","utf-8")
    print(f"Prepared {len(maps)} water rows and {len(files)} resources")


def apply(repo: Path, bundle: Path, profile: Path, publish=False) -> None:
    engine = repo / "_tools/rpgcobo-tool"
    if profile == engine:
        raise ValueError("Choose an isolated review profile.")
    source = engine / ROOT
    preview = profile / ROOT
    receipt = data_json(bundle/"water-proof.json")
    maps = receipt["maps"]
    current = data_json(source/"index.json")
    story = data_json(engine/CATALOG)
    after = {mid:item["after"] for mid,item in maps.items()}
    for path,checksum in receipt["source"].items():
        if digest((source/path).read_bytes()) != checksum:
            raise ValueError(f"Water source asset changed after review {path}")
    for mid,item in maps.items():
        assert current[mid] in (item["before"],item["after"]),mid
        assert digest(json_bytes(story[mid]))==item["story"],mid
        assert digest(water_path(engine,mid).read_bytes())==item["world"],mid
    payload = {path:(bundle/"files"/path).read_bytes() for path in receipt["files"]}
    assert all(digest(data)==receipt["files"][key] for key,data in payload.items())
    root = source if publish else preview
    index = root/"index.json"
    baseline = index.read_bytes()
    rows = json.loads(baseline)
    replacements = {index:json_bytes({**rows,**after})}
    originals = {index:baseline}
    additions = {}

    def place(path, data, *, immutable=False):
        if path.is_file():
            existing = path.read_bytes()
            if existing == data:
                return
            if immutable:
                raise ValueError(f"Water asset does not match staged bytes {path}")
            originals[path] = existing
            replacements[path] = data
        else:
            additions[path] = data

    if publish:
        candidate = data_json(preview/"index.json")
        review_story = data_json(profile/CATALOG)
        for mid,item in maps.items():
            assert candidate[mid]==item["after"],mid
            assert digest(water_path(profile,mid).read_bytes())==item["world"],mid
            assert digest(json_bytes(review_story[mid]))==item["story"],mid
            assert digest((preview/item["model"]).read_bytes())==receipt["source"][item["model"]],mid
        for path,data in payload.items():
            assert (preview/path).read_bytes()==data,path
    else:
        old_rows = {mid:item["before"] for mid,item in maps.items()}
        for path,data in resource_files(source,old_rows).items():
            place(preview/path,data)
        profile_story = data_json(profile/CATALOG)
        for mid in maps:
            place(water_path(profile,mid),water_path(engine,mid).read_bytes())
            profile_story[mid] = story[mid]
        place(profile/CATALOG,json_bytes(profile_story))
    for path,data in payload.items():
        place(root/path,data,immutable=True)
    for path in additions:
        path.parent.mkdir(parents=True,exist_ok=True)
    write_transaction(originals,replacements,additions)
    assert all(data_json(index)[mid]==item["after"] for mid,item in maps.items())
    print(f"{'Published' if publish else 'Staged'} {len(maps)} water-only map rows.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--profile",type=Path)
    args = parser.parse_args()
    repo,bundle = args.repo.resolve(),args.bundle.resolve()
    if args.action == "prepare":
        prepare(repo,bundle)
    elif args.profile is None:
        parser.error("--profile is required for stage and publish")
    else:
        apply(repo,bundle,args.profile.resolve(),publish=args.action=="publish")


if __name__ == "__main__":
    main()
