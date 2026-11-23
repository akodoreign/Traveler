"""Stage the caravan road and Cakon street geometry with the original story events."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch
from cakon_paddy_worlds import MAPS as PADDY_MAPS, stage as stage_paddy
from winter_river_worlds import MAPS as WINTER_MAPS, stage as stage_winter
from snake_den_worlds import MAPS as SNAKE_MAPS, stage as stage_snake


GROUPS = {
    "paddy-hut": PADDY_MAPS,
    "winter-river": WINTER_MAPS,
    "snake-den": SNAKE_MAPS,
    "caravan": ("M413",),
    "river": ("M414", "M415"),
    "city": ("M416", "M417", "M883"),
    "hamlet": ("M418", "M419", "M884"),
}

FRAGMENTS = {
    "caravan": '''
def rebuild_iuchi_caravan(m):
    shelters = set()
    for x in range(20,100,14):
        shelters.update((x,18+k,MATTING) for k in (0,1))
        shelters.add((x+1,18,VOID))
        shelters.update((p,19,DARKWOOD) for p in (x-1,x+4))
    m.objs = [o for o in m.objs if not (
        o["t"] == "fb" and o["fbtype"] == 20 and o["fbparam"] in (TREE_S,TREE_M,TREE_L)
        or o["t"] == "fill" and (o["x"]-PAD_X,o["z"]-PAD_BOTTOM,o["blk"]) in shelters
    )]
''',
    "river": '''
def rebuild_cakon_river(m):
    m.objs = [o for o in m.objs if not (
        o["t"] == "fb" and ((m.mid == "M414" and o["fbtype"] == 20 and o["fbparam"] in (TREE_S,TREE_M,TREE_L))
                        or (m.mid == "M415" and (o["fbtype"],o["fbparam"]) == (2,LAMP_STREET)))
        or m.mid == "M414" and o["t"] == "fill" and o["blk"] == WOOD and (o["w"],o["h"],o["d"]) == (4,2,3)
    )]
''',
    "city": '''
def rebuild_cakon_city(m):
    if m.mid == "M417":
        # Carve the city wall in the compiler so that the visible gate has a true travel lane.
        blocks = {(110,4,8,4,14,16,STONEW), (110,4,17,4,6,4,VOID)}
        m.objs = [o for o in m.objs if o["t"] != "fill" or
                  tuple(o[k] for k in ("x","y","z","w","h","d","blk")) not in blocks]
        fill(m,110,4,8,4,14,9,STONEW)
        fill(m,110,4,21,4,14,3,STONEW)
        fill(m,110,10,17,4,8,4,STONEW)
        fill(m,110,4,0,4,8,8,STONEW)
        fill(m,110,4,24,4,8,m.d-24,STONEW)
        fill(m,110,12,0,4,1,8,ROOF)
        fill(m,110,12,24,4,1,m.d-24,ROOF)
        return
    stands = {(x+PAD_X,8+PAD_BOTTOM) for x in range(30,90,12)}
    m.objs = [o for o in m.objs if not (
        o["t"] == "fb" and (o["fbtype"],o["fbparam"]) == (2,LAMP_STREET)
        or m.mid == "M416" and o["t"] == "fill" and (
            (o["x"],o["z"]) in stands and (o["blk"],o["h"]) == (WOOD,1)
            or (o["x"],o["z"],o["w"],o["h"],o["blk"]) == (90+PAD_X,5+PAD_BOTTOM,6,2,PLASTER)
        )
    )]
''',
    "hamlet": '''
def rebuild_cakon_hamlet(m):
    if m.mid == "M418":
        fixtures = {(x+PAD_X,z+PAD_BOTTOM) for x,z in ((8,22),(20,24),(64,22),(76,23),(88,21),
                    (10,4),(30,5),(70,4),(84,6),(34,22),(44,21),(43,20))}
        m.objs = [o for o in m.objs if not (o["t"]=="fill" and
                  (o["x"],o["z"]) in fixtures and o["blk"] in (MATTING,WOOD,ROOF))]
    else:
        m.objs = [o for o in m.objs if not (o["t"]=="fb" and o["fbtype"]==20 and
                  o["fbparam"] in (TREE_S,TREE_M,TREE_L))]
        if m.mid == "M419":
            # Leave the raised log deck and open the water below it.
            fill(m,70,0,18,12,3,3,0)
            fill(m,70,0,18,12,1,3,WATER)
''',
}

FUNCTIONS = {
    "caravan": "rebuild_iuchi_caravan",
    "river": "rebuild_cakon_river",
    "city": "rebuild_cakon_city",
    "hamlet": "rebuild_cakon_hamlet",
}


def variant(repo, group):
    return with_world_patch(repo,GROUPS[group],FUNCTIONS[group],FRAGMENTS[group])


def stage(repo, profile, group, publish):
    if group=="snake-den":
        return stage_snake(repo,profile,publish)
    if group=="winter-river":
        return stage_winter(repo,profile,publish)
    if group=="paddy-hut":
        return stage_paddy(repo,profile,publish)
    maps=GROUPS[group]
    stage_worlds(repo,profile,publish,maps,"cakon-"+group,variant(repo,group),("M417",))


if __name__=="__main__":
    repo,profile=(Path(arg).resolve() for arg in sys.argv[1:3])
    stage(repo,profile,sys.argv[3],"--publish" in sys.argv[4:])
