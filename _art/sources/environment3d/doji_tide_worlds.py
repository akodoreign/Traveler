"""Compile the Doji coastal road, tide cave, and the cove battle ground."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from river_lion_worlds import connected
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
ROAD,CAVE,ARENA="M474","M486","M828"
MAPS=ROAD,CAVE,ARENA
ARENAS={ROAD:ARENA,CAVE:"M829"}
POSITIONS={CAVE:{"#1#":[46,3,8,2],"#85#":[46,3,4,2]}}
PATCH="DOJI_TIDE_POSITIONS = "+repr(POSITIONS)+"\n"+"DOJI_BATTLE_SCENES = "+repr(ARENAS)+'''
for _doji_route,_doji_arena in DOJI_BATTLE_SCENES.items():
    ENCOUNTERS[_doji_route]=(_doji_arena,ENCOUNTERS[_doji_route][1])


def rebuild_doji_tide_caves(m,ev):
    for key,pos in DOJI_TIDE_POSITIONS.get(m.mid,{}).items():
        ev.ev[key]["pos"]=list(pos)
    if m.mid=="M828":
        zz,xx=np.indices(m.hgt.shape)
        outer=86.+5.3*np.sin(xx*.069)+1.7*np.cos(xx*.25)
        beach=(zz>=74)&(zz<=outer)
        water=(zz>outer)&~((xx<23)&(zz<102))&~((xx>110)&(zz<98))
        ridge=((zz>84)&(xx<24)&~water)|((zz>82)&(xx>111)&~water)
        m.hgt=np.where(ridge,4+np.rint(1.8*np.sin(xx*.17+zz*.09)).astype(int),0)
        m.blk=np.where(water,WATER,np.where(ridge,STONE,np.where(beach,SAND,DIRT))).astype(np.int32)
        m.objs=[]
        return

    zz,xx=np.indices(m.hgt.shape)
    if m.mid=="M474":
        routes=m.blk==ROAD
        old=(m.hgt>3)&np.isin(m.blk,(T(2,0),T(2,1)))
        m.hgt[old]=3
        m.blk[old]=GRASS
        m.objs=[]
        reserve=np.zeros_like(routes)
        for e in ev.ev.values():
            if e.get("pos") and e["pos"][1]==4 and e["role"]!="villager":
                x,y,z,d=e["pos"]
                reserve|=(xx-x)**2+(zz-z)**2<=5
        coast=8.5+1.7*np.sin(xx*.087)+1.5*np.sin(xx*.16-.71)
        causeway=(abs(xx-91)<=4)&(zz<=12)
        foreshore=(zz<coast+3.7)&(xx>=4)&(xx<153)&~(reserve|routes)
        surf=(zz<coast)&foreshore&~causeway
        m.blk[foreshore]=SAND
        m.blk[surf]=WATER
        m.hgt[surf]=1
        m.blk[causeway]=PLANK
        cx=90
        neck=(abs(xx-cx)<=3)&(zz>=25)&(zz<=33)
        for px,pz,rx,rz in ((90,36,18,10),(58,45,19,12),(120,43,17,10),(160,45,14,9)):
            lump=((xx-px)/rx)**2+((zz-pz)/rz)**2
            hill=(lump<1.)&(zz>=28)&~(neck|routes|reserve)
            m.hgt[hill]=np.maximum(m.hgt[hill],7+np.rint(6.0*(1.-lump[hill])).astype(int))
            m.blk[hill]=STONE
        m.hgt[neck]=3
        m.blk[neck]=DIRT
        fill(m,cx-3,9,27,7,3,7,STONE)
        return

    m.d=108
    zz,xx=np.indices((m.d,m.w))
    paths=(
        ((46,3),(46,13),(55,18),(66,20),(74,22),(82,26),(93,27),(101,26),(112,26),
         (124,30),(135,37),(147,42),(162,43)),
        ((60,19),(54,26),(53,37),(50,46),(44,52),(40,58),(37,65)),
        ((73,22),(79,29),(83,34),(86,44),(91,48)),
        ((109,27),(111,34),(120,40)),((86,44),(86,52),(81,57)),
        ((144,41),(151,33),(158,29),(166,22),(170,14)),
    )
    lanes=np.zeros(xx.shape,dtype=bool)
    for line in paths:
        lanes|=order_cave_route(xx,zz,line,3.8)
    walk=lanes.copy()
    for x,z,rx,rz in ((52,16,14,10),(71,24,16,12),(56,36,14,10),(47,52,11,13),
                     (37,64,10,8),(86,42,15,13),(80,58,13,9),(109,29,20,12),
                     (120,39,14,10),(140,37,16,11),(156,43,16,12),(168,17,10,10)):
        flake=.055*np.sin(xx*.71+zz*.31)+.032*np.cos(xx*.44-zz*.24)
        walk|=((xx-x)/rx)**2+((zz-z)/rz)**2<1.+flake
    keep=np.zeros_like(walk)
    for e in ev.ev.values():
        if e.get("pos") and e.get("role") in ("portal","custom","itemchest"):
            x,y,z,_=e["pos"]
            if y==3:
                keep|=(xx-x)**2+(zz-z)**2<=9
    walk|=keep
    walk[:8,:] &= abs(xx[:8]-46)<=3
    wall=9+np.rint(1.8*np.sin(xx*.17+zz*.19)+1.1*np.cos(zz*.27)).astype(int)
    m.hgt=np.where(walk,2,np.where(zz<21,5,wall)).astype(np.int32)
    m.blk=np.where(walk,np.where(lanes,DIRT,CAVE_FLOOR),STONE).astype(np.int32)
    m.objs=[]
    m.walls=[]
    flow=90.1+2.7*np.sin(zz*.19)
    tidal=(abs(xx-flow)<2.75+.45*np.cos(zz*.4))&(zz>=16)&(zz<=58)
    decking=(xx>=83)&(xx<=98)&(zz>=24)&(zz<=29)&walk
    water=tidal&~(decking|keep)
    for x,z,rx,rz in ((67,32,10,6),(103,36,9,6),(128,45,11,6),(151,47,9,6),(42,57,6,5)):
        water|=(((xx-x)/rx)**2+((zz-z)/rz)**2<1.)&walk&~(lanes|keep|decking)
    m.blk[water]=WATER
    m.hgt[water]=1
    m.blk[decking]=PLANK
    fill(m,43,8,2,7,2,6,STONE)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_doji_tide_caves",PATCH,uses_events=True)


def revise_catalog(raw):
    data=json.loads(raw)
    for mid,changes in POSITIONS.items():
        for key,pos in changes.items():
            data[mid]["event"][key]["pos"]=pos
    for mid,arena in ARENAS.items():
        for row in data[mid]["encount"]:
            row["mapid"]=arena
    return data


def stage(repo,profile):
    _,old,gm,_,_=variant(repo)
    gm.JOBDIR=str(profile/"tmp/rt_mapgen")
    destination=profile/"project/data/map.json"
    existing=json.loads(destination.read_bytes())
    candidate=revise_catalog((repo/"_tools/rpgcobo-tool/project/data/map.json").read_bytes())
    report,jobs={},[]
    for mid in MAPS:
        prior,base=old.make(mid)
        world,events=gm.make(mid)
        expected=deepcopy(base.ev) if base else None
        for key,pos in POSITIONS.get(mid,{}).items():
            expected[key]["pos"]=pos
        assert expected==(events.ev if events else None),mid
        anchors=[]
        if mid!=ARENA:
            floor=3 if mid==ROAD else 2
            seen=connected(world,gm,(90,22) if mid==ROAD else (46,8),floor)
            for key,event in events.ev.items():
                x,y,z,_=event.get("pos",(0,0,0,0))
                if event["role"] in ("portal","itemchest") or (event["role"]=="custom" and event.get("mdlid")=="CE000"):
                    if y==floor+1:
                        assert (x,z) in seen,(mid,key,x,z)
                        anchors.append(key)
            if mid==CAVE:
                assert (90,27) in seen and (96,27) in seen
        else:
            assert world.hgt[53:77,35:89].max()==0
        report[mid]={"size":[world.w,world.d],"original_depth":prior.d,"reachable_events":anchors}
        record=world.write()
        record["out"]=f"tmp/rt_mapgen/{mid}_doji_tide_candidate.bw"
        jobs.append(record)
        existing[mid]=candidate[mid]
    compile_worlds(profile,jobs,stem="doji-tide-route")
    overwrite(destination,json.dumps(existing,ensure_ascii=False,indent="\t").encode())
    for mid in MAPS:
        report[mid]["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"doji-tide-worlds.json").write_text(json.dumps(report,indent=2),"utf8")
    print({mid:len(entry["reachable_events"]) for mid,entry in report.items()})


if __name__=="__main__":
    stage(*(Path(value).resolve() for value in sys.argv[1:3]))
