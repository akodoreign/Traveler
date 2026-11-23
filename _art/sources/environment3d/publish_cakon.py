"""Publish a tested caravan or Cakon map group from an isolated profile."""

from hashlib import sha256
import json
from pathlib import Path
import sys

from cakon_worlds import GROUPS, stage
from install_environment_rows import install, STAGE
from shadowlands_march_worlds import overwrite


HERE=Path(__file__).resolve().parent
PLUGIN=Path("project/plugin/rokugan/RokuganEnvironmentKit.sk")
INDEX=Path("project/resource/native_environment/index.json")


def publish(repo,profile,group):
    engine=repo/"_tools/rpgcobo-tool"
    maps=GROUPS[group]
    catalog=engine/"project/data/map.json"
    worlds={mid:engine/f"project/data/mapdata/{mid}.bw" for mid in maps}
    paths=(catalog,engine/INDEX,engine/PLUGIN,repo/"tools/gen_maps.py",*worlds.values())
    before={path:path.read_bytes() for path in paths}
    runtime=(profile/PLUGIN).read_bytes()
    assert runtime==(HERE/"RokuganEnvironmentKit.sk").read_bytes()
    live=json.loads(before[engine/INDEX])
    checked=json.loads((profile/INDEX).read_bytes())
    prepared=json.loads((STAGE/"index.json").read_bytes())
    assert all(mid not in live and checked[mid]==prepared[mid] for mid in maps)
    try:
        stage(repo,profile,group,True)
        install(engine,maps,preserve_existing=True)
        if runtime!=before[engine/PLUGIN]:
            overwrite(engine/PLUGIN,runtime)
        assert catalog.read_bytes()==before[catalog]
        assert (engine/PLUGIN).read_bytes()==runtime
        assert json.loads((engine/INDEX).read_bytes())=={**live,**{mid:checked[mid] for mid in maps}}
        proof=json.loads((HERE/f"cakon-{group}-worlds.json").read_bytes())
        for mid,world in worlds.items():
            assert sha256(world.read_bytes()).hexdigest()==proof[mid]["sha256"]
    except BaseException:
        for path,data in before.items():
            if path.read_bytes()!=data:
                overwrite(path,data)
        raise


if __name__=="__main__":
    publish(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),sys.argv[3])
