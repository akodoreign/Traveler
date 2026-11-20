"""Draw Mitsue's original short-edged night trails."""
from pathlib import Path
import sys

from hero_signature_fx import AMETHYST, CREAM, VIOLET, ellipse, path, render, subtrail


def trace(draw, index):
    w=min(1.,.26+.19*index)
    for i in range(3):
        casing = ellipse(64,65,48+5*i,15+5*i,-.43,-2.9,-.10)
        visible = subtrail(casing,w-.10*i)
        path(draw,visible,AMETHYST,8.5-2*i)
        path(draw,visible,VIOLET,5.3-i)
        path(draw,visible,CREAM,1.7)
    for i in range(min(3,index+1)):
        x,y = (77+8*i,52-6*i)
        path(draw,[(x-3,y+4),(x+4,y-4)],CREAM,2.0)


if __name__=="__main__":
    dest=Path(sys.argv[1])
    render(dest,"hero_shosuro_trace",trace,245,1.05,.70,(255,230,153,0))
