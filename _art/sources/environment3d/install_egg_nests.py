"""Remove the M130 placeholder blossoms now that woven nest assets exist."""

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

repo=Path(sys.argv[1])
sys.path.insert(0,str(repo/"tools"))
import gen_maps as gm
import engine_lock

HERE=Path(__file__).resolve().parent
engine=repo/"_tools/rpgcobo-tool"
runtime=engine/"project"
source=repo/"tools/gen_maps.py"
world=runtime/"data/mapdata/M130.bw"
index=json.loads((HERE/"native_environment/index.json").read_bytes())
assert sum(row[0]=="egg_nest" for row in index["M130"]["placements"])>=3

original_source=source.read_bytes()
original_world=world.read_bytes()
linebreak=b"\r\n" if b"\r\n" in original_source else b"\n"
old=(
    b"    for x, z in ((28, 15), (33, 20), (40, 14), (44, 19)):                 # straw nests (yellow flowers as straw)",
    b"        m.block(x, z, TUFT)",
)
old=linebreak.join(old)+linebreak
new=b"    # The environment kit sets woven nests on the cave floor."+linebreak
assert original_source.count(old)==1
updated_source=original_source.replace(old,new)
candidate_module=ModuleType("stage_egg_nests")
candidate_namespace=vars(candidate_module)
candidate_namespace.update({name:value for name,value in vars(gm).items() if name!="__name__"})
sys.modules[candidate_module.__name__]=candidate_module
exec(compile(updated_source,str(source),"exec"),candidate_namespace)
original,original_events=gm.make("M130")
candidate,candidate_events=candidate_namespace["make"]("M130")
assert (original.blk==candidate.blk).all() and (original.hgt==candidate.hgt).all()
assert original_events.ev==candidate_events.ev
assert original.walls==candidate.walls
removed=[o for o in original.objs if o not in candidate.objs]
assert len(removed)==4 and all(o["t"]=="blk" and o["blk"]==gm.TUFT for o in removed)
assert not any(o not in original.objs for o in candidate.objs)

ref=candidate.write()
ref["out"]="tmp/rt_mapgen/M130_environment_candidate.bw"
job=engine/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf-8") as file:
    json.dump({"maps":[ref]},file)

log=HERE/"egg-nests-world-build.log"
try:
    with log.open("w",encoding="utf-8") as output:
        proc=engine_lock.launch([str(engine/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                cwd=engine,stdout=output,stderr=output,tries=14)
        try:
            code=proc.wait(timeout=45)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)
finally:
    job.unlink(missing_ok=True)

result=log.read_text(errors="replace")
assert "RTMAPGEN done" in result and "RTMAPGEN error" not in result,result[-2500:]
updated_world=(engine/ref["out"]).read_bytes()
assert updated_world!=original_world
assert source.read_bytes()==original_source and world.read_bytes()==original_world
backup=HERE/"M130-before-nests.bw"
if not backup.exists():
    backup.write_bytes(original_world)
world.write_bytes(updated_world)
try:
    source.write_bytes(updated_source)
except BaseException:
    world.write_bytes(original_world)
    raise
hashes={label:sha256(blob).hexdigest() for label,blob in (("previous",original_world),("published",updated_world))}
(HERE/"egg-nests-world-build.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
print("Published M130 with four placeholder flowers removed and identical event data.")
