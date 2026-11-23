"""Compile the keep's open altar in an isolated engine profile."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType


HERE = Path(__file__).resolve().parent


def main(repo, profile, publish):
    source = repo/"tools/gen_maps.py"
    source_before = source.read_bytes()
    sys.path.insert(0, str(source.parent))
    import gen_maps as gm

    text = source_before.decode("utf8")
    old = '    shrine(m, 44, 18)\n    ev = Events(m)\n    ev.talk(1, 16, "CE000", [(None, [go("M461", 104, 16)])], trigger=5)'
    new = old.replace("    shrine(m, 44, 18)", (
        "    # The fitted timber altar replaces the former freestanding shrine.\n"
        "    m.walls.extend((x, z) for x in range(44, 50) for z in range(20, 22))"
    ))
    if "\r\n" in text:
        old, new = (piece.replace("\n","\r\n") for piece in (old,new))
    assert text.count(old) + text.count(new) == 1
    changed = text.replace(old,new,1)
    module = ModuleType("hiruma_keep_candidate")
    module.__dict__.update({k:v for k,v in vars(gm).items() if k!="__name__"})
    sys.modules[module.__name__] = module
    exec(compile(changed,str(source),"exec"),module.__dict__)
    regular, old_events = gm.make("M462")
    model, events = module.make("M462")
    assert (regular.w, regular.d)==(model.w,model.d)
    assert events.ev==old_events.ev
    assert model.hgt.tobytes()==regular.hgt.tobytes()
    assert model.blk.tobytes()==regular.blk.tobytes()
    name = "project/data/mapdata/M462.bw"
    receipt = HERE/"hiruma-keep-world-build.json"
    if publish:
        measures = json.loads(receipt.read_bytes())
        candidate = (profile/name).read_bytes()
        assert measures["sha256"]==sha256(candidate).hexdigest()
        assert measures["legacy_objects_removed"]==len(regular.objs)-len(model.objs)
        assert measures["events_unchanged"]==len(events.ev)
    else:
        module.JOBDIR = str(profile/"tmp/rt_mapgen")
        row = model.write()
        row["out"] = "tmp/rt_mapgen/M462_fit_altar.bw"
        candidate = compile_world(profile, row)
        (profile/name).write_bytes(candidate)
        measures = {"map":"M462", "legacy_objects_removed":len(regular.objs)-len(model.objs),
                    "events_unchanged":len(events.ev),"sha256":sha256(candidate).hexdigest()}
    if publish:
        assert source.read_bytes()==source_before
        target = repo/"_tools/rpgcobo-tool"/name
        backup = target.read_bytes()
        (HERE/"M462-before-fitted-altar.bw").write_bytes(backup)
        try:
            write(source,changed.encode("utf8"))
            write(target,candidate)
        except BaseException:
            write(source,source_before)
            write(target,backup)
            raise
    receipt.write_text(json.dumps(measures,indent=2),encoding="utf8")
    print(measures)


def compile_world(profile, row):
    job = profile/"tmp/rt_mapgen/job.json"
    with job.open("x",encoding="utf8") as handle:
        json.dump({"maps":[row]},handle)
    log = HERE/"hiruma-keep-compile.log"
    try:
        with log.open("w",encoding="utf8") as out:
            proc = subprocess.Popen([str(profile/"rpgcobo.exe"),"-testplay","-map","M462","[34,2,10,0]"],
                                    cwd=profile,stdout=out,stderr=subprocess.STDOUT)
            try:
                deadline=time.monotonic()+40
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
    messages = log.read_text(errors="replace")
    assert "RTMAPGEN done" in messages and "RTMAPGEN error" not in messages, messages[-3000:]
    return (profile/row["out"]).read_bytes()


def write(target, data):
    with target.open("r+b") as handle:
        handle.write(data)
        handle.truncate()


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),"--publish" in sys.argv[3:])
