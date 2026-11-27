"""Build an isolated expansion of the Mieko estate cellar."""

import json
from pathlib import Path
import sys

import numpy as np

from kensu_worlds import with_world_patch
from shadowlands_march_worlds import compile_worlds


ROOT = Path(__file__).resolve().parents[3]
PATCH = """
def rebuild_mieko_cellar(m, ev):
    if (m.w, m.d) != (32, 32):
        raise ValueError("The Mieko cellar baseline changed")
    east_wall = [o for o in m.objs if o["t"] == "fill" and
                 (o["x"], o["z"], o["w"], o["d"]) == (26, 10, 1, 11)]
    if len(east_wall) != 1:
        raise ValueError("The Mieko cellar east wall changed")
    m.objs.remove(east_wall[0])
    m.objs = [o for o in m.objs if not (
        o["t"] == "fill" and o["x"] == 26 and o["z"] in (14, 18)
        and o["w"] == 1 and o["d"] == 1)]
    m.objs.extend([{**east_wall[0], "d": 3},
                   {**east_wall[0], "z": 19, "d": 2}])
    old_height, old_blocks = m.hgt.copy(), m.blk.copy()
    m.w, m.d = 112, 64
    zz, xx = np.indices((m.d, m.w))
    floor = np.zeros((m.d, m.w), dtype=bool)
    paths = (
        ((22, 16), (30, 16), (40, 20), (50, 26), (62, 27), (73, 22), (86, 20)),
        ((50, 26), (51, 37), (61, 43), (75, 43), (84, 36), (86, 20)),
        ((62, 27), (67, 16), (78, 12), (88, 14)),
    )
    for path in paths:
        for (ax, az), (bx, bz) in zip(path, path[1:]):
            dx, dz = bx-ax, bz-az
            t = np.clip(((xx-ax)*dx+(zz-az)*dz)/(dx*dx+dz*dz), 0., 1.)
            floor |= (xx-ax-t*dx)**2 + (zz-az-t*dz)**2 <= 4.5**2
    for x, z, rx, rz in ((38, 19, 9, 7), (53, 26, 10, 8), (69, 41, 12, 8),
                          (84, 21, 10, 9), (79, 13, 9, 6)):
        irregular = .05*np.sin(xx*.35+zz*.52) + .035*np.cos(xx*.6-zz*.3)
        floor |= ((xx-x)/rx)**2 + ((zz-z)/rz)**2 < 1. + irregular
    floor &= (xx >= 26)
    m.hgt = np.where(floor, 1, 16).astype(np.int32)
    m.blk = np.where(floor, PLANK, STONE).astype(np.int32)
    m.hgt[10:21, 5:26] = old_height[10:21, 5:26]
    m.blk[10:21, 5:26] = old_blocks[10:21, 5:26]
    # Keep the original doorway and story room intact; only the east wall opens.
    m.hgt[13:19, 25:29] = 1
    m.blk[13:19, 25:29] = PLANK
"""


def variant():
    return with_world_patch(ROOT, ("M295",), "rebuild_mieko_cellar", PATCH,
                            uses_events=True)


def baseline(module):
    patch = getattr(module, "rebuild_mieko_cellar", None)
    if patch is None:
        return module.make("M295")
    module.rebuild_mieko_cellar = lambda m, ev: None
    try:
        return module.make("M295")
    finally:
        module.rebuild_mieko_cellar = patch


def stage(profile):
    profile = Path(profile).resolve()
    if profile == (ROOT / "_tools" / "rpgcobo-tool").resolve():
        raise ValueError("Use an isolated profile")
    _, original, candidate, _, _ = variant()
    before, before_events = baseline(original)
    world, events = candidate.make("M295")
    if before_events.ev != events.ev:
        raise ValueError("The cellar quest events changed")
    catalog = profile / "project" / "data" / "map.json"
    raw = catalog.read_bytes()
    rows = json.loads(raw)
    if rows["M295"]["size"] != [before.w, 64, before.d]:
        raise ValueError("The profile cellar differs from its original baseline")
    working = json.loads((ROOT / "_tools" / "rpgcobo-tool" / "project" /
                          "data" / "map.json").read_bytes())
    if rows["M295"]["event"] != working["M295"]["event"]:
        raise ValueError("The profile cellar events differ from the working catalog")
    candidate.JOBDIR = str(profile / "tmp" / "rt_mapgen")
    job = world.write()
    job["out"] = "tmp/rt_mapgen/M295_mieko_candidate.bw"
    compile_worlds(profile, [job], stem="mieko-cellar")
    if catalog.read_bytes() != raw:
        raise RuntimeError("The profile map catalog changed during staging")
    rows["M295"]["size"] = [world.w, 64, world.d]
    catalog.write_text(json.dumps(rows, ensure_ascii=False, indent="\t"), encoding="utf-8")
    print(f"M295 isolated candidate: {before.w}x{before.d} -> {world.w}x{world.d}")


if __name__ == "__main__":
    stage(sys.argv[1])
