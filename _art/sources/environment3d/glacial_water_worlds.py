"""Project a clear-water depth strip along the winter River of Gold."""
from pathlib import Path
import importlib.util
import json
import struct
import sys

import numpy as np
from PIL import Image

from export_coast import Geometry, STAGE, export
from install_environment_rows import install

HERE=Path(__file__).resolve().parent
MAPS=("M422","M423","M424","M888")
ROOT=Path("project/resource/native_environment")
PREFIX="winter_river_glacial_depth"
FAMILIES={"M422":(5.,12.),"M424":(4.5,11.)}


def world_quads(path):
    raw=path.read_bytes()
    assert raw[:6]==b"SMDL\x00\x01"
    role,format,_,dimension,_,_,offset,count=struct.unpack_from(">6BII",raw,14)
    assert (role,format,dimension,offset)==(0,1,3,0)
    return np.frombuffer(raw,dtype=">f4",count=count*3,offset=28).reshape(-1,4,3)


def coordinates(mid,x,z):
    if mid in FAMILIES:
        bank,width=FAMILIES[mid]
        depth=(bank-z)/width
    elif mid=="M423":
        depth=.60+.095*np.sin(x*.12+z*.19)+.10*np.cos(z*.22)
    elif z<40.:
        depth=(19.-z)/14.
    else:
        depth=min(z-47.,52.5-z)/2.82
    return x/34.+.032*np.sin(z*.28), .007+.985*float(np.clip(depth,0.,1.))


def project(mid,old):
    result=Geometry()
    for native in old:
        left,y,front=native.min(axis=0)
        right,high,back=native.max(axis=0)
        assert abs(float(high-y))<1.e-6 and right>left and back>front
        rings=np.linspace(front,back,1+max(1,int(np.ceil((back-front)/.49))))
        columns=np.linspace(left,right,1+max(1,int(np.ceil((right-left)/4.4))))
        for za,zb in zip(rings,rings[1:]):
            for xa,xb in zip(columns,columns[1:]):
                corners=[(xa,za,y),(xb,za,y),(xb,zb,y),(xa,zb,y)]
                uv=[coordinates(mid,x,z) for x,z,_ in corners]
                result.quad(corners,uv,PREFIX)
    return result


def json_rows(path):
    return json.loads(path.read_bytes())


def stage(engine,profile):
    live=engine/ROOT
    spec=importlib.util.spec_from_file_location("glacial_strip",HERE/"water-color-pass/glacial_strip.py")
    painter=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(painter)
    for index in range(64):
        frame=painter.frame(index)
        assert frame.shape==(256,1024,3) and frame.dtype==np.uint8
        Image.fromarray(frame).save(STAGE/"tex"/f"{PREFIX}{index:02}.png")
    rows=json_rows(STAGE/"index.json")
    baseline=json_rows(live/"index.json")
    for mid in MAPS:
        tag=mid.lower()+"_winter_river_water"
        mesh=project(mid,world_quads(live/(tag+".mdl")))
        export(tag+"_shore_strip",mesh,{PREFIX:(PREFIX+"00.png",.29)})
        current=baseline[mid]
        rows[mid]={**current,"water":tag+"_shore_strip",
                   "waterSequence":{"prefix":PREFIX,"frames":64,"seconds":17.8}}
    (STAGE/"index.json").write_text(json.dumps(rows,separators=(",",":")),"utf8")
    install(profile,MAPS)


def publish(engine,profile):
    old=json_rows(engine/ROOT/"index.json")
    checked=json_rows(profile/ROOT/"index.json")
    created=json_rows(STAGE/"index.json")
    keys=set(("water","waterSequence"))
    for mid in MAPS:
        assert checked[mid]==created[mid]
        assert {k:v for k,v in checked[mid].items() if k not in keys}=={k:v for k,v in old[mid].items() if k not in keys}
        for relative in [*(f'{checked[mid]["water"]}.{ext}' for ext in ("pm","mdl")),
                         *(f"tex/{PREFIX}{i:02}.png" for i in range(64))]:
            assert (profile/ROOT/relative).read_bytes()==(STAGE/relative).read_bytes()
    install(engine,MAPS,preserve_existing=True,replace_existing=True)
    assert json_rows(engine/ROOT/"index.json")=={**old,**{mid:checked[mid] for mid in MAPS}}


if __name__=="__main__":
    engine=Path(sys.argv[1]).resolve()/"_tools/rpgcobo-tool"
    profile=Path(sys.argv[2]).resolve()
    (publish if "--publish" in sys.argv[3:] else stage)(engine,profile)
