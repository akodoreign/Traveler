"""Export the exposed solid faces of a carved passage and its natural rock roof."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_kaiu_kit import faces
from build_furnace import grid_surfaces
from export_coast import Geometry, STAGE, export, terrain
from prepare_coast import collect

HERE=Path(__file__).resolve().parent
MAPS=("M102","M105","M437")
STYLES=("","furnace_ash","furnace_basalt","furnace_scorch","lava","furnace_road")


def entrance_mesh(m, outside, inside):
    cut=m.environment_tunnel
    x0,z0=cut["x"]-8,cut["z"]-1
    x1,z1=cut["x"]+9,cut["z"]+cut["reach"]+2
    solid=np.zeros((x1-x0,z1-z0,24),dtype=np.uint8)
    solid[...]=np.arange(24)[None,None,:] <= m.hgt[z0:z1,x0:x1].T[...,None]
    opening=np.zeros_like(solid,dtype=bool)
    for left,right,z,y in cut["path"]:
        opening[left-x0:right-x0,z-z0,y+1:9]=True
    for x,y,z,w,h,d,_ in cut["roof"]:
        solid[x-x0:x-x0+w,z-z0:z-z0+d,y:y+h]=1
    opening &= ~solid.astype(bool)
    result=Geometry()
    eye=np.eye(3)
    origin=np.array([x0,z0,0])
    for axis in range(3):
        a,b=(axis+1)%3,(axis+2)%3
        transformed=solid.transpose(axis,b,a)
        cavity=opening.transpose(axis,b,a)
        blank=np.zeros_like(transformed[0])
        for index,layer in enumerate(transformed):
            for sign in (-1,1):
                adjacent = index+sign
                empty=0<=adjacent<len(transformed)
                neighbor=transformed[adjacent] if empty else blank
                recess=cavity[adjacent] if empty else blank
                mask=np.where((layer!=0)&(neighbor==0),1+recess,0)
                if axis==2 and sign<0 and index==0:
                    continue
                plane=(index+(sign>0))*.5+sign*.093
                for left,front,right,back,shade in faces(mask):
                    corners=((left,front),(right,front),(right,back),(left,back))
                    if sign<0:
                        corners=(corners[0],corners[3],corners[2],corners[1])
                    points=[origin*.5+eye[axis]*plane+eye[a]*u*.5+eye[b]*v*.5
                            for u,v in corners]
                    uv=[(p[a]/2.7,p[b]/2.2) for p in points]
                    result.quad(points,uv,inside if shade==2 else outside)
    return result


def dark_material(texture, key, tint):
    image=Image.open(STAGE/"tex"/texture).convert("RGB")
    dark=np.asarray(image)*np.asarray(tint)
    Image.fromarray(np.uint8(dark.clip(0,255))).save(STAGE/"tex"/key)


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm

    dark_material("cliff.png","coastal_tunnel_interior.png",[.27,.30,.32])
    dark_material("furnace_basalt.png","volcanic_tunnel_interior.png",[.24,.22,.24])
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    report={}
    for mid in MAPS:
        m,events=gm.make(mid)
        cut=m.environment_tunnel
        x,z=cut["x"],cut["z"]
        coast=mid!="M437"
        key="coastal_entrance" if coast else "volcanic_entrance"
        stone="cliff.png" if coast else "furnace_basalt.png"
        outside,inside="rock","interior"
        if mid!="M105":
            mesh=entrance_mesh(m,outside,inside)
            textured="coastal_tunnel_interior.png" if coast else "volcanic_tunnel_interior.png"
            export(key,mesh,{outside:(stone,.96),inside:(textured,.97)})
        if coast:
            terrain(mid,collect(gm,mid))
        else:
            block=m.blk
            liquid=block==gm.LAVA
            code=np.where(block!=0,1,0)
            code[(m.hgt>=5)&(block!=0)]=2
            code[block==gm.DIRT]=5
            code[liquid]=4
            solid,_=grid_surfaces(code,m.hgt.astype(int),STYLES,wall_style="furnace_basalt",fluid=4)
            export("m437_oracle",solid,{k:(k+".png",.93) for k in STYLES if k and k!="lava"})
        entry=index[mid]
        entry["placements"]=[row for row in entry["placements"]
                             if row[0] not in ("egg_cave_arch","oracle_lava_tube",key)
                             and not (abs(row[1]-(x+.5)*.5)<4.0
                                      and z*.5-.8<row[3]<(z+cut["reach"])*.5)]
        entry["placements"].append([key,0.,0.,0.,1.,0.])
        if not coast:
            entry["poolLights"]=[row for row in entry["poolLights"] if abs(row[2]-z*.5)>.9]
            entry["poolLights"].append([x*.5+.25,2.42,z*.5+3.25,3.9,2.4])
        report[mid]=dict(width_in_cells=max(right-left for left,right,_,_ in cut["path"]),
                         depth_in_cells=cut["reach"],entry_world=[x*.5+.25,2.,z*.5],
                         roof_cells=len(cut["roof"]),events=len(events.ev))
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"cave-entrances-layout.json").write_text(json.dumps(report,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
