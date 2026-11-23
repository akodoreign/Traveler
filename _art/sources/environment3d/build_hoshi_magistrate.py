"""Build a magistrate's reception and shelves for Hoshi's case records."""

import json
from pathlib import Path
import sys

import numpy as np

from build_hoshi_stall import box
from build_hoshi_teahouse import MATS
from export_coast import Geometry, STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save

HERE = Path(__file__).resolve().parent


def shell():
    room = Geometry()
    for i in range(44):
        x = 2.512 + i*.385
        seam = 8.71 + ((i*3)%6)*.25
        for z, end in ((3.52,seam), (seam+.013,15.49)):
            box(room,(x,z,1.017),(.373,end-z,.055),"cedar",1.60)
    for x in (2.02,19.48):
        box(room,(x,3.03,1.047),(.50,12.95,2.73),"paper",2.21)
    box(room,(2.02,15.5,1.047),(17.96,.48,2.73),"paper",2.24)
    for x in np.linspace(2.50,19.48,8):
        box(room,(x,15.39,1.08),(.18,.24,2.73),"rail",1.03)
    for z in np.linspace(3.39,15.37,6):
        for x in (2.31,19.47):
            box(room,(x,z,1.08),(.21,.21,2.73),"rail",.91)
    for y in (1.10,2.22,3.65):
        box(room,(2.42,15.37,y),(17.12,.24,.12),"rail",1.38)
        for x in (2.35,19.46):
            box(room,(x,3.37,y),(.19,12.13,.12),"rail",1.38)
    for x,width in ((2.52,5.74),(10.74,8.73)):
        box(room,(x,3.057,1.04),(width,.45,.40),"paper",1.28)
        box(room,(x,3.026,1.417),(width,.50,.09),"rail",1.04)
    box(room,(8.25,3.5,1.027),(2.51,1.56,.085),"stone",.83)
    # A formal scroll sits between raised shoji panels behind Kanbe's desk.
    for x in (7.25,12.41):
        box(room,(x,15.348,2.52),(2.32,.095,.91),"rail",1.03)
        box(room,(x+.073,15.26,2.60),(2.17,.085,.75),"paper",1.02)
        for i in range(1,8):
            box(room,(x+i*.29,15.221,2.60),(.023,.058,.75),"cedar",.64)
    box(room,(10.53,15.255,2.28),(.91,.05,1.33),"rail",.74)
    box(room,(10.62,15.208,2.39),(.73,.053,1.10),"scroll",1.0)
    for y in (2.355,3.493):
        box(room,(10.49,15.18,y),(.99,.102,.071),"lacquer",.91)
    export("hoshi_magistrate_room",room,MATS)


def desk():
    shape = Geometry()
    for x in (-1.12,.96):
        for z in (-.28,.25):
            box(shape,(x,z,0),(.16,.14,.70),"rail",.79)
    box(shape,(-1.12,-.30,.32),(2.24,.108,.38),"cedar",.94)
    box(shape,(-1.22,-.40,.69),(2.44,.82,.089),"rail",1.03)
    box(shape,(-1.12,-.31,.78),(.91,.64,.031),"lacquer",.82)
    export("hoshi_magistrate_desk",shape,MATS)


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import voxfile

    meshes = {}
    for key,dimensions in (("hoshi_case_bundle",(.31,.25,.125)),("hoshi_inkstone",(.24,.14,.063))):
        meshes[key] = save(*convert_prop(key,dimensions,37,lower=.020),voxfile)
        voxel_asset(key)
    shell()
    desk()
    props = [
        ["hoshi_magistrate_desk",10.67,1.076,7.81,1.,0.],
        ["hoshi_inn_bench",4.68,1.074,8.42,1.,0.],
        ["hoshi_inn_bench",7.66,1.074,9.95,.88,.0],
        ["hoshi_trade_chest",16.31,1.074,9.18,1.45,-.05],
        ["hoshi_trade_chest",15.77,1.074,9.73,1.25,.15],
        ["hoshi_inkstone",9.98,1.895,7.80,1.05,.11],
        ["hoshi_case_bundle",10.43,1.888,7.98,1.24,-.16],
        ["hoshi_case_bundle",10.83,1.855,7.91,1.14,.12],
        ["hoshi_case_bundle",11.47,1.855,7.64,.96,.04],
        ["hoshi_tea_mat",10.1,1.074,8.7,1.,.0],
        ["hoshi_tea_mat",11.11,1.074,8.7,1.,.0],
    ]
    for x in (4.93,7.60,16.04,18.29):
        props.append(["hoshi_goods_rack",x,1.075,13.84,.94,0.])
        for i in range(3):
            for j in range(3):
                off=(j-1)*(.52+i*.016)
                props.append(["hoshi_case_bundle",x+off,1.312+i*.56,13.79,
                              .96+(i+j)%3*.12,.18*((i*2+j)%3-1)])
    lights = []
    for x,z,scale in ((3.44,5.46,.97),(13.13,8.94,1.),(18.94,12.98,1.01)):
        props.append(["hoshi_andon",x,1.075,z,scale,0.])
        lights.append([x,1.44,z,4.7,1.52])
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    index["M124"] = dict(terrain="hoshi_magistrate_room",placements=props,poolLights=lights)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"hoshi-magistrate-layout.json").write_text(json.dumps({
        "room":[44,40],"furnishings":len(props),"generated_props":meshes,
    },indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
