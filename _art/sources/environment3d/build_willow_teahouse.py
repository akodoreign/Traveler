"""Build the Willow teahouse for Norie's private scene."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_kaiu_kit import world_mesh
from build_kudo_rooms import MATS as ROOM, frame
from export_coast import Geometry, STAGE, export, voxel_asset
from kudo_rooms_worlds import variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={**ROOM,"willow_red":("willow_red.png",.86),"willow_tatami":("willow_tatami.png",.91)}


def main(repo):
    _,gm,_,_=variant(repo,group="willow")
    import voxfile

    for label,source,tint in (
        ("willow_red","bayushi_rain_dark_lacquer",(81,25,37)),
        ("willow_tatami","kudo_inn_mat",(116,92,56)),
    ):
        image=Image.open(HERE/f"surface_sources/{source}.png").convert("RGB")
        value=periodic(image,768)@[.27,.59,.14]
        grain=np.clip(value/max(1.,np.median(value)),.57,1.43)
        rgb=np.asarray(tint)*(.22+.78*grain[...,None])
        Image.fromarray(np.uint8(rgb)).save(STAGE/f"tex/{label}.png")

    world,_=gm.make("M346")
    shell=world_mesh(gm,world,{gm.PLANK:"kaiu_wood",gm.STONEW:"warm_plaster"})
    trim=Geometry()
    for x in (4.86,6.68,8.50):
        box(trim,(x,7.39,1.056),(1.75,3.05,.067),"willow_tatami",1.39)
    for x in (3.82,9.85):
        frame(trim,(x,11.97,1.14),2.05,1.68,"kaiu_shoji")
    box(trim,(4.62,11.54,1.08),(5.8,.18,.14),"willow_red",1.37)
    for x in (4.65,10.19):
        box(trim,(x,11.51,1.12),(.13,.097,1.75),"willow_red")
    export("m346_willow_teahouse",shell,MATS)
    export("willow_tea_trim",trim,MATS)

    label="scorpion_willow_tea_service"
    source=save(*convert_prop(label,(.65,.46,.42),37,lower=.02),voxfile)
    voxel_asset(label)
    props=[
        ["willow_tea_trim",0.,0.,0.,1.,0.],
        ["hoshi_tea_table",7.48,1.093,7.39,1.17,.04],
        [label,7.49,1.435,7.43,.97,.09],
        ["ojatara_nihime_screen",7.39,1.062,11.89,.89,0.],
        ["kudo_carp_sake_rack",11.81,1.069,10.57,.81,1.54],
    ]
    lights=[]
    for x,z in ((2.87,6.25),(7.43,10.77),(12.04,6.21)):
        props.append(["kamen_temple_andon",x,1.067,z,.94,0.])
        lights.append([x,1.72,z,4.84,1.66])
    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    index["M346"]={"terrain":"m346_willow_teahouse","placements":props,"poolLights":lights}
    path.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"willow-teahouse-layout.json").write_text(
        json.dumps({"map":index["M346"],"source":source},indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
