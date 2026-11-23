"""Promote the tested winter lighting and material pass over its existing rows."""
import json
from pathlib import Path
import sys

from install_environment_rows import STAGE, install
from publish_castle_gates import resource_files
from winter_river_worlds import MAPS

ROOT=Path("project/resource/native_environment")
PRIVATE=("winter_","floating_flowers_river_post",*(mid.lower()+"_" for mid in MAPS))

def publish(repo, profile):
    engine=repo/"_tools/rpgcobo-tool"
    live=engine/ROOT
    preview=profile/ROOT
    stage=json.loads((STAGE/"index.json").read_bytes())
    old=json.loads((live/"index.json").read_bytes())
    reviewed=json.loads((preview/"index.json").read_bytes())
    rows={mid:stage[mid] for mid in MAPS}
    assert all(reviewed[mid]==row and mid in old for mid,row in rows.items())
    candidate=resource_files(STAGE,rows)
    for part,data in candidate.items():
        assert (preview/part).read_bytes()==data,part
        previous=live/part
        if not previous.is_file() or previous.read_bytes()!=data:
            assert Path(part).name.startswith(PRIVATE),part
    install(engine, MAPS)
    assert json.loads((live/"index.json").read_bytes())=={**old,**rows}

if __name__=="__main__":
    publish(*(Path(arg).resolve() for arg in sys.argv[1:3]))
