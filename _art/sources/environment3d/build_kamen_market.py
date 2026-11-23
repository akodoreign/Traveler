"""Build the Hospitality District, market stalls, and city combat streets."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from kensu_worlds import MARKET_MAPS, variants
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
MATS = {
    **KAIU,
    "market_stone": ("kamen_market_stone.png", .90),
    "market_walk": ("kamen_market_walk.png", .91),
    "market_trim": ("kamen_market_trim.png", .84),
    "market_tile": ("kamen_market_tile.png", .83),
}
SIGNS = {
    "kamen_sweetcup_sign": ("THE SWEET", "CUP", "#713745"),
    "kamen_crimson_sign": ("CRIMSON", "BLOSSOM", "#67383b"),
    "kamen_dream_sign": ("PLEASANT", "DREAM", "#4b445f"),
    "kamen_silk_sign": ("SILKEN", "TOUCH", "#674452"),
    "kamen_forge_sign": ("NANAME'S", "FORGE", "#463c40"),
    "kamen_brewery_sign": ("BLACK WATER", "BREWERY", "#514044"),
    "kamen_masks_sign": ("MASK", "MARKET", "#754251"),
}


def surfaces():
    image = Image.open(HERE / "surface_sources/kamen_old_flagstones.png").convert("RGB")
    texture = periodic(image, 768)
    value = texture @ [.26, .61, .13]
    grain = np.clip(value / max(1., np.median(value)), .54, 1.53)
    for key, color in (
        ("stone", (73, 69, 77)), ("walk", (103, 92, 83)),
        ("trim", (126, 38, 43)), ("tile", (36, 46, 64)),
    ):
        rgb = np.asarray(color) * (.24 + .76 * grain[..., None])
        Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / f"tex/kamen_market_{key}.png")


def gateway():
    gate = Geometry()
    for sign in (-1, 1):
        x = 1.58 * sign
        box(gate, (x - .31, -.34, 0.), (.62, .68, .33), "market_stone")
        box(gate, (x - .18, -.20, .27), (.36, .40, 2.70), "market_trim")
        box(gate, (x - .24, -.27, 2.51), (.48, .52, .22), "kaiu_wood")
        box(gate, (x - .28, -.25, .51), (.56, .50, .17), "kaiu_wood")
    box(gate, (-1.92, -.25, 2.70), (3.84, .50, .28), "market_trim")
    box(gate, (-1.98, -.40, 3.05), (3.96, .80, .22), "kaiu_wood")
    for layer in range(4):
        front = -.69 + layer * .13
        box(gate, (-2.14 + layer * .03, front, 3.24 + layer * .12),
            (4.28 - layer * .06, -2. * front, .14), "market_tile", 1.5)
    box(gate, (-2.20, -.16, 3.72), (4.40, .32, .13), "kaiu_wood")
    export("kamen_street_gateway", gate, MATS)


def pavement(gm, world):
    # Give the road a separate surface from masonry walls while retaining
    # the stock collision grid and all story points.
    floor_code = gm.T(4, 1)
    world.blk[world.blk == gm.STONEW] = floor_code
    terrain = world_mesh(gm, world, {
        gm.STONEW: "market_stone", gm.STONE: "market_stone",
        gm.ROAD: "market_walk", floor_code: "market_walk", gm.ROOF: "market_tile",
        gm.TORII: "market_trim",
    })
    for face, style in zip(terrain.faces, terrain.materials, strict=True):
        if style != "market_walk":
            continue
        vertices = np.asarray([terrain.vertices[i] for i in face])
        if np.ptp(vertices[:, 2]) < .0001:
            for i in face:
                terrain.vertices[i] = terrain.vertices[i] + [0., 0., .062]
    return terrain


def dress(gm, world, mid):
    arena = mid == "M866"
    placements = []
    lights = []

    def put(asset, x, z, scale=1., yaw=0., rise=0.):
        bx, bz = (x, z) if arena else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
        y = (int(world.hgt[bz, bx]) + 1) * .5 + rise
        row = [asset, bx * .5 + .25, y, bz * .5 + .25, scale, yaw]
        placements.append(row)
        return row[1:4]

    def lamp(x, z, scale=1.):
        xx, y, zz = put("kamen_hospitality_lantern", x, z, scale)
        lights.append([xx, y + 1.15 * scale, zz, 4.7, 1.42])

    doors = []
    if mid == "M362":
        put("kamen_street_gateway", 2, 17, 1.16, math.pi / 2)
        put("kamen_street_gateway", 106, 17, 1.10, math.pi / 2)
        for x in range(5, 111, 12):
            lamp(x, 20, .90 + .05 * (x % 3))
        for x, z in ((9, 7), (20, 8), (39, 7), (58, 7), (77, 8), (95, 8), (105, 9)):
            put("coast_pine", x, z, .74 + .08 * (x % 4), x * .31)
        for key, x in (("sweetcup", 17), ("crimson", 30), ("dream", 46), ("silk", 78)):
            put(f"kamen_{key}_sign", x, 21, .82)
        for x in (18, 32, 52, 84):
            put("kamen_mask_display", x, 23, .68, .11 * (x % 4))
        for x in (23, 38, 93):
            put("hoshi_inn_bench", x, 11, .98, .13 * (x % 3))
        front = (gm.PAD_BOTTOM + 22) * .5 - .118
        for center in (32, 49, 66, 83):
            x = (gm.PAD_X + center) * .5
            placements.extend([
                ["kudo_shut_door", x, 2.5, front, 1., 0.],
                ["town_door_stoop_half", x - .5, 2., front, 1., 0.],
            ])
        doors.append({"x": 19.5, "y": 2.5, "z": front, "grade": 2., "event": 2,
                      "stoop": "town_door_stoop_half"})
    elif mid == "M364":
        for x in range(43, 91, 9):
            put("kamen_merchant_awning", x, 25, 1.14, .06 * (x % 3))
            put("kamen_mask_display", x, 25, .78, .07)
            put("kudo_eel_basket", x + 2, 24, .80, .13)
        for key, x in (("forge", 5), ("brewery", 23), ("masks", 39)):
            put(f"kamen_{key}_sign", x, 21, .90)
        for x in range(6, 117, 11):
            lamp(x, 18 if x % 2 else 21, .89)
        for x, z in ((9, 23), (12, 24)):
            put("shinomen_smith_anvil", x, z, .77, .12)
        for x in (106, 110, 114):
            put("hoshi_trade_chest", x, 21, .95, .1 * (x % 2))
        front = (gm.PAD_BOTTOM + 23) * .5 - .118
        for center in (11, 28, 105):
            x = (gm.PAD_X + center) * .5
            placements.extend([
                ["kudo_shut_door", x, 2.5, front, 1., 0.],
                ["town_door_stoop_half", x - .5, 2., front, 1., 0.],
            ])
    else:
        for x in range(10, 122, 15):
            lamp(x, 88, 1.0)
        for x in (17, 39, 89, 109):
            put("kamen_merchant_awning", x, 93, 1.14, .04)
            put("kamen_mask_display", x, 89, .93)
        put("kamen_street_gateway", 62, 88, 1.20)
    return placements, lights, doors


def main(repo):
    _, _, gm, _, _ = variants(repo, city=True)
    import voxfile

    surfaces()
    gateway()
    for tag, (first, second, hue) in SIGNS.items():
        shop_board(tag, first, second, hue)
    sources = {}
    for key, dimension, resolution in (
        ("kamen_mask_display", (1.14, .57, 1.55), 38),
        ("kamen_merchant_awning", (2.74, 1.68, 2.49), 44),
    ):
        label,points,colors,pitch,source=convert_prop(key, dimension, resolution, lower=.02)
        if key=="kamen_merchant_awning":
            rgb=colors.astype(float)
            cloth=(points[:,2]>.62*points[:,2].max()) & (rgb[:,0]>rgb[:,1]+22)
            rgb[cloth]*=[.73,.36,.42]
            rgb[~cloth]*=[.72,.68,.59]
            colors=np.uint8(np.clip(rgb,0,255))
        sources[key] = save(label,points,colors,pitch,source,voxfile)
        voxel_asset(key)
    manifest = STAGE / "index.json"
    index = json.loads(manifest.read_bytes())
    report = {}
    for mid in MARKET_MAPS:
        world, events = gm.make(mid)
        key = f"{mid.lower()}_kamen_market"
        export(key, pavement(gm, world), MATS)
        props, lights, doors = dress(gm, world, mid)
        index[mid] = {"terrain": key, "placements": props, "poolLights": lights, "doors": doors}
        report[mid] = {"props": len(props), "lights": len(lights),
                       "events": len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "kamen-market-layout.json").write_text(
        json.dumps({"maps": report, "sources": sources}, indent=2), encoding="utf8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
