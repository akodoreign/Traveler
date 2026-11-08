"""Upright guide sheets for the AI sprites (never touches the game's sheets or registry).
python -E tools/gen_upright_guides.py natsuko rensei      travelers by key
python -E tools/gen_upright_guides.py --all               every sheet of the AI run: travelers, side cast, human enemies, looks
Writes _art/preview/agents/pixelai/guides/<sheet>: a copy of the game's sheet with only the standing blocks
(gen_sprites2d.UPRIGHT_KINDS, 48 of the 154 frames) redrawn upright, so every other frame is the game's own pixels.
guides/<sheet>.changed.json lists the frames that really differ. Already rendered sheets are skipped unless --force.
"""
import json
import os
import sys
import time

os.environ["RT_UPRIGHT"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import gen_sprites2d as s  # noqa: E402
import gen_sidecast as sc  # noqa: E402
import gen_human_enemies as he  # noqa: E402
sys.argv = _argv

GUIDES = os.path.join(HERE, "..", "_art", "preview", "agents", "pixelai", "guides")
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
PIC = os.path.join(RES, "enemy_pic")
FW, FH, COLS = s.FW, s.FH, s.COLS


def targets(keys, every):
    out = {}
    trav = {t["key"]: t for t in s.TRAVELERS}
    for k, t in trav.items():
        if every or k in keys:
            out["trav_%s.png" % k] = t
    if every:
        for c in sc.CAST:                                   # a repeated key: the last entry wrote the file
            out["side_%s.png" % c["key"]] = sc.config(c)
        for c in he.ENEMIES:
            out["hum_%s.png" % c["key"]] = he.config(c)
        ep = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
        for ti, T in enumerate(s.TRAVELERS):
            for combo, epid, w, h in s.look_combos(ti, T):
                pic = os.path.basename((ep.get(epid) or {}).get("pic3d", ""))
                if pic and epid != "EP%03d" % (200 + ti):
                    out[pic] = s.look_variant(T, w, h)
    return out


def main():
    a = sys.argv[1:]
    every, force = "--all" in a, "--force" in a
    keys = [k for k in a if not k.startswith("--")]
    os.makedirs(GUIDES, exist_ok=True)
    work = targets(keys, every)
    idxs = [n for n, (kind, _) in enumerate(s.FRAMES) if kind in s.UPRIGHT_KINDS]
    t0 = time.time()
    done, missing = 0, []
    for sheet, T in work.items():
        out = os.path.join(GUIDES, sheet)
        src = os.path.join(PIC, sheet)
        if not os.path.exists(src):
            missing.append(sheet)
            continue
        if os.path.exists(out) and os.path.exists(out + ".changed.json") and not force:
            continue
        cur = np.asarray(Image.open(src).convert("RGBA"))
        new = cur.copy()
        changed = []
        for n in idxs:
            kind, i = s.FRAMES[n]
            r, c = n // COLS, n % COLS
            box = (r * FH, (r + 1) * FH, c * FW, (c + 1) * FW)
            fr = s.frame(T, kind, i)
            new[box[0]:box[1], box[2]:box[3]] = fr
            if not (fr == cur[box[0]:box[1], box[2]:box[3]]).all():
                changed.append(n)
        Image.fromarray(new, "RGBA").save(out + ".tmp.png")
        os.replace(out + ".tmp.png", out)
        json.dump(changed, open(out + ".changed.json", "w"))
        done += 1
        if done % 50 == 0:
            print(done, "sheets", int(time.time() - t0), "s", flush=True)
    print("rendered", done, "of", len(work), "in", int(time.time() - t0), "s; missing source sheets:", missing[:10])


if __name__ == "__main__":
    main()
