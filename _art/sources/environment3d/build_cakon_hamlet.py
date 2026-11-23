"""Build the outer hamlet, maple-log crossing, and matching canal arena."""

import json
from copy import copy
from pathlib import Path
import sys

import numpy as np

from build_cakon import MATS, STAGE, WATER, geometry
from build_hoshi_stall import box, shop_board
from cakon_huts import build_assets
from cakon_worlds import GROUPS, variant
from diorama_trees import MAPLE, PINE, build_diorama_mesh, falling_leaves
from export_coast import export


HERE=Path(__file__).resolve().parent
LOG="cakon_canal_maple_log"


def layout(gm,w):
    props,lights,leaves=[],[],[]
    row={"placements":props,"poolLights":lights,"leafDrift":leaves}

    def put(model,x,z,scale=1.,yaw=0.,level=None,sway=0.):
        y=(int(w.hgt[z,x])+1)*.5+.035 if level is None else level
        p=[x*.5+.25,y,z*.5+.25]
        props.append([model,*p,scale,yaw,*([sway] if sway else [])])
        return p

    def tree(model,x,z,scale):
        point=put(model,x,z,scale,x*.29,sway=.014 if model==PINE else .023)
        if model==MAPLE:
            leaves.extend(falling_leaves(point,scale,x))

    if w.mid=="M418":
        for x,z in ((8,22),(20,24),(64,22),(76,23),(88,21),(10,4),(30,5),(70,4),(84,6),(34,22)):
            bx,bz=x+gm.PAD_X,z+gm.PAD_BOTTOM
            put("cakon_hamlet_hut",bx+2,bz+1,.91+(x%5)*.032)
            put("cakon_staved_barrel",bx+5,bz+1,.85+(z%4)*.04,.04)
        put("cakon_hamlet_shrine",73,27,1.)
        put("cakon_hamlet_shrine_sign",69,24,.79)
        for x,z in ((64,24),(81,24),(44,27),(120,22)):
            a,y,b=put("iuchi_fitted_andon",x,z,.79)
            lights.append([a,y+.43,b,3.60,1.09])
        for x,z in ((36,15),(48,7),(66,6),(74,10),(95,14),(108,18),(130,9),(139,12),(142,31)):
            tree(MAPLE if x%3==0 else PINE,x,z,.76+x%5*.11)
        for x,z in ((40,30),(49,27),(63,24),(83,26),(94,28),(111,21),(43,9),(62,12),(126,15)):
            put("cakon_thatch_bundle",x,z,.78+x%3*.11,.29*x)
    elif w.mid=="M419":
        put(LOG,75,19,1.,level=1.43)
        for x in (60,65,67,84,87,94):
            for z in (7+x%3,24+x%5,33+x%3):
                put("iuchi_brook_reeds",x,z,1.07,.27*x,sway=.105)
        for x,z in ((42,11),(49,8),(57,12),(63,26),(89,14),(91,31),(106,9),(117,13)):
            tree(MAPLE if x%2 else PINE,x,z,.83+x%5*.08)
        for x,z in ((65,17),(69,24),(84,18),(85,25)):
            put("cakon_paddy_red_stone",x,z,.88+x%4*.11,.36*x)
    else:
        for x in (10,24,39,53,68,81,97,113):
            put("cakon_paddy_red_stone",x,97+x%5,1.15+x%4*.14,.18*x,level=.57)
            put("iuchi_brook_reeds",x+2,97+x%5,.93,.28*x,level=.55,sway=.098)
        for x in (13,38,55,72,91,112):
            p=put(MAPLE if x%2 else PINE,x,108+x%5,1.14+x%3*.12,.24*x,level=.54,sway=.023)
            if x%2:
                leaves.extend(falling_leaves(p,1.20,x))
    if w.mid!="M418":
        row.update({"water":w.mid.lower()+"_cakon_river",
                    "waterSequence":{"prefix":WATER,"frames":32,"seconds":16.5}})
    return row


def main(repo):
    _,_,gm,_,_=variant(repo,"hamlet")
    build_assets()
    shop_board("cakon_hamlet_shrine_sign","WAYSIDE","SHRINE","#544e3e")
    dimensions=((LOG,(6.40,.76,1.85),True),("cakon_thatch_bundle",(.72,.43,.59),False),
                ("cakon_paddy_red_stone",(.91,.71,.68),False))
    assets={name:build_diorama_mesh(name,name,span,align_x=align,main_component=name==LOG)
            for name,span,align in dimensions}
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    details={}
    for mid in GROUPS["hamlet"]:
        world,events=gm.make(mid)
        shell=world
        if mid=="M419":
            shell=copy(world)
            shell.blk=world.blk.copy()
            shell.hgt=world.hgt.copy()
            shell.blk[18:21,70:82]=gm.WATER
            shell.hgt[18:21,70:82]=0
            shell.objs=[obj for obj in world.objs if not (obj["t"]=="fill" and
                        (obj["x"],obj["y"],obj["z"])==(70,0,18))]
        shape=geometry(gm,shell)
        if mid=="M884":
            for x,d,y in ((0.,16.,.71),(16.,13.,.63),(29.,19.,.84),(48.,16.,.72)):
                box(shape,(x,48.0,.075),(d,16.,y),"cakon_silt")
        tag=mid.lower()+"_cakon"
        export(tag,shape,MATS)
        index[mid]={"terrain":tag,**layout(gm,world)}
        details[mid]={"events":len(events.ev) if events else 0,"placements":len(index[mid]["placements"])}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"cakon-hamlet-layout.json").write_text(json.dumps({"maps":details,"sources":assets},indent=2),
                                               encoding="utf-8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
