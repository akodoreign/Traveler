"""Build the Oracle switchback, crater shrine, and scripted battle backdrop."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

HERE = Path(__file__).resolve().parent
STAGE = HERE / "native_environment"
TEX = STAGE / "tex"
ART = HERE.parent / "coast-kit"
SOURCE_IMAGES = ART / "surface_sources"
MAPS = ("M442", "M443", "M896")
ROOT = Path("project/resource/native_environment")
CATALOG = Path("project/data/map.json")

sys.path.insert(0, str(ART))
import diorama_trees
import export_coast
import install_environment_rows
from build_furnace import grid_surfaces
from build_hoshi_stall import box
from export_coast import Geometry, export
from publish_castle_gates import resource_files

ASH = "oracle_volcanic_russet"
TREAD = "oracle_volcanic_stair"
FIRELINE = "oracle_volcanic_cinder"
BASALT = "oracle_volcanic_basalt"
CRAGS = "oracle_volcanic_crags"
STONE = "oracle_volcanic_foundation"
CEDAR = "oracle_volcanic_inkwood"
RED = "oracle_volcanic_lacquer"
COPPER = "oracle_volcanic_copper_roof"
NORMAL = "oracle_volcanic_basalt_normal.png"
FLOW = "oracle_volcanic_melt"
FLAMES = 32
LANTERN = "volcano_cave_bronze_lantern"
SHELF = "volcano_cave_crusted_lava_bank"
MARKER = "volcano_cave_rope_waymarker"
PROPS = (LANTERN, SHELF, MARKER, "magma_spatter")
MATERIALS = {
    ASH: (ASH + ".png", .86), TREAD: (TREAD + ".png", .84),
    FIRELINE: (FIRELINE + ".png", .86), BASALT: (BASALT + ".png", .88),
    CRAGS: (CRAGS + ".png", .79), STONE: (STONE + ".png", .89),
    CEDAR: (CEDAR + ".png", .94), RED: (RED + ".png", .78),
    COPPER: (COPPER + ".png", .76),
}


def read_json(path):
    return json.loads(path.read_bytes())


def digest(data):
    return sha256(data).hexdigest()


def write_image(name, pixels):
    Image.fromarray(np.uint8(np.rint(np.clip(pixels, 0, 255)))).save(TEX / name)


def game_definition(repo):
    source = repo / "tools/gen_maps.py"
    code = source.read_text(encoding="utf8")
    # Importing the map generator computes a roster report. Redirect its
    # one import-time output to this candidate folder.
    original = 'os.path.join(HERE, "_ladder_foes.json")'
    assert code.count(original) == 1
    code = code.replace(original, repr(str(HERE / "_ladder_foes.json")))
    sys.path.insert(0, str(source.parent))
    gm = ModuleType("gen_maps")
    gm.__file__ = str(source)
    sys.modules[gm.__name__] = gm
    exec(compile(code, str(source), "exec"), vars(gm))
    return gm


def make_palettes():
    sample = np.asarray(Image.open(SOURCE_IMAGES / "rock_01_diff_1k.jpg").convert("L"), dtype=float)
    broad = gaussian_filter(sample, 8.5, mode="wrap")
    medium = gaussian_filter(sample, 2.8, mode="wrap")
    relief = np.clip((broad + .42 * (medium - broad) - np.median(broad)) / sample.std(), -1.9, 1.9)
    palette = (
        (ASH, (85, 48, 49), .14), (TREAD, (150, 106, 77), .18),
        (FIRELINE, (80, 29, 43), .19), (BASALT, (62, 58, 94), .22),
        (CRAGS, (54, 56, 88), .25), (STONE, (104, 76, 89), .25),
        (CEDAR, (66, 36, 42), .20), (RED, (160, 48, 29), .17),
        (COPPER, (101, 62, 62), .20),
    )
    for key, color, strength in palette:
        write_image(key + ".png", np.asarray(color) * (1 + strength * relief[..., None]))

    normal = np.asarray(Image.open(SOURCE_IMAGES / "rock_01_nor_gl_1k.jpg").convert("RGB"), dtype=float)/127.5-1.
    normal = gaussian_filter(normal, (3.4, 3.4, 0), mode="wrap")
    normal[..., :2] *= .47
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-8)
    write_image(NORMAL, (1 + normal) * 127.5)


def make_lava():
    # Mid-scale convection carries the image. The animation advects those
    # folds rather than sprinkling moving fine speckles over the surface.
    diffuse = np.asarray(Image.open(SOURCE_IMAGES / "furnace_flow.png").convert("RGB").resize((512, 512)),
                         dtype=float)
    sample = gaussian_filter(diffuse @ [.51, .38, .11], 4.5, mode="wrap")
    sample -= np.median(sample)
    y, x = np.indices(sample.shape, dtype=float)
    u, v = x * np.pi/256., y * np.pi/256.
    curl = np.sin(3*u + 2*v + 1.5*np.sin(u-v)) + .38*np.sin(4*v-u + np.cos(u+v))
    edge = (np.cos(2*u-v+.98*np.cos(3*v)) + .6*np.sin(4*u+2*v)) * .24
    temp = np.clip(.65 + .25*curl + edge + sample/600, .06, 1.0)
    intensity = temp ** 1.24
    base = np.dstack((158.+97.*temp ** .46, 31.+204.*intensity, 9.+109.*temp ** 2.55))
    for frame in range(FLAMES):
        phase = np.pi * 2 * frame / FLAMES
        ax = (x+5*np.sin(v+phase)+3.5*np.cos(2*v-u+phase)) % 512
        az = (y+16*np.sin(u+phase)+7*np.cos(2*u-v-phase)) % 512
        pixels = np.dstack([map_coordinates(base[..., c], (az, ax), order=1, mode="grid-wrap")
                            for c in range(3)])
        pulse = .985 + .027*np.cos(v+phase)
        pixels[..., :2] *= pulse[..., None]
        write_image(f"{FLOW}{frame:02}.png", pixels)


def top(world, x, z):
    return (int(world.hgt[min(world.d-1, int(z*2)), min(world.w-1, int(x*2))]) + 1)*.5


def quads(geo, pts, style, rate=3.2):
    geo.quad(pts, [((x+.29*z)/rate, (z*.68+y)/rate) for x,z,y in pts], style)


def ridge(world, geo, rear, lower):
    # Shape the profile into connected cool basalt shoulders. The dry walk
    # stops well before the toe so the original support still owns traversal.
    count = world.w + 1
    x = np.linspace(0., world.w*.5, count)
    tail = world.d*.5 - rear
    offsets = np.array([-.52, .22, min(1.55,tail*.43), min(3.20,tail*.64), tail])
    for i, (a,b) in enumerate(zip(offsets, offsets[1:])):
        blend_a,blend_b = [(0.,.47),(.47,.89),(.89,1.05),(1.05,1.)][i]
        for j in range(count-1):
            shape = []
            for k,off,amount in ((j,a,blend_a),(j+1,a,blend_a),(j+1,b,blend_b),(j,b,blend_b)):
                u = x[k]
                wave = .53*np.sin(u*.48)+.29*np.cos(u*.91)+.34*np.sin(u*.224)
                normal = np.clip((tail-off)/(tail+.52),0.,1.)
                z = rear + off + wave*normal
                near = lower[min(k,world.w-1)]
                h = max(near+.85, top(world, u,max(0.,world.d*.5-.25)))
                varies = (.42*np.sin(u*.61)+.47*np.cos(u*.286)+.17*np.sin(u*1.91)) * amount
                shape.append((u,z,near+(h-near)*amount+varies))
            quads(geo,shape,CRAGS)
    for side, k in enumerate((0, count-1)):
        u = x[k]
        near = lower[min(k,world.w-1)]
        h = top(world,u,world.d*.5-.25)
        z = rear + offsets[0]
        pts = [(u,z,near),(u,world.d*.5,h),(u,world.d*.5,near-.5),(u,z,near-.5)]
        quads(geo,pts if side==0 else pts[::-1],CRAGS)


def crater_shrine(geo):
    # Match the stock 7 by 5 support and the roof ridge. The front entrance
    # reads as a shut devotional building on this route, which fits its
    # solid interior in the preserved world.
    x,z,y=22.,13.,3.50
    box(geo,(x-.06,z-.07,y),(3.62,2.63,.5),STONE,1.65)
    box(geo,(x+.03,z+.035,y+.5),(3.44,2.43,2.38),CEDAR,2.21)
    for col in (x+.08,x+.97,x+2.52,x+3.40):
        box(geo,(col-.065,z-.08,y+.46),(.13,.19,2.43),RED,.77)
    for depth in (z+.24,z+2.24):
        for col in (x-.07,x+3.47):
            box(geo,(col,depth,y+.48),(.15,.16,2.46),RED,.81)
    box(geo,(x+.995,z-.095,y+.54),(.995,.10,1.91),CEDAR,1.12)
    box(geo,(x+1.006,z-.13,y+.53),(.095,.052,1.91),RED,.90)
    box(geo,(x+1.918,z-.13,y+.53),(.095,.052,1.91),RED,.90)
    box(geo,(x+.88,z-.14,y+2.40),(1.23,.18,.14),RED,.98)
    for beam in (y+.57,y+2.82):
        box(geo,(x-.18,z-.11,beam),(3.87,.19,.16),RED,1.42)
    for side in (-1,1):
        roof_first = z+1.25+side*.015
        roof_last = z+1.25+side*1.72
        for i in range(13):
            a=x-.48+i*.343
            pts=[(a,roof_first,y+4.17),(a+.354,roof_first,y+4.17),
                 (a+.354,roof_last,y+2.88),(a,roof_last,y+2.88)]
            quads(geo,pts if side>0 else pts[::-1],COPPER,1.5)
            box(geo,(a,min(roof_last,roof_last+side*.04),y+2.81),(.365,.13,.115),CEDAR)
        trim = [(x-.50,roof_last,y+2.80),(x+3.98,roof_last,y+2.80),
                (x+3.98,roof_last,y+2.92),(x-.50,roof_last,y+2.92)]
        quads(geo,trim if side<0 else trim[::-1],RED)
    for i,u in enumerate((x+.025,x+3.465)):
        gable=[(u,z+.036,y+2.88),(u,z+1.24,y+4.13),
               (u,z+2.46,y+2.88),(u,z+1.24,y+2.72)]
        quads(geo,gable if i==0 else gable[::-1],CEDAR)
    box(geo,(x-.68,z+1.17,y+4.17),(4.87,.17,.16),RED,1.3)


def stair_treads(w,solid):
    for column in (50,74,98,122):
        step_x=column*.5
        height=top(w,step_x-.25,9.7)
        assert np.isclose(top(w,step_x+.25,9.7)-height,.5)
        for riser in range(3):
            x=step_x-.54+.18*riser
            box(solid,(x,8.548,height+.048),(.183,2.40,.167*(riser+1)+.001),TREAD,1.35)


def channel(solid, liquid, axis, long_bounds, across, center, width, grade, recess,
            *, bridges=None):
    start,end=long_bounds
    t=np.linspace(start,end,int(np.ceil((end-start)/.23))+1)
    if bridges:
        t=np.unique(np.r_[t,bridges])
    edges=[]
    for p in t:
        middle=center(p)
        half=min(width(p),middle-across[0]-.22,across[1]-middle-.22)
        lo,hi=middle-half,middle+half
        ledge=.18+.034*np.cos(p*1.81)
        ramp=(across[0],lo-ledge,lo,hi,hi+ledge,across[1])
        levels=(grade,grade-.018,grade-recess,grade-recess,grade-.018,grade)
        points=[(p,x,y) if axis=="x" else (x,p,y) for x,y in zip(ramp,levels)]
        edges.append(points)
    for i,(a,b) in enumerate(zip(edges,edges[1:])):
        blocked=bridges and bridges[0]<=t[i] and t[i+1]<=bridges[1]
        if blocked:
            a=[(x,z,grade) for x,z,_ in a]
            b=[(x,z,grade) for x,z,_ in b]
        for k in range(len(a)-1):
            points=[a[k],b[k],b[k+1],a[k+1]]
            points=points if axis=="x" else points[::-1]
            if k==2 and not blocked:
                quads(liquid,points,"lava",2.85)
            else:
                quads(solid,points,TREAD if blocked else FIRELINE if 0<k<4 else BASALT)


def arena_river_center(z):
    return 32.05+.65*np.sin(z*.38)+.28*np.cos(z*.84)


def arena_river_width(z):
    near_end=np.clip(min(z-21.5,45.5-z),0,1.7)
    return (0.57+.11*np.cos(z*.46))*(.28+.72*near_end/1.7)


def crater_pool_center(x):
    return 11.0+.20*np.sin(x*.98)+.12*np.cos(x*1.67)


def crater_pool_width(x):
    edge=np.clip(np.minimum(x-34.5,44.5-x),0,1.8)
    return (3.06+.17*np.cos(x*1.32))*(.39+.61*edge/1.8)


def terrain(gm, w):
    zz,xx=np.indices(w.hgt.shape)
    bank = np.zeros_like(w.hgt, dtype=bool)
    melt = w.blk==gm.LAVA
    if w.mid=="M442":
        # The non-traversable valley below the old invisible cliff wall.
        c=7.45 + 1.68*np.sin(xx*.135) + .51*np.cos(xx*.239)
        melt=(abs(zz-c)<1.20+.28*np.sin(xx*.56)) & (xx>=10) & (xx<=w.w-13)
        rear=28
        lava_heights=w.hgt.copy()
    elif w.mid=="M443":
        rear=32
        lava_heights=w.hgt.copy()
        melt &= np.abs((zz+.5)*.5-crater_pool_center((xx+.5)*.5)) < crater_pool_width((xx+.5)*.5)
    else:
        # This ribbon recess is a visual skin over the native grade-zero
        # arena. The stone bridge and the original collision share a grade.
        depth=(zz+.5)*.5
        c=arena_river_center(depth)
        taper=.28+.72*np.clip(np.minimum(depth-21.5,45.5-depth),0,1.7)/1.7
        melt=(abs((xx+.5)*.5-c)<(.57+.11*np.cos(depth*.46))*taper) & (zz>=43) & (zz<91)
        melt &= ~((zz>=59)&(zz<=68))
        rear=92
        lava_heights=w.hgt.copy()
    for dz,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        bank |= np.roll(melt,(dz,dx),axis=(0,1))
    bank &= ~melt
    tile=np.where(w.blk!=0,1,0)
    tile[w.blk==gm.STONEW]=2
    tile[bank]=3
    if w.mid=="M442":
        tile[melt]=4
    elif w.mid=="M443":
        tile[w.blk==gm.LAVA]=0
    else:
        tile[43:91,59:70]=0
    tile[rear:]=0
    solid, liquid=grid_surfaces(tile,lava_heights,("",ASH,TREAD,FIRELINE,"lava"),wall_style=BASALT,fluid=4)
    support=(w.hgt[rear-1]+1.)*.5 + .04
    ridge(w,solid,rear*.5,support)
    if w.mid=="M443":
        channel(solid,liquid,"x",(34.5,44.5),(7.5,14.5),crater_pool_center,crater_pool_width,1.89,.32)
        crater_shrine(solid)
    if w.mid=="M896":
        channel(solid,liquid,"z",(21.5,45.5),(29.5,35.),arena_river_center,arena_river_width,.549,.145,
                bridges=(29.5,34.5))
        for a in (30.75,33.08):
            box(solid,(a,30.16,.553),(.37,3.72,.095),STONE,1.15)
        for i in range(11):
            a=30.47 + i*.239
            box(solid,(a,30.32,.554),(.224,3.42,.061),TREAD,1.30)
    if w.mid=="M442":
        stair_treads(w,solid)
    return solid,liquid,melt,bank


def dressing(gm,w,melt,bank):
    placements,lights,pops=[],[],[]

    def adorn(key,x,z,scale,yaw):
        y=top(w,x,z)
        placements.append([key,x,y,z,scale,yaw])
        return y

    def lamp(x,z,scale=.94,yaw=.1):
        y=adorn(LANTERN,x,z,scale,yaw)
        lights.append([x,y+1.02*scale,z,4.8,5.9,0xffae55ff])

    if w.mid=="M442":
        for i,x in enumerate((16.42,22.15,27.42,32.95,39.02,44.31,52.45,59.82,62.15,66.88)):
            lamp(x,11.14+.19*np.sin(i),1.03 if i==7 else .75,.26*np.sin(i))
        for i,x in enumerate((17.9,30.29,41.28,48.12,64.41)):
            adorn(MARKER,x,11.77+.20*np.sin(i),.75+.06*np.cos(i),.51*i)
    elif w.mid=="M443":
        for x,z,scale in ((21.08,12.87,1.04),(26.22,12.92,1.04),(17.3,11.22,.78),
                          (27.65,11.41,.77),(31.12,11.96,.92),(32.83,11.82,.84)):
            lamp(x,z,scale)
        adorn(MARKER,17.04,11.92,.92,.50)
        adorn(MARKER,31.26,6.56,.78,.28)
    else:
        for i,(x,z) in enumerate(((19.5,39.6),(24.,41.2),(29.1,39.76),(38.6,39.77),(43.,40.7),(48.,40.0))):
            lamp(x,z,.87+.10*np.sin(i),.15*i)
        adorn(MARKER,24.2,41.6,1.0,.31)
        adorn(MARKER,40.8,42.0,1.0,-.28)
    spots=sorted((int(x),int(z)) for z,x in np.argwhere(melt))
    for i, (x,z) in enumerate(spots[4::max(5,len(spots)//11)]):
        px,pz=x*.5+.25,z*.5+.25
        y=(.413 if w.mid=="M896" else 1.581 if w.mid=="M443" else top(w,px,pz)+.089)
        lights.append([px,y+.35,pz,3.95 if w.mid=="M896" else 4.4,2.3,0xff651fff])
        pops.append([px,y+.024,pz,.45+.13*(i%3),(i*1.477)%8,.14+.053*(i%4)])
    verge=sorted((int(x),int(z)) for z,x in np.argwhere(bank))
    for i,(x,z) in enumerate(verge[7::max(9,len(verge)//9)]):
        if w.mid=="M443" and z<13:
            continue
        if w.mid=="M896" and z<71:
            continue
        adorn(SHELF,x*.5+.25,z*.5+.25,.46+.065*(i%4),(i*.71)%6.28)
    return placements,lights,pops


def battle_audit(catalog, melt):
    arena=catalog["M896"]
    markers={v["name"]:v for v in arena["marker"].values()}
    enemy=markers["*enemyloc"]["pos"]
    party=markers["*memberloc"]["pos"]
    groups=[g for g in catalog["M001"]["encount"] if g["mapid"]=="M896"]
    assert {g["gid"] for g in groups} == {149,150,151,153}
    locations=[]
    for group in groups:
        for row in group["enemies"]:
            x=int(enemy[0]+2*row["x"])
            z=int(enemy[2]+3.6*row["z"])
            assert not melt[max(0,z-2):z+3,max(0,x-2):x+3].any(),(group["gid"],x,z)
            locations.append((x,z))
    assert not melt[:,party[0]-2:party[0]+3].any()
    assert not melt[59:69].any()
    return {"groups":[g["gid"] for g in groups],"enemy_cells":locations,"party_marker":party,
            "bridge_cells":[59,68],"retains_full_native_collision":True}


def build(repo):
    engine=repo/"_tools/rpgcobo-tool"
    catalog=read_json(engine/CATALOG)
    gm=game_definition(repo)
    TEX.mkdir(parents=True,exist_ok=True)
    export_coast.STAGE=STAGE
    diorama_trees.STAGE=STAGE
    make_palettes()
    make_lava()
    prop_reports={}
    for name,size in ((MARKER,(.72,1.52,.64)),(SHELF,(2.4,.64,1.20)),(LANTERN,(.61,1.24,.62))):
        prop_reports[name]=diorama_trees.build_diorama_mesh(name,name,size,main_component=True)
    for name,raw in resource_files(engine/ROOT,{"required":{"placements":[["magma_spatter"]]}}).items():
        (STAGE/name).write_bytes(raw)
    rows,report={},{}
    for mid in MAPS:
        world,events=gm.make(mid)
        row=catalog[mid]
        assert row["size"][:3:2]==[world.w,world.d],mid
        assert all(row["event"][k]["pos"]==v["pos"] for k,v in events.ev.items()
                   if k in row["event"] and "pos" in v)
        rock,lava,melt,bank=terrain(gm,world)
        model=mid.lower()+"_oracle_volcanic"
        export(model,rock,MATERIALS,
               normal_maps={k:NORMAL for k in (BASALT,CRAGS,TREAD,STONE)},
               smooth_materials=(CRAGS,))
        export(model+"_melt",lava,{"lava":(FLOW+"00.png",.49)})
        placements,lights,pops=dressing(gm,world,melt,bank)
        rows[mid]=dict(terrain=model,water=model+"_melt",waterMode="lava",hideStockScenery=True,
                       waterSequence={"prefix":FLOW,"frames":FLAMES,"seconds":15.2},
                       placements=placements,poolLights=lights,magmaSpatter=pops)
        report[mid]={"catalog_hash":digest(json.dumps(row,sort_keys=True).encode()),
                     "world_hash":digest((engine/f"project/data/mapdata/{mid}.bw").read_bytes()),
                     "shape":[world.w,world.d],"lava_cells":int(melt.sum()),
                     "quads":len(rock.faces),"liquid_quads":len(lava.faces),
                     "story_anchors":{k:v["pos"] for k,v in events.ev.items()
                                      if "pos" in v and v["role"] in ("light","portal","custom") and int(k.strip("#"))<=120},
                     "placements":len(placements),"pop_emitters":len(pops)}
        if mid=="M896":
            report[mid]["formations"]=battle_audit(catalog,melt)
    (STAGE/"index.json").write_text(json.dumps(rows,separators=(",",":")),encoding="utf8")
    payload=resource_files(STAGE,rows)
    info={"maps":report,"props":prop_reports,"files":{k:digest(v) for k,v in payload.items()}}
    (HERE/"oracle-volcanic-receipt.json").write_text(json.dumps(info,indent=2),encoding="utf8")


def stage(repo, engine):
    live=repo/"_tools/rpgcobo-tool"
    if engine.resolve()==live.resolve():
        raise ValueError("Use a closed isolated playtest profile.")
    proof=read_json(HERE/"oracle-volcanic-receipt.json")
    catalog=read_json(engine/CATALOG)
    for mid,row in proof["maps"].items():
        assert digest(json.dumps(catalog[mid],sort_keys=True).encode())==row["catalog_hash"],mid
        assert digest((engine/f"project/data/mapdata/{mid}.bw").read_bytes())==row["world_hash"],mid
    for name,checksum in proof["files"].items():
        assert digest((STAGE/name).read_bytes())==checksum,name
    (engine/ROOT/"tex").mkdir(parents=True,exist_ok=True)
    install_environment_rows.STAGE=STAGE
    install_environment_rows.install(engine,MAPS)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("build","stage"))
    parser.add_argument("repository",type=Path)
    parser.add_argument("--profile",type=Path)
    args=parser.parse_args()
    repo=args.repository.resolve()
    if args.action=="build":
        build(repo)
    else:
        if args.profile is None:
            parser.error("--profile is required for stage")
        stage(repo,args.profile.resolve())
