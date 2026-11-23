"""Walk the Dragon gates, mountain stream crossing, and cave return in the game."""
from pathlib import Path
import sys

from preview_clan_castles import run,spawn

QUIET="::rpgstage.encinc=0.0;"
FIRST="wait,790|evalf,tmp/castle_native.sk|"
TEST="evalf,tmp/dragon_mountain_verification.sk"


def main(profile):
    probe=profile/"tmp/dragon_mountain_verification.sk"
    try:
        probe.write_text(r"""
local s=::rpgstage, p=s.player3d.pos;
if(s.mapid!="M476" || !s.rtEnvironmentKit || Math.abs(p.x-45.)>.6 || p.z>14.7)
    throw Exception("The Dragon cave exit missed the recessed mountain mouth");
printf("[DRAGON] Returned through the same mouth at %.2f %.2f\n",p.x,p.z);
""","utf8")
        run(profile,"dragon-mountain-cave-round-trip","M476","kitsuki",spawn(90,21,2.),
            FIRST+"goto,90,32,9200|untilmap,M488,8800|wait,630|evalf,tmp/castle_native.sk|"
            "goto,46,2,9400|untilmap,M476,9200|wait,540|"+TEST,
            ("BOT reached M488","BOT reached M476","[DRAGON] Returned"),QUIET,timeout=57)
        probe.write_text(r"""
local s=::rpgstage, p=s.player3d.pos;
if(s.mapid!="M476" || !s.rtEnvironmentKit || p.x<62.2 || Math.abs(p.z-10.5)>.66)
    throw Exception("The footpath across the mountain stream failed");
printf("[DRAGON] Walked the mountain crossing at %.2f %.2f %.2f\n",p.x,p.y,p.z);
""","utf8")
        run(profile,"dragon-mountain-stream-crossing","M476","kitsuki",spawn(101,21,2.),
            FIRST+"goto,126,21,11200|wait,480|"+TEST,
            ("[DRAGON] Walked the mountain crossing",),QUIET,timeout=45)
        for name,mid,x,flag,lead in (("buried-leaves","M387",45,"G1307","iuchi"),
                                     ("dragon-town","M379",136,"G1302","bayushi")):
            flags=QUIET+f'::rpgvar["{flag}"]=true;'
            run(profile,"dragon-mountain-gate-"+name,"M476",lead,spawn(x,14,2.),
                FIRST+f"vars,{flag}|goto,{x},-3,10000|untilmap,{mid},9000",
                (f"BOT reached {mid}",),flags,flags=flag,timeout=48)
        for mid,target,x,z,floor in (("M476","M872",95,20,2.),("M488","M798",76,20,1.5)):
            probe.write_text(rf"""
local s=::rpgstage;
if(s.mapid!="{target}" || !s.rtEnvironmentKit || !s["battle"] || length(s.battle.enemies)<1)
    throw Exception("The registered encounter did not use its mountain arena");
printf("[DRAGON] {mid} loaded {target} with %d foes\n",length(s.battle.enemies));
""","utf8")
            run(profile,"dragon-mountain-battle-"+mid.lower(),mid,"kitsuki",spawn(x,z,floor),
                FIRST+f"untilmap,{target},14000|wait,1450|"+TEST,
                (f"BOT reached {target}",f"[DRAGON] {mid} loaded {target}"),"::rpgstage.raiseEncounter();",timeout=48)
    finally:
        probe.unlink(missing_ok=True)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
