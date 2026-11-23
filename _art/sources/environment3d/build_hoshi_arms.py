"""Build a cedar tradesman's interior with exhibition stands and a service aisle."""

import json
from pathlib import Path
import sys

import numpy as np

from build_hoshi_stall import box
from build_hoshi_teahouse import MATS as TEA
from export_coast import Geometry, STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save

HERE = Path(__file__).resolve().parent
MATS = {**TEA, "indigo": ("inn_indigo.png",.92)}


def shell():
    room = Geometry()
    for i in range(31):
        x = 3.51 + i*.404
        seam = 7.84 + ((i*3)%5)*.28
        for z, end in ((4.506,seam), (seam+.014,13.03)):
            box(room, (x,z,1.013), (.392,end-z,.060), "cedar", 1.38)
    for x in (3.02,15.99):
        box(room,(x,4.04,1.04),(.51,9.35,2.53),"paper",2.18)
    box(room,(3.02,13.01,1.04),(13.45,.49,2.53),"paper",2.18)
    for x in np.linspace(3.46,15.96,7):
        box(room,(x,12.89,1.06),(.17,.26,2.52),"rail",.94)
    for z in np.linspace(4.09,12.96,5):
        for x in (3.29,15.96):
            box(room,(x,z,1.06),(.24,.16,2.53),"rail",.94)
    for y in (1.12,2.26,3.44):
        box(room,(3.34,12.87,y),(12.92,.22,.10),"rail",1.14)
        for x in (3.43,15.91):
            box(room,(x,4.1,y),(.16,8.90,.10),"rail",1.14)
    for x,width in ((3.42,3.35),(9.25,7.04)):
        box(room,(x,4.03,1.02),(width,.44,.45),"paper",1.06)
        box(room,(x,4.013,1.43),(width,.49,.084),"rail",.91)
    box(room,(6.83,4.43,1.029),(2.33,1.85,.075),"stone",.78)
    for x in (3.98,8.59,13.13):
        box(room,(x,12.82,2.45),(1.64,.094,.72),"rail",1.0)
        box(room,(x+.071,12.75,2.522),(1.498,.068,.58),"paper",.92)
        for i in range(1,7):
            box(room,(x+i*.234,12.70,2.521),(.028,.068,.58),"cedar",.55)
    export("hoshi_arms_room",room,MATS)


def displays():
    rack = Geometry()
    for x in (-.91,.82):
        for z in (-.27,.21):
            box(rack,(x,z,0),(.115,.112,1.71),"rail",.81)
    for y in (.17,.64,1.11,1.57):
        box(rack,(-.93,-.277,y),(1.86,.61,.073),"cedar",.88)
        box(rack,(-.79,-.22,y+.075),(1.58,.48,.018),"indigo",.81)
    export("hoshi_arms_display",rack,MATS)

    plinth = Geometry()
    box(plinth,(-.55,-.45,.03),(1.10,.90,.22),"rail",.95)
    box(plinth,(-.59,-.49,.24),(1.18,.98,.071),"cedar",.79)
    box(plinth,(-.52,-.42,.31),(1.04,.84,.026),"indigo",.78)
    export("hoshi_arms_plinth",plinth,MATS)


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import voxfile

    meshes = {}
    for key,dimensions in (
        ("hoshi_arms_bundle",(1.22,.18,.19)),
        ("hoshi_arms_armor_sample",(.78,.61,1.13)),
    ):
        meshes[key] = save(*convert_prop(key,dimensions,42,lower=.022),voxfile)
        voxel_asset(key)
    shell()
    displays()
    props = [
        ["hoshi_goods_counter",8.53,1.075,6.63,1.,0.],
        ["hoshi_arms_display",5.23,1.074,11.69,1.,.04],
        ["hoshi_arms_display",7.26,1.074,11.69,1.,.00],
        ["hoshi_arms_display",12.76,1.074,11.69,1.,.00],
        ["hoshi_arms_plinth",13.35,1.074,9.23,1.08,0.],
        ["hoshi_arms_plinth",14.11,1.074,10.14,.91,-.1],
        ["hoshi_arms_armor_sample",13.35,1.438,9.23,1.08,.07],
        ["hoshi_arms_armor_sample",14.11,1.384,10.14,.89,.28],
        ["hoshi_trade_chest",4.88,1.075,8.32,1.17,-.13],
        ["hoshi_trade_chest",5.43,1.075,8.52,1.0,.19],
        ["hoshi_storage_jar",3.91,1.073,10.17,1.19,.44],
    ]
    for x,levels in ((5.23,(.17,.64,1.57)),(7.26,(.64,1.11,1.57)),(12.76,(.17,.64,1.11))):
        for y in levels:
            props.append(["hoshi_arms_bundle",x,1.166+y,11.68,.9+.09*y,.06-y*.026])
    lights = []
    for x,z,scale in ((3.92,5.8,.93),(10.11,7.10,.86),(10.16,12.0,.96)):
        props.append(["hoshi_andon",x,1.075,z,scale,0.])
        lights.append([x,1.45,z,4.7,1.48])
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    index["M121"] = dict(terrain="hoshi_arms_room",placements=props,poolLights=lights)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"hoshi-arms-layout.json").write_text(json.dumps({
        "room":[36,36],"furnishings":len(props),"generated_props":meshes,
    },indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()
