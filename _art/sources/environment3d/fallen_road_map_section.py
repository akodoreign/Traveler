"""First deep Shadowlands route past the scouts' wreck and tainted pools."""

FALLEN_TRAIL = (
    (0,16),(12,16),(21,12),(30,12),(38,27),(47,39),(62,38),
    (69,25),(79,12),(92,10),(102,16),(111,16),
)
FALLEN_SPURS = (
    ((13,16),(14,13)),
    ((36,24),(30,24)),
    ((79,12),(74,6)),
)


def rebuild_fallen_road(m):
    m.d = 52
    z,x = np.indices((m.d,m.w))
    rough = np.sin(x*.209-z*.371)+.43*np.sin(z*.67+x*.152)+.31*np.cos(x*.59+z*.31)
    m.hgt = np.asarray(3+(rough>.86)-(rough<-.96),dtype=np.int32)
    m.blk = np.asarray(np.where(rough>.38,SL_ASH,SL_GROUND),dtype=np.int32)
    m.objs.clear()
    d = np.full_like(rough,2000.0)
    for route in (FALLEN_TRAIL,*FALLEN_SPURS):
        for (ax,az),(bx,bz) in zip(route,route[1:]):
            dx,dz=bx-ax,bz-az
            t=np.clip(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz),0.0,1.0)
            d=np.minimum(d,(x-ax-dx*t)**2+(z-az-dz*t)**2)
    for bx,bz,sx,sz in ((17,31,12,8),(50,18,10,7),(66,9,8,7),(87,29,9,10),(101,41,7,8)):
        seep=((x-bx)/sx)**2+((z-bz)/sz)**2<1+.15*rough
        m.blk[seep & (d>14)]=TARSTAIN
    for bx,bz,sx,sz,high in ((27,37,6,10,5),(49,28,9,4,5),(63,32,7,6,6),
                             (76,34,4,10,5),(97,24,7,5,6)):
        ridge=((x-bx)/sx)**2+((z-bz)/sz)**2<1+.18*rough
        ridge &= d>10
        m.hgt[ridge]+=high
        m.blk[ridge]=STONE
    m.hgt[d<14]=3
    m.blk[d<8]=ROAD
    m.hgt[:5,:5]=3
