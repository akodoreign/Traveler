"""Bigger, sprawling caves (user, 2026-11-08): new galleries and looping tunnels carved into the solid rock of a finished cave map.
Called from gen_maps.make() after the hand-placed rooms and events exist.

The story route must not change: everything new is one cluster of rooms hanging off a single spot already on the player's
route. It may have several tunnels back to that spot and loops inside itself, but it never touches another room, so it can't
walk around a scene trigger, a boss or a sealed wall. Sealed areas (not reachable from the map's portals) are kept clear.
New galleries hold a few chests, and a rest-and-save shrine when the map has none."""
import collections
import re

import cv2
import numpy as np

CAVE_NAME = re.compile(r"\bcave|tunnel|catacomb|cellar|under the|\bcove\b|lava tube|\bmines?\b|\bden\b", re.I)
LOOT = [("I445", 2), ("I447", 2), ("I100", 3), ("I446", 1), ("I448", 1), ("I101", 2), ("N000", 120), ("N000", 200)]


def wanted(name):
    return bool(CAVE_NAME.search(name))


def grow_size(w, d, rooms, links):
    """A cave grows toward a side with no exit on it: east if it can, else south. Hand-placed coordinates stay valid."""
    east = any(max(l[0], l[2]) >= w - 3 for l in links) or any(r[0] + r[2] >= w - 2 for r in rooms)
    south = any(max(l[1], l[3]) >= d - 3 for l in links) or any(r[1] + r[3] >= d - 2 for r in rooms)
    return (w if east else int(w * 1.6)), (d if south else int(d * 1.5))   # (user) use the space: both ways when both are free


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


def climbable(hgt, floor):
    """Cells the player can get on top of from the floor: up by at most 2 blocks (the jump), down by any."""
    seen = floor.copy()
    while True:
        n = seen.copy()
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            n |= np.roll(seen, sh, ax) & (hgt <= np.roll(hgt, sh, ax) + 2)
        if (n == seen).all():
            return seen
        seen = n


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


def event_cells(m, ev):
    spots = np.zeros((m.d, m.w), bool)
    for e in ev.ev.values():
        if "pos" in e and 0 <= int(e["pos"][2]) < m.d and 0 <= int(e["pos"][0]) < m.w:
            spots[int(e["pos"][2]), int(e["pos"][0])] = True
    return spots


def reach_of(m, ev):
    """(floor_open, where the player can walk from the exits). A cave with no portal is entered by its touch triggers."""
    floor_open = m.hgt <= 3                                              # floors and pools; rims and rock stand higher
    walk = floor_open & (m.blk != 8)                                     # pits and steps can be walked; water, tar and lava can't
    for o in m.objs:
        if o["t"] == "fill" and o.get("blk") is not None and o["h"] > 1:   # a filled block in the way stays in the way
            walk[max(0, o["z"]):o["z"] + o["d"], max(0, o["x"]):o["x"] + o["w"]] = False
    seeds = [(int(e["pos"][0]), int(e["pos"][2])) for e in ev.ev.values() if e.get("role") == "portal" and "pos" in e]
    if not seeds:                                                        # entered and left by scene triggers alone
        seeds = [(int(e["pos"][0]), int(e["pos"][2])) for e in ev.ev.values() if "pos" in e and e.get("role") != "light"]
    if not seeds:
        return floor_open, None
    expanded = [(x + dx, z + dz) for x, z in seeds for dx in range(-2, 3) for dz in range(-2, 3)]
    reach, _ = flood(walk, expanded)
    if reach.sum() < 20:                                                 # an exit standing on a step or a fill: start from the events
        spots = [(int(e["pos"][0]), int(e["pos"][2])) for e in ev.ev.values() if "pos" in e and e.get("role") != "light"]
        reach, _ = flood(walk, spots)
    return floor_open, reach


def necks(m, ev, reach, avoid):
    """(user, 2026-11-10: force the travelers through a good part of each level) Every narrow spot on the walkable floor that
    is the only way between two sizeable parts of the cave and has no event near it: (plug, side A, side B), most even split
    first. Swapping such a bridge for a longer one keeps the story order: nothing on either side can be skipped."""
    d, w = reach.shape
    raw = event_cells(m, ev)
    spots = dilate(raw, 1)
    door = np.zeros((d, w), bool)                                        # the entrance stub counts as a side, however small
    for e in ev.ev.values():
        if e.get("role") == "portal" and "pos" in e and 0 <= int(e["pos"][2]) < d and 0 <= int(e["pos"][0]) < w:
            door[int(e["pos"][2]), int(e["pos"][0])] = True
    door = dilate(door, 2)
    u8 = reach.astype(np.uint8)
    dt = cv2.distanceTransform(u8, cv2.DIST_L2, 3)
    _, lab0 = cv2.connectedComponents(u8, connectivity=4)
    zz, xx = np.mgrid[0:d, 0:w]
    found = []
    for r in (1.5, 2.5, 3.5, 4.5, 5.5):
        cells = np.argwhere(reach & (dt > r - 1.2) & (dt <= r))
        for z, x in cells[::2]:
            for shape in ("disc", "across", "along"):                    # a thin wall fits between two events where a round plug can't
                if shape == "disc":
                    disc = ((xx - x) ** 2 + (zz - z) ** 2 <= (r + 1.0) ** 2) & reach
                elif shape == "across":
                    disc = (np.abs(zz - z) <= 1) & (np.abs(xx - x) <= r + 2) & reach
                else:
                    disc = (np.abs(xx - x) <= 1) & (np.abs(zz - z) <= r + 2) & reach
                if (disc & spots).any() or (disc & avoid).any():
                    continue
                left = reach & ~disc
                n, lab, stats, _ = cv2.connectedComponentsWithStats(left.astype(np.uint8), connectivity=4)
                home = lab0 == lab0[z, x]
                ids = [i for i in np.unique(lab[home & left]) if i]
                big = [i for i in ids if stats[i, cv2.CC_STAT_AREA] >= 30 or (stats[i, cv2.CC_STAT_AREA] >= 8 and (door & (lab == i)).any())]
                if len(big) != 2:
                    continue
                frag = home & left & ~np.isin(lab, big)
                if frag.sum() > 40 or (frag & raw).any():
                    continue
                found.append((min(stats[i, cv2.CC_STAT_AREA] for i in big), int(x), int(z), disc | frag, lab == big[0], lab == big[1]))
    found.sort(key=lambda f: -f[0])
    out, kept = [], []
    for _, x, z, cut, a, b in found:
        if all((x - u) ** 2 + (z - v) ** 2 >= 12 ** 2 for u, v in kept):
            kept.append((x, z))
            out.append((cut, a, b))
    return out


PASSES = 3


def event_groups(m, ev, reach):
    """How many separate walkable areas hold the events that stood on the route before this pass."""
    walk = (m.hgt <= 3) & (m.blk != 8)
    _, lab = cv2.connectedComponents(walk.astype(np.uint8), connectivity=4)
    return len({int(lab[z, x]) for z, x in np.argwhere(event_cells(m, ev) & reach)} - {0}) + \
        int((event_cells(m, ev) & reach & ~walk).sum())


def sprawl(m, ev, mid, rocks, save_shrine):
    """Reroute the required path through new galleries at up to PASSES narrow spots, so getting through the level means walking
    them (user). Only a cave with no such spot at all gets a side branch. Returns the number of rooms added."""
    if ev is None or not hasattr(m, "cave_floor"):
        return 0
    total = 0
    for p in range(PASSES):
        _, reach = reach_of(m, ev)
        if reach is None or reach.sum() < 20:
            break
        cands = necks(m, ev, reach, dilate(getattr(m, "sprawled", np.zeros((m.d, m.w), bool)), 2))
        built = 0
        for gain in (80, 50, 25, 8):                                         # the longest detour this neck can give
            for k, c in enumerate(cands[:10]):
                saved = (m.hgt.copy(), m.blk.copy(), set(ev.ev), len(m.objs), getattr(m, "has_shrine", False), getattr(m, "sprawled", None))
                groups = event_groups(m, ev, reach)
                built = _build(m, ev, mid, rocks, save_shrine, c, p * 20 + k, PASSES - p, gain)
                if built and event_groups(m, ev, reach) > groups:        # something got cut off: never ship that
                    m.hgt, m.blk = saved[0], saved[1]
                    for key in set(ev.ev) - saved[2]:
                        del ev.ev[key]
                    del m.objs[saved[3]:]
                    m.has_shrine, m.sprawled = saved[4], saved[5] if saved[5] is not None else np.zeros((m.d, m.w), bool)
                    built = 0
                if built:
                    break
            if built:
                break
        if not built:
            break
        total += built
    total = total or _build(m, ev, mid, rocks, save_shrine, None, 9, 1)
    if total:                                                            # last: no wall top anywhere can be climbed to get around a plug
        floor = m.hgt <= 3
        for _ in range(8):
            bad = climbable(m.hgt, floor) & ~floor
            if not bad.any():
                break
            m.hgt[bad] = 2 + m.cave_wall_h
    return total


def _build(m, ev, mid, rocks, save_shrine, link, attempt, share, gain=0):
    rng = np.random.default_rng(int(mid[1:]) * 7 + 11 + attempt)
    d, w = m.d, m.w
    floor_open, reach = reach_of(m, ev)
    cut = None
    if reach is None or reach.sum() < 20:
        return 0
    if link is not None:
        cut, side_a, side_b = link
        if (side_a & reach).sum() < 10 or (side_b & reach).sum() < 10:
            return 0
        floor_open = floor_open & ~cut
        reach = reach & ~cut
    sealed = floor_open & ~reach
    keep_clear = dilate(floor_open, 4)
    keep_clear[:3, :] = keep_clear[-3:, :] = True
    keep_clear[:, :3] = keep_clear[:, -3:] = True
    zz, xx = np.mgrid[0:d, 0:w]
    target = int(np.clip((~keep_clear).sum() / 420 / share, 3, 12))
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
    pts = np.argwhere(reach if link is None else (reach & side_a))
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
        bcells = np.argwhere(reach & side_b)
        joined = None
        for i in sorted(used[1:] or used, key=lambda u: -np.sum((rc[u] - rc[used[0]]) ** 2)):
            order = np.argsort(np.sum((bcells[:, ::-1] - rc[i]) ** 2, 1))[:30]
            for q in order[::3]:
                a2 = (int(bcells[q][1]), int(bcells[q][0]))
                for _ in range(10):
                    path = disc_path((d, w), jog(rooms[i]["c"], a2), 4)
                    near = (xx - a2[0]) ** 2 + (zz - a2[1]) ** 2 <= 16
                    if not (path & forbid & ~near).any() and not (path & sealed).any():
                        carved |= path
                        joined = a2
                        break
                if joined:
                    break
            if joined:
                break
        if not joined:
            return 0
        if flood(carved, [anchor])[1].get(joined, 0) < gain:              # too short a detour to be worth a wall
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
    m.sprawled = getattr(m, "sprawled", np.zeros((d, w), bool)) | carved
    m.blk[carved] = m.cave_floor
    m.hgt[carved] = 2
    wall_top = m.cave_wall_h
    solid = ~(carved | floor_open)
    m.rerouted = cut is not None
    front = np.zeros((d, w), bool)                                       # the same cut-away as cave_map: walls in front of a
    for k in range(1, 10):                                               # room drop to a low rim so the room stays visible
        front[:d - k] |= carved[k:]
    front &= solid & ~dilate(sealed, 3)
    m.hgt[front & (m.hgt > 5)] = 5
    ring = dilate(carved, 1) & solid                                     # a lip nobody can jump onto from the new galleries
    m.hgt[ring] = np.maximum(m.hgt[ring], 5)
    m.blk[ring] = m.cave_wall
    guard = ring.copy()
    if cut is not None:
        low = np.zeros((d, w), bool)                                     # a plug in front of floor is a low rim the camera sees over
        for k in range(1, 10):
            low[:d - k] |= (carved | floor_open)[k:]
        m.hgt[cut & low] = 5
        m.hgt[cut] = np.maximum(m.hgt[cut], 5)
        guard |= cut
    tall = 2 + m.cave_wall_h
    for _ in range(8):                                                   # no climbing a low rim, along the lip and down the far side
        got = climbable(m.hgt, carved | floor_open)
        bad = got & guard & solid
        if not bad.any():
            break
        m.hgt[bad] = tall
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
