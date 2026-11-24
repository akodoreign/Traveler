"""The squirrels, for ever (user 2026-11-24: "i need them to just keep going and recycling fixing till they all reach the
end of all quests, main one first. help the llm out").

Each of the two windows works on its own, one road at a time, until every traveler's road and side quests are done:
  - window 1 takes the unfinished stories first (main road first); window 2 takes side quests, or a story when no
    road is on its side quests yet. A road is never in both windows at once.
  - story phase: a run from the road's latest save state (markerchase --resume); a road whose game says it is
    walked (RokuganChase "WALKED <pid> yes") moves on to its side quests;
  - side phase: markerchase sidequests from the end of that road; done when every quest on the list was either
    finished (QUESTDONE) or reported broken (QUESTBROKEN);
  - a road that ends three runs running at the same goal is parked ("needs Claude") so it stops eating window time;
    its save states and logs are kept. STATUS.md says where everyone is after each run.
(user 2026-11-24: "squirrels must be hybernating") no window waits for the other, and no squirrel waits on Claude
(markerchase files the question in ASK/ and the squirrel goes on). The local model drives both windows when stuck.
Read only, like the squirrels: it never changes the game.

    python -E tools/squirrel_loop.py [--minutes 60]
"""
import json
import os
import re
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "_art", "preview", "chase")
RUNS = os.path.join(OUT, "player-runs")
STATE = os.path.join(OUT, "loop_state.json")
STATUS = os.path.join(OUT, "STATUS.md")
PY = sys.executable
sys.path.insert(0, HERE)
import markerchase as mc                                                          # noqa: E402 (PATHS, path_quests)

LOCK = threading.Lock()


def log_of(job):
    p = os.path.join(RUNS, job, "log.txt")
    return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""


def run(mode, i, engine, minutes, tag):
    args = [PY, "-E", "-u", os.path.join(HERE, "markerchase.py"), mode, "--only", str(i),
            "--minutes", str(minutes), "--windows", "1", "--engine", engine, "--resume"]
    with open(os.path.join(OUT, "orchestrator_%s.txt" % tag), "a", encoding="utf-8") as out:
        out.write("\n=== %s %s road %d (%s)\n" % (time.strftime("%H:%M"), mode, i, mc.PATHS[i]))
        out.flush()
        return subprocess.call(args, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)


def write_state(st):
    json.dump(st, open(STATE, "w"), indent=1)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("# Squirrels (%s)\n\n| road | phase | runs | last goal | same goal | broken quests | now |\n"
                "|---|---|---|---|---|---|---|\n" % time.strftime("%Y-%m-%d %H:%M"))
        for i, s in sorted(st.items(), key=lambda kv: int(kv[0])):
            f.write("| %s | %s | %d | %s | %d | %s | %s |\n" % (s["name"], s["phase"], s["cycles"], s["last_goal"],
                                                              s["same"], ", ".join(s["broken"]) or "-",
                                                              s.get("busy") or "-"))


def judge(i, s):
    """After a run of road I: move it on (story -> side -> done), or park it after three runs at the same goal."""
    s["cycles"] += 1
    if s["phase"] == "story":
        text = log_of("story_%d_%s" % (i, s["name"]))
        walked = re.findall(r"\[RT\] CHASE WALKED \S+ (yes|no)", text)
        if walked and walked[-1] == "yes":
            s["phase"], s["same"] = "side", 0
            return
    else:
        text = log_of("side_%d_%s" % (i, s["name"]))
        total = len(mc.path_quests("P1%02d" % i))
        seen = set(re.findall(r"\[RT\] CHASE QUEST(?:DONE|BROKEN) (\d+)", text))
        s["broken"] = sorted(set(re.findall(r"\[RT\] CHASE QUESTBROKEN (\d+)", text)))
        if len(seen) >= total:
            s["phase"] = "done"
            return
    goals = re.findall(r"\[RT\] CHASE GOAL (.+)", text)
    g = goals[-1] if goals else ""
    s["same"] = s["same"] + 1 if g and g == s["last_goal"] else 0
    s["last_goal"] = g
    if s["same"] >= 3:
        s["phase"] = "parked (%s): needs Claude" % s["phase"]


def pick(st, window):
    """The next road for this window (the fewest runs first), or None."""
    free = [(s["cycles"], int(i)) for i, s in st.items() if not s.get("busy")]
    story = sorted(c for c in free if st[str(c[1])]["phase"] == "story")
    side = sorted(c for c in free if st[str(c[1])]["phase"] == "side")
    order = [("story", story), ("sidequests", side)] if window == "w1" else [("sidequests", side), ("story", story)]
    for mode, lst in order:
        if lst:
            return mode, lst[0][1]
    return None


def worker(st, window, engine, minutes):
    while True:
        with LOCK:
            if not [s for s in st.values() if s["phase"] in ("story", "side")]:
                return
            job = pick(st, window)
            if job:
                st[str(job[1])]["busy"] = window
                write_state(st)
        if not job:
            time.sleep(60)                                # (everything left is in the other window)
            continue
        mode, i = job
        run(mode, i, engine, minutes * 2 if mode == "sidequests" else minutes, window)
        with LOCK:
            s = st[str(i)]
            s["busy"] = ""
            judge(i, s)
            write_state(st)


def main():
    a = sys.argv[1:]
    minutes = int(a[a.index("--minutes") + 1]) if "--minutes" in a else 60
    names = [p.lower() for p in mc.PATHS]
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    for i, n in enumerate(names):
        st.setdefault(str(i), {"name": n, "phase": "story", "cycles": 0, "last_goal": "", "same": 0, "broken": []})
    for s in st.values():
        s["busy"] = ""
    write_state(st)
    ws = [threading.Thread(target=worker, args=(st, "w1", "main", minutes)),
          threading.Thread(target=worker, args=(st, "w2", "-w2", minutes))]
    ws[0].start()
    time.sleep(15)                                        # (the two engines don't start in the same second)
    ws[1].start()
    for w in ws:
        w.join()
    print("squirrel loop: every road done")


if __name__ == "__main__":
    main()
