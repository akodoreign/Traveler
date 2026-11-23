"""Refine the reviewed coast lighting, backdrop and tide-cave floor."""
import argparse
from copy import deepcopy
import io
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image

from coastal_daylight import apply, digest, read, s32, smooth


BASE_SKY=Path("project/resource/ibltex/wildflower_field_2k_ibl.ktx")
COAST_SKY=Path("project/resource/ibltex/traveler_clear_coast_ibl.ktx")
LUMA=np.array((.213,.715,.072),dtype=np.float32)


def rgb9e5(rgb):
    color=np.clip(rgb,0,65000.)
    channel_peak=color.max(axis=-1)
    exp=np.clip(np.floor(np.log2(np.maximum(channel_peak,1e-7)))+16,0,31).astype(np.int32)
    values=np.rint(color*np.exp2(24-exp)[...,None])
    exp+=values.max(axis=-1)>=512
    xy=np.rint(color*np.exp2(24-exp)[...,None]).clip(0,511).astype(np.uint32)
    return (xy[:,:,0] | (xy[:,:,1]<<9) | (xy[:,:,2]<<18) | (exp.astype(np.uint32)<<27)).astype("<u4")


def sphere(side,face):
    unit=(2.*(np.arange(side,dtype=np.float32)+.5)/side)-1.
    u,v=np.meshgrid(unit,unit)
    one=np.ones_like(u)
    orient=((one,-v,-u),(-one,-v,u),(u,one,v),(u,-one,-v),(u,-v,one),(-u,-v,-one))
    xyz=np.stack(orient[face],axis=-1)
    return xyz/np.linalg.norm(xyz,axis=-1,keepdims=True)


def sky_face(side,face,level,preset="clear"):
    x,y,z=sphere(side,face).transpose(2,0,1)
    horizon=np.array((.46,.74,1.12))
    nadir=np.array((.155,.32,.57))
    zenith=np.array((.087,.342,.77))
    below=smooth(-1.,-.02,y)
    above=smooth(.0,.92,y)
    scene=nadir+(horizon-nadir)*below[...,None]
    scene+=(zenith-horizon)*above[...,None]
    # Bands of soft white haze vary in direction without introducing a near
    # horizon from an unrelated panorama into the high-pitch gameplay shot.
    bands=.55+.24*np.sin(14*x+5*z+2*y)
    bands+=.16*np.sin(26*z-7*x+5*y)+.05*np.cos(38*x+31*z)
    haze=smooth(.58,.95,bands)*np.exp(-((y-.13)/.24)**2)*(.22/(1.+.25*level))
    scene+=(np.array((1.02,1.13,1.19))-scene)*haze[...,None]
    return rgb9e5(scene)


def daylight_ktx(base):
    """Use the engine-tested cube format and blue-skylight diffuse SH data."""
    signature=b"\xabKTX 11\xbb\r\n\x1a\n"
    assert base.startswith(signature)
    fields=struct.unpack_from("<13I",base,12)
    endianness,packing,_,_,_,_,width,height,_,_,faces,mips,metadata=fields
    assert endianness==0x04030201 and packing==0x8C3E and faces==6 and width==height
    # Stock SH metadata retains the existing cool sky diffuse illumination
    # separately from our framings' cleaner visual/background hemisphere.
    out=bytearray(base[:64+metadata])
    for level in range(mips):
        dim=max(1,width>>level)
        out.extend(struct.pack("<I",dim*dim*4))
        for face in range(faces):
            out.extend(sky_face(dim,face,level).tobytes())
    assert len(out)==len(base)
    return bytes(out)


def dry_stone(source):
    im=Image.open(io.BytesIO(source)).convert("RGB")
    data=np.asarray(im,dtype=np.float32)
    r,g,b=data.transpose(2,0,1)
    luma=data@LUMA
    stone=smooth(7,32,g-r)*smooth(7,26,b-r)
    center=np.median(luma[stone>.85])
    gray=np.array((43,54,68)) + (luma-center)[...,None]*.92
    out=data+(.92*stone)[...,None]*(gray-data)
    buffer=io.BytesIO()
    Image.fromarray(np.rint(np.clip(out,0,255)).astype(np.uint8)).save(buffer,format="PNG")
    return buffer.getvalue()


def revise(repo,old,dest):
    proof=deepcopy(read(old/"coastal-proof.json"))
    files={key:(old/"files"/key).read_bytes() for key in proof["files"]}
    live=repo/"_tools/rpgcobo-tool"
    ids={}
    for setting in proof["presets"]:
        old_id=setting["id"]
        if old_id.endswith(("_road","_arena")):
            setting["id"]=old_id+"_horizon"
            setting["ibl"]["ibltex"]="/resource/ibltex/"+COAST_SKY.name
            if old_id.endswith("_arena"):
                key=setting["envlights"][0]
                key.update(head=-25,pitch=64,power=2190,color=s32(0xFFF0DFFF),scolor=s32(0xFFF0DFFF))
                setting["ibl"].update(ibldiff=540,iblspec=155,iblcolor=s32(0xE8F3FFFF))
        ids[old_id]=setting["id"]
    for row in proof["maps"].values():
        row["after"]["renderPreset"]=ids[row["after"]["renderPreset"]]

    if "M486" in proof["maps"]:
        row=proof["maps"]["M486"]["after"]
        old_key=row["terrain"]
        new_key=old_key+"_dry_floor"
        old_atlas="doji_tidal_footpath_atlas_coastal_daylight.png"
        new_atlas="doji_tidal_footpath_atlas_coastal_daylight_dry_floor.png"
        files["tex/"+new_atlas]=dry_stone(files.pop("tex/"+old_atlas))
        descriptor=files.pop(old_key+".pm")
        assert descriptor.count(old_atlas.encode())==1
        files[new_key+".pm"]=descriptor.replace(old_atlas.encode(),new_atlas.encode())
        row["terrain"]=new_key

    source=(live/BASE_SKY).read_bytes()
    packed=daylight_ktx(source)
    proof["projectSource"]={BASE_SKY.as_posix():digest(source)}
    proof["projectFiles"]={COAST_SKY.as_posix():digest(packed)}
    proof["files"]={key:digest(data) for key,data in files.items()}
    files[COAST_SKY.as_posix()]=packed
    for key,data in files.items():
        path=dest/"files"/key
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    (dest/"coastal-proof.json").write_text(json.dumps(proof,indent=2)+"\n",encoding="utf8")
    print("Revised the scoped backdrop and arena light.")
    

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=("prepare","stage","publish"))
    p.add_argument("repo",type=Path)
    p.add_argument("bundle",type=Path)
    p.add_argument("--prior",type=Path)
    p.add_argument("--profile",type=Path)
    a=p.parse_args()
    if a.action=="prepare":
        if a.prior is None:p.error("--prior is required to revise the first bundle")
        revise(a.repo.resolve(),a.prior.resolve(),a.bundle.resolve())
    else:
        if a.profile is None:p.error("--profile is required for stage or publish")
        apply(a.repo.resolve(),a.profile.resolve(),a.bundle.resolve(),a.action=="publish")


if __name__=="__main__":
    main()
