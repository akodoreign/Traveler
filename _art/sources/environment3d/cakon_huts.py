"""Build fitted riverside architecture and cooperage for the Cakon maps."""

from math import cos, sin, tau
from pathlib import Path
import json

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_iuchi_tower import tint_texture
from export_coast import Geometry, STAGE, export


HERE = Path(__file__).resolve().parent
SIZES = {
    "cakon_riverside_hut": (2.34, 1.68, 1.84),
    "cakon_hamlet_hut": (2.86, 2.17, 2.36),
    "cakon_hamlet_shrine": (4.84, 3.00, 3.28),
    "cakon_staved_barrel": (.65, .82, .65),
    "cakon_staved_barrel_lid": (.532, .065, .532),
}
TIMBER = "cakon_hut_timber"
PLANK = "cakon_hut_plank"
EARTH = "cakon_hut_earth"
STONE = "cakon_hut_stone"
ALTAR = "cakon_hut_altar"
COOPER = "cakon_cooper_bound"
LID = "cakon_cooper_lid"
STAVES = tuple(f"cakon_cooper_stave_{index}" for index in range(3))
THATCH = "cakon_hut_thatch"
WICKER = "cakon_hut_wicker"
PALETTE = {
    TIMBER: ("cakon_cedar_deck_scan", (65, 49, 41), .027),
    PLANK: ("cakon_cedar_deck_scan", (112, 83, 61), .042),
    EARTH: ("cakon_plaster_scan", (151, 127, 98), .028),
    STONE: ("cakon_stone_setts_scan", (77, 79, 74), .024),
    ALTAR: ("cakon_cedar_deck_scan", (101, 62, 51), .034),
    COOPER: ("cakon_stone_setts_scan", (58, 61, 60), .025),
    LID: ("cakon_cedar_deck_scan", (126, 91, 61), .044),
    STAVES[0]: ("cakon_cedar_deck_scan", (121, 84, 53), .044),
    STAVES[1]: ("cakon_cedar_deck_scan", (114, 78, 49), .044),
    STAVES[2]: ("cakon_cedar_deck_scan", (129, 91, 58), .044),
}
MATERIALS = {name: (f"{name}.png", .94) for name in (*PALETTE, THATCH, WICKER)}


def textures():
    for key, (scan, color, contrast) in PALETTE.items():
        tint_texture(key, scan, color, contrast)
    # Keep the straw and reed accents coherent when minified to gameplay size.
    y, x = np.mgrid[0:512, 0:512] / 512
    bend = .005 * np.sin(tau * (2 * y + x))
    grain = np.sin(tau * (74 * (x + bend))) + .58 * np.cos(tau * (53 * x - 3 * y))
    bundles = np.sin(tau * 9 * (x + bend))
    courses = np.power(.5 + .5 * np.cos(tau * 5 * (y + .004 * np.sin(tau * x))), 12)
    straw = np.array([146., 111., 67.]) + (3.1 * grain + 3.0 * bundles - 7.0 * courses)[..., None]
    Image.fromarray(np.clip(straw, 0, 255).astype(np.uint8)).save(STAGE / "tex" / f"{THATCH}.png")
    warp = np.sin(tau * 30 * x)
    cross = np.sin(tau * 40 * y)
    reed = np.array([157., 130., 93.]) + (3.0 * warp + 2.4 * cross + 2.2 * warp * cross)[..., None]
    Image.fromarray(np.clip(reed, 0, 255).astype(np.uint8)).save(STAGE / "tex" / f"{WICKER}.png")


def roof(geo, width, depth, eave, peak):
    # Each slope eases off near the eave. The clipped ends expose the timber gable.
    reach, half = depth / 2, width / 2
    slopes = ((-1., eave, 1.), (-.68, eave + (peak - eave) * .23, .98),
              (0., peak - .065, .86), (.68, eave + (peak - eave) * .23, .98),
              (1., eave, 1.))
    row_width = width / .78
    for (z0, h0, w0), (z1, h1, w1) in zip(slopes, slopes[1:]):
        z0, z1 = z0 * reach, z1 * reach
        x0, x1 = half * w0, half * w1
        uv = [(0., z0 / .78), (row_width, z0 / .78),
              (row_width, z1 / .78), (0., z1 / .78)]
        top = [(-x0, z0, h0), (x0, z0, h0), (x1, z1, h1), (-x1, z1, h1)]
        geo.quad(top, uv, THATCH)
        under = [(x, z, y - .12) for x, z, y in top]
        geo.quad(under[::-1], uv[::-1], PLANK)
        for ids in ((0, 3), (2, 1)):
            a, b = ids
            geo.quad([top[a], top[b], under[b], under[a]],
                     [(0., 1.), (1., 1.), (1., 0.), (0., 0.)], THATCH)
    for z in (-reach, reach - .044):
        box(geo, (-half, z, eave - .115), (width, .044, .114), THATCH, .89)
        box(geo, (-half + .048, z, eave - .164), (width - .096, .044, .047), TIMBER)
    ridge = width * .87
    box(geo, (-ridge / 2, -.087, peak - .110), (ridge, .174, .110), THATCH, .87)
    for x in (-ridge / 2 + .07, ridge / 2 - .14):
        box(geo, (x, -.092, peak - .105), (.070, .184, .025), TIMBER)


def plank_door(geo, width, height, z, x, base, frame=TIMBER):
    edge = .053
    for index in range(6):
        plank = width / 6
        box(geo, (x - width / 2 + index * plank + .006, z, base),
            (plank - .012, .025, height), PLANK if index % 3 else frame, .66)
    for side in (-1, 1):
        box(geo, (x + side * (width / 2 + edge / 2) - edge / 2, z - .027, base - .015),
            (edge, .052, height + .066), frame)
    box(geo, (x - width / 2 - edge, z - .027, base + height),
        (width + 2 * edge, .064, edge), frame)
    for y in (base + height * .23, base + height * .76):
        box(geo, (x - width / 2 + .021, z - .021, y), (width - .042, .029, .046), frame)
    box(geo, (x + width * .29, z - .042, base + height * .51), (.036, .027, .068), COOPER)


def hut(size, shrine=False):
    width, peak, depth = size
    geo = Geometry()
    body_width = width - (.84 if shrine else .37)
    body_depth = depth - (.76 if shrine else .34)
    left, front = -body_width / 2, -body_depth / 2
    sill = .21 if shrine else .13
    wall = peak * (.59 if shrine else .62)
    post = .096 if shrine else .072
    trim = ALTAR if shrine else TIMBER
    box(geo, (left - .037, front - .031, 0),
        (body_width + .074, body_depth + .062, sill - .029), STONE, .92)
    box(geo, (left - .011, front - .011, sill - .029),
        (body_width + .022, body_depth + .022, .063), TIMBER)
    box(geo, (left + .018, front + .018, sill),
        (body_width - .036, body_depth - .036, wall - sill), PLANK if shrine else WICKER, .82)
    for x in (left, -left - post):
        for z in (front, -front - post):
            box(geo, (x, z, sill - .016), (post, post, wall - sill + .091), trim)
        for h in (sill + .073, wall - .063):
            box(geo, (x, front + post, h), (post, body_depth - 2 * post, .061), trim)
    for z in (front, -front - post / 2):
        box(geo, (left, z, wall - .046), (body_width, post, .105), trim)
        box(geo, (left, z, sill), (body_width, post, .060), trim)
    # Gable siding recessed behind the narrow verge and canopy.
    for x, facing in ((left + .04, -1), (-left - .04, 1)):
        points = [(x, front, wall), (x, -front, wall), (x, 0., peak - .18)]
        if facing < 0:
            points = points[::-1]
        geo.quad(points + [points[-1]], [(0., 0.), (1., 0.), (.5, 1.), (.5, 1.)], PLANK)
        box(geo, (x - .026, -.035, wall), (.052, .07, peak - wall - .22), TIMBER)
    door_w = body_width * (.36 if shrine else .35)
    door_h = (wall - sill) * .90
    plank_door(geo, door_w, door_h, front - .014, 0., sill + .015, trim)
    if shrine:
        for x in (-.92, .92):
            box(geo, (x - .16, front - .026, wall * .41), (.32, .037, .43), EARTH)
            for k in (-1, 0, 1):
                box(geo, (x + k * .11 - .019, front - .049, wall * .40),
                    (.038, .048, .46), trim)
            for h in (wall * .40, wall * .58):
                box(geo, (x - .185, front - .049, h), (.37, .048, .039), trim)
        box(geo, (-door_w / 2 - .17, front - .263, 0), (door_w + .34, .263, .104), STONE)
        box(geo, (-door_w / 2 - .119, front - .145, .105), (door_w + .238, .145, .088), TIMBER)
        box(geo, (-.14, front - .058, wall - .101), (.28, .048, .18), EARTH)
    else:
        for x in (left + body_width * .22, -left - body_width * .22):
            box(geo, (x - .022, front, sill + .05), (.044, .039, wall - sill - .071), TIMBER)
        box(geo, (-door_w / 2 - .07, front - .113, .05), (door_w + .14, .117, .068), STONE)
    roof(geo, width, depth, wall + .155, peak)
    return geo


def barrel_shell(geo, profile, steps, materials, gap=0.):
    for sector in range(steps):
        a = tau * sector / steps + gap
        b = tau * (sector + 1) / steps - gap
        material = materials[sector % len(materials)]
        for (h0, r0), (h1, r1) in zip(profile, profile[1:]):
            p0, p1 = (cos(a) * r0, sin(a) * r0, h0), (cos(b) * r0, sin(b) * r0, h0)
            p2, p3 = (cos(b) * r1, sin(b) * r1, h1), (cos(a) * r1, sin(a) * r1, h1)
            geo.quad([p0, p1, p2, p3], [(.11, h0), (.89, h0), (.89, h1), (.11, h1)], material)


def lid(geo, base=0.):
    rim = .266
    top = base + .065
    barrel_shell(geo, ((base, rim - .013), (base + .024, rim), (top, rim)), 24, (LID,))
    for index in range(24):
        a, b = tau * index / 24, tau * (index + 1) / 24
        arc = [(cos(phase) * rim, sin(phase) * rim, top) for phase in (a, b)]
        points = [(0., 0., top), *arc, arc[-1]]
        geo.quad(points, [(x + .5, z + .5) for x, z, _ in points], LID)
    for offset in (-.102, .092):
        box(geo, (-.16, offset, top - .009), (.32, .027, .009), PLANK)


def barrel():
    geo = Geometry()
    profile = ((0., .254), (.060, .269), (.22, .302), (.41, .320),
               (.61, .306), (.75, .270), (.805, .263))
    barrel_shell(geo, [(h, r - .008) for h, r in profile], 24, (TIMBER,))
    barrel_shell(geo, profile, 24, (STAVES[0], STAVES[1], STAVES[0], STAVES[2]), .009)
    for h, lower, upper in ((.117, .293, .302), (.384, .323, .325), (.671, .294, .288)):
        barrel_shell(geo, ((h - .008, lower - .008), (h, lower), (h + .025, upper),
                           (h + .035, upper - .007)), 24, (COOPER,))
    lid(geo, .755)
    return geo


def build_assets():
    """Write only the five Cakon model files and their dedicated texture files."""
    textures()
    assets = {name: hut(SIZES[name], name == "cakon_hamlet_shrine")
              for name in ("cakon_riverside_hut", "cakon_hamlet_hut", "cakon_hamlet_shrine")}
    assets["cakon_staved_barrel"] = barrel()
    barrel_lid = Geometry()
    lid(barrel_lid)
    assets["cakon_staved_barrel_lid"] = barrel_lid
    receipt = {}
    for name, geo in assets.items():
        export(name, geo, MATERIALS)
        native = np.asarray(geo.vertices)[:, [0, 2, 1]]
        assert np.isfinite(native).all()
        assert np.allclose(np.ptp(native, axis=0), SIZES[name], atol=.012), (name, np.ptp(native, axis=0))
        receipt[name] = {
            "nativeSpan": np.round(np.ptp(native, axis=0), 4).tolist(),
            "quads": len(geo.faces),
            "materials": sorted(set(geo.materials)),
        }
    (HERE / "cakon-hut-barrel-assets.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    build_assets()
