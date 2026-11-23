"""Read the registered worlds and identify surviving stepped A-frame tents."""
import argparse
import builtins
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from types import FunctionType, ModuleType

HERE = Path(__file__).resolve().parent
INDEX = "resource/native_environment/index.json"
CATALOG = "data/map.json"


@dataclass(frozen=True)
class StockTent:
    x: int
    z: int
    y: int
    width: int
    depth: int
    pieces: tuple
    present: tuple

    def placements(self):
        # Keep the Gonta south opening and scale both parts uniformly from
        # the same pivot. The standard six-by-five tent keeps its authored
        # size and flap pose; small ones get more clearance at the path.
        scale = min(self.width / 6, self.depth / 5)
        if self.width >= 8 and self.depth >= 6:
            scale = min(self.width / 6, self.depth / 5)
        scale = round(scale, 5)
        front = self.z * 0.5
        x = self.x * 0.5 + self.width * 0.25
        y = self.y * 0.5
        return [
            ["quarry_tent", x, y, round(front + 1.25*scale, 5), scale, 0.0],
            ["quarry_tent_flap", round(x - .13*scale, 5), round(y + 1.43*scale, 5),
             round(front + .032*scale, 5), scale, .055],
        ]

    def walls(self):
        # Equivalent to the Gonta quarry map: two front post cells and the
        # rear edge. Snap to the actual width if the fitted model is narrower
        # than the old pad. Return world block cells, already padded.
        canopy, _ = self.placements()
        _, x, _, z, s, _ = canopy
        left, right = int((x - 1.48*s)*2), int((x + 1.47*s)*2)
        left, right = max(left, self.x), min(right, self.x+self.width-1)
        front = self.z
        back = self.z + self.depth - 1
        return [(left, front), (right, front), *((p, back) for p in range(left, right+1))]


def load_generator(repo, *, raw_castles=False):
    source = repo / "tools/gen_maps.py"
    sys.path.insert(0, str(source.parent))
    code = source.read_bytes()
    module = ModuleType("_tent_audit_maps")
    module.__file__ = str(source)
    # The game generator emits a deterministic ladder file during import.
    # Keep that scratch side effect out of the working tree.
    def local_open(file, mode="r", *args, **kwargs):
        if any(flag in mode for flag in "wax+"):
            dest = Path(file)
            if dest.name != "_ladder_foes.json":
                raise RuntimeError(f"Unexpected generator write {dest}")
            file = HERE / "audit-ladder-foes.json"
        return builtins.open(file, mode, *args, **kwargs)
    module.open = local_open
    sys.modules[module.__name__] = module
    sys.modules["gen_maps"] = module
    exec(compile(code, str(source), "exec"), vars(module))
    if raw_castles and hasattr(module, "_CLAN_CASTLE_ART"):
        module._CLAN_CASTLE_ART = {}

    original = module.tent
    def record_tent(world, x, z, w=6, d=5):
        start = len(world.objs)
        original(world, x, z, w, d)
        if not hasattr(world, "audit_tents"):
            world.audit_tents = []
        world.audit_tents.append((w, d, tuple(world.objs[start:])))
    module.tent = record_tent
    return module


def raw_tents(world):
    survivors = {id(piece) for piece in world.objs}
    matches = []
    for w, d, pieces in getattr(world, "audit_tents", []):
        present = tuple(o for o in pieces if id(o) in survivors)
        base = pieces[0]
        matches.append(StockTent(base["x"], base["z"], base["y"], w, d, pieces, present))
    return matches


def reference_parts(row):
    return sorted({p[0] for p in row.get("placements", []) if any(
        key in p[0] for key in ("tent", "canvas", "shelter", "awning")
    )})


def serialize(tent):
    return {
        "base": [tent.x, tent.y, tent.z],
        "footprint": [tent.width, tent.depth],
        "stock_pieces": len(tent.pieces),
        "surviving_stock_pieces": len(tent.present),
        "staged_native": tent.placements(),
        "rear_and_poles": tent.walls(),
    }


def calls_tent(fn, module, seen):
    if not isinstance(fn,FunctionType) or fn.__module__!=module.__name__ or fn in seen:
        return False
    seen.add(fn)
    names=fn.__code__.co_names
    if "tent" in names:
        return True
    return any(calls_tent(vars(module).get(name),module,seen) for name in names)


def scan(repo, entire_catalog=False):
    game = repo / "_tools/rpgcobo-tool/project"
    registered = json.loads((game / CATALOG).read_bytes())
    native = json.loads((game / INDEX).read_bytes())
    gm = load_generator(repo)
    result = {}
    # Widen the audit to every builder and both registered battle variants and
    # auto-generated interiors. Stock tent objects are identified by identity
    # after all the map-specific removals and coordinate padding have run.
    maps=sorted(set(gm.MAPS) | set(gm.BATTLE_SPECS) | set(gm.AUTO_INTERIOR_PARENT))
    total_maps=len(maps)
    if not entire_catalog:
        builders={**gm.BATTLE_SPECS,**gm.MAPS}
        maps=[mid for mid in maps if calls_tent(builders.get(mid),gm,set())]
    errors = {}
    for mid in maps:
        try:
            world, _ = gm.make(mid)
        except Exception as exc:
            errors[mid] = str(exc)
            continue
        matches = raw_tents(world)
        if not matches:
            continue
        result[mid] = {
            "name": registered.get(mid, {}).get("name", world.name),
            "registered": mid in registered,
            "native_terrain": native.get(mid, {}).get("terrain"),
            "existing_tent_keys": reference_parts(native.get(mid, {})),
            "stock_sites": [serialize(tent) for tent in matches],
        }
    data = {
        "registered_builder_candidates": total_maps,
        "generated_maps_checked": len(maps),
        "filtered_by_stock_tent_call": not entire_catalog,
        "failures": errors,
        "counts": dict(Counter(
            "solid_stock" if t["surviving_stock_pieces"] == t["stock_pieces"] else
            "partial_stock" if t["surviving_stock_pieces"] else "already_removed"
            for r in result.values() for t in r["stock_sites"]
        )),
        "maps": result,
    }
    name="world-tent-inventory-full.json" if entire_catalog else "world-tent-inventory.json"
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n", "utf-8")
    for mid, row in result.items():
        print(mid, row["name"], [t["surviving_stock_pieces"] for t in row["stock_sites"]], row["existing_tent_keys"])
    print("MAPS", len(maps), "ERRORS", errors)
    print("CANDIDATES", data["counts"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("--entire-catalog",action="store_true")
    args = parser.parse_args()
    scan(args.repo.resolve(),args.entire_catalog)

