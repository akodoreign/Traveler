"""Run the Squirrels through Traveler's story using its ordinary player mechanics.

    python -E tools/markerchase.py story [--only 0,3] [--minutes 60] [--windows 2] [--profiles DIR] [--no-llm]

Start at the configured New Game entry. Player-visible menu choices and Auto Battle are allowed.
Story runs start with a level-40 party and use minigame win-mode self-play on the hardest offered difficulty.
Follow objectives without grinding. Do not seed quest state or edit game code or data. Keep story-run
logs and snapshots separate from older fixture runs. The adviser and the human handoff share the
same checked action vocabulary. Unresolved findings go to _art/preview/chase/STUCK and ASK.
"""
import json
import math
import os
import re
import subprocess
import sys
import glob
import shutil
import threading
import time

from squirrels_navigation import ASK_POSITION, observed_waypoints, walking_hint

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))
TOOL2 = TOOL + "-w2"                   # window 2: a copy of the exe with project/ etc. linked (one per folder)


def wtool():
    """This window's engine folder."""
    return getattr(SLOT, "tool", TOOL)
OUT = os.path.join(HERE, "..", "_art", "preview", "chase")
PLAYER_RUNS = os.path.join(OUT, "player-runs")
STUCKDIR = os.path.join(OUT, "STUCK")
RESUME = False                                          # --resume (see chase())
ASKDIR = os.path.join(OUT, "ASK")                       # a chaser's question (five tries at one goal): Claude answers
ANSDIR = os.path.join(OUT, "ANSWERS")                   #  in ANSWERS/<job>.txt: retry | goto X Z | use NAME |
                                                        #  broken [why] | close
KNOW = os.path.join(PLAYER_RUNS, "knowledge.json")
STORY_ASSISTS = ("Level 40", "Minigame self-play in win mode")
# The initial selections for the three in-game Easy/Hard menus. The number after | is the last option index.
HARD_MENUS = {"Dance. (Easy)|2": 1, "Perform it. (Easy)|1": 1}
MENU_LOG = re.compile(r"\[RT\] CHASE CHOICE (.+?) => (\d+) \((.*)\)")
DIFFICULTY = {"easy": 0, "normal": 1, "medium": 1, "hard": 2, "expert": 3, "master": 4}
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
        if not use:
            say("model: off")
            return
        self.p = subprocess.Popen([sys.executable, "-B", os.path.join(HERE, "chase_llm.py")], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
        hello = json.loads(self.p.stdout.readline() or "{}")
        self.ok = bool(hello.get("ready"))
        say("model: %s" % (("ready on " + str(hello.get("device"))) if self.ok else "failed to load"))

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
        os.makedirs(PLAYER_RUNS, exist_ok=True)
        json.dump(k, open(KNOW, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def hardest_option(options):
    """Return the highest difficulty index for a menu with recognized labeled difficulties."""
    labeled = {}
    for index, label in enumerate(options.split(" / ")):
        match = re.fullmatch(r"(?:.*\s\()?([a-z]+)\)?", label.strip().lower())
        if match and match[1] in DIFFICULTY:
            labeled[index] = DIFFICULTY[match[1]]
    return max(labeled, key=labeled.get) if len(set(labeled.values())) >= 2 else None


def policy_for(job, know):
    """The answers to try this time: a menu answered just before a stall gets the next option it hasn't tried."""
    pol = {}
    for key, rec in know.get(job, {}).get("menus", {}).items():
        hardest = hardest_option(rec.get("options", ""))
        if hardest is not None:
            pol[key] = hardest
            continue
        tried, n = rec.get("tried", []), rec.get("n", 1)
        if rec.get("stalled"):
            left = [i for i in range(n + 1) if i not in tried]
            pol[key] = left[0] if left else 0
        elif "good" in rec:
            pol[key] = rec["good"]
    pol.update(HARD_MENUS)
    path = os.path.join(wtool(), "tmp", "chase", "policy_%s.json" % job)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(pol, open(path, "w", encoding="utf-8"))
    return "tmp/chase/policy_%s.json" % job, len(pol)


# ------------------------------------------------------------------ jobs
def story_jobs(only):
    with open(os.path.join(TOOL, "project", "data", "setting.json"), encoding="utf-8") as source:
        start = json.load(source)["inimap"]
    jobs = []
    for i, name in enumerate(PATHS):
        if only and str(i) not in only:
            continue
        jobs.append({"job": "story_%d_%s" % (i, name.lower()), "map": start["mapid"],
                     "pos": json.dumps(start["pos"]), "choice": i})
    return jobs


def path_quests(pid):
    """(user 2026-11-23: "crane is done, crane should go through their side quests now") the quests a traveler can
    take on their road: their own (journal who), and the open odd jobs whose giver stands on their road (MK_PATH)."""
    rk = os.path.join(TOOL, "project", "plugin", "rokugan")
    s = open(os.path.join(rk, "RokuganMarkerData.sk"), encoding="utf-8").read()
    i = s.index("MK_PATH <- {")
    path = dict(re.findall(r'(M\d+) = "(P\d+)"', s[i:s.index("};", i)]))
    i = s.index("MK_QUEST <- {")
    mq = {int(a): json.loads(b) for a, b in re.findall(r"\[(\d+)\] = (\[.*?\]),?\n", s[i:s.index("};", i)])}
    j = open(os.path.join(rk, "RokuganJournalData.sk"), encoding="utf-8").read()
    out = []
    for qid, who in re.findall(r'id = (\d+), who = (null|"P\d+")', j):
        qid, g = int(qid), mq.get(int(qid))
        if who == '"%s"' % pid or (who == "null" and g and path.get(g[0]) == pid):
            out.append(qid)
    return sorted(set(out))


def side_jobs(only):
    jobs = []
    for job in story_jobs(only):
        i = job["choice"]
        qs = path_quests("P1%02d" % i)
        if qs:
            jobs.append(dict(job, job="side_%d_%s" % (i, PATHS[i].lower()), quests=qs,
                             resume_from="story_%d_%s" % (i, PATHS[i].lower()), title="%d side quests" % len(qs)))
    return jobs


# ------------------------------------------------------------------ one chase run
PROGRESS = re.compile(r"\[RT\] CHASE (GOAL|REACHED|MAP|TALK|SWEPT|OBJECTIVE|BATTLE_END|PROMPT|DROVE)")
MINIGAME_TICK = re.compile(r"\[RT\] mini-game \S+ (?:open|waiting|result)")
TROUBLE = re.compile(r"\[RT\] CHASE (STUCK|NOPROMPT|NOREACT|NOPOINT|NOEVENT|ERROR|BROKEN)|xception in|compile error")


def player_launch(job, minutes, policy, saved_slot=None, drive=False):
    # (user 2026-11-23: "your rensei needs a big level boost before you try him again")
    pack = ["bot wait,36000000", "lv %d" % {"story_1_crane": 70, "story_0_crab": 70, "side_0_crab": 70}.get(job["job"], 40), "mini win", "chase %d" % minutes, "chasepolicy %s" % policy,
            "chasejob %s" % job["job"]]
    start_map, start_pos = job["map"], job["pos"]
    if saved_slot is not None:
        # (2026-11-24: Lion's resume save on M513 came up on M240) a resumed run skips the New Game: no road choice
        # (its opening scene - Lion's has a battle - raced the load), launched in a quiet shop with no scenes
        pack.append("loadsave %d" % saved_slot)
        start_map, start_pos = "M903", "[8.5, 1.5, 5.5, 0.0]"
    else:
        pack.append("choice %d" % job["choice"])
    if job.get("quests"):
        pack.append("chasequests %s" % ",".join(str(q) for q in job["quests"]))
    if drive:                                                          # (the local model takes the stick when the
        pack.append("chasedrive 60")                                   # script is stuck a minute: RokuganChase)
    return [os.path.join(wtool(), "rpgcobo.exe"), "-testplay", "-map", start_map, start_pos,
            "-rtfast", "-rtauto", "-debuglv", "40", "-rt", ";".join(pack)]


def chase(job, minutes, model, know):
    name = job["job"]
    out = os.path.join(PLAYER_RUNS, name)
    os.makedirs(out, exist_ok=True)
    log = os.path.join(out, "log.txt")
    pol, npol = policy_for(name, know)
    snapdir = os.path.join(wtool(), "tmp", "chase", name)
    os.makedirs(snapdir, exist_ok=True)
    for path in glob.glob(os.path.join(snapdir, "snap_*.bin")) + [os.path.join(snapdir, "answer.txt")]:
        if os.path.isfile(path):
            os.remove(path)
    # (user 2026-11-23: "you can use savestates when you get stuck so you can keep going without completely starting
    # from scratch") --resume: start from the job's latest save state (the one it took when it got bored or asked)
    resumed, resume_slot = None, None
    if RESUME:
        def own(files):                                                # (only saves this traveler leads)
            want = "P1%02d" % job["choice"]
            keep = []
            for f in files:
                lf = f[:-4] + ".lead"
                if not os.path.exists(lf) or open(lf, encoding="utf-8").read().strip() == want:
                    keep.append(f)
            return keep
        old = own(sorted(glob.glob(os.path.join(out, "snapshots", "snap_*.bin")), key=os.path.getmtime))
        if not old and job.get("resume_from"):                         # (side quests: from the story's end)
            old = own(sorted(glob.glob(os.path.join(os.path.dirname(out), job["resume_from"], "snapshots",
                                                    "snap_*.bin")), key=os.path.getmtime))
        if old:
            slot = getattr(SLOT, "n", 90)
            save = os.path.join(wtool(), "savedata", "save%03d.bin" % slot)
            os.makedirs(os.path.dirname(save), exist_ok=True)
            shutil.copy(old[-1], save)
            shutil.copy(old[-1], os.path.join(out, "resumed_from.bin"))
            resume_slot = slot
            resumed = os.path.basename(old[-1])
    args = player_launch(job, minutes, pol, resume_slot, drive=bool(model is not None and model.ok))
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
        verdict, waiting, question, asked_at = "unverified end", False, "", 0.0
        while True:
            time.sleep(4)
            text = open(log, encoding="utf-8", errors="replace").read()
            lines = text.splitlines()
            new = lines[seen:]
            seen = len(lines)
            if any(PROGRESS.search(ln) or MINIGAME_TICK.search(ln) for ln in new):
                last_prog = time.time()
            for ln in new:
                if TROUBLE.search(ln) and ln not in flagged:
                    flagged.add(ln)
                    report_stuck(name, ln, lines, loud=False)
                if "[RT] CHASE VIEWEND" in ln:                         # the model's turn at the stick
                    drive(name, lines, model, snapdir)
                if "[RT] CHASE ASK " in ln:
                    # (user 2026-11-24: "squirrels must be hybernating") never wait on Claude: ask() always
                    # answers at once - the local model's move, or "broken" with the question filed in ASK/
                    waiting = False
                    asked_at = time.time()
                    question = ln.split("CHASE ASK ", 1)[1]
                    ask(name, ln, lines, model, snapdir)
                if "[RT] CHASE ANSWER " in ln:
                    waiting = False
                    last_prog = time.time()
                if "[RT] CHASE BROKEN " in ln:
                    say("BROKEN %s: %s" % (name, ln.split("BROKEN ", 1)[1][:200]))
                    verdict = "blocked"
            ans = os.path.join(ANSDIR, name + ".txt")
            if waiting and os.path.exists(ans) and os.path.getmtime(ans) >= asked_at:
                a = open(ans, encoding="utf-8").read().strip()
                os.remove(ans)
                if a != "restart":
                    a = checked_action(a, question, lines)
                    if a is None:
                        report_stuck(name, "Rejected an unsupported playtest action from the handoff", lines)
                        continue
                with open(os.path.join(snapdir, "answer.txt"), "w", encoding="utf-8") as f:
                    f.write(a + "\n")
                say("ANSWERED %s: %s" % (name, a))
                if a.strip() == "restart":                               # Claude fixed the cause: go on from
                    verdict = "restart"
                    break
            if waiting:
                last_prog = time.time()
                if time.time() - t0 > minutes * 60 + 3000:                # (45 min for an answer, then it closes itself)
                    verdict = "no answer"
                    break
                continue
            if any("[RT] CHASE DONE" in ln for ln in new):
                if verdict == "unverified end":
                    ending = next((ln.split("CHASE END ", 1)[1] for ln in reversed(lines)
                                   if "[RT] CHASE END " in ln), "the chase stopped")
                    report_stuck(name, "Unverified route ending: " + ending, lines)
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
                args = player_launch(job, minutes, pol, slot)
                say("RESTART %s (%d) from %s via slot %d, %d learned answers" % (name, restarts,
                                                                              os.path.basename(snaps[-1]), slot, npol))
            else:
                args = player_launch(job, minutes, pol)
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
        shots_now(name, sd)
    except Exception:                                                    # noqa: BLE001 (no shots is fine)
        pass
    text = open(os.path.join(out, "log.txt"), encoding="utf-8", errors="replace").read()
    rows = re.findall(r"\[RT\] CHASE SNAP (\d+) (.+)", text)
    # (2026-11-24: Crane's side quests were played as Hiruma - a road's end starts the next traveler's road, and the
    # newest save was the Crab's) each save notes who leads its party (snap_NN.lead), and --resume only takes a save
    # led by the job's own traveler
    lead = {}
    for n, rest in rows:                                          # (the last line for a number is this run's)
        m = re.search(r"party=(P\d+)", rest)
        if m:
            lead[n] = m.group(1)
    for f in glob.glob(os.path.join(sd, "snap_*.bin")):
        n = os.path.basename(f)[5:-4]
        if n in lead and os.path.getmtime(f) >= time.time() - 6 * 3600:
            with open(f[:-4] + ".lead", "w", encoding="utf-8") as g:
                g.write(lead[n] + "\n")
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


LOCAL_TRIES = {}                                         # (job, goal) -> answers the local model already gave


def observed_targets(question, lines):
    """Find the current position, witnessed prompts, and marker projected on this map."""
    number = r"-?\d+(?:\.\d+)?"
    location = re.search(rf"\| on (M\d+) at ({number}) ({number})(?: |$)", question)
    if not location:
        return None, {}, None
    mid, x, z = location.groups()
    position = (float(x), float(z))
    visit = []
    for line in reversed(lines):
        if "[RT] ARRIVE " in line and f"[RT] ARRIVE {mid} " not in line:
            break
        visit.append(line)
    prompts = {p[1] for line in visit if (p := re.search(r'\[RT\] CHASE PROMPT (.+?): "', line))}
    targets = {}
    event_pattern = rf"\[RT\] CHASE EVENT (\S+) on {mid} at ({number}) ({number}), trigger (\d+)"
    for line in reversed(visit):
        event = re.search(event_pattern, line)
        if event and event[1] in prompts:
            x, z, trigger = event.groups()[1:]
            reach = 0.45 if trigger == "1" else 1.4
            targets[event[1]] = (x, z, reach)
    marker_pattern = rf"\[RT\] marker: .*? \(on {mid}\) at ({number}) ({number}), player "
    marker = next((match.groups() for line in visit if (match := re.search(marker_pattern, line))), None)
    if marker is None:
        goal = re.match(rf"{mid} ({number}) ({number}) \|", question)
        marker = goal.groups() if goal else None
    return position, targets, marker


def in_range(position, target):
    x, z, reach = target
    return math.hypot(float(x) - position[0], float(z) - position[1]) <= reach


def checked_action(answer, question, lines, hint=""):
    answer = " ".join(str(answer).strip().strip("`").split())
    if answer == "close":                                              # (2026-11-24: a local "close" ended Crane's
        return "retry"                                                 #  23-quest run on its first quest)
    if answer == "retry" or re.fullmatch(r"broken .{1,290}", answer):
        return answer
    position, targets, marker = observed_targets(question, lines)
    if position is None:
        return None
    if match := re.fullmatch(r"use ([\w*#-]{1,70})", answer):
        target = targets.get(match[1])
        if target:
            return answer if in_range(position, target) else f"goto {target[0]} {target[1]}"
    if match := re.fullmatch(r"goto (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)", answer):
        if answer == hint:
            return answer
        wanted = tuple(map(float, match.groups()))
        current = ASK_POSITION.search(question)
        points = observed_waypoints(current[1], lines) if current else []
        points.extend(target[:2] for target in targets.values())
        if marker:
            points.append(marker)
        if any(wanted == tuple(map(float, point)) for point in points):
            return answer
    return None


def drive(name, lines, model, snapdir):
    """(user 2026-11-24: "why don't you let the local LLM move the chars if the script fails after a min" / "yeah just
    like let it move all of them") the game shows the model where the squirrel stands (DRIVE + VIEW + VIEWKEY lines,
    RokuganChase.chaseDrive); its one move goes back through answer.txt. Every move is kept in drive_log.md."""
    starts = [k for k, ln in enumerate(lines) if "[RT] CHASE DRIVE " in ln]
    if not starts:
        return
    block = [ln.split("[RT] CHASE ", 1)[1] for ln in lines[starts[-1]:]
             if "[RT] CHASE " in ln and "[RT] CHASE VIEWEND" not in ln]
    res = model.ask({"task": "drive", "job": name, "view": "\n".join(block)}) if model is not None and model.ok else {}
    a = " ".join(str(res.get("answer") or "back").split())[:200]
    with open(os.path.join(snapdir, "answer.txt"), "w", encoding="utf-8") as f:
        f.write(a + "\n")
    with LOCK:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "drive_log.md"), "a", encoding="utf-8") as f:
            f.write("- %s %s | %s -> **%s** (%s)\n" % (time.strftime("%H:%M:%S"), name, block[0][6:150], a,
                                                         str(res.get("why", res.get("error", "")))[:160]))


def ask(name, line, lines, model=None, snapdir=None):
    """A chaser asks (five tries at one goal). (user: "it should be doing this on local and just reporting back to
    you occasionally") The local model answers first - up to two answers per goal; only when those don't help does
    the question go to Claude: the save state, its screenshot, what it tried."""
    q = line.split("CHASE ASK ", 1)[1]
    goal = q.split(" | ")[0]
    tried = LOCAL_TRIES.setdefault((name, goal), [])
    finding = ""
    if model is not None and model.ok and len(tried) < 2 and snapdir:
        evidence = ("[RT] CHASE ", "[RT] BOT at ", "[RT] BOT STUCK", "[RT] ARRIVE ", "[RT] marker:")
        tail = "\n".join(line for line in lines[-150:] if line.startswith(evidence))[-3500:]
        position, targets, marker = observed_targets(q, lines)
        events = "\n".join(
            f"{event}: {x} {z} ({'prompt in reach' if in_range(position, (x, z, reach)) else 'walk to this prompt first'})"
            for event, (x, z, reach) in targets.items()
        )
        if marker:
            events += "\nCurrent map's visible marker: " + " ".join(marker)
        current = ASK_POSITION.search(q)
        if current:
            waypoints = observed_waypoints(current[1], lines)
            if waypoints:
                events += "\nPreviously walked waypoints on this map: " + "; ".join(f"{x:g} {z:g}" for x, z in waypoints[:8])
        remembered = walking_hint(name, q, tried)
        result = {"answer": remembered} if remembered else model.ask(
            {"task": "answer", "question": q, "tail": tail, "events": events, "tried": tried}
        ) or {}
        a = checked_action(result.get("answer", ""), q, lines, hint=remembered)
        if a is None:
            finding = result.get("error", "No supported action in the model's answer")
            a = "retry"
        tried.append(a)
        with open(os.path.join(snapdir, "answer.txt"), "w", encoding="utf-8") as f:
            f.write(a + "\n")
        with LOCK:
            os.makedirs(OUT, exist_ok=True)
            with open(os.path.join(OUT, "local_answers.md"), "a", encoding="utf-8") as f:
                f.write("- %s %s | %s -> **%s**\n" % (time.strftime("%H:%M"), name, q[:160], a))
        if not a.startswith("broken"):
            return
        finding = result.get("why", a[7:])
        report_stuck(name, finding, lines)
    # the local model's answers didn't help: Claude
    os.makedirs(ASKDIR, exist_ok=True)
    os.makedirs(ANSDIR, exist_ok=True)
    out = os.path.join(PLAYER_RUNS, name, "snapshots")
    pngs = shots_now(name, out)
    for f in glob.glob(os.path.join(wtool(), "tmp", "chase", name, "snap_*.bin")):
        shutil.copy(f, out)
    q = line.split("CHASE ASK ", 1)[1]
    tried = [ln.split("CHASE ", 1)[1] for ln in lines[-200:] if "[RT] CHASE " in ln][-40:]
    with LOCK:
        with open(os.path.join(ASKDIR, name + ".md"), "w", encoding="utf-8") as f:
            f.write("# %s asks\n\n**%s**\n\nLocal finding: %s\n\nScreenshot: %s\nSave state: %s (window folder %s)\n\n"
                    "Answer in _art/preview/chase/ANSWERS/%s.txt, one line: retry | goto X Z | use NAME | "
                    "broken [why] | close\n\n## The last things it did\n\n```\n%s\n```\n"
                    % (name, q, finding or "No observed action advanced the quest.", pngs[-1] if pngs else "-",
                       os.path.join(out, "snap_*.bin"), wtool(), name,
                       "\n".join(tried)))
    say("ASK %s: %s" % (name, q[:220]))
    if snapdir:                                       # (filed for Claude; the squirrel saves, reports, goes on)
        with open(os.path.join(snapdir, "answer.txt"), "w", encoding="utf-8") as f:
            f.write("broken filed for Claude (ASK/%s.md): %s\n" % (name, " ".join(q.split())[:160]))


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
    menus = MENU_LOG.findall(text)
    # (2026-11-23) a window closed from outside (code 0: the user closing a looping run) or a restart is no evidence
    # against the menus answered before it
    if verdict.startswith("the game exited") or verdict == "restart":
        know_save(know)
        return
    stalled = verdict=="blocked" or any(marker in text for marker in ("CHASE STUCK", "CHASE BROKEN", "gave up"))
    for key, v, opts in menus:
        m = rec["menus"].setdefault(key, {"tried": [], "n": opts.count(" / ")})
        m["options"] = opts
        if int(v) not in m["tried"]:
            m["tried"].append(int(v))
    if stalled and menus:                                                # the last menus before the stall are suspects
        for key, v, opts in menus[-3:]:
            rec["menus"][key]["stalled"] = True
        rec["stalls"].append({"verdict": verdict, "last": re.findall(r"\[RT\] CHASE GOAL (.+)", text)[-1:]})
    elif verdict=="completed":
        for key, v, opts in menus:
            rec["menus"][key]["good"] = int(v)
            rec["menus"][key].pop("stalled", None)
    know_save(know)


# ------------------------------------------------------------------ notes
def notes(job, out, model, verdict, secs):
    text = open(os.path.join(out, "log.txt"), encoding="utf-8", errors="replace").read()
    L = ["# %s" % job["job"], "", "%s. Ended: %s after %.0f min." % (job.get("title", "From New Game"), verdict, secs / 60),
         "", "Story test assists: " + ", ".join(STORY_ASSISTS) + ".", ""]
    minigame_results = re.findall(r"\[RT\].*?mini-game (\S+) result (\d+)", text)
    difficulty_choices = [(options.split(" / ")[int(choice)], options.split(" / ")[hardest])
                          for _, choice, options in MENU_LOG.findall(text)
                          if (hardest := hardest_option(options)) is not None
                          and int(choice) < len(options.split(" / "))]
    L += ["## Minigames", ""]
    for selected, hardest in difficulty_choices:
        L.append(f"- Selected {selected}. Hardest offered: {hardest}.")
    outcomes = {"0": "did not run", "1": "won", "2": "lost"}
    for game, result in minigame_results:
        L.append(f"- {game}: {outcomes.get(result, 'engine result ' + result)} (assisted).")
    results = re.findall(r"\[RT\] ((?:dance|kabuki): (?:act \d+ )?over - .+)", text)
    L.extend(f"- {result}" for result in results)
    if not minigame_results:
        L.append("- No minigame result observed.")
    L.append("")
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


def report_remaining_coverage(mode):
    """Record standalone coverage the player-only runner cannot yet exercise."""
    remaining = {
        "quests": "Standalone quest fixtures start with pre-set quest flags. Exercise them from a legitimate story save.",
        "games": "Story runs exercise minigames with assisted self-play. Standalone input and difficulty coverage still need verification.",
    }
    kinds = ("quests", "games") if mode == "all" else (mode,)
    os.makedirs(PLAYER_RUNS, exist_ok=True)
    path = os.path.join(PLAYER_RUNS, "coverage-pending.md")
    with open(path, "a", encoding="utf-8") as target:
        for kind in kinds:
            target.write(f"- {remaining[kind]} Coverage is unverified.\n")
    say("Unverified standalone coverage recorded at " + os.path.normpath(path))


# ------------------------------------------------------------------ main
def main():
    a = sys.argv[1:]
    what = a[0] if a and not a[0].startswith("--") else "story"
    if what not in ("story", "sidequests", "quests", "games", "all"):
        raise SystemExit("Choose story, sidequests, quests, games, or all.")
    if what not in ("story", "sidequests"):
        report_remaining_coverage(what)
        if what != "all":
            return

    def opt(k, d):
        return a[a.index(k) + 1] if k in a else d
    only = set(opt("--only", "").split(",")) - {""}
    global RESUME
    RESUME = "--resume" in a
    minutes, windows = int(opt("--minutes", "60")), int(opt("--windows", "2"))
    q = side_jobs(only) if what == "sidequests" else story_jobs(only)
    profile_root = opt("--profiles", "")
    candidates = [os.path.join(profile_root, slot) for slot in ("slot-a", "slot-b")] if profile_root else [TOOL, TOOL2]
    engine_folders = [p for p in candidates if os.path.isfile(os.path.join(p, "rpgcobo.exe"))
                      and os.path.isfile(os.path.join(p, "project", "plugin", "rokugan", "RokuganChase.sk"))]
    if "--engine" in a:                                                 # (--engine -w2: this run only uses that
        engine_folders = [TOOL + opt("--engine", "").replace("main", "")]   #  folder, so two runs can share the PC)
    if not engine_folders:
        raise SystemExit("Travelers' native game executable was not found.")
    windows = min(max(1, windows), len(engine_folders))
    say("JOBS %d (%d windows)" % (len(q), windows))
    use_model = "--no-llm" not in a
    model = Model(use_model)
    if use_model and not model.ok:
        model.close()
        raise SystemExit("The Squirrels' Ollama model is unavailable. Start Ollama before running with the adviser.")
    know = know_load()

    def worker(window, engine):
        SLOT.n = 90 + ([TOOL, TOOL2].index(engine) if engine in (TOOL, TOOL2) else window)   # (by folder: two runs never share a save slot)
        SLOT.tool = engine
        while True:
            with LOCK:
                if not q:
                    return
                job = q.pop(0)
            try:
                chase(job, minutes, model, know)
            except Exception as e:                                       # noqa: BLE001 (keep the other window going)
                report_stuck(job["job"], "Python runner failed: " + str(e), [])
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
    ts = [threading.Thread(target=worker, args=(i, engine)) for i, engine in enumerate(engine_folders[:windows])]
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
