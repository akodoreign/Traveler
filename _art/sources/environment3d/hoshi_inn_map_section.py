"""Map-generator source for Hoshi's rebuilt inn."""


def rebuild_hoshi_inn(m, ev):
    ox, oz = ROOM_OFS[m.mid]
    m.w, m.d = 44, 40
    m.blk = np.zeros((m.d,m.w),dtype=np.int32)
    m.hgt = np.zeros((m.d,m.w),dtype=np.int32)
    m.rect(ox,oz,36,26,DARKWOOD,0)
    m.rect(ox+1,oz+1,34,24,PLANK,1)
    m.rect(17,oz+1,10,4,STONEW,1)
    m.objs.clear()
    m.walls.clear()
    fill(m,ox,2,oz+25,36,5,1,PLASTER)
    for x in (ox,ox+35):
        fill(m,x,2,oz,1,5,26,PLASTER)
    fill(m,ox+1,2,oz,12,1,1,DARKWOOD)
    fill(m,ox+23,2,oz,12,1,1,DARKWOOD)
    for left,front,width,depth in ((9,14,5,2),(8,21,5,3),(25,25,1,6),(31,25,1,6)):
        m.walls.extend((x,z) for x in range(left,left+width) for z in range(front,front+depth))
    for number in (3,4,5):
        stock=ev.ev.pop("#%d#" % number)
        assert stock["role"] in ("custom","light")
