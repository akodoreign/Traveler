"""Prepare collision updates for the four regional cave previews."""

import json
from pathlib import Path
import sys

import numpy as np

from kensu_worlds import with_world_patch
from river_lion_worlds import audit, connected
from shadowlands_march_worlds import compile_worlds


ROOT = Path(__file__).resolve().parents[3]
MAPS = ("M482", "M483", "M484", "M485")
PATCH = """
def raise_regional_cave_walls(m):
    m.hgt[m.blk == STONE] = np.maximum(m.hgt[m.blk == STONE], 16)
"""


def variant():
    return with_world_patch(ROOT, MAPS, "raise_regional_cave_walls", PATCH)


def baseline(module, mid):
    wall_patch = getattr(module, "raise_regional_cave_walls", None)
    if wall_patch is None:
        return module.make(mid)
    module.raise_regional_cave_walls = lambda m: None
    try:
        return module.make(mid)
    finally:
        module.raise_regional_cave_walls = wall_patch


def stage(profile):
    profile = Path(profile).resolve()
    if profile == (ROOT / "_tools" / "rpgcobo-tool").resolve():
        raise ValueError("Use an isolated profile")
    _, original, candidate, _, _ = variant()
    candidate.JOBDIR = str(profile / "tmp" / "rt_mapgen")
    catalog = json.loads((profile / "project" / "data" / "map.json").read_bytes())
    live = json.loads((ROOT / "_tools" / "rpgcobo-tool" / "project" /
                       "data" / "map.json").read_bytes())
    jobs = []
    for mid in MAPS:
        before, old_events = baseline(original, mid)
        world, events = candidate.make(mid)
        if old_events.ev != events.ev or catalog[mid] != live[mid]:
            raise ValueError(f"{mid} events or preview catalog differ")
        if not np.array_equal(before.blk, world.blk):
            raise ValueError(f"{mid} blocks changed")
        walls = before.blk == candidate.STONE
        if not np.array_equal(before.hgt[~walls], world.hgt[~walls]):
            raise ValueError(f"{mid} walkable heights changed")
        if int(world.hgt[walls].min()) - 2 <= 10:
            raise ValueError(f"{mid} walls are too low")
        if mid == "M485":
            reachable = connected(world, candidate, (46, 8), 2)
            for key, event in events.ev.items():
                x, y, z, _ = event.get("pos", (0, 0, 0, 0))
                if event.get("role") in ("portal", "custom", "itemchest") and y == 3:
                    if (x, z) not in reachable:
                        raise ValueError(f"{mid} event {key} is unreachable")
        else:
            audit(world, events, candidate)
        job = world.write()
        job["out"] = f"tmp/rt_mapgen/{mid}_regional_revisit.bw"
        jobs.append(job)
    compile_worlds(profile, jobs, stem="regional-cave-revisit")
    print("Prepared isolated cave collision candidates:", ", ".join(MAPS))


if __name__ == "__main__":
    stage(sys.argv[1])
