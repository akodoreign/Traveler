"""Castle geometry, reciprocal routes and fetch-state regression checks (no engine required).

Run: py -3.12 -E -m unittest discover -s tools -p test_castles.py
"""
import json
import unittest
from collections import deque

import numpy as np

import gen_maps as gm
import walkcheck


def walkable(m, ev):
    """Find the lowest head-clear floor, including paths UNDER door lintels, not on top of them."""
    solid = (np.arange(64)[None, None, :] <= m.hgt[:, :, None]) & (m.blk[:, :, None] != 0)
    for o in m.objs:
        if o["t"] == "fill":
            solid[o["z"]:o["z"] + o["d"], o["x"]:o["x"] + o["w"],
                  o["y"]:o["y"] + o["h"]] = o["blk"] != gm.VOID
        elif o["t"] == "blk" and (o["blk"] & 31) != 11:
            solid[o["z"], o["x"], o["y"]] = True
    clear = solid[:, :, :-3] & ~solid[:, :, 1:-2] & ~solid[:, :, 2:-1] & ~solid[:, :, 3:]
    heights = np.where(clear.any(axis=2), clear.argmax(axis=2) + 1, -1)
    _, blocked = walkcheck.floors(m)
    for e in ev.ev.values():
        if "G293" in str(e.get("reqs0")):
            continue
        if e.get("mdlid", "").startswith(("EP", "CV")) and e.get("role") != "light":
            x, _, z, _ = e["pos"]
            blocked[z, x] = True
    ok = ~blocked & (heights >= 0)
    wide = ok[:-1, :-1] & ok[1:, :-1] & ok[:-1, 1:] & ok[1:, 1:]
    levels = (heights[:-1, :-1], heights[1:, :-1], heights[:-1, 1:], heights[1:, 1:])
    wide &= np.maximum.reduce(levels) - np.minimum.reduce(levels) <= 1
    return heights, wide


def flood(heights, wide, start):
    seen, queue = {start}, deque([start])
    while queue:
        x, z = queue.popleft()
        for nx, nz in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
            if (0 <= nz < wide.shape[0] and 0 <= nx < wide.shape[1] and wide[nz, nx]
                    and (nx, nz) not in seen and abs(int(heights[nz, nx]) - int(heights[z, x])) <= 1):
                seen.add((nx, nz))
                queue.append((nx, nz))
    return seen


class CastleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps = {}
        for castle in gm.CLAN_CASTLES:
            for mid in (*castle["grounds"].values(), *castle["ids"][1:]):
                cls.maps[mid] = gm.make(mid)

    def test_full_maps_and_reciprocal_routes(self):
        ids = [mid for c in gm.CLAN_CASTLES for mid in (*c["grounds"].values(), *c["ids"][1:])]
        self.assertEqual(len(ids), len(set(ids)))
        for castle in gm.CLAN_CASTLES:
            with self.subTest(castle=castle["name"]):
                self.assertEqual(set(castle["grounds"]), {(x, z) for x in range(3) for z in range(4)})
                for mid in (*castle["grounds"].values(), *castle["ids"][1:]):
                    m, ev = self.maps[mid]
                    self.assertGreaterEqual(m.w, 96)
                    self.assertGreaterEqual(m.d, 64)
                    for key, e in ev.ev.items():
                        if e.get("role") != "portal":
                            continue
                        dest = e["dest"]
                        target = self.maps.get(dest["mapid"]) or gm.make(dest["mapid"])
                        landing = target[1].ev["#%s#" % dest["evid"]]
                        self.assertTrue(landing["role"] == "portal" or any(
                            p.get("memo") == "landing" for p in landing.get("page", [])), (mid, key, dest))
                        self.assertTrue(any(e.get("dest", {}).get("mapid") == mid
                                            for e in target[1].ev.values()), (mid, key, "missing return route"))

    def test_every_exit_and_resident_reachable_without_jumping(self):
        directions = {0: (0, -2), 1: (-2, 0), 2: (0, 2), 3: (2, 0)}
        for mid, (m, ev) in self.maps.items():
            with self.subTest(map=mid):
                heights, wide = walkable(m, ev)
                landings = [e for e in ev.ev.values() if any(
                    p.get("memo") == "landing" for p in e.get("page", [])) or (
                        e.get("role") == "portal" and e.get("memo") != "stairwell"
                        and max(e.get("mdl", {}).get("r", [0] * 6)[3:6:2]) <= 1.5)]
                first = landings[0]["pos"]
                dx, dz = directions[first[3]]
                start = (first[0] + dx, first[2] + dz)
                self.assertTrue(wide[start[1], start[0]], (mid, "blocked arrival", start))
                seen = flood(heights, wide, start)
                self.assertGreater(len(seen), 3000, (mid, "not a full playable map"))
                for key, e in ev.ev.items():
                    if "pos" not in e or e.get("role") == "light":
                        continue
                    if "G293" in str(e.get("reqs0")):
                        continue
                    if e.get("role") == "portal" and e not in landings:
                        if e.get("memo") == "stairwell":
                            x, _, z, _ = e["pos"]
                            self.assertIn((x, z), seen, (mid, key, "unreachable descending flight"))
                        continue
                    if e.get("mdlid") == "CE000" and e.get("role") != "portal":
                        if e not in landings:
                            continue
                    x, y, z, direction = e["pos"]
                    if e in landings:
                        dx, dz = directions[direction]
                        ax, az = x + dx, z + dz
                        self.assertTrue((ax, az) in seen, (mid, key, "unreachable arrival"))
                        self.assertLessEqual(abs(int(heights[az, ax]) - y), 1, (mid, key, "arrival height"))
                    self.assertTrue(any((x + dx, z + dz) in seen for dx in range(-2, 3)
                                        for dz in range(-2, 3)), (mid, key, "unreachable interaction"))

    def test_keep_stairs_and_doorways(self):
        for castle in gm.CLAN_CASTLES:
            for level, mid in enumerate(castle["ids"][1:]):
                with self.subTest(map=mid):
                    m, ev = self.maps[mid]
                    ox, oz = gm.ROOM_OFS[mid]
                    for key in ("#1#", "#2#") if level < 3 else ("#1#",):
                        x, y, z, _ = ev.ev[key]["pos"]
                        lintel = any(o["t"] == "fill" and o["x"] <= x < o["x"] + o["w"]
                                     and o["z"] == z and o["y"] == y + 5 for o in m.objs)
                        self.assertEqual(lintel, level == 0 and key == "#1#",
                                         (mid, key, "doorframes belong at doors, not stair openings"))
                    if level < 3:
                        self.assertEqual([int(m.hgt[z + oz, 86 + ox]) for z in range(46, 53)],
                                         list(range(9, 16)))
                        self.assertEqual(ev.ev["#2#"]["dest"], {"mapid": castle["ids"][level + 2], "evid": 3})
                    if level:
                        self.assertEqual([int(m.hgt[z + oz, 9 + ox]) for z in range(12, 5, -1)],
                                         list(range(9, 2, -1)))
                        self.assertEqual(ev.ev["#1#"]["dest"], {"mapid": castle["ids"][level], "evid": 4})
                    self.assertEqual(ev.ev["#3#"]["pos"], [9 + ox, 10, 14 + oz, 2])
                    self.assertEqual(ev.ev["#4#"]["pos"], [87 + ox, 10, 46 + oz, 0])

    def test_castle_errands_have_guarded_pickups_and_single_rewards(self):
        flags = [f for group in gm.FQ_FLAGS.values() for f in group]
        self.assertEqual(len(flags), len(set(flags)))
        for q in gm.FETCH_QUESTS:
            key, _, giver, _, _, _, _, pickup, *_ = q
            if not gm.FQ_SETTINGS.get(key, {}).get("castle"):
                continue
            with self.subTest(quest=key):
                taken, found, done = gm.FQ_FLAGS[key]
                giver_events = self.maps[giver][1].ev.values()
                event = next(e for e in giver_events if any(
                    gm.flag(done) in (p.get("reqs") or []) for p in e.get("page", [])))
                reward = next(p for p in event["page"] if gm.flag(found) in (p.get("reqs") or [])
                              and gm.flag(done, False) in p["reqs"])
                self.assertEqual(sum(c.get("cmd") == "cmd_moneyop" for c in reward["cmdblock"]), 1)
                self.assertIn(gm.setf(done), reward["cmdblock"])
                offers = [p for p in event["page"] if gm.flag(taken, False) in (p.get("reqs") or [])]
                self.assertEqual(len(offers), 1)
                self.assertIsNone(gm.FQ_SETTINGS[key]["who"])
                self.assertNotIn(gm.flag(gm.FQ_OPEN), offers[0]["reqs"])
                pickup_events = self.maps[pickup][1].ev.values()
                item = next(e for e in pickup_events if gm.setf(found) in [
                    c for p in e.get("page", []) for c in p["cmdblock"]])
                self.assertEqual(item["reqs0"], [gm.flag(taken), gm.flag(found, False)])
                self.assertTrue(any(e.get("mdlid") in gm.DECOR_EP.values() and e["pos"][:3] == item["pos"][:3]
                                    for e in self.maps[pickup][1].ev.values()))
                self.assertNotIn("questExp", json.dumps(reward))


if __name__ == "__main__":
    unittest.main()
