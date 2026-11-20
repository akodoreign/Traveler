"""Paint clan lacquering along the visible upper perimeters of fitted hard plates."""
from argparse import ArgumentParser
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

from author_rivet_guides import BASE, barycentric, draw_texture, load_native_mesh, projection, project, tex_array


def flipped(course):
    return [(w, [(-x, y) for x, y in points]) for w, points in course]


def arc(width, left_side, top, right_side):
    return width, [left_side, *top, right_side]


def level(y, left, right, drop, width=.28, bend=.12):
    return arc(width, (left+.12,y-drop), [(left,y), ((left+right)/2,y+bend), (right,y)],
               (right-.12,y-drop))


def hiruma_shoulder(rear):
    if rear:
        return [
            arc(.30, (-14.65,89.4), [(-14.7,93.1),(-12.4,95.5),(-10.1,93.4),(-8.55,90.7)], (-9.5,87.5)),
            arc(.25, (-14.75,86.6), [(-14.7,89.6),(-12.9,88.3),(-10.6,86.2),(-9.3,84.9)], (-10.25,82.9)),
        ]
    return [
        arc(.31, (-14.5,89.3), [(-14.4,93.35),(-12.15,95.65),(-10.0,94.2),(-8.55,91.8)], (-9.1,87.9)),
        arc(.27, (-14.7,88.), [(-14.5,90.7),(-12.7,89.7),(-11.0,88.6),(-8.15,86.2)], (-8.85,83.9)),
        arc(.24, (-14.65,83.4), [(-14.55,86.),(-12.8,85.15),(-10.5,83.75),(-8.6,82.)], (-9.55,80.5)),
    ]


def kabuto_guard(y, inside, outside, shoulder_rise=.46, width=.26):
    return arc(width, (inside+.06, y-1.02),
               [(inside,y), ((inside+outside)*.5,y+.13),(outside,y+shoulder_rise)],
               (outside+.12,y-.56))


def do_maru_shoulder():
    return [
        arc(.33, (-14.95,90.6), [(-14.75,93.4),(-12.9,95.3),(-10.4,96.1),(-8.15,94.7)], (-8.6,92.4)),
        arc(.28, (-14.5,86.5), [(-14.65,89.5),(-12.8,90.3),(-10.7,91.35),(-8.75,91.95)], (-8.7,89.8)),
        arc(.24, (-13.65,82.6), [(-14.1,85.4),(-12.2,86.12),(-10.5,87.1),(-8.8,87.9)], (-8.8,85.8)),
    ]


COURSES = {
    "A173": {
        1: (hiruma_shoulder(False) + flipped(hiruma_shoulder(False)) +
            [level(86.1,-4.05,4.05,2.32,.31,.2),
             level(79.3,-4.10,4.10,1.72,.28,.10),
             level(74.97,-4.13,4.13,1.62,.28,.08),
             level(71.06,-4.10,4.10,1.54,.28,.08),
             arc(.25,(-9.0,62.55),[(-8.9,64.45),(-7.95,65.07),(-7.25,65.36)],(-7.44,63.08))] +
            flipped([arc(.25,(-9.0,62.55),[(-8.9,64.45),(-7.95,65.07),(-7.25,65.36)],(-7.44,63.08))])),
        -1: (hiruma_shoulder(True) + flipped(hiruma_shoulder(True)) +
             [level(74.85,-7.3,7.3,1.45,.26,-.12),
              level(69.18,-7.8,7.8,1.65,.31,.2),
              level(63.00,-9.25,9.25,1.3,.28,-.36)]),
    },
    "A110": {
        1: ([arc(.25,(-8.35,125.25),[(-7.25,126.34),(-4.7,127.7),(-1.35,128.24),
                                   (1.35,128.24),(4.7,127.7),(7.25,126.34)],(8.35,125.25)),
             arc(.29,(-8.2,113.65),[(-8.25,114.8),(-5.45,116.62),(-2.9,116.27),
                                     (0,115.07),(2.9,116.27),(5.45,116.62),(8.25,114.8)],(8.2,113.65))] +
             [arc(.29,(10.54,116.95),[(10.0,118.45),(11.45,120.06),(12.4,120.38),
                                       (13.75,118.76),(14.95,117.36)],(15.65,115.90)),
              kabuto_guard(111.72,8.01,12.45), kabuto_guard(109.2,8.23,13.57),
              kabuto_guard(106.9,8.4,14.43)] +
             flipped([arc(.29,(10.54,116.95),[(10.0,118.45),(11.45,120.06),(12.4,120.38),
                                              (13.75,118.76),(14.95,117.36)],(15.65,115.90)),
                      kabuto_guard(111.72,8.01,12.45), kabuto_guard(109.2,8.23,13.57),
                      kabuto_guard(106.9,8.4,14.43)])),
        -1: ([arc(.27,(-9.15,125.20),[(-8.15,126.38),(-4.8,127.58),(-1.55,128.21),
                                     (1.55,128.21),(4.8,127.58),(8.15,126.38)],(9.15,125.20)),
              arc(.26,(-8.44,116.28),[(-8.55,117.7),(-5.42,117.66),(0,117.58),
                                      (5.42,117.66),(8.55,117.7)],(8.44,116.28)),
              arc(.27,(-12.08,110.67),[(-11.55,112.0),(-8.06,111.23),(0,110.96),
                                       (8.06,111.23),(11.55,112.0)],(12.08,110.67)),
              arc(.28,(-13.13,108.34),[(-12.42,109.66),(-8.77,109.01),(0,108.97),
                                       (8.77,109.01),(12.42,109.66)],(13.13,108.34)),
              arc(.26,(-14.05,105.88),[(-13.45,107.45),(-9.19,106.82),(0,106.67),
                                       (9.19,106.82),(13.45,107.45)],(14.05,105.88))]),
    },
    "A141": {
        1: (do_maru_shoulder() + flipped(do_maru_shoulder()) +
            [level(86.98,-5.75,5.75,2.1,.31,-.58),
             level(82.25,-5.75,5.75,1.76,.29,-.39),
             level(78.25,-5.65,5.65,1.65,.28,-.38),
             level(74.18,-4.87,4.87,1.71,.31,-.35),
             level(59.69,4.0,9.6,2.04,.3,-.38),
             level(54.9,4.42,10.2,2.11,.29,-.4),
             level(49.68,4.97,11.2,2.0,.29,-.43)] +
            flipped([level(59.69,4.0,9.6,2.04,.3,-.38),
                     level(54.9,4.42,10.2,2.11,.29,-.4),
                     level(49.68,4.97,11.2,2.0,.29,-.43)])),
        -1: (do_maru_shoulder() + flipped(do_maru_shoulder()) +
             [level(62.2,-7.96,7.96,1.7,.29,-.21),
              level(56.4,-8.72,8.72,2.3,.29,-.2),
              level(51.25,-9.3,9.3,2.22,.28,-.32)]),
    },
}


from catalog_plate_courses import add_catalog

add_catalog(COURSES, arc, flipped, level)


def ease(a, b, v):
    t = np.clip((v-a)/(b-a),0,1)
    return t*t*(3-2*t)


def masks(verts, uv, faces, view, render, item, w, h):
    left, top, scale, pw, ph = view
    projected = verts[faces][:, :, (2, 1)]
    mins, maxs = projected.min(axis=1), projected.max(axis=1)
    surface_uv = uv[faces] * (w-1, h-1)
    outline = np.zeros((h,w),dtype=np.float32)
    high = np.zeros((h,w),dtype=np.float32)
    for side, depth in render.items():
        for radius, course in COURSES[item][side] if item in COURSES else []:
            for k, (p, q) in enumerate(zip(course, course[1:])):
                p, q = np.asarray(p), np.asarray(q)
                low, top_edge = np.minimum(p,q)-radius, np.maximum(p,q)+radius
                candidates = np.flatnonzero(np.all((mins <= top_edge) & (maxs >= low),axis=1))
                direction = q-p
                for ti in candidates:
                    triangle = surface_uv[ti]
                    x0,y0=np.maximum(0,np.floor(triangle.min(axis=0)).astype(int))
                    x1,y1=np.minimum((w-1,h-1),np.ceil(triangle.max(axis=0)).astype(int))
                    yy,xx=np.mgrid[y0:y1+1,x0:x1+1].astype(np.float32)
                    weights = barycentric(triangle,xx,yy)
                    if weights is None:
                        continue
                    a,b,c=weights
                    inside=(a>=-.024)&(b>=-.024)&(c>=-.024)
                    if not np.any(inside):
                        continue
                    v0,v1,v2=verts[faces[ti]]
                    world=v0*a[...,None]+v1*b[...,None]+v2*c[...,None]
                    relative=world[...,(2,1)]-p
                    step=np.clip(np.sum(relative*direction,axis=-1)/(direction@direction),0,1)
                    start=ease(0.,.56,step) if k==0 else 1.
                    end=1-ease(.44,1.,step) if k==len(course)-2 else 1.
                    taper=start*end
                    offset=relative-direction*step[...,None]
                    distance=np.linalg.norm(offset,axis=-1)
                    sx=np.clip(((world[...,2]-left)*scale).astype(int),0,pw-1)
                    sy=np.clip(((top-world[...,1])*scale).astype(int),0,ph-1)
                    shown=(world[...,0]*side>=depth[sy,sx]-.31)&np.isfinite(depth[sy,sx])
                    coverage=(1-ease(radius*.65,radius*1.03,distance/(.52+.48*taper)))*taper*inside*shown
                    region=(slice(y0,y1+1),slice(x0,x1+1))
                    outline[region]=np.maximum(outline[region],coverage)
                    high[region]=np.maximum(high[region],(.56+.44*ease(-radius,radius,offset[...,1]))*coverage)
    return outline, high


def save(path, colors):
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(np.round(np.clip(colors,0,1)*255).astype(np.uint8)).save(path)


def apply(base, masks, accent, protection=None, role_colors=None):
    shape, lip=masks
    if protection is not None:
        shape=shape*(1-.93*ease(.025,.33,protection))
        lip=lip*(1-.93*ease(.025,.33,protection))
    value=base.max(axis=-1)
    chroma=value-base.min(axis=-1)
    bright_metal=ease(.43,.69,value)*(1-ease(.08,.20,chroma))
    if role_colors is not None:
        bright_metal*=ease(.025,.10,value-gaussian_filter(value,2.2))
    source=base if role_colors is None else role_colors
    existing_cord=ease(.15,.4,source[...,0]-np.maximum(source[...,1],source[...,2]))
    coverage=shape*(1-.81*bright_metal)*(1-.63*existing_cord)
    pigment=np.asarray(accent,dtype=np.float32)/255.
    material= pigment * (.80+.23*lip+.16*value)[...,None]
    return base*(1-coverage[...,None])+material*coverage[...,None]


def comparison(images, path):
    cols=len(images)
    w,h=340,295
    sheet=Image.new("RGB",(cols*w,2*h+62),"#111a25")
    pen=ImageDraw.Draw(sheet)
    big=ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf",23)
    text=ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf",14)
    pen.text((13,9),"Clan-colored hard-plate edging",font=big,fill="#e9f0fa")
    pen.text((13,41),"Fitted UV authoring views",font=text,fill="#b6c6db")
    for index,(name,pairs) in enumerate(images):
        for row,(caption,avatar) in enumerate(pairs):
            avatar.thumbnail((w-30,h-28),Image.Resampling.LANCZOS)
            x,y=index*w,row*h+62
            sheet.paste(avatar,(x+(w-avatar.width)//2,y+23))
            pen.text((x+13,y+2),f"{name} · {caption}",font=text,fill="#cddbf0")
    sheet.save(path)


def build(repo, work, destination, preview, items, shared):
    resource=repo/BASE
    sys.path.insert(0,str(repo/"tools"))
    from gear_palette import NATIVE_CLANS
    images=[]
    for item in items:
        verts,uv,faces=load_native_mesh(resource/f"{item}.mdl")
        view=projection(verts)
        l,t,s,w,h=view
        view=l,t,2*s,2*w,2*h
        forward, forward_uv=project(verts,uv,faces,view,1)
        back, back_uv=project(verts,uv,faces,view,-1)
        if item in ("A173","A110") and not shared:
            # Restore from the reviewed texture package to keep repeat exports deterministic.
            texture_path=Path("tex/crab")/f"trav_natsuko_{item}.png"
            inherited=work/"rivets-v1"/texture_path
            atlases=[(texture_path,inherited,(159,19,14))]
        else:
            atlases=[]
            for clan,palette in NATIVE_CLANS.items():
                rel=Path("tex")/clan/f"{item}.png"
                source=resource/rel
                if not source.is_file():
                    continue
                accent=tuple(round(.83*y+.17*z) for y,z in zip(palette[2],palette[4]))
                atlases.append((rel,source,accent))
            # Undyed neutral is a separate authored gear appearance, using its dark copper trim.
            default_path=Path("tex")/f"{item}_color_srgb.png"
            undyed=(181,131,68) if item.startswith("mitsue_soldier") else (156,111,62)
            atlases.append((default_path,resource/default_path,undyed))
        height,width=tex_array(atlases[0][1]).shape[:2]
        raw=masks(verts,uv,faces,view,{1:forward,-1:back},item,width,height)
        save(destination/"masks"/f"{item}-top-upper-sides.png",np.stack((*raw, np.zeros_like(raw[0])),axis=-1))
        guard_path=work/"rivets-v1/masks"/f"{item}-hard-plate-mask.png"
        protection=tex_array(guard_path)[...,1] if guard_path.exists() else None
        for rel, source, accent in atlases:
            before=tex_array(source)
            role_colors=tex_array(resource/"tex"/f"{item}_color_srgb.png") if shared else None
            after=apply(before,raw,accent,protection,role_colors)
            save(destination/rel,after)
            selected = item in {"A108","A141","A166","A160"} or len(items) <= 4
            if (not shared and item in ("A173","A110")) or (selected and (rel.parent.name=="dragon" or item.startswith("mitsue_soldier"))):
                images.append((f"{item} front", [
                    ("Before",draw_texture(before,forward,forward_uv)),
                    ("Upper-edge lacquer",draw_texture(after,forward,forward_uv))
                ]))
                if item=="A110" and not shared:
                    images.append((f"{item} rear", [
                        ("Before",draw_texture(before,back,back_uv)),
                        ("Upper-edge lacquer",draw_texture(after,back,back_uv))
                    ]))
    comparison(images,preview)


if __name__=="__main__":
    args=ArgumentParser(description=__doc__)
    args.add_argument("repository",type=Path)
    args.add_argument("working",type=Path)
    args.add_argument("destination",type=Path)
    args.add_argument("preview",type=Path)
    args.add_argument("items",nargs="+")
    args.add_argument("--shared",action="store_true")
    cfg=args.parse_args()
    build(cfg.repository,cfg.working,cfg.destination,cfg.preview,cfg.items,cfg.shared)

