"""Build the Ojatara roadside camps, towns, bell hill, graves, and arenas."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as KAIU, world_mesh
from export_coast import Geometry, STAGE, export, voxel_asset
from ojatara_worlds import MAPS, variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE=Path(__file__).resolve().parent
MATS={
    **KAIU,
    "ojatara_grass":("ojatara_autumn.png",.94),
    "ojatara_ash":("ojatara_ash.png",.93),
    "ojatara_clay":("ojatara_clay.png",.92),
    "ojatara_stone":("ojatara_stone.png",.91),
    "ojatara_trim":("ojatara_trim.png",.86),
    "ojatara_flower":("ojatara_flowerbed.png",.94),
    "indigo_canvas":("ojatara_canvas_indigo.png",.93),
    "oxide_canvas":("ojatara_canvas_oxide.png",.94),
    "offwhite_canvas":("ojatara_canvas_offwhite.png",.93),
    "shelter_timber":("ojatara_shelter_timber.png",.94),
    "shelter_cord":("ojatara_shelter_cord.png",.96),
}

CAMP_TENTS={
    "M368":((69,23,1.12),(79,23,1.04)),
    "M369":((88,8,1.08),(96,11,1.04),(104,7,1.02),(14,8,1.09),(32,10,1.04)),
    "M371":((11,23,1.04),(21,24,1.10),(87,23,1.08),(97,24,1.03)),
}


def surfaces():
    for key,source,tint in (
        ("autumn","ojatara_autumn_meadow",(48,79,39)),
        ("ash","ojatara_earth_v2",(41,35,33)),
        ("clay","ojatara_earth_v2",(86,58,40)),
        ("stone","ojatara_rain_stone",(64,71,73)),
        ("trim","ojatara_earth_v2",(60,33,26)),
        ("flowerbed","ojatara_autumn_meadow",(55,86,43)),
        ("canvas_indigo","ojatara_indigo_canvas",(30,49,87)),
        ("canvas_oxide","ojatara_oxblood_canvas",(111,47,39)),
        ("canvas_offwhite","ojatara_offwhite_canvas",(151,133,103)),
        ("shelter_timber","kamen_temple_cypress",(46,31,27)),
        ("shelter_cord","ojatara_offwhite_canvas",(130,100,63)),
    ):
        image=Image.open(HERE/f"surface_sources/{source}.png").convert("RGB")
        value=periodic(image,768)@[.26,.61,.13]
        if key in ("ash","clay"):
            smooth=np.asarray(Image.fromarray(np.uint8(value)).filter(ImageFilter.GaussianBlur(17.)))
            detail=value-smooth
            grain=1+.085*np.clip(detail/max(1.,detail.std()),-2.3,2.3)
            grain+=.26*(smooth/max(1.,np.median(smooth))-1)
        else:
            grain=np.clip(value/max(1.,np.median(value)),.57,1.43)
        colors=np.asarray(tint)*(.22+.78*grain[...,None])
        Image.fromarray(np.uint8(np.clip(colors,0,255))).save(STAGE/f"tex/ojatara_{key}.png")


def gate():
    shut=Geometry()
    for side in (-1,1):
        x=side*1.265
        box(shut,(x-.15,-.17,0.),(.30,.37,2.89),"ojatara_stone")
    box(shut,(-1.51,-.21,2.58),(3.02,.45,.42),"ojatara_stone")
    for i in range(10):
        box(shut,(-1.115+i*.225,-.07,.065),(.217,.154,2.48),"ojatara_trim",1.66)
    for y in (.25,1.02,1.84):
        box(shut,(-1.16,-.128,y),(2.32,.093,.072),"kaiu_roof")
    for x in (-.13,.04):
        box(shut,(x,-.162,.99),(.093,.071,.23),"kaiu_roof")
    export("ojatara_sealed_mine",shut,MATS)
    shop_board("ojatara_buried_leaves_sign","BURIED","LEAVES","#544b3c")
    shop_board("ojatara_welcome_road_sign","THE WELCOME","ROAD","#504034")
    shop_board("ojatara_tribunal_sign","OJATARA","TRIBUNAL","#5d4337")
    shop_board("ojatara_petal_sign","PERFUME PETAL","BLOSSOM","#65504f")


def shelter(name, width, depth, eave, fabric, repair):
    tent=Geometry()
    length=width*.5
    half=depth*.5
    for x in (-length+.14,length-.14):
        for z in (-half+.105,half-.10):
            box(tent,(x-.11,z-.13,0.),(.22,.25,.115),"ojatara_stone")
            box(tent,(x-.055,z-.058,.105),(.11,.116,eave-.095),"shelter_timber",.72)
            for y in (eave-.24,eave-.198):
                box(tent,(x-.062,z-.065,y),(.124,.13,.026),"shelter_cord",.19)
        box(tent,(x-.036,-half+.06,eave-.075),(.073,depth-.12,.104),"shelter_timber",.92)
    for z in (-half+.05,half-.085):
        box(tent,(-length-.03,z,eave-.066),(width+.06,.082,.11),"shelter_timber",1.13)
    box(tent,(-length-.12,-.052,eave+.413),(width+.24,.105,.105),"shelter_timber",1.24)
    for x in (-length+.15,length-.15):
        box(tent,(x-.034,-.034,eave-.068),(.067,.067,.54),"shelter_timber",.44)
    def canvas_height(x,z):
        sag=.067*(1.-(x/length)**2)*abs(z/half)
        folds=.022*math.cos(x*3.7+z*.8)*abs(z/half)
        return eave+.49*(1.-abs(z/half))-sag+folds

    def canvas(x0,x1,z0,z1,material,lift=0.):
        edges=((x0,z0),(x1,z0),(x1,z1),(x0,z1))
        points=[(x,z,canvas_height(x,z)+lift) for x,z in edges]
        uv=[(x/1.07,z/1.07) for x,z in edges]
        tent.quad(points,uv,material)
        if not lift:
            tent.quad([(x,z,y-.043) for x,z,y in reversed(points)],list(reversed(uv)),material)

    for xs in range(9):
        x0=-length-.085+(width+.17)*xs/9
        x1=-length-.085+(width+.17)*(xs+1)/9
        for a,b in ((-half,-half*.53),(-half*.53,0.),(0.,half*.53),(half*.53,half)):
            canvas(x0,x1,a,b,fabric)
    canvas(-length+.19,-length+.68,-half*.78,-half*.45,repair,.015)
    canvas(length-.74,length-.31,half*.44,half*.73,repair,.015)
    for sign in (-1,1):
        x=sign*(length+.045)
        for row in range(6):
            z=-half+row*depth/6.
            drop=.075+.023*((row*3)%4)
            box(tent,(x-.023,z+.015,eave-drop),(.046,depth/6.-.013,drop+.058),repair,.67)
    # The lower span remains open. Only the last quarter of the back gets a rain flap.
    for i in range(6):
        x=-length+width*i/6
        drop=.39+.04*((i*7)%4)
        box(tent,(x+.012,half-.052,eave-drop),(width/6-.013,.057,drop+.033),fabric,.79)
    export(name,tent,MATS)


def terrain(gm,m):
    floor=gm.T(4,4)
    m.blk[m.blk==gm.STONEW]=floor
    style={
        gm.GRASS:"ojatara_grass",gm.GRASS2:"ojatara_grass",gm.GRASS3:"ojatara_grass",
        gm.SL_GROUND:"ojatara_ash",gm.DIRT:"ojatara_clay",gm.ROAD:"ojatara_clay",
        gm.STONE:"ojatara_stone",gm.STONEW:"ojatara_stone",floor:"ojatara_stone",
        gm.POPPYF:"ojatara_flower",
    }
    if m.mid=="M372":
        style[gm.DARKWOOD]="ojatara_trim"
    result=world_mesh(gm,m,style)
    for face,key in zip(result.faces,result.materials,strict=True):
        if key not in ("ojatara_grass","ojatara_ash","ojatara_clay","ojatara_flower"):
            continue
        verts=np.array([result.vertices[i] for i in face])
        if np.ptp(verts[:,2])<.0001:
            for i in face:
                result.vertices[i]=result.vertices[i]+[0.,0.,.055]
    return result


def loam_atlas(geometry,world):
    width=2048
    height=max(512,round(width*world.d/world.w))
    rng=np.random.default_rng(int(world.mid[1:]))
    broad=Image.fromarray(rng.integers(24,224,(8,18),dtype=np.uint8)).resize((width,height),Image.Resampling.BICUBIC)
    earth=np.asarray(Image.open(STAGE/"tex/ojatara_clay.png").convert("RGB"),dtype=float)
    height_cells,width_cells=np.indices((height,width),sparse=True)
    sampled=earth[(height_cells*983//height)%earth.shape[0],(width_cells*2391//width)%earth.shape[1]]
    soil=(np.asarray(broad,dtype=float)/255.-.5)[...,None]
    color=np.clip(sampled+soil*[37,45,27],0,255).astype(np.uint8)
    key=f"{world.mid.lower()}_loam"
    filename=f"{key}.png"
    Image.fromarray(color).save(STAGE/"tex"/filename)
    for n,(face,style) in enumerate(zip(geometry.faces,geometry.materials,strict=True)):
        if style!="ojatara_clay":
            continue
        vertices=np.asarray([geometry.vertices[i] for i in face])
        if np.ptp(vertices[:,2])<.0001:
            geometry.materials[n]=key
            geometry.uvs[n]=[(x*2/world.w,z*2/world.d) for x,z,_ in vertices]
    return {**MATS,key:(filename,.92)}


def layout(gm,m):
    mid=m.mid
    arena=mid in ("M869","M870","M871")
    placements=[]
    lights=[]
    doors=[]

    def put(key,x,z,scale=1.,turn=0.,rise=0.,wind=None):
        bx,bz=(x,z) if arena else (x+gm.PAD_X,z+gm.PAD_BOTTOM)
        y=(int(m.hgt[bz,bx])+1)*.5+rise
        row=[key,bx*.5+.25,y,bz*.5+.25,scale,turn]
        if wind:
            row.append(wind)
        placements.append(row)
        return row[1:4]

    def lamp(x,z):
        xx,y,zz=put("kamen_hospitality_lantern",x,z,.88)
        lights.append([xx,y+1.08,zz,4.5,1.50])

    def house(x,z,event=None):
        a=(gm.PAD_X+x)*.5
        b=(gm.PAD_BOTTOM+z)*.5-.118
        if event is None:
            placements.extend([["kudo_shut_door",a,2.5,b,1.,0.],
                               ["town_door_stoop_half",a,2.,b,1.,0.]])
        else:
            doors.append({"x":a,"y":2.5,"z":b,"grade":2.,"event":event,
                          "stoop":"town_door_stoop_half"})

    for n,(x,z,size) in enumerate(CAMP_TENTS.get(mid,())):
        asset="ojatara_refugee_shelter_indigo" if (n+(mid=="M369"))%2==0 else "ojatara_refugee_shelter_oxide"
        put(asset,x,z,size,.06*((x%3)-1))
        put("ojatara_field_sacks",x-2,z-1,.84,.13)

    if mid=="M368":
        for x,z in ((16,23),(26,23)):
            put("ojatara_refugee_shelter_indigo",x,z,.92,.11)
        for x,z in ((8,29),(28,28),(46,29),(56,8),(81,9),(101,29)):
            put("coast_pine",x,z,.85+.075*(x%5),x*.24)
        for x,z in ((8,12),(40,12),(64,11),(91,11)):
            put("ojatara_stone_waypost",x,z,.85+.05*(x%3),x*.09)
        for x,z in ((14,9),(34,5),(47,9),(63,9),(78,10),(95,8)):
            put("shadowlands_burnt_stump",x,z,.56+.10*(x%3),x*.32)
    elif mid=="M369":
        put("ojatara_buried_leaves_sign",8,12,.94)
        put("ojatara_welcome_road_sign",10,20,.90)
        put("ojatara_tribunal_sign",35,21,1.)
        put("ojatara_costume_trunk",84,11,1.05,.16)
        for x in (4,25,52,68,84,100):
            lamp(x,20)
        for x,z in ((5,9),(28,32),(89,34),(98,24),(107,19)):
            put("ojatara_field_sacks",x,z,1.0,.11)
        for x,event in ((14,97),(39,2),(61,98),(75,99)):
            house(x,22,event)
        put("kamen_street_gateway",84,22,.83)
    elif mid=="M371":
        put("ojatara_command_shelter",64,23,1.05,.02)
        put("ojatara_field_sacks",67,21,1.09,.13)
        for x,z in ((12,6),(26,4),(44,7),(64,5),(82,6)):
            put("ojatara_collapsed_timber",x+2,z+1,.53,.29*x)
        for x,z in ((18,20),(32,20),(62,19),(68,19),(92,20)):
            lamp(x,z)
    elif mid=="M372":
        put("ojatara_funeral_offering",36,19,1.02,-.12)
        for x,z in ((29,21),(46,22),(49,24),(32,26),(41,25)):
            put("ojatara_collapsed_timber",x,z,.81+.09*(x%4),x*.19)
        for x,z in ((6,12),(24,9),(54,9),(73,12)):
            put("coast_pine",x,z,.98,x*.17)
        lamp(34,18)
        lamp(44,18)
        for x in (13,38,61):
            house(x,20)
    elif mid=="M374":
        put("ojatara_yotomo_bell",47,23,1.07,-.05)
        for x,z in ((26,24),(38,23),(55,24),(63,11),(79,19)):
            put("ojatara_stone_waypost",x,z,.87+.09*(x%3),x*.24)
        for x,z in ((7,7),(23,8),(54,7),(69,8),(86,7)):
            put("coast_pine",x,z,.86+.08*(x%4),x*.23)
        lamp(44,19)
        lamp(51,20)
        for x in (11.5,23.5,73.5,83.5):
            house(x,22)
    elif mid=="M375":
        put("ojatara_petal_sign",20,11,.98)
        for row in range(11):
            x=3+9*row
            put("ojatara_flower_planter",x+1,10,.91+.06*(row%3),.03*(row%5))
            for z in (4,7):
                for off in (0,3,5):
                    put("coast_flowers",x+off,z,.77+.09*((row+off)%5),.3*((row+off)%7),0.,.08)
        for x,z in ((8,19),(23,19),(36,19),(55,19),(67,19),(80,19),(94,19)):
            lamp(x,z)
        for x in (11,27,65,81):
            house(x,22)
        house(46,22,2)
        put("kamen_street_gateway",70,21,.77)
    elif mid=="M377":
        for x in range(6,86,7):
            for z in (6,22):
                put("ojatara_grave_marker",x+1,z+x%3,.79+.08*(x%4),.12*(x%5))
                put("coast_flowers",x+2,z+x%3,.52+.07*(x%4),.11*x,0.,.05)
        put("ojatara_sealed_mine",83,15,1.18,math.pi/2,-.05)
        put("ojatara_collapsed_timber",81,11,.81,.48)
        lamp(79,18)
    elif mid=="M378":
        for x in range(5,97,9):
            put("coast_pine",x,7+x%3,.88+.09*(x%4),x*.17)
        for x in (18,28,39,52,65,82,93):
            put("ojatara_stone_waypost",x,19,.66+.1*(x%3),x*.39)
        for x in (29,46,71):
            lamp(x,10)
    elif mid=="M869":
        for x in (11,32,94,115):
            put("ojatara_refugee_shelter_oxide",x,87,1.12,.07)
            put("ojatara_field_sacks",x+3,84,1.14,.2)
        for x in (14,41,72,98,119):
            put("coast_pine",x,108,.95+.09*(x%3),x*.24)
    elif mid=="M870":
        for x in range(8,127,12):
            z=97+(x-2)%5
            put("ojatara_grave_marker",x,z,1.08+x%3*.13,.1*(x%4))
            put("coast_flowers",x-1,z,1.05,0.,0.,.06)
    else:
        for x in range(8,126,11):
            put("coast_pine",x,89+(x%2),1.15+.12*(x%4),x*.37)
        for x in (21,62,104):
            lamp(x,88)
    return placements,lights,doors


def main(repo):
    _,_,gm,_,_=variant(repo)
    import voxfile

    surfaces()
    gate()
    shelter("ojatara_refugee_shelter_indigo",2.71,1.87,1.79,"indigo_canvas","oxide_canvas")
    shelter("ojatara_refugee_shelter_oxide",2.71,1.87,1.79,"oxide_canvas","indigo_canvas")
    shelter("ojatara_command_shelter",3.35,2.23,2.08,"offwhite_canvas","oxide_canvas")
    sources={}
    for key,dimensions,count in (
        ("ojatara_costume_trunk",(.78,.50,.53),37),
        ("ojatara_field_sacks",(.93,.62,.65),34),
        ("ojatara_stone_waypost",(.49,.45,.96),38),
        ("ojatara_yotomo_bell",(2.12,1.55,2.58),47),
        ("ojatara_flower_planter",(.94,.61,.75),40),
        ("ojatara_grave_marker",(.73,.48,.69),36),
        ("ojatara_funeral_offering",(1.03,.59,.85),38),
        ("ojatara_collapsed_timber",(1.68,.87,.68),40),
    ):
        sources[key]=save(*convert_prop(key,dimensions,count,lower=.02),voxfile)
        voxel_asset(key)
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    stats={}
    for mid in MAPS:
        m,events=gm.make(mid)
        key=f"{mid.lower()}_ojatara"
        land=terrain(gm,m)
        materials=loam_atlas(land,m) if mid in ("M369","M371","M869","M871") else MATS
        export(key,land,materials)
        placements,lights,doors=layout(gm,m)
        index[mid]={"terrain":key,"placements":placements,"poolLights":lights,"doors":doors}
        stats[mid]={"props":len(placements),"doors":len(doors),"lanterns":len(lights),
                    "events":len(events.ev) if events else 0}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"ojatara-valley-layout.json").write_text(
        json.dumps({"maps":stats,"sources":sources},indent=2),encoding="utf8")


if __name__=="__main__":
    main(Path(sys.argv[1]))
