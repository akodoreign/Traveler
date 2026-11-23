"""Add a recessed east-facing Yotomo cave and replace the old decorative vats."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


MAPS = ("M396", "M397", "M398", "M876", "M877")
POSITIONS = {
    "M396": {"#2#": [125, 4, 24, 3]},
    "M397": {"#1#": [38, 3, 7, 2], "#84#": [38, 3, 4, 2], "#85#": [84, 3, 48, 0]},
    "M398": {"#1#": [61, 3, 7, 2], "#85#": [61, 3, 4, 2]},
}
FRAGMENT = f"YOTOMO_POSITIONS = {POSITIONS!r}\n\n\n" + '''def rebuild_yotomo_route(m, ev):
    for event, pos in YOTOMO_POSITIONS.get(m.mid, {}).items():
        x, y, z, _ = pos
        assert int(m.hgt[z,x]) + 1 == y, (m.mid, event, pos)
        ev.ev[event]["pos"] = list(pos)
    if m.mid in ("M396", "M397", "M398"):
        fixtures = {(20,obj["fbparam"]) for obj in m.objs if obj["t"] == "fb" and obj["fbtype"] == 20}
        if m.mid == "M398":
            fixtures.add((4,IN["barrel"]))
        m.objs = [obj for obj in m.objs
                  if obj["t"] != "fb" or (obj["fbtype"],obj["fbparam"]) not in fixtures]
    if m.mid != "M396":
        return
    center = 24
    start = m.w - 15
    for x in range(start, m.w):
        depth = x - start
        for side in (-1, 1):
            for offset, extra in ((3, 0), (4, 1), (5, 3), (6, 4)):
                height = min(10, 2 + depth) - extra + (x + offset * side) % 3
                if height > 0:
                    fill(m, x, 4, center + side * offset, 1, height, 1, STONE)
        if depth < 4:
            continue
        for dz in range(-2, 3):
            bottom = 9 if abs(dz) == 2 else 10
            top = 11 + min(4, depth // 3) - (dz + x) % 2
            fill(m, x, bottom, center + dz, 1, top - bottom + 1, 1, STONE)
'''


def variant(repo):
    return with_world_patch(repo, MAPS, "rebuild_yotomo_route", FRAGMENT, uses_events=True)


if __name__ == "__main__":
    repo, profile = (Path(arg).resolve() for arg in sys.argv[1:3])
    stage_worlds(repo, profile, "--publish" in sys.argv[3:], MAPS, "yotomo-village", variant(repo),
                 ("M396", "M876", "M877"), positions=POSITIONS)
