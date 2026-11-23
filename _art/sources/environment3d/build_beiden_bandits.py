"""Fit the Beiden woodland and the bandits' lived-in cavern."""
from copy import copy
import json
from math import sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from beiden_bandit_worlds import ROAD,CAVE,FIELD,HIDEOUT,HERE,MAPS,variant
from build_hoshi_stall import box
from build_iuchi_tower import tint_texture
from build_kaiu_kit import MATS as CORE,world_mesh
from build_yasuki_coast import INNER,STONE,WALL,cave_mouth,faceted_rock
from diorama_trees import LEAF,MAPLE,build_diorama_mesh,falling_leaves
from export_coast import STAGE,export
from publish_castle_gates import resource_files

WOOD="beiden_smoked_cypress"
WALLSTONE="beiden_sable_limestone"
COLD="beiden_rock_recess"
PLUM="beiden_hewn_russet_limestone"
LEAFMOLD="beiden_leafmold"
TRACK="beiden_clay_path"
FIR="beiden_woodland_green"
PINE="traveler_diorama_pine_coastal_daylight"
COT="beiden_cave_bandit_folding_cot"
RACK="beiden_cave_bandit_sack_rack"
LAMP="iuchi_fitted_andon"
BARREL="cakon_staved_barrel"
COVER="yasuki_cave_covered_supply_bales"
NORMALS={key:"beiden_weathered_limestone_normal.png" for key in (WALLSTONE,COLD,PLUM)}
MATS={**CORE,**{key:(key+".png",.89) for key in (WOOD,WALLSTONE,COLD,PLUM,LEAFMOLD,TRACK,FIR)}}


def prepare(repo):
    source=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    tags=(PINE,MAPLE,LEAF,LAMP,BARREL,COVER)
    for path,data in resource_files(source,{"beiden":{"placements":[[key] for key in tags]}}).items():
        dest=STAGE/path
        if not dest.is_file() or dest.read_bytes()!=data:
            dest.write_bytes(data)
    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    raw=gaussian_filter(scan,4.,mode="wrap")
    groove=np.clip((raw-np.median(raw))/scan.std(),-2.,2.)
    for key,tone,variation in ((WALLSTONE,(77.,46.,104.),.24),(PLUM,(112.,52.,68.),.21),(COLD,(30.,24.,56.),.24)):
        rgb=np.array(tone)*(1.+variation*groove[...,None])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{key}.png")
    normal=np.asarray(Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=float)/127.5-1.
    normal=gaussian_filter(normal,(3.,3.,0.),mode="wrap")
    normal[...,:2]*=.42
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((1.+normal)*127.5).clip(0,255))).save(STAGE/"tex/beiden_weathered_limestone_normal.png")
    for key,scan,tone,contrast in ((WOOD,"kaiu_cedar",(75,38,21),.20),(LEAFMOLD,"meadow_scan",(89,56,52),.08),
                                   (TRACK,"kensu_path_clay",(148,93,50),.09),(FIR,"meadow_scan",(32,112,45),.17)):
        tint_texture(key,scan,tone,contrast)


def floor_atlas(w,gm,geo,height):
    key=f"{w.mid.lower()}_beiden_floor_atlas"
    trail=gaussian_filter(zoom(np.isin(w.blk,(gm.ROAD,gm.DIRT)).astype(float),8,order=1),5.3)
    if w.mid in (FIELD,HIDEOUT):
        trail*=.55
    ground=np.array([33.,110.,45.] if w.mid in (ROAD,FIELD) else [88.,54.,51.])
    clay=np.array([153.,97.,55.] if w.mid in (ROAD,FIELD) else [148.,99.,50.])
    z,x=np.indices(trail.shape,dtype=float)
    variation=(.067*np.cos(x*.031-z*.052)+.039*np.sin(x*.086+z*.018)+.026*np.cos(x*.068+z*.053))
    color=(ground+(clay-ground)*trail[...,None])*(1.+variation[...,None])
    Image.fromarray(np.uint8(color.clip(0,255))).save(STAGE/"tex"/f"{key}.png")
    for i,old in enumerate(geo.materials):
        if old in (TRACK,FIR,LEAFMOLD):
            points=np.asarray([geo.vertices[j] for j in geo.faces[i]])
            if points[:,2].min()>=height-.022 and np.ptp(points[:,2])<.002:
                geo.materials[i]=key
                geo.uvs[i]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in points]
    return {key:(key+".png",.88)}


def wood_deck(geo,x,z,y,width,depth):
    box(geo,(x,z,y+.026),(width,depth,.10),WOOD,1.15)
    for i in range(int(width/.16)):
        box(geo,(x+i*.16+.011,z+.017,y+.124),(.15,depth-.034,.025),WOOD,1.75)


def shored_adit(geo,cx,front,back,floor,half,span,stone):
    cave_mouth(geo,cx,front,back,floor,half,1.64,span,stone)
    z=front-.31
    for side in (-1.,1.):
        x=cx+side*(half+.11)
        box(geo,(x-.12,z-.11,floor),(.24,.29,2.38),WOOD,.98)
        box(geo,(x-.16,z-.15,floor),(.32,.38,.15),PLUM,.90)
    box(geo,(cx-half-.29,z-.14,floor+2.26),(2.*half+.58,.32,.27),WOOD,1.22)


def scenery(w,gm):
    outdoor=w.mid in (ROAD,FIELD)
    floor=2.005 if w.mid==ROAD else 1.505 if w.mid==CAVE else .505
    stone=w.blk==gm.STONE
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(stone,0,w.blk)
    color={gm.ROAD:TRACK,gm.DIRT:TRACK,gm.GRASS:FIR,gm.GRASS3:FIR,gm.CAVE_FLOOR:LEAFMOLD}
    geo=world_mesh(gm,dry,color)
    atlas=floor_atlas(w,gm,geo,floor)
    rock=copy(w)
    rock.mid="M470" if outdoor else "M829" if w.mid==HIDEOUT else "M480"
    first=len(geo.faces)
    faceted_rock(geo,rock,stone,floor)
    for i in range(first,len(geo.faces)):
        p=[geo.vertices[j] for j in geo.faces[i]]
        geo.materials[i]=PLUM if outdoor else WALLSTONE
        geo.uvs[i]=[((x+.42*z)/3.85,(y+.27*z)/3.09) for x,z,y in p]
    if w.mid==ROAD:
        shored_adit(geo,45.25,12.90,17.15,floor,1.63,3.53,PLUM)
    elif w.mid==CAVE:
        shored_adit(geo,23.25,1.10,4.30,floor,1.54,2.76,WALLSTONE)
        wood_deck(geo,25.73,15.66,floor,2.48,1.95)
        wood_deck(geo,54.72,20.35,floor,3.48,1.45)
    elif w.mid==HIDEOUT:
        wood_deck(geo,32.30,38.2,floor,6.60,1.65)
    geo.materials=[{STONE:PLUM if outdoor else WALLSTONE,WALL:PLUM,INNER:COLD}.get(k,k)
                   for k in geo.materials]
    key=w.mid.lower()+"_beiden_bandits"
    export(key,geo,{**MATS,**atlas},normal_maps=NORMALS,smooth_materials=(WALLSTONE,PLUM))
    return key


def adorn(w,gm,events):
    outdoor=w.mid in (ROAD,FIELD)
    pieces,lighting,drift=[],[],[]
    grade=3 if w.mid==ROAD else 2 if w.mid==CAVE else 0
    anchors=[row["pos"] for row in events.ev.values() if row.get("pos") and row["role"]!="villager"] if events else []

    def add(key,x,z,scale=1.,yaw=0.,sway=0.,offset=0.):
        if w.hgt[int(z*2),int(x*2)]!=grade:
            return None
        y=(grade+1)*.5+.023+offset
        pieces.append([key,x,y,z,scale,yaw,*([sway] if sway else [])])
        if key==LAMP:
            lighting.append([x,y+.66*scale,z,4.45,8.45,0xffac4dff])
        return x,y,z

    if outdoor:
        rng=np.random.default_rng(int(w.mid[1:]))
        for zrow in ((5.4,8.,14.43,17.28,20.4) if w.mid==ROAD else (41.,44.2,48.28,51.82)):
            for index in range(5,int(w.w*.5)-3,3):
                if rng.random()<.25: continue
                x,z=index+rng.uniform(-.95,.95),zrow+rng.uniform(-.81,.81)
                if w.mid==ROAD and (w.blk[int(z*2),int(x*2)]==gm.ROAD or
                    (abs(x-45.25)<5.0 and z>6.3) or
                    any((a*.5-x)**2+(b*.5-z)**2<1.8 for a,_,b,_ in anchors)):
                    continue
                asset=MAPLE if rng.random()<.36 else PINE
                size=float(rng.uniform(.84,1.36))
                pos=add(asset,x,z,size,.6*x,.027)
                if pos and asset==MAPLE and rng.random()<.34:
                    drift.extend(falling_leaves(pos,size,index))
        if w.mid==ROAD:
            for x,z in ((41.89,13.19),(48.81,13.19),(36.5,12.34),(62.11,12.70)):
                add(LAMP,x,z,.78,.15)
    elif w.mid==CAVE:
        for x,z,yaw in ((26.52,16.73,.31),(27.67,16.94,.62),(55.63,21.13,.21),(57.23,21.15,-.27)):
            add(COT,x,z,.91,yaw,offset=.14)
        for x,z,yaw in ((29.27,18.28,.38),(36.1,12.11,.59),(41.46,15.64,.28),(56.75,13.48,.17),
                        (62.59,10.96,.46),(69.61,16.92,.67),(76.49,16.69,.31),(82.33,19.07,.24)):
            add(RACK,x,z,.93,yaw)
        for x,z in ((22.01,6.93),(26.73,11.38),(31.25,13.47),(37.20,12.28),(42.38,15.73),
                    (48.99,10.03),(55.34,13.14),(60.09,10.8),(65.52,10.36),(69.42,14.30),(76.07,18.16)):
            add(LAMP,x,z,.91,.1)
        for x,z in ((34.05,12.54),(44.86,13.91),(57.59,21.64),(68.14,10.43),(75.58,15.51)):
            add(BARREL,x,z,.84,.49)
    else:
        for x,z,key,offset in ((28.51,38.7,COVER,0.),(33.3,38.9,COT,.14),(35.43,38.94,RACK,.14),
                               (37.29,38.85,COT,.14),(42.11,38.02,RACK,0.),(46.13,38.24,BARREL,0.)):
            add(key,x,z,.92,.30,offset=offset)
        for x,z in ((23.73,40.28),(29.22,38.40),(32.53,37.74),(38.92,37.95),(44.56,38.02)):
            add(LAMP,x,z,.96,.12)
    return {"placements":pieces,"poolLights":lighting,"leafDrift":drift,"hideStockScenery":True,
            "renderPreset":("rt_coastal_brilliance_road_horizon" if w.mid==ROAD else
                            "rt_coastal_brilliance_arena_horizon" if w.mid==FIELD else "rt_coastal_brilliance_cave")}


def build(repo):
    gm=variant(repo)[2]
    prepare(repo)
    sources={COT:build_diorama_mesh(COT,COT,(1.82,.80,1.13),align_x=True,main_component=True),
             RACK:build_diorama_mesh(RACK,RACK,(1.50,1.64,.85),main_component=True)}
    manifest=STAGE/"index.json"
    rows=json.loads(manifest.read_bytes())
    counts={}
    for mid in MAPS:
        world,events=gm.make(mid)
        row=adorn(world,gm,events)
        row["terrain"]=scenery(world,gm)
        rows[mid]=row
        counts[mid]={"placements":len(row["placements"]),"leaves":len(row["leafDrift"])}
    manifest.write_text(json.dumps(rows,separators=(",",":")),"utf8")
    (HERE/"beiden-bandit-layout.json").write_text(json.dumps({"maps":counts,"sources":sources},indent=2),"utf8")


if __name__=="__main__":
    build(Path(sys.argv[1]).resolve())
