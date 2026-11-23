"""Build the Buried Leaves market, autumn valleys, and the matching battle map."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

from autumn_worlds import MAPS, variant
from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from build_kudo_rooms import frame
from build_ojatara import shelter
from dragon_inn_joinery import DOOR_MODELS
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
PALETTE = {
    "autumn_leaf_bed": ("autumn_valley_leaf_litter", (71, 73, 37), .065),
    "autumn_road": ("ojatara_earth_v2", (113, 76, 52), .045),
    "autumn_ash": ("ojatara_earth_v2", (42, 37, 35), .040),
    "autumn_scorch": ("kamen_temple_rock", (29, 26, 31), .065),
    "autumn_salt": ("dragon_clean_wall_plaster", (157, 142, 119), .048),
    "autumn_rock": ("ojatara_rain_stone", (57, 53, 62), .042),
    "autumn_timber": ("dragon_clean_lacquered_wood", (73, 43, 32), .034),
    "autumn_wall": ("dragon_clean_wall_plaster", (144, 113, 82), .033),
    "autumn_roof": ("kawara_bluegrey", (47, 46, 66), .055),
    "autumn_indigo": ("ojatara_indigo_canvas", (44, 48, 88), .031),
    "autumn_brass": ("dragon_clean_wall_plaster", (128, 98, 50), .028),
}
STYLES = {**KAIU, **{key: (f"{key}.png", .93) for key in PALETTE}}
MODELS = (
    ("autumn_valley_maple", (3.25, 2.75, 3.58), 52),
    ("autumn_camp_cooking_tripod", (1.28, 1.06, 1.54), 48),
)
MARKET_TENTS = ((88, 6), (96, 9), (102, 5), (12, 6), (30, 8), (44, 5))


def textures():
    for key, (scan, color, strength) in PALETTE.items():
        pixels = periodic(Image.open(HERE / f"surface_sources/{scan}.png").convert("RGB"), 512)
        values = pixels @ [.26, .61, .13]
        broad = np.asarray(Image.fromarray(np.uint8(values)).filter(ImageFilter.GaussianBlur(11.)))
        detail = values - broad
        gain = 1 + strength * np.clip(detail / max(1., detail.std()), -2.1, 2.1)
        gain += .095 * (broad / max(1., np.median(broad)) - 1)
        rgb = np.asarray(color) * gain[..., None]
        Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / f"tex/{key}.png")


def structures():
    shelter("autumn_camp_indigo", 2.58, 1.86, 1.62, "indigo_canvas", "offwhite_canvas")
    shelter("autumn_camp_ochre", 2.61, 1.86, 1.57, "offwhite_canvas", "oxide_canvas")
    shelter("autumn_camp_oxide", 2.57, 1.88, 1.68, "oxide_canvas", "offwhite_canvas")
    shelter("autumn_officer_tent", 3.05, 2.05, 1.94, "indigo_canvas", "offwhite_canvas")
    stall = Geometry()
    for x in (-.93, .85):
        for z in (-.48, .38):
            box(stall, (x, z, 0.), (.082, .084, 1.73), "autumn_timber")
    box(stall, (-.99, -.58, 1.71), (1.98, 1.11, .10), "autumn_indigo")
    box(stall, (-.64, -.42, .71), (1.62, .47, .097), "autumn_timber")
    box(stall, (-.64, -.39, .076), (1.61, .16, .64), "autumn_wall")
    export("autumn_market_counter", stall, STYLES)

    banner = Geometry()
    box(banner, (-.11, -.095, 0.), (.22, .19, .18), "autumn_rock")
    box(banner, (-.032, -.027, .16), (.062, .059, 2.21), "autumn_timber")
    box(banner, (-.045, -.031, 2.16), (.72, .064, .069), "autumn_brass")
    box(banner, (.017, -.026, .98), (.61, .037, 1.17), "autumn_indigo")
    for y in (1.055, 1.19):
        box(banner, (.019, -.033, y), (.605, .010, .038), "autumn_brass")
    export("autumn_iuchi_banner", banner, STYLES)

    wreckage = Geometry()
    for x, z, height, length in ((-.69, -.35, .06, 1.32), (-.4, .02, .20, .98), (-.56, .40, .02, .53)):
        box(wreckage, (x, z, height), (length, .15, .132), "autumn_scorch")
    box(wreckage, (-.33, -.41, .025), (.18, .92, .14), "autumn_timber")
    export("autumn_crater_wreckage", wreckage, STYLES)

    for name, line1, line2 in (("welcome", "WELCOME", "ROAD INN"), ("stable", "PERSIMMON", "STABLE"),
                               ("iuchi", "SHIRO", "IUCHI"), ("hafuna", "HAFUNA", "FIELDS"),
                               ("soshi", "SHIRO NO", "SOSHI"), ("motobu", "MOTOBU", "CRATER"),
                               ("yotomo", "ROAD TO", "YOTOMO")):
        shop_board(f"autumn_{name}_board", line1, line2, "#534254")


def ground_atlas(world, styles, gm):
    width, depth = world.w * 12, world.d * 12
    rows, cols = np.indices((depth, width), sparse=True)
    tiles = world.blk[rows // 12, cols // 12]
    salt = {"autumn_leaf_bed", "autumn_ash", "autumn_scorch", "autumn_salt", "autumn_road"}
    tint = np.zeros((depth, width, 3), dtype=np.float32)
    total = np.zeros((depth, width), dtype=np.float32)
    for tile, material in styles.items():
        if material not in salt:
            continue
        mask = gaussian_filter((tiles == tile).astype(np.float32), 4.25)
        tint += mask[..., None] * np.asarray(PALETTE[material][1])
        total += mask
    tint /= np.maximum(total[..., None], .001)
    tint[total < .001] = PALETTE["autumn_leaf_bed"][1]
    x, z = cols / 24., rows / 24.
    grain = 1. + .029 * np.sin(x * 2.3 + np.sin(z * 1.4)) * np.cos(z * 1.7)
    grain = grain + .018 * np.random.default_rng(int(world.mid[1:])).standard_normal((depth, width))
    if world.mid == "M392":
        local_x, local_z = x * 2 - gm.PAD_X, z * 2 - gm.PAD_BOTTOM
        lane = local_x % 11
        wandering = .085 * np.sin(z * 1.8 + x * 1.3)
        furrow = np.exp(-(((((lane + wandering) - 1.45) % 1.8) - .9) / .20) ** 2)
        bed = (lane >= 2) & (lane <= 9) & (local_z > 4.6) & (local_z < 17.2)
        feather = np.clip(np.minimum(local_z - 4.6, 17.2 - local_z), 0., 1.)
        grain -= .16 * furrow * bed * feather
    tag = f"{world.mid.lower()}_autumn_ground"
    Image.fromarray(np.uint8(np.clip(tint * grain[..., None], 0, 255))).save(STAGE / "tex" / (tag + ".png"))
    return tag, salt


def surface_mesh(gm, world):
    styles = {gm.GRASS: "autumn_leaf_bed", gm.GRASS2: "autumn_leaf_bed", gm.GRASS3: "autumn_leaf_bed",
              gm.DIRT: "autumn_road", gm.ROAD: "autumn_road", gm.STONE: "autumn_rock", gm.STONEW: "autumn_rock",
              gm.WOOD: "autumn_timber", gm.DARKWOOD: "autumn_timber", gm.PLANK: "autumn_timber",
              gm.SL_GROUND: "autumn_ash", gm.SNOW: "autumn_salt", gm.PLASTER: "autumn_wall",
              gm.ROOF: "autumn_roof", gm.T(1): "autumn_scorch"}
    mesh = world_mesh(gm, world, styles)
    atlas, floors = ground_atlas(world, styles, gm)
    for index, face in enumerate(mesh.faces):
        material = mesh.materials[index]
        verts = np.asarray([mesh.vertices[i] for i in face])
        if material not in floors or np.ptp(verts[:, 2]) >= .0001:
            continue
        if np.cross(verts[1] - verts[0], verts[2] - verts[0])[2] <= 0:
            continue
        mesh.materials[index] = atlas
        mesh.uvs[index] = [(v[0] * 2 / world.w, 1. - v[1] * 2 / world.d) for v in verts]
        for i in face:
            mesh.vertices[i] = mesh.vertices[i] + [0., 0., .061]
    if world.mid == "M391":
        x, z = (18 + gm.PAD_X) * .5, (26 + gm.PAD_BOTTOM) * .5
        box(mesh, (x, z - .17, 2.014), (24., .204, .27), "autumn_rock", 2.3)
        for y in (2.73, 5.43):
            box(mesh, (x - .02, z - .038, y), (24.04, .091, .11), "autumn_timber", 2.1)
        for offset in (2.68, 6.68, 10.68, 14.68, 18.68, 22.68):
            frame(mesh, (x + offset, z - .08, 3.10), 1.46, 1.38, "kaiu_shoji")
    return mesh, atlas


def layout(gm, world):
    mid = world.mid
    arena = mid == "M875"
    placements, lights, doors = [], [], []
    plant = "autumn_valley_maple"
    lantern = "dragon_mountain_andon"
    rock = "togashi_garden_stone"

    def put(asset, x, z, size=1., yaw=0., wind=0., lift=0.):
        bx, bz = (x, z) if arena else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
        y = (int(world.hgt[bz, bx]) + 1) * .5 + lift
        row = [asset, bx * .5 + .25, y, bz * .5 + .25, size, yaw]
        placements.append(row + [wind] if wind else row)
        return row[1:4]

    def lamp(x, z):
        x, y, z = put(lantern, x, z, .88)
        lights.append([x, y + .57, z, 3.8, 1.35])

    def tent(x, z, key, size=1.):
        put(f"autumn_camp_{key}", x + 2, z + 1, size)

    def maple(x, z, size):
        put(plant, x, z, size, x * .43, .020)

    def entrance(x, z, event=None):
        bx, bz = x + gm.PAD_X, z + gm.PAD_BOTTOM
        cut, = (obj for obj in world.objs if obj["t"] == "fill" and obj["blk"] == gm.VOID
                and (obj["x"], obj["z"], obj["w"], obj["h"]) == (bx - 1, bz, 2, 4))
        grade = (int(world.hgt[bz - 1, cut["x"]]) + 1) * .5
        threshold = cut["y"] * .5
        stoop = {.5: "dragon_inn_stoop_half", 1.: "dragon_inn_stoop_full"}.get(threshold - grade)
        doors.append({"x": cut["x"] * .5, "y": threshold, "z": cut["z"] * .5 - .078,
                      "grade": grade, "event": event, "stoop": stoop, "models": DOOR_MODELS})

    if mid == "M387":
        for x, z, event in ((14, 22, 1), (30, 22, None), (61, 22, 87), (80, 23, None)):
            entrance(x, z, event)
        put("autumn_welcome_board", 8, 20)
        put("autumn_stable_board", 25, 20, .83)
        put("autumn_market_counter", 63, 21, .84)
        for x in (4, 24, 52, 70, 89, 103):
            lamp(x, 20)
        for i, (x, z) in enumerate(MARKET_TENTS):
            tent(x, z, ("ochre", "oxide", "indigo")[i % 3])
        for x, z in ((4, 27), (38, 26), (53, 25), (72, 26), (95, 25), (106, 10)):
            maple(x, z, .86 + x % 4 * .08)
        put("hoshi_inn_bench", 18, 21, .86)
    elif mid == "M389":
        for i, x in enumerate(range(4, 96, 9)):
            for j, z in enumerate((4, 22, 28)):
                tent(x + z % 3, z, ("ochre", "indigo", "ochre", "oxide")[(i + 3 * j) % 4], .94 + i % 3 * .054)
        for x in (20, 52, 80):
            put("autumn_camp_cooking_tripod", x + 2, 20, .93, x * .12)
            put("hoshi_inn_bench", x - 2, 21, .90, .14)
        put("autumn_market_counter", 32, 21, .87)
        lamp(10, 20)
        lamp(64, 20)
        for x, z in ((16, 8), (40, 32), (72, 10), (89, 8)):
            maple(x, z, .82 + z % 3 * .10)
    elif mid == "M390":
        for x, z, sign in ((96, 18, "iuchi"), (76, 15, "hafuna"), (36, 15, "soshi"),
                           (4, 17, "motobu"), (56, 19, "yotomo")):
            put(f"autumn_{sign}_board", x + 2, z, .85)
        for x, z in ((20, 22), (70, 23), (100, 22)):
            tent(x, z, "ochre", .88)
        for x, z in ((12, 23), (23, 7), (33, 24), (41, 7), (50, 23), (65, 23), (81, 7), (85, 24), (104, 6), (117, 23)):
            maple(x, z, .85 + x % 4 * .09)
        for x in range(7, 124, 13):
            put(rock, x, 27, 1.05 + x % 4 * .23, x * .34)
            put("wind_grass", x + 1, 11, .88, x * .29, .076)
    elif mid == "M391":
        for x, z in ((20, 18), (28, 10), (56, 9), (62, 18), (48, 22)):
            maple(x, z, .82 + z % 4 * .105)
        for x in (24, 32, 43, 55, 61):
            put("autumn_iuchi_banner", x, 24, .97, .1, .068)
        for x, z in ((27, 14), (33, 22), (49, 20), (57, 14)):
            put("dragon_garden_stone_lantern", x, z, .90)
            put("wind_grass", x - 1, z - 1, .76, x * .24, .16)
        put("bayushi_pond_basin", 36, 21, 1.04)
        put("bayushi_pond_basin", 49, 22, .94)
    elif mid == "M392":
        put("autumn_officer_tent", 65, 16, 1.0)
        put("hoshi_tea_table", 62, 19, 1.10, .04)
        for x in (59, 66):
            put("autumn_iuchi_banner", x, 16, .95, -.10, .060)
        for x in (11, 21, 55, 70, 87):
            put(rock, x, 29, .90 + x % 4 * .18, x * .44)
    elif mid == "M393":
        for x, z, size in ((36, 22, 1.19), (42, 26, 1.48), (50, 24, 1.3), (54, 27, 1.54),
                           (44, 30, .91), (58, 21, 1.30), (35, 29, .88), (60, 29, .75)):
            put(rock, x, z, size, x * .43)
        for x, z in ((21, 23), (34, 31), (56, 29), (66, 23), (75, 27)):
            put("shadowlands_burnt_stump", x, z, .74 + x % 3 * .105, x * .45)
        for x, z in ((33, 24), (53, 29), (61, 26)):
            put("autumn_crater_wreckage", x, z, .91 + x % 4 * .08, x * .44)
        put("dragon_togashi_stele", 29, 20, .76, .21)
        put("dragon_garden_stone_lantern", 26, 20, .77)
    elif mid == "M395":
        entrance(31, 14)
        for x, z in ((10, 8), (14, 20), (48, 10), (52, 22), (8, 24), (56, 6)):
            maple(x, z, .68 + x % 4 * .10)
            put("coast_flowers", x + 1, z - 1, 1.05, x * .20, .080)
        put("hoshi_inn_bench", 27, 12, .83)
        put("hoshi_tea_table", 36, 12, .86)
        for x in (23, 39):
            lamp(x, 12)
        for x, z in ((16, 14), (21, 11), (42, 11), (46, 16)):
            put("ojatara_flower_planter", x, z, .80, .08)
    else:
        for x, z in ((10, 86), (24, 93), (37, 89), (47, 92), (69, 92), (78, 85), (103, 89), (118, 85)):
            maple(x, z, .88 + x % 4 * .14)
            put(rock, x + 2, 95, 1.08 + x % 3 * .15, x * .33)
        for x, z in ((15, 84), (27, 78), (39, 84), (62, 87), (77, 84), (90, 78), (115, 82)):
            put("wind_grass", x, z, 1.12, x * .40, .082)
    return {"placements": placements, "poolLights": lights, "doors": doors}


def main(repo):
    _, _, gm, _, _ = variant(repo)
    import voxfile

    textures()
    structures()
    sources = {}
    for name, dimensions, resolution in MODELS:
        sources[name] = save(*convert_prop(name, dimensions, resolution, lower=.018), voxfile)
        voxel_asset(name)
    path = STAGE / "index.json"
    index = json.loads(path.read_bytes())
    audit = {}
    for mid in MAPS:
        world, events = gm.make(mid)
        name = mid.lower() + "_autumn_valley"
        mesh, atlas = surface_mesh(gm, world)
        export(name, mesh, {**STYLES, atlas: (atlas + ".png", .94)})
        row = {"terrain": name, **layout(gm, world)}
        index[mid] = row
        audit[mid] = {"events": len(events.ev) if events else 0, "placements": len(row["placements"])}
    path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "autumn-valley-layout.json").write_text(json.dumps({"maps": audit, "sources": sources}, indent=2),
                                                  encoding="utf8")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
