"""Build the gate courtyard, forge shop and two Shadowlands combat backdrops."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as WALL_MATS, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from shinomen_gate_worlds import variant
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={
    **WALL_MATS, "waste_earth":("waste_earth.png",.96),
    "waste_ash":("waste_ash.png",.96), "waste_shale":("waste_shale.png",.96),
    "waste_trail":("waste_trail.png",.94), "blackpitch":("shadowlands_blackpitch.png",.55),
    "iron":("furnace_basalt.png",.83), "ember":("waste_taint.png",.75),
}


def gate_joinery():
    gate=Geometry()
    for side in (-1,1):
        x=side*1.56
        box(gate,(x-.17,-.49,0),(.34,.77,.56),"kaiu_stone")
        box(gate,(x-.13,-.31,.36),(.26,.49,3.90),"kaiu_wood",1.7)
        box(gate,(x-.154,-.322,.19),(.308,.513,.23),"iron")
        # Swing the leaves against the side walls, open along the passage.
        gate_x=x-.043 if side>0 else x+.043
        box(gate,(gate_x-.07,.24,.0),(.14,1.56,2.90),"kaiu_redwood",1.99)
        for y in (.37,1.40,2.51):
            box(gate,(gate_x-.080,.19,y),(.16,1.65,.10),"iron")
        for z in (.22,.75,1.23,1.73):
            box(gate,(gate_x-.081,z,.14),(.16,.035,2.68),"kaiu_wood")
    box(gate,(-1.94,-.44,3.89),(3.88,.68,.37),"kaiu_wood")
    box(gate,(-1.81,-.53,4.18),(3.62,.84,.09),"kaiu_roof")
    box(gate,(-1.78,-.43,4.26),(3.56,.44,.27),"kaiu_stone")
    for x,z in ((-1.56,.5),(.89,3.0)):
        box(gate,(x-.13,z-.17,.35),(.29,.34,.20),"kaiu_wood")
    for side in (-1,1):
        x=-2.15 if side<0 else 1.80
        for i in range(3):
            box(gate,(x-i*.08,-.45-i*.22,i*.27),(.42,.67,.25),"kaiu_stone")
    export("shinomen_gate_open_joinery",gate,MATS)


def forge_shell():
    room=Geometry()
    for index in range(29):
        x=2.30+index*.428
        middle=7.2+(index%6)*.31
        for z,limit in ((3.55,middle),(middle+.014,12.75)):
            box(room,(x,z,1.016),(.414,limit-z,.046),"kaiu_wood",1.65)
    for x in (1.94,14.80):
        box(room,(x,3.27,1.047),(.45,9.60,2.18),"kaiu_plaster",2.30)
    box(room,(1.96,12.68,1.04),(13.24,.52,2.29),"kaiu_plaster",2.22)
    for x in (2.1,4.65,7.3,9.9,12.45,14.91):
        box(room,(x,12.59,1.07),(.19,.29,2.27),"kaiu_wood")
    for rise in (1.15,2.20,3.23):
        box(room,(2.03,12.50,rise),(12.92,.18,.11),"kaiu_wood")
        for x in (2.24,14.60):
            box(room,(x,3.4,rise),(.19,9.23,.11),"kaiu_wood")
    for x,width in ((2.24,5.20),(9.63,5.15)):
        box(room,(x,3.26,1.05),(width,.43,.34),"kaiu_stone")
        box(room,(x,3.24,1.383),(width,.45,.086),"kaiu_wood")
    box(room,(7.55,3.24,1.022),(1.97,1.36,.084),"kaiu_stone")
    for x in (3.98,11.88):
        box(room,(x,12.58,2.26),(1.91,.16,.83),"kaiu_wood")
        box(room,(x+.10,12.485,2.36),(1.71,.071,.62),"kaiu_shoji")
        for ix in range(1,7):
            box(room,(x+.10+.245*ix,12.43,2.32),(.035,.082,.70),"kaiu_wood")
    export("shinomen_smith_room",room,MATS)

    hearth=Geometry()
    box(hearth,(-1.03,-.65,.01),(2.06,1.30,.38),"kaiu_stone")
    for x in (-.97,.67):
        box(hearth,(x,-.61,.38),(.30,1.22,.27),"kaiu_stone")
    box(hearth,(-.67,.36,.38),(1.34,.25,.26),"kaiu_stone")
    box(hearth,(-.64,-.48,.39),(1.28,.86,.07),"ember")
    for lane in range(5):
        box(hearth,(-.61+lane*.27,-.42,.44),(.06,.73,.047),"iron")
    export("shinomen_raised_hearth",hearth,MATS)


def step_pad(placements,mid):
    if mid=="M991":
        return
    for obj in placements:
        if obj[0] in ("shadowlands_oni_bones","shadowlands_burnt_stump","shadowlands_shards","shadowlands_thorns"):
            # The engine's active battle lineup normally sits near z=34–39.
            # Large, non-colliding scenic objects are arranged behind it.
            if mid=="M817" or mid=="M818":
                assert obj[3]>=40.


def main(repo):
    _, gm, _, _=variant(repo)
    import voxfile

    source={}
    for key,extent,count in (
        ("shinomen_watch_drum",(1.08,.88,.98),38),
        ("shinomen_smith_anvil",(.59,.55,.82),33),
        ("shinomen_covered_supplies",(1.18,.95,1.16),42),
        ("shadowlands_oni_bones",(1.62,1.14,.89),36),
        ("shadowlands_burnt_stump",(1.11,1.03,1.87),39),
    ):
        source[key]=save(*convert_prop(key,extent,count,lower=.022),voxfile)
        voxel_asset(key)
    raw=np.asarray(periodic(Image.open(HERE/"surface_sources/shadowlands_blackpitch.png").convert("RGB"),768))
    value=raw@[.24,.64,.12]
    tone=np.clip( .57 + .46*value/max(1.,np.median(value)), .64,1.33)
    rgb=np.asarray((35,31,42))*tone[...,None]
    Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/"tex/shadowlands_blackpitch.png")
    gate_joinery()
    forge_shell()
    shop_board("shinomen_forge_sign","KAIU","SMITH","#263748")

    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    for mid in ("M457","M817","M818"):
        world,_=gm.make(mid)
        terrain=f"{mid.lower()}_shinomen"
        if mid=="M457":
            shell=world_mesh(gm,world)
        else:
            shell=world_mesh(gm,world,{
                gm.SL_GROUND:"waste_earth",gm.SL_ASH:"waste_ash",gm.TAR:"blackpitch",gm.ROAD:"waste_trail"})
            shell.materials=["waste_shale" if name=="cliff" else name for name in shell.materials]
        export(terrain,shell,MATS)
        props=[]

        def place(key,x,z,scale=1.,yaw=0.,height=None):
            y=(int(world.hgt[z,x])+1)*.5 if height is None else height
            props.append([key,x*.5+.25,y,z*.5+.25,scale,yaw])

        lights=[]
        watchfires=[]

        def beacon(x,z,size):
            place("watchtower_signal",x,z,size,.24+(x%7)*.09)
            wx,y,wz=props[-1][1:4]
            watchfires.append([wx,y+size*.93,wz,size*.71])
            lights.append([wx,y+size*1.38,wz,4.7,1.66])

        if mid=="M457":
            for x,z,size in ((32,19,.67),(72,19,.65),(90,19,.67),(77,32,.58),(85,32,.58)):
                beacon(x,z,size)
            place("shinomen_gate_open_joinery",81,34,1.,0.,1.50)
            place("shinomen_watch_drum",76,31,1.16,-.21)
            place("shinomen_watch_drum",87,32,.93,.19)
            for x,z,size in ((35,19,.94),(39,19,1.03),(56,20,1.05),(58,19,.76),(92,27,1.0)):
                place("shinomen_covered_supplies",x,z,size,.11*(x%4)-.19)
            place("shinomen_smith_anvil",42,19,1.10,-.26)
            place("shinomen_forge_sign",43,20,.86,.01)
            for x,z in ((78,35),(83,40)):
                place("hoshi_andon",x,z,.73,.0,2.05)
                lights.append([x*.5+.25,2.69,z*.5+.25,4.6,2.45])
        elif mid=="M817":
            for x,z,s,angle in ((19,88,1.02,.31),(40,84,.85,-.24),(54,91,1.09,.56),
                                (71,87,1.42,-.25),(91,87,1.02,.65),(113,89,1.17,.23)):
                place("shadowlands_burnt_stump",x,z,s,angle)
            for x,z,s in ((16,82,1.1),(26,87,.97),(37,81,.88),(79,90,1.06),(95,81,.95),(109,82,1.13)):
                place("shadowlands_oni_bones",x,z,s,(x%5)*.9)
            for x,z in ((10,86),(32,91),(50,93),(67,90),(86,92),(103,91),(119,88)):
                place("shadowlands_shards",x,z,1.02,(x%4)*.58)
        else:
            for x,z,s in ((20,88,.63),(50,91,.55),(79,90,.59),(112,88,.64)):
                beacon(x,z,s)
            for x,z,s in ((16,85,.88),(37,84,1.02),(72,87,1.02),(91,86,.87),(103,85,.98)):
                place("shinomen_covered_supplies",x,z,s,.4-(x%6)*.12)
            place("shinomen_watch_drum",44,90,1.2,-.22)
            place("shinomen_watch_drum",96,89,.99,.22)
        step_pad(props,mid)
        index[mid]={"terrain":terrain,"placements":props,"watchfires":watchfires,"poolLights":lights}
        if mid=="M457":
            index[mid]["doors"]=[
                {"event":79,"x":19.5,"y":2.0,"z":10.882,"stoop":"town_door_stoop_half","grade":1.5},
                {"event":None,"x":29.0,"y":2.0,"z":10.882,"stoop":"town_door_stoop_half","grade":1.5},
            ]

    props=[
        ["hoshi_goods_counter",8.46,1.085,6.48,1.04,0.],
        ["shinomen_raised_hearth",11.57,1.075,11.32,1.,0.],
        ["shinomen_smith_anvil",10.82,1.075,9.31,1.3,-.30],
        ["shinomen_covered_supplies",4.38,1.074,11.07,1.08,.12],
        ["shinomen_covered_supplies",12.91,1.075,10.75,.92,-.11],
        ["hoshi_arms_display",6.45,1.074,11.73,1.08,0.],
        ["hoshi_arms_bundle",6.50,2.26,11.72,1.,.08],
        ["hoshi_storage_jar",13.39,1.074,8.65,1.12,.27],
        ["hoshi_andon",3.20,1.076,8.15,.98,0.],
        ["hoshi_andon",8.16,1.076,11.79,.87,0.],
    ]
    index["M991"]={"terrain":"shinomen_smith_room","placements":props,
                   "watchfires":[[11.57,1.60,11.32,.78]],
                   "poolLights":[[11.57,2.1,11.32,5.3,1.8],[3.20,1.47,8.15,4.4,1.2]]}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    report={"maps":{mid:index[mid] for mid in ("M457","M817","M818","M991")},"sources":source}
    (HERE/"shinomen-gate-layout.json").write_text(json.dumps(report,indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
