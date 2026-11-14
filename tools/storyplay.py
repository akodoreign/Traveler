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
                unknown = any(not (isinstance(r.get("lvar"), str) and re.match(r"^G\d+$", r["lvar"]))
                              for r in c.get("reqs") or [])
                if unknown:                                       # (W from a script, an item, money: either way)
                    if any(walk(b) for b in br):
                        return True
                    continue
                pick = br[0] if holds(c.get("reqs"), flags) else (br[1] if len(br) > 1 else [])
                if walk(pick):
                    return True
                continue
            if c.get("cmd") == "cmd_compute" and isinstance(c.get("lvar"), str) and re.match(r"^G\d+$", c["lvar"])                     and c["lvar"] not in TOGGLES:                 # (a switch that flips back and forth: wax in/out)
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


def grid(mid, strict=False):
    if mid not in _grid:
        m, ev = gm.make(mid)
        seen, blocked, fl = et.reach_map(m, ev)
        wide = seen.copy()                                        # strict: 2 cells clear of every tree trunk (a
        for o in m.objs:                                          # canopy collides wider than reach_map's 1 cell:
            if o.get("t") == "fb" and o.get("fbtype") == 20 and o.get("fbparam") in (gm.TREE_L, gm.TREE_M):
                x, z = o["x"], o["z"]                             # the bot wedged between M103's padding trees)
                wide[max(0, z - 2):z + 3, max(0, x - 2):x + 3] = False
        for e in (MP.get(mid, {}).get("event") or {}).values():   # never walk across a door on the way somewhere
            s = json.dumps(e.get("page") or [])                   # else (M141: the route east crossed the inn door,
            if "pos" in e and (e.get("role") == "portal" or '"trigger": 5' in s and "cmd_mapmove" in s):  # in, out,
                fp = et.footprint(e, m.w, m.d)                    # in ... forever)
                if fp and len(fp) <= 9:
                    for x, z in fp:
                        if 0 <= x < m.w and 0 <= z < m.d:
                            seen[z, x] = wide[z, x] = False
        _grid[mid] = (m, ev, seen, fl, wide)
    m, ev, seen, fl, wide = _grid[mid]
    return (m, ev, wide if strict else seen, fl)


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
                    menu = menu_moves(pg.get("cmdblock"))
                    if menu:                                           # a menu of places (the sea chart): each
                        for i, dests in menu:                          # answer is its own way out
                            for dd in dests:
                                out.append((dd, x, z, "talk%d" % i, {(x, z)}))
                    else:
                        d = re.findall(r'"cmd": "cmd_mapmove", "dest": \{"mapid": "(M\d+)"', s)
                        if d:
                            out.append((d[0], x, z, "talk", {(x, z)}))
            cb = (pg or {}).get("cmdblock") or []
            if cb and isinstance(cb[0], dict) and cb[0].get("cmd") == "cmd_if" and not holds(cb[0].get("reqs"), flags):
                pg = None                                              # a scene that isn't ready yet
            if pg and pg.get("trigger") == 5:
                s = json.dumps(pg.get("cmdblock"))
                top = [c.get("cmd") for c in pg.get("cmdblock") or [] if isinstance(c, dict)]
                fades = all(t in ("cmd_screenfxon", "cmd_wait", "cmd_mapmove", "cmd_screenfxoff", "cmd_se") for t in top)
                if s.startswith('[{"cmd": "cmd_mapmove"') or (len(pg.get("cmdblock") or []) <= 3 and "cmd_mapmove" in s)                         or ("cmd_mapmove" in top and fades):           # (a fade to black, then the move: M329's door)
                    d = re.findall(r'"mapid": "(M\d+)"', s)
                    if d:
                        out.append((d[0], x, z, {0: "up", 1: "right", 2: "down", 3: "left"}.get(e["pos"][3], "up"),
                                    fp))
    return [o for o in out if o[0] in MP and o[0] != mid and not ("M800" <= o[0] < "M900")]


def menu_moves(cmds):
    """[(answer, [maps it moves to]), ...] for the first menu in cmds whose answers lead to different maps."""
    for c in cmds or []:
        if not isinstance(c, dict):
            continue
        if c.get("cmd") == "cmd_choices":
            res = []
            for i, br in enumerate(c.get("cmdblocks") or []):
                d = [m for m in re.findall(r'"mapid": "(M\d+)"', json.dumps(br)) if "M100" <= m < "M800"]
                if d:
                    res.append((i, sorted(set(d))))
            if len(res) > 1:
                return res
        for b in c.get("cmdblocks") or []:
            r = menu_moves(b)
            if r:
                return r
    return None


TOGGLES = set()                                                  # flags newly set 3+ times: state switches, not story
FLIPS = {}
CHOICE_PAGES = set()                                              # (map, event@page) that open a menu
HIRE_PAGES = set()                                                # (map, event@page) of hirelings
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


def push_step(ex, ez, push, w=None, fp=None):
    """Walk on through the doorway (a goto in map terms: the keys are camera-relative, and an interior's camera
    turned M260's "down" into a wall push). An edge strip is crossed straight from where the walk ended (its centre
    can be 35 squares away: M288's north strip)."""
    dx, dz = {"up": (0, 1), "down": (0, -1), "right": (1, 0), "left": (-1, 0)}[push]
    if fp and len(fp) > 9 and w:
        lx, lz = (float(v) for v in w[-1].split()[1:3])
        if dx:
            return "goto %.1f %.1f 4000" % (ex + 0.5 + dx * 2.0, lz)
        return "goto %.1f %.1f 4000" % (lx, ez + 0.5 + dz * 2.0)
    return "goto %.1f %.1f 2500" % (ex + 0.5 + dx * 2.0, ez + 0.5 + dz * 2.0)


def door_push(mid, ex, ez, push, fp=None):
    """Which way a door is walked into: toward its wall (the one side that is rock, a building or off the map).
    The portal's own facing is the way you face coming OUT of it on that side, not always the way in (M227's west
    cave door, d=1, is walked into going left)."""
    m, _ev, seen, fl, _w = _grid[mid] if mid in _grid else (grid(mid) and _grid[mid])
    dirs = (("up", (0, 1)), ("down", (0, -1)), ("right", (1, 0)), ("left", (-1, 0)))
    if fp and len(fp) > 1:                                        # a door box lies along its wall: walk in across it
        xs, zs = {a for a, b in fp}, {b for a, b in fp}
        if len(xs) > len(zs):
            dirs = dirs[:2]
            if push not in ("up", "down"):
                return push
        elif len(zs) > len(xs):
            dirs = dirs[2:]
            if push not in ("left", "right"):
                return push
    for reach in (1, 2):                                          # (a door a square out from its wall)
        walls = []
        for key, (dx, dz) in dirs:
            a, b = ex + dx * reach, ez + dz * reach
            if not (0 <= a < m.w and 0 <= b < m.d) or fl[b, a] < 0 or int(fl[b, a]) >= int(fl[ez, ex]) + 3:
                walls.append(key)
        if len(walls) == 1:
            return walls[0]
        if walls:
            break
    return push


def road_path(m, seen, fl, start, goals):
    """Cheapest walk, a road square costing a third of open ground (a player follows the road, not the forest)."""
    import heapq
    cost = {start: 0}
    prev = {start: None}
    h = [(0, start)]
    while h:
        c0, c = heapq.heappop(h)
        if c0 > cost.get(c, 1e9):
            continue
        if c in goals:
            out = []
            while c:
                out.append(c)
                c = prev[c]
            return out[::-1]
        for nb in et.nbrs(c[0], c[1], seen, fl):
            nc = c0 + (1 if m.blk[nb[1], nb[0]] == gm.ROAD else 3)
            if nc < cost.get(nb, 1e9):
                cost[nb] = nc
                prev[nb] = c
                heapq.heappush(h, (nc, nb))
    return None


def walk_steps(mid, start, goal_cells):
    """Clear of trees by 2 cells if it can (roads, not the padding forest), else the plain walk grid."""
    return _walk_steps(mid, start, goal_cells, True) or _walk_steps(mid, start, goal_cells, False)


def _walk_steps(mid, start, goal_cells, strict):
    m, ev, seen, fl = grid(mid, strict)
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
    route = road_path(m, seen, fl, (best[1], best[2]), goals)
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
            if "cmd_moneyop" in s or "W = n <= 1" in s or ("answer the Guest call" in s and pg.get("trigger") == 2
                    and "Objective" not in s):
                # a hireling, an optional companion (Yosai: "W" = room in the party) or a Guest-call offer:
                # side business, one try, last
                prio = 2
                HIRE_PAGES.add((mid, "%s@%d" % (key, n)))
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
        if tried.get((tm, key), 0) >= (1 if (tm, key) in HIRE_PAGES else 6 if (tm, key) in CHOICE_PAGES else
                                       3 if trig == 6 else 2):
            continue                                              # (a menu: try its other answers)
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
            if d == nxt and push.startswith("talk"):
                ring, fl = near(ex, ez, 2) - near(ex, ez, 0), grid(mid)[3]
                ey = min([e["pos"][1] for e in (MP[mid].get("event") or {}).values()
                          if e.get("pos") and int(e["pos"][0]) == ex and int(e["pos"][2]) == ez] or [0]) - 1
                level = {(a, b) for a, b in ring if 0 <= b < fl.shape[0] and 0 <= a < fl.shape[1] and int(fl[b, a]) == ey}
                w = (walk_steps(mid, (x, z), level) if level else None) or walk_steps(mid, (x, z), ring)
                if w is not None:
                    ans = ["answer %s" % push[4:]] if push[4:] else []   # (the sea chart: this answer goes there)
                    return (tm, key, "go %s via %s" % (tm, nxt), (mid, nxt)), w + ans + [
                        "talkto %d %d" % (ex, ez), "untilmap %s 12000" % nxt, "wait 800"]
                continue
            if d == nxt:
                gmap = grid(mid)[0]                                    # a player follows the road out
                road = {(a, b) for a, b in fp if 0 <= b < gmap.d and 0 <= a < gmap.w and gmap.blk[b, a] == gm.ROAD}
                goal = {c for a, b in (road or fp) for c in near(a, b)}
                if len(fp) > 9 and push in ("up", "down", "left", "right"):   # an edge strip: stop 3 squares short
                    sx, sz = {"up": (0, 1), "down": (0, -1), "right": (1, 0), "left": (-1, 0)}[push]   # and cross it
                    goal = {(a - 3 * sx, b - 3 * sz) for a, b in (road or fp)}       # walking (a body must pass
                w = walk_steps(mid, (x, z), goal)                                    # wholly through the box)
                if w is not None:
                    if len(fp) <= 9:                                   # a door: line up in front of it, push in
                        push = door_push(mid, ex, ez, push, fp)
                        bx, bz = {"up": (0, -2), "down": (0, 2), "left": (2, 0), "right": (-2, 0)}[push]
                        w = w + ["goto %.1f %.1f 3000" % (ex + bx + 0.5, ez + bz + 0.5)]
                    return (tm, key, "go %s via %s" % (tm, nxt), (mid, nxt)), w + [push_step(ex, ez, push, w, fp), "untilmap %s 12000" % nxt,
                                                                       "wait 800"]
        return (tm, key, "no walking route to the %s exit" % nxt), None
    if trig == 6:
        if abs(tx - x) + abs(tz - z) > 8:                         # an autorun only exists while its spot is on
            w = walk_steps(mid, (x, z), near(tx, tz, 3) - near(tx, tz, 0))    # screen (spawndist 1): go there
            if w is not None:                                     # (M282's Silent Court card at x 76, landing 29)
                return (tm, key, "arrival scene"), w + ["wait 1500"]
        if tried.get((tm, key), 0) >= 1:                          # an arrival scene that waits for you to ARRIVE
            for d, ex, ez, push, fp in exits(mid, flags):          # (M267: its flag was set while we were here):
                if (mid, d) in BROKEN or push.startswith("talk"):  # step out and come back, as a player would
                    continue
                gmap = grid(mid)[0]
                road = {(a, b) for a, b in fp if 0 <= b < gmap.d and 0 <= a < gmap.w and gmap.blk[b, a] == gm.ROAD}
                w = walk_steps(mid, (x, z), {c for a, b in (road or fp) for c in near(a, b)})
                if w is not None:
                    if len(fp) <= 9:
                        push = door_push(mid, ex, ez, push, fp)
                    return (tm, key, "go %s via %s" % (d, d), (mid, d)), w + [push_step(ex, ez, push, w, fp),
                                                                           "untilmap %s 12000" % d, "wait 800"]
        return (tm, key, "arrival scene"), ["wait 1500"]
    if trig == 5:
        w = walk_steps(mid, (x, z), near(tx, tz))
        return (tm, key, "walk onto"), (w + ["goto %.1f %.1f 4000" % (tx + 0.5, tz + 0.5), "wait 1500"]) if w is not None else None
    ring = near(tx, tz, 1) - near(tx, tz, 0)                        # beside them (talk reaches ~1 m), on their
    fl = grid(mid)[3]                                                 # floor (not up on the table they stand at)
    ty = (MP[mid]["event"].get(key.split("@")[0]) or {}).get("pos", [0, 0])[1] - 1
    level = {(a, b) for a, b in ring if 0 <= b < fl.shape[0] and 0 <= a < fl.shape[1] and int(fl[b, a]) == ty}
    w = walk_steps(mid, (x, z), level) if level else None
    if w is None:
        w = walk_steps(mid, (x, z), ring)
    if w is None:
        w = walk_steps(mid, (x, z), near(tx, tz, 2) - near(tx, tz, 1))   # across a counter
    gear = []                                                     # a mask gate: wear the mask it asks for
    pg = (MP[tm]["event"].get(key.split("@")[0]) or {}).get("page") or []
    pi = int(key.split("@")[1]) if "@" in key else 0
    for pid, aid in re.findall(r'wearsMask\( \\"(P\d+)\\", \\"(A\d+)\\"\)', json.dumps(pg[pi] if pi < len(pg) else {})):
        gear = ["equip %s 4 %s" % (pid, aid)]
    return (tm, key, "talk"), (w + gear + ["talkto %d %d" % (tx, tz), "wait 2000"]) if w is not None else None


def rest_plan(state, flags):
    """Somebody is down or under half HP: a player rests first, at anything on this map that offers "Rest and save."
    (a save shrine, the gate before the finale's waves, the glade's last save)."""
    mid, x, z = state
    for key, e in (MP.get(mid, {}).get("event") or {}).items():
        n, pg = page_now(e, flags) if "pos" in e else (None, None)
        if pg and pg.get("trigger") in (1, 2) and '"Rest and save."' in json.dumps(pg):
            tx, tz = int(round(e["pos"][0])), int(round(e["pos"][2]))
            w = walk_steps(mid, (x, z), near(tx, tz, 1) - near(tx, tz, 0)) or                 walk_steps(mid, (x, z), near(tx, tz, 2) - near(tx, tz, 1))
            if w is not None:
                return (mid, key, "rest at the shrine"), w + ["talkto %d %d" % (tx, tz), "wait 2500"]
    return None, None


# ------------------------------------------------------------------ checkpoints (save / resume)
CKDIR = os.path.join(HERE, "..", "_art", "preview", "bot", "checkpoints")
TANK = "--tank" in sys.argv                                       # --tank: nobody falls (-rttank), to see what comes
                                                                  # after a fight the auto-battler keeps losing
PARTY0 = "P100"                                                   # who a -testplay start has in the party


def parse_flags(raw):
    flags = {}
    for kv in raw.split(","):
        if "=" in kv:
            k, v = kv.split("=")
            flags[k] = True if v == "1" and GV.get(k, {}).get("type") == 1 else int(v) if v.lstrip("-").isdigit() else True
    return flags


def parse_kit(raw):
    """'party=P100+P120 money=40 items=I104x5+I200x1' -> dict"""
    kit = {"party": [], "money": 0, "items": []}
    for part in raw.split():
        k, _, v = part.partition("=")
        if k == "party":
            kit["party"] = [p for p in v.split("+") if p]
        elif k == "money":
            kit["money"] = int(v) if v.lstrip("-").isdigit() else 0
        elif k == "items":
            kit["items"] = [p for p in v.split("+") if p]
        elif k == "equip":
            kit["equip"] = [p for p in v.split(",") if p]
        elif k == "hurt":
            kit["hurt"] = int(v) if v.isdigit() else 0
    return kit


def save_checkpoint(path, n, state, flags, kit, chapter, done, why, tried, broken, extra=None):
    """_art/preview/bot/checkpoints/path_N.json (the latest) + path_N_<why>.json (kept: one per chapter start)."""
    os.makedirs(CKDIR, exist_ok=True)
    ck = {"path": path, "name": PATHS[path], "leg": n, "map": state[0], "x": state[1], "z": state[2],
          "y": state[3] if len(state) > 3 else None, "flags": flags, "kit": kit, "chapter": chapter,
          "chapters_done": done, "why": why, "saved": time.strftime("%Y-%m-%d %H:%M"),
          "tried": [[m, k, c] for (m, k), c in sorted(tried.items())], "broken": sorted(list(b) for b in broken)}
    ck.update(extra or {})
    for f in ["path_%d.json" % path] + (["path_%d_%s.json" % (path, why)] if why.startswith("ch") else []):
        tmp = os.path.join(CKDIR, f + ".tmp")
        json.dump(ck, open(tmp, "w"), indent=1)
        os.replace(tmp, os.path.join(CKDIR, f))
    return ck


def checkpoint_from_log(path, leg=None):
    """Rebuild a checkpoint from a run's own log (story_N/log.txt + play.txt): the last leg (or LEG) that reported."""
    out = os.path.join(HERE, "..", "_art", "preview", "bot", "story_%d" % path)
    lines = [ln[ln.find("[RT]"):] for ln in open(os.path.join(out, "log.txt"), errors="replace").read().splitlines()
             if "[RT] BOT " in ln]
    st, fl, kt = {}, {}, {}
    for ln in lines:
        p = ln.split(" ", 4)
        if ln.startswith("[RT] BOT state "):
            q = ln.split()
            st[int(q[3])] = (q[4], float(q[5]), float(q[6]), float(q[7]) if len(q) > 7 else None)
        elif ln.startswith("[RT] BOT flags "):
            fl[int(p[3])] = parse_flags(p[4] if len(p) > 4 else "")
        elif ln.startswith("[RT] BOT kit "):
            kt[int(p[3])] = parse_kit(p[4] if len(p) > 4 else "")
    legs = sorted(k for k in st if k in fl and (leg is None or k <= leg))
    if not legs:
        raise SystemExit("no leg reported in the log")
    n = legs[-1]
    chapter, done, tried, broken = 1, 0, {}, set()
    hist = {}                                                     # leg -> the state before it (a resumed run's
    for ln in open(os.path.join(out, "play.txt"), encoding="utf-8", errors="replace"):   # lines replace the old ones)
        mr = re.search(r"RESUMED at leg (\d+)", ln)
        if mr:
            k = min([j for j in hist if j > int(mr.group(1))] or [None]) if hist else None
            if k is not None:
                chapter, done, tried, broken = hist[k][0], hist[k][1], dict(hist[k][2]), set(hist[k][3])
            hist = {j: v for j, v in hist.items() if j <= int(mr.group(1))}
            continue
        ml = re.match(r"\s*(\d+) M\d+ ", ln)
        if ml:
            if int(ml.group(1)) > n:                              # (past the leg we save: ignore the rest of
                hist.setdefault(int(ml.group(1)), (chapter, done, dict(tried), set(broken)))   # this section)
                continue
            hist[int(ml.group(1))] = (chapter, done, dict(tried), set(broken))
        if hist and max(hist) > n and not ml:
            continue
        m = re.match(r"\s*(\d+) M\d+ .*-> (M\d+) (\S+) \((talk|walk onto|arrival scene)\)", ln)
        if m and int(m.group(1)) < n:
            tried[(m.group(2), m.group(3))] = tried.get((m.group(2), m.group(3)), 0) + 1
        m = re.search(r"CHAPTER (\d+)", ln)
        if m:
            chapter = int(m.group(1))
        if "- complete" in ln:
            done += 1
        m = re.search(r"the exit (M\d+) -> (M\d+) did not", ln)
        if m:
            broken.add((m.group(1), m.group(2)))
    kit = kt.get(n) or {"party": [PARTY0], "money": 0, "items": []}
    return save_checkpoint(path, n, st[n], fl[n], kit, chapter, done, "log", tried, broken)


def resume_args(ck, name, lv=60):
    """Engine arguments that start where the checkpoint stood: map, spot, flags, party, purse, bag."""
    flags = ck["flags"]
    vl = [k if v is True else "%s=%d" % (k, int(v)) for k, v in sorted(flags.items())]
    vl += ["%s=0" % k for k, d in DEF.items() if re.match(r"^G\d+$", k) and d and k not in flags]   # (cleared since)
    vf = os.path.join(TOOL, "tmp", "bot", name + "_resume_vars.txt")
    json.dump(vl or ["G000"], open(vf, "w"))
    y = ck.get("y")
    pos = "[%.2f,%.2f,%.2f,0.0]" % (ck["x"] / 2.0, (y / 2.0 + 0.05) if y is not None else 2.0, ck["z"] / 2.0) \
        if y is not None else pb.start_pos(ck["map"], ck["x"], ck["z"])
    # (the engine passes at most 13 arguments: the rest go packed in -rt, "lv 60;party P132;...")
    pack = ["bot serve,tmp/bot/%s_cmd.txt" % name, "fast", "auto", "lv %s" % lv] + (["tank"] if TANK else [])
    kit = ck.get("kit") or {}
    party = kit.get("party") or [PARTY0]
    if party[0] != PARTY0:
        pack.append("lead " + party[0])
    if len(party) > 1:
        pack.append("party " + ",".join(party[1:]))       # (-rtparty joiners take the lead's level)
    if kit.get("items"):
        pack.append("item " + ",".join(kit["items"]))
    if kit.get("money"):
        pack.append("money %d" % kit["money"])
    if kit.get("equip"):
        pack.append("equip " + ",".join(kit["equip"]))
    return ["-testplay", "-map", ck["map"], pos, "-rtvar", "@tmp/bot/%s_resume_vars.txt" % name,
            "-debuglv", str(lv), "-rt", ";".join(pack)]


# ------------------------------------------------------------------ the loop
def main():
    a = sys.argv[1:]
    opts = {"--lv": "60", "--legs": "400", "--minutes": "90", "--save-from-log": None, "--ckpt": None}
    resume = "--resume" in a
    a = [x for x in a if x not in ("--resume", "--tank")]
    for k in list(opts):
        if k in a:
            i = a.index(k)
            opts[k] = a[i + 1] if i + 1 < len(a) else ""
            a = a[:i] + a[i + 2:]
    path = int(a[0])
    if opts["--save-from-log"] is not None:                       # storyplay.py N --save-from-log [LEG|last]
        lg = opts["--save-from-log"]
        ck = checkpoint_from_log(path, int(lg) if lg.isdigit() else None)
        print("checkpoint leg %d %s %.0f,%.0f chapter %d -> %s" % (ck["leg"], ck["map"], ck["x"], ck["z"],
                                                                   ck["chapter"], CKDIR))
        return
    name = "story_%d" % path
    out = os.path.join(HERE, "..", "_art", "preview", "bot", name)
    os.makedirs(out, exist_ok=True)
    cmdf = os.path.join(TOOL, "tmp", "bot", name + "_cmd.txt")
    os.makedirs(os.path.dirname(cmdf), exist_ok=True)
    flagnames = sorted(k for k in GV if re.match(r"^G\d+$", k))
    ck = None
    if resume:                                                    # --resume [--ckpt FILE]: path_N.json by default
        ckf = opts["--ckpt"] or os.path.join(CKDIR, "path_%d.json" % path)
        if not os.path.isabs(ckf) and not os.path.exists(ckf):
            ckf = os.path.join(CKDIR, ckf)
        ck = json.load(open(ckf))
    shots = os.path.join(TOOL, "tmp", "rt_shot")
    os.makedirs(shots, exist_ok=True)
    battle0 = 0
    for f in os.listdir(shots):
        if f.startswith("bot_%s_" % name):
            mb = re.match(r"bot_%s_battle_(\d+)_" % name, f)
            if resume and mb:
                battle0 = max(battle0, int(mb.group(1)))              # a resumed run numbers its battles on
            elif not resume:
                os.remove(os.path.join(shots, f))

    shot_box = [None]

    def cmd(n, steps, quit_=False):
        tmp = cmdf + ".tmp"
        d = {"n": n, "steps": [s.replace(" ", ",") for s in steps], "flags": flagnames, "quit": quit_,
             "shot": shot_box[0]}
        if battle0:
            d["battle0"] = battle0
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, cmdf)                                     # (never a half-written file)
    cmd(0, [])
    pass                                                                  # (never kill engines this script did not start: the user and other agents run their own)
    log = os.path.join(out, "log_resume.txt" if resume else "log.txt")
    if resume:
        args = [os.path.join(TOOL, "rpgcobo.exe")] + resume_args(ck, name, opts["--lv"])
    else:
        args = [os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-map", "M099", pb.start_pos("M099", *pb.block("M099", 12, 6)), "-rtvar",
                "G000", "-rtfast", "-rtauto", "-debuglv", opts["--lv"],
                "-rt", "bot serve,tmp/bot/%s_cmd.txt;choice %d" % (name, path)]
    lf = open(log, "w")
    proc = subprocess.Popen(args, cwd=TOOL, stdout=lf, stderr=subprocess.STDOUT)
    play = open(os.path.join(out, "play.txt"), "a" if resume else "w", encoding="utf-8")

    def note(s):
        print(s)
        play.write(s + "\n")
        play.flush()
    t0, n, tried, seen_lines = time.time(), 0, {}, 0
    last_flags, what, fails = None, None, {}
    chapter, done, kit, last_ck, rested = 1, 0, None, 0, -9
    send = ["wait 4000"]                                          # the prologue plays first
    shot_next = None
    if resume:
        n = ck["leg"]
        chapter, done, last_ck = ck.get("chapter", 1), ck.get("chapters_done", 0), ck["leg"]
        tried = {(m, k): c for m, k, c in ck.get("tried", [])}
        for b in ck.get("broken", []):
            BROKEN.add(tuple(b))
        note("== %s path, level %s, RESUMED at leg %d (%s %.0f,%.0f, chapter %d) from %s" % (
            PATHS[path], opts["--lv"], n, ck["map"], ck["x"], ck["z"], chapter, ck.get("saved")))
        send = ["wait 3000"]
    else:
        note("== %s path, level %s" % (PATHS[path], opts["--lv"]))
    legs_max = n + int(opts["--legs"])
    while n < legs_max and time.time() - t0 < float(opts["--minutes"]) * 60:
        n += 1
        shot_box[0] = shot_next
        cmd(n, send)
        state = flags = None
        lines = []
        finished = False
        t1 = time.time()
        while time.time() - t1 < 240 and proc.poll() is None:
            time.sleep(0.5)
            lines = [ln[ln.find("[RT]"):] if "[RT]" in ln else ln
                     for ln in open(log, errors="replace").read().splitlines()]
            for ln in lines[seen_lines:]:
                if "[RT] MSG" in ln and ("Objective" in ln or "- complete" in ln or "CHAPTER" in ln):
                    note("   " + ln[ln.find("[RT] MSG") + 9:][:150])
                    mc = re.search(r"CHAPTER (\d+)", ln)
                    if mc:
                        chapter = int(mc.group(1))
                    if "- complete" in ln:
                        done += 1
                        finished = True
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
                y = float(p[7]) if len(p) > 7 else None
                raw = fl[-1].split(" ", 4)[4] if len(fl[-1].split(" ", 4)) > 4 else ""
                flags = parse_flags(raw)
                kl = [l for l in lines if l.startswith("[RT] BOT kit %d " % n)]
                if kl:
                    kit = parse_kit(kl[-1].split(" ", 4)[4] if len(kl[-1].split(" ", 4)) > 4 else "")
                break
        if state is None:
            wiped = any("ARRIVE M000" in l for l in lines[-60:]) if lines else False
            note("!! %s after leg %d" % ("PARTY WIPED (game over, back at the title)" if wiped else
                                        "no answer from the game (crashed or hung)", n))
            break
        if "M100" <= state[0] < "M800" and (finished or n - last_ck >= 40):
            why = "ch%d_done%d" % (chapter, done) if finished else "leg"
            save_checkpoint(path, n, state + (y,), flags, kit or {"party": [PARTY0], "money": 0, "items": []},
                            chapter, done, why, tried, BROKEN)
            last_ck = n
            note("   [checkpoint leg %d: %s]" % (n, why))
        moved = flags != last_flags                                      # (a story scene moved us: not a door)
        if what and len(what) > 3 and state[0] not in what[3] and not ("M800" <= state[0] < "M900") and not moved:
            note("   ?? went %s -> %s but landed in %s" % (what[3][0], what[3][1], state[0]))   # (walked into a
            fails[what[3]] = fails.get(what[3], 0) + 1                                         # door on the way)
            if fails[what[3]] >= 3:
                BROKEN.add(what[3])
                note("!! BUG? the way %s -> %s keeps landing in %s; routing around it" % (what[3] + (state[0],)))
        if what and len(what) > 3 and state[0] == what[3][0]:          # a "go" leg that left us where we were
            fails[what[3]] = fails.get(what[3], 0) + 1
            if fails[what[3]] >= 3:
                BROKEN.add(what[3])
                note("!! BUG? the exit %s -> %s did not take the player there (twice); routing around it" % what[3])
        if what and what[2] in ("talk", "walk onto", "arrival scene"):     # did the last try move the story?
            newly = [k for k, v in (flags or {}).items() if v is True and (last_flags or {}).get(k) is not True]
            if newly:
                note("   + " + ",".join(sorted(newly)))
            if newly:                                             # something moved: walk-ons that pushed us back
                for (tm_, tk_) in list(tried):                    # (a rope point, a gate) get another go
                    ev_ = (MP.get(tm_, {}).get("event") or {}).get(tk_.split("@")[0]) or {}
                    pg_ = ev_.get("page") or []
                    pi_ = int(tk_.split("@")[1]) if "@" in tk_ else 0
                    if pi_ < len(pg_) and pg_[pi_].get("trigger") == 5 and tried[(tm_, tk_)] < 9:
                        del tried[(tm_, tk_)]
            for k in newly:
                FLIPS[k] = FLIPS.get(k, 0) + 1
                if FLIPS[k] == 3:
                    TOGGLES.add(k)
                    note("   (%s keeps flipping: a switch, not the story)" % k)
            tried[(what[0], what[1])] = tried.get((what[0], what[1]), 0) + 1   # every page gets two tries
        last_flags = flags
        what = steps = None
        if kit and kit.get("hurt") and rested != n - 1:              # (once in a row: a menu answer may be "Leave")
            what, steps = rest_plan(state, flags)
            if what:
                rested = n
        if what is None:
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
        passing = what[2].startswith("go ") or what[2].startswith("rest")   # (a menu met on the way: the first answer;
        send = ["pin %d" % (0 if passing else -1)] + steps                # rotate at a target)
        shot_next = "%s_%03d" % (name, n + 1)                             # (taken once the scene is over)
    if state and flags is not None and "M100" <= state[0] < "M800":
        save_checkpoint(path, n, state + (y,), flags, kit or {"party": [PARTY0], "money": 0, "items": []},
                        chapter, done, "end", tried, BROKEN)
        note("   [checkpoint leg %d: end]" % n)
    cmd(n + 1, [], True)
    time.sleep(2)
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    lf.close()
    if resume:                                                    # (battlesheet reads log.txt for the enemy names)
        with open(os.path.join(out, "log.txt"), "a") as f:
            f.write("\n==== RESUMED RUN from leg %d ====\n" % ck["leg"])
            f.write(open(log, errors="replace").read())
    pb.convert_shots(name, out)
    note("== %d legs, %.0f min" % (n, (time.time() - t0) / 60))


if __name__ == "__main__":
    main()
