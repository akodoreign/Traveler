"""Stage a more open Shinomen Lava Trees route and landmark clearing."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates


HERE = Path(__file__).resolve().parent
FIRST = HERE.parent / "lava-trees"
sys.path.insert(0, str(FIRST))
import shinomen_lava_trees as first
from volcanic_route import BASALT, CRAGS, FLOW, FLAMES, NORMAL, ROOT

route = first.route
STAGE = HERE / "native_environment"
TEX = STAGE / "tex"
MID = first.MID
SOIL = "m450_lava_glade_soil"
LAND = "m450_lava_glade"
FIRE = LAND + "_melt"
PINE = "traveler_diorama_pine_coastal_daylight"
ROCK = "volcano_cave_crusted_lava_bank"
SHRINE = first.SHRINE
ROOTS = first.ROOTS
POOLS = (
    (41.63, 6.47, 1.44, .67), (44.59, 6.22, 1.02, .61),
    (44.18, 12.62, 2.14, .88), (48.33, 12.84, 1.77, .79),
    (51.32, 13.26, .85, .54),
)


def material(world, support, pools):
    cols, rows = 2048, 720
    z, x = np.meshgrid(np.arange(rows) * world.d / rows,
                       np.arange(cols) * world.w / cols, indexing="ij")
    pathway = gaussian_filter(support.astype(float), .84)
    path = map_coordinates(pathway, (z - .5, x - .5), order=1, mode="nearest")
    path = np.clip((path - .05)*1.29, 0., 1.)

    source = Image.open(route.SOURCE_IMAGES / "rock_01_diff_1k.jpg").convert("L")
    raw = np.asarray(source,dtype=float)
    broad = gaussian_filter(raw, 5.0, mode="wrap")
    detail = gaussian_filter(raw, 2.4, mode="wrap")
    relief = map_coordinates(.74*broad + .26*detail, (z*21.2, x*24.4), order=1, mode="grid-wrap")
    relief = np.clip((relief-np.median(relief)) / (2.7*np.std(relief)), -.62, .70)
    lobes = .47 + .19*np.sin(x*.57+z*.28) + .14*np.cos(z*.93-x*.31) + .14*np.sin(x*.20-z*.19)
    glades = 1.-.37*np.exp(-(((x-89)/17)**2+((z-20)/10)**2))
    moss = np.array([39., 93., 53.]) + (glades*lobes)[..., None]*[38., 51., 15.]
    dirt = np.array([146., 96., 58.]) + lobes[..., None]*[22., 16., 7.]
    char = np.zeros_like(path)
    for px,pz,a,b in pools:
        edge = np.exp(-(((x*.5-px)/(a+.58))**2+((z*.5-pz)/(b+.55))**2))
        char = np.maximum(char, edge)
    char *= 1.-path
    soil = moss*(1-path[..., None]) + dirt*path[..., None]
    soil = soil*(1-.84*char[..., None]) + np.array([66., 34., 53.])*char[..., None]*.84
    route.write_image(SOIL + ".png", soil*(1+.34*relief[..., None]))


def floor_height(x,z):
    # The ridge rises outside the old forest's main trail and side routes.
    shoulder = np.clip((z-18.9)/6.1,0.,1.)
    ridge = shoulder*shoulder*(3-2*shoulder)
    return 2.052 + ridge*(.58+.20*np.sin(x*.51)+.18*np.cos(x*.237))


def land(world, gm):
    gz,gx = np.indices(world.blk.shape)
    center = 16+np.rint(2.5*np.sin(np.clip(gx-gm.PAD_X,1,98)/9+4))+gm.PAD_BOTTOM
    dirt = (world.blk == gm.DIRT) & ((abs(gz-center)<3.5) | (gx<68) | (gx>111))
    support = (world.blk == gm.ROAD) | dirt
    pool_shape = np.full_like(gx, np.inf, dtype=float)
    for x,z,a,b in POOLS:
        d = ((gx*.5+.25-x)/a)**2 + ((gz*.5+.25-z)/b)**2
        pool_shape = np.minimum(pool_shape,d)
    wet = pool_shape<1.10
    assert not np.any(wet & support)
    material(world,support,POOLS)
    ground,lava = first.Geometry(),first.Geometry()

    def surface(x0,z0,x1,z1):
        points=[(x,z,float(floor_height(x,z))) for x,z in ((x0,z0),(x1,z0),(x1,z1),(x0,z1))]
        ground.quad(points,[(np.clip(x*2/world.w,.003,.997),np.clip(z*2/world.d,.003,.997))
                            for x,z,_ in points],SOIL)

    for x0,z0,x1,z1,_ in first.faces((~wet[:38]).astype(np.uint8)):
        surface(x0*.5,z0*.5,x1*.5,z1*.5)

    # Gentle shoulders fill the frame at the edges of the wooded map.
    end = world.w*.5
    bounds = [(-4.,0.,0.,19.), (end,0.,end+4.,19.),
              (-4.,19.,end+4.,30.), (-4.,-6.,end+4.,0.)]
    for x0,z0,x1,z1 in bounds:
        xs=np.linspace(x0,x1,round((x1-x0)/1.6)+1)
        zs=np.linspace(z0,z1,round((z1-z0)/1.1)+1)
        for z,pz in zip(zs[:-1],zs[1:]):
            for x,px in zip(xs[:-1],xs[1:]):
                surface(x,z,px,pz)

    for x,z,a,b in POOLS:
        theta = np.arange(37)*np.pi/18
        vectors = np.column_stack((np.cos(theta)*a,np.sin(theta)*b))
        vectors *= (1.+.09*np.sin(theta*3+x)+.07*np.sin(theta*5+z))[:,None]
        for i,(p,q) in enumerate(zip(vectors[:-1],vectors[1:])):
            outer = 2.115+.031*np.cos(i*.65+x)
            for lo,hi,y1,y2,key in ((.70,1.02,1.969,outer,CRAGS),
                                   (1.02,1.53,outer,2.057,BASALT)):
                points = [(x+r[0]*s,z+r[1]*s,y) for r,s,y in
                          ((p,lo,y1),(p,hi,y2),(q,hi,y2),(q,lo,y1))]
                route.quads(ground,points,key,1.6)
            points=[(x,z,2.074),(x+p[0]*.89,z+p[1]*.89,2.074),
                    (x+q[0]*.89,z+q[1]*.89,2.074),(x+q[0]*.89,z+q[1]*.89,2.074)]
            lava.quad(points,[(u/3.4,v/2.57) for u,v,_ in points],"lava")
    return ground,lava,support,wet


def grove(world,support):
    candidates = {(o["x"],o["z"]):o for o in world.objs if o["fbtype"]==20}
    # Sections of the forest beside the lava hearth stay open for the reveal.
    selected = []
    for x,z in sorted(candidates, key=lambda p: ((p[0]*89+p[1]*37)%197, p)):
        if z>=46 or support[z,x]:
            continue
        wx,wz=x*.5+.25,z*.5+.25
        if wx<14 or wx>62:
            if (x*7+z*11)%9>=4:
                continue
        if 39.<wx<52. and 4.8<wz<16.2:
            continue
        if 34.<wx<56. and wz<5. and ((x*7+z*13)%8!=0 or wz<2.5):
            continue
        if 20.5<wx<26. and 3.8<wz<8.1:
            continue
        if np.any(support[max(0,z-2):z+3,max(0,x-2):x+3]):
            continue
        space = 1.93 + .40*np.cos(wx*.22+wz*.49)
        if any((wx-a)**2+(wz-b)**2 < space*space for a,b,_,_ in selected):
            continue
        size=.60 + ((x*11+z*17)%14)*.032
        if 39.<wx<51. and wz<5.5:
            size*=.79
        selected.append((wx,wz,size,(x*7+z*13)*.37))
    pines=[]
    for i,(x,z,s,yaw) in enumerate(selected):
        row=[PINE,x,float(floor_height(x,z)),z,s,yaw]
        if i%7==0 or (39.<x<51. and 15.5<z<18.5):
            row.append(.024 + .006*(i%5))
        pines.append(row)
    return pines


def props(world,support):
    pines = grove(world,support)
    roots=[
        [ROOTS,42.45,2.066,5.79,.80,2.1],
        [ROOTS,45.39,2.069,6.10,.72,-.5],
        [ROOTS,43.26,2.056,13.33,1.01,3.4],
        [ROOTS,45.94,2.065,12.80,1.15,1.35],
        [ROOTS,49.12,2.063,13.58,.94,4.6],
        [ROOTS,51.20,2.063,14.04,.72,1.93],
    ]
    rocks=[
        [ROCK,39.48,2.045,5.93,.68,-.22],
        [ROCK,44.31,2.046,5.26,.62,1.29],
        [ROCK,41.34,2.048,13.34,.86,2.25],
        [ROCK,46.38,2.055,14.31,.86,.17],
        [ROCK,53.19,2.050,13.38,.87,3.22],
    ]
    for asset,x,_,z,*_ in [*roots,*rocks]:
        assert not support[int(z*2),int(x*2)], (asset,x,z)
    ornaments = [[SHRINE,23.75,2.054,6.75,.53,0.]]
    return [*pines,*roots,*rocks,*ornaments], (len(pines),len(roots),len(rocks))


def build(repo):
    live = repo/"_tools/rpgcobo-tool"
    original = route.read_json(FIRST/"receipt.json")
    catalog = route.read_json(live/route.CATALOG)
    catalog_hash = route.digest(json.dumps(catalog[MID],sort_keys=True).encode())
    world_hash = route.digest((live/f"project/data/mapdata/{MID}.bw").read_bytes())
    assert (catalog_hash,world_hash)==(original["catalog_hash"],original["world_hash"])
    gm = route.game_definition(repo)
    world,_ = gm.make(MID)
    assert world.w==152 and world.d==50 and np.all(world.hgt==3)
    TEX.mkdir(parents=True,exist_ok=True)
    route.STAGE = route.export_coast.STAGE = STAGE
    route.TEX = TEX
    ground,lava,support,wet = land(world,gm)

    retained = route.resource_files(FIRST/"native_environment",
        {"retained":{"placements":[[ROOTS],[SHRINE]],"magmaSpatter":[[]]}})
    approved = route.resource_files(live/ROOT,{"approved":{"placements":[[PINE]]}})
    reused_rocks = route.resource_files(HERE.parent/"native_environment",
        {"rocks":{"placements":[[ROCK]]}})
    textures = [BASALT+".png",CRAGS+".png",NORMAL,*(f"{FLOW}{i:02d}.png" for i in range(FLAMES))]
    for name in textures:
        relative = "tex/" + name
        retained[relative] = (FIRST/"native_environment"/relative).read_bytes()
    for name,data in {**retained, **approved, **reused_rocks}.items():
        (STAGE/name).write_bytes(data)

    texture = {SOIL:(SOIL+".png",.89), BASALT:route.MATERIALS[BASALT], CRAGS:route.MATERIALS[CRAGS]}
    first.export(LAND,ground,texture,normal_maps={BASALT:NORMAL,CRAGS:NORMAL},smooth_materials=(SOIL,CRAGS))
    first.export(FIRE,lava,{"lava":(FLOW+"00.png",.49)})
    placements, counts=props(world,support)
    pops=[[x,2.083,z,.47+.085*(i%3),i*1.49,.22+.13*(i%3)] for i,(x,z,_,_) in enumerate(POOLS)]
    glow=[[x,2.74,z,4.60,1.54,0xff913bff] for x,z,_,_ in POOLS]
    row={MID:dict(terrain=LAND,water=FIRE,waterMode="lava",hideStockScenery=True,placements=placements,
                  waterSequence={"prefix":FLOW,"frames":FLAMES,"seconds":15.2},
                  poolLights=glow,magmaSpatter=pops)}
    (STAGE/"index.json").write_text(json.dumps(row,separators=(",",":")),encoding="utf8")
    proof={"catalog_hash":catalog_hash,"world_hash":world_hash,
           "pine_count":counts[0],"root_count":counts[1],"rock_count":counts[2],
           "swaying":sum(len(p)>6 for p in placements),"pool_count":len(POOLS),
           "pool_cells":int(wet.sum()),"route_cells":int(support.sum()),
           "files":{name:route.digest(data) for name,data in route.resource_files(STAGE,row).items()}}
    (HERE/"receipt.json").write_text(json.dumps(proof,indent=2),encoding="utf8")


def stage(repo,profile):
    first.HERE=HERE
    first.STAGE=STAGE
    first.stage(repo,profile)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("build","stage"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("--profile",type=Path)
    args=parser.parse_args()
    if args.action=="build":
        build(args.repo.resolve())
    elif args.profile is None:
        parser.error("--profile is required for stage")
    else:
        stage(args.repo.resolve(),args.profile.resolve())
