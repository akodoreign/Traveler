"""HD-2D look for RPG-Cobo maps: render presets + battle camera (idempotent).

- renderset "rt_hd2d_field"  : deep focus (far-only blur), soft bloom, warm key light, matte IBL, aerial fog
- renderset "rt_hd2d_battle" : same for battle maps (avoids the tilt-shift "miniature diorama" look)
- battle maps M800-M805: side-on camera from slightly above (Octopath battle framing) instead of the 45° diagonal
Tuning lives in FIELD / BATTLE / BATTLE_CAM below.
Run: python -E tools/gen_render.py
"""
import copy
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project")
BACKUP = os.path.join(HERE, "..", "_tools", "data_orig")


def s32(rgba):
    """0xRRGGBBAA -> signed int as stored in renderset.json."""
    return rgba - (1 << 32) if rgba & 0x80000000 else rgba


# Anti-"diorama" tuning: a miniature look comes from shallow focus + glossy plastic shading + no haze.
# Real-scale cues instead: deep focus (blur only the far distance), matte surfaces, aerial-perspective fog,
# crisp sun shadows. PBR fog colour: RGB + exponent byte (intensity = 1.1^(A-128)), not alpha.
FIELD = dict(postfx={"bloomblur": 3.5, "bloompow": 0.16, "bloomthrs": 0.8, "dofblur": 0.45, "dofrange": 40.0,
                     "dofz": 34.0},
             light=0xFFDCB0FF, power=1600, pitch=44, head=-35, iblspec=200, ibldiff=800,
             fog={"type": 3, "color": 0xC9D6E6C0, "density": 0.009, "zoffs": 18.0, "yplane": 0.0, "yfalloff": 0.12},
             ss={"aobias": 0.5, "aoexp": 1.1, "aopow": 0.7, "aoradius": 3.0, "gipow": 1.0, "gitype": 0})
BATTLE = dict(postfx={"bloomblur": 3.5, "bloompow": 0.16, "bloomthrs": 0.8, "dofblur": 0.45, "dofrange": 26.0,
                      "dofz": 22.0},
              light=0xFFDCB0FF, power=1600, pitch=40, head=-25, iblspec=200, ibldiff=800,
              fog={"type": 3, "color": 0xC9D6E6C0, "density": 0.011, "zoffs": 14.0, "yplane": 0.0, "yfalloff": 0.12},
              ss={"aobias": 0.5, "aoexp": 1.1, "aopow": 0.7, "aoradius": 3.0, "gipow": 1.0, "gitype": 0})
# Weather layers (SK3DWeather): drifting cloud shadows = Octopath's dappled light pools on field maps;
# warm floating motes in battle. Same dict shape as ::weatherlist entries (without id).
FIELD_WEATHER = {"type": "cloud", "spd": [0.025, 0.015], "cloudcol": 0x6E6A78FF, "scale": 120, "dens": 0.42,
                 "smooth": 0.22}
BATTLE_WEATHER = {"type": "particle", "spd": 0.08, "size": 0.12, "dens": 0.35, "col1": 0xFFE7A0FF, "col2": 0xFFF6D0FF}
NIGHT = dict(postfx={"bloomblur": 4.0, "bloompow": 0.28, "bloomthrs": 0.6, "dofblur": 0.45, "dofrange": 40.0,
                     "dofz": 34.0},
             light=0x8FA8E0FF, power=420, pitch=55, head=-60, iblspec=120, ibldiff=380,
             fog={"type": 3, "color": 0x2C3E5CB8, "density": 0.03, "zoffs": 10.0, "yplane": 0.0, "yfalloff": 0.1},
             ss={"aobias": 0.5, "aoexp": 1.1, "aopow": 0.9, "aoradius": 3.0, "gipow": 1.0, "gitype": 0})
NIGHT_MAPS = ["M100", "M105", "M099", "M203", "M204", "M214", "M224", "M240", "M260", "M268", "M274", "M275", "M286"]                # + Crane Ch1: the prologue, the night forest
# Caves: no sky; a low warm key light standing in for torches, dark brown haze, drifting dust.
CAVE = dict(postfx={"bloomblur": 4.0, "bloompow": 0.32, "bloomthrs": 0.55, "dofblur": 0.45, "dofrange": 40.0,
                    "dofz": 34.0},
            light=0xFFB878FF, power=520, pitch=68, head=-20, iblspec=70, ibldiff=260,
            fog={"type": 3, "color": 0x22180FBC, "density": 0.035, "zoffs": 10.0, "yplane": 0.0, "yfalloff": 0.1},
            ss={"aobias": 0.5, "aoexp": 1.2, "aopow": 1.0, "aoradius": 3.0, "gipow": 1.0, "gitype": 0})
CAVE_MAPS = ["M130", "M131", "M132", "M133", "M813", "M148", "M149", "M150", "M815", "M208", "M824", "M226", "M227", "M829", "M261"]  # + Goroso's cells
# Shadowlands (Crab Ch3): a low blood-orange sun through crimson haze, falling ash
SHADOW = dict(postfx={"bloomblur": 4.0, "bloompow": 0.3, "bloomthrs": 0.6, "dofblur": 0.45, "dofrange": 40.0,
                      "dofz": 34.0},
              light=0xFF8A5AFF, power=950, pitch=30, head=-50, iblspec=110, ibldiff=420,
              fog={"type": 3, "color": 0x4A1A12BE, "density": 0.024, "zoffs": 12.0, "yplane": 0.0, "yfalloff": 0.1},
              ss={"aobias": 0.5, "aoexp": 1.1, "aopow": 0.9, "aoradius": 3.0, "gipow": 1.0, "gitype": 0})
SHADOW_MAPS = ["M171", "M172", "M173", "M174", "M175", "M176", "M177", "M817", "M818"]
ASH_WEATHER = {"type": "particle", "spd": 0.05, "size": 0.10, "dens": 0.45, "col1": 0x8C7A74FF, "col2": 0xC0A090FF}
# Winter (Crab Ch2): falling snow over the field look
SNOW_MAPS = ["M140", "M141", "M147", "M814"]
SNOW_WEATHER = {"type": "particle", "spd": 0.10, "size": 0.11, "dens": 0.55, "col1": 0xFFFFFFFF, "col2": 0xE4EEFFFF}
CAVE_WEATHER = {"type": "particle", "spd": 0.04, "size": 0.09, "dens": 0.25, "col1": 0xC8A070FF, "col2": 0xE8C890FF}
NIGHT_WEATHER = {"type": "mist", "spd": [0.22, 0.1], "dens": 30, "scale": 50, "xscale": 3.0, "modspd": 0.1,
                 "mistcol": 0x8CA0C8FF}
BATTLE_CAM = {"fovy": 26, "hpb": [0, 16, 0], "viewport": 4.6, "yoffs": 0.5}   # framed for half-size cast
FIELD_MAPS = ["M000", "M001", "M002", "M003", "M005", "M101", "M102", "M103", "M104", "M140", "M141", "M147",
              "M200", "M201", "M202", "M205", "M209", "M210", "M211", "M216", "M212", "M213", "M215",
              "M220", "M221", "M222", "M223", "M225", "M228", "M235", "M242", "M241", "M250", "M251", "M252", "M254", "M255", "M256", "M266", "M267", "M269", "M270", "M271", "M272", "M273", "M276", "M281", "M282", "M283", "M284", "M285", "M287", "M288", "M289", "M291",
               "M292", "M293", "M294", "M297", "M298", "M299", "M301", "M302", "M303", "M304", "M307", "M309",
               "M310", "M311", "M312", "M314", "M315", "M318", "M319", "M320", "M321",
               "M322", "M323", "M325", "M326", "M333", "M334", "M335", "M336", "M337",
               "M340", "M341", "M343"]   # M000 = title backdrop; M200+ Crane Ch1
BATTLE_MAPS = ["M800", "M801", "M802", "M803", "M804", "M805", "M810", "M811", "M812", "M813", "M814", "M815", "M816",
               "M817", "M818", "M820", "M821", "M822", "M823", "M824", "M825", "M826", "M827", "M828", "M829", "M830", "M831", "M832", "M833", "M834", "M835", "M836", "M837", "M838", "M839", "M840", "M841", "M842", "M843", "M844", "M845", "M846", "M847", "M848", "M849", "M850", "M851", "M852", "M853", "M854", "M855", "M856", "M857", "M858", "M859", "M860"]
NIGHT_BATTLE_MAPS = ["M810", "M822", "M833"]                   # (M839: night fog hid the fear shades and Ianwa)                   # (M830 the storm deck: night fog hid Yosuke)


def weather(w):
    """Colours are stored as signed int32 like the rest of the project JSON."""
    return {k: (s32(v) if k.endswith(("col", "col1", "col2")) and isinstance(v, int) else v) for k, v in w.items()}


def make(base, rid, name, spec):
    r = copy.deepcopy(base)
    r["id"] = rid
    r["name"] = {"en": name, "ja": name}
    r["lock"] = False
    r["postfx"] = spec["postfx"]
    r["ss"] = spec["ss"]
    fog = dict(spec["fog"])
    fog["color"] = s32(fog["color"])
    r["fog"] = fog
    r["ibl"]["iblspec"] = spec["iblspec"]
    r["ibl"]["ibldiff"] = spec["ibldiff"]
    lt = r["envlights"][0]
    lt["shadow"]["shadowsoft"] = 0.2
    lt.update({"color": s32(spec["light"]), "scolor": s32(spec["light"]), "power": spec["power"],
               "pitch": spec["pitch"], "head": spec["head"]})
    return r


VIGNETTE = dict(strength=0.72, inner=0.48, topbottom=0.34, color=(18, 12, 10))


def make_vignette():
    """Octopath-style screen vignette (overlaid by the plugin between the 3D view and the UI)."""
    import numpy as np
    from PIL import Image
    w, h = 320, 180
    ys, xs = np.mgrid[0:h, 0:w]
    nx, ny = (xs + 0.5) / w * 2 - 1, (ys + 0.5) / h * 2 - 1
    r = np.sqrt((nx * 0.92) ** 2 + (ny * 1.0) ** 2)
    a = np.clip((r - VIGNETTE["inner"]) / (1.35 - VIGNETTE["inner"]), 0, 1) ** 1.7 * VIGNETTE["strength"]
    edge = np.clip(1 - np.abs(ny) * 1.0, 0, 1)
    a = np.clip(a + (1 - np.clip(edge / 0.28, 0, 1)) ** 2 * VIGNETTE["topbottom"], 0, 0.85)
    img = np.zeros((h, w, 4), np.uint8)
    img[..., :3] = VIGNETTE["color"]
    img[..., 3] = (a * 255).astype(np.uint8)
    out = os.path.join(PROJ, "resource", "efx", "rt_vignette.png")
    Image.fromarray(img, "RGBA").save(out)
    return out


def main():
    make_vignette()
    rpath = os.path.join(PROJ, "resource", "renderset.json")
    os.makedirs(BACKUP, exist_ok=True)
    rb = os.path.join(BACKUP, "renderset.json")
    if not os.path.exists(rb):
        shutil.copy(rpath, rb)
    rs = json.load(open(rb, encoding="utf-8"))
    base = next(r for r in rs["rendersets"] if r["id"] == "pbr_df-4-1-1")
    rs["rendersets"] = [r for r in rs["rendersets"] if not r["id"].startswith("rt_")]
    rs["rendersets"].append(make(base, "rt_hd2d_field", "HD-2D Field (Rokugan)", FIELD))
    rs["rendersets"].append(make(base, "rt_hd2d_battle", "HD-2D Battle (Rokugan)", BATTLE))
    rs["rendersets"].append(make(base, "rt_hd2d_night", "HD-2D Night (Rokugan)", NIGHT))
    rs["rendersets"].append(make(base, "rt_hd2d_cave", "HD-2D Cave (Rokugan)", CAVE))
    rs["rendersets"].append(make(base, "rt_hd2d_shadow", "HD-2D Shadowlands (Rokugan)", SHADOW))
    json.dump(rs, open(rpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")

    mpath = os.path.join(PROJ, "data", "map.json")
    m = json.load(open(mpath, encoding="utf-8"))   # gen_data.py owns map.json; run it before this script
    for k in FIELD_MAPS:
        if k not in m:
            continue
        m[k]["rsetid"] = "rt_hd2d_field"
        if k != "M000":
            m[k]["weather"] = weather(FIELD_WEATHER)
    for k in NIGHT_MAPS:
        if k in m:
            m[k]["rsetid"] = "rt_hd2d_night"
            m[k]["weather"] = weather(NIGHT_WEATHER)
    for k in BATTLE_MAPS:
        if k not in m:
            continue
        m[k]["rsetid"] = "rt_hd2d_battle"
        m[k]["camwork"] = dict(BATTLE_CAM)
        for mk in (m[k].get("marker") or {}).values():       # the battle camera itself is the *maincam marker
            if mk.get("name") == "*maincam":
                mk["viewport"], mk["hpb"], mk["yoffs"] = 8.0, [0, 20, 0], -0.4
            elif mk.get("name") == "*memberloc":             # lines closer together for the half-size cast
                mk["pos"][0] = 71
            elif mk.get("name") == "*enemyloc":
                mk["pos"][0] = 58
        m[k]["weather"] = weather(BATTLE_WEATHER)
    for k in NIGHT_BATTLE_MAPS:
        if k in m:
            m[k]["rsetid"] = "rt_hd2d_night"
            m[k]["weather"] = weather(NIGHT_WEATHER)
    for k in SNOW_MAPS:
        if k in m:
            m[k]["weather"] = weather(SNOW_WEATHER)
    for k in CAVE_MAPS:
        if k in m:
            m[k]["rsetid"] = "rt_hd2d_cave"
            m[k]["weather"] = weather(CAVE_WEATHER)
    json.dump(m, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    for k in SHADOW_MAPS:                                  # (a second pass: written after the cameras above)
        if k in m:
            m[k]["rsetid"] = "rt_hd2d_shadow"
            m[k]["weather"] = weather(ASH_WEATHER)
    json.dump(m, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=chr(9))
    print("render presets + cameras written")


if __name__ == "__main__":
    main()
