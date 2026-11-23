"""Build the winter river, walkable rice barge, and Floating Flowers village."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_clan_castles import roof
from build_furnace import grid_surfaces
from build_hoshi_stall import box, shop_board
from build_iuchi_tower import lift_floor, tint_texture
from build_kaiu_kit import MATS as SHARED, world_mesh
from build_town_doors import find_facades
from diorama_trees import build_diorama_mesh
from export_coast import Geometry, STAGE, export
from publish_castle_gates import resource_files
from winter_river_worlds import MAPS, variant

HERE=Path(__file__).resolve().parent
ROAD="winter_river_ochre_road"
ICE="winter_river_bank_ice"
SNOW="winter_river_powder_snow"
DECK="winter_river_deck"
BEAM="winter_river_cedar"
TILE="winter_village_indigo_tile"
PLASTER="winter_village_cream_plaster"
RED="winter_shrine_cinnabar"
SHALE="winter_river_shale"
PAPER="winter_village_paper"
AMBER="winter_village_lamp_paper"
WATER="winter_river_water"
STORM="winter_jetty_storm_water"
PINE="castle_snow_pine"
REED="winter_river_frost_reed"
FOX="winter_river_fox_offering"
BALE="winter_river_rice_bales"
SKIFF="floating_flowers_work_skiff"
RIBBONS="floating_flowers_ribbon_wares"
FISH="floating_flowers_paper_fish"
MATERIALS={**SHARED, **{key:(key+".png",.92) for key in (ROAD,ICE,SNOW,DECK,BEAM,TILE,PLASTER,RED,SHALE,PAPER)},
           WATER:(WATER+"00.png",.33),STORM:(STORM+"00.png",.39),"glow":(AMBER+".png",.57)}
MODELS={
    REED:("rokugan_frosted_river_reeds",(.61,.73,.46),False),
    FOX:("rokugan_winter_fox_offering",(.56,.97,.65),False),
    BALE:("rokugan_barge_rice_bales",(1.43,.87,.88),True),
    SKIFF:(SKIFF,(4.92,.99,1.71),True),
    RIBBONS:(RIBBONS,(.96,.38,.64),True),
    FISH:(FISH,(.37,.38,.22),True),
}
SHARE=(PINE,"cakon_river_barge","cakon_fish_basket","cakon_staved_barrel","cakon_mooring_gear",
       "smooth_coast_salt_crate","iuchi_fitted_andon","cakon_hamlet_hut","cakon_market_crock",
       "cakon_paddy_red_stone","town_door_frame","town_door_leaf","town_door_stoop_half","town_door_stoop_full")


def material_maps():
    for key,scan,color,contrast in (
        (ROAD,"cakon_paddy_mud_scan",(80,45,28),.13),
        (ICE,"iuchi_frosted_meadow",(91,152,198),.105),
        (SNOW,"iuchi_frosted_meadow",(207,229,255),.052),
        (DECK,"cakon_cedar_deck_scan",(109,60,31),.14),
        (BEAM,"kaiu_cedar",(36,20,27),.13),
        (TILE,"kawara_bluegrey",(21,49,99),.11),
        (PLASTER,"cakon_plaster_scan",(184,137,92),.07),
        (RED,"kaiu_cedar",(168,28,35),.13),
        (SHALE,"iuchi_riverbed_stone",(49,74,112),.14),
        (PAPER,"kaiu_plaster",(212,161,82),.071),
    ):
        tint_texture(key,scan,color,contrast)
    tint_texture(AMBER,"kaiu_plaster",(255,161,42),.065)
    z,x=np.mgrid[0:2*pi:256j,0:2*pi:256j]
    for water,storm in ((WATER,False),(STORM,True)):
        for phase in range(32):
            t=phase*pi/16
            roll=np.sin(z*(6 if storm else 3)+x+(.66*np.sin(2*x-z))+t)
            fine=np.sin(z*9-x*3+2*t)
            crest=np.clip(roll,0,1)**9
            rgb=np.array([23,49,87] if storm else [16,64,118])+(roll*5+fine*1.15+crest*(12 if storm else 4.5))[...,None]*[.70,.92,1.14]
            Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/"tex"/f"{water}{phase:02}.png")


def copy_shared(repo):
    native=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    needed={"shared":{"placements":[[part] for part in SHARE]}}
    for path,content in resource_files(native,needed).items():
        target=STAGE/path
        if not target.is_file() or target.read_bytes()!=content:
            target.write_bytes(content)


def panels(geom, points, style, scale=1.):
    geom.quad(points,[(p[0]/scale,(p[1]+p[2]*.72)/scale) for p in points],style)


def lantern_post():
    mesh=Geometry()
    box(mesh,(-.21,-.18,0),(.42,.36,.10),SHALE,.67)
    box(mesh,(-.069,-.062,.081),(.138,.124,1.77),BEAM,.85)
    box(mesh,(-.18,-.16,1.76),(.36,.32,.10),RED,.73)
    box(mesh,(-.129,-.116,1.84),(.258,.232,.37),"glow",.83)
    for x in (-.15,.128):
        for z in (-.135,.112):
            box(mesh,(x,z,1.84),(.030,.030,.40),BEAM)
    roof(mesh,-.214,0,2.24,.428,.40,.14,BEAM,TILE)
    export("floating_flowers_river_post",mesh,MATERIALS)


def stalls():
    for bar,trim in (("floating_flowers_ribbon_stall",RED),("floating_flowers_fish_stall",TILE)):
        mesh=Geometry()
        for x in (-1.05,.97):
            for z in (-.47,.48):
                box(mesh,(x,z,0),(.087,.095,1.94),BEAM)
        box(mesh,(-.99,-.54,.81),(1.98,.77,.093),DECK,.83)
        box(mesh,(-.99,.12,.53),(1.98,.117,.27),BEAM,1.2)
        box(mesh,(-1.11,-.60,1.70),(2.22,.06,.17),trim)
        panels(mesh,[(-1.12,-.57,1.82),(1.12,-.57,1.82),(1.12,.62,2.12),(-1.12,.62,2.12)],trim,1.07)
        export(bar,mesh,MATERIALS)


def barge_mesh():
    mesh=Geometry()
    cx,cz=28.50,8.25
    # Eleven fitted hull stations enclose the old 17 by 4.5 metre walkable deck.
    stations=((-9.55,.10,.41),(-8.90,1.35,.22),(-8.25,2.39,.105),(-6.75,2.67,.032),
              (-4.65,2.75,0.),(-1.80,2.79,0.),(1.8,2.73,0.),(4.65,2.68,.024),
              (6.80,2.57,.060),(8.46,2.31,.16),(9.52,.29,.34))
    levels=((.72,.41),(1.12,.68),(1.49,.87),(1.86,.95),(2.23,1.))
    for side in (-1,1):
        for a,b in zip(stations,stations[1:]):
            for j,((y,k),(Y,K)) in enumerate(zip(levels,levels[1:])):
                def point(s,h,r):
                    x,breadth,lift=s
                    return cx+x,cz+side*breadth*r,h+lift
                p=[point(a,y,k),point(b,y,k),point(b,Y,K),point(a,Y,K)]
                if side>0:
                    p.reverse()
                panels(mesh,p,BEAM if j in (0,3) else DECK,1.72)
                if j==3:
                    p2=[point(a,Y-.03,K*1.006),point(b,Y-.03,K*1.006),
                        point(b,Y+.092,K*1.012),point(a,Y+.092,K*1.012)]
                    panels(mesh,p2 if side<0 else list(reversed(p2)),RED,1.11)
    for i,row in enumerate(np.arange(6.03,10.46,.284)):
        seams=(20.01,25.+.21*(i%3),30.72+.18*(i%2),36.99)
        for a,b in zip(seams,seams[1:]):
            box(mesh,(a+.013,row,1.98),(b-a-.024,.264,.08),DECK,1.33)
    for x in (20.0,36.94):
        box(mesh,(x-.13,5.93,2.035),(.17,4.60,.105),BEAM)
    # The short stern house sits on the registered cabin footprint.
    box(mesh,(36.09,6.62,2.06),(.89,3.53,1.36),BEAM,.87)
    box(mesh,(36.03,7.29,2.60),(.068,1.52,.53),"glow",.71)
    for z in (6.61,7.27,8.80,10.08):
        box(mesh,(35.96,z,2.055),(.11,.105,1.38),RED)
    roof(mesh,35.76,8.34,3.43,1.55,3.95,.51,BEAM,TILE)
    return mesh


def snow_cover(mesh,x,z,y,width,length,rise):
    half=length*.5
    for side in (-1,1):
        for row in range(7):
            a,b=row/7.,(row+1)/7.
            def section(t):
                reach=.17*(1.-t)
                ridge=y+rise*t**1.64-.095*sin(pi*t)+.151
                depth=z+side*(half*(1.-t)-.053)
                return (x-reach+.055,depth,ridge),(x+width+reach-.066,depth,ridge)
            left,right=section(a)
            outer,inner=section(b)
            panel=[left,right,inner,outer]
            panels(mesh,panel if side<0 else panel[::-1],SNOW,2.4)


def fitted_roofs(gm,world,mesh):
    for course in getattr(world,"river_roofs",()):
        first,last=course[0],course[-1]
        x,z=first["x"]*.5,(first["z"]+first["d"]*.5)*.5
        h=(first["y"]+.36)*.5
        w,d=first["w"]*.5,first["d"]*.5
        rise=max(.52,(last["y"]-first["y"])*.49+.27)
        roof(mesh,x,z,h,w,d+.14,rise,BEAM,TILE)
        if world.mid=="M422":
            snow_cover(mesh,x,z,h,w,d+.14,rise)
            front=z-d/2-.057
            for xx in (x+.35,x+w-.78):
                sill=h-.94
                box(mesh,(xx-.061,front-.027,sill-.061),(.56,.092,.57),BEAM,.79)
                box(mesh,(xx,front-.058,sill),(.43,.067,.45),"glow",.47)
                for offset in (.135,.277):
                    box(mesh,(xx+offset,front-.072,sill),(.024,.024,.45),BEAM)
                for offset in (.14,.287):
                    box(mesh,(xx,front-.072,sill+offset),(.43,.024,.024),BEAM)
        if len(course)<2:
            continue
        # A narrow timber eave line and actual shoji panels read at gameplay distance.
        front=(first["z"]+1)*.5-.046
        for x0 in np.arange(x+.47,x+w-.33,.95):
            zc=max(0,min(world.d-1,int(front*2)))
            xc=max(0,min(world.w-1,int(x0*2)))
            floor=(world.hgt[zc,xc]+1)*.5
            column_bottom=max(floor+.54,h-1.92)
            box(mesh,(x0,front-.057,column_bottom),(.062,.101,max(.09,h-column_bottom-.07)),BEAM,1.02)


def ground(gm,w):
    water=w.blk==gm.WATER
    # Stage the winter battle beside the same broad river as exploration.
    if w.mid=="M888":
        water[94:105]=True
    ground=copy(w)
    ground.blk=np.where(water,gm.DIRT,w.blk)
    ground.hgt=np.where(water,w.hgt-1,w.hgt)
    styles={gm.SNOW:SNOW,gm.ROAD:ROAD,gm.DIRT:ROAD,gm.GRASS3:ICE,gm.PLANK:DECK,gm.WOOD:DECK,
            gm.DARKWOOD:BEAM,gm.ROOF:TILE,gm.SHOJI:PAPER,gm.PLASTER:PLASTER,gm.STONEW:SHALE}
    mesh=barge_mesh() if w.mid=="M423" else world_mesh(gm,ground,styles)
    lift_floor(mesh,{SNOW,ROAD,ICE,DECK},.077 if w.mid!="M423" else 0.)
    fitted_roofs(gm,w,mesh)
    if w.mid=="M422":
        # Keep the tracks beside the story prompt and clear of the road lane.
        for i in range(13):
            x=51.70+i*.21
            z=11.6+i*.15+.062*sin(i)
            box(mesh,(x,z,2.087),(.054,.044,.007),SHALE,.53)
            for dx in (-.012,.026):
                box(mesh,(x+dx,z+.026,2.090),(.021,.020,.006),SHALE,.53)
        for x in (10.8,28.2,45.4,63.3,76.6):
            box(mesh,(x,4.89,1.51),(.56,.21,.14),ICE)
    if w.mid in ("M424","M889"):
        # Run each low wale along the actual dry edge and leave the jetty joins open.
        shoreline=np.argmax(~water,axis=0)
        ordinary=int(np.bincount(shoreline).argmax())
        edges=np.flatnonzero(np.diff(np.r_[False,shoreline==ordinary,False].astype(np.int8)))
        for start,end in zip(edges[::2],edges[1::2],strict=True):
            if end-start<2:
                continue
            x,z,width=start*.5,ordinary*.5,(end-start)*.5
            y=2.002 if w.mid=="M424" else .522
            box(mesh,(x,z-.045,y),(width,.118,.13),BEAM,.92)
            for xx in np.arange(x+.66,x+width-.3,2.8):
                box(mesh,(xx,z-.079,y),(.145,.17,.30),BEAM,1.0)
    key=None
    if water.any():
        key=STORM if w.mid=="M889" else WATER
        _,fluid=grid_surfaces(water.astype(int),w.hgt,("",key),wall_style=SHALE,fluid=1)
        if w.mid in ("M422","M423","M424","M888"):
            # Extend the scenery water past the cutaway while leaving travel bounds in the world file.
            height=max(float(p[2]) for p in fluid.vertices)
            lift=.104 if w.mid=="M888" else .065
            fluid.vertices=[np.asarray(point)+[0.,0.,lift] for point in fluid.vertices]
            y=height+lift
            border=((-.0,-12.,w.w*.5,0.),)
            if w.mid=="M423":
                border=(*border,(-15.,-12.,0.,w.d*.5+12.),(w.w*.5,-12.,w.w*.5+15.,w.d*.5+12.),
                        (0.,w.d*.5,w.w*.5,w.d*.5+12.))
            for x,z,u,v in border:
                points=[(x,z,y),(u,z,y),(u,v,y),(x,v,y)]
                # The native grid uses 4.7 cells per repeat, at .5 m each.
                fluid.quad(points,[(a/2.35,b/2.35) for a,b,_ in points],key)
        export(w.mid.lower()+"_winter_river_water",fluid,MATERIALS)
    return mesh,key


def dress(gm,w,catalog):
    row={"placements":[],"poolLights":[]}
    def put(key,x,z,size=1.,yaw=0.,sway=0.,*,y=None):
        assert 0<=x<w.w*.5 and 0<=z<w.d*.5,(w.mid,x,z)
        if y is None:
            y=(int(w.hgt[int(z*2),int(x*2)])+1)*.5+.025
        row["placements"].append([key,x,y,z,size,yaw,*([sway] if sway else [])])
        return y

    def lamp(x,z,scale=1.):
        y=put("floating_flowers_river_post",x,z,scale)
        row["poolLights"].append([x,y+2.04*scale,z,4.5,4.5,0xffb752ff])

    for o in getattr(w,"river_fixtures",()):
        x,z=o["x"]*.5+.25,o["z"]*.5+.25
        if o["fbtype"]==20:
            if w.mid=="M424" and o["x"]%3==0:
                continue
            size=(.72+.19*(o["x"]%5)/4)*(1.16 if o["fbparam"]==gm.TREE_L else 1.)
            put(PINE,x,z,size,.37*x,.014)
        else:
            lamp(x,z,.84 if w.mid=="M424" else .75)
    if w.mid=="M422":
        for x in np.arange(2.8,w.w*.5-1.9,1.65):
            put(REED,float(x),5.38+.09*sin(x),.78+.17*sin(x*.77),.28*x,.041)
        for x,z,size in ((54.85,13.49,.88),(59.44,13.41,.89)):
            put(FOX,x,z,size,.14*x)
            put("cakon_market_crock",x+.22,z+.15,.53,.37)
        for x,z in ((16.6,6.01),(26.3,6.17),(45.2,6.06),(63.3,6.30),(71.0,6.20)):
            put("cakon_paddy_red_stone",x,z,.68,.30*x)
        row["doors"]=find_facades(gm,w,catalog["event"])
    elif w.mid=="M423":
        for x,z,scale in ((23.02,9.78,1.01),(27.01,9.76,.95),(34.02,9.78,.97)):
            put(BALE,x,z,scale,.17*(x%3))
        for x,z in ((21.34,6.48),(32.16,9.48),(35.12,7.04)):
            y=put("iuchi_fitted_andon",x,z,.94)
            row["poolLights"].append([x,y+.47,z,4.06,1.42])
        put("cakon_mooring_gear",36.44,6.38,.86,.3)
        put("cakon_market_crock",25.81,9.78,.58,1.2)
    elif w.mid=="M424":
        for x,z,heading in ((22.7,3.37,.05),(41.54,2.92,-.13)):
            put(SKIFF,x,z,1.03,heading,y=1.22)
        put("cakon_river_barge",66.75,2.84,.79,.015,y=1.18)
        for x,z in ((21.0,4.95),(43.6,4.98),(65.4,5.39),(69.1,5.37)):
            put("cakon_mooring_gear",x,z,.78,.11*x)
        for x,z,name in ((34.2,12.91,"floating_flowers_ribbon_stall"),(38.4,12.91,"floating_flowers_fish_stall")):
            y=put(name,x,z)
            for dx in (-.46,.43):
                put(RIBBONS if "ribbon" in name else "cakon_fish_basket",x+dx,z-.11,.92,dx*.55,y=y+.90)
        for x in (29.,32.10,35.96):
            put(RIBBONS,x,14.18,.91,.13+x*.04)
        for x,z in ((48.3,13.37),(52.8,13.66),(55.9,10.9),(56.1,14.14)):
            put("smooth_coast_salt_crate",x,z,.93,.06*x)
        for x,z in ((48.99,14.05),(57.10,13.6),(24.8,14.18)):
            put("cakon_staved_barrel",x,z,.96,x*.63)
        put("cakon_hamlet_hut",70.24,16.48,.81,-.04)
        put("floating_flowers_wanted_board",15.78,7.19,1.,.09)
        for x in (61.0,62.4,64.1):
            put(FISH,x,14.37,.96,.26*x,.093,y=4.61)
        row["doors"]=find_facades(gm,w,catalog["event"])
    elif w.mid=="M888":
        for x in np.arange(3.0,62.,2.55):
            put(REED,float(x),47.13+.26*sin(x),.81+.13*cos(x),.12*x,.052,y=.51)
        for x,z in ((20.6,36.81),(25.1,36.71),(46.0,37.1),(49.3,37.0)):
            put("cakon_paddy_red_stone",x,z,.94,.44*x)
    else:
        for x,z,n in ((23.5,44.7,"cakon_staved_barrel"),(41.6,45.8,"smooth_coast_salt_crate"),
                        (26.4,43.99,"cakon_mooring_gear"),(36.4,43.8,"cakon_staved_barrel")):
            put(n,x,z,.95,.36*x)
        for x in (24.31,39.75):
            lamp(x,39.94,.93)
    return row


def main(repo):
    _,_,gm,_,_=variant(repo)
    copy_shared(repo)
    material_maps()
    sources={name:build_diorama_mesh(name,src,dim,align_x=align,
             main_component=name in (SKIFF,FOX)) for name,(src,dim,align) in MODELS.items()}
    lantern_post()
    stalls()
    shop_board("floating_flowers_wanted_board","WANTED","THE WAVE GIRL","#7f2d34")
    ext=repo/"_tools/rpgcobo-tool/project/data/map.json"
    catalog=json.loads(ext.read_bytes())
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    report={}
    for mid in MAPS:
        world,events=gm.make(mid)
        geo,water=ground(gm,world)
        terrain=mid.lower()+"_winter_river_scene"
        export(terrain,geo,MATERIALS)
        row=dress(gm,world,catalog[mid])
        row["terrain"]=terrain
        if water:
            row.update(water=mid.lower()+"_winter_river_water",
                       waterSequence={"prefix":water,"frames":32,"seconds":9.6 if water==STORM else 17.8})
        index[mid]=row
        report[mid]={"events":len(events.ev) if events else 0,"placements":len(row["placements"]),
                     "terrain_quads":len(geo.faces),"water":water,"doors":len(row.get("doors",()))}
    manifest.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"cakon-winter-river-layout.json").write_text(json.dumps({"maps":report,"sources":sources},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())

