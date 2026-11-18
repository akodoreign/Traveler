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
HEAD = ((0, 97.5, 0), 1.19)                    # the head and everything on it, enlarged about the neck
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
        self.surface, self.surfaces = "", []

    def add(self, shape, colour, weights, smooth=True, colours=None, paint=None, part=None):
        """paint(face centre) may return another colour for that face: detail is painted, not modelled."""
        verts, faces = shape
        if paint:
            colours = [paint(np.mean([verts[i] for i in face], axis=0)) or colour for face in faces]
        if self.zoom:
            verts = [np.asarray(self.zoom[0], float) + (np.asarray(v) - self.zoom[0]) * self.zoom[1] for v in verts]
        base = len(self.verts)
        if part is None:
            self.parts += 1
            part = self.parts
        self.verts += verts
        self.weights += weights if isinstance(weights, list) else [weights] * len(verts)
        for i, face in enumerate(faces):
            self.faces.append(tuple(base + k for k in face))
            self.colour.append(colours[i] if colours else colour)
            self.surfaces.append(self.surface)
            self.part.append(part)
            self.smooth.append(smooth)

    def loft(self, points, colour, weight, z=0., n=10, band=None, x=0., pleats=None):
        """A vertical tube through (y, half depth, half width) control points.
        weight(y) gives the bone weights at a height; band = (step, [colours]) stripes it horizontally."""
        ys = sorted(p[0] for p in points)
        if band:
            ys = sorted({*ys, *np.arange(ys[0], ys[-1], band[0])})
        rings = []
        for y in ys:
            v = profile(points, y)
            rings.append(((v[2], y, v[3]) if len(v) > 2 else (x, y, z), v[0], v[1]))
        verts, faces = tube(rings, n, pleats=pleats)
        colours = None
        if band:
            pick = band[1] if callable(band[1]) else (lambda row, k: band[1][row % len(band[1])])
            colours = [pick(math.floor(((a + b) / 2 - ys[0]) / band[0]), k)
                       for a, b in zip(ys, ys[1:]) for k in range(n)] + [colour, colour]
        self.add((verts, faces), colour, [weight(y) for y in ys for _ in range(n)], colours=colours)

    def build(self, armature, surface_materials=False):
        mesh = bpy.data.meshes.new("skin")
        mesh.from_pydata([blender(v) for v in self.verts], [], self.faces)
        roles = self.surfaces if surface_materials else [""] * len(self.faces)
        labels = list(zip(self.colour, roles))
        palette = sorted(set(labels))
        for rgb, surface in palette:
            name = "c%02x%02x%02x" % rgb
            material = bpy.data.materials.new(f"{name}_{surface}" if surface else name)
            material.diffuse_color = [(c / 255) ** 2.2 for c in rgb] + [1]
            mesh.materials.append(material)
        slots = {label: i for i, label in enumerate(palette)}
        mesh.polygons.foreach_set("material_index", [slots[label] for label in labels])
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
    # Keep the skin and its sleeves/wraps on the same cross-sections at joints.
    ys = sorted({y0, y1, *(y for y in np.arange(6., 97., 1.5) if y0 < y < y1)})
    for y in ys:
        v, t = profile(BODY[name], y), (y1 - y) / (y1 - y0)
        g = GIRTH[name]
        out.append((y, v[0] * g + grow + flare * t, v[1] * g + grow + flare * t)
                   + ((v[2], v[3] * sign) if len(v) > 2 else ()))
    return out


HEAD_C, HEAD_R = (.8, 108.5, 0.), (8.2, 10.2, 7.6)
JAW = [(98.3, 0, 0, 4.7), (98.65, 1.6, 1.75, 4.6),
       (99.25, 3.2, 2.85, 3.9), (100.15, 4.5, 3.8, 3.0),
       (101.4, 5.7, 4.95, 2.1), (102.8, 6.8, 5.85, 1.5),
       (104.0, 7.37, 6.45, 1.24)]
SAYA_AT = (6., 4., 11.5)                        # scabbard mouth, from the pelvis


def head_section(y):
    if y <= JAW[-1][0]:
        return profile(JAW, y)
    t = max(0., (HEAD_C[1] - y) / HEAD_R[1])
    r = math.sqrt(max(0., 1 - ((y - HEAD_C[1]) / HEAD_R[1]) ** 2))
    return HEAD_R[0] * (1 - .3 * t ** 1.5) * r, HEAD_R[2] * (1 - .5 * t ** 1.5) * r, HEAD_C[0] + 1.2 * t


def face_x(y, z):
    depth, width, x = head_section(y)
    return x + depth * math.sqrt(max(0., 1 - (z / max(width, .1)) ** 2))


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


def face_patch(S, points, colour, offset, part):
    """Lay a painted feature on the curved skin, in front-to-back layer order."""
    points = np.asarray(points)
    centre = np.mean(points, axis=0)
    verts = [np.array((face_x(y, z) + offset, y, z)) for z, y in [centre, *points]]
    S.add((verts, [(0, i + 1, (i + 1) % len(points) + 1) for i in range(len(points))]),
          colour, {"head": 1.}, smooth=False, part=part)


def face(S, spec, skin):
    part = S.parts
    iris = tuple(spec.get("eye", (60, 44, 40)))
    brow = tuple(spec["hair"])
    eye = spec.get("kit", {}).get("eye")
    opening = .72 if eye in ("half", "smile") else 1.16 if eye in ("wide", "round") else .95
    for _, side in SIDES:
        def patch(profile, colour, offset):
            points = [(side * z, y) for z, y in profile]
            face_patch(S, points if side > 0 else points[::-1], colour, offset, part)

        lower = 105.7 - opening
        patch([(1.28, 105.8), (2.35, 106.33), (4.25, 106.45),
               (5.65, 106.0), (4.5, lower + .16), (2.55, lower)], (248, 232, 213), .19)
        patch([(2.46, 106.3), (4.08, 106.39), (4.28, 105.63),
               (3.83, lower + .05), (2.77, lower + .04), (2.4, 105.42)], iris, .33)
        patch([(2.89, 106.3), (3.67, 106.32), (3.83, 105.27), (2.9, 105.1)], INK, .47)
        patch([(2.56, 106.22), (3.08, 106.23), (3.08, 105.66), (2.56, 105.66)], WHITE, .56)
        patch([(1.18, 105.68), (2.48, 106.69), (4.25, 107.03), (5.92, 106.34),
               (5.57, 105.72), (4.1, 106.41), (2.52, 106.21)], INK, .45)
        patch([(1.85, 108.38), (3.54, 109.0), (5.29, 108.75),
               (5.27, 108.38), (3.58, 108.51), (1.91, 107.98)], brow, .27)
        S.add(ellipsoid((.6, 105.5, 7.2 * side), (1.4, 2., 1.15), 8, 6), skin, {"head": 1.})
    face_patch(S, [(-.68, 103.1), (0, 103.46), (.64, 102.8), (.11, 102.68)], shade(skin, .86), .17, part)
    face_patch(S, [(-1.02, 101.44), (.12, 101.52), (1.22, 101.6),
                   (.87, 101.22), (-.42, 101.1)], shade(skin, .61), .2, part)


def ink_stroke(S, path, width, colour, surface, weight, mirrored=False):
    pairs = []
    for i, point in enumerate(path):
        x, y = point
        dx, dy = np.subtract(path[min(i + 1, len(path) - 1)], path[max(i - 1, 0)])
        nx, ny = -dy / math.hypot(dx, dy), dx / math.hypot(dx, dy)
        half = width * (.55 if i in (0, len(path) - 1) else 1.)
        pairs.extend(surface(x + f * half * nx, y + f * half * ny) for f in (-1, 1))
    faces = [(i, i + 1, i + 3, i + 2) for i in range(0, len(pairs) - 2, 2)]
    if mirrored:
        faces = [f[::-1] for f in faces]
    S.add((pairs, faces), colour, [weight(p[1]) for p in pairs])


def yosai_ink(S, spec):
    ink = tuple(spec["tattoo"])
    deep, blue = shade(ink, .72), (27, 112, 151)

    def cylinder(part, sign, centre_angle, width):
        def surface(u, y):
            depth, radius, *centre = profile(BODY[part], y)
            x, z = centre if centre else (0., 0.)
            a = centre_angle + width * u
            return (x + (depth * GIRTH[part] + .22) * math.cos(a), y,
                    sign * (z + (radius * GIRTH[part] + .22) * math.sin(a)))
        return surface

    def spiral(x, y, rx, ry, turn=1.):
        angles = (turn * i * .32 for i in range(23))
        return [(x + rx * math.cos(t) * (1. - i / 25.),
                 y + ry * math.sin(t) * (1. - i / 25.)) for i, t in enumerate(angles)]

    def stroke(path, width, colour, surface, weight, mirrored=False):
        # Short segments keep the ink on the curved skin through both bend and twist.
        samples = [np.asarray(path[0], dtype=float)]
        for a, b in zip(path, path[1:]):
            start, end = np.asarray(a), np.asarray(b)
            count = max(1, math.ceil(float(np.linalg.norm(end - start)) * 3))
            samples.extend(start + (end - start) * (i / count) for i in range(1, count + 1))
        ink_stroke(S, samples, width, colour, surface, weight, mirrored)

    # Keep the dragon's head below the cuff so the motif reads in the short haori.
    for side, sign in SIDES:
        arm = cylinder("arm", sign, .97, .4)

        def draw(path, width, colour=ink):
            stroke(path, width, colour, arm, arm_w(side), sign < 0)

        if sign > 0:
            spine = [(1.18 * math.sin(i * .32), 67.2 + .48 * i) for i in range(34)]
            draw(spine, .74, deep)
            draw([(u + .24, y) for u, y in spine], .25, blue)
            draw([(-1.42, 82.1), (-1.55, 83.25), (-.87, 84.12), (.03, 83.86), (.49, 83.04),
                  (1.75, 83.25), (2.26, 82.52), (1.63, 81.86), (.44, 81.72), (-.26, 80.84),
                  (-1.23, 81.14), (-1.42, 82.1)], .38, blue)
            draw([(-1.01, 83.68), (-1.4, 84.76), (-2.28, 85.12)], .28, deep)
            draw([(-.23, 83.51), (-.25, 84.7), (-.83, 85.58)], .27, deep)
            draw([(.28, 82.92), (.09, 82.75), (-.23, 82.93)], .22, deep)
            draw([(1.48, 82.36), (2.29, 81.74), (2.22, 80.64), (1.71, 80.26)], .19, blue)
            for i, direction in ((5, -1), (11, 1), (18, -1), (25, 1)):
                u, y = spine[i]
                draw([(u, y), (u + direction*.95, y - .45), (u + direction*1.35, y - 1.45),
                      (u + direction*1.58, y - 1.17)], .27, deep)
            for i in (7, 14, 21, 28):
                u, y = spine[i]
                draw([(u-.8, y+.55), (u-.27, y+.9), (u+.55, y+.65)], .18, blue)
        else:
            stem = [(.68 * math.sin(i * .24), 67.3 + i * .58) for i in range(38)]
            draw(stem, .38, deep)
            for index, direction in ((4,-1), (9,1), (15,-1), (21,1), (28,-1), (33,1)):
                u, y = stem[index]
                draw([(u,y), (u+direction*.85,y+.8), (u+direction*1.48,y+.28),
                      (u+direction*1.86,y+1.22), (u+direction*1.84,y+3.05),
                      (u+direction*.76,y+2.73), (u+direction*.34,y+1.91),
                      (u+direction*.85,y+.8)], .31, blue)
                draw([(u+direction*.8,y+.79), (u+direction*1.18,y+1.6),
                      (u+direction*1.71,y+2.54)], .18, deep)

    chest = cylinder("torso", 1, 0., .26)
    for sign in (-1, 1):
        stroke(spiral(sign*1.48, 88, 1.02, 4.31, sign), .36, blue, chest, torso_w())
        stroke([(sign * (.82 + .55 * math.sin(i * .19)), 78.5 + i * .6) for i in range(24)],
               .43, ink, chest, torso_w())

    def scalp(angle, y):
        depth, width, x = head_section(y)
        return x + (depth + .19) * math.cos(angle), y, (width + .19) * math.sin(angle)

    S.zoom = HEAD
    head = lambda _: {"head": 1.}
    for sign in (-1, 1):
        def scroll(path, width, colour=blue):
            stroke([(sign*u, y) for u, y in path], width, colour, scalp, head, sign < 0)

        scroll([(.11, 108.4), (.17, 109.08), (.17, 110.45), (.1, 112.16),
                (.16, 114.0), (.3, 115.6)], .102)
        scroll([(.13, 110.2), (.32, 111.19), (.56, 111.25), (.85, 110.83), (1.08, 109.93)], .091)
        scroll(spiral(.59, 113.15, .46, 2.25), .072)
        scroll([(.51, 116.54), (.77, 116.12), (1.04, 115.11), (1.23, 113.92)], .061, deep)
        scroll(spiral(1.19, 104.65, .32, 1.55, -1), .078)
        scroll([(.99, 104.32), (1.03, 103.57), (1.1, 102.68), (1.13, 101.38),
                (.97, 100.25), (.78, 99.64)], .091)
        scroll([(.16, 100.82), (.17, 100.03), (.27, 99.43), (.49, 99.2), (.7, 99.41)], .088, ink)
    S.zoom = None

def head_ornaments(S, spec):
    head = {"head": 1.}
    if spec.get("head_tattoo") and spec.get("body_ink") != "ise_zumi":
        ink = tuple(spec["tattoo"])

        def scalp(u, y):
            depth, width, centre = head_section(y)
            return centre + (depth + .16) * math.cos(u), y, (width + .16) * math.sin(u)

        for side in (-1, 1):
            ink_stroke(S, [(side * (.26 + .28 * math.sin(i * .23)), 110.2 + i * .48)
                           for i in range(15)], .034, ink, scalp, lambda _: head, side < 0)
    if spec.get("ear_ornament"):
        style, rgb = spec["ear_ornament"]
        metal = tuple(rgb)
        sides = (-1, 1) if style == "drop" else (1,)
        for side in sides:
            S.add(ellipsoid((1.18, 104.4, 8.02 * side), (.36, .43, .33), 8, 5), metal, head)
            if style == "drop":
                strand(S, shade(metal, .67), [(1.16, 104.42, 8.03 * side),
                                              (1.16, 103.4, 8.14 * side),
                                              (1.22, 102.8, 8.16 * side)], .2)
                S.add(ellipsoid((1.22, 102.7, 8.16 * side), (.43, .65, .35), 8, 6), metal, head)
    if spec.get("glasses"):
        for _, side in SIDES:
            points = [(face_x(105.8 + 1.34 * math.sin(t), side * (3.57 + 2.66 * math.cos(t))) + .63,
                       105.8 + 1.34 * math.sin(t), side * (3.57 + 2.66 * math.cos(t)))
                      for t in (i * math.tau / 18 for i in range(19))]
            S.add(tube([(point, .17, .17) for point in points], 6), (87, 69, 53), head)
        S.add(ellipsoid((face_x(106, 0) + .68, 106, 0), (.19, .18, 1.14), 8, 5), (87, 69, 53), head)


def signature_mask(S, spec):
    """Head-bound costume piece so equipped masks can take its place."""
    style = spec["mask"]
    default = {"porcelain": (227, 221, 199), "noh": (210, 183, 146), "death": (169, 154, 145),
               "reed": (154, 112, 69), "mempo": (69, 65, 71), "cloth": (138, 27, 43)}
    colour = tuple(spec.get("mask_col", spec.get("mask_tone", default.get(style, INK))))
    head = {"head": 1.}
    S.zoom = HEAD
    for _, side in SIDES:
        # Rows follow the actual face. Avoid a fan whose flat triangles slice through the cheek.
        rows = [(104.55, 104.17, 104.26, 104.81), (103.35, 103.24, 103.36, 104.26),
                (101.88, 101.82, 102.06, 103.62), (100.38, 100.39, 100.78, 102.12),
                (99.32, 99.49, 100.05, 101.25)]
        widths = [(0, 2.15, 4.35, 6.65), (0, 2.1, 4.15, 6.42), (0, 1.95, 3.9, 6.08),
                  (0, 1.72, 3.35, 5.38), (0, 1.05, 2.45, 4.43)]
        verts = [(face_x(y, side*z) + .92 + (.32 if z < 2.2 and r in (0, 1) else 0), y, side*z)
                 for r, (row, width) in enumerate(zip(rows, widths)) for y, z in zip(row, width)]
        faces = [(i, i+1, i+5, i+4) for i in range(15) if i % 4 != 3]
        if side < 0:
            faces = [face[::-1] for face in faces]
        dark, light = shade(colour, .69), shade(colour, 1.16, 5)
        tones = [light if r == 0 or (style in ("reed", "mempo") and r == 2) else dark if c == 2
                 else colour for r in range(4) for c in range(3)]
        S.add((verts, faces), colour, head, colours=tones)
        S.add(tube([((4.3, 104.88, 6.56*side), .22, .22), ((1.7, 104.54, 8.14*side), .22, .22),
                    ((-.7, 104.15, 8.38*side), .21, .22)], 6), dark, head)
    S.zoom = None


def body(S, spec):
    """The bare figure: skin, a loincloth, a chest wrap and wrist and ankle wraps."""
    skin, h = tuple(spec["skin"]), {"head": 1.}
    S.loft(cover("torso", 55, 96, 0), skin, torso_w(), n=12)
    S.loft(cover("torso", 55, 64, .5), WHITE, torso_w(), n=12)
    if spec.get("female") or spec.get("wrap"):
        S.loft(cover("torso", 79, 90, .5), WHITE, torso_w(), n=12)
    S.loft([(94, 2.8, 2.8), (101, 2.6, 2.6)], skin, blend((94, "spine"), (101, "head")), n=8)
    S.zoom = HEAD
    head = ellipsoid((0, HEAD_C[1], 0), (1, HEAD_R[1], 1), 40, 36)
    for v in head[0]:
        depth, width, x = head_section(v[1])
        r = math.hypot(v[0], v[2])
        v[0], v[2] = (x + depth * v[0] / r, width * v[2] / r) if r else (x, 0)
    S.add(head, skin, h)
    face(S, spec, skin)
    head_ornaments(S, spec)

    S.zoom = None
    for s, sg in SIDES:
        S.loft(cover("leg", 5, 61, 0, sg), skin, leg_w(s))
        S.loft(cover("leg", 6, 13, .35, sg), WHITE, leg_w(s))
        S.add(foot_mesh(sg), skin, {"foot" + s: 1.})
        S.loft(cover("arm", 61, 95, 0, sg), skin, arm_w(s), n=8)
        S.loft(cover("arm", 61.5, 66, .3, sg), WHITE, arm_w(s), n=8)
        S.add(ellipsoid((.3, 58.4, 13.4 * sg), (2.7, 3.6, 2.1), 8, 6), skin, {"hand" + s: 1.})
    if spec.get("body_ink") == "ise_zumi":
        yosai_ink(S, spec)


def hair(S, spec):
    """Hair is a full mass around the skull with locks over it; a painted band of sheen keeps it from going flat."""
    style, colour, h = spec.get("hairstyle", "short"), tuple(spec["hair"]), {"head": 1.}
    if style == "bald":
        return
    sheen = shade(colour, 1.25, 17)
    S.surface = "hair"
    S.zoom = HEAD
    cap = ellipsoid((-.3, 109.6, 0), (10.2, 11.7, 9.9), 20, 14)
    keep = [f for f in cap[1] if not (np.mean([cap[0][i][0] for i in f]) > 2.8 and np.mean([cap[0][i][1] for i in f]) < 112.5
                                      and abs(np.mean([cap[0][i][2] for i in f])) < 7.6)]
    S.add((cap[0], keep), colour, h, paint=lambda c: sheen if 115.6 < c[1] < 117.7 and c[0] > -7.5 else None)
    lower_mass = (5.6, 7.4, 8.8) if style in ("short", "spiky") else (7.2, 9.6, 10.2)
    S.add(ellipsoid((-5., 106., 0), lower_mass, 14, 10), colour, h)                       # mass behind the head
    sweep = .85 if spec.get("bangs") == "side" else 1.45
    for i, z in enumerate((-7.8, -5.3, -2.6, .15, 3., 5.8, 8.)):
        low = 109.25 + (i % 3) * .8 - 2.65 * (abs(z) > 5)
        tip = z + sweep
        lock = shade(colour, 1.05, 8) if i % 3 == 1 else colour
        strand(S, lock, [(3.6, 119.6 - abs(z) * .18, z * .58),
                         (face_x(114, z * .76) + 2.1, 114., z * .85),
                         (face_x(low + 1.8, z) + 1.75, low + 1.8, z),
                         (face_x(low, tip) + 1.55, low, tip)], 2.65)
    for _, sg in SIDES:
        strand(S, colour, [(2.2, 114, 8.6 * sg), (5., 105, 8.65 * sg),
                           (4.1, 99 if style == "spiky" else 95, 7.4 * sg)], 2.55)
    if style in ("spiky", "short", "mane"):
        for i in range(11):
            a = 2 * math.pi * (i * .618 % 1)
            tilt = .48 + .67 * ((i * 7) % 5) / 4
            out = np.array((math.cos(a) * math.sin(tilt), math.cos(tilt), math.sin(a) * math.sin(tilt)))
            base = np.array((-.3, 109.6, 0)) + out * (9.2, 10.6, 8.9)
            length = (4.6 + i % 3 * .58) if style == "spiky" else 3.45
            strand(S, sheen if i % 4 == 1 else colour,
                   [base - out * 2.8, base + out * 1.6, base + out * length - (3., .4, -.6)], 3.4)

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
        bottom = {"long": 73, "mane": 88, "bob": 99}[style]
        S.loft([(bottom, 3.4, 9., -7.5, 0), (100, 4.6, 10.2, -7., 0), (112, 3.6, 9.4, -6., 0)], colour,
               blend((bottom, "tail" if style == "long" else "head"), (104, "head"), (112, "head")), n=14,
               pleats=(5, .08))
        if style == "long":
            for i, z in enumerate((-8.7, -5.4, -1.8, 1.8, 5.4, 8.7)):
                rings = [((-5.5, 112., z * .82), 2.5, 2.4), ((-11.9, 99, z), 2.3, 2.1),
                         ((-12.1, 85, z * 1.12), 1.9, 1.6),
                         ((-10.9, 68 + i % 3 * 3., z * 1.06), .45, .34)]
                S.add(tube(rings, 8), sheen if i in (1, 4) else colour,
                      [blend((72, "tail"), (104, "head"))(p[1]) for p, _, _ in rings for _ in range(8)])
    S.zoom = None
    S.surface = ""


# ------------------------------------------------------------------------------------------------ outfit
def skirt_w(v):
    near = min(1., max(0., v[2] / 6 + .5))
    if v[1] >= 61:
        return torso_w()(v[1])
    weights = {}
    for suffix, share in (("N", near), ("F", 1 - near)):
        for bone, amount in leg_w(suffix)(v[1]).items():
            if share:
                weights[bone] = weights.get(bone, 0.) + share * amount
    return weights


def brocade(u, y, pattern):
    """A staggered repeat in garment space. The fabric pattern moves with the mesh."""
    row = math.floor(y / 12)
    x = (u + 5.5 * (row % 2)) % 11 - 5.5
    v = y % 12 - 6
    if pattern == "stripes":
        return abs(x) < .85
    if pattern == "clouds":
        return abs(v - 2.2 * math.cos(x * .63)) < 1.05 and abs(x) < 4.15
    if pattern == "rings":
        return 2.05 < math.hypot(x, v) < 3.65
    if pattern == "diamonds":
        d = abs(x) + abs(v)
        return 2.35 < d < 4.05 or d < 1.18
    # Five petals around a small open centre, with room between repeats.
    return any(math.hypot(x - 2.5 * math.cos(a), v - 2.5 * math.sin(a)) < 1.6
               for a in (math.tau * i / 5 for i in range(5)))


def coat(S, spec):
    """Open-front robe panels over the hakama, continuous around the back."""
    colour = tuple(spec["top"])
    lining = tuple(spec.get("lining", spec["accent"]))
    motif = tuple(spec["pcol"]) if spec.get("pattern") and spec.get("pcol") else None
    bottom, top = spec.get("coat_bottom", 15. if spec.get("long_robe") else 20.), 68.
    n = 56
    ys = list(np.arange(bottom, top, 1.45)) + [top]
    verts, faces, colours = [], [], []
    for y in ys:
        t = (top - y) / (top - bottom)
        depth, width = profile(BODY["torso"], max(y, 55))
        # Tuck the top of the panels underneath the obi. Below the waist the
        # knees and pleats need more room even while each side tracks its leg.
        drape = min(1., max(0., (63.7 - y) / 18.))
        rx = depth * GIRTH["torso"] + 2.1 + 8.7 * drape
        side_drape = min(1., max(0., (57.5 - y) / 12.))
        rz = width * GIRTH["torso"] + .85 + 7.55 * side_drape
        gap = .16 + .28 * t
        for k in range(n + 1):
            a = gap + (math.tau - 2 * gap) * k / n
            fold = (1 + .052 * drape * math.cos(9 * a) + .028 * drape * math.sin(5 * a))
            verts.append((rx * math.cos(a) * fold, y + 1.35 * t * math.sin(a * 2), -rz * math.sin(a) * fold))

    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        y = (a + b) / 2
        for k in range(n):
            index = i * (n + 1) + k
            faces.append((index, index + 1, index + n + 2, index + n + 1))
            if k in (0, n - 1) or y < bottom + 1.5:
                colour_at = lining
            elif motif and y < top - 5 and brocade((k + .5) * 1.52, y - bottom, spec["pattern"]):
                colour_at = motif
            elif math.cos(9 * (k + .5) * math.tau / n) < -.72:
                colour_at = shade(colour, .86)
            else:
                colour_at = colour
            colours.append(colour_at)

    # Turn the open front and the hem inwards so their back faces have a fabric edge.
    def turn_edge(indices):
        offset = len(verts)
        for idx in indices:
            x, y, z = verts[idx]
            verts.append((x * .945, y, z * .945))
        for j, (a, b) in enumerate(zip(indices, indices[1:])):
            faces.append((b, a, offset + j, offset + j + 1))
            colours.append(shade(lining, .72))

    turn_edge(list(range(n + 1)))
    turn_edge([i * (n + 1) for i in range(len(ys) - 1, -1, -1)])
    turn_edge([i * (n + 1) + n for i in range(len(ys))])
    S.add((verts, faces), colour, [skirt_w(v) for v in verts], colours=colours)

def kimono(S, spec, wide=False):
    """Overlapping collar, fitted shoulders and wide sleeves with a returned cuff."""
    top, collar = tuple(spec["top"]), tuple(spec.get("collar", WHITE))
    lining = tuple(spec.get("lining", spec["accent"]))
    motif = tuple(spec["pcol"]) if wide and spec.get("pattern") and spec.get("pcol") else None
    S.loft(cover("torso", 60, 96, 1.25), top, torso_w(), n=16)
    for s, sg in SIDES:
        # Each lapel is a flat ribbon that runs along the actual torso profile.
        stations = [(95.8, 3.5, .7), (93, 3.2, 1.05), (88, 2., 1.1),
                    (83, .55, 1.1), (78, -1.15, 1.), (73, -2.8, .72)]
        stations = stations if sg == 1 else stations[:4]
        verts = []
        for y, z, width in stations:
            rx, rz = profile(BODY["torso"], y)
            rx, rz = rx * GIRTH["torso"] + 1.25, rz * GIRTH["torso"] + 1.25
            for lateral in (-width, .38 * width, width):
                v = z * sg + lateral * sg
                verts.append((rx * math.sqrt(1 - (v / rz) ** 2) + .48, y, v))
        faces = [(i + j, i + j + 1, i + j + 4, i + j + 3)
                 for i in range(0, len(verts) - 3, 3) for j in range(2)]
        S.add((verts, faces), collar, [torso_w()(y) for _, y, _ in verts],
              colours=[c for _ in stations[1:] for c in (collar, lining)])
        if spec.get("short_sleeves"):
            S.loft(cover("arm", 85, 95.4, 1.25, sg, flare=.7), top, arm_w(s), n=20, pleats=(4, .065))
            S.loft(cover("arm", 84.9, 86, 2.05, sg), lining, arm_w(s), n=20)
        elif wide:
            def sleeve_paint(row, k):
                if row == 0:
                    return lining
                if motif and row > 1 and brocade(k * 1.5, row * 1.45 + 3, spec["pattern"]):
                    return motif
                return shade(top, .76) if k in (8, 9, 19) else top

            S.loft(cover("arm", 62.3, 95.4, 1.12, sg, flare=4.5), top, arm_w(s), n=28,
                   pleats=(4, .075), band=(1.45, sleeve_paint))
            # Draped fabric behind the cuff follows the forearm instead of floating below it.
            rings = [((-1.3, 79, 12.6 * sg), 3.5, 3.4), ((-3.2, 69, 13.0 * sg), 5.8, 4.3),
                     ((-4.9, 59.2, 13.25 * sg), 6.7, 4.4), ((-5.3, 54.8, 13.3 * sg), 4.2, 3.4)]
            S.add(tube(rings, 12, pleats=(3, .08)), shade(top, .82), {"fore" + s: 1.},
                  paint=lambda c: lining if c[1] < 56 else None)
        else:
            S.loft(cover("arm", 73, 95.4, 1.65, sg, flare=2.65), top, arm_w(s), n=16, pleats=(4, .065))
            S.loft(cover("arm", 72.7, 74.4, 4.82, sg), lining, arm_w(s), n=16)


def hakama(S, spec, short=False):
    """Divided pleats, with each trouser leg following its original leg weights."""
    lower = tuple(spec["lower"])
    lining = tuple(spec.get("lining", spec["accent"]))
    fold = shade(lower, .67)
    for s, sg in SIDES:
        bottom = spec.get("hakama_hem", 27.) if short else 7.9
        if short:
            S.loft(cover("leg", 8, 43, .68, sg), shade(lower, .8), leg_w(s), n=16)
        S.loft(cover("leg", bottom, 62, 1.4, sg, flare=3.1 if short else 3.7), lower, leg_w(s), n=24,
               pleats=(6, .12), band=(1.65, lambda row, k: lining if short and row == 0
                                      else fold if k % 4 == 2 else lower))

def obi(S, spec):
    accent, gold = tuple(spec["accent"]), trim(spec)
    cord = tuple(spec.get("cord", spec["accent"]))
    wrap = shade(tuple(spec["lower"]), .58)
    S.loft(cover("torso", 63.7, 71.4, 3.24), wrap, torso_w(), n=24,
           band=(1.2, (wrap, shade(wrap, 1.13, 6), wrap, wrap)))
    for y in (65.8, 68.6):
        S.loft(cover("torso", y, y + 1.1, 3.6), accent, torso_w(), n=24)
    w = torso_w()(67.)
    for side in (-1., 1.):
        S.add(tube([((10.1, 67.1, .6 * side), .75, .72), ((10.3, 69.1, 2.75 * side), .85, .8),
                    ((10.3, 66.85, 3.45 * side), .88, .8), ((10.5, 66.2, .65 * side), .64, .62)], 8), accent, w)
    S.add(ellipsoid((10.55, 67.1, 0), (1.12, 1.45, 1.65), 8, 6), cord, w)
    for z, end in ((-1.4, 54.4), (1.3, 51.2)):
        rings = [((11.0, 67.2, z * .34), .58, .73), ((12.8, 62.8, z), .51, .59),
                 ((16.8, end + 1.5, z * 1.35), .46, .53), ((17.3, end, z * 1.48), .58, .61)]
        vertices, faces = tube(rings, 8)
        S.add((vertices, faces), accent, [skirt_w(v) for v in vertices],
              paint=lambda c: gold if c[1] < end + 1.6 else None)

def armour(S, spec):
    """Lamellar: rows of small plates laced together, over the kimono."""
    plate, lace = tuple(spec["armor"]), tuple(spec.get("lace", spec["accent"]))
    gold, gap, cloth = trim(spec), shade(plate, .6), shade(tuple(spec["top"]), .62)

    def lamellar(row, k):
        return (lace if k % 2 else gap) if row % 4 == 3 else plate

    S.loft(cover("torso", 70, 91.4, 2.38), plate, torso_w(), n=32, band=(.95, lamellar))
    for y in (72.7, 76.5, 80.3, 84.1, 87.9):
        S.loft(cover("torso", y, y + .62, 2.58), gap, torso_w(), n=32,
               band=(.7, lambda row, k: lace if k % 4 == 0 else gap))
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
            y, z = 94.5 - i * 2.75, (16.4 + i * .62) * sg
            bone = {"upper" + s: 1.}
            rings = [((x, y - .7 * abs(x / 6), z - sg * .9 * (x / 6) ** 2), ry, rz)
                     for x, ry, rz in ((-6.9, .68, .65), (-5.2, 1.6, 1.18),
                                       (5.05, 1.6, 1.18), (6.9, .68, .65))]
            S.add(tube(rings, 8), plate, bone, smooth=False,
                  paint=lambda c: gap if c[1] < y - .8 else shade(plate, 1.14, 8) if c[1] > y + .75 else None)
            for x in (-3.35, 2.55):
                S.add(box((x, y - 1.26, z + 1.05 * sg), (.62, .57, .38)),
                      gold if i == 3 else lace, bone, smooth=False)
        S.loft(cover("arm", 62, 73, 1., sg), cloth, arm_w(s), n=8,           # kote: splints on a cloth sleeve
               band=(1.4, lambda row, k: lace if row % 4 == 3 else plate if k % 2 else cloth))
        S.loft(cover("leg", 8, 30, 1.2, sg), cloth, leg_w(s),               # suneate: a shin plate on dark leggings
               band=(1.6, lambda row, k: (lace if row % 5 == 4 else plate) if k in (8, 9, 0, 1) else cloth))


def helmet(S, spec):
    """Natsuko's shallow iron cap, worn over the base headband."""
    if not spec.get("iron_cap"):
        return
    plate, band = tuple(spec["armor"]), tuple(spec.get("band", spec["accent"]))
    S.surface = "iron"
    S.zoom = HEAD
    rings = [((-.65, 113.05, 0), 10.98, 10.74), ((-.7, 116.1, 0), 10.67, 10.26),
             ((-1., 119.5, 0), 9.52, 9.18), ((-1.1, 122.7, 0), 6.78, 6.31),
             ((-1.5, 124.35, 0), 2.4, 2.55)]
    n = 32
    verts, faces = tube(rings, n)
    colours = [shade(plate, 1.08, 13) if k % 8 == 0 else shade(plate, .59) if row == 0
               else plate for row in range(len(rings) - 1) for k in range(n)] + [plate, plate]
    S.add((verts, faces), plate, {"head": 1.}, colours=colours)
    S.surface = "linen"
    S.add(tube([((-.33, 112.65, 0), 11.32, 10.95), ((-.36, 113.52, 0), 11.25, 10.88)], n),
          band, {"head": 1.})
    S.zoom = None
    S.surface = ""


FOOT = [(-3.9, .8, 3.1, .32, 0), (-3.35, .35, 4.8, 1.65, 0),
        (-2.5, .25, 5.75, 2.45, 0), (-.8, .25, 6.15, 2.65, 0),
        (1.3, .65, 5.4, 2.55, .25), (3.4, .45, 4.55, 2.8, .1),
        (5.8, .23, 3.65, 3.3, -.14), (7.5, .23, 3.25, 3.18, -.4),
        (8.7, .36, 2.85, 2.55, -.65), (9.55, .62, 2.36, 1.35, -1.02),
        (9.9, 1.13, 1.8, .36, -1.28)]


def foot_mesh(sign, layer="bare"):
    """Rounded heel, raised instep and tapered toes; +X is forward."""
    n = 20
    verts, faces = [], []
    for x, low, high, width, centre in FOOT:
        if layer == "tabi":
            x, low, high, width = x * 1.04, max(.18, low - .2), high + .23, width + .24
        elif layer == "sole":
            x, low, high, width = x * 1.12, 0., 1.14, width + .52
        for i in range(n):
            angle = 2 * math.pi * i / n
            y, z = math.cos(angle), math.sin(angle)
            if layer == "sole":  # Flatten the tread without squaring off the outline.
                y, z = math.copysign(abs(y) ** .34, y), math.copysign(abs(z) ** .52, z)
            verts.append((x, (low + high + (high - low) * y) / 2, sign * (5.5 + centre) + width * z))
    for row in range(len(FOOT) - 1):
        a, b = row * n, (row + 1) * n
        faces.extend((a + i, a + (i + 1) % n, b + (i + 1) % n, b + i) for i in range(n))
    return verts, [tuple(reversed(range(n))), *faces, tuple(range(len(verts) - n, len(verts)))]


def footwear(S, spec, tabi=WHITE):
    for s, sg in SIDES:
        S.add(foot_mesh(sg, "tabi"), tabi, {"foot" + s: 1.})
        S.add(foot_mesh(sg, "sole"), STRAW, {"foot" + s: 1.})
        z = 5.5 * sg
        for side in (-1., 1.):
            S.add(tube([((2.3, 1.05, z + side * 3.12), .49, .47), ((4., 3.25, z + side * 2.22), .45, .49),
                        ((7.45, 3.37, z - 1.15 * sg), .39, .41)], 10),
                  tuple(spec["accent"]), {"foot" + s: 1.})


def headband(S, spec, growth=0.):
    band = tuple(spec.get("band", spec["accent"]))
    S.surface = "linen"
    S.zoom = HEAD
    S.add(tube([((-.3, 111.2, 0), 10.75 + growth, 10.4 + growth),
                ((-.3, 114., 0), 10.6 + growth, 10.25 + growth)], 20, caps=False), band, {"head": 1.})
    S.add(ellipsoid((-11.3, 112.6, 0), (1.4, 1.6, 1.9), 6, 4), band, {"head": 1.})               # the knot
    for z, low in ((-1.4, 99.), (1.4, 101.5)):                              # ribbon tails
        strand(S, band, [(-11.5, 112, z), (-14.5, 108, z * 1.6), (-16., low, z * 2.2)], 1.7, "tail")
    S.zoom = None
    S.surface = ""


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
    elif kind in ("fan", "kama", "nunchaku", "bokken"):
        def segment(a, b, radius, colour):
            S.add(tube([(a, radius, radius), (b, radius, radius)], 6), colour, w)

        if kind == "fan":
            tips = [(14 * math.sin(t), 14 * math.cos(t), 0.) for t in np.linspace(-1., 1., 9)]
            rim = [(0., 0., 0.), *tips]
            n = len(rim)
            face = [(x, y, z + dz) for dz in (-.36, .36) for x, y, z in rim]
            edges = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
            S.add((face, [tuple(reversed(range(n))), tuple(range(n, 2 * n)), *edges]), tuple(spec["accent"]), w)
            for tip in tips:
                segment((0, -2, 0), (tip[0], tip[1], .45), .2, WOOD)
        else:
            segment((0, -6, 0), (0, 28 if kind == "bokken" else 12, 0), 1.05, WOOD)
            if kind == "kama":
                segment((0, 12, 0), (8, 15, 0), .85, STEEL)
                segment((8, 15, 0), (12, 11, 0), .48, STEEL)
            if kind == "nunchaku":
                segment((0, 12, 0), (4, 17, 0), .35, STEEL)
                segment((4, 17, 0), (13, 9, 0), 1.05, WOOD)
    elif kind in ("katana", "tanto", "nodachi"):
        length, gold = {"katana": 37, "tanto": 15, "nodachi": 51}[kind], trim(spec)

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
    "armored": [kimono, lambda S, spec: hakama(S, spec, True), obi, armour, helmet, lambda S, spec: footwear(S, spec, INK)],
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
    if outfit != "bare" and spec.get("mask"):
        signature_mask(S, spec)
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
    if gear and c["weapon"].get("roll"):
        at, x, y, z = F["weapon"]
        roll = math.radians(c["weapon"]["roll"])
        cos, sin = math.cos(roll), math.sin(roll)
        F["weapon"] = (at, cos * x + sin * z, y, cos * z - sin * x)
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


if __name__ == "__main__":
    main()
