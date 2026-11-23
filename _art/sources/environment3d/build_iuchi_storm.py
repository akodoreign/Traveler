"""Build native voxel scenery for the Iuchi siege and storm room."""

from copy import copy
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from build_iuchi_mines import MATS as SHARED
from build_iuchi_tower import ground_styles, lift_floor, save_props, tint_texture, write_rows
from build_kaiu_kit import world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from iuchi_storm_worlds import LOWER, UPPER, variant
from voxelize_coast import convert_prop, save

ROCK = "iuchi_gale_slate"
SHALE = "iuchi_gale_shale"
RIDGE = "iuchi_gale_ridge"
DIRT = "iuchi_siege_earth"
SAND = "iuchi_gale_scoured"
CANVAS = "iuchi_siege_canvas"
LINEN = "iuchi_storm_cloth"
LINTEL = "iuchi_storm_mineral"
VAPOR = "iuchi_gale_dust"
MATS = {**SHARED, **{key: (key+".png", .94) for key in
        (ROCK,SHALE,RIDGE,DIRT,SAND,CANVAS,LINEN,LINTEL,VAPOR)}}


def textures(upper):
    scans = (
        (LINEN, "iuchi_storm_woven_cloth", (27,41,76), .055),
        (LINTEL, "iuchi_storm_dais_stone", (60,72,94), .075),
    ) if upper else (
        (ROCK, "iuchi_wind_cleft_scan", (40,55,74), .069),
        (SHALE, "iuchi_wind_cleft_scan", (24,34,51), .074),
        (RIDGE, "iuchi_wind_cleft_scan", (53,70,84), .068),
        (DIRT, "iuchi_scoured_sand_scan", (112,71,48), .056),
        (SAND, "iuchi_scoured_sand_scan", (166,154,124), .047),
        (CANVAS, "ojatara_offwhite_canvas", (35,75,47), .066),
    )
    for key,scan,color,contrast in scans:
        tint_texture(key,scan,color,contrast)
    if not upper:
        Image.new("RGB",(8,8),(188,202,205)).save(STAGE/"tex"/(VAPOR+".png"))


def wind_model():
    dust=Geometry()
    uv=[(0.,0.),(0.,1.),(1.,1.),(1.,0.)]
    for x,z,w in ((0.,0.,1.03),(.37,.16,.59),(.82,-.13,.76)):
        p=[(x,z,.01),(x+w*.37,z+.037,.021),(x+w,z+.026,.096),(x+w*.34,z,.041)]
        dust.quad(p,uv,VAPOR)
        dust.quad(list(reversed(p)),uv,VAPOR)
    export("iuchi_wind_dust",dust,MATS)


def tent_roof():
    tent=Geometry()
    for x in (-1.54,1.44):
        for z in (-1.13,1.04):
            box(tent,(x,z,0.),(.11,.11,1.92),"iuchi_beam")
    for side in (-1,1):
        z=side*1.24
        corners=[(-1.7,0.,2.53),(1.7,0.,2.53),(1.7,z,1.83),(-1.7,z,1.83)]
        for quad in (corners,list(reversed(corners))):
            tent.quad(quad,[(x*.65,v*.65) for x,v,_ in quad],CANVAS)
        box(tent,(-1.72,z-.02,1.74),(3.44,.046,.102),"iuchi_oak")
    box(tent,(-1.75,-.04,2.50),(3.50,.086,.083),"iuchi_beam")
    export("iuchi_siege_pavilion",tent,MATS)


def cleft(mesh, start, end, front, base, length, rise, *, direction=1):
    """Fold the cliff face back in coarse, colored strata."""
    rng=np.random.default_rng(int(front*30))
    spans=np.linspace(start,end,max(2,int((end-start)/length)+1))
    levels=np.array([0.,.16,.36,.59,.83,1.])
    tips=spans[None,:]+rng.uniform(-.58,.58,(len(levels),len(spans)))
    tips[:,0],tips[:,-1]=spans[0],spans[-1]
    ledges=front+direction*(rng.uniform(-.32,.34,tips.shape)+levels[:,None]**2*.46)
    y=base+rise*levels[:,None]+rng.uniform(-.22,.25,tips.shape)
    y[0,:]=base
    palette=(SHALE,ROCK,ROCK,RIDGE,ROCK)
    for i in range(len(spans)-1):
        for j in range(len(levels)-1):
            quad=[(tips[v,k],ledges[v,k],y[v,k]) for v,k in ((j,i),(j,i+1),(j+1,i+1),(j+1,i))]
            if direction<0:
                quad.reverse()
            mesh.quad(quad,[(x/3.,h/2.) for x,_,h in quad],palette[(j+(i%4==0))%len(palette)])
        a0,a1=tips[-1,i:i+2]
        z0,z1=ledges[-1,i:i+2]
        y0,y1=y[-1,i:i+2]
        quad=[(a0,z0,y0),(a1,z1,y1),(a1,front+direction*5,y1-.28),(a0,front+direction*5,y0-.28)]
        if direction<0:
            quad.reverse()
        mesh.quad(quad,[(x*.34,z*.36) for x,z,_ in quad],RIDGE)


def tunnel_portal(mesh):
    center=10.25
    for i in range(9):
        a,b=(i*pi/9,(i+1)*pi/9)
        points=[(66.22,center+cos(a)*1.21,3.21+sin(a)*1.23),
                (66.22,center+cos(b)*1.21,3.21+sin(b)*1.23),
                (66.04,center+cos(b)*1.90,3.21+sin(b)*(1.97+.10*((i+1)%2))),
                (66.04,center+cos(a)*1.90,3.21+sin(a)*(1.97+.10*(i%2)))]
        uv=[(z*.64,y*.61) for _,z,y in points]
        mesh.quad(points,uv,(SHALE,ROCK,RIDGE)[i%3])
    for z in (8.31,11.45):
        box(mesh,(65.97,z,2.02),(.47,.73,1.22),ROCK)
    box(mesh,(69.76,8.97,2.01),(.12,2.55,2.46),SHALE)


def fittings(upper):
    if not upper:
        wind_model()
        tent_roof()
        gate=Geometry()
        for x in (-.18,2.04):
            box(gate,(x,-.18,0.),(.21,.42,3.43),"iuchi_beam")
            box(gate,(x-.05,-.231,0.),(.31,.52,.28),ROCK)
        box(gate,(-.335,-.22,3.0),(2.67,.52,.25),"iuchi_beam")
        box(gate,(-.475,-.29,3.30),(2.93,.65,.19),"iuchi_indigo")
        export("iuchi_wind_gate_frame",gate,MATS)
        leaf=Geometry()
        for i in range(8):
            box(leaf,(i*.242,-.036,.035),(.232,.076,2.96),
                "iuchi_oak" if i%3 else "iuchi_board_a")
        for y in (.38,1.40,2.43):
            box(leaf,(-.008,-.062,y),(1.945,.132,.079),"iuchi_beam")
        export("iuchi_wind_gate_leaf",leaf,MATS)
        return
    banner=Geometry()
    box(banner,(-.38,0.,1.42),(.76,.071,.054),"iuchi_iron")
    hem=[(-.33,.08,.16),(-.10,.12,.08),(.10,.13,.23),(.33,.09,.15)]
    for a,b in zip(hem,hem[1:]):
        corners=[(a[0],0.,1.44),(b[0],0.,1.44),b,a]
        for face in (corners,list(reversed(corners))):
            banner.quad(face,[(x+.5,y*.7) for x,_,y in face],LINEN)
    export("iuchi_storm_hanging",banner,MATS)


def terrain(gm,w):
    mid=w.mid
    if mid in LOWER:
        styles={**ground_styles(gm),gm.DIRT:DIRT,gm.ROAD:"iuchi_path",gm.SAND:SAND,
                gm.STONE:ROCK,gm.STONEW:"iuchi_light_stone"}
        art=copy(w)
        art.hgt=w.hgt.copy()
        art.blk=w.blk.copy()
        if mid in ("M409","M410","M881"):
            cliffs=art.blk==gm.STONE
            art.hgt[cliffs]=0 if mid=="M881" else 3
            art.blk[cliffs]=gm.DIRT
        elif mid=="M408":
            art.objs=[o for o in w.objs if not (o["t"]=="fill" and o["blk"]==gm.STONE and o["w"]>8)]
        mesh=world_mesh(gm,art,styles)
        lift_floor(mesh,{DIRT,"iuchi_path",SAND},.044)
        if mid=="M408":
            cleft(mesh,1.4,79.8,16.96,2.02,3.35,7.55)
            # Footpath ends beneath the actual tunnel roof and touch event.
            for i in range(16):
                x=60.02+i*.5
                box(mesh,(x,9.27,2.049),(.501,1.48,.008),DIRT)
            cleft(mesh,65.65,72.5,8.38,2.03,1.12,4.95,direction=-1)
            cleft(mesh,65.65,72.5,11.23,2.03,1.12,4.98)
            tunnel_portal(mesh)
        elif mid=="M881":
            cleft(mesh,0.,64.,44.59,.52,2.99,8.44)
        else:
            if mid=="M409":
                cleft(mesh,0.,80.99,10.23,2.04,2.13,6.43)
            else:
                cleft(mesh,0.,61.,10.23,2.04,2.13,6.43)
                cleft(mesh,65.04,80.99,10.23,2.04,2.13,6.43)
            # Use the same corridor centerline as the collision map.
            cleft(mesh,0.,80.99,4.41,2.04,2.37,1.29,direction=-1)
        return mesh

    art=copy(w)
    if mid=="M882":
        walls=w.blk==gm.STONEW
        art.hgt=np.where(walls,0,w.hgt)
        art.blk=np.where(walls,gm.PLANK,w.blk)
    mesh=world_mesh(gm,art,{**ground_styles(gm),gm.STONEW:LINTEL})
    if mid=="M882":
        box(mesh,(0.,46.46,.50),(64.,.61,1.39),LINTEL)
        box(mesh,(0.,46.46,4.29),(64.,.61,2.24),LINTEL)
        for x,width in [(0,4),*((x+3.85,5.15) for x in range(4,50,9)),(61.85,2.15)]:
            box(mesh,(float(x),46.46,1.89),(width,.61,2.40),LINTEL)
        for x in range(4,60,9):
            for a in (x-.19,x+3.85):
                box(mesh,(a,46.25,1.62),(.19,.52,2.8),"iuchi_beam")
            for y in (1.62,4.22):
                box(mesh,(x-.19,46.25,y),(4.23,.52,.19),"iuchi_beam")
        return mesh
    for row in range(15):
        z=5.04+row*.34
        joints=[2.52,5.1+row%3*.32,8.+row%4*.38,11.6+row%3*.43,14.5+row%2*.24,17.47]
        for n,(a,b) in enumerate(zip(joints,joints[1:])):
            if mid=="M411" and z>=7.18 and a<12.0 and b>8.0:
                continue
            box(mesh,(a+.004,z,1.025),(b-a-.008,.334,.025),
                "iuchi_board_a" if (row+n)%3 else "iuchi_board_b",1.33)
    if mid=="M411":
        for y,z,depth in ((1.5,7.5,1.0),(2.0,8.5,1.0),(2.5,9.5,1.0)):
            box(mesh,(8.,z,y+.022),(4.0,depth,.037),"iuchi_oak",1.24)
            box(mesh,(7.98,z-.052,y-.025),(4.04,.076,.105),"iuchi_beam")
            for x in (7.84,12.02):
                box(mesh,(x,z+.13,y+.06),(.117,.105,.87),"iuchi_beam")
                box(mesh,(x-.018,z-.035,y+.82),(.154,depth+.045,.102),"iuchi_indigo")
        return mesh

    for start,end in ((8,12),(14,18),(20,24),(26,30),(32,35)):
        for x in (start*.5-.085,end*.5):
            box(mesh,(x,10.365,1.93),(.10,.305,1.65),"iuchi_beam")
        for y in (1.93,3.51):
            box(mesh,(start*.5-.09,10.355,y),((end-start)*.5+.18,.315,.09),"iuchi_beam")
    for i in range(4):
        box(mesh,(8.522+i*.741,8.56,1.059),(.734,1.30,.042),LINTEL)
    return mesh


def layout(gm,w):
    props,lights,wind=[],[],[]
    mid=w.mid
    row={"placements":props,"poolLights":lights,"windStreaks":wind}

    def put(model,x,z,size=1.,yaw=0.,height=None,sway=0.):
        y=(int(w.hgt[z,x])+1)*.5+.03 if height is None else height
        point=[x*.5+.25,y,z*.5+.25]
        props.append([model,*point,size,yaw,*([sway] if sway else [])])
        return point

    def lamp(x,z,size=1.):
        a,y,b=put("iuchi_fitted_andon",x,z,size)
        lights.append([a,y+.50*size,b,4.,1.40])

    def drift(x,z,y,n,hazard):
        phase=(n*.61803398875)%1.
        wind.append(["iuchi_wind_dust",x,y,z,.75+n%4*.20,1.42 if hazard else .30,
                     hazard,phase,-1.7-n%3*.30,.50+n%3*.13])

    if mid=="M408":
        for x,z in ((33,31),(43,31),(53,31),(63,31),(73,31),(94,30),(105,30)):
            put("iuchi_siege_pavilion" if x<80 else "iuchi_dragon_command",
                x,z,.96 if x<80 else .87)
        put("iuchi_siege_field_hearth",45,31,1.12,.14)
        for x,z in ((39,32),(51,31),(85,33)):
            put("hoshi_inn_bench",x,z,.94,.05)
        for x,z in ((31,30),(54,31),(78,32),(99,32),(119,32),(130,18),(130,22)):
            lamp(x,z,.91)
        for x,z in ((35,31),(70,31),(95,32),(116,35),(131,17)):
            put("iuchi_dragon_standard",x,z,1.02,.24,sway=.133)
        for x,z,size in ((130,17,1.1),(131,23,.9),(134,16,1.5),(135,24,1.38),(137,16,1.44)):
            put("iuchi_wind_buttress",x,z,size,.24*x)
    elif mid in ("M409","M410","M881"):
        arena=mid=="M881"
        for x in (range(10,124,7) if arena else range(31,137,5)):
            z=90 if arena else 23+x%2
            if mid=="M410" and x in range(117,133):
                continue
            put("iuchi_wind_buttress",x,z,.74+x%5*.15,.54*x, .53 if arena else 2.03)
            if not arena and x%3==0:
                put("wind_grass",x+1,z-2,.71,.44*x,sway=.24)
        for x in np.flatnonzero((w.blk==gm.SAND).any(axis=0)):
            if (not arena and not 36<=x<=140) or x%2:
                continue
            zcoords=np.flatnonzero((w.blk[:,x]==gm.SAND) & (w.hgt[:,x]==(0 if arena else 3)))
            for n,z in enumerate(zcoords[1::5 if arena else 3]):
                drift(x*.5+.22,z*.5, .58 if arena else 2.16,x+n,not arena)
        if mid=="M410":
            row["doors"]=[{"event":2,"x":62.04,"y":2.0,"z":8.89,
                           "models":["iuchi_wind_gate_frame","iuchi_wind_gate_leaf"]}]
            for x in (122,129):
                lamp(x,16,.86)
    elif mid=="M411":
        for x,z in ((8,14),(13,18),(26,18),(29,14),(29,20)):
            lamp(x,z,.93)
        for x in (7,31):
            put("iuchi_storm_hanging",x,20,.88,0.,1.03,.08)
    elif mid=="M412":
        for x,z in ((7,14),(13,19),(26,19),(32,14)):
            lamp(x,z,.91)
        for x,z in ((8,20),(15,20),(27,20),(32,20)):
            put("iuchi_storm_broken_frame",x,z,1.02,.08*(x%3))
        for x in (12,18,24,30):
            put("iuchi_storm_hanging",x,20,.94,.055,1.56,.28)
            for i in range(2):
                drift(x*.5+.12,9.55-i*.8,1.67+i*.17,x+i,False)
    else:
        for x in (17,34,49,64,81,94,111):
            put("iuchi_storm_broken_frame",x,92,1.36,.09*(x%5))
            put("iuchi_storm_hanging",x+3,92,.98,.05,1.84,.24)
        for x in (26,50,76,102):
            lamp(x,89,1.17)
            for i in range(4):
                drift(x*.5+.25,44.0-i*1.96,.89+i*.11,x+i,False)
    return row


def main(repo,upper):
    _,_,gm,_,_=variant(repo,upper)
    import voxfile

    textures(upper)
    fittings(upper)
    if upper:
        sources=save_props((("iuchi_storm_broken_frame",(1.42,.40,1.35),43),),voxfile)
    else:
        sources=save_props((("iuchi_siege_field_hearth",(1.15,.88,1.02),44),),voxfile)
        name="iuchi_wind_buttress"
        dimensions=(2.10,1.22,1.24)
        key,points,rgb,_,source=convert_prop(name,dimensions,61,lower=.05)
        light=rgb@np.array([.23,.64,.13])
        keep=(light<166) | (np.ptp(rgb,axis=1)>25)
        points,rgb=points[keep],rgb[keep]
        points-=points.min(axis=0)
        light=rgb@np.array([.23,.64,.13])
        tint=np.clip((light-np.median(light))*.39,-19.,25.)
        color=np.clip([50,65,77]+tint[:,None],0,255)
        sources[name]=save(key,points,color,np.asarray(dimensions)/(points.max(axis=0)+1),source,voxfile)
        voxel_asset(name)
    write_rows(UPPER if upper else LOWER,gm,terrain,layout,MATS,
               ("iuchi-storm-room" if upper else "iuchi-wind-siege")+"-layout.json",sources)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve(),"--upper" in sys.argv[2:])
