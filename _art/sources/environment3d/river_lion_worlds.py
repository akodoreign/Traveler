"""Compile the River of Gold and Lion branch maps into the review profile."""
from copy import deepcopy
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
ROADS=("M471","M472")
CAVES=("M482","M483","M484")
ARENA="M819"
MAPS=(*ROADS,*CAVES,ARENA)
ARENAS={"M482":"M829","M483":ARENA,"M484":ARENA}
POSITIONS={
    "M471":{"#3#":[76,4,29,0],"#6#":[79,4,28,2]},
    "M482":{"#1#":[46,3,8,2],"#84#":[46,3,4,2]},
    "M483":{"#1#":[46,3,8,2],"#83#":[46,3,4,2]},
    "M484":{"#1#":[46,3,8,2],"#83#":[46,3,4,2]},
}
PATCH="BRANCH_CAVE_POSITIONS = "+repr(POSITIONS)+"\n"+"BRANCH_CAVE_ARENAS = "+repr(ARENAS)+'''
_BRANCH_CAVE_PLANS = {
    "M482": (
        100,
        (((46,3),(46,12),(52,18),(62,22),(72,25),(79,27),(87,27),(95,30),(106,28),(114,26),(124,19),(126,15)),
         ((60,21),(55,27),(51,33),(56,41),(63,49),(66,62)),
         ((63,49),(53,54),(44,57),(36,62)),
         ((95,30),(90,38),(93,46),(100,48),(113,49),(122,52),(129,53)),
         ((93,44),(89,57)),((108,49),(109,41)),),
        ((51,15,13,8),(69,24,16,11),(100,29,19,12),(117,24,16,10),(125,16,8,7),
         (52,36,13,11),(61,54,13,13),(37,62,10,8),(92,50,15,14),(117,51,17,10)),
    ),
    "M483": (
        99,
        (((46,3),(46,13),(58,17),(72,16),(83,18),(92,19),(102,23),(112,24),(129,26),(145,37),(155,38),(171,47)),
         ((58,17),(54,27),(52,33),(57,43),(67,52)),((102,23),(94,30),(89,37)),
         ((145,37),(158,30),(165,24),(172,17))),
        ((52,15,13,9),(73,16,14,9),(97,22,15,11),(116,26,17,11),(52,36,12,13),
         (62,49,12,10),(92,37,13,11),(141,34,16,12),(158,43,16,10),(171,18,9,8)),
    ),
    "M484": (
        105,
        (((46,3),(46,12),(56,16),(77,16),(91,16),(109,22),(125,18),(138,13)),
         ((54,16),(55,29),(56,38),(51,49),(51,56),(45,61),(35,65)),
         ((56,38),(70,37),(87,40),(106,41),(120,36),(134,40),(154,36)),
         ((109,22),(109,30),(120,36)),((76,16),(87,24),(87,40))),
        ((49,15,13,9),(77,18,17,9),(111,23,16,11),(138,14,11,8),
         (58,38,14,12),(50,56,13,11),(35,65,10,8),(89,39,13,12),(120,40,20,11),(151,37,14,11)),
    ),
}


def branch_lion_cave_battle():
    return MapSpec("M819","Battle: the Lion hill caverns",128,128,base=CAVE_FLOOR,y=0)


MAPS["M819"]=BATTLE_SPECS["M819"]=branch_lion_cave_battle
RSET["M819"]="rt_hd2d_cave"
for _branch_cave,_branch_arena in BRANCH_CAVE_ARENAS.items():
    ENCOUNTERS[_branch_cave]=(_branch_arena,ENCOUNTERS[_branch_cave][1])


def rebuild_branch_caves(m, ev):
    for key,pos in BRANCH_CAVE_POSITIONS.get(m.mid,{}).items():
        ev.ev[key]["pos"]=list(pos)
    if m.mid=="M819":
        zz,xx=np.indices(m.hgt.shape)
        ridge=86.+2.4*np.sin(xx*.19)+2.*np.cos(xx*.21)
        stone=(zz>ridge)|(zz<29)
        lane=(zz>=56)&(zz<=75)
        m.hgt=np.where(stone,np.where(zz<29,1,8+np.rint(1.6*np.sin(xx*.17)).astype(int)),0).astype(np.int32)
        m.blk=np.where(stone,STONE,np.where(lane,DIRT,CAVE_FLOOR)).astype(np.int32)
        m.objs=[]
        return

    if m.mid in ("M471","M472"):
        zz,xx=np.indices(m.hgt.shape)
        river=m.mid=="M471"
        mouths=(76,) if river else (70,112)
        keep_road=m.blk==ROAD
        old_mounds=(m.hgt>3)&np.isin(m.blk,(T(2,0),T(2,1)))
        m.hgt[old_mounds]=3
        m.blk[old_mounds]=GRASS2 if river else GRASS
        m.objs=[]
        m.branch_mouths=[]
        if river:
            shore=8.1+1.6*np.sin(xx*.103)+.8*np.cos(xx*.166)
            # The south portal is on the dry causeway between the two reaches.
            reaches=((xx>=5)&(xx<=86)) | ((xx>=96)&(xx<=136))
            water=(zz<shore)&reaches&~keep_road
            bank=(zz<shore+4.)&reaches&~keep_road&~water
            m.blk[bank]=SAND
            m.blk[water]=WATER
            m.hgt[water]=1
            xx_lane=(abs(xx-91)<=4)&(zz<13)
            m.blk[xx_lane]=PLANK
        else:
            light_dry=(np.sin(xx*.10+zz*.18)+.7*np.sin(xx*.29-zz*.26))>.4
            m.blk[(m.blk==GRASS)&light_dry]=GRASS2
        protected=np.zeros(xx.shape,dtype=bool)
        for e in ev.ev.values():
            if e.get("role") in ("portal","itemchest") or (e.get("role")=="custom" and e.get("mdlid")=="CE000"):
                x,y,z,_=e["pos"]
                if y==4:
                    protected|=(xx-x)**2+(zz-z)**2<=7
        occupied=np.zeros_like(protected)
        for e in ev.ev.values():
            if e.get("pos") and e["pos"][1]==4:
                x,_,z,_=e["pos"]
                occupied|=(xx-x)**2+(zz-z)**2<=4
        # Raised woodland and ochre scarps break the back edge without
        # crossing the dry valley or either of the story-gated approaches.
        knolls=((24,44,17,10),(52,47,17,11),(129,49,17,9),(164,44,14,11))
        for x,z,rx,rz in knolls:
            shape=((xx-x)/rx)**2+((zz-z)/rz)**2
            hillside=(shape<1.)&(zz>=35)&~(keep_road|occupied|protected)&(abs(xx-91)>7)
            m.hgt[hillside]=np.maximum(m.hgt[hillside],6+np.rint((1.-shape[hillside])*5.4).astype(int))
            m.blk[hillside]=STONE
        for cx in mouths:
            body=((xx-cx)/14.6)**2+((zz-35.8)/9.)**2
            ridge=(body<1.)&(zz>=28)&(abs(xx-91)>5)&~keep_road
            throat=(abs(xx-cx)<=3)&(zz>=25)&(zz<=33)
            ridge &= ~(throat|protected)
            m.hgt[ridge]=np.maximum(7,12-np.floor(4.*body[ridge]).astype(int))
            m.blk[ridge]=STONE
            m.hgt[throat]=3
            m.blk[throat]=DIRT
            fill(m,cx-3,9,27,7,3,7,STONE)
            m.branch_mouths.append((cx,27,33))
        return

    width=m.w
    depth,lanes,galleries=_BRANCH_CAVE_PLANS[m.mid]
    zz,xx=np.indices((depth,width))
    path=np.zeros(xx.shape,dtype=bool)
    for line in lanes:
        path |= order_cave_route(xx,zz,line,3.5)
    floors=path.copy()
    for x,z,rx,rz in galleries:
        ripple=.056*np.sin(xx*.53+zz*.32)+.036*np.cos(xx*.74-zz*.63)
        floors |= ((xx-x)/rx)**2+((zz-z)/rz)**2 < 1.+ripple
    anchors=np.zeros_like(path)
    for event in ev.ev.values():
        if event.get("role") in ("portal","custom","itemchest") and "pos" in event:
            x,y,z,_=event["pos"]
            if y==3:
                anchors|=(xx-x)**2+(zz-z)**2<=9
    floors |= anchors
    floors[:8,:] &= abs(xx[:8]-46)<=3
    ridge=9+np.rint(1.3*np.sin(xx*.14+zz*.23)+1.3*np.cos(xx*.19-zz*.12)).astype(int)
    ridge=np.where(zz<20,5,ridge)
    m.d=depth
    m.blk=np.where(floors,CAVE_FLOOR,STONE).astype(np.int32)
    m.blk[path&floors]=DIRT
    m.hgt=np.where(floors,2,ridge).astype(np.int32)
    m.objs=[]
    m.walls=[]
    fill(m,43,8,2,7,2,6,STONE)
    if m.mid=="M482":
        channel=82.3+2.8*np.sin(zz*.094)
        ribbon=(abs(xx-channel)<2.25+.63*np.cos(zz*.21))&(zz>13)&(zz<57)
        cross=(abs(zz-27)<=2)&(xx>=75)&(xx<=91)&floors
        wet=ribbon&~cross&~anchors
        m.blk[wet]=WATER
        m.hgt[wet]=1
        bridge=(abs(zz-27)<=2)&(xx>=76)&(xx<=88)&floors
        m.blk[bridge]=PLANK
        m.branch_bridge=(76,89,25,30)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_branch_caves",PATCH,uses_events=True)


def connected(m,gm,origin,grade):
    dry=(m.blk!=gm.WATER)&(m.hgt==grade)
    assert dry[origin[1],origin[0]],(m.mid,origin)
    found={origin}
    frontier=deque([origin])
    while frontier:
        x,z=frontier.popleft()
        for a,b in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            if 0<=a<m.w and 0<=b<m.d and dry[b,a] and (a,b) not in found:
                found.add((a,b))
                frontier.append((a,b))
    return found


def audit(m,ev,gm):
    report={"width":m.w,"depth":m.d,"water_tiles":int((m.blk==gm.WATER).sum())}
    if m.mid==ARENA:
        assert m.hgt[58:77,38:90].max()==0
        return report
    road=m.mid in ROADS
    floor=3 if road else 2
    live=connected(m,gm,(91,22) if road else (46,8),floor)
    checked=[]
    for key,e in ev.ev.items():
        x,y,z,_=e.get("pos",(0,0,0,0))
        if e["role"] in ("portal","itemchest") or (e["role"]=="custom" and e.get("mdlid")=="CE000"):
            if y==floor+1:
                assert (x,z) in live,(m.mid,key,x,z)
                checked.append(key)
    if m.mid=="M482":
        assert (81,27) in live and (96,28) in live
    return {**report,"connected_floor_cells":len(live),"reachable_events":checked}


def catalog_rows(raw):
    data=json.loads(raw)
    original=data.get(ARENA)
    if original is None:
        new=deepcopy(data["M829"])
        new.update(name="Battle: the Lion hill caverns",rsetid="rt_hd2d_cave",size=[128,64,128])
        data[ARENA]=new
    else:
        assert original["name"]=="Battle: the Lion hill caverns"
    for mid,entries in POSITIONS.items():
        for key,pos in entries.items():
            data[mid]["event"][key]["pos"]=pos
    for mid,target in ARENAS.items():
        for row in data[mid]["encount"]:
            row["mapid"]=target
    return data


def stage(repo,profile):
    _,old,gm,_,_=variant(repo)
    gm.JOBDIR=str(profile/"tmp/rt_mapgen")
    live=repo/"_tools/rpgcobo-tool/project/data/map.json"
    profile_catalog=profile/"project/data/map.json"
    target=json.loads(profile_catalog.read_bytes())
    catalog=catalog_rows(live.read_bytes())
    jobs=[]
    evidence={}
    for mid in MAPS:
        m,after=gm.make(mid)
        evidence[mid]=audit(m,after,gm)
        if mid!=ARENA:
            base,before=old.make(mid)
            expected=deepcopy(before.ev)
            for key,pos in POSITIONS.get(mid,{}).items():
                expected[key]["pos"]=pos
            assert expected==after.ev,mid
            evidence[mid]["original_depth"]=base.d
        job=m.write()
        job["out"]=f"tmp/rt_mapgen/{mid}_branch_caves_candidate.bw"
        jobs.append(job)
        target[mid]=catalog[mid]
    compile_worlds(profile,jobs,stem="river-lion-caves")
    overwrite(profile_catalog,json.dumps(target,ensure_ascii=False,indent="\t").encode())
    for mid in MAPS:
        evidence[mid]["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"river-lion-caves-worlds.json").write_text(json.dumps(evidence,indent=2),"utf8")
    print({mid:(row["depth"],len(row.get("reachable_events",()))) for mid,row in evidence.items()})


if __name__=="__main__":
    stage(*(Path(a).resolve() for a in sys.argv[1:3]))
