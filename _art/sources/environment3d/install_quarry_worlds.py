"""Compile the camp and arena with the old tents and free blocks removed."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType

HERE=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
engine=repo/"_tools/rpgcobo-tool"
project=engine/"project"
source=repo/"tools/gen_maps.py"
sys.path.insert(0,str(source.parent))
import gen_maps as gm
import engine_lock

ids=("M104","M812")
worlds={mid:project/"data/mapdata"/f"{mid}.bw" for mid in ids}
old={mid:file.read_bytes() for mid,file in worlds.items()}
code=source.read_bytes()
eol=b"\r\n" if b"\r\n" in code else b"\n"
new=code


def revise(first,second):
    global new
    first,second=(s.encode().replace(b"\n",eol) for s in (first,second))
    assert new.count(first)==1,first
    new=new.replace(first,second,1)


revise("        tent(m, x, z)\n    m.tree(40, 21, ROCK_S)",
       "        quarry_shelter(m, x, z)\n    m.tree(40, 21, ROCK_S)")
revise("        tent(m, x, 78)\n    for x in range(8, 128, 13):",
       "        quarry_shelter(m, x, 78)\n    for x in range(8, 128, 13):")
fragment=(HERE/"quarry_map_section.py").read_text(encoding="utf-8")
fragment=fragment[fragment.index("def quarry_shelter"):].strip()
revise("def quarry_camp():",fragment+"\n\n\ndef quarry_camp():")
revise('''    if i == "M120":
        rebuild_hoshi_inn(m, ev)''','''    if i == "M120":
        rebuild_hoshi_inn(m, ev)
    if i in ("M104", "M812"):
        m.quarry_replaced = [o for o in m.objs if o["t"] == "fb" and o["fbtype"] == 20]
        m.objs = [o for o in m.objs if o not in m.quarry_replaced]
        m.walls.extend((o["x"], o["z"]) for o in m.quarry_replaced)''')
module=ModuleType("stage_quarry_worlds")
module.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
sys.modules[module.__name__]=module
exec(compile(new,str(source),"exec"),module.__dict__)

report={}
jobs=[]
for mid in ids:
    before,events=gm.make(mid)
    after,fitted=module.make(mid)
    assert events.ev==fitted.ev
    assert (before.hgt==after.hgt).all() and (before.blk==after.blk).all()
    assert len(after.quarry_shelters)==(4 if mid=="M104" else 3)
    removed=len(before.objs)-len(after.objs)
    assert removed==len(after.quarry_replaced)+6*len(after.quarry_shelters)
    report[mid]={"removed_stock_entries":removed,"new_tents":len(after.quarry_shelters)}
    row=after.write()
    row["out"]=f"tmp/rt_mapgen/{mid}_quarry_candidate.bw"
    jobs.append(row)

job=engine/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf-8") as file:
    json.dump({"maps":jobs},file)
log=HERE/"quarry-world-build.log"
try:
    with log.open("w",encoding="utf-8") as output:
        proc=engine_lock.launch([str(engine/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                cwd=engine,stdout=output,stderr=subprocess.STDOUT,tries=16)
        try:
            cutoff=time.monotonic()+42
            while time.monotonic()<cutoff and proc.poll() is None:
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
assert "RTMAPGEN done" in result and "RTMAPGEN error" not in result,result[-2400:]
payload={row["id"]:(engine/row["out"]).read_bytes() for row in jobs}
assert source.read_bytes()==code
written=[]
try:
    for mid,file in worlds.items():
        assert file.read_bytes()==old[mid] and payload[mid]!=old[mid]
        (HERE/f"{mid}-before-quarry-rebuild.bw").write_bytes(old[mid])
        written.append(mid)
        file.write_bytes(payload[mid])
        report[mid]["sha256"]=sha256(payload[mid]).hexdigest()
    source.write_bytes(new)
except BaseException:
    for mid in written:
        worlds[mid].write_bytes(old[mid])
    if source.read_bytes()!=code:
        source.write_bytes(code)
    raise
(HERE/"quarry-world-build.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("Published the new quarry camp and arena.",report)
