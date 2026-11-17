"""Battle sprite sizing and atlas coverage checks.

Run: py -3.12 -E -W ignore::ResourceWarning -m unittest discover -s tools -p test_battle_sprite_scale.py
"""
import json
import re
import unittest
from pathlib import Path

from PIL import Image

import gen_sprites2d as sprites


ACTOR_MEMO_MARKERS = (
    "traveler sprite",
    "traveler look",
    "side-cast sprite",
    "human enemy sprite",
    "monster (tools/gen_monsters.py)",
    "procedural (tools/gen_enemy_art.py)",
    "nezumi (tools/gen_nezumi.py)",
    "boss art (tools/gen_bossart.py",
    "AI foe art (tools/gen_foe_art.py",
)


def is_battle_actor(eid, entry):
    legacy = re.fullmatch(r"EP(\d{3})", eid)
    if legacy and 1 <= int(legacy.group(1)) <= 60:
        return True
    memo = entry.get("memo", "")
    return any(marker in memo for marker in ACTOR_MEMO_MARKERS)


class BattleSpriteScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = Path(sprites.RES)
        cls.models = json.loads((cls.resource / "enemy_pic.json").read_text(encoding="utf-8"))
        cls.actors = {eid: entry for eid, entry in cls.models.items()
                      if isinstance(entry, dict) and entry.get("pic3d") and is_battle_actor(eid, entry)}

    def test_all_battle_actor_animation_zones_fit_their_sheets(self):
        self.assertGreater(len(self.actors), 1200)
        sizes = {}
        for eid, entry in self.actors.items():
            with self.subTest(model=eid):
                cols, rows = entry.get("aniuv", (1, 1))
                self.assertGreater(cols, 0)
                self.assertGreater(rows, 0)
                pic = entry["pic3d"].split("/resource/", 1)[1]
                path = self.resource / Path(pic)
                if pic not in sizes:
                    with Image.open(path) as image:
                        sizes[pic] = image.size
                width, height = sizes[pic]
                self.assertEqual(width % cols, 0)
                self.assertEqual(height % rows, 0)
                frame_count = cols * rows
                for animation in entry.get("animap", []):
                    self.assertGreaterEqual(animation["st"], 0)
                    self.assertGreater(animation["en"], animation["st"])
                    self.assertLessEqual(animation["en"], frame_count)

    def test_every_registered_actor_uses_the_larger_scale(self):
        self.assertAlmostEqual(self.models["EP200"]["scale1x"],
                               1.45 * sprites.CAST_SCALE * sprites.HUMAN_SCALE * sprites.BATTLE_SPRITE_SCALE)
        self.assertAlmostEqual(self.models["EP200"]["scale"], self.models["EP200"]["scale1x"] / 2)
        for eid, entry in self.actors.items():
            if "/enemy_pic2x/" in entry["pic3d"]:
                self.assertIn("scale1x", entry)
                self.assertAlmostEqual(entry["scale"], entry["scale1x"] / 2)
            else:
                self.assertGreater(entry["scale"], 0)
        for number in range(1, 61):
            self.assertAlmostEqual(self.models["EP%03d" % number]["scale"], sprites.BATTLE_SPRITE_SCALE)

    def test_roster_inventory_covers_travelers_cast_and_foes(self):
        memos = [entry.get("memo", "") for entry in self.actors.values()]
        self.assertEqual(sum(m.startswith("traveler sprite") for m in memos), 8)
        self.assertGreaterEqual(sum(m.startswith("side-cast sprite") for m in memos), 690)
        self.assertGreaterEqual(sum(m.startswith("human enemy sprite") for m in memos), 70)
        self.assertGreaterEqual(sum("monster (tools/gen_monsters.py)" in m for m in memos), 40)
        self.assertGreaterEqual(sum("boss art (tools/gen_bossart.py" in m for m in memos), 40)
        self.assertGreaterEqual(sum("AI foe art (tools/gen_foe_art.py" in m for m in memos), 20)
