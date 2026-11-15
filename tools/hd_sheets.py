"""Point the game at the HD character sheets (user 2026-11-15: "upscale these a small bit to use in game").

tools/fix_sheet.py --install writes resource/enemy_pic2x/<key>.png: the remastered 14x11 sheet at 2x + a 12th row of
conversation gestures (tools/rig_anim.py GESTURES). The 1x resource/enemy_pic/<key>.png stays the tools' working copy.
For every enemy_pic.json entry whose sheet has an HD copy this sets:
  pic3d  -> /resource/enemy_pic2x/<key>.png      scale -> scale1x / 2 (scale1x kept, so the in-game size is the same)
  aniuv  -> [14, 12]                             animap + facepalm / shrug / crossarms / scratch / point (frames 154+)
Idempotent (re-run after any tool rewrites an entry: the watcher tools/fix_new_sheets.py does). Locked + atomic.
  python -E tools/hd_sheets.py [--dry] [key ...]"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
JP = os.path.join(RES, "enemy_pic.json")
LOCK = JP + ".lock"
HD_ROWS = {}
GESTURES = [("facepalm", 4, 5.0), ("shrug", 3, 5.0), ("crossarms", 2, 4.0), ("scratch", 3, 7.0), ("point", 2, 5.0)]


def lock():
    for _ in range(600):
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            if time.time() - os.path.getmtime(LOCK) > 120:   # a stale lock (a crashed writer)
                os.remove(LOCK)
            time.sleep(0.2)
    return False


def main():
    a = sys.argv[1:]
    dry = "--dry" in a
    only = {k for k in a if not k.startswith("--")}
    if not lock():
        print("enemy_pic.json is locked; try again")
        return
    try:
        j = json.load(open(JP, encoding="utf-8"))
        n = 0
        for eid, e in j.items():
            if not isinstance(e, dict) or not e.get("pic3d"):
                continue
            key = os.path.basename(e["pic3d"])[:-4]
            if only and key not in only:
                continue
            hd = os.path.join(RES, "enemy_pic2x", key + ".png")
            if not os.path.exists(hd) or e.get("aniuv") not in ([14, 11], [14, 12], [14, 13]):
                continue
            rows = HD_ROWS.get(hd)
            if rows is None:
                from PIL import Image
                with Image.open(hd) as im:
                    rows = HD_ROWS[hd] = int(round(im.size[1] / 136.0))
            want_pic = "/resource/enemy_pic2x/%s.png" % key
            if "scale1x" not in e:
                e["scale1x"] = e.get("scale", 1.0)
            changed = e["pic3d"] != want_pic or e.get("aniuv") != [14, rows] or \
                abs(e.get("scale", 0) - e["scale1x"] / 2.0) > 1e-9
            e["pic3d"] = want_pic
            e["scale"] = e["scale1x"] / 2.0
            e["aniuv"] = [14, rows]
            have = {x["id"] for x in e.get("animap", [])}
            st = 154
            for suffix, row in (("", 12), ("_f", 13)):              # side gestures row 12, front-view row 13
                st = 14 * (row - 1)
                for gid, cnt, spd in GESTURES:
                    if row <= rows and gid + suffix not in have:
                        e.setdefault("animap", []).append({"id": gid + suffix, "st": st, "en": st + cnt,
                                                           "spd": spd, "loop": False, "replay": False})
                        changed = True
                    # the held last pose (looping: the engine keeps a looping event animation locked) - the
                    # gesture stays through the line it goes with (gen_maps gestures())
                    if row <= rows and gid + "_hold" + suffix not in have:
                        e.setdefault("animap", []).append({"id": gid + "_hold" + suffix, "st": st + cnt - 1,
                                                           "en": st + cnt, "spd": 1.0, "loop": True,
                                                           "replay": False})
                        changed = True
                    st += cnt
            n += changed
        print("HD entries updated:", n)
        if not dry and n:
            tmp = JP + ".tmp"
            json.dump(j, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
            os.replace(tmp, JP)
    finally:
        os.remove(LOCK)


if __name__ == "__main__":
    main()
