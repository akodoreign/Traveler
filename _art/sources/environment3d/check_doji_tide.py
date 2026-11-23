"""Walk through the cave and its crossing and trigger the registered battles."""
from pathlib import Path
import sys

from preview_clan_castles import run, spawn

QUIET="::rpgstage.encinc=0.0;"


def main(profile):
    probe=profile/"tmp/doji_tide_verification.sk"
    use="evalf,tmp/doji_tide_verification.sk"
    begin="wait,760|evalf,tmp/castle_native.sk|"
    try:
        probe.write_text(r"""
local s=::rpgstage;
local p=s.player3d.pos;
if(s.mapid!="M474" || Math.abs(p.x-45.)>.60 || p.z>14.7 || !s.rtEnvironmentKit)
    throw Exception("The return did not surface beside the Doji cliff opening");
printf("[DOJI] Returned through the Doji cave mouth at %.2f %.2f\n",p.x,p.z);
""","utf8")
        run(profile,"doji-tide-cave-round-trip","M474","doji",spawn(90,20,2.),
            begin+"goto,90,32,8500|untilmap,M486,8800|wait,580|evalf,tmp/castle_native.sk|"
            "goto,46,2,8500|untilmap,M474,8800|wait,540|"+use,
            ("BOT reached M486","BOT reached M474","[DOJI] Returned"),QUIET,timeout=57)

        probe.write_text(r"""
local s=::rpgstage;
local p=s.player3d.pos;
if(s.mapid!="M486" || p.x<50.5 || Math.abs(p.z-13.5)>.64 || !s.rtEnvironmentKit)
    throw Exception("The party did not walk to the far end of the tide bridge");
printf("[DOJI] Crossed the tide bridge at %.2f %.2f %.2f\n",p.x,p.y,p.z);
""","utf8")
        run(profile,"doji-tide-cave-crossing","M486","doji",spawn(80,27,1.5),
            begin+"goto,102,27,11400|wait,480|"+use,
            ("[DOJI] Crossed the tide bridge",),QUIET,timeout=44)

        for event,dest,flag,leader,sx,sz,tx,tz in (
            ("cakon","M415","G1303","kitsuki",91,13,91,-3),
            ("kyuden-doji","M228","G1301","hida",166,28,185,28),
        ):
            flags=QUIET+f'::rpgvar["{flag}"]=true;'
            run(profile,"doji-tide-road-"+event,"M474",leader,spawn(sx,sz,2.),
                begin+f"vars,{flag}|goto,{tx},{tz},9200|untilmap,{dest},8600",
                (f"BOT reached {dest}",),flags,flags=flag,timeout=44)

        for source,dest,sx,sz,y in (("M474","M828",90,22,2.),("M486","M829",77,24,1.5)):
            probe.write_text(rf"""
local s=::rpgstage;
if(s.mapid!="{dest}" || !s.rtEnvironmentKit || !s["battle"] || length(s.battle.enemies)<1)
    throw Exception("The source encounter loaded the wrong coastal battle");
printf("[DOJI] {source} loaded {dest} with %d foes\n",length(s.battle.enemies));
""","utf8")
            run(profile,"doji-tide-battle-"+source.lower(),source,"doji",spawn(sx,sz,y),
                begin+f"untilmap,{dest},15000|wait,1450|"+use,
                (f"BOT reached {dest}",f"[DOJI] {source} loaded {dest}"),"::rpgstage.raiseEncounter();",timeout=48)
    finally:
        probe.unlink(missing_ok=True)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
