"""Check the three fitted helmet envelopes against regenerated native heads."""

import argparse
from pathlib import Path
import struct

import numpy as np
from scipy.spatial import ConvexHull

from install_cave_foes import FITS, HUMAN, STAGE, load_json, read


TYPES = {1: ">f4", 2: ">f2", 3: ">u2", 4: ">i2", 5: "u1", 6: "i1", 7: ">u4", 8: ">i4"}


def mesh(data):
    assert data.startswith(b"SMDL\x00\x01")
    start = 14
    attributes = {}
    for _ in range(data[9]):
        role, kind, _, width, _, _, _, count = struct.unpack_from(">6BII", data, start)
        start += 14
        dtype = np.dtype(TYPES[kind])
        attributes[role] = np.ndarray((count, width), dtype=dtype, buffer=data, offset=start)
        start += count * width * dtype.itemsize
    assert 0 in attributes and 6 in attributes
    return attributes[0], start + 5, data[start + 4]


def fit_under_shell(source, shell):
    """Trim only crown triangles beyond the upper helmet shell envelope."""
    points, cursor, groups = mesh(source)
    shell_points, _, _ = mesh(shell)
    upper_shell = shell_points[shell_points[:, 1] >= 116.0]
    planes = ConvexHull(upper_shell).equations
    exposed = np.zeros(len(points), dtype=bool)
    crown = points[:, 1] >= 118.0
    exposed[crown] = np.any(points[crown] @ planes[:, :3].T + planes[:, 3] > 0.65, axis=1)
    out = bytearray(source[:cursor])
    removed = 0
    for _ in range(groups):
        mode, marker, fmt, kind, size, count = struct.unpack_from(">4BII", source, cursor)
        assert mode == 4
        start = cursor + 12
        end = start + size
        indices = np.frombuffer(source, dtype=TYPES[kind], count=count, offset=start).reshape(-1, 3)
        keep = ~np.any(exposed[indices], axis=1)
        assert np.count_nonzero(keep) > np.count_nonzero(~keep) * 100, "Crown is too far from the existing shell"
        chosen = indices[keep]
        out.extend(struct.pack(">4BII", mode, marker, fmt, kind, chosen.nbytes, chosen.size))
        out.extend(chosen.tobytes())
        out.extend(source[end:end + 4])
        cursor = end + 4
        removed += np.count_nonzero(~keep)
    out.extend(source[cursor:])
    return bytes(out), removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Directory containing project/")
    args = parser.parse_args()
    human = load_json(args.target, HUMAN / "index.json")
    dest = STAGE / HUMAN
    dest.mkdir(parents=True, exist_ok=True)
    for key, fit in FITS.items():
        if not fit.helmet_face:
            continue
        donor = human[fit.donor]["face"]
        visor = human[key]["hat"]
        source = read(args.target, HUMAN / f"{donor}.mdl")
        shell = read(args.target, HUMAN / f"{visor}.mdl")
        fitted, removed = fit_under_shell(source, shell)
        variant = f"{key}_fitted_portrait_under_kabuto"
        pm = read(args.target, HUMAN / f"{donor}.pm").replace(
            f'"{donor}.mdl"'.encode(), f'"{variant}.mdl"'.encode()
        )
        (dest / f"{variant}.pm").write_bytes(pm)
        (dest / f"{variant}.mdl").write_bytes(fitted)
        print(f"{key} {donor} helmet-crown trim {removed} triangles")


if __name__ == "__main__":
    main()
