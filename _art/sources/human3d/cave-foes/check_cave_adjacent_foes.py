"""Exercise the remaining humanoid routes with their actual enemy aliases."""
from pathlib import Path
import json,sys

from preview_clan_castles import run,spawn

DIR=Path(__file__).resolve().parent.parent/"human-foes/cave-stage"
sys.path.insert(0,str(DIR))
from install_cave_foes import FITS, HUMAN, PRIORITY, expect_skin

BASE=r"""
local stage=::rpgstage, battle=stage["battle"];
if(!battle){
    ::RPGMain.enterBattle({mapid="M819",escape=true,enemies=@ENEMIES@});
    return;
}
local fits=@FITS@;
local checked=0;
foreach(enemy in battle.enemies) {
    local actor=battle.getChara3D(enemy), model=enemy.data.mdlid;
    local fit=fits[model];
    if(!fit || actor["nativeKey"]!=model || actor.nativeBodyTemplate!=fit[5]
        || !actor.nativeBody || length(actor.nativeBody.bones)!=50 || !actor.nativeBody.motion)
        throw Exception("Incorrect shared rig on cave foe " .. model);
    if (!actor.nativeFace || actor.nativeFace.mesh.res.name!=fit[0]
         || !actor.nativeFace.mesh.face[0].m.tex0 || !actor.nativeOutfit
         || actor.nativeTailoring!=fit[1] || Math.abs(actor.travelerWidth-fit[2])>.0001)
        throw Exception("Incorrect textured face or outfit on cave foe " .. model);
    if(!actor.nativeWeapon || actor.nativeWeapon.mesh.res.name!=fit[3])
        throw Exception("Incorrect cave-foe weapon fit on " .. model);
    foreach(part in ["neck","throat","hands","core"]){
        local cut=actor.nativeBody.mesh.face.find(@(item) item.m.name=="c807060_"..part);
        if(!cut || cut.m.basecol!=fit[4]) throw Exception("Skin mismatch on " .. model);
    }
    if(!actor.anime2(#{id="slash1"})) throw Exception("Missing native attack on " .. model);
    actor.anime2(#{id="fight"});
    printf("[CAVE FOE COVERAGE] %S %S verified\n",enemy.dataid,model);
    ++checked;
}
if (checked!=@COUNT@) throw Exception("Expected cave foe coverage count did not match");
"""

ROUTES=("M470","M471","M472","M480","M481","M482","M483","M484")


def main(profile):
    runtime=profile/"project/data"
    map_data=json.loads((runtime/"map.json").read_bytes())
    enemy_data=json.loads((runtime/"enemy.json").read_bytes())
    humans=json.loads((profile/HUMAN/"index.json").read_bytes())
    by_actor={}
    for mid in ROUTES:
        for group in map_data[mid].get("encount",[]) or []:
            for member in group["enemies"]:
                eid=member["id"]
                by_actor.setdefault(enemy_data[eid]["mdlid"],eid)
    remainder=[key for key in FITS if key not in PRIORITY]
    offsets=((1.51,-.65),(.62,.45),(-.43,-.34),(-1.13,.83))
    for n in range(0,len(remainder),4):
        members=remainder[n:n+4]
        rows,entries=[],[]
        for key,(x,z) in zip(members,offsets):
            eid=by_actor[key]
            fit=FITS[key]
            color=expect_skin((profile/HUMAN/f"{key}.pm").read_text("utf8"),key)
            row=[humans[key]["face"]+".pm",fit.outfit,fit.width,fit.weapon+".pm",color]
            data="["+ ",".join(json.dumps(field) for field in row[:-1])+","+color+","+json.dumps(humans[key]["base"])+"]"
            entries.append(key+"="+data)
            rows.append('{id="'+eid+'",x='+str(x)+',z='+str(z)+'}')
        code=BASE.replace("@ENEMIES@","["+",".join(rows)+"]")
        code=code.replace("@FITS@","{"+",".join(entries)+"}").replace("@COUNT@",str(len(rows)))
        run(profile,f"cave-adjacent-model-fits-{n//4+1}","M484","kitsuki",spawn(68,16,1.5),
            "wait,750|evalf,tmp/castle_native.sk|untilmap,M819,14500|wait,1350|evalf,tmp/castle_native.sk",
            tuple(f"{by_actor[key]} {key} verified" for key in members),code,timeout=43)

if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
