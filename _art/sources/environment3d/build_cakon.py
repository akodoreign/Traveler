"""Create the Cakon riverbank, timber quays, market, and city gate."""

from copy import copy
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import box, shop_board
from build_iuchi_mines import MATS as SHARED
from build_iuchi_tower import ground_styles, lift_floor, tint_texture
from build_kaiu_kit import world_mesh
from cakon_huts import build_assets
from cakon_worlds import GROUPS, variant
from diorama_trees import MAPLE, PINE, build_diorama_mesh, falling_leaves
from dragon_inn_joinery import DOOR_MODELS
from export_coast import Geometry, STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
DECK="cakon_deck"
END="cakon_deck_ends"
SILT="cakon_silt"
GRASS="cakon_river_grass"
SETTS="cakon_market_setts"
PLASTER="cakon_ivory_plaster"
BLUE="cakon_crane_blue"
WATER="cakon_river"
BARGE="cakon_river_barge"
MATS={**SHARED,**{k:(k+".png",.94) for k in (DECK,END,SILT,GRASS,SETTS,PLASTER,BLUE)},
      WATER:(WATER+"00.png",.28)}
MODELS={
    "river": (("cakon_herb_cluster",(.48,.42,.42),40),("cakon_mooring_gear",(.96,.77,.83),46)),
    "city": (("cakon_fish_basket",(.81,.56,.47),43),("cakon_market_crock",(.50,.49,.66),42)),
}


def surfaces(group):
    specs=(
        (DECK,"cakon_cedar_deck_scan",(87,54,30),.057),
        (END,"cakon_cedar_deck_scan",(117,78,46),.062),
        (SILT,"cakon_river_silt_scan",(55,57,50),.069),
        (GRASS,"iuchi_frosted_meadow",(43,70,34),.064),
        (PLASTER,"cakon_plaster_scan",(151,132,102),.048),
        (BLUE,"iuchi_storm_woven_cloth",(27,50,86),.058),
    ) if group=="river" else (
        (SETTS,"cakon_stone_setts_scan",(66,74,82),.070),
        (PLASTER,"cakon_plaster_scan",(151,132,102),.048),
        (BLUE,"iuchi_storm_woven_cloth",(27,50,86),.058),
    )
    for key,source,rgb,contrast in specs:
        tint_texture(key,source,rgb,contrast)
    if group=="city":
        return
    z,x=np.mgrid[0:np.pi*2:256j,0:np.pi*2:256j]
    for i in range(32):
        t=i*np.pi/16
        long=np.sin(z*8.+x*2.+t+.55*np.sin(x*3.+z-t))
        fine=np.cos(z*13.-x*5.-2*t)
        glint=np.maximum(long,0.)**7
        rgb=np.array([31,82,88])+(long*4.1+fine*1.1+glint*3.5)[...,None]*[.58,1.04,1.18]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/"tex"/f"{WATER}{i:02d}.png")


def props(group,voxfile):
    sources={}
    for name,dimensions,resolution in MODELS[group]:
        key,points,colors,_,source=convert_prop(name,dimensions,resolution,lower=.025)
        white=(colors.min(axis=1)>177) & (np.ptp(colors,axis=1)<37)
        edge=((points[:,2]<3) | (points[:,1]<2) | (points[:,1]>points[:,1].max()-2))
        points,colors=points[~(white & edge)],colors[~(white & edge)]
        points-=points.min(axis=0)
        sources[name]=save(key,points,colors,np.asarray(dimensions)/(points.max(axis=0)+1),source,voxfile)
        voxel_asset(name)
    return sources


def fixtures(group):
    if group=="river":
        shop_board("cakon_harbour_sign","CAKON","HARBOUR","#30455b")
        return
    shop_board("cakon_herbs_sign","HERBS","TEA","#334e59")
    shop_board("cakon_armoury_sign","CRANE","ARMOURY","#2e4058")
    shop_board("cakon_music_sign","MUSIC","COURT","#32485a")
    booth=Geometry()
    for x in (-.89,.81):
        for z in (-.49,.43):
            box(booth,(x,z,0.),(.075,.075,1.97),"iuchi_beam")
    box(booth,(-.82,-.52,.82),(1.64,.50,.079),END)
    box(booth,(-.82,-.40,.59),(1.64,.113,.25),DECK)
    p=[(-1.03,-.66,1.76),(1.03,-.66,1.76),(1.03,.66,2.09),(-1.03,.66,2.09)]
    for q in (p,list(reversed(p))):
        booth.quad(q,[(x*.56,z*.68) for x,z,_ in q],BLUE)
    box(booth,(-1.03,-.688,1.66),(2.06,.058,.114),BLUE)
    export("cakon_market_stand",booth,MATS)
    canopy=Geometry()
    for x in (-1.33,1.25):
        for z in (-.61,.57):
            box(canopy,(x,z,0.),(.08,.08,2.08),"iuchi_beam")
    a=[(-1.57,-.71,1.9),(1.57,-.71,1.9),(1.57,.76,2.28),(-1.57,.76,2.28)]
    canopy.quad(a,[(x*.54,z*.70) for x,z,_ in a],BLUE)
    canopy.quad(list(reversed(a)),[(x*.54,z*.70) for x,z,_ in reversed(a)],BLUE)
    export("cakon_musicians_canopy",canopy,MATS)

    portal=Geometry()
    for z in (-.19,2.0):
        box(portal,(-.27,z,0.),(.56,.19,3.06),"iuchi_beam")
        box(portal,(-.31,z-.07,0.),(.63,.32,.32),"iuchi_slate")
    box(portal,(-.34,-.31,3.0),(.69,2.57,.30),"iuchi_beam")
    box(portal,(-.43,-.42,3.26),(.87,2.78,.145),BLUE)
    export("cakon_river_gate_frame",portal,MATS)
    grate=Geometry()
    for i in range(7):
        z=.04+i*.304
        box(grate,(-.044,z,.24),(.098,.083,2.70),"iuchi_beam")
        box(grate,(-.049,z+.012,.09),(.105,.056,.19),"iuchi_iron")
    for y in (.45,1.18,1.93,2.62,2.93):
        box(grate,(-.068,-.011,y),(.142,1.982,.086),END)
        for z in (.062,.670,1.278,1.886):
            box(grate,(-.081,z,y+.022),(.021,.038,.043),"iuchi_iron")
    export("cakon_portcullis",grate,MATS)


def geometry(gm,w):
    city=w.mid in GROUPS["city"]
    styles={**ground_styles(gm),gm.GRASS2:GRASS,gm.GRASS3:GRASS,gm.DIRT:SILT,gm.DIRT3:SILT,gm.ROAD:SETTS if city else SILT,
            gm.STONEW:SETTS if city else "iuchi_slate",gm.PLANK:DECK,gm.WOOD:DECK,
            gm.DARKWOOD:"iuchi_beam",gm.PLASTER:PLASTER,gm.ROOF:BLUE}
    water=w.blk==gm.WATER
    art=copy(w)
    if water.any():
        art.blk=np.where(water,gm.DIRT,w.blk)
        art.hgt=np.where(water,w.hgt-1,w.hgt)
    mesh=world_mesh(gm,art,styles)
    lift_floor(mesh,{SILT,GRASS,DECK,SETTS},.056)
    if water.any():
        _,fluid=grid_surfaces(water.astype(int),w.hgt,("",WATER),wall_style=SILT,fluid=1)
        export(w.mid.lower()+"_cakon_river",fluid,MATS)
        box(mesh,(0.,-.051,.99),(w.w*.5,.061,.51),SILT)
    if w.mid=="M415":
        # Deck boards line the working quay and a separate outfitted herb barge.
        for bz in range(13,25):
            z=bz*.5+.05
            seams=[1.0,10.0+bz%3,22.0+bz%4,35.,49.0+bz%3,61.0+bz%4,75.4]
            for i,(a,b) in enumerate(zip(seams,seams[1:])):
                box(mesh,(a+.012,z,2.070),(b-a-.020,.434,.016),END if (i+bz)%5==0 else DECK)
        for x in range(7,74,4):
            box(mesh,(float(x),5.39,1.46),(.119,.137,.82),"iuchi_beam")
    if w.mid in ("M415","M416","M883"):
        for wall in (o for o in w.objs if o["t"]=="fill" and o["h"]>=6 and o["w"]>=9 and o["d"]>=5
                     and o["blk"] in (gm.WOOD,gm.DARKWOOD,gm.PLASTER)):
            x,y,z=(wall[a]*.5 for a in ("x","y","z"))
            width=wall["w"]*.5
            height=wall["h"]*.5
            for offset in (.13,width-.19):
                box(mesh,(x+offset,z-.087,y),(.119,.12,height),"iuchi_beam")
            for h in (.14,height-.23):
                box(mesh,(x-.02,z-.092,y+h),(width+.05,.12,.087),END)
            for offset in np.arange(.5,width-.28,.74):
                box(mesh,(x+offset,z-.064,y+height-.66),(.052,.083,.42),"iuchi_beam")
    if w.mid=="M417":
        for z in (4.96,10.94):
            for x in np.arange(13.24,43.1,1.45):
                box(mesh,(float(x),z,2.03),(.093,.144,2.49),"iuchi_beam")
            box(mesh,(13.21,z-.048,4.34),(29.86,.227,.204),BLUE)
        for x in (54.94,57.01):
            for z,span in ((0.,8.5),(10.50,w.d*.5-10.5)):
                box(mesh,(x,z,2.),(.11,span,.28),END)
                for base in np.arange(z+.70,z+span-.12,1.22):
                    box(mesh,(x-.02,float(base),2.22),(.145,.084,3.16),"iuchi_beam")
            for y in (5.17,7.76):
                box(mesh,(x-.13,4.13,y),(.26,7.89,.156),"iuchi_beam")
        for side in (-1,1):
            x=56.+side*1.70
            roof=[(56.,3.42,10.67),(56.,12.60,10.67),(x,12.96,9.49),(x,3.07,9.49)]
            if side<0:
                roof.reverse()
            for face in (roof,list(reversed(roof))):
                mesh.quad(face,[(z*.53,x*.77) for x,z,_ in face],BLUE)
            box(mesh,(x-.060,3.05,9.42),(.124,9.92,.090),END)
        box(mesh,(55.90,3.27,10.62),(.20,9.44,.13),"iuchi_beam")
    return mesh


def layout(gm,w):
    mid=w.mid
    placements,lights,doors,leaves=[],[],[],[]
    result={"placements":placements,"poolLights":lights,"doors":doors,"leafDrift":leaves}
    def put(name,x,z,size=1.,yaw=0.,sway=0.,level=None):
        y=(int(w.hgt[z,x])+1)*.5+.028 if level is None else level
        point=[x*.5+.25,y,z*.5+.25]
        placements.append([name,*point,size,yaw,*([sway] if sway else [])])
        return point
    def lamp(x,z,scale=.91):
        a,y,b=put("iuchi_fitted_andon",x,z,scale)
        lights.append([a,y+.51*scale,b,4.03,1.47])
    def door(cut,event):
        x,y,z=(cut[k]*.5 for k in ("x","y","z"))
        doors.append({"x":x,"y":y,"z":z-.08,"grade":y-.50,"event":event,
                      "stoop":"dragon_inn_stoop_half","models":DOOR_MODELS})

    if mid=="M414":
        for x in range(11,108,7):
            size=.84+x%4*.16
            tree=PINE if x%4 else MAPLE
            point=put(tree,x,27+x%4,size,x*.31,.019 if tree==MAPLE else .013)
            if tree==MAPLE:
                leaves.extend(falling_leaves(point,size,x))
        for x,z in ((37,12),(43,12),(52,16),(55,15),(59,14),(68,12),(79,12),(88,12)):
            put("cakon_herb_cluster",x,z,.97+x%3*.18,.18*x,.065)
        for x in range(22,106,5):
            put("iuchi_brook_reeds",x,10,.74+x%4*.12,.23*x,.109)
        put("iuchi_valley_pack_basket",47,13,.81,.33)
        for x in (67,75,83):
            put("cakon_riverside_hut",x,25,1.0)
    elif mid=="M415":
        for cut,event in zip(sorted((o for o in w.objs if o.get("blk")==gm.VOID),key=lambda o:o["x"]),
                             (88,89,None),strict=True):
            door(cut,event)
        for x,z in ((37,23),(57,23),(77,23),(94,24),(121,23)):
            lamp(x,z)
        put(BARGE,39,8,1.,level=1.34)
        for x,z,y in ((53,12,2.04),(66,12,2.04),(87,12,2.04),(109,12,2.04)):
            put("cakon_mooring_gear",x,z,.94,.31*x,level=y)
        put("cakon_harbour_sign",42,16,.88)
        put("iuchi_valley_pack_basket",40,8,.69,.15,level=1.82)
        for x,z in ((51,24),(72,24),(106,23),(111,24)):
            put("salt_crate",x,z,1.13,.37*x)
        for x,z in ((48,24),(76,24),(108,23),(112,24)):
            put("cakon_staved_barrel",x,z,.98,.34*x)
    elif mid=="M416":
        for cut,event in zip(sorted((o for o in w.objs if o.get("blk")==gm.VOID),key=lambda o:o["x"]),
                             (None,93,94,None),strict=True):
            door(cut,event)
        for x in (34,54,74,94,116,133):
            lamp(x,22)
        for i,x in enumerate((57,69,81,93,105)):
            put("cakon_market_stand",x,11,.85+(i%3)*.075)
            for k in (-1,1):
                put("cakon_fish_basket" if i%2==0 else "cakon_market_crock",
                    x+k,10,.70,.19*x,level=2.76)
        put("cakon_musicians_canopy",118,12,1.30)
        for x,z,name in ((63,19,"cakon_herbs_sign"),(86,21,"cakon_armoury_sign"),(124,11,"cakon_music_sign")):
            put(name,x,z,.89,.04)
    elif mid=="M417":
        put("cakon_river_gate_frame",109,17,1.,level=2.)
        put("cakon_river_gate_frame",114,17,1.,level=2.)
        result["portcullises"]=[{"model":"cakon_portcullis","x":55.38,"y":2.02,"z":8.51,
                                 "event":113,"lift":2.88,"blockX":111,"blockZ":17,"width":4}]
        for x,z in ((29,20),(48,20),(64,20),(82,20),(104,17),(108,21),(116,21),(139,22)):
            lamp(x,z,.89)
        for x,z in ((39,19),(58,20),(75,14),(85,19),(103,13)):
            put("cakon_market_crock",x,z,.90,.37*x)
    elif mid=="M883":
        for x in (19,39,56,73,89,112):
            lamp(x,86,1.12)
            put("cakon_market_crock",x+3,88,.95,.41*x)
        for x in (39,91):
            put("cakon_market_stand",x,87,1.12)
    if mid in GROUPS["river"]:
        result.update({"water":mid.lower()+"_cakon_river",
                       "waterSequence":{"prefix":WATER,"frames":32,"seconds":16.5}})
    return result


def main(repo,group):
    _,_,gm,_,_=variant(repo,group)
    import voxfile

    surfaces(group)
    sources=props(group,voxfile)
    if group=="river":
        build_assets()
        sources[BARGE]=build_diorama_mesh(BARGE,BARGE,(7.55,1.04,2.64),align_x=True)
    fixtures(group)
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    details={}
    for mid in GROUPS[group]:
        w,events=gm.make(mid)
        tag=mid.lower()+"_cakon"
        export(tag,geometry(gm,w),MATS)
        index[mid]={"terrain":tag,**layout(gm,w)}
        details[mid]={"events":len(events.ev) if events else 0,"placements":len(index[mid]["placements"])}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/f"cakon-{group}-layout.json").write_text(json.dumps({"maps":details,"sources":sources},indent=2),encoding="utf-8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve(),sys.argv[2])
