"""Fit the Drop Soup stall to the existing event, footprint and street."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE = Path(__file__).resolve().parent
TEX = STAGE / "tex"


def box(geom, origin, span, surface, spread=.58):
    lo = np.asarray(origin, dtype=float)
    dims = np.asarray(span, dtype=float)
    one = np.eye(3)
    for axis, direction in enumerate(one):
        k, l = (axis+1)%3, (axis+2)%3
        for step in (-1, 1):
            a = lo + (direction * dims if step>0 else 0)
            b, c = one[k]*dims, one[l]*dims
            points = (a,a+b,a+b+c,a+c) if step>0 else (a,a+c,a+b+c,a+b)
            geom.quad(points, [(p[k]/spread,p[l]/spread) for p in points],surface)


def material(key, crop, tint, contrast):
    reference = Image.open(HERE / "town_concepts" / "noodle_counter.png").convert("RGB")
    data = periodic(reference.crop(crop), 256)
    value = data @ [.23,.59,.18]
    v = (value - np.median(value)) / max(np.std(value),1)
    rgb = np.asarray(tint) * (1 + contrast * np.clip(v[..., None],-1.7,1.7))
    Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(TEX / f"{key}.png")


def sign():
    image = Image.open(TEX/"cedar.png").resize((576,288)).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((10,10,566,278),radius=12,outline="#c6a567",width=9)
    draw.line((235,237,541,237),fill="#c8aa75",width=4)
    f = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf",48)
    draw.text((372,93),"NOODLES",font=f,anchor="mm",fill="#f0dbaf")
    draw.text((372,165),"& SOUP",font=f,anchor="mm",fill="#f0dbaf")
    draw.arc((39,100,211,219),0,180,fill="#f0dbaf",width=12)
    draw.line((42,161,208,161),fill="#f0dbaf",width=10)
    for x, y in ((96,78),(129,63),(162,78)):
        draw.line([(x,y),(x-8,y+16),(x+4,y+40)],fill="#e9ca87",width=8)
    image.save(TEX/"stall_sign.png")


def stall():
    geom = Geometry()
    for x in (-2.48,2.35):
        for z in (-1.15,1.25):
            box(geom,(x-.12,z-.12,0),(.34,.34,.11),"stone")
            box(geom,(x,z,.08),(.16,.16,2.32),"cedar")
    for z in (-1.23,1.32):
        box(geom,(-2.60,z,2.17),(5.16,.18,.18),"cedar")
    for x in (-2.48,2.35):
        box(geom,(x,-1.36,2.20),(.15,2.91,.16),"cedar")
    for i in range(30):
        x = -2.49 + i*.166
        box(geom,(x,1.45,.09),(.155,.09,2.12),"cedar",.44)
    for i in range(29):
        x = -2.73 + i * .19
        for side in (-1,1):
            for tier in range(9):
                next_z = (tier+1)*.207
                z = -next_z if side<0 else tier*.207
                y = 2.94 - tier * .072
                box(geom,(x,z,y),(.195,.231,.074),"roof",.46)
    box(geom,(-2.81,-.096,2.998),(5.67,.195,.115),"cedar")
    for z in (-1.89,1.83):
        box(geom,(-2.75,z,2.35),(5.51,.105,.11),"cedar")
    box(geom,(.85,-1.29,1.70),(1.49,.055,.53),"cedar")
    points=[(.87,-1.32,1.72),(2.32,-1.32,1.72),(2.32,-1.32,2.21),(.87,-1.32,2.21)]
    geom.quad(points,[(0,0),(1,0),(1,1),(0,1)],"sign")
    for x in (.97,2.23):
        box(geom,(x,-1.27,2.22),(.03,.031,.12),"stone")
    export("noodle_awning",geom,{"cedar":("cedar.png",.89),"roof":("cedar_roof.png",.92),
                               "stone":("cliff.png",.91),"sign":("stall_sign.png",.92)})


def partitions():
    well = Geometry()
    # Three courses of separate irregular stone blocks with a dark centre.
    for layer in range(3):
        for sector in range(15):
            phase=.12*layer+sector*math.tau/15
            x,z = .55*math.cos(phase),.55*math.sin(phase)
            box(well,(x-.138,z-.133,layer*.126),(.285,.27,.130),"stone",.37)
    box(well,(-.43,-.42,.135),(.86,.84,.013),"depth")
    for x in (-.69,.57):
        box(well,(x,-.11,0),(.14,.16,1.65),"cedar")
    box(well,(-.766,-.14,1.55),(1.57,.20,.16),"cedar")
    box(well,(-.04,-.03,.44),(.048,.048,1.15),"rope")
    export("stone_well",well,{"stone":("cliff.png",.90),"cedar":("cedar.png",.89),
                            "rope":("cedar_roof.png",.86),"depth":("surf00.png",.4)})


def shop_board(key, top, bottom, accent):
    file=key+".png"
    im=Image.open(TEX/"cedar.png").resize((400,256))
    im=Image.blend(im,Image.new("RGB",im.size,accent),.38)
    draw=ImageDraw.Draw(im)
    draw.rectangle((12,12,388,244),outline="#d4b883",width=6)
    font=ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf",43)
    for label, y in ((top,86),(bottom,163)):
        draw.text((200,y),label,anchor="mm",font=font,fill="#f2dfb8")
    im.save(TEX/file)
    mesh=Geometry()
    box(mesh,(-.041,-.065,0),(.082,.117,1.47),"cedar")
    box(mesh,(-.38,-.105,.79),(.76,.097,.56),"cedar")
    quad=[(-.365,-.107,.804),(.365,-.107,.804),(.365,-.107,1.34),(-.365,-.107,1.34)]
    mesh.quad(quad,[(0,0),(1,0),(1,1),(0,1)],"paint")
    export(key,mesh,{"cedar":("cedar.png",.89),"paint":(file,.86)})


def patron_chair():
    geo=Geometry()
    for x in (-.23,.16):
        for z in (-.23,.16):
            box(geo,(x,z,0.),(.075,.073,.43 if z<0 else .77),"cedar")
    for i in range(5):
        box(geo,(-.25+i*.101,-.25,.356),(.097,.50,.065),"cedar")
    for y in (.61,.715):
        box(geo,(-.245,.162,y),(.48,.067,.066),"cedar")
    box(geo,(-.255,-.239,.299),(.50,.065,.057),"cedar")
    export("patron_chair",geo,{"cedar":("cedar.png",.9)})


def patron_table():
    geo=Geometry()
    for x in (-.39,.315):
        for z in (-.174,.099):
            box(geo,(x,z,0.),(.075,.075,.607),"cedar")
    for z in (-.207,-.069,.069):
        box(geo,(-.437,z,.599),(.874,.137,.055),"cedar",.52)
    for x in (-.405,.324):
        box(geo,(x,-.19,.53),(.081,.38,.078),"cedar")
    export("patron_table",geo,{"cedar":("cedar.png",.89)})


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import voxfile
    material("cedar",(261,643,614,757),(103,69,43),.21)
    material("cedar_roof",(273,152,669,232),(106,72,47),.23)
    sign()
    stall()
    partitions()
    shop_board("tea_board","TEA","HOUSE","#294433")
    shop_board("egg_board","EGGS","& GRAIN","#74342a")
    shop_board("fish_board","SALT","FISH","#2a4056")
    patron_chair()
    patron_table()
    # Fit only the generated cooking props. The awning's exact structural
    # dimensions come from its in-game NPC and clearance anchors.
    assets=[
        convert_prop("iron_pot",(.41,.38,.35),25,lower=.18,upper=.72),
        convert_prop("soup_bowl",(.20,.19,.10),19),
    ]
    manifest=[]
    for item in assets:
        manifest.append(save(*item,voxfile))
        voxel_asset(item[0])
    (HERE/"town-props.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    serving=Geometry()
    box(serving,(-.90,-.27,.82),(1.8,.55,.078),"cedar")
    for x in (-.81,.72):
        for z in (-.24,.14):
            box(serving,(x,z,0),(.11,.11,.83),"cedar")
    for z in (-.27,.22):
        for j in range(3):
            box(serving,(-.88,z,.45+j*.118),(1.77,.04,.115),"cedar")
    export("soup_counter",serving,{"cedar":("cedar.png",.9)})
    layouts=json.loads((STAGE/"index.json").read_bytes())
    town=layouts.setdefault("M103",{"placements":[]})
    scenery=[row for row in town["placements"] if row[0] in ("wind_grass","coast_flowers") and
            ((row[3]<9. or row[3]>24.5) and (row[2]<3.6 or row[2]>5.0))]
    if len(scenery)>188:
        selection=np.random.default_rng(10323).choice(len(scenery),188,replace=False)
        scenery=[scenery[i] for i in sorted(selection)]
    town["placements"]=scenery+[
        ["noodle_awning",57.25,2.,18.25,1.,0.],
        ["soup_counter",58.4,2.,17.93,1.,0.],
        ["iron_pot",58.86,2.898,17.99,1.,.09],
        ["soup_bowl",58.08,2.899,17.74,1.,.07],
        ["soup_bowl",57.74,2.899,17.74,1.,.21],
        ["patron_chair",55.07,2.,17.01,1.,.0],
        ["patron_table",55.07,2.,16.64,1.,.015],
        ["soup_bowl",55.08,2.654,16.68,1.08,.07],
        ["soup_bowl",55.34,2.654,16.61,.76,-.13],
        ["cedar_bench",55.70,2.,17.93,.87,.04],
        ["salt_crate",59.22,2.,18.85,1.,.23],
        ["stone_well",24.85,2.,20.05,1.,.08],
        ["tea_board",49.80,2.,17.13,1.,.05],
        ["egg_board",39.42,2.,16.93,1.,-.09],
        ["fish_board",47.99,2.,13.10,1.,.03],
    ]
    town["seats"]=[{"event":10,"motion":"taneo_chair"}]
    (STAGE/"index.json").write_text(json.dumps(layouts,separators=(",",":")),encoding="utf-8")


if __name__=="__main__":
    main()
