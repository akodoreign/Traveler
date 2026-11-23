"""Compile the physical Hiruma climb and Kudo's continuous road connection."""

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1])
ENGINE = ROOT/"_tools/rpgcobo-tool"
DATA = ENGINE/"project/data"
SOURCE = ROOT/"tools/gen_maps.py"
MAP_DATA = DATA/"map.json"
sys.path.insert(0,str(SOURCE.parent))
import engine_lock
import gen_maps as gm

ward_only = "--ward-only" in sys.argv[2:]
fallen_only = "--fallen" in sys.argv[2:]
maze_only = "--maze" in sys.argv[2:]
assert sum((ward_only,fallen_only,maze_only))<=1
targets = (tuple(gm.MAZE) if maze_only else ("M458",) if fallen_only else
           ("M351",) if ward_only else ("M351","M460"))
world_paths = {mid: DATA/"mapdata"/f"{mid}.bw" for mid in targets}
before = {p:p.read_bytes() for p in (SOURCE,MAP_DATA,*world_paths.values())}
source = before[SOURCE]
eol = b"\r\n" if b"\r\n" in source else b"\n"
old_source = source.decode("utf8")
updated = old_source.replace("\r\n","\n")


def replace(first, second):
    global updated
    assert updated.count(first)==1, first
    updated = updated.replace(first,second,1)


if maze_only:
    fragment = (HERE/"shifting_waste_map_section.py").read_text(encoding="utf8").strip()
    fragment = fragment[fragment.index("def shifting_waste_paths"):].strip()
    replace("def shifting_waste(k):",fragment+"\n\n\ndef shifting_waste(k):")
    anchor = "    m, ev = r if isinstance(r, tuple) else (r, None)\n    if i == \"M458\":\n        rebuild_fallen_road(m)"
    replace(anchor,anchor+"\n    if i in MAZE:\n        rebuild_shifting_waste(m, MAZE.index(i)+1)")
elif fallen_only:
    fragment = (HERE/"fallen_road_map_section.py").read_text(encoding="utf8").strip()
    fragment = fragment[fragment.index("FALLEN_TRAIL = "):]
    replace("def deep_road_1():",fragment+"\n\n\ndef deep_road_1():")
    anchor = "    m, ev = r if isinstance(r, tuple) else (r, None)\n    if ev is not None:\n        _castle_town_access(i, m, ev)"
    replace(anchor,"    m, ev = r if isinstance(r, tuple) else (r, None)\n"
                   "    if i == \"M458\":\n        rebuild_fallen_road(m)\n"
                   "    if ev is not None:\n        _castle_town_access(i, m, ev)")
elif not ward_only:
    fragment = (HERE/"hiruma_road_map_section.py").read_text(encoding="utf8").strip()
    fragment = fragment[fragment.index("HIRUMA_TRAIL = "):]
    start = updated.index("def deep_road_3():")
    end = updated.index("\n\ndef shrine_pg_marker",start)
    updated = updated[:start] + fragment + "\n" + updated[end:]
    replace('    ev.talk(1, 16, "CE000", [(None, [go("M460", 104, 16)])], trigger=5)',
            '    ev.talk(1, 16, "CE000", [(None, [go("M460", 104, 41)])], trigger=5)')
    kudo = updated.index("def kudo():")
    physical = '    m.rect(10, 14, 102, 6, ROAD, 3)'
    entry = updated.index(physical,kudo)
    updated = updated[:entry] + (
        "    # The raised west approach meets the river road between the working docks.\n"
        "    m.rect(0, 10, 15, 6, ROAD, 3)\n" + updated[entry:]
    )
    replace('    ev.portal(110, 16, "M350", 2, d=3)',
            '    ev.portal(1, 12, "M350", 2, d=3)  ')
    replace('    ev.scene(104, 16, "G845", S04_SCP1, after=[flag("G840")])',
            '    ev.scene(15, 15, "G845", S04_SCP1, after=[flag("G840")])')
if not (fallen_only or maze_only):
    replace('"district": "Caravan Market", "clan": "Scorpion", "prop": "bottle",',
            '"district": "Caravan Market", "clan": "Scorpion", "prop": "bottle", "preferred_edge": "b",')
    replace('def _ward_edge_tile(m, ev):','def _ward_edge_tile(m, ev, preferred=None):')
    replace('    for rank, side in enumerate(sorted("fewb", key=lambda s: (s in used, "fewb".index(s)))):',
            '    order = sorted("fewb", key=lambda side: (side != preferred, side in used, "fewb".index(side)))\n'
            '    for rank, side in enumerate(order):')
    replace('    spot = _ward_edge_tile(m, ev)','    spot = _ward_edge_tile(m, ev, region.get("preferred_edge"))')
module = ModuleType("stage_shadowlands_routes")
module.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
sys.modules[module.__name__] = module
exec(compile(updated,str(SOURCE),"exec"),module.__dict__)

maps = json.loads(before[MAP_DATA])
jobs, report = [], {}


def merge_change(previous, revised, live, route):
    if previous==revised:
        return live
    if isinstance(previous,dict) and isinstance(revised,dict) and isinstance(live,dict):
        result = dict(live)
        for key in previous.keys()-revised.keys():
            assert result[key]==previous[key], (route,key)
            del result[key]
        for key in revised.keys()-previous.keys():
            assert key not in result or result[key]==revised[key], (route,key)
            result[key] = revised[key]
        for key in previous.keys() & revised.keys():
            if previous[key]!=revised[key]:
                result[key] = merge_change(previous[key],revised[key],result[key],(*route,key))
        return result
    if isinstance(previous,list) and isinstance(revised,list) and isinstance(live,list):
        if len(previous)==len(revised)==len(live):
            return [merge_change(p,r,c,(*route,index))
                    for index,(p,r,c) in enumerate(zip(previous,revised,live))]
    assert live==previous or live==revised, (route,live,previous)
    return revised


for mid in targets if ward_only or fallen_only or maze_only else (*targets,"M461"):
    old_model, old_events = gm.make(mid)
    model, new_events = module.make(mid)
    original = json.loads(json.dumps(old_events.ev))
    revised = json.loads(json.dumps(new_events.ev))
    changed = {eid:event for eid,event in revised.items() if event!=original.get(eid)}
    assert set(original)==set(revised), mid
    current = maps[mid]
    assert all(eid in current["event"] for eid in changed), (mid,sorted(changed))
    # The built-in world bits, flag tests, and commands are retained where their event doesn't move.
    for eid,event in changed.items():
        active = current["event"][eid]
        if (mid,eid)==("M460","#5#"):
            live_commands = active["page"][0]["cmdblock"]
            next_commands = event["page"][0]["cmdblock"]
            assert [cmd["cmd"] for cmd in live_commands]==[
                "cmd_showmsg","cmd_showmsg","cmd_compute","cmd_choices"]
            assert live_commands[2]["lvar"]=="G1215"
            event["page"][0]["cmdblock"] = [
                next_commands[0],live_commands[2],next_commands[2],
                live_commands[1],live_commands[3],
            ]
            original[eid]["page"][0]["cmdblock"] = live_commands
        current["event"][eid] = merge_change(original[eid],event,active,(mid,eid))
    if mid in world_paths:
        assert current["size"]==[old_model.w,64,old_model.d]
        current["size"] = [model.w,64,model.d]
        row = model.write()
        row["out"] = f"tmp/rt_mapgen/{mid}_routes_candidate.bw"
        jobs.append(row)
    report[mid] = {"changed_events":sorted(changed),"size":current["size"]}
    if mid=="M351":
        expected={"#101#","#102#"} if ward_only else {"#1#","#7#","#99#"}
        assert set(changed)==expected, set(changed)
        assert ("#99#","w") in model.edge_out
        assert ("#101#","b") in model.edge_out
        assert new_events.ev["#99#"]["dest"]==original["#99#"]["dest"]
    if mid=="M460":
        assert model.d>old_model.d and model.hgt.max()>=9
        assert int(model.hgt[20,31])==3
        assert int(model.hgt[46,130])>=8
    if mid=="M458":
        assert model.w==old_model.w and model.d>old_model.d
        assert all(new_events.ev[k]["page"]==old_events.ev[k]["page"] for k in changed)
    if mid in gm.MAZE:
        assert (model.w,model.d)==(old_model.w,old_model.d)
        assert all((original[k].get("page")==revised[k].get("page") and
                    original[k].get("dest")==revised[k].get("dest")) for k in original)

if "--check" in sys.argv[2:]:
    print(report)
    sys.exit()

job = ENGINE/"tmp/rt_mapgen/job.json"
with job.open("x",encoding="utf8") as handle:
    json.dump({"maps":jobs},handle)
log = HERE/"shadowlands-routes-build.log"
try:
    with log.open("w",encoding="utf8") as output:
        proc = engine_lock.launch([str(ENGINE/"rpgcobo.exe"),"-testplay","-map","M102","[25,2,11,0]"],
                                 cwd=ENGINE,stdout=output,stderr=subprocess.STDOUT,tries=27)
        try:
            until = time.monotonic()+45
            while proc.poll() is None and time.monotonic()<until:
                if "RTMAPGEN done" in log.read_text(errors="replace"):
                    break
                time.sleep(.20)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
finally:
    job.unlink(missing_ok=True)
log_data = log.read_text(errors="replace")
assert "RTMAPGEN done" in log_data and "RTMAPGEN error" not in log_data, log_data[-2500:]
assert all(p.read_bytes()==data for p,data in before.items()), "Source or map data changed during build"


def overwrite(path, data):
    with path.open("r+b") as handle:
        handle.write(data)
        handle.truncate()


map_eol = b"\r\n" if b"\r\n" in before[MAP_DATA] else b"\n"
new_map = json.dumps(maps,ensure_ascii=False,indent="\t").encode().replace(b"\n",map_eol)
replacements = [(SOURCE,updated.encode().replace(b"\n",eol)),(MAP_DATA,new_map)]
for row in jobs:
    mid = row["id"]
    data = (ENGINE/row["out"]).read_bytes()
    replacements.append((world_paths[mid],data))
    report[mid]["sha256"] = sha256(data).hexdigest()
    backup_label = "ward-repin" if ward_only else "route-rebuild"
    (HERE/f"{mid}-before-{backup_label}.bw").write_bytes(before[world_paths[mid]])
written = []
try:
    for path,data in replacements:
        written.append(path)
        overwrite(path,data)
except BaseException:
    for path in reversed(written):
        overwrite(path,before[path])
    raise
receipt = ("shifting-waste-world-build.json" if maze_only else
           "fallen-road-world-build.json" if fallen_only else "kudo-ward-repin.json"
           if ward_only else "shadowlands-routes-build.json")
(HERE/receipt).write_text(json.dumps(report,indent=2),encoding="utf8")
print(report)
