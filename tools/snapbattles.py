"""Unattended screenshots of battles (no keys): one -battle M001 <gid> per group, the game's own -rtshot capture,
and a contact sheet _art/preview/battle_backdrops.png (4 per row, labelled with gid and backdrop).
python -E tools/snapbattles.py [gid ...]          (default: one group per backdrop in use)"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_lock  # noqa: E402

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))
PREVIEW = os.path.join(HERE, "..", "_art", "preview")


def shot(gid, wait_ms=7000):
    engine_lock.wait_free()                                              # (single-instance engine: never kill one this script did not start)
    rel = "tmp/rt_shot/battle_%d_%d.raw" % (gid, int(time.time()))     # a fresh name: nothing to delete first
    raw = os.path.join(TOOL, rel)
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    log = open(os.path.join(PREVIEW, "battle_%d.txt" % gid), "w")
    proc = engine_lock.launch([os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-battle", "M001", str(gid),
                             "-debuglv", "20", "-rtfast", "-rtshot", rel, str(wait_ms)], cwd=TOOL, stdout=log,
                            stderr=subprocess.STDOUT)
    t0 = time.time()
    while time.time() - t0 < 60 and not (os.path.exists(raw) and os.path.getsize(raw) > 8):
        time.sleep(1.0)
    time.sleep(1.0)
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    log.close()
    if not os.path.exists(raw):
        return None
    b = open(raw, "rb").read()
    w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
    a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
    return Image.fromarray(a[..., :3].copy(), "RGB")


def main():
    mp = json.load(open(os.path.join(TOOL, "project", "data", "map.json"), encoding="utf-8"))
    groups = {g["gid"]: g["mapid"] for g in mp["M001"]["encount"]}
    gids = [int(v) for v in sys.argv[1:]]
    if not gids:
        seen = {}
        for gid, bm in sorted(groups.items()):
            seen.setdefault(bm, gid)
        gids = sorted(seen.values())
    sheet = Image.new("RGB", (640 * 4, 360 * ((len(gids) + 3) // 4)), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for n, gid in enumerate(gids):
        im = shot(gid)
        x, y = (n % 4) * 640, (n // 4) * 360
        if im:
            sheet.paste(im.resize((640, 360)), (x, y))
        d.text((x + 8, y + 330), "gid %d  %s%s" % (gid, groups.get(gid), "" if im else "  (no shot)"),
               fill=(255, 255, 0))
        print("gid", gid, groups.get(gid), "ok" if im else "FAILED")
    out = os.path.join(PREVIEW, "battle_backdrops.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
