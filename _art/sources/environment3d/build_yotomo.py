"""Build the Yotomo village, recessed cave, two chambers, and combat backdrops."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

from build_autumn_valley import STYLES as AUTUMN, surface_mesh
from build_furnace import grid_surfaces
from build_hoshi_stall import box, shop_board
from dragon_inn_joinery import DOOR_MODELS
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save
from yotomo_worlds import MAPS, variant


HERE = Path(__file__).resolve().parent
CAVE_STYLES = ("", "yotomo_cave_floor", "yotomo_cave_wall", "yotomo_chalk")
MATERIALS = {**AUTUMN, **{k: (k + ".png", .92) for k in (*CAVE_STYLES[1:], "yotomo_cave_approach")}}
PROPS = (("autumn_yotomo_pigeon_house", (1.18, .85, 1.60), 43),
         ("autumn_yotomo_storage_vat", (.82, .77, .91), 40))


def surfaces():
    source = HERE / "surface_sources/autumn_yotomo_cave_limestone.png"
    gray = periodic(Image.open(source).convert("RGB"), 768) @ [.26, .61, .13]
    broad = np.asarray(Image.fromarray(np.uint8(gray)).filter(ImageFilter.GaussianBlur(12.)))
    fine = gray - broad
    grain = 1 + .053 * np.clip(fine / max(fine.std(), 1.), -2.0, 2.0)
    grain += .11 * (broad / max(np.median(broad), 1.) - 1.)
    for style, color in zip(CAVE_STYLES[1:], ((70, 64, 65), (43, 46, 54), (105, 100, 93)), strict=True):
        rgb = grain[..., None] * np.asarray(color)
        Image.fromarray(np.uint8(np.clip(rgb, 0., 255.))).save(STAGE / f"tex/{style}.png")
    fade = np.clip((np.linspace(0., 1., gray.shape[1]) - .22) / .62, 0., 1.)
    fade = fade**2 * (3. - 2. * fade)
    color = np.array([113, 76, 52]) * (1 - fade[:, None]) + np.array([36, 34, 37]) * fade[:, None]
    Image.fromarray(np.uint8(np.clip(grain[..., None] * color, 0., 255.))).save(
        STAGE / "tex/yotomo_cave_approach.png")


def structures():
    shop_board("yotomo_dovecote_board", "YOTOMO", "DOVECOTES", "#4b4b49")
    shop_board("yotomo_east_cave_board", "EAST", "PIGEON CAVE", "#484754")
    perch = Geometry()
    for x in (-.62, .57):
        box(perch, (x, -.076, 0.), (.062, .071, 1.00), "autumn_timber")
    for y in (.47, .82):
        box(perch, (-.67, -.095, y), (1.34, .09, .071), "autumn_timber")
    export("yotomo_bird_perch", perch, MATERIALS)


def cave_mesh(gm, world):
    battle = world.mid in ("M876", "M877")
    rock = world.blk == (gm.STONE if battle else gm.CAVE_WALL)
    if not battle:
        rock |= world.hgt > 3
    edges = np.roll(rock, 1, axis=0) | np.roll(rock, -1, axis=1)
    z, x = np.indices(world.blk.shape)
    seams = np.cos(z * .49 + x * .21) + .49 * np.sin(x * .88) > 1.18
    tile = np.where(world.blk != 0, 1, 0)
    tile[rock & (world.blk != 0)] = 2
    tile[(tile == 1) & ((edges & seams) | (world.blk == gm.SNOW))] = 3
    return grid_surfaces(tile, world.hgt.astype(int), CAVE_STYLES, wall_style="yotomo_cave_wall", fluid=-1)


def scene(gm, world):
    mid = world.mid
    battle = mid in ("M876", "M877")
    props, lights, doors = [], [], []

    def put(asset, x, z, size=1., yaw=0., lift=0.):
        bx, bz = (x, z) if battle else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
        y = (int(world.hgt[bz, bx]) + 1) * .5 + lift
        row = [asset, bx * .5 + .25, y, bz * .5 + .25, size, yaw]
        props.append(row)
        return row[1:4]

    def lamp(x, z, size=1.):
        x, y, z = put("dragon_mountain_andon", x, z, size)
        lights.append([x, y + .70 * size, z, 4.8, 1.64])

    if mid == "M396":
        for x in (8, 22, 46, 60):
            bx, bz = x + 4 + gm.PAD_X, 22 + gm.PAD_BOTTOM
            cut, = (obj for obj in world.objs if obj["t"] == "fill" and obj["blk"] == gm.VOID
                    and (obj["x"], obj["z"], obj["w"], obj["h"]) == (bx - 1, bz, 2, 4))
            doors.append({"x": cut["x"] * .5, "y": cut["y"] * .5, "z": cut["z"] * .5 - .078,
                          "grade": 2., "event": None, "stoop": "dragon_inn_stoop_half", "models": DOOR_MODELS})
            put("autumn_yotomo_pigeon_house", x + 7, 20, .99, .12)
            put("yotomo_bird_perch", x + 2, 21, .94, -.10)
            lamp(x - 1, 20, .86)
        for x, z in ((8, 9), (24, 8), (40, 22), (53, 8), (75, 20), (79, 9)):
            put("autumn_valley_maple", x, z, .90 + x % 4 * .09, x * .43)
        put("yotomo_dovecote_board", 6, 18, .90)
        put("yotomo_east_cave_board", 94, 18, .86, .06)
        lamp(102, 16, .86)
        for x, z, size in ((97, 16, .83), (99, 24, 1.21), (103, 26, 1.35), (103, 13, 1.40)):
            put("togashi_garden_stone", x, z, size, .37 * x)
    elif mid == "M397":
        for x, z in ((11, 6), (14, 14), (27, 16), (45, 17), (58, 27), (60, 34)):
            lamp(x, z, .83)
        for x, z in ((12, 4), (21, 17), (41, 22), (58, 32)):
            put("yotomo_bird_perch", x, z, .90, .19 * x)
        for x, z in ((15, 8), (22, 20), (43, 16), (55, 24), (61, 29)):
            put("togashi_garden_stone", x, z, .62 + x % 4 * .09, .31 * x)
    elif mid == "M398":
        for x, z in ((31, 7), (27, 16), (25, 25), (44, 18), (48, 27)):
            lamp(x, z, .89)
        for x, z in ((28, 26), (42, 27), (35, 29), (23, 25), (47, 22)):
            put("autumn_yotomo_storage_vat", x, z, 1.18 + x % 3 * .14, .31 * x)
        for x, z in ((25, 19), (46, 24), (37, 28)):
            put("yotomo_bird_perch", x, z, 1.11, .19 * x)
    else:
        for x in (9, 28, 53, 77, 99, 119):
            lamp(x, 88 + x % 3, 1.04)
            put("togashi_garden_stone", x + 2, 89 + x % 3, 1.01 + x % 4 * .12, .27 * x)
        if mid == "M877":
            for x, z in ((29, 90), (43, 88), (56, 91), (68, 89), (87, 91), (103, 90)):
                put("autumn_yotomo_storage_vat", x, z, 1.17 + x % 3 * .16, .28 * x)
        else:
            for x, z in ((34, 90), (49, 89), (73, 91), (106, 90)):
                put("yotomo_bird_perch", x, z, 1.25, .12 * x)
    return {"placements": props, "poolLights": lights, "doors": doors}


def main(repo):
    _, _, gm, _, _ = variant(repo)
    import voxfile

    surfaces()
    structures()
    sources = {}
    for name, dimensions, resolution in PROPS:
        model = convert_prop(name, dimensions, resolution, lower=.035)
        sources[name] = save(*model, voxfile)
        voxel_asset(name)
    path = STAGE / "index.json"
    index = json.loads(path.read_bytes())
    audit = {}
    for mid in MAPS:
        world, events = gm.make(mid)
        tag = f"{mid.lower()}_yotomo"
        if mid == "M396":
            mesh, floor = surface_mesh(gm, world)
            mouth = (world.w - 15) * .5
            end = world.w * .5
            mesh.quad([(mouth-1.10,11.10,2.091), (end,11.10,2.091), (end,13.37,2.091), (mouth-1.10,13.37,2.091)],
                      [(0.,0.),(1.,0.),(1.,1.),(0.,1.)], "yotomo_cave_approach")
            # The portal lies before this render-only slab beyond the map boundary.
            box(mesh, (end + .085, 10.95, 2.), (.20, 2.67, 3.02), "autumn_scorch", 2.3)
            export(tag, mesh, {**MATERIALS, floor: (floor + ".png", .94)})
        else:
            mesh, liquid = cave_mesh(gm, world)
            assert not liquid.faces
            export(tag, mesh, MATERIALS)
        row = {"terrain": tag, **scene(gm, world)}
        index[mid] = row
        audit[mid] = {"events": len(events.ev) if events else 0, "placements": len(row["placements"])}
    path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "yotomo-layout.json").write_text(json.dumps({"maps": audit, "sources": sources}, indent=2), encoding="utf8")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
