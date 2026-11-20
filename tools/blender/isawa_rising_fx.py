"""Native visual linework for the Isawa rising aura."""
import math
from pathlib import Path
import sys

from hero_signature_fx import AMETHYST, CREAM, ICE, INK, VIOLET, ellipse, path, pixels, render, subtrail


def rising(draw, index):
    p = min(1.0, .31+.20*index)
    rad = index*.019
    a = ellipse(63,64,48,25,-.42+rad,-2.24,2.55)
    b = ellipse(63,66,39,20,-.42+rad,-1.98,2.36)
    for strip, width in ((a,7.4),(b,4.6)):
        visible = subtrail(strip,p)
        path(draw,visible,AMETHYST,width)
        path(draw,visible,VIOLET,width*.61)
        path(draw,visible,ICE,width*.25)
    x,y = a[max(1,int((len(a)-1)*p))]
    diamond=[(x,y-5),(x+4,y),(x,y+5),(x-4,y)]
    draw.polygon(pixels(diamond),fill=AMETHYST)
    path(draw,[*diamond, diamond[0]],CREAM,1.5)


def sigil(draw, index):
    p = min(1,.30+.18*index)
    for radius, thickness in ((52,7),(43,3.4)):
        a=ellipse(64,69,radius,radius*.32,0.,-.30,math.tau-.30)
        a=subtrail(a,p)
        path(draw,a,AMETHYST,thickness+3)
        path(draw,a,VIOLET,thickness)
        path(draw,a,ICE,thickness*.45)
    for i in range(5):
        phi=math.tau*i/5+math.pi*.16
        if i/5. > p:
            break
        x,y = 64+38*math.cos(phi), 69+38*.32*math.sin(phi)
        mark=[(x,y-4),(x+5,y),(x,y+4),(x-5,y)]
        path(draw,[*mark,mark[0]],CREAM,2.1)


if __name__ == "__main__":
    dest = Path(sys.argv[1])
    render(dest,"hero_isawa_rising",rising,990,1.65,.78,(255,255,255,181,0))
    render(dest,"hero_isawa_seal",sigil,1030,1.88,.63,(240,255,244,130,0))
