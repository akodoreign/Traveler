"""Sculpt the visible Coast Road cliffs around the installed block-world collision."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import types

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, spline_filter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import export_coast
from publish_castle_gates import publish as transact, resource_files
from early_materials import MATERIAL, MODEL, NATIVE, STORY, ramp, sections

MID="M102"
NAME="m102_sculpted_coastal_bluffs"
SKIN="m102_sculpted_cliff_skin"
THROAT=NAME+"_throat"
SEALED=NAME+"_sealed"
JOINED=NAME+"_limestone"
DRESSED=JOINED+"_dressed"
EGG_JAMB="m102_egg_limestone_jambs"
EGG_FLOOR="m102_egg_continuous_bore_floor"
THROAT_SKIN=SKIN+"_throat"
MAIN="m102_authored_materials_finish"
OLD_PINE="coast_pine_coastal_daylight"
PINE="traveler_diorama_pine_coastal_daylight"
BOULDER="river_cave_water_polished_boulder"
ROCK="m102_rock_finish"
INTERIOR="m102_tunnel_natural_shade"
THROAT_ROCK=ROCK+"_quiet"
THROAT_INTERIOR=INTERIOR+"_recessed"
THROAT_GROUND="m102_ground_cave_verge"
HEIGHT=2.092
FOOT=13.5
BACK=30.


def digest(data):
    return hashlib.sha256(data).hexdigest()


def world_spec(repo):
    """Evaluate the current map recipe without emitting a ladder sidecar."""
    source=repo/"tools/gen_maps.py"
    data=source.read_text("utf-8-sig")
    sidecar='json.dump({v: [k[0], k[1]] for k, v in ids.items()}, open(out, "w", encoding="utf-8"), indent=1, sort_keys=True)'
    assert data.count(sidecar)==1, "Refresh the read-only map recipe loader"
    module=types.ModuleType("gen_maps")
    module.__file__=str(source)
    sys.modules["gen_maps"]=module
    sys.path.insert(0,str(source.parent))
    exec(compile(data.replace(sidecar,"pass"),str(source),"exec"),module.__dict__)
    return module.make(MID)


class Bluff:
    def __init__(self,w):
        self.width=w.w*.5
        self.cut=w.environment_tunnel
        self.cx=self.cut["x"]*.5+.25
        self.front=self.cut["z"]*.5
        self.path_mask=np.zeros_like(w.hgt,dtype=bool)
        physical=w.hgt.copy()
        for left,right,z,grade in self.cut["path"]:
            assert np.all(w.hgt[z,left:right]==grade)
            self.path_mask[z,left:right]=True
        for x,y,z,width,height,depth,_ in self.cut["roof"]:
            physical[z:z+depth,x:x+width]=np.maximum(physical[z:z+depth,x:x+width],y+height-1)
        self.source=(physical.astype(np.float64)+1)*.5+.092
        self.spline=spline_filter(self.source,order=3,mode="nearest")
        assert w.d*.5==BACK and self.front==FOOT
        self.texture_width=4096
        self.texture_height=1024

    def height(self,x,z):
        x,z=np.broadcast_arrays(x,z)
        coords=np.array([(z*2.-.5).ravel(),(x*2.-.5).ravel()])
        linear=map_coordinates(self.source,coords,order=1,mode="nearest",prefilter=False).reshape(x.shape)
        spline=map_coordinates(self.spline,coords,order=3,mode="nearest",prefilter=False).reshape(x.shape)
        gentle=linear+.74*np.clip(spline-linear,-.18,.18)
        # No displacement at the original cell centers. The small erosion
        # wavelength only shapes the faces between those exact supports.
        between=(.5+.5*np.cos(4.*np.pi*x))*(.5+.5*np.cos(4.*np.pi*z))
        erosion=(.076*np.sin(x*2.9+z*4.1)+.037*np.sin(z*7.7-x*1.78))
        return np.maximum(HEIGHT,gentle+between*erosion*ramp(2.13,3.8,gentle))

    def chart(self,x,z,y):
        return (x+.042)/ (self.width+.084), (z-FOOT+.48*(y-HEIGHT)+.04)/(BACK-FOOT+2.68)


def read_rgb(path):
    return np.asarray(Image.open(path).convert("RGB"),dtype=np.float32)


def texture_lookup(rgb,u,v):
    height,width=rgb.shape[:2]
    return np.stack([map_coordinates(rgb[...,i],[v*(height-1),u*(width-1)],order=1,mode="nearest",
                                     prefilter=False) for i in range(3)],axis=-1)


def save_im(path,array):
    Image.fromarray(np.clip(np.rint(array),0,255).astype(np.uint8),"RGB").save(path,compress_level=5)


def quiet_color(color,sigma,strength):
    average=gaussian_filter(color,(sigma,sigma,0.),mode="nearest")
    return color+(average-color)*strength


def quiet_normal(pixels,sigma,strength):
    smooth=gaussian_filter(pixels,(sigma,sigma,0.),mode="nearest")/127.5-1.
    smooth[...,:2]*=strength
    return (1.+smooth/np.linalg.norm(smooth,axis=-1,keepdims=True).clip(.001,None))*127.5


def paint_bluff(b,tex,assets,finish=False):
    ground=read_rgb(assets/"tex/m102_ground.png")
    rock=read_rgb(assets/"tex/m102_rock_finish.png")
    rn=read_rgb(assets/"tex/m102_rock_finish_normal.png")
    gn=read_rgb(assets/"tex/m102_ground_normal.png")
    width,height=b.texture_width,b.texture_height
    u,v=np.meshgrid(np.linspace(0.,1.,width,dtype=np.float32),np.linspace(0.,1.,height,dtype=np.float32))
    xx=u*(b.width+.084)-.042
    z=np.linspace(FOOT-.14,BACK+.14,210)
    zchart=np.zeros_like(u)
    # Bending the relief atlas down the escarpment restores vertical texel
    # scale on steep terrain, instead of smearing a top-down projection.
    for i,wx in enumerate(xx[0]):
        yy=b.height(wx,z)
        _,curve=b.chart(wx,z,yy)
        zchart[:,i]=np.interp(v[:,i],np.maximum.accumulate(curve),z)
    yy=b.height(xx,zchart)
    dy=np.hypot((b.height(xx+.16,zchart)-b.height(xx-.16,zchart))/.32,
                (b.height(xx,zchart+.16)-b.height(xx,zchart-.16))/.32)
    moss=.18*np.sin(xx*.71+zchart*.49)+.15*np.sin(xx*.37-zchart*1.70)+.09*np.cos(xx*1.76+zchart*1.24)
    green=(1.-ramp(.31,1.65,dy+moss))*ramp(15.12,16.0,zchart)
    if finish:
        foot=1.-ramp(2.102,2.50,yy+.14*moss)
        around_mouth=ramp(1.34,2.60,np.abs(xx-b.cx))*ramp(13.55,14.6,zchart)+1.-ramp(13.55,14.6,zchart)
        green=np.maximum(green,foot*around_mouth)
        ground=quiet_color(ground,1.58,.89)
        rock=quiet_color(rock,1.50,.80)
        rn=quiet_normal(rn,1.65,.73)
        gn=quiet_normal(gn,1.92,.59)
    # Match the accepted local Coast Road atlas and live cliff grade.
    gu=(xx+.035)/(b.width+.07)
    gv=(zchart-6.956+.036)/(BACK-6.956+.072)
    ru=(xx+.72*zchart-4.99)/(b.width+16.62)
    rv=(yy-.965)/6.07
    a=texture_lookup(rock,ru,rv)
    d=texture_lookup(ground,gu,gv)
    base=a+(d-a)*green[...,None]
    base+=green[...,None]*moss[...,None]*[3.2,10.5,2.2]
    skin=THROAT_SKIN if finish else SKIN
    inside=THROAT_INTERIOR if finish else INTERIOR
    save_im(tex/(skin+".png"),base)
    n0,n1=texture_lookup(rn,ru,rv),texture_lookup(gn,gu,gv)
    normal=((n0+(n1-n0)*green[...,None])/127.5)-1.
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True).clip(.01,None)
    save_im(tex/(skin+"_normal.png"),(normal+1.)*127.5)
    save_im(tex/(inside+".png"),rock*([.39,.445,.51] if finish else [.48,.53,.59]))
    if finish:
        save_im(tex/(THROAT_ROCK+".png"),rock)
        save_im(tex/(THROAT_ROCK+"_normal.png"),rn)
        zg,xg=np.indices(ground.shape[:2],dtype=np.float32)
        zg=zg/(ground.shape[0]-1)*(BACK-6.956+.072)+6.956-.036
        xg=xg/(ground.shape[1]-1)*(b.width+.07)-.035
        meander=b.cx+.085*np.sin((zg-12.45)*2.96)+.078*np.sin(zg*1.39)
        edge=.63+.096*np.cos(zg*4.85)+.069*np.sin(xg*7.7+zg*5.3)
        reach=(1.-ramp(edge-.20,edge+.25,np.abs(xg-meander)))*ramp(12.26,12.73,zg)
        road=np.median(ground[272:350],axis=(0,1))
        sampled=np.broadcast_to(road,ground.shape)+ground*.065
        fade=ramp(14.40,17.1,zg)
        sample=sampled*(.82-.29*fade[...,None])
        path=ground+(sample-ground)*np.minimum(reach,.94)[...,None]
        save_im(tex/(THROAT_GROUND+".png"),path)
        save_im(tex/(THROAT_GROUND+"_normal.png"),gn)


def quad(mesh,points,style,coordinates):
    mesh.quad(points,[coordinates(*p) for p in points],style)


def rock_uv(x,z,y):
    return ((x+.72*z-4.99)/112.62,1.-(y-.965)/6.07)


def ground_uv(x,z):
    return ((x+.035)/96.07,1.-(z-6.92)/23.116)


def original_shell(mesh,assets,b,finish=False,omit_inner=False):
    """Retain the exact low surfaces and fitted inside faces of the Egg Cave."""
    desc=(assets/(MAIN+".pm")).read_text("utf8")
    points,groups,uv=sections(assets/(MAIN+".mdl"),with_uv=True)
    names=[key for key,_ in MATERIAL.findall(desc)]
    retained=[]
    skips=[]
    reprojection=[]
    for i,(p,j,old_uv) in enumerate(zip(points,groups,uv)):
        if p[:,1].max()<=2.099:
            style=names[j]
            mapped=[(u,1.-v) for u,v in old_uv]
            if finish:
                lower_riser=np.ptp(p[:,1])<.11 and np.ptp(p[:,1])>.001 and p[:,2].mean()>12.4
                at_mouth=np.ptp(p[:,1])<.001 and abs(p[:,0].mean()-b.cx)<2.15 and p[:,2].mean()>13.4
                if style=="m102_ground":
                    style=THROAT_GROUND
                elif style==ROCK and (at_mouth or lower_riser):
                    style=THROAT_GROUND
                    if lower_riser:
                        mapped=[ground_uv(x,z-.12 if y>2.044 else z-.045) for x,y,z in p]
                    else:
                        mapped=[ground_uv(x,z) for x,y,z in p]
                    reprojection.append(len(retained))
                elif style==ROCK:
                    style=THROAT_ROCK
            mesh.quad(p[:,[0,2,1]],mapped,style)
            retained.append(i)
        else:
            skips.append(i)
    # The old interior only contains cavity-facing surfaces below the roof.
    old_title="coastal_entrance"
    original_desc=(assets/(old_title+".pm")).read_text("utf8")
    original_mats=[key for key,_ in MATERIAL.findall(original_desc)]
    src=sections(assets/(old_title+".mdl"),with_uv=True)
    count=0
    for p,j,old_uv in zip(*src):
        if original_mats[j]!="interior":
            continue
        if not omit_inner:
            atlas_uv=[rock_uv(x,z,y) for x,y,z in p]
            mesh.quad(p[:,[0,2,1]],atlas_uv,THROAT_INTERIOR if finish else INTERIOR)
        count+=1
    return retained,skips,count,reprojection


def terrain(mesh,b,finish=False):
    nx=1+int(b.width*4)
    nz=1+int((BACK-FOOT)*4)
    xs=np.linspace(0.,b.width,nx)
    zs=np.linspace(FOOT,BACK,nz)
    x,z=np.meshgrid(xs,zs)
    y=b.height(x,z)
    y[0]=HEIGHT
    count=0
    for iz,ix in np.argwhere((y[:-1,:-1]>HEIGHT+.015)|(y[1:,:-1]>HEIGHT+.015)|
                              (y[:-1,1:]>HEIGHT+.015)|(y[1:,1:]>HEIGHT+.015)):
        cx=(xs[ix]+xs[ix+1])*.5
        cz=(zs[iz]+zs[iz+1])*.5
        # The entrance remains an actual opening beneath the first 7-cell
        # roof. Its center floor and normal walking clearance are authored.
        if finish and abs(cx-b.cx)<2.41 and 13.5<cz<15.95:
            continue
        if not finish and abs(cx-b.cx)<1.755 and cz<15.01:
            continue
        points=[(x[r,c],z[r,c],y[r,c]) for r,c in ((iz,ix),(iz,ix+1),(iz+1,ix+1),(iz+1,ix))]
        quad(mesh,points,THROAT_SKIN if finish else SKIN,lambda a,d,h:(b.chart(a,d,h)[0],1.-b.chart(a,d,h)[1]))
        count+=1
    return count


def cave_face(mesh,b):
    """Shape the visual jamb and lip along the actual recessed tunnel."""
    center=b.cx
    face,inside=14.85,15.49
    floor=2.008
    theta=np.linspace(0.,np.pi,25)
    samples=[]
    for a in theta:
        side=np.sign(np.cos(a))*abs(np.cos(a))**.57
        height=3.79+.72*np.sin(a)**.57
        wave=.075*np.sin(a*7.8)+.034*np.cos(a*13.2)
        samples.append((
            (center+1.72*side,face+.085*side+wave*.69,height),
            (center+1.80*side,face+.21+.057*np.sin(7*a),height+.16),
            (center+2.58*side,face+.39+abs(side)*.31,height+.73+wave),
            (center+3.20*side,inside+.43+abs(side)*.28,float(b.height(center+3.20*side,inside+.43+abs(side)*.28))),
        ))
    for a,c in zip(samples,samples[1:]):
        for j in range(3):
            quad(mesh,[a[j],c[j],c[j+1],a[j+1]],ROCK,rock_uv)
        p,q=a[0],c[0]
        p2,q2=(p[0],inside,p[2]),(q[0],inside,q[2])
        quad(mesh,[q,p,p2,q2],INTERIOR,rock_uv)
        quad(mesh,[q2,p2,p,q],INTERIOR,rock_uv)
    for j in (0,-1):
        rim=samples[j]
        for a,c in zip(rim,rim[1:]):
            points=[a,c,(c[0],c[1],floor),(a[0],a[1],floor)]
            quad(mesh,points if j==0 else points[::-1],ROCK,rock_uv)
        p=rim[0]
        points=[p,(p[0],inside,p[2]),(p[0],inside,floor),(p[0],p[1],floor)]
        quad(mesh,points if j==0 else points[::-1],INTERIOR,rock_uv)


def sculpt_throat(mesh,b):
    """Join the rounded entrance and low lining into the existing bluff."""
    center=b.cx
    floor=2.011
    outline=[]
    # Extend the jambs to the original floor before turning the arch.
    angles=np.linspace(0.,np.pi,33)
    for index,a in enumerate(angles):
        side=np.sign(np.cos(a))*abs(np.cos(a))**.82
        wave=.060*np.sin(a*7.94)+.031*np.cos(a*15.3)
        inner=(center+1.66*side,14.30+.07*side+.46*wave,3.23+1.16*np.sin(a)**.91+wave*.60)
        # A rock lip sweeps out above the established walk width.
        around=(center+1.83*side,14.44+.06*side+wave,inner[2]+.22+wave*.67)
        crown=(center+2.60*side,14.74+.40*abs(side)+1.12*wave,inner[2]+.83+wave)
        rear_d=16.41+.06*np.sin(a*5.9)
        rear_x=center+3.24*side
        back=(rear_x,rear_d,float(b.height(rear_x,rear_d)))
        if index==0:
            outline.append(((inner[0],inner[1]-.02,floor),
                            (around[0]+.15,around[1]-.11,floor+.018),
                            (crown[0]+.21,crown[1]-.25,floor+.14),
                            (rear_x+.12,15.71,float(b.height(rear_x+.12,15.71)))))
        outline.append((inner,around,crown,back))
        if index==len(angles)-1:
            outline.append(((inner[0],inner[1]-.02,floor),
                            (around[0]-.15,around[1]-.11,floor+.018),
                            (crown[0]-.21,crown[1]-.25,floor+.14),
                            (rear_x-.12,15.71,float(b.height(rear_x-.12,15.71)))))
    for a,c in zip(outline,outline[1:]):
        for index in range(3):
            # The outer weathered shoulder shares its own atlas with the cliff.
            points=[a[index],c[index],c[index+1],a[index+1]]
            if index<2:
                quad(mesh,points,THROAT_ROCK,rock_uv)
            else:
                quad(mesh,points,THROAT_SKIN,lambda x,z,y:(b.chart(x,z,y)[0],1.-b.chart(x,z,y)[1]))
        for near,far in zip((0.,.34,.68),(.34,.68,1.)):
            def lining(p,t):
                x,z,y=p
                dx=x-center
                # Inside backing is preserved and masked by these faces.
                # The end of the sleeve is behind the active z=16 threshold.
                end_x=center+dx*.932
                end_y=max(floor,y-.108)
                return (x+(end_x-x)*t,z+(16.42-z)*t,y+(end_y-y)*t-.024*np.sin(np.pi*t))
            surface=[lining(a[0],near),lining(c[0],near),lining(c[0],far),lining(a[0],far)]
            quad(mesh,surface[::-1],THROAT_INTERIOR,rock_uv)
            quad(mesh,surface,THROAT_INTERIOR,rock_uv)


def oriented(mesh,points,style,uv,direction):
    """Orient a visible face in the geometry exporter's x/z/y axes."""
    a,b,c,d=map(np.asarray,points)
    normal=np.cross(b-a,c-a)+np.cross(c-a,d-a)
    sign=float(np.dot(normal,direction))
    if sign<0.:
        points=points[::-1]
    quad(mesh,points,style,uv)


def bore_section(center,z,*,lip=False):
    floor=2.011-.50*ramp(17.495,17.515,z)
    half=1.65-.49*ramp(16.33,16.50,z)
    side_y=floor+1.19
    crown=4.41-.495*ramp(17.73,18.22,z)
    theta=np.linspace(0.,np.pi,41)
    arch=[]
    for a in theta:
        side=np.sign(np.cos(a))*abs(np.cos(a))**.82
        wave=np.sin(8.3*a)*np.sin(a)*.029
        x=center+half*side
        y=side_y+(crown-side_y)*np.sin(a)**.9+wave
        d=z+(.053*side+.021*np.sin(7*a) if lip else 0.)
        arch.append((x,d,y))
    return [(arch[0][0],arch[0][1],floor),*arch,
            (arch[-1][0],arch[-1][1],floor)]


def jamb_uv(x,z,y):
    return ((x-43.91)/8.68,1.-(y-1.94)/4.1)


def bore_floor_uv(x,z,y):
    # The y term supplies a visible rock mapping on the half-block riser.
    return ((x-46.40)/3.70,1.-(z-13.99+.16*(2.03-y))/6.65)


def limestone_materials(tex):
    """Give the jambs damp seams and add a calm, readable stone floor."""
    slate=read_rgb(tex/(THROAT_ROCK+".png"))
    old_normal=read_rgb(tex/(THROAT_ROCK+"_normal.png"))
    verge=read_rgb(tex/(THROAT_GROUND+".png"))
    v,u=np.mgrid[0.:1.:512j,0.:1.:1024j]
    x,y=43.91+8.68*u,1.94+4.1*v
    d=x-48.25
    a,b=(x+.72*(14.28+.06*np.sin(3.1*d))-4.99)/112.62,(y-.965)/6.07
    original=texture_lookup(slate,a,b)
    old=texture_lookup(old_normal,a,b)/127.5-1.
    dip=np.zeros_like(x)
    slab=np.zeros_like(x)
    for center,base,span,angle in (
        (-2.32,2.62,1.07,-.16),(-2.58,3.10,1.43,-.07),
        (2.25,2.57,1.14,.07),(2.84,2.96,1.22,.17),
        (-.93,4.42,1.12,-.11),(.84,4.63,1.19,.12),
    ):
        xx=d-center
        section=base+angle*xx+.075*np.sin(xx*5.12)+.038*np.cos(xx*11.0)
        long=1.-ramp(.29,1.,np.abs(xx)/span)
        dip+=long*np.exp(-((y-section)/.080)**2)
        slab+=long*np.exp(-((y-section-.116)/.119)**2)
    mineral=.27*np.sin(d*4.8+y*6.25)+.27*np.cos(d*7.32-y*5.18)+.46*np.sin(d*1.87-y*3.33)
    wet_lower=(1.-ramp(2.30,3.72,y+.18*mineral))*ramp(1.45,1.75,np.abs(d))
    moss=wet_lower*ramp(-.52,.39,mineral+.44*dip)
    weather=original+slab[...,None]*[12.,9.3,5.6]-dip[...,None]*[15.,15.,15.]
    green=np.array([31.,58.,33.])+mineral[...,None]*[11.,15.,9.]
    color=weather+(green-weather)*(.87*moss[...,None])
    save_im(tex/(EGG_JAMB+".png"),color)
    h=.019*slab-.012*dip+.014*moss+.008*mineral
    sy,sx=np.gradient(h,4.1/511.,8.68/1023.)
    normal=np.stack((.55*old[...,0]-sx,.56*old[...,1]+sy,np.ones_like(x)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    save_im(tex/(EGG_JAMB+"_normal.png"),(1.+normal)*127.5)

    z,x=np.mgrid[13.99:20.64:768j,46.40:50.10:512j]
    f=x-48.25
    uu=(x+.035)/96.07
    vv=(z-6.92)/23.116
    path=texture_lookup(verge,uu,vv)
    weather=.39*np.sin(f*4.6+z*2.17)+.29*np.sin(z*5.9-f*4.8)+.29*np.cos(z*3.75+f*7.2)
    joints=np.exp(-(np.sin(2.6*z+.29*np.sin(4.3*f)+.61*np.sin(z*.7+f))/.31)**2)
    joints*=ramp(-.26,.49,np.sin(3.8*f-z*2.9))
    stone=np.array([90.,85.,74.])+weather[...,None]*[17.,17.,16.]-joints[...,None]*[8.5,8.,6.3]
    stone-=ramp(16.25,20.20,z)[...,None]*[18.,17.,12.]
    transition=ramp(14.18,15.52,z+.11*weather)
    floor=path+(stone-path)*transition[...,None]
    save_im(tex/(EGG_FLOOR+".png"),floor)
    hd=(weather*.017-joints*.007)*transition
    sy,sx=np.gradient(hd,6.65/767.,3.70/511.)
    normal=np.stack((-sx,sy,np.ones_like(z)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    save_im(tex/(EGG_FLOOR+"_normal.png"),(1.+normal)*127.5)


def bore_support_floor(mesh,b):
    """Cover the native tunnel supports and the exact original half-step."""
    quads=0
    for left,right,cell_z,grade in b.cut["path"]:
        z=cell_z*.5
        start=max(z,14.08)
        stop=z+.5
        if start>=stop:
            continue
        x,x2=left*.5+.003,right*.5-.003
        height=(grade+1)*.5
        # The onset is just above the accepted atlas floor. After the
        # overlap the constant offset is 2.7 cm above native collision.
        boundaries=(start,14.35,stop) if start<14.35<stop else (start,stop)
        for a,c in zip(boundaries,boundaries[1:]):
            low=height+.021+.006*ramp(14.08,14.35,a)
            high=height+.021+.006*ramp(14.08,14.35,c)
            points=[(x,a,low),(x2,a,low),(x2,c,high),(x,c,high)]
            oriented(mesh,points,EGG_FLOOR,bore_floor_uv,np.array((0.,0.,1.)))
            quads+=1
    for prior,following in zip(b.cut["path"],b.cut["path"][1:]):
        left,right,cell_z,grade=following
        step=grade-prior[3]
        if not step:
            continue
        z=cell_z*.5
        x,x2=left*.5+.003,right*.5-.003
        top=(prior[3]+1)*.5+.027
        bottom=(grade+1)*.5+.027
        points=[(x,z,top),(x2,z,top),(x2,z,bottom),(x,z,bottom)]
        oriented(mesh,points,EGG_FLOOR,bore_floor_uv,np.array((0.,-np.sign(step),0.)))
        quads+=1
    return quads


def seal_throat(mesh,b):
    """Seal the complete aperture with an outcrop apron and a continuous bore."""
    center=b.cx
    entrance=bore_section(center,14.29,lip=True)
    rings=[entrance,[],[],[]]
    for x,z,y in entrance:
        side=(x-center)/1.65
        lift=ramp(2.02,4.41,y)
        fold=.038*np.sin(8.0*x+4.1*y)+.034*np.sin(4.4*x-7.9*y)
        rings[1].append((center+side*1.96,z+.15+fold,y+.084+.29*lift+fold))
        rings[2].append((center+side*2.74,14.76+.39*abs(side)+fold,
                         y+.16+.76*lift+.12*np.sin(3.8*side)))
        rear_x=center+side*3.62
        rear_z=16.38-.18*abs(side)+fold
        # The outer edge enters the continuous solid land form.
        rim=float(b.height(rear_x,rear_z))-.024
        if y<2.02:
            rear_z=15.11+.22*abs(side)+fold
            rim=2.082
        rings[3].append((rear_x,rear_z,rim))
    for index,(inner,outer) in enumerate(zip(rings,rings[1:])):
        style=THROAT_ROCK if index<2 else THROAT_SKIN
        uv=rock_uv if index<2 else lambda x,z,y:(b.chart(x,z,y)[0],1.-b.chart(x,z,y)[1])
        for a,c,p,q in zip(inner,inner[1:],outer,outer[1:]):
            # The camera approaches from -z. The face normal is measured
            # in the same basis from which the exporter computes winding.
            oriented(mesh,[a,c,q,p],style,uv,np.array((0.,-1.,.05)))
    behind=[entrance,*[bore_section(center,z) for z in
         (14.52,14.91,15.29,15.72,16.03,16.32,16.50,16.85,17.22,17.495,
          17.515,17.87,18.26,18.72,19.21,19.71,20.17,20.48)]]
    for front,back in zip(behind,behind[1:]):
        for a,c,p,q in zip(front,front[1:],back,back[1:]):
            average=(np.asarray(a)+c+p+q)*.25
            towards=np.array((center-average[0],0.,2.78-average[2]))
            oriented(mesh,[a,c,q,p],THROAT_INTERIOR,rock_uv,towards)
    rear=behind[-1]
    for a,c in zip(rear[1:-2],rear[2:-1]):
        points=[a,c,(c[0],c[1],rear[0][2]),(a[0],a[1],rear[0][2])]
        oriented(mesh,points,THROAT_INTERIOR,rock_uv,np.array((0.,-1.,0.)))

    # A continuous stone section immediately behind the scarp closes its
    # union with the bluff at all angles. Only the exact bore remains open.
    seam_z=15.985
    aperture=bore_section(center,seam_z)
    profile=np.asarray(aperture[-2:0:-1])
    left,right=profile[0,0],profile[-1,0]
    intervals=[(np.linspace(center-3.94,left,25),False),
               (profile[:,0],True),
               (np.linspace(right,center+3.94,25),False)]
    for span,bore in intervals:
        if bore:
            bottom=profile[:,2]-.025
        else:
            bottom=np.full(len(span),2.014)
        depth=seam_z+.022*np.sin(span*1.3)
        cap=np.maximum(b.height(span,depth)+.025,bottom+.065)
        for i in range(len(span)-1):
            # Outer faces are hidden behind most of the curved apron, and
            # the closed side backs sit inside the current cliff volume.
            ab=(span[i],depth[i],bottom[i])
            cb=(span[i+1],depth[i+1],bottom[i+1])
            ac=(span[i],depth[i],cap[i])
            cc=(span[i+1],depth[i+1],cap[i+1])
            oriented(mesh,[ab,cb,cc,ac],THROAT_ROCK,rock_uv,np.array((0.,-1.,0.)))


def joined_limestone(mesh,b,dressed=False):
    """Connect the front limestone apron to the real terrain without gaps."""
    center=b.cx
    width=4.17
    ground=1.985
    front=14.28
    back=16.43
    level=np.linspace(0.,1.,7)
    face_normal=np.array((0.,-1.,0.))
    roof_normal=np.array((0.,0.,1.))
    arc=np.asarray(bore_section(center,front)[-2:0:-1])
    jamb=EGG_JAMB if dressed else THROAT_ROCK
    surface_uv=jamb_uv if dressed else rock_uv

    def edge_z(x,y):
        d=x-center
        weather=.039*np.sin(4.21*d+1.64*y)+.052*np.cos(2.47*d-3.21*y)
        if dressed:
            rim=np.interp(x,arc[:,0],arc[:,2])
            above=y-rim
            brim=ramp(.025,.13,above)*(1.-ramp(.27,.62,above))*(1.-ramp(1.18,1.69,abs(d)))
            chip=.074*np.sin(17.7*d+3.31*y)+.039*np.cos(5.93*d-7.7*y)
            weather+=brim*chip
        return front+.22*(abs(d)/width)**1.85+weather

    def roof_y(x):
        d=x-center
        body=1.-ramp(2.26,width,abs(d))
        mark=5.61+(.09*np.sin(2.3*d)+.07*np.cos(4.87*d))*body
        edge=float(b.height(x,15.36))+.045
        return (1.-body)*edge+body*mark

    def grade_uv(x,z,y):
        return ground_uv(x,z)

    def skin_uv(x,z,y):
        u,v=b.chart(x,z,y)
        return u,1.-v

    def contour(z,at_lip=False):
        section=bore_section(center,z)
        first,last=np.asarray(section[0]),np.asarray(section[-1])
        start,end=np.asarray(section[1]),np.asarray(section[-2])
        right=[first+t*(start-first) for t in level[:-1]]
        left=[end+t*(last-end) for t in level[1:]]
        points=[*right,*section[1:-1],*left]
        if at_lip:
            return [(x,edge_z(x,y),y) for x,_,y in points]
        return [tuple(p) for p in points]

    lip=contour(front,True)
    arch=list(reversed(lip[6:-6]))
    left,right=arch[0][0],arch[-1][0]
    sill,shoulder=lip[0][2],lip[6][2]
    x_left=np.linspace(center-width,left,23)
    x_right=np.linspace(right,center+width,23)

    def curtain(xs,sill,high):
        surface=[]
        for x,lo,hi in zip(xs,sill,high):
            ys=lo+level*(hi-lo)
            surface.append([(x,edge_z(x,y),y) for y in ys])
        for left_column,right_column in zip(surface,surface[1:]):
            for i in range(len(level)-1):
                points=(left_column[i],right_column[i],right_column[i+1],left_column[i+1])
                oriented(mesh,points,jamb,surface_uv,face_normal)

    for xs in (x_left,x_right):
        foot=[ground]*len(xs)
        # Split at the jamb spring so the side returns share each lip
        # vertex with the opening, at the same tessellation rate.
        shoulder_line=[min(shoulder,roof_y(x)-.02) for x in xs]
        curtain(xs,foot,[sill]*len(xs))
        curtain(xs,[sill]*len(xs),shoulder_line)
        curtain(xs,shoulder_line,[roof_y(x) for x in xs])
    curtain([p[0] for p in arch],[p[2] for p in arch],[roof_y(p[0]) for p in arch])

    # The upper rear edge lands on the same surface the bluff renders.
    xs=[*x_left[:-1],*(p[0] for p in arch),*x_right[1:]]
    depth=np.linspace(0.,1.,13)
    cap=[]
    for x in xs:
        y0=roof_y(x)
        z0=edge_z(x,y0)
        ridge=[]
        for t in depth:
            z=z0+t*(back-z0)
            y0_to_land=y0+(float(b.height(x,z))-y0)*ramp(.12,1.,t)
            ridge.append((x,z,y0_to_land))
        cap.append(ridge)
    for left_column,right_column in zip(cap,cap[1:]):
        for i in range(len(depth)-1):
            points=(left_column[i],right_column[i],right_column[i+1],left_column[i+1])
            oriented(mesh,points,THROAT_SKIN,skin_uv,roof_normal)
    for cap_edge,side in ((cap[0],-1.),(cap[-1],1.)):
        for a,c in zip(cap_edge,cap_edge[1:]):
            points=[a,c,(c[0],c[1],ground),(a[0],a[1],ground)]
            oriented(mesh,points,jamb,surface_uv,np.array((side,0.,0.)))

    # The visible path retains all old ground faces. This lower layer only
    # closes the seams between the foot of the art and the verge.
    foundation=[(center-width-.10,13.43,ground),(center+width+.10,13.43,ground),
                (center+width+.10,16.42,ground),(center-width-.10,16.42,ground)]
    oriented(mesh,foundation,THROAT_GROUND,grade_uv,roof_normal)

    bore=[lip,*[contour(z) for z in
          (14.48,14.70,14.97,15.31,15.61,15.88,16.10,16.32,16.50,16.83,17.20,17.495,
           17.515,17.87,18.27,18.70,19.19,19.70,20.17,20.48)]]
    for face,reverse in zip(bore,bore[1:]):
        for a,c,p,q in zip(face,face[1:],reverse,reverse[1:]):
            average=(np.asarray(a)+c+p+q)*.25
            inner=np.array((center-average[0],0.,2.78-average[2]))
            oriented(mesh,[a,c,q,p],THROAT_INTERIOR,rock_uv,inner)
    rear=bore[-1][6:-6]
    floor=bore[-1][0][2]
    for a,c in zip(rear,rear[1:]):
        points=[a,c,(c[0],c[1],floor),(a[0],a[1],floor)]
        oriented(mesh,points,THROAT_INTERIOR,rock_uv,face_normal)
    return bore_support_floor(mesh,b) if dressed else 0


def placements(row,b):
    results=[]
    for item in row["placements"]:
        model,x,y,z,scale,yaw,*motion=item
        if model=="coastal_entrance":
            continue
        if model==OLD_PINE:
            if y>=2.5 and z>=FOOT:
                y=float(b.height(x,z))-.042
            results.append([PINE,x,y,z,scale,yaw,*([.022] if not motion else motion)])
        elif model=="shore_talus":
            results.append([BOULDER,x,y,z,.57+.030*np.cos(x*.29),yaw,*motion])
        else:
            results.append(item)
    return results


def prepare(repo,bundle,finish=False,predecessor=None,sealed=False,joined=False,dressed=False):
    engine=repo/"_tools/rpgcobo-tool"
    assets=engine/NATIVE
    base=json.loads((assets/"index.json").read_bytes())[MID]
    story=json.loads((engine/STORY).read_bytes())[MID]
    physical=digest((engine/"project/data/mapdata/M102.bw").read_bytes())
    w,e=world_spec(repo)
    assert base["terrain"]==MAIN and e.ev["#11#"]["pos"]==story["event"]["#11#"]["pos"]
    b=Bluff(w)
    export_coast.STAGE=bundle/"files"
    tex=export_coast.STAGE/"tex"
    tex.mkdir(parents=True,exist_ok=True)
    # Reuse the exact approved textures on the walking surfaces.
    kept=("m102_ground","m102_seawall_finish",ROCK)
    for style in kept:
        for suffix in ("","_normal"):
            path=tex/f"{style}{suffix}.png"
            path.write_bytes((assets/"tex"/path.name).read_bytes())
    if sealed or joined:
        assert finish and predecessor
        prior=json.loads((predecessor/"coast-bluff-proof.json").read_bytes())
        assert prior["base"]==base and prior["world_sha256"]==physical
        assert {k:v for k,v in prior["story"].items() if k!="bg"}=={k:v for k,v in story.items() if k!="bg"}
        assert prior["after"]["terrain"]==(JOINED if dressed else SEALED if joined else THROAT)
        for rel,sum_ in prior["files"].items():
            if rel.startswith("tex/"):
                data=(predecessor/"files"/rel).read_bytes()
                assert digest(data)==sum_
                (export_coast.STAGE/rel).write_bytes(data)
        if dressed:
            assert joined
            limestone_materials(tex)
    else:
        paint_bluff(b,tex,assets,finish)
    mesh=export_coast.Geometry()
    preserved,_,inside,reprojected=original_shell(mesh,assets,b,finish,omit_inner=joined)
    sculpted=terrain(mesh,b,finish)
    floor_faces=0
    if finish:
        if joined:
            floor_faces=joined_limestone(mesh,b,dressed)
        elif sealed:
            seal_throat(mesh,b)
        else:
            sculpt_throat(mesh,b)
        model=DRESSED if dressed else JOINED if joined else SEALED if sealed else THROAT
        normals=("m102_seawall_finish",THROAT_SKIN,THROAT_GROUND,THROAT_ROCK)
        shading=THROAT_INTERIOR
        softened=(THROAT_SKIN,THROAT_ROCK,THROAT_INTERIOR) if joined else (THROAT_SKIN,)
        if dressed:
            normals=(*normals,EGG_JAMB,EGG_FLOOR)
            softened=(*softened,EGG_JAMB)
    else:
        cave_face(mesh,b)
        model=NAME
        normals=(*kept,SKIN)
        shading=INTERIOR
        softened=(SKIN,)
    names={name:(name+".png",.88) for name in (*normals,shading)}
    normal={name:name+"_normal.png" for name in normals}
    export_coast.export(model,mesh,names,normal_maps=normal,smooth_materials=softened)
    row={**base,"terrain":model,"hideStockScenery":True,"placements":placements(base,b)}
    # Check exact supports at centers of every visible lower floor cell
    # and every retained original shell vertex, plus the tunnel headroom.
    src,_,old_uv=sections(assets/(MAIN+".mdl"),with_uv=True)
    staged,_,new_uv=sections(export_coast.STAGE/(model+".mdl"),with_uv=True)
    assert np.array_equal(staged[:len(preserved)],src[preserved])
    corresponding=np.ones(len(preserved),dtype=bool)
    corresponding[reprojected]=False
    assert np.allclose(new_uv[:len(preserved)][corresponding],old_uv[preserved][corresponding],atol=1e-7)
    old,groups=sections(assets/"coastal_entrance.mdl")
    labels=[key for key,_ in MATERIAL.findall((assets/"coastal_entrance.pm").read_text("utf8"))]
    inner=old[groups==labels.index("interior")]
    if joined:
        assert len(inner)==inside==41
    else:
        assert np.array_equal(staged[len(preserved):len(preserved)+inside],inner)
    z,x=np.nonzero((w.hgt>=4)&~b.path_mask)
    tops=(w.hgt[z,x]+1)*.5+.092
    difference=np.abs(b.height(x*.5+.25,z*.5+.25)-tops)
    assert difference.max()<1e-8
    assert inside>0 and b.cx==48.25 and story["event"]["#11#"]["pos"]==[96,4,32,0]
    assert len(row["placements"])==len(base["placements"])-1
    new_style=(THROAT_SKIN,THROAT_ROCK,THROAT_GROUND) if finish else (SKIN,)
    if dressed:
        new_style=(*new_style,EGG_JAMB,EGG_FLOOR)
        assert floor_faces==15
    files=[model+".mdl",model+".pm",f"tex/{shading}.png",
           *(f"tex/{style}{suffix}.png" for style in new_style for suffix in ("","_normal"))]
    proof={"base":base,"after":row,"story":story,"world_sha256":physical,
           "retained_low_quads":len(preserved),"retained_interior_quads":0 if joined else inside,
           "removed_render_interior_quads":inside if joined else 0,"sculpted_quads":sculpted,
           "native_floor_overlay_quads":floor_faces,
           "checked_bluff_cells":len(tops),"max_center_delta_m":float(difference.max()),"resurfaced_low_quads":len(reprojected),
           "replaced_rocks":sum(p[0]==BOULDER for p in row["placements"]),"gate":story["event"]["#11#"]["pos"],
           "files":{name:digest((export_coast.STAGE/name).read_bytes()) for name in files},
           "shared":{path.name:digest(path.read_bytes()) for path in tex.glob("*.png")
                     if path.stem.removesuffix("_normal") in normals and "tex/"+path.name not in files}}
    if predecessor:
        original=json.loads((predecessor/"coast-bluff-proof.json").read_bytes())
        assert original["base"]==base and original["world_sha256"]==physical
        if original["story"]!=story:
            assert {k:v for k,v in original["story"].items() if k!="bg"}=={k:v for k,v in story.items() if k!="bg"}
            proof["previous_story"]=original["story"]
        assert original["after"]["terrain"]==(JOINED if dressed else SEALED if joined else THROAT if sealed else NAME)
        proof["predecessor"]=original["after"]
        if sealed or joined:
            proof["earlier"]=original["predecessor"]
    (bundle/"coast-bluff-proof.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),"utf8")
    print({key:proof[key] for key in ("retained_low_quads","retained_interior_quads","sculpted_quads","checked_bluff_cells","max_center_delta_m","replaced_rocks")})


def apply(repo,bundle,profile,publish=False):
    real=(repo/"_tools/rpgcobo-tool").resolve()
    assert real!=profile
    live=real if publish else profile
    receipt=json.loads((bundle/"coast-bluff-proof.json").read_bytes())
    path=live/NATIVE/"index.json"
    raw=path.read_bytes()
    catalog=json.loads(raw)
    base,after=receipt["base"],receipt["after"]
    assert catalog[MID] in (base,after,receipt.get("predecessor"),receipt.get("earlier")),MID
    raw_story=json.loads((live/STORY).read_bytes())
    compatible=(receipt["story"],) if publish else (receipt["story"],receipt.get("previous_story"))
    assert raw_story[MID] in compatible,MID
    assert digest((live/"project/data/mapdata/M102.bw").read_bytes())==receipt["world_sha256"]
    if publish:
        reviewed=json.loads((profile/NATIVE/"index.json").read_bytes())
        assert reviewed[MID]==after
        assert digest((profile/"project/data/mapdata/M102.bw").read_bytes())==receipt["world_sha256"]
        assert json.loads((profile/STORY).read_bytes())[MID]==receipt["story"]
    additions={}
    for rel,key in receipt["files"].items():
        data=(bundle/"files"/rel).read_bytes()
        assert digest(data)==key
        target=live/NATIVE/rel
        if publish:
            assert (profile/NATIVE/rel).read_bytes()==data
        if target.is_file():
            assert target.read_bytes()==data
        else:
            additions[target]=data
    for leaf,key in receipt["shared"].items():
        assert digest((live/NATIVE/"tex"/leaf).read_bytes())==key,leaf
    for rel,content in resource_files(real/NATIVE,{"reused":{"placements":[[PINE],[BOULDER]]}}).items():
        path_to=live/NATIVE/rel
        if path_to.is_file():
            assert path_to.read_bytes()==content,rel
        else:
            assert not publish,rel
            additions[path_to]=content
    catalog[MID]=after
    for target in additions:
        target.parent.mkdir(parents=True,exist_ok=True)
    transact({path:raw},{path:json.dumps(catalog,separators=(",",":"),ensure_ascii=False).encode()},additions)
    print("Published M102 sculpted coast." if publish else "Staged M102 sculpted coast.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--profile",type=Path)
    parser.add_argument("--finish",action="store_true")
    parser.add_argument("--sealed",action="store_true")
    parser.add_argument("--joined",action="store_true")
    parser.add_argument("--dressed",action="store_true")
    parser.add_argument("--predecessor",type=Path)
    args=parser.parse_args()
    if args.action=="prepare":
        prepare(args.repo.resolve(),args.bundle.resolve(),args.finish,args.predecessor,args.sealed,args.joined,args.dressed)
    else:
        apply(args.repo.resolve(),args.bundle.resolve(),args.profile.resolve(),args.action=="publish")


if __name__=="__main__":
    main()
