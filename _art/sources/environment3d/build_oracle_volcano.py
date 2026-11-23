"""Carry the volcanic kit into the Oracle's mountain route and battle."""

import json
from pathlib import Path
import sys

import numpy as np

from build_furnace import dressing, grid_surfaces
from export_coast import STAGE, export

HERE = Path(__file__).resolve().parent
STYLES = ("","furnace_ash","furnace_basalt","furnace_scorch","lava","furnace_road")


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    info={}
    for mid in ("M437","M894"):
        m,events=gm.make(mid)
        block, height=m.blk,m.hgt.astype(int)
        z,x=np.indices(block.shape)
        melt=block==gm.LAVA
        road=block==gm.DIRT
        step=(z>=54+1.5*np.cos(x*.08))&(z<=73+1.5*np.cos(x*.08))
        if mid=="M894":
            # A narrow tributary lies between the combat formations.
            center=63.+2.1*np.sin(z*.26)+1.15*np.cos(z*.36)
            tributary=(abs(x-center)<1.20+.37*np.sin(z*.43))&(z>42)&(z<84)
            melt |= tributary
            road |= step
        shore = ~melt & (np.roll(melt,1,axis=0)|np.roll(melt,-1,axis=0)|
                         np.roll(melt,1,axis=1)|np.roll(melt,-1,axis=1))
        tile=np.where(block!=0,1,0)
        rock=(height>=5)
        if mid=="M894":
            rock |= (z>=84+3.7*np.sin(x*.19)+2.0*np.cos(x*.31))&(~road)
        tile[rock]=2
        tile[road]=5
        tile[shore]=3
        tile[melt]=4
        solid,fluid=grid_surfaces(tile,height,STYLES,wall_style="furnace_basalt",fluid=4)
        tag=mid.lower()+"_oracle"
        export(tag,solid,{k:(k+".png",.92) for k in STYLES if k and k!="lava"})
        export(tag+"_flow",fluid,{"lava":("magma00.png",.66)})
        props,lights,spatter=dressing(gm,m,melt)
        if mid=="M894":
            for i,bx in enumerate(range(11,125,11)):
                bz=88+(i*3)%5
                y=(height[bz,bx]+1)*.5
                props.append(["basalt_spires",bx*.5+.25,float(y),bz*.5+.25,1.1+(i%4)*.25,.49*i])
        index[mid]=dict(terrain=tag,water=tag+"_flow",waterMode="lava",
                        placements=props,poolLights=lights,magmaSpatter=spatter)
        info[mid]=dict(name=m.name,props=len(props),liquid_cells=int(melt.sum()),
                       events=len(events.ev) if events else 0)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"oracle-volcano-layout.json").write_text(json.dumps({"maps":info},indent=2),
                                                 encoding="utf-8")


if __name__=="__main__":
    main()
