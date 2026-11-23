"""Rebuild the Kaiu Wall surfaces from the authored world grid and new scans."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box, shop_board
from export_coast import Geometry, STAGE, export
from prepare_coast import periodic

HERE=Path(__file__).resolve().parent
TEX=STAGE/"tex"
SCAN=HERE/"surface_sources"

TILE_SCAN={
    "kaiu_stone": ("kaiu_masonry",(91,94,100),.91),
    "kaiu_wood": ("kaiu_cedar",(78,63,49),.91),
    "kaiu_plaster": ("kaiu_plaster",(196,188,166),.92),
    "kaiu_roof": ("kawara_bluegrey",(64,76,85),.85),
    "kaiu_shoji": ("kaiu_plaster",(176,157,128),.92),
    "kaiu_redwood": ("kaiu_cedar",(123,65,44),.84),
}
MATS = {
    name:(name+".png",roughness) for name,(_,_,roughness) in TILE_SCAN.items()
}
MATS.update({"cliff":("cliff.png",.94),"meadow":("meadow.png",.95),
             "path":("path.png",.95)})
MATERIALS=("","path","cliff","meadow",*TILE_SCAN)


def scans():
    for name,(source,shade,_) in TILE_SCAN.items():
        im=Image.open(SCAN/f"{source}.png").convert("RGB")
        sample=periodic(im.crop((16,16,im.width-16,im.height-16)),1024)
        value=sample@np.array([.25,.6,.15])
        spread=max(np.percentile(value,90)-np.percentile(value,10),1)
        effect=np.clip((value-np.median(value))/spread,-.55,.55)
        colored=np.asarray(shade)[None,None,:]*(1+.77*effect[...,None])
        if name=="kaiu_shoji":
            for p in range(0,1024,256):
                colored[:,p:p+19,:]*=.48
                colored[p:p+17,:,:]*=.57
        Image.fromarray(np.uint8(np.clip(colored,0,255))).save(TEX/f"{name}.png")


def faces(mask):
    """Merge coplanar identical surfaces into rectangles."""
    pending=mask.copy()
    for row in range(pending.shape[0]):
        start=0
        while start<pending.shape[1]:
            material=int(pending[row,start])
            if not material:
                start+=1
                continue
            end=start+1
            while end<pending.shape[1] and pending[row,end]==material:
                end+=1
            height=row+1
            while height<pending.shape[0] and np.all(pending[height,start:end]==material):
                height+=1
            pending[row:height,start:end]=0
            yield start,row,end,height,material
            start=end


def world_mesh(gm,m,extra_tile_styles=None):
    volume=np.zeros((m.w,m.d,int(m.hgt.max())+22),dtype=np.uint8)
    solid=np.zeros_like(volume)
    tile_to_style={gm.KAIU:"kaiu_stone",gm.STONE:"kaiu_stone",gm.STONEW:"kaiu_stone",
                   gm.DARKWOOD:"kaiu_wood",gm.WOOD:"kaiu_wood",gm.PLANK:"kaiu_wood",
                   gm.PLASTER:"kaiu_plaster",gm.SHOJI:"kaiu_shoji",gm.ROOF:"kaiu_roof",
                   gm.TORII:"kaiu_redwood"}
    if extra_tile_styles:
        tile_to_style.update(extra_tile_styles)
    styles=tuple(dict.fromkeys((*MATERIALS,*tile_to_style.values())))
    code={name:k for k,name in enumerate(styles)}
    for iy in range(volume.shape[2]):
        live=(m.hgt.T>=iy)&(m.blk.T!=0)
        volume[...,iy][live]=code["cliff"]
        floor=live&(m.hgt.T==iy)
        volume[...,iy][floor&(m.blk.T==gm.ROAD)]=code["path"]
        volume[...,iy][floor&np.isin(m.blk.T,(gm.GRASS,gm.GRASS2,gm.GRASS3))]=code["meadow"]
        for tile,style in tile_to_style.items():
            volume[...,iy][live&(m.blk.T==tile)]=code[style]
    for prop in m.objs:
        if prop["t"] not in ("fill","blk"):
            continue
        tile=int(prop["blk"])
        x,y,z=map(int,(prop["x"],prop["y"],prop["z"]))
        if min(x,y,z)<0:
            continue
        w,h,d=(int(prop.get(k,1)) for k in ("w","h","d"))
        if tile == gm.VOID:
            volume[x:x+w,z:z+d,y:y+h]=0
            solid[x:x+w,z:z+d,y:y+h]=0
            continue
        # Reserve original shape and event logic. The replacement surface is
        # generated only for authored wall, plank, floor and roofing fills.
        tile_style=tile_to_style.get(tile,"path" if tile&31==2 else None)
        if tile_style:
            volume[x:x+w,z:z+d,y:y+h]=code[tile_style]
        solid[x:x+w,z:z+d,y:y+h]=1
    chosen=Geometry()
    shift=np.eye(3)
    for axis in range(3):
        a,b=(axis+1)%3,(axis+2)%3
        ordered=volume.transpose((axis,b,a))
        filled=(volume | solid).transpose((axis,b,a))
        pad=np.zeros_like(filled[0])
        for index,layer in enumerate(ordered):
            if not layer.any():
                continue
            for step in (-1,1):
                neighbor=filled[index+step] if 0<=index+step<len(ordered) else pad
                mask=np.where(neighbor==0,layer,0)
                plane=(index+(step>0))*.5+step*.019
                for x,z,w,d,mat in faces(mask):
                    corner=shift[axis]*plane
                    ops=((x,z),(w,z),(w,d),(x,d)) if step>0 else ((x,z),(x,d),(w,d),(w,z))
                    verts=[corner+shift[a]*r*.5+shift[b]*s*.5 for r,s in ops]
                    style=styles[mat]
                    tile=3.5 if style in ("meadow","path") else 2.6
                    chosen.quad(verts,[(r*.5/tile,s*.5/tile) for r,s in ops],style)
    return chosen


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    scans()
    # Connected travel route from the lookout down to the mainland gate.
    row_specs={
        "M100":[(56,18,"wall_watch_board",.95),(64,20,"salt_crate",.93)],
        "M101":[(43,26,"wall_garrison_board",1.),(74,33,"cedar_bench",.95),
                (76,33,"salt_crate",.90),(77,33,"salt_crate",1.08)],
        "M810":[],
    }
    shop_board("wall_watch_board","KAIU","WATCH","#243745")
    shop_board("wall_garrison_board","KAIU","GARRISON","#422d2a")
    resource=STAGE/"index.json"
    index=json.loads(resource.read_bytes())
    reports={}
    for mid,placements in row_specs.items():
        m,events=gm.make(mid)
        geometry=world_mesh(gm,m)
        tag=mid.lower()+"_kaiu"
        export(tag,geometry,MATS)
        nodes=[]
        event_cells=[(v["pos"][0],v["pos"][2]) for v in events.ev.values()
                     if isinstance(v.get("pos"),(list,tuple)) and len(v["pos"])>=3] if events else []
        for x,z,key,size in placements:
            if any(abs(x-ex)<2 and abs(z-ez)<2 for ex,ez in event_cells):
                continue
            y=(int(m.hgt[z,x])+1)*.5
            nodes.append([key,x*.5+.25,y,z*.5+.25,size,.07])
        index[mid]={"terrain":tag,"placements":nodes}
        reports[mid]={"map":m.name,"surface_quads":len(geometry.faces),"details":nodes,
                      "events":len(events.ev) if events else 0}
    resource.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"kaiu-kit-layout.json").write_text(json.dumps(reports,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
