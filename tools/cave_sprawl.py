"""Bigger, sprawling caves (user, 2026-11-08): new galleries and looping tunnels carved into the solid rock of a finished cave map.
Called from gen_maps.make() after the hand-placed rooms and events exist.

The story route must not change: everything new is one cluster of rooms hanging off a single spot already on the player's
route. It may have several tunnels back to that spot and loops inside itself, but it never touches another room, so it can't
walk around a scene trigger, a boss or a sealed wall. Sealed areas (not reachable from the map's portals) are kept clear.
New galleries hold a few chests, and a rest-and-save shrine when the map has none."""
import collections
import re

import numpy as np

CAVE_NAME = re.compile(r"\bcave|tunnel|catacomb|cellar|under the|\bcove\b|lava tube|\bmines?\b|\bden\b", re.I)
LOOT = [("I445", 2), ("I447", 2), ("I100", 3), ("I446", 1), ("I448", 1), ("I101", 2), ("N000", 120), ("N000", 200)]


def wanted(name):
    return bool(CAVE_NAME.search(name))


def grow_size(w, d, rooms, links):
    """A cave grows toward a side with no exit on it: east if it can, else south. Hand-placed coordinates stay valid."""
    east = any(max(l[0], l[2]) >= w - 3 for l in links) or any(r[0] + r[2] >= w - 2 for r in rooms)
    south = any(max(l[1], l[3]) >= d - 3 for l in links) or any(r[1] + r[3] >= d - 2 for r in rooms)
    if not east:
        return int(w * 1.6), d
    if not south:
        return w, int(d * 1.5)
    return w, d


def dilate(a, k):
    out = a.copy()
    for _ in range(k):
        n = out.copy()
        n[1:, :] |= out[:-1, :]
        n[:-1, :] |= out[1:, :]
        n[:, 1:] |= out[:, :-1]
        n[:, :-1] |= out[:, 1:]
        out = n
    return out


def flood(open_, seeds):
    d, w = open_.shape
    seen = np.zeros(open_.shape, bool)
    dist = {}
    q = collections.deque()
    for x, z in seeds:
        if 0 <= x < w and 0 <= z < d and open_[z, x] and not seen[z, x]:
            seen[z, x] = True
            dist[(x, z)] = 0
            q.append((x, z))
    while q:
        x, z = q.popleft()
        for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if 0 <= nx < w and 0 <= nz < d and open_[nz, nx] and not seen[nz, nx]:
                seen[nz, nx] = True
                dist[(nx, nz)] = dist[(x, z)] + 1
                q.append((nx, nz))
    return seen, dist


def disc_path(shape, pts, width):
    d, w = shape
    mask = np.zeros(shape, bool)
    zz, xx = np.mgrid[0:d, 0:w]
    r2 = (width / 2.0) ** 2
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        n = int(max(abs(x1 - x0), abs(z1 - z0))) * 2 + 2
        for t in np.linspace(0, 1, n):
            px, pz = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            x_a, x_b, z_a, z_b = max(0, int(px) - 3), min(w, int(px) + 4), max(0, int(pz) - 3), min(d, int(pz) + 4)
            sub = (xx[z_a:z_b, x_a:x_b] - px) ** 2 + (zz[z_a:z_b, x_a:x_b] - pz) ** 2 <= r2
            mask[z_a:z_b, x_a:x_b] |= sub
    return mask


def candidates(m, ev):
    """Direct tunnels between two rooms that hold no event: these can be walled off and rerouted through the new galleries."""
    spots = np.zeros((m.d, m.w), bool)
    for e in ev.ev.values():
        if "pos" in e and 0 <= int(e["pos"][2]) < m.d and 0 <= int(e["pos"][0]) < m.w:
            spots[int(e["pos"][2]), int(e["pos"][0])] = True
    spots = dilate(spots, 3)
    rooms_all = np.zeros((m.d, m.w), bool)
    for r in m.cave_rooms:
        rooms_all |= r
    out = []
    for a, b, lm in m.cave_links:
        ends = [next((i for i, r in enumerate(m.cave_rooms) if 0 <= int(p[1]) < m.d and 0 <= int(p[0]) < m.w and r[int(p[1]), int(p[0])]), None)
                for p in (a, b)]
        cut = lm & ~rooms_all
        if None in ends or ends[0] == ends[1] or cut.sum() < 8 or (cut & spots).any():
            continue
        out.append((cut, ends[0], ends[1]))
    return out


def sprawl(m, ev, mid, rocks, save_shrine):
    """Reroute the main path through new galleries where a tunnel allows it (user: main routes can sit at the end of long
    corridors); otherwise the galleries are a side branch. Returns the number of rooms added."""
    if ev is None or not hasattr(m, "cave_floor"):
        return 0
    cands = candidates(m, ev)
    np.random.default_rng(int(mid[1:])).shuffle(cands)
    for k, c in enumerate(cands[:6]):
        n = _build(m, ev, mid, rocks, save_shrine, c, k)
        if n:
            return n
    return _build(m, ev, mid, rocks, save_shrine, None, 9)


def _build(m, ev, mid, rocks, save_shrine, link, attempt):
    rng = np.random.default_rng(int(mid[1:]) * 7 + 11 + attempt)
    d, w = m.d, m.w
    floor_open = m.hgt <= 3                                              # floors and pools; rims and rock stand higher
    walk = (m.hgt == 2)
    cut = None
    for o in m.objs:
        if o["t"] == "fill" and o.get("blk") is not None and o["h"] > 1:   # a filled block in the way stays in the way
            walk[max(0, o["z"]):o["z"] + o["d"], max(0, o["x"]):o["x"] + o["w"]] = False
    seeds = []
    for e in ev.ev.values():
        if e.get("role") == "portal" and "pos" in e:
            seeds.append((int(e["pos"][0]), int(e["pos"][2])))
    if not seeds:
        return 0
    expanded = [(x + dx, z + dz) for x, z in seeds for dx in range(-2, 3) for dz in range(-2, 3)]
    reach, _ = flood(walk, expanded)
    if reach.sum() < 20:
        return 0
    if link is not None:
        cut, ra, rb = link
        if (m.cave_rooms[ra] & reach).sum() < 10 or (m.cave_rooms[rb] & reach).sum() < 10:
            return 0
        floor_open = floor_open & ~cut
        reach = reach & ~cut
    sealed = floor_open & ~reach
    keep_clear = dilate(floor_open, 4)
    keep_clear[:3, :] = keep_clear[-3:, :] = True
    keep_clear[:, :3] = keep_clear[:, -3:] = True
    zz, xx = np.mgrid[0:d, 0:w]
    target = int(np.clip((~keep_clear).sum() / 420, 4, 12))
    rooms, new = [], np.zeros((d, w), bool)
    for _ in range(900):
        if len(rooms) >= target:
            break
        rx, rz = int(rng.integers(5, 11)), int(rng.integers(4, 7))
        cx, cz = int(rng.integers(rx + 3, max(rx + 4, w - rx - 3))), int(rng.integers(rz + 3, max(rz + 4, d - rz - 3)))
        ang = np.arctan2(zz - cz, xx - cx)
        wob = 1 + 0.14 * np.sin(ang * 5 + rng.uniform(0, 6)) + 0.08 * np.sin(ang * 9 + rng.uniform(0, 6))
        mask = ((xx - cx) / rx) ** 2 + ((zz - cz) / rz) ** 2 <= wob
        if (mask & (keep_clear | dilate(new, 4))).any():
            continue
        rooms.append({"c": (cx, cz), "m": mask})
        new |= mask
    if not rooms:
        return 0

    def jog(a, b):
        mx, mz = (a[0] + b[0]) / 2.0 + rng.uniform(-7, 7), (a[1] + b[1]) / 2.0 + rng.uniform(-4, 4)
        return [a, (mx, mz), b]

    forbid = dilate(floor_open, 2)
    rc = [np.array(r["c"]) for r in rooms]
    pts = np.argwhere(reach if link is None else (reach & m.cave_rooms[ra]))
    pts_xz = np.stack([pts[:, 1], pts[:, 0]], 1)
    best = sorted(range(len(rooms)), key=lambda i: np.min(np.sum((pts_xz - rc[i]) ** 2, 1)))
    carved, anchor = None, None
    for i in best[:6]:
        c = rc[i]
        order = np.argsort(np.sum((pts_xz - c) ** 2, 1))[:40]
        for k in order[::4]:
            a = (int(pts_xz[k][0]), int(pts_xz[k][1]))
            for _ in range(10):
                path = disc_path((d, w), jog(tuple(rooms[i]["c"]), a), 3)
                near = (xx - a[0]) ** 2 + (zz - a[1]) ** 2 <= 16
                if not (path & forbid & ~near).any() and not (path & sealed).any():
                    carved, anchor = path | rooms[i]["m"], a
                    used = [i]
                    break
            if carved is not None:
                break
        if carved is not None:
            break
    if carved is None:
        return 0
    links = 0
    rest = [i for i in range(len(rooms)) if i not in used]
    while rest:
        done = False
        rest.sort(key=lambda i: min(np.sum((rc[i] - rc[j]) ** 2) for j in used))
        for i in rest:
            j = min(used, key=lambda u: np.sum((rc[i] - rc[u]) ** 2))
            for _ in range(10):
                path = disc_path((d, w), jog(rooms[i]["c"], rooms[j]["c"]), 3 + int(rng.integers(0, 2)))
                if not (path & forbid).any():
                    carved |= path | rooms[i]["m"]
                    used.append(i)
                    rest.remove(i)
                    done = True
                    break
            if done:
                break
        if not done:
            break
    for a_i, i in enumerate(used):                                       # loops: more than one way through
        for j in used[a_i + 1:]:
            if np.sum((rc[i] - rc[j]) ** 2) < 34 ** 2 and rng.random() < 0.55 and links < len(used):
                path = disc_path((d, w), jog(rooms[i]["c"], rooms[j]["c"]), 3)
                if not (path & forbid).any():
                    carved |= path
                    links += 1
    if link is not None:                                                 # the far side of the walled tunnel: the way on
        bcells = np.argwhere(reach & m.cave_rooms[rb])
        joined = False
        for i in sorted(used[1:] or used, key=lambda u: -np.sum((rc[u] - rc[used[0]]) ** 2)):
            order = np.argsort(np.sum((bcells[:, ::-1] - rc[i]) ** 2, 1))[:30]
            for q in order[::3]:
                a2 = (int(bcells[q][1]), int(bcells[q][0]))
                for _ in range(10):
                    path = disc_path((d, w), jog(rooms[i]["c"], a2), 4)
                    near = (xx - a2[0]) ** 2 + (zz - a2[1]) ** 2 <= 16
                    if not (path & forbid & ~near).any() and not (path & sealed).any():
                        carved |= path
                        joined = True
                        break
                if joined:
                    break
            if joined:
                break
        if not joined:
            return 0
    _, dist = flood(reach, [anchor])                                     # a second way back to the same spot on the route
    near_anchor = [p for p, v in dist.items() if 6 <= v <= 18]
    if near_anchor and len(used) > 1:
        rng.shuffle(near_anchor)
        for a in near_anchor[:12]:
            a = (int(a[0]), int(a[1]))
            path = disc_path((d, w), jog(rooms[used[1]]["c"], a), 3)
            near = (xx - a[0]) ** 2 + (zz - a[1]) ** 2 <= 16
            if not (path & forbid & ~near).any() and not (path & sealed).any():
                carved |= path
                break
    if cut is not None:
        m.blk[cut] = m.cave_wall
        m.hgt[cut] = 2 + m.cave_wall_h
    m.blk[carved] = m.cave_floor
    m.hgt[carved] = 2
    wall_top = m.cave_wall_h
    solid = ~(carved | floor_open)
    m.rerouted = cut is not None
    front = np.zeros((d, w), bool)                                       # the same cut-away as cave_map: walls in front of a
    for k in range(1, 10):                                               # room drop to a low rim so the room stays visible
        front[:d - k] |= carved[k:]
    front &= solid & ~dilate(sealed, 3)
    m.hgt[front & (m.hgt > 4)] = 4
    ring = dilate(carved, 1) & solid                                     # a lip nobody can jump onto from the new galleries
    m.hgt[ring] = np.maximum(m.hgt[ring], 5)
    m.blk[ring] = m.cave_wall
    placed = 0
    rooms_used = [rooms[i] for i in used]
    rng.shuffle(rooms_used)
    if not getattr(m, "has_shrine", False):
        cx, cz = rooms_used[0]["c"]
        save_shrine(m, ev, cx, cz)
        rooms_used = rooms_used[1:]
    for r in rooms_used[:max(1, len(rooms_used) * 2 // 3)]:
        cx, cz = r["c"]
        item, num = LOOT[int(rng.integers(0, len(LOOT)))]
        ev.chest(cx + int(rng.integers(-2, 3)), cz + int(rng.integers(-1, 2)), item, num)
        placed += 1
    for r in rooms_used:
        cells = np.argwhere(r["m"] & ~dilate(~r["m"], 2))
        if len(cells) and rng.random() < 0.5:
            z, x = cells[int(rng.integers(0, len(cells)))]
            if abs(x - r["c"][0]) > 2 or abs(z - r["c"][1]) > 2:
                m.tree(int(x), int(z), rocks[int(rng.integers(0, 2))])
    return len(used)
