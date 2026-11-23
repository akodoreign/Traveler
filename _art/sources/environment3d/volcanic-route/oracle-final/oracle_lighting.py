"""Stage and verify the Oracle route's localized daylight and dawn color."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

RENDER = Path("project/resource/renderset.json")
CATALOG = Path("project/data/map.json")
PRESETS = {
    "M442": ("rt_hd2d_night", "rt_hd2d_oracle_dawn"),
    "M443": ("rt_hd2d_field", "rt_hd2d_oracle_day"),
    "M896": ("rt_hd2d_battle", "rt_hd2d_oracle_arena"),
}


def rgba(r, g, b, a=255):
    argb = (r << 24) | (g << 16) | (b << 8) | a
    return argb - (1 << 32) if argb >= 1 << 31 else argb


def lighting_pack(raw):
    text = raw.decode("utf-8")
    data = json.loads(text)
    by_id = {item["id"]: item for item in data["rendersets"]}
    revised = []
    for mid, (original, name) in PRESETS.items():
        entry = deepcopy(by_id[original])
        dawn = mid == "M442"
        key = entry["envlights"][0]
        key.update(head=-38, pitch=51, power=475 if dawn else 1290,
                   color=rgba(128, 149, 240) if dawn else rgba(244, 231, 214),
                   scolor=rgba(128, 149, 240) if dawn else rgba(244, 231, 214))
        key["shadow"].update(shadowdens=.41, shadowsoft=.40)
        entry["ibl"].update(iblcolor=rgba(106, 141, 246), ibldiff=435 if dawn else 555, iblspec=85)
        entry["fog"].update(zoffs=20.0, density=.011 if dawn else .0028,
                            color=rgba(57, 69, 127, 99))
        entry["postfx"].update(bloompow=.11, bloomthrs=.9)
        entry["id"] = name
        entry["name"] = {"en": "Oracle Basalt " + ("Dawn" if dawn else "Daylight")}
        revised.append(entry)
    if all(by_id.get(row["id"]) == row for row in revised):
        return raw
    assert not any(row["id"] in by_id for row in revised), "Oracle render settings already differ"
    opening = '"rendersets": ['
    assert text.count(opening) == 1
    lines = ",\n".join("\n".join("\t\t" + line for line in json.dumps(row, indent="\t").splitlines()) for row in revised)
    updated = text.replace(opening, opening + "\n" + lines + ",", 1)
    assert json.loads(updated)["rendersets"] == revised + data["rendersets"]
    return updated.encode("utf-8")


def replace_settings(catalog, production):
    for mid, (prior, selected) in PRESETS.items():
        current = production[mid]
        assert current["rsetid"] in (prior, selected), mid
        catalog[mid] = {**current, "rsetid": selected}
    return catalog


def stage_lighting(engine, profile):
    catalog_path = profile / CATALOG
    catalog = json.loads(catalog_path.read_bytes())
    production = json.loads((engine / CATALOG).read_bytes())
    catalog = replace_settings(catalog, production)
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    (profile / RENDER).write_bytes(lighting_pack((engine / RENDER).read_bytes()))


def source_presets(content):
    night = b'"M442": "rt_hd2d_night", "M895": "rt_hd2d_night"'
    day = b'"M442": "rt_hd2d_oracle_dawn", "M443": "rt_hd2d_oracle_day", "M895": "rt_hd2d_night"'
    fight = b'"M896": "rt_hd2d_battle"})'
    revised = b'"M896": "rt_hd2d_oracle_arena"})'
    if day in content and revised in content:
        return content
    assert content.count(night) == content.count(fight) == 1
    return content.replace(night, day).replace(fight, revised)


def publish_route(repo, profile):
    root = Path(__file__).resolve().parent
    work_root = root.parents[1]
    sys.path.insert(0, str(work_root / "coast-kit" if (work_root / "coast-kit").is_dir() else work_root))
    from publish_verified_visual_maps import plan, publish, require

    rows, before, updated, additions = plan(repo, profile, root / "oracle-volcanic-receipt.json", PRESETS)
    require(rows.keys() == PRESETS.keys(), "Lighting scope and verified route scope differ")
    engine = repo / "_tools/rpgcobo-tool"
    before[engine / RENDER] = (engine / RENDER).read_bytes()
    updated[engine / RENDER] = lighting_pack(before[engine / RENDER])
    require(updated[engine / RENDER] == (profile / RENDER).read_bytes(), "Reviewed render resources differ")
    source = repo / "tools/gen_maps.py"
    before[source] = source.read_bytes()
    updated[source] = source_presets(before[source])
    compile(updated[source], str(source), "exec")
    publish(before, updated, additions)
    print(f"Published {', '.join(rows)} and their localized render settings")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("stage", "publish"))
    parser.add_argument("repo", type=Path)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    repo, profile = args.repo.resolve(), args.profile.resolve()
    if profile == (repo / "_tools/rpgcobo-tool").resolve():
        parser.error("The review profile must differ from the live engine")
    if args.action == "stage":
        stage_lighting(repo / "_tools/rpgcobo-tool", profile)
    else:
        publish_route(repo, profile)
