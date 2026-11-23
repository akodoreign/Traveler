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


if kind=="kudo":
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
          "-rtfast","-rtvar",flags,"-rtlead","P102","-rtbot",path]
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
