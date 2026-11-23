"""Replace autumn valley scenery while preserving terrain heights and story events."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


MAPS = ("M387", "M389", "M390", "M391", "M392", "M393", "M395", "M875")
FRAGMENT = '''def rebuild_autumn_valley(m):
    tents = {
        "M387": tuple((x,z,5,4) for x,z in ((88,6),(96,9),(102,5),(12,6),(30,8),(44,5))),
        "M389": tuple((x + (z % 3),z,5,4) for x in range(4,96,9) for z in (4,22,28)),
        "M392": ((62,15,6,4),),
    }
    removed = set()
    for x,z,w,d in tents.get(m.mid,()):
        removed.update((x,z+k,MATTING) for k in range((d+1)//2))
        removed.add((x+w//2-1,z,VOID))
        removed.update((tip,z+(d-1)//2,DARKWOOD) for tip in (x-1,x+w))
    if m.mid == "M390":
        removed.update((x,z,WOOD) for x,z in ((20,22),(70,23),(100,22)))
    legacy = {(2,LAMP_STREET), (20,TREE_S), (20,TREE_M), (20,TREE_L)}
    if m.mid == "M393":
        legacy.update(((20,ROCK_S), (20,ROCK_M)))
    m.objs = [obj for obj in m.objs if not (
        obj["t"] == "fb" and (obj["fbtype"],obj["fbparam"]) in legacy
        or obj["t"] == "fill" and (obj["x"]-PAD_X,obj["z"]-PAD_BOTTOM,obj["blk"]) in removed
    )]
'''


def variant(repo):
    return with_world_patch(repo, MAPS, "rebuild_autumn_valley", FRAGMENT)


if __name__ == "__main__":
    repo, profile = (Path(arg).resolve() for arg in sys.argv[1:3])
    stage_worlds(repo, profile, "--publish" in sys.argv[3:], MAPS, "autumn-valley", variant(repo), ("M875",))
