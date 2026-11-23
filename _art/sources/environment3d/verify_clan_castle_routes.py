"""Check representative exterior and indoor transitions on each castle in-game."""
import argparse
import json
from pathlib import Path

from preview_clan_castles import route

CASTLES = {
    "hida": ("M500","M538","M541","M501","M502","M503","M504","M141","G200"),
    "doji": ("M505","M549","M552","M506","M507","M508","M509","M228",""),
    "akodo": ("M510","M560","M563","M511","M512","M513","M514","M255",""),
    "isawa": ("M515","M571","M574","M516","M517","M518","M519","M288",""),
    "bayushi": ("M520","M582","M585","M521","M522","M523","M524","M347",""),
    "kitsuki": ("M525","M593","M596","M526","M527","M528","M529","M343",""),
    "iuchi": ("M530","M604","M607","M531","M532","M533","M534","M390",""),
    "togashi": ("M623","M615","M618","M624","M625","M626","M627","M382","G947"),
}


def destination(catalog, mid, target):
    return next(row for row in catalog[mid]["event"].values() if row.get("dest",{}).get("mapid")==target)


def keep_round_trip(profile, theme, castle, catalog):
    _,_,keep,floor,*_=castle
    px,py,pz,_=destination(catalog,keep,floor)["pos"]
    ix,_,iz,_=destination(catalog,floor,keep)["pos"]
    steps=(f"wait,450|goto,{px},{pz-3},5550|goto,{px},{pz+2},6200|untilmap,{floor},8100|"
           f"wait,500|goto,{ix},{iz-1},5700|untilmap,{keep},8400")
    route(profile,keep,theme,px,pz-10,2.,f"{theme}-keep-round-trip",steps,(floor,keep),"")


def court_round_trip(profile, theme, castle, catalog):
    reception,garden,*_=castle
    px,py,pz,_=destination(catalog,reception,garden)["pos"]
    rx,_,rz,_=destination(catalog,garden,reception)["pos"]
    steps=(f"wait,450|goto,{px},{pz+1},8400|untilmap,{garden},8100|"
           f"wait,440|goto,{rx},{rz-1},6000|untilmap,{reception},8100")
    route(profile,reception,theme,px,pz-11,py/2,f"{theme}-garden-round-trip",steps,(garden,reception),"")


def stair_round_trip(profile,theme,lower,upper,catalog):
    x,_,z,_=destination(catalog,lower,upper)["pos"]
    down_x,_,down_z,_=destination(catalog,upper,lower)["pos"]
    steps=(f"wait,450|goto,{x},{z+1},9500|untilmap,{upper},8500|"
           f"wait,500|goto,{down_x},{down_z-1},9000|untilmap,{lower},8500")
    route(profile,lower,theme,x,z-13,5.,f"{theme}-{lower.lower()}-stairs",steps,(upper,lower),"")


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("profile",type=Path)
    p.add_argument("themes",nargs="+",choices=CASTLES)
    p.add_argument("--stairs",action="store_true")
    p.add_argument("--courts",action="store_true")
    args=p.parse_args()
    profile=args.profile.resolve()
    catalog=json.loads((profile/"project/data/map.json").read_bytes())
    for theme in args.themes:
        castle=CASTLES[theme]
        keep_round_trip(profile,theme,castle,catalog)
        if args.courts:
            court_round_trip(profile,theme,castle,catalog)
        if args.stairs:
            floors=castle[3:7]
            for lower,upper in zip(floors,floors[1:]):
                stair_round_trip(profile,theme,lower,upper,catalog)
