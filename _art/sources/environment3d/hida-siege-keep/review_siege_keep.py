"""Native daylight review and transition fixtures for the Hida siege."""
import argparse
import json
import math
from pathlib import Path
import struct
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "coast-kit"))
import preview_clan_castles as native

# A direct testplay launch seeds flags after the siege wrapper first runs.
FLAGS = "G271,G272,G273,G274,G275,G1644"
VIEWS = {
    "service-hall": ("M501",(56,32,5.),(25.8,6.20,16.1,.21,.52,14.7,55.),"",None),
    "guest-wing": ("M502",(46,34,5.),(23.6,6.15,18.5,.25,.53,16.1,55.),"G276,G277",None),
    "archives": ("M503",(70,31,5.),(32.8,6.15,18.3,.21,.50,16.3,55.),"G276,G277,G278",None),
    "stairs-locked": ("M502",(91,43,5.),(45.55,6.0,25.16,.25,.39,8.9,53.),"G276,G277",None),
    "stairs-open": ("M502",(91,43,5.),(45.55,6.0,25.16,.25,.39,8.9,53.),"G276,G277,G278",None),
    "arena": ("M816",(64,64,.5),(32.15,1.45,35.42,.22,.42,19.8,56.),"",("M001","15")),
}
ROUTES = (
    ("service-locked","M501",(91,44,5.),(91,49),None,""),
    ("guest-locked-one","M502",(91,44,5.),(91,49),None,"G276,G277"),
    ("service-up","M501",(91,44,5.),(91,59),"M502","G276"),
    ("guest-down","M502",(13,19,5.),(13,9),"M501","G276"),
    ("guest-up","M502",(91,44,5.),(91,59),"M503","G276,G277,G278"),
    ("archives-down","M503",(13,19,5.),(13,9),"M502","G276,G277,G278"),
    ("archives-up","M503",(91,44,5.),(91,59),"M504","G276,G277,G278"),
)

CAPTURE = r"""
local stage=::rpgstage, kit=stage.rtEnvironmentKit;
if(stage.mapid!=@MAP@ || !kit || length(kit.townDoors)!=@DOORS@ || !length(kit.poolLighting))
    throw Exception("The requested Hida siege environment did not load");
if(@DOORS@ && Math.abs(kit.townDoors[0][2]-@ANGLE@)>.06)
    throw Exception("The siege door is out of sync with the floor's story state");
if(@ARENA@){
    if(!stage["battle"] || !stage.battle.enemies.find(@(foe) foe.dataid=="E236"))
        throw Exception("The original Noboru duel did not load");
    stage.battle.battleui.setVisible(false);
}
if(@DAYLIGHT@) stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class SiegeKeepCamera extends RPGCameraMotion {
    function update(dt){}
    function modifyCamera(cw){
        cw.to(Vector3D(@X@,@Y@,@Z@));
        cw.hpb.x=@HEADING@; cw.hpb.y=@PITCH@; cw.zoom=@ZOOM@; cw.fovy=@LENS@;
    }
}
local cam=SiegeKeepCamera({});
stage.camwork.addMotion(cam);
sleep(650);
screenshot(renderer,@FILE@);
stage.camwork.cammots.removeValue(cam);
printf("[HIDA-SIEGE] Native 4K %S\n",stage.mapid);
"""

LOCK_PROOF = r"""
local stage=::rpgstage, kit=stage.rtEnvironmentKit;
if(stage.mapid!=@MAP@ || !kit || length(kit.townDoors)!=1 ||
    Math.abs(kit.townDoors[0][2])>.05 || stage.player3d.pos.z>25.2)
    throw Exception("The closed stair was passed before its floor was cleared");
printf("[HIDA-SIEGE] Original stair lock held on %S\n",stage.mapid);
"""


def flags(extra):
    return FLAGS + ("," + extra if extra else "")


def capture(profile, view, daylight, output):
    mid, origin, camera, extra, encounter = VIEWS[view]
    x,y,z,heading,pitch,zoom,lens = camera
    label = "hida-siege-" + view + ("-daylight" if daylight else "-story-light") + "-4k"
    relative = f"tmp/rt_shot/bot_{label}.raw"
    (profile / relative).parent.mkdir(exist_ok=True)
    options = {
        "MAP":json.dumps(mid), "DOORS":0 if encounter else 1,
        "ANGLE":math.radians(79.) if view in ("stairs-open","archives") else 0.,
        "DAYLIGHT":"true" if daylight else "false", "ARENA":"true" if encounter else "false",
        "X":x, "Y":y, "Z":z, "HEADING":heading, "PITCH":pitch, "ZOOM":zoom, "LENS":lens,
        "FILE":json.dumps(relative),
    }
    script = CAPTURE
    for key,value in options.items():
        script=script.replace(f"@{key}@",str(value))
    source=(HERE.parent/"coast-kit/preview_coast.sk").read_text("utf8")
    screenshot=source[source.index("function screenshot("):source.index("\n\nlocal views")]
    native.run(profile,label,mid,"hida-siege",native.spawn(*origin),
               "wait,1320|evalf,tmp/castle_native.sk",("[HIDA-SIEGE] Native 4K","[ENV] 4K frame"),
               screenshot+"\n"+script,flags=flags(extra),battle=encounter,timeout=72)
    raw=profile/relative
    data=raw.read_bytes()
    assert struct.unpack_from("<II",data)==(3840,2160)
    output.mkdir(parents=True,exist_ok=True)
    target=output/(label+".png")
    Image.frombytes("RGBA",(3840,2160),data[8:]).convert("RGB").save(target)
    raw.unlink()
    print(target)


def routes(profile, only=None):
    for name,mid,origin,(x,z),dest,extra in ROUTES:
        if only and only!=name:
            continue
        steps=f"wait,700|goto,{x},{z},9500"
        if dest:
            steps+=f"|untilmap,{dest},10500|pos"
            test=(f"BOT reached {dest}",)
            proof=""
        else:
            steps+="|wait,1600|evalf,tmp/castle_native.sk"
            test=("[HIDA-SIEGE] Original stair lock held",)
            proof=LOCK_PROOF.replace("@MAP@",json.dumps(mid))
        native.run(profile,"hida-siege-"+name,mid,"hida-siege",native.spawn(*origin),steps,test,
                   proof,flags=flags(extra),timeout=65)


def compatibility(profile):
    for mid,target in zip(("M154","M155","M156"),("M501","M502","M503"),strict=True):
        native.run(profile,"hida-siege-save-"+mid.lower(),mid,"hida-siege",native.spawn(30,24,2.),
                   f"wait,750|untilmap,{target},10000|pos",(f"BOT reached {target}",),
                   flags=flags("G276,G277,G278"),timeout=62)
    proof = r"""
if(::rpgvar["G1644"] || length(::rpgstage.rtEnvironmentKit.townDoors))
    throw Exception("Ordinary keep chose siege art");
printf("[HIDA-SIEGE] Normal keep selected its regular art\n");
"""
    native.run(profile,"hida-siege-day-state","M501","hida-siege",native.spawn(52,27,5.),
               "wait,1300|evalf,tmp/castle_native.sk",("[HIDA-SIEGE] Normal keep selected its regular art",),proof,timeout=55)


def chase(profile):
    native.run(profile,"hida-siege-unmask-to-deep-tunnel","M503","hida-siege",native.spawn(70,31,5.),
               "wait,650|answer,3|talkto,70,37|untilmap,M157,16000|vars,G279",
               ("BOT reached M157","BOT var G279 = true"),flags=flags("G276,G277,G278,G290,G280"),timeout=71)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("mode",choices=("capture","routes","compatibility","chase"))
    parser.add_argument("--view",choices=VIEWS,default="service-hall")
    parser.add_argument("--leg",choices=tuple(row[0] for row in ROUTES))
    parser.add_argument("--story-light",action="store_true")
    parser.add_argument("--output",type=Path,default=HERE.parent.parent/"outputs")
    args=parser.parse_args()
    native.HERE=HERE
    native.LEADS["hida-siege"]="P100"
    if args.mode=="capture":
        capture(args.profile.resolve(),args.view,not args.story_light,args.output)
    elif args.mode=="routes":
        routes(args.profile.resolve(),args.leg)
    elif args.mode=="chase":
        chase(args.profile.resolve())
    else:
        compatibility(args.profile.resolve())
