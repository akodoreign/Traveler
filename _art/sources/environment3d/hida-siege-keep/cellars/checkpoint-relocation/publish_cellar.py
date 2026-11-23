"""Publish the exact reviewed M153 art and its doorway and checkpoint layout."""
from pathlib import Path
import json
import sys

import relocate_cellar_checkpoint as checkpoint
from publish_castle_gates import CATALOG, publish, require
from publish_verified_visual_maps import plan


def install(repo, profile):
    engine=repo/"_tools/rpgcobo-tool"
    prior=(engine/CATALOG).read_bytes()
    state=json.loads(prior)[checkpoint.MID]["event"][checkpoint.EVENT]["pos"]
    repaired=prior if state==checkpoint.NEW else checkpoint.bytes_for_catalog(prior)[0]
    rows,before,updated,additions=plan(
        repo,profile,checkpoint.HERE/"receipt.json",revised_catalog=repaired)
    require(set(rows)=={checkpoint.MID},"Unexpected cellar release scope")
    source=repo/"tools/gen_maps.py"
    raw=source.read_bytes()
    end=b"\r\n" if b"\r\n" in raw else b"\n"
    anchor=checkpoint.WIDEN.encode().replace(b"\n",end)
    inserted=checkpoint.SOURCE_CHANGE.encode().replace(b"\n",end)
    require(raw.count(anchor)==1,"Cannot find the verified cellar generator anchor")
    after=raw if inserted in raw else raw.replace(anchor,anchor+inserted,1)
    compile(after,str(source),"exec")
    before[source]=raw
    updated[source]=after
    publish(before,updated,additions)
    print("Published M153 with the native-reviewed stairs and reachable save shrine.")


if __name__=="__main__":
    install(*(Path(arg).resolve() for arg in sys.argv[1:3]))
