"""Map-generator source for the rebuilt Hoshi storehouse."""


def storehouse():
    mid = "M125"
    m, ev = interior(mid, "Hoshi-no-Ichi - Storehouse", 22, 14, [],
                     ("M103", DOOR_EV[("M103", "store")]),
                     chests=[(10, 12, "N000", 200)], scale=1)
    ox, oz = ROOM_OFS[mid]
    # Retain the return gate and loot event, then build a new cutaway shell.
    m.objs.clear()
    fill(m, ox, 2, oz + 16, 24, 5, 1, PLASTER)
    for x in (ox, ox + 23):
        fill(m, x, 2, oz, 1, 5, 17, PLASTER)
    for x, w in ((ox + 1, 9), (ox + 14, 9)):
        fill(m, x, 2, oz, w, 1, 1, DARKWOOD)
    m.walls.extend((ox+x,oz+z) for left,front,width,depth in ((2,13,6,2),(15,13,7,2),(3,5,2,5),(18,5,3,6))
                   for x in range(left,left+width) for z in range(front,front+depth))
    treasure = ev.ev["#2#"]
    treasure["mdlid"] = "CE000"
    treasure["mdl"] = {"r": [0, .45, 0, .49, .55, .41]}
    # Previous saves keep all IDs for the two gameplay events and the dormant followers.
    ev.n = 4
    return m, ev
