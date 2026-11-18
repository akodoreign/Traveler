import unittest

from chara3d_native_all import build_registry


class NativeProportionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        roster, _, _ = build_registry()
        cls.sizes = {key: entry["proportions"] for key, entry in roster.items()}
        cls.groups = {key: entry["group"] for key, entry in roster.items()}

    def test_tallest_travelers(self):
        travelers = [key for key, group in self.groups.items() if group == "traveler"]
        travelers.append("side_yosai")  # Playable traveler, indexed as a story companion.
        travelers.sort(key=lambda key: self.sizes[key][1], reverse=True)
        self.assertEqual(travelers[:3], ["side_yosai", "trav_natsuko", "trav_tamotsu"])
        self.assertGreater(self.sizes[travelers[2]][1], self.sizes[travelers[3]][1])

    def test_cast_stature_and_outfit_variants(self):
        self.assertGreater(self.sizes["side_kisada"][1], self.sizes["side_yosai"][1])
        self.assertLess(self.sizes["side_gontaboy"][1], self.sizes["side_oldwoman"][1])
        self.assertEqual(self.sizes["side_kage_ch3"], self.sizes["side_kage"])
        self.assertEqual(self.sizes["side_kafu_nosword"], self.sizes["side_kafu"])

    def test_each_group_varies_in_height_and_width(self):
        for group in set(self.groups.values()):
            with self.subTest(group=group):
                sizes = [size for key, size in self.sizes.items() if self.groups[key] == group]
                self.assertGreater(len({height for _, height, _ in sizes}), 3)
                self.assertGreater(len({width for _, _, width in sizes}), 3)
