"""Native layout changes for the Shinomen gate and Shadowlands battle bowl."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType


HERE = Path(__file__).resolve().parent
MAPS = ("M457", "M817", "M991")
SHOP_DECOR = ("#3#", "#4#")


def shop_world(gm):
    """Replace the generic interior while preserving its existing portal and clerk."""
    m=gm.MapSpec("M991","Kaiu Wall - the Shinomen gate - Shop",34,32,base=0,y=0)
    m.rect(3,6,28,21,gm.PLANK,1)
    m.rect(3,6,1,21,gm.STONEW,5)
    m.rect(30,6,1,21,gm.STONEW,5)
    m.rect(3,26,28,1,gm.STONEW,5)
    m.rect(3,6,12,1,gm.STONEW,2)
    m.rect(19,6,12,1,gm.STONEW,2)
    m.rect(15,5,4,2,gm.STONEW,1)
    m.walls.extend((x,z) for x in range(21,25) for z in range(21,24))
    return m


def revised_source(text):
    # Cut through the full thickness of the Wall and move the existing gate
    # choice within its roofed passage. Returning from the Fallen Road still
    # lands in the courtyard, south of the trigger.
    start = text.index("def wall_shinomen_gate():")
    end = text.index("\ndef deep_road(", start)
    gate = text[start:end]
    before = '    fill(m, 52, 3, 30, 7, 9, 1, VOID)'
    after = ('    m.rect(52, 30, 7, 10, ROAD, 2)\n'
             '    fill(m, 52, 12, 30, 7, 5, 10, KAIU)')
    assert gate.count(before) + gate.count(after) == 1
    if before in gate:
        gate = gate.replace(before,after).replace(
            '    ev.talk(55, 28, "CE000"', '    gate_event = ev.talk(55, 34, "CE000"')
        gate = gate.replace("    return m, ev", '    ev.ev[f"#{gate_event}#"]["pos"][1] = 3\n    return m, ev')
    gate = gate.replace("    for x in (6, 46, 64):\n        fb(m, x, 15, 2, LAMP_STREET)\n","")
    text = text[:start] + gate + text[end:]

    start = text.index("def battle_shadowlands():")
    end = text.index("\ndef battle_road_home(", start)
    arena = text[start:end]
    rocks = """    for x in range(6, 128, 12):
        m.tree(x, 84 + (x * 5) % 6, (TREE_L, TREE_M)[x % 2])
"""
    return text[:start] + arena.replace(rocks, "") + text[end:]


def variant(repo):
    source = repo/"tools/gen_maps.py"
    sys.path.insert(0,str(source.parent))
    import gen_maps as original

    raw = source.read_bytes()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf8").replace("\r\n","\n")
    changed = revised_source(text)
    module = ModuleType("shinomen_gate_candidate")
    module.__dict__.update({key:value for key,value in vars(original).items() if key!="__name__"})
    sys.modules[module.__name__]=module
    exec(compile(changed,str(source),"exec"),module.__dict__)
    return original, module, raw, changed.replace("\n",eol).encode("utf8")


def overwrite(path,data):
    with path.open("r+b") as file:
        file.write(data)
        file.truncate()


def main(repo,engine,publish):
    original, changed, source_before, source_after = variant(repo)
    source = repo/"tools/gen_maps.py"
    live = repo/"_tools/rpgcobo-tool/project/data"
    map_path = live/"map.json"
    live_maps = json.loads(map_path.read_bytes())
    updates = {}
    changed.JOBDIR = str(engine/"tmp/rt_mapgen")
    jobs = []
    for mid in MAPS:
        if mid=="M991":
            record=live_maps[mid]
            assert record["size"]==[34,64,32] and record["event"]["#2#"]["storeid"]=="R170"
            assert record["event"]["#1#"]["dest"]=={"mapid":"M457","evid":79}
            for key in SHOP_DECOR:
                if key in record["event"]:
                    assert all(page["trigger"]==0 and not page["cmdblock"]
                               for page in record["event"][key]["page"])
            row=shop_world(changed).write()
            row["out"]="tmp/rt_mapgen/M991_shinomen_candidate.bw"
            jobs.append(row)
            continue
        regular, old_events = original.make(mid)
        model, new_events = changed.make(mid)
        heights=list(zip(*original.np.nonzero(model.hgt!=regular.hgt)))
        if heights:
            assert mid=="M457" and all(34<=z<model.d and 78<=x<=84 for z,x in heights)
        cells=list(zip(*original.np.nonzero(model.blk!=regular.blk)))
        if cells:
            assert mid=="M457" and all(29<=z<model.d and 72<=x<=84 for z,x in cells)
        if old_events is not None:
            old, new = old_events.ev, new_events.ev
            assert old.keys()==new.keys()
            for key, value in new.items():
                if value==old[key]:
                    continue
                a, b = old[key], value
                assert mid=="M457" and key=="#6#" and b["pos"][2]==a["pos"][2]+6
                assert dict(a,pos=b["pos"])==b
                row = live_maps[mid]["event"][key]
                assert row["pos"] in (a["pos"],b["pos"])
                assert "M458" in json.dumps(row["page"])
                updates[mid]=(key,b["pos"])
        row=model.write()
        row["out"]=f"tmp/rt_mapgen/{mid}_shinomen_candidate.bw"
        jobs.append(row)

    receipt=HERE/"shinomen-gate-worlds.json"
    spec_digest=sha256(json.dumps(jobs,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if publish:
        report=json.loads(receipt.read_bytes())
        assert report["spec"]==spec_digest
        built={mid:(engine/"project/data/mapdata"/f"{mid}.bw").read_bytes() for mid in MAPS}
        assert all(sha256(data).hexdigest()==report["worlds"][mid] for mid,data in built.items())
        existing=map_path.read_bytes()
        for mid,(key,pos) in updates.items():
            live_maps[mid]["event"][key]["pos"]=pos
        for key in SHOP_DECOR:
            live_maps["M991"]["event"].pop(key,None)
        eol=b"\r\n" if b"\r\n" in existing else b"\n"
        after=json.dumps(live_maps,ensure_ascii=False,indent="\t").encode().replace(b"\n",eol)
        assert source.read_bytes()==source_before and map_path.read_bytes()==existing
        targets=[(source,source_after),(map_path,after)]
        targets.extend((live/"mapdata"/f"{mid}.bw",data) for mid,data in built.items())
        backups={path:path.read_bytes() for path,_ in targets}
        written=[]
        try:
            for path,data in targets:
                written.append(path)
                overwrite(path,data)
        except BaseException:
            for path in reversed(written):
                overwrite(path,backups[path])
            raise
        print("Published",report)
        return

    job=engine/"tmp/rt_mapgen/job.json"
    log=HERE/"shinomen-gate-compile.log"
    with job.open("x",encoding="utf8") as file:
        json.dump({"maps":jobs},file)
    try:
        with log.open("w",encoding="utf8") as out:
            proc=subprocess.Popen([str(engine/"rpgcobo.exe"),"-testplay","-map","M457","[25,1.5,11,0]"],
                                  cwd=engine,stdout=out,stderr=subprocess.STDOUT)
            try:
                deadline=time.monotonic()+45
                while proc.poll() is None and time.monotonic()<deadline:
                    if "RTMAPGEN done" in log.read_text(errors="replace"):
                        break
                    time.sleep(.2)
            finally:
                if proc.poll() is None:
                    proc.kill()
                proc.wait(timeout=10)
    finally:
        job.unlink(missing_ok=True)
    evidence=log.read_text(errors="replace")
    assert "RTMAPGEN done" in evidence and "RTMAPGEN error" not in evidence,evidence[-2800:]
    hashes={}
    for row in jobs:
        mid=row["id"]
        assert f"RTMAPGEN built {mid}" in evidence
        data=(engine/row["out"]).read_bytes()
        (engine/"project/data/mapdata"/f"{mid}.bw").write_bytes(data)
        hashes[mid]=sha256(data).hexdigest()
    profile_map=engine/"project/data/map.json"
    profile_records=json.loads(profile_map.read_bytes())
    for mid,(key,pos) in updates.items():
        profile_records[mid]["event"][key]["pos"]=pos
    for key in SHOP_DECOR:
        profile_records["M991"]["event"].pop(key,None)
    profile_map.write_text(json.dumps(profile_records,ensure_ascii=False,indent="\t"),encoding="utf8")
    report={"worlds":hashes,"spec":spec_digest,"gate_positions":updates}
    receipt.write_text(json.dumps(report,indent=2),encoding="utf8")
    print(report)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),"--publish" in sys.argv[3:])
