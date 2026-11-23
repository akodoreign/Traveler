"""Install Snake Den's render preset without editing other render settings."""
from copy import deepcopy
import json
from pathlib import Path
import sys

def install(profile):
    path=profile/"project/resource/renderset.json"
    raw=path.read_bytes()
    data=json.loads(raw)
    presets=data["rendersets"]
    source=next(row for row in presets if row["id"]=="rt_hd2d_cave")
    candidate=deepcopy(source)
    candidate["id"]="rt_hd2d_snake_den"
    candidate["name"]={"en":"Snake Den","ja":"Snake Den"}
    candidate["envlights"][0].update(power=1130,head=-25,pitch=52,color=-1804033,scolor=-1804033)
    candidate["exposure"]["ev100"]=8.85
    candidate["fog"].update(color=0x101e43bc,density=.014,zoffs=19.)
    candidate["ibl"].update(ibldiff=645,iblspec=150,iblcolor=-1)
    candidate["postfx"].update(bloompow=.20,bloomthrs=.68)
    candidate["ss"].update(aopow=.74)
    for current in presets:
        if current["id"]==candidate["id"]:
            current.update(candidate)
            break
    else:
        presets.append(candidate)
    result=json.dumps(data,ensure_ascii=False,indent="\t").encode("utf8")+b"\n"
    if path.read_bytes()!=raw:
        raise RuntimeError("Render settings changed during installation")
    path.write_bytes(result)

if __name__=="__main__":
    install(Path(sys.argv[1]).resolve())
