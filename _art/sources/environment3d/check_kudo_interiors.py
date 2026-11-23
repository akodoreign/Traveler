"""Walk through all three working Kudo doors and back to the street."""

from pathlib import Path
import subprocess
import sys
import time


repo=Path(sys.argv[1]).resolve()
profile=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(repo/"tools"))
import playbot


entries=(("M352",94,6),("M353",72,7),("M354",111,7))
selection=set(sys.argv[3:])

def round_trip(mid,outside,inside):
    tests = [
        f"goto,{outside+.4},25.8,9000",
        f"untilmap,{mid},8500",
        "wait,1200",
        f"evalf,tmp/check_kudo_{mid}.sk",
        f"goto,{inside+.25},15.2,6000",
        f"goto,{inside+.25},11.0,7000",
        "untilmap,M351,8500",
        "wait,900",
    ]
    filename=profile/"tmp"/f"check_kudo_{mid}.sk"
    filename.write_text(
        f'if(::rpgstage.mapid!="{mid}" || !::rpgstage.rtEnvironmentKit)\n'
        '    throw Exception("The furnished room did not load");\n'
        '::Rokugan.botleg = null;\n'
        f'printf("KUDO room {mid} installed and reached\\n");\n',encoding="utf8")
    log=Path(__file__).resolve().with_name(f"kudo-interior-{mid}-route.log")
    try:
        with log.open("w",encoding="utf8") as output:
            proc=subprocess.Popen([str(profile/"rpgcobo.exe"),"-testplay","-map","M351",
                playbot.start_pos("M351",outside+.4,21.2),"-rtfast","-rtlead","P105",
                "-rtvar","G845,G876,G861","-rtbot","wait,650|"+"|".join(tests)],
                cwd=profile,stdout=output,stderr=subprocess.STDOUT)
            try:
                until=time.monotonic()+43.
                while proc.poll() is None and time.monotonic()<until:
                    data=log.read_text(errors="replace")
                    if "BOT finished" in data or "NOT reached" in data:
                        break
                    time.sleep(.2)
            finally:
                if proc.poll() is None:
                    proc.kill()
                proc.wait(timeout=10)
    finally:
        filename.unlink(missing_ok=True)
    report=log.read_text(errors="replace")
    assert "BOT finished" in report and "NOT reached" not in report and "threw" not in report,report[-4500:]
    assert f"KUDO room {mid} installed and reached" in report and "BOT reached M351" in report
    for line in report.splitlines():
        if "KUDO room" in line or "BOT reached M351" in line:
            print(line)


for mid,outside,inside in entries:
    if not selection or mid in selection:
        round_trip(mid,outside,inside)
