"""Stage and install only the audited door placements and portal anchors."""

import json
from pathlib import Path
import sys

from door_centering_candidates import replace_index_field, replace_live_positions, variant, verify
from publish_castle_gates import CATALOG, INDEX, resource_files, replace_file_contents


HERE=Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_bytes())


def changes(repo, profile, publish):
    findings=read(HERE/"door-centering-candidate.json")
    verify(repo,findings)
    engine=repo/"_tools/rpgcobo-tool"
    index=read(engine/INDEX)
    catalog=read(engine/CATALOG)
    for field in ("doors","placements"):
        replace_index_field(index,findings,field)
    replace_live_positions(catalog,findings)
    maps=set(findings["doors"])|set(findings["placements"])
    event_maps=set(findings["events"])
    destinations={edit["destination"]["mapid"] for rows in findings["events"].values()
                  for edit in rows.values()}
    catalog_scope=event_maps|maps|destinations
    if publish:
        checked=read(profile/INDEX)
        checked_catalog=read(profile/CATALOG)
        assert all(checked[mid]==index[mid] for mid in maps)
        assert all(checked_catalog[mid]==catalog[mid] for mid in event_maps)
        source,_,_,previous,updated=variant(repo,findings)
        assert source.read_bytes()==previous
        files={engine/INDEX: json.dumps(index,separators=(",",":")).encode(),
               engine/CATALOG: json.dumps(catalog,ensure_ascii=False,indent="\t").encode(),
               source:updated}
    else:
        current=read(profile/INDEX)
        current_catalog=read(profile/CATALOG)
        for mid in maps:
            current[mid]=index[mid]
        for mid in catalog_scope:
            current_catalog[mid]=catalog[mid]
            rel=Path("project/data/mapdata")/(mid+".bw")
            (profile/rel).write_bytes((engine/rel).read_bytes())
        resources=resource_files((engine/INDEX).parent,{mid:index[mid] for mid in maps})
        for asset,content in resources.items():
            dest=(profile/INDEX).parent/asset
            if not dest.is_file() or dest.read_bytes()!=content:
                dest.write_bytes(content)
        files={profile/INDEX:json.dumps(current,separators=(",",":")).encode(),
               profile/CATALOG:json.dumps(current_catalog,ensure_ascii=False,separators=(",",":")).encode()}
    before={file:file.read_bytes() for file in files}
    try:
        for file,content in files.items():
            assert file.read_bytes()==before[file]
            replace_file_contents(file,content)
        assert all(file.read_bytes()==content for file,content in files.items())
    except BaseException:
        for file,content in before.items():
            if file.read_bytes()!=content:
                replace_file_contents(file,content)
        raise
    print(f"{'Installed' if publish else 'Staged'} door alignment on {len(maps|event_maps)} maps.")


if __name__=="__main__":
    changes(*(Path(v).resolve() for v in sys.argv[1:3]),"--publish" in sys.argv[3:])
