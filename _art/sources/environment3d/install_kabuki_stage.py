"""Replace the North Garden stage's stock scenery while keeping its performance events."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1])
ENGINE = ROOT/"_tools/rpgcobo-tool"
SOURCE = ROOT/"tools/gen_maps.py"
WORLD = ENGINE/"project/data/mapdata/M555.bw"
before_src,before_world = SOURCE.read_bytes(),WORLD.read_bytes()
eol = "\r\n" if b"\r\n" in before_src else "\n"
src = before_src.decode("utf8").replace("\r\n","\n")
sys.path.insert(0,str(SOURCE.parent))
import engine_lock
import gen_maps as gm

start = src.index("def kabuki_stage(m, ev):")
end = src.index("\n\nCASTLE_STORY[DOJI",start)
section = src[start:end]
curtain = section.index("    for i, x in enumerate(range(31, 66, 3)):")
walkway = section.index("    m.rect(33, 38",curtain)
section = (section[:curtain] +
           "    # The native fitted backdrop takes the place of the stock curtain.\n"
           "    m.walls.extend((x, 61) for x in range(30, 67))\n" +
           section[walkway:])
lamps = '    for x, z in ((29, 49), (67, 49), (29, 60), (67, 60)):\n        fb(m, x, z, 2, LAMP_STREET)\n'
assert section.count(lamps)==1
section = section.replace(lamps,"",1)
new_src = src[:start]+section+src[end:]
module = ModuleType("stage_north_garden")
module.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
sys.modules[module.__name__] = module
exec(compile(new_src,str(SOURCE),"exec"),module.__dict__)
original,events = gm.make("M555")
new,staged = module.make("M555")
assert events.ev==staged.ev
assert (original.hgt==new.hgt).all() and (original.blk==new.blk).all()
assert len(original.objs)-len(new.objs)>=13
if "--check" in sys.argv[2:]:
    print(f"M555 performance and audience events preserved. {len(original.objs)-len(new.objs)} stock fixtures can be removed.")
    sys.exit()
entry = new.write()
entry["out"] = "tmp/rt_mapgen/M555_kabuki_candidate.bw"
job = ENGINE/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf8") as handle:
    json.dump({"maps":[entry]},handle)
log = HERE/"kabuki-stage-build.log"
try:
    with log.open("w",encoding="utf8") as output:
        proc = engine_lock.launch([str(ENGINE/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                 cwd=ENGINE,stdout=output,stderr=subprocess.STDOUT,tries=30)
        try:
            cutoff = time.monotonic()+36
            while proc.poll() is None and time.monotonic()<cutoff:
                if "RTMAPGEN done" in log.read_text(errors="replace"):
                    break
                time.sleep(.2)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
finally:
    job.unlink(missing_ok=True)
contents = log.read_text(errors="replace")
assert "RTMAPGEN done" in contents and "RTMAPGEN error" not in contents,contents[-2800:]
assert SOURCE.read_bytes()==before_src and WORLD.read_bytes()==before_world
payload = (ENGINE/entry["out"]).read_bytes()
assert payload!=before_world
(HERE/"M555-before-kabuki-stage.bw").write_bytes(before_world)


def write(file,data):
    with file.open("r+b") as handle:
        handle.write(data)
        handle.truncate()


try:
    write(WORLD,payload)
    write(SOURCE,new_src.replace("\n",eol).encode())
except BaseException:
    write(WORLD,before_world)
    write(SOURCE,before_src)
    raise
(HERE/"kabuki-stage-build.json").write_text(json.dumps({
    "map":"M555","removed_fixtures":len(original.objs)-len(new.objs),
    "shared_story_events":len(events.ev),"hash":sha256(payload).hexdigest(),
},indent=2),encoding="utf8")
print("The rebuilt north garden stage preserves the original deck paths, audience and dialogue trigger.")
