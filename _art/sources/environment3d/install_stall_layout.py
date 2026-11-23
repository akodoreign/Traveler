"""Replace the old closed M103 footprint while preserving all map events."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
repo = Path(sys.argv[1]).resolve()
tools = repo / "tools"
sys.path.insert(0, str(tools))
import engine_lock
import gen_maps as gm

source = tools / "gen_maps.py"
engine = repo / "_tools/rpgcobo-tool"
map_asset = engine / "project/data/mapdata/M103.bw"
map_setup = engine / "project/data/map.json"
before_asset = map_asset.read_bytes()
before_data = map_setup.read_bytes()
before_code = source.read_bytes()
old_scene, old_events = gm.make("M103")
old = b'    building(m, 86, 32, 7, 5, wall_h=3, wall=WOOD)                           # noodle stall'
new = (
    b'    # The open cedar noodle stall is dressed by the environment kit. Reserve its rear wall\n'
    b'    # and outer posts, with the street-facing approach open for Kiyo and Taneo.\n'
    b'    m.walls.extend([(x, 36) for x in range(83, 94)])\n'
    b'    m.walls.extend([(83, 32), (94, 32), (94, 36)])'
)
if b"\r\n" in before_code:
    new = new.replace(b"\n", b"\r\n")
assert before_code.count(old)==1 or before_code.count(new)==1
new_code = before_code.replace(old,new,1)
old_lamp = b"    for x in (24, 60, 84):"
lantern = b"        fb(m, x, 29, 2, LAMP_STREET)"
newline = b"\r\n" if b"\r\n" in new_code else b"\n"
start = new_code.index(b"def hoshi_town():")
stop = new_code.index(b"def after_line(",start)
town = new_code[start:stop]
assert town.count(old_lamp)==1 and town.count(lantern)==1
town = town.replace(old_lamp,b"    for x in (24, 60):",1)
town = town.replace(lantern,lantern+newline+b"    fb(m, 82, 30, 2, LAMP_STREET)",1)
new_code = new_code[:start]+town+new_code[stop:]
namespace=vars(gm).copy()
namespace["__name__"] = "gen_maps_stall_stage"
exec(compile(new_code,str(source),"exec"),namespace)
new_scene,new_events = namespace["make"]("M103")
assert old_events.ev == new_events.ev, "The existing event records changed in the stall stage"
assert (old_scene.blk == new_scene.blk).all() and (old_scene.hgt == new_scene.hgt).all()
assert len(new_scene.walls)>=len(old_scene.walls) and new_scene.objs!=old_scene.objs

job_dir=engine/"tmp/rt_mapgen"
job_file=job_dir/"job.json"
staged_map=job_dir/"M103_stall_candidate.bw"
assert not job_file.exists(), "The map generator already has a job"
job=new_scene.write()
job["out"]="tmp/rt_mapgen/M103_stall_candidate.bw"
job_file.write_text(json.dumps({"maps":[job]}),encoding="utf-8")
log = HERE / "hoshi-world-build.log"
try:
    with log.open("w",encoding="utf-8") as output:
        proc=engine_lock.launch([str(engine/"rpgcobo.exe"),"-testplay","-map","M103","[55,2,15,0]"],
                                cwd=engine,stdout=output,stderr=subprocess.STDOUT,tries=13)
        try:
            until=time.monotonic()+30
            while proc.poll() is None and time.monotonic()<until:
                if "RTMAPGEN done" in log.read_text(errors="replace"):
                    break
                time.sleep(.2)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
finally:
    job_file.unlink(missing_ok=True)
result=log.read_text(errors="replace")
if "RTMAPGEN built M103" not in result or "RTMAPGEN done" not in result or not staged_map.is_file():
    raise RuntimeError(result[-4400:])
assert source.read_bytes()==before_code and map_asset.read_bytes()==before_asset and map_setup.read_bytes()==before_data
after=staged_map.read_bytes()
assert after != before_asset and len(after)>15000
original = HERE/"M103-before-stall.bw"
if not original.exists():
    original.write_bytes(before_asset)
try:
    source.write_bytes(new_code)
    map_asset.write_bytes(after)
except BaseException:
    if source.read_bytes()!=before_code:
        source.write_bytes(before_code)
    if map_asset.read_bytes()!=before_asset:
        map_asset.write_bytes(before_asset)
    raise
meta={"map":"M103","events_unchanged":len(new_events.ev),"original_world_sha256":sha256(original.read_bytes()).hexdigest(),
      "installed_world_sha256":sha256(after).hexdigest(),"kept_data_map_json":True}
(HERE/"stall-layout.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print(meta)
