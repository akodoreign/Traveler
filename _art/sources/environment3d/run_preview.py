"""Run the native 4K map capture without changing display settings or saves."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
repo = Path(sys.argv[1])
target = sys.argv[2]
battle_maps = ("M808", "M810", "M811", "M812", "M813", "M817", "M818", "M862", "M863", "M864", "M865", "M866", "M867", "M868",
               "M861", "M869", "M870", "M871", "M872", "M873", "M874", "M875", "M876", "M877", "M878", "M879", "M880", "M881", "M882", "M883", "M884", "M894")
shifting_waste = ("M459", "M465", "M466", "M467", "M468", "M469")
hiruma_castle = ("M461", "M462", "M463")
march = ("M171","M172","M173","M174","M175","M176","M177")
kudo_rooms = ("M352","M353","M354")
kudo_marsh = ("M355","M356","M357","M358")
kensu = ("M359","M360","M361")
city = ("M362","M363","M364","M365","M366","M367")
ojatara = ("M368","M369","M370","M371","M372","M374","M375","M376","M377","M378")
scorpion = ("M345","M346","M347","M348","M349")
dragon = ("M379","M380","M381","M382","M383")
autumn = ("M387","M388","M389","M390","M391","M392","M393","M394","M395")
yotomo = ("M396","M397","M398")
iuchi = tuple(f"M{i}" for i in range(399,414))
cakon = ("M414","M415","M416","M417","M418","M419","M883","M884")
assert target in ("M100", "M101", "M102", "M103", "M104", "M105", "M120", "M121", "M122", "M123", "M124", "M125", "M130", "M131", "M132", "M133",
                  "M212", "M236", "M350", "M351", "M384", "M385", "M386", "M437", "M457", "M458", "M460", "M555", "M991",
                  *battle_maps, *shifting_waste, *hiruma_castle, *march, *kudo_rooms, *kudo_marsh, *kensu, *city, *ojatara,
                  *scorpion,*dragon,*autumn,*yotomo,*iuchi,*cakon)
wave_clip="--waves" in sys.argv[3:]
entrance="--entrance" in sys.argv[3:]
cave_entry="--cave-entry" in sys.argv[3:]
doors="--doors" in sys.argv[3:]
hiruma_open="--hiruma-open" in sys.argv[3:]
daylight="--daylight" in sys.argv[3:]
locked_gate="--locked-gate" in sys.argv[3:]
isolated = "--profile" in sys.argv[3:]
assert not cave_entry or target in ("M102","M105")
assert not doors or target=="M103"
label = "newcoast" + target.lower()
sys.path.insert(0, str(repo / "tools"))
import engine_lock
import playbot

tool = Path(sys.argv[sys.argv.index("--profile")+1]).resolve() if isolated else repo / "_tools/rpgcobo-tool"
stage = tool/"tmp/coast_environment_preview.sk" if isolated else repo / "tools/out/coast_environment_preview.sk"
script = "tmp/coast_environment_preview.sk" if isolated else "../../tools/out/coast_environment_preview.sk"
playbot.TOOL = str(tool)
(tool/"tmp/rt_shot").mkdir(parents=True, exist_ok=True)
stage.write_text((HERE / "preview_coast.sk").read_text(encoding="utf-8")
                 .replace("@MAP@", target).replace("@STAMP@", label)
                 .replace("@ENTRANCE@","true" if entrance else "false")
                 .replace("@DOORS@","true" if doors else "false")
                 .replace("@DAYLIGHT@","true" if daylight else "false")
                 .replace("@GATE_LOCKED@","true" if locked_gate else "false")
                 .replace("@WAVE_CLIP@","true" if wave_clip else "false"), encoding="utf-8")
start = "M202" if target in battle_maps else "M101" if target=="M100" else target
coords={"M100": (34,12),"M101": (14,36),"M102": (24,18), "M103": (84,23), "M104": (39,18),
        "M105": (24,18), "M123": (15,6), "M125": (12,6),"M130": (35,14),"M131": (41,18),"M132": (34,17),"M133": (32,16),
        "M202": (49,15), "M384": (37,23), "M385": (46,26), "M386": (53,15), "M437": (82,15)}
coords["M460"]=(103,41)
coords["M458"]=(18,15)
coords["M457"]=(52,23)
coords.update(dict.fromkeys(shifting_waste, (22,32)))
coords.update({"M461": (62,16), "M462": (42,17), "M463": (14,12)})
coords["M555"]=(45,44)
coords["M212"]=(4,15)
coords["M236"]=(4,15)
coords["M350"]=(52,15)
coords["M351"]=(45,16)
coords.update({"M352":(9,5),"M353":(7,5),"M354":(8,4)})
coords.update({"M355":(47,14),"M356":(68,12),"M357":(18,19),"M358":(37,18)})
coords.update({"M359":(58,16),"M360":(15,17),"M361":(83,16)})
coords.update({"M362":(14,17),"M364":(50,19),"M365":(60,25),"M366":(54,21)})
coords.update({"M368":(65,15),"M369":(39,18),"M371":(64,16),"M372":(38,16),
               "M374":(45,17),"M375":(45,18),"M377":(50,15),"M378":(40,14)})
coords.update({"M345":(36,13),"M347":(30,19),"M348":(52,15),"M349":(55,18)})
coords.update({"M379":(43,15),"M380":(61,16),"M382":(65,15),"M383":(34,12)})
coords.update({"M387":(57,17),"M389":(53,16),"M390":(82,14),"M391":(40,12),
               "M392":(51,21),"M393":(34,19),"M395":(30,8)})
coords.update({"M396":(82,17),"M397":(28,15),"M398":(35,15)})
coords.update({"M399":(31,22),"M403":(51,12),"M404":(55,15),"M405":(22,17),"M406":(36,20),"M407":(30,21)})
coords.update({"M408":(25,14),"M409":(26,8),"M410":(57,8),"M411":(4,7),"M412":(4,7)})
coords.update({"M413":(26,15),"M414":(25,11),"M415":(28,13),"M416":(59,15),"M417":(68,15)})
coords.update({"M418":(40,16),"M419":(37,15)})
coords.update({"M171":(42,16),"M172":(37,15),"M173":(35,15),"M174":(35,18),
               "M175":(36,20),"M176":(53,16),"M177":(73,16)})
if entrance or cave_entry:
    coords[target]=(84,18) if target=="M437" else (70,17)
if doors:
    coords[target]=(41,25)
location = {"M120":(21,12),"M121":(16,11),"M122":(16,11),"M123":(19,13),"M124":(19,11),
            "M125":(16,13),"M346":(13,13),"M363":(11,13),"M367":(12,12),"M370":(16,14),"M376":(13,14),
            "M381":(15,13),"M388":(16,13),"M394":(16,13),"M400":(18,14),"M401":(19,15),"M402":(17,14),
            "M408":(46,28),"M409":(49,17),"M410":(120,15),"M411":(7,14),"M412":(7,14)}.get(start)
if start=="M991":
    spawn="[8.5,1.0,5.4,0.0]"
else:
    if location is None:
        location=playbot.block(start,*coords[start])
    spawn=playbot.start_pos(start,*location)
steps = f"wait,1000|evalf,{script}"
if entrance:
    walk=(110,33) if target=="M437" else (96,34)
    steps=f"wait,750|goto,{walk[0]},{walk[1]},10000|evalf,{script}"
if cave_entry:
    steps="wait,750|goto,96,36,7500|untilmap,M130,5000"
if doors:
    steps+=f"|talkto,67,34|wait,1200|evalf,{script}"
if target=="M100":
    steps = f"wait,850|warp,M100,56,13|wait,1200|evalf,{script}"
if target in battle_maps:
    steps += f"|wait,2200|evalf,{script}"
lead="P105" if target in ("M350","M351","M861","M862","M863","M864","M865","M866","M867","M868","M869","M870","M871","M872",
                         *kudo_rooms,*kudo_marsh,*kensu,*city,*ojatara,*scorpion,*dragon) else "P102"
if target in (*autumn,*yotomo,*iuchi,"M875","M876","M877","M878","M879","M880","M881","M882"):
    lead="P106"
if target in cakon:
    lead="P107"
args = [str(tool/"rpgcobo.exe"),"-testplay","-map",start,spawn,
        "-rtfast","-rtlead",lead,"-rtparty","P101"]
if cave_entry:
    args+=["-rtvar","G024"]
elif doors:
    args+=["-rtvar","G054"]
elif target=="M100":
    args+=["-rtvar","G010"]
elif target=="M555":
    args+=["-rtvar","G425,G426"]
elif hiruma_open:
    args+=["-rtvar","G1215"]
elif target in hiruma_castle:
    args+=["-rtvar","G1216,G1217,G1218,G1219"]
elif target in march:
    args+=["-rtvar","G242,G243,G244,G245,G246,G249,G250,G254"]
elif target=="M351":
    args+=["-rtvar","G845"]
elif target in kudo_rooms:
    args+=["-rtvar","G845,G876,G861"]
elif target in kudo_marsh:
    args+=["-rtvar","G853,G854,G855,G856,G857,G859"]
elif target in kensu:
    args+=["-rtvar","G861,G879,G880,G881"]
elif target in city:
    flags="G879,G880,G881,G882,G898,G899,G903,G904,G917"
    args+=["-rtvar",flags if locked_gate else flags+",G891,G893"]
elif target in ojatara:
    args+=["-rtvar","G909,G918,G919,G924,G925,G926,G927,G929,G932,G933,G943"]
elif target=="M346":
    args+=["-rtvar","G831,G832,G837,G838"]
elif target in scorpion:
    args+=["-rtvar","G831,G832,G838,G839,G869,G840,G842,G843,G845"]
elif target in dragon:
    args+=["-rtvar","G944,G945,G946,G947,G948,G959"]
elif target in autumn:
    args+=["-rtvar","G967,G968,G969,G972,G973,G974,G977,G978,G979,G981,G982"]
elif target in yotomo:
    completed = ",G981" if target == "M398" else ""
    args+=["-rtvar","G967,G968,G969,G972,G973,G974,G977,G978,G979,G980" + completed]
elif target in cakon:
    flags="G1062,G1040,G1041,G1061,G1055,G1045,G1047"
    args+=["-rtvar",flags if locked_gate else flags+",G1043"]
elif target in iuchi:
    flags = "G994,G998,G999,G1001,G1002,G1004,G1006,G1007,G1008,G1009,G1010,G1021"
    if target in ("M408","M409","M410","M411","M412"):
        flags+=",G1022,G1025,G1027"
        if not locked_gate:
            flags+=",G1026"
    if target=="M413":
        flags="G1029,G1030,G1031,G1203"
    args+=["-rtvar",flags if target == "M399" else flags + ",G1000"]
else:
    args+=["-debuglv","20"]
args+=["-rtbot",steps]
log = HERE / f"{label}.log"
try:
    with log.open("w", encoding="utf-8") as output:
        if isolated:
            child_env = {**os.environ, "TEMP": str(tool/"os-temp"), "TMP": str(tool/"os-temp"),
                         "APPDATA": str(tool/"roaming"), "LOCALAPPDATA": str(tool/"local")}
            proc = subprocess.Popen(args, cwd=tool, env=child_env, stdout=output, stderr=subprocess.STDOUT)
            print(f"{tool.name} PID {proc.pid}", flush=True)
        else:
            proc = engine_lock.launch(args, cwd=tool, stdout=output, stderr=subprocess.STDOUT, tries=14)
        try:
            limit = time.monotonic()+46
            while time.monotonic()<limit and proc.poll() is None:
                if "BOT finished" in log.read_text(errors="replace"):
                    break
                time.sleep(.2)
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
    result=log.read_text(errors="replace")
    proof = "BOT reached M130" if cave_entry else "[LIVE COMBAT]"
    if "BOT finished" not in result or proof not in result or "Exception in thread" in result:
        raise RuntimeError(result[-5400:])
    if doors and ("storehouse-ajar.raw" not in result or "storehouse-locked.raw" not in result):
        raise RuntimeError(result[-5400:])
    if not cave_entry:
        playbot.convert_shots(label,str(HERE))
    for line in result.splitlines():
        if "[ENV]" in line or "[LIVE COMBAT]" in line or (cave_entry and "BOT reached M130" in line):
            print(line)
finally:
    stage.unlink(missing_ok=True)
