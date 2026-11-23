"""Compile the Ojatara exteriors and battles after removing stock fixtures."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


MAPS=("M368","M369","M371","M372","M374","M375","M377","M378","M869","M870","M871")

FRAGMENT='''def rebuild_ojatara(m):
    tents = {
        "M368": ((66,20,6,5),(76,21,6,5)),
        "M369": ((86,6,5,4),(94,9,5,4),(102,5,5,4),(12,6,5,4),(30,8,5,4)),
        "M371": ((8,21,6,5),(18,22,6,5),(84,21,6,5),(94,22,6,5),(60,20,8,6)),
    }
    legacy = {(2,LAMP_STREET),(20,TREE_S),(20,TREE_M),(20,TREE_L)}
    removed_builders = set()
    for x,z,w,d in tents.get(m.mid,()):
        # The old straw tent is made of stepped roof slices, one doorway
        # carve and two ridge tips. These coordinates name those pieces.
        removed_builders.update((x,z+k,MATTING) for k in range((d+1)//2))
        removed_builders.add((x+w//2-1,z,VOID))
        for tip in (x-1,x+w):
            removed_builders.add((tip,z+(d-1)//2,DARKWOOD))
    if m.mid == "M368":
        removed_builders.update(((14,21,WOOD),(24,22,WOOD)))
    if m.mid == "M374":
        removed_builders.update(((45,23,DARKWOOD),(50,23,DARKWOOD)))
    m.objs = [item for item in m.objs if not (
        item["t"] == "fb" and (item["fbtype"],item["fbparam"]) in legacy
        or item["t"] == "fill"
        and (item["x"]-PAD_X,item["z"]-PAD_BOTTOM,item["blk"]) in removed_builders
    )]
'''


def variant(repo):
    return with_world_patch(repo, MAPS, "rebuild_ojatara", FRAGMENT)


if __name__=="__main__":
    repo, profile=(Path(path).resolve() for path in sys.argv[1:3])
    stage_worlds(repo, profile, "--publish" in sys.argv[3:], MAPS, "ojatara-valley",
                 variant(repo), ("M377","M870","M871"))
