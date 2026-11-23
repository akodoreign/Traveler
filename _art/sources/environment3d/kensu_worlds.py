"""Compile the Hisatu Kensu approach with its stock trees and lamps removed."""

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

from shadowlands_march_worlds import compile_worlds, overwrite


HERE = Path(__file__).resolve().parent
MAPS = ("M359", "M360", "M361", "M865")
MARKET_MAPS = ("M362", "M364", "M866")


def with_world_patch(repo, ids, name, fragment, *, uses_events=False):
    source = repo / "tools/gen_maps.py"
    sys.path.insert(0, str(source.parent))
    import gen_maps

    raw = source.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode().replace("\r\n", "\n")
    args = "m, ev" if uses_events else "m"
    if f"def {name}({args}):\n" not in text:
        start = text.index("def make(i):")
        end = text.index("\n    return m, ev", start)
        text = text[:end] + f"\n    if i in {ids!r}:\n        {name}({args})" + text[end:]
        text = text[:start] + fragment.strip() + "\n\n\n" + text[start:]
    updated = text.replace("\n", eol).encode()
    candidate = ModuleType(name + "_candidate")
    candidate.__dict__.update({key: val for key, val in vars(gen_maps).items() if key != "__name__"})
    sys.modules[candidate.__name__] = candidate
    exec(compile(text, str(source), "exec"), candidate.__dict__)
    return source, gen_maps, candidate, raw, updated


def variants(repo, city=False):
    if not city:
        return with_world_patch(repo, MAPS, "rebuild_kensu_approach", '''def rebuild_kensu_approach(m):
    # Replace the catalog trees and street lamps with the new environment placements.
    old_fixtures = {(2,LAMP_STREET),(20,TREE_S),(20,TREE_M),(20,TREE_L)}
    m.objs = [item for item in m.objs
              if item["t"] != "fb" or (item["fbtype"],item["fbparam"]) not in old_fixtures]
''')
    return with_world_patch(repo, MARKET_MAPS, "rebuild_kamen_market", '''def rebuild_kamen_market(m):
    # The new timber stalls leave the old merchant footpaths and shop events intact.
    stall_blocks = {(x + PAD_X, z + PAD_BOTTOM, y)
                    for x in range(40, 92, 9) for y, z in ((4, 24), (7, 23))}
    m.objs = [item for item in m.objs if not (
        item["t"] == "fb" and (item["fbtype"] == 20 and item["fbparam"] in (TREE_S,TREE_M,TREE_L)
                                or (item["fbtype"],item["fbparam"]) == (2,LAMP_STREET))
        or m.mid == "M364" and item["t"] == "fill"
        and (item["x"],item["z"],item["y"]) in stall_blocks
    )]
''')


def stage_worlds(repo, profile, publish, maps, family, version, terrain_only=(), *, positions=None):
    source, old, candidate, raw, updated = version
    candidate.JOBDIR = str(profile / "tmp/rt_mapgen")
    audit = {}
    jobs = []
    for mid in maps:
        before, before_events = old.make(mid)
        world, events = candidate.make(mid)
        expected = before_events.ev if before_events else None
        for key, pos in (positions or {}).get(mid, {}).items():
            assert expected[key]["role"] in ("portal", "custom")
            expected[key] = {**expected[key], "pos": pos}
        assert expected == (events.ev if events else None)
        assert candidate.np.array_equal(before.blk, world.blk)
        assert candidate.np.array_equal(before.hgt, world.hgt)
        removed = len(before.objs) - len(world.objs)
        assert removed > 0 or mid in terrain_only or raw == updated, (mid, removed)
        count_key = "removed_stock_fixtures" if removed >= 0 else "net_new_fixtures"
        audit[mid] = {count_key: abs(removed), "events_preserved": len(events.ev) if events else 0}
        if mid in (positions or {}):
            audit[mid]["event_positions_updated"] = positions[mid]
        row = world.write()
        row["out"] = f"tmp/rt_mapgen/{mid}_{family}_candidate.bw"
        jobs.append(row)

    receipt = HERE / f"{family}-worlds.json"
    worlds = {mid: Path("project/data/mapdata") / (mid + ".bw") for mid in maps}
    catalog = (repo / "_tools/rpgcobo-tool" if publish else profile) / "project/data/map.json"
    catalog_update = None
    if positions:
        original_catalog = catalog.read_bytes()
        rows = json.loads(original_catalog)
        for mid, changes in positions.items():
            for key, pos in changes.items():
                rows[mid]["event"][key]["pos"] = pos
        eol = b"\r\n" if b"\r\n" in original_catalog else b"\n"
        catalog_update = json.dumps(rows, ensure_ascii=False, indent="\t").encode().replace(b"\n", eol)
    if not publish:
        compile_worlds(profile, jobs, stem=family)
        if catalog_update is not None:
            assert catalog.read_bytes() == original_catalog
            overwrite(catalog, catalog_update)
        for mid, file in worlds.items():
            audit[mid]["sha256"] = sha256((profile / file).read_bytes()).hexdigest()
        receipt.write_text(json.dumps(audit, indent=2), encoding="utf8")
    else:
        expected = json.loads(receipt.read_bytes())
        items = {}
        for mid, file in worlds.items():
            content = (profile / file).read_bytes()
            assert sha256(content).hexdigest() == expected[mid]["sha256"]
            if mid in (positions or {}):
                assert expected[mid]["event_positions_updated"] == positions[mid]
            items[repo / "_tools/rpgcobo-tool" / file] = content
        assert source.read_bytes() == raw
        items[source] = updated
        if catalog_update is not None:
            assert catalog.read_bytes() == original_catalog
            items[catalog] = catalog_update
        prior = {file: file.read_bytes() for file in items}
        attempted = []
        try:
            for file, content in items.items():
                attempted.append(file)
                overwrite(file, content)
        except BaseException:
            for file in reversed(attempted):
                overwrite(file, prior[file])
            raise
    print(audit)


def main(repo, profile, publish, city=False):
    maps = MARKET_MAPS if city else MAPS
    family = "kamen-market" if city else "kensu-approach"
    stage_worlds(repo, profile, publish, maps, family, variants(repo, city), ("M866",))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(),
         "--publish" in sys.argv[3:], "--city" in sys.argv[3:])
