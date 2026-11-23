"""Furnish the Welcome Road inn and Shiro no Soshi with fitted interior meshes."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

from build_hoshi_stall import box
from build_kaiu_kit import world_mesh
from build_kudo_rooms import MATS as ROOM, frame
from dragon_inn_joinery import MATERIALS as JOINERY, ceramic, floorboards
from export_coast import Geometry, STAGE, export
from kudo_rooms_worlds import variant
from prepare_coast import periodic


HERE = Path(__file__).resolve().parent
STYLES = {**ROOM, **JOINERY, "autumn_wall": ("autumn_wall.png", .93),
          "autumn_brocade": ("autumn_brocade.png", .88), "autumn_soshi_lacquer": ("autumn_soshi_lacquer.png", .76),
          "autumn_reed_mats": ("autumn_reed_mats.png", .94)}


def swatches():
    for key, scan, palette, strength in (
        ("autumn_brocade", "autumn_soshi_brocade", (92, 25, 39), .15),
        ("autumn_soshi_lacquer", "dragon_clean_lacquered_wood", (51, 29, 37), .035),
        ("autumn_reed_mats", "kudo_inn_mat", (142, 108, 63), .055),
    ):
        tile = periodic(Image.open(HERE / f"surface_sources/{scan}.png").convert("RGB"), 512)
        value = tile @ [.26, .61, .13]
        broad = np.asarray(Image.fromarray(np.uint8(value)).filter(ImageFilter.GaussianBlur(13.)))
        detail = value - broad
        gain = 1 + strength * np.clip(detail / max(1., detail.std()), -2.1, 2.1)
        rgb = np.uint8(np.clip(np.asarray(palette) * gain[..., None], 0., 255.))
        Image.fromarray(rgb).save(STAGE / f"tex/{key}.png")


def fittings():
    notice = Geometry()
    for x in (-.48, .44):
        box(notice, (x, 0., 0.), (.059, .066, 1.40), "inn_beam")
    box(notice, (-.53, -.03, .57), (1.06, .093, .79), "inn_cypress")
    for x, z, height in ((-.42, -.041, .82), (-.12, -.046, .77), (.15, -.046, .90)):
        box(notice, (x, z, height), (.21, .013, .33), "inn_cream")
        for line in range(3):
            box(notice, (x + .04 + line * .055, z - .003, height+.053), (.008, .004, .23), "inn_beam")
    export("autumn_petition_board", notice, STYLES)

    partition = Geometry()
    for x in (-.65, .60):
        box(partition, (x, -.13, 0.), (.066, .28, .078), "autumn_soshi_lacquer")
        box(partition, (x, -.044, .075), (.069, .071, 1.64), "autumn_soshi_lacquer")
    for y in (.17, 1.68):
        box(partition, (-.68, -.05, y), (1.36, .082, .065), "autumn_soshi_lacquer")
    box(partition, (-.576, -.023, .225), (1.168, .023, 1.454), "autumn_brocade", .57)
    for y in (.25, 1.60):
        box(partition, (-.584, -.028, y), (1.185, .021, .030), "inn_heartwood")
    export("autumn_soshi_partition", partition, STYLES)

    desk = Geometry()
    for x in (-.48, .38):
        for z in (-.245, .166):
            box(desk, (x, z, 0.), (.104, .092, .32), "autumn_soshi_lacquer")
    box(desk, (-.54, -.28, .29), (1.08, .58, .087), "autumn_soshi_lacquer")
    box(desk, (-.483, -.29, .295), (.969, .024, .027), "inn_heartwood")
    box(desk, (-.395, -.181, .378), (.52, .30, .019), "inn_cream")
    for x in (-.399, .094):
        box(desk, (x, -.194, .377), (.044, .327, .041), "inn_cream")
    box(desk, (.225, .016, .377), (.159, .132, .051), "inn_iron")
    box(desk, (.245, -.132, .377), (.022, .139, .023), "inn_beam")
    export("autumn_soshi_writing_desk", desk, STYLES)

    hearth = Geometry()
    for x in (-.60, .49):
        for z in (-.52, .41):
            box(hearth, (x, z, 0.), (.11, .11, .147), "inn_beam")
    box(hearth, (-.66, -.57, .116), (1.32, 1.14, .122), "inn_slate")
    for x in (-.68, .56):
        box(hearth, (x, -.59, .192), (.12, 1.18, .094), "inn_beam")
    for z in (-.59, .465):
        box(hearth, (-.568, z, .192), (1.128, .125, .094), "inn_beam")
    box(hearth, (-.25, -.26, .231), (.50, .48, .054), "inn_iron")
    kettle = ((0., .61), (.045, .98), (.135, 1.), (.222, .82), (.24, .64), (.254, .59),
              (.257, .29), (.259, .13), (.288, .13))
    ceramic(hearth, -.038, .021, .283, .231, kettle, "inn_iron")
    for x in (-.16, .086):
        box(hearth, (x, .001, .475), (.031, .042, .196), "inn_iron")
    box(hearth, (-.16, .001, .651), (.277, .044, .031), "inn_iron")
    box(hearth, (.15, -.018, .431), (.109, .055, .049), "inn_iron")
    export("autumn_welcome_hearth", hearth, STYLES)


def room_props(mid, trim):
    inn = mid == "M388"
    if inn:
        for x in (5.10, 7.3, 10.01, 12.18):
            box(trim, (x, 8.95, 1.057), (1.65, 2.13, .062), "autumn_reed_mats", 1.15)
        for x in (4.60, 8.34, 12.2):
            frame(trim, (x, 12.53, 1.08), 1.77, 1.56, "kaiu_shoji")
        props = [["autumn_welcome_hearth", 8.65, 1.12, 10.58, .95, .025],
                 ["dragon_inn_shelves", 14.67, 1.057, 10.78, .91, 1.57],
                 ["autumn_petition_board", 4.09, 1.057, 8.48, .97, .12],
                 ["hoshi_inn_bench", 6.03, 1.12, 11.19, .95, .06],
                 ["hoshi_inn_bench", 12.74, 1.12, 11.23, .95, -.06],
                 ["hoshi_tea_table", 11.48, 1.12, 9.03, .93, .12]]
        lights = [[8.65, 1.74, 10.58, 5.75, 2.10]]
    else:
        box(trim, (6.13, 9.43, 1.057), (5.20, 2.54, .055), "autumn_brocade", 1.51)
        for x in (6.23, 11.16):
            box(trim, (x, 9.48, 1.113), (.06, 2.39, .006), "inn_heartwood")
        for x in (7.1, 10.78):
            frame(trim, (x, 12.53, 1.08), 1.53, 1.65, "kaiu_shoji")
        props = [["autumn_soshi_partition", 4.47, 1.057, 11.54, 1.03, .23],
                 ["autumn_soshi_partition", 13.11, 1.057, 11.57, 1.03, -.23],
                 ["autumn_soshi_writing_desk", 5.51, 1.057, 9.26, .99, .15],
                 ["autumn_soshi_writing_desk", 12.28, 1.057, 9.30, .95, -.09],
                 ["hoshi_inn_bench", 8.67, 1.12, 11.74, 1.10, .015]]
        lights = []
    for x, z in ((2.84, 6.08), (15.67, 6.26), (3.14, 11.53), (14.81, 12.10)):
        props.append(["dragon_mountain_andon", x, 1.057, z, .90, .14])
        lights.append([x, 1.72, z, 4.35, 1.62])
    return props, lights


def main(repo):
    _, gm, _, _ = variant(repo, group="autumn")
    swatches()
    fittings()
    path = STAGE / "index.json"
    index = json.loads(path.read_bytes())
    audit = {}
    for mid in ("M388", "M394"):
        world, events = gm.make(mid)
        terrain = world_mesh(gm, world, {gm.PLANK: "inn_cypress", gm.STONEW: "autumn_wall"})
        floorboards(terrain, right=17.5)
        box(terrain, (2.51, 3.51, 1.023), (1.47, .99, .029), "inn_cypress", 1.2)
        props, lights = room_props(mid, terrain)
        tag = mid.lower() + "_autumn_room"
        export(tag, terrain, STYLES)
        index[mid] = {"terrain": tag, "placements": props, "poolLights": lights}
        audit[mid] = {"events": len(events.ev), "placements": len(props)}
    path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf8")
    (HERE / "autumn-interiors-layout.json").write_text(
        json.dumps({"maps": audit}, indent=2), encoding="utf8")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
