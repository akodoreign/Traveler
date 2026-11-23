"""Stage the ruined bailey, keep, lord's hall, and the matching combat hall."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_kaiu_kit import MATS as WALL_MATS, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
MAPS = ("M461", "M462", "M463", "M808")
MATERIAL_REPLACEMENTS = {
    "kaiu_stone": ("hiruma_ishi", (104, 100, 104), .92),
    "kaiu_wood": ("hiruma_scorched_cedar", (56, 41, 44), .92),
    "kaiu_roof": ("hiruma_kawara", (65, 73, 85), .85),
    "kaiu_plaster": ("hiruma_stained_plaster", (168, 154, 144), .93),
    "cliff": ("hiruma_ash", (79, 66, 81), .96),
    "path": ("hiruma_courtyard", (117, 95, 89), .90),
}


def surface_materials():
    materials = dict(WALL_MATS)
    for source, (name, color, roughness) in MATERIAL_REPLACEMENTS.items():
        raw = Image.open(STAGE / "tex" / WALL_MATS[source][0]).convert("RGB")
        intensity = np.asarray(raw) @ [.24, .64, .12]
        relief = intensity / max(1., np.median(intensity))
        rgb = np.asarray(color) * np.clip(relief[..., None], .48, 1.65)
        image = name + ".png"
        Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).save(STAGE / "tex" / image)
        materials[name] = (image, roughness)
    materials["hiruma_taint"] = ("waste_taint.png", .93)
    return materials


def stage_props(voxfile):
    props = {}
    for key, extent in (
        ("hiruma_gate_ruin", (4.68, 2.14, 3.69)),
        ("hiruma_ancestor_tablets", (1.59, .63, 1.22)),
        ("hiruma_fallen_standard", (1.43, .82, 1.45)),
    ):
        tag, points, rgb, pitch, source = convert_prop(key, extent, 48, lower=.022)
        if tag == "hiruma_gate_ruin":
            # The playable aperture stays clear even if the generated mesh
            # contains drapery or rubble between the gateposts.
            center = (points[:, 0].max() + 1) * .5
            occupied = (abs((points[:, 0] + .5 - center) * pitch[0]) >= 1.10) | (
                points[:, 2] * pitch[2] >= 2.40)
            points, rgb = points[occupied], rgb[occupied]
        props[key] = save(tag, points, rgb, pitch, source, voxfile)
        voxel_asset(key)
    return props


def ruin_surface(gm, world, exit_position=None):
    original_ground = world.blk.copy()
    if world.mid == "M461":
        z,x = np.indices(world.blk.shape)
        center = gm.PAD_BOTTOM + 16 + 2.3 * np.sin((x - gm.PAD_X) * .117)
        ramp = np.clip((x - (exit_position[0] - 29)) / 25., 0., 1.)
        center += (exit_position[2] - center) * ramp
        walk = (x >= gm.PAD_X) & (abs(z-center) <= 3.2)
        world.blk[walk & np.isin(world.blk, (gm.SL_GROUND, gm.SL_ASH))] = gm.ROAD
    shell = world_mesh(gm, world, {gm.TARSTAIN: "hiruma_taint"})
    names = {old: item[0] for old, item in MATERIAL_REPLACEMENTS.items()}
    shell.materials = [names.get(name, name) for name in shell.materials]
    world.blk[:] = original_ground
    return shell


def hall_joinery(materials):
    screen = Geometry()
    for x in (-1.54, -.52, .50, 1.52):
        box(screen, (x, -.07, 0), (.10, .15, 2.19), "hiruma_scorched_cedar")
    for y in (0, .60, 2.10):
        box(screen, (-1.54, -.07, y), (3.16, .15, .09), "hiruma_scorched_cedar")
    for x, height in ((-1.43, 1.24),(-.42, 1.51),(.61,.84)):
        box(screen, (x,-.037,.678),(.90,.070,height), "hiruma_stained_plaster")
    export("hiruma_hall_screen", screen, materials)

    gate = Geometry()
    for x in (-1.49, 1.24):
        box(gate, (x-.12,-.37,0),(.54,.72,.47),"hiruma_ishi")
        box(gate, (x,-.23,.36),(.29,.43,2.32),"hiruma_scorched_cedar")
    box(gate,(-1.58,-.22,2.49),(3.22,.43,.24),"hiruma_scorched_cedar")
    for x in (-3.05,1.75):
        for run,width,height in ((0.,1.32,.55),(.11,1.21,.43),(.29,.87,.30)):
            box(gate,(x+run,-.37,height-.12),(width,.72,.35),"hiruma_ishi")
    export("hiruma_gate_structure",gate,materials)

    altar = Geometry()
    box(altar,(-1.45,-.60,0),(2.90,1.21,.145),"hiruma_ishi")
    box(altar,(-1.25,-.38,.128),(2.48,.813,.107),"hiruma_scorched_cedar")
    for x in (-1.02,.93):
        box(altar,(x,.35,.22),(.12,.12,1.91),"hiruma_scorched_cedar")
    box(altar,(-1.02,.35,1.99),(2.08,.12,.14),"hiruma_scorched_cedar")
    box(altar,(-.87,.39,.29),(1.72,.07,1.62),"hiruma_stained_plaster")
    export("hiruma_ancestor_altar",altar,materials)


def main(repo):
    sys.path.insert(0, str(repo / "tools"))
    import gen_maps as gm
    import voxfile

    materials = surface_materials()
    sources = stage_props(voxfile)
    hall_joinery(materials)
    path = STAGE / "index.json"
    index = json.loads(path.read_bytes())
    report = {}
    for mid in MAPS:
        world, events = gm.make(mid)
        exit_id = {"M461": "#3#", "M462": "#4#"}.get(mid)
        exit_position = events.ev[exit_id]["pos"] if exit_id else None
        if mid == "M462" and "--open-altar" in sys.argv[2:]:
            # Match the candidate world while it is under native review.
            # The open altar has the same interaction point as the old shrine.
            world.objs = [obj for obj in world.objs if not old_altar_object(gm, obj)]
        terrain = f"{mid.lower()}_hiruma_ruin"
        part = ruin_surface(gm, world, exit_position)
        export(terrain, part, materials)
        props = []

        def put(key, x, z, scale=1., yaw=0., raise_by=0., padded=False):
            bx, bz = (x, z) if padded or mid == "M808" else (x + gm.PAD_X, z + gm.PAD_BOTTOM)
            y = .5 * (world.hgt[bz, bx] + 1) + raise_by
            props.append([key, bx*.5+.25, float(y), bz*.5+.25, scale, yaw])

        if exit_position:
            x, _, z, _ = exit_position
            scale = 1.04 if mid == "M461" else .87
            for piece in ("hiruma_gate_ruin", "hiruma_gate_structure"):
                put(piece, x-4, z, scale, math.pi/2, padded=True)

        if mid == "M461":
            put("hiruma_fallen_standard", 10, 22, .97, -.43)
            put("hiruma_fallen_standard", 91, 24, 1.10, .31)
            put("shadowlands_dead_cedar", 14, 27, 1.22, .45)
            put("shadowlands_dead_cedar", 63, 28, 1.35, -.60)
            for x,z in ((17,8),(32,25),(48,11),(66,22),(77,12),(98,24)):
                put("shadowlands_shards",x,z,1.0,(x%7)*.24)
        elif mid == "M462":
            put("hiruma_ancestor_altar", 47, 20, 1.)
            put("hiruma_ancestor_tablets", 47, 20, .93, math.pi, .233)
            put("hoshi_andon",44,20,.92)
            put("hoshi_andon",50,20,.92)
            put("hiruma_hall_screen", 32, 24, .93, -.04)
            put("hiruma_hall_screen", 59, 24, .90, .07)
            put("hiruma_fallen_standard", 14, 22, .74, .36)
        elif mid == "M463":
            put("hiruma_hall_screen", 12, 19, .89)
            put("hiruma_hall_screen", 36, 19, .89)
            put("hiruma_fallen_standard", 17, 17, .75, -.46)
            put("hiruma_fallen_standard", 31, 17, .75, .46)
        else:
            for x in (13, 47, 78, 112):
                put("hiruma_hall_screen", x, 80, 1.11, .05 if x<64 else -.05)
            put("hiruma_fallen_standard", 20, 73, .98, -.32)
            put("hiruma_fallen_standard", 47, 74, .98, .43)
        index[mid] = {"terrain": terrain, "placements": props}
        report[mid] = {"terrain_quads": len(part.faces), "placements": props}
    path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "hiruma-castle-layout.json").write_text(json.dumps({
        "maps": report, "generated_props": sources,
    }, indent=2), encoding="utf8")


def old_altar_object(gm, obj):
    x, z = obj["x"] - gm.PAD_X, obj["z"] - gm.PAD_BOTTOM
    return (
        (obj["t"] in ("fill", "blk") and 42 <= x <= 51 and 17 <= z <= 23)
        or (obj["t"] == "fb" and (x, z) in ((42, 19), (52, 19)))
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
