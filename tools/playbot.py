"""Play the game like a player, unattended (no keys sent to Windows, no focus): the in-game test player
(plugin RokuganBot.sk, -rtbot) holds virtual keys, walks to places, talks, and takes screenshots.

python -E tools/playbot.py NAME START_MAP X Z "step; step; ..." [--vars G010,G054] [--lv 20] [--party P120]
                           [--choice 0,1] [--secs 240]
Coordinates are gen_maps block coordinates of the map named in the step (unpadded, as in gen_maps.py):
  goto MAP X Z [MS]   walk there (jumps when blocked, detours, gives up after MS; default 30000)
  rgoto BX BZ [MS]    the same in the built map's block coordinates
  warp MAP BX BZ      teleport (built block coordinates)
  hold KEYS MS | tap KEYS | wait MS | shot NAME | pos | untilmap MAP [MS] | until FLAG [MS] | vars G1 G2
Output: _art/preview/bot/NAME/ (log.txt, NAME_*.png). Prints the [RT] BOT lines, map changes and errors."""
import json
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
KEEP = ("[RT] BOT", "[RT] MSG", "[RT] CHOICE", "[RT] RESCUE", "ERROR", "xception", "[RT] battle", "[RT] travel")


def block(mid, x, z):
    """gen_maps block x, z -> the built map's block coordinates (world * 2)."""
    if mid in gm.ROOM_DIMS:
        p = gm.world(mid, x, z, 0.0, padded=False)
        return p[0] * 2, p[2] * 2
    if mid not in gm.ROOM_OFS:
        gm.make(mid)                                                      # castle floors register their offset here
    if mid in gm.ROOM_OFS:
        ox, oz = gm.ROOM_OFS[mid]
        return x + ox, z + oz
    return x + gm.PAD_X, z + gm.PAD_BOTTOM


def start_pos(mid, bx, bz):
    mm, _ev = gm.make(mid)
    h = int(mm.hgt[int(bz), int(bx)]) if mm.hgt.shape[0] > bz and mm.hgt.shape[1] > bx else 2
    return "[%.1f,%.2f,%.1f,0.0]" % (bx / 2.0, (h + 1) / 2.0, bz / 2.0)


def convert_shots(name, out):
    """The bot's raw screenshots (tmp/rt_shot/bot_NAME_*.raw) -> OUT/NAME_*.png."""
    import numpy as np
    from PIL import Image
    shots = os.path.join(TOOL, "tmp", "rt_shot")
    for f in sorted(os.listdir(shots)):
        if f.startswith("bot_%s_" % name) and f.endswith(".raw"):
            b = open(os.path.join(shots, f), "rb").read()
            w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
            arr = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
            Image.fromarray(arr[..., :3].copy(), "RGB").save(os.path.join(out, f[4:-4] + ".png"))


def launch(name, mid, bx, bz, lines, vars_="", lv="9", party="", choice="", secs=240.0, quiet=False, lead="", extra=None):
    """Run the bot with raw step lines from built block bx, bz on map mid. Returns the log lines kept."""
    out = os.path.join(HERE, "..", "_art", "preview", "bot", name)
    os.makedirs(out, exist_ok=True)
    shots = os.path.join(TOOL, "tmp", "rt_shot")
    os.makedirs(shots, exist_ok=True)
    for f in os.listdir(shots):
        if f.startswith("bot_%s_" % name):
            os.remove(os.path.join(shots, f))
    engine_lock.wait_free()                                              # (single-instance engine: never kill one this script did not start)
    packed = ["bot " + "|".join(ln.replace(" ", ",") for ln in lines)]
    if choice:
        packed.append("choice " + choice)
    if party:
        packed.append("party " + party)
    if lead:
        packed.append("lead " + lead)
    packed += list(extra or [])                                           # more -rt flags ("tank", ...)                                     # (another traveler leads: -rtlead)
    varfile = None
    if len(vars_) > 2000:                                                 # a long list goes through a file
        varfile = os.path.join(TOOL, "tmp", "bot", name + "_vars.txt")
        os.makedirs(os.path.dirname(varfile), exist_ok=True)
        json.dump([v for v in vars_.split(",") if v], open(varfile, "w"))
    args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-map", mid, start_pos(mid, bx, bz), "-rtvar",
            ("@" + os.path.relpath(varfile, TOOL).replace(os.sep, "/")) if varfile else (vars_ or "G000"),
            "-rtfast", "-rtauto", "-debuglv", str(lv), "-rt", ";".join(packed)]
    log = os.path.join(out, "log.txt")
    with open(log, "w") as lf:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    t0 = time.time()
    while time.time() - t0 < secs:
        time.sleep(1.0)
        if "[RT] BOT finished" in open(log, errors="replace").read():
            time.sleep(1.5)
            break
    timed_out = time.time() - t0 >= secs
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    convert_shots(name, out)
    kept = []
    for ln in open(log, errors="replace").read().splitlines():
        if any(k in ln for k in KEEP) and "BOT step" not in ln:
            kept.append(ln[ln.find("[RT]"):][:180] if "[RT]" in ln else ln[:180])
    if not quiet:
        for ln in kept:
            print(ln)
        print("-- log", os.path.normpath(log), "TIMED OUT" if timed_out else "finished")
    return kept, timed_out


def main():
    a = sys.argv[1:]
    opts = {"--vars": "", "--lv": "9", "--party": "", "--choice": "", "--secs": "240"}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1]
            a = a[:i] + a[i + 2:]
    name, mid, x, z, steps = a[0], a[1], float(a[2]), float(a[3]), a[4]
    lines = []
    for st in [s.strip() for s in steps.split(";") if s.strip()]:
        p = st.split()
        if p[0] == "goto":
            bx, bz = block(p[1], float(p[2]), float(p[3]))
            lines.append("goto %.1f %.1f %s" % (bx + 0.5, bz + 0.5, p[4] if len(p) > 4 else "30000"))
        elif p[0] == "rgoto":
            lines.append("goto " + " ".join(p[1:]))
        elif p[0] == "shot":
            lines.append("shot %s_%s" % (name, p[1]))
        else:
            lines.append(st)
    bx, bz = block(mid, x, z)
    launch(name, mid, bx, bz, lines, opts["--vars"], opts["--lv"], opts["--party"], opts["--choice"],
           float(opts["--secs"]))


if __name__ == "__main__":
    main()
