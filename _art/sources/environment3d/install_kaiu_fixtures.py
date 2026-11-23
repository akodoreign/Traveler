"""Publish the three Kaiu worlds with their replaced stock fixtures removed."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType

here=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
engine=repo/"_tools/rpgcobo-tool"
project=engine/"project"
source=repo/"tools/gen_maps.py"
sys.path.insert(0,str(source.parent))
import gen_maps as gm
import engine_lock

counts={"M100":4,"M101":7,"M810":9}
files={mid:project/"data/mapdata"/f"{mid}.bw" for mid in counts}
original={mid:file.read_bytes() for mid,file in files.items()}
for file in files.values():
    with file.open("r+b"):
        pass

code=source.read_bytes()
eol=b"\r\n" if b"\r\n" in code else b"\n"
anchor=b'    if i == "M103":'+eol+b"        ev.n = configure_hoshi_storehouse(ev.ev)"+eol
assert code.count(anchor)==1 and b"m.kaiu_replaced =" not in code
insert='''    if i in ("M100", "M101", "M810"):
        m.kaiu_replaced = [o for o in m.objs if o["t"] == "fb" and
                           (o["fbtype"], o["fbparam"]) in ((2, 5), (2, 6), (30, 2))]
        m.objs = [o for o in m.objs if o not in m.kaiu_replaced]
        m.walls.extend((o["x"], o["z"]) for o in m.kaiu_replaced if o["fbtype"] == 30)
'''
updated=code.replace(anchor,anchor+insert.encode().replace(b"\n",eol),1)
module=ModuleType("stage_kaiu_fixture_worlds")
module.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
sys.modules[module.__name__]=module
exec(compile(updated,str(source),"exec"),module.__dict__)

staged=json.loads((here/"native_environment/index.json").read_bytes())
jobs=[]
for mid,count in counts.items():
    before,old_events=gm.make(mid)
    after,new_events=module.make(mid)
    assert (old_events is None and new_events is None) or old_events.ev==new_events.ev
    assert (before.hgt==after.hgt).all() and (before.blk==after.blk).all()
    assert len(after.kaiu_replaced)==count==len(before.objs)-len(after.objs)
    expected_lights=sum(o["fbtype"]==2 for o in after.kaiu_replaced)
    assert len(staged[mid]["watchfires"])==expected_lights
    row=after.write()
    row["out"]=f"tmp/rt_mapgen/{mid}_kaiu_fixture_candidate.bw"
    jobs.append(row)
map_data=(project/"data/map.json").read_bytes()
job=engine/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf-8") as file:
    json.dump({"maps":jobs},file)
log=here/"kaiu-fixture-world-build.log"
try:
    with log.open("w",encoding="utf-8") as output:
        proc=engine_lock.launch([str(engine/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                cwd=engine,stdout=output,stderr=subprocess.STDOUT,tries=16)
        try:
            deadline=time.monotonic()+42
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
assert "RTMAPGEN done" in result and "RTMAPGEN error" not in result, result[-2400:]
assert source.read_bytes()==code and (project/"data/map.json").read_bytes()==map_data
new={row["id"]:(engine/row["out"]).read_bytes() for row in jobs}
written=[]
report={}
try:
    for mid,dest in files.items():
        assert dest.read_bytes()==original[mid] and new[mid]!=original[mid]
        backup=here/f"{mid}-before-kaiu-fixtures.bw"
        if not backup.exists():
            backup.write_bytes(original[mid])
        written.append(mid)
        dest.write_bytes(new[mid])
        report[mid]={"replaced":counts[mid],"sha256":sha256(new[mid]).hexdigest()}
    source.write_bytes(updated)
except BaseException:
    for mid in written:
        files[mid].write_bytes(original[mid])
    if source.read_bytes()!=code:
        source.write_bytes(code)
    raise
(here/"kaiu-fixture-world-build.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("Published 20 stock fixture replacements on the Kaiu Wall maps.")
