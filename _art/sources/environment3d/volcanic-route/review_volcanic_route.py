"""Walk and capture the volcanic candidate in the supervisor's playtest slot."""

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
    "M442": ("switchback-stair", (47.0,19.0,2.0), ((27.60,3.0,9.1),.11,.51,19.4,54.), None),
    "M443": ("crater-shrine", (32.0,19.0,3.5), ((31.62,3.11,11.15),.23,.51,23.5,56.), None),
    "M450": ("shinomen-lava-trees", (80.0,20.0,2.0), ((44.10,2.50,9.25),.18,.43,20.,54.), None),
    "M896": ("switchback-champion-arena", (64.0,64.0,.5), ((32.42,1.70,34.50),.15,.44,20.3,54.), ("M001","153")),
}
LAVA_GLADE_VIEW=("shinomen-lava-glade", (80.0,20.0,2.0), ((44.30,2.58,9.58),.13,.56,16.,52.), None)
BANK_VIEWS={
    "M442": ("switchback-stair", (47.0,19.0,2.0), ((28.3,3.42,9.05),.10,.37,16.,54.), None),
    "M443": ("crater-shrine", (32.0,19.0,3.5), ((32.25,3.19,11.82),.20,.43,20.,55.), None),
    "M896": ("switchback-champion-arena", (64.0,64.0,.5), ((32.10,1.3,33.55),.25,.51,13.7,55.), ("M001","153")),
}
CAPTURE=r"""
local stage=::rpgstage, kit=stage.rtEnvironmentKit;
if(stage.mapid!=@MAP@ || !kit || !kit.water || length(kit.waterTextures)!=32 || !length(kit.magmaSpatter))
    throw Exception("Volcanic terrain, staged lava, or spatter is missing");
if(@MAP@=="M896"){
    if(!stage["battle"] || !stage.battle.enemies.find(@(entry) entry.dataid=="E559"))
        throw Exception("The registered Naga champion did not appear");
    stage.battle.battleui.setVisible(false);
}
if(@DAY@) stage.changeRenderSetting(@LIGHTING@);
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class VolcanicReviewCamera extends RPGCameraMotion {
    function update(dt){}
    function modifyCamera(cw) {
        cw.to(Vector3D(@X@,@Y@,@Z@));
        cw.hpb.x=@HEAD@; cw.hpb.y=@PITCH@; cw.zoom=@ZOOM@; cw.fovy=@LENS@;
    }
}
local cam=VolcanicReviewCamera({});
stage.camwork.addMotion(cam);
local phase=kit.waterFrame;
sleep(1000);
if(kit.waterFrame==phase) throw Exception("The installed lava texture did not advance");
screenshot(renderer,@PATH@);
stage.camwork.cammots.removeValue(cam);
printf("[VOLCANIC] %S 4K phase %d to %d\n",stage.mapid,phase,kit.waterFrame);
"""

STAIR_FLAGS="G1144=2,G1147,G1148,G1149,G1150,G1151"
WALK=r"""
local stage=::rpgstage, p=stage.player3d.pos;
if(stage.mapid!="M442" || !stage.rtEnvironmentKit || p.x<50.5 || p.y<3.38)
    throw Exception("The original switchback grade did not support the party");
printf("[VOLCANIC] Reached the east stair at %.2f %.2f %.2f\n",p.x,p.y,p.z);
"""


def screenshot_function():
    source=(ART/"preview_coast.sk").read_text("utf8")
    start=source.index("function screenshot(")
    return source[start:source.index("\n\nlocal views",start)]


def capture(profile,mid,daylight,output,glade=False,layered=False,banks=False):
    view=LAVA_GLADE_VIEW if glade else BANK_VIEWS[mid] if banks else VIEWS[mid]
    name,(bx,bz,floor),((x,y,z),heading,pitch,zoom,lens),battle=view
    suffix="daylight" if daylight else "story-lighting"
    variant="-cooling-banks" if banks else "-layered-basalt" if layered else ""
    label=f"{'oracle-' if mid!='M450' else ''}{name}{variant}-{suffix}-4k"
    relative=f"tmp/rt_shot/bot_{label}.raw"
    (profile/relative).parent.mkdir(exist_ok=True)
    values={"MAP":json.dumps(mid),"DAY":"true" if daylight else "false",
            "LIGHTING":json.dumps("rt_hd2d_oracle_day" if banks else "rt_hd2d_field"),
            "X":x,"Y":y,"Z":z,"HEAD":heading,"PITCH":pitch,"ZOOM":zoom,"LENS":lens,
            "PATH":json.dumps(relative)}
    camera=CAPTURE
    for key,value in values.items():
        camera=camera.replace(f"@{key}@",str(value))
    native.run(profile,label,mid,"kitsuki",native.spawn(bx,bz,floor),
               "wait,1150|evalf,tmp/castle_native.sk",("[VOLCANIC]", "[ENV] 4K frame"),
               screenshot_function()+"\n"+camera,battle=battle,
               flags=STAIR_FLAGS if mid=="M442" else "",timeout=72 if mid=="M442" else 50)
    raw=profile/relative
    blob=raw.read_bytes()
    dimensions=struct.unpack_from("<II",blob)
    if dimensions!=(3840,2160):
        dimensions=struct.unpack_from(">II",blob)
    assert dimensions==(3840,2160),dimensions
    output.mkdir(parents=True,exist_ok=True)
    path=output/(label+".png")
    Image.frombytes("RGBA",dimensions,blob[8:]).convert("RGB").save(path)
    raw.unlink()
    print(path)


def walk(profile):
    native.run(profile,"oracle-switchback-walk","M442","kitsuki",native.spawn(62,19,2.5),
               "pos|wait,720|goto,102,19,15500|pos|wait,550|evalf,tmp/castle_native.sk",
               ("[VOLCANIC] Reached the east stair",),WALK,flags=STAIR_FLAGS,timeout=72)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("mode",choices=("capture","walk"))
    parser.add_argument("--map",choices=VIEWS)
    parser.add_argument("--daylight",action="store_true")
    parser.add_argument("--glade",action="store_true",help="Closer M450 landmark overview")
    parser.add_argument("--layered-basalt",action="store_true",help="Save the revised volcanic map sample with a distinct filename")
    parser.add_argument("--cooling-banks",action="store_true",help="Review the finished cliff and crossing variant")
    parser.add_argument("--output",type=Path,default=HERE.parent.parent/"outputs")
    args=parser.parse_args()
    native.HERE=HERE
    if args.mode=="walk":
        walk(args.profile.resolve())
    elif args.map is None:
        parser.error("--map is required for capture")
    elif args.glade and args.map!="M450":
        parser.error("--glade is only available for M450")
    elif args.layered_basalt and args.map=="M450":
        parser.error("--layered-basalt applies to M442, M443, and M896")
    elif args.cooling_banks and args.map not in BANK_VIEWS:
        parser.error("--cooling-banks applies to M442, M443, and M896")
    else:
        capture(args.profile.resolve(),args.map,args.daylight,args.output.resolve(),args.glade,
                args.layered_basalt,args.cooling_banks)
