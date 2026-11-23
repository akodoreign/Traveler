"""Furnish the tribunal and Nihime's house with separate fitted interiors."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_kaiu_kit import world_mesh
from build_kudo_rooms import MATS as ROOM, frame
from export_coast import Geometry, STAGE, export, voxel_asset
from kudo_rooms_worlds import OJATARA_ROOMS, variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={
    **ROOM,
    "court_wood":("ojatara_court_wood.png",.91),
    "court_indigo":("ojatara_court_indigo.png",.88),
    "petal_mat":("ojatara_petal_mat.png",.94),
}


def surfaces():
    wood=Image.open(HERE/"surface_sources/kamen_temple_cypress.png").convert("RGB")
    straw=Image.open(HERE/"surface_sources/kudo_inn_mat.png").convert("RGB")
    for key,source,tint in (
        ("court_wood",wood,(85,62,52)),
        ("court_indigo",straw,(63,72,100)),
        ("petal_mat",straw,(160,135,86)),
    ):
        value=periodic(source,768)@[.25,.62,.13]
        grain=np.clip(value/max(1.,np.median(value)),.61,1.38)
        rgb=np.asarray(tint)*grain[...,None]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/ojatara_{key}.png")


def room(world,gm,mid):
    terrain=world_mesh(gm,world,{gm.PLANK:"court_wood",gm.STONEW:"warm_plaster"})
    floor=Geometry()
    if mid=="M370":
        for x in (4.62,8.61,12.61):
            box(floor,(x,9.95,1.056),(2.85,2.70,.071),"court_indigo",1.18)
        for x in (3.82,7.64,11.48):
            frame(floor,(x,13.43,1.21),2.08,1.71,"kaiu_shoji")
        box(floor,(2.75,8.40,1.08),(1.90,.18,1.74),"court_wood")
        for x,y,h in ((2.91,1.39,.25),(3.35,1.45,.46),(3.89,1.36,.32),(4.33,1.48,.43)):
            box(floor,(x,8.268,y),(.223,.038,h),"kaiu_shoji")
    else:
        for x in (4.41,6.38,8.35,10.32):
            box(floor,(x,8.42,1.056),(1.89,2.66,.061),"petal_mat",1.40)
        for x in (3.55,6.0,8.45):
            frame(floor,(x,12.43,1.28),1.94,1.49,"kaiu_shoji")
    export(f"{mid.lower()}_ojatara_shell",terrain,MATS)
    export(f"{mid.lower()}_ojatara_trim",floor,MATS)


def layout(mid):
    props=[[f"{mid.lower()}_ojatara_trim",0.,0.,0.,1.,0.]]
    lights=[]

    def place(key,x,z,scale=1.,angle=0.,y=1.057):
        props.append([key,x,y,z,scale,angle])

    def lamp(x,z):
        place("kamen_temple_andon",x,z,.92)
        lights.append([x,1.71,z,4.95,1.63])

    if mid=="M370":
        for x,z,scale in ((5.94,10.52,.91),(10.02,10.88,1.11),(14.10,10.50,.92)):
            place("ojatara_tribunal_seat",x,z,scale)
            place("ojatara_court_ledger",x+.27,z-.12,.80,.08,1.51)
        place("hoshi_inn_bench",12.20,6.55,1.03,.09)
        place("hoshi_case_bundle",3.32,7.63,.89,.11)
        for x,z in ((2.97,6.25),(5.72,12.47),(10.0,12.40),(14.16,12.48),(16.52,6.36)):
            lamp(x,z)
    else:
        place("ojatara_nihime_screen",10.65,11.13,1.21,-.06)
        place("ojatara_nihime_screen",4.21,11.33,.87,.17)
        place("hoshi_tea_table",7.43,7.71,1.11)
        place("ojatara_incense_set",7.57,7.72,1.03,-.07,1.40)
        place("ojatara_flower_planter",3.05,8.81,.93,.13)
        place("kudo_carp_sake_rack",12.25,9.49,.82,1.56)
        for x,z in ((2.91,6.10),(7.67,11.66),(12.03,6.15)):
            lamp(x,z)
    return props,lights


def main(repo):
    _,gm,_,_=variant(repo,ojatara=True)
    import voxfile

    surfaces()
    sources={}
    for key,extent,size in (
        ("ojatara_tribunal_seat",(1.45,.76,.83),41),
        ("ojatara_nihime_screen",(1.85,.61,1.38),42),
        ("ojatara_incense_set",(.50,.30,.31),32),
        ("ojatara_court_ledger",(.39,.26,.21),34),
    ):
        sources[key]=save(*convert_prop(key,extent,size,lower=.02),voxfile)
        voxel_asset(key)
    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    for mid in OJATARA_ROOMS:
        world,_=gm.make(mid)
        room(world,gm,mid)
        props,lights=layout(mid)
        index[mid]={"terrain":f"{mid.lower()}_ojatara_shell","placements":props,"poolLights":lights}
    path.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"ojatara-interiors-layout.json").write_text(json.dumps({
        "maps":{mid:index[mid] for mid in OJATARA_ROOMS},"sources":sources,
    },indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
