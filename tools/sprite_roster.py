"""Inventory game sprite sheets without treating an existing upscale as a completed redraw."""
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOURCE = ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"
NON_ACTOR_MEMOS = ("decoration", "prop ", "quest marker", "quest marker/pickup",
                   "world map", "boss intro banner")


def inventory(resource=RESOURCE):
    models = json.loads((resource / "enemy_pic.json").read_text(encoding="utf-8"))
    sheets = {}
    for eid, entry in models.items():
        if not isinstance(entry, dict) or not entry.get("pic3d"):
            continue
        memo = entry.get("memo", "")
        if memo.startswith(NON_ACTOR_MEMOS):
            continue
        relative = entry["pic3d"].split("/resource/", 1)[-1]
        path = resource / relative
        key = path.stem
        if key.startswith("trav_"):
            group = "traveler_variant" if "__" in key else "traveler"
        elif key.startswith("side_"):
            group = "cast_companion_hireable_npc"
        elif key.startswith("npc_"):
            group = "nonhuman_npc"
        else:
            group = "foe"
        record = sheets.setdefault(key, {
            "key": key, "group": group, "model_ids": [], "names": [],
            "resource_paths": [], "required_animations": [], "source_memos": [],
            "state": "pending_redraw",
        })
        record["model_ids"].append(eid)
        name = entry.get("name", key)
        if isinstance(name, dict):
            name = name.get("en", key)
        for field, value in (("names", name), ("resource_paths", relative), ("source_memos", memo)):
            if value not in record[field]:
                record[field].append(value)
        for anim in entry.get("animap", []):
            if anim["id"] not in record["required_animations"]:
                record["required_animations"].append(anim["id"])
        if not path.is_file():
            raise FileNotFoundError(f"{eid}: registered sprite is missing: {path}")
    return list(sheets.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = inventory()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sheets": len(records), "groups": Counter(r["group"] for r in records),
                      "model_ids": sum(len(r["model_ids"]) for r in records)}, indent=2))


if __name__ == "__main__":
    main()
