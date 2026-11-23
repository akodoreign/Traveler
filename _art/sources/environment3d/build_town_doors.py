"""Dress town entrances from the building footprints and registered map transitions."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export
from prepare_coast import periodic

HERE = Path(__file__).resolve().parent
SCAN = HERE / "surface_sources"
TEX = STAGE / "tex"
MATERIALS = {
    "cedar": ("door_cedar.png", .89),
    "frame": ("door_frame.png", .91),
    "iron": ("door_iron.png", .77),
    "recess": ("door_recess.png", .96),
    "stone": ("door_stoop.png", .94),
}


def door_materials():
    for source, output, tint, contrast in (
        ("town_door_cedar", "door_cedar", [111, 72, 49], .77),
        ("town_door_cedar", "door_frame", [69, 46, 33], .71),
        ("town_door_cedar", "door_recess", [29, 23, 20], .37),
        ("town_door_iron", "door_iron", [63, 58, 50], .81),
        ("kaiu_masonry", "door_stoop", [122, 111, 97], .72),
    ):
        im = Image.open(SCAN / f"{source}.png").convert("RGB")
        sample = periodic(im.crop((9, 9, im.width-9, im.height-9)), 512)
        luminance = sample @ [.24,.67,.09]
        detail = np.clip((luminance-np.median(luminance)) /
                         max(2., np.percentile(luminance,91)-np.percentile(luminance,9)), -.63,.63)
        rgb = np.array(tint)[None,None,:]*(1+contrast*detail[...,None])
        Image.fromarray(rgb.clip(0,255).astype(np.uint8)).save(TEX/f"{output}.png")


def leaves():
    jamb=Geometry()
    for x in (.002,.926):
        box(jamb,(x,-.045,0.),(.072,.22,1.99),"frame",.85)
    box(jamb,(0.,-.055,1.914),(1.,.24,.086),"frame",.93)
    box(jamb,(.017,-.073,0.),(.966,.20,.047),"frame",.79)
    # The actual threshold occupies half a metre before the wall behind it.
    box(jamb,(.078,.44,.046),(.846,.014,1.868),"recess",1.02)
    export("town_door_frame",jamb,MATERIALS)

    leaf=Geometry()
    for k in range(6):
        h=1.833 + (.016 if k%2 else .011)
        box(leaf,(.071+k*.143,.036,.045),(.139,.058,h),"cedar",.78)
    for y in (.16,1.68):
        box(leaf,(.073,.024,y),(.843,.021,.109),"frame",.68)
        box(leaf,(.076,.089,y),(.79,.021,.102),"frame",.71)
    for y in (.21,1.60):
        box(leaf,(.069,.011,y),(.076,.034,.073),"iron",.59)
        box(leaf,(.087,.006,y+.021),(.129,.016,.031),"iron",.47)
    box(leaf,(.781,.015,1.02),(.085,.026,.141),"iron",.67)
    for x,w in ((.794,.017),(.837,.017)):
        box(leaf,(x,-.026,1.048),(w,.046,.057),"iron",.55)
    box(leaf,(.795,-.028,1.044),(.059,.026,.017),"iron",.56)
    hinge = np.array([.073,.076,0.])
    leaf.vertices=[np.asarray(point)-hinge for point in leaf.vertices]
    export("town_door_leaf",leaf,MATERIALS)


def stoops():
    for name, rise, treads in (("half",.5,2),("full",1.,3)):
        geom=Geometry()
        for tread in range(treads):
            depth=(treads-tread)*.265
            top=rise*(tread+1)/treads
            # Mortised pavers above the squared stone riser.
            box(geom,(-.133+tread*.021,-depth+.02,rise*tread/treads-.024),
                (1.266-tread*.042,depth+.14,top-rise*tread/treads-.024),"stone",.56)
            box(geom,(-.158+tread*.021,-depth-.016,top-.049),
                (1.316-tread*.042,depth+.174,.049),"stone",.61)
        export(f"town_door_stoop_{name}",geom,MATERIALS)


def find_facades(gm, world, events):
    """Pair a visible threshold with its portal so the game can display the live unlocked state."""
    doors = []
    for raw_x, raw_z, width, _ in world.buildings:
        x,z=raw_x+gm.PAD_X+width//2,raw_z+gm.PAD_BOTTOM
        cuts=[obj for obj in world.objs if obj["t"]=="fill" and obj["blk"]==gm.VOID
              and obj["x"]==x-1 and obj["z"]==z and obj["w"]==2 and obj["h"]==4]
        if not cuts:
            continue
        cut,=cuts
        candidates=[(key,event) for key,event in events.items() if event.get("role")=="portal"
                    and abs(event["pos"][0]-x)<=1 and event["pos"][2]==z-2]
        if len(candidates)>1:
            raise ValueError(f"{world.mid} doorway {(x,z)} has several matching portals")
        key, portal = candidates[0] if candidates else (None,None)
        ground=float((world.hgt[z-1,x]+1)*.5)
        rise=cut["y"]*.5-ground
        stoop={.5:"town_door_stoop_half",1.:"town_door_stoop_full"}.get(rise)
        doors.append(dict(x=cut["x"]*.5,y=cut["y"]*.5,z=cut["z"]*.5-.118,
                          grade=ground,stoop=stoop,
                          event=int(key.strip("#")) if key else None,
                          dest=portal["dest"]["mapid"] if portal else None))
    return doors


def main():
    repo = Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    door_materials()
    leaves()
    stoops()
    manifest=STAGE/"index.json"
    index=json.loads(manifest.read_bytes())
    maps=json.loads((repo/"_tools/rpgcobo-tool/project/data/map.json").read_bytes())
    towns = sys.argv[2:] or ["M103"]
    result={}
    for mid in towns:
        world,_=gm.make(mid)
        doors=find_facades(gm,world,maps[mid]["event"])
        if not doors:
            raise RuntimeError(f"No fitted building facades on {mid}")
        index.setdefault(mid,{"placements":[]})["doors"]=doors
        result[mid]=doors
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"town-door-layout.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("Fitted",sum(map(len,result.values())),"town facades:",", ".join(towns))


if __name__=="__main__":
    main()
