"""Rebuild Snake Den collision and chamber shapes around the original events."""
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from shadowlands_march_worlds import compile_worlds, overwrite

MAPS=("M425","M426","M427","M428","M890")
HERE=Path(__file__).resolve().parent
PROOF=HERE/"cakon-snake-den-worlds.json"

PATCH='''
_ORDER_CAVE_PLANS = {
    # (expanded depth, walk routes, chambers: center x/z and horizontal/depth radii)
    "M425": (
        76,
        (((26,19),(38,19),(49,20),(56,24),(65,23),(73,19),(86,23),(97,24),(108,19),(115,19),
          (125,23),(135,29),(143,32)), ((58,22),(58,32),(62,40)), ((87,23),(94,32),(103,39))),
        ((38,20,11,9),(60,25,17,11),(86,25,15,12),(110,20,14,9),(63,40,10,7),(105,40,12,8))),
    "M426": (
        63,
        (((26,16),(38,16),(58,19),(82,21),(97,16),(108,17),(117,21),(125,21)),),
        ((41,16,14,9),(73,21,32,13),(106,21,15,9))),
    "M427": (
        68,
        (((25,19),(34,19),(46,22),(54,19),(65,21),(73,24),(73,34)),),
        ((38,21,14,11),(58,23,16,13),(73,27,13,11),(89,30,13,10))),
    "M428": (
        76,
        (((28,19),(39,19),(49,16),(59,19),(69,25),(82,19),(93,19),(106,19),(110,19)),
         ((80,22),(88,31),(97,39)), ((60,22),(58,32),(52,39))),
        ((37,19,10,8),(58,23,16,12),(85,23,18,13),(103,21,10,9),(97,40,11,8),(50,39,10,9))),
    "M890": (
        128,
        (((9,68),(48,65),(65,65),(96,69),(121,72)), ((61,66),(66,85),(73,99))),
        ((62,66,38,28),(89,75,27,19),(33,78,22,20),(66,98,26,17))),
}


def order_cave_route(xx, zz, points, radius):
    mask=np.zeros(xx.shape,dtype=bool)
    for (ax,az),(bx,bz) in zip(points,points[1:]):
        dx,dz=bx-ax,bz-az
        t=np.clip(((xx-ax)*dx+(zz-az)*dz)/(dx*dx+dz*dz),0.,1.)
        mask |= (xx-ax-t*dx)**2+(zz-az-t*dz)**2 <= radius*radius
    return mask


def rebuild_order_caves(m, ev):
    depth, paths, rooms = _ORDER_CAVE_PLANS[m.mid]
    xx,zz=np.meshgrid(np.arange(m.w),np.arange(depth))
    arena=m.mid=="M890"
    floor=0 if arena else 2
    path=np.zeros(xx.shape,dtype=bool)
    for points in paths:
        path |= order_cave_route(xx,zz,points,6.0 if arena else 4.2)
    open_floor=path.copy()
    for x,z,rx,rz in rooms:
        ripple=.053*np.sin(xx*.91+zz*.46)+.034*np.cos(zz*.69-xx*.22)
        open_floor |= ((xx-x)/rx)**2+((zz-z)/rz)**2 <= 1.+ripple

    # Reserve the unchanged interaction anchors within the rebuilt floor plan.
    if ev is not None:
        for key, event in ev.ev.items():
            if event.get("role")=="light" or "pos" not in event or int(key.strip("#"))>12 and event.get("role")!="portal":
                continue
            x,y,z,_=event["pos"]
            if event.get("role") in ("portal","itemchest") or event.get("mdlid")=="CE000":
                open_floor |= ((xx-x)**2+(zz-z)**2 <= 9)&(y==floor+1)

    wall_top=np.where(zz<(39 if arena else 16),floor+2,
                      floor+7+np.floor(1.7*np.sin(xx*.20+zz*.15)+1.5*np.cos(zz*.29)).astype(int))
    m.d=depth
    m.hgt=np.where(open_floor,floor,wall_top).astype(np.int32)
    m.blk=np.where(open_floor,CAVE_FLOOR,STONE).astype(np.int32)
    m.blk[path]=ROAD
    m.objs=[]
    m.walls=[]
    if m.mid=="M426":
        sand=((xx-73)/32)**2+((zz-21)/12)**2 < 1.
        m.blk[open_floor & sand]=SAND
    for x,z,rx,rz in {
        "M425":((106,41,8.1,4.4),),
        "M427":((94,33,5.4,4.2),),
        "M428":((49,39,7.1,4.6),),
        "M890":((38,84,10.8,3.55),(103,88,13.5,3.62)),
    }.get(m.mid,()):
        pond=(((xx-x)/rx)**2+((zz-z)/rz)**2<1.) & open_floor & ~path
        m.blk[pond]=WATER
        m.hgt[pond]=max(0,floor-1)
    if m.mid=="M427":
        # Tie both jambs into the chamber walls. The ridge has one
        # opening, centered on the original portal at (73, 26).
        across=np.abs(xx-73)
        threshold=28.+.93*np.sin(xx*.14)
        ridge=(across>3)&(np.abs(zz-threshold)<2.28+.60*np.sin(xx*.35))
        rubble=3+np.minimum(5,(across//4)).astype(np.int32)
        m.hgt[ridge]=np.maximum(m.hgt[ridge],floor+rubble[ridge])
        m.blk[ridge]=STONE
    if m.mid=="M428":
        # The back of the exit platform is the boathouse ladder.
        for z in range(22,25):
            for x in range(103,109):
                if m.hgt[z,x]==floor:
                    m.walls.append((x,z))
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_order_caves",PATCH,uses_events=True)


def map_anchors(events):
    if events is None:
        return []
    anchors=[]
    for key,event in events.ev.items():
        if "pos" not in event or event.get("role")=="light":
            continue
        if not (int(key.strip("#"))<=12 or event.get("role")=="portal"):
            continue
        if event.get("mdlid")=="CE000" or event.get("role") in ("portal","itemchest"):
            x,y,z,_=event["pos"]
            if y==3:
                anchors.append((key,x,z))
    return anchors


def audit(gm,world,events):
    anchors=map_anchors(events)
    if not anchors:
        return {"width":world.w,"depth":world.d,"battle_floor":int(world.hgt[66,66])}
    floor=(world.hgt==2)&(world.blk!=gm.WATER)
    for x,z in world.walls:
        floor[z,x]=False
    _,x,z=anchors[0]
    seen={(x,z)}
    frontier=deque(seen)
    while frontier:
        x,z=frontier.popleft()
        for nx,nz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            if 0<=nx<world.w and 0<=nz<world.d and floor[nz,nx] and (nx,nz) not in seen:
                seen.add((nx,nz))
                frontier.append((nx,nz))
    for key,x,z in anchors:
        assert floor[z,x] and (x,z) in seen,(world.mid,key,x,z)
    return {"width":world.w,"depth":world.d,"connected_floor_cells":len(seen),
            "unchanged_reachable_anchors":len(anchors)}


def stage(repo,profile,publish=False):
    source,old,gm,prior,updated=variant(repo)
    gm.JOBDIR=str(profile/"tmp/rt_mapgen")
    jobs,proof=[],{}
    for mid in MAPS:
        original,before=old.make(mid)
        world,after=gm.make(mid)
        assert (before.ev if before else None)==(after.ev if after else None),mid
        proof[mid]=audit(gm,world,after)
        proof[mid]["source_depth"]=original.d
        if not publish:
            entry=world.write()
            entry["out"]=f"tmp/rt_mapgen/{mid}_snake_den_candidate.bw"
            jobs.append(entry)
    if not publish:
        compile_worlds(profile,jobs,stem="cakon-snake-den")
        for mid,info in proof.items():
            info["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
        PROOF.write_text(json.dumps(proof,indent=2),"utf8")
    else:
        receipts=json.loads(PROOF.read_bytes())
        engine=repo/"_tools/rpgcobo-tool"
        contents={}
        for mid in MAPS:
            local=Path(f"project/data/mapdata/{mid}.bw")
            data=(profile/local).read_bytes()
            assert sha256(data).hexdigest()==receipts[mid]["sha256"],mid
            contents[engine/local]=data
        assert source.read_bytes()==prior
        for path,data in contents.items():
            overwrite(path,data)
        overwrite(source,updated)
    print(proof,flush=True)


if __name__=="__main__":
    stage(*(Path(v).resolve() for v in sys.argv[1:3]),"--publish" in sys.argv[3:])
