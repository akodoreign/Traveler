"""Project decal grids directly onto a garment's weighted bind-pose surface."""
from collections import defaultdict

from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

import chara3d as c
import gear_catalog as catalog

FACES = ((9, 9, 9), (21, 21, 21))
BASIS = (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))


def placements(item, slot):
    # Facing (+front/-back, 2=top), vertical and lateral center, width and height.
    if slot == "body":
        style = catalog.BODY[item][0]
        if style in ("plate", "lamellar"):
            return ((1, 86.5, 4.5, 8.5, 8.5), (-1, 80, 2.7, 14, 14))
        return ((1, 88.5, 5.35, 7.9, 7.9), (-1, 79.5, 2.4, 15, 14))
    if slot == "cape":
        return ((-1, 83, 0, 13, 13), (-1, 72, -7.7, 7, 7))
    pivot, scale = c.HEAD
    if slot == "head":
        style = catalog.HEAD[item]
        if style in ("band", "champion_band"):
            shapes = ((1, 112.7, 0, 6.6, 2.6), (1, 112.7, -6.1, 3.15, 2.6))
        elif style in ("kabuto", "legion"):
            shapes = ((1, 120, 0, 8.7, 8.1), (-1, 118, 0, 6.6, 6.6))
        elif style == "eboshi":
            shapes = ((1, 124, 0, 7.45, 7.45), (-1, 123, 0, 5.1, 5.1))
        else:
            shapes = ((2, 0, 0, 15.4, 15.4), (1, 121.3, 0, 7.4, 4.6))
    else:
        shapes = ((1, 102.45, 0, 4.55, 3.75), (1, 102.65, -3.5, 2.35, 2.35))
    return tuple((side, y if side == 2 else pivot[1] + (y - pivot[1]) * scale,
                  z * scale, w * scale, h * scale)
                 for side, y, z, w, h in shapes)


def project(item, slot, garment):
    verts = [Vector(v) for v in garment.verts]
    triangles = [(face[0], face[i], face[i + 1]) for face in garment.faces for i in range(1, len(face) - 1)]
    surface = BVHTree.FromPolygons(verts, triangles, all_triangles=True)
    patches = placements(item, slot)
    skin = c.Skin()
    for colour, (facing, center_y, center_z, width, height) in zip(FACES, patches):
        side = min(facing, 1)
        count = 12
        hits, points, weights = [], [], []
        for j in range(count + 1):
            y = center_y + (j / count - .5) * height
            for i in range(count + 1):
                z = center_z - side * (i / count - .5) * width
                origin, direction = ((-y, 180, z), (0, -1, 0)) if facing == 2 else (
                    (side * 180, y, z), (-side, 0, 0))
                contact, _, index, _ = surface.ray_cast(origin, direction, 360)
                hits.append(len(points) if contact is not None else None)
                if contact is None:
                    continue
                triangle = triangles[index]
                factors = barycentric_transform(contact, *(verts[k] for k in triangle), *BASIS)
                bone_weights = defaultdict(float)
                for k, factor in zip(triangle, factors):
                    for bone, weight in garment.weights[k].items():
                        bone_weights[bone] += weight * max(0., factor)
                strongest = sorted(bone_weights.items(), key=lambda pair: -pair[1])[:4]
                total = sum(value for _, value in strongest)
                weights.append({bone: value / total for bone, value in strongest if value > 0})
                points.append((-y, contact.y + .23, z) if facing == 2 else (contact.x + .23 * side, y, z))
        faces = []
        for j in range(count):
            for i in range(count):
                k = j * (count + 1) + i
                quad = tuple(hits[p] for p in (k, k + 1, k + count + 2, k + count + 1))
                if None not in quad:
                    faces.append(quad)
        if not faces:
            raise ValueError(f"No surface found for {item} decal {colour}")
        skin.add((points, faces), colour, weights)

    def map_uv(colour, position):
        tile = FACES.index(colour)
        facing, center_y, center_z, width, height = patches[tile]
        x, minus_z, y = position
        if facing == 2:
            y = -x
        u = .5 + min(facing, 1) * (minus_z + center_z) / width
        v = .5 + (y - center_y) / height
        return ((tile + .014 + .972 * u) / 2, .014 + .972 * v)

    return skin, map_uv
