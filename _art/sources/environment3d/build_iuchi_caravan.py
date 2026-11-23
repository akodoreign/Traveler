"""Dress the homeward caravan around the existing cast and road events."""

import json
from math import cos, pi, sin
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from build_hoshi_stall import box, shop_board
from build_iuchi_storm import MATS as STORM_MATS, cleft
from build_iuchi_tower import ground_styles, tint_texture
from build_kaiu_kit import world_mesh
from cakon_worlds import variant
from diorama_trees import MAPLE, PINE, build_trees, falling_leaves
from export_coast import Geometry, STAGE, export, voxel_asset
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
GROUND = "iuchi_caravan_ground"
MEADOW = "iuchi_caravan_meadow"
PATH = "iuchi_caravan_track"
WEAR = "iuchi_caravan_linen"
MATS = {**STORM_MATS, **{k: (k + ".png",.94) for k in (GROUND,MEADOW,PATH,WEAR)}}
BASKET = "iuchi_valley_pack_basket"
STONE = "iuchi_valley_wayside_stone"


def props(voxfile):
    evidence = {}
    for name,dimensions,resolution in ((BASKET,(.69,.54,.87),60),(STONE,(.59,.79,.67),56)):
        key, points, rgb, _, source = convert_prop(name,dimensions,resolution,lower=.01)
        bright = (rgb.min(axis=1)>169) & (np.ptp(rgb,axis=1)<39)
        rim = ((points[:,2]<3) | (points[:,1]<2) | (points[:,1]>=points[:,1].max()-1))
        keep = ~(bright & rim)
        points,rgb = points[keep],rgb[keep]
        points -= points.min(axis=0)
        evidence[name] = save(key,points,rgb,np.asarray(dimensions)/(points.max(axis=0)+1),source,voxfile)
        voxel_asset(name)
    return {**evidence,**build_trees()}


def camp_models():
    tint_texture(WEAR,"ojatara_offwhite_canvas",(160,131,89),.038)
    roof=Geometry()
    for x in (-1.01,.94):
        for z in (-.70,.64):
            box(roof,(x,z,0.),(.076,.076,1.31),"iuchi_beam")
    for side in (-1,1):
        z=side*.80
        p=[(-1.16,0.,1.73),(1.16,0.,1.73),(1.16,z,1.25),(-1.16,z,1.25)]
        for q in (p,list(reversed(p))):
            roof.quad(q,[(x*.72,z*.62) for x,z,_ in q],WEAR)
        box(roof,(-1.16,z-.021,1.21),(2.32,.042,.075),"iuchi_oak")
    box(roof,(-1.20,-.028,1.695),(2.40,.056,.074),"iuchi_beam")
    export("iuchi_caravan_lean_to",roof,MATS)

    cart=Geometry()
    box(cart,(-.38,-.52,.38),(.76,1.04,.10),"iuchi_beam")
    for x in (-.38,.33):
        box(cart,(x,-1.20,.39),(.05,1.76,.065),"iuchi_oak")
        box(cart,(x,-.52,.47),(.045,1.04,.131),"iuchi_oak")
    box(cart,(-.49,-.049,.305),(.98,.098,.092),"iuchi_beam")
    for x in (-.43,.39):
        box(cart,(x-.018,-.061,.281),(.088,.122,.128),"iuchi_bronze")
        for i in range(12):
            a,b=i*pi/6,(i+1)*pi/6
            rim=[(cos(a)*.32,.345+sin(a)*.32),(cos(b)*.32,.345+sin(b)*.32),
                 (cos(b)*.248,.345+sin(b)*.248),(cos(a)*.248,.345+sin(a)*.248)]
            face=[(x,z,y) for z,y in rim]
            side=[(x+.053,z,y) for z,y in reversed(rim)]
            uv=[(0.,0.),(1.,0.),(1.,1.),(0.,1.)]
            cart.quad(face,uv,"iuchi_beam")
            cart.quad(side,uv,"iuchi_beam")
            z1,y1 = rim[0]
            z2,y2 = rim[1]
            cart.quad([(x,z1,y1),(x+.053,z1,y1),(x+.053,z2,y2),(x,z2,y2)],uv,"iuchi_oak")
        box(cart,(x,-.021,.076),(.054,.042,.534),"iuchi_oak")
        box(cart,(x,-.278,.321),(.054,.556,.043),"iuchi_oak")
    export("iuchi_caravan_handcart",cart,MATS)
    shop_board("iuchi_caravan_wayboard","BURIED","LEAVES","#474332")


def terrain(gm,world):
    grass = world.blk==gm.GRASS3
    tint_texture(MEADOW,"iuchi_frosted_meadow",(48,76,37),.081)
    tint_texture(PATH,"iuchi_scoured_sand_scan",(114,76,48),.052)
    # Feather the printed track into the surrounding moss, using the walkable road as its guide.
    size=(world.w*12,world.d*12)
    zz,xx=np.indices((size[1],size[0]),sparse=True)
    moss=np.asarray(Image.open(STAGE/"tex"/(MEADOW+".png")))
    path=np.asarray(Image.open(STAGE/"tex"/(PATH+".png")))
    grain=moss[zz%512,xx%512]
    dirt=path[(zz+39)%512,(xx+83)%512]
    divide=gaussian_filter((~grass[zz//12,xx//12]).astype(np.float32),7.4)
    offset=.065*np.sin(xx*.015+zz*.047) + .046*np.cos(xx*.074-zz*.039)
    blend=np.clip(divide+offset,0,1)[...,None]
    texture=grain*(1-blend)+dirt*blend
    shade=.96+.093*np.sin(xx*.0051+zz*.018)+.044*np.sin(xx*.021-zz*.010)
    Image.fromarray(np.uint8(np.clip(texture*shade[...,None],0,255))).save(STAGE/"tex"/(GROUND+".png"))

    styles={**ground_styles(gm),gm.GRASS3:MEADOW,gm.DIRT:PATH,gm.ROAD:PATH,gm.STONE:"iuchi_mine_slate"}
    mesh=world_mesh(gm,world,styles)
    cleft(mesh,11.8,74.6,13.10,2.035,3.89,4.63)
    for i,face in enumerate(mesh.faces):
        p=np.asarray([mesh.vertices[j] for j in face])
        if mesh.materials[i] not in (MEADOW,PATH) or np.ptp(p[:,2])>.001:
            continue
        if np.cross(p[1]-p[0],p[2]-p[0])[2]<=0:
            continue
        mesh.materials[i]=GROUND
        mesh.uvs[i]=[(2*x/world.w,1-2*z/world.d) for x,z,_ in p]
        for j in face:
            mesh.vertices[j] += [0.,0.,.058]
    return mesh


def layout(gm,w,events):
    placements,lights,leaves=[],[],[]
    cast=np.array([v["pos"][::2][:2] for v in events.ev.values() if v.get("mdlid") not in ("CE000",None)])
    def put(name,x,z,size=1.,yaw=0.,sway=0.,lift=.022):
        bx,bz=x+gm.PAD_X,z+gm.PAD_BOTTOM
        y=(int(w.hgt[bz,bx])+1)*.5+lift
        placements.append([name,bx*.5+.25,y,bz*.5+.25,size,yaw,*([sway] if sway else [])])
        return bx*.5+.25,y,bz*.5+.25
    def lamp(x,z):
        a,y,b=put("iuchi_fitted_andon",x,z,.84)
        lights.append([a,y+.45,b,3.4,1.22])

    for x,z in ((6,6),(16,8),(25,5),(36,6),(46,5),(59,8),(73,6),(82,8),(94,6),(110,8),(116,5),
                (7,21),(32,21),(69,21),(98,21)):
        tree=MAPLE if x in (6,25,32,59,73,98,110) else PINE
        size=.83+x%5*.065
        point=put(tree,x,z,size,.16*x,.020 if tree==MAPLE else .013)
        if tree==MAPLE:
            leaves.extend(falling_leaves(point,size,x))
    for x,z in ((9,10),(14,11),(18,20),(27,9),(34,10),(42,11),(48,19),(51,22),(61,9),(70,10),
                (78,10),(87,20),(93,9),(104,22),(111,10),(116,21)):
        put("wind_grass" if x%3 else "coast_flowers",x,z,.78+x%4*.14,.25*x,.105)
    for x,z,size in ((12,21,.97),(21,22,.93),(40,22,.89),(61,21,1.),(85,23,.81),(100,21,.88)):
        put("iuchi_caravan_lean_to",x,z,size)
    for x,z in ((21,19),(27,20),(59,19),(81,20)):
        assert np.linalg.norm(cast-(x+gm.PAD_X,z+gm.PAD_BOTTOM),axis=1).min()>1.4
        put(BASKET,x,z,.82+x%3*.05,.11*x)
    put("iuchi_caravan_handcart",19,18,.95,1.39)
    put(BASKET,19,18,.75,.08,.0,.45)
    put("iuchi_caravan_handcart",56,19,.88,-1.27)
    put("iuchi_siege_field_hearth",23,22,.76,.29)
    for x,z in ((3,18),(24,19),(55,21),(86,21)):
        lamp(x,z)
    for x,z,size in ((5,16,.95),(46,10,.94),(107,16,.86)):
        put(STONE,x,z,size,.43)
    put("iuchi_caravan_wayboard",4,18,.84)
    return {"placements":placements,"poolLights":lights,"leafDrift":leaves}


def main(repo):
    _,_,gm,_,_=variant(repo,"caravan")
    import voxfile

    sources=props(voxfile)
    camp_models()
    world,events=gm.make("M413")
    export("m413_caravan",terrain(gm,world),MATS)
    row={"terrain":"m413_caravan",**layout(gm,world,events)}
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    index[world.mid]=row
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    evidence={"map":world.mid,"events":len(events.ev),"placements":len(row["placements"]),"sources":sources}
    (HERE/"cakon-caravan-layout.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
