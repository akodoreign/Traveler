import unittest
from collections import deque

import numpy as np

import mieko_cellar_worlds as cellar


class MiekoCellarWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, original, candidate, _, _ = cellar.variant()
        cls.before, cls.before_events = cellar.baseline(original)
        cls.world, cls.events = candidate.make("M295")

    def test_story_events_and_old_room_are_preserved(self):
        self.assertEqual(self.events.ev, self.before_events.ev)
        self.assertTrue(np.array_equal(self.world.hgt[10:21, 5:26],
                                       self.before.hgt[10:21, 5:26]))
        self.assertTrue(np.array_equal(self.world.blk[10:21, 5:25],
                                       self.before.blk[10:21, 5:25]))
        self.assertEqual(self.events.ev["#1#"]["dest"], {"mapid": "M294", "evid": 2})

    def test_entrance_boss_and_new_gallery_are_connected(self):
        m = self.world
        free = m.hgt == 1
        for obj in m.objs:
            if obj["t"] in ("fill", "blk") and obj["y"] <= 2:
                free[obj["z"]:obj["z"] + obj.get("d", 1),
                     obj["x"]:obj["x"] + obj.get("w", 1)] = False
        start = (7, 12)
        self.assertTrue(free[start[1], start[0]])
        visited, pending = {start}, deque([start])
        while pending:
            x, z = pending.popleft()
            for nx, nz in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
                if 0 <= nx < m.w and 0 <= nz < m.d and free[nz, nx] and (nx, nz) not in visited:
                    visited.add((nx, nz))
                    pending.append((nx, nz))
        for target in ((15, 15), (50, 26), (69, 41), (84, 21)):
            self.assertIn(target, visited)
        self.assertGreater(int(m.hgt[m.hgt > 1].min()) - 1, 10)


if __name__ == "__main__":
    unittest.main()
