"""Physical follow-through for the seven chapter-three Shadowlands maps."""


SHADOWLANDS_MARCH_ROUTES = {
    "M171": ((0,16),(13,16),(22,13),(33,18),(44,16),(63,16),(75,12),(87,15),(99,16),(111,16)),
    "M172": ((0,16),(12,16),(22,15),(36,20),(47,17),(58,16),(65,19),(80,15),(96,16),(111,16)),
    "M173": ((0,16),(13,16),(25,14),(38,15),(50,14),(57,16),(68,14),(81,16),(94,16),(111,16)),
    "M174": ((0,16),(13,16),(24,17),(32,17),(37,25),(45,17),(58,16),(69,13),(79,16)),
    "M175": ((0,20),(12,20),(24,19),(31,20),(42,21),(54,20),(63,19),(72,16),(83,20)),
    "M176": ((0,16),(14,16),(23,12),(37,17),(49,20),(56,16),(69,16),(80,12),(95,14),(108,17),(121,16)),
    "M177": ((0,16),(13,16),(25,13),(37,19),(48,22),(59,17),(71,13),(83,17),(96,16),(105,16),(111,16)),
}


def rebuild_shadowlands_march(m, ev):
    m.objs = [o for o in m.objs if not (
        (o["t"]=="fb" and o["fbtype"]==20)
        or (m.mid=="M173" and o["t"]=="blk" and o["blk"]==FLOWER_R)
    )]
    route = SHADOWLANDS_MARCH_ROUTES[m.mid]
    z,x = np.indices((m.d,m.w))
    distance = np.full((m.d,m.w),4000.)
    segments=list(zip(route,route[1:]))
    for event in ev.ev.values():
        pos=event.get("pos")
        if not pos or event["role"] not in ("custom","itemchest","portal"):
            continue
        ex, _, ez, _ = pos
        if ez<4 or (event.get("mdlid")=="CE000" and event["role"]=="custom" and ex<7):
            continue
        end=min(route,key=lambda pt:(pt[0]-ex)**2+(pt[1]-ez)**2)
        if end!=(ex,ez):
            segments.append((end,(ex,ez)))
    for (ax,az),(bx,bz) in segments:
        dx,dz=bx-ax,bz-az
        t=np.clip(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz),0.,1.)
        distance=np.minimum(distance,(x-ax-dx*t)**2+(z-az-dz*t)**2)

    ground = (m.blk==SL_GROUND) | (m.blk==SL_ASH)
    m.blk[ground & (distance<=5.7)] = ROAD
    fingers = {
        "M171": ((20,24,7,4),(37,25,5,5),(71,24,6,4),(89,25,7,4)),
        "M172": ((18,10,5,5),(39,25,6,4),(71,10,5,4),(93,27,6,4)),
        "M173": ((27,18,6,5),(40,24,5,4),(57,10,5,5),(77,24,6,5)),
        "M174": ((15,21,6,5),(53,22,7,4),(63,8,5,4)),
        "M175": ((16,29,6,4),(63,28,7,4),(75,9,5,4)),
        "M176": ((25,22,6,4),(39,10,7,4),(72,23,6,5),(105,27,7,5)),
        "M177": ((16,24,6,5),(31,25,6,4),(56,26,6,4),(82,24,6,4)),
    }
    rough=1+.12*np.sin(x*.65+z*.51)+.10*np.cos(x*.37-z*.57)
    for rx,rz,sx,sz in fingers[m.mid]:
        ridge=(((x-rx)/sx)**2+((z-rz)/sz)**2<rough)&ground&(distance>15.)
        if m.mid=="M175":
            ridge&=(abs(x-42)>18)
        m.hgt[ridge]+=3+(np.sin(x[ridge]*.76+z[ridge]*.52)>.2)
        m.blk[ridge]=STONE
