"""Build the River of Gold road and Kudo's working waterfront."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={
    **KAIU, "river_silt":("kudo_silt.png",.92), "road_clay":("kudo_road.png",.92),
    "rice_leaf":("kudo_rice.png",.91), "kudo_river":("kudo_river00.png",.29),
    "kudo_meadow":("kudo_meadow.png",.94),
    "quarantine_cloth":("kudo_quarantine.png",.88),
    "kudo_timber":("kudo_timber.png",.93), "kudo_kawara":("kudo_kawara.png",.87),
}


def surfaces():
    material=Image.open(HERE/"surface_sources/kudo_river_silt.png").convert("RGB")
    grain=np.asarray(periodic(material,768))@[.24,.64,.12]
    grain=np.clip(grain/max(1.,np.median(grain)),.54,1.48)
    for key,tint in (("kudo_silt",(75,66,51)),("kudo_quarantine",(165,105,27))):
        image=np.asarray(tint)*(.22+.78*grain[...,None])
        Image.fromarray(np.uint8(np.clip(image,0,255))).save(STAGE/f"tex/{key}.png")
    for key,scan,tint in (("kudo_meadow","kensu_meadow_scan",(49,81,46)),
                         ("kudo_rice","kensu_meadow_scan",(39,75,44)),
                         ("kudo_road","ojatara_earth_v2",(109,78,53))):
        field=Image.open(HERE/f"surface_sources/{scan}.png").convert("RGB")
        light=periodic(field,768)@[.24,.64,.12]
        fibers=np.clip(light/max(1.,np.median(light)),.59,1.39)
        rgb=np.asarray(tint)*(.42+.58*fibers[...,None])
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{key}.png")
    for key,scan,tint in (("kudo_timber","kaiu_cedar",(59,42,32)),
                         ("kudo_kawara","kawara_bluegrey",(42,63,75))):
        source=Image.open(HERE/f"surface_sources/{scan}.png").convert("RGB")
        value=periodic(source,768)@[.24,.64,.12]
        variation=np.clip(value/max(1.,np.median(value)),.51,1.49)
        rgb=np.asarray(tint)*(.25+.75*variation[...,None])
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{key}.png")
    for i in range(32):
        source=np.asarray(Image.open(STAGE/f"tex/surf{i:02d}.png").convert("RGB"),dtype=float)
        light=source@[.22,.63,.15]
        relief=(light-np.median(light))/95.
        rgb=np.asarray([33,91,83])+relief[...,None]*[22,43,39]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/kudo_river{i:02d}.png")


def geometry():
    bridge=Geometry()
    for i in range(13):
        x=-1.50+i*.231
        box(bridge,(x,-1.483,.013),(.223,2.967,.062),"kaiu_wood",1.75)
    for side in (-1,1):
        z=side*1.35
        for x in (-1.44,-.53,.53,1.44):
            box(bridge,(x-.061,z-.07,.05),(.126,.143,.81),"kaiu_redwood")
            box(bridge,(x-.087,z-.092,.82),(.174,.184,.069),"kaiu_roof")
        for y in (.34,.67):
            box(bridge,(-1.50,z-.045,y),(3.00,.091,.088),"kaiu_redwood",1.43)
    export("kudo_district_bridge",bridge,MATS)
    counter=Geometry()
    for x in (-.89,.76):
        box(counter,(x,-.32,0),(.136,.64,.85),"kaiu_redwood")
    box(counter,(-.96,-.33,.12),(1.92,.65,.11),"kaiu_wood")
    box(counter,(-1.08,-.45,.82),(2.16,.90,.082),"kaiu_wood",1.23)
    box(counter,(-.96,-.46,.32),(1.92,.061,.44),"kaiu_plaster")
    export("kudo_fish_stall",counter,MATS)
    door=Geometry()
    box(door,(-.61,-.067,-.015),(1.22,.102,2.11),"kaiu_wood",1.43)
    for x in (-.56,-.27,.03,.32):
        box(door,(x,-.085,.029),(.033,.052,2.01),"kaiu_redwood")
    for y in (.10, .89, 1.92):
        box(door,(-.57,-.106,y),(1.15,.070,.082),"kaiu_redwood")
    box(door,(.27,-.156,.95),(.099,.071,.183),"kaiu_roof")
    export("kudo_shut_door",door,MATS)
    banner=Geometry()
    box(banner,(-.09,-.06,0),(.18,.12,2.61),"kaiu_wood")
    box(banner,(-.09,-.054,2.48),(.85,.117,.073),"kaiu_wood")
    for i in range(9):
        x=i*.078
        sway=.034*math.sin(i*.56)
        box(banner,(x,sway-.036,1.23-.021*math.cos(i*.47)),(.094,.035,1.22),"quarantine_cloth")
    export("kudo_quarantine_banner",banner,MATS)
    shop_board("kudo_dreaming_carp_sign","DREAMING","CARP","#334b4d")
    shop_board("kudo_mantis_guest_sign","MANTIS","GUEST","#29453f")


def main(repo):
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    import voxfile

    surfaces()
    geometry()
    sources={}
    for name,extent,resolution in (
        ("kudo_cargo_boat",(3.80,1.03,.81),44),
        ("kudo_reed_bank",(.65,.55,.74),25),
        ("kudo_eel_basket",(.42,.29,.52),32),
        ("kudo_river_lantern",(.38,.37,1.13),33),
    ):
        sources[name]=save(*convert_prop(name,extent,resolution,lower=.021),voxfile)
        voxel_asset(name)

    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    report={}
    for mid in ("M350","M351"):
        m,events=gm.make(mid)
        water=m.blk==gm.WATER
        stone=gm.T(3,None)
        m.blk[water]=stone
        m.hgt[water]-=1
        land=world_mesh(gm,m,{stone:"river_silt",gm.ROAD:"road_clay",
                             gm.GRASS:"kudo_meadow",gm.GRASS3:"rice_leaf",gm.GRASS2:"rice_leaf",
                             gm.WOOD:"kudo_timber",gm.DARKWOOD:"kudo_timber",gm.ROOF:"kudo_kawara"})
        for face,material in zip(land.faces,land.materials,strict=True):
            if material not in ("kudo_meadow","rice_leaf","road_clay"):
                continue
            vertices=np.asarray([land.vertices[i] for i in face])
            if np.ptp(vertices[:,2])<.0001:
                for i in face:
                    land.vertices[i]=land.vertices[i]+np.array((0.,0.,.064))
        m.hgt[water]+=1
        m.blk[water]=gm.WATER
        _,stream=grid_surfaces(np.where(water,1,0),m.hgt,("","kudo_river"),wall_style="river_silt",fluid=1)
        asset=f"{mid.lower()}_kudo"
        export(asset,land,MATS)
        export(asset+"_water",stream,MATS)
        props=[]
        def place(key,x,z,scale=1.,angle=0.,rise=0.,wind=None):
            bx,bz=x+gm.PAD_X,z+gm.PAD_BOTTOM
            y=(int(m.hgt[bz,bx])+1)*.5+rise
            row=[key,bx*.5+.25,y,bz*.5+.25,scale,angle]
            if wind:
                row.append(wind)
            props.append(row)

        if mid=="M350":
            for x in range(3,109,5):
                for j in ((0,1) if x%3 else (0,)):
                    place("kudo_reed_bank",x+j,8+j,.67+(x%4)*.14,x*.32,.01,.085)
            for x,z,s in ((21,26,.84),(43,22,.92),(74,25,1.11),(98,23,.98)):
                place("coast_pine",x,z,s,x*.31)
            for x,z,s in ((13,11,.78),(38,10,.84),(57,10,.83),(82,10,.92),(105,9,.88)):
                place("kudo_river_lantern",x,z,s,.0)
            place("kudo_cargo_boat",51,6,.85,.05,-.32)
            place("kudo_cargo_boat",85,6,.75,-.13,-.34)
            doors=[]
        else:
            for x,z,turn,size in ((4,3,math.pi/2,.83),(4,24,math.pi/2,1.07),(4,36,math.pi/2,.94)):
                place("kudo_cargo_boat",x,z,size,turn,-.35)
            for x,z,s in ((6,6,.77),(8,31,.81),(7,30,.72),(8,7,.81),(11,27,1.12),(10,5,.98)):
                place("kudo_eel_basket",x,z,s,z*.31)
            for x,z in ((4,5),(8,28),(13,19),(23,19),(41,20),(51,17),(57,17),
                        (64,19),(76,20),(92,20),(103,20)):
                place("kudo_river_lantern",x,z,.95+(x%3)*.09)
            for x,z,s in ((60,7,.84),(66,3,1.03),(80,4,1.12),(88,8,.88),(101,5,1.14),
                          (106,32,1.03),(102,42,.88),(79,41,.86),(64,42,1.04),(90,44,1.02)):
                place("coast_pine",x,z,s,(x%6)*.34)
            for x,z in ((9,2),(9,3),(9,20),(9,24),(9,35),(10,38),(51,8),(56,9),(51,24),(56,28),
                        (52,38),(56,39),(50,42),(55,46)):
                place("kudo_reed_bank",x,z,.94+(x%4)*.07,x*.42,0.,.078)
            place("kudo_fish_stall",22,10,.91)
            place("kudo_eel_basket",21,10,.76,.09,.82)
            place("kudo_eel_basket",23,10,.61,-.13,.80)
            props.append(["kudo_district_bridge",40.0,2.5,10.5,1.,0.])
            place("kudo_dreaming_carp_sign",89,20,.87)
            place("kudo_mantis_guest_sign",44,20,.88)
            place("kudo_quarantine_banner",31,21,1.02,.04,0.,.03)
            doors=[]
            for local_x,event in ((20,None),(34,None),(46,3),(68,2),(85,4),(99,None)):
                x=(gm.PAD_X+local_x)*.5
                z=(gm.PAD_BOTTOM+(23 if local_x==99 else 22))*.5-.118
                if event is None:
                    props.append(["kudo_shut_door",x,2.50,z,1.,0.])
                    props.append(["town_door_stoop_half",x,2.,z,1.,0.])
                else:
                    doors.append({"x":x,"y":2.5,"z":z,"grade":2.0,"event":event,
                                  "stoop":"town_door_stoop_half"})
        index[mid]={"terrain":asset,"water":asset+"_water","placements":props,"doors":doors,
                    "waterSequence":{"prefix":"kudo_river","frames":32,"seconds":9.20}}
        report[mid]={"placements":len(props),"water_cells":int(water.sum()),"events":len(events.ev)}
    path.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"kudo-river-layout.json").write_text(json.dumps({
        "maps":report,"sources":sources,
    },indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
