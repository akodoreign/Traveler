"""Run one M001 battle group on auto, unattended, and summarise it (rounds, outcome, key plugin log lines).
python -E tools/testbattle.py GID [--map M102] [--lv 34] [--rt "party P120,P123;equip P100+0+W128"] [--vars G281] [--grep a|b]
A -battle test exits when the fight ends; the log is _art/preview/battle_<gid>.log."""
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_lock  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))
PARTY_NAMES = ("Hiruma", "Hida", "Isawa", "Squeak", "Gonta", "Kakita", "Matsu", "Kitsuki", "Akodo", "Lion", "Shiba",
               "Doji", "Togashi", "Shosuro", "Yoritomo", "Seppun", "Tamori", "Ide", "Shinjo", "Sayo")


def party_hp(txt):
    """From a -battle log: {member: (hp, max)} at the end, from the [RT] stat and [RT] dmg lines."""
    hp = {}
    for name, val in re.findall(r"\[RT\] stat (.+?) LV\d+ HP(\d+) ", txt):
        if name.startswith(PARTY_NAMES):
            hp.setdefault(name, (int(val), int(val)))
    for line in txt.splitlines():                  # "(HP a/b)" is the HP before this hit (or heal): apply it
        m = re.search(r"\[RT\] dmg .* (-?\d+)( MISS)? \(HP (\d+)/(\d+)\)\s*$", line)
        if m:
            dmg, top = (0 if m.group(2) else int(m.group(1))), int(m.group(4))
            for n in hp:
                if ("-> %s " % n) in line:
                    hp[n] = (max(0, min(top, int(m.group(3)) - dmg)), top)
    return hp


def main():
    a = sys.argv[1:]
    opts = {"--lv": "30", "--rt": "", "--vars": "", "--grep": "", "--wait": "420", "--map": "M001"}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1]
            a = a[:i] + a[i + 2:]
    gid = a[0]
    engine_lock.wait_free()                                              # (single-instance engine: never kill one this script did not start)
    log = os.path.join(HERE, "..", "_art", "preview", "battle_%s.log" % gid)
    args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-battle", opts["--map"], gid, "-debuglv", opts["--lv"],
            "-rtauto", "-rtfast"]
    if opts["--vars"]:
        args += ["-rtvar", opts["--vars"]]
    if opts["--rt"]:
        args += ["-rt", opts["--rt"]]
    with open(log, "w") as lf:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    t0 = time.time()
    while proc.poll() is None and time.time() - t0 < float(opts["--wait"]):
        time.sleep(2)
    if proc.poll() is None:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    txt = open(log, errors="replace").read()
    rounds = txt.count("[RT] order now")
    lost = "DEFEATED" in txt
    hp = party_hp(txt)
    print("gid %s: %d rounds, %s%s  %s" % (gid, rounds, "LOST" if lost else "won/ended",
                                          "" if proc.returncode is not None else " (timed out)",
                                          ", ".join("%s %d/%d" % (n, a, b) for n, (a, b) in hp.items())))
    pat = re.compile(opts["--grep"] or r"raises|alone|WARD|ward|Blood Ward|Shield the Master|War Chant|Grave Feast|"
                                       r"Rally|courtiers|bounce|volley|xception")
    for ln in txt.splitlines():
        if "[RT]" in ln and pat.search(ln) or "xception" in ln and "serializable" not in ln:
            print("  ", ln[ln.find("["):][:150])


if __name__ == "__main__":
    main()
