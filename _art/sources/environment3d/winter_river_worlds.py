"""Stage the winter River of Gold route, rice barge, quay, and outdoor arenas."""
import sys
from pathlib import Path

from kensu_worlds import stage_worlds, with_world_patch

MAPS=("M422","M423","M424","M888","M889")
HERE=Path(__file__).resolve().parent

PATCH='''
def rebuild_winter_river_and_quay(m):
    if m.mid in ("M422","M424","M888","M889"):
        m.river_fixtures = [
            o for o in m.objs if o["t"]=="fb" and (o["fbtype"]==20 or (o["fbtype"],o["fbparam"])==(2,LAMP_STREET))
        ]
        m.objs = [o for o in m.objs if o not in m.river_fixtures]
    if m.mid in ("M422","M424","M889"):
        courses = []
        for o in m.objs:
            if o["t"]!="fill" or o["blk"]!=ROOF:
                continue
            if m.mid=="M424" and o["x"]==112+PAD_X:
                continue
            if courses and (o["x"],o["w"])==(courses[-1][-1]["x"],courses[-1][-1]["w"]) and o["y"]==courses[-1][-1]["y"]+1:
                courses[-1].append(o)
            else:
                courses.append([o])
        m.river_roofs = courses
        removed = [o for course in courses for o in course]
        for course in courses:
            last=course[-1]
            removed.extend(o for o in m.objs if o["t"]=="fill" and o["blk"]==DARKWOOD and o["x"]==last["x"]-1
                and o["y"]==last["y"]+1 and o["z"]==last["z"] and o["w"]==last["w"]+2)
        m.objs = [o for o in m.objs if o not in removed]
    if m.mid=="M423":
        # Preserve the deck surface and the original rice and cabin barrier footprints.
        for o in m.objs:
            if o["t"]=="fill":
                m.walls.extend((x,z) for x in range(o["x"],o["x"]+o["w"]) for z in range(o["z"],o["z"]+o["d"]))
        m.objs = []
    elif m.mid=="M424":
        m.objs = [o for o in m.objs if not (o["t"]=="fill" and (
            o["x"]==100+PAD_X and o["w"]==12 and o["blk"]==WOOD
            or o["x"] in (40+PAD_X,48+PAD_X) and o["z"]==21+PAD_BOTTOM and o["w"]==5 and o["blk"]==WOOD
            or o["x"]==112+PAD_X and o["z"]==26+PAD_BOTTOM and o["blk"] in (MATTING,ROOF)
            or o["x"]==5+PAD_X and o["z"]==10+PAD_BOTTOM and o["blk"]==DARKWOOD
        ))]
        # The separately fitted unenterable hut remains solid. The market stays open.
        m.walls.extend((x,z) for x in range(112+PAD_X,117+PAD_X) for z in range(26+PAD_BOTTOM,30+PAD_BOTTOM))
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_winter_river_and_quay",PATCH)


def stage(repo,profile,publish=False):
    stage_worlds(repo,profile,publish,MAPS,"cakon-winter-river",variant(repo),MAPS)


if __name__=="__main__":
    stage(*(Path(v).resolve() for v in sys.argv[1:3]),"--publish" in sys.argv[3:])
