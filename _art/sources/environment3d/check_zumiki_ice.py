"""Prove the matching ice-cave entrance, nearby gates and registered encounter."""
from pathlib import Path
import sys
from preview_clan_castles import run,spawn

QUIET="::rpgstage.encinc=0.0;"


def main(profile):
    probe=profile/"tmp/ice_cave_verification.sk"
    try:
        probe.write_text(r"""
local stage=::rpgstage;
local p=stage.player3d.pos;
if(stage.mapid!="M473" || Math.abs(p.x-37.0)>.55 || p.z>=14.45)
    throw Exception("Ice cave exit did not land at the matching entrance");
printf("[ZUMIKI] Matching entry and return at %.2f %.2f\n",p.x,p.z);
""","utf8")
        run(profile,"zumiki-ice-cave-round-trip","M473","kitsuki",spawn(74,20,2.),
            "wait,700|evalf,tmp/castle_native.sk|goto,74,32,8300|untilmap,M485,8600|"
            "wait,650|evalf,tmp/castle_native.sk|goto,46,2,8500|untilmap,M473,8800|"
            "wait,720|evalf,tmp/ice_cave_verification.sk",
            ("BOT reached M485","BOT reached M473","[ZUMIKI] Matching entry and return"),QUIET,timeout=58)
        for label,mid,flag,theme,z,end in (
            ("wounded-lion","M430","G1303","kitsuki",13,-3),
            ("zumiki","M282","G1305","isawa",43,59),
        ):
            force=QUIET+f'::rpgvar["{flag}"]=true;'
            run(profile,"zumiki-road-"+label,"M473",theme,spawn(91,z,2.),
                f"wait,710|evalf,tmp/castle_native.sk|vars,{flag}|goto,91,{end},9200|untilmap,{mid},8400",
                (f"BOT reached {mid}",),force,flags=flag,timeout=42)
        probe.write_text(r"""
local stage=::rpgstage;
if(stage.mapid!="M844" || !stage.rtEnvironmentKit || !stage["battle"] || length(stage.battle.enemies)<1)
    throw Exception("Ice cave loaded the wrong combat scene");
printf("[ZUMIKI] Registered ice cave encounter entered the ice arena with %d foes\n",length(stage.battle.enemies));
""","utf8")
        run(profile,"zumiki-registered-encounter","M485","kitsuki",spawn(62,23,1.5),
            "wait,800|evalf,tmp/castle_native.sk|untilmap,M844,15000|wait,1300|evalf,tmp/ice_cave_verification.sk",
            ("BOT reached M844","[ZUMIKI] Registered ice cave encounter"),"::rpgstage.raiseEncounter();",timeout=46)
    finally:
        probe.unlink(missing_ok=True)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
