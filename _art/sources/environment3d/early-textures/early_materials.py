"""Build map-local tactile materials on the exact authored early-map surfaces."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import struct
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
sys.path.insert(0,str(WORK))
import export_coast
from publish_castle_gates import publish as transact

NATIVE=Path("project/resource/native_environment")
STORY=Path("project/data/map.json")
SOURCES=WORK/"surface_sources"
MODEL=re.compile(r'^modeldata = "([^"]+)"',re.M)
MATERIAL=re.compile(r'name = "([^"]+)"[^}]*?texture0 = "([^"]+)"',re.S)
ROUGHNESS=re.compile(r'name = "([^"]+)"[^}]*?rough = ([0-9.]+)',re.S)
LUMA=np.array((.213,.715,.072),dtype=np.float32)
KNOWN={"M101","M102","M103"}


def stretch(values):
    normal=np.clip((values-np.median(values))/max(float(np.std(values)),1.),-2.65,2.65)
    return normal.astype(np.float32)


def ramp(lo,hi,value):
    t=np.clip((value-lo)/(hi-lo),0.,1.)
    return t*t*(3.-2.*t)


def save_image(stem,data):
    image=np.clip(np.rint(data),0,255).astype(np.uint8)
    Image.fromarray(image).save(export_coast.STAGE/"tex"/f"{stem}.png",compress_level=5)


def load_scan(name):
    rgb=np.asarray(Image.open(SOURCES/name).convert("RGB"),dtype=np.float32)
    return rgb@LUMA


def sample(scan,x,y):
    h,w=scan.shape
    return map_coordinates(scan,[y*h,x*w],order=1,mode="grid-wrap",prefilter=False)


def mix_scan(scan,x,y,period):
    """Layer two spatially coherent views of a scan at physical scales."""
    u=x/period
    v=y/period
    a=sample(scan,u+.19*v,v-.16*u)
    b=sample(scan,.71*u-.21*v+.37,.19*u+.76*v+.11)
    return a*.76+b*.24


def relief(stem,height,xstep,ystep,strength=1.):
    y,x=np.gradient(height,ystep,xstep)
    vectors=np.stack((-x*strength,y*strength,np.ones_like(height)),axis=-1)
    vectors/=np.linalg.norm(vectors,axis=-1,keepdims=True)
    save_image(stem,(1.+vectors)*127.5)


def sections(path,*,with_uv=False):
    """Read exact SMDL positions and the material group of each original quad."""
    raw=path.read_bytes()
    assert raw[:9]==b"SMDL\0\1\0\0\0"
    cursor=14
    for _ in range(raw[9]):
        role,kind,_,width,_,_,_,count=struct.unpack_from(">6BII",raw,cursor)
        cursor+=14
        dtype={1:">f4",4:">i2"}[kind]
        data=np.frombuffer(raw,dtype=dtype,count=count*width,offset=cursor)
        if role==0:
            xyz=data.reshape(-1,4,3).astype(np.float32)
        if role==4:
            uv=data.reshape(-1,4,2).astype(np.float32)
        cursor+=data.nbytes
    count=raw[cursor+4]
    cursor+=5
    groups=np.full(len(xyz),-1,np.int32)
    for group in range(count):
        _,_,_,kind,length,count=struct.unpack_from(">4BII",raw,cursor)
        ids=np.frombuffer(raw,dtype={3:">u2",7:">u4"}[kind],count=count,offset=cursor+12)
        triangles=ids.astype(np.int64).reshape(-1,6)
        base=triangles[:,0]
        assert (triangles==base[:,None]+[0,2,1,0,3,2]).all() and (base%4==0).all()
        assert (groups[base//4]==-1).all()
        groups[base//4]=group
        cursor+=16+length
    assert (groups>=0).all()
    return (xyz,groups,uv) if with_uv else (xyz,groups)


def palette(assets,grade,mid,baseline):
    """Use the accepted map palette to fix the new surfaces' median tones."""
    grade=grade.resolve() if grade else None
    record=json.loads((grade/"coastal-proof.json").read_bytes()) if grade else {}
    row=record.get("maps",{}).get(mid,{}).get("after",baseline)
    alias=row["terrain"]+".pm"
    path=grade/"files"/alias if grade else assets/alias
    desc=(path if path.is_file() else assets/alias).read_text("utf8")
    result={}
    for key,texture in MATERIAL.findall(desc):
        painted=grade/"files"/texture if grade else assets/texture
        if not painted.is_file():
            painted=assets/texture
        rgb=np.asarray(Image.open(painted).convert("RGB"),dtype=np.float32)
        result[key]=np.median(rgb.reshape(-1,3),axis=0)
    return result


def terrain_top(tag,box,quads,labels,colors):
    x0,z0,width,depth=box
    w,h=4096,1536
    x,z=np.meshgrid(np.linspace(x0,x0+width,w,dtype=np.float32),
                    np.linspace(z0,z0+depth,h,dtype=np.float32))
    xs,zs=width/(w-1),depth/(h-1)
    scans={key:stretch(load_scan(src)) for key,src in (
        ("meadow","meadow_scan.png"),("path","kensu_path_clay.png"),("sand","sand_scan.png"))}
    grass=mix_scan(scans["meadow"],x,z,3.72)
    trail=mix_scan(scans["path"],x,z,4.71)
    sand=mix_scan(scans["sand"],x,z,2.8)
    broad=.56*np.sin(.16*x+1.12*z)+.47*np.sin(.57*x-.43*z)+.21*np.cos(2.06*x+.75*z)
    heather=(.54*np.sin(1.27*x+.94*z)+.46*np.cos(.55*x-2.21*z))*0.5+.5
    grass_rgb=np.array(colors["meadow"])+grass[...,None]*[4.2,7.8,3.8]
    grass_rgb+=broad[...,None]*[5.4,7.2,2.9]+(heather[...,None]-.5)*[12.5,5.0,-3.5]
    trail_rgb=np.array(colors["path"])+trail[...,None]*[5.6,5.1,4.4]+broad[...,None]*[3.1,3.3,3.5]
    trail_height=trail*.0038
    stem=tag+"_ground"
    if tag=="m102":
        # Trails wear hardest in their middle. Let grasses feather into
        # the landward margin, with coherent texture on both ledge and lane.
        shoulder=12.5+.055*np.sin(2.5*x)+.051*np.sin(6.1*x+.2)+.045*np.cos(.87*x)
        blend=ramp(shoulder-.19,shoulder+.24,z)
        lane=(np.exp(-((z-10.74)/.31)**2)+.70*np.exp(-((z-11.55)/.29)**2))
        trail_rgb+=lane[...,None]*[4.0,3.3,1.8]
        sand_rgb=np.array(colors["sand"])+sand[...,None]*[5.5,5.1,4.6]
        damp=1.-ramp(7.,7.82,z)
        sand_rgb-=damp[...,None]*[15.0,12.0,7.0]
        ground=trail_rgb*(1-blend[...,None])+grass_rgb*blend[...,None]
        ground=np.where((z<9.997)[...,None],sand_rgb,ground)
        height=trail_height*(1.-blend)+grass*.0034*blend
        height=np.where(z<9.997,sand*.0037,height)
    else:
        # Stay aligned to the market courtyard's authored surface cells.
        grass_mask=np.zeros((h,w),dtype=np.float32)
        for row,style in zip(quads,labels):
            if style!="meadow" or np.ptp(row[:,1])>.001:
                continue
            qx,_,qz=row.min(0)
            rx,_,rz=row.max(0)
            a,b=np.clip(np.rint((np.array((qx,rx))-x0)/xs).astype(int),0,w-1)
            c,d=np.clip(np.rint((np.array((qz,rz))-z0)/zs).astype(int),0,h-1)
            grass_mask[c:d+1,a:b+1]=1.
        blend=gaussian_filter(grass_mask,(.09/zs,.09/xs))
        ground=trail_rgb*(1-blend[...,None])+grass_rgb*blend[...,None]
        height=trail_height*(1-blend)+grass*.0034*blend
    save_image(stem,ground)
    relief(stem+"_normal",height,xs,zs)


def terrain_wall(tag,box,colors):
    x0,y0,width,height=box
    w,h=4096,420
    u,v=np.meshgrid(np.linspace(x0,x0+width,w,dtype=np.float32),
                     np.linspace(y0,y0+height,h,dtype=np.float32))
    xs,ys=width/(w-1),height/(h-1)
    rock=stretch(load_scan("rock_01_diff_1k.jpg"))
    grain=mix_scan(rock,u,v,2.82)
    body=.43*np.sin(u*.59+v*2.3)+.39*np.sin(.17*u-v*3.2)+.36*np.cos(.95*u+3.7*v)
    layers=1.-np.exp(-14.*np.sin(v*8.3+.44*np.sin(u*.9)+.28*np.cos(u*.59))**2)
    weather=body*.36+.55*layers+grain*.57-.26
    lichen=np.maximum(0.,body-.27)*.75
    gray=np.array(colors["cliff"])+weather[...,None]*[15.,15.8,16.5]
    gray+=lichen[...,None]*[-3.,7.1,-3.5]
    save_image(tag+"_rock",gray)

    # Keep the photo-normal direction and add only shallow broad weathering.
    normal=np.asarray(Image.open(SOURCES/"rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=np.float32)/127.5-1.
    ox,oy=(sample(normal[...,i],u/2.82+.19*v/2.82,v/2.82-.16*u/2.82) for i in (0,1))
    vy,ux=np.gradient(body*.009+layers*.006,ys,xs)
    vectors=np.stack((.57*ox-ux,.57*oy+vy,np.ones_like(body)),axis=-1)
    vectors/=np.linalg.norm(vectors,axis=-1,keepdims=True)
    save_image(tag+"_rock_normal",(1.+vectors)*127.5)

    if tag=="m102":
        masonry=stretch(load_scan("kaiu_masonry.png"))
        coursing=mix_scan(masonry,u,v,2.65)
        # Sea splash darkens the lower masonry, distinct from the dry road.
        lower=1.-ramp(1.10,2.12,v)
        sea=np.array(colors["cliff"])+[-3.,-.5,2.]+coursing[...,None]*[9.,10.5,11.3]
        sea-=lower[...,None]*[5.,6.,6.]
        save_image(tag+"_seawall",sea)
        relief(tag+"_seawall_normal",coursing*.007,xs,ys)


def finish_cliff(tag,box,colors):
    """Add separated natural fractures and shallow hand-laid seawall courses."""
    x0,y0,width,height=box
    w,h=4096,420
    u,v=np.meshgrid(np.linspace(x0,x0+width,w,dtype=np.float32),
                     np.linspace(y0,y0+height,h,dtype=np.float32))
    xs,ys=width/(w-1),height/(h-1)
    source=stretch(load_scan("rock_01_diff_1k.jpg"))
    grain=mix_scan(source,u,v,2.82)
    middle=mix_scan(gaussian_filter(source,21.,mode="wrap"),u+.27*v,v-.19*u,4.45)
    mass=.49*np.sin(.71*u+.55*v)+.34*np.cos(.3*u-v*.84)+.29*np.sin(.27*u+1.53*v)
    basin=gaussian_filter(middle,(3.,4.5),mode="nearest")
    seams=np.zeros_like(u)
    raised=np.zeros_like(u)
    rng=np.random.default_rng(1266202)
    # Each fracture follows one short, tilted reach with tapering ends.
    for _ in range(79):
        center,level=rng.uniform(x0,x0+width),rng.uniform(y0,y0+height)
        half=rng.uniform(1.4,5.1)
        region=np.flatnonzero(np.abs(u[0]-center)<half)
        local=u[:,region]-center
        trace=(level+rng.choice((-1.,1.))*rng.uniform(.067,.24)*local+
               .042*np.sin(local*rng.uniform(1.6,3.6)+rng.uniform(0.,6.2)))
        radius=rng.uniform(.018,.052)
        tips=(1.-ramp(.32,1.,np.abs(local)/half))*(.65+.35*np.sin(local*1.65+.9)**2)
        ridge=np.exp(-((v[:,region]-trace)/radius)**2)*tips
        ledge=np.exp(-((v[:,region]-trace-radius*1.4)/(1.4*radius))**2)*tips
        seams[:,region]+=ridge*rng.uniform(.37,1.)
        raised[:,region]+=ledge*rng.uniform(.22,.65)
    weather=grain*.29+basin*.80+mass*.26
    color=np.array(colors["cliff"])+weather[...,None]*[18.,19.,20.8]
    color+=seams[...,None]*[-11.5,-11.8,-13.]
    color+=raised[...,None]*[9.,8.8,7.6]
    lichen=ramp(.25,.84,mass)*ramp(-.2,.39,basin)
    color+=lichen[...,None]*[4.8,7.2,2.5]
    name=tag+"_rock_finish"
    save_image(name,color)
    image=np.asarray(Image.open(SOURCES/"rock_01_nor_gl_1k.jpg").convert("RGB"),dtype=np.float32)/127.5-1.
    ox,oy=(sample(image[...,i],u/2.82+.19*v/2.82,v/2.82-.16*u/2.82) for i in (0,1))
    vy,ux=np.gradient(mass*.012+basin*.0065-seams*.002+raised*.0012,ys,xs)
    normal=np.stack((.52*ox-ux,.52*oy+vy,np.ones_like(mass)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    save_image(name+"_normal",(normal+1.)*127.5)

    # Unequal stones interlock in shallow courses. Grain stays subordinate
    # to the visible edges and the weathered faces catch the same coast light.
    joints=np.zeros_like(u)
    shade=np.zeros_like(u)
    relief_height=np.zeros_like(u)
    course_edges=np.array((.84,1.08,1.29,1.50,1.74,1.97,2.19,2.44))
    warped=v+.026*np.sin(u*.87)+.008*np.cos(u*2.67)
    for bottom,top in zip(course_edges,course_edges[1:]):
        fraction=(warped-bottom)/(top-bottom)
        active=(fraction>=0.)&(fraction<1.)
        steps=np.r_[x0-rng.uniform(.4,1.25),x0+np.cumsum(rng.uniform(.31,.81,420))]
        warped_u=u+.014*np.sin(v*12.9+u*.5)
        index=np.searchsorted(steps,warped_u,side="right")-1
        xleft,xright=steps[index],steps[index+1]
        along=(warped_u-xleft)/(xright-xleft)
        across_gap=np.exp(-(np.minimum(fraction,1.-fraction)*(top-bottom)/.0185)**2)
        side_gap=np.exp(-(np.minimum(warped_u-xleft,xright-warped_u)/.023)**2)
        joint=np.maximum(across_gap,side_gap*.94)
        block=np.where(active,rng.uniform(-1.,1.,len(steps))[index],0.)
        joints+=np.where(active,joint,0.)
        shade+=block
        rounded=np.sin(np.pi*np.clip(along,0.,1.))*np.sin(np.pi*np.clip(fraction,0.,1.))
        relief_height+=np.where(active,.0043*rounded-.0028*joint,0.)
    weathered=grain*.36+basin*.65
    near_splash=1.-ramp(1.08,2.1,v)
    name=tag+"_seawall_finish"
    masonry=np.array(colors["cliff"])+[-3.,-.5,2.]+weathered[...,None]*[8.,8.3,8.8]
    masonry+=shade[...,None]*[7.0,7.2,7.6]-joints[...,None]*[18.0,17.7,16.5]
    masonry-=near_splash[...,None]*[5.,6.,6.]
    save_image(name,masonry)
    relief(name+"_normal",relief_height+gaussian_filter(weathered,(1.,1.1))*.0013,xs,ys)


def garrison_materials(colors,files):
    """Keep the fort's original tile proportions and strengthen surface relief."""
    w=1024
    u,v=np.meshgrid(np.linspace(0.,1.,w,dtype=np.float32),np.linspace(0.,1.,w,dtype=np.float32))
    block=np.asarray(Image.open(SOURCES/"kaiu_masonry.png").convert("L").resize((w,w)),dtype=np.float32)
    mortar=stretch(gaussian_filter(block,2.6,mode="wrap"))
    raw=stretch(block)
    slate=mix_scan(stretch(load_scan("rock_01_diff_1k.jpg")),u,v,.58)
    body=mortar*.45+raw*.42+slate*.24
    name="m101_laid_stone"
    stone=np.array(colors["kaiu_stone"])+body[...,None]*[12.8,13.0,14.1]
    save_image(name,stone)
    relief(name+"_normal",gaussian_filter(body,1.2,mode="wrap")*.012,2.6/w,2.6/w)
    files["kaiu_stone"]=name
    for key in ("kaiu_wood","kaiu_redwood"):
        # Extract actual grain contrast from the existing approved atlas.
        source=np.asarray(Image.open(files[key]).convert("RGB"),dtype=np.float32)
        gray=source@LUMA
        grain=gray-gaussian_filter(gray,(.75,3.3),mode="wrap")
        name="m101_"+key
        save_image(name,source+grain[...,None]*.23)
        relief(name+"_normal",gaussian_filter(stretch(gray),1.8,mode="wrap")*.004,
               2.6/gray.shape[1],2.6/gray.shape[0])
        files[key]=name


def prepare(repo,bundle,mids,grade,finish=False):
    root=repo/"_tools/rpgcobo-tool"
    assets=root/NATIVE
    original=json.loads((assets/"index.json").read_bytes())
    story=json.loads((root/STORY).read_bytes())
    export_coast.STAGE=bundle/"files"
    (export_coast.STAGE/"tex").mkdir(parents=True,exist_ok=True)
    receipt={}
    for mid in mids:
        row=original[mid]
        descriptor=(assets/(row["terrain"]+".pm")).read_text("utf8")
        path=assets/MODEL.search(descriptor)[1]
        quads,groups,original_uv=sections(path,with_uv=True)
        links=dict(MATERIAL.findall(descriptor))
        old_roughness={key:float(value) for key,value in ROUGHNESS.findall(descriptor)}
        names=list(links)
        labels=[names[i] for i in groups]
        colors=palette(assets,grade,mid,row)
        tag=mid.lower()
        x,_,z=quads.min(axis=(0,1))
        right,_,back=quads.max(axis=(0,1))
        topbox=x-.035,z-.035,right-x+.07,back-z+.07
        terrain_top(tag,topbox,quads,labels,colors)
        u=quads[...,0]+quads[...,2]*.72
        y=quads[...,1]
        wallbox=u.min()-.035,y.min()-.035,np.ptp(u)+.07,np.ptp(y)+.07
        if finish:
            assert mid=="M102"
            finish_cliff(tag,wallbox,colors)
        else:
            terrain_wall(tag,wallbox,colors)
        geometry=export_coast.Geometry()
        mats,normal_maps={},{}
        painted={}
        if mid=="M101":
            inputs={key:assets/relative for key,relative in links.items()}
            garrison_materials(colors,inputs)
            painted={k:v for k,v in inputs.items() if isinstance(v,str)}
            for key,source in inputs.items():
                if key in painted:
                    continue
                local=export_coast.STAGE/"tex"/source.name
                if not local.exists():
                    shutil.copyfile(source,local)
        for row,key,old_uv in zip(quads,labels,original_uv):
            flat=np.ptp(row[:,1])<.001
            points=row[:,[0,2,1]]
            if flat and key in ("sand","path","meadow"):
                style=tag+"_ground"
                a,b,c,d=topbox
                uv=[((xx-a)/c,1.-(zz-b)/d) for xx,zz,_ in points]
            elif mid!="M101" or key=="cliff" and not flat:
                low=row[:,1].max()<2.04 and row[:,2].mean()<10.04
                style=tag+("_seawall" if mid=="M102" and low else "_rock")+("_finish" if finish else "")
                a,b,c,d=wallbox
                uv=[((xx+.72*zz-a)/c,1.-((yy if not flat else yy+.37*zz)-b)/d) for xx,zz,yy in points]
            else:
                style=painted.get(key,key)
                uv=[(u,1.-v) for u,v in old_uv]
            geometry.quad(points,uv,style)
            texture=style+".png" if style.startswith(tag+"_") else Path(links[style]).name
            roughness=(.91 if style.endswith("_ground") else .87) if style.startswith(tag+"_") else old_roughness[style]
            mats[style]=(texture,roughness)
            if style.startswith(tag+"_"):
                normal_maps[style]=style+"_normal.png"
        target=tag+"_authored_materials"+("_finish" if finish else "")
        export_coast.export(target,geometry,mats,normal_maps=normal_maps)
        review,_=sections(export_coast.STAGE/(target+".mdl"))
        assert np.array_equal(review,quads),mid
        files=[target+".mdl",target+".pm",*[f"tex/{s}{suffix}.png" for s in normal_maps for suffix in ("","_normal")]]
        receipt[mid]={"baseline_mesh":path.name,"geometry_sha256":sha256(quads.tobytes()).hexdigest(),
             "vertices":int(quads.shape[0]*4),"terrain":target,
             "world":sha256((root/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest(),
             "story":story[mid],"files":{p:sha256((export_coast.STAGE/p).read_bytes()).hexdigest() for p in files}}
        if finish:
            receipt[mid]["predecessor"]=tag+"_authored_materials.mdl"
    (bundle/"receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),"utf8")


def apply(repo,bundle,profile,publish=False):
    live=(repo/"_tools/rpgcobo-tool").resolve()
    assert profile!=live
    engine=live if publish else profile
    receipt=json.loads((bundle/"receipt.json").read_bytes())
    baseline,updates,additions={},{},{}
    index=engine/NATIVE/"index.json"
    raw=index.read_bytes()
    rows=json.loads(raw)
    tested=json.loads((profile/NATIVE/"index.json").read_bytes())
    story=json.loads((engine/STORY).read_bytes())
    for mid,proof in receipt.items():
        assert story[mid]==proof["story"],mid
        assert sha256((engine/f"project/data/mapdata/{mid}.bw").read_bytes()).hexdigest()==proof["world"],mid
        old=engine/NATIVE/(rows[mid]["terrain"]+".pm")
        mesh=MODEL.search(old.read_text("utf8"))[1]
        assert mesh==proof["baseline_mesh"] or rows[mid]["terrain"]==proof["terrain"] or mesh==proof.get("predecessor"),mid
        updated={**rows[mid],"terrain":proof["terrain"]}
        if publish:
            assert tested[mid]==updated,(mid,"preview row differs from production row")
        rows[mid]=updated
        for rel,checksum in proof["files"].items():
            target=engine/NATIVE/rel
            resource=(bundle/"files"/rel).read_bytes()
            assert sha256(resource).hexdigest()==checksum,rel
            if publish:
                assert (profile/NATIVE/rel).read_bytes()==resource,rel
            if target.is_file():
                assert target.read_bytes()==resource,rel
            else:
                additions[target]=resource
    baseline[index]=raw
    updates[index]=json.dumps(rows,ensure_ascii=False,separators=(",",":")).encode()
    for path in additions:
        path.parent.mkdir(parents=True,exist_ok=True)
    transact(baseline,updates,additions)
    print(f"{'Published' if publish else 'Staged'} {', '.join(receipt)} with matching geometry and story.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","stage","publish"))
    parser.add_argument("repo",type=Path)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--maps",nargs="+",choices=sorted(KNOWN),default=["M102"])
    parser.add_argument("--grade",type=Path)
    parser.add_argument("--finish",action="store_true")
    parser.add_argument("--profile",type=Path)
    args=parser.parse_args()
    if args.action=="prepare":
        prepare(args.repo.resolve(),args.bundle.resolve(),args.maps,args.grade,args.finish)
    else:
        apply(args.repo.resolve(),args.bundle.resolve(),args.profile.resolve(),args.action=="publish")


if __name__=="__main__":
    main()
