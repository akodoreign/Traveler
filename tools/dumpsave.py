"""Print a save slot's state (map, position, party, flags) from the engine: python -E tools/dumpsave.py [slot]
Starts its own engine with -rtdumpsave and stops only that process (the user's game is left alone)."""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "_tools", "rpgcobo-tool")


def main():
    shot = "--shot" in sys.argv
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    slot = pos[0] if pos else "0"
    log = os.path.join(TOOL, "tmp", "savedump_%s.txt" % slot)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-map", "M101", "[60,3,20,0]", "-rtfast",
            "-rtdumpsave", slot] + (["-rtloadsave", slot] if shot else [])
    with open(log, "w") as lf:
        proc = subprocess.Popen(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    t0 = time.time()
    end = "LOADSHOT done" if shot else "SAVEDUMP END"
    while time.time() - t0 < 150:
        time.sleep(1.0)
        if end in open(log, errors="replace").read():
            break
    if shot:
        sys.path.insert(0, HERE)
        import playbot
        out = os.path.join(HERE, "..", "_art", "preview", "bot", "usersave")
        os.makedirs(out, exist_ok=True)
        playbot.convert_shots("usersave_%s" % slot, out)
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    for ln in open(log, errors="replace").read().splitlines():
        if "SAVEDUMP" in ln or "compile" in ln.lower() or "error" in ln.lower():
            print(ln[ln.find("[RT]"):] if "[RT]" in ln else ln)


if __name__ == "__main__":
    main()
