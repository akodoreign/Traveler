"""Prepare a map-local coastal material and daylight candidate."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from publish_castle_gates import publish as transact, resource_files


ASSETS=Path("project/resource/native_environment")
CATALOG=Path("project/data/map.json")
RENDER=Path("project/resource/renderset.json")
FRAME=re.compile(r'^([ \t]*texture0 = ")tex/([^"]+)(")',re.M)
MODEL=re.compile(r'^modeldata = "([^"]+)"',re.M)
ALIAS="_coastal_daylight"
LUMA=np.array((.213,.715,.072),dtype=np.float32)

CORE={
    "M102":"road","M470":"road","M474":"road","M486":"cave","M828":"arena",
}
PHOENIX={
    "M475":"road","M487":"cave","M799":"cave","M846":"arena",
}
GROUPS={"coast":CORE,"phoenix":PHOENIX}
WATER={
    "surf":("traveler_coast_clear_water",(8,41,102),(33,145,173),.55),
    "yasuki_open_blue_coast":("yasuki_coast_clear_water",(8,37,116),(36,155,188),.43),
    "doji_open_cove_water":("doji_cove_clear_water",(9,41,125),(36,167,201),.42),
    "doji_cave_tide":("doji_tide_clear_water",(9,61,118),(31,142,174),.52),
    "phoenix_fox_spring":("phoenix_fox_clear_spring",(10,54,109),(35,143,154),.43),
}
PAINT={
 "cliff":((84,88,94),.54),"sand":((200,159,99),.59),"path":((143,93,55),.53),
 "meadow":((20,107,47),.76),"doji_maritime_grass":((11,121,49),.82),
 "doji_coast_path":((135,86,54),.69),"doji_tide_sand":((194,159,104),.59),
 "doji_coastal_sandstone":((45,69,109),.63),"doji_sea_cliff_slate":((28,64,111),.69),
 "doji_tidal_recess":((17,33,58),.62),"doji_cave_wet_slate":((27,56,87),.61),
 "doji_tide_linen":((239,223,180),.61),"doji_tide_indigo":((16,44,135),.76),
 "branch_worn_cedar":((83,42,24),.66),"branch_smoked_cedar":((47,22,19),.72),
 "yasuki_blue_coast_slate":((27,55,103),.67),"yasuki_recess_shale":((20,32,46),.53),
 "yasuki_salt_grass":((29,108,42),.79),"yasuki_dry_coast_track":((144,86,40),.64),
 "yasuki_gilt_silt":((179,133,75),.53),"yasuki_tarred_cedar":((47,25,19),.54),
 "yasuki_crab_blue":((11,37,102),.69),"yasuki_crab_vermilion":((178,42,25),.56),
 "phoenix_evergreen_floor":((27,101,43),.80),"phoenix_moss_floor":((48,97,46),.70),
 "phoenix_worn_trail":((147,91,53),.67),"phoenix_ochre_shelves":((132,70,41),.57),
 "phoenix_cliff_recess":((38,26,49),.55),"phoenix_hematite_cliff":((65,43,65),.62),
 "phoenix_shrine_cedar":((86,47,26),.58),"phoenix_shrine_lacquer":((172,38,34),.67),
 "phoenix_shrine_linen":((235,217,176),.58),
}
BOTANIC={"coast_pine","traveler_diorama_pine","coast_flowers","wind_grass","iuchi_brook_reeds"}
ATLAS={"m474_coastal_floor_atlas","m828_coastal_floor_atlas","doji_tidal_footpath_atlas",
       "m475_phoenix_floor","m487_phoenix_floor","m799_phoenix_floor","m846_phoenix_floor"}


def s32(rgba):
    return rgba-2**32 if rgba>=2**31 else rgba


def digest(data):
    return sha256(data).hexdigest()


def js(data):
    return json.dumps(data,ensure_ascii=False,separators=(",",":")).encode("utf8")


def read(path):
    return json.loads(path.read_bytes())


def smooth(lo,hi,x):
    z=np.clip((x-lo)/(hi-lo),0,1)
    return z*z*(3-2*z)


def preset(old, kind):
    v=deepcopy(old)
    v["id"]="rt_coastal_brilliance_"+kind
    title={"road":"Clear Coastal Sun","cave":"Coastal Cave Lanterns","arena":"Clear Cove Sun"}[kind]
    v["name"]={"en":title,"ja":title}
    l=v["envlights"][0]
    if kind=="cave":
        l.update(color=s32(0xFFF0D5FF),scolor=s32(0xFFF0D5FF),power=1230,pitch=59,head=-22)
        v["ibl"].update(ibldiff=360,iblspec=102,iblcolor=s32(0xD6EBFFFF))
        v["fog"].update(density=.006,zoffs=23.5,color=s32(0x28384AB8))
        v["postfx"].update(bloompow=.20,bloomthrs=.70)
    else:
        # High sun and a short path to the beach keep the formation in light.
        l.update(color=s32(0xFFF0D8FF),scolor=s32(0xFFF0D8FF),power=2400 if kind=="arena" else 2240,
                 pitch=67 if kind=="arena" else 58,head=156 if kind=="arena" else -42)
        l["shadow"].update(shadowdens=.59,shadowsoft=.12 if kind=="arena" else .16)
        v["ibl"].update(ibldiff=370,iblspec=170,iblcolor=s32(0xE4F2FFFF),ibldir=0,
                        ibltex="/resource/ibltex/wildflower_field_2k_ibl.ktx")
        v["fog"].update(density=.0027,zoffs=35.0,color=s32(0x84B6E5B3))
        v["postfx"].update(bloompow=.09,bloomthrs=.92)
    return v


def transfer(raw, stem, *, water=None, water_limits=None, pigment=None):
    im=Image.open(io.BytesIO(raw))
    rgba=np.asarray(im.convert("RGBA"),dtype=np.float32)
    data=rgba[:,:,:3]
    lum=data@LUMA
    alpha=rgba[:,:,3]>112
    center=float(np.median(lum[alpha]))
    if water is not None:
        low,high,amount=water
        lo,hi=water_limits
        t=smooth(lo,hi,lum)
        dye=np.array(low)+(np.array(high)-np.array(low))*t[...,None]
        tint=dye+.22*(data-lum[...,None])
        result=data+amount*(tint-data)
    elif pigment is None and stem in ATLAS:
        # Keep the existing sand/grass/path boundaries and dirt microtexture.
        r,g,b=data.transpose(2,0,1)
        green=smooth(9,45,g-r)
        blue=smooth(5,26,b-r)*smooth(10,38,b-g)
        stone=smooth(-21.,-4.,r-g)
        tint=data.copy()
        tint+=(green[...,None]*np.array((-19.,12.,-3.)))
        tint+=(blue[...,None]*np.array((-9.,-5.,9.)))
        dune=(1.-green)*(1.-blue)*(1.-stone)
        tint+=dune[...,None]*np.array((7.,-4.,-8.))
        result=lum[...,None]+1.17*(tint-lum[...,None])
    elif pigment is None and stem in BOTANIC:
        r,g,b=data.transpose(2,0,1)
        greens=smooth(4,22,g-b)*smooth(-6,13,g-r)
        greens*=smooth(21,49,lum)*(1.-smooth(169,228,lum))
        vegetation=data+greens[...,None]*np.array((-34.,21.,-5.))
        result=lum[...,None]+1.12*(vegetation-lum[...,None])
    else:
        color,mix=PAINT[stem] if pigment is None else pigment
        tex=np.array(color)+(lum-center)[...,None]*1.10
        tex+=.19*(data-lum[...,None])
        result=data+mix*(tex-data)
    out=Image.fromarray(np.rint(np.clip(result,0,255)).astype(np.uint8))
    if "A" in im.getbands() or "transparency" in im.info:
        out.putalpha(Image.fromarray(rgba[:,:,3].astype(np.uint8)))
    stream=io.BytesIO()
    out.save(stream,format="PNG")
    return stream.getvalue()


def prepare(repo,bundle,groups):
    engine=repo/"_tools/rpgcobo-tool"
    root=engine/ASSETS
    live=read(root/"index.json")
    story=read(engine/CATALOG)
    settings={d["id"]:d for d in read(engine/RENDER)["rendersets"]}
    base_keys={"road":"rt_hd2d_field","cave":"rt_hd2d_snake_den","arena":"rt_hd2d_battle"}
    profiles={kind:preset(settings[base],kind) for kind,base in base_keys.items()}
    files,hashes,maps,models={}, {}, {}, {}

    def baseline(path):
        value=(root/path).read_bytes()
        hashes[path]=digest(value)
        return value

    def material(path):
        stem=Path(path).stem
        if stem not in PAINT and stem not in BOTANIC and stem not in ATLAS:
            return path
        revised=stem+ALIAS+".png"
        dest="tex/"+revised
        if dest not in files:
            files[dest]=transfer(baseline("tex/"+path),stem)
        return revised

    def node(name,water=None):
        key=(name,water)
        if key in models:
            return models[key]
        desc=baseline(name+".pm").decode("utf8")
        def revise(match):
            tex=match[2]
            if water:
                old,new=water
                result=new+"00.png" if tex==old+"00.png" else tex
            else:
                result=material(tex)
            return match[1]+"tex/"+result+match[3]
        frame=FRAME.sub(revise,desc)
        if frame==desc:
            models[key]=name
            return name
        model=MODEL.search(desc)[1]
        baseline(model)
        alias=name+ALIAS
        files[alias+".pm"]=frame.encode("utf8")
        models[key]=alias
        return alias

    for group in groups:
        for mid,kind in GROUPS[group].items():
            before=live[mid]
            after={**before,"terrain":node(before["terrain"]),"renderPreset":profiles[kind]["id"]}
            after["placements"]=[]
            for item in before["placements"]:
                name=item[0]
                alias=node(name) if name in BOTANIC else name
                reviewed=[alias,*item[1:]]
                # Match the runtime's named fallback sway after an alias rename.
                if alias!=name and len(item)==6 and name in ("wind_grass","coast_flowers"):
                    reviewed.append(.14 if name=="wind_grass" else .09)
                after["placements"].append(reviewed)

            if before.get("water"):
                wet=before.get("waterSequence",{"prefix":"surf","frames":32,"seconds":7.6})
                old=wet["prefix"]
                new,lo,hi,grade=WATER[old]
                first=np.asarray(Image.open(io.BytesIO(baseline(f"tex/{old}00.png"))).convert("RGB"),dtype=np.float32)
                limits=tuple(np.percentile(first@LUMA,[8,94]))
                if limits[1]-limits[0]<10:
                    midtone=np.median(first@LUMA)
                    limits=midtone-9,midtone+9
                for i in range(wet["frames"]):
                    suffix=f"{i:02d}.png"
                    key="tex/"+new+suffix
                    if key not in files:
                        files[key]=transfer(baseline("tex/"+old+suffix),old,water=(lo,hi,grade),water_limits=limits)
                after["water"]=node(before["water"],(old,new))
                after["waterSequence"]={**wet,"prefix":new}
            world=engine/"project/data/mapdata"/f"{mid}.bw"
            maps[mid]={"before":before,"after":after,"story":digest(js(story[mid])),"world":digest(world.read_bytes())}
    for path,content in files.items():
        target=bundle/"files"/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(content)
    used={m["after"]["renderPreset"] for m in maps.values()}
    info={"maps":maps,"source":hashes,"files":{p:digest(d) for p,d in files.items()},
          "presets":[p for p in profiles.values() if p["id"] in used],
          "basePresets":{key:settings[key] for key in base_keys.values()}}
    (bundle/"coastal-proof.json").write_text(json.dumps(info,indent=2)+"\n",encoding="utf8")
    print(f"Prepared {len(maps)} coastal maps, {len(files)} visual resources and {len(used)} scoped render profiles.")


def append_render_presets(raw, presets):
    """Append only new objects while preserving the original JSON bytes."""
    if not presets:
        return raw
    original=raw.decode("utf8")
    newline="\r\n" if "\r\n" in original else "\n"
    match=re.search(r'"rendersets"\s*:\s*',original)
    assert match is not None
    start=match.end()
    items,end=json.JSONDecoder().raw_decode(original,start)
    assert isinstance(items,list) and original[end-1]=="]"
    left=original[:end-1].rstrip()
    right=original[len(left):]
    blocks=[]
    for row in presets:
        block=json.dumps(row,ensure_ascii=False,indent="\t")
        blocks.append(newline.join("\t\t"+line for line in block.splitlines()))
    revised=left+("," if items else "")+newline+(","+newline).join(blocks)+right
    assert json.loads(revised)["rendersets"]==items+presets
    return revised.encode("utf8")


def apply(repo,profile,bundle,publish=False):
    live=repo/"_tools/rpgcobo-tool"
    assert live!=profile
    source,preview=live/ASSETS,profile/ASSETS
    receipt=read(bundle/"coastal-proof.json")
    prior=read(source/"index.json")
    story=read(live/CATALOG)
    live_render=read(live/RENDER)
    stock={r["id"]:r for r in live_render["rendersets"]}
    assert all(stock[k]==v for k,v in receipt["basePresets"].items())
    for key,checksum in receipt.get("projectSource",{}).items():
        assert digest((live/key).read_bytes())==checksum,key
    for key,checksum in receipt["source"].items():
        assert digest((source/key).read_bytes())==checksum,key
    after={}
    review_index=read(preview/"index.json")
    review_story=read(profile/CATALOG)
    for mid,item in receipt["maps"].items():
        assert prior[mid] in (item["before"],item["after"]),mid
        assert digest(js(story[mid]))==item["story"],mid
        bw=Path("project/data/mapdata")/f"{mid}.bw"
        assert digest((live/bw).read_bytes())==item["world"],mid
        if publish:
            assert review_index[mid]==item["after"],mid
            assert digest(js(review_story[mid]))==item["story"],mid
            assert digest((profile/bw).read_bytes())==item["world"],mid
        after[mid]=item["after"]
    engine=live if publish else profile
    root=engine/ASSETS
    additions,updates,baseline={}, {}, {}

    def place(path,data,immutable=False):
        if path.is_file():
            old=path.read_bytes()
            if old==data:
                return
            if immutable:
                raise ValueError(f"Conflicting scoped art {path}")
            baseline[path]=old
            updates[path]=data
        else:
            additions[path]=data

    original_render=(engine/RENDER).read_bytes()
    render=json.loads(original_render)
    by_id={r["id"]:r for r in render["rendersets"]}
    append=[]
    approved={r["id"]:r for r in read(profile/RENDER)["rendersets"]}
    for setting in receipt["presets"]:
        key=setting["id"]
        if publish:
            assert approved[key]==setting,key
        if key in by_id:
            assert by_id[key]==setting,key
        else:
            append.append(setting)
    place(engine/RENDER,append_render_presets(original_render,append))
    for key,checksum in receipt["files"].items():
        payload=(bundle/"files"/key).read_bytes()
        assert digest(payload)==checksum,key
        if publish:
            assert (preview/key).read_bytes()==payload,key
        place(root/key,payload,True)
    for key,checksum in receipt.get("projectFiles",{}).items():
        relative=Path(key)
        assert relative.parent==Path("project/resource/ibltex") and relative.suffix==".ktx",key
        payload=(bundle/"files"/relative).read_bytes()
        assert digest(payload)==checksum,key
        if publish:
            assert (profile/relative).read_bytes()==payload,key
        place(engine/relative,payload,True)
    if not publish:
        for mid in after:
            review_story[mid]=story[mid]
            bw=Path("project/data/mapdata")/f"{mid}.bw"
            place(profile/bw,(live/bw).read_bytes())
        place(profile/CATALOG,js(review_story))
        for key,content in resource_files(source,{m:row["before"] for m,row in receipt["maps"].items()}).items():
            place(preview/key,content)
    index=root/"index.json"
    place(index,js({**read(index),**after}))
    for path in additions:
        path.parent.mkdir(parents=True,exist_ok=True)
    transact(baseline,updates,additions)
    print(f"{'Published' if publish else 'Staged'} {len(after)} coastal rows.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--groups",nargs="+",choices=GROUPS,default=("coast",))
    parser.add_argument("--profile",type=Path)
    a=parser.parse_args()
    repo,bundle=a.repo.resolve(),a.bundle.resolve()
    if a.action=="prepare":
        prepare(repo,bundle,a.groups)
    elif a.profile is None:
        parser.error("--profile is mandatory for stage and publish")
    else:
        apply(repo,a.profile.resolve(),bundle,a.action=="publish")


if __name__=="__main__":
    main()
