"""Build irrigation rows and a clay-on-bamboo cottage in the native environment kit."""
from copy import copy
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import box
from build_iuchi_tower import lift_floor, tint_texture
from build_cakon import MATS as CORE
from build_kaiu_kit import world_mesh
from cakon_paddy_worlds import MAPS, variant
from diorama_trees import PINE, build_diorama_mesh
from export_coast import Geometry, STAGE, export

HERE=Path(__file__).resolve().parent
CLAY="cakon_tomie_red_clay"
SILT="cakon_paddy_bund"
MOSS="cakon_paddy_moss"
ASH="cakon_tomie_ash"
BAMBOO="cakon_tomie_bamboo"
HEMP="cakon_tomie_hemp"
SOOT="cakon_tomie_soot"
WATER="cakon_paddy_water"
CEDAR="cakon_paddy_cedar_mesh"
JIZO="cakon_wayside_jizo"
KAKASHI="cakon_kakashi_indigo"
DOME="cakon_tomie_fitted_dome"
RICE="cakon_rice_seedlings"
SCALES={
    "cakon_paddy_sluice":("cakon_paddy_sluice",(1.22,.52,.88),True),
    CEDAR:("cakon_cedar_diorama",(2.52,4.36,2.48),False),
    KAKASHI:("cakon_indigo_kakashi",(1.30,1.79,.48),True),
    JIZO:("cakon_paddy_jizo",(.63,1.19,.59),False),
    "cakon_tomie_drying_rack":("cakon_tomie_herb_rack",(1.62,1.31,.60),True),
    "cakon_tomie_mortar":("cakon_herb_bowl",(.48,.36,.44),False),
}
PLANT_COLORS={"rice_jade":(63,109,22),"rice_green":(91,133,28),"rice_yellow":(131,154,41)}
MATS={**CORE,**{name:(name+".png",.93) for name in (CLAY,SILT,MOSS,ASH,BAMBOO,HEMP,SOOT,*PLANT_COLORS)},
      WATER:(WATER+"00.png",.26)}


def materials():
    # Extract clay from the generated dome reference, where no reeds or background interrupt the material.
    source=HERE/"surface_sources"
    reference=Image.open(source/"cakon_tomie_clay_dome.png").convert("RGB")
    reference.crop((284,221,473,320)).save(source/"cakon_tomie_clay_contact.png")
    for key,source,color,contrast in (
        (CLAY,"cakon_tomie_clay_contact",(122,61,37),.19),
        (SILT,"cakon_paddy_mud_scan",(101,66,39),.11),
        (MOSS,"iuchi_frosted_meadow",(37,84,28),.14),
        (ASH,"cakon_river_silt_scan",(58,53,61),.11),
        (BAMBOO,"cakon_cedar_deck_scan",(139,94,45),.09),
        (HEMP,"cakon_cedar_deck_scan",(171,136,78),.08),
        (SOOT,"cakon_tomie_clay_contact",(58,33,27),.18),
    ):
        tint_texture(key,source,color,contrast)
    for key,color in PLANT_COLORS.items():
        Image.new("RGB",(8,8),color).save(STAGE/"tex"/(key+".png"))
    z,x=np.mgrid[0:2*pi:256j,0:2*pi:256j]
    for frame in range(32):
        t=frame*pi/16
        a=np.sin(4*z+x+t+.37*np.sin(2*x-z))
        b=np.sin(11*z-3*x-.4*t)
        glint=np.clip(a,0,1)**12
        rgb=np.array([30.,75.,74.])+(a*4.6+b*1.45+glint*6)[...,None]*[.62,.91,1.19]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/"tex"/f"{WATER}{frame:02}.png")


def quad(geom,v,style,repeat=1.):
    geom.quad(v,[(p[0]/repeat,(p[1]+p[2])/repeat) for p in v],style)


def cane(geom,start,end,radius,style,sides=7):
    a,b=map(lambda q:np.asarray(q,float),(start,end))
    forward=b-a
    direction=forward/np.linalg.norm(forward)
    axis=np.array((1.,0.,0.)) if abs(direction[0])<.84 else np.array((0.,1.,0.))
    u=np.cross(direction,axis)
    u*=radius/np.linalg.norm(u)
    v=np.cross(direction,u)
    ring=[cos(k*2*pi/sides)*u+sin(k*2*pi/sides)*v for k in range(sides)]
    for k,p in enumerate(ring):
        q=ring[(k+1)%sides]
        geom.quad([a+p,a+q,b+q,b+p],[(k/sides,0),((k+1)/sides,0),
                  ((k+1)/sides,np.linalg.norm(forward)),(k/sides,np.linalg.norm(forward))],style)
    for point,order in ((a,list(reversed(ring))), (b,ring)):
        for p,q in zip(order,order[1:]+order[:1],strict=True):
            quad(geom,[point,point+p,point+q,point+q],style)


def dome():
    geom=Geometry()
    radius_x,radius_z=2.52,2.27
    # Low clay ledge, upright wall, and the hand-shaped dome above the reed drip edge.
    profile=((0.,.96),(.20,1.00),(.86,1.014),(1.51,.999),(1.87,.968),
             (2.16,.896),(2.50,.760),(2.83,.522),(3.04,.277),(3.10,.025))
    span=48

    def vertex(i,layer,shell=0.):
        height,radius=profile[layer]
        a=i*2*pi/span
        ripple=1.+.022*sin(7*a+layer*.20)+.014*cos(11*a-layer*.22)
        return (max(.022,radius_x*radius*ripple-shell)*cos(a),max(.022,radius_z*radius*ripple-shell)*sin(a),
                height+.019*radius*sin(2*a))

    for layer in range(len(profile)-1):
        for i in range(span):
            if i in (34,35,36,37) and layer<4:
                if i in (34,37):
                    edge=i+1 if i==37 else i
                    outer=[vertex(edge,layer),vertex(edge,layer+1)]
                    inset=[vertex(edge,layer,.24),vertex(edge,layer+1,.24)]
                    wall=[outer[0],outer[1],inset[1],inset[0]]
                    quad(geom,wall if i==34 else list(reversed(wall)),SOOT,1.65)
                continue
            uv=[(i*.24,profile[layer][0]),((i+1)*.24,profile[layer][0]),
                ((i+1)*.24,profile[layer+1][0]),(i*.24,profile[layer+1][0])]
            for inset in (0.,.24):
                points=[vertex(i,layer,inset),vertex(i+1,layer,inset),
                        vertex(i+1,layer+1,inset),vertex(i,layer+1,inset)]
                geom.quad(points if not inset else list(reversed(points)),uv if not inset else list(reversed(uv)),
                          CLAY if inset==0. else SOOT)
    top=profile[-1][0]+.015
    for i in range(span):
        quad(geom,[(0.,0.,top),vertex(i,len(profile)-1),vertex(i+1,len(profile)-1),
                   vertex(i+1,len(profile)-1)],CLAY)
    for i in range(span):
        t0,t1=i*2*pi/span,(i+1)*2*pi/span
        for y,radius,tube,finish in ((1.87,1.035,.043,BAMBOO),(1.96,1.010,.041,HEMP),(.34,1.015,.041,BAMBOO)):
            if y<1. and i in (34,35,36,37):
                continue
            a=(radius*radius_x*cos(t0),radius*radius_z*sin(t0),y+.022*sin(t0*4))
            b=(radius*radius_x*cos(t1),radius*radius_z*sin(t1),y+.022*sin(t1*4))
            cane(geom,a,b,tube,finish,5)
        # The exposed reed drip edge is thicker around the front.
        c,s=cos(t0),sin(t0)
        p=[(radius_x*c,radius_z*s,1.92),(radius_x*cos(t1),radius_z*sin(t1),1.92),
           (1.105*radius_x*cos(t1),1.105*radius_z*sin(t1),1.77+.04*sin(t1*15)),
           (1.105*radius_x*c,1.105*radius_z*s,1.77+.04*sin(t0*15))]
        quad(geom,p,HEMP,.48)
        quad(geom,list(reversed(p)),HEMP,.48)
        if i%3==0 and i not in (33,36,39):
            cane(geom,(radius_x*1.01*c,radius_z*1.01*s,.06),
                 (radius_x*1.011*c,radius_z*1.011*s,.66),.026,BAMBOO,5)
    # Leave an open walk-in shadow and give its visible frame a bamboo arch.
    for x in (-.68,.68):
        cane(geom,(x,-2.22,.015),(x*.91,-2.18,1.53),.072,BAMBOO,9)
        for y in (.24,1.46):
            cane(geom,(x,-2.22,y),(x,-2.22,y+.055),.080,HEMP,8)
    arch=[(-.62,-2.19,1.52),(-.46,-2.20,1.69),(0.,-2.24,1.77),(.45,-2.20,1.69),(.62,-2.19,1.52)]
    for a,b in zip(arch,arch[1:]):
        cane(geom,a,b,.067,BAMBOO,9)
    box(geom,(-.65,-2.28,-.015),(1.30,.27,.042),SILT)
    for x in (-1.09,1.03):
        box(geom,(x-.057,-2.09,1.02),(.152,.055,.49),HEMP,.71)
        for i in range(5):
            box(geom,(x-.031,-2.10,1.39-i*.068),(.061+.015*(i%3),.012,.014),SOOT,.42)
    export(DOME,geom,MATS)


def rice_strip():
    plant=Geometry()
    rng=np.random.default_rng(1813)
    for center_x in np.arange(-.88,1.05,.245):
        for center_z in (-.22,.11,.39):
            x=center_x+rng.uniform(-.058,.058)
            z=center_z+rng.uniform(-.068,.066)
            height=rng.uniform(.41,.69)
            for blade in range(4):
                a=(blade*.25+rng.uniform(0.,.22))*2*pi
                u=np.array((cos(a),sin(a),0.))
                q=np.array((-sin(a),cos(a),0.))
                anchor=np.array((x,z,-.08))
                bend=rng.uniform(.12,.32)
                sections=[]
                for t in (0.,.35,.68,1.):
                    center=anchor+u*bend*t**2+np.array((0.,0.,height*t))
                    width=.018*(1.-t*t)+.001
                    sections.append((center+q*width,center-q*width))
                style=tuple(PLANT_COLORS)[(blade+(1 if height>.495 else 0))%3]
                for (a0,a1),(b0,b1) in zip(sections,sections[1:]):
                    face=(a0,a1,b1,b0)
                    quad(plant,face,style,.57)
                    quad(plant,list(reversed(face)),style,.57)
    export(RICE,plant,MATS)


def hearth():
    geom=Geometry()
    for i in range(9):
        a=i*2*pi/9
        scale=.90+.08*(i%3)
        x,z=.72*cos(a),.55*sin(a)
        box(geom,(x-.12*scale,z-.09*scale,0.),(.24*scale,.18*scale,.115+(.03*(i%3))),
            "iuchi_slate",.41)
    box(geom,(-.56,-.40,.012),(1.12,.80,.05),ASH,.90)
    for end in (-1,1):
        cane(geom,(-.46,.23*end,.08),(.44,-.24*end,.105),.075,SOOT,6)
    export("cakon_tomie_fire_ring",geom,MATS)


def water_cells(gm,w):
    water=w.blk==gm.WATER
    if w.mid=="M885":
        # Leave the central trail and both formations clear between the shallow beds.
        water[68:83,7:47]=True
        water[70:84,86:119]=True
    return water


def interior_lattice(geom):
    center=(33.0,34.35)
    angles=np.linspace(.045*pi,.955*pi,30)
    tiers=((.50,1.),(1.70,1.01),(2.91,.98),(3.91,.88),(4.69,.70),(5.30,.52))
    def node(angle,layer,rib=0.):
        y,factor=tiers[layer]
        return (center[0]+(14.2*factor-rib)*cos(angle),
                center[1]+(8.65*factor-rib)*sin(angle), y)
    for i,(a,b) in enumerate(zip(angles,angles[1:])):
        for layer in range(len(tiers)-1):
            shell=[node(a,layer),node(b,layer),node(b,layer+1),node(a,layer+1)]
            finish=CLAY if layer<3 else SOOT
            quad(geom,shell,finish,2.1)
            quad(geom,list(reversed(shell)),finish,2.1)
            if i%2==0:
                cane(geom,node(a,layer,.11),node(a,layer+1,.11),.065,BAMBOO,7)
            if layer in (0,2,4):
                cane(geom,node(a,layer,.093),node(b,layer,.093),.058,HEMP,6)


def surfaces(gm,w):
    ground=copy(w)
    water=water_cells(gm,w)
    if water.any():
        ground.blk=np.where(water,gm.DIRT,w.blk)
        ground.hgt=np.where(water,w.hgt-1,w.hgt)
    if w.mid in ("M421","M886","M887"):
        x,z=np.meshgrid(np.arange(w.w),np.arange(w.d))
        ground.blk=w.blk.copy()
        if w.mid=="M421":
            center=19.3+1.1*np.sin((x-64.)*.155)
            trail=(x>=62)&(x<=88)&(np.abs(z-center) < 2.6+.5*np.sin(x*.23))
            apron=((x-84.)/9.)**2+((z-22.)/7.5)**2<1.
        elif w.mid=="M886":
            center=66.+.24*(x-57.)
            trail=(np.abs(z-center) < 3.5+.68*np.sin(x*.18))
            apron=((x-64.)/15.)**2+((z-87.)/10.)**2<1.
        else:
            trail=(np.abs(z-(63.+.17*(x-59.)))<4)
            apron=((x-66.)/24.)**2+((z-75.)/10.)**2<1.
            ground.blk[z<90]=gm.DIRT3
        ground.blk[(trail|apron)&(w.blk!=gm.TAMPERED)]=gm.DIRT
    style={gm.GRASS:MOSS,gm.GRASS2:MOSS,gm.GRASS3:MOSS,gm.ROAD:SILT,gm.DIRT:SILT,
           gm.DIRT3:ASH if w.mid=="M887" else SILT,gm.SL_ASH:ASH,gm.SL_GROUND:ASH,
           gm.TAMPERED:CLAY,gm.STONEW:"iuchi_slate",gm.SAND:SILT}
    geom=world_mesh(gm,ground,style)
    lift_floor(geom,{SILT,MOSS,ASH,CLAY},.086)
    if water.any():
        _,fluid=grid_surfaces(water.astype(int),w.hgt,("",WATER),wall_style=SILT,fluid=1)
        offset=.265 if w.mid=="M420" else .103
        fluid.vertices=[np.asarray(point)+[0.,0.,offset] for point in fluid.vertices]
        export(w.mid.lower()+"_paddy_water",fluid,MATS)
    if w.mid=="M420":
        # Low muddy banks soften the drop from the foot path into the shallow planting beds.
        for bz,bx in np.argwhere(water):
            y=(w.hgt[bz,bx]+1)*.5+.30
            for dx,dz in ((-1,0),(1,0),(0,-1),(0,1)):
                x,z=bx+dx,bz+dz
                if not (0<=x<w.w and 0<=z<w.d) or water[z,x]:
                    continue
                a,b=bx*.5,bz*.5
                if dx:
                    edge=a+(.5 if dx>0 else 0.)
                    foot=edge-.20*dx
                    vertices=[(foot,b,y),(foot,b+.5,y),(edge,b+.5,y+.23),(edge,b,y+.23)]
                    quad(geom,vertices if dx>0 else list(reversed(vertices)),SILT,2.3)
                else:
                    edge=b+(.5 if dz>0 else 0.)
                    foot=edge-.20*dz
                    vertices=[(a,foot,y),(a+.5,foot,y),(a+.5,edge,y+.23),(a,edge,y+.23)]
                    quad(geom,vertices if dz<0 else list(reversed(vertices)),SILT,2.3)
        for z in (8.,16.1):
            for x in (15.1,28.1,41.5,55.2,68.3):
                cane(geom,(x-.33,z,2.05),(x+.33,z,2.09),.025,BAMBOO,5)
    if w.mid=="M887":
        interior_lattice(geom)
    return geom,bool(water.any())


def layout(gm,w):
    row={"placements":[],"poolLights":[]}
    props=row["placements"]
    def put(model,x,z,size=1.,yaw=0.,sway=0.,height=None):
        bx,bz=min(int(x*2),w.w-1),min(int(z*2),w.d-1)
        y=(int(w.hgt[bz,bx])+1)*.5+.038 if height is None else height
        props.append([model,x,y,z,size,yaw,*([sway] if sway else [])])
        return y

    if w.mid in ("M420","M885"):
        water=water_cells(gm,w)
        for bz in range(1,w.d-1):
            if bz%3:
                continue
            line=np.r_[False,water[bz],False].astype(np.int8)
            edges=np.flatnonzero(np.diff(line))
            for a,b in zip(edges[::2],edges[1::2],strict=True):
                if b-a<6:
                    continue
                choices=np.arange(a+2.1,b-1.5,4.05)
                for j,xx in enumerate(choices):
                    h=(int(w.hgt[bz,int(xx)])+1)*.5
                    put(RICE,xx*.5+.11,bz*.5+.12,.76+((a+bz+j)%5)*.063,.062*sin(a+bz+j),.12,
                        height=h+(.19 if w.mid=="M420" else 0.))
        if w.mid=="M420":
            for x,z,scale in ((28.2,11.8,.78),(29.8,12.8,.70),(31.5,11.6,.82),(33.3,12.3,.71)):
                put(PINE,x,z,scale,.39*x,.020)
            for x,z,scale in ((17.73,18.1,.67),(20.28,17.9,.72),(35.26,18.8,.69),(56.31,18.9,.82),(65.15,18.40,.75)):
                put(PINE,x,z,scale,.20*x,.014)
            put(CEDAR,51.25,12.43,1.10,.15,.014)
            for x,z,yaw in ((50.09,11.96,.50),(52.69,11.80,-.95)):
                put("cakon_paddy_red_stone",x,z,1.09,yaw)
            put(KAKASHI,43.22,11.97,1.0,.13,.057)
            put(JIZO,59.24,12.76,1.0,-.10)
            for x,z,yaw in ((18.42,6.68,.14),(36.68,13.29,pi),(46.67,6.73,-.12),(60.61,14.22,pi)):
                put("cakon_paddy_sluice",x,z,.92,yaw)
        else:
            for x,z,size in ((13.5,55.7,.59),(27.3,54.1,.63),(44.6,56.5,.73),(56.0,54.,.68)):
                put(PINE,x,z,size,.78,.017)
            put(CEDAR,36.8,56.3,.93,.77,.015)
            put(KAKASHI,31.75,51.35,.94,.14,.056)
            put("cakon_paddy_sluice",21.27,47.8,.96,pi/2)
    elif w.mid=="M421":
        put(DOME,42.50,12.76,1.,0.,height=2.025)
        put("cakon_tomie_fire_ring",39.23,9.20,.77)
        put("cakon_tomie_drying_rack",45.82,11.12,.85,-.15)
        put("cakon_tomie_mortar",40.31,10.02,.82,.52)
        put("cakon_market_crock",39.72,10.14,.78,.41)
        for x,z,size in ((20.,14.7,.78),(27.5,15.7,.93),(35.4,15.2,.87),(38.2,16.5,.82),
                         (46.9,16.1,1.02),(49.28,14.9,.85),(54.0,15.95,1.08)):
            put(CEDAR,x,z,size,.14*x,.015)
        for x,z in ((26.2,6.1),(35.6,5.8),(46.8,6.28),(48.2,12.61),(52.4,7.28)):
            put("cakon_paddy_red_stone",x,z,.72+.04*(x%5),x*.23)
        row["poolLights"]=[[39.23,2.63,9.20,4.25,1.04]]
    elif w.mid=="M886":
        put(DOME,32.0,45.29,1.66,0.,height=.53)
        put("cakon_tomie_fire_ring",32.35,40.76,1.38)
        put("cakon_tomie_drying_rack",37.7,42.49,1.15,-.19)
        put("cakon_tomie_mortar",29.38,41.26,1.16,.19)
        for x,z in ((12.1,49.),(18.,47.),(24.2,48.1),(40.45,47.8),(46.22,48.4),(54.,47.4)):
            put(CEDAR,x,z,1.08,.20*x,.014)
            put("cakon_paddy_red_stone",x-.84,z-1.33,.72+.13*(x%3),.32*x)
        row["watchfires"]=[[32.35,.66,40.76,.83]]
        row["poolLights"]=[[32.35,1.26,40.76,6.10,1.19]]
    else:
        for x,z in ((22.8,37.6),(28.14,40.87),(37.90,40.49),(43.0,38.4)):
            put("cakon_tomie_drying_rack",x,z,.91,.19*sin(x))
            put("cakon_tomie_mortar",x+.44,z-.575,.72,.13*x)
        for x,z in ((25.13,38.99),(35.5,40.5),(42.14,38.1)):
            put("cakon_market_crock",x,z,1.12,.14*x)
            put("iuchi_fitted_andon",x+.61,z+.23,.82)
        put("cakon_tomie_fire_ring",32.1,40.65,.60)
        row["watchfires"]=[[32.1,.61,40.65,.45]]
        row["poolLights"]=[[32.1,1.14,40.65,6.3,1.16],[42.76,.97,38.36,5.5,.94]]
    return row


def main(repo):
    _,_,gm,_,_=variant(repo)
    materials()
    models={name:build_diorama_mesh(name,source,size,align_x=align,main_component=name!=KAKASHI)
            for name,(source,size,align) in SCALES.items()}
    dome()
    rice_strip()
    hearth()
    index_path=STAGE/"index.json"
    index=json.loads(index_path.read_bytes())
    report={"mesh_sources":models,"maps":{}}
    for mid in MAPS:
        world,events=gm.make(mid)
        mesh,water=surfaces(gm,world)
        row=layout(gm,world)
        terrain=mid.lower()+"_cakon_paddy_hut"
        export(terrain,mesh,MATS)
        row["terrain"]=terrain
        if water:
            row.update(water=mid.lower()+"_paddy_water",
                       waterSequence={"prefix":WATER,"frames":32,"seconds":15.8})
        index[mid]=row
        report["maps"][mid]={"terrain_quads":len(mesh.faces),"events":len(events.ev) if events else 0,
                            "placements":len(row["placements"]),"water":water}
    index_path.write_text(json.dumps(index,separators=(",",":")),"utf8")
    (HERE/"cakon-paddy-hut-layout.json").write_text(json.dumps(report,indent=2),"utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
