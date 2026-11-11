"""Redraw single AI sprite sheets beside the running gen_pixeldrive runner, without stopping it (user 2026-11-11:
"yeah redraw them" - Hida Sachiko's tetsubo over her face, the noisy Moto Outrider).
python -E tools/pixelai_redo.py side_sachiko side_h_moto
Before: move the old frames out of sheets/<key>/ (to pixelai/replaced/), fix the spec / guide. The runner itself only
picks a sheet up again on its next full pass, so this draws it now (its ComfyUI jobs queue in with the runner's) and
writes the same "complete" marker + DONE.txt line, so the runner skips it afterwards."""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixeldrive as pd  # noqa: E402
sys.argv = _argv


def main():
    a = sys.argv[1:]
    if "--log" in a:                                          # detached runs have no console
        i = a.index("--log")
        sys.stdout = sys.stderr = open(a[i + 1], "a", encoding="utf-8", buffering=1)
        a = a[:i] + a[i + 2:]
    if "--after" in a:                                        # queue behind an earlier redo: wait for that pid to end
        i = a.index("--after")
        pid = int(a[i + 1])
        a = a[:i] + a[i + 2:]
        print(time.strftime("%H:%M"), "waiting for redo pid", pid, flush=True)
        while subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True,
                             text=True).stdout.count(" %d " % pid):
            time.sleep(60)
    for k in a:
        sp = json.load(open(os.path.join(pd.SPECS, "%s.json" % k)))
        am = pd.animap(sp["sheet"])
        print(time.strftime("%H:%M"), "redo", k, len(am), "animations", flush=True)
        for attempt in range(3):
            if pd.do_sheet(sp, os.path.join(pd.RES, sp["sheet"]), k, am):
                open(os.path.join(pd.SHEETS, k, "complete"), "w").write("1")
                open(os.path.join(pd.ps.PX, "DONE.txt"), "a").write("%s %s (redo)\n" % (time.strftime("%m-%d %H:%M"), k))
                print(time.strftime("%H:%M"), "sheet done", k, flush=True)
                break


if __name__ == "__main__":
    main()
