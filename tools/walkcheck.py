"""Walkability check (user: "can't get out of this room... take a full run through on props"): for every field map,
rebuild it in memory (gen_maps.make, no engine), work out where the player can stand, and report exits, NPCs, chests
and triggers that can't be reached from the map's arrival points. Approximate: a column's floor is its highest solid
block with 3 free blocks above (gen_maps fill() walls and VOID-carved doorways applied in order); water and every
standing object (trees, lamps, furniture, NPCs, props, chests) block their cell; neighbours connect when the floors
differ by at most STEP (2: the X jump). Seeds: the map's touch triggers and portals at its edges, its scene spots, and
the arrival spot of every go()/portal pointing here from another map.
python -E tools/walkcheck.py [MAP ...]   (default: all field maps)"""
import os
import sys
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402

STEP, CLEAR = 2, 3
WATERISH = (8,)                     # block type 8: water / tar / lava (gen_maps WATER, TAR, LAVA, BOG)
PLANT = (11,)                       # flowers and tufts: decoration, walkable


def floors(m):
    """Per column: the standing height (top solid + 1) or -1 if nothing to stand on; and a blocked mask."""
    d, w = m.d, m.w
    H = 64
    solid = np.zeros((d, w, H), bool)
    for z in range(d):
        for x in range(w):
            solid[z, x, :max(0, int(m.hgt[z, x])) + 1] = True
    water = (m.blk & 31) == 8
    for o in m.objs:
        if o["t"] == "fill":
            x0, z0, y0 = o["x"], o["z"], o["y"]
            xs, zs = slice(max(0, x0), max(0, min(w, x0 + o["w"]))), slice(max(0, z0), max(0, min(d, z0 + o["d"])))
            ys = slice(max(0, y0), max(0, min(H, y0 + o["h"])))
            solid[zs, xs, ys] = (o["blk"] != gm.VOID)
            if (o["blk"] & 31) == 8:
                water[zs, xs] = True
        elif o["t"] == "blk" and (o["blk"] & 31) not in PLANT and 0 <= o["z"] < d and 0 <= o["x"] < w:
            if 0 <= o["y"] < H:
                solid[o["z"], o["x"], o["y"]] = True
    fl = np.full((d, w), -1, np.int32)
    for z in range(d):
        for x in range(w):
            col = solid[z, x]
            for y in range(H - CLEAR - 1, -1, -1):
                if col[y] and not col[y + 1:y + 1 + CLEAR].any():
                    fl[z, x] = y + 1
                    break
    blocked = water | (m.blk == 0)                         # (embedded rooms: the empty map around the room)
    for x, z in m.walls:                                   # invisible walls (block furniture, gen_maps furnish)
        if 0 <= z < d and 0 <= x < w:
            blocked[z, x] = True
    for o in m.objs:
        if o["t"] == "fb":
            x, z = o["x"], o["z"]
            if o["fbtype"] == 2 and o["fbparam"] == 7:            # the hearth: about 3 x 2 around its anchor
                cells = [(x + i, z + j) for i in (-2, -1, 0, 1) for j in (-1, 0, 1)]   # (the model spills forward)
            elif o["fbtype"] == 4 and o["fbparam"] in (5, 7, 8, 9, 10, 11):   # bench, table, chests, shelf, counter
                cells = [(x, z), (x + 1, z)]
            else:
                cells = [(x, z)]
            for cx, cz in cells:
                if 0 <= cz < d and 0 <= cx < w:
                    blocked[cz, cx] = True
        if o["t"] == "asset" and 0 <= o["z"] < d and 0 <= o["x"] < w:
            blocked[o["z"], o["x"]] = True
    return fl, blocked


def cell(pos):
    return int(round(pos[0])), int(round(pos[2]))


def check(mid, arrivals):
    m, ev = gm.make(mid)
    if ev is None:
        return None
    fl, blocked = floors(m)
    d, w = m.d, m.w
    targets, seeds = [], []
    for key, e in ev.ev.items():
        if "pos" not in e or e.get("role") == "light":
            continue
        x, z = cell(e["pos"])
        if not (0 <= x < w and 0 <= z < d):
            continue
        role, mdl = e.get("role"), e.get("mdlid", "")
        if "G293" in str(e.get("reqs0")):                  # hireling NPCs: parked until hired (moved at run time)
            continue
        if e.get("memo") == "barricade":                   # a closed road's barricade: it is SUPPOSED to block
            continue
        pages = e.get("page") or []
        trig = pages[0].get("trigger") if pages else None
        solid_ev = role in ("villager", "clerk", "hotel", "itemchest") or (role == "custom" and mdl not in ("", "CE000"))
        if solid_ev:
            blocked[z, x] = True
        if role in ("portal",) or (role == "custom" and trig in (5, 6)) or (pages and pages[0].get("memo") == "landing"):
            seeds.append((x, z))                             # (a landing: where another map's portal puts you)
        if role == "custom" and trig == 6:
            continue                                         # autorun scenes: not a place to reach
        name = e.get("name", key)
        targets.append((name, role, x, z, solid_ev))
    for x, z in arrivals.get(mid, []):
        if 0 <= x < w and 0 <= z < d:
            seeds.append((x, z))
    if WIDE:
        # (user 2026-11-14: "at least one full block to walk through to get to every object in the caves") the body
        # needs a 2 x 2 cell square (1 m): a cell is passable only as the corner of a clear, level-enough square
        ok = ~blocked & (fl >= 0)
        sq = ok.copy()
        sq[:-1, :] &= ok[1:, :]
        sq[:, :-1] &= ok[:, 1:]
        sq[:-1, :-1] &= ok[1:, 1:]
        sq[-1, :] = False
        sq[:, -1] = False
        f = fl.astype(int)
        span = np.maximum.reduce([f, np.roll(f, -1, 0), np.roll(f, -1, 1), np.roll(np.roll(f, -1, 0), -1, 1)]) - \
            np.minimum.reduce([f, np.roll(f, -1, 0), np.roll(f, -1, 1), np.roll(np.roll(f, -1, 0), -1, 1)])
        sq &= span <= STEP
        blocked = ~sq
        seeds = [(x + dx, z + dz) for x, z in seeds for dx in (-1, 0) for dz in (-1, 0)]
    seen = np.zeros((d, w), bool)
    q = deque()
    for x, z in seeds:
        if fl[z, x] >= 0 and not seen[z, x] and not blocked[z, x]:
            seen[z, x] = True
            q.append((x, z))
    while q:
        x, z = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if 0 <= nx < w and 0 <= nz < d and not seen[nz, nx] and not blocked[nz, nx] and fl[nz, nx] >= 0 \
                    and abs(int(fl[nz, nx]) - int(fl[z, x])) <= STEP:
                seen[nz, nx] = True
                q.append((nx, nz))
    bad = []
    for name, role, x, z, solid_ev in targets:
        # reach: an event's hit box is about 1 m (2 blocks) around it, so it can be checked from 2 cells away
        ok = any(0 <= x + dx < w and 0 <= z + dz < d and seen[z + dz, x + dx]
                 for dx in range(-2, 3) for dz in range(-2, 3))
        if not ok:
            bad.append((name, role, x, z))
    return bad, int(seen.sum())


def widen(m, ev):
    """(user 2026-11-14) Caves: every object gets a way to it at least a full body (2 x 2 cells) wide. For each event the
    wide flood misses, the shortest single-cell way out to the wide-reachable floor is widened: the cells beside it
    are cut down to its floor (wall feet, rims) and rubble on them is removed. Returns the number of cells cut."""
    fl, blocked = floors(m)
    d, w = m.d, m.w
    solid_ev, seeds, targets, at = set(), [], [], {}
    for e in ev.ev.values():
        if "pos" not in e or e.get("role") == "light" or e.get("memo") == "barricade":
            continue
        x, z = cell(e["pos"])
        if not (0 <= x < w and 0 <= z < d):
            continue
        role, mdl = e.get("role"), e.get("mdlid", "")
        pages = e.get("page") or []
        trig = pages[0].get("trigger") if pages else None
        if role in ("villager", "clerk", "hotel", "itemchest") or (role == "custom" and mdl not in ("", "CE000")):
            solid_ev.add((x, z))
            at.setdefault((x, z), []).append(e)
        if role == "portal" or (role == "custom" and trig in (5, 6)) or (pages and pages[0].get("memo") == "landing"):
            seeds.append((x, z))
        if not (role == "custom" and trig == 6):
            targets.append((x, z))
    nb = blocked.copy()
    for x, z in solid_ev:
        nb[z, x] = True
    solid_ev_cells = set(solid_ev)
    for x, z in solid_ev:
        nb[z, x] = True
    cut = 0
    for _round in range(3):
        ok = ~nb & (fl >= 0)
        sq = ok.copy()
        sq[:-1, :] &= ok[1:, :]
        sq[:, :-1] &= ok[:, 1:]
        sq[:-1, :-1] &= ok[1:, 1:]
        sq[-1, :] = False
        sq[:, -1] = False
        seen = np.zeros((d, w), bool)
        q = deque()
        for sx, sz in seeds:
            for x, z in ((sx + a, sz + b) for a in (-1, 0) for b in (-1, 0)):
                if 0 <= x < w and 0 <= z < d and sq[z, x] and not seen[z, x]:
                    seen[z, x] = True
                    q.append((x, z))
        while q:
            x, z = q.popleft()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if 0 <= nx < w and 0 <= nz < d and not seen[nz, nx] and sq[nz, nx]:
                    hs = [int(fl[nz + b, nx + a]) for a in (0, 1) for b in (0, 1)]
                    if max(hs) - min(hs) <= STEP and abs(int(fl[nz, nx]) - int(fl[z, x])) <= STEP:
                        seen[nz, nx] = True
                        q.append((nx, nz))
        near = seen.copy()                                 # the body's square reaches one cell further
        near[1:, :] |= seen[:-1, :]
        near[:, 1:] |= seen[:, :-1]
        near[1:, 1:] |= seen[:-1, :-1]
        missing = [(x, z) for x, z in targets
                   if not any(0 <= x + a < w and 0 <= z + b < d and near[z + b, x + a]
                              for a in range(-2, 3) for b in range(-2, 3))]
        if not missing:
            break
        for tx, tz in missing:                             # single-cell BFS from the object to the wide floor
            prev = {}
            q = deque()
            for a in range(-2, 3):
                for b in range(-2, 3):
                    x, z = tx + a, tz + b
                    if 0 <= x < w and 0 <= z < d and not nb[z, x] and fl[z, x] >= 0 and (x, z) not in prev:
                        prev[(x, z)] = None
                        q.append((x, z))
            end = None
            while q:
                x, z = q.popleft()
                if near[z, x]:
                    end = (x, z)
                    break
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, nz = x + dx, z + dz
                    if 0 <= nx < w and 0 <= nz < d and (nx, nz) not in prev and fl[nz, nx] >= 0 \
                            and (not nb[nz, nx] or ((nx, nz) in solid_ev and not blocked[nz, nx])) \
                            and abs(int(fl[nz, nx]) - int(fl[z, x])) <= STEP:
                        prev[(nx, nz)] = (x, z)
                        q.append((nx, nz))
            if end is None:
                continue
            path, c = [], end
            while c is not None:
                path.append(c)
                c = prev[c]
            onpath = set(path) | {(x + a, z + b) for x, z in path for a in (0, 1) for b in (0, 1)}
            for x, z in list(path):                        # a chest or prop in the only gap steps aside
                if (x, z) not in solid_ev or (x, z) == (tx, tz):
                    continue
                spot = next(((x + a, z + b) for r in (1, 2, 3) for a in range(-r, r + 1) for b in range(-r, r + 1)
                             if 0 <= x + a < w and 0 <= z + b < d and (x + a, z + b) not in onpath
                             and not nb[z + b, x + a] and fl[z + b, x + a] == fl[z, x]), None)
                if spot is None:
                    continue
                for e in at.pop((x, z), []):
                    e["pos"][0] += spot[0] - x
                    e["pos"][2] += spot[1] - z
                    at.setdefault(spot, []).append(e)
                solid_ev.discard((x, z))
                solid_ev.add(spot)
                nb[z, x] = False
                nb[spot[1], spot[0]] = True
            kill = set()
            for x, z in path:                              # make each path cell the corner of a clear square
                h = int(m.hgt[z, x])
                for a in (0, 1):
                    for b in (0, 1):
                        px, pz = x + a, z + b
                        if not (0 <= px < w and 0 <= pz < d) or (px, pz) in solid_ev or (int(m.blk[pz, px]) & 31) == 8:
                            continue
                        if int(m.hgt[pz, px]) > h:
                            m.hgt[pz, px] = h
                            m.blk[pz, px] = m.blk[z, x]
                            fl[pz, px] = fl[z, x]
                            cut += 1
                        if nb[pz, px] and blocked[pz, px]:
                            kill.add((px, pz))
                            nb[pz, px] = False
            if kill:
                m.objs = [o for o in m.objs if not (o["t"] == "fb" and o.get("fbtype") == 20 and (o["x"], o["z"]) in kill)]
    return cut


def arrival_points():
    """go() destinations by map (world coords -> block cells), from every map's events."""
    out = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("cmd") == "cmd_mapmove":
                dst = o["dest"]
                if "pos" in dst and dst["pos"]:
                    p = dst["pos"]
                    out.setdefault(dst["mapid"], []).append((int(p[0] * 2), int(p[2] * 2)))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for mid in gm.MAPS:
        if mid >= "M800" and mid < "M900":
            continue
        try:
            _m, ev = gm.make(mid)
        except Exception:
            continue
        if ev:
            walk(ev.ev)
    return out


WIDE = "--wide" in sys.argv
if WIDE:
    sys.argv.remove("--wide")
if "--caves" in sys.argv:                                 # every cave map (gen_maps CAVE_MAPS, filled while building)
    sys.argv.remove("--caves")
    for _k in [k for k in gm.MAPS if "M100" <= k < "M800" and k not in gm.DEBUG_MAPS]:
        try:
            gm.make(_k)
        except Exception:
            pass
    sys.argv += sorted(gm.CAVE_MAPS)


def main():
    ids = sys.argv[1:] or [k for k in gm.MAPS if not ("M800" <= k < "M900") and k not in gm.DEBUG_MAPS]
    arr = arrival_points()
    n = 0
    for mid in sorted(ids):
        try:
            r = check(mid, arr)
        except Exception as ex:
            print("%s ERROR %s" % (mid, ex))
            continue
        if not r:
            continue
        bad, area = r
        if bad:
            n += 1
            print("%s (%s cells reachable)" % (mid, area))
            for b in bad:
                print("   unreachable: %s %s at %d,%d" % b)
    print("maps with unreachable things:", n)


if __name__ == "__main__":
    main()
