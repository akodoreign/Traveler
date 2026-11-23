"""Stage Cakon's paddy road, Tomie Cho's hut, and their three battle maps."""
import sys
from pathlib import Path

from kensu_worlds import stage_worlds, with_world_patch

MAPS=("M420","M421","M885","M886","M887")
HERE=Path(__file__).resolve().parent

PATCH='''
def rebuild_cakon_paddies_and_hut(m):
    if m.mid == "M420":
        red_stones = {(x+PAD_X,4,19+PAD_BOTTOM) for x in (74,79)}
        m.objs = [obj for obj in m.objs if not (
            obj["t"]=="fb" and (obj["fbtype"]==20 or (obj["fbtype"],obj["fbparam"])==(3,14))
            or obj["t"]=="fill" and obj["blk"]==STONEW
            and (obj["x"],obj["y"],obj["z"]) in red_stones)]
    elif m.mid == "M421":
        m.objs = [obj for obj in m.objs if not (
            obj["t"]=="fb" and obj["fbtype"]==20
            or obj["t"]=="fill" and (obj["blk"]==TAMPERED and obj["x"]-PAD_X in (54,55,56)
               or obj["blk"]==VOID and obj["x"]==57+PAD_X and obj["z"]==17+PAD_BOTTOM))]
        # The round footprint follows the clay wall and leaves its front recess clear.
        for z in range(21,30):
            for x in range(80,90):
                a,b = (x+.5-85.)/5.0, (z+.5-25.5)/4.95
                distance = a*a+b*b
                if .41 < distance < 1.18 and not (z <= 23 and 83 <= x <= 86):
                    m.walls.append((x,z))
    else:
        m.objs = [obj for obj in m.objs if not (
            obj["t"]=="fb" and (obj["fbtype"]==20 or obj["fbtype"]==2 and m.mid in ("M886","M887"))
            or m.mid=="M886" and obj["t"]=="fill" and obj["blk"]==TAMPERED)]
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_cakon_paddies_and_hut",PATCH)


def stage(repo,profile,publish=False):
    stage_worlds(repo,profile,publish,MAPS,"cakon-paddy-hut",variant(repo),MAPS)


if __name__=="__main__":
    stage(*(Path(v).resolve() for v in sys.argv[1:3]),"--publish" in sys.argv[3:])
