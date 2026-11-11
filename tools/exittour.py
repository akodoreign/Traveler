"""Walk into every exit in the game, like a player (user, 2026-11-10: "approach it like a player"). The world is set to
its end state (every true/false story flag true: no scene hijacks the walk, roads are open). For each exit the test
player warps to a walkable spot a few steps from it, walks into it, waits for the next map, and takes a screenshot.
Checks: the exit fires, it leads to the map it should, and the screen after arriving is not black.
python -E tools/exittour.py [MAP ...] [--batch 10]      (default: every field map)
Report: _art/preview/bot/tour_report.txt; screenshots _art/preview/bot/tour_*/."""
import json
import os
import re
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402
import playbot as pb  # noqa: E402
import walkcheck as wc  # noqa: E402

OUT = os.path.join(HERE, "..", "_art", "preview", "bot")


def end_state_vars():
    gv = json.load(open(os.path.join(gm.PROJ, "data", "gvar.json"), encoding="utf-8"))
    return [k for k, v in gv.items() if isinstance(v, dict) and v.get("type") == 1]


def open_in_end_state(reqs, numeric):
    for r in reqs or []:
        lv, op, rv = r.get("lvar"), r.get("op"), r.get("rvar")
        if not (isinstance(lv, str) and re.match(r"^G\d+$", lv)) or lv in numeric:
            continue
        if (op == "==" and rv is False) or (op == "!=" and rv is True):
            return False
    return True


def footprint(e, w, d):
    """The cells an event's trigger box covers (r = [ox, oy, oz, half-length m, half-height m, half-depth m]; the
    long side runs along x for d 0/2, along z for d 1/3)."""
    x, z = wc.cell(e["pos"])
    r = (e.get("mdl") or {}).get("r") or [0, 1.0, 0, 1.0, 1.0, 1.0]
    half = max(0, int(round(float(r[3]) * 2)) - 1)
    along_x = e["pos"][3] in (0, 2)
    out = set()
    for a in range(-half, half + 1):
        nx, nz = (x + a, z) if along_x else (x, z + a)
        if 0 <= nx < w and 0 <= nz < d:
            out.add((nx, nz))
    return out


def reach_map(m, ev):
    fl, blocked = wc.floors(m)
    d, w = m.d, m.w
    for o in m.objs:                                                      # a tree's canopy and the gaps between
        if o["t"] == "fb" and o["fbtype"] == 20 and o["fbparam"] in (gm.TREE_L, gm.TREE_M):   # (not rocks: they line
                                                                          # cave tunnels) trunks: too tight, so routes
            x, z = o["x"], o["z"]                                         # keep a cell clear of every tree (the
            blocked[max(0, z - 1):z + 2, max(0, x - 1):x + 2] = True      # bot walked into M101's padding forest)
    seeds, strips = [], []
    for e in ev.ev.values():
        if "pos" in e and (e.get("role") == "portal" or e.get("page")) and e.get("role") != "villager":
            x, z = wc.cell(e["pos"])
            fp = footprint(e, w, d)
            if 0 <= x < w and 0 <= z < d and len(fp) <= 9:                 # (not an edge strip: its middle
                seeds.append((x, z, e["pos"][1]))                             # is often a cliff top)
            else:
                strips.append((fp, e["pos"][1]))
        if e.get("role") in ("villager", "clerk", "hotel", "itemchest") and "pos" in e:
            x, z = wc.cell(e["pos"])
            if 0 <= x < w and 0 <= z < d:
                blocked[z, x] = True
    if not seeds:                                                         # only edge strips (the shifting waste):
        seeds = [(x, z, y) for fp, y in strips for x, z in fp              # their cells at the strip's own height
                 if 0 <= x < w and 0 <= z < d and fl[z, x] >= 0 and abs(int(fl[z, x]) - y) <= wc.STEP]
    seen = np.zeros((d, w), bool)
    q = deque()
    for x, z, y in seeds:                                                # (at the event's height: not the cliff
        for dx in range(-3, 4):                                           # top beside an exit)
            for dz in range(-3, 4):
                nx, nz = x + dx, z + dz
                if 0 <= nx < w and 0 <= nz < d and fl[nz, nx] >= 0 and not blocked[nz, nx] and not seen[nz, nx] \
                        and (not isinstance(y, (int, float)) or abs(int(fl[nz, nx]) - y) <= wc.STEP + 1):
                    seen[nz, nx] = True
                    q.append((nx, nz))
    while q:
        x, z = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if 0 <= nx < w and 0 <= nz < d and not seen[nz, nx] and not blocked[nz, nx] and fl[nz, nx] >= 0 \
                    and abs(int(fl[nz, nx]) - int(fl[z, x])) <= wc.STEP:
                seen[nz, nx] = True
                q.append((nx, nz))
    return seen, blocked, fl


def nbrs(x, z, seen, fl):
    d, w = seen.shape
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, nz = x + dx, z + dz
        if 0 <= nx < w and 0 <= nz < d and seen[nz, nx] and abs(int(fl[nz, nx]) - int(fl[z, x])) <= wc.STEP:
            yield nx, nz


def main_area(seen, fl, exits=None):
    """The connected walkable area a player who arrived normally walks on: the one that touches the most exits (the
    largest is often a ridge or a roof nobody stands on), or the largest when no exits are given."""
    lab = np.zeros(seen.shape, np.int32)
    sizes = {}
    n = 0
    for z0, x0 in zip(*np.nonzero(seen)):
        if lab[z0, x0]:
            continue
        n += 1
        lab[z0, x0] = n
        q, size = deque([(x0, z0)]), 0
        while q:
            x, z = q.popleft()
            size += 1
            for nx, nz in nbrs(x, z, seen, fl):
                if not lab[nz, nx]:
                    lab[nz, nx] = n
                    q.append((nx, nz))
        sizes[n] = size
    if not sizes:
        return lab > 0
    votes = {k: 0 for k in sizes}
    for fp in exits or []:                                                # each exit's box: the areas under it
        for r in range(4):                                                # (or the nearest, a step away)
            ks = {int(lab[z + dz, x + dx]) for x, z in fp for dx in range(-r, r + 1) for dz in range(-r, r + 1)
                  if 0 <= z + dz < lab.shape[0] and 0 <= x + dx < lab.shape[1] and lab[z + dz, x + dx]}
            if ks:
                for k in ks:
                    votes[k] += 1
                break
    best = max(sizes, key=lambda k: (votes[k], sizes[k]))
    return lab == best


def path(seen, fl, start, goal_cells):
    prev = {start: None}
    q = deque([start])
    while q:
        c = q.popleft()
        if c in goal_cells:
            out = []
            while c:
                out.append(c)
                c = prev[c]
            return out[::-1]
        for nb in nbrs(c[0], c[1], seen, fl):
            if nb not in prev:
                prev[nb] = c
                q.append(nb)
    return None


def exits_of(mid, numeric):
    m, ev = gm.make(mid)
    if ev is None:
        return []
    seen, blocked, fl = reach_map(m, ev)
    trig_cells = []
    out = []
    for key, e in ev.ev.items():
        if "pos" not in e or e.get("memo") == "barricade":
            continue
        dest = None
        if e.get("role") == "portal" and e.get("dest"):
            dest = e["dest"]["mapid"]
            reqs = e.get("reqs0")
        else:
            for pg in e.get("page") or []:
                if pg.get("trigger") == 5 and "cmd_mapmove" in json.dumps(pg.get("cmdblock")):
                    found = re.findall(r'"mapid": "(M\d+)"', json.dumps(pg.get("cmdblock")))
                    if found and open_in_end_state(pg.get("reqs"), numeric):
                        dest, reqs = found[0], e.get("reqs0")
        if not dest or dest == mid:
            continue
        x, z = wc.cell(e["pos"])
        fp = footprint(e, m.w, m.d) or {(x, z)}
        trig_cells.append(fp)
        push = {0: "up", 1: "right", 2: "down", 3: "left"}.get(e["pos"][3]) if e.get("role") == "portal" else None
        out.append([key, dest, x, z, open_in_end_state(reqs, numeric), push, fp])
    main = main_area(seen, fl, trig_cells)
    near_trig = np.zeros(seen.shape, bool)                               # start spots keep 4 steps from any box
    for fp in trig_cells:
        for a, b in fp:
            near_trig[max(0, b - 3):b + 4, max(0, a - 3):a + 4] = True
    res = []
    for key, dest, x, z, isopen, push, fp in out:
        fp = {(a, b) for a, b in fp if m.blk[b, a] == gm.ROAD} or fp      # a player follows the road out
        goal = {(a + dx, b + dz) for a, b in fp for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                if 0 <= a + dx < m.w and 0 <= b + dz < m.d and seen[b + dz, a + dx]}
        on = [c for c in fp if main[c[1], c[0]]] or [c for c in goal if main[c[1], c[0]]]
        ax, az = min(on, key=lambda c: abs(c[0] - x) + abs(c[1] - z)) if on else (x, z)
        cands = []
        for dx in range(-12, 13):
            for dz in range(-12, 13):
                nx, nz = ax + dx, az + dz
                dd = abs(dx) + abs(dz)
                if not (4 <= dd <= 12) or not (5 <= nx < m.w - 5 and 5 <= nz < m.d - 5) or not main[nz, nx]:
                    continue                                       # (not on an edge strip: it would fire)
                if near_trig[nz, nx]:
                    continue
                cands.append((abs(dd - 6), nx, nz))
        route = None
        for _c, nx, nz in sorted(cands)[:6]:
            route = path(seen, fl, (nx, nz), goal)
            if route:
                break
        if route:
            x, z = route[-1]                                             # walk to where the route meets the box
        if route and not push:                                           # walk-on trigger: push on along the route
            lx, lz = route[-2] if len(route) > 1 else route[0]
            dx, dz = x - lx, z - lz
            push = ("right" if dx > 0 else "left") if abs(dx) >= abs(dz) and dx else ("up" if dz > 0 else "down")
        res.append((key, dest, x, z, isopen, route, push))
    return res


def legs(mid, ex, name):
    key, dest, x, z, isopen, route, push = ex
    sx, sz = route[0]
    out = ["warp %s %d %d" % (mid, sx, sz), "pos"]
    for cx, cz in route[3::3] + [route[-1]]:                             # waypoints along the computed path
        out.append("goto %.1f %.1f 4000" % (cx + 0.5, cz + 0.5))
    out += ["goto %.1f %.1f 5000" % (x + 0.5, z + 0.5), "hold %s 900" % push, "untilmap %s 5000" % dest, "wait 1300",
            "shot %s_%s_%s" % (name, mid, key.strip("#")), "pos"]
    return out


def dark(path):
    try:
        a = np.asarray(Image.open(path).convert("L"), np.float32)
        return float(a[:600].mean())
    except OSError:
        return -1.0


def main():
    a = sys.argv[1:]
    batch = 10
    if "--batch" in a:
        i = a.index("--batch")
        batch = int(a[i + 1])
        a = a[:i] + a[i + 2:]
    ids = a or [k for k in gm.MAPS if "M100" <= k < "M800" and k not in gm.DEBUG_MAPS]
    gv = json.load(open(os.path.join(gm.PROJ, "data", "gvar.json"), encoding="utf-8"))
    numeric = {k for k, v in gv.items() if isinstance(v, dict) and v.get("type") == 2}
    allvars = ",".join(end_state_vars())
    todo = []
    report = []
    for mid in ids:
        try:
            for ex in exits_of(mid, numeric):
                if not ex[4]:
                    report.append("SKIP %s %s -> %s: closed in the end state" % (mid, ex[0], ex[1]))
                elif not ex[5]:
                    report.append("BAD  %s %s -> %s: no walking route from the map's main area to the exit at %d,%d"
                                  % (mid, ex[0], ex[1], ex[2], ex[3]))
                else:
                    todo.append((mid, ex))
        except Exception as e:  # noqa: BLE001
            report.append("ERR  %s: %s" % (mid, e))
    print("%d exits to walk, %d skipped/bad" % (len(todo), len(report)))
    for b0 in range(0, len(todo), batch):
        chunk = todo[b0:b0 + batch]
        name = "tour_%03d" % (b0 // batch)
        lines = []
        for mid, ex in chunk:
            lines += legs(mid, ex, name)
        mid0, ex0 = chunk[0]
        kept, to = pb.launch(name, mid0, ex0[5][0][0], ex0[5][0][1], lines, allvars, lv="60",
                             secs=40 + 30 * len(chunk), quiet=True)
        segs, cur = [], None                                  # one segment per leg, from its "warped" line on
        for ln in kept:
            if "BOT warped" in ln:
                cur = []
                segs.append(cur)
            elif cur is not None:
                cur.append(ln)
        for n, (mid, ex) in enumerate(chunk):
            key, dest = ex[0], ex[1]
            shot = os.path.join(OUT, name, "%s_%s_%s.png" % (name, mid, key.strip("#")))
            seg = "\n".join(segs[n]) if n < len(segs) else ""
            ok = ("goto ended: map %s" % dest) in seg or ("MAP %s" % dest) in seg
            lum = dark(shot) if os.path.exists(shot) else -1
            status = "OK  " if ok and lum > 25 else "DARK" if ok and 0 <= lum <= 25 else "FAIL"
            report.append("%s %s %s -> %s  (lum %.0f) %s" % (status, mid, key, dest, lum,
                                                            "" if ok else "[exit did not take the player there]"))
        print(name, "done", "TIMED OUT" if to else "")
        open(os.path.join(OUT, "tour_report.txt"), "w").write("\n".join(report) + "\n")
    bad = [r for r in report if not r.startswith(("OK", "SKIP"))]
    print("%d OK, %d skipped, %d problems -> %s" % (sum(r.startswith("OK") for r in report),
                                                    sum(r.startswith("SKIP") for r in report), len(bad),
                                                    os.path.join(OUT, "tour_report.txt")))
    for r in bad[:60]:
        print("  ", r)


if __name__ == "__main__":
    main()
