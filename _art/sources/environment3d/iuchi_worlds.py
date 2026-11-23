"""Compile Shiro Iuchi and its mine road without replacing story logic."""

from pathlib import Path
import sys

from kensu_worlds import stage_worlds, with_world_patch


TOWER = ("M399", "M400", "M401", "M402", "M878")
MINES = ("M403", "M404", "M405", "M406", "M407", "M879", "M880")
TOWER_POSITIONS = {"M399": {"#4#": [81, 4, 33, 2]}}
MINE_POSITIONS = {
    "M403": {"#85#": [1, 4, 25, 3]},
    "M404": {"#2#": [143, 4, 28, 3]},
    "M405": {"#1#": [36, 3, 7, 2], "#98#": [36, 3, 4, 2], "#99#": [86, 3, 48, 0]},
    "M406": {"#1#": [62, 3, 7, 2], "#112#": [62, 3, 4, 2], "#113#": [86, 3, 48, 0]},
    "M407": {"#1#": [56, 3, 7, 2], "#80#": [56, 3, 4, 2]},
}

TOWER_FRAGMENT = f"IUCHI_TOWER_POSITIONS = {TOWER_POSITIONS!r}\n\n\n" + '''def rebuild_iuchi_tower(m, ev):
    for key, pos in IUCHI_TOWER_POSITIONS.get(m.mid, {}).items():
        x,y,z,_ = pos
        assert int(m.hgt[z,x]) + 1 == y, (m.mid, key, pos)
        ev.ev[key]["pos"] = list(pos)
    if m.mid in ("M399", "M878"):
        m.objs = [obj for obj in m.objs if obj["t"] != "fb" or obj["fbtype"] not in (2,20)]
'''

MINE_FRAGMENT = f"IUCHI_MINE_POSITIONS = {MINE_POSITIONS!r}\n\n\n" + '''def rebuild_iuchi_mines(m, ev):
    for key, pos in IUCHI_MINE_POSITIONS.get(m.mid, {}).items():
        x,y,z,_ = pos
        assert int(m.hgt[z,x]) + 1 == y, (m.mid, key, pos)
        ev.ev[key]["pos"] = list(pos)
    obsolete = {(2,LAMP_TORCH), (2,LAMP_CANDLE), (4,IN["jewel"]), (4,IN["box"]), (4,IN["sword"])}
    camp = m.mid == "M404"
    if camp or m.mid == "M403":
        obsolete.update((20,p) for p in (TREE_S,TREE_M,TREE_L))
    if m.mid in ("M405","M406","M407"):
        obsolete.update((20,p) for p in (ROCK_S,ROCK_M))
    cuts = set()
    if camp:
        tents = [(x,z,6,5) for x,z in ((6,21),(16,22),(70,21),(82,22),(94,21),(8,5),(20,4),(88,5))]
        tents.append((44,21,12,7))
        for x,z,w,d in tents:
            cuts.update((x,z+k,MATTING) for k in range((d+1)//2))
            cuts.add((x+w//2-1,z,VOID))
            cuts.update((tip,z+(d-1)//2,DARKWOOD) for tip in (x-1,x+w))
        for x in (40,58):
            cuts.update(((x,21,DARKWOOD),(x+1,21,PLASTER)))
    m.objs = [obj for obj in m.objs if not (
        obj["t"] == "fb" and (obj["fbtype"],obj["fbparam"]) in obsolete
        or obj["t"] == "fill" and (obj["x"]-PAD_X,obj["z"]-PAD_BOTTOM,obj["blk"]) in cuts
    )]
    if not camp:
        return
    # Build the two sides separately so the former wall has no collider in the passage.
    wall, = (o for o in m.objs if o["t"] == "fill" and o["blk"] == STONE and
             (o["x"],o["y"],o["z"],o["w"],o["h"],o["d"]) == (26,4,36,108,8,4))
    m.objs.remove(wall)
    fill(m,26,4,36,51,8,4,STONE)
    fill(m,84,4,36,50,8,4,STONE)
    fill(m,77,10,36,7,2,4,STONE)
    # Keep the actual eastern transition at block 158 under a solid roof.
    center, start = 28, m.w - 15
    for x in range(start,m.w):
        depth = x - start
        for side in (-1,1):
            for offset, taper in ((3,0),(4,1),(5,3),(6,4)):
                height = min(10,2+depth) - taper + (x+offset*side)%3
                if height > 0:
                    fill(m,x,4,center+side*offset,1,height,1,STONE)
        if depth >= 4:
            for dz in range(-2,3):
                bottom = 9 if abs(dz) == 2 else 10
                top = 11 + min(4,depth//3) - (x+dz)%2
                fill(m,x,bottom,center+dz,1,top-bottom+1,1,STONE)
'''


def variant(repo, mines=False):
    if mines:
        return with_world_patch(repo, MINES, "rebuild_iuchi_mines", MINE_FRAGMENT, uses_events=True)
    return with_world_patch(repo, TOWER, "rebuild_iuchi_tower", TOWER_FRAGMENT, uses_events=True)


def stage(repo, profile, publish, mines=False):
    maps = MINES if mines else TOWER
    optional = ("M404", "M405", "M406", "M407", "M879", "M880") if mines else TOWER[1:]
    stage_worlds(repo, profile, publish, maps, "iuchi-mines" if mines else "iuchi-tower",
                 variant(repo, mines), optional, positions=MINE_POSITIONS if mines else TOWER_POSITIONS)


if __name__ == "__main__":
    repo, profile = (Path(arg).resolve() for arg in sys.argv[1:3])
    stage(repo, profile, "--publish" in sys.argv[3:], "--mines" in sys.argv[3:])
