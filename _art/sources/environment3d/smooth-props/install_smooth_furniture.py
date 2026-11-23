"""Fit continuous Comfy furniture meshes and stage exact prop-key substitutions."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import diorama_trees
import export_coast
from publish_castle_gates import CATALOG, INDEX, RUNTIME, resource_files, replace_file_contents

ART = HERE / "native"
PROOF = HERE / "fit-proof.json"
SWAPS = {
    "iuchi_storm_broken_frame": ("smooth_iuchi_storm_shoji", True),
    "hoshi_trade_chest": ("smooth_hoshi_trade_chest", True),
    "hoshi_storage_jar": ("smooth_hoshi_storage_jar", False),
    "salt_crate": ("smooth_coast_salt_crate", True),
    "shadowlands_broken_cart": ("smooth_shadowlands_cart", True),
}
WORLDS = Path("project/data/mapdata")


def write(path, content):
    if path.exists():
        if path.read_bytes() != content:
            replace_file_contents(path, content)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def digest(data):
    return sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def bounds(root, model):
    file = root / (model + ".pm")
    start = file.read_text("utf8").split("bnd = ", 1)[1].splitlines()[0]
    return np.asarray(json.JSONDecoder().raw_decode(start)[0])


_raw_mesh_source = diorama_trees.mesh_source


def furniture_source(key):
    source, mesh = _raw_mesh_source(key)
    if key == "smooth_hoshi_trade_chest":
        # Place the brass pulls on the same side as the old merchant chest.
        mesh.apply_transform(np.diag((-1., 1., -1., 1.)))
    if key == "smooth_hoshi_storage_jar":
        center = (mesh.triangles_center - mesh.bounds[0]) / mesh.extents
        radius = np.linalg.norm(center[:, (0, 2)] - .5, axis=1)
        rgb = mesh.visual.to_color().vertex_colors[mesh.faces, :3].mean(axis=1)
        pale = (rgb.min(axis=1)>133.) & (np.ptp(rgb, axis=1)<49.)
        backdrop = (center[:, 1]<.132) & (pale | (radius>.308))
        mesh.update_faces(~backdrop)
        mesh.remove_unreferenced_vertices()
    return source, mesh


def fit(engine, names):
    root = engine / INDEX.parent
    (ART / "tex").mkdir(parents=True, exist_ok=True)
    # The established native mesh exporter emits into this scoped bundle.
    export_coast.STAGE = diorama_trees.STAGE = ART
    diorama_trees.mesh_source = furniture_source
    rows = read_json(PROOF) if PROOF.exists() else {}
    for old in names:
        new, long_axis = SWAPS[old]
        bound = bounds(root, old)
        assert np.allclose(bound[:3],(0.,bound[4],0.),atol=.002), (old, bound)
        mesh = diorama_trees.build_diorama_mesh(new, new, tuple(bound[3:] * 2.),
                                               align_x=long_axis, main_component=old not in {"hoshi_storage_jar","shadowlands_broken_cart"})
        fitted = bounds(ART, new)
        assert np.allclose(fitted, bound, atol=.002), (old, bound, fitted)
        assets = resource_files(ART,{"preview":{"placements":[[new]]}})
        rows[old] = {"model":new,"bounds":fitted.tolist(),"fit":mesh,
                     "files":{key:digest(content) for key,content in assets.items()}}
        print(new,mesh["triangles"],"continuous textured triangles",flush=True)
    write(PROOF,json_bytes(rows))


def plan(engine, names):
    mapping = {old:SWAPS[old][0] for old in names}
    prepared=read_json(PROOF)
    resources=resource_files(ART,{"preview":{"placements":[[name] for name in mapping.values()]}})
    expected={key:value for old in names for key,value in prepared[old]["files"].items()}
    assert {key:digest(data) for key,data in resources.items()}==expected
    live=read_json(engine / INDEX)
    rows={}
    changes={}
    for mid,row in live.items():
        placements=row.get("placements",[])
        counts=Counter(p[0] for p in placements if p[0] in mapping)
        if not counts:
            continue
        updated=deepcopy(row)
        for p in updated["placements"]:
            p[0]=mapping.get(p[0],p[0])
        assert all(old[1:]==new[1:] for old,new in zip(placements,updated["placements"],strict=True))
        assert {k:v for k,v in row.items() if k!="placements"}=={
                k:v for k,v in updated.items() if k!="placements"}
        rows[mid]=updated
        changes[mid]=dict(counts)
    if not rows:
        raise ValueError("The selected original placements are no longer installed.")
    if "iuchi_storm_broken_frame" in names:
        assert changes.get("M412",{}).get("iuchi_storm_broken_frame")==4
        assert changes.get("M882",{}).get("iuchi_storm_broken_frame")==7
    if "shadowlands_broken_cart" in names:
        for mid in ("M174","M458"):
            assert changes.get(mid,{}).get("shadowlands_broken_cart")==1,(mid,"cart placement missing")
    return live,rows,resources,changes


def copy_test_dependencies(engine,profile,live,rows):
    group={mid:live[mid] for mid in rows}
    for path,content in resource_files(engine / INDEX.parent,group).items():
        write(profile / INDEX.parent / path,content)
    catalog=read_json(engine / CATALOG)
    staged_catalog=read_json(profile / CATALOG)
    staged_catalog.update({mid:catalog[mid] for mid in rows})
    write(profile / CATALOG,json_bytes(staged_catalog))
    for mid in rows:
        file=WORLDS/(mid+".bw")
        write(profile / file,(engine / file).read_bytes())
    write(profile / RUNTIME,(engine / RUNTIME).read_bytes())


def stage(engine,profile,names):
    live,rows,resources,changes=plan(engine,names)
    copy_test_dependencies(engine,profile,live,rows)
    for path,content in resources.items():
        write(profile / INDEX.parent / path,content)
    staged=read_json(profile/INDEX)
    staged.update(rows)
    write(profile/INDEX,json_bytes(staged))
    return changes


def publish(engine,profile,names):
    _,rows,resources,changes=plan(engine,names)
    peer=read_json(profile/INDEX)
    live_catalog=read_json(engine/CATALOG)
    staged_catalog=read_json(profile/CATALOG)
    for mid,row in rows.items():
        assert peer[mid]==row,(mid,"staged row differs")
        assert staged_catalog[mid]==live_catalog[mid],(mid,"staged event catalog differs")
        file=WORLDS/(mid+".bw")
        assert (profile/file).read_bytes()==(engine/file).read_bytes(),(mid,"world geometry differs")
    for rel,data in resources.items():
        assert (profile/INDEX.parent/rel).read_bytes()==data,(rel,"tested prop differs")
        dest=engine/INDEX.parent/rel
        if dest.exists():
            assert dest.read_bytes()==data,(rel,"asset already exists with different bytes")
    path=engine/INDEX
    baseline=path.read_bytes()
    current=json.loads(baseline)
    # Keep changes outside the audited map set, including concurrent publishes.
    for mid,row in rows.items():
        positions=current[mid].get("placements",[])
        mapping={old:SWAPS[old][0] for old in names}
        expected={**current[mid],"placements":[[mapping.get(p[0],p[0]),*p[1:]] for p in positions]}
        assert expected==row,(mid,"installed map changed since planning")
    replacements={engine/INDEX.parent/rel:data for rel,data in resources.items()}
    replacements[path]=json_bytes({**current,**rows})
    before={target:target.read_bytes() if target.exists() else None for target in replacements}
    assert before[path]==baseline,"The live index changed during installation."
    changed=[]
    try:
        for target,data in replacements.items():
            assert (target.read_bytes() if target.exists() else None)==before[target],target
            changed.append(target)
            write(target,data)
        assert all(target.read_bytes()==data for target,data in replacements.items())
    except BaseException:
        for target in reversed(changed):
            if before[target] is None:
                target.unlink(missing_ok=True)
            else:
                write(target,before[target])
        raise
    return changes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("fit","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    parser.add_argument("--only",choices=SWAPS,nargs="+")
    args=parser.parse_args()
    names=tuple(args.only or (old for old in SWAPS if old!="shadowlands_broken_cart"))
    engine=args.repo.resolve()/"_tools/rpgcobo-tool"
    if args.action=="fit":
        fit(engine,names)
        return
    if not args.profile or args.profile.resolve()==engine:
        parser.error("Use an isolated native profile for staging and replay.")
    action={"stage":stage,"publish":publish}[args.action]
    changes=action(engine,args.profile.resolve(),names)
    label="Staged" if args.action=="stage" else "Installed"
    total=sum(sum(counts.values()) for counts in changes.values())
    print(f"{label} {total} smooth furniture placements across {len(changes)} maps.")
    print(json_bytes(changes).decode())


if __name__=="__main__":
    main()



