"""Stage and publish the fitted castle art without changing story routes."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys

from build_clan_castles import STAGE
from publish_castle_gates import CATALOG, INDEX, RUNTIME, resource_files, replace_file_contents
from shadowlands_march_worlds import compile_worlds

HERE = Path(__file__).resolve().parent
PLAN = "clan_castle_art.json"
SOURCE_PATCH = """
with open(os.path.join(HERE, "clan_castle_art.json"), encoding="utf-8") as _castle_art_source:
    _CLAN_CASTLE_ART = json.load(_castle_art_source)


def rebuild_clan_castle_art(m, ev):
    plan = _CLAN_CASTLE_ART.get(m.mid)
    if not plan:
        return
    for obj in plan["remove"]:
        if obj in m.objs:
            m.objs.remove(obj)
    for obj in plan.get("add", ()):
        if obj not in m.objs:
            m.objs.append(obj)
    for point in plan.get("walls", ()):
        cell = tuple(point)
        if cell not in m.walls:
            m.walls.append(cell)
    for key, (previous, updated) in plan.get("positions", {}).items():
        event = ev.ev.get(key)
        if event and event.get("role") == "portal" and event["pos"] == previous:
            event["pos"] = updated.copy()
    for key, (previous, replacement) in plan["decor"].items():
        event = ev.ev.get(key)
        if event and event.get("mdlid") == previous and event.get("role") == "custom" and len(event["page"]) == 1:
            page = event["page"][0]
            if not (page.get("cmdblock") or page.get("reqs") or page.get("trigger") or event.get("reqs0")):
                event["mdlid"] = replacement


"""


def read(path):
    return json.loads(path.read_bytes())


def write_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf8")


def hash_bytes(data):
    return sha256(data).hexdigest()


def resources(engine, rows):
    return dict((engine / INDEX.parent / relative, content)
                for relative,content in resource_files(STAGE,rows).items())


def patch_catalog(original, plans):
    for mid, plan in plans.items():
        for key,(old,new) in plan.get("positions",{}).items():
            event=original[mid]["event"][key]
            assert event["role"]=="portal" and event["pos"] in (old,new), (mid,key)
            event["pos"]=new.copy()
        for key, (old,new) in plan["decor"].items():
            event=original[mid]["event"][key]
            assert event["mdlid"] in (old,new), (mid,key,"unexpected decoration")
            assert event.get("role")=="custom" and len(event["page"])==1 and not event.get("reqs0"), (mid,key)
            page=event["page"][0]
            assert not (page.get("cmdblock") or page.get("reqs") or page.get("trigger")), (mid,key)
            event["mdlid"]=new
    return original


def set_file(path,content):
    if path.exists():
        if path.read_bytes()!=content:
            replace_file_contents(path,content)
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("xb") as out:
            out.write(content)


def stage(repo,profile,group,plans,rows):
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm

    live=repo/"_tools/rpgcobo-tool"
    live_map=read(live/CATALOG)
    assets=resources(profile,rows)
    for path, content in assets.items():
        set_file(path,content)
    catalog=read(profile/CATALOG)
    if hasattr(gm,"_CLAN_CASTLE_ART"):
        gm._CLAN_CASTLE_ART={mid:plan for mid,plan in gm._CLAN_CASTLE_ART.items() if mid not in plans}
    target=set(plans)
    if "M573" in plans:
        target.add("M296")
    for castle in gm.CLAN_CASTLES:
        if castle["ids"][0] in plans:
            target.add(castle["town"])
    for mid in target:
        catalog[mid]=live_map[mid]
        if mid not in plans:
            shutil.copyfile(live/f"project/data/mapdata/{mid}.bw",
                            profile/f"project/data/mapdata/{mid}.bw")
            for path, content in resource_files((live/INDEX).parent,{mid:read(live/INDEX).get(mid,{})}).items():
                set_file((profile/INDEX).parent/path,content)
    index=read(profile/INDEX)
    index.update({mid:read(live/INDEX)[mid] for mid in target-set(plans) if mid in read(live/INDEX)})
    index.update(rows)
    set_file(profile/CATALOG,write_json(patch_catalog(catalog,plans)))
    set_file(profile/INDEX,write_json(index))
    set_file(profile/RUNTIME,(live/RUNTIME).read_bytes())

    gm.JOBDIR=str(profile/"tmp/rt_mapgen")
    jobs=[]
    for mid,plan in plans.items():
        world,events=gm.make(mid)
        original=list(world.objs)
        for obj in plan["remove"]:
            assert obj in world.objs, (mid,obj)
            world.objs.remove(obj)
        assert len(original)>=len(world.objs)
        for obj in plan.get("add",()):
            if obj not in world.objs:
                world.objs.append(obj)
        for point in plan.get("walls", ()):
            x,z=point
            assert 0<=x<world.w and 0<=z<world.d, (mid,point)
            if (x,z) not in world.walls:
                world.walls.append((x,z))
        candidate=world.write()
        candidate["out"]=f"tmp/rt_mapgen/{mid}_castle_art.bw"
        jobs.append(candidate)
    for i in range(0,len(jobs),16):
        compile_worlds(profile,jobs[i:i+16],stem=f"clan-castles-{group}-{i//16+1}")
    proof={}
    for mid in plans:
        built=profile/f"project/data/mapdata/{mid}.bw"
        proof[mid]={"world":hash_bytes(built.read_bytes()),"art":rows[mid]["terrain"],
                    "catalog":hash_bytes(write_json(catalog[mid]))}
    (HERE/f"clan-castles-{group}"/"staged-proof.json").write_text(json.dumps(proof,indent=2),"utf8")
    print(f"Staged {len(plans)} castle maps in {profile.name}.")


def publish(repo,profile,group,plans,rows):
    live=repo/"_tools/rpgcobo-tool"
    proof=read(HERE/f"clan-castles-{group}"/"staged-proof.json")
    staged=read(profile/CATALOG)
    catalog=patch_catalog(read(live/CATALOG),plans)
    index=read(live/INDEX)
    assert set(proof)==set(plans)==set(rows)
    staged_index=read(profile/INDEX)
    updates={}
    for mid in plans:
        assert staged_index[mid]==rows[mid] and staged[mid]==catalog[mid], (mid,"staged data differs")
        relative=Path(f"project/data/mapdata/{mid}.bw")
        content=(profile/relative).read_bytes()
        assert hash_bytes(content)==proof[mid]["world"], (mid,"compiled fingerprint differs")
        updates[live/relative]=content
    updates[live/CATALOG]=write_json(catalog)
    updates[live/INDEX]=write_json({**index,**rows})
    for p,content in resources(live,rows).items():
        peer=profile/INDEX.parent/p.relative_to(live/INDEX.parent)
        assert peer.read_bytes()==content, (p,"staged resource differs")
        assert not p.exists() or p.read_bytes()==content, (p,"different shared file")
        if not p.exists():
            updates[p]=content
    generator=repo/"tools/gen_maps.py"
    source=generator.read_bytes()
    eol=b"\r\n" if b"\r\n" in source else b"\n"
    if b"def rebuild_clan_castle_art" not in source:
        head=b"def make(i):"
        assert source.count(head)==1
        source=source.replace(head,SOURCE_PATCH.encode().replace(b"\n",eol).lstrip()+head,1)
        start=source.index(head)
        before_ret=source.index(eol+b"    return m, ev",start)
        call=eol+b"    if ev is not None:"+eol+b"        rebuild_clan_castle_art(m, ev)"
        source=source[:before_ret]+call+source[before_ret:]
    asset_plan=repo/"tools"/PLAN
    saved=read(asset_plan) if asset_plan.exists() else {}
    updates[asset_plan]=write_json({**saved,**plans})
    updates[generator]=source
    before={p:p.read_bytes() if p.exists() else None for p in updates}
    changed=[]
    try:
        for p,content in updates.items():
            assert (p.read_bytes() if p.exists() else None)==before[p],(p,"changed during publication")
            changed.append(p)
            set_file(p,content)
        assert all(p.read_bytes()==b for p,b in updates.items())
    except BaseException:
        for p in reversed(changed):
            if before[p] is None:
                p.unlink(missing_ok=True)
            else:
                set_file(p,before[p])
        raise
    print(f"Installed {len(plans)} castle maps. The world index now covers {len(set(index)|set(rows))} maps.")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo",type=Path)
    p.add_argument("profile",type=Path)
    p.add_argument("group")
    p.add_argument("--publish",action="store_true")
    a=p.parse_args()
    bundle=HERE/f"clan-castles-{a.group}"
    action=publish if a.publish else stage
    action(a.repo.resolve(),a.profile.resolve(),a.group,read(bundle/"plans.json"),read(bundle/"rows.json"))
