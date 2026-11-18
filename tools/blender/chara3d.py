"""A real 3-D character: one skinned mesh on an armature, posed by the shared pose library.

Runs inside Blender:  blender -b --factory-startup --python tools/blender/chara3d.py -- job.json
job = {"spec": look, "family": weapon family, "out": folder, "size": [w, h], "origin": [x, y],
       "frames": [[kind, index, count, view], ...]}
Each frame is rendered three times at sprite resolution with no anti-aliasing: lit ("s"), flat
material colour ("a") and flat part id ("i"). tools/chara3d_sheet.py turns those into pixel art.

Character space matches tools/rig3d_poses.py: x forward, y up, z toward the camera side (N half);
one unit is one sprite pixel. Clothes, hair and weapons are separate pieces of the mesh, weighted to
the bones as they are built, so changing an outfit or adding a motion never needs new drawings.
"""
import json
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rig3d_poses as poses

EX, EY, EZ = np.eye(3)
SIDES = (("N", 1.), ("F", -1.))
# Rest skeleton: N-side joints (the F side mirrors z).
REST = dict(pelvis=(0, 60, 0), neck=(0, 97, 0), hip=(0, 58, 5.5), knee=(0, 31.5, 5.5), ankle=(0, 6, 5.5),
            sh=(0, 93, 11.5), elbow=(0, 76.5, 12.5), wrist=(0, 61.5, 13.2), grip=(0, 57.5, 13.4),
            tail=(-14.3, 119, 0))
HEAD = ((0, 97.5, 0), 1.3)                    # the head and everything on it, enlarged about the neck
GIRTH = dict(torso=1.15, leg=1.32, arm=1.38)
POLE_LEN = dict(tail=56., tip=62.)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def P(name, sign=1.):
    return np.array(REST[name], float) * (1, 1, sign)


def blender(p):
    return (float(p[0]), float(-p[2]), float(p[1]))


def frame(a, b, front):
    """Bone frame at a, pointing at b, with its z axis turned toward front."""
    y = unit(np.asarray(b, float) - a)
    z = front - y * (front @ y)
    if np.linalg.norm(z) < 1e-4:
        z = EY - y * (EY @ y)
    z = unit(z)
    return np.asarray(a, float), np.cross(y, z), y, z


def matrix(f):
    a, x, y, z = f
    m = Matrix.Identity(4)
    for column, axis in enumerate((x, y, z, a)):
        for row, value in enumerate(blender(axis)):
            m[row][column] = value
    return m


# ---------------------------------------------------------------------------------------------- geometry
def tube(rings, n=10, caps=True, pleats=None):
    """Loft elliptical rings (centre, half depth, half width) along their path; pleats = (count, depth) folds."""
    centres = [np.array(r[0], float) for r in rings]
    verts, faces, u = [], [], None
    for i, (c, rx, rz) in enumerate(rings):
        t = unit(centres[min(i + 1, len(rings) - 1)] - centres[max(i - 1, 0)])
        if u is None:
            u = EX if abs(t @ EX) < .7 else EY
        u = unit(u - t * (u @ t))
        w = np.cross(t, u)
        fold = (lambda a: 1 + pleats[1] * math.cos(pleats[0] * a)) if pleats else (lambda a: 1.)
        verts += [centres[i] + (u * rx * math.cos(a) + w * rz * math.sin(a)) * fold(a)
                  for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    for i in range(len(rings) - 1):
        faces += [(i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k) for k in range(n)]
    if caps:
        faces += [tuple(range(n)), tuple((len(rings) - 1) * n + k for k in range(n))]
    return verts, faces


def ellipsoid(centre, radii, n=12, m=8):
    verts = [np.array(centre, float) + (0, radii[1], 0)]
    for j in range(1, m):
        lat = math.pi * j / m
        verts += [np.array(centre, float) + (radii[0] * math.sin(lat) * math.cos(a), radii[1] * math.cos(lat),
                                             radii[2] * math.sin(lat) * math.sin(a))
                  for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
    verts.append(np.array(centre, float) - (0, radii[1], 0))
    faces = [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)]
    for j in range(m - 2):
        a, b = 1 + j * n, 1 + (j + 1) * n
        faces += [(a + k, b + k, b + (k + 1) % n, a + (k + 1) % n) for k in range(n)]
    last = len(verts) - 1
    faces += [(last, last - n + (k + 1) % n, last - n + k) for k in range(n)]
    return verts, faces


def box(centre, half, yaw=0.):
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    verts = []
    for dx in (-1, 1):
        for dy in (-1, 1):
            for dz in (-1, 1):
                x, z = dx * half[0], dz * half[2]
                verts.append(np.array(centre, float) + (x * c + z * s, dy * half[1], -x * s + z * c))
    return verts, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def profile(points, y):
    """Interpolate (y, half depth, half width[, x, z]) control points at height y."""
    points = sorted(points)
    ys = [p[0] for p in points]
    return [float(np.interp(y, ys, [p[i] for p in points])) for i in range(1, len(points[0]))]


class Skin:
    """Collects every piece of the character into one mesh with authored bone weights."""

    def __init__(self):
        self.verts, self.faces, self.colour, self.part, self.weights, self.smooth, self.parts = [], [], [], [], [], [], 0
        self.zoom = None                        # (pivot, factor) applied to pieces while set

    def add(self, shape, colour, weights, smooth=True, colours=None, paint=None):
        """paint(face centre) may return another colour for that face: detail is painted, not modelled."""
        verts, faces = shape
        if paint:
            colours = [paint(np.mean([verts[i] for i in face], axis=0)) or colour for face in faces]
        if self.zoom:
            verts = [np.asarray(self.zoom[0], float) + (v - self.zoom[0]) * self.zoom[1] for v in verts]
        base = len(self.verts)
        self.parts += 1
        self.verts += verts
        self.weights += weights if isinstance(weights, list) else [weights] * len(verts)
        for i, face in enumerate(faces):
            self.faces.append(tuple(base + k for k in face))
            self.colour.append(colours[i] if colours else colour)
            self.part.append(self.parts)
            self.smooth.append(smooth)

    def loft(self, points, colour, weight, z=0., n=10, band=None, x=0., pleats=None):
        """A vertical tube through (y, half depth, half width) control points.
        weight(y) gives the bone weights at a height; band = (step, [colours]) stripes it horizontally."""
        ys = sorted(p[0] for p in points)
        if band:
            ys = list(np.arange(ys[0], ys[-1], band[0])) + [ys[-1]]
        rings = []
        for y in ys:
            v = profile(points, y)
            rings.append(((v[2], y, v[3]) if len(v) > 2 else (x, y, z), v[0], v[1]))
        verts, faces = tube(rings, n, pleats=pleats)
        colours = None
        if band:
            pick = band[1] if callable(band[1]) else (lambda row, k: band[1][row % len(band[1])])
            colours = [pick(i, k) for i in range(len(ys) - 1) for k in range(n)] + [colour, colour]
        self.add((verts, faces), colour, [weight(y) for y in ys for _ in range(n)], colours=colours)

    def build(self, armature):
        mesh = bpy.data.meshes.new("skin")
        mesh.from_pydata([blender(v) for v in self.verts], [], self.faces)
        palette = sorted(set(self.colour))
        for rgb in palette:
            material = bpy.data.materials.new("c%02x%02x%02x" % rgb)
            material.diffuse_color = [(c / 255) ** 2.2 for c in rgb] + [1]
            mesh.materials.append(material)
        mesh.polygons.foreach_set("material_index", [palette.index(c) for c in self.colour])
        ids = mesh.color_attributes.new("part", "BYTE_COLOR", "CORNER")
        loops = [((p * 53) % 16 / 16 + .03, (p * 29) % 16 / 16 + .03, (p * 11) % 16 / 16 + .03, 1.)
                 for p, face in zip(self.part, self.faces) for _ in face]
        ids.data.foreach_set("color", [c for loop in loops for c in loop])
        mesh.color_attributes.active_color = ids
        mesh.polygons.foreach_set("use_smooth", self.smooth)
        fix = bmesh.new()
        fix.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(fix, faces=fix.faces)
        fix.to_mesh(mesh)
        fix.free()
        obj = bpy.data.objects.new("skin", mesh)
        bpy.context.scene.collection.objects.link(obj)
        groups = {}
        for index, weights in enumerate(self.weights):
            for bone, value in weights.items():
                groups.setdefault(bone, obj.vertex_groups.new(name=bone)) if bone not in groups else None
                groups[bone].add([index], value, "REPLACE")
        obj.modifiers.new("armature", "ARMATURE").object = armature
        return obj
# ------------------------------------------------------------------------------------------------- body
# (y, half depth, half width[, x, z]) of the bare body; clothes are the same sections grown outward.
BODY = dict(
    torso=[(55, 5.4, 8.6), (62, 5.2, 8.0), (70, 4.6, 6.8), (84, 5.6, 9.0), (92, 4.8, 10.6), (96, 2.8, 4.4)],
    leg=[(61, 5.0, 4.6, 0, 5.2), (46, 4.6, 4.2, 0, 5.5), (31.5, 3.5, 3.3, 0, 5.5), (27, 3.3, 3.1, -.3, 5.5),
         (17, 3.5, 3.2, -.6, 5.5), (8, 2.4, 2.3, 0, 5.5), (5, 2.4, 2.3, 0, 5.5)],
    arm=[(95, 3.0, 2.6, 0, 10.6), (90, 3.1, 2.9, 0, 11.9), (78, 2.7, 2.6, 0, 12.5), (74, 2.6, 2.5, 0, 12.7),
         (67, 2.5, 2.4, 0, 13), (61, 1.9, 1.8, 0, 13.2)])
WHITE, STRAW, INK, WOOD, STEEL = (236, 232, 222), (196, 168, 108), (44, 36, 44), (140, 94, 54), (206, 214, 226)


def blend(*stops):
    """Bone weights by height: (y, bone) stops, blended linearly between neighbours."""
    def weight(y):
        for (y0, b0), (y1, b1) in zip(stops, stops[1:]):
            if y <= y1 or y1 == stops[-1][0]:
                t = min(1., max(0., (y - y0) / (y1 - y0)))
                return {b0: 1.} if b0 == b1 or t <= 0 else {b1: 1.} if t >= 1 else {b0: 1 - t, b1: t}
    return weight


def torso_w():
    return blend((55, "pelvis"), (63, "pelvis"), (80, "spine"), (97, "spine"))


def leg_w(s):
    return blend((5, "foot" + s), (9, "shin" + s), (28, "shin" + s), (35, "thigh" + s), (52, "thigh" + s), (61, "pelvis"))


def arm_w(s):
    return blend((57, "hand" + s), (63, "fore" + s), (74, "fore" + s), (79, "upper" + s), (91, "upper" + s), (96, "spine"))


def cover(name, y0, y1, grow, sign=1., flare=0.):
    """The body section between two heights, grown outward (flare widens the lower end)."""
    out = []
    for y in list(np.arange(y0, y1, 3.)) + [y1]:
        v, t = profile(BODY[name], y), (y1 - y) / (y1 - y0)
        g = GIRTH[name]
        out.append((y, v[0] * g + grow + flare * t, v[1] * g + grow + flare * t)
                   + ((v[2], v[3] * sign) if len(v) > 2 else ()))
    return out


HEAD_C, HEAD_R = (.8, 108.5, 0.), (8.2, 10.2, 7.6)
SAYA_AT = (6., 4., 11.5)                        # scabbard mouth, from the pelvis


def face_x(y, z):
    """Forward surface of the egg-shaped head at a height and a sideways offset."""
    t = max(0., (HEAD_C[1] - y) / HEAD_R[1])
    r = math.sqrt(max(0., 1 - ((y - HEAD_C[1]) / HEAD_R[1]) ** 2))
    wide = max(HEAD_R[2] * (1 - .5 * t ** 1.5) * r, .1)
    return HEAD_C[0] + HEAD_R[0] * (1 - .3 * t ** 1.5) * r * math.sqrt(max(0., 1 - (z / wide) ** 2)) + 1.2 * t


def strand(S, colour, points, radius, bone="head"):
    """A tapering lock of hair through the given points."""
    last = len(points) - 1
    S.add(tube([(p, radius * (1 - .85 * i / last), radius * .8 * (1 - .85 * i / last)) for i, p in enumerate(points)], 6),
          colour, {bone: 1.})


def trim(spec):
    """Metal trim colour; some looks use "trim" for a material name instead."""
    value = spec.get("trim")
    return tuple(value) if isinstance(value, (list, tuple)) else (214, 188, 88)


def shade(colour, f, lift=0):
    return tuple(max(0, min(255, int(c * f + lift))) for c in colour)


def body(S, spec):
    """The bare figure: skin, a loincloth, a chest wrap and wrist and ankle wraps."""
    skin, h = tuple(spec["skin"]), {"head": 1.}
    S.loft(cover("torso", 55, 96, 0), skin, torso_w(), n=12)
    S.loft(cover("torso", 55, 64, .5), WHITE, torso_w(), n=12)
    if spec.get("female") or spec.get("wrap"):
        S.loft(cover("torso", 79, 90, .5), WHITE, torso_w(), n=12)
    S.loft([(94, 2.8, 2.8), (101, 2.6, 2.6)], skin, blend((94, "spine"), (101, "head")), n=8)
    S.zoom = HEAD
    head = ellipsoid(HEAD_C, HEAD_R, 16, 12)
    for v in head[0]:                           # an egg: full cranium, narrow jaw, the chin a little forward
        t = max(0., (HEAD_C[1] - v[1]) / HEAD_R[1])
        v[0] = HEAD_C[0] + (v[0] - HEAD_C[0]) * (1 - .3 * t ** 1.5) + 1.2 * t
        v[2] *= 1 - .5 * t ** 1.5
    S.add(head, skin, h)
    eye, hair = tuple(spec.get("eye", (60, 44, 40))), tuple(spec["hair"])
    for _, sg in SIDES:
        z = 3.9 * sg
        x = face_x(105.2, z)
        S.add(ellipsoid((x - .1, 105.1, z), (.7, 2.2, 1.7), 8, 6), eye, h)                       # iris
        S.add(ellipsoid((x + .15, 107.0, z), (.8, .85, 2.05), 8, 4), INK, h)                     # lid and lashes
        S.add(ellipsoid((x + .45, 105.3, z), (.4, 1.05, .8), 6, 4), INK, h)                      # pupil
        S.add(box((x + .95, 106.0, z + .75), (.25, .5, .45)), WHITE, h, smooth=False)            # catch-light
        S.add(box((face_x(109.8, z) + .1, 109.8, z), (.5, .3, 2.1)), hair, h, smooth=False)      # brow
        S.add(ellipsoid((.5, 105.5, 7.4 * sg), (1.4, 2.3, 1.1), 6, 4), skin, h)                  # ear
    S.add(ellipsoid((face_x(103.1, 0) + .1, 103.1, 0), (.9, .8, .8), 6, 4), skin, h)             # nose
    S.add(box((face_x(100.8, 0) + .15, 100.8, 0), (.35, .25, 1.1)), shade(skin, .68), h, smooth=False)
    S.zoom = None
    for s, sg in SIDES:
        S.loft(cover("leg", 5, 61, 0, sg), skin, leg_w(s))
        S.loft(cover("leg", 6, 13, .35, sg), WHITE, leg_w(s))
        S.add(ellipsoid((3., 2.9, 5.5 * sg), (6.8, 3., 3.4), 10, 6), skin, {"foot" + s: 1.})
        S.loft(cover("arm", 61, 95, 0, sg), skin, arm_w(s), n=8)
        S.loft(cover("arm", 61.5, 66, .3, sg), WHITE, arm_w(s), n=8)
        S.add(ellipsoid((.3, 58.4, 13.4 * sg), (2.7, 3.6, 2.1), 8, 6), skin, {"hand" + s: 1.})


def hair(S, spec):
    """Hair is a full mass around the skull with locks over it; a painted band of sheen keeps it from going flat."""
    style, colour, h = spec.get("hairstyle", "short"), tuple(spec["hair"]), {"head": 1.}
    if style == "bald":
        return
    sheen = shade(colour, 1.4, 22)
    S.zoom = HEAD
    cap = ellipsoid((-.3, 109.6, 0), (10.2, 11.7, 9.9), 20, 14)
    keep = [f for f in cap[1] if not (np.mean([cap[0][i][0] for i in f]) > 2.8 and np.mean([cap[0][i][1] for i in f]) < 112.5
                                      and abs(np.mean([cap[0][i][2] for i in f])) < 7.6)]
    S.add((cap[0], keep), colour, h, paint=lambda c: sheen if 115.6 < c[1] < 117.7 and c[0] > -7.5 else None)
    S.add(ellipsoid((-5., 106., 0), (7.2, 9.6, 10.2), 14, 10), colour, h)                       # mass behind the head
    for i, z in enumerate((-7., -4.2, -1.4, 1.4, 4.2, 7.)):                  # a jagged fringe
        low = 109.6 + (i % 2) * 1.7 - (abs(z) > 5) * 2.2
        strand(S, colour, [(6.5, 118., z * .8), (face_x(113.5, z * .9) + 2.2, 113.5, z),
                           (face_x(low, z * .9) + 1.6, low, z * 1.05)], 2.8)
    for _, sg in SIDES:                                                     # locks in front of the ears
        strand(S, colour, [(3.5, 113, 9. * sg), (5., 105, 9.3 * sg), (5.4, 96.5, 8.2 * sg)], 2.5)
    if style in ("spiky", "short", "mane"):
        for i in range(14):                                                 # tufts break up the outline
            a, tilt = 2 * math.pi * (i * .618 % 1), .3 + .75 * ((i * 7) % 5) / 4
            out = np.array((math.cos(a) * math.sin(tilt), math.cos(tilt), math.sin(a) * math.sin(tilt)))
            base = np.array((-.3, 109.6, 0)) + out * (9.2, 10.6, 8.9)
            strand(S, colour, [base - out * 1.5, base + out * 3 - (1, 0, 0), base + out * 7 - (2.5, .5, 0)], 3.2)
    if style in ("ponytail", "long_topknot", "chonmage", "bun"):
        rings = {"ponytail": [((-8, 114, 0), 2.6, 2.6), ((-12.5, 117, 0), 3.6, 3.4), ((-15.5, 112, 0), 4., 3.8),
                              ((-16.5, 102, 0), 3.6, 3.4), ((-15.5, 93, 0), 2.6, 2.4), ((-14.6, 86, 0), .8, .7)],
                 "long_topknot": [((-8, 114, 0), 2.4, 2.4), ((-12.5, 117, 0), 3.1, 2.9), ((-15.5, 109, 0), 3., 2.8),
                                  ((-15.5, 92, 0), 2.3, 2.1), ((-14.6, 80, 0), .7, .6)],
                 "chonmage": [((-5, 119.5, 0), 2., 2.), ((-1, 122, 0), 2.1, 1.9), ((4.5, 121.5, 0), 1.4, 1.3)],
                 "bun": [((-8, 115, 0), 2.2, 2.2), ((-12, 117.5, 0), 4., 3.8), ((-15, 118.5, 0), 1.8, 1.8)]}[style]
        hang = style in ("ponytail", "long_topknot")
        S.add(tube(rings, 10), colour, [h if i < 2 or not hang else {"tail": 1.}
                                        for i in range(len(rings)) for _ in range(10)],
              paint=lambda c: sheen if hang and 104 < c[1] < 108 else None)
    if style in ("long", "mane", "bob"):
        bottom = {"long": 78, "mane": 88, "bob": 99}[style]
        S.loft([(bottom, 3.4, 9., -7.5, 0), (100, 4.6, 10.2, -7., 0), (112, 3.6, 9.4, -6., 0)], colour,
               blend((bottom, "tail" if style == "long" else "head"), (104, "head"), (112, "head")), n=14,
               pleats=(5, .08))
    S.zoom = None


# ------------------------------------------------------------------------------------------------ outfit
def skirt_w(v):
    near, lower = min(1., max(0., v[2] / 6 + .5)), min(1., max(0., (40 - v[1]) / 12))
    hip = min(1., max(0., (v[1] - 46) / 10))
    w = {"pelvis": hip, "thighN": near * (1 - lower) * (1 - hip), "shinN": near * lower * (1 - hip),
         "thighF": (1 - near) * (1 - lower) * (1 - hip), "shinF": (1 - near) * lower * (1 - hip)}
    return {k: x for k, x in w.items() if x > .01}


def skirt(S, colour, top, bottom, grow, flare, pleats=None, hem=None, motif=None):
    """A garment around both legs: it hangs from the hips and each half follows its own leg.
    Folds, the hem and a woven crest pattern are painted on its faces."""
    def radii(y):
        v, t = profile(BODY["torso"], max(y, 55.)), (top - y) / (top - bottom)
        return v[0] * GIRTH["torso"] + grow + flare * t, v[1] * GIRTH["torso"] + grow + flare * t

    n, ys = 36, list(np.arange(bottom, top, 1.6)) + [top]
    verts, faces = tube([((0, y, 0), *radii(y)) for y in ys], n, pleats=pleats)
    spots = [(2 * math.pi * (i * .618 % 1), bottom + 6 + (top - bottom - 16) * ((i * 5) % 7) / 6)
             for i in range(10 if motif else 0)]
    fold = shade(colour, .72)

    def paint(row, k):
        a, y = 2 * math.pi * (k + .5) / n, (ys[row] + ys[row + 1]) / 2
        if hem and y < bottom + 2.8:
            return hem
        for at, height in spots:                # a crest: a dot inside a ring
            d = math.hypot(((a - at + math.pi) % (2 * math.pi) - math.pi) * radii(y)[1], y - height)
            if d < 1.1 or 2.3 < d < 3.7:
                return motif
        return fold if pleats and math.cos(pleats[0] * a) < -.72 else colour

    S.add((verts, faces), colour, [skirt_w(v) for v in verts],
          colours=[paint(i, k) for i in range(len(ys) - 1) for k in range(n)] + [colour, colour])


def kimono(S, spec, wide=False):
    """Upper garment: body, crossed collar and sleeves (wide hanging ones, or elbow-length ones under armour)."""
    top, collar = tuple(spec["top"]), tuple(spec.get("collar", WHITE))
    motif = tuple(spec["pcol"]) if wide and spec.get("pattern") and spec.get("pcol") else None
    S.loft(cover("torso", 62, 96, .9), top, torso_w(), n=12)
    for s, sg in SIDES:
        S.add(tube([((3.6, 95.5, 3.6 * sg), 1.1, 1.4), ((7.9, 87, 1.3 * sg), 1.1, 1.6), ((8.1, 78, -1.3 * sg), 1.1, 1.6)], 6),
              collar, {"spine": 1.})
        if wide:
            def crest(row, k, sg=sg):           # crests scattered down the sleeve
                return motif if motif and (row * 3 + k * 5) % 11 == 0 and row > 1 else top
            S.loft(cover("arm", 63, 93.5, .5, sg, flare=5.), top, arm_w(s), n=12, pleats=(3, .07), band=(2.2, crest))
            S.add(box((-1.5, 63., 13.2 * sg), (7., 8., 1.7)), top, {"fore" + s: 1.}, smooth=False)   # the hanging pocket
            S.loft(cover("arm", 62.5, 65, 5., sg), collar, arm_w(s), n=12)
        else:
            S.loft(cover("arm", 73, 93.5, 1.6, sg, flare=3.), top, arm_w(s), n=12, pleats=(4, .08))
            S.loft(cover("arm", 72.4, 74.4, 4.7, sg), tuple(spec["accent"]), arm_w(s), n=12)          # cuff trim


def hakama(S, spec, short=False):
    """Pleated trousers: a knee-length divided skirt over leggings, or full length to the ankle."""
    lower = tuple(spec["lower"])
    if short:
        skirt(S, lower, 66, 27, 1.5, 8., pleats=(9, .1), hem=tuple(spec["accent"]))
        for s, sg in SIDES:
            S.loft(cover("leg", 8, 40, .5, sg), shade(lower, .8), leg_w(s))
    else:
        fold = shade(lower, .72)
        for s, sg in SIDES:
            S.loft(cover("leg", 9, 50, 1.8, sg, flare=4.), lower, leg_w(s), n=16, pleats=(4, .1),
                   band=(2., lambda row, k: fold if k % 4 == 2 else lower))


def coat(S, spec):
    """The long skirt of a kimono, worn over the hakama."""
    skirt(S, tuple(spec["top"]), 66, 21, 2.7, 6.5, pleats=(7, .09), hem=tuple(spec["accent"]),
          motif=tuple(spec["pcol"]) if spec.get("pattern") and spec.get("pcol") else None)


def obi(S, spec):
    accent, gold = tuple(spec["accent"]), trim(spec)
    S.loft(cover("torso", 64, 70.5, 2.6), accent, torso_w(), n=12)
    S.add(ellipsoid((9.6, 67.2, 0), (1.3, 2.2, 3.), 8, 5), accent, {"pelvis": .5, "spine": .5})       # the knot
    for z in (-1.5, 1.5):                                                   # cords and tassels
        S.add(box((10., 60, z), (.6, 5.5, .7)), accent, {"pelvis": 1.}, smooth=False)
        S.add(box((10., 53.4, z), (.8, 1.3, 1.)), gold, {"pelvis": 1.}, smooth=False)


def armour(S, spec):
    """Lamellar: rows of small plates laced together, over the kimono."""
    plate, lace = tuple(spec["armor"]), tuple(spec.get("lace", spec["accent"]))
    gold, gap, cloth = trim(spec), shade(plate, .6), shade(tuple(spec["top"]), .62)

    def lamellar(row, k):
        return (lace if k % 2 else gap) if row % 4 == 3 else plate

    S.loft(cover("torso", 70, 92, 2.3), plate, torso_w(), n=24, band=(1.1, lamellar))
    S.loft(cover("torso", 91.2, 92.8, 2.6), gold, torso_w(), n=24)
    S.add(ellipsoid((9.6, 85, 0), (.9, 1.5, 1.7), 6, 4), lace, {"spine": 1.})                    # chest cord and tassel
    for z in (-.9, .9):
        S.add(box((9.6, 81.2, z), (.45, 2.6, .55)), lace, {"spine": 1.}, smooth=False)
    for angle, bone in ((35, "thighN"), (-35, "thighF"), (95, "thighN"), (-95, "thighF"), (150, "thighN"), (-150, "thighF")):
        a = math.radians(angle)                                             # kusazuri: panels hung from the waist
        for i, y in enumerate((61.5, 56., 50.5)):
            centre = ((11.8 + i * 1.3) * math.cos(a), (15.6 + i * 1.3) * math.sin(a))
            w = {"pelvis": .5, bone: .5}
            S.add(box((centre[0], y, centre[1]), (1.1, 2.4, 4.8), yaw=90 - angle), plate, w, smooth=False)
            S.add(box((centre[0], y - 2.6, centre[1]), (1.2, .5, 4.9), yaw=90 - angle), gold if i == 2 else lace, w, smooth=False)
    for s, sg in SIDES:
        for i in range(4):                                                  # sode: layered shoulder plates
            S.add(box((0, 94.5 - i * 3., (19.5 + i * .7) * sg), (6.8, 1.4, 1.4)), plate, {"upper" + s: 1.}, smooth=False)
            S.add(box((0, 92.9 - i * 3., (19.6 + i * .7) * sg), (6.9, .4, 1.5)), gold if i == 3 else lace,
                  {"upper" + s: 1.}, smooth=False)
        S.loft(cover("arm", 62, 73, 1., sg), cloth, arm_w(s), n=8,           # kote: splints on a cloth sleeve
               band=(1.4, lambda row, k: lace if row % 4 == 3 else plate if k % 2 else cloth))
        S.loft(cover("leg", 8, 30, 1.2, sg), cloth, leg_w(s),               # suneate: a shin plate on dark leggings
               band=(1.6, lambda row, k: (lace if row % 5 == 4 else plate) if k in (8, 9, 0, 1) else cloth))


def footwear(S, spec, tabi=WHITE):
    for s, sg in SIDES:
        S.add(ellipsoid((3.1, 3.2, 5.5 * sg), (7.3, 3.4, 3.9), 10, 6), tabi, {"foot" + s: 1.})
        S.add(box((3.1, .7, 5.5 * sg), (7.9, .8, 4.3)), STRAW, {"foot" + s: 1.}, smooth=False)
        for x in (2.6, 5.4):
            S.add(box((x, 4.9, 5.5 * sg), (.7, 2., 4.)), tuple(spec["accent"]), {"foot" + s: 1.}, smooth=False)


def headband(S, spec):
    band = tuple(spec.get("band", spec["accent"]))
    S.zoom = HEAD
    S.add(tube([((-.3, 111.2, 0), 10.75, 10.4), ((-.3, 114., 0), 10.6, 10.25)], 20, caps=False), band, {"head": 1.})
    S.add(ellipsoid((-11.3, 112.6, 0), (1.4, 1.6, 1.9), 6, 4), band, {"head": 1.})               # the knot
    for z, low in ((-1.4, 99.), (1.4, 101.5)):                              # ribbon tails
        strand(S, band, [(-11.5, 112, z), (-14.5, 108, z * 1.6), (-16., low, z * 2.2)], 1.7, "tail")
    S.zoom = None


def weapon(S, spec, kind):
    """Weapons are their own pieces on the weapon bone: grip at the bone's origin, pointing along it."""
    w = {"weapon": 1.}
    if kind in ("yari", "naginata", "bo", "shakujo"):
        S.add(tube([((0, -POLE_LEN["tail"], 0), 1., 1.), ((0, 49, 0), 1., 1.)], 6), WOOD, w)
        if kind == "yari":
            S.add(ellipsoid((0, 47, 0), (1.9, 2.2, 1.9), 8, 5), tuple(spec["accent"]), w)
            S.add(tube([((0, 48, 0), 1.1, .7), ((0, 52, 0), 2.4, .8), ((0, 62, 0), .2, .2)], 6), STEEL, w)
        elif kind == "naginata":
            S.add(tube([((0, 48, 0), 1.2, .7), ((.8, 56, 0), 2.6, .7), ((3., 64, 0), .2, .2)], 6), STEEL, w)
        else:
            S.add(ellipsoid((0, 50, 0), (1.5, 1.5, 1.5), 8, 5), tuple(spec["accent"]), w)
    elif kind == "yumi":                                                    # limbs curve back toward the archer
        ys = np.linspace(-22, 30, 9)
        S.add(tube([((6 * (y / 30) ** 2, y, 0), .9, .7) for y in ys], 6), WOOD, w)
        S.add(tube([((6 * (22 / 30) ** 2, -22, 0), .25, .25), ((6., 30, 0), .25, .25)], 4), WHITE, w)
        S.add(tube([((0, -2.5, 0), 1.2, 1.), ((0, 2.5, 0), 1.2, 1.)], 6), tuple(spec["accent"]), w)
    elif kind == "tetsubo":
        S.add(tube([((0, -9, 0), 1., 1.), ((0, 6, 0), 1.2, 1.2), ((0, 34, 0), 2.7, 2.7)], 8), (112, 116, 126), w,
              paint=lambda c: STEEL if c[1] > 8 and int(c[1]) % 5 == 0 else None)
    elif kind in ("katana", "tanto"):
        length, gold = 37 if kind == "katana" else 15, trim(spec)

        def sword(bone, at, d, blade):
            at, d = np.asarray(at, float), unit(np.asarray(d, float))
            S.add(tube([(at - d * (7 if kind == "katana" else 4), 1., .8), (at + d * 2, 1., .8)], 6), INK, {bone: 1.})
            S.add(ellipsoid(at + d * 2.6, (1.9, 1.9, 1.9), 8, 4), gold, {bone: 1.})
            if blade:
                S.add(tube([(at + d * 3, 1.2, .5), (at + d * length * .65, 1.1, .45), (at + d * length, .2, .2)], 6),
                      STEEL, {bone: 1.})

        sword("weapon", (0, 0, 0), EY, True)                                # in the hand
        mouth, sheath = P("pelvis") + SAYA_AT, unit(np.asarray(poses.SAYA_DIR, float))
        S.add(tube([(mouth, 1.5, 1.1), (mouth + sheath * (length - 3), 1.3, 1.)], 6), INK, {"pelvis": 1.})
        S.add(ellipsoid(mouth + sheath * (length - 3), (1.5, 1.5, 1.5), 6, 4), gold, {"pelvis": 1.})
        sword("sheathed", mouth - sheath * 3, -sheath, False)               # the hilt, while the blade is put away


OUTFITS = {
    "bare": [],
    "armored": [kimono, lambda S, spec: hakama(S, spec, True), obi, armour, lambda S, spec: footwear(S, spec, INK)],
    "robe": [lambda S, spec: kimono(S, spec, True), hakama, coat, obi, footwear],
}


def build_character(spec, outfit=None, arms=None):
    S = Skin()
    body(S, spec)
    build = spec.get("build", "normal")
    for piece in OUTFITS[outfit or ("armored" if build.startswith("armored") or build == "heavy" else "robe")]:
        piece(S, spec)
    hair(S, spec)
    if spec.get("head") == "hachimaki":
        headband(S, spec)
    weapon(S, spec, arms or spec.get("weapon", "none"))
    return S


# --------------------------------------------------------------------------------------------------- rig
THIGH, SHIN = float(np.linalg.norm(P("hip") - P("knee"))), float(np.linalg.norm(P("knee") - P("ankle")))
UPPER, FORE = float(np.linalg.norm(P("sh") - P("elbow"))), float(np.linalg.norm(P("elbow") - P("wrist")))
HAND, L = float(np.linalg.norm(P("wrist") - P("grip"))), THIGH + SHIN


def rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1.)))


def ry(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array(((c, 0, -s), (0, 1., 0), (s, 0, c)))


def rx(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array(((1., 0, 0), (0, c, -s), (0, s, c)))


def ik(a, target, l1, l2, pole):
    d = target - a
    dist = np.linalg.norm(d)
    u = d / dist if dist > 1e-6 else -EY
    reach = float(np.clip(dist, abs(l1 - l2) + .05, l1 + l2 - .05))
    along = (l1 * l1 - l2 * l2 + reach * reach) / (2 * reach)
    side = pole - u * (pole @ u)
    if np.linalg.norm(side) < 1e-6:
        side = np.cross(u, EZ)
    return a + u * along + unit(side) * math.sqrt(max(0., l1 * l1 - along * along)), a + u * reach


def rest_frames():
    frames = {"pelvis": frame(P("pelvis"), P("pelvis") + EY, EX), "spine": frame(P("pelvis"), P("neck"), EX),
              "head": frame(P("neck"), P("neck") + EY, EX), "tail": frame(P("tail"), P("tail") - EY, EX),
              "weapon": frame(np.zeros(3), EY, EX), "sheathed": frame(P("pelvis"), P("pelvis") + EY, EX)}
    for s, sg in SIDES:
        frames.update({"thigh" + s: frame(P("hip", sg), P("knee", sg), EX),
                       "shin" + s: frame(P("knee", sg), P("ankle", sg), EX),
                       "foot" + s: frame(P("ankle", sg), P("ankle", sg) + EX, EY),
                       "upper" + s: frame(P("sh", sg), P("elbow", sg), EX),
                       "fore" + s: frame(P("elbow", sg), P("wrist", sg), EX),
                       "hand" + s: frame(P("wrist", sg), P("grip", sg), EX)})
    return frames


def make_armature(frames):
    data = bpy.data.armatures.new("rig")
    rig = bpy.data.objects.new("rig", data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name, f in frames.items():              # unparented bones: each is placed directly from the solved joints
        bone = data.edit_bones.new(name)
        bone.head, bone.tail = blender(f[0]), blender(f[0] + f[2] * 8)
        bone.matrix = matrix(f)
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


def solve(c):
    """Joint positions for one set of pose controls: planted feet, fixed bone lengths, hands on targets."""
    R = rz(-c["lean"]) @ ry(c["twist"]) @ rx(c["bend"])
    pelvis = P("pelvis") + np.asarray(c["root"], float) * L
    feet, J = {}, {}
    for s, sg in SIDES:
        x, y, z = c["feet"][s][:3]
        base = P("hip", sg) - P("pelvis")
        feet[s] = np.array((base[0] + x * L, REST["ankle"][1] + y * L, base[2] + z * L))
        if s in c["kick"]:
            continue
        reach = (THIGH + SHIN) * .985
        flat = math.hypot(feet[s][0] - pelvis[0] - base[0], feet[s][2] - pelvis[2] - base[2])
        if flat >= reach:
            raise ValueError(f"{s} foot is beyond the leg's reach")
        pelvis[1] = min(pelvis[1], feet[s][1] + math.sqrt(reach * reach - flat * flat) - base[1])
    J["pelvis"], J["neck"] = pelvis, pelvis + R @ (P("neck") - P("pelvis"))
    up, look = R @ rz(-c["head"]) @ EY, R @ rz(-c["head"]) @ EX
    for s, sg in SIDES:
        hip = J["hip" + s] = pelvis + P("hip", sg) - P("pelvis")
        yaw = math.radians(c["feet"][s][3])
        pole = np.asarray(c["poles"].get(s, (math.cos(yaw), .1, math.sin(yaw))), float)
        if s in c["kick"]:
            feet[s], pole = hip + np.asarray(c["kick"][s], float) * L, np.array((.3, 1., 0.))
        J["knee" + s], J["ankle" + s] = ik(hip, feet[s], THIGH, SHIN, pole)
    sheath = unit(np.asarray(c.get("saya", poses.SAYA_DIR), float))
    mouth = pelvis + SAYA_AT + sheath * c["saya_pull"]
    shoulder = {s: pelvis + R @ (P("sh", sg) - P("pelvis")) for s, sg in SIDES}
    face, w, gear = J["neck"] + up * 11, c["weapon"], None

    def goal(s, sg, spec):
        if isinstance(spec, str):
            return mouth - sheath * 5 if spec == "hilt" else mouth + sheath * 3
        if isinstance(spec, dict):
            if "plant" in spec:
                return np.array((-3., POLE_LEN["tail"], REST["grip"][2] + 6 + spec["plant"][1] * L))
            return face + R @ np.asarray(spec["face"], float)
        return shoulder[s] + R @ (np.asarray(spec, float) * (1, 1, sg)) * (UPPER + FORE + HAND)

    for s in ("FN" if w and w["hand"] == "F" else "NF"):
        sg = 1. if s == "N" else -1.
        if w and s != w["hand"] and w.get("sep") is not None:
            target = J["grip" + w["hand"]] + gear["dir"] * w["sep"]
        else:
            target = goal(s, sg, c["arms"][s])
        bend = np.asarray(c["elbows"].get(s, (-.5, -.6, .65)), float) * (1, 1, sg)
        J["sh" + s] = shoulder[s]
        J["elbow" + s], J["grip" + s] = ik(shoulder[s], target, UPPER, FORE + HAND, R @ bend)
        J["wrist" + s] = J["elbow" + s] + (J["grip" + s] - J["elbow" + s]) * FORE / (FORE + HAND)
        if w and s == w["hand"]:
            d = unit(np.asarray(w["dir"], float))
            gear = dict(at=J["grip" + s] - d * w.get("shift", 0), dir=d)
    return J, R @ EX, up, look, gear


def pose_frames(c):
    """Bone frames for one pose; None hides a bone's pieces (a weapon that is put away)."""
    J, forward, up, look, gear = solve(c)
    F = {"pelvis": frame(J["pelvis"], J["pelvis"] + EY, EX + forward), "spine": frame(J["pelvis"], J["neck"], forward),
         "head": frame(J["neck"], J["neck"] + up, look)}
    crown = J["neck"] + up * (REST["tail"][1] - 97) + look * REST["tail"][0]                                  # hair hangs from the back of the head
    F["tail"] = frame(crown, crown - EY - look * .15, look)
    F["weapon"] = frame(gear["at"], gear["at"] + gear["dir"], EY + EX * .01) if gear else None
    F["sheathed"] = None if gear else F["pelvis"]
    for s, sg in SIDES:
        yaw, pitch = (math.radians(v) for v in c["feet"][s][3:5])
        heading = np.array((math.cos(yaw), 0., math.sin(yaw)))
        hip, knee, ankle = J["hip" + s], J["knee" + s], J["ankle" + s]
        front = heading + 4 * (knee - (hip + ankle) / 2) / L                 # the knee leads the leg's front
        F["thigh" + s], F["shin" + s] = frame(hip, knee, front), frame(knee, ankle, front)
        toe = heading * math.cos(pitch) - EY * math.sin(pitch)
        F["foot" + s] = frame(ankle, ankle + toe, EY * math.cos(pitch) + heading * math.sin(pitch))
        sh, elbow, wrist, grip = (J[n + s] for n in ("sh", "elbow", "wrist", "grip"))
        a, b = elbow - sh, grip - elbow                                      # the elbow's fold decides the arm's twist
        fold_a = (b - a * (b @ a) / (a @ a)) / (FORE + HAND)
        fold_b = -(a - b * (a @ b) / (b @ b)) / UPPER
        F["upper" + s] = frame(sh, elbow, fold_a + forward * .25)
        F["fore" + s] = frame(elbow, wrist, fold_b + forward * .25)
        F["hand" + s] = frame(wrist, grip, fold_b + forward * .25)
    if c["tip"]:                                # a fall: the posed figure tips over and lies on the ground
        T = rz(c["tip"])
        F = {n: (T @ f[0], T @ f[1], T @ f[2], T @ f[3]) if f else None for n, f in F.items()}
        ys, xs = [f[0][1] for f in F.values() if f], [f[0][0] for f in F.values() if f]
        shift = np.array((-(min(xs) + max(xs)) / 2, 6 - min(ys), 0.))
        F = {n: (f[0] + shift, *f[1:]) if f else None for n, f in F.items()}
    return F


# ------------------------------------------------------------------------------------------------ render
def main():
    job = json.load(open(sys.argv[sys.argv.index("--") + 1], encoding="utf-8"))
    size, origin = job["size"], job["origin"]
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj)
    scene = bpy.context.scene
    rig = make_armature(rest_frames())
    skin = build_character(job["spec"], job.get("outfit"), job.get("weapon"))
    skin.build(rig)
    camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type, camera.data.ortho_scale, camera.data.clip_end = "ORTHO", max(size) / job["scale"], 2000
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = size[0], size[1], 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format, scene.render.image_settings.color_mode = "PNG", "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.display.render_aa = "OFF"
    shading = scene.display.shading
    shading.show_specular_highlight = shading.show_shadows = shading.show_object_outline = False
    scene.display.matcap_ssao_distance, scene.display.matcap_ssao_samples = 5., 64
    rest = {bone.name: bone.matrix_local.inverted() for bone in rig.data.bones}
    elevation = math.radians(14)
    for number, (kind, index, count, view) in enumerate(job["frames"]):
        for name, f in pose_frames(poses.controls(kind, index, count, job["family"])).items():
            rig.pose.bones[name].matrix_basis = rest[name] @ matrix(f) if f else Matrix.Scale(0., 4)
        yaw = math.radians({None: 50., "front": 90., "back": -90.}[view])
        toward = np.array((math.sin(yaw) * math.cos(elevation), math.sin(elevation), math.cos(yaw) * math.cos(elevation)))
        right = unit(np.cross(EY, toward))
        target = np.array((0., (origin[1] - size[1] / 2) / job["scale"] / math.cos(elevation), 0.))
        camera.location = blender(target + toward * 500)
        camera.rotation_euler = Matrix(np.column_stack(
            [blender(right), blender(np.cross(toward, right)), blender(toward)]).tolist()).to_euler()
        for mode, light, colour in (("s", "STUDIO", "MATERIAL"), ("a", "FLAT", "MATERIAL"), ("i", "FLAT", "VERTEX")):
            shading.light, shading.color_type, shading.show_cavity = light, colour, mode == "s"
            if mode == "s":
                shading.cavity_type = "WORLD"
            scene.render.filepath = os.path.join(job["out"], f"{number:04d}_{mode}.png")
            bpy.ops.render.render(write_still=True)
    json.dump({"palette": sorted(set(skin.colour))}, open(os.path.join(job["out"], "meta.json"), "w"))


main()
