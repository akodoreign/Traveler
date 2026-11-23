"""Replace the one maple reference after checking its cleaned native mesh."""

import json
from pathlib import Path
import sys

from diorama_trees import MAPLE
from install_environment_rows import install, STAGE


def replace(repo, profile):
    mid="M413"
    engine=repo/"_tools/rpgcobo-tool"
    resource=Path("project/resource/native_environment")
    before=json.loads((engine/resource/"index.json").read_bytes())
    staged=json.loads((STAGE/"index.json").read_bytes())[mid]
    checked=json.loads((profile/resource/"index.json").read_bytes())[mid]
    assert checked==staged
    expected=before[mid]
    placements=expected["placements"]
    assert sum(p[0]=="iuchi_caravan_maple" for p in placements)==7
    expected={**expected,"placements":[[MAPLE,*p[1:]] if p[0]=="iuchi_caravan_maple" else p
                                        for p in placements]}
    assert expected==staged
    for file in (MAPLE+".mdl",MAPLE+".pm","tex/"+MAPLE+".png"):
        assert (profile/resource/file).read_bytes()==(STAGE/file).read_bytes()
    install(engine,[mid],preserve_existing=True,replace_existing=True)
    assert json.loads((engine/resource/"index.json").read_bytes())=={**before,mid:expected}


if __name__=="__main__":
    replace(*(Path(s).resolve() for s in sys.argv[1:3]))
