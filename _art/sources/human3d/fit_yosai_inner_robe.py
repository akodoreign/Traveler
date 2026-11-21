"""Recess the inner panel below Yosai's open chest while retaining its skin weights."""
import argparse
from pathlib import Path

import numpy as np

from fit_yosai_neckline import attributes, normalized, smooth


def recess_panel(vertices):
    front, height, lateral = vertices.T
    opening = 3.1+1.1*smooth((height-85.5)/6.0)
    inner = 1.0-smooth((abs(lateral)-opening)/1.55)
    exposed = smooth((height-81.8)/5.2)
    front_panel = smooth((front+.45)/3.6)
    points = vertices.copy()
    points[:, 0] -= 4.5*inner*exposed*front_panel
    return points


def fit(source, output):
    data = bytearray(source.read_bytes())
    mesh, _ = attributes(data)
    rest = mesh[0].astype(float)
    moved = recess_panel(rest)
    selection = np.any(abs(moved-rest) > 1e-6, axis=1)
    if not 5 < selection.sum() < .35*len(rest):
        raise ValueError(f"Unexpected inner panel extent for {source.name}")
    selected = rest[selection]
    jacobian = np.stack([(recess_panel(selected+axis)-recess_panel(selected-axis))/.002
                         for axis in np.eye(3)*.001], -1)
    # The coordinate blend can fold the hidden panel inward. Transform normals
    # only where the local frame remains well conditioned.
    stable = np.linalg.det(jacobian) > .12
    index = np.flatnonzero(selection)[stable]
    differential = jacobian[stable]
    inverse = np.swapaxes(np.linalg.inv(differential), 1, 2)
    normal = normalized(np.einsum("nij,nj->ni", inverse, mesh[1][index]/32767.0))
    mesh[0][selection] = moved[selection]
    mesh[1][index] = np.rint(normal*32767.0)
    if 8 in mesh:
        tangent = normalized(np.einsum("nij,nj->ni", differential, mesh[8][index, :3]/32767.0))
        mesh[8][index,:3] = np.rint(tangent*32767.0)
    output.write_bytes(data)
    print(f"{source.name} recessed {selection.sum()} inner-panel vertices")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name in ("side_yosai_signature.mdl", "side_yosai_signature_decal.mdl"):
        fit(args.source/name, args.output/name)
