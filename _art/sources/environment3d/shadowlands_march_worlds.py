"""Build and audit the seven Shadowlands march worlds in a playtest profile."""

from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType


HERE=Path(__file__).resolve().parent
MAPS=tuple(f"M{i}" for i in range(171,178))


def variant(repo):
    source=repo/"tools/gen_maps.py"
    sys.path.insert(0,str(source.parent))
    import gen_maps as original

    raw=source.read_bytes()
    eol="\r\n" if b"\r\n" in raw else "\n"
    text=raw.decode().replace("\r\n","\n")
    if "def rebuild_shadowlands_march(" not in text:
        next_func="def shifting_waste_paths("
        insertion="    if i in MAZE:\n        rebuild_shifting_waste(m, MAZE.index(i)+1)\n"
        assert text.count(next_func)==1 and text.count(insertion)==1
        fragment=(HERE/"shadowlands_march_map_section.py").read_text(encoding="utf8")
        fragment=fragment[fragment.index("SHADOWLANDS_MARCH_ROUTES ="):].strip()
        text=text.replace(next_func,fragment+"\n\n\n"+next_func,1)
        text=text.replace(insertion,insertion+
                          "    if i in SHADOWLANDS_MARCH_ROUTES:\n        rebuild_shadowlands_march(m, ev)\n",1)

    module=ModuleType("shadowlands_march_candidate")
    module.__dict__.update({key:value for key,value in vars(original).items() if key!="__name__"})
    sys.modules[module.__name__]=module
    exec(compile(text,str(source),"exec"),module.__dict__)
    return original,module,raw,text.replace("\n",eol).encode()


def walkable(gm, world):
    column=world.hgt.copy()
    for obj in world.objs:
        if obj["t"] not in ("fill","blk") or obj["blk"]==gm.VOID:
            continue
        x,z=obj["x"],obj["z"]
        height=obj["y"]+obj.get("h",1)-1
        piece=column[z:z+obj.get("d",1),x:x+obj.get("w",1)]
        gm.np.maximum(piece,height,out=piece)
    start=(gm.PAD_X+4,gm.PAD_BOTTOM+(20 if world.mid=="M175" else 16))
    queue=deque([start])
    seen={start}
    while queue:
        x,z=queue.popleft()
        for a,b in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
            if (a,b) in seen or not 0<=a<world.w or not 0<=b<world.d:
                continue
            cell=world.blk[b,a]
            if cell in (0,gm.VOID,gm.LAVA,gm.WATER):
                continue
            if cell==gm.TAR and column[b,a]==world.hgt[b,a]:
                continue
            if abs(int(column[b,a])-int(column[z,x]))<=1:
                seen.add((a,b))
                queue.append((a,b))
    return seen


def audit(gm, before, after, event):
    points=walkable(gm,before)
    revised=walkable(gm,after)
    objectives=[r["pos"] for r in event.ev.values() if r["role"] in ("portal","custom","itemchest") and "pos" in r]
    def reachable(cells,p):
        x,_,z,_=p
        return any((a,b) in cells for a in range(x-1,x+2) for b in range(z-1,z+2))
    lost=[p for p in objectives if reachable(points,p) and not reachable(revised,p)]
    assert not lost,(before.mid,lost)
    return {"floor_cells_before":len(points),"floor_cells_after":len(revised),
            "story_points_connected":sum(reachable(revised,p) for p in objectives),
            "legacy_objects_removed":len(before.objs)-len(after.objs),
            "height_cells_changed":int(gm.np.count_nonzero(before.hgt!=after.hgt))}


def compile_worlds(engine, jobs, stem="shadowlands-march", start=None):
    job=engine/"tmp/rt_mapgen/job.json"
    log=HERE/f"{stem}-worlds.log"
    with job.open("x",encoding="utf8") as file:
        json.dump({"maps":jobs},file)
    try:
        with log.open("w",encoding="utf8") as out:
            proc=subprocess.Popen([str(engine/"rpgcobo.exe"),"-testplay","-map",start or jobs[0]["id"],"[25,2,10,0]"],
                cwd=engine,stdout=out,stderr=subprocess.STDOUT)
            try:
                deadline=time.monotonic()+60
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
    for row in jobs:
        mid=row["id"]
        assert f"RTMAPGEN built {mid}" in evidence
        path=engine/"project/data/mapdata"/f"{mid}.bw"
        path.write_bytes((engine/row["out"]).read_bytes())


def main(repo,engine,mode):
    gm, candidate, old_code, new_code=variant(repo)
    candidate.JOBDIR=str(engine/"tmp/rt_mapgen")
    report={}
    jobs=[]
    for mid in MAPS:
        before, old_event=gm.make(mid)
        after, event=candidate.make(mid)
        assert (before.w,before.d)==(after.w,after.d) and old_event.ev==event.ev,mid
        report[mid]=audit(gm,before,after,event)
        row=after.write()
        row["out"]=f"tmp/rt_mapgen/{mid}_march_candidate.bw"
        jobs.append(row)
    if mode=="--check":
        print(report)
        return
    spec=sha256(json.dumps(jobs,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    receipt=HERE/"shadowlands-march-worlds.json"
    if mode=="--publish":
        expected=json.loads(receipt.read_bytes())
        assert expected["spec"]==spec
        replace={}
        for mid in MAPS:
            relative=Path("project/data/mapdata")/f"{mid}.bw"
            data=(engine/relative).read_bytes()
            assert expected["maps"][mid]["sha256"]==sha256(data).hexdigest()
            replace[repo/"_tools/rpgcobo-tool"/relative]=data
        source=repo/"tools/gen_maps.py"
        assert source.read_bytes()==old_code
        replace[source]=new_code
        originals={path:path.read_bytes() for path in replace}
        copied=[]
        try:
            for path,data in replace.items():
                copied.append(path)
                overwrite(path,data)
        except BaseException:
            for path in reversed(copied):
                overwrite(path,originals[path])
            raise
    else:
        compile_worlds(engine,jobs)
        for mid,row in report.items():
            file=engine/"project/data/mapdata"/f"{mid}.bw"
            row["sha256"]=sha256(file.read_bytes()).hexdigest()
        receipt.write_text(json.dumps({"spec":spec,"maps":report},indent=2),encoding="utf8")
    print(report)


def overwrite(path,data):
    with path.open("r+b") as file:
        length=file.seek(0,2)
        file.seek(0)
        file.write(data)
        if len(data)<length:
            if path.suffix==".json":
                file.write(b" "*(length-len(data)))
            else:
                file.truncate()


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),sys.argv[3] if len(sys.argv)>3 else None)
