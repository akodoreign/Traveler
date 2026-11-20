"""Draw native signatures from original linework in camera-facing particle strips."""
from argparse import ArgumentParser
import math
from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 128
AA = 3
FRAMES = 12
INK = (80, 28, 18, 255)
COPPER = (217, 86, 35, 255)
GOLD = (255, 195, 70, 255)
CREAM = (255, 248, 209, 255)
AMETHYST = (82, 55, 153, 255)
VIOLET = (168, 126, 245, 255)
ICE = (164, 218, 255, 255)


def pixels(points):
    return [(round(x * AA), round(y * AA)) for x, y in points]


def path(draw, points, color, width):
    if len(points) < 2:
        return
    pts = pixels(points)
    draw.line(pts, fill=color, width=max(1, round(width * AA)), joint="curve")
    radius = width * AA * .5
    for x, y in (pts[0], pts[-1]):
        draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill=color)


def subtrail(points, t):
    if t <= 0:
        return []
    if t >= 1:
        return points
    i = (len(points)-1)*t
    j = int(i)
    x,y = points[j]
    u,v = points[j+1]
    return [*points[:j+1], (x+(u-x)*(i-j),y+(v-y)*(i-j))]


def ellipse(cx, cy, rx, ry, angle, start, stop, steps=56):
    points = []
    sn, cs = math.sin(angle), math.cos(angle)
    for i in range(steps + 1):
        t = start + (stop-start)*i/steps
        x,y = rx*math.cos(t), ry*math.sin(t)
        points.append((cx+x*cs-y*sn,cy+x*sn+y*cs))
    return points


# The authored paths follow the proportions and join positions of the supplied reference.
YU = [
    [(32,19),(48,17),(65,14),(80,12),(88,15),(77,20),(69,24),(64,28)],
    [(51,25),(54,27),(61,30),(67,34)],
    [(33,38),(37,44),(40,57),(43,68)],
    [(36,40),(57,38),(76,36),(87,34),(94,37),(91,47),(86,62),(83,65)],
    [(61,38),(62,49),(63,61),(64,71)],
    [(46,54),(59,52),(69,49),(81,48)],
    [(43,68),(61,65),(78,62),(83,64)],
    [(33,81),(49,78),(67,75),(84,71),(92,76),(89,85),(85,96),(80,107),(76,113),(67,109),(62,100)],
    [(63,64),(62,75),(58,86),(50,94),(40,107),(26,114)],
]
YU_WEIGHTS = (1.12,.68,1.0,1.23,1.09,.79,.84,1.21,1.12)


def yu(draw, i):
    total = min(9, .48 + 2.22 * i)
    for index, stroke in enumerate(YU):
        track = subtrail(stroke, total-index)
        if not track:
            continue
        weight = YU_WEIGHTS[index]
        path(draw, track, INK, 9.6*weight)
        path(draw, track, COPPER, 7.5*weight)
        path(draw, track, GOLD, 4.9*weight)
        path(draw, track, CREAM, 2.2*weight)
        if index == int(total):
            x,y = track[-1]
            draw.ellipse((int((x-3)*AA),int((y-3)*AA),int((x+3)*AA),int((y+3)*AA)), fill=CREAM)

def lion_arc(draw, i):
    f = min(1, .24 + i*.18)
    arc = ellipse(55, 66, 48, 32, -.80, math.radians(-32), math.radians(-247), 64)
    arc = subtrail(arc, f)
    path(draw, arc, INK, 15.0)
    path(draw, arc, COPPER, 11.0)
    path(draw, arc, GOLD, 6.7)
    path(draw, arc, CREAM, 2.5)
    follow = subtrail(ellipse(62, 66, 53, 36, -.80, math.radians(-44), math.radians(-242)), f-.11)
    path(draw, follow, COPPER, 3.6)
    path(draw, follow, GOLD, 1.6)


def strip(path_, draw, frames):
    sheet = Image.new("RGBA", (SIZE*frames,SIZE))
    for index in range(frames):
        im = Image.new("RGBA", (SIZE*AA,SIZE*AA))
        draw(ImageDraw.Draw(im),index)
        sheet.paste(im.resize((SIZE,SIZE),Image.Resampling.LANCZOS),(index*SIZE,0))
    sheet.save(path_)


def particle(out, name, life, width, height, opacities, frames):
    shape = f'{{"axis":0,"r":0.0,"w":{width:.2f},"h":{height:.2f}}}'
    alpha = ",".join(str(-256+a) for a in opacities)
    (out / f"{name}.ptd").write_text(f'''// Original school signature linework.
parentcoord <- false
currentgroup <- 0
prof <- {{}}
groups <- [
    with ParticleGroupData(){{
        name = "{name}"
        enabled = true
        aimtype = 1
        localcoord = true
        emitter = with ParticleEmitter(){{
            num = 1
            start = 0, start_spr = 0
            life = {life}, life_spr = 0
        }},
        shapetype = 0
        shapedata = {shape}
        texture = "/resource/efx/rt/{name}.png"
        color = 0xffffffff
        blendmode = 5
        blend = 1
        Ka = 0xffffffff
        Ks = 0
        mod = [
            {{"classid":"ptcmod_texanime","frame":[0,{frames}]}},
            {{"classid":"ptcmod_color","color":[{alpha}]}},
        ]
    }},
]
actions <- [{{"acttype":"emitall","time":0}}]
''',encoding="utf-8")


def render(out, name, art, life, width, height, opacity, frames=FRAMES):
    strip(out/f"{name}.png",art,frames)
    particle(out,name,life,width,height,opacity,frames)


if __name__ == "__main__":
    a = ArgumentParser(description=__doc__)
    a.add_argument("output",type=Path)
    p = a.parse_args().output
    p.mkdir(parents=True,exist_ok=True)
    render(p,"hero_lion_courage",yu,1380,1.82,1.82,(255,255,255,255,255,0),24)
    render(p,"hero_lion_upswing",lion_arc,380,2.02,2.02,(255,240,174,0))
