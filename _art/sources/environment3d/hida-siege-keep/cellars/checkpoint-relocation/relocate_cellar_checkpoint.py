"""Stage the single-event M153 save checkpoint repair and its visual niche."""

import argparse
from copy import deepcopy
from difflib import unified_diff
import json
from pathlib import Path
import re
import sys
from types import ModuleType

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import build_hida_cellar as cellar
from build_hoshi_stall import box

h=cellar.h
base=cellar.base
STAGE=HERE/"native_environment"
OLD=[66,10,23,2]
NEW=[68,3,24,2]
NEAR=(69,24)
EVENT="#12#"
MID="M153"
DRESS=cellar.placements
WIDEN='            print("   %s: widened %d cells (a full block to every object)" % (i, n))\n'
SOURCE_CHANGE=(
    '    if i == "M153":\n'
    '        # The original save shrine was left on the roof after the cellar widened.\n'
    '        # Keep its interaction and move it to the existing floor alcove.\n'
    '        sx, sz = 68, 24\n'
    '        assert m.hgt[sz, sx] == 2\n'
    '        ev.ev["#12#"]["pos"][:3] = [sx, int(m.hgt[sz, sx]) + 1, sz]\n'
)


def bytes_for_catalog(raw):
    before=json.loads(raw)
    assert before[MID]["event"][EVENT]["pos"]==OLD
    mid=re.search(rb'"M153"\s*:\s*\{',raw)
    assert mid
    same_map_end=re.search(rb'"M154"\s*:\s*\{',raw[mid.end():])
    assert same_map_end
    end=mid.end()+same_map_end.start()
    section=raw[mid.start():end]
    event=re.search(rb'"#12#"\s*:\s*\{',section)
    assert event
    pattern=rb'"pos"\s*:\s*\[\s*(66)\s*,\s*(10)\s*,\s*(23)\s*,\s*(2)\s*\]'
    pos=re.search(pattern,section[event.end():])
    assert pos
    a=mid.start()+event.end()
    out=raw
    # Change only the three numeric fields and keep byte formatting everywhere.
    for i in (3,2,1):
        start,stop=pos.span(i)
        out=out[:a+start]+str(NEW[i-1]).encode()+out[a+stop:]
    after=json.loads(out)
    assert after[MID]["event"][EVENT]["pos"]==NEW
    nominal=deepcopy(before)
    nominal[MID]["event"][EVENT]["pos"]=NEW
    assert after==nominal
    return out,before,after


def relocate_shrine(geo,w):
    x,y,z,_=NEW
    assert w.hgt[z,x]==2
    y=y*.5
    # Keep half the alcove free for the player to face and examine it.
    ux,uz=x*.5-.19,z*.5-.12
    box(geo,(ux-.24,uz-.18,y+.025),(.49,.37,.094),h.BRICK,1.26)
    box(geo,(ux-.21,uz-.16,y+.117),(.43,.33,.055),h.SLATE,1.27)
    box(geo,(ux-.28,uz-.19,y+.024),(.057,.38,.060),cellar.AMBER,1.29)
    return (ux,uz,y+.17),y


def dress(w,route,niche):
    props,lights=DRESS(w,route,niche)
    props=props[:-2]
    lights=lights[:-1]
    x,z,y=niche
    props.extend([[h.SHRINE,x,y,z,.49,-.20],
                  [h.ANDON,x-.47,y-.142,z-.08,.54,.09]])
    lights.append([x-.38,y+.58,z,3.6,5.50,0xffad4aff])
    return props,lights


def setup():
    cellar.HERE=HERE
    cellar.STAGE=STAGE
    cellar.TEX=STAGE/"tex"
    cellar.LAND="m153_hida_siege_cellar_checkpoint"
    cellar.checkpoint=relocate_shrine
    cellar.placements=dress
    h.HERE=HERE
    h.STAGE=STAGE


def altered_generator(repo,orig):
    assert orig.count(WIDEN)==1
    new=orig.replace(WIDEN,WIDEN+SOURCE_CHANGE)
    source=repo/"tools/gen_maps.py"
    pathlib_patch="tools/gen_maps.py"
    patch="".join(unified_diff(orig.splitlines(keepends=True),new.splitlines(keepends=True),
                               "a/"+pathlib_patch,"b/"+pathlib_patch))
    (HERE/"gen-maps-checkpoint.patch").write_text(patch,encoding="utf8",newline="\n")
    code=new.replace('os.path.join(HERE, "_ladder_foes.json")',repr(str(HERE/"_ladder_foes.json")))
    sys.path.insert(0,str(source.parent))
    gm=ModuleType("gen_maps")
    gm.__file__=str(source)
    sys.modules["gen_maps"]=gm
    exec(compile(code,str(source),"exec"),vars(gm))
    return gm


def prove_source(repo,stock):
    original,historical=stock.make(MID)
    source=(repo/"tools/gen_maps.py").read_text(encoding="utf8")
    patched=altered_generator(repo,source)
    new,current=patched.make(MID)
    events=deepcopy(historical.ev)
    assert events[EVENT]["pos"]==OLD
    events[EVENT]["pos"]=NEW
    assert current.ev==events
    assert np.array_equal(original.hgt,new.hgt) and np.array_equal(original.blk,new.blk)
    assert original.objs==new.objs and original.walls==new.walls
    n=h.get_floor_route(new,((34,18),NEAR,(NEW[0],NEW[2])))
    assert n[-2:]==[NEAR,(NEW[0],NEW[2])]
    assert abs(NEW[0]-NEAR[0])*.5==.5 and NEW[2]==NEAR[1]
    return n


def build(repo):
    # The existing cellar build validates all original story anchors, materials
    # and collisions before the distinct checkpoint snapshot is exported.
    live=repo/"_tools/rpgcobo-tool"
    stock=base.game_definition(repo)
    proof=prove_source(repo,stock)
    setup()
    saved=cellar.HERE
    # Cellar material sources live in the prior Hida stone pass.
    old_materials=cellar.materials
    def materials(world,route):
        cellar.HERE=HERE.parent
        try:
            return old_materials(world,route)
        finally:
            cellar.HERE=saved
    cellar.materials=materials
    cellar.build(repo)
    original=(live/base.CATALOG).read_bytes()
    candidate,before,after=bytes_for_catalog(original)
    receipt=base.read_json(HERE/"receipt.json")
    row=receipt["maps"][MID]
    row["catalog_hash"]=base.digest(json.dumps(after[MID],sort_keys=True).encode())
    row["checkpoint_event"]=NEW[:3]
    row["checkpoint_approach"]=[list(c) for c in proof[-8:]]
    row["checkpoint_support_m"]=1.5
    (HERE/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf8")
    repair={"map":MID,"event":EVENT,"field":"pos","original":OLD,"candidate":NEW,
            "original_catalog_sha256":base.digest(original),"candidate_catalog_sha256":base.digest(candidate),
            "original_m153_row_sha256":base.digest(json.dumps(before[MID],sort_keys=True).encode()),
            "candidate_m153_row_sha256":row["catalog_hash"],
            "unchanged_original_event":{k:v for k,v in before[MID]["event"][EVENT].items() if k!="pos"},
            "proof":{"approach":list(NEAR),"interaction_distance_m":.5,"floor_grade_m":1.5,
                     "positions_to_approach":len(proof),"generated_world_unchanged":True}}
    (HERE/"catalog-delta.json").write_text(json.dumps(repair,indent=2),encoding="utf8")


def stage(repo,profile):
    live=repo/"_tools/rpgcobo-tool"
    if profile.resolve()==live.resolve():
        raise ValueError("Stage into an isolated playtest copy.")
    receipt=base.read_json(HERE/"receipt.json")
    row=receipt["maps"][MID]
    assert base.digest((profile/"project/data/mapdata/M153.bw").read_bytes())==row["world_hash"]
    for name,sha in receipt["files"].items():
        assert base.digest((STAGE/name).read_bytes())==sha
    file=profile/base.CATALOG
    original=file.read_bytes()
    current=json.loads(original)
    already=current[MID]["event"][EVENT]["pos"]==NEW
    candidate=original if already else bytes_for_catalog(original)[0]
    fixed=json.loads(candidate)
    assert base.digest(json.dumps(fixed[MID],sort_keys=True).encode())==row["catalog_hash"]
    if not already:
        assert file.read_bytes()==original
        temp=file.with_name("map-cellar-checkpoint-stage.json")
        temp.write_bytes(candidate)
        temp.replace(file)
    setup()
    try:
        h.stage(repo,profile)
    except (OSError,ValueError,AssertionError,RuntimeError):
        if not already and file.read_bytes()==candidate:
            temp.write_bytes(original)
            temp.replace(file)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("build","stage"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    args=parser.parse_args()
    if args.action=="build":
        build(args.repo.resolve())
    elif args.profile is None:
        parser.error("--profile is required for stage")
    else:
        stage(args.repo.resolve(),args.profile.resolve())
