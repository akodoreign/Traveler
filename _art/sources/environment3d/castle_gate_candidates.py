"""Prepare scoped castle gate candidates without changing an active stage or index."""

import builtins
import io
import json
from collections import deque
from pathlib import Path
import sys
from types import ModuleType

import numpy as np

from kensu_worlds import with_world_patch


GROUPS = {"narrows": ("M410",), "hiruma": ("M461", "M462"), "kamen": ("M362",)}

# Coordinates in the padded world grid, matching the published .bw files.
# Each fill is x, y, z, width, height, depth, and a generator material name.
NARROWS = (
    (122, 4, 22, 2, 10, 2, "STONEW"),
    (128, 4, 22, 2, 10, 2, "STONEW"),
    (120, 4, 19, 2, 8, 4, "STONEW"),
    (130, 4, 19, 2, 8, 4, "STONEW"),
    (124, 14, 18, 4, 3, 2, "STONEW"),
    (123, 17, 18, 6, 1, 3, "ROOF"),
)
HIRUMA = {
    "M461": (156, 26, 31),
    "M462": (142, 24, 29),
}
KAMEN = (
    (132, 4, 0, 2, 7, 19, "STONEW"),
    (132, 4, 24, 2, 7, 36, "STONEW"),
    (132, 11, 0, 2, 1, 19, "ROOF"),
    (132, 11, 24, 2, 1, 36, "ROOF"),
    (133, 10, 19, 1, 5, 5, "STONEW"),
    (133, 15, 18, 2, 1, 7, "ROOF"),
)


def hiruma_fills(mid, depth):
    """Low battered curtain beside the original open ruin aperture."""
    x, opening, far = HIRUMA[mid]
    spans = ((0, opening), (far, depth))
    pieces = [(x, 4, z, 2, 7, stop-z, "STONEW") for z, stop in spans]
    for z, stop in spans:
        for start in range(z, stop, 4):
            top = 1 + ((start * 5 + x) % 3)
            run = min(3, stop-start)
            pieces.append((x, 11, start, 2, top, run, "STONEW"))
    return tuple(pieces)


def _fills(mid):
    if mid == "M410":
        return NARROWS
    if mid == "M362":
        return KAMEN
    return hiruma_fills(mid, {"M461": 56, "M462": 52}[mid])


def _read_generator(repo):
    """Keep the encounter ladder computation intact while discarding its cache write."""
    source = repo/"tools/gen_maps.py"
    cache = source.with_name("_ladder_foes.json")

    def read_only_open(file, mode="r", *args, **kwargs):
        if file == str(cache) and mode == "w":
            return io.StringIO()
        return builtins.open(file, mode, *args, **kwargs)

    generator = ModuleType("gen_maps")
    generator.__file__ = str(source)
    generator.open = read_only_open
    sys.modules["gen_maps"] = generator
    sys.path.insert(0, str(source.parent))
    exec(compile(source.read_bytes(), str(source), "exec"), generator.__dict__)
    return generator


def _fragment(group, function):
    blueprint = {mid: _fills(mid) for mid in GROUPS[group]}
    name = function.upper()
    return f"""
{name} = {blueprint!r}


def {function}(m):
    for x, y, z, w, h, d, material in {name}[m.mid]:
        assert 0 <= x < x+w <= m.w and 0 <= z < z+d <= m.d, (m.mid, x, z)
        tile = STONEW if material == "STONEW" else ROOF
        fill(m, x, y, z, w, h, d, tile)
"""


def variant(repo, group):
    """Return a stage_worlds-compatible version, with no event rewrites."""
    ids = GROUPS[group]
    function = f"rebuild_{group}_gate_curtains"
    _read_generator(repo)
    return with_world_patch(repo, ids, function, _fragment(group, function))


def _ground_access(gm, world):
    """Approximate low approaches while retaining real overhead apertures."""
    ground = world.hgt.astype(int)
    clear = ((world.blk & 31) != 8) & (world.blk != 0)
    for x, z in world.walls:
        if 0 <= x < world.w and 0 <= z < world.d:
            clear[z, x] = False
    for obj in world.objs:
        if obj["t"] != "fill" or obj["blk"] == gm.VOID:
            continue
        left, south, grade = (obj[axis] for axis in ("x", "z", "y"))
        x = slice(max(0, left), min(world.w, left+obj["w"]))
        z = slice(max(0, south), min(world.d, south+obj["d"]))
        if x.start >= x.stop or z.start >= z.stop:
            continue
        live_grade = ground[z, x]
        # Four blocks (2 m) of clearance above the local walking floor.
        clears = (grade >= live_grade+5) | (grade+obj["h"] <= live_grade+1)
        clear[z, x] &= clears
    return ground, clear


def _reach(ground, clear, start):
    todo, seen = deque([start]), {start}
    assert clear[start[1], start[0]], start
    while todo:
        x, z = todo.popleft()
        for x2, z2 in ((x+1,z), (x-1,z), (x,z+1), (x,z-1)):
            dst = (x2, z2)
            if not (0 <= x2 < ground.shape[1] and 0 <= z2 < ground.shape[0]):
                continue
            if dst not in seen and clear[z2, x2] and abs(ground[z, x]-ground[z2, x2]) <= 2:
                seen.add(dst)
                todo.append(dst)
    return seen


def validate(repo, group):
    """Verify event equality and low-floor reachability in both gate states."""
    _, old, candidate, _, _ = variant(repo, group)
    report = {}
    for mid in GROUPS[group]:
        first, previous_events = old.make(mid)
        world, new_events = candidate.make(mid)
        assert previous_events.ev == new_events.ev
        assert np.array_equal(first.hgt, world.hgt) and np.array_equal(first.blk, world.blk)
        ground, clear = _ground_access(candidate, world)
        if mid == "M410":
            start, target = (126, 14), (126, 20)
            assert (126, 18) in _reach(ground, clear, target)
            assert start in _reach(ground, clear, target)
            assert target in _reach(ground, clear, start)
            locked = clear.copy()
            locked[18, 124:128] = False
            assert target not in _reach(ground, locked, start)
            # Check a player starting at either flank, rather than only in the lane.
            for flank in ((119, 20), (132, 20)):
                assert target not in _reach(ground, locked, flank)
            report[mid] = {"open": True, "closed": True, "return_landing": [126,18],
                           "unchanged_events": len(new_events.ev)}
        elif mid == "M362":
            start, return_landing = (128,21), (134,21)
            target = (162,30)
            assert target in _reach(ground, clear, start)
            assert start in _reach(ground, clear, return_landing)
            locked = clear.copy()
            locked[19:24,132] = False
            assert target not in _reach(ground, locked, start)
            assert (130,21) in _reach(ground, locked, start)
            report[mid] = {"open": True, "closed": True, "return_landing": list(return_landing),
                           "unchanged_events": len(new_events.ev)}
        else:
            x, low, high = HIRUMA[mid]
            z = (low+high)//2
            start, target = (x-5, z), (x+4, z)
            assert target in _reach(ground, clear, start)
            assert start in _reach(ground, clear, target)
            sealed = clear.copy()
            sealed[low:high, x] = False
            assert target not in _reach(ground, sealed, start)
            report[mid] = {"only_crossing": [x, low, high-1],
                           "unchanged_events": len(new_events.ev)}
    return report


def build_assets(repo, group, output):
    """Write new meshes and row patches into an isolated output directory."""
    import export_coast
    from build_hoshi_stall import box
    from export_coast import Geometry, export
    from shutil import copyfile

    validate(repo, group)
    prod = repo/"_tools/rpgcobo-tool/project/resource/native_environment"
    live = json.loads((prod/"index.json").read_bytes())
    output.mkdir(parents=True, exist_ok=True)
    (output/"tex").mkdir(exist_ok=True)
    maps = {
        "iuchi_light_stone": ("iuchi_light_stone.png", .94),
        "iuchi_indigo": ("iuchi_indigo.png", .89),
        "iuchi_beam": ("iuchi_beam.png", .86),
        "iuchi_iron": ("iuchi_iron.png", .90),
        "hiruma_ishi": ("hiruma_ishi.png", .92),
        "market_stone": ("kamen_market_stone.png", .90),
        "market_trim": ("kamen_market_trim.png", .84),
        "market_tile": ("kamen_market_tile.png", .83),
    }
    palettes = {
        "narrows": ("iuchi_light_stone", "iuchi_indigo", "iuchi_beam", "iuchi_iron"),
        "hiruma": ("hiruma_ishi",),
        "kamen": ("market_stone", "market_tile", "market_trim", "iuchi_iron"),
    }
    required = palettes[group]
    for key in required:
        name, _ = maps[key]
        copyfile(prod/"tex"/name, output/"tex"/name)
    rows = {}
    before_stage = export_coast.STAGE
    export_coast.STAGE = output
    try:
        for mid in GROUPS[group]:
            additions = _fills(mid)
            stone = required[0]
            masonry = Geometry()
            for x, y, z, w, h, d, material in additions:
                # The fitted skin covers the underlying native block edges.
                # Keep the two axial walls out of the open corridor.
                box(masonry, (x*.5-.016, z*.5-.018, y*.5),
                    (w*.5+.032, d*.5+.036, h*.5+.021),
                    stone if material == "STONEW" else required[1])
            name = f"{mid.lower()}_curtain_gate_skin"
            export(name, masonry, maps)
            row = live[mid]
            row["placements"].append([name, 0., 0., 0., 1., 0.])
            rows[mid] = row
        if group == "narrows":
            name = "m410_lifting_portcullis"
            grate = Geometry()
            for i in range(7):
                x = .052+i*.302
                box(grate, (x, -.049, .20), (.080, .098, 2.75), "iuchi_beam")
                box(grate, (x+.011, -.055, .043), (.058, .110, .20), "iuchi_iron")
            for y in (.37, 1.12, 1.87, 2.62, 2.90):
                box(grate, (.018, -.070, y), (1.974, .139, .083), "iuchi_iron")
            export(name, grate, maps)
            row = rows["M410"]
            doors = row["doors"]
            assert len(doors) == 1 and doors[0]["event"] == 2
            frame = doors.pop()
            row["placements"].append([frame["models"][0], frame["x"], frame["y"], frame["z"],1.,0.])
            row["portcullises"] = [{"model": name, "x": 62.0, "y": 2.02, "z": 9.07,
                                     "event": 2,"lift": 2.90,"axis": "x","yaw": 0.0,
                                     "blockX": 124,"blockZ": 18,"width": 4,"blockY": 4,"blockHeight": 6}]
        elif group == "kamen":
            name = "m362_temple_portcullis"
            grate = Geometry()
            for i in range(8):
                z = .053+i*.330
                box(grate, (-.046, z, .208), (.092, .097, 2.66), "market_trim")
                box(grate, (-.058, z+.016, .043), (.115, .066, .195), "iuchi_iron")
            for y in (.38, 1.18, 1.98, 2.78):
                box(grate, (-.066, .025, y), (.131, 2.433, .090), "iuchi_iron")
            export(name, grate, maps)
            guide = Geometry()
            for z in (-.12,2.46):
                box(guide, (-.152,z,2.22), (.304,.172,3.86), "market_trim")
                for y in (2.57,4.11,5.56):
                    box(guide, (-.19,z-.026,y), (.38,.22,.077), "iuchi_iron")
            box(guide, (-.20,-.175,5.98), (.40,2.87,.13), "market_trim")
            box(guide, (-.24,-.20,6.12), (.48,2.92,.09), "market_tile")
            export("m362_temple_portcullis_guide", guide, maps)
            rows["M362"]["placements"].append(["m362_temple_portcullis_guide",66.12,2.02,9.50,1.,0.])
            rows["M362"]["portcullises"] = [{
                "model": name, "x": 66.12, "y": 2.02, "z": 9.50, "event": 90,
                "lift": 2.90, "axis": "z", "yaw": 0.0, "blockX": 132, "blockZ": 19,
                "width": 5, "blockY": 4, "blockHeight": 6,
            }]
    finally:
        export_coast.STAGE = before_stage
    (output/"rows.json").write_text(json.dumps(rows,indent=2),encoding="utf8")
    return rows


if __name__ == "__main__":
    repo, group = Path(sys.argv[1]).resolve(), sys.argv[2]
    if len(sys.argv)>3:
        build_assets(repo, group, Path(sys.argv[3]).resolve())
    print(json.dumps(validate(repo, group), indent=2))
