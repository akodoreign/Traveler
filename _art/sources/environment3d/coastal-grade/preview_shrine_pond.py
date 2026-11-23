"""Capture the Shrine Court and verify live koi move in the two wet basins."""
import argparse
import json
from pathlib import Path
import struct
import sys

from PIL import Image


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from preview_clan_castles import run, spawn


SLIP = r"""
local stage=::rpgstage;
if(stage.mapid!="M586" || !stage.rtEnvironmentKit)
    throw Exception("The Shrine Court environment did not load");
local koi=stage.rtEnvironmentKit.pondFish;
if(length(koi)!=@COUNT@)
    throw Exception("Unexpected Shrine Court koi count");
::renderhint.set(ClientConfig.renderhints[4]);
local renderer=stage.view3d.renderer;
renderer.updateRenderHint(::renderhint);
class ShrinePondCamera extends RPGCameraMotion {
    function update(dt){}
    function modifyCamera(cw){
        cw.to(Vector3D(18.0,2.1,12.2));
        cw.hpb.x=.04; cw.hpb.y=.67; cw.zoom=14.; cw.fovy=50.;
    }
}
local cam=ShrinePondCamera({});
stage.camwork.addMotion(cam);
sleep(600);

function readPositions(koi) {
    local positions=[];
    foreach(i,pair in koi) {
        local fish=pair[0], p=fish.pos;
        local left=(i<2);
        if(p.x<=(left?14.5:18.5) || p.x>=(left?17.:21.) || p.z<=10.5 || p.z>=14.5)
            throw Exception("A koi left its authored water basin");
        if(!fish.mesh || !fish.mesh.face[0].m.tex0)
            throw Exception("A koi has no mesh or active texture");
        positions.append([p.x,p.z]);
    }
    return positions;
}

@SCREENSHOT@
local before=readPositions(koi);
screenshot(renderer,@FIRST@);
if(length(koi)) {
    sleep(1600);
    local after=readPositions(koi);
    foreach(i,p in before) {
        local dx=after[i][0]-p[0], dz=after[i][1]-p[1];
        if(dx*dx+dz*dz<.04)
            throw Exception("A Shrine Court koi was stationary");
        printf("[KOI] %d from %.3f,%.3f to %.3f,%.3f\n",i,p[0],p[1],after[i][0],after[i][1]);
    }
    screenshot(renderer,@SECOND@);
}
stage.camwork.cammots.removeValue(cam);
printf("[KOI] Shrine Court capture complete.\n");
"""


def capture(engine, destination, baseline):
    tag = "baseline" if baseline else "koi"
    (engine / "tmp/rt_shot").mkdir(exist_ok=True)
    destination.mkdir(parents=True, exist_ok=True)
    files = [f"tmp/rt_shot/bot-bayushi-shrine-pond-{tag}-{t}.raw" for t in ("a", "b")]
    template = (HERE.parent / "preview_coast.sk").read_text("utf8")
    start = template.index("function screenshot(")
    screenshot = template[start:template.index("\n\nlocal views", start)]
    script = SLIP.replace("@SCREENSHOT@", screenshot).replace("@COUNT@", "0" if baseline else "4")
    script = script.replace("@FIRST@", json.dumps(files[0])).replace("@SECOND@", json.dumps(files[1]))
    markers = ("[KOI] Shrine Court capture complete.", "4K frame")
    if not baseline:
        markers += tuple(f"[KOI] {i} from" for i in range(4))
    run(
        engine, f"bayushi-m586-pond-{tag}", "M586", "bayushi", spawn(34, 18, 2.),
        "wait,1200|evalf,tmp/castle_native.sk", markers, script, flags="G831,G832", timeout=55,
    )
    for relative in files[:1] if baseline else files:
        raw = engine / relative
        blob = raw.read_bytes()
        width, height = struct.unpack(">II", blob[:8])
        if (width, height) != (3840, 2160):
            width, height = struct.unpack("<II", blob[:8])
        assert (width, height) == (3840, 2160), (width, height)
        image = Image.frombytes("RGBA", (width, height), blob[8:]).convert("RGB")
        output = destination / (raw.stem.removeprefix("bot-") + "-4k.png")
        image.save(output)
        raw.unlink()
        print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--before", action="store_true")
    args = parser.parse_args()
    capture(args.profile.resolve(), args.destination.resolve(), args.before)


if __name__ == "__main__":
    main()
