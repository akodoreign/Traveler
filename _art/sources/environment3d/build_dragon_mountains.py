"""Build the Dragon mountain settlements, roads, garden, inn, and arena."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import label
from scipy.spatial import ConvexHull, cKDTree

from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from build_kudo_rooms import MATS as ROOM, frame
from dragon_inn_joinery import DOOR_MODELS, MATERIALS as JOINERY, door_models, floorboards, shelf, surfaces
from dragon_worlds import MAPS, variant
from export_coast import Geometry, STAGE, export, voxel_asset
from kudo_rooms_worlds import variant as room_variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
MATERIALS = {
    "dragon_grass": ("dragon_slate_moss", (38, 80, 48)),
    "dragon_track": ("ojatara_earth_v2", (101, 73, 47)),
    "dragon_slate": ("dragon_slate_moss", (52, 66, 84)),
    "dragon_dark_slate": ("kamen_temple_rock", (36, 47, 62)),
    "dragon_snow": ("kamen_old_flagstones", (160, 175, 182)),
    "dragon_timber": ("dragon_inn_burnished_cypress", (71, 43, 31)),
    "dragon_roof": ("kawara_bluegrey", (31, 56, 62)),
    "dragon_mats": ("kudo_inn_mat", (142, 113, 68)),
    "dragon_plaster": ("dragon_clean_wall_plaster", (163, 143, 111)),
    "highland_meadow": ("meadow_scan", (31, 73, 41)),
    "highland_slate": ("dragon_slate_moss", (45, 58, 75)),
    "highland_dark_slate": ("kamen_temple_rock", (27, 39, 53)),
    "highland_snow": ("dragon_clean_wall_plaster", (142, 158, 170)),
}
MATS = {**KAIU, **ROOM, **JOINERY, **{k: (f"{k}.png", .91) for k in MATERIALS},
        "dragon_raked": ("dragon_raked.png", .94)}
PROPS = (
    ("dragon_slate_waystation", (2.35, 1.48, 2.05), 41),
    ("dragon_forest_torii", (3.24, .81, 2.91), 44),
    ("dragon_mountain_andon", (.36, .33, .93), 34),
    ("dragon_togashi_stele", (.69, .47, 1.26), 36),
    ("dragon_inn_hearth", (1.66, 1.23, .67), 39),
    ("dragon_procession_bell", (1.06, .56, 1.44), 39),
    ("dragon_garden_stone_lantern", (.69, .61, 1.36), 39),
    ("dragon_inn_hanging_screen", (1.54, .27, 1.48), 38),
    ("togashi_garden_stone", (1.70, 1.03, .89), 42),
)
GARDEN_STONES = ((20, 8, 1.21), (46, 9, 1.04), (33, 6, .84))


def garden_stone(dimensions, resolution):
    name, points, colors, _, source = convert_prop("togashi_garden_stone", dimensions, resolution)
    # The reconstruction included a white photography sweep and a thin base slab.
    white = (colors.min(axis=1) > 180) & (np.ptp(colors, axis=1) < 30)
    keep = ~white & (points[:, 1] < points[:, 1].max() - 2) & (points[:, 2] > 4)
    points, colors = points[keep], colors[keep]
    points -= points.min(axis=0)
    shape = points.max(axis=0) + 1
    mask = np.zeros(shape, dtype=bool)
    mask[tuple(points.T)] = True
    components, _ = label(mask, structure=np.ones((3, 3, 3)))
    ids = components[tuple(points.T)]
    keep = ids == np.bincount(ids).argmax()
    points, colors = points[keep], colors[keep]
    points -= points.min(axis=0)
    shape = points.max(axis=0) + 1
    hull = ConvexHull(points).equations
    volume = np.indices(shape).reshape(3, -1).T
    filled = np.all(volume @ hull[:, :3].T + hull[:, 3] < .18, axis=1)
    body = volume[filled]
    samples = colors[cKDTree(points).query(body)[1]]
    luminance = samples @ [.26, .61, .13]
    shade = np.clip(np.rint((luminance - np.median(luminance)) / 21), -3., 3.)
    palette = np.array([73, 94, 108]) + shade[:, None] * np.array([6, 7, 8])
    return name, body, palette.astype(np.uint8), np.asarray(dimensions) / shape, source


def materials():
    for key, (scan, tint) in MATERIALS.items():
        source = Image.open(HERE / f"surface_sources/{scan}.png").convert("RGB")
        brightness = periodic(source, 768) @ [.26, .61, .13]
        broad = np.asarray(Image.fromarray(np.uint8(brightness)).filter(ImageFilter.GaussianBlur(16.)))
        detail = brightness - broad
        clean = key.startswith("highland_")
        grain = 1 + (.029 if clean else .071) * np.clip(detail / max(detail.std(), 1.), -2.4, 2.4)
        grain += (.085 if clean else .21) * (broad / max(1., np.median(broad)) - 1)
        if key == "highland_meadow":
            z, x = (axis * (math.tau / grain.shape[0]) for axis in np.indices(grain.shape, sparse=True))
            grain += .034 * np.sin(x * 3. + 1.3 * np.cos(z * 2.)) * np.sin(z * 3.)
        rgb = np.asarray(tint) * grain[..., None]
        Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / f"tex/{key}.png")


def garden_gravel(geometry, world, gm):
    width, height = 2048, 1024
    z, x = np.indices((height, width), sparse=True)
    x = x * world.w * .5 / (width - 1)
    z = z * world.d * .5 / (height - 1)
    rows = np.cos((z + .022 * np.sin(x * 3.)) * math.tau / .195)
    for bx, bz, size in GARDEN_STONES:
        dx = x - (bx + gm.PAD_X) * .5 - .25
        dz = z - (bz + gm.PAD_BOTTOM) * .5 - .25
        distance = np.sqrt(dx * dx + .90 * dz * dz)
        blend = np.clip((1.40 * size - distance) / (.54 * size), 0., 1.)
        rows = rows * (1 - blend) + np.cos(distance * math.tau / .195) * blend
    variation = 5.2 * rows + np.random.default_rng(383).normal(0., 1.1, rows.shape)
    rgb = np.asarray([146, 132, 106]) + variation[..., None]
    Image.fromarray(np.uint8(np.clip(rgb, 0., 255.))).save(STAGE / "tex/dragon_raked.png")
    for i, face in enumerate(geometry.faces):
        if geometry.materials[i] == "dragon_raked":
            geometry.uvs[i] = [(p[0] * 2 / world.w, p[1] * 2 / world.d)
                               for p in (geometry.vertices[vi] for vi in face)]

    left, right = gm.PAD_X * .5, (gm.PAD_X + 64) * .5
    front, rear = gm.PAD_BOTTOM * .5, (gm.PAD_BOTTOM + 25) * .5
    slate = "highland_dark_slate"
    box(geometry, (left - .06, rear - .065, 5.019), (right - left + .12, 2.63, .14), slate, 2.6)
    box(geometry, (left, rear - .037, 4.68), (right - left, .070, .15), "inn_beam", 1.9)
    for x in (left, right - .5):
        box(geometry, (x - .054, front, 5.019), (.605, rear - front + .04, .14), slate, 2.6)
    for x in np.arange(left + 2.5, right - 1., 4.5):
        box(geometry, (x, rear - .057, 2.02), (.13, .12, 2.92), "inn_beam", 1.3)


def structures():
    cliff = Geometry()
    tiers = (
        (-1.04, -.39, .0, 2.31, .92, .48, "dragon_dark_slate"),
        (-.83, -.44, .43, 1.74, .78, .44, "dragon_slate"),
        (-.65, -.35, .84, 1.38, .74, .59, "dragon_slate"),
        (-.45, -.29, 1.36, 1.18, .68, .47, "dragon_dark_slate"),
        (-.34, -.24, 1.79, .81, .52, .32, "dragon_slate"),
        (.32, -.58, .0, 1.09, .61, .49, "dragon_slate"),
    )
    for x, z, y, w, d, h, material in tiers:
        box(cliff, (x, z, y), (w, d, h), material, 1.13)
    export("dragon_slate_outcrop", cliff, MATS)

    stall = Geometry()
    for x in (-1.15, 1.06):
        for z in (-.56, .50):
            box(stall, (x, z, 0.), (.094, .092, 1.82), "dragon_timber")
    box(stall, (-1.26, -.64, 1.82), (2.51, 1.36, .10), "dragon_roof", 1.05)
    box(stall, (-1.17, -.44, .74), (2.29, .51, .10), "dragon_timber", 1.05)
    for x in (-.98, .91):
        box(stall, (x, -.39, .0), (.11, .31, .74), "dragon_timber")
    export("dragon_incense_counter", stall, MATS)
    shop_board("dragon_inn_board", "MOUNTAIN", "INN", "#346051")
    shop_board("dragon_outfitter_board", "TOGASHI", "OUTFITTER", "#3c6550")
    shop_board("dragon_incense_board", "PILGRIM", "INCENSE", "#744536")


def terrain(gm, world):
    palette = {gm.GRASS: "dragon_grass", gm.GRASS2: "dragon_grass", gm.GRASS3: "dragon_grass",
               gm.ROAD: "dragon_track", gm.DIRT: "dragon_track", gm.STONE: "dragon_slate",
               gm.STONEW: "dragon_dark_slate", gm.SNOW: "dragon_snow", gm.WOOD: "dragon_timber",
               gm.DARKWOOD: "dragon_timber", gm.ROOF: "dragon_roof"}
    if world.mid != "M380":
        palette.update({gm.GRASS: "highland_meadow", gm.GRASS2: "highland_meadow", gm.GRASS3: "highland_meadow",
                        gm.STONE: "highland_slate", gm.STONEW: "highland_dark_slate", gm.SNOW: "highland_snow"})
    if world.mid == "M383":
        palette[gm.CAVE_FLOOR] = "dragon_raked"
    geometry = world_mesh(gm, world, palette)
    for face, material in zip(geometry.faces, geometry.materials, strict=True):
        if material in ("dragon_grass", "dragon_track", "dragon_snow", "dragon_raked", "highland_meadow", "highland_snow"):
            vertices = np.array([geometry.vertices[i] for i in face])
            if np.ptp(vertices[:, 2]) < .0001:
                for i in face:
                    geometry.vertices[i] = geometry.vertices[i] + [0., 0., .052]
    if world.mid == "M383":
        garden_gravel(geometry, world, gm)
    return geometry


def layout(gm, world):
    mid = world.mid
    arena = mid == "M872"
    placements, lights, doors = [], [], []
    rng = np.random.default_rng(int(mid[1:]))

    def put(asset, x, z, size=1., turn=0., lift=0., wind=0.):
        bx, bz = (x, z) if arena else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
        y = (int(world.hgt[bz, bx]) + 1) * .5 + lift
        row = [asset, bx * .5 + .25, y, bz * .5 + .25, size, turn]
        placements.append(row + [wind] if wind else row)
        return row[1:4]

    def lamp(x, z, size=.92):
        xx, y, zz = put("dragon_mountain_andon", x, z, size)
        lights.append([xx, y + .66 * size, zz, 4.4, 1.50])

    def door(x, z, event):
        bx, bz = x + gm.PAD_X, z + gm.PAD_BOTTOM
        cut, = (obj for obj in world.objs if obj["t"] == "fill" and obj["blk"] == gm.VOID
                and (obj["x"], obj["z"], obj["w"], obj["h"]) == (bx - 1, bz, 2, 4))
        grade = (int(world.hgt[bz - 1, cut["x"]]) + 1) * .5
        threshold = cut["y"] * .5
        stoop = {.5: "dragon_inn_stoop_half", 1.: "dragon_inn_stoop_full"}[threshold - grade]
        doors.append({"x": cut["x"] * .5, "y": threshold, "z": cut["z"] * .5 - .078,
                      "grade": grade, "event": event, "stoop": stoop, "models": DOOR_MODELS})

    if mid == "M379":
        for x in (4, 24, 39, 55, 74, 85, 103):
            lamp(x, 20)
        door(13, 22, 95)
        door(31, 22, 96)
        door(65, 23, None)
        put("dragon_inn_board", 9, 20, .96)
        put("dragon_outfitter_board", 27, 20, .91)
        put("dragon_incense_counter", 45, 22, .92)
        put("dragon_incense_board", 42, 19, .71)
        put("kudo_eel_basket", 45, 22, .61, .1, .77)
        put("dragon_forest_torii", 95, 20, .90, .02)
        put("dragon_slate_waystation", 76, 19, .86, -.10)
        for x in (8, 24, 39, 55, 74, 92, 105):
            put("scorpion_grove_cedar_v2", x, 7 + x % 3, .72 + x % 4 * .10, x * .17)
        for x in (4, 24, 40, 54, 77, 100):
            put("togashi_garden_stone", x, 30, 1.19 + x % 3 * .23, x * .09)
    elif mid == "M380":
        door(61, 21, 2)
        put("dragon_inn_board", 54, 20, .86)
        lamp(57, 20)
        lamp(65, 20)
        put("hoshi_inn_bench", 66, 18, 1.07, .2)
        for x, z in ((6, 12), (35, 12), (82, 19), (105, 17)):
            put("dragon_togashi_stele", x, z, .84 + .13 * (x % 3), x * .27)
        for x in range(9, 109, 11):
            put("scorpion_grove_cedar_v2", x, 7 + x % 3, .82 + x % 4 * .10, x * .19)
        for x in (6, 19, 32, 43, 71, 82, 93, 106):
            put("dragon_slate_outcrop", x, 25, 1.16 + x % 3 * .23, x * .22)
            put("wind_grass", x, 11, .83, .2 * x, 0., .07)
    elif mid == "M382":
        put("dragon_forest_torii", 100, 15, .95, math.pi / 2)
        put("dragon_procession_bell", 63, 20, .92)
        put("dragon_slate_waystation", 73, 21, .92)
        for x, z in ((18, 12), (48, 19), (86, 19), (103, 13)):
            put("dragon_togashi_stele", x, z, .94, .22 * x)
        for x in (7, 19, 31, 47, 66, 82, 89, 114):
            put("scorpion_grove_cedar_v2", x, 7 + x % 4, .74 + x % 4 * .10, .43 * x)
            put("togashi_garden_stone", x, 25, 1.33 + x % 4 * .15, .17 * x)
        lamp(73, 20)
        lamp(102, 19)
        for x, z in ((8, 12), (17, 19), (29, 19), (38, 11), (56, 23), (65, 11), (82, 20), (96, 20), (108, 10)):
            put("wind_grass", x, z, .82 + x % 4 * .13, x * .33, 0., .09)
    elif mid == "M383":
        for x, z, size in GARDEN_STONES:
            put("togashi_garden_stone", x, z, size, x * .19)
        for x, z in ((13, 20), (25, 22), (49, 21), (57, 18)):
            put("coast_pine", x, z, .94 + x % 4 * .08, x * .23)
        for x, z in ((7, 12), (29, 19), (43, 19), (54, 13)):
            put("dragon_garden_stone_lantern", x, z, .90, x * .07)
        put("bayushi_pond_basin", 52, 22, .78)
        put("dragon_forest_torii", 7, 15, .84, math.pi / 2)
    else:
        for x in (7, 16, 33, 43, 49, 71, 87, 95, 117, 123):
            put("scorpion_grove_cedar_v2", x, 82 + x % 9,
                float(rng.uniform(.85, 1.19)), float(rng.uniform(0., math.tau)))
        for x in (9, 31, 44, 63, 79, 99, 116):
            put("togashi_garden_stone", x, 88 + x % 3, 1.25 + x % 4 * .18, x * .31)
        for x, z in ((19, 80), (34, 84), (42, 78), (68, 82), (75, 77), (88, 84), (108, 83)):
            put("wind_grass", x, z, 1.03 + x % 3 * .12, .12 * x, 0., .08)
    return {"placements": placements, "poolLights": lights, "doors": doors}


def mountain_inn(repo):
    _, gm, _, _ = room_variant(repo, group="dragon")
    world, events = gm.make("M381")
    room = world_mesh(gm, world, {gm.PLANK: "dragon_timber", gm.STONEW: "dragon_plaster"})
    trim = Geometry()
    floorboards(trim)
    for x in (5.20, 7.04, 8.88):
        box(trim, (x, 8.16, 1.06), (1.75, 2.88, .066), "dragon_mats", 1.22)
    for x in (3.65, 7.95, 11.62):
        frame(trim, (x, 12.56, 1.18), 1.73, 1.55, "kaiu_shoji")
    export("m381_dragon_mountain", room, MATS)
    export("dragon_inn_trim", trim, MATS)

    props = [
        ["dragon_inn_trim", 0., 0., 0., 1., 0.],
        ["dragon_inn_hearth", 8.05, 1.09, 9.60, .94, .03],
        ["hoshi_inn_bench", 6.29, 1.08, 8.46, .95, .06],
        ["hoshi_inn_bench", 10.15, 1.08, 8.45, .94, -.06],
        ["dragon_inn_hanging_screen", 12.23, 1.08, 10.48, .85, -.11],
        ["dragon_inn_shelves", 2.372, 1.057, 10.65, 1., -math.pi / 2],
        ["hoshi_tea_table", 5.27, 1.08, 11.23, .91, -.05],
    ]
    lights = [[8.05, 1.75, 9.60, 5.8, 2.2]]
    for x, z in ((2.73, 6.35), (12.62, 6.42), (11.29, 11.70)):
        props.append(["dragon_mountain_andon", x, 1.08, z, .93, .04])
        lights.append([x, 1.74, z, 4.5, 1.55])
    return {"terrain": "m381_dragon_mountain", "placements": props, "poolLights": lights}, len(events.ev)


def main(repo):
    _, _, gm, _, _ = variant(repo)
    import voxfile

    materials()
    structures()
    surfaces(HERE / "surface_sources/dragon_clean_lacquered_wood.png")
    shelf()
    door_models()
    sources = {}
    for name, dimensions, resolution in PROPS:
        source = (garden_stone(dimensions, resolution) if name == "togashi_garden_stone"
                  else convert_prop(name, dimensions, resolution, lower=.02))
        sources[name] = save(*source, voxfile)
        voxel_asset(name)
    path = STAGE / "index.json"
    index = json.loads(path.read_bytes())
    audit = {}
    for mid in MAPS:
        world, events = gm.make(mid)
        tag = f"{mid.lower()}_dragon_mountain"
        export(tag, terrain(gm, world), MATS)
        index[mid] = {"terrain": tag, **layout(gm, world)}
        audit[mid] = {"events": len(events.ev) if events else 0, "props": len(index[mid]["placements"])}
    index["M381"], events = mountain_inn(repo)
    audit["M381"] = {"events": events, "props": len(index["M381"]["placements"])}
    path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "dragon-mountains-layout.json").write_text(
        json.dumps({"maps": audit, "sources": sources}, indent=2), encoding="utf8")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
