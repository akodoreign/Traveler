"""Build the fitted Dragon slate shelter and describe its two replacement rows."""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from build_hoshi_stall import box
from build_iuchi_tower import tint_texture
from export_coast import Geometry, STAGE, export


HERE = Path(__file__).resolve().parent
MAPS = ("M379", "M382")
PREVIOUS = "dragon_slate_waystation"
REPLACEMENT = "dragon_fitted_slate_waystation"
SIZE = (2.35, 2.05, 1.48)
POST = "dragon_waystation_post"
BOARD = "dragon_waystation_board"
BENCH = "dragon_waystation_bench"
FOOT = "dragon_waystation_footing"
SLATE = tuple(f"dragon_waystation_slate_{index}" for index in range(3))
PALETTE = {
    POST: ("dragon_clean_lacquered_wood", (53, 40, 35), .030),
    BOARD: ("cakon_cedar_deck_scan", (104, 75, 52), .047),
    BENCH: ("cakon_cedar_deck_scan", (121, 90, 61), .045),
    FOOT: ("dragon_slate_moss", (75, 78, 74), .025),
    SLATE[0]: ("dragon_slate_moss", (78, 90, 99), .029),
    SLATE[1]: ("dragon_slate_moss", (72, 83, 93), .029),
    SLATE[2]: ("dragon_slate_moss", (84, 95, 104), .029),
}


def tiled_roof(geo):
    half_width, eave, ridge = SIZE[0] / 2, 1.56, 2.00
    reach = SIZE[2] / 2
    tiles = 6
    for side in (-1, 1):
        for course in range(4):
            u, v = course / 4, (course + 1) / 4
            upper = (1 - u) * ridge + u * eave
            lower = (1 - v) * ridge + v * eave
            for column in range(tiles):
                x0 = -half_width + SIZE[0] * column / tiles + (.010 if column else 0.)
                x1 = -half_width + SIZE[0] * (column + 1) / tiles - (.010 if column + 1 < tiles else 0.)
                a, b = side * u * reach, side * v * reach
                p = [(x0, a, upper), (x1, a, upper), (x1, b, lower), (x0, b, lower)]
                uv = [(x * 1.65, z * 1.65) for x, z, _ in p]
                if side < 0:
                    p, uv = p[::-1], uv[::-1]
                geo.quad(p, uv, SLATE[(column + 2 * course) % len(SLATE)])
                bottom = [(x, z, h - .047) for x, z, h in p]
                geo.quad(bottom[::-1], uv[::-1], POST)
                for edge in range(4):
                    end = (edge + 1) % 4
                    geo.quad([p[end], p[edge], bottom[edge], bottom[end]],
                             [(.00, .00), (.8, .00), (.8, .1), (.00, .1)], SLATE[0])
        box(geo, (-1.135, side * .688 - .02, 1.475), (2.27, .039, .113), POST)
    box(geo, (-1.124, -.057, 1.966), (2.248, .114, .073), SLATE[1])
    box(geo, (-1.083, -.037, 2.018), (2.166, .074, .032), SLATE[2])


def build_shelter():
    for key, (scan, tint, contrast) in PALETTE.items():
        tint_texture(key, scan, tint, contrast)
    geo = Geometry()
    # Broad open front retains the covered waiting space. Side boards sit below the eye line.
    for x in (-.856, .734):
        for z in (-.50, .38):
            box(geo, (x - .050, z - .047, 0.), (.218, .215, .114), FOOT, .65)
            box(geo, (x, z, .104), (.122, .121, 1.474), POST, .81)
        box(geo, (x + .026, -.389, .141), (.061, .777, .711), BOARD, .87)
        box(geo, (x - .002, -.398, .808), (.123, .796, .070), POST)
        box(geo, (x - .026, -.591, 1.493), (.175, 1.18, .124), POST)
    for column in range(10):
        box(geo, (-.741 + .149 * column, .420, .134), (.143, .054, 1.398),
            BOARD if column % 3 else BENCH, .86)
    for z in (-.559, .398):
        box(geo, (-.935, z, 1.449), (1.87, .110, .125), POST)
    box(geo, (-.768, .225, .601), (1.536, .256, .095), BENCH, .84)
    for x in (-.687, .594):
        box(geo, (x, .242, .133), (.093, .122, .475), POST)
    box(geo, (-.786, -.493, .094), (1.572, .970, .052), BOARD, .84)
    for p in (-1, 1):
        x = p * .881
        triangle = [(x, -.59, 1.556), (x, .59, 1.556), (x, 0., 1.960)]
        if p < 0:
            triangle = triangle[::-1]
        geo.quad(triangle + [triangle[-1]], [(0., 0.), (1., 0.), (.5, 1.), (.5, 1.)], BOARD)
    tiled_roof(geo)
    native = np.asarray(geo.vertices)[:, [0, 2, 1]]
    assert np.allclose(np.ptp(native, axis=0), SIZE, atol=.001)
    export(REPLACEMENT, geo, {key: (f"{key}.png", .94) for key in PALETTE})


def replacement_rows(repo):
    """Read the published rows and write only the asset-reference change to a scratch receipt."""
    manifest = repo / "_tools/rpgcobo-tool/project/resource/native_environment/index.json"
    live = json.loads(manifest.read_bytes())
    before = {mid: live[mid] for mid in MAPS}
    after = deepcopy(before)
    swapped = {}
    for mid, row in after.items():
        changed = [entry for entry in row["placements"] if entry[0] == PREVIOUS]
        assert len(changed) == 1, (mid, len(changed))
        entry = changed[0]
        swapped[mid] = {"from": list(entry), "to": [REPLACEMENT, *entry[1:]]}
        entry[0] = REPLACEMENT
    files = [f"{REPLACEMENT}.pm", f"{REPLACEMENT}.mdl", *(f"tex/{key}.png" for key in PALETTE)]
    receipt = {
        "before": before,
        "rows": after,
        "swaps": swapped,
        "files": {path: sha256((STAGE / path).read_bytes()).hexdigest() for path in files},
        "nativeSpan": SIZE,
    }
    result = HERE / "dragon-waystation-replacement.json"
    result.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    args = parser.parse_args()
    build_shelter()
    print(f"Staged row receipt {replacement_rows(args.repo)}.")
