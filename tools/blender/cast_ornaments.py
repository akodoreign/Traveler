"""Build skinned personal accessories and tattoo ribbons from a cast ornament job."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import chara3d as c
from chara3d_native import save_piece

BRASS = (195, 147, 70)
DARK = (74, 55, 43)


def line(s, path, radius, color, weights):
    s.add(c.tube([(p, radius, radius) for p in path], 8), color, weights)


def sash(s, spec, style):
    cord = tuple(spec.get("cord", spec.get("accent", (71, 73, 87))))
    w = c.torso_w()(67.)
    x = 10.7 + s.fit("torso")(67., 0.)
    for i in range(2 if style == "bells" else 1):
        z = 3.2 + i * 2.5
        y = 59.6 + i * 2.3
        end = (x + 2.6, y, z)
        line(s, [(x, 67.6, 1.2), (x + 1.5, 65.1, z), end], .28, cord, w)
        if style == "bells":
            rings = [((end[0], y+h, z), r, r) for h,r in
                     ((.38,.32), (.04,.75), (-.60,1.12), (-1.12,1.29), (-1.34,1.29))]
            s.add(c.tube(rings, 16, caps=False), BRASS, w)
            s.add(c.ellipsoid((end[0], y-1.39, z), (.39,.47,.39), 10, 6), DARK, w)
        elif style == "inro":
            s.add(c.tube([((end[0], y+h, z), .62, r) for h,r in
                          ((.5,.9),(.15,1.3),(-2.35,1.3),(-2.65,.92))], 12), (73,47,39), w)
            for h in (-.45,-1.28,-2.08):
                s.add(c.tube([((end[0],y+h+d,z),.66,1.32) for d in (0,.14)],12),BRASS,w)
        elif style == "gourd":
            for offset, radius in ((-.3, .85), (-1.85, 1.27)):
                s.add(c.ellipsoid((end[0], y+offset, z), (radius, radius*1.15, radius), 12, 8),
                      (155, 98, 52), w)
            line(s, [(end[0], y+.25, z), (end[0], y+1.15, z)], .34, DARK, w)
        elif style == "coin":
            # Square-holed kan coin, with the decorated face toward the viewer.
            verts = []
            for dx, radius in ((-.19, 1.55), (.19, 1.55), (.19, .6), (-.19, .6)):
                for k in range(16):
                    a = math.tau*k/16
                    u, v = math.cos(a), math.sin(a)
                    scale = radius if radius > 1 else radius/max(abs(u), abs(v))
                    verts.append((end[0]+dx, y-1.1+v*scale, z+u*scale))
            faces = [(ring*16+k, ring*16+(k+1)%16, ((ring+1)%4)*16+(k+1)%16,
                      ((ring+1)%4)*16+k) for ring in range(4) for k in range(16)]
            s.add((verts, faces), BRASS, w, smooth=False)
        else:
            s.add(c.ellipsoid(end,(.74,.68,.74),10,6),BRASS,w)
            for k in (-1,0,1):
                line(s,[(end[0],y-.45,z),(end[0]+.18,y-2.1,z+.28*k),
                        (end[0]+.23,y-3.65,z+.56*k)],.23,cord,w)


def tattoo(s, spec, style):
    color = tuple(spec.get("tattoo",(58,72,76)))
    relief = c.human_relief(spec,"arm")
    def surface(angle,y):
        depth, radius, x, z = c.profile(c.BODY["arm"],y)
        lift = relief(y,angle) + .20
        return (x+(depth*c.GIRTH["arm"]+lift)*math.cos(angle),y,
                z+(radius*c.GIRTH["arm"]+lift)*math.sin(angle))
    # Ink paths are drawn in surface-distance units so width is consistent around the arm.
    def on_arm(u, y):
        return surface(.14 + u / 3.45, y)

    paths = []
    if style == "reed":
        paths = [[(1.4,65.5),(3.8,69.2),(6.7,72.8)],
                 [(3.8,69.2),(3.2,71.2),(2.7,71.9)],
                 [(4.7,70.4),(6.7,70.6),(7.8,71.1)]]
    elif style == "lozenge":
        for x in (2.4, 5.7):
            paths.append([(x,67.2),(x+1.55,69.4),(x,71.6),(x-1.55,69.4),(x,67.2)])
    else:
        for j in range(2):
            path = []
            for k in range(41):
                t = k/40
                wave = math.sin(math.tau*t) if style == "tide" else 1-abs(4*t-2)
                path.append((9.2*t, 68.1+1.55*j+2.1*wave))
            paths.append(path)
    for path in paths:
        sampled = []
        for (u0,y0),(u1,y1) in zip(path,path[1:]):
            count = max(1, math.ceil(math.hypot(u1-u0,y1-y0)/.25))
            sampled.extend((u0+(u1-u0)*i/count,y0+(y1-y0)*i/count) for i in range(count))
        c.ink_stroke(s, sampled+[path[-1]], .28, color, on_arm, c.arm_w("N"))


def mask(s,spec):
    s.zoom=c.HEAD
    w={"head":1.}
    verts=[]
    for r in range(9):
        for i in range(29):
            a=(i/28-.5)*2.95
            y=104.95-1.05*abs(math.sin(a))-(r/8)*(5.68-2.4*abs(math.sin(a)))
            depth,width,axis=c.anime_head.section(y,spec.get("face"))
            z=width*math.sin(a)
            f=c.anime_head.projection(spec,y,z)
            ridge=.42+.30*(r in (1,4,7))
            verts.append((f+ridge*math.cos(a),y,z+ridge*math.sin(a)))
    faces=[(j,j+1,j+30,j+29) for j in range(8*29) if j%29!=28]
    plum=(65,47,58)
    s.add((verts,faces),plum,w,colours=[(106,53,64) if j//28==0 else plum for j in range(len(faces))])
    for side in (-1,1):
        depth, width, axis = c.anime_head.section(103.5, spec.get("face"))
        tie = []
        for i in range(25):
            a = 1.45 + (math.pi-1.45)*i/24
            tie.append((axis+(depth+.5)*math.cos(a),103.5+.35*i/24,
                        side*(width+.5)*math.sin(a)))
        line(s,tie,.31,plum,w)
    s.zoom=None


def costume(s, spec, role, head_only=False):
    colors = {
        "shinobi": ((54,36,61),(36,25,47),(148,52,76)),
        "maid": ((68,88,112),(43,60,83),(241,224,192)),
        "fox": ((36,103,70),(23,63,45),(221,159,72)),
        "soldier": ((93,59,131),(56,36,89),(197,133,69)),
    }
    top, lower, accent = colors[role]
    spec = dict(spec, top=top, lower=lower, accent=accent, cord=accent, collar=accent)
    if not head_only:
        c.kimono(s,spec,wide=role in ("fox","maid"))
        c.hakama(s,spec,short=role=="shinobi")
        c.obi(s,spec)
        c.footwear(s,spec)
    if role == "soldier" and head_only:
        c.helmet(s,dict(spec, iron_cap=True, armor=(91,80,99),band=accent))
    if role == "maid" and not head_only:
        # The apron falls forward from the obi and flares over the hakama.
        stations = [(46.,13.2,11.),(55.,13.8,9.5),(62.,13.4,7.5),(68.,11.8,6.4)]
        rings = [(y, *c.profile(stations, y)) for y in c.np.linspace(46,68,18)]
        width = 21
        verts = [(x-2*t*t+.37*c.math.cos(15*t)*(68-y)/22,y-.8*t*t,t*z)
                 for y,x,z in rings for t in c.np.linspace(-1,1,width)]
        faces = [(i,i+1,i+width+1,i+width) for i in range((len(rings)-1)*width) if i%width!=width-1]
        s.surface = "linen"
        s.add((verts,faces),accent,[c.torso_w()(y) for x,y,z in verts])
        s.surface = ""
    if role == "maid" and head_only:
        s.zoom=c.HEAD
        s.surface = "linen"
        s.add(c.ellipsoid((-2,118.4,0),(9.6,5.5,9.3),24,12),accent,{"head":1.})
        s.zoom=None
        s.surface = ""
    if role == "fox" and not head_only:
        tail = [((-6,65,0),1.6,1.7),((-10,60,2),2.6,2.7),((-14,54,4),3.8,3.5),
                ((-19,54,7),3.2,2.9),((-23,58,8),1.9,1.6),((-24,62,8),.15,.16)]
        fur=(161,81,42)
        s.add(c.tube(tail,16),fur,{"pelvis":1.},colours=[fur]*64+[(232,209,173)]*16+[fur,(232,209,173)])
    if role == "fox" and head_only:
        fur=(161,81,42)
        c.headband(s,dict(spec,band=(95,58,48)))
        s.zoom=c.HEAD
        for side in (-1,1):
            tip=(-1.4,122.,13.8*side)
            outer=[(4.3,117.,4.8*side),(3.2,113.,8.8*side),tip,(-3.,115.,6.8*side)]
            s.add((outer,[(0,1,2),(0,2,3),(1,3,2),(0,3,1)]),fur,{"head":1.})
            center=tuple(sum(v[i] for v in outer[:3])/3 for i in range(3))
            inset=[tuple(center[i]+.72*(v[i]-center[i])+(.12 if i==0 else 0)
                         for i in range(3)) for v in outer[:3]]
            s.add((inset,[(0,1,2)]),(223,162,135),{"head":1.})
        s.zoom=None


def main():
    folder=Path(sys.argv[sys.argv.index("--")+1])
    jobs=json.loads((folder/"job.json").read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig=c.make_armature(c.rest_frames())
    from head_surfaces import CLOTH_PATTERNS, HeadSurface, make_textures

    roles = {"cloth", "linen", "iron"}
    roles.update(entry["spec"].get("pattern") for entry in jobs.values() if entry["spec"].get("pattern") in CLOTH_PATTERNS)
    detail = HeadSurface(make_textures(folder / "tex", roles))
    for key,job in jobs.items():
        for role,style in job["parts"].items():
            s=c.Skin(job["spec"])
            if role=="ink": tattoo(s,job["spec"],style)
            elif role=="mask": mask(s,job["spec"])
            elif role=="sash": sash(s,job["spec"],style)
            else: costume(s,job["spec"],style,role.endswith("_head"))
            save_piece(bpy.context.scene,folder,rig,key+"_"+role,s,surface=detail if any(s.surfaces) else None)


if __name__=="__main__":
    main()

