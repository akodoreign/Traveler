"""Compile the Dragon approaches while retaining the existing terrain and events."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


MAPS = ("M379", "M380", "M382", "M383", "M872")
INN_ROAD = ("M380",)
INN_FRAGMENT = '''def rebuild_mountain_inn_road(m):
    old_fixtures = {(2, LAMP_STREET), (20, TREE_S), (20, TREE_M), (20, TREE_L)}
    m.objs = [obj for obj in m.objs if obj["t"] != "fb" or
              (obj["fbtype"], obj["fbparam"]) not in old_fixtures]
'''
FRAGMENT = '''def rebuild_dragon_approach(m):
    forest = (TREE_S, TREE_M, TREE_L)
    if m.mid == "M383":
        forest += (ROCK_S, ROCK_M)
    m.objs = [obj for obj in m.objs if obj["t"] != "fb" or not (
        obj["fbtype"] == 20 and obj["fbparam"] in forest
        or obj["fbtype"] == 2 and obj["fbparam"] == LAMP_STREET
    )]
    if m.mid == "M379":
        # The incense seller uses the new open counter at this footprint.
        m.objs = [obj for obj in m.objs if obj["t"] != "fill" or not (
            41 + PAD_X <= obj["x"] <= 48 + PAD_X
            and 21 + PAD_BOTTOM <= obj["z"] <= 23 + PAD_BOTTOM
        )]
'''


def variant(repo, inn_only=False):
    if inn_only:
        return with_world_patch(repo, INN_ROAD, "rebuild_mountain_inn_road", INN_FRAGMENT)
    published = "def rebuild_mountain_inn_road(" in (repo / "tools/gen_maps.py").read_text(encoding="utf8")
    ids = tuple(mid for mid in MAPS if not published or mid not in INN_ROAD)
    return with_world_patch(repo, ids, "rebuild_dragon_approach", FRAGMENT)


if __name__ == "__main__":
    repo, profile = (Path(arg).resolve() for arg in sys.argv[1:3])
    inn_only = "--inn-only" in sys.argv[3:]
    stage_worlds(repo, profile, "--publish" in sys.argv[3:], INN_ROAD if inn_only else MAPS,
                 "dragon-mountains", variant(repo, inn_only), terrain_only=() if inn_only else INN_ROAD)
