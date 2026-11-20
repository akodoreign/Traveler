"""Clean isolated fluorescent RGB leakage from the generated dragon's surface atlas."""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import trimesh


def repair(src, out):
    mesh, = trimesh.load_scene(src, process=False).dump()
    atlas = np.asarray(mesh.visual.material.baseColorTexture.convert("RGB"))
    r, g, b = atlas.astype(np.int16).transpose(2, 0, 1)
    red = (r > 125) & (r - np.maximum(g, b) > 76)
    green = (g > 129) & (g - np.maximum(r, b) > 45)
    mask = cv2.dilate((red | green).astype(np.uint8), np.ones((3, 3), np.uint8))
    fixed = cv2.inpaint(atlas, mask, 5, cv2.INPAINT_TELEA)
    Image.fromarray(fixed).save(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("atlas", type=Path)
    args = parser.parse_args()
    repair(args.source,args.atlas)

