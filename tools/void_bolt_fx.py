"""Draw the original animated particles for Haruki's Void Bolt."""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 96
AA = 4
FRAMES = 8
INK = (28, 16, 55, 255)
IRIS = (71, 35, 135, 255)
BLUE = (92, 167, 255, 255)
LAVENDER = (171, 129, 248, 255)
WHITE = (242, 239, 255, 255)


def scaled(points):
    return [(round(x*AA), round(y*AA)) for x, y in points]


def line(draw, points, fill, width):
    draw.line(scaled(points), fill=fill, width=round(width*AA), joint="curve")


def arc(cx, cy, radius_x, radius_y, tilt, start, end):
    sn, cs = math.sin(tilt), math.cos(tilt)
    points = []
    for i in range(45):
        a = start + (end-start)*i/44
        x, y = radius_x*math.cos(a), radius_y*math.sin(a)
        points.append((cx + cs*x - sn*y, cy + sn*x + cs*y))
    return points


def core(draw, index):
    t = math.tau * index / FRAMES
    # Front and back arcs are separated by the ink-dark core.
    a = arc(48, 48, 38, 19, -.52+.32*math.sin(t), math.pi, math.tau)
    line(draw, a, IRIS, 5.8)
    line(draw, a, LAVENDER, 3.0)
    b = arc(48, 48, 32, 12, .65+.28*math.cos(t), math.pi, math.tau)
    line(draw, b, BLUE, 3.3)
    points = [(48,22), (67,33), (74,48), (66,64), (48,73), (29,64), (22,48), (32,31)]
    draw.polygon(scaled(points), fill=INK)
    line(draw, [*points, points[0]], IRIS, 4.6)
    line(draw, [(31,51),(32,33),(48,24),(65,34)], LAVENDER, 2.2)
    line(draw, [(39,44),(47,33),(48,50),(56,47),(51,61)], WHITE, 2.8)
    for radii, tilt, shade in (((38,19), -.52+.32*math.sin(t), LAVENDER),
                              ((32,12), .65+.28*math.cos(t), BLUE)):
        arc_line = arc(48, 48, *radii, tilt, .25, math.pi-.11)
        line(draw, arc_line, IRIS, 6.0)
        line(draw, arc_line, shade, 3.3)
        line(draw, arc_line[9:30], WHITE, 1.25)


def wake(draw, index):
    wobble = math.sin(math.tau*index/FRAMES)
    mark = [(9,47),(26,44+wobble*7),(48,42),(67,36-wobble*6),
            (85,47),(67,58),(50,54),(24,51+wobble*4)]
    draw.polygon(scaled(mark), fill=INK)
    line(draw, [(14,47),(41,47+wobble*4),(66,43),(82,47)], LAVENDER, 4.6)
    line(draw, [(53,45),(68,44),(79,47)], WHITE, 2.7)


def impact(draw, index):
    u = index/(FRAMES-1)
    radius = 15+30*(1-(1-u)**2)
    for j in range(4):
        angle = math.tau*j/4 + u*.35
        a = arc(48,48,radius,radius*.76,-.22,angle+.065,angle+1.05)
        line(draw, a, IRIS, 5.5 - 2*u)
        line(draw, a, LAVENDER if j % 2 else BLUE, 3.4-1.4*u)
        line(draw, a[11:28], WHITE, 1.4)
        v, w = math.cos(angle), math.sin(angle)
        tip = [(48+(radius+2)*v,48+(radius+2)*w),
               (48+(radius+7)*v,48+(radius+7)*w)]
        line(draw, tip, LAVENDER, 2.5)
    centre = [(48,30+u*13),(59-u*5,48),(48,64-u*11),(37+u*5,48)]
    draw.polygon(scaled(centre), fill=INK)
    line(draw, [*centre, centre[0]], WHITE, 2.0)


def build_strip(path, draw):
    sheet = Image.new("RGBA", (SIZE*FRAMES, SIZE))
    for i in range(FRAMES):
        source = Image.new("RGBA", (SIZE*AA,SIZE*AA))
        draw(ImageDraw.Draw(source), i)
        sheet.paste(source.resize((SIZE,SIZE), Image.Resampling.LANCZOS), (i*SIZE, 0))
    sheet.save(path)


def particle(path, name, life, width, height, opacity):
    shape = f'{{"axis":0,"r":0.0,"w":{width:.2f},"h":{height:.2f}}}'
    color_steps = ",".join(str(-256+value) for value in opacity)
    source = f'''// Native camera-facing Void Bolt mark with tracked world position.
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
            {{"classid":"ptcmod_texanime","frame":[0,{FRAMES}]}},
            {{"classid":"ptcmod_color","color":[{color_steps}]}},
        ]
    }},
]
actions <- [{{"acttype":"emitall","time":0}}]
'''
    path.write_text(source, encoding="utf-8")


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    specs = (
        ("void_bolt_core", core, 950, .69, .69, (255,255,255,245)),
        ("void_bolt_wake", wake, 166, .53, .42, (213,175,103,0)),
        ("void_bolt_impact", impact, 570, 1.23, 1.18, (255,255,203,0)),
    )
    for name, draw, life, width, height, opacity in specs:
        build_strip(output / f"{name}.png", draw)
        particle(output / f"{name}.ptd", name, life, width, height, opacity)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
