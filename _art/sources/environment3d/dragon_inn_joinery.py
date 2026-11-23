"""Build the fitted Dragon inn joinery and its restrained material palette."""

import math

import numpy as np
from PIL import Image, ImageFilter

from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export


COLORS = {
    "inn_cypress": (105, 58, 37),
    "inn_beam": (60, 37, 28),
    "inn_heartwood": (129, 76, 46),
    "inn_floor": (91, 56, 42),
    "inn_floor_light": (102, 65, 47),
    "inn_floor_medium": (97, 61, 44),
    "inn_iron": (31, 39, 41),
    "inn_slate": (59, 74, 79),
    "inn_celadon": (59, 100, 84),
    "inn_cream": (169, 148, 109),
    "inn_earthenware": (114, 61, 47),
}
MATERIALS = {name: (f"dragon_{name}.png", .89) for name in COLORS}
FLOOR_BOARDS = ("inn_floor", "inn_floor_medium", "inn_floor_light", "inn_floor_medium")
DOOR_MODELS = ("dragon_inn_entry_frame", "dragon_inn_entry_leaf")


def surfaces(scan_path):
    sample = Image.open(scan_path).convert("L")
    width, height = sample.size
    patch = sample.crop((width * .37, height * .31, width * .57, height * .62))
    patch = patch.resize((128, 128), Image.Resampling.LANCZOS)
    detail = np.asarray(patch, dtype=float) - np.asarray(patch.filter(ImageFilter.GaussianBlur(3)))
    grain = np.concatenate([detail, detail[:, ::-1]], axis=1)
    grain = np.concatenate([grain, grain[::-1]], axis=0)
    grain = np.clip(grain / max(grain.std(), 1.), -2., 2.)
    for name, color in COLORS.items():
        amount = .035 if name in FLOOR_BOARDS or name in ("inn_cypress", "inn_beam", "inn_heartwood") else 0.
        rgb = np.asarray(color) * (1 + amount * grain[..., None])
        Image.fromarray(np.uint8(rgb)).save(STAGE / "tex" / MATERIALS[name][0])


def ceramic(geom, x, z, y, radius, rings, material):
    """Use flat facets and a visible inner rim so the pots read in a wide shot."""
    corners = 10
    angles = [math.tau * k / corners for k in range(corners)]
    for (lower, low_radius), (upper, high_radius) in zip(rings, rings[1:]):
        for k, a in enumerate(angles):
            b = angles[(k + 1) % corners]
            corners3d = [
                (x + radius * width * math.cos(angle), z + radius * width * math.sin(angle), y + h)
                for h, width, angle in ((lower, low_radius, a), (lower, low_radius, b),
                                        (upper, high_radius, b), (upper, high_radius, a))
            ]
            geom.quad(corners3d, [(0., 0.), (1., 0.), (1., 1.), (0., 1.)], material)


def shelf():
    rack = Geometry()
    for x in (-.88, .804):
        for z in (-.20, .25):
            box(rack, (x, z, 0.), (.076, .076, 1.66), "inn_beam")
    for y in (.23, .75, 1.26, 1.58):
        box(rack, (-.90, -.233, y), (1.80, .58, .071), "inn_cypress")
        box(rack, (-.908, -.242, y + .005), (1.816, .022, .033), "inn_heartwood")
    for y in (.37, .90, 1.43):
        box(rack, (-.823, .277, y), (1.646, .039, .067), "inn_beam")
    jar = ((0., .63), (.062, .88), (.17, 1.), (.27, .83), (.31, .49), (.37, .48),
           (.38, .58), (.404, .57), (.404, .38), (.356, .37))
    bowl = ((0., .46), (.026, .49), (.074, .83), (.121, 1.), (.141, 1.),
            (.141, .89), (.069, .59), (.042, .37))
    for x, z, height, radius, shape, color in (
        (-.54, .055, .301, .22, jar, "inn_earthenware"),
        (.32, .013, .301, .17, jar, "inn_celadon"),
        (.62, .094, .301, .135, bowl, "inn_cream"),
        (-.56, .04, .821, .18, bowl, "inn_celadon"),
        (-.12, .02, .821, .19, bowl, "inn_cream"),
        (.50, .06, .821, .17, jar, "inn_earthenware"),
        (-.32, .06, 1.331, .16, bowl, "inn_cream"),
        (.37, .08, 1.331, .195, bowl, "inn_celadon"),
    ):
        ceramic(rack, x, z, height, radius, shape, color)
    export("dragon_inn_shelves", rack, MATERIALS)


def door_models():
    frame = Geometry()
    for x in (-.024, .926):
        box(frame, (x, -.010, 0.), (.098, .27, 2.025), "inn_beam")
    box(frame, (-.039, -.025, 1.906), (1.078, .30, .122), "inn_beam")
    box(frame, (.006, -.049, .003), (.988, .33, .039), "inn_slate")
    export(DOOR_MODELS[0], frame, MATERIALS)
    leaf = Geometry()
    # The engine positions the hinge 0.073 m from the left jamb.
    for n in range(5):
        key = "inn_heartwood" if n in (1, 4) else "inn_cypress"
        box(leaf, (.014 + n * .164, -.029, .053), (.160, .076, 1.828), key, .9)
    for y in (.25, 1.46):
        box(leaf, (.006, -.052, y), (.835, .025, .092), "inn_beam")
        box(leaf, (.0, -.069, y + .01), (.20, .021, .058), "inn_iron")
        box(leaf, (.006, .047, y), (.835, .023, .092), "inn_beam")
    box(leaf, (.738, -.059, .91), (.069, .022, .13), "inn_iron")
    for x in (.742, .79):
        box(leaf, (x, -.089, .94), (.014, .033, .078), "inn_iron")
    box(leaf, (.746, -.093, .935), (.054, .022, .016), "inn_iron")
    export(DOOR_MODELS[1], leaf, MATERIALS)

    for name, rise in (("half", .5), ("full", 1.)):
        stair = Geometry()
        count = round(rise / .25)
        for step in range(count):
            extent = (count - step) * .255
            box(stair, (-.13, -extent, .25 * step), (1.26, extent + .10, .25), "inn_slate")
        export(f"dragon_inn_stoop_{name}", stair, MATERIALS)


def floorboards(geom, right=15.0):
    left, front, back = 2.0, 4.5, 13.0
    box(geom, (left, front, 1.023), (right-left, back-front, .016), "inn_beam")
    plank_width = .38
    for row in range(math.ceil((back - front) / plank_width)):
        z = front + row * plank_width
        seams = [left, *(left + x - (row % 4) * .68 for x in (3.20, 6.50, 9.75)), right]
        for n, (start, end) in enumerate(zip(seams, seams[1:])):
            box(geom, (start + .004, z + .004, 1.038),
                (end - start - .008, min(plank_width, back - z) - .008, .019),
                FLOOR_BOARDS[(row + 3 * n) % len(FLOOR_BOARDS)], 1.4)

    for x in (1.49, right):
        box(geom, (x, 4.0, 3.018), (.51, 9.5, .073), "inn_beam")
    box(geom, (2., 13., 3.018), (right - left, .50, .073), "inn_beam")
    for x, width in ((1.49, 1.01), (4.0, right - 3.49)):
        box(geom, (x, 3.99, 1.519), (width, .52, .072), "inn_beam")
