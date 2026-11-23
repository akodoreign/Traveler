"""Walk the native Shinomen tunnel and the smith entrance and return."""

from pathlib import Path
import sys
import subprocess
import time


repo=Path(sys.argv[1]).resolve()
engine=Path(sys.argv[2]).resolve()
here=Path(__file__).resolve().parent
sys.path.insert(0,str(repo/"tools"))
import playbot


def run(label,x,z,path,checks,script):
    fixture=engine/"tmp/shinomen_verify.sk"
    log=here/f"shinomen-{label}-route.log"
    fixture.write_text(script,encoding="utf8")
    try:
        args=[str(engine/"rpgcobo.exe"),"-testplay","-map","M457",playbot.start_pos("M457",x,z),
              "-rtfast","-rtauto","-rt",f"bot {path};choice 0;lead P102"]
        with log.open("w",encoding="utf8") as output:
            proc=subprocess.Popen(args,cwd=engine,stdout=output,stderr=subprocess.STDOUT)
            try:
                end=time.monotonic()+42.
                while proc.poll() is None and time.monotonic()<end:
                    if "BOT finished" in log.read_text(errors="replace"):
                        break
                    time.sleep(.2)
            finally:
                if proc.poll() is None:
                    proc.kill()
                proc.wait(timeout=10)
    finally:
        fixture.unlink(missing_ok=True)
    evidence=log.read_text(errors="replace")
    assert "BOT finished" in evidence and "NOT reached" not in evidence and "threw" not in evidence,evidence[-4500:]
    assert all(mark in evidence for mark in checks),evidence[-4500:]
    for line in evidence.splitlines():
        if any(mark in line for mark in (*checks,"BOT finished")):
            print(line)


run("gate",81.5,30,(
    "wait,650|goto,81.5,36.3,7600|evalf,tmp/shinomen_verify.sk|"
    "goto,81.5,41.2,8500|untilmap,M458,11500"
),("SHINOMEN physical passage clear","BOT reached M458"),r'''
local a=::rpgstage.player3d;
if(::rpgstage.mapid!="M457" || Math.abs(a.pos.x-40.75)>.65 || a.pos.z<17.58 || a.pos.y>2.35)
    throw Exception("The party did not reach the roofed tunnel");
printf("SHINOMEN physical passage clear %S\n",a.pos);
''')


run("smith",40.5,16,(
    "wait,650|goto,40.5,21.6,7500|untilmap,M991,8000|"
    "evalf,tmp/shinomen_verify.sk|goto,17.5,12.2,6500|"
    "goto,17.5,7.2,7500|untilmap,M457,8000"
),("BOT reached M991","SHINOMEN smith registered","BOT reached M457"),r'''
local clerk=::rpgstage.getEvent(2);
if(::rpgstage.mapid!="M991" || !clerk || clerk.data.storeid!="R170")
    throw Exception("Wrong shop registration");
printf("SHINOMEN smith registered R170\n");
''')
