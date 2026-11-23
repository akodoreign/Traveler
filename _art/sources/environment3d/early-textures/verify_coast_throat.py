"""Measure view-facing clearance and closure in the native Coast Road mesh."""
from __future__ import annotations

from dataclasses import dataclass
import json
from math import cos, radians, sin, tan
from pathlib import Path
import sys

import numpy as np

from early_materials import sections


@dataclass
class Ray:
    label: str
    origin: tuple[float,float,float]
    direction: tuple[float,float,float]
    cutoff: float
    blocked: bool


def distances(triangles,origin,direction):
    """Use the renderer's front-face winding and discard rear-facing hits."""
    a,b,c=triangles.transpose(1,0,2)
    e1,e2=b-a,c-a
    ray=np.array(direction)
    h=np.cross(ray,e2)
    det=np.einsum("ij,ij->i",e1,h)
    facing=det>1e-6
    a,e1,e2,h,det=(v[facing] for v in (a,e1,e2,h,det))
    s=np.array(origin)-a
    u=np.einsum("ij,ij->i",s,h)/det
    q=np.cross(s,e1)
    v=q@ray/det
    d=np.einsum("ij,ij->i",e2,q)/det
    seen=(u>=-1e-6)&(v>=-1e-6)&(u+v<=1.000001)&(d>1e-6)
    return d[seen]


def measurements(mesh):
    source,_=sections(mesh)
    q=source[np.any((source[...,0]>43.)&(source[...,0]<53.50)&
                    (source[...,2]>=12.25)&(source[...,2]<20.75),axis=1)]
    triangles=q[:,[[0,2,1],[0,3,2]],:].reshape(-1,3,3)
    tests=[]
    center=48.25
    along=(0.,0.,1.)
    front=12.69
    for x in (47.43,47.89,48.25,48.61,49.07):
        for y in (2.15,2.50,2.95,3.35,3.78):
            tests.append(Ray("walking clearance",(x,y,front),along,16.37-front,False))
    for side in (-1.,1.):
        for offset in (1.81,2.12,2.46,2.80,3.15):
            for y in (2.16,2.53,2.95,3.35,3.74):
                tests.append(Ray("stone flank",(center+side*offset,y,front),along,16.37-front,True))
        vector=np.array((-.46*side,0.,1.))
        direction=tuple(vector/np.linalg.norm(vector))
        for offset in (1.97,2.34,2.68):
            for y in (2.32,2.98,3.53):
                origin=(center+side*(offset+1.36),y,front)
                tests.append(Ray("oblique flank",origin,direction,4.0,True))
    for offset in (-1.25,-.77,0.,.77,1.25):
        for y in (4.49,4.68,4.91,5.14):
            tests.append(Ray("stone above rim",(center+offset,y,front),along,16.37-front,True))
    for z in (14.70,15.4,16.17,17.04,18.32,19.82):
        for side in (-1.,1.):
            tests.append(Ray("inside sidewall",(center,2.62,z),(side,0.,0.),2.7,True))
            tests.append(Ray("inside corner",(center+side*.39,3.28,z),(side,0.,0.),2.7,True))
        for offset in (-.70,0.,.70):
            tests.append(Ray("inside ceiling",(center+offset,3.57,z),(0.,1.,0.),1.7,True))
    for y in (2.40,2.71,3.30,3.64):
        for offset in (-.61,0.,.61):
            tests.append(Ray("opaque far rock",(center+offset,y,18.43),along,2.18,True))
    if mesh.stem.endswith("_limestone"):
        tests.extend(native_views(center))
    issues=[]
    totals={}
    for test in tests:
        received=distances(triangles,test.origin,test.direction)
        hit=np.any(received<=test.cutoff)
        totals[test.label]=totals.get(test.label,0)+1
        if hit!=test.blocked:
            issues.append((test.label,test.origin,float(received.min()) if len(received) else None))
    print(totals)
    assert not issues,issues


def camera_eye(target,heading,pitch,level,fovy):
    """Reconstruct the perspective view used by CoastCamera.modifyCamera."""
    radius=level*.5/tan(radians(fovy)*.5)
    return np.asarray(target)+radius*np.array((-sin(heading)*cos(pitch),sin(pitch),-cos(heading)*cos(pitch)))


def native_views(center):
    entrance=((48.23,2.95,15.15),.23,.28,8.4,56.)
    interior=((48.23,2.29,16.11),.03,.09,5.8,56.)
    for key,view in (("entrance",entrance),("interior",interior)):
        eye=camera_eye(*view)
        def project(label,target):
            ray=np.asarray(target)-eye
            length=float(np.linalg.norm(ray))
            return Ray(f"{key} camera {label}",tuple(eye),tuple(ray/length),length+.035,True)
        for side in (-1.,1.):
            for dx in (1.79,2.03,2.32,2.56,2.84,3.14):
                for y in (2.09,2.25,2.46,2.78,3.13,3.49):
                    yield project("lower jamb",(center+side*dx,y,14.67))
        for dx in (-1.32,-.87,0.,.87,1.32):
            for y in (4.43,4.61,4.85,5.11):
                yield project("limestone above lip",(center+dx,y,14.71))
        for z in (15.14,15.60,16.10,16.85,17.70,18.55):
            for dx in (-.80,0.,.80):
                yield project("bore ceiling",(center+dx,4.55,z))


if __name__=="__main__":
    root=Path(sys.argv[1])
    proof=json.loads((root/"coast-bluff-proof.json").read_bytes())
    measurements(root/"files"/(proof["after"]["terrain"]+".mdl"))
