"""Rebuild the Dragon mountain route, its cavern and its cavern arena."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from river_lion_worlds import connected
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
ROAD,CAVE,SHRINE="M476","M488","M798"
MAPS=ROAD,CAVE,SHRINE
ARENAS={ROAD:"M872",CAVE:SHRINE}
POSITIONS={CAVE:{"#1#":[46,3,9,2],"#84#":[46,3,4,2]}}
EXIT_BOUNDS=[0,1.,0,1.55,1.64,.75]
PATCH=f"DRAGON_SPRING_POSITIONS = {POSITIONS!r}\nDRAGON_SPRING_EXIT = {EXIT_BOUNDS!r}\n"+'''
def dragon_spring_battle():
    return MapSpec("M798","Battle: the Dragon mountain cave",128,128,base=CAVE_FLOOR,y=0)


MAPS["M798"]=dragon_spring_battle
BATTLE_SPECS["M798"]=dragon_spring_battle
RSET["M798"]="rt_hd2d_cave"
for _dragon_route,_dragon_arena in (("M476","M872"),("M488","M798")):
    ENCOUNTERS[_dragon_route]=(_dragon_arena,ENCOUNTERS[_dragon_route][1])


def rebuild_dragon_spring(m,ev):
    for key,pos in DRAGON_SPRING_POSITIONS.get(m.mid,{}).items():
        ev.ev[key]["pos"]=list(pos)
    if m.mid=="M488":
        ev.ev["#84#"]["mdl"]["r"]=DRAGON_SPRING_EXIT
    if m.mid=="M798":
        zz,xx=np.indices(m.hgt.shape)
        ledge=87+4.2*np.sin(xx*.143)+2.2*np.cos(xx*.173)
        outer=zz>ledge+3
        stream=(zz>=ledge-4)&(zz<=ledge+1)&(xx>=22)&(xx<=104)
        m.hgt=np.where(outer,4+np.rint(3*np.sin(xx*.09+zz*.14)+1.2*np.cos(zz*.23)),0).astype(int)
        m.blk=np.where(outer,STONE,np.where(stream,WATER,np.where(zz<74,DIRT,CAVE_FLOOR)))
        m.objs=[]
        return

    zz,xx=np.indices(m.hgt.shape)
    if m.mid=="M476":
        approaches=(m.blk==ROAD)
        reserve=np.zeros_like(approaches)
        for row in ev.ev.values():
            x,y,z,d=row.get("pos",(0,0,0,0))
            if y==4 and row["role"]!="villager":
                reserve|=(xx-x)**2+(zz-z)**2<9
        neck=(abs(xx-90)<=3)&(zz>=21)&(zz<34)
        protect=approaches|reserve|neck
        m.objs=[o for o in m.objs if not (o["t"]=="fb" and o["fbtype"] in (20,21))]
        m.hgt[neck]=3
        m.blk[neck]=DIRT
        for x,z,rx,rz,rise in ((18,36,22,14,5),(46,41,18,13,8),(89,37,19,11,7),
                              (128,43,16,14,5),(161,40,21,12,6)):
            profile=((xx-x)/rx)**2+((zz-z)/rz)**2+.07*np.sin(xx*.35+zz*.48)
            rock=(profile<1.)&~protect
            m.blk[rock]=STONE
            m.hgt[rock]=np.maximum(m.hgt[rock],7+np.rint(rise*(1.-profile[rock])).astype(int))
        stream=abs(xx-(115+3.9*np.sin(zz*.135+.61)))<3.0+1.4*np.sin(zz*.235)**2
        stream&=(zz>4)&(zz<46)&~reserve
        bridge=(xx>=104)&(xx<=122)&(zz>=18)&(zz<=24)&~reserve
        m.hgt[stream&~bridge]=1
        m.blk[stream&~bridge]=WATER
        m.hgt[bridge]=3
        m.blk[bridge]=PLANK
        fill(m,87,9,27,7,3,7,STONE)
        return

    m.d=108
    zz,xx=np.indices((m.d,m.w))
    corridors=(
        ((46,3),(46,11),(53,17),(68,19),(78,16),(91,21),(106,23),(116,23),
         (126,20),(138,16),(147,18)),
        ((63,20),(58,26),(54,31),(51,39),(40,41),(36,40),(37,52),(40,63)),
        ((75,19),(76,30),(84,40),(93,46),(105,43),(116,38),(117,27)),
        ((84,39),(72,45),(67,50),(61,62),(54,68),(43,65)),
    )
    main=np.zeros_like(xx,dtype=bool)
    for corridor in corridors:
        main|=order_cave_route(xx,zz,corridor,3.7)
    walk=main.copy()
    for x,z,rx,rz in ((54,15,14,9),(78,22,18,12),(57,34,14,9),(38,41,10,11),
                      (41,62,13,12),(68,54,14,11),(90,42,19,13),(118,34,15,14),(142,18,16,9)):
        boundary=1.+.054*np.cos(xx*.47+zz*.53)+.028*np.sin(xx*.58-zz*.34)
        walk|=((xx-x)/rx)**2+((zz-z)/rz)**2<boundary
    proof=np.zeros_like(walk)
    for row in ev.ev.values():
        x,y,z,d=row.get("pos",(0,0,0,0))
        if y==3 and row["role"] in ("portal","itemchest","custom"):
            proof|=(xx-x)**2+(zz-z)**2<=9
    walk|=proof
    walk[:8,:]&=abs(xx[:8,:]-46)<=3
    walls=9+np.rint(2.1*np.sin(xx*.14+zz*.17)+1.2*np.cos(zz*.23)).astype(int)
    pond=np.zeros_like(walk)
    for x,z,rx,rz in ((72,28,10,6),(94,32,11,7),(63,57,10,5),(112,35,6,4),(42,54,4,8)):
        pond|=((xx-x)/rx)**2+((zz-z)/rz)**2<1.
    water=pond&walk&~(main|proof)
    m.hgt=np.where(water,1,np.where(walk,2,np.where(zz<21,6,walls)))
    m.blk=np.where(water,WATER,np.where(walk,np.where(main,DIRT,CAVE_FLOOR),STONE))
    m.objs=[]
    m.walls=[]
    fill(m,43,8,2,7,2,6,STONE)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_dragon_spring",PATCH,uses_events=True)


def revise_catalog(raw):
    data=json.loads(raw)
    if SHRINE not in data:
        data[SHRINE]=deepcopy(data["M799"])
        data[SHRINE]["name"]="Battle: the Dragon mountain cave"
    else:
        assert data[SHRINE]["name"]=="Battle: the Dragon mountain cave"
    for key,pos in POSITIONS[CAVE].items():
        data[CAVE]["event"][key]["pos"]=pos
    data[CAVE]["event"]["#84#"]["mdl"]["r"]=EXIT_BOUNDS
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
        world,events=gm.make(mid)
        anchored=[]
        if mid!=SHRINE:
            _,base=old.make(mid)
            expected=deepcopy(base.ev)
            for key,pos in POSITIONS.get(mid,{}).items():
                expected[key]["pos"]=pos
            if mid==CAVE:
                expected["#84#"]["mdl"]["r"]=EXIT_BOUNDS
            assert expected==events.ev,mid
            grade=3 if mid==ROAD else 2
            seen=connected(world,gm,(90,21) if mid==ROAD else (46,9),grade)
            for key,event in events.ev.items():
                x,y,z,_=event.get("pos",(0,0,0,0))
                if event["role"] in ("portal","itemchest") or (event["role"]=="custom" and event.get("mdlid")=="CE000"):
                    if y==grade+1:
                        assert (x,z) in seen,(mid,key,x,z)
                        anchored.append(key)
            if mid==ROAD:
                assert all((x,21) in seen for x in range(104,123))
        else:
            assert world.hgt[53:77,35:89].max()==0
        report[mid]={"size":[world.w,world.d],"reachable_events":anchored}
        job=world.write()
        job["out"]=f"tmp/rt_mapgen/{mid}_dragon_mountain_candidate.bw"
        jobs.append(job)
        existing[mid]=candidate[mid]
        if mid==ROAD:
            existing["M872"]=candidate["M872"]
    compile_worlds(profile,jobs,stem="dragon-mountain-route")
    overwrite(destination,json.dumps(existing,ensure_ascii=False,indent="\t").encode())
    for mid in MAPS:
        report[mid]["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"dragon-mountain-worlds.json").write_text(json.dumps(report,indent=2),"utf8")
    print({mid:len(entry["reachable_events"]) for mid,entry in report.items()})


if __name__=="__main__":
    stage(*(Path(value).resolve() for value in sys.argv[1:3]))
