"""Walk the branch cave routes, the bridge, and sample registered encounters."""
from pathlib import Path
import sys
from preview_clan_castles import run, spawn

QUIET=r"""
::rpgstage.encinc=0.0;
"""


def movement(profile):
    for road,cave,x in (("M471","M482",76),("M472","M483",70),("M472","M484",112)):
        fixture=profile/"tmp/branch_cave_return.sk"
        fixture.write_text(r"""
local stage=::rpgstage;
local p=stage.player3d.pos;
if(stage.mapid!="%s" || Math.abs(p.x-%.2f)>.56 || p.z>=14.45)
    throw Exception("Branch cave returned through the wrong mouth");
printf("[BRANCH] Returned to the matching road approach %%.2f %%.2f\n",p.x,p.z);
""" % (road,x*.5),"utf8")
        try:
            run(profile,"branch-"+cave.lower()+"-round-trip",road,"kitsuki",spawn(x,21,2.),
                f"wait,750|evalf,tmp/castle_native.sk|goto,{x},33,8300|untilmap,{cave},8000|"
                f"wait,700|evalf,tmp/castle_native.sk|goto,46,2,8400|untilmap,{road},8500|"
                "wait,650|evalf,tmp/branch_cave_return.sk",
                (f"BOT reached {cave}",f"BOT reached {road}","[BRANCH] Returned to the matching road approach"),
                QUIET,timeout=52)
        finally:
            fixture.unlink(missing_ok=True)
    west=profile/"tmp/branch_bridge_crossing.sk"
    west.write_text(r"""
local stage=::rpgstage;
local p=stage.player3d.pos;
if(stage.mapid!="M482" || p.x<47.2 || p.z<12.7 || p.z>14.4 || p.y<1.65)
    throw Exception("The party did not cross the bridge on foot");
printf("[BRANCH] Bridge crossed at deck height %.2f %.2f %.2f\n",p.x,p.y,p.z);
""","utf8")
    try:
        run(profile,"branch-river-footbridge","M482","kitsuki",spawn(73,27,1.5),
            "wait,650|evalf,tmp/castle_native.sk|goto,96,27,8700|evalf,tmp/branch_bridge_crossing.sk",
            ("[BRANCH] Bridge crossed at deck height",),QUIET,timeout=35)
    finally:
        west.unlink(missing_ok=True)


def mine_switch_walk(profile):
    marker=profile/"tmp/mine_switch_walk.sk"
    marker.write_text(r"""
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M484" || p.x<47.5 || p.z<18.7 || p.y<1.72)
    throw Exception("The connecting gallery between switch stands was blocked");
printf("[BRANCH] Mine switch gallery walked at %.2f %.2f %.2f\n",p.x,p.y,p.z);
""","utf8")
    try:
        run(profile,"branch-mine-switch-gallery","M484","kitsuki",spawn(84,14,1.5),
            "wait,600|evalf,tmp/castle_native.sk|goto,88,18,4500|goto,88,25,6000|"
            "goto,87,32,6000|goto,91,37,6100|goto,97,40,6200|evalf,tmp/mine_switch_walk.sk",
            ("[BRANCH] Mine switch gallery walked",),QUIET,timeout=80)
    finally:
        marker.unlink(missing_ok=True)


def roads(profile):
    suites=(
        ("kudo","M471","M351","bayushi","G1302",(91,43),(91,59)),
        ("floating-flowers","M471","M424","kitsuki","G1303",(91,13),(91,-3)),
        ("shiro-akodo","M472","M255","akodo","G1304",(91,13),(91,-3)),
        ("wounded-lion","M472","M430","kitsuki","G1303",(91,43),(91,59)),
    )
    for label,origin,dest,lead,flag,start,(x,z) in suites:
        script=QUIET+'::rpgvar["'+flag+'"]=true;\n'
        run(profile,"branch-road-"+label,origin,lead,spawn(*start,2.),
            f"wait,760|evalf,tmp/castle_native.sk|vars,{flag}|goto,{x},{z},9000|untilmap,{dest},8500",
            (f"BOT reached {dest}",),script,flags=flag,timeout=37)


def battles(profile):
    for origin,arena in (("M482","M829"),("M483","M819"),("M484","M819")):
        check=profile/"tmp/branch_encounter.sk"
        check.write_text(r"""
local stage=::rpgstage;
if(stage.mapid!="%s" || !stage.rtEnvironmentKit || !stage["battle"] || !length(stage.battle.enemies))
    throw Exception("Missing branch cave battle or enemy formation");
printf("[BRANCH] Active cave encounter with %%d foes on %%S\n",length(stage.battle.enemies),stage.mapid);
""" % arena,"utf8")
        try:
            run(profile,"branch-"+origin.lower()+"-encounter",origin,"kitsuki",spawn(65,18,1.5),
                f"wait,800|evalf,tmp/castle_native.sk|untilmap,{arena},13000|wait,950|evalf,tmp/branch_encounter.sk",
                (f"BOT reached {arena}","[BRANCH] Active cave encounter"),
                "::rpgstage.raiseEncounter();",timeout=38)
        finally:
            check.unlink(missing_ok=True)


if __name__=="__main__":
    profile=Path(sys.argv[1]).resolve()
    {"movement":movement,"roads":roads,"battles":battles,"mine":mine_switch_walk}[sys.argv[2]](profile)
