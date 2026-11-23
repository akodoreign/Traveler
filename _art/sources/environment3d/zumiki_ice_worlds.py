"""Compile Zumiki’s snow road, ice cave, and sheltered snowbound arena."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from river_lion_worlds import connected
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
ROAD,CAVE,ARENA="M473","M485","M844"
MAPS=(ROAD,CAVE,ARENA)
POSITIONS={
    ROAD:{"#3#":[74,4,29,0],"#6#":[77,4,28,2]},
    CAVE:{"#1#":[46,3,8,2],"#83#":[46,3,4,2]},
}
PATCH="ZUMIKI_ICE_POSITIONS = "+repr(POSITIONS)+'''
ENCOUNTERS["M485"]=("M844",ENCOUNTERS["M485"][1])


def rebuild_zumiki_ice_route(m,ev):
    for key,pos in ZUMIKI_ICE_POSITIONS.get(m.mid,{}).items():
        ev.ev[key]["pos"]=list(pos)
    if m.mid=="M473":
        zz,xx=np.indices(m.hgt.shape)
        route=m.blk==ROAD
        snowy=(m.hgt>3)&np.isin(m.blk,(T(2,0),T(2,1)))
        m.hgt[snowy]=3
        m.blk[snowy]=SNOW
        m.objs=[]
        cx=74
        hill=((xx-cx)/17.)**2+((zz-36.)/10.)**2
        throat=(abs(xx-cx)<=3)&(zz>=25)&(zz<=34)
        occupied=np.zeros(hill.shape,dtype=bool)
        for e in ev.ev.values():
            if e.get("pos") and e["pos"][1]==4 and e["role"]!="villager":
                x,y,z,d=e["pos"]
                occupied|=(xx-x)**2+(zz-z)**2<=5
        rock=(hill<1.)&(zz>=28)&~(throat|occupied|route)
        for x,z,w,h in ((24,44,17,9),(111,47,14,8),(161,43,15,8)):
            mound=((xx-x)/w)**2+((zz-z)/h)**2
            flank=(mound<1.)&(abs(xx-91)>9)&(zz>35)&~(route|occupied)
            m.hgt[flank]=np.maximum(m.hgt[flank],6+np.rint(4.*(1.-mound[flank])).astype(int))
            m.blk[flank]=STONE
        m.blk[rock]=STONE
        m.hgt[rock]=np.maximum(m.hgt[rock],8+np.rint(5.2*(1.-hill[rock])).astype(int))
        m.hgt[throat]=3
        m.blk[throat]=ROAD
        fill(m,cx-3,9,27,7,4,8,STONE)
        pool=((xx-117.)/17.1)**2+((zz-8.)/5.8)**2<1.
        pool &= ~occupied&~route
        m.hgt[pool]=1
        m.blk[pool]=WATER
        return
    if m.mid=="M844":
        zz,xx=np.indices(m.hgt.shape)
        rock=(zz>86.+2.6*np.sin(xx*.10)+1.7*np.sin(xx*.21)) | (zz<29)
        m.hgt=np.where(rock,np.where(zz<29,1,8+np.rint(2.*np.sin(xx*.13)).astype(int)),0).astype(np.int32)
        m.blk=np.where(rock,STONE,SNOW).astype(np.int32)
        m.objs=[]
        return

    m.d=104
    zz,xx=np.indices((m.d,m.w))
    passes=(
        ((46,3),(46,13),(54,17),(69,20),(77,19),(86,23),(103,22),(114,25),(127,26),
         (142,25),(149,28),(163,28),(173,29)),
        ((54,17),(52,28),(52,33),(49,42),(44,50)),
        ((69,20),(68,31),(72,42),(78,54)), ((103,22),(95,31),(87,38),(77,43),(72,42)),
        ((142,25),(147,18),(153,13)),
    )
    path=np.zeros(xx.shape,dtype=bool)
    for line in passes:
        path |= order_cave_route(xx,zz,line,3.9)
    walk=path.copy()
    for x,z,rx,rz in ((50,15,13,9),(73,22,17,12),(53,34,13,10),(49,47,14,10),
                      (76,49,16,12),(102,27,18,13),(123,27,16,11),(147,27,16,11),
                      (154,13,10,7),(171,29,11,8)):
        fold=.055*np.sin(.79*xx+.39*zz)+.035*np.cos(.29*xx-.41*zz)
        walk|=((xx-x)/rx)**2+((zz-z)/rz)**2<1.+fold
    important=np.zeros_like(path)
    for e in ev.ev.values():
        if e.get("pos") and e.get("role") in ("portal","custom","itemchest"):
            x,y,z,_=e["pos"]
            if y==3:
                important|=(xx-x)**2+(zz-z)**2<=8
    walk|=important
    walk[:8,:] &= abs(xx[:8]-46)<=3
    ridge=10+np.rint(1.7*np.sin(.13*xx+.30*zz)+1.3*np.cos(.22*xx-.13*zz)).astype(int)
    m.hgt=np.where(walk,2,np.where(zz<19,5,ridge)).astype(np.int32)
    m.blk=np.where(walk,np.where(path,ROAD,CAVE_FLOOR),STONE).astype(np.int32)
    m.objs=[]
    m.walls=[]
    for x,z,rx,rz in ((63,36,12,9),(107,37,8,6),(138,34,8,5)):
        pool=(((xx-x)/rx)**2+((zz-z)/rz)**2<1.)&walk&~(path|important)
        m.blk[pool]=WATER
        m.hgt[pool]=1
    fill(m,43,8,2,7,2,6,STONE)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_zumiki_ice_route",PATCH,uses_events=True)


def revise_catalog(raw):
    table=json.loads(raw)
    for mid,changes in POSITIONS.items():
        for key,pos in changes.items():
            table[mid]["event"][key]["pos"]=pos
    for group in table[CAVE]["encount"]:
        group["mapid"]=ARENA
    return table


def stage(repo,profile):
    _,base,worlds,_,_=variant(repo)
    worlds.JOBDIR=str(profile/"tmp/rt_mapgen")
    live=repo/"_tools/rpgcobo-tool/project/data/map.json"
    dst=profile/"project/data/map.json"
    selected=revise_catalog(live.read_bytes())
    stored=json.loads(dst.read_bytes())
    jobs,proof=[],{}
    for mid in MAPS:
        old,prior=base.make(mid)
        m,ev=worlds.make(mid)
        expected=deepcopy(prior.ev) if prior else None
        for key,pos in POSITIONS.get(mid,{}).items():
            expected[key]["pos"]=pos
        assert expected==(ev.ev if ev else None),mid
        exact=[]
        if mid!=ARENA:
            floor=3 if mid==ROAD else 2
            dry=connected(m,worlds,(91,22) if mid==ROAD else (46,8),floor)
            for key,e in ev.ev.items():
                x,y,z,_=e.get("pos",(0,0,0,0))
                if e["role"] in ("portal","itemchest") or (e["role"]=="custom" and e.get("mdlid")=="CE000"):
                    if y==floor+1:
                        assert (x,z) in dry,(mid,key,x,z)
                        exact.append(key)
        proof[mid]={"size":[m.w,m.d],"old_depth":old.d,"reachable_events":exact}
        job=m.write()
        job["out"]=f"tmp/rt_mapgen/{mid}_zumiki_candidate.bw"
        jobs.append(job)
        stored[mid]=selected[mid]
    compile_worlds(profile,jobs,stem="zumiki-ice")
    overwrite(dst,json.dumps(stored,ensure_ascii=False,indent="\t").encode())
    for mid in MAPS:
        proof[mid]["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"zumiki-ice-worlds.json").write_text(json.dumps(proof,indent=2),"utf8")
    print({mid:len(row["reachable_events"]) for mid,row in proof.items()})


if __name__=="__main__":
    stage(*(Path(x).resolve() for x in sys.argv[1:3]))
