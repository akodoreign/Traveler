"""Fit the Doji tide road, cave and arena to their authored native worlds."""
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
from build_river_lion_caves import EDGE, IRON, WOOD, native_bridge
from build_yasuki_coast import INNER, STONE, WALL, cave_mouth, faceted_rock
from diorama_trees import build_diorama_mesh
from doji_tide_worlds import ARENA, CAVE, HERE, MAPS, ROAD, variant
from export_coast import Geometry, STAGE, export
from publish_castle_gates import resource_files

SLATE="doji_sea_cliff_slate"
RECESS="doji_tidal_recess"
STRATA="doji_coastal_sandstone"
LEDGE="doji_cave_wet_slate"
SAND="doji_tide_sand"
TRACK="doji_coast_path"
GRASS="doji_maritime_grass"
NAVY="doji_tide_indigo"
IVORY="doji_tide_linen"
SEA="doji_open_cove_water"
POOL="doji_cave_tide"
MARK="doji_tide_cave_marker"
PINE="traveler_diorama_pine"
REED="iuchi_brook_reeds"
LAMP="snake_den_stone_lantern"
SKIFF="floating_flowers_work_skiff"
MOORING="cakon_mooring_gear"
ROCKS="yasuki_cave_tide_scored_rocks"
TIMBER=(WOOD,EDGE,IRON)
NORMALS={k:"doji_coastal_stone_normal.png" for k in (SLATE,RECESS,STRATA,LEDGE)}
MATS={**CORE, **{k:(k+".png",.86) for k in
      (SLATE,RECESS,STRATA,LEDGE,SAND,TRACK,GRASS,NAVY,IVORY,*TIMBER)},
      **{k:(k+"00.png",.23) for k in (SEA,POOL)}}


def materials(repo):
    root=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    assets={"shore":{"placements":[[a] for a in (PINE,REED,LAMP,SKIFF,MOORING,ROCKS)]}}
    for rel,data in resource_files(root,assets).items():
        path=STAGE/rel
        if not path.is_file() or path.read_bytes()!=data:
            path.write_bytes(data)
    for key in TIMBER:
        path=STAGE/"tex"/f"{key}.png"
        path.write_bytes((root/"tex"/path.name).read_bytes())

    image=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    relief=np.clip((image-np.median(image))/max(1.,image.std()),-2.2,2.2)
    v,u=np.indices(relief.shape,dtype=float)*2*pi/1024.
    bedding=np.maximum(0.,np.cos(2*v+.51*np.sin(2*u+v)+.35*np.sin(5*u-v)+.59*relief))**9
    color_variation=8.*np.cos(u)*np.sin(v)+3.4*np.sin(3*u+2*v)
    for key,color,strength in ((SLATE,(42,75,120),.22),(RECESS,(22,44,71),.18),
                               (STRATA,(55,86,126),.21),(LEDGE,(31,73,104),.19)):
        rgb=np.array(color)*(1.+strength*relief[...,None])+bedding[...,None]*[9.,7.,3.]
        rgb+=color_variation[...,None]*[.70,.88,1.]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{key}.png")
    normal=np.asarray(Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=float)
    normal=normal/127.5-1.
    normal[...,:2]*=.55
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((1.+normal)*127.5).clip(0,255))).save(STAGE/"tex/doji_coastal_stone_normal.png")
    for key,source,color,strength in (
        (SAND,"sand_scan",(187,151,97),.12),(TRACK,"kensu_path_clay",(161,121,76),.13),
        (GRASS,"meadow_scan",(53,122,59),.22),(NAVY,"iuchi_storm_woven_cloth",(19,44,96),.09),
        (IVORY,"iuchi_storm_woven_cloth",(218,216,184),.12),
    ):
        tint_texture(key,source,color,strength)

    z,x=np.mgrid[0:2*pi:320j,0:2*pi:320j]
    bed=4.2*np.cos(3*x-2*z)+5.*np.sin(z-x)+2.*np.cos(5*x+2*z)
    for phase in range(40):
        depth=Image.open(root/"tex"/f"winter_river_glacial_depth{phase:02}.png").convert("RGB")
        coast=np.asarray(depth,dtype=float)*[.89,1.08,1.26]
        Image.fromarray(np.uint8(coast.clip(0,255))).save(STAGE/"tex"/f"{SEA}{phase:02}.png")
        time=phase*2*pi/40.
        flow=np.sin(2*x+4*z-time+.41*np.sin(x+z))+.26*np.cos(3*x-3*z+2*time)
        variation=(bed+5.1*flow+3.*np.maximum(flow,0)**4)[...,None]
        water=np.array([12.,89.,127.])+variation*[.84,1.08,1.24]
        Image.fromarray(np.uint8(water.clip(0,255))).save(STAGE/"tex"/f"{POOL}{phase:02}.png")


def cave_floor(w,gm,geometry):
    name="doji_tidal_footpath_atlas"
    path=gaussian_filter(zoom((w.blk==gm.DIRT).astype(float),8,order=1),5.0)
    z,x=np.indices(path.shape,dtype=np.float32)
    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    grain=np.clip((scan[(z.astype(int)*2)%1024,(x.astype(int)*2)%1024]-np.median(scan))/scan.std(),-2.2,2.2)
    wash=np.cos(x*.026-z*.023)+.63*np.sin(x*.044+z*.047)
    shale=np.array([44.,91.,117.])
    ochre=np.array([133.,102.,63.])
    color=(shale+(ochre-shale)*(.89*path[...,None]))*(1.+(.105*grain+.06*wash)[...,None])
    Image.fromarray(np.uint8(color.clip(0,255))).save(STAGE/"tex"/f"{name}.png")
    for index,key in enumerate(geometry.materials):
        if key in (TRACK,LEDGE):
            corners=np.asarray([geometry.vertices[i] for i in geometry.faces[index]])
            if corners[:,2].min()>=1.49 and np.ptp(corners[:,2])<.002:
                geometry.materials[index]=name
                geometry.uvs[index]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in corners]
    return {name:(name+".png",.92)}


def coastal_floor(w,gm,geometry,grade):
    name=f"{w.mid.lower()}_coastal_floor_atlas"
    shape=(w.d*8,w.w*8)
    s=gaussian_filter(zoom(np.isin(w.blk,(gm.WATER,gm.SAND)).astype(float),8,order=1),7.0)
    route=gaussian_filter(zoom(np.isin(w.blk,(gm.ROAD,gm.DIRT)).astype(float),8,order=1),4.5)
    z,x=np.indices(shape,dtype=np.float32)
    patches=np.random.default_rng(174828).random((int(w.d*.48),int(w.w*.48)))
    field=np.asarray(Image.fromarray(np.float32(patches)).resize(shape[::-1],Image.Resampling.BICUBIC))-.5
    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    grain=np.clip((scan[(z.astype(int)*3)%1024,(x.astype(int)*3)%1024]-np.median(scan))/scan.std(),-2.2,2.2)
    grass=np.array([43.,116.,47.])
    sand=np.array([165.,133.,88.])
    clay=np.array([125.,94.,58.])
    if w.mid==ARENA:
        color=sand+(clay*.92-sand)*(.19*route[...,None])
    else:
        color=grass+(sand-grass)*np.clip(s[...,None]*1.13,0.,1.)
        color+=(clay-color)*np.clip(route[...,None]*1.11,0.,1.)
    color*=1.+(.27*field+.064*grain)[...,None]
    Image.fromarray(np.uint8(color.clip(0,255))).save(STAGE/"tex"/f"{name}.png")
    for index,key in enumerate(geometry.materials):
        if key in (TRACK,GRASS,SAND):
            corners=np.asarray([geometry.vertices[i] for i in geometry.faces[index]])
            if corners[:,2].min()>=grade-.018 and np.ptp(corners[:,2])<.002:
                geometry.materials[index]=name
                geometry.uvs[index]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in corners]
    return {name:(name+".png",.88)}


def front_deck(geometry):
    for z in np.arange(.03,6.5,.229):
        box(geometry,(43.5,z,1.94),(4.5,.211,.104),EDGE,1.28)
    for x in (43.54,47.88):
        box(geometry,(x,.03,2.44),(.108,6.47,.106),WOOD,1.57)
        for z in np.arange(.29,6.4,1.11):
            box(geometry,(x-.045,z,1.55),(.184,.166,1.05),WOOD,.90)


def palisades(geometry):
    for start,end,depth in ((10.5,19.1,41.36),(46.5,55.0,41.05)):
        box(geometry,(start,depth,.82),(end-start,.17,.132),WOOD,1.56)
        box(geometry,(start,depth,1.34),(end-start,.17,.125),WOOD,1.56)
        for index,x in enumerate(np.arange(start,end,.248)):
            z=depth-.15+.031*cos(index*.9)
            height=1.13+.15*sin(index*1.21)
            box(geometry,(x,z,.515),(.206,.206,height),EDGE,1.13)
            top=[(x,z,height+.515),(x+.206,z,height+.515),
                 (x+.15,z+.103,height+.64),(x+.04,z+.103,height+.64)]
            geometry.quad(top,[(0.,0.),(1.,0.),(1.,1.),(0.,1.)],EDGE)
        for x in (start+.02,end-.2):
            box(geometry,(x,depth-.18,.515),(.275,.32,1.24),WOOD,1.0)
            box(geometry,(x-.023,depth-.205,1.46),(.32,.37,.092),NAVY,1.0)


def crane_waycloth(geometry,x,z,y):
    box(geometry,(x-.071,z-.07,y),(.142,.14,2.27),WOOD,1.08)
    box(geometry,(x-.43,z-.07,y+2.18),(.86,.14,.095),WOOD,1.08)
    for i in range(14):
        a=-.39+i*.78/14
        b=a+.78/14
        def point(u,hem):
            return (x+u,z-.096+.052*cos(u*14),y+(1.23+.07*cos(u*8) if hem else 2.16))
        panel=[point(a,False),point(b,False),point(b,True),point(a,True)]
        uv=[(0.,0.),(1.,0.),(1.,1.),(0.,1.)]
        kind=IVORY if i in (0,1,5,6,7,8,12,13) else NAVY
        geometry.quad(panel,uv,kind)
        geometry.quad(panel[::-1],uv[::-1],kind)


def surface(w,gm):
    wet=w.blk==gm.WATER
    water_height=w.hgt.copy()
    if w.mid!=ARENA:
        water_height[w.blk==gm.PLANK]=1
        wet|=(w.blk==gm.PLANK)
    style=POOL if w.mid==CAVE else SEA
    _,base=grid_surfaces(wet.astype(int),water_height,("",style),wall_style=SLATE,fluid=1)
    if w.mid==CAVE:
        return base,style
    y=max(p[2] for p in base.vertices)
    quads=np.asarray(base.vertices).reshape(-1,4,3).tolist()
    if w.mid==ROAD:
        begin,end=-180.,0.
    else:
        begin,end=w.d*.5,w.d*.5+180.
    quads.append([(0.,begin,y),(w.w*.5,begin,y),(w.w*.5,end,y),(0.,end,y)])
    if w.mid==ARENA:
        for left,right in ((-115.,0.),(w.w*.5,w.w*.5+115.)):
            quads.append([(left,45.,y),(right,45.,y),(right,end,y),(left,end,y)])
    result=Geometry()
    for quad in quads:
        x0,z0,_=np.min(quad,axis=0)
        x1,z1,height=np.max(quad,axis=0)
        xs=np.linspace(x0,x1,1+max(1,int(np.ceil((x1-x0)/2.3))))
        zs=np.linspace(z0,z1,1+max(1,int(np.ceil((z1-z0)/.54))))
        for lo,hi in zip(xs,xs[1:]):
            for near,far in zip(zs,zs[1:]):
                points=[(lo,near,height),(hi,near,height),(hi,far,height),(lo,far,height)]
                uv=[]
                for x,z,_ in points:
                    if w.mid==ROAD:
                        bank=(8.5+1.7*sin(x*.174)+1.5*sin(x*.32-.71))*.5
                        depth=(bank-z)/11.
                    else:
                        bank=(86.+5.3*sin(x*.138)+1.7*cos(x*.5))*.5
                        depth=(z-bank)/12.
                    uv.append((x/29.+.015*sin(z*.15),.007+.985*float(np.clip(depth,0.,1.))))
                result.quad(points,uv,style)
    return result,style


def landscape(w,gm):
    water=w.blk==gm.WATER
    deck=w.blk==gm.PLANK
    stone=w.blk==gm.STONE
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(stone|deck,0,np.where(water,gm.SAND if w.mid!=CAVE else gm.CAVE_FLOOR,w.blk))
    dry.hgt=np.where(water,np.maximum(0,w.hgt-1),w.hgt)
    geometry=world_mesh(gm,dry,{gm.ROAD:TRACK,gm.DIRT:TRACK,gm.GRASS:GRASS,gm.SAND:SAND,gm.CAVE_FLOOR:LEDGE})
    grade=2.005 if w.mid==ROAD else 1.505 if w.mid==CAVE else .505
    palette=cave_floor(w,gm,geometry) if w.mid==CAVE else coastal_floor(w,gm,geometry,grade)
    shell=copy(w)
    shell.mid="M480" if w.mid==CAVE else "M470"
    first=len(geometry.faces)
    faceted_rock(geometry,shell,stone,grade)
    for i in range(first,len(geometry.faces)):
        points=[geometry.vertices[j] for j in geometry.faces[i]]
        x,z,y=np.mean(points,axis=0)
        geometry.materials[i]=RECESS if (w.mid==ROAD and abs(x-45.25)<2.2 and 16.8<z<19.6 and y<4.) else STRATA
        geometry.uvs[i]=[((x+.31*z)/3.4,(y+.18*z)/2.85) for x,z,y in points]
    if w.mid==ROAD:
        cave_mouth(geometry,45.25,12.72,17.13,grade,1.64,1.56,3.55,SLATE)
        front_deck(geometry)
        crane_waycloth(geometry,42.78,11.82,2.01)
        crane_waycloth(geometry,47.73,11.82,2.01)
    elif w.mid==CAVE:
        cave_mouth(geometry,23.25,.92,4.24,grade,1.55,1.53,2.83,SLATE)
        native_bridge(geometry,41.5,49.5,12.,15.,1.50)
    else:
        palisades(geometry)
        crane_waycloth(geometry,18.28,40.75,.515)
        crane_waycloth(geometry,47.10,40.49,.515)
    geometry.materials=[{STONE:SLATE,WALL:LEDGE,INNER:RECESS}.get(k,k) for k in geometry.materials]
    key=f"{w.mid.lower()}_doji_tide"
    export(key,geometry,{**MATS,**palette},normal_maps=NORMALS,smooth_materials=(STRATA,))
    layer,style=surface(w,gm)
    water_key=f"{key}_water"
    export(water_key,layer,MATS)
    return key,water_key,style,len(geometry.faces)


def adorn(w,gm):
    props,lights=[],[]
    grade=3 if w.mid==ROAD else 2 if w.mid==CAVE else 0

    def fit(key,x,z,size=1.,yaw=0.,sway=0.,*,water=False):
        iz,ix=int(z*2),int(x*2)
        wet=w.blk[iz,ix]==gm.WATER
        if (water and not wet) or (not water and (wet or int(w.hgt[iz,ix])!=grade)):
            return
        y=(w.hgt[iz,ix]+1)*.5+(.07 if water else .017)
        props.append([key,x,y,z,size,yaw,*([sway] if sway else [])])
        if key==LAMP:
            lights.append([x,y+1.05*size,z,4.47,8.7,0xffb45aff])

    if w.mid==ROAD:
        for x,z,s in ((9.,14.7,1.02),(14.6,13.5,1.10),(18.2,15.6,.88),(23.8,14.42,.96),
                      (29.3,13.5,1.12),(34.7,13.1,.88),(39.4,12.6,.83),(51.4,12.5,1.03),
                      (57.6,13.91,1.14),(63.5,13.40,.87),(69.4,13.88,1.2),(74.36,13.81,.96),
                      (80.7,14.21,.91),(84.4,15.8,1.02),(87.9,17.7,.9)):
            fit(PINE,x,z,s,.43*x,.019)
        for i,x in enumerate((17.6,22.8,28.33,33.7,37.,39.8,49.5,54.7,57.2,61.3,67.55)):
            fit(REED,x,5.51+1.02*sin(i*1.33),.59+.081*(i%4),.63*i,.031)
        for x,z,size in ((14.7,6.3,.49),(25.16,5.75,.46),(32.7,7.32,.46),(36.1,14.19,.74),
                         (40.1,12.68,.63),(49.33,12.68,.63),(53.03,6.12,.48),(63.56,6.03,.55),
                         (75.53,8.2,.54),(79.82,14.3,.64)):
            fit(ROCKS,x,z,size,.41*x)
        for x,z,s in ((41.75,12.06,.82),(48.12,12.08,.8),(41.98,6.66,.79),(49.17,6.69,.79)):
            fit(LAMP,x,z,s,.31)
        fit(MARK,40.80,11.16,1.02,.31)
        fit(MOORING,49.26,5.91,.84,.12)
        fit(SKIFF,42.07,2.51,.91,-1.15,water=True)
    elif w.mid==CAVE:
        for x,z,s in ((22.0,5.52,.74),(27.29,8.54,.88),(33.79,11.3,.8),(38.73,12.74,.8),
                      (41.2,12.78,.81),(49.91,12.58,.82),(55.4,13.94,.84),(61.21,15.26,.82),
                      (66.98,16.92,.90),(72.11,20.44,.82),(77.42,21.14,.81),(81.2,20.75,.81)):
            fit(LAMP,x,z,s,.18)
        fit(MARK,40.19,11.78,.82,.32)
        fit(MARK,51.05,14.56,.81,-.29)
        fit(MOORING,50.7,11.61,.9,.31)
        for x,z,size in ((31.32,13.08,.67),(38.12,15.1,.58),(49.29,17.32,.70),
                         (56.88,16.44,.59),(65.78,18.42,.77),(76.62,22.79,.74)):
            fit(ROCKS,x,z,size,.61*x)
    else:
        for x,z,s in ((13.1,40.26,.91),(20.11,41.1,.80),(25.36,41.18,.78),
                      (43.19,41.09,.74),(45.11,40.66,.78),(52.4,40.33,.84)):
            fit(LAMP,x,z,s,.17)
        for x,z,s in ((9.78,40.6,1.14),(12.2,42.6,.93),(55.1,42.20,1.16),(53.4,42.68,.89)):
            fit(PINE,x,z,s,.43*x,.023)
        for x,z,s in ((22.28,41.54,.69),(25.15,41.32,.53),(37.41,41.77,.65),(42.27,42.72,.75)):
            fit(ROCKS,x,z,s,.43*x)
        fit(MOORING,33.89,42.34,.83,-.26)
        fit(SKIFF,35.8,44.62,1.28,-1.34,water=True)
    result={"placements":props,"poolLights":lights,"hideStockScenery":True}
    if w.mid==CAVE:
        result["renderPreset"]="rt_hd2d_snake_den"
    return result


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials(repo)
    source=build_diorama_mesh(MARK,MARK,(.88,1.59,.76),main_component=True)
    index_path=STAGE/"index.json"
    index=json.loads(index_path.read_bytes())
    report={}
    for mid in MAPS:
        world,_=gm.make(mid)
        terrain,water,style,quads=landscape(world,gm)
        art=adorn(world,gm)
        art.update(terrain=terrain,water=water,
                   waterSequence={"prefix":style,"frames":40,"seconds":22.6 if mid==CAVE else 30.8})
        index[mid]=art
        report[mid]={"terrain_quads":quads,"placements":len(art["placements"]),"water":water}
    index_path.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"doji-tide-layout.json").write_text(json.dumps({"maps":report,"source":source},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
