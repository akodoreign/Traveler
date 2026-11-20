"""Draw the distinct world-space masks for the initial active spell bank."""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from elemental_marks import engraved
from elemental_profiles import spell_profiles
from school_marks import school_mark
from school_profiles import school_profiles
from support_marks import draw_support_mark
from support_profiles import support_profiles

ROOT = Path(__file__).parent
PROFILES = json.loads((ROOT / "spell_profiles.json").read_text())
PROFILES.update(spell_profiles())
OUT = ROOT / "efx/rt/ability"
COLORS = {
    "water": (46, 171, 255), "lightning": (255, 203, 75), "air": (115, 248, 205),
    "earth": (239, 141, 64), "jade": (113, 255, 97), "void": (164, 124, 255),
    "fire": (255, 103, 47), "ice": (144, 221, 255), "shadow": (195, 95, 180),
    "steel": (143, 194, 239), "wood": (226, 173, 101), "shade": (207, 116, 206),
}


def arc(draw, box, start, end, width=4):
    draw.arc(box, start, end, fill=255, width=width)


def star(draw, x, y, width, height):
    draw.polygon([(x-width,y),(x-2,y-2),(x,y-height),(x+2,y-2),
                  (x+width,y),(x+2,y+2),(x,y+height),(x-2,y+2)], fill=255)


def draw_shape(shape):
    mask = Image.new("L", (128, 128))
    draw = ImageDraw.Draw(mask)
    if shape == "petals":
        for i in range(7):
            a = i * math.tau / 7
            x,y = 64+32*math.cos(a),64+32*math.sin(a)
            draw.ellipse((x-6,y-9,x+6,y+9),outline=255,width=3)
        star(draw,64,64,15,20)
    elif shape == "ribbon":
        for phase in (0, 1.9):
            points = [(x,64+22*math.sin((x-16)/16+phase)) for x in range(16,112)]
            draw.line(points,fill=255,width=4)
        star(draw,98,54,11,15)
    elif shape == "fork":
        draw.line([(82,13),(50,53),(69,55),(30,112)],fill=255,width=7)
        draw.line([(61,43),(32,51),(22,74)],fill=255,width=3)
        draw.line([(58,71),(82,79),(100,70)],fill=255,width=4)
        draw.line([(50,93),(61,104),(77,109)],fill=255,width=2)
    elif shape == "crescents":
        for i in range(3):
            arc(draw,(15+i*14,21+i*8,91+i*11,107-i*6),243,129,4-i//2)
        star(draw,103,75,9,9)
    elif shape == "plates":
        for x,y,s in [(31,79,18),(63,52,21),(96,79,18)]:
            draw.polygon([(x-s,y),(x-s//3,y-s),(x+s//2,y-s),(x+s,y-2),(x+s//3,y+11),(x-s//2,y+9)],outline=255,width=4)
            draw.line([(x-s//3,y-s),(x,y-3),(x+s,y-2)],fill=255,width=2)
    elif shape == "eclipse":
        arc(draw,(20,20,108,108),188,550,4)
        arc(draw,(33,20,106,92),-58,142,3)
        star(draw,98,36,11,15)
        star(draw,31,88,7,11)
    elif shape == "drops":
        for x,y,s in [(34,69,10),(62,43,13),(91,78,13)]:
            draw.polygon([(x,y-2*s),(x+s,y),(x+s//2,y+s),(x-s//2,y+s),(x-s,y)],outline=255,width=3)
            star(draw,x,y,3,s//2)
    elif shape == "spiral":
        points = []
        for i in range(150):
            a = i*.091
            radius = i*.33
            points.append((64+radius*math.cos(a),64+radius*.77*math.sin(a)))
        draw.line(points,fill=255,width=4)
        for x,y in [(25,89),(97,29),(99,87)]:
            star(draw,x,y,7,9)
    elif shape == "feathers":
        for x,y in [(38,73),(67,50),(87,81)]:
            arc(draw,(x-18,y-25,x+20,y+22),202,358)
            arc(draw,(x-7,y-24,x+21,y+17),3,158,2)
            draw.line([(x-13,y+22),(x+10,y-16)], fill=255,width=2)
    elif shape == "shards":
        for x,y,s in [(34,75,11),(64,55,21),(93,73,14)]:
            draw.polygon([(x,y-s*2),(x+s,y-5),(x,y+s),(x-s,y-3)],outline=255,width=4)
            draw.line([(x,y-s*2),(x+1,y+s)],fill=255,width=2)
    elif shape == "stitch":
        draw.line([(18,81),(110,47)],fill=255,width=4)
        for i in range(5):
            x,y=29+i*16,77-i*6
            draw.line([(x-5,y-9),(x+5,y+9)],fill=255,width=3)
        star(draw,106,50,10,15)
    elif shape == "halo":
        for i in (0,7,14):
            arc(draw,(14+i,42+i//2,114-i,86-i//2),0,359,2)
        draw.line([(24,49),(104,49)],fill=255,width=4)
        star(draw,64,49,9,16)
    else:
        return engraved(shape)
    return mask


def save_particle(identifier, mask, color):
    glow = mask.filter(ImageFilter.GaussianBlur(6)).point(lambda value: min(255,value*3))
    background = Image.new("RGBA",mask.size,(*color,0))
    background.putalpha(glow)
    edge = Image.new("RGBA",mask.size,(*color,0))
    edge.putalpha(mask.filter(ImageFilter.MaxFilter(5)).point(lambda value: min(255,int(value*.87))))
    white = Image.new("RGBA",mask.size,(244,251,255,0))
    white.putalpha(mask)
    background.alpha_composite(edge)
    background.alpha_composite(white)
    background.save(OUT / (identifier + ".png"))
    (OUT / (identifier + ".ptd")).write_text(
        """// Camera-facing mark, positioned by the active ability choreography.
parentcoord <- false
currentgroup <- 0
prof <- {}
groups <- [
    with ParticleGroupData(){
        name = "%s"
        enabled = true
        aimtype = 1
        localcoord = true
        emitter = with ParticleEmitter(){
            num = 1
            start = 0, start_spr = 0
            life = 1100, life_spr = 0
        },
        shapetype = 0
        shapedata = {"axis":0,"r":0.0,"w":0.92,"h":0.92}
        texture = "/resource/efx/rt/ability/%s.png"
        color = 0xffffffff
        blendmode = 5
        blend = 1
        Ka = 0xffffffff
        Ks = 0
        mod = [
            {"classid":"ptcmod_color","color":[-1,-1,-41,-243]},
        ]
    },
]
actions <- [{"acttype":"emitall","time":0}]
""" % (identifier, identifier), encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for ability, profile in PROFILES.items():
        save_particle(ability, draw_shape(profile["shape"]), COLORS[profile["element"]])
    for ability, profile in school_profiles().items():
        try:
            mark = school_mark(profile["shape"])
        except ValueError:
            mark = draw_shape(profile["shape"])
        save_particle(ability, mark, COLORS[profile["element"]])
    for ability, profile in support_profiles().items():
        save_particle(ability, draw_support_mark(profile["shape"]), COLORS[profile["element"]])
    void = Image.new("L",(128,128))
    brush = ImageDraw.Draw(void)
    arc(brush,(12,12,116,116),11,166,4)
    arc(brush,(12,12,116,116),191,346,4)
    for x,y in [(21,64),(64,21),(107,64),(64,107)]:
        star(brush,x,y,11,15)
    save_particle("void_echo",void,(211,126,255))

