"""Map-generator source for the first two physically recessed cave entrances."""


def carve_environment_cave(m):
    """Cut a walkable tunnel and build a solid roof over the inner passage."""
    coast = m.mid in ("M102", "M105")
    x = (70 if coast else 84) + PAD_X
    z = (23 if coast else 22) + PAD_BOTTOM
    roof_start = 3 if coast else 2
    floor_blk = T(4) if coast else SL_GROUND
    rock_blk = STONE if coast else SL_GROUND
    old_rock = m.hgt.copy()
    removed = []
    if not coast:
        removed = [o for o in m.objs if (
            o["t"]=="fill" and o.get("blk")==VOID and o["x"]==x-1 and o["z"]==z+2
        ) or (
            o["t"]=="fb" and o.get("fbtype")==20
            and abs(o["x"]-x)<=5 and z<=o["z"]<z+5
        )]
        m.objs = [o for o in m.objs if o not in removed]

    shell = []
    path = []
    widths = (3,3,3,3,3,3,2,2,2,2,2,2,2,2)
    for dz, half in enumerate(widths):
        pz = z+dz
        grade = 3 if dz<8 else 2
        left,right = x-half,x+half+1
        path.append((left,right,pz,grade))
        m.rect(left,pz,right-left,1,floor_blk,grade)

        # The ribs gradually merge with the hillside. The ledges on either
        # side keep the opening continuous with the cliff at both ends.
        for dx, offset in ((half+1,0),(half+2,1),(half+3,3),(half+4,4)):
            for side in (-1,1):
                px=x+dx*side
                cheek = 7 + min(4,dz) - offset - ((px+dz)%5==0)
                if int(m.hgt[pz,px])<cheek:
                    m.rect(px,pz,1,1,rock_blk,cheek)

        if dz<roof_start:
            continue
        for px in range(left,right):
            distance = abs(px-x)
            # Tall central headroom. Inner corners step down by half a block.
            ceiling = 9 if distance<half else 8
            if dz>8:
                ceiling-=1
            crown = max(ceiling, int(old_rock[pz,px]),
                        10+min(3,(dz-2)//2)-(1 if distance==half else 0))
            row=(px,ceiling,pz,1,crown-ceiling+1,1,rock_blk)
            fill(m,*row)
            shell.append(row)

    m.environment_tunnel = dict(x=x,z=z,reach=len(widths),path=path,roof=shell,removed=removed)
