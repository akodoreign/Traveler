"""Build the night ford, haunted marsh, heart clearing, and their arenas."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_kudo import MATS as RIVER, world_mesh
from export_coast import STAGE, export, voxel_asset
from kudo_worlds import MARSH, variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
ARENAS={"M862","M863","M864"}
HEART={"M358","M864"}
MATS={**RIVER,"marsh_mud":("kudo_marsh_mud.png",.91),"marsh_leaf":("kudo_marsh_leaf.png",.91),
      "marsh_track":("kudo_marsh_track.png",.94),"marsh_taint":("kudo_marsh_taint.png",.90),
      "swamp_water":("kudo_swamp00.png",.34),"blood_pit":("kudo_pit00.png",.42)}


def material():
    sample=np.asarray(periodic(Image.open(HERE/"surface_sources/kudo_marsh_silt.png").convert("RGB"),768))
    light=sample@[.24,.64,.12]
    grain=np.clip(light/max(1.,np.median(light)),.52,1.53)
    for key,tint in (("kudo_marsh_mud",(49,59,41)),("kudo_marsh_leaf",(51,83,44)),
                     ("kudo_marsh_track",(74,66,49)),("kudo_marsh_taint",(99,46,45))):
        rgb=np.asarray(tint)*grain[...,None]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{key}.png")
    for i in range(32):
        a=np.asarray(Image.open(STAGE/f"tex/kudo_river{i:02d}.png").convert("RGB"),dtype=float)
        l=a@[.24,.63,.13]
        motion=(l-np.median(l))/46.
        for term,base,bias in (("kudo_swamp",(28,67,55),(22,34,28)),("kudo_pit",(86,17,24),(48,17,18))):
            pulse=(1.+.15*np.cos(i*np.pi/16.)) if term=="kudo_pit" else 1.
            rgb=np.asarray(base)*pulse+motion[...,None]*bias
            Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{term}{i:02d}.png")


def make_layers(gm,world):
    heart=world.mid in HEART
    liquid=world.blk==(gm.EMBER if heart else gm.WATER)
    floor=world.blk.copy()
    hgt=world.hgt.copy()
    world.blk[liquid]=gm.T(3,None)
    world.hgt[liquid]=np.maximum(0,hgt[liquid]-1)
    terrain=world_mesh(gm,world,{gm.T(3,None):"marsh_mud",gm.TARSTAIN:"marsh_taint",
        gm.SL_GROUND:"marsh_mud",gm.DIRT:"marsh_track",gm.SAND:"river_silt",
        gm.GRASS3:"marsh_leaf",gm.GRASS:"marsh_leaf",gm.GRASS2:"marsh_leaf"})
    for face,key in zip(terrain.faces,terrain.materials,strict=True):
        if key not in ("marsh_leaf","marsh_taint","marsh_track","marsh_mud"):
            continue
        vertices=np.asarray([terrain.vertices[i] for i in face])
        x,z=np.floor(vertices[:,:2].mean(axis=0)*2).astype(int)
        if (np.ptp(vertices[:,2])<.0001 and 0<=x<world.w and 0<=z<world.d and not liquid[z,x]):
            for i in face:
                terrain.vertices[i]=terrain.vertices[i]+[0.,0.,.058]
    world.blk[:]=floor
    world.hgt[:]=hgt
    suffix="blood_pit" if heart else "swamp_water"
    _,water=grid_surfaces(np.where(liquid,1,0),hgt,("",suffix),wall_style="marsh_mud",fluid=1)
    return terrain,water,liquid


def dress(gm,m):
    props=[]
    lights=[]
    arena=m.mid in ARENAS

    def put(key,x,z,size=1.,yaw=0.,rise=0.,sway=None):
        bx,bz=(x,z) if arena else (x+gm.PAD_X,z+gm.PAD_BOTTOM)
        y=(int(m.hgt[bz,bx])+1)*.5+rise
        row=[key,bx*.5+.25,y,bz*.5+.25,size,yaw]
        if sway:
            row.append(sway)
        props.append(row)
        return row[1],row[2],row[3]

    if m.mid=="M355":
        for i,x in enumerate(range(15,54,2)):
            z=13+i%2
            put("kudo_ford_slab",x,z,1.03+(i%3)*.06,.32*((i%3)-1),-.21)
        for x,z in ((10,13),(14,17),(55,12),(59,14)):
            a,y,b=put("kudo_river_lantern",x,z,.82,0.)
            lights.append([a,y+.88,b,4.6,1.55])
        for x,z,turn in ((6,6,.31),(9,22,.89),(58,8,.95),(64,22,-.33)):
            put("kudo_sap_willow",x,z,1.08,turn)
    elif m.mid=="M356":
        put("kudo_marsh_barge",68,3,1.05,-.04,-.51,.014)
        put("kudo_sap_willow",30,25,1.20,.35)
        for x,z,s in ((12,8,1.23),(23,24,1.04),(39,8,.95),(47,25,1.29),
                      (55,24,1.05),(61,9,1.11),(77,7,.96),(83,25,1.18)):
            put("kudo_sap_willow",x,z,s,z*.17)
        for x,z in ((61,2),(62,4),(64,6),(69,7),(74,5),(77,3),(79,5),(70,8)):
            put("kudo_reed_bank",x,z,1.09,x*.36,0.,.09)
    elif m.mid=="M357":
        put("kudo_miya_casket",18,22,1.10,.32,-.29)
        for i,x in enumerate((14,24,30,35,42,48,53,60,68,75,81)):
            z=9+int(i%2==0)*2 if i%4!=0 else 24
            put("kudo_sap_willow",x,z,.91+(i%4)*.17,.34*i)
        for x,z in ((14,21),(17,23),(20,24),(23,21),(21,27),(27,26)):
            put("kudo_reed_bank",x,z,1.05,.4*x,0.,.082)
    elif m.mid=="M358":
        for i,x in enumerate(range(4,59,5)):
            for z in (3,27+(i%3)):
                put("kudo_sap_willow",x,z,.92+(i%4)*.16,i*.6)
        for x,z in ((24,15),(25,20),(29,22),(34,20),(35,15)):
            put("shadowlands_shards",x,z,.84,.57*x)
        put("kudo_miya_casket",29,17,.86,.31,-.15)
        for x,z,power in ((26,17,1.22),(32,17,1.31)):
            a,b=(x+gm.PAD_X)*.5+.25,(z+gm.PAD_BOTTOM)*.5+.25
            lights.append([a,2.52,b,4.1,power])
    else:
        for i,x in enumerate(range(7,126,11)):
            z=99+(i*7)%15
            put("kudo_sap_willow",x,z,.93+(i%4)*.17,.48*i)
        for i,x in enumerate(range(16,119,8)):
            z=83+(i*7)%6
            put("kudo_reed_bank",x,z,1.28,.22*i,0.,.077)
        if m.mid=="M862":
            for x,z in ((24,83),(49,90),(87,89),(108,82)):
                a,y,b=put("kudo_river_lantern",x,z,.90,0.)
                lights.append([a,y+.81,b,4.3,1.38])
        elif m.mid=="M864":
            for x,z in ((15,75),(26,77),(37,76)):
                put("shadowlands_shards",x,z,1.18,x*.35)
            lights.append([13.1,1.38,34.7,6.7,2.45])
    return props, lights


def main(repo):
    _,gm,_,_=variant(repo,marsh=True)
    import voxfile

    material()
    source={}
    for key,dimensions,samples in (
        ("kudo_marsh_barge",(5.20,1.85,1.21),45),
        ("kudo_sap_willow",(1.67,1.56,3.26),40),
        ("kudo_ford_slab",(1.14,.84,.28),33),
        ("kudo_miya_casket",(.36,.26,.21),32),
    ):
        tag,points,colors,pitch,src=convert_prop(key,dimensions,samples,lower=.025)
        if key=="kudo_sap_willow":
            rgb=colors.astype(float)
            canopy=(points[:,2]>.32*points[:,2].max()) & (rgb[:,1]>=.81*rgb[:,0])
            rgb[canopy]*=[.54,.73,.55]
            rgb[~canopy]*=[.75,.70,.64]
            colors=np.uint8(np.clip(rgb,0,255))
        source[key]=save(tag,points,colors,pitch,src,voxfile)
        voxel_asset(key)
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    report={}
    for mid in MARSH:
        m,events=gm.make(mid)
        terrain,water,mask=make_layers(gm,m)
        tag=f"{mid.lower()}_kudo_marsh"
        export(tag,terrain,MATS)
        export(tag+"_water",water,MATS)
        props,lights=dress(gm,m)
        cycle=3.52 if mid in HEART else 11.80
        prefix="kudo_pit" if mid in HEART else "kudo_swamp"
        index[mid]={"terrain":tag,"water":tag+"_water","placements":props,"poolLights":lights,
                    "waterSequence":{"prefix":prefix,"frames":32,"seconds":cycle}}
        report[mid]={"props":len(props),"surface_cells":int(mask.sum()),"pulse_seconds":cycle,
                     "events":len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"kudo-marsh-layout.json").write_text(json.dumps({"maps":report,"sources":source},
                                                         indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
