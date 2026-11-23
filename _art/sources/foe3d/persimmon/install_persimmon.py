"""Install Persimmon's rig and move the Buried Leaves field actor off the stoop."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent / "coast-kit"))
from publish_castle_gates import CATALOG, INDEX, publish, require, resource_files

FOES = Path("project/resource/native_foe")
KEY = "EP172"
VIEWS = {"M387":5,"M408":8,"M413":3}
BEFORE = [55,4,24,1]
AFTER = [61,4,23,1]


def patch_catalog(raw):
    data=json.loads(raw)
    target=data["M387"]["event"]["#5#"]
    require(target["mdlid"]==KEY and target["pos"] in (BEFORE,AFTER),"Unexpected Persimmon stable event")
    for m,num in VIEWS.items():
        require(data[m]["event"][f"#{num}#"]["mdlid"]==KEY,f"Persimmon event drift in {m}")
    if target["pos"]==AFTER:
        return raw
    start=re.search(rb'"M387"\s*:\s*\{',raw)
    end=re.search(rb'"M388"\s*:\s*\{',raw[start.end():])
    target_start=re.search(rb'"#5#"\s*:\s*\{',raw[start.start():start.end()+end.start()])
    idx=start.start()+target_start.end()
    pos=re.search(rb'"pos"\s*:\s*\[\s*(55)\s*,\s*4\s*,\s*(24)\s*,\s*1\s*\]',raw[idx:])
    require(pos and pos.start()<500,"Cannot locate exact Persimmon position")
    updated=raw[:idx+pos.start(2)]+b"23"+raw[idx+pos.end(2):]
    updated=updated[:idx+pos.start(1)]+b"61"+updated[idx+pos.end(1):]
    data["M387"]["event"]["#5#"]["pos"]=AFTER
    require(json.loads(updated)==data,"Pony placement changed another catalog value")
    return updated


def pose_spec(raw):
    data=json.loads(raw)
    motions={row["id"]: row for row in data["EP110"]["animap"]}
    quiet=deepcopy(motions["stand"])
    quiet["spd"]=4
    spec={"animap":[quiet,motions["walk"]],"scale":.018,"height":1.69,"radius":.49}
    if KEY in data:
        require(data[KEY]==spec,"Another native pony fit is installed")
        return raw
    end=raw.rfind(b"}")
    require(end>0,"Native registry is incomplete")
    patch=b',\n  "EP172": '+json.dumps(spec,separators=(",",":")).encode()+b"\n"
    revised=raw[:end].rstrip()+patch+raw[end:]
    require(json.loads(revised)=={**data,KEY:spec},"Pony registration changed another foe")
    return revised


def plan(engine):
    catalog=engine/CATALOG
    index=engine/FOES/"index.json"
    before={catalog:catalog.read_bytes(),index:index.read_bytes()}
    updated={catalog:patch_catalog(before[catalog]),index:pose_spec(before[index])}
    assets={}
    directory=HERE/"native_foe"
    for filename in ("EP172.pm","EP172.mdl","EP172.mot","tex/ep172_hunyuan_color_srgb.png","tex/hunyuan_flat_normal.png"):
        path=engine/FOES/filename
        blob=(directory/filename).read_bytes()
        if path.is_file():
            require(path.read_bytes()==blob,f"Changed shared foe file {filename}")
        else:
            assets[path]=blob
    return before,updated,assets


def sync_review(engine,profile):
    catalog=json.loads((engine/CATALOG).read_bytes())
    env=json.loads((engine/INDEX).read_bytes())
    target=json.loads((profile/INDEX).read_bytes())
    (profile/CATALOG).write_bytes((engine/CATALOG).read_bytes())
    for mid in VIEWS:
        rel=Path(f"project/data/mapdata/{mid}.bw")
        (profile/rel).write_bytes((engine/rel).read_bytes())
        if catalog[mid]["bg"]["type"]=="tex":
            bg=Path("project")/catalog[mid]["bg"]["tex"].lstrip("/")
            (profile/bg).write_bytes((engine/bg).read_bytes())
        if mid in env:
            target[mid]=env[mid]
    for name,data in resource_files((engine/INDEX).parent,{m:env[m] for m in VIEWS if m in env}).items():
        ((profile/INDEX).parent/name).write_bytes(data)
    (profile/INDEX).write_text(json.dumps(target,ensure_ascii=False,separators=(",",":")),encoding="utf8")


def deploy(repo,profile,action):
    engine=repo/"_tools/rpgcobo-tool"
    require(engine.resolve()!=profile,"Use an isolated native profile")
    if action=="baseline":
        sync_review(engine,profile)
        return
    target=profile if action=="stage" else engine
    before,updated,new=plan(target)
    if action=="publish":
        for path,blob in {**updated,**new}.items():
            reviewed=(profile/path.relative_to(engine)).read_bytes()
            if path==engine/CATALOG:
                live_row=json.loads(blob)["M387"]["event"]["#5#"]
                require(live_row==json.loads(reviewed)["M387"]["event"]["#5#"],"The reviewed pony location changed")
            elif path==engine/FOES/"index.json":
                require(json.loads(blob)[KEY]==json.loads(reviewed)[KEY],"The reviewed pony rig changed")
            else:
                require(blob==reviewed,f"The reviewed {path.name} changed")
        source=repo/"tools/gen_maps.py"
        before[source]=source.read_bytes()
        old=b'ev.prop(29, 20, "EP172", msg="Persimmon glares at you.'
        new_spawn=b'ev.prop(35, 19, "EP172", msg="Persimmon glares at you.'
        require(before[source].count(old)+before[source].count(new_spawn)==1,"M387 source pony anchor changed")
        updated[source]=before[source].replace(old,new_spawn,1)
        compile(updated[source],str(source),"exec")
    publish(before,updated,new)
    print("Installed the textured 10-joint Persimmon fit across the existing pony events.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("baseline","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("profile",type=Path)
    args=parser.parse_args()
    deploy(args.repo.resolve(),args.profile.resolve(),args.action)
