"""Compile a rebuilt Hoshi hospitality interior around its original interactions."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType

here=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
mid=sys.argv[2]
kind,removed_slots={
    "M120":("inn",range(3,6)),
    "M121":("arms",range(3,7)),
    "M122":("goods",range(3,6)),
    "M123":("teahouse",range(4,9)),
    "M124":("magistrate",range(3,6)),
}[mid]
name=f"hoshi-{kind}"
function_name=f"rebuild_hoshi_{kind}"
engine=repo/"_tools/rpgcobo-tool"
project=engine/"project"
source=repo/"tools/gen_maps.py"
maps=project/"data/map.json"
world=project/"data/mapdata"/f"{mid}.bw"
baseline={path:path.read_bytes() for path in (source,maps,world)}
sys.path.insert(0,str(source.parent))
import gen_maps as gm
import engine_lock

code=baseline[source]
eol=b"\r\n" if b"\r\n" in code else b"\n"
anchor=b'    if i == "M103":'+eol+b"        ev.n = configure_hoshi_storehouse(ev.ev)"+eol
assert code.count(anchor)==1 and f"def {function_name}(".encode() not in code
script=(here/f"hoshi_{kind}_map_section.py").read_text(encoding="utf-8")
function=script[script.index(f"def {function_name}"):].strip().encode().replace(b"\n",eol)
use=f'    if i == "{mid}":\n        {function_name}(m, ev)\n'.encode().replace(b"\n",eol)
updated=code.replace(anchor,anchor+use,1)
mark=b"def configure_hoshi_storehouse(events):"
assert updated.count(mark)==1
updated=updated.replace(mark,function+eol*3+mark,1)
module=ModuleType(f"stage_hoshi_{kind}_world")
module.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
sys.modules[module.__name__]=module
exec(compile(updated,str(source),"exec"),module.__dict__)

old,original=gm.make(mid)
model,current=module.make(mid)
removed={f"#{id_}#" for id_ in removed_slots}
assert set(original.ev)-set(current.ev)==removed
assert all(original.ev[k]==value for k,value in current.ev.items())
assert model.w>old.w and model.d>old.d and len(model.objs)==5
cfg=json.loads(baseline[maps])
record=cfg[mid]
assert record["size"]==[old.w,64,old.d]
record["size"]=[model.w,64,model.d]
for key in removed:
    assert record["event"][key]["role"] in ("custom","light")
    del record["event"][key]

job=engine/"tmp/rt_mapgen/job.json"
ref=model.write()
ref["out"]=f"tmp/rt_mapgen/{mid}_{kind}_candidate.bw"
with job.open("x",encoding="utf-8") as file:
    json.dump({"maps":[ref]},file)
log=here/f"{name}-world-build.log"
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
text=log.read_text(errors="replace")
assert "RTMAPGEN done" in text and "RTMAPGEN error" not in text,text[-2400:]
new=(engine/ref["out"]).read_bytes()
assert new!=baseline[world] and all(path.read_bytes()==previous for path,previous in baseline.items())
map_eol=b"\r\n" if b"\r\n" in baseline[maps] else b"\n"
serial=json.dumps(cfg,ensure_ascii=False,indent="\t").encode().replace(b"\n",map_eol)


def overwrite(path, value):
    with path.open("r+b") as file:
        file.write(value)
        file.truncate()


(here/f"{mid}-before-{kind}-rebuild.bw").write_bytes(baseline[world])
written=[]
try:
    for path,value in ((world,new),(source,updated),(maps,serial)):
        written.append(path)
        overwrite(path,value)
except BaseException:
    for path in written:
        if path.read_bytes()!=baseline[path]:
            overwrite(path,baseline[path])
    raise
(here/f"{name}-world-build.json").write_text(json.dumps({"map":mid,"sha256":sha256(new).hexdigest(),
    "size":record["size"],"removed_stock":sorted(removed)},indent=2),encoding="utf-8")
print(f"Published the enlarged Hoshi {kind} with its doorway and story interactions preserved.")
