"""Build Hoshi's coastal goods shop around a working counter and two stock aisles."""

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
    for index in range(35):
        x = 3.01 + index * .364
        for z, length in ((4.53, 2.72), (7.27, 2.77), (10.06, 3.98)):
            box(room, (x,z,1.018), (.354,length,.056), "cedar", 1.49)
    box(room, (6.84,4.47,1.025), (2.34,1.72,.084), "stone", .79)
    box(room, (2.52,14.0,1.04), (13.95,.49,2.55), "paper", 2.52)
    for x in (2.53,15.98):
        box(room, (x,4.04,1.04), (.49,10.02,2.54), "paper", 2.56)
    for x in np.linspace(2.95,15.92,7):
        box(room, (x,13.883,1.081), (.14,.24,2.55), "rail", .93)
    for z in np.linspace(4.41,13.78,5):
        for x in (2.81,15.85):
            box(room, (x,z,1.081), (.15,.22,2.54), "rail", .93)
    for y in (1.13,2.07,3.46):
        box(room, (2.86,13.87,y), (13.21,.23,.12), "rail", 1.44)
        for x in (2.85,15.88):
            box(room, (x,4.10,y), (.16,9.79,.12), "rail", 1.42)
    for x, width in ((2.92,3.91),(9.30,6.83)):
        box(room, (x,4.034,1.0), (width,.46,.41), "paper", 1.15)
        box(room, (x,4.018,1.406), (width,.49,.083), "rail", .95)
    for x in (4.28,7.83,11.52):
        box(room, (x,13.83,2.48), (1.47,.086,.76), "rail", 1.0)
        box(room, (x+.071,13.768,2.553), (1.328,.054,.62), "paper", .89)
        for i in range(1,7):
            box(room, (x+i*.206,13.741,2.554), (.022,.055,.617), "cedar", .54)
    export("hoshi_goods_room",room,MATS)


def furniture():
    counter = Geometry()
    box(counter, (-1.1,-.34,.04), (2.2,.68,.67), "rail", .92)
    for i in range(10):
        box(counter, (-1.08+i*.215,-.384,.115), (.207,.044,.550), "cedar", .65)
    box(counter, (-1.17,-.42,.708), (2.34,.85,.085), "cedar", 1.02)
    box(counter, (-.93,-.24,.793), (.43,.32,.03), "lacquer", .71)
    box(counter, (.53,-.075,.793), (.26,.19,.028), "paper", .57)
    export("hoshi_goods_counter",counter,MATS)

    rack = Geometry()
    for x in (-1.19,1.06):
        for z in (-.30,.20):
            box(rack, (x,z,0), (.126,.12,1.72), "rail", .75)
    for y in (.18,.76,1.37):
        box(rack, (-1.18,-.32,y), (2.35,.66,.073), "cedar", 1.05)
        box(rack, (-1.16,.275,y+.07), (2.32,.06,.09), "rail", .85)
    export("hoshi_goods_rack",rack,MATS)


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import voxfile

    meshes = {}
    for key, dimensions in (
        ("hoshi_trade_chest",(.65,.36,.38)),
        ("hoshi_salt_sack",(.47,.44,.46)),
    ):
        meshes[key] = save(*convert_prop(key,dimensions,35,lower=.018),voxfile)
        voxel_asset(key)
    shell()
    furniture()
    props = [
        ["hoshi_goods_counter",9.26,1.075,6.58,1.,0.],
        ["hoshi_goods_rack",5.37,1.075,12.69,1.,0.],
        ["hoshi_goods_rack",8.35,1.075,12.69,1.,0.],
        ["hoshi_goods_rack",13.72,1.075,12.36,1.02,-.14],
        ["hoshi_trade_chest",10.49,1.075,8.82,1.19,.11],
        ["hoshi_trade_chest",4.73,1.328,12.61,.97,.02],
        ["hoshi_trade_chest",13.22,1.328,12.19,1.03,-.14],
        ["hoshi_storage_jar",4.04,1.076,7.34,1.14,.02],
        ["hoshi_storage_jar",4.51,1.076,7.62,1.00,-.14],
        ["hoshi_storage_jar",4.97,1.076,7.42,.87,.16],
        ["hoshi_storage_jar",7.91,1.909,12.65,.78,.28],
        ["hoshi_storage_jar",8.35,1.909,12.64,.65,-.11],
        ["hoshi_storage_jar",13.71,1.936,12.32,.78,-.11],
        ["hoshi_storage_jar",14.13,1.936,12.25,.73,.15],
        ["hoshi_salt_sack",5.71,1.328,12.57,1.06,-.12],
        ["hoshi_salt_sack",6.19,1.328,12.56,.90,.26],
        ["hoshi_salt_sack",8.94,1.909,12.61,.96,-.11],
        ["hoshi_salt_sack",13.11,1.936,12.43,.90,-.14],
        ["hoshi_salt_sack",14.45,1.076,10.74,1.18,.22],
        ["hoshi_salt_sack",14.92,1.076,10.39,1.11,-.37],
        ["hoshi_rice_bale",3.94,1.075,9.29,1.04,-.18],
        ["hoshi_rice_bale",4.81,1.075,9.48,.99,.34],
        ["hoshi_rice_bale",12.89,1.076,11.21,.97,.17],
    ]
    light = []
    for x,z,scale in ((3.34,5.90,.93),(10.82,7.03,.88),(10.36,12.96,1.0)):
        props.append(["hoshi_andon",x,1.075,z,scale,0.])
        light.append([x,1.43,z,4.7,1.5])
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    index["M122"] = dict(terrain="hoshi_goods_room",placements=props,poolLights=light)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"hoshi-goods-layout.json").write_text(json.dumps({
        "room":[36,36],"furnishings":len(props),"generated_props":meshes,
    },indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()
