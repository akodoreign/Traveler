"""Compile the three recessed tunnel worlds without changing their story events."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType

HERE=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
sys.path.insert(0,str(repo/"tools"))
import gen_maps as gm
import engine_lock

MAPS=("M102","M105","M437")
engine=repo/"_tools/rpgcobo-tool"
project=engine/"project"
source=repo/"tools/gen_maps.py"
files={mid:project/"data/mapdata"/f"{mid}.bw" for mid in MAPS}
original={mid:dest.read_bytes() for mid,dest in files.items()}
for dest in files.values():
    with dest.open("r+b"):
        pass

code=source.read_bytes()
eol=b"\r\n" if b"\r\n" in code else b"\n"
marker=b"    return m, ev"+eol*3+b"DEBUG_MAPS ="
assert code.count(marker)==1 and b"carve_environment_cave(m)" not in code
fragment=(HERE/"carve_cave_entrance.py").read_text(encoding="utf-8")
function=fragment[fragment.index("def carve_environment_cave"):].strip().replace("\n",eol.decode()).encode()
use=b'    if i in ("M102", "M105", "M437"):'+eol+b"        carve_environment_cave(m)"+eol
updated=code.replace(marker,use+b"    return m, ev"+eol*3+function+eol*3+b"DEBUG_MAPS =",1)
temp=ModuleType("stage_recessed_caves")
temp.__dict__.update({name:value for name,value in vars(gm).items() if name!="__name__"})
sys.modules[temp.__name__]=temp
exec(compile(updated,str(source),"exec"),temp.__dict__)

registration=(project/"data/map.json").read_bytes()
jobs = []
records = {}
for mid in MAPS:
    before,events=gm.make(mid)
    after,built_events=temp.make(mid)
    assert events.ev==built_events.ev
    assert before.walls==after.walls and (before.w,before.d)==(after.w,after.d)
    cut=after.environment_tunnel
    assert len(cut["roof"])>=50
    for left,right,z,y in cut["path"]:
        assert after.hgt[z,left:right].min()==after.hgt[z,left:right].max()==y
        assert left+2 <= cut["x"] < right-2
        assert all(not (px==cut["x"] and pz==z) for px,pz in after.walls)
    assert all(roof[1]>=8 for roof in cut["roof"] if roof[0]==cut["x"])
    ref=after.write()
    ref["out"]=f"tmp/rt_mapgen/{mid}_entrance_candidate.bw"
    jobs.append(ref)
    records[mid]={"entrance_cell":[cut["x"],cut["z"]],
                  "unchanged_events":len(events.ev),"roof_blocks":len(cut["roof"])}

job=engine/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf-8") as file:
    json.dump({"maps":jobs},file)
log=HERE/"recessed-caves-world-build.log"
try:
    with log.open("w",encoding="utf-8") as output:
        proc=engine_lock.launch([str(engine/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                cwd=engine,stdout=output,stderr=subprocess.STDOUT,tries=16)
        try:
            deadline=time.monotonic()+45
            while time.monotonic()<deadline and proc.poll() is None:
                if "RTMAPGEN done" in log.read_text(errors="replace"):
                    break
                time.sleep(.2)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
finally:
    job.unlink(missing_ok=True)

result=log.read_text(errors="replace")
assert "RTMAPGEN error" not in result and "RTMAPGEN done" in result,result[-3000:]
assert source.read_bytes()==code and (project/"data/map.json").read_bytes()==registration
new={row["id"]:(engine/row["out"]).read_bytes() for row in jobs}
written=[]
try:
    for mid,dest in files.items():
        assert dest.read_bytes()==original[mid] and new[mid]!=original[mid]
        backup=HERE/f"{mid}-before-recessed-cave.bw"
        if not backup.exists():
            backup.write_bytes(original[mid])
        written.append(mid)
        dest.write_bytes(new[mid])
        records[mid].update(previous=sha256(original[mid]).hexdigest(),current=sha256(new[mid]).hexdigest())
    source.write_bytes(updated)
except BaseException:
    for mid in written:
        files[mid].write_bytes(original[mid])
    if source.read_bytes()!=code:
        source.write_bytes(code)
    raise

(HERE/"recessed-caves-world-build.json").write_text(json.dumps(records,indent=2),encoding="utf-8")
print("Carved the Egg Caves' two approaches and the Oracle's lava tube. Existing events are unchanged.")
