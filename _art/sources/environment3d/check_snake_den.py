"""Walk the original Snake Den thresholds on the rebuilt cave floor."""
from pathlib import Path
import sys

from preview_clan_castles import run, spawn

FLAGS = "G1055,G1063,G1064,G1066,G1067,G1068,G1070,G1071,G1072,G1074,G1075,G1078,G1093"
QUIET = """
::rpgstage.encinc=0.0;
if(!::rpgstage.rtEnvironmentKit) throw Exception("The rebuilt Snake Den did not load");
"""

ROUTES = (
    ("snake-den-archive-sand", "M425", "M426", (134, 30), (144, 32), (31, 16)),
    ("snake-den-sand-mouth", "M426", "M427", (115, 20), (126, 21), (31, 19)),
    ("snake-den-mouth-enforcer", "M427", "M428", (73, 17), (73, 28), (27, 19)),
)


def main(profile):
    for label, origin, destination, (x, z), (tx, tz), (rx, rz) in ROUTES:
        run(profile, label, origin, "kitsuki", spawn(x, z, 1.5),
            f"wait,550|evalf,tmp/castle_native.sk|goto,{tx},{tz},8500|untilmap,{destination},8400|"
            f"wait,600|evalf,tmp/castle_native.sk|goto,{rx},{rz},8500|untilmap,{origin},8400",
            (f"BOT reached {destination}", f"BOT reached {origin}"),
            QUIET, flags=FLAGS, timeout=60)


def flank_checks(profile):
    for x in (63, 85):
        script=QUIET+r"""
local p=::rpgstage.player3d.pos;
if (::rpgstage.mapid!="M427" || p.z>=13.4 || p.y>2.3)
    throw Exception("Serpent doorway flank collision did not stop the player");
printf("[SNAKE DEN] Flank blocked at %.2f %.2f %.2f\n",p.x,p.y,p.z);
"""
        run(profile,f"snake-den-flank-{x}","M427","kitsuki",spawn(x,21,1.5),
            f"wait,550|evalf,tmp/castle_native.sk|goto,{x},33,4200|evalf,tmp/castle_native.sk",
            ("[SNAKE DEN] Flank blocked",),script,flags=FLAGS,timeout=30)


def harbour_stair(profile):
    run(profile,"snake-den-harbour-stair","M424","kitsuki",spawn(35,25,2.0),
        "wait,550|evalf,tmp/castle_native.sk|answer,0|talkto,35,27|untilmap,M425,10500|"
        "wait,650|answer,0|talkto,30,19|untilmap,M424,11500",
        ("BOT reached M425","BOT reached M424"),QUIET,flags=FLAGS,timeout=55)


if __name__ == "__main__":
    profile=Path(sys.argv[1]).resolve()
    main(profile)
    flank_checks(profile)
    harbour_stair(profile)
