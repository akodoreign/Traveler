"""Walk both Phoenix road gates and the fox cave and test registered encounters."""
from pathlib import Path
import sys

from preview_clan_castles import run, spawn

QUIET="::rpgstage.encinc=0.0;"
BEGIN="wait,800|evalf,tmp/castle_native.sk|"
USE="evalf,tmp/phoenix_fox_verification.sk"


def main(profile):
    probe=profile/"tmp/phoenix_fox_verification.sk"
    try:
        probe.write_text(r"""
local s=::rpgstage;
local p=s.player3d.pos;
if(s.mapid!="M475" || Math.abs(p.x-35.)>.56 || p.z>14.7 || !s.rtEnvironmentKit)
    throw Exception("The fox cave returned the party to the wrong part of the route");
printf("[FOX] Round trip through the recessed mouth at %.2f %.2f\n",p.x,p.z);
""","utf8")
        run(profile,"phoenix-fox-round-trip","M475","isawa",spawn(70,21,2.),
            BEGIN+"goto,70,32,9000|untilmap,M487,9000|wait,650|evalf,tmp/castle_native.sk|"
            "goto,46,2,9100|untilmap,M475,9000|wait,560|"+USE,
            ("BOT reached M487","BOT reached M475","[FOX] Round trip"),QUIET,timeout=57)
        for name,dest,flag,lead,start,end in (("kamatori","M252","G1306","isawa",19,-3),
                                             ("mountain-town","M379","G1302","bayushi",11,59)):
            setup=QUIET+f'::rpgvar["{flag}"]=true;'
            run(profile,"phoenix-northern-road-"+name,"M475",lead,spawn(91,start,2.),
                BEGIN+f"vars,{flag}|goto,91,{end},15500|untilmap,{dest},9000",
                (f"BOT reached {dest}",),setup,flags=flag,timeout=49)
        for mid,dest,x,z,floor in (("M475","M846",72,22,2.),("M487","M799",75,24,1.5)):
            probe.write_text(rf"""
local s=::rpgstage;
if(s.mapid!="{dest}" || !s.rtEnvironmentKit || !s["battle"] || length(s.battle.enemies)<1)
    throw Exception("The Phoenix route loaded the wrong encounter arena");
printf("[FOX] {mid} loaded {dest} with %d foes\n",length(s.battle.enemies));
""","utf8")
            run(profile,"phoenix-fox-encounter-"+mid.lower(),mid,"isawa",spawn(x,z,floor),
                BEGIN+f"untilmap,{dest},14000|wait,1400|"+USE,
                (f"BOT reached {dest}",f"[FOX] {mid} loaded {dest}"),"::rpgstage.raiseEncounter();",timeout=46)
    finally:
        probe.unlink(missing_ok=True)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
