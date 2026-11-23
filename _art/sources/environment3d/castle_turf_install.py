"""Replace repeated bright grass with the castle-specific miniature turf."""
import argparse
import json
from pathlib import Path

from build_clan_castles import STAGE
from publish_castle_gates import INDEX, replace_file_contents

def main(repo,profile,publish):
    live=repo/"_tools/rpgcobo-tool"
    baseline=(live/INDEX).parent
    target=((live if publish else profile)/INDEX).parent
    staged=(profile/INDEX).parent
    old=b'texture0 = "tex/cakon_river_grass.png"'
    new=b'texture0 = "tex/castle_turf.png"'
    rows=json.loads((live/INDEX).read_bytes())
    changes={}
    for row in rows.values():
        model=row.get("terrain","")
        if "_castle" not in model:
            continue
        name=model+".pm"
        data=(baseline/name).read_bytes()
        if old not in data:
            continue
        changed=data.replace(old,new)
        if publish and (staged/name).is_file():
            assert (staged/name).read_bytes()==changed, name
        changes[target/name]=changed
    texture=Path("tex/castle_turf.png")
    content=(STAGE/texture).read_bytes()
    if publish:
        assert (staged/texture).read_bytes()==content
    if (target/texture).exists():
        assert (target/texture).read_bytes()==content
    else:
        (target/texture).write_bytes(content)
    for path,data in changes.items():
        if path.is_file():
            replace_file_contents(path,data)
        else:
            path.write_bytes(data)
    print(f"{'Installed' if publish else 'Staged'} matte turf on {len(changes)} castle districts.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    p.add_argument("profile",type=Path)
    p.add_argument("--publish",action="store_true")
    args=p.parse_args()
    main(args.repo.resolve(),args.profile.resolve(),args.publish)
