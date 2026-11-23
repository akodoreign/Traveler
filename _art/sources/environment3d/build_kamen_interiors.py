"""Furnish Kamen's sake room, temple passages, monastery, and battle rooms."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_kaiu_kit import MATS as KAIU, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from kudo_rooms_worlds import KAMEN_ROOMS, KAMEN_TEMPLE, variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
MATS = {
    **KAIU,
    "kamen_rock": ("kamen_temple_wall.png", .93),
    "kamen_stone": ("kamen_temple_floor.png", .92),
    "kamen_wood": ("kamen_temple_wood.png", .92),
    "kamen_ink": ("kamen_temple_ink.png", .88),
}


def textures():
    for key, source, base in (
        ("wall", "kamen_temple_rock", (49, 58, 67)),
        ("floor", "kamen_old_flagstones", (78, 70, 61)),
        ("wood", "kamen_temple_cypress", (62, 40, 33)),
        ("ink", "kamen_temple_cypress", (29, 24, 37)),
    ):
        ref = Image.open(HERE / f"surface_sources/{source}.png").convert("RGB")
        diffuse = periodic(ref, 768) @ [.24, .63, .13]
        grain = np.clip(diffuse / max(1, np.median(diffuse)), .53, 1.48)
        rgb = np.asarray(base) * (.28 + .72 * grain[..., None])
        Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / f"tex/kamen_temple_{key}.png")


def ornaments():
    veil = Geometry()
    for i, width in enumerate((.75, 1.02, 1.15, 1.28, 1.34, 1.37, 1.33, 1.18, .99, .67)):
        y = .195 * i
        if i == 6:
            for a, b in ((-.66, -.50), (-.24, .24), (.50, .66)):
                box(veil, (a, -.025, y), (b - a, .08, .196), "kamen_ink")
        else:
            box(veil, (-width / 2, -.025, y), (width, .08, .196), "kamen_ink")
    export("kamen_wall_mask_shadow", veil, MATS)

    screen = Geometry()
    box(screen, (-.76, -.06, 0.), (1.52, .12, 1.37), "kaiu_wood")
    for x in (-.62, -.20, .22):
        box(screen, (x, -.087, .11), (.38, .05, 1.16), "kaiu_shoji")
        for y in (.47, .81):
            box(screen, (x, -.108, y), (.38, .035, .021), "kaiu_wood")
    for x in (-.61, .50):
        box(screen, (x, -.16, 0.), (.11, .32, .11), "kaiu_wood")
    export("kamen_low_shoji", screen, MATS)


def layer(gm, world):
    material = gm.T(4, 4)
    world.blk[world.blk == gm.STONEW] = material
    terrain = world_mesh(gm, world, {
        gm.STONE: "kamen_rock", gm.STONEW: "kamen_rock",
        gm.PLANK: "kamen_wood", gm.DARKWOOD: "kamen_ink",
        material: "kamen_stone",
    })
    for face, kind in zip(terrain.faces, terrain.materials, strict=True):
        if kind not in ("kamen_wood", "kamen_stone"):
            continue
        vertices = np.array([terrain.vertices[i] for i in face])
        if np.ptp(vertices[:, 2]) < .0001:
            for i in face:
                terrain.vertices[i] = terrain.vertices[i] + [0., 0., .045]
    return terrain


def room(mid):
    pieces = []
    lights = []

    def put(key, x, z, size=1., turn=0., height=1.057):
        pieces.append([key, x, height, z, size, turn])

    def lamp(x, z):
        put("kamen_temple_andon", x, z, .86)
        lights.append([x, 1.68, z, 4.70, 1.65])

    if mid == "M363":
        put("kamen_sweet_cup_counter", 5.27, 9.71, 1.02)
        put("kudo_carp_sake_rack", 3.08, 11.99, .91)
        put("kudo_carp_sake_rack", 5.31, 12.09, .84)
        put("hoshi_tea_table", 9.48, 6.93, 1.17)
        put("hoshi_tea_table", 12.31, 10.48, .91)
        put("kudo_bamboo_food_cover", 9.47, 6.94, 1.03, 0., 1.38)
        put("kamen_mask_display", 11.73, 11.80, .82)
        put("kamen_low_shoji", 8.67, 11.43, 1.07)
        put("kamen_low_shoji", 10.39, 11.43, 1.07)
        for x, z in ((2.69, 6.33), (7.16, 10.03), (12.48, 6.53)):
            lamp(x, z)
    else:
        put("kamen_monastery_dais", 8.60, 9.84, 1.36)
        put("kamen_wall_mask_shadow", 8.60, 12.92, 1.48, 0., 1.34)
        put("kamen_shrine_offering_stand", 11.34, 9.95, .95)
        put("kamen_rotted_sleep_mat", 13.87, 9.88, 1.08)
        put("kamen_rotted_sleep_mat", 14.77, 11.21, .93)
        for x, z in ((3.75, 7.15), (6.62, 11.63), (10.57, 11.62), (13.77, 7.09)):
            lamp(x, z)
    return pieces, lights


def temple(mid, gm, world, events):
    pieces = []
    lights = []
    arena = mid in ("M867", "M868")
    occupied = {(e["pos"][0], e["pos"][2]) for e in events.ev.values()} if events else set()

    def put(key, x, z, scale=1., yaw=0., radius=5):
        bx, bz = (x, z) if arena else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
        choices = [(a, b) for a in range(bx - radius, bx + radius + 1)
                   for b in range(bz - radius, bz + radius + 1)
                   if 0 <= a < world.w and 0 <= b < world.d and world.hgt[b, a] <= 2
                   and (a, b) not in occupied]
        if not choices:
            raise ValueError(f"No temple floor near {mid} {x} {z}")
        bx, bz = min(choices, key=lambda p: (p[0] - bx) ** 2 + (p[1] - bz) ** 2)
        occupied.add((bx, bz))
        y = (int(world.hgt[bz, bx]) + 1) * .5 + .049
        row = [key, bx * .5 + .25, y, bz * .5 + .25, scale, yaw]
        pieces.append(row)
        return row[1:4]

    def lamp(x, z, power=1.6):
        xx, y, zz = put("kamen_temple_andon", x, z, .92)
        lights.append([xx, y + .67, zz, 5.10, power])

    if mid == "M365":
        put("kamen_sun_statue", 62, 25, 1.20, -.16)
        put("kamen_sun_reliquary", 58, 25, .95, .15)
        put("kamen_shrine_offering_stand", 37, 20, .84, .09)
        for x, z in ((7, 18), (14, 19), (31, 19), (40, 19), (54, 23),
                     (61, 23), (64, 27), (73, 15), (77, 14)):
            lamp(x, z)
    elif mid == "M366":
        put("kamen_scriptorium_desk", 30, 17, 1.01, .15)
        put("kamen_rotted_sleep_mat", 32, 13, .83)
        put("kamen_sewn_face_shrine", 55, 23, 1.06, -.13)
        put("kamen_shrine_offering_stand", 58, 25, .98)
        for x, z in ((8, 17), (13, 21), (29, 13), (35, 17), (51, 20),
                     (56, 22), (59, 21), (73, 15), (76, 18)):
            lamp(x, z)
    else:
        for x in range(12, 121, 12):
            lamp(x, 86, 2.0)
        if mid == "M867":
            for x in (23, 59, 101):
                put("kamen_sewn_face_shrine", x, 89, 1.40)
        else:
            put("kamen_monastery_dais", 61, 89, 1.60)
            pieces.append(["kamen_wall_mask_shadow", 31.0, 1.18, 46.92, 2.00, 0.])
            for x in (39, 80):
                put("kamen_shrine_offering_stand", x, 90, 1.14)
    return pieces, lights


def main(repo):
    _, gm, _, _ = variant(repo, city=True)
    import voxfile

    textures()
    ornaments()
    sources = {}
    for key, dimensions, count in (
        ("kamen_shrine_offering_stand", (1.21, .58, .88), 40),
        ("kamen_sweet_cup_counter", (1.97, .79, 1.19), 43),
        ("kamen_scriptorium_desk", (1.10, .66, .73), 36),
        ("kamen_monastery_dais", (1.89, 1.44, .28), 41),
        ("kamen_sun_reliquary", (.59, .42, .78), 36),
        ("kamen_sewn_face_shrine", (1.32, .75, 1.73), 44),
        ("kamen_sun_statue", (.88, .66, 1.70), 43),
        ("kamen_temple_andon", (.39, .34, .87), 36),
        ("kamen_rotted_sleep_mat", (.94, .67, .29), 37),
    ):
        sources[key] = save(*convert_prop(key, dimensions, count, lower=.02), voxfile)
        voxel_asset(key)
    manifest = STAGE / "index.json"
    index = json.loads(manifest.read_bytes())
    report = {}
    for mid in (*KAMEN_ROOMS, *KAMEN_TEMPLE):
        world, events = gm.make(mid)
        name = f"{mid.lower()}_kamen_interior"
        export(name, layer(gm, world), MATS)
        props, lights = room(mid) if mid in KAMEN_ROOMS else temple(mid, gm, world, events)
        index[mid] = {"terrain": name, "placements": props, "poolLights": lights}
        report[mid] = {"props": len(props), "lanterns": len(lights), "events": len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "kamen-interiors-layout.json").write_text(
        json.dumps({"maps": report, "sources": sources}, indent=2), encoding="utf8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
