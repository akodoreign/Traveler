"""Furnish the Fox governor's hall, Mantis office, and Dreaming Carp."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_kudo import MATS as RIVER
from export_coast import Geometry, STAGE, export, voxel_asset
from kudo_room_map_section import KUDO_ROOM_LAYOUTS
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={**RIVER, "woven_mat":("kudo_mat.png",.87), "fox_green":("kudo_fox.png",.89),
      "mantis_ink":("kudo_mantis.png",.91), "warm_plaster":("kudo_plaster.png",.90)}


def materials():
    sample=np.asarray(periodic(Image.open(HERE/"surface_sources/kudo_inn_mat.png").convert("RGB"),768))
    grain=sample@[.26,.61,.13]
    grain=np.clip(grain/max(1.,np.median(grain)),.49,1.51)
    for name,tint in (("kudo_mat",(128,100,54)),("kudo_fox",(43,86,58)),
                     ("kudo_mantis",(34,65,97)),("kudo_plaster",(170,148,120))):
        rgb=np.asarray(tint)*grain[...,None]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/{name}.png")


def frame(surface,origin,width,height,finish):
    x,z,y=origin
    box(surface,(x,z,y),(width,.066,height),"kaiu_wood")
    box(surface,(x+.06,z-.034,y+.060),(width-.12,.047,height-.12),finish,.96)
    for i in range(1,5):
        box(surface,(x+i*width/5,z-.040,y+.06),(.027,.051,height-.12),"kaiu_wood")
    for off in (.34,.67):
        box(surface,(x+.057,z-.049,y+height*off),(width-.117,.05,.026),"kaiu_wood")


def shell(mid):
    left,right,front,back,entry,_=KUDO_ROOM_LAYOUTS[mid]
    x0,x1,z0,z1=left*.5+.17,(right+1)*.5-.17,front*.5+.19,(back+1)*.5-.27
    room=Geometry()
    accent={"M352":"fox_green","M353":"mantis_ink","M354":"warm_plaster"}[mid]
    for x in np.arange(x0,x1,.451):
        box(room,(x,z0,1.011),(min(.44,x1-x),z1-z0,.054),"kaiu_wood",1.56)
    for x in (x0-.24,x1-.02):
        box(room,(x,z0-.21,1.04),(.26,z1-z0+.27,2.15),accent,1.55)
    box(room,(x0-.14,z1-.019,1.033),(x1-x0+.30,.290,2.18),"warm_plaster",1.2)
    for x in np.linspace(x0+.11,x1-.25,9):
        box(room,(x,z1-.111,1.055),(.123,.148,2.158),"kaiu_wood",1.03)
    for y in (1.08,2.11,3.18):
        box(room,(x0,z1-.16,y),(x1-x0,.16,.083),"kaiu_redwood")
        for x in (x0-.071,x1-.10):
            box(room,(x,z0,y),(.098,z1-z0,.091),"kaiu_wood")
    ex=(entry+.5)*.5
    for lo,hi in ((x0,ex-.64),(ex+.65,x1)):
        if hi>lo:
            box(room,(lo,z0-.20,1.04),(hi-lo,.33,.37),"kaiu_redwood")
    box(room,(ex-.68,z0-.237,1.015),(1.36,.85,.085),"kaiu_stone")
    for x in (ex-.64,ex+.55):
        box(room,(x,z0-.235,1.05),(.113,.191,2.10),"kaiu_wood")
    box(room,(ex-.65,z0-.237,3.06),(1.30,.215,.10),"kaiu_wood")
    for x in (x0+1.42, (x0+x1)*.5-.82, x1-3.04):
        frame(room,(x,z1-.19,2.19),1.62,.76,"kaiu_shoji")
    if mid=="M352":
        for x in (5.13,7.26,9.39):
            box(room,(x,10.17,1.058),(2.07,2.55,.060),"woven_mat",1.32)
        for x in (3.68,9.57,12.15):
            frame(room,(x,12.36,1.16),1.37,.93,accent)
    elif mid=="M353":
        for x in (2.55,4.75,6.95):
            box(room,(x,10.46,1.058),(2.13,2.33,.062),accent,1.24)
        frame(room,(9.17,11.91,1.057),2.26,1.79,"kaiu_shoji")
    else:
        for x in (8.84,10.80,12.76):
            box(room,(x,10.12,1.058),(1.91,2.69,.062),"woven_mat",1.29)
        frame(room,(8.92,10.11,1.071),2.02,1.43,"kaiu_shoji")
        frame(room,(11.87,10.24,1.072),1.86,1.48,"kaiu_shoji")
    export(f"{mid.lower()}_kudo_interior",room,MATS)


def main(repo):
    sys.path.insert(0,str(repo/"tools"))
    import voxfile

    materials()
    sources={}
    for name,dimensions,samples in (
        ("kudo_fox_pillar",(.44,.42,2.19),38),
        ("kudo_mantis_chart_desk",(1.59,.91,.79),43),
        ("kudo_carp_sake_rack",(1.64,.64,1.57),42),
        ("kudo_bamboo_food_cover",(.49,.41,.34),31),
    ):
        sources[name]=save(*convert_prop(name,dimensions,samples,lower=.025),voxfile)
        voxel_asset(name)
    props={
        "M352":[
            ["kudo_fox_pillar",4.27,1.075,10.38,.90,.03],
            ["kudo_fox_pillar",6.72,1.075,11.09,1.03,-.03],
            ["kudo_fox_pillar",10.93,1.075,11.08,1.03,.01],
            ["kudo_fox_pillar",13.49,1.075,10.34,.96,-.04],
            ["hoshi_tea_table",8.11,1.114,9.58,1.13,.0],
            ["kudo_bamboo_food_cover",8.10,1.44,9.51,1.03,.10],
            ["hoshi_storage_jar",3.86,1.078,11.76,1.09,.23],
            ["hoshi_goods_rack",13.39,1.078,12.24,1.02,0.],
        ],
        "M353":[
            ["kudo_mantis_chart_desk",4.66,1.072,9.29,1.06,.01],
            ["hoshi_trade_chest",4.25,1.120,11.52,1.27,.17],
            ["hoshi_inn_bench",7.36,1.072,10.54,.93,0.],
            ["hoshi_goods_rack",12.91,1.074,12.17,.92,0.],
            ["hoshi_case_bundle",12.92,1.48,12.16,1.03,.11],
            ["hoshi_case_bundle",12.63,2.04,12.15,.99,-.09],
        ],
        "M354":[
            ["hoshi_goods_counter",5.26,1.071,7.62,1.09,0.],
            ["kudo_carp_sake_rack",4.10,1.071,12.18,1.12,.04],
            ["kudo_carp_sake_rack",6.86,1.071,12.19,.97,-.03],
            ["hoshi_tea_table",8.30,1.076,9.66,1.09,0.],
            ["kudo_bamboo_food_cover",8.23,1.403,9.66,.99,0.],
            ["hoshi_inn_bedding",11.32,1.125,11.63,.83,0.],
            ["hoshi_inn_bedding",13.37,1.125,11.42,.83,0.],
        ],
    }
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    for mid in KUDO_ROOM_LAYOUTS:
        shell(mid)
        nodes=props[mid]
        lights=[]
        for x,z in ((2.82,6.81),(7.45,11.88),(13.66,7.51)):
            nodes.append(["hoshi_andon",x,1.072,z,.95,.01])
            lights.append([x,1.51,z,4.45,1.28])
        index[mid]={"terrain":f"{mid.lower()}_kudo_interior","placements":nodes,"poolLights":lights}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"kudo-interiors-layout.json").write_text(json.dumps({
        "maps":{mid:index[mid] for mid in KUDO_ROOM_LAYOUTS},"sources":sources,
    },indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
