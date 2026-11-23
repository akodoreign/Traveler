"""Compile and publish the new M125 room while keeping its gameplay event IDs."""

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
maps=project/"data/map.json"
world=project/"data/mapdata/M125.bw"
baseline={path:path.read_bytes() for path in (source,maps,world)}
sys.path.insert(0,str(source.parent))
import gen_maps as gm
import engine_lock

code=baseline[source]
eol=b"\r\n" if b"\r\n" in code else b"\n"
begin=code.index(b"def storehouse():")
end=code.index(eol+b"INTERIORS =",begin)
fragment=(here/"storehouse_map_section.py").read_text(encoding="utf-8")
room=fragment[fragment.index("def storehouse():"):].strip().encode().replace(b"\n",eol)
updated=code[:begin]+room+eol*2+code[end:]
compiled=ModuleType("stage_hoshi_storehouse_world")
compiled.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
sys.modules[compiled.__name__]=compiled
exec(compile(updated,str(source),"exec"),compiled.__dict__)

old,old_events=gm.make("M125")
model,events=compiled.make("M125")
assert len(model.objs)==5 < len(old.objs)
assert set(old_events.ev)-set(events.ev)=={"#3#","#4#"}
assert events.ev["#1#"]["dest"]==old_events.ev["#1#"]["dest"]
assert events.ev["#2#"]["pos"]==old_events.ev["#2#"]["pos"]
assert all(old_events.ev[k]==events.ev[k] for k in events.ev if k not in ("#1#","#2#"))
cfg=json.loads(baseline[maps])
record=cfg["M125"]
assert record["size"]==[model.w,64,model.d]
runtime_events=record["event"]
assert set(runtime_events)==set(old_events.ev)
original_chest=runtime_events["#2#"].copy()
for key in ("#3#","#4#"):
    del runtime_events[key]
runtime_events["#1#"]["pos"]=events.ev["#1#"]["pos"]
runtime_events["#2#"]["mdl"]=events.ev["#2#"]["mdl"]
runtime_events["#2#"]["mdlid"]=events.ev["#2#"]["mdlid"]
assert all(runtime_events["#2#"][key]==original_chest[key] for key in ("num","itemid","pos","role"))

ref=model.write()
ref["out"]="tmp/rt_mapgen/M125_storehouse_candidate.bw"
job=engine/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf-8") as file:
    json.dump({"maps":[ref]},file)
log=here/"hoshi-storehouse-world-build.log"
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
assert "RTMAPGEN done" in result and "RTMAPGEN error" not in result,result[-2400:]
assert all(path.read_bytes()==previous for path,previous in baseline.items())
new=(engine/ref["out"]).read_bytes()
assert new!=baseline[world]
map_eol=b"\r\n" if b"\r\n" in baseline[maps] else b"\n"
serialized=json.dumps(cfg,ensure_ascii=False,indent="\t").encode().replace(b"\n",map_eol)
written=[]
try:
    for path,data in ((world,new),(source,updated),(maps,serialized)):
        written.append(path)
        path.write_bytes(data)
except BaseException:
    for path in written:
        path.write_bytes(baseline[path])
    raise
(here/"M125-before-storehouse-rebuild.bw").write_bytes(baseline[world])
(here/"hoshi-storehouse-world-build.json").write_text(json.dumps({"map":"M125",
    "sha256":sha256(new).hexdigest(),"exit":runtime_events["#1#"]["pos"],
    "loot":runtime_events["#2#"]["pos"],"removed_props":len(old.objs)-len(model.objs)+2},indent=2),encoding="utf-8")
print("Rebuilt the Hoshi storehouse's physical room. Its exit and loot retain their original IDs.")
