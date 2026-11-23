"""Compare fixed native frames with and without the sampled render effects."""
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from preview_clan_castles import HERE,run,spawn

STAGE=r"""
local stage=::rpgstage;
if(stage.mapid!="M488" || !stage.rtEnvironmentKit) throw Exception("No Dragon cavern to sample");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class SurfaceReviewCamera extends RPGCameraMotion{
    function update(dt){}
    function modifyCamera(cw){
        cw.to(Vector3D(41.58,2.27,11.47));
        cw.hpb.x=.15; cw.hpb.y=.48; cw.zoom=15.5; cw.fovy=54.;
    }
}
stage.camwork.addMotion(SurfaceReviewCamera({}));
sleep(470);
screenshot(renderer,"tmp/rt_shot/bot_grain_first.raw");
sleep(800);
screenshot(renderer,"tmp/rt_shot/bot_grain_later.raw");
local p=renderer.mainpass;
if(!p.ssaopass || !p.pbrpostpass) throw Exception("Missing active deferred render passes");
p.ssaopass.enabled=false;
sleep(120);
screenshot(renderer,"tmp/rt_shot/bot_grain_noao.raw");
p.pbrpostpass.setBloom(0.,0.,0.);
p.pbrpostpass.setDOF(0.,0.);
sleep(120);
screenshot(renderer,"tmp/rt_shot/bot_grain_none.raw");
printf("[GRAIN] Sampled a fixed cave wall with and without ambient occlusion and post effects\n");
"""


def check(profile):
    preview=(HERE/"preview_coast.sk").read_text("utf8")
    shader=preview[preview.index("function screenshot("):preview.index("\n\nlocal views")]
    run(profile,"grain-probe","M488","kitsuki",spawn(76,20,1.5),
        "wait,850|evalf,tmp/castle_native.sk",("[GRAIN] Sampled",),shader+"\n"+STAGE,timeout=35)
    darkest=[]
    root=HERE/"color-qa"
    for key in ("first","later","noao","none"):
        blob=(profile/"tmp/rt_shot"/f"bot_grain_{key}.raw").read_bytes()
        size=struct.unpack_from("<II",blob)
        assert size==(3840,2160),size
        image=Image.frombytes("RGBA",size,blob[8:]).convert("RGB")
        crop=image.crop((1010,105,1955,510))
        crop.save(root/f"m488-grain-{key}.png")
        signal=np.asarray(crop,dtype=float)@[.2126,.7152,.0722]
        fine=signal-gaussian_filter(signal,2.)
        darkest.append(fine)
        print(key,"fine rock detail RMS",round(float(np.sqrt(np.mean(fine**2))),3))
    print("Fixed exposure frame-to-frame fine detail RMS",
          round(float(np.sqrt(np.mean((darkest[0]-darkest[1])**2))),3))


if __name__=="__main__":
    check(Path(sys.argv[1]).resolve())
