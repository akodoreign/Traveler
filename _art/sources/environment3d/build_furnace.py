"""Build the connected Tamori's Furnace caves, crater, and combat backdrops."""

import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, label, map_coordinates

from build_kaiu_kit import faces
from export_coast import Geometry, STAGE, export, voxel_asset
from prepare_coast import periodic
from voxelize_coast import save

HERE = Path(__file__).resolve().parent
SCANS = HERE / "surface_sources"
TEX = STAGE / "tex"
STYLES = ("", "furnace_ash", "furnace_basalt", "furnace_scorch", "lava")
MAPS = ("M384", "M385", "M386", "M873", "M874")


def generated_scan(key, size):
    image = Image.open(SCANS / f"{key}.png").convert("RGB")
    return periodic(image.crop((11, 11, image.width-11, image.height-11)), size)


def materials():
    for key in ("furnace_ash", "furnace_basalt"):
        scan = generated_scan(key, 1024)
        if key == "furnace_ash":
            scan = scan * .89 + [3, 2, 5]
        else:
            scan = scan * .88 + [8, 5, 3]
        Image.fromarray(np.uint8(scan.clip(0, 255))).save(TEX / f"{key}.png")
        if key == "furnace_ash":
            burnt = scan * [.97, .76, .72] + [18, 1, 0]
            Image.fromarray(np.uint8(burnt.clip(0, 255))).save(TEX / "furnace_scorch.png")
            pilgrim = scan * [1.05,.98,.83] + [16,11,7]
            Image.fromarray(np.uint8(pilgrim.clip(0, 255))).save(TEX / "furnace_road.png")
    size = 512
    scan = generated_scan("furnace_flow", size)
    y, x = np.indices((size, size), dtype=float)
    # Keep the generated folds and seams, but broaden the molten portion.
    # Isolated plates stay dark. The flowing body uses a wholly warm ramp.
    veins = (scan[...,0]-scan[...,2]>68)&(scan[...,0]>scan[...,1]*1.28)
    dist = distance_transform_edt(np.tile(~veins,(3,3)))[size:2*size,size:2*size]
    ripple = (np.sin(x*.099+y*.063) + np.cos(y*.17-x*.062)) * 2.1
    heat = np.clip((48-dist+ripple)/43,0,1)
    relief = np.clip((scan[...,0]+scan[...,1]) / 400,0,1)
    reds = 55+197*np.power(heat,.54)+relief*24
    amber = 7+140*np.power(heat,1.57)+relief*56*heat
    gold = 4+42*np.power(heat,3.4)+relief*25*heat
    lava = np.dstack((reds,amber,gold))
    for frame in range(24):
        phase = frame * np.pi / 12
        coords = [(y + 8 * np.sin(x*.024 + phase) + 3 * np.sin(y*.016-phase)) % size,
                  (x + 8 * np.cos(y*.031 + phase) + 3.5 * np.sin(x*.029+phase*2)) % size]
        moved = np.dstack([map_coordinates(lava[...,channel], coords, order=1, mode="grid-wrap")
                           for channel in range(3)])
        pulse = .98 + .067*np.sin(phase + y*.013)
        moved[...,0] *= pulse
        moved[...,1] *= pulse
        Image.fromarray(np.uint8(moved.clip(0,255))).save(TEX / f"magma{frame:02}.png")
    return lava


def source_voxels(voxfile, lava):
    source = SCANS / "furnace_columns.png"
    image = np.array(Image.open(source).convert("RGB")).reshape(-1,3)
    usable = image[(image[:,0]>image[:,1]+4)&(image[:,0]<149)&(image[:,0]>18)]
    tones = np.percentile(usable, [12,30,48,65,85], axis=0)
    reports = []
    for form, columns in {
        "basalt_organ": [(4,7,4,18),(10,4,4,24),(13,10,4,30),(18,8,3,17),(10,15,4,13),(17,15,4,9)],
        "basalt_spires": [(5,10,4,10),(9,8,3,17),(13,8,4,24),(17,11,3,20),(11,14,4,7)],
    }.items():
        occ = {}
        for idx, (cx, cz, radius, height) in enumerate(columns):
            for h in range(height):
                for z in range(cz-radius,cz+radius+1):
                    for x in range(cx-radius,cx+radius+1):
                        if max(abs(x-cx),abs(z-cz))>radius or abs(x-cx)+abs(z-cz)>radius+2:
                            continue
                        if h>=height-2 and (x+z+idx)%4==0:
                            continue
                        grain = ((x*11+z*5+h*3+idx)//3)%5
                        color = tones[grain]*(1.11 if h%7 not in (0,1) else .79)
                        occ[x,z,h] = np.clip(color + [15,12,12], 0, 255)
        points = np.asarray(list(occ))
        points -= points.min(axis=0)
        reports.append(save(form,points,np.asarray(list(occ.values())),[.095,.095,.095],str(source),voxfile))
        voxel_asset(form)

    form = "lava_crust_shelf"
    occ = {}
    for x in range(41):
        crest = .9*np.sin(x*.38)
        for z in range(15):
            taper = .62 + .38*np.sin(np.pi*(x+1)/42)
            rim = abs(z - 7 + crest) / (7*taper)
            if rim > 1:
                continue
            for h in range(2 if rim<.53 else 3+(x+z)%3):
                sample = lava[(z*27+14)%512,(x*16+53)%512]
                if h==1 and rim<.53:
                    color = np.maximum(sample,[179,44+int(18*np.sin(x*.21)),8])
                else:
                    color = [43+(x*5+z*3+h)%20, 34+(z*7+h)%14, 46+(x*3+h)%15]
                occ[x,z,h] = color
    points = np.asarray(list(occ))
    points -= points.min(axis=0)
    reports.append(save(form,points,np.asarray(list(occ.values())),[.074,.074,.074],
                        str(SCANS/"furnace_flow.png"),voxfile))
    voxel_asset(form, hot_material=True)
    spark = np.array([(0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,1,1),(0,0,2),
                      (3,1,2),(3,1,3),(1,3,4)])
    colors = np.array([(236,58,8),(249,96,10),(246,118,12),(250,156,17),(255,176,25),
                       (255,194,47),(255,220,81),(236,84,10),(255,160,26),(255,127,21)])
    reports.append(save("magma_spatter",spark,colors,[.045,.045,.042],
                        str(SCANS/"furnace_flow.png"),voxfile))
    voxel_asset("magma_spatter",hot_material=True)
    return reports


def surface(gm, m):
    block, height = m.blk, m.hgt.astype(int)
    liquid = block==gm.LAVA
    fireline = block==gm.EMBER
    wall = block==gm.STONE
    z, x = np.indices(block.shape)
    if m.mid in ("M873","M874"):
        # Both formations face inward on the x axis. A narrow tributary
        # runs through the empty space between them toward the rear pool.
        center = 63.0 + 2.2*np.sin((z-62)*.20) + .8*np.cos((z-63)*.34)
        stream = (abs(x-center)<1.25+.38*np.cos(z*.19)) & (z>=53) & (z<96)
        liquid |= stream
        bank = (abs(x-center)<3.3) & (z>=52) & (z<94)
        fireline |= bank & ~liquid
    if m.mid=="M873":
        # Pull molten channels toward the camera, keeping the entire actor area dry.
        # The banks continue offstage into the existing full-width sheet.
        fingers = ((abs(x-18-4*np.sin(z*.21))<4.0)&(z>=65) |
                   (abs(x-104-5*np.cos(z*.18))<4.7)&(z>=66) |
                   ((z>=78+4*np.sin(x*.17))&(z<84)))
        liquid |= fingers & (z<94)
        fireline |= ((z==77)|(z==78)) & ~liquid
    elif m.mid=="M874":
        liquid |= (z>=86+5*np.sin(x*.15)+1.5*np.cos(x*.47)) & (z<99)

    tile = np.where(block!=0,1,0)
    tile[wall] = 2
    tile[fireline] = 3
    tile[liquid] = 4
    rock,melt = grid_surfaces(tile,height,STYLES,wall_style="furnace_basalt",fluid=4)
    return rock,melt,liquid


def grid_surfaces(tile, height, styles, *, wall_style, fluid=0):
    """Skin an existing world grid with continuous surfaces and UVs."""
    rock, melt = Geometry(), Geometry()

    for high in np.unique(height):
        mask = np.where(height==high,tile,0)
        for x0,z0,x1,z1,material in faces(mask):
            s = styles[material]
            elevation = (high+1)*.5+(.079 if material==fluid else .049)
            corners = [(a*.5,b*.5,elevation) for a,b in ((x0,z0),(x1,z0),(x1,z1),(x0,z1))]
            repeat = 4.7 if material==fluid else 4.6
            (melt if material==fluid else rock).quad(corners,[(a/repeat,b/repeat) for a,b,_ in corners],s)

    # Generate all exposed interior risers from the same local rock. Overlay
    # faces sit just above the saved world since it still owns navigation.
    for axis in (0,1):
        grid = height if axis==0 else height.T
        types = tile if axis==0 else tile.T
        for row in range(1,len(grid)):
            up, down = grid[row], grid[row-1]
            for direction, low, high, kinds in ((-1,down,up,types[row]),(1,up,down,types[row-1])):
                active = (low<high)&(kinds!=0)
                for col in np.flatnonzero(active):
                    plane = row*.5+direction*.046
                    left, right = col*.5,(col+1)*.5
                    y0,y1 = (low[col]+1)*.5,(high[col]+1)*.5+.049
                    line = [(left,plane,y0),(right,plane,y0),(right,plane,y1),(left,plane,y1)]
                    if axis==1:
                        line = [(b,a,c) for a,b,c in line]
                    if (axis==0 and direction>0) or (axis==1 and direction<0):
                        line.reverse()
                    rock.quad(line,[(p[axis]/4.,p[2]/3.) for p in line],wall_style)
    return rock,melt


def dressing(gm, m, liquid):
    props, lights, spatter = [], [], []
    def add(key, x, z, size, yaw, floor=None):
        y = float((m.hgt[z,x]+1)*.5) if floor is None else floor
        props.append([key,x*.5+.25,y,z*.5+.25,size,yaw])

    if m.mid in ("M873","M874"):
        # Left and right silhouettes frame the encounter without entering
        # the battle actor rectangle. Smaller cutaways break the distant bank.
        for x,z,key,size,yaw in (
            (25,74,"basalt_organ",1.2,.30),(37,79,"basalt_spires",.88,.75),
            (89,82,"basalt_organ",.78,1.1),(95,75,"basalt_spires",1.05,.49),
            (117,82,"basalt_organ",1.38,-.64),(8,83,"basalt_spires",1.3,.37),
            (53,83,"lava_crust_shelf",.86,-.2),(76,87,"lava_crust_shelf",.93,.16)):
            add(key,x,z,size,yaw)
        if m.mid=="M873":
            for i,x in enumerate(range(14,125,9)):
                z = 95+(i*7)%5
                size = 2.0+.55*np.sin(i*1.8)**2
                add("basalt_organ",x,z,size,.43+i*.77,.53)
        for x,z in ((18,72),(40,82),(62,83),(84,83),(108,74)):
            lights.append([x*.5+.25,1.16,z*.5+.25,6.8,2.0])
        for z in (58,67,73,79):
            cells = np.flatnonzero(liquid[z,58:69])+58
            if len(cells):
                x = int(cells[len(cells)//2])
                lights.append([x*.5+.25,.85,z*.5+.25,3.4,1.75])
        candidates = np.argwhere(liquid & (np.indices(liquid.shape)[0]<94))
        for i, (z,x) in enumerate(candidates[17::49]):
            spatter.append([x*.5+.25,float((m.hgt[z,x]+1)*.5+.11),z*.5+.25,
                            .55+(i*3)%7*.10,(i*1.37)%8.,.18+(i%5)*.10])
        for z in (57,64,68,73,77):
            cells = np.flatnonzero(liquid[z,58:69])+58
            if len(cells):
                x=int(cells[len(cells)//2])
                spatter.append([x*.5+.25,.62,z*.5+.25,.83,z*.69%8.,.43])
    else:
        zones,num = label(liquid)
        for zone in range(1,num+1):
            zz,xx = np.where(zones==zone)
            if len(zz)<4:
                continue
            k = ((zz-np.mean(zz))**2+(xx-np.mean(xx))**2).argmin()
            x,z = int(xx[k]),int(zz[k])
            y = (int(m.hgt[z,x])+1)*.5
            lights.append([x*.5+.25,y+.48,z*.5+.25,4.6 if len(zz)<100 else 8.6,1.18])
            if len(zz)>11:
                add("lava_crust_shelf",x,z,.37 if len(zz)<100 else .87,.25)
            for i,k in enumerate(range(1,len(zz),max(4,len(zz)//15))):
                tz,tx=int(zz[k]),int(xx[k])
                spatter.append([tx*.5+.25,float((m.hgt[tz,tx]+1)*.5+.11),tz*.5+.25,
                                .65,zone*1.17+i*.79,.22+(i%4)*.10])
        if m.mid=="M386":
            bank = np.argwhere(liquid & ~np.roll(liquid,1,axis=0))
            for z,x in bank[5::16]:
                add("basalt_spires",int(x),int(z),.69,-.19)
        else:
            # Dress wall shoulders a few courses above the route. They don't
            # jut upward from the paths, quest markers, or pool ledges.
            height=m.hgt
            for z,x in np.argwhere((height>=8)&(np.roll(height,2,axis=0)<=2)):
                if 10<x<m.w-10 and (x*17+z*13)%83<3:
                    add("basalt_spires",int(x),int(z),.56,.22)
    return props,lights,spatter


def main():
    repo = Path(sys.argv[1])
    sys.path.insert(0,str(repo/"tools"))
    import gen_maps as gm
    import voxfile

    voxel_sources = source_voxels(voxfile, materials())
    resource = STAGE/"index.json"
    index = json.loads(resource.read_bytes())
    report = {}
    rock_materials = {key:(f"{key}.png",.92) for key in STYLES[1:4]}
    for mid in MAPS:
        m,events = gm.make(mid)
        rock,melt,liquid = surface(gm,m)
        tag = mid.lower()
        export(tag+"_furnace",rock,rock_materials)
        export(tag+"_magma",melt,{"lava":("magma00.png",.66)})
        props,lights,spatter = dressing(gm,m,liquid)
        index[mid] = dict(terrain=tag+"_furnace",water=tag+"_magma",waterMode="lava",
                          placements=props,poolLights=lights,magmaSpatter=spatter)
        report[mid] = dict(name=m.name, grid=[m.w,m.d], magma_quads=len(melt.faces),
                           basalt_quads=len(rock.faces), liquid_cells=int(liquid.sum()),
                           props=len(props), lights=len(lights), events=len(events.ev) if events else 0)
    resource.write_text(json.dumps(index,separators=(",",":")),encoding="utf-8")
    (HERE/"furnace-layout.json").write_text(json.dumps({"maps":report,"voxels":voxel_sources},indent=2),
                                            encoding="utf-8")


if __name__=="__main__":
    main()
