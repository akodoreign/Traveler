"""Load Akodo Gusai's two real duel registrations and his field event."""
from pathlib import Path
import struct
import sys

from PIL import Image

from preview_clan_castles import HERE, OUTPUTS, run, spawn

CAPTURE=r"""
stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
battle.battleui.setVisible(false);
class GusaiReviewCamera extends RPGCameraMotion {
    target = null;
    heading = 0.;
    function update(dt){}
    function modifyCamera(cw){
        cw.to(target);
        cw.hpb.x=heading;
        cw.hpb.y=.23;
        cw.zoom=3.85;
        cw.fovy=51.;
    }
}
local p=actor.pos;
local cam=GusaiReviewCamera({});
cam.target=Vector3D(p.x,p.y+1.02,p.z);
stage.camwork.addMotion(cam);
local start=actor.dir+Math.PI;
foreach(view in [["front",start],["side",start+Math.PI*.5]]){
    cam.heading=view[1];
    sleep(400);
    screenshot(renderer,"tmp/rt_shot/bot_gusai_"..view[0]..".raw");
}
stage.camwork.cammots.removeValue(cam);
"""


def verify(profile,fixtures):
    field=(fixtures/"gusai_field_proof.sk").read_text("utf8")
    duel=(fixtures/"gusai_duel_proof.sk").read_text("utf8")
    probe="wait,1120|evalf,tmp/castle_native.sk"
    run(profile,"gusai-field-m245","M245","akodo",spawn(25,20,1.),probe,
        ("[GUSAI FIELD FIT] M245 event 6",),field)
    for group,enemy,arena in (("51","E351","M834"),("68","E389","M833")):
        run(profile,"gusai-real-duel-"+enemy.lower(),"M245","akodo",spawn(25,20,1.),
            probe,(f"[GUSAI DUEL FIT] {arena} {enemy} EP834",),duel,
            battle=("M001",group))
    preview=(HERE/"preview_coast.sk").read_text("utf8")
    start=preview.index("function screenshot(")
    png=preview[start:preview.index("\n\nlocal views",start)]
    run(profile,"gusai-daylight-review","M102","akodo",spawn(49,21,2.),
        probe+"|untilmap,M811,14000|wait,1450|evalf,tmp/castle_native.sk",
        ("BOT reached M811","[GUSAI DUEL FIT] M811 E351 EP834"),png+"\n"+duel+CAPTURE)
    for view in ("front","side"):
        blob=(profile/"tmp/rt_shot"/f"bot_gusai_{view}.raw").read_bytes()
        dimensions=struct.unpack_from("<II",blob)
        assert dimensions==(3840,2160),dimensions
        Image.frombytes("RGBA",dimensions,blob[8:]).convert("RGB").save(OUTPUTS/f"akodo-gusai-{view}-daylight-4k.png")


if __name__=="__main__":
    verify(*(Path(arg).resolve() for arg in sys.argv[1:3]))
