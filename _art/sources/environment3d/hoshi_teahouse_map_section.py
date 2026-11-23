"""Map-generator source for Satomi's rebuilt tea-house interior."""


def rebuild_hoshi_teahouse(m, ev):
    ox, oz = ROOM_OFS[m.mid]
    # Keep the door, Satomi and the story scene at their existing positions.
    m.w, m.d = 42, 38
    m.blk = np.zeros((m.d, m.w), dtype=np.int32)
    m.hgt = np.zeros((m.d, m.w), dtype=np.int32)
    m.rect(ox, oz, 34, 23, DARKWOOD, 0)
    m.rect(ox + 1, oz + 1, 32, 21, PLANK, 1)
    m.rect(15, oz + 1, 9, 3, STONEW, 1)
    m.objs.clear()
    m.walls.clear()
    fill(m, ox, 2, oz + 22, 34, 5, 1, PLASTER)
    for x in (ox, ox + 33):
        fill(m, x, 2, oz, 1, 5, 23, PLASTER)
    fill(m, ox + 1, 2, oz, 12, 1, 1, DARKWOOD)
    fill(m, ox + 21, 2, oz, 12, 1, 1, DARKWOOD)
    # Furniture occupies the sides. The street-to-Satomi approach stays open.
    for left, front, width, depth in ((9, 16, 4, 2), (27, 16, 4, 2), (29, 23, 4, 3)):
        m.walls.extend((x, z) for x in range(left, left+width) for z in range(front, front+depth))
    for number in range(4, 9):
        stock = ev.ev.pop("#%d#" % number)
        assert stock["role"] in ("custom", "light")
