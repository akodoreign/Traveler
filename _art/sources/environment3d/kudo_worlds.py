"""Replace the stock trees and lamps on the River of Gold road and in Kudo."""

from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

from shadowlands_march_worlds import compile_worlds, overwrite


HERE=Path(__file__).resolve().parent
MAPS=("M350","M351")
MARSH=("M355","M356","M357","M358","M862","M863","M864")


def revised_source(text):
    start=text.index("def river_road():")
    end=text.index("\n\n# ---- M351 ",start)
    road=text[start:end]
    trees=("    for x in range(5, 110, 8):\n"
           "        m.tree(x, 10 + x % 2, TREE_S)                                       # reeds\n")
    text=text[:start]+road.replace(trees,"")+text[end:]
    start=text.index("def kudo():")
    end=text.index("\n\n# ---- M352 ",start)
    town=text[start:end]
    if "    for x, z in ((60, 6)" in town:
        trees=town.index("    for x, z in ((60, 6)")
        gardens=town.index("    for x in range(14, 50, 6):",trees)
        lamps=town.index("    for x in (12, 26, 40, 60, 74, 88, 104):",gardens)
        events=town.index("    ev = Events(m)",lamps)
        town=town[:trees]+town[gardens:lamps]+town[events:]
    return text[:start]+town+text[end:]


def revised_marsh(text):
    if "def rebuild_kudo_marsh(" in text:
        return text
    start=text.index("def make(i):")
    end=text.index("\n    return m, ev",start)
    text=text[:end]+'\n    if i in ("M355", "M356", "M357", "M358", "M862", "M863", "M864"):\n        rebuild_kudo_marsh(m)'+text[end:]
    return text.replace("def make(i):",'''def rebuild_kudo_marsh(m):
    # The new placed willows and reeds replace the stock vegetation. Keep
    # the old barge's block deck as a footprint under its new timber hull.
    removed = {(63+PAD_X,2+PAD_BOTTOM),(66+PAD_X,3+PAD_BOTTOM)}
    m.objs = [item for item in m.objs if not (
        item["t"]=="fb" and item["fbtype"]==20 or
        m.mid=="M356" and item["t"]=="fill" and (item["x"],item["z"]) in removed
    )]
    if m.mid in ("M358","M864"):
        # Round the ritual pool inside its existing footprint while keeping
        # every actor mark outside the reshaped shoreline.
        pz,px = np.where(m.blk==EMBER)
        if len(px):
            cx,cz = px.mean(),pz.mean()
            rx,rz = (np.ptp(px)+1)*.50,(np.ptp(pz)+1)*.51
            silhouette = ((px-cx)/rx)**2+((pz-cz)/rz)**2
            rim=1+.10*np.sin(px*.77+pz*.62)+.06*np.cos(pz*.71)
            z,x=pz[silhouette>rim],px[silhouette>rim]
            m.blk[z,x]=TARSTAIN
            m.hgt[z,x]=3 if m.mid=="M358" else 0


def make(i):''',1)


def variant(repo,marsh=False):
    source=repo/"tools/gen_maps.py"
    sys.path.insert(0,str(source.parent))
    import gen_maps as gm

    raw=source.read_bytes()
    eol="\r\n" if b"\r\n" in raw else "\n"
    transform=revised_marsh if marsh else revised_source
    text=transform(raw.decode().replace("\r\n","\n"))
    candidate=ModuleType("kudo_world_candidate")
    candidate.__dict__.update({key:value for key,value in vars(gm).items() if key!="__name__"})
    sys.modules[candidate.__name__]=candidate
    exec(compile(text,str(source),"exec"),candidate.__dict__)
    return gm,candidate,raw,text.replace("\n",eol).encode()


def main(repo,profile,publish,marsh=False):
    source=repo/"tools/gen_maps.py"
    gm,candidate,raw,updated=variant(repo,marsh)
    family="kudo-marsh" if marsh else "kudo-river"
    ids=MARSH if marsh else MAPS
    candidate.JOBDIR=str(profile/"tmp/rt_mapgen")
    jobs=[]
    audit={}
    for mid in ids:
        old,old_events=gm.make(mid)
        world,events=candidate.make(mid)
        assert (old_events.ev if old_events else None)==(events.ev if events else None)
        modified=(old.blk!=world.blk) | (old.hgt!=world.hgt)
        if modified.any():
            assert marsh and mid in ("M358","M864")
            assert gm.np.all(old.blk[modified]==gm.EMBER) and gm.np.all(world.blk[modified]==gm.TARSTAIN)
        removed=len(old.objs)-len(world.objs)
        if raw!=updated:
            assert removed>0 if marsh else removed=={"M350":13,"M351":18}[mid],(mid,removed)
        row=world.write()
        row["out"]=f"tmp/rt_mapgen/{mid}_{family}_candidate.bw"
        jobs.append(row)
        audit[mid]={"removed_stock_fixtures":removed,"events_preserved":len(events.ev) if events else 0}

    receipt=HERE/f"{family}-worlds.json"
    digest=sha256(json.dumps(jobs,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if publish:
        expected=json.loads(receipt.read_bytes())
        assert expected["job_spec"]==digest
        items={}
        for mid in ids:
            path=Path("project/data/mapdata")/(mid+".bw")
            content=(profile/path).read_bytes()
            assert sha256(content).hexdigest()==expected["worlds"][mid]["sha256"]
            items[repo/"_tools/rpgcobo-tool"/path]=content
        assert source.read_bytes()==raw
        items[source]=updated
        prior={path:path.read_bytes() for path in items}
        changed=[]
        try:
            for path,data in items.items():
                changed.append(path)
                overwrite(path,data)
        except BaseException:
            for path in reversed(changed):
                overwrite(path,prior[path])
            raise
    else:
        compile_worlds(profile,jobs,stem=family)
        for mid in ids:
            f=profile/"project/data/mapdata"/(mid+".bw")
            audit[mid]["sha256"]=sha256(f.read_bytes()).hexdigest()
        receipt.write_text(json.dumps({"job_spec":digest,"worlds":audit},indent=2),encoding="utf8")
    print(audit)


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),
         "--publish" in sys.argv[3:],"--marsh" in sys.argv[3:])
