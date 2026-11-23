"""Publish newly dressed Coast worlds after rebuilding only their prop footprints."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
source=repo/"tools/gen_maps.py"
engine=repo/"_tools/rpgcobo-tool"
runtime=engine/"project"
sys.path.insert(0,str(repo/"tools"))
import engine_lock
import gen_maps as gm

MAPS=("M102","M105","M811")
before_code=source.read_bytes()
needle=b"    return m, ev\n\n\nDEBUG_MAPS ="
if b"\r\n" in before_code:
    needle=needle.replace(b"\n",b"\r\n")
assert before_code.count(needle)==1 and b"m.environment_replaced" not in before_code
newlines=b"\r\n" if b"\r\n" in before_code else b"\n"
section=(
    b'    if i in {"M102", "M105", "M811"}:\n'
    b'        # The period Coast kit owns the visible props. Keep a no-entry footprint\n'
    b'        # at the old plants, stones and lights while preserving route markers.\n'
    b'        m.environment_replaced = [o for o in m.objs if o["t"] == "fb" and (\n'
    b'            o["fbtype"] == 20 or (o["fbtype"], o["fbparam"]) in ((3, 10), (3, 21), (2, 5)))]\n'
    b'        m.objs = [o for o in m.objs if o not in m.environment_replaced]\n'
    b'        m.walls.extend((o["x"],o["z"]) for o in m.environment_replaced if o["fbtype"] in (20,2))\n'
)
after_code=before_code.replace(needle,section.replace(b"\n",newlines)+needle,1)
fresh=vars(gm).copy()
fresh["__name__"]="stage_coast_worlds"
exec(compile(after_code,str(source),"exec"),fresh)
orig_worlds={mid: runtime/"data/mapdata"/f"{mid}.bw" for mid in MAPS}
original={mid:path.read_bytes() for mid,path in orig_worlds.items()}
registration=(runtime/"data/map.json").read_bytes()
environment=json.loads((runtime/"resource/native_environment/index.json").read_bytes())
jobs=[]
for mid in MAPS:
    old,old_events=gm.make(mid)
    model,events=fresh["make"](mid)
    assert old_events is None and events is None or old_events.ev==events.ev
    assert (model.blk==old.blk).all() and (model.hgt==old.hgt).all()
    assert len(model.environment_replaced)==len(old.objs)-len(model.objs)
    native=[row for row in environment[mid]["placements"] if row[0] in
            ("coast_pine","shore_talus","coast_lantern","egg_cave_arch","road_notice")]
    assert len(native)==len(model.environment_replaced)
    for asset,*_ in native:
        assert (runtime/"resource/native_environment"/f"{asset}.mdl").is_file()
    job=model.write()
    job["out"]=f"tmp/rt_mapgen/{mid}_environment_candidate.bw"
    jobs.append(job)

jobfile=engine/"tmp/rt_mapgen/job.json"
assert not jobfile.exists()
jobfile.write_text(json.dumps({"maps":jobs}),encoding="utf-8")
log=HERE/"coast-world-build.log"
try:
    with log.open("w",encoding="utf-8") as output:
        game=engine_lock.launch([str(engine/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                cwd=engine,stdout=output,stderr=subprocess.STDOUT,tries=20)
        try:
            until=time.monotonic()+40
            while game.poll() is None and time.monotonic()<until:
                if "RTMAPGEN done" in log.read_text(errors="replace"):
                    break
                time.sleep(.25)
        finally:
            if game.poll() is None:
                game.kill()
            game.wait(timeout=10)
finally:
    jobfile.unlink(missing_ok=True)
report=log.read_text(errors="replace")
assert "RTMAPGEN done" in report and "RTMAPGEN error" not in report
after={item["id"]:(engine/item["out"]).read_bytes() for item in jobs}
assert all(after[mid]!=original[mid] for mid in MAPS)
assert source.read_bytes()==before_code and (runtime/"data/map.json").read_bytes()==registration
staged={}
try:
    source.write_bytes(after_code)
    for mid,file in orig_worlds.items():
        assert file.read_bytes()==original[mid]
        backup=HERE/f"{mid}-before-environment.bw"
        if not backup.exists():
            backup.write_bytes(original[mid])
        staged[mid]=file
        file.write_bytes(after[mid])
except BaseException:
    source.write_bytes(before_code)
    for mid,file in staged.items():
        file.write_bytes(original[mid])
    raise
manifest={mid:{"previous_sha256":sha256(original[mid]).hexdigest(),"current_sha256":sha256(after[mid]).hexdigest()}
          for mid in MAPS}
(HERE/"coast-world-build.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print("Rebuilt the three Coast Road worlds. At map level, placed props changed and event data stayed identical.")
