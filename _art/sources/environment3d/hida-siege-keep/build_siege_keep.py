"""Author the siege-night variant of the live Kyuden Hida keep."""
import argparse
from copy import copy, deepcopy
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK / "volcanic-route"))
from volcanic_route import game_definition
import export_coast
import diorama_trees
from build_hoshi_stall import box
from build_kaiu_kit import world_mesh
from export_coast import Geometry, export
from publish_castle_gates import CATALOG, INDEX, RUNTIME, hash_data, publish, require, resource_files
from publish_verified_visual_maps import plan


STAGE = HERE / "native_environment"
RECEIPT = HERE / "receipt.json"
TEX = STAGE / "tex"
SCANS = WORK / "coast-kit/surface_sources"
RENDERS = Path("project/resource/renderset.json")
FLOORS = ("M501", "M502", "M503")
ARENA = "M816"
STAIR_FRAME = "hida_siege_stair_frame"
STAIR_LEAF = "hida_siege_stair_leaf"
LANTERN = "castle_kaiu_lantern"
ANDON = "castle_paper_andon"
TABLE = "castle_council_table"
CHEST = "castle_lacquer_supply_chest"
SCROLLS = "castle_scroll_stack"
BENCH = "hida_cell_cedar_bench"
PROPS = {
    "tray": ("hida_siege_serving_tray", (.63,.25,.44)),
    "cabinet": ("hida_siege_archive_cabinet", (1.26,.93,.57)),
}
COLORS = {
    "cedar": ((89, 40, 37), .34, .86),
    "plank": ((116, 61, 42), .37, .80),
    "iron": ((36, 42, 64), .17, .64),
    "stone": ((41, 61, 100), .32, .91),
    "paper": ((224, 178, 118), .11, .94),
    "plaster": ((114, 152, 180), .17, .91),
    "indigo": ((22, 58, 125), .19, .94),
    "weave": ((40, 95, 128), .24, .94),
    "linen": ((168, 148, 116), .18, .96),
    "red": ((153, 32, 42), .12, .82),
    "gold": ((200, 126, 46), .16, .68),
}
MATERIALS = {key: (f"hida_siege_{key}.png", spec[2]) for key, spec in COLORS.items()}
NORMAL = "hida_siege_cut_slate_normal.png"


def read_json(path):
    return json.loads(path.read_bytes())


def write_image(path, values):
    Image.fromarray(np.uint8(np.clip(values, 0, 255))).save(path)


def detail(path, smooth=2.5):
    raw = np.asarray(Image.open(path).convert("L").resize((768, 768)), dtype=float)
    low = gaussian_filter(raw, 8.4, mode="wrap")
    signal = low + .60 * (gaussian_filter(raw, smooth, mode="wrap") - low)
    return np.clip((signal - np.median(signal)) / (2.0 * max(1, signal.std())), -.90, 1.)


def textures(live_assets):
    stone = detail(SCANS / "rock_01_diff_1k.jpg")
    wood = detail(live_assets / "tex/castle_hida_floor.png", 1.6)
    woven = detail(live_assets / "tex/tea_tatami.png", 2.9)
    y, x = np.indices(stone.shape, dtype=float)
    fiber = .46 * np.sin(x * .24 + .89 * np.sin(y * .015)) + .25 * woven
    for key, (pigment, strength, _) in COLORS.items():
        pattern = wood if key in ("cedar", "plank", "red") else fiber if key in (
            "indigo", "weave", "linen", "paper") else stone
        if key == "plank":
            seam = np.minimum((y % 128) / 4., 1.) * np.minimum((127 - y % 128) / 4., 1.)
            cut = (x + (np.floor(y / 128) % 3) * 159) % 384
            seam *= np.minimum(cut / 5., 1.) * np.minimum((383 - cut) / 5., 1.)
            pattern = pattern - .95 * (1. - seam)
        write_image(TEX / MATERIALS[key][0], np.asarray(pigment) * (1. + strength * pattern[..., None]))
    normal = np.asarray(Image.open(SCANS / "rock_01_nor_gl_1k.jpg").convert("RGB"), dtype=float) / 127.5 - 1.
    normal = gaussian_filter(normal, (3.0, 3.0, 0), mode="wrap")
    normal[..., :2] *= .64
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1.e-8)
    write_image(TEX / NORMAL, (normal + 1.) * 127.5)


def tile_styles(gm):
    return {gm.STONE: "stone", gm.STONEW: "stone", gm.KAIU: "stone",
            gm.WOOD: "cedar", gm.DARKWOOD: "cedar", gm.PLANK: "plank",
            gm.PLASTER: "plaster", gm.SHOJI: "paper", gm.TORII: "red",
            gm.ROOF: "iron", gm.TATAMI: "weave", gm.MATTING: "indigo", gm.FUTON: "linen"}


def stairs_geometry():
    frame, leaf = Geometry(), Geometry()
    for x in (0., 2.94):
        box(frame, (x, -.18, 0.), (.21, .45, 2.63), "cedar", 1.6)
        box(frame, (x - .03, -.22, .0), (.27, .51, .16), "stone", .65)
        box(frame, (x - .015, -.197, 2.24), (.24, .47, .17), "red", .95)
        box(frame, (x + .02, -.195, .32), (.166, .48, .063), "gold", .85)
    box(frame, (-.12, -.23, 2.53), (3.39, .54, .25), "cedar", 2.6)
    box(frame, (-.04, -.231, 2.60), (3.22, .049, .075), "red", 1.9)
    box(frame, (.22, -.112, .007), (2.72, .24, .022), "stone", 1.9)
    box(leaf, (.137, -.073, .051), (2.735, .128, 2.394), "cedar", 1.7)
    for x in (.214, 1.44, 2.653):
        box(leaf, (x, -.097, .08), (.063, .188, 2.33), "red", 1.25)
    for y in (.59, 1.39, 2.27):
        box(leaf, (.162, -.112, y), (2.69, .042, .076), "iron", 1.20)
    box(leaf, (2.438, -.159, 1.07), (.13, .064, .282), "iron", .64)
    for y in (1.07, 1.29):
        box(leaf, (2.435, -.171, y), (.136, .07, .038), "gold", .60)
    export(STAIR_FRAME, frame, MATERIALS, normal_maps={"stone": NORMAL})
    export(STAIR_LEAF, leaf, MATERIALS)


def shoji(geo, x, z, y, width, height):
    # Face the playable side of the retained shoji collision wall.
    for px in (x, x + width - .085):
        box(geo, (px, z - .039, y), (.087, .061, height), "cedar", 1.28)
    pieces = max(1, round(width / 1.35))
    for n in range(1, pieces):
        p = x + width * n / pieces
        box(geo, (p, z - .040, y), (.039, .063, height), "cedar", 1.28)
    for h in (0., .27 * height, .66 * height, height - .058):
        box(geo, (x, z - .038, y + h), (width, .069, .058), "cedar", 1.45)
    box(geo, (x + .08, z - .040, y + .08), (width - .16, .020, .20 * height), "indigo", 1.8)


def stairs_decor(geo, world):
    # The side posts follow the actual rise of the original stone/wood flights.
    for xx in (43.72, 47.08):
        for bz in (51, 53, 55, 58):
            y = (int(world.hgt[bz, 91]) + 1) * .5
            box(geo, (xx, bz * .5 + .04, y), (.126, .126, .89), "cedar", 1.3)
            box(geo, (xx - .019, bz * .5 + .023, y + .84), (.166, .16, .083), "gold", .87)
        a, b = (5.5, 8.)
        for yoff in (.57, .88):
            points = [(xx, 25.58, a + yoff), (xx + .12, 25.58, a + yoff),
                      (xx + .12, 28.15, b + yoff), (xx, 28.15, b + yoff)]
            geo.quad(points, [(0,0),(0,.12),(2.57,.12),(2.57,0)], "cedar")


def edged_mat(geo, x, z, width, depth):
    box(geo, (x, z, 5.020), (width, depth, .021), "weave", 2.25)
    for p in (x, x + width - .067):
        box(geo, (p, z, 5.041), (.065, depth, .014), "indigo", 1.2)
    for p in (z, z + depth - .064):
        box(geo, (x, p, 5.041), (width, .062, .014), "indigo", 1.2)


def bedding(geo, x, z):
    box(geo, (x, z, 5.046), (1.0, 1.71, .113), "linen", 1.22)
    box(geo, (x + .022, z + .39, 5.156), (.955, 1.29, .046), "indigo", 1.41)
    box(geo, (x + .034, z + .42, 5.202), (.93, .14, .014), "red", 1.2)
    box(geo, (x + .125, z + .088, 5.155), (.72, .27, .105), "paper", .67)


def bookcase(geo, x, z):
    for u in (x, x + 2.26):
        box(geo, (u, z, 5.019), (.14, .65, 1.76), "cedar", 1.40)
    for y in (5.09, 5.49, 5.95, 6.46):
        box(geo, (x+.126,z+.02,y),(2.14,.61,.091),"cedar",1.55)
    box(geo, (x+.14,z+.58,5.14),(2.11,.085,1.36),"indigo",1.75)
    for i in range(14):
        u = x + .21 + (i % 7) * .278
        y = 5.58 + (i // 7) * .46
        box(geo, (u,z+.14+(i%3)*.047,y),(.183,.36,.084+(i%3)*.068),
            ("paper","linen","red","indigo")[i%4], .71)


def keep(gm, world, catalog, daylight, level, decorative):
    clone = copy(world)
    # Replace visible furnishings. The original collision stays in the compiled world.
    furniture = {(x,z) for x in (20,70) for z in (20,42)}
    bedding_slots = {(x,z) for x in (20,28,70,78) for z in (26,48)}
    clone.objs = [obj for obj in world.objs if not (
        obj["t"] in ("fill","blk") and obj["y"] == 10 and
        ((obj["x"],obj["z"]) in furniture or (level == 1 and (obj["x"],obj["z"]) in bedding_slots)))]
    geom = world_mesh(gm, clone, tile_styles(gm))
    for obj in world.objs:
        if obj["t"] == "fill" and obj["blk"] == gm.SHOJI and obj["d"] == 1:
            shoji(geom, obj["x"]*.5, obj["z"]*.5-.018, obj["y"]*.5+.018, obj["w"]*.5, obj["h"]*.5-.027)
    props = []
    lights = []

    def lamp(x,z,grade=5.025,scale=1.,strength=3.4,style=ANDON):
        props.append([style,x,grade,z,scale,0.])
        lights.append([x,grade+.52*scale,z,4.2,strength,0xffa244ff])

    for x in (10.05,35.05):
        for z in (10.05,21.05):
            edged_mat(geom, x, z+.65, 4.41, 3.86)
            if level == 0:
                props.extend([[TABLE,x+.90,5.054,z+.20,.92,0.],
                              [CHEST,x+3.53,5.040,z+3.45,.80,1.57]])
                props.append([decorative["tray"],x+1.40,5.587,z+.29,.93,.09])
            elif level == 1:
                bedding(geom, x+.53, z+2.12)
                props.append([TABLE,x+.90,5.054,z+.20,.88,0.])
            else:
                bookcase(geom, x+.4, z+3.58)
                props.append([decorative["cabinet"],x+3.33,5.04,z+2.2,1.,0.])
                props.append([SCROLLS,x+.69,5.05,z+1.68,.87,.20])
            lamp(x+4.79,z+2.3)
    for x,z in ((21.32,13.8),(30.45,15.5),(43.55,23.05),(47.42,26.4)):
        lamp(x,z,style=LANTERN,scale=.73,strength=3.9)
    stairs_decor(geom, world)
    if level == 0:
        # Mark the real services landing without adding a return trigger.
        for px in (7.24, 8.97):
            box(geom,(px,16.32,5.023),(.155,.231,2.44),"cedar",1.36)
            box(geom,(px-.027,16.30,5.025),(.21,.27,.19),"stone",.84)
        box(geom,(7.18,16.27,7.36),(2.00,.35,.156),"cedar",1.55)
        lamp(7.03,17.42,scale=.84)
        props.append([BENCH,7.1,5.03,20.1,.76,1.57])
    else:
        for xx in (5.81,7.73):
            for bz in (12,14,16):
                y = (int(world.hgt[bz,13])+1)*.5
                box(geom,(xx,bz*.5+.10,y),(.103,.103,.83),"cedar",1.12)
        lamp(8.29,8.28,scale=.88)
        if level == 2:
            bedding(geom, 12.12, 22.45)
            bedding(geom, 13.53, 22.42)
    # Keep the original dais footprint. A low dark-blue hanging frames it.
    box(geom,(20.67,25.70,6.21),(.143,.186,2.12),"cedar",1.6)
    box(geom,(30.70,25.70,6.21),(.143,.186,2.12),"cedar",1.6)
    box(geom,(20.67,25.70,8.25),(10.17,.17,.144),"cedar",2.5)
    for i in (0,1,2):
        x = 22.2 + 2.79*i
        box(geom,(x,25.64,7.26),(1.77,.09,.984),"indigo",1.6)
        box(geom,(x,25.58,7.27),(1.77,.06,.092),"red",1.08)
        box(geom,(x+.37,25.58,7.63),(1.03,.05,.046),"gold",1.09)
    model = world.mid.lower() + "_hida_siege_rooms"
    export_terrain(model, geom)
    flags = (("G276",), ("G277","G278"), ())[level]
    stair = {"x":43.95,"y":5.02,"z":24.40,"event":2,"swing":79.,
             "models":[STAIR_FRAME, STAIR_LEAF]}
    if flags:
        # Only the same story requirements that remove the stair lock open its model.
        stair["event"] = -1
        stair["alternateOpen"] = [{"lvar":flag,"op":"==","rvar":True} for flag in flags]
    assert catalog["event"]["#2#"]["pos"] == [91,16,58,0]
    return {**daylight, "siege":{
        "terrain": model, "hideStockScenery": True, "placements": props,
        "poolLights": lights, "doors": [stair],
        "renderPreset": "rt_hd2d_hida_siege_keep",
    }}


def export_terrain(name, geometry):
    extras = {"cliff": MATERIALS["stone"], "path": MATERIALS["stone"]}
    materials = {**MATERIALS, **extras}
    export(name, geometry, materials, normal_maps={"stone": NORMAL, "cliff": NORMAL})


def battle_hall(gm, world):
    geom = world_mesh(gm, world, tile_styles(gm))
    placements, lamps = [], []
    for x in (19.50,23.25,27.05,37.15,40.85,44.76):
        z = 43.50
        shoji(geom,x,z,.58,2.20,2.12)
        box(geom,(x-.06,z+.003,2.61),(2.33,.40,.21),"cedar",1.7)
        placements.append([LANTERN,x+.56,.527,z-1.93,.90,0.])
        lamps.append([x+.56,1.24,z-1.93,4.70,3.65,0xffa342ff])
        box(geom,(x-.02,z+.098,3.02),(1.51,.11,.83),"indigo",1.33)
        box(geom,(x-.02,z+.044,3.025),(1.51,.047,.11),"red",1.07)
    for x in (18.2,46.45):
        for z in (25.4,33.3,39.4):
            placements.append([ANDON,x,.527,z,1.18,0.])
            lamps.append([x,1.07,z,3.65,1.68,0xffaa58ff])
    # The indigo dais border sits behind both original battle formations.
    box(geom,(21.50,42.81,.524),(22.70,.53,.073),"indigo",3.5)
    box(geom,(21.50,42.83,.598),(22.70,.04,.012),"red",2.3)
    name = "m816_hida_castle_hall"
    export_terrain(name, geom)
    return {"terrain":name,"placements":placements,"poolLights":lamps,"hideStockScenery":True}


def render_settings(raw):
    text=raw.decode("utf8")
    by_id={item["id"]:item for item in json.loads(text)["rendersets"]}
    entry=deepcopy(by_id["rt_hd2d_night"])
    entry.update(id="rt_hd2d_hida_siege_keep", name={"en":"Hida siege keep"})
    key=entry["envlights"][0]
    key.update(head=-42,pitch=48,power=490,color=-1767451649,scolor=-1767451649)
    key["shadow"].update(shadowdens=.44,shadowsoft=.33)
    entry["ibl"].update(ibldiff=415,iblspec=92,iblcolor=-1921188865)
    entry["fog"].update(density=.009,zoffs=18.5,color=910067542)
    entry["postfx"].update(bloompow=.16)
    if entry["id"] in by_id:
        require(entry == by_id[entry["id"]], "Live siege palette differs from the staged preset")
        return raw
    anchor='"rendersets": ['
    require(text.count(anchor)==1,"Cannot add to the render settings list")
    layer="\n".join("\t\t"+line for line in json.dumps(entry,indent="\t").splitlines())
    updated=text.replace(anchor,anchor+"\n"+layer+",",1)
    require(json.loads(updated)["rendersets"][0]==entry,"Invalid siege preset")
    return updated.encode()


def runtime_data(raw):
    anchor=b'    rtEnvironmentKit = def && this["scn"] ? EnvironmentKit(this,def) : null;'
    selection=b'    if(def && def["siege"] && ::rpgvar["G1644"]) def=def["siege"];'
    eol=b"\r\n" if b"\r\n" in raw else b"\n"
    edits=(
        (anchor,selection+eol+anchor,selection),
        (b'townDoors.append([door.event,leaf,null,door["alternateOpen"]]);',
         b'townDoors.append([door.event,leaf,null,door["alternateOpen"],door["swing"] || 52.0]);',
         b'door["swing"] || 52.0'),
        (b'local target=open ? 52.0*Math.DTOR : 0.0;',
         b'local target=open ? row[4]*Math.DTOR : 0.0;',
         b'local target=open ? row[4]*Math.DTOR : 0.0;'),
    )
    for original, updated, marker in edits:
        if marker not in raw:
            require(raw.count(original)==1,"EnvironmentKit launch or door binding changed")
            raw=raw.replace(original,updated,1)
    return raw


def build(repo):
    engine=repo/"_tools/rpgcobo-tool"
    catalog=read_json(engine/CATALOG)
    live=read_json(engine/INDEX)
    live_assets=(engine/INDEX).parent
    gm=game_definition(repo)
    export_coast.STAGE=STAGE
    diorama_trees.STAGE=STAGE
    TEX.mkdir(parents=True,exist_ok=True)
    textures(live_assets)
    stairs_geometry()
    generated={kind:name for kind,(name,_) in PROPS.items()}
    sources={name:diorama_trees.build_diorama_mesh(name,name,size,align_x=True,main_component=True)
             for name,size in PROPS.values()}
    rows, checks={}, {}
    for level,mid in enumerate(FLOORS):
        w,ev=gm.make(mid)
        for key,source in ev.ev.items():
            assert source["pos"]==catalog[mid]["event"][key]["pos"],(mid,key)
        base={key:value for key,value in live[mid].items() if key!="siege"}
        rows[mid]=keep(gm,w,catalog[mid],base,level,generated)
    w,_=gm.make(ARENA)
    rows[ARENA]=battle_hall(gm,w)
    cached_models={prop[0] for row in rows.values() for prop in row.get("siege",row)["placements"]}
    base_rows={mid:{k:v for k,v in live[mid].items() if k!="siege"} for mid in FLOORS}
    shared={**base_rows,"furnishing":{"placements":[[name] for name in sorted(cached_models-set(sources))]}}
    for relative,data in resource_files(live_assets, shared).items():
        if not (STAGE/relative).exists():
            (STAGE/relative).write_bytes(data)
    for mid in rows:
        checks[mid]={"catalog_hash":hash_data(json.dumps(catalog[mid],sort_keys=True).encode()),
                     "world_hash":hash_data((engine/f"project/data/mapdata/{mid}.bw").read_bytes())}
    for mid in ("M154","M155","M156"):
        recorded=json.dumps(catalog[mid]["event"])
        assert FLOORS[int(mid[-1])-4] in recorded,mid
    (STAGE/"index.json").write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf8")
    files=resource_files(STAGE,rows)
    RECEIPT.write_text(json.dumps({"maps":checks,"files":{k:hash_data(v) for k,v in files.items()},
                                  "sources":sources},indent=2),encoding="utf8")


def stage(repo,profile):
    from install_environment_rows import install
    import install_environment_rows
    engine=repo/"_tools/rpgcobo-tool"
    proof=read_json(RECEIPT)
    source=read_json(engine/CATALOG)
    target=read_json(profile/CATALOG)
    # The live story maps can come from a newer castle expansion than the test profile.
    for mid in (*proof["maps"],"M152","M153","M154","M155","M156","M541","M157","M504"):
        row=source[mid]
        if mid in proof["maps"]:
            require(hash_data(json.dumps(row,sort_keys=True).encode())==proof["maps"][mid]["catalog_hash"],mid)
        world=Path(f"project/data/mapdata/{mid}.bw")
        if (profile/world).read_bytes()!=(engine/world).read_bytes():
            (profile/world).write_bytes((engine/world).read_bytes())
        target[mid]=row
        bg=row.get("bg",{})
        if bg.get("type")=="tex":
            rel=Path("project")/bg["tex"].lstrip("/")
            (profile/rel).write_bytes((engine/rel).read_bytes())
    (profile/CATALOG).write_text(json.dumps(target,ensure_ascii=False,separators=(",",":")),encoding="utf8")
    for field,patch in ((RUNTIME,runtime_data),(RENDERS,render_settings)):
        (profile/field).write_bytes(patch((engine/field).read_bytes()))
    install_environment_rows.STAGE=STAGE
    install(profile,tuple(proof["maps"]))


def install_live(repo, profile):
    rows,before,updated,additions=plan(repo,profile,RECEIPT)
    require(set(rows)=={*FLOORS,ARENA},"Unexpected map scope")
    engine=repo/"_tools/rpgcobo-tool"
    for relative,patch in ((RUNTIME,runtime_data),(RENDERS,render_settings)):
        path=engine/relative
        before[path]=path.read_bytes()
        updated[path]=patch(before[path])
        require(updated[path]==(profile/relative).read_bytes(),f"Reviewed file differs: {relative}")
    publish(before,updated,additions)
    print(f"Installed the siege keep variant and castle hall arena across {len(rows)} maps.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    args=parser.parse_args()
    repo=args.repo.resolve()
    if args.action=="build":
        build(repo)
    elif args.profile is None or args.profile.resolve()==(repo/"_tools/rpgcobo-tool").resolve():
        parser.error("Provide a closed isolated profile")
    else:
        (stage if args.action=="stage" else install_live)(repo,args.profile.resolve())
