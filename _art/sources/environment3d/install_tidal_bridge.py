"""Install both native tide maps and connect them through the existing wait choice."""

from copy import deepcopy
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
DATA = ENGINE/"project/data"
MAPS = DATA/"map.json"
SOURCE = ROOT/"tools/gen_maps.py"
WORLDS = {mid:DATA/"mapdata"/f"{mid}.bw" for mid in ("M212","M236")}
before = {file:file.read_bytes() for file in (SOURCE,MAPS,WORLDS["M212"])}
assert not WORLDS["M236"].exists(), "M236 is already reserved"
sys.path.insert(0,str(SOURCE.parent))
import engine_lock
import gen_maps as gm

eol = "\r\n" if b"\r\n" in before[SOURCE] else "\n"
source = before[SOURCE].decode("utf8").replace("\r\n","\n")
section = (HERE/"tidal_bridge_map_section.py").read_text(encoding="utf8")
section = section[section.index("def tidal_bridge_banks"):].strip()


def replace(old,new):
    global source
    assert source.count(old)==1, old
    source=source.replace(old,new,1)


replace("def land_bridge():",section+"\n\n\ndef land_bridge():")
start = source.index('    m.rect(0, 13, 120, 7, SAND, 2)',source.index("def land_bridge():"))
end = source.index('    ev = Events(m)',start)
source = source[:start] + """    for x in range(120):
        center = 16 + int(1.8*np.sin((x-4)*.077)+.5*np.sin(x*.28))
        m.rect(x,center-4,1,9,SAND,2)
    tidal_bridge_banks(m)
    m.rect(70,21,6,5,SAND,2)
    m.rect(71,22,4,3,WATER,1)
""" + source[end:]
replace('south = ev.portal(108, 16, "M212", 1, d=3)','south = ev.portal(108, 16, "M236", 1, d=3)')
replace('    ev.portal(1, 16, "M212", 2, d=1)','    ev.portal(1, 16, "M236", 2, d=1)')
replace('MAPS_CRANE.update({"M212": land_bridge, "M213": yasuki_yashiki, "M219": yasuki_hall})',
        'MAPS_CRANE.update({"M212": land_bridge, "M213": yasuki_yashiki, "M219": yasuki_hall,\n'
        '                   "M236": tide_submerged})')
module = ModuleType("stage_tidal_bridge")
module.__dict__.update({key:value for key,value in vars(gm).items() if key!="__name__"})
sys.modules[module.__name__] = module
exec(compile(source,str(SOURCE),"exec"),module.__dict__)
maps = json.loads(before[MAPS])
assert "M236" not in maps and "M236" not in gm.MAPS
rows = []
for mid in WORLDS:
    world, events = module.make(mid)
    row = world.write()
    row["out"] = f"tmp/rt_mapgen/{mid}_tide_candidate.bw"
    rows.append(row)
    if mid=="M236":
        maps[mid] = deepcopy(maps["M212"])
        maps[mid].update(name=world.name,encount=[],encntrate=0.0,marker={},event=events.ev)
        assert all(int(world.blk[z,x])==module.WATER for x in range(40,132) for z in range(4,39))
    else:
        old, old_events = gm.make(mid)
        assert (world.w,world.d)==(old.w,old.d)
        for eid in ("#1#","#2#","#3#","#4#","#5#","#6#","#7#","#8#","#9#"):
            assert eid in events.ev and old_events.ev[eid]["pos"]==events.ev[eid]["pos"]
    maps[mid]["size"] = [world.w,64,world.d]
for mid,landing in (("M210",1),("M213",2)):
    matches=[event for event in maps[mid]["event"].values()
             if (event.get("dest") or {}).get("mapid")=="M212"]
    assert len(matches)==1 and matches[0]["dest"]["evid"]==landing, (mid,len(matches))
    matches[0]["dest"]["mapid"]="M236"

if "--check" in sys.argv[2:]:
    print("M210 and M213 lead to the matching bank. M236 is flooded and M212's IDs are preserved.")
    sys.exit()
job = ENGINE/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf8") as handle:
    json.dump({"maps":rows},handle)
log = HERE/"land-bridge-build.log"
try:
    with log.open("w",encoding="utf8") as output:
        proc = engine_lock.launch([str(ENGINE/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                 cwd=ENGINE,stdout=output,stderr=subprocess.STDOUT,tries=28)
        try:
            stop=time.monotonic()+36
            while proc.poll() is None and time.monotonic()<stop:
                if "RTMAPGEN done" in log.read_text(errors="replace"):
                    break
                time.sleep(.2)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
finally:
    job.unlink(missing_ok=True)
log_text = log.read_text(errors="replace")
assert "RTMAPGEN done" in log_text and "RTMAPGEN error" not in log_text, log_text[-3300:]
assert all(path.read_bytes()==value for path,value in before.items())
assert not WORLDS["M236"].exists()
renders = {row["id"]:(ENGINE/row["out"]).read_bytes() for row in rows}
changes = [
    (SOURCE,source.replace("\n",eol).encode()),
    (MAPS,json.dumps(maps,ensure_ascii=False,indent="\t").encode().replace(
        b"\n",b"\r\n" if b"\r\n" in before[MAPS] else b"\n")),
    *((WORLDS[mid],data) for mid,data in renders.items()),
]
(HERE/"M212-before-tidal-bridge.bw").write_bytes(before[WORLDS["M212"]])
written = []
try:
    for file,data in changes:
        mode = "r+b" if file in before else "xb"
        with file.open(mode) as handle:
            written.append(file)
            handle.write(data)
            handle.truncate()
except BaseException:
    for file in reversed(written):
        if file in before:
            with file.open("r+b") as handle:
                handle.write(before[file])
                handle.truncate()
        else:
            file.unlink()
    raise
(HERE/"land-bridge-build.json").write_text(
    json.dumps({mid:{"hash":sha256(data).hexdigest(),"size":maps[mid]["size"]}
                for mid,data in renders.items()},indent=2),encoding="utf8")
print("Published exposed M212 and submerged M236, with the two manual wait transitions.")
