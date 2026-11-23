"""Remake the Coast Road's original visible roadside prop families."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box, shop_board
from export_coast import Geometry, STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save

HERE=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
sys.path.insert(0,str(repo/"tools"))
import gen_maps as gm
import voxfile

TEX=STAGE/"tex"


def pine():
    _, points, rgb, pitch, input_=convert_prop("coast_pine_v2",(2.38,2.29,3.15),42,lower=.012,upper=.998)
    shadows=(rgb[:,1]>rgb[:,0]*1.025) & (rgb[:,1] >= rgb[:,2])
    color=rgb.astype(float)
    color[shadows]=color[shadows]*.81+np.array([9,19,0])
    color=np.clip(color,0,255)
    return save("coast_pine",points,color,pitch,input_,voxfile)


def talus():
    _, vox, rgb, _, input_=convert_prop("shore_boulder",(1.,1.,1.),26,lower=.08,upper=.92)
    span=vox.max(0)+1
    center=(span[:2]-1)*.5
    lifted=vox.copy()
    # Sloped layers of an irregular coastal outcrop share the Comfy texture.
    for axis in (0,1):
        h=vox[:,2]/span[2]
        scale=1.-.38*(h**1.38)
        shifted=(vox[:,axis]-center[axis])*scale+center[axis]
        lifted[:,axis]=np.rint(shifted + (h-.5)*(3. if axis==0 else -3.)).astype(int)
    lifted -= lifted.min(0)
    unique, take=np.unique(lifted,axis=0,return_index=True)
    rgb=rgb[take].astype(float)
    rgb *= .75
    return save("shore_talus",unique,np.clip(rgb,0,255),np.asarray([1.22,.94,.66])/(unique.max(0)+1),input_,voxfile)


def stonework():
    Image.new("RGB",(8,8),(224,159,70)).save(TEX/"lantern_flame.png")
    lamp=Geometry()
    for y,width,thickness in ((0,.60,.15),(.15,.46,.12),(.28,.28,.28),(.56,.54,.09),(.99,.61,.11),
                               (1.10,.48,.11),(1.21,.35,.095),(1.304,.20,.064)):
        box(lamp,(-width/2,-width/2,y),(width,width,thickness),"stone",.47)
    for x in (-.233,.15):
        for z in (-.233,.15):
            box(lamp,(x,z,.65),(.085,.085,.34),"stone",.43)
    box(lamp,(-.11,-.11,.67),(.22,.22,.25),"glow",.50)
    export("coast_lantern",lamp,{"stone":("cliff.png",.87),"glow":("lantern_flame.png",.51)})


def specs():
    manifest = [pine(),talus()]
    for row in manifest:
        voxel_asset(row["name"])
    stonework()
    shop_board("road_notice","HOSHI","NO-ICHI","#394638")
    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    evidence={}
    for mid in ("M102","M105","M811"):
        m,_=gm.make(mid)
        selected=getattr(m,"environment_replaced",None)
        if selected is None:
            selected=[o for o in m.objs if o["t"]=="fb" and (
                       o.get("fbtype")==20 or (o.get("fbtype"),o.get("fbparam")) in ((3,10),(3,21),(2,5)))]
        converted=[]
        for part in selected:
            kind=part["fbtype"]; idx=part["fbparam"]
            rotation=float(part.get("rot",0))*np.pi/2
            if kind==20:
                if idx in (gm.ROCK_S,gm.ROCK_M):
                    key,size,rotation="shore_talus",.91 if idx==gm.ROCK_S else 1.16,rotation+.08*part["x"]
                else:
                    key,size,rotation="coast_pine",{0:1.08,1:.80,3:.47}.get(idx,.75),rotation+.09*part["x"]
            elif kind==2:
                key,size="coast_lantern",.88
            elif idx==21:
                # Handled by the recessed passage in the map generator.
                continue
            else:
                key,size="road_notice",.91
            converted.append([key,part["x"]*.5+.25,part["y"]*.5,part["z"]*.5+.25,size,rotation])
        stock={"shore_boulder","shore_talus","coast_pine","coast_lantern","road_notice","egg_cave_arch"}
        index[mid]["placements"]=[row for row in index[mid]["placements"] if row[0] not in stock]+converted
        evidence[mid]={"removed_free_blocks":len(selected),"replacement_props":len(converted),
                       "asset_types":sorted(set(row[0] for row in converted))}
    path.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"coast-replacement-layouts.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
    (HERE/"coast-replacement-voxel-sources.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(evidence)


if __name__=="__main__":
    specs()
