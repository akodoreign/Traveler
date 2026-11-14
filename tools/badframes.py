"""Find bad animation frames (user, 2026-11-11: "bad animation frames ... like the togashi's head"): AI-drawn sheets
sometimes have a frame with two heads (the figure turned halfway, a ghost of the last pose). Within each animation the
head band - the top quarter of the figure - keeps about the same width; a frame whose head band is much wider (or that
is much wider overall) than the animation's median is flagged.
python -E tools/badframes.py EP309 [...] [--all] [--fix]
  --all  every sprite in enemy_pic.json;  --fix  replace each flagged frame with the nearest good one in its animation
  (the sheet is backed up once as NAME.orig.png next to it)."""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image
from atomic_io import save_png, copy_file  # noqa: E402  (atomic writes: the game may be running)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
ORIG = os.path.join(HERE, "..", "_art", "frame_orig")                    # each sheet as drawn, before frame fixes
LOOPS = {"stand", "fight", "idle", "sick", "walk", "run", "dash"}             # the ones a player watches loop


def measure(fr):
    a = np.asarray(fr)[..., 3] > 40
    ys, xs = np.nonzero(a)
    if len(ys) < 20:
        return None
    top, bot = ys.min(), ys.max()
    band = a[top:top + max(3, (bot - top) // 4)]
    cols = np.nonzero(band.any(0))[0]
    return {"head": int(cols.max() - cols.min() + 1) if len(cols) else 0, "h": int(bot - top + 1)}


def check(epid, pics, fix=False):
    e = pics[epid]
    path = os.path.join(RES, "enemy_pic", os.path.basename(e["pic3d"]))
    im = Image.open(path).convert("RGBA")
    cols, rows = e.get("aniuv") or (14, 11)
    fw, fh = im.size[0] // cols, im.size[1] // rows
    box = lambda i: ((i % cols) * fw, (i // cols) * fh, (i % cols + 1) * fw, (i // cols + 1) * fh)  # noqa: E731
    m = {}
    bad = {}
    for a in e.get("animap", []):
        if not isinstance(a, dict) or a.get("id") not in LOOPS or a["en"] - a["st"] < 3:
            continue
        idx = [i for i in range(a["st"], a["en"]) if i < cols * rows]
        for i in idx:
            if i not in m:
                m[i] = measure(im.crop(box(i)))
        vals = [m[i]["head"] for i in idx if m[i]]
        if len(vals) < 3:
            continue
        med = float(np.median(vals))
        for i in idx:
            if m[i] and m[i]["head"] > med * 1.3 + 2:
                bad.setdefault(i, []).append("%s head %d vs %d" % (a["id"], m[i]["head"], med))
    if fix and bad:
        orig = path[:-4] + ".orig.png"
        if not os.path.exists(orig):
            shutil.copy(path, orig)
        for i in sorted(bad):
            anim = next(a for a in e["animap"] if isinstance(a, dict) and a.get("st", 0) <= i < a.get("en", 0)
                        and a.get("id") in LOOPS)
            good = [j for j in range(anim["st"], anim["en"]) if j not in bad]
            if good:
                j = min(good, key=lambda g: abs(g - i))
                im.paste(im.crop(box(j)), box(i)[:2])
        save_png(im, path)
    return bad


def apply_fixes(pics):
    """tools/frame_fixes.json: copy each listed good frame over the bad one (from the .orig.png, so it repeats safely)."""
    fixes = json.load(open(os.path.join(HERE, "frame_fixes.json"), encoding="utf-8"))
    # One pass per SHEET, not per EP: two EPs can share a sheet (EP309 Togashi Yosai + EP709, EP342 Gonta + EP742
    # Wrestler). Applied one after the other, the second saw the first's fixes as "redrawn since", took them as the
    # original and re-copied only its own frames - so the two maps fought (2026-11-11). Merge them (bigger map wins).
    # (lead 2026-11-14) AI-drawn human-enemy sheets (hum_*, pixelai/sheets/hum_<key>/complete) get the standard fix
    # automatically, like the side cast: idle head-turn 0,1,6,7 <- 3,2,5,4 and the turned first/last walk frames
    # 8 <- 9, 15 <- 14 (seen on EP514). An explicit frame_fixes.json entry for the EP wins.
    px = os.path.join(HERE, "..", "_art", "preview", "agents", "pixelai", "sheets")
    std = {"0": 3, "1": 2, "6": 5, "7": 4, "8": 9, "15": 14}
    fixes = dict(fixes)
    for epid, e in pics.items():
        pic = os.path.basename(e.get("pic3d", "")) if isinstance(e, dict) else ""
        if pic.startswith("hum_") and epid not in fixes and \
                os.path.exists(os.path.join(px, pic[:-4], "complete")):
            am = {a.get("id"): a for a in e.get("animap", []) if isinstance(a, dict)}
            if am.get("stand", {}).get("en") == 8 and am.get("walk", {}).get("st") == 8:
                fixes[epid] = std
    sheets = {}
    for epid, mp in sorted(fixes.items(), key=lambda kv: len(kv[1]) if isinstance(kv[1], dict) else 0):
        if epid.startswith("_") or epid not in pics:
            continue
        key = os.path.basename(pics[epid]["pic3d"])
        ep0, m0 = sheets.get(key, (epid, {}))
        sheets[key] = (ep0 if key in sheets else epid, {**m0, **mp})
    for key, (epid, mp) in sheets.items():
        e = pics[epid]
        path = os.path.join(RES, "enemy_pic", os.path.basename(e["pic3d"]))
        orig = os.path.join(ORIG, os.path.basename(path))                # (outside the game's resources)
        cur = Image.open(path).convert("RGBA")
        cols, rows = e.get("aniuv") or (14, 11)
        fw, fh = cur.size[0] // cols, cur.size[1] // rows
        box = lambda i: ((i % cols) * fw, (i // cols) * fh, (i % cols + 1) * fw, (i // cols + 1) * fh)  # noqa: E731
        if os.path.exists(orig):                                            # redrawn since (the sprite runner)? then
            o = Image.open(orig).convert("RGBA")                            # the new drawing is the original
            keep = [i for i in range(cols * rows) if str(i) not in mp]
            if o.size != cur.size or any(np.asarray(o.crop(box(i))).tobytes() != np.asarray(cur.crop(box(i))).tobytes()
                                         for i in keep):    # every frame (2026-11-12: [:20] missed changes
                # past frame 20 - anim_harmonize's attack / cast frames, the ref pass - and put the old drawing back)
                shutil.copy(path, orig)
        else:
            os.makedirs(ORIG, exist_ok=True)
            shutil.copy(path, orig)
        im = Image.open(orig).convert("RGBA")
        src = im.copy()
        for bad, good in mp.items():
            im.paste(src.crop(box(int(good))), box(int(bad))[:2])
        save_png(im, path)
        print("fixed", epid, len(mp), "frames")


def main():
    a = sys.argv[1:]
    fix = "--fix" in a
    pics = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
    if "--apply" in a:
        apply_fixes(pics)
        # the travelers' weapon / hat look sheets are built from the (now fixed) AI base sheets (user 2026-11-12:
        # katana look showed the old art); always the last step after install_aisheets / anim_harmonize
        import look_hybrid
        look_hybrid.main()
        return
    ids = [k for k in pics if isinstance(pics[k], dict) and pics[k].get("pic3d")] if "--all" in a else \
        [x for x in a if not x.startswith("--")]
    n = 0
    for ep in ids:
        try:
            bad = check(ep, pics, fix)
        except (OSError, KeyError) as ex:
            print(ep, "skip:", ex)
            continue
        if bad:
            n += 1
            print(ep, pics[ep].get("name", {}).get("ja", ""), {k: v for k, v in sorted(bad.items())})
    print("%d sprites with flagged frames%s" % (n, " (fixed)" if fix else ""))


if __name__ == "__main__":
    main()
