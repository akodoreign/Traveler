"""Resolve every Shosuro Renegade alias in native combat."""
from pathlib import Path
import struct
import sys

from PIL import Image

from preview_clan_castles import HERE, OUTPUTS, run, spawn
from verify_gusai import CAPTURE


def main(profile,fixtures):
    fixture=(fixtures/"renegade_foe_proof.sk").read_text("utf8")
    start="wait,1040|evalf,tmp/castle_native.sk|"
    run(profile,"shosuro-renegade-pilgrim-road","M437","bayushi",spawn(104,21,2.),
        start+"untilmap,M894,14000|wait,1270|evalf,tmp/castle_native.sk",
        ("BOT reached M894","[RENEGADE FIT] M894 E561","[RENEGADE FIT] M894 E951"),fixture)
    shared=(HERE/"preview_coast.sk").read_text("utf8")
    image=shared[shared.index("function screenshot("):shared.index("\n\nlocal views")]
    focus="\nlocal actor=battle.getChara3D(battle.enemies[0]);\n"
    capture=CAPTURE.replace("GusaiReviewCamera","RenegadeReviewCamera").replace("bot_gusai_","bot_renegade_")
    run(profile,"shosuro-renegade-daylight","M102","bayushi",spawn(49,21,2.),
        start+"untilmap,M811,14000|wait,1280|evalf,tmp/castle_native.sk",
        ("BOT reached M811","[RENEGADE FIT] M811 E561","[RENEGADE FIT] M811 E951",
         "[RENEGADE FIT] M811 E227"),image+"\n"+fixture+focus+capture)
    for view in ("front","side"):
        raw=(profile/"tmp/rt_shot"/f"bot_renegade_{view}.raw").read_bytes()
        size=struct.unpack_from("<II",raw)
        assert size==(3840,2160)
        Image.frombytes("RGBA",size,raw[8:]).convert("RGB").save(OUTPUTS/f"shosuro-renegade-{view}-daylight-4k.png")


if __name__=="__main__":
    main(*(Path(item).resolve() for item in sys.argv[1:3]))
