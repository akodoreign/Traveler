"""Appoint the Snake Den's rebuilt rooms with dry limestone, sand, and jade."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, gaussian_filter, zoom

from build_cakon_paddy_hut import cane
from build_furnace import grid_surfaces
from build_hoshi_stall import box
from build_iuchi_tower import lift_floor, tint_texture
from build_kaiu_kit import MATS as CORE, faces, world_mesh
from diorama_trees import build_diorama_mesh
from export_coast import Geometry, STAGE, export
from publish_castle_gates import resource_files
from snake_den_worlds import MAPS, variant

HERE=Path(__file__).resolve().parent
STONE="snake_den_veined_stone"
ONYX="snake_den_onyx"
FLOOR="snake_den_damp_floor"
PATH="snake_den_worn_path"
SAND="snake_den_ritual_sand"
SOOT="snake_den_dark_sand"
GOLD="snake_den_gold_vein"
VEIN="snake_den_lapis_seam"
IVORY="snake_den_ivory"
JADE="snake_den_carved_jade"
EYE="snake_den_jade_inlay"
CEDAR="snake_den_dark_cedar"
WATER="snake_den_dark_water"
STATUE="snake_den_coiled_guardian"
CALCITE="snake_den_calcite_cluster"
ARCH="snake_den_open_serpent_jaw"
LANTERN="snake_den_stone_lantern"
LANTERN_PAPER="snake_den_lantern_paper.png"
MATS={**CORE,**{key:(key+".png",.92) for key in (STONE,FLOOR,PATH,SAND,SOOT,JADE,EYE,CEDAR,GOLD,VEIN,IVORY,ONYX)},
      JADE:(JADE+".png",.33), WATER:(WATER+"00.png",.39),
      "glow":(EYE+".png",.44)}
NORMALS={JADE:JADE+"_normal.png",**{key:"snake_den_stone_normal.png" for key in (STONE,VEIN,ONYX,FLOOR)}}
SHARED=("smooth_hoshi_trade_chest",)


def materials(repo):
    source=repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    for name,data in resource_files(source,{"set":{"placements":[[key] for key in SHARED]}}).items():
        (STAGE/name).write_bytes(data)
    for key,color,contrast in (
        (STONE,(22,39,77),.19),(FLOOR,(28,51,77),.14),(PATH,(102,67,34),.13),
        (SAND,(224,159,59),.083),(SOOT,(16,25,44),.10),(JADE,(10,111,68),.19),
        (CEDAR,(62,30,24),.108),(GOLD,(215,133,38),.097),
        (VEIN,(21,58,103),.13),(IVORY,(226,208,148),.075),(ONYX,(10,21,48),.14),
    ):
        tint_texture(key,"kaiu_cedar" if key==CEDAR else "snake_den_vein_cut_limestone",color,contrast)
    scanned_stone_materials()
    jade_material()
    Image.new("RGB",(8,8),(255,176,57)).save(STAGE/"tex"/LANTERN_PAPER)
    Image.new("RGB",(8,8),(58,222,145)).save(STAGE/"tex"/(EYE+".png"))
    z,x=np.mgrid[0:2*pi:256j,0:2*pi:256j]
    for step in range(32):
        t=step*pi/16
        wave=np.sin(3*z+2*x+t+.61*np.cos(3*x-z))
        pearl=np.clip(wave,0,1)**12
        rgb=np.array([7,85,96])+((wave*6.2+pearl*13)[...,None]*[.47,.97,1.11])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{WATER}{step:02}.png")


def jade_material():
    from build_hoshi_stall import periodic

    scan=Image.open(HERE/"surface_sources/iuchi_jade_wall_scan.png").convert("RGB")
    raw=periodic(scan,512) @ [.23,.61,.16]
    fine=gaussian_filter(raw,1.1,mode="wrap")
    veins=gaussian_filter(raw,11.,mode="wrap")-gaussian_filter(raw,39.,mode="wrap")
    veins=np.clip(veins/max(veins.std(),1.),-2.3,2.3)
    facets=gaussian_filter(raw,3.7,mode="wrap")-gaussian_filter(raw,18.,mode="wrap")
    height=.53*fine+.47*gaussian_filter(raw,6.,mode="wrap")+.52*facets+3.1*veins
    du=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.065
    dv=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.065
    normal=np.stack((-du,dv,np.ones_like(du)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(STAGE/"tex/snake_den_carved_jade_normal.png")
    base=np.array([5.,114.,62.])
    rim=np.clip(veins+.23,0.,2.3)**1.5
    color=base + rim[...,None]*[5.1,23.5,14.] + (fine-np.median(fine))[...,None]*[.22,.41,.28]
    Image.fromarray(np.uint8(np.clip(color,0,255))).save(STAGE/"tex"/(JADE+".png"))


def scanned_stone_materials():
    # Poly Haven Rock 01 by Rob Tuytel, CC0. Retint the diffuse while
    # preserving its mineral detail and use its actual scan normal.
    data=np.asarray(Image.open(HERE/"surface_sources/rock_01_diff_1k.jpg").convert("RGB"))
    luminance=data @ [.23,.61,.16]
    value=np.clip((luminance-np.median(luminance))/max(1.,luminance.std()),-2.25,2.25)
    for key,color,strength in ((STONE,(25.,48.,100.),.136),(VEIN,(25.,76.,137.),.165),
                                (ONYX,(13.,29.,71.),.15),(FLOOR,(30.,58.,91.),.114)):
        rgb=np.asarray(color)*(1.+strength*value[...,None])
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/(key+".png"))
    shape=Image.open(HERE/"surface_sources/rock_01_nor_gl_1k.jpg").convert("RGB")
    normals=np.asarray(shape).astype(float)/127.5-1.
    normals[...,:2]*=.65
    normals/=np.linalg.norm(normals,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(((normals+1.)*127.5).clip(0,255))).save(STAGE/"tex/snake_den_stone_normal.png")


def quad(geom,points,key,scale=1.):
    geom.quad(points,[(p[0]/scale,(p[1]+p[2])/scale) for p in points],key)


def stone_taper(geom, start, finish, base, tip, material, sides=7, seed=0):
    start, finish = np.asarray(start), np.asarray(finish)
    axis = finish-start
    axis /= np.linalg.norm(axis)
    across = np.cross(axis, [1., 0., 0.])
    across /= np.linalg.norm(across)
    tangent = np.cross(axis, across)
    angles = np.linspace(0., 2*pi, sides, endpoint=False)
    ring = [across*cos(a)+tangent*sin(a) for a in angles]
    roots = [start + base*(1.+.14*cos(i*2.8+seed))*ray for i,ray in enumerate(ring)]
    caps = [finish + tip*ray for ray in ring]
    for n in range(sides):
        j = (n+1)%sides
        quad(geom, [roots[n], roots[j], caps[j], caps[n]], material, .81)


def rock_shoulders(arch):
    # These are the visible surface of the solid flanks in the M427
    # collision map. The central passage is open behind the jade front.
    for side in (-1,1):
        rows=(
            ((1.65,.65,0.),(2.30,.63,1.53),(2.37,.50,2.30),(1.91,.57,3.47),(1.19,.61,4.73)),
            ((3.22,-.25,.015),(3.35,-.48,1.40),(3.17,-.29,2.62),(2.96,-.03,3.74),(2.14,.21,5.38)),
            ((4.07,-.08,.0),(4.45,-.17,1.28),(4.20,.01,2.75),(3.87,.39,4.32),(3.75,.85,5.76)),
            ((5.67,.44,0.),(5.92,.42,1.59),(5.71,.75,2.98),(5.43,.70,4.67),(5.25,1.07,6.13)),
            ((7.15,1.00,.0),(7.30,1.13,1.72),(7.49,1.37,3.06),(7.15,1.68,4.51),(6.74,1.83,5.68)),
        )
        ribs=[[(x*side,z,y) for x,z,y in row] for row in rows]
        for j,(inner,outer) in enumerate(zip(ribs,ribs[1:])):
            for i in range(4):
                face=[inner[i],outer[i],outer[i+1],inner[i+1]]
                if side<0:
                    face.reverse()
                corners=np.asarray(face)
                center=corners.mean(axis=0)+[side*.14*sin(j+i),-.21+.14*cos(j*3.2+i),.18*cos(j-i)]
                for k,(a,b) in enumerate(zip(corners,np.roll(corners,-1,axis=0))):
                    wedge=[a,b,center,center]
                    mineral=j==0 and i in (1,2) and k!=(1 if side>0 else 2)
                    style=JADE if mineral else STONE
                    quad(arch,wedge,style,2.53)
                    quad(arch,wedge[:1]+wedge[2:3]+wedge[1:2]+wedge[1:2],style,2.53)
        for i,(a,b) in enumerate(zip(ribs[-1],ribs[-1][1:])):
            cap=[a,(a[0]*1.13,3.04,a[2]-.30),(b[0]*1.13,3.20,b[2]-.42),b]
            quad(arch,cap,STONE,2.53)
            quad(arch,cap[::-1],STONE,2.53)
        crown=[r[-1] for r in ribs]
        for i,(a,b) in enumerate(zip(crown,crown[1:])):
            face=[a,b,(b[0],2.85,b[2]+.22),(a[0],2.83,a[2]+.35)]
            quad(arch,face,ONYX if i%2 else STONE,2.53)
            quad(arch,face[::-1],ONYX if i%2 else STONE,2.53)
    for side in (-1,1):
        face=[(side*2.17,.31,5.39),(side*1.20,.43,4.73),
              (0.,.35,4.58),(0.,.80,6.56)]
        quad(arch,face,STONE,2.11)
        quad(arch,face[::-1],STONE,2.11)
        face=[(side*2.17,.31,5.39),(0.,.80,6.56),(0.,2.93,6.32),(side*2.17,2.82,5.66)]
        quad(arch,face,ONYX,2.11)
        quad(arch,face[::-1],ONYX,2.11)


def relief_arch():
    arch=Geometry()
    rock_shoulders(arch)
    phi=np.linspace(0.,pi,25)
    fronts=[]
    for angle in phi:
        sign=abs(cos(angle))
        fronts.append(np.array([
            [1.57*cos(angle),-.41,1.50+1.19*sin(angle)],
            [2.04*cos(angle),-.77,1.25+1.93*sin(angle)],
            [2.77*cos(angle),-.90+.30*sign,.83+3.09*sin(angle)],
            [3.63*cos(angle),-.22,.40+4.22*sin(angle)],
            [3.35*cos(angle),1.28,.39+4.04*sin(angle)],
        ]))
    for n,(left,right) in enumerate(zip(fronts,fronts[1:])):
        for strip,style in enumerate((JADE,JADE,JADE,STONE)):
            panel=[left[strip],right[strip],right[strip+1],left[strip+1]]
            quad(arch,panel,style,1.25)
            quad(arch,panel[::-1],style,1.25)
        mouth=[left[0],left[0]+[0.,2.79,.21],right[0]+[0.,2.79,.21],right[0]]
        quad(arch,mouth,SOOT,1.48)
        quad(arch,mouth[::-1],SOOT,1.48)
        if 2<=n<22:
            trace_left=.69*left[3]+.31*left[2]+[0.,-.028,0.]
            trace_right=.69*right[3]+.31*right[2]+[0.,-.028,0.]
            cane(arch,trace_left,trace_right,.040,GOLD,6)
    for side in (-1,1):
        x=1.53 if side>0 else -3.55
        box(arch,(x,-.38,.017),(2.02,1.97,1.51),JADE,1.35)
        for n in range(5):
            width=.67-.08*n
            cx=side*(2.29+.21*n)
            z=1.32-.19*n
            corners=[(cx-width/2,-.412,z),(cx,-.58,z-.23),
                     (cx+width/2,-.412,z),(cx,-.56,z+.15)]
            quad(arch,corners,VEIN,.64)
            quad(arch,corners[::-1],VEIN,.64)
        eye_x=side*1.67
        for n in range(12):
            a,b=2*pi*n/12,2*pi*(n+1)/12
            center=(eye_x,-.923,3.19)
            left=(eye_x+.35*cos(a),-.918,3.19+.19*sin(a)+side*.063*cos(a))
            right=(eye_x+.35*cos(b),-.918,3.19+.19*sin(b)+side*.063*cos(b))
            quad(arch,[center,left,right,right],"glow",.65)
            quad(arch,[center,right,left,left],"glow",.65)
            cane(arch,left,right,.035,GOLD,6)
        cane(arch,(eye_x+side*.045,-.947,3.02),(eye_x-side*.02,-.947,3.36),.042,SOOT,6)
        cane(arch,(side*1.19,-.90,3.53),(side*2.34,-.65,3.21),.15,JADE,7)
        for x,y,h in ((1.52,2.50,.62),(1.86,2.32,.45),(2.15,2.06,.26)):
            stone_taper(arch,(side*x,-.56,y),(side*(x-.13),-.57,y-h),.113,.008,IVORY)
    export(ARCH,arch,MATS,normal_maps=NORMALS)


def rock_vault(mesh, world, stone):
    # Sculpt the visible cliffs inside the retained solid collision. The
    # transition from floor to rock stays clear of every walkable tile.
    arena=world.mid=="M890"
    floor=.52 if arena else 1.52
    solid=zoom(stone.astype(float),2,order=0)>.5
    edge=distance_transform_edt(solid)*.25
    heights=zoom(world.hgt.astype(float),2,order=1)
    z,x=np.indices(solid.shape)*.25
    relief=.32*np.sin(x*1.84+z*.92)+.18*np.cos(z*3.78-x*1.22)+.105*np.sin(x*6.4+z*5.2)
    far_wall=(.18+.85*np.maximum(0.,np.sin(x*.25-z*.19)))*np.clip((z-(39. if arena else 14.))*.19,0.,1.)
    rear=np.clip((z-world.d*.34)/(world.d*.135),0.,1.)**1.7
    crown=rear*(9.3+2.8*np.cos(x*.096)+1.4*np.sin(x*.41))
    face_height=np.maximum(.45,(gaussian_filter(heights,1.5)+1.)*.5-floor+far_wall+relief+crown)
    slope=np.clip((edge-.19)/.96,0.,1.)
    slope=slope**.67
    y=floor+slope*face_height
    pitch=.25
    for rz,rx in np.argwhere(solid[:-1,:-1] | solid[1:,:-1] | solid[1:,1:] | solid[:-1,1:]):
        if max(y[rz,rx],y[rz+1,rx],y[rz+1,rx+1],y[rz,rx+1]) <= floor+.005:
            continue
        corners=[(x[r,c]+pitch*.5,z[r,c]+pitch*.5,y[r,c]) for r,c in
                 ((rz,rx),(rz,rx+1),(rz+1,rx+1),(rz+1,rx))]
        height=sum(p[2] for p in corners)/4.
        strata=(height*2.6+x[rz,rx]*.32+sin(z[rz,rx]*.77)*.61)%3.3
        material=VEIN if .88<strata<1.05 and sin(z[rz,rx]*.41+x[rz,rx]*.31)>.65 else STONE
        mesh.quad(corners, [((a+b*.33)/2.88,(.64*b+c)/2.50) for a,b,c in corners], material)


def stair_frame():
    mesh=Geometry()
    for i in range(7):
        box(mesh,(-.83,.17*i,.13*i),(1.66,1.33-.17*i,.157),STONE,.9)
    for x in (-.98,.85):
        box(mesh,(x,.045,.02),(.125,.122,2.17),CEDAR,.72)
    box(mesh,(-1.04,.02,2.15),(2.08,.16,.15),CEDAR,1.05)
    export("snake_den_harbour_stair",mesh,MATS)
    ladder=Geometry()
    for x in (-.43,.39):
        cane(ladder,(x,0.,0.),(x,.26,2.49),.069,CEDAR,9)
    for n in range(7):
        y=.27+n*.30
        cane(ladder,(-.40,.115*y,y),(.42,.115*y,y),.044,CEDAR,8)
    export("snake_den_boathouse_ladder",ladder,MATS)


def stone_lantern():
    mesh=Geometry()
    box(mesh,(-.28,-.28,0),(.56,.56,.13),STONE,.64)
    stone_taper(mesh,(0.,0.,.13),(0.,0.,.80),.17,.12,ONYX,8)
    box(mesh,(-.23,-.23,.72),(.46,.46,.16),STONE,.7)
    box(mesh,(-.17,-.17,.88),(.34,.34,.29),"glow",.52)
    for x in (-.188,.157):
        for z in (-.188,.157):
            box(mesh,(x,z,.88),(.031,.031,.31),ONYX,.45)
    stone_taper(mesh,(0.,0.,1.14),(0.,0.,1.41),.40,.093,STONE,8)
    stone_taper(mesh,(0.,0.,1.39),(0.,0.,1.57),.091,.023,ONYX,7)
    export(LANTERN,mesh,{**MATS,"glow":(LANTERN_PAPER,.64)},normal_maps=NORMALS)


def sand_mark(geom):
    font=ImageFont.truetype("C:/Windows/Fonts/YuGothM.ttc",92)
    bitmap=Image.new("L",(110,110))
    ImageDraw.Draw(bitmap).text((55,55),"蛇",anchor="mm",font=font,fill=255)
    mask=np.asarray(bitmap)>115
    for a,b,c,d,_ in faces(mask.astype(np.uint8)):
        x,z,u,v=32.6+a*.040,8.48+b*.040,32.6+c*.040,8.48+d*.040
        quad(geom,[(x,z,1.604),(u,z,1.604),(u,v,1.604),(x,v,1.604)],SOOT,1.0)


def cave_surface(gm,w):
    ground=copy(w)
    water=w.blk==gm.WATER
    stone=w.blk==gm.STONE
    ground.blk=np.where(stone,0,np.where(water,gm.CAVE_FLOOR,w.blk))
    ground.hgt=np.where(water,w.hgt-1,w.hgt)
    styles={gm.STONE:STONE,gm.CAVE_FLOOR:FLOOR,gm.ROAD:PATH,gm.SAND:SAND}
    mesh=world_mesh(gm,ground,styles)
    lift_floor(mesh,{FLOOR,PATH,SAND},.073)
    rock_vault(mesh,w,stone)
    if water.any():
        _,fluid=grid_surfaces(water.astype(int),w.hgt,("",WATER),wall_style=STONE,fluid=1)
        fluid.vertices=[np.asarray(p)+[0.,0.,.077] for p in fluid.vertices]
        export(w.mid.lower()+"_snake_den_pool",fluid,MATS)
    if w.mid=="M426":
        sand_mark(mesh)
        # Stone niches flank the room. The central sand lane stays wide enough to approach either door.
        for x in np.arange(25.,46.,1.45):
            z=14.95
            for y in (1.91,2.62,3.27):
                box(mesh,(x,z,y),(.32,.26,.22),JADE,.46)
                box(mesh,(x+.049,z-.014,y+.038),(.224,.040,.145),SOOT,.47)
    if w.mid=="M890":
        for x in (22.,37.,49.):
            z=43.0+.85*sin(x)
            y=.52
            box(mesh,(x,z,y),(2.6,1.38,.38),STONE,.86)
            for e in (.22,2.16):
                box(mesh,(x+e,z+.22,y+.38),(.21,.21,2.66),JADE)
    return mesh,water.any()


def dress(gm,w):
    row={"placements":[],"poolLights":[],"hideStockScenery":True,"renderPreset":"rt_hd2d_snake_den"}
    floor=.55 if w.mid=="M890" else 1.545

    def put(name,x,z,scale=1.,yaw=0.,height=None):
        row["placements"].append([name,x,floor if height is None else height,z,scale,yaw])

    def lamp(x,z,scale=1.):
        put(LANTERN,x,z,scale)
        row["poolLights"].append([x,floor+1.06*scale,z,4.9,8.4,0xffae52ff])

    if w.mid=="M425":
        put("snake_den_harbour_stair",14.88,10.10,1.0,-.06)
        for x,z,scale in ((23.,12.9,1.14),(34.3,13.1,1.02),(43.1,15.2,1.11),(55.3,13.1,.92)):
            put(STATUE,x,z,scale,.13*sin(x))
        put(STATUE,30.18,17.81,.86,-.27)
        for x,z in ((24.4,15.0),(36.0,14.85),(51.30,19.7),(56.75,17.1),(64.2,12.86)):
            put(CALCITE,x,z,.80+.20*cos(x),.54*x)
        for x,z in ((17.10,9.03),(27.4,13.01),(34.8,9.43),(43.0,11.0),(54.2,9.22),(66.45,12.49)):
            lamp(x,z,.87)
    elif w.mid=="M426":
        for x,z in ((23.00,11.7),(31.87,15.62),(43.77,15.57),(50.12,11.39)):
            put(STATUE,x,z,1.12,.12*cos(x))
            lamp(x+.75,z-.10,.74)
        for x,z in ((24.6,13.76),(52.2,13.54)):
            put(CALCITE,x,z,.95,.24*x)
    elif w.mid=="M427":
        put(ARCH,36.5,13.41,1.,0.,1.515)
        for x,z,scale in ((24.5,12.3,.92),(27.4,14.8,1.08),(41.27,12.9,1.32),(46.1,16.9,.94),(32.60,13.02,1.35),(40.24,13.36,1.53)):
            put(CALCITE,x,z,scale,.38*x)
        for x,z in ((24.12,10.46),(33.32,12.0),(39.88,12.04)):
            lamp(x,z,.84)
    elif w.mid=="M428":
        put("snake_den_boathouse_ladder",53.03,11.21,1.,0.)
        for x,z,scale in ((20.0,11.7,.95),(26.5,17.95,1.08),(42.8,13.4,1.03),(49.0,18.8,1.12)):
            put(CALCITE,x,z,scale,.33*x)
        for x,z in ((22.4,10.4),(31.8,12.87),(40.5,11.70),(49.82,10.78),(53.47,9.82)):
            lamp(x,z,.85)
        put("smooth_hoshi_trade_chest",51.02,11.83,.82,-.23)
    else:
        for x,z,scale in ((20.6,39.8,.95),(27.6,40.2,.90),(39.5,41.4,.97),(44.0,41.0,1.17)):
            put(CALCITE,x,z,scale,.59*x)
        for x,z in ((24.2,41.7),(37.2,41.8),(46.6,44.1)):
            put(STATUE,x,z,1.34,.12*cos(x))
        for x,z in ((22.8,39.6),(27.7,38.7),(39.5,40.0),(43.9,39.4)):
            lamp(x,z,.91)
    return row


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials(repo)
    detail={}
    for name,extent in ((STATUE,(1.14,1.78,1.11)),(CALCITE,(1.73,1.70,1.34))):
        detail[name]=build_diorama_mesh(name,name,extent,main_component=name==STATUE)
    stair_frame()
    stone_lantern()
    relief_arch()
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    report={}
    for mid in MAPS:
        w,events=gm.make(mid)
        mesh,water=cave_surface(gm,w)
        terrain=mid.lower()+"_order_cavern"
        export(terrain,mesh,MATS,normal_maps=NORMALS)
        row=dress(gm,w)
        row["terrain"]=terrain
        if water:
            row.update(water=mid.lower()+"_snake_den_pool",waterSequence={"prefix":WATER,"frames":32,"seconds":18.4})
        index[mid]=row
        report[mid]={"width":w.w,"depth":w.d,"placements":len(row["placements"]),"terrain_quads":len(mesh.faces),
                     "events":len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"cakon-snake-den-layout.json").write_text(json.dumps({"maps":report,"sources":detail},indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
