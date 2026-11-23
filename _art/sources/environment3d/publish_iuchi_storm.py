"""Publish the reviewed Iuchi siege or storm room group from its test profile."""

from hashlib import sha256
import json
from pathlib import Path
import sys

from install_environment_rows import install, STAGE
from iuchi_storm_worlds import LOWER, LOWER_POSITIONS, UPPER, stage
from shadowlands_march_worlds import overwrite


HERE = Path(__file__).resolve().parent
PLUGIN = Path("project/plugin/rokugan/RokuganEnvironmentKit.sk")
INDEX = Path("project/resource/native_environment/index.json")


def publish(repo, profile, upper):
    engine=repo/"_tools/rpgcobo-tool"
    ids=UPPER if upper else LOWER
    receipt="iuchi-storm-room" if upper else "iuchi-wind-siege"
    catalog=engine/"project/data/map.json"
    worlds={mid:engine/f"project/data/mapdata/{mid}.bw" for mid in ids}
    snapshots={file:file.read_bytes() for file in
               (catalog,engine/INDEX,engine/PLUGIN,repo/"tools/gen_maps.py",*worlds.values())}
    runtime=(profile/PLUGIN).read_bytes()
    assert runtime==(HERE/"RokuganEnvironmentKit.sk").read_bytes()
    if upper:
        assert runtime==snapshots[engine/PLUGIN]
    published=json.loads(snapshots[engine/INDEX])
    checked=json.loads((profile/INDEX).read_bytes())
    staged=json.loads((STAGE/"index.json").read_bytes())
    expected=json.loads(snapshots[catalog])
    if not upper:
        for mid,targets in LOWER_POSITIONS.items():
            for event,position in targets.items():
                expected[mid]["event"][event]["pos"]=position
    assert all(mid not in published and checked[mid]==staged[mid] for mid in ids)
    try:
        stage(repo,profile,True,upper)
        install(engine,ids,preserve_existing=True)
        if not upper:
            overwrite(engine/PLUGIN,runtime)
        assert (engine/PLUGIN).read_bytes()==runtime
        assert json.loads(catalog.read_bytes())==expected
        assert json.loads((engine/INDEX).read_bytes())=={**published,**{mid:checked[mid] for mid in ids}}
        proof=json.loads((HERE/f"{receipt}-worlds.json").read_bytes())
        for mid,file in worlds.items():
            assert sha256(file.read_bytes()).hexdigest()==proof[mid]["sha256"]
    except BaseException:
        for file,original in snapshots.items():
            if file.read_bytes()!=original:
                overwrite(file,original)
        raise


if __name__=="__main__":
    publish(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),"--upper" in sys.argv[3:])
