"""Dress the rice road, hot springs, and City of Masks approach."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from export_coast import STAGE, export, voxel_asset
from kensu_worlds import MAPS, variants
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
MATS = {
    **KAIU,
    "kensu_meadow": ("kensu_meadow.png", .94),
    "kensu_clay": ("kensu_road.png", .94),
    "kensu_field": ("kensu_field.png", .91),
    "kensu_granite": ("kensu_granite.png", .87),
    "kensu_timber": ("kensu_timber.png", .91),
    "kensu_kawara": ("kensu_kawara.png", .86),
    "kensu_paddy": ("kensu_paddy00.png", .34),
    "kensu_spring": ("kensu_spring00.png", .32),
}


def surfaces():
    for key, ref, tint in (
        ("kensu_road", "kensu_path_clay", (99, 67, 45)),
        ("kensu_field", "kensu_path_clay", (50, 82, 43)),
        ("kensu_meadow", "kensu_meadow_scan", (45, 83, 41)),
        ("kensu_granite", "kamen_old_flagstones", (83, 84, 87)),
        ("kensu_timber", "kaiu_cedar", (78, 42, 28)),
        ("kensu_kawara", "kawara_bluegrey", (34, 58, 62)),
    ):
        sample = periodic(Image.open(HERE / f"surface_sources/{ref}.png").convert("RGB"), 768)
        value = sample @ [.24, .63, .13]
        grain = np.clip(value / max(1., np.median(value)), .55, 1.44)
        rgb = np.asarray(tint) * (.17 + .83 * grain[..., None])
        Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / f"tex/{key}.png")

    for frame in range(32):
        ref = STAGE / f"tex/kudo_river{frame:02d}.png"
        source = np.asarray(Image.open(ref).convert("RGB"), dtype=float)
        value = source @ [.24, .63, .13]
        relief = (value - np.median(value)) / 45.
        for key, tint, strength in (
            ("kensu_paddy", (46, 82, 48), (19, 32, 16)),
            ("kensu_spring", (46, 110, 104), (32, 42, 35)),
        ):
            rgb = np.asarray(tint) + relief[..., None] * strength
            Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / f"tex/{key}{frame:02d}.png")


def geometry(gm, world, water_material):
    water = world.blk == gm.WATER
    height = world.hgt.copy()
    world.blk[water] = gm.T(3, None)
    world.hgt[water] = np.maximum(height[water] - 1, 0)
    terrain = world_mesh(gm, world, {
        gm.ROAD: "kensu_clay", gm.GRASS3: "kensu_field", gm.STONEW: "kensu_granite",
        gm.T(3, None): "kensu_field", gm.GRASS: "kensu_meadow", gm.GRASS2: "kensu_meadow",
        gm.WOOD: "kensu_timber", gm.DARKWOOD: "kensu_timber", gm.ROOF: "kensu_kawara",
    })
    for face, style in zip(terrain.faces, terrain.materials, strict=True):
        if style not in ("kensu_meadow", "kensu_field", "kensu_clay"):
            continue
        vertices = np.array([terrain.vertices[i] for i in face])
        if np.ptp(vertices[:, 2]) < .0001:
            for i in face:
                terrain.vertices[i] = terrain.vertices[i] + [0., 0., .055]
    world.blk[water] = gm.WATER
    world.hgt[:] = height
    if not water.any():
        return terrain, None
    _, liquid = grid_surfaces(water.astype(int), height, ("", water_material), wall_style="kensu_field", fluid=1)
    return terrain, liquid


def dress(gm, world, map_id):
    arena = map_id == "M865"
    props = []

    def put(asset, x, z, scale=1., yaw=0., offset=0., sway=0.):
        bx, bz = (x, z) if arena else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
        y = (int(world.hgt[bz, bx]) + 1) * .5 + offset
        row = [asset, bx * .5 + .25, y, bz * .5 + .25, scale, yaw]
        if sway:
            row.append(sway)
        props.append(row)

    if map_id == "M359":
        for ix in range(0, 104, 13):
            for dx in (3, 5, 7, 9):
                for z in (23, 26):
                    put("kensu_rice_seedlings", ix + dx, z, .82 + .1 * ((dx + ix) % 3), .12 * dx, -.16, .08)
            put("coast_pine", ix + 4, 7 + ix % 3, .83 + .1 * (ix % 4), ix * .16)
            put("kensu_spring_rocks", ix + 5, 31, .85 + ix % 3 * .15, ix * .31)
        put("kensu_field_jizo", 57, 11, .95, .05)
        put("kensu_valley_sign", 61, 11, .86, .12)
    elif map_id == "M360":
        for x, z in ((10, 4), (30, 6), (78, 4), (92, 7)):
            put("kensu_spring_rocks", x + 1, z + 1, 1.32, .6, -.23)
            put("kensu_spring_rocks", x + 6, z + 4, 1.23, -1., -.24)
            put("kensu_bath_supplies", x + 4, z - 2, .88, .12)
            put("kamen_hospitality_lantern", x + 7, z - 1, .77, .08)
            put("coast_pine", x - 2, z + 5, 1.01, .23 * x)
        for x in (4, 24, 44, 62, 80, 98):
            put("kamen_hospitality_lantern", x, 19, .93 + .06 * (x % 3), .07)
        put("kensu_springs_sign", 23, 19, .90)
        put("kensu_bath_supplies", 37, 20, 1.05, -.25)
        for x in (34, 52):
            center = (gm.PAD_X + x) * .5
            front = (gm.PAD_BOTTOM + 22) * .5 - .118
            props.append(["kudo_shut_door", center, 2.5, front, 1., 0.])
            props.append(["town_door_stoop_half", center - .5, 2., front, 1., 0.])
    elif map_id == "M361":
        for i, x in enumerate(range(4, 103, 8)):
            put("coast_pine", x, 5 + (i % 5), .72 + (i % 5) * .11, .33 * i)
            put("kensu_spring_rocks", x + 3, 24 + (i % 3), .71 + (i % 4) * .16, .55 * i)
        put("kensu_field_jizo", 44, 12, 1.03, -.17)
        put("kensu_field_jizo", 83, 19, 1.28, .2)
        put("kensu_city_sign", 88, 12, .91)
        for x, z in ((91, 12), (91, 19), (97, 12), (97, 19)):
            put("kamen_hospitality_lantern", x, z, .80)
    else:
        for i, x in enumerate(range(8, 120, 4)):
            for z in (96, 100, 105, 111):
                put("kensu_rice_seedlings", x, z, 1.0 + (i % 3) * .12, .1 * i, -.18, .08)
        for x, z in ((8, 88), (30, 91), (52, 88), (74, 90), (91, 89), (118, 90)):
            put("kensu_spring_rocks", x, z, 1.40, x * .2)
        for x in (7, 41, 68, 107):
            put("coast_pine", x, 89, 1.18, x * .09)
    return props


def main(repo):
    _, _, gm, _, _ = variants(repo)
    import voxfile

    surfaces()
    shop_board("kensu_valley_sign", "OJATARA", "VALLEYS", "#564436")
    shop_board("kensu_springs_sign", "HISATU KENSU", "HOT SPRINGS", "#4b4854")
    shop_board("kensu_city_sign", "KAMEN NO", "TOSHI", "#613b38")
    sources = {}
    for key, dimensions, resolution in (
        ("kensu_bath_supplies", (.94, .57, .76), 38),
        ("kensu_spring_rocks", (1.8, .89, .67), 39),
        ("kensu_rice_seedlings", (.60, .56, .50), 37),
        ("kensu_field_jizo", (.63, .51, .99), 38),
        ("kamen_hospitality_lantern", (.48, .41, 1.55), 43),
    ):
        sources[key] = save(*convert_prop(key, dimensions, resolution, lower=.02), voxfile)
        voxel_asset(key)

    manifest = STAGE / "index.json"
    index = json.loads(manifest.read_bytes())
    layout = {}
    for mid in MAPS:
        m, events = gm.make(mid)
        key = f"{mid.lower()}_kensu"
        material = "kensu_spring" if mid == "M360" else "kensu_paddy"
        land, water = geometry(gm, m, material)
        export(key, land, MATS)
        props = dress(gm, m, mid)
        row = {"terrain": key, "placements": props}
        if water is not None:
            export(key + "_water", water, MATS)
            row["water"] = key + "_water"
            row["waterSequence"] = {"prefix": material, "frames": 32, "seconds": 13.0}
        if mid == "M360":
            front = (gm.PAD_BOTTOM + 22) * .5 - .118
            row["doors"] = [
                {"x": (gm.PAD_X + x - 1) * .5, "y": 2.5, "z": front, "grade": 2.,
                 "event": event, "stoop": "town_door_stoop_half"}
                for x, event in ((14, 85), (69, 86))
            ]
        index[mid] = row
        layout[mid] = {"props": len(props), "events": len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "kensu-approach-layout.json").write_text(
        json.dumps({"maps": layout, "sources": sources}, indent=2), encoding="utf8"
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
