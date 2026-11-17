"""Quest key-item, pickup-star, and giver-marker regression checks.

Run: py -3.12 -E -W ignore::ResourceWarning -m unittest discover -s tools -p test_quest_items.py
"""
import json
import unittest
from copy import deepcopy
from pathlib import Path

from PIL import Image

import gen_maps as gm


class QuestItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project = Path(gm.PROJ)
        cls.maps = json.loads((project / "data" / "map.json").read_text(encoding="utf-8"))
        cls.items = json.loads((project / "data" / "item.json").read_text(encoding="utf-8"))
        cls.models = json.loads((project / "resource" / "enemy_pic.json").read_text(encoding="utf-8"))
        cls.plugin = (project / "plugin" / "rokugan" / "RokuganQuestItems.sk").read_text(encoding="utf-8")

    def test_every_fetch_quest_has_a_unique_key_item_and_turnin(self):
        self.assertEqual(len(gm.FQ_ITEM_IDS), len(gm.FETCH_QUESTS))
        self.assertEqual(len(set(gm.FQ_ITEM_IDS.values())), len(gm.FQ_ITEM_IDS))
        for key, title, gmap, _, _, _, _, imap, *_ in gm.FETCH_QUESTS:
            with self.subTest(quest=key):
                itemid = gm.FQ_ITEM_IDS[key]
                item = self.items[itemid]
                self.assertEqual((item["itemtype"], item["name"]), (1, title))
                self.assertIn("Key item", item["desc"])
                taken, found, done = gm.FQ_FLAGS[key]
                giver = next(event for event in self.maps[gmap]["event"].values()
                             if "Odd job: %s" % title in json.dumps(event, ensure_ascii=False))
                turnin = next(page for page in giver.get("page", [])
                              if gm.flag(found) in (page.get("reqs") or [])
                              and gm.flag(done, False) in (page.get("reqs") or []))
                self.assertIn(gm.script("::Rokugan.returnQuestItem(%s);" %
                                        json.dumps(itemid)), turnin["cmdblock"])
                pickup = next(event for event in self.maps[imap]["event"].values()
                              if gm.setf(found) in [command for page in event.get("page", [])
                                                    for command in page.get("cmdblock", [])])
                self.assertIn({"cmd": "cmd_itemop", "itemid": itemid, "op": 0, "num": 1, "LV": 1},
                              pickup["page"][0]["cmdblock"])
                if gm.FQ_SETTINGS.get(key, {}).get("prop"):
                    self.assertTrue(any(event.get("mdlid") == "CE000"
                                        and event.get("pos", [])[:3] == pickup["pos"][:3]
                                        and event.get("reqs0") == [gm.flag(taken), gm.flag(found, False)]
                                        for event in self.maps[imap]["event"].values()))
                else:
                    self.assertEqual(pickup["mdlid"], "CE000")

    def test_yellow_and_blue_marker_data_covers_registered_quest_givers(self):
        records = gm.quest_marker_records(self.maps)
        quest_count = sum(len(states) for spots in records.values() for _, _, states in spots)
        self.assertEqual(quest_count, len(gm.FETCH_QUESTS) + len(gm.SIDE_QUESTS)
                         + len(gm.JOURNAL_SIDE_MARKERS))
        generated = (Path(gm.PROJ) / "plugin" / "rokugan" / "RokuganQuestData.sk").read_text(encoding="utf-8")
        self.assertIn("::Rokugan.QM_NPC", generated)
        self.assertIn("::Rokugan.QM_ITEM", generated)
        self.assertTrue(all(mid in generated for mid in records))
        for sid, quest in gm.journal_side_registry().items():
            spec = gm.JOURNAL_SIDE_MARKERS[sid]
            giver = next(event for event in self.maps[spec["map"]]["event"].values()
                         if event.get("mdlid") == spec["model"])
            x, z = round(giver["pos"][0] / 2.0, 2), round(giver["pos"][2] / 2.0, 2)
            row = next(row for row in records[spec["map"]] if row[:2] == [x, z])
            self.assertIn([quest["open"], spec["taken"], quest["done"]], row[2])

    def test_journal_side_quest_acceptance_is_idempotent_and_preserves_event_ids(self):
        maps = deepcopy(self.maps)
        event_ids = {mid: set((maps.get(mid) or {}).get("event", {}))
                     for mid in {spec["map"] for spec in gm.JOURNAL_SIDE_MARKERS.values()}}
        gm.migrate_journal_quest_acceptance(maps)
        gm.migrate_journal_quest_acceptance(maps)
        for sid, spec in gm.JOURNAL_SIDE_MARKERS.items():
            if not spec["choice"]:
                self.assertEqual(spec["taken"], "G1217")
                continue
            events = [event for event in maps[spec["map"]]["event"].values()
                      if event.get("mdlid") == spec["model"]]
            blocks = [block for event in events for block in gm._choice_commands(event, spec["choice"])]
            self.assertTrue(blocks, "No acceptance choice for side quest %d" % sid)
            self.assertTrue(all(sum(command.get("lvar") == spec["taken"] for command in block
                                    if isinstance(command, dict)) == 1 for block in blocks))
        self.assertEqual(event_ids, {mid: set((maps.get(mid) or {}).get("event", {})) for mid in event_ids})

    def test_fetch_item_migration_is_idempotent(self):
        maps = deepcopy(self.maps)
        original = deepcopy(maps)
        gm.migrate_fetch_quest_items(maps)
        gm.migrate_fetch_quest_items(maps)
        self.assertEqual(maps, original)

    def test_pulsing_item_markers_cover_all_fetch_pickup_locations(self):
        records = gm.quest_item_records(self.maps)
        self.assertEqual(sum(len(rows) for rows in records.values()), len(gm.FETCH_QUESTS))
        for key, *_ in gm.FETCH_QUESTS:
            taken, found, _done = gm.FQ_FLAGS[key]
            row = next(row for rows in records.values() for row in rows
                       if row[3:] == [taken, found])
            self.assertEqual(len(row), 5)
        self.assertIn("e.obj.setVisible( Math.sin( ms * 4.0) > 0.0)", self.plugin)

    def test_star_models_are_static_renderable_icons_and_legacy_turnins_are_safe(self):
        for mid in (gm.QUEST_MARKER_YELLOW_MODEL, gm.QUEST_MARKER_BLUE_MODEL, gm.QUEST_ITEM_MODEL):
            with self.subTest(model=mid):
                model = self.models[mid]
                self.assertEqual(model["aniuv"], [1, 1])
                self.assertEqual(model["animap"][0]["en"], 1)
                if mid != gm.QUEST_ITEM_MODEL:
                    self.assertLess(model["scale"], self.models["EP361"]["scale"])
                else:
                    self.assertGreater(model["scale"], self.models["EP361"]["scale"])
                image = Path(gm.PROJ) / "resource" / model["pic3d"].split("/resource/")[1]
                self.assertTrue(image.is_file())
                self.assertEqual(Image.open(image).size, (128, 128))
        self.assertIn("countItems( itemid, false)", self.plugin)
        self.assertIn("reduceItemID( itemid, 1)", self.plugin)
        self.assertIn("legacy quest pickup already recorded", self.plugin)


if __name__ == "__main__":
    unittest.main()
