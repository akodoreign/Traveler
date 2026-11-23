"""Offline textured previews for the original Hunyuan meshes in this set."""
from pathlib import Path
import sys
import struct
import numpy as np
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import trimesh
from install_smooth_furniture import ART, SWAPS

OUT=Path(__file__).resolve().parent
SIZE=360


def sample(mesh,heading):
    vertices=mesh.vertices.copy()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    vertices-=center
    h=heading
    altitude=.22
    camera=np.array((np.sin(h)*np.cos(altitude),np.sin(altitude),-np.cos(h)*np.cos(altitude)))
    right=np.array((np.cos(h),0.,np.sin(h)))
    up=np.cross(camera,right)*-1
    point=np.stack((vertices@right, vertices@up),axis=-1)
    depth=vertices@camera
    point[:,1]*=-1
    lo,hi=point.min(axis=0),point.max(axis=0)
    point=(point-(lo+hi)/2)*(SIZE*.82/(hi-lo).max())+SIZE*.5
    rgb=np.full((SIZE,SIZE,3),222.,dtype=float)
    zbuffer=np.full((SIZE,SIZE),-100.)
    tex=np.asarray(mesh.visual.material.baseColorTexture.convert("RGB"),float)
    tx,ty=tex.shape[1]-1,tex.shape[0]-1
    uv=mesh.visual.uv
    for tri,norm in zip(mesh.faces,mesh.face_normals,strict=True):
        a,b,c=point[tri]
        p,q=b-a,c-a
        det=p[0]*q[1]-p[1]*q[0]
        if abs(det)<.001:
            continue
        l,t=np.maximum(np.floor(np.minimum(a,np.minimum(b,c))).astype(int),0)
        r,u=np.minimum(np.ceil(np.maximum(a,np.maximum(b,c))).astype(int),SIZE-1)
        if l>r or t>u:
            continue
        y,x=np.mgrid[t:u+1,l:r+1]
        d,e=x+.5-a[0],y+.5-a[1]
        b1=(d*q[1]-e*q[0])/det
        b2=(p[0]*e-p[1]*d)/det
        b0=1-b1-b2
        dz=b0*depth[tri[0]]+b1*depth[tri[1]]+b2*depth[tri[2]]
        mask=(b1>=0)&(b2>=0)&(b0>=0)&(dz>zbuffer[t:u+1,l:r+1])
        if not mask.any():
            continue
        zbuffer[t:u+1,l:r+1][mask]=dz[mask]
        v=b0[mask,None]*uv[tri[0]]+b1[mask,None]*uv[tri[1]]+b2[mask,None]*uv[tri[2]]
        rgb[t:u+1,l:r+1][mask]=tex[np.clip(np.round((1.-v[:,1])*ty),0,ty).astype(int),
                                     np.clip(np.round(v[:,0]*tx),0,tx).astype(int)]*(.89+.11*abs(norm[1]))
    return Image.fromarray(rgb.astype(np.uint8))


def fitted_mesh(name):
    """Read the actual positions, triangles and atlas used by the native asset."""
    data=(ART/(name+".mdl")).read_bytes()
    streams=[]
    offset=14
    for dtype,width in ((">f4",3),(">i2",3),(">f4",2)):
        count=struct.unpack_from(">6BII",data,offset)[-1]
        offset+=14
        stream=np.frombuffer(data,dtype=dtype,count=count*width,offset=offset)
        streams.append(stream.reshape(-1,width).astype(float))
        offset+=stream.nbytes
    offset+=4
    groups=data[offset]
    offset+=1
    faces=[]
    for _ in range(groups):
        *_,kind,length,count=struct.unpack_from(">4BII",data,offset)
        offset+=12
        array=np.frombuffer(data,dtype=">u4" if kind==7 else ">u2",count=count,offset=offset)
        faces.extend(array.reshape(-1,3))
        offset+=length+4
    xyz,_,uv=streams
    uv[:,1]=1-uv[:,1]
    tex=Image.open(ART/"tex"/(name+".png"))
    material=trimesh.visual.material.PBRMaterial(baseColorTexture=tex)
    vis=trimesh.visual.texture.TextureVisuals(uv=uv,material=material)
    return trimesh.Trimesh(vertices=xyz,faces=faces,visual=vis,process=False)


if __name__=="__main__":
    pairs=[]
    for name,_ in SWAPS.values():
        if (ART/(name+".mdl")).exists():
            mesh=fitted_mesh(name)
            pairs.append((name,[sample(mesh,heading) for heading in (-.43,2.60)]))
    sheet=Image.new("RGB",(len(pairs)*SIZE,2*SIZE+32),"#20252a")
    for i,(name,images) in enumerate(pairs):
        for j,image in enumerate(images):
            sheet.paste(image,(i*SIZE,j*SIZE+32))
        ImageDraw.Draw(sheet).text((i*SIZE+10,9),name,fill="white")
    sheet.save(OUT/"smooth-furniture-review.jpg",quality=94)
