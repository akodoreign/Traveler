"""Build the Zumiki snow road and the ice cutaways from its registered worlds."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,zoom

from build_furnace import grid_surfaces
from build_iuchi_tower import tint_texture
from build_kaiu_kit import MATS as CORE, world_mesh
from build_yasuki_coast import (STONE as OLD_STONE, WALL as OLD_WALL, INNER as OLD_INNER,
                               faceted_rock, cave_mouth)
from diorama_trees import build_diorama_mesh
from export_coast import STAGE, export
from publish_castle_gates import resource_files
from zumiki_ice_worlds import ARENA, CAVE, MAPS, ROAD, variant

HERE=Path(__file__).resolve().parent
BLUE="zumiki_cobalt_ice"
MID="zumiki_blue_limestone"
SHADE="zumiki_ice_recess"
HARD="zumiki_polished_ice_floor"
SNOW="zumiki_blue_white_snow"
TRACK="zumiki_pressed_snow_track"
WATER="zumiki_under_ice_water"
CRYSTAL="zumiki_ice_cave_crystal_curtain"
PINE="castle_snow_pine"
REED="winter_river_frost_reed"
LANTERN="snake_den_stone_lantern"
MATS={**CORE,**{k:(k+".png",.81) for k in (BLUE,MID,SHADE,HARD,SNOW,TRACK)},
      WATER:(WATER+"00.png",.25)}
NORMALS={k:"zumiki_ice_surface_normal.png" for k in (BLUE,MID,SHADE,HARD)}


def materials(repo):
    base=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    chosen={ROAD:{"placements":[[key] for key in (PINE,REED,LANTERN,"floating_flowers_river_post")]}}
    for rel,data in resource_files(base,chosen).items():
        target=STAGE/rel
        if not target.is_file() or target.read_bytes()!=data:
            target.write_bytes(data)
    # The weathered limestone diffuse drives stone relief. Frost and ice
    # keep separate color values so the crystals catch their own light.
    image=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    relief=np.clip((image-np.median(image))/max(1.,image.std()),-2.2,2.2)
    for key,color,contrast in ((BLUE,(19.,70.,143.),.16),(MID,(35.,97.,142.),.19),
                                (SHADE,(14.,25.,62.),.18),(HARD,(48.,105.,140.),.083)):
        rgb=np.asarray(color)*(1.+contrast*relief[...,None])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/(key+".png"))
    normal=np.asarray(Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB")).astype(float)
    normal=normal/127.5-1.
    normal[...,:2]*=.29
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((1.+normal)*127.5).clip(0,255))).save(STAGE/"tex/zumiki_ice_surface_normal.png")
    tint_texture(SNOW,"iuchi_frosted_meadow",(213,232,255),.065)
    tint_texture(TRACK,"iuchi_frosted_meadow",(150,184,213),.077)
    z,x=np.mgrid[0:2*pi:320j,0:2*pi:320j]
    fault=np.abs(np.sin(2*x-z+.33*np.cos(3*z+x)))
    ice_cracks=np.exp(-15.*fault)*(.8+.2*np.sin(3*z))
    bed=3.*np.cos(3*x-2*z)+2.8*np.sin(z-x)+9.0*ice_cracks
    for step in range(40):
        time=step*2*pi/40.
        run=np.sin(x+4*z-time+.39*np.sin(x+z)) + .23*np.cos(2*x-3*z+2*time)
        rgb=np.array([11.,68.,136.])+(bed+4.2*run+2.4*np.maximum(run,0)**4)[...,None]*[.58,.92,1.04]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{WATER}{step:02}.png")


def frost_floor(gm,w,geo):
    key="zumiki_frost_walk_atlas"
    powder=gaussian_filter(zoom((w.blk==gm.ROAD).astype(float),8,order=1),5.2)
    z,x=np.indices(powder.shape,dtype=np.float32)
    flecks=.31*np.sin(x*.037+z*.042)+.21*np.cos(z*.093+x*.033)+.42*np.cos(x*.026-z*.023)
    ice=np.array([55.,113.,153.])
    snow=np.array([159.,202.,235.])
    rgb=(ice+(snow-ice)*powder[...,None])*(1+.08*flecks[...,None])
    Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/(key+".png"))
    for index,kind in enumerate(geo.materials):
        if kind not in (TRACK,HARD):
            continue
        face=[geo.vertices[k] for k in geo.faces[index]]
        height=[v[2] for v in face]
        if max(height)-min(height)<.002 and min(height)>1.49:
            geo.materials[index]=key
            geo.uvs[index]=[(x/(w.w*.5),1.-z/(w.d*.5)) for x,z,_ in face]
    return {key:(key+".png",.73)}


def landscape(gm,w):
    outer=w.mid==ROAD
    arena=w.mid==ARENA
    water=w.blk==gm.WATER
    tall=w.blk==gm.STONE
    floor=2. if outer else .5 if arena else 1.5
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(tall,0,np.where(water,gm.CAVE_FLOOR,w.blk))
    dry.hgt=np.where(water,w.hgt-1,w.hgt)
    colors={gm.ROAD:TRACK,gm.SNOW:SNOW,gm.CAVE_FLOOR:HARD}
    geo=world_mesh(gm,dry,colors)
    atlas=frost_floor(gm,w,geo) if w.mid==CAVE else {}
    first=len(geo.faces)
    cut=copy(w)
    cut.mid="M470" if outer else "M829" if arena else "M480"
    faceted_rock(geo,cut,tall,floor+.006)
    for n in range(first,len(geo.faces)):
        points=np.asarray([geo.vertices[i] for i in geo.faces[n]])
        x,z,y=points.mean(axis=0)
        height=y-floor
        ledge=(height+.31*sin(x*.26)+.22*cos(z*.32))%2.2
        if outer and height>1.0 and np.ptp(points[:,2])<.35 and (ledge>1.2 or height>2.48):
            geo.materials[n]=SNOW
        elif height<.68 or (not outer and ledge<.34):
            geo.materials[n]=BLUE
        else:
            geo.materials[n]=MID
    if outer:
        cave_mouth(geo,37.25,12.86,17.18,floor+.006,1.63,1.56,3.53,BLUE)
    elif not arena:
        cave_mouth(geo,23.25,1.42,4.22,floor+.006,1.54,1.51,2.82,BLUE)
    geo.materials=[{OLD_STONE:BLUE,OLD_WALL:MID,OLD_INNER:SHADE}.get(k,k) for k in geo.materials]
    terrain=f"{w.mid.lower()}_zumiki_ice"
    export(terrain,geo,{**MATS,**atlas},normal_maps=NORMALS)
    if water.any():
        _,layer=grid_surfaces(water.astype(int),w.hgt,("",WATER),wall_style=BLUE,fluid=1)
        name=f"{w.mid.lower()}_zumiki_water"
        export(name,layer,MATS)
        return terrain,name,len(geo.faces)
    return terrain,None,len(geo.faces)


def adorn(gm,w):
    props,lights=[],[]
    grade=3 if w.mid==ROAD else 0 if w.mid==ARENA else 2
    def place(key,x,z,size=1.,yaw=0.,sway=0.,*,submerge=False):
        height=int(w.hgt[int(z*2),int(x*2)])
        if height!=grade and not (submerge and w.blk[int(z*2),int(x*2)]==gm.WATER):
            return None
        floor=(height+1)*.5+.018
        props.append([key,x,floor,z,size,yaw,*([sway] if sway else [])])
        return floor

    def lamp(x,z,scale=1.):
        y=place(LANTERN,x,z,scale)
        if y is not None:
            lights.append([x,y+1.05*scale,z,4.32,8.4,0xffb45aff])

    if w.mid==ROAD:
        for x,z,size in ((10.33,15.1,.91),(17.41,14.54,.96),(21.3,17.02,1.11),(25.4,15.6,.91),
                         (29.6,16.1,1.17),(32.62,13.4,.88),(42.15,14.67,.81),(48.87,15.,.92),
                         (56.39,16.1,.97),(64.78,16.7,1.22),(75.17,14.18,1.05),(83.65,15.12,.91),
                         (21.6,4.34,.75),(29.46,6.14,.87),(49.2,5.89,.78),(66.94,6.01,.85),(73.39,7.29,.78)):
            place(PINE,x,z,size,.55*x,.020)
        for x,z,s in ((32.72,12.98,.88),(41.36,12.81,.71),(52.56,4.82,.54),(63.37,4.34,.62)):
            place(CRYSTAL,x,z,s,.40*x)
        for x,z,s in ((34.93,12.12,.79),(39.56,12.22,.80),(45.5,4.9,.76)):
            lamp(x,z,s)
        for x in (24.7,29.12,53.4,56.31,62.52,66.09,70.35):
            place(REED,x,5.8+.47*sin(x),.73,.50*x,.025)
    elif w.mid==CAVE:
        for x,z,s in ((25.6,6.7,.77),(29.05,8.35,1.01),(33.8,13.95,1.2),(35.6,12.31,1.15),
                      (38.8,19.15,1.21),(46.34,15.45,1.05),(53.44,17.61,1.03),(60.25,10.44,.93),
                      (70.8,15.32,1.14),(78.34,10.65,.94)):
            y=place(CRYSTAL,x,z,s,.33*x,submerge=True)
            if y is not None:
                lights.append([x,y+.66*s,z,4.65,6.3,0x5b94faff])
        for x,z,s in ((24.3,7.46,.77),(32.42,10.38,.84),(37.15,12.91,.72),(42.96,13.15,.82),
                      (51.49,13.55,.84),(60.73,13.21,.82),(72.43,13.9,.84)):
            lamp(x,z,s)
    else:
        for x,z,s in ((20.1,41.5,1.30),(26.8,41.17,1.09),(34.35,40.53,1.04),
                      (39.47,42.2,1.44),(45.52,41.1,1.13),(50.1,39.9,.96)):
            y=place(CRYSTAL,x,z,s,.47*x)
            if y is not None:
                lights.append([x,y+.94*s,z,5.8,8.0,0x6ca2ffff])
        for x,z,s in ((24.43,39.57,.88),(31.82,40.20,.77),(37.70,39.17,.83),(46.45,39.53,.88)):
            lamp(x,z,s)
    return {"placements":props,"poolLights":lights,"hideStockScenery":True,
            **({} if w.mid==ROAD else {"renderPreset":"rt_hd2d_snake_den"})}


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials(repo)
    source=build_diorama_mesh(CRYSTAL,CRYSTAL,(2.12,2.48,1.70),main_component=True)
    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    report={}
    for mid in MAPS:
        world,_=gm.make(mid)
        terrain,water,quads=landscape(gm,world)
        entry=adorn(gm,world)
        entry["terrain"]=terrain
        if water:
            entry.update(water=water,waterSequence={"prefix":WATER,"frames":40,"seconds":22.4})
        index[mid]=entry
        report[mid]={"quads":quads,"props":len(entry["placements"]),"water":water}
    path.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"zumiki-ice-layout.json").write_text(json.dumps({"maps":report,"source":source},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
