"""Town and island districts, errands, docks and reciprocal route regression checks.

Run: py -3.12 -E -W ignore::ResourceWarning -m unittest discover -s tools -p test_settlements.py
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gen_maps as gm
from test_castles import flood, walkable


class InteriorDoorwayTests(unittest.TestCase):
    def test_exit_fires_at_threshold_without_catching_arrivals(self):
        maps = json.loads((Path(gm.PROJ) / "data" / "map.json").read_text(encoding="utf-8"))
        for mid in ("M111", "M142", "M206", gm.TOWN_WARDS[0]["room"]):
            with self.subTest(map=mid):
                _, events = gm.make(mid)
                generated = events.ev["#1#"]
                shipped = maps[mid]["event"]["#1#"]
                self.assertEqual(shipped["mdl"]["r"], generated["mdl"]["r"])
                _, arrival_offset, _, width, _, depth = shipped["mdl"]["r"]
                # A player stopped 0.4 m inside the doorway must fit;
                # one entering from outside must spawn past the trigger.
                self.assertGreater(depth - 0.38, 0.4)
                self.assertLess(depth - 0.38, arrival_offset * 0.5 + 0.5)
                if mid == "M206":
                    self.assertGreater(width - 0.38, 0.75)


class ScorpionRouteTests(unittest.TestCase):
    def test_costume_arts_regenerate_with_tp_costs_and_are_not_sold(self):
        import mitsue_costumes
        project = Path(gm.PROJ) / "data"
        skills = json.loads((project / "skill.json").read_text(encoding="utf-8"))
        generated = json.loads(json.dumps(skills))
        mitsue_costumes.skills(generated)
        for sid in ("S950", "S951", "S952"):
            with self.subTest(skill=sid):
                self.assertEqual(skills[sid], generated[sid])
                self.assertEqual(skills[sid]["consume"], [1, 8])
                self.assertTrue(skills[sid]["addlist"])
        stores = (project / "store.json").read_text(encoding="utf-8")
        armor = json.loads((project / "armor.json").read_text(encoding="utf-8"))
        for aid, item in armor.items():
            if item.get("rt_costume") or item.get("rt_costume_head"):
                with self.subTest(garment=aid):
                    self.assertNotIn(json.dumps(aid), stores)

    def test_teahouse_disguise_has_a_single_mandatory_many_faces_choice(self):
        maps = json.loads((Path(gm.PROJ) / "data" / "map.json").read_text(encoding="utf-8"))
        shipped = maps["M346"]["event"]["#4#"]["page"][1]["cmdblock"][0]["cmdblocks"][0]
        for commands in (gm.S02_SCP1, shipped):
            with self.subTest(scene="generator" if commands is gm.S02_SCP1 else "shipped"):
                disguise = next(index for index, command in enumerate(commands)
                                if command.get("text", "").startswith("Mitsue becomes a teahouse servant"))
                self.assertEqual(commands[disguise - 1], gm.script('::Rokugan.takeDisguise("A181", "A185");'))
                self.assertEqual(commands[disguise - 2],
                                 gm.choices(("Many Faces: become a teahouse servant.", [])))

    def test_governor_retry_is_guaranteed_and_disguise_stays_available_until_the_reveal(self):
        project = Path(gm.PROJ)
        maps = json.loads((project / "data" / "map.json").read_text(encoding="utf-8"))
        pages = maps["M352"]["event"]["#5#"]["page"]

        def page_for(flags):
            return next(page for page in reversed(pages)
                        if all(flags.get(req["lvar"], False) == req["rvar"] for req in page.get("reqs") or []))

        old_failed = {"G848": True}
        retry = page_for(old_failed)
        self.assertEqual(page_for({}), retry)
        choice = next(command for command in retry["cmdblock"] if command["cmd"] == "cmd_choices")
        self.assertEqual(choice["text0"], "Eavesdrop (100%)")
        self.assertIn(gm.setf("W"), choice["cmdblocks"][0])
        self.assertNotIn("Rokugan.roll", json.dumps(choice["cmdblocks"][0]))
        success = next(command for command in choice["cmdblocks"][0] if command["cmd"] == "cmd_if")["cmdblocks"][0]
        self.assertIn(gm.setf("G858"), success)
        self.assertIn(gm.setf("G851", 1, "+="), success)
        self.assertIn('"lvar": "G849", "op": "=", "rvar": true', json.dumps(success))
        repeat = page_for(old_failed | {"G858": True})
        self.assertIn("Many Faces: take the kitchen servant's place.", json.dumps(repeat))
        self.assertNotIn('"lvar": "G851"', json.dumps(repeat))
        revealed = page_for(old_failed | {"G858": True, "G849": True})
        self.assertNotIn("cmd_choices", json.dumps(revealed))
        gvars = json.loads((project / "data" / "gvar.json").read_text(encoding="utf-8"))
        self.assertEqual(gvars["G858"]["defval"], False)
        _, events = gm.make("M352")
        generated = {"M352": {"event": {"#5#": events.ev["#5#"]}}}
        with patch.dict(gm.MAP_PATH, {"M352": "P105"}):
            gm.gesture_pass(generated)
        self.assertEqual(generated["M352"]["event"]["#5#"]["page"], pages)

    def test_story_road_from_bayushi_leads_to_traitors_grove(self):
        project = Path(gm.PROJ)
        maps = json.loads((project / "data" / "map.json").read_text(encoding="utf-8"))
        town, events = gm.make("M347")
        shipped = maps["M347"]["event"]
        east = next(key for key, side in town.edge_out if side == "e")
        portal = shipped[east]
        self.assertEqual(portal["dest"], {"mapid": "M348", "evid": 1})
        self.assertEqual(portal["mdl"], events.ev[east]["mdl"])
        self.assertTrue(any(event.get("dest") == {"mapid": "M347", "evid": 1}
                            for event in maps["M348"]["event"].values()))
        self.assertTrue(any(event.get("dest", {}).get("mapid") == "M477"
                            for key, event in shipped.items() if key != east))
        markers = (project / "plugin" / "rokugan" / "RokuganMarkerData.sk").read_text(encoding="utf-8")
        self.assertIn('["M348", 77.0, 14.0, 0.5, 14.0]', markers)
        self.assertNotIn('["M477", 77.0, 14.0,', markers)
        self.assertIn('M348 = "P105"', markers)

    def test_investigation_marker_targets_match_the_conversations_and_survive_regeneration(self):
        project = Path(gm.PROJ)
        maps = json.loads((project / "data" / "map.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            plugin = Path(temp) / "plugin" / "rokugan"
            plugin.mkdir(parents=True)
            shutil.copyfile(project / "plugin" / "rokugan" / "RokuganJournal.sk", plugin / "RokuganJournal.sk")
            with patch.object(gm, "PROJ", temp), patch.dict(gm.MAP_PATH):
                gm.marker_pass(maps)
            generated = (plugin / "RokuganMarkerData.sk").read_text(encoding="utf-8")
        beats = json.loads(generated.split("::Rokugan.MK_BEATS <- ", 1)[1].split(";", 1)[0])
        shipped = (project / "plugin" / "rokugan" / "RokuganMarkerData.sk").read_text(encoding="utf-8")
        shipped_beats = json.loads(shipped.split("::Rokugan.MK_BEATS <- ", 1)[1].split(";", 1)[0])
        for mid, done in (("M352", "G849"), ("M351", "G850"), ("M352", "G852")):
            with self.subTest(conversation=done):
                event = next(event for event in maps[mid]["event"].values()
                             if json.dumps(gm.setf(done)) in json.dumps(event))
                beat = next(beat for beat in beats if beat[3][0] == [done, "==", False])
                self.assertIn(beat, shipped_beats)
                self.assertEqual(beat[:3], [mid, event["pos"][0] / 2.0, event["pos"][2] / 2.0])
                for prerequisite in (["G845", "==", True], ["G876", "==", True], ["G853", "==", False]):
                    self.assertIn(prerequisite, beat[3])
                if done != "G849":
                    self.assertIn(["G849", "==", True], beat[3])
                    self.assertIn(["G851", "<", 2], beat[3])


class SettlementExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regions = gm.TOWN_WARDS + gm.ISLAND_WARDS
        cls.islets = gm.SEA_ISLETS
        cls.maps = json.loads((Path(gm.PROJ) / "data" / "map.json").read_text(encoding="utf-8"))
        cls.outdoor = {region["mid"]: gm.make(region["mid"]) for region in cls.regions}
        cls.outdoor.update({islet["mid"]: gm.make(islet["mid"]) for islet in cls.islets})

    def test_inventory_and_map_ids_are_complete(self):
        regions = self.regions + self.islets
        mids = [region["mid"] for region in regions]
        rooms = [region["room"] for region in self.regions if region["room"] is not None]
        self.assertEqual(len(mids), 34)
        self.assertEqual(len(mids), len(set(mids)))
        self.assertEqual(len(rooms), len(set(rooms)))
        self.assertEqual(len(set(mids) & set(rooms)), 0)
        self.assertEqual(len(self.regions), 28)
        self.assertEqual(len(self.islets), 6)
        for region in regions:
            with self.subTest(map=region["mid"]):
                self.assertIn(region["mid"], gm.MAPS)
                self.assertGreaterEqual(self.outdoor[region["mid"]][0].w, 120)
                self.assertGreaterEqual(self.outdoor[region["mid"]][0].d, 64)
        for region in gm.TOWN_WARDS:
            self.assertIn(region["room"], gm.MAPS)

    def test_every_town_and_existing_island_has_reciprocal_routes(self):
        for region in self.regions:
            area_mid, (area, area_events) = region["mid"], self.outdoor[region["mid"]]
            for source_index, source in enumerate(region["sources"]):
                with self.subTest(area=area_mid, source=source):
                    source_map, source_events = gm.make(source)
                    trigger = next((event for event in source_events.ev.values()
                                    if event.get("role") == "portal"
                                    and event.get("dest", {}).get("mapid") == area_mid), None)
                    self.assertIsNotNone(trigger, (source, area_mid))
                    radius = trigger["mdl"]["r"]
                    self.assertGreaterEqual(radius[3], 1.5)
                    self.assertGreaterEqual(radius[4], 3.0)
                    # (2026-11-22) the ward opens from the town's edge, beside it, not from a portal mid-town
                    side = region["town_side"][source_index]
                    if side:
                        self.assertIn(side, dict(source_map.exits).values(), (source, "ward not on an edge"))
                        self.assertGreaterEqual(radius[5], 0.5)
                    entry = region["entry"][source_index]
                    access = (entry, source_events.ev["#%d#" % entry])           # the landing other maps arrive at
                    _, wide = walkable(source_map, source_events)
                    x, _, z, _ = access[1]["pos"]
                    self.assertTrue(any(0 <= z + dz < wide.shape[0] and 0 <= x + dx < wide.shape[1]
                                        and wide[z + dz, x + dx]
                                        for dx in range(-2, 3) for dz in range(-2, 3)),
                        (source, area_mid, "new entrance is not on walkable ground"))
                    return_event = next(event for event in area_events.ev.values()
                                         if event.get("role") == "portal"
                                         and event.get("dest", {}).get("mapid") == source
                                         and event.get("dest", {}).get("evid") == access[0])
                    self.assertEqual(return_event["dest"]["mapid"], source)
                    self.assertEqual(return_event["dest"]["evid"], access[0])
                    self.assertGreaterEqual(return_event["mdl"]["r"][5], 1.5)

            if region in gm.TOWN_WARDS:
                inn_mid = region["room"]
                inn, inn_events = gm.make(inn_mid)
                door = next((event for event in area_events.ev.values()
                             if event.get("role") == "portal"
                             and event.get("dest", {}).get("mapid") == inn_mid), None)
                self.assertIsNotNone(door, area_mid)
                self.assertGreaterEqual(door["mdl"]["r"][3], 1.5)
                self.assertEqual(inn_events.ev["#1#"]["dest"]["mapid"], area_mid)
                self.assertGreaterEqual(inn_events.ev["#1#"]["mdl"]["r"][3], 1.5)
                self.assertEqual(inn_events.ev["#1#"]["dest"]["evid"],
                                 next(int(key[1:-1]) for key, event in area_events.ev.items()
                                      if event is door))

    def test_every_new_resident_errand_has_a_giver_and_pickup(self):
        quests = gm.FETCH_QUESTS[-(len(self.regions) + len(self.islets)):]
        self.assertEqual(len(quests), 34)
        self.assertEqual(len({quest[0] for quest in quests}), len(quests))
        for key, title, gmap, *_rest in quests:
            with self.subTest(quest=key):
                self.assertIn(gmap, gm.MAPS)
                settings = gm.FQ_SETTINGS[key]
                self.assertEqual(settings["who"], None)
                self.assertEqual(settings["open"], [])
                self.assertIn(settings["prop"], gm.DECOR_EP)
                events = self.outdoor[gmap][1].ev
                text = json.dumps(events, ensure_ascii=False)
                self.assertIn("Odd job: " + title, text)
                self.assertIn(gm.FQ_FLAGS[key][0], text)
                self.assertIn(gm.FQ_FLAGS[key][1], text)
                taken, found, _done = gm.FQ_FLAGS[key]
                pickup = next(event for event in events.values()
                              if gm.setf(found) in [command for page in event.get("page", [])
                                                    for command in page.get("cmdblock", [])])
                self.assertEqual(pickup["reqs0"], [gm.flag(taken), gm.flag(found, False)])
                self.assertGreaterEqual(pickup["mdl"]["r"][3], 1.5)
                self.assertGreaterEqual(pickup["mdl"]["r"][4], 3.0)
                item_command = {"cmd": "cmd_itemop", "itemid": gm.FQ_ITEM_IDS[key],
                                "op": 0, "num": 1, "LV": 1}
                self.assertTrue(any(item_command in page.get("cmdblock", [])
                                    for page in pickup.get("page", [])))
                self.assertTrue(any(row[3:] == [taken, found]
                                    and row[0] == pickup["pos"][0] / 2.0
                                    and row[2] == pickup["pos"][2] / 2.0
                                    for row in gm.quest_item_records(self.maps)[gmap]))

    def test_all_new_district_paths_are_walkable(self):
        directions = {0: (0, -2), 1: (-2, 0), 2: (0, 2), 3: (2, 0)}
        for mid, (m, ev) in self.outdoor.items():
            with self.subTest(map=mid):
                heights, wide = walkable(m, ev)
                if mid in {islet["mid"] for islet in self.islets}:
                    start = (8 + gm.PAD_X, 15 + gm.PAD_BOTTOM)
                else:
                    landing = ev.ev["#1#"]
                    dx, dz = directions[landing["pos"][3]]
                    start = (landing["pos"][0] + dx, landing["pos"][2] + dz)
                self.assertTrue(wide[start[1], start[0]], (mid, "blocked arrival", start))
                seen = flood(heights, wide, start)
                self.assertGreater(len(seen), 3000, (mid, "district is not fully walkable"))
                for key, event in ev.ev.items():
                    if event.get("role") != "portal":
                        continue
                    x, _, z, _ = event["pos"]
                    self.assertTrue(any((x + dx, z + dz) in seen
                                        for dx in range(-2, 3) for dz in range(-2, 3)),
                                    (mid, key, "unreachable portal"))

    def test_outer_coast_islets_have_two_way_docks(self):
        sea_routes = (("M493", self.islets[:3]), ("M494", self.islets[3:]))
        for sea_mid, islets in sea_routes:
            _, sea_events = gm.make(sea_mid)
            for islet in islets:
                with self.subTest(sea=sea_mid, island=islet["mid"]):
                    landfall = next(event for event in sea_events.ev.values()
                                    if islet["mid"] in json.dumps(event))
                    self.assertGreaterEqual(landfall["mdl"]["r"][3], 2.5)
                    self.assertEqual(landfall["mdl"]["r"][5], 1.0)
                    _, island_events = self.outdoor[islet["mid"]]
                    self.assertIn(sea_mid, json.dumps(island_events.ev))
                    self.assertIn("cmd_mapmove", json.dumps(island_events.ev))

    def test_persisted_routes_preserve_story_event_ids(self):
        project_maps = json.loads((Path(gm.PROJ) / "data" / "map.json").read_text(encoding="utf-8"))
        for region in self.regions:
            for source in region["sources"]:
                with self.subTest(source=source, destination=region["mid"]):
                    source_events = project_maps[source]["event"]
                    # (2026-11-22) the way to the ward is an edge strip; the ward's way back lands on the town's
                    # landing spot, which keeps the id the generator gives it
                    self.assertTrue(any(event.get("role") == "portal"
                                        and event.get("dest", {}).get("mapid") == region["mid"]
                                        for event in source_events.values()), (source, "no way to the ward"))
                    return_event = next(
                        event for event in project_maps[region["mid"]]["event"].values()
                        if event.get("role") == "portal"
                        and event.get("dest", {}).get("mapid") == source)
                    self.assertEqual(return_event["dest"]["evid"],
                                     region["entry"][region["sources"].index(source)])
                    landing = source_events["#%d#" % return_event["dest"]["evid"]]
                    self.assertTrue(landing["role"] == "portal" or any(
                        p.get("memo") == "landing" for p in landing.get("page", [])), (source, "not a landing"))

        # M103's original herbalist event occupied #27 before the new ward entrance was added.
        original = project_maps["M103"]["event"]["#27#"]
        self.assertEqual((original["role"], original["mdlid"]), ("custom", "EP390"))
        self.assertTrue(any(event.get("role") == "portal"
                            and event.get("dest", {}).get("mapid") == "M630"
                            for event in project_maps["M103"]["event"].values()))

        for islet in self.islets:
            with self.subTest(islet=islet["mid"]):
                sea_events = project_maps[islet["sea"]]["event"]
                landfall = next(event for event in sea_events.values()
                                if islet["mid"] in json.dumps(event))
                self.assertEqual(landfall["page"][0]["trigger"], 5)

    def test_phoenix_west_tower_is_on_west_side_and_has_a_visible_door(self):
        courtyard, events = gm.make("M242")
        tower_event_id = gm.DOOR_EV[("M242", "tower")]
        tower_event = events.ev["#%d#" % tower_event_id]
        x, _, z, _ = tower_event["pos"]
        self.assertLess(x, courtyard.w // 2)
        self.assertEqual(tower_event["dest"]["mapid"], "M278")
        self.assertGreaterEqual(tower_event["mdl"]["r"][3], 1.5)
        doorway = [obj for obj in courtyard.objs if obj["t"] == "fill" and obj["blk"] == gm.VOID
                   and obj["x"] <= x < obj["x"] + obj["w"] and obj["z"] == z + 1]
        self.assertTrue(doorway, "the tower portal must sit in a visible ground-floor doorway")
        _, tower_events = gm.make("M278")
        return_event = next(event for event in tower_events.ev.values()
                            if event.get("role") == "portal"
                            and event.get("dest", {}).get("mapid") == "M242")
        self.assertEqual(return_event["dest"]["evid"], tower_event_id)
        self.assertGreaterEqual(return_event["mdl"]["r"][3], 1.5)


if __name__ == "__main__":
    unittest.main()
