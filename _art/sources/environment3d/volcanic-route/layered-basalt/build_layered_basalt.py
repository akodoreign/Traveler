"""Build revised basalt ravines and crossings over the checked volcanic maps."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import volcanic_route as first
from build_furnace import grid_surfaces
from build_hoshi_stall import box
from export_coast import Geometry, export

STAGE = HERE / "native_environment"
TEX = STAGE / "tex"
MAPS = first.MAPS
ASH = "basalt_revision_ash"
TRAIL = "basalt_revision_tread"
GLASS = "basalt_revision_glass"
SCREE = "basalt_revision_scree"
INDIGO = "basalt_revision_indigo"
OXIDE = "basalt_revision_oxide"
STONE = "basalt_revision_stone"
SHRINE_LACQUER = "basalt_revision_shrine_lacquer"
SHRINE_CEDAR = "basalt_revision_shrine_cedar"
SHRINE_ROOF = "basalt_revision_shrine_roof"
SHRINE_FOOT = "basalt_revision_shrine_foot"
NORMAL = "basalt_revision_normal.png"
PALETTE = {
    ASH: ((48,34,72), .88),
    TRAIL: ((145,100,62), .86),
    GLASS: ((32,24,57), .76),
    SCREE: ((76,48,88), .88),
    INDIGO: ((48,39,98), .85),
    OXIDE: ((114,47,48), .87),
    STONE: ((127,81,68), .83),
    SHRINE_LACQUER: ((202,38,35), .79),
    SHRINE_CEDAR: ((63,29,41), .94),
    SHRINE_ROOF: ((57,73,108), .75),
    SHRINE_FOOT: ((91,58,88), .89),
}
MATERIALS = {k:(k+".png",rough) for k,(_,rough) in PALETTE.items()}
NORMALS = {k:NORMAL for k in (ASH,GLASS,SCREE,INDIGO,OXIDE,STONE,TRAIL,SHRINE_FOOT)}


def pigments():
    src = first.SOURCE_IMAGES
    image = np.asarray(Image.open(src/"rock_01_diff_1k.jpg").convert("L"),dtype=float)
    broad = gaussian_filter(image,8.,mode="wrap")
    medium = gaussian_filter(image,3.2,mode="wrap")
    relief = broad+.58*(medium-broad)
    relief = np.clip((relief-np.median(relief))/(relief.std()*2.7),-.88,.99)
    gy,gx = np.indices(image.shape,dtype=float)
    vein = .68*np.sin(gx*.024+gy*.020) + .32*np.cos(gx*.013-gy*.041)
    for name,(rgb,_) in PALETTE.items():
        strength = .12 if name in (SHRINE_LACQUER,SHRINE_CEDAR,SHRINE_ROOF) else .34
        tex = np.array(rgb)[None,None,:]*(1+strength*relief[...,None])
        if name in (ASH,INDIGO,GLASS,SCREE):
            highlight = np.maximum(.0,vein+relief*.36-.3)[...,None]
            tex += highlight*np.array([12.,4.,17.])
        first.write_image(name+".png",tex)
    normal = np.asarray(Image.open(src/"rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=float)/127.5-1.
    normal = gaussian_filter(normal,(3.,3.,0),mode="wrap")
    normal[...,:2] *= .76
    normal /= np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-8)
    first.write_image(NORMAL,(1+normal)*127.5)


def strip(geo,left,right,materials,axis):
    for i,name in enumerate(materials):
        if name is None:
            continue
        points=[left[i],right[i],right[i+1],left[i+1]]
        if axis=="z":
            points.reverse()
        first.quads(geo,points,name,3.05 if name!="lava" else 2.65)


def top(w,x,z):
    return first.top(w,max(0.,x),max(0.,z))


def dry_map(w,gm,front=0):
    tile=np.where(w.blk!=0,1,0)
    tile[w.blk==gm.STONEW]=2
    tile[w.blk==gm.LAVA]=0
    tile[:front]=0
    rear=28 if w.mid=="M442" else 32
    tile[rear:]=0
    solid,_ = grid_surfaces(tile,w.hgt,("",ASH,TRAIL),wall_style=INDIGO,fluid=3)
    return solid


def layered_cliffs(w,geo,toe,upper):
    # Bands follow geological layers and follow the same native upper shelf.
    stop = w.w*.5
    tail = w.d*.5-toe
    xs = np.linspace(0.,stop,int(stop/.26)+1)
    bands = np.array([-.25,.42,.88,1.77,2.92,5.10,tail+1.8])
    amounts = (0.,.22,.44,.58,.84,1.06,1.02)
    layers = (SCREE,INDIGO,GLASS,INDIGO,SCREE,INDIGO)
    edge=[]
    for x in xs:
        shoulder=upper(x)
        cap=max(shoulder+.88,top(w,x,w.d*.5-.25))
        folds=.44*np.sin(x*.53)+.25*np.cos(x*1.11)+.24*np.cos(x*.192)
        rise=.55*np.cos(x*.39)+.31*np.sin(x*.76)+.28*np.sin(x*1.89)
        line=[]
        for k,(d,t) in enumerate(zip(bands,amounts,strict=True)):
            a_k = 0. if k==0 else (.18*np.cos(x*1.72+k)+.12*np.sin(x*3.07-k))*(1-t*.55)
            z=toe+d+folds*(.48+.38*t)+a_k
            y=shoulder+(cap-shoulder)*t+rise*t+.14*np.sin(x*3.32+k)*t
            line.append((x,z,y))
        edge.append(line)
    for a,b in zip(edge[:-1],edge[1:]):
        strip(geo,a,b,layers,"x")
    for line,flip in ((edge[0],True),(edge[-1],False)):
        for p,q in zip(line[:-1],line[1:]):
            points=[p,q,(q[0],q[1],q[2]-2.1),(p[0],p[1],p[2]-2.1)]
            first.quads(geo,points[::-1] if flip else points,INDIGO)


def stone_cluster(geo,x,z,y,dx,dz,h,seed,body=INDIGO):
    angles=np.arange(9)*np.pi/4+seed
    outline=.91+.12*np.sin(angles*3+seed)+.09*np.cos(angles*5+seed)
    flank=[(x+dx*np.cos(a)*b,z+dz*np.sin(a)*b) for a,b in zip(angles,outline,strict=True)]
    rim=[(x+.70*(u-x)+.16*dx,z+.72*(v-z),y+h*(.71+.22*np.sin(3*a+seed)))
         for a,(u,v) in zip(angles,flank,strict=True)]
    top_center=(x+.19*dx,z-.21*dz,y+h*.97)
    for i,((a,b),(c,d)) in enumerate(zip(flank[:-1],flank[1:])):
        p,q=rim[i:i+2]
        first.quads(geo,[(c,d,y),(a,b,y),p,q],body,1.72)
        first.quads(geo,[p,q,top_center,top_center],body,1.72)


def stair_ravine(w,gm,cliffs=layered_cliffs):
    solid,liquid=dry_map(w,gm,front=15),Geometry()
    cliff_y=lambda x:top(w,x,13.74)+.035
    cliffs(w,solid,14.,cliff_y)
    xs=np.unique(np.r_[np.linspace(0.,w.w*.5,351),13.2,70.4])
    grade_x=(0.,24.65,25.35,36.62,37.37,48.65,49.35,60.65,61.41,w.w*.5)
    grade_y=(1.03,1.03,1.53,1.53,2.03,2.03,2.53,2.53,3.03,3.03)
    sections=[]
    centerline=[]
    for x in xs:
        base=float(np.interp(x,grade_x,grade_y))
        floor=base-.11+.025*np.sin(x*1.02)
        c=3.48+.65*np.sin(x*.403)+.31*np.cos(x*.821)
        span=max(.04,min(1.,(x-13.2)/1.1,(70.4-x)/1.1))
        width=(.47+.12*np.sin(x*.89)+.058*np.cos(x*1.78))*span
        h0=.28*np.sin(x*.63)+.14*np.cos(x*1.21)
        lo,hi=c-width,c+width
        lip=hi+.86+.13*np.sin(x*1.23)
        upper=top(w,x,7.55)+.049
        sections.append([
            (x,-1.8,base+.15+h0*.37),(x,.10,base+.21+h0),
            (x,lo-.89-.11*np.cos(x*1.3),base+.24+h0*.39),(x,lo-.24,base+.04),
            (x,lo,floor),(x,hi,floor),(x,hi+.20,base+.09+h0*.16),
            (x,lip,base+.80+h0*.44),(x,6.60+.10*np.sin(x*1.99),upper-.34+h0*.24),
            (x,7.51,upper),
        ])
        centerline.append((x,c,floor,lo,hi))
    keys=(INDIGO,SCREE,GLASS,OXIDE,None,GLASS,OXIDE,INDIGO,SCREE)
    for i,(a,b) in enumerate(zip(sections[:-1],sections[1:])):
        wet=13.2<=xs[i] and xs[i+1]<=70.4
        strip(solid,a,b,keys if wet else (*keys[:4],ASH,*keys[5:]),"x")
        if wet:
            strip(liquid,a[4:6],b[4:6],("lava",),"x")
    first.stair_treads(w,solid)
    solid.materials=[TRAIL if k==first.TREAD else k for k in solid.materials]
    for i,x in enumerate(np.linspace(14.4,69.4,25)):
        row=centerline[int(np.argmin(abs(xs-x)))]
        z=row[3]-.47 if i%2 else row[4]+.72
        y=row[2]+(.23 if i%2 else .56)
        stone_cluster(solid,x,z,y,.44+.26*(i%3),.30+.14*(i%2),.32+(i%4)*.11,i*.71,
                      INDIGO if i%3 else SCREE)
    effects=[centerline[int(np.argmin(abs(xs-x)))][:3] for x in np.linspace(15.8,67.3,14)]
    return solid,liquid,effects


def crater_basin(w,gm,cliffs=layered_cliffs,pool_radius=None):
    solid,liquid=dry_map(w,gm),Geometry()
    cliffs(w,solid,16.,lambda x:top(w,x,15.72)+.043)
    first.crater_shrine(solid)
    palette = {first.RED:SHRINE_LACQUER,first.CEDAR:SHRINE_CEDAR,
               first.COPPER:SHRINE_ROOF,first.STONE:SHRINE_FOOT}
    solid.materials=[palette.get(style,style) for style in solid.materials]
    a,b,c,d=34.5,44.5,7.5,14.5
    cells=np.argwhere(w.blk==gm.LAVA)
    assert tuple(cells.min(axis=0))==(15,69) and tuple(cells.max(axis=0))==(28,88)
    cx,cz=39.45,10.95
    corners=[np.arctan2(z-cz,x-cx)%(2*np.pi) for x in (a,b) for z in (c,d)]
    angles=np.unique(np.r_[np.linspace(0.,2*np.pi,193),corners])
    rings=[]
    for angle in angles:
        u,v=np.cos(angle),np.sin(angle)
        rim_t=min((b-cx)/u if u>1e-7 else (a-cx)/u if u<-1e-7 else np.inf,
                  (d-cz)/v if v>1e-7 else (c-cz)/v if v<-1e-7 else np.inf)
        x,z=cx+rim_t*u,cz+rim_t*v
        edge_y=top(w,x+.031*u,z+.031*v)+.049
        lobe=.53+.055*np.sin(angle*5+.3)+.038*np.cos(angle*9-.5)
        if pool_radius is not None:
            lobe=pool_radius(angle,rim_t)
        wobble=.11*np.sin(angle*17)+.07*np.sin(angle*11)
        crest=max(2.10,edge_y*.77+.53)+.10*np.sin(angle*13)+.058*np.cos(angle*25)
        radial=np.array([0.,lobe,lobe+.10,lobe+.17,.82,.91,1.])*rim_t
        height=(1.578,1.578,1.72+wobble*.4,1.87+wobble*.82,crest,crest*.66+edge_y*.34,edge_y)
        rings.append([(cx+r*u,cz+r*v,y) for r,y in zip(radial,height,strict=True)])
    for p,q in zip(rings[:-1],rings[1:]):
        polygon=[p[0],p[1],q[1],q[1]]
        first.quads(liquid,polygon,"lava",2.5)
        for i,style in enumerate((GLASS,OXIDE,INDIGO,GLASS,SCREE),1):
            first.quads(solid,[p[i],p[i+1],q[i+1],q[i]],style,1.9)
    for i in range(5,len(rings)-1,12):
        x,z,y=rings[i][4]
        stone_cluster(solid,x,z,y-.09,.32+(i%7)*.044,.29+(i%5)*.061,.15+(i%6)*.07,
                      i*.194,INDIGO if i%4==1 else GLASS)
    # The low foreground scree follows the existing barrier below the terrace.
    for i,x in enumerate(np.linspace(15.,53.,23)):
        z=3.49+.53*np.sin(x*.72)
        stone_cluster(solid,x,z,2.52,.45+(i%5)*.17,.43+(i%3)*.16,.24+(i%4)*.14,i*.9,SCREE)
    effects=[(cx+np.cos(t)*1.63,cz+np.sin(t)*.97,1.594)
             for t in np.linspace(.4,2*np.pi- .29,10)]
    return solid,liquid,effects


def arena_width(z):
    taper=.28+.72*np.clip(np.minimum(z-21.5,45.5-z),0.,1.7)/1.7
    return np.maximum(.05,(.57+.11*np.cos(z*.46))*taper+.08*np.sin(z*3.69)+.052*np.cos(z*4.82))


def plain_crossing(solid):
    for i in range(8):
        z=29.89+i*.53
        drift=.07*np.sin(i*1.11)
        x=29.93+drift
        box(solid,(x,z,.547),(4.37-.18*np.cos(i),.505,.025),STONE,1.4)


def arena_crossing(w,catalog,cliffs=layered_cliffs,crossing=plain_crossing):
    solid,liquid=Geometry(),Geometry()
    cliffs(w,solid,46.,lambda _: .537)
    gz,gx=np.indices(w.hgt.shape)
    nz=(gz+.5)*.5
    wet=((abs((gx+.5)*.5-first.arena_river_center(nz))
          < arena_width(nz))&(nz>=21.5)&(nz<45.5)
         &((nz<29.5)|(nz>=34.5)))
    formations=first.battle_audit(catalog,wet)
    zs=np.unique(np.r_[np.linspace(0.,46.,216),21.5,29.5,34.5,45.5])
    transitions=[]
    for z in zs:
        c=first.arena_river_center(z)
        width=arena_width(z)
        lo,hi=c-width,c+width
        grit=.11*np.sin(z*1.11)+.08*np.cos(z*2.1)
        rock=.61+grit*.46
        shoulder=.46+.16*np.cos(z*1.28)
        transitions.append([
            (0.,z,.547),(c-6.9-.56*np.sin(z*.72),z,.546),
            (lo-1.87-.36*np.cos(z*.38),z,.548),(lo-shoulder,z,rock),
            (lo-.10,z,.565),(lo,z,.411),(hi,z,.411),(hi+.09,z,.56),
            (hi+shoulder+.10,z,rock),(hi+2.06+.34*np.sin(z*.86),z,.547),
            (c+7.2+.53*np.cos(z*.67),z,.548),(64.,z,.547),
        ])
    keys=(ASH,ASH,ASH,GLASS,OXIDE,None,OXIDE,GLASS,ASH,ASH,ASH)
    for i,(a,b) in enumerate(zip(transitions[:-1],transitions[1:])):
        active=21.5<=zs[i] and zs[i+1]<=45.5
        dry=29.5<=zs[i] and zs[i+1]<=34.5
        if active and not dry:
            strip(solid,a,b,keys,"z")
            strip(liquid,a[5:7],b[5:7],("lava",),"z")
        else:
            aa=[(x,z,.547) for x,z,_ in a]
            bb=[(x,z,.547) for x,z,_ in b]
            strip(solid,aa,bb,(ASH,)*len(keys),"z")
    # Broad dry slabs lie nearly flush with the unchanged native battle floor.
    crossing(solid)
    for i,z in enumerate((23.4,25.6,27.6,37.4,38.8,40.6,42.3,43.5,44.5)):
        s=-1 if i%2 else 1
        x=first.arena_river_center(z)+s*(1.4+.19*np.cos(z))
        stone_cluster(solid,x,z,.548,.22+.13*(i%3),.25+.092*(i%4),.14+.065*(i%4),i*.53,INDIGO)
    for i,x in enumerate(np.linspace(8.5,55.5,18)):
        z=42.6+(i%3)*.8
        if abs(x-first.arena_river_center(z))<3.2:
            continue
        stone_cluster(solid,x,z,.54,.61+.22*(i%5),.42+.12*(i%4),.42+.18*(i%3),i*.73,INDIGO)
    effects=[(first.arena_river_center(z),z,.421) for z in (22.7,24.2,26.7,28.4,35.8,37.8,39.4,42.9,44.3)]
    return solid,liquid,effects,formations


def build(repo):
    live=repo/"_tools/rpgcobo-tool"
    cat=first.read_json(live/first.CATALOG)
    original=first.read_json(HERE.parent/"oracle-volcanic-receipt.json")
    gm=first.game_definition(repo)
    TEX.mkdir(parents=True,exist_ok=True)
    first.STAGE=first.export_coast.STAGE=STAGE
    first.TEX=TEX
    pigments()
    earlier=first.read_json(HERE.parent/"native_environment/index.json")
    retained={mid:{**row,"terrain":None,"water":None,
                   "placements":[p for p in row["placements"] if p[0]!=first.SHELF]}
              for mid,row in earlier.items() if mid in MAPS}
    for path,data in first.resource_files(HERE.parent/"native_environment",retained).items():
        (STAGE/path).write_bytes(data)
    for i in range(first.FLAMES):
        name=f"{first.FLOW}{i:02d}.png"
        (TEX/name).write_bytes((HERE.parent/"native_environment/tex"/name).read_bytes())
    rows,report = {},{}
    for mid in MAPS:
        world_hash=first.digest((live/f"project/data/mapdata/{mid}.bw").read_bytes())
        catalog_hash=first.digest(json.dumps(cat[mid],sort_keys=True).encode())
        prior=original["maps"][mid]
        assert (catalog_hash,world_hash)==(prior["catalog_hash"],prior["world_hash"]),mid
        world,events=gm.make(mid)
        assert all(cat[mid]["event"][key]["pos"]==item["pos"] for key,item in events.ev.items() if "pos" in item)
        formation=None
        if mid=="M442":
            ground,melt,effects=stair_ravine(world,gm)
        elif mid=="M443":
            ground,melt,effects=crater_basin(world,gm)
        else:
            ground,melt,effects,formation=arena_crossing(world,cat)
        name=mid.lower()+"_layered_basalt"
        export(name,ground,MATERIALS,normal_maps=NORMALS,smooth_materials=(ASH,SCREE,INDIGO))
        export(name+"_melt",melt,{"lava":(first.FLOW+"00.png",.49)})
        lamps=[row for row in earlier[mid]["poolLights"] if row[4]>3.0]
        glow=[[x,y+.42,z,4.05,1.62,0xff7634ff] for x,z,y in effects]
        pops=[[x,y+.032,z,.47+.09*(i%4),i*1.19,.13+.071*(i%4)] for i,(x,z,y) in enumerate(effects)]
        rows[mid]={**retained[mid],"terrain":name,"water":name+"_melt",
                   "poolLights":lamps+glow,"magmaSpatter":pops}
        report[mid]={"catalog_hash":catalog_hash,"world_hash":world_hash,"terrain_quads":len(ground.faces),
                     "liquid_quads":len(melt.faces),"effects":len(effects)}
        if formation is not None:
            report[mid]["formations"]=formation
    (STAGE/"index.json").write_text(json.dumps(rows,separators=(",",":")),encoding="utf8")
    files={name:first.digest(data) for name,data in first.resource_files(STAGE,rows).items()}
    (HERE/"oracle-volcanic-receipt.json").write_text(json.dumps({"maps":report,"files":files},indent=2),encoding="utf8")


def stage(repo,profile):
    first.HERE=HERE
    first.STAGE=STAGE
    first.stage(repo,profile)


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
        stage(args.repo.resolve(),args.profile.resolve())
