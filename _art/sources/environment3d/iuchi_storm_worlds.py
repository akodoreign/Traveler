"""Compile the Iuchi siege route and open the storm room's rear windows."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


LOWER = ("M408", "M409", "M410", "M881")
UPPER = ("M411", "M412", "M882")
LOWER_POSITIONS = {"M410": {"#2#": [126,4,20,0]}}

LOWER_FRAGMENT = f"IUCHI_NARROWS_POSITIONS = {LOWER_POSITIONS!r}\n\n\n" + '''def rebuild_iuchi_wind_approach(m, ev):
    if m.mid == "M410":
        for key, pos in IUCHI_NARROWS_POSITIONS[m.mid].items():
            x,y,z,_ = pos
            assert int(m.hgt[z,x]) + 1 == y, (m.mid, key, pos)
            ev.ev[key]["pos"] = list(pos)
        # Replace the solid gatehouse with jambs and a true through opening.
        gate = {(122,4,18,8,10,4,STONEW), (124,4,17,4,6,1,VOID)}
        m.objs = [o for o in m.objs if o["t"] != "fill" or
                  tuple(o[k] for k in ("x","y","z","w","h","d","blk")) not in gate]
        fill(m,122,4,18,2,10,4,STONEW)
        fill(m,128,4,18,2,10,4,STONEW)
        fill(m,124,10,18,4,4,4,STONEW)
        return
    if m.mid != "M408":
        return
    tents = [(x,21,6,5) for x in range(4,50,10)] + [(62,21,8,6),(74,22,8,6)]
    old = set()
    for x,z,w,d in tents:
        old.update((x,z+k,MATTING) for k in range((d+1)//2))
        old.add((x+w//2-1,z,VOID))
        old.update((tip,z+(d-1)//2,DARKWOOD) for tip in (x-1,x+w))
    m.objs = [o for o in m.objs if not (
        o["t"] == "fb" and (o["fbtype"],o["fbparam"]) == (2,LAMP_TORCH)
        or o["t"] == "fill" and (o["x"]-PAD_X,o["z"]-PAD_BOTTOM,o["blk"]) in old
    )]
    # The chapter's touch event stays at x134 in this east-facing passage.
    for x in range(131,146):
        advance = x-131
        for offset, slope in ((3,0),(4,2),(5,3)):
            for side in (-1,1):
                h = min(10,3+advance)-slope + (x+offset*side)%2
                if h > 0:
                    fill(m,x,4,20+side*offset,1,h,1,STONE)
        if advance >= 2:
            fill(m,x,9,18,1,min(5,2+advance//4),5,STONE)
'''

UPPER_FRAGMENT = '''def rebuild_iuchi_storm_room(m):
    if m.mid == "M882":
        m.objs = [o for o in m.objs if o["t"] != "fb" or (o["fbtype"],o["fbparam"]) != (2,LAMP_CANDLE)]
    if m.mid != "M412":
        return
    # Keep a continuous sill and expose the actual wall plane, in front of the old void cuts.
    m.objs = [o for o in m.objs if not (o["t"] == "fill" and o["d"] == 1 and
               (o["z"] == 21 or (o["z"] == 22 and o["blk"] == VOID)))]
    fill(m,4,2,21,32,2,1,STONEW)
    fill(m,4,7,21,32,1,1,DARKWOOD)
    for x,w in ((4,4),(12,2),(18,2),(24,2),(30,2),(35,1)):
        fill(m,x,4,21,w,3,1,STONEW)
'''


def variant(repo, upper=False):
    if upper:
        return with_world_patch(repo,UPPER,"rebuild_iuchi_storm_room",UPPER_FRAGMENT)
    return with_world_patch(repo,LOWER,"rebuild_iuchi_wind_approach",LOWER_FRAGMENT,uses_events=True)


def stage(repo, profile, publish, upper=False):
    maps=UPPER if upper else LOWER
    optional=("M411","M412","M882") if upper else LOWER
    stage_worlds(repo,profile,publish,maps,"iuchi-storm-room" if upper else "iuchi-wind-siege",
                 variant(repo,upper),optional,positions=None if upper else LOWER_POSITIONS)


if __name__ == "__main__":
    repo,profile=(Path(arg).resolve() for arg in sys.argv[1:3])
    stage(repo,profile,"--publish" in sys.argv[3:],"--upper" in sys.argv[3:])
