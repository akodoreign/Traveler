"""Author the frost-scarred star field, gate, and three distinct tower floors."""

import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

from build_hoshi_stall import box, shop_board
from build_kaiu_kit import MATS as ARCHITECTURE, world_mesh
from build_kudo_rooms import frame
from export_coast import Geometry, STAGE, export, voxel_asset
from iuchi_worlds import TOWER, variant
from prepare_coast import periodic
from voxelize_coast import convert_prop, save


HERE = Path(__file__).resolve().parent
PALETTE = {
    "iuchi_frost": ("iuchi_frosted_meadow", (149, 169, 175), .040),
    "iuchi_meadow": ("iuchi_frosted_meadow", (68, 96, 81), .062),
    "iuchi_path": ("ojatara_earth_v2", (123, 96, 73), .038),
    "iuchi_char": ("iuchi_jade_wall_scan", (50, 42, 47), .049),
    "iuchi_slate": ("iuchi_jade_wall_scan", (53, 66, 80), .052),
    "iuchi_light_stone": ("dragon_clean_wall_plaster", (109, 117, 126), .034),
    "iuchi_plaster": ("dragon_clean_wall_plaster", (165, 151, 130), .027),
    "iuchi_beam": ("dragon_clean_lacquered_wood", (54, 39, 36), .031),
    "iuchi_oak": ("dragon_clean_lacquered_wood", (110, 73, 49), .036),
    "iuchi_board_a": ("dragon_clean_lacquered_wood", (96, 65, 51), .050),
    "iuchi_board_b": ("dragon_clean_lacquered_wood", (103, 73, 58), .050),
    "iuchi_indigo": ("ojatara_indigo_canvas", (41, 48, 87), .045),
    "iuchi_bronze": ("dragon_clean_wall_plaster", (108, 84, 54), .025),
    "iuchi_paper": ("dragon_clean_wall_plaster", (179, 160, 119), .021),
    "iuchi_iron": ("iuchi_jade_wall_scan", (35, 44, 51), .029),
}
MATS = {**ARCHITECTURE, **{key: (key + ".png", .93) for key in PALETTE},
        "iuchi_burned_star": ("iuchi_burned_star.png", .94)}
BASE_PROPS = (("iuchi_mountain_birch", (2.24, 1.90, 3.40), 47),)


def tint_texture(key, scan, color, contrast):
    image = Image.open(HERE / "surface_sources" / (scan + ".png")).convert("RGB")
    val = periodic(image, 512) @ [.26, .61, .13]
    broad = np.asarray(Image.fromarray(val.astype(np.uint8)).filter(ImageFilter.GaussianBlur(12.)))
    detail = val - broad
    grain = 1 + contrast * np.clip(detail / max(1., detail.std()), -2.2, 2.2)
    grain += .079 * (broad / max(1., np.median(broad)) - 1.)
    rgb = grain[..., None] * np.asarray(color)
    Image.fromarray(np.uint8(np.clip(rgb, 0., 255.))).save(STAGE / "tex" / (key + ".png"))


def textures():
    for key, config in PALETTE.items():
        tint_texture(key, *config)


def star_field_atlas(gm, world):
    detail = 12
    rows, columns = np.indices((world.d*detail,world.w*detail),sparse=True)
    x = columns / (detail*2) - (30+gm.PAD_X)*.5 - .25
    z = rows / (detail*2) - (25+gm.PAD_BOTTOM)*.5 - .25
    tiles = world.blk[rows//detail,columns//detail]
    grass = gaussian_filter((tiles==gm.GRASS3).astype(float),5.1)
    road = gaussian_filter((tiles==gm.DIRT).astype(float),3.2)
    road *= np.clip((-z-3.2)*2.5,0.,1.)
    direction, dist = np.arctan2(z, x), np.hypot(x, z)
    rays = 1 - np.abs(((direction / math.tau * 8) % 1) - .5) * 2
    edge = 1.00 + 3.25 * rays**2 + .108*np.sin(x*15+z*11) + .048*np.cos(x*33-z*19)
    burn = np.clip((edge - dist + .12) / .29, 0., 1.)
    core = np.exp(-((dist / .65)**2))
    rgb = np.array([149,169,175]) + grass[...,None]*[-46,-52,-52] + road[...,None]*[-26,-73,-102]
    rgb -= burn[...,None]*[104,125,130]
    rgb += core[...,None]*[28,9,4]
    grain = np.random.default_rng(399).normal(0, 1.85, dist.shape)
    Image.fromarray(np.uint8(np.clip(rgb + grain[..., None], 0., 255.))).save(STAGE / "tex/iuchi_burned_star.png")


def save_props(specs, voxfile):
    sources = {}
    for name, dims, samples in specs:
        candidate = convert_prop(name, dims, samples, lower=.025)
        sources[name] = save(*candidate, voxfile)
        voxel_asset(name)
    return sources


def ground_styles(gm):
    return {gm.SNOW:"iuchi_frost",gm.GRASS:"iuchi_meadow",gm.GRASS2:"iuchi_meadow",gm.GRASS3:"iuchi_meadow",
            gm.DIRT:"iuchi_path",gm.ROAD:"iuchi_path",gm.SL_GROUND:"iuchi_char",
            gm.STONE:"iuchi_slate",gm.STONEW:"iuchi_light_stone",gm.WOOD:"iuchi_oak",gm.DARKWOOD:"iuchi_beam",
            gm.PLASTER:"iuchi_plaster",gm.PLANK:"iuchi_board_a",gm.ROOF:"iuchi_indigo"}


def lift_floor(mesh, materials, height=.053):
    for face, material in zip(mesh.faces, mesh.materials, strict=True):
        vertices = np.array([mesh.vertices[i] for i in face])
        if material in materials and np.ptp(vertices[:,2]) < .0001 and np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])[2] > 0:
            for i in face:
                mesh.vertices[i] += [0.,0.,height]


def gate_and_fittings():
    jamb = Geometry()
    for x in (-.22,2.94):
        box(jamb,(x,-.19,0.),(.28,.58,3.40),"iuchi_beam")
        box(jamb,(x-.065,-.26,0.),(.40,.67,.31),"iuchi_slate")
    for y, depth, material in ((2.88,.62,"iuchi_beam"),(3.32,.76,"iuchi_beam"),(3.61,.86,"iuchi_indigo")):
        box(jamb,(-.27,-depth/2,y),(3.55,depth,.26),material)
    box(jamb,(-.50,-.51,3.79),(4.,1.02,.15),"iuchi_indigo")
    box(jamb,(-.31,-.37,3.92),(3.62,.74,.12),"iuchi_beam")
    export("iuchi_gate_frame",jamb,MATS)
    leaf = Geometry()
    for i in range(10):
        finish = "iuchi_oak" if i % 3 else "iuchi_board_a"
        box(leaf,(i*.286,-.035,.042),(.281,.104,2.79),finish,1.10)
    for y in (.38,1.37,2.45):
        for z in (-.076,.069):
            box(leaf,(-.013,z,y),(2.864,.047,.087),"iuchi_beam")
        box(leaf,(.016,-.102,y+.019),(.59,.026,.057),"iuchi_iron")
    box(leaf,(2.56,-.088,1.16),(.087,.041,.27),"iuchi_iron")
    export("iuchi_gate_leaf",leaf,MATS)

    lantern = Geometry()
    for x in (-.172,.139):
        for z in (-.172,.139):
            box(lantern,(x,z,.035),(.033,.033,.550),"iuchi_beam")
    box(lantern,(-.178,-.178,.066),(.356,.356,.048),"iuchi_indigo")
    box(lantern,(-.139,-.139,.108),(.278,.278,.45),"iuchi_paper")
    box(lantern,(-.183,-.183,.552),(.366,.366,.061),"iuchi_beam")
    box(lantern,(-.165,-.165,.609),(.33,.330,.032),"iuchi_indigo")
    export("iuchi_fitted_andon",lantern,MATS)

    rail = Geometry()
    for x in (-.56,.494):
        box(rail,(x,-.041,0.),(.066,.082,.98),"iuchi_beam")
    for y in (.29,.77):
        box(rail,(-.585,-.046,y),(1.176,.09,.063),"iuchi_oak")
    export("iuchi_wind_rail",rail,MATS)

    scroll = Geometry()
    box(scroll,(-.70,-.26,.294),(1.42,.53,.068),"iuchi_beam")
    for x in (-.62,.49):
        for z in (-.20,.12):
            box(scroll,(x,z,0.),(.112,.074,.31),"iuchi_beam")
    box(scroll,(-.40,-.20,.362),(.63,.36,.023),"iuchi_paper")
    for x in (-.407,.195):
        box(scroll,(x,-.206,.362),(.055,.371,.041),"iuchi_oak")
    box(scroll,(.40,-.015,.362),(.19,.123,.043),"iuchi_iron")
    export("iuchi_notes_table",scroll,MATS)
    shop_board("iuchi_tower_waymark","SHIRO","IUCHI","#3d435d")


def terrain(gm, world):
    styles = ground_styles(gm)
    mesh = world_mesh(gm, world, styles)
    if world.mid == "M399":
        star_field_atlas(gm,world)
        surfaces = {"iuchi_frost","iuchi_meadow","iuchi_path","iuchi_char"}
        lift_floor(mesh,surfaces,.071)
        for i, face in enumerate(mesh.faces):
            verts = np.asarray([mesh.vertices[k] for k in face])
            if mesh.materials[i] in surfaces and np.ptp(verts[:,2])<.0001 and 2.05 < verts[0,2] < 2.20:
                mesh.materials[i] = "iuchi_burned_star"
                mesh.uvs[i] = [(a*2/world.w,1.-b*2/world.d) for a,b,_ in verts]
    elif world.mid != "M878":
        for row in range(16):
            z = 5.0 + row*.344
            seams = [2.50, 5.65+row%3*.48, 9.20+row%4*.44, 13.18+row%3*.51, 17.50]
            for n,(a,b) in enumerate(zip(seams,seams[1:])):
                mat = "iuchi_board_a" if (row + n) % 3 else "iuchi_board_b"
                box(mesh,(a+.004,z,1.025),(b-a-.008,.337,.026),mat,1.28)
        for x in (2.0,17.5):
            box(mesh,(x,4.5,3.493),(.51,6.51,.16),"iuchi_beam",1.6)
        box(mesh,(2.0,10.5,4.012),(16.01,.515,.13),"iuchi_beam",1.6)
        for x in (3.48,5.98,8.48,10.98,13.48,15.98):
            frame(mesh,(x,10.445,1.48),1.55,1.55,"kaiu_shoji")
        if world.mid=="M400":
            box(mesh,(9.15,6.03,1.050),(1.50,4.13,.023),"iuchi_indigo",1.1)
            for x in (9.19,10.57):
                box(mesh,(x,6.074,1.074),(.034,4.04,.005),"iuchi_bronze",1.0)
        if world.mid=="M402":
            box(mesh,(12.986,7.486,1.034),(1.028,1.53,.487),"iuchi_indigo",.97)
            box(mesh,(13.06,8.61,1.518),(.85,.29,.14),"iuchi_paper",.95)
            box(mesh,(13.04,7.56,1.520),(.90,.82,.046),"iuchi_board_b",.95)
    else:
        box(mesh,(23.54,40.78,.524),(16.02,2.39,.021),"iuchi_indigo",1.7)
        for z in (40.84,43.07):
            box(mesh,(23.70,z,.546),(15.73,.046,.006),"iuchi_bronze",1.7)
    return mesh


def layout(gm, world):
    mid = world.mid
    props, lights, doors = [], [], []

    def place(asset,x,y,z,size=1.,yaw=0.,wind=0.):
        row = [asset,x,y,z,size,yaw]
        props.append(row+[wind] if wind else row)

    def lamp(x,y,z,size=1.):
        place("iuchi_fitted_andon",x,y,z,size)
        lights.append([x,y+.50*size,z,4.4,1.50])

    if mid == "M399":
        for x,z,size in ((7,7,.95),(15,28,.83),(42,28,1.17),(70,26,.94),(76,8,.92),(87,26,1.07),(103,8,1.02)):
            place("iuchi_mountain_birch",(x+gm.PAD_X)*.5+.25,2.02,(z+gm.PAD_BOTTOM)*.5+.25,size,x*.41,.022)
        for x,z in ((16,22),(22,19),(35,19),(48,20),(64,23),(74,24),(93,26),(101,23)):
            place("togashi_garden_stone",(x+gm.PAD_X)*.5+.25,2.04,(z+gm.PAD_BOTTOM)*.5+.25,.64+x%4*.11,x*.31)
        for x in (32.95,47.55):
            lamp(x,2.02,15.65,1.18)
        place("iuchi_tower_waymark",37.13,2.03,15.15,.93)
        doors.append(dict(x=(52+gm.PAD_X)*.5,y=2.,z=(30+gm.PAD_BOTTOM)*.5-.12,event=1,
                          models=("iuchi_gate_frame","iuchi_gate_leaf"),
                          alternateOpen=[gm.flag("G998"),gm.flag("G1000",False)]))
    elif mid == "M400":
        place("iuchi_notes_table",4.26,1.05,8.95,1.03,.1)
        place("iuchi_tower_screen",14.44,1.06,9.61,.91,-.18)
        for x,z in ((5.19,6.89),(12.62,10.02),(16.68,6.71)):
            lamp(x,1.057,z,.88)
    elif mid == "M401":
        place("iuchi_wind_rail",3.53,1.054,9.52,1.01,.08)
        place("iuchi_wind_rail",15.26,1.054,9.23,.98,1.54)
        place("iuchi_tower_screen",10.58,1.053,9.82,.85,.12)
        for x,z in ((3.21,7.70),(8.98,10.02),(16.92,7.09)):
            lamp(x,1.056,z,.91)
    elif mid == "M402":
        place("iuchi_tower_screen",6.01,1.05,10.01,.93,.1)
        place("iuchi_tower_screen",14.18,1.05,10.01,.93,-.13)
        place("iuchi_notes_table",11.86,1.05,9.91,.84,.03)
        for x,z in ((3.21,8.65),(8.13,10.12),(15.75,9.94)):
            lamp(x,1.055,z,.88)
    else:
        for x in (7.,14.,21.,31.,41.,50.,57.):
            place("iuchi_tower_screen",x,.506,45.39,1.18,.025)
        for x in (12.,24.,34.,44.,53.):
            lamp(x,.51,43.09,1.12)
    return {"placements":props,"poolLights":lights,"doors":doors}


def write_rows(identities, gm, mesh_for, place_for, materials, receipt, sources):
    path = STAGE / "index.json"
    index = json.loads(path.read_bytes())
    audit = {}
    for mid in identities:
        world, events = gm.make(mid)
        tag = mid.lower() + "_iuchi"
        export(tag,mesh_for(gm,world),materials)
        row = {"terrain":tag,**place_for(gm,world)}
        index[mid] = row
        audit[mid] = {"events":len(events.ev) if events else 0,"placements":len(row["placements"])}
    path.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/receipt).write_text(json.dumps({"maps":audit,"sources":sources},indent=2),encoding="utf8")


def main(repo):
    _,_,gm,_,_ = variant(repo)
    import voxfile

    textures()
    gate_and_fittings()
    sources = save_props((*BASE_PROPS,("iuchi_tower_screen",(1.35,.35,1.72),42)),voxfile)
    write_rows(TOWER,gm,terrain,layout,MATS,"iuchi-tower-layout.json",sources)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
