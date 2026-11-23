"""Audit active field rigs in isolated native playtest windows."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


HERE=Path(__file__).resolve().parent
MAPS={
    "M101":(57,42,"G286,G233,G234,G235,G236",2),
    "M101-early":(53,42,"G255",1),
    "M177":(113,20,"G242,G243,G244,G245,G246,G249,G250",1),
    "M355":(57,18,"",1),
    "M130":(67,38,"G057",3),
    "M131":(59,39,"G041,G058",3),
    "M172":(93,20,"G242,G243",4),
    "M444":(94,19,"G507,G1162",1),
    "M536":(55,14,"",1),
    "M538":(33,24,"",1),
    "M539":(96,12,"",1),
    "M541":(107,17,"",1),
}


def check(repo,profile,test):
    sys.path.insert(0,str(repo/"tools"))
    import playbot

    x,z,flags,minimum=MAPS[test]
    map_id=test.split("-",1)[0]
    asset=repo/"_tools/rpgcobo-tool/project"
    for part in ("plugin/rokugan/RokuganLook.sk","resource/efx/rt/side_story_question.png"):
        shutil.copyfile(asset/part,profile/"project"/part)
    filename=profile/"tmp/check_field_rig.sk"
    text=(repo/"tools/test_native_side_story.sk").read_text(encoding="utf8")
    filename.write_text('::rpgstage.changeRenderSetting("rt_hd2d_field");\n'+text,encoding="utf8")
    log=HERE/f"field-rig-{test}.log"
    args=[str(profile/"rpgcobo.exe"),"-testplay","-map",map_id,playbot.start_pos(map_id,x,z),
          "-rtfast","-rtlead","P102"]
    if flags:
        args+=["-rtvar",flags]
    args+=["-rtbot","wait,2000|evalf,tmp/check_field_rig.sk"]
    custom_env={**os.environ,"TEMP":str(profile/"os-temp"),"TMP":str(profile/"os-temp"),
                "APPDATA":str(profile/"roaming"),"LOCALAPPDATA":str(profile/"local")}
    try:
        with log.open("w",encoding="utf8") as output:
            process=subprocess.Popen(args,cwd=profile,env=custom_env,stdout=output,stderr=subprocess.STDOUT)
            try:
                until=time.monotonic()+25
                while process.poll() is None and time.monotonic()<until:
                    if "BOT finished" in log.read_text(errors="replace"):
                        break
                    time.sleep(.15)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=10)
    finally:
        filename.unlink(missing_ok=True)
    report=log.read_text(errors="replace")
    proof=[line for line in report.splitlines() if "[FIELD RIG]" in line]
    assert "BOT finished" in report and "threw" not in report and len(proof)>=minimum,report[-4100:]
    for line in proof:
        print(line)


if __name__=="__main__":
    check(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),sys.argv[3])
