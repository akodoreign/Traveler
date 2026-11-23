"""Audit doorway alignment and emit field-scoped candidates for native testing."""

import argparse
from copy import deepcopy
from difflib import unified_diff
import json
from pathlib import Path

from castle_gate_candidates import _read_generator
from kensu_worlds import with_world_patch


HERE = Path(__file__).resolve().parent
NATIVE_INDEX = "_tools/rpgcobo-tool/project/resource/native_environment/index.json"
EVENT_CATALOG = "_tools/rpgcobo-tool/project/data/map.json"

# Event ID, current frame origin in metres, and cut's left edge in authored blocks.
HINGED = {
    "M457": [(79, 20., 39), (None, 29.5, 58)],
    "M351": [(3, 36., 71), (2, 47., 93), (4, 55.5, 110)],
    "M360": [(85, 20., 39), (86, 47.5, 94)],
    "M362": [(2, 20., 39)],
    "M369": [(97, 20., 39), (2, 32.5, 64), (98, 43.5, 86), (99, 50.5, 100)],
    "M375": [(2, 36., 71)],
    "M347": [(94, 25., 49), (95, 32.5, 64), (96, 49., 97)],
}

# Existing event positions and destinations. The new X is the cut midpoint.
PORTALS = {
    "M360": {"#85#": ((39, 4, 24, 0), "M955")},
    "M375": {"#2#": ((71, 4, 25, 0), "M376")},
    "M380": {"#2#": ((86, 7, 24, 0), "M381")},
    "M387": {"#1#": ((39, 4, 25, 0), "M388")},
}

# Published decorative doors, named by their precise current X and Z.
FIXED = {
    "M351": [(23., 12.882, 45), (30., 12.882, 59), (62.5, 13.382, 124)],
    "M360": [(30., 12.882, 59), (39., 12.882, 77)],
    "M362": [(29., 12.882, 57), (37.5, 12.882, 74), (46., 12.882, 91), (54.5, 12.882, 108)],
    "M364": [(18.5, 13.382, 36), (27., 13.382, 53), (65.5, 13.382, 130)],
    "M372": [(19.5, 11.882, 38), (32., 11.882, 63), (43.5, 11.882, 86)],
    "M374": [(18.75, 12.882, 36), (24.75, 12.882, 48), (49.75, 12.882, 98), (54.75, 12.882, 108)],
    "M375": [(18.5, 12.882, 36), (26.5, 12.882, 52), (45.5, 12.882, 90), (53.5, 12.882, 106)],
    "M347": [(17.5, 13.382, 34), (40.5, 13.382, 80)],
    "M349": [(17.5, 13.382, 34), (25., 13.382, 49), (32.5, 13.382, 64),
             (40., 13.382, 79), (47.5, 13.382, 94), (55., 13.382, 109)],
}

# Carry the same anchor corrections into each environment builder on its next run.
# Patch paths are relative to this scratch directory.
BUILDER_EDITS = {
    "build_shinomen_gate.py": (
        ('"event":79,"x":20.0', '"event":79,"x":19.5'),
        ('"event":None,"x":29.5', '"event":None,"x":29.0'),
    ),
    "build_kudo.py": (
        ('["town_door_stoop_half",x,2.,z,1.,0.]', '["town_door_stoop_half",x-.5,2.,z,1.,0.]'),
        ('doors.append({"x":x,', 'doors.append({"x":x-.5,'),
    ),
    "build_kensu_approach.py": (
        ('["town_door_stoop_half", center, 2., front, 1., 0.]',
         '["town_door_stoop_half", center - .5, 2., front, 1., 0.]'),
        ('{"x": (gm.PAD_X + x) * .5, "y": 2.5',
         '{"x": (gm.PAD_X + x - 1) * .5, "y": 2.5'),
    ),
    "build_kamen_market.py": (
        ('["town_door_stoop_half", x, 2., front, 1., 0.]',
         '["town_door_stoop_half", x - .5, 2., front, 1., 0.]', 2),
        ('doors.append({"x": 20.,', 'doors.append({"x": 19.5,'),
    ),
    "build_ojatara.py": (
        ('["town_door_stoop_half",a,2.,b,1.,0.]', '["town_door_stoop_half",a-.5,2.,b,1.,0.]'),
        ('doors.append({"x":a,', 'doors.append({"x":a-.5,'),
        ('(11.5,23.5,73.5,83.5)', '(11,23,73,83)'),
    ),
    "build_scorpion_road.py": (
        ('["town_door_stoop_half",px,2.,pz,1.,0.]', '["town_door_stoop_half",px-.5,2.,pz,1.,0.]'),
        ('doors.append({"x":px,', 'doors.append({"x":px-.5,'),
    ),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def doorway_cut(gm, world, left, threshold, anchor_z, grade):
    """Match the exact two-cell front aperture and both approach grades."""
    matches = [
        obj for obj in world.objs
        if obj["t"] == "fill" and obj["blk"] == gm.VOID
        and obj["x"] == left and obj["y"] == threshold * 2
        and 0 <= obj["z"] - anchor_z * 2 < .28
        and (obj["w"], obj["h"], obj["d"]) == (2, 4, 1)
    ]
    assert len(matches) == 1, (world.mid, left, threshold, anchor_z, matches)
    cut = matches[0]
    floor = [(int(world.hgt[cut["z"] - 1, x]) + 1) / 2 for x in (left, left + 1)]
    assert floor == [grade, grade], (world.mid, left, floor, grade)
    return [cut[axis] for axis in ("x", "y", "z", "w", "h", "d")]


def centered_portal(mid, key, portal, left):
    trigger = tuple(portal["pos"])
    update = PORTALS.get(mid, {}).get(key)
    if update:
        assert trigger == update[0] and portal["dest"]["mapid"] == update[1], (mid, portal)
    else:
        assert trigger[0] == left + 1, (mid, portal, left)
    return [left + 1, *trigger[1:]]


def audit(repo):
    index = read_json(repo / NATIVE_INDEX)
    catalog = read_json(repo / EVENT_CATALOG)
    gm = _read_generator(repo)
    world_ids = sorted(HINGED.keys() | PORTALS.keys() | FIXED.keys())
    worlds = {mid: gm.make(mid)[0] for mid in world_ids}
    hinged, fixed, portal_changes = {}, {}, {}

    for mid, specifications in HINGED.items():
        rows = index[mid]["doors"]
        hinged[mid] = []
        for event, old_x, left in specifications:
            matches = [row for row in rows if row["event"] == event and row["x"] == old_x]
            assert len(matches) == 1, (mid, event, old_x, matches)
            row, = matches
            assert row["stoop"] == "town_door_stoop_half", (mid, row)
            assert old_x == (left + 1) / 2
            cut = doorway_cut(gm, worlds[mid], left, row["y"], row["z"], row["grade"])
            updated = {**row, "x": left / 2}
            centre = updated["x"] + .5
            assert centre == (cut[0] + cut[3] / 2) / 2
            key = f"#{event}#"
            trigger = None if event is None else centered_portal(mid, key, catalog[mid]["event"][key], left)
            hinged[mid].append({
                "before": row, "after": updated, "cutBlocks": cut, "centreMetres": centre,
                "expectedPortalPosition": trigger,
            })

    for mid, specifications in FIXED.items():
        rows = index[mid]["placements"]
        fixed[mid] = []
        for old_x, z, left in specifications:
            cut = doorway_cut(gm, worlds[mid], left, 2.5, z, 2.)
            centre = (cut[0] + cut[3] / 2) / 2
            shut = ["kudo_shut_door", old_x, 2.5, z, 1., 0.]
            step = ["town_door_stoop_half", old_x, 2., z, 1., 0.]
            assert rows.count(shut) == rows.count(step) == 1, (mid, old_x, z)
            replacements = [(step, left / 2)]
            if old_x != centre:
                replacements.append((shut, centre))
            for before, new_x in replacements:
                after = [before[0], new_x, *before[2:]]
                centre_offset = .5 if before[0] == "town_door_stoop_half" else 0.
                assert after[1] + centre_offset == centre
                fixed[mid].append({
                    "before": before, "after": after, "cutBlocks": cut, "centreMetres": centre,
                })

    for mid, specifications in PORTALS.items():
        portal_changes[mid] = {}
        for key, (before, destination) in specifications.items():
            row = catalog[mid]["event"][key]
            assert row["role"] == "portal" and tuple(row["pos"]) == before, (mid, key, row)
            assert row["dest"] == {"mapid": destination, "evid": 1}, (mid, key, row["dest"])
            event = int(key.strip("#"))
            door, = [item for item in index[mid]["doors"] if item["event"] == event]
            cut = doorway_cut(gm, worlds[mid], before[0], door["y"], door["z"], door["grade"])
            after = centered_portal(mid, key, row, cut[0])
            inward = catalog[destination]["event"]["#1#"]
            exits = [
                {"key": exit_key, "pos": exit_row["pos"], "dest": exit_row["dest"]}
                for exit_key, exit_row in catalog[destination]["event"].items()
                if exit_row.get("dest", {}).get("mapid") == mid
            ]
            assert exits, (mid, key, destination)
            portal_changes[mid][key] = {
                "before": list(before), "after": after, "destination": row["dest"],
                "cutBlocks": cut, "centreMetres": after[0] / 2,
                "destinationEntryPos": inward["pos"], "returnExits": exits,
            }
    return {"doors": hinged, "placements": fixed, "events": portal_changes}


def replace_index_field(document, findings, field):
    """Apply one field of exact row substitutions in memory."""
    assert field in ("doors", "placements")
    for mid, replacements in findings[field].items():
        rows = document[mid][field]
        for edit in replacements:
            assert rows.count(edit["before"]) == 1, (mid, field, edit["before"])
            rows[rows.index(edit["before"])] = deepcopy(edit["after"])


def replace_live_positions(catalog, findings):
    """Modify just each portal's position, preserving its installed behavior."""
    for mid, changes in findings["events"].items():
        for key, edit in changes.items():
            event = catalog[mid]["event"][key]
            assert event["role"] == "portal" and event["dest"] == edit["destination"]
            assert event["pos"] == edit["before"], (mid, key, event["pos"])
            event["pos"] = edit["after"].copy()


def variant(repo, findings):
    """Return a gen_maps version with only the four portal positions edited."""
    _read_generator(repo)
    positions = {
        mid: {key: (edit["before"], edit["after"], edit["destination"]) for key, edit in rows.items()}
        for mid, rows in findings["events"].items()
    }
    name = "align_building_door_portals"
    fragment = f"""
CENTRED_BUILDING_PORTALS = {positions!r}


def {name}(m, ev):
    for key, (before, after, destination) in CENTRED_BUILDING_PORTALS[m.mid].items():
        event = ev.ev[key]
        assert event["role"] == "portal" and event["dest"] == destination, (m.mid, key)
        assert event["pos"] in (before, after), (m.mid, key, event["pos"])
        event["pos"] = after.copy()
"""
    return with_world_patch(repo, tuple(positions), name, fragment, uses_events=True)


def verify(repo, findings):
    """Verify scoped merges and ensure the generator candidate changes no geometry."""
    original_index = read_json(repo / NATIVE_INDEX)
    index_after = deepcopy(original_index)
    original_catalog = read_json(repo / EVENT_CATALOG)
    catalog_after = deepcopy(original_catalog)
    for field in ("doors", "placements"):
        replace_index_field(index_after, findings, field)
    replace_live_positions(catalog_after, findings)

    for mid, row in index_after.items():
        for field, value in row.items():
            if mid not in findings.get(field, {}):
                assert value == original_index[mid][field], (mid, field)
    _, old_generator, candidate, _, _ = variant(repo, findings)
    for mid, changes in findings["events"].items():
        old_world, old_events = old_generator.make(mid)
        new_world, new_events = candidate.make(mid)
        assert old_generator.np.array_equal(old_world.blk, new_world.blk)
        assert old_generator.np.array_equal(old_world.hgt, new_world.hgt)
        assert old_world.objs == new_world.objs and old_world.walls == new_world.walls
        expected = deepcopy(old_events.ev)
        for key, edit in changes.items():
            expected[key]["pos"] = edit["after"]
        assert expected == new_events.ev, mid
        for key, row in original_catalog[mid]["event"].items():
            expected_row = dict(row)
            if key in changes:
                expected_row["pos"] = changes[key]["after"]
            assert expected_row == catalog_after[mid]["event"][key], (mid, key)


def builder_patch():
    """Generate a separate persistence patch without editing live builder sources."""
    patch = []
    for name, replacements in BUILDER_EDITS.items():
        original = (HERE / name).read_text(encoding="utf-8")
        edited = original
        for before, after, *count in replacements:
            assert edited.count(before) == (count[0] if count else 1), (name, before)
            edited = edited.replace(before, after)
        compile(edited, name, "exec")
        patch.extend(unified_diff(
            original.splitlines(keepends=True), edited.splitlines(keepends=True),
            f"a/{name}", f"b/{name}",
        ))
    return "".join(patch)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    args = parser.parse_args()
    findings = audit(args.repo.resolve())
    verify(args.repo.resolve(), findings)
    output = HERE / "door-centering-candidate.json"
    output.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    (HERE / "door-centering-builder.patch").write_text(builder_patch(), encoding="utf-8", newline="\n")
    for field, maps in findings.items():
        print(f"{field}: {sum(len(edits) for edits in maps.values())} edits in {len(maps)} maps")
    print(output)


if __name__ == "__main__":
    main()
