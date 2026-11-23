"""Larger equipment shop with a central aisle and the original trader."""


def rebuild_hoshi_arms(m, ev):
    ox, oz = ROOM_OFS[m.mid]
    m.w, m.d = 36, 36
    m.blk = np.zeros((m.d, m.w), dtype=np.int32)
    m.hgt = np.zeros((m.d, m.w), dtype=np.int32)
    m.rect(ox, oz, 27, 19, DARKWOOD, 0)
    m.rect(ox+1, oz+1, 25, 17, PLANK, 1)
    m.objs.clear()
    m.walls.clear()
    fill(m, ox, 2, oz+18, 27, 5, 1, PLASTER)
    for x in (ox, ox+26):
        fill(m, x, 2, oz, 1, 5, 19, PLASTER)
    door = ev.ev["#1#"]["pos"][0]
    fill(m, ox+1, 2, oz, door-ox-3, 1, 1, DARKWOOD)
    fill(m, door+2, 2, oz, ox+24-door, 1, 1, DARKWOOD)
    for left,front,width,depth in ((14,13,6,1),(8,22,9,2),(23,22,5,2),(25,16,4,5)):
        m.walls.extend((x,z) for x in range(left,left+width) for z in range(front,front+depth))
    for number in (3,4,5,6):
        old = ev.ev.pop("#%d#" % number)
        assert old["role"] == "custom"
