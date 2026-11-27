"""Build an isolated scenery candidate for the Mieko cellar."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter, zoom

import export_coast
import install_environment_rows
import mieko_cellar_worlds
from build_furnace import grid_surfaces
from build_hoshi_stall import box


def cave_backdrop(ground, world):
    for x in np.arange(-36., world.w * .5 + 36., 1.):
        for y in np.arange(0., 40., 1.):
            points = [(a, world.d * .5 + 1.4 * np.sin(a * .21 + b * .17)
                       + .48 * np.sin(a * .73 - b * .33)
                       + .25 * np.cos(a * 1.13 + b * .61), b)
                      for a, b in ((x, y), (x + 1., y), (x + 1., y + 1.), (x, y + 1.))]
            ground.quad(points, [(a / 3.8, b / 3.8) for a, _, b in points],
                        "harbour_tunnel_rock")
    for z in np.arange(-24., world.d * .5 + 2., 1.):
        for y in np.arange(0., 40., 1.):
            points = [(world.w * .5 + 1.5 + .55 * np.sin(a * .29 + b * .2),
                       a, b) for a, b in ((z, y), (z + 1., y), (z + 1., y + 1.), (z, y + 1.))]
            ground.quad(points, [(a / 3.8, b / 3.8) for _, a, b in points],
                        "harbour_tunnel_rock")


def build(overlay):
    stage = Path(overlay) / "resource" / "native_environment"
    _, _, candidate, _, _ = mieko_cellar_worlds.variant()
    world, _ = candidate.make("M295")
    kinds = np.ones(world.blk.shape, dtype=np.uint8)
    kinds[10:20, 6:26] = 2
    ground, _ = grid_surfaces(kinds, np.ones_like(world.hgt),
                              ("", "floor", "estate_floor"), wall_style="rock")
    source = np.asarray(Image.open(stage / "tex" / "harbour_tunnel_rock_vivid.png")
                        .convert("L"), dtype=float)
    detail = source / max(source.mean(), 1.)
    tint = detail[..., None] * np.array([42., 67., 77.])
    Image.fromarray(np.uint8(tint.clip(0, 255))).save(stage / "tex" / "m295_cellar_rock_v4.png")

    rock = world.hgt > 3
    edge, nearest = distance_transform_edt(rock, return_indices=True)
    zz, xx = np.indices(rock.shape, dtype=float)
    far_side = gaussian_filter((zz >= nearest[0]).astype(float), 1.5)
    crest = 1.42 + 2.8 * far_side + .16 * np.sin(xx * .31 + zz * .27)
    height = .99 + np.clip((edge - .3) / 2.2, 0., 1.) * (crest - .99)
    height = gaussian_filter(height, 1.05)
    height[~rock] = .99
    height = zoom(height, 2, order=1)
    visible = height > 1.049
    for z, x in np.argwhere(visible[:-1, :-1] | visible[1:, :-1] |
                            visible[1:, 1:] | visible[:-1, 1:]):
        points = [(a * .25 + .25, b * .25 + .25, height[b, a])
                  for b, a in ((z, x), (z, x + 1), (z + 1, x + 1), (z + 1, x))]
        ground.quad(points, [((a + .2 * b) / 3.5, (b + c) / 3.5)
                             for a, b, c in points], "harbour_tunnel_rock")
    cave_backdrop(ground, world)

    for obj in world.objs:
        if obj["t"] not in ("fill", "blk") or obj["blk"] != 227:
            continue
        x, y, z = (obj[k] * .5 for k in ("x", "y", "z"))
        w, h, d = (obj.get(k, 1) * .5 for k in ("w", "h", "d"))
        box(ground, (x, z, y), (w, d, h), "wood", 2.6)

    for x, z in ((36, 18), (62, 27), (76, 41)):
        low = high = z
        while low > 0 and world.hgt[low - 1, x] == 1:
            low -= 1
        while high + 1 < world.d and world.hgt[high + 1, x] == 1:
            high += 1
        for side in (low, high + 1):
            box(ground, (x * .5, side * .5 - .08, 1.), (.20, .16, 2.55), "wood", 2.6)
        box(ground, (x * .5, low * .5 - .08, 3.40),
            (.20, (high + 1 - low) * .5 + .16, .15), "wood", 2.6)

    old_stage = export_coast.STAGE
    export_coast.STAGE = stage
    try:
        export_coast.export(
            "m295_mieko_cellar_candidate_v6", ground,
            {"floor": ("harbour_tunnel_floor_vivid.png", .93),
             "estate_floor": ("castle_bayushi_floor.png", .93),
             "harbour_tunnel_rock": ("m295_cellar_rock_v4.png", .93),
             "wood": ("castle_bayushi_wood.png", .9)},
            smooth_materials=("harbour_tunnel_rock",))
        lamps = [(32, 13), (46, 22), (56, 20), (68, 28), (76, 36), (84, 40),
                 (87, 16), (72, 12)]
        placements = [["snake_den_stone_lantern", x * .5 + .25, 1., z * .5 + .25, .6, 0.]
                      for x, z in lamps]
        placements += [["cakon_staved_barrel", x * .5 + .25, 1., z * .5 + .25, .75, .2]
                       for x, z in ((40, 24), (56, 36), (92, 24))]
        placements += [["smooth_coast_salt_crate", x * .5 + .25, 1., z * .5 + .25, .72, .12]
                       for x, z in ((42, 23), (58, 36), (91, 23))]
        placements += [["hoshi_salt_sack", x * .5 + .25, 1., z * .5 + .25, .65, .25]
                       for x, z in ((38, 23), (59, 38), (88, 23))]
        row = {"terrain": "m295_mieko_cellar_candidate_v6", "placements": placements,
               "poolLights": [[x * .5 + .25, 1.7, z * .5 + .25, 4., 1.1, 0xffbb59ff]
                              for x, z in lamps],
               "hideStockScenery": True}
        (stage / "index.json").write_text(json.dumps({"M295": row}), encoding="utf-8")
    finally:
        export_coast.STAGE = old_stage


def install_preview(overlay, profile):
    profile = Path(profile).resolve()
    if profile == (mieko_cellar_worlds.ROOT / "_tools" / "rpgcobo-tool").resolve():
        raise ValueError("Use an isolated profile")
    index = profile / "project" / "resource" / "native_environment" / "index.json"
    old = json.loads(index.read_bytes()).get("M295")
    if old and old.get("terrain") not in ("m295_mieko_cellar_candidate",
                                           "m295_mieko_cellar_candidate_v2",
                                           "m295_mieko_cellar_candidate_v3",
                                           "m295_mieko_cellar_candidate_v4",
                                           "m295_mieko_cellar_candidate_v5",
                                           "m295_mieko_cellar_candidate_v6"):
        raise ValueError("Refusing to replace an unexpected M295 environment")
    previous = install_environment_rows.STAGE
    install_environment_rows.STAGE = Path(overlay) / "resource" / "native_environment"
    try:
        install_environment_rows.install(profile, ("M295",), preserve_existing=True,
                                         replace_existing=bool(old))
    finally:
        install_environment_rows.STAGE = previous


if __name__ == "__main__":
    build(sys.argv[1])
    install_preview(sys.argv[1], sys.argv[2])
