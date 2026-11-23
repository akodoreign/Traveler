"""Walk to each Yasuki cave and return through the mouth used for entry."""
from pathlib import Path
import sys

from preview_clan_castles import run, spawn

QUIET=r"""
::rpgstage.encinc=0.0;
"""
RETURN=r"""
local stage=::rpgstage;
local p=stage.player3d.pos;
if(stage.mapid!="M470" || p.z>=14.55)
    throw Exception("The return landing is inside the cave trigger");
printf("[YASUKI] Returned to the road side of the mouth at %.2f %.2f %.2f\n",p.x,p.y,p.z);
"""


def main(profile):
    for name,cave,x in (("sea","M480",70),("smuggler","M481",112)):
        run(profile,f"yasuki-{name}-cave-round-trip","M470","kitsuki",spawn(x,20,2.),
            f"wait,700|evalf,tmp/castle_native.sk|goto,{x},32,8200|untilmap,{cave},9500|"
            "wait,600|evalf,tmp/castle_native.sk|goto,46,2,7500|untilmap,M470,9500|"
            "wait,600|evalf,tmp/yasuki_return.sk",
            (f"BOT reached {cave}","BOT reached M470","[YASUKI] Returned to the road side"),
            QUIET,timeout=60)


def check_coast_links(profile):
    run(profile,"yasuki-road-hoshi","M470","kitsuki",spawn(11,28,2.),
        "wait,780|evalf,tmp/castle_native.sk|goto,0,28,8500|untilmap,M103,10000",
        ("BOT reached M103",),QUIET+'::rpgvar["G1300"]=true;',timeout=44)
    run(profile,"yasuki-road-yashiki","M470","hida",spawn(91,43,2.),
        "wait,780|vars,G1301|goto,91,59,9000|untilmap,M213,8500",
        ("BOT reached M213",),flags="G1301",timeout=37)


def check_cave_battle(profile, origin):
    launch=r"""
local stage=::rpgstage;
if(!stage.rtEnvironmentKit || !length(stage.map.encount))
    throw Exception("Missing coastal cave or its encounters");
stage.raiseEncounter();
"""
    inspect=r"""
local stage=::rpgstage;
if(stage.mapid!="M829" || !stage.rtEnvironmentKit || !stage["battle"]
    || !length(stage.battle.enemies))
    throw Exception("The cave did not enter its themed arena");
printf("[YASUKI] Cave encounter active on %S with %d foes\n",
    stage.mapid,length(stage.battle.enemies));
"""
    proof=profile/"tmp/yasuki_battle.sk"
    proof.write_text(inspect,"utf8")
    try:
        run(profile,f"yasuki-encounter-{origin.lower()}",origin,"kitsuki",spawn(65,20,1.5),
            "wait,800|evalf,tmp/castle_native.sk|untilmap,M829,12500|wait,800|evalf,tmp/yasuki_battle.sk",
            ("BOT reached M829","[YASUKI] Cave encounter active"),launch,timeout=45)
    finally:
        proof.unlink(missing_ok=True)


if __name__=="__main__":
    profile=Path(sys.argv[1]).resolve()
    proof=profile/"tmp/yasuki_return.sk"
    proof.write_text(RETURN,"utf8")
    try:
        main(profile)
    finally:
        proof.unlink(missing_ok=True)

    for origin in ("M480","M481"):
        check_cave_battle(profile,origin)

    check_coast_links(profile)
