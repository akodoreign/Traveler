"""Walk the Cakon paddy links and the fitted hut recess in the native engine."""
import sys
from pathlib import Path

from preview_clan_castles import run, spawn

FLAGS="G1047,G1048,G1051,G1054"
QUIET=r"""
::rpgstage.encinc=0.0;
if(!::rpgstage.rtEnvironmentKit) throw Exception("The Cakon scenery did not load");
"""
THRESHOLD=r"""
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M421" || Math.abs(p.x-42.5)>.48 || p.z<11.30 || p.y>2.63)
    throw Exception("Could not walk through the clay arch");
printf("CAKON clay threshold walked at %.2f %.2f %.2f\n",p.x,p.y,p.z);
"""
BOUNDARY=r"""
local p=::rpgstage.player3d.pos;
local dx=(p.x-42.5)/2.5, dz=(p.z-12.75)/2.46;
local mask=::rpgstage.bw.bmp;
if(::rpgstage.mapid!="M421" || dx*dx+dz*dz<.83 || !mask.get(80,25) || mask.get(85,21))
    throw Exception("The built hut wall did not stop a side approach");
printf("CAKON clay flank blocked at %.2f %.2f\n",p.x,p.z);
"""


def main(profile):
    run(profile,"cakon-paddy-hut","M420","kitsuki",spawn(148,26,2.0),
        "wait,620|evalf,tmp/castle_native.sk|goto,161,26,8800|untilmap,M421,8500|"
        "wait,650|evalf,tmp/castle_native.sk|goto,-.5,23,8500|untilmap,M420,8500",
        ("BOT reached M421","BOT reached M420"),QUIET,flags=FLAGS,timeout=60)
    run(profile,"cakon-paddy-canal","M420","kitsuki",spawn(9,26,2.0),
        "wait,600|evalf,tmp/castle_native.sk|goto,-.5,26,8000|untilmap,M419,8000|"
        "wait,640|evalf,tmp/castle_native.sk|goto,152,24,8300|untilmap,M420,8100",
        ("BOT reached M419","BOT reached M420"),QUIET,flags=FLAGS,timeout=60)
    run(profile,"cakon-clay-threshold","M421","kitsuki",spawn(85,17,2.0),
        "wait,520|goto,85,23.7,6300|evalf,tmp/castle_native.sk",
        ("CAKON clay threshold walked",),THRESHOLD,flags=FLAGS)
    run(profile,"cakon-clay-side-wall","M421","kitsuki",spawn(76,25,2.0),
        "wait,520|goto,85,25,5500|evalf,tmp/castle_native.sk",
        ("CAKON clay flank blocked",),BOUNDARY,flags=FLAGS)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
