"""Build Hida cave wall aprons and the revised Kaiu exit masonry."""

import argparse
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import build_hida_caves as initial
from build_hoshi_stall import box
from export_coast import Geometry

base=initial.base
NAVY,COBALT,INNER,SCREE=(initial.NAVY,initial.COBALT,initial.INNER,initial.SCREE)
SLATE,BRICK,MORTAR=(initial.SLATE,initial.BRICK,initial.MORTAR)
IRON,RUST,WOOD=(initial.IRON,initial.RUST,initial.WOOD)
DECK="hida_wall_relief_paving"

FIRST_MATERIALS=initial.make_materials
FIRST_FLOOR=initial.flagstone
FIRST_DRESS=initial.dress
PALETTE={
    NAVY:((18,29,62),.88), COBALT:((23,43,87),.87), INNER:((8,14,34),.91),
    SCREE:((21,34,67),.88), SLATE:((28,42,65),.68), BRICK:((27,34,54),.86),
    MORTAR:((15,21,38),.92), IRON:((22,26,38),.79), RUST:((139,46,32),.86),
    WOOD:((70,39,30),.87), initial.GOLD:((211,125,35),.73), initial.JADE:((57,169,107),.65),
}


def make_materials():
    scan=FIRST_MATERIALS()
    for name in PALETTE:
        (initial.TEX/(name+".png")).replace(initial.TEX/(name+"_relief.png"))
    image=Image.open(initial.TEX/(BRICK+"_relief.png")).convert("RGB")
    values=np.asarray(image,dtype=float)
    z,x=np.indices(values.shape[:2],dtype=float)
    stagger=np.floor(z/161)*79.
    row=(z%161)<7
    joint=((x+stagger)%180)<7
    wear=1.+.16*np.cos(x*.013+z*.023)
    stones=np.where(row|joint,.53,wear)
    base.write_image(DECK+".png",np.clip(values*stones[...,None]+[6,10,16],0,255))
    return scan


def flagstone(w,route,scan,arena=False):
    prior=FIRST_FLOOR(w,route,scan,arena)
    image=Image.open(initial.TEX/(prior+".png")).convert("RGB")
    pixels=np.asarray(image,dtype=float)
    red,_,blue=np.moveaxis(pixels,-1,0)
    warm=np.clip((red-blue+26)/43,0.,1.)
    neutral=pixels*[.65,.62,.55]
    color=neutral+warm[...,None]*[8.5,2.,-3.5]
    name=prior+"_relief"
    base.write_image(name+".png",color)
    return name


def arch_wall(w,mesh,floor):
    # A node touching any open tile belongs to the buried apron. Interpolation
    # over both triangles then keeps the entire native playable tile clear.
    walk=w.hgt==2
    surround=np.pad(walk,((1,1),(1,1)),constant_values=False)
    touches=(surround[:-1,:-1]|surround[1:,:-1]|
             surround[:-1,1:]|surround[1:,1:])
    xs,zs=np.meshgrid(np.arange(w.w+1,dtype=float),np.arange(w.d+1,dtype=float))
    border=distance_transform_edt(~walk)-distance_transform_edt(walk)
    edge=map_coordinates(gaussian_filter(border,.62),(zs-.5,xs-.5),order=1,mode="nearest")
    source=gaussian_filter(w.hgt.astype(float),1.32)
    target=map_coordinates(source,(zs-.5,xs-.5),order=1,mode="nearest")
    swell=.27*np.sin(xs*.41+zs*.27)+.18*np.cos(xs*.32-zs*.61)+.10*np.sin(xs*.98+zs*.92)
    slope=np.clip((edge-.41)/2.16,0.,1.)
    slope=slope*slope*(3.-2.*slope)
    high=np.maximum(floor+.28,(target+1)*.5+swell)
    buried=floor-.086
    crest=buried + slope*(high-buried)
    crest[touches]=buried
    assert np.all(crest[touches]<floor)
    active=~(touches[:-1,:-1]&touches[1:,:-1]&touches[:-1,1:]&touches[1:,1:])
    # Keep the toes below the slab before skipping faces, including on the
    # diagonal cuts around cells and the lowest front cutaway shelves.
    for z,x in np.argwhere(active):
        order=((x,z),(x+1,z),(x+1,z+1),(x,z+1))
        points=[(a*.5,b*.5,float(crest[b,a])) for a,b in order]
        material=NAVY
        if edge[z,x]<2.56:
            material=SCREE
        if edge[z,x]>3.4 and swell[z,x]>.27:
            material=COBALT
        base.quads(mesh,points,material,3.45)
    outer=(
        [(x,0) for x in range(w.w,-1,-1)],[(w.w,z) for z in range(w.d,-1,-1)],
        [(x,w.d) for x in range(w.w+1)],[(0,z) for z in range(w.d+1)],
    )
    for side in outer:
        for (ax,az),(bx,bz) in zip(side[:-1],side[1:]):
            u,v=crest[az,ax],crest[bz,bx]
            if max(u,v)<=floor:
                continue
            a,b=(ax*.5,az*.5),(bx*.5,bz*.5)
            base.quads(mesh,[(*a,u),(*b,v),(*b,floor-.18),(*a,floor-.18)],NAVY,3.15)


def section(geo,x0,x1,z,y,depth,height,count):
    width=(x1-x0)/count
    box(geo,(x0,z,y),(x1-x0,depth,height),MORTAR,1.9)
    for j in range(3):
        dy=height/3
        for i in range(count):
            x=x0+i*width
            s=.012+.024*np.sin(i*.79+j*1.61)**2
            style=(NAVY,BRICK,SCREE)[(i*3+j)%5%3]
            box(geo,(x+.025,z-.08-s,y+j*dy+.019),
                (width-.05,depth+.12+s,dy-.039),style,1.8)


def crenellation(geo,item):
    x,z=item["x"]*.5,item["z"]*.5
    w,h,d=[item[k]*.5 for k in ("w","h","d")]
    y=item["y"]*.5
    section(geo,x+.008,x+w-.008,z+.033,y+.012,d-.063,h-.10,2)
    box(geo,(x+.017,z+.015,y+h-.131),(w-.034,d-.03,.131),SCREE,1.25)


def tunnel_shell(geo):
    floor=8.532
    cx=28.50
    configs=((3.30,.53,1.01),(4.08,.70,1.09),(5.36,1.20,1.13),(6.54,1.29,1.12))
    angles=np.linspace(0.,np.pi,31)
    rings=[]
    for z,half,spring in configs:
        shape=[]
        for i,a in enumerate(angles):
            y=floor+spring+1.57*np.sin(a)
            x=cx+half*np.cos(a)
            step=.018*np.sin(a*18)
            outer_x=cx+(half+.31)*np.cos(a)
            shape.append(((x,z,y),(outer_x,z,y+.31+step)))
        rings.append(shape)
    for p,q in zip(rings[:-1],rings[1:]):
        for i in range(len(angles)-1):
            a,b=p[i],p[i+1]
            c,d=q[i],q[i+1]
            shell=[a[1],b[1],d[1],c[1]]
            bore=[a[0],c[0],d[0],b[0]]
            base.quads(geo,shell,SCREE if i%4==0 else BRICK,1.6)
            base.quads(geo,bore,INNER,1.68)
            base.quads(geo,bore[::-1],INNER,1.68)
    for shell,flip in ((rings[0],False),(rings[-1],True)):
        for i,(p,q) in enumerate(zip(shell[:-1],shell[1:])):
            face=[p[0],q[0],q[1],p[1]]
            base.quads(geo,face[::-1] if flip else face,BRICK if i%4 else COBALT,1.48)
    # Occupy the two original castellated blocks in front of the arrival.
    # Behind them the roof spreads beside the bore above standing height.
    for x in (27.05,29.04):
        section(geo,x,x+.91,3.10,floor,.79,2.14,2)
        box(geo,(x+.16,3.20,floor+1.44),(.60,.54,.18),RUST,1.31)
    for x in (26.02,30.51):
        section(geo,x,x+.56,3.02,10.41,1.68,1.08,2)
        for z in (3.1,4.29,5.46):
            box(geo,(x-.04,z,10.48),(.66,.23,.21),RUST,1.28)
    for z in (3.02,4.88,6.45):
        box(geo,(26.07,z,11.60),(5.00,.24,.22),SCREE,2.4)
    box(geo,(26.20,3.07,11.50),(4.74,3.52,.13),NAVY,2.8)


def wall_top(w):
    geo=Geometry()
    floor=8.532
    initial.floor_mesh(w,geo,DECK,floor)
    # The deck texture tiles over the original full walkable shelf.
    geo.uvs[0]=[(0,0),(w.w*.5/6.3,0),(w.w*.5/6.3,w.d*.5/6.3),(0,w.d*.5/6.3)]
    far=w.w*.5
    # The long retaining wall and outside battlement sit beyond the live deck.
    section(geo,0.,far,-.92,6.08,.90,2.46,51)
    section(geo,12.9,48.15,-.81,8.54,.78,1.62,32)
    box(geo,(12.75,-.98,10.14),(35.55,.98,.19),SCREE,4.2)
    for i,x in enumerate(np.arange(13.12,47.1,1.93)):
        if 26.7<x<30.7:
            continue
        section(geo,float(x),float(x)+.93,-.79,10.30,.76,.71,2)
        if i%5==0:
            box(geo,(float(x)-.065,-1.01,8.52),(1.06,.52,1.72),BRICK,1.31)
    for item in w.objs:
        if item["t"]=="fill":
            crenellation(geo,item)
    # Low bordered pavers mark the exit line without adding a step.
    for z in np.linspace(4.04,12.17,24):
        for x in (27.27,29.24):
            box(geo,(x,z,floor+.003),(.13,.29,.009),RUST,1.29)
    tunnel_shell(geo)
    bores=[{"center":[56,10],"roof_depth_m":3.24,"axis":"z","arrival_only":True,
            "parapet_blocks":sum(o["t"]=="fill" for o in w.objs)}]
    return geo,{**initial.MATERIALS,DECK:(DECK+".png",.78)},[],bores


def dress(w,cat,route):
    placements,lights=FIRST_DRESS(w,cat,route)
    for light in lights:
        light[3]=3.75
        light[4]*=1.58
        light[5]=0xffa13bff
    if w.mid=="M158":
        placements.extend([
            [initial.BENCH,22.85,8.56,8.88,.89,0.74],
            [initial.BENCH,33.98,8.56,9.54,.83,-.61],
            [initial.DRAIN,25.72,8.54,5.83,.75,.15],
            [initial.DRAIN,31.22,8.54,5.92,.74,-.09],
            [initial.LAMP,28.97,10.49,3.73,.49,-.19],
        ])
        lights.extend([[27.11,9.45,5.77,3.27,3.5,0xff9e43ff],
                       [29.53,9.50,5.65,3.27,3.8,0xffa241ff]])
    return placements,lights


def setup(deep):
    target=HERE/"deep" if deep else HERE
    initial.HERE=target
    initial.STAGE=target/"native_environment"
    initial.TEX=initial.STAGE/"tex"
    initial.PALETTE=PALETTE
    initial.NORMAL="hida_cave_relief_normal.png"
    initial.MATERIALS={k:(k+"_relief.png",rough) for k,(_,rough) in PALETTE.items()}
    initial.make_materials=make_materials
    initial.flagstone=flagstone
    initial.natural_walls=arch_wall
    initial.wall_top=wall_top
    initial.dress=dress


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("build","stage"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    parser.add_argument("--deep",action="store_true")
    args=parser.parse_args()
    setup(args.deep)
    if args.action=="build":
        initial.build(args.repo.resolve(),initial.DEEP if args.deep else initial.FIRST,"_relief")
    elif args.profile is None:
        parser.error("--profile is required for stage")
    else:
        initial.stage(args.repo.resolve(),args.profile.resolve())
