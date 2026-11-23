"""Verify routes through rebuilt outdoor maps in the native game."""

from pathlib import Path
import subprocess
import sys
import time


repo=Path(sys.argv[1]).resolve()
profile=Path(sys.argv[2]).resolve()
kind=sys.argv[3]
sys.path.insert(0,str(repo/"tools"))
import playbot

extra_args=[]
lead="P102"

if kind.startswith("door-centred-"):
    mid,dest,event,x,z,goal,back,flags={
        "bath":("M360","M955",85,40.0,19.1,"40.0,25.1","21.2,7.0","G861,G879,G880,G881"),
        "willow":("M375","M376",2,72.0,19.9,"72.0,26.1","7.2,11.0","G918,G919,G924,G925,G926,G927"),
        "dragon":("M380","M381",2,87.0,18.8,"87.0,25.7","6.4,9.7","G944,G945,G946,G947,G948,G959"),
        "autumn":("M387","M388",1,40.0,20.0,"40.0,26.7","6.4,9.2","G967,G968,G969,G972,G977,G978,G979,G981,G982"),
    }[kind.removeprefix("door-centred-")]
    path=(f"wait,780|evalf,tmp/route_check_start.sk|goto,{goal},10500|untilmap,{dest},8500|"
          f"wait,680|evalf,tmp/route_check_end.sk|goto,{back},10500|untilmap,{mid},8500")
    first=f'''
::rpgstage.encinc=0.0;
local e=::rpgstage.getEvent({event});
if(!e || e.data.pos[0]!={int(x)})
    throw Exception("The doorway trigger is off the opening's centre");
printf("DOOR centre and trigger agree\\n");
'''
    second=f'''
if(::rpgstage.mapid!="{dest}") throw Exception("The centred door reached the wrong interior");
printf("DOOR centred walk reached the interior\\n");
'''
    marks=("DOOR centre and trigger agree",f"BOT reached {dest}",
           "DOOR centred walk reached the interior",f"BOT reached {mid}")
elif kind=="iuchi-caravan":
    mid,x,z,flags="M413",13.6,23.0,"G1029,G1203"
    lead="P106"
    path=("wait,820|evalf,tmp/route_check_start.sk|answer,0|goto,-.2,23.0,14000|"
          "untilmap,M369,14000|evalf,tmp/route_check_end.sk")
    first=r'''
::rpgstage.encinc=0.0;
if(!::rpgvar["G1031"] || !::rpgstage.rtEnvironmentKit)
    throw Exception("The caravan did not finish the homecoming scene");
printf("IUCHI homecoming scene complete\n");
'''
    second=r'''
if(::rpgstage.mapid!="M369") throw Exception("The valley road did not reach Buried Leaves");
printf("IUCHI caravan reached Buried Leaves\n");
'''
    marks=("IUCHI homecoming scene complete","BOT reached M369","IUCHI caravan reached Buried Leaves")
elif kind=="cakon-memory":
    mid,x,z,flags="M414",34.,16.,"G1038,G1040"
    lead="P107"
    path="wait,750|untilmap,M415,17000|wait,700|evalf,tmp/route_check_end.sk"
    first=""
    second=r'''
if(::rpgstage.mapid!="M415" || !::rpgvar["G1062"] || !::rpgstage.rtEnvironmentKit)
    throw Exception("The memory did not land on the Cakon dock");
printf("CAKON memory scene landed on the dock\n");
'''
    marks=("BOT reached M415","CAKON memory scene landed on the dock")
elif kind in ("cakon-river-hut","cakon-hamlet-hut"):
    river=kind=="cakon-river-hut"
    mid,x,z,flags=("M414",61.7,25.0,"G1062") if river else ("M418",29.8,28.0,"G1043,G1045")
    goal=68.0 if river else 36.8
    block=66 if river else 34
    width,front,depth=(4,24,3) if river else (5,26,4)
    lead="P107"
    path=f"wait,800|evalf,tmp/route_check_start.sk|goto,{goal},{z},5100|evalf,tmp/route_check_end.sk"
    first=f'''
::rpgstage.encinc=0.0;
if(!::rpgstage.bw.bmp || !::rpgstage.bw.bmp.get({block},{int(z)}))
    throw Exception("The fitted hut lost its footprint");
'''
    second=f'''
local p=::rpgstage.player3d.pos;
if(p.x>={block/2} && p.x<{(block+width)/2} && p.z>={front/2} && p.z<{(front+depth)/2})
    throw Exception("The party walked into a closed hut");
printf("CAKON hut footprint blocked entry\\n");
'''
    marks=("BOT jump (blocked)","CAKON hut footprint blocked entry")
elif kind in ("cakon-gate-locked","cakon-gate-no-bypass"):
    mid,x,flags="M417",106.7,"G1040,G1041,G1061"
    z=19.0 if kind.endswith("locked") else 35.0
    lead="P107"
    path=(f"wait,720|evalf,tmp/route_check_start.sk|goto,118.0,{z},5500|"
          "evalf,tmp/route_check_end.sk")
    first=r'''
::rpgstage.encinc=0.0;
local gate=::rpgstage.rtEnvironmentKit.portcullises[0];
if(gate[2]!=0.0 || gate[3] || !::rpgstage.bw.bmp.get(111,19))
    throw Exception("The portcullis is open before the story unlock");
printf("CAKON portcullis is locked\n");
'''
    second=r'''
if(::rpgstage.player3d.pos.x>=56.0)
    throw Exception("The party walked around the locked gate");
printf("CAKON wall held the closed route\n");
'''
    marks=("CAKON portcullis is locked","CAKON wall held the closed route")
elif kind in ("cakon-docks-market","cakon-market-docks","cakon-market-alley","cakon-alley-market",
              "cakon-gate-east","cakon-gate-west","cakon-hamlet-canal","cakon-canal-hamlet",
              "cakon-canal-paddies","cakon-paddies-canal"):
    mid,dest,x,z,way={
        "cakon-docks-market":("M415","M416",146.3,25.0,"155.4,25.0"),
        "cakon-market-docks":("M416","M415",8.0,28.0,"-.4,28.0"),
        "cakon-market-alley":("M416","M417",153.2,28.0,"161.4,28.0"),
        "cakon-alley-market":("M417","M416",8.0,23.0,"-.4,23.0"),
        "cakon-gate-east":("M417","M418",104.6,19.1,"151.0,23.0"),
        "cakon-gate-west":("M418","M417",8.0,26.0,"-.4,26.0"),
        "cakon-hamlet-canal":("M418","M419",144.1,26.0,"151.0,26.0"),
        "cakon-canal-hamlet":("M419","M418",7.8,24.0,"-.4,24.0"),
        "cakon-canal-paddies":("M419","M420",66.4,19.2,"151.2,24.0"),
        "cakon-paddies-canal":("M420","M419",8.0,26.0,"-.4,26.0"),
    }[kind]
    lead="P107"
    flags="G1062,G1040,G1041,G1043,G1061,G1055,G1045,G1047,G1048"
    first='::rpgstage.encinc=0.0;'
    second=f'''
if(::rpgstage.mapid!="{dest}") throw Exception("The Cakon exit led to the wrong map");
printf("CAKON arrived in {dest} on foot\\n");
'''
    approach=""
    path_end=""
    if kind=="cakon-canal-paddies":
        approach="|goto,84.5,19.2,10500|evalf,tmp/route_check_start.sk"
        first=r'''
::rpgstage.encinc=0.0;
local p=::rpgstage.player3d.pos;
if(p.x>41.9 && p.y>=1.94)
    printf("CAKON walked over the maple log\n");
'''
    if kind=="cakon-gate-east":
        approach="|goto,117.5,19.1,9000|evalf,tmp/route_check_start.sk"
        first=r'''
::rpgstage.encinc=0.0;
local p=::rpgstage.player3d.pos;
local gate=::rpgstage.rtEnvironmentKit.portcullises[0];
if(!gate[3] || ::rpgstage.bw.bmp.get(111,19))
    throw Exception("The portcullis failed to lift its blocking cells");
if(p.x<53.) return;
if(p.x<57.5 || p.z<8.55 || p.z>10.55)
    throw Exception("The party did not walk through the river gate");
printf("CAKON walked through the original river wall\n");
'''
    if kind=="cakon-gate-west":
        path_end="|goto,106.5,19.1,11000|evalf,tmp/route_check_start.sk"
        first=r'''
::rpgstage.encinc=0.0;
if(::rpgstage.mapid!="M417") return;
if(::rpgstage.player3d.pos.x>54.)
    throw Exception("The party could not return through the river gate");
printf("CAKON returned through the original river wall\n");
'''
    path=(f"wait,750|evalf,tmp/route_check_start.sk{approach}|goto,{way},14000|untilmap,{dest},14000|"
          f"evalf,tmp/route_check_end.sk{path_end}")
    marks=(f"BOT reached {dest}",f"CAKON arrived in {dest} on foot")
    if kind=="cakon-gate-east":
        marks+=("CAKON walked through the original river wall",)
    elif kind=="cakon-gate-west":
        marks+=("CAKON returned through the original river wall",)
    elif kind=="cakon-canal-paddies":
        marks+=("CAKON walked over the maple log",)
elif kind in ("kamen-temple-gate-locked","kamen-temple-gate-open"):
    mid,x,z,flags="M362",125.4,21.0,"G879,G880,G881,G882,G898,G899,G903,G904,G917"
    lead="P105"
    closed=kind.endswith("locked")
    if not closed:
        flags+=",G891,G893"
    path="wait,740|evalf,tmp/route_check_start.sk|goto,142.0,21.0,8400|evalf,tmp/route_check_end.sk"
    first=r'''
::rpgstage.encinc=0.0;
local gate=::rpgstage.rtEnvironmentKit.portcullises[0];
if(gate[3]==!!::rpgstage.bw.bmp.get(132,21))
    throw Exception("The temple gate's collision does not match its lift");
printf("KAMEN gate condition and collision match\n");
'''
    bound="p.x>=66.0" if closed else "p.x<69.5"
    second=f'''
local p=::rpgstage.player3d.pos;
if({bound}) throw Exception("The temple gate behaved incorrectly on foot");
printf("KAMEN gate walk passed\\n");
'''
    marks=("KAMEN gate condition and collision match","KAMEN gate walk passed")
    if not closed:
        path+="|goto,154.0,30.0,9500|goto,163.0,30.0,9500|untilmap,M365,8500"
        marks+=("BOT reached M365",)
elif kind in ("hiruma-curtain-bailey","hiruma-curtain-keep"):
    mid,dest,x,z,threshold,target={
        "hiruma-curtain-bailey":("M461","M462",150.,28.,"157.0,28.0","160.6,28.0"),
        "hiruma-curtain-keep":("M462","M463",135.,26.,"143.0,26.0","146.6,26.0"),
    }[kind]
    flags="G1216,G1217,G1218,G1219"
    lead="P105"
    first="::rpgstage.encinc=0.0;"
    second=f'''
if(::rpgstage.mapid!="{dest}") throw Exception("The Hiruma ruin left its original approach");
printf("HIRUMA walked through the ruined gate\\n");
'''
    path=(f"wait,750|evalf,tmp/route_check_start.sk|answer,0|goto,{threshold},8200|goto,{target},9000|"
          f"untilmap,{dest},9000|evalf,tmp/route_check_end.sk")
    marks=(f"BOT reached {dest}","HIRUMA walked through the ruined gate")
elif kind in ("iuchi-narrows-locked","iuchi-narrows-flank"):
    mid,flags="M410","G999,G1022,G1025,G1027,G1029"
    x,z,goal=(126.4,14.1,"126.4,21.0") if kind.endswith("locked") else (119.2,19.9,"126.0,20.0")
    path=f"wait,710|evalf,tmp/route_check_start.sk|goto,{goal},6100|evalf,tmp/route_check_end.sk"
    first=r'''
::rpgstage.encinc=0.0;
local gate=::rpgstage.rtEnvironmentKit.portcullises[0];
if(gate[3] || !::rpgstage.bw.bmp.get(126,18))
    throw Exception("The narrows gate did not block the crosswise lane");
printf("IUCHI crosswise portcullis is locked\n");
'''
    bound="p.z>=9.15" if kind.endswith("locked") else "p.x>=62.0 && p.z>=9.05"
    second=f'''
local p=::rpgstage.player3d.pos;
if({bound}) throw Exception("The party bypassed the locked narrows gate");
printf("IUCHI closed narrows held the approach\\n");
'''
    marks=("IUCHI crosswise portcullis is locked","IUCHI closed narrows held the approach")
elif kind.startswith("iuchi-gale-"):
    mid="M410" if kind.endswith("narrows") else "M409"
    forced="gust" in kind
    x,z,flags=52.8,16.0,"G999,G1022,G1025,G1026,G1027,G1029"
    path=("wait,750|evalf,tmp/route_check_start.sk|goto,63.0,16.0,9500|"
          "evalf,tmp/route_check_end.sk")
    first=r'''
::rpgstage.encinc=0.0;
local kit=::rpgstage.rtEnvironmentKit;
local forced=::arguments.indexOf("-rtgale100")>=0;
local gust=false, lull=false, start=skGetTime();
while(skGetTime()-start<2400){
    kit.syncWind();
    local expected=forced || (skGetTime()/900)%2==0;
    if(kit.gustActive==expected){
        gust=gust || (expected && kit.windStreaks[0][0].visible);
        lull=lull || (!expected && !kit.windStreaks[0][0].visible);
    }
    if(gust && (forced || lull)) break;
    suspend();
}
if(!gust || (!forced && !lull)) throw Exception("Wind cues did not follow the hazard clock");
printf("IUCHI gale cues sync with gameplay\n");
'''
    second=r'''
local x=::rpgstage.player3d.pos.x;
local forced=::arguments.indexOf("-rtgale100")>=0;
if(forced ? (x>=31.0) : (x<30.9))
    throw Exception("Gale strip walk finished at the wrong position: " + x);
printf("IUCHI gale walk finished at %.2f\n", x);
'''
    marks=("IUCHI gale cues sync with gameplay","IUCHI gale walk finished")
    if forced:
        extra_args.append("-rtgale100")
        marks+=("[RT] GALE back",)
elif kind=="iuchi-storm-ending":
    mid,x,z,flags="M412",10.0,13.0,"G999"
    path=("wait,750|answer,0|evalf,tmp/route_check_start.sk|goto,20.3,13.0,10000|"
          "untilmap,M413,26000|evalf,tmp/route_check_end.sk")
    first=r'''
newthread().start(function(){
    local start=skGetTime();
    while(skGetTime()-start<18000){
        local stage=::rpgstage, fight=stage["battle"];
        if(stage.mapid=="M882" && fight && stage.rtEnvironmentKit &&
           fight.enemies.find(@(e) e.dataid=="E518") && fight.enemies.find(@(e) e.dataid=="E519")){
            printf("IUCHI Kurosho and the Doji loaded in the storm arena\n");
            fight.stopBattle(1);
            fight.setAutoBattle(true);
            return;
        }
        sleep(100);
    }
    throw Exception("The storm room did not start its actual encounter");
});
'''
    second=r'''
if(::rpgstage.mapid!="M413" || !::rpgvar["G1029"] || !::rpgvar["G1030"])
    throw Exception("The storm room story did not reach the road after the treaty");
printf("IUCHI storm room story reached the valley road\n");
'''
    extra_args.extend(("-debuglv","80"))
    marks=("BOT MAP M882","IUCHI Kurosho and the Doji loaded in the storm arena",
           "[ENV] M412 wind settled",
           "BOT reached M413","IUCHI storm room story reached the valley road")
elif kind in ("iuchi-siege-mouth","iuchi-wind-connection","iuchi-wind-west","iuchi-narrows-gate","iuchi-storm-stairs"):
    flags="G1010,G1022,G1025,G1026,G1027,G1029"
    mid,dest,x,z,way,back={
        "iuchi-siege-mouth":("M408","M409",126.8,20.0,"136.0,20.0","-.6,20.0"),
        "iuchi-wind-connection":("M409","M410",153.3,20.0,"160.8,20.0",None),
        "iuchi-wind-west":("M410","M409",7.2,20.0,"-.6,20.0",None),
        "iuchi-narrows-gate":("M410","M411",126.4,14.1,"126.4,21.0","6.2,10.0"),
        "iuchi-storm-stairs":("M411","M412",32.3,13.8,"32.3,17.7","6.2,10.0"),
    }[kind]
    if mid!="M408":
        flags+=",G999"
    first='::rpgstage.encinc=0.0;'
    second=f'''
::rpgstage.encinc=0.0;
if(::rpgstage.mapid!="{dest}" || !::rpgstage.rtEnvironmentKit)
    throw Exception("Wrong destination or missing environment");
printf("IUCHI arrived in {dest} on foot\\n");
'''
    choice="|answer,0" if kind=="iuchi-siege-mouth" else ""
    if choice:
        second+=r'''
if(!::rpgvar["G999"]) throw Exception("The tunnel choice did not equip the wax");
printf("IUCHI wax applied by the tunnel choice\n");
'''
    path=(f"wait,750|evalf,tmp/route_check_start.sk{choice}|goto,{way},10500|untilmap,{dest},8500|"
          "wait,680|evalf,tmp/route_check_end.sk")
    marks=(f"BOT reached {dest}",f"IUCHI arrived in {dest} on foot")
    if back:
        path+=f"|goto,{back},21000|untilmap,{mid},8500"
        marks+=(f"BOT reached {mid}",)
    if choice:
        marks+=("IUCHI wax applied by the tunnel choice",)
elif kind=="kudo":
    mid,x,z,flags="M350",149.5,24.0,"G845"
    path=("wait,700|goto,161.0,24.5,10800|untilmap,M351,8500|"
          "evalf,tmp/route_check_start.sk|goto,43.5,18.5,8500|evalf,tmp/route_check_end.sk")
    first=r'''
if(::rpgstage.mapid!="M351" || ::rpgstage.player3d.pos.x>=20.0)
    throw Exception("Kudo did not land on its west approach");
::Rokugan.kudoProofStart <- ::rpgstage.player3d.pos.x;
printf("KUDO west landing %.2f\n", ::Rokugan.kudoProofStart);
'''
    second=r'''
if(::rpgstage.mapid!="M351" || ::rpgstage.player3d.pos.x<::Rokugan.kudoProofStart+4.0)
    throw Exception("Kudo did not continue eastward");
printf("KUDO east walk %.2f\n", ::rpgstage.player3d.pos.x);
'''
    marks=("BOT reached M351","KUDO west landing","KUDO east walk")
elif kind=="ford":
    mid,x,z,flags="M355",92.5,18.5,"G853,G854,G855"
    path=("wait,750|goto,62.5,18.5,12500|evalf,tmp/route_check_start.sk|"
          "goto,27.0,18.5,13000|goto,13.0,23.5,10000|goto,0.05,23.5,8500|"
          "untilmap,M356,8500|evalf,tmp/route_check_end.sk")
    first=r'''
if(::rpgstage.mapid!="M355" || ::rpgstage.player3d.pos.x<30.0 ||
   ::rpgstage.player3d.pos.x>33.0 || ::rpgstage.player3d.pos.y<1.45)
    throw Exception("The party could not stand on the stone ford");
printf("KUDO ford crossing at %.2f\n", ::rpgstage.player3d.pos.x);
if(!::rpgvar["G854"]) throw Exception("The west exit requires G854");
'''
    second=r'''
if(::rpgstage.mapid!="M356" || ::rpgstage.player3d.pos.x<40.0)
    throw Exception("The ford did not connect to the east approach of the west marsh");
printf("KUDO marsh landing %.2f\n", ::rpgstage.player3d.pos.x);
'''
    marks=("KUDO ford crossing","BOT reached M356","KUDO marsh landing")
elif kind in ("kensu-inn","kensu-trader"):
    mid,z,flags="M360",20.9,"G861,G879,G880,G881"
    x,event,dest=(39.3,85,"M955") if kind=="kensu-inn" else (95.3,86,"M956")
    path=(f"wait,1000|evalf,tmp/route_check_start.sk|goto,{x},25.8,9000|"
          f"untilmap,{dest},8500|evalf,tmp/route_check_end.sk")
    first=r'''
local found=false;
foreach(row in ::rpgstage.rtEnvironmentKit.townDoors)
    if(row[0]==@EVENT@ && row[2]>.80) found=true;
if(!found) throw Exception("The accessible exterior door did not open");
printf("KENSU door @EVENT@ is ajar\n");
'''.replace("@EVENT@",str(event))
    second=r'''
if(::rpgstage.mapid!="@DEST@") throw Exception("The exterior door did not lead to its room");
printf("KENSU room @DEST@ reached\n");
'''.replace("@DEST@",dest)
    marks=(f"KENSU door {event} is ajar",f"BOT reached {dest}",f"KENSU room {dest} reached")
elif kind=="kamen":
    mid,x,z,flags="M361",145.5,19.2,"G879,G880,G881,G882,G891,G893,G898,G899"
    path=("wait,800|goto,155.5,24,9500|untilmap,M362,8500|"
          "evalf,tmp/route_check_start.sk|goto,40.5,22.1,8500|goto,40.5,26.0,8500|"
          "untilmap,M363,8500|wait,1100|evalf,tmp/route_check_end.sk|"
          "goto,6.4,10.2,7000|untilmap,M362,8500")
    first=r'''
if(::rpgstage.mapid!="M362" || ::rpgstage.player3d.pos.x>=18.0)
    throw Exception("An eastbound traveler should enter Kamen through the west gateway");
printf("KAMEN west gateway %.2f\n", ::rpgstage.player3d.pos.x);
'''
    second=r'''
if(::rpgstage.mapid!="M363" || !::rpgstage.rtEnvironmentKit)
    throw Exception("The furnished Sweet Cup room did not load");
printf("KAMEN Sweet Cup back room reached\n");
'''
    marks=("BOT reached M362","KAMEN west gateway","BOT reached M363","KAMEN Sweet Cup back room reached")
elif kind=="ojatara":
    mid,x,z,flags="M368",145.5,19.0,"G909,G918,G919,G925,G926,G927"
    path=("wait,800|goto,155.7,25.0,9500|untilmap,M369,8500|wait,1200|"
          "evalf,tmp/route_check_start.sk|goto,65.5,20.4,14000|goto,65.4,26.3,8000|"
          "untilmap,M370,8500|wait,1000|evalf,tmp/route_check_end.sk|"
          "goto,6.4,9.4,7000|untilmap,M369,8500")
    first=r'''
if(::rpgstage.mapid!="M369" || ::rpgstage.player3d.pos.x>=19.0)
    throw Exception("The Ojatara road did not enter the west end of Buried Leaves");
if(!::rpgstage.rtEnvironmentKit || length(::rpgstage.rtEnvironmentKit.townDoors)!=4)
    throw Exception("The four available doors did not load");
printf("OJATARA Buried Leaves west landing %.2f\n", ::rpgstage.player3d.pos.x);
'''
    second=r'''
if(::rpgstage.mapid!="M370" || !::rpgstage.rtEnvironmentKit)
    throw Exception("The open tribunal door did not reach the furnished tribunal");
printf("OJATARA tribunal reached\n");
'''
    marks=("BOT reached M369","OJATARA Buried Leaves west landing","BOT reached M370","OJATARA tribunal reached")
elif kind=="nihime":
    mid,x,z,flags="M375",71.2,21.4,"G927,G929,G943"
    path=("wait,1000|evalf,tmp/route_check_start.sk|goto,71.2,26.0,8000|"
          "untilmap,M376,8500|wait,1000|evalf,tmp/route_check_end.sk|"
          "goto,7.4,10.3,7000|untilmap,M375,8500")
    first=r'''
if(length(::rpgstage.rtEnvironmentKit.townDoors)!=1 || ::rpgstage.rtEnvironmentKit.townDoors[0][2]<.8)
    throw Exception("Nihime's house is visually closed");
printf("OJATARA Nihime door ajar\n");
'''
    second=r'''
if(::rpgstage.mapid!="M376" || !::rpgstage.rtEnvironmentKit)
    throw Exception("Nihime's furnished house did not load");
printf("OJATARA Nihime house reached\n");
'''
    marks=("OJATARA Nihime door ajar","BOT reached M376","OJATARA Nihime house reached","BOT reached M375")
elif kind=="scorpion":
    mid,x,z,flags="M347",145.7,21.2,"G839,G869,G840,G842,G843,G844,G845"
    path=("wait,750|goto,155.8,28,9500|untilmap,M348,8500|"
          "evalf,tmp/route_check_start.sk|goto,137.6,18.2,24500|goto,147.8,24,9500|"
          "untilmap,M349,8500|evalf,tmp/route_check_end.sk")
    first=r'''
if(::rpgstage.mapid!="M348" || ::rpgstage.player3d.pos.x>=20.0)
    throw Exception("The eastbound castle route did not enter the west side of Traitor's Grove");
::rpgstage.encinc=0.0;
printf("SCORPION grove west landing %.2f\n",::rpgstage.player3d.pos.x);
'''
    second=r'''
if(::rpgstage.mapid!="M349" || ::rpgstage.player3d.pos.x>=20.0)
    throw Exception("The eastbound grove route did not enter the west side of Shutai");
printf("SCORPION Shutai west landing %.2f\n",::rpgstage.player3d.pos.x);
'''
    marks=("BOT reached M348","SCORPION grove west landing","BOT reached M349","SCORPION Shutai west landing")
elif kind=="bayushi-bridge":
    mid,x,z,flags="M345",42.0,17.3,"G831,G832,G838,G839"
    path=("wait,550|goto,42.2,24,8500|evalf,tmp/route_check_start.sk|"
          "goto,42.2,33.3,9500|evalf,tmp/route_check_end.sk")
    first=r'''
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M345" || p.z<11.4 || p.z>12.7 || p.y<2.1)
    throw Exception("The garden bridge is not reachable over the koi pond");
printf("BAYUSHI bridge deck %.2f %.2f\n",p.y,p.z);
'''
    second=r'''
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M345" || p.z<16.05)
    throw Exception("The koi bridge did not reach the far garden bank");
printf("BAYUSHI far bank %.2f\n",p.z);
'''
    marks=("BAYUSHI bridge deck","BAYUSHI far bank")
elif kind=="dragon-inn":
    mid,x,z,flags="M380",86.4,18.8,"G944,G945,G946,G947,G948,G959"
    path=("wait,950|evalf,tmp/route_check_start.sk|goto,86.4,25.7,9000|"
          "untilmap,M381,8500|wait,1000|evalf,tmp/route_check_end.sk|"
          "goto,6.4,9.7,7500|untilmap,M380,8500")
    first=r'''
::rpgstage.encinc=0.0;
if(length(::rpgstage.rtEnvironmentKit.townDoors)!=1 || ::rpgstage.rtEnvironmentKit.townDoors[0][2]<.8)
    throw Exception("The available mountain inn door is visually closed");
printf("DRAGON mountain inn door ajar\n");
'''
    second=r'''
if(::rpgstage.mapid!="M381" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(5))
    throw Exception("The common room or innkeeper is missing");
printf("DRAGON common room reached\n");
'''
    marks=("DRAGON mountain inn door ajar","BOT reached M381","DRAGON common room reached","BOT reached M380")
elif kind=="autumn-inn":
    mid,x,z,flags="M387",39.4,20.0,"G967,G968,G969,G972,G977,G978,G979,G981,G982"
    path=("wait,750|evalf,tmp/route_check_start.sk|goto,39.4,26.7,8500|"
          "untilmap,M388,8500|wait,800|evalf,tmp/route_check_end.sk|"
          "goto,6.4,9.2,7500|untilmap,M387,8500")
    first=r'''
if(length(::rpgstage.rtEnvironmentKit.townDoors)!=2 || ::rpgstage.rtEnvironmentKit.townDoors[0][2]<.8 ||
   ::rpgstage.rtEnvironmentKit.townDoors[1][2]<.8)
    throw Exception("The available Welcome Road inn door is visually closed");
printf("AUTUMN Welcome Road door ajar\n");
'''
    second=r'''
if(::rpgstage.mapid!="M388" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(11))
    throw Exception("The Welcome Road room or innkeeper is missing");
printf("AUTUMN Welcome Road common room reached\n");
'''
    marks=("AUTUMN Welcome Road door ajar","BOT reached M388","AUTUMN Welcome Road common room reached","BOT reached M387")
elif kind=="hafuna":
    mid,x,z,flags="M390",102.4,20.6,"G967,G968,G969,G972,G973,G974,G977,G978,G979,G981,G982"
    path=("wait,720|evalf,tmp/route_check_start.sk|goto,102.4,14.6,8500|"
          "untilmap,M392,8500|wait,730|evalf,tmp/route_check_end.sk|"
          "goto,71.4,32.3,7500|untilmap,M390,8500")
    first=r'''
::rpgstage.encinc=0.0;
if(!::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(3))
    throw Exception("The valley road or Hafuna turnoff is missing");
printf("AUTUMN Hafuna turnoff present\n");
'''
    second=r'''
if(::rpgstage.mapid!="M392" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(2))
    throw Exception("The Hafuna field or its testimony event is missing");
printf("AUTUMN Hafuna testimony present\n");
'''
    marks=("AUTUMN Hafuna turnoff present","BOT reached M392","AUTUMN Hafuna testimony present","BOT reached M390")
elif kind=="yotomo-cave":
    mid,x,z,flags="M396",126.4,24.4,"G967,G968,G969,G972,G978,G979,G980,G981"
    path=("wait,750|goto,135.4,24.4,7500|evalf,tmp/route_check_start.sk|goto,141.0,24.4,7500|"
          "untilmap,M397,8500|wait,780|evalf,tmp/route_check_end.sk|goto,38.2,3.0,7500|untilmap,M396,8500")
    first=r'''
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M396" || p.x<66.8 || p.z<11.0 || p.z>13.0 || p.y>3.5)
    throw Exception("The party could not walk under the Yotomo cave roof");
printf("YOTOMO walked beneath the cave roof\n");
'''
    second=r'''
::rpgstage.encinc=0.0;
if(::rpgstage.mapid!="M397" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(85))
    throw Exception("The pigeon cave or its deeper exit is missing");
printf("YOTOMO pigeon cave reached\n");
'''
    marks=("YOTOMO walked beneath the cave roof","BOT reached M397","YOTOMO pigeon cave reached","BOT reached M396")
elif kind=="yotomo-vat":
    mid,x,z,flags="M397",84.2,43.4,"G967,G968,G969,G972,G978,G979,G980,G981"
    path=("wait,750|evalf,tmp/route_check_start.sk|goto,84.2,49.0,7500|untilmap,M398,8500|"
          "wait,750|evalf,tmp/route_check_end.sk|goto,61.2,3.0,7500|untilmap,M397,8500")
    first=r'''
::rpgstage.encinc=0.0;
if(::rpgstage.mapid!="M397" || !::rpgstage.getEvent(85))
    throw Exception("The vat chamber approach is missing");
printf("YOTOMO passage to the vat chamber present\n");
'''
    second=r'''
if(::rpgstage.mapid!="M398" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(85))
    throw Exception("The vat chamber or its return exit is missing");
printf("YOTOMO vat chamber reached\n");
'''
    marks=("YOTOMO passage to the vat chamber present","BOT reached M398","YOTOMO vat chamber reached","BOT reached M397")
elif kind=="iuchi-gate":
    mid,x,z,flags="M399",81.35,28.3,"G1001,G1002,G1004,G1006,G1007,G1008,G1009,G1010,G1021"
    path=("wait,830|evalf,tmp/route_check_start.sk|wait,1050|answer,0|goto,81.35,34.2,8500|untilmap,M400,8500|"
          "wait,800|evalf,tmp/route_check_end.sk|goto,6.2,13.3,9500|goto,6.2,10.0,7500|untilmap,M399,8500")
    first=r'''
local doors=::rpgstage.rtEnvironmentKit.townDoors;
if(length(doors)!=1 || doors[0][2]>.02)
    throw Exception("The tower gate is visible as open before the unlock flag");
printf("IUCHI tower gate starts closed\n");
::rpgvar["G998"]=true;
'''
    second=r'''
if(::rpgstage.mapid!="M400" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(2))
    throw Exception("The tower hall or staircase is missing");
printf("IUCHI tower gate opens into the hall\n");
'''
    marks=("IUCHI tower gate starts closed","BOT reached M400","IUCHI tower gate opens into the hall","BOT reached M399")
elif kind=="iuchi-stairs":
    mid,x,z,flags="M400",8.5,14.0,"G994,G998,G999,G1000,G1001,G1002,G1021"
    path=("wait,750|evalf,tmp/route_check_start.sk|goto,32.2,17.5,10000|untilmap,M401,8500|"
          "wait,650|evalf,tmp/route_check_start.sk|goto,32.2,17.5,10000|untilmap,M402,8500|"
          "wait,650|evalf,tmp/route_check_end.sk|goto,6.2,10.1,7500|untilmap,M401,8500|"
          "wait,650|evalf,tmp/route_check_start.sk|goto,6.2,11.0,9500|untilmap,M400,8500")
    first=r'''
::rpgstage.encinc=0.0;
if(!::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(2)) throw Exception("The tower stair is missing");
'''
    second=r'''
if(::rpgstage.mapid!="M402" || !::rpgstage.rtEnvironmentKit || !::rpgstage.getEvent(4))
    throw Exception("The upper room or its story scene is missing");
printf("IUCHI tower upper room reached\n");
'''
    marks=("BOT reached M401","BOT reached M402","IUCHI tower upper room reached","BOT reached M400")
elif kind=="iuchi-woods":
    mid,x,z,flags="M399",154.1,25.8,"G994,G998,G999,G1000,G1001,G1002,G1004,G1006,G1007,G1008,G1009,G1010,G1021"
    path=("wait,750|evalf,tmp/route_check_start.sk|goto,160.8,26.2,9500|untilmap,M403,8500|"
          "wait,750|evalf,tmp/route_check_end.sk|goto,-.55,25.0,11000|untilmap,M399,8500")
    first=r'''
::rpgstage.encinc=0.0;
'''
    second=r'''
if(::rpgstage.mapid!="M403" || !::rpgstage.rtEnvironmentKit ||
   length(::rpgstage.rtEnvironmentKit.waterTextures)!=32 || !::rpgstage.getEvent(2))
    throw Exception("The brook or clearing event is missing");
printf("IUCHI brook and Daiyu clearing reached\n");
'''
    marks=("BOT reached M403","IUCHI brook and Daiyu clearing reached","BOT reached M399")
elif kind=="iuchi-camp-road":
    mid,x,z,flags="M399",81.4,8.3,"G994,G998,G1000,G1001,G1002,G1004,G1006,G1007,G1008,G1009,G1010,G1021"
    path=("wait,690|evalf,tmp/route_check_start.sk|goto,81.4,.15,8500|untilmap,M404,8500|"
          "wait,700|goto,80.4,33.7,9500|evalf,tmp/route_check_end.sk|"
          "goto,80.4,55.6,10000|untilmap,M399,8500")
    first=r'''
::rpgstage.encinc=0.0;
'''
    second=r'''
local p=::rpgstage.player3d.pos;
if(::rpgstage.mapid!="M404" || p.z>17.2 || !::rpgstage.rtEnvironmentKit)
    throw Exception("The northern approach did not lead into the main camp");
printf("IUCHI reached the camp from the star field\n");
'''
    marks=("BOT reached M404","IUCHI reached the camp from the star field","BOT reached M399")
elif kind in ("iuchi-mine-mouth","iuchi-mine-gallery","iuchi-mine-deep"):
    flags="G994,G998,G999,G1000,G1001,G1002,G1004,G1006,G1007,G1008,G1009,G1010,G1021"
    mid,dest,x,z,goal,back={
        "iuchi-mine-mouth": ("M404","M405",143.8,28.4,"159.1,28.4","36.2,3.0"),
        "iuchi-mine-gallery": ("M405","M406",86.4,43.4,"86.4,49.0","62.2,3.0"),
        "iuchi-mine-deep": ("M406","M407",86.4,43.4,"86.4,49.0","56.2,3.0"),
    }[kind]
    approach="|goto,153.4,28.4,7800" if kind=="iuchi-mine-mouth" else ""
    path=(f"wait,710{approach}|evalf,tmp/route_check_start.sk|goto,{goal},8500|untilmap,{dest},8500|"
          f"wait,760|evalf,tmp/route_check_end.sk|goto,{back},8500|untilmap,{mid},8500")
    first=r'''
::rpgstage.encinc=0.0;
if(!::rpgstage.rtEnvironmentKit) throw Exception("The mine approach is missing");
'''
    if kind=="iuchi-mine-mouth":
        first+=r'''
local p=::rpgstage.player3d.pos;
if(p.x<76.1 || p.y>3.5 || p.z<13.7 || p.z>14.9)
    throw Exception("The party did not pass under the mine roof on foot");
printf("IUCHI walked under the mine roof\n");
'''
    second=f'''
::rpgstage.encinc=0.0;
if(::rpgstage.mapid!="{dest}" || !::rpgstage.rtEnvironmentKit)
    throw Exception("The mine destination is missing");
printf("IUCHI mine destination reached\\n");
'''
    marks=(f"BOT reached {dest}","IUCHI mine destination reached",f"BOT reached {mid}")
    if kind=="iuchi-mine-mouth":
        marks=("IUCHI walked under the mine roof",*marks)
else:
    assert kind=="bridge"
    mid,x,z,flags="M171",68.5,20.0,"G242"
    path=("wait,700|goto,73.0,20.0,6000|evalf,tmp/route_check_start.sk|"
          "goto,92.2,20.0,11000|evalf,tmp/route_check_end.sk")
    first=r'''
if(::rpgstage.mapid!="M171" || ::rpgstage.player3d.pos.x<35.7)
    throw Exception("The west bridge approach was unreachable");
printf("CHASM west bank %.2f\n", ::rpgstage.player3d.pos.x);
'''
    second=r'''
if(::rpgstage.mapid!="M171" || ::rpgstage.player3d.pos.x<45.4 || ::rpgstage.player3d.pos.y<1.8)
    throw Exception("The party could not cross the actual rope bridge");
printf("CHASM east bank %.2f\n", ::rpgstage.player3d.pos.x);
'''
    marks=("CHASM west bank","CHASM east bank")

scripts=list(zip(
    (profile/"tmp/route_check_start.sk",profile/"tmp/route_check_end.sk"),(first,second),
))
log=Path(__file__).resolve().with_name(f"native-{kind}-route.log")
try:
    for file,data in scripts:
        file.write_text(data,encoding="utf8")
    args=[str(profile/"rpgcobo.exe"),"-testplay","-map",mid,playbot.start_pos(mid,x,z),
          "-rtfast","-rtvar",flags,"-rtlead",lead,*extra_args,"-rtbot",path]
    with log.open("w",encoding="utf8") as output:
        proc=subprocess.Popen(args,cwd=profile,stdout=output,stderr=subprocess.STDOUT)
        try:
            until=time.monotonic()+62.
            while proc.poll() is None and time.monotonic()<until:
                if "BOT finished" in log.read_text(errors="replace"):
                    break
                time.sleep(.15)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
finally:
    for file,_ in scripts:
        file.unlink(missing_ok=True)
report=log.read_text(errors="replace")
assert all(mark in report for mark in (*marks,"BOT finished")),report[-4300:]
assert "threw" not in report and "NOT reached" not in report,report[-4300:]
if kind=="kamen":
    assert report.count("BOT reached M362")==2,report[-4300:]
if kind=="ojatara":
    assert report.count("BOT reached M369")==2,report[-4300:]
for line in report.splitlines():
    if any(mark in line for mark in marks):
        print(line)
