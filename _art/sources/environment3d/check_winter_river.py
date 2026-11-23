"""Exercise the winter shore, fitted warehouse threshold, and rice barge."""
import sys
from pathlib import Path

from preview_clan_castles import run, spawn

FLAGS="G1055,G1063,G1064,G1066,G1067,G1068,G1070,G1071,G1075,G1078"
QUIET=r"""
::rpgstage.encinc=0.0;
if(!::rpgstage.rtEnvironmentKit) throw Exception("The winter river scenery did not load");
"""
DECK=r"""
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M423" || p.x<33.65 || p.y<2.35 || p.z<6.3 || p.z>9.3)
    throw Exception("The crew cannot walk the fitted barge deck");
printf("RIVER barge deck walked at %.2f %.2f %.2f\n",p.x,p.y,p.z);
"""


def main(profile):
    run(profile,"winter-river-round-trip","M422","kitsuki",spawn(150,25,2.0),
        "wait,580|evalf,tmp/castle_native.sk|goto,164,25,8500|untilmap,M424,8400|"
        "wait,610|evalf,tmp/castle_native.sk|goto,-.8,30,9500|untilmap,M422,8500",
        ("BOT reached M424","BOT reached M422"),QUIET,flags=FLAGS,timeout=62)
    run(profile,"floating-flowers-warehouse","M424","kitsuki",spawn(103,23,2.0),
        "wait,550|goto,103,28,8000|untilmap,M973,8500|"
        "wait,600|goto,19,6,6800|untilmap,M424,8300",
        ("BOT reached M973","BOT reached M424"),flags=FLAGS,timeout=59)
    run(profile,"winter-barge-deck","M423","kitsuki",spawn(43,14,2.0),
        "wait,580|goto,69,14,9600|evalf,tmp/castle_native.sk",
        ("RIVER barge deck walked",),DECK,flags=FLAGS,timeout=50)
    run(profile,"winter-barge-arrival","M423","kitsuki",spawn(46,16,2.0),
        "wait,1050|untilmap,M424,38000",
        ("BOT reached M424",),flags="G1055,G1063,G1064",timeout=54)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
