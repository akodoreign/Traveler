"""Build Beiden's through road, bandit hideout and their battle settings."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from river_lion_worlds import connected
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
ROAD,CAVE,FIELD,HIDEOUT="M477","M489","M821","M797"
MAPS=ROAD,CAVE,FIELD,HIDEOUT
ARENAS={CAVE:HIDEOUT}
POSITIONS={CAVE:{"#1#":[46,3,9,2],"#86#":[46,3,4,2]}}
BOUNDS=[0,1.,0,1.54,1.63,.78]
PATCH=f"BEIDEN_HIDEOUT_POSITIONS = {POSITIONS!r}\nBEIDEN_HIDEOUT_BOUNDS = {BOUNDS!r}\n"+'''
def battle_beiden_bandit_hideout():
    return MapSpec("M797","Battle: the Beiden hideout",128,128,base=CAVE_FLOOR,y=0)


MAPS["M797"]=battle_beiden_bandit_hideout
BATTLE_SPECS["M797"]=battle_beiden_bandit_hideout
RSET["M797"]="rt_hd2d_cave"
ENCOUNTERS["M489"]=("M797",ENCOUNTERS["M489"][1])


def rebuild_beiden_bandit_hideout(m,ev):
    for key,pos in BEIDEN_HIDEOUT_POSITIONS.get(m.mid,{}).items():
        ev.ev[key]["pos"]=list(pos)
    if m.mid=="M489":
        ev.ev["#86#"]["mdl"]["r"]=BEIDEN_HIDEOUT_BOUNDS
    zz,xx=np.indices(m.hgt.shape)
    if m.mid=="M477":
        clean=m.blk==ROAD
        for event in ev.ev.values():
            x,y,z,_=event.get("pos",(0,0,0,0))
            if y==4 and event["role"]!="villager":
                clean|=(xx-x)**2+(zz-z)**2<10
        branch=(abs(xx-90)<=3)&(zz>=21)&(zz<34)
        clean|=branch
        m.hgt[branch]=3
        m.blk[branch]=DIRT
        for x,z,rx,rz,rise in ((19,41,20,13,4),(66,46,16,11,4),(92,39,18,11,6),
                              (115,38,13,8,4),(161,42,18,14,5)):
            border=((xx-x)/rx)**2+((zz-z)/rz)**2+.05*np.cos(xx*.47+zz*.38)
            hill=(border<1.)&~clean
            m.hgt[hill]=np.maximum(m.hgt[hill],6+np.rint(rise*(1.-border[hill])).astype(int))
            m.blk[hill]=STONE
        m.objs=[o for o in m.objs if not (o["t"]=="fb" and o["fbtype"] in (20,21))]
        fill(m,87,9,27,7,3,7,STONE)
        return

    if m.mid in ("M821","M797"):
        fields=m.mid=="M821"
        limit=83+4.4*np.sin(xx*.097)+2.8*np.cos(xx*.235)
        sides=(zz>limit-3)&((xx<25)|(xx>103))
        recess=(zz>limit+1)&~((abs(xx-70)<8)&(zz<92))
        rock=sides|((zz>=106) if fields else recess)
        clean=np.where(zz>76,GRASS3 if fields else CAVE_FLOOR,DIRT)
        m.blk=np.where(rock,STONE,clean)
        m.hgt=np.where(rock,(7+np.rint(3.*np.sin(xx*.17+zz*.27)+.66*np.cos(zz*.31))).astype(int),0)
        m.objs=[]
        return

    m.d=115
    zz,xx=np.indices((m.d,m.w))
    tunnels=(
        ((46,3),(46,11),(54,17),(67,22),(78,20),(85,27),(95,24),(107,23),
         (121,21),(131,17),(142,21),(154,25),(160,29),(168,43)),
        ((63,23),(57,32),(55,36),(49,48),(41,55),(34,59)),
        ((76,21),(78,31),(85,38),(93,43),(107,44),(119,43)),
        ((85,36),(77,46),(69,53),(78,59),(91,63),(100,66),(115,66),(127,61)),
        ((141,22),(134,31),(127,41),(118,43),(112,51),(127,61)),
    )
    route=np.zeros_like(xx,dtype=bool)
    for tunnel in tunnels:
        route|=order_cave_route(xx,zz,tunnel,3.75)
    ground=route.copy()
    for x,z,rx,rz in ((50,14,12,10),(68,22,15,10),(87,30,15,11),(58,36,14,10),
                      (43,55,13,10),(69,53,13,11),(101,65,15,12),(123,58,15,12),
                      (122,43,18,12),(108,24,16,10),(140,20,15,10),(161,32,14,10),
                      (167,44,13,10)):
        lobe=1.+.049*np.sin(xx*.56+zz*.39)+.037*np.cos(xx*.63-zz*.22)
        ground|=((xx-x)/rx)**2+((zz-z)/rz)**2<lobe
    for event in ev.ev.values():
        x,y,z,_=event.get("pos",(0,0,0,0))
        if y==3 and event["role"] in ("portal","itemchest","custom"):
            ground|=(xx-x)**2+(zz-z)**2<=10
    ground[:8]&=abs(xx[:8]-46)<=3
    walls=9+np.rint(2.3*np.sin(xx*.133+zz*.159)+1.3*np.cos(zz*.24)).astype(int)
    m.hgt=np.where(ground,2,np.where(zz<20,6,walls))
    m.blk=np.where(ground,np.where(route,DIRT,CAVE_FLOOR),STONE)
    m.objs=[]
    m.walls=[]
    fill(m,43,8,2,7,2,6,STONE)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_beiden_bandit_hideout",PATCH,uses_events=True)


def revise_catalog(raw):
    data=json.loads(raw)
    if HIDEOUT not in data:
        data[HIDEOUT]=deepcopy(data["M799"])
        data[HIDEOUT]["name"]="Battle: the Beiden hideout"
    else:
        assert data[HIDEOUT]["name"]=="Battle: the Beiden hideout"
    for key,pos in POSITIONS[CAVE].items():
        data[CAVE]["event"][key]["pos"]=pos
    data[CAVE]["event"]["#86#"]["mdl"]["r"]=BOUNDS
    for mid,arena in ARENAS.items():
        for row in data[mid]["encount"]:
            row["mapid"]=arena
    return data


def audit(original,gm):
    result={}
    for mid in MAPS:
        world,events=gm.make(mid)
        if mid in (FIELD,HIDEOUT):
            assert world.hgt[53:77,35:89].max()==0
            result[mid]={"size":[world.w,world.d],"arena":True}
            continue
        prior=deepcopy(original.make(mid)[1].ev)
        for key,pos in POSITIONS.get(mid,{}).items():
            prior[key]["pos"]=pos
        if mid==CAVE:
            prior["#86#"]["mdl"]["r"]=BOUNDS
        assert prior==events.ev,mid
        grade=3 if mid==ROAD else 2
        origin=(90,21) if mid==ROAD else (46,9)
        walk=connected(world,gm,origin,grade)
        anchors=[]
        for key,event in events.ev.items():
            x,y,z,_=event.get("pos",(0,0,0,0))
            if y==grade+1 and (event["role"] in ("portal","itemchest") or event.get("mdlid")=="CE000"):
                assert (x,z) in walk,(mid,key,x,z)
                anchors.append(key)
        result[mid]={"size":[world.w,world.d],"reachable_events":anchors}
    return result


def stage(repo,profile):
    _,original,gm,_,_=variant(repo)
    result=audit(original,gm)
    gm.JOBDIR=str(profile/"tmp/rt_mapgen")
    catalog=profile/"project/data/map.json"
    live=repo/"_tools/rpgcobo-tool/project/data/map.json"
    existing=json.loads(catalog.read_bytes())
    candidate=revise_catalog(live.read_bytes())
    jobs=[]
    for mid in MAPS:
        world,_=gm.make(mid)
        job=world.write()
        job["out"]=f"tmp/rt_mapgen/{mid}_beiden_hideout_candidate.bw"
        jobs.append(job)
        existing[mid]=candidate[mid]
    compile_worlds(profile,jobs,stem="beiden-bandit-hideout")
    overwrite(catalog,json.dumps(existing,ensure_ascii=False,indent="\t").encode())
    for mid in MAPS:
        result[mid]["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"beiden-bandit-worlds.json").write_text(json.dumps(result,indent=2),"utf8")
    print({mid:len(row.get("reachable_events",())) for mid,row in result.items()})


if __name__=="__main__":
    stage(*(Path(a).resolve() for a in sys.argv[1:3]))
