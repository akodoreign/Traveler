"""Build and stage the trail's continuous terrain, brambles, and broken stone."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

from build_furnace import grid_surfaces
from build_hoshi_stall import box
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import convert_prop, save

HERE = Path(__file__).resolve().parent
STYLES = ("","waste_earth","waste_ash","waste_shale","waste_trail","waste_taint")
MATS = {style:(style+".png",.95) for style in STYLES[1:]}


def materials():
    raw = Image.open(HERE/"surface_sources/shadowlands_earth.png").convert("RGB")
    sample = periodic(raw,1024)
    gray = sample@[.24,.64,.12]
    relief = np.clip((gray-np.median(gray))/max(1.,np.ptp(np.percentile(gray,[8,92]))),-.72,.72)
    for key,tint,slope in (
        ("waste_earth",(79,65,72),.63),("waste_ash",(101,90,97),.61),
        ("waste_shale",(65,58,64),.79),("waste_trail",(113,89,79),.37),
        ("waste_taint",(67,46,48),.79),
    ):
        rgb = np.asarray(tint)*(1+relief[...,None]*slope)
        Image.fromarray(np.uint8(rgb.clip(0,255))).save(STAGE/"tex"/f"{key}.png")


def silhouette():
    wall = Geometry()
    for index in range(13):
        left = index*.46
        high = .86 + .20*np.sin(index*1.6)
        box(wall,(left,-.38,0.),(.45,.74,high),"waste_shale",1.02)
        if index in (0,1,4,8,11,12):
            box(wall,(left+.045,-.29,high),(.37,.55,.38+(index%2)*.15),"waste_shale",.71)
    export("shadowlands_broken_wall",wall,MATS)


def trail_surface(gm,world,name):
    block,height = world.blk,world.hgt.astype(int)
    tiles = np.where(block!=0,1,0)
    for style,codes in (
        (2,(gm.SL_ASH,)),(3,(gm.STONE,)),(4,(gm.ROAD,)),(5,(gm.TARSTAIN,gm.POPPYF,gm.EMBER)),
    ):
        tiles[np.isin(block,codes)] = style
    base,_ = grid_surfaces(tiles,height,STYLES,wall_style="waste_shale")
    export(name,base,MATS)
    return height


def fallen(gm,voxfile,world):
    source = {}
    for key,dimensions in (
        ("shadowlands_waymarker",(.58,.49,.95)),
        ("shadowlands_broken_cart",(2.02,1.12,1.07)),
    ):
        source[key] = save(*convert_prop(key,dimensions,38,lower=.025),voxfile)
        voxel_asset(key)
    heights = trail_surface(gm,world,"fallen_road_terrain")
    positions = (
        ("shadowlands_waymarker",14,14,1.,.13),("shadowlands_broken_cart",32,19,1.13,-.39),
        ("shadowlands_shards",12,21,.91,-.37),("shadowlands_thorns",16,28,1.14,.21),
        ("shadowlands_shards",20,31,.98,.57),("shadowlands_shards",42,28,1.08,1.12),
        ("shadowlands_thorns",35,34,.98,-.77),("shadowlands_thorns",46,34,.96,.32),
        ("shadowlands_shards",50,43,1.10,.13),("shadowlands_thorns",53,42,.86,.11),
        ("shadowlands_thorns",61,43,1.11,-.60),("shadowlands_shards",64,47,1.13,.7),
        ("shadowlands_shards",69,31,.94,.24),("shadowlands_thorns",74,24,1.10,1.09),
        ("shadowlands_shards",76,27,1.05,-1.0),("shadowlands_thorns",82,17,.97,.35),
        ("shadowlands_shards",89,15,1.03,1.36),("shadowlands_thorns",96,13,1.11,1.11),
        ("shadowlands_shards",101,23,1.25,.35),("shadowlands_thorns",106,20,.93,1.5),
        ("shadowlands_shards",107,22,1.0,-.62),
    )
    props = []
    for key,x,z,size,yaw in positions:
        bx,bz = x+gm.PAD_X,z+gm.PAD_BOTTOM
        y = (heights[bz,bx]+1)*.5
        props.append([key,bx*.5+.25,float(y),bz*.5+.25,size,yaw])
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    index["M458"] = dict(terrain="fallen_road_terrain",placements=props)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"fallen-road-layout.json").write_text(json.dumps({
        "trail":gm.FALLEN_TRAIL,"placements":len(props),"size":[world.w,world.d],"source":source,
    },indent=2),encoding="utf8")


def maze(gm,voxfile):
    source = {}
    for key,dimensions in (
        ("shadowlands_dead_cedar",(1.81,1.31,2.29)),
        ("shadowlands_ruined_shrine",(1.13,.94,1.29)),
    ):
        source[key] = save(*convert_prop(key,dimensions,40,lower=.027),voxfile)
        voxel_asset(key)
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    records = {}
    for k,mid in enumerate(gm.MAZE,1):
        world,_ = gm.make(mid)
        asset = f"{mid.lower()}_shifting_terrain"
        heights = trail_surface(gm,world,asset)
        positions = [
            ("shadowlands_ruined_shrine",11+k%3,35+k%2,.96,.21*k),
            ("shadowlands_dead_cedar",57-k%3,10+k%4,.98,.61*k),
            ("shadowlands_shards",25,21,.88,.76*k),
            ("shadowlands_shards",37,31,1.02,-.79),
            ("shadowlands_thorns",39,32,.95,.31),
            ("shadowlands_shards",52,26,1.15,.34*k),
            ("shadowlands_thorns",54,28,.94,.41),
            ("shadowlands_dead_cedar",27+k%3,44-k%3,.81,-.31*k),
            ("shadowlands_thorns",17,10,.83,.76),
            ("shadowlands_thorns",17,36,.81,-.42*k),
            ("shadowlands_ruined_shrine",66,41,.73,.83*k),
            ("shadowlands_shards",65,19,.77,-.34*k),
        ]
        positions.append((
            "shadowlands_dead_cedar" if k%2 else "shadowlands_ruined_shrine",
            59 if k%2 else 12, 38 if k%2 else 15,1.29,.52*k,
        ))
        props = []
        for key,x,z,size,yaw in positions:
            bx,bz = x+gm.PAD_X,z+gm.PAD_BOTTOM
            y = (heights[bz,bx]+1)*.5
            props.append([key,bx*.5+.25,float(y),bz*.5+.25,size,yaw])
        index[mid] = dict(terrain=asset,placements=props)
        records[mid] = {"landmark":positions[-1][0],"paths":gm.shifting_waste_paths(k),
                        "placements":len(props),"size":[world.w,world.d]}
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"shifting-waste-layout.json").write_text(json.dumps({
        "states":records,"source":source,
    },indent=2),encoding="utf8")


def main():
    sys.path.insert(0,str(Path(sys.argv[1])/"tools"))
    import gen_maps as gm
    import voxfile

    if "--maze" in sys.argv[2:]:
        maze(gm,voxfile)
        return
    if "--fallen" in sys.argv[2:]:
        world,_ = gm.make("M458")
        fallen(gm,voxfile,world)
        return
    m,events = gm.make("M460")
    assert hasattr(gm,"HIRUMA_TRAIL")
    materials()
    silhouette()
    source = {}
    for key,dimensions in (
        ("shadowlands_thorns",(1.39,1.26,1.33)),
        ("shadowlands_shards",(1.95,1.51,1.63)),
    ):
        source[key] = save(*convert_prop(key,dimensions,42,lower=.024),voxfile)
        voxel_asset(key)
    height = trail_surface(gm,m,"hiruma_road_terrain")
    props = []

    def place(key,x,z,size,yaw):
        x += gm.PAD_X
        z += gm.PAD_BOTTOM
        y = (height[z,x]+1)*.5
        props.append([key,x*.5+.25,float(y),z*.5+.25,size,yaw])

    for i,(x,z,key) in enumerate((
        (8,22,"shadowlands_thorns"),(18,12,"shadowlands_thorns"),(26,14,"shadowlands_shards"),
        (33,28,"shadowlands_shards"),(37,17,"shadowlands_thorns"),(42,26,"shadowlands_shards"),
        (39,38,"shadowlands_thorns"),(56,48,"shadowlands_thorns"),(63,43,"shadowlands_shards"),
        (67,36,"shadowlands_thorns"),(74,22,"shadowlands_shards"),(84,21,"shadowlands_shards"),
        (84,9,"shadowlands_thorns"),(90,15,"shadowlands_thorns"),(97,26,"shadowlands_thorns"),
        (103,32,"shadowlands_shards"),(104,36,"shadowlands_thorns"),(105,40,"shadowlands_thorns"),
        (107,39,"shadowlands_thorns"),(108,45,"shadowlands_thorns"),(99,46,"shadowlands_shards"),
        (109,48,"shadowlands_broken_wall"),(105,52,"shadowlands_shards"),
    )):
        size = (.73+(i%5)*.092) if key!="shadowlands_broken_wall" else .9
        place(key,x,z,size,(i*.71)%3.9 if key!="shadowlands_broken_wall" else -.61)
    gate_x = 107 + gm.PAD_X
    entries = []
    for z,sign in ((41,-1),(43,1)):
        bz = z+gm.PAD_BOTTOM
        entries.append({"x":gate_x*.5+.26,"y":(height[bz,gate_x]+1)*.5,"z":bz*.5+.25,
                        "size":1.18,"side":sign,"yaw":sign*.38})
    manifest = STAGE/"index.json"
    index = json.loads(manifest.read_bytes())
    index["M460"] = dict(terrain="hiruma_road_terrain",placements=props,brushReveal=entries)
    manifest.write_text(json.dumps(index,separators=(",",":")),encoding="utf8")
    (HERE/"hiruma-road-layout.json").write_text(json.dumps({
        "trail":gm.HIRUMA_TRAIL, "props":len(props), "brush":entries,
        "size":[m.w,m.d],"source":source,
    },indent=2),encoding="utf8")


if __name__=="__main__":
    main()
