"""Make an original canvas camp and cut stone for the Old Quarry."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE=Path(__file__).resolve().parent
TEX=STAGE/"tex"
MATS={"face":("quarry_face.png",.96),"scree":("quarry_scree.png",.95),
      "canvas":("quarry_hemp.png",.95),"edge":("quarry_edge.png",.93),
      "timber":("storehouse_frame.png",.92),"grass":("meadow.png",.95)}
STYLES=("","scree","face","grass")
SHELTERS={"M104":((10,18),(22,25),(54,23),(66,19)),"M812":((30,78),(52,78),(88,78))}


def materials():
    for source,key,tint,slope in (
        ("quarry_face","quarry_face",(111,111,105),.86),
        ("quarry_face","quarry_scree",(132,116,95),.42),
        ("quarry_canvas","quarry_hemp",(148,129,96),.75),
        ("quarry_canvas","quarry_edge",(84,66,48),.53),
    ):
        im=Image.open(HERE/"surface_sources"/f"{source}.png").convert("RGB")
        scan=periodic(im,1024)
        n=scan@[.24,.64,.12]
        val=np.clip((n-np.median(n))/max(1.,np.ptp(np.percentile(n,[7,93]))),-.65,.65)
        rgb=np.array(tint)*(1.+val[...,None]*slope)
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(TEX/f"{key}.png")


def canopy():
    g=Geometry()
    for x in (-1.48,1.37):
        for z in (-1.12,1.02):
            box(g,(x,z,.015),(.105,.102,.42),"timber",.58)
    for z in (-1.25,1.24):
        box(g,(-.059,z,0.),(.12,.113,1.62),"timber",.69)
    box(g,(-.057,-1.36,1.569),(.119,2.83,.071),"timber",.68)
    for side in (-1.,1.):
        for i in range(5):
            z0=-1.23+i*.505
            z1=z0+.52
            ripple=.032*np.sin(.7+i*1.6)
            eave=side*(1.47+.038*np.sin(i*.79))
            points=[(0.,z0,1.594),(eave,z0,.16+ripple),(eave,z1,.17+ripple),(0.,z1,1.60)]
            uv=[(0.,z0),(.99,z0),(.99,z1),(0.,z1)]
            g.quad(points,uv,"canvas")
            g.quad(points[::-1],uv[::-1],"canvas")
            seam=[(0.,z0+.01,1.598),(eave,z0+.01,.17+ripple),(eave,z0+.033,.17+ripple),(0.,z0+.033,1.605)]
            g.quad(seam,[(0.,0.),(1.,0.),(1.,.03),(0.,.03)],"edge")
    # Close the lee end with unbleached canvas. The south end stays open.
    for col in range(12):
        x0=-1.40+col*.232
        x1=x0+.231
        y0=1.52-abs(x0)*.94
        y1=1.52-abs(x1)*.94
        points=[(x0,1.26,.01),(x1,1.26,.01),(x1,1.26,y1),(x0,1.26,y0)]
        uv=[(x, y) for x,_,y in points]
        g.quad(points,uv,"edge")
        g.quad(points[::-1],uv[::-1],"edge")
    export("quarry_tent",g,MATS)

    flap=Geometry()
    for i in range(8):
        left=i*.057
        right=left+.057
        kick=lambda x: .064*np.sin(x*34.)
        points=[(left,kick(left),0),(right,kick(right),0),
                (right,kick(right)*1.10,-.57-.088*np.sin(right*7)),(left,kick(left)*1.10,-.57-.088*np.sin(left*7))]
        uv=[(x*2,y) for x,_,y in points]
        flap.quad(points,uv,"canvas")
        flap.quad(points[::-1],uv[::-1],"canvas")
    export("quarry_tent_flap",flap,MATS)


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    import voxfile
    materials()
    canopy()
    source=save(*convert_prop("quarry_cut_rock",(1.18,.94,.54),30,lower=.066),voxfile)
    voxel_asset("quarry_cut_rock")
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    report={}
    for mid,fallback in SHELTERS.items():
        world,_=gm.make(mid)
        tile=np.where(world.blk!=0,1,0)
        tile[(world.blk==gm.STONE)|(world.blk==gm.STONEW)]=2
        tile[np.isin(world.blk,[gm.GRASS,gm.GRASS2,gm.GRASS3])]=3
        surface,_=grid_surfaces(tile,world.hgt.astype(int),STYLES,wall_style="face")
        # The stock turf has tall voxel blades above the dirt block.
        for face,material in zip(surface.faces,surface.materials,strict=True):
            if material=="grass":
                for index_ in face:
                    x,z,y=surface.vertices[index_]
                    surface.vertices[index_]=(x,z,y+.061)
        tag=mid.lower()+"_quarry"
        export(tag,surface,MATS)
        px,pz=(gm.PAD_X,gm.PAD_BOTTOM) if mid=="M104" else (0,0)
        shelters=getattr(world,"quarry_shelters",fallback)
        placements=[]
        for x,z in shelters:
            x,z=x+px,z+pz
            y=float((world.hgt[z,x]+1)*.5)
            placements.append(["quarry_tent",x*.5+1.50,y,z*.5+1.25,1.,0.])
            placements.append(["quarry_tent_flap",x*.5+1.37,y+1.43,z*.5+.032,1.,.055])
        stock=getattr(world,"quarry_replaced",None)
        if stock is None:
            stock=[o for o in world.objs if o["t"]=="fb" and o["fbtype"]==20]
        for o in stock:
            rock=o["fbparam"] in (gm.ROCK_S,gm.ROCK_M,19)
            name="quarry_cut_rock" if rock else "coast_pine"
            size=(.86 if o["fbparam"]==gm.ROCK_S else 1.13) if rock else (
                  1.07 if o["fbparam"]==gm.TREE_L else .74)
            placements.append([name,o["x"]*.5+.25,o["y"]*.5,o["z"]*.5+.25,
                               size,(o["x"]*.47+o["z"]*.23)%6.28])
        index[mid]=dict(terrain=tag,placements=placements)
        report[mid]={"tents":len(shelters),"stock_free_blocks_replaced":len(stock),"faces":len(surface.faces)}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"quarry-layout.json").write_text(json.dumps({"maps":report,"rock":source},indent=2),encoding="utf-8")
    print(report)


if __name__=="__main__":
    main()
