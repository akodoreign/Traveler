"""Keep the old hut footprints solid behind their fitted visible models."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


MAPS=("M414","M418")
FRAGMENT='''
def keep_cakon_hut_footprints(m):
    if m.mid=="M414":
        footprints=[(x,24,4,3) for x in (66,74,82)]
    else:
        footprints=[(x+PAD_X,z+PAD_BOTTOM,5,4) for x,z in ((8,22),(20,24),(64,22),(76,23),
                    (88,21),(10,4),(30,5),(70,4),(84,6),(34,22))]
        footprints.append((70,25,8,5))
    m.walls.extend((bx,bz) for x,z,w,d in footprints
                   for bx in range(x,x+w) for bz in range(z,z+d) if (bx,bz) not in m.walls)
'''


if __name__=="__main__":
    root,profile=(Path(arg).resolve() for arg in sys.argv[1:3])
    candidate=with_world_patch(root,MAPS,"keep_cakon_hut_footprints",FRAGMENT)
    stage_worlds(root,profile,"--publish" in sys.argv[3:],MAPS,"cakon-hut-collision",candidate,MAPS)
