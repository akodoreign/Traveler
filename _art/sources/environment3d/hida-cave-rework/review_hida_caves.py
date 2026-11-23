"""Supervisor-only 4K views and isolated walking checks for the Hida caves."""

import argparse
import json
from pathlib import Path
import struct
import sys

from PIL import Image

HERE=Path(__file__).resolve().parent
ART=HERE.parent/"coast-kit"
sys.path.insert(0,str(ART))
import preview_clan_castles as native

VIEWS={
    "M148": ("donjon-cells",(61.,21.,1.5),((30.9,2.63,11.77),.20,.48,13.8,53.),"G224",None),
    "M149": ("trap-catacombs",(61.,18.,1.5),((32.1,2.33,9.91),.17,.57,15.4,53.),"G225,G226",None),
    "M150": ("deepest-cell",(56.,20.,1.5),((28.24,2.54,12.54),.24,.49,14.5,54.),"G227",None),
    "M815": ("donjon-troll-arena",(64.,64.,.5),((32.41,1.75,34.73),.19,.45,18.5,54.),"",("M001","14")),
    "M157": ("deep-trap-tunnel",(61.,22.,1.5),((31.92,2.44,11.1),.16,.51,15.3,53.),"G280",None),
    "M158": ("wall-tunnel-mouth",(56.,12.,8.5),((28.1,9.55,7.8),.24,.37,15.4,51.),"G284",None),
    "M170": ("kaiu-trap-tunnel",(44.,19.,1.5),((27.35,2.21,10.01),.27,.51,16.2,53.),"G260,G241",None),
}
PORTALS=(
    ("cells-down","M148",(61,47,1.5),(61,54),"M149","G224,G213,G225,G226"),
    ("catacombs-up","M149",(61,7,1.5),(61,2),"M148","G224,G213,G225,G226"),
    ("catacombs-down","M149",(61,46,1.5),(61,54),"M150","G225,G226,G227"),
    ("deepest-return","M150",(56,7,1.5),(56,2),"M149","G225,G226,G227"),
)
SCRIPTED=(
    ("flare-to-wall","M157",(61,7,1.5),(61,10),"M158","G279,G284",""),
    ("kaiu-return","M170",(9,19,1.5),(1,19),"M101","G260,G241",""),
    ("kaiu-shadowlands","M170",(110,19,1.5),(113,19),"M171","G260,G241","answer,0|"),
)
THRESHOLD={
    "M148": ("donjon-entry",(61.,8.,1.5),((30.7,2.45,3.33),.15,.35,9.6,51.),"G224",None),
    "M149": ("catacombs-south-bore",(61.,46.,1.5),((30.68,2.48,23.94),.12,.32,9.6,51.),"G225,G226",None),
    "M150": ("deepest-cell-threshold",(56.,10.,1.5),((28.15,2.54,6.25),.19,.35,9.9,52.),"G227",None),
}
WALL_RELIEF_VIEW=("wall-tunnel-mouth",(56.,12.,8.5),((28.4,9.46,6.35),.18,.43,15.8,52.),"G284",None)
CAPTURE=r"""
local stage=::rpgstage, kit=stage.rtEnvironmentKit;
if(stage.mapid!=@MAP@ || !kit || !length(kit.poolLighting))
    throw Exception("The installed Hida environment did not load");
if(@BATTLE@){
    if(!stage["battle"] || !stage.battle.enemies.find(@(e) e && e.dataid=="E235"))
        throw Exception("The registered puppet-troll encounter did not load");
    stage.battle.battleui.setVisible(false);
}
if(@DAY@) stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class HidaReviewCamera extends RPGCameraMotion {
    function update(dt){}
    function modifyCamera(cw){
        cw.to(Vector3D(@X@,@Y@,@Z@));
        cw.hpb.x=@HEAD@; cw.hpb.y=@PITCH@; cw.zoom=@ZOOM@; cw.fovy=@LENS@;
    }
}
local cam=HidaReviewCamera({});
stage.camwork.addMotion(cam);
sleep(750);
screenshot(renderer,@PATH@);
stage.camwork.cammots.removeValue(cam);
printf("[HIDA-CAVES] 4K %S\n",stage.mapid);
"""


def screenshot_function():
    source=(ART/"preview_coast.sk").read_text("utf8")
    start=source.index("function screenshot(")
    return source[start:source.index("\n\nlocal views",start)]


def capture(profile,mid,output,daylight,threshold,relief=False):
    fixture=WALL_RELIEF_VIEW if relief and mid=="M158" else (THRESHOLD if threshold else VIEWS)[mid]
    name,spawn,view,flags,battle=fixture
    (x,y,z),heading,pitch,zoom,lens=view
    version="-stone-relief" if relief else ""
    label=f"hida-{name}{version}-{'daylight' if daylight else 'story-light'}-4k"
    relative=f"tmp/rt_shot/bot_{label}.raw"
    (profile/relative).parent.mkdir(exist_ok=True)
    values={"MAP":json.dumps(mid),"BATTLE":"true" if battle else "false",
            "DAY":"true" if daylight else "false","X":x,"Y":y,"Z":z,
            "HEAD":heading,"PITCH":pitch,"ZOOM":zoom,"LENS":lens,"PATH":json.dumps(relative)}
    script=CAPTURE
    for name,value in values.items():
        script=script.replace(f"@{name}@",str(value))
    native.run(profile,label,mid,"hida-caves",native.spawn(*spawn),
               "wait,1000|evalf,tmp/castle_native.sk",("[HIDA-CAVES] 4K", "[ENV] 4K frame"),
               screenshot_function()+"\n"+script,flags=flags,battle=battle,timeout=80)
    path=profile/relative
    payload=path.read_bytes()
    size=struct.unpack_from("<II",payload)
    if size!=(3840,2160):
        size=struct.unpack_from(">II",payload)
    assert size==(3840,2160),size
    output.mkdir(parents=True,exist_ok=True)
    target=output/(label+".png")
    Image.frombytes("RGBA",size,payload[8:]).convert("RGB").save(target)
    path.unlink()
    print(target)


def portals(profile,selected):
    routes=tuple((*route,"") for route in PORTALS)
    if selected:
        routes+=SCRIPTED
    for name,mid,spawn,goal,dest,flags,prefix in routes:
        if selected and name!=selected:
            continue
        x,z=goal
        steps=f"{prefix}pos|wait,650|goto,{x},{z},13000|untilmap,{dest},12500|pos"
        native.run(profile,f"hida-{name}",mid,"hida-caves",native.spawn(*spawn),steps,
                   (f"BOT reached {dest}",),flags=flags,timeout=75)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("mode",choices=("capture","portals"))
    parser.add_argument("--map",choices=VIEWS)
    parser.add_argument("--leg",choices=tuple(p[0] for p in (*PORTALS,*SCRIPTED)))
    parser.add_argument("--story-light",action="store_true")
    parser.add_argument("--threshold",action="store_true",help="Close view of the M148–M150 passage")
    parser.add_argument("--relief",action="store_true",help="Save the stone revision under its own filename")
    parser.add_argument("--output",type=Path,default=HERE.parent.parent/"outputs")
    args=parser.parse_args()
    native.HERE=HERE
    native.LEADS["hida-caves"]="P100"
    if args.mode=="portals":
        portals(args.profile.resolve(),args.leg)
    elif args.map is None:
        parser.error("--map is required for capture")
    elif args.threshold and args.map not in THRESHOLD:
        parser.error("--threshold is available on M148, M149, and M150")
    else:
        capture(args.profile.resolve(),args.map,args.output.resolve(),not args.story_light,args.threshold,args.relief)
