"""Fitted physical shells for the three Kudo story interiors."""


KUDO_ROOM_LAYOUTS = {
    "M352": (3,30,8,26,6,("#8#","#9#","#10#","#11#")),
    "M353": (4,28,8,26,7,("#8#","#9#","#10#")),
    "M354": (4,28,8,26,7,("#6#","#7#")),
}


def rebuild_kudo_room(m, ev):
    left,right,front,back,entry,old_decor=KUDO_ROOM_LAYOUTS[m.mid]
    m.blk.fill(0)
    m.hgt.fill(0)
    m.objs.clear()
    m.walls.clear()
    m.rect(left,front,right-left+1,back-front+1,PLANK,1)
    m.rect(left,front,1,back-front+1,STONEW,5)
    m.rect(right,front,1,back-front+1,STONEW,5)
    m.rect(left,back,right-left+1,1,STONEW,5)
    m.rect(left,front,entry-left-1,1,STONEW,2)
    m.rect(entry+2,front,right-entry-1,1,STONEW,2)
    m.rect(entry-1,front-1,3,2,STONEW,1)
    for key in old_decor:
        node=ev.ev.get(key)
        if node and (node["role"]=="light" or
                     all(page["trigger"]==0 and not page["cmdblock"] for page in node["page"])):
            del ev.ev[key]
