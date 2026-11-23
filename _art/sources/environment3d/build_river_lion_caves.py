"""Fit the east bank, Lion foothills, three branch caves, and Lion cavern arena."""
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
from build_yasuki_coast import (STONE as YASUKI_STONE, INNER as YASUKI_INNER, TIMBER as YASUKI_WOOD,
                               PAINT as YASUKI_PAINT, RED as YASUKI_RED, WALL as YASUKI_WALL,
                               faceted_rock, cave_mouth)
from diorama_trees import build_diorama_mesh
from export_coast import Geometry, STAGE, export
from mine_track_geometry import put_mine_tracks, audit_mine_tracks
from publish_castle_gates import resource_files
from river_lion_worlds import ARENA, MAPS, ROADS, variant

HERE=Path(__file__).resolve().parent
JADE="branch_river_slate"
RUSSET="branch_lion_russet_stone"
SEAM="branch_sanguine_mineral_seam"
DARK="branch_rock_recess"
SAND="branch_copper_path"
GILT="branch_lion_dry_grass"
MOSS="branch_river_reed_green"
WOOD="branch_smoked_cedar"
EDGE="branch_worn_cedar"
GOLD="branch_lion_gold_lacquer"
VERMILION="branch_iron_red"
IRON="branch_smithed_iron"
BANK_WATER="branch_east_bank_water"
STREAM="branch_cavern_stream"

BOULDER="river_cave_water_polished_boulder"
MONUMENT="lion_cave_ocher_standing_stone"
ORE="lion_cave_old_mine_ore_basket"
PINE="traveler_diorama_pine"
MAPLE="traveler_diorama_maple"
LANTERN="snake_den_stone_lantern"
BUSH="iuchi_brook_reeds"
WOODLAMP="iuchi_fitted_andon"
SHARED=(PINE,MAPLE,LANTERN,BUSH,WOODLAMP,"smooth_hoshi_trade_chest","cakon_staved_barrel")
KEYS=(JADE,RUSSET,SEAM,DARK,SAND,GILT,MOSS,WOOD,EDGE,GOLD,VERMILION,IRON)
MATS={**CORE,**{item:(item+".png",.88) for item in KEYS},
      BANK_WATER:(BANK_WATER+"00.png",.32),STREAM:(STREAM+"00.png",.40)}
NORMALS={item:"branch_cavern_normal.png" for item in (JADE,RUSSET,SEAM,DARK)}


def materials(repo):
    source=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    for name,data in resource_files(source,{"shared":{"placements":[[asset] for asset in SHARED]}}).items():
        dest=STAGE/name
        if not dest.is_file() or dest.read_bytes()!=data:
            dest.write_bytes(data)
    photographed=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("RGB")) @ [.24,.63,.13]
    light=np.clip((photographed-np.median(photographed))/max(1.,photographed.std()),-2.,2.)
    for material,color,contrast in ((JADE,(16.,80.,99.),.24),(RUSSET,(64.,36.,37.),.23),(SEAM,(131.,62.,37.),.17),(DARK,(28.,20.,28.),.14)):
        rgb=np.asarray(color)*(1.+contrast*light[...,None])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/(material+".png"))
    original=np.asarray(Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB")).astype(float)
    normal=original/127.5-1.
    normal[...,:2]*=.48
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((normal+1.)*127.5).clip(0,255))).save(STAGE/"tex/branch_cavern_normal.png")
    for key,scan,color,contrast in (
        (SAND,"cakon_paddy_mud_scan",(153,98,51),.105),(MOSS,"iuchi_frosted_meadow",(45,112,49),.12),
        (GILT,"iuchi_frosted_meadow",(140,138,52),.14),(WOOD,"kaiu_cedar",(39,22,26),.18),
        (EDGE,"kaiu_cedar",(91,48,29),.19),(GOLD,"kaiu_cedar",(211,144,48),.115),
        (VERMILION,"kaiu_cedar",(144,30,25),.115),(IRON,"kaiu_cedar",(45,49,61),.105),
    ):
        tint_texture(key,scan,color,contrast)
    for phase in range(64):
        data=np.asarray(Image.open(source/"tex"/f"winter_river_glacial_depth{phase:02}.png").convert("RGB"))
        rgb=data*np.array([.92,1.10,.98])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{BANK_WATER}{phase:02}.png")
    z,x=np.mgrid[0:2*pi:256j,0:2*pi:256j]
    for phase in range(48):
        angle=phase*2*pi/48
        bed=4.4*np.cos(x+3*z)+2.9*np.cos(4*x-z)
        roll=np.sin(2*x+4*z-angle+.51*np.sin(x+z)) + .34*np.sin(x-3*z+2*angle)
        shine=np.maximum(0.,roll)**4
        rgb=np.array([9.,88.,106.])+(bed+4.1*roll+4.8*shine)[...,None]*[.52,1.06,1.29]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{STREAM}{phase:02}.png")


def cave_floor(w,geo,gm,watery):
    key=f"{w.mid.lower()}_branch_cave_floor"
    trail=gaussian_filter(zoom((w.blk==gm.DIRT).astype(float),7,order=1),4.5)
    z,x=np.indices(trail.shape,dtype=np.float32)
    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=np.float32)
    mineral=np.clip((scan[(z.astype(int)*3)%scan.shape[0],(x.astype(int)*3)%scan.shape[1]]-np.median(scan))/
                    max(1.,scan.std()),-2,2)
    roll=.55*np.sin(.037*x+.05*z)+.37*np.cos(z*.031-x*.029)
    base=np.array([25.,73.,80.] if watery else ([43.,26.,33.] if w.mid=="M484" else [64.,37.,35.]))
    path=np.array([112.,89.,52.] if watery else ([91.,51.,32.] if w.mid=="M484" else [139.,82.,38.]))
    rgb=(base+(path-base)*(.77*trail[...,None]))*(1.+(.107*mineral+.069*roll)[...,None])
    Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/(key+".png"))
    for n,material in enumerate(geo.materials):
        if material not in (JADE,RUSSET,SAND):
            continue
        vertices=[geo.vertices[i] for i in geo.faces[n]]
        heights=[v[2] for v in vertices]
        if max(heights)-min(heights)<.002 and min(heights)>(.49 if w.mid==ARENA else 1.49):
            geo.materials[n]=key
            geo.uvs[n]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in vertices]
    return {key:(key+".png",.92)}


def native_bridge(geo, left, right, south, north, y, rails=True):
    for x in np.arange(left,right,.205):
        box(geo,(x,south,y-.059),(min(.185,right-x),north-south,.097),EDGE,1.3)
    if not rails:
        return
    for z in (south-.055,north-.045):
        box(geo,(left,z,y+.49),(right-left,.10,.105),WOOD,1.4)
        for x in np.linspace(left+.11,right-.17,max(4,int((right-left)/1.25)+1)):
            box(geo,(x,z-.035,y),(.115,.155,.62),WOOD)
            box(geo,(x-.012,z-.052,y+.136),(.14,.19,.066),IRON)


def mine_support(geo,x,z,grade,span):
    for xx in (x-span*.5-.15,x+span*.5):
        box(geo,(xx,z,grade),(.29,.28,2.67),WOOD,.92)
        box(geo,(xx-.068,z-.055,grade+.21),(.421,.396,.12),IRON,.94)
    box(geo,(x-span*.5-.18,z-.04,grade+2.54),(span+.39,.41,.26),EDGE,1.1)


def votive_post(geo,x,z,y,scale=1.):
    post=.075*scale
    box(geo,(x-post,z-post,y),(.15*scale,.15*scale,2.22*scale),WOOD,.87)
    box(geo,(x-.44*scale,z-post,y+2.18*scale),(.88*scale,.15*scale,.11*scale),WOOD,.85)
    for i in range(8):
        lo=-.34+i*.085
        hi=lo+.085
        def strip(u,low):
            return x+u*scale,z-.22*scale+.062*scale*sin(u*10),y+scale*(1.20+.08*cos(u*8) if low else 2.13)
        panel=[strip(lo,False),strip(hi,False),strip(hi,True),strip(lo,True)]
        uv=[(0.,1.),(1.,1.),(1.,0.),(0.,0.)]
        color=GOLD if i in (0,3,4,7) else VERMILION
        geo.quad(panel,uv,color)
        geo.quad(panel[::-1],uv[::-1],color)


def bank_surface(surface,w):
    y=max(p[2] for p in surface.vertices)
    quads=np.asarray(surface.vertices).reshape(-1,4,3).tolist()
    quads.append([(2.5,-19.,y),(68.5,-19.,y),(68.5,0.,y),(2.5,0.,y)])
    quads.append([(43.5,0.,y),(48.,0.,y),(48.,4.95,y),(43.5,4.95,y)])
    result=Geometry()
    for quad in quads:
        a,b,_=np.min(quad,axis=0)
        c,d,height=np.max(quad,axis=0)
        cols=np.linspace(a,c,1+max(1,int(np.ceil((c-a)/2.8))))
        rows=np.linspace(b,d,1+max(1,int(np.ceil((d-b)/.5))))
        for x,u in zip(cols,cols[1:]):
            for z,v in zip(rows,rows[1:]):
                corners=[(x,z,height),(u,z,height),(u,v,height),(x,v,height)]
                texture=[]
                for wx,wz,_ in corners:
                    shore=(8.1+1.6*sin(.206*wx)+.8*cos(.332*wx))*.5
                    depth=float(np.clip((shore-wz)/12.,0,1))
                    texture.append((wx/34.+.015*sin(wz*.22),.007+.985*depth))
                result.quad(corners,texture,BANK_WATER)
    return result


def scenery(gm,w):
    road=w.mid in ROADS
    bank=w.mid=="M471"
    watery=w.mid in ("M471","M482")
    grade=2. if road else .5 if w.mid==ARENA else 1.5
    rock=JADE if watery else RUSSET
    water=w.blk==gm.WATER
    stone=w.blk==gm.STONE
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(stone,0,np.where(water,gm.SAND if road else gm.CAVE_FLOOR,w.blk))
    dry.hgt=np.where(water,w.hgt-1,w.hgt)
    # The fitted deck owns the visual top across the collider. Leave the
    # water and supporting ground visible through the slat gaps.
    deck=(w.blk==gm.PLANK)
    if bank:
        zz,xx=np.indices(deck.shape)
        deck &= zz<=9
    dry.blk[deck]=0
    geo=world_mesh(gm,dry,{gm.CAVE_FLOOR:rock,gm.SAND:SAND,gm.DIRT:SAND,gm.ROAD:SAND,
                            gm.GRASS:GILT,gm.GRASS2:MOSS if bank else GILT,gm.PLANK:EDGE})
    palette={} if road else cave_floor(w,geo,gm,watery)
    # Reuse the continuous rock builder with the same cutaway profiles.
    shell=copy(w)
    shell.mid="M470" if road else "M829" if w.mid==ARENA else "M480"
    first_rock=len(geo.faces)
    faceted_rock(geo,shell,stone,grade+.006)
    if not watery:
        for n in range(first_rock,len(geo.faces)):
            x,z,y=np.mean([geo.vertices[v] for v in geo.faces[n]],axis=0)
            seam=(y*2.57+.34*sin(x*.69)+.31*cos(z*.67))%3.17
            if y>grade+.63 and 1.12<seam<1.40:
                geo.materials[n]=SEAM
    if road:
        for center,start,end in w.branch_mouths:
            cave_mouth(geo,center*.5+.25,start*.5-.63,end*.5,grade+.009,1.65,1.60,3.41,
                       rock,reinforced=not bank)
        if bank:
            native_bridge(geo,43.5,48.,.12,6.35,grade+.03,rails=False)
    elif w.mid!=ARENA:
        cave_mouth(geo,23.25,1.43,4.27,grade+.007,1.55,1.52,2.76,
                   rock,reinforced=w.mid=="M484")
    if w.mid=="M482":
        a,b,c,d=w.branch_bridge
        native_bridge(geo,a*.5,b*.5,c*.5,d*.5,grade+.014)
    elif w.mid=="M483":
        box(geo,(33.75,9.77,grade), (1.7,.96,.16),RUSSET,.92)
        box(geo,(33.62,9.64,grade), (1.92,1.2,.065),SEAM,.92)
        for x,z in ((32.94,10.01),(36.24,10.31),(49.26,10.55)):
            votive_post(geo,x,z,grade,.87)
    elif w.mid=="M484":
        for x,z,span in ((26.8,8.50,3.24),(42.4,8.93,3.22),(58.0,11.20,3.38),(60.6,19.1,3.50)):
            mine_support(geo,x,z,grade,span)
        failures={index:len(points) for index,points in audit_mine_tracks(w).items() if len(points)}
        assert not failures,failures
        put_mine_tracks(geo,w,grade,WOOD,IRON,GOLD,VERMILION)
    elif w.mid==ARENA:
        put_mine_tracks(geo,w,grade,WOOD,IRON,GOLD,VERMILION,arena=True)
        for x in (25.45,30.4,44.32):
            votive_post(geo,x,40.5,grade,1.03)
        for x in (22.62,43.45):
            mine_support(geo,x,42.25,grade,3.05)

    remap={YASUKI_STONE:rock,YASUKI_WALL:rock,YASUKI_INNER:DARK,
           YASUKI_WOOD:WOOD,YASUKI_PAINT:GOLD,YASUKI_RED:VERMILION}
    geo.materials=[remap.get(item,item) for item in geo.materials]
    terrain=f"{w.mid.lower()}_branch_landscape"
    export(terrain,geo,{**MATS,**palette},normal_maps=NORMALS)
    if not water.any():
        return terrain,None,len(geo.faces)
    prefix=BANK_WATER if bank else STREAM
    _,wet=grid_surfaces(water.astype(int),w.hgt,("",prefix),wall_style=rock,fluid=1)
    if bank:
        wet=bank_surface(wet,w)
    else:
        # The stream continues below the dry collider and slatted deck.
        xyz=[(41.3,12.49,1.071),(44.3,12.49,1.071),(44.3,15.03,1.071),(41.3,15.03,1.071)]
        wet.quad(xyz,[(a/4.7,b/4.7) for a,b,_ in xyz],STREAM)
    name=f"{w.mid.lower()}_branch_water"
    export(name,wet,MATS)
    return terrain,name,len(geo.faces)


def dress(gm,w):
    props,lights=[],[]
    exterior=w.mid in ROADS
    floor=3 if exterior else 0 if w.mid==ARENA else 2
    def put(key,x,z,scale=1.,yaw=0.,sway=0.,raise_by=0.):
        h=int(w.hgt[int(z*2),int(x*2)])
        if h!=floor:
            return None
        y=(h+1)*.5+.027+raise_by
        props.append([key,x,y,z,scale,yaw,*([sway] if sway else [])])
        return y

    def lantern(x,z,size=1.,warm=False):
        y=put(WOODLAMP if warm else LANTERN,x,z,size)
        if y is not None:
            lights.append([x,y+( .59 if warm else 1.05)*size,z,4.4,8.3,0xffbb59ff])

    if exterior:
        river=w.mid=="M471"
        for x,z in ((12.0,14.7),(16.61,17.2),(22.8,13.7),(27.37,17.8),(33.52,16.17),
                    (46.35,17.03),(50.49,14.3),(64.7,17.58),(70.62,13.2),(76.45,16.56),
                    (81.65,14.02),(30.45,5.93),(50.19,6.32),(65.15,6.33),(76.47,5.32),(18.3,17.64),(30.27,14.56),(42.67,17.20),(52.06,16.33),(59.4,17.36),(66.94,17.79),(75.45,18.48),(81.6,17.55)):
            put(PINE if river or int(x)%3 else MAPLE,x,z,.86+.14*sin(x),.42*x,.024)
        for center,_,_ in w.branch_mouths:
            x=(center+.5)*.5
            put(BOULDER if river else MONUMENT,x-3.22,12.43,1.06,.34)
            put(BOULDER if river else ORE,x+3.39,12.61,.83,.51)
            lantern(x-2.1,12.14,.76)
            lantern(x+2.08,12.13,.80)
        for x in (12.66,18.38,25.06,32.54,40.20,50.12,56.64,63.86,73.31,83.17):
            put(BUSH,x,5.4+.75*cos(x*.13),.79,.16*x,.054)
    elif w.mid=="M482":
        for x,z,s in ((27.3,7.94,.87),(35.7,13.1,1.16),(39.89,10.35,1.01),
                      (45.82,16.99,.84),(47.49,12.34,1.11),(53.3,16.45,.96),(60.54,24.8,.87)):
            put(BOULDER,x,z,s,.39*x)
        for x,z in ((25.58,7.03),(34.39,12.34),(37.95,12.16),(45.05,14.8),(49.62,19.94),(60.84,26.02)):
            lantern(x,z,.79)
    elif w.mid=="M483":
        for x,z,s in ((34.6,10.23,1.08),(50.55,10.19,1.12),(55.35,14.31,.83),
                      (69.56,17.42,1.03),(76.49,21.34,1.15)):
            put(MONUMENT,x,z,s,.19*x,raise_by=.151 if x==34.6 else 0.)
        for x,z in ((31.86,8.91),(35.55,10.41),(49.03,10.07),(53.30,14.32),(72.36,18.08)):
            lantern(x,z,.82,True)
    elif w.mid=="M484":
        for x,z,s in ((32.82,9.89,.99),(38.91,11.51,1.12),(45.94,10.19,.93),
                      (50.37,21.01,.92),(56.87,21.29,1.1),(66.63,16.79,1.13)):
            put(ORE,x,z,s,.21*x)
        for x,z in ((26.12,8.82),(37.1,10.1),(44.51,9.46),(53.10,19.35),(59.24,21.88),(67.3,16.90)):
            lantern(x,z,.93,True)
    else:
        for x,z,s in ((22.3,40.0,1.17),(29.4,42.03,1.44),(39.6,41.62,1.34),(47.4,40.93,1.11)):
            put(MONUMENT,x,z,s,.27*x)
        for x,z in ((24.44,39.68),(34.04,40.51),(42.61,40.04),(46.98,40.07)):
            put(ORE,x,z,.87,.35*x)
            lantern(x-.63,z-.55,.84,True)
    return {"placements":props,"poolLights":lights,"hideStockScenery":True,
            **({} if exterior else {"renderPreset":"rt_hd2d_snake_den"})}


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials(repo)
    sources={key:build_diorama_mesh(key,key,size,main_component=True) for key,size in (
        (BOULDER,(2.03,1.04,1.44)),(MONUMENT,(1.20,2.19,.94)),(ORE,(1.48,.84,1.06))
    )}
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    proof={}
    for mid in MAPS:
        world,_=gm.make(mid)
        terrain,water,quads=scenery(gm,world)
        entry=dress(gm,world)
        entry["terrain"]=terrain
        if water:
            bank=mid=="M471"
            entry.update(water=water,waterSequence={"prefix":BANK_WATER if bank else STREAM,
                         "frames":64 if bank else 48,"seconds":18.9 if bank else 15.8})
        index[mid]=entry
        proof[mid]={"terrain_quads":quads,"props":len(entry["placements"]),"animated_water":water}
    manifest.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"river-lion-caves-layout.json").write_text(json.dumps({"maps":proof,"sources":sources},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
