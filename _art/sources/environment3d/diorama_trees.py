"""Export textured miniature tree meshes and a few falling maple leaves."""

from math import cos, pi, sin

import numpy as np
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from export_coast import Geometry, STAGE, export, write_model
from voxelize_coast import mesh_source


MAPLE="traveler_diorama_maple"
PINE="traveler_diorama_pine"
LEAF="iuchi_maple_leaf"
TREES=(
    (MAPLE,"cakon_maple_miniature",(2.55,3.05,2.15)),
    (PINE,"coast_pine_v2",(2.38,3.15,2.29)),
)


def build_diorama_mesh(name, key, dimensions, *, align_x=False, main_component=False):
    source,mesh=mesh_source(key)
    if align_x and mesh.extents[2]>mesh.extents[0]:
        mesh.vertices=mesh.vertices[:,[2,1,0]]*[1.,1.,-1.]
    face_ids=np.arange(len(mesh.faces))
    if main_component:
        # Weld positions for component identification while retaining the original UV seams.
        welded,index=np.unique(np.round(mesh.vertices,5),axis=0,return_inverse=True)
        corners=index[mesh.faces]
        a,b=corners.ravel(),corners[:,[1,2,0]].ravel()
        edges=coo_matrix((np.ones(len(a),dtype=bool),(a,b)),shape=(len(welded),len(welded))).tocsr()
        _,labels=connected_components(edges,directed=False)
        groups=labels[corners[:,0]]
        face_ids=face_ids[groups==np.bincount(groups).argmax()]
    faces=mesh.faces[face_ids]
    lower,upper=mesh.bounds
    if main_component:
        lower,upper=mesh.vertices[faces].min(axis=(0,1)),mesh.vertices[faces].max(axis=(0,1))
    unit=(mesh.vertices-lower)/(upper-lower)
    mesh.vertices=(unit-[.5,0.,.5])*dimensions
    # Remove bright legacy backdrop sheets from the bottom/rear silhouettes.
    rgb=mesh.visual.to_color().vertex_colors[:,:3][faces].mean(axis=1)
    center=unit[faces].mean(axis=1)
    white=(rgb.min(axis=1)>169) & (np.ptp(rgb,axis=1)<32)
    fringe=(center[:,1]<.042) | (center[:,2]<.027) | (center[:,2]>.983)
    faces=faces[~(white & fringe) & (mesh.area_faces[face_ids]>1e-7)]
    used=np.arange(len(mesh.vertices))
    if main_component:
        used,faces=np.unique(faces,return_inverse=True)
    uv=mesh.visual.uv[used].copy()
    uv[:,1]=1.-uv[:,1]
    texture=name+".png"
    mesh.visual.material.baseColorTexture.convert("RGB").save(STAGE/"tex"/texture)
    write_model(name,mesh.vertices[used],np.rint(mesh.vertex_normals[used]*32767),uv,
                {name:faces.reshape(-1)},{name:(texture,.94)})
    return {"source":str(source),"triangles":len(faces),"world_size":dimensions}


def build_trees():
    sources={name:build_diorama_mesh(name,key,dimensions,main_component=name==MAPLE)
             for name,key,dimensions in TREES}
    colors={"iuchi_leaf_copper":(158,74,34),"iuchi_leaf_amber":(172,108,45)}
    for key,color in colors.items():
        Image.new("RGB",(8,8),color).save(STAGE/"tex"/(key+".png"))
    leaf=Geometry()
    outline=[(0.,-.35),(-.30,-.26),(-.20,-.05),(-.47,.14),(-.17,.12),
             (-.25,.42),(-.07,.29),(0.,.55),(.10,.30),(.26,.42),(.17,.13),
             (.46,.18),(.23,-.04),(.29,-.26)]
    for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1],strict=True)):
        for p,q in ((a,b),(b,a)):
            leaf.quad([(0.,0.,.047),(*p,0.),(*q,0.),(*q,0.)],
                      [(0.,0.)]*4,"iuchi_leaf_amber" if i<7 else "iuchi_leaf_copper")
    export(LEAF,leaf,{key:(key+".png",.92) for key in colors})
    return sources


def falling_leaves(tree_position, scale, seed):
    x,y,z=tree_position
    rows=[]
    for i in range(2):
        a=seed*2.17+i*pi
        rows.append([LEAF,x+cos(a)*.49*scale,y+(2.35-i*.27)*scale,z+sin(a)*.45*scale,
                     .102+i*.017,(seed*.117+i*.48)%1.,a])
    return rows
