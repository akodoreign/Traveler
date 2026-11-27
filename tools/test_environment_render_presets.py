import json
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool" / "project"


class EnvironmentRenderPresetTests(unittest.TestCase):
    def test_environment_presets_exist(self):
        settings = json.loads((PROJECT / "resource" / "renderset.json").read_bytes())
        presets = {item["id"] for item in settings["rendersets"]}
        maps = json.loads((PROJECT / "resource" / "native_environment" / "index.json").read_bytes())
        missing = {}
        for map_id, row in maps.items():
            for variant in (row, row.get("siege", {})):
                preset = variant.get("renderPreset")
                if preset and preset not in presets:
                    missing.setdefault(preset, []).append(map_id)
        self.assertEqual(missing, {})


if __name__ == "__main__":
    unittest.main()
