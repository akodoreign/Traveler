"""Give all six shifting-waste states winding routes and distinct silhouettes."""


def shifting_waste_paths(k):
    dx = (-2,2,0,3,-3,1)[k-1]
    dz = (1,-1,3,-2,0,2)[k-1]
    meet = (38+dx,24+dz)
    paths = [
        ((1,24),(8,24),(16,31+dz),(24,34+dz),(31+dx,32+dz),meet),
        ((70,24),(63,24),(55,19+dz),(47,16+dz),(42+dx,18+dz),meet),
        ((36,1),(36,7),(31+dx,12),(30+dx,20),(35+dx,23),meet),
        ((36,46),(36,40),(43+dx,37),(47+dx,32+dz),(44+dx,26+dz),meet),
    ]
    if k==3:
        paths.append(((47+dx,32+dz),(52,32),(54,34)))
    if k==5:
        paths.append(((31+dx,12),(25,10),(18,12)))
    return paths


def rebuild_shifting_waste(m,k):
    z,x = np.indices((m.d,m.w))
    rough = np.sin(x*.35+z*.21+k)+.57*np.cos(z*.47-x*.16+k*.84)+.29*np.sin(x*.78+z*.66)
    m.blk[:] = np.where(rough>.33,SL_ASH,SL_GROUND)
    m.hgt[:] = 3 + (rough>.89) - (rough<-1.03)
    m.objs.clear()
    approach = np.full((m.d,m.w),3000.,dtype=float)
    for path in shifting_waste_paths(k):
        for (ax,az),(bx,bz) in zip(path,path[1:]):
            dx,dz = bx-ax,bz-az
            t = np.clip(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz),0.,1.)
            approach = np.minimum(approach,(x-ax-dx*t)**2+(z-az-dz*t)**2)
    corruption = (TARSTAIN,EMBER,POPPYF)[k%3]
    for bx,bz,sx,sz in ((12,10,8,6),(19,40,8,5),(34,34,9,7),(55,12,8,7),(57,37,8,8)):
        ground = ((x-bx)/sx)**2+((z-bz)/sz)**2<1+.17*rough
        m.blk[ground & (approach>13)] = corruption
    for bx,bz,sx,sz,high in (
        (23,22,7,6,5),(36,29,5.6,4.5,6),(45,12,5.7,4.6,5),
        (53,27,6.8,5.7,7),(28,41,5.9,4.2,5),(64,36,3.8,7.7,5),
    ):
        bank = ((x-bx)/sx)**2+((z-bz)/sz)**2<1+.13*rough
        bank &= approach>10
        m.hgt[bank] += high+(k%2)
        m.blk[bank] = STONE
    m.hgt[approach<14] = 3
    m.blk[approach<8] = ROAD
    m.hgt[:5,:5] = 3
