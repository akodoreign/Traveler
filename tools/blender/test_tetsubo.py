r"""Run with Blender --background --python-exit-code 1 --python tools\blender\test_tetsubo.py."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chara3d as c
from chara3d_victory import weapon_mesh


class TetsuboGeometryTest(unittest.TestCase):
    def setUp(self):
        self.skin = c.Skin()
        c.weapon(self.skin, {"accent": (130, 61, 45), "trim": (155, 143, 120)}, "tetsubo")

    def vertices(self, parts):
        indices = {index for face, part in zip(self.skin.faces, self.skin.part)
                   if part in parts for index in face}
        return c.np.asarray([self.skin.verts[index] for index in indices])

    def test_long_straight_striking_section(self):
        points = c.np.asarray(self.skin.verts)
        length = c.np.ptp(points[:, 1])
        self.assertGreater(length, 100)
        self.assertLess(length, 140)
        wood_parts = {part for part, colour in zip(self.skin.part, self.skin.colour) if colour == c.WOOD}
        shaft = self.vertices(wood_parts)
        self.assertGreater(c.np.ptp(shaft[:, 1]) / length, .7)
        radii = c.np.linalg.norm(shaft[:, (0, 2)], axis=1)
        self.assertLess(max(radii) / min(radii), 1.15)
        self.assertGreater(min(radii), 3)

    def test_raised_studs_along_every_side(self):
        parts = set(self.skin.part)
        studs = []
        for part in parts:
            points = self.vertices({part})
            if min(points[:, 1]) > 12 and max(points[:, 1]) < 97 and c.np.ptp(points[:, 1]) < 3:
                studs.append(points)
        self.assertGreaterEqual(len(studs), 48)
        for points in studs:
            self.assertGreater(max(c.np.linalg.norm(points[:, (0, 2)], axis=1)), 4)
        centres = c.np.asarray([points.mean(axis=0) for points in studs])
        self.assertGreater(c.np.ptp(centres[:, 1]), 60)
        self.assertEqual(len(set(c.np.round(c.np.arctan2(centres[:, 2], centres[:, 0]), 3))), 8)

    def test_original_grip_and_item_weighting(self):
        for skin in (self.skin, weapon_mesh("W103", "tetsubo", "Oak Tetsubo"),
                     weapon_mesh("W117", "tetsubo", "Jade-studded Tetsubo")):
            self.assertTrue(all(weight == {"weapon": 1.} for weight in skin.weights))
            points = c.np.asarray(skin.verts)
            self.assertLess(min(points[:, 1]), -10)
            self.assertGreater(max(points[:, 1]), 90)
            grip = points[c.np.abs(points[:, 1]) < 1]
            self.assertGreater(len(grip), 0)
            self.assertLess(max(c.np.linalg.norm(grip[:, (0, 2)], axis=1)), 2)


if __name__ == "__main__":
    unittest.main(argv=[__file__])
