"""Dress the seven Shadowlands march maps with the new materials and props."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import dressing, grid_surfaces
from build_hoshi_stall import box
from build_shinomen_gate import MATS, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from shadowlands_march_worlds import MAPS, variant
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
SURFACES={**MATS,"ochre_ash":("shadowlands_ochre_ash.png",.94),"lava":("magma00.png",.64),
          "waste_taint":("waste_taint.png",.94)}


def assets(voxfile):
    sources={}
    for key,dimensions,resolution in (
        ("tainted_poppy_clump",(.67,.59,.43),23),
        ("shadowlands_tar_bridge_end",(1.44,.94,1.20),36),
        ("shadowlands_obsidian_tree",(1.46,1.38,2.51),40),
        ("shadowlands_watchpost_winch",(1.37,.83,1.20),38),
        ("toshi_kijo_gravestone",(.73,.57,1.43),36),
    ):
        name,points,rgb,pitch,glb=convert_prop(key,dimensions,resolution,lower=.022)
        if name=="shadowlands_obsidian_tree":
            points[:,2]=points[:,2].max()-points[:,2]
        if name=="tainted_poppy_clump":
            flower=(rgb[:,0]>(rgb[:,1]*1.24+13))&(rgb[:,0]>72)
            rgb[flower]=np.uint8(np.clip(rgb[flower]*[1.30,.74,.80],0,255))
        sources[key]=save(name,points,rgb,pitch,glb,voxfile)
        voxel_asset(key)
    sample=np.asarray(periodic(Image.open(HERE/"surface_sources/shadowlands_ochre_ash.png").convert("RGB"),1024))
    grey=sample@[.24,.64,.12]
    shade=np.clip(grey/max(1.,np.median(grey)),.43,1.43)
    out=np.asarray([124,105,91])*shade[...,None]
    Image.fromarray(np.uint8(np.clip(out,0,255))).save(STAGE/"tex/shadowlands_ochre_ash.png")
    return sources


def rail(mesh,start,end,r,width,style):
    a,b=np.asarray(start),np.asarray(end)
    along=b-a
    cross=np.cross(along,[0.,0.,1.])
    cross/=np.linalg.norm(cross)
    up=np.cross(cross,along)/np.linalg.norm(along)
    ring=[r*cross+width*up,r*cross-width*up,-r*cross-width*up,-r*cross+width*up]
    for i in range(4):
        u=i
        v=(i+1)%4
        mesh.quad([a+ring[u],a+ring[v],b+ring[v],b+ring[u]],[(0,0),(0,1),(1,1),(1,0)],style)


def chasm_bridge():
    bridge=Geometry()
    for x in np.linspace(37.013,43.737,23):
        edge=.025*math.sin(x*1.7)
        box(bridge,(x,9.022+edge,1.96),(.285,1.957,.082),"kaiu_wood",1.64)
    for z in (9.07,10.95):
        for order,x in enumerate((37.06,37.51,43.50,43.94)):
            h=.97 if order in (0,3) else .89
            box(bridge,(x-.064,z-.063,2.013),(.128,.127,h),"kaiu_wood")
            box(bridge,(x-.074,z-.073,2.72),(.148,.147,.091),"kaiu_roof")
        for top in (2.96,2.68):
            xs=np.linspace(37.07,43.94,16)
            cable=[(x,z,top-.34*math.sin(math.pi*(x-xs[0])/(xs[-1]-xs[0]))) for x in xs]
            for a,b in zip(cable,cable[1:]):
                rail(bridge,a,b,.023,.026,"kaiu_plaster")
    export("shadowlands_chasm_bridge",bridge,SURFACES)


def surface(gm,m):
    textures={
        gm.SL_GROUND:"waste_earth",gm.SL_ASH:"ochre_ash" if m.mid in ("M176","M177") else "waste_ash",
        gm.STONE:"waste_shale",gm.ROAD:"waste_trail",gm.TARSTAIN:"waste_taint",
        gm.POPPYF:"waste_taint",gm.TAR:"blackpitch",gm.EMBER:"waste_taint",
        gm.LAVA:"waste_shale",
    }
    scene=world_mesh(gm,m,textures)
    scene.materials=["waste_shale" if key=="cliff" else key for key in scene.materials]
    return scene


def details(gm,m,row):
    props=row["placements"]

    def place(key,x,z,size=1.,yaw=0.,rise=0.):
        bx,bz=x+gm.PAD_X,z+gm.PAD_BOTTOM
        y=(int(m.hgt[bz,bx])+1)*.5+rise
        props.append([key,bx*.5+.25,y,bz*.5+.25,size,yaw])

    if m.mid=="M171":
        props.append(["shadowlands_chasm_bridge",0.,0.,0.,1.,0.])
        for x,z,a in ((47,13,.94),(62,18,-.38)):
            place("shadowlands_tar_bridge_end",x,z,.75,a)
        for x,z,s in ((14,22,.91),(35,7,.85),(65,23,1.21),(89,21,.86),(103,26,1.05)):
            place("shadowlands_burnt_stump",x,z,s,.4+x*.11)
    elif m.mid=="M172":
        for i,x in enumerate((13,22,30,38,48,57,67,76,86,96,103)):
            z=28+(i*3)%4
            place("shadowlands_obsidian_tree",x,z,.91+(i%4)*.18,.24*i,.10)
            if i%2==1:
                place("shadowlands_shards",x+2,z-2,.88,.56*i)
        place("shadowlands_obsidian_tree",38,26,1.17,-.14,.11)
        place("shadowlands_oni_bones",103,28,.59,.35)
    elif m.mid=="M173":
        for z,x in np.argwhere(m.blk==gm.POPPYF):
            if (x*19+z*23)%23==0 or (x%3==z%3==0):
                props.append(["tainted_poppy_clump",x*.5+.25,(int(m.hgt[z,x])+1)*.5,
                              z*.5+.25,.82+((x*11+z*7)%7)*.09,((x*13+z*5)%31)*.18,.072])
        for x,z,a in ((58,26,.31),(85,20,-.68),(99,13,.48)):
            place("shadowlands_shards",x,z,.89,a)
    elif m.mid=="M174":
        for x,z,key,s,a in (
            (28,24,"shadowlands_watchpost_winch",.93,-.45),
            (33,26,"hiruma_fallen_standard",.83,.36),
            (41,27,"shinomen_covered_supplies",.87,.31),
            (51,20,"shadowlands_broken_cart",.86,-.18),
            (23,14,"shadowlands_burnt_stump",1.06,.70),
        ):
            place(key,x,z,s,a)
    elif m.mid=="M175":
        for x,z,s in ((28,24,.8),(31,13,.98),(36,26,.65),(48,14,1.01),(50,24,.81),(56,22,.92)):
            place("toshi_kijo_gravestone",x,z,s,.42*x)
        place("shadowlands_ruined_shrine",45,32,.95,-.08)
        for x,z,s in ((33,15,.67),(43,16,.76),(54,25,.72),(20,23,.82)):
            place("hoshi_storage_jar",x,z,s,(x%5)*.6)
    elif m.mid=="M176":
        for x,z,s in ((15,24,.97),(34,19,.88),(59,21,1.30),(62,21,.96),(82,24,1.23),(102,23,1.27)):
            place("shadowlands_shards",x,z,s,x*.35)
        for x,z,s in ((20,7,.95),(42,23,.65),(86,13,.81),(103,15,.89)):
            place("shadowlands_oni_bones",x,z,s,z*.36)
        place("toshi_kijo_gravestone",92,27,.81,.12)
    elif m.mid=="M177":
        for x,z,s in ((21,9,.91),(46,19,.77),(76,27,.88),(100,23,1.11)):
            place("hiruma_fallen_standard",x,z,s,(x%8)*.19)
        for x,z,s in ((22,25,.91),(52,24,1.31),(80,21,1.18),(104,25,.84)):
            place("shadowlands_burnt_stump",x,z,s,z*.31)
        for x,z,s in ((89,22,.63),(107,26,.68)):
            place("watchtower_signal",x,z,s,z*.35)
            _,wx,y,wz,_,_=props[-1]
            row.setdefault("watchfires",[]).append([wx,y+s*.93,wz,s*.71])
            row.setdefault("poolLights",[]).append([wx,y+s*1.25,wz,4.6,1.35])


def main(repo):
    _,gm,_,_=variant(repo)
    import voxfile

    originals=assets(voxfile)
    chasm_bridge()
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    report={}
    for mid in MAPS:
        world,events=gm.make(mid)
        base=f"{mid.lower()}_march"
        terrain=surface(gm,world)
        export(base,terrain,SURFACES)
        row={"terrain":base,"placements":[]}
        if mid=="M172":
            mask=world.blk==gm.LAVA
            _,liquid=grid_surfaces(np.where(mask,1,0),world.hgt,("","lava"),
                                   wall_style="waste_shale",fluid=1)
            export(base+"_fire",liquid,SURFACES)
            props,lights,spatter=dressing(gm,world,mask)
            row.update(water=base+"_fire",waterMode="lava",placements=props,
                       poolLights=lights,magmaSpatter=spatter)
        details(gm,world,row)
        index[mid]=row
        report[mid]={"terrain_quads":len(terrain.faces),"props":len(row["placements"]),
                     "event_count":len(events.ev),"live_fluid_frames":24 if "water" in row else 0}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"shadowlands-march-layout.json").write_text(json.dumps({
        "maps":report,"sources":originals,
    },indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
