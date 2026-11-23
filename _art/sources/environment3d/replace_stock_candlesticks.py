"""Replace the widely placed candle1 model with a compact cedar paper lantern."""

import json
from pathlib import Path
import sys

import numpy as np

here=Path(__file__).resolve().parent
repo=Path(sys.argv[1])
models=repo/"_tools/rpgcobo-tool/project/resource/vox/map/lamp/lamp1.vox"
palette_path=repo/"_tools/rpgcobo-tool/project/resource/map_vox.json"
sys.path.insert(0,str(repo/"tools"))
import voxfile

stock=models.read_bytes()
config_bytes=palette_path.read_bytes()
config=json.loads(config_bytes)
variant=config["lamp"]["#4#"]
assert variant["vp0"]==["lamp1","candle1"]
vox=voxfile.VoxFile.load(models)
assert len(vox.models)==18 and vox.models[12].size==vox.models[13].size==(12,8,12)
indices={11:(62,40,24),14:(111,71,39),53:(148,116,82),54:(174,140,99),55:(201,166,112),
         56:(220,191,135),177:(177,89,36),178:(207,111,52),179:(228,144,62),180:(239,176,83)}
for i in range(0,len(variant["pal0"]),2):
    slot=variant["pal0"][i]
    if slot in indices:
        red,green,blue=indices[slot]
        variant["pal0"][i+1]=(variant["pal0"][i+1]&0xff000000) | red | (green<<8) | (blue<<16)

for index,lit in ((12,False),(13,True)):
    lantern=np.zeros((12,8,12),dtype=np.uint8)
    lantern[2:10,1:7,:2]=11
    lantern[3:9,2:6,2:10]=0
    for height in range(2,10):
        for x in range(2,10):
            for z in range(1,7):
                if x not in (2,9) and z not in (1,6):
                    continue
                rail=(x in (2,9) and z in (1,6)) or height in (2,9)
                if rail or (height in (5,6) and (z in (1,6) and x==5 or x in (2,9) and z==3)):
                    lantern[x,z,height]=14 if (x+z+height)%4 else 11
                else:
                    patch=((x*13+z*5+height*3)//5)%4
                    lantern[x,z,height]=(177,178,179,180)[patch] if lit else (53,54,55,56)[patch]
    lantern[1:11,0:8,10]=11
    lantern[2:10,1:7,11]=14
    vox.models[index].vox=lantern

candidate=here/"candle1-lantern.vox"
vox.save(candidate)
old_vox=voxfile.VoxFile.load(models)
new_vox=voxfile.VoxFile.load(candidate)
assert old_vox.chunks==new_vox.chunks
assert all(np.array_equal(a.vox,b.vox) for i,(a,b) in enumerate(zip(old_vox.models,new_vox.models,strict=True))
           if i not in (12,13))
eol=b"\r\n" if b"\r\n" in config_bytes else b"\n"
ending=eol if config_bytes.endswith(eol) else b""
encode=lambda data:json.dumps(data,ensure_ascii=False,indent="\t").encode().replace(b"\n",eol)+ending
assert encode(json.loads(config_bytes))==config_bytes
formatted=encode(config)
assert models.read_bytes()==stock and palette_path.read_bytes()==config_bytes
(here/"lamp1-before-paper-lantern.vox").write_bytes(stock)
try:
    models.write_bytes(candidate.read_bytes())
    palette_path.write_bytes(formatted)
except BaseException:
    models.write_bytes(stock)
    palette_path.write_bytes(config_bytes)
    raise
print("Replaced the two candle1 states with small paper lanterns. Other lamp models and collision are unchanged.")
