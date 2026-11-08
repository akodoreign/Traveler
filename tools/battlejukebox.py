"""Play a queue of example battles at normal speed (sound on, auto-battle), one per music theme, for the user to
watch and listen. Waits until no rpgcobo.exe is running (never kills the user's game). Each battle plays up to
--secs seconds (default 90; 0 = until you close it) or until it ends; closing a battle window skips to the next.
The party can't fall (-rttank: full HP before every hit), so the music keeps playing.
python -E tools/battlejukebox.py [gid ...] [--secs 90]"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))

# (gid, level, label): one per battle theme (gen_music BATTLE_MUSIC)
QUEUE = [
    (1, 20, "MU104 battle - Goblin raid"),
    (38, 40, "MU105 boss - Katsuo the White Brother"),
    (21, 40, "MU115 boss_oni - Oni no Kommei"),
    (31, 40, "MU116 duel - Kakita Yasurugi"),
    (35, 45, "MU117 intrigue - the Iron Cranes"),
    (36, 40, "MU118 miniboss - Chihaya the Quick"),
    (167, 70, "MU119 final1 - Doji Nashiko"),
    (168, 70, "MU120 final2 - Body of Damned Time"),
    (169, 70, "MU121 final3 - The Empress of Nothing"),
    (172, 80, "MU123 okura - Oni no Okura"),
    (173, 80, "MU122 orochi - The Orochi"),
]


def running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq rpgcobo.exe"], capture_output=True, text=True).stdout
    return "rpgcobo.exe" in out


def main():
    a = sys.argv[1:]
    secs = 90.0
    if "--secs" in a:
        i = a.index("--secs")
        secs = float(a[i + 1])
        a = a[:i] + a[i + 2:]
    queue = [q for q in QUEUE if not a or str(q[0]) in a] or [(int(g), 40, "group %s" % g) for g in a]
    if running():
        print("Waiting for the game to close...", flush=True)
        while running():
            time.sleep(2)
    for gid, lv, label in queue:
        print("Now playing: %s (group %d)" % (label, gid), flush=True)
        proc = subprocess.Popen([os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-battle", "M001", str(gid),
                                 "-debuglv", str(lv), "-rtauto", "-rttank"], cwd=TOOL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while proc.poll() is None and (secs <= 0 or time.time() - t0 < secs):
            time.sleep(1)
        if proc.poll() is None:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
        time.sleep(1.5)
    print("Queue done.", flush=True)


if __name__ == "__main__":
    main()
