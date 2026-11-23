"""Verify the two Beiden exits, the hideout return and both native arenas."""
from pathlib import Path
import sys

from preview_clan_castles import run,spawn

QUIET="::rpgstage.encinc=0.0;"
BEGIN="wait,790|evalf,tmp/castle_native.sk|"
PROBE="evalf,tmp/beiden_verification.sk"


def main(profile):
    probe=profile/"tmp/beiden_verification.sk"
    try:
        probe.write_text(r"""
local s=::rpgstage;
local p=s.player3d.pos;
if(s.mapid!="M477" || !s.rtEnvironmentKit || Math.abs(p.x-45.)>.56 || p.z>14.7)
    throw Exception("The party returned outside the hideout's actual mouth");
printf("[BEIDEN] Returned through the timber-shored mouth at %.2f %.2f\n",p.x,p.z);
""","utf8")
        run(profile,"beiden-hideout-round-trip","M477","bayushi",spawn(90,21,2.),
            BEGIN+"goto,90,32,9200|untilmap,M489,8850|wait,680|evalf,tmp/castle_native.sk|"
            "goto,46,2,9400|untilmap,M477,9000|wait,550|"+PROBE,
            ("BOT reached M489","BOT reached M477","[BEIDEN] Returned"),QUIET,timeout=55)
        for name,target,x,flag,lead in (("pleasant-eaves","M202",45,"G1301","hida"),
                                       ("kyuden-bayushi","M347",136,"G1302","bayushi")):
            cfg=QUIET+f'::rpgvar["{flag}"]=true;'
            run(profile,"beiden-gate-"+name,"M477",lead,spawn(x,40,2.),
                BEGIN+f"vars,{flag}|goto,{x},59,11100|untilmap,{target},9000",
                (f"BOT reached {target}",),cfg,flags=flag,timeout=45)
        for mid,arena,x,z,floor in (("M477","M821",83,21,2.),("M489","M797",78,21,1.5)):
            probe.write_text(rf"""
local s=::rpgstage;
if(s.mapid!="{arena}" || !s.rtEnvironmentKit || !s["battle"] || length(s.battle.enemies)<1)
    throw Exception("The original Beiden encounter chose the wrong arena");
printf("[BEIDEN] {mid} entered {arena} with %d foes\n",length(s.battle.enemies));
""","utf8")
            run(profile,"beiden-battle-"+mid.lower(),mid,"bayushi",spawn(x,z,floor),
                BEGIN+f"untilmap,{arena},14000|wait,1420|"+PROBE,
                (f"BOT reached {arena}",f"[BEIDEN] {mid} entered {arena}"),
                "::rpgstage.raiseEncounter();",timeout=46)
    finally:
        probe.unlink(missing_ok=True)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
