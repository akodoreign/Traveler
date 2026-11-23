"""Replace Kaiu's map-specific fixtures with Comfy-sourced voxel modules."""

import json
from pathlib import Path
import sys

import numpy as np

from export_coast import STAGE, voxel_asset
from voxelize_coast import convert_prop, save

HERE=Path(__file__).resolve().parent
MAPS=("M100","M101","M810")


def flame(voxfile):
    cells=[]
    colors=[]
    for h in range(22):
        t=h/21
        lean=2.2*t*t + .65*np.sin(h*.63)
        radius=4.7*(1-t)**.72 + .45
        for x in range(14):
            for z in range(11):
                d=np.hypot(x-5-lean,(z-5)*1.13)
                if d>radius or (d>radius*.8 and (x*7+z*5+h)%9==0):
                    continue
                center=np.clip((radius-d)/3.8,0,1)
                cells.append((x,z,h))
                colors.append([246+9*center,62+158*center+28*(1-t),9+87*center*(1-t)])
    voxels=np.array(cells)
    voxels-=voxels.min(axis=0)
    result=save("kaiu_brazier_flame",voxels,np.asarray(colors),[.046,.047,.038],
                str(HERE/"surface_sources/watchtower_signal.png"),voxfile)
    voxel_asset("kaiu_brazier_flame",hot_material=True)
    return result


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    import voxfile

    stock=[]
    for name,size,samples in (
        ("watchtower_signal",(.83,.78,1.03),31),
        ("garrison_gate",(3.50,.61,4.44),49),
        ("kaiu_straw_target",(1.04,.69,1.63),36),
    ):
        stock.append(save(*convert_prop(name,size,samples),voxfile))
        voxel_asset(name)
    stock.append(flame(voxfile))
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    summary={}
    for mid in MAPS:
        world,events=gm.make(mid)
        replaced=getattr(world,"kaiu_replaced",None)
        if replaced is None:
            replaced=[o for o in world.objs if o["t"]=="fb" and
                      (o["fbtype"],o["fbparam"]) in ((2,5),(2,6),(30,2))]
        config=index[mid]
        replacing={"watchtower_signal","garrison_gate","kaiu_straw_target"}
        config["placements"]=[row for row in config["placements"] if row[0] not in replacing]
        fires,lights=[],[]
        for o in replaced:
            x,y,z=o["x"]*.5+.25,o["y"]*.5,o["z"]*.5+.25
            if o["fbtype"]==30:
                config["placements"].append(["kaiu_straw_target",x,y,z,.89,.07])
            else:
                size=.69 if o["fbparam"]==6 else .61
                config["placements"].append(["watchtower_signal",x,y,z,size,.17+o["x"]*.19])
                fires.append([x,y+size*.93,z,size*.71])
                lights.append([x,y+size*1.38,z,4.7,1.66])
        if mid=="M101":
            config["placements"].append(["garrison_gate",19.75,1.49,22.74,.99,0.])
        config["watchfires"]=fires
        config["poolLights"]=lights
        summary[mid]={"stock_fixtures":len(replaced),"animated_watchfires":len(fires),
                      "events":len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"kaiu-detail-layout.json").write_text(json.dumps({"maps":summary,"voxels":stock},indent=2),encoding="utf-8")
    print(summary)


if __name__=="__main__":
    main()
