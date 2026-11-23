"""Build fitted native scenery for all eight roamable clan castles."""
from copy import copy
from math import cos, pi, sin
from pathlib import Path
import argparse
import json
import sys

import numpy as np
from PIL import Image, ImageFilter

from build_hoshi_stall import box
from build_kaiu_kit import MATS, world_mesh
from comfy_surface_pass import OUT as SCANS
from diorama_trees import MAPLE, build_diorama_mesh, falling_leaves
from export_coast import Geometry, STAGE, export
from prepare_coast import periodic

HERE = Path(__file__).resolve().parent
WATER = "cakon_river"
THEMES = {
    "Kyuden Hida": ("hida", (27, 46, 66), (141, 54, 42), (102, 108, 110), (201, 189, 166)),
    "Kyuden Doji": ("doji", (61, 98, 130), (209, 218, 216), (128, 131, 124), (222, 216, 193)),
    "Shiro Akodo": ("akodo", (85, 66, 51), (187, 133, 51), (120, 118, 109), (209, 197, 169)),
    "Kyuden Isawa": ("isawa", (96, 54, 41), (199, 112, 44), (117, 104, 92), (212, 194, 161)),
    "Kyuden Bayushi": ("bayushi", (40, 31, 41), (170, 53, 62), (112, 94, 101), (142, 105, 91)),
    "Shiro Kitsuki": ("kitsuki", (49, 74, 59), (179, 149, 66), (108, 119, 111), (200, 190, 160)),
    "Shiro Iuchi": ("iuchi", (65, 54, 85), (172, 117, 153), (122, 115, 121), (203, 190, 174)),
    "Kyuden Togashi": ("togashi", (54, 71, 61), (172, 123, 56), (104, 115, 103), (185, 174, 144)),
}
MODELS = {
    "castle_kaiu_lantern": (.54, 1.03, .54),
    "castle_lacquer_supply_chest": (.93, .56, .48),
    "castle_council_table": (1.07, .50, .55),
    "castle_diorama_matsu": (2.76, 3.13, 2.43),
    "castle_iris_clump": (.44, .61, .43),
    "castle_tamori_stones": (1.85, .93, 1.18),
    "castle_unicorn_saddle": (.68, .85, .48),
    "castle_bayushi_mask_stand": (.77, .49, .33),
    "castle_snow_pine": (3.14, 3.70, 2.68),
    "castle_lion_makiwara": (1.14, 1.50, .66),
    "castle_isawa_incense": (.58, .54, .58),
    "castle_kitsuki_archive": (1.34, .97, .49),
}
DECOR = {"EP210": "castle_sword_rest", "EP215": "castle_scroll_stack",
         "EP216": "castle_scroll_stack", "EP220": "castle_paper_andon"}
LANTERN = "castle_kaiu_lantern"
CHEST = "castle_lacquer_supply_chest"
TABLE = "castle_council_table"
MATSU = "castle_diorama_matsu"
ROCK = "castle_tamori_stones"
IRIS = "castle_iris_clump"


def castle_turf():
    source=Image.open(STAGE/"tex/meadow.png").convert("RGB").resize((768,768))
    light=np.asarray(source).astype(float) @ [.22,.67,.11]
    coarse=np.asarray(source.filter(ImageFilter.GaussianBlur(14))).astype(float) @ [.22,.67,.11]
    relief=np.clip((light-np.median(light))/max(np.std(light),1.),-2.1,2.1)
    bands=np.clip((coarse-np.median(coarse))/max(np.std(coarse),1.),-2.0,2.0)
    tint=np.array((78,100,58))
    rgb=tint*(1+.11*relief[...,None]+.072*bands[...,None])
    Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(STAGE/"tex/castle_turf.png")


def material_files(theme):
    slug, dark, accent, stone, plaster = theme
    mats = dict(MATS)
    mats.update({key: (key + ".png", .93) for key in (
        "highland_snow", "tea_tatami", "cakon_river_grass", "cakon_silt", "dragon_snow")})
    mats["cakon_river_grass"]=("castle_turf.png",.95)
    samples = {
        "stone": (SCANS / "castle_ishigaki_scan.png", stone, .20),
        "wood": (STAGE / "tex/kaiu_wood.png", dark, .16),
        "plaster": (STAGE / "tex/kaiu_plaster.png", plaster, .10),
        "roof": (STAGE / "tex/kaiu_roof.png", dark, .19),
        "paper": (STAGE / "tex/kaiu_shoji.png", (213, 192, 152), .11),
        "floor": (SCANS / "castle_cedar_board_scan.png", (115, 84, 63), .22),
        "accent": (STAGE / "tex/kaiu_wood.png", accent, .13),
        "gravel": (STAGE / "tex/cakon_market_setts.png", tuple(min(v+29, 195) for v in stone), .14),
        "linen": (STAGE / "tex/tea_tatami.png", (200, 189, 167), .08),
    }
    for material, (image, color, contrast) in samples.items():
        source = Image.open(image).convert("RGB")
        tex = periodic(source.crop((8, 8, source.width-8, source.height-8)), 512)
        value = tex @ [.25, .62, .13]
        relief = np.clip((value-np.median(value))/max(np.std(value), 1.), -2.4, 2.4)
        arr = np.asarray(color) * (1 + contrast*relief[..., None])
        if material == "paper":
            for step in range(0, 512, 128):
                arr[:, step:step+8, :] *= .43
                arr[step:step+7, :, :] *= .43
        if material == "roof":
            for step in range(0, 512, 43):
                arr[:, step:step+3, :] *= .66
        key = f"castle_{slug}_{material}"
        file = key + ".png"
        Image.fromarray(np.uint8(np.clip(arr, 0, 255))).save(STAGE / "tex" / file)
        mats[key] = file, .87 if material in {"wood", "roof"} else .94
    return mats


def roof(geom, x, z, y, width, length, rise, wood, tiles):
    half = length/2
    steps = 7
    course = half/steps
    def height(distance):
        t = distance/half
        return y + rise * (t**1.64) - .095*sin(pi*t)
    for side in (-1, 1):
        for row in range(steps):
            a, b = row*course, (row+1)*course
            za, zb = z + side*(half-a), z + side*(half-b)
            reach_a, reach_b = .17*(1-a/half), .17*(1-b/half)
            face = [(x-reach_a,za,height(a)),(x+width+reach_a,za,height(a)),
                    (x+width+reach_b,zb,height(b)),(x-reach_b,zb,height(b))]
            if side == 1:
                face.reverse()
            geom.quad(face, [(p[0]/2.3,p[1]/2.3) for p in face], tiles)
            box(geom,(x-reach_a,za-.034,height(a)-.05),(width+2*reach_a,.068,.082),tiles,.9)
        eave = z + side*half
        box(geom,(x-.22,eave-.07,y-.145),(width+.44,.14,.13),wood,1.5)
        for rafter in np.arange(x+.06,x+width,.39):
            box(geom,(rafter,eave-.125,y-.22),(.085,.27,.17),wood,.8)
    box(geom,(x-.24,z-.11,y+rise-.035),(width+.48,.22,.18),tiles,1.4)
    for end in (x-.26, x+width+.14):
        box(geom,(end,z-.14,y+rise+.065),(.14,.28,.22),tiles,1.1)


def fitting_strip(geom, gm, world, slug):
    def style(key):
        return f"castle_{slug}_{key}"

    # Filter the stock roof courses from the visible shell. The fitted kawara
    # pieces keep the same building footprint and clear volume above pathways.
    roofs = [o for o in world.objs if o["t"]=="fill" and o["blk"]==gm.ROOF and o["w"]>=8]
    roots = []
    for item in roofs:
        if roots and (item["x"],item["w"])==(roots[-1][-1]["x"],roots[-1][-1]["w"]) and item["y"]==roots[-1][-1]["y"]+1:
            roots[-1].append(item)
        else:
            roots.append([item])
    remove = set(map(id, roofs))
    for chain in roots:
        low, high = chain[0], chain[-1]
        x, z = low["x"]*.5, (low["z"]+low["d"]*.5)*.5
        height = (low["y"]+.20)*.5
        rise = max(.68,(high["y"]-low["y"])*.51+.35)
        roof(geom,x,z,height,low["w"]*.5,low["d"]*.5+.15,rise,style("wood"),style("roof"))
        for obj in world.objs:
            if obj["t"]=="fill" and obj["blk"]==gm.DARKWOOD and obj["x"]==high["x"]-1 and obj["w"]==high["w"]+2 and obj["y"]==high["y"]+1:
                remove.add(id(obj))
        if low["w"] >= 33 and low["y"] >= 24 and len(chain) > 3:
            # A narrow watch storey nests into the main ridge. Set back the
            # facade so the keep reads as successive roofs from ground level.
            upper_base = height + rise - .51
            center = x + low["w"]*.25
            upper_w = low["w"]*.265
            upper_d = low["d"]*.235
            upper_x, upper_z = center-upper_w/2, z-upper_d/2
            box(geom,(upper_x,upper_z,upper_base),(upper_w,upper_d,1.84),style("plaster"),1.8)
            box(geom,(upper_x-.055,upper_z-.115,upper_base+.25),(upper_w+.11,.13,.22),style("wood"),1.25)
            for column in np.arange(upper_x+.1,upper_x+upper_w,1.30):
                box(geom,(column,upper_z-.074,upper_base),(.12,.10,1.82),style("wood"),1.2)
                box(geom,(column+.23,upper_z-.070,upper_base+.68),(.68,.09,.56),style("paper"),1.05)
            roof(geom,upper_x-.38,z,upper_base+1.84,upper_w+.76,upper_d+1.01,1.19,
                 style("wood"),style("roof"))
        if low["w"] < 18 or len(chain) == 1:
            continue
        front = (low["z"]+1)*.5
        ground = (int(world.hgt[low["z"]+1,low["x"]+1])+1)*.5
        if ground+.8 < height:
            left, right=x+.70,x+low["w"]*.5-.70
            openings=[(o["x"]*.5,(o["x"]+o["w"])*.5) for o in world.objs if
                      o["t"]=="fill" and o["blk"]==gm.VOID and o["z"]*.5==front and left<o["x"]*.5<right]
            gaps=[left]
            for start,end in sorted(openings):
                gaps.extend((start-.07,end+.07))
            gaps.append(right)
            for start,end in zip(gaps[::2],gaps[1::2],strict=True):
                if end>start:
                    box(geom,(start,front-.085,ground+.72),(end-start,.11,.12),style("wood"),1.4)
            for column in np.arange(x+.95,x+low["w"]*.5-.85,1.5):
                if any(start-.10<=column<=end for start,end in openings):
                    continue
                box(geom,(column,front-.055,ground+.38),(.10,.095,max(.55,height-ground-.55)),style("wood"),1.4)
    return remove


def add_gate(geom, x, z, floor, slug, width, height, *, roofed=True):
    def style(name):
        return f"castle_{slug}_{name}"
    for px in (x-width/2-.20, x+width/2-.20):
        box(geom,(px-.10,z-.40,floor),(.59,.80,.32),style("stone"))
        box(geom,(px,z-.25,floor+.28),(.39,.50,height-.20),style("wood"))
        box(geom,(px-.055,z-.30,floor+height-.38),(.50,.60,.23),style("accent"))
    box(geom,(x-width/2-.5,z-.29,floor+height),(width+1.0,.58,.30),style("wood"))
    if roofed:
        roof(geom,x-width/2-.65,z,floor+height+.28,width+1.3,1.60,.64,style("wood"),style("roof"))


def arts_booth(geom, x, z, y, slug, width=3.60, depth=2.15, open_front=True):
    def style(name):
        return f"castle_{slug}_{name}"
    for dx in (0,width-.13):
        for dz in (0,depth-.13):
            box(geom,(x+dx,z+dz,y),(.13,.13,2.05),style("wood"))
    box(geom,(x,z+depth-.15,y+.24),(width,.12,1.54),style("paper"))
    if not open_front:
        box(geom,(x,z+.12,y+.18),(width,depth-.24,1.62),style("wood"))
    box(geom,(x-.20,z-.15,y),(width+.40,depth+.30,.19),style("floor"))
    roof(geom,x-.26,z+depth/2,y+2.03,width+.52,depth+.53,.66,style("wood"),style("roof"))


def yard_features(geom, gm, w, col, row, theme, put):
    slug = theme[0]
    tree = "castle_snow_pine" if slug in {"hida","akodo"} else MATSU
    motif = {"hida":"stone", "doji":"water", "akodo":"drill", "isawa":"rings", "bayushi":"masks",
             "kitsuki":"rock", "iuchi":"horses", "togashi":"rock"}[slug]
    accent, wood, stone = (f"castle_{slug}_{key}" for key in ("accent","wood","stone"))
    def cells(x,z):
        return x+gm.PAD_X, z+gm.PAD_BOTTOM
    def mx(x,z):
        a,b=cells(x,z)
        return a*.5+.25,b*.5+.25,(int(w.hgt[b,a])+1)*.5
    def item(model,x,z,scale=1.,heading=0.,sway=0.,raise_by=0.):
        put(model,*cells(x,z),scale,heading,sway,raise_by)
    def banner(x,z,height=2.7):
        a,b,y=mx(x,z)
        box(geom,(a-.07,b-.07,y),(.14,.14,height),wood,.85)
        box(geom,(a-.57,b-.06,y+height-.18),(1.02,.12,.085),wood,.64)
        box(geom,(a-.51,b-.037,y+height-1.45),(.79,.074,1.28),accent,.76)
        box(geom,(a-.36,b-.044,y+height-.95),(.47,.089,.105),stone,.32)
        box(geom,(a-.33,b-.046,y+height-.67),(.41,.091,.086),stone,.32)
    if (col,row)==(1,0):
        x,z,y=mx(48,12)
        add_gate(geom,x-.25,z,y,slug,4.6,4.05)
        for px in (39,57):
            banner(px,17)
        for px in (30,65):
            item(tree,px,21,1.08,px*.23,.012)
        return
    if (col,row)==(1,2):
        x,z,y=mx(48,35)
        add_gate(geom,x-.25,z,y,slug,3.30,2.88)
        for side in (-1,1):
            banner(48+side*8,37,3.1)
            item(tree,48+side*22,47,1.11,side*.51,.012)
            item(LANTERN,48+side*5,34,.95)
            a,b,y=mx(48+side*25,53)
            arts_booth(geom,a-2.05,b,y,slug,4.1,2.6,False)
        return
    if row==1 or (col,row)==(1,3):
        for k,(x,z) in enumerate(((18,18),(70,18),(18,44),(70,44))):
            if motif in {"water","rings"} and (motif=="water" or x>48):
                for j in range(3):
                    item(IRIS,x-3+3*j,z+3,.86+j*.12,j*.48,.045)
                item(ROCK,x+6,z-3,1.06,k*.71)
            elif motif=="horses":
                item("castle_unicorn_saddle",x,z+4,1.02,.25*k)
                # Keep the hitching rail to one side of the tent entrance.
                for j in (6, 10):
                    a,b,y=mx(x+j,z-3)
                    box(geom,(a-.08,b-.08,y),(.16,.16,.93),wood)
                a,b,y=mx(x+6,z-3)
                box(geom,(a,b-.065,y+.68),(2.0,.13,.13),wood,.95)
            elif motif=="masks":
                a,b,y=mx(x-4,z+2)
                arts_booth(geom,a,b,y,slug,3.45,1.75)
                item(TABLE,x-1,z+4,1.07,0.,raise_by=.18)
                item("castle_bayushi_mask_stand",x-1,z+4,.92,0.,raise_by=.71)
            elif motif=="drill":
                for j in (-3, 3):
                    item("castle_lion_makiwara",x+j,z+2,1.11,k*.14)
            else:
                item(ROCK,x+3,z+3,1.18,k*1.13)
            item(LANTERN,x-5,z+5,.76,k*.51)
        if (col,row)==(1,3):
            for x in (20,75):
                banner(x,50,2.4)
        elif col==2:
            a,b,y=mx(50,52)
            arts_booth(geom,a+2.5,b,y,slug)
            item(TABLE,57,54,1.05,raise_by=.18)
        return
    if (col,row)==(2,0):
        for x in (13,23,66,76):
            item("castle_unicorn_saddle" if motif=="horses" else CHEST,x,20,1.,x*.4)
        for x in (12,67):
            a,b,y=mx(x,15)
            arts_booth(geom,a,b,y,slug,3.90,2.32)
    elif (col,row)==(0,2):
        for x in (16,24,68,76):
            item(TABLE,x,19,1.08)
            item(CHEST,x+2,21,.80)
    elif (col,row)==(2,2):
        if slug=="isawa":
            for x,z in ((31,15),(34,13),(37,15),(37,20),(31,20)):
                item("castle_isawa_incense",x,z,1.24,x*.59)
        for x in (13,26):
            item(LANTERN,x,12,.94)
            item(ROCK,x+1,9,1.03,.57)
        banner(22,7,2.35)
    elif (col,row)==(0,3):
        for x in (12,20,66,74):
            for dz in (13,17):
                item(IRIS,x+1,dz,.62,x*.15,.045)
        for x in (28,82):
            item(CHEST,x,18,.75,pi/2)
    else:
        for x in (17,72):
            banner(x,18)
            item(CHEST,x+4,19,1.02,pi/2)
    for x in (32,63):
        item(tree,x,21,.98,.19*x,.012)


def interior_features(geom, gm, world, level, theme, put):
    slug = theme[0]
    ox, oz = gm.ROOM_OFS[world.mid]
    def style(kind):
        return f"castle_{slug}_{kind}"
    # Furnished groups sit inside each wing, leaving the center and stair runs clear.
    for x in (16,66):
        for z in (16,38):
            a,b = (x+ox)*.5, (z+oz)*.5
            box(geom,(a-.35,b-.35,5.025),(4.30,3.82,.034),"tea_tatami",2.0)
            for y in (b-.33,b+3.43):
                box(geom,(a-.34,y,5.045),(4.27,.076,.024),style("accent"),1.2)
            put(TABLE,x+5+ox,z+2+oz,1.0,0.,0.,.065,dx=.25)
            if level==0:
                for i in (0,8):
                    put(CHEST,x+i+ox,z+6+oz,.78,pi/2,0.,.065)
            elif level==1:
                # Layer a folded cover and bolster across the existing raised futon.
                for i in (0,8):
                    xx,zz=(x+i+ox)*.5,(z+6+oz)*.5
                    box(geom,(xx+.05,zz+.68,5.51),(.90,.77,.045),style("accent"),.84)
                    box(geom,(xx+.13,zz+.15,5.52),(.74,.31,.13),style("linen"),.70)
            elif level==2:
                model="castle_kitsuki_archive" if slug=="kitsuki" else CHEST
                put(model,x+3+ox,z+9+oz,1.2,0.,0.,.038)
            elif level==3 and slug=="isawa":
                put("castle_isawa_incense",x+1+ox,z+3+oz,1.12,0.,0.,.045)
            elif level==3 and slug=="bayushi":
                put("castle_bayushi_mask_stand",x+5+ox,z+2+oz,.70,0.,0.,.55,dx=.25)
    # The audience dais stays in its original collision footprint.
    x,z=(38+ox)*.5,(49+oz)*.5
    for dx in (0.26,9.50):
        box(geom,(x+dx,z+1.48,5.56),(.24,.24,1.15),style("wood"))
    box(geom,(x+.28,z+1.56,6.66),(9.48,.10,.13),style("wood"),1.35)
    for dx in (1.05,3.77,6.49):
        box(geom,(x+dx,z+1.62,5.73),(2.38,.10,.92),style("paper"),1.55)
        box(geom,(x+dx,z+1.54,5.73),(2.38,.11,.11),style("accent"),1.20)


def authored_small(mats):
    common = {"paper":("kaiu_shoji.png",.9), "wood":("castle_hida_wood.png",.90),
              "lacquer":("castle_bayushi_accent.png",.86), "steel":("kaiu_stone.png",.55),
              "linen":("castle_hida_linen.png",.93)}
    andon=Geometry()
    box(andon,(-.21,-.20,0),(.42,.40,.046),"wood")
    box(andon,(-.169,-.148,.052),(.338,.296,.34),"paper")
    for x in (-.18,.148):
        for z in (-.158,.13):
            box(andon,(x,z,.036),(.037,.034,.387),"wood")
    box(andon,(-.198,-.175,.411),(.396,.35,.04),"wood")
    export("castle_paper_andon",andon,common)
    scroll=Geometry()
    box(scroll,(-.23,-.14,.00),(.46,.28,.09),"wood")
    for i,z in enumerate((-.122,-.037,.048)):
        box(scroll,(-.215,z,.096),(.43,.075,.065),"linen")
        box(scroll,(-.045+i*.015,z-.005,.150),(.039,.086,.017),"lacquer")
    export("castle_scroll_stack",scroll,common)
    swords=Geometry()
    for x in (-.32,.24):
        box(swords,(x,-.18,0),(.075,.36,.11),"wood")
        box(swords,(x,-.055,.07),(.075,.107,.28),"wood")
    for z,y in ((-.05,.19),(.111,.34)):
        box(swords,(-.38,z,y),(.77,.057,.044),"lacquer")
        box(swords,(.28,z-.025,y-.012),(.021,.105,.075),"steel")
        box(swords,(.32,z+.003,y+.001),(.21,.056,.041),"wood")
    export("castle_sword_rest",swords,common)


def map_row(gm,w,ev,theme,layout,old_map):
    slug = theme[0]
    def style(kind):
        return f"castle_{slug}_{kind}"
    shell = copy(w)
    roofmesh = Geometry()
    inner = isinstance(layout,int)
    roof_removal = fitting_strip(roofmesh,gm,w,slug)
    # Keep stock geometry as collision, while the export draws tailored surfaces over it.
    # Interior table footprints and roof courses get their own fitted models.
    shell.objs = [o for o in w.objs if id(o) not in roof_removal]
    if inner:
        ox,oz = gm.ROOM_OFS[w.mid]
        furniture = {(x+ox+5,z+oz+2,2,gm.DARKWOOD) for x in (16,66) for z in (16,38)}
        if layout==0:
            furniture |= {(x+ox+dx,z+oz+6,1,gm.MATTING) for x in (16,66) for z in (16,38) for dx in (0,8)}
        shell.objs = [o for o in shell.objs if not (o["t"]=="fill" and o["y"]==10 and o["d"]==1 and o["h"]==1
                      and (o["x"],o["z"],o["w"],o["blk"]) in furniture)]
    moves = {}
    marks = set()
    data = {"placements": [], "poolLights": [], "leafDrift": []}
    def put(model,x,z,scale=1.,heading=0.,sway=0.,raise_by=0.,*,y=None,dx=0.):
        if not (0 <= x < w.w and 0 <= z < w.d) or not w.blk[z,x] or (w.blk[z,x]&31)==8:
            return None
        point = [x*.5+.25+dx, ((int(w.hgt[z,x])+1)*.5 if y is None else y)+raise_by, z*.5+.25]
        data["placements"].append([model,*point,scale,heading,*([sway] if sway else [])])
        return point
    for obj in w.objs:
        if obj["t"] != "fb":
            continue
        x,y,z,fb,kind = (obj[k] for k in ("x","y","z","fbtype","fbparam"))
        if fb==2 and kind==gm.LAMP_STREET:
            model=LANTERN
            if (point:=put(model,x,z,.83,0.,y=y*.5)):
                data["poolLights"].append([point[0],point[1]+.68,point[2],3.35,1.04])
        elif fb==20 and kind in (gm.TREE_M,gm.TREE_L,gm.TREE_S,gm.ROCK_M,gm.ROCK_S):
            is_tree=kind in (gm.TREE_M,gm.TREE_L,gm.TREE_S)
            maple=is_tree and slug=="kitsuki" and x%3==0
            pine="castle_snow_pine" if slug in {"hida","akodo"} else MATSU
            model=(MAPLE if maple else pine) if is_tree else ROCK
            scale={gm.TREE_M:1.,gm.TREE_L:1.33,gm.TREE_S:.70,gm.ROCK_M:.76,gm.ROCK_S:.52}[kind]
            if (point:=put(model,x,z,scale,.083*x,.015 if is_tree else 0.,y=y*.5)) and maple:
                data["leafDrift"].extend(falling_leaves(point,scale,x))
        elif obj["t"]=="fb" and (fb,kind)==(3,14):
            model=None
            # Road guidance and automatic exit posts lie close to active portals.
            if all(abs(x-p["pos"][0])>3 or abs(z-p["pos"][2])>3
                   for p in ev.ev.values() if p.get("role")=="portal"):
                put("castle_lacquer_supply_chest",x,z,.71,pi/2,y=y*.5)
                model=CHEST
            if not model:
                continue
        else:
            continue
        marks.add((obj["x"],obj["z"],obj["y"],fb,kind))
    for key,e in old_map["event"].items():
        previous=e.get("mdlid")
        if previous=="CE000":
            source_event=ev.ev.get(key,{})
            if source_event.get("pos")==e.get("pos"):
                previous=source_event.get("mdlid")
        model=DECOR.get(previous)
        if not model or e.get("reqs0") or len(e.get("page",()))!=1:
            continue
        page=e["page"][0]
        if e.get("role")!="custom" or page.get("cmdblock") or page.get("reqs") or page.get("trigger",0)!=0:
            continue
        x,y,z,_=e["pos"]
        if put(model,x,z,y=y*.5):
            moves[key]=[previous,"CE000"]
    if inner:
        interior_features(roofmesh,gm,w,layout,theme,put)
    else:
        yard_features(roofmesh,gm,w,*layout,theme,put)
    # Avoid a duplicate stock torii at the reception; its central opening remains clear.
    if not inner and layout==(1,0):
        gx,gz=gm.PAD_X+43,gm.PAD_BOTTOM+12
        shell.objs=[o for o in shell.objs if not (o["t"]=="fill" and o["z"]==gz and
            gx-1<=o["x"]<=gx+10 and o["blk"] in (gm.TORII,gm.DARKWOOD))]
    tile_style={gm.STONE:style("stone"),gm.STONEW:style("stone"),gm.KAIU:style("stone"),
                gm.WOOD:style("wood") if not inner else style("plaster"),gm.DARKWOOD:style("wood"),
                gm.PLANK:style("floor"),gm.PLASTER:style("plaster"),gm.ROOF:style("roof"),gm.SHOJI:style("paper"),
                gm.TORII:style("accent"),gm.MATTING:style("linen"),gm.TATAMI:"tea_tatami",gm.FUTON:style("linen"),
                gm.SNOW:"highland_snow",gm.GRASS:"cakon_river_grass",gm.GRASS2:"cakon_river_grass",
                gm.GRASS3:"cakon_river_grass",gm.DIRT:"cakon_silt",gm.SAND:style("gravel"),
                gm.WATER:style("stone"),gm.ROAD:style("gravel")}
    shell.objs=[o for o in shell.objs if not (o["t"]=="blk" and (o["blk"]&31)==11)]
    geom=world_mesh(gm,shell,tile_style)
    for k,mat in enumerate(roofmesh.materials):
        geom.quad(roofmesh.vertices[4*k:4*k+4],roofmesh.uvs[k],mat)
    # Water comes from the existing animated texture loop, with original water collision.
    water=Geometry()
    for z,x in np.argwhere(w.blk==gm.WATER):
        y=(int(w.hgt[z,x])+1)*.5+.034
        corners=[(x*.5,z*.5,y),(x*.5+.5,z*.5,y),(x*.5+.5,z*.5+.5,y),(x*.5,z*.5+.5,y)]
        water.quad(corners,[(px/10,pz/10) for px,pz,py in corners],"pond")
    data["terrain"]=f"{w.mid.lower()}_{slug}_castle" + ("_v2" if w.mid=="M573" else "")
    if water.faces:
        data.update(water=data["terrain"]+"_pond",waterSequence={"prefix":WATER,"frames":32,"seconds":17.8})
    return data, geom, water, marks, roof_removal, moves


def main(repo, groups, maps=None):
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    # Generate art from the full shapes, including furnishings hidden by an installed pass.
    gm._CLAN_CASTLE_ART={}
    stage_index={}
    engine=repo/"_tools/rpgcobo-tool/project"
    live=json.loads((engine/"data/map.json").read_bytes())
    live_index=json.loads((engine/"resource/native_environment/index.json").read_bytes())
    sources={}
    specific = {
        "castle_unicorn_saddle": {"iuchi"},
        "castle_bayushi_mask_stand": {"bayushi"},
        "castle_snow_pine": {"hida", "akodo"},
        "castle_lion_makiwara": {"akodo"},
        "castle_isawa_incense": {"isawa"},
        "castle_kitsuki_archive": {"kitsuki"},
    }
    for model,size in MODELS.items():
        if model in specific and not specific[model].intersection(groups):
            continue
        sources[model]=build_diorama_mesh(model,model,size,align_x=model in (CHEST,TABLE,"castle_kitsuki_archive"),
                                         main_component=model in (MATSU,"castle_snow_pine"))
    castle_turf()
    material_sets={theme[0]:material_files(theme) for theme in THEMES.values()
                   if theme[0] in {*groups,"hida","bayushi"}}
    authored_small(material_sets["hida"])
    plans={}
    report={}
    for castle in gm.CLAN_CASTLES:
        theme=THEMES[castle["name"]]
        if theme[0] not in groups:
            continue
        floors={mid:i for i,mid in enumerate(castle["ids"][1:])}
        layouts={mid:p for p,mid in castle["grounds"].items()} | floors
        for mid, layout in layouts.items():
            if maps and mid not in maps:
                continue
            world,events=gm.make(mid)
            add, positions = [], {}
            if mid=="M573":
                door=live[mid]["event"]["#8#"]
                expected=[47,4,45,2]
                assert door["dest"]=={"mapid":"M296","evid":1} and door["pos"] in (expected,[47,4,45,0])
                # Make a recess in the solid frontage, centered on the original portal.
                fill={"t":"fill","x":46,"y":4,"z":46,"w":2,"h":4,"d":2,"blk":gm.VOID}
                if fill not in world.objs:
                    world.objs.append(fill)
                add.append(fill)
                positions["#8#"]=[expected,[47,4,45,0]]
            row, terrain, water, fixtures, roof_ids, event_edits=map_row(gm,world,events,theme,layout,live[mid])
            if positions:
                row["doors"]=[{"event":8,"x":23.0,"y":2.0,"z":22.94}]
            mats=material_sets[theme[0]]
            export(row["terrain"],terrain,mats)
            if water.faces:
                export(row["water"],water,{"pond":(WATER+"00.png",.72)})
            if mid=="M555":
                # The camera and performance script already place the custom Crane stage.
                old=live_index[mid]
                row["placements"]=[p for p in old["placements"] if p[0]=="kabuki_kyuden_deck"]+row["placements"]
                row["poolLights"]=old["poolLights"][:4]+row["poolLights"]
            stage_index[mid]=row
            remove=[obj for obj in world.objs if id(obj) in roof_ids or obj["t"]=="fb" and
                    (obj["x"],obj["z"],obj["y"],obj["fbtype"],obj["fbparam"]) in fixtures]
            if isinstance(layout,int):
                ox,oz=gm.ROOM_OFS[mid]
                furniture={(x+ox+5,z+oz+2,2,gm.DARKWOOD) for x in (16,66) for z in (16,38)}
                if layout==0:
                    furniture |= {(x+ox+dx,z+oz+6,1,gm.MATTING) for x in (16,66) for z in (16,38) for dx in (0,8)}
                remove.extend(o for o in world.objs if o["t"]=="fill" and (o["y"],o["d"],o["h"])==(10,1,1)
                              and (o["x"],o["z"],o["w"],o["blk"]) in furniture)
            elif layout==(1,0):
                gx,gz=gm.PAD_X+43,gm.PAD_BOTTOM+12
                remove.extend(o for o in world.objs if o["t"]=="fill" and o["z"]==gz and
                    gx-1<=o["x"]<=gx+10 and o["blk"] in (gm.TORII,gm.DARKWOOD))
            plans[mid]={"remove":remove,"add":add,"decor":event_edits,"positions":positions,"theme":theme[0]}
            report[mid]={"name":world.name,"places":len(row["placements"]),"quads":len(terrain.faces),
                         "removed":len(remove),"prop_models_replaced":len(event_edits)}
    tag="-".join(groups if not maps else [*groups,*sorted(maps)])
    out=HERE/f"clan-castles-{tag}"
    out.mkdir(exist_ok=True)
    (out/"plans.json").write_text(json.dumps(plans,separators=(",",":")),"utf-8")
    (out/"rows.json").write_text(json.dumps({mid:stage_index[mid] for mid in plans},separators=(",",":")),"utf-8")
    (out/"art-report.json").write_text(json.dumps({"maps":report,"sources":sources},indent=2),"utf-8")
    print(f"CASTLES prepared {len(plans)} maps in {out.name}")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    p.add_argument("themes",nargs="+",choices=[t[0] for t in THEMES.values()])
    p.add_argument('--maps',nargs='+')
    a=p.parse_args()
    main(a.repo.resolve(),a.themes,a.maps)
