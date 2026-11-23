"""Fit the Dragon road and mountain cavern art to the authored worlds."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from build_furnace import grid_surfaces
from build_iuchi_tower import tint_texture
from build_kaiu_kit import MATS as CORE, world_mesh
from build_river_lion_caves import EDGE, IRON, WOOD, native_bridge
from build_yasuki_coast import INNER, STONE, WALL, cave_mouth, faceted_rock
from diorama_trees import build_diorama_mesh
from dragon_mountain_worlds import CAVE, HERE, MAPS, ROAD, SHRINE, variant
from export_coast import STAGE, export
from publish_castle_gates import resource_files

SHALE="dragon_spring_fractured_shale"
COLD="dragon_spring_blue_recess"
LEDGES="dragon_spring_emerald_ledge"
CLAY="dragon_spring_ochre_path"
FIR="dragon_spring_fir_ground"
JASPER="dragon_spring_warm_jasper"
STREAM="dragon_spring_running_water"
ROCK="dragon_cave_mountain_shale"
PINE="traveler_diorama_pine_coastal_daylight"
REEDS="iuchi_brook_reeds_coastal_daylight"
LAMP="dragon_mountain_andon"
JADE="iuchi_jade_seam"
MARKER="dragon_togashi_stele"
NORMAL={k:"dragon_spring_shale_normal.png" for k in (SHALE,COLD,LEDGES,JASPER)}
MATS={**CORE,**{key:(f"{key}.png",.88) for key in
      (SHALE,COLD,LEDGES,CLAY,FIR,JASPER,WOOD,EDGE,IRON)},STREAM:(STREAM+"00.png",.31)}


def prepare(repo):
    source=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    shared={"props":{"placements":[[key] for key in (PINE,REEDS,LAMP,JADE,MARKER)]}}
    for rel,data in resource_files(source,shared).items():
        path=STAGE/rel
        if not path.is_file() or path.read_bytes()!=data:
            path.write_bytes(data)
    for key in (WOOD,EDGE,IRON):
        copy_path=STAGE/"tex"/f"{key}.png"
        copy_path.write_bytes((source/"tex"/copy_path.name).read_bytes())

    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    diffuse=gaussian_filter(scan,3.2,mode="wrap")
    relief=np.clip((diffuse-np.median(diffuse))/scan.std(),-2.4,2.4)
    v,u=np.mgrid[0:2*pi:1024j,0:2*pi:1024j]
    seams=np.maximum(0.,np.cos(3*v-u+.51*np.sin(2*u+v)+.65*relief))**8
    seams*=.29+.71*np.sin(2*u+v)**2
    for key,color,contrast,spark in ((SHALE,(23.,58.,80.),.23,(19.,25.,21.)),
                                   (COLD,(17.,31.,51.),.18,(7.,9.,14.)),
                                   (LEDGES,(23.,76.,62.),.23,(10.,22.,14.)),
                                   (JASPER,(94.,59.,43.),.18,(24.,16.,6.))):
        rgb=np.array(color)*(1.+contrast*relief[...,None])+seams[...,None]*np.array(spark)
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{key}.png")
    normal=np.asarray(Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=float)
    normal=normal/127.5-1.
    normal=gaussian_filter(normal,(2.7,2.7,0.),mode="wrap")
    normal[...,:2]*=.44
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((1.+normal)*127.5).clip(0,255))).save(STAGE/"tex/dragon_spring_shale_normal.png")
    tint_texture(CLAY,"kensu_path_clay",(151,108,58),.19)
    tint_texture(FIR,"meadow_scan",(30,109,49),.22)
    z,x=np.mgrid[0:2*pi:320j,0:2*pi:320j]
    gravel=6.3*np.sin(3*x-z)+6.1*np.cos(4*x+5*z)+3.5*np.sin(7*z-x)
    for phase in range(48):
        t=phase*2*pi/48.
        riffle=np.sin(x+5*z-t+.31*np.cos(3*x+2*z))+.25*np.cos(2*x+3*z-2*t)
        surface=(gravel+3.8*riffle+6.*np.maximum(0.,riffle)**5)[...,None]
        rgb=np.array([12.,91.,127.])+surface*[.51,1.05,1.28]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{STREAM}{phase:02}.png")


def track_atlas(w,gm,geo,grade):
    name=f"{w.mid.lower()}_dragon_trail_atlas"
    z,x=np.indices((w.d*8,w.w*8))
    trails=gaussian_filter(zoom(np.isin(w.blk,(gm.ROAD,gm.DIRT)).astype(float),8,order=1),5.2)
    relief=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    source=gaussian_filter(relief,3.45,mode="wrap")
    grain=np.clip((source[(3*z)%1024,(3*x)%1024]-np.median(source))/relief.std(),-2.,2.)
    drift=np.cos(x*.028+z*.041)+.71*np.sin(x*.033-z*.059)
    if w.mid==ROAD:
        ground=np.array([25.,112.,43.])
        clay=np.array([148.,107.,60.])
    else:
        ground=np.array([23.,91.,61.])
        clay=np.array([125.,83.,51.])
    colors=(ground+(clay-ground)*trails[...,None])*(1.+(.052*grain+.053*drift)[...,None])
    Image.fromarray(np.uint8(colors.clip(0,255))).save(STAGE/"tex"/f"{name}.png")
    for i,material in enumerate(geo.materials):
        if material not in (CLAY,FIR,LEDGES):
            continue
        points=np.asarray([geo.vertices[j] for j in geo.faces[i]])
        if points[:,2].min()>=grade-.02 and np.ptp(points[:,2])<.002:
            geo.materials[i]=name
            geo.uvs[i]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in points]
    return {name:(name+".png",.92)}


def fit_wet_banks(geometry,w,flowing,planks,stone,grade):
    surface=np.where(flowing&planks,1,w.hgt)
    rows,columns=flowing.shape
    for r,c in np.argwhere(flowing):
        x,z=c*.5,r*.5
        if planks[r,c]:
            continue
        for dz,dx,a,b,inward in (
            (-1,0,(x,z),(x+.5,z),(0.,1.)),
            (0,1,(x+.5,z),(x+.5,z+.5),(-1.,0.)),
            (1,0,(x+.5,z+.5),(x,z+.5),(0.,-1.)),
            (0,-1,(x,z+.5),(x,z),(1.,0.)),
        ):
            rr,cc=r+dz,c+dx
            if not (0<=rr<rows and 0<=cc<columns):
                continue
            if flowing[rr,cc] or planks[rr,cc] or stone[rr,cc]:
                continue
            low=max((int(surface[r,c])+1)*.5+.011,grade-.91)
            if low>=grade-.03:
                continue
            above=grade-.006
            dx,dz=inward
            slope=.16+.046*sin(x*2.27+z*.71)
            points=[(*a,above),(*b,above),(b[0]+dx*slope,b[1]+dz*slope,low),
                    (a[0]+dx*slope,a[1]+dz*slope,low)]
            uv=[((px+.41*pz)/2.67,(y+.29*pz)/2.31) for px,pz,y in points]
            geometry.quad(points,uv,LEDGES)


def landscape(w,gm):
    flowing,planks,stone=w.blk==gm.WATER,w.blk==gm.PLANK,w.blk==gm.STONE
    grade=2.005 if w.mid==ROAD else 1.505 if w.mid==CAVE else .505
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(stone|planks,0,np.where(flowing,gm.CAVE_FLOOR,w.blk))
    dry.hgt=np.where(flowing,np.maximum(0,w.hgt-1),w.hgt)
    color_tiles={gm.ROAD:CLAY,gm.DIRT:CLAY,gm.GRASS:FIR,gm.GRASS3:FIR,gm.CAVE_FLOOR:LEDGES}
    if w.mid==ROAD:
        color_tiles[gm.ROUTE_THEME["mountain"][0]]=FIR
    geometry=world_mesh(gm,dry,color_tiles)
    atlas=track_atlas(w,gm,geometry,grade)
    rock=copy(w)
    rock.mid="M480" if w.mid==CAVE else "M829" if w.mid==SHRINE else "M470"
    first=len(geometry.faces)
    faceted_rock(geometry,rock,stone,grade)
    for index in range(first,len(geometry.faces)):
        points=[geometry.vertices[j] for j in geometry.faces[index]]
        geometry.materials[index]=SHALE
        geometry.uvs[index]=[((x+.44*z)/3.37,(y+.23*z)/2.87) for x,z,y in points]
    if w.mid==ROAD:
        cave_mouth(geometry,45.25,12.78,17.15,grade,1.62,1.61,3.54,SHALE)
        native_bridge(geometry,52.,61.5,9.,12.50,2.0)
        z,x=np.indices(w.hgt.shape)
        under=(abs(x-(115+3.9*np.sin(z*.135+.61)))<4.15)&planks
        flowing|=under
    elif w.mid==CAVE:
        cave_mouth(geometry,23.25,1.16,4.22,grade,1.53,1.51,2.84,SHALE)
    fit_wet_banks(geometry,w,flowing,planks,stone,grade)
    geometry.materials=[{STONE:SHALE,WALL:LEDGES,INNER:COLD}.get(k,k) for k in geometry.materials]
    model=w.mid.lower()+"_dragon_mountain"
    export(model,geometry,{**MATS,**atlas},normal_maps=NORMAL,smooth_materials=(SHALE,))
    riverbed=np.where(flowing&planks,1,w.hgt)
    _,water=grid_surfaces(flowing.astype(int),riverbed,("",STREAM),wall_style=SHALE,fluid=1)
    water_model=model+"_stream"
    export(water_model,water,MATS)
    return model,water_model,len(geometry.faces)


def props(w,gm,events):
    placements,lights=[],[]
    grade=3 if w.mid==ROAD else 2 if w.mid==CAVE else 0
    reserved=(gm.ROAD,gm.DIRT,gm.PLANK,gm.WATER)
    occupied=[row["pos"] for row in events.ev.values() if row.get("pos") and row["role"]!="villager"] if events else []

    def fit(asset,x,z,size=1.,yaw=0.,sway=0.,*,verge=False):
        r,c=int(z*2),int(x*2)
        if w.hgt[r,c]!=grade or w.blk[r,c]==gm.WATER:
            return
        if verge and (w.blk[r,c] in reserved or any((a*.5-x)**2+(b*.5-z)**2<1.9 for a,_,b,_ in occupied)):
            return
        y=(grade+1)*.5+.02
        placements.append([asset,x,y,z,size,yaw,*([sway] if sway else [])])
        if asset==LAMP:
            lights.append([x,y+.76*size,z,4.38,8.4,0xffb05cff])

    if w.mid==ROAD:
        rng=np.random.default_rng(476)
        for z0 in (5.65,8.21,14.76,17.9,21.4):
            for x0 in range(5,88,4):
                x,z=x0+rng.uniform(-.92,.92),z0+rng.uniform(-.69,.69)
                if (abs(x-45.25)<4.75 and z>10.) or rng.random()<.26:
                    continue
                fit(PINE,x,z,float(rng.uniform(.86,1.41)),.48*x,.021,verge=True)
        for x,z,scale in ((37.7,12.95,.77),(41.55,12.61,.92),(48.84,12.69,.82),(55.75,15.62,.70),(61.65,8.36,.89),
                          (62.22,13.53,.81),(73.16,12.97,.71),(82.76,12.99,.62)):
            fit(ROCK,x,z,scale,.46*x)
        for x,z,scale in ((41.67,11.75,.89),(48.79,11.66,.92),(51.43,12.78,.76),(62.26,12.61,.78),(66.11,10.65,.81)):
            fit(LAMP,x,z,scale,.11)
        for x,z in ((55.34,5.38),(58.81,7.45),(57.66,13.89),(54.88,16.91),(56.12,20.4),(59.02,17.10)):
            fit(REEDS,x,z,.84,.41*x,.024)
        fit(MARKER,40.16,11.25,.76,-.18)
    elif w.mid==CAVE:
        for x,z,scale in ((22.1,5.17,.85),(27.42,7.13,.87),(32.86,9.21,.9),(39.16,11.92,.82),(43.53,12.62,.77),
                         (48.18,11.2,.82),(53.86,14.6,.76),(58.46,13.3,.85),(63.11,11.52,.79),(70.36,9.34,.77)):
            fit(LAMP,x,z,scale,.11)
        for x,z,scale in ((27.22,9.87,.67),(36.49,10.79,.82),(43.46,14.81,.74),(48.31,15.02,.87),
                         (53.87,16.08,.95),(61.41,14.67,.76),(66.37,11.31,.89)):
            fit(ROCK,x,z,scale,.55*x)
        for x,z,scale in ((35.42,13.7,.87),(47.14,13.94,.83),(55.34,15.49,.86),(59.42,17.52,1.0),(65.66,13.80,1.07)):
            fit(JADE,x,z,scale,.38*x)
        fit(MARKER,42.43,12.76,.87,.12)
    else:
        for x,z,scale in ((15.6,40.1,1.24),(22.32,39.49,1.0),(28.03,39.85,.93),(38.81,40.43,1.21),
                          (45.8,38.9,1.13),(51.09,40.21,1.22)):
            fit(ROCK,x,z,scale,.47*x)
        for x,z,scale in ((24.41,37.66,1.18),(34.,38.02,1.22),(42.61,37.24,.94)):
            fit(JADE,x,z,scale,.38*x)
        for x,z in ((20.75,39.66),(28.39,38.63),(32.58,39.16),(40.16,39.52),(46.66,39.18)):
            fit(LAMP,x,z,.89,.17)
        fit(MARKER,35.16,39.67,1.13,.2)
    return {"placements":placements,"poolLights":lights,"hideStockScenery":True,
            "renderPreset":"rt_coastal_brilliance_road_horizon" if w.mid==ROAD else "rt_coastal_brilliance_cave"}


def main(repo):
    _,_,gm,_,_=variant(repo)
    prepare(repo)
    source=build_diorama_mesh(ROCK,ROCK,(1.88,1.44,1.76),main_component=True)
    index_path=STAGE/"index.json"
    data=json.loads(index_path.read_bytes())
    report={}
    for mid in MAPS:
        world,events=gm.make(mid)
        model,water,count=landscape(world,gm)
        entry=props(world,gm,events)
        entry.update(terrain=model,water=water,waterSequence={"prefix":STREAM,"frames":48,"seconds":22.8})
        data[mid]=entry
        report[mid]={"quads":count,"placements":len(entry["placements"]),"water":water}
    index_path.write_text(json.dumps(data,separators=(",",":")),"utf8")
    (HERE/"dragon-mountain-layout.json").write_text(json.dumps({"maps":report,"source":source},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
