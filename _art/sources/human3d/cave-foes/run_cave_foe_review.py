"""Verify the cave foe fits and capture the battlers in native daylight."""
from pathlib import Path
import struct,sys
from PIL import Image

from preview_clan_castles import run,spawn

HERE=Path.cwd()
ART=HERE.parent/"human-foes/cave-stage/cave_foe_proof.sk"
OUT=HERE.parent.parent/"outputs"
CAPTURE=r"""
stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
battle.battleui.setVisible(false);
local lengthFoes=length(battle.enemies), cx=0.,cy=0.,cz=0.;
foreach(enemy in battle.enemies){
    local actor=battle.getChara3D(enemy);
    cx+=actor.pos.x;
    cy+=actor.pos.y;
    cz+=actor.pos.z;
}
cx/=lengthFoes; cy/=lengthFoes; cz/=lengthFoes;
class ReviewActorCamera extends RPGCameraMotion {
    focus = null;
    scale = 0.;
    function update(dt){}
    function modifyCamera(cw){
        cw.to(focus);
        cw.hpb.x=-.62;
        cw.hpb.y=.28;
        cw.zoom=scale;
        cw.fovy=48.;
    }
}
local review=ReviewActorCamera({});
review.focus=Vector3D(cx,cy+.89,cz);
review.scale=lengthFoes>2 ? 9.05 : lengthFoes>1 ? 6.6 : 4.75;
stage.camwork.addMotion(review);
sleep(680);
screenshot(renderer,@FILE@);
stage.camwork.cammots.removeValue(review);
"""

def main(profile):
    raw=HERE.joinpath("preview_coast.sk").read_text("utf8")
    start=raw.index("function screenshot(")
    image_function=raw[start:raw.index("\n\nlocal views",start)]
    fixture=ART.read_text("utf8")
    cases=(
        ("yasuki-border-patrol","M480","M829",65,20),
        ("river-border-patrol","M482","M829",62,23),
        ("lion-swords-for-hire","M483","M819",67,17),
        ("lion-mine-foe-fits","M484","M819",73,16),
    )
    for name,origin,arena,x,z in cases:
        filename=f"tmp/rt_shot/{name}.raw"
        outfile=OUT/f"{name}-daylight-4k.png"
        (profile/filename).parent.mkdir(exist_ok=True)
        script=fixture+"\n"+image_function+CAPTURE.replace("@FILE@",'"'+filename+'"')
        run(profile,name,origin,"kitsuki",spawn(x,z,1.5),
            f"wait,760|evalf,tmp/castle_native.sk|untilmap,{arena},14000|wait,1550|evalf,tmp/castle_native.sk",
            (f"BOT reached {arena}","fixture passed","4K frame"),script,timeout=50)
        raw=(profile/filename).read_bytes()
        w,h=struct.unpack("<II",raw[:8])
        assert (w,h)==(3840,2160),(name,w,h)
        Image.frombytes("RGBA",(w,h),raw[8:]).convert("RGB").save(outfile)
        (profile/filename).unlink()
        print(outfile,flush=True)

if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
