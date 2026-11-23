"""Prepare tent placement data for the six remaining non-castle stock maps.

The outputs are inputs to each map's terrain rebuild. They do not replace or
publish any active terrain, events, or assets.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from audit_stock_tents import CATALOG, INDEX, load_generator, raw_tents

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent/"native_environment"
BUNDLE=HERE.parent/"clan-castles-world-stock-tents"
EXPECTED={"M214":17,"M215":3,"M323":2,"M325":2,"M337":6,"M825":7}


def prepare(repo):
    gm=load_generator(repo)
    project=repo/"_tools/rpgcobo-tool/project"
    catalog=json.loads((project/CATALOG).read_bytes())
    installed=json.loads((project/INDEX).read_bytes())
    native=(project/INDEX).parent
    for part in ("quarry_tent.pm","quarry_tent.mdl","quarry_tent_flap.pm","quarry_tent_flap.mdl",
                 "tex/quarry_hemp.png","tex/quarry_edge.png","tex/storehouse_frame.png"):
        assert (STAGE/part).read_bytes()==(native/part).read_bytes(), part
    layouts={}
    plans={}
    rows={}
    for mid,count in EXPECTED.items():
        assert mid not in installed, f"{mid}: existing native art needs a fresh inspection"
        world,events=gm.make(mid)
        tents=raw_tents(world)
        assert len(tents)==count and all(len(t.present)==len(t.pieces) for t in tents), mid
        fills=[piece for t in tents for piece in t.pieces]
        assert len({id(x) for x in fills})==len(fills),mid
        event_cells={(p[0],p[2]):key for key,event in catalog[mid]["event"].items() if (p:=event.get("pos"))}
        front_posts_and_lee={cell for tent in tents for cell in tent.walls()}
        blocked=front_posts_and_lee & event_cells.keys()
        # Preserve the original interaction anchors. No door destinations,
        # story/collision settings, shops or encounter blocks move.
        walls=front_posts_and_lee - blocked - set(world.walls)
        placements=[r for t in tents for r in t.placements()]
        assert Counter(row[0] for row in placements)=={"quarry_tent":count,"quarry_tent_flap":count},mid
        layouts[mid]={"name":world.name,"next":"Rebuild terrain and merge these fitted props with its native environment row.",
                      "stock_tent_count":count,"event_count":len(event_cells),
                      "role":"battle" if mid=="M825" else "world","remove":fills,
                      "walls":[list(p) for p in sorted(walls)],"placements":placements,
                      "reserved_event_cells":[{"cell":list(p),"event":event_cells[p]} for p in sorted(blocked)]}
        plans[mid]={"theme":"world-stock-tents","remove":fills,"add":[],"decor":{},"positions":{},
                    "walls":[list(p) for p in sorted(walls)]}
        rows[mid]={"terrain":None,"placements":placements,"propOnly":"quarry-tent-retrofit"}
        print(mid,world.name,count,"tents",len(blocked),"reserved event cells")
    (HERE/"world-tent-fits.json").write_text(json.dumps(layouts,indent=2)+"\n","utf-8")
    BUNDLE.mkdir(exist_ok=True)
    for name,data in (("plans",plans),("rows",rows),("art-report",{"maps":layouts})):
        (BUNDLE/(name+".json")).write_text(json.dumps(data,indent=2)+"\n","utf-8")
    print("Prepared",sum(EXPECTED.values()),"tents in",BUNDLE)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    args=p.parse_args()
    prepare(args.repo.resolve())
