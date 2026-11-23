"""Build visual layers for the Kyuden Hida cells and caves."""

import argparse
from collections import deque
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"volcanic-route"))
import volcanic_route as base
import build_yasuki_coast as mouth
from build_hoshi_stall import box
from export_coast import Geometry, export

STAGE = HERE / "native_environment"
TEX = STAGE / "tex"
FIRST = ("M148","M149","M150","M815")
DEEP = ("M157","M158","M170")
NAVY = "hida_caves_navy"
COBALT = "hida_caves_cobalt"
INNER = "hida_caves_recess"
SCREE = "hida_caves_scree"
SLATE = "hida_caves_wet_slate"
BRICK = "hida_caves_dressed_stone"
MORTAR = "hida_caves_mortar"
IRON = "hida_caves_iron"
RUST = "hida_caves_red_oxide"
WOOD = "hida_caves_smoked_cedar"
GOLD = "hida_caves_amber"
JADE = "hida_caves_jade_trace"
NORMAL = "hida_cave_rock_normal.png"
BENCH = "hida_cell_cedar_bench"
LAMP = "hida_cell_iron_lamp"
DRAIN = "hida_catacomb_basalt_drains"
ANDON = "castle_kaiu_lantern"
SHRINE = "shadowlands_ruined_shrine"
STONES = "castle_tamori_stones"
PROPS = {BENCH:(1.19,.52,.39), LAMP:(.42,.76,.43), DRAIN:(1.44,.47,.58)}
PALETTE={
    NAVY:((45,68,126),.88), COBALT:((55,94,166),.89), INNER:((23,35,78),.86),
    SCREE:((51,75,128),.89), SLATE:((50,74,105),.63), BRICK:((63,78,114),.85),
    MORTAR:((30,41,61),.91), IRON:((38,40,54),.78), RUST:((155,47,36),.87),
    WOOD:((85,47,37),.89), GOLD:((219,139,43),.72), JADE:((77,183,133),.64),
}
MATERIALS={name:(name+".png",rough) for name,(_,rough) in PALETTE.items()}
PATHS={
    "M148":((61,2),(61,5),(61,10),(61,30),(61,42),(61,54)),
    "M149":((61,2),(61,5),(61,16),(61,25),(61,42),(61,54)),
    "M150":((56,2),(56,5),(56,14),(56,29)),
    "M157":((61,5),(61,10),(61,17),(61,22),(61,30),(66,38)),
    "M170":((1,19),(31,19),(44,19),(100,19),(113,19)),
}


def make_materials():
    original = np.asarray(Image.open(base.SOURCE_IMAGES/"rock_01_diff_1k.jpg").convert("L"),dtype=float)
    broad = gaussian_filter(original,7.4,mode="wrap")
    scale = gaussian_filter(original,2.3,mode="wrap")
    surface=broad+.67*(scale-broad)
    tex = np.clip((surface-np.median(surface))/(2.65*surface.std()),-.82,.96)
    z,x=np.indices(tex.shape,dtype=float)
    folds=.6*np.cos(z*.024+x*.012)+.4*np.sin(z*.018-x*.023)
    for key,(rgb,_) in PALETTE.items():
        contrast=.21 if key in (RUST,GOLD,JADE,IRON) else .34
        mix=np.array(rgb)[None,None,:]*(1.+(contrast*tex+.038*folds)[...,None])
        base.write_image(key+".png",mix)
    normal=np.asarray(Image.open(base.SOURCE_IMAGES/"rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=float)/127.5-1
    normal=gaussian_filter(normal,(2.6,2.6,0.),mode="wrap")
    normal[...,:2]*=.66
    normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-8)
    base.write_image(NORMAL,(normal+1)*127.5)
    return surface


def get_floor_route(w, anchors):
    usable=w.hgt==2
    visited=[]
    for origin,goal in zip(anchors[:-1],anchors[1:]):
        assert usable[origin[1],origin[0]] and usable[goal[1],goal[0]],(w.mid,origin,goal)
        frontier=deque([origin])
        steps={origin:None}
        while frontier and goal not in steps:
            x,z=frontier.popleft()
            for a,b in ((x-1,z),(x+1,z),(x,z+1),(x,z-1)):
                if 0<=a<w.w and 0<=b<w.d and usable[b,a] and (a,b) not in steps:
                    steps[a,b]=(x,z)
                    frontier.append((a,b))
        assert goal in steps,(w.mid,origin,goal)
        span=[]
        point=goal
        while point is not None:
            span.append(point)
            point=steps[point]
        visited.extend(reversed(span))
    return visited


def flagstone(w,route,scan,arena=False):
    name=w.mid.lower()+"_hida_floor"
    cols,rows=2048,1024 if arena else 752
    z,x=np.meshgrid(np.arange(rows)*w.d/rows,np.arange(cols)*w.w/cols,indexing="ij")
    road=np.zeros_like(w.hgt,dtype=bool)
    for bx,bz in route:
        road[bz,bx]=True
    if arena:
        road[51:77,22:106]=True
    reach=distance_transform_edt(~road)
    distance=map_coordinates(reach,(z-.5,x-.5),order=1,mode="nearest")
    center=np.exp(-np.square(distance/(2.3 if not arena else 13.)))
    xoff=.25*np.cos(x*.43+z*.66)+.13*np.sin(z*.91)
    joint=.38+np.floor((z+xoff)/2.36)
    variation=.86+.14*np.cos(joint*2.77+np.floor((x+joint*.86)/2.63)*1.783)
    line_a=np.abs(((z+xoff)/2.36)%1.-.5)
    line_b=np.abs(((x+joint*.86+.1*np.sin(z*.8))/2.63)%1.-.5)
    seams=np.clip((np.maximum(line_a,line_b)-.438)*17.,0.,.64)
    if w.mid in ("M149","M157","M170"):
        seams*=.47
    surface=map_coordinates(scan,(z*22.3,x*24.2),order=1,mode="grid-wrap")
    mineral=np.clip((surface-np.median(surface))/(2.8*surface.std()),-.61,.71)
    shades={
        "M148":([45,66,113],[107,80,68]), "M149":([45,65,102],[95,83,75]),
        "M150":([36,55,98],[107,70,64]), "M815":([38,53,98],[72,75,104]),
        "M157":([34,61,102],[77,74,77]), "M170":([31,55,96],[91,72,55]),
    }
    cool,route_color=map(np.asarray,shades[w.mid])
    cells=cool+(route_color-cool)*(.83*center[...,None])
    pixels=cells*(variation*(1.-.49*seams)*(1.+.31*mineral))[...,None]
    base.write_image(name+".png",pixels)
    return name


def floor_mesh(w,mesh,k,floor):
    # The slab continues under the walls, so the chamfers join the visible
    # floor and the native collision retains the original route.
    p=[(0.,0.,floor),(w.w*.5,0.,floor),(w.w*.5,w.d*.5,floor),(0.,w.d*.5,floor)]
    mesh.quad(p,[(0,0),(1,0),(1,1),(0,1)],k)


def natural_walls(w,mesh,floor):
    # Native height stays at the wall core. Round the visual wall toe within
    # the solid cells and retain the low front cutaway where the map has it.
    xs,zs=np.meshgrid(np.arange(w.w+1,dtype=float),np.arange(w.d+1,dtype=float))
    walk=w.hgt==2
    border=distance_transform_edt(~walk) - distance_transform_edt(walk)
    edge=map_coordinates(border,(zs-.5,xs-.5),order=1,mode="nearest")
    target=map_coordinates(gaussian_filter(w.hgt.astype(float),.86),(zs-.5,xs-.5),order=1,mode="nearest")
    r=.28*np.sin(xs*.67+zs*.44)+.11*np.cos(xs*1.59-zs*.67)+.087*np.cos(xs*.81+zs*1.67)
    slope=np.clip((edge-.03)/1.94,0.,1.)
    crest=floor+slope*(np.maximum(floor+.10,(target+1)*.5+r)-floor)
    wall=(~walk)&(w.blk!=0)
    for z,x in np.argwhere(wall):
        fan=((x,z),(x+1,z),(x+1,z+1),(x,z+1))
        if max(crest[b,a] for a,b in fan)<floor+.014:
            continue
        p=[(a*.5,b*.5,float(crest[b,a])) for a,b in fan]
        style=(SCREE if crest[z,x]<floor+1.08 else NAVY if r[z,x]<.07 else COBALT)
        base.quads(mesh,p,style,2.24)


def mouth_at(geo,w,x,z,axis="z",direction=1,span=None,depth=1.32,reinforced=True):
    # The fitting uses the actual run of traversable tiles at the mouth.
    if axis=="z":
        bounds=np.flatnonzero(w.hgt[z]==2)
        along=x
    else:
        bounds=np.flatnonzero(w.hgt[:,x]==2)
        along=z
    assert along in bounds,(w.mid,x,z)
    lo=hi=along
    while lo-1 in bounds:
        lo-=1
    while hi+1 in bounds:
        hi+=1
    half=min((hi-lo+1)*.25+.035,span if span is not None else 1.28)
    assert half>=.72,(w.mid,x,z,lo,hi)
    offset=(lo+hi+1)*.25 if hi-lo<7 else along*.5+.25
    temp=Geometry()
    front=(z if axis=="z" else x)*.5+.10
    mouth.cave_mouth(temp,offset,front,front+depth,1.528,half,1.51,half+.86,
                     mouth.STONE,reinforced=reinforced)
    mats={mouth.STONE:COBALT,mouth.INNER:INNER,mouth.TIMBER:WOOD,mouth.PAINT:BRICK,mouth.RED:RUST}
    for i,face in enumerate(temp.faces):
        points=[]
        uvs=temp.uvs[i]
        for idx in face:
            a,b,y=temp.vertices[idx]
            b=front+direction*(b-front)
            points.append((a,b,y) if axis=="z" else (b,a,y))
        reflected = (axis == "x") == (direction > 0)
        # The borrowed rock shell faces the bore. Turn it outward for the
        # exposed cutaway, while keeping the two-sided throat and timber.
        rock_shell = temp.materials[i] == mouth.STONE
        if reflected != rock_shell:
            points.reverse()
            uvs=uvs[::-1]
        geo.quad(points,uvs,mats[temp.materials[i]])
    return {"center":[x,z],"native_bore_cells":[int(lo),int(hi)],"half_width_m":half,"roof_depth_m":depth,"axis":axis}


def lining(geo,w,zs,xmax,xmin,side):
    # Cedar brackets, ashlar and darker joints stay against the cave wall.
    for z in zs:
        z=int(z)
        row=np.flatnonzero((w.hgt[z]==2)&(np.arange(w.w)>=xmin)&(np.arange(w.w)<xmax))
        if not len(row):
            continue
        x=(row[0] if side<0 else row[-1]+1)*.5
        start=x-.36 if side<0 else x
        for j in range(3):
            drift=.11*((j%2)-.5)
            box(geo,(start+drift,z*.5-.06,1.53+j*.38),(.34,.57,.358),
                BRICK if (j+z)%4 else NAVY,1.31)
        if z%4==0:
            box(geo,(start-.04,z*.5+.08,1.65),(.42,.20,.17),RUST,1.03)


def barred_piece(geo,x,z,y,width=.36,tall=1.65):
    box(geo,(x-width*.5-.08,z-.095,y),(.12,.19,tall+.12),BRICK)
    box(geo,(x+width*.5-.04,z-.095,y),(.12,.19,tall+.12),BRICK)
    for a in np.linspace(x-width*.40,x+width*.40,4):
        box(geo,(a-.018,z-.041,y+.12),(.037,.08,tall-.23),IRON)
    for h in (.18,tall-.23):
        box(geo,(x-width*.5,z-.068,y+h),(width,.13,.082),RUST)


def floor_detail(geo,w):
    if w.mid=="M148":
        for item in w.objs:
            if item["t"]=="blk":
                barred_piece(geo,item["x"]*.5+.25,item["z"]*.5+.25,item["y"]*.5+.038)
        lining(geo,w,range(10,25),75,47,1)
        lining(geo,w,(8,10,15,17,18,22,23),75,47,-1)
        # The rat-way dialogue uses the old x57 landing. The raised lid and
        # shallow recess mark the trapdoor without changing its scripted travel.
        x,z=28.48,5.03
        for a,b,dx,dz in ((x-.37,z-.23,.74,.09),(x-.37,z+.23,.74,.09),
                          (x-.37,z-.14,.08,.37),(x+.29,z-.14,.08,.37)):
            box(geo,(a,b,1.533),(dx,dz,.058),BRICK)
        box(geo,(x-.28,z-.14,1.535),(.56,.37,.016),INNER)
        box(geo,(x-.34,z+.26,1.571),(.67,.105,.43),WOOD)
    elif w.mid in ("M149","M157","M170"):
        footing=(16,25) if w.mid=="M149" else (16,22,30) if w.mid=="M157" else (19,)
        for z in footing:
            for ix in range(w.w):
                if w.hgt[z,ix]!=2:
                    continue
                if w.mid=="M149" and not 59<=ix<=64:
                    continue
                if w.mid!="M149" and w.blk[z,ix]!=707:
                    continue
                s=JADE if w.mid=="M149" and z==25 else RUST if ix%3 else BRICK
                height=.005 if s==JADE else .012
                box(geo,(ix*.5+.055,z*.5+.19,1.535),(.39,.089,height),s,1.44)
    elif w.mid=="M150":
        # The broken restraint frame sits behind the troll and item anchor.
        for x,z in ((25.43,15.52),(31.31,14.85)):
            y=1.52
            box(geo,(x-.19,z-.20,y),(.38,.40,1.62),BRICK,1.24)
            box(geo,(x-.22,z-.21,y+.67),(.44,.42,.13),RUST)
            box(geo,(x-.22,z-.21,y+1.39),(.44,.42,.13),IRON)


def caves(w,scan):
    route=get_floor_route(w,PATHS[w.mid])
    name=flagstone(w,route,scan)
    geo=Geometry()
    floor_mesh(w,geo,name,1.521)
    natural_walls(w,geo,1.521)
    configs={
        "M148":((61,3,"z",1,1.12,1.36,True),(61,47,"z",-1,1.03,2.12,True)),
        "M149":((61,3,"z",1,1.10,1.47,True),(61,48,"z",-1,1.02,2.15,True)),
        "M150":((56,3,"z",1,1.10,1.41,True),(56,13,"z",1,.85,1.21,False)),
        "M157":((61,3,"z",1,1.14,1.73,True),(61,44,"z",-1,1.05,2.12,False)),
        "M170":((19,19,"x",1,1.08,1.90,True),(109,19,"x",1,.88,1.28,False)),
    }
    bores=[mouth_at(geo,w,*fit) for fit in configs[w.mid]]
    floor_detail(geo,w)
    mats={**MATERIALS,name:(name+".png",.72)}
    return geo,mats,route,bores


def arena(w,scan):
    geo=Geometry()
    name=flagstone(w,(),scan,arena=True)
    floor_mesh(w,geo,name,.516)
    # Far cave layers slant back from the original backdrop footprint and
    # leave the exact fighter formations clear.
    pts=[]
    for x in np.linspace(0.,64.,183):
        lobes=.61*np.cos(x*.71)+.38*np.sin(x*1.47)+.19*np.sin(x*3.47)
        t=.25*np.cos(x*.91)+.47*np.sin(x*.31)
        pts.append([(x,42.85+t,.55),(x,43.45+t,1.23+lobes*.39),
                    (x,44.27+t,2.06+lobes*.63),(x,46.2+t,3.65+lobes),
                    (x,50.6+t,5.81+lobes),(x,64.,5.32+lobes*.89)])
    for a,b in zip(pts[:-1],pts[1:]):
        for i,style in enumerate((SCREE,INNER,NAVY,COBALT,NAVY)):
            base.quads(geo,[a[i],b[i],b[i+1],a[i+1]],style,2.65)
    for item in w.objs:
        if item["t"]=="blk":
            barred_piece(geo,item["x"]*.5+.25,item["z"]*.5+.25,.53,width=.48,tall=1.68)
    return geo,{**MATERIALS,name:(name+".png",.72)},[],[]


def wall_top(w):
    # The M157 story warp arrives at the rear of this building. The real
    # unfilled bore suggests the same stair, while the native event drives
    # the one-way transition.
    geo=Geometry()
    floor_mesh(w,geo,BRICK,8.532)
    for item in w.objs:
        if item["t"]=="blk":
            x,z=item["x"]*.5,item["z"]*.5
            box(geo,(x,z,item["y"]*.5),(.498,.498,.498),BRICK)
    temp=Geometry()
    mouth.cave_mouth(temp,28.24,4.19,6.06,8.532,1.24,1.55,2.36,mouth.STONE,reinforced=True)
    mats={mouth.STONE:COBALT,mouth.INNER:INNER,mouth.TIMBER:WOOD,mouth.PAINT:BRICK,mouth.RED:RUST}
    for i,face in enumerate(temp.faces):
        geo.quad([temp.vertices[k] for k in face],temp.uvs[i],mats[temp.materials[i]])
    return geo,MATERIALS,[],[{"center":[56,8],"roof_depth_m":1.87,"axis":"z","arrival_only":True}]


def dress(w,cat,mroute):
    center={key:(row["pos"][0],row["pos"][2]) for key,row in cat["event"].items()
            if "pos" in row and row["role"]!="villager"}
    placed,lights=[],[]

    def place(asset,bx,bz,s=1.,yaw=0.,rise=0.):
        assert 0<=bx<w.w and 0<=bz<w.d
        wx,wz=bx*.5+.25,bz*.5+.25
        y=(int(w.hgt[bz,bx])+1)*.5+rise
        placed.append([asset,wx,y,wz,s,yaw])
        return wx,wz,y

    def lamp(asset,x,z,s=.81,rise=.0,power=3.34):
        a,b,y=place(asset,x,z,s,.05,rise)
        height=(.92 if asset==ANDON else .53)*s
        lights.append([a,y+height,b,4.45,power,0xffb34bff])

    if w.mid=="M815":
        for x,z,s in ((37,82,.94),(56,80,.85),(70,83,.88),(89,81,.94)):
            lamp(ANDON,x,z,s,power=2.9)
        for x,z in ((45,82),(83,83),(93,82)):
            place(DRAIN,x,z,.86,.12)
        return placed,lights
    if w.mid=="M158":
        for x,z in ((53,12),(59,12),(41,28),(67,28),(80,28)):
            lamp(ANDON,x,z,.96)
        return placed,lights
    route=set(mroute)
    floor=w.hgt==2
    props={
        "M148":((BENCH,43,21,.79,.02),(BENCH,81,22,.82,-.11),(BENCH,58,32,.74,1.52),
                (DRAIN,57,24,.58,.10)),
        "M149":((DRAIN,59,14,.66,1.50),(DRAIN,75,29,.78,.08),(DRAIN,68,31,.66,.36),
                (BENCH,40,30,.78,.16)),
        "M150":((BENCH,47,24,.84,.19),(DRAIN,65,24,.79,.30),(DRAIN,62,30,.74,1.44)),
        "M157":((DRAIN,57,21,.62,1.4),(DRAIN,66,35,.63,.58)),
        "M170":((DRAIN,45,20,.60,.14),(DRAIN,72,35,.69,.17),(DRAIN,116,30,.82,1.52)),
    }[w.mid]
    for asset,x,z,s,yaw in props:
        # Off-route dressing may sit on a nearby solid shelf or an open
        # side cell. Keep its footprint clear of route centers and triggers.
        if (x,z) in route or any((x-a)**2+(z-b)**2<4 for a,b in center.values()):
            continue
        if floor[z,x] or (2<w.hgt[z,x]<7):
            place(asset,x,z,s,yaw,.04)
    if w.mid=="M149":
        place(SHRINE,66,33,.47,0)
    for item in w.objs:
        if item["t"]=="fb" and item.get("fbtype")==20:
            x,z=item["x"],item["z"]
            if (x,z) not in route and all((x-a)**2+(z-b)**2>2 for a,b in center.values()):
                place(STONES,x,z,.55,.33)
    spots={
        "M148":((58,8),(65,16),(53,21),(72,21),(59,35),(64,43)),
        "M149":((59,7),(48,9),(49,17),(60,14),(62,22),(70,19),(74,27),(64,32),(58,43)),
        "M150":((53,8),(59,17),(45,22),(66,22),(48,29),(63,26)),
        "M157":((58,8),(64,15),(57,23),(65,33),(62,41)),
        "M170":((25,17),(42,18),(55,17),(71,21),(73,30),(82,36),(95,35),(108,29),(111,17)),
    }[w.mid]
    for i,(x,z) in enumerate(spots):
        asset=ANDON if i%3!=1 else LAMP
        if (x,z) not in route and w.hgt[z,x]<7:
            lamp(asset,x,z,.83 if asset==ANDON else .69,.025)
    return placed,lights


def encounter_rows(cat):
    groups=[]
    for owner in ("M001","M148","M149"):
        groups.extend((owner,row) for row in cat[owner]["encount"] if row["mapid"]=="M815")
    assert {row["gid"] for owner,row in groups if owner=="M001"}=={13,14,23}
    for owner in ("M148","M149"):
        assert {row["gid"] for source,row in groups if source==owner}==set(range(1,10))
    return groups


def build(repo,maps,model_suffix=""):
    live=repo/"_tools/rpgcobo-tool"
    cat=base.read_json(live/base.CATALOG)
    gm=base.game_definition(repo)
    TEX.mkdir(parents=True,exist_ok=True)
    base.STAGE=base.export_coast.STAGE=base.diorama_trees.STAGE=STAGE
    base.TEX=TEX
    scan=make_materials()
    generated={asset:base.diorama_trees.build_diorama_mesh(asset,asset,size,main_component=True)
               for asset,size in PROPS.items()}
    for name,data in base.resource_files(live/base.ROOT,{"shared":{"placements":[[a] for a in (ANDON,SHRINE,STONES)]}}).items():
        (STAGE/name).write_bytes(data)
    rows,info={},{}
    for mid in maps:
        w,events=gm.make(mid)
        row=cat[mid]
        assert row["size"][:3:2]==[w.w,w.d]
        if events:
            assert all(row["event"][key]["pos"]==item["pos"] for key,item in events.ev.items() if "pos" in item)
        if mid=="M815":
            geo,mats,route,bores=arena(w,scan)
        elif mid=="M158":
            geo,mats,route,bores=wall_top(w)
        else:
            geo,mats,route,bores=caves(w,scan)
        model=mid.lower()+"_hida_caves"+model_suffix
        mnormal={k:NORMAL for k in mats if k not in (WOOD,RUST,IRON,GOLD,JADE)}
        export(model,geo,mats,normal_maps=mnormal,smooth_materials=(NAVY,COBALT,SCREE))
        placements,lights=dress(w,row,route)
        rows[mid]=dict(terrain=model,hideStockScenery=True,placements=placements,poolLights=lights)
        data={"catalog_hash":base.digest(json.dumps(row,sort_keys=True).encode()),
              "world_hash":base.digest((live/f"project/data/mapdata/{mid}.bw").read_bytes()),
              "native_shape":[w.w,w.d],"terrain_quads":len(geo.faces),"set_dressing":len(placements),
              "preserved_route_blocks":len(route),"route_waypoints":route[::8],"roofed_bores":bores,
              "portal_events":{k:e["pos"] for k,e in row["event"].items() if e["role"]=="portal"}}
        if mid=="M815":
            data["encounters"]=[[name,row["gid"]] for name,row in encounter_rows(cat)]
            data["formations"]={m["name"]:m["pos"] for m in row["marker"].values()}
        info[mid]=data
    (STAGE/"index.json").write_text(json.dumps(rows,separators=(",",":")),encoding="utf8")
    files={name:base.digest(bits) for name,bits in base.resource_files(STAGE,rows).items()}
    (HERE/"receipt.json").write_text(json.dumps({"maps":info,"files":files,"sources":generated},indent=2),encoding="utf8")


def stage(repo,slot):
    live=repo/"_tools/rpgcobo-tool"
    if slot.resolve()==live.resolve():
        raise ValueError("Stage into an isolated playtest copy.")
    proof=base.read_json(HERE/"receipt.json")
    cat=base.read_json(slot/base.CATALOG)
    for mid,row in proof["maps"].items():
        assert base.digest(json.dumps(cat[mid],sort_keys=True).encode())==row["catalog_hash"],mid
        assert base.digest((slot/f"project/data/mapdata/{mid}.bw").read_bytes())==row["world_hash"],mid
    for name,sha in proof["files"].items():
        assert base.digest((STAGE/name).read_bytes())==sha,name
    (slot/base.ROOT/"tex").mkdir(parents=True,exist_ok=True)
    base.install_environment_rows.STAGE=STAGE
    base.install_environment_rows.install(slot,tuple(proof["maps"]))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("build","stage"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    parser.add_argument("--deep",action="store_true",help="Use the independent M157/M158/M170 bundle")
    args=parser.parse_args()
    if args.deep:
        HERE=HERE/"deep"
        STAGE=HERE/"native_environment"
        TEX=STAGE/"tex"
    if args.action=="build":
        build(args.repo.resolve(),DEEP if args.deep else FIRST)
    elif args.profile is None:
        parser.error("--profile is required for stage")
    else:
        stage(args.repo.resolve(),args.profile.resolve())
