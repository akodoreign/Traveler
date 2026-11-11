"""Hand-pick a candidate as a sheet's frame (the runner picks the least noisy candidate, which can be one turned the
wrong way - Hida Sachiko's first idle frame looked left, 2026-11-11). The picked frame anchors the following frames.
python -E tools/pixelai_pick.py side_sachiko 0 1100      (sheet key, frame, candidate seed: cand/f000_s1100.png)
Deletes the later frames of the same animation so they are redrawn from the new one. Stop pixelai_redo first."""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixeldrive as pd  # noqa: E402
sys.argv = _argv


def main():
    key, i, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    sp = json.load(open(os.path.join(pd.SPECS, "%s.json" % key)))
    od = os.path.join(pd.SHEETS, key)
    rig = pd.ps.frame(sp["sheet"], i)
    q, idx = pd.Pal(sp).quantize(Image.open(os.path.join(od, "cand", "f%03d_s%d.png" % (i, seed))).convert("RGBA"), rig)
    pd.save_frame(q, idx, os.path.join(od, "f%03d.png" % i))
    for a in pd.animap(sp["sheet"]):                       # later frames of the animation(s) holding frame i
        if a["st"] <= i < a["en"]:
            for j in range(i + 1, a["en"]):
                for p in (os.path.join(od, "f%03d.png" % j), os.path.join(od, "f%03d.png.npy" % j)):
                    if os.path.exists(p):
                        os.remove(p)
    print("picked", key, i, seed)


if __name__ == "__main__":
    main()
