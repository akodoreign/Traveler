"""Dress the new Yasuki road and both working cave mouths."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter, zoom

from build_furnace import grid_surfaces
from build_hoshi_stall import box
from build_iuchi_tower import tint_texture
from build_kaiu_kit import MATS as EXISTING, world_mesh
from diorama_trees import build_diorama_mesh
from export_coast import Geometry, STAGE, export
from publish_castle_gates import resource_files
from yasuki_coast_worlds import MAPS, variant

HERE=Path(__file__).resolve().parent
ARENA="M829"
STONE="yasuki_blue_coast_slate"
WALL="yasuki_wet_blue_slate"
INNER="yasuki_recess_shale"
SAND="yasuki_gilt_silt"
TRACK="yasuki_dry_coast_track"
GRASS="yasuki_salt_grass"
TIMBER="yasuki_tarred_cedar"
PAINT="yasuki_crab_blue"
RED="yasuki_crab_vermilion"
SEA="yasuki_open_blue_coast"
POOL="yasuki_tidal_pool"
ROCK="yasuki_cave_tide_scored_rocks"
DOCK="yasuki_cave_boat_landing"
BALES="yasuki_cave_covered_supply_bales"
PINE="traveler_diorama_pine"
LANTERN="snake_den_stone_lantern"
SURFACES=(STONE,WALL,INNER,SAND,TRACK,GRASS,TIMBER,PAINT,RED)
MAT={**EXISTING,**{key:(key+".png",.86) for key in SURFACES},
     SEA:(SEA+"00.png",.34),POOL:(POOL+"00.png",.45)}
NORMALS={key:"yasuki_coast_slate_normal.png" for key in (STONE,WALL,INNER)}
SHARED=(PINE,LANTERN,"iuchi_fitted_andon","cakon_mooring_gear","floating_flowers_work_skiff",
        "cakon_staved_barrel","smooth_hoshi_trade_chest","iuchi_brook_reeds")


def materials(repo):
    source=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    for name,data in resource_files(source,{"all":{"placements":[[asset] for asset in SHARED]}}).items():
        if not (STAGE/name).is_file() or (STAGE/name).read_bytes()!=data:
            (STAGE/name).write_bytes(data)
    image=Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("RGB")
    value=np.asarray(image) @ [.24,.62,.14]
    mineral=np.clip((value-np.median(value))/max(1.,value.std()),-2.,2.)
    for key,tint,contrast in ((STONE,(26.,60.,113.),.23),(WALL,(22.,62.,85.),.18),(INNER,(15.,35.,60.),.19)):
        sample=np.asarray(tint)*(1.+contrast*mineral[...,None])
        Image.fromarray(np.uint8(sample.clip(0,255))).save(STAGE/"tex"/(key+".png"))
    normal=Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB")
    vec=np.asarray(normal).astype(float)/127.5-1.
    vec[...,:2]*=.42
    vec/=np.linalg.norm(vec,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((vec+1.)*127.5).clip(0,255))).save(STAGE/"tex/yasuki_coast_slate_normal.png")
    for key,scan,tint,contrast in (
        (SAND,"cakon_paddy_mud_scan",(168,120,65),.093),
        (TRACK,"cakon_paddy_mud_scan",(155,100,51),.135),
        (GRASS,"iuchi_frosted_meadow",(84,126,36),.15),
        (TIMBER,"kaiu_cedar",(49,25,17),.17),
        (PAINT,"kaiu_cedar",(22,54,110),.13),
        (RED,"kaiu_cedar",(160,32,28),.125),
    ):
        tint_texture(key,scan,tint,contrast)
    # Start from the approved shore-to-depth treatment, tuned to the cooler
    # open coast. Underwater texture details stay aligned to the shoreline.
    for phase in range(64):
        data=np.asarray(Image.open(source/"tex"/f"winter_river_glacial_depth{phase:02}.png").convert("RGB"))
        rgb=data*np.array([.88,1.04,1.12])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{SEA}{phase:02}.png")
    z,x=np.mgrid[0:2*pi:256j,0:2*pi:256j]
    for phase in range(32):
        t=phase*pi/16.
        bed=3.*np.sin(3*x+2*z)+4.2*np.cos(x-z+.32*np.sin(z))
        ripple=np.sin(2*x+4*z-t+.7*np.sin(x-z)) + .35*np.sin(x-3*z+2*t)
        band=np.maximum(0.,ripple)**3
        rgb=np.array([9.,69.,97.])+(bed+3.2*ripple+4.1*band)[...,None]*[.54,1.3,1.42]
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{POOL}{phase:02}.png")


def face(mesh,points,material,repeat=3.2):
    uv=[((a+.27*b)/repeat,(.76*b+c)/repeat) for a,b,c in points]
    mesh.quad(points,uv,material)


def cave_mouth(mesh,cx,front,back,floor,half,rise,span,outer,reinforced=False):
    frames=[]
    for a in np.linspace(0.,pi,25):
        side=cos(a)
        wobble=.068*sin(9*a)+.036*cos(17*a)
        frames.append(np.array([
            [cx+half*side,front+.13*side+.075*sin(8*a),floor+.90+rise*sin(a)],
            [cx+(half+.51)*side,front-.14+.22*abs(side),floor+.69+(rise+.69+wobble)*sin(a)],
            [cx+(span+wobble)*side,front+.46+.75*abs(side),floor+.38+(rise+1.59+wobble)*sin(a)],
            [cx+(span+.58)*side,back+.40, floor+.53+(rise+1.62)*sin(a)],
        ]))
    for i,(a,b) in enumerate(zip(frames,frames[1:])):
        for j,style in enumerate((outer,outer,STONE)):
            face(mesh,[a[j],b[j],b[j+1],a[j+1]],style,2.7)
        shift=np.array([0.,back-front,.14])
        inside=[a[0],a[0]+shift,b[0]+shift,b[0]]
        face(mesh,inside,INNER,2.7)
        face(mesh,inside[::-1],INNER,2.7)
    for side in (-1,1):
        roots=frames[0] if side>0 else frames[-1]
        for index in range(3):
            a,b=roots[index],roots[index+1]
            face(mesh,[a,b,(b[0],b[1],floor),(a[0],a[1],floor)],outer,2.6)
        inner=roots[0]
        face(mesh,[(inner[0],inner[1],floor),(inner[0],inner[1],inner[2]),
                   (inner[0],back,inner[2]+.14),(inner[0],back,floor)],INNER,2.6)
    if reinforced:
        for side in (-1,1):
            x=cx+side*(half+.175)
            box(mesh,(x-.105,front-.20,floor),(.21,.31,2.35),TIMBER,.85)
            box(mesh,(x-.155,front-.245,floor+.14),(.31,.38,.15),PAINT,1.1)
            box(mesh,(x-.126,front-.222,floor+2.03),(.26,.351,.12),RED,.92)
        box(mesh,(cx-half-.31,front-.23,floor+2.30),(2*half+.62,.36,.24),TIMBER,1.38)


def rock_heights(world,stone,base):
    edge=distance_transform_edt(stone)
    cols,rows=world.w,world.d
    z,x=np.indices((rows,cols))*.5
    height=max(0.,base)
    surface=(gaussian_filter(world.hgt.astype(float),1.02)+1.)*.5
    rumple=.24*np.cos(x*1.4+z*.91)+.14*np.sin(z*2.8-x*1.0)+.09*np.cos(x*4.3+z*5.4)
    crest=0.
    if world.mid!="M470":
        # Only the far rock rises into the backdrop. The near cutaway
        # stays low so it cannot mask either combat formation.
        rear=.338 if world.mid==ARENA else .31
        crest=np.clip((z-rows*rear)/(rows*.10),0.,1.)**1.54
        crest*= (10.6 if world.mid==ARENA else 6.8)+1.7*np.cos(x*.09)
    return height+np.clip((edge-.64)/2.03,0.,1.)**.69*np.maximum(.77,surface-height+rumple+crest)


def faceted_rock(mesh,world,stone,height):
    z,x=np.indices(stone.shape)*.5
    y=rock_heights(world,stone,height)
    for r,c in np.argwhere(stone[:-1,:-1] | stone[1:,:-1] | stone[1:,1:] | stone[:-1,1:]):
        corners=[(x[a,b]+.25,z[a,b]+.25,y[a,b])
                 for a,b in ((r,c),(r,c+1),(r+1,c+1),(r+1,c))]
        if max(p[2] for p in corners)>height+.024:
            style=WALL if np.mean([p[2] for p in corners])<height+.47 and world.mid!="M470" else STONE
            face(mesh,corners,style,3.55)


def ocean(mesh,world):
    y=max(v[2] for v in mesh.vertices)
    cap=Geometry()
    # Both existing nearshore quads and extension use the same world UVs.
    surfaces=np.asarray(mesh.vertices).reshape(-1,4,3).tolist()
    surfaces.append([(0.,-26.,y),(world.w*.5,-26.,y),(world.w*.5,0.,y),(0.,0.,y)])
    for src in surfaces:
        x0,z0,_=np.min(src,axis=0)
        x1,z1,y=np.max(src,axis=0)
        rows=np.linspace(z0,z1,1+max(1,int(np.ceil((z1-z0)/.48))))
        cols=np.linspace(x0,x1,1+max(1,int(np.ceil((x1-x0)/2.4))))
        for lo,hi in zip(rows,rows[1:]):
            for left,right in zip(cols,cols[1:]):
                frame=[(left,lo,y),(right,lo,y),(right,hi,y),(left,hi,y)]
                uv=[]
                for x,z,_ in frame:
                    bank=(6.+1.3*sin(x*.182)+.8*sin(x*.454))*.5
                    depth=float(np.clip((bank-z)/13.,0.,1.))
                    uv.append((x/34.+.018*sin(z*.18),.007+.985*depth))
                cap.quad(frame,uv,SEA)
    return cap


def smooth_floor(w,ground,gm,top):
    key=f"{w.mid.lower()}_mineral_floor"
    dims=(w.d*8,w.w*8)
    path=gaussian_filter(zoom((w.blk==gm.DIRT).astype(float),8,order=1),5.2)
    z,x=np.indices(dims,dtype=np.float32)
    scan=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("L"),dtype=float)
    u=(x.astype(np.int32)*3)%scan.shape[1]
    v=(z.astype(np.int32)*3)%scan.shape[0]
    texture=np.clip((scan[v,u]-np.median(scan))/max(1.,scan.std()),-2.,2.)
    weather=np.sin(x*.041+z*.027)+.68*np.cos(x*.024-z*.031)+.35*np.cos(.15*z-.023*x)
    damp=np.array([21.,67.,79.] if w.mid=="M480" else [25.,47.,69.])
    amber=np.array([116.,72.,35.] if w.mid=="M480" else [100.,60.,32.])
    color=damp+(amber-damp)*(.72*path[...,None])
    color*=1.+(.095*texture+.055*weather)[...,None]
    Image.fromarray(np.uint8(np.clip(color,0,255))).save(STAGE/"tex"/(key+".png"))
    for index,material in enumerate(ground.materials):
        if material not in (TRACK,WALL):
            continue
        points=np.asarray([ground.vertices[i] for i in ground.faces[index]])
        if points[:,2].min()>=top-.07 and np.ptp(points[:,2])<.002:
            ground.materials[index]=key
            ground.uvs[index]=[(a/(w.w*.5),1.-b/(w.d*.5)) for a,b,_ in points]
    return {key:(key+".png",.92)}


def build_geometry(gm,w):
    road=w.mid=="M470"
    arena=w.mid==ARENA
    water=w.blk==gm.WATER
    stone=w.blk==gm.STONE
    dry=copy(w)
    dry.objs=[]
    dry.blk=np.where(stone,0,np.where(water,gm.SAND if road else gm.CAVE_FLOOR,w.blk))
    dry.hgt=np.where(water,np.maximum(0,w.hgt-1),w.hgt)
    styles={gm.SAND:SAND,gm.DIRT:TRACK,gm.ROAD:TRACK,gm.GRASS:GRASS,gm.CAVE_FLOOR:WALL}
    ground=world_mesh(gm,dry,styles)
    floor=2.005 if road else .505 if arena else 1.505
    terrain_material={} if road else smooth_floor(w,ground,gm,floor)
    faceted_rock(ground,w,stone,floor)
    if road:
        for cell,front,back in w.yasuki_mouths:
            cave_mouth(ground,cell*.5+.25,front*.5-.58,back*.5,2.01,
                       1.67,1.56,3.46,STONE,reinforced=cell==112)
    elif not arena:
        cave_mouth(ground,23.25,1.42,4.32,1.51,1.55,1.53,2.78,WALL,reinforced=w.mid=="M481")
    terrain=f"{w.mid.lower()}_yasuki_coast"
    export(terrain,ground,{**MAT,**terrain_material},normal_maps=NORMALS)
    prefix=SEA if road else POOL
    _,surface=grid_surfaces(water.astype(int),w.hgt,("",prefix),wall_style=STONE,fluid=1)
    name=f"{w.mid.lower()}_yasuki_water"
    export(name,ocean(surface,w) if road else surface,MAT)
    return terrain,name,len(ground.faces)


def dress(gm,w):
    road=w.mid=="M470"
    props=[]
    lights=[]
    stone=w.blk==gm.STONE
    base=2.005 if road else .505 if w.mid==ARENA else 1.505
    height=rock_heights(w,stone,base)
    def put(name,x,z,scale=1.,yaw=0.,sway=0.,y=None):
        if y is None:
            col,row=int(x*2),int(z*2)
            if stone[row,col]:
                # Sample the dressed rock. The underlying grid is steeper
                # than its continuous visible face.
                left,front=int(x*2-.5),int(z*2-.5)
                dx,dz=x*2-.5-left,z*2-.5-front
                patch=height[front:front+2,left:left+2]
                y=float(np.array([1.-dz,dz]) @ patch @ np.array([1.-dx,dx]))-.10*scale
            else:
                y=(int(w.hgt[row,col])+1)*.5+.045
        props.append([name,x,y,z,scale,yaw,*([sway] if sway else [])])
        return y

    def lamp(x,z,size=1.,stone=True):
        y=put(LANTERN if stone else "iuchi_fitted_andon",x,z,size)
        lights.append([x,y+(.97 if stone else .55)*size,z,4.2,7.6,0xffbb5bff])

    if road:
        for x,z,s in ((18.8,13.4,.86),(22.8,14.0,.85),(25.8,16.7,1.11),(30.2,19.8,.93),
                      (39.8,20.6,.94),(43.8,19.6,1.02),(47.65,13.80,.88),(52.02,19.60,.93),
                      (59.4,14.72,1.12),(62.3,17.73,.89),(75.6,12.05,.91),(79.6,14.5,.81)):
            if w.hgt[int(z*2),int(x*2)]==3:
                put(PINE,x,z,s,.29*x,.033)
        for x,z,s in ((31.15,12.82,.96),(38.75,12.77,.86),(52.11,12.53,.95),(60.08,12.57,1.03),
                      (21.,4.52,1.08),(43.9,4.02,1.16),(61.3,5.88,.97),(72.5,4.20,1.29)):
            put(ROCK,x,z,s,.63*x)
        for x in (19.1,22.5,25.1,28.1,39.17,42.,48.3,53.2,59.3,67.4,77.2):
            put("iuchi_brook_reeds",x,6.02+.5*sin(x),.87+.08*cos(x),.43*x,.047)
        for x,z in ((33.08,12.78),(37.03,12.35),(54.01,12.28),(58.18,12.25)):
            lamp(x,z,.80)
        put("cakon_mooring_gear",54.28,9.0,.85,.19)
        put("cakon_staved_barrel",59.15,12.4,.88,1.13)
    elif w.mid==ARENA:
        for x,z,size in ((20.8,40.68,1.09),(26.4,42.28,1.26),(37.2,42.14,1.02),
                         (45.71,41.28,1.23),(49.86,40.91,1.11)):
            put(ROCK,x,z,size,.35*x)
        for x,z,size in ((22.43,38.60,.80),(29.50,40.83,.79),(37.80,41.80,.83),(45.20,38.75,.74)):
            lamp(x,z,size)
        put(DOCK,32.44,40.01,.89,.06)
        put(BALES,42.12,38.5,.88,.28)
    elif w.mid=="M480":
        for x,z,s in ((26.9,9.6,.94),(34.1,13.5,1.19),(43.3,12.3,1.22),(50.5,20.6,.96),
                      (58.8,16.8,.96),(64.9,17.8,.94)):
            put(ROCK,x,z,s,.38*x)
        put(DOCK,38.32,14.27,1.,.04)
        put("floating_flowers_work_skiff",36.30,16.91,.53,-.39,y=1.065)
        put("cakon_mooring_gear",36.94,15.50,.58,.27,y=1.52)
        for x,z,s in ((27.09,9.6,.80),(33.1,11.4,.89),(39.5,14.02,.76),(44.73,17.90,.85),(62.65,16.19,.81)):
            lamp(x,z,s)
    else:
        for x,z,s in ((27.4,11.85,.76),(38.05,9.90,.85),(44.8,17.47,1.11),(54.4,21.47,1.16),
                      (66.67,13.87,.98),(74.9,15.57,.93)):
            put(ROCK,x,z,s,.44*x)
        for x,z,scale in ((33.7,11.52,1.06),(39.8,12.76,.89),(46.49,16.48,1.02),(54.5,21.85,.91),
                          (60.25,14.90,1.1),(72.5,13.28,1.06)):
            put(BALES,x,z,scale,.20*x)
        put(DOCK,55.51,19.89,1.12,.20)
        for x,z,s in ((31.42,9.68,.91),(37.82,11.22,1.05),(44.85,16.11,.86),(52.20,20.56,1.08),(68.34,14.96,1.09)):
            lamp(x,z,s,stone=False)
    return {"placements":props,"poolLights":lights,"hideStockScenery":True,
            **({} if road else {"renderPreset":"rt_hd2d_snake_den"})}


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials(repo)
    sources={key:build_diorama_mesh(key,key,extents,main_component=True) for key,extents in (
        (ROCK,(2.6,1.62,1.76)),(DOCK,(3.21,.83,2.29)),(BALES,(1.32,.91,1.12))
    )}
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    proof={}
    for mid in MAPS:
        world,_=gm.make(mid)
        terrain,water,quads=build_geometry(gm,world)
        prefix=SEA if mid=="M470" else POOL
        row=dress(gm,world)
        row.update(terrain=terrain,water=water,
                   waterSequence={"prefix":prefix,"frames":64 if mid=="M470" else 32,
                                  "seconds":20.5 if mid=="M470" else 24.})
        index[mid]=row
        proof[mid]={"terrain_quads":quads,"placements":len(row["placements"]),"decks":sum(p[0]==DOCK for p in row["placements"])}
    manifest.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"yasuki-coast-layout.json").write_text(json.dumps({"maps":proof,"sources":sources},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
