"""Finish the Oracle basalt shelves, crater lip and traversable lava crossing."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "layered-basalt"))
import build_layered_basalt as layered
from oracle_lighting import PRESETS


first = layered.first
STAGE = HERE / "native_environment"
TEXTURES = STAGE / "tex"
RECEIPT = HERE / "oracle-volcanic-receipt.json"
FLOW = "oracle_ember_current"
NORMAL = "oracle_cooling_joints_normal.png"
ROCK = "oracle_cooling_joints"
SHADE = "oracle_indigo_obsidian"
CHIP = "oracle_blue_break"
PAVER = "oracle_cut_paver"
CREASE = "oracle_pavers_shadow"

PIGMENTS = {
    layered.ASH: ((56, 43, 64), .27, .92),
    layered.TRAIL: ((160, 104, 59), .23, .87),
    layered.GLASS: ((27, 24, 50), .33, .69),
    layered.SCREE: ((44, 40, 79), .29, .88),
    layered.INDIGO: ((40, 44, 94), .22, .83),
    layered.OXIDE: ((71, 33, 48), .35, .87),
    layered.STONE: ((74, 57, 79), .28, .84),
    layered.SHRINE_FOOT: ((84, 52, 83), .23, .91),
    layered.SHRINE_LACQUER: ((189, 30, 21), .08, .78),
    layered.SHRINE_CEDAR: ((67, 22, 32), .15, .94),
    layered.SHRINE_ROOF: ((34, 62, 94), .15, .75),
    ROCK: ((36, 42, 94), .30, .81),
    SHADE: ((30, 29, 77), .25, .84),
    CHIP: ((43, 49, 104), .24, .86),
    PAVER: ((73, 63, 85), .22, .89),
    CREASE: ((40, 29, 49), .21, .92),
}
MATERIALS = {key: (key + ".png", rough) for key, (_, _, rough) in PIGMENTS.items()}
NORMALS = {key: NORMAL for key in PIGMENTS if key not in
           (layered.SHRINE_LACQUER, layered.SHRINE_CEDAR, layered.SHRINE_ROOF)}


def prepare_surfaces():
    src = first.SOURCE_IMAGES
    scan = np.asarray(Image.open(src / "rock_01_diff_1k.jpg").convert("L"), dtype=float)
    broad = gaussian_filter(scan, 9., mode="wrap")
    resolved = broad + .54 * (gaussian_filter(scan, 3.8, mode="wrap") - broad)
    tone = np.clip((resolved - np.median(resolved)) / (2.15 * resolved.std()), -.82, 1.)
    y, x = np.indices(tone.shape, dtype=float)
    seam = (np.cos(.010 * x + .026 * y + 2.1 * gaussian_filter(tone, 18, mode="wrap")) + 1.) * .5
    seam = seam ** 12 * np.maximum(tone + .32, 0.)
    fissure = np.sin((.042 * x - .017 * y) + 2.3 * np.sin(.015 * x + .008 * y)
                      + 3.4 * gaussian_filter(tone, 15, mode="wrap"))
    fracture = np.clip((abs(fissure) - .92) / .08, 0., 1.)
    for key, (pigment, detail, _) in PIGMENTS.items():
        texture = np.asarray(pigment) * (1. + detail * tone[..., None])
        if key in (ROCK, CHIP, SHADE, layered.GLASS):
            texture = texture + seam[..., None] * [13., 8., 20.]
            texture = texture * (1. - .20 * fracture[..., None])
        first.write_image(key + ".png", texture)
    normals = np.asarray(Image.open(src / "rock_01_nor_gl_1k.jpg").convert("RGB"), dtype=float)
    normals = gaussian_filter(normals / 127.5 - 1., (3.1, 3.1, 0), mode="wrap")
    normals[..., :2] *= .67
    normals /= np.maximum(np.linalg.norm(normals, axis=-1, keepdims=True), 1e-8)
    first.write_image(NORMAL, (normals + 1.) * 127.5)


def animate_lava():
    prior = HERE.parent / "native_environment/tex"
    for frame in range(first.FLAMES):
        source = np.asarray(Image.open(prior / f"{first.FLOW}{frame:02d}.png"), dtype=float)
        heat = np.clip((source[..., 1] - 30.) / 205., 0., 1.)
        body = np.stack((139. + 113. * heat ** .52,
                         21. + 180. * heat ** 1.67,
                         4. + 69. * heat ** 3.1), axis=-1)
        first.write_image(f"{FLOW}{frame:02d}.png", body)


def cleaved_wall(world, geo, toe, floor):
    """Put uneven buttresses behind the existing walkable shelf."""
    width, border = world.w * .5, world.d * .5 + 1.6
    rng = np.random.default_rng(world.w * 163 + world.d)
    xs = [0.]
    while xs[-1] + 1.45 < width:
        step = rng.uniform(1.48, 3.58)
        xs.append(min(width, xs[-1] + step))
    if xs[-1] < width:
        xs[-1] = width
    stretches = []
    for n, x in enumerate(xs):
        near = floor(x)
        crest = max(near + 2.4, layered.top(world, x, world.d * .5 - .25))
        crest += 1.17 + .74 * np.sin(x * .26) + .38 * np.cos(x * .67)
        notch = rng.uniform(-.33, .42)
        sweep = .49 * np.sin(x * .44) + .35 * np.cos(x * .19)
        seam = int(n % 3 != 0) * notch
        stretches.append([
            (x, toe - .49 + sweep * .45, near - .05),
            (x, toe + .23 + sweep * .63 + seam, near + .48 + notch),
            (x, toe + 1.04 + sweep + seam * .86, near + (crest - near) * (.50 + notch * .12)),
            (x, toe + 2.18 + sweep * .64 + notch * .55, near + (crest - near) * .82 + notch * .44),
            (x, min(border - 1., toe + 3.6 + sweep * .55 + notch), crest),
            (x, border + sweep * .55, crest - .67 + notch * .56),
        ])
    for i, (left, right) in enumerate(zip(stretches[:-1], stretches[1:])):
        for j, material in enumerate((layered.SCREE, ROCK, ROCK, ROCK, ROCK)):
            points = [left[j], right[j], right[j + 1], left[j + 1]]
            first.quads(geo, points, material, 4.8)
        if .88 * np.sin(xs[i] * .38) + .55 * np.cos(xs[i] * .81) < .20:
            continue
        # Overlap unequal columns into the face in local groups.
        for t in (.16, .52, .96):
            x = xs[i] + (xs[i + 1] - xs[i]) * t
            foot = left[1][1] + (right[1][1] - left[1][1]) * t + rng.uniform(-.18, .43)
            height = min((left[3][2] + right[3][2]) * .5 - floor(x), rng.uniform(1.45, 4.25))
            stone_pier(geo, x, foot, floor(x) - .12, rng.uniform(.44, .96), rng.uniform(.47, 1.03),
                       max(.8, height), rng.uniform(0., 6.28), body=SHADE)
    for edge, flip in ((stretches[0], False), (stretches[-1], True)):
        for p, q in zip(edge[:-1], edge[1:]):
            side = [p, q, (q[0], q[1], q[2] - 3.5), (p[0], p[1], p[2] - 3.5)]
            first.quads(geo, side[::-1] if flip else side, SHADE, 3.4)


def stone_pier(geo, x, z, bottom, half_x, half_z, height, skew, body=ROCK):
    """Build irregular column faces with a fractured cap and asymmetric lean."""
    angles = np.arange(7) * (np.pi / 3.) + skew
    outline = .91 + .13 * np.cos(angles * 3 + skew)
    corners = [(half_x * a * np.cos(t), half_z * a * np.sin(t))
               for t, a in zip(angles, outline, strict=True)]
    foot = [(x + u, z + v, bottom) for u, v in corners]
    shoulder = [(x + u * .94 + .13, z + v * .91, bottom + height * (.74 + .10 * np.sin(j + skew)))
                for j, (u,v) in enumerate(corners)]
    cap = [(x + u * .65 + .17, z + v * .72 + .13, bottom + height * (1. + .10 * np.sin(j * 1.4 + skew)))
           for j, (u,v) in enumerate(corners)]
    middle = (x + .11, z + .14, bottom + height * 1.05)
    colors = (SHADE, body, CHIP, body, SHADE, body)
    for i, material in enumerate(colors):
        j = i + 1
        first.quads(geo, [foot[i], foot[j], shoulder[j], shoulder[i]], material, 3.2)
        first.quads(geo, [shoulder[i], shoulder[j], cap[j], cap[i]], body, 3.)
        first.quads(geo, [cap[i], cap[j], middle, middle], body, 2.8)


def heart_of_crater(angle, rim_t):
    unit = np.hypot(np.cos(angle) / 3.33, np.sin(angle) / 2.22)
    oval = (1. + .079 * np.sin(angle * 5 + .23) + .049 * np.cos(angle * 8)) / unit
    return np.clip(oval / rim_t, .44, .70)


def fitted_causeway(geo):
    """Fit flush cut slabs within the clear five-metre lane across the rift."""
    rng = np.random.default_rng(896)
    grade = .547
    x_edges = np.array([29.53, 30.34, 31.36, 32.42, 33.43, 34.52])
    z_edges = np.array([29.70, 30.58, 31.64, 32.67, 33.57, 34.32])
    base = np.array([[(x, z) for x in x_edges] for z in z_edges])
    base += rng.uniform(-.22, .22, size=base.shape)
    base[0, :, 1] = np.maximum(base[0, :, 1], 29.60)
    base[-1, :, 1] = np.minimum(base[-1, :, 1], 34.43)
    base[0, [0, -1], 1] += .28
    base[-1, [0, -1], 1] -= .26
    for zj, (a, b) in enumerate(zip(base[:-1], base[1:])):
        for xi in range(len(x_edges) - 1):
            corners = np.array([a[xi], a[xi + 1], b[xi + 1], b[xi]])
            center = corners.mean(axis=0)
            lower = corners * .971 + center * .029
            upper = corners * .921 + center * .079
            y = grade + .039 + rng.uniform(-.008, .017)
            top = [(x, z, y) for x, z in upper]
            ground = [(x, z, grade + .002) for x, z in lower]
            mat = PAVER if (xi + 2 * zj) % 4 else layered.STONE
            first.quads(geo, top, mat, 2.2)
            for i in range(4):
                j = (i + 1) % 4
                first.quads(geo, [ground[i], ground[j], top[j], top[i]], CREASE, 2.4)
    for z, direction in ((29.53, -1), (34.47, 1)):
        center = first.arena_river_center(z)
        for i in (-1, 1):
            x = center + i * 1.10
            stone_pier(geo, x, z + direction * .29, grade - .014,
                       .36, .38, .23, 1.3 + .4 * i)


def small_crust(geo, mid, points):
    """Give the molten edge a broken shelf with occasional hanging plates."""
    rng = np.random.default_rng(int(mid[1:]))
    for i, (x, z, y) in enumerate(points):
        if mid == "M442":
            z += (.34 if i % 2 else -.34) + rng.uniform(-.05, .05)
            dx, dz = rng.uniform(.23, .47), rng.uniform(.14, .29)
        elif mid == "M443":
            x = 39.45 + 1.64 * (x - 39.45)
            z = 10.95 + 1.81 * (z - 10.95)
            dx, dz = rng.uniform(.23, .49), rng.uniform(.19, .34)
        else:
            x += (.47 if i % 2 else -.47)
            dx, dz = rng.uniform(.18, .32), rng.uniform(.25, .53)
        stone_pier(geo, x, z, y + .006, dx, dz,
                   rng.uniform(.058, .133), rng.uniform(0, 6.3))


def build(repo):
    live = repo / "_tools/rpgcobo-tool"
    baseline = first.read_json(HERE.parent / "oracle-volcanic-receipt.json")["maps"]
    previous = HERE.parent / "layered-basalt/native_environment"
    rows = first.read_json(previous / "index.json")
    catalog = first.read_json(live / first.CATALOG)
    gm = first.game_definition(repo)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    first.TEX = TEXTURES
    first.export_coast.STAGE = STAGE
    prepare_surfaces()
    animate_lava()
    retained = {m: {**row, "terrain": None, "water": None} for m, row in rows.items()}
    for key, data in first.resource_files(previous, retained).items():
        (STAGE / key).write_bytes(data)
    proof = {}
    for mid, row in rows.items():
        world, _ = gm.make(mid)
        original_row = {**catalog[mid], "rsetid": PRESETS[mid][0]}
        catalog_hash = first.digest(json.dumps(original_row, sort_keys=True).encode())
        world_hash = first.digest((live / f"project/data/mapdata/{mid}.bw").read_bytes())
        assert world_hash == baseline[mid]["world_hash"], mid
        assert catalog_hash == baseline[mid]["catalog_hash"] or first.digest(json.dumps(
            {**original_row, "bg": {"type": "skybox"}}, sort_keys=True).encode()) == baseline[mid]["catalog_hash"], mid
        formations = None
        if mid == "M442":
            ground, lava, effects = layered.stair_ravine(world, gm, cliffs=cleaved_wall)
        elif mid == "M443":
            ground, lava, effects = layered.crater_basin(world, gm, cliffs=cleaved_wall, pool_radius=heart_of_crater)
        else:
            ground, lava, effects, formations = layered.arena_crossing(
                world, catalog, cliffs=cleaved_wall, crossing=fitted_causeway)
        small_crust(ground, mid, effects)
        name = mid.lower() + "_oracle_cooling_banks"
        first.export(name, ground, MATERIALS, normal_maps=NORMALS, smooth_materials=(ROCK,))
        first.export(name + "_melt", lava, {"lava": (FLOW + "00.png", .57)})
        descriptor = STAGE / (name + "_melt.pm")
        descriptor.write_text(descriptor.read_text("utf8").replace("0xff600000", "0xff480000"),
                              encoding="utf8", newline="\n")
        lamps = [entry for entry in row["poolLights"] if entry[4] > 3.]
        glow = [[x, y + .38, z, 3.6, 1.34, 0xff712cff] for x,z,y in effects]
        rows[mid] = {**row, "terrain": name, "water": name + "_melt",
                     "waterSequence": {"prefix": FLOW, "frames": first.FLAMES, "seconds": 15.2},
                     "poolLights": lamps + glow}
        proof[mid] = {"catalog_hash": catalog_hash, "world_hash": world_hash,
                      "terrain_quads": len(ground.faces), "liquid_quads": len(lava.faces)}
        if formations is not None:
            proof[mid]["formations"] = formations
    (STAGE / "index.json").write_text(json.dumps(rows, separators=(",", ":")), encoding="utf8")
    assets = first.resource_files(STAGE, rows)
    RECEIPT.write_text(json.dumps({"maps": proof, "files": {key: first.digest(data) for key, data in assets.items()}},
                                  indent=2), encoding="utf8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    if args.stage:
        live = args.repo.resolve() / "_tools/rpgcobo-tool"
        profile = args.stage.resolve()
        if live.resolve() == profile:
            parser.error("Use a closed isolated playtest profile for --stage")
        catalog_file = profile / first.CATALOG
        live_catalog = first.read_json(live / first.CATALOG)
        profile_catalog = first.read_json(catalog_file)
        receipt = first.read_json(RECEIPT)["maps"]
        for mid, (prior, _) in PRESETS.items():
            row = {**live_catalog[mid], "rsetid": prior}
            assert first.digest(json.dumps(row, sort_keys=True).encode()) == receipt[mid]["catalog_hash"], mid
            background = row["bg"]
            if background["type"] == "tex":
                relative = Path("project") / background["tex"].lstrip("/")
                (profile / relative).parent.mkdir(parents=True, exist_ok=True)
                (profile / relative).write_bytes((live / relative).read_bytes())
            profile_catalog[mid] = row
        catalog_file.write_text(json.dumps(profile_catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
        first.STAGE, first.HERE = STAGE, HERE
        first.stage(args.repo.resolve(), profile)
    else:
        build(args.repo.resolve())
