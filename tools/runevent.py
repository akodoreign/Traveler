"""Run one event page unattended and print what it said (no keys, no focus).
python -E tools/runevent.py M143 2 0 [--vars G200,G201] [--choice 0,1] [--wait 25] [--lv 20] [--party P123]
python -E tools/runevent.py --list M143          (event ids, roles, positions, models and page reqs)
Launches rpgcobo -testplay -event MAP ID PAGE with -rtfast (messages are logged, not waited on), waits until the log
goes quiet, kills the game and prints the [RT] lines and any errors. Log: _art/preview/event_<map>_<id>.txt"""
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


def listing(mid):
    _m, ev = gm.make(mid)
    for key, e in ev.ev.items():
        reqs = [p.get("reqs") for p in e.get("pages", [])] if e.get("pages") else e.get("reqs0")
        print("%-5s %-9s pos=%-16s mdl=%-7s reqs=%s" % (key.strip("#"), e["role"], e.get("pos"),
                                                       e.get("mdlid", ""), reqs))


def run(mid, eid, page, rtvar, choice, wait, quiet=6.0, lv="", party="", rt=""):
    engine_lock.wait_free()                                              # (single-instance engine: never kill one this script did not start)
    log = os.path.join(HERE, "..", "_art", "preview", "event_%s_%s.txt" % (mid, eid))
    args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-event", mid, str(eid), str(page), "-rtfast",
            "-rtauto", "-debuglv", lv or "9"]                   # the debug level is also the party's level
    packed = []                                         # the engine passes only 13 arguments: pack the rest
    if rtvar:
        packed.append("var " + rtvar)
    if choice:
        packed.append("choice " + choice)
    if party:
        packed.append("party " + party)
    if rt:
        packed.append(rt)
    if packed:
        args += ["-rt", ";".join(packed)]
    with open(log, "w") as lf:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    t0, last, size = time.time(), time.time(), 0
    while time.time() - t0 < wait:
        time.sleep(1.0)
        s = os.path.getsize(log)
        if s != size:
            size, last = s, time.time()
        elif time.time() - last > quiet and time.time() - t0 > 8:
            break
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    lines = open(log, errors="replace").read().splitlines()
    rt = [ln for ln in lines if "[RT]" in ln]
    errs = [ln for ln in lines if "ERROR" in ln or "xception in thread" in ln]
    for ln in rt:
        print(ln[ln.index("[RT]"):][:200])
    print("-- %s #%s page %s: %d RT lines, %d errors" % (mid, eid, page, len(rt), len(errs)))
    for e in errs[:5]:
        print("   ", e[:200])
    return rt, errs


def main():
    a = sys.argv[1:]
    if a and a[0] == "--list":
        listing(a[1])
        return
    opts = {"--vars": "", "--choice": "", "--wait": "40", "--lv": "", "--party": "", "--rt": ""}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1]
            a = a[:i] + a[i + 2:]
    run(a[0], a[1], a[2] if len(a) > 2 else "0", opts["--vars"], opts["--choice"], float(opts["--wait"]),
        lv=opts["--lv"], party=opts["--party"], rt=opts["--rt"])


if __name__ == "__main__":
    main()
