"""Build Madame Hagi's pinned lacquer flower in the production head's rest space."""

import argparse
from pathlib import Path
import struct

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals


NAME = "side_hagi_flower_comb"
DTYPES = {1: ">f4", 4: ">i2", 5: "u1"}
PALETTE = {
    "lacquer": ((101, 26, 31), .36, 0),
    "crimson": ((176, 27, 46), .66, 0),
    "red": ((206, 43, 60), .63, 0),
    "rose": ((222, 64, 72), .63, 0),
    "cord": ((164, 31, 47), .76, 0),
    "cord_shadow": ((126, 23, 36), .76, 0),
    "brass": ((227, 167, 71), .33, .35),
}


def oval(center, axes, radii):
    mesh = trimesh.creation.icosphere(subdivisions=2)
    mesh.vertices = (mesh.vertices * radii) @ np.asarray(axes) + center
    mesh.fix_normals()
    return mesh


def tube(points, radius, color, parts):
    for start, end in zip(points[:-1], points[1:]):
        parts[color].append(trimesh.creation.cylinder(radius=radius, segment=[start, end], sections=8))
    for point in points[1:-1]:
        parts[color].append(oval(point, np.eye(3), (radius,) * 3))


def make_comb(side):
    face = np.array([.48, .14, side * .86])
    face /= np.linalg.norm(face)
    up = np.array([0., 1., 0.]) - face[1] * face
    up /= np.linalg.norm(up)
    across = np.cross(up, face) * side
    center = np.array([.45, 117.65, side * 5.90])
    parts = {name: [] for name in PALETTE}
    axes = (across, up, face)
    parts["lacquer"].append(oval(center - .23 * face, axes, (1.42, .90, .34)))
    for slot in (-1., -.5, 0., .5, 1.):
        root = center + slot * across - .48 * up - .38 * face
        tip = root - 1.65 * face - .80 * up - .34 * across
        tube([root, (root + tip) / 2 - .18 * up, tip * .90 + root * .10], .105, "lacquer", parts)

    for count, spread, depth, offset, labels in (
        (6, 1.12, .16, .10, ("crimson", "red", "crimson")),
        (5, .69, .40, .53, ("red", "rose", "red")),
    ):
        for i in range(count):
            angle = i * (2 * np.pi / count) + offset
            radial = across * np.cos(angle) + up * np.sin(angle)
            tangent = -across * np.sin(angle) + up * np.cos(angle)
            petal = center + radial * spread + face * depth
            parts[labels[i % len(labels)]].append(
                oval(petal, (radial + .16 * face, tangent, face), (.84 * spread, .57 * spread, .26))
            )
    parts["lacquer"].append(oval(center + .60 * face, axes, (.46, .46, .20)))
    for i in range(9):
        angle = i * 2 * np.pi / 9
        stamen = center + .81 * face + .32 * (np.cos(angle) * across + np.sin(angle) * up)
        parts["brass"].append(oval(stamen, axes, (.105, .105, .079)))
    parts["brass"].append(oval(center + .87 * face, axes, (.17, .17, .10)))

    for i, (angle, width) in enumerate(((.56, .51), (-.46, .42))):
        lift = np.cos(angle) * up + np.sin(angle) * across
        span = -np.sin(angle) * up + np.cos(angle) * across
        loop = [center - .32 * face + lift * (.27 + 1.08 * (1 - np.cos(t))) + span * width * np.sin(t)
                for t in np.linspace(0, 2 * np.pi, 25)]
        tube(loop, .13, "cord" if i == 0 else "cord_shadow", parts)

    cord = [[-.70, 117.0, 6.34], [-1.44, 115.4, 6.87], [-2.26, 113.7, 7.48],
            [-2.82, 112.05, 7.95], [-2.97, 110.70, 8.15]]
    cord = np.asarray(cord) * [1, 1, side]
    tube(cord, .16, "cord", parts)
    tie = cord[-1]
    parts["brass"].append(oval(tie, np.eye(3), (.35, .38, .31)))
    for i in range(11):
        angle = i * 2 * np.pi / 11
        strand = np.array([np.cos(angle), 0, np.sin(angle) * side])
        points = [tie + strand * .11 + [0, -.19, 0],
                  tie + strand * .27 + [-.20, -1.06, side * .13],
                  tie + strand * .47 + [-.34, -2.93 + .25 * np.sin(angle * 3), side * .18]]
        tube(points, .125, "cord" if i % 3 else "cord_shadow", parts)

    return {color: trimesh.util.concatenate(meshes) for color, meshes in parts.items()}


def export_native(meshes, reference, output):
    vertices = np.vstack([mesh.vertices for mesh in meshes.values()])
    normals = np.vstack([mesh.vertex_normals for mesh in meshes.values()])
    count = len(vertices)
    assert 0 < count < 65536
    indices = np.zeros((count, 4), dtype="u1")
    weights = indices.copy()
    weights[:, 0] = 255
    columns = {0: vertices.astype(">f4"), 1: np.rint(normals * 32767).astype(">i2"),
               4: np.zeros((count, 2), dtype=">f4"), 6: indices, 7: weights}
    original = reference.read_bytes()
    stride = struct.unpack_from(">I", original, 10)[0] // struct.unpack_from(">I", original, 24)[0]
    data = bytearray(original[:10]) + struct.pack(">I", count * stride)
    offset = 14
    for _ in range(original[9]):
        role, kind, _, dim, _, _, _, length = struct.unpack_from(">6BII", original, offset)
        assert columns[role].dtype == np.dtype(DTYPES[kind])
        data.extend(original[offset:offset + 10] + struct.pack(">I", count) + columns[role].tobytes())
        offset += 14 + np.dtype(DTYPES[kind]).itemsize * dim * length
    data.extend(struct.pack(">IB", 0, len(meshes)))
    first = 0
    for mesh in meshes.values():
        faces = (mesh.faces + first).astype(">u2")
        data.extend(struct.pack(">4BII", 4, 0, 0, 3, faces.nbytes, faces.size))
        data.extend(faces.tobytes() + struct.pack(">I", 0))
        first += len(mesh.vertices)
    data.extend(struct.pack(">IBH", 0, 1, 4) + b"head" + struct.pack(">IBI", 0, 0, 0))
    (output / f"{NAME}.mdl").write_bytes(data)

    # Native bounds are expressed as center and half extents.
    low, high = vertices.min(axis=0), vertices.max(axis=0)
    bounds = ", ".join(f"{value:.6f}" for value in np.r_[(low + high) / 2, (high - low) / 2])
    materials = []
    scene = trimesh.Scene()
    for color, mesh in meshes.items():
        rgb, rough, metal = PALETTE[color]
        linear = "".join(f"{round(255 * (v / 255) ** 2.2):02x}" for v in rgb)
        materials.append(f'''\t{{
\t\tname = "{color}"
\t\ttec = "pbr.basic"
\t\tmtype = 0
\t\tbasecol = 0x{linear}ff
\t\trough = {rough:.3f}
\t\tmetal = {metal:.3f}
\t\tmparam = 0xff000000
\t\ttexmap = 0x00000000
\t\ttexture0 = null
\t\ttexture1 = null
\t\ttexture2 = null
\t}}''')
        mesh.visual = TextureVisuals(material=PBRMaterial(name=color, baseColorFactor=[*rgb, 255],
                                                         roughnessFactor=rough, metallicFactor=metal))
        scene.add_geometry(mesh, node_name=color, geom_name=color)
    blocks = "\n".join(materials)
    (output / f"{NAME}.pm").write_text(
        f'return {{\nmodeldata = "{NAME}.mdl"\nbnd = [{bounds}]\nmaterial = [\n{blocks}\n]\n}}\n',
        encoding="utf-8",
    )
    scene.export(output / f"{NAME}.glb")
    print(f"Built {NAME}: {count} head-bound vertices, {len(meshes)} material groups")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ornament_folder", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--side", type=int, choices=(-1, 1), default=1)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True, parents=True)
    export_native(make_comb(args.side), args.ornament_folder / "side_hagi_sash.mdl", args.output)
