"""Build the siege cellar and its servants' stair over M153's native layout."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"stone-relief"))
import build_hida_relief as relief
from build_hoshi_stall import box
from export_coast import Geometry,export

h=relief.initial
base=h.base
STAGE=HERE/"native_environment"
TEX=STAGE/"tex"
LAND="m153_hida_siege_cellar"
FRAME=LAND+"_door_frame"
LEAF=LAND+"_door_leaf"
FLOOR=LAND+"_flagstone"
VARNISH=LAND+"_cedar"
LACQUER=LAND+"_rust"
METAL=LAND+"_iron"
AMBER=LAND+"_amber"
BARREL="cakon_staved_barrel"
DOOR={"event":1,"x":46.24,"y":1.525,"z":8.225,"models":[FRAME,LEAF],
      "alternateOpen":[{"lvar":"G275","op":"==","rvar":True}]}
ROUTE=((34,18),(44,18),(84,18),(92,18))
CHECKPOINT=(66,10,23)


def commands(tree):
    if isinstance(tree,dict):
        yield tree
        for part in tree.values():
            yield from commands(part)
    elif isinstance(tree,list):
        for part in tree:
            yield from commands(part)


def check_catalog(cat):
    entry=cat["M541"]["event"]["#15#"]
    row=cat["M153"]
    event=row["event"]
    exit_=event["#1#"]
    assert entry["pos"]==[96,4,13,2]
    assert entry["reqs0"]==[{"lvar":"G1644","op":"==","rvar":True}]
    assert entry["page"][1]["reqs"]==[{"lvar":"G273","op":"==","rvar":True}]
    assert any(c.get("cmd")=="cmd_mapmove" and c["dest"]=={"mapid":"M153","pos":[17.0,None,9.0,0.0]}
               for c in commands(entry))
    assert exit_["pos"]==[92,3,18,2] and exit_["reqs0"]==DOOR["alternateOpen"]
    assert exit_["page"][0]["trigger"]==5
    assert any(c.get("cmd")=="cmd_mapmove" and c["dest"]=={"mapid":"M501","pos":[8.0,None,17.0,0.0]}
               for c in commands(exit_))
    assert event["#5#"]["pos"]==[44,3,18,2]
    assert any(c.get("cmd")=="cmd_battle1" and c["mapid"]=="M001" and c["gid"]==23
               for c in commands(event["#5#"]))
    assert any(c["gid"]==23 and c["mapid"]=="M815" for c in cat["M001"]["encount"])
    assert event["#10#"]["pos"]==[84,3,18,2]
    assert tuple(event["#12#"]["pos"][:3])==CHECKPOINT


def materials(w,route):
    # Reuse the tested slate and continuous stone style from the Hida revision,
    # and make the cellar's floor and aged joinery darker and warmer.
    common=HERE.parent/"stone-relief/native_environment/tex"
    palette={k:(k+"_relief.png",rough) for k,(_,rough) in relief.PALETTE.items()}
    normal="hida_cave_relief_normal.png"
    (TEX/normal).write_bytes((common/normal).read_bytes())
    for file,_ in palette.values():
        (TEX/file).write_bytes((common/file).read_bytes())
    photo=np.asarray(Image.open(base.SOURCE_IMAGES/"rock_01_diff_1k.jpg").convert("L"),dtype=float)
    detail=gaussian_filter(photo,2.7,mode="wrap")
    broad=gaussian_filter(photo,7.5,mode="wrap")
    scan=.62*detail+.38*broad
    tint=np.clip((scan-np.median(scan))/(2.7*scan.std()),-.67,.75)
    wood_src=np.asarray(Image.open(base.SOURCE_IMAGES/"kaiu_cedar.png").convert("L").resize((1024,1024)),dtype=float)
    wood=gaussian_filter(wood_src,2.9,mode="wrap")
    plank=np.clip((wood-np.median(wood))/(2.9*wood.std()),-.69,.80)
    for name,color,rel,rough in ((VARNISH,[99,50,31],plank,.86),(LACQUER,[146,36,25],plank,.83),
                                 (METAL,[42,34,43],tint,.80),(AMBER,[188,98,26],tint,.77)):
        base.write_image(name+".png",np.array(color)*(1+.39*rel[...,None]))
        palette[name]=(name+".png",rough)

    mask=np.zeros_like(w.hgt,dtype=bool)
    for x,z in route:
        mask[z,x]=True
    reach=distance_transform_edt(~mask)
    z,x=np.meshgrid(np.arange(928)*w.d/928,np.arange(2048)*w.w/2048,indexing="ij")
    way=map_coordinates(reach,(z-.5,x-.5),order=1,mode="nearest")
    light=np.exp(-np.square(way/2.24))
    grain=map_coordinates(scan,(z*27.8,x*32.1),order=1,mode="grid-wrap")
    grain=np.clip((grain-np.median(grain))/(2.8*grain.std()),-.71,.8)
    vx=x+.15*np.sin(z*.63)+.09*np.cos(x*.37-z*.59)
    vz=z+.13*np.cos(x*.75+z*.4)
    row=np.floor(vz/2.02)
    joint=np.maximum(abs((vz/2.02)%1.-.5),abs(((vx+row*.87)/2.91)%1.-.5))
    gap=np.clip((joint-.454)*25.,0.,.64)
    stone=.88+.12*np.cos(row*1.95+np.floor((vx+row*.87)/2.91)*1.13)
    cold,hot=np.array([25.,31.,57.]),np.array([83.,50.,35.])
    pigment=cold+(hot-cold)*(.87*light[...,None])
    base.write_image(FLOOR+".png",pigment*(stone*(1.-gap*.52)*(1+.48*grain))[...,None])
    palette[FLOOR]=(FLOOR+".png",.74)
    normals={k:normal for k in (h.NAVY,h.COBALT,h.SCREE,h.INNER,h.BRICK,h.SLATE,FLOOR)}
    return palette,normals


def stairs(geo,x_outer,x_inner,zc,half,n,rise):
    pitch=(x_inner-x_outer)/n
    for i in range(n):
        a=min(x_outer+i*pitch,x_outer+(i+1)*pitch)
        y=1.532+rise*(n-i)/n
        box(geo,(a,zc-half,1.528),(abs(pitch)+.018,2*half,y-1.528),h.BRICK,1.4)
        box(geo,(a+.022,zc-half+.015,y-.017),(abs(pitch)-.012,2*half-.030,.022),h.SLATE,1.1)
        bullnose=a+.023 if pitch<0 else a+pitch-.031
        box(geo,(bullnose,zc-half+.01,y-.013),(.031,2*half-.02,.017),AMBER,1.78)


def cross_brace(geo,x,z,y,span):
    for side in (-1,1):
        a=z+side*span*.5
        box(geo,(x-.135,a-.13,y),(.34,.26,2.11),VARNISH,.99)
        box(geo,(x-.161,a-.15,y+.21),(.40,.30,.14),LACQUER,1.03)
        box(geo,(x-.144,a-.138,y+1.95),(.37,.29,.12),METAL,1.42)
    box(geo,(x-.16,z-span*.5-.16,y+2.04),(.39,span+.32,.255),VARNISH,1.33)
    box(geo,(x-.173,z-span*.5-.13,y+2.19),(.41,span+.26,.071),LACQUER,1.29)


def make_exit_models(mats,norms):
    frame,door=Geometry(),Geometry()
    for z in (-.105,1.60):
        box(frame,(-.11,z,0),(.26,.20,2.19),VARNISH,1.2)
        box(frame,(-.133,z-.016,.235),(.30,.24,.14),LACQUER,1.14)
    box(frame,(-.122,-.129,2.036),(.27,1.95,.215),VARNISH,1.29)
    box(frame,(-.139,-.107,2.157),(.28,1.91,.086),LACQUER,.95)
    for j in range(6):
        box(door,(-.026,j*.258,.077),(.086,.252,1.925),VARNISH,1.07)
    for y in (.24,.93,1.61):
        box(door,(-.062,.009,y),(.13,1.54,.075),LACQUER,1.61)
    for z in (.17,1.48):
        box(door,(-.064,z,.098),(.11,.093,1.90),METAL,1.5)
    box(door,(-.081,1.27,.927),(.145,.074,.18),AMBER,.86)
    export(FRAME,frame,mats,normal_maps=norms)
    export(LEAF,door,mats,normal_maps=norms)


def checkpoint(geo,w):
    # The save interaction belongs to the pre-existing high event. Support
    # its marker on a shrine niche and show a lower offering rest beside the
    # original walk, without substituting a new interaction.
    bx,by,bz=CHECKPOINT
    x,z,y=bx*.5+.25,bz*.5+.25,by*.5
    shelf=(int(w.hgt[bz,bx])+1)*.5
    for i in range(5):
        level=shelf+i*(y-shelf)/5.
        box(geo,(x-.48+i*.04,z-.39+i*.03,level-.003),
            (.97-i*.08,.80-i*.06,(y-shelf)/5+.012),h.BRICK if i%2 else h.NAVY,1.59)
    box(geo,(x-.29,z-.25,y-.09),(.59,.51,.095),h.SLATE,1.32)
    assert y>shelf
    return (x,z,y),shelf


def make_land(w,route,mats,norms):
    geo=Geometry()
    h.floor_mesh(w,geo,FLOOR,1.525)
    relief.arch_wall(w,geo,1.525)
    bores=[
        h.mouth_at(geo,w,31,18,axis="x",direction=1,span=1.13,depth=1.48,reinforced=False),
        h.mouth_at(geo,w,90,18,axis="x",direction=1,span=1.14,depth=2.54,reinforced=False),
    ]
    # Incoming risers lie behind the one-way story landing. Outgoing risers
    # begin beyond the opening's existing story trigger.
    stairs(geo,14.16,15.59,9.22,.62,5,.56)
    stairs(geo,48.78,46.81,9.21,.66,6,.81)
    cross_brace(geo,15.22,9.20,1.53,1.88)
    cross_brace(geo,18.98,9.19,1.53,1.93)
    cross_brace(geo,43.88,9.24,1.53,1.95)
    for x,z in ((20.8,10.73),(36.19,11.64),(40.61,6.62),(43.37,10.94)):
        y=1.55
        box(geo,(x-.23,z-.23,y),(.51,.47,.28),h.BRICK,1.11)
        box(geo,(x-.27,z-.26,y+.229),(.59,.53,.085),VARNISH,1.25)
    (x,z,y),shelf=checkpoint(geo,w)
    export(LAND,geo,mats,normal_maps=norms,smooth_materials=(h.NAVY,h.COBALT,h.SCREE))
    return geo,bores,(x,z,y),shelf


def placements(w,route,niche):
    props,lights=[],[]
    foot=set(route)

    def prop(model,bx,bz,size,yaw=0.,rise=0.):
        y=(int(w.hgt[bz,bx])+1)*.5+rise
        x,z=bx*.5+.25,bz*.5+.25
        props.append([model,x,y,z,size,yaw])
        return x,y,z

    for i,o in enumerate(w.objs):
        if o["t"]=="blk":
            x,z=o["x"],o["z"]
            if w.hgt[z,x]==2 and abs(o["y"]-3)<2 and (x,z) not in foot:
                prop(BARREL,x,z,.82+(i%4)*.075,.47*i,.035)
    for x,z,s,yaw in ((38,16,.71,1.60),(48,22,.82,-.15),(53,35,.81,.25),(79,23,.77,-.05)):
        if (x,z) not in foot and w.hgt[z,x]==2:
            prop(h.BENCH,x,z,s,yaw,.023)
    for i,(x,z,s) in enumerate(((31,17,.86),(35,20,.81),(41,17,.82),(47,22,.88),
                                  (43,28,.76),(49,34,.87),(58,37,.84),(63,33,.78),
                                  (66,26,.79),(72,22,.78),(79,17,.81),(85,20,.92),(92,17,.86))):
        if (x,z) in foot or w.hgt[z,x]>6:
            continue
        asset=h.ANDON if i%3!=1 else h.LAMP
        px,y,pz=prop(asset,x,z,s,.17*np.sin(i),.035)
        light_height=(.8 if asset==h.ANDON else .53)*s
        lights.append([px,y+light_height,pz,3.68,5.47,0xffaa42ff])
    x,z,y=niche
    props.append([h.SHRINE,x,y,z,.58,.18])
    props.append([h.ANDON,x-.51,y-.28,z+.13,.63,0.])
    lights.append([x-.49,y+.64,z+.15,3.95,4.69,0xffac43ff])
    return props,lights


def build(repo):
    live=repo/"_tools/rpgcobo-tool"
    cat=base.read_json(live/base.CATALOG)
    check_catalog(cat)
    gm=base.game_definition(repo)
    w,events=gm.make("M153")
    row=cat["M153"]
    assert row["size"][:3:2]==[w.w,w.d]
    assert all(row["event"][key]["pos"]==e["pos"] for key,e in events.ev.items() if "pos" in e)
    for x,z in ((31,18),(32,18),(33,18),(34,18),(90,18),(91,18),(92,18),(93,18),(94,18),(95,18)):
        assert w.hgt[z,x]==2
    route=h.get_floor_route(w,ROUTE)
    TEX.mkdir(parents=True,exist_ok=True)
    base.TEX=TEX
    base.export_coast.STAGE=STAGE
    mats,norms=materials(w,route)
    make_exit_models(mats,norms)
    geo,bores,niche,shelf=make_land(w,route,mats,norms)
    props,lights=placements(w,route,niche)
    # Published props are intentionally byte-for-byte copies.
    req={"reuse":{"placements":[[a] for a in sorted({r[0] for r in props})]}}
    for name,data in base.resource_files(live/base.ROOT,req).items():
        (STAGE/name).write_bytes(data)
    index={"M153":{"terrain":LAND,"hideStockScenery":True,"placements":props,
                   "poolLights":lights,"doors":[DOOR]}}
    (STAGE/"index.json").write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    info={"catalog_hash":base.digest(json.dumps(row,sort_keys=True).encode()),
          "world_hash":base.digest((live/"project/data/mapdata/M153.bw").read_bytes()),
          "route_blocks":len(route),"route_waypoints":route[::5],"roofed_bores":bores,
          "main_quads":len(geo.faces),"checkpoint_event":list(CHECKPOINT),
          "checkpoint_support_m":shelf,"dressing":len(props)}
    receipt={"maps":{"M153":info},"files":{name:base.digest(data) for name,data in base.resource_files(STAGE,index).items()}}
    (HERE/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf8")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("build","stage"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    args=parser.parse_args()
    if args.action=="build":
        build(args.repo.resolve())
    elif args.profile is None:
        parser.error("--profile is required for stage")
    else:
        h.STAGE=STAGE
        h.HERE=HERE
        h.stage(args.repo.resolve(),args.profile.resolve())
