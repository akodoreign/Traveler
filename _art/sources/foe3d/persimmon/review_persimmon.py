"""Capture the stable and verify Persimmon's three existing field appearances."""
import argparse
import json
from pathlib import Path
import struct
import sys

from PIL import Image

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"coast-kit"))
import preview_clan_castles as native
from install_persimmon import VIEWS

CHECK=r"""
local stage=::rpgstage, runner=stage.getEvent(@EVENT@);
local pony=runner ? runner["rp3d"] : null;
if(!pony || pony["nativeKey"]!="EP172" || !pony.creatureReady ||
    !pony.nativeBody.motion || length(pony.nativeBody.bones)!=10 ||
    !pony.nativeBody.findBone("neck") || !pony.nativeBody.findBone("front_leg1") ||
    pony.event!=runner || !pony.nativeBody.mesh.face[0].m.tex0)
    throw Exception("Persimmon did not receive the textured native rig and original event");
printf("[PERSIMMON] Original %S event %d uses the ten-joint pony\n",stage.mapid,@EVENT@);
"""
CAM=r"""
local stage=::rpgstage;
stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class PersimmonCamera extends RPGCameraMotion {
    function update(dt){}
    function modifyCamera(cw){
        cw.to(Vector3D(29.65,2.89,12.36));
        cw.hpb.x=.18; cw.hpb.y=.25; cw.zoom=7.77; cw.fovy=47.;
    }
}
local cam=PersimmonCamera({});
stage.camwork.addMotion(cam);
sleep(700);
screenshot(renderer,@PATH@);
stage.camwork.cammots.removeValue(cam);
"""


def capture(profile, preview=False):
    output=native.OUTPUTS
    label="persimmon-stable-"+("before" if preview else "daylight")+"-4k"
    relative=f"tmp/rt_shot/bot_{label}.raw"
    (profile/relative).parent.mkdir(exist_ok=True)
    code=(HERE.parent/"coast-kit/preview_coast.sk").read_text("utf8")
    script=code[code.index("function screenshot("):code.index("\n\nlocal views")]
    if not preview:
        script+="\n"+CHECK.replace("@EVENT@","5")
    script+="\n"+CAM.replace("@PATH@",json.dumps(relative))
    steps="wait,1400|evalf,tmp/castle_native.sk"
    markers=("[ENV] 4K frame",)
    if not preview:
        steps+="|talkto,61,23|wait,800"
        markers+=("[PERSIMMON] Original M387 event 5","Persimmon glares at you.")
    native.run(profile,label,"M387","kitsuki",native.spawn(57,20,2.),steps,markers,script,timeout=68)
    file=profile/relative
    blob=file.read_bytes()
    assert struct.unpack_from("<II",blob)==(3840,2160)
    Image.frombytes("RGBA",(3840,2160),blob[8:]).convert("RGB").save(output/(label+".png"))
    file.unlink()


def aliases(profile):
    for mid,origin,flags in (("M408",(118,19,2.),"G997,G998,G999"),
                             ("M413",(41,17,2.),"G1029,G1031")):
        num=VIEWS[mid]
        native.run(profile,"persimmon-"+mid.lower(),mid,"kitsuki",native.spawn(*origin),
                   "wait,1400|evalf,tmp/castle_native.sk",
                   (f"[PERSIMMON] Original {mid} event {num}",),CHECK.replace("@EVENT@",str(num)),
                   flags=flags,timeout=65)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("mode",choices=("before","capture","aliases"))
    args=parser.parse_args()
    native.HERE=HERE
    if args.mode=="aliases":
        aliases(args.profile.resolve())
    else:
        capture(args.profile.resolve(),args.mode=="before")
