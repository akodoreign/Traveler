"""Verify the Lava Trees glebe, exits, and real registered fight."""
from pathlib import Path
import sys

from preview_clan_castles import run,spawn

QUIET="::rpgstage.encinc=0.0;"


def main(profile):
    for label,target,start,end in (("west","M449",13,-3),("east","M451",138,154)):
        run(profile,f"lava-trees-{label}-gate","M450","bayushi",spawn(start,25,2.),
            f"wait,850|evalf,tmp/castle_native.sk|goto,{end},25,9800|untilmap,{target},8500",
            (f"BOT reached {target}",),QUIET,timeout=54)
    setup=r"""
local stage=::rpgstage;
if(stage.mapid=="M450"){
    local kit=stage.rtEnvironmentKit;
    if(!kit || length(kit.waterTextures)!=32 || !length(kit.vegetation) || !length(kit.magmaSpatter))
        throw Exception("Missing Lava Trees scene or animation");
    stage.raiseEncounter();
    return;
}
if(stage.mapid!="M899" || !stage["battle"] || !length(stage.battle.enemies))
    throw Exception("The Lava Trees encounter did not load its usual arena");
printf("[LAVA TREES] The original registered encounter entered M899\n");
"""
    run(profile,"lava-trees-registered-encounter","M450","bayushi",spawn(79,25,2.),
        "wait,930|evalf,tmp/castle_native.sk|untilmap,M899,12000|wait,1300|evalf,tmp/castle_native.sk",
        ("BOT reached M899","[LAVA TREES] The original registered encounter"),setup,timeout=56)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
