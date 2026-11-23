"""Publish the verified Beiden road, hideout and arenas."""
from hashlib import sha256
import json
from pathlib import Path
import sys

from install_environment_rows import STAGE, install
from publish_castle_gates import resource_files
from beiden_bandit_worlds import ARENAS, HERE, MAPS, HIDEOUT as SHRINE, revise_catalog, variant


from shadowlands_march_worlds import overwrite

ROOT=Path("project/resource/native_environment")
CATALOG=Path("project/data/map.json")


def publish(repo, profile):
    engine=repo/"_tools/rpgcobo-tool"
    source,_,_,old_source,new_source=variant(repo)
    runtime=engine/CATALOG
    raw=runtime.read_bytes()
    original=json.loads(raw)
    candidate=revise_catalog(raw)
    checked=json.loads((profile/CATALOG).read_bytes())
    assert all(checked[mid]==candidate[mid] for mid in MAPS)
    for mid,target in ARENAS.items():
        prior=original[mid]["encount"]
        verified=candidate[mid]["encount"]
        assert len(prior)==len(verified)
        assert all(e=={**p,"mapid":target} for p,e in zip(prior,verified)),mid
    assert all(candidate[mid]==original[mid] for mid in original if mid not in MAPS)
    assert set(candidate)-set(original)=={SHRINE}
    assert candidate[SHRINE]["name"]=="Battle: the Beiden hideout"
    proof=json.loads((HERE/"beiden-bandit-worlds.json").read_bytes())
    paths={}
    for mid in MAPS:
        rel=Path(f"project/data/mapdata/{mid}.bw")
        current=(profile/rel).read_bytes()
        assert sha256(current).hexdigest()==proof[mid]["sha256"],mid
        paths[engine/rel]=current
    preview=json.loads((profile/ROOT/"index.json").read_bytes())
    stage=json.loads((STAGE/"index.json").read_bytes())
    dest=engine/ROOT/"index.json"
    old_index=dest.read_bytes()
    applied=json.loads(old_index)
    selected={mid:stage[mid] for mid in MAPS}
    assert not set(applied).intersection(MAPS)
    assert all(preview[mid]==selected[mid] for mid in MAPS)
    for name,contents in resource_files(STAGE,selected).items():
        assert (profile/ROOT/name).read_bytes()==contents,name
    assert source.read_bytes()==old_source and runtime.read_bytes()==raw
    newline=b"\r\n" if b"\r\n" in raw else b"\n"
    paths[runtime]=json.dumps(candidate,ensure_ascii=False,indent="\t").encode().replace(b"\n",newline)+newline
    paths[source]=new_source
    old={p:p.read_bytes() if p.is_file() else None for p in (*paths,dest)}
    done=[]
    try:
        for p,data in paths.items():
            assert (p.read_bytes() if p.is_file() else None)==old[p],p
            if old[p] is None:
                with p.open("xb") as created:
                    done.append(p)
                    created.write(data)
            else:
                done.append(p)
                overwrite(p,data)
        done.append(dest)
        install(engine,MAPS,preserve_existing=True)
        assert json.loads(runtime.read_bytes())==candidate
        assert json.loads(dest.read_bytes())=={**applied,**selected}
    except BaseException:
        for p in reversed(done):
            if old[p] is None:
                p.unlink(missing_ok=True)
            elif p.read_bytes()!=old[p]:
                overwrite(p,old[p])
        raise


if __name__=="__main__":
    publish(*(Path(arg).resolve() for arg in sys.argv[1:3]))

