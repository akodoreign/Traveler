"""Stage the Shiro Iuchi quarry-tent retrofit for install_clan_castles.py."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

from audit_stock_tents import CATALOG, INDEX, load_generator, raw_tents, serialize

HERE = Path(__file__).resolve().parent
COAST = HERE.parent
GROUP = "iuchi-tents"
sys.path.insert(0, str(COAST))

import build_clan_castles as castles
from export_coast import STAGE, export


def terrain_materials(native_root, model):
    descriptor=(native_root / (model + ".pm")).read_text("utf-8")
    materials={}
    for block in re.findall(r"{([^{}]+)}", descriptor):
        name=re.search(r'name = "([^"]+)"', block)
        texture=re.search(r'texture0 = "tex/([^"]+)"', block)
        roughness=re.search(r'rough = ([\d.]+)', block)
        if name and texture and roughness:
            materials[name[1]]=texture[1],float(roughness[1])
    if not materials:
        raise ValueError(f"No live materials found on {model}")
    return materials


def apply(repo):
    gm=load_generator(repo, raw_castles=True)
    castle=next(c for c in gm.CLAN_CASTLES if c["name"]=="Shiro Iuchi")
    theme=castles.THEMES[castle["name"]]
    game=repo / "_tools/rpgcobo-tool/project"
    published=json.loads((game / INDEX).read_bytes())
    catalog=json.loads((game / CATALOG).read_bytes())
    original_plans=json.loads((repo / "tools/clan_castle_art.json").read_bytes())
    native_root=(game / INDEX).parent
    plans={}
    rows={}
    evidence={}
    for layout,mid in castle["grounds"].items():
        world,events=gm.make(mid)
        tents=raw_tents(world)
        if not tents:
            continue
        assert len(tents)==4 and all(len(t.present)==len(t.pieces)==6 for t in tents), mid
        assert all((t.width,t.depth)==(6,5) for t in tents), mid
        live=published[mid]

        new_plan=deepcopy(original_plans[mid])
        removed=[piece for tent in tents for piece in tent.present]
        assert len({id(o) for o in removed})==len(removed), mid
        new_plan["remove"].extend(obj for obj in removed if obj not in new_plan["remove"])
        new_walls=sorted({cell for tent in tents for cell in tent.walls()}-set(world.walls))
        # An authored event may stand near a tent. Do not assign the new
        # collision over any event anchor, including quest markers.
        event_cells={(p[0],p[2]) for event in catalog[mid]["event"].values() if (p:=event.get("pos"))}
        assert not set(new_walls) & event_cells, (mid, set(new_walls) & event_cells)
        new_plan["walls"]=[list(cell) for cell in new_walls]
        plans[mid]=new_plan

        omit={id(o) for o in removed}
        world.objs=[obj for obj in world.objs if id(obj) not in omit]
        _, land, _, _, _, _=castles.map_row(gm,world,events,theme,layout,catalog[mid])
        native_id=f"{mid.lower()}_iuchi_castle_quarry_tents_v2"
        materials=terrain_materials(native_root,live["terrain"])
        assert set(land.materials)<=materials.keys(), (mid,set(land.materials)-materials.keys())
        for texture in {materials[key][0] for key in land.materials}:
            target=STAGE / "tex" / texture
            live_texture=(native_root / "tex" / texture).read_bytes()
            assert target.is_file() and target.read_bytes()==live_texture, (mid,texture)
        export(native_id,land,materials)
        new_row=deepcopy(live)
        new_row["terrain"]=native_id
        fitted=[p for tent in tents for p in tent.placements()]
        existing=[p for p in live["placements"] if p[0] in {"quarry_tent","quarry_tent_flap"}]
        assert not existing or existing==fitted, mid
        if not existing:
            new_row["placements"].extend(fitted)
        rows[mid]=new_row
        assert {k:v for k,v in new_row.items() if k not in ("terrain","placements")} == {
            k:v for k,v in live.items() if k not in ("terrain","placements")
        }
        assert new_row["placements"][:len(live["placements"])]==live["placements"]

        evidence[mid]={
            "name":world.name, "garden":list(layout),
            "stock_tent_fills_removed":len(removed),
            "ground_mesh":native_id, "ground_quads":len(land.faces),
            "preserved_event_count":len(events.ev), "tent_sites":[serialize(tent) for tent in tents],
        }

    assert len(plans)==4, list(plans)
    out=COAST / ("clan-castles-"+GROUP)
    out.mkdir(exist_ok=True)
    for name,data in (
        ("plans",plans),("rows",rows),
        ("art-report",{"maps":evidence,"reused_published_art":["quarry_tent","quarry_tent_flap"]}),
    ):
        (out/(name+".json")).write_text(json.dumps(data,indent=2)+"\n","utf-8")
    print(f"Prepared {len(plans)} maps, {sum(len(r['tent_sites']) for r in evidence.values())} tents and flaps")
    print(out)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    args=p.parse_args()
    apply(args.repo.resolve())
