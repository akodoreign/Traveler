"""Compile Kyuden Bayushi, Traitor's Grove, and Shutai with new fixture placements."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


MAPS=("M345","M347","M348","M349","M861")
FRAGMENT='''def rebuild_scorpion_road(m):
    legacy={(2,LAMP_STREET),(20,TREE_L),(20,TREE_M),(20,TREE_S)}
    if m.mid == "M345":
        legacy.add((2,LAMP_CANDLE))
    m.objs=[item for item in m.objs if item["t"]!="fb"
            or (item["fbtype"],item["fbparam"]) not in legacy]
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_scorpion_road",FRAGMENT)


if __name__=="__main__":
    repo,profile=(Path(arg).resolve() for arg in sys.argv[1:3])
    stage_worlds(repo,profile,"--publish" in sys.argv[3:],MAPS,"scorpion-road",variant(repo),("M349",))
