"""Play one path from New Game like a player (user, 2026-11-10: "simulate each path ... approach it like a player").
The in-game test player (RokuganBot.sk, serve mode) walks; this script watches its live state (map, position, story
flags) and decides what a player would do next: the nearest thing the story is waiting on (an arrival scene on another
map, a walk-on scene, someone to talk to), the route there (map to map through open exits, a walking path on each
map), then walks it, talks, and repeats. Battles run on Auto; choices take the first option; save menus are skipped.
python -E tools/storyplay.py PATH [--lv 60] [--legs 400] [--minutes 90]      PATH: 0 Crab ... 7 Ronin
Output: _art/preview/bot/story_PATH/ (log.txt, play.txt = the playthrough as a readable list, shots)."""
import json
import os
import re
import subprocess
import sys
import time
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402
import exittour as et  # noqa: E402
import playbot as pb  # noqa: E402

PATHS = ["Crab", "Crane", "Lion", "Phoenix", "Dragon", "Scorpion", "Unicorn", "Ronin"]
TOOL = gm.TOOL
MP = json.load(open(os.path.join(gm.PROJ, "data", "map.json"), encoding="utf-8"))
GV = json.load(open(os.path.join(gm.PROJ, "data", "gvar.json"), encoding="utf-8"))
DEF = {k: v.get("defval") for k, v in GV.items() if isinstance(v, dict)}


# ------------------------------------------------------------------ conditions on live values
def val(flags, k):
    if k in flags:
        return flags[k]
    d = DEF.get(k)
    return d if d is not None else False


def test(a, op, b):
    a1 = 0 if a is False else 1 if a is True else a
    b1 = 0 if b is False else 1 if b is True else b
    try:
        return {"==": a1 == b1, "!=": a1 != b1, ">=": a1 >= b1, "<=": a1 <= b1, ">": a1 > b1, "<": a1 < b1}[op]
    except (TypeError, KeyError):
        return True


def holds(reqs, flags):
    for r in reqs or []:
        lv = r.get("lvar")
        if not (isinstance(lv, str) and re.match(r"^G\d+$", lv)):
            continue                                              # items, money, script temporaries: assume yes
        rv = r.get("rvar")
        if isinstance(rv, str) and re.match(r"^G\d+$", rv):
            rv = val(flags, rv)
        if not test(val(flags, lv), r.get("op", "=="), rv):
            return False
    return True


def page_now(e, flags):
    if not holds(e.get("reqs0"), flags):
        return None, None
    pages = e.get("page") or []
    for n in range(len(pages) - 1, -1, -1):
        if holds(pages[n].get("reqs"), flags):
            return n, pages[n]
    return None, None


def would_change(page, flags):
    """Does this page set any story flag to something it isn't now? (it moves the story) IF blocks follow the branch
    the live flags would take (a scene guarded by "not seen yet and after X" does nothing before X)."""
    def walk(cmds):
        for c in cmds or []:
            if not isinstance(c, dict):
                continue
            if c.get("cmd") == "cmd_if":
                br = c.get("cmdblocks") or []
                pick = br[0] if holds(c.get("reqs"), flags) else (br[1] if len(br) > 1 else [])
                if walk(pick):
                    return True
                continue
            if c.get("cmd") == "cmd_compute" and isinstance(c.get("lvar"), str) and re.match(r"^G\d+$", c["lvar"]):
                rv = c.get("rvar")
                if isinstance(rv, (bool, int)) and (c.get("op") != "=" or not test(val(flags, c["lvar"]), "==", rv)):
                    return True
            for k in ("cmdblocks",):
                for b in c.get(k) or []:
                    if walk(b):
                        return True
        return False
    return walk(page.get("cmdblock"))


# ------------------------------------------------------------------ maps
_grid = {}


def grid(mid):
    if mid not in _grid:
        m, ev = gm.make(mid)
        seen, blocked, fl = et.reach_map(m, ev)
        _grid[mid] = (m, ev, seen, fl)
    return _grid[mid]


def exits(mid, flags):
    """(dest, cell x, z, push key) for every exit open now."""
    out = []
    for key, e in (MP[mid].get("event") or {}).items():
        if e.get("memo") == "barricade" or "pos" not in e:
            continue
        x, z = int(round(e["pos"][0])), int(round(e["pos"][2]))
        fp = et.footprint(e, 10 ** 6, 10 ** 6) or {(x, z)}                 # (the whole box: an edge strip's middle
        if e.get("role") == "portal" and e.get("dest"):                    # can be a cliff)
            if holds(e.get("reqs0"), flags):
                push = {0: "up", 1: "right", 2: "down", 3: "left"}.get(e["pos"][3], "up")
                out.append((e["dest"]["mapid"], x, z, push, fp))
        else:
            n, pg = page_now(e, flags)
            if pg and pg.get("trigger") in (1, 2):                     # examine to go (a cave mouth, a ladder)
                s = json.dumps(pg.get("cmdblock"))
                if "cmd_mapmove" in s:                                 # (a guard: "Go up? (Night falls.)")
                    d = re.findall(r'"cmd": "cmd_mapmove", "dest": \{"mapid": "(M\d+)"', s)
                    if d:
                        out.append((d[0], x, z, "talk", {(x, z)}))
            cb = (pg or {}).get("cmdblock") or []
            if cb and isinstance(cb[0], dict) and cb[0].get("cmd") == "cmd_if" and not holds(cb[0].get("reqs"), flags):
                pg = None                                              # a scene that isn't ready yet
            if pg and pg.get("trigger") == 5:
                s = json.dumps(pg.get("cmdblock"))
                if s.startswith('[{"cmd": "cmd_mapmove"') or (len(pg.get("cmdblock") or []) <= 3 and "cmd_mapmove" in s):
                    d = re.findall(r'"mapid": "(M\d+)"', s)
                    if d:
                        out.append((d[0], x, z, {0: "up", 1: "right", 2: "down", 3: "left"}.get(e["pos"][3], "up"),
                                    fp))
    return [o for o in out if o[0] in MP and o[0] != mid and not ("M800" <= o[0] < "M900")]


CHOICE_PAGES = set()                                              # (map, event@page) that open a menu
BROKEN = set()                                                  # (map, next map): its exit never took us there


def map_route(src, dst, flags):
    prev = {src: None}
    q = deque([src])
    while q:
        m = q.popleft()
        if m == dst:
            out = []
            while m:
                out.append(m)
                m = prev[m]
            return out[::-1]
        for d, *_ in exits(m, flags):
            if d not in prev and (m, d) not in BROKEN:
                prev[d] = m
                q.append(d)
    return None


def walk_steps(mid, start, goal_cells):
    m, ev, seen, fl = grid(mid)
    sx, sz = int(start[0]), int(start[1])
    if not (0 <= sx < m.w and 0 <= sz < m.d):
        return None
    best = None
    for dx in range(-3, 4):                                       # snap the start onto the walk grid
        for dz in range(-3, 4):
            x, z = sx + dx, sz + dz
            if 0 <= x < m.w and 0 <= z < m.d and seen[z, x] and (best is None or abs(dx) + abs(dz) < best[0]):
                best = (abs(dx) + abs(dz), x, z)
    if not best:
        return None
    goals = {g for g in goal_cells if 0 <= g[0] < m.w and 0 <= g[1] < m.d and seen[g[1], g[0]]}
    if not goals:
        return None
    route = et.path(seen, fl, (best[1], best[2]), goals)
    if not route:
        return None
    return ["goto %.1f %.1f 4000" % (x + 0.5, z + 0.5) for x, z in route[2::3] + [route[-1]]]


def near(x, z, r=1):
    return {(x + dx, z + dz) for dx in range(-r, r + 1) for dz in range(-r, r + 1)}


# ------------------------------------------------------------------ what would a player do next
def targets(flags, here):
    """Story events that can run now and would move the story, with what to do to run them."""
    out = []
    for mid, mp in MP.items():
        if not re.match(r"^M[1-7]\d\d$", mid) or not isinstance(mp, dict):
            continue
        for key, e in (mp.get("event") or {}).items():
            if e.get("role") in ("clerk", "hotel", "itemchest", "portal") or e.get("memo") == "barricade":
                continue
            n, pg = page_now(e, flags)
            if pg is None or pg.get("trigger") not in (1, 2, 5, 6) or not would_change(pg, flags):
                continue
            s = json.dumps(pg)
            prio = 0 if "Objective" in s else 1
            if pg.get("trigger") == 6:
                prio -= 1                                         # a scene that plays on arrival
            out.append((prio, mid, "%s@%d" % (key, n), pg.get("trigger"), int(round(e["pos"][0])),
                        int(round(e["pos"][2]))))                     # (tries count per page: a new page is new)
            if "cmd_choices" in s:
                CHOICE_PAGES.add((mid, "%s@%d" % (key, n)))
    return out


def plan(state, flags, tried):
    mid, x, z = state
    best = None
    for prio, tm, key, trig, tx, tz in targets(flags, mid):
        if tried.get((tm, key), 0) >= (6 if (tm, key) in CHOICE_PAGES else 2):   # a menu: try its other answers
            continue
        r = map_route(mid, tm, flags)
        if r is None:
            continue
        cost = (prio, len(r), abs(tx - x) + abs(tz - z) if tm == mid else 0)
        if best is None or cost < best[0]:
            best = (cost, tm, key, trig, tx, tz, r)
    if not best:
        return None, None
    _c, tm, key, trig, tx, tz, r = best
    if len(r) > 1:                                                # walk to the next map on the route
        nxt = r[1]
        for d, ex, ez, push, fp in exits(mid, flags):
            if d == nxt and push == "talk":
                w = walk_steps(mid, (x, z), near(ex, ez, 2) - near(ex, ez, 0))
                if w is not None:
                    return (tm, key, "go %s via %s" % (tm, nxt), (mid, nxt)), w + [
                        "face %d %d" % (ex, ez), "tap z", "untilmap %s 12000" % nxt, "wait 800"]
                continue
            if d == nxt:
                gmap = grid(mid)[0]                                    # a player follows the road out
                road = {(a, b) for a, b in fp if 0 <= b < gmap.d and 0 <= a < gmap.w and gmap.blk[b, a] == gm.ROAD}
                w = walk_steps(mid, (x, z), {c for a, b in (road or fp) for c in near(a, b)})
                if w is not None:
                    if len(fp) <= 9:                                   # a door: line up in front of it, push in
                        bx, bz = {"up": (0, -2), "down": (0, 2), "left": (2, 0), "right": (-2, 0)}[push]
                        w = w + ["goto %.1f %.1f 3000" % (ex + bx + 0.5, ez + bz + 0.5)]
                    return (tm, key, "go %s via %s" % (tm, nxt), (mid, nxt)), w + ["hold %s 900" % push, "untilmap %s 12000" % nxt,
                                                                       "wait 800"]
        return (tm, key, "no walking route to the %s exit" % nxt), None
    if trig == 6:
        return (tm, key, "arrival scene"), ["wait 1500"]
    if trig == 5:
        w = walk_steps(mid, (x, z), near(tx, tz))
        return (tm, key, "walk onto"), (w + ["goto %.1f %.1f 4000" % (tx + 0.5, tz + 0.5), "wait 1500"]) if w is not None else None
    w = walk_steps(mid, (x, z), near(tx, tz, 1) - near(tx, tz, 0))   # beside them (talk reaches ~1 m)
    if w is None:
        w = walk_steps(mid, (x, z), near(tx, tz, 2) - near(tx, tz, 1))   # across a counter
    return (tm, key, "talk"), (w + ["talkto %d %d" % (tx, tz), "wait 2000"]) if w is not None else None


# ------------------------------------------------------------------ the loop
def main():
    a = sys.argv[1:]
    opts = {"--lv": "60", "--legs": "400", "--minutes": "90"}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1]
            a = a[:i] + a[i + 2:]
    path = int(a[0])
    name = "story_%d" % path
    out = os.path.join(HERE, "..", "_art", "preview", "bot", name)
    os.makedirs(out, exist_ok=True)
    cmdf = os.path.join(TOOL, "tmp", "bot", name + "_cmd.txt")
    os.makedirs(os.path.dirname(cmdf), exist_ok=True)
    flagnames = sorted(k for k in GV if re.match(r"^G\d+$", k))

    def cmd(n, steps, quit_=False):
        tmp = cmdf + ".tmp"
        json.dump({"n": n, "steps": [s.replace(" ", ",") for s in steps], "flags": flagnames, "quit": quit_},
                  open(tmp, "w"))
        os.replace(tmp, cmdf)                                     # (never a half-written file)
    cmd(0, [])
    shots = os.path.join(TOOL, "tmp", "rt_shot")
    os.makedirs(shots, exist_ok=True)
    for f in os.listdir(shots):
        if f.startswith("bot_%s_" % name):
            os.remove(os.path.join(shots, f))
    subprocess.run(["taskkill", "/IM", "rpgcobo.exe", "/F"], capture_output=True)
    log = os.path.join(out, "log.txt")
    args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-map", "M099", pb.start_pos("M099", *pb.block("M099", 12, 6)), "-rtvar",
            "G000", "-rtfast", "-rtauto", "-debuglv", opts["--lv"],
            "-rt", "bot serve,tmp/bot/%s_cmd.txt;choice %d" % (name, path)]
    lf = open(log, "w")
    proc = subprocess.Popen(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    play = open(os.path.join(out, "play.txt"), "w", encoding="utf-8")

    def note(s):
        print(s)
        play.write(s + "\n")
        play.flush()
    note("== %s path, level %s" % (PATHS[path], opts["--lv"]))
    t0, n, tried, seen_lines = time.time(), 0, {}, 0
    last_flags, what, fails = None, None, {}
    send = ["wait 4000"]                                          # the prologue plays first
    while n < int(opts["--legs"]) and time.time() - t0 < float(opts["--minutes"]) * 60:
        n += 1
        cmd(n, send)
        state = flags = None
        t1 = time.time()
        while time.time() - t1 < 240 and proc.poll() is None:
            time.sleep(0.5)
            lines = [ln[ln.find("[RT]"):] if "[RT]" in ln else ln
                     for ln in open(log, errors="replace").read().splitlines()]
            for ln in lines[seen_lines:]:
                if "[RT] MSG" in ln and ("Objective" in ln or "- complete" in ln or "CHAPTER" in ln):
                    note("   " + ln[ln.find("[RT] MSG") + 9:][:150])
                if "xception in thread" in ln or "ERROR" in ln:
                    note("   !! " + ln[:160])
                if "[RT] BOT STUCK" in ln:
                    note("   stuck: " + ln[ln.find("STUCK"):][:120])
            seen_lines = len(lines)
            st = [l for l in lines if l.startswith("[RT] BOT state %d " % n)]
            fl = [l for l in lines if l.startswith("[RT] BOT flags %d" % n)]
            if st and fl:
                p = st[-1].split()
                state = (p[4], float(p[5]), float(p[6]))
                raw = fl[-1].split(" ", 4)[4] if len(fl[-1].split(" ", 4)) > 4 else ""
                flags = {}
                for kv in raw.split(","):
                    if "=" in kv:
                        k, v = kv.split("=")
                        flags[k] = True if v == "1" and GV.get(k, {}).get("type") == 1 else int(v) if v.lstrip("-").isdigit() else True
                break
        if state is None:
            note("!! no answer from the game (crashed or hung) after leg %d" % n)
            break
        if what and len(what) > 3 and state[0] == what[3][0]:          # a "go" leg that left us where we were
            fails[what[3]] = fails.get(what[3], 0) + 1
            if fails[what[3]] >= 3:
                BROKEN.add(what[3])
                note("!! BUG? the exit %s -> %s did not take the player there (twice); routing around it" % what[3])
        if what and what[2] in ("talk", "walk onto", "arrival scene"):     # did the last try move the story?
            newly = [k for k, v in (flags or {}).items() if v is True and (last_flags or {}).get(k) is not True]
            if newly:
                note("   + " + ",".join(sorted(newly)))
            tried[(what[0], what[1])] = tried.get((what[0], what[1]), 0) + 1   # every page gets two tries
        last_flags = flags
        what, steps = plan(state, flags, tried)
        if what is None:
            note("-- nothing left that moves the story (at %s %.0f,%.0f)" % state)
            break
        if steps is None:
            note("!! %s %s: %s" % (what[0], what[1], what[2]))
            tried[(what[0], what[1])] = 9
            send = ["wait 300"]
            continue
        note("%3d %s %4.0f,%-4.0f -> %s %s (%s)" % (n, state[0], state[1], state[2], what[0], what[1], what[2]))
        send = steps + ["shot %s_%03d" % (name, n + 1)]                 # what the player sees after this leg
    cmd(n + 1, [], True)
    time.sleep(2)
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    pb.convert_shots(name, out)
    note("== %d legs, %.0f min" % (n, (time.time() - t0) / 60))


if __name__ == "__main__":
    main()
