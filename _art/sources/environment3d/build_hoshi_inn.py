"""Create the inn's reception hall, warm hearth and separate guest bays."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_hoshi_teahouse import MATS as TEA
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE=Path(__file__).resolve().parent
TEX=STAGE/"tex"
MATS={**TEA,"cotton":("inn_cotton.png",.95),"indigo":("inn_indigo.png",.92)}


def linens():
    im=Image.open(HERE/"surface_sources/hoshi_inn_bedding.png").convert("RGB")
    a=periodic(im,512)@[.24,.64,.12]
    rel=np.clip((a-np.median(a))/max(1.,np.ptp(np.percentile(a,[8,93]))),-.66,.66)
    for name,shade in (("inn_cotton",(201,186,155)),("inn_indigo",(58,80,108))):
        rgb=np.asarray(shade)*(1+rel[...,None]*.48)
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(TEX/f"{name}.png")


def architecture():
    shape=Geometry()
    def piece(x,z,y,w,d,h,mat,tile=1.0):
        box(shape,(x,z,y),(w,d,h),mat,tile)
    for i in range(47):
        x=2.51+i*.36
        for z,length in ((3.49,2.76),(6.26,2.64),(8.92,2.95),(11.89,3.54)):
            piece(x,z,1.015,.350,length,.062,"cedar",1.39)
    piece(8.43,3.47,1.026,5.06,1.82,.07,"stone",1.44)
    piece(1.95,15.39,1.01,18.10,.63,2.62,"paper",2.73)
    for x in (1.94,19.45):
        piece(x,2.96,1.01,.62,13.07,2.62,"paper",2.97)
    for x in np.arange(2.30,19.90,2.41):
        piece(x,15.21,1.062,.17,.25,2.67,"rail",1.06)
    for z in np.arange(3.4,15.6,2.42):
        for x in (2.40,19.36):
            piece(x,z,1.04,.21,.226,2.63,"rail",.91)
    for y in (1.21,3.57):
        piece(2.27,15.20,y,17.51,.26,.16,"rail",1.35)
        for x in (2.41,19.36):
            piece(x,3.36,y,.23,11.9,.15,"rail",1.31)
    for x,w in ((2.5,5.82),(13.52,5.89)):
        piece(x,2.96,1.0,w,.53,.43,"paper",1.51)
        piece(x,2.94,1.423,w,.56,.096,"rail",1.27)
    # Rear sleeping bays with half-screen walls. The walkway before them remains central.
    for x in (12.52,15.57):
        piece(x,12.53,1.08,.093,2.88,1.73,"paper",1.63)
        for z in np.linspace(12.58,15.34,7):
            piece(x-.028,z,1.09,.132,.035,1.70,"rail",.83)
        for y in (1.09,1.65,2.21,2.75):
            piece(x-.03,12.52,y,.15,2.90,.055,"rail",.82)
    # Low rear windows in the common room are above the benches.
    for x in (3.71,6.83,9.80):
        piece(x,15.18,2.41,1.53,.069,.73,"rail",1.02)
        piece(x+.055,15.12,2.46,1.42,.052,.626,"paper",1.12)
        for j in range(1,7):
            piece(x+.21*j,15.083,2.46,.019,.054,.623,"cedar",.46)
    export("hoshi_inn_room",shape,MATS)


def furniture():
    desk=Geometry()
    box(desk,(-1.08,-.38,.02),(2.16,.76,.78),"rail",1.0)
    for i in range(8):
        box(desk,(-1.05+i*.265,-.40,.087),(.253,.044,.60),"cedar",.84)
    box(desk,(-1.15,-.44,.787),(2.30,.85,.096),"cedar",1.12)
    box(desk,(-.84,-.07,.885),(.52,.31,.046),"lacquer",.67)
    for i in range(3):
        box(desk,(-.79,-.048+i*.021,.932),(.43,.246,.017),"cotton",.59)
    export("hoshi_inn_counter",desk,MATS)

    bedding=Geometry()
    for x,z,y,w,d,h,name in (
        (-.50,-1.07,0,1.,2.14,.033,"mat"),
        (-.445,-1.01,.035,.89,2.03,.045,"cotton"),
        (-.429,-.65,.082,.855,1.64,.047,"indigo"),
        (-.41,-.64,.126,.815,.155,.023,"cotton"),
        (-.295,-.96,.085,.59,.30,.069,"cotton"),
    ):
        box(bedding,(x,z,y),(w,d,h),name,.81)
    for z in np.linspace(-.40,.83,6):
        box(bedding,(-.420,z,.126),(.833,.013,.008),"rail",.81)
    export("hoshi_inn_bedding",bedding,MATS)

    bench=Geometry()
    for x in (-.71,.66):
        box(bench,(x,-.19,0),(.12,.40,.39),"rail",.68)
    for z in (-.24,-.08,.08):
        box(bench,(-.92,z,.366),(1.84,.15,.074),"cedar",.73)
    export("hoshi_inn_bench",bench,MATS)


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import voxfile
    source=save(*convert_prop("hoshi_travel_bundle",(.56,.41,.37),31,lower=.025),voxfile)
    voxel_asset("hoshi_travel_bundle")
    linens()
    architecture()
    furniture()
    details=[
        ["hoshi_inn_counter",5.72,1.082,7.46,1.,0.],
        ["hoshi_tea_irori",5.12,1.081,11.00,1.30,0.],
        ["hoshi_tea_kettle",5.19,1.316,10.88,1.23,.30],
        ["hoshi_inn_bench",5.06,1.081,10.00,1.,0.],
        ["hoshi_inn_bench",5.16,1.081,12.06,1.,math.pi],
        ["hoshi_inn_bench",3.91,1.081,11.02,.88,1.57],
        ["hoshi_travel_bundle",4.96,1.077,5.43,1.12,-.14],
        ["hoshi_travel_bundle",3.63,1.077,8.71,.82,.61],
        ["hoshi_storage_jar",3.44,1.082,13.10,1.05,.38],
        ["hoshi_storage_jar",3.90,1.082,13.28,.96,-.63],
    ]
    for x in (14.13,17.12):
        for dx,dz in ((-.49,-.94),(.49,-.94),(-.49,.95),(.49,.95)):
            details.append(["hoshi_tea_mat",x+dx,1.077,13.47+dz,1.,0.])
        details.append(["hoshi_inn_bedding",x,1.13,13.68,1.0,.0])
        details.append(["hoshi_travel_bundle",x+.88,1.129,12.45,.91,.1])
    lights=[]
    for x,z,size in ((3.06,4.60,.94),(8.57,12.83,1.),(11.27,14.66,.92),(18.83,11.91,.93)):
        details.append(["hoshi_andon",x,1.081,z,size,0.])
        lights.append([x,1.42,z,4.6,1.6])
    lights.append([5.12,1.46,11.,3.3,1.1])
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    index["M120"]=dict(terrain="hoshi_inn_room",placements=details,poolLights=lights)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"hoshi-inn-layout.json").write_text(json.dumps({"room":[44,40],
        "furnishings":len(details),"source":source},indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
