"""Keep every 14x11 character sheet remastered by tools/fix_sheet.py (user 2026-11-15: "apply across all the cast and
crew, also probably need to do this to all the sheets we have"): the travelers and their look sheets, the side cast,
the npc_ and the hum_ enemies.

  a. a sheet with no fixsheet _before.png yet           -> fix_sheet KEY --install
  b. a sheet whose own AI sheet finished AFTER its _before.png was taken (pixelai/sheets/<spec>/complete newer):
     the AI art never installed (install_aisheets skips remastered sheets), so: drop the _before.png,
     install_aisheets <spec>, fix_sheet KEY --install
Base traveler sheets that change also rebuild their look sheets first (look_hybrid) - the looks are built on them.

  python -E tools/fix_new_sheets.py [--workers 6] [--loop MINUTES] [--log FILE] [--dry]
--loop keeps it running (tools/start_queues.ps1 starts it that way), so sheets the GPU queues finish later get fixed."""
import glob
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
RES = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource")
FIX = os.path.join(ROOT, "_art", "preview", "fixsheet")
PX = os.path.join(ROOT, "_art", "preview", "agents", "pixelai")
SPECS = os.path.join(HERE, "pixelai_specs")


def log(*a):
    print(time.strftime("%m-%d %H:%M"), *a, flush=True)


def sheets():
    j = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
    ks = {os.path.basename(v["pic3d"])[:-4] for v in j.values()
          if isinstance(v, dict) and v.get("aniuv") == [14, 11] and v.get("pic3d")}
    return sorted(k for k in ks if os.path.exists(os.path.join(RES, "enemy_pic", k + ".png")))


def spec_map():
    """sheet key -> AI spec key (pixelai/sheets/<spec>), from every spec's "sheet" path."""
    m = {}
    for p in glob.glob(os.path.join(SPECS, "*.json")) + glob.glob(os.path.join(SPECS, "looks", "*.json")):
        try:
            sp = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        sh = sp.get("sheet") or ""
        if sh:
            m[os.path.basename(sh)[:-4]] = os.path.basename(p)[:-5]
    return m


def run(args):
    r = subprocess.run([PY, "-E"] + args, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout.strip().splitlines() or [""])[-1], r.stderr[-300:]


def fix(key):
    rc, out, err = run([os.path.join(HERE, "fix_sheet.py"), key, "--install"])
    log("fixed" if rc == 0 else "FAILED", key, out if rc == 0 else err)
    return rc == 0


def one_pass(workers, dry):
    smap = spec_map()
    todo, reinstall = [], []
    for k in sheets():
        bk = os.path.join(FIX, k + "_before.png")
        spec = smap.get(k)
        done = os.path.join(PX, "sheets", spec, "complete") if spec else None
        if not os.path.exists(bk):
            todo.append(k)
        elif done and os.path.exists(done) and os.path.getmtime(done) > os.path.getmtime(bk):
            reinstall.append((k, spec))
    log("pass: %d to fix, %d with new AI art" % (len(todo), len(reinstall)))
    if dry:
        log("dry:", todo[:20], reinstall[:10])
        return
    for k, spec in reinstall:                                  # (b) new AI art: install it, then remaster it
        os.remove(os.path.join(FIX, k + "_before.png"))
        rc, out, err = run([os.path.join(HERE, "install_aisheets.py"), spec])
        log("installed AI" if rc == 0 else "install FAILED", k, out if rc == 0 else err)
        todo.append(k)
    bases = sorted({k for k in todo if k.startswith("trav_") and "__" not in k})
    for b in bases:                                            # bases first: their looks are built on them
        fix(b)
    if bases:
        rc, out, err = run([os.path.join(HERE, "look_hybrid.py")] + [b[5:] for b in bases])
        log("looks rebuilt" if rc == 0 else "look_hybrid FAILED", out if rc == 0 else err)
    rest = [k for k in todo if k not in bases]
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(fix, rest))
    if todo:
        subprocess.run([PY, "-E", os.path.join(HERE, "gen_portraits.py")], capture_output=True, cwd=ROOT)
        log("portraits regenerated")


def main():
    a = sys.argv[1:]
    if "--log" in a:
        i = a.index("--log")
        sys.stdout = sys.stderr = open(a[i + 1], "a", encoding="utf-8", buffering=1)
        a = a[:i] + a[i + 2:]
    workers = int(a[a.index("--workers") + 1]) if "--workers" in a else 6
    loop = int(a[a.index("--loop") + 1]) if "--loop" in a else 0
    while True:
        one_pass(workers, "--dry" in a)
        if not loop:
            break
        time.sleep(loop * 60)


if __name__ == "__main__":
    main()
