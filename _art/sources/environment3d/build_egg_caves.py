"""Make the Egg Caves a consistent set of coastal limestone chambers."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import generated_scan, grid_surfaces
from export_coast import STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save

HERE = Path(__file__).resolve().parent
CAVES = ("M130","M131","M132","M133","M813")
STYLES = ("","egg_silt","egg_limestone","egg_wet","water")
NESTS = ((28,15),(33,20),(40,14),(44,19))


def textures():
    target = STAGE/"tex"
    stone = generated_scan("egg_limestone",1024)
    silt = generated_scan("egg_silt",1024)
    mixes = {"egg_limestone": stone*.67+[15,18,14],
             "egg_silt":silt*.63+[10,11,9],
             "egg_wet":silt*[.35,.48,.52]+[8,16,12]}
    for key,rgb in mixes.items():
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(target/f"{key}.png")


def surfaces(gm,m):
    colors = np.where(m.blk==0,0,1)
    wet = (m.blk & 31)==8
    rock = (m.blk==gm.CAVE_WALL)|(m.hgt>3)
    z,x = np.indices(m.blk.shape)
    if m.mid=="M813":
        rock = (m.blk==gm.CAVE_WALL)
    # Use a single damp deposit shared along the wall feet and between
    # chambers. Height breaks still come from the playable world grid.
    adjacent = np.roll(rock,1,axis=0)|np.roll(rock,-1,axis=0)|np.roll(rock,1,axis=1)|np.roll(rock,-1,axis=1)
    deposit = (.8*np.cos(x*.12)+.55*np.sin(z*.23+x*.08)) > (.41 if m.mid=="M131" else .67)
    colors[~rock & ~wet & (m.blk!=0) & (adjacent|deposit)] = 3
    colors[rock & (m.blk!=0)] = 2
    colors[wet] = 4
    return grid_surfaces(colors,m.hgt.astype(int),STYLES,wall_style="egg_limestone",fluid=4)


def details(gm,m,events):
    props = []
    lights = []
    event_tiles = [(event["pos"][0],event["pos"][2]) for event in events.ev.values()
                   if isinstance(event.get("pos"),(list,tuple)) and len(event["pos"])>=3] if events else []
    def add(key,x,z,size,yaw,y=None):
        if not (0<x<m.w-1 and 0<z<m.d-1):
            return
        if y is None:
            y=(int(m.hgt[z,x])+1)*.5
        props.append([key,x*.5+.25,y,z*.5+.25,size,yaw])
    if m.mid=="M813":
        for index,x in enumerate(range(8,127,8)):
            size=1.4+1.3*np.sin(index*1.77)**2
            add("egg_calcite",x,84+index%4,size,index*.25)
        for x,z,heat in ((29,83,1.35),(52,85,1.68),(74,85,1.45),(99,83,1.65)):
            lights.append([x*.5+.25,1.3,z*.5+.25,6.8,heat])
        return props,lights

    for z,x in np.argwhere((m.hgt>=5)&(np.roll(m.hgt,1,axis=0)<=2)):
        if (x*17+z*31)%55>1 or any(abs(x-ex)<3 and abs(z-ez)<3 for ex,ez in event_tiles):
            continue
        # Set the formation back from the cutaway face. Its full root
        # needs solid rock underneath.
        if x<1 or x>=m.w-1 or z+3>=m.d:
            continue
        plateau = m.hgt[z+1:z+4,x-1:x+2]
        if plateau.min()==plateau.max() and plateau[0,0]>=m.hgt[z,x]:
            add("egg_calcite",int(x),int(z+2),.72+(x*3%9)*.065,x*.90)
    # Each stop has one readable point of interest beyond the shared rock.
    if m.mid=="M130":
        placed_nests=[]
        offsets=sorted(((x,z) for x in range(-5,6) for z in range(-5,6)),
                       key=lambda p:(p[0]**2+p[1]**2,abs(p[0])))
        for x,z in NESTS:
            x,z=x+gm.PAD_X,z+gm.PAD_BOTTOM
            # Keep the woven base fully on the floor and outside loot markers.
            nearby=[(int(px),int(pz)) for px,pz in event_tiles+placed_nests
                    if abs(px-x)<8 and abs(pz-z)<8]
            for dx,dz in offsets:
                nx,nz=x+dx,z+dz
                patch=m.hgt[nz-1:nz+2,nx-1:nx+2]
                if patch.min()==patch.max()==2 and all((nx-px)**2+(nz-pz)**2>5 for px,pz in nearby):
                    add("egg_nest",nx,nz,.84,z*.34,1.52)
                    placed_nests.append((nx,nz))
                    break
    if m.mid=="M131":
        pools=np.argwhere((m.blk&31)==8)
        if len(pools):
            z,x = (int(v) for v in np.median(pools,axis=0))
            for dx,dz in ((-2,0),(2,3),(-1,2)):
                if (m.blk[z+dz,x+dx]&31)==8:
                    add("egg_calcite",x+dx,z+dz,.57,.54)
            lights.append([x*.5+.3,1.9,z*.5+.3,4.8,1.03])
    if m.mid=="M133":
        # Leave Ryozo, the eggs and the altar trigger clear.
        for x,z in ((21,17),(43,18),(23,32),(43,30)):
            x,z=x+gm.PAD_X,z+gm.PAD_BOTTOM
            if m.hgt[z,x]>=4:
                add("egg_calcite",x,z,1.05,x*.77)
    return props,lights


def main():
    repo=Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    import voxfile
    textures()
    sources=[]
    for key,world,cells in (("egg_calcite",(1.45,.94,1.69),42),("egg_nest",(1.27,1.13,.27),39)):
        sources.append(save(*convert_prop(key,world,cells),voxfile))
        voxel_asset(key)
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    material={name:(f"{name}.png",.92) for name in STYLES[1:4]}
    report={}
    for mid in CAVES:
        m,events=gm.make(mid)
        solid,water=surfaces(gm,m)
        key=mid.lower()+"_limestone"
        export(key,solid,material)
        props,lights=details(gm,m,events)
        entry={"terrain":key,"placements":props,"poolLights":lights}
        if water.faces:
            water_key=mid.lower()+"_limestone_pool"
            export(water_key,water,{"water":("surf00.png",.43)})
            entry["water"]=water_key
        index[mid]=entry
        report[mid]={"name":m.name,"world_grid":[m.w,m.d],"faces":len(solid.faces),
                     "props":len(props),"events":len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"egg-caves-layout.json").write_text(json.dumps({"maps":report,"sources":sources},indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
