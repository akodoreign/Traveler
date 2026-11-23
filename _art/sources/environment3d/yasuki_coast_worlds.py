"""Rebuild and compile the Yasuki coastal road and its two branch caves."""
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
MAPS=("M470","M480","M481","M829")
POSITIONS={
    "M480":{"#1#":[46,3,8,2],"#84#":[46,3,4,2]},
    "M481":{"#1#":[46,3,8,2],"#85#":[46,3,4,2]},
}
PATCH="YASUKI_CAVE_POSITIONS = "+repr(POSITIONS)+"\n"+'''
_YASUKI_CAVE_PLANS = {
    "M480": (
        94,
        (((46,3),(46,11),(51,17),(63,18),(76,23),(84,32),(91,36),(104,35),(114,27),(126,27),(139,31)),
         ((61,18),(56,27),(51,35),(48,45),(48,54),(47,62)),
         ((48,45),(39,49)),((84,31),(93,21),(95,10)),((122,27),(129,20),(138,14))),
        ((51,15,13,8),(76,23,16,12),(53,36,12,13),(89,36,17,12),(112,29,15,12),
         (140,31,12,10),(46,57,13,13),(96,10,7,6),(138,14,8,6)),
        ((69,33,9,6),(99,48,12,7),(115,37,7,4),(143,36,8,4)),
    ),
    "M481": (
        98,
        (((46,3),(46,13),(53,20),(63,19),(74,22),(85,31),(88,37),(105,41),(115,37),(111,28),
          (122,21),(136,23),(149,29),(164,30),(166,15)),
         ((55,19),(46,24),(36,24)),((69,19),(69,35),(62,48),(60,57),(68,62),(79,60)),
         ((64,45),(53,43),(42,46)),((140,25),(145,37),(155,48))),
        ((47,16,13,9),(74,21,14,11),(90,37,16,12),(111,34,17,13),(74,58,17,12),
         (49,45,13,10),(148,30,16,14),(165,20,8,10),(154,48,10,8),(36,24,7,6)),
        ((90,46,8,6),(113,49,12,7),(135,32,8,5),(154,40,7,6),(66,46,6,7)),
    ),
}


def yasuki_tube_mask(xx, zz, points, radius):
    mask=np.zeros(xx.shape,dtype=bool)
    for (ax,az),(bx,bz) in zip(points,points[1:]):
        dx,dz=bx-ax,bz-az
        t=np.clip(((xx-ax)*dx+(zz-az)*dz)/(dx*dx+dz*dz),0.,1.)
        mask |= (xx-ax-t*dx)**2+(zz-az-t*dz)**2 <= radius**2
    return mask


for _yasuki_mid in ("M480","M481"):
    ENCOUNTERS[_yasuki_mid] = ("M829",ENCOUNTERS[_yasuki_mid][1])


def rebuild_yasuki_caves(m, ev):
    if m.mid=="M829":
        zz,xx=np.indices(m.hgt.shape)
        wall=(zz>86.+2.6*np.sin(xx*.13)+2.2*np.sin(xx*.29)) | (zz<31)
        route=(zz>=59)&(zz<=74)&(xx>19)&(xx<111)
        pools=((xx-44.)/15.)**2+((zz-80.)/5.8)**2<1.
        pools|=((xx-87.)/13.5)**2+((zz-80.)/5.3)**2<1.
        pools &= ~(wall|route)
        m.blk=np.where(wall,STONE,np.where(pools,WATER,CAVE_FLOOR)).astype(np.int32)
        m.blk[route]=DIRT
        m.hgt=np.where(wall,np.where(zz<31,1,8+np.rint(2.*np.sin(xx*.14)).astype(int)),0).astype(np.int32)
        m.objs=[]
        return
    if m.mid=="M470":
        zz,xx=np.indices(m.hgt.shape)
        shore=6.+1.3*np.sin(xx*.091)+.8*np.sin(xx*.227)
        tide=(zz<shore)&((xx<24)|(xx>35))
        mud=(zz>=shore)&(zz<shore+4.)&((xx<24)|(xx>35))
        m.blk[tide]=WATER
        m.hgt[tide]=1
        m.blk[mud]=SAND
        m.objs=[]
        m.yasuki_mouths=[]
        for center in (70,112):
            flank=((xx-center)/19.)**2+((zz-36.)/10.3)**2
            bank=(flank<1.) & (zz>=31) & (np.abs(xx-91)>4)
            bank &= ~((zz>=39)&(xx>=118))
            m.hgt[bank]=np.maximum(m.hgt[bank],8+np.rint(5.*(1.-flank[bank])).astype(int))
            m.blk[bank]=STONE
        for cx in (70,112):
            dx=np.abs(xx-cx)
            # Reserve the sign and the main road in front. The mass
            # closes behind the story threshold and ties into the roof.
            belly=((xx-cx)/15.)**2+((zz-35.)/8.)**2
            rock=(belly<1.)&(zz>=28)
            throat=(dx<=3)&(zz>=25)&(zz<=33)
            rock &= ~throat
            for key in ("#7#","#8#"):
                x,y,z,d=ev.ev[key]["pos"]
                rock[z,x]=False
            m.hgt[rock]=np.maximum(7,11-np.floor(belly[rock]*4).astype(int))
            m.blk[rock]=STONE
            m.hgt[throat]=3
            m.blk[throat]=DIRT
            fill(m,cx-3,9,27,7,3,8,STONE)
            m.yasuki_mouths.append((cx,27,34))
        return

    for key,pos in YASUKI_CAVE_POSITIONS[m.mid].items():
        ev.ev[key]["pos"]=list(pos)
    depth, corridors, chambers, pools = _YASUKI_CAVE_PLANS[m.mid]
    zz,xx=np.indices((depth,m.w))
    path=np.zeros(xx.shape,dtype=bool)
    for points in corridors:
        path |= yasuki_tube_mask(xx,zz,points,3.5)
    open_floor=path.copy()
    for x,z,rx,rz in chambers:
        rough=.062*np.sin(.61*xx+.94*zz)+.038*np.cos(.47*xx-.32*zz)
        open_floor |= ((xx-x)/rx)**2+((zz-z)/rz)**2 < 1.+rough
    important=np.zeros_like(path)
    for event in ev.ev.values():
        if event.get("role") in ("portal","custom","itemchest") and "pos" in event:
            x,y,z,_=event["pos"]
            if y==3:
                important |= (xx-x)**2+(zz-z)**2 <= 9
    open_floor |= important
    # Keep the narrow entry passage square to the threshold; south is the coast.
    open_floor[:8,:] &= (np.abs(xx[:8]-46)<=3)
    floor=2
    tall=9+np.rint(1.34*np.sin(xx*.15+zz*.18)+1.11*np.cos(zz*.29)).astype(int)
    # Match the roof cuts in the normal camera foreground.
    tall=np.where(zz<20,5,tall)
    m.d=depth
    m.hgt=np.where(open_floor,floor,tall).astype(np.int32)
    m.blk=np.where(open_floor,CAVE_FLOOR,STONE).astype(np.int32)
    m.blk[path & open_floor]=DIRT
    m.objs=[]
    m.walls=[]
    for x,z,rx,rz in pools:
        water=(((xx-x)/rx)**2+((zz-z)/rz)**2<1.)&open_floor&~(path|important)
        m.blk[water]=WATER
        m.hgt[water]=1
    fill(m,43,8,2,7,2,6,STONE)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_yasuki_caves",PATCH,uses_events=True)


def connected(world, gm, root, floor):
    free=(world.hgt==floor)&(world.blk!=gm.WATER)
    assert free[root[1],root[0]],root
    pending=deque([root])
    found={root}
    while pending:
        x,z=pending.popleft()
        for nx,nz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            if (nx,nz) not in found and 0<=nx<world.w and 0<=nz<world.d and free[nz,nx]:
                pending.append((nx,nz))
                found.add((nx,nz))
    return found


def audit(world, events, gm):
    if world.mid=="M829":
        assert world.hgt[60:74,30:101].max()==0
        return {"width":world.w,"depth":world.d,"connected_cells":0,"reachable_events":{},
                "battle_water_tiles":int((world.blk==gm.WATER).sum())}
    road=world.mid=="M470"
    floor=3 if road else 2
    root=(70,23) if road else (46,8)
    seen=connected(world,gm,root,floor)
    objectives={}
    for key,event in events.ev.items():
        if event.get("role") in ("portal","itemchest","custom") and "pos" in event:
            x,y,z,_=event["pos"]
            if not road or event.get("mdlid")=="CE000" or event["role"] in ("portal","itemchest"):
                if y==floor+1:
                    assert (x,z) in seen,(world.mid,key,x,z)
                    objectives[key]=[x,z]
    return {"width":world.w,"depth":world.d,"connected_cells":len(seen),"reachable_events":objectives}


def events_for(catalog):
    rows=json.loads(catalog.read_bytes())
    for mid,patch in POSITIONS.items():
        for key,pos in patch.items():
            rows[mid]["event"][key]["pos"]=pos
    for mid in ("M480","M481"):
        for encounter in rows[mid]["encount"]:
            assert encounter["mapid"] in ("M814","M829")
            encounter["mapid"]="M829"
    return rows


def stage(repo,profile):
    _,old,gm,_,_=variant(repo)
    gm.JOBDIR=str(profile/"tmp/rt_mapgen")
    live=repo/"_tools/rpgcobo-tool/project/data/map.json"
    profile_catalog=profile/"project/data/map.json"
    catalog=json.loads(profile_catalog.read_bytes())
    revised=events_for(live)
    reports={}
    jobs=[]
    for mid in MAPS:
        original,before=old.make(mid)
        world,after=gm.make(mid)
        expected=before.ev if before else None
        for key,pos in POSITIONS.get(mid,{}).items():
            expected[key]={**expected[key],"pos":pos}
        assert (after.ev if after else None)==expected,mid
        reports[mid]=audit(world,after,gm)
        reports[mid]["original_depth"]=original.d
        job=world.write()
        job["out"]=f"tmp/rt_mapgen/{mid}_yasuki_candidate.bw"
        jobs.append(job)
        catalog[mid]=revised[mid]
    compile_worlds(profile,jobs,stem="yasuki-coast")
    overwrite(profile_catalog,json.dumps(catalog,ensure_ascii=False,indent="\t").encode())
    for mid,report in reports.items():
        report["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"yasuki-coast-worlds.json").write_text(json.dumps(reports,indent=2),"utf8")
    print({mid:{**value,"reachable_events":len(value["reachable_events"])} for mid,value in reports.items()})


if __name__=="__main__":
    stage(*(Path(arg).resolve() for arg in sys.argv[1:3]))
