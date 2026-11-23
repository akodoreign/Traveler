"""Build a cedar and shoji tea room with original storage and tea furnishings."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageOps

from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE=Path(__file__).resolve().parent
TEX=STAGE/"tex"
MATS={
    "cedar":("storehouse_board.png",.91),
    "rail":("tea_rail.png",.88),
    "paper":("tea_shoji.png",.94),
    "stone":("door_stoop.png",.96),
    "mat":("tea_tatami.png",.94),
    "hem":("tea_hem.png",.92),
    "cushion":("tea_cushion.png",.94),
    "lacquer":("tea_lacquer.png",.40),
    "coal":("tea_coal.png",.96),
    "scroll":("tea_scroll.png",.94),
}


def materials():
    for source,name,tint,contrast in (
        ("hoshi_tatami","tea_tatami",(138,131,79),.73),
        ("hoshi_tatami","tea_hem",(51,67,61),.41),
        ("hoshi_tatami","tea_cushion",(95,45,43),.48),
        ("hoshi_paper_lantern","tea_shoji",(202,189,155),.34),
        ("town_door_cedar","tea_rail",(72,45,30),.61),
        ("town_door_iron","tea_lacquer",(43,31,29),.49),
        ("furnace_ash","tea_coal",(32,25,25),.77),
    ):
        img=Image.open(HERE/"surface_sources"/f"{source}.png").convert("RGB")
        scan=periodic(img,512)
        value=scan@[.22,.66,.12]
        detail=np.clip((value-np.median(value))/max(1.,np.ptp(np.percentile(value,[9,92]))),-.63,.63)
        rgb=np.asarray(tint)*(1.+detail[...,None]*contrast)
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(TEX/f"{name}.png")
    scroll=Image.open(HERE/"surface_sources/hoshi_tea_scroll.png").convert("RGB")
    ImageOps.fit(scroll,(360,680)).save(TEX/"tea_scroll.png")


def shell():
    g=Geometry()
    def part(x,z,h,w,d,height,mat,tile=.91):
        box(g,(x,z,h),(w,d,height),mat,tile)
    for i in range(46):
        x=2.49+i*.348
        for z,d in ((3.99,2.29),(6.29,2.67),(8.97,2.46),(11.44,2.94)):
            part(x,z,1.015,.34,d,.061,"cedar",1.60)
    part(7.52,3.97,1.027,4.44,1.64,.061,"stone",1.16)
    # Cedar frame, raised floor edge, and tall paneled walls.
    part(1.96,14.37,1.004,17.11,.69,2.63,"paper",2.8)
    for x in (1.95,18.44):
        part(x,3.44,1.014,.63,11.59,2.62,"paper",2.6)
    for x in (2.32,4.37,6.39,8.40,10.42,12.44,14.46,16.48,18.50):
        part(x,14.22,1.061,.12,.255,2.67,"rail",.83)
    for y in (1.14,1.41,3.36,3.62):
        part(2.21,14.16,y,16.56,.28,.12,"rail",1.27)
    for panel in (2.48,4.50,6.52,10.56,12.58,14.60,16.62):
        for column in range(1,6):
            part(panel+column*.29,14.191,1.48,.025,.06,1.81,"cedar",.54)
        for n in range(1,4):
            part(panel,14.17,1.45+n*.465,1.80,.061,.026,"cedar",.58)
    for x in (2.41,18.38):
        for z in (3.79,6.31,8.79,11.29,14.21):
            part(x,z,1.04,.215,.223,2.62,"rail",1.08)
        for y in (1.24,3.58):
            part(x,3.63,y,.24,10.87,.13,"rail",1.35)
    for x,w in ((2.45,5.17),(12.24,6.30)):
        part(x,3.45,1.00,w,.63,.41,"paper",1.54)
        part(x,3.43,1.381,w,.65,.106,"rail",1.0)
    # A shallow display alcove centers the return wall.
    part(8.45,13.70,1.09,2.01,.60,.17,"rail",.83)
    part(8.70,14.06,1.34,1.53,.12,1.91,"rail",.80)
    front=14.045
    corners=[(8.91,front,1.53),(10.01,front,1.53),(10.01,front,3.14),(8.91,front,3.14)]
    g.quad(corners,[(0,0),(1,0),(1,1),(0,1)],"scroll")
    part(8.88,14.01,1.495,1.16,.068,.057,"cedar",.70)
    export("hoshi_teahouse_room",g,MATS)


def props():
    mat=Geometry()
    box(mat,(-.48,-.92,0),(.96,1.84,.045),"mat",.74)
    for x in (-.48,.431):
        box(mat,(x,-.92,.042),(.049,1.84,.012),"hem",.74)
    export("hoshi_tea_mat",mat,MATS)

    cushion=Geometry()
    for x,z,w,d,y,h in ((-.32,-.29,.64,.58,0.,.048),(-.30,-.27,.60,.54,.042,.055),
                       (-.28,-.25,.56,.50,.089,.022)):
        box(cushion,(x,z,y),(w,d,h),"cushion",.69)
    export("hoshi_tea_cushion",cushion,MATS)

    table=Geometry()
    for x in (-.82,.73):
        for z in (-.37,.27):
            box(table,(x,z,0),(.11,.11,.36),"rail",.68)
    box(table,(-.89,-.43,.352),(1.78,.86,.087),"cedar",.92)
    for z in (-.45,.42):
        box(table,(-.92,z,.354),(1.84,.032,.082),"lacquer",.88)
    box(table,(-.34,-.28,.44),(.72,.50,.028),"lacquer",.71)
    for x in (-.35,.353):
        box(table,(x,-.29,.458),(.027,.52,.034),"rail",.72)
    export("hoshi_tea_table",table,MATS)

    irori=Geometry()
    box(irori,(-.80,-.60,0),(1.60,1.20,.083),"stone",.71)
    for x in (-.82,.66):
        box(irori,(x,-.62,.084),(.16,1.24,.13),"rail",.74)
    for z in (-.62,.47):
        box(irori,(-.67,z,.084),(1.34,.15,.124),"rail",.74)
    box(irori,(-.66,-.46,.085),(1.32,.93,.055),"coal",.73)
    for x,z,w in ((-.41,-.25,.24),(-.18,.17,.32),(.15,-.18,.42),(.18,.23,.27)):
        box(irori,(x,z,.139),(w,.11,.088),"coal",.47)
    export("hoshi_tea_irori",irori,MATS)


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import voxfile
    sources=[]
    for name,size,resolution in (("hoshi_tea_bowl",(.272,.261,.145),24),
                                  ("hoshi_tea_kettle",(.53,.47,.35),29)):
        sources.append(save(*convert_prop(name,size,resolution),voxfile))
        voxel_asset(name)
    materials()
    shell()
    props()
    details=[]
    for center in (5.14,14.3):
        for k in range(4):
            for z in (7.08,8.99,10.90):
                details.append(["hoshi_tea_mat",center-1.52+k*1.02,1.077,z,1.,0.])
        details.append(["hoshi_tea_table",center,1.133,8.63,1.,0.])
        for x,z,d in ((-.52,7.83,.03),(.54,9.39,.14)):
            details.append(["hoshi_tea_cushion",center+x,1.135,z,1.,d])
        for x,z,scale in ((-.55,8.55,.94),(.17,8.82,1.),(.59,8.62,.87)):
            details.append(["hoshi_tea_bowl",center+x,1.574,z,scale,.19+x*.23])
    details.append(["hoshi_tea_irori",15.38,1.087,12.19,1.,0.])
    details.append(["hoshi_tea_kettle",15.28,1.28,12.15,1.19,.35])
    lights=[]
    for x,z in ((3.10,4.79),(17.67,6.13),(11.29,13.88)):
        details.append(["hoshi_andon",x,1.083,z,1.0,0.])
        lights.append([x,1.39,z,4.1,1.7])
    lights.append([15.4,1.46,12.19,2.8,.96])
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    index["M123"]=dict(terrain="hoshi_teahouse_room",placements=details,poolLights=lights)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"hoshi-teahouse-layout.json").write_text(json.dumps({"room":[42,38],
        "furnishings":len(details),"sources":sources,"fit":"M123 original gameplay events 1–3"},indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
