"""Build the storehouse's architecture and all its visible storage furnishings."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE=Path(__file__).resolve().parent
TEX=STAGE/"tex"
MATS={
    "board":("storehouse_board.png",.94),
    "frame":("storehouse_frame.png",.91),
    "earth":("storehouse_earth.png",.96),
    "stone":("door_stoop.png",.96),
    "iron":("door_iron.png",.79),
    "glow":("andon_paper.png",.92),
}


def surfaces():
    for source,key,tint in (("town_door_cedar","storehouse_board",(111,75,48)),
                            ("kaiu_cedar","storehouse_frame",(64,45,33)),
                            ("kaiu_plaster","storehouse_earth",(162,140,112)),
                            ("hoshi_paper_lantern","andon_paper",(231,164,75))):
        im=Image.open(HERE/"surface_sources"/f"{source}.png").convert("RGB")
        rgb=periodic(im,512)
        lum=rgb@[.24,.64,.12]
        detail=np.clip((lum-np.median(lum))/max(2.,np.percentile(lum,92)-np.percentile(lum,8)),-.70,.70)
        result=np.array(tint)*(1+detail[...,None]*(.31 if key=="andon_paper" else .59))
        Image.fromarray(np.uint8(result.clip(0,255))).save(TEX/f"{key}.png")


def room(ox,oz):
    g=Geometry()
    def block(x,z,y,w,d,h,material,repeat=.85):
        box(g,(ox+x,oz+z,y),(w,d,h),material,repeat)

    # Raised longitudinal floorboards, floor sill and stone entry apron.
    for i in range(35):
        x=.51+i*.312
        for z, depth in ((.52,2.20),(2.727,2.46),(5.195,2.78)):
            block(x,z,1.021,.304,depth,.062,"board",1.35)
    block(4.97,.49,1.013,2.04,1.02,.078,"stone",1.47)
    block(.44,.49,.929,11.10,.12,.12,"frame",1.36)
    # Earthen infill on timber footings and full-height posts.
    block(-.07,7.91,1.02,12.13,.65,2.58,"earth",1.74)
    for x in (-.061,11.44):
        block(x,-.05,1.02,.62,8.56,2.58,"earth",1.74)
    for x in (.12,2.31,4.64,7.29,9.64,11.61):
        block(x,7.76,1.05,.19,.25,2.66,"frame",1.28)
    block(.10,7.76,1.18,11.74,.26,.20,"frame",1.45)
    block(.10,7.75,3.49,11.74,.29,.22,"frame",1.45)
    for x in (.39,11.39):
        for z in (.34,2.63,5.12,7.74):
            block(x,z,1.06,.21,.21,2.63,"frame",1.28)
        block(x,.29,3.49,.23,7.49,.21,"frame",1.29)
        block(x,.29,1.18,.23,7.49,.13,"frame",1.29)
    # High slatted vents read as woodworking appropriate to a storage room.
    for x in (2.58,8.02):
        block(x,7.735,2.95,1.56,.08,.41,"frame",1.15)
        for offset in (.12,.33,.54,.75,.96,1.17,1.38):
            block(x+offset,7.658,2.99,.055,.11,.33,"board",.52)
    # The two front wall fragments afford a clear cutaway and keep the door readable.
    for x,w in ((.49,4.48),(7.01,4.52)):
        block(x,-.023,1.004,w,.53,.48,"earth",1.9)
        block(x,-.045,1.435,w,.55,.09,"frame",1.24)
    export("hoshi_storehouse_room",g,MATS)


def furnishings():
    rack=Geometry()
    for x in (-1.06,1.06):
        for z in (-.32,.32):
            box(rack,(x-.064,z-.06,0),(.13,.125,1.88),"frame",.75)
    for h in (.13,.77,1.43):
        for i in range(4):
            box(rack,(-1.13,-.37+i*.179,h),(2.26,.17,.086),"board",.98)
        box(rack,(-1.13,.27,h+.076),(2.26,.087,.096),"frame",1.0)
    export("hoshi_storehouse_rack",rack,MATS)

    andon=Geometry()
    for h,w in ((0.,.39),(.047,.33),(.52,.38),(.556,.31)):
        box(andon,(-w/2,-w/2,h),(w,w,.044),"frame",.42)
    for x in (-.15,.129):
        for z in (-.15,.129):
            box(andon,(x,z,.078),(.027,.027,.47),"frame",.34)
    for x in (-.145,.135):
        box(andon,(x,-.135,.126),(.009,.275,.388),"glow",.42)
    for z in (-.145,.135):
        box(andon,(-.135,z,.126),(.275,.009,.388),"glow",.42)
        box(andon,(-.15,z,.29),(.30,.016,.018),"frame",.34)
    export("hoshi_andon",andon,MATS)

    crate=Geometry()
    box(crate,(-.50,-.30,0),(1.,.60,.13),"frame",.73)
    for z in (-.30,.26):
        for y in (.13,.258,.386):
            box(crate,(-.50,z,y),(1.,.043,.123),"board",.89)
    for x in (-.50,.46):
        box(crate,(x,-.256,.13),(.043,.512,.385),"board",.78)
    for x in (-.44,.37):
        box(crate,(x,-.324,.11),(.069,.022,.39),"frame",.83)
    box(crate,(-.072,-.334,.34),(.144,.035,.15),"iron",.51)
    export("hoshi_storehouse_chest",crate,MATS)
    lid=Geometry()
    for x in (-.50,-.335,-.17,-.005,.16,.325):
        box(lid,(x,-.60,0),(.158,.60,.081),"board",.83)
    for x in (-.42,.36):
        box(lid,(x,-.605,.069),(.066,.609,.037),"frame",.82)
    export("hoshi_storehouse_lid",lid,MATS)


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    import voxfile
    sources=[]
    for name,size,samples in (("hoshi_storage_jar",(.49,.48,.73),33),
                              ("hoshi_rice_bale",(.91,.56,.53),33)):
        key,points,colors,pitch,reference=convert_prop(name,size,samples)
        if key=="hoshi_rice_bale":
            # The reconstructed straw rests one layer above the captured white plane.
            keep=points[:,2]>0
            points,colors=points[keep],colors[keep]
            points-=points.min(axis=0)
            pitch=np.asarray(size)/(points.max(axis=0)+1)
        sources.append(save(key,points,colors,pitch,reference,voxfile))
        voxel_asset(name)
    surfaces()
    furnishings()
    mid="M125"
    m,events=gm.make(mid)
    ox,oz=(coordinate*.5 for coordinate in gm.ROOM_OFS[mid])
    room(ox,oz)
    placements=[]
    def prop(key,x,z,y=1.081,scale=1.,yaw=0.):
        placements.append([key,ox+x,y,oz+z,scale,yaw])

    for x,z in ((2.05,7.12),(9.13,7.13)):
        prop("hoshi_storehouse_rack",x,z)
        for offset,scale in ((-.67,.83),(0,.75),(.68,.91)):
            prop("hoshi_storage_jar",x+offset,z,1.92,scale,offset)
        for offset in (-.66,.44):
            prop("hoshi_rice_bale",x+offset,z,1.31,.83,.18)
    for x,z,s in ((2.07,3.4,1.02),(2.70,3.92,.91),(2.17,4.43,1.0),
                  (9.54,3.2,1.03),(9.58,3.89,.98),(9.52,4.54,.86)):
        prop("hoshi_rice_bale",x,z,scale=s,yaw=.10+x*.16)
    for x,z,s in ((9.02,5.74,1.14),(9.63,5.95,1.03),(9.68,6.44,.81),(1.21,5.68,1.07)):
        prop("hoshi_storage_jar",x,z,scale=s,yaw=.15)
    lights=[]
    for x,z,s in ((1.06,1.66,1.0),(10.84,2.3,1.0),(6.87,7.36,.93)):
        prop("hoshi_andon",x,z,scale=s)
        lights.append([ox+x,1.40,oz+z,3.8,1.6])
    treasure=events.ev["#2#"]["pos"]
    x,y,z=(v*.5 for v in treasure[:3])
    placements.append(["hoshi_storehouse_chest",x,y+.082,z,1.,0.])
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    index[mid]=dict(terrain="hoshi_storehouse_room",placements=placements,poolLights=lights,
                    chests=[dict(event=2,x=x,y=y+.594,z=z+.30)])
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"hoshi-storehouse-layout.json").write_text(json.dumps({"room":[m.w,m.d],"origin":[ox,oz],
        "placed_props":len(placements),"lanterns":len(lights),"sources":sources},indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
