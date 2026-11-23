"""Author four interchangeable sets for the Crane rehearsal stage."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE = Path(__file__).resolve().parent
TEX = STAGE/"tex"
SCREEN_HEIGHT = 6.35
MATS = {
    "cypress": ("kabuki_cypress.png",.82),
    "frame": ("tea_rail.png",.92),
    "lacquer": ("kabuki_lacquer.png",.49),
    "gold": ("kabuki_gold.png",.62),
    "paper": ("tea_shoji.png",.92),
    "russet": ("kabuki_russet.png",.93),
    "green": ("kabuki_green.png",.92),
    "night": ("kabuki_night.png",.92),
    "mat": ("tea_tatami.png",.95),
    "jade": ("kabuki_jade.png",.66),
    "mirror": ("kabuki_bronze_mirror.png",.76),
    **{act:(f"kabuki_{act}_paint.png",.94) for act in ("komatsu","mirror_flat","blade","title")},
}


def materials():
    wood = Image.open(TEX/"storehouse_board.png").convert("RGB")
    texture = periodic(wood,512)
    gray = texture@[.26,.61,.13]
    contrast = (gray-np.median(gray))/max(1.,np.ptp(np.percentile(gray,[6,95])))
    contrast = np.clip(contrast,-.71,.71)
    for key,tint,factor in (
        ("cypress",(155,117,80),.66),("lacquer",(63,28,26),.55),
        ("gold",(185,125,45),.51),("russet",(111,54,39),.48),
        ("green",(45,70,55),.51),("night",(37,48,65),.50),("jade",(76,133,103),.62),
    ):
        rgb = np.asarray(tint)*(1+contrast[...,None]*factor)
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(TEX/f"kabuki_{key}.png")
    for key in ("komatsu","mirror_flat","blade","title"):
        input_name = "mirror" if key=="mirror_flat" else key
        im = Image.open(HERE/"surface_sources"/f"kabuki_{input_name}_paint.png").convert("RGB")
        width,height = im.size
        strip = im.crop((0,int(height*.16),width,int(height*.84)))
        strip.resize((1536,768),Image.Resampling.LANCZOS).save(TEX/f"kabuki_{key}_paint.png")


def permanent_stage():
    g = Geometry()
    # The native top sits just above the existing navigable deck.
    for i in range(54):
        x = -9.17+i*.341
        seam = -.19+.38*np.sin(i*1.31)
        for z,far in ((-2.03,seam),(seam+.014,2.96)):
            box(g,(x,z,.011),(.329,far-z,.052),"cypress",1.64)
    box(g,(-9.32,-2.10,-.49),(18.67,.18,.54),"frame",1.32)
    box(g,(-9.33,-2.174,-.081),(18.68,.243,.133),"cypress",1.42)
    for x in np.linspace(-8.87,8.84,15):
        box(g,(x,-2.201,-.46),(.18,.13,.36),"lacquer",.71)
    # Audience-left hanamichi and center entrance steps.
    bridge_x = -7.52
    for i in range(23):
        z = -8.57+i*.286
        box(g,(bridge_x,z,.009),(1.51,.275,.054),"cypress",1.42)
    for offset in (0,1.51):
        box(g,(bridge_x+offset,-8.58,-.11),(.093,6.64,.17),"frame",1.00)
    for i,(base,depth) in enumerate(((-.49,.31),(-.36,.33),(-.23,.34))):
        box(g,(-1.03,-3.065+.30*i,base),(2.06,depth,.12),"frame",.68)
        box(g,(-1.04,-3.080+.30*i,base+.108),(2.08,depth+.027,.047),"cypress",.82)
    # Replace the visible face of the fixed striped backdrop and keep its backstage footprint.
    colors = ("night","russet","green")
    for i in range(42):
        x = -9.01+i*.43
        z = 2.77+.066*math.sin(i*2.17)
        box(g,(x,z,.062),(.438,.14,3.38),colors[(i//4)%3],.91)
    box(g,(-9.28,2.741,3.39),(18.53,.23,.17),"frame",1.39)
    for x in (-9.23,9.06):
        box(g,(x,2.53,-.05),(.18,.30,3.49),"frame",1.12)
    for x in (-8.85,8.67):
        box(g,(x,-1.69,.04),(.19,.17,1.48),"frame",.74)
        box(g,(x-.10,-1.81,1.42),(.40,.42,.55),"paper",.73)
        for y in (1.42,1.95):
            box(g,(x-.146,-1.85,y),(.49,.49,.07),"lacquer",.72)
    export("kabuki_kyuden_deck",g,MATS)


def change_screen():
    g = Geometry()
    for i in range(6):
        x = -4.55+i*1.516
        # Centered opaque panels hide the set while leaving their wood frames visible.
        box(g,(x,-.049,.104),(1.517,.098,4.258),"paper",1.02)
        box(g,(x+.018,-.105,.08),(.069,.21,4.29),"lacquer",.87)
        box(g,(x+1.426,-.105,.08),(.072,.21,4.29),"lacquer",.87)
        box(g,(x,-.111,.06),(1.515,.23,.10),"frame",.87)
        box(g,(x,-.111,4.33),(1.515,.23,.12),"frame",.87)
        for y in (.87,3.05):
            box(g,(x+.061,-.113,y),(1.39,.15,.06),"gold",.81)
        for j in range(1,4):
            box(g,(x+.362*j,-.100,.135),(.027,.11,4.15),"frame",.90)
        for foot in (.24,1.26):
            box(g,(x+foot-.045,-.277,0.),(.095,.55,.074),"frame",.62)
    g.vertices = [(x,z,y*(SCREEN_HEIGHT/4.45)) for x,z,y in g.vertices]
    export("kabuki_screen_panel",g,MATS)


def set_flat(g,paint,left=-8.24,width=16.48):
    low,high,z = .061,3.14,2.565
    edge = left+width
    g.quad([(left,z,low),(edge,z,low),(edge,z,high),(left,z,high)],
           [(0.,0.),(1.,0.),(1.,1.),(0.,1.)],paint)
    for x in np.linspace(left,edge,9):
        box(g,(x-.044,z-.055,low),(.088,.127,high-low),"frame",.96)
    for y in (low,high-.066):
        box(g,(left-.075,z-.059,y),(width+.15,.145,.108),"frame",.85)


def court(g):
    set_flat(g,"komatsu")
    for x in (-6.4,6.2):
        box(g,(x,1.77,.06),(.194,.22,2.92),"lacquer",1.07)
        for y in (.19,.38,2.68,2.86):
            box(g,(x-.046,1.72,y),(.292,.315,.07),"gold",.81)
    # Low seat and arms behind the Lord’s mark. The guard's paths stay clear.
    box(g,(3.60,1.23,.042),(2.05,1.04,.103),"lacquer",.93)
    box(g,(3.71,1.37,.144),(1.83,.83,.053),"gold",.82)
    for x in (3.83,5.27):
        box(g,(x,1.46,.189),(.111,.62,.32),"lacquer",.76)
    box(g,(3.86,2.045,.181),(1.48,.11,.86),"lacquer",.76)
    box(g,(3.88,2.008,.87),(1.44,.14,.061),"gold",.77)
    for x in (-4.44,-2.75,2.48):
        box(g,(x,1.79,.061),(1.16,.64,.043),"mat",.83)


def mirror(g,mesh):
    set_flat(g,"mirror_flat")
    for i,face in enumerate(mesh.faces):
        points = [(x+1.70,z+1.11,y+.061) for x,z,y in (mesh.vertices[j] for j in face)]
        g.quad(points,mesh.uvs[i],"mirror")
    for x,z in ((2.86,1.67),(3.65,1.65)):
        box(g,(x,z,.069),(.51,.38,.08),"lacquer",.78)
        box(g,(x+.153,z+.097,.148),(.19,.18,.075),"jade",.65)
        box(g,(x+.193,z+.136,.218),(.12,.10,.045),"jade",.62)
    for x in (-5.28,5.52):
        box(g,(x,1.74,.067),(1.12,.69,.038),"mat",.76)


def moon_lantern(g,x,z):
    box(g,(x-.03,z-.03,.04),(.10,.11,1.21),"frame",.83)
    box(g,(x-.147,z-.16,1.22),(.33,.34,.46),"paper",.82)
    for y in (1.22,1.65):
        box(g,(x-.189,z-.196,y),(.41,.41,.061),"night",.71)


def confrontation(g):
    set_flat(g,"blade")
    for x in (-7.45,7.29):
        moon_lantern(g,x,1.58)
    for x in (-7.82,6.47):
        for offset in (.0,.72,1.44):
            box(g,(x+offset,2.285,.061),(.079,.108,1.98),"night",.74)
        for y in (.151,1.13,2.008):
            box(g,(x,2.29,y),(1.54,.101,.069),"lacquer",.90)


def ending(g):
    set_flat(g,"title")
    for x in (-7.38,7.21):
        box(g,(x,2.10,.065),(.15,.14,2.51),"lacquer",.83)
        box(g,(x-.27,2.12,1.49),(.68,.084,.84),"russet",.93)
        box(g,(x-.29,2.08,2.30),(.72,.16,.10),"gold",.78)
    for x in (-4.28,3.58):
        box(g,(x,1.68,.063),(1.32,.73,.04),"mat",.88)
    # A low gold-edged palace frame marks the Empress’s rear entrance.
    for x in (-1.10,1.02):
        box(g,(x,2.26,.063),(.12,.16,2.35),"lacquer",1.02)
    box(g,(-1.22,2.24,2.29),(2.45,.19,.15),"gold",.91)


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import voxfile

    materials()
    permanent_stage()
    change_screen()
    source = save(*convert_prop("kabuki_bronze_mirror",(.86,.48,1.47),42,lower=.025),voxfile)
    prop_mesh = voxel_asset("kabuki_bronze_mirror")
    for name,builder in (("komatsu",court),("mirror",lambda g:mirror(g,prop_mesh)),
                         ("blade",confrontation),("title",ending)):
        g = Geometry()
        builder(g)
        export("kabuki_act_"+name,g,MATS)
    (HERE/"kabuki-set-layout.json").write_text(json.dumps({
        "map":"M555","mark":[48,55],"stage_relative_origin":[37.25,2.5,29.75],
        "screen_width":9.10,"screen_height":SCREEN_HEIGHT,"screen_travel":[13.8,4.5],
        "mirror_source":source,
    },indent=2),encoding="utf8")


if __name__=="__main__":
    main()
