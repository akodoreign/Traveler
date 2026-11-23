"""Build continuous narrow-gauge tracks and the visible turnout stands."""
from math import ceil
from pathlib import Path
import sys

import numpy as np

from build_cakon_paddy_hut import cane
from build_hoshi_stall import box

MINE_ROUTES=(
    ((24.8,7.1),(32.,7.37),(42.,6.85),(48.,8.23),(53.8,8.95),
     (59.2,9.95),(64.1,9.05),(68.05,7.05)),
    ((42.,6.85),(43.30,6.95),(44.10,8.48),(43.89,10.72),(43.56,12.99),
     (43.70,16.0),(45.44,18.79),(48.8,20.25),(54.,20.34),(59.1,19.55),
     (64.5,19.56),(69.45,19.11),(74.6,17.8)),
    ((53.8,8.95),(55.16,9.43),(55.55,11.87),(55.47,14.31),(56.92,16.7),
     (58.15,18.12),(59.1,19.55)),
)
MINE_STANDS=((41.72,5.79),(54.25,7.82),(59.23,20.89))
ARENA_ROUTES=(
    ((18.9,41.14),(25.0,41.22),(33.3,41.18),(39.35,41.2),(45.91,41.09),(49.12,40.99)),
    ((33.3,41.18),(34.1,41.14),(35.8,40.36),(38.05,39.85),(42.25,39.99)),
)
ARENA_STANDS=((33.32,42.24),)


def curve(points):
    anchors=np.array(points,dtype=float)
    extended=np.vstack((anchors[0],anchors,anchors[-1]))
    samples=[]
    for a,b,c,d in zip(extended,extended[1:],extended[2:],extended[3:]):
        length=np.linalg.norm(c-b)
        t=np.linspace(0.,1.,max(2,ceil(length/.12)),endpoint=False)[:,None]
        piece=.5*((2.*b)+(-a+c)*t+(2.*a-5.*b+4.*c-d)*t*t+(-a+3.*b-3.*c+d)*t*t*t)
        samples.extend(piece)
    samples.append(anchors[-1])
    return np.asarray(samples)


def spread(points):
    direction=np.gradient(points,axis=0)
    direction/=np.linalg.norm(direction,axis=1,keepdims=True)
    return direction,np.column_stack((-direction[:,1],direction[:,0]))


def geometry_box(geom,center,direction,width,length,grade,height,material):
    side=np.array([-direction[1],direction[0]])
    left=center-direction*length*.5
    right=center+direction*length*.5
    corners=[left-side*width*.5,right-side*width*.5,right+side*width*.5,left+side*width*.5]
    top=[(*p,grade+height) for p in corners]
    bottom=[(*p,grade) for p in corners]
    uv=[(0,0),(1,0),(1,1),(0,1)]
    geom.quad(top,uv,material)
    for i in range(4):
        j=(i+1)%4
        geom.quad([bottom[i],bottom[j],top[j],top[i]],uv,material)


def rails(geom,points,grade,wood,iron):
    direction,side=spread(points)
    uv=[(0,0),(1,0),(1,1),(0,1)]
    distance=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    for n in np.unique(np.searchsorted(distance,np.arange(.07,distance[-1],.31))):
        geometry_box(geom,points[n],direction[n],.96,.118,grade+.022,.073,wood)
    for gauge in (-.302,.302):
        left=points+side*(gauge-.027)
        right=points+side*(gauge+.027)
        for i in range(len(points)-1):
            deck=.153+grade
            a,b,c,d=left[i],left[i+1],right[i+1],right[i]
            geom.quad([(*a,deck),(*b,deck),(*c,deck),(*d,deck)],uv,iron)
            geom.quad([(*a,deck-.066),(*b,deck-.066),(*b,deck),(*a,deck)],uv,iron)
            geom.quad([(*d,deck),(*c,deck),(*c,deck-.066),(*d,deck-.066)],uv,iron)
    return direction


def switch_stand(geom,x,z,grade,wood,iron,gold,red):
    box(geom,(x-.28,z-.20,grade),(.54,.39,.11),wood)
    box(geom,(x-.099,z-.084,grade+.1),(.19,.17,.49),iron)
    axle=(x,z,grade+.51)
    handle=(x+.23,z-.18,grade+.86)
    cane(geom,axle,handle,.032,iron,8)
    cane(geom,(x+.19,z-.18,grade+.86),(x+.30,z-.18,grade+.86),.045,gold,7)
    box(geom,(x-.075,z-.062,grade+.49),(.15,.12,.25),red)
    box(geom,(x-.068,z-.085,grade+.72),(.14,.161,.039),gold)


def boundary(geom,p,direction,grade,wood,iron):
    geometry_box(geom,p,direction,1.06,.28,grade+.05,.19,wood)
    geometry_box(geom,p,direction,1.09,.34,grade+.23,.105,iron)


def put_mine_tracks(geom,world,grade,wood,iron,gold,red,arena=False):
    choices=ARENA_ROUTES if arena else MINE_ROUTES
    markers=ARENA_STANDS if arena else MINE_STANDS
    for number,route in enumerate(choices):
        points=curve(route)
        direction=rails(geom,points,grade,wood,iron)
        if number==0:
            boundary(geom,points[0],direction[0],grade,wood,iron)
        if number<2:
            boundary(geom,points[-1],direction[-1],grade,wood,iron)
    for x,z in markers:
        switch_stand(geom,x,z,grade,wood,iron,gold,red)


def audit_mine_tracks(world):
    samples={}
    for number,route in enumerate(MINE_ROUTES):
        points=curve(route)
        _,side=spread(points)
        sweep=np.concatenate((points,points+.45*side,points-.45*side))
        cells=np.floor(2.*sweep).astype(int)
        unsafe=sweep[world.hgt[cells[:,1],cells[:,0]]!=2]
        samples[number]=unsafe
    return samples


if __name__=="__main__":
    from river_lion_worlds import variant
    _,_,gm,_,_=variant(Path(sys.argv[1]))
    world,_=gm.make("M484")
    arena,_=gm.make("M819")
    for j,path in enumerate(ARENA_ROUTES):
        points=curve(path)
        _,side=spread(points)
        sweep=np.concatenate((points,points+.45*side,points-.45*side))
        cells=np.floor(2.*sweep).astype(int)
        bad=sweep[arena.hgt[cells[:,1],cells[:,0]]!=0]
        print("arena",j,len(bad),np.round(bad[::max(1,len(bad)//10)],2).tolist())
    for i,cells in audit_mine_tracks(world).items():
        print(i,len(cells),np.round(cells[::max(1,len(cells)//15)],2).tolist())
