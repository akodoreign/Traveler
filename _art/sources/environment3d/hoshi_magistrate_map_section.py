"""The Hoshi magistrate's room, preserving Kanbe and the route back to town."""


def rebuild_hoshi_magistrate(m, ev):
    ox, oz = ROOM_OFS[m.mid]
    m.w, m.d = 44, 40
    m.blk = np.zeros((m.d,m.w),dtype=np.int32)
    m.hgt = np.zeros((m.d,m.w),dtype=np.int32)
    m.rect(ox,oz,36,26,DARKWOOD,0)
    m.rect(ox+1,oz+1,34,24,PLANK,1)
    m.objs.clear()
    m.walls.clear()
    fill(m,ox,2,oz+25,36,5,1,PLASTER)
    for x in (ox,ox+35):
        fill(m,x,2,oz,1,5,26,PLASTER)
    door = ev.ev["#1#"]["pos"][0]
    fill(m,ox+1,2,oz,door-ox-3,1,1,DARKWOOD)
    fill(m,door+2,2,oz,ox+33-door,1,1,DARKWOOD)
    for left,front,width,depth in ((19,15,5,1),(7,26,10,3),(30,26,7,3),(7,16,5,2),(31,17,4,3)):
        m.walls.extend((x,z) for x in range(left,left+width) for z in range(front,front+depth))
    for number in (3,4,5):
        old = ev.ev.pop("#%d#" % number)
        assert old["role"] in ("custom","light")
