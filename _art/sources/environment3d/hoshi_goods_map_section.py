"""Physical floor, barriers and preserved service point for Hoshi's goods shop."""


def rebuild_hoshi_goods(m, ev):
    ox, oz = ROOM_OFS[m.mid]
    m.w, m.d = 36, 36
    m.blk = np.zeros((m.d, m.w), dtype=np.int32)
    m.hgt = np.zeros((m.d, m.w), dtype=np.int32)
    m.rect(ox, oz, 28, 21, DARKWOOD, 0)
    m.rect(ox+1, oz+1, 26, 19, PLANK, 1)
    m.objs.clear()
    m.walls.clear()
    fill(m, ox, 2, oz+20, 28, 5, 1, PLASTER)
    for x in (ox, ox+27):
        fill(m, x, 2, oz, 1, 5, 21, PLASTER)
    door = ev.ev["#1#"]["pos"][0]
    fill(m, ox+1, 2, oz, door-ox-3, 1, 1, DARKWOOD)
    fill(m, door+2, 2, oz, ox+25-door, 1, 1, DARKWOOD)
    # Counter and the two stock shelves. Retain a side passage to the clerk.
    for left, front, width, depth in ((16,13,5,1),(7,24,14,3),(24,21,5,6),(7,12,4,4)):
        m.walls.extend((x,z) for x in range(left,left+width) for z in range(front,front+depth))
    for number in (3,4,5):
        old = ev.ev.pop("#%d#" % number)
        assert old["role"] == "custom"
