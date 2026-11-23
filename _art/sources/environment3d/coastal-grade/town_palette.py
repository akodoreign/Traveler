"""Stage readable, map-specific colors for towns and alpine roads."""
import argparse
from copy import deepcopy
from pathlib import Path

from coastal_daylight import ASSETS, CATALOG, FRAME, RENDER, apply, digest, js, read, resource_files, s32
from coastal_daylight import transfer


BASE_DAY = "rt_coastal_brilliance_road_horizon"
BASE_INTERIOR = "rt_hd2d_field"
SKY = Path("project/resource/ibltex/traveler_clear_coast_ibl.ktx")
SHOJI = ((226, 196, 139), .42)
PAPER = ((245, 171, 69), .53)
LEGACY_SWAY = {"wind_grass": .14, "coast_flowers": .09, "quarry_tent_flap": .083}

HOSHI_STREET = {
    "cedar": ((108, 64, 42), .55), "cedar_roof": ((107, 46, 31), .49),
    "cliff": ((103, 99, 91), .51), "path": ((186, 134, 77), .57),
    "meadow": ((19, 124, 51), .63), "wind_grass": ((54, 137, 50), .45),
}
HOSHI_ROOM = {
    "tea_shoji": SHOJI, "andon_paper": PAPER, "door_stoop": ((143, 116, 91), .43),
    "storehouse_board": ((132, 79, 46), .52), "storehouse_frame": ((78, 36, 27), .58),
    "tea_rail": ((96, 46, 31), .57), "tea_lacquer": ((109, 35, 29), .61),
}
HOSHI_ACCENTS = {
    "M120": {
        "tea_tatami": ((138, 151, 75), .60), "inn_cotton": ((210, 178, 133), .56),
        "inn_indigo": ((39, 71, 142), .71), "tea_hem": ((46, 89, 125), .61),
    },
    "M121": {
        "storehouse_board": ((108, 63, 43), .57), "tea_rail": ((64, 36, 33), .59),
        "inn_indigo": ((24, 57, 123), .67), "tea_lacquer": ((123, 38, 29), .60),
    },
    "M122": {
        "storehouse_board": ((156, 98, 52), .56), "tea_rail": ((76, 59, 39), .61),
        "tea_lacquer": ((28, 92, 82), .64), "hoshi_rice_bale": ((194, 147, 59), .43),
    },
    "M123": {
        "tea_rail": ((104, 44, 40), .59), "tea_tatami": ((136, 161, 69), .58),
        "tea_cushion": ((130, 37, 53), .68), "tea_hem": ((44, 86, 66), .60),
    },
    "M124": {
        "storehouse_board": ((124, 74, 50), .55), "tea_rail": ((67, 33, 51), .56),
        "tea_lacquer": ((73, 33, 61), .67), "tea_tatami": ((163, 138, 73), .56),
    },
    "M125": {
        "storehouse_earth": ((99, 69, 55), .53), "storehouse_board": ((117, 67, 42), .54),
        "storehouse_frame": ((78, 44, 37), .58), "hoshi_rice_bale": ((180, 134, 60), .45),
    },
}
BAYUSHI = {
    "bayushi_cedar": ((91, 42, 37), .51), "bayushi_lacquer": ((129, 27, 39), .72),
    "bayushi_scarlet_lantern": ((199, 48, 40), .62),
    "bayushi_shrine_lattice": ((135, 37, 42), .54),
    "bayushi_moss": ((20, 112, 57), .68), "bayushi_road": ((154, 94, 63), .51),
    "bayushi_block": ((122, 105, 108), .52), "bayushi_kawara": ((55, 57, 91), .56),
    "bayushi_pond_basin": ((46, 94, 84), .49),
    "shutai_mud": ((111, 69, 49), .50),
    "kaiu_redwood": ((134, 49, 39), .56), "kaiu_wood": ((99, 48, 37), .49),
    "kaiu_roof": ((48, 52, 77), .55), "kaiu_plaster": ((218, 184, 126), .51),
    "kaiu_shoji": SHOJI,
}
KAMEN = {
    "kamen_market_tile": ((133, 92, 80), .41), "kamen_market_stone": ((152, 113, 89), .49),
    "kamen_market_trim": ((96, 58, 72), .58), "kamen_market_walk": ((181, 132, 91), .46),
    "kamen_temple_wall": ((87, 77, 105), .56), "kamen_temple_floor": ((135, 100, 107), .64),
    "kaiu_wood": ((99, 51, 43), .51), "kaiu_redwood": ((144, 52, 36), .56),
    "kaiu_roof": ((57, 59, 91), .65), "kaiu_plaster": ((225, 191, 128), .53),
    "kaiu_shoji": SHOJI,
}
DRAGON = {
    "highland_meadow": ((25, 110, 62), .66), "dragon_grass": ((35, 115, 51), .60),
    "dragon_track": ((161, 105, 65), .50), "highland_snow": ((222, 235, 244), .34),
    "highland_slate": ((112, 117, 126), .47), "highland_dark_slate": ((64, 72, 87), .54),
    "dragon_slate": ((116, 121, 128), .45), "dragon_dark_slate": ((66, 77, 88), .51),
    "dragon_timber": ((108, 54, 36), .53), "dragon_roof": ((31, 79, 70), .61),
    "kaiu_shoji": SHOJI, "kaiu_plaster": ((224, 187, 127), .44),
    "scorpion_grove_cedar_v2": ((53, 105, 53), .41),
    "wind_grass": ((63, 138, 58), .42),
}


def interior(source, shrine=False):
    setting = deepcopy(source)
    title = "Sewn Faces Lantern Light" if shrine else "Hoshi Amber Lantern Light"
    setting["id"] = "rt_kamen_shrine_color" if shrine else "rt_hoshi_room_color"
    setting["name"] = {"en": title, "ja": title}
    warm = s32(0xFFE1ADFF if shrine else 0xFFF0CDFF)
    key = setting["envlights"][0]
    key.update(head=-38, pitch=53, power=1280 if shrine else 1780, color=warm, scolor=warm)
    key["shadow"].update(shadowdens=.47, shadowsoft=.30)
    setting["ibl"].update(ibldiff=371 if shrine else 460, iblspec=122, iblcolor=s32(0xD8D9FFFF))
    setting["fog"].update(density=.0036, zoffs=24.0, color=s32(0x3E344FAC))
    setting["postfx"].update(bloompow=.13, bloomthrs=.78)
    return setting


def prepare(repo, bundle, group):
    engine = repo / "_tools/rpgcobo-tool"
    root = engine / ASSETS
    index = read(root / "index.json")
    story = read(engine / CATALOG)
    stock = {row["id"]: row for row in read(engine / RENDER)["rendersets"]}
    road = stock[BASE_DAY]
    rooms = interior(stock[BASE_INTERIOR], shrine=group == "scorpion")
    if group == "hoshi":
        selections = {"M103": (HOSHI_STREET, road)}
        selections.update({map_id: ({**HOSHI_ROOM, **dyes}, rooms) for map_id, dyes in HOSHI_ACCENTS.items()})
    elif group == "scorpion":
        selections = {map_id: (BAYUSHI, road) for map_id in ("M345", "M347", "M348", "M349")}
        selections.update({map_id: (KAMEN, road) for map_id in ("M362", "M364")})
        selections["M366"] = (KAMEN, rooms)
    else:
        selections = {map_id: (DRAGON, road) for map_id in ("M379", "M380", "M382")}
        selections["M872"] = (DRAGON, None)

    maps = {}
    payloads = {}
    before = {map_id: index[map_id] for map_id in selections}
    dependencies = resource_files(root, before)
    for map_id, (palette, preset) in selections.items():
        row = before[map_id]
        alias_suffix = "_" + map_id.lower() + "_town_color"
        variants = {}

        def variant(name):
            if name in variants:
                return variants[name]
            descriptor = dependencies[name + ".pm"].decode("utf8")

            def material(match):
                filename = match[2]
                stem = Path(filename).stem
                if stem not in palette:
                    return match[0]
                new_name = stem + alias_suffix + ".png"
                key = "tex/" + new_name
                if key not in payloads:
                    # Selected textures use the calibrated dye as a base and
                    # keep the local material grain and alpha intact.
                    payloads[key] = transfer(dependencies["tex/" + filename], stem, pigment=palette[stem])
                return match[1] + "tex/" + new_name + match[3]

            changed = FRAME.sub(material, descriptor)
            alias = name if changed == descriptor else name + alias_suffix
            if alias != name:
                payloads[alias + ".pm"] = changed.encode("utf8")
            variants[name] = alias
            return alias

        after = deepcopy(row)
        after["terrain"] = variant(row["terrain"])
        if preset is not None:
            after["renderPreset"] = preset["id"]
        for prop in after["placements"]:
            name = prop[0]
            prop[0] = variant(name)
            if prop[0] != name and len(prop) == 6 and name in LEGACY_SWAY:
                prop.append(LEGACY_SWAY[name])
        assert row["terrain"] != after["terrain"], map_id
        maps[map_id] = {
            "before": row,
            "after": after,
            "story": digest(js(story[map_id])),
            "world": digest((engine / "project/data/mapdata" / f"{map_id}.bw").read_bytes()),
        }

    sky_data = (engine / SKY).read_bytes()
    sky_proof = {SKY.as_posix(): digest(sky_data)}
    proof = {
        "maps": maps,
        "basePresets": {BASE_INTERIOR: stock[BASE_INTERIOR], BASE_DAY: road},
        "presets": list({p["id"]: p for _, p in selections.values() if p is not None}.values()),
        "source": {key: digest(content) for key, content in dependencies.items()},
        "files": {key: digest(content) for key, content in payloads.items()},
        "projectSource": sky_proof,
        "projectFiles": sky_proof,
    }
    for filename, content in {**payloads, SKY.as_posix(): sky_data}.items():
        destination = bundle / "files" / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    (bundle / "coastal-proof.json").write_bytes(js(proof) + b"\n")
    print(f"Prepared {len(maps)} {group} rows and {len(payloads)} material files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "stage", "publish"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--group", choices=("hoshi", "scorpion", "dragon"))
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    repo, bundle = args.repo.resolve(), args.bundle.resolve()
    if args.action == "prepare":
        if args.group is None:
            parser.error("--group is required to prepare.")
        prepare(repo, bundle, args.group)
    elif args.profile is None:
        parser.error("--profile is required to stage or publish.")
    else:
        apply(repo, args.profile.resolve(), bundle, args.action == "publish")


if __name__ == "__main__":
    main()
