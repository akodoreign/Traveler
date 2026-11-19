"""Original stylized human heads and UV-mapped locks for Traveler."""

import math
from functools import partial

import numpy as np


HEAD_WEIGHT = {"head": 1.}


def tint(rgb, factor, lift=0):
    return tuple(int(min(255, max(0, c*factor + lift))) for c in rgb)


def section(y, shape=""):
    """Continuous cap and tapered three-quarter profile in the existing rig space."""
    middle, radius = 108.4, 10.1
    t = (y-middle) / radius
    circle = math.sqrt(max(0., 1-t*t))
    chin = max(0., -t)
    cheek = math.exp(-((y-104.0)/3.3)**2)
    lower = {"round": .10, "wide": .10, "square": .14, "sharp": -.06, "long": -.035}.get(shape, .0)
    width = 7.8*circle*(1-.19*chin + lower*cheek)
    depth = 8.05*circle*(1-.18*chin)
    axis = .35 + 2.5*chin**2
    return depth, width, axis


def face_profile(spec, y, z, width):
    """A shallow socket, short nose and soft cheek volume, with no separate skin rims."""
    limit = 1. - (z / max(width, .01))**2
    if limit <= 0:
        return 0.
    u = abs(z)
    eye = -.30*math.exp(-((y-105.9)/1.43)**2 - ((u-3.6)/1.8)**2)
    cheek = .25*math.exp(-((y-103.7)/2.0)**2 - ((u-4.4)/2.25)**2)
    bridge = .57*math.exp(-((y-104.7)/2.1)**2 - (z/1.45)**2)
    nose = (1.08 if spec.get("kit", {}).get("nose") == "strong" else .81)
    nose *= math.exp(-((y-103.1)/.91)**2 - (z/1.10)**2)
    return (eye + cheek + bridge + nose)*min(1., limit*3.)


def projection(spec, y, z):
    d, w, center = section(y, spec.get("face"))
    angle = math.sqrt(max(0., 1 - (z/max(.01,w))**2))
    return center + angle*d + face_profile(spec, y, z, w)


def add_head(S, spec, ellipsoid):
    skin = tuple(spec["skin"])
    head = ellipsoid((0, 108.4, 0), (1, 10.1, 1), 80, 64)
    project = partial(projection, spec)
    for v in head[0]:
        d, w, center = section(v[1], spec.get("face"))
        rho = math.hypot(v[0],v[2])
        dx, dz = (v[0]/rho, v[2]/rho) if rho else (0., 0.)
        v[2] = w*dz
        v[0] = project(v[1],v[2]) if dx > 0 else center + dx*d
    prior_surface = S.surface
    if spec.get("face_albedo"):
        S.surface = "face"
    S.add(head, skin, HEAD_WEIGHT)
    S.surface = prior_surface
    part = S.parts

    def paint(points, rgb, depth, shades=None):
        """A projected, subdivided polygon that stays close to the sculpt."""
        points = np.asarray(points, dtype=float)
        n = len(points)
        center = points.mean(axis=0)
        site = [center, *(center + (point-center)*t for t in (.34,.67,1.) for point in points)]
        verts = [(project(y,z)+depth,y,z) for z,y in site]
        faces = [(0, k+1, (k+1)%n+1) for k in range(n)]
        for row in range(2):
            i=1+row*n
            faces.extend((i+k,i+(k+1)%n,i+(k+1)%n+n,i+k+n) for k in range(n))
        colours = [shades(sum(verts[i][1] for i in f)/len(f)) for f in faces] if shades else None
        S.add((verts, faces), rgb, HEAD_WEIGHT, colours=colours, part=part)

    kit = spec.get("kit", {})
    eye = kit.get("eye", spec.get("eyes"))
    aperture = {"half": .82, "narrow": .80, "old": .77, "round": 1.07, "wide": 1.12}.get(eye, 1.)
    model = spec.get("model_key")
    if model == "trav_natsuko":
        aperture = 1.04
    iris = tuple(spec.get("eye", (98, 62, 42)))
    brow = tint(tuple(spec["hair"]), .73)
    ink = (45, 30, 33)
    for side in (-1, 1):
        def on_side(points, colour, depth, shades=None):
            pts = [(side*z,y) for z,y in points]
            paint(pts if side > 0 else pts[::-1], colour, depth, shades)

        center = 105.84
        upper = [(1.48, 0.), (2.11, .73), (3.23, 1.10), (4.45, 1.12), (5.58, .59)]
        lower = [(5.30, -.43), (4.53, -.96), (3.42, -1.05), (2.26, -.72)]
        points = [(z, center+y*aperture) for z,y in upper+lower]
        on_side(points, (242, 225, 216), .055)
        iris_z = 3.57
        iris_y = center + .015
        contour = [(iris_z + 1.03*math.cos(a), iris_y+1.015*aperture*math.sin(a))
                   for a in np.linspace(0.,math.tau,16,endpoint=False)]
        on_side(contour, iris, .111, lambda h: tint(iris, .55 if h>center+.30 else 1.19 if h<center-.27 else .90,
                                                   13 if h<center-.27 else 0))
        on_side([(iris_z + .34*math.cos(a), iris_y + .42*math.sin(a))
                 for a in np.linspace(0.,math.tau,12,endpoint=False)], (31,23,26), .145)
        on_side([(3.16, center+.28), (3.23, center+.54), (3.52, center+.48), (3.48, center+.20)],
                (255,244,229), .177)
        for (za, ya), (zb, yb) in zip(upper, upper[1:]):
            on_side([(za,center+ya*aperture+.15), (zb,center+yb*aperture+.18),
                     (zb,center+yb*aperture-.12), (za,center+ya*aperture-.12)], ink, .173)
        brow_tilt = {"worried": -.25, "stern": .22}.get(kit.get("brow",spec.get("brow")),0.)
        on_side([(z,y + (z-3.5)*brow_tilt) for z,y in
                 ((1.74,108.05),(3.05,108.55),(4.46,108.57),(5.63,108.18),
                  (4.44,108.34),(3.05,108.32),(1.82,107.88))], brow, .076)
        ear = ellipsoid((.24,105.05,7.12*side), (1.06,1.8,1.), 16, 10)
        S.add(ear, skin, HEAD_WEIGHT)
        inset = ellipsoid((.44,105.03,7.90*side), (.49,.96,.19), 12, 8)
        S.add(inset, tint(skin,.83,5), HEAD_WEIGHT)

    expression = kit.get("mouth",spec.get("mouth"))
    corner = {"grin": .35, "smile": .18, "smirk": .10, "frown": -.13}.get(expression, .04)
    width = 1.54 if expression == "grin" else 1.18
    y = 101.39
    if not spec.get("face_albedo"):
        paint([(-width,y+corner),(-.40,y+.08),(.42,y+.08),(width,y+corner),
               (.61,y-.11),(0.,y-.21),(-.61,y-.11)], tint(skin,.69,8), .072)
    if expression == "grin":
        paint([(-.84,y+.16),(.89,y+.18),(.59,y-.045),(-.57,y-.06)], (231,205,185), .105)
    if model == "trav_natsuko":
        paint([(-1.22,104.28),(0.,104.14),(1.15,104.24),(.10,104.05)], tint(skin,.83,4), .07)
    if spec.get("scar"):
        paint([(4.92,104.38),(4.61,103.91),(3.49,102.65),(3.72,103.17)],
              tint(skin,.76,5), .074)
    if model == "trav_tamotsu":
        beard = tint(tuple(spec["hair"]),.57)
        for side in (-1,1):
            paint([(side*z,y) for z,y in ((.0,102.10),(1.30,102.17),(2.86,101.62),
                                          (1.2,101.60),(.0,101.80))], beard,.12)
            paint([(side*z,y) for z,y in ((2.17,101.81),(3.09,102.13),(2.43,100.14),
                                          (1.33,99.61),(.90,100.1))],beard,.13)
        paint([(-1.55,100.29),(1.55,100.29),(1.07,99.52),(.0,99.22),(-1.07,99.52)],beard,.12)
    return project


def hair_lock(S, centers, colour, weights):
    """Loft a curved lock along its own frame and map the texture root to tip."""
    n = 12
    controls = np.array([(*position,wide,depth) for position,wide,depth in centers])
    path, bone_weights = [], []
    for i, (p0, p1) in enumerate(zip(controls, controls[1:])):
        before = controls[max(0, i-1)]
        after = controls[min(len(controls)-1, i+2)]
        for t in (0., .2, .4, .6, .8):
            path.append(.5*((2*p0) + (-before+p1)*t
                           + (2*before-5*p0+4*p1-after)*t*t
                           + (-before+3*p0-3*p1+after)*t**3))
            if weights[i] == weights[i+1] or t == 0.:
                bone_weights.append(weights[i])
            else:
                bone_weights.append({bone: weights[i].get(bone,0.)*(1.-t)+weights[i+1].get(bone,0.)*t
                                     for bone in weights[i].keys() | weights[i+1].keys()})
    path.append(controls[-1])
    bone_weights.append(weights[-1])
    verts, uv = [], []
    side = np.array((0., 0., 1.))
    for i, row in enumerate(path):
        pos, wide, depth = row[:3], max(.06,row[3]), max(.06,row[4])
        t = path[min(i+1,len(path)-1)][:3]-path[max(0,i-1)][:3]
        t /= np.linalg.norm(t)
        cross = side-t*np.dot(side,t)
        side = cross/np.linalg.norm(cross)
        front = np.cross(t,side)
        for k in range(n):
            a = math.tau*k/n
            verts.append(pos+front*(depth*math.cos(a))+side*(wide*math.sin(a)))
            uv.append((k/n,1.-i/(len(path)-1)))
    faces, colours = [], []
    for row in range(len(path)-1):
        t=(row+.5)/(len(path)-1)
        for k in range(n):
            faces.append((row*n+k,row*n+(k+1)%n,(row+1)*n+(k+1)%n,(row+1)*n+k))
            glint = .20 if .24<t<.52 and k>=7 else .07 if k>=5 else 0.
            colours.append(tint(colour,.87+glint,6 if glint>.1 else 0))
    faces.extend((tuple(reversed(range(n))),tuple((len(path)-1)*n+k for k in range(n))))
    colours.extend((colour,colour))
    S.add((verts,faces),colour,[w for w in bone_weights for _ in range(n)],colours=colours,detail_uv=uv)


def write_lock_uv(mesh, face, layer, lock_uv):
    """Assign an authored root-to-tip map, unwrapping the seam per corner."""
    if lock_uv is None:
        return False
    corners = [lock_uv.data[mesh.loops[i].vertex_index].vector for i in face.loop_indices]
    if any(c[0] < 0. for c in corners):
        return False
    seam = max(c[0] for c in corners) - min(c[0] for c in corners) > .8
    for index, coord in zip(face.loop_indices, corners):
        layer.data[index].uv = coord[0] + (1. if seam and coord[0] < .2 else 0.), coord[1]
    return True


def add_hair(S, spec):
    style = spec.get("hairstyle", "short")
    if style == "bald":
        return
    colour = tuple(spec["hair"])
    S.surface = "hair"
    n = 48
    rows=14
    verts=[(-.56,121.35,0.)]
    for j in range(1,rows+1):
        t=j/rows
        for k in range(n):
            a=math.tau*k/n
            front=math.cos(a)
            front_lift = (2.15 if style == "chonmage" else 2.8*max(0.,front)**3)
            lip = 110.4 + front_lift - 7.8*max(0.,-front) - 1.8*(1-abs(front))
            latitude=math.acos((lip-109.7)/11.65)*t
            verts.append((-.55+10.0*math.sin(latitude)*front,109.7+11.65*math.cos(latitude),
                          9.06*math.sin(latitude)*math.sin(a)))
    faces=[(0,1+(k+1)%n,1+k) for k in range(n)]
    for j in range(rows-1):
        i=1+j*n
        faces.extend((i+k,i+(k+1)%n,i+(k+1)%n+n,i+k+n) for k in range(n))
    S.add((verts,faces),colour,HEAD_WEIGHT)

    if style != "chonmage":
        sweep = 3.05 if spec.get("bangs") in ("side", "swept") or spec.get("model_key") == "trav_natsuko" else 1.40
        for i,z in enumerate((-6.8,-4.1,-1.4,1.35,4.1,6.75)):
            low = 110.15 + ((2-i)*.60 if sweep>2 else .44*(i%3))
            tip = min(8.45,z+sweep)
            centers = [((2.2,118.6,z*.53),1.48,.72),
                       ((projection(spec,115.,z*.72)+1.06,115.,z*.76),1.68,.93),
                       ((projection(spec,low+1.82,z)+1.23,low+1.82,z+.60*sweep),1.23,.66),
                       ((projection(spec,low,tip)+.63,low,tip),.07,.13)]
            hair_lock(S,centers,colour,[HEAD_WEIGHT]*4)

    if style == "spiky":
        for z, reach in ((-2.9, .95), (1.1, 1.55)):
            centers = [((.9,118.7,z),1.04,.79),
                       ((-.79,120.6,z+reach*.38),1.08,.67),
                       ((-2.71,121.4,z+reach),.52,.37),
                       ((-3.86,121.0,z+reach*1.46),.07,.11)]
            hair_lock(S, centers, colour, [HEAD_WEIGHT]*4)

    lengths={"ponytail":91.,"long_topknot":85.,"long":76.,"mane":85.,"bob":98.}
    bottom=lengths.get(style,104.)
    if style not in ("chonmage","bun","ponytail","long_topknot"):
        for i,a in enumerate(np.linspace(.76,math.tau-.76,8)):
            x,z=math.cos(a),math.sin(a)
            y=bottom+(i%3)*1.7
            if style in ("short","spiky"):
                y+=max(0.,x)*2.4
            swing = .63 if i % 2 else -.58
            centers=[((3.6*x,114.,6.4*z),1.50,1.03),
                     ((7.2*x,108.8,9.10*z),1.91,1.29),
                     ((7.9*x-.8,y+5.7,9.45*z+swing),1.60,.92),
                     ((7.6*x-1.55,y,8.65*z+1.15*swing),.11,.16)]
            hair_lock(S,centers,colour,[HEAD_WEIGHT]*4)

    if style in ("ponytail","long_topknot","bun","chonmage"):
        y=bottom if style in ("ponytail","long_topknot") else 114.
        for i in (-1,0,1):
            centers=[((-5.7,116.8,i*.94),1.44,1.12),
                     ((-10.3,119.4,i*1.38),1.67,1.49),
                     ((-14.3,(y+117.)/2,i*1.88),1.50,1.24),
                     ((-12.45,y+i*.75,i*2.09),.10,.16)]
            tail={"tail":1.} if style in ("ponytail","long_topknot") else HEAD_WEIGHT
            hair_lock(S,centers,colour,[HEAD_WEIGHT,HEAD_WEIGHT,tail,tail])
    S.surface = ""
