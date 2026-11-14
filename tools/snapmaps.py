"""Unattended screenshots of maps (no keypresses, no focus): launches rpgcobo -testplay -map for each entry, waits
for the arrival log line, captures the game window with wincap, and kills the game.
python -E tools/snapmaps.py "M146:20,10" "M141:54,40" ... [--vars G010,G054,...]
Block coordinates; padded maps (exteriors) are converted with gen_maps.world(). Output _art/preview/snap_<map>.png"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_lock  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402

TOOL = gm.TOOL


def snap(mid, x, z, rtvar, wait=4.0):
    padded = not (mid in gm.INTERIORS or mid in gm.ROOM_DIMS)
    if mid in gm.ROOM_DIMS:
        pos = gm.world(mid, x, z, 0.0, padded=False)
    elif mid in gm.INTERIORS:
        gm.make(mid)
        ox, oz = gm.ROOM_OFS[mid]
        pos = [(x + ox) / 2.0, None, (z + oz) / 2.0, 0.0]
    else:
        pos = gm.world(mid, x, z, 0.0, padded=True)
    mm, _ev = gm.make(mid)                                  # make() builds dependencies and pads exteriors
    if padded:
        h = int(mm.hgt[int(z + gm.PAD_BOTTOM), int(x + gm.PAD_X)])
    else:
        ox, oz = gm.ROOM_OFS.get(mid, (0, 0))
        h = int(mm.hgt[int(z + oz), int(x + ox)])
    pos[1] = (h + 1) / 2.0
    engine_lock.wait_free()                                              # (single-instance engine: never kill one this script did not start)
    log = os.path.join(gm.HERE, "..", "_art", "preview", "snap_%s.txt" % mid)
    with open(log, "w") as lf:
        os.makedirs(os.path.join(TOOL, "tmp", "rt_shot"), exist_ok=True)
        raw = os.path.join(TOOL, "tmp", "rt_shot", "snap_%s.raw" % mid)          # the game may only write here
        if os.path.exists(raw):
            os.remove(raw)
        proc = engine_lock.launch([os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-map", mid,
                                 "[%.1f,%.2f,%.1f,0.0]" % (pos[0], pos[1], pos[2]), "-rtvar", rtvar, "-rtfast",
                                 "-rtshot", "tmp/rt_shot/snap_%s.raw" % mid, str(int(wait * 1000) + 3000)],
                                cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    t0 = time.time()
    while time.time() - t0 < 90 and not (os.path.exists(raw) and os.path.getsize(raw) > 8):
        time.sleep(1.0)
    time.sleep(1.0)
    out = os.path.join(gm.HERE, "..", "_art", "preview", "snap_%s.png" % mid)
    if os.path.exists(raw):
        import numpy as np
        from PIL import Image
        b = open(raw, "rb").read()
        w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
        a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
        Image.fromarray(a[..., :3].copy(), "RGB").save(out)
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    errs = [l for l in open(log, errors="replace").read().splitlines() if "ERROR" in l or "xception in thread" in l]
    print(mid, out, "errors:", len(errs))
    for e in errs[:3]:
        print("   ", e[:160])


def main():
    rtvar = "G010,G011,G012,G013,G054"
    args = sys.argv[1:]
    if "--vars" in args:
        i = args.index("--vars")
        rtvar = args[i + 1]
        args = args[:i] + args[i + 2:]
    for a in args:
        mid, xz = a.split(":")
        x, z = (float(v) for v in xz.split(","))
        snap(mid, x, z, rtvar)


if __name__ == "__main__":
    main()
