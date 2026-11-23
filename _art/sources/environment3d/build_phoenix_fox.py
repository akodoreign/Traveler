"""Fit miniature woods, mineral springs and offering niches to the Phoenix route."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from build_furnace import grid_surfaces
from build_hoshi_stall import box
from build_iuchi_tower import tint_texture
from build_kaiu_kit import MATS as CORE, world_mesh
from build_yasuki_coast import INNER, STONE, WALL, cave_mouth, faceted_rock
from diorama_trees import LEAF, MAPLE, PINE, build_diorama_mesh, falling_leaves
from export_coast import STAGE, export
from phoenix_fox_worlds import CAVE, FOREST, HERE, MAPS, ROAD, SHRINE, variant
from publish_castle_gates import resource_files

RUSSET="phoenix_hematite_cliff"
SHADOW="phoenix_cliff_recess"
COPPER="phoenix_ochre_shelves"
DIRT="phoenix_worn_trail"
MOSS="phoenix_moss_floor"
MEADOW="phoenix_evergreen_floor"
WATER="phoenix_fox_spring"
VERMILION="phoenix_shrine_lacquer"
CEDAR="phoenix_shrine_cedar"
LINEN="phoenix_shrine_linen"
FOX="phoenix_fox_cave_votive_pair"
TABLE="phoenix_cave_fox_offering_table"
STELE="phoenix_north_road_trail_stele"
LANTERN="snake_den_stone_lantern"
ANDON="dragon_mountain_andon"
REEDS="iuchi_brook_reeds"
TORII="dragon_forest_torii"
NORMALS={k:"phoenix_hematite_scanned_normal.png" for k in (RUSSET,SHADOW,COPPER)}
MATS={**CORE, **{k:(k+".png",.84) for k in
      (RUSSET,SHADOW,COPPER,DIRT,MOSS,MEADOW,VERMILION,CEDAR,LINEN)},
      WATER:(WATER+"00.png",.27)}


def materials(repo):
    assets={"woods":{"placements":[[key] for key in (PINE,MAPLE,LEAF,LANTERN,ANDON,REEDS,TORII)]}}
    source=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    for rel,data in resource_files(source,assets).items():
        path=STAGE/rel
        if not path.is_file() or path.read_bytes()!=data:
            path.write_bytes(data)
    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    grain=np.clip((scan-np.median(scan))/scan.std(),-2.2,2.2)
    v,u=np.mgrid[0:2*pi:1024j,0:2*pi:1024j]
    bands=np.maximum(0.,np.sin(3*v+.43*np.sin(2*u+v)+.53*grain))**9
    rock_color=((RUSSET,(75.,37.,49.),.23),(SHADOW,(27.,22.,48.),.15),(COPPER,(120.,64.,44.),.19))
    for key,value,contrast in rock_color:
        rgb=np.array(value)*(1.+(contrast*grain)[...,None])+bands[...,None]*[16.,7.,2.]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{key}.png")
    normal=np.asarray(Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=float)
    normal=normal/127.5-1.
    normal[...,:2]*=.51
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((1.+normal)*127.5).clip(0,255))).save(STAGE/"tex/phoenix_hematite_scanned_normal.png")
    for key,scan_name,color,strength in (
        (DIRT,"kensu_path_clay",(134,93,52),.15),
        (MOSS,"bayushi_garden_moss",(42,87,60),.17),
        (MEADOW,"meadow_scan",(42,104,43),.18),
        (VERMILION,"kaiu_cedar",(147,36,22),.12),
        (CEDAR,"kaiu_cedar",(75,41,31),.19),
        (LINEN,"iuchi_storm_woven_cloth",(224,206,167),.10),
    ):
        tint_texture(key,scan_name,color,strength)
    z,x=np.mgrid[0:2*pi:320j,0:2*pi:320j]
    stones=.28*np.sin(7*x+5*z)+.35*np.cos(4*x-3*z)+.25*np.sin(5*x+9*z)
    for phase in range(36):
        t=phase*2*pi/36.
        ripples=np.sin(4*z-x-t+.33*np.cos(2*x+z))+.25*np.cos(3*z+4*x-2*t)
        values=12.4*stones+3.5*ripples+7.*np.maximum(ripples,0.)**5
        rgb=np.array([15.,94.,113.])+values[...,None]*[.6,1.13,1.12]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{WATER}{phase:02}.png")


def paint_floor(w,gm,geometry,grade):
    key=w.mid.lower()+"_phoenix_floor"
    shape=(w.d*8,w.w*8)
    track=gaussian_filter(zoom(np.isin(w.blk,(gm.ROAD,gm.DIRT)).astype(float),8,order=1),4.8)
    z,x=np.indices(shape)
    field=np.random.default_rng(int(w.mid[1:])).random((w.d//2,w.w//2))
    field=np.asarray(Image.fromarray(np.float32(field)).resize(shape[::-1],Image.Resampling.BICUBIC))-.5
    stone=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    grain=np.clip((stone[(4*z)%1024,(4*x)%1024]-np.median(stone))/stone.std(),-2.2,2.2)
    clay=np.array([126.,88.,47.])
    green=np.array([38.,98.,38.] if w.mid in (ROAD,FOREST) else [33.,70.,52.])
    if w.mid in (FOREST,SHRINE):
        track*=.43 if w.mid==FOREST else .59
    rgb=(green+(clay-green)*track[...,None])*(1.+(.28*field+.052*grain)[...,None])
    Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{key}.png")
    for i,kind in enumerate(geometry.materials):
        if kind in (DIRT,MOSS,MEADOW):
            points=np.asarray([geometry.vertices[j] for j in geometry.faces[i]])
            if points[:,2].min()>=grade-.02 and np.ptp(points[:,2])<.002:
                geometry.materials[i]=key
                geometry.uvs[i]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in points]
    return {key:(key+".png",.88)}


def shrine_platform(geometry,x,z,y):
    """Ground the altar and its two offering shelves in a dry chamber."""
    box(geometry,(x-1.57,z-.78,y), (3.14,1.49,.145),COPPER,1.36)
    box(geometry,(x-1.44,z-.66,y+.14),(2.88,1.24,.108),CEDAR,1.33)
    box(geometry,(x-.92,z-1.04,y), (1.84,.28,.099),COPPER,1.13)
    for side in (-1.,1.):
        col=x+side*1.25
        box(geometry,(col-.13,z+.15,y+.24),(.26,.26,2.1),VERMILION,.92)
        box(geometry,(col-.19,z+.09,y+.235),(.38,.38,.122),COPPER,.83)
    box(geometry,(x-1.47,z+.13,y+2.12),(2.94,.28,.114),VERMILION,1.55)
    box(geometry,(x-1.61,z+.07,y+2.42),(3.22,.38,.17),CEDAR,1.58)
    box(geometry,(x-1.56,z+.075,y+2.36),(3.12,.37,.074),VERMILION,1.30)
    for i in range(5):
        xx=x-.84+i*.42
        points=[(xx-.073,z+.112,y+2.12),(xx+.073,z+.112,y+2.12),
                (xx+.083,z+.08,y+1.89),(xx-.044,z+.064,y+1.88)]
        uv=[(0,0),(1,0),(1,1),(0,1)]
        geometry.quad(points,uv,LINEN)
        geometry.quad(points[::-1],uv[::-1],LINEN)


def spring_rims(geometry,wet):
    """Run submerged sloped ledges against the physical spring boundary."""
    for r,c in np.argwhere(wet):
        x,z=c*.5,r*.5
        for dz,dx,a,b,inward in (
            (-1,0,(x,z),(x+.5,z),(0.,1.)),
            (0,1,(x+.5,z),(x+.5,z+.5),(-1.,0.)),
            (1,0,(x+.5,z+.5),(x,z+.5),(0.,-1.)),
            (0,-1,(x,z+.5),(x,z),(1.,0.)),
        ):
            row,col=r+dz,c+dx
            if 0<=row<wet.shape[0] and 0<=col<wet.shape[1] and wet[row,col]:
                continue
            bevel=.123+.039*sin(x*2.7+z)
            u,v=inward
            points=[(*a,1.475),(*b,1.475),(b[0]+u*bevel,b[1]+v*bevel,1.065),
                    (a[0]+u*bevel,a[1]+v*bevel,1.065)]
            t=a[0]+.76*a[1]
            geometry.quad(points,[(t,0.),(t+.5,0.),(t+.5,.42),(t,.42)],RUSSET)


def terrain(w,gm):
    wet,rock=w.blk==gm.WATER,w.blk==gm.STONE
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(rock,0,np.where(wet,gm.CAVE_FLOOR,w.blk))
    dry.hgt=np.where(wet,w.hgt-1,w.hgt)
    geometry=world_mesh(gm,dry,{gm.ROAD:DIRT,gm.DIRT:DIRT,gm.GRASS:MEADOW,
                               gm.GRASS3:MEADOW,gm.CAVE_FLOOR:MOSS})
    grade=2.005 if w.mid==ROAD else 1.505 if w.mid==CAVE else .505
    palette=paint_floor(w,gm,geometry,grade)
    shape=copy(w)
    shape.mid="M480" if w.mid in (CAVE,SHRINE) else "M470"
    first=len(geometry.faces)
    faceted_rock(geometry,shape,rock,grade)
    for i in range(first,len(geometry.faces)):
        points=[geometry.vertices[j] for j in geometry.faces[i]]
        geometry.materials[i]=COPPER if w.mid in (ROAD,FOREST) else RUSSET
        geometry.uvs[i]=[((x+.47*z)/3.67,(y+.22*z)/3.31) for x,z,y in points]
    if w.mid==ROAD:
        cave_mouth(geometry,35.25,12.91,17.17,grade,1.68,1.53,3.38,COPPER)
    elif w.mid==CAVE:
        cave_mouth(geometry,23.25,1.14,4.17,grade,1.51,1.48,2.75,RUSSET)
        shrine_platform(geometry,37.63,14.43,grade)
        spring_rims(geometry,wet)
    elif w.mid==SHRINE:
        shrine_platform(geometry,34.0,38.22,grade)
    geometry.materials=[{STONE:COPPER if w.mid==ROAD else RUSSET,INNER:SHADOW,WALL:RUSSET}.get(k,k)
                        for k in geometry.materials]
    model=w.mid.lower()+"_phoenix_fox"
    export(model,geometry,{**MATS,**palette},normal_maps=NORMALS,smooth_materials=(COPPER,RUSSET,SHADOW))
    layer=None
    if wet.any():
        _,surface=grid_surfaces(wet.astype(int),w.hgt,("",WATER),wall_style=RUSSET,fluid=1)
        layer=model+"_springs"
        export(layer,surface,MATS)
    return model,layer,len(geometry.faces)


def placements(w,gm,events):
    props,lights,leaves=[],[],[]
    outdoor=w.mid in (ROAD,FOREST)
    grade=3 if w.mid==ROAD else 2 if w.mid==CAVE else 0
    anchors=[row["pos"] for row in events.ev.values() if "pos" in row and row["role"]!="villager"] if events else []

    def fit(asset,x,z,scale=1.,yaw=0.,sway=0.,seat=0.):
        if int(w.hgt[int(z*2),int(x*2)])!=grade or w.blk[int(z*2),int(x*2)]==gm.WATER:
            return None
        y=(grade+1)*.5+.018+seat
        props.append([asset,x,y,z,scale,yaw,*([sway] if sway else [])])
        if asset in (LANTERN,ANDON):
            lights.append([x,y+(1.02 if asset==LANTERN else .66)*scale,z,4.65,8.4,0xffb15aff])
        return x,y,z

    if outdoor:
        rng=np.random.default_rng(int(w.mid[1:]))
        for z0 in ((5.9,13.7,17.0,20.3) if w.mid==ROAD else (40.56,44.73,48.34,51.21)):
            for x0 in range(5,int(w.w*.5-3),3):
                if rng.random()<.21:
                    continue
                x,z=x0+rng.uniform(-.8,.8),z0+rng.uniform(-.63,.63)
                if w.mid==ROAD:
                    if (abs(x-35.25)<5.4 and z>11.) or abs(x-45.5)<4.75 or any(
                        (a*.5-x)**2+(c*.5-z)**2<1.69 for a,_,c,_ in anchors):
                        continue
                    if w.blk[int(z*2),int(x*2)] not in (gm.GRASS,gm.GRASS2,gm.GRASS3):
                        continue
                elif 36.9<x<42.7 and z<46.:
                    continue
                use=MAPLE if rng.random()<(.46 if w.mid==ROAD else .29) else PINE
                scale=float(rng.uniform(.86,1.39))
                point=fit(use,x,z,scale,.31*x,.021 if use==PINE else .032)
                if point is not None and use==MAPLE and rng.random()<.32:
                    leaves.extend(falling_leaves(point,scale,x))
    if w.mid==ROAD:
        for x,z in ((32.58,12.48),(38.01,12.43),(43.01,9.39),(48.75,14.95),(63.19,13.46)):
            fit(LANTERN,x,z,.79,-.21)
        fit(STELE,32.48,10.86,1.0,.26)
        fit(STELE,48.88,13.84,.78,-.13)
    elif w.mid==CAVE:
        fit(TABLE,37.63,14.29,.91,-.14,.0,.24)
        fit(FOX,37.63,14.94,1.09,pi+.07,.0,.24)
        fit(FOX,29.39,10.18,.72,pi+.25)
        for x,z in ((22.05,6.49),(27.14,7.84),(33.46,10.73),(36.31,13.02),(39.03,13.04),
                    (44.53,15.42),(48.55,17.49),(54.57,13.48),(62.07,13.19),(69.21,7.28)):
            fit(LANTERN,x,z,.83,.16)
        for x,z in ((42.01,21.31),(50.93,23.95),(56.05,22.30),(71.88,22.78)):
            fit(ANDON,x,z,.85,-.21)
        for x,z in ((35.92,18.01),(48.65,19.90),(52.85,29.84),(65.32,25.36)):
            fit(REEDS,x,z,.71,.7,.013)
    elif w.mid==SHRINE:
        fit(TABLE,34.,37.94,.92,-.12,.0,.24)
        fit(FOX,34.,38.68,1.11,pi+.04,.0,.24)
        for x,z in ((25.9,40.06),(29.7,39.67),(32.04,39.73),(36.,39.72),(38.77,39.90),
                    (44.22,40.24),(47.91,39.33)):
            fit(LANTERN,x,z,.90,.27)
    else:
        fit(TORII,40.2,41.18,1.13,-.14)
        fit(STELE,37.42,41.11,.79,.15)
        for x,z in ((32.87,39.7),(38.81,41.75),(44.31,40.44)):
            fit(LANTERN,x,z,.87,.2)
    return {"placements":props,"poolLights":lights,"leafDrift":leaves,"hideStockScenery":True,
            **({} if outdoor else {"renderPreset":"rt_hd2d_snake_den"})}


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials(repo)
    sources={key:build_diorama_mesh(key,key,size,main_component=key!=FOX) for key,size in
             ((FOX,(2.35,1.39,1.05)),(TABLE,(1.38,.88,.81)),(STELE,(.88,1.53,.84)))}
    path=STAGE/"index.json"
    index=json.loads(path.read_bytes())
    stats={}
    for mid in MAPS:
        world,events=gm.make(mid)
        model,water,quads=terrain(world,gm)
        row=placements(world,gm,events)
        row["terrain"]=model
        if water:
            row.update(water=water,waterSequence={"prefix":WATER,"frames":36,"seconds":24.3})
        index[mid]=row
        stats[mid]={"quads":quads,"props":len(row["placements"]),"drifting_leaves":len(row["leafDrift"])}
    path.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"phoenix-fox-layout.json").write_text(json.dumps({"maps":stats,"sources":sources},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
