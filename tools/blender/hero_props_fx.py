"""Draw Gendo's evidence glint and the original remedy steam linework."""
import math
from pathlib import Path
import sys

from hero_signature_fx import CREAM, ellipse, path, pixels, render, subtrail


INK=(61,32,33,255)
AMBER=(213,126,48,255)
BLUE=(150,218,220,255)
FOLIAGE=(45,108,85,255)
GREEN=(149,216,139,255)


def evidence(draw, index):
    x = 64
    u = min(1.,index*.21 + .23)
    guides = [ellipse(x,63,39,26,-.13,-1.64,2.43),
              ellipse(x,63,38,28,-.13,1.46,4.67)]
    for track in guides:
        line = subtrail(track,u)
        path(draw,line,INK,9)
        path(draw,line,AMBER,5.6)
        path(draw,line,CREAM,2.05)
    pupil = [(x,44),(x+15,62),(x,80),(x-16,63)]
    draw.polygon(pixels(pupil),fill=INK)
    path(draw,[*pupil,pupil[0]],AMBER,3.2)
    path(draw,[(x-6,61),(x-2,54),(x+5,57)],CREAM,2.4)
    for i,(a,b) in enumerate(((40,35),(87,38),(27,74),(99,72))):
        if index >= i:
            path(draw,[(a,b-5),(a,b+5)],CREAM,2.2)
            path(draw,[(a-5,b),(a+5,b)],AMBER,2.0)


def remedy(draw,index):
    t=min(1.,.30+.145*index)
    for n in range(3):
        a=29+n*23
        trace=[(a+9*math.sin(i*.53+n*.5+index*.12),90-5*i) for i in range(13)]
        trace=subtrail(trace,t)
        path(draw,trace,FOLIAGE,8)
        path(draw,trace,GREEN,4.7)
        path(draw,trace,BLUE if n==1 else CREAM,2.0)
    leaves=[(22,58),(99,62),(46,39),(75,35),(58,71),(87,47)]
    for i,(x,y) in enumerate(leaves):
        if index >= i:
            points=[(x-5,y-2),(x+1,y-4),(x+7,y),(x+1,y+4)]
            draw.polygon(pixels(points),fill=GREEN if i%2 else FOLIAGE)


if __name__ == "__main__":
    dest=Path(sys.argv[1])
    render(dest,"hero_gendo_evidence",evidence,810,1.16,.89,(255,255,237,0))
    render(dest,"hero_sayo_steam",remedy,870,.91,1.16,(225,255,186,0))
