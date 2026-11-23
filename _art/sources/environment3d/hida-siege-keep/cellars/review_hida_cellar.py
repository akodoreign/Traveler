"""Supervisor-only M153 4K samples and native transition fixtures."""

import argparse
import json
from pathlib import Path
import struct
import sys

from PIL import Image

HERE=Path(__file__).resolve().parent
ART=HERE.parent.parent/"coast-kit"
sys.path.insert(0,str(ART))
import preview_clan_castles as native

VIEWS={
    "entry": ((34.,18.,1.5),((18.8,2.52,9.72),.42,.45,11.4,52.),"G271",False),
    "checkpoint": ((66.,27.,1.5),((32.2,2.57,14.03),.13,.55,14.6,54.),"G271,G274",False),
    "checkpoint-relocated": ((69.,24.,1.5),((33.70,2.34,12.39),.41,.48,9.1,52.),"G271,G274,G275",True),
    "storeroom": ((79.,18.,1.5),((39.67,2.26,9.32),.18,.51,12.7,53.),"G271,G274,G275",True),
    "exit-open": ((79.,18.,1.5),((44.60,2.43,9.51),.65,.44,10.6,50.),"G271,G274,G275",True),
    "exit-locked": ((34.,18.,1.5),((44.60,2.43,9.51),.65,.44,10.6,50.),"G271,G274",False),
}
ROUTES={
    "entry":("M541",(96,16,2.0),(96,13),"M153","G1644,G271,G273"),
    "exit":("M153",(89,18,1.5),(92,18),"M501","G271,G274,G275"),
}
CAPTURE=r"""
local stage=::rpgstage, kit=stage.rtEnvironmentKit;
if(stage.mapid!="M153" || !kit || length(kit.townDoors)!=1 || !length(kit.poolLighting))
    throw Exception("The M153 cellar or door did not load");
local expected=@OPEN@ ? 52.0*Math.DTOR : 0.0;
if(Math.abs(kit.townDoors[0][2]-expected)>.05)
    throw Exception("The servants' door disagrees with its original story flag");
if(@DAY@) stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class HidaCellarCamera extends RPGCameraMotion {
    function update(dt){}
    function modifyCamera(cw){
        cw.to(Vector3D(@X@,@Y@,@Z@));
        cw.hpb.x=@HEAD@; cw.hpb.y=@PITCH@; cw.zoom=@ZOOM@; cw.fovy=@LENS@;
    }
}
local cam=HidaCellarCamera({});
stage.camwork.addMotion(cam);
sleep(720);
screenshot(renderer,@PATH@);
stage.camwork.cammots.removeValue(cam);
printf("[HIDA-CELLAR] 4K and door angle %.2f\n",kit.townDoors[0][2]);
"""


def capture(profile,view,out,daylight):
    spawn,cam,flags,open_=VIEWS[view]
    (x,y,z),heading,pitch,zoom,lens=cam
    label=f"hida-siege-cellar-{view}-{'daylight' if daylight else 'story-light'}-4k"
    relative=f"tmp/rt_shot/bot_{label}.raw"
    (profile/relative).parent.mkdir(exist_ok=True)
    source=(ART/"preview_coast.sk").read_text("utf8")
    start=source.index("function screenshot(")
    script=source[start:source.index("\n\nlocal views",start)]+"\n"+CAPTURE
    fields={"OPEN":"true" if open_ else "false","DAY":"true" if daylight else "false",
            "X":x,"Y":y,"Z":z,"HEAD":heading,"PITCH":pitch,"ZOOM":zoom,"LENS":lens,
            "PATH":json.dumps(relative)}
    for key,value in fields.items():
        script=script.replace(f"@{key}@",str(value))
    native.run(profile,label,"M153","hida-cellar",native.spawn(*spawn),
               "wait,1200|evalf,tmp/castle_native.sk",("[HIDA-CELLAR] 4K", "[ENV] 4K frame"),
               script,flags=flags,timeout=80)
    raw=profile/relative
    payload=raw.read_bytes()
    size=struct.unpack_from("<II",payload)
    if size!=(3840,2160):
        size=struct.unpack_from(">II",payload)
    assert size==(3840,2160),size
    out.mkdir(parents=True,exist_ok=True)
    png=out/(label+".png")
    Image.frombytes("RGBA",size,payload[8:]).convert("RGB").save(png)
    raw.unlink()
    print(png)


def traverse(profile,leg):
    mid,spawn,(x,z),dest,flags=ROUTES[leg]
    steps=f"pos|wait,700|goto,{x},{z},12000|untilmap,{dest},11000|pos"
    native.run(profile,f"hida-siege-cellar-{leg}-transition",mid,"hida-cellar",native.spawn(*spawn),
               steps,(f"BOT reached {dest}",),flags=flags,timeout=75)


def check_checkpoint(profile):
    script=r"""
local stage=::rpgstage;
local save=stage.getEvent(12);
if(stage.mapid!="M153" || !save || !stage.searchdst || stage.searchdst["event"]!=save)
    throw Exception("The original checkpoint is out of interaction reach");
printf("[HIDA-CELLAR] Original save event is within reach\n");
"""
    steps=("pos|goto,67,25,5500|goto,69,25,7000|goto,69,24,5300|face,68,24|wait,590|"
           "evalf,tmp/castle_native.sk|answer,1|tap,z|wait,700|pos")
    native.run(profile,"hida-siege-cellar-save-checkpoint","M153","hida-cellar",
               native.spawn(67,26,1.5),steps,("[HIDA-CELLAR] Original save event is within reach",
               "A small stone shrine to the Fortunes"),script,flags="G271,G274,G275",timeout=80)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("action",choices=("capture","traverse","checkpoint"))
    parser.add_argument("--view",choices=VIEWS,default="storeroom")
    parser.add_argument("--leg",choices=ROUTES,default="entry")
    parser.add_argument("--story-light",action="store_true")
    parser.add_argument("--output",type=Path,default=HERE.parent.parent.parent/"outputs")
    args=parser.parse_args()
    native.HERE=HERE
    native.LEADS["hida-cellar"]="P100"
    if args.action=="capture":
        capture(args.profile.resolve(),args.view,args.output.resolve(),not args.story_light)
    elif args.action=="checkpoint":
        check_checkpoint(args.profile.resolve())
    else:
        traverse(args.profile.resolve(),args.leg)
