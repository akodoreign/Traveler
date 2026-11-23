"""Dress the same two shores at exposed and submerged tide levels."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from export_coast import STAGE, export

HERE = Path(__file__).resolve().parent
STYLES = ("","tidal_sand","tidal_wet","tidal_water","cliff")
MATERIALS = {
    "tidal_sand":("sand.png",.93),
    "tidal_wet":("tidal_wet.png",.85),
    "tidal_water":("surf00.png",.30),
    "cliff":("cliff.png",.97),
}


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import gen_maps as gm

    sand = np.asarray(Image.open(STAGE/"tex/sand.png").convert("RGB"),dtype=float)
    wet = sand*np.array((.72,.76,.82))
    Image.fromarray(np.uint8(wet.clip(0,255))).save(STAGE/"tex/tidal_wet.png")
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    report = {}
    for mid in ("M212","M236"):
        world,_ = gm.make(mid)
        block,height = world.blk,world.hgt.astype(int)
        flooding = block==gm.WATER
        seaward = np.zeros_like(flooding)
        for axis,sign in ((0,-1),(0,1),(1,-1),(1,1)):
            seaward |= np.roll(flooding,sign,axis=axis)
        tiles = np.where(block!=0,1,0)
        tiles[seaward & (block==gm.SAND)] = 2
        tiles[flooding] = 3
        terrain,water = grid_surfaces(tiles,height,STYLES,wall_style="cliff",fluid=3)
        name = f"{mid.lower()}_landbridge"
        export(name,terrain,MATERIALS)
        export(name+"_water",water,MATERIALS)
        rows = []

        def prop(key,x,z,scale,yaw):
            x += gm.PAD_X
            z += gm.PAD_BOTTOM
            rows.append([key,x*.5+.25,float(height[z,x]+1)*.5,z*.5+.25,scale,yaw])

        for x,view in ((3,-1),(116,1)):
            prop("coast_pine",x,29,1.05,.42*view)
            prop("coast_pine",x+view*2,7,.74,-.63*view)
            prop("shore_talus",x-view*1,24,1.0,.42*view)
            prop("shore_talus",x-view*2,10,.70,.31*view)
            prop("wind_grass",x,24,.81,1.25*view)
            prop("wind_grass",x+view,12,.90,-.83*view)
            prop("coast_flowers",x,30,.78,.66*view)
        if mid=="M212":
            for x,z,size in ((70,24,.54),(73,21,.48),(75,24,.61)):
                prop("shore_talus",x,z,size,.15*x)
        index[mid] = dict(terrain=name,water=name+"_water",placements=rows)
        report[mid] = {"water_cells":int(flooding.sum()),"placements":len(rows)}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"tidal-bridge-layout.json").write_text(json.dumps(report,indent=2),encoding="utf8")


if __name__=="__main__":
    main()
