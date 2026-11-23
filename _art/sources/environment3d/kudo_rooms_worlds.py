"""Compile and publish fitted story interiors with verified event fixtures."""

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

from kudo_room_map_section import KUDO_ROOM_LAYOUTS
from shadowlands_march_worlds import compile_worlds, overwrite


HERE=Path(__file__).resolve().parent
MAPS=tuple(KUDO_ROOM_LAYOUTS)
KAMEN_ROOMS={
    "M363":(3,28,8,26,6,("#9#","#10#","#11#","#12#")),
    "M367":(3,34,8,26,6,("#5#","#6#","#7#","#8#")),
}
KAMEN_TEMPLE=("M365","M366","M867","M868")
OJATARA_ROOMS={
    "M370":(3,37,8,27,6,("#13#","#14#","#15#","#16#","#17#")),
    "M376":(3,28,8,25,7,("#6#","#7#","#8#","#9#")),
}
WILLOW_ROOMS={"M346":(3,28,8,25,7,("#5#","#6#","#7#","#8#"))}
DRAGON_ROOMS={"M381":(3,30,8,26,6,("#8#","#9#","#10#","#11#"))}
AUTUMN_ROOMS={
    "M388":(3,35,8,26,6,("#14#","#15#","#16#","#17#")),
    "M394":(3,35,8,26,6,("#9#","#10#","#11#","#12#")),
}


ROOMS={
    "kudo":(KUDO_ROOM_LAYOUTS,(),"M351"),
    "kamen":(KAMEN_ROOMS,KAMEN_TEMPLE,"M362"),
    "ojatara":(OJATARA_ROOMS,(),"M369"),
    "willow":(WILLOW_ROOMS,(),"M345"),
    "dragon":(DRAGON_ROOMS,(),"M380"),
    "autumn":(AUTUMN_ROOMS,(),"M387"),
}


def room_group(group,city,ojatara):
    return "ojatara" if ojatara else "kamen" if city else group


def variant(repo,city=False,ojatara=False,*,group="kudo"):
    source=repo/"tools/gen_maps.py"
    sys.path.insert(0,str(source.parent))
    import gen_maps as gm
    raw=source.read_bytes()
    eol="\r\n" if b"\r\n" in raw else "\n"
    text=raw.decode().replace("\r\n","\n")
    group=room_group(group,city,ojatara)
    name=f"rebuild_{group}_room"
    if f"def {name}(" not in text:
        start=text.index("def make(i):")
        end=text.index("\n    return m, ev",start)
        fragment=(HERE/"kudo_room_map_section.py").read_text(encoding="utf8")
        fragment=fragment[fragment.index("KUDO_ROOM_LAYOUTS ="):].strip()
        hook="\n    if i in KUDO_ROOM_LAYOUTS:\n        rebuild_kudo_room(m, ev)"
        if group=="kamen":
            fragment=(f"KAMEN_ROOM_LAYOUTS = {KAMEN_ROOMS!r}\n\n\n"+
                      fragment[fragment.index("def rebuild_kudo_room"):].replace(
                          "rebuild_kudo_room","rebuild_kamen_room").replace(
                          "KUDO_ROOM_LAYOUTS","KAMEN_ROOM_LAYOUTS").replace(
                          "right-left+1,1,STONEW,5)", "right-left+1,1,STONEW,8 if m.mid == \"M367\" else 5)"))
            hook=("\n    if i in KAMEN_ROOM_LAYOUTS:\n        rebuild_kamen_room(m, ev)"
                  "\n    if i in (\"M365\", \"M366\"):\n"
                  "        m.objs = [o for o in m.objs if o[\"t\"] != \"fb\" or o[\"fbtype\"] != 20]"
                  "\n    if i == \"M868\":\n"
                  "        m.objs = [o for o in m.objs if o.get(\"blk\") != DARKWOOD or o[\"z\"] != 93]")
        if group in ("ojatara","willow","dragon","autumn"):
            key=f"{group.upper()}_ROOM_LAYOUTS"
            fragment=(f"{key} = {ROOMS[group][0]!r}\n\n\n"+
                      fragment[fragment.index("def rebuild_kudo_room"):].replace(
                          "rebuild_kudo_room",name).replace("KUDO_ROOM_LAYOUTS",key))
            hook=f"\n    if i in {key}:\n        {name}(m, ev)"
        text=text[:end]+hook+text[end:]
        text=text.replace("def make(i):",fragment+"\n\n\ndef make(i):",1)
    module=ModuleType("kudo_rooms_candidate")
    module.__dict__.update({key:value for key,value in vars(gm).items() if key!="__name__"})
    sys.modules[module.__name__]=module
    exec(compile(text,str(source),"exec"),module.__dict__)
    return gm,module,raw,text.replace("\n",eol).encode()


def main(repo,engine,publish,group="kudo"):
    old,new,source_before,source_after=variant(repo,group=group)
    family=f"{group}-interiors"
    layouts,other,start=ROOMS[group]
    ids=(*layouts,*other)
    new.JOBDIR=str(engine/"tmp/rt_mapgen")
    data=repo/"_tools/rpgcobo-tool/project/data"
    catalog=data/"map.json"
    raw_catalog=catalog.read_bytes()
    meta=json.loads(raw_catalog)
    receipts={}
    jobs=[]
    for mid in ids:
        previous,prev=old.make(mid)
        world,ev=new.make(mid)
        assert (previous.w,previous.d)==(world.w,world.d)
        original_events=prev.ev if prev else {}
        current_events=ev.ev if ev else {}
        decor=layouts[mid][-1] if mid in layouts else ()
        removed=set(original_events)-set(current_events)
        if source_before!=source_after:
            assert removed==set(decor)
        assert all(original_events[key]==event for key,event in current_events.items())
        if mid not in layouts:
            assert new.np.array_equal(previous.hgt,world.hgt)
            assert new.np.array_equal(previous.blk,world.blk)
        for key in removed:
            row=meta[mid]["event"][key]
            assert row["role"]=="light" or all(p["trigger"]==0 and not p["cmdblock"] for p in row["page"])
        row=world.write()
        row["out"]=f"tmp/rt_mapgen/{mid}_{family}_candidate.bw"
        jobs.append(row)
        receipts[mid]={"old_decor_removed":sorted(removed),"story_events_retained":len(current_events)}
    receipt=HERE/f"{family}-worlds.json"
    spec=sha256(json.dumps(jobs,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if publish:
        proof=json.loads(receipt.read_bytes())
        assert proof["spec"]==spec
        replacements={}
        for mid in ids:
            path=Path("project/data/mapdata")/(mid+".bw")
            binary=(engine/path).read_bytes()
            assert sha256(binary).hexdigest()==proof["rooms"][mid]["sha256"]
            replacements[data/"mapdata"/(mid+".bw")]=binary
            for key in layouts[mid][-1] if mid in layouts else ():
                meta[mid]["event"].pop(key,None)
        source=repo/"tools/gen_maps.py"
        assert source.read_bytes()==source_before and catalog.read_bytes()==raw_catalog
        eol=b"\r\n" if b"\r\n" in raw_catalog else b"\n"
        replacements[catalog]=json.dumps(meta,ensure_ascii=False,indent="\t").encode().replace(b"\n",eol)
        replacements[source]=source_after
        original={p:p.read_bytes() for p in replacements}
        wrote=[]
        try:
            for path,content in replacements.items():
                wrote.append(path)
                overwrite(path,content)
        except BaseException:
            for path in reversed(wrote):
                overwrite(path,original[path])
            raise
    else:
        compile_worlds(engine,jobs,stem=family,start=start)
        path=engine/"project/data/map.json"
        cloned=json.loads(path.read_bytes())
        for mid,row in receipts.items():
            f=engine/"project/data/mapdata"/(mid+".bw")
            row["sha256"]=sha256(f.read_bytes()).hexdigest()
            for key in layouts[mid][-1] if mid in layouts else ():
                cloned[mid]["event"].pop(key,None)
        path.write_text(json.dumps(cloned,ensure_ascii=False,indent="\t"),encoding="utf8")
        receipt.write_text(json.dumps({"spec":spec,"rooms":receipts},indent=2),encoding="utf8")
    print(receipts)


if __name__=="__main__":
    group=room_group("autumn" if "--autumn" in sys.argv[3:] else "dragon" if "--dragon" in sys.argv[3:]
                     else "willow" if "--willow" in sys.argv[3:] else "kudo",
                     "--city" in sys.argv[3:],"--ojatara" in sys.argv[3:])
    main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),
         "--publish" in sys.argv[3:],group)
