"""Install only the reviewed Yasuki worlds, art, and portal positions."""
from hashlib import sha256
import json
from pathlib import Path
import sys

from install_environment_rows import STAGE, install
from publish_castle_gates import resource_files
from shadowlands_march_worlds import overwrite
from yasuki_coast_worlds import HERE, MAPS, events_for, variant

RESOURCE=Path("project/resource/native_environment")
CATALOG=Path("project/data/map.json")
CAVES=("M480","M481")


def publish(repo, profile):
    engine=repo/"_tools/rpgcobo-tool"
    source,_,_,baseline_source,updated_source=variant(repo)
    live_catalog=engine/CATALOG
    baseline_catalog=live_catalog.read_bytes()
    previous=json.loads(baseline_catalog)
    new=events_for(live_catalog)
    checked=json.loads((profile/CATALOG).read_bytes())
    for mid in MAPS:
        assert checked[mid]==new[mid],mid
    for mid in CAVES:
        assert len(previous[mid]["encount"])==len(new[mid]["encount"])
        for back,front in zip(previous[mid]["encount"],new[mid]["encount"]):
            assert front=={**back,"mapid":"M829"},mid
    proof=json.loads((HERE/"yasuki-coast-worlds.json").read_bytes())
    replacements={}
    for mid in MAPS:
        rel=Path(f"project/data/mapdata/{mid}.bw")
        data=(profile/rel).read_bytes()
        assert sha256(data).hexdigest()==proof[mid]["sha256"],mid
        replacements[engine/rel]=data
    reviewed=json.loads((profile/RESOURCE/"index.json").read_bytes())
    prepared=json.loads((STAGE/"index.json").read_bytes())
    installed_index=engine/RESOURCE/"index.json"
    before_index=installed_index.read_bytes()
    installed=json.loads(before_index)
    rows={mid:prepared[mid] for mid in MAPS}
    assert set(MAPS).isdisjoint(installed)
    assert all(reviewed[mid]==row for mid,row in rows.items())
    for name,content in resource_files(STAGE,rows).items():
        compare=profile/RESOURCE/name
        assert compare.read_bytes()==content, name
    assert source.read_bytes()==baseline_source and live_catalog.read_bytes()==baseline_catalog
    newline=b"\r\n" if b"\r\n" in baseline_catalog else b"\n"
    replacements[live_catalog]=json.dumps(new,ensure_ascii=False,indent="\t").encode().replace(b"\n",newline)+newline
    replacements[source]=updated_source
    backups={path:path.read_bytes() for path in (*replacements,installed_index)}
    attempted=[]
    try:
        for path,data in replacements.items():
            assert path.read_bytes()==backups[path],path
            attempted.append(path)
            overwrite(path,data)
        attempted.append(installed_index)
        install(engine,MAPS,preserve_existing=True)
        assert json.loads(live_catalog.read_bytes())==new
        assert json.loads(installed_index.read_bytes())=={**installed,**rows}
    except BaseException:
        for path in reversed(attempted):
            if path.read_bytes()!=backups[path]:
                overwrite(path,backups[path])
        raise
    print("Installed the Yasuki road, two sea caves, and shared cave arena.")


if __name__=="__main__":
    publish(*(Path(v).resolve() for v in sys.argv[1:3]))
