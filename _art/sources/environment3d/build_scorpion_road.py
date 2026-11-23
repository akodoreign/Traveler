"""Build the Scorpion memorial, castle town, grove, and lower river frontage."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

from build_furnace import grid_surfaces
from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from scorpion_road_worlds import MAPS, variant
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={
    **KAIU,
    "bayushi_moss":("bayushi_moss.png",.93),
    "bayushi_road":("bayushi_road.png",.94),
    "bayushi_cedar":("bayushi_cedar.png",.92),
    "bayushi_lacquer":("bayushi_lacquer.png",.86),
    "bayushi_kawara":("bayushi_kawara.png",.86),
    "bayushi_block":("bayushi_block.png",.93),
    "shutai_mud":("shutai_mud.png",.92),
    "bayushi_pond":("bayushi_pond00.png",.34),
    "shutai_river":("shutai_river00.png",.34),
}


def materials():
    for key,source,tint in (
        ("bayushi_moss","bayushi_garden_moss",(29,69,42)),
        ("bayushi_road","scorpion_damp_gravel",(81,72,63)),
        ("bayushi_cedar","kaiu_cedar",(43,28,25)),
        ("bayushi_lacquer","bayushi_rain_dark_lacquer",(96,26,34)),
        ("bayushi_kawara","kawara_bluegrey",(34,43,59)),
        ("bayushi_block","kamen_old_flagstones",(67,67,75)),
        ("shutai_mud","ojatara_earth_v2",(66,47,33)),
    ):
        ref=Image.open(HERE/f"surface_sources/{source}.png").convert("RGB")
        measured=periodic(ref,768)@[.27,.58,.15]
        if key in ("bayushi_moss","bayushi_road","shutai_mud"):
            broad=np.asarray(Image.fromarray(np.uint8(measured)).filter(ImageFilter.GaussianBlur(18.)))
            rough=measured-broad
            grain=1+.094*np.clip(rough/max(1.,rough.std()),-2.6,2.6)
            grain+=.25*(broad/max(1.,np.median(broad))-1.)
        else:
            grain=np.clip(measured/max(1.,np.median(measured)),.59,1.41)
        rgb=np.asarray(tint)*(.18+.82*grain[...,None])
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{key}.png")
    for i in range(32):
        t=np.asarray(Image.open(STAGE/f"tex/kudo_river{i:02d}.png").convert("RGB"),dtype=float)
        tone=t@[.23,.66,.11]
        motion=(tone-np.median(tone))/50.
        for key,base,reflection in (
            ("bayushi_pond",(24,75,66),(18,41,29)),
            ("shutai_river",(37,78,77),(28,47,43)),
        ):
            rgb=np.asarray(base)+motion[...,None]*reflection
            Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{key}{i:02d}.png")


def structures():
    rail=Geometry()
    for x in (-1.0,1.0):
        for z in (-2.75,-1.45,0.,1.45,2.75):
            box(rail,(x-.09,z-.079,0.),(.18,.158,.81),"bayushi_lacquer")
            box(rail,(x-.12,z-.105,.81),(.24,.21,.096),"bayushi_cedar")
        for y in (.30,.64):
            box(rail,(x-.054,-2.82,y),(.108,5.64,.098),"bayushi_lacquer",1.17)
    for n in range(25):
        z=-2.89+n*.231
        box(rail,(-.98,z,.014),(1.96,.222,.058),"bayushi_cedar",1.37)
    export("bayushi_pond_bridge",rail,MATS)
    shop_board("bayushi_apothecary_board","BAYUSHI","APOTHECARY","#6e2332")
    shop_board("bayushi_outfitter_board","CASTLE","OUTFITTER","#612432")
    shop_board("bayushi_theatre_board","BAYUSHI","THEATRE","#7b2636")
    shop_board("shutai_inn_board","SHUTAI","INN","#514035")
    shop_board("shutai_megu_board","MEGU'S","SAKE HOUSE","#592c35")


def terrain(gm,world):
    liquid=world.blk==gm.WATER
    height=world.hgt.copy()
    bank=gm.T(4,4)
    world.blk[liquid]=bank
    world.hgt[liquid]=np.maximum(0,height[liquid]-1)
    style={
        gm.GRASS:"bayushi_moss",gm.GRASS2:"bayushi_moss",gm.GRASS3:"bayushi_moss",
        gm.ROAD:"bayushi_road",gm.DIRT:"shutai_mud",gm.STONE:"bayushi_block",
        gm.STONEW:"bayushi_block",gm.ROOF:"bayushi_kawara",gm.WOOD:"bayushi_cedar",
        gm.DARKWOOD:"bayushi_cedar",gm.PLANK:"bayushi_cedar",bank:"bayushi_block",
        gm.TORII:"bayushi_lacquer",
    }
    land=world_mesh(gm,world,style)
    for face,kind in zip(land.faces,land.materials,strict=True):
        if kind not in ("bayushi_moss","bayushi_road","shutai_mud"):
            continue
        verts=np.array([land.vertices[i] for i in face])
        if np.ptp(verts[:,2])<.0001:
            for i in face:
                land.vertices[i]=land.vertices[i]+[0.,0.,.052]
    world.blk[liquid]=gm.WATER
    world.hgt[:]=height
    water="bayushi_pond" if world.mid=="M345" else "shutai_river"
    if not liquid.any():
        return land,None,water
    _,surface=grid_surfaces(liquid.astype(int),height,("",water),wall_style="bayushi_block",fluid=1)
    return land,surface,water


def layout(gm,world):
    mid=world.mid
    props=[]
    lights=[]
    doors=[]
    fish=[]

    def put(asset,x,z,size=1.,yaw=0.,rise=0.,wind=None):
        bx,bz=(x,z) if mid=="M861" else (x+gm.PAD_X,z+gm.PAD_BOTTOM)
        y=(int(world.hgt[bz,bx])+1)*.5+rise
        row=[asset,bx*.5+.25,y,bz*.5+.25,size,yaw]
        if wind:
            row.append(wind)
        props.append(row)
        return row[1:4]

    def lamp(x,z,size=1.):
        bx,y,bz=put("bayushi_scarlet_lantern",x,z,size)
        lights.append([bx,y+.95*size,bz,4.8,1.54])

    def door(x,z,event=None):
        px,pz=(x+gm.PAD_X)*.5,(z+gm.PAD_BOTTOM)*.5-.118
        if event is None:
            props.extend([["kudo_shut_door",px,2.5,pz,1.,0.],
                          ["town_door_stoop_half",px,2.,pz,1.,0.]])
        else:
            doors.append({"x":px,"y":2.5,"z":pz,"grade":2.,"event":event,"stoop":"town_door_stoop_half"})

    if mid=="M345":
        props.append(["bayushi_pond_bridge",21.,2.,13.,1.,0.])
        for x,z,a in ((9,19,.05),(11,24,.34),(18,25,-.17),(22,18,.49),(24,24,.88)):
            put("bayushi_water_lilies",x,z,.80+.07*(x%3),a,.089,.027)
        fish=[
            ["bayushi_pond_koi",18.23,1.56,12.78,.85,.78,1.46,.62,.10],
            ["bayushi_pond_koi",18.60,1.54,13.33,.65,.63,1.44,.48,2.90],
            ["bayushi_pond_koi",24.40,1.55,13.20,1.0,1.09,1.77,.52,4.30],
        ]
        put("scorpion_memorial_stele",33,18,1.05,.10)
        put("bayushi_pond_basin",27,22,1.02,.25)
        put("bayushi_shrine_lattice",38,27,1.12,.04)
        for x,z in ((4,15),(28,18),(30,12),(44,14),(70,17),(72,26),(7,31),(47,31)):
            put("coast_pine",x,z,.93+.12*(x%4),.24*x)
        for x,z in ((12,11),(26,11),(42,11),(58,11),(70,11),(32,25),(40,25)):
            lamp(x,z,.87)
        for x,z in ((6,19),(6,25),(27,18),(27,24),(30,23),(41,27)):
            put("coast_flowers",x,z,.95,.12*x,0.,.059)
    elif mid=="M347":
        for x in (4,16,29,46,59,78,96):
            lamp(x,20,.93)
        for x,z in ((25,8),(55,5),(77,7),(97,5)):
            put("coast_pine",x,z,1.04,.13*x)
        put("bayushi_household_well",40,10,1.05,.09)
        put("bayushi_shrine_lattice",88,23,.85,.05)
        for key,x in (("outfitter",20),("apothecary",36),("theatre",51)):
            put(f"bayushi_{key}_board",x,21,.86)
        for x,event in ((24,94),(39,95),(72,96)):
            door(x,23,event)
        for x in (9,55):
            door(x,23)
        put("kamen_street_gateway",50,17,.74)
    elif mid=="M348":
        rng=np.random.default_rng(348)
        for x in range(17,89,4):
            for z in (23,30):
                put("scorpion_grove_cedar_v2",x+int(rng.integers(-1,2)),z-int(rng.integers(0,3)),
                    float(rng.uniform(.80,1.16)),float(rng.uniform(0.,math.tau)))
        for x in range(21,78,5):
            put("scorpion_grove_cedar_v2",x,6+(x%4),.64+.04*(x%6),.37*x)
            put("wind_grass",x-1,9+(x%2),.80,.11*x,0.,.058)
        for x,z in ((12,13),(78,18),(89,13)):
            lamp(x,z,.78)
    elif mid=="M349":
        for x in (13,29,44,63,80,97):
            lamp(x,20,.80)
        put("shutai_inn_board",21,21,.88)
        put("shutai_megu_board",72,21,.88)
        put("bayushi_household_well",60,13,.90,.07)
        for x,z in ((15,11),(32,10),(66,12),(91,10)):
            put("shutai_willow_cart",x,z,.88,.08*(x%5))
        for x,z in ((22,23),(36,22),(68,23),(72,22),(84,26)):
            put("scorpion_shutai_sake_store",x,z,.87,.10*(x%5))
        for x in (9,24,39,54,69,84):
            door(x,23)
        for x,s in ((7,.87),(25,.87),(58,1.03),(83,.96),(99,.83)):
            put("kudo_cargo_boat",x,4,s,math.pi/2,-.21)
        for x in range(3,103,5):
            put("kudo_reed_bank",x,7,.88,.17*x,0.,.056)
    else:
        for i,x in enumerate(range(5,125,6)):
            put("scorpion_grove_cedar_v2",x,94+(i*3)%13,.98+.09*(i%4),.32*i)
        for x in (17,46,81,110):
            lamp(x,84,.78)
    return props,lights,doors,fish


def main(repo):
    _,_,gm,_,_=variant(repo)
    import voxfile

    materials()
    structures()
    sources={}
    for key,dims,samples in (
        ("scorpion_memorial_stele",(1.78,.93,2.11),47),
        ("scorpion_grove_cedar_v2",(2.59,2.24,5.28),50),
        ("scorpion_shutai_sake_store",(1.45,.83,1.21),42),
        ("bayushi_household_well",(1.54,1.45,2.01),43),
        ("bayushi_scarlet_lantern",(.43,.38,1.35),41),
        ("shutai_willow_cart",(1.77,.94,1.04),44),
        ("bayushi_shrine_lattice",(1.21,.72,1.71),42),
        ("bayushi_pond_koi",(.69,.32,.18),34),
        ("bayushi_water_lilies",(.74,.55,.26),35),
        ("bayushi_pond_basin",(1.02,.90,1.17),42),
    ):
        label,points,colors,pitch,source=convert_prop(key,dims,samples,lower=.02)
        if key=="scorpion_grove_cedar_v2":
            rgb=colors.astype(float)
            needles=(points[:,2]>.24*points[:,2].max()) & (rgb[:,1]>.87*rgb[:,0])
            rgb[needles]*=[.56,.76,.60]
            rgb[~needles]*=[.69,.62,.56]
            colors=np.uint8(np.clip(rgb,0,255))
        sources[key]=save(label,points,colors,pitch,source,voxfile)
        voxel_asset(key)
    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    reports={}
    for mid in MAPS:
        m,events=gm.make(mid)
        land,surface,fluid=terrain(gm,m)
        key=f"{mid.lower()}_scorpion"
        export(key,land,MATS)
        props,lights,doors,fish=layout(gm,m)
        row={"terrain":key,"placements":props,"poolLights":lights,"doors":doors}
        if surface is not None:
            export(key+"_water",surface,MATS)
            row["water"]=key+"_water"
            row["waterSequence"]={"prefix":fluid,"frames":32,"seconds":12.40 if mid=="M345" else 9.20}
        if fish:
            row["pondFish"]=fish
        index[mid]=row
        reports[mid]={"events":len(events.ev) if events else 0,"props":len(props),"koi":len(fish)}
    path.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"scorpion-road-layout.json").write_text(json.dumps({"maps":reports,"sources":sources},indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
