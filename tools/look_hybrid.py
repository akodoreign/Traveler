"""Traveler look sheets (weapon / hat variants, RokuganLook) on the new AI art until their own AI sheets are drawn
(user 2026-11-12: "When you swap to katana on the Hiruma it goes back to the original pixel art not the new ones").

The look sheet and the base sheet come from the same procedural rig, so the body is posed identically; only the
weapon (and hat) pixels differ. Per frame: start from the installed AI base frame, clear the pixels where the
procedural base differs from the procedural look (the old weapon, a little grown), and draw the procedural look's
pixels there (the new weapon / hat). Where the AI frame wandered from the rig, the AI pixels stay.
A look whose own AI sheet is finished (pixelai/sheets/<trav>__<w>_<h>/complete) is left to install_aisheets.

    python -E tools/look_hybrid.py [natsuko ...]      (default: every traveler with an installed AI base sheet)
Originals: the procedural look sheets are kept once in _art/frame_orig/looks/ (the input on every rerun)."""
import json
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_sprites2d as s2  # noqa: E402
sys.argv = _argv
from atomic_io import save_png  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, ".."))
PIC = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource", "enemy_pic")
EPJ = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource", "enemy_pic.json")
PX = os.path.join(ROOT, "_art", "preview", "agents", "pixelai")
BASE_ORIG = os.path.join(PX, "game_sheets_orig")              # the procedural base, kept by install_aisheets
LOOK_ORIG = os.path.join(ROOT, "_art", "frame_orig", "looks")


def hybrid(base_proc, look_proc, ai):
    b, l, a = (np.asarray(x.convert("RGBA")).astype(np.int16) for x in (base_proc, look_proc, ai))
    diff = np.abs(b - l).sum(2) > 0
    grow = cv2.dilate(diff.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    old_only = grow & (b[..., 3] > 0) & (l[..., 3] == 0)       # the old weapon's pixels (+1 px of AI anti-alias)
    out = a.copy()
    out[old_only] = 0
    new = diff & (l[..., 3] > 0)
    out[new] = l[new]
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def main(keys=None):
    want = set(keys or [])
    ep = json.load(open(EPJ, encoding="utf-8"))
    os.makedirs(LOOK_ORIG, exist_ok=True)
    for ti, T in enumerate(s2.TRAVELERS):
        k = T["key"]
        if want and k not in want:
            continue
        base_sheet = "trav_%s.png" % k
        if not (os.path.exists(os.path.join(PX, "sheets", k, "complete")) and
                os.path.exists(os.path.join(BASE_ORIG, base_sheet))):
            print("skip", k, "(no installed AI base sheet)")
            continue
        bp = Image.open(os.path.join(BASE_ORIG, base_sheet))
        ai = Image.open(os.path.join(PIC, base_sheet))
        n = 0
        for combo, epid, w, h in s2.look_combos(ti, T):
            pic = os.path.basename((ep.get(epid) or {}).get("pic3d", ""))
            if not pic or pic == base_sheet or not os.path.exists(os.path.join(PIC, pic)):
                continue
            if os.path.exists(os.path.join(PX, "sheets", "%s__%s_%s" % (k, w, h or "own"), "complete")):
                continue                                         # its own AI sheet: install_aisheets
            orig = os.path.join(LOOK_ORIG, pic)
            if not os.path.exists(orig):
                shutil.copy(os.path.join(PIC, pic), orig)
            lp = Image.open(orig)
            if lp.size != bp.size:
                print("size mismatch", pic)
                continue
            save_png(hybrid(bp, lp, ai), os.path.join(PIC, pic))
            n += 1
        print(k, n, "look sheets on the AI base")


if __name__ == "__main__":
    main(sys.argv[1:])
