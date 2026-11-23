"""Lay out the Phoenix trail, fox cave, and their themed battle grounds."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

from kensu_worlds import with_world_patch
from river_lion_worlds import connected
from shadowlands_march_worlds import compile_worlds, overwrite

HERE=Path(__file__).resolve().parent
ROAD,CAVE,FOREST,SHRINE="M475","M487","M846","M799"
MAPS=(ROAD,CAVE,FOREST,SHRINE)
ARENAS={ROAD:FOREST,CAVE:SHRINE}
POSITIONS={ROAD:{"#3#":[70,4,29,0],"#6#":[73,4,28,2]},
           CAVE:{"#1#":[46,3,9,2],"#83#":[46,3,4,2]}}
EXIT_BOUNDS=[0,1.,0,1.55,1.64,.75]
PATCH=f"FOX_POSITIONS = {POSITIONS!r}\nFOX_EXIT_BOUNDS = {EXIT_BOUNDS!r}\n"+'''

def phoenix_fox_shrine_arena():
    return MapSpec("M799","Battle: the fox shrine cave",128,128,base=CAVE_FLOOR,y=0)


MAPS["M799"]=phoenix_fox_shrine_arena
BATTLE_SPECS["M799"]=phoenix_fox_shrine_arena
RSET["M799"]="rt_hd2d_cave"
for _fox_route,_fox_arena in (("M475","M846"),("M487","M799")):
    ENCOUNTERS[_fox_route]=(_fox_arena,ENCOUNTERS[_fox_route][1])


def rebuild_phoenix_fox_cave(m,ev):
    for key,pos in FOX_POSITIONS.get(m.mid,{}).items():
        ev.ev[key]["pos"]=list(pos)
    if m.mid=="M487":
        ev.ev["#83#"]["mdl"]["r"]=FOX_EXIT_BOUNDS
    if m.mid=="M475":
        zz,xx=np.indices(m.hgt.shape)
        exclude=np.zeros_like(m.hgt,dtype=bool)
        for event in ev.ev.values():
            x,y,z,_=event.get("pos",(0,0,0,0))
            if y==4:
                exclude|=(xx-x)**2+(zz-z)**2<9
        m.objs=[o for o in m.objs if not (o["t"]=="fb" and o["fbtype"] in (20,21))]
        underway=(abs(xx-91)<=6)&(zz>=19)
        original=m.blk==ROAD
        path_to_cave=(abs(xx-70)<=3)&(zz>=17)&(zz<=34)
        keep=exclude|original|underway|path_to_cave
        m.hgt[underway|path_to_cave]=3
        m.blk[underway]=ROAD
        m.blk[path_to_cave]=DIRT
        for x,z,rx,rz,h in ((35,42,22,13,5),(66,39,16,10,6),(115,46,14,9,5),(160,44,18,13,6),(18,9,14,8,4)):
            rise=((xx-x)/rx)**2+((zz-z)/rz)**2+.06*np.sin(xx*.28+zz*.53)
            selection=(rise<1.)&~keep
            m.blk[selection]=STONE
            m.hgt[selection]=np.maximum(m.hgt[selection],6+np.rint(h*(1.-rise[selection])).astype(int))
        fill(m,67,9,27,7,3,7,STONE)
        return

    if m.mid in ("M846","M799"):
        zz,xx=np.indices(m.hgt.shape)
        forest=m.mid=="M846"
        toes=86+5*np.sin(xx*.082)+3*np.cos(xx*.24)
        rocks=(zz>toes) if not forest else ((zz>toes-7)&((xx<26)|(xx>99)))|(zz>=108)
        cliff=5+np.rint(3.2*np.cos(xx*.14+zz*.22)+1.3*np.sin(zz*.19)).astype(int)
        m.hgt=np.where(rocks,cliff,0)
        m.blk=np.where(rocks,STONE,np.where(zz>80,GRASS3 if forest else CAVE_FLOOR,DIRT))
        m.objs=[]
        return

    m.d=102
    zz,xx=np.indices((m.d,m.w))
    paths=(
        ((46,3),(46,13),(53,19),(66,22),(77,23),(86,28),(99,30),(113,24),(127,23),
         (139,13)),
        ((62,22),(54,30),(53,34),(56,43),(66,52)),
        ((79,24),(82,34),(86,40),(97,47),(109,54),(109,66)),
        ((98,30),(112,39),(118,45),(133,47),(150,48),(160,48)),
    )
    lanes=np.zeros(xx.shape,dtype=bool)
    for route in paths:
        lanes|=order_cave_route(xx,zz,route,3.7)
    walk=lanes.copy()
    for x,z,rx,rz in ((51,16,15,9),(75,24,18,11),(54,35,12,11),(64,51,11,9),
                     (92,39,16,14),(110,58,14,13),(117,25,16,12),(140,14,13,9),
                     (132,47,18,13),(156,48,16,10)):
        rim=.062*np.sin(xx*.37+zz*.49)+.044*np.cos(xx*.72-zz*.62)
        walk|=((xx-x)/rx)**2+((zz-z)/rz)**2<1.+rim
    protect=np.zeros_like(walk)
    for event in ev.ev.values():
        x,y,z,_=event.get("pos",(0,0,0,0))
        if y==3 and event["role"] in ("portal","custom","itemchest"):
            protect|=(xx-x)**2+(zz-z)**2<=9
    walk|=protect
    walk[:8]&=abs(xx[:8]-46)<=3
    spring=np.zeros_like(walk)
    for x,z,rx,rz in ((74,35,8,5),(93,38,5,7),(104,61,3,8),(129,53,15,4)):
        spring|=((xx-x)/rx)**2+((zz-z)/rz)**2<1.
    water=spring&walk&~(lanes|protect)
    rock=9+np.rint(2.2*np.sin(xx*.12+zz*.19)+1.2*np.cos(zz*.23)).astype(int)
    m.blk=np.where(water,WATER,np.where(walk,np.where(lanes,DIRT,CAVE_FLOOR),STONE))
    m.hgt=np.where(water,1,np.where(walk,2,np.where(zz<22,6,rock)))
    m.objs=[]
    m.walls=[]
    fill(m,43,8,2,7,2,6,STONE)
'''


def variant(repo):
    return with_world_patch(repo,MAPS,"rebuild_phoenix_fox_cave",PATCH,uses_events=True)


def revise_catalog(raw):
    data=json.loads(raw)
    if SHRINE not in data:
        data[SHRINE]=deepcopy(data[FOREST])
        data[SHRINE].update(name="Battle: the fox shrine cave",rsetid="rt_hd2d_cave")
    else:
        assert data[SHRINE]["name"]=="Battle: the fox shrine cave"
    for mid,changes in POSITIONS.items():
        for key,pos in changes.items():
            data[mid]["event"][key]["pos"]=pos
    data[CAVE]["event"]["#83#"]["mdl"]["r"]=EXIT_BOUNDS
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
        anchors=[]
        if mid in POSITIONS:
            _,base=old.make(mid)
            expected=deepcopy(base.ev)
            for key,pos in POSITIONS[mid].items():
                expected[key]["pos"]=pos
            if mid==CAVE:
                expected["#83#"]["mdl"]["r"]=EXIT_BOUNDS
            assert expected==events.ev,mid
            grade=3 if mid==ROAD else 2
            origin=(91,20) if mid==ROAD else (46,9)
            seen=connected(world,gm,origin,grade)
            for key,event in events.ev.items():
                x,y,z,_=event.get("pos",(0,0,0,0))
                if event["role"] in ("portal","itemchest") or (event["role"]=="custom" and event.get("mdlid")=="CE000"):
                    if y==grade+1:
                        assert (x,z) in seen,(mid,key,x,z)
                        anchors.append(key)
            if mid==ROAD:
                assert all((91,z) in seen for z in range(3,54))
        else:
            assert world.hgt[53:77,35:89].max()==0
        report[mid]={"size":[world.w,world.d],"reachable_events":anchors}
        record=world.write()
        record["out"]=f"tmp/rt_mapgen/{mid}_phoenix_fox_candidate.bw"
        jobs.append(record)
        existing[mid]=candidate[mid]
    compile_worlds(profile,jobs,stem="phoenix-fox-cave")
    overwrite(destination,json.dumps(existing,ensure_ascii=False,indent="\t").encode())
    for mid in MAPS:
        report[mid]["sha256"]=sha256((profile/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()
    (HERE/"phoenix-fox-worlds.json").write_text(json.dumps(report,indent=2),"utf8")
    print({mid:len(entry["reachable_events"]) for mid,entry in report.items()})


if __name__=="__main__":
    stage(*(Path(value).resolve() for value in sys.argv[1:3]))
