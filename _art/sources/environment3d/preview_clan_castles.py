"""Capture and walk the compiled clan castles in the isolated native game."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

from PIL import Image

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent.parent / "outputs"
PROFILE_ENV = {"TEMP":"os-temp","TMP":"os-temp","APPDATA":"roaming","LOCALAPPDATA":"local"}
LEADS = {"hida":"P101","doji":"P102","akodo":"P103","isawa":"P104",
         "bayushi":"P105","kitsuki":"P107","iuchi":"P106","togashi":"P108"}
CAMERAS = {
    "entry": ((37.0,3.27,12.5),.25,.43,17.0,52., (74,31)),
    "court": ((31.0,2.93,20.5),.17,.57,22.6,55., (74,32)),
    "keep": ((37.0,8.12,24.2),.23,.43,27.4,56., (74,30)),
    "first-floor": ((25.5,5.93,17.75),.15,.63,21.6,52., (56,20)),
    "audience": ((26.3,6.0,25.7),.15,.53,20.8,56., (54,40)),
    "cakon-market": ((38.68,2.92,11.90),.25,.45,17.5,54., (85,19)),
    "crane-camp": ((56.0,3.05,15.3),.17,.32,12.6,51., (112,26)),
    "dawn-camp": ((18.8,2.92,6.0),.21,.32,10.8,51., (37,7)),
    "gate-market": ((51.0,2.95,13.0),.25,.35,11.0,51., (100,22)),
    "city-market": ((29.2,2.89,5.8),.29,.37,11.4,51., (57,5)),
    "war-camp": ((38.0,3.27,15.5),.23,.30,13.0,51., (73,26)),
    "border-arena": ((12.0,1.22,42.4),.23,.32,14.0,51., (23,76)),
    "tent": ((21.92,2.67,11.05),.49,.27,8.9,50., (44,14)),
    "library": ((24.0,3.20,23.3),.19,.28,11.9,53., (47,35)),
    "garden": ((49.0,2.76,23.9),.15,.49,15.3,52., (74,32)),
}
CAM = r"""
local stage=::rpgstage;
if(stage.mapid!={mid} || !stage.rtEnvironmentKit)
    throw Exception("The installed castle environment did not load");
stage.changeRenderSetting("rt_hd2d_field");
local renderer=stage.view3d.renderer;
::renderhint.set(ClientConfig.renderhints[4]);
renderer.updateRenderHint(::renderhint);
class CastlePreviewCamera extends RPGCameraMotion {{
    function update(dt){{}}
    function modifyCamera(cw){{
        cw.to(Vector3D({x},{y},{z}));
        cw.hpb.x={heading}; cw.hpb.y={pitch}; cw.zoom={zoom}; cw.fovy={lens};
    }}
}}
local cam=CastlePreviewCamera({{}});
stage.camwork.addMotion(cam);
sleep(600);
{screenshot}
screenshot(renderer,{file});
stage.camwork.cammots.removeValue(cam);
printf("[CASTLE] captured %S.\n",stage.mapid);
"""


def spawn(x,z,y):
    return json.dumps([x*.5,y,z*.5,0.])


def run(engine, label, mid, theme, origin, steps, markers, script="", *, flags="", timeout=52, battle=None):
    fixture=engine/"tmp/castle_native.sk"
    if script:
        fixture.write_text(script,encoding="utf8")
    log=HERE/f"castle-native-{label}.log"
    launch=["-battle",*battle] if battle else ["-map",mid,origin]
    args=[str(engine/"rpgcobo.exe"),"-testplay",*launch,"-rtfast","-rtlead",LEADS[theme],
          "-rtparty","P101","-rtbot",steps]
    if flags:
        args+=["-rtvar",flags]
    env={**os.environ,**{k:str(engine/v) for k,v in PROFILE_ENV.items()}}
    try:
        with log.open("w",encoding="utf8") as stream:
            with subprocess.Popen(args,cwd=engine,stdout=stream,stderr=subprocess.STDOUT,env=env) as game:
                end=time.monotonic()+timeout
                try:
                    while game.poll() is None and time.monotonic()<end:
                        if "BOT finished" in log.read_text(errors="replace"):
                            break
                        time.sleep(.20)
                finally:
                    if game.poll() is None:
                        game.kill()
                    game.wait(timeout=10)
    finally:
        if script:
            fixture.unlink(missing_ok=True)
    result=log.read_text(errors="replace")
    bad=("Exception in thread","NOT reached","[BOT] script error")
    assert all(mark in result for mark in (*markers,"BOT finished")) and not any(s in result for s in bad), result[-5600:]
    print("\n".join(line for line in result.splitlines() if any(m in line for m in markers)))


def capture(engine, mid, theme, view, flags=""):
    (x,y,z),heading,pitch,zoom,lens,(bx,bz)=CAMERAS[view]
    state="-open" if flags and view=="library" else ""
    name=f"{theme}-{mid.lower()}-{view}{state}-daylight-4k"
    relative="tmp/rt_shot/bot_"+name+".raw"
    (engine/relative).parent.mkdir(exist_ok=True)
    script=(HERE/"preview_coast.sk").read_text("utf8")
    start=script.index("function screenshot(")
    function=script[start:script.index("\n\nlocal views",start)]
    cam=CAM.format(mid=json.dumps(mid),x=x,y=y,z=z,heading=heading,pitch=pitch,zoom=zoom,lens=lens,
                   screenshot=function,file=json.dumps(relative))
    y=5. if view in ("first-floor","audience") else .5 if view=="border-arena" else 2.
    run(engine,name,mid,theme,spawn(bx,bz,y),
        "wait,900|evalf,tmp/castle_native.sk",("[CASTLE] captured","4K frame"),cam,flags=flags)
    import struct
    raw=engine/relative
    blob=raw.read_bytes()
    w,h=struct.unpack(">II",blob[:8])
    if (w,h)!=(3840,2160):
        w,h=struct.unpack("<II",blob[:8])
    assert (w,h)==(3840,2160),(w,h)
    output=OUTPUTS/(name+".png")
    image=Image.frombytes("RGBA",(w,h),blob[8:]).convert("RGB")
    image.save(output)
    raw.unlink()
    print(output)


def route(engine, mid, theme, x,z,y, label, steps, maps,flags):
    run(engine,label,mid,theme,spawn(x,z,y),steps,tuple("BOT reached "+m for m in maps),flags=flags,timeout=68)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile",type=Path)
    parser.add_argument("theme",choices=LEADS)
    parser.add_argument("mid")
    sub=parser.add_subparsers(dest="mode",required=True)
    cap=sub.add_parser("capture")
    cap.add_argument("view",choices=CAMERAS)
    cap.add_argument("--flags",default="")
    rt=sub.add_parser("route")
    rt.add_argument("x",type=float)
    rt.add_argument("z",type=float)
    rt.add_argument("y",type=float)
    rt.add_argument("label")
    rt.add_argument("steps")
    rt.add_argument("maps",nargs="+")
    rt.add_argument("--flags",default="")
    args=parser.parse_args()
    if args.mode=="capture":
        capture(args.profile.resolve(),args.mid,args.theme,args.view,args.flags)
    else:
        route(args.profile.resolve(),args.mid,args.theme,args.x,args.z,args.y,args.label,args.steps,args.maps,args.flags)

