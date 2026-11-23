"""Build the Iuchi woods, trail camp, jade mine tiers, and their two arenas."""

import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import box, shop_board
from build_iuchi_tower import HERE, MATS as TOWER_MATS, ground_styles, lift_floor, save_props, tint_texture, write_rows
from build_kaiu_kit import world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from iuchi_worlds import MINES, variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


CAVE = ("", "iuchi_mine_floor", "iuchi_mine_slate", "iuchi_mine_dust")
MATS = {**TOWER_MATS, **{k: (k+".png", .94) for k in CAVE[1:]},
        "iuchi_woodland": ("iuchi_woodland.png", .94), "iuchi_mine_approach": ("iuchi_mine_approach.png", .94),
        "iuchi_canvas": ("iuchi_canvas.png", .94), "iuchi_jade": ("iuchi_jade.png", .85),
        "iuchi_brook": ("iuchi_brook00.png", .28)}
PROPS = (("iuchi_mine_cart", (1.49,.92,.87), 46), ("iuchi_brook_reeds", (.45,.40,.54), 36))


def stone_source(name, dimensions, resolution, voxfile):
    key, points, colors, _, source = convert_prop(name, dimensions, resolution, lower=.025)
    bright = (colors.min(axis=1)>175) & (np.ptp(colors,axis=1)<26)
    # Reconstruction sweeps live on an outer slice. Preserve light mineral faces in the body.
    keep = ~(bright & ((points[:,2]<2) | (points[:,1]<2) | (points[:,1]>points[:,1].max()-2)))
    points,colors=points[keep],colors[keep]
    points-=points.min(axis=0)
    if name=="iuchi_jade_seam":
        x,z,y=points.T
        raw=colors @ [.25,.62,.13]
        shade=np.clip((raw-np.median(raw))*.47,-24.,36.)
        seam=(x*.81 + y*.92 + z*.20 + 1.28*np.sin(z*.21+y*.18))%8.90
        veins=(seam<1.28) & (raw>40)
        base=np.where(veins[:,None],np.array([40,109,71]),np.array([60,71,78]))
        colors=np.uint8(np.clip(base+shade[:,None],0.,255.))
    return save(key,points,colors,np.asarray(dimensions)/(points.max(axis=0)+1),source,voxfile)


def textures():
    for k, scan, color, contrast in (
        ("iuchi_mine_floor","iuchi_jade_wall_scan",(69,67,65),.068),
        ("iuchi_mine_slate","iuchi_jade_wall_scan",(41,51,59),.061),
        ("iuchi_mine_dust","iuchi_jade_wall_scan",(87,98,90),.057),
        ("iuchi_jade","iuchi_jade_wall_scan",(48,104,81),.071),
        ("iuchi_woodland","iuchi_frosted_meadow",(58,89,62),.071),
        ("iuchi_canvas","ojatara_offwhite_canvas",(58,84,59),.066),
    ):
        tint_texture(k,scan,color,contrast)
    bed = periodic(Image.open(HERE/"surface_sources/iuchi_riverbed_stone.png").convert("RGB"),256) @ [.25,.62,.13]
    shade = np.clip((bed - np.median(bed))/max(12.,bed.std()),-2.0,2.0)
    z,x = np.mgrid[0:math.tau:256j,0:math.tau:256j]
    for k in range(32):
        phase=k*math.tau/32
        ripples=np.sin(z*7.+x*2.-phase+.25*np.sin(x*3.-phase))
        ripple_trails=np.cos(z*5.-x*3.+phase+.4*np.sin(z))
        light=3.9*shade + 3.9*ripples + 1.8*ripple_trails + 4.9*np.maximum(ripples,0.)**7
        rgb=np.array([46,114,111])+light[...,None]*[.76,1.04,1.15]
        Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/f"tex/iuchi_brook{k:02d}.png")
    v = np.clip((np.linspace(0.,1.,256)-.20)/.67,0.,1.)
    v = v**2*(3.-2.*v)
    dusk = np.array([123,96,73])*(1-v[:,None])+np.array([31,39,45])*v[:,None]
    rgb=dusk[None,:,:]+shade[...,None]*1.5
    Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/"tex/iuchi_mine_approach.png")


def fittings():
    for name,width,depth,eaves in (("iuchi_dragon_shelter",2.90,2.25,1.70),
                                  ("iuchi_dragon_command",5.70,3.12,2.36)):
        g=Geometry()
        for x in (-width*.5+.10,width*.5-.16):
            for z in (-depth*.5+.095,depth*.5-.16):
                box(g,(x,z,0.),(.105,.107,eaves),"iuchi_beam")
                box(g,(x-.037,z-.036,0.),(.173,.178,.118),"iuchi_slate")
        for z in (-depth*.5+.079,depth*.5-.137):
            box(g,(-width*.5,z,eaves-.085),(width,.073,.105),"iuchi_beam")
        for side in (-1.,1.):
            z=side*depth*.5
            points=[(-width*.5,0.,eaves+.47),(width*.5,0.,eaves+.47),
                    (width*.5,z,eaves),(-width*.5,z,eaves)]
            if side < 0:
                points.reverse()
            g.quad(points,[(x*.6,d*.6) for x,d,_ in points],"iuchi_canvas")
            under=[(x,d,y-.039) for x,d,y in reversed(points)]
            g.quad(under,[(x*.6,d*.6) for x,d,_ in under],"iuchi_canvas")
            box(g,(-width*.5,z-.016,eaves-.16),(width,.033,.17),"iuchi_canvas")
        box(g,(-width*.5-.077,-.036,eaves+.428),(width+.15,.076,.089),"iuchi_beam")
        export(name,g,MATS)

    banner=Geometry()
    box(banner,(-.036,-.032,0.),(.077,.073,2.47),"iuchi_beam")
    box(banner,(-.062,-.039,2.31),(.75,.090,.067),"iuchi_bronze")
    box(banner,(.026,-.041,1.12),(.58,.039,1.20),"iuchi_canvas")
    for y in (1.25,1.40,2.12):
        box(banner,(.032,-.048,y),(.568,.011,.035),"iuchi_bronze")
    box(banner,(-.13,-.126,0.),(.26,.25,.14),"iuchi_slate")
    export("iuchi_dragon_standard",banner,MATS)

    altar=Geometry()
    box(altar,(-1.08,-.53,0.),(2.16,1.06,.15),"iuchi_mine_slate")
    box(altar,(-.77,-.42,.13),(1.54,.87,.22),"iuchi_light_stone")
    for x in (-.73,.53):
        box(altar,(x,.19,.32),(.21,.29,1.24),"iuchi_slate")
    box(altar,(-.85,.15,1.43),(.74,.41,.19),"iuchi_mine_slate")
    box(altar,(-.064,.15,1.38),(.91,.41,.19),"iuchi_mine_slate")
    box(altar,(-.59,-.34,.34),(1.18,.33,.092),"iuchi_oak")
    for x,d in ((-.38,.23),(-.02,.15),(.25,.16)):
        box(altar,(x,-.19,.431),(d,.14,.12),"iuchi_jade")
    export("iuchi_deep_stone_shrine",altar,MATS)

    grave=Geometry()
    box(grave,(-.25,-.22,0.),(.50,.46,.085),"iuchi_mine_slate")
    box(grave,(-.159,-.023,.075),(.30,.165,.47),"iuchi_light_stone")
    box(grave,(-.145,-.011,.537),(.258,.141,.057),"iuchi_slate")
    box(grave,(-.205,-.196,.104),(.399,.192,.064),"iuchi_oak")
    box(grave,(-.084,-.169,.169),(.172,.086,.020),"iuchi_paper")
    export("iuchi_fitted_memorial",grave,MATS)
    shop_board("iuchi_jade_waymark","JADE","MINES","#425459")


def terrain(gm,w):
    if w.mid == "M403":
        mask=w.blk==gm.WATER
        height=w.hgt.copy()
        bed=gm.T(3)
        w.blk[mask]=bed
        w.hgt[mask]-=1
        styles={**ground_styles(gm),gm.GRASS2:"iuchi_woodland",gm.GRASS:"iuchi_woodland",bed:"iuchi_mine_slate"}
        mesh=world_mesh(gm,w,styles)
        w.blk[mask]=gm.WATER
        w.hgt[:]=height
        lift_floor(mesh,{"iuchi_woodland","iuchi_path","iuchi_meadow"})
        _,stream=grid_surfaces(mask.astype(int),height,("","iuchi_brook"),wall_style="iuchi_slate",fluid=1)
        zmin=min(p[1] for p in stream.vertices)
        stream.vertices=[(x,z+(-.08 if z==zmin else .08),y+.49) for x,z,y in stream.vertices]
        export("m403_iuchi_brook",stream,MATS)
        return mesh
    if w.mid == "M404":
        mesh=world_mesh(gm,w,ground_styles(gm))
        lift_floor(mesh,{"iuchi_meadow","iuchi_path","iuchi_frost"})
        end=w.w*.5
        near=end-8.61
        mesh.quad([(near,13.08,2.091),(end,13.08,2.091),(end,15.42,2.091),(near,15.42,2.091)],
                  [(0.,0.),(1.,0.),(1.,1.),(0.,1.)],"iuchi_mine_approach")
        box(mesh,(end+.085,12.93,2.),(.20,2.65,3.15),"iuchi_mine_slate")
        box(mesh,(38.74,16.65,2.079),(3.01,9.96,.017),"iuchi_path",3.1)
        return mesh
    cave=world_mesh(gm,w,{gm.CAVE_FLOOR:"iuchi_mine_floor",gm.DIRT:"iuchi_mine_floor",gm.SL_GROUND:"iuchi_mine_floor",
                          gm.CAVE_WALL:"iuchi_mine_slate",gm.STONE:"iuchi_mine_slate",gm.STONEW:"iuchi_slate",
                          gm.GRASS3:"iuchi_mine_dust"})
    cave.materials=[{"path":"iuchi_mine_floor","cliff":"iuchi_mine_slate"}.get(m,m) for m in cave.materials]
    lift_floor(cave,{"iuchi_mine_floor","iuchi_mine_slate","iuchi_mine_dust"})
    return cave


def layout(gm,w):
    mid=w.mid
    arena=mid in ("M879","M880")
    props,lights=[],[]

    def put(asset,x,z,size=1.,yaw=0.,level=None,sway=0.):
        y=(int(w.hgt[z,x])+1)*.5 + .024 if level is None else level
        row=[asset,x*.5+.25,y,z*.5+.25,size,yaw]
        props.append(row+[sway] if sway else row)
        return row[1:4]

    def lamp(x,z,size=.91):
        xx,y,zz=put("iuchi_fitted_andon",x,z,size)
        lights.append([xx,y+.50*size,zz,4.5,1.66])

    if mid == "M403":
        for x in range(29,145,7):
            for z in (9+x%4,34+x%4):
                if 69 <= x <= 89 and z<17:
                    continue
                put("iuchi_mountain_birch",x,z,.83+x%5*.12,.33*x,sway=.033)
        for x,z in ((48,35),(69,40),(103,34),(135,39)):
            put("coast_pine",x,z,1.02+x%4*.12,.27*x,sway=.017)
        for x,z in ((59,13),(68,14),(78,18),(84,17),(92,17),(93,11),(102,21),(119,25),(143,23)):
            put("coast_flowers" if x%3==0 else "wind_grass",x,z,.81+x%4*.09,.5*x,sway=.12)
        for x in range(31,144,8):
            put("iuchi_brook_pebbles",x,28+x%2,.73+x%3*.14,x*.34)
            put("iuchi_brook_reeds",x+2,29,.89+x%4*.11,x*.22,sway=.13)
        put("iuchi_fitted_memorial",113,25,.78,.18)
        return {"placements":props,"poolLights":lights,"water":"m403_iuchi_brook",
                "waterSequence":{"prefix":"iuchi_brook","frames":32,"seconds":13.0}}
    if mid == "M404":
        for x,z in ((6,21),(16,22),(70,21),(82,22),(94,21),(8,5),(20,4),(88,5)):
            put("iuchi_dragon_shelter",x+3+gm.PAD_X,z+2+gm.PAD_BOTTOM,1.)
        put("iuchi_dragon_command",70,28,1.0)
        for x in (75,85):
            lamp(x,35,.98)
        for x,z in ((30,25),(62,25),(100,25),(141,30)):
            lamp(x+gm.PAD_X if x<110 else x,z)
        for x,z in ((62,26),(77,26),(105,26),(132,31)):
            put("iuchi_dragon_standard",x,z,1.01,.08,sway=.052)
        put("autumn_camp_cooking_tripod",36,26,.93,.23)
        put("hoshi_inn_bench",42,25,.87,.15)
        put("iuchi_jade_waymark",142,25,.92,.03)
        for x,z,size in ((145,22,.9),(149,33,1.1),(152,24,.93)):
            put("togashi_garden_stone",x,z,size,.23*x)
    elif mid == "M405":
        for x,z in ((34,12),(40,11)):
            put("iuchi_fitted_memorial",x,z,1.01,-.14)
            put("coast_flowers",x+1,z,.75,.16,sway=.035)
        for x,z in ((34,7),(42,15),(55,20),(72,16),(83,35),(84,44)):
            lamp(x,z,.87)
        for x,z in ((43,24),(65,18),(88,34),(51,31),(79,32)):
            put("iuchi_jade_seam",x,z,.82+x%4*.14,.26*x)
    elif mid == "M406":
        for x,z in ((59,8),(54,22),(72,22),(38,34),(85,33),(84,44)):
            lamp(x,z,.88)
        for x,z in ((54,21),(69,20),(65,26)):
            put("iuchi_mine_cart",x,z,1.04,.17*x)
        for x,z in ((51,25),(74,26),(89,34),(41,32),(43,36)):
            put("iuchi_jade_seam",x,z,.86+x%4*.12,.22*x)
        put("iuchi_notes_table",38,37,.92,.09)
    elif mid == "M407":
        for x,z in ((54,10),(46,24),(64,25),(49,31),(63,32)):
            lamp(x,z,1.01)
        for x,z in ((42,26),(67,29),(48,32),(64,34),(51,35)):
            put("iuchi_jade_seam",x,z,1.06+x%4*.10,.31*x)
    elif arena:
        for x,z in ((17,88),(33,84),(48,89),(69,87),(83,85),(101,89),(117,88)):
            put("iuchi_jade_seam",x,z,1.06+x%4*.13,.23*x)
        for x in (21,43,81,108):
            lamp(x,86+x%3,1.16)
        if mid == "M879":
            for x,z in ((30,88),(59,90),(93,89)):
                put("iuchi_mine_cart",x,z,1.19,.17*x)
    if mid in ("M407","M880"):
        shrine,= (o for o in w.objs if o["t"]=="fill" and o["blk"]==gm.STONEW)
        x=shrine["x"]+shrine["w"]//2-1
        z=shrine["z"]+shrine["d"]//2-1
        put("iuchi_deep_stone_shrine",x,z,1.03,.02,(shrine["y"]+shrine["h"])*.5+.027)
    return {"placements":props,"poolLights":lights}


def main(repo):
    _,_,gm,_,_=variant(repo,True)
    import voxfile

    textures()
    fittings()
    sources=save_props(PROPS,voxfile)
    for name,dim,res in (("iuchi_jade_seam",(1.48,.93,.89),43),("iuchi_brook_pebbles",(1.37,.86,.44),41)):
        sources[name]=stone_source(name,dim,res,voxfile)
        voxel_asset(name)
    write_rows(MINES,gm,terrain,layout,MATS,"iuchi-mines-layout.json",sources)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
