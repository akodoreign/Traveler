import unittest

import numpy as np

import regional_cave_revisit as revisit
from river_lion_worlds import audit, connected


class RegionalCaveRevisitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.original, cls.candidate, _, _ = revisit.variant()

    def test_raise_walls_without_altering_routes_or_events(self):
        for mid in revisit.MAPS:
            with self.subTest(mid=mid):
                old, old_events = revisit.baseline(self.original, mid)
                new, new_events = self.candidate.make(mid)
                walls = old.blk == self.candidate.STONE
                self.assertEqual(old_events.ev, new_events.ev)
                np.testing.assert_array_equal(old.blk, new.blk)
                np.testing.assert_array_equal(old.hgt[~walls], new.hgt[~walls])
                self.assertGreater(int(new.hgt[walls].min()) - 2, 10)
                if mid == "M485":
                    self.assertEqual(connected(old, self.original, (46, 8), 2),
                                     connected(new, self.candidate, (46, 8), 2))
                else:
                    self.assertEqual(audit(old, old_events, self.original),
                                     audit(new, new_events, self.candidate))


if __name__ == "__main__":
    unittest.main()
