"""The marker chasers (user 2026-11-23: "squirl scripts whos job is just to chase the objective marker to each goal for
each story/quest/sidequest. let them take notes, you can use local llm ... a small model ... the intel npu. you can have
2 game windows open. have it check every quest and game (let it self learn, do not let it change any code its job is
read only)"; "let the local llm be able to launch and close its instance incase it gets stuck"; "if it gets stuck let
it let you know so you can fix the stuck"; "have it do all the triggers and conversations as well. all the notes").

READ ONLY: this script and the in-game chaser (plugin RokuganChase.sk, -rtchase) change no code and no game data. They
play test launches (never a save slot: the bot skips save menus) and write only under _art/preview/chase/ and the
engine's tmp/chase/. They never close a game they didn't start.

    python -E tools/markerchase.py [story|quests|games|all] [--only 0,3 | --only 100,101] [--minutes 60]
                                   [--windows 2] [--no-llm]

Jobs:  story  - each of the eight roads from New Game (the prologue's choice), following the marker to the end.
       quests - each Journal quest (RokuganJournalData.sk) and side story: started at the giver with the quest's
                opening flags set, the quest tracked (G1244), followed until the marker says it's done.
       games  - every mini-game, through the existing self-play tests (minitest, dance, kabuki, Game of Masks, the
                castles' clan games and go).
Each run: the chaser follows the marker, sweeps every map (talks to everyone, examines everything, walk-on triggers
that stay on the map), and logs it all. Notes: _art/preview/chase/<job>/notes.md (goals + timings, every event used,
the whole conversation per map, menus, battles, errors, the model's findings). A stuck run (no progress, a STUCK /
NOPROMPT / NOPOINT line) writes _art/preview/chase/STUCK/<job>.md and prints "STUCK <job>: ..." - the line Claude's
watcher waits for. The local model (tools/chase_llm.py, NPU) decides on a stuck window: continue, restart or close.
Learning: _art/preview/chase/knowledge.json - for each job, the menus answered before a stall; the next run of that
job gets a different answer for them (the in-game policy file tmp/chase/policy_<job>.json)."""
import json
import os
import re
import subprocess
import sys
import glob
import shutil
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot as pb  # noqa: E402
import gen_maps as gm  # noqa: E402

TOOL = gm.TOOL
TOOL2 = TOOL + "-w2"                   # window 2: a copy of the exe with project/ etc. linked (one per folder)


def wtool():
    """This window's engine folder."""
    return getattr(SLOT, "tool", TOOL)
OUT = os.path.join(HERE, "..", "_art", "preview", "chase")
STUCKDIR = os.path.join(OUT, "STUCK")
RESUME = False                                          # --resume (see chase())
ASKDIR = os.path.join(OUT, "ASK")                       # a chaser's question (five tries at one goal): Claude answers
ANSDIR = os.path.join(OUT, "ANSWERS")                   #  in ANSWERS/<job>.txt: retry | goto X Z | use NAME |
                                                        #  broken [why] | close
KNOW = os.path.join(OUT, "knowledge.json")
NPU_PY = r"D:\RokuganTraveler\.venv-npu\Scripts\python.exe"
PLUG = os.path.join(gm.PROJ, "plugin", "rokugan")
PATHS = ["Crab", "Crane", "Lion", "Phoenix", "Dragon", "Scorpion", "Unicorn", "Ronin"]
LOCK = threading.Lock()
SLOT = threading.local()                                                 # each window's reserved save slot (90, 91...)
PRINT = threading.Lock()


def say(s):
    with PRINT:
        print(s, flush=True)


# ------------------------------------------------------------------ the local model (one process, shared)
class Model:
    def __init__(self, use):
        self.p, self.ok, self.lock = None, False, threading.Lock()
        if not use or not os.path.exists(NPU_PY):
            say("model: off")
            return
        self.p = subprocess.Popen([NPU_PY, os.path.join(HERE, "chase_llm.py")], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
        hello = json.loads(self.p.stdout.readline() or "{}")
        self.ok = bool(hello.get("ready"))
        say("model: %s" % (("ready on " + str(hello.get("device"))) if self.ok else "failed to load (rules only)"))

    def ask(self, req):
        if not self.ok:
            return {}
        with self.lock:
            try:
                self.p.stdin.write(json.dumps(req) + "\n")
                self.p.stdin.flush()
                return json.loads(self.p.stdout.readline() or "{}")
            except (OSError, ValueError):
                self.ok = False
                return {}

    def close(self):
        if self.p:
            try:
                self.p.stdin.close()
                self.p.wait(10)
            except (OSError, subprocess.TimeoutExpired):
                self.p.kill()


# ------------------------------------------------------------------ learning
def know_load():
    try:
        return json.load(open(KNOW, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def know_save(k):
    with LOCK:
        os.makedirs(OUT, exist_ok=True)
        json.dump(k, open(KNOW, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def policy_for(job, know):
    """The answers to try this time: a menu answered just before a stall gets the next option it hasn't tried."""
    pol = {}
    for key, rec in know.get(job, {}).get("menus", {}).items():
        tried, n = rec.get("tried", []), rec.get("n", 1)
        if rec.get("stalled"):
            left = [i for i in range(n + 1) if i not in tried]
            pol[key] = left[0] if left else 0
        elif "good" in rec:
            pol[key] = rec["good"]
    path = os.path.join(wtool(), "tmp", "chase", "policy_%s.json" % job)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(pol, open(path, "w", encoding="utf-8"))
    return "tmp/chase/policy_%s.json" % job, len(pol)


# ------------------------------------------------------------------ jobs
def story_jobs(only):
    jobs = []
    for i, name in enumerate(PATHS):
        if only and str(i) not in only:
            continue
        bx, bz = pb.block("M099", 12, 6)
        jobs.append({"job": "story_%d_%s" % (i, name.lower()), "map": "M099", "pos": pb.start_pos("M099", bx, bz),
                     "vars": "G000", "extra": ["choice %d" % i], "lead": None})
    return jobs


def quest_jobs(only):
    jd = open(os.path.join(PLUG, "RokuganJournalData.sk"), encoding="utf-8").read()
    md = open(os.path.join(PLUG, "RokuganMarkerData.sk"), encoding="utf-8").read()
    js = open(os.path.join(PLUG, "RokuganJournal.sk"), encoding="utf-8").read()
    spots = {int(a): (b, float(c), float(d)) for a, b, c, d in
             re.findall(r'\[(\d+)\] = \["(M\d+)", ([\d.]+), ([\d.]+),', md)}
    jobs = []
    for txt in (jd, js):
        for m in re.finditer(r'\{ id = (\d+), who = (null|"P\d+"), title = ("(?:[^"\\]|\\.)*")[^}]*?open = \[([^\]]*)\]',
                             txt):
            qid, who, title, opens = int(m.group(1)), m.group(2), json.loads(m.group(3)), m.group(4)
            if only and str(qid) not in only:
                continue
            if qid not in spots:
                continue
            mp, x, z = spots[qid]
            flags = re.findall(r'"(G\d+)"', opens)
            lead = who.strip('"') if who != "null" else "P100"
            try:
                pos = pb.start_pos(mp, x * 2.0, z * 2.0 + 3.0)
            except Exception:                                          # noqa: BLE001 (a map not buildable here)
                continue
            jobs.append({"job": "quest_%d" % qid, "title": title, "map": mp, "pos": pos,
                         "vars": ",".join(["G000"] + flags), "extra": ["chasequest %d" % qid], "lead": lead})
    return jobs


GAME_TESTS = [("games_winter_court", ["minitest.py", "both", "--plan", "lose,win"]),
              ("games_memory", ["minitest.py", "memory", "--plan", "lose,win"]),
              ("games_clan", ["test_clan_games.py", "all"]),
              ("games_masks", ["test_sadane.py", "stranger", "1"]),
              ("games_dance", ["test_dance.py"]),
              ("games_kabuki", ["test_kabuki.py", "win"])]


# ------------------------------------------------------------------ one chase run
PROGRESS = re.compile(r"\[RT\] CHASE (GOAL|REACHED|MAP|TALK|SWEPT|OBJECTIVE|BATTLE_END|PROMPT)")
TROUBLE = re.compile(r"\[RT\] CHASE (STUCK|NOPROMPT|NOREACT|NOPOINT|NOEVENT|ERROR)|xception in|compile error")


def chase(job, minutes, model, know):
    name = job["job"]
    out = os.path.join(OUT, name)
    os.makedirs(out, exist_ok=True)
    log = os.path.join(out, "log.txt")
    pol, npol = policy_for(name, know)
    snapdir = os.path.join(wtool(), "tmp", "chase", name)
    shutil.rmtree(snapdir, ignore_errors=True)
    os.makedirs(snapdir, exist_ok=True)
    pack = ["bot wait,36000000", "fast", "auto", "lv 40", "mini win", "chase %d" % minutes, "chasepolicy %s" % pol,
            "chasejob %s" % name]
    pack += job["extra"]
    if job.get("lead"):
        pack.append("lead %s" % job["lead"])
    # (user 2026-11-23: "you can use savestates when you get stuck so you can keep going without completely starting
    # from scratch") --resume: start from the job's latest save state (the one it took when it got bored or asked)
    resumed = None
    if RESUME:
        old = sorted(glob.glob(os.path.join(out, "snapshots", "snap_*.bin")), key=os.path.getmtime)
        if old:
            slot = getattr(SLOT, "n", 90)
            save = os.path.join(wtool(), "savedata", "save%03d.bin" % slot)
            os.makedirs(os.path.dirname(save), exist_ok=True)
            shutil.copy(old[-1], save)
            shutil.copy(old[-1], os.path.join(out, "resumed_from.bin"))
            pack.append("loadsave %d" % slot)
            resumed = os.path.basename(old[-1])
    args = [os.path.join(wtool(), "rpgcobo.exe"), "-testplay", "-map", job["map"], job["pos"], "-rtvar", job["vars"],
            "-rtfast", "-rtauto", "-debuglv", "40", "-rt", ";".join(pack)]
    restarts, t_start = 0, time.time()
    say("RUN %s (%s, %d learned answers)%s" % (name, job.get("title", "from New Game"), npol,
                                               " - resumed from its save state " + resumed if resumed else ""))
    while True:
        lf = open(log, "a" if restarts or resumed else "w")            # (a resumed run keeps the earlier log)
        proc = subprocess.Popen(args, cwd=wtool(), stdout=lf, stderr=subprocess.STDOUT)
        t7 = time.time()
        while time.time() - t7 < 4 and proc.poll() is None:
            time.sleep(0.2)
        if proc.poll() == 7:                                           # this folder's engine is busy
            lf.close()
            say("WAIT %s: the engine in %s is busy (code 7), trying again" % (name, os.path.basename(wtool())))
            time.sleep(15)
            continue
        t0, last_prog, flagged = time.time(), time.time(), set()
        seen = len(open(log, encoding="utf-8", errors="replace").read().splitlines()) if restarts or resumed else 0
        verdict, waiting = "done", False
        while True:
            time.sleep(4)
            text = open(log, encoding="utf-8", errors="replace").read()
            lines = text.splitlines()
            new = lines[seen:]
            seen = len(lines)
            if any(PROGRESS.search(ln) for ln in new):
                last_prog = time.time()
            for ln in new:
                if TROUBLE.search(ln) and ln not in flagged:
                    flagged.add(ln)
                    report_stuck(name, ln, lines, loud=False)
                if "[RT] CHASE ASK " in ln:
                    waiting = True
                    ask(name, ln, lines, model, snapdir)
                if "[RT] CHASE ANSWER " in ln:
                    waiting = False
                    last_prog = time.time()
                if "[RT] CHASE BROKEN " in ln:
                    say("BROKEN %s: %s" % (name, ln.split("BROKEN ", 1)[1][:200]))
            ans = os.path.join(ANSDIR, name + ".txt")
            if os.path.exists(ans):                                      # Claude's answer -> the game
                a = open(ans, encoding="utf-8").read().strip()
                os.remove(ans)
                with open(os.path.join(snapdir, "answer.txt"), "w", encoding="utf-8") as f:
                    f.write(a + "\n")
                say("ANSWERED %s: %s" % (name, a))
                if a.strip() == "restart":                               # Claude fixed the cause: go on from
                    verdict = "restart"                                  #  the latest save state with the new code
                    break
            if waiting:
                last_prog = time.time()
                if time.time() - t0 > minutes * 60 + 3000:                # (45 min for an answer, then it closes itself)
                    verdict = "no answer"
                    break
                continue
            if any("[RT] CHASE DONE" in ln for ln in new):                # (this run's own lines: a resumed log
                verdict = "done"                                         #  holds the last run's DONE)
                break
            if proc.poll() is not None:
                verdict = "the game exited (code %s)" % proc.returncode
                # (user 2026-11-23: code 0 here = the user closed a window that kept looping; the chaser now times
                # out on its own - RokuganChase.sk, five minutes on one screen)
                break
            idle = time.time() - last_prog
            if idle > 180:                                               # three minutes without progress: ask
                tail = "\n".join(ln for ln in lines[-60:] if "[RT]" in ln)[-3500:]
                ans = model.ask({"task": "supervise", "job": name, "tail": tail, "idle_s": idle}) or {}
                act = ans.get("action") or ("restart" if idle > 420 else "continue")
                say("SUPERVISOR %s: %s after %.0f s idle (%s)" % (name, act, idle, ans.get("why", "rules")))
                if act == "continue" and idle < 600:
                    last_prog = time.time() - 120                       # look again in a minute
                    continue
                report_stuck(name, "no progress for %.0f s - the supervisor chose %s" % (idle, act), lines)
                verdict = act
                break
            if time.time() - t0 > minutes * 60 + 120:
                verdict = "time limit"
                break
        if proc.poll() is None:                                          # only ever our own process
            proc.kill()
        lf.close()
        learn(name, open(log, encoding="utf-8", errors="replace").read(), verdict, know)
        keep_snaps(name, out)
        if verdict == "restart" and restarts < 3:
            restarts += 1
            pol, npol = policy_for(name, know)
            snaps = sorted(glob.glob(os.path.join(snapdir, "snap_*.bin")))
            if snaps:                                                    # resume where it last stood well
                slot = getattr(SLOT, "n", 90)
                save = os.path.join(wtool(), "savedata", "save%03d.bin" % slot)
                os.makedirs(os.path.dirname(save), exist_ok=True)
                shutil.copy(snaps[-1], save)
                rt = ";".join([x for x in args[args.index("-rt") + 1].split(";") if not x.startswith("loadsave")] +
                              ["loadsave %d" % slot])
                args[args.index("-rt") + 1] = rt
                say("RESTART %s (%d) from %s via slot %d, %d learned answers" % (name, restarts,
                                                                              os.path.basename(snaps[-1]), slot, npol))
            else:
                say("RESTART %s (%d, from the start, %d learned answers)" % (name, restarts, npol))
            continue
        break
    notes(job, out, model, verdict, time.time() - t_start)


def keep_snaps(name, out):
    """The run's save states, screenshots and their one-line summaries -> <out>/snapshots/ + snapshots.md."""
    sd = os.path.join(out, "snapshots")
    os.makedirs(sd, exist_ok=True)
    for f in glob.glob(os.path.join(wtool(), "tmp", "chase", name, "snap_*.bin")):
        shutil.copy2(f, sd)                                       # (keeps the time: --resume takes the newest)
    try:
        pb.convert_shots("chase_" + name, sd)
    except Exception:                                                    # noqa: BLE001 (no shots is fine)
        pass
    text = open(os.path.join(out, "log.txt"), encoding="utf-8", errors="replace").read()
    rows = re.findall(r"\[RT\] CHASE SNAP (\d+) (.+)", text)
    L = ["# %s - save states" % name, "",
         "Each snap_NN.bin is a full save (what the game's own Save writes). To look at one in the game: copy it to",
         "_tools/rpgcobo-tool/savedata/save090.bin and launch with -rtloadsave 90 (or load slot 90). The screenshot",
         "chase_%s_NN.png was taken at the same moment." % name, ""]
    L += ["- **%s** %s" % (n, rest) for n, rest in rows]
    with open(os.path.join(out, "snapshots.md"), "a" if os.path.exists(os.path.join(out, "snapshots.md")) else "w",
              encoding="utf-8") as f:
        f.write("\n".join(L) + "\n\n")


def shots_now(name, dest):
    """This window's raw screenshots for the job -> PNGs in dest (playbot.convert_shots, but from either window)."""
    import numpy as np
    from PIL import Image
    shots = os.path.join(wtool(), "tmp", "rt_shot")
    os.makedirs(dest, exist_ok=True)
    out = []
    for f in sorted(glob.glob(os.path.join(shots, "bot_chase_%s_*.raw" % name))):
        b = open(f, "rb").read()
        w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
        arr = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
        png = os.path.join(dest, os.path.basename(f)[4:-4] + ".png")
        Image.fromarray(arr[..., :3].copy(), "RGB").save(png)
        out.append(png)
    return out


MAPDATA = {}
LOCAL_TRIES = {}                                         # (job, goal) -> answers the local model already gave


def map_events(mid):
    """What the model is shown about the chaser's map: each usable event's name, place, trigger and first words."""
    if not MAPDATA:
        MAPDATA.update(json.load(open(os.path.join(gm.PROJ, "data", "map.json"), encoding="utf-8")))
    out = []
    for e in (MAPDATA.get(mid) or {}).get("event", {}).values():
        if e.get("role") in ("portal", "light") or "pos" not in e:
            continue
        pages = e.get("page") or []
        trig = max([p.get("trigger") or 0 for p in pages] or [2 if e.get("role") in ("villager", "clerk", "hotel")
                                                                else 0])
        if trig not in (1, 2, 5) and e.get("role") not in ("villager", "clerk", "hotel"):
            continue
        said = e.get("msg") or next(iter(re.findall(r'"text": "([^"]{4,60})', json.dumps(e))), "")
        out.append("%s, %.1f, %.1f, %s, %s" % (e.get("name"), e["pos"][0] / 2.0, e["pos"][2] / 2.0, trig, said[:60]))
    return "\n".join(out[:40])


def ask(name, line, lines, model=None, snapdir=None):
    """A chaser asks (five tries at one goal). (user: "it should be doing this on local and just reporting back to
    you occasionally") The local model answers first - up to two answers per goal; only when those don't help does
    the question go to Claude: the save state, its screenshot, what it tried."""
    q = line.split("CHASE ASK ", 1)[1]
    goal = q.split(" | ")[0]
    mid = (re.search(r"on (M\d+) at", q) or [None, ""])[1]
    tried = LOCAL_TRIES.setdefault((name, goal), [])
    if model is not None and model.ok and len(tried) < 2 and snapdir:
        tail = "\n".join(ln.split("CHASE ", 1)[1] for ln in lines[-120:] if "[RT] CHASE " in ln)[-2500:]
        a = (model.ask({"task": "answer", "question": q, "tail": tail, "events": map_events(mid),
                        "tried": tried}) or {}).get("answer", "retry")
        a = a.strip().strip("`").strip()
        if not re.match(r"^(retry|close|broken\b.*|goto -?[\d.]+ -?[\d.]+|use \S+)$", a):
            a = "retry"
        tried.append(a)
        with open(os.path.join(snapdir, "answer.txt"), "w", encoding="utf-8") as f:
            f.write(a + "\n")
        with LOCK:
            os.makedirs(OUT, exist_ok=True)
            with open(os.path.join(OUT, "local_answers.md"), "a", encoding="utf-8") as f:
                f.write("- %s %s | %s -> **%s**\n" % (time.strftime("%H:%M"), name, q[:160], a))
        if a.startswith("broken"):
            say("BROKEN %s (the local model): %s | %s" % (name, q[:160], a))
        return
    # the local model's answers didn't help: Claude
    os.makedirs(ASKDIR, exist_ok=True)
    os.makedirs(ANSDIR, exist_ok=True)
    out = os.path.join(OUT, name, "snapshots")
    pngs = shots_now(name, out)
    for f in glob.glob(os.path.join(wtool(), "tmp", "chase", name, "snap_*.bin")):
        shutil.copy(f, out)
    q = line.split("CHASE ASK ", 1)[1]
    tried = [ln.split("CHASE ", 1)[1] for ln in lines[-200:] if "[RT] CHASE " in ln][-40:]
    with LOCK:
        with open(os.path.join(ASKDIR, name + ".md"), "w", encoding="utf-8") as f:
            f.write("# %s asks\n\n**%s**\n\nScreenshot: %s\nSave state: %s (window folder %s)\n\n"
                    "Answer in _art/preview/chase/ANSWERS/%s.txt, one line: retry | goto X Z | use NAME | "
                    "broken [why] | close\n\n## The last things it did\n\n```\n%s\n```\n"
                    % (name, q, pngs[-1] if pngs else "-", os.path.join(out, "snap_*.bin"), wtool(), name,
                       "\n".join(tried)))
    say("ASK %s: %s" % (name, q[:220]))


def report_stuck(name, why, lines, loud=True):
    os.makedirs(STUCKDIR, exist_ok=True)
    tail = "\n".join(ln for ln in lines[-80:] if "[RT]" in ln)
    with LOCK:
        with open(os.path.join(STUCKDIR, name + ".md"), "a", encoding="utf-8") as f:
            f.write("## %s - %s\n\n```\n%s\n```\n\n" % (time.strftime("%H:%M:%S"), why.strip(), tail[-4000:]))
    if loud:
        say("STUCK %s: %s" % (name, why.strip()[:200]))


def learn(name, text, verdict, know):
    rec = know.setdefault(name, {"runs": 0, "menus": {}, "stalls": []})
    rec["runs"] += 1
    menus = re.findall(r"\[RT\] CHASE CHOICE (.+?) => (\d+) \((.*)\)", text)
    # (2026-11-23) a window closed from outside (code 0: the user closing a looping run) or a restart is no evidence
    # against the menus answered before it
    if verdict.startswith("the game exited") or verdict == "restart":
        know_save(know)
        return
    stalled = verdict not in ("done",) or "CHASE STUCK" in text or "gave up" in text
    for key, v, opts in menus:
        m = rec["menus"].setdefault(key, {"tried": [], "n": opts.count(" / ")})
        if int(v) not in m["tried"]:
            m["tried"].append(int(v))
    if stalled and menus:                                                # the last menus before the stall are suspects
        for key, v, opts in menus[-3:]:
            rec["menus"][key]["stalled"] = True
        rec["stalls"].append({"verdict": verdict, "last": re.findall(r"\[RT\] CHASE GOAL (.+)", text)[-1:]})
    elif not stalled:
        for key, v, opts in menus:
            rec["menus"][key]["good"] = int(v)
            rec["menus"][key].pop("stalled", None)
    know_save(know)


# ------------------------------------------------------------------ notes
def notes(job, out, model, verdict, secs):
    text = open(os.path.join(out, "log.txt"), encoding="utf-8", errors="replace").read()
    L = ["# %s" % job["job"], "", "%s. Ended: %s after %.0f min." % (job.get("title", "From New Game"), verdict, secs / 60),
         ""]
    goals = re.findall(r"\[RT\] CHASE (GOAL|REACHED|OBJECTIVE) (.+)", text)
    L += ["## Goals and objectives", ""] + ["- **%s** %s" % (k.lower(), v) for k, v in goals] + [""]
    trouble = [ln.split("CHASE ", 1)[1] for ln in text.splitlines() if TROUBLE.search(ln) and "CHASE " in ln]
    errs = [ln for ln in text.splitlines() if "xception in" in ln or "compile error" in ln]
    L += ["## Trouble", ""] + ["- %s" % t for t in trouble + errs] + (["- none"] if not trouble and not errs else []) + [""]
    L += ["## Events used, and what was said", ""]
    cur = None
    for ln in text.splitlines():
        m = re.search(r"\[RT\] CHASE (MAP|EVENT|SWEPT|PROMPT|TALK|BATTLE|BATTLE_END) (.+)", ln)
        if m:
            k, v = m.groups()
            if k == "MAP":
                cur = v.split()[0]
                L += ["", "### %s" % v.replace(" undefined", ""), ""]
            elif k == "EVENT":
                L.append("- event: %s" % v)
            elif k in ("BATTLE", "BATTLE_END"):
                L.append("- (%s)" % k.lower().replace("_", " "))
            continue
        m = re.search(r"\[RT\] MSG (.*?): (.*)", ln)
        if m:
            L.append("    - %s%s" % (m.group(1) + ": " if m.group(1) else "", m.group(2)))
            continue
        m = re.search(r"\[RT\] CHASE CHOICE (.+?) => (\d+) \((.*)\)", ln)
        if m:
            L.append("    - menu: %s -> took %s" % (m.group(3), m.group(2)))
    body = "\n".join(L)
    played = bool(re.search(r"\[RT\] CHASE (GOAL|EVENT|MAP)", text))
    if not played:
        body = body.replace("## Goals and objectives", "## Findings\n\n- The run never got going (%s): nothing to report.\n\n## Goals and objectives" % verdict, 1)
    if model.ok and played:
        ans = model.ask({"task": "summarise", "job": job["job"], "notes": body}) or {}
        if ans.get("text"):
            body = body.replace("## Goals and objectives", "## Findings (local model)\n\n%s\n\n## Goals and objectives"
                                % ans["text"], 1)
    open(os.path.join(out, "notes.md"), "w", encoding="utf-8").write(body + "\n")
    say("NOTES %s -> %s" % (job["job"], os.path.normpath(os.path.join(out, "notes.md"))))


def game_run(name, cmd):
    out = os.path.join(OUT, name)
    os.makedirs(out, exist_ok=True)
    say("RUN %s" % name)
    r = subprocess.run([sys.executable, "-E", os.path.join(HERE, cmd[0])] + cmd[1:], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=3600)
    text = r.stdout + r.stderr
    open(os.path.join(out, "log.txt"), "w", encoding="utf-8").write(text)
    lines = [ln for ln in text.splitlines() if re.search(r"round \d+ over|result \d|-> \d|BOT var|TIMED OUT|rror", ln)]
    bad = [ln for ln in lines if "TIMED OUT" in ln or "rror" in ln]
    open(os.path.join(out, "notes.md"), "w", encoding="utf-8").write(
        "# %s\n\n`%s`\n\n" % (name, " ".join(cmd)) + "\n".join("- " + ln.strip() for ln in lines) + "\n")
    if bad:
        report_stuck(name, bad[0], text.splitlines())
    say("NOTES %s (%d result lines%s)" % (name, len(lines), ", trouble" if bad else ""))


# ------------------------------------------------------------------ main
def main():
    a = sys.argv[1:]
    what = a[0] if a and not a[0].startswith("--") else "all"

    def opt(k, d):
        return a[a.index(k) + 1] if k in a else d
    only = set(opt("--only", "").split(",")) - {""}
    global RESUME
    RESUME = "--resume" in a
    minutes, windows = int(opt("--minutes", "60")), int(opt("--windows", "2"))
    model = Model("--no-llm" not in a)
    know = know_load()
    jobs = []
    if what in ("story", "all"):
        jobs += [("chase", j) for j in story_jobs(only)]
    if what in ("quests", "all"):
        jobs += [("chase", j) for j in quest_jobs(only)]
    if what in ("games", "all"):
        jobs += [("game", g) for g in GAME_TESTS if not only or g[0] in only]
    say("JOBS %d (%d windows)" % (len(jobs), windows))
    q = list(jobs)

    slots = iter(range(90, 90 + max(1, windows)))

    tools = iter([TOOL, TOOL2] + [TOOL] * 8)

    def worker():
        SLOT.n = next(slots)
        SLOT.tool = next(tools)
        while True:
            with LOCK:
                if not q:
                    return
                kind, j = q.pop(0)
            try:
                if kind == "chase":
                    chase(j, minutes if j["job"].startswith("story") else min(minutes, 20), model, know)
                else:
                    game_run(*j)
            except Exception as e:                                       # noqa: BLE001 (keep the other window going)
                say("STUCK %s: the orchestrator failed: %s" % (j["job"] if kind == "chase" else j[0], e))
    # (the mini-game tests launch through engine_lock / playbot, one at a time on their own)
    total = len(q)

    def heartbeat():
        while any(t.is_alive() for t in ts):
            time.sleep(1800)
            with LOCK:
                left = len(q)
            asks = len(glob.glob(os.path.join(ASKDIR, "*.md")))
            local = sum(1 for _ in open(os.path.join(OUT, "local_answers.md"), encoding="utf-8")) \
                if os.path.exists(os.path.join(OUT, "local_answers.md")) else 0
            say("PROGRESS %d of %d jobs started, %d questions answered locally, %d sent to Claude" %
                (total - left, total, local, asks))
    ts = [threading.Thread(target=worker) for _ in range(max(1, windows))]
    for t in ts:
        t.start()
        time.sleep(8)                                                    # (stagger the two windows' starts)
    threading.Thread(target=heartbeat, daemon=True).start()
    for t in ts:
        t.join()
    model.close()
    say("ALL DONE")


if __name__ == "__main__":
    main()
